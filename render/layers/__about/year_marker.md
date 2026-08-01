# Year Marker Layer

**Script:** [Year Marker Layer (script)](../year_marker.py) ·
**Flow:** [diagram](../__flow/year_marker.md)

## Purpose

Paints the date markers along the inside of the dial: the Earth (riding the
year wheel, summer solstice at the top — or the Calendar's own almanac
month wedges) and the Moon (riding its own cycle, new moon at the top, full
at the bottom, clockwise, showing the current illumination). The Elements
switches (`show_earth`/`show_moon`) pick which of the two draws. During a
±12h (Earth) or ±6h (Moon) event window — a season turning point, a solar
or lunar eclipse — the marker RELOCATES radially onto the ring band
centerline and grows a colored glow (golden/silver normally, red/bronze for
an eclipse, muted silver when the eclipse is real but not visible from the
active location). The module also exports a standalone helper,
`earth_region(latitude, default)`, imported directly by
`render/compositor.py` for hover/tooltip text — not only used internally by
the layer.

`Cadence.MINUTE`: eclipse windows, season-event glow and moon transit
opacity are all evaluated against `ctx.tick`, and both markers relocate
within a tick-scale window — needs a per-tick repaint. Not `hover_variable`
— `MINUTE` already repaints every frame; the individually-hoverable "earth"
and "moon" elements are gated with `Layer._gate` like any other MINUTE
layer, and their lift twin lives in `HoverLiftLayer`.

## Connections

### Uses
- [Asset Variants](../../__about/asset_variants.md) — `moon_lit_region`
- [Calendar Mount](../../__about/calendar_mount.md) — `calendar_day_arrow`,
  `calendar_wheel`
- [Render Context](../../__about/context.md) — `Cadence`, `Layer`, `RenderContext`
- [Daylight](../../__about/daylight.md) — `moon_transit_opacity`
- [Eclipse Glow](../../__about/eclipse_glow.md) — `draw_event_glow`,
  `eclipse_render_state`, `eclipse_state_glow_strength`
- [Painting](../../__about/painting.md) — `dial_point`, `draw_outlined_text`,
  `draw_pixmap_centered`, `tinted_gray`
- [Skin Geometry](../../__about/skin_geometry.md) — `hover_factor`
- [Subdial](../../__about/subdial.md) — `display_year`

### Used by
- [Compositor](../../__about/compositor.md) — fifth layer in the default `z_order`
  (skipped when both `show_earth` and `show_moon` are off); also imports
  the module-level `earth_region()` function directly for hover text
- [Hover Lift Layer](hover_lift.md) — a `lift=True` twin repaints whichever
  of "earth"/"moon" is hovered, above the hands

## Classes

### YearMarkerLayer
`cadence = Cadence.MINUTE`.
- `paint()`: draws the Earth then the Moon, each gated independently by its
  own Elements switch and `Layer._gate`.
- `_draw_earth()`: resolves the year-wheel angle (almanac month wedge under
  the Calendar pointer, the shared six-anchor season wheel otherwise),
  relocates + glows during a season/solar-eclipse window, picks the
  region/day-night art variant (`earth_region()` below), clips to the
  marker disc, and draws the FOUR exclusive label modes
  (`_draw_earth_label`: weekday / date / date+weekday / full date+year).
- `_draw_moon()`: draws the moon image or a procedural disc, masks the
  unlit region via the lit/terminator path (`moon_lit_region`), and — during
  a lunar eclipse — multiplies the WHOLE disc by a neutral (or copper, for
  totality) gray to darken it without a translucent color wash.

### earth_region (module function)
`earth_region(latitude, default) -> str` — the Earth marker's art region:
the active location's continent, except at extreme latitudes where the
planet honestly shows its pole.
