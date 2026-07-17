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
import time
from typing import Optional

try:
    from faster_whisper import WhisperModel
except Exception:  # pragma: no cover - runtime optional
    WhisperModel = None


def list_input_devices():
    """Return a list of (index, name, max_input_channels) for input-capable devices."""
    try:
        import sounddevice as sd
    except Exception:
        return []
    devices = []
    for idx, dev in enumerate(sd.query_devices()):
        if dev.get("max_input_channels", 0) > 0:
            devices.append((idx, dev.get("name", "?"), dev["max_input_channels"]))
    return devices


def print_input_devices():
    """Pretty-print available microphones (for --list-mics)."""
    devices = list_input_devices()
    if not devices:
        print("⚠️ No input (microphone) devices found.")
        return
    try:
        import sounddevice as sd
        default_in = sd.default.device[0]
    except Exception:
        default_in = None
    print("🎤 Available microphones (use the number or a name substring):")
    for idx, name, ch in devices:
        marker = "  <- current default" if idx == default_in else ""
        print(f"   [{idx}] {name}  ({ch} in){marker}")
    print("   Tip: the built-in robot mic shows up as 'Reachy Mini Audio'.")


def resolve_input_device(mic_device):
    """Turn a user-supplied mic spec into a sounddevice device index (or None).

    Accepts:
      - None            -> system default (returns None)
      - int / digit str -> that device index
      - other string    -> first input device whose name contains it (case-insensitive)
    Returns an int index, or None to mean "use the default device".
    """
    if mic_device is None:
        return None
    # Numeric (int or a string like "4")
    try:
        return int(mic_device)
    except (TypeError, ValueError):
        pass
    needle = str(mic_device).strip().lower()
    if not needle:
        return None
    for idx, name, _ in list_input_devices():
        if needle in name.lower():
            return idx
    print(f"⚠️ No microphone matching {mic_device!r}; using the system default.")
    return None


class FasterWhisperASREngine:
    """ASR engine built on faster-whisper (CPU) with VAD support.

    Example:
        engine = FasterWhisperASREngine(model_name='small')
        # Fixed recording
        text = engine.transcribe_from_mic(4.0)
        # VAD-based recording (stops when speech ends)
        text = engine.transcribe_from_mic_vad(max_duration=4.0)
    """

    def __init__(self, model_name: str = "small", device: str = "cpu", beam_size: int = 5,
                 mic_device=None):
        if WhisperModel is None:
            raise RuntimeError("faster-whisper not installed. Install with `pip install faster-whisper`")

        self.model_name = model_name
        self.device = device
        self.beam_size = beam_size
        # Which microphone to record from. None = system default (PipeWire/PulseAudio).
        # Can be an int index or a substring of the device name (e.g. "Reachy").
        self.mic_device = resolve_input_device(mic_device)

        # Load model once and reuse
        self.model = WhisperModel(self.model_name, device=self.device)
        
    def configure_for_latency(self):
        """Configure for optimal latency (smaller model, faster processing)"""
        # Use tiny model for faster processing
        self.model_name = "tiny"
        self.beam_size = 1  # Smaller beam size for faster decoding
        # Note: In practice, you'd need to reload the model
        # For simplicity in this example, we'll just update settings

    def transcribe_file(self, path: str, language: str = None) -> str:
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        # Anti-hallucination settings: faster-whisper tends to invent common
        # phrases ("Thank you.", "you", etc.) when fed silence/noise. These
        # thresholds + built-in VAD filtering suppress most of that at the source.
        segments, info = self.model.transcribe(
            path,
            beam_size=self.beam_size,
            language=language,
            vad_filter=True,
            no_speech_threshold=0.6,
            log_prob_threshold=-1.0,
            condition_on_previous_text=False,
        )
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
        data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels,
                      dtype='int16', device=self.mic_device)
        sd.wait()

        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_path = tmp.name
        tmp.close()

        sf.write(tmp_path, data, samplerate=samplerate)
        return tmp_path

    def _record_temp_wav_vad(self, max_duration: float = 5.0, samplerate: int = 16000, silence_threshold: float = 2.0, min_rms: float = 120.0) -> Optional[str]:
        """Record using Voice Activity Detection (VAD) - stops when speech ends.

        Returns the temp WAV path, or None if the clip was too quiet to be speech.
        """
        try:
            import sounddevice as sd
            import soundfile as sf
            import numpy as np
        except Exception as e:
            raise RuntimeError("sounddevice, soundfile, and numpy are required for VAD recording") from e
        
        try:
            import webrtcvad
            # Level 2 (was 3): level 3 is so aggressive it drops quiet/soft speech
            # on many laptop mics, which reads as "the mic doesn't pick anything up".
            vad = webrtcvad.Vad(2)
        except ImportError:
            print("⚠️ webrtcvad not installed. Falling back to fixed recording.")
            return self._record_temp_wav(max_duration, samplerate)

        channels = 1
        frames = []
        dev_name = ""
        if self.mic_device is not None:
            try:
                dev_name = f" [{sd.query_devices(self.mic_device)['name']}]"
            except Exception:
                dev_name = f" [device {self.mic_device}]"
        print(f"🎙️ Listening{dev_name} (max {max_duration:.1f}s) - speak now...")
        
        frame_duration_ms = 30  # WebRTC VAD works best with 10, 20, or 30ms frames
        frame_samples = int(samplerate * frame_duration_ms / 1000)
        
        # Record until trailing silence (only after speech started) or max duration.
        start_time = time.time()
        silent_frames = 0
        required_silent_frames = int(silence_threshold * 1000 / frame_duration_ms)
        speech_started = False   # don't count leading silence before the user speaks
        peak = 0                 # loudest sample seen (for a "did it hear me" hint)

        try:
            with sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16',
                                device=self.mic_device) as stream:
                while (time.time() - start_time) < max_duration:
                    data, _ = stream.read(frame_samples)
                    if data is None:
                        break

                    frames.append(data)
                    peak = max(peak, int(np.abs(data).max()))

                    # Check if frame contains speech
                    is_speech = False
                    try:
                        is_speech = vad.is_speech(data.tobytes(), samplerate)
                    except Exception:
                        # VAD may fail for very short or malformed frames
                        is_speech = False

                    if is_speech:
                        speech_started = True
                        silent_frames = 0  # Reset silence counter
                    elif speech_started:
                        # Only start the "trailing silence" countdown once we've
                        # actually heard speech — otherwise we'd stop instantly
                        # during the natural pause before the user starts talking.
                        silent_frames += 1

                    if speech_started and silent_frames >= required_silent_frames:
                        print(f"🔇 Detected {silence_threshold}s of silence - stopping recording")
                        break
        except Exception as e:
            raise RuntimeError(
                f"Could not open microphone{dev_name}: {e}. "
                f"List mics with --list-mics and pick one with --mic."
            ) from e

        if not frames:
            raise RuntimeError("No audio captured")
        
        audio_data = np.concatenate(frames, axis=0)
        actual_duration = len(audio_data) / samplerate

        # Energy gate: if the whole clip is basically silence/quiet room noise,
        # don't bother transcribing it (avoids Whisper hallucinating on silence).
        rms = float(np.sqrt(np.mean(np.square(audio_data.astype(np.float32)))))
        if rms < min_rms:
            # A very low peak means the mic itself isn't picking up sound (wrong
            # device or muted input) rather than the user simply being quiet.
            if peak < 500:
                print(f"🔇 Mic heard almost nothing (peak={peak}). Is the right mic "
                      f"selected and un-muted? List mics with --list-mics.")
            else:
                print(f"🔇 Clip too quiet (rms={rms:.0f} < {min_rms:.0f}) - ignoring")
            return None

        print(f"⏱️ Recorded {actual_duration:.2f}s (rms={rms:.0f}, peak={peak})")
        
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp_path = tmp.name
        tmp.close()
        
        sf.write(tmp_path, audio_data, samplerate=samplerate)
        return tmp_path

    def transcribe_from_mic(self, duration: float = 5.0, samplerate: int = 16000, language: str = None) -> Optional[str]:
        """Record from mic then transcribe; returns the transcribed text or None."""
        wav_path = None
        try:
            wav_path = self._record_temp_wav(duration, samplerate)
            text = self.transcribe_file(wav_path, language=language)
            return text
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass

    # Phrases faster-whisper commonly hallucinates from silence/noise.
    # Compared case-insensitively after stripping punctuation/whitespace.
    _HALLUCINATION_BLOCKLIST = {
        "", "you", "thank you", "thanks", "thank you.", "thanks for watching",
        "thanks for watching!", "thank you for watching", "bye", "bye.",
        "okay", "ok", "yeah", "so", "uh", "um", "hmm", ".", "the",
        "please subscribe", "subscribe", "i'm sorry",
    }

    @classmethod
    def _is_hallucination(cls, text: str, min_chars: int = 3) -> bool:
        """Heuristic: is this transcription likely noise/silence junk, not real speech?"""
        normalized = "".join(c for c in text.lower() if c.isalnum() or c.isspace()).strip()
        if len(normalized) < min_chars:
            return True
        if normalized in cls._HALLUCINATION_BLOCKLIST:
            return True
        return False

    def transcribe_from_mic_vad(self, max_duration: float = 5.0, samplerate: int = 16000, silence_threshold: float = 2.0, language: str = None, min_rms: float = 120.0) -> Optional[str]:
        """Record from mic using VAD then transcribe; returns the transcribed text or None.

        Returns None if the clip was too quiet or the transcription looks like a
        Whisper hallucination (common when fed silence/background noise).
        """
        wav_path = None
        try:
            wav_path = self._record_temp_wav_vad(max_duration, samplerate, silence_threshold, min_rms=min_rms)
            if wav_path is None:
                return None
            text = self.transcribe_file(wav_path, language=language)
            if self._is_hallucination(text):
                print(f"🚫 Ignoring likely noise/hallucination: {text!r}")
                return None
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
        
        print('\n--- Testing VAD recording ---')
        try:
            txt_vad = engine.transcribe_from_mic_vad(max_duration=4.0)
            print('VAD Transcription:', txt_vad)
        except Exception as e:
            print(f'VAD test error: {e}')
