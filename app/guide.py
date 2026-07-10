"""The Guide window — a left/right help carousel (owner spec).

Slides are the owner's PNGs in assets/guide/ (sorted by filename, e.g.
01_intro.png) with optional captions in assets/guide/captions.json
({"01_intro": "text"}). Until they land, the window shows a friendly
placeholder — the frame ships first so the content can simply be
dropped in.
"""

import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from config import constants, defaults


class GuideDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{constants.APP_NAME} — Guide")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._slides = sorted(defaults.GUIDE_DIR.glob("*.png"))
        self._captions = {}
        captions_path = defaults.GUIDE_DIR / "captions.json"
        if captions_path.exists():
            self._captions = json.loads(captions_path.read_text(encoding="utf-8"))
        self._index = 0

        self._image = QLabel()
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption = QLabel()
        self._caption.setWordWrap(True)
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._counter = QLabel()
        previous = QPushButton("← Previous")
        previous.clicked.connect(lambda: self._step(-1))
        following = QPushButton("Next →")
        following.clicked.connect(lambda: self._step(+1))
        row = QHBoxLayout()
        row.addWidget(previous)
        row.addStretch(1)
        row.addWidget(self._counter)
        row.addStretch(1)
        row.addWidget(following)
        layout = QVBoxLayout(self)
        layout.addWidget(self._image)
        layout.addWidget(self._caption)
        layout.addLayout(row)
        self._show_slide()

    def _step(self, delta: int) -> None:
        if self._slides:
            self._index = (self._index + delta) % len(self._slides)
            self._show_slide()

    def _show_slide(self) -> None:
        if not self._slides:
            self._image.setText(
                "The guide slides are on their way —\n"
                "drop them into assets/guide/ as NN_name.png."
            )
            self._counter.setText("0 / 0")
            return
        slide = self._slides[self._index]
        pixmap = QPixmap(str(slide))
        if pixmap.width() > defaults.GUIDE_SLIDE_MAX_PX:
            pixmap = pixmap.scaledToWidth(
                defaults.GUIDE_SLIDE_MAX_PX,
                Qt.TransformationMode.SmoothTransformation,
            )
        self._image.setPixmap(pixmap)
        self._caption.setText(self._captions.get(slide.stem, ""))
        self._counter.setText(f"{self._index + 1} / {len(self._slides)}")
