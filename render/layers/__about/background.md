# Background Layer

**Script:** [Background Layer (script)](../background.py) ·
**Flow:** [diagram](../__flow/background.md)

## Purpose

Paints the dial's lowest visual layer: the UMBRA (a gray brightness wheel,
lightest at true solar noon, darkest at true solar midnight) and the AURA
(the colored hue wedges over the sunlit part of the day — or the fixed
twelve Calendar wedges, or the armless Aurora bands). Both rotate with the
star (`ctx.rotation`) unless solar rotation is off, in which case they stand
upright. THE DAYLIGHT SWITCH (owner correction 2026-07-29): with
`daylight_active(skin)` False — only the Calendar and the Rose pointers —
day and night vanish from the WHOLE dial (flat noon everywhere), not just
the star.

`Cadence.DAILY`: the Umbra/Aura shape depends only on the day's sunrise and
sunset times (`ctx.day.sun`) and the skin, never on the live tick — it does
not need to repaint every minute, only when the day context changes. Not
`hover_variable` — nothing on this layer is individually hoverable, so it
is safe to bake into the cached STATIC/DAILY composite.

## Connections

### Uses
- [Calendar Mount](../../__about/calendar_mount.md) — `_draw_calendar_mount`,
  `calendar_wedge_bounds`, `calendar_wheel` for the Calendar pointer's
  twelve 2-hour wedges and optional mount
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Daylight](../../__about/daylight.md) — `aurora_bands`, `lit_regions`, `umbra_ladder`
- [Painting](../../__about/painting.md) — `draw_pie`, `draw_pixmap_centered`, `pie_path`,
  `tinted_gray`
- [Shapes](../../__about/shapes.md) — `aura_wedge_bounds` (each hue's wedge anchored on its
  own lead ray)
- [Skin Geometry](../../__about/skin_geometry.md) — `aura_palette_for`, `daylight_active`

### Used by
- [Compositor](../../__about/compositor.md) — first layer in the default `z_order`,
  stacked into the cached DAILY composite

## Classes

### BackgroundLayer
`cadence = Cadence.DAILY`.
- `paint()`: draws the Umbra (asset or procedural), then dispatches on
  `ctx.skin.pointer` — Aurora draws hue bands with no wedge geometry,
  Calendar draws twelve calendar-fixed wedges (rotation 0) plus its optional
  mount, everything else draws the per-hue Aura wedges anchored on the
  star's own rays.
- `_paint_aura()`: the ONE law shared by every wedge-carrying pointer
  (Rule #5) — clips to each lit arc and draws every hue's wedge at that
  arc's alpha when the daylight law runs, or draws the whole circle at
  `day_alpha` when it is switched off.
- `_draw_umbra()`: the brightness wheel — a per-skin `umbra_asset`, a
  per-pixel conical gradient, or discrete mirrored pie sections
  (`umbra_form`), tinted by `ring_tint`; flat-noon single circle when the
  daylight switch is off.
