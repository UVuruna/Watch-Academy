# Slot Descriptor

**Script:** [Slot Descriptor (script)](../slot_descriptor.py)

## Purpose
The shared `SlotDescriptor` dataclass — one per weekday-body slot
(1st/2nd/3rd), each carrying its own config values AND its own setter
callables (`set_mode`, `set_style_mode`, `set_weekday`, `set_names`).
Originally defined inside the now-DELETED `app.slot_theme` window (Phase
6 FINAL cleanup retired it); lives in its own small module now so
`app.controller` (the producer, via `_slot_descriptors()`) never has to
import from `app.watch_face` (the sole consumer, via `themes.py`/
`theme_tree.py`) — Rule #5, one shape, defined once, imported from
whichever side needs it.

## Connections

### Uses
- `dataclasses.dataclass`, `typing.Callable` — stdlib only, no project
  dependency

### Used by
- [Watch Controller](../__about/controller.md) — `_slot_descriptors()`
  builds one `SlotDescriptor` per slot fresh from the live `Settings`
  on every call
- [Watch Face — Themes & Slots](../watch_face/__about/themes.md) /
  [Content Tree](../watch_face/__about/theme_tree.md) — read the
  descriptor triple `setters["slot_descriptors"]()` hands them

## Classes

### SlotDescriptor
Plain dataclass, no methods: `index`, `title`, `mode_value`,
`style_value`, `theme_value`, `roster_value`, `names_value`,
`enabled_value` (the slot's current config) plus `set_mode`,
`set_style_mode`, `set_weekday`, `set_names` (its own bound setter
callables, already wrapped by the controller to apply AND refresh
whichever window is open).
