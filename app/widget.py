"""The transparent desktop clock window.

All window flags/attributes are set in __init__, BEFORE the first show()
— changing them later re-parents and hides the window on Windows.
"""

from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPolygonF
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtWidgets import QMenu, QWidget

from config import constants, defaults


class ClockWidget(QWidget):
    """Frameless, per-pixel-transparent, always-at-bottom dial window."""

    moved = Signal()

    def __init__(self, diameter: int, menu: QMenu):
        super().__init__()
        self._closing = False
        self._menu = menu

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
        """Tell the Win+D watchdog that the coming hide is intentional."""
        self._closing = True

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

    # --- Painting (M1 placeholder — replaced by render/ in M3) -----------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height())
        margin = defaults.PLACEHOLDER_RING_MARGIN
        dial = QRectF(margin, margin, side - 2 * margin, side - 2 * margin)
        center = dial.center()

        # Translucent disc
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*defaults.PLACEHOLDER_DISC_RGBA))
        painter.drawEllipse(dial)

        # Outer ring
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QColor(*defaults.PLACEHOLDER_RING_RGBA))
        pen = painter.pen()
        pen.setWidthF(defaults.PLACEHOLDER_RING_WIDTH)
        painter.setPen(pen)
        painter.drawEllipse(dial)

        # Noon marker: small triangle at the top (12:00 position)
        mark = side * defaults.PLACEHOLDER_NOON_MARK_SIZE
        top = QPointF(center.x(), dial.top())
        triangle = QPolygonF(
            [
                QPointF(top.x() - mark / 2, top.y()),
                QPointF(top.x() + mark / 2, top.y()),
                QPointF(top.x(), top.y() + mark),
            ]
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(*defaults.PLACEHOLDER_NOON_MARK_RGBA))
        painter.drawPolygon(triangle)

        # Center dot
        dot = side * defaults.PLACEHOLDER_CENTER_DOT_SIZE
        painter.setBrush(QColor(*defaults.PLACEHOLDER_CENTER_DOT_RGBA))
        painter.drawEllipse(center, dot, dot)

        # Faint wordmark
        font = QFont()
        font.setPixelSize(int(side * defaults.PLACEHOLDER_TEXT_SIZE))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(*defaults.PLACEHOLDER_TEXT_RGBA))
        text_rect = QRectF(
            dial.left(),
            center.y() + side * defaults.PLACEHOLDER_TEXT_OFFSET_Y,
            dial.width(),
            side * defaults.PLACEHOLDER_TEXT_RECT_HEIGHT,
        )
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter, defaults.PLACEHOLDER_TEXT)
