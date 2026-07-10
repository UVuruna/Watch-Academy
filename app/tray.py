"""System tray icon.

Keeps strong Python references to the icon and menu — Qt does not own
them and the GC would otherwise destroy the menu mid-use.
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from config import constants, defaults


def _draw_tray_icon() -> QIcon:
    """The owner's gold watch (assets/logo.svg) rasterized to the tray
    size, aspect kept and centered. A missing/broken logo must be
    visible — the app raises instead of showing an empty tray."""
    renderer = QSvgRenderer(str(defaults.LOGO_ASSET))
    if not renderer.isValid():
        raise ValueError(f"cannot load the tray logo: {defaults.LOGO_ASSET}")
    size = defaults.TRAY_ICON_SIZE
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    design = renderer.defaultSize()
    scale = size / max(design.width(), design.height())
    width, height = design.width() * scale, design.height() * scale
    renderer.render(
        painter, QRectF((size - width) / 2, (size - height) / 2, width, height)
    )
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
