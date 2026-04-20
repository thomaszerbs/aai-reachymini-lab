#!/usr/bin/env python3
"""
emo_v5.py - Reachy Mini with Edge-TTS Integration
Combines the best of tts.py (Edge-TTS) with emo_v4.py (emotion control)
"""

import time
import json
import threading
import tempfile
import os
from typing import Dict, List, Tuple, Optional


def _create_head_pose(*args, **kwargs):
    from reachy_mini.utils import create_head_pose as _chp
    return _chp(*args, **kwargs)


def check_runtime_dependencies(require_reachy: bool = False) -> bool:
    """Check that optional dependencies are importable before using them."""
    try:
        import requests  # noqa: F401
    except Exception as exc:
        print(f"❌ Missing dependency 'requests': {exc}")
        print("   Install: pip install requests")
        return False
    if require_reachy:
        try:
            import reachy_mini  # noqa: F401
        except Exception as exc:
            print(f"❌ Missing dependency 'reachy-mini': {exc}")
            print("   Install: pip install 'reachy-mini[mujoco]'")
            return False
    return True

class EdgeTTSEngine:
    """Edge-TTS engine with emotional voice selection"""

    def __init__(self, default_voice: str = "zh-CN-XiaoxiaoNeural", sample_rate: int = 22050):
        self.default_voice = default_voice
        self.sample_rate = sample_rate
        self.debug = True  # Force debug on for clarity
        print(f"🎙️ EdgeTTSEngine initialized")
        print(f"   - Using voice: {default_voice}")
        print(f"   - Sample rate: {sample_rate}Hz")

        # Emotional voice mapping
        self.emotion_voices = {
            'positive': "en-US-JennyNeural",      # Friendly, cheerful
            'negative': "en-US-DavisNeural",       # Softer, compassionate
            'question': "en-US-BrianNeural",       # Curious, thoughtful
            'activity': "en-US-AriaNeural",        # Energetic, lively
            'neutral': default_voice,              # Default Chinese
        }

        self.voice_params = {
            'positive': {'rate': '+10%', 'pitch': '+5Hz'},
            'negative': {'rate': '-10%', 'pitch': '-5Hz'},
            'question': {'rate': '+0%', 'pitch': '+2Hz'},
            'activity': {'rate': '+15%', 'pitch': '+8Hz'},
            'neutral': {'rate': '+0%', 'pitch': '+0Hz'},
        }

    def _has_chinese(self, text: str) -> bool:
        """Detect CJK Unified Ideographs in text."""
        if not text:
            return False
        for ch in text:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    async def _speak_async(self, text: str, voice: str) -> Tuple:
        """Synthesize speech to a temporary WAV file, read it and return (audio, samplerate).

        This avoids guessing the raw stream format and preserves the correct sample rate
        so playback via sounddevice does not introduce noise.
        """
        import numpy as np
        import edge_tts
        import soundfile as sf
        try:
            # Save to a temporary WAV file using edge-tts's save helper
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name

            communicate = edge_tts.Communicate(text, voice)
            try:
                try:
                    await communicate.save(tmp_path)
                except Exception as save_exc:
                    if self.debug and not self._has_chinese(text):
                        print(f"⚠️ Edge-TTS save error: {save_exc}")
                    # Retry with default voice if different
                    if voice != self.default_voice:
                        if self.debug and not self._has_chinese(text):
                            print("⚠️ Retrying synthesis with default voice...")
                        time.sleep(0.5)
                        try:
                            communicate = edge_tts.Communicate(text, self.default_voice)
                            await communicate.save(tmp_path)
                        except Exception as save_exc2:
                            if self.debug and not self._has_chinese(text):
                                print(f"⚠️ Retry with default voice failed: {save_exc2}")
                            # Propagate original save exception
                            raise save_exc2
                    else:
                        raise save_exc
            except Exception:
                # If saving failed entirely, ensure temp file removed and raise
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
                raise

            # If file is empty, retry with default voice (useful for mismatched language/voice)
            try:
                if os.path.getsize(tmp_path) == 0:
                    if voice != self.default_voice:
                        if self.debug and not self._has_chinese(text):
                            print("⚠️ Edge-TTS produced empty file; retrying with default voice...")
                        try:
                            communicate = edge_tts.Communicate(text, self.default_voice)
                            await communicate.save(tmp_path)
                        except Exception as e2:
                            if self.debug and not self._has_chinese(text):
                                print(f"⚠️ Retry with default voice failed: {e2}")
            except OSError:
                # File might not exist yet; continue to read and let sf raise
                pass

            # Read the WAV file using soundfile to get correct dtype and samplerate
            try:
                data, sr = sf.read(tmp_path, dtype='float32')
            except Exception as re:
                if self.debug:
                    print(f"⚠️ Failed to read synthesized WAV: {re}")
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
                raise

            # Ensure mono or stereo shape is acceptable for sounddevice
            if data.ndim == 1:
                audio = data
            else:
                # sounddevice handles stereo arrays; keep as-is
                audio = data

            # Clean up temporary file
            try:
                os.remove(tmp_path)
            except Exception:
                pass

            # If audio is empty, signal failure
            if audio.size == 0 or sr == 0:
                raise RuntimeError("No audio produced")

            return audio, sr

        except Exception as e:
            if self.debug:
                print(f"Edge-TTS synthesis error: {e}")
            return np.array([], dtype=np.float32), 0

    def speak_with_emotion(self, text: str, emotion: str = 'neutral'):
        """Speak text with emotional voice"""
        import asyncio
        import sounddevice as sd
        if not text.strip():
            return

        voice = self.emotion_voices.get(emotion, self.default_voice)

        try:
            audio_data, sr = asyncio.run(self._speak_async(text, voice))

            if sr and audio_data.size:
                # Play with the correct samplerate returned by the file
                sd.play(audio_data, samplerate=sr)
                sd.wait()
            else:
                if self.debug:
                    print("⚠️ No audio produced by Edge-TTS")
                raise RuntimeError("No audio produced")
        except Exception as e:
            print(f"⚠️ Edge-TTS error: {e}")
            self._fallback_tts(text, emotion)

    def _fallback_tts(self, text: str, emotion: str):
        """Fallback if Edge-TTS fails"""
        import subprocess
        import platform

        system = platform.system()

        if system == "Darwin":
            try:
                subprocess.run(['say', text], check=True)
                print("✅ Using macOS 'say' as fallback")
            except:
                pass
        elif system == "Windows":
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                print("✅ Using pyttsx3 as fallback")
            except:
                pass

class LipSyncControllerV5:
    """Lip-sync using your antenna/eye control approach"""

    def __init__(self, reachy, debug: bool = False):
        self.reachy = reachy
        self.is_speaking = False
        self.sync_thread = None
        self.debug = debug
        if debug:
            print("✅ LipSyncControllerV5 initialized (handles antenna/eye movements)")

    def start_lip_sync(self, text: str, emotion_level: float = 0.5):
        """Start lip-sync with your approach"""
        self.is_speaking = True

        def lip_sync_animation():
            while self.is_speaking:
                try:
                    # Check if robot head exists
                    if hasattr(self.reachy, 'head'):
                        self.reachy.head.r_antenna.goal_position = emotion_level * 0.8
                        self.reachy.head.l_antenna.goal_position = emotion_level * 0.8
                        self.reachy.head.r_eye.goal_position = 1 - (emotion_level * 0.3)
                        self.reachy.head.l_eye.goal_position = 1 - (emotion_level * 0.3)
                except Exception as e:
                    print(f"⚠️ Lip-sync error (robot may not support): {e}")
                    break
                time.sleep(0.1)

            # Return to neutral (with error handling)
            try:
                if hasattr(self.reachy, 'head'):
                    self.reachy.head.r_antenna.goal_position = 0
                    self.reachy.head.l_antenna.goal_position = 0
                    self.reachy.head.r_eye.goal_position = 0.5
                    self.reachy.head.l_eye.goal_position = 0.5
            except:
                pass

        self.sync_thread = threading.Thread(target=lip_sync_animation, daemon=True)
        self.sync_thread.start()

    def stop_lip_sync(self):
        """Stop lip-sync"""
        self.is_speaking = False
        if self.sync_thread:
            self.sync_thread.join(timeout=0.5)

class EmotionControllerV5:
    """Emotion controller with Edge-TTS integration"""

    def __init__(self, reachy, debug: bool = False):
        self.reachy = reachy
        self.debug = debug
        from reachy_mini.motion.recorded_move import RecordedMoves
        self.recorded_moves = RecordedMoves("pollen-robotics/reachy-mini-dances-library")
        self.tts_engine = EdgeTTSEngine()
        self.lip_sync = LipSyncControllerV5(reachy)
        self._categorize_recorded_moves()

        self.simple_actions = {
            'nod': self._simple_nod,
            'shake': self._simple_shake,
            'look_curious': self._simple_look_curious,
            'look_sad': self._simple_look_sad,
            'excited_wiggle': self._simple_excited_wiggle,
            'thoughtful_tilt': self._simple_thoughtful_tilt,
        }

    def _categorize_recorded_moves(self):
        """Categorize recorded moves by emotion"""
        all_moves = self.recorded_moves.list_moves()

        self.emotion_to_moves = {
            'positive': [],
            'negative': [],
            'question': [],
            'activity': [],
            'neutral': [],
        }

        emotion_keywords = {
            'positive': ['开心', '快乐', '高兴', '喜欢', '爱', '谢谢', '感谢', '好', '棒', '完美', 'excited', 'happy', 'joy', 'love', 'thanks', 'good', 'great', 'awesome'],
            'negative': ['伤心', '难过', '悲伤', '生气', '失望', '抱歉', '对不起', '不好', '坏', 'sad', 'angry', 'sorry', 'disappointed', 'bad', 'wrong', 'hate'],
            'question': ['吗', '？', '?', '为什么', '怎么', '如何', 'what', 'why', 'how', 'when'],
            'activity': ['跳舞', '舞蹈', '运动', '活动', '动起来', 'dance', 'move', 'action', 'play'],
            'neutral': ['simple', 'basic', 'neutral', 'calm'],
        }

        for move_name in all_moves:
            move = self.recorded_moves.get(move_name)
            desc = move.description.lower() if move.description else ""

            best_match = 'neutral'
            best_score = 0

            for emotion, keywords in emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in desc)
                if score > best_score:
                    best_score = score
                    best_match = emotion

            self.emotion_to_moves[best_match].append(move_name)
            if self.debug:
                print(f"🔍 Categorized '{move_name}' as {best_match}")

    def analyze_emotion(self, text: str) -> Tuple[str, str, float]:
        """Analyze emotion with your level calculation"""
        text_lower = text.lower()
        emotion_level = min(len(text) / 200, 1.0)

        positive_words = ['开心', '快乐', '高兴', '喜欢', '爱', '谢谢', '感谢', '好', '棒', '完美', 'excited', 'happy', 'joy', 'love', 'thanks', 'good', 'great', 'awesome']
        negative_words = ['伤心', '难过', '悲伤', '生气', '失望', '抱歉', '对不起', '不好', '坏', 'sad', 'angry', 'sorry', 'disappointed', 'bad', 'wrong', 'hate']
        question_words = ['吗', '？', '?', '为什么', '怎么', '如何', 'what', 'why', 'how', 'when']
        activity_words = ['跳舞', '舞蹈', '运动', '活动', '动起来', 'dance', 'move', 'action', 'play']

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        ques_count = sum(1 for word in question_words if word in text_lower)
        act_count = sum(1 for word in activity_words if word in text_lower)

        emoji_pos = ['😊', '😄', '😍', '👍', '🥰', '😎', '🎉', '❤️', '😂', '🤗']
        emoji_neg = ['😢', '😭', '😡', '👎', '😔', '😞', '😤', '💔']
        emoji_ques = ['🤔', '❓', '⁉️', '💭', '🧐', '🔍']
        emoji_act = ['💃', '🕺', '🎵', '🎶', '⚽', '🏀', '🎮']

        pos_count += sum(1 for emoji in emoji_pos if emoji in text)
        neg_count += sum(1 for emoji in emoji_neg if emoji in text)
        ques_count += sum(1 for emoji in emoji_ques if emoji in text)
        act_count += sum(1 for emoji in emoji_act if emoji in text)

        scores = {
            'positive': pos_count,
            'negative': neg_count,
            'question': ques_count,
            'activity': act_count
        }

        emotion_type = max(scores, key=scores.get)
        total_score = sum(scores.values())

        if total_score >= 3:
            intensity = 'high'
        elif total_score >= 1:
            intensity = 'medium'
        else:
            intensity = 'low'

        if emotion_type == 'positive':
            emotion_level *= 1.2
        elif emotion_type == 'negative':
            emotion_level *= 0.8

        return emotion_type, intensity, emotion_level

    def execute_recorded_move(self, move_name: str, initial_goto_duration: float = 1.0):
        """Execute a recorded move"""
        if self.debug:
            print(f"🎬 Playing recorded move: {move_name}")
        move = self.recorded_moves.get(move_name)
        self.reachy.play_move(move, initial_goto_duration=initial_goto_duration)

    def execute_emotion_move(self, emotion_type: str, intensity: str = 'medium'):
        """Execute move based on emotion"""
        available_moves = self.emotion_to_moves.get(emotion_type, [])

        if available_moves:
            if intensity == 'high' and len(available_moves) > 1:
                move_name = available_moves[-1]
            elif intensity == 'low' and len(available_moves) > 1:
                move_name = available_moves[0]
            else:
                import random
                move_name = random.choice(available_moves)

            duration_map = {'high': 0.8, 'medium': 1.0, 'low': 1.2}
            self.execute_recorded_move(move_name, duration_map.get(intensity, 1.0))
        else:
            if self.debug:
                print(f"⚠️ No recorded moves for {emotion_type}, using simple action")
            self._execute_simple_action(emotion_type, intensity)

    def _execute_simple_action(self, emotion_type: str, intensity: str):
        duration_map = {'high': 1.5, 'medium': 2.0, 'low': 2.5}
        duration = duration_map.get(intensity, 2.0)

        if emotion_type == 'positive':
            self.simple_actions['nod'](duration)
        elif emotion_type == 'negative':
            self.simple_actions['look_sad'](duration)
        elif emotion_type == 'question':
            self.simple_actions['look_curious'](duration)
        elif emotion_type == 'activity':
            self.simple_actions['excited_wiggle'](duration)
        else:
            self.simple_actions['nod'](duration)

    def speak_with_expression(self, text: str, emotion: str = 'neutral', intensity: str = 'medium', emotion_level: float = 0.5):
        """Speak with Edge-TTS and your lip-sync"""
        if not text.strip():
            return

        if self.debug:
            print(f"🗣️ Speaking with {emotion} emotion (level: {emotion_level:.2f})")

        word_count = len(text.split())
        estimated_duration = max(1.0, word_count / 2.5)

        self.lip_sync.start_lip_sync(text, emotion_level)

        action_thread = threading.Thread(
            target=self.execute_emotion_move,
            args=(emotion, intensity),
            daemon=True
        )
        action_thread.start()

        self.tts_engine.speak_with_emotion(text, emotion)

        self.lip_sync.stop_lip_sync()

    def _simple_nod(self, duration: float = 2.0):
        amplitude = 0.6
        cycles = int(duration * 2)

        for _ in range(cycles):
            self.reachy.goto_target(head=_create_head_pose(pitch=20*amplitude, degrees=True), duration=0.25)
            time.sleep(0.1)
            self.reachy.goto_target(head=_create_head_pose(pitch=-10*amplitude, degrees=True), duration=0.25)
            time.sleep(0.1)

        self.reachy.goto_target(head=_create_head_pose(), duration=0.5)

    def _simple_shake(self, duration: float = 2.0):
        amplitude = 0.7
        cycles = int(duration * 1.5)

        for _ in range(cycles):
            self.reachy.goto_target(head=_create_head_pose(yaw=30*amplitude, degrees=True), duration=0.3)
            time.sleep(0.1)
            self.reachy.goto_target(head=_create_head_pose(yaw=-30*amplitude, degrees=True), duration=0.3)
            time.sleep(0.1)

        self.reachy.goto_target(head=_create_head_pose(), duration=0.5)

    def _simple_look_curious(self, duration: float = 2.0):
        amplitude = 0.8

        self.reachy.goto_target(head=_create_head_pose(yaw=25*amplitude, pitch=10*amplitude, degrees=True), duration=duration/3)
        time.sleep(duration/3)
        self.reachy.goto_target(head=_create_head_pose(yaw=-25*amplitude, pitch=10*amplitude, degrees=True), duration=duration/3)
        time.sleep(duration/3)
        self.reachy.goto_target(head=_create_head_pose(), duration=duration/3)

    def _simple_look_sad(self, duration: float = 2.0):
        self.reachy.goto_target(head=_create_head_pose(pitch=30, degrees=True), duration=duration/2)
        time.sleep(duration/2)
        self.reachy.goto_target(head=_create_head_pose(), duration=duration/2)

    def _simple_excited_wiggle(self, duration: float = 2.0):
        cycles = int(duration * 3)

        for i in range(cycles):
            left_val = 0.7 if i % 2 == 0 else -0.7
            right_val = -0.7 if i % 2 == 0 else 0.7

            self.reachy.goto_target(antennas=[left_val, right_val], duration=0.15)
            time.sleep(0.05)

        self.reachy.goto_target(antennas=[0, 0], duration=0.3)

    def _simple_thoughtful_tilt(self, duration: float = 2.0):
        amplitude = 0.6

        self.reachy.goto_target(head=_create_head_pose(roll=15*amplitude, degrees=True), duration=duration/4)
        time.sleep(duration/4)
        self.reachy.goto_target(head=_create_head_pose(roll=-15*amplitude, degrees=True), duration=duration/4)
        time.sleep(duration/4)
        self.reachy.goto_target(head=_create_head_pose(), duration=duration/2)

class ChatAppWithEdgeTTS:
    """Chat application with Edge-TTS"""

    def __init__(self, model: str = "qwen3:0.6b", ollama_url: str = "http://localhost:11434", debug: bool = False):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.controller = None

    def start_chat(self):
        """Start chat with Edge-TTS"""
        if not check_runtime_dependencies(require_reachy=True):
            return
        from reachy_mini import ReachyMini
        print("="*60)
        print("🤖 Reachy Mini Chat v5 with Edge-TTS")
        print("="*60)
        print("Features:")
        print("1. Edge-TTS (Microsoft Azure voices)")
        print("2. Your antenna/eye lip-sync approach")
        print("3. Emotion level calculation (like tts.py)")
        print("4. Recorded moves library")
        print("5. Enhanced emotion detection")
        print("="*60)

        try:
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")
                self.controller = EmotionControllerV5(reachy, debug=self.debug)
                reachy.goto_target(head=_create_head_pose(), duration=1.0)
                time.sleep(1.0)

                print("\n💬 Start chatting (type 'quit' to exit)")
                print("🎭 Uses Edge-TTS with emotional voices")
                print("👄 Lip-sync with antennas and eyes")
                print("="*60)

                eof_count = 0
                while True:
                    try:
                        user_input = input("\n🧑 You: ").strip()
                        if user_input.lower() in ['quit', 'exit', 'q']: break
                        if not user_input: continue

                        print("\n🤖 Reachy Mini: ", end="", flush=True)
                        response = self._get_ollama_response(user_input)

                        if response and self.controller:
                            emotion, intensity, emotion_level = self.controller.analyze_emotion(response)
                            if self.debug: print(f"\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}")
                            self.controller.speak_with_expression(response, emotion, intensity, emotion_level)

                    except KeyboardInterrupt:
                        print("\n\n👋 Interrupted")
                        break
                    except EOFError:
                        eof_count += 1
                        if eof_count >= 3:
                            print("\n👋 Non-interactive stdin detected, exiting.")
                            break
                        print("\n⚠️ Warning: no input available (EOF)")
                    except Exception as e:
                        print(f"\n⚠️ Error: {e}")
                        self._tts_only_mode()

        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            self._tts_only_mode()

    def _get_ollama_response(self, prompt: str) -> Optional[str]:
        """Get response from Ollama"""
        import requests
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": True,
                      "system": "You are a cute desktop robot assistant. Respond with enthusiasm and warmth.",
                      "options": {"temperature": 0.8, "num_predict": 200}},
                stream=True, timeout=30
            )
            if response.status_code != 200:
                print(f"\n❌ Ollama returned HTTP {response.status_code}")
                return None

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if chunk.get('error'):
                            print(f"\n❌ Ollama error: {chunk['error']}")
                            return None
                        content = chunk.get('response', '') or chunk.get('thinking', '')
                        if content:
                            print(content, end="", flush=True)
                            full_response += content
                    except Exception:
                        if self.debug:
                            import traceback
                            traceback.print_exc()
                        continue

            print()
            return full_response

        except Exception as e:
            print(f"\n⚠️ Ollama error: {e}")
            return None

    def _tts_only_mode(self):
        """Run TTS without robot"""
        if not check_runtime_dependencies(require_reachy=True):
            print("\n📻 Running in TTS-only mode (no robot)")
            print("Testing Edge-TTS standalone...")
            tts_engine = EdgeTTSEngine()
            tts_engine.speak_with_emotion("Hello! This is Edge-TTS working.", "neutral")
            return
        from reachy_mini import ReachyMini
        print("\n📻 Running in TTS-only mode (no robot)")

        try:
            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV5(reachy, debug=self.debug)

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

        except Exception as e:
            print(f"\n⚠️ TTS-only fallback error: {e}")
            print("\nTesting Edge-TTS standalone...")
            tts_engine = EdgeTTSEngine()
            tts_engine.speak_with_emotion("Hello! This is Edge-TTS working.", "neutral")

    def test_edge_tts(self):
        """Test Edge-TTS functionality"""
        if not check_runtime_dependencies(require_reachy=True):
            print("Testing Edge-TTS without robot...")
            tts_engine = EdgeTTSEngine()
            tts_engine.speak_with_emotion("Hello! This is Edge-TTS working.", "neutral")
            return
        from reachy_mini import ReachyMini
        print("🧪 Testing Edge-TTS...")

        test_sentences = [
            ("Hello! I am Reachy Mini!", "positive"),
            ("你好！我是Reachy Mini！", "neutral"),
            ("我今天非常开心！", "positive"),
            ("这是什么问题？", "question"),
        ]

        try:
            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV5(reachy, debug=self.debug)

                for text, emotion in test_sentences:
                    print(f"\nTesting: '{text}'")
                    emotion_type, intensity, level = controller.analyze_emotion(text)
                    print(f"Analyzed: {emotion_type}, {intensity}, level={level:.2f}")
                    controller.speak_with_expression(text, emotion_type, intensity, level)
                    time.sleep(2.0)

        except Exception as e:
            print(f"❌ Error: {e}")
            print("\nTesting Edge-TTS without robot...")
            tts_engine = EdgeTTSEngine()
            for text, emotion in test_sentences[:2]:
                print(f"\nTesting TTS: '{text}'")
                tts_engine.speak_with_emotion(text, emotion)
                time.sleep(2.0)

    def test_like_tts_py(self):
        """Test compatibility with your tts.py approach"""
        if not check_runtime_dependencies(require_reachy=True):
            print("⚠️ Cannot test without Reachy Mini")
            return
        from reachy_mini import ReachyMini
        print("🧪 Testing tts.py compatibility mode...")

        try:
            with ReachyMini(media_backend="no_media") as reachy:
                print("模拟你的 tts.py 流程:")

                user_input = "你好，介绍一下你自己"
                print(f"\n用户: {user_input}")

                response = "你好！我是Reachy Mini，一个可爱的桌面机器人助手。我很高兴为你服务！"
                print(f"Reachy: {response}")

                emotion_level = min(len(response) / 200, 1.0)
                print(f"情感值: {emotion_level:.2f}")

                if hasattr(reachy, 'head'):
                    reachy.head.r_antenna.goal_position = emotion_level * 0.8
                    reachy.head.l_antenna.goal_position = emotion_level * 0.8
                    reachy.head.r_eye.goal_position = 1 - (emotion_level * 0.3)
                    reachy.head.l_eye.goal_position = 1 - (emotion_level * 0.3)
                else:
                    try:
                        # Try using generic goto_target for antennas if head not present
                        reachy.goto_target(antennas=[emotion_level * 0.8, emotion_level * 0.8], duration=0.2)
                    except Exception:
                        print("⚠️ Robot has no head/antennas interface; skipping visual expression")

                print("🗣️ Speaking with Edge-TTS...")
                tts_engine = EdgeTTSEngine()
                tts_engine.speak_with_emotion(response, "positive")

                if hasattr(reachy, 'head'):
                    reachy.head.r_antenna.goal_position = 0
                    reachy.head.l_antenna.goal_position = 0
                    reachy.head.r_eye.goal_position = 0.5
                    reachy.head.l_eye.goal_position = 0.5
                else:
                    try:
                        reachy.goto_target(antennas=[0, 0], duration=0.2)
                    except Exception:
                        pass

        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Reachy Mini Chat v5 with Edge-TTS")
    parser.add_argument('--chat', action='store_true', help='Start interactive chat (requires Reachy Mini)')
    parser.add_argument('--test-tts', action='store_true', help='Test Edge-TTS functionality (requires Reachy Mini)')
    parser.add_argument('--test-compat', action='store_true', help='Test tts.py compatibility (requires Reachy Mini)')
    parser.add_argument('--model', default='qwen3:0.6b', help='Ollama model to use')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()
    app = ChatAppWithEdgeTTS(model=args.model, ollama_url=args.url, debug=args.debug)

    if args.test_tts:
        app.test_edge_tts()
    elif args.test_compat:
        app.test_like_tts_py()
    elif args.chat:
        if not check_runtime_dependencies(require_reachy=True):
            return
        app.start_chat()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
