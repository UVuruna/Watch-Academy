# Controller — Context Menu

**Script:** [Controller Menu (script)](../controller_menu.py) · **Flow:**
[diagram](../__flow/controller_menu.md)

## Purpose
The dial's right-click / tray menu: builds it, and keeps its checks and
gray states in step with the settings. `_ContextMenuMixin` is one of the
five responsibility mixins [Watch Controller](controller.md) inherits
(WA-R14 of the [OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md),
2026-08-19).

This module owns the MENU, never what an entry does: every action it
creates calls a setter in [Controller Display](controller_display.md) or
a dialog host in [Controller Dialogs](controller_dialogs.md).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `archetypes`,
  `palette`, `shortcuts` (the shortcut column beside each label),
  `ui_text.ui`
- [Skin Builder](skin_builder.md) — `slot_seconds`, `watch_title`
- [Controller Display](controller_display.md) — every setter an entry calls
- [Controller Dialogs](controller_dialogs.md) — every `_open_*` an entry calls

### Used by
- [Watch Controller](controller.md) — inherits the mixin; `__init__`
  builds the menu once and hands it to both the widget and
  [Tray Controller](tray.md)

## Classes and helpers
- `_StayOpenMenu(QMenu)` — a menu whose CHECKABLE items (and plain
  actions carrying the `"stay_open"` property) do not close it, so
  several settings change in one visit
- `_guard_exclusive_choice(action, apply)` — one member of an EXCLUSIVE
  `QActionGroup` wired so a click on the ALREADY-CHECKED member is a
  no-op. Qt only auto-unchecks SIBLINGS when a DIFFERENT member becomes
  checked; clicking the sole checked member flips it off and empties the
  group (owner screenshot: Planetary/Pantheon both unchecked)
- `_build_menu()` — the whole tree; `_add_choice_group`,
  `_add_choice_submenu`, `_add_toggle`, `_submenu`, `_ui`, `_labeled`
  are its vocabulary
- `_refresh_menu_gating()` — recomputes every gated FLAT entry from the
  CURRENT settings without rebuilding, so the stay-open menu keeps its
  window and only the gray states move

## Design Decisions
- **One gating implementation serves both paths.** The fresh build and
  the in-place refresh both end in `_refresh_menu_gating()`, so a gate
  can never be right in one and stale in the other.
- **Every exclusive group in the app routes through two doors** —
  `_add_choice_group` and the slot menus' own `slot_action`, both of
  them wired with `_guard_exclusive_choice`.
