"""The transparent desktop clock window.

All window flags/attributes are set in __init__, BEFORE the first show()
— changing them later re-parents and hides the window on Windows.
Painting is delegated to the render compositor; the widget itself knows
nothing about the dial.
"""

from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMenu, QWidget

from config import constants, defaults


class ClockWidget(QWidget):
    """Frameless, per-pixel-transparent, always-at-bottom dial window."""

    moved = Signal()

    def __init__(self, diameter: int, menu: QMenu):
        super().__init__()
        self._closing = False
        self._menu = menu
        self._renderer = None
        self._tick = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnBottomHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowTitle(constants.APP_NAME)
        self.resize(diameter, diameter)

    def mark_closing(self) -> None:
        """Tell the spontaneous-hide watchdog that the coming hide is
        intentional."""
        self._closing = True

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

    def contextMenuEvent(self, event) -> None:
        self._menu.exec(event.globalPos())

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        self.moved.emit()

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
