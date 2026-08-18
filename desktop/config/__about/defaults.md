# Defaults

**Script:** [Defaults (script)](../defaults.py) · **Flow:** [diagram](../__flow/defaults.md)

## Purpose

Developer tunables — everything read-only at runtime that does not fit
any ONE of the six single-responsibility modules Session 36 (THE
CONFIG SPLIT, [Work Plan Structure](../../../docs/archive/WORKPLAN-STRUCTURE.md))
carved out of this file (`dial.py`, `shortcuts.py`, `pantheon.py`,
`calendar_mounts.py`, `encyclopedia_ui.py`, `glow.py`, plus
`continents.py`, the pantheon fallback) — landed at 812 lines from
~3,700 before the split.

What stays here are two kinds of thing: values that fit no single new
module's charter, and COORDINATOR values/functions that legitimately
need more than one new module's data
(`dial_window_margin_fraction` combines `dial.py`'s ring/jewel/crown-text
geometry with `glow.py`'s own glow extent; `ECLIPSE_SOLAR_ART` needs
`pantheon.py`'s `weekday_art`). The fixed import DAG lets a new module
import only stdlib + `config.{paths, constants, palette}`, never each
other and never this file — so a value two new modules both need
either duplicates (forbidden, Rule #5) or stays here, and this remnant
alone may import every new module downhill.

Layer: config — pure, no Qt, no wall clock.

## Contents

- **`ECLIPSE_SOLAR_ART`** (owner correction 2026-08-11 — "nemoj da
  koristis eklipsu koju predstavlja nedelja... slike sa kojima
  predstavljamo eklipsu su one koje smo mi pravili"): the marker art at
  a solar eclipse is now `assets/instrument/icons/sun_eclipse.png`, the
  owner's OWN icon, a plain path literal — never the Planets theme's
  Eclipsed-Sun weekday dual, which belongs to the Sunday mechanic
  alone. No longer a cross-DAG remnant needing `pantheon.weekday_art`
  for this name; `pantheon` stays imported here regardless, for the
  `DEFAULT_SKIN.weekday_set.bodies`/`moon_asset` tables further down,
  which do still call `pantheon.weekday_art`.
- **`ECLIPSE_BODY_SUN_ART` / `ECLIPSE_BODY_MOON_ART`** (owner art
  2026-08-13): the two plates the `bite` style composites — his rayed
  yellow Sun and the black Moon that crosses it. `ECLIPSE_SOLAR_ART`
  above is one finished PICTURE of an eclipse; these two are its
  INGREDIENTS, and that distinction is the whole point: overlap them
  fully for totality, shrink the dark one for the ring of fire, offset
  it for a partial, and one pair of files draws every solar eclipse
  there is (COMPUTE, DON'T GENERATE, in his own art). The disc radii
  they are composited by are MEASURED off the files in
  `render.marker_marks` — see [Marker Marks](../../render/__about/marker_marks.md).
  He named them `eclipse_light`/`eclipse_dark` and renamed them himself.
  The `.svg` twins beside them are his working files and nothing reads
  them: Qt's SVG Tiny 1.2 drops the mask his Moon is built on, and his
  own exporter mangles them, which is why he redrew both as PNG.
- **Cross-DAG remnants** — `ECLIPSE_LUNAR_TYPE_ICON`/
  `eclipse_lunar_type_icon()`/`ECLIPSE_SOLAR_TYPE_ICON_SOURCE` (need
  `ICON_DIR`, defined here).
- **Location** — `DEFAULT_CITY` (Belgrade, until the picker arrives).
- **Tick scheduling** — `TICK_EPSILON_MS`, `CLOCK_JUMP_THRESHOLD_S`,
  `CLICK_THROUGH_HOVER_POLL_MS`, `HOVER_BYPASS_MODIFIER`.
- **Settings persistence** — `SETTINGS_SCHEMA_VERSION`, `SETTINGS_
  WRITE_DEBOUNCE_MS`.
- **Tray/app presentation** — `TRAY_ICON_SIZE`, `LOGO_ASSET`, `LOGO_
  SETUP_ASSET`, `WINDOW_ICON_SIZES_PX`.
- **UI icon chrome** — `ICON_DIR`, `ICON_FILES`, `icon_path(name)` (the
  shared graceful-absent resolver every UI-glyph consumer calls),
  `SETTINGS_NAV_WIDTH_PX`. The Fast Travel picker's solar-eclipse row
  names NO file here: it holds a COMPUTED glyph
  (`render.asset_variants.eclipse_sun_icon_file`) after the owner's
  correction and verdict of 2026-08-12. Both candidates from this table
  failed the same way at menu size — `sun_eclipse.png` reads as the Moon
  row beside it, and `eclipse_sun.svg`'s many rays are hairlines that die
  below one pixel. `eclipse_sun` stays here for its ORIGINAL consumer,
  Quick Jump's own eclipse rows, and `ECLIPSE_SOLAR_ART` still gives the
  DIAL his art — a different spot at a different size, which is exactly
  what this table's one-file-many-spots rule is for.
- **Working-set ceilings** — `WORKING_SET_CEILINGS` (per-asset-subtree
  downscale ceilings), `REVEAL_WEEK_DURATION_S`.
- **Background warm pool sizes** — `ART_DRAIN_WORKERS`,
  `WORKING_SET_WORKERS` (owner bar 2026-08-09, MIGRATE-GUI Phase 1:
  `max(2, min((os.cpu_count() or 4) - 2, 12))` — DERIVED, not the old
  hardcoded `2` that pinned the cold working-set build to two cores no
  matter the machine; floor matches the old constant, ceiling mirrors
  `ART_DRAIN_WORKERS`'s own cap), `ART_REPAINT_DEBOUNCE_MS`.
- **Time Travel Quick Jumps** — `QUICK_JUMP_POLE_LATITUDE`,
  `GREENWICH_*`, `TIME_TRAVEL_ROW_ICON_PX`/`_ARROW_BUTTON_PX`.
- **Subdial recolor recipe** — `SUBDIAL_RECOLOR_VALUE_RAMP`/`_SAT_
  CUTOFF`/`_RIM_RADIUS`/`_VERSION`/`_FIELD_GAIN` (the numeric SHAPING
  of a recolor — not a colour, [Palette](palette.md)'s own documented
  boundary).
- **Report** — `REPORT_REFRESH_MS`, `REPORT_BAR_TOP_N`, `REPORT_CHART_
  HEIGHT_PX`.
- **The Observatory** — `OBSERVATORY_BUNDLE_*` (bundled JSON
  filenames), chart geometry, zoom/tick-ladder tunables (`OBSERVATORY_
  ZOOM_*`, `OBSERVATORY_TARGET_X_TICKS`/`_Y_TICKS`), the Enlarge dialog
  geometry, `OBSERVATORY_ECLIPSE_KIND_INFO` (one legend sentence per
  eclipse kind).
- **The Guide** — `GUIDE_DIR`, `GUIDE_INITIAL_IMAGE_PX`, text sizing.
- **Dialog opening sizes** — `DIALOG_A4_*` (Encyclopedia/Observatory),
  `DIALOG_SQUARE_HEIGHT_FRACTION` (Settings/Guide).
- **Translation** — `TRANSLATE_ENDPOINT`, `TRANSLATE_TIMEOUT_S`.
- **The transparent window margin** — `DIAL_WINDOW_MARGIN_EPSILON`,
  `dial_window_margin_fraction(skin)` (the coordinator function).
- **Shared art content roots** — `ZODIAC_ART_DIR`, `EMBLEM_ART_DIRS`,
  `TRINITY_ART_DIR`, `SEASON_ART_DIR`, `ERA_ART_DIR`, `MONTHS_ART_DIR`,
  `HOVER_BADGE_WIDTH_PX`.
- **THE METAL SHADES** (the ramp mapping, not the recipe) —
  `METAL_SHADES` (shade name → `recolor/presets/metals.json` ramp
  name), `METAL_SOURCE_BADGE`/`_LETTER`, `METAL_MASK_BADGE`/`_LETTER`,
  `METAL_SWAP_VERSION`, `METAL_SWAP_TARGETS`.
- **`DEFAULT_SKIN`** — the ONE typed `SkinDefinition` the compositor
  consumes (z-order, background, star, ring, weekday_set, year_marker,
  hands) — the controller overlays the ring preset and the user's
  display choices onto it at build time.
- **Pole light/dark emoji windows** — `POLE_LIGHT_WINDOW`, `POLE_
  LIGHT_EMOJI`/`_DARK_EMOJI`/`_COLD_EMOJI`, `GREENWICH_EMOJI`,
  `pole_is_light()`, `pole_emoji()`, `pole_icon_name()`.

## Connections

### Uses
- [Config (folder)](../___config.md) — `calendar_mounts`, `constants`,
  `continents`, `dial`, `encyclopedia_ui`, `glow`, `palette`,
  `pantheon`, `paths` (every DAG-peer module downhill, plus the base
  three)
- `skins.manifest` — `BackgroundSpec`, `HandSpec`, `HandsSpec`,
  `RingSpec`, `SkinDefinition`, `StarSpec`, `WeekdaySpec`,
  `YearMarkerSpec` — the typed shapes `DEFAULT_SKIN` is built from

### Used by
- [Config (folder)](../___config.md) — every DAG-peer module keeps
  this file OUT of its own imports (the fixed DAG's whole point); only
  this remnant imports them
- [App (folder)](../../app/___app.md) — `controller.build_skin`
  overlays onto `DEFAULT_SKIN`, `apply_display_settings`,
  `settings_store`
- [Render (folder)](../../render/___render.md) — every layer/compositor
  path that reads a tunable not owned by a DAG-peer module

## Functions

- `icon_path(name)`: the UI icon file for `name`, or `None` when it
  has not landed on disk yet (graceful-absent, Rule #1)
- `eclipse_lunar_type_icon(type_)`: the small lunar eclipse type icon,
  or `None` for an unknown type or a missing file
- `dial_window_margin_fraction(skin)`: the per-side transparent window
  margin (fraction of the dial diameter) for the CURRENT skin —
  recomputed on every skin install so a size/hover/jewel slider
  re-sizes the window to fit exactly. `max()`s four graceful-absent
  extent terms: the event glow, the ring jewels, a preset's static
  `crown_text` arc, and — Crown Polish round, owner correction
  2026-08-06 — the LIVE crown's own reach for every preset
  `dial.RING_LIVE_CROWN` names (The One, Templar): neither carries a
  `crown_text` card entry, so this fourth term used to stay 0.0 and the
  window clipped the live glyphs at default size. ONE CROWN SIZE LAW
  (owner defect 2026-08-07): both crown terms now read
  `RING_CROWN_TEXT_SIZE * crown_text_scale` — the live term used to be
  sized off the hour band, and the static term used to multiply
  `ring_jewels_scale` as well (THE DECOUPLED SCALES). Both sliders
  default to 1.0, so the folded constant is 1.0 and no default window
  changed size; The One now reserves exactly what the Dollar does,
  because its live crown genuinely reaches as far
- `pole_is_light(pole, on_date)`, `pole_emoji(pole, on_date)`,
  `pole_icon_name(pole, on_date)`: the season-dependent light/dark
  glyph for one pole's Quick Jump row, from a plain calendar-date
  window (no astronomy call)

## Design Decisions
- **A number two windows both compute with is ONE number here** (R7 of
  the OOP audit, 2026-08-18). `SETTINGS_NAV_CHROME_PX` is what a nav
  LIST spends around its widest title, and both the Settings dialog and
  the Watch Face window measure `max(NAV_WIDTH, longest + CHROME)` with
  it — they each carried their own `+ 48` before, which is two places to
  change and one to forget. `SETTINGS_NAV_ITEM_CHROME_PX` is the same
  story for one nav ITEM's own padding.

- **A cross-referencing name follows its dependency, or stays here.**
  Every value that turned out to need TWO new modules' data (or one
  new module plus something only this remnant holds, like `ICON_DIR`)
  stays in the remnant rather than forcing a DAG cycle.
- **`METAL_SHADES` here, `METAL_SHADE_NAMES` in [Constants](constants.md).**
  The split follows the same rule as `SUBDIAL_SETS` (names, in
  constants) vs `SUBDIAL_RECOLOR_COLORS` (recipe, in defaults) — the
  validation/enumeration surface lives in `constants.py` (nothing else
  depends on it), the numeric recipe lives here because it depends on
  nothing else either but is not a product invariant.
- **The move was proven value-identical.** The pre-split `defaults.py`
  was recovered from git HEAD and imported under a private module
  name; all 351 of its public names (values, functions, classes) were
  compared against their new homes in one process — 0 differences.
