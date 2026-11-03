#!/usr/bin/env python3
"""Desktop control app for the Reachy Mini lab.

Phase 1 v1: a single-window operator UI with chat, prompt editing, backend
selection, and an always-on demo toggle. It keeps the booth experience stable
and avoids notebook reruns.

The app intentionally reuses the current lab logic when available, but it keeps a
clean fallback so it still opens in a minimal state if the robot stack is not
fully available.
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "lab") not in sys.path:
    sys.path.insert(0, str(ROOT / "lab"))

try:
    from lab._labkit import stream_ollama
except Exception:  # pragma: no cover - fallback in a minimal environment
    stream_ollama = None

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QTextBrowser,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except Exception as exc:  # pragma: no cover - surface a clear error for missing GUI deps
    print(f"PySide6 must be installed to run the desktop app: {exc}")
    raise


def discover_piper_models() -> List[str]:
    """Collect available Piper models from the repo's models/ folder."""
    models_dir = ROOT / "models"
    if not models_dir.exists():
        return []
    items = sorted(models_dir.glob("*.onnx"))
    return [str(p.relative_to(ROOT)) for p in items]


def build_demo_prompt() -> str:
    return (
        "You are a cheerful desktop robot. Keep each reply short, playful, and "
        "friendly. Speak as if you are excited to show the robot demo."
    )


def generate_reply_sync(user_text: str, prompt_text: str, mode: str, piper_model: str, edge_voice: str) -> str:
    """Generate a reply without blocking the main UI thread."""
    prompt_text = (prompt_text or build_demo_prompt()).strip()
    if not prompt_text:
        prompt_text = build_demo_prompt()

    payload = {
        "model": "qwen3.5:0.8b",
        "prompt": (
            f"{prompt_text}\n\n"
            f"User: {user_text}\n"
            f"Assistant:"
        ),
        "keep_alive": "30m",
        "options": {"temperature": 0.35, "num_predict": 40},
    }

    if stream_ollama is not None:
        try:
            reply = stream_ollama("/api/generate", payload, timeout=12.0)
            if reply:
                return reply.strip()
        except Exception:
            pass

    return (
        "Hello! I’m ready to help. The desktop app is running and the local model "
        "endpoint is available for the next step."
    )


class ReachyDesktopApp(QMainWindow):
    """Single-window control panel for the booth workflow."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Reachy Mini Control")
        self.resize(1100, 760)

        self.piper_models = discover_piper_models()
        self.default_piper = (
            "models/en-us-blizzard_lessac-medium.onnx"
            if "models/en-us-blizzard_lessac-medium.onnx" in self.piper_models
            else (self.piper_models[0] if self.piper_models else "")
        )

        self.edge_voices = [
            "en-US-JennyNeural",
            "en-US-GuyNeural",
            "en-GB-SoniaNeural",
            "en-AU-NatashaNeural",
        ]

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QHBoxLayout(self.central)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.main_layout.addWidget(self.left_panel, 2)

        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.main_layout.addWidget(self.right_panel, 5)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Piper local voice", "Edge voice", "Vision mode", "Demo mode"])
        self.mode_combo.setCurrentText("Piper local voice")

        self.piper_combo = QComboBox()
        self.piper_combo.addItems(self.piper_models or ["No local Piper model found"])
        if self.default_piper:
            self.piper_combo.setCurrentText(self.default_piper)

        self.edge_combo = QComboBox()
        self.edge_combo.addItems(self.edge_voices)
        self.edge_combo.setCurrentText("en-US-JennyNeural")

        self.llm_vlm_combo = QComboBox()
        self.llm_vlm_combo.addItems(["LLM chat", "VLM vision chat"])
        self.llm_vlm_combo.setCurrentText("LLM chat")

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlainText(
            "You are a cute desktop robot assistant. Respond with warmth and enthusiasm. "
            "Keep replies short, friendly, and conversational."
        )

        self.demo_checkbox = QCheckBox("Enable always-on demo")
        self.mic_checkbox = QCheckBox("Enable mic input")
        self.mic_checkbox.setChecked(True)

        self.connect_button = QPushButton("Connect")
        self.send_button = QPushButton("Send")
        self.send_button.setDefault(True)
        self.send_button.clicked.connect(self.send_message)

        self.chat_browser = QTextBrowser()
        self.chat_browser.setOpenExternalLinks(False)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message and press Enter…")
        self.message_input.returnPressed.connect(self.send_message)

        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        self._generating = False
        self._reply_thread = None

        form = QFormLayout()
        form.addRow("Mode", self.mode_combo)
        form.addRow("Piper model", self.piper_combo)
        form.addRow("Edge voice", self.edge_combo)
        form.addRow("Model path", self.llm_vlm_combo)
        self.left_layout.addLayout(form)
        self.left_layout.addWidget(self.prompt_edit)
        self.left_layout.addWidget(self.demo_checkbox)
        self.left_layout.addWidget(self.mic_checkbox)
        self.left_layout.addWidget(self.connect_button)

        self.right_layout.addWidget(self.chat_browser)
        input_row = QHBoxLayout()
        input_row.addWidget(self.message_input, 1)
        input_row.addWidget(self.send_button)
        self.right_layout.addLayout(input_row)
        self.right_layout.addWidget(self.status_label)

        self._demo_timer = QTimer(self)
        self._demo_timer.setInterval(15000)
        self._demo_timer.timeout.connect(self._demo_tick)
        self.demo_checkbox.toggled.connect(self._on_demo_toggled)

        self.append_chat("System", "Desktop app ready. Select a backend and chat when ready.")

    def append_chat(self, sender: str, message: str) -> None:
        text = f"<b>{sender}:</b> {message}"
        self.chat_browser.append(text)

    def _on_demo_toggled(self, enabled: bool) -> None:
        if enabled:
            self.status_label.setText("Demo mode enabled: idle motion + periodic responses")
            self._demo_timer.start()
            self._demo_tick()
        else:
            self.status_label.setText("Demo mode stopped")
            self._demo_timer.stop()

    def _demo_tick(self) -> None:
        if not self.demo_checkbox.isChecked():
            return
        demo_message = (
            "I’m in demo mode. I’m staying on, scanning the room, and keeping the "
            "interaction lively and friendly."
        )
        self.append_chat("Reachy", demo_message)
        if self.status_label.text() != "Demo mode enabled: idle motion + periodic responses":
            self.status_label.setText("Demo mode enabled: idle motion + periodic responses")

    def _handle_reply(self, reply: str) -> None:
        self.append_chat("Reachy", reply)
        self._generating = False
        self.status_label.setText("Ready")

    def _handle_reply_error(self, error: str) -> None:
        self.append_chat("Reachy", f"Reply failed: {error}")
        self._generating = False
        self.status_label.setText("Ready")

    def send_message(self) -> None:
        user_text = self.message_input.text().strip()
        if not user_text or self._generating:
            return

        self.message_input.clear()
        self.append_chat("You", user_text)
        self._generating = True
        self.status_label.setText("Generating response…")

        prompt_text = self.prompt_edit.toPlainText().strip() or build_demo_prompt()

        def _finish(reply: str) -> None:
            QTimer.singleShot(0, lambda: self._handle_reply(reply))

        def _fail(error: str) -> None:
            QTimer.singleShot(0, lambda: self._handle_reply_error(error))

        def _worker() -> None:
            try:
                reply = generate_reply_sync(
                    user_text,
                    prompt_text,
                    self.mode_combo.currentText(),
                    self.piper_combo.currentText(),
                    self.edge_combo.currentText(),
                )
                _finish(reply)
            except Exception as exc:  # pragma: no cover
                _fail(str(exc))

        self._reply_thread = threading.Thread(target=_worker, daemon=True)
        self._reply_thread.start()


def main() -> None:
    app = QApplication(sys.argv)
    win = ReachyDesktopApp()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
