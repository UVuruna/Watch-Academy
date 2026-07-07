# Angles

**Script:** [Angles (script)](angles.py)

## Purpose
The single time→dial-angle mapping (Rule #5). Degrees, clockwise, 0 at
the dial top — ready for `QPainter.rotate()`.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `DIAL_OFFSET_DEG`,
  `SOLAR_NOON_SECS`, `SECONDS_PER_DEGREE`

### Used by
- [Clock State](clock_state.md), [Sun](sun.md) consumers, the render
  layers (M3), [Tests (folder)](../tests/___tests.md)

## Functions
- `time_to_dial_angle(t)`: 12:00→0°, 18:00→90°, 00:00→180°, 06:00→270°
- `minute_hand_angle(t)`: one revolution per hour
- `hexagram_rotation_deg(solar_noon)`: +15°/hour of solar-noon lateness
  (positive = clockwise = west-in-zone or DST; negative = east-in-zone)
