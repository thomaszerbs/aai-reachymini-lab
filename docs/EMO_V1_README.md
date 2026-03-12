# emo_v1.py — Baseline Emotion Controller

Short summary
- `emo_v1.py` is the project's baseline emotion controller and demo harness for Reachy Mini. It implements a simple, high-intensity emotion behavior set and example usage for quickly testing motion and TTS integrations.

What you'll find
- Basic head/antenna movements mapped to a small set of emotion labels.
- Simple offline TTS hooks (espeak in older flows) and placeholders for playback.
- Example CLI usage to run quick motion/TTS tests.

Notes
- Useful as a starting point if you want the simplest, lowest-dependency demo.
- For higher-quality TTS or recorded-move playback look at later versions (emo_v4/emo_v5/emo_v6).

Quick test
```bash
python emo_v1.py --test-tts
```

