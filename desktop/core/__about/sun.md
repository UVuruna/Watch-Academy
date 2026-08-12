# Sun

**Script:** [Sun (script)](../sun.py) · **Flow:** [diagram](../__flow/sun.md)

## Purpose
Per-day sun events and daylight-regime classification for any latitude
— including the polar cases the bundled location database contains
(cities up to 81.7 deg N). The five events are computed INDIVIDUALLY:
`astral.sun.sun()` is all-or-nothing and raises `ValueError` at high
latitudes even when four of the five events exist, and its message is
identical for polar day and polar night — exception text can never
classify the regime. `noon()` never raises, so the star rotation is
always computable, even in polar night.

## Connections

### Uses
- astral 3.2 (`astral.sun.dawn/sunrise/noon/sunset/dusk/elevation`)
- [Config (folder)](../../config/___config.md) — `CIVIL_DEPRESSION`,
  `HORIZON_ELEVATION_DEG`, `CIVIL_TWILIGHT_ELEVATION_DEG`

### Used by
- [Clock State](clock_state.md) — `compute_sun_day`, `day_length_hm`,
  `DaylightRegime`, `SunDay`
- [Observatory](../../app/__about/observatory.md) — `day_length_curve` for the
  local day-length chart
- [Tests (folder)](../../tests/___tests.md) — regime/event goldens

## Classes

### DaylightRegime (Enum)
`NORMAL` (sunrise/sunset and dawn/dusk all exist), `WHITE_NIGHTS`
(sunrise/sunset exist, sky never fully dark), `TWILIGHT_ONLY` (sun never
rises, but twilight occurs — including the all-day-twilight edge with no
event boundary at all), `POLAR_DAY` (sun never sets), `POLAR_NIGHT` (sun
never comes near the horizon).

### SunDay
Frozen: `dawn`/`sunrise`/`sunset`/`dusk` (`None` = does not occur that
day at that latitude — documented behavior, not an error), `noon`
(always present), `regime`.

## Functions
- `compute_sun_day(observer, local_date, tz)`: each event in its own
  `try/except ValueError`; corrects `noon()`'s lack of local-date
  re-search in UTC+13/+14 zones (e.g. Kiritimati), where the transit of
  the requested UTC day can land on the next local day.
- `_classify(observer, noon, dawn, sunrise, sunset, dusk)`: the regime
  decision tree — see [Flow](../__flow/sun.md).
- `day_length_minutes(sun)`: daylight duration in whole minutes (1440 on
  polar days, 0 in polar night/twilight-only; complement logic on
  inverted midnight-sun days; local-midnight bounds on one-sided
  transitional days).
- `day_length_hm(sun)`: `day_length_minutes` formatted `"H:MM"` (the
  octa bottom-arm slot option).
- `day_length_curve(observer, tz, year, step_days=1)`: the daylight-
  minutes curve over one calendar year, one sample every `step_days` —
  pure (the year is explicit; no wall clock read).

## Design Decisions
- Regime classification reads GEOMETRIC elevation
  (`with_refraction=False`) against `HORIZON_ELEVATION_DEG`, which
  already contains astral's own refraction allowance — apparent
  elevation would double-count it and misreport POLAR_DAY on all-day-
  twilight days above roughly 87 deg.
