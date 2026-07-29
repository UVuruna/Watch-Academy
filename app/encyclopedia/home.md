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

## The grid never dictates a minimum

> **Root cause fixed 2026-07-29 (owner bug, Rule #25).** The window
> resized ONE WAY: every enlargement stuck and it could never be
> dragged back down — height most visibly.
>
> `fit()` measures the cards FROM the viewport and pins them with
> `setFixedWidth`/`setFixedHeight` — which is also how Qt declares a
> MINIMUM. Because this screen owns no scroll area, that minimum went
> straight up into the dialog: stretched to 1920x1200 the home screen
> reported a minimum of 1898x1126, so the floor was wherever the user
> had last dragged the edge. Growth was a ratchet.
>
> The grid's own size hints are meaningless BY DESIGN here — the
> viewport is the INPUT, not the output — so the grid and this screen
> both declare `QSizePolicy.Ignored`, and the only floor left is the
> dialog's own `ENCYCLOPEDIA_MIN_WIDTH_PX` x `ENCYCLOPEDIA_MIN_HEIGHT_PX`
> (the owner's 1280x720 opening screen). Pinned by
> `test_growing_the_window_never_raises_its_own_minimum`.

## The plate — computed, not generated

Root Rule #19: a category image is derivable, so it is never generated.

```
IF a drawn plate exists at ENCYCLOPEDIA_WHOLE_ART_DIR/<whole>.png
    -> use it
ELSE
    -> compose the whole's first four theme plates into one square
```

A hand-drawn plate always wins; the mosaic is the floor, not a ceiling.
