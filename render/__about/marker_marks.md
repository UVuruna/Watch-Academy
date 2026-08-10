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
  protrusion/recess geometry), `palette` (`INSTRUMENT_SEASON_COLORS`,
  the marker border, the glow colours)

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `YearMarkerLayer`
  draws every pointer, station mark and solar eclipse through here
- [Watch Face (folder)](../../app/___app.md) — `thumbs` builds each
  picker's preview from the same functions

## Functions
- `draw_pointer(painter, shape, angle_deg, radius, edge_fraction, half_size_fraction, color)`
- `draw_station_mark(painter, style, station, radius, color)` — the
  Moon's grammar; `draw_sun_station_mark(...)` is its solar twin, which
  adds the seasonal halo and the day/night wedge.
- `draw_solar_eclipse(painter, style, radius, state, magnitude, paint_face)`
- `station_of_moon_event(name)` / `station_of_season_event(name)` — the
  event name a tick already carries, resolved to one of the four
  stations, or None when the instant is not a principal one.
