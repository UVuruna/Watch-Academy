# Card

**Script:** [Card (script)](cards.py)

## Purpose
ONE card component for both gallery levels — plate, title, about line,
footer stat, and the whole's accent on its edge — plus the `CardGrid`
that lays cards in centered rows, and the two width formulas that make
the no-X-scroll law arithmetic.

## Connections

### Uses
- [Asset Variants](../../render/asset_variants.md) — the pre-warmed downscale a card icon decodes from

### Used by
- [Home Screen](home.md), [Theme Screen](themes.md)

## The width pair (Rule #5 — one formula, two directions)

```
row_content_width(card, columns)
    = columns * card + (columns - 1) * gap + margins

card_width_for(viewport, columns)          <- the exact inverse
    = (viewport - margins - (columns - 1) * gap) / columns
```

The old gallery grew a horizontal scrollbar TWICE because its two
directions were computed separately and drifted. They are one pair now.

## Design Decisions
- **Rows center as blocks** — a stretch on both sides, so a short
  trailing row centers exactly like a full one (owner round R8b item 5d).
- **A missing plate is not an error** — the card shows its title, the
  graceful-absent contract every tile has always had.
