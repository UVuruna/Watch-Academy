# Controller — Display Settings

**Script:** [Controller Display (script)](../controller_display.py)

## Purpose
One visual choice in, a rebuilt skin out. `_DisplaySettingsMixin` is one
of the five responsibility mixins [Watch Controller](controller.md)
inherits (WA-R14 of the
[OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md), 2026-08-19).

Every `_set_*` here writes ONE (or one small family of) `Settings`
field(s) and reinstalls the skin through
`self._install_skin(build_skin(...))`. It is the single writer the menu,
the Watch Face window and the shortcuts all share — none of them touches
`Settings` directly.

## Connections

### Uses
- [Settings Store](settings_store.md) — `replace`, `rotation_themes`
- [Skin Builder](skin_builder.md) — `build_skin`
- [Config (folder)](../../config/___config.md) —
  `registry.slots.SLOT_KEYS`

### Used by
- [Watch Controller](controller.md) — inherits the mixin and owns
  `_install_skin`
- [Controller Menu](controller_menu.md) — every checkable entry lands on
  a setter here
- [Controller Dialogs](controller_dialogs.md) — `_watch_face_setters`
  wraps these same methods for the Watch Face window
- [Controller Shortcuts](controller_shortcuts.md) — the cyclers land here

## The setters
- **Ring** — `_set_ring`, `_set_ring_eye_shine`, `_set_ring_inner`,
  `_set_custom_ring_crown_text`, `_set_custom_ring_crown_orientation`,
  `_set_ring_crown_location`
- **Hands / metal** — `_set_hands`, `_metal_updates`
- **Slots** — `_set_slot` (the ONE writer behind all three slots, WA-R3)
- **Weekday theme and its rotation** — `_set_weekday_theme`,
  `_configure_theme_rotation`, `_rotate_theme`, `_next_rotation_theme`
- **The plain choices** — `_set_display_choice(key, value)`, the path
  every row of
  [`config.watch_face.DISPLAY_CHOICE_KEYS`](../../config/__about/watch_face.md)
  takes; `_set_earth_label`
- **Visibility** — `_set_visible`, `_refresh_visible_check`,
  `_toggle_all_visible`

## Design Decisions
- **`_install_skin` stayed in the controller.** It is not a choice, it
  is the wiring that hands a built skin to the widget, the compositor
  and the hover warm — the composition root's own job.
- **`_next_rotation_theme` lives here**, with the rotation it serves;
  [Controller Shortcuts](controller_shortcuts.md) imports it for the
  slot cycler, a one-way dependency between two mixins.
- **The no-op guard is load-bearing.** `_set_display_choice` returns
  early when the value has not changed, which skips a whole skin
  rebuild — that is why the day slot's MODE keeps this path instead of
  the generic slot writer.
