# Download Ephemeris Data

**Script:** [Download Ephemeris Data (script)](../download_ephe.py)

## Purpose

Fetches the Swiss Ephemeris `.se1` data files the pipeline needs (Sun+Moon,
~98 MB across ~100 files) from the maintained `aloistr/swisseph` GitHub
mirror — Astrodienst's old ftp path now just redirects there. Enumerates the
mirror's `ephe/` folder, keeps only the wanted prefixes (`sepl*` planets
incl. Sun, `semo*` Moon), downloads each with exponential-backoff retries
into `./ephe/`, and skips any file already present at the correct size (so
re-runs are cheap). Coverage is then VERIFIED by probing `swe.calc` at both
temporal extremes.

## Usage

```bash
python download_ephe.py
```

Run from `research/ephemeris/`, under the pipeline's own venv (see
[Ephemeris (subfolder)](../___ephemeris.md) → How to rerun). Prerequisite
for [Extract](extract.md) and [Extract Eclipses](extract_eclipses.md).

## Connections

### Uses
- GitHub's REST API (`api.github.com`) and raw content host
  (`raw.githubusercontent.com`)
- Writes into `research/ephemeris/ephe/` (gitignored)

### Used by
- [Extract](extract.md), [Extract Eclipses](extract_eclipses.md) — both
  require `ephe/` populated first
- [Ephemeris (subfolder)](../___ephemeris.md) — step 2 of "How to rerun"

## Functions

- `_get(url, retries, timeout)` — HTTP GET with exponential-backoff retry
- `list_files()` — the mirror's file list, filtered to the wanted prefixes
  and `.se1` extension
- `download_all()` — downloads every missing/undersized file, with a running
  progress percentage of the total byte count
- `verify_coverage()` — probes `swe.calc` for the Sun at three years
  (`-12998`, `0`, `17000`) spanning the whole scan window
