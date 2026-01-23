# emo_v3.py — Streaming-triggered Emotion Controller

Short summary
- `emo_v3.py` explores streaming LM responses triggering actions early. It demonstrates reacting to partial LM output (streaming) and beginning robot motions before full responses finish.

What you'll find
- Integration patterns for streaming text responses to drive early motion cues.
- Example flows showing how to interleave movement with incremental text output.

Notes
- This version is useful when you want lower-latency, more reactive behavior (robot starts moving as the model speaks).
- Combine with ASR/streaming ASR later for fully real-time conversational loops.

Quick test
```bash
python emo_v3.py
```

