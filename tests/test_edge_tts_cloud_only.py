import asyncio
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))

import emo_v1


def test_sync_edge_tts_failure_does_not_use_local_voice():
    engine = emo_v1.EdgeTTSEngine(default_voice="en-US-JennyNeural")
    engine.debug = False
    fallback_calls = []

    def fail(coroutine):
        coroutine.close()
        raise RuntimeError("cloud unavailable")

    with mock.patch.object(engine, "_run_coro_blocking", fail):
        with mock.patch.object(
            engine,
            "_fallback_tts",
            lambda *args: fallback_calls.append(args),
            create=True,
        ):
            engine.speak_with_emotion("hello there", "neutral")

    assert fallback_calls == []


def test_async_edge_tts_failure_does_not_use_local_voice():
    engine = emo_v1.EdgeTTSEngine(default_voice="en-US-JennyNeural")
    engine.debug = False
    fallback_calls = []

    async def fail(*args, **kwargs):
        raise RuntimeError("cloud unavailable")

    with mock.patch.object(engine, "_speak_async", fail):
        with mock.patch.object(
            engine,
            "_fallback_tts",
            lambda *args: fallback_calls.append(args),
            create=True,
        ):
            asyncio.run(engine.speak_with_emotion_async("hello there", "neutral"))

    assert fallback_calls == []