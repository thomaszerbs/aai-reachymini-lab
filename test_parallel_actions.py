#!/usr/bin/env python3
"""
test_parallel_actions.py - Test parallel action execution

Demonstrates the difference between:
1. Sequential actions (emo_v2.py): Text → Analysis → Action
2. Parallel actions (emo_v3.py): Text & Action happen together
"""

import time
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose


def test_sequential_vs_parallel():
    """Test and compare sequential vs parallel action execution"""
    
    print("\n" + "="*60)
    print("Testing Sequential vs Parallel Actions")
    print("="*60)
    
    # Test 1: Sequential timing (like emo_v2)
    print("\n1. SEQUENTIAL EXECUTION (emo_v2 style):")
    print("   Text output → Emotion analysis → Action execution")
    
    with ReachyMini(media_backend='no_media') as reachy:
        # Simulate text streaming
        text = "Hello! I'm so happy to see you today! 😄"
        print(f"\n   Text: '{text}'")
        
        # Simulate sequential flow
        print("   [Text streaming...]", end="", flush=True)
        for char in text:
            print(char, end="", flush=True)
            time.sleep(0.05)  # Simulate streaming delay
        
        print("\n   [Text complete]")
        print("   [Analyzing emotion...]")
        time.sleep(0.5)  # Simulate analysis time
        
        print("   [Executing action...]")
        # Simple nod action
        reachy.goto_target(head=create_head_pose(pitch=20, degrees=True), duration=0.5)
        time.sleep(0.3)
        reachy.goto_target(head=create_head_pose(pitch=-10, degrees=True), duration=0.5)
        time.sleep(0.3)
        reachy.goto_target(head=create_head_pose(), duration=0.5)
        
        print("   ✅ Sequential execution complete")
        time.sleep(1.0)
    
    # Test 2: Parallel timing (like emo_v3)
    print("\n2. PARALLEL EXECUTION (emo_v3 style):")
    print("   Text output & Action execution happen together")
    
    with ReachyMini(media_backend='no_media') as reachy:
        text = "Hello! I'm so happy to see you today! 😄"
        print(f"\n   Text: '{text}'")
        
        # Simulate parallel flow
        print("   [Text streaming with parallel action...]", end="", flush=True)
        
        # Start action after first few words
        words = text.split()
        for i, word in enumerate(words):
            print(f"{word} ", end="", flush=True)
            time.sleep(0.1)  # Simulate streaming delay
            
            # Start action after 3 words
            if i == 2:
                print("\n   [Starting action in parallel...]", end="", flush=True)
                # Simple nod action in "parallel"
                reachy.goto_target(head=create_head_pose(pitch=20, degrees=True), duration=0.5)
        
        # Continue action while finishing text
        time.sleep(0.3)
        reachy.goto_target(head=create_head_pose(pitch=-10, degrees=True), duration=0.5)
        time.sleep(0.3)
        reachy.goto_target(head=create_head_pose(), duration=0.5)
        
        print("\n   ✅ Parallel execution complete")
        time.sleep(1.0)
    
    print("\n" + "="*60)
    print("Comparison Summary")
    print("="*60)
    print("\nSequential (emo_v2):")
    print("  - Text completes first")
    print("  - Emotion analyzed after text")
    print("  - Action executes after analysis")
    print("  - Total time: Text + Analysis + Action")
    
    print("\nParallel (emo_v3):")
    print("  - Action starts during text streaming")
    print("  - Emotion analyzed from partial text")
    print("  - Action overlaps with text output")
    print("  - Total time: max(Text, Action)")
    
    print("\nKey improvement:")
    print("  - More natural interaction")
    print("  - Robot appears more responsive")
    print("  - Better user experience")


def test_min_chars_threshold():
    """Test minimum characters threshold for early emotion analysis"""
    
    print("\n" + "="*60)
    print("Testing Minimum Characters Threshold")
    print("="*60)
    
    test_cases = [
        ("Hi!", 3, "Too short - wait for full response"),
        ("Hello there!", 12, "Enough for early analysis"),
        ("I am very happy!", 16, "Good for early analysis"),
        ("😊", 1, "Emoji only - special handling"),
        ("This is a longer response that should trigger early action.", 55, "Definitely triggers early"),
    ]
    
    for text, length, expected in test_cases:
        print(f"\nText: '{text}'")
        print(f"Length: {length} characters")
        print(f"Expected: {expected}")
        
        # Simulate the logic
        min_chars = 10
        if length >= min_chars:
            print("✅ Would trigger early action")
        else:
            print("⚠️ Would wait for complete response")


def demo_emo_v3_flow():
    """Demonstrate the emo_v3 parallel flow"""
    
    print("\n" + "="*60)
    print("emo_v3 Parallel Flow Demonstration")
    print("="*60)
    
    print("\nUser: 'Tell me a happy story!'")
    print("\nReachy Mini response flow:")
    
    # Simulate the parallel flow
    steps = [
        ("Streaming text", "Hello! Let me tell you..."),
        ("10+ chars reached", "Analyzing emotion from buffer"),
        ("Emotion: positive", "Starting action in background thread"),
        ("Continue streaming", "a story about a little robot..."),
        ("Action executing", "Robot nodding happily"),
        ("Text complete", "that learned to dance! 😄"),
        ("Action complete", "Returning to neutral"),
    ]
    
    for step, description in steps:
        print(f"\n  [{step}]")
        print(f"    {description}")
        time.sleep(0.3)
    
    print("\n✅ Parallel execution complete!")
    print("\nUser experiences:")
    print("  - Robot starts moving while still talking")
    print("  - More natural, human-like interaction")
    print("  - No awkward pause after speech")


if __name__ == "__main__":
    print("Parallel Actions Test Script")
    print("="*60)
    
    test_sequential_vs_parallel()
    time.sleep(1)
    
    test_min_chars_threshold()
    time.sleep(1)
    
    demo_emo_v3_flow()
    
    print("\n" + "="*60)
    print("To test actual implementation:")
    print("="*60)
    print("\nSequential version (emo_v2):")
    print("  python emo_v2.py --chat")
    
    print("\nParallel version (emo_v3):")
    print("  python emo_v3.py --chat")
    
    print("\nCompare by timing the response actions!")