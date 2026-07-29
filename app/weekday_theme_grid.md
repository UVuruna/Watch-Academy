# Weekday Theme Grid

**Script:** [Weekday Theme Grid (script)](weekday_theme_grid.py)

## Purpose

Reusable, scrollable IMAGE + NAME galleries. Two live here — the weekday
BODY themes and the CALENDAR MOUNT — built from the same three
primitives (`_tile`, `_add_section`, `_scrollable`) so they look and
behave identically (Rule #5).

### The weekday body themes

A picker for the weekday body themes
(Planets, Ancient Gods, Society, Scripture, Animals, The Inner Wheel,
Arcana) — the SAME grouping-by-kinship the old menu's Weekday submenu
used (`config.defaults.WEEKDAY_MENU_TOP` / `WEEKDAY_MENU_GROUPS`), now
rendered as a gallery of tiles instead of a nested dropdown chain (R5
MENU REWORK, owner spec: "u lepsem vecem meniju sa slikama i tekstom").

Built once (Rule #5) and shared by BOTH new mini windows that need a
weekday-theme picker: [Pointer Theme](pointer_theme.md) (the star
pointer's own weekday-body layer, 1st Slot) and [Slot Theme](slot_theme.md)
(any of the three slots, one of several option groups per slot). Follows
the SAME gallery pattern the [Encyclopedia (subfolder)](encyclopedia/___encyclopedia.md) topic
screen already uses — `QToolButton` (`ToolButtonTextUnderIcon`) tiles in
a wrapped `QGridLayout`, centered, inside a `QScrollArea` — for visual
consistency and because it is proven not to spill horizontally.

### The Calendar mount (owner decree 2026-07-29)

The roster that rides the Calendar pointer's twelve wedges. The choice
MOVED here out of the Design window's Pointer tab, because a mount is
CONTENT — a roster, with art, wanting a gallery — and this module is
where content is picked; the Design tab keeps SHAPE alone. The stored
key is unchanged (`Settings.calendar_mount`): the control moved, the
setting did not, so no settings migration exists or is needed.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `WEEKDAY_MENU_TOP`,
  `WEEKDAY_MENU_GROUPS`, `WEEKDAY_THEME_TITLES`,
  `weekday_theme_body_art()` (the per-theme representative preview
  image, moved here from the Encyclopedia in this same round — Rule #5),
  and `CALENDAR_MOUNTS` (the mount registry — the ONE source of the
  mount gallery's offer).

### Used by
- [Pointer Theme](pointer_theme.md) — the picker for the 1st Slot's own
  weekday-body layer.
- [Slot Theme](slot_theme.md) — one of the option groups for whichever
  slot (1st/2nd/3rd) is being edited.

## Functions

### `build_weekday_theme_grid(current_theme, on_pick, tr)`
Returns a `QScrollArea` containing the Planets-flat entry followed by
every kinship group, each its own labeled section — clicking a tile
calls `on_pick(theme_key)`. The CURRENTLY active theme's tile carries a
visible selected marker (an accent border) so the picker doubles as a
"what is showing now" readout. Purely presentational — it holds no
settings state itself; the caller decides what a pick means (which
slot, which roster/metal stay untouched).

### `build_calendar_mount_grid(current_mount, on_pick, tr)`
Returns a `QScrollArea` of one tile per mountable roster, "None" first
(the mount-off tile, matching the setting's own `"off"` value) —
clicking calls `on_pick(mount_key)`. The offer is read straight off
`defaults.CALENDAR_MOUNTS`, so registering a roster there puts it on
this screen with no edit in this module.

```
tiles = [ "None" ]
FOR EACH (key, mount) IN the mount registry:
    preview = the plate of the roster's FIRST member
              (the crown of a System B wheel, the opening sign of a
               System A one) — absent art simply shows no icon
    label   = "<roster title> (<seat count>)"
    tiles  += one tile, accent-bordered when key is the active mount
```

The seat count rides the label because it is the reader's own question:
a Dozen fills one seat per wedge, a 24-set two.
