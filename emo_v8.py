#!/usr/bin/env python3
"""emo_v8.py - Reachy Mini Chat with VAD-based ASR (Voice Activity Detection)

This file builds on `emo_v7.py` and replaces fixed 4s ASR recording with
VAD-based recording that stops when speech ends, reducing E2E latency.

Key improvements:
1. VAD-based ASR recording (stops when user stops speaking, not fixed 4s)
2. Latency measurement and reporting
3. Optimized for lower E2E latency

Usage:
  python emo_v8.py --asr          # VAD-based push-to-talk ASR mode
  python emo_v8.py                # fall back to text input chat
"""

import time
import json
import requests
import argparse
from typing import Optional

from emo_v6 import EmotionControllerV6, EdgeTTSEngine
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


class ChatAppWithASR:
    def __init__(self, model: str = "qwen3:0.6b", ollama_url: str = "http://localhost:11434", debug: bool = False, use_asr: bool = False):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.use_asr = use_asr
        self.controller: Optional[EmotionControllerV6] = None
        self.asr_engine = None

    def _get_ollama_response(self, prompt: str) -> Optional[str]:
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": True,
                      "system": "You are a cute desktop robot assistant. Respond with enthusiasm and warmth.",
                      "options": {"temperature": 0.8, "num_predict": 200}},
                stream=True, timeout=30
            )

            full_response = ""
            for line in response.iter_lines():
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
            print(f"\n⚠️ Ollama error: {e}")
            return None

    def start_chat(self):
        print("="*60)
        print("🤖 Reachy Mini Chat v8 with VAD-based ASR")
        print("="*60)

        try:
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")
                self.controller = EmotionControllerV6(reachy, debug=self.debug)
                reachy.goto_target(head=create_head_pose(), duration=1.0)
                time.sleep(1.0)

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

                    print("\n🎤 VAD ASR mode: press Ctrl-C to stop. Speak naturally, stops when you stop.")
                    print("⏱️ Latency measurements enabled")
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
                            llm_start = time.time()
                            response = self._get_ollama_response(transcription)
                            llm_latency = time.time() - llm_start

                            if response and self.controller:
                                emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                                if self.debug:
                                    print(f"\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}")
                                self.controller.speak_with_expression(response, emotion, intensity, emotion_level)

                        except KeyboardInterrupt:
                            print("\n👋 Exiting ASR chat")
                            break
                        except Exception as e:
                            print(f"⚠️ Error during ASR chat loop: {e}")
                            time.sleep(1.0)

                else:
                    print("\n💬 Start chatting (type 'quit' to exit)")
                    while True:
                        try:
                            user_input = input("\n🧑 You: ").strip()
                            if user_input.lower() in ['quit', 'exit', 'q']:
                                break
                            if not user_input:
                                continue

                            print("\n🤖 Reachy Mini: ", end="", flush=True)
                            response = self._get_ollama_response(user_input)

                            if response and self.controller:
                                emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                                if self.debug:
                                    print(f"\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}")
                                self.controller.speak_with_expression(response, emotion, intensity, emotion_level)

                        except KeyboardInterrupt:
                            print("\n\n👋 Interrupted")
                            break
                        except Exception as e:
                            print(f"\n⚠️ Error: {e}")

        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            print("Falling back to TTS-only mode")
            self._tts_only_mode()

    def _tts_only_mode(self):
        print("\n📻 Running in TTS-only mode (no robot)")
        try:
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
            print("\nTesting Edge-TTS standalone...")
            tts_engine = EdgeTTSEngine()
            tts_engine.speak_with_emotion("Hello! This is Edge-TTS working.", "neutral")


def main():
    parser = argparse.ArgumentParser(description="Reachy Mini Chat v8 with VAD-based ASR")
    parser.add_argument('--chat', action='store_true', help='Start interactive chat')
    parser.add_argument('--asr', action='store_true', help='Use microphone ASR input (push-to-talk)')
    parser.add_argument('--model', default='qwen3:0.6b', help='Ollama model to use')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()
    app = ChatAppWithASR(model=args.model, ollama_url=args.url, debug=args.debug, use_asr=args.asr)

    app.start_chat()


if __name__ == '__main__':
    main()
