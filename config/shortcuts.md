# Shortcuts

**Script:** [Shortcuts (script)](shortcuts.py)

## Purpose

Keyboard input and the fast-travel it drives — one of six modules
Session 36 (THE CONFIG SPLIT, [Work Plan Structure](../WORKPLAN-STRUCTURE.md))
carved out of `config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## What moved here

- **Keyboard shortcuts** — `SHORTCUTS` (the one action_id → Qt.Key/
  modifiers/description table), `shortcut_display()`, the display-name
  override tables.
- **Fast Travel** — `FAST_TRAVEL_THEMES` (the Sun/Moon/Calendar jump
  options).
- **Fast Travel FLASH** — the transient overlay's geometry/timing
  constants (`FAST_TRAVEL_FLASH_*`), the Calendar's own computed-icon
  geometry (`CALENDAR_ICON_WEDGE_COUNT`/`_RING_WIDTH_FRACTION`), and
  `TIME_TRAVEL_DURATION_S`/`DEEP_TIME_YEAR_RANGE` — the latter two sat
  in this section's span in the source (a minor drift; they are Time
  Travel dialog values, not Fast Travel ones, but too small to justify
  a seventh destination and not named anywhere in the split map).

## Connections

### Uses
- Nothing beyond stdlib — every value here is a plain literal or a
  Qt-free string naming a `Qt.Key`/`Qt.KeyboardModifier` enum member
  (config stays Qt-free; `app.widget` resolves the names).

### Used by
- [App (folder)](../app/___app.md) — `controller._build_menu`'s
  shortcut column, `widget.keyPressEvent`'s dispatch,
  `fast_travel_flash.py`

## Design Decisions

- **The shortcut table stays Qt-free by naming enum members as
  strings**, exactly as the original `defaults.py` did — this module
  changes WHERE the table lives, never its shape.
