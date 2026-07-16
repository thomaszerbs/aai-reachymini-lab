# Reachy Mini: Interactive AI Robot

In the next **~10 minutes** you'll bring a desktop robot to life: from a robot
with a **cloud** voice, to one that thinks and talks **100% offline on this AMD
machine**, to one that **sees**. You'll edit just **one line** in Tasks 2 and 3.
Everything else is pre-configured and ready.

> **Running locally on AMD:** a chat LLM (`qwen3.5:0.8b`), a VLM / vision-language
> model (`qwen2.5vl:3b`), a neural voice (Piper), and speech recognition
> (`faster-whisper`). All via Ollama + open models, no cloud (except Task 1's voice).

**Key:**  ▶️ **run & chat** = just run it and type to Reachy · 🎙️ **talk** = speak
to Reachy instead of typing · ✋ **your turn** = you edit one line.

| Task | What happens | You... |
|------|--------------|--------|
| 1 · Give Reachy a Voice | Expressive robot with a **cloud** voice | ▶️ run & chat |
| 2 · Run Local | Same robot, now **100% offline on AMD** (and snappier!) | ▶️ run & chat · ✋ edit one line to 🎙️ talk |
| 3 · Give Reachy Eyes | Reachy **sees** and describes the world | ✋ edit one line |

> **Everything happens right here in VS Code.** Two terminals are open:
> **Terminal A** runs the robot (leave it alone); **Terminal B** is yours, where
> you type the commands. When a step says to edit a file, just click the link and
> it opens right here.

---

## Task 1 · Give Reachy a Voice · *cloud*  ▶️

Reachy moves *while it speaks* (head, antennas, eye-blinks), with a voice from
**Microsoft Edge-TTS, a cloud service** (remember that for Task 2!).

```bash
python lab/emo_v1.py --chat
```

Type something like `tell me a joke` and press **Enter**. Reachy replies out loud
and reacts. Great voice, but it took a round-trip to the **cloud**. **Ctrl+C** when
done.

---

## Task 2 · Run Local · *100% offline on AMD*  ▶️

Same expressive robot, but the voice is now **Piper-TTS**, running **locally**.
With the local LLM, **nothing leaves this machine.**

```bash
python lab/emo_v2.py --chat
```

Chat away. This time everything (the LLM and the voice) runs right here on AMD,
and it's often **snappier** than Task 1 (no cloud round-trip). **Ctrl+C** when done.

> **🔌 Want proof it's local?** You could even switch off Wi-Fi (top-right menu)
> and keep chatting; Reachy won't miss a beat. Task 1, by contrast, would go
> quiet: its voice lives in the cloud.

### ✋ Now make it talk: edit one line for voice

Even better: *talk* instead of typing (the speech recognition is offline too).

1. **Ctrl+C** in Terminal B to stop it.
2. Open [`emo_v2.py`](emo_v2.py) (click the link, or **Ctrl+P** → `emo_v2.py`).
3. Find the `# >>> TRY ME <<<` block near the top (**Ctrl+F** → `TRY ME`).
4. Change the `USE_VOICE_CHAT` line to:

```python
USE_VOICE_CHAT = True
```

5. **Save (Ctrl+S)**, then run it again and just **speak** (no typing):

```bash
python lab/emo_v2.py
```

Now its ears, brain, and voice all run right here. **Ctrl+C** when done. Next,
let's give it eyes.

---

## Task 3 · Give Reachy Eyes · *vision, still local*  ✋ *your turn*

Reachy looks through its **own camera**, sends the image to a **local vision
model** on this AMD machine, and describes what it sees.

```bash
python lab/emo_v3.py --preview-web
```

Open **http://localhost:8080** to see the **live feed** plus a **"Look &
Describe"** button. Hold up an object (badge, phone, your hand) and **click the
button**. Reachy looks, describes it, and reacts.

> **Tip:** to keep it in VS Code, open the built-in browser:
> **Ctrl+Shift+P → "Simple Browser: Show"** → `http://localhost:8080`.
> (Or just use any browser. No browser? Run `python lab/emo_v3.py` and press
> **Enter** in the terminal to look.)

### ✋ Now make it yours: the one edit everyone does

Change **one line** and watch Reachy's whole personality shift:

1. **Ctrl+C** in Terminal B to stop it.
2. Open [`emo_v3.py`](emo_v3.py) (click the link, or **Ctrl+P** → `emo_v3.py`).
3. Find the `# >>> TRY ME <<<` block near the top (**Ctrl+F** → `TRY ME`).
4. Change the `VISION_PROMPT` line. Copy one of these or write your own:

- `VISION_PROMPT = "Describe what you see like a pirate."`
- `VISION_PROMPT = "Guess my mood in one playful sentence."`
- `VISION_PROMPT = "Name every object you can see, then pick your favorite."`
- `VISION_PROMPT = "React like you're seeing this for the very first time."`

5. **Save (Ctrl+S)**, then run it again and click **"Look & Describe"**:

```bash
python lab/emo_v3.py --preview-web
```

Try a couple; a few seconds each. Same robot, same local AMD hardware, totally
different behavior, all from **one line you changed**. (Not a coder? It's pure
copy-paste, and staff are happy to help.)

---

## 🏁 You did it!

You took a robot from a cloud-voiced toy to one that **sees, thinks, and speaks
entirely on local AMD silicon**, then reprogrammed how it sees. That's the
physical-AI stack in 10 minutes. Ask staff about editing the other tasks, running
a bigger model, or recording your own robot dance moves.
