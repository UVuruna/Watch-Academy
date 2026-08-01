# Seasons Repository

**Script:** [Seasons Repository (script)](../seasons.py)

## Purpose

Builds a `YearAnchors` (six season-boundary instants bracketing a
calendar year) from `Database/seasons_utc.json`, parsed once per year
and cached; the source dict is discarded after extraction. Field
semantics (numerically verified): an entry for year N is self-contained
— `start` is the December solstice of year N−1, `spring`/`summer`/
`autumn.start` are the instants inside year N, `winter.start` is the
December solstice OF year N, and `end` is the spring equinox of year
N+1. `winter.duration` describes the winter that BEGINS the entry, so
it must never be paired with `winter.start` (which ends it).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `paths.database_dir()`
- [Core (folder)](../../core/___core.md) — the `YearAnchors` dataclass
  (`core/year_wheel.py`)
- [Deep Time Repository](deep_time.md) — the optional chain target
  beyond the bundled file's coverage

### Used by
- [Watch Controller](../../app/__about/controller.md) — injects the optional
  Deep Time pack once at startup, calls on year change
- [Core (folder)](../../core/___core.md) CLI (`core/__main__.py`)
- [Tests (folder)](../../tests/___tests.md) — run against the live
  bundled file

## Classes

### SeasonsRepository
- `__init__(path=None, deep=None)`: `deep` is the optional
  `DeepTimeRepository`, injected once by the controller.
- `coverage()`: the inclusive `(first, last)` calendar years the
  BUNDLED file holds, read straight from the data (never hardcoded).
- `year_anchors(year)`: the six anchor instants of `year`. A year the
  bundled file has no entry for chains to the injected Deep Time pack
  (proxy-shifted where `datetime` cannot hold the real year); bundled
  years NEVER go to the pack. Without a pack it raises `ValueError`
  naming the supported range.
