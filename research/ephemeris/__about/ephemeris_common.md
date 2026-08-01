# Ephemeris Common

**Script:** [Ephemeris Common (script)](../ephemeris_common.py) ·
**Flow:** [diagram](../__flow/ephemeris_common.md)

## Purpose

Shared setup and root-finding for the ephemeris pipeline. Pure computation
over the Swiss Ephemeris DE441-derived data files — no app code, no Qt. Sets
the ephemeris path (`init()`), exposes `sun_lon(jd)` and `elongation(jd)`
(both strictly increasing with time), TT↔UT conversion (`jd_ut_of`, via
`swe.deltat`) and proleptic-Gregorian ISO stamping (`iso_ut`). Holds the
effective scan window (`SCAN_JD_FLOOR`/`SCAN_JD_CEIL`, a hair inside the
data's real coverage). The one algorithmic core is `Marcher`: it walks a
monotonic angle function forward and returns the Julian Day of each 90°-grid
crossing, by undershoot-bracket + secant-with-bisection-fallback refinement
to `1e-6` degrees.

## Usage

Imported by [Extract](extract.md) and [Extract Eclipses](extract_eclipses.md)
— not run directly.

## Connections

### Uses
- `pyswisseph` (`swisseph`) — the `ephe/` data files, pointed at via
  `init()`

### Used by
- [Extract](extract.md) — both `sun_lon` and `elongation`, walked by
  `Marcher`
- [Extract Eclipses](extract_eclipses.md) — `iso_ut` only (its own scan uses
  the Swiss Ephemeris' direct eclipse finders, not `Marcher`)

## Classes

### Marcher
Walks a strictly-increasing angle function forward, yielding the JD of every
crossing of a 90°-grid.
- `__init__(fn, jd0, rate, grid=90.0)` — anchors the unwrapped angle at
  `jd0`, sets the next grid multiple strictly above the start angle
- `_u(jd)` — the unwrapped (never-wraps-mod-360) angle at `jd`, re-anchored
  to the last accepted evaluation (valid because every search step stays
  under 180°)
- `next_crossing(jd)` — brackets the next target by an undershoot estimate
  from the angular rate, then refines by secant (bisection fallback) to the
  tolerance; returns `(jd_cross, target_deg_mod_360)` and advances the
  internal target by one grid step
