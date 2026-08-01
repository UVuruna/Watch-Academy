# Migrate Tree Law

**Script:** [Migrate Tree Law (script)](../migrate_tree_law.py) ·
**Flow:** [diagram](../__flow/migrate_tree_law.md)

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

**Historical / one-shot:** the 2026-07-26 tree-law migration already
executed; `assets/` matches the law today. Kept as the executable record of
the rule set.

## Modes

- **Dry run (default)** — prints the full move plan, every collision, and
  per-category before/after counts; touches nothing.
- **`--execute`** — performs the plan with `git mv`, creating directories as
  needed; a collision ABORTS the run before any move (all-or-nothing); a
  final recount confirms the plan.

## Companion

[Rewrite Look Paths](rewrite_look_paths.md) is the TEXT side of the same
migration: it derives the exact directory map from the executed migration
commit's own rename records (`git show -M --name-status`) and rewrites every
literal `assets/...` path in the prompt sheets, COVERAGE and the sheet-path
lint whitelist — exact by construction. Its one blind spot, found and fixed
the same day: a SOURCE dir that fans out to MANY destinations (the
`assets/titles/` distribution) collapses to one map entry; the titles were
re-repaired from the commit's FILE-level records instead.

## Connections

### Uses
- `git` (`git mv` — every move is a rename in history)
- The PLAN tables at the top of the script — the single place the law's
  application to the existing zoo is written down

### Used by
- One-shot migration sessions (2026-07-26 wave); kept afterwards as the
  executable record of WHAT moved WHERE

## Design Decisions

- **Explicit PLAN over clever walker** — every oddball (zodiac's four look
  folders, planets' signs/art, bible's three registers) is a named table row
  the owner can audit, not an if-branch surprise.
- **Dry-run first, always** — the law forbids losing a single file; the dry
  run proves the before/after counts match before git touches anything.
- **`git mv`, never copy+delete** — blame and history survive the migration.
