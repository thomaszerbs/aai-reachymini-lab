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

# Text chat mode (fallback to typing)
python emo_v7.py
```

Notes and next steps
- Consider replacing fixed-length recording with VAD (`webrtcvad`) to automatically detect end-of-speech.
- For lower-latency ASR, consider `whisper.cpp` (ggml) or VOSK streaming as future options.

