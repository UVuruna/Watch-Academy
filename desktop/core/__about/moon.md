# Moon

**Script:** [Moon (script)](../moon.py) · **Flow:** [diagram](../__flow/moon.md)

## Purpose
Moon cycle fraction from bundled principal-phase instants — exact at
the anchors, ~0.0001 cycle accurate in between (`astral.moon.phase()` is
day-granular and deliberately not used) — and the TRUE analytic
illumination: the compact Meeus 48.4 elongation series, replacing an
earlier cycle-fraction cosine that was up to ~3 percentage points off
mid-phase.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `MOON_PHASE_FRACTIONS`,
  `MOON_CYCLE_QUARTER`, `CHINA_UTC_OFFSET_HOURS`, `CHINESE_ANIMALS`,
  `CHINESE_ELEMENTS`, `CHINESE_NEW_YEAR_WINDOW`, `MOON_PRINCIPAL_WINDOW`
- [Deep Time](deep_time.md) — `julian_day`, `delta_t_seconds`,
  `real_year` — the proleptic Julian Day, ΔT and the proxy-frame
  un-shift the analytic series needs
- [Angles](angles.md) — `time_to_dial_angle`, the ONE dial mapping
  `moon_horizon_arcs` reuses rather than re-deriving

### Used by
- [Moon Phases Repository](../../data/__about/moon_phases.md) —
  constructs `MoonWindow`
- [Clock State](clock_state.md) — `phase_fraction`, `illumination`,
  `chinese_zodiac`, `moon_rise_set`
- [Blue Moon](blue_moon.md) — `MoonWindow` as an input type
- [Watch Controller](../../app/__about/controller.md) — `chinese_name_of_year`
  for the deep-travel correction
- [Moon Band](../../render/layers/__about/moon_band.md) — `moon_horizon_arcs`,
  the Moon Horizon Band's whole geometry input

## Classes

### MoonWindow
Frozen: sorted `events` — `(instant_utc, cycle_fraction)` tuples
spanning the period of interest plus margins.

## Functions
- `phase_fraction(now, window)`: 0.0 new .. 0.25 first quarter .. 0.5
  full .. 0.75 third quarter, wrapping mod 1.0; waxing below 0.5, waning
  above; raises `ValueError` when `now` is outside the window span.
- `illumination(when, cycles=0)`: TRUE lit fraction (0.0 new .. 1.0
  full) at a tz-aware instant — Meeus 48.4 (sun mean anomaly, moon mean
  anomaly, mean elongation D, plus six principal periodic correction
  terms), `k = (1 - cos(D_corrected)) / 2`, evaluated at TT via the
  Espenak-Meeus ΔT. `cycles` un-shifts the deep proxy frame so a deep
  travel evaluates at the REAL epoch.
- `nominal_illumination(fraction)`: the plain cosine mapping
  `(1 - cos(2*pi*fraction)) / 2` — used ONLY for the hypothetical ring-
  tick hover ("what would stand here"), never for the live moon.
- `moon_rise_set(observer, day, tzinfo)`: local `(moonrise, moonset)` via
  astral, either `None` when the event does not occur that day
  (documented: the moon skips a rise or set roughly once a synodic
  month, more often at polar latitudes).
- `chinese_zodiac(now_local, window)`: `("Fire Horse", start, end)` — the
  Chinese year begins at the new moon in the Jan 21 - Feb 20 window
  (China Standard Time); the cusp comparison happens entirely in China's
  calendar frame.
- `chinese_name_of_year(year)`: the sexagenary name alone (element +
  animal) — shared by `chinese_zodiac` and the deep-time correction (a
  400-year proxy shift moves the sexagenary cycle by 40).
- `phase_name(fraction)`: English phase name — a principal name (New,
  First Quarter, Full, Third Quarter) applies only within
  `MOON_PRINCIPAL_WINDOW` of its instant, else an octant name
  (Waxing/Waning Crescent/Gibbous).

### MoonArc
Frozen: one above-horizon span on the dial's tick circle —
`start_deg`/`end_deg` (UNWRAPPED, `end_deg >= start_deg`, `% 360` taken
by the render side), `culmination_deg` (the arc's own midpoint —
`core.moon` has no lunar-transit computation, so this is the owner-
approved approximation), `full_circle` (both rise/set missing that
day).

- `moon_horizon_arcs(moonrise, moonset)`: the Moon Horizon Band's
  geometry (owner verdict 2026-08-09) — `tuple[MoonArc, ...]`, built
  from the SAME `(moonrise, moonset)` pair `_is_moon_up` reads. THE
  NONE-DAY RULE mirrors `_is_moon_up`'s own policy: both missing ->
  ONE full-circle arc (treated as visible, same "never lie about
  hiding a visible moon" reasoning); one missing -> the arc runs from/
  to local midnight; both present but rise AFTER set (up at midnight,
  sets, rises again) -> TWO arcs, split at the dial's own seam.

## Design Decisions
- `illumination` supersedes the older cosine mapping for every LIVE
  reading; `nominal_illumination` is kept only for the hypothetical ring
  hover, which needs the ring's own idealized mapping, not the true sky.
- `moon_horizon_arcs` reuses `_is_moon_up`'s None-day policy verbatim
  (Rule #5) rather than writing a second, competing interpretation of a
  missing rise/set.
