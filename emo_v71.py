#!/usr/bin/env python3
"""emo_v71.py - Reachy Mini Chat with Piper-TTS (Offline)

Based on emo_v7.py, replacing Edge-TTS with Piper-TTS for fully offline operation.

Usage:
  python emo_v71.py --piper-model models/en_US-lessac-high.onnx  # Run with specific Piper model
  python emo_v71.py --asr                                        # Enable ASR
  python emo_v71.py --model qwen2.5:0.5b                         # Set Ollama model
"""

import os
import sys
import time
import json
import wave
import tempfile
import asyncio
import argparse
import threading
import subprocess
import numpy as np
import soundfile as sf
import sounddevice as sd
import aiohttp
from typing import Optional, Tuple

# Import from existing modules
# We need to ensure we can import from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from emo_v6 import EmotionControllerV6
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# Optional faster-whisper ASR engine
try:
    from utils.asr import FasterWhisperASREngine
except Exception:
    try:
        from .utils.asr import FasterWhisperASREngine
    except Exception:
        FasterWhisperASREngine = None

class PiperTTSEngine:
    """Piper-TTS engine wrapper for offline speech synthesis."""
    
    def __init__(self, model_path: str, config_path: str = None, speaker_id: int = 0, debug: bool = False):
        self.debug = debug
        self.model_path = model_path
        self.config_path = config_path
        self.speaker_id = speaker_id
        self.voice = None
        
        try:
            from piper import PiperVoice, PiperConfig
            # Import SynthesisConfig if available, else use default dict
            try:
                from piper import SynthesisConfig
                self.SynthesisConfig = SynthesisConfig
            except ImportError:
                self.SynthesisConfig = None
            
            import onnxruntime
            self.PiperVoice = PiperVoice
            self.PiperConfig = PiperConfig
            self.onnxruntime = onnxruntime
        except ImportError:
            print("❌ piper-tts not installed. Install with: pip install piper-tts")
            return

        if not os.path.exists(model_path):
            print(f"❌ Piper model not found at: {model_path}")
            
            # Try to find any onnx model in models/ or current directory
            print("🔍 Searching for available models...")
            found_models = []
            for search_dir in ['.', 'models']:
                if os.path.exists(search_dir):
                    for f in os.listdir(search_dir):
                        if f.endswith('.onnx'):
                            found_models.append(os.path.join(search_dir, f))
            
            if found_models:
                print(f"💡 Found available models:")
                for m in found_models:
                    print(f"   --piper-model {m}")
                print(f"\nExample: python emo_v71.py --piper-model {found_models[0]}")
            else:
                print("⚠️ No .onnx models found. Please download one from https://github.com/rhasspy/piper/releases/tag/v0.0.2")
                
            self.voice = None
            return

        try:
            # If config path not provided, assume .json with same name as .onnx
            if not config_path:
                potential_config = model_path + ".json"
                if os.path.exists(potential_config):
                    self.config_path = potential_config
            
            print(f"🎙️ Loading Piper model: {model_path}")
            
            # Manually load config to fix legacy phoneme_type issue
            with open(self.config_path or (model_path + ".json"), 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # FIX: Replace legacy "PhonemeType.ESPEAK" string with "espeak"
            if config_dict.get('phoneme_type') == 'PhonemeType.ESPEAK':
                print("🔧 Fixing legacy phoneme_type in config...")
                config_dict['phoneme_type'] = 'espeak'
                
            # Create config object
            config = self.PiperConfig.from_dict(config_dict)
            
            # Create ONNX session
            session = self.onnxruntime.InferenceSession(
                str(model_path),
                sess_options=self.onnxruntime.SessionOptions(),
                providers=["CPUExecutionProvider"]
            )
            
            # Initialize voice manually
            self.voice = self.PiperVoice(session=session, config=config)
                
            print(f"✅ Piper TTS initialized")
            
        except Exception as e:
            print(f"❌ Failed to load Piper model: {e}")
            self.voice = None

    def speak_with_emotion(self, text: str, emotion: str = 'neutral'):
        """Speak text using Piper (blocking)."""
        if not text.strip():
            return
            
        if not self.voice:
            print(f"⚠️ Piper voice not loaded. Skipping speech: '{text[:20]}...'")
            return

        try:
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name

            # Synthesize to file
            with wave.open(tmp_path, "wb") as wav_file:
                # Use synthesize_wav which handles wave header automatically
                syn_config = None
                if self.SynthesisConfig and self.speaker_id is not None:
                    syn_config = self.SynthesisConfig(speaker_id=self.speaker_id)
                
                self.voice.synthesize_wav(text, wav_file, syn_config=syn_config)

            # Read and play
            data, sr = sf.read(tmp_path, dtype='float32')
            if data.size > 0:
                sd.play(data, samplerate=sr)
                sd.wait()
            
            # Cleanup
            try:
                os.remove(tmp_path)
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Piper TTS error: {e}")

    async def speak_with_emotion_async(self, text: str, emotion: str = 'neutral'):
        """Async version of speak_with_emotion (runs in thread)."""
        # Piper synthesis is CPU bound, so run in a separate thread
        await asyncio.to_thread(self.speak_with_emotion, text, emotion)


class EmotionControllerV71(EmotionControllerV6):
    """Emotion controller using Piper-TTS instead of Edge-TTS."""
    
    def __init__(self, reachy: ReachyMini, piper_model: str, piper_config: str = None, speaker_id: int = 0, debug: bool = False):
        # Initialize parent
        super().__init__(reachy, debug)
        
        # Override TTS engine
        self.tts_engine = PiperTTSEngine(piper_model, piper_config, speaker_id, debug)


class ChatAppWithPiper:
    def __init__(self, 
                 model: str = "qwen3:0.6b", 
                 ollama_url: str = "http://localhost:11434", 
                 piper_model: str = "en_US-libritts_r-medium.onnx",
                 piper_config: str = None,
                 speaker_id: int = 0,
                 debug: bool = False, 
                 use_asr: bool = False):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.use_asr = use_asr
        self.piper_model = piper_model
        self.piper_config = piper_config
        self.speaker_id = speaker_id
        
        self.controller: Optional[EmotionControllerV71] = None
        self.asr_engine = None

    async def _get_ollama_response_async(self, prompt: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Get response from Ollama (streaming)."""
        try:
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model, 
                    "prompt": prompt, 
                    "stream": True,
                    "system": "You are a cute desktop robot assistant. Respond with enthusiasm and warmth.",
                    "options": {"temperature": 0.8, "num_predict": 200}
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                full_response = ""
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                content = chunk['response']
                                print(content, end="", flush=True)
                                full_response += content
                        except Exception:
                            continue
                
                print()
                return full_response
                
        except Exception as e:
            print(f"\n⚠️ Ollama async error: {e}")
            return None

    async def _show_thinking_animation(self, reachy: ReachyMini, duration: float = 5.0):
        """Show robot 'thinking' animation."""
        import math
        start_time = time.time()
        while time.time() - start_time < duration:
            angle = math.sin((time.time() - start_time) * 3) * 0.1
            pose = create_head_pose(roll=angle)
            reachy.goto_target(head=pose, duration=0.3)
            await asyncio.sleep(0.1)
            
            if hasattr(reachy, 'l_antenna') and hasattr(reachy, 'r_antenna'):
                reachy.l_antenna.goto_position(angle * 0.5, duration=0.2)
                reachy.r_antenna.goto_position(-angle * 0.5, duration=0.2)
            
            await asyncio.sleep(0.2)
            
        reachy.goto_target(head=create_head_pose(), duration=0.5)

    async def start_chat_async(self):
        print("="*60)
        print("🤖 Reachy Mini Chat v7.1 with Piper-TTS (Offline)")
        print("="*60)
        print(f"Piper Model: {self.piper_model}")
        print("💡 Need more voices? Download .onnx models from:")
        print("   https://github.com/rhasspy/piper/releases/tag/v0.0.2")

        try:
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")
                
                # Initialize controller with Piper
                self.controller = EmotionControllerV71(
                    reachy, 
                    self.piper_model, 
                    self.piper_config, 
                    self.speaker_id, 
                    self.debug
                )
                
                reachy.goto_target(head=create_head_pose(), duration=1.0)
                await asyncio.sleep(1.0)

                if self.use_asr:
                    if FasterWhisperASREngine is None:
                        print("❌ ASR requested but FasterWhisperASREngine not available.")
                        return

                    print("Initializing ASR engine...")
                    try:
                        self.asr_engine = FasterWhisperASREngine(model_name='small', device='cpu')
                    except Exception as e:
                        print(f"❌ Failed to initialize ASR engine: {e}")
                        return

                    print("\n🎤 VAD ASR + Async mode: press Ctrl-C to stop")
                    
                    async with aiohttp.ClientSession() as session:
                        while True:
                            try:
                                print("\n🎙️ Speak now...")
                                start_time = time.time()
                                transcription = self.asr_engine.transcribe_from_mic_vad(max_duration=4.0, silence_threshold=1.5)
                                
                                if not transcription:
                                    continue

                                print(f"📝 You: {transcription}")
                                print("\n🤖 Reachy Mini: ", end="", flush=True)
                                
                                llm_start = time.time()
                                thinking_task = asyncio.create_task(self._show_thinking_animation(reachy, 10.0))
                                llm_task = asyncio.create_task(self._get_ollama_response_async(transcription, session))
                                
                                response = await llm_task
                                thinking_task.cancel()
                                
                                if response and self.controller:
                                    emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                                    await self.controller.speak_with_expression_parallel(response, emotion, intensity, emotion_level)

                            except KeyboardInterrupt:
                                break
                            except Exception as e:
                                print(f"⚠️ Error: {e}")
                                await asyncio.sleep(1.0)

                else:
                    print("\n💬 Start chatting (type 'quit' to exit)")
                    async with aiohttp.ClientSession() as session:
                        while True:
                            try:
                                user_input = input("\n🧑 You: ").strip()
                                if user_input.lower() in ['quit', 'exit', 'q']:
                                    break
                                if not user_input:
                                    continue

                                print("\n🤖 Reachy Mini: ", end="", flush=True)
                                
                                thinking_task = asyncio.create_task(self._show_thinking_animation(reachy, 10.0))
                                llm_task = asyncio.create_task(self._get_ollama_response_async(user_input, session))
                                
                                response = await llm_task
                                thinking_task.cancel()
                                
                                if response and self.controller:
                                    emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                                    await self.controller.speak_with_expression_parallel(response, emotion, intensity, emotion_level)

                            except KeyboardInterrupt:
                                break
                            except Exception as e:
                                print(f"\n⚠️ Error: {e}")

        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            self._tts_only_mode()

    def start_chat(self):
        asyncio.run(self.start_chat_async())

    def _tts_only_mode(self):
        print("\n📻 Running in TTS-only mode (no robot)")
        print("💡 Need more voices? Download .onnx models from:")
        print("   https://github.com/rhasspy/piper/releases/tag/v0.0.2")
        tts = PiperTTSEngine(self.piper_model, self.piper_config, self.speaker_id, self.debug)
        tts.speak_with_emotion("Hello! Piper TTS is working.", "neutral")


def main():
    parser = argparse.ArgumentParser(description="Reachy Mini Chat v7.1 with Piper-TTS")
    parser.add_argument('--chat', action='store_true', help='Start interactive chat')
    parser.add_argument('--asr', action='store_true', help='Use microphone ASR input')
    parser.add_argument('--model', default='qwen3:0.6b', help='Ollama model')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--piper-model', default='en_US-libritts_r-medium.onnx', help='Path to Piper .onnx model')
    parser.add_argument('--piper-config', default=None, help='Path to Piper .json config')
    parser.add_argument('--speaker', type=int, default=0, help='Speaker ID for multi-speaker models')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()
    
    # Needs aiohttp
    try:
        import aiohttp
    except ImportError:
        print("❌ aiohttp not found. Please install: pip install aiohttp")
        return

    app = ChatAppWithPiper(
        model=args.model, 
        ollama_url=args.url, 
        piper_model=args.piper_model,
        piper_config=args.piper_config,
        speaker_id=args.speaker,
        debug=args.debug, 
        use_asr=args.asr
    )

    app.start_chat()


if __name__ == '__main__':
    main()
