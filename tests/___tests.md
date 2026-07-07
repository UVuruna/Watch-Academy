# tests/

Headless pytest suite — no QApplication anywhere; run with
`python -m pytest tests` from the project root (the root `conftest.py`
puts the packages on `sys.path`).

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
CEST: cache key with DST offset, weekday→Mars, hexagram tilt range, hands
at the top, year angle ~16 days past the solstice.

### `test_repositories.py`
Against the LIVE Database files: 5 continents, 241 countries, 127
mixed-depth, 45,650 cities; the audited admin-nested sample
(Serbia→Banat→Ada); Belgrade lookup; loud unknown-path and
out-of-coverage errors.

### `test_settings_store.py`
Round-trip, atomic-write cleanup, BOM tolerance, corruption and
diameter-range errors, quarantine-to-.bak.

### `test_purity.py`
Asserts nothing under `core/` or `data/` mentions PySide6.

## Connections

### Uses
- [Core (folder)](../core/___core.md), [Data (folder)](../data/___data.md),
  [App (folder)](../app/___app.md) (settings store),
  [Database (folder)](../Database/___database.md)
