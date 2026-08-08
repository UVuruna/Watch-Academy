"""Reusable image+name pickers — R5 MENU REWORK (owner spec: "u lepsem
vecem meniju sa slikama i tekstom"), shared by the Watch Face window's
Themes & Slots section (`app.watch_face.theme_tree`/`themes`) instead of
holding its own copy of a gallery layout. Originally shared by the
now-DELETED Pointer Theme and Slot Theme windows (Phase 6 FINAL
cleanup retired them); the galleries themselves outlived those windows
unchanged (Rule #5, one gallery, whichever caller needs it).

Two galleries live here, both built from the SAME tile/section
primitives: the weekday BODY themes (kinship-grouped) and — since the
Pointers REWORK phase 2, owner decree 2026-07-29 — the CALENDAR MOUNT,
the roster that rides the Calendar pointer's twelve wedges. The mount
originally moved here out of the Design window's Pointer tab because it
is a CONTENT choice (a roster, with art, needing a gallery); it now
surfaces in the Watch Face Themes & Slots section, shown only while the
Calendar pointer is active (`app.watch_face.themes._calendar_mount_group`).
"""

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.watch_face import thumbs
from app.watch_face.widgets import tile
from config import calendar_mounts, defaults, pantheon

_MAX_COLUMNS = 4


def _tile(label: str, icon_path, selected: bool, on_click) -> QToolButton:
    """One gallery tile — image over name, an accent border when it is
    the active choice. The ONE tile builder both galleries use — since
    2026-08-08 a thin adapter over `app.watch_face.widgets.tile` (Rule
    #5: one tile look, one icon size, one builder), which also moves
    the raw `QIcon(path)` load these galleries carried onto
    `thumbs.art_thumbnail`'s disk-cached 256px source (R-33: every
    gallery draws its icon from the thumbnail service)."""
    return tile(label, thumbs.art_thumbnail(icon_path), selected, on_click)


def _theme_icon(key: str):
    """The representative plate for one weekday theme's tile — the
    theme's own Sun body AS THE DIAL SHOWS IT TODAY (`on_date`, the
    universal rotation convention). The date-less canonical resolution
    the grids used before missed every family shipped as `_v2`-only
    (the Films group tile stood iconless on the owner's 2026-08-08
    screenshot while sw_jedi's whole cast sat on disk)."""
    return pantheon.weekday_theme_body_art(key, "sun", on_date=date.today())


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
    # Left-packed since the 2026-08-06 design pass: the centered wrap
    # made every gallery row float mid-column, reading as scattered
    # tiles (the owner's Watch Face screenshots) — the trailing stretch
    # alone keeps tiles at their own size, packed to the reading edge.
    wrap = QHBoxLayout()
    wrap.addLayout(grid)
    wrap.addStretch(1)
    column.addLayout(wrap)


def build_weekday_theme_grid(current_theme: str, on_pick, tr) -> QWidget:
    """A gallery of every weekday theme (a plain widget since 2026-08-08
    — the Watch Face page's own scroll area is the ONE scroller; a
    nested inner scroll clipped the full-size tiles the moment they grew
    to `widgets.TILE_ICON_PX`), Planets flat first
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
                _theme_icon(key),
                key == current_theme,
                lambda k=key: on_pick(k),
            )
            for key in keys
        ])

    add_group(None, pantheon.WEEKDAY_MENU_TOP)
    for group_title, keys in pantheon.WEEKDAY_MENU_GROUPS:
        add_group(group_title, keys)
    column.addStretch(1)
    return content


# --- Kinship GROUPS — the Watch Face content tree's Level 2/3 -----------
#
# The Watch Face window's Themes & Slots content tree (R-17/R-18) never
# dumps all ~30 weekday themes flat — it shows kinship groups first
# (Level 2), then that ONE group's own tiles (Level 3). These three
# functions expose the SAME `pantheon.WEEKDAY_MENU_TOP`/`_GROUPS` data
# `build_weekday_theme_grid` already reads, through the SAME `_tile`/
# `_add_section` primitives, so the tree never forks a second copy of
# the theme list (Rule #5) — it is a different SHAPE over identical data.

#: "Planets" stands in for the flat `WEEKDAY_MENU_TOP` entries so every
#: Level-2 tile is a real, clickable group — the top list has no title
#: of its own in the flat gallery above.
PLANETS_GROUP_TITLE = "Planets"


def weekday_group_titles() -> tuple[str, ...]:
    """Level-2 group titles, in menu order."""
    return (PLANETS_GROUP_TITLE,) + tuple(
        title for title, _keys in pantheon.WEEKDAY_MENU_GROUPS
    )


def weekday_group_keys(group_title: str) -> tuple[str, ...]:
    """The theme keys inside one Level-2 group."""
    if group_title == PLANETS_GROUP_TITLE:
        return pantheon.WEEKDAY_MENU_TOP
    return next(
        keys for title, keys in pantheon.WEEKDAY_MENU_GROUPS
        if title == group_title
    )


def build_weekday_group_grid(current_group: str | None, on_pick, tr) -> QWidget:
    """Level 2 — one tile per kinship group; no per-group art (a group
    is a folder, not a theme), so each tile shows its first member's
    plate as a representative icon."""
    content = QWidget()
    column = QVBoxLayout(content)
    column.setSpacing(12)
    tiles = []
    for title in weekday_group_titles():
        first_key = weekday_group_keys(title)[0]
        tiles.append(_tile(
            tr(title),
            _theme_icon(first_key),
            title == current_group,
            lambda t=title: on_pick(t),
        ))
    _add_section(column, None, tiles)
    column.addStretch(1)
    return content


def build_weekday_theme_tiles(
    group_title: str, current_theme: str, default_theme: str, on_pick, tr,
) -> QWidget:
    """Level 3 — one group's own theme tiles. The pointer's documented
    DEFAULT theme (`constants.WATCH_FACE_KINDS_BY_POINTER`, see
    themes.md) carries a "★ " prefix wherever it appears, so the
    default is visible without opening a tooltip."""
    content = QWidget()
    column = QVBoxLayout(content)
    column.setSpacing(12)
    tiles = [
        _tile(
            (
                f"★ {tr(pantheon.WEEKDAY_THEME_TITLES[key])}"
                if key == default_theme
                else tr(pantheon.WEEKDAY_THEME_TITLES[key])
            ),
            _theme_icon(key),
            key == current_theme,
            lambda k=key: on_pick(k),
        )
        for key in weekday_group_keys(group_title)
    ]
    _add_section(column, None, tiles)
    column.addStretch(1)
    return content


def build_calendar_mount_grid(current_mount: str, on_pick, tr) -> QWidget:
    """A gallery (plain widget — see `build_weekday_theme_grid` on why
    the inner scroll died) of every roster that may ride the Calendar
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
        tiles.append(_tile(
            f"{tr(mount.title)} ({mount.seats})",
            defaults.ZODIAC_ART_DIR / mount.art_dir / f"{mount.stems[0]}.png",
            key == current_mount,
            lambda k=key: on_pick(k),
        ))
    _add_section(column, None, tiles)
    column.addStretch(1)
    return content
