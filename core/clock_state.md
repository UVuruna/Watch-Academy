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
star rotation, `YearAnchors`, the `MoonWindow` (principal-phase
instants — the tick reads the LIVE cycle fraction from it),
`southern_hemisphere` (the moon renders rotated 180° there), the day
length string ("15:25", the octa slot option), the tropical zodiac sign
(name, symbol, local start/end dates — cusps ride the year wheel), the
Chinese year ("Fire Horse" + start/end dates, CNY derived from the
bundled new-moon instants), the season/moon event instants with their
names (glow inputs) and the active tzinfo (hover instant display).
`cache_key = (local_date, utc_offset)` — the offset component catches
DST transitions, where the star legitimately jumps 15°.

**`deep_cycles` (Session 16, owner 2026-07-17):** every datetime in the
context lives in the 400-year PROXY frame shifted by this many
Gregorian cycles (0 in normal operation). The real astronomical year of
any of them is `core.deep_time.real_year(dt.year, deep_cycles)` —
display sites convert before formatting a year, and the analytic
illumination evaluates at the real epoch. The CONTROLLER stamps it
after the build (`build_day_context` itself is frame-agnostic — the
proxy mapping is exact, so its computations need no awareness).

### TickState
Frozen: hour angle, minute angle, year angle (recomputed per tick to
stay smooth — it moves ~1°/day), `moon_fraction`/`moon_illumination`
(LIVE per minute — owner bug 2026-07-14: a day-time New Moon must wrap
the marker at its instant, not at the next day-context rebuild;
`moon_illumination` is the TRUE analytic value since Session 16,
evaluated at the real epoch in deep travel),
`is_daylight` (sun above the horizon right now; drives the Earth
marker's day/night image — correct even on inverted midnight-sun
transition days where sunset precedes sunrise), `time_hm` (the octa
slot's digital time) and the active glow events: `season_event`
(±12 h around a solstice/equinox) and `moon_event` (±6 h around a
principal phase), None outside their windows.

## Functions
- `build_day_context(now_local, observer, year_anchors, moon_window)`
- `build_tick_state(now_local, day_context)`
