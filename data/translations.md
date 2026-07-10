# Translations

**Script:** [Translations (script)](translations.py)

## Purpose
The owner's translation model: WE ship only English; the user's machine
translates it once and caches it. `collect_corpus()` gathers every
translatable text (all article sets, zodiac/chinese/element/trio
articles, guide captions) under stable keys; `TranslationStore` caches
per-language JSON in `%APPDATA%/DOMY Watch/translations/` with a source
HASH per entry — after we edit an article only the changed entries are
re-translated, and an interrupted run resumes where it stopped.
`translate_texts()` talks to the keyless Google gtx endpoint (no
account, no key — the owner's "simple option"); `sr-Latn` is served as
Serbian plus a local Cyrillic→Latin transliteration.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — endpoint, language table,
  database path
- [Symbolism Repository](symbolism.md) — the corpus source

### Used by
- [App Controller](../app/controller.md) — background translation on
  language change; the overlay feeds the repository and the Guide

## Functions

- `collect_corpus()`: key → English text for everything translatable
- `translate_texts(texts, target, progress?)`: translated dict; raises
  on network failure (the caller shows it — Rule #1)
- `transliterate_sr(text)`: Serbian Cyrillic → Latin

## Classes

### TranslationStore
- `load(lang)`: the cached overlay (key → text) or `{}`
- `missing(lang, corpus)`: entries new or changed since caching
- `save(lang, corpus_slice, texts)`: merge + persist (atomic)
