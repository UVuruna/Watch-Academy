# core/

**Planned — implemented in M2.** Pure computation: zero Qt, zero file I/O,
zero `datetime.now()` — callers inject "now" and pre-extracted data, so every
function is deterministic, pytest-testable headless, and reusable for a
future mobile version.

## Planned Files

### `angles.py` — Time → Dial Angle
The one shared time→angle mapping (noon at top, clockwise) used by the hour
hand, all sun-event arc boundaries and the solar-noon marker; minute-hand
angle; hexagram rotation from the solar-noon offset.

### `sun.py` — Sun Events & Daylight Regimes
The five sun events (dawn/sunrise/noon/sunset/dusk) computed INDIVIDUALLY
(per-event error handling — polar day/night make some events nonexistent);
`DaylightRegime` classification (NORMAL, WHITE_NIGHTS, TWILIGHT_ONLY,
POLAR_DAY, POLAR_NIGHT).

### `year_wheel.py` — Year Marker
Piecewise-linear interpolation between the season anchors from
`seasons_utc.json`: summer solstice exactly at the top, winter at the
bottom, equinoxes exactly at 90°/270°.

### `moon.py` — Moon Phase
Cycle-fraction interpolation between principal-phase instants +
illumination fraction.

### `clock_state.py` — Two-Tier State
`DayContext` (frozen per-day: sun events, hexagram rotation, weekday, year
angle, moon fraction; cache key `(local_date, utcoffset)` so DST is caught)
and `TickState` (per-minute hand angles).

### `__main__.py` — CLI Selftest
`python -m core --city ... [--at ISO]` prints the full computed state —
the time-travel flag for eyeballing DST/polar/solstice days.

## Connections

### Uses
- [Config (folder)](../config/___config.md)

### Used by
- [App (folder)](../app/___app.md), [Render (folder)](../render/___render.md) (M3)
