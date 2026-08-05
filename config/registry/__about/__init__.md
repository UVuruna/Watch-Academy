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
