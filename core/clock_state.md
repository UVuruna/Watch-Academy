# Clock State

**Script:** [Clock State (script)](clock_state.py)

## Purpose
The two-tier render state consumed by the compositor (M3): a frozen
per-day bundle and a tiny per-minute tick.

## Connections

### Uses
- [Angles](angles.md), [Sun](sun.md), [Year Wheel](year_wheel.md),
  [Moon](moon.md)

### Used by
- [App Controller](../app/controller.md) (M3) — rebuild/tick flow
- [Core (folder)](___core.md) CLI selftest

## Classes

### DayContext
Frozen: local date, UTC offset, weekday index (Monday=0), `SunDay`,
hexagram rotation, `YearAnchors`, moon fraction/illumination, and
`southern_hemisphere` (the moon renders rotated 180° there).
`cache_key = (local_date, utc_offset)` — the offset component catches
DST transitions, where the hexagram legitimately jumps 15°.

### TickState
Frozen: hour angle, minute angle, year angle (recomputed per tick to
stay smooth — it moves ~1°/day), and `is_daylight` (sun above the horizon
right now; drives the Earth marker's day/night image — correct even on
inverted midnight-sun transition days where sunset precedes sunrise).

## Functions
- `build_day_context(now_local, observer, year_anchors, moon_window)`
- `build_tick_state(now_local, day_context)`
