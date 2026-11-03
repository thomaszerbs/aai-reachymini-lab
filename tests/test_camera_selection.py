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


if __name__ == "__main__":
    test_find_camera_device_prefers_non_laptop_camera()
    print("camera selection regression test passed")
