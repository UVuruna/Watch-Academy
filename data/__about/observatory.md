# Observatory Data

**Script:** [Observatory Data (script)](../observatory.py) ·
**Flow:** [diagram](../__flow/observatory.md)

## Purpose

Read-only access to the Observatory's three COMMITTED chart bundles
under `Database/` — `observatory_seasons.json`, `observatory_eclipses
.json`, `observatory_envelope.json` (built by `setup/make_observatory
.py`). These small JSON files always ship (unlike the gitignored
`deep_time.sqlite`), so the Observatory charts never require the Deep
Time pack.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) —
  `defaults.OBSERVATORY_BUNDLE_SEASONS` /
  `OBSERVATORY_BUNDLE_ECLIPSES` / `OBSERVATORY_BUNDLE_ENVELOPE` /
  `OBSERVATORY_EXTREMA_WINDOW_YEARS`, `paths.database_dir()`

### Used by
- [Observatory Dialog](../../app/__about/observatory.md) — the five charts
- [Instrument Diagrams](../../render/__about/instrument_diagrams.md)

## Classes

### ObservatoryData
Loads all three bundles once in `__init__`.

- `season_series()`: `{years, spring, summer, autumn, winter, light,
  dark}` — the four bin-mean season durations (TT days) plus the two
  derived half-years (`light = spring+summer`, `dark = autumn+winter`),
  parallel arrays over `years`.
- `season_eras()`: the era markers block from the bundle's `meta.eras`.
- `season_span()`: `(first, last)` bin-center years from
  `meta.span_years`.
- `light_dark_extrema()`: every local peak/trough of light-minus-dark
  over the whole bundled span — see [flow](../__flow/observatory.md).
- `eclipse_density()`: `{years, solar, lunar}` — eclipse counts per
  time bucket, always available.
- `eclipse_meta()`: per-century rates, per-type counts, totals, the ΔT
  caveat.
- `laskar_envelope()`: `{years, signed_days, envelope_days}` — the
  La2004 amplitude envelope and signed oscillation.
- `laskar_envelope_meta()`: the DE441 overlap window, sealed extrema
  and the doctrine caption text.

## Design Decisions

The two derived half-year series (`light`, `dark`) are computed here,
not stored, so the bundle stays minimal and `light = spring + summer`
is guaranteed by construction rather than by two separately-authored
numbers agreeing.
