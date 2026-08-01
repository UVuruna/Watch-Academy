# Deep Time Pack Generator

**Script:** [Deep Time Pack Generator (script)](../make_deep_time.py) ·
**Flow:** [diagram](../__flow/make_deep_time.md)

## Purpose

One-time, rerunnable generator (Session 16, 2026-07-17):

```bash
python setup/make_deep_time.py
```

Builds the gitignored app-side `Database/deep_time.sqlite` (~57 MB) from
the research extraction `research/ephemeris/events.sqlite` (also
gitignored, ~92 MB) — copies every solstice/equinox, every principal
moon phase and both eclipse catalogs over the full usable span
(currently −12997…+16993), converting each source ISO instant into
ASTRONOMICAL calendar fields (year, month, day, second-of-day) because
`datetime`/`fromisoformat` cannot carry negative years. The pack ships
only with the M7 FULL installation; the app detects it at startup and
runs happily without it (the bundled `seasons_utc.json`/
`moonPhases_utc.json` cover the ordinary span).

## Connections

### Uses
- `research/ephemeris/events.sqlite` (gitignored, ~92 MB) — the sole
  input, produced by the research pipeline; see
  [Research Ephemeris (subfolder)](../../research/ephemeris/___ephemeris.md)

### Used by
- Nobody at runtime — the owner runs it manually before an M7 FULL
  build. Its output, `Database/deep_time.sqlite`, is read by the
  [Deep Time Repository](../../data/__about/deep_time.md)

## Functions

- `_parse(iso_ut) -> (year, month, day, sod)` — regex-parses the
  research pipeline's `"±YYYYY-MM-DDTHH:MM:SSZ"` stamp into astronomical
  calendar fields; raises `ValueError` loudly on any format drift
- `_copy(source, target, select, insert, transform, label, total)` —
  generic batched table copy: runs `select` against the source,
  transforms each row, inserts in batches of 10,000, and prints Rule #10
  progress every 100,000 rows
- `main()` — recreates `Database/deep_time.sqlite` from scratch
  (`PRAGMA journal_mode/synchronous = OFF` for build speed), copies
  `sun_events`, `moon_events`, `solar_eclipses`, `lunar_eclipses` via
  `_copy`, computes the `meta.coverage_first`/`coverage_last` bounds
  from the copied data (see [flow](../__flow/make_deep_time.md) for the
  edge-case reasoning), builds the four year-indexes, writes the `meta`
  table (schema, coverage, source, build date, per-table row counts),
  commits, `VACUUM`s, and prints a size/coverage summary
