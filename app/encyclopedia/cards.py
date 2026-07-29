"""The Encyclopedia's CARD — one component for both gallery levels.

The Session 27 rework (owner-sealed 2026-07-28) gave the browser two
gallery screens instead of one: six WHOLES on the home screen, then the
chosen whole's THEME cards. Both wear the same card — image, title,
one-line about, and a small footer stat — so there is one recipe, one
hover, one accent law (Rule #5). The two screens differ only in how the
grid is measured:

- **Home** — a FIXED 3x2 grid measured from the viewport's own width AND
  height, because the home screen may never scroll (owner law). The
  cards shrink with the window; nothing ever spills.
- **Themes** — up to `ENCYCLOPEDIA_GALLERY_MAX_COLUMNS` per row, wrapping
  into further rows, measured from the width alone; the vertical
  scrollbar is the only overflow this level ever needs.

THE NO-X-SCROLL LAW is enforced twice over, on purpose: the geometry
below can never produce a row wider than its viewport, AND the screens
that own a scroll area switch its horizontal bar OFF entirely. A law
that matters this much to the owner is not left to one mechanism.

Layer: app. Documentation: cards.md.
"""

from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from config import defaults, palette, paths
from render.asset_variants import scaled_variant_file


def row_content_width(card_width: int, columns: int) -> int:
    """The pixel width one full row of `columns` cards needs — the cards
    side by side, the gaps between them and the grid's own margins. The
    inverse of `card_width_for` below; the pair is one formula (Rule #5)
    so the dialog's minimum width and the live per-resize card size can
    never drift apart, which is exactly how the old gallery grew a
    horizontal scrollbar twice."""
    gap = defaults.ENCYCLOPEDIA_CARD_GAP_PX
    margins = defaults.ENCYCLOPEDIA_CARD_GAP_PX * 2
    return columns * card_width + (columns - 1) * gap + margins


def card_width_for(viewport_width: int, columns: int) -> int:
    """The widest card `columns` of which still fit inside
    `viewport_width` — the exact inverse of `row_content_width`."""
    gap = defaults.ENCYCLOPEDIA_CARD_GAP_PX
    margins = defaults.ENCYCLOPEDIA_CARD_GAP_PX * 2
    available = viewport_width - margins - (columns - 1) * gap
    return max(defaults.ENCYCLOPEDIA_CARD_MIN_WIDTH_PX, available // columns)


def card_pixmap(icon: Path | None) -> QPixmap:
    """The card's plate, decoded ONCE at the card decode ceiling and
    never at full resolution on the GUI thread (owner order 2026-07-26:
    entering the Encyclopedia must never block — the pre-warmed
    downscale answers when it exists, `build=False` never builds one
    here). A missing plate returns a null pixmap and the card simply
    shows its title, the graceful-absent contract every gallery tile
    has always had."""
    if icon is None:
        return QPixmap()
    resolved = paths.art_file(icon)
    if not resolved.exists():
        return QPixmap()
    ready = scaled_variant_file(
        resolved, defaults.ENCYCLOPEDIA_CARD_ICON_DECODE_PX, build=False,
    )
    return QPixmap(str(ready))


def mosaic_pixmap(icons: list[Path]) -> QPixmap:
    """A whole's tile COMPUTED from its own theme plates (root Rule #19
    — a category image is derivable, so it is never generated): the
    first four plates laid 2x2 on a transparent square. One plate fills
    the square alone, two split it side by side, three leave the fourth
    quarter empty. Fewer than one plate returns a null pixmap and the
    card shows its title alone, the graceful-absent contract.

    A hand-drawn plate at `ENCYCLOPEDIA_WHOLE_ART_DIR/<key>.png` takes
    precedence (see `home.py`) — this is the floor, not a ceiling."""
    plates = [plate for plate in (card_pixmap(icon) for icon in icons[:4])
              if not plate.isNull()]
    if not plates:
        return QPixmap()
    side = defaults.ENCYCLOPEDIA_MOSAIC_PX
    gap = defaults.ENCYCLOPEDIA_MOSAIC_GAP_PX
    canvas = QPixmap(side, side)
    canvas.fill(Qt.GlobalColor.transparent)
    columns = 1 if len(plates) == 1 else 2
    rows = 1 if len(plates) <= 2 else 2
    cell_w = (side - gap * (columns - 1)) // columns
    cell_h = (side - gap * (rows - 1)) // rows
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    for index, plate in enumerate(plates):
        scaled = plate.scaled(
            QSize(cell_w, cell_h),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        column, row = index % columns, index // columns
        box = QRect(
            column * (cell_w + gap), row * (cell_h + gap), cell_w, cell_h,
        )
        painter.drawPixmap(
            box.x() + (cell_w - scaled.width()) // 2,
            box.y() + (cell_h - scaled.height()) // 2,
            scaled,
        )
    painter.end()
    return canvas


class Card(QFrame):
    """One clickable card: plate, title, about, footer stat.

    The ACCENT is its whole's own Rose hue (`config.encyclopedia_tree`):
    a hairline at rest, a lit border and a tinted wash on hover, so the
    reader sees which whole he is inside before he reads a word.
    """

    clicked = Signal(str)

    def __init__(self, key: str, title: str, about: str, plate: QPixmap,
                 footer: str, accent: str):
        super().__init__()
        self._key = key
        self._accent = accent
        self._source = plate
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._image = QLabel()
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image.setStyleSheet("background: transparent; border: none;")
        self._title = QLabel(title)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setWordWrap(True)
        self._title.setStyleSheet(
            f"color: {palette.THEME_COLORS['text_primary']};"
            "font-weight: bold; background: transparent; border: none;"
        )
        self._about = QLabel(about)
        self._about.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._about.setWordWrap(True)
        self._about.setStyleSheet(
            f"color: {palette.THEME_COLORS['text_secondary']};"
            "background: transparent; border: none;"
        )
        self._footer = QLabel(footer)
        self._footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer.setStyleSheet(
            f"color: {accent}; font-weight: bold;"
            "background: transparent; border: none;"
        )
        self._footer.setVisible(bool(footer))

        column = QVBoxLayout(self)
        column.setContentsMargins(
            defaults.ENCYCLOPEDIA_CARD_PAD_PX, defaults.ENCYCLOPEDIA_CARD_PAD_PX,
            defaults.ENCYCLOPEDIA_CARD_PAD_PX, defaults.ENCYCLOPEDIA_CARD_PAD_PX,
        )
        column.setSpacing(defaults.ENCYCLOPEDIA_CARD_PAD_PX // 2)
        column.addWidget(self._image, stretch=1)
        column.addWidget(self._title)
        column.addWidget(self._about)
        column.addWidget(self._footer)
        self._paint(hover=False)

    def _paint(self, hover: bool) -> None:
        tint = QColor(self._accent)
        wash = (
            f"rgba({tint.red()}, {tint.green()}, {tint.blue()}, "
            f"{defaults.ENCYCLOPEDIA_CARD_HOVER_WASH_ALPHA})"
            if hover else palette.THEME_COLORS["surface_1"]
        )
        border = (
            self._accent if hover
            else f"rgba({tint.red()}, {tint.green()}, {tint.blue()}, "
                 f"{defaults.ENCYCLOPEDIA_CARD_EDGE_ALPHA})"
        )
        self.setStyleSheet(
            "QFrame {"
            f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            f" stop:0 {wash}, stop:1 {palette.THEME_COLORS['surface_0']});"
            f"border: {defaults.ENCYCLOPEDIA_CARD_EDGE_PX}px solid {border};"
            f"border-radius: {defaults.ENCYCLOPEDIA_CARD_RADIUS_PX}px; }}"
        )

    def enterEvent(self, event) -> None:      # noqa: N802 — Qt override
        self._paint(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:      # noqa: N802 — Qt override
        self._paint(hover=False)
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event) -> None:   # noqa: N802 — Qt override
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(
            event.position().toPoint()
        ):
            self.clicked.emit(self._key)
        super().mouseReleaseEvent(event)

    def fit(self, width: int, height: int | None, font_px: int) -> None:
        """Size the card and re-fit its plate. `height=None` lets the
        card keep its natural height (the theme grid, which scrolls);
        a given height pins it (the home grid, which may not)."""
        title_font = self._title.font()
        title_font.setPixelSize(font_px + defaults.ENCYCLOPEDIA_CARD_TITLE_BUMP)
        self._title.setFont(title_font)
        for label in (self._about, self._footer):
            font = label.font()
            font.setPixelSize(max(1, font_px - 1))
            label.setFont(font)
        self.setFixedWidth(width)
        inner = width - 2 * defaults.ENCYCLOPEDIA_CARD_PAD_PX
        if height is None:
            image_height = round(inner * defaults.ENCYCLOPEDIA_CARD_IMAGE_RATIO)
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        else:
            self.setFixedHeight(height)
            text_height = (
                self._title.heightForWidth(inner)
                + self._about.heightForWidth(inner)
                + (self._footer.sizeHint().height() if self._footer.isVisible()
                   else 0)
                + defaults.ENCYCLOPEDIA_CARD_PAD_PX * 3
            )
            image_height = max(
                defaults.ENCYCLOPEDIA_CARD_IMAGE_MIN_PX, height - text_height,
            )
        self._image.setFixedHeight(image_height)
        if self._source.isNull():
            return
        self._image.setPixmap(self._source.scaled(
            QSize(inner, image_height),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))


class CardGrid(QWidget):
    """Rows of cards, every row centered as its own block.

    A row holds at most `columns` cards and WRAPS into the next row —
    it never spills sideways, which together with the width-clamped card
    size is the geometric half of the no-X-scroll law.
    """

    opened = Signal(str)

    def __init__(self, columns: int):
        super().__init__()
        self._columns = columns
        self._cards: list[Card] = []
        self._column = QVBoxLayout(self)
        self._column.setContentsMargins(
            defaults.ENCYCLOPEDIA_CARD_GAP_PX, defaults.ENCYCLOPEDIA_CARD_GAP_PX,
            defaults.ENCYCLOPEDIA_CARD_GAP_PX, defaults.ENCYCLOPEDIA_CARD_GAP_PX,
        )
        self._column.setSpacing(defaults.ENCYCLOPEDIA_CARD_GAP_PX)

    @property
    def cards(self) -> list[Card]:
        return self._cards

    def set_cards(self, specs: list[dict]) -> None:
        """Rebuild the grid from `specs` — one dict per card with
        `key`, `title`, `about`, `plate`, `footer`, `accent`."""
        while self._column.count():
            item = self._column.takeAt(0)
            layout = item.layout()
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0).widget()
                    if child is not None:
                        child.setParent(None)
                layout.setParent(None)
            elif item.widget() is not None:
                item.widget().setParent(None)
        self._cards = []
        for start in range(0, len(specs), self._columns):
            row = QHBoxLayout()
            row.setSpacing(defaults.ENCYCLOPEDIA_CARD_GAP_PX)
            row.addStretch(1)
            for spec in specs[start:start + self._columns]:
                card = Card(
                    spec["key"], spec["title"], spec["about"],
                    spec["plate"], spec.get("footer", ""), spec["accent"],
                )
                card.clicked.connect(self.opened)
                row.addWidget(card)
                self._cards.append(card)
            row.addStretch(1)
            self._column.addLayout(row)

    def fit(self, viewport_width: int, viewport_height: int | None,
            zoom: float = 1.0) -> None:
        """Re-measure every card for the viewport. `viewport_height`
        given (the home screen) pins the row height so the grid fits
        without scrolling; None (the theme screen) lets the rows take
        their natural height and scroll."""
        width = card_width_for(viewport_width, self._columns)
        width = max(
            defaults.ENCYCLOPEDIA_CARD_MIN_WIDTH_PX,
            min(round(width * zoom), width),
        )
        font_px = min(
            defaults.ENCYCLOPEDIA_MAX_FONT_PX,
            max(
                defaults.ENCYCLOPEDIA_BASE_FONT_PX,
                round(width * defaults.ENCYCLOPEDIA_CARD_FONT_RATIO * zoom),
            ),
        )
        height = None
        if viewport_height is not None:
            rows = max(1, (len(self._cards) + self._columns - 1) // self._columns)
            gaps = defaults.ENCYCLOPEDIA_CARD_GAP_PX * (rows + 1)
            height = max(
                defaults.ENCYCLOPEDIA_CARD_MIN_HEIGHT_PX,
                (viewport_height - gaps) // rows,
            )
        for card in self._cards:
            card.fit(width, height, font_px)
