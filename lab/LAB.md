# Reachy Mini Mini-Lab — Build a Robot That Runs Entirely on AMD

Welcome! In the next **~10 minutes** you'll bring a little desktop robot to life.
You'll **run and chat with it** across two quick demos — from a robot with a
**cloud** voice to one that thinks and talks **100% offline on this AMD machine** —
and then **you'll take the controls** and give Reachy *eyes*. No cloud at the finish
line.

> **You only *have* to edit one thing — in Task 3.** Tasks 1 and 2 you just **run
> and chat** with (any editing there is optional). This station is pre-configured:
> the robot and the AI models are ready to go.

**Key:**

- ▶️ **run & chat** = just run the command and type a message to Reachy.
- ✋ **your turn** = you edit a `# >>> TRY ME <<<` block yourself (only in Task 3).
- 💡 **Optional** = nice-to-try extras you can skip.

**The arc (3 tasks):**

| Task | What happens | You... | Runs where |
|--------|-------------|--------|-----------|
| 1 · Give Reachy a Voice | An expressive robot with a **cloud** voice | ▶️ **run & chat** | Cloud voice |
| 2 · Run Local | The same robot, now **100% offline on AMD** (and snappier!) | ▶️ **run & chat** (+ unplug the network!) | Local |
| 3 · Give Reachy Eyes | Reachy gets **eyes** — describes what it sees | ✋ **edit it yourself** | Local |

---

## How this station is set up

There are **two terminal windows** open:

- **Terminal A — the robot daemon.** It's already running and connected to Reachy.
  **Leave it alone** (don't close it).
- **Terminal B — your terminal.** You'll type commands here.

In **Terminal B** everything is ready: the Python environment is active and you're
in the project folder.

> **What's a `# >>> TRY ME <<<` block?** Throughout the lab, the *one* place you're
> meant to edit is a clearly-marked block near the top of a file that looks like
> `# >>> TRY ME <<<`. Everything else you just run — no code changes needed.

> Throughout the lab: press **Ctrl+C** to stop the current program and move on to
> the next one.

---

## Task 1 · Give Reachy a Voice — *cloud*  ▶️ *run & chat*

**Idea:** A rich emotion engine: continuous, synchronized motion (head + body +
antennas + eye blinks) that plays *while Reachy speaks*. The voice here comes from
**Microsoft Edge-TTS — a cloud service** (remember that for Task 2!).

**Run it:**

```bash
python lab/emo_v1.py --chat
```

**Then chat:** type a message like `hello` or `tell me a joke` and press **Enter** —
Reachy replies out loud and reacts. Notice how *alive* it feels — and that it has a
real **voice**. Because that voice is generated in the cloud, each reply makes a
quick round-trip over the network. Press **Ctrl+C** when ready.

**Takeaway:** Great voice, rich expression — but that voice needed the **cloud**.
What if the network is down, or you care about privacy (or speed)? → Task 2.

---

## Task 2 · Run Local — *100% offline on AMD*  ▶️ *run & chat (the fun one)*

**Idea:** The same expressive robot as Task 1, but the voice is now **Piper-TTS**,
running **locally**. Combined with the local LLM, **nothing leaves this machine.**

**Run it:**

```bash
python lab/emo_v2.py --chat
```

**Then chat:** type a message like `hello` or `tell me a joke` and press **Enter** —
Reachy replies out loud and reacts. Sounds great, still expressive. Two things to
notice:

> **⚡ Feel the speed:** no cloud round-trip for the voice means replies often come
> back **snappier** than Task 1 — the AMD chip synthesizes speech right here.

> **🔌 The party trick:** ask a staff member to **turn off Wi-Fi / unplug the
> network**, then chat with Reachy again. **It keeps thinking and talking** —
> because the LLM (Ollama) and the voice (Piper) both run on the AMD chip right
> in front of you.

> **💡 Optional — talk to Reachy with your voice.** Open `lab/emo_v2.py`, and in
> the `# >>> TRY ME <<<` block set `USE_VOICE_CHAT = True`, save, then run
> `python lab/emo_v2.py`. Now you speak instead of type — and the speech
> recognition (offline `faster-whisper`) also runs right here, so it's *still
> 100% local*. *(Optional — the run-and-chat flow above works fine without it.)*

Press **Ctrl+C** when ready.

**Takeaway:** A complete conversational robot — language, voice, expression —
running entirely on local AMD hardware, and faster for it. Now let's give it eyes.

---

## Task 3 · Give Reachy Eyes — *vision, still local*  ✋ *your turn*

**Idea:** Reachy looks through its **own camera**, sends the image to a **local
vision model** (a VLM running in Ollama on this AMD machine), describes what it
sees out loud, and reacts — still 100% offline.

**Run it:**

```bash
python lab/emo_v3.py
```

Hold an object in front of Reachy (your badge, a phone, your hand), then **press
Enter**. Reachy looks, then tells you what it sees.

> **💡 Want to see what Reachy sees?** Run it with the live browser view:
>
> ```bash
> python lab/emo_v3.py --preview-web
> ```
>
> Then open **http://localhost:8080** in a browser. You'll see the **live camera
> feed** plus a big **"Look & Describe"** button — click it and Reachy looks,
> describes what it sees, and reacts. (You can still press **Enter** in the
> terminal instead.) *(Optional — the plain `python lab/emo_v3.py` flow works fine
> without it.)*

### ✋ Now make it yours — change what Reachy says  *(the one required edit)*

**This is the hands-on part — the one edit everyone does.** You'll change **one
line** in the `# >>> TRY ME <<<` block and see Reachy's whole personality change.

1. Press **Ctrl+C** to stop it.
2. Open **`lab/emo_v3.py`** in the editor on screen (or run `nano lab/emo_v3.py`).
3. Near the top, find the block marked:

```text
# >>> TRY ME <<<  Mini-lab Task 3
```

4. Change the `VISION_PROMPT` line. Copy-paste one of these (or write your own!):

- `VISION_PROMPT = "Describe what you see like a pirate."`
- `VISION_PROMPT = "Guess my mood in one playful sentence."`
- `VISION_PROMPT = "Name every object you can see, then pick your favorite."`
- `VISION_PROMPT = "React like you're seeing this for the very first time."`

5. **Save** the file, then run it again and press Enter:

```bash
python lab/emo_v3.py
```

Try a couple of different prompts — it only takes a few seconds each time. Same
robot, same local AMD hardware, totally different behavior, all because you
changed one line.

> Not a coder? No problem — the edit is pure copy-paste, and staff are happy to
> help. The point is to *feel* how one line reshapes what the robot does.

**Takeaway:** Vision + language + voice + motion — a full *physical AI* loop,
all local on AMD, and now shaped by **you**.

---

## 🏁 You did it!

You chatted with a robot as it went from a cloud-voiced toy to one that **sees,
thinks, and speaks entirely on local AMD silicon** — then you reprogrammed how it
sees. That's the physical-AI stack in 10 minutes.

Want to go further? Ask the staff about:
- Editing the *other* tasks too (voices, personas — each file has its own `# >>> TRY ME <<<` block).
- Running a bigger LLM or a sharper vision model.
- Recording your own robot dance moves.

---

## Troubleshooting (flag a staff member if stuck)

| Symptom | Fix |
|---------|-----|
| Robot doesn't move | Make sure Terminal A (the daemon) is still running. |
| `Connection refused` / Ollama errors | Local LLM server isn't up: `ollama serve`. |
| No audio | Check the speaker volume (audio plays through Reachy's speaker). |
| Task 3: "Could not read camera" | Ask staff — the camera device may need selecting: `python lab/emo_v3.py --camera-device /dev/video0`. |
| Task 3: "Device or resource busy" | The daemon is holding the camera. Staff: restart it as `reachy-mini-daemon --no-media`. |
| Task 3: browser preview is blank | Give it a second to start; make sure you opened `http://localhost:8080` and the daemon was started with `--no-media`. |
| Edited a file and it broke | Undo your change (Ctrl+Z in the editor) and re-run. |
| Want to stop a program | Press **Ctrl+C** in Terminal B. |
