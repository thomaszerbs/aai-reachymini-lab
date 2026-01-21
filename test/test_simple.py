#!/usr/bin/env python3
"""
Simple test script for Reachy Mini Ollama app.
This tests the basic functionality without requiring Ollama or Reachy Mini to be running.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock imports for testing
class MockReachyMini:
    def __init__(self, *args, **kwargs):
        print("MockReachyMini: Initialized")
        
    def goto_target(self, head=None, duration=1.0, antennas=None):
        print(f"MockReachyMini: goto_target(head={head is not None}, duration={duration}, antennas={antennas})")
        
    def set_target(self, head=None, antennas=None):
        print(f"MockReachyMini: set_target(head={head is not None}, antennas={antennas})")
        
    def close(self):
        print("MockReachyMini: close()")
        
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        self.close()

# Mock the reachy_mini import
import unittest.mock as mock

# Test the controller logic
def test_controller_logic():
    """Test the controller's internal logic."""
    print("Testing controller logic...")
    
    # Mock the imports
    with mock.patch.dict('sys.modules', {
        'reachy_mini': mock.MagicMock(ReachyMini=MockReachyMini),
        'reachy_mini.utils': mock.MagicMock(create_head_pose=lambda **kwargs: f"head_pose({kwargs})")
    }):
        try:
            # Now import and test
            from app import ReachyOllamaController
            
            # Create controller
            controller = ReachyOllamaController(model="test-model")
            
            # Test action registration
            print(f"\nRegistered actions: {list(controller.actions.keys())}")
            assert len(controller.actions) == 10, f"Expected 10 actions, got {len(controller.actions)}"
            
            # Test that all action methods exist
            for action_name in controller.actions:
                assert callable(controller.actions[action_name]), f"Action {action_name} is not callable"
                
            print("✅ All action methods are callable")
            
            # Test action names
            expected_actions = {'nod', 'shake', 'look_left', 'look_right', 'look_up', 
                               'look_down', 'antennas_wiggle', 'circle_head', 
                               'excited', 'thoughtful'}
            actual_actions = set(controller.actions.keys())
            assert expected_actions == actual_actions, f"Actions mismatch"
            
            print("✅ All expected actions are present")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in controller logic: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_imports():
    """Test that all required imports are available."""
    print("\nTesting imports...")
    
    required_modules = [
        ('json', 'json'),
        ('random', 'random'),
        ('threading', 'threading'),
        ('time', 'time'),
        ('requests', 'requests'),
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
    ]
    
    for module_name, import_name in required_modules:
        try:
            __import__(import_name)
            print(f"✅ {module_name}")
        except ImportError:
            print(f"❌ {module_name} - Not found")
            return False
    
    # Also check for scipy.spatial.transform
    try:
        from scipy.spatial.transform import Rotation
        print("✅ scipy.spatial.transform")
        return True
    except ImportError:
        print("❌ scipy.spatial.transform - Not found")
        return False

def main():
    print("=" * 60)
    print("Reachy Mini Ollama App - Basic Tests")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        
    # Test controller logic
    if not test_controller_logic():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All basic tests passed!")
        print("\nNote: This only tests the Python code logic.")
        print("To fully test the app, you need:")
        print("1. Ollama running with a model (e.g., qwen3:0.6b)")
        print("2. Reachy Mini simulation running")
        print("\nRun: python app.py --test (to test robot actions)")
        print("Run: python app.py (for interactive chat)")
    else:
        print("❌ Some tests failed")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())