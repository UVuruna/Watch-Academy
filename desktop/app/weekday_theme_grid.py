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

from PySide6.QtWidgets import QVBoxLayout, QWidget


from app.watch_face import thumbs
from app.watch_face.controls import picture_group
from config import calendar_mounts, defaults, pantheon

#: The gap between the stacked picture groups every builder in this
#: module lays out — one number, four readers (it was written out four
#: times; OOP audit 2026-08-18, section 4).
_COLUMN_SPACING_PX = 12


def _entry(key: str, label: str, blurb: str, icon_path) -> tuple:
    """One card's `(key, label, blurb, icon)` — the ONE entry builder
    both galleries use. Since the 2026-08-14 CardGroup migration the
    tile itself is built by `controls.picture_group`; this keeps the
    thumbnail service as the single icon door (R-33: every gallery
    draws its icon from `thumbs.art_thumbnail`'s disk-cached source)."""
    return (key, label, blurb, thumbs.art_thumbnail(icon_path))


def _theme_icon(key: str):
    """The representative plate for one weekday theme's tile — the
    theme's own Sun body AS THE DIAL SHOWS IT TODAY (`on_date`, the
    universal rotation convention). The date-less canonical resolution
    the grids used before missed every family shipped as `_v2`-only
    (the Films group tile stood iconless on the owner's 2026-08-08
    screenshot while sw_jedi's whole cast sat on disk)."""
    return pantheon.weekday_theme_body_art(key, "sun", on_date=date.today())


def _theme_blurb(key: str, tr) -> str:
    """One theme card's hover line (the mandatory blurb the element
    classes require). Stated from what the REGISTRY actually knows —
    the theme's title and, when it declares one, its article set — and
    never invented lore: the encyclopedic text is the Encyclopedia's
    job, this is the one line that says what picking the card does."""
    title = tr(pantheon.WEEKDAY_THEME_TITLES[key])
    return tr("The weekday bodies drawn from the {title} cast.").format(
        title=title
    )


def _add_section(
    column: QVBoxLayout, title: str, description: str, entries: list,
    current, on_pick,
) -> None:
    """One titled card gallery — the ONE section builder both galleries
    use. The hand-built header + rule + `flow_gallery` it replaced
    (2026-08-14) is exactly what `CardGroup` is: a title, a sentence
    under it, and the centered width-aware flow underneath."""
    column.addWidget(picture_group(
        title, description, entries, current, on_pick
    ))


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
    column.setSpacing(_COLUMN_SPACING_PX)

    def add_group(title: str, keys: tuple[str, ...]) -> None:
        _add_section(
            column, tr(title),
            tr("Which cast of bodies fills the seven weekday seats."),
            [
                _entry(
                    key, tr(pantheon.WEEKDAY_THEME_TITLES[key]),
                    _theme_blurb(key, tr), _theme_icon(key),
                )
                for key in keys
            ],
            current_theme if current_theme in keys else None,
            on_pick,
        )

    add_group(PLANETS_GROUP_TITLE, pantheon.WEEKDAY_MENU_TOP)
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
# `build_weekday_theme_grid` already reads, through the SAME `_entry`/
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
    column.setSpacing(_COLUMN_SPACING_PX)
    entries = [
        _entry(
            title, tr(title),
            tr("The {title} family — open it to see its themes.").format(
                title=tr(title)
            ),
            _theme_icon(weekday_group_keys(title)[0]),
        )
        for title in weekday_group_titles()
    ]
    _add_section(
        column, tr("Theme families"),
        tr("Themes are grouped by kinship — pick a family to see its casts."),
        entries, current_group, on_pick,
    )
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
    column.setSpacing(_COLUMN_SPACING_PX)
    entries = [
        _entry(
            key,
            (
                f"★ {tr(pantheon.WEEKDAY_THEME_TITLES[key])}"
                if key == default_theme
                else tr(pantheon.WEEKDAY_THEME_TITLES[key])
            ),
            (
                _theme_blurb(key, tr) + " "
                + tr("This is this pointer's own default.")
                if key == default_theme else _theme_blurb(key, tr)
            ),
            _theme_icon(key),
        )
        for key in weekday_group_keys(group_title)
    ]
    _add_section(
        column, tr(group_title),
        tr("The casts inside this family — ★ marks this pointer's default."),
        entries, current_theme, on_pick,
    )
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
    column.setSpacing(_COLUMN_SPACING_PX)
    entries = [_entry(
        "off", tr("None"),
        tr("The wedges stay empty — no roster rides the Calendar pointer."),
        None,
    )]
    for key, mount in calendar_mounts.CALENDAR_MOUNTS.items():
        entries.append(_entry(
            key, f"{tr(mount.title)} ({mount.seats})",
            tr("{title} rides the twelve wedges — {seats} seats.").format(
                title=tr(mount.title), seats=mount.seats,
            ),
            defaults.ZODIAC_ART_DIR / mount.art_dir / f"{mount.stems[0]}.png",
        ))
    _add_section(
        column, tr("Calendar mount"),
        tr("Which roster rides the Calendar pointer's twelve wedges."),
        entries, current_mount, on_pick,
    )
    column.addStretch(1)
    return content
