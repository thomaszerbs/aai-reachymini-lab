# Troubleshooting — Reachy Mini Mini-Lab

Quick fixes for the attendee lab. If in doubt, **flag a staff member.**
(Operators: deeper setup/ROCm/camera notes live in the [README](../README.md).)

| Symptom | Fix |
|---------|-----|
| Launcher won't start / "venv not found" | Staff: run `./setup.sh` from the repo root first. |
| Robot doesn't move | The robot daemon isn't running. The launcher normally starts it; staff can check with `pgrep -af reachy-mini-daemon`. |
| Daemon fails: `Failed to start daemon: Permission denied` (on `/dev/ttyACM0`) | The current session isn't in the `dialout` group (common on a desktop/terminal opened *before* the group was added). **Log out and back in** (or `newgrp dialout`), then start it again. One-time: `sudo usermod -aG dialout $USER`. A leftover half-dead daemon can also hold the port — `pkill -9 -f reachy-mini-daemon` then retry. |
| `Connection refused` / Ollama errors | Local AI server isn't up: `ollama serve` (the launcher tries to start it automatically). |
| Offline chat won't connect (`Cannot connect to host localhost:11434`) | Ollama is local on `127.0.0.1`; `localhost` can resolve to IPv6 (`::1`) and fail with Wi-Fi off. The lab scripts already use `127.0.0.1`. |
| No audio / too quiet | Raise it in **Settings → Sound** (Output Volume + Device), or the top-right slider. Still quiet? Run `alsamixer`, press **F6**, pick the AMD sound card, and boost it. |
| Talk mode: mic "doesn't pick anything up" | Wrong mic selected. From the launcher menu press **`m`** to list mics, then staff can run it pointed at the right one: `python lab/emo_v2.py --asr --mic Reachy` (robot mic) or `--mic 5` (laptop mic). Also check the input isn't muted in **Settings → Sound → Input**. |
| Vision: "Could not read camera" | Ask staff — may need `python lab/emo_v3.py --camera-device /dev/video0`. |
| Vision: "Device or resource busy" | Staff: the daemon must run with `--no-media` (the launcher does this). Restart it if needed. |
| Vision: browser preview blank | Give it a second; confirm `http://localhost:8080` and the daemon started with `--no-media`. |
| Vision feed is choppy / slideshow | Fixed by forcing MJPEG capture; if it recurs, staff can try a specific `--camera-device`. |
| Want to stop a task / go back to the menu | Press **Ctrl+C**. |
| Ctrl+C won't stop it | Staff: force-kill from another terminal — `pkill -9 -f emo_v` — then re-run. |
