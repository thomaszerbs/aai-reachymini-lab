# emo_v4.py - Reachy Mini with Text-to-Speech Integration

## Overview

`emo_v4.py` adds Text-to-Speech (TTS) capabilities to the emotion controller, creating a fully voice-enabled Reachy Mini robot. It combines all features from `emo_v3.py` with emotional speech synthesis and lip-sync simulation.

## Key Features

### 1. **Multi-Backend TTS Support**
- **Piper TTS** (recommended): Fast, high-quality, runs locally
- **macOS `say` command**: Built-in, reliable fallback
- **eSpeak**: Lightweight alternative
- **Emotional voice modulation**: Pitch, speed, volume adjustments per emotion

### 2. **Lip-Sync Simulation**
- Antenna movements synchronized with speech
- Creates "talking robot" illusion
- Adjustable animation based on speech duration

### 3. **Parallel Execution**
- Speech synthesis happens in background threads
- Actions continue during speech
- Non-blocking user interaction

### 4. **All emo_v3.py Features**
- Recorded moves library (19 moves)
- Enhanced emotion detection
- Intensity-based action selection
- Debug mode support

## Installation & Setup

### TTS Backend Installation

#### Option 1: macOS Built-in (Recommended for testing)
```bash
# macOS has 'say' command built-in
# No installation needed
```

#### Option 2: Piper TTS (Recommended for production)
```bash
# Install Piper
brew install piper-tts

# Download a voice model (English example)
mkdir -p ~/.local/share/piper/models
curl -L -o ~/.local/share/piper/models/en_US-lessac-medium.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
curl -L -o ~/.local/share/piper/models/en_US-lessac-medium.onnx.json \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

#### Option 3: eSpeak
```bash
# Install eSpeak (cross-platform)

# Ubuntu / Debian
sudo apt update
sudo apt install -y espeak libsndfile1

# macOS (Homebrew)
brew install espeak

# Windows (Chocolatey - recommended)
choco install espeak

# Or download eSpeak from the project releases and add the installation folder to your PATH.
```

### Quick tests

Linux / macOS:
```bash
espeak "hello world"
espeak "你好，测试"
```

Windows (PowerShell):
```powershell
espeak "hello world"
```

### Python playback test (if synthesizing to WAV)
```bash
python3 - <<'PY'
import soundfile as sf, sounddevice as sd
data, sr = sf.read('test.wav', dtype='float32')
sd.play(data, sr)
sd.wait()
PY
```

### Notes
- `espeak` is an offline, lightweight TTS engine available on Linux, macOS and Windows. It produces robotic but reliable speech and is suitable as a universal fallback.
- Ensure the `espeak` executable is on your `PATH` before running `emo_v4.py`.
- If `espeak` appears to be installed but `emo_v4.py` still reports it missing, close and re-open your terminal or log out and log back in so PATH changes take effect.

## Usage

### Command Line Interface
```bash
# Start chat with TTS
python emo_v4.py --chat

# Test TTS functionality
python emo_v4.py --test-tts

# Test recorded moves
python emo_v4.py --test-moves

# Disable TTS (use text-only mode)
python emo_v4.py --chat --no-tts

# With debug output
python emo_v4.py --chat --debug
```

### Python API
```python
from reachy_mini import ReachyMini
from emo_v4 import EmotionControllerV4

with ReachyMini() as reachy:
    controller = EmotionControllerV4(reachy, debug=True)
    
    # Speak with emotional expression
    controller.speak_with_expression(
        "Hello! I'm so happy to see you!",
        emotion='positive',
        intensity='high'
    )
    
    # Or just execute moves
    controller.execute_emotion_move('positive', 'high')
```

## Emotional Voice Parameters

Each emotion has different voice characteristics:

| Emotion | Speed | Pitch | Volume | Description |
|---------|-------|-------|--------|-------------|
| Positive | 1.1x | 1.2x | 1.0x | Faster, higher pitch, enthusiastic |
| Negative | 0.9x | 0.9x | 0.8x | Slower, lower pitch, subdued |
| Question | 1.0x | 1.1x | 1.0x | Slightly higher pitch, curious |
| Activity | 1.2x | 1.1x | 1.1x | Fast, energetic, loud |
| Neutral | 1.0x | 1.0x | 1.0x | Default settings |

## Lip-Sync Simulation

The robot simulates "talking" by:
1. Alternating antenna movements during speech
2. Estimating speech duration from word count
3. Starting/stopping animation with TTS
4. Maintaining emotional expressions

## Architecture

### Key Classes

1. **`TTSEngine`**: Handles speech synthesis
   - Multi-backend support (Piper, say, eSpeak)
   - Emotional voice modulation
   - Audio playback

2. **`LipSyncController`**: Simulates talking
   - Antenna animation
   - Speech duration estimation
   - Thread-safe control

3. **`EmotionControllerV4`**: Main controller
   - Integrates TTS with movement
   - Parallel execution
   - Fallback systems

4. **`ChatAppWithTTS`**: Application wrapper
   - CLI interface
   - Ollama integration
   - User interaction

## Comparison with Previous Versions

### vs emo_v3.py
- **Added**: Full TTS support
- **Added**: Lip-sync simulation  
- **Added**: Emotional voice modulation
- **Same**: Recorded moves library
- **Same**: Parallel actions
- **Same**: Emotion detection

### vs emo_v2.py
- **Added**: TTS and lip-sync
- **Improved**: Parallel execution (v3 feature)
- **Same**: Enhanced emotion detection
- **Same**: Recorded moves

## Performance Considerations

### Audio Synthesis
- **Piper**: ~1-2s for short sentences (fastest)
- **macOS say**: ~0.5-1s (built-in, reliable)
- **eSpeak**: ~0.5s (robotic but fast)

### Memory Usage
- Audio files stored temporarily in `/tmp`
- Automatic cleanup after playback
- Minimal memory footprint

### Threading
- TTS synthesis in background thread
- Audio playback non-blocking
- Lip-sync animation separate thread

## Troubleshooting

### Common Issues

1. **No audio output**
   ```bash
   # Test macOS say command
   say "Hello"
   
   # Check audio permissions
   python emo_v4.py --test-tts --debug
   ```

2. **Piper not found**
   ```bash
   # Check installation
   which piper
   
   # Use fallback
   python emo_v4.py --chat --no-tts
   ```

3. **Robot not moving during speech**
   ```bash
   # Enable debug mode
   python emo_v4.py --chat --debug
   
   # Check emotion detection
   python emo_v4.py --test-tts --debug
   ```

### Debug Output
```bash
# See detailed TTS information
python emo_v4.py --test-tts --debug

# Monitor parallel execution
python emo_v4.py --chat --debug
```

## Customization

### Change Voice Model
```python
# In emo_v4.py, modify:
tts_engine = TTSEngine(
    tts_backend="piper",
    voice_model="en_US-lessac-medium"  # Change this
)
```

### Add New Emotions
```python
# Add to voice_params
self.voice_params['surprise'] = {'speed': 1.3, 'pitch': 1.3, 'volume': 1.2}

# Add to emotion detection
if any(word in text_lower for word in ["wow", "amazing", "surprise"]):
    emotion = "surprise"
```

### Adjust Lip-Sync
```python
# Modify LipSyncController.start_lip_sync()
# Change antenna movement values or timing
left_val = 0.5  # Increase for more movement
right_val = -0.5
```

## Examples

### Interactive Demo
```bash
# Full interactive chat
python emo_v4.py --chat

# Watch the robot speak and move
# 1. You type a question
# 2. Robot analyzes emotion
# 3. Robot speaks with emotional voice
# 4. Robot moves appropriately
# 5. Lip-sync antennas animate
```

### TTS Testing
```bash
# Test all TTS backends
python emo_v4.py --test-tts

# Output shows which backend is used
# ✅ Using macOS 'say' command (AIFF)
# ✅ Using Piper TTS
# ✅ Using espeak
```

## Future Enhancements

1. **Speech Recognition**: Add voice input
2. **Better Lip-Sync**: Mouth animation simulation
3. **Multiple Languages**: International voice support
4. **Voice Cloning**: Custom voice training
5. **Emotion from Tone**: Analyze audio emotion

## Conclusion

`emo_v4.py` transforms Reachy Mini from a text-based chatbot to a fully voice-enabled interactive robot. The combination of emotional TTS, lip-sync simulation, and coordinated movements creates an engaging, human-like interaction experience.