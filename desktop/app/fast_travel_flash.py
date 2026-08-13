"""Fast Travel's transient flash overlay (R5b FINAL MAP round, owner
spec sealed 2026-07-21): icon + option text, popping above the dial on
every Ctrl+[ / Ctrl+] theme/option change and fading out on its own.

R-30 (2026-08) reuses this SAME overlay for a LOCATION change, and the
owner's order of 2026-08-12 finished the merge: a location no longer
gets a big white font across the MIDDLE of the dial, but the same plate
letters at the same place above it, with its own logo beside — the poles
their compass roses, Greenwich the plain one Time Travel already uses.
One mechanism, ONE position, one look.
"""

import sys

from PySide6.QtCore import QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from app import native
from config import palette, shortcuts


class FastTravelFlash(QWidget):
    """One per watch (owner spec: "per-watch — the focused watch
    flashes its own"). Mirrors [Legend Popup](legend_popup.md)'s own
    non-focus-stealing topmost window recipe (ToolTip | Frameless |
    WindowStaysOnTopHint, WA_ShowWithoutActivating, native.assert_topmost
    on every show) — necessary here because every Fast Travel shortcut
    needs the DIAL to keep holding keyboard focus for the next press."""

    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._icon_label = QLabel()
        self._text_label = QLabel()
        layout = QHBoxLayout(self)
        pad = shortcuts.FAST_TRAVEL_FLASH_PADDING_PX
        layout.setContentsMargins(pad, pad, pad, pad)
        layout.setSpacing(8)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)
        self.setStyleSheet(
            f"FastTravelFlash {{ background: {palette.FAST_TRAVEL_FLASH_BG}; "
            f"border-radius: {shortcuts.FAST_TRAVEL_FLASH_RADIUS_PX}px; }}"
        )
        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(shortcuts.FAST_TRAVEL_FLASH_FADE_MS)
        self._fade.setStartValue(1.0)
        self._fade.setEndValue(0.0)
        self._fade.finished.connect(self.hide)
        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._fade.start)

    def flash(
        self, dial_widget: QWidget, icon_path, emoji: str, text: str,
    ) -> None:
        """Show `text` beside `icon_path` (graceful-absent to `emoji` —
        Rule #1) positioned ABOVE `dial_widget`'s current geometry,
        falling BELOW it when the dial hugs the screen top, then holds
        before fading. A flash already in flight restarts cleanly.

        ONE FLASH, ONE PLACE (owner order 2026-08-12): a LOCATION change
        used to take a second look entirely — big white font letters
        across the MIDDLE of the dial, no icon. His correction: "that
        FLASH which writes North Pole, Greenwich and so on when the
        location changes should be written ABOVE, where this switcher
        with Ctrl+[ is, and in the theme's letters with a logo beside
        it". lang-ok: the owner's own sentence, the rule this is. So
        `big` is gone with `_position_centered` and the font path: every
        flash this widget shows is now plates, an icon and one position.

        The two-metal accent survives the merge: whatever separates the
        two halves — the Fast Travel picker's " : " or a location's
        "CITY, COUNTRY" — the first half wears GOLD at full height and
        the second SILVER a step smaller. Only the picker DRAWS its
        separator (the colon plate); a comma has no plate and needs
        none, since the metal change already says "second half"."""
        self._fade.stop()
        self._hold_timer.stop()
        self._opacity.setOpacity(1.0)
        has_icon = icon_path is not None or bool(emoji)
        self._icon_label.setVisible(has_icon)
        if icon_path is not None:
            self._icon_label.setPixmap(self._icon_pixmap(icon_path))
            self._icon_label.setText("")
        elif emoji:
            self._icon_label.setPixmap(QIcon().pixmap(0, 0))
            self._icon_label.setText(emoji)
            self._icon_label.setStyleSheet(
                f"font-size: {shortcuts.FAST_TRAVEL_FLASH_ICON_PX}px;"
            )
        self._set_plate_text(text)
        self.adjustSize()
        self._position_above_or_below(dial_widget)
        self.show()
        native.assert_topmost(int(self.winId()))
        hold_ms = max(
            0,
            round(
                shortcuts.FAST_TRAVEL_FLASH_DURATION_S * 1000
                - shortcuts.FAST_TRAVEL_FLASH_FADE_MS
            ),
        )
        self._hold_timer.start(hold_ms)

    def _icon_pixmap(self, icon_path) -> QPixmap:
        """The flash's icon at a LOGICAL size of exactly
        `FAST_TRAVEL_FLASH_ICON_PX`, whatever the source and whatever the
        screen's scaling.

        ONE SIZE, ONE PLACE — the owner's drift report of 2026-08-13: as
        he cycles the category with Ctrl+[, the label seems to shift
        slightly and to change size, instead of always standing at the
        same distance from the dial circle in the same size.

        MEASURED before it was believed: on his 125 % display the flash
        box stood 48 px tall for Solar Eclipse / Date / Time and 42 px
        for the other three, and since the box is anchored by its BOTTOM
        edge above the dial, its text jumped 3 px between categories.

        The mechanism was `QIcon.pixmap()`'s DPI awareness meeting
        `QPixmap.scaled()`'s DEVICE pixels. A source that can supply any
        size — the SVGs, a raster larger than the request — hands back
        `n * dpr` device pixels ALREADY carrying `devicePixelRatio =
        dpr`; the two COMPUTED icons are drawn at exactly
        `SUPERSAMPLE * ICON_PX` px, so QIcon can only return that many
        at a dpr of 1. `scaled(28, 28)` then means 28 DEVICE pixels for
        both and PRESERVES each source's dpr, so the same call produced
        22.4 logical px for one family and 28.0 for the other — a 6 px
        box difference, and an icon a quarter smaller, which is the
        other half of what he saw. At 100 % scaling the bug is
        invisible, which is why it shipped.

        So the size is decided HERE, in device pixels we compute
        ourselves, and the ratio is stamped on the result. The
        aspect-preserved image is then centred on a SQUARE canvas, so
        the label's box is `ICON_PX` even for art that is not square —
        the position follows the declared metric, never the ink.

        RASTERIZE BIG, THEN SHRINK survives
        (`FAST_TRAVEL_FLASH_ICON_SUPERSAMPLE`): asked for the final size
        directly, Qt renders a vector's fine detail below one pixel and
        the glyph collapses."""
        size = shortcuts.FAST_TRAVEL_FLASH_ICON_PX
        over = shortcuts.FAST_TRAVEL_FLASH_ICON_SUPERSAMPLE
        dpr = self.devicePixelRatioF() or 1.0
        device = max(1, round(size * dpr))
        drawn = QIcon(str(icon_path)).pixmap(over * device, over * device).scaled(
            device, device,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        canvas = QPixmap(device, device)
        canvas.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas)
        try:
            painter.drawPixmap(
                (device - drawn.width()) // 2,
                (device - drawn.height()) // 2,
                drawn,
            )
        finally:
            painter.end()
        canvas.setDevicePixelRatio(dpr)
        return canvas

    def _set_plate_text(self, text: str) -> None:
        """THE ONE PLATE LAW reaches this text (owner corrections
        2026-08-11: the SAME letter plates the jewels and the crown text
        wear, never a white font — a white font vanishes on a white
        desktop). The CATEGORY/CITY wears gold at full height, the
        OPTION/COUNTRY silver a step smaller.

        THE LORD'S DAY PRECEDENT: a glyph with no plate does not kill a
        keystroke here. The picker's own titles are plate-safe by
        construction, but a location carries whatever the world calls
        itself, and the library owns no accented masters today.
        # lang-ok: place names quoted as data, not product text.
        ("Nis", "Zurich" and their real spellings are the cases meant.)
        Rather than raise on a legitimate place name, the flash falls
        back to the styled font FOR THAT ONE TEXT and names the offending
        character on stderr, exactly as the weekday labels do for the
        apostrophe. The fallback is loud and per-string, never a silent
        standing font path."""
        from render.letter_plates import MissingPlate, plate_text_segments_pixmap

        for separator in (" : ", ", "):
            head, found, tail = text.partition(separator)
            if found:
                segments = (
                    (head, "gold", 1.0),
                    # The picker DRAWS its colon; a comma has no plate
                    # and needs none — the metal change is the seam.
                    (f": {tail}" if separator == " : " else tail, "silver", 0.82),
                )
                break
        else:
            segments = ((text, "gold", 1.0),)
        try:
            pixmap = plate_text_segments_pixmap(
                segments, shortcuts.FAST_TRAVEL_FLASH_FONT_PX,
                dpr=self.devicePixelRatioF() or 1.0,
            )
        except MissingPlate as missing:
            print(f"flash text falls back to the font: {missing}", file=sys.stderr)
            self._text_label.setPixmap(QPixmap())
            self._text_label.setStyleSheet(
                f"color: {palette.FAST_TRAVEL_FLASH_TEXT_COLOR};"
                f"font-weight: 600; "
                f"font-size: {shortcuts.FAST_TRAVEL_FLASH_FONT_PX}px;"
            )
            self._text_label.setText(text)
            return
        self._text_label.setText("")
        self._text_label.setPixmap(pixmap)

    def _position_above_or_below(self, dial_widget: QWidget) -> None:
        dial_geo = dial_widget.frameGeometry()
        x = dial_geo.center().x() - self.width() // 2
        gap = shortcuts.FAST_TRAVEL_FLASH_GAP_PX
        above_y = dial_geo.top() - self.height() - gap
        screen = dial_widget.screen() or QGuiApplication.primaryScreen()
        avail = screen.availableGeometry()
        if above_y < avail.top():
            y = dial_geo.bottom() + gap        # falls below instead
        else:
            y = above_y
        self.move(max(avail.left(), min(x, avail.right() - self.width())), y)

