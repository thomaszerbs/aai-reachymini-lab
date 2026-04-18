#!/usr/bin/env python3
"""emo_v7_vad.py - Reachy Mini Chat with VAD-based ASR and Async HTTP

This file builds on `emo_v7.py` with two major latency improvements:
1. VAD-based ASR recording (stops when speech ends, not fixed 4s)
2. Async HTTP requests for non-blocking LLM responses

Key improvements:
- ASR latency: ~4.5s → ~1.5-2.5s (VAD recording)
- LLM latency: Hidden via async + thinking animations
- Better UX: Robot shows "thinking" during LLM processing

Usage:
  python emo_v7_vad.py --asr          # VAD-based push-to-talk ASR mode
  python emo_v7_vad.py                # fall back to text input chat
"""

import time
import json
import argparse
from typing import Optional
from contextlib import suppress

def check_runtime_dependencies(require_reachy: bool = False) -> bool:
    """Check that optional runtime deps are importable."""
    missing = []
    try:
        import aiohttp  # noqa: F401
    except Exception:
        missing.append("aiohttp")
    if require_reachy:
        try:
            import reachy_mini  # noqa: F401
        except Exception:
            missing.append("reachy-mini")
    if missing:
        print(f"❌ Missing runtime dependencies: {', '.join(missing)}")
        print("   Install: pip install -r requirements.txt")
        if "reachy-mini" in missing:
            print("   For robot: pip install 'reachy-mini[mujoco]'")
        return False
    return True

# Optional faster-whisper ASR engine
try:
    from utils.asr import FasterWhisperASREngine
except Exception:
    try:
        from .utils.asr import FasterWhisperASREngine
    except Exception:
        FasterWhisperASREngine = None


class ChatAppWithASR:
    def __init__(self, model: str = "qwen3:0.6b", ollama_url: str = "http://localhost:11434", debug: bool = False, use_asr: bool = False):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.use_asr = use_asr
        self.controller = None
        self.asr_engine = None

    async def _get_ollama_response_async(self, prompt: str, session) -> Optional[str]:
        """Async version of LLM request with streaming response."""
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
                if response.status != 200:
                    error_text = await response.text()
                    print(f"\n⚠️ Ollama async error ({response.status}): {error_text}")
                    return None

                full_response = ""
                while True:
                    line = await response.content.readline()
                    if not line:
                        break
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if chunk.get("error"):
                                print(f"\n⚠️ Ollama error: {chunk['error']}")
                                return None
                            content = chunk.get("response") or chunk.get("thinking") or ""
                            if content:
                                print(content, end="", flush=True)
                                full_response += content
                        except Exception:
                            continue
                
                print()
                return full_response
                
        except Exception as e:
            print(f"\n⚠️ Ollama async error: {e}")
            return None

    async def _show_thinking_animation(self, reachy, duration: float = 5.0):
        """Show robot 'thinking' animation during LLM processing."""
        import math
        import asyncio
        from reachy_mini.utils import create_head_pose as _chp
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                # Gentle head movements to show "thinking"
                angle = math.sin((time.time() - start_time) * 3) * 0.1  # ±0.1 rad (~6 degrees)
                pose = _chp(roll=angle)
                reachy.goto_target(head=pose, duration=0.3)
                await asyncio.sleep(0.1)

                # Small antenna movements
                if hasattr(reachy, 'l_antenna') and hasattr(reachy, 'r_antenna'):
                    reachy.l_antenna.goto_position(angle * 0.5, duration=0.2)
                    reachy.r_antenna.goto_position(-angle * 0.5, duration=0.2)

                await asyncio.sleep(0.2)
        finally:
            reachy.goto_target(head=_chp(), duration=0.5)

    async def start_chat_async(self):
        """Async version of chat with non-blocking LLM requests."""
        import asyncio
        import aiohttp
        from reachy_mini import ReachyMini
        from emo_v6 import EmotionControllerV6
        from reachy_mini.utils import create_head_pose as _chp
        print("="*60)
        print("🤖 Reachy Mini Chat v7 VAD with Async HTTP")
        print("="*60)

        try:
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")
                self.controller = EmotionControllerV6(reachy, debug=self.debug)
                reachy.goto_target(head=_chp(), duration=1.0)
                await asyncio.sleep(1.0)

                if self.use_asr:
                    if FasterWhisperASREngine is None:
                        print("❌ ASR requested but FasterWhisperASREngine not available. Install faster-whisper and deps.")
                        return

                    print("Initializing ASR engine (model may download on first run)...")
                    try:
                        self.asr_engine = FasterWhisperASREngine(model_name='small', device='cpu')
                    except Exception as e:
                        print(f"❌ Failed to initialize ASR engine: {e}")
                        return

                    print("\n🎤 VAD ASR + Async mode: press Ctrl-C to stop")
                    print("🤔 Robot will show 'thinking' during LLM processing")
                    print("⏱️ Latency measurements enabled")
                    
                    async with aiohttp.ClientSession() as session:
                        while True:
                            try:
                                print("\n🎙️ Speak now (VAD will stop recording when you stop)...")
                                start_time = time.time()
                                transcription = self.asr_engine.transcribe_from_mic_vad(max_duration=4.0, silence_threshold=1.5)
                                asr_latency = time.time() - start_time
                                
                                if not transcription:
                                    print("⚠️ No speech detected, try again")
                                    continue

                                print(f"\n⏱️ ASR latency: {asr_latency:.2f}s (VAD stopped recording)")
                                print(f"📝 You (transcribed): {transcription}")
                                
                                print("\n🤖 Reachy Mini: ", end="", flush=True)
                                
                                # Start thinking animation and LLM request concurrently
                                llm_start = time.time()
                                thinking_task = asyncio.create_task(
                                    self._show_thinking_animation(reachy, duration=10.0)
                                )
                                llm_task = asyncio.create_task(
                                    self._get_ollama_response_async(transcription, session)
                                )
                                
                                # Wait for LLM response (thinking animation runs concurrently)
                                response = await llm_task
                                llm_latency = time.time() - llm_start
                                
                                # Cancel thinking animation since we got response
                                thinking_task.cancel()
                                with suppress(asyncio.CancelledError):
                                    await thinking_task
                                print(f"\n⏱️ LLM latency: {llm_latency:.2f}s")
                                
                                if response and self.controller:
                                    emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                                    if self.debug:
                                        print(f"\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}")
                                    # Use PARALLEL TTS with immediate robot movements
                                    await self.controller.speak_with_expression_parallel(response, emotion, intensity, emotion_level)

                            except KeyboardInterrupt:
                                print("\n👋 Exiting ASR chat")
                                break
                            except asyncio.CancelledError:
                                print("\n⚠️ Task cancelled")
                                break
                            except Exception as e:
                                print(f"⚠️ Error during ASR chat loop: {e}")
                                await asyncio.sleep(1.0)

                else:
                    print("\n💬 Start chatting (type 'quit' to exit)")
                    async with aiohttp.ClientSession() as session:
                        eof_count = 0
                        while True:
                            try:
                                user_input = input("\n🧑 You: ").strip()
                                if user_input.lower() in ['quit', 'exit', 'q']:
                                    break
                                if not user_input:
                                    continue
                                eof_count = 0

                                print("\n🤖 Reachy Mini: ", end="", flush=True)
                                
                                # Start thinking animation and LLM request concurrently
                                llm_start = time.time()
                                thinking_task = asyncio.create_task(
                                    self._show_thinking_animation(reachy, duration=10.0)
                                )
                                llm_task = asyncio.create_task(
                                    self._get_ollama_response_async(user_input, session)
                                )
                                
                                response = await llm_task
                                llm_latency = time.time() - llm_start
                                
                                thinking_task.cancel()
                                with suppress(asyncio.CancelledError):
                                    await thinking_task
                                print(f"\n⏱️ LLM latency: {llm_latency:.2f}s")
                                
                                if response and self.controller:
                                    emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                                    if self.debug:
                                        print(f"\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}")
                                    # Use PARALLEL TTS for text mode too
                                    await self.controller.speak_with_expression_parallel(response, emotion, intensity, emotion_level)

                            except EOFError:
                                eof_count += 1
                                if eof_count >= 3:
                                    print("\n👋 EOF received, exiting chat.")
                                    break
                                print("\n⚠️ Empty input (EOF). Type 'quit' to exit.")
                                continue
                            except KeyboardInterrupt:
                                print("\n\n👋 Interrupted")
                                break
                            except Exception as e:
                                print(f"\n⚠️ Error: {e}")

        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            print("Falling back to TTS-only mode")
            self._tts_only_mode()

    def start_chat(self):
        """Synchronous wrapper for backward compatibility."""
        import asyncio
        asyncio.run(self.start_chat_async())

    def _tts_only_mode(self):
        print("\n📻 Running in TTS-only mode (no robot)")
        try:
            from reachy_mini import ReachyMini
            from emo_v6 import EmotionControllerV6
            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV6(reachy, debug=self.debug)

                test_texts = [
                    ("你好！我是Reachy Mini！", "neutral"),
                    ("我今天很开心！", "positive"),
                    ("我有点难过...", "negative"),
                    ("这是什么？", "question"),
                ]

                for text, emotion in test_texts:
                    print(f"\nTesting: '{text}'")
                    controller.tts_engine.speak_with_emotion(text, emotion)
                    time.sleep(1.0)

        except Exception:
            from emo_v6 import EdgeTTSEngine
            print("\nTesting Edge-TTS standalone...")
            tts_engine = EdgeTTSEngine()
            tts_engine.speak_with_emotion("Hello! This is Edge-TTS working.", "neutral")


def main():
    parser = argparse.ArgumentParser(description="Reachy Mini Chat v7 VAD with ASR")
    parser.add_argument('--chat', action='store_true', help='Start interactive chat')
    parser.add_argument('--asr', action='store_true', help='Use microphone ASR input (push-to-talk)')
    parser.add_argument('--model', default='qwen3:0.6b', help='Ollama model to use')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    if not (args.chat or args.asr):
        parser.print_help()
        return

    if not check_runtime_dependencies(require_reachy=True):
        return

    app = ChatAppWithASR(model=args.model, ollama_url=args.url, debug=args.debug, use_asr=args.asr)
    app.start_chat()


if __name__ == '__main__':
    main()
