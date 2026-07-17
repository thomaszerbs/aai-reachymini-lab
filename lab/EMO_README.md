# EMO README — Reachy Mini Mini-Lab Versions

This document summarizes the **emotion/chat versions used in the mini-lab**
(`emo_v1.py` → `emo_v3.py`), building up to a robot that sees, thinks, and speaks
entirely on local AMD hardware. The timed main flow is **three tasks** — `emo_v1`
(Task 1), `emo_v2` (Task 2), `emo_v3` (Task 3).

> **Notebook is primary.** The attendee experience is now the
> [`lab/lab.ipynb`](lab.ipynb) notebook (all three tasks in one place, powered by
> [`_labkit.py`](_labkit.py)); these `emo_v*.py` scripts are the **fallback** if
> Jupyter has trouble. Same tasks, same `# >>> TRY ME <<<` knobs. (One
> difference: the notebook's Task 3 uses a **question bar** — you type what you
> want to know and Reachy answers about the live view — while the `emo_v3.py`
> script below uses Enter / "Look & Describe" with a `VISION_PROMPT`.)

> Older experimental versions from the upstream
> [ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat) project
> (`emo_v5`, `emo_v7`, the espeak/Edge-TTS prototypes, etc.) live in
> [`archive/`](../archive/) and are **not** part of the lab.

> **Edit the `# >>> TRY ME <<<` block, then re-run:** attendees edit the TRY ME
> constants at the top of each script, save, and re-run the command to see the
> change. Each knob also has an override CLI flag for coders who'd rather pass an
> arg: `--persona` + `--voice` (v1), `--persona` (v2), `--prompt` (v3).

---

## Version Comparison Table

| Feature | emo_v1 | emo_v2 | emo_v3 |
|---|---|---|---|
| Task | 1 — expressive | 2 — offline | 3 — vision |
| Purpose | Continuous synchronized actions + voice | Same robot, fully offline | Reachy "sees" and reacts |
| Input | Text chat | Text **or** mic (`--asr`) | Camera frame (press Enter) |
| LLM | Ollama (local) | Ollama (local) | Ollama vision model (local) |
| TTS Engine | Edge-TTS (**cloud**) | Piper-TTS (**offline**) | Piper-TTS (**offline**) |
| Lip-sync | multi-modal synchronized | multi-modal synchronized | multi-modal synchronized |
| Eye blink + body yaw + antennas | synchronized | synchronized | synchronized |
| Runs fully offline | no (cloud voice) | **yes** | **yes** |
| Camera / vision | no | no | **yes** (local VLM) |

---

## emo_v1 — Expressive Robot + Cloud Voice (Task 1)

- **Purpose:** Continuous, synchronized emotional actions throughout speech
  (eye blinking + body yaw + head poses + antennas), with a cute cartoon voice
  via Microsoft **Edge-TTS** (a cloud service). Uses the Hugging Face
  dances/emotions recorded-move library (downloaded on first run).
- **Note:** Edge-TTS requires internet — this is the only lab task that does.
- **Run it:**

```bash
python lab/emo_v1.py --chat          # uses the default chat model (qwen3.5:0.8b)

# Component tests
python lab/emo_v1.py --test-actions   # synchronized motion test
python lab/emo_v1.py --test-tts       # Edge-TTS + emotion analysis
```

---

## emo_v2 — Fully Offline (Task 2)

- **Purpose:** The same expressive robot as Task 1, but **100% offline** (and,
  with local Piper-TTS, often snappier than the cloud voice — no network round-trip).
  Replaces Edge-TTS with **Piper-TTS** while keeping Ollama chat and the
  emotion/action flow. Adds optional microphone input via `faster-whisper` ASR.
  Reuses the emotion engine from `emo_v1` (`from emo_v1 import EmotionControllerV6`).
- **Prove it's offline:** unplug the network and run again — Reachy keeps talking.
- **Run it:**

```bash
# Text chat (English voice is bundled in models/)
python lab/emo_v2.py --chat --piper-model models/en-us-blizzard_lessac-medium.onnx

# Microphone ASR mode (Chinese voice + gentle motions)
python lab/emo_v2.py --asr --piper-model models/zh_CN-huayan-medium.onnx --gentle
```

- **Voice-chat toggle:** besides the `--asr` flag, the `# >>> TRY ME <<<` block
  has a `USE_VOICE_CHAT = True` switch (with `VOICE_CHAT_LANG`) that turns on the
  same offline mic ASR — attendees just flip it and run `python lab/emo_v2.py`.

Piper voice models: download `.onnx` + matching `.onnx.json` from
[Piper Voices](https://huggingface.co/rhasspy/piper-voices) into `models/`,
or pass a full path via `--piper-model`.

---

## emo_v3 — Reachy Sees (Task 3)

- **Purpose:** Reachy looks through its own camera, sends the frame to a **local
  vision model** (Ollama VLM), describes what it sees, and reacts with the same
  offline Piper-TTS voice + emotion motions as Task 2
  (`from emo_v2 import EmotionControllerV71`).
- **Camera note:** frames are read directly from the V4L2 device via `ffmpeg`
  (more reliable than the SDK media server on the booth machines). Motion still
  goes through the daemon.
- **Run it:**

```bash
python lab/emo_v3.py                          # press Enter and Reachy describes the scene
python lab/emo_v3.py --preview                # live camera window of what Reachy sees
python lab/emo_v3.py --gentle                 # subtler motions for nearby humans
python lab/emo_v3.py --camera-device /dev/video2
python lab/emo_v3.py --save-frame look.jpg    # save what the camera saw (debugging)
```

`--preview` is optional (needs `opencv-python` — already in `requirements.txt` —
and a display); it falls back to the default one-shot grab if unavailable.

Requires the vision model: `ollama pull qwen2.5vl:3b`.

---

## Dependency Chain

`emo_v3.py` → imports `EmotionControllerV71` from `emo_v2.py` → imports
`EmotionControllerV6` from `emo_v1.py`. So when editing the emotion engine,
changes in `lab/emo_v1.py` propagate up to Tasks 2 and 3 (`emo_v2`, `emo_v3`).

---

## Tests & Utilities

- All `emo_v*.py` scripts support `--help` and use lazy imports, so help prints
  even when optional dependencies are missing.
- `python lab/emo_v1.py --test-actions` — synchronized eye blink + body yaw + head + antennas.
- `python lab/emo_v1.py --test-tts` — Edge-TTS with emotion analysis and cartoon voices.
- `python utils/test_actions.py` — validates the recorded-move libraries.
- `python utils/test_ollama_connection.py --url <url>` — tests Ollama connectivity.
- `python utils/test_emotion_analysis.py` — emotion analysis demo (`--interactive` for manual).
- `python utils/latency_harness.py` — measures fixed vs VAD recording + ASR timings.
