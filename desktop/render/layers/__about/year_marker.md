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

THE LINE AND THE BODIES (owner correction 2026-08-10, the four-styles
screenshot round — SUPERSEDES the 2026-08-09 "clear orbit lane"
clearance and its hexagram-apothem floor): the QUIET (non-glowing)
orbit radius is computed fresh every paint by `config.dial.
earth_moon_orbit_fraction(ring_size, half_size)`, now a PER-BODY
TANGENT fit — `dial.RING_INNER_CONTENT_INNER_FRACTION` (THE LAST
LINE: the inner side of the inner ring, where the five-minute
strokes/arrows/numbers stop, owner third round 2026-08-11 — so the
body never slices any inner-ring element) scaled by
`dial.interior_scale`, minus THIS body's own half-size — BOTH bodies
touch that line, each on its own radius, and the Moon Horizon Band's
thread rides the SAME line behind them. The
skin's own `orbit_fraction`/`moon_orbit_fraction` fields stay NOMINAL,
read only by `moon_transit_opacity`'s touch-angle approximation.
A literal transit — the Moon crossing the Earth — still exists (the
two radii differ only by the bodies' half-size difference);
`render/compositor.py`'s `_element_at` hit-test computes the identical
radius so hover/click always matches the drawn position. Pinned by
`tests/test_earth_moon_orbit.py`. The GLOWING relocation below (to the
ring band centerline, during a season/eclipse event window) is
untouched — that overlap is the owner's own approved dramatic effect.
The position pointer is drawn BEHIND the body (owner correction
2026-08-11, "IZA NE ISPRED ZEMLJE" — his second time saying it), its
dimensions proportional to the body's own half-size, bridging the
tick zone: base hidden under the disc, tip on the thread line at the
tick roots (`tests/test_marker_pointer.py`). The 2026-07-12
below-horizon Moon dimming is RETIRED (owner 2026-08-11, "mesec opet
ima OPACITY!!!") — the band says whether the Moon is up; the disc is
always solid; `moon_hidden_alpha` stays stored but unread.

THE POSITION POINTER (off by default) lives in
[`marker_marks.draw_pointer`](../../__about/marker_marks.md) since
2026-08-10, when the owner approved a chevron and a gem beside the
triangle; every shape rides the body's own dial angle rather than a
fixed screen "up". Its z has flipped twice: the 2026-08-09 grader round
moved it ON TOP of the body, and the owner's 2026-08-11 screenshot
round reversed that as wrong — it is BEHIND the body now (see THE LINE
AND THE BODIES above), which is what he had asked for the first time.

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
- `_draw_moon()`: hands the face to
  [`render.moon_face`](../../__about/moon_face.md), which owns the three
  owner-approved treatments of the unlit half and decides whether the
  face is clipped first (the cut styles) or covered after (the opaque
  one). A lunar eclipse then takes one of three routes: "umbra_sweep"
  draws Earth's shadow as a real curved edge across the disc,
  "halo" keeps the older whole-disc multiply by a neutral (or copper, at
  totality) gray, and "horizon_shadow" leaves the disc alone because the
  event is written on the Moon Horizon Band instead.
- `_day_fraction(day_length)`: the day's share of 24 h, parsed off the
  SAME "HH:MM" string the octa's bottom arm displays — the Sun's
  day/night wedge station is a picture of that number, so the two
  cannot disagree.

THE MOVING BODIES (owner verdict 2026-08-10). Everything about HOW the
two markers are drawn is now a user menu, picked in Watch Face ▸ Hands &
Bodies and carried on the spec: the unlit half, the crossing, the
pointer's shape, both eclipse treatments and both bodies' four life
stations. This layer only dispatches — the drawing lives in
[`moon_face`](../../__about/moon_face.md) and
[`marker_marks`](../../__about/marker_marks.md).

THE FOUR STATIONS take the halo's place at a principal instant: new moon
is birth, first quarter youth, full moon the zenith of maturity, last
quarter age, and the Sun's four turning points are the same arc across
the year. An eclipse outranks a station — when both fall on one tick the
eclipse's own treatment is what shows.

THE CROSSING no longer dims anything. The translucent pass was retired
with the owner's cross on the proposals page; the three survivors read
`moon_transit_nearness` and either split the lane, shrink the Moon, or
let it occult the Earth outright.

### earth_region (module function)
`earth_region(latitude, longitude) -> str` — the Earth marker's art region:
the active location's continent (via `config.continents.
continent_from_coordinates`), except at extreme latitudes where the planet
honestly shows its pole. Both coordinates come straight from the day
context, so the region is recomputed every paint — no stale skin-baked
default.
