#!/usr/bin/env python3
"""Fix emo_v6.py for lazy imports, dependency checks, and CLI robustness."""

import re

PATH = "emo_v6.py"

with open(PATH, "r") as f:
    src = f.read()

# ------------------------------------------------------------------
# 1. Strip top-level optional imports (keep stdlib + typing)
# ------------------------------------------------------------------

OLD_IMPORTS = '''import time
import json
import requests
import threading
import asyncio
import numpy as np
import edge_tts
import sounddevice as sd
import soundfile as sf
import tempfile
import os
from typing import Dict, List, Tuple, Optional
from reachy_mini import ReachyMini
from reachy_mini.motion.recorded_move import RecordedMoves
from reachy_mini.utils import create_head_pose'''

NEW_IMPORTS = '''import time
import json
import threading
from typing import Dict, List, Tuple, Optional

def _create_head_pose(*args, **kwargs):
    from reachy_mini.utils import create_head_pose as _chp
    return _chp(*args, **kwargs)

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
    return True'''

src = src.replace(OLD_IMPORTS, NEW_IMPORTS, 1)

# ------------------------------------------------------------------
# 2. Remove ReachyMini type annotations (import-time dependency)
# ------------------------------------------------------------------
src = src.replace(": ReachyMini", "")

# ------------------------------------------------------------------
# 3. Replace direct create_head_pose calls with lazy wrapper
#    (skip the import line and wrapper def itself by matching '(')
# ------------------------------------------------------------------
src = src.replace("create_head_pose(", "_create_head_pose(")

# ------------------------------------------------------------------
# 4. Fix ChatAppWithEdgeTTS to accept gentle/voice and pass them on
# ------------------------------------------------------------------
OLD_INIT = '''    def __init__(self, model: str = "qwen3:0.6b", ollama_url: str = "http://localhost:11434", debug: bool = False):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.controller = None'''

NEW_INIT = '''    def __init__(self, model: str = "qwen3:0.6b", ollama_url: str = "http://localhost:11434", debug: bool = False, gentle: bool = False, voice: str = "zh-CN-XiaoxiaoNeural"):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.gentle = gentle
        self.voice = voice
        self.controller = None'''

src = src.replace(OLD_INIT, NEW_INIT, 1)

# ------------------------------------------------------------------
# 5. Fix start_chat to pass gentle/voice into EmotionControllerV6
# ------------------------------------------------------------------
OLD_START_CHAT = '''                self.controller = EmotionControllerV6(reachy, debug=self.debug)'''
NEW_START_CHAT = '''                self.controller = EmotionControllerV6(reachy, debug=self.debug, gentle_mode=self.gentle, voice=self.voice)'''
src = src.replace(OLD_START_CHAT, NEW_START_CHAT, 1)

# ------------------------------------------------------------------
# 6. Fix _get_ollama_response: HTTP status, thinking field, error field
# ------------------------------------------------------------------
OLD_GET_OLLAMA = '''    def _get_ollama_response(self, prompt: str) -> Optional[str]:
        """Get response from Ollama"""
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
                    except:
                        continue

            print()
            return full_response

        except Exception as e:
            print(f"\\n⚠️ Ollama error: {e}")
            return None'''

NEW_GET_OLLAMA = '''    def _get_ollama_response(self, prompt: str) -> Optional[str]:
        """Get response from Ollama"""
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
                print(f"\\n⚠️ Ollama HTTP {response.status_code}: {response.text[:200]}")
                return None

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if chunk.get("error"):
                            print(f"\\n⚠️ Ollama error: {chunk['error']}")
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
            print(f"\\n⚠️ Ollama error: {e}")
            return None'''

src = src.replace(OLD_GET_OLLAMA, NEW_GET_OLLAMA, 1)

# ------------------------------------------------------------------
# 7. Add EOFError guard in start_chat loop + 3-strike exit
# ------------------------------------------------------------------
OLD_LOOP = '''                while True:
                    try:
                        user_input = input("\\n🧑 You: ").strip()
                        if user_input.lower() in ['quit', 'exit', 'q']: break
                        if not user_input: continue

                        print("\\n🤖 Reachy Mini: ", end="", flush=True)
                        response = self._get_ollama_response(user_input)

                        if response and self.controller:
                            emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                            if self.debug: print(f"\\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}")
                            self.controller.speak_with_expression(response, emotion, intensity, emotion_level)

                    except KeyboardInterrupt:
                        print("\\n\\n👋 Interrupted")
                        break
                    except Exception as e:
                        print(f"\\n⚠️ Error: {e}")
                        self._tts_only_mode()'''

NEW_LOOP = '''                eof_count = 0
                while True:
                    try:
                        user_input = input("\\n🧑 You: ").strip()
                        if user_input.lower() in ['quit', 'exit', 'q']: break
                        if not user_input: continue
                        eof_count = 0

                        print("\\n🤖 Reachy Mini: ", end="", flush=True)
                        response = self._get_ollama_response(user_input)

                        if response and self.controller:
                            emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                            if self.debug: print(f"\\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}")
                            self.controller.speak_with_expression(response, emotion, intensity, emotion_level)

                    except EOFError:
                        eof_count += 1
                        if eof_count >= 3:
                            print("\\n👋 EOF received, exiting chat.")
                            break
                        print("\\n⚠️ Empty input (EOF). Type 'quit' to exit.")
                        continue
                    except KeyboardInterrupt:
                        print("\\n\\n👋 Interrupted")
                        break
                    except Exception as e:
                        print(f"\\n⚠️ Error: {e}")
                        self._tts_only_mode()'''

src = src.replace(OLD_LOOP, NEW_LOOP, 1)

# ------------------------------------------------------------------
# 8. Fix test_edge_tts referencing EmotionControllerV5 (should be V6)
# ------------------------------------------------------------------
src = src.replace("controller = EmotionControllerV5(reachy, debug=self.debug)",
                  "controller = EmotionControllerV6(reachy, debug=self.debug)", 1)

# ------------------------------------------------------------------
# 9. Fix main() to show help when no args and pass gentle/voice
# ------------------------------------------------------------------
OLD_MAIN = '''    args = parser.parse_args()
    app = ChatAppWithEdgeTTS(model=args.model, ollama_url=args.url, debug=args.debug)

    # Pass gentle/voice into controller construction where used
    if args.test_tts:
        app.test_edge_tts()
    elif args.test_actions:
        app.test_combined_actions()

        print("\\n" + "="*50)
        response = input("Also test individual components? (y/n): ").lower().strip()
        if response == 'y':
            app.test_individual_actions()

    else:
        app.start_chat()'''

NEW_MAIN = '''    args = parser.parse_args()

    if not any([args.chat, args.test_tts, args.test_actions]):
        parser.print_help()
        return

    if not check_runtime_dependencies(require_reachy=True):
        return

    app = ChatAppWithEdgeTTS(model=args.model, ollama_url=args.url, debug=args.debug, gentle=args.gentle, voice=args.voice)

    if args.test_tts:
        app.test_edge_tts()
    elif args.test_actions:
        app.test_combined_actions()

        if sys.stdin.isatty():
            print("\\n" + "="*50)
            response = input("Also test individual components? (y/n): ").lower().strip()
            if response == 'y':
                app.test_individual_actions()

    elif args.chat:
        app.start_chat()'''

src = src.replace(OLD_MAIN, NEW_MAIN, 1)

# ------------------------------------------------------------------
# 10. Add missing sys import at top (used in main)
# ------------------------------------------------------------------
# We already replaced the whole import block; add sys there.
src = src.replace("import time\nimport json", "import sys\nimport time\nimport json", 1)

# ------------------------------------------------------------------
# 11. Ensure EdgeTTSEngine lazy-imports edge_tts/soundfile/sounddevice
# ------------------------------------------------------------------
# _speak_async uses edge_tts, sf, os, tempfile — sf/sd already top-level in original.
# We removed them; add lazy imports inside methods that need them.

OLD_SPEAK_ASYNC = '''    async def _speak_async(self, text: str, voice: str, rate: str = "+0%", pitch: str = "+0Hz", style: str = "general") -> Tuple[np.ndarray, int]:
        """Synthesize speech to a temporary WAV file with voice parameters, read it and return (audio, samplerate).

        This avoids guessing the raw stream format and preserves the correct sample rate
        so playback via sounddevice does not introduce noise.
        """
        try:
            # Save to a temporary WAV file using edge-tts's save helper
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name

            # Create communicate with voice parameters
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)'''

NEW_SPEAK_ASYNC = '''    async def _speak_async(self, text: str, voice: str, rate: str = "+0%", pitch: str = "+0Hz", style: str = "general") -> Tuple:
        """Synthesize speech to a temporary WAV file with voice parameters, read it and return (audio, samplerate).

        This avoids guessing the raw stream format and preserves the correct sample rate
        so playback via sounddevice does not introduce noise.
        """
        try:
            import tempfile
            import os
            import numpy as np
            import edge_tts
            import soundfile as sf

            # Save to a temporary WAV file using edge-tts's save helper
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name

            # Create communicate with voice parameters
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)'''

src = src.replace(OLD_SPEAK_ASYNC, NEW_SPEAK_ASYNC, 1)

# Also fix the return type Tuple[np.ndarray, int] → Tuple (lazy np)
# Already handled in replacement above.

# ------------------------------------------------------------------
# 12. Fix speak_with_emotion / speak_with_emotion_async sd.play usage
# ------------------------------------------------------------------
# sd was imported top-level; now lazy inside methods.
OLD_SWE = '''            if sr and audio_data.size:
                # Play with the correct samplerate returned by the file
                sd.play(audio_data, samplerate=sr)
                sd.wait()'''
NEW_SWE = '''            if sr and audio_data.size:
                import sounddevice as sd
                sd.play(audio_data, samplerate=sr)
                sd.wait()'''
src = src.replace(OLD_SWE, NEW_SWE, 1)

OLD_SWEA = '''            if sr and audio_data.size:
                # Play with the correct samplerate returned by the file
                # Use asyncio.to_thread to run blocking sounddevice.play/wait in thread
                await asyncio.to_thread(lambda: (sd.play(audio_data, samplerate=sr), sd.wait()))'''
NEW_SWEA = '''            if sr and audio_data.size:
                import sounddevice as sd
                # Play with the correct samplerate returned by the file
                # Use asyncio.to_thread to run blocking sounddevice.play/wait in thread
                await asyncio.to_thread(lambda: (sd.play(audio_data, samplerate=sr), sd.wait()))'''
src = src.replace(OLD_SWEA, NEW_SWEA, 1)

# ------------------------------------------------------------------
# 13. EdgeTTSEngine __init__ uses no lazy imports, but emotion_voices/voice_params are static.
# No changes needed there.

# ------------------------------------------------------------------
# 14. EmotionControllerV6 __init__ loads RecordedMoves; keep lazy inside.
# ------------------------------------------------------------------
OLD_ECV6_INIT = '''    def __init__(self, reachy, debug: bool = False, gentle_mode: bool = True, voice: str = "zh-CN-XiaoxiaoNeural"):
        self.reachy = reachy
        self.debug = debug
        self.gentle_mode = gentle_mode
        self.is_speaking_action = False
        # TTS and lip-sync
        self.tts_engine = EdgeTTSEngine(default_voice=voice)
        self.lip_sync = LipSyncControllerV5(reachy, debug=self.debug)

        # Load both libraries for richer motions
        self.emotions_lib = RecordedMoves("pollen-robotics/reachy-mini-emotions-library")
        self.dances_lib = RecordedMoves("pollen-robotics/reachy-mini-dances-library")'''

NEW_ECV6_INIT = '''    def __init__(self, reachy, debug: bool = False, gentle_mode: bool = True, voice: str = "zh-CN-XiaoxiaoNeural"):
        from reachy_mini.motion.recorded_move import RecordedMoves
        self.reachy = reachy
        self.debug = debug
        self.gentle_mode = gentle_mode
        self.is_speaking_action = False
        # TTS and lip-sync
        self.tts_engine = EdgeTTSEngine(default_voice=voice)
        self.lip_sync = LipSyncControllerV5(reachy, debug=self.debug)

        # Load both libraries for richer motions
        self.emotions_lib = RecordedMoves("pollen-robotics/reachy-mini-emotions-library")
        self.dances_lib = RecordedMoves("pollen-robotics/reachy-mini-dances-library")'''

src = src.replace(OLD_ECV6_INIT, NEW_ECV6_INIT, 1)

# ------------------------------------------------------------------
# 15. ChatAppWithEdgeTTS methods that instantiate ReachyMini need lazy import
# ------------------------------------------------------------------
# start_chat, _tts_only_mode, test_edge_tts, test_like_tts_py, test_combined_actions, test_individual_actions
for method_marker, indent in [
    ("    def start_chat(self):", "        "),
    ("    def _tts_only_mode(self):", "        "),
    ("    def test_edge_tts(self):", "        "),
    ("    def test_like_tts_py(self):", "        "),
    ("    def test_combined_actions(self):", "        "),
    ("    def test_individual_actions(self):", "        "),
]:
    # Replace first occurrence of 'with ReachyMini(media_backend="no_media") as reachy:' in each method
    # Simple string replacement across whole file is okay because it's identical everywhere.
    pass  # handled below

# Replace all occurrences of `with ReachyMini` with lazy import version
OLD_WITH = '''        try:
            with ReachyMini(media_backend="no_media") as reachy:'''
NEW_WITH = '''        try:
            from reachy_mini import ReachyMini
            with ReachyMini(media_backend="no_media") as reachy:'''

src = src.replace(OLD_WITH, NEW_WITH)

# ------------------------------------------------------------------
# 16. Write back
# ------------------------------------------------------------------
with open(PATH, "w") as f:
    f.write(src)

print("Done. Verifying syntax...")
import py_compile
py_compile.compile(PATH, doraise=True)
print("Syntax OK.")
