"""System tray icon.

Keeps strong Python references to the icon and menu — Qt does not own
them and the GC would otherwise destroy the menu mid-use.
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from config import constants, defaults


def logo_icon() -> QIcon:
    """The owner's gold watch (assets/logo.svg) rasterized to the tray
    size, aspect kept and centered — the ONE app face: the tray and the
    app-wide window icon (dialog title bars) both wear it; the built
    EXE additionally embeds the M7 ICO. A missing/broken logo must be
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
    def __init__(self, menu: QMenu, icon: QIcon):
        self._menu = menu
        self._icon = QSystemTrayIcon(icon)
        self._icon.setToolTip(constants.APP_NAME)
        self._icon.setContextMenu(menu)

    def set_menu(self, menu: QMenu) -> None:
        """Swap the context menu (rebuilt after Settings)."""
        self._menu = menu
        self._icon.setContextMenu(menu)

    def on_double_click(self, callback) -> None:
        """Wire `callback()` to a tray icon DOUBLE-CLICK (owner
        2026-07-18, ROADMAP 15h — the "Show" affordance's second
        trigger, beside the menu entry). The caller decides whether the
        gesture means anything right now (it is a no-op outside
        "normal" z-mode) — this is just the Qt activation-reason
        plumbing."""
        def on_activated(reason: QSystemTrayIcon.ActivationReason) -> None:
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                callback()

        self._icon.activated.connect(on_activated)

    def show(self) -> None:
        self._icon.show()

    def hide(self) -> None:
        self._icon.hide()

    def notify(self, title: str, message: str, critical: bool = True) -> None:
        """Non-blocking balloon: errors by default, `critical=False`
        for progress notes (e.g. background translation)."""
        icon = (
            QSystemTrayIcon.MessageIcon.Critical
            if critical
            else QSystemTrayIcon.MessageIcon.Information
        )
        self._icon.showMessage(title, message, icon)
