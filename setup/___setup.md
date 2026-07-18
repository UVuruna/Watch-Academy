# setup/

Build tooling and one-time asset generators (the full M7 pipeline —
build.py, installer.nsi, svg_to_ico.py, certificates — lands here).

## Files

### `make_silver_letters.py` — Silver Letter Generator
One-time (rerunnable) generator: rasterizes each ACTIVE gold ring
letter at high resolution, desaturates it offline (grayscale with the
alpha kept) and saves `<Stem>_silver.png` beside the gold master in
`assets/ring/letters/`. Run it again whenever a new letter becomes
active in a ring preset (owner decision: silver is pre-rendered art,
not a runtime effect).

### `make_moon_phases.py` — Moon Phase Plate Generator
One-time (rerunnable) generator (owner 2026-07-16): renders the
EIGHT moon-phase plates for the Encyclopedia's Moon pages from the
full-moon master, using the dial's own terminator geometry
(half-disc ∪/∖ terminator half-ellipse, the year-marker shadow
color and alpha) — output `assets/moon/<source>/<phase>.png`. Rerun
when the moon master or the shadow tunables change.

### `make_bronze_letters.py` — Bronze Letter Generator
Derives `<Stem>_bronze.png` from each pre-rendered silver letter: a
straight multiply with `BRONZE_LETTER_TINT` (brightness/contrast knobs
exist but sit at 1.0 — the owner's verdict on the live dial: darkened
candidates sat darker than the bronze medallions). Run AFTER
`make_silver_letters.py` whenever a letter master changes.

### `make_deep_time.py` — Deep Time Pack Generator
One-time (rerunnable) generator (Session 16, owner 2026-07-17):
builds the compact app-side `Database/deep_time.sqlite` from the
research extraction `research/ephemeris/events.sqlite` (gitignored,
~92 MB — rerun the research pipeline first if absent):

    python setup/make_deep_time.py

Copies all sun events, moon phases and both eclipse catalogs over the
full usable span, storing ASTRONOMICAL calendar fields per instant
(ISO strings cannot carry negative years) plus `jd_ut` on the eclipse
tables as the ordering key; writes the pack coverage into `meta` from
the actual event content — a year Y needs the December solstice of
Y−1, the March equinox of Y+1 AND the January–February moon events of
its neighbors (the Chinese New Year cusp; verified trap 2026-07-17:
the scan starts mid-year, so the naive extents-trimmed-by-one bound
let the edge year crash the day build). Progress every 100k rows
(Rule #10). Current build: coverage −12997…+16993, ~1.75M rows,
**56.6 MB**. The pack is GITIGNORED (the entry names this
script as the way back) and ships only with the M7 FULL installation —
the app detects it at startup and runs happily without it.

### `make_observatory.py` — Observatory Series Generator
One-time (rerunnable) generator (Session 17, owner 2026-07-16): builds
the compact, COMMITTED chart bundles the [Observatory](../app/observatory.md)
reads — `Database/observatory_seasons.json` (the four northern season
durations, bin-mean decimated from `events.sqlite` sun_events, plus an
`eras` block from `anno_lucis.json`) and `Database/observatory_eclipses.json`
(solar/lunar counts per bucket + the per-type summary):

    python setup/make_observatory.py

Unlike the multi-megabyte sqlite packs these bundles are small
(~55 KB + ~2 KB) and committed — the Observatory never requires
deep_time.sqlite. Validates the derived light/dark halves against
`season_halves.json` (Rule #1). Rerun the research pipeline first if
`events.sqlite` is absent (gitignored, ~92 MB).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — letter file table and art dir
- [Research Ephemeris (subfolder)](../research/ephemeris/___ephemeris.md)
  — the events database `make_deep_time.py` / `make_observatory.py` read

### Used by
- Nobody at runtime — the app loads the generated PNGs like any asset;
  the Deep Time pack is read by the
  [Deep Time Repository](../data/deep_time.md).
