"""Reusable image+name pickers — R5 MENU REWORK (owner spec: "u lepsem
vecem meniju sa slikama i tekstom"), shared by the Pointer Theme and
Slot Theme windows (Rule #5) instead of each holding its own copy of a
gallery layout.

Two galleries live here, both built from the SAME tile/section
primitives: the weekday BODY themes (kinship-grouped) and — since the
Pointers REWORK phase 2, owner decree 2026-07-29 — the CALENDAR MOUNT,
the roster that rides the Calendar pointer's twelve wedges. The mount
moved here out of the Design window's Pointer tab because it is a
CONTENT choice (a roster, with art, needing a gallery), and content is
picked in these windows; the Design tab keeps shape alone.
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

from config import calendar_mounts, defaults, palette, pantheon, paths

_MAX_COLUMNS = 4


def _tile(label: str, icon_path, selected: bool, on_click) -> QToolButton:
    """One gallery tile — image over name, an accent border when it is
    the active choice. The ONE tile builder both galleries use."""
    button = QToolButton()
    button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    button.setText(label)
    if icon_path is not None and Path(icon_path).exists():
        button.setIcon(QIcon(str(icon_path)))
    if selected:
        button.setStyleSheet(
            f"border: 2px solid {palette.THEME_COLORS['accent']};"
            "border-radius: 8px;"
        )
    button.clicked.connect(lambda checked=False: on_click())
    return button


def _add_section(column: QVBoxLayout, title: str | None, tiles: list) -> None:
    """A labeled, centered, wrapped row of tiles — the ONE section
    builder both galleries use (`title` None = no header/rule)."""
    if title is not None:
        header = QLabel(title)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-weight: 700; font-size: 13px;")
        column.addWidget(header)
        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setFrameShadow(QFrame.Shadow.Sunken)
        column.addWidget(rule)
    grid = QGridLayout()
    grid.setSpacing(14)
    for index, tile in enumerate(tiles):
        row, col = divmod(index, _MAX_COLUMNS)
        grid.addWidget(tile, row, col)
    wrap = QHBoxLayout()
    wrap.addStretch(1)
    wrap.addLayout(grid)
    wrap.addStretch(1)
    column.addLayout(wrap)


def _scrollable(content: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content)
    return scroll


def build_weekday_theme_grid(current_theme: str, on_pick, tr) -> QScrollArea:
    """A scrollable gallery of every weekday theme, Planets flat first
    then the kinship groups (`pantheon.WEEKDAY_MENU_TOP` /
    `WEEKDAY_MENU_GROUPS` — the SAME order/grouping the old Weekday
    submenu used). `on_pick(theme_key)` fires on a tile click; the
    CURRENTLY active theme's tile carries an accent border."""
    content = QWidget()
    column = QVBoxLayout(content)
    column.setSpacing(12)

    def add_group(title: str | None, keys: tuple[str, ...]) -> None:
        _add_section(column, tr(title) if title is not None else None, [
            _tile(
                tr(pantheon.WEEKDAY_THEME_TITLES[key]),
                paths.art_file(pantheon.weekday_theme_body_art(key, "sun")),
                key == current_theme,
                lambda k=key: on_pick(k),
            )
            for key in keys
        ])

    add_group(None, pantheon.WEEKDAY_MENU_TOP)
    for group_title, keys in pantheon.WEEKDAY_MENU_GROUPS:
        add_group(group_title, keys)
    column.addStretch(1)
    return _scrollable(content)


def build_calendar_mount_grid(current_mount: str, on_pick, tr) -> QScrollArea:
    """A scrollable gallery of every roster that may ride the Calendar
    pointer's twelve wedges (owner decree 2026-07-29 — the choice moved
    here from the Design window's Pointer tab).

    The offer is `calendar_mounts.CALENDAR_MOUNTS` and nothing else, so
    registering a roster there puts it on this screen with no edit here
    (Rule #5). Each tile previews the roster with its OWN first member's
    plate — the crown of a System B wheel, the opening sign of a System
    A one — and says how many seats it fills, because the seat count is
    the reader's own question ("does this fill one per wedge or two?").
    "None" leads, the way "off" leads the setting's own value list."""
    content = QWidget()
    column = QVBoxLayout(content)
    column.setSpacing(12)
    tiles = [_tile(
        tr("None"), None, current_mount == "off", lambda: on_pick("off"),
    )]
    for key, mount in calendar_mounts.CALENDAR_MOUNTS.items():
        preview = paths.art_file(
            defaults.ZODIAC_ART_DIR / mount.art_dir / f"{mount.stems[0]}.png"
        )
        tiles.append(_tile(
            f"{tr(mount.title)} ({mount.seats})",
            preview if preview.exists() else None,
            key == current_mount,
            lambda k=key: on_pick(k),
        ))
    _add_section(column, None, tiles)
    column.addStretch(1)
    return _scrollable(content)
