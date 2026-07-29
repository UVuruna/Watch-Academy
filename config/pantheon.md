# Pantheon

**Script:** [Pantheon (script)](pantheon.py)

## Purpose

The weekday THEME registry — who sits on which day, in which art. One
of six modules Session 36 (THE CONFIG SPLIT,
[Work Plan Structure](../WORKPLAN-STRUCTURE.md)) carved out of
`config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## ⚠ Over the god-file threshold — an open item

**This file is 1,549 lines, over Rule #20's ~1,000-line threshold, and
is NOT in `tests/test_structure_law.py`'s ratchet.**
`tests/test_structure_law.py::test_no_file_crosses_the_threshold_
outside_the_ratchet` and `tests/test_config_cohesion.py`'s own
threshold check both fail on it, honestly, on purpose — the ratchet
"requires the owner's explicit approval in that same session" (its own
words) and this session did not have it. Per root `CLAUDE.md` Rule #25
this is the session's one **CANNOT FIX HERE** item, not a false
"solved": either the owner grants a ratchet entry, or authorizes a
further split in a follow-up session (candidate boundary: the WEEKDAY
NAMES/DIRS/FILES/DUAL tables vs. the roster-and-rotation engine below
— see the arithmetic).

**Why the split map's own remedy fell short.** The map (WORKPLAN-
STRUCTURE.md) estimated pantheon.py at "~1,270" lines and named ONE
deterministic fallback if that proved insufficient: carve the
CONTINENTS family into `config/continents.py` (done — see that
module). Two things the map's estimate could not have priced in:

1. **The file had grown since the map was red-teamed.** Twelve new
   weekday casts (Sessions 31–33) each added a row to `WEEKDAY_THEME_
   NAMES`, `WEEKDAY_THEME_DIRS`/`_FILES` and `WEEKDAY_THEME_TITLES` —
   these tables alone, plus `WEEKDAY_PANTHEON`, `weekday_art()` and
   `WEEKDAY_MENU_TOP`/`_GROUPS` (the literal, non-negotiable "every
   WEEKDAY_* table" the map requires), already total **~1,091 lines**
   with NOTHING else in the file — over the threshold on their own,
   before a single helper function joins them.
2. **The rotation/roster engine cannot live anywhere else.**
   `WEEKDAY_SEAT_ROSTERS` (the map's own "roster/cast tables the waves
   added") needs `_seat_roster_of`, which `rotating_art_file()` calls;
   `weekday_theme_body_art()` (every weekday consumer's one chokepoint)
   needs `rotating_art_file()`; `scale_variant_file()` (the
   Encyclopedia's "Two Triangles" topic) needs the same rotation
   primitives. The fixed DAG forbids one new module importing another,
   so this whole cluster (~460 lines) either duplicates across modules
   (forbidden, Rule #5) or lives in ONE place with `WEEKDAY_SEAT_
   ROSTERS` — which can only be pantheon.py, since `WEEKDAY_SEAT_
   ROSTERS` IS weekday data.

The CONTINENTS fallback (~75 lines) was applied and is real — without
it pantheon.py would be ~1,625 lines instead of 1,549. It just was not
enough on its own once the rotation/roster engine's true size is
counted.

## What moved here

- **"The PANTHEON roster"** — `WEEKDAY_PANTHEON`, `pantheon_seat()`.
  (`WORKING_SET_CEILINGS` and `ARM_OUTLINE_WIDTH`, which sat inside
  this banner's span, are NOT pantheon material — an asset-downscaling
  ceiling table and a dial-arm line width respectively — and moved to
  `defaults.py`/`dial.py` instead.)
- **Every `WEEKDAY_*` table** — `WEEKDAY_THEME_NAMES`, `WEEKDAY_THEME_
  DIRS`, `WEEKDAY_THEME_FILES` (+ every per-theme subscript extension),
  `WEEKDAY_DUAL_NAMES`, `WEEKDAY_DUAL_FILES`, `WEEKDAY_SEAT_ROSTERS`,
  `WEEKDAY_THEME_TITLES`, `WEEKDAY_MENU_TOP`, `WEEKDAY_MENU_GROUPS`,
  plus their private helpers (`_ASCII_FOLD`, `_LOWERCASE_THEMES`,
  `_pascal_stem()`, `_SEAT_ROSTER_BY_PLATE`, `_seat_roster_of()`,
  `_roster_candidates()`).
- **`weekday_art()`** — the split map's explicit call-out ("it moves
  WITH them into pantheon.py").
- **The rotation engine** — `ROTATION_DAYS`, `_VERSION_SUFFIX`,
  `_sourceless_core()`, `_rotation_candidates_in()`, `_rotation_
  candidates()`, `_pick_rotation()`, `_pick_weekly_mandate()`,
  `rotating_art_file()` — THE UNIVERSAL ROTATION CONVENTION every
  weekday consumer (and era badges, tetramorph figures, the scale
  duality topic) calls through.
- **`SCALE_ART_DIR`/`scale_variant_file()`/`INSTRUMENT_ART_DIR`** — the
  Encyclopedia's "Two Triangles" duality-topic resolver; it needs the
  rotation primitives above, so it lives beside them rather than in
  `encyclopedia_ui.py`. `INSTRUMENT_ART_DIR` travels with it because
  `DUALITY_GENERIC_ART`/`THIRTEENTH_GENERIC_ART` (below) are built
  from it.
- **The title-plate cluster** — `colored_variant_rel()`, `TITLE_PLATE_
  STEM`, `DUALITY_PLATE_STEM`, `DUALITY_GENERIC_ART`, `THIRTEENTH_
  GENERIC_ART`, `THEME_OWN_DUALITY_PLATE`, `TITLE_PLATE_SEATS`,
  `theme_title_art()`, `weekday_theme_body_art()`. `THIRTEENTH_
  GENERIC_ART` stayed beside `DUALITY_GENERIC_ART` (its declared pair,
  "THE TWO GENERIC PLATES") rather than following the letter "any
  other 13th/mount table" to `calendar_mounts.py` — splitting the pair
  would have forced `INSTRUMENT_ART_DIR` into two places at once.

### Continents cross-reference

`WEEKDAY_THEME_FILES["continents"]`, `weekday_art()`'s `"../earth/..."`
branch and `WEEKDAY_DUAL_FILES`'s continents entry all need `continents.
py`'s own `EARTH_ART_DIR`/`CONTINENTS_REGIONS`/`CONTINENTS_PREVIEW_
STYLE`/`CONTINENTS_DUAL_REGION`. `continents.py` is the deterministic
fallback CARVED OUT OF this module (not one of the six DAG peers), so
`pantheon.py` importing it downhill is the fallback working as
designed, not a DAG violation.

## Connections

### Uses
- [Config (folder)](___config.md) — `constants`, `continents`, `paths`
- `config.taxonomy` (local imports inside `weekday_art()` and `theme_
  title_art()`, exactly as before the split)

### Used by
- [Render (folder)](../render/___render.md) — `layers.py` (weekday
  body/slot drawing, the era/tetramorph rotation), `compositor.py`
  (hover legend, duals, Ninth plates)
- [App (folder)](../app/___app.md) — the Encyclopedia package, the
  Pointer/Slot Theme pickers, `controller.py`, `settings_store.py`
- [Config (folder)](___config.md) — `defaults.py`'s `DEFAULT_SKIN` and
  `ECLIPSE_SOLAR_ART` read `weekday_art()` downhill

## Design Decisions

- **The remnant's shrink was prioritized over this module's.**
  `config/defaults.py` losing its ratchet entry is Session 36's named,
  back-referenced deliverable ("owed to YOU" in the ratchet's own
  words); pantheon.py needing an owner decision regardless of its
  exact size meant every coordinator that ONLY weekday/scale/era
  material actually calls (the rotation engine, the title-plate
  cluster) stayed with its biggest consumer here rather than
  fragmenting into the remnant to shave a few hundred lines off an
  already-over-threshold file.
- **The value-identity proof, not a trust exercise.** All 351 public
  names that lived in the pre-split `config/defaults.py` were
  snapshotted from the ORIGINAL file (recovered from git HEAD) and
  compared against their new homes in one process: 0 differences.
