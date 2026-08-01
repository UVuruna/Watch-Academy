# Constants — Flow

**About:** [description](../__about/constants.md)

This file is 1,863 lines of tables, not one algorithm — the tree below
shows every section's SHAPE and how many entries it carries, not a key
dump. Two dispatch-like corners get their own diagram further down.

## Section tree

```
📁 constants.py
  App identity              APP_NAME, ORGANIZATION, APP_USER_MODEL_ID
  Dial identity              HOURS_PER_REVOLUTION=24, DIAL_OFFSET_DEG=180,
                             SOLAR_NOON_SECS, SECONDS_PER_DEGREE
  Sun                        CIVIL_DEPRESSION, HORIZON/CIVIL_TWILIGHT elevations
  Year wheel                 YEAR_ANCHOR_ANGLES (6 unwrapped angles)
  Hidden mode                HIDDEN_MODE_SECRET
  Artwork sources            ART_SOURCES (gemini, chatgpt)
  Moon                       SYNODIC_MONTH_DAYS, MOON_PHASE_NAMES (8),
                             MOON_PHASE_FRACTIONS (4 principal)
  Deep Time era system
    ├─ ERA_NOTATIONS (2: bce_ce, bc_ad)
    ├─ ANNO_LUCIS_OFFSET=4079, AGE_OF_LIGHT window
    └─ THIRD_ERAS (10: none, auc, byzantine, hebrew, hegirae, chinese,
                    maya, kali, olympiad, unix)
         ├─ 5 are OFFSET eras   (THIRD_ERA_OFFSETS: auc/byzantine/hebrew/
         │                       chinese/kali — CE + N)
         ├─ 1 is LUNAR          (hegirae — AH ≈ (CE-622) x 33/32)
         └─ 3 are FORMATTERS,   maya (day count, no year), unix (epoch
             not offsets         seconds), olympiad (4-year cycle count)
  Geography                  LATITUDE/LONGITUDE_RANGE, city transliterations
  Weekday bodies              WEEKDAY_BODIES (7, Sunday-first mapping)
  Pointer variants
    ├─ POINTER_POINTS         hue/palette count per pointer (7 pointers)
    ├─ POINTER_DIAL_COUNTS    what the READER counts (can differ — Rose 8 vs 24)
    ├─ POINTER_PALETTE_LABELS the wheel-name table (per pointer, up to 3 wheels)
    ├─ POINTER_ARM_LABELS     per-pointer arm position names
    └─ THE POINTERS REWORK    POINTER_SHAPES, POLYGON_*, ROSE_STAR_OFFSETS,
                              ROSE_AURA_WEDGE_ANCHOR, ROSE_STAR_SETS
  The Umbra                  UMBRA_FORMS (3), UMBRA_CONTRAST_VARIANTS (4)
  Wheel slots                 PALETTE_STYLES (3), THIRD_WHEEL_POINTERS (4),
                              WHEEL_ARM_OFFSET_DEG, CUBE_LOOK_WHEELS
  The South Slot              OCTA_SLOT_MODES (8), WEEKDAY_SLOT_MODES (8),
                              SLOT_COMPLICATION_TITLES (4)
  Ring finishes                RING_FINISHES (4), RING_THEMATIC_SHADES (5),
                              METAL_SHADE_NAMES (per metal, incl. thematic's 21)
  Subdial                     SUBDIAL_SETS (5: set1-4, solo)
  Figure rosters               FIGURE_ROSTERS (2: planetary, pantheon)
  Ring layouts & letters      RING_LAYOUTS (3: flame/chalice/seal),
                              RING_LETTER_GROUPS (Latin/Greek/Numbers/Symbols)
  Weekday themes — MASTER LIST
    ├─ WEEKDAY_THEMES          ~38 registered theme keys
    ├─ METAL_THEMES            bronze-plate-capable subset
    ├─ WEEKDAY_THEME_BLURBS    theme -> symbolism.json blurb key
    └─ WEEKDAY_THEME_ARTICLES  theme -> symbolism.json article set
  The Ninth
    ├─ WEEKDAY_THEME_NINTHS       theme -> (name, plate) — ~30 themes
    ├─ WEEKDAY_THEME_NINTH_EASTER_EGG   {continents: Pangea}
    ├─ WEEKDAY_THEME_NINTH_NIGHT        {sw_dyad: Exegol}
    └─ THE DOUBLE NINTH LAW
         NINTH_MECHANISMS  {continents: easter_egg, sw_dyad: daynight,
                             cp_corpo: term_weekly}
  Chinese zodiac              CHINESE_ANIMALS (12), CHINESE_MONTH_BRANCH_ANIMALS (12)
  Tropical zodiac              ZODIAC_SIGNS (12, Cancer-first)
  THE BLUE MOON / AXLE LAW
    THIRTEENTHS (10 keys: 4 calendar-driven + 6 always-centers)
    AXLE_ALWAYS_CENTERS (6: hestia, jesus, prudence, cunning, peace,
                          hardness_of_heart)
  Event glow windows           SEASON/MOON/ECLIPSE_GLOW_WINDOW_H
  Season event names            SEASON_EVENT_NAMES x 3 hemispheres
  Translation languages         TRANSLATION_LANGUAGES (~70 codes)
  UI slider ranges              ENCYCLOPEDIA_ZOOM_RANGE, ELEMENT_SCALE_RANGE,
                              POINTER/RING_SATURATION_RANGE
  Weekday slot seating
    ├─ POINTER_WEEKDAY_SLOTS   per-pointer (angle, occupant bodies) layout
    ├─ SOUTH_SLOT_ANGLE = 180, SERVANT_SEAT_ANGLE = {rose: 270}
    └─ AURORA_DUAL_WEEKDAY_ANGLE / _SLOT_ANGLE
  THE DUALITY-AXES CONFIG
    DUALITY_RULER_ON_COLD_POLE = {religion}
    CENTER_DUALITY_WHEELS = {(cross, tertiary)}
    HORIZONTAL_DUALITY_WHEELS = {(octa, tertiary)}
    DUALITY_SERVANT_ON_TOP = {continents}
```

## THE DOUBLE NINTH LAW's dispatch

```mermaid
flowchart TB
    A[theme has a double Ninth?] --> B{NINTH_MECHANISMS.get(theme)}
    B -- "easter_egg" --> C["core.continents.pangea_over_zealandia(date)\n— eclipse / turning point / principal moon phase?"]
    C -- yes --> D[show the ALT face\ne.g. Pangea]
    C -- no --> E[show the CANONICAL face\ne.g. Zealandia]
    B -- "daynight" --> F{TickState.is_daylight?}
    F -- yes --> G[canonical face — day]
    F -- no --> H["WEEKDAY_THEME_NIGHT face — night\ne.g. Exegol"]
    B -- "term_weekly" --> I["date.isocalendar().week parity"]
    I -- even --> J[canonical roster half\ne.g. Arasaka]
    I -- odd --> K[alternate roster half\ne.g. NUSA]
    B -- absent --> L[single canonical WEEKDAY_THEME_NINTHS\nentry, no alternation]
```

A theme absent from `NINTH_MECHANISMS` has no double Ninth at all — the
plain single entry in `WEEKDAY_THEME_NINTHS` is the only face it ever
shows. `tests/test_ninth_mechanisms.py` fails the build if a double
Ninth found in ANY registry lacks an entry here, or if an entry names
anything outside `NINTH_MECHANISM_KINDS`.

## Third-era year formatting dispatch

```mermaid
flowchart TB
    A["format_year_line(astro_year, third_era)"] --> B{third_era in\nTHIRD_ERA_OFFSETS?}
    B -- yes, e.g. auc/byzantine/hebrew/chinese/kali --> C["display = astro_year + OFFSET\n'{display}. {LABEL}'"]
    B -- no --> D{third_era == "hegirae"?}
    D -- yes --> E["AH ~= (CE - 622) x 33/32\n(lunar approximation)"]
    D -- no --> F{third_era == "maya"?}
    F -- yes --> G["core.deep_time.maya_long_count(date)\nvia Julian Day Number, epoch MAYA_EPOCH_JDN\n(a day count, no year at all)"]
    F -- no --> H{third_era == "olympiad"?}
    H -- yes --> I["4-year cycle count FROM OLYMPIAD_EPOCH_YEAR\n(-775 = 776 BCE)"]
    H -- no --> J{third_era == "unix"?}
    J -- yes --> K["seconds since 1970-01-01 00:00 UTC\nat this date's own midnight UTC"]
```

Every offset era shares ONE formula (`astro_year + THIRD_ERA_OFFSETS
[era]`); the three FORMATTER eras (`maya`/`olympiad`/`unix`) each need
their own branch in `core.deep_time.format_year_line` because they are
not offsets at all — this table only supplies the constants each
branch reads (`MAYA_EPOCH_JDN`, `OLYMPIAD_EPOCH_YEAR`), never the
branching logic itself (which lives in `core/`, outside this pure
config layer).
