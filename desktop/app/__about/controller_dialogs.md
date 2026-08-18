# Controller — Dialog Hosts

**Script:** [Controller Dialogs (script)](../controller_dialogs.py)

## Purpose
The watch's own windows: opens them, re-raises a live one, forgets a
closed one, and builds the payload each is handed. `_DialogHostsMixin`
is one of the five responsibility mixins
[Watch Controller](controller.md) inherits (WA-R14 of the
[OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md), 2026-08-19).

The controller holds the `_watch_face` / `_encyclopedia` / `_observatory`
handles; this module is the only place that assigns them, so "one window
at a time, raised not duplicated" has a single implementation.

## Connections

### Uses
- [Watch Face (subfolder)](../watch_face/___watch_face.md) ·
  [Settings Dialog (subfolder)](../settings_dialog/___settings_dialog.md) ·
  [Encyclopedia (subfolder)](../encyclopedia/___encyclopedia.md) ·
  [Observatory (subfolder)](../observatory/___observatory.md) —
  the windows it opens
- [Report](report.md) · [Shortcuts Window](shortcuts_window.md) — the two
  modal references
- [Slot Descriptor](slot_descriptor.md) — the triple
  `_slot_descriptors()` builds for the Themes & Slots section
- [Controller Display](controller_display.md) — the setters
  `_watch_face_setters` wraps
- [Config (folder)](../../config/___config.md) —
  [`watch_face.DISPLAY_CHOICE_KEYS`](../../config/__about/watch_face.md),
  `constants.MOVING_BODY_MENUS`, `palette`, `paths`

### Used by
- [Watch Controller](controller.md) — inherits the mixin and owns the
  window handles
- [Controller Menu](controller_menu.md) — every `…` entry calls an
  `_open_*` here

## The hosts
- **Non-modal, one live instance** — `_open_watch_face`,
  `_open_encyclopedia_at`, `_open_observatory`, `_open_guide`, each
  paired with its `_on_*_closed`
- **Modal** — `_open_settings`, `_open_report`, `_open_shortcuts`,
  `_open_custom_ring_editor`
- **`_reopen_live(dialog)`** — the ONE door all three non-modal openers
  go through (owner bug 2026-08-07, "CHI neće da mi otvori Watch Face,
  ostali hoće"). A handler that only called `raise_()` left a window
  HIDDEN without `done()` invisible forever — its `finished` never
  fired, so the reference stayed set — and a window whose C++ object had
  died raised `RuntimeError` inside a Qt slot, where it is swallowed and
  the menu item goes permanently silent on that one watch. `_reopen_live`
  shows first, and answers False for a corpse so the caller builds afresh
- **`_apply_settings_dialog_result`** — the ONE apply path an accepted
  `SettingsDialog` takes, however it was reached: the plain menu opener
  and the Watch Face Ring section's "Custom ring…" button both call it

## The payloads
- `_watch_face_setters()` — a COMPREHENSION over
  [`config.watch_face.DISPLAY_CHOICE_KEYS`](../../config/__about/watch_face.md)
  plus `constants.MOVING_BODY_MENUS` (WA-R2 replaced fifty-six
  hand-written lambdas), followed by the ~16 controls that need a real
  method of their own. `wrap()` keeps `functools.wraps` so
  `app.watch_face.section_reset` can still read a setter's true arity
- `_slot_descriptors()` · `_opacity_skin_defaults()` — data PROVIDERS,
  not setters: the Themes & Slots section and the Opacity section read
  the ACTIVE skin through them
- `_bundled_coverage()` / `_travel_coverage()` — the year range Time
  Travel and the Observatory are allowed to ask for

## Module-level function
- `_display_choice(set_display_choice, key)` — the ONE setter shape
  behind every plain Watch Face control, a real function of arity ONE
  so `functools.wraps`'s `__wrapped__` still reports it truthfully

## Design Decisions
- **Non-modal Encyclopedia/Guide/Observatory** (`.show()`, not
  `.exec()`): `exec()` forces application modality — blocking the dial
  too — for as long as the dialog stays open. Settings and Time Travel
  stay modal; they mutate state transactionally and must not be left
  half-applied by a stray close.
