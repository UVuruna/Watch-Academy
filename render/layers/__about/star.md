# Star Layer

**Script:** [Star Layer (script)](../star.py) ·
**Flow:** [diagram](../__flow/star.md)

## Purpose

Paints the drawn wheel: an N-diamond STAR or the plain POLYGON of the same
arms (owner sheet 2026-07-29), whose top arm points at true solar noon (or
straight up with solar rotation off). Colored near-full opacity where the
sun is up, colored borders everywhere else so night arms stay recognizable.
The armless Aurora pointer draws nothing here at all — it IS the pointer,
drawn one layer down by `BackgroundLayer`; the Calendar pointer draws its
own two hexagrams / twelve-point star over its own wedges through this same
class.

`Cadence.DAILY`: which arcs are lit (`lit_regions(ctx.day.sun, ...)`) and
where the border clips fall depend only on the day's sunrise/sunset, not the
live tick. Not `hover_variable` — the star has no individually-hoverable
elements (arm hover text is a `Compositor` hit-test over the geometry, not a
`ctx.hovered` gate on this layer).

## Connections

### Uses
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Daylight](../../__about/daylight.md) — `border_clips`, `lit_regions`
- [Painting](../../__about/painting.md) — `pie_path`
- [Shapes](../../__about/shapes.md) — `arm_shape_path` (the one arm/polygon path every
  pointer's paint AND hit-test share), `drawn_arms` (z-order of every arm of
  every pass — the Rose's three stars bottom-first, the Calendar's odd
  hexagram under its even one)
- [Skin Geometry](../../__about/skin_geometry.md) — `daylight_active`, `palette_for`,
  `wheel_rotation`

### Used by
- [Compositor](../../__about/compositor.md) — second layer in the default `z_order`,
  stacked into the cached DAILY composite; skipped entirely when
  `show_pointer` is off

## Classes

### StarLayer
`cadence = Cadence.DAILY`.
- `paint()`: returns immediately for the Aurora pointer; otherwise draws a
  colored-BORDER pass over `border_clips()` (full circle unless the reader
  hid night borders), then a colored-FILL pass over `lit_regions()` — or the
  whole wheel at full color when the daylight switch is off.
- `_paint_pass()`: one whole-wheel pass at a given alpha, optionally clipped
  to a dial arc in wall-clock space, with the wheel itself drawn inside its
  own rotated frame (`wheel_rotation`).
- `_draw_arms()`: draws every arm/polygon face in `drawn_arms()` z-order;
  fills are stroked with the owner's lead-line pen AS they are filled (the
  outline follows the z-stack and shared internal edges come free); borders
  are clipped to the arm shape and stroked at double width so only the inner
  half shows, `IntersectClip` so a night-hiding clip from `_paint_pass`
  survives.
