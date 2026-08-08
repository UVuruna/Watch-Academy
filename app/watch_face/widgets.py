"""Shared pill/tile builders (see widgets.md) — the functional twin of
`design_window.DesignDialog._pill`/`_tile`, freed of the class so every
Watch Face section module can share ONE definition (Rule #5) instead of
each redefining its own styled button.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QGridLayout, QPushButton, QToolButton

from app.ui_style import style_button
from config import defaults, palette

# The ONE gallery icon size (owner instruction 2026-08-08: every picker
# shows WHAT IT PICKS at a readable size, the Hands gallery being the
# model). It lives in the tile builder itself so no gallery can forget
# it — the defect behind the owner's six screenshots was nine call
# sites each relying on Qt's ~16px default while only Hands set its
# own. Still under `thumbs.THUMB_SOURCE_PX` (256), so every disk-cached
# source stays sharp at this display size.
TILE_ICON_PX = 128


def pack_grid(grid: QGridLayout, columns: int) -> QGridLayout:
    """Left-pack a gallery grid: the trailing stretch column takes the
    window's surplus, so the tiles keep their own size and a modest gap
    instead of drifting apart with every extra pixel (the owner's
    2026-08-06 screenshots — tiles scattered across a 4K window)."""
    grid.setHorizontalSpacing(defaults.GUIDE_SPACING_PX)
    grid.setVerticalSpacing(defaults.GUIDE_SPACING_PX)
    grid.setColumnStretch(columns, 1)
    return grid


def pill(label: str, checked: bool, on_click) -> QPushButton:
    button = QPushButton(label)
    style_button(button, "next" if checked else "neutral", small=True)
    button.clicked.connect(lambda checked=False: on_click())
    return button


def tile(label: str, icon: QIcon | None, checked: bool, on_click) -> QToolButton:
    """A gallery tile. Unlike `design_window._tile`, `icon` is an
    already-built `QIcon` (the caller resolves it, typically through
    `thumbs.py`'s disk-cached service) rather than a raw `Path` — the
    tile builder itself does no file I/O. A tile with no icon reserves
    the SAME icon box, transparently empty (uniform siblings, GUI Rules
    ALG-5): an honest blank field, never a shrunken tile beside full
    ones — and never invented stand-in art."""
    button = QToolButton()
    button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    button.setText(label)
    if icon is None:
        placeholder = QPixmap(TILE_ICON_PX, TILE_ICON_PX)
        placeholder.fill(Qt.GlobalColor.transparent)
        icon = QIcon(placeholder)
    button.setIcon(icon)
    button.setIconSize(QSize(TILE_ICON_PX, TILE_ICON_PX))
    if checked:
        button.setStyleSheet(
            f"border: 2px solid {palette.THEME_COLORS['accent']};"
            "border-radius: 8px;"
        )
    button.clicked.connect(lambda checked=False: on_click())
    return button
