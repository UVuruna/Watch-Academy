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
5 events (two full moons); "Last Quarter" normalization; the nominal
cosine curve — and the TRUE analytic illumination goldens (Session 16):
~0/50/100/50 at every 2026 bundled principal instant (±0.6 p.p.), the
owner's cross-check (2026-07-17 10:11 → 11.5 ± 0.5%), the deep
proxy-frame un-shift, and the research-database sweep across the whole
span (skips cleanly when the gitignored research db is absent).

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

### `test_archetype.py`
THE ARCHETYPE MODE goldens (owner sealed package 2026-07-16): the
seven-archetype grid and figure/center tables, the render-level
override (slots/weekday off without mutating settings; the big
seconds hand returns), the hour-space lighting boundaries per pointer
(trio/cross/hexa/octa, solar rotation riding the drawn arms), the
1×1-placeholder fallback to the figure's name, the repurposed Omega
reveal hiding the hands, the graceful two-row article path and the
pending line, the Walks→Professions encyclopedia mapping, the Earth
day-label option, and the menu gating (full controller against a TEMP
settings home).

### `test_repositories.py`
Against the LIVE Database files: 5 continents, 241 countries, 121
mixed-depth, 45,649 cities (post-curation shape); the audited
admin-nested sample (Serbia→Banat→Ada); the macro-region curation;
Belgrade lookup; loud unknown-path and out-of-coverage errors; and
`coverage()` reading (1560–2640 / 1551–2649) straight from the data,
with the error message matching what coverage reports.

### `test_time_travel.py`
The BCE-capable moment editor (Session 16, owner slika 13): 4500 BCE
accepted with the pack coverage (era combo + spin → astro −4499, proxy
2301/cycles 17), the refusal messages (pack absent names the pack;
beyond the pack names the Laskar tier), the live precision-tier and
coverage lines, the dual-calendar header (Anno Lucis always paired;
third calendar joins), era labels per notation, proleptic Feb-29
clamping (year 0 IS leap), the inclusive bounds — and the proof the
guard blocks the die-visibly SystemExit path.

### `deep_fixture.py` + `test_deep_time.py`
Session 16: the SMALL fixture pack builder (same schema as the
generator — never the 92 MB build) and the Deep Time goldens: the
year-line formatters (owner amendment 2026-07-17), 1 BCE = year 0
round-trips, third-era years, the 400-year proxy frame (canonical
window, leap/weekday preservation), proleptic Julian Day (modern
goldens + a real-pack sweep that skips when the pack is absent), ΔT
sanity against measured Swiss Ephemeris values, quick-jump calendar
arithmetic (leap clamps, era edges), pack detection present/absent,
proxy-shifted anchors/windows, loud missing-year errors, repository
chaining (bundled years stay bit-identical), and eclipse next/prev
with the catalog-edge clamp.

### `test_settings_store.py`
Round-trip, atomic-write cleanup, BOM tolerance, corruption and
diameter-range errors, quarantine-to-.bak; the Session 16 keys
(era_notation/show_era_suffix/third_era/jump_cities) round-trip and
validate loudly.

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
