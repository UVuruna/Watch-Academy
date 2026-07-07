"""System tray icon.

Keeps strong Python references to the icon and menu — Qt does not own
them and the GC would otherwise destroy the menu mid-use.
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from config import constants, defaults


def _draw_tray_icon() -> QIcon:
    """Procedural stand-in until assets/logo.svg exists (M7)."""
    size = defaults.TRAY_ICON_SIZE
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    rect = QRectF(pixmap.rect())
    margin = size * defaults.TRAY_ICON_MARGIN
    dial = rect.adjusted(margin, margin, -margin, -margin)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(*defaults.TRAY_DISC_RGB))
    painter.drawEllipse(dial)
    painter.setBrush(QColor(*defaults.TRAY_MARK_RGB))
    noon = size * defaults.TRAY_MARK_SIZE
    painter.drawEllipse(QRectF(rect.center().x() - noon / 2, dial.top(), noon, noon))
    painter.end()
    return QIcon(pixmap)


class TrayController:
    def __init__(self, menu: QMenu):
        self._menu = menu
        self._icon = QSystemTrayIcon(_draw_tray_icon())
        self._icon.setToolTip(constants.APP_NAME)
        self._icon.setContextMenu(menu)

    def show(self) -> None:
        self._icon.show()

    def hide(self) -> None:
        self._icon.hide()

    def notify(self, title: str, message: str) -> None:
        """Non-blocking error balloon (used for mid-run save failures)."""
        self._icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Critical)
