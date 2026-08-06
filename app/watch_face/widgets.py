"""Shared pill/tile builders (see widgets.md) — the functional twin of
`design_window.DesignDialog._pill`/`_tile`, freed of the class so every
Watch Face section module can share ONE definition (Rule #5) instead of
each redefining its own styled button.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QGridLayout, QPushButton, QToolButton

from app.ui_style import style_button
from config import defaults, palette


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
    tile builder itself does no file I/O."""
    button = QToolButton()
    button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    button.setText(label)
    if icon is not None:
        button.setIcon(icon)
    if checked:
        button.setStyleSheet(
            f"border: 2px solid {palette.THEME_COLORS['accent']};"
            "border-radius: 8px;"
        )
    button.clicked.connect(lambda checked=False: on_click())
    return button
