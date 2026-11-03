import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))

fake_emo_v2 = types.ModuleType("emo_v2")
fake_emo_v2.EmotionControllerV71 = object
sys.modules.setdefault("emo_v2", fake_emo_v2)

import emo_v3


def test_external_preview_uses_webpreview_backend():
    import _labkit

    class FakeWebPreview:
        def __init__(self, device, max_width=320, fps=2, quality=8, port=8080):
            self.device = device
            self.max_width = max_width
            self.fps = fps
            self.quality = quality
            self.port = port
            self.error = None

        def start(self, timeout=8.0):
            self.error = None

    seen = {}

    def fake_start(device, fps=2, quality=8):
        seen["device"] = device
        seen["fps"] = fps
        seen["quality"] = quality
        return FakeWebPreview(device, max_width=320, fps=fps, quality=quality, port=8080)

    old = _labkit._start_external_preview
    try:
        _labkit._start_external_preview = fake_start
        reader = _labkit._start_external_preview("/dev/video0", fps=2, quality=8)
        assert reader.device == "/dev/video0"
        assert reader.fps == 2
        assert reader.port == 8080
        assert seen["device"] == "/dev/video0"
    finally:
        _labkit._start_external_preview = old

    assert _labkit.ask_live.__defaults__[-1] is True


def _make_fake_sysfs(root, devices):
    sysfs_root = root / "sys" / "class" / "video4linux"
    sysfs_root.mkdir(parents=True, exist_ok=True)
    for idx, name in devices:
        dev_dir = sysfs_root / f"video{idx}"
        dev_dir.mkdir(parents=True, exist_ok=True)
        (dev_dir / "name").write_text(name)
    return sysfs_root


def test_find_camera_device_prefers_non_laptop_camera():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sysfs_root = _make_fake_sysfs(
            root,
            [
                (0, "Integrated Camera"),
                (2, "USB Camera"),
            ],
        )

        old_glob = emo_v3.glob.glob
        emo_v3.glob.glob = lambda pattern: [str(p) for p in sorted(sysfs_root.iterdir())]
        try:
            assert emo_v3.find_camera_device("Arducam") == "/dev/video2"
        finally:
            emo_v3.glob.glob = old_glob


def test_find_camera_device_rejects_preview_stream_and_prefers_reachy_sensor():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sysfs_root = _make_fake_sysfs(
            root,
            [
                (0, "Reachy Mini Camera: Reachy Mini"),
                (1, "Reachy Mini Camera: Reachy Mini"),
                (2, "Preview"),
            ],
        )

        old_glob = emo_v3.glob.glob
        emo_v3.glob.glob = lambda pattern: [str(p) for p in sorted(sysfs_root.iterdir())]
        try:
            assert emo_v3.find_camera_device() == "/dev/video0"
        finally:
            emo_v3.glob.glob = old_glob


if __name__ == "__main__":
    test_find_camera_device_prefers_non_laptop_camera()
    test_find_camera_device_rejects_preview_stream_and_prefers_reachy_sensor()
    print("camera selection regression test passed")
