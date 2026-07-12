# Ascendant

**Script:** [Ascendant (script)](ascendant.py)

## Purpose
The ASCENDANT (rising sign, owner request 2026-07-12): the zodiac sign
crossing the eastern horizon at a given instant and place — the
"podznak" of natal astrology, cycling through all twelve signs every
day (~two hours per sign, latitude-dependent). Pure math, no I/O:
Julian date → Greenwich mean sidereal time → local sidereal time
(RAMC) → the ascendant ecliptic longitude from the standard spherical
formula with the mean obliquity and the geographic latitude.

Validated against the owner's own birth (20 June 1990, 12:15 CEST,
Belgrade → 174.3° = Virgo, his documented rising sign) — the golden
test pins it.

## Connections

### Uses
- Nothing beyond the stdlib (`math`, `datetime`) — importable anywhere.

### Used by
- [Clock State](clock_state.md) — `TickState.ascendant_sign` on every
  minute tick (the South slot's Ascendant mode reads it)

## Functions

- `julian_date(moment_utc)`: astronomical Julian date of a UTC instant
- `ascendant_longitude(moment_utc, latitude, longitude)`: ecliptic
  longitude of the ascendant in degrees [0, 360)
- `ascendant_sign(moment_utc, latitude, longitude)`: the sign name
  ("Virgo") — longitude // 30 into the tropical wheel
