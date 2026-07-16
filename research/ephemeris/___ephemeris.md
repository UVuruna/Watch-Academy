# research/ephemeris/

The **Anno Lucis** pipeline (ROADMAP queue item 12, owner 2026-07-16). A
reproducible, research-only extraction over the full Swiss Ephemeris
DE441-derived span: every solstice/equinox and every Moon phase across
~30 000 years, from which the northern LIGHT / DARK half-year durations and
the **Anno Lucis year** — the year the light half durably outgrows the dark
— are derived.

This folder is NOT part of the app runtime. Nothing here is imported by the
watch; it produces committable evidence files (`season_halves.json`,
`anno_lucis.json`, `anno_lucis.png`) and a large gitignored event database.

## The Anno Lucis result (owner definition SEALED 2026-07-16)

- **ANNO LUCIS = 4079 BCE** (astronomical year −4078): the first year
  of the UNBROKEN light era. No averaging — the raw measured series
  (the owner ruled out smoothed indicators).
- **The dawn flickered for 11 years:** −4088 ONE light year (the first
  flicker ever), then dark returned for 7 years, one light year
  (−4080), one last dark year (−4079) — and from **−4078 the light
  half won EVERY year, 10,501 years in a row**.
- **The light era runs 4079 BCE → 6423 CE.** Around +6423–6432 the
  reverse flicker happens and the DARK era begins (~10,000 years);
  the NEXT Anno Lucis is +16429 — one apsidal cycle later.
- **Today (2026): the light half is ~7.5 days longer** than the dark —
  near the era's peak. The A.L. calendar: **A.L. = CE + 4079** →
  2026 CE = **A.L. 6105**.
- The superseded 71-yr smoothed crossing (≈4083 BCE) stays recorded in
  `anno_lucis.json` for the method history only.

## Files

### `ephemeris_common.py` — Setup & the crossing marcher
Sets the ephemeris path, exposes `sun_lon(jd)` and `elongation(jd)` (both
strictly increasing in time), TT↔UT conversion (`jd_ut_of`, via `swe.deltat`)
and proleptic-Gregorian ISO stamping. The `Marcher` walks a monotonic angle
function forward and returns the JD of each 90°-grid crossing by
undershoot-bracket + secant refinement to 1e-6°. Holds the effective scan
window: `SCAN_JD_FLOOR`/`SCAN_JD_CEIL` clamp the walk a hair inside the data.

### `download_ephe.py` — Fetch the .se1 data
Astrodienst's old ftp path now redirects to the maintained GitHub mirror
(`aloistr/swisseph`). This enumerates that `ephe/` folder, keeps the Sun
(`sepl*`) and Moon (`semo*`) files the span needs (~98 MB, 100 files),
downloads each with exponential-backoff retries into `ephe/`, skips files
already present at the right size, then VERIFIES coverage by probing
`swe.calc` at both temporal extremes.

### `extract.py` — The pipeline
Subcommands `sun` / `moon` / `halves` / `anno` / `plot` / `all`.
- `sun` / `moon`: march the crossings into `events.sqlite`
  (`sun_events`, `moon_events` — `jd_tt, jd_ut, iso_ut, type`; `type` is the
  crossing degree 0/90/180/270). **Resumable** — each scan records its
  last-reached JD in a `meta` table and skips forward on restart; progress
  is logged every 1000 events (elapsed, count/total, rate — house Rule #10).
- `halves`: pairs vernal→autumn→vernal equinoxes into per-year northern
  LIGHT/DARK durations (TT days) → `season_halves.json`.
- `anno`: rolling-mean smoothing of `light − dark` + the raw sustained-run
  criterion → `anno_lucis.json`.
- `plot`: the deviation curve → `anno_lucis.png`.

### `extract_eclipses.py` — Phase II: the eclipse catalog
Extends the pipeline with every SOLAR and LUNAR eclipse across the full
span, via the Swiss Ephemeris' direct global finders (not the crossing
marcher). Subcommands `solar` / `lunar` / `summary` / `all`.
- `solar`: walks `swe.sol_eclipse_when_glob` forward (each result's
  `tret[0]` = the maximum instant); at that instant `swe.sol_eclipse_where`
  gives the TYPE, the MAGNITUDE (NASA, `attr[8]`) and the GEOGRAPHIC POINT
  of greatest eclipse (`geopos[0]/[1]` — the central line, or the
  greatest-partial point for partials). Into `solar_eclipses`
  (`jd_tt, jd_ut, iso_ut, type, magnitude, lat, lon`). Types decoded from
  the return flag: **hybrid** (annular-total, bit 32 — tested first),
  **total**, **annular**, **partial**. If `where` reports no surface point
  (`rf==0`) the place/magnitude are stored NULL, the type/time kept.
- `lunar`: walks `swe.lun_eclipse_when`; `swe.lun_eclipse_how` gives the
  MAGNITUDE — umbral (`attr[0]`) for total/partial, penumbral (`attr[1]`)
  for penumbral. Into `lunar_eclipses`
  (`jd_tt, jd_ut, iso_ut, type, magnitude`).
- Both finders work in UT; we store `jd_ut` as returned and
  `jd_tt = jd_ut + deltat`. RESUMABLE (shared `meta` table, per-table
  `last_jd`/`done`), progress every 500 events (Rule #10).
- `summary`: writes `eclipses_summary.json`.

### `eclipses_summary.json` (committable)
Counts per type per catalog, events-per-century, first/last events, span,
and the sharper eclipse ΔT caveat. Current run: **70,644 solar** (total
19,250 · annular 23,549 · hybrid 3,228 · partial 24,617) + **70,778 lunar**
(total 21,056 · partial 25,035 · penumbral 24,687) = **141,422** eclipses,
~236 of each per century, spanning −12998 … +16993.

**Eclipse ΔT caveat (SHARPER than the season one):** THAT an eclipse
happens, and its DATE and TYPE, are robust across the whole span. But the
SHADOW-PATH LONGITUDE (the solar greatest-eclipse `lon`) is only trustworthy
within a few millennia of the present — hours of ΔT at the extremes slide
the sub-solar longitude by tens of degrees. Latitudes and magnitudes stay
reliable.

### `test_ephemeris.py` — Golden checks
Runs under the venv python; **skips** cleanly when `events.sqlite` (or a
table / an unfinished scan) is absent, so CI stays green without the
gitignored database. Checks: 2026 June solstice within 60 s of bundled
`Database/seasons_utc.json`; 2026-07-07 last quarter within 5 min of bundled
`Database/moonPhases_utc.json` (once the Moon scan is complete); CE 1000 June
solstice on the expected proleptic-Gregorian day; ~4 sun events/year cadence.
Phase II: the 1999-08-11 and 2024-04-08 TOTAL solars (max time within 5 min,
greatest-eclipse point within ~1°) and the 2019-01-21 TOTAL lunar
(umbral magnitude ~1.2) — all skip cleanly when the eclipse tables are absent.

### `season_halves.json` (~0.94 MB, committable)
`{year: [light_days, dark_days]}` for ~29 992 years. The compact evidence
the Anno Lucis rests on.

### `anno_lucis.json` (committable)
The result + full method note (definition, smoothing window, raw criterion,
all smoothed crossings, span, ΔT caveat).

### `anno_lucis.png` (committable)
Light (gold) / dark (purple) half-year duration deviation across the whole
span, Anno Lucis marked — the analogue of the owner's `Anno Lucis.png`.

### Gitignored (regenerate locally)
`ephe/` (data files), `.venv/` (uv-managed Python 3.11), `events.sqlite`
(the full event database — hundreds of MB).

## How to rerun

```
# 1. environment: pyswisseph has no Windows wheel for 3.12/3.13, so we use
#    a uv-managed Python 3.11 venv (cp311 wheel exists).
python -m pip install uv
python -m uv venv --python 3.11 .venv
python -m uv pip install --python .venv/Scripts/python.exe pyswisseph numpy matplotlib pytest

# 2. data (~98 MB) + full extraction
.venv/Scripts/python.exe download_ephe.py
.venv/Scripts/python.exe extract.py all       # sun (~15s) -> moon (~min) -> halves -> anno -> plot
.venv/Scripts/python.exe extract_eclipses.py all  # solar (~1min) -> lunar (~1min) -> eclipses_summary.json

# 3. verify
.venv/Scripts/python.exe -m pytest test_ephemeris.py -v
```

## The ΔT caveat (read this)

Over ±15 millennia the model for ΔT (the Earth-rotation clock error between
TT and UT) carries **hours** of uncertainty. Consequently: event **years**
and season **durations** are robust (they depend on the Sun/Moon geometry,
which DE441 nails), but exact **local clock times** at the extremes are not.
The Anno Lucis year is a duration-difference result and is therefore solid;
do not read the ancient ISO timestamps as wall-clock truth.

Coverage note: this compressed .se1 set actually spans −12999-05 … +17182-10
(probed), a touch narrower than DE441's nominal −13200…+17191; the scan runs
the usable interval −12998 … +16993.

## Connections

### Uses
- [Database (folder)](../../Database/___database.md) — `seasons_utc.json`
  and `moonPhases_utc.json` supply the golden reference values.

### Used by
- Nothing in the runtime. Feeds the owner's Anno Lucis / dual-calendar
  direction (ROADMAP items 12–13); app integration is a LATER task.
