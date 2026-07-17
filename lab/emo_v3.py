#!/usr/bin/env python3
"""emo_v3.py - Reachy Mini "sees" with a local vision model (Offline)

    ┌───────────────────────────────────────────────────────────────┐
    │  LAB EDIT?  Jump to the "# >>> TRY ME <<<" block below          │
    │  (press Ctrl+F, search: TRY ME). Change VISION_PROMPT, save,    │
    │  and re-run. That one block is the only thing you need to edit. │
    └───────────────────────────────────────────────────────────────┘

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
  python lab/emo_v3.py --preview-web         # live feed + "Look" button in a browser at http://localhost:8080
  python lab/emo_v3.py --preview             # same thing (redirects to the browser preview)
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

# Silence the Reachy SDK's intentionally-unused media subsystem (see the detailed
# note in emo_v1.py). Repeated here so the suppression still applies when this
# script is run directly. Idempotent; runs before the robot connects.
def _drop_audio_not_initialized(record: logging.LogRecord) -> bool:
    return "Audio system is not initialized." not in record.getMessage()


logging.getLogger("reachy_mini.media.media_manager").addFilter(
    _drop_audio_not_initialized
)
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

# The one-click launcher (run-lab.sh) lets attendees type a prompt without
# editing this file; it passes it in via LAB_VISION_PROMPT. A value here wins
# over the default above, but editing VISION_PROMPT directly still works too.
if os.environ.get("LAB_VISION_PROMPT", "").strip():
    VISION_PROMPT = os.environ["LAB_VISION_PROMPT"].strip()

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


def capture_jpeg(device: str, max_width: int = 1024, quality: int = 4, timeout: int = 15,
                 retries: int = 3, retry_delay: float = 0.8,
                 capture_width: int = 1280, capture_height: int = 720) -> bytes:
    """Grab a single JPEG frame from a V4L2 device using ffmpeg.

    Returns the raw JPEG bytes. Raises RuntimeError on failure.

    "Device or resource busy" is often transient — a preview thread releasing the
    camera, or the daemon briefly touching it during startup — so we retry a few
    times before giving up.

    We force MJPEG input at a modest capture resolution. Without an explicit
    `-input_format`/`-video_size`, ffmpeg often negotiates the camera's raw YUYV
    mode at its huge native resolution, which the Arducam only offers at ~1 fps —
    that both makes the grab crawl and gives wildly different behavior machine to
    machine. MJPEG at 1280x720 is fast and consistent everywhere.
    """
    tail = [
        "-i", device,
        "-frames:v", "1",
        "-vf", f"scale='min({max_width},iw)':-2",
        "-q:v", str(quality),
        "-f", "image2", "-c:v", "mjpeg", "pipe:1",
    ]
    # Preferred: force MJPEG at a modest size (fast + consistent). Fallback: let
    # ffmpeg negotiate whatever the device offers (for non-Arducam devices that
    # may not expose MJPEG at 1280x720).
    cmd_mjpeg = [
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-f", "v4l2",
        "-input_format", "mjpeg",
        "-video_size", f"{capture_width}x{capture_height}",
    ] + tail
    cmd_auto = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "v4l2"] + tail

    last_err = ""
    for cmd in (cmd_mjpeg, cmd_auto):
        for attempt in range(max(1, retries)):
            proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
            if proc.returncode == 0 and proc.stdout:
                return proc.stdout
            last_err = proc.stderr.decode(errors="ignore").strip()
            if "busy" in last_err.lower() and attempt < retries - 1:
                time.sleep(retry_delay)
                continue
            break  # non-busy error: try the next command variant
    raise RuntimeError(last_err[:300] or "ffmpeg produced no frame")


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


class WebPreview:
    """Browser-based live preview: one ffmpeg MJPEG stream, served over HTTP.

    This is the robust alternative to the OpenCV window (`CameraPreview`) for
    machines where cv2's Qt GUI can't init (e.g. broken xcb plugin under
    Wayland). A single ffmpeg process owns the camera and emits a continuous
    MJPEG stream; a tiny stdlib HTTP server hands frames to the browser AND to
    the VLM (via `encode_latest_jpeg`), so nothing else ever opens the camera —
    no "Device or resource busy" collisions.

    Open http://localhost:<port>/ in a browser to watch the feed.
    """

    def __init__(
        self,
        device: str,
        port: int = 8080,
        max_width: int = 960,
        fps: int = 15,
        quality: int = 5,
        debug: bool = False,
        capture_width: int = 1280,
        capture_height: int = 720,
    ):
        self.device = device
        self.port = port
        self.max_width = max_width
        self.fps = fps
        self.quality = quality
        self.debug = debug
        self.capture_width = capture_width
        self.capture_height = capture_height

        self._latest = None            # most recent JPEG bytes
        self._lock = threading.Lock()  # guards _latest
        self._stop = threading.Event()
        self._ready = threading.Event()  # set once we have a frame or an error
        self._look = threading.Event()   # set when the browser "Look" button is clicked
        self._busy = False               # True while a look is being processed
        self._frozen = None              # JPEG bytes to show while frozen (None = live)
        self._error: str = None
        self._proc = None              # ffmpeg subprocess
        self._reader: threading.Thread = None
        self._httpd = None
        self._http_thread: threading.Thread = None

    @property
    def error(self) -> str:
        return self._error

    @property
    def stopped(self) -> bool:
        return self._stop.is_set()

    def start(self, timeout: float = 12.0) -> None:
        """Start ffmpeg + HTTP server; block until the first frame or an error."""
        self._reader = threading.Thread(target=self._run_ffmpeg, name="reachy-web-cam", daemon=True)
        self._reader.start()
        if not self._ready.wait(timeout=timeout):
            self._error = self._error or "timed out waiting for the first frame"
            return
        if self._error:
            return
        self._start_http()

    def _build_ffmpeg_cmd(self, force_mjpeg: bool) -> list:
        # Continuous MJPEG to stdout. mpjpeg muxer emits multipart frames we can
        # split on the JPEG SOI/EOI markers.
        #
        # force_mjpeg: ask the camera for its MJPEG mode at a modest capture size.
        # Without this, ffmpeg often picks the Arducam's raw YUYV mode at full
        # native resolution, which the sensor only delivers at ~1 fps — the exact
        # "super low fps on some machines" bug. MJPEG is fast + consistent, but a
        # few non-Arducam webcams don't expose it, so we keep an auto fallback.
        head = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "v4l2"]
        if force_mjpeg:
            head += [
                "-input_format", "mjpeg",
                "-video_size", f"{self.capture_width}x{self.capture_height}",
                "-framerate", str(self.fps),
            ]
        return head + [
            "-i", self.device,
            "-vf", f"scale='min({self.max_width},iw)':-2",
            "-r", str(self.fps),
            "-q:v", str(self.quality),
            "-f", "mpjpeg", "-",
        ]

    def _run_ffmpeg(self) -> None:
        # Try the fast, consistent MJPEG mode first; if the device rejects it
        # (rare non-Arducam webcams) and we never got a frame, retry with ffmpeg's
        # default format negotiation so the preview still works somewhere.
        for force_mjpeg in (True, False):
            got_frame = self._stream_ffmpeg(self._build_ffmpeg_cmd(force_mjpeg))
            if got_frame or self._stop.is_set():
                return
            if force_mjpeg and self.debug:
                print("   (web preview) MJPEG mode failed, retrying auto format...")
            # Clear the pending error so the fallback attempt gets a clean slate.
            self._error = None

    def _stream_ffmpeg(self, cmd: list) -> bool:
        """Run one ffmpeg capture attempt. Returns True if any frame was read."""
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0
            )
        except Exception as e:
            self._error = f"could not start ffmpeg: {e}"
            self._ready.set()
            return False

        got_frame = False
        buf = b""
        soi = b"\xff\xd8"  # JPEG start
        eoi = b"\xff\xd9"  # JPEG end
        try:
            while not self._stop.is_set():
                chunk = self._proc.stdout.read(4096)
                if not chunk:
                    # ffmpeg exited — surface its error.
                    err = b""
                    try:
                        err = self._proc.stderr.read() or b""
                    except Exception:
                        pass
                    msg = err.decode(errors="ignore").strip()
                    self._error = self._error or (msg[:300] or "camera stream ended")
                    # Only mark ready on a hard failure; if we already streamed
                    # frames the ready flag is long since set.
                    if not got_frame:
                        self._ready.set()
                    break
                buf += chunk
                # Extract the most recent complete JPEG in the buffer.
                start = buf.rfind(soi)
                end = buf.rfind(eoi)
                if start != -1 and end != -1 and end > start:
                    frame = buf[start:end + 2]
                    with self._lock:
                        self._latest = frame
                    got_frame = True
                    if not self._ready.is_set():
                        self._ready.set()
                    buf = buf[end + 2:]
                # Guard against unbounded growth if markers aren't found.
                if len(buf) > 4_000_000:
                    buf = buf[-1_000_000:]
        finally:
            self._terminate_ffmpeg()
        return got_frame

    def _start_http(self) -> None:
        import http.server

        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                if outer.debug:
                    super().log_message(*args)

            def do_GET(self):
                if self.path in ("/", "/index.html"):
                    self._serve_page()
                elif self.path.startswith("/frame"):
                    self._serve_frame()
                elif self.path.startswith("/look"):
                    self._serve_look()
                else:
                    self.send_error(404)

            def _serve_look(self):
                # Browser "Look" button — trigger a look from the web UI so the
                # user never has to touch the terminal.
                accepted = not outer._busy
                if accepted:
                    outer._look.set()
                body = b'{"accepted": true}' if accepted else b'{"accepted": false}'
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def _serve_page(self):
                # A self-refreshing <img> that polls /frame. Each request is
                # short-lived (one frame, then the connection closes), so the
                # server never accumulates long-lived streaming threads — robust
                # for a booth even with multiple tabs open.
                html = (
                    b"<!doctype html><html><head><meta charset='utf-8'>"
                    b"<title>Reachy sees</title>"
                    b"<style>body{margin:0;background:#111;display:flex;flex-direction:column;"
                    b"align-items:center;justify-content:center;height:100vh;font-family:sans-serif;color:#eee}"
                    b"h1{font-weight:600;margin:12px}img{max-width:96vw;max-height:76vh;"
                    b"border-radius:12px;box-shadow:0 8px 40px rgba(0,0,0,.6)}"
                    b"#look{margin:18px;padding:16px 42px;font-size:22px;font-weight:700;"
                    b"border:none;border-radius:999px;background:#e8112d;color:#fff;cursor:pointer;"
                    b"box-shadow:0 4px 20px rgba(232,17,45,.5);transition:transform .06s}"
                    b"#look:active{transform:scale(.96)}#look:disabled{background:#666;cursor:default;box-shadow:none}"
                    b"#msg{min-height:24px;font-size:16px;color:#bbb;margin-top:4px}</style></head>"
                    b"<body><h1>Reachy sees</h1>"
                    b"<img id='v' alt='live camera feed'/>"
                    b"<button id='look'>Look &amp; Describe</button>"
                    b"<div id='msg'></div>"
                    b"<script>"
                    b"const img=document.getElementById('v');"
                    b"function tick(){const n=new Image();"
                    b"n.onload=()=>{img.src=n.src;setTimeout(tick,66);};"
                    b"n.onerror=()=>setTimeout(tick,300);"
                    b"n.src='/frame?t='+Date.now();}"
                    b"tick();"
                    b"const btn=document.getElementById('look'),msg=document.getElementById('msg');"
                    b"btn.onclick=async()=>{btn.disabled=true;img.style.opacity='.6';msg.textContent='Looking (feed frozen)...';"
                    b"try{const r=await fetch('/look');const j=await r.json();"
                    b"msg.textContent=j.accepted?'Reachy is looking & describing (listen!)':'Reachy is busy, one sec...';}"
                    b"catch(e){msg.textContent='Error triggering look';}"
                    b"setTimeout(()=>{btn.disabled=false;img.style.opacity='1';msg.textContent='';},6000);};"
                    b"</script></body></html>"
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)

            def _serve_frame(self):
                # While a look is being processed we freeze the feed on the exact
                # frame the VLM is looking at, so the browser shows what Reachy saw.
                frame = outer._frozen if outer._frozen is not None else outer._get_latest()
                if frame is None:
                    self.send_error(503, "no frame yet")
                    return
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(frame)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                try:
                    self.wfile.write(frame)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # browser navigated away mid-write — normal

        try:
            self._httpd = http.server.ThreadingHTTPServer(("0.0.0.0", self.port), Handler)
            # Reap request threads so multiple tabs/reconnects can't pile up.
            self._httpd.daemon_threads = True
        except OSError as e:
            self._error = f"could not bind http port {self.port}: {e}"
            return
        self._http_thread = threading.Thread(
            target=self._httpd.serve_forever, name="reachy-web-http", daemon=True
        )
        self._http_thread.start()

    def _get_latest(self):
        with self._lock:
            return self._latest

    def encode_latest_jpeg(self) -> bytes:
        """Return the most recent stream frame as JPEG bytes (for the VLM)."""
        frame = self._get_latest()
        if frame is None:
            raise RuntimeError("no preview frame available yet")
        return frame

    def freeze(self, frame: bytes = None) -> None:
        """Freeze the browser feed on `frame` (defaults to the latest frame)."""
        if frame is None:
            frame = self._get_latest()
        self._frozen = frame

    def unfreeze(self) -> None:
        """Resume the live browser feed."""
        self._frozen = None

    def _terminate_ffmpeg(self) -> None:
        if self._proc is not None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=2)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass

    def stop(self, join_timeout: float = 2.0) -> None:
        self._stop.set()
        if self._httpd is not None:
            try:
                self._httpd.shutdown()
            except Exception:
                pass
        self._terminate_ffmpeg()
        if self._reader is not None:
            self._reader.join(timeout=join_timeout)


class VisionApp:
    def __init__(
        self,
        vlm_model: str = VLM_MODEL,
        ollama_url: str = "http://127.0.0.1:11434",
        piper_model: str = DEFAULT_PIPER_MODEL,
        piper_config: str = None,
        speaker_id: int = 0,
        gentle: bool = False,
        debug: bool = False,
        camera_device: str = None,
        save_frame: str = None,
        preview: bool = False,
        preview_web: bool = False,
        web_port: int = 8080,
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
        self.preview_web = preview_web
        self.web_port = web_port
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

        # OpenCV's HighGUI (Qt) window fails to initialize under a native GNOME
        # Wayland session ("Ignoring XDG_SESSION_TYPE=wayland on Gnome ...") and
        # the preview then times out. Route the window through Xwayland (xcb)
        # when we're on Wayland but an X display ($DISPLAY) is available. Must be
        # set BEFORE cv2 initializes its GUI backend. Respect any value the user
        # already exported.
        if (
            os.environ.get("WAYLAND_DISPLAY")
            and os.environ.get("DISPLAY")
            and not os.environ.get("QT_QPA_PLATFORM")
        ):
            os.environ["QT_QPA_PLATFORM"] = "xcb"
            if self.debug:
                print("   (preview) forcing QT_QPA_PLATFORM=xcb for Xwayland")

        try:
            import cv2  # noqa: F401  (lazy: only needed for --preview)
        except Exception:
            print("⚠️ --preview needs opencv-python: pip install opencv-python")
            return None

        try:
            preview = CameraPreview(device, debug=self.debug)
            # Xwayland window init on first launch can be slow; give it room so
            # we don't fall back to the ffmpeg path (which then races the camera).
            preview.start(timeout=12.0)
        except Exception as e:
            print(f"⚠️ Could not start camera preview: {e}")
            return None

        if preview.error:
            print(f"⚠️ Could not start camera preview: {preview.error}")
            preview.stop()
            return None

        print("✅ Live preview open — this window now owns the camera.")
        return preview

    def _try_start_web_preview(self, device: str):
        """Start the browser MJPEG preview; return WebPreview or None.

        Robust alternative to the OpenCV window: no native GUI, so it can't hit
        the Qt/Wayland problems. Returns None (with a hint) if it fails, and the
        caller falls back to the on-demand ffmpeg grab.
        """
        try:
            web = WebPreview(device, port=self.web_port, debug=self.debug)
            web.start()
        except Exception as e:
            print(f"⚠️ Could not start web preview: {e}")
            return None

        if web.error:
            print(f"⚠️ Could not start web preview: {web.error}")
            web.stop()
            return None

        print("=" * 60)
        print(f"🌐 Live preview: open  http://localhost:{self.web_port}  in a browser")
        print("   (this stream now owns the camera for the whole session)")
        print("=" * 60)
        return web

    async def _describe_scene(self, session, b64_image: str) -> str:
        """Stream a description of the image from the local vision model."""
        import aiohttp

        payload = {
            "model": self.vlm_model,
            "prompt": VISION_PROMPT,
            "images": [b64_image],
            "stream": True,
            # keep_alive: keep the vision model resident between looks. The VLM is
            # the heaviest model in the lab, so avoiding a cold reload matters most
            # here — the second "Look" then feels much snappier than the first.
            "keep_alive": "30m",
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

        # When a live preview is on, ONE owner holds the camera for the whole
        # session and the VLM frame is pulled from that same stream. Otherwise we
        # use the reliable on-demand ffmpeg grab (the unchanged booth default).
        #
        # Both --preview and --preview-web use the browser feed. The native
        # OpenCV window (`--preview`) is unreliable on the booth machines (cv2's
        # Qt/xcb GUI can't init under Wayland and hard-crashes), so we always
        # route live preview through the robust browser path and just tell the
        # user when we're redirecting from --preview.
        preview = None
        if self.preview and not self.preview_web:
            print("ℹ️  --preview (native window) isn't reliable here — using the "
                  "browser preview instead.")
            self.preview_web = True
        if self.preview_web:
            preview = self._try_start_web_preview(device)
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

                # Web preview adds a browser "Look" button so the user never has
                # to touch the terminal. We wait for whichever fires first: the
                # button (web_look event) or a terminal line (Enter / 'q').
                web = preview if isinstance(preview, WebPreview) else None
                if web is not None:
                    print("\n👉 Click the red \"Look & Describe\" button in the browser "
                          "(or press Enter here).")

                # Trigger handling. Two things can start a look: pressing Enter in
                # this terminal, or clicking the browser button.
                #
                # stdin: input() can't be cancelled cleanly, so we run it on its
                # OWN dedicated single-thread executor and keep the future alive
                # across iterations (recreated only after it returns a line). This
                # is critical: earlier we ran BOTH the stdin reader and a blocking
                # web._look.wait() on the shared default executor. The un-cancelable
                # web waiters leaked threads and eventually starved the pool, so
                # input() never got a worker and pressing Enter did nothing. We now
                # (a) give stdin its own executor and (b) POLL the web event with a
                # short timeout so its worker thread always returns promptly.
                import concurrent.futures
                loop = asyncio.get_running_loop()
                stdin_pool = concurrent.futures.ThreadPoolExecutor(
                    max_workers=1, thread_name_prefix="reachy-stdin"
                )
                pending = {"stdin": None}

                def _make_stdin_task():
                    return asyncio.ensure_future(
                        loop.run_in_executor(
                            stdin_pool,
                            input,
                            "\n👁️  Press Enter (or click the button) to look; 'q' to quit: ",
                        )
                    )

                async def wait_for_trigger():
                    """Return 'quit' or 'look' — whichever the user does first."""
                    if pending["stdin"] is None or pending["stdin"].done():
                        pending["stdin"] = _make_stdin_task()

                    # Poll: check the web button often, but let Enter interrupt the
                    # wait as soon as it arrives.
                    while True:
                        if web is not None and web._look.is_set():
                            return "look"
                        done, _ = await asyncio.wait(
                            [pending["stdin"]], timeout=0.15,
                            return_when=asyncio.FIRST_COMPLETED,
                        )
                        if pending["stdin"] in done:
                            break
                        if web is None:
                            # No web button: just keep waiting on stdin.
                            continue

                    result = "look"
                    if pending["stdin"].done():
                        try:
                            cmd = pending["stdin"].result()
                            if cmd.strip().lower() in ("q", "quit", "exit"):
                                result = "quit"
                        except Exception:
                            result = "look"
                        pending["stdin"] = None  # consumed; make a fresh one next time
                    # If the web button fired, we leave the stdin task pending and
                    # reuse it next iteration (no extra threads accumulate).
                    return result

                async with aiohttp.ClientSession() as session:
                    while True:
                        if preview is not None and preview.stopped:
                            print("\n👋 Preview window closed — quitting.")
                            break

                        trigger = await wait_for_trigger()
                        if trigger == "quit":
                            print("👋 Goodbye!")
                            break

                        if web is not None:
                            web._busy = True
                        print("📸 Looking...", flush=True)
                        try:
                            jpeg = await asyncio.to_thread(grab_jpeg)
                        except Exception as e:
                            print(f"⚠️ Could not capture a frame: {e}")
                            if web is not None:
                                web._busy = False
                                web._look.clear()
                            continue

                        # Freeze the browser feed on the exact frame Reachy is
                        # describing, so the viewer sees what it saw until done.
                        if web is not None:
                            web.freeze(jpeg)

                        print(f"🤔 Thinking about what I see ({len(jpeg)} bytes)...", flush=True)

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

                        if web is not None:
                            web.unfreeze()
                            web._busy = False
                            web._look.clear()

                # The stdin worker may still be parked in a blocking input();
                # don't wait for it (it can't be interrupted) so 'q' quits cleanly.
                stdin_pool.shutdown(wait=False, cancel_futures=True)

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
    parser.add_argument('--url', default='http://127.0.0.1:11434', help='Ollama URL')
    parser.add_argument('--piper-model', default=DEFAULT_PIPER_MODEL, help='Path to Piper .onnx model')
    parser.add_argument('--piper-config', default=None, help='Path to Piper .json config')
    parser.add_argument('--speaker', type=int, default=0, help='Speaker ID for multi-speaker models')
    parser.add_argument('--gentle', action='store_true', help='Enable gentle_mode for subtler motions')
    parser.add_argument('--camera-device', default=None,
                        help='V4L2 device to use (default: auto-detect the Arducam, e.g. /dev/video2)')
    parser.add_argument('--save-frame', default=None, help='Save each captured frame to this path (debugging)')
    parser.add_argument('--preview', action='store_true',
                        help='Show a live preview of what Reachy sees (redirects to the browser preview)')
    parser.add_argument('--preview-web', action='store_true',
                        help='Live feed + "Look" button in a browser at http://localhost:PORT (no GUI needed)')
    parser.add_argument('--web-port', type=int, default=8080,
                        help='Port for --preview-web (default: 8080)')
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
        preview_web=args.preview_web,
        web_port=args.web_port,
    )
    app.run()


if __name__ == "__main__":
    main()
