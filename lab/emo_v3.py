#!/usr/bin/env python3
"""emo_v3.py - Reachy Mini "sees" with a local vision model (Offline)

Mini-lab Task 3. Reachy looks through its own camera, sends the frame to a
local vision model (Ollama VLM), describes what it sees, and reacts with the
same offline Piper-TTS voice + emotion motions used in Task 2 (emo_v2).

Everything runs locally on the AMD machine: vision (Ollama VLM), voice (Piper),
and motion (Reachy Mini SDK). No cloud, no internet.

Camera note: we read the robot's camera directly from its V4L2 device (via
ffmpeg) rather than through the SDK media server. On the booth machines the
daemon's WebRTC media server is unavailable (missing GStreamer webrtc plugin),
and direct V4L2 capture is simpler and more reliable. Motion still goes through
the daemon (media_backend="no_media").

Usage:
  python lab/emo_v3.py                        # push-to-look: press Enter, Reachy describes the scene
  python lab/emo_v3.py --gentle               # subtler motions for nearby humans
  python lab/emo_v3.py --camera-device /dev/video2
  python lab/emo_v3.py --save-frame look.jpg  # also save what the camera saw (debugging)
  python lab/emo_v3.py --preview             # show a live window of what Reachy sees (needs a display)
"""

import os
import sys
import time
import json
import glob
import base64
import asyncio
import logging
import argparse
import threading
import subprocess

# Add this file's dir (for sibling emo_v*.py) and the repo root (for `utils/`),
# so the script works when run as `python lab/emo_v3.py` from the repo root.
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_here)
sys.path.append(os.path.dirname(_here))

# Reuse the offline engine from Task 2 (Piper-TTS + emotion controller).
from emo_v2 import EmotionControllerV71

# Silence the Reachy SDK's intentionally-unused media subsystem (see note in
# emo_v1.py). Repeated here so the suppression still applies when this script is
# run directly. Idempotent and harmless; runs before the robot connects.
logging.getLogger("reachy_mini.media").setLevel(logging.ERROR)


# ============================================================================
# >>> TRY ME <<<  Mini-lab Task 3
# Change what Reachy looks for, then re-run `python lab/emo_v3.py`.
# All of this runs on a *local* vision model on the AMD machine.
# ============================================================================

# 1) What you ask the vision model every time it looks. Make it your own!
#    Try: "Describe what you see like a pirate."
#         "Guess the mood of the person you see in one playful sentence."
#         "Name every object you can see, then pick your favorite."
VISION_PROMPT = (
    "You are a curious desktop robot looking through your own camera. "
    "In one or two short, upbeat sentences, describe what you see right now."
)

# 2) The local vision model (must be pulled in Ollama: `ollama pull <name>`).
VLM_MODEL = "qwen2.5vl:3b"

# 3) The offline Piper voice (same models/ folder as Task 2).
DEFAULT_PIPER_MODEL = "models/en-us-blizzard_lessac-medium.onnx"
# ============================================================================

# Reachy Mini's camera shows up as an "Arducam" V4L2 device. We auto-detect it
# by name; override with --camera-device if needed.
CAMERA_NAME_HINT = "Arducam"


def check_runtime_dependencies(require_reachy: bool = True) -> bool:
    """Check optional runtime dependencies and print actionable hints."""
    missing = []
    try:
        import requests  # noqa: F401
    except Exception:
        missing.append(("requests", "pip install -r requirements.txt"))

    # ffmpeg is used for camera capture
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
    except Exception:
        missing.append(("ffmpeg", "sudo apt install -y ffmpeg"))

    if require_reachy:
        try:
            import reachy_mini  # noqa: F401
        except Exception:
            missing.append(("reachy-mini", "pip install 'reachy-mini[mujoco]'"))

    if missing:
        print("❌ Missing runtime dependencies:")
        for mod, hint in missing:
            print(f"   - {mod}  ->  {hint}")
        return False
    return True


def find_camera_device(name_hint: str = CAMERA_NAME_HINT) -> str:
    """Find the robot camera's V4L2 device path by matching its name.

    Falls back to the lowest-numbered /dev/video* if no name matches.
    """
    devices = []
    for path in glob.glob("/sys/class/video4linux/video*"):
        base = os.path.basename(path)  # e.g. "video2"
        try:
            idx = int(base.replace("video", ""))
        except ValueError:
            continue
        try:
            with open(os.path.join(path, "name")) as f:
                name = f.read().strip()
        except Exception:
            name = ""
        devices.append((idx, f"/dev/{base}", name))

    devices.sort()
    for _, dev, name in devices:
        if name_hint.lower() in name.lower():
            return dev
    if devices:
        return devices[0][1]
    return "/dev/video0"


def capture_jpeg(device: str, max_width: int = 1024, quality: int = 4, timeout: int = 15) -> bytes:
    """Grab a single JPEG frame from a V4L2 device using ffmpeg.

    Returns the raw JPEG bytes. Raises RuntimeError on failure.
    """
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-f", "v4l2", "-i", device,
        "-frames:v", "1",
        "-vf", f"scale='min({max_width},iw)':-2",
        "-q:v", str(quality),
        "-f", "image2", "-c:v", "mjpeg", "pipe:1",
    ]
    proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
    if proc.returncode != 0 or not proc.stdout:
        err = proc.stderr.decode(errors="ignore").strip()
        raise RuntimeError(err[:300] or "ffmpeg produced no frame")
    return proc.stdout


class CameraPreview:
    """Single-owner OpenCV VideoCapture preview thread for Task 3 (--preview).

    The Arducam is a single V4L2 device with exactly one owner at a time. When
    the live preview is on, THIS thread owns the camera for the whole session,
    and the VLM's still frame is pulled from this same stream (never a separate
    ffmpeg grab) so the two never collide with "Device or resource busy".

    All OpenCV GUI calls (imshow/waitKey/namedWindow/destroyAllWindows) live on
    this one thread; cv2 is imported lazily by the caller before constructing.
    """

    def __init__(
        self,
        device: str,
        width: int = 1280,
        height: int = 720,
        window_title: str = "Reachy sees (Task 3)",
        debug: bool = False,
    ):
        import cv2  # lazy: caller guards ImportError before we get here

        self._cv2 = cv2
        self.device = device
        self.width = width
        self.height = height
        self.window_title = window_title
        self.debug = debug

        self._latest = None            # most recent BGR frame (numpy array)
        self._lock = threading.Lock()  # guards _latest
        self._stop = threading.Event()
        self._ready = threading.Event()  # set once we have a frame or an error
        self._error: str = None
        self._thread: threading.Thread = None

    @property
    def error(self) -> str:
        return self._error

    @property
    def stopped(self) -> bool:
        """True if the user closed the window / pressed ESC in the preview."""
        return self._stop.is_set()

    @staticmethod
    def _device_to_index(device: str) -> int:
        """Convert "/dev/video2" (or "2") to the integer OpenCV index (2)."""
        base = os.path.basename(str(device))
        digits = "".join(ch for ch in base if ch.isdigit())
        return int(digits) if digits else 0

    def start(self, timeout: float = 6.0) -> None:
        """Start the preview thread and block until the first frame or error."""
        self._thread = threading.Thread(
            target=self._run, name="reachy-preview", daemon=True
        )
        self._thread.start()
        if not self._ready.wait(timeout=timeout):
            self._error = self._error or "timed out waiting for the first frame"

    def _run(self) -> None:
        cv2 = self._cv2
        idx = self._device_to_index(self.device)

        cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
        if not cap.isOpened():
            # Fall back to opening the raw device path via the V4L2 backend.
            cap = cv2.VideoCapture(self.device, cv2.CAP_V4L2)
        if not cap.isOpened():
            self._error = f"could not open camera {self.device}"
            self._ready.set()
            return

        # Keep the preview light on the AMD box.
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        try:
            cv2.namedWindow(self.window_title, cv2.WINDOW_NORMAL)
        except Exception as e:
            self._error = f"cannot open preview window ({e})"
            self._ready.set()
            cap.release()
            return

        try:
            while not self._stop.is_set():
                ok, frame = cap.read()
                if not ok or frame is None:
                    time.sleep(0.01)
                    continue

                with self._lock:
                    self._latest = frame
                if not self._ready.is_set():
                    self._ready.set()

                try:
                    cv2.imshow(self.window_title, frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC quits the preview
                        self._stop.set()
                        break
                    # Detect the window being closed by the user.
                    if cv2.getWindowProperty(self.window_title, cv2.WND_PROP_VISIBLE) < 1:
                        self._stop.set()
                        break
                except Exception as e:
                    self._error = f"preview display failed ({e})"
                    self._ready.set()
                    break
        finally:
            cap.release()
            try:
                cv2.destroyAllWindows()
                cv2.waitKey(1)  # let the window manager actually close the window
            except Exception:
                pass

    def encode_latest_jpeg(self) -> bytes:
        """Return the most recent preview frame as JPEG bytes (for the VLM)."""
        cv2 = self._cv2
        with self._lock:
            frame = None if self._latest is None else self._latest.copy()
        if frame is None:
            raise RuntimeError("no preview frame available yet")
        ok, buf = cv2.imencode(".jpg", frame)
        if not ok:
            raise RuntimeError("failed to encode preview frame")
        return buf.tobytes()

    def stop(self, join_timeout: float = 2.0) -> None:
        """Signal the thread to stop and wait for a clean camera release."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=join_timeout)


class VisionApp:
    def __init__(
        self,
        vlm_model: str = VLM_MODEL,
        ollama_url: str = "http://localhost:11434",
        piper_model: str = DEFAULT_PIPER_MODEL,
        piper_config: str = None,
        speaker_id: int = 0,
        gentle: bool = False,
        debug: bool = False,
        camera_device: str = None,
        save_frame: str = None,
        preview: bool = False,
    ):
        self.vlm_model = vlm_model
        self.ollama_url = ollama_url.rstrip("/")
        self.piper_model = piper_model
        self.piper_config = piper_config
        self.speaker_id = speaker_id
        self.gentle = gentle
        self.debug = debug
        self.camera_device = camera_device
        self.save_frame = save_frame
        self.preview = preview
        self.controller = None

    def _try_start_preview(self, device: str):
        """Start the live preview if possible; return CameraPreview or None.

        Returns None (and prints an actionable hint) when opencv is missing, no
        display is available, or the camera/window fails to open. In every
        None case the caller falls back to the reliable ffmpeg one-shot path.
        """
        # Headless guard: imshow needs a display server (X11 or Wayland).
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            print("⚠️ --preview needs a display, but none was detected "
                  "($DISPLAY/$WAYLAND_DISPLAY unset).")
            return None

        try:
            import cv2  # noqa: F401  (lazy: only needed for --preview)
        except Exception:
            print("⚠️ --preview needs opencv-python: pip install opencv-python")
            return None

        try:
            preview = CameraPreview(device, debug=self.debug)
            preview.start()
        except Exception as e:
            print(f"⚠️ Could not start camera preview: {e}")
            return None

        if preview.error:
            print(f"⚠️ Could not start camera preview: {preview.error}")
            preview.stop()
            return None

        print("✅ Live preview open — this window now owns the camera.")
        return preview

    async def _describe_scene(self, session, b64_image: str) -> str:
        """Stream a description of the image from the local vision model."""
        import aiohttp

        payload = {
            "model": self.vlm_model,
            "prompt": VISION_PROMPT,
            "images": [b64_image],
            "stream": True,
            "options": {"temperature": 0.5, "num_predict": 120},
        }

        full = ""
        try:
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300),
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"\n⚠️ Ollama vision error ({resp.status}): {text[:200]}")
                    return ""
                async for raw in resp.content:
                    if not raw:
                        continue
                    try:
                        chunk = json.loads(raw.decode("utf-8"))
                    except Exception:
                        continue
                    if chunk.get("error"):
                        print(f"\n⚠️ Ollama error: {chunk['error']}")
                        return ""
                    piece = chunk.get("response", "")
                    if piece:
                        print(piece, end="", flush=True)
                        full += piece
                    if chunk.get("done"):
                        break
        except asyncio.TimeoutError:
            print("\n⚠️ Vision model timed out.")
        except Exception as e:
            print(f"\n⚠️ Vision request failed: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
        return full.strip()

    async def run_async(self):
        import aiohttp
        from reachy_mini import ReachyMini
        from reachy_mini.utils import create_head_pose

        # Resolve the camera device up front so we fail early with a clear message.
        device = self.camera_device or find_camera_device()

        print("=" * 60)
        print("👀 Reachy Mini Vision (Task 3) — fully local on AMD")
        print("=" * 60)
        print(f"Vision model:  {self.vlm_model}")
        print(f"Piper model:   {self.piper_model}")
        print(f"Camera device: {device}")
        print("Press Enter to have Reachy look and describe. Type 'q' then Enter to quit.")
        print("=" * 60)

        # When --preview is on, one OpenCV thread owns the camera for the whole
        # session and the VLM frame is pulled from that stream. Otherwise we use
        # the reliable on-demand ffmpeg grab (the unchanged booth default).
        preview = None
        if self.preview:
            preview = self._try_start_preview(device)
            if preview is None:
                print("   Falling back to the ffmpeg one-shot capture path.")

        # Both paths converge on JPEG bytes, so the save/base64/VLM code is shared.
        def grab_jpeg() -> bytes:
            if preview is not None:
                return preview.encode_latest_jpeg()
            return capture_jpeg(device)

        # Verify the camera before connecting to the robot.
        print("📷 Testing camera...")
        try:
            test_jpeg = await asyncio.to_thread(grab_jpeg)
            print(f"✅ Camera OK ({len(test_jpeg)} bytes).\n")
        except Exception as e:
            print(f"❌ Could not read camera {device}: {e}")
            print("   Try a different device, e.g.: --camera-device /dev/video0")
            print("   List cameras with: v4l2-ctl --list-devices")
            if preview is not None:
                preview.stop()
            return

        try:
            # media_backend="no_media": motion only. We read the camera ourselves
            # (the daemon's WebRTC media server is not available on the booth box).
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")

                self.controller = EmotionControllerV71(
                    reachy,
                    self.piper_model,
                    self.piper_config,
                    self.speaker_id,
                    self.debug,
                    gentle_mode=self.gentle,
                )

                reachy.goto_target(head=create_head_pose(), duration=1.0)
                await asyncio.sleep(1.0)

                async with aiohttp.ClientSession() as session:
                    while True:
                        if preview is not None and preview.stopped:
                            print("\n👋 Preview window closed — quitting.")
                            break

                        cmd = await asyncio.to_thread(input, "\n👁️  Press Enter to look (or 'q' to quit): ")
                        if cmd.strip().lower() in ("q", "quit", "exit"):
                            print("👋 Goodbye!")
                            break

                        try:
                            jpeg = await asyncio.to_thread(grab_jpeg)
                        except Exception as e:
                            print(f"⚠️ Could not capture a frame: {e}")
                            continue

                        if preview is not None:
                            print("📸 Captured the current preview frame.")

                        if self.save_frame:
                            try:
                                with open(self.save_frame, "wb") as f:
                                    f.write(jpeg)
                                print(f"💾 Saved camera frame to {self.save_frame}")
                            except Exception as e:
                                print(f"⚠️ Could not save frame: {e}")

                        b64 = base64.b64encode(jpeg).decode("ascii")

                        print("\n🤖 Reachy sees: ", end="", flush=True)
                        description = await self._describe_scene(session, b64)
                        print()

                        if description:
                            emotion, intensity, emotion_level = self.controller.analyze_emotion(description)
                            if self.debug:
                                print(f"🎭 Emotion: {emotion} ({intensity}, level={emotion_level})")
                            await self.controller.speak_with_expression_parallel(
                                description, emotion, intensity, emotion_level
                            )

        except KeyboardInterrupt:
            print("\n👋 Interrupted.")
        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            print("   Is the daemon running? Start it with: reachy-mini-daemon")
            if self.debug:
                import traceback
                traceback.print_exc()
        finally:
            if preview is not None:
                preview.stop()

    def run(self):
        asyncio.run(self.run_async())


def main():
    parser = argparse.ArgumentParser(description="Reachy Mini Vision (Task 3) — local VLM + Piper-TTS")
    parser.add_argument('--vlm-model', default=VLM_MODEL, help='Ollama vision model name')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--piper-model', default=DEFAULT_PIPER_MODEL, help='Path to Piper .onnx model')
    parser.add_argument('--piper-config', default=None, help='Path to Piper .json config')
    parser.add_argument('--speaker', type=int, default=0, help='Speaker ID for multi-speaker models')
    parser.add_argument('--gentle', action='store_true', help='Enable gentle_mode for subtler motions')
    parser.add_argument('--camera-device', default=None,
                        help='V4L2 device to use (default: auto-detect the Arducam, e.g. /dev/video2)')
    parser.add_argument('--save-frame', default=None, help='Save each captured frame to this path (debugging)')
    parser.add_argument('--preview', action='store_true',
                        help='Show a live window of what Reachy sees (needs opencv-python + a display)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')

    args = parser.parse_args()

    if not check_runtime_dependencies(require_reachy=True):
        return

    app = VisionApp(
        vlm_model=args.vlm_model,
        ollama_url=args.url,
        piper_model=args.piper_model,
        piper_config=args.piper_config,
        speaker_id=args.speaker,
        gentle=args.gentle,
        debug=args.debug,
        camera_device=args.camera_device,
        save_frame=args.save_frame,
        preview=args.preview,
    )
    app.run()


if __name__ == "__main__":
    main()
