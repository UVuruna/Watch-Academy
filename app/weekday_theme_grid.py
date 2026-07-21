"""A reusable image+name picker for the weekday body themes — R5 MENU
REWORK (owner spec: "u lepsem vecem meniju sa slikama i tekstom"),
shared by the Pointer Theme and Slot Theme windows (Rule #5) instead of
each holding its own copy of the Weekday submenu's kinship-grouped
layout.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from config import defaults, paths

_MAX_COLUMNS = 4


def build_weekday_theme_grid(current_theme: str, on_pick, tr) -> QScrollArea:
    """A scrollable gallery of every weekday theme, Planets flat first
    then the kinship groups (`defaults.WEEKDAY_MENU_TOP` /
    `WEEKDAY_MENU_GROUPS` — the SAME order/grouping the old Weekday
    submenu used). `on_pick(theme_key)` fires on a tile click; the
    CURRENTLY active theme's tile carries an accent border."""
    content = QWidget()
    column = QVBoxLayout(content)
    column.setSpacing(12)

    def add_group(title: str | None, keys: tuple[str, ...]) -> None:
        if title is not None:
            header = QLabel(tr(title))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setStyleSheet("font-weight: 700; font-size: 13px;")
            column.addWidget(header)
            rule = QFrame()
            rule.setFrameShape(QFrame.Shape.HLine)
            rule.setFrameShadow(QFrame.Shadow.Sunken)
            column.addWidget(rule)
        grid = QGridLayout()
        grid.setSpacing(14)
        for index, key in enumerate(keys):
            tile = QToolButton()
            tile.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            tile.setText(tr(defaults.WEEKDAY_THEME_TITLES[key]))
            icon_path = paths.art_file(defaults.weekday_theme_body_art(key, "sun"))
            if icon_path is not None and Path(icon_path).exists():
                tile.setIcon(QIcon(str(icon_path)))
            if key == current_theme:
                tile.setStyleSheet(
                    f"border: 2px solid {defaults.THEME_COLORS['accent']};"
                    "border-radius: 8px;"
                )
            tile.clicked.connect(lambda checked=False, k=key: on_pick(k))
            row, col = divmod(index, _MAX_COLUMNS)
            grid.addWidget(tile, row, col)
        wrap = QHBoxLayout()
        wrap.addStretch(1)
        wrap.addLayout(grid)
        wrap.addStretch(1)
        column.addLayout(wrap)

    add_group(None, defaults.WEEKDAY_MENU_TOP)
    for group_title, keys in defaults.WEEKDAY_MENU_GROUPS:
        add_group(group_title, keys)
    column.addStretch(1)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content)
    return scroll
