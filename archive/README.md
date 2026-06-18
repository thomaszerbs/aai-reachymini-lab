# Archive

These files are **not part of the mini-lab**. They are kept from the original
[ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat) project for
reference and history.

The mini-lab uses only three top-level scripts plus the vision add-on:

- `emo_v1.py` — Station 1: hand-coded emotion engine
- `emo_v6.py` — Station 2: expressive + cloud voice (Edge-TTS)
- `emo_v8.py` — Station 3: fully offline pipeline (Piper-TTS)
- `emo_v9_vision.py` — Station 4: Reachy "sees" with a local vision model

Everything below was moved out of the way to keep the lab repo focused:

| File | Original purpose |
|------|------------------|
| `emo_v2.py` | Recorded-moves library integration |
| `emo_v3.py` | Streaming-triggered actions |
| `emo_v4.py` | Offline espeak TTS + lip-sync |
| `emo_v5.py` | Edge-TTS integration (superseded by v6) |
| `emo_v7.py` | ASR → LLM → TTS (Edge-TTS) |
| `emo_v1_zh.py` | Chinese variant of v1 |
| `fix_v6.py` | One-off patch script for v6 |
| `demo_zh.sh` | Chinese demo launcher |
| `EMO_V*_README.md` | Per-version docs for the above |
| `WORKSHOP_SH.md` | Shell-script variant of the original workshop |
