# Constants

**Script:** [Constants (script)](../constants.py) · **Flow:** [diagram](../__flow/constants.md)

## Purpose

Product-defining invariants — values that define what DOMY Watch IS
and never change at runtime, never user-tunable. The largest file in
`config/` (1,863 lines) and, unlike [Defaults](defaults.md)/
[Pantheon](pantheon.md), NOT a Session 36 split target: everything here
predates and postdates that split as one continuous body of canon
tables, dial-identity constants and enumeration sources.

Developer TUNABLES (things a session might reasonably adjust) live in
[Defaults](defaults.md); Win32 API literals live in
[Win32 API Literals](winapi.md).

Layer: config — pure, no Qt, no wall clock.

## Contents (by topic — see the flow doc for the full section tree)

- **App identity** — `APP_NAME`, `ORGANIZATION`, `SINGLE_INSTANCE_
  MUTEX`, `APP_USER_MODEL_ID`.
- **Dial identity** — the 24h clockwise convention (`HOURS_PER_
  REVOLUTION`, `DIAL_TOP_HOUR`, `DIAL_OFFSET_DEG` = 180°,
  `SOLAR_NOON_SECS`, `SECONDS_PER_DEGREE`), `HAND_HUB_OFFSET_UNITS`.
- **Sun / Moon geometry** — `CIVIL_DEPRESSION`, horizon/twilight
  elevations; `SYNODIC_MONTH_DAYS`, `MOON_PHASE_NAMES` (the eight
  octant names), `MOON_PHASE_FRACTIONS`.
- **Year wheel** — `YEAR_ANCHOR_ANGLES` (the six season-anchor
  unwrapped angles).
- **Artwork sources** — `ART_SOURCES` (`gemini`/`chatgpt`),
  `ART_SOURCE_DEFAULT`, `ART_SOURCE_TITLES`.
- **Deep Time era system** — `DEEP_TIME_DB_FILENAME`, `ERA_NOTATIONS`/
  `_TITLES`/`_NAMES`, `ANNO_LUCIS_OFFSET`/`_LABEL`, `AGE_OF_LIGHT_
  START/END_YEAR`, the whole THIRD ERA family (`THIRD_ERAS`, `_TITLES`,
  `_OFFSETS`, `_LABELS`, `_NOTES` — ten calendars: none, AUC, Byzantine,
  Hebrew, Hegirae, Chinese/Huangdi, Maya, Kali Yuga, Olympiad, Unix),
  `MAYA_EPOCH_JDN`, `OLYMPIAD_EPOCH_YEAR`, `GREGORIAN_CYCLE_YEARS`,
  `PROXY_WINDOW_FIRST`.
- **Geography** — `LATITUDE_RANGE`/`LONGITUDE_RANGE`,
  `CITY_NAME_TRANSLITERATIONS`.
- **Weekday bodies** — `WEEKDAY_BODIES` (Monday→moon … Sunday→sun),
  `WEEKDAY_LABELS`, `WEEKDAY_FULL_NAMES`.
- **Pointer variants** — `POINTER_POINTS` (the palette/hue count per
  pointer), `POINTER_DIAL_COUNTS` (what the READER counts, not always
  the same number), `POINTER_DISPLAY_NAMES`, `POINTER_PALETTE_LABELS`
  (the wheel-name table every wheel-naming UI reads), `POINTER_ARM_
  LABELS`, `POINTER_ARM_HALF_ANGLE_DEG`, THE POINTERS REWORK
  (`POINTER_SHAPES`, `POLYGON_POINTERS`, `POLYGON_CURVATURE_*`,
  `POLYGON_EDGE_MODES`, `CALENDAR_STAR_ARMS`), the Rose's own tables
  (`ROSE_STAR_OFFSETS`, `AURA_WEDGE_ANCHOR_DEFAULT`, `ROSE_AURA_WEDGE_
  ANCHOR`, `ROSE_STAR_SETS`, `ROSE_ARM_SYSTEMS`), `DAYLIGHT_SWITCH_
  POINTERS`, `TRIO_ARM_THEMES`, `GENESIS_ARM_OFFICES`.
- **The Umbra** — `UMBRA_FORMS`, `UMBRA_SECTION_COUNTS`, `UMBRA_
  CONTRAST_VARIANTS`.
- **Wheel slots** — `PALETTE_STYLES`, `THIRD_WHEEL_POINTERS`,
  `palette_styles_for(pointer)`, `GENESIS_ARM_OFFSET_DEG`, `SEASONS_
  ARM_OFFSET_DEG`, `WHEEL_ARM_OFFSET_DEG`, `CUBE_LOOK_WHEELS`.
- **The South Slot** — `OCTA_SLOT_MODES`, `WEEKDAY_SLOT_MODES`,
  `SLOT_COMPLICATION_TITLES`, the fixed seat angles, `ZODIAC_SLOT_
  STYLES`/`CHINESE_SLOT_STYLES`/`SLOT_STYLE_VALUES`, the style→art-dir
  tables, `EARTH_STYLES`.
- **Ring finishes** — `RING_FINISHES` (gold/silver/bronze/thematic),
  `RING_THEMATIC_SHADES` (per-preset theme colour), `METAL_SHADE_
  NAMES`/`_DEFAULT`/`_TITLES` (the enumeration/validation surface —
  the numeric recipe lives in [Defaults](defaults.md)).
- **Subdial** — `SUBDIAL_STYLES`, `SUBDIAL_SETS`/`_DEFAULT`/`_TITLES`.
- **Figure rosters** — `FIGURE_ROSTERS` (`planetary`/`pantheon`).
- **Ring layouts and letters** — `RING_LAYOUTS` (flame/chalice/seal),
  `RING_TWO_METALS_DEFAULT`, THE EYE AT THE APEX (`RING_EYE_GLYPH`/
  `_SHINE_FILE`/`_SHINE_DEFAULT`/`_SHINE_ENLARGE`), `RING_LETTER_
  GROUPS`/`_FILES` (the full Latin/Greek/Numbers/Symbols letter
  library).
- **Weekday themes — the master list** — `WEEKDAY_THEMES` (every
  registered dial theme key, ~38 entries), `METAL_THEMES`, `THEME_
  METALS`, `THEME_METALS_OVERRIDE`/`theme_metals()`, `WEEKDAY_THEME_
  BLURBS`, `WEEKDAY_THEME_ARTICLES`.
- **The Ninth** — `WEEKDAY_THEME_NINTHS` (display name + plate per
  theme with a Ninth), `WEEKDAY_THEME_NINTH_EASTER_EGG` (Pangea),
  `WEEKDAY_THEME_NINTH_NIGHT` (Exegol) — and THE DOUBLE NINTH LAW's own
  dispatch registry, `NINTH_MECHANISMS`/`NINTH_MECHANISM_KINDS`
  (`easter_egg`/`daynight`/`term_weekly`), `CENTER_WINDOW_HOURS`.
- **Chinese zodiac** — `CHINESE_ANIMALS`, `CHINESE_ELEMENTS`,
  `CHINESE_NEW_YEAR_WINDOW`, `CHINA_UTC_OFFSET_HOURS`, `CHINESE_MONTH_
  BRANCH_ANIMALS` (the static 12-wedge mount's own animal-per-Gregorian-
  month table, distinct from the live lunar-month zodiac).
- **Tropical zodiac** — `ZODIAC_SIGNS`, `ZODIAC_SPAN_DEG`.
- **THE BLUE MOON LAW / THE AXLE LAW** — `THIRTEENTHS` (the 13th member
  of every 12-set, calendar-driven and always-present alike),
  `AXLE_ALWAYS_CENTERS`, `OPHIUCHUS_WINDOW`/`SOL_WINDOW`/`MODRENIK_
  WINDOW_HALF_DAYS`.
- **Event glow windows** — `SEASON_GLOW_WINDOW_H`, `MOON_GLOW_
  WINDOW_H`, `ECLIPSE_GLOW_WINDOW_H`, `ECLIPSE_SOLAR_VISIBILITY_KM`,
  `EARTH_RADIUS_KM`.
- **Season event names** — `SEASON_EVENT_NAMES`, `ZONE_SEASON_EVENT_
  NAMES` (north/south/tropics readings of the same four angles).
- **Translation languages** — `TRANSLATION_ORIGINALS`, `TRANSLATION_
  LANGUAGES` (the ~70 Google-translate codes offered in Settings).
- **UI sliders' fixed ranges** — `ENCYCLOPEDIA_ZOOM_RANGE`/`_STEP`,
  `ELEMENT_SCALE_RANGE`, `HOVER_ENLARGE_RANGE`, `POINTER_SATURATION_
  RANGE`/`_STEP`, `RING_SATURATION_RANGE`/`_STEP`.
- **Tropics** — `TROPIC_LATITUDE_DEG`, `TROPICAL_YEAR_DAYS`.
- **Weekday slot seating** — `SUNDAY_FIRST_INDEX`, `POINTER_WEEKDAY_
  SLOTS` (every pointer's own arm→body-set layout), `SOUTH_SLOT_
  ANGLE`, `SERVANT_SEAT_ANGLE`, `AURORA_DUAL_WEEKDAY_ANGLE`/`_SLOT_
  ANGLE`.
- **THE DUALITY-AXES CONFIG** — `DUALITY_RULER_ON_COLD_POLE`,
  `CENTER_DUALITY_WHEELS`, `HORIZONTAL_DUALITY_WHEELS`, `DUALITY_
  SERVANT_ON_TOP` (the per-theme/per-wheel exceptions to the standard
  Sunday duality seating).

## Connections

### Uses
- Nothing inside `config/` — `constants.py` sits at the BASE of the
  import DAG alongside `paths.py` and `palette.py`; every other config
  module may import it, it imports none of its siblings.
  (Its own docstring lists `calendar_mounts, continents, palette,
  pantheon` in a comment — those are the DOWNSTREAM modules that
  import `constants`, not imports this file performs; see Known doc
  drift below.)

### Used by
- Effectively every module in the project — [Config (folder)](../___config.md)
  siblings (`defaults.py`, `dial.py`, `palette.py`, `pantheon.py`,
  `calendar_mounts.py`, `paths.py`, `archetypes.py`, `encyclopedia_
  ui.py`), `core/` (pure astronomy/geometry consumers of the dial
  identity and zodiac/Chinese tables), [Render (folder)](../../render/___render.md),
  [App (folder)](../../app/___app.md)

## Functions

- `palette_styles_for(pointer)`: the wheel slots this pointer actually
  serves — `("primary", "secondary")` everywhere, plus `"tertiary"` on
  `THIRD_WHEEL_POINTERS`
- `theme_metals(theme)`: the metal looks a theme may wear —
  `THEME_METALS` unless `THEME_METALS_OVERRIDE` names an exception

## Design Decisions

- **One table per decision, never a branch at the call site.** Every
  "if theme is X, do Y" the render/app layers might otherwise hardcode
  is instead a dict here (`NINTH_MECHANISMS`, `DUALITY_RULER_ON_COLD_
  POLE`, `WHEEL_ARM_OFFSET_DEG`) — adding a new theme/wheel is a table
  row, never a new `if`.
- **The vocabulary a dispatch implements is named beside the dispatch
  data.** `NINTH_MECHANISM_KINDS` is a frozenset the render layer's own
  dispatch is checked against by a dedicated test
  (`test_ninth_mechanisms.py`) — a registry entry naming an
  unimplemented mechanism fails the build rather than silently no-op'ing
  at runtime.
- **Enumeration/validation lives here; numeric recipes live in
  [Defaults](defaults.md).** `METAL_SHADE_NAMES` (here) is the set of
  legal Settings choices; what a shade actually RESOLVES to
  (`METAL_SHADES`, in `defaults.py`) depends on `recolor/presets/
  metals.json` and belongs beside that dependency instead.

## Known doc drift

The module's own docstring (top of `constants.py`) reads:

```
from config import calendar_mounts, continents, palette, pantheon
```

This line is NOT a real import statement inside the module (it sits
inside the triple-quoted docstring, before any executable code) and it
is backwards: `constants.py` imports nothing from `config` — those four
modules import `constants`, not the other way around, exactly as the
Design Decisions above and the import DAG in
[Defaults' flow](../__flow/defaults.md) describe. This migration flags
the stale line as a doc lie in the source rather than editing the `.py`
file (docs-only migration).
