# Shortcuts

**Script:** [Shortcuts (script)](../shortcuts.py) · **Flow:** [diagram](../__flow/shortcuts.md)

## Purpose

Keyboard input and the fast-travel it drives — one of six modules
Session 36 (THE CONFIG SPLIT, [Work Plan Structure](../../../docs/archive/WORKPLAN-STRUCTURE.md))
carved out of `config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## Contents

- **Keyboard shortcuts** — `SHORTCUTS`, the ONE `(action_id, key name,
  modifier names, description)` table, pinned by
  `tests/test_shortcuts.py` and rendered into each menu entry's
  shortcut column. `shortcut_display(action_id)` — the "Ctrl+R"
  human-readable label; `_SHORTCUT_MODIFIER_DISPLAY`/
  `_SHORTCUT_KEY_DISPLAY_OVERRIDES` are its private lookup tables.
- **Fast Travel** — `FAST_TRAVEL_THEMES`, SIX categories (owner
  selector spec 2026-08-11): Solar Eclipse (Any/Total/Annular/Partial/
  Hybrid), Lunar Eclipse (Any/Total/Partial/Penumbral), Sun Turning
  Points (Any/Solstices/Equinoxes), Moon Stations (Any/Full/New/
  Quarters), Date (Day/Month/Year/Century/Millennium — id stays
  `"calendar"` for the computed wheel icon) and Time (Hour/Minute/
  Second — id `"clock"`, emoji fallback), each with an `options`
  sub-tuple naming `jump_stem`s that feed the shared `_compute_jump`
  machinery. This retires the old absurdity of a solar eclipse living
  as an option under Moon phases.
- **Fast Travel FLASH** — the transient overlay's geometry/timing
  constants (`FAST_TRAVEL_FLASH_*`, including
  `FAST_TRAVEL_FLASH_ICON_SUPERSAMPLE` — every icon is produced at that
  multiple of its final size and shrunk, because Qt rasterizing a vector
  at 28 px simply loses anything thinner than a pixel), the geometry of
  the THREE computed glyphs (`CALENDAR_SHEET_*`, `CLOCK_ICON_*`,
  `ECLIPSE_ICON_*` — the solar-eclipse row joined them on the owner's
  verdict of 2026-08-12, after two of his art files each read as the Moon
  row beside them at menu size), and
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
