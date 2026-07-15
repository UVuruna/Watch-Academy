# tests/

Headless pytest suite; run with `python -m pytest tests` from the project
root (the root `conftest.py` puts the packages on `sys.path`). Core, data
and settings tests need no QApplication; the render tests create one on
the `offscreen` Qt platform.

## Files

### `test_angles.py`
Dial-angle quadrants (12:00→0°, 18:00→90°, 00:00→180°, 06:00→270°),
minute hand, hexagram sign convention (±15°/hour).

### `test_sun.py`
Golden sun values: Belgrade DST hexagram jump −4.17°→+10.76° across
2026-03-28/29; the four Tromsø daylight regimes; Longyearbyen polar
night with solar noon still computable (11:55, rotation −1.2°); Santiago
de Compostela +39.8° summer / +23.0° winter; Kamchatka +22.6°; the
mockup day 20.6.2025 (sunrise 04:52, sunset 20:27).

### `test_year_wheel.py`
Cardinal points EXACTLY at 0/90/180/270 (rejects naive linear-over-year,
which lands the autumn equinox at ~92.3°); monotonicity; loud
out-of-span failure; mockup-day Earth within 2° of the top; the
`winter.start` field trap (previous vs this December solstice).

### `test_moon.py`
Fraction 0.74 on 2026-07-07; exactness at anchor instants; May 2026 has
5 events (two full moons); "Last Quarter" normalization; illumination
curve.

### `test_clock_state.py`
Composition through the real repositories for Belgrade 2026-07-07 12:00
CEST: cache key with DST offset (including the spring-forward day, where
the key must carry the offset of NOW, not midnight), weekday→Mars,
hexagram tilt range, hands at the top, `is_daylight`, year angle ~16 days
past the solstice.

### `test_elements.py`
The Elements switches (FINAL.txt #5): pointer off drops the star AND
the octa info slot, weekday off drops the bodies and the center, both
markers off drop the year-marker layer, seconds off drops the third
hand; Colorful off paints the Aura white (pixel saturation probe);
switched-off elements answer no hovers.

### `test_render.py`
Offscreen compositor smoke tests (`QT_QPA_PLATFORM=offscreen`): frame
size, transparent corners, opaque ring, painted center, yellowish noon
sector in July daylight.

### `test_repositories.py`
Against the LIVE Database files: 5 continents, 241 countries, 121
mixed-depth, 45,649 cities (post-curation shape); the audited
admin-nested sample (Serbia→Banat→Ada); the macro-region curation;
Belgrade lookup; loud unknown-path and out-of-coverage errors.

### `test_settings_store.py`
Round-trip, atomic-write cleanup, BOM tolerance, corruption and
diameter-range errors, quarantine-to-.bak.

### `test_profiling.py`
The `@timed` statistics store (owner 2026-07-15): cumulative
aggregates with session-only recents, atomic persistence and reset;
the Report's readable-unit formatting (ns whole, µs/ms at two
decimals, s at three).

### `test_purity.py`
Asserts nothing under `core/` or `data/` mentions PySide6 — and that
library code reads no wall clock (`datetime.now`/`.today`/`time.time`;
`core/__main__.py` is exempt as CLI glue).

## Connections

### Uses
- [Core (folder)](../core/___core.md), [Data (folder)](../data/___data.md),
  [App (folder)](../app/___app.md) (settings store),
  [Database (folder)](../Database/___database.md)
