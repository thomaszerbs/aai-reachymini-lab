# Reachy Mini Chat Workshop — From v1 to v8

A hands-on guide covering emotion-driven robotics, TTS integration, and ASR pipelines. Each section is designed for ~5-10 minutes.

---

## Prerequisites (do this once)

```bash
# Terminal 1 — Start the robot simulator
export PYGLFW_LIBRARY_VARIANT=x11
reachy-mini-daemon --sim

# Terminal 2 — Activate environment
cd ReachyMiniChat
source .venv/bin/activate

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

> **Tip:** Every script supports `--help`. Run `python emo_vX.py --help` to see available flags without launching the full pipeline.

---

## v1 — High-Intensity Emotion Engine

**Concept:** Baseline emotion controller with large-amplitude motions triggered by keyword analysis.

```bash
# Quick logic test (no robot required)
python emo_v1.py --test

# Interactive chat (requires daemon + Ollama)
python emo_v1.py --chat
```

**Try:** Type "happy" vs "sad" and observe the motion amplitude.

**Key idea:** Emotions are classified by simple keyword matching; intensity is always "high".

---

## v2 — Recorded Moves Library

**Concept:** Replace custom motions with pre-recorded move libraries from Hugging Face.

```bash
# Play all recorded moves (dances + emotions)
python utils/test_actions.py

# Interactive chat with recorded moves
python emo_v2.py --chat
```

**Try:** Watch the robot perform dances from `pollen-robotics/reachy-mini-dances-library`.

**Key idea:** Moves are categorized by emotion and selected based on LLM output analysis.

---

## v3 — Parallel Actions During Streaming

**Concept:** Trigger actions *while* the LLM is still generating text, not after.

```bash
python emo_v3.py --chat
```

**Try:** Ask a long question. The robot starts moving before the full response is received.

**Key idea:** Actions are triggered on partial response chunks for lower latency.

---

## v4 — Offline TTS (espeak) + Lip-sync

**Concept:** Add deterministic offline speech synthesis using `espeak` with basic lip-sync hooks.

```bash
# Test TTS only
python emo_v4.py --test-tts

# Full chat with speech
python emo_v4.py --chat
```

**Try:** `--no-tts` flag disables speech if you only want motion.

**Key idea:** Audio is generated via `espeak --stdout` and played with `sounddevice`.

---

## v5 — Edge-TTS (Cloud Neural Voices)

**Concept:** Higher-quality multilingual speech via Microsoft Edge-TTS cloud API.

```bash
# Test Edge-TTS voice
python emo_v5.py --test-tts

# Chat with neural voice
python emo_v5.py --chat
```

**Try:** `utils/test_edge_tts_voices.py` discovers cartoon/cute voices across languages.

**Key idea:** WAV is saved at the source sample rate to avoid playback distortion.

---

## v6 — Continuous Synchronized Actions

**Concept:** Actions persist throughout the *entire* speech, with synchronized eye blink + body yaw + head pose + antenna movement.

```bash
# Test synchronized action sequences
python emo_v6.py --test-actions

# Test TTS with cartoon voices
python emo_v6.py --test-tts

# Full experience
python emo_v6.py --chat
```

**Try:** `--gentle` reduces motion amplitude for safe human-robot interaction.

**Key idea:** 4-5 action sequences per emotion; threading coordinates speech and motion.

---

## v7 — ASR → LLM → TTS (Push-to-Talk)

**Concept:** Speak to the robot instead of typing. 4-second fixed recording per utterance.

```bash
# Microphone mode
python emo_v7.py --asr

# Gentler motions for nearby humans
python emo_v7.py --asr --gentle
```

**Try:** Speak clearly; the robot transcribes → queries Ollama → speaks the response.

**Key idea:** `faster-whisper` on CPU transcribes audio; the rest of the pipeline is identical to v6.

---

## v7_vad — VAD-Enhanced ASR (Experimental)

**Concept:** Same as v7, but recording stops automatically when you stop speaking (Voice Activity Detection).

```bash
# Auto-stop recording on silence
python emo_v7_vad.py --asr

# Tune VAD sensitivity
python emo_v7_vad.py --asr --vad-aggressive 2
```

**Try:** Speak a short sentence and pause — recording stops without waiting 4s.

**Key idea:** `webrtcvad` detects silence; falls back to fixed 4s if unavailable.

---

## v8 — Fully Offline Pipeline (Piper-TTS)

**Concept:** Replace Edge-TTS with Piper-TTS so the entire pipeline works without internet.

```bash
# Text chat with offline voice
python emo_v8.py --chat --piper-model models/en-us-blizzard_lessac-medium.onnx

# ASR + offline voice
python emo_v8.py --asr --piper-model models/zh_CN-huayan-medium.onnx --gentle
```

**Try:** Download additional `.onnx` + `.json` voices from [Piper Voices](https://huggingface.co/rhasspy/piper-voices).

**Key idea:** Ollama (local LLM) + Piper-TTS (local TTS) + faster-whisper (local ASR) = fully offline robot.

---

## Quick Command Cheat Sheet

| Goal | Command |
|------|---------|
| Check dependencies | `python emo_v8.py --help` |
| Test robot moves | `python utils/test_actions.py` |
| Test Ollama connection | `python utils/test_ollama_connection.py` |
| Test emotion analysis | `python utils/test_emotion_analysis.py` |
| Measure ASR latency | `python utils/latency_harness.py` |
| Offline chat | `python emo_v8.py --chat --piper-model ...` |
| Voice chat (VAD) | `python emo_v7_vad.py --asr` |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` | `source .venv/bin/activate && pip install -r requirements.txt` |
| `Connection refused` | Ensure `reachy-mini-daemon --sim` is running |
| No audio / distorted | Install `libsndfile1` and `portaudio19-dev`; verify `sounddevice` in venv |
| Ollama timeout | Run `ollama serve` and verify with `curl http://localhost:11434/api/tags` |
| ASR not working | Check microphone permissions; try `python utils/asr.py` standalone |
| `--help` works but chat fails | Run dependency check: script will print missing packages |

---

## Optional Challenges

1. **Sim-to-Real:** Swap `--sim` for real hardware (`reachy-mini-daemon` without `--sim`).
2. **Custom Voice:** Download a new Piper voice and pass it to `emo_v8.py --piper-model`.
3. **Emotion Tuning:** Modify emotion keywords in `utils/test_emotion_analysis.py` and test with `--interactive`.
4. **Pipeline Timing:** Run `utils/latency_harness.py` to compare fixed vs VAD recording latency.

---

*Workshop duration: ~60-90 minutes for v1→v8. Adjust depth per audience.*
