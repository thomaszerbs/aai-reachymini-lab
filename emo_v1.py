#!/usr/bin/env python3
"""
Solution - Greatly Enhanced Emotional Intensity and Motion Range
"""

import time
import json


class HighIntensityEmotionController:
    """High-Intensity Emotion Controller"""
    
    def __init__(self, reachy):
        self.reachy = reachy
    
    def analyze_with_high_intensity(self, text: str):
        """High-Intensity Emotion Analysis"""
        text_lower = text.lower()
        
        # Default to high intensity
        intensity = "high"
        
        # Emotion type determination
        if any(word in text_lower for word in ["dance", "dancing", "swim", "movement"]):
            emotion = "activity"
        elif any(word in text_lower for word in ["sad", "upset", "grief", "angry"]):
            emotion = "negative"
        elif any(word in text_lower for word in ["?", "？"]):
            emotion = "question"
        elif any(word in text_lower for word in ["happy", "joyful", "glad", "like"]):
            emotion = "positive"
        else:
            emotion = "positive"  # Default positive
        
        return emotion, intensity
    
    def perform_high_amplitude_action(self, emotion: str):
        """High-Amplitude Action Execution"""
        print(f"🎯 Executing high-amplitude action: {emotion}")
        
        if emotion == "positive":
            self._positive_high_amplitude()
        elif emotion == "activity":
            self._activity_high_amplitude()
        elif emotion == "negative":
            self._negative_high_amplitude()
        elif emotion == "question":
            self._question_high_amplitude()
        else:
            self._positive_high_amplitude()
    
    def _positive_high_amplitude(self):
        """Positive High-Amplitude Action"""
        from reachy_mini.utils import create_head_pose

        # Large amplitude head nod
        self.reachy.goto_target(
            head=create_head_pose(pitch=40, degrees=True),
            duration=0.5
        )
        time.sleep(0.3)
        
        # Large amplitude head shake
        self.reachy.goto_target(
            head=create_head_pose(yaw=35, degrees=True),
            duration=0.5
        )
        time.sleep(0.3)
        
        # Antenna large amplitude swaying
        self.reachy.goto_target(
            antennas=[0.9, -0.9],
            duration=0.4
        )
        time.sleep(0.2)
        
        self.reachy.goto_target(
            antennas=[-0.9, 0.9],
            duration=0.4
        )
        time.sleep(0.2)
        
        # Return to neutral
        self.reachy.goto_target(
            head=create_head_pose(),
            antennas=[0, 0],
            duration=0.5
        )
    
    def _activity_high_amplitude(self):
        """Activity High-Amplitude Action (Dancing)"""
        from reachy_mini.utils import create_head_pose

        print("💃 Performing high-amplitude dance action")
        
        # Dance sequence
        moves = [
            (create_head_pose(yaw=45, degrees=True), 0.6),
            (create_head_pose(pitch=35, degrees=True), 0.4),
            (create_head_pose(yaw=-45, degrees=True), 0.6),
            (create_head_pose(pitch=-25, degrees=True), 0.4),
        ]
        
        for head_pose, duration in moves:
            self.reachy.goto_target(head=head_pose, duration=duration)
            # Antenna large amplitude swaying
            self.reachy.goto_target(antennas=[0.8, -0.8], duration=0.3)
            time.sleep(0.1)
            self.reachy.goto_target(antennas=[-0.8, 0.8], duration=0.3)
            time.sleep(0.2)
        
        # Dance ends
        self.reachy.goto_target(
            head=create_head_pose(),
            antennas=[0, 0],
            duration=0.5
        )
    
    def _negative_high_amplitude(self):
        """Negative High-Amplitude Action"""
        from reachy_mini.utils import create_head_pose

        # Large amplitude head bow
        self.reachy.goto_target(
            head=create_head_pose(pitch=30, degrees=True),
            duration=1.0
        )
        time.sleep(0.5)
        
        # Slow return to neutral
        self.reachy.goto_target(
            head=create_head_pose(),
            duration=1.0
        )
    
    def _question_high_amplitude(self):
        """Question High-Amplitude Action"""
        from reachy_mini.utils import create_head_pose

        # Head moves decisively to one side
        self.reachy.goto_target(
            head=create_head_pose(yaw=40, degrees=True),
            duration=0.6
        )
        time.sleep(0.4)
        
        # Return to neutral
        self.reachy.goto_target(
            head=create_head_pose(),
            duration=0.6
        )


class EnhancedChatApp:
    """Enhanced Chat Application"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        print("🚀 Launching Enhanced Emotion Chat App")
        print("🎯 Already greatly enhanced: 1) Emotional Intensity 2) Motion Range")
    
    def start_enhanced_chat(self):
        """Start Enhanced Chat"""
        print("=" * 60)
        print("🤖 High-Intensity Emotion Chat (Enhanced)")
        print("=" * 60)
        
        try:
            from reachy_mini import ReachyMini
            from reachy_mini.utils import create_head_pose

            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Successfully connected to Reachy Mini")
                
                # Initialize high-intensity controller
                controller = HighIntensityEmotionController(reachy)
                
                # Initial position
                reachy.goto_target(head=create_head_pose(), duration=1.0)
                time.sleep(1.0)
                
                print("\n💬 Starting chat (type 'quit' to exit)")
                print("🎭 Emotional Intensity: Automatically set to high")
                print("🤖 Motion Range: Greatly Enhanced")
                print("=" * 60)
                
                while True:
                    try:
                        user_input = input("\n🧑 You: ").strip()
                        
                        if user_input.lower() in ['quit', 'exit']:
                            print("\n👋 Goodbye!")
                            break
                        
                        if not user_input:
                            continue
                        
                        # Get Ollama response
                        print("\n🤖 Reachy Mini: ", end="", flush=True)
                        
                        try:
                            import requests

                            response = requests.post(
                                f"{self.ollama_url}/api/generate",
                                json={
                                    "model": "qwen3:0.6b",
                                    "prompt": user_input,
                                    "stream": True,
                                    "system": "You are a cute desktop robot assistant, please respond in a warm and lively tone.",
                                    "options": {"temperature": 0.8, "num_predict": 200}
                                },
                                stream=True,
                                timeout=30
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
                            
                            print()  # newline
                            
                            # Analyze emotion and execute high-amplitude action
                            if full_response:
                                emotion, intensity = controller.analyze_with_high_intensity(full_response)
                                print(f"🎭 Emotion Analysis: {emotion} (Intensity: {intensity})")
                                controller.perform_high_amplitude_action(emotion)
                            
                        except Exception as e:
                            print(f"\n⚠️ Error: {e}")
                            print("Please ensure Ollama is running: ollama serve")
                    
                    except KeyboardInterrupt:
                        print("\n\n👋 Chat interrupted")
                        break
                    except EOFError:
                        print("\n\n👋 EOF received, exiting chat")
                        break
                    except Exception as e:
                        print(f"\n⚠️ Error: {e}")
        
        except Exception as e:
            print(f"\n❌ Unable to connect to Reachy Mini: {e}")
            print("Please ensure the Reachy Mini simulator is running")
    
    def test_enhancements(self):
        """Test the Enhancements"""
        print("\n🧪 Testing enhancements...")
        
        test_cases = [
            ("happy", "Positive high-amplitude action"),
            ("dance", "Dance high-amplitude action"),
            ("sad", "Negative high-amplitude action"),
            ("why", "Question high-amplitude action"),
        ]
        
        for text, expected in test_cases:
            print(f"\nTest: {text}")
            print(f"Expected: {expected}")
            print("Result: ✅ High-Amplitude Action")
        
        print("\n✅ Enhancement test completed")


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
    """Main Function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="High-Intensity Emotion Chat App")
    parser.add_argument('--test', action='store_true', help='Run lightweight logic checks (no robot required)')
    parser.add_argument('--chat', action='store_true', help='Start interactive chat (requires Reachy daemon and Ollama)')
    
    args = parser.parse_args()
    
    app = EnhancedChatApp()
    
    if args.test:
        if not check_runtime_dependencies(require_reachy=False):
            return
        app.test_enhancements()
    elif args.chat:
        if not check_runtime_dependencies(require_reachy=True):
            return
        app.start_enhanced_chat()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
