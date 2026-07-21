# Translations

**Script:** [Translations (script)](translations.py)

## Purpose
The owner's translation model: English and Serbian Latin ship as
hand-written ORIGINALS (owner decision 2026-07-11 — pinned at the top
of the language combo); every other language machine-translates once
on the user's machine and caches. `collect_corpus()` gathers every
translatable text (all article sets, zodiac/chinese/element/trio
articles, guide captions and page titles) under stable keys;
`TranslationStore` layers three sources: the shipped English, the
BUNDLED originals (`Database/translations/<lang>.json`) and the user's
cache in `%APPDATA%/DOMY Watch/translations/` — each entry carries a
sha1 of its ENGLISH source, so after we edit an article only the
changed entries re-translate (for originals they fall back to machine
output until we refresh the bundle), and an interrupted run resumes
where it stopped. `translate_texts()` talks to the keyless Google gtx
endpoint (no account, no key — the owner's "simple option"); `sr` is
served as Serbian plus a local Cyrillic→Latin transliteration when
the target is `sr-Latn` and no bundle covers an entry.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — endpoint, language table,
  database path
- [Symbolism Repository](symbolism.md) — the corpus source

### Used by
- [Watch Controller](../app/controller.md) — background translation on
  language change; the overlay feeds the repository and the Guide

## Functions

- `collect_corpus()`: key → English text for everything translatable
- `translate_texts(texts, target, progress?)`: translated dict; raises
  on network failure (the caller shows it — Rule #1)
- `transliterate_sr(text)`: Serbian Cyrillic → Latin

## Classes

### TranslationStore
- `load(lang)`: the overlay (key → text) — bundled original first,
  the user's cache on top; `{}` when neither exists
- `missing(lang, corpus)`: entries new or changed since caching
  (bundled hashes count as cached; the user's cache wins on conflict)
- `save(lang, corpus_slice, texts)`: merge + persist into the USER
  cache (atomic; the bundle is never written at runtime)
