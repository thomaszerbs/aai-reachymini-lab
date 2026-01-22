#!/usr/bin/env python3
"""
Simple test script for Reachy Mini combined actions
Tests the synchronized eye blinking and body yaw with head/antennas movements
"""

import time
from reachy_mini import ReachyMini
from emo_v6 import EmotionControllerV6

def test_combined_actions():
    """Test various combined action sequences"""
    print("🧪 Testing Reachy Mini Combined Actions")
    print("=" * 50)

    try:
        with ReachyMini(media_backend="no_media") as reachy:
            print("✅ Connected to Reachy Mini")

            # Initialize emotion controller
            controller = EmotionControllerV6(reachy, debug=True)

            # Test each emotion's combined actions
            test_sequences = [
                ("Positive", [
                    controller._combined_nod_blink,
                    controller._combined_shake_blink_yaw,
                    controller._combined_excited_sequence
                ]),
                ("Negative", [
                    controller._combined_sad_blink,
                    controller._combined_slow_sequence
                ]),
                ("Question", [
                    controller._combined_curious_blink,
                    controller._combined_question_sequence
                ]),
                ("Activity", [
                    controller._combined_wiggle_blink,
                    controller._combined_activity_sequence
                ]),
                ("Neutral", [
                    controller._combined_nod_blink,
                    controller._combined_neutral_sequence
                ])
            ]

            for emotion_name, actions in test_sequences:
                print(f"\n🎭 Testing {emotion_name} Actions")
                print("-" * 30)

                for i, action in enumerate(actions, 1):
                    print(f"  {i}. Performing action...")
                    action()
                    time.sleep(2.0)  # Pause between actions

                print(f"✅ {emotion_name} actions completed")
                time.sleep(1.0)

            print("\n🎉 All combined action tests completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: Make sure Reachy Mini is connected and accessible")

def test_individual_actions():
    """Test individual action components"""
    print("\n🔧 Testing Individual Action Components")
    print("=" * 50)

    try:
        with ReachyMini(media_backend="no_media") as reachy:
            controller = EmotionControllerV6(reachy, debug=True)

            print("Testing basic movements:")

            # Test basic components
            print("1. Blink...")
            controller._simple_blink_once()
            time.sleep(1.5)

            print("2. Body yaw...")
            controller.reachy.set_target_body_yaw(0.3)  # 17 degrees
            time.sleep(1.0)
            controller.reachy.set_target_body_yaw(0.0)
            time.sleep(1.0)

            print("3. Antenna wiggle...")
            controller._simple_excited_wiggle_once()
            time.sleep(1.5)

            print("4. Head nod...")
            controller._simple_nod_once()
            time.sleep(1.5)

            print("✅ Individual component tests completed!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Run combined actions test
    test_combined_actions()

    # Optionally run individual component tests
    print("\n" + "="*50)
    response = input("Also test individual components? (y/n): ").lower().strip()
    if response == 'y':
        test_individual_actions()

    print("\n👋 Test completed!")
