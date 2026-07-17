# Reachy Mini: Interactive AI Robot

In the next **~10 minutes** you'll bring a desktop robot to life: from a robot
with a **cloud** voice, to one that thinks and talks **100% offline on this AMD
machine**, to one that **sees** — and you'll shape its personality just by
telling it what to do. No coding, no terminals.

> **Running locally on AMD:** a chat LLM (`qwen3.5:0.8b`), a vision-language
> model (`qwen2.5vl:3b`), a neural voice (Piper), and speech recognition
> (`faster-whisper`). All via open models — no cloud (except Task 1's voice).

---

## ▶️ Start here

**Double-click the “Reachy Mini Lab” icon on the desktop.**
(No icon? Open a terminal and run `./run-lab.sh`.)

A simple menu appears. Type a number, press **Enter**, and you're off. That's it —
the launcher wakes up the robot and starts everything for you.

```
  1  🗣️   Give Reachy a voice        (cloud voice, type to chat)
  2  💻  Run it 100% offline on AMD (local AI, type to chat)
  3  🎙️   Talk to Reachy            (offline, speak instead of typing)
  4  👀  Give Reachy eyes           (sees & describes, in the browser)

  m  🎤  Choose / test the microphone
  q  👋  Quit
```

> **To stop a task and return to the menu:** press **Ctrl+C**.

---

## The four things to try

### 1 · 🗣️ Give Reachy a Voice — *cloud*

Reachy moves *while it speaks* (head, antennas, eye-blinks), with a voice from a
**cloud** service. Type something like `tell me a joke` and press **Enter**.
Reachy replies out loud and reacts. Great voice — but it took a round-trip to the
cloud. (Remember that for the next one!)

### 2 · 💻 Run it 100% offline on AMD

Same expressive robot, but now the brain **and** the voice run **right here on
this machine** — nothing leaves it.

First, the launcher asks you to **give Reachy a personality**:

> `talk like an excited puppy` · `be a grumpy pirate` · `sound like a wise robot`

Type one (or press **Enter** to keep the default), then chat away. It's often
**snappier** than Task 1 — no cloud round-trip.

> **🔌 Want proof it's local?** You could switch off Wi-Fi and keep chatting;
> Reachy won't miss a beat. Task 1's voice, by contrast, would go quiet.

### 3 · 🎙️ Talk to Reachy — *offline*

Same offline robot, but now **speak** instead of typing — the speech recognition
runs locally too. Give it a personality (or keep the default), then just talk.

> **Mic not picking you up?** Back at the menu, press **`m`** to see the
> microphones, then a staff member can point it at the right one.

### 4 · 👀 Give Reachy Eyes — *vision, still local*

Reachy looks through its **own camera**, sends the image to a **local vision
model**, and describes what it sees.

First, the launcher asks **how Reachy should describe what it sees**:

> `describe it like a pirate` · `guess my mood` · `name every object you see`

Type one (or press **Enter** for the default). A browser window opens with the
**live camera feed** and a big **“Look & Describe”** button. Hold up an object
(badge, phone, your hand) and **click the button** — Reachy looks, freezes on
what it saw, describes it, and reacts.

Try a couple of different instructions. Same robot, same local AMD hardware,
totally different behavior — all from **what you told it**.

---

## 🏁 You did it!

You took a robot from a cloud-voiced toy to one that **sees, thinks, and speaks
entirely on local AMD silicon**, and gave it a personality of your own — no code
required. That's the physical-AI stack in 10 minutes. Ask staff about running a
bigger model or recording your own robot dance moves.

---

## Something not working?

**Flag a staff member** and they'll get you going. Common fixes live in
**[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**.

> Quick one: press **Ctrl+C** to stop the current task and return to the menu.
