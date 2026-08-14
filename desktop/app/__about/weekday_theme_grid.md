# Weekday Theme Grid

**Script:** [Weekday Theme Grid (script)](../weekday_theme_grid.py) · **Flow:** [diagram](../__flow/weekday_theme_grid.md)

## Purpose
Reusable image+name galleries. Two live here — the weekday BODY themes
and the Calendar MOUNT — built from the same two primitives (`_tile`,
`_add_section`) so they look and behave identically (Rule #5).
Originally shared by the now-DELETED Pointer Theme and Slot Theme
windows (Phase 6 FINAL cleanup); the sole caller today is the Watch
Face window's Themes & Slots section.

## Connections

### Uses
- [Watch Face — Shared Widgets](../watch_face/__about/widgets.md) —
  `picture_group` (the ONE gallery door since 2026-08-14 — title,
  sentence, mandatory blurb, reserved border, shared icon size)
- [Watch Face — Thumbnails](../watch_face/__about/thumbs.md) —
  `art_thumbnail` (disk-cached 256px icon source, R-33)
- [Config (folder)](../../config/___config.md) — `pantheon.WEEKDAY_MENU_TOP`/
  `WEEKDAY_MENU_GROUPS`/`WEEKDAY_THEME_TITLES`/`weekday_theme_body_art()`,
  `calendar_mounts.CALENDAR_MOUNTS`

### Used by
- [Watch Face — Content Tree](../watch_face/__about/theme_tree.md) —
  `build_weekday_group_grid`/`build_weekday_theme_tiles` (Level 2/3 of
  the breadcrumb-navigated weekday-body picker)
- [Watch Face — Themes & Slots](../watch_face/__about/themes.md) —
  `build_calendar_mount_grid`, shown only while the Calendar pointer is
  active

## Functions

### `build_weekday_theme_grid(current_theme, on_pick, tr) -> QWidget`
A gallery of every weekday theme, Planets flat first then the kinship
groups (`WEEKDAY_MENU_TOP`/`_GROUPS` — the same order the old Weekday
submenu used). `on_pick(theme_key)` fires on a tile click; the currently
active theme's tile carries an accent border. Purely presentational — it
holds no settings state; the caller decides what a pick means.

### `build_calendar_mount_grid(current_mount, on_pick, tr) -> QWidget`
A gallery of one tile per roster that may ride the Calendar pointer's
twelve wedges, "None" first. Each tile previews the roster with its own
first member's plate and states its seat count (`"<title> (<seats>)"`).
The offer is read straight off `calendar_mounts.CALENDAR_MOUNTS`, so
registering a roster there puts it on this screen with no edit here.

### `_tile(label: str, icon_path, selected, on_click) -> QToolButton`
The one tile builder both galleries share — since 2026-08-08 a thin
adapter over `app.watch_face.widgets.tile`: it resolves `icon_path`
through `thumbs.art_thumbnail` (disk-cached, missing → honest blank
icon box) and inherits the shared `TILE_ICON_PX` icon size, so these
galleries can never again drift from the Watch Face sections' tiles.

### `_theme_icon(key) -> Path`
The representative plate for one theme's tile: the theme's own Sun body
AS THE DIAL SHOWS IT TODAY (`weekday_theme_body_art(key, "sun",
on_date=today)`). The date-less canonical resolution used before missed
every family shipped as `_v2`-only — the Films group tile stood
iconless on the owner's 2026-08-08 screenshot while sw_jedi's whole
cast sat on disk.

### `_add_section(column, title, tiles)`
The one labeled/centered/wrapped tile-row builder both galleries share
(`title=None` → no header/rule).

## Design Decisions
- **Five columns since the Zubi fix round (2026-08-09, ALG-7).** The
  4-column wrap left the gallery band's right half mostly empty at the
  window's minimum while further sections stacked below — the ladder
  says fill the row first. Tiles stay left-packed at their own size
  (the owner's 2026-08-06 decree); only the wrap point moved. The
  LAST, non-full row of a left-packed gallery is an owner-approved
  baseline entry (2026-08-09) — ALG-7's own docstring names it the
  known false positive.
- **No inner scroll areas (2026-08-08).** The builders used to wrap
  their content in a private `QScrollArea`; at the full `TILE_ICON_PX`
  tile size those nested scrollers clipped every tile row and grew a
  horizontal scrollbar (Space & Legibility BUG A+B on the session's own
  first screenshots). The Watch Face page's own scroll area is the ONE
  scroller — the builders now return the plain content widget, and the
  Zubi audit's SCROLL findings on this window went 3 → 0.
- **Raw `QIcon(path)` loads are gone** — every icon rides
  `thumbs.art_thumbnail`'s disk cache; ~30 full-resolution plates are
  no longer decoded on every Themes & Slots open.
