# Controller — Shortcut Actions

**Script:** [Controller Shortcuts (script)](../controller_shortcuts.py)

## Purpose
Every keyboard shortcut the watch answers, and the flashes they raise on
the dial. `_ShortcutActionsMixin` is one of the five responsibility
mixins [Watch Controller](controller.md) inherits (WA-R14 of the
[OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md), 2026-08-19).

`_on_shortcut(action_id)` is the ONE reader of
[`config.shortcuts.SHORTCUTS`](../../config/__about/shortcuts.md); every
other method here is one family's handler.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `shortcuts` (the table),
  `archetypes`, `constants`, `defaults`, `pantheon`,
  `registry.slots.SLOT_KEYS`
- [Controller Display](controller_display.md) — `_next_rotation_theme`,
  and every `_set_*` a cycler lands on
- [Skin Builder](skin_builder.md) — `build_skin`, `effective_weekday_slot`
- [Fast Travel Flash](fast_travel_flash.md) — the transient icon+text toast
- [Rings](../../data/__about/rings.md) — the preset list a ring cycler walks

### Used by
- [Watch Controller](controller.md) — inherits the mixin; the widget's
  `shortcut_triggered` signal is wired straight to `_on_shortcut`

## Class attributes (they travelled with their group)
- `_WEEKDAY_THEME_ORDER` — ordered exactly like the Weekday submenu
  (Planets first and flat, then the kinship groups)
- `_SLOT_COMPLICATION_ORDER` — the 4 Complication modes Ctrl+1/2/3 cycle
- `_LOCATION_JUMP_KINDS` — the jump kinds that LAND somewhere new and so
  deserve a location flash (R-30)
- `_LOCATION_FLASH_ICONS` — the two compass roses and Greenwich's plain
  one; an ordinary city names none, on purpose

## The families
- **Ring / weekday theme** — `_cycle_ring`, `_cycle_weekday_theme`,
  `_weekday_theme_on_diamonds`
- **Slots** — `_slot_active`, `_slot_mode_state`, `_slot_theme_state`,
  `_cycle_slot`, `_cycle_slot_complication`, `_cycle_slot_weekday_theme`;
  `_cycle_slots`/`_apply_slot_layout`/`_set_slot_layout` share their flag
  arithmetic with the Watch Face window's FACE LAYOUT row (Phase ③, R-17)
- **Fast travel** — `_fast_travel_theme`, `_fast_travel_option_index`,
  `_cycle_fast_travel_theme`, `_cycle_fast_travel_option`,
  `_flash_fast_travel`, `_step_fast_travel`
- **Locations** — `_flash_location`, `_flash_jump_location`,
  `_jump_to_place`, `_cycle_jump_city`
- **Archetype** — `_toggle_archetype_shortcut`, which mirrors the menu
  action with signals blocked rather than re-entering the handler

## Module-level function
- `_location_flash_text(name, path, timezone)` — R-30's "CITY, COUNTRY"
  formatter. `WatchController.__init__` seeds
  `_active_location_display` with it and `_flash_location` refreshes it,
  so the ring's Location crown text and the flash never disagree.

## Design Decisions
- **A mixin, not a collaborator.** Every action here READS and WRITES
  `self._settings`, `self._skin`, the open windows and the timers. A
  collaborator would need a back-channel to all four; a mixin keeps
  `self` and changes no call site at all — the shape
  [Settings Dialog (subfolder)](../settings_dialog/___settings_dialog.md)
  already uses for its section mixins.
- **The class attributes travelled with their methods.** An order table
  read by exactly one cycler belongs beside that cycler, not in the
  composition root.
