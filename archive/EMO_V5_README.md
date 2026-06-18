# emo_v5.py - Edge-TTS Integration with Reachy Mini

## Overview

`emo_v5.py` combines your `tts.py` approach (Edge-TTS + sounddevice) with the enhanced emotion controller system from previous versions. This creates a **high-quality, cloud-based TTS solution** with emotional intelligence and robot control.

## Key Features

### 1. **Edge-TTS Integration**
- Uses Microsoft Azure neural voices via Edge-TTS
- **High-quality cloud voices** vs local TTS
- **Multiple language support** (English, Chinese, etc.)
- **Emotional voice mapping** (different voices per emotion)

### 2. **Your tts.py Approach**
- **Antenna/eye lip-sync**: Your emotion level calculation
- **Sounddevice playback**: Direct audio output
- **Emotion level**: `min(len(text) / 200, 1.0)` calculation
- **Direct motor control**: `goal_position` for precise control

### 3. **Enhanced Emotion System**
- **Recorded moves library** (19 movements)
- **Emotion categorization** (positive, negative, question, activity)
- **Intensity detection** (high/medium/low)
- **Emoji support** 😊😢🤔💃

### 4. **Cross-Version Compatibility**
- **Backward compatible** with emo_v2/v3/v4 APIs
- **Forward compatible** with your tts.py approach
- **Modular design** for easy swapping

## Architecture

### EdgeTTSEngine Class
```python
# Your approach + enhanced
class EdgeTTSEngine:
    # Emotional voice mapping
    emotion_voices = {
        'positive': "en-US-JennyNeural",
        'negative': "en-US-DavisNeural", 
        'question': "en-US-BrianNeural",
        'activity': "en-US-AriaNeural",
    }
    
    # Your async synthesis approach
    async def _speak_async(self, text: str, voice: str) -> np.ndarray
```

### LipSyncControllerV5 Class  
```python
# Your antenna/eye control approach
class LipSyncControllerV5:
    def start_lip_sync(self, text: str, emotion_level: float = 0.5):
        # Your direct motor control
        self.reachy.head.r_antenna.goal_position = emotion_level * 0.8
        self.reachy.head.l_antenna.goal_position = emotion_level * 0.8
        self.reachy.head.r_eye.goal_position = 1 - (emotion_level * 0.3)
        self.reachy.head.l_eye.goal_position = 1 - (emotion_level * 0.3)
```

### EmotionControllerV5 Class
```python
# Enhanced emotion analysis with your level calculation
class EmotionControllerV5:
    def analyze_emotion(self, text: str) -> Tuple[str, str, float]:
        # Your emotion level calculation
        emotion_level = min(len(text) / 200, 1.0)
        
        # Enhanced emotion detection
        # ... returns (emotion_type, intensity, emotion_level)
```

## Usage

### Command Line
```bash
# Start interactive chat with Edge-TTS
python emo_v5.py --chat

# Test Edge-TTS functionality
python emo_v5.py --test-tts

# Test tts.py compatibility mode
python emo_v5.py --test-compat

# With debug output
python emo_v5.py --chat --debug
```

### Python API
```python
from reachy_mini import ReachyMini
from emo_v5 import EmotionControllerV5

with ReachyMini() as reachy:
    controller = EmotionControllerV5(reachy, debug=True)
    
    # Your tts.py approach
    text = "你好！我是Reachy Mini！"
    emotion_level = min(len(text) / 200, 1.0)
    
    # Apply antenna/eye positions (your approach)
    reachy.head.r_antenna.goal_position = emotion_level * 0.8
    reachy.head.l_antenna.goal_position = emotion_level * 0.8
    reachy.head.r_eye.goal_position = 1 - (emotion_level * 0.3)
    reachy.head.l_eye.goal_position = 1 - (emotion_level * 0.3)
    
    # Speak with Edge-TTS
    controller.tts_engine.speak_with_emotion(text, "neutral")
```

### Compatibility Mode
```bash
# Test exact tts.py workflow
python emo_v5.py --test-compat

# Output:
# 模拟你的 tts.py 流程:
# 用户: 你好，介绍一下你自己
# Reachy: 你好！我是Reachy Mini...
# 情感值: 0.45
# 🗣️ Speaking with Edge-TTS...
```

## Dependencies

### Required Packages
```bash
# Core dependencies
pip install edge-tts
pip install sounddevice
pip install numpy
pip install requests

# Reachy Mini SDK (already in your environment)
```

### Installation
```bash
cd /path/to/reachy_mini_ollama_chat
pip install edge-tts sounddevice numpy
```

## Comparison with tts.py

### What's Same
1. **Edge-TTS backend**: Microsoft Azure voices
2. **Sounddevice playback**: Direct audio output
3. **Antenna/eye control**: Your lip-sync approach
4. **Emotion level calculation**: `len(text) / 200`
5. **Async speech synthesis**: `asyncio` + `edge_tts.Communicate`

### What's Enhanced
1. **Emotion mapping**: Different voices per emotion type
2. **Recorded moves**: 19 pre-recorded movements
3. **Intensity detection**: High/medium/low based on text
4. **Fallback system**: macOS `say`, pyttsx3, etc.
5. **Debug mode**: Detailed logging and control

## Comparison with Previous Versions

### vs emo_v4.py
- **Better TTS**: Edge-TTS vs local TTS
- **Your lip-sync**: Direct antenna/eye control vs generic
- **Cloud voices**: Azure neural voices vs local voices
- **More natural**: Higher quality speech

### vs Your tts.py
- **More emotions**: 4 types vs basic level
- **More actions**: 19 recorded moves vs simple
- **Better detection**: Enhanced emotion analysis
- **Fallback**: Multiple TTS backends

## Emotion Voice Mapping

| Emotion | Edge-TTS Voice | Description |
|---------|----------------|-------------|
| Positive | `en-US-JennyNeural` | Friendly, cheerful |
| Negative | `en-US-DavisNeural` | Softer, compassionate |
| Question | `en-US-BrianNeural` | Curious, thoughtful |
| Activity | `en-US-AriaNeural` | Energetic, lively |
| Neutral | `zh-CN-XiaoxiaoNeural` | Default Chinese voice |

## Performance

### Advantages
1. **High quality**: Neural TTS vs robotic TTS
2. **Fast**: Cloud synthesis is fast
3. **Natural**: Human-like voices
4. **Multilingual**: Supports many languages

### Considerations
1. **Internet required**: Edge-TTS needs internet
2. **Cloud dependency**: Microsoft Azure services
3. **Latency**: Network round-trip time

## Troubleshooting

### Common Issues

1. **No audio output**
   ```bash
   # Test sounddevice
   python -c "import sounddevice as sd; print(sd.query_devices())"
   
   # Test Edge-TTS
   python -c "import edge_tts; print('Edge-TTS available')"
   ```

2. **Network issues**
   ```bash
   # Check internet connectivity
   curl -I https://speech.platform.bing.com
   
   # Use fallback mode
   python emo_v5.py --test-compat --debug
   ```

3. **Robot connection**
   ```bash
   # Test Reachy Mini
   python -c "from reachy_mini import ReachyMini; print('SDK available')"
   
   # Run TTS-only mode
   python emo_v5.py --test-tts
   ```

### Debug Output
```bash
python emo_v5.py --chat --debug

# Shows:
# ✅ Edge-TTS voice selection
# 🎭 Emotion analysis results  
# 🎬 Recorded move selection
# 🗣️ Speech synthesis status
# 👄 Lip-sync animation
```

## Extending the System

### Add New Voices
```python
# In EdgeTTSEngine.__init__
self.emotion_voices['surprise'] = "en-US-ChristopherNeural"
self.emotion_voices['anger'] = "en-US-GuyNeural"
```

### Custom Lip-Sync
```python
# In LipSyncControllerV5.start_lip_sync
# Modify the animation loop
def custom_animation():
    # Your custom animation logic
    pass
```

### New Emotion Types
```python
# In EmotionControllerV5.analyze_emotion
# Add new emotion detection
if any(word in text_lower for word in ["wow", "amazing", "surprise"]):
    emotion_type = "surprise"
```

## Conclusion

`emo_v5.py` provides:

1. **✅ Your tts.py approach**: Edge-TTS + sounddevice + antenna control
2. **✅ Enhanced emotion system**: Recorded moves + intensity detection
3. **✅ High-quality speech**: Microsoft Azure neural voices
4. **✅ Cross-platform**: Works on macOS, Windows, Linux
5. **✅ Easy to use**: Simple API, good defaults

It combines the **best of both worlds**: your high-quality TTS approach with the sophisticated emotion control of the emo_v* series.