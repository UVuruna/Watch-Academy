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
- [Deep Time Repository](deep_time.md) — the optional chain target
  beyond the bundle (Session 16)
- `_io.load_json_checked`

### Used by
- [App Controller](../app/controller.md) (M3),
  [Core (folder)](../core/___core.md) CLI,
  [Tests (folder)](../tests/___tests.md)

## Classes

### MoonPhaseRepository
- Constructed with the optional Deep Time pack (`deep=`, Session 16) —
  injected once by the controller.
- `moon_window(year)`: filters month keys with `isdigit()` (year entries
  mix months with aggregate counts), normalizes "Last Quarter" →
  "Third Quarter", spans year−1..year+1 so any instant inside the year
  has bracketing events. A year the bundled file does not hold chains
  to the pack (the WHOLE window from one source, never mixed); without
  the pack it raises `ValueError` naming the range (derived from the
  data, not hardcoded).
- `coverage()`: the inclusive `(first, last)` years the BUNDLED file
  holds, read from the data (owner 2026-07-16) — the controller
  intersects it with the seasons coverage and widens with the pack's
  coverage when present.
