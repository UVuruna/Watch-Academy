# Observatory Series Generator

**Script:** [Observatory Series Generator (script)](../make_observatory.py) ·
**Flow:** [diagram](../__flow/make_observatory.md)

## Purpose

One-time, rerunnable generator (Session 17, 2026-07-16; extended Fix
round D Task 4, 2026-07-19):

```bash
python setup/make_observatory.py
```

Builds the three small, COMMITTED chart bundles the Observatory dialog
reads — unlike `make_deep_time.py`'s multi-megabyte gitignored pack,
these are decimated down to chart resolution and shipped in every
build, so the Observatory never requires `deep_time.sqlite`:

- `Database/observatory_seasons.json` (~55 KB) — the four northern
  astronomical season durations, bin-mean decimated (20-year bins) from
  `sun_events`, plus an `eras` block (Anno Lucis + the sealed
  starry-season transitions)
- `Database/observatory_eclipses.json` (~2 KB) — solar/lunar eclipse
  COUNTS per 500-year bucket (density timeline) plus the per-type
  summary
- `Database/observatory_envelope.json` (~9 KB) — the La2004 Laskar long
  envelope of the light-minus-dark half-year amplitude, sliced to the
  owner's ±200,000-year chart window

## Connections

### Uses
- `research/ephemeris/events.sqlite` (gitignored, ~92 MB) — source for
  the seasons and eclipses bundles; see
  [Research Ephemeris (subfolder)](../../research/ephemeris/___ephemeris.md)
- `research/ephemeris/season_halves.json` — validates the derived
  light/dark half-year sums (loud `ValueError` on drift, Rule #1)
- `research/ephemeris/anno_lucis.json` — the era markers folded into
  the seasons bundle's `eras` block
- `research/ephemeris/eclipses_summary.json` — the per-type eclipse
  summary folded into the eclipses bundle
- `research/ephemeris/long_envelope.json` — the committed La2004
  envelope; the envelope bundle is a straight window-slice of it, no
  further decimation needed

### Used by
- Nobody at runtime — the owner reruns it whenever the research
  extraction changes. Its three outputs are read by
  [Observatory Data](../../data/__about/observatory.md)

## Functions

- `_year(iso_ut) -> int` — regex-extracts the astronomical year from a
  research ISO stamp; raises `ValueError` loudly on format drift
- `_season_durations(source) -> {year: {season: TT days}}` — walks
  `sun_events` ordered by `jd_tt`, computing each season's duration as
  the gap between consecutive crossings, keyed by the year the season
  STARTS in; keeps only years where all four seasons are present
  (Rule #10 progress every 200,000 rows)
- `_bin_mean(durations)` — bin-mean decimates the per-year durations
  into `SEASON_BIN_YEARS` (20)-year windows, skipping sparse edge bins
  (fewer than half a bin's years measured)
- `_eras()` — assembles the `eras` block from `anno_lucis.json` plus
  the owner-sealed starry-season transition years (hardcoded — these
  are sealed doctrine, not derived data)
- `_write_seasons(source)` — orchestrates `_season_durations` +
  `_bin_mean`, validates the light/dark halves against
  `season_halves.json` at three spot-check years, and writes
  `observatory_seasons.json`
- `_write_eclipses(source)` — buckets `solar_eclipses`/`lunar_eclipses`
  rows by `year // ECLIPSE_BUCKET_YEARS` (500), counts per type per
  bucket, and writes `observatory_eclipses.json`
- `_write_envelope()` — reads `long_envelope.json`, slices `t_kyr` to
  `±ENVELOPE_WINDOW_KYR` (200), converts kyr offsets to calendar years,
  and writes `observatory_envelope.json`
- `main()` — checks both source files exist, opens `events.sqlite`
  read-only, runs the three writers in order, prints "done"
