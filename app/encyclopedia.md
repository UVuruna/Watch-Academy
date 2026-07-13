# Encyclopedia

**Script:** [Encyclopedia (script)](encyclopedia.py)

## Purpose
The article BROWSER (owner spec 2026-07-12; menu Encyclopedia… below
Time Travel…): every legend readable without hovering the dial, on two
screens —

1. **Topics** — a gallery in the owner's GROUPS (`_TOPIC_GROUPS`):
   The Clock, Gods, Zodiac, Themes, Religions, Animal Societies and
   The Inner Wheel — EVERYTHING centered (owner 2026-07-13: headers
   and card rows alike) and the cards RESPONSIVE: `_rescale_topics`
   grows/shrinks the icons with the window between
   `ENCYCLOPEDIA_TOPIC_ICON_MIN/MAX_PX`; only below the minimum does
   the scrollbar take over.
2. **Articles** — a scrollable list of the topic's entries: the
   entity image(s) — Astrology shows the sign LOGO and its
   CONSTELLATION side by side, every Sunday RULER/SERVANT pair stands
   side by side too (owner correction 2026-07-13: never stacked) —
   the NAME as a bold title and the
   full base article, translated through the active overlay and with
   the canon terms highlighted exactly like the dial legends (virtues
   blue, vices red, moods yellow, the entity's own arm hue).

The window is RESIZABLE: each entry is ONE centered block spanning
`ENCYCLOPEDIA_TEXT_WIDTH_FRACTION` of the width (the text stays
left-aligned INSIDE the block — owner: center the object, never the
lines), images share the block, and the font grows with the width at
the gentle em-like coefficient (`ENCYCLOPEDIA_FONT_GROWTH`, capped).

It is a NORMAL window (owner 2026-07-13: no stay-on-top). The look
images decode LAZILY — `_show_topic` keeps only PATHS and
`_render_cell` loads through the `_pixmap` cache on first display
(owner 2026-07-13: The Week opened far too slowly when every look of
every entry decoded upfront), and after every look switch the grid
geometry is committed immediately so larger art never draws clipped
under its neighbors.

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
- `_show_topic(key)`: fills the scrollable article list (paths only —
  pixmaps decode lazily)
- `_rescale()`: live sizing on resize — gallery cards through
  `_rescale_topics()`, article blocks/fonts otherwise
- `_pixmap(path)`: the decoded-image cache behind the lazy looks
