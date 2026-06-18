# emo_v2.py - Enhanced Emotion Controller for Reachy Mini

## Overview

`emo_v2.py` is a major enhancement of `emo_v1.py` that incorporates lessons learned from `test_actions.py` to create a richer, more expressive emotional controller for Reachy Mini. The key improvement is the integration of the recorded moves library from "pollen-robotics/reachy-mini-dances-library" to provide pre-recorded, natural movements.

## Key Improvements from emo_v1

### 1. **Recorded Moves Integration** 🎬
   - Uses 19 pre-recorded moves from the dances library
   - Moves are categorized by emotion (positive, negative, question, activity)
   - Provides more natural and varied expressions

### 2. **Easier API** 🛠️
   - Simplified API inspired by `test_actions.py`:
     ```python
     # Like test_actions.py
     controller.execute_recorded_move('simple_nod')
     
     # Enhanced emotion-based API
     controller.execute_emotion_move('positive', 'high')
     ```

### 3. **Enhanced Emotion Detection** 🎭
   - Detects 4 emotion types: positive, negative, question, activity
   - Intensity detection: high/medium/low based on keyword matches
   - Emoji support: 😄😢🤔💃 etc.
   - Better keyword matching with weighted scoring

### 4. **More Actions Available** 🤸
   - 19 recorded moves vs ~4 custom actions in emo_v1
   - Each emotion type has multiple associated moves
   - Intensity-based move selection

### 5. **Fallback System** 🔄
   - Falls back to simple custom actions if no recorded moves available
   - Ensures reliability even if library changes

## Architecture

### EmotionRecordedController Class
```python
# Core methods:
analyze_emotion(text) -> (emotion_type, intensity)
execute_recorded_move(move_name, duration=1.0)
execute_emotion_move(emotion_type, intensity='medium')
```

### Move Categorization
Moves are automatically categorized based on their descriptions:
- **Positive**: `simple_nod`, `yeah_nod` (happy, affirmative movements)
- **Negative**: `stumble_and_recover`, `neck_recoil` (sad, recoiling movements)
- **Question**: `side_glance_flick`, `side_peekaboo` (curious, peeking movements)
- **Activity**: `pendulum_swing`, `groovy_sway_and_roll` (dance-like movements)
- **Neutral**: 9 other moves (default category)

## Usage Examples

### Basic Usage
```python
from reachy_mini import ReachyMini
from emo_v2 import EmotionRecordedController

with ReachyMini() as reachy:
    controller = EmotionRecordedController(reachy)
    
    # Analyze text emotion
    text = "I'm so happy! 😄"
    emotion, intensity = controller.analyze_emotion(text)
    
    # Execute appropriate move
    controller.execute_emotion_move(emotion, intensity)
```

### Like test_actions.py
```python
# Direct move execution (same as test_actions.py)
controller.execute_recorded_move('simple_nod', initial_goto_duration=0.8)
controller.execute_recorded_move('groovy_sway_and_roll')
```

### Command Line Interface
```bash
# Start interactive chat
python emo_v2.py --chat

# Test all moves (like test_actions.py)
python emo_v2.py --test-moves

# Test emotion mapping
python emo_v2.py --test-emotions

# With custom model
python emo_v2.py --chat --model "llama3.2:latest"

# With debug output
python emo_v2.py --chat --debug
python emo_v2.py --test-moves --debug
```

## Comparison with emo_v1

| Feature | emo_v1 | emo_v2 |
|---------|--------|--------|
| Move Source | Custom coded | Recorded moves library (19 moves) |
| Emotion Types | 4 basic | 4 enhanced with intensity |
| Action Variety | Limited | Rich, pre-recorded |
| API Style | `perform_high_amplitude_action()` | `execute_emotion_move()` |
| Emoji Support | No | Yes |
| Fallback System | No | Yes |
| Integration | Standalone | Uses test_actions.py approach |

## Learning from test_actions.py

The key insight from `test_actions.py` was the simplicity of using the recorded moves library:
```python
# test_actions.py approach
recorded_moves = RecordedMoves("pollen-robotics/reachy-mini-dances-library")
mini.play_move(recorded_moves.get(move_name))
```

`emo_v2.py` builds on this by:
1. **Categorizing moves** by emotion
2. **Adding emotion detection** to select appropriate moves
3. **Creating a simpler API** that hides the complexity
4. **Adding fallbacks** for reliability

## Extending the System

### Adding New Emotions
```python
# Extend emotion_keywords in _categorize_recorded_moves()
emotion_keywords = {
    'surprise': ['surprise', 'wow', 'amazing', 'shock'],
    'anger': ['angry', 'mad', 'furious', 'rage'],
}
```

### Adding Custom Moves
```python
# Add to simple_actions dictionary
self.simple_actions['custom_move'] = self._custom_move_action

def _custom_move_action(self, duration: float):
    # Your custom movement logic
    pass
```

## Debug Mode

The `--debug` flag enables verbose output for troubleshooting:

```bash
# See categorization details and move selection logic
python emo_v2.py --test-emotions --debug

# See emotion detection details during chat
python emo_v2.py --chat --debug
```

**Debug output includes:**
- Move categorization scores
- Selected moves for each emotion/intensity
- Emotion detection details
- Fallback system notifications
- Execution confirmation messages

## Performance Notes

- **Categorization**: Happens once during initialization
- **Move Selection**: O(1) lookup for emotion-move mapping
- **Fallback**: Simple actions provide consistent performance
- **Memory**: Stores only move names, not full trajectories

## Requirements

Same as original project:
-## Python 3.8+
- Reachy Mini SDK (installed in virtual environment)
- Recorded moves library (automatically downloaded)

## Conclusion

`emo_v2.py` successfully combines the simplicity of `test_actions.py` with the emotional intelligence of `emo_v1.py` to create a more expressive, reliable, and easier-to-use system for emotional robot interactions.