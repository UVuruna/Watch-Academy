# Slot Layer

**Script:** [Slot Layer (script)](../slot.py) ·
**Flow:** [diagram](../__flow/slot.md)

## Purpose

Paints every SEATED subdial complication (owner matrix 2026-07-14): small
seconds, full date, time, day-length, weekday (in its own seat theme/roster),
zodiac/ascendant sign, or the Chinese animal — at whatever matrix position
`slot_layout()` assigns it. Angle seats ride the star's rotation; a "center"
seat sits on the hub. The classic weekday unit (undecorated, following the
skin's own theme) belongs to `WeekdayLayer` instead — this layer only draws
slots the owner has explicitly SEATED.

`Cadence.MINUTE`: the ascendant sign moves hourly and the small-seconds hand
repaints on the per-second tick, so the whole layer must repaint live every
tick even though most of its own slots (date, zodiac, weekday) only change
daily. Not `hover_variable` — `MINUTE` already repaints every frame.

## Connections

### Uses
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Painting](../../__about/painting.md) — `dial_point`, `draw_pixmap_centered`
- [Skin Geometry](../../__about/skin_geometry.md) — `hover_factor`
- [Slot Layout](../../__about/slot_layout.md) — `slot_layout`, `slot_seat_orbit`,
  `slot_seat_rotation`, `slot_seat_scale`, `slot_view`
- [Subdial](../../__about/subdial.md) — `display_year`, `draw_fitted_text`,
  `draw_slot_roundel`, `draw_small_seconds`, `draw_two_lines`,
  `octa_slot_art`, `slot_text`
- [Weekday Body](../../__about/weekday_body.md) — `draw_body_label`, `draw_weekday_body`
- [Skins (folder)](../../../skins/___skins.md) — `SkinDefinition`

### Used by
- [Compositor](../../__about/compositor.md) — TWO instances by default: an angle-seated
  one below the hands (when any seat is not "center") and a centered one
  above the hands (when a seat IS "center")
- [Hover Lift Layer](hover_lift.md) — a THIRD, `lift=True` instance repaints
  whichever seated slot is hovered, above the hands — covering both angle
  and center seats through the one instance (see Design Decisions in
  [Layers (folder)](../___layers.md))

## Classes

### SlotLayer
`cadence = Cadence.MINUTE`.
- `__init__(skin, centered=False, lift=False)`: `centered` picks which of
  the two non-lift instances this is; `lift` (inherited constructor arg)
  makes it the hover twin instead.
- `paint()`: iterates every seated index from `slot_layout()`, skips the
  "classic" seat (WeekdayLayer's own) and — for a non-lift instance — any
  seat whose "is it center?" doesn't match `self._centered`, then gates each
  remaining seat through `Layer._gate` before positioning and sizing it
  (`slot_seat_rotation`/`slot_seat_orbit`/`slot_seat_scale`, each scaled
  again by `hover_factor`).
- `_draw_slot()`: dispatches on the seat's `mode` (from `slot_view`) —
  seconds / date / time / day_length draw a roundel plus fitted/two-line
  text; weekday delegates to `_draw_weekday_slot`; zodiac/ascendant and
  Chinese draw style-specific art (colored badge, flat glyph-on-subdial, or
  a text fallback until the art lands).
- `_draw_weekday_slot()`: resolves today's body art in THIS slot's own
  theme/roster/metal — a Pantheon seat, a themed weekday body, or the
  documented roundel-and-text fallback when no art exists on disk yet.
