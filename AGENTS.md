# AGENTS.md — Reachy Mini Mini-Lab

This file contains essential information for AI coding agents working on this project.

This repo is a **10–15 minute hands-on mini-lab** for the Advancing AI "Physical AI"
table (Developer Zone). Attendees progress through four stations and end with a robot
that **sees, thinks, and speaks entirely on local AMD hardware**. It was repurposed
from the upstream [ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat) project;
unused experimental versions now live in `archive/`.

The two key docs:
- **`README.md`** — operator/booth setup guide (for staff, before the event).
- **`docs/WORKSHOP.md`** — the attendee-facing lab script followed at the table.

Each lab script has a `# >>> TRY ME <<<` block at the top — the single place attendees
are meant to edit. **Preserve these blocks** when modifying scripts.

---

## Project Overview

Each station integrates:

- **Ollama LLM** for conversational AI (local inference)
- **Ollama VLM** (`qwen2.5vl:3b`) for local vision / scene description (Station 4)
- **Piper-TTS** for offline text-to-speech synthesis
- **Edge-TTS** for cloud neural voices (Station 2, the "cloud" contrast)
- **faster-whisper** for automatic speech recognition (ASR)
- **Reachy Mini SDK** for robot motion control, animation, and camera access

The end state is a fully offline, emotion-driven, *seeing* conversational robot.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| Robot SDK | `reachy-mini` (real hardware + MuJoCo simulation) |
| LLM Backend | Ollama (local API at `http://localhost:11434`) |
| Vision (VLM) | Ollama `qwen2.5vl:3b` (local, Station 4) |
| Camera capture | `ffmpeg` reading the robot's V4L2 device directly |
| TTS Engine | Piper-TTS (offline ONNX models) + Edge-TTS (cloud) |
| ASR Engine | faster-whisper (CPU inference) |
| VAD | webrtcvad-wheels |
| Audio I/O | sounddevice + soundfile |
| HTTP Client | aiohttp (async) |

---

## Project Structure

```
aai-reachymini-lab/
├── emo_v1.py                    # Station 1 — hand-coded emotion engine
├── emo_v6.py                    # Station 2 — expressive + cloud voice (Edge-TTS)
├── emo_v8.py                    # Station 3 — fully offline (Piper-TTS + local LLM)
├── emo_v9_vision.py             # Station 4 — local vision model ("Reachy sees")
├── utils/                       # Utility modules
│   ├── asr.py                   # FasterWhisper ASR engine with VAD
│   ├── test_actions.py          # Test robot recorded moves
│   ├── test_edge_tts_voices.py  # Edge-TTS voice discovery
│   ├── test_emotion_analysis.py # Emotion analysis testing
│   ├── test_ollama_connection.py # Ollama connectivity check
│   ├── latency_harness.py       # Performance testing
│   └── simple_interact.py       # Manual robot testing
├── models/                      # Piper-TTS voice models (.onnx + .json)
├── docs/
│   └── WORKSHOP.md              # Attendee-facing mini-lab script
├── archive/                     # Upstream experimental versions (NOT used in lab)
├── requirements.txt             # Python dependencies
├── README.md                    # Operator/booth setup guide
└── AGENTS.md                    # This file
```

> Note: `emo_v8.py` imports its emotion engine from `emo_v6.py`
> (`from emo_v6 import EmotionControllerV6`), and `emo_v9_vision.py` reuses
> `EmotionControllerV71` from `emo_v8.py`. So the dependency chain is
> v9_vision → v8 → v6. Do not remove v6 or v8.

---

## Mini-Lab Stations (active files)

| Station | File | Key Feature | Runs |
|---------|------|-------------|------|
| 1 | `emo_v1.py` | Hand-coded keyword emotion engine | Local |
| 2 | `emo_v6.py` | Continuous synchronized actions + Edge-TTS voice | Cloud voice |
| 3 | `emo_v8.py` | Fully offline (Piper-TTS + local LLM) | Local |
| 4 | `emo_v9_vision.py` | Local vision model describes the camera view | Local |

The narrative arc: hand-coded → cloud-assisted → 100% offline on AMD → offline + vision.

**Archived** (in `archive/`, not part of the lab): `emo_v2/v3/v4/v5/v7.py`,
`emo_v1_zh.py`, `fix_v6.py`.

---

## Setup and Installation

### System Requirements

- **OS**: Ubuntu 24.04 (developed on AMD Ryzen™ AI Max+ 395)
- **Python**: 3.8+
- **Hardware**: CPU sufficient; AMD ROCm optional for GPU acceleration

### System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip espeak ffmpeg libsndfile1 portaudio19-dev
```

### Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install "reachy-mini[mujoco]"
```

### Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Chat LLM (Stations 1–3) and vision model (Station 4)
ollama pull qwen3:0.6b
ollama pull qwen2.5vl:3b
```

### Piper Voice Models

Download `.onnx` and `.onnx.json` files from:
- https://github.com/rhasspy/piper/releases/tag/v0.0.2
- https://huggingface.co/rhasspy/piper-voices

Place in `models/` directory.

---

## Running the Application

### Start the robot daemon (Terminal A — leave running)

```bash
# Real robot (booth setup): allow serial access, then start the daemon
sudo chmod 666 /dev/ttyACM0
reachy-mini-daemon

# Simulator alternative (no camera, so Station 4 won't work):
export PYGLFW_LIBRARY_VARIANT=x11
reachy-mini-daemon --sim
```

### Run the stations (Terminal B)

```bash
python emo_v1.py --chat            # Station 1
python emo_v6.py --chat            # Station 2 (cloud Edge-TTS voice)
python emo_v8.py --chat            # Station 3 (offline; --asr for mic input)
python emo_v9_vision.py            # Station 4 (press Enter to look; needs camera)
```

### Common CLI Flags

| Flag | Scripts | Description |
|------|---------|-------------|
| `--chat` | v1, v6, v8 | Start interactive text chat |
| `--asr [auto\|zh\|en]` | v8 | Enable microphone ASR input |
| `--model` | v1*, v6, v8 | Ollama LLM name (default: `qwen3:0.6b`) |
| `--piper-model` | v8, v9_vision | Path to Piper `.onnx` voice model |
| `--vlm-model` | v9_vision | Ollama vision model (default: `qwen2.5vl:3b`) |
| `--save-frame PATH` | v9_vision | Save captured camera frame for debugging |
| `--gentle` | v6, v8, v9_vision | Subtler motions for nearby humans |
| `--debug` | v6, v8, v9_vision | Verbose debug output |
| `--test-tts` / `--test-actions` | v6 | Component self-tests |

\* `emo_v1.py` only exposes `--test` and `--chat`; its model is set in the TRY ME block.

---

## Code Organization

### Core Classes

#### `PiperTTSEngine` (emo_v8.py)
Offline TTS wrapper around piper-tts library.
- Loads ONNX voice models
- Synthesizes speech to temporary WAV files
- Plays audio via sounddevice

#### `FasterWhisperASREngine` (utils/asr.py)
ASR engine with VAD support.
- `transcribe_from_mic(duration)` — Fixed-length recording
- `transcribe_from_mic_vad(max_duration, silence_threshold)` — VAD-based recording

#### `EmotionControllerV6` (emo_v6.py)
Base emotion controller with:
- Emotion analysis from text (`analyze_emotion`)
- Recorded moves library integration
- Lip-sync controller
- Combined action sequences (eye blink + body yaw + head + antennas)
- `speak_with_expression_parallel(text, emotion, intensity, level)` — speak + move

#### `EmotionControllerV71` (emo_v8.py)
Extends `EmotionControllerV6`, replacing Edge-TTS with Piper-TTS. Reused by Station 4.

#### `ChatAppWithPiper` (emo_v8.py)
Station 3 app: async Ollama chat + ASR/TTS coordination + robot animation.

#### `VisionApp` (emo_v9_vision.py)
Station 4 app: captures a JPEG frame directly from the robot's V4L2 camera
(`ffmpeg`, auto-detecting the "Arducam" device, e.g. `/dev/video2`), base64-encodes
it, streams a description from the local Ollama VLM, then reuses
`EmotionControllerV71` to speak + react. The robot is created with
`media_backend="no_media"` (motion only) — we do **not** use the SDK media server.

> Why direct V4L2 instead of `reachy.media.get_frame()`? The SDK camera paths
> (LOCAL IPC and WEBRTC) both depend on the daemon's media server, which fails to
> start on the booth machines because the GStreamer Rust webrtc plugin
> (`webrtcsink`) is missing. Reading the V4L2 device directly avoids that
> dependency entirely and is more reliable for the table. Reachy's camera is the
> "Arducam" device; the other `/dev/video*` nodes may be unrelated USB webcams.

---

## Development Conventions

### Code Style

- Use **type hints** for function signatures
- Use **async/await** for I/O-bound operations (HTTP, TTS)
- Use **threading** for CPU-bound operations (ASR inference)
- Prefix private methods with underscore: `_helper_method()`
- Use emoji indicators in user-facing output: ✅ ❌ ⚠️ 🤖

### Error Handling

```python
try:
    result = await async_operation()
except asyncio.TimeoutError:
    print("⚠️ Operation timed out")
    return None
except Exception as e:
    if self.debug:
        import traceback
        traceback.print_exc()
    return None
```

### Adding New Features

1. **Incremental changes**: Make small, testable modifications
2. **Version files**: Create new `emo_v{N}.py` for major changes
3. **CLI flags**: Add argparse arguments for configuration
4. **Documentation**: Update relevant README files

---

## Testing

### Test Robot Actions

```bash
python utils/test_actions.py
```

### Test ASR

```bash
python utils/asr.py  # Interactive test
```

### Test Ollama Connection

```bash
python utils/test_ollama_connection.py
```

### Component Tests (emo_v6+)

```bash
# Test TTS only
python emo_v6.py --test-tts

# Test robot actions
python emo_v6.py --test-actions

# Test Edge-TTS voices
python utils/test_edge_tts_voices.py
```

---

## Key Dependencies

See `requirements.txt` for full list:

```
requests>=2.31.0
numpy>=1.24.0
scipy>=1.10.0
edge-tts>=1.2.0
soundfile>=0.12.1
sounddevice>=0.4.8
aiohttp>=3.9.0
faster-whisper>=1.2.1
webrtcvad-wheels>=2.0.14
piper-tts>=1.4.0
```

Station 4 also needs the system `ffmpeg` binary (apt) for V4L2 camera capture.

---

## Troubleshooting

### Audio Issues
- Ensure `libsndfile1` and `portaudio19-dev` are installed
- Check audio devices: `aplay -l` (Linux)
- Verify `sounddevice` is installed in venv

### Robot Connection
- Ensure `reachy-mini-daemon` is running (Terminal A)
- Real robot: serial port at `/dev/ttyACM0` (`sudo chmod 666 /dev/ttyACM0` or add user to `dialout`)
- Sim only: `export PYGLFW_LIBRARY_VARIANT=x11` for Wayland GUI issues

### Ollama Issues
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check model availability: `ollama list` (need `qwen3:0.6b` and `qwen2.5vl:3b`)

### Camera / Vision (Station 4) Issues
- Station 4 reads the robot camera directly from its V4L2 device (no SDK media
  server). It auto-detects the "Arducam" device; override with
  `--camera-device /dev/videoN`.
- List cameras: `v4l2-ctl --list-devices`. Reachy's camera is the Arducam
  (e.g. `/dev/video2`); other nodes may be unrelated USB webcams.
- `Device or resource busy` → another process holds that camera; pick the correct
  Arducam node or stop the other process.
- The MuJoCo simulator has **no camera** — Station 4 requires the real robot.
- Debug the feed independently: `python emo_v9_vision.py --save-frame /tmp/look.jpg`,
  or `ffmpeg -f v4l2 -i /dev/video2 -frames:v 1 /tmp/look.jpg`.
- (FYI: the daemon's `webrtcsink` media-server error is expected and harmless for
  the lab — we bypass the media server by reading V4L2 directly.)

---

## Security Considerations

- Ollama API runs locally on `localhost:11434` — no external exposure
- Piper-TTS is fully offline — no cloud dependencies for speech
- ASR runs locally on CPU — no audio data leaves the machine
- Edge-TTS (Station 2 / `emo_v6.py`) requires internet — cloud-based Microsoft voices
- The vision model (Station 4) runs locally — camera images never leave the machine

---

## Language Notes

- Project documentation uses **English** primarily
- Code comments and docstrings use **English**
- The robot supports **multilingual** TTS (English, Chinese, etc.); the booth lab
  defaults to English voices and the `qwen3:0.6b` LLM

---

## References

- Reachy Mini SDK: https://docs.pollen-robotics.com/
- Ollama: https://ollama.com/
- Piper TTS: https://github.com/rhasspy/piper
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
