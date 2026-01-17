#!/usr/bin/env python3
"""
Example usage of the Reachy Mini Ollama Chat App.

This script demonstrates various ways to use the app.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def example_1_basic_chat():
    """Example 1: Basic interactive chat."""
    print("=" * 60)
    print("Example 1: Basic Interactive Chat")
    print("=" * 60)
    print("\nTo run a basic interactive chat session:")
    print("\nCommand:")
    print("  python app.py")
    print("\nOr with custom model:")
    print("  python app.py --model llama3.2:3b")
    print("\nThis will:")
    print("  1. Connect to Reachy Mini simulation")
    print("  2. Start an interactive chat session")
    print("  3. Reachy Mini will move during Ollama responses")
    print("  4. Type '/help' for available commands")
    print("=" * 60)

def example_2_test_mode():
    """Example 2: Test mode without Ollama."""
    print("\n" + "=" * 60)
    print("Example 2: Test Mode")
    print("=" * 60)
    print("\nTo test Reachy Mini actions without Ollama:")
    print("\nCommand:")
    print("  python app.py --test")
    print("\nThis will:")
    print("  1. Connect to Reachy Mini simulation")
    print("  2. Run random actions for 10 seconds")
    print("  3. Disconnect cleanly")
    print("=" * 60)

def example_3_programmatic_use():
    """Example charge 3: Programmatic use of the controller."""
    print("\n" + "=" * 60)
    print("Example 3: Programmatic Use")
    print("=" * 60)
    
    code_example = '''import time
from app import ReachyOllamaController

# Create controller
controller = ReachyOllamaController(model="qwen3:0.6b")

try:
    # Connect to Reachy Mini
    controller.connect_reachy()
    
    # Perform specific actions
    print("Testing individual actions...")
    controller.actions['nod'](2.0)
    time.sleep(1)
    controller.actions['shake'](2.0)
    time.sleep(1)
    
    # Start continuous random actions
    print("Starting continuous random actions...")
    controller.continuous_random_actions()
    time.sleep(5)  # Let it run for 5 seconds
    
    # Stop continuous actions
    controller.stop_continuous_actions()
    
    # Chat with Ollama
    print("\\nChatting with Ollama...")
    response = controller.chat_with_ollama("Hello, how are you?")
    print(f"Response: {response}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    # Cleanup
    controller.disconnect_reachy()
'''
    
    print("\nProgrammatic usage example:")
    print(code_example)
    print("=" * 60)

def example_4_custom_actions():
    """Example 4: Adding custom actions."""
    print("\n" + "=" * 60)
    print("Example 4: Adding Custom Actions")
    print("=" * 60)
    
    code_example = '''from app import ReachyOllamaController

class CustomReachyController(ReachyOllamaController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add custom actions
        self.actions.update({
            'wave': self.wave_hello,
            'dance': self.dance_movement,
        })
    
    def wave_hello(self, duration=3.0):
        """Wave hello by moving head side to side."""
        if not self.reachy:
            return
            
        # Wave pattern
        for _ in range(3):
            self.reachy.goto_target(
                head=create_head_pose(yaw=30, degrees=True),
                duration=0.3
            )
            time.sleep(0.2)
            self.reachy.goto_target(
                head=create_head_pose(yaw=-30, degrees=True),
                duration=0.3
            )
            time.sleep(0.2)
        
        # Return to center
        self.reachy.goto_target(
            head=create_head_pose(yaw=0, degrees=True),
            duration=0.5
        )
    
    def dance_movement(self, duration=4.0):
        """Dance movement with complex pattern."""
        if not self.reachy:
            return
            
        steps = int(duration / 0.2)
        for i in range(steps):
            # Complex dance pattern
            pitch = 20 * math.sin(2 * math.pi * i / steps)
            yaw = 30 * math.cos(2 * math.pi * i / steps)
            left_antenna = 0.5 * math.sin(2 * math.pi * i / steps * 2)
            right_antenna = 0.5 * math.cos(2 * math.pi * i / steps * 2)
            
            self.reachy.set_target(
                head=create_head_pose(pitch=pitch, yaw=yaw, degrees=True),
                antennas=[left_antenna, right_antenna]
            )
            time.sleep(0.2)
        
        # Return to neutral
        self.reachy.set_target(
            head=create_head_pose(),
            antennas=[0, 0]
        )

# Usage
controller = CustomReachyController()
print(f"Available actions: {list(controller.actions.keys())}")
'''
    
    print("\nHow to add custom actions:")
    print(code_example)
    print("=" * 60)

def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("REACHY MINI OLLAMA APP - USAGE EXAMPLES")
    print("=" * 60)
    
    example_1_basic_chat()
    example_2_test_mode()
    example_3_programmatic_use()
    example_4_custom_actions()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nKey Files:")
    print("  app.py - Main application")
    print("  test_simple.py - Basic tests")
    print("  example_usage.py - This file")
    print("  README.md - Documentation")
    print("  requirements.txt - Dependencies")
    
    print("\nQuick Start:")
    print("  1. Ensure Ollama is running: `ollama serve`")
    print("  2. Pull the model: `ollama pull qwen3:0.6b`")
    print("  3. Start Reachy Mini simulation")
    print("  4. Run: `python app.py --test` (to test)")
    print("  5. Run: `python app.py` (for chat)")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()