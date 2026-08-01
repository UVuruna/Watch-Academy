# tests/

Headless pytest suite for an astronomical instrument — most of these tests
are GOLDEN-VALUE pins against real astronomy (equinox angles, DST hexagram
tilt, moon illumination, sunrise/sunset), not behavior checks against
invented numbers. Run with `python -m pytest tests` from the project root
(the root `conftest.py` puts the packages on `sys.path`). Core, data and
settings tests need no `QApplication`; render/GUI tests create one on the
`offscreen` Qt platform. A handful of tests RE-RUN an exhaustive search or
walk the real bundled `assets/`/`Database/` trees rather than compare
against a frozen constant, so a golden can never silently drift out of sync
with the argument that produced it.

Per [DOCS.md](../../../rules/DOCS.md) tier rules, `tests/` is a doc tier of
its own — this file is the ONLY doc in the folder; no `__about/`, no
`__flow/`, no per-test `.md`.

## Files

| File | What it pins |
|------|---------------|
| `test_angles.py` | Dial-angle quadrants (12:00→0°, 18:00→90°, 00:00→180°, 06:00→270°), minute hand, hexagram sign convention (±15°/hour). |
| `test_app_info.py` | Pre-M7 `setup/app_info.json` seed: product markets as **Watch Academy**, exe/installer stay DOMY-named. |
| `test_archetype.py` | THE ARCHETYPE MODE goldens: seven-archetype grid/figure/center tables, render-level override, hour-space lighting per pointer, Omega reveal, R5-shrunk menu gating. |
| `test_article_charter.py` | Article Charter rule 4 (no scene description): the exact deleted staging phrases stay dead; standing corpus lint bans depiction verbs while allowing legitimate "stands"/"standing" doctrine. |
| `test_assets_structure.py` | The `assets/` TAXONOMY MIRROR law: fixed top-level roots, no source-named/`alt/` folders survive, `weeks/<group>/<theme>` matches `WEEK_GROUPS`, every figure image sits at the one legal tree path. |
| `test_blue_moon.py` | 13th-member-of-the-year law: `thirteen_moon_year` against published full-moon counts, each 13th's window, the Cat's lunisolar leap month, the graceful-absent contract, the Calendar-only four-mode gate. |
| `test_calendar.py` | Calendar pointer: two wheels' palettes, Almanac real-calendar year mapping, Earth day-arrow, pinned slot layout, no-solar-rotation of wedges, deleted lit-wedge regression guards. |
| `test_clock_state.py` | Composition through the real repositories for Belgrade 2026-07-07 12:00 CEST: DST-aware cache key, weekday→Mars, hexagram tilt, hands, `is_daylight`, year angle. |
| `test_config_cohesion.py` | GUARD — see below. |
| `test_config_sections.py` | GUARD — see below. |
| `test_continents.py` | Continents theme: six-continent + polar-dual + Zealandia/Pangea-Ninth registration, Ninth easter-egg golden dates, Encyclopedia topic, live day/night body art. |
| `test_controller_dialogs.py` | Encyclopedia/Guide/Observatory open non-modal, a second open RAISES the live instance instead of stacking, a themed SPACE jump navigates it, `quit()` closes every open dialog, per-dialog opening sizes. |
| `test_cube_encyclopedia.py` | Cube ENCYCLOPEDIA wave: three new families complete and Charter-obedient, the 24-field union table, Two Crosses, each wheel figure's `enc` index, sealed theme name, Charter-rework regression pin. |
| `test_cube_preview3d.py` | 3D Preview integration: the model exporter validates against the sibling gadget's schema, `build_widget()` returns `None` for out-of-scope kinds and whenever the gadget is unreachable, the four page families mount a live panel when it IS present (skips, not fails, if the sibling folder is absent). |
| `test_cube_roster.py` | The ROSTERS: every engine-spoken name stands in `CUBE.md`, sealed 108 seats + 48 new edge seats, each seat's three sets are three different people, centre is always `None`, unknown cell/seat/register raises. |
| `test_cube_seating.py` | Seating geometry: RE-RUNS the exhaustive search (65-term table, the 3+6+3 family counts, the symmetry law, the parity theorem, the 1056→1 funnel, the pole-hue ceiling) rather than comparing frozen constants. |
| `test_cube_wheels.py` | Cube wheels engine: third-wheel "cube" slot, sealed cube palettes, the Genesis inversion end to end, Council/Character figure tables, Diamond/Cube toggle, settings round-trip, the Rose ring preset. |
| `test_deep_time.py` | (uses the `deep_fixture.py` helper below) Year-line formatters, 1 BCE = year 0, the 400-year proxy frame, proleptic Julian Day, ΔT sanity, quick-jump arithmetic, eclipse next/prev with catalog-edge clamp. |
| `test_design_window.py` | `DesignDialog`: the tab-bounce fix, the Pointer tab's Shape/Curvature+Edge/Hide-night-borders gating matrix per pointer×shape, night-borders row greys out when there is no night. |
| `test_doc_links.py` | GUARD — see below. |
| `test_docs_coverage.py` | GUARD — see below. |
| `test_dual_sunday_wheels.py` | THE DUAL SUNDAY WHEEL MAP: duality is a property of the wheel (center on hexa/trio/Seasons, vertical on Quaternity/Compass, horizontal on Rose/Character), plus the two sealed per-theme flips. |
| `test_eclipse.py` | Eclipse display: bounded (non-scanning) data lookup, the ±3h core window, red-solar/bronze-lunar render, the absence rule — no Deep Time pack means no eclipse ever renders. |
| `test_elements.py` | The Elements switches: pointer/weekday/marker/seconds toggles drop exactly their own layers, Colorful-off Aura pixel probe, switched-off elements answer no hovers. |
| `test_encyclopedia_loading.py` | THE LAZY LOADING LAW: naming a metal variant stays pure, pixels build only in `ensure_variant` (on display or in the background warm) — the fix for a main-thread minutes-long block on every art rename. |
| `test_encyclopedia_tree.py` | THE ENCYCLOPEDIA TREE: nine wholes seat every theme, the REACHABILITY LAW (every dial theme resolves to a seated topic bar documented look-only exceptions), no-horizontal-scroll, home 3×3 grid, variant-switcher offset, coverage law. |
| `test_intelligences.py` | Nine Intelligences rewrite: topic page order, the sealed day→intelligence mapping, the Sun's three faces, each article's virtue/vice/mood/weekday/profession web matches `symbolism.json`. |
| `test_menu_rework.py` | R5 MENU REWORK: `watch_title` short/full forms, the live title row + tray tooltip, the `SHORTCUTS` table and full dispatch, Elements→Visible rename, Time Travel Quick Jump rows, the three R5 mini windows. |
| `test_months.py` | THE SLAVIC MONTHS: twelve-month Gregorian-order registration, the sourceless `months/` root, the DESIGN ZODIAC mount radius, the Encyclopedia article web (etymology, Gregorian equivalent, pan-Slavic siblings). |
| `test_moon.py` | Fraction 0.74 on 2026-07-07, anchor-instant exactness, May 2026's 5 events, "Last Quarter" normalization, the TRUE analytic illumination goldens across every 2026 principal instant, the owner cross-check, the proxy-frame un-shift, the research-db sweep (skips cleanly when absent). |
| `test_ninth_mechanisms.py` | THE DOUBLE NINTH LAW: every registry-shape ninth maps to a `NINTH_MECHANISMS` entry a real dispatch implements, no orphan entries, the three sealed mechanisms by name, live active-only Encyclopedia behavior for the two live-state mechanisms. |
| `test_observatory.py` | The Observatory: committed series-bundle integrity, season/day-length math goldens, an offscreen render smoke test per chart. |
| `test_one_soul_theme.py` | ONE SOUL theme: the family complete in wheel arm order, every page obeying the Article Charter, the doctrine content itself, the triple-name display proved on a live offscreen dialog, the Spacebar contract, no duplicated hover row. |
| `test_palette_law.py` | GUARD — see below. |
| `test_pointer.py` | Pointer variants (hexa/cross/octa): slot layouts, shared-slot priority, palette presets, the octa bottom slot, the Umbra, the solar-rotation toggle. *(In the structure-law ratchet — owed a test-hygiene split.)* |
| `test_pointer_shapes.py` | THE POINTERS REWORK: the two shapes' geometry measured on drawn paths, the curvature law, the offset wheels staying on full hours, the owner's own AURA alignment numbers, the lead-line color, the daylight switch reaching the background, settings round-trip. |
| `test_profiling.py` | The `@timed` statistics store: cumulative aggregates with session-only recents, atomic persistence and reset, the Report's readable-unit formatting. |
| `test_prompt_paths.py` | THE SHEET-PATH LINT: every prompt sheet's declared `assets/...` drop path resolves to something a config table or consuming module actually references — catches sheet/code path drift before art is generated. |
| `test_purity.py` | GUARD — see below. |
| `test_recolor.py` | The metal transformer: golden pins plus one regression per named failure of the kernel it replaced, run against a SYNTHESIZED test plate (never the owner's gitignored `UV/` art). |
| `test_render.py` | Offscreen compositor smoke tests: frame size, transparent corners, opaque ring, painted center, yellowish noon sector in July daylight. |
| `test_repositories.py` | Against the LIVE `Database/` files: continent/country/city counts, an audited admin-nested sample, macro-region curation, Belgrade lookup, loud unknown-path/out-of-coverage errors, `coverage()` reading matching its own error text. |
| `test_rose_pointer.py` | THE ROSE pointer: three-star geometry and z-order on both wheels, the one shared `ROSE_PALETTE`, the weekday COLOR LAW with its dual Sunday, the DAYLIGHT switch's exact scope, the deleted-RING-preset recurrence pin. |
| `test_scale_rotation.py` | THE UNIVERSAL ROTATION CONVENTION: base file + `_vN` siblings + `alt/` pool merge into one daily rotation, the generic resolver and the Scale-specific wrapper, driven against synthetic tmp trees only. |
| `test_settings_dialog.py` | M6 settings window: location-picker cascade over the real database, opacity overrides, the palette editor. *(In the structure-law ratchet — owed a test-hygiene split.)* |
| `test_settings_store.py` | Round-trip, atomic-write cleanup, BOM tolerance, corruption/quarantine-to-`.bak`, Session 16 keys; ADD WATCH per-watch `settings.<N>.json` naming and `discover_watch_indices()`'s startup scan. |
| `test_shortcuts_r5b.py` | R5b FINAL MAP: the sealed shortcut table, the SLOTS/FAST TRAVEL/LOCATIONS families, the Fast Travel flash overlay, two real `ClockWidget.keyPressEvent` fixes (bare-Space-only, KeypadModifier masking). |
| `test_skins.py` | Ring presets and the built render config: the DOMY/PILOT/third bundled card goldens (layout, letters), `missing_assets` validation. *(In the structure-law ratchet — owed a test-hygiene split.)* |
| `test_startup_warm.py` | THE SLOW START fix (14.78s→1.46s for three watches): first paint runs NO metal recolor, the background drain builds it, the warm pass runs ONCE per process, legend-off skips the hover sweep entirely. |
| `test_structure_law.py` | GUARD — see below. |
| `test_sun.py` | Golden sun values: Belgrade DST hexagram jump −4.17°→+10.76°, the four Tromsø daylight regimes, Longyearbyen polar-night solar noon, Santiago de Compostela/Kamchatka angles, the mockup day 20.6.2025. |
| `test_system_trio.py` | The native SPACE-without-focus keyboard hook's install/uninstall bookkeeping and callback contract, stale-hover clearing off themed elements, the permanent crash-log file and a synthetic unhandled exception. |
| `test_theme_completeness.py` | GUARD — see below. |
| `test_time_travel.py` | The BCE-capable moment editor: 4500 BCE with pack coverage, refusal messages naming the right tier, the dual-calendar header, proleptic Feb-29 clamping, the guard against a die-visibly `SystemExit`. |
| `test_translations.py` | Translate-once-then-cache: corpus collection covers every article family, the hash-tracked cache only re-translates changed text, Serbian transliteration, the repository overlay — all offline. |
| `test_tray.py` | Per-watch tray icon rule: watch 1 the gold master, watch 2 the rose-gold master, watch 3+ tinted along the calendar-month color wheel starting purple, wrapping forever; every `logo_icon()` call returns non-null. |
| `test_watch_manager.py` | ADD WATCH: `AppController` builds/rediscovers watches across a restart, `add_watch()` seeds from the current watch, `remove_watch()` guards the anchor and tears down the dial window (not just the tray icon) plus its settings file. |
| `test_weekday_rotation.py` | The rotation convention reaching the weekday tree: real bundled `alt/` assets wired through `weekday_theme_body_art`/`theme_ninth`, THE WEEKLY MANDATE — cp_corpo's rosters turn by ISO-week parity, not daily ordinal. |
| `test_widget.py` | The clock window's z-order modes: the three-way `z_mode` swap and TRUE always-on-top re-assertion after Qt's native window recreation (the Win32 call is stubbed and counted). |
| `test_year_wheel.py` | Cardinal points EXACTLY at 0/90/180/270 (rejects naive linear-over-year), monotonicity, loud out-of-span failure, mockup-day Earth within 2° of the top, the `winter.start` field trap. |

## Guard tests — monorepo law enforcement

Nine tests enforce the monorepo constitution's laws rather than astronomy.
FOUR of them are the standard guard set every project in the monorepo
carries ([Code Rules](../../../rules/CODE.md) -> Enforcement) — marked
**[standard]** below; the rest are this project's own. All four standard
guards run from [Guard Runner (script)](run_guards.py), which the Claude
Code hooks in `.claude/settings.json` fire after every edit (`--fast`:
structure + config sections) and again when a session tries to stop (all
four). It exits **2**, which is what makes a hook BLOCKING.

- **`test_structure_law.py`** **[standard]** — THE STRUCTURE LAW's
  god-file ratchet. Fails the build on any `.py` file over ~1,000 lines
  that is not a named `RATCHET` entry; a second test fails if a healed or
  deleted file is still listed. Current ratchet: `app/controller.py`,
  `render/compositor.py`, `config/constants.py`, `config/pantheon.py`
  (owner-approved), `app/observatory.py`, plus five test files
  (`test_pointer.py`, `test_settings_dialog.py`, `test_skins.py`,
  `test_archetype.py`, `test_eclipse.py`) owed to a future test-hygiene
  round. `render/layers.py` LEFT the list on 2026-08-01 when it was split
  into `render/layers/` plus twelve responsibility modules — the ratchet
  only ever shrinks.
- **`test_config_sections.py`** **[standard]** — THE CONFIG SECTION LAW.
  For every `config/*.py`: no module-level patching of a table defined
  earlier in the same file (`TABLE[...] = ...`, `TABLE.update(...)`), no
  duplicate dict keys, and no top-level definition above the file's first
  section banner. It carries its own shrink-only `PATCHING_RATCHET`, today
  holding exactly one entry (`config/pantheon.py`) with the reason and the
  round that owes the fix.
- **`test_docs_coverage.py`** **[standard]** — THE DOCS LAW, coverage half.
  Every source file has exactly the docs its TIER requires — Trivial: none
  at all, Standard: `__about/{name}.md`, Algorithmic: `__about/` **and**
  `__flow/`. The tier assignment lives in the test itself as two
  frozensets, so changing a file's tier is a deliberate edit. It also
  refuses the two shapes MD-First 2.0 replaced: beside-script docs and
  orphan docs whose script is gone.
- **`test_doc_links.py`** **[standard]** — THE DOCS LAW, navigation half.
  No broken relative link in any project `.md`, and every project `.md`
  reachable from [Watch Academy (README)](../README.md) by following
  links.
- **`test_config_cohesion.py`** — the config split's own guard: every
  `config/*.py` file must be at/under the god-file threshold except the two
  entries already tracked in `test_structure_law.py`'s ratchet
  (`constants.py`, `pantheon.py`, not duplicated here); and no name that
  moved out of `config/defaults.py` into the six new modules (`dial`,
  `shortcuts`, `pantheon`, `calendar_mounts`, `encyclopedia_ui`, `glow`,
  `continents`) may still resolve as `defaults.<name>` (Rule #6, no
  re-export shims).
- **`test_purity.py`** — `core/`, `data/` and `recolor/` must import no
  PySide6 and must read no wall clock (`datetime.now`/`.today`,
  `time.time`); `core/__main__.py` is exempt from the wall-clock check
  only, as documented CLI glue.
- **`test_theme_completeness.py`** — THE THEME COMPLETION LAW: a registered
  theme (every `constants.WEEKDAY_THEMES` key) must resolve its article
  set, blurb set, title article and (if it has one) Ninth article, with two
  named exceptions; and every `assets/weeks/` theme folder must be either a
  registered key or an open row in the STAGING LEDGER
  (`research/theme_staging.md`) — the guard that would have caught the
  twelve-cast/429-file failure the law is named for.
- **`test_palette_law.py`** — THE COLOUR LAW: no hex or CSS `rgba(...)`
  literal anywhere outside `config/palette.py` (`tests/` itself is exempt —
  a probe fixture's fill is data, not a design decision); `PALETTE_PRESETS`
  values are bare names, never inlined hues; every pointer's palette
  entries form ONE contiguous run in the table; the table's pointer/style
  pairs agree with `constants.palette_styles_for`.
- **`test_app_info.py`** — the pre-M7 `setup/app_info.json` seed: `name`/
  `description` market the app as **Watch Academy** while `exe_name`/
  `installer_name` stay DOMY-based (`DOMYWatch.exe` /
  `DOMYWatch_Setup.exe`), since DOMY remains the dial's own on-disk/binary
  identity.

## Helper modules (not tests)

- **`art_debt.py`** — the ART DEBT REGISTRY: the one list of plates a
  REGISTERED theme has declared but the owner has not generated yet.
  `test_settings_dialog.py`, `test_skins.py`, `test_pointer.py` and
  `test_weekday_rotation.py` each read this ONE module instead of carrying
  their own hand-written exception list (Rule #5). Semantics are SUBSET,
  never equality — art arriving can never turn the suite red, but an
  ungueued gap fails immediately.
- **`deep_fixture.py`** — builds the SMALL Deep Time fixture pack (same
  schema as the real generator, never the 92 MB build) that
  `test_deep_time.py`'s goldens run against.

## How to run

```bash
python -m pytest tests
```

Honest warning: the full suite is SLOW — over ~15 minutes on the owner's
machine (dozens of offscreen Qt widgets, the exhaustive Cube-seating
search, the live `Database/` walk, the prompt-sheet corpus scan). Run a
single file or test while iterating:

```bash
python -m pytest tests/test_moon.py
python -m pytest tests/test_moon.py::test_fraction_matches_the_owner_cross_check
```

## Connections

- [Watch Academy (README)](../README.md) — project entry point; this
  suite is the project's verification layer.

### Uses
- [Config (folder)](../config/___config.md) — the tables and thresholds
  every golden and every guard test reads against (palette, constants,
  pantheon, defaults).
- [Core (folder)](../core/___core.md) — the pure astronomy/geometry engine
  the golden-value tests pin directly.
- [Data (folder)](../data/___data.md) — the repositories (seasons, moon
  phases, Database cities, Deep Time, encyclopedia, symbolism) tests read
  through, some against the real bundled files.
- [Render (folder)](../render/___render.md) — the compositor and layers
  the offscreen render/smoke tests exercise.
- [App (folder)](../app/___app.md) — the controller, dialogs, settings
  store and watch manager the GUI-level tests drive headlessly.
- [Skins (folder)](../skins/___skins.md) — the ring-preset/skin system
  `test_skins.py` validates.
- [Recolor (folder)](../recolor/___recolor.md) — the metal-transform
  kernel `test_recolor.py` pins and `test_purity.py` keeps Qt-free.
