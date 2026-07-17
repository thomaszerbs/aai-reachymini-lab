# Reachy Mini: Interactive AI Robot

In ~10 minutes you'll take a desktop robot from a **cloud** voice → **100%
offline on this AMD machine** → one that **sees**. You spend your time *running*
and *tweaking*, not reading.

> **Running locally on AMD:** chat LLM (`qwen3.5:0.8b`), vision model
> (`qwen2.5vl:3b`), neural voice (Piper), speech recognition (`faster-whisper`).
> All local via Ollama — no cloud (except Task 1's voice, on purpose).

**You run everything in one notebook: [`lab/lab.ipynb`](lab.ipynb).** Open it,
pick the **venv kernel**, and run the **Setup** cell first (it connects to the
robot). Then, for each task:

1. *(Optional)* edit the `# >>> TRY ME <<<` config cell, then **run it**.
2. **Tasks 1–2:** type a message in the **chat bar** and hit **Send** — Reachy
   replies out loud and reacts.
3. **Task 3:** run the **action cell** for a **live feed**, then **type a
   question** (or click a suggestion) — Reachy answers about what it sees.

> **Fresh visitor?** Follow the **"Want a fresh start?"** section (right after
> Setup): run `./reset.sh`, reload the notebook from disk, and re-run Setup, so
> you don't inherit the previous persona/voice/style.

| Task | What it is | You do |
|------|-----------|--------|
| 1 · Voice | Expressive robot, **cloud** voice | edit persona/voice → run → **type in the chat bar** |
| 2 · Local | Same robot, **100% offline on AMD** | edit persona → run → **type in the chat bar** |
| 3 · Eyes | Reachy **sees** and answers your questions | run the action cell → **type a question in the bar** |

---

## Task 1 · Give Reachy a Voice · *cloud*

Reachy moves *while it speaks*, with a voice from **Microsoft Edge-TTS (a cloud
service)** — remember that for Task 2.

**Edit → run → chat:** in the `# >>> TRY ME <<<` cell change `PERSONA_1` or
`VOICE_1`, run it, then type `tell me a joke` in the chat bar and hit **Send**.

A few voices to try: `en-US-AnaNeural` (child), `en-GB-RyanNeural` (British),
`en-US-GuyNeural` (deep).

---

## Task 2 · Run Local · *100% offline on AMD*

Same expressive robot, but the LLM **and** the voice (Piper-TTS) now run **right
here** — nothing leaves this machine. Often **snappier** than Task 1 (no cloud
round-trip).

**Edit → run → chat:** change `PERSONA_2` (or swap `PIPER_MODEL`) in the
`# >>> TRY ME <<<` cell, run it, then chat away in the bar.

> **🔌 Proof it's local:** turn off Wi-Fi (top-right menu) and keep chatting.
> Reachy won't miss a beat. Task 1 would go quiet — its voice lives in the cloud.

---

## Task 3 · Give Reachy Eyes · *vision, still local*

Reachy looks through its **own camera** (a **live feed** appears), and when you
**type a question** it sends the current frame to a **local vision model** on
this AMD machine and answers out loud.

**Run the action cell**, then hold up an object (badge, phone, your hand) and
**type a question in the bar** (press Enter), or click a suggestion chip:
**What do you see?**, **What do I look like?**, or **Describe where I am?**.
Reachy freezes on that frame, answers, and reacts.

**The one edit everyone does:** change `VISION_STYLE` in the `# >>> TRY ME <<<`
cell to steer Reachy's tone for every answer. Copy one of these or write your own:

- `VISION_STYLE = "Answer like a pirate."`
- `VISION_STYLE = "Answer like an excited scientist."`
- `VISION_STYLE = "Answer in a calm, poetic voice."`

Same robot, same local AMD hardware, totally different vibe, all from **one line
you changed** (plus whatever you ask). (Not a coder? It's pure copy-paste, and
staff are happy to help.)

---

## 🏁 You did it!

You took a robot from a cloud-voiced toy to one that **sees, thinks, and speaks
entirely on local AMD silicon**, then reprogrammed how it sees — the physical-AI
stack in 10 minutes. When you're done, run the **Shutdown** cell. Ask staff about
editing the other tasks, running a bigger model, or recording your own robot
dance moves.

---

## Fallback: terminal scripts

If Jupyter/the notebook has trouble, the same three tasks run as terminal
scripts (each has the same `# >>> TRY ME <<<` block). Ask staff — the loop is
**edit the block + save**, then **Ctrl+C** to stop and re-run the command:

```bash
python lab/emo_v1.py --chat      # Task 1 (cloud voice); edit PERSONA/VOICE + re-run
python lab/emo_v2.py --chat      # Task 2 (100% offline); edit PERSONA + re-run
python lab/emo_v3.py --preview-web   # Task 3 (vision); open http://localhost:8080,
                                     # edit VISION_PROMPT + re-run, click "Look & Describe"
```

> Note: the notebook's Task 3 uses a **question bar** (type what you want to
> know); the fallback `emo_v3.py` script instead uses **Enter / "Look &
> Describe"** with a `VISION_PROMPT` describe-prompt.

Coders can skip the edit and pass a flag instead: `--persona`/`--voice`
(emo_v1), `--persona` (emo_v2), `--prompt` (emo_v3).
