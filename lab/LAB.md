# Reachy Mini — Interactive AI Robot

In the next **~10 minutes** you'll bring a desktop robot to life — from a robot
with a **cloud** voice, to one that thinks and talks **100% offline on this AMD
machine**, to one that **sees**. You only *have* to edit **one line**, in Task 3.
Everything's pre-configured and ready.

**Key:**  ▶️ **run & chat** = just run it and type to Reachy · 🎙️ **talk** = speak
to Reachy instead of typing · ✋ **your turn** = you edit one line.

| Task | What happens | You... |
|------|--------------|--------|
| 1 · Give Reachy a Voice | Expressive robot with a **cloud** voice | ▶️ run & chat |
| 2 · Run Local | Same robot, now **100% offline on AMD** (and snappier!) | ▶️ run & chat, unplug the network, then 🎙️ talk to it |
| 3 · Give Reachy Eyes | Reachy **sees** and describes the world | ✋ edit one line |

> **Everything happens right here in VS Code.** Two terminals are open:
> **Terminal A** runs the robot (leave it alone); **Terminal B** is yours — type
> the commands there. When a step says to edit a file, just click the link — it
> opens right here.

---

## Task 1 · Give Reachy a Voice — *cloud*  ▶️

A rich emotion engine — head, body, antennas, and eye-blinks all move *while
Reachy speaks*. The voice comes from **Microsoft Edge-TTS, a cloud service**
(remember that for Task 2!).

```bash
python lab/emo_v1.py --chat
```

Type something like `tell me a joke` and press **Enter**. Reachy replies out loud
and reacts — notice how *alive* it feels. But that voice took a round-trip to the
cloud. **Ctrl+C** when done.

> **Takeaway:** great voice — but it needed the cloud. What if the network's down?
> → Task 2.

---

## Task 2 · Run Local — *100% offline on AMD*  ▶️

Same expressive robot, but the voice is now **Piper-TTS**, running **locally** —
so with the local LLM, **nothing leaves this machine.** Let's prove it.

> **🔌 Switch off Wi-Fi first** (top-right menu → turn off Wi-Fi, or ask staff to
> unplug the network). *Then* run:

```bash
python lab/emo_v2.py --chat
```

Chat away — Reachy keeps thinking and talking with **no internet at all**, and
often **snappier** than Task 1 (no cloud round-trip). **Ctrl+C** when done.

> **⚡ The contrast:** run **Task 1** (`emo_v1.py`) with Wi-Fi still off — it
> *can't reply*, because its voice lives in the cloud. Same robot; only the local
> one survives offline. (Turn Wi-Fi back on if you retry Task 1.)

### 🎙️ Now talk to Reachy with your voice

Even better — *talk* instead of typing. The speech recognition runs offline here
too, so it's still fully local.

1. Open [`emo_v2.py`](emo_v2.py) (click the link, or **Ctrl+P** → `emo_v2.py`).
2. Find the `# >>> TRY ME <<<` block near the top (**Ctrl+F** → `TRY ME`) and set:

```python
USE_VOICE_CHAT = True
```

3. **Save (Ctrl+S)**, then run it and just **speak** — no typing:

```bash
python lab/emo_v2.py
```

You're now having a spoken conversation with a robot whose ears, brain, and voice
all run right here. **Ctrl+C** when done.

> **Takeaway:** a complete conversational robot — hearing, language, voice, motion
> — all on local AMD. Now let's give it eyes.

---

## Task 3 · Give Reachy Eyes — *vision, still local*  ✋ *your turn*

Reachy looks through its **own camera**, sends the image to a **local vision
model** on this AMD machine, and describes what it sees.

```bash
python lab/emo_v3.py --preview-web
```

Open **http://localhost:8080** to see the **live feed** plus a **"Look &
Describe"** button. Hold up an object (badge, phone, your hand) and **click the
button**. Reachy looks, describes it, and reacts.

> **Tip:** to keep it in VS Code, open the built-in browser —
> **Ctrl+Shift+P → "Simple Browser: Show"** → `http://localhost:8080`.
> (Or just use any browser. No browser? Run `python lab/emo_v3.py` and press
> **Enter** in the terminal to look.)

### ✋ Now make it yours — the one edit everyone does

You'll change **one line** and watch Reachy's whole personality shift.

1. **Ctrl+C** in Terminal B to stop it.
2. Open [`emo_v3.py`](emo_v3.py) (click the link, or **Ctrl+P** → `emo_v3.py`).
3. Find the `# >>> TRY ME <<<` block near the top (**Ctrl+F** → `TRY ME`).
4. Change the `VISION_PROMPT` line — copy one of these or write your own:

- `VISION_PROMPT = "Describe what you see like a pirate."`
- `VISION_PROMPT = "Guess my mood in one playful sentence."`
- `VISION_PROMPT = "Name every object you can see, then pick your favorite."`
- `VISION_PROMPT = "React like you're seeing this for the very first time."`

5. **Save (Ctrl+S)**, then run it again and click **"Look & Describe"**:

```bash
python lab/emo_v3.py --preview-web
```

Try a couple of prompts — a few seconds each. Same robot, same local AMD
hardware, totally different behavior, all from **one line you changed**.

> Not a coder? It's pure copy-paste, and staff are happy to help.

> **Takeaway:** vision + language + voice + motion — a full *physical AI* loop,
> all local on AMD, now shaped by **you**.

---

## 🏁 You did it!

You took a robot from a cloud-voiced toy to one that **sees, thinks, and speaks
entirely on local AMD silicon** — then reprogrammed how it sees. That's the
physical-AI stack in 10 minutes. Ask staff about editing the other tasks, running
a bigger model, or recording your own robot dance moves.

---

## Something not working?

**Flag a staff member** — they'll get you going. Common fixes live in
**[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**.

> Quick ones: **Ctrl+C** in Terminal B stops the current program. Edited a file
> and it broke? **Ctrl+Z** to undo, then re-run.
