# core/

Pure computation: zero Qt, zero file I/O, zero `datetime.now()` in
library code (the one documented exception is `__main__.py`'s `--at`
default) — callers inject "now" and pre-extracted data, so every
function is deterministic, pytest-testable headless, and reusable
outside the desktop widget. `tests/test_purity.py` enforces the no-Qt
and no-wall-clock rules by AST inspection. Dial convention: degrees
CLOCKWISE from the TOP (12:00 noon top, 00:00 midnight bottom,
`DIAL_OFFSET_DEG = 180`).

## Files

| File | Tier | One line |
|------|------|----------|
| `angles.py` | Algorithmic | the one shared time -> dial-angle mapping — [about](__about/angles.md) · [flow](__flow/angles.md) |
| `ascendant.py` | Algorithmic | sidereal-time rising-sign math — [about](__about/ascendant.md) · [flow](__flow/ascendant.md) |
| `blue_moon.py` | Algorithmic | the Blue Moon Law — the hidden 13th member of every 12-set — [about](__about/blue_moon.md) · [flow](__flow/blue_moon.md) |
| `clock_state.py` | Algorithmic | the two-tier render state, `DayContext` + `TickState` — [about](__about/clock_state.md) · [flow](__flow/clock_state.md) |
| `continents.py` | Algorithmic | the Continents theme's Zealandia/Pangea Ninth-seat law — [about](__about/continents.md) · [flow](__flow/continents.md) |
| `cube_seating.py` | Algorithmic | the Character Cube's geometry — Calendar-12 and Rose-24 — [about](__about/cube_seating.md) · [flow](__flow/cube_seating.md) |
| `deep_time.py` | Algorithmic | Deep Time calendar mathematics — eras, the 400-year proxy, Julian Day, ΔT — [about](__about/deep_time.md) · [flow](__flow/deep_time.md) |
| `motto.py` | Algorithmic | outer Great Seal / station-word ring-arc glyph angles — [about](__about/motto.md) · [flow](__flow/motto.md) |
| `moon.py` | Algorithmic | moon phase fraction and analytic illumination — [about](__about/moon.md) · [flow](__flow/moon.md) |
| `sun.py` | Algorithmic | sun events and daylight-regime classification — [about](__about/sun.md) · [flow](__flow/sun.md) |
| `year_wheel.py` | Algorithmic | year-marker angle, piecewise-linear between season anchors — [about](__about/year_wheel.md) · [flow](__flow/year_wheel.md) |
| `__main__.py` | Standard | `python -m core` CLI selftest — prints the full computed state — [about](__about/__main__.md) |
| `__init__.py` | Trivial | module docstring only, no code |

## Connections

### Uses
- [Config (folder)](../config/___config.md) — every dial/sun/moon/cube
  invariant and threshold this layer reads

### Used by
- [Data (folder)](../data/___data.md) — constructs `YearAnchors`/`MoonWindow`
  from bundled ephemeris data, then hands them into `core`
- [App (folder)](../app/___app.md) — the controller drives the
  rebuild/tick flow (`build_day_context`/`build_tick_state`)
- [Render (folder)](../render/___render.md) — consumes `DayContext`/
  `TickState` every paint; `cube_diagrams`/`cube_model_export` reuse
  `cube_seating`'s `cell_color`/`find_pole`
- [Tests (folder)](../tests/___tests.md) — the golden-value suite pins
  every formula in this folder

## Design Decisions
- Events may be `None` (documented polar/edge behavior) — enums like
  `DaylightRegime`, not exception text, tell the renderer which sectors
  exist.
- All angles are degrees clockwise from the dial top, directly usable by
  `QPainter.rotate()` in y-down screen coordinates.
- **Nothing derivable is stored** (root Rule #19 — compute, don't
  generate): `cube_seating`'s families, indices and ray hues, the
  Calendar-12's twelve arms, and every angle in this folder are computed
  from a handful of rules, never enumerated as data.
- **Purity is the contract, not a convention** — `tests/test_purity.py`
  fails the build on any `PySide6` import or wall-clock call anywhere in
  `core/`, `data/`, or `recolor/`, with `core/__main__.py`'s `--at`
  default as the one documented, tested exception.
