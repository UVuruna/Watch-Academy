# Observatory Data

**Script:** [Observatory Data (script)](observatory.py)

## Purpose
Read-only access to the Observatory's committed series bundles under
`Database/` (`observatory_seasons.json`, `observatory_eclipses.json`,
built by [Make Observatory](../setup/make_observatory.py)). These small
JSON files are ALWAYS present (committed, unlike the gitignored
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
- [Observatory Dialog](../app/observatory.md) — the four charts

## Classes

### ObservatoryData
Loads both bundles once in `__init__`.

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

## Design Decisions
The bundles are pure data — no wall clock, no Qt. The two derived
half-year series are computed here (not stored) so the file stays
minimal and the linearity `light = spring+summer` is guaranteed. The
season durations are bin-mean decimated (`SEASON_BIN_YEARS`) — the
millennial Age-of-Light/Darkness trend is preserved well under chart
resolution; the raw per-year record lives in
`research/ephemeris/season_halves.json`.
