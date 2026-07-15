# Troubleshooting — Reachy Mini Mini-Lab

Quick fixes for the attendee lab. If in doubt, **flag a staff member.**
(Operators: deeper setup/ROCm/camera notes live in the [README](../README.md).)

| Symptom | Fix |
|---------|-----|
| Robot doesn't move | Make sure Terminal A (the daemon) is still running. |
| `Connection refused` / Ollama errors | Local LLM server isn't up: `ollama serve`. |
| Offline chat won't connect (`Cannot connect to host localhost:11434`) | Ollama is local on `127.0.0.1`; `localhost` can resolve to IPv6 (`::1`) and fail with Wi-Fi off. The lab scripts already use `127.0.0.1` — re-run the latest `emo_v2.py`/`emo_v3.py`. |
| No audio / too quiet | Raise it in **Settings → Sound** (Output Volume + Device), or the top-right slider. Still quiet? Run `alsamixer`, press **F6**, pick the AMD sound card, and boost it. |
| Task 3: "Could not read camera" | Ask staff — may need `python lab/emo_v3.py --camera-device /dev/video0`. |
| Task 3: "Device or resource busy" | Staff: restart the daemon as `reachy-mini-daemon --no-media`. |
| Task 3: browser preview blank | Give it a second; confirm `http://localhost:8080` and the daemon started with `--no-media`. |
| Edited a file and it broke | Undo (**Ctrl+Z**) and re-run. |
| Want to stop a program | Press **Ctrl+C** in Terminal B. |
| Ctrl+C won't stop it | Staff: force-kill from another terminal — `pkill -9 -f emo_v` — then re-run. |
| Guide preview jumped to the top | Just scroll back — VS Code re-renders the preview when you switch back to it. |
