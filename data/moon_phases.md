# Moon Phases

**Script:** [Moon Phases (script)](moon_phases.py)

## Purpose
Builds `MoonWindow` (sorted principal-phase events of a year ± neighbor
years) from `moonPhases_utc.json`, once per year.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — database path, coverage
  range, phase-name → fraction mapping
- [Moon](../core/moon.md) — the `MoonWindow` dataclass
- `_io.load_json_checked`

### Used by
- [App Controller](../app/controller.md) (M3),
  [Core (folder)](../core/___core.md) CLI,
  [Tests (folder)](../tests/___tests.md)

## Classes

### MoonPhaseRepository
- `moon_window(year)`: filters month keys with `isdigit()` (year entries
  mix months with aggregate counts), normalizes "Last Quarter" →
  "Third Quarter", spans year−1..year+1 so any instant inside the year
  has bracketing events; outside 1551–2649 raises `ValueError` naming
  the range.
