# FAQ — Reachy Mini Mini-Lab

### 1. How to install ROCm on the Ubuntu Ryzen platform?

Refer to [install-rocm.md](./install-rocm.md).

### 2. How to install Ollama?

For Linux: https://ollama.com/download/linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify it runs on the iGPU:

```bash
ollama run qwen3.5:0.8b "hi" --think=false --verbose ; ollama ps
```

More info on how to use Ollama: https://docs.ollama.com/

### 3. Which models do I need for the lab?

```bash
ollama pull qwen3.5:0.8b    # chat LLM (Tasks 1–2)
ollama pull qwen2.5vl:3b    # vision model used by Task 3 (lab/emo_v3.py)
```

### 4. How do I start the robot?

Start the daemon in its own terminal:

```bash
# Simulator (MuJoCo)
reachy-mini-daemon --sim

# Real robot over USB
sudo chmod 666 /dev/ttyACM0   # adjust port as needed
reachy-mini-daemon --no-media   # --no-media frees the camera for Task 3 (vision)
```

If the GUI fails to launch on Wayland (Ubuntu 24.04 default):

```bash
export PYGLFW_LIBRARY_VARIANT=x11
```

### 5. How do I control the audio volume?

There's no `--volume` flag in the apps; speech plays through your system's audio
stack. On Ubuntu 24.04 (PipeWire):

```bash
wpctl set-volume @DEFAULT_AUDIO_SINK@ 60%      # set to 60%
wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-      # quieter
wpctl set-mute   @DEFAULT_AUDIO_SINK@ toggle   # mute/unmute
```

For a GUI with per-app sliders, install `pavucontrol` (`sudo apt install pavucontrol`)
and adjust the python/sounddevice stream on the **Playback** tab while Reachy speaks.
You may also need to select the ReachyMini device under Ubuntu **Sound** settings.

### 6. Which script does each task run?

| Task | Script | What it does |
|---|---|---|
| 1 | `lab/emo_v1.py` | Expressive robot + cloud voice (Edge-TTS, needs internet) |
| 2 | `lab/emo_v2.py` | Same robot, 100% offline (Piper-TTS + local LLM, `--asr` for mic) |
| 3 | `lab/emo_v3.py` | Local vision model — "Reachy sees" |

See [lab/EMO_README.md](./lab/EMO_README.md) for details. Older experimental versions
live in [`archive/`](archive/) and are not part of the lab.

### 7. Task 3 shows "Failed to create webrtcsink ... GStreamer webrtc plugin"

This is **expected and harmless**. Task 3 reads the camera directly from its
V4L2 device via `ffmpeg` and bypasses the daemon's media server. Make sure
`ffmpeg` is installed. If the camera can't be read, select the device explicitly:

```bash
python lab/emo_v3.py --camera-device /dev/video2
```

### 8. Ollama connectivity check

```bash
curl http://localhost:11434/api/tags     # is the server up?
ollama list                              # which models are installed?
python utils/test_ollama_connection.py   # full connectivity test
```

### 9. How do I *show* the AMD GPU is doing the work (live, during the demo)?

Nice booth moment: prove the LLM/vision model really runs on the AMD GPU while
Reachy is thinking. Open a small third terminal next to the two lab terminals and
run a live view, then chat with Reachy (Task 2) or trigger a look (Task 3) — you'll
see GPU utilization jump on each reply.

```bash
# Live GPU utilization (official AMD tool) — watch the "GFX" / usage % spike
# while Reachy generates a reply. Ctrl+C to stop.
amd-smi monitor
```

Two quick confirmations if you'd rather not watch a live meter:

```bash
# 1) Ollama's own view — during/just after a reply, PROCESSOR reads "100% GPU"
watch -n 1 ollama ps

# 2) One-off snapshot of GPU use and VRAM
rocm-smi
```

> If `ollama ps` shows `100% CPU` instead, ROCm isn't being picked up — the lab
> still works, just slower. See the ROCm notes in the README to enable the GPU.
