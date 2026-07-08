# Sun

**Script:** [Sun (script)](sun.py)

## Purpose
Per-day sun events and daylight-regime classification for any latitude —
including the polar cases the bundled location database contains (cities
up to 81.7°N).

## Connections

### Uses
- astral 3.2 (`astral.sun.dawn/sunrise/noon/sunset/dusk/elevation`)
- [Config (folder)](../config/___config.md) — depression and elevation thresholds

### Used by
- [Clock State](clock_state.md), the background layer (M3),
  [Tests (folder)](../tests/___tests.md)

## Classes

### DaylightRegime
`NORMAL`, `WHITE_NIGHTS` (sun sets, sky never fully dark),
`TWILIGHT_ONLY` (sun never rises, twilight occurs — including the
all-day-twilight edge where no event boundary exists), `POLAR_DAY`,
`POLAR_NIGHT`.

### SunDay
Frozen: `dawn/sunrise/sunset/dusk` (`None` = does not occur that day —
documented behavior, not an error), `noon` (always present), `regime`.

## Functions
- `compute_sun_day(observer, local_date, tz)`: each event in its own
  `try/except ValueError` — never `astral.sun.sun()`, which throws away
  four valid events when one is missing and whose polar-day/night
  messages are identical.
- `day_length_hm(sun)`: daylight duration as "H:MM" (the octa slot
  option) — 24:00 on polar days, 0:00 in polar night/twilight-only,
  complement logic on inverted midnight-sun days, local-midnight bounds
  on one-sided transitional days.
