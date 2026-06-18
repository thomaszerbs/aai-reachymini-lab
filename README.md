# Reachy Mini Mini-Lab (Advancing AI — Physical AI table)

A **10–15 minute hands-on station** for the Developer Zone. Attendees build up a
desktop robot across four quick stations and end with a robot that **sees, thinks,
and speaks entirely on local AMD hardware**:

1. **`emo_v1.py`** — hand-coded emotion engine (intro)
2. **`emo_v6.py`** — expressive robot with a **cloud** voice (Edge-TTS)
3. **`emo_v8.py`** — the same robot, **100% offline** (Piper-TTS + local LLM)
4. **`emo_v9_vision.py`** — Reachy gets **eyes**: a **local vision model** describes what it sees

> 👉 **This README is the operator/booth setup guide** (for *you*, before the event).
> The script attendees follow at the table is **[`docs/WORKSHOP.md`](docs/WORKSHOP.md)**.

Older experimental versions from the upstream
[ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat) project live in
[`archive/`](archive/) and are not part of the lab.

---

## Booth hardware (per station)

- 1× **AMD Strix Halo** machine (HP ZBook laptop or HP Z2 G1a) running Ubuntu 24.04
- 1× **Reachy Mini** robot (with built-in camera) connected over USB (`/dev/ttyACM0`)
- Speaker/headphones; the lab is audio-heavy
- Reliable network for setup; Stations 3 & 4 work fully offline

Plan for **three identical stations**. Set one up, verify it end-to-end, then
replicate.

---

## One-time setup (per station)

### 1. System packages (incl. camera/GStreamer for Station 4)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl espeak ffmpeg \
    libsndfile1 portaudio19-dev libcairo2-dev libgirepository1.0-dev \
    python3-gi gir1.2-gst-plugins-base-1.0 libgstreamer1.0-0 gstreamer1.0-tools \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-libav
```

> **Station 4 (camera) note:** the lab reads the robot's camera **directly from its
> V4L2 device using `ffmpeg`** (auto-detecting the "Arducam" device, e.g.
> `/dev/video2`). This deliberately bypasses the SDK/daemon media server, so the
> `Failed to create webrtcsink element ... GStreamer webrtc rust plugin` warning
> you may see from the daemon is **expected and harmless** for this lab. Make sure
> `ffmpeg` and (optionally) `v4l2-utils` are installed. Verify with the pre-flight
> check below.

### 2. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install "reachy-mini[mujoco]"
```

`requirements.txt` includes everything the lab needs. Station 4 additionally uses
the system `ffmpeg` binary (installed above) to grab camera frames.

### 3. Ollama + models (LLM **and** vision model)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve            # leave running (or rely on the systemd service)

ollama pull qwen3:0.6b      # default chat LLM (Stations 1–3)
ollama pull qwen3.5:0.8b    # slightly larger chat LLM (used at this station)
ollama pull qwen2.5vl:3b    # vision model used by Station 4
```

The scripts default to `qwen3:0.6b`. To use the larger model, pass `--model`:

```bash
python emo_v8.py --chat --model qwen3.5:0.8b
python emo_v6.py --chat --model qwen3.5:0.8b
```

> Want `qwen3.5:0.8b` to be the default everywhere (no `--model` needed)? It's a
> one-line change per script — say the word and it can be wired in.

### 4. Piper voice models

The English voice used by default is already in [`models/`](models/)
(`en-us-blizzard_lessac-medium.onnx` + `.onnx.json`). To add more, download
`.onnx` + matching `.onnx.json` from
[Piper Voices](https://huggingface.co/rhasspy/piper-voices) into `models/`.

### 5. Recorded-moves library (Station 2)

`emo_v6.py` uses the Hugging Face dances/emotions move library, downloaded on first
run. Log in once so it caches:

```bash
export HF_TOKEN=<your token>
export HF_HOME=${HOME}/huggingface_cache
mkdir -p ${HF_HOME}
python utils/test_actions.py   # downloads + plays the recorded moves once
```

### 6. GPU acceleration (ROCm)

On the booth Strix Halo machines, **the LLM and vision model run on the GPU** via
ROCm — Ollama auto-detects the Radeon 8060S (`gfx1151`) and offloads the model, no
flags needed. (Piper-TTS and faster-whisper run on CPU; they don't use ROCm, and
that's fine — those workloads are light.)

ROCm is already installed at `/opt/rocm-7.2.0`. If you're imaging a fresh station,
follow [`install-rocm.md`](install-rocm.md). Verify the GPU is actually being used:

```bash
rocminfo | grep gfx          # GPU visible to ROCm (expect gfx1151)
ollama ps                    # after a query: PROCESSOR should read "100% GPU"
journalctl -u ollama | grep -i rocm   # confirms Ollama loaded the ROCm runtime
```

> If `ollama ps` shows `100% CPU` on a station, ROCm isn't being picked up
> (unsupported arch or missing ROCm). As a fallback, set
> `HSA_OVERRIDE_GFX_VERSION=11.0.0` in the ollama service environment and restart it.
> This isn't needed on the verified Strix Halo setup.

---

## Running the station (event day)

Use **two terminals**.

**Terminal A — robot daemon (leave running all day):**

```bash
# One-time per machine: give your user serial access (survives reboots)
sudo usermod -aG dialout $USER
newgrp dialout          # apply the group in this shell now (or log out/in)

reachy-mini-daemon      # real robot (omit --sim)
```

> Quick one-off alternative (resets on reboot): `sudo chmod 666 /dev/ttyACM0`.

> No physical robot? Use the simulator instead: `export PYGLFW_LIBRARY_VARIANT=x11`
> then `reachy-mini-daemon --sim`. (Note: the MuJoCo sim has no camera, so Station 4
> needs the real robot.)

**Terminal B — attendee terminal** (activate the venv and you're ready):

```bash
source venv/bin/activate
```

Then hand the attendee **[`docs/WORKSHOP.md`](docs/WORKSHOP.md)**.

### Audio / volume

The lab is audio-heavy, so set a comfortable output level before the event. From
the terminal:

```bash
alsamixer        # arrow keys to adjust volume, M to (un)mute, Esc to exit
```

> Pick the right output device with F6 inside `alsamixer` if there are several.

---

## Pre-flight check (run before the event)

```bash
source venv/bin/activate

# 1. LLM + vision models present
ollama list | grep -E "qwen3:0.6b|qwen3.5:0.8b|qwen2.5vl"

# 2. Each station launches (Ctrl+C after the robot reacts)
python emo_v1.py --chat
python emo_v6.py --chat
python emo_v8.py --chat

# 3. Camera + vision works (press Enter, confirm Reachy describes the scene)
python emo_v9_vision.py
#    Auto-detects the Arducam; override with --camera-device /dev/videoN.
#    List cameras:  v4l2-ctl --list-devices
#    Save a frame:  python emo_v9_vision.py --save-frame /tmp/look.jpg
```

---

## Repo layout

```
emo_v1.py            Station 1 — hand-coded emotion engine
emo_v6.py            Station 2 — expressive + cloud voice (Edge-TTS)
emo_v8.py            Station 3 — fully offline (Piper-TTS + local LLM)
emo_v9_vision.py     Station 4 — local vision model ("Reachy sees")
docs/WORKSHOP.md     Attendee-facing lab script
models/              Piper voice models
utils/               ASR, Ollama check, action/emotion tests
archive/             Upstream experimental versions (not used in the lab)
```

Each lab script has a clearly-marked `# >>> TRY ME <<<` block at the top — that's
the one place attendees edit. Keep those blocks intact when updating scripts.

## Credits

Forked from [alexhegit/ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat)
(Apache-2.0). See [`LICENSE`](LICENSE).
