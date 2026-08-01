# Subdial

**Script:** [Subdial (script)](../subdial.py) · **Flow:** [diagram](../__flow/subdial.md)

## Purpose
Subdial (complication) drawing — the small roundels and their text: the
slot plates, their LIVE drop shadow, fitted one- and two-line text, and
the small-seconds sub-dial. `octa_slot_art` resolves a slot art file
and is shared with the calendar mounts and the thirteenth plates.

## Connections

### Uses
- [Context](context.md), [Painting](painting.md) — `draw_pixmap_centered`,
  `draw_shadowed_text`
- [Asset Variants](asset_variants.md) — `ring_face_color`,
  `subdial_plate_file`
- [Config (folder)](../../config/___config.md) — `defaults`, `dial`,
  `palette`, `paths`
- [Core (folder)](../../core/___core.md) — `format_official`, `real_year`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `SlotLayer` draws every
  seated slot's flat face on `draw_slot_roundel`
- [Calendar Mount](calendar_mount.md), [Ninths](ninths.md) —
  `octa_slot_art` (the shared art resolver)
- [Compositor](compositor.md) — `display_year` (hover date text)

## Functions
- `octa_slot_art(folder, name)`: the PNG for an image slot style under
  `assets/calendars/<folder>/<name>.png`, or `None` while the art has
  not landed (graceful-absent).
- `slot_text(mode, ctx)`: the info text of a time/date/day-length slot.
- `display_year(ctx)`: the compact OFFICIAL year form for the date
  complication and the Earth marker's deep-travel row.
- `draw_slot_roundel(painter, ctx, pos, diameter)`: the watch-face
  subdial behind flat slot content — a live outward shadow
  (`_draw_subdial_shadow`), then the active set's master plate
  (recolored to the requested finish/tint), or a procedural rimmed
  circle when no plate art exists.
- `draw_fitted_text`/`draw_two_lines`: fit-to-width one/two-line slot
  text in the letter-finish metal over a shadow.
- `draw_small_seconds(painter, ctx, pos, diameter)`: the small-seconds
  complication — eight rim ticks plus the active set's own seconds hand
  in miniature, both in the finish metal.

## Design Decisions
- **The seat never reaches a plate file directly** (owner decree
  2026-07-20) — only the LIVE shadow is keyed to the seat's dial
  position; the plate itself is one master, recolored on demand
  ([Asset Recolor](asset_recolor.md)), per root Rule #19.
- **Every subdial accent wears the letter-finish metal** (`_finish_color`),
  never plain white — texts and the small-seconds hand/ticks alike,
  always over a drop shadow so they read on both plate styles.
