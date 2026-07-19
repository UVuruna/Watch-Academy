# Observatory Data

**Script:** [Observatory Data (script)](observatory.py)

## Purpose
Read-only access to the Observatory's committed series bundles under
`Database/` (`observatory_seasons.json`, `observatory_eclipses.json`,
`observatory_envelope.json`, built by
[Make Observatory](../setup/make_observatory.py)). These small JSON
files are ALWAYS present (committed, unlike the gitignored
`deep_time.sqlite`), so the Observatory charts never require the Deep
Time pack — they read only this data. The eclipse timeline may
ADDITIONALLY use the Deep Time pack for exact nearest-eclipse instants
when it is installed; without it, only the bundled density and the
per-type summary are available (the documented split).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — bundle filenames, paths
- [IO Helper](_io.py) — `load_json_checked` (loud on a missing/broken
  bundle — a build-integrity error, Rule #1)

### Used by
- [Observatory Dialog](../app/observatory.md) — the five charts

## Classes

### ObservatoryData
Loads all three bundles once in `__init__`.

#### Methods
- `season_series()`: `{years, spring, summer, autumn, winter, light,
  dark}` — the four bin-mean season durations (TT days) plus the two
  derived half-years (`light = spring+summer`, `dark = autumn+winter`),
  all parallel arrays over `years`.
- `season_eras()`: the era markers (`anno_lucis_year`, `age_of_light`,
  `next_anno_lucis`, `dark_peak_prev`, `starry_transitions`) for the
  light−dark chart.
- `season_span()`: `(first, last)` bin-center years.
- `eclipse_density()`: `{years, solar, lunar}` — eclipse counts per
  time bucket (the always-available density timeline).
- `eclipse_meta()`: per-century rates, per-type counts, totals and the
  ΔT caveat.
- `light_dark_extrema()` (Fix round D, Task 3): every local peak/trough
  of light-minus-dark over the whole bundled span —
  `[(year, value_days, kind)]`, kind "light_peak"/"dark_peak". Windowed
  against `OBSERVATORY_EXTREMA_WINDOW_YEARS` so the bin-mean series'
  own rounding noise never registers as a spurious peak (see the
  design note below).
- `laskar_envelope()` (Fix round D, Task 4): `{years, signed_days,
  envelope_days}` — the La2004 amplitude envelope + signed oscillation
  over the owner's ±200,000-year chart window.
- `laskar_envelope_meta()`: the DE441 overlap window, the sealed
  extrema (coming eccentricity minimum etc.) and the doctrine caption.

## Design Decisions
The bundles are pure data — no wall clock, no Qt. The two derived
half-year series are computed here (not stored) so the file stays
minimal and the linearity `light = spring+summer` is guaranteed. The
season durations are bin-mean decimated (`SEASON_BIN_YEARS`) — the
millennial Age-of-Light/Darkness trend is preserved well under chart
resolution; the raw per-year record lives in
`research/ephemeris/season_halves.json`.

`light_dark_extrema()` cannot use a bare immediate-neighbor comparison:
measured on the committed bundle, that flagged 27 "peaks" within a few
bins of the true turning points, agreeing to 3 decimal places —
decimation rounding noise, not real turning points. A candidate must be
the most extreme point within a window of years on each side
(comfortably smaller than the oscillation's ~10,000-year half-period),
and near-duplicate survivors from a flat plateau are merged to the
single most extreme point — settling to the 3 physically real extrema
over the bundled span (2 dark peaks, 1 light peak).
