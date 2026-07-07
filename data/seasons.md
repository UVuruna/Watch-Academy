# Seasons

**Script:** [Seasons (script)](seasons.py)

## Purpose
Builds `YearAnchors` (six season instants bracketing a calendar year)
from `seasons_utc.json`, once per year, discarding the parsed file.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — database path, coverage range
- [Year Wheel](../core/year_wheel.md) — the `YearAnchors` dataclass
- `_io.load_json_checked`

### Used by
- [App Controller](../app/controller.md) (M3) on year change,
  [Core (folder)](../core/___core.md) CLI,
  [Tests (folder)](../tests/___tests.md)

## Classes

### SeasonsRepository
- `year_anchors(year)`: `[entry.start, spring.start, summer.start,
  autumn.start, winter.start, entry.end]` → `YearAnchors`; outside
  1560–2640 raises `ValueError` naming the supported range. Never touches
  `winter.duration` (it belongs to the PREVIOUS winter — verified trap).
