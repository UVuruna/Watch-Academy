# Angles

**Script:** [Angles (script)](../angles.py) · **Flow:** [diagram](../__flow/angles.md)

## Purpose
The single time -> dial-angle mapping (root Rule #5 — one shared formula,
never duplicated inline). Every angle is degrees, clockwise, 0 at the
dial top, ready for `QPainter.rotate()` in y-down screen coordinates —
the project's dial convention (`DIAL_OFFSET_DEG = 180`).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `DIAL_OFFSET_DEG`,
  `SOLAR_NOON_SECS`, `SECONDS_PER_DEGREE`, `SECONDS_PER_HOUR`,
  `SECONDS_PER_DAY`

### Used by
- [Clock State](clock_state.md) — `time_to_dial_angle`, `minute_hand_angle`,
  `second_hand_angle`, `star_rotation_deg`
- [Ascendant](ascendant.md) does NOT use this module (its own sidereal
  math is self-contained)
- [Motto](motto.md) — `ring_position_angle`, `readable_rotation_deg`
- [Layers](../../render/layers/___layers.md), [Compositor](../../render/__about/compositor.md)
  (render layer, M3) — hour hand, ring letters, hover geometry
- [Tests (folder)](../../tests/___tests.md) — golden angle values

## Functions
- `time_to_dial_angle(t)`: 12:00 -> 0 deg, 18:00 -> 90 deg, 00:00 -> 180 deg,
  06:00 -> 270 deg — the hour-hand mapping.
- `minute_hand_angle(t)`: one revolution per hour, 0 at the top.
- `second_hand_angle(t)`: one revolution per minute (`t.second * 6.0`) —
  unused while the dial ships with no seconds hand, but present for a
  future skin.
- `moon_cycle_angle(fraction)`: new moon at the top (0 deg), full moon at
  the bottom (180 deg), clockwise.
- `ring_position_angle(position)`: dial angle of a FIXED ring position/hour
  (the six hexagram seats and every other ring hour) — the base every
  [Motto](motto.md) glyph angle is built from.
- `readable_rotation_deg(theta)`: the glyph rotation that keeps ring-band
  letters upright all the way around — the lower half (90-270 deg) flips
  180 deg so text never reads upside down.
- `hours_between(angle_a, angle_b)`: shortest SIGNED hours from `angle_b`
  to `angle_a`, wrapped to [-12, 12) — 15 deg/hour, the same mapping
  `time_to_dial_angle` uses. Pure building block for solar-anchor
  time-window comparisons (e.g. the render layer's center-face logic).
- `star_rotation_deg(solar_noon)`: rotation of the star/solar-noon arrow
  from the dial top — +15 deg/hour of solar-noon lateness (positive =
  clockwise = city west of its zone meridian or DST active).
