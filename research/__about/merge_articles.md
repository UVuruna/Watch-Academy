# Merge Articles

**Script:** [Merge Articles (script)](../merge_articles.py) ·
**Flow:** [diagram](../__flow/merge_articles.md)

## Purpose

One-shot merge of the staged pantheon/religion/ninth articles into the live
databases (owner execution wave, 2026-07-15): adds the four Pantheon article
sets to `Database/symbolism.json` (validating shape — 7 bodies, and every
non-`$ref` entry carries a `base` plus exactly the six pointer/palette
variant keys), applies the Religion rework moves (Christianity → sun with
the new ruler/servant faces, Sikhism → venus, Eleusis → the Ancient set),
adds the new Ninths to `Database/encyclopedia.json`, lands every staged
Serbian text into the sr-Latn bundle (hash-keyed against the merged
English, orphans pruned), and prints the audit.

**Historical / one-shot:** its input folder, `research/articles_staging/`,
was deleted after the clean merge that consumed it (per the script's own
docstring) and is absent today — re-running it now fails at the first
missing staging file. Kept as the executable record of the 2026-07-15 merge.

## Usage

```bash
python research/merge_articles.py
```

Run from the project root. Idempotent by design — re-running overwrites the
same keys with the same data (when the staging input still exists).

## Connections

### Uses
- `research/articles_staging/*.json` (gone — one-shot, historical)
- `Database/symbolism.json`, `Database/encyclopedia.json`,
  `Database/translations/sr-Latn.json` — read and overwritten in place
- `data.translations.collect_corpus` — the live English-text corpus the SR
  bundle is audited against

### Used by
- Nobody at runtime; historical record of the 2026-07-15 article-merge wave

## Functions

- `check_entry(name, entry)` — validates one article entry's shape: either a
  two-element `$ref` pointer, or a non-empty `base` plus exactly the six
  variant keys (`hexa_primary`, `hexa_secondary`, `octa_primary`,
  `octa_secondary`, `cross`, `trio`), each non-empty
- `main()` — merges the four Pantheon sets, applies the Religion rework,
  writes the two Database JSON files, then merges/prunes the Serbian bundle
  and prints the audit (bundle count vs. corpus count, missing/stale keys)
