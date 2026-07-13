# Reachy Mini Mini-Lab (Advancing AI — Physical AI table)

A **~10 minute station** for the Developer Zone. Attendees **watch** a desktop
robot evolve across two quick demos, then go **hands-on** at the final task,
ending with a robot that **sees, thinks, and speaks entirely on local AMD
hardware**:

1. **`lab/emo_v1.py`** — expressive robot with a **cloud** voice (Edge-TTS) — *watch*
2. **`lab/emo_v2.py`** — the same robot, **100% offline** (Piper-TTS + local LLM), and snappier — *watch (+ the "unplug the network" party trick)*
3. **`lab/emo_v3.py`** — Reachy gets **eyes**: a **local vision model** describes what it sees — *hands-on: attendees edit `VISION_PROMPT`*

> 👉 **This README is the operator/booth setup guide** (for *you*, before the event).
> The script attendees follow at the table is **[`lab/LAB.md`](lab/LAB.md)**.

Older experimental versions from the upstream
[ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat) project live in
[`archive/`](archive/) and are not part of the lab.

---

## Booth hardware (per station)

- 1× **AMD Strix Halo** machine (HP ZBook laptop or HP Z2 G1a) running Ubuntu 24.04
- 1× **Reachy Mini** robot (with built-in camera) connected over USB (`/dev/ttyACM0`)
- Speaker/headphones; the lab is audio-heavy
- Reliable network for setup; Tasks 2 & 3 (offline chat + vision) work fully offline

Plan for **three identical stations**. Set one up, verify it end-to-end, then
replicate.

---

## One-time setup (per station)

Provisioning a fresh station is **two ordered steps**: install the AMD GPU stack
(ROCm) **first**, then run `./setup.sh`. Do them in this order — `setup.sh`
installs and starts Ollama, and Ollama only offloads to the GPU if ROCm is
already present when it starts.

> ⏱️ **Budget 45–90 min and do it the day *before* the event, not the morning
> of.** Step 0 involves a kernel install and **two reboots**; `setup.sh` then
> downloads multi-GB Ollama models. None of this is something you want to be
> doing while attendees wait.

### Step 0 — Install ROCm (GPU acceleration) — **do this first**

On the AMD Strix Halo / Ryzen AI booth machines, the LLM and vision model run on
the GPU. ROCm is **not** installed by `setup.sh` (it involves a new kernel and
reboots, which shouldn't be silently automated). Follow
**[`install-rocm.md`](install-rocm.md)** — the short version:

```bash
# 1) OEM kernel (required for ROCm on Ryzen), then REBOOT #1
sudo apt update && sudo apt install -y linux-oem-24.04c
sudo reboot
uname -r                     # after reboot: confirm 6.14-1018 (or newer)
sudo apt upgrade -y          # make sure the system is current before the driver

# 2) AMD driver + ROCm, then REBOOT #2
wget https://repo.radeon.com/amdgpu-install/7.2/ubuntu/noble/amdgpu-install_7.2.70200-1_all.deb
sudo apt install -y ./amdgpu-install_7.2.70200-1_all.deb
amdgpu-install -y --usecase=rocm --no-dkms
sudo usermod -a -G render,video $LOGNAME
sudo reboot

# 3) Verify the GPU is visible to ROCm
rocminfo | grep gfx          # expect gfx1151 on Strix Halo
```

> **No AMD GPU / just want it working?** You can **skip Step 0** entirely. The
> lab runs fine CPU-only — Ollama automatically falls back to CPU. It's just
> slower (most noticeable on the Task 3 vision model). Everything else is identical.

### Step 1 — Provision the lab with one script — `./setup.sh`

```bash
git clone https://github.com/thomaszerbs/aai-reachymini-lab.git
cd aai-reachymini-lab
export HF_TOKEN=<your token>     # optional but recommended — pre-caches Task 1 moves
./setup.sh
```

`setup.sh` is idempotent (safe to re-run) and consolidates every one-time step.
Use `./setup.sh --help` for options, or `./setup.sh --skip-models` to skip the
slow Ollama model pulls on quick re-runs.

**What `./setup.sh` does:**

1. **System packages** — `apt`-installs Python, audio (`portaudio`, `libsndfile`),
   and the camera/GStreamer stack (`ffmpeg`, `v4l-utils`) the vision task needs.
2. **Python environment** — creates `venv/`, then installs `requirements.txt`
   and `reachy-mini[mujoco]`.
3. **Ollama + models** — installs Ollama and pulls the chat LLM
   (`qwen3.5:0.8b`, Tasks 1–2) and the vision model (`qwen2.5vl:3b`, Task 3).
4. **Piper voice** — verifies the default offline voice is present in `models/`
   (already committed to the repo; only downloads if missing).
5. **Recorded-moves library** — warms the Hugging Face dances/emotions cache for
   Task 1 (needs `HF_TOKEN`; skipped with a note if it's unset).
6. **ROCm GPU check** — *verifies* the ROCm you installed in Step 0 is detected
   and prints how to confirm the GPU is used (it does **not** install ROCm).
7. **Reset baseline** — snapshots the pristine lab scripts into `.lab-baseline/`
   so `./reset.sh` can restore a clean slate between attendees (see below).

### Notes & manual fallback

Every step above can also be run by hand (the full commands live in git history /
`setup.sh` itself), but these operator details are worth keeping handy:

- **Piper voice is already committed** in [`models/`](models/)
  (`en-us-blizzard_lessac-medium.onnx` + `.onnx.json`) — no download needed on a
  normal clone. Add more voices by dropping `.onnx` + matching `.onnx.json` from
  [Piper Voices](https://huggingface.co/rhasspy/piper-voices) into `models/`.
- **Moves library needs `HF_TOKEN`.** To cache the Task 1 (`emo_v1.py`) recorded
  moves ahead of time, export a token before running setup (otherwise it downloads
  on first run of `emo_v1.py`):

```bash
export HF_TOKEN=<your token>
export HF_HOME=${HOME}/huggingface_cache
./setup.sh                 # or: python utils/test_actions.py
```

- **Vision task (`emo_v3.py`) reads the camera directly via V4L2/`ffmpeg`**
  (auto-detecting the "Arducam" device, e.g. `/dev/video0`). This deliberately
  bypasses the SDK/daemon media server, so the
  `Failed to create webrtcsink element ... GStreamer webrtc rust plugin` warning
  you may see from the daemon is **expected and harmless** for this lab. Verify
  with the pre-flight check below.
  - **Start the daemon with `--no-media`** (see "Running the station" below). The
    daemon otherwise opens the camera itself and the vision task fails with
    `Device or resource busy`. Note the Arducam exposes two nodes (`/dev/video0`
    and `/dev/video1`) but **only `/dev/video0` is a usable capture node**.
  - **Live preview is browser-based**: `python lab/emo_v3.py --preview-web` serves
    the feed + a "Look & Describe" button at `http://localhost:8080`. The native
    OpenCV window (`--preview`) is unreliable on these machines (cv2's Qt/xcb GUI
    crashes under Wayland), so it auto-redirects to the browser preview.
- **GPU acceleration (ROCm).** Once ROCm is installed (Step 0 above), the LLM and
  vision model run on the GPU — Ollama auto-detects the Radeon 8060S (`gfx1151`)
  and offloads the model, no flags needed. (Piper-TTS and faster-whisper run on
  CPU, which is fine — those workloads are light.) On the verified Strix Halo
  build ROCm lives at `/opt/rocm-7.2.0`. Verify the GPU is actually used:

```bash
rocminfo | grep gfx          # GPU visible to ROCm (expect gfx1151)
ollama ps                    # after a query: PROCESSOR should read "100% GPU"
journalctl -u ollama | grep -i rocm   # confirms Ollama loaded the ROCm runtime
```

> If `ollama ps` shows `100% CPU` on a station, ROCm isn't being picked up
> (unsupported arch or missing ROCm). As a fallback, set
> `HSA_OVERRIDE_GFX_VERSION=11.0.0` in the ollama service environment and restart
> it. This isn't needed on the verified Strix Halo setup.

- **Different LLM?** The scripts default to `qwen3.5:0.8b`; pass `--model
  <other-model>` to `emo_v1.py`/`emo_v2.py` to try another Ollama model.

---

## Running the station (event day)

Use **two terminals**.

**Terminal A — robot daemon (leave running all day):**

```bash
# One-time per machine: give your user serial access (survives reboots)
sudo usermod -aG dialout $USER
newgrp dialout          # apply the group in this shell now (or log out/in)

source venv/bin/activate   # reachy-mini-daemon lives in the venv — activate it first
reachy-mini-daemon --no-media   # real robot; --no-media frees the camera for the vision task
```

> **Why `--no-media`?** The daemon otherwise opens the robot camera itself, so the
> vision task (Task 3) would fail with `Device or resource busy`. `--no-media`
> disables the daemon's camera/audio/WebRTC (which we don't use — the vision task
> reads the camera directly), leaving the camera free. Motion still works.

> Quick one-off alternative (resets on reboot): `sudo chmod 666 /dev/ttyACM0`.

> No physical robot? Use the simulator instead (still inside the venv):
> `export PYGLFW_LIBRARY_VARIANT=x11` then `reachy-mini-daemon --sim`. (Note: the
> MuJoCo sim has no camera, so the vision task (Task 3, `emo_v3.py`) needs the real
> robot.)

**Terminal B — attendee terminal** (activate the venv and you're ready):

```bash
source venv/bin/activate
```

Then hand the attendee **[`lab/LAB.md`](lab/LAB.md)**.

### Audio / volume

The lab is audio-heavy, so set a comfortable output level before the event. Open
**Settings → Sound**, pick the Reachy Mini speaker as the **Output Device**, and
set the **Output Volume** slider (or use the top-right system-menu slider).

> Prefer the terminal? `alsamixer` works too (F6 picks the output device).

---

## Reset between attendees

Task 3 is hands-on: each attendee edits the `VISION_PROMPT` line (and maybe the
bonus TRY-ME blocks in the earlier tasks). Between attendees, restore a clean
slate with:

```bash
./reset.sh
```

This copies the pristine `lab/emo_v1.py`, `lab/emo_v2.py`, and `lab/emo_v3.py`
back from the `.lab-baseline/` snapshot and touches nothing else. That baseline is
captured automatically by `./setup.sh` (it snapshots the scripts once, on the
first run, so a good-known baseline is never overwritten). If `.lab-baseline/` is
missing, `reset.sh` will tell you to run `./setup.sh` first.

---

## Pre-flight check (run before the event)

Tasks 1–2 are **watch-and-react** demos for attendees, so here you just confirm
each one launches and the robot reacts. Task 3 is the **hands-on edit** task,
so also walk through the `VISION_PROMPT` edit workflow attendees will follow.

```bash
source venv/bin/activate

# 1. LLM + vision models present
ollama list | grep -E "qwen3.5:0.8b|qwen2.5vl"

# 2. Tasks 1–2 — quick "does it launch and react?" check (watch)
#    Type a line, confirm Reachy moves/talks, then Ctrl+C to move on.
python lab/emo_v1.py --chat          # Task 1: cloud Edge-TTS voice — confirm network is up
python lab/emo_v2.py --chat          # Task 2: fully offline — the attendee "unplug the network" demo

# 3. Task 3 (emo_v3) — the hands-on edit task. Verify both:
#    (a) camera + vision works: press Enter, confirm Reachy describes the scene
python lab/emo_v3.py
#    Auto-detects the Arducam; override with --camera-device /dev/videoN.
#    List cameras:  v4l2-ctl --list-devices
#    Save a frame:  python lab/emo_v3.py --save-frame /tmp/look.jpg
#    Live view:     python lab/emo_v3.py --preview-web  (open http://localhost:8080 —
#                   shows the live feed + a "Look & Describe" button; no GUI needed).
#                   NOTE: --preview (native OpenCV window) is unreliable on the booth
#                   machines and auto-redirects to the browser view.
#    (b) the edit workflow: change the VISION_PROMPT line in the
#        `# >>> TRY ME <<<` block of lab/emo_v3.py, save, re-run, confirm the
#        robot's description changes. (This is the one line attendees edit.)
```

---

## Repo layout

```
lab/                 The mini-lab (run scripts from the repo root)
  emo_v1.py          Task 1 — expressive + cloud voice (Edge-TTS)
  emo_v2.py          Task 2 — fully offline (Piper-TTS + local LLM)
  emo_v3.py          Task 3 — local vision model ("Reachy sees")
  EMO_README.md      Per-task version notes
  LAB.md             Attendee-facing lab script
models/              Piper voice models
utils/               ASR, Ollama check, action/emotion tests
archive/             Upstream experimental versions + old docs/assets (not used in the lab)
```

Each lab script has a clearly-marked `# >>> TRY ME <<<` block at the top. In the
main flow attendees edit only Task 3's (`VISION_PROMPT`, in `emo_v3.py`); the
earlier tasks' blocks are for the "💡 Optional" tinkering notes in `LAB.md`
(e.g. the voice-chat toggle in Task 2).
Either way, that block is the one place edits are meant to happen — keep those
blocks intact when updating scripts.

## Credits

Forked from [alexhegit/ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat)
(Apache-2.0). See [`LICENSE`](LICENSE).
