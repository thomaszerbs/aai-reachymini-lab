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

**Provision each fresh station with one script — `./setup.sh`:**

```bash
git clone <repo> && cd aai-reachymini-lab && ./setup.sh
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
6. **ROCm GPU check** — detects ROCm and prints how to confirm the GPU is used.
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
- **GPU acceleration (ROCm).** On the booth Strix Halo machines the LLM and
  vision model run on the GPU — Ollama auto-detects the Radeon 8060S (`gfx1151`)
  and offloads the model, no flags needed. (Piper-TTS and faster-whisper run on
  CPU, which is fine — those workloads are light.) ROCm is preinstalled at
  `/opt/rocm-7.2.0`; to image a fresh station, follow
  [`install-rocm.md`](install-rocm.md). Verify the GPU is actually used:

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

reachy-mini-daemon      # real robot (omit --sim)
```

> Quick one-off alternative (resets on reboot): `sudo chmod 666 /dev/ttyACM0`.

> No physical robot? Use the simulator instead: `export PYGLFW_LIBRARY_VARIANT=x11`
> then `reachy-mini-daemon --sim`. (Note: the MuJoCo sim has no camera, so the
> vision task (Task 3, `emo_v3.py`) needs the real robot.)

**Terminal B — attendee terminal** (activate the venv and you're ready):

```bash
source venv/bin/activate
```

Then hand the attendee **[`lab/LAB.md`](lab/LAB.md)**.

### Audio / volume

The lab is audio-heavy, so set a comfortable output level before the event. From
the terminal:

```bash
alsamixer        # arrow keys to adjust volume, M to (un)mute, Esc to exit
```

> Pick the right output device with F6 inside `alsamixer` if there are several.

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
#    Live view:     python lab/emo_v3.py --preview  (opens a window showing what
#                   Reachy sees; needs a display, uses opencv-python from requirements)
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
earlier tasks' blocks are for the optional "Bonus: tinker if you have time"
section of `LAB.md`.
Either way, that block is the one place edits are meant to happen — keep those
blocks intact when updating scripts.

## Credits

Forked from [alexhegit/ReachyMiniChat](https://github.com/alexhegit/ReachyMiniChat)
(Apache-2.0). See [`LICENSE`](LICENSE).
