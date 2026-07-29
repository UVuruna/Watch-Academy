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

### `test_rose_pointer.py`
THE ROSE — the seventh pointer (owner seal 2026-07-27, [The Cube
Canon](../CUBE.md) §The Rose). Pins the three-star geometry and its
z-order on both wheels (`ROSE_STAR_OFFSETS` in DRAW order; the 0° star
topmost on BOTH, so the dominant arm always points at true 12h;
Prophecy rides the FUTURE star in the middle z-layer), the one
`ROSE_PALETTE` shared by both wheels and the Character wheel, the
weekday COLOR LAW with its dual Sunday (Ruler red 18h, Servant blue
06h, Thursday and Wednesday keeping their canonical seats) and the
DAYLIGHT switch (only the Calendar and the Rose honor it; the stored
setting survives a pointer switch on the other five). Two of its pins
are guards rather than goldens: the four cardinal hues are checked
against `core.year_wheel`'s OWN computed turning-point angles — proof
the palette and the year agree — and
`test_the_rose_ring_preset_is_gone_for_good` fails the moment any
trace of Session 20's mis-built RING preset reappears (Rule #25 — the
recurrence pin, since that build came from a canon mis-transcription
and was deleted whole).

### `test_pointer_shapes.py`
THE POINTERS REWORK, phase 1 (owner sheet `UV/Pointers.png`, sealed
2026-07-29) — see
[The Pointer Shapes](../render/layers.md#the-pointer-shapes). Pins the
two SHAPES and their geometry, measured on the DRAWN paths rather than
re-derived from the formulas: one vertex per arm tip; the plain polygon
really being a square / hexagon / octagon (every sampled point on the
straight chord, not merely the corners); the CUBE standing in for the
Trinity's triangle, silhouette-identical to the Cube look's own figure;
the Calendar's two hexagrams (odd wedges under the even ones) and its
twelve-point polygon; the Rose's twenty-four rays. The CURVATURE is
pinned as a law, not as numbers: 0 = the plain polygon, strictly
monotone inward, 1.0 landing exactly on the star's inner radius, the
two edge forms agreeing ONLY at 0 — and inert on the Calendar and the
Rose. The OFFSET WHEELS: the Seasons' boundaries on 12h/3h/6h/9h in
both shapes, the Prophecy rays on HH:30 while Legacy keeps the hours,
with a pin that the shift moves no hue off its own ray. The AURA
alignment (the owner's top-priority fix): golden wedge angles for both
Rose wheels plus the general law — every ray falls inside the wedge
drawn in its own hue. Plus the night-border option (clip law, inert
while daylight is off, and an offscreen pin that it repaints the night
and not the day) and the settings round-trip of the four new keys
(defaults for a pre-rework file, `SettingsCorruptError` for a
hand-edited bad value). `test_the_star_shape_is_untouched_by_the_rework`
is the regression pin that the default dial did not move. Phase 3
(the Design window's own rows, `test_design_window.py` below) closes
the loop here too: `test_the_four_design_rows_persist_and_reach_the_
live_skin` drives a REAL `WatchController`'s `_design_setters()` and
checks both `Settings` and the installed skin move.

### `test_design_window.py`
The `DesignDialog` regressions — THE TAB BOUNCE fix (owner fix
2026-07-26: a live-apply rebuild now keeps whichever tab was open) and,
since Pointers REWORK phase 3 (owner sheet `UV/Pointers.png`,
2026-07-29), the Pointer tab's three new rows: the full pointer×shape
gating matrix for Shape / Curvature+Edge / Hide-night-borders (a
polygon pointer in "Polygon" shape shows all three; Aurora shows none;
the Calendar and the Rose never show Curvature+Edge even in "Polygon"
shape, since their own "polygon" is a touching-arm star that never
curves), and which widget calls which `_setters[...]` key with which
value (a `_RecordingSetters` stub — the real wiring, persistence and
the live skin, is `test_pointer_shapes.py`'s own controller test above).

### `test_cube_seating.py`
The Seating geometry goldens (WORKPLAN Session 26, CUBE.md §The
Seatings). It does NOT merely compare against the sealed constants — it
RE-RUNS the exhaustive search, law by law, so the Rose-24 ring can never
drift away from the argument that produced it. Pinned: the 65-term table;
the 3 + 6 + 3 family counts that make the symmetry law possible at all;
THE SYMMETRY LAW itself (the owner's own hexagram pairs 12h-24h, 4h-16h,
20h-8h, and what it costs — 48 of the 1056 rings obey it); the parity
theorem (14 vs 12 over all 26 cells, 12 vs 12 once the Sacred pair
leaves); the funnel 1056 → 48 → 8 → 4 → 2 → 1; the proven 4-of-6 ceiling
on pole hues and the mirrored Activation pencil; the hue-pencil
structure; the Calendar's three families at exactly 120°/120°/60° plus
the inverted version; the radial law; and the two negative results on
rotation↔hour (no element of order 24; the half-turn is the inversion).

### `test_cube_roster.py`
The ROSTERS (WORKPLAN Session 24, CUBE.md §The Rosters) — who holds each
of the twenty-six human cells in each of the three figure sets, and who
echoes the two sacred corners. The pins run canon → engine: every name
the engine speaks must stand in `CUBE.md` (a typo or a quiet swap fails
at once), the sealed 108 seats are spot-pinned unchanged and the 48 new
edge seats are pinned whole. Structural pins: each seat's three sets are
three DIFFERENT people (Charter rule 5); a figure repeats ONLY between a
vertex and its own flat shadow — proved from the coordinates, not from a
hand-written list of exceptions; the 52 people this round added are each
new and each seated once; the centre answers `None` in every register (by
doctrine); an unknown cell, seat or register RAISES; both Rose wheels
resolve their 48 seat-readings through the one table; each Cube wheel arm
seats the cell its own two names claim; and the star map, the roster and
the disk registers now speak ONE vocabulary.

### `test_cube_wheels.py`
The Cube wheels engine goldens (WORKPLAN Session 20; owner seal
2026-07-26, CUBE.md): the third-wheel slot (the "cube" style exists
only on trio/hexa/octa; sealed menu labels; `effective_palette_style`
normalization at `apply_display_settings` and in the watch title), the
sealed cube palettes (Genesis' moon-gray inverted trio, the Council's
re-dressed hexa wheel, Character = `ROSE_PALETTE` exactly as the Rose
is drawn), the Genesis inversion end to end (offset only on trio·cube;
figures/lit-index/weekday-slots on the 24h/16h/08h arms; the arm
hover speaking its creation office with the pending line and a silent
Spacebar jump), the Council/Character figure tables, the Diamond/Cube
display toggle (family gating; 180/N face-rhombus halves), the
settings round-trip, and the Rose ring preset (the computed card,
the procedural skin, an offscreen render carrying all eight ray hues,
and the per-ray hover legend).

### `test_cube_encyclopedia.py`
The Cube ENCYCLOPEDIA wave (WORKPLAN Session 21, 2026-07-27): the
three new `encyclopedia.json` families are complete (20 + 5 + 14
pages) and every one of them obeys the Article Charter's four
movements in order; the 24-field union table names all twelve
office/process pairs; the Two Crosses carry the Latin and Greek rows,
the chiasm, TRUST/DISTRUST and both ciphers; the Archetypes hall's
three topics resolve and every Cube wheel figure's `enc` index lands
on the page it argues (the Spacebar contract); the three wheels'
article sets speak their own prose instead of the pending line; the
six combo figures the owner delegated to this session are written;
the sealed prism-light theme name (all three kept, "One Soul" alone
where one name must stand, and the hexa PRIMARY slot renamed to
**Persons** on 2026-07-27); and a REGRESSION PIN on the Charter
rework — the exact scene-describing phrases that were removed can
never come back.

### `test_one_soul_theme.py`
The ONE SOUL theme (owner verdict 2026-07-27): the `one_soul`
encyclopedia family is complete and in the wheel's own arm order
(title page, six pillars 12h→08h, the Union, the Child) with every
page obeying the Article Charter; the pages carry the DOCTRINE a
hover cannot — the conjugation law, all six cross-cures of the three
axes of love, the union's kept/felt faces, the family triangle and
its hearth roles; every pillar names its own shadow; the TRIPLE NAME
is what the reader actually sees (topic title + title page) while the
gallery card carries the single name, proved on a live offscreen
dialog that opens on the theme and pages through all nine entries;
the Spacebar contract for all six arms AND the centre; and a Rule #5
pin that no dial hover row is duplicated into a page.
`test_archetype.py` carries the same jump proved through the real
hover geometry.

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

### `test_app_info.py`
WORKPLAN Session 22 (the Renaming, 2026-07-27): pins the pre-M7
`setup/app_info.json` seed — `name`/`description` say **Watch Academy**
(the sealed application name, CUBE.md §The Name) while `exe_name`/
`installer_name` stay DOMY-based, since DOMY remains the dial's own
name and the on-disk/binary identity.

## Connections

### Uses
- [Core (folder)](../core/___core.md), [Data (folder)](../data/___data.md),
  [App (folder)](../app/___app.md) (settings store),
  [Database (folder)](../Database/___database.md)
