# Rewrite Sheet Paths

**Script:** [Rewrite Sheet Paths (script)](../rewrite_sheet_paths.py) ·
**Flow:** [diagram](../__flow/rewrite_sheet_paths.md)

## Purpose

RESTRUCTURE Phase 2 — rewrites every prompt-sheet drop path to the new
one-hierarchy tree, sourceless (PromptPainter injects the `_gem`/`_gpt`
source suffix at generation time — Phase 4). Same relocation rules as
[Build Relocation Manifest](build_relocation_manifest.md), minus the
source-folder collapse (sheets are already sourceless) and minus the
filename suffix. Walks every `research/prompts/**.md`, transforms each
backticked `assets/…png|svg` path in place, and reports the count.
Idempotent — a path already under a new root is left untouched.

**Historical / one-shot:** ran once during RESTRUCTURE Phase 2; every sheet
under `research/prompts/` already uses the new tree today.

## Usage

```bash
python research/rewrite_sheet_paths.py
```

## Connections

### Uses
- Every `research/prompts/**/*.md` file — rewrites paths in place

### Used by
- Nobody at runtime; the one-shot RESTRUCTURE Phase 2 execution session

## Functions

- `_flatten_alt(parts)` — turns a `.../alt/<name>.png` tail into its
  figure-first, flattened filename (same `ALT_FIGURE` table as
  [Build Relocation Manifest](build_relocation_manifest.md), plus a `_v2`
  fallback for unlisted stems)
- `transform(path)` — the per-path relocation rule, dispatched on the
  asset's top-level root (mirrors `build_relocation_manifest.new_path`,
  sourceless)
- `main()` — walks every sheet, substitutes every matched path, writes
  changed files, prints the rewrite count
