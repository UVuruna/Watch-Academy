"""System tray icon.

Keeps strong Python references to the icon and menu — Qt does not own
them and the GC would otherwise destroy the menu mid-use.
"""

from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from config import constants, defaults
from render.asset_recolor import tinted_pixmap


def _rasterize_logo(size: int, asset: Path = defaults.LOGO_ASSET) -> QPixmap:
    """`asset` rasterized to `size` px, aspect kept and centered — the
    shared rasterizer behind the tray icon and the multi-resolution
    window icon. `asset` defaults to the owner's gold watch
    (assets/logo.svg); ADD WATCH round's `logo_icon(watch_index)`
    passes the rose-gold master for watch 2. A missing/broken logo
    must be visible — callers propagate the ValueError instead of
    showing an empty/generic icon."""
    renderer = QSvgRenderer(str(asset))
    if not renderer.isValid():
        raise ValueError(f"cannot load the app logo: {asset}")
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
    return pixmap


def _logo_asset(watch_index: int) -> Path:
    """The MASTER a watch's tray icon rasterizes from (ADD WATCH round,
    owner INSTRUCTION.txt item 2B): watch 2 is the pre-existing
    rose-gold master (`logo-setup.svg`, a second master — not a
    recolor); every other watch (1, and 3+ before their wheel tint
    below) rasterizes the plain gold master."""
    return defaults.LOGO_SETUP_ASSET if watch_index == 2 else defaults.LOGO_ASSET


def _tray_tint(watch_index: int) -> str | None:
    """The RECOLOR hex for a watch's tray icon, by its own ORDER (owner
    INSTRUCTION.txt item 2B): `None` for watch 1 (gold as-is) and watch
    2 (its own rose-gold MASTER, not a recolor — see `_logo_asset`);
    watch 3+ cycle `defaults.TRAY_COLOR_WHEEL` forever (Rule #19 —
    computed, never a new generated icon)."""
    if watch_index <= 2:
        return None
    wheel = defaults.TRAY_COLOR_WHEEL
    return wheel[(watch_index - 3) % len(wheel)]


def logo_icon(watch_index: int = 1) -> QIcon:
    """The TRAY icon for `watch_index` (1-based, default watch 1) — ONE
    fixed size, the tray never asks for another. See `_logo_asset`/
    `_tray_tint`'s own docstrings for the ADD WATCH round's per-watch
    identity rule (golden, rose-gold, then the color wheel)."""
    pixmap = _rasterize_logo(defaults.TRAY_ICON_SIZE, _logo_asset(watch_index))
    tint = _tray_tint(watch_index)
    return QIcon(pixmap if tint is None else tinted_pixmap(pixmap, tint))


def window_icon() -> QIcon:
    """The app-wide WINDOW icon (owner screenshot 2026-07-20): every
    dialog title bar, Alt-Tab thumbnail and taskbar button wears this —
    MULTIPLE resolutions in one QIcon, so Windows picks the sharpest
    match for each context instead of blurrily scaling a single size (a
    single-size icon was part of why Settings/Time Travel/Guide/
    Encyclopedia/Observatory windows fell back to python.exe's own
    logo in the taskbar; `native.set_app_user_model_id` fixes the other
    half — the process identity itself)."""
    icon = QIcon()
    for size in defaults.WINDOW_ICON_SIZES_PX:
        icon.addPixmap(_rasterize_logo(size))
    return icon


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

    def set_tooltip(self, text: str) -> None:
        """The tray icon HOVER tooltip (owner INSTRUCTION.txt item 2A,
        R5 MENU REWORK): carries the watch's FULL name form — unlike
        the menu's own TITLE row, which stays short (just the location)
        until more than one watch exists."""
        self._icon.setToolTip(text)

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
