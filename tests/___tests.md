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
settings home) — R5 MENU REWORK shrank the gating test to the
Archetype toggle + the Pointer Theme/Slot Theme entries (the Design/
slot-submenu-specific tests moved to `test_menu_rework.py`, which now
owns the whole R5 round; several tests tied to the retired Quick
Jump/Design/Slot submenus and the Elements→Visible rename were
removed here as their subject moved).

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
guard blocks the die-visibly SystemExit path. The R5 Quick Jump ROWS
(item 3A) goldens live in `test_menu_rework.py` instead (arrow clicks
edit the dialog's own fields without touching a live simulation,
eclipse-row graying, pole/Greenwich/city rows).

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
validate loudly. ADD WATCH round (owner INSTRUCTION.txt item 2, sealed
2026-07-21): `config.paths.settings_path(watch_index)`'s naming scheme
(`settings.json` for watch 1, `settings.<N>.json` for 2+, sharing one
user dir), independent round-trips per watch file, and
`discover_watch_indices()`'s startup scan (finds every numbered file,
ignores a quarantined `.bak`/an in-flight `.tmp`, `[1]` on an empty dir).

### `test_tray.py`
ADD WATCH round (owner INSTRUCTION.txt item 2B): the per-watch tray
icon rule — watch 1 the gold master untouched, watch 2 the pre-existing
rose-gold master (not a recolor), watch 3+ tinted along the CALENDAR
MONTH color wheel starting PURPLE `#8000FF` (R:G:B 1:0:2, the owner's
own worked example) then BLUE `#0000FF` (R:G:B 0:0:1) and onward,
wrapping forever past December; every `logo_icon(watch_index)` call
returns a non-null `QIcon`.

### `test_watch_manager.py`
ADD WATCH round: `app.watch_manager.AppController` builds one anchor
watch (index 1) at startup and rediscovers every watch on disk across a
restart; `add_watch()` seeds a new watch's settings from the CURRENT
watch (position cleared so it re-centers instead of overlapping);
`remove_watch()` refuses the anchor, confirms via a Yes/No box before
tearing a watch down, and deletes its settings file — a removed watch's
own index is never reused while a higher one survives; the menu TITLE
row (and ONLY the title row — the tray hover stays full always) switches
short/full as the roster crosses two watches; Exit is wired to the
manager's `quit_all()` (process-wide) on every watch, Remove Watch stays
per-watch.

### `test_profiling.py`
The `@timed` statistics store (owner 2026-07-15): cumulative
aggregates with session-only recents, atomic persistence and reset;
the Report's readable-unit formatting (ns whole, µs/ms at two
decimals, s at three).

### `test_purity.py`
Asserts nothing under `core/` or `data/` mentions PySide6 — and that
library code reads no wall clock (`datetime.now`/`.today`/`time.time`;
`core/__main__.py` is exempt as CLI glue).

### `test_controller_dialogs.py`
R4 owner instruction batch 2026-07-20, ITEM 1/3: Encyclopedia/Guide/
Observatory open NON-MODAL (`.show()`, `isModal()` False) and stay that
way while the dial keeps processing events; a second open request
RAISES the live instance (identity-checked) instead of stacking a
duplicate; a themed second SPACE jump NAVIGATES the live Encyclopedia
window (`navigate_to`); closing a dialog clears the controller's own
reference; `quit()` closes every still-open one — widened this round
to the three R5 mini windows too (Design/Pointer Theme/Slot Theme).
Opening sizes: A4 portrait at 80% screen height (Encyclopedia
respecting its own gallery min-width law, Observatory), square at 50%
(Guide, Settings respecting its own content-width floor) — built
against a REAL `WatchController` (standalone construction, unchanged
by the ADD WATCH round's `app.watch_manager.AppController`), minus the
single-instance mutex and `run()`'s tray/scheduler/background-thread
side effects.

### `test_menu_rework.py`
R5 MENU REWORK round (owner spec 2026-07-20,
`UV/DESIGN/RIGHT CLICK MENU.txt` + `UV/INSTRUCTION.txt` item 2A):
`watch_title` both forms (short = location, full = the owner's own
"Belgrade-Gold DOMY-Family Trinity" worked example, untranslated by
signature); the TITLE row heading the menu + the tray tooltip staying
live through `_install_skin` without a rebuild; the keyboard
`SHORTCUTS` table (the ten owner-named action ids, every entry
carrying a modifier so it can never feed the hidden-mode secret
buffer, `shortcut_display`'s "Ctrl+R" rendering), a bare
`ClockWidget.keyPressEvent` → `shortcut_triggered` mapping for every
table entry (isolated from a real controller so it cannot open a
blocking modal), `WatchController._on_shortcut`'s full dispatch table,
`_cycle_ring`/`_cycle_slots`'s legal-state walks; the Elements→Visible
rename (menu text, no stale `_element_*` identifiers); the Time
Travel window's own Quick Jump rows (item 3A — arrow clicks edit the
dialog's own fields without touching the live simulation, an edge
clamp is a no-op, eclipse rows gray without the Deep Time pack, pole/
Greenwich/city rows); and the three mini windows (Pointer Theme, Slot
Theme, Design, item 3B/3C/3D) — non-modal + raises-on-second-open,
their own gating (Archetype-on, Pointer hidden, no Slot visible), live
regray while already open, and picks applying through the SAME
`_set_*` methods the old menu chains used.

## Connections

### Uses
- [Core (folder)](../core/___core.md), [Data (folder)](../data/___data.md),
  [App (folder)](../app/___app.md) (settings store),
  [Database (folder)](../Database/___database.md)
