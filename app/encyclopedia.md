# Encyclopedia

**Script:** [Encyclopedia (script)](encyclopedia.py)

## Purpose
The article BROWSER (owner spec 2026-07-12; menu Encyclopedia… below
Time Travel…): every legend readable without hovering the dial, on two
screens —

1. **Topics** — a gallery in FOUR GROUPS (owner UX round 2026-07-12,
   `_TOPIC_GROUPS`): Gods (Greek/Norse/Egyptian/Slavic), Zodiac
   (Astrology, Chinese zodiac, Planets, Planet signs), Themes
   (Alchemy, Japanese week, Professions, Trinity) and Religions
   (two members for now) — a bold header + rule above each card row.
2. **Articles** — a scrollable list of the topic's entries: the
   entity image(s) — Astrology shows the sign LOGO and its
   CONSTELLATION side by side — the NAME as a bold title and the
   full base article, translated through the active overlay and with
   the canon terms highlighted exactly like the dial legends (virtues
   blue, vices red, moods yellow, the entity's own arm hue).

The window is RESIZABLE: each entry is ONE centered block spanning
`ENCYCLOPEDIA_TEXT_WIDTH_FRACTION` of the width (the text stays
left-aligned INSIDE the block — owner: center the object, never the
lines), images share the block, and the font grows with the width at
the gentle em-like coefficient (`ENCYCLOPEDIA_FONT_GROWTH`, capped).

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
