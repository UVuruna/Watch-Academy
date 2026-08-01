# Rewrite Look Paths

**Script:** [Rewrite Look Paths (script)](../rewrite_look_paths.py)

## Purpose

Rewrites every literal `assets/...` path in the prompt sheets, the COVERAGE
ledger and the sheet-path lint whitelist onto the tree law — the directory
map is derived from the EXECUTED migration commit's own rename records
(`git show -M --name-status`), so the rewrite is exact by construction,
never a guessed regex. One-shot companion of
[Migrate Tree Law](migrate_tree_law.md); kept as the record of how the text
side of that migration moved.

**Historical / one-shot:** ran once against the 2026-07-26 tree-law commit.

## Usage

```bash
python research/rewrite_look_paths.py <tree-commit-hash>
```

## Connections

### Uses
- `git show -M --name-status` against the given commit — the source of the
  directory rename map
- Rewrites `research/prompts/**/*.md` and `tests/test_prompt_paths.py` in
  place

### Used by
- Nobody at runtime; the one-shot 2026-07-26 tree-law session, run once
  right after [Migrate Tree Law](migrate_tree_law.md)'s `--execute`

## Functions

- `dir_map(commit)` — parses `git show`'s renamed-file lines into an
  `{old_dir: new_dir}` map, longest-old-path first
- `main()` — applies every directory rename as a text substitution across
  the prompt sheets and the path-lint whitelist, reporting changed lines
  per file
