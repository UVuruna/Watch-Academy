# Translations

**Script:** [Translations (script)](../translations.py) ·
**Flow:** [diagram](../__flow/translations.md)

## Purpose

Translate-once-then-cache (owner spec): the app ships ONLY English.
`collect_corpus()` gathers every translatable text (article sets,
zodiac/Chinese/element/trio articles, every Encyclopedia section and
emblem family, guide captions/page titles, and the UI chrome strings)
under stable keys. `TranslationStore` layers three sources per language
— the shipped English, a BUNDLED original (English and Serbian Latin
ship hand-written, `Database/translations/<lang>.json`) and the user's
own cache — hash-tracked per entry so an edited source re-translates
only the changed entries, and an interrupted run resumes.
`translate_texts()` talks to the keyless Google `gtx` endpoint (no
account, no key); `sr-Latn` runs its result through a local Cyrillic →
Latin transliteration.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) —
  `defaults.TRANSLATE_ENDPOINT` / `TRANSLATE_TIMEOUT_S`,
  `defaults.GUIDE_DIR`, `paths.database_dir()` / `paths.settings_path()`,
  `ui_text.UI_STRINGS`, `profiling.timed`
- `Database/symbolism.json`, `Database/encyclopedia.json` — read
  directly for the corpus walk (not through their own repositories)

### Used by
- [Watch Controller](../../app/__about/controller.md) — background translation
  on language change; the loaded overlay feeds
  [Symbolism Repository](symbolism.md), [Encyclopedia Repository]
  (encyclopedia.md) and the Guide

## Functions

- `collect_corpus()`: `key → English text` for everything translatable
  — see [flow](../__flow/translations.md) for the full key-naming walk.
- `translate_texts(texts, target, progress=None)`: translated dict, one
  HTTP request per entry; raises on network failure (Rule #1 — the
  caller surfaces it); `sr-Latn` transliterates the `sr` result.
- `transliterate_sr(text)`: Serbian Cyrillic → Latin, digraphs (`lj`,
  `nj`, `dž`) following their word's case.

## Classes

### TranslationStore
- `__init__(directory=None, bundled=None)`: `directory` defaults to
  `<settings dir>/translations`, `bundled` to `Database/translations`.
- `load(lang)`: `key → translated text`. A bundled original wins
  whenever its English source hash matches the user's cached entry's
  hash; the user's cached entry wins only where its English moved on
  since the bundled original was made.
- `missing(lang, corpus)`: the corpus entries whose current English
  hash matches NEITHER the bundled original's hash NOR the user's
  cached hash for that key — i.e. new keys and keys whose source text
  changed since the last translation.
- `save(lang, corpus_slice, texts)`: merges freshly translated entries
  into the user's cache and writes it atomically (`os.replace`); the
  bundled file is never written at runtime.

## ONE run, ONE writer, ONE corpus (owner bug 2026-08-06)

`WatchController._apply_language` guarded on its OWN `_translation_
thread`, which is per watch. Five watches sharing a language therefore
started five workers: the same corpus translated five times through the
same endpoint, and five writers on one cache file.

- `claim_translation(language)` / `release_translation(language)` — the
  process-wide claim. Taken BEFORE the corpus is built, so the 1.5 MB of
  reading behind `missing()` happens once too. The worker releases in a
  `finally`: a claim left standing would block every later retry, and
  the run is resumable by design.
- `_SAVE_LOCK` serializes `save()`'s read-merge-write. **This was a
  correctness bug, not a slowdown**: the interleaving A-reads, B-reads,
  A-writes, B-writes silently DROPS every entry A had persisted, and the
  resumable-chunk design makes the loss invisible — the next run simply
  retranslates what it thinks is missing. The temp file also carries the
  writer's thread id, so a stale `.tmp` from a killed process is never
  mistaken for this one's.
- `_CORPUS` memoizes `collect_corpus()`, which re-reads symbolism.json
  (1.12 MB) and encyclopedia.json (439 KB); it ran once per watch at
  startup and again inside the worker.
