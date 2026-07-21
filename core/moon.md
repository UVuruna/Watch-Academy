# Moon

**Script:** [Moon (script)](moon.py)

## Purpose
Moon cycle fraction from bundled principal-phase instants — exact at
the anchors, ~0.0001 cycle accurate in between (`astral.moon.phase()`
is day-granular and deliberately not used) — and, since Session 16
(owner slike 4–7, 2026-07-17), the TRUE analytic illumination: the
compact Meeus 48.4 elongation series replaces the cycle-fraction
cosine, which was up to ~3 p.p. off mid-phase (ours 10.3% vs the true
~11.5% on the owner's screenshots).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `MOON_PHASE_FRACTIONS`,
  `MOON_CYCLE_QUARTER`
- [Deep Time](deep_time.md) — the proleptic Julian Day, ΔT and the
  proxy-frame un-shift the analytic series needs

### Used by
- [Moon Phases Repository](../data/moon_phases.md) — constructs `MoonWindow`
- [Clock State](clock_state.md), the year-marker layer in moon mode (M3)
- [Watch Controller](../app/controller.md) — `chinese_name_of_year` for
  the deep-travel correction

## Classes

### MoonWindow
Frozen: sorted `(instant_utc, cycle_fraction)` events spanning the
period of interest plus margins.

## Functions
- `phase_fraction(now, window)`: 0.0 new … 0.5 full … wraps at 1.0;
  waxing below 0.5, waning above; raises outside the window span —
  UNCHANGED by Session 16: the cycle-day reading ("Day 3.1 of 29.53")
  is a cycle position, not illumination
- `illumination(when, cycles=0)`: TRUE lit fraction at a tz-aware
  instant — Meeus 48.4 (sun mean anomaly, moon mean anomaly, mean
  elongation + the six principal periodic terms),
  `k = (1 − cos(D + corrections))/2`, TT via the Espenak–Meeus ΔT.
  `cycles` un-shifts the deep proxy frame so a deep travel evaluates
  at the REAL epoch. Measured against the DE441 events database
  (2026-07-17): max 0.35 p.p. at modern principal instants, max
  2.4 p.p. at the ±13000-year edges — better than the old
  interpolation everywhere, so it serves the whole span
- `nominal_illumination(fraction)`: the old cosine `(1−cos 2πf)/2` —
  kept ONLY for the hypothetical ring-tick hover ("what would stand at
  this angle"); never the live moon
- `phase_name(fraction)`: principal name within ±half a day of its
  instant, octant names otherwise
- `chinese_zodiac(now, window)`: ("Fire Horse", start, end) — the
  Chinese year begins at the new moon in the Jan 21 – Feb 20 window
  (China time); raises loudly when the window lacks the cusp new moons
- `chinese_name_of_year(year)`: the sexagenary name alone — shared by
  chinese_zodiac and the controller's deep correction (a 400-year
  proxy shift moves the sexagenary cycle by 40)
