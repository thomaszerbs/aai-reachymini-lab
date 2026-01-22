# Reachy Mini — Ollama Chat + Emotion/Dance Demo

Short summary
- This repository contains demo apps and controllers for the Reachy Mini simulator and small robot, focused on emotion-driven and dance actions triggered from language model outputs (Ollama). It includes several experimental versions (`emo_v1` → `emo_v5`) that explore recorded-move playback, streaming-triggered motions, and TTS integration.

What you'll find
- `emo_v1.py` — baseline high-intensity emotion controller and examples.
- `emo_v2.py` — RecordedMoves categorization and selection.
- `emo_v3.py` — streaming LM responses triggering actions early.
- `emo_v4.py` — offline- focused TTS (espeak) with lip-sync hooks.
- `emo_v5.py` — Edge-TTS integration with WAV save/read/play flow (multilanguage support).
- `test_actions.py` — utility script to play recorded move libraries and smoke-test behaviors.
- `simple_interact.py` — small interactive entrypoint for manual testing.

Installation prerequisites (Linux / Debian-family)
1. System packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip espeak ffmpeg libsndfile1 portaudio19-dev
```

Notes:
- `espeak` is required for the offline TTS flow used by `emo_v4.py`.
- `libsndfile1` and `portaudio` are required for `soundfile` and `sounddevice` (used when playing WAVs).
- `ffmpeg` is optional but useful if you need to convert audio formats or debug audio files.

2. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Optional: Ollama / Reachy simulator
- If you use Ollama or a local Reachy simulator, follow those tools' own install instructions. This repo integrates with Ollama for LM responses in some demos; the code is written to gracefully fall back when Ollama or the robot SDK is absent.

Quick test commands

```bash
# Run the action tests (plays recorded moves + emotions)
python test_actions.py

# Test TTS in emo_v5 (Edge-TTS path) — the script includes a --test-tts flag in emo_v5
python emo_v5.py --test-tts

# Test espeak offline TTS in emo_v4
python emo_v4.py --test-tts
```

Project notes and troubleshooting
- If you hear noisy or distorted audio, ensure `soundfile` and `sounddevice` are installed in the active venv, and the system `libsndfile` and PortAudio development packages are present.
- `emo_v5.py` writes Edge-TTS output to WAV and plays it back using the file's sample rate to avoid playback artifacts.
- `emo_v4.py` uses `espeak --stdout` as the primary offline TTS backend; ensure `espeak` is installed.