#!/usr/bin/env python3
"""
test_all_versions.py - Test and demonstrate all emotion controller versions

Tests:
1. emo_v1.py - Basic emotion controller
2. emo_v2.py - Enhanced with recorded moves
3. emo_v3.py - Parallel actions
4. emo_v4.py - TTS integration
"""

import time
import subprocess
import sys


def test_version(version: str, test_type: str = "basic"):
    """Test a specific version of the emotion controller"""
    
    print(f"\n{'='*60}")
    print(f"Testing emo_v{version}.py - {test_type}")
    print(f"{'='*60}")
    
    # Use the virtual environment Python directly
    cmd = f"/Users/hcf/ReachyMini-sim/reachy_mini_env/bin/python emo_v{version}.py"
    
    if test_type == "basic":
        # Just show help to verify it works
        cmd += " --help"
    elif test_type == "test-moves":
        cmd += " --test-moves"
    elif test_type == "test-tts" and version == "4":
        cmd += " --test-tts --no-tts"  # Test without actual audio
    elif test_type == "test-emotions" and version in ["2", "3", "4"]:
        cmd += " --test-emotions"
    
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ emo_v{version}.py works correctly")
            
            # Show first few lines of output
            lines = result.stdout.strip().split('\n')
            for line in lines[:10]:
                if line.strip():
                    print(f"  {line}")
            
            if len(lines) > 10:
                print(f"  ... ({len(lines)-10} more lines)")
        else:
            print(f"❌ emo_v{version}.py failed")
            print(f"Error: {result.stderr[:200]}")
            
    except subprocess.TimeoutExpired:
        print(f"⚠️ emo_v{version}.py timed out (may be running robot)")
    except Exception as e:
        print(f"❌ Error testing emo_v{version}.py: {e}")


def compare_features():
    """Compare features of all versions"""
    
    print("\n" + "="*60)
    print("Feature Comparison")
    print("="*60)
    
    features = {
        'emo_v1.py': [
            "Basic emotion controller",
            "4 custom actions",
            "No recorded moves",
            "Sequential execution",
            "No TTS",
        ],
        'emo_v2.py': [
            "Recorded moves library (19 moves)",
            "Enhanced emotion detection",
            "Emoji support",
            "Intensity detection",
            "Debug mode",
            "Sequential execution",
            "No TTS",
        ],
        'emo_v3.py': [
            "All v2 features",
            "Parallel actions",
            "Early emotion analysis",
            "Non-blocking execution",
            "Better responsiveness",
            "No TTS",
        ],
        'emo_v4.py': [
            "All v3 features",
            "Multi-backend TTS",
            "Emotional voice modulation",
            "Lip-sync simulation",
            "Parallel speech + actions",
            "Voice-enabled interaction",
        ],
    }
    
    for version, version_features in features.items():
        print(f"\n{version}:")
        for feature in version_features:
            print(f"  ✓ {feature}")


def show_usage_examples():
    """Show usage examples for each version"""
    
    print("\n" + "="*60)
    print("Usage Examples")
    print("="*60)
    
    examples = {
        'emo_v1.py': "python emo_v1.py",
        'emo_v2.py': """python emo_v2.py --chat
python emo_v2.py --test-moves
python emo_v2.py --chat --debug""",
        'emo_v3.py': """python emo_v3.py --chat
python emo_v3.py --test-moves
python emo_v3.py --chat --debug""",
        'emo_v4.py': """python emo_v4.py --chat
python emo_v4.py --test-tts
python emo_v4.py --test-moves
python emo_v4.py --chat --no-tts
python emo_v4.py --chat --debug""",
    }
    
    for version, example in examples.items():
        print(f"\n{version}:")
        print(f"```bash")
        print(example)
        print(f"```")


def test_quick_demo():
    """Run a quick demo of key features"""
    
    print("\n" + "="*60)
    print("Quick Demo")
    print("="*60)
    
    print("\nTesting core functionality...")
    
    # Check if files exist
    versions_to_test = []
    for v in ["1", "2", "3", "4"]:
        import os
        if os.path.exists(f"emo_v{v}.py"):
            versions_to_test.append(v)
    
    print(f"\nFound versions: {', '.join([f'v{v}' for v in versions_to_test])}")
    
    # Test each version
    for version in versions_to_test:
        test_version(version, "basic")
        time.sleep(0.5)
    
    # Test specific features
    if "2" in versions_to_test or "3" in versions_to_test or "4" in versions_to_test:
        print("\nTesting recorded moves (v2/v3/v4)...")
        test_version("2" if "2" in versions_to_test else "3", "test-moves")
    
    if "4" in versions_to_test:
        print("\nTesting TTS functionality (v4)...")
        test_version("4", "test-tts")


def main():
    """Main function"""
    
    print("Reachy Mini Emotion Controller - All Versions Test")
    print("="*60)
    
    # Check Python version
    print(f"Python version: {sys.version.split()[0]}")
    
    # Run tests
    test_quick_demo()
    
    # Show comparisons
    compare_features()
    
    # Show usage
    show_usage_examples()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("\nVersion Recommendations:")
    print("1. emo_v1.py - Basic, simple, for reference")
    print("2. emo_v2.py - Good for testing, reliable")
    print("3. emo_v3.py - Best for production (no voice)")
    print("4. emo_v4.py - Best for demos (with voice)")
    
    print("\nTo learn more:")
    print("1. Read VERSION_COMPARISON.md")
    print("2. Read individual README files")
    print("3. Run: python emo_v4.py --chat --debug")
    print("4. Run: python test_parallel_actions.py")


if __name__ == "__main__":
    main()