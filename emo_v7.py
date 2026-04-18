#!/usr/bin/env python3
"""emo_v7.py - Reachy Mini Chat with ASR (faster-whisper CPU)

This file builds on `emo_v6.py` and adds a simple ASR input mode using
`faster-whisper` via `utils/asr.FasterWhisperASREngine`.

Usage:
  python emo_v7.py --asr          # push-to-talk ASR mode
  python emo_v7.py                # fall back to text input chat
"""

import time
import json
import argparse
from typing import Optional

def check_runtime_dependencies(require_reachy: bool = False) -> bool:
    """Check that optional runtime deps are importable."""
    missing = []
    try:
        import requests  # noqa: F401
    except Exception:
        missing.append("requests")
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
    def __init__(self, model: str = "qwen3:0.6b", ollama_url: str = "http://localhost:11434", debug: bool = False, use_asr: bool = False, gentle: bool = False):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.use_asr = use_asr
        self.gentle = gentle
        self.controller = None
        self.asr_engine = None

    def _get_ollama_response(self, prompt: str) -> Optional[str]:
        try:
            import requests
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": True,
                      "system": "You are a cute desktop robot assistant. Respond with enthusiasm and warmth.",
                      "options": {"temperature": 0.8, "num_predict": 200}},
                stream=True, timeout=30
            )

            if not response.ok:
                print(f"\n⚠️ Ollama HTTP {response.status_code}: {response.text[:200]}")
                return None

            full_response = ""
            for line in response.iter_lines():
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
            print(f"\n⚠️ Ollama error: {e}")
            return None

    def start_chat(self):
        print("="*60)
        print("🤖 Reachy Mini Chat v7 with ASR")
        print("="*60)

        try:
            from reachy_mini import ReachyMini
            from emo_v6 import EmotionControllerV6
            from reachy_mini.utils import create_head_pose
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")
                self.controller = EmotionControllerV6(reachy, debug=self.debug, gentle_mode=self.gentle)
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

                    print("\n🎤 ASR mode: press Ctrl-C to stop. Recording 4s per utterance.")
                    while True:
                        try:
                            print("\n⏺️ Recording (4s)...")
                            transcription = self.asr_engine.transcribe_from_mic(4.0)
                            if not transcription:
                                print("⚠️ No speech detected, try again")
                                continue

                            print(f"\n📝 You (transcribed): {transcription}")
                            print("\n🤖 Reachy Mini: ", end="", flush=True)
                            response = self._get_ollama_response(transcription)

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
                            response = self._get_ollama_response(user_input)

                            if response and self.controller:
                                emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                                if self.debug:
                                    print(f"\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}")
                                self.controller.speak_with_expression(response, emotion, intensity, emotion_level)

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

    def _tts_only_mode(self):
        print("\n📻 Running in TTS-only mode (no robot)")
        try:
            from reachy_mini import ReachyMini
            from emo_v6 import EmotionControllerV6
            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV6(reachy, debug=self.debug, gentle_mode=self.gentle)

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
    parser = argparse.ArgumentParser(description="Reachy Mini Chat v7 with ASR")
    parser.add_argument('--chat', action='store_true', help='Start interactive chat')
    parser.add_argument('--asr', action='store_true', help='Use microphone ASR input (push-to-talk)')
    parser.add_argument('--model', default='qwen3:0.6b', help='Ollama model to use')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--gentle', action='store_true', help='Enable gentle_mode for subtle emotions')

    args = parser.parse_args()

    if not (args.chat or args.asr):
        parser.print_help()
        return

    if not check_runtime_dependencies(require_reachy=True):
        return

    app = ChatAppWithASR(model=args.model, ollama_url=args.url, debug=args.debug, use_asr=args.asr, gentle=args.gentle)
    app.start_chat()


if __name__ == '__main__':
    main()
