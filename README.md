# Reachy Mini — Interactive AI Robot

A **~10 minute station** for the Developer Zone. Attendees drive a desktop robot
through four hands-on moments from a **one-click launcher** — no terminals, no
code — ending with a robot that **sees, thinks, and speaks entirely on local AMD
hardware**, with a personality they shaped themselves:

1. **🗣️ Voice** (`lab/emo_v1.py`) — expressive robot, **cloud** voice (Edge-TTS)
2. **💻 Offline** (`lab/emo_v2.py`) — same robot, **100% offline** (Piper-TTS + local LLM), snappier; attendee gives it a **personality**
3. **🎙️ Talk** (`lab/emo_v2.py --asr`) — speak to it instead of typing (offline speech recognition)
4. **👀 Eyes** (`lab/emo_v3.py`) — a **local vision model** describes what it sees; attendee sets **how it describes** things

The attendee experience is the launcher **`run-lab.sh`** (desktop icon “Reachy
Mini Lab”). It activates the venv, auto-starts Ollama and the robot daemon,
asks the attendee for a personality / vision instruction, and opens the browser
for the vision task. Prompts are passed via env vars — nothing on disk changes,
so every attendee starts clean.

> 👉 **This README is the operator/booth setup guide** (for *you*, before the event).
> The one-page card attendees follow at the table is **[`lab/LAB.md`](lab/LAB.md)**.
> A classic terminal/IDE flow (running the `lab/emo_v*.py` scripts by hand, editing
> the `# >>> TRY ME <<<` block) still works as a staff fallback.
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

The attendee experience is the **one-click launcher** — it handles the venv,
Ollama, and the robot daemon for you.

### The one-time bits (per machine, before the event)

```bash
# 1) Serial access so the daemon can open the robot's USB port.
sudo usermod -aG dialout $USER
#    ⚠️ Then LOG OUT and back in (or reboot). A shell/desktop session opened
#    before this won't have the group and the daemon fails with "Permission
#    denied" on /dev/ttyACM0. See TROUBLESHOOTING.md.

# 2) Install the desktop icon ("Reachy Mini Lab").
desktop-file-install --dir="$HOME/.local/share/applications" reachy-mini-lab.desktop
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
#    (Edit the paths in reachy-mini-lab.desktop if the repo isn't at
#     /home/amd/aai-reachymini-lab.)
```

### On the day

**Just double-click “Reachy Mini Lab”** on the desktop (or run `./run-lab.sh`
from the repo). The launcher:

- activates `venv/`,
- starts **Ollama** and the **robot daemon** (`--no-media`, freeing the camera
  for the vision task) if they aren't already running,
- shows the task menu, asks the attendee for a personality / vision instruction,
  and opens the browser for the vision task.

Hand the attendee **[`lab/LAB.md`](lab/LAB.md)** as the one-page card.

> **Prefer to run the daemon yourself all day?** You still can:
> ```bash
> source venv/bin/activate && reachy-mini-daemon --no-media
> ```
> The launcher detects it's already up and won't start a second one.

> **No physical robot?** `export PYGLFW_LIBRARY_VARIANT=x11` then
> `reachy-mini-daemon --sim`. The MuJoCo sim has no camera, so the vision task
> needs the real robot.

> **Staff fallback (no launcher).** The scripts still run by hand:
> `python lab/emo_v1.py --chat`, `emo_v2.py --chat` / `--asr`,
> `emo_v3.py --preview-web`, editing the `# >>> TRY ME <<<` block if desired.

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

> **Usually not needed with the launcher.** Attendee personality / vision prompts
> are passed via env vars (`LAB_ROBOT_PERSONA` / `LAB_VISION_PROMPT`) and never
> written to disk, so each run already starts clean. `reset.sh` only matters if a
> staff member hand-edited a `# >>> TRY ME <<<` block in the fallback flow.

---

## Pre-flight check (run before the event)

Fastest check: **run the launcher and walk all four menu items** exactly as an
attendee would.

```bash
# 0. Models present
source venv/bin/activate && ollama list | grep -E "qwen3.5:0.8b|qwen2.5vl"

# 1. The real thing — launcher menu, tasks 1–4
./run-lab.sh
#   1 Voice   : type a line, confirm Reachy moves/talks (needs network)
#   2 Offline : give it a personality, confirm the tone changes ("unplug" demo)
#   3 Talk    : speak; confirm the mic is heard (press 'm' to pick a mic if not)
#   4 Eyes    : type a vision instruction; in the browser (http://localhost:8080)
#               confirm smooth feed, the "Look & Describe" button + Enter both
#               trigger a look, and the feed freezes while it describes.
```

Handy fallbacks when debugging a specific piece:

```bash
python lab/emo_v2.py --list-mics                 # see mics; pick with --mic Reachy / --mic 5
python lab/emo_v3.py --preview-web               # vision only; --camera-device /dev/videoN to override
#   List cameras: v4l2-ctl --list-devices        Save a frame: --save-frame /tmp/look.jpg
```

---

## Repo layout

```
run-lab.sh              Attendee launcher — the main experience (menu of tasks)
start-lab.sh            Opens run-lab.sh in a terminal (used by the desktop icon)
reachy-mini-lab.desktop Double-clickable desktop launcher
lab/          Mini-lab scripts (run from repo root) + reachy-icon.png + LAB.md
models/       Piper voice models
utils/        ASR (mic selection/VAD), Ollama check, action/emotion tests
archive/      Upstream experimental versions (not used in the lab)
```

The launcher passes attendee input to the scripts via env vars
(`LAB_ROBOT_PERSONA`, `LAB_VISION_PROMPT`, plus `--mic`), so the normal flow needs
**no file edits**. Each script also keeps a `# >>> TRY ME <<<` block near the top
for the staff fallback flow — a value there wins over the default but the env-var
override still takes precedence, so the launcher always reflects what the attendee
typed.

## Credits

Forked from [alexhegit/ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat)
(Apache-2.0). See [`LICENSE`](LICENSE).
