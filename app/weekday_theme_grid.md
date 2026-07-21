# Weekday Theme Grid

**Script:** [Weekday Theme Grid (script)](weekday_theme_grid.py)

## Purpose

A reusable, scrollable IMAGE + NAME picker for the weekday body themes
(Planets, Ancient Gods, Society, Scripture, Animals, The Inner Wheel,
Arcana) — the SAME grouping-by-kinship the old menu's Weekday submenu
used (`config.defaults.WEEKDAY_MENU_TOP` / `WEEKDAY_MENU_GROUPS`), now
rendered as a gallery of tiles instead of a nested dropdown chain (R5
MENU REWORK, owner spec: "u lepsem vecem meniju sa slikama i tekstom").

Built once (Rule #5) and shared by BOTH new mini windows that need a
weekday-theme picker: [Pointer Theme](pointer_theme.md) (the star
pointer's own weekday-body layer, 1st Slot) and [Slot Theme](slot_theme.md)
(any of the three slots, one of several option groups per slot). Follows
the SAME gallery pattern the [Encyclopedia](encyclopedia.md) topic
screen already uses — `QToolButton` (`ToolButtonTextUnderIcon`) tiles in
a wrapped `QGridLayout`, centered, inside a `QScrollArea` — for visual
consistency and because it is proven not to spill horizontally.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `WEEKDAY_MENU_TOP`,
  `WEEKDAY_MENU_GROUPS`, `WEEKDAY_THEME_TITLES`,
  `weekday_theme_body_art()` (the per-theme representative preview
  image, moved here from the Encyclopedia in this same round — Rule #5).

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
