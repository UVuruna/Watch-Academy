# Year Wheel

**Script:** [Year Wheel (script)](year_wheel.py)

## Purpose
Dial angle of the year marker (Earth/Moon icon): piecewise-linear
between real season instants so the summer solstice sits exactly at the
top, winter at the bottom, equinoxes exactly at 90°/270°.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `YEAR_ANCHOR_ANGLES`

### Used by
- [Seasons Repository](../data/seasons.md) — constructs `YearAnchors`
- [Clock State](clock_state.md), [Tests (folder)](../tests/___tests.md)

## Classes

### YearAnchors
Frozen: `year`, six increasing tz-aware instants (previous December
solstice → next spring equinox) paired with unwrapped angles
(180, 270, 360, 450, 540, 630).

## Functions
- `year_marker_angle(now, anchors)`: bracketing-pair interpolation,
  mod 360; raises `ValueError` outside the anchor span (wrong-year
  anchors must fail loudly, not interpolate blindly).
- `zodiac_sign(now, anchors)`: (name, symbol, start, end) of the
  tropical sign — exact 30° arcs of the same wheel (Cancer's first
  point IS the summer solstice, Capricorn's the winter solstice,
  Aries' the spring equinox); cusp instants via inverse interpolation.
