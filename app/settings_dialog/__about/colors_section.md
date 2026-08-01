# Colors Section

**Script:** [Colors Section (script)](../colors_section.py) · **Flow:** [diagram](../__flow/colors_section.md)

## Purpose

`_ColorsSectionMixin` — the **Colors** nav section: Saturation, Palette and
Clock (ring) tint groups. Plain-Python mixin (no base class); composed onto
[Settings Dialog](dialog.md)'s `QDialog` shell.

- **Saturation** (owner verdict, Session 21-D — "Saturation does not belong
  in Element sizes"; his allowed options were a Display-own-group or
  Colors, and Colors is where Palette + Ring tint already live) — its OWN
  group, TWO INDEPENDENT 0–100% sliders, both default 100%, each with its
  own "Default" reset:
  - **Aura** (`pointer_saturation`, storage key renamed from
    `palette_saturation` — `app/settings_store.py` migrates the old key as
    the fallback default on load) — scales the active Star+Aura palette's
    HSV saturation, feeding both the star diamonds and the Aura wedges so
    they move together.
  - **Ring** (`ring_saturation`) — scales the RING PLATE's and its letter
    overlay's HSV saturation, applied AFTER the ring_tint recolor.
    GROUND-TRUTHED SCOPE (owner asked for it explicitly): this is
    DELIBERATELY narrower than `ring_tint`'s own reach — ring_tint also
    recolors the hands, the Umbra, and the subdial's "theme" plate style,
    but `ring_saturation` touches ONLY the ring band's own art (the plate +
    its letters).
- **Palette** — one BIG color circle per hue of the ACTIVE (pointer, style)
  preset (owner spec 2026-07-11: Paint-style swatches); hovering a circle
  names the arm position it colors (Top / Bottom Left — the Compass speaks
  compass: North-East…), from `palette.pointer_arm_labels` over
  `constants.POINTER_ARM_LABELS` (the Genesis wheel — trio + the "cube"
  style, Session 20 — speaks its inverted seats Bottom/Left/Right; the
  dialog shell normalizes a stray stored "cube" style through
  `palette.effective_palette_style` before any preset lookup); clicking
  opens `QColorDialog`. Edited palettes are saved as the user's custom
  preset for that combination ("Reset to preset" returns to the owner
  preset).
- **Clock tint** (labeled "Clock tint — dial, hands and Umbra (letters
  excluded)") — one hue recolors the whole clock body (ring art, hands,
  Umbra, and the subdial's "theme" plate style; the letter art stays
  untouched): TWO labeled Paint-style grids from `palette.RING_TINT_GROUPS`
  (owner 2026-07-15: the flat palette read too light) — **Lighter** (the
  gold palette, silvers and pastels) and **Darker** (the deep ring variants
  plus the fashion darks — Navy, Oxford Blue, Petrol, Gunmetal, Graphite,
  Iron, Pewter, Dark Olive, Aubergine, Bordeaux) plus a free `QColorDialog`
  picker. Names live in the tooltips, the active swatch wears a white ring,
  "Gray (default)" = the untouched art (`self._ring_tint is None`).

`_round_swatch` (the shared Paint-style circle painter) is used by both
Palette (`_paint_chip`) and Clock tint (`_show_ring_tint`) — one painting
routine, two galleries, Rule #5.

## Connections

### Uses
- [Config (folder)](../../../config/___config.md) — `constants.POINTER_DISPLAY_NAMES`/
  `POINTER_ARM_LABELS`/`POINTER_SATURATION_RANGE`/`POINTER_SATURATION_SLIDER_STEP`/
  `RING_SATURATION_RANGE`/`RING_SATURATION_SLIDER_STEP`, `palette.pointer_arm_labels`/
  `RING_TINT_GROUPS`/`RING_TINT_PICKER_SEED`/`RING_TINT_NONE_SWATCH`,
  `dial.PALETTE_SWATCH_PX`/`RING_TINT_SWATCHES_PER_ROW`/`RING_TINT_SWATCH_PX`
- `self._palette_style` — read here, but normalized in [Settings Dialog]
  (dialog.md)'s `__init__` via `palette.effective_palette_style`, not by
  this mixin

### Used by
- [Settings Dialog](dialog.md) — the shell's `__init__` calls
  `_build_saturation_group()`, `_build_palette_group()`,
  `_build_ring_tint_group()`; `result_settings()` reads
  `self._pointer_saturation_slider`/`_ring_saturation_slider`/`self._hues`/
  `self._ring_tint` (the latter two set in `dialog.py.__init__`, mutated by
  this mixin's pickers)

## Classes

### _ColorsSectionMixin
- `_build_saturation_group() -> QGroupBox`: the Aura/Ring saturation sliders
- `_build_palette_group() -> QGroupBox`: the active preset's hue swatches
- `_round_swatch(chip, hue, size, selected=False)` (static): paints one
  Paint-style color circle
- `_paint_chip(chip, hue, index)`: repaints one palette swatch + its tooltip
- `_pick_color(index)`: opens `QColorDialog` for one palette arm
- `_reset_palette()`: restores the preset's hues
- `_build_ring_tint_group() -> QGroupBox`: the Clock tint grids + picker
- `_set_ring_tint(hue)`: applies a picked/preset tint
- `_pick_ring_tint()`: opens `QColorDialog` for a custom tint
- `_show_ring_tint()`: repaints the tint label + every swatch's selection ring
