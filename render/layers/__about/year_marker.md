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
`earth_region(latitude, longitude)`, imported directly by
`render/compositor.py` for hover/tooltip text — not only used internally by
the layer. It resolves the continent LIVE from the day context's own
coordinates on every call (R-28 fix, 2026-08) — nothing about the region is
baked into the skin, so a Quick Jump/Time Travel/Greenwich simulation moves
the Earth marker's face exactly like an ordinary location change does.

THE CLEAR ORBIT LANE (owner verdict 2026-08-09, "Earth touches the outer
ring"): the QUIET (non-glowing) orbit radius is no longer the skin's own
`orbit_fraction`/`moon_orbit_fraction` fields — those are now NOMINAL,
read only by `moon_transit_opacity`'s touch-angle approximation. The
DRAWN radius is computed fresh every paint by `config.dial.
earth_moon_orbit_fraction(ring_size, half_size)`: pulled inside
WHICHEVER inner element reaches furthest out — the minute band's own
live radius (`dial.MINUTES_RADIUS_FRACTION`, scaled by
`dial.interior_scale`) or THE HEXAGRAM/PENTAGON FLOOR
(`dial.POLYGON_FILL_MIN_RADIUS_FRACTION`, added in the same
correction round after an independent grader saw the Moon sit across
the star/polygon background fill's own boundary line) — by whichever
marker is currently the bigger of the two (`max(spec.scale,
spec.moon_scale)`) plus a fixed visible clearance — so the marker's
disc never reaches the minute band's own content, the star/polygon
fill's boundary, NOR the outer hour band above it, at any dial size or
ring preset. Earth and Moon still share this ONE radius (the "same rim"
design, so a literal transit — the Moon crossing the Earth — still
exists); `render/compositor.py`'s `_element_at` hit-test computes the
identical radius so hover/click always matches the drawn position.
Pinned by `tests/test_earth_moon_orbit.py`. The GLOWING relocation below
(to the ring band centerline, during a season/eclipse event window) is
untouched — that overlap is the owner's own approved dramatic effect,
not the touching bug this law fixes.

THE POSITION POINTER (Settings ▸ Earth, off by default): `_draw_orbit_
pointer` is called AFTER the body's own pixmap/disc for both markers
(visual proof correction round 2026-08-09) — the first cut drew it
BEFORE the body, so only its outward tip's protrusion peeked past the
sphere's own edge, a sliver an independent grader read as a rendering
glitch. On top it reads as an intentional marker at a glance.

THE WORLD OFFSET ([World](../../../core/__about/world.md)): both markers are
drawn ON the turning dial face, so both take `ctx.world_offset`. At night
that is +180, which stands the WINTER solstice where the summer solstice
stood and the FULL moon where the new moon stood. The rim-transit test
between them keeps the RAW angles — the same offset on both leaves their
separation unchanged.

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
- [Config (folder)](../../../config/___config.md) — `dial.earth_moon_orbit_fraction`,
  `dial.interior_scale`, `dial.GLOW_RING_RADIUS_FRACTION`
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
`earth_region(latitude, longitude) -> str` — the Earth marker's art region:
the active location's continent (via `config.continents.
continent_from_coordinates`), except at extreme latitudes where the planet
honestly shows its pole. Both coordinates come straight from the day
context, so the region is recomputed every paint — no stale skin-baked
default.
