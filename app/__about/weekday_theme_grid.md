# Weekday Theme Grid

**Script:** [Weekday Theme Grid (script)](../weekday_theme_grid.py) · **Flow:** [diagram](../__flow/weekday_theme_grid.md)

## Purpose
Reusable, scrollable image+name galleries. Two live here — the weekday
BODY themes and the Calendar MOUNT — built from the same three
primitives (`_tile`, `_add_section`, `_scrollable`) so they look and
behave identically (Rule #5). Originally shared by the now-DELETED
Pointer Theme and Slot Theme windows (Phase 6 FINAL cleanup); the sole
caller today is the Watch Face window's Themes & Slots section.

## Connections

### Uses
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

### `build_weekday_theme_grid(current_theme, on_pick, tr) -> QScrollArea`
A gallery of every weekday theme, Planets flat first then the kinship
groups (`WEEKDAY_MENU_TOP`/`_GROUPS` — the same order the old Weekday
submenu used). `on_pick(theme_key)` fires on a tile click; the currently
active theme's tile carries an accent border. Purely presentational — it
holds no settings state; the caller decides what a pick means.

### `build_calendar_mount_grid(current_mount, on_pick, tr) -> QScrollArea`
A gallery of one tile per roster that may ride the Calendar pointer's
twelve wedges, "None" first. Each tile previews the roster with its own
first member's plate and states its seat count (`"<title> (<seats>)"`).
The offer is read straight off `calendar_mounts.CALENDAR_MOUNTS`, so
registering a roster there puts it on this screen with no edit here.

### `_tile(label, icon_path, selected, on_click) -> QToolButton`
The one tile builder both galleries share — image over name, an accent
border when it is the active choice.

### `_add_section(column, title, tiles)`
The one labeled/centered/wrapped tile-row builder both galleries share
(`title=None` → no header/rule).

### `_scrollable(content) -> QScrollArea`
Wraps a widget in a resizable scroll area.
