# Seasons

**Script:** [Seasons (script)](seasons.py)

## Purpose
Builds `YearAnchors` (six season instants bracketing a calendar year)
from `seasons_utc.json`, once per year, discarding the parsed file.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — database path, coverage range
- [Year Wheel](../core/year_wheel.md) — the `YearAnchors` dataclass
- [Deep Time Repository](deep_time.md) — the optional chain target
  beyond the bundle (Session 16)
- `_io.load_json_checked`

### Used by
- [App Controller](../app/controller.md) (M3) on year change,
  [Core (folder)](../core/___core.md) CLI,
  [Tests (folder)](../tests/___tests.md)

## Classes

### SeasonsRepository
- Constructed with the optional Deep Time pack (`deep=`, Session 16):
  the controller detects the pack ONCE and injects it here.
- `year_anchors(year)`: `[entry.start, spring.start, summer.start,
  autumn.start, winter.start, entry.end]` → `YearAnchors`. A year the
  bundled file does not hold chains to the pack (proxy-shifted where
  datetime cannot carry it); without the pack it raises `ValueError`
  naming the supported range (derived from the data, not hardcoded).
  Bundled years NEVER go to the pack — the minute-exact tier stays
  bit-identical. Never touches `winter.duration` (it belongs to the
  PREVIOUS winter — verified trap).
- `coverage()`: the inclusive `(first, last)` calendar years the BUNDLED
  file holds, read straight from the data (owner 2026-07-16) — the
  controller intersects it with the moon coverage for the minute-exact
  core tier and widens with the pack's own coverage when present.
