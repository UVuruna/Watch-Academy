# PascalCase Stems

**Script:** [PascalCase Stems (script)](../pascalcase_stems.py) ·
**Flow:** [diagram](../__flow/pascalcase_stems.md)

## Purpose

One-shot PascalCase stem unification (tree law rule 5's case half,
owner-approved 2026-07-26): every figure stem in the three figure categories
(`weeks/`, `calendars/`, `archetypes/`) reads as a NAME — `anubis` →
`Anubis`, `afu_ra` → `Afu_Ra`, `big_bang` → `Big_Bang` — while `_vN` version
and `_gem`/`_gpt` source suffixes ride along verbatim, and tokens that
already carry a capital (`Yggdrasil`, `KaliYuga`) stay exactly as drawn.
Case-only renames go through a two-step `git mv` (Windows' case-insensitive
filesystem swallows a direct one). Dry-run by default.

**Historical / one-shot:** ran once on 2026-07-26; filenames under the three
figure roots already carry PascalCase stems today.

## Usage

```bash
python research/pascalcase_stems.py            # dry run — prints the plan
python research/pascalcase_stems.py --execute  # performs the git mv plan
```

## Connections

### Uses
- `git` (`git mv`, two-step for case-only renames)
- The `weeks/`, `calendars/`, `archetypes/` trees under `assets/`

### Used by
- Nobody at runtime; the one-shot 2026-07-26 tree-law session. Companion of
  [Migrate Tree Law](migrate_tree_law.md) — same contract: explicit plan,
  collision abort, before/after counts

## Functions

- `pascal_name(filename)` — peels off a trailing source tag (`_gem`/`_gpt`)
  and a trailing `_vN`, keeps them verbatim, Titlecases every remaining
  token that has no uppercase letter already
- `plan()` — the full list of (old, new) path pairs whose name actually
  changes
- `main()` — collision detection (two sources landing on one target, or a
  genuinely different pre-existing file), then dry-run print or `--execute`
