# Pantheon

**Script:** [Pantheon (script)](../pantheon.py) · **Flow:** [diagram](../__flow/pantheon.md)

## Purpose

The weekday theme ENGINE — the resolvers, not the data.

Every `WEEKDAY_*` table this module used to declare moved to
[the registry](../registry/__about/__init__.md) on 2026-08-05 (owner decree
2026-08-01): one entry per theme, each table computed from it in ONE
assignment. The names are kept here because thirty-odd call sites read
them, and they resolve to the registry's own tables — there is no second
copy to keep in step, and the ~30 post-definition patches that made this
file the last `PATCHING_RATCHET` entry are gone with them. The ratchet is
empty.

Layer: config — pure, no Qt, no wall clock.

## Contents

- **"The PANTHEON roster"** — `WEEKDAY_PANTHEON` (per culture theme:
  candidate art paths per body, names, dual), `pantheon_seat(theme,
  body)` (the safety-law resolver: first EXISTING candidate wins with
  its pantheon identity, or `None` and the caller keeps the planetary
  bundle whole).
- **Every `WEEKDAY_*` table** — `WEEKDAY_THEME_NAMES` (display names
  per theme per body), `WEEKDAY_THEME_DIRS` (art folder per theme),
  `WEEKDAY_THEME_FILES` (derived file stems, with per-theme explicit
  overrides), `WEEKDAY_DUAL_NAMES`/`_FILES` (the Sunday second face),
  `WEEKDAY_SEAT_ROSTERS` (a seat that turns through SEVERAL different
  named figures — the Cyberpunk/Star Wars "roster seats"),
  `WEEKDAY_THEME_TITLES` (one menu/encyclopedia/settings title per
  theme), `WEEKDAY_MENU_TOP`/`WEEKDAY_MENU_GROUPS` (the Weekday
  submenu's structure).
- **`weekday_art(rel)`** — resolves a theme-relative art path
  (`"greek/primary/Helios.png"`) to its absolute, suffix-less location,
  routing the Inner-Wheel and Continents step-ups (`"../emblem/..."`,
  `"../earth/..."`) to their own relocated roots.
- **THE UNIVERSAL ROTATION CONVENTION** — `ROTATION_DAYS`,
  `_sourceless_core()`, `_rotation_candidates_in/()`, `_pick_rotation()`,
  `_pick_weekly_mandate()` (cp_corpo's ISO-week-parity cadence),
  `rotating_art_file(canonical_path, on_date)` — the ONE chokepoint
  every weekday consumer (and era badges, tetramorph figures, the
  Scale duality topic) calls through to pick a daily/weekly face from a
  version-sibling pool or a declared seat roster. Since 2026-08-08 a
  family whose MASTER file is absent but whose `_v2` siblings exist
  still resolves (both the version pool and each roster member's own
  family): an early master-existence guard once left ten Star Wars
  seats, shipped as `_v2`-only files, invisible to the dial and every
  picker while the whole suite stayed green.
- **`scale_variant_file(figure, on_date)`** — the Judas/Lucifer Scale
  badge's own rotation (needs the same rotation primitives, so it
  lives beside them rather than in `encyclopedia_ui.py`).
- **The title-plate cluster** — `colored_variant_rel(rel)`,
  `TITLE_PLATE_STEM`/`DUALITY_PLATE_STEM`, `DUALITY_GENERIC_ART`/
  `THIRTEENTH_GENERIC_ART` (the two shared generic plates, owner
  decree 2026-07-29), `THEME_OWN_DUALITY_PLATE`, `TITLE_PLATE_SEATS`,
  `theme_title_art(key, duality=False)`, `weekday_theme_body_art(theme,
  body, on_date=None, colored=False)` — the ONE weekday-body-plate
  chokepoint every render/hover/picker call site uses.

## Connections

### Uses
- [Config (folder)](../___config.md) — `constants`, `continents`,
  `paths`; `config.taxonomy` (local imports inside `weekday_art()` and
  `theme_title_art()`)

### Used by
- [Render (folder)](../../render/___render.md) — `layers.py` (weekday
  body/slot drawing, the era/tetramorph rotation), `compositor.py`
  (hover legend, duals, Ninth plates)
- [App (folder)](../../app/___app.md) — the Encyclopedia package, the
  Pointer/Slot Theme pickers, `controller.py`, `settings_store.py`
- [Config (folder)](../___config.md) — `defaults.py`'s `DEFAULT_SKIN`
  and `ECLIPSE_SOLAR_ART` read `weekday_art()` downhill

## Functions

- `pantheon_seat(theme, body)`: the pantheon bundle for one (theme,
  body) or `None`
- `weekday_art(rel)`: theme-relative path → absolute suffix-less path
- `rotating_art_file(canonical_path, on_date)`: one asset from a
  rotating family — a version-sibling pool by default, or a declared
  seat roster's own figures
- `scale_variant_file(figure, on_date)`: the Scale badge's own daily
  pick, in step across Judas and Lucifer
- `theme_title_art(key, duality=False)`: the plate for one theme-title
  or week-duality-title page
- `weekday_theme_body_art(theme, body, on_date=None, colored=False)`:
  one theme's plate for one weekday body, optionally rotated

## Design Decisions

- **The remnant's shrink was prioritized over this module's.**
  `config/defaults.py` losing its own god-file ratchet entry was
  Session 36's back-referenced deliverable; every coordinator that
  ONLY weekday/scale/era material actually calls (the rotation engine,
  the title-plate cluster) stayed with its biggest consumer here
  rather than fragmenting into the remnant to shave lines off an
  already-over-threshold file.
- **This module is allowed to import `continents.py` downhill** — that
  module is a deterministic fallback CARVED OUT of `pantheon.py`
  (Session 36), not one of the six DAG-peer modules, so the import is
  the split working as designed, not a DAG violation.
- **The value-identity proof, not a trust exercise.** All 351 public
  names that lived in the pre-split `config/defaults.py` were
  snapshotted from the original file and compared against their new
  homes in one process: 0 differences.

## THE ROTATION POOL CACHE (owner bug 2026-08-06)

`_rotation_candidates_in` is reached from every weekday body and every
seated slot on every tick, and it called `directory.iterdir()` once PER
STEM. Two changes: ONE walk per call instead of N, and `_ROTATION_CACHE`
keyed by (directory, stems).

**NON-EMPTY RESULTS ONLY** — an empty pool means "the art has not landed
yet", and remembering that would keep a freshly generated figure off the
dial until the next restart. Same rule and same reason as
[Paths](paths.md)' art cache; `reset_rotation_cache()` is cleared beside
it whenever new art lands.

Measured: 6 `iterdir()` calls per paint, per watch, down to zero.
