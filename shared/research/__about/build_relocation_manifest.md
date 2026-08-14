# Build Relocation Manifest

**Script:** [Build Relocation Manifest (script)](../build_relocation_manifest.py) ·
**Flow:** [diagram](../__flow/build_relocation_manifest.md)

## Purpose

RESTRUCTURE Phase 1's deterministic relocation-map generator. Walks the real
`assets/` tree and computes, for every `.png`/`.svg`, its new home under the
one-hierarchy taxonomy sealed in `RESTRUCTURE.md` (2026-07-22). The rules
encoded here ARE the Folder Relocation Map, the Naming Convention (source
folder → filename suffix), the Theme Renames and the figure-first `alt/`
resolution.

**Historical / one-shot:** the RESTRUCTURE Phase 1 move already executed —
`assets/` matches the new tree today. Re-running this script now would report
almost zero moves; it is kept as the executable record of the rule set, and
as a reference for future asset-tree work.

## Usage

```bash
python research/build_relocation_manifest.py            # write the manifest
python research/build_relocation_manifest.py --emit-mv   # print a git mv list
```

Pure stdlib, no Qt, no project imports — safe to run standalone.

## Connections

### Uses
- The `assets/` tree on disk only — no project imports

### Used by
- Nobody at runtime. Its default-mode output is
  [Relocation Manifest](../relocation_manifest.md); its `--emit-mv` mode fed
  the one-shot `git mv` session that executed RESTRUCTURE Phase 1

## Functions

- `new_path(rel)` — the per-file relocation rule: dispatches on the asset's
  top-level root folder (`weekday`, `emblem`, `archetype`, `badge`,
  `eclipse`/`era`/`earth`, `zodiac`, `months`, `instrument` and the
  `hands`/`ring`/`icons`/`guide`/`subdial` merge-ins) and returns the new
  assets-relative path, or an `UNRESOLVED::` marker
- `_resolve_alt(rest, parent_dir, source)` — flattens a `.../alt/<name>.png`
  tail into a figure-first filename (via `ALT_FIGURE`, or a `_v2` suffix when
  the stem already exists in the parent — a version sibling)
- `main()` — walks every asset file, builds the (old, new) pairs, prints
  per-root before/after counts and a loss check, then either emits `git mv`
  lines or writes `research/relocation_manifest.md`

## Design Decisions

- **Explicit per-root dispatch tables** (`THEME_GROUP`, `THEME_RENAME`,
  `WOW_BLOCK`/`CP_BLOCK`/`SW_BLOCK`, `ALT_FIGURE`) — every oddball in the old
  tree is a named entry, never an inferred heuristic.
- **Loss check built in** — `main()` asserts total-files-in equals
  total-files-out (or reports UNRESOLVED explicitly) before anyone runs the
  real `git mv`.
