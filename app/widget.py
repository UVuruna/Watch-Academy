"""The transparent desktop clock window.

All window flags/attributes are set in __init__, BEFORE the first show()
— changing them later re-parents and hides the window on Windows.
Painting is delegated to the render compositor; the widget itself knows
nothing about the dial.
"""

from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMenu, QWidget

from app import native
from config import constants, defaults, winapi


class ClockWidget(QWidget):
    """Frameless, per-pixel-transparent, always-at-bottom dial window."""

    moved = Signal()

    def __init__(self, diameter: int, menu: QMenu, legend):
        super().__init__()
        self._closing = False
        self._menu = menu
        self._legend = legend           # the shared LegendPopup
        self._renderer = None
        self._tick = None
        self._click_through = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnBottomHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowTitle(constants.APP_NAME)
        self.setMouseTracking(True)     # hover tooltips on small dials
        self.resize(diameter, diameter)

    def mark_closing(self) -> None:
        """Tell the spontaneous-hide watchdog that the coming hide is
        intentional."""
        self._closing = True

    def set_click_through(self, enabled: bool) -> None:
        """TRUE click-through: the whole window stops taking mouse input
        (left and right clicks and system hover all pass to whatever lies
        beneath). Recovery is via the tray; hover tooltips come from the
        controller's cursor poller while the mode is on."""
        self._click_through = enabled
        native.set_click_through(int(self.winId()), enabled)

    # --- Rendering --------------------------------------------------------------

    def set_renderer(self, renderer) -> None:
        """The compositor: paint(painter, size, dpr, tick)."""
        self._renderer = renderer

    def set_tick(self, tick) -> None:
        self._tick = tick
        self.update()

    def paintEvent(self, event) -> None:
        if self._renderer is None or self._tick is None:
            # Documented startup order: the controller delivers the first
            # tick before show(), so this only covers stray early paints.
            return
        painter = QPainter(self)
        self._renderer.paint(
            painter,
            float(min(self.width(), self.height())),
            self.devicePixelRatioF(),
            self._tick,
        )

    # --- Input ----------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            # Native OS move: correct across monitors and DPI changes.
            self.windowHandle().startSystemMove()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._renderer is not None and self._tick is not None:
            size = float(min(self.width(), self.height()))
            if self._renderer.set_hover(
                event.position().x(), event.position().y(), size
            ):
                self.update()           # hover-enlarge target changed
            tip = self._renderer.tooltip_at(
                event.position().x(),
                event.position().y(),
                size,
            )
            if tip:
                self._legend.show_html(tip, event.globalPosition().toPoint())
            else:
                self._legend.dismiss()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        if self._renderer is not None and self._renderer.set_hover(
            -1.0e9, -1.0e9, float(min(self.width(), self.height()))
        ):
            self.update()               # shrink the enlarged element back
        # Crossing INTO the legend popup must not close it — the wheel
        # scrolls the article there; its own leaveEvent hides it.
        self._legend.hide_unless_hovered()
        super().leaveEvent(event)

    def contextMenuEvent(self, event) -> None:
        self._menu.exec(event.globalPos())

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self.moved.emit()

    def nativeEvent(self, event_type, message):
        """Clicks outside the dial's inscribed circle fall through to
        whatever lies beneath — the square window corners are not ours.
        (In click-through mode WS_EX_TRANSPARENT bypasses hit testing
        altogether, so this only matters in normal mode.)"""
        if event_type == b"windows_generic_MSG" and native.nchittest_falls_outside(
            int(message)
        ):
            return True, winapi.HTTRANSPARENT
        return super().nativeEvent(event_type, message)

    # --- Spontaneous-hide watchdog ----------------------------------------------
    # An OS-initiated hide/minimize we did not request is undone after a
    # short delay. Verified on Windows 11 24H2: Win+D does NOT trigger these
    # events (it covers the window with the raised desktop layer instead and
    # restores it when Show Desktop mode ends) — this guard covers the other
    # shell actions that genuinely hide or minimize the window.

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        if event.spontaneous() and not self._closing:
            QTimer.singleShot(defaults.WATCHDOG_RESHOW_MS, self._reshow)

    def changeEvent(self, event) -> None:
        if (
            event.type() == QEvent.Type.WindowStateChange
            and self.isMinimized()
            and not self._closing
        ):
            QTimer.singleShot(defaults.WATCHDOG_RESHOW_MS, self.showNormal)
        super().changeEvent(event)

    def _reshow(self) -> None:
        if not self._closing:
            self.show()
