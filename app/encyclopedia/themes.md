# Theme Screen

**Script:** [Theme Screen (script)](themes.py)

## Purpose
Level two — one whole's theme cards, in the same card language as the
home screen (Rule #5, one `CardGrid`), up to
`ENCYCLOPEDIA_GALLERY_MAX_COLUMNS` per row, wrapping into further rows.

**Vertical scroll is allowed here; horizontal never** — the bar is
switched off outright and the card width is measured from the viewport,
so no row can want one.

## Connections

### Uses
- [Card](cards.md) — the shared card and grid
- [Encyclopedia Repository](../../data/encyclopedia.md) — `about(topic)`

### Used by
- [Encyclopedia Dialog](dialog.md)

## The footer stat
`26 pages / 3 registers` — the second half appears only for a theme
whose switcher has something to walk.
