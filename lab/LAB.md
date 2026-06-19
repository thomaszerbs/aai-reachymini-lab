# Reachy Mini Mini-Lab — Build a Robot That Runs Entirely on AMD

Welcome! In the next **~12 minutes** you'll bring a little desktop robot to life —
and **change its behavior yourself** at every step. By the end, Reachy will think,
talk, *and see*, with **everything running locally on this AMD machine**. No cloud.

> This station is pre-configured. The robot and the AI models are ready to go.
> You just run a few commands and edit a couple of lines. Have fun with it!

**You'll do 4 quick stations:**

| Station | What you'll build | Runs where |
|--------|-------------------|-----------|
| 1 | A hand-coded emotion engine | Local |
| 2 | An expressive robot with a **cloud** voice | Cloud voice |
| 3 | The same robot, now **100% offline on AMD** | Local |
| 4 | Reachy gets **eyes** — it describes what it sees | Local |

---

## How this station is set up

There are **two terminal windows** open:

- **Terminal A — the robot daemon.** It's already running and connected to Reachy.
  **Leave it alone** (don't close it).
- **Terminal B — your terminal.** You'll type commands here.

In **Terminal B**, everything is ready: the Python environment is active and you're
in the project folder. Quick sanity check (optional):

```bash
# Is the local LLM server up?
curl -s http://localhost:11434/api/tags >/dev/null && echo "Ollama OK"
```

> Throughout the lab: press **Ctrl+C** to stop the current program and move on.
> To edit a file, open it in the editor on screen (or `nano lab/emo_v1.py`).

---

## Station 1 — Reachy's hand-coded brain  ⏱️ ~3 min

**Idea:** The simplest possible robot. Words are matched to emotions with plain
`if`-statements, and each emotion plays a hand-coded head/antenna motion.

**Run it:**

```bash
python lab/emo_v1.py --chat
```

Type a few things and watch Reachy react: try `I'm so happy!`, then `that's sad`,
then `let's dance`. (It also chats back using a local LLM.)

### 🛠️ TRY ME — change Reachy's brain

Stop it with **Ctrl+C**, open **`lab/emo_v1.py`**, and find the big

```text
# >>> TRY ME <<<  Mini-lab Station 1
```

block near the top. Change one thing, save, and re-run `python lab/emo_v1.py --chat`:

- Add a word to `HAPPY_WORDS` (e.g. `"pizza"`) → now "pizza" makes Reachy happy.
- Bump `NOD_AMPLITUDE_DEG` from `40` to `60` → bigger, more dramatic nods.
- Rewrite `ROBOT_PERSONA` → give Reachy a totally new attitude.

**Takeaway:** "Emotion" here is just keyword matching + motion presets. Simple,
but you can already *program a personality*.

---

## Station 2 — Expressive Reachy with a cloud voice  ⏱️ ~3 min

**Idea:** A richer engine: continuous, synchronized motion (head + body + antennas
+ eye blinks) that plays *while Reachy speaks*. The voice here comes from
**Microsoft Edge-TTS — a cloud service** (remember that for Station 3!).

**Run it:**

```bash
python lab/emo_v2.py --chat
```

Chat with it and notice how much more *alive* it feels than Station 1.

### 🛠️ TRY ME — give Reachy a new voice & personality

Ctrl+C, open **`lab/emo_v2.py`**, find the `# >>> TRY ME <<< Mini-lab Station 2` block:

- Change `DEFAULT_VOICE` to `en-US-AnaNeural` (child), `en-GB-RyanNeural` (British),
  or `en-US-GuyNeural` (deep).
- Rewrite `ROBOT_PERSONA` (e.g. *"You are a grumpy but lovable robot."*).

Re-run `python lab/emo_v2.py --chat` and hear the difference.

**Takeaway:** Great voice, rich expression — but the voice needed the **cloud**.
What if the network is down, or you care about privacy? → Station 3.

---

## Station 3 — Fully offline on AMD  ⏱️ ~2.5 min

**Idea:** Same expression engine as Station 2, but the voice is now **Piper-TTS**,
running **locally**. Combined with the local LLM, **nothing leaves this machine.**

**Run it:**

```bash
python lab/emo_v3.py --chat
```

### 🛠️ TRY ME — prove it's really offline

1. Open **`lab/emo_v3.py`**, find the `# >>> TRY ME <<< Mini-lab Station 3` block, and
   change `ROBOT_PERSONA` or swap `DEFAULT_PIPER_MODEL` to another voice in `models/`.
2. **The fun part:** ask the staff to unplug the network cable / turn off Wi-Fi,
   then run `python lab/emo_v3.py --chat` again. **Reachy keeps thinking and talking** —
   because the LLM (Ollama) and the voice (Piper) both run on the AMD chip.

**Takeaway:** A complete conversational robot — language, voice, expression —
running entirely on local AMD hardware.

---

## Station 4 — Give Reachy eyes  ⏱️ ~2.5 min  👀

**Idea:** Reachy looks through its **own camera**, sends the image to a **local
vision model** (a VLM running in Ollama on this AMD machine), describes what it
sees out loud, and reacts — still 100% offline.

**Run it:**

```bash
python lab/emo_v4.py
```

Hold an object in front of Reachy (your badge, a phone, your hand), then **press
Enter**. Reachy looks, then tells you what it sees.

### 🛠️ TRY ME — change what Reachy looks for

Ctrl+C, open **`lab/emo_v4.py`**, find `# >>> TRY ME <<< Mini-lab Station 4`,
and rewrite `VISION_PROMPT`. Some fun ones:

- `"Describe what you see like a pirate."`
- `"Guess my mood in one playful sentence."`
- `"Name every object you can see, then pick your favorite."`

Re-run and look again.

**Takeaway:** Vision + language + voice + motion — a full *physical AI* loop,
all local on AMD.

---

## 🏁 You did it!

You started with `if happy: nod` and ended with a robot that **sees, thinks, and
speaks entirely on local AMD silicon.** That's the physical-AI stack in 12 minutes.

Want to go further? Ask the staff about:
- Running a bigger LLM or a sharper vision model.
- Recording your own robot dance moves.
- Putting Reachy on real hardware vs. the simulator.

---

## Quick reference

| Station | Command | One-line edit |
|--------|---------|---------------|
| 1 | `python lab/emo_v1.py --chat` | trigger words / `NOD_AMPLITUDE_DEG` / persona |
| 2 | `python lab/emo_v2.py --chat` | `DEFAULT_VOICE` / persona |
| 3 | `python lab/emo_v3.py --chat` | persona / `DEFAULT_PIPER_MODEL` |
| 4 | `python lab/emo_v4.py` | `VISION_PROMPT` |

## Troubleshooting (flag a staff member if stuck)

| Symptom | Fix |
|---------|-----|
| Robot doesn't move | Make sure Terminal A (the daemon) is still running. |
| `Connection refused` / Ollama errors | Local LLM server isn't up: `ollama serve`. |
| No audio | Check the speaker volume / that headphones are plugged in. |
| Station 4: "Could not read camera" | Ask staff — the camera device may need selecting: `python lab/emo_v4.py --camera-device /dev/video2`. |
| Edited a file and it broke | Undo your change (Ctrl+Z in the editor) and re-run. |
| Want to stop a program | Press **Ctrl+C** in Terminal B. |
