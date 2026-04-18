#!/usr/bin/env python3
"""
emo_v4.py - Enhanced emotional controller for Reachy Mini with TTS & Ollama

Key features:
1. Text-to-Speech integration (Piper TTS)
2. Parallel actions during speech
3. Emotional voice modulation
4. Lip-sync simulation with antennas
5. Enhanced from emo_v3.py
"""

import time
import json
import threading
import subprocess
import tempfile
import os
import queue
import platform
from typing import Dict, List, Tuple, Optional, Callable


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


class TTSEngine:
    """Text-to-Speech engine with emotional modulation"""
    
    def __init__(self, tts_backend: str = "piper", voice_model: str = "en_US-lessac-medium"):
        self.tts_backend = tts_backend
        self.voice_model = voice_model
        self.audio_queue = queue.Queue()
        self.is_playing = False
        
        # Voice parameters for different emotions
        self.voice_params = {
            'positive': {'speed': 1.1, 'pitch': 1.2, 'volume': 1.0},
            'negative': {'speed': 0.9, 'pitch': 0.9, 'volume': 0.8},
            'question': {'speed': 1.0, 'pitch': 1.1, 'volume': 1.0},
            'activity': {'speed': 1.2, 'pitch': 1.1, 'volume': 1.1},
            'neutral': {'speed': 1.0, 'pitch': 1.0, 'volume': 1.0},
        }
        
        # Check if espeak is available (we use espeak as the only TTS)
        self.espeak_available = self._check_espeak_available()
        
    def _check_espeak_available(self) -> bool:
        """Check if espeak (or espeak-ng) is available on PATH."""
        try:
            system = platform.system()
            if system == "Windows":
                result = subprocess.run(['where', 'espeak'], capture_output=True, text=True, shell=True)
                if result.returncode != 0:
                    result = subprocess.run(['where', 'espeak-ng'], capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(['which', 'espeak'], capture_output=True, text=True)
                if result.returncode != 0:
                    result = subprocess.run(['which', 'espeak-ng'], capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip().split('\n')[0]
                print(f"✅ espeak found at: {path}")
                return True
            else:
                print("⚠️ espeak not found on PATH. Install espeak to enable TTS.")
                return False
        except Exception as e:
            print(f"⚠️ Error checking espeak: {e}")
            return False
    
    def synthesize_speech(self, text: str, emotion: str = 'neutral', output_file: str = None) -> Optional[str]:
        """Synthesize speech with emotional modulation"""
        params = self.voice_params.get(emotion, self.voice_params['neutral'])
        
        try:
            # We exclusively use espeak for TTS
            if not self.espeak_available:
                if output_file is None:
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                        output_file = f.name
                return self._fallback_tts(text, output_file)

            if output_file is None:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    output_file = f.name

            # Use espeak to generate WAV on stdout and write to file
            cmd = ['espeak', '--stdout', text]
            result = subprocess.run(cmd, capture_output=True, check=True)
            if result.stdout:
                with open(output_file, 'wb') as f:
                    f.write(result.stdout)
                print("✅ Synthesized with espeak")
                return output_file
            else:
                print("⚠️ espeak produced no output")
                return None
        except Exception as e:
            print(f"❌ TTS synthesis error: {e}")
            return None
    
    def _fallback_tts(self, text: str, output_file: str) -> Optional[str]:
        """Fallback TTS methods (cross-platform)"""
        import platform
        
        system = platform.system()
        
        # macOS specific
        if system == "Darwin":
            try:
                # Try macOS say command with different formats
                for format_ext in ['.aiff', '.wav', '.caf']:
                    try:
                        audio_file = output_file.replace('.wav', format_ext)
                        subprocess.run(['say', '-o', audio_file, text], check=True, capture_output=True)
                        if os.path.exists(audio_file):
                            print(f"✅ Using macOS 'say' command ({format_ext})")
                            return audio_file
                    except:
                        continue
                
                # Try direct playback
                print("🗣️ Speaking directly (macOS)...")
                subprocess.run(['say', text], check=True, capture_output=True)
                return "direct_playback"
            except Exception as e:
                print(f"⚠️ macOS say failed: {e}")
        
        # Windows specific
        elif system == "Windows":
            try:
                # Try Windows built-in TTS via PowerShell
                ps_script = f"""
                Add-Type -AssemblyName System.speech
                $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $speak.Speak("{text.replace('"', '\\"')}")
                """
                subprocess.run(['powershell', '-Command', ps_script], check=True, capture_output=True)
                print("✅ Using Windows System.Speech")
                return "direct_playback"
            except Exception as e:
                print(f"⚠️ Windows TTS failed: {e}")
                
            try:
                # Try pyttsx3 if installed
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                print("✅ Using pyttsx3")
                return "direct_playback"
            except ImportError:
                print("⚠️ pyttsx3 not installed")
            except Exception as e:
                print(f"⚠️ pyttsx3 failed: {e}")
        
        # Linux/Unix (including macOS if say failed)
        try:
            # Try espeak (available on Linux, installable on macOS/Windows)
            cmd = ['espeak', '--stdout', text]
            result = subprocess.run(cmd, capture_output=True, check=True)
            if result.stdout:
                with open(output_file, 'wb') as f:
                    f.write(result.stdout)
                print("✅ Using espeak")
                return output_file
        except Exception as e:
            print(f"⚠️ espeak failed: {e}")
        
        # Platform-independent fallback
        try:
            # Try gTTS (requires internet)
            from gtts import gTTS
            tts = gTTS(text=text, lang='en')
            tts.save(output_file)
            if os.path.exists(output_file):
                print("✅ Using gTTS (internet required)")
                return output_file
        except ImportError:
            print("⚠️ gTTS not installed")
        except Exception as e:
            print(f"⚠️ gTTS failed: {e}")
        
        print("❌ No TTS backend available")
        return None
    
    def play_audio(self, audio_file: str):
        """Play audio file (cross-platform)"""
        import platform
        
        if audio_file == "direct_playback":
            # Already played directly by TTS engine
            return
        
        if not audio_file or not os.path.exists(audio_file):
            return
        
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                # Try afplay first
                if subprocess.run(['which', 'afplay'], capture_output=True).returncode == 0:
                    subprocess.Popen(['afplay', audio_file])
                else:
                    # Fallback to sox or ffplay
                    subprocess.Popen(['play', audio_file])
                    
            elif system == "Windows":
                # Try winsound for WAV files
                if audio_file.endswith('.wav'):
                    import winsound
                    winsound.PlaySound(audio_file, winsound.SND_FILENAME)
                else:
                    # Use Windows Media Player command
                    subprocess.Popen(['cmd', '/c', 'start', '/wait', audio_file], shell=True)
                    
            else:  # Linux/Unix
                # Try aplay (ALSA)
                if subprocess.run(['which', 'aplay'], capture_output=True).returncode == 0:
                    subprocess.Popen(['aplay', audio_file])
                # Try paplay (PulseAudio)
                elif subprocess.run(['which', 'paplay'], capture_output=True).returncode == 0:
                    subprocess.Popen(['paplay', audio_file])
                # Try ffplay (FFmpeg)
                elif subprocess.run(['which', 'ffplay'], capture_output=True).returncode == 0:
                    subprocess.Popen(['ffplay', '-nodisp', '-autoexit', audio_file])
                # Try sox
                elif subprocess.run(['which', 'play'], capture_output=True).returncode == 0:
                    subprocess.Popen(['play', audio_file])
                else:
                    print("⚠️ No audio player found")
                    
        except Exception as e:
            print(f"⚠️ Audio playback error: {e}")
    
    def speak_with_emotion(self, text: str, emotion: str = 'neutral'):
        """Synthesize and play speech with emotional modulation"""
        if not text.strip():
            return

        audio_file = self.synthesize_speech(text, emotion)
        
        if audio_file:
            # Play audio
            self.play_audio(audio_file)
            
            # Clean up temp file after playback
            def cleanup():
                time.sleep(5)  # Wait for playback to finish
                try:
                    os.unlink(audio_file)
                except OSError:
                    pass
            
            cleanup_thread = threading.Thread(target=cleanup, daemon=True)
            cleanup_thread.start()
            
            return audio_file
        return None


class LipSyncController:
    """Simple lip-sync simulation using antennas"""
    
    def __init__(self, reachy):
        self.reachy = reachy
        self.is_speaking = False
        self.sync_thread = None
        
    def start_lip_sync(self, text: str, speech_duration: float):
        """Start lip-sync animation during speech"""
        self.is_speaking = True
        
        def lip_sync_animation():
            words = text.split()
            word_count = len(words)
            if word_count == 0:
                return
            
            # Estimate time per word
            time_per_word = speech_duration / word_count
            
            for i in range(int(speech_duration * 2)):  # Twice per second
                if not self.is_speaking:
                    break
                
                # Alternate antenna movements for "speaking" effect
                left_val = 0.3 if i % 2 == 0 else -0.3
                right_val = -0.3 if i % 2 == 0 else 0.3
                
                self.reachy.goto_target(
                    antennas=[left_val, right_val],
                    duration=0.1
                )
                time.sleep(0.05)
            
            # Return to neutral
            self.reachy.goto_target(antennas=[0, 0], duration=0.2)
        
        self.sync_thread = threading.Thread(target=lip_sync_animation, daemon=True)
        self.sync_thread.start()
    
    def stop_lip_sync(self):
        """Stop lip-sync animation"""
        self.is_speaking = False
        if self.sync_thread:
            self.sync_thread.join(timeout=0.5)
        # Return antennas to neutral
        self.reachy.goto_target(antennas=[0, 0], duration=0.2)


class EmotionControllerV4:
    """Enhanced emotion controller with TTS integration"""
    
    def __init__(self, reachy, debug: bool = False):
        self.reachy = reachy
        self.debug = debug
        from reachy_mini.motion.recorded_move import RecordedMoves
        self.recorded_moves = RecordedMoves("pollen-robotics/reachy-mini-dances-library")
        self.tts_engine = TTSEngine()
        self.lip_sync = LipSyncController(reachy)
        
        # Map moves to emotions based on their descriptions
        self._categorize_recorded_moves()
        
        # Still keep custom simple actions for quick responses
        self.simple_actions = {
            'nod': self._simple_nod,
            'shake': self._simple_shake,
            'look_curious': self._simple_look_curious,
            'look_sad': self._simple_look_sad,
            'excited_wiggle': self._simple_excited_wiggle,
            'thoughtful_tilt': self._simple_thoughtful_tilt,
        }
    
    def _categorize_recorded_moves(self):
        """Categorize recorded moves by emotion type"""
        all_moves = self.recorded_moves.list_moves()
        
        # Analyze move descriptions to categorize
        self.emotion_to_moves = {
            'positive': [],      # Happy, excited
            'negative': [],      # Sad, disappointed
            'question': [],      # Curious, thinking
            'activity': [],      # Energetic, dancing
            'neutral': [],       # Default, calm
        }
        
        # Keyword mapping for move descriptions
        emotion_keywords = {
            'positive': ['happy', 'joy', 'excited', 'yes', 'nod', 'positive', 'good'],
            'negative': ['stumble', 'recover', 'recoil', 'sad', 'low', 'negative'],
            'question': ['curious', 'thinking', 'wonder', 'question', 'peek', 'glance'],
            'activity': ['dance', 'sway', 'spin', 'groovy', 'rhythm', 'swing', 'movement'],
            'neutral': ['simple', 'basic', 'neutral', 'calm'],
        }
        
        for move_name in all_moves:
            move = self.recorded_moves.get(move_name)
            desc = move.description.lower() if move.description else ""
            
            # Find best matching emotion
            best_match = 'neutral'
            best_score = 0
            
            for emotion, keywords in emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in desc)
                if score > best_score:
                    best_score = score
                    best_match = emotion
            
            self.emotion_to_moves[best_match].append(move_name)
            if self.debug:
                print(f"🔍 Categorized '{move_name}' as {best_match} (score: {best_score})")
    
    def analyze_emotion(self, text: str) -> Tuple[str, str]:
        """Analyze text emotion with improved detection"""
        text_lower = text.lower()
        
        # Emotion keywords (enhanced from v1)
        positive_words = ['开心', '快乐', '高兴', '喜欢', '爱', '谢谢', '感谢', '好', '棒', '完美',
                         'excited', 'happy', 'joy', 'love', 'thanks', 'good', 'great', 'awesome']
        negative_words = ['伤心', '难过', '悲伤', '生气', '失望', '抱歉', '对不起', '不好', '坏',
                         'sad', 'angry', 'sorry', 'disappointed', 'bad', 'wrong', 'hate']
        question_words = ['吗', '？', '?', '为什么', '怎么', '如何', 'what', 'why', 'how', 'when']
        activity_words = ['跳舞', '舞蹈', '运动', '活动', '动起来', 'dance', 'move', 'action', 'play']
        
        # Count matches
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        ques_count = sum(1 for word in question_words if word in text_lower)
        act_count = sum(1 for word in activity_words if word in text_lower)
        
        # Emoji detection
        emoji_pos = ['😊', '😄', '😍', '👍', '🥰', '😎', '🎉', '❤️', '😂', '🤗']
        emoji_neg = ['😢', '😭', '😡', '👎', '😔', '😞', '😤', '💔']
        emoji_ques = ['🤔', '❓', '⁉️', '💭', '🧐', '🔍']
        emoji_act = ['💃', '🕺', '🎵', '🎶', '⚽', '🏀', '🎮']
        
        # Add emoji scores
        pos_count += sum(1 for emoji in emoji_pos if emoji in text)
        neg_count += sum(1 for emoji in emoji_neg if emoji in text)
        ques_count += sum(1 for emoji in emoji_ques if emoji in text)
        act_count += sum(1 for emoji in emoji_act if emoji in text)
        
        # Determine emotion type
        scores = {
            'positive': pos_count,
            'negative': neg_count,
            'question': ques_count,
            'activity': act_count
        }
        
        emotion_type = max(scores, key=scores.get)
        
        # Determine intensity
        total_score = sum(scores.values())
        if total_score >= 3:     # High confidence
            intensity = 'high'
        elif total_score >= 1:   # Medium confidence
            intensity = 'medium'
        else:                    # Low confidence
            intensity = 'low'
            
        return emotion_type, intensity
    
    def execute_recorded_move(self, move_name: str, initial_goto_duration: float = 1.0):
        """Execute a recorded move by name"""
        if self.debug:
            print(f"🎬 Playing recorded move: {move_name}")
        move = self.recorded_moves.get(move_name)
        self.reachy.play_move(move, initial_goto_duration=initial_goto_duration)
    
    def execute_emotion_move(self, emotion_type: str, intensity: str = 'medium'):
        """Execute appropriate move based on emotion and intensity"""
        available_moves = self.emotion_to_moves.get(emotion_type, [])
        
        if available_moves:
            # Select move based on intensity
            if intensity == 'high' and len(available_moves) > 1:
                # For high intensity, pick more energetic moves (later in list often)
                move_name = available_moves[-1]
            elif intensity == 'low' and len(available_moves) > 1:
                # For low intensity, pick simpler moves
                move_name = available_moves[0]
            else:
                # Medium intensity or only one move available
                import random
                move_name = random.choice(available_moves)
            
            # Adjust duration based on intensity
            duration_map = {'high': 0.8, 'medium': 1.0, 'low': 1.2}
            duration = duration_map.get(intensity, 1.0)
            
            if self.debug:
                print(f"🎭 Selected move '{move_name}' for {emotion_type} ({intensity})")
            
            self.execute_recorded_move(move_name, duration)
        else:
            # Fallback to simple actions
            if self.debug:
                print(f"⚠️ No recorded moves for {emotion_type}, using simple action")
            self._execute_simple_action(emotion_type, intensity)
    
    def _execute_simple_action(self, emotion_type: str, intensity: str):
        """Fallback to simple custom actions"""
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
    
    def speak_with_expression(self, text: str, emotion: str = 'neutral', intensity: str = 'medium', 
                              execute_movement: bool = False):
        """Speak text with emotional expression
        
        Args:
            text: Text to speak
            emotion: Emotion type (positive, negative, question, activity, neutral)
            intensity: Emotion intensity (high, medium, low)
            execute_movement: Whether to execute movement (set False if already done)
        """
        if not text.strip():
            return
        
        if self.debug:
            print(f"🗣️ Speaking with {emotion} emotion ({intensity} intensity)")
        
        # Estimate speech duration (approx 150 words per minute)
        word_count = len(text.split())
        estimated_duration = max(1.0, word_count / 2.5)  # 150 WPM
        
        # Start lip sync
        self.lip_sync.start_lip_sync(text, estimated_duration)
        
        # Start TTS in background
        tts_thread = threading.Thread(
            target=self.tts_engine.speak_with_emotion,
            args=(text, emotion),
            daemon=True
        )
        tts_thread.start()
        
        # Only execute movement if requested (usually already done)
        if execute_movement:
            action_thread = threading.Thread(
                target=self.execute_emotion_move,
                args=(emotion, intensity),
                daemon=True
            )
            action_thread.start()
        
        # Wait for speech to complete
        time.sleep(estimated_duration)
        
        # Stop lip sync
        self.lip_sync.stop_lip_sync()
    
    # Simple action implementations (same as v2/v3)
    def _simple_nod(self, duration: float = 2.0):
        """Simple nodding action"""
        amplitude = 0.6
        cycles = int(duration * 2)  # 2 cycles per second
        
        for _ in range(cycles):
            self.reachy.goto_target(
                head=_create_head_pose(pitch=20*amplitude, degrees=True),
                duration=0.25
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=_create_head_pose(pitch=-10*amplitude, degrees=True),
                duration=0.25
            )
            time.sleep(0.1)
        
        # Return to center
        self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
    
    def _simple_shake(self, duration: float = 2.0):
        """Simple shaking head (no) action"""
        amplitude = 0.7
        cycles = int(duration * 1.5)
        
        for _ in range(cycles):
            self.reachy.goto_target(
                head=_create_head_pose(yaw=30*amplitude, degrees=True),
                duration=0.3
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=_create_head_pose(yaw=-30*amplitude, degrees=True),
                duration=0.3
            )
            time.sleep(0.1)
        
        self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
    
    def _simple_look_curious(self, duration: float = 2.0):
        """Curious look (head tilt)"""
        amplitude = 0.8
        
        self.reachy.goto_target(
            head=_create_head_pose(yaw=25*amplitude, pitch=10*amplitude, degrees=True),
            duration=duration/3
        )
        time.sleep(duration/3)
        
        self.reachy.goto_target(
            head=_create_head_pose(yaw=-25*amplitude, pitch=10*amplitude, degrees=True),
            duration=duration/3
        )
        time.sleep(duration/3)
        
        self.reachy.goto_target(head=_create_head_pose(), duration=duration/3)
    
    def _simple_look_sad(self, duration: float = 2.0):
        """Sad look (head down)"""
        self.reachy.goto_target(
            head=_create_head_pose(pitch=30, degrees=True),
            duration=duration/2
        )
        time.sleep(duration/2)
        self.reachy.goto_target(head=_create_head_pose(), duration=duration/2)
    
    def _simple_excited_wiggle(self, duration: float = 2.0):
        """Excited antenna wiggling"""
        cycles = int(duration * 3)
        
        for i in range(cycles):
            left_val = 0.7 if i % 2 == 0 else -0.7
            right_val = -0.7 if i % 2 == 0 else 0.7
            
            self.reachy.goto_target(
                antennas=[left_val, right_val],
                duration=0.15
            )
            time.sleep(0.05)
        
        self.reachy.goto_target(antennas=[0, 0], duration=0.3)
    
    def _simple_thoughtful_tilt(self, duration: float = 2.0):
        """Thoughtful head tilting"""
        amplitude = 0.6
        
        self.reachy.goto_target(
            head=_create_head_pose(roll=15*amplitude, degrees=True),
            duration=duration/4
        )
        time.sleep(duration/4)
        
        self.reachy.goto_target(
            head=_create_head_pose(roll=-15*amplitude, degrees=True),
            duration=duration/4
        )
        time.sleep(duration/4)
        
        self.reachy.goto_target(head=_create_head_pose(), duration=duration/2)


class ChatAppWithTTS:
    """Chat application with Text-to-Speech integration"""
    
    def __init__(self, model: str = "qwen3:0.6b", ollama_url: str = "http://localhost:11434", debug: bool = False):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.controller = None
        self.tts_enabled = True
        
    def start_chat(self):
        """Start interactive chat session with TTS"""
        if not check_runtime_dependencies(require_reachy=True):
            return
        from reachy_mini import ReachyMini
        print("=" * 60)
        print("🤖 Reachy Mini Chat v4 with TTS")
        print("=" * 60)
        print("Features:")
        print("1. Text-to-Speech (Piper/macOS say/espeak)")
        print("2. Emotional voice modulation")
        print("3. Lip-sync simulation")
        print("4. Parallel actions during speech")
        print("5. Recorded moves library")
        print("=" * 60)
        
        try:
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")
                
                # Initialize controller
                self.controller = EmotionControllerV4(reachy, debug=self.debug)
                
                # Go to initial position
                reachy.goto_target(head=_create_head_pose(), duration=1.0)
                time.sleep(1.0)
                
                print("\n💬 Start chatting (type 'quit' to exit)")
                print("🎭 Emotions: positive, negative, question, activity")
                print("🗣️ TTS: Enabled (use --no-tts to disable)")
                print("=" * 60)
                
                eof_count = 0
                while True:
                    try:
                        user_input = input("\n🧑 You: ").strip()
                        
                        if user_input.lower() in ['quit', 'exit', 'q']:
                            print("\n👋 Goodbye!")
                            break
                        
                        if not user_input:
                            continue
                        
                        # Get Ollama response
                        print("\n🤖 Reachy Mini: ", end="", flush=True)
                        response = self._get_ollama_response_parallel(user_input)
                        
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
        
        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            print("Please ensure Reachy Mini simulator is running")
    
    def _get_ollama_response_parallel(self, prompt: str) -> Optional[str]:
        """Get response from Ollama with improved TTS timing"""
        import requests
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "system": "You are a cute desktop robot assistant. Respond with enthusiasm and warmth.",
                    "options": {"temperature": 0.8, "num_predict": 200}
                },
                stream=True,
                timeout=30
            )
            if response.status_code != 200:
                print(f"\n❌ Ollama returned HTTP {response.status_code}")
                return None
            
            full_response = ""
            buffer = ""
            emotion_detected = False
            detected_emotion = "neutral"
            detected_intensity = "medium"
            min_chars_for_emotion = 15  # Increased for better emotion detection
            
            # Phase 1: Stream text and detect emotion (but don't speak yet)
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
                            buffer += content
                            
                            # Detect emotion early for immediate action
                            if not emotion_detected and len(buffer) >= min_chars_for_emotion:
                                if self.controller:
                                    detected_emotion, detected_intensity = self.controller.analyze_emotion(buffer)
                                    if self.debug:
                                        print(f"\n🎭 Early emotion: {detected_emotion} (intensity: {detected_intensity})")
                                    
                                    # Start action immediately (but NOT TTS yet)
                                    self.controller.execute_emotion_move(detected_emotion, detected_intensity)
                                    emotion_detected = True
                    except Exception:
                        if self.debug:
                            import traceback
                            traceback.print_exc()
                        continue
            
            print()  # New line after streaming
            
            # Phase 2: After complete response, speak the full sentence
            if full_response and self.controller:
                if not emotion_detected:
                    # If we never detected emotion, analyze from full response
                    detected_emotion, detected_intensity = self.controller.analyze_emotion(full_response)
                    if self.debug:
                        print(f"\n🎭 Final emotion: {detected_emotion} (intensity: {detected_intensity})")
                
                if self.tts_enabled:
                    # Speak the COMPLETE response
                    if self.debug:
                        print(f"🗣️ Speaking complete response ({len(full_response)} chars)")
                    
                    # Use threading for non-blocking TTS (movement already executed)
                    tts_thread = threading.Thread(
                        target=self.controller.speak_with_expression,
                        args=(full_response, detected_emotion, detected_intensity, False),  # execute_movement=False
                        daemon=True
                    )
                    tts_thread.start()
                    
                    # Optionally wait a bit for TTS to start
                    time.sleep(0.1)
                else:
                    # If TTS disabled, just ensure action happened
                    if not emotion_detected:
                        self.controller.execute_emotion_move(detected_emotion, detected_intensity)
            
            return full_response
            
        except Exception as e:
            print(f"\n⚠️ Ollama error: {e}")
            print("Please ensure Ollama is running: ollama serve")
            return None
    
    def test_tts(self):
        """Test TTS functionality"""
        if not check_runtime_dependencies(require_reachy=True):
            return
        from reachy_mini import ReachyMini
        print("🧪 Testing TTS functionality...")
        
        test_sentences = [
            ("Hello! I am Reachy Mini!", "positive"),
            ("I am feeling a bit sad today.", "negative"),
            ("What is the meaning of life?", "question"),
            ("Let's dance and have fun!", "activity"),
        ]
        
        try:
            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV4(reachy, debug=self.debug)
                
                for text, emotion in test_sentences:
                    print(f"\nTesting: '{text}'")
                    print(f"Emotion: {emotion}")
                    
                    controller.speak_with_expression(text, emotion, execute_movement=True)
                    time.sleep(2.0)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            # Test TTS without robot
            print("\nTesting TTS without robot...")
            tts_engine = TTSEngine()
            for text, emotion in test_sentences[:1]:  # Just test first one
                print(f"\nTesting TTS: '{text}'")
                tts_engine.speak_with_emotion(text, emotion)
                time.sleep(3.0)
    
    def test_all_moves(self):
        """Test all recorded moves"""
        if not check_runtime_dependencies(require_reachy=True):
            return
        from reachy_mini import ReachyMini
        print("🧪 Testing all recorded moves...")
        
        try:
            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV4(reachy, debug=self.debug)
                all_moves = controller.recorded_moves.list_moves()
                
                print(f"\nFound {len(all_moves)} recorded moves:")
                for i, move_name in enumerate(all_moves, 1):
                    print(f"{i:2d}. {move_name}")
                
                print("\nPlaying each move...")
                for move_name in all_moves:
                    print(f"\n🎬 Playing: {move_name}")
                    controller.execute_recorded_move(move_name)
                    time.sleep(0.5)  # Brief pause between moves
        
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Reachy Mini Chat v4 with TTS")
    parser.add_argument('--chat', action='store_true', help='Start interactive chat (requires Reachy Mini)')
    parser.add_argument('--test-moves', action='store_true', help='Test all recorded moves (requires Reachy Mini)')
    parser.add_argument('--test-tts', action='store_true', help='Test TTS functionality (requires Reachy Mini)')
    parser.add_argument('--model', default='qwen3:0.6b', help='Ollama model to use')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--no-tts', action='store_true', help='Disable TTS')
    
    args = parser.parse_args()
    
    app = ChatAppWithTTS(model=args.model, ollama_url=args.url, debug=args.debug)
    app.tts_enabled = not args.no_tts
    
    if args.test_tts:
        app.test_tts()
    elif args.test_moves:
        app.test_all_moves()
    elif args.chat:
        if not check_runtime_dependencies(require_reachy=True):
            return
        app.start_chat()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
