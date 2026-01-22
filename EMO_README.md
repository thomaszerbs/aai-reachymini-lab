# EMO README — Reachy Mini Emotion Versions (Merged)

This document consolidates per-version summaries and a full version-comparison table for `emo_v1.py` → `emo_v5.py`.

---

## emo_v1 — High-Intensity Emotion Engine

Summary
- Purpose: Baseline high-intensity emotion controller and interactive chat app.
- Key features: high-intensity defaults, large-amplitude motion mappings, simple keyword-based emotion classification, quick test harness.

Code snapshot
```python
# emo_v1: basic analysis
text_lower = text.lower()
if any(w in text_lower for w in ["跳舞", "舞蹈"]):
    emotion = "activity"
controller.perform_high_amplitude_action(emotion)
```

---

## emo_v2 — Recorded Moves Integration

Summary
- Purpose: Use `RecordedMoves` for a richer motion vocabulary and categorize moves by emotion.

Code snapshot
```python
# emo_v2 categorize recorded moves
all_moves = self.recorded_moves.list_moves()
for move_name in all_moves:
    move = self.recorded_moves.get(move_name)
    desc = move.description.lower() if move.description else ""
    # assign best_match
```

---

## emo_v3 — Parallel Actions During Streaming

Summary
- Purpose: Trigger actions early while Ollama streams the response for better responsiveness.

Code snapshot
```python
# emo_v3 pseudo
for line in response.iter_lines():
    if 'response' in chunk:
        if should_trigger_now(partial):
            start_background_move()
```

---

## emo_v4 — Reliable Offline TTS (espeak) + Lip-sync

Summary
- Purpose: Add deterministic offline TTS using `espeak` and add lip-sync (antenna/eye animation).

Code snapshot (espeak synth)
```python
cmd = ['espeak', '--stdout', text]
result = subprocess.run(cmd, capture_output=True, check=True)
with open(output_file, 'wb') as f:
    f.write(result.stdout)
```

---

## emo_v5 — High-Quality Edge-TTS with Correct Playback

Summary
- Purpose: Use Edge-TTS to create higher-quality, multilingual speech. Save to WAV, read with `soundfile` and play using `sounddevice` at the file's sample rate to avoid noise.

Code snapshot
```python
# emo_v5
await edge_tts.Communicate(text, voice).save(tmp_path)
data, sr = sf.read(tmp_path, dtype='float32')
sd.play(data, samplerate=sr)
sd.wait()
```

---

## Full Version Comparison Table

| Feature | emo_v1 | emo_v2 | emo_v3 | emo_v4 | emo_v5 |
|---|---:|---:|---:|---:|---:|
| Action Source | custom | recorded moves | recorded moves | recorded moves | recorded moves |
| Emotion Types | 4 basic | 4 enhanced | 4 enhanced | 4 enhanced | 4 enhanced |
| Action Timing | after text | after text | during text | during speech | during speech |
| TTS Engine | none | none | none | multi-backend (local) | Edge-TTS (cloud)
| Lip-sync | no | no | no | generic | antenna/eye precise
| Voice Quality | N/A | N/A | N/A | local | neural cloud
| Threading | no | no | yes | yes | yes
| Emoji Support | no | yes | yes | yes | yes

---

## Migration & CLI notes
- Use `controller.execute_emotion_move()` to move from v1→v2 style.
- `emo_v3` introduces streaming hooks; prefer `_get_ollama_response_parallel`.
- `emo_v4` and `emo_v5` add TTS: use `--test-tts` to validate.

---

## Tests
- `python test_actions.py` now validates both dances and emotions recorded-move libraries (limited to a small set by default).
- `python emo_v4.py --test-tts` validates local `espeak` integration.
- `python emo_v5.py --test-tts` validates Edge-TTS (requires network).

---

If you'd like I can:
- Replace the original `EMO_README.md` with this merged file (overwrite), and
- Delete `VERSION_COMPARISON.md` (cleanup).

Tell me whether you want me to overwrite the existing `EMO_README.md` and remove `VERSION_COMPARISON.md` now.
