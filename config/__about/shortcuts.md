# Shortcuts

**Script:** [Shortcuts (script)](../shortcuts.py) · **Flow:** [diagram](../__flow/shortcuts.md)

## Purpose

Keyboard input and the fast-travel it drives — one of six modules
Session 36 (THE CONFIG SPLIT, [Work Plan Structure](../../WORKPLAN-STRUCTURE.md))
carved out of `config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## Contents

- **Keyboard shortcuts** — `SHORTCUTS`, the ONE `(action_id, key name,
  modifier names, description)` table, pinned by
  `tests/test_shortcuts.py` and rendered into each menu entry's
  shortcut column. `shortcut_display(action_id)` — the "Ctrl+R"
  human-readable label; `_SHORTCUT_MODIFIER_DISPLAY`/
  `_SHORTCUT_KEY_DISPLAY_OVERRIDES` are its private lookup tables.
- **Fast Travel** — `FAST_TRAVEL_THEMES` (the Sun/Moon/Calendar jump
  options, each with an `options` sub-tuple naming `jump_stem`s that
  feed the shared `_compute_jump` machinery).
- **Fast Travel FLASH** — the transient overlay's geometry/timing
  constants (`FAST_TRAVEL_FLASH_*`), the Calendar's own computed-icon
  geometry (`CALENDAR_ICON_WEDGE_COUNT`/`_RING_WIDTH_FRACTION`), and
  `TIME_TRAVEL_DURATION_S`/`DEEP_TIME_YEAR_RANGE` (Time Travel dialog
  values, not strictly Fast Travel ones, but too small to justify a
  seventh destination module).

## Connections

### Uses
- Nothing beyond stdlib — every value here is a plain literal or a
  Qt-free string naming a `Qt.Key`/`Qt.KeyboardModifier` enum member
  (config stays Qt-free; `app.widget` resolves the names).

### Used by
- [App (folder)](../../app/___app.md) — `controller._build_menu`'s
  shortcut column, `widget.keyPressEvent`'s dispatch,
  `fast_travel_flash.py`

## Functions

- `shortcut_display(action_id)`: the combo's human-readable label
  ("Ctrl+R") for the menu's shortcut column — raises `KeyError` for an
  unknown action_id.

## Design Decisions

- **The shortcut table stays Qt-free by naming enum members as
  strings** — `key` is a `Qt.Key` enum NAME and `modifiers` a tuple of
  `Qt.KeyboardModifier` enum NAMES; `app.widget` resolves both once at
  import time. This module changes WHERE the table lives, never its
  shape.
- **Every combo carries a MODIFIER on purpose.** A bare letter would
  collide with the `HIDDEN_MODE_SECRET` typed-sequence buffer, which
  only ever sees printable no-modifier text — a held modifier routes
  the key event around that buffer entirely by construction.
- **An action_id may appear TWICE** (`fast_travel_future`, bound to
  both `Key_Equal` and `Key_Plus`) when the owner wants two physical
  combos to fire the SAME action — `app.widget` already loops the
  whole table, so a second row needs no special casing.
