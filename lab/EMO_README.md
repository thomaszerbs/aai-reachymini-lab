# EMO README — Reachy Mini Mini-Lab Versions

This document summarizes the **four emotion/chat versions used in the mini-lab**
(`emo_v1.py` → `emo_v4.py`). Each version is one station in the
[`LAB.md`](LAB.md) flow, building up to a robot that sees,
thinks, and speaks entirely on local AMD hardware.

> Older experimental versions from the upstream
> [ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat) project
> (`emo_v5`, `emo_v7`, the espeak/Edge-TTS prototypes, etc.) live in
> [`archive/`](../archive/) and are **not** part of the lab.

---

## Version Comparison Table

| Feature | emo_v1 | emo_v2 | emo_v3 | emo_v4 |
|---|---|---|---|---|
| Station | 1 — intro | 2 — expressive | 3 — offline | 4 — vision |
| Purpose | Hand-coded emotion engine | Continuous synchronized actions + voice | Same robot, fully offline | Reachy "sees" and reacts |
| Input | Text chat | Text chat | Text **or** mic (`--asr`) | Camera frame (press Enter) |
| LLM | Ollama (local) | Ollama (local) | Ollama (local) | Ollama vision model (local) |
| TTS Engine | none / minimal | Edge-TTS (**cloud**) | Piper-TTS (**offline**) | Piper-TTS (**offline**) |
| Lip-sync | no | multi-modal synchronized | multi-modal synchronized | multi-modal synchronized |
| Eye blink + body yaw + antennas | no | synchronized | synchronized | synchronized |
| Runs fully offline | LLM only | no (cloud voice) | **yes** | **yes** |
| Camera / vision | no | no | no | **yes** (local VLM) |

---

## emo_v1 — Hand-Coded Emotion Engine (Station 1, intro)

- **Purpose:** Baseline, easy-to-read emotion controller. Keyword-based emotion
  classification maps text to large-amplitude robot motions — a clear intro to
  how language drives movement.
- **Run it:**

```bash
python lab/emo_v1.py --chat
```

---

## emo_v2 — Expressive Robot + Cloud Voice (Station 2)

- **Purpose:** Continuous, synchronized emotional actions throughout speech
  (eye blinking + body yaw + head poses + antennas), with a cute cartoon voice
  via Microsoft **Edge-TTS** (a cloud service). Uses the Hugging Face
  dances/emotions recorded-move library (downloaded on first run).
- **Note:** Edge-TTS requires internet — this is the only lab station that does.
- **Run it:**

```bash
python lab/emo_v2.py --chat
python lab/emo_v2.py --chat --model qwen3.5:0.8b

# Component tests
python lab/emo_v2.py --test-actions   # synchronized motion test
python lab/emo_v2.py --test-tts       # Edge-TTS + emotion analysis
```

---

## emo_v3 — Fully Offline (Station 3)

- **Purpose:** The same expressive robot as Station 2, but **100% offline**.
  Replaces Edge-TTS with **Piper-TTS** while keeping Ollama chat and the
  emotion/action flow. Adds optional microphone input via `faster-whisper` ASR.
  Reuses the emotion engine from `emo_v2` (`from emo_v2 import EmotionControllerV6`).
- **Prove it's offline:** unplug the network and run again — Reachy keeps talking.
- **Run it:**

```bash
# Text chat (English voice is bundled in models/)
python lab/emo_v3.py --chat --piper-model models/en-us-blizzard_lessac-medium.onnx

# Microphone ASR mode (Chinese voice + gentle motions)
python lab/emo_v3.py --asr --piper-model models/zh_CN-huayan-medium.onnx --gentle
```

Piper voice models: download `.onnx` + matching `.onnx.json` from
[Piper Voices](https://huggingface.co/rhasspy/piper-voices) into `models/`,
or pass a full path via `--piper-model`.

---

## emo_v4 — Reachy Sees (Station 4)

- **Purpose:** Reachy looks through its own camera, sends the frame to a **local
  vision model** (Ollama VLM), describes what it sees, and reacts with the same
  offline Piper-TTS voice + emotion motions as Station 3
  (`from emo_v3 import EmotionControllerV71`).
- **Camera note:** frames are read directly from the V4L2 device via `ffmpeg`
  (more reliable than the SDK media server on the booth machines). Motion still
  goes through the daemon.
- **Run it:**

```bash
python lab/emo_v4.py                          # press Enter and Reachy describes the scene
python lab/emo_v4.py --gentle                 # subtler motions for nearby humans
python lab/emo_v4.py --camera-device /dev/video2
python lab/emo_v4.py --save-frame look.jpg    # save what the camera saw (debugging)
```

Requires the vision model: `ollama pull qwen2.5vl:3b`.

---

## Dependency Chain

`emo_v4.py` → imports `EmotionControllerV71` from `emo_v3.py` → imports
`EmotionControllerV6` from `emo_v2.py`. So when editing the emotion engine,
  changes in `lab/emo_v2.py` propagate up to Stations 3 and 4.

---

## Tests & Utilities

- All `emo_v*.py` scripts support `--help` and use lazy imports, so help prints
  even when optional dependencies are missing.
- `python lab/emo_v2.py --test-actions` — synchronized eye blink + body yaw + head + antennas.
- `python lab/emo_v2.py --test-tts` — Edge-TTS with emotion analysis and cartoon voices.
- `python utils/test_actions.py` — validates the recorded-move libraries.
- `python utils/test_ollama_connection.py --url <url>` — tests Ollama connectivity.
- `python utils/test_emotion_analysis.py` — emotion analysis demo (`--interactive` for manual).
- `python utils/latency_harness.py` — measures fixed vs VAD recording + ASR timings.
