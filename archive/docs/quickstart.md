# Reachy Mini — Ollama Chat + Emotion/Dance Demo

## Short summary
- This repository contains demo apps and controllers for the Reachy Mini simulator and small robot, focused on emotion-driven and dance actions triggered from language model outputs (Ollama). It includes several experimental versions (`emo_v1` → `emo_v8`) that explore recorded-move playback, streaming-triggered motions, and TTS integration.

What you'll find
- `emo_v1.py` — Baseline high-intensity emotion controller and examples.
- `emo_v2.py` — RecordedMoves categorization and selection.
- `emo_v3.py` — Streaming LM responses triggering actions early.
- `emo_v4.py` — Offline-focused TTS (eSpeak) with lip-sync hooks.
- `emo_v5.py` — Edge-TTS integration with WAV save/read/play flow (multi-language support).
- `emo_v6.py` — Continuous synchronized actions with cartoon voices and multi-modal expressions.
- `emo_v7.py` — ASR → LLM → TTS demo (see `docs/EMO_V7_README.md`)
- `emo_v8.py` — Offline Piper-TTS version (ASR/text chat + Ollama + Piper)


## Run it

Suppose the repo cloned to ~/ReachyMiniChat and vene has been setup by refer to the ../README.md. You should make sure you run the commands after activate the venv.

```
cd ~/ReachyMiniChat
source venv/bin/activate
```

1. Start the Reachy Mini Deamon in terminal 1:

Use `export PYGLFW_LIBRARY_VARIANT=x11` if the GUI launch fails on Wayland, which is the default backend of Ubuntu 24.04+.

```bash
cd ~/ReachyMiniChat
source venv/bin/activate
export PYGLFW_LIBRARY_VARIANT=x11
reachy-mini-daemon --sim
```

If you have the real Reachy Mini Robot connected, you could play with it by 


```bash
cd ~/ReachyMiniChat
source venv/bin/activate
sudo chmod 666 /dev/ttyACM0 # set the permission, you may change ttyACM* according the real port in your environment
reachy-mini-daemon
```

2. Quick test commands (terminal 2)

```bash
cd ~/ReachyMiniChat
source venv/bin/activate
```

```bash
# Run v1, exit by Ctrl+C
python emo_v1.py --chat
```

```bash
# Test the actions, exit by Ctrl+C
python utils/test_actions
```

```bash
# Run v1, exit by Ctrl+C
python emo_v2.py --test-moves
```
It will download the pollen-robotics/reachy-mini-dances-library at the first time run it. And the play the 19 recorded moves one by one from Mujoco sim GUI or realy Reachy Mini Robot.


## emo_v4 (Offline eSpeak-TTS)

You may need to set the audio device to ReachyMini throuhg the Sound settings of Ubuntu. 

```bash
# Run v4 which use eSpeak TTS, exit by Ctrl+C
python emo_v4.py --test-tts
python emo_v4.py --chat
```

## emo_v7 (ASR → LLM → TTS)

The emo_v7 use edgeTTS which need internet access.

- `emo_v7.py` adds a microphone-first pipeline using `faster-whisper` (CPU) for ASR, then forwards the transcription to Ollama and uses the existing emotion controller + Edge-TTS for speech and actions.
- See [EMO_V7_README.md](docs/EMO_V7_README.md) for usage, requirements, and notes about model choices and VAD improvements.
- New CLI flag: `--gentle` — enables gentle_mode which restricts selected recorded moves to a curated gentle set and adjusts motion durations for subtler actions. Example:

```bash
python emo_v7.py --asr --gentle
```

```bash
# VAD ASR mode (auto-stop on silence)
python emo_v7_vad.py --asr

# Text chat mode
python emo_v7_vad.py --chat
```

## emo_v8 (Offline Piper-TTS)
- `emo_v8.py` replaces Edge-TTS with Piper-TTS for fully offline speech synthesis, while keeping Ollama chat and emotion/action flow.
- New dependency is already included in `requirements.txt`:
  - `piper-tts>=1.4.0`
- `emo_v8.py` also supports `--gentle` (same behavior as emo_v7/emo_v6) and accepts `--piper-model` and `--piper-config` to point to local voice models. Example:

```bash
python emo_v8.py --piper-model models/zh_CN-huayan-medium.onnx --gentle
```

Piper voice model download
- Download `.onnx` and matching `.onnx.json` voice files from:
- Piper release page: `https://github.com/rhasspy/piper/releases/tag/v0.0.2`
- Place files under `models/` (or any path you pass to `--piper-model`).

Usage examples(default ollama model is qwen3:0.6b)

```bash
# Text chat mode + english (default)
python emo_v8.py --chat --piper-model models/en-us-blizzard_lessac-medium.onnx
python emo_v8.py --chat --piper-model models/en-us-blizzard_lessac-medium.onnx --model qwen3.5:0.8b

# ASR mode + Chinese
python emo_v8.py --asr --piper-model models/zh_CN-huayan-medium.onnx --gentle
python emo_v8.py --asr --piper-model models/zh_CN-huayan-medium.onnx --gentle --model qwen3.5:0.8b

# ASR + gentle action + Chinese
python emo_v8.py --asr --piper-model ./models/zh_CN-huayan-medium.onnx --gentle
python emo_v8.py --asr --piper-model ./models/zh_CN-huayan-medium.onnx --gentle --model qwen3.5:0.8b
```

