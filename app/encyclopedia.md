# Encyclopedia

**Script:** [Encyclopedia (script)](encyclopedia.py)

## Purpose
The article BROWSER (owner spec 2026-07-12; menu Encyclopedia… below
Time Travel…): every legend readable without hovering the dial, on two
screens —

1. **Topics** — a gallery grid, one card per topic with its symbol
   image: every weekday theme (`WEEKDAY_THEME_TITLES`, ten as of
   2026-07-12 — Slavic gods and Alchemy joined), Astrology (the
   twelve signs), the Chinese zodiac (twelve animals + five
   elements) and the Trinity.
2. **Articles** — a scrollable list of the topic's entries: the
   entity image, its NAME as a bold title and the full base article,
   translated through the active overlay and with the canon terms
   highlighted exactly like the dial legends (virtues blue, vices
   red, moods yellow, the entity's own arm hue).

The window is RESIZABLE like the Guide: entry images rescale live
with the width.

## Connections

### Uses
- [Symbolism Repository](../data/symbolism.md) — articles (overlay
  applied)
- [UI Text Catalog](../config/ui_text.md) — chrome + entity names
- [Compositor](../render/compositor.md) — `_article_body_html` (the
  one wrap/highlight implementation, Rule #5)
- [Config (folder)](../config/___config.md) — art directories, accent
  tables

### Used by
- [App Controller](../app/controller.md) — opens it from the menu
  with the translation overlay

## Classes

### EncyclopediaDialog
- `__init__(translations)`: builds the topic gallery
- `_show_topic(key)`: fills the scrollable article list
- `_rescale()`: live image sizing on resize (Guide pattern)
