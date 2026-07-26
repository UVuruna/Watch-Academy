# Migrate Tree Law

**Script:** [Migrate Tree Law (script)](migrate_tree_law.py)

## Purpose

The one-shot executor of the owner-approved TREE LAW (2026-07-26):

```
assets/<category>/<group>/<theme>/<register>/<look>/<Figure>[_vN]_<src>.png
```

It moves the existing figure trees (`weeks/`, `calendars/`, `archetypes/`)
onto the law with `git mv` (history preserved), from an explicit,
auditable PLAN — never a guessed heuristic:

- theme-level `colored/` folders descend INTO their register
  (`egypt/colored/` → `egypt/primary/colored/` — the owner's own
  complaint: "COLORED unutar PANTHEON važi i za primary");
- loose files in a register folder descend into their LOOK subfolder
  (`bronze/` for cameo-master sets that have a colored twin or metal
  cycle, `colored/` for as-drawn full-color sets);
- the `assets/titles/` drop distributes as reserved `Title` stems into
  each theme's own register/look (law rule 6);
- oddball trees (zodiac looks, planets signs/art, bible registers) are
  named case-by-case in the PLAN table, visible and reviewable.

## Modes

Pseudocode (Rule #21):

```
DRY RUN (default):
    walk the PLAN → print every planned move, every collision,
    per-category counts (files before = files after, byte-for-byte)
    NOTHING is touched
EXECUTE (--execute):
    same walk → git mv each file, mkdir as needed
    collisions ABORT the run before any move (all-or-nothing per rule)
    final inventory: recount and compare against the dry-run plan
```

## Connections

### Uses
- git (`git mv` — every move is a rename in history)
- The PLAN tables at the top of the script — the single place the
  law's application to the existing zoo is written down

### Used by
- One-shot migration sessions (2026-07-26 wave); kept afterwards as
  the executable record of WHAT moved WHERE

## Design Decisions

- **Explicit PLAN over clever walker** — every oddball (zodiac's four
  look folders, planets' signs/art, bible's three registers) is a
  named table row the owner can audit, not an if-branch surprise.
- **Dry-run first, always** — the law forbids losing a single file;
  the dry run proves the before/after counts match before git touches
  anything.
- **`git mv`, never copy+delete** — blame and history survive the
  migration.
