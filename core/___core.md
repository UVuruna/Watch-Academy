# core/

Pure computation: zero Qt, zero file I/O, zero `datetime.now()` in library
code — callers inject "now" and pre-extracted data, so every function is
deterministic, pytest-testable headless, and reusable for a future mobile
version. A purity test enforces the no-Qt rule.

## Files

### `angles.py` — Time → Dial Angle
The one shared time→angle mapping (noon at top, clockwise: 12:00→0°,
18:00→90°, 00:00→180°, 06:00→270°) used by the hour hand, the sun-event
arc boundaries and the solar-noon marker; the minute-hand angle; the
hexagram rotation from the solar-noon offset (+15°/hour late, computed
from integer seconds to avoid timedelta sign bugs).
See [Angles](angles.md).

### `sun.py` — Sun Events & Daylight Regimes
The five sun events (dawn/sunrise/noon/sunset/dusk) computed INDIVIDUALLY
via astral — `astral.sun.sun()` is all-or-nothing and its polar-day and
polar-night error messages are identical. `noon()` never raises, so the
hexagram is always computable. `DaylightRegime` classification: NORMAL,
WHITE_NIGHTS, TWILIGHT_ONLY, POLAR_DAY, POLAR_NIGHT (elevation checks
against −0.833°/−6°). See [Sun](sun.md).

### `year_wheel.py` — Year Marker
Piecewise-linear interpolation between the six season anchors of a
calendar year: summer solstice exactly at the top, winter at the bottom,
equinoxes exactly at 90°/270° (naive linear-over-year is ~2.3° wrong at
the equinoxes and is rejected by the golden tests).
See [Year Wheel](year_wheel.md).

### `moon.py` — Moon Phase
Cycle-fraction interpolation between principal-phase instants +
illumination fraction; exact at the anchors, ~0.0001 cycle accurate in
between (astral.moon is day-granular and not used).
See [Moon](moon.md).

### `clock_state.py` — Two-Tier State
`DayContext` (frozen per-day bundle; cache key `(local_date, utcoffset)`
catches DST — the hexagram legitimately jumps 15° at transitions) and
`TickState` (per-minute hand angles + smooth year angle).
See [Clock State](clock_state.md).

### `__main__.py` — CLI Selftest
`python -m core --city NAME [--at ISO]` (or `--lat --lng --tz`) prints
the full computed state — the time-travel flag for eyeballing DST, polar
and solstice days. Verified against the design mockup for 20.6.2025:
sunrise 04:52, sunset 20:27, solar noon 12:39, Friday→Venus, Earth at
the top.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — dial/sun/moon invariants

### Used by
- [Data (folder)](../data/___data.md) — constructs `YearAnchors`/`MoonWindow`
- [App (folder)](../app/___app.md) and [Render (folder)](../render/___render.md) — consume `DayContext`/`TickState` (M3)
- [Tests (folder)](../tests/___tests.md) — golden-value suite

## Design Decisions
- Events may be `None` (documented polar behavior) — the regime enum, not
  exception text, tells the renderer which sectors exist.
- All angles are degrees clockwise from the dial top, directly usable by
  `QPainter.rotate()` in y-down screen coordinates.
