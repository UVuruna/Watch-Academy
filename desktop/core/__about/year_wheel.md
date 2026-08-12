# Year Wheel

**Script:** [Year Wheel (script)](../year_wheel.py) · **Flow:** [diagram](../__flow/year_wheel.md)

## Purpose
Dial angle of the year marker (Earth/Moon icon): piecewise-linear
interpolation between six real season instants so the summer solstice
sits exactly at the top (0 deg), the winter solstice at the bottom
(180 deg), and the equinoxes exactly at 90/270 deg. Plain linear
interpolation over the whole tropical year is NOT equivalent — it puts
the autumn equinox at ~92.3 deg, a visible error the golden tests
reject.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `YEAR_ANCHOR_ANGLES`,
  `ZODIAC_SPAN_DEG`, `ZODIAC_SIGNS`, `CALENDAR_WEDGE_DEG`

### Used by
- [Seasons Repository](../../data/__about/seasons.md) — constructs `YearAnchors`
- [Clock State](clock_state.md) — `year_marker_angle`, `zodiac_sign`
- [Tests (folder)](../../tests/___tests.md) — exact-equinox goldens

## Classes

### YearAnchors
Frozen: `year`, six strictly increasing tz-aware UTC `instants`
(instants[0] = the December solstice BEFORE the year, instants[5] = the
spring equinox AFTER it — any timestamp inside the calendar year falls
between two anchors without stitching neighbor years), paired with their
unwrapped `angles` (default `constants.YEAR_ANCHOR_ANGLES`, i.e.
180, 270, 360, 450, 540, 630).

## Functions
- `year_marker_angle(now, anchors)`: dial angle of the year marker
  (degrees, clockwise, 0 = top); raises `ValueError` when `now` falls
  outside the anchor span.
- `almanac_month_index(month)`: the Almanac wheel's wedge index (0..11),
  counted clockwise from June = wedge 0.
- `almanac_marker_angle(when)`: dial angle of the Earth marker on the
  Calendar pointer's Almanac wheel — every month spans exactly 30 deg,
  the 1st on the wedge-start line, day D at `(D-1)/days_in_month` into
  the wedge; leap February rides the real calendar
  (`calendar.monthrange`).
- `instant_at_marker_angle(anchors, dial_angle, southern=False)`: public
  inverse of `year_marker_angle` (the ring-tick hover) — un-mirrors the
  southern wheel first (+180 deg south of the equator).
- `zodiac_sign(now, anchors)`: `(name, symbol, start, end)` of the
  tropical zodiac sign at `now` — signs are exact 30-deg arcs of the
  same year wheel (Cancer's first point IS the summer solstice,
  Capricorn's the winter solstice, Aries' the spring equinox).
- `zodiac_span(anchors, start_dial_angle)`: cusp instants of any sign by
  its start angle.
- `meteorological_span(anchors, center_angle)`: meteorological season
  bounds around an anchor — each bound lies halfway between neighboring
  anchor instants, so every season centers on its solstice/equinox.
- `_unwrapped_angle(now, anchors)` / `_instant_at(anchors, unwrapped_angle)`:
  the shared bracketing-pair interpolation and its inverse — module-
  private.

## Design Decisions
- The anchor span must bracket `now` exactly — outside it,
  `_unwrapped_angle` raises rather than extrapolate, since that means
  the anchors were built for the wrong year and must be visible, not
  silently interpolated.
