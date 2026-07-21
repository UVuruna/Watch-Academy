"""Fast Travel's transient flash overlay (R5b FINAL MAP round, owner
spec sealed 2026-07-21): icon + option text, popping above the dial on
every Ctrl+[ / Ctrl+] theme/option change and fading out on its own.
"""

from PySide6.QtCore import QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from app import native
from config import defaults


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
        self._text_label.setStyleSheet(
            f"color: {defaults.FAST_TRAVEL_FLASH_TEXT_COLOR};"
            f"font-weight: 600; font-size: {defaults.FAST_TRAVEL_FLASH_FONT_PX}px;"
        )
        layout = QHBoxLayout(self)
        pad = defaults.FAST_TRAVEL_FLASH_PADDING_PX
        layout.setContentsMargins(pad, pad, pad, pad)
        layout.setSpacing(8)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)
        self.setStyleSheet(
            f"FastTravelFlash {{ background: {defaults.FAST_TRAVEL_FLASH_BG}; "
            f"border-radius: {defaults.FAST_TRAVEL_FLASH_RADIUS_PX}px; }}"
        )
        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(defaults.FAST_TRAVEL_FLASH_FADE_MS)
        self._fade.setStartValue(1.0)
        self._fade.setEndValue(0.0)
        self._fade.finished.connect(self.hide)
        self._hold_timer = QTimer(self)
        self._hold_timer.setSingleShot(True)
        self._hold_timer.timeout.connect(self._fade.start)

    def flash(self, dial_widget: QWidget, icon_path, emoji: str, text: str) -> None:
        """Show `text` beside `icon_path` (graceful-absent to `emoji` —
        Rule #1) positioned ABOVE `dial_widget`'s current geometry,
        falling BELOW it when the dial hugs the screen top, then holds
        before fading. A flash already in flight restarts cleanly."""
        self._fade.stop()
        self._hold_timer.stop()
        self._opacity.setOpacity(1.0)
        if icon_path is not None:
            size = defaults.FAST_TRAVEL_FLASH_ICON_PX
            self._icon_label.setPixmap(QIcon(str(icon_path)).pixmap(size, size))
            self._icon_label.setText("")
        else:
            self._icon_label.setPixmap(QIcon().pixmap(0, 0))
            self._icon_label.setText(emoji)
            self._icon_label.setStyleSheet(
                f"font-size: {defaults.FAST_TRAVEL_FLASH_ICON_PX}px;"
            )
        self._text_label.setText(text)
        self.adjustSize()
        self._position_above_or_below(dial_widget)
        self.show()
        native.assert_topmost(int(self.winId()))
        hold_ms = max(
            0,
            round(
                defaults.FAST_TRAVEL_FLASH_DURATION_S * 1000
                - defaults.FAST_TRAVEL_FLASH_FADE_MS
            ),
        )
        self._hold_timer.start(hold_ms)

    def _position_above_or_below(self, dial_widget: QWidget) -> None:
        dial_geo = dial_widget.frameGeometry()
        x = dial_geo.center().x() - self.width() // 2
        gap = defaults.FAST_TRAVEL_FLASH_GAP_PX
        above_y = dial_geo.top() - self.height() - gap
        screen = dial_widget.screen() or QGuiApplication.primaryScreen()
        avail = screen.availableGeometry()
        if above_y < avail.top():
            y = dial_geo.bottom() + gap        # falls below instead
        else:
            y = above_y
        self.move(max(avail.left(), min(x, avail.right() - self.width())), y)
