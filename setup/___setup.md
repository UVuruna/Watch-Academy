# setup/

Build tooling and one-time asset generators (the full M7 pipeline —
build.py, installer.nsi, svg_to_ico.py, certificates — lands here).

## Files

**LIVE-RENDER CLEANUP (owner decree 2026-07-19: "bolje crtati na licu
mesta nego 15MB fajlova")** — three one-time generators are RETIRED
whole (Rule #6, no leftovers), their output now computed at load/on
demand instead of shipped as pre-rendered files:
- `make_silver_letters.py` / `make_bronze_letters.py` (ring letters):
  the ~15 MB of `<Stem>_silver.png`/`<Stem>_bronze.png` in
  `assets/ring/letters/` are deleted; `render.asset_recolor.letter_metal_file`
  derives both from the gold master at load (silver = grayscale
  desaturation, bronze = a straight multiply with `BRONZE_LETTER_TINT`
  off the silver result), disk-cached like every other derived asset.
- `make_moon_phases.py` (Encyclopedia Moon pages): the ~7 MB of
  `assets/moon/<source>/<phase>.png` plates are deleted;
  `render.asset_variants.moon_phase_image` (the shared terminator geometry
  extracted out of `render.layers._draw_moon` as `moon_lit_region`,
  fixing an exact-quarter degeneracy the plates shipped with) plus
  `moon_phase_file` (disk-cached path wrapper) render each phase live.

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
One-time (rerunnable) generator (Session 17, owner 2026-07-16; extended
Fix round D, Task 4, 2026-07-19) builds the compact, COMMITTED chart
bundles the [Observatory](../app/observatory.md) reads —
`Database/observatory_seasons.json` (the four northern season
durations, bin-mean decimated from `events.sqlite` sun_events, plus an
`eras` block from `anno_lucis.json`), `Database/observatory_eclipses.json`
(solar/lunar counts per bucket + the per-type summary), and
`Database/observatory_envelope.json` (the La2004 Laskar amplitude
envelope, sliced from `research/ephemeris/long_envelope.json` to the
owner's ±200,000-year chart window — already 1-kyr step, so the slice
alone is ~401 rows, no further decimation needed):

    python setup/make_observatory.py

Unlike the multi-megabyte sqlite packs these bundles are small
(~55 KB + ~2 KB + ~9 KB) and committed — the Observatory never requires
deep_time.sqlite. Validates the derived light/dark halves against
`season_halves.json` (Rule #1). Rerun the research pipeline first if
`events.sqlite` is absent (gitignored, ~92 MB); the envelope slice needs
`research/ephemeris/long_envelope.json` (committed — regenerate via the
research venv's `long_envelope.py` per
[Research Ephemeris (subfolder)](../research/ephemeris/___ephemeris.md)
only if it is ever missing).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — letter file table and art dir
- [Research Ephemeris (subfolder)](../research/ephemeris/___ephemeris.md)
  — the events database `make_deep_time.py` / `make_observatory.py` read

### Used by
- Nobody at runtime — the app loads the generated PNGs like any asset;
  the Deep Time pack is read by the
  [Deep Time Repository](../data/deep_time.md).
