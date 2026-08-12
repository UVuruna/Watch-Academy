# Extract (Phase I — the Anno Lucis Pipeline)

**Script:** [Extract (script)](../extract.py) ·
**Flow:** [diagram](../__flow/extract.md)

## Purpose

Phase I of the Anno Lucis pipeline. Subcommands `sun` / `moon` / `halves` /
`anno` / `plot` / `all`:

- `sun` / `moon` — march every solstice/equinox and every Moon-phase
  crossing (via [Ephemeris Common](ephemeris_common.md)'s `Marcher`) into
  `events.sqlite` (`sun_events`, `moon_events`). **Resumable** — each scan
  records its last-reached JD in a `meta` table and skips forward on
  restart; progress is logged every 1000 events (elapsed, count/total, rate
  — Rule #10).
- `halves` — pairs vernal→autumn→vernal equinox triples into per-year
  northern LIGHT/DARK half-year durations (TT days) → `season_halves.json`.
- `anno` — rolling-mean smoothing (71-year window) of `light − dark`, plus
  the raw sustained-run criterion, to find the Anno Lucis year →
  `anno_lucis.json`.
- `plot` — the deviation curve → `anno_lucis.png`.

## Usage

```bash
# from the pipeline's own venv (research/ephemeris/.venv)
python extract.py sun          # ~120k events, minutes
python extract.py moon         # ~1.5M events, longer; resumable
python extract.py halves       # season_halves.json from sun_events
python extract.py anno         # anno_lucis.json from season_halves
python extract.py plot         # deviation curve PNG
python extract.py all          # sun -> moon -> halves -> anno -> plot
```

## Connections

### Uses
- [Ephemeris Common](ephemeris_common.md) — `Marcher`, `sun_lon`,
  `elongation`, `jd_ut_of`, `iso_ut`, the scan-window constants
- `pyswisseph`, the `ephe/` data files (via
  [Download Ephemeris Data](download_ephe.md))

### Used by
- [Ephemeris (subfolder)](../___ephemeris.md) — "How to rerun"
- `season_halves.json` feeds [Long Envelope](long_envelope.md)'s validation
- `events.sqlite` feeds the ephemeris folder's own `test_ephemeris.py`
  golden checks

## Functions

- `open_db`, `meta_get`, `meta_set` — the shared `events.sqlite` schema and
  resume-point bookkeeping
- `scan(conn, table, fn, rate, total_estimate)` — the resumable Marcher scan
  loop, batched inserts every 1000 events
- `scan_sun`, `scan_moon` — `scan()` bound to the Sun-longitude / elongation
  functions
- `build_halves` — vernal→autumn→vernal triple pairing into
  `season_halves.json`
- `_rolling_mean`, `build_anno` — the smoothing + up-crossing search that
  produces `anno_lucis.json`
- `build_plot` — the light/dark deviation chart
