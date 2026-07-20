"""The Guide window — a paged, RESIZABLE help book (owner spec).

Pages group related images (assets/guide/pages.json) in a 1- or
2-column grid; every image carries its own bold subtitle and paragraph
(captions.json, "Title\\ntext" — the first line is the title). Images
scale WITH the window: the initial size shows a single-column image at
GUIDE_INITIAL_IMAGE_PX (540 = 75% of the 720 originals) and resizing
the dialog resizes them live. Page content scrolls when taller than
the window.
"""

import html
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.theme import apply_theme, size_to_screen
from app.ui_style import style_button
from config import constants, defaults
from config.ui_text import ui


class GuideDialog(QDialog):
    def __init__(self, translations: dict | None = None):
        super().__init__()
        overlay = translations or {}
        self.setWindowTitle(f"{constants.APP_NAME} — {ui(overlay, 'Guide')}")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # Minimize/maximize in the title bar (owner 2026-07-14 — same
        # as the Encyclopedia).
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        # NON-MODAL lifecycle (ITEM 1, R4 owner instruction batch
        # 2026-07-20): the controller now `.show()`s this dialog instead
        # of `.exec()`ing it, so the dial stays interactive while it is
        # open — the controller keeps the ONE live instance as an
        # attribute and this flag lets Qt tear the C++ object down the
        # moment the window closes, matching the Python reference it
        # clears on the same `finished` signal.
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        pages_path = defaults.GUIDE_DIR / "pages.json"
        self._pages = json.loads(pages_path.read_text(encoding="utf-8"))["pages"]
        captions = {}
        captions_path = defaults.GUIDE_DIR / "captions.json"
        if captions_path.exists():
            captions = json.loads(captions_path.read_text(encoding="utf-8"))
        # The active language's overlay wins over the shipped English.
        self._captions = {
            stem: overlay.get(f"guide/{stem}", text)
            for stem, text in captions.items()
        }
        self._page_titles = [
            overlay.get(f"guide_page/{index}", page["title"])
            for index, page in enumerate(self._pages)
        ]
        self._index = 0
        self._cells: list[tuple[QLabel, QPixmap, int]] = []  # label, art, columns

        self._title = QLabel()
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            f"font-size: {defaults.GUIDE_TITLE_PX}px; font-weight: bold;"
            f"margin: {defaults.GUIDE_SPACING_PX}px;"
        )
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        # The pager wears the shared gradient pills (owner 2026-07-14:
        # big, vivid, modern — same chrome as the Encyclopedia).
        self._counter = QLabel()
        self._counter.setStyleSheet(
            f"font-size: {defaults.UI_BUTTON_FONT_PX}px;"
            "font-weight: bold;"
        )
        previous = QPushButton(ui(overlay, "← Previous"))
        previous.clicked.connect(lambda: self._step(-1))
        style_button(previous, "previous")
        following = QPushButton(ui(overlay, "Next →"))
        following.clicked.connect(lambda: self._step(+1))
        style_button(following, "next")
        row = QHBoxLayout()
        row.addWidget(previous)
        row.addStretch(1)
        row.addWidget(self._counter)
        row.addStretch(1)
        row.addWidget(following)
        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._scroll, stretch=1)
        layout.addLayout(row)

        # OPENING SIZE (owner DESIGN #1): square, 50% of the screen's
        # available height — the images already rescale live with the
        # window (`_rescale`/`resizeEvent`/`showEvent` below), so a
        # shape different from the old GUIDE_INITIAL_IMAGE_PX-derived
        # rectangle costs nothing.
        size_to_screen(self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION)
        apply_theme(self)
        self._show_page()

    def _step(self, delta: int) -> None:
        self._index = (self._index + delta) % len(self._pages)
        self._show_page()

    def _show_page(self) -> None:
        page = self._pages[self._index]
        self._title.setText(self._page_titles[self._index])
        self._counter.setText(f"{self._index + 1} / {len(self._pages)}")
        columns = page["columns"]
        content = QWidget()
        grid = QGridLayout(content)
        grid.setHorizontalSpacing(defaults.GUIDE_SPACING_PX * 2)
        grid.setVerticalSpacing(defaults.GUIDE_SPACING_PX * 2)
        self._cells = []
        for position, stem in enumerate(page["images"]):
            cell = QVBoxLayout()
            cell.setSpacing(defaults.GUIDE_SPACING_PX)
            image = QLabel()
            image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            art = QPixmap(str(defaults.GUIDE_DIR / f"{stem}.png"))
            self._cells.append((image, art, columns))
            cell.addWidget(image)
            title, _, body = self._captions.get(stem, "\n").partition("\n")
            text = QLabel(
                f"<div style='font-size: {defaults.GUIDE_SUBTITLE_PX}px'>"
                f"<b>{html.escape(title)}</b></div>"
                f"<div style='margin-top: {defaults.GUIDE_SPACING_PX}px;"
                f"font-size: {defaults.GUIDE_BODY_PX}px'>"
                f"{html.escape(body)}</div>"
            )
            text.setWordWrap(True)
            text.setAlignment(Qt.AlignmentFlag.AlignTop)
            cell.addWidget(text)
            cell.addStretch(1)
            grid.addLayout(cell, position // columns, position % columns)
        self._scroll.setWidget(content)
        self._rescale()

    def _rescale(self) -> None:
        """Fit every image to its grid cell — called on page turns AND
        window resizes (owner spec: the Guide is resizable). The
        HEIGHT ceiling applies here too (owner imperative 2026-07-14:
        an image never eats more than the fraction of the page — the
        caption must stay on screen)."""
        available = max(
            240,
            self._scroll.viewport().width() - 4 * defaults.GUIDE_SPACING_PX,
        )
        max_height = round(
            self._scroll.viewport().height()
            * defaults.READER_IMAGE_MAX_HEIGHT_FRACTION
        )
        for image, art, columns in self._cells:
            if art.isNull():
                continue
            width = max(160, available // columns - defaults.GUIDE_SPACING_PX)
            pixmap = art.scaledToWidth(
                min(width, art.width()),
                Qt.TransformationMode.SmoothTransformation,
            )
            if pixmap.height() > max_height:
                pixmap = art.scaledToHeight(
                    max(24, max_height),
                    Qt.TransformationMode.SmoothTransformation,
                )
            image.setPixmap(pixmap)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._rescale()

    def showEvent(self, event) -> None:
        # The page is built BEFORE the window has its real geometry —
        # the images sized themselves to a guessed, smaller viewport
        # until a manual resize (owner bug 2026-07-14: same class as
        # the Encyclopedia's first-open deformation). Rescale once the
        # true size exists.
        super().showEvent(event)
        self._rescale()
