# Reachy Mini — Interactive AI Robot

In the next **~10 minutes** you'll bring a desktop robot to life — from a robot
with a **cloud** voice, to one that thinks and talks **100% offline on this AMD
machine**, to one that **sees**. You only *have* to edit **one line**, in Task 3.
Everything's pre-configured and ready.

**Key:**  ▶️ **run & chat** = just run it and type to Reachy · ✋ **your turn** =
you edit one line · 💡 **Optional** = nice-to-try, skippable.

| Task | What happens | You... |
|------|--------------|--------|
| 1 · Give Reachy a Voice | Expressive robot with a **cloud** voice | ▶️ run & chat |
| 2 · Run Local | Same robot, now **100% offline on AMD** (and snappier!) | ▶️ run & chat + unplug the network! |
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
and reacts. Notice how *alive* it feels — but that voice took a round-trip to the
cloud. **Ctrl+C** when done.

> **Takeaway:** great voice, but it needed the cloud. What if the network's down,
> or you care about privacy or speed? → Task 2.

---

## Task 2 · Run Local — *100% offline on AMD*  ▶️

The same expressive robot, but the voice is now **Piper-TTS**, running **locally**.
With the local LLM, **nothing leaves this machine** — so let's prove it.

> **🔌 Switch off Wi-Fi first** (top-right menu → turn off Wi-Fi, or ask staff to
> unplug the network). *Then* run:

```bash
python lab/emo_v2.py --chat
```

Chat away — Reachy keeps thinking and talking with **no internet at all**, because
the LLM (Ollama) and the voice (Piper) both run right here on AMD. It's often
**snappier** too, with no cloud round-trip. **Ctrl+C** when done.

> **⚡ The contrast:** try running **Task 1** (`emo_v1.py`) with Wi-Fi still off —
> it *can't reply*, because its voice lives in the cloud. Same robot, but only the
> local one keeps working offline. (Turn Wi-Fi back on afterward if you retry Task 1.)

> **💡 Optional — talk with your voice.** Open [`emo_v2.py`](emo_v2.py), set
> `USE_VOICE_CHAT = True` in the `# >>> TRY ME <<<` block, save, and run
> `python lab/emo_v2.py`. Speech recognition (offline `faster-whisper`) also runs
> locally — still 100% offline.

> **Takeaway:** a full conversational robot — language, voice, expression — all on
> local AMD hardware. Now let's give it eyes.

---

## Task 3 · Give Reachy Eyes — *vision, still local*  ✋ *your turn*

Reachy looks through its **own camera**, sends the image to a **local vision
model** on this AMD machine, and describes what it sees — still 100% offline.

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
