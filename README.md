# Reachy Mini — Interactive AI Robot

A **~10 minute station** for the Developer Zone. Attendees **watch** a desktop
robot evolve across two demos, then go **hands-on** at the final task — ending
with a robot that **sees, thinks, and speaks entirely on local AMD hardware**:

1. **`lab/emo_v1.py`** — expressive robot, **cloud** voice (Edge-TTS) — *watch*
2. **`lab/emo_v2.py`** — same robot, **100% offline** (Piper-TTS + local LLM), snappier — *watch (+ the "unplug the network" trick)*
3. **`lab/emo_v3.py`** — Reachy gets **eyes**: a **local vision model** describes what it sees — *hands-on: attendees edit `VISION_PROMPT`*

> 👉 **This README is the operator/booth setup guide** (for *you*, before the event).
> The script attendees follow at the table is **[`lab/LAB.md`](lab/LAB.md)**.
> Upstream experimental versions live in [`archive/`](archive/) (not part of the lab).

---

## Hardware setup

- **AMD Strix Halo** machine (HP ZBook laptop) running Ubuntu 24.04
- **Reachy Mini** robot over USB (`/dev/ttyACM0`), with speaker, mic, and camera built-in
- Network for setup; Tasks 2 & 3 (offline chat + vision) then work fully offline

---

## One-time setup

Two ordered steps: install the AMD GPU stack (ROCm) **first**, then run
`./setup.sh`. Order matters — `setup.sh` starts Ollama, and Ollama only offloads
to the GPU if ROCm is already present when it starts.

> ⏱️ **Budget 30 min, before the event.** Step 0 involves a kernel
> install and **two reboots**; `setup.sh` then downloads multi-GB Ollama models.
> Not something to do while attendees wait.

### Step 0 — Install ROCm (GPU acceleration) — **do this first**

The LLM and vision model run on the GPU. ROCm is **not** installed by `setup.sh`
(it involves a new kernel and reboots, which shouldn't be silently automated).
Follow **[`install-rocm.md`](install-rocm.md)** — the short version:

```bash
# 1) OEM kernel (required for ROCm on Ryzen), then REBOOT #1
sudo apt update && sudo apt install -y linux-oem-24.04c
sudo reboot
uname -r                     # after reboot: confirm 6.14-1018 (or newer)
sudo apt upgrade -y          # bring the system current before the driver

# 2) AMD driver + ROCm, then REBOOT #2
wget https://repo.radeon.com/amdgpu-install/7.2/ubuntu/noble/amdgpu-install_7.2.70200-1_all.deb
sudo apt install -y ./amdgpu-install_7.2.70200-1_all.deb
amdgpu-install -y --usecase=rocm --no-dkms
sudo usermod -a -G render,video $LOGNAME
sudo reboot

# 3) Verify the GPU is visible to ROCm
rocminfo | grep gfx          # expect gfx1151 on Strix Halo
```

> **No AMD GPU / just want it working?** **Skip Step 0** entirely — the lab runs
> fine CPU-only (Ollama auto-falls back to CPU). Just slower, most noticeably on
> the Task 3 vision model. Everything else is identical.

### Step 1 — Provision with one script — `./setup.sh`

```bash
git clone https://github.com/thomaszerbs/aai-reachymini-lab.git
cd aai-reachymini-lab
./setup.sh
```

`setup.sh` is idempotent (safe to re-run). Use `--help` for options, or
`--skip-models` to skip the slow Ollama model pulls on quick re-runs.

**What it does:** (1) `apt` system packages incl. audio + camera/GStreamer stack;
(2) creates `venv/` and installs `requirements.txt` + `reachy-mini[mujoco]`;
(3) installs Ollama and pulls the chat LLM (`qwen3.5:0.8b`) and vision model
(`qwen2.5vl:3b`); (4) verifies the committed Piper voice in `models/`;
(5) pre-caches the Task 1 moves library (optional `HF_TOKEN`, see below);
(6) *checks* ROCm is detected (does **not** install it); (7) snapshots the lab
files into `.lab-baseline/` for `./reset.sh`.

### Operator notes

- **Piper voice is committed** in [`models/`](models/)
  (`en-us-blizzard_lessac-medium.onnx` + `.json`) — no download on a normal clone.
  Add voices by dropping `.onnx` + matching `.onnx.json` from
  [Piper Voices](https://huggingface.co/rhasspy/piper-voices) into `models/`.
- **Vision task reads the camera directly** via V4L2/`ffmpeg`, bypassing the
  daemon's media server. Start the daemon with **`--no-media`** or Task 3 fails
  with `Device or resource busy` (the daemon's `webrtcsink ... GStreamer webrtc
  plugin` warning is expected and harmless). It auto-detects the "Arducam" —
  which exposes `/dev/video0` and `/dev/video1`, but **only `/dev/video0`** works.
  Live preview is **browser-based** (`--preview-web`, `http://localhost:8080`);
  `--preview` (native OpenCV) is unreliable under Wayland and redirects there.
- **GPU (ROCm).** Once installed, Ollama auto-detects the Radeon 8060S (`gfx1151`)
  and offloads — no flags. (Piper-TTS and faster-whisper stay on CPU; they're
  light.) On the verified build ROCm lives at `/opt/rocm-7.2.0`. Confirm it's used:
  ```bash
  rocminfo | grep gfx                   # GPU visible to ROCm (expect gfx1151)
  ollama ps                             # after a query: PROCESSOR reads "100% GPU"
  journalctl -u ollama | grep -i rocm   # Ollama loaded the ROCm runtime
  ```
  If `ollama ps` shows `100% CPU`, ROCm isn't picked up — as a fallback set
  `HSA_OVERRIDE_GFX_VERSION=11.0.0` in the ollama service and restart it (not
  needed on the verified Strix Halo setup).

---

## Running the station (event day)

Use **two terminals**.

**Terminal A — robot daemon (leave running all day):**

```bash
# One-time per machine: serial access (survives reboots)
sudo usermod -aG dialout $USER
newgrp dialout                  # apply now in this shell (or log out/in)

source venv/bin/activate        # the daemon lives in the venv
reachy-mini-daemon --no-media   # --no-media frees the camera for the vision task
```

> **No physical robot?** `export PYGLFW_LIBRARY_VARIANT=x11` then
> `reachy-mini-daemon --sim`. The MuJoCo sim has no camera, so Task 3 needs the
> real robot.

**Terminal B — attendee terminal:** `source venv/bin/activate`, then hand them
**[`lab/LAB.md`](lab/LAB.md)**.

### 🔊 Audio / volume

The lab is audio-heavy — set a comfortable level first via **Settings → Sound**
(pick the Reachy Mini speaker as Output Device + set Output Volume), or the
top-right slider.

> **Still too quiet?** Run `alsamixer` in a terminal, press **F6** to select the
> AMD sound card, and boost the audio there.

---

## Reset between attendees

```bash
./reset.sh
```

Restores the pristine lab files (`emo_v1/2/3.py` + `LAB.md`) from the
`.lab-baseline/` snapshot `setup.sh` captured, and touches nothing else. If
`.lab-baseline/` is missing, it tells you to run `./setup.sh` first.

---

## Pre-flight check (run before the event)

Tasks 1–2 are watch-and-react (just confirm each launches and the robot reacts);
Task 3 is the hands-on edit, so also walk the `VISION_PROMPT` workflow.

```bash
source venv/bin/activate

# 1. Models present
ollama list | grep -E "qwen3.5:0.8b|qwen2.5vl"

# 2. Tasks 1–2 — type a line, confirm Reachy moves/talks, Ctrl+C to move on
python lab/emo_v1.py --chat          # Task 1: cloud voice — confirm network is up
python lab/emo_v2.py --chat          # Task 2: fully offline — the "unplug" demo

# 3. Task 3 — verify (a) camera+vision and (b) the edit workflow
python lab/emo_v3.py                  # press Enter; confirm Reachy describes the scene
#   Auto-detects the Arducam; override: --camera-device /dev/videoN
#   List cameras: v4l2-ctl --list-devices   Save a frame: --save-frame /tmp/look.jpg
#   Live view:    --preview-web  (http://localhost:8080; --preview redirects here)
#   Then change VISION_PROMPT in the `# >>> TRY ME <<<` block, save, re-run,
#   and confirm the description changes. (This is the one line attendees edit.)
```

---

## Repo layout

```
lab/          Mini-lab scripts (run from repo root) + EMO_README.md + LAB.md
models/       Piper voice models
utils/        ASR, Ollama check, action/emotion tests
archive/      Upstream experimental versions (not used in the lab)
```

Each lab script has a `# >>> TRY ME <<<` block near the top — the one place edits
are meant to happen (keep it intact when updating scripts). In the main flow
attendees edit only Task 3's `VISION_PROMPT`.

## Credits

Forked from [alexhegit/ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat)
(Apache-2.0). See [`LICENSE`](LICENSE).
