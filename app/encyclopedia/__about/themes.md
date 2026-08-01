# Theme Screen

**Script:** [Theme Screen (script)](../themes.py) · **Flow:** [diagram](../__flow/themes.md)

## Purpose
Level two — one whole's theme cards, in the same card language as the
home screen (Rule #5, one `CardGrid`), up to
`encyclopedia_ui.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS` per row, wrapping into
further rows.

**Vertical scroll is allowed here; horizontal never** — the scroll
area's horizontal bar is switched off outright and the card width is
measured from the viewport, so no row can want one in the first place.

## Connections

### Uses
- [Card](cards.md) — `CardGrid`, `card_pixmap`
- [Encyclopedia Repository](../../../data/__about/encyclopedia.md) — `about(topic)`
- [Encyclopedia Tree (config)](../../../config/__about/encyclopedia_tree.md) — `WHOLE_BY_KEY`

### Used by
- [Encyclopedia Dialog](dialog.md) — the second stacked screen

## Classes

### ThemeScreen
`QWidget`, `opened = Signal(str)`.

- `__init__(topics, encyclopedia, tr)`: one `CardGrid` sized
  `ENCYCLOPEDIA_GALLERY_MAX_COLUMNS`, wrapped in a `QScrollArea` whose
  horizontal bar is force-off
- `whole` (property): the whole currently shown, or `None`
- `show_whole(key)`: looks up `tree.WHOLE_BY_KEY[key]`, rebuilds the
  grid from that whole's own themes, `fit()`s and resets the scrollbar
  to the top
- `_spec(theme)`: the card spec dict — `footer` is `"N pages"`, plus
  `"· M registers"` when the theme carries more than one variant
- `fit(zoom=None)` / `resizeEvent(event)`: re-measures from
  `self._scroll.viewport().width()` alone (height is never pinned —
  vertical scroll absorbs the rest)

## Design Decisions
- **The footer's register count** only appears for a theme whose
  variant switcher has something to walk (`len(topic["variants"]) > 1`)
  — a single-register theme's footer stays a bare page count.
- **Only the width drives sizing here** — unlike the home screen, this
  grid never needs a pinned height; the scroll area is exactly what the
  home screen deliberately has none of.
