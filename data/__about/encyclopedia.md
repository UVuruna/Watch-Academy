# Encyclopedia Repository

**Script:** [Encyclopedia Repository (script)](../encyclopedia.py)

## Purpose

Loads `Database/encyclopedia.json` — the Encyclopedia's OWN content,
separate from the dial articles in `symbolism.json`: the home screen's
NINE WHOLES cards, each theme's about line, the INSTRUMENT functionality
articles, the WEEK day pages, the SEASONS/SUN/MOON/ERA/ECLIPSE articles,
every weekday theme's THEME_TITLE and WEEK_DUALITY opening pages, and
the emblem-family entries (virtues/sins/moods/duality/ninths/
intelligence/wider/months/cube/double_trinity/crosses/one_soul). Every
text rides the same overlay mechanism as the dial articles
(`encyclopedia/<section>/<key>/title|base` keys), so the bundled
Serbian and any machine-translated language apply automatically.

## Connections

### Uses
- [Database (folder)](../../Database/___database.md) —
  `encyclopedia.json`
- [Config (folder)](../../config/___config.md) — `paths.database_dir()`

### Used by
- [Encyclopedia (subfolder)](../../app/encyclopedia/___encyclopedia.md)
  — the browser UI
- [Compositor](../../render/__about/compositor.md)
- [Translations Repository](translations.md) — `collect_corpus()` walks
  every section this repository serves

## Classes

### EncyclopediaRepository
- `__init__(overlay=None)`: `overlay` is the active language's
  translated texts (key → text), laid over the English originals.
- `whole(key)`: `{title, base}` of one of the home screen's NINE
  WHOLES cards.
- `about(key)`: `{base}` — one theme card's about line on the theme
  screen.
- `instrument(key)` / `week(body)` / `season(key)` / `sun(key)` /
  `moon(key)` / `era(key)` / `eclipse(key)`: `{title, base}` of one
  article in that top-level section.
- `theme_title(theme)` / `week_duality(theme)`: `{title, base}` of a
  weekday theme's own opening page / its week-duality title page.
- `entry(family, name)`: `{base}` of one emblem-family article —
  `family` is any of virtues/sins/moods/duality/ninths/intelligence/
  wider/months/cube/double_trinity/crosses/one_soul.
- `_section(section, key)` (private): the shared localized lookup
  every public method above delegates to — `{title, base}` of
  `data[section][key]`, overlaid.
