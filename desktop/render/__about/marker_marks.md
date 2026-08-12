# Marker Marks

**Script:** [Marker Marks (script)](../marker_marks.py) · **Flow:** [diagram](../__flow/marker_marks.md)

## Purpose
Everything drawn AROUND an Earth/Moon marker rather than on its face:
the position pointer's three shapes, the four life stations' marks, and
the solar eclipse's own geometry. One module because all three answer
the same question with the same inputs — given a body at a dial angle,
with a radius, what ornament does it wear? — and all three were
approved in the owner's single 2026-08-10 pass over the
rendering-proposals page.

The Moon's own FACE is the other half and lives in
[Moon Face](moon_face.md); the halo behind a relocated marker is older
and still lives in [Eclipse Glow](eclipse_glow.md).

## The angle is never "up"
Every mark here takes the body's own dial angle and is built from
`painting.dial_point`, so it points along the RADIUS at the body's
actual seat on the circle. This is written down because the owner had
to correct it once (2026-08-10): the proposals page drew each pointer
straight up, which is only correct for a body at the top of the dial.
The shipped code was already radial — the mockup was the thing that was
wrong — and `tests/test_marker_pointer.py` pins it for all three shapes
so the drawing and the drawings of the drawing cannot drift again.

## The 2026-08-10 screenshot corrections
The owner's four-styles screenshot round re-cut two of the three
shapes: the CHEVRON is now the SAME triangle geometry drawn as LINE
only (the open-V first cut was far too wide and looked unrelated to
the triangle beside it). All three are PROPORTIONAL to the body's own
half-size, drawn BEHIND the body ("IZA NE ISPRED ZEMLJE"), bridging
the tick zone: base hidden under the disc, tip on the thread line at
the tick roots (`dial.earth_moon_orbit_fraction`'s tangent fit puts
the body's edge on the little pointers' tip line).

## The direction follows the body (owner correction 2026-08-11)
`draw_pointer` takes an optional `tip_radius` — the marked point's own
radius, the 360 small pointers' tips. A body on its ordinary orbit
sits INSIDE that circle, so the arrow points OUTWARD, as before; a
body relocated onto the ring band (its event window) sits OUTSIDE it,
so the arrow FLIPS and points INWARD at the same marked point instead.
`tip_radius=None` reproduces the ordinary outward case from the
measured plate ratio, unchanged. The owner's own words for the flip:
"obrni strelicu... jer je sada na RINGU" (slika 4/5).

## The gem, rewritten (owner correction 2026-08-11)
The GEM shape no longer hides part of itself under the disc: one
vertex sits on the body's own edge, the other on the marked point, and
the WHOLE diamond lives in the gap between the body's circle and the
360 tips' circle (slika 2/3 — parts under the disc used to make it
read like the triangle beside it). Its width is a fraction of its own
height (`dial.MARKER_GEM_WIDTH_RATIO`, always < 1) so height is never
less than width — "ako je ista vrednost moze blago veca visina".
`MARKER_GEM_LENGTH_RATIO` is retired; the gem's length is now simply
the gap itself.

## The stations
New moon is birth, first quarter youth, full moon the zenith of
maturity, last quarter age; winter solstice, spring equinox, summer
solstice and autumn equinox are the same arc across the year. Both
bodies share one grammar so the language is learned once and read on
two clocks — the reason `arc_grammar` is the default for each.

`inner_glow` follows the owner's own specification of intensity: the
glow's RADIUS never changes, only its alpha, so a full moon burns
brighter rather than reaching further. Youth carries a glow both inside
the dark half and outside; age carries the same OUTER strength with no
inner glow at all; birth carries light almost entirely inside. The
numbers are `constants.MOON_STATION_GLOW`.

## Connections

### Uses
- [Painting](painting.md) — `dial_point`, the one clockwise-from-top
  polar conversion
- [Moon Face](moon_face.md) — `dark_region`, so the inner glow and the
  shadow agree about where the dark half is
- [Config (folder)](../../config/___config.md) — `constants` (the
  rosters, the glow ramp, the station lookups), `dial` (the pointer's
  proportional length/width ratios and the tick-line measurements), `palette` (`INSTRUMENT_SEASON_COLORS`,
  the marker border, the glow colours)

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `YearMarkerLayer`
  draws every pointer, station mark and solar eclipse through here
- [Watch Face (folder)](../../app/___app.md) — `thumbs` builds each
  picker's preview from the same functions

## The eclipse "bite", repainted as seen (owner correction 2026-08-11)
A black offset-occulter circle over the already-black eclipse art was
invisible ("ne moze crni isecak na crnoj eklipsi") — the base art
under the bite is now `config.defaults.ECLIPSE_SOLAR_ART`, the owner's
own icon (a black disc in rays), and the bite paints only the VISIBLE
remainder: a bright crescent shaped by the SAME terminator construction
the Moon's own phases use (`render.asset_variants.moon_lit_region`),
the cycle-fraction inverted (via `acos`) so the crescent's AREA matches
the Sun's visible share. Totality adds nothing — the icon alone is the
look; annular draws the ring of fire around the black disc; a partial
phase draws the crescent over it. The old procedural corona-spikes
block is gone with the two-circle bite it drew.

## Functions
- `draw_pointer(painter, shape, angle_deg, dial_radius, orbit_fraction, half_size_fraction, color, tip_radius=None)`
- `draw_station_mark(painter, style, station, radius, color)` — the
  Moon's grammar; `draw_sun_station_mark(...)` is its solar twin, which
  adds the seasonal halo and the day/night wedge.
- `draw_solar_eclipse(painter, style, radius, state, magnitude, paint_face)`
- `station_of_moon_event(name)` / `station_of_season_event(name)` — the
  event name a tick already carries, resolved to one of the four
  stations, or None when the instant is not a principal one.
