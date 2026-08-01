# Extract Eclipses (Phase II — the Eclipse Catalog)

**Script:** [Extract Eclipses (script)](../extract_eclipses.py) ·
**Flow:** [diagram](../__flow/extract_eclipses.md)

## Purpose

Phase II — extends the Anno Lucis pipeline with every SOLAR and LUNAR
eclipse across the same full span, using the Swiss Ephemeris' direct global
finders (not the crossing marcher):

- `solar` — walks `swe.sol_eclipse_when_glob` forward (each result's
  `tret[0]` is the maximum instant); at that instant `swe.sol_eclipse_where`
  gives the TYPE, the MAGNITUDE (NASA, `attr[8]`) and the GEOGRAPHIC POINT of
  greatest eclipse. Into `solar_eclipses`
  (`jd_tt, jd_ut, iso_ut, type, magnitude, lat, lon`). Types decoded from the
  return flag: **hybrid** (bit 32, tested first), **total**, **annular**,
  **partial**. When `where` reports no surface point, place/magnitude are
  stored NULL and the type/time are kept.
- `lunar` — walks `swe.lun_eclipse_when`; `swe.lun_eclipse_how` gives the
  MAGNITUDE — umbral for total/partial, penumbral for penumbral. Into
  `lunar_eclipses` (`jd_tt, jd_ut, iso_ut, type, magnitude`).
- `summary` — writes `eclipses_summary.json` (counts per type, per-century
  rate, first/last events, the sharper eclipse ΔT caveat).

Both finders work in Universal Time; the script stores `jd_ut` as returned
and `jd_tt = jd_ut + deltat`. RESUMABLE (shared `meta` table, per-table
`last_jd`/`done`), progress every 500 events (Rule #10).

## Usage

```bash
# from the pipeline's own venv
python extract_eclipses.py solar     # ~70-75k events, resumable
python extract_eclipses.py lunar     # ~85-90k events, resumable
python extract_eclipses.py summary   # eclipses_summary.json
python extract_eclipses.py all       # solar -> lunar -> summary
```

## Connections

### Uses
- [Ephemeris Common](ephemeris_common.md) — `iso_ut` only (its own scan
  loop calls the Swiss Ephemeris' direct eclipse finders, not `Marcher`)
- `pyswisseph`'s global eclipse finders; the same `events.sqlite` as
  [Extract](extract.md) (new tables)

### Used by
- `research/ephemeris/test_ephemeris.py` — the 1999-08-11 / 2024-04-08
  total-solar and 2019-01-21 total-lunar golden checks (see
  [Ephemeris (subfolder)](../___ephemeris.md))

## Functions

- `open_db`, `meta_get`, `meta_set` — schema + resume bookkeeping (own
  tables, shared `meta`)
- `solar_type(flag)`, `lunar_type(flag)` — decode the Swiss Ephemeris return
  bitflag into a type string
- `scan_solar`, `scan_lunar` — the resumable global-finder scan loops
- `build_summary` — counts, per-century rate, first/last events, the ΔT
  caveat text, written to `eclipses_summary.json`
