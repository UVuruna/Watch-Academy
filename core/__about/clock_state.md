# Clock State

**Script:** [Clock State (script)](../clock_state.py) · **Flow:** [diagram](../__flow/clock_state.md)

## Purpose
The two-tier render state consumed by the compositor: a frozen per-day
bundle (`DayContext`) rebuilt only when its cache key changes, and a
tiny per-minute tick (`TickState`) rebuilt every minute.

## Connections

### Uses
- [Angles](angles.md) — `star_rotation_deg`, `time_to_dial_angle`,
  `minute_hand_angle`, `second_hand_angle`
- [Ascendant](ascendant.md) — `ascendant_sign` on every tick
- [Blue Moon](blue_moon.md) — `chinese_leap_month`,
  `thirteenth_candidates`, computed once per day
- [Moon](moon.md) — `MoonWindow`, `chinese_zodiac`, `illumination`,
  `moon_rise_set`, `phase_fraction`
- [Sun](sun.md) — `DaylightRegime`, `SunDay`, `compute_sun_day`,
  `day_length_hm`
- [Year Wheel](year_wheel.md) — `YearAnchors`, `year_marker_angle`,
  `zodiac_sign`
- [Config (folder)](../../config/___config.md) — `MOON_PHASE_FRACTIONS`,
  `TROPIC_LATITUDE_DEG`, `ZONE_SEASON_EVENT_NAMES`,
  `SEASON_GLOW_WINDOW_H`, `MOON_GLOW_WINDOW_H`, `ECLIPSE_GLOW_WINDOW_H`,
  `HORIZON_ELEVATION_DEG`, `ECLIPSE_SOLAR_VISIBILITY_KM`,
  `EARTH_RADIUS_KM`
- astral 3.2 (`astral.Observer`, `astral.moon.elevation`,
  `astral.sun.elevation`)

### Used by
- [Watch Controller](../../app/__about/controller.md) — the rebuild/tick flow
- [__main__ (CLI selftest)](__main__.md) — prints the built state
- [Data (folder)](../../data/___data.md) — feeds `YearAnchors`/`MoonWindow`
  built elsewhere into `build_day_context`
- [Render (folder)](../../render/___render.md) — consumes
  `DayContext`/`TickState` every paint

## Classes

### DayContext
Frozen: `local_date`, `utc_offset`, `weekday_index` (Monday=0), `sun`
(`SunDay`), `star_rotation`, `year_anchors` (`YearAnchors`), `moon_window`
(`MoonWindow` — the minute tick reads the LIVE cycle fraction from it),
`moonrise`/`moonset` (`None` when the event skips that date),
`southern_hemisphere` (the moon renders rotated 180 deg there), `zone`
("north" | "tropics" | "south"), `day_length` ("15:35" string),
`zodiac_name`/`zodiac_symbol`/`zodiac_start`/`zodiac_end` (tropical sign
+ local cusp dates), `chinese_name`/`chinese_start`/`chinese_end`
("Fire Horse" + CNY-derived dates), `season_events`/`moon_events`
(anchor instants + names, the glow inputs), `anchor_day_lengths` (day
length at each of the six season anchors), `tzinfo`, `latitude`/
`longitude` (default 0.0 — feed the Ascendant), `eclipses` (default `()`
— up to 4 `EclipseEvent` candidates, populated ONLY by the optional Deep
Time pack), `thirteenth_candidates` (default `frozenset()` — the Blue
Moon Law's fact set), `chinese_leap_month_number` (default `None`),
`deep_cycles` (default 0 — the 400-year proxy shift the controller
stamps after the build).
`cache_key = (local_date, utc_offset)` — the offset component catches
DST transitions, where the star legitimately jumps 15 deg.

### EclipseEvent
Frozen: `kind` ("solar" | "lunar"), `instant` (UT, proxy-shifted),
`type` (total/annular/hybrid/partial/penumbral), `magnitude`
(`float | None`), `lat`/`lon` (greatest-eclipse ground point, solar
only, `None` otherwise), `visible` (default `True`), `distance_km`
(default `None`). Built ONLY from the optional Deep Time pack — absent
it, `DayContext.eclipses` is always empty and no eclipse ever renders.
`visible`/`distance_km` are stamped by the module-private
`_with_visibility` at the moment `_active_eclipse` picks the winning
candidate for the tick — a pure function of the event and the observer's
coordinates: LUNAR visible iff the Moon's elevation at the instant is
above 0 deg; SOLAR visible iff the Sun's geometric elevation is above
`HORIZON_ELEVATION_DEG` AND the haversine distance to `(lat, lon)` is
within `ECLIPSE_SOLAR_VISIBILITY_KM`.

### TickState
Frozen: `hour_angle`, `minute_angle`, `second_angle` (used only when a
seconds hand is on), `year_angle` (recomputed per tick to stay smooth —
moves ~1 deg/day), `moon_fraction`/`moon_illumination` (LIVE per
minute), `is_daylight`, `is_moon_up`, `time_hm` ("14:34"),
`season_event`/`moon_event` (`str | None`, active within their glow
windows), `ascendant_sign` (default `""`), `eclipse_event`
(`EclipseEvent | None`, default `None` — always `None` without the Deep
Time pack).

## Functions
- `build_day_context(now_local, observer, year_anchors, moon_window, eclipses=())`
  -> `DayContext`
- `build_tick_state(now_local, day)` -> `TickState`
- `_active_eclipse(now, day, window_hours)`, `_with_visibility(event, lat, lon)`,
  `_great_circle_km(lat1, lon1, lat2, lon2)` (haversine, mean Earth
  radius) — the eclipse visibility pipeline, module-private.
- `_active_event(now, events, window_hours)` — shared glow-window lookup
  for season/moon events.
- `_is_moon_up(now, day)` — dims the moon marker below the horizon; both
  rise and set missing (polar edge) is treated as "up" (dimming a moon
  someone can see would be the worse lie).
- `_is_daylight(now, sun)` — regime-aware daylight test, including the
  inverted-midnight-sun day where sunset precedes sunrise.

## Design Decisions
- Events may be `None` (documented polar behavior) — the `DaylightRegime`
  enum, not exception text, tells the renderer which sectors exist.
- All angles are degrees clockwise from the dial top, directly usable by
  `QPainter.rotate()` in y-down screen coordinates.
- `build_day_context` is deep-time FRAME-AGNOSTIC — it stamps no
  `deep_cycles`; the controller sets that field after the build, since
  the 400-year proxy mapping is exact and every computation inside needs
  no awareness of it.
