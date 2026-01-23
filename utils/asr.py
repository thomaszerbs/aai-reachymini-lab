#!/usr/bin/env python3
"""ASR engine using faster-whisper (CPU) with a simple mic recorder.

This module provides `FasterWhisperASREngine` which loads a faster-whisper
`WhisperModel` on CPU and exposes `transcribe_file` and
`transcribe_from_mic` helper methods.

Notes:
- Install dependencies: `pip install faster-whisper sounddevice soundfile`
- Use `model_name='small'` or smaller for reasonable CPU latency.
"""
from __future__ import annotations

import tempfile
import os
from typing import Optional

try:
    from faster_whisper import WhisperModel
except Exception:  # pragma: no cover - runtime optional
    WhisperModel = None


class FasterWhisperASREngine:
    """ASR engine built on faster-whisper (CPU).

    Example:
        engine = FasterWhisperASREngine(model_name='small')
        text = engine.transcribe_from_mic(4.0)
    """

    def __init__(self, model_name: str = "small", device: str = "cpu", beam_size: int = 5):
        if WhisperModel is None:
            raise RuntimeError("faster-whisper not installed. Install with `pip install faster-whisper`")

        self.model_name = model_name
        self.device = device
        self.beam_size = beam_size

        # Load model once and reuse
        self.model = WhisperModel(self.model_name, device=self.device)

    def transcribe_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        segments, info = self.model.transcribe(path, beam_size=self.beam_size)
        text = "".join(segment.text for segment in segments)
        return text.strip()

    def _record_temp_wav(self, duration: float = 5.0, samplerate: int = 16000) -> str:
        try:
            import sounddevice as sd
            import soundfile as sf
        except Exception as e:
            raise RuntimeError("sounddevice and soundfile are required for recording: pip install sounddevice soundfile") from e

        channels = 1
        print(f"🎙️ Recording {duration:.1f}s @ {samplerate}Hz...")
        data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
        sd.wait()

        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_path = tmp.name
        tmp.close()

        sf.write(tmp_path, data, samplerate=samplerate)
        return tmp_path

    def transcribe_from_mic(self, duration: float = 5.0, samplerate: int = 16000) -> Optional[str]:
        """Record from mic then transcribe; returns the transcribed text or None."""
        wav_path = None
        try:
            wav_path = self._record_temp_wav(duration, samplerate)
            text = self.transcribe_file(wav_path)
            return text
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass


if __name__ == '__main__':
    # Quick interactive test (if faster-whisper + sounddevice installed)
    try:
        engine = FasterWhisperASREngine(model_name='small')
    except Exception as e:
        print('Initialization error:', e)
    else:
        print('Recording 4s and transcribing...')
        txt = engine.transcribe_from_mic(4.0)
        print('Transcription:', txt)
