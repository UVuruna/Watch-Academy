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

### Used by
- [Moon Phases Repository](../../data/__about/moon_phases.md) —
  constructs `MoonWindow`
- [Clock State](clock_state.md) — `phase_fraction`, `illumination`,
  `chinese_zodiac`, `moon_rise_set`
- [Blue Moon](blue_moon.md) — `MoonWindow` as an input type
- [Watch Controller](../../app/__about/controller.md) — `chinese_name_of_year`
  for the deep-travel correction

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

## Design Decisions
- `illumination` supersedes the older cosine mapping for every LIVE
  reading; `nominal_illumination` is kept only for the hypothetical ring
  hover, which needs the ring's own idealized mapping, not the true sky.
