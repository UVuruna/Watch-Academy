# Registry (derivation layer)

**Script:** [Registry (script)](../__init__.py) · **Flow:** [diagram](../__flow/__init__.md)

## Purpose

Turns [the week registry](week.md) into the tables every consumer
already reads — ONE assignment per table, no patching afterwards. This
is where the ~30 post-definition assignments THE CONFIG SECTION LAW
forbids went to die: each is now a field of its theme's entry.

Layer: config — pure.

## Contents

- **Vocabulary** — `BODIES`, `DAYS` (day → body), `BODY_DAY`.
- **Derived tables** — `THEMES`, `GROUP_OF`, `TITLES`, `DIRS`,
  `ARTICLES`, `BLURBS`, `METAL_THEMES`, `METALS`, `NAMES`, `FILES`,
  `DUAL_NAMES`, `DUAL_FILES`, `NINTHS`, `MECHANISMS`, `NINTH_ALTS`,
  `NINTH_EASTER_EGG`, `NINTH_NIGHT`, `SEAT_ROSTERS`, `PANTHEON`,
  `TITLE_PLATE_SEATS`.
- **`_earth_stems()`** — the one lazy reach out of the registry, for
  the Continents' COMPUTED stems; imported inside the function so the
  registry stays importable from anywhere in `config`.

## Every kind, one view

`themes_of(kind)`, `kinds_of(theme)`, `kind_of(theme)` and
`members_of(theme)` answer for all four kinds without a caller knowing
which module declares which. They are VIEWS, never copies — each reads
the owning table live, so the registry cannot disagree with the thing
it describes. The dozen, the cube and the wheels keep their data where
it has always been (owner ruling 2026-08-05): each is already a single
declarative table in its own section, and moving it would cost a reader
more than it buys.

**A key is scoped to its KIND, not to the program.** `virtues` and
`sins` are each both a week theme (the Inner Wheel's emblem families)
and a Dozen (the Virtue Wheel, the Sins Dozen) — different rosters that
share a word. `kinds_of` is the honest answer; `kind_of` is the
convenience for the many keys that are unique, and
`tests/test_registry.py` fails if a THIRD collision ever appears
unnamed.

## Notes

The two ALT Ninth tables (`NINTH_EASTER_EGG`, `NINTH_NIGHT`) are ONE
field in the registry, split here by the mechanism that governs it — a
sky trigger surfaces the easter egg, the daylight state swaps the night
face. `term_weekly` needs no alt table at all: its roster already names
both halves.

`tests/test_registry.py` pins every table here against the live
`constants`/`pantheon` values, so the two cannot drift while the
migration finishes.

## Connections

### Uses
- [Week Registry](week.md)
- `config.continents` — lazily, for the COMPUTED stems

### Used by
- [Constants](../../__about/constants.md), [Pantheon](../../__about/pantheon.md)
