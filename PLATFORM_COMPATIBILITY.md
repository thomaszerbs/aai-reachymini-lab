# Platform Compatibility Guide

## Overview

`emo_v4.py` now supports **macOS, Windows, and Linux** with automatic detection and fallback mechanisms for TTS (Text-to-Speech) and audio playback.

## Supported Platforms

### ✅ macOS
- **TTS Options**: 
  - `say` command (built-in, recommended)
  - Piper TTS (installable)
  - eSpeak (installable)
- **Audio Playback**:
  - `afplay` (built-in)
  - `sox` (installable)
- **Installation**:
  ```bash
  # Piper TTS
  brew install piper-tts
  
  # eSpeak
  brew install espeak
  
  # Sox (audio tools)
  brew install sox
  ```

### ✅ Windows
- **TTS Options**:
  - `System.Speech` (built-in, .NET)
  - `pyttsx3` (Python library)
  - Piper TTS (installable)
  - eSpeak (installable)
- **Audio Playback**:
  - `winsound` (built-in for WAV)
  - Windows Media Player (built-in)
- **Installation**:
  ```bash
  # Python packages
  pip install pyttsx3
  pip install gtts
  
  # Piper (download from GitHub releases)
  # https://github.com/rhasspy/piper/releases
  
  # eSpeak (download installer)
  # https://github.com/espeak-ng/espeak-ng/releases
  ```

### ✅ Linux
- **TTS Options**:
  - eSpeak (installable)
  - Piper TTS (installable)
  - gTTS (Python, requires internet)
- **Audio Playback**:
  - `aplay` (ALSA, usually built-in)
  - `paplay` (PulseAudio)
  - `ffplay` (FFmpeg)
  - `sox` (installable)
- **Installation**:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install espeak ffmpeg sox
  
  # Piper TTS
  # Download from GitHub releases or build from source
  
  # Python packages
  pip install pyttsx3 gtts
  ```

## Automatic Detection

The code automatically detects your platform and chooses the best available options:

```python
import platform
system = platform.system()  # Returns: 'Darwin', 'Windows', or 'Linux'
```

### Detection Logic
1. **Check platform** (`platform.system()`)
2. **Try platform-specific TTS** first
3. **Fallback** to cross-platform options
4. **Graceful degradation** if nothing works

## TTS Backend Priority

### macOS Priority
1. `say` command (built-in, highest quality)
2. Piper TTS (installable, very good quality)
3. eSpeak (installable, robotic but reliable)

### Windows Priority
1. `System.Speech` (built-in, .NET)
2. `pyttsx3` (Python, requires install)
3. Piper TTS (installable)
4. eSpeak (installable)

### Linux Priority
1. eSpeak (usually available)
2. Piper TTS (installable)
3. gTTS (requires internet)

## Audio Playback Priority

### macOS
1. `afplay` (built-in)
2. `sox` (installable)

### Windows
1. `winsound` (built-in for WAV)
2. Windows Media Player (built-in)

### Linux
1. `aplay` (ALSA, common)
2. `paplay` (PulseAudio)
3. `ffplay` (FFmpeg)
4. `sox` (installable)

## Installation Requirements

### Core Requirements (All Platforms)
```bash
# Python packages
pip install requests

# Reachy Mini SDK
# Already in your virtual environment
```

### Platform-Specific Setup

#### macOS (Simplest)
```bash
# Nothing to install for basic functionality
# 'say' command works out of the box

# For better quality:
brew install piper-tts
```

#### Windows
```powershell
# Install Python packages
pip install pyttsx3

# OR use built-in .NET TTS
# No installation needed for System.Speech
```

#### Linux
```bash
# Install system packages
sudo apt-get install espeak ffmpeg

# Install Python packages
pip install pyttsx3 gtts
```

## Testing Your Setup

Run the platform test:
```bash
python emo_v4.py --test-tts --debug
```

Expected output (macOS example):
```
✅ Using macOS 'say' command (.aiff)
✅ Audio playback via afplay
```

Expected output (Windows example):
```
✅ Using Windows System.Speech
✅ Audio playback via winsound
```

Expected output (Linux example):
```
✅ Using espeak
✅ Audio playback via aplay
```

## Troubleshooting

### No Audio Output
1. **Check speakers/headphones** are connected
2. **Volume** is not muted
3. **Test system audio** plays other sounds
4. **Run platform test** with debug

### TTS Not Working
```bash
# Test platform detection
python -c "import platform; print(f'Platform: {platform.system()}')"

# Test individual TTS backends
# macOS:
echo "Hello" | say

# Linux:
espeak "Hello"

# Windows (PowerShell):
powershell "Add-Type -AssemblyName System.speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('Hello')"
```

### Installation Issues
- **macOS**: Ensure Homebrew is installed for Piper/eSpeak
- **Windows**: May need to enable .NET Framework 3.5
- **Linux**: Use package manager (apt, yum, pacman)

## Custom Configuration

### Override Auto-Detection
```python
# In emo_v4.py, modify TTSEngine.__init__
self.tts_backend = "piper"  # Force Piper
# OR
self.tts_backend = "system"  # Force system default
```

### Add Custom Backends
```python
# Add to _fallback_tts method
try:
    # Your custom TTS implementation
    pass
except:
    pass
```

## Performance Notes

### Speed
- **Fastest**: System TTS (`say` on macOS, `System.Speech` on Windows)
- **Medium**: Piper TTS (high quality, moderate speed)
- **Slowest**: gTTS (requires internet, variable speed)

### Quality
- **Best**: Piper TTS (neural voices)
- **Good**: System TTS (varies by platform)
- **Basic**: eSpeak (robotic but reliable)

### Reliability
- **Most reliable**: System TTS (always available)
- **Reliable**: eSpeak (works everywhere)
- **Variable**: Piper (requires installation)

## Platform-Specific Features

### macOS Exclusive
- `say` command with multiple voice options
- `afplay` for high-quality audio
- Best out-of-box experience

### Windows Exclusive
- `.NET System.Speech` integration
- `winsound` for simple WAV playback
- Good corporate environment support

### Linux Strengths
- Open source options
- Highly customizable
- Server-friendly (no GUI required)

## Conclusion

`emo_v4.py` provides:
- ✅ **Cross-platform** TTS support
- ✅ **Automatic detection** and fallback
- ✅ **Graceful degradation** when features unavailable
- ✅ **Consistent API** across all platforms

The system will always try to provide the best available experience on your platform, automatically adapting to what's installed.