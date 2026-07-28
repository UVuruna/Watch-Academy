# Home Screen

**Script:** [Home Screen (script)](home.py)

## Purpose
Level one — the SIX WHOLES in a 2x3 grid. The owner's law is absolute
(*"Prvi ekran nema scroll. uvek sve staje u window"*), so this screen
owns **no scroll area at all** and measures its cards from the widget's
own width AND height.

Each card carries its whole's Rose accent, a plate, the whole's about
line and a live count (`5 themes / 52 pages`).

## Connections

### Uses
- [Card](cards.md) — the shared card and grid, and `mosaic_pixmap`
- [Encyclopedia Repository](../../data/encyclopedia.md) — `whole(key)`, the about text
- [Encyclopedia Tree](../../config/encyclopedia_tree.md) — the six wholes

### Used by
- [Encyclopedia Dialog](dialog.md)

## The plate — computed, not generated

Root Rule #19: a category image is derivable, so it is never generated.

```
IF a drawn plate exists at ENCYCLOPEDIA_WHOLE_ART_DIR/<whole>.png
    -> use it
ELSE
    -> compose the whole's first four theme plates into one square
```

A hand-drawn plate always wins; the mosaic is the floor, not a ceiling.
