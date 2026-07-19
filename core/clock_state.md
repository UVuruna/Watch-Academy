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

**`eclipses` (ROADMAP 15h item 11, owner 2026-07-18):** up to 4
`EclipseEvent` candidates — the nearest catalog solar/lunar eclipse
before and after the day-context build instant — fed by the OPTIONAL
Deep Time pack (`data.deep_time.DeepTimeRepository.eclipses_near`,
one indexed jd_ut query per side, never a table scan). Defaults to `()`
and STAYS `()` without the pack — the documented absence: no eclipse
ever renders, identical to the app before this round (Rule #1).

### EclipseEvent
Frozen: `kind` ("solar" | "lunar"), `instant` (UT, proxy-shifted like
every other DayContext datetime in deep travel), `type`
(total/annular/hybrid/partial/penumbral) and `magnitude` — the render's
glow-strength input (`render.layers.eclipse_glow_strength`). Built ONLY
by the data layer from the catalog; core never touches the database.

**VISIBILITY (TASK 4, owner verdict "may", fix round E, 2026-07-19):**
`lat`/`lon` (greatest-eclipse ground point, solar only — carried
straight through from `data.deep_time.DeepEclipse`, None for lunar and
for solar rows the finder reported no point), `visible` (bool, default
True so any pre-existing caller that never touches it is unaffected)
and `distance_km` (the observer's great-circle distance to the ground
point, solar only, None when unknown). `visible`/`distance_km` are
stamped by `_with_visibility` — a PURE function of the event and the
observer's coordinates (no wall clock, matching the purity law) — the
moment `_active_eclipse` picks the winning candidate for the tick, since
that is the first point an observer is in hand: LUNAR visible ⟺ the
Moon's `astral.moon.elevation` at the instant is above 0°; SOLAR visible
⟺ the Sun's `astral.sun.elevation` (geometric, `with_refraction=False`,
same `constants.HORIZON_ELEVATION_DEG` threshold `core.sun` uses) is
above the horizon AND the haversine distance to `(lat, lon)` is within
`constants.ECLIPSE_SOLAR_VISIBILITY_KM` (3500 km). Evaluated at the
eclipse's own INSTANT, never the day's rise/set edges — the ±3h glow
window is short enough that only the instant matters.

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
(±12 h around a solstice/equinox), `moon_event` (±6 h around a
principal phase) and `eclipse_event` (±3 h around a catalog eclipse,
`constants.ECLIPSE_GLOW_WINDOW_H` — ROADMAP 15h item 11), None outside
their windows. `eclipse_event` is always None without the Deep Time
pack (`DayContext.eclipses` stays empty).

## Functions
- `build_day_context(now_local, observer, year_anchors, moon_window, eclipses=())`
- `build_tick_state(now_local, day_context)`
