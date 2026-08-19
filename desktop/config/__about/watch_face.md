# Watch Face (config)

**Script:** [Watch Face (script)](../watch_face.py)

## Purpose
`DISPLAY_CHOICE_KEYS` — every Watch Face control whose entire job is
"store this key and rebuild the skin", as data.

Most of the window's ~72 controls do exactly that, through
`WatchController._set_display_choice(key, value)`. Until the [OOP
audit](../../../docs/AUDIT-OOP-2026-08-18.md)'s R2 the wiring was
written out fifty-six times inside a 4,400-line controller —
`"pointer": wrap(lambda v: self._set_display_choice("pointer", v))` —
where the only thing that changed line to line was the key, repeated
twice. That is a table pretending to be code, which ONE KIND, ONE CLASS
forbids: the knowledge is WHICH KEYS take the plain path, and knowledge
is data. Adding a plain setting is now one line here.

## Connections

### Uses
- nothing — pure data, no imports at all

### Used by
- [Controller](../../app/__about/controller.md) —
  `_watch_face_setters()` builds one wrapped setter per key in this
  tuple, spliced with `constants.MOVING_BODY_MENUS` (the seven moving
  bodies take the same path but are named by their own registry, so a
  body can never be added in one place and forgotten in the other)
- `tests/test_watch_face_colors.py` — asks the REAL mapping whether a
  Colors/Opacity key is bound

## Design Decisions
- **Only the PLAIN path lives here.** A control that touches more than
  one key (`ring`, `hands`, `palettes`), opens a window
  (`open_custom_ring`) or ANSWERS a question instead of setting
  anything (`slot_descriptors`, `opacity_skin_defaults`,
  `ring_has_crown_text`) stays written out in the controller, one line
  each — so that being special is visible where the map is built.
- **The moving bodies are NOT re-listed.** They already have a registry
  (`constants.MOVING_BODY_MENUS`, which the storage and the overlay
  also walk); repeating their names here would be the same defect in a
  new place.
- **Grouped by the section that shows them, in build order**, with the
  history comments that used to sit beside each line — THE UNIFIED
  NAMES SWITCH, THE CALENDAR MOUNT, THE DEAD PILL, the live numeral
  bands. A key's reason moves with the key.
- **Order is documentation, not behaviour.** Nothing reads this tuple
  positionally; the map is consumed by key lookup only.

## What THE CONSTANTS SPLIT added (2026-08-19)

**WATCH FACE CONTENT KINDS (R-18)** moved in from the deleted
`config/constants.py`: `WATCH_FACE_KINDS_BY_POINTER` and the
`watch_face_kinds()` reader.

This module is THE WATCH FACE CONTROL VOCABULARY — every control whose
setter is just "store this key". Which content kinds a pointer may carry
is exactly that vocabulary, and it was the only Watch Face table still
living outside it.

The whole 38-section map, with the reason for every destination, is
in [Config (folder)](../___config.md#the-constants-split).
