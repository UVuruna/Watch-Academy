# Symbolism Repository

**Script:** [Symbolism Repository (script)](../symbolism.py) ·
**Flow:** [diagram](../__flow/symbolism.md)

## Purpose

Read-only access to `Database/symbolism.json` — the machine-readable
companion of the narrative canon (`SYMBOLISM.md`). Serves the per-body
hover blurbs and the encyclopedic ARTICLES: per (article set, body) a
base text plus one variant paragraph per pointer/palette combination
(and, for the dual Sunday seats, per-face text), the zodiac/Chinese/
element/trio articles, and the two-row archetype-wheel articles.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `paths.database_dir()`
- [Database (folder)](../../Database/___database.md) —
  `symbolism.json`

### Used by
- [Compositor](../../render/__about/compositor.md) — the hexa arm hover text
- [Translations Repository](translations.md) — `collect_corpus()`
  reads `symbolism.json` directly (not through this repository) to
  build the translatable corpus

## Classes

### SymbolismRepository
- `__init__(path=None, overlay=None)`: `overlay` is the active
  language's translated texts (key → text), laid over the English
  originals; entries not yet translated fall back to English.
- `arm_blurbs(body)`: the blurb texts of one weekday body, center
  included.
- `article(article_set, body)`: `{base, variants[, faces]}` of one
  entity. A `$ref` entry (a pantheon reseat) resolves to its SOURCE
  entity's article, localized under the source's own keys — see
  [flow](../__flow/symbolism.md).
- `archetype_article(article_set, entity)`: the two-row archetype
  article `{"rows": [row1, row2]}`, or `None` when the set/entity is
  not yet written (the documented graceful path — never a `KeyError`
  inside a hover).
- `zodiac_article(sign)`: `{base, variants}` of one tropical sign.
- `trio_article(virtue)`: `{base}` of one Trinity-arm virtue.
- `chinese_article(animal)` / `chinese_element(element)`: `{base}` of
  one Chinese zodiac animal / Wu Xing element.
