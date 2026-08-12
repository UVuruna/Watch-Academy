# Ascendant

**Script:** [Ascendant (script)](../ascendant.py) · **Flow:** [diagram](../__flow/ascendant.md)

## Purpose
The ASCENDANT — the zodiac sign rising on the eastern horizon at a given
instant and place (owner request 2026-07-12: the natal "podznak",
cycling through all twelve signs roughly every two hours, latitude-
dependent). Pure math, stdlib only: Julian date -> Greenwich mean
sidereal time -> local sidereal time (RAMC) -> ascendant ecliptic
longitude via the standard spherical formula.

Validated against the owner's own birth chart (20 June 1990, 12:15 CEST,
Belgrade -> 174.3 deg = Virgo).

## Connections

### Uses
- Nothing beyond `math` and `datetime` — importable anywhere, no
  project dependency at all.

### Used by
- [Clock State](clock_state.md) — `TickState.ascendant_sign`, recomputed
  every minute tick (the South slot's Ascendant mode reads it)

## Functions
- `julian_date(moment_utc)`: astronomical Julian date of a UTC instant
  (Meeus).
- `ascendant_longitude(moment, latitude, longitude)`: ecliptic longitude
  of the ascendant in degrees [0, 360). `moment` may carry any timezone
  — reduced to UTC internally; east longitude positive.
- `ascendant_sign(moment, latitude, longitude)`: the sign name ("Virgo")
  — `ascendant_longitude(...) // 30` into the twelve tropical signs.

## Design Decisions
- Self-contained on purpose: no `config` import, no `core.angles` — the
  sidereal-time formula uses its own obliquity/GMST constants inline
  since they belong to this one calculation, not to the dial's clockwise
  convention.
