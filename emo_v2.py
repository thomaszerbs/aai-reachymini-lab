#!/usr/bin/env python3
from __future__ import annotations
"""
emo_v2.py - Enhanced emotional controller for Reachy Mini with Ollama

Learning from test_actions.py:
1. Uses recorded moves library for richer, pre-defined actions
2. More intuitive API design
3. Enhanced emotion-action mapping with more variety
"""

import time
import json
from typing import Dict, List, Tuple, Optional


def create_head_pose(*args, **kwargs):
    """Lazy wrapper to avoid importing reachy_mini at module import time."""
    from reachy_mini.utils import create_head_pose as _create_head_pose
    return _create_head_pose(*args, **kwargs)


class EmotionRecordedController:
    """Emotion controller using recorded moves library for richer expressions"""
    
    def __init__(self, reachy: ReachyMini, debug: bool = False):
        from reachy_mini.motion.recorded_move import RecordedMoves

        self.reachy = reachy
        self.debug = debug
        self.recorded_moves = RecordedMoves("pollen-robotics/reachy-mini-dances-library")
        
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
        """Execute a recorded move by name (like test_actions.py)"""
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
    
    # Simple action implementations
    def _simple_nod(self, duration: float = 2.0):
        """Simple nodding action"""
        amplitude = 0.6
        cycles = int(duration * 2)  # 2 cycles per second
        
        for _ in range(cycles):
            self.reachy.goto_target(
                head=create_head_pose(pitch=20*amplitude, degrees=True),
                duration=0.25
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=create_head_pose(pitch=-10*amplitude, degrees=True),
                duration=0.25
            )
            time.sleep(0.1)
        
        # Return to center
        self.reachy.goto_target(head=create_head_pose(), duration=0.5)
    
    def _simple_shake(self, duration: float = 2.0):
        """Simple shaking head (no) action"""
        amplitude = 0.7
        cycles = int(duration * 1.5)
        
        for _ in range(cycles):
            self.reachy.goto_target(
                head=create_head_pose(yaw=30*amplitude, degrees=True),
                duration=0.3
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=create_head_pose(yaw=-30*amplitude, degrees=True),
                duration=0.3
            )
            time.sleep(0.1)
        
        self.reachy.goto_target(head=create_head_pose(), duration=0.5)
    
    def _simple_look_curious(self, duration: float = 2.0):
        """Curious look (head tilt)"""
        amplitude = 0.8
        
        self.reachy.goto_target(
            head=create_head_pose(yaw=25*amplitude, pitch=10*amplitude, degrees=True),
            duration=duration/3
        )
        time.sleep(duration/3)
        
        self.reachy.goto_target(
            head=create_head_pose(yaw=-25*amplitude, pitch=10*amplitude, degrees=True),
            duration=duration/3
        )
        time.sleep(duration/3)
        
        self.reachy.goto_target(head=create_head_pose(), duration=duration/3)
    
    def _simple_look_sad(self, duration: float = 2.0):
        """Sad look (head down)"""
        self.reachy.goto_target(
            head=create_head_pose(pitch=30, degrees=True),
            duration=duration/2
        )
        time.sleep(duration/2)
        self.reachy.goto_target(head=create_head_pose(), duration=duration/2)
    
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
            head=create_head_pose(roll=15*amplitude, degrees=True),
            duration=duration/4
        )
        time.sleep(duration/4)
        
        self.reachy.goto_target(
            head=create_head_pose(roll=-15*amplitude, degrees=True),
            duration=duration/4
        )
        time.sleep(duration/4)
        
        self.reachy.goto_target(head=create_head_pose(), duration=duration/2)


class EnhancedChatAppV2:
    """Enhanced chat application with recorded moves integration"""
    
    def __init__(self, model: str = "qwen3:0.6b", ollama_url: str = "http://localhost:11434", debug: bool = False):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.controller = None
        
    def start_chat(self):
        """Start interactive chat session"""
        print("=" * 60)
        print("🤖 Reachy Mini Enhanced Chat v2")
        print("=" * 60)
        print("Features:")
        print("1. Uses recorded moves library for richer expressions")
        print("2. Enhanced emotion detection with emoji support")
        print("3. Intensity-based action selection")
        print("4. Fallback to simple actions")
        print("=" * 60)
        
        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")
                
                # Initialize controller
                self.controller = EmotionRecordedController(reachy, debug=self.debug)
                
                # Go to initial position
                reachy.goto_target(head=create_head_pose(), duration=1.0)
                time.sleep(1.0)
                
                print("\n💬 Start chatting (type 'quit' to exit)")
                print("🎭 Emotions: positive, negative, question, activity")
                print("💪 Intensity: auto-detected from text")
                print("=" * 60)
                
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
                        response = self._get_ollama_response(user_input)
                        
                        if response:
                            # Analyze emotion and execute move
                            emotion, intensity = self.controller.analyze_emotion(response)
                            if self.debug:
                                print(f"\n🎭 Emotion: {emotion} | 💪 Intensity: {intensity}")
                            self.controller.execute_emotion_move(emotion, intensity)
                        
                    except KeyboardInterrupt:
                        print("\n\n👋 Interrupted")
                        break
                    except Exception as e:
                        print(f"\n⚠️ Error: {e}")
        
        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            print("Please ensure Reachy Mini simulator is running")
    
    def _get_ollama_response(self, prompt: str) -> Optional[str]:
        """Get response from Ollama"""
        try:
            import requests

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

            # Check HTTP status first so model-not-found errors surface clearly.
            if response.status_code != 200:
                try:
                    err_data = response.json()
                    err_msg = err_data.get("error", f"HTTP {response.status_code}")
                except Exception:
                    err_msg = f"HTTP {response.status_code}"
                print(f"\n❌ Ollama request failed: {err_msg}")
                print(f"   Requested model: {self.model}")
                print("   Check the model name and ensure it is pulled: ollama list")
                return None

            full_response = ""
            thinking_response = ""
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if self.debug:
                            print(f"\n[DEBUG chunk {chunk_count}] {chunk}")
                        if 'error' in chunk:
                            print(f"\n❌ Ollama error: {chunk['error']}")
                            print(f"   Requested model: {self.model}")
                            return None
                        if 'response' in chunk:
                            content = chunk['response']
                            if content:
                                print(content, end="", flush=True)
                                full_response += content
                            elif self.debug:
                                print("\n[DEBUG] empty response field in chunk")
                        # Thinking/reasoning models (e.g. qwen3, deepseek-r1) stream
                        # content in the 'thinking' field instead of 'response'.
                        if 'thinking' in chunk:
                            thinking_piece = chunk['thinking']
                            if thinking_piece:
                                print(thinking_piece, end="", flush=True)
                                thinking_response += thinking_piece
                            elif self.debug:
                                print("\n[DEBUG] empty thinking field in chunk")
                        if self.debug and 'response' not in chunk and 'thinking' not in chunk:
                            print(f"\n[DEBUG] no 'response' or 'thinking' key in chunk, keys={list(chunk.keys())}")
                        chunk_count += 1
                    except Exception as e:
                        if self.debug:
                            print(f"\n[DEBUG] JSON parse error: {e}, line={line[:200]}")
                        continue

            print()  # New line
            if not full_response and not thinking_response:
                print(f"\n⚠️ Ollama returned empty response (model={self.model}, chunks={chunk_count})")
                print("   Try running with --debug to see raw chunks.")
                print("   Check if the model is loaded correctly: ollama run " + self.model)
            return full_response if full_response else thinking_response

        except requests.exceptions.ConnectionError:
            print(f"\n❌ Cannot connect to Ollama at {self.ollama_url}")
            print("   Please ensure Ollama is running: ollama serve")
            return None
        except Exception as e:
            print(f"\n⚠️ Ollama error: {e}")
            print("   Please ensure Ollama is running: ollama serve")
            return None
    
    def test_all_moves(self):
        """Test all recorded moves (like test_actions.py)"""
        print("🧪 Testing all recorded moves...")
        
        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionRecordedController(reachy, debug=self.debug)
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
    
    def test_emotion_mapping(self):
        """Test emotion mapping to moves"""
        print("🧪 Testing emotion-move mapping...")
        
        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionRecordedController(reachy, debug=self.debug)
                
                test_cases = [
                    ("我非常开心！今天是个好日子！😄", "positive"),
                    ("我有点难过... 😢", "negative"),
                    ("这是什么？为什么会这样？🤔", "question"),
                    ("让我们跳舞吧！💃", "activity"),
                ]
                
                for text, expected_emotion in test_cases:
                    print(f"\nText: {text}")
                    emotion, intensity = controller.analyze_emotion(text)
                    print(f"Detected: {emotion} (intensity: {intensity})")
                    print(f"Expected: {expected_emotion}")
                    
                    if emotion == expected_emotion:
                        print("✅ Match!")
                    else:
                        print("⚠️ Mismatch")
                    
                    # Show available moves for this emotion
                    available = controller.emotion_to_moves.get(emotion, [])
                    print(f"Available moves: {len(available)}")
                    if available:
                        print(f"  Sample: {available[0]}")
        
        except Exception as e:
            print(f"❌ Error: {e}")


def check_runtime_dependencies(require_reachy: bool = False) -> bool:
    """Check optional runtime dependencies and print actionable hints."""
    ok = True

    try:
        import requests as _requests  # noqa: F401
    except Exception:
        ok = False
        print("❌ Missing Python package: requests")
        print("   Install in this project: . .venv/bin/activate && pip install -r requirements.txt")

    if require_reachy:
        try:
            import reachy_mini  # noqa: F401
        except Exception:
            ok = False
            print("❌ Missing Python package: reachy-mini")
            print("   Install in this project: . .venv/bin/activate && pip install \"reachy-mini[mujoco]\"")

    return ok


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Reachy Mini Enhanced Chat v2")
    parser.add_argument('--chat', action='store_true', help='Start interactive chat (requires Reachy daemon and Ollama)')
    parser.add_argument('--test-moves', action='store_true', help='Play all recorded moves (requires Reachy daemon)')
    parser.add_argument('--test-emotions', action='store_true', help='Test emotion mapping and available moves (requires Reachy daemon)')
    parser.add_argument('--model', default='qwen3:0.6b', help='Ollama model to use')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    app = EnhancedChatAppV2(model=args.model, ollama_url=args.url, debug=args.debug)
    
    if args.test_moves:
        if not check_runtime_dependencies(require_reachy=True):
            return
        app.test_all_moves()
    elif args.test_emotions:
        if not check_runtime_dependencies(require_reachy=True):
            return
        app.test_emotion_mapping()
    elif args.chat:
        if not check_runtime_dependencies(require_reachy=True):
            return
        app.start_chat()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
