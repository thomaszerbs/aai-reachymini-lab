# emo_v7.py — ASR → LLM → TTS Pipeline (faster-whisper)

Short summary
- `emo_v7.py` extends the Emo controller family with an ASR input mode using `faster-whisper` (CPU). It implements a simple push-to-talk flow: record from microphone → transcribe → send to Ollama → synthesize and animate via Edge-TTS and the emotion controller.

What you'll find
- `--asr` flag to run push-to-talk ASR mode (4s recordings by default).
- Integration with `EmotionControllerV6` for emotion analysis, recorded-move selection, and lip-sync during TTS.
- Example usage and quick startup instructions.

Requirements
- Install dependencies into your virtualenv:
```bash
pip install faster-whisper sounddevice soundfile requests
```
- `faster-whisper` runs on CPU with `device='cpu'`. Use `model_name='small'` or smaller for reasonable latency.

Quick test
```bash
# ASR push-to-talk mode (records 4s per utterance)
python emo_v7.py --asr

# ASR with gentler motions
python emo_v7.py --asr --gentle

# Text chat mode (fallback to typing)
python emo_v7.py
```

Notes and next steps
- New CLI flag `--gentle` was added to restrict selected recorded moves to a curated "gentle" set and to prefer slower, subtler durations. Use this when testing with a human nearby or on a fragile setup.
- If you see repeated "Audio system is not initialized." messages but still hear sound, this is often a transient PortAudio/sounddevice initialization warning — the system may still play audio on retry. Installing `sounddevice` in your venv and ensuring PulseAudio/PipeWire is running usually resolves it. You can also force a specific output device by setting `sd.default.device` in the code (see emo_v6.EdgeTTSEngine for possible adjustments).
- Consider replacing fixed-length recording with VAD (`webrtcvad`) to automatically detect end-of-speech for better UX.
- For lower-latency ASR, consider `whisper.cpp` (ggml) or VOSK streaming as future options.

