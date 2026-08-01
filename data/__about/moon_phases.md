# Moon Phases Repository

**Script:** [Moon Phases Repository (script)](../moon_phases.py)

## Purpose

Builds a `MoonWindow` (sorted principal-phase events of a calendar year
plus its two neighbor years) from `Database/moonPhases_utc.json`, cached
once per year. Year entries mix month dicts (`"1"`..`"12"`) with
year-level aggregate count keys (e.g. `"New Moon": 12`); month keys are
filtered with `isdigit()`. The database's `"Last Quarter"` event name is
normalized to `"Third Quarter"` on load.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `paths.database_dir()`,
  `constants.MOON_PHASE_FRACTIONS`
- [Core (folder)](../../core/___core.md) — the `MoonWindow` dataclass
  (`core/moon.py`)
- [Deep Time Repository](deep_time.md) — the optional chain target
  beyond the bundled file's coverage

### Used by
- [Watch Controller](../../app/__about/controller.md) — injects the optional
  Deep Time pack once at startup
- [Core (folder)](../../core/___core.md) CLI (`core/__main__.py`)
- [Tests (folder)](../../tests/___tests.md) — run against the live
  bundled file

## Classes

### MoonPhaseRepository
- `__init__(path=None, deep=None)`: `deep` is the optional
  `DeepTimeRepository`, injected once by the controller.
- `coverage()`: the inclusive `(first, last)` calendar years the
  BUNDLED file holds, read straight from the data (never hardcoded).
- `moon_window(year)`: events of `year - 1 .. year + 1` so any instant
  inside `year` has bracketing events. A year the bundled file has no
  entry for chains to the injected Deep Time pack (the WHOLE window
  comes from one source, never mixed with the bundle); without a pack
  it raises `ValueError` naming the supported range.
