#!/usr/bin/env python3
"""
example_emo_v2.py - Example usage of emo_v2.py

Shows how to use the enhanced emotion controller with:
1. Recorded moves integration
2. Simple API for emotion-based actions
3. Multiple ways to control Reachy Mini
"""

from reachy_mini import ReachyMini
from emo_v2 import EmotionRecordedController
import time


def example_1_basic_usage():
    """Example 1: Basic emotion analysis and action"""
    print("\n" + "="*60)
    print("Example 1: Basic Emotion Analysis")
    print("="*60)
    
    with ReachyMini(media_backend='no_media') as reachy:
        controller = EmotionRecordedController(reachy, debug=True)
        
        # Test texts with different emotions
        test_texts = [
            "I'm so happy today! 😄",
            "This makes me sad... 😢",
            "What is this? How does it work? 🤔",
            "Let's dance! 💃",
        ]
        
        for text in test_texts:
            print(f"\nText: {text}")
            emotion, intensity = controller.analyze_emotion(text)
            print(f"  Emotion: {emotion}, Intensity: {intensity}")
            
            # Execute appropriate move
            print(f"  Executing {emotion} move...")
            controller.execute_emotion_move(emotion, intensity)
            time.sleep(1.0)


def example_2_direct_move_execution():
    """Example 2: Direct move execution (like test_actions.py)"""
    print("\n" + "="*60)
    print("Example 2: Direct Move Execution")
    print("="*60)
    
    with ReachyMini(media_backend='no_media') as reachy:
        controller = EmotionRecordedController(reachy, debug=True)
        
        # Get all moves
        all_moves = controller.recorded_moves.list_moves()
        print(f"Total moves available: {len(all_moves)}")
        
        # Play some specific moves
        moves_to_play = ['simple_nod', 'yeah_nod', 'groovy_sway_and_roll', 'side_peekaboo']
        
        for move_name in moves_to_play:
            print(f"\nPlaying: {move_name}")
            controller.execute_recorded_move(move_name, initial_goto_duration=0.8)
            time.sleep(0.5)


def example_3_emotion_mapping_info():
    """Example 3: Show emotion mapping information"""
    print("\n" + "="*60)
    print("Example 3: Emotion-Move Mapping")
    print("="*60)
    
    with ReachyMini(media_backend='no_media') as reachy:
        controller = EmotionRecordedController(reachy, debug=True)
        
        # Show what moves are available for each emotion
        for emotion_type, moves in controller.emotion_to_moves.items():
            print(f"\n{emotion_type.upper()} moves ({len(moves)}):")
            if moves:
                for move_name in moves[:5]:  # Show first 5
                    move = controller.recorded_moves.get(move_name)
                    desc = move.description[:50] + "..." if len(move.description) > 50 else move.description
                    print(f"  - {move_name}: {desc}")


def example_4_custom_simple_actions():
    """Example 4: Using custom simple actions"""
    print("\n" + "="*60)
    print("Example 4: Custom Simple Actions")
    print("="*60)
    
    with ReachyMini(media_backend='no_media') as reachy:
        controller = EmotionRecordedController(reachy, debug=True)
        
        # Test all simple actions
        print("\nTesting simple actions:")
        
        actions = [
            ('nod', 'Nodding head'),
            ('shake', 'Shaking head'),
            ('look_curious', 'Curious look'),
            ('look_sad', 'Sad look'),
            ('excited_wiggle', 'Excited wiggle'),
            ('thoughtful_tilt', 'Thoughtful tilt'),
        ]
        
        for action_name, description in actions:
            print(f"\n{description}...")
            if action_name in controller.simple_actions:
                controller.simple_actions[action_name](duration=1.5)
                time.sleep(0.3)


def example_5_compare_with_emo_v1():
    """Example 5: Compare with emo_v1 approach"""
    print("\n" + "="*60)
    print("Example 5: Comparison with emo_v1")
    print("="*60)
    
    print("\nKey improvements in emo_v2:")
    print("1. Uses recorded moves library - richer, pre-recorded actions")
    print("2. More emotion types detected (positive, negative, question, activity)")
    print("3. Intensity detection (high/medium/low)")
    print("4. Emoji support in emotion analysis")
    print("5. Fallback to simple actions when no recorded moves available")
    print("6. Better API: controller.execute_emotion_move(emotion, intensity)")
    print("7. Direct move execution: controller.execute_recorded_move(name)")
    print("8. Categorization of moves by emotion")
    
    print("\nExample comparison:")
    print("  emo_v1: controller.perform_high_amplitude_action('positive')")
    print("  emo_v2: controller.execute_emotion_move('positive', 'high')")
    print("          (Automatically selects best move from recorded library)")


def main():
    """Run all examples"""
    print("Reachy Mini Enhanced Emotion Controller v2 - Examples")
    print("="*60)
    
    # Run examples
    example_1_basic_usage()
    time.sleep(1)
    
    example_2_direct_move_execution()
    time.sleep(1)
    
    example_3_emotion_mapping_info()
    
    example_4_custom_simple_actions()
    
    example_5_compare_with_emo_v1()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("\nThe enhanced emo_v2.py provides:")
    print("✅ Richer expressions using recorded moves library")
    print("✅ More natural and varied emotional responses")
    print("✅ Easier API similar to test_actions.py")
    print("✅ Better emotion detection with emoji support")
    print("✅ Fallback system for reliability")
    
    print("\nTo start interactive chat:")
    print("  python emo_v2.py --chat")
    
    print("\nTo test all moves:")
    print("  python emo_v2.py --test-moves")
    
    print("\nTo test emotion mapping:")
    print("  python emo_v2.py --test-emotions")


if __name__ == "__main__":
    main()