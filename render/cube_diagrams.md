# Cube Diagrams

**Script:** [Cube Diagrams (script)](cube_diagrams.py)

## Purpose

The Cube's Encyclopedia pages that are COMPOSITIONS rather than scenes,
drawn by the program from [Cube canon](../config/cube.md)'s own
coordinates.

The Session 27 coverage law says every article carries an image. Twenty
three pages could not honestly be given one: an axis IS its two poles
through the centre, a term grid is a table, a cipher is a word — and the
canon exempted exactly those from generation in writing (CUBE.md,
Session 25, under root Rule #19). The owner's verdict (2026-07-29)
closed the circle: **computed, not generated, and never blank.**

Change a term in the canon table and every diagram showing it changes
with it. That is the whole reason to compute an asset instead of storing
one.

## Connections

### Uses
- [Cube](../config/cube.md) — the thirteen axes, their cells and the
  sealed Rose hue of each face pole
- [Config (folder)](../config/___config.md) — the drawing ratios and the
  theme colours

### Used by
- [Reader Screen](../app/encyclopedia/reader.md) — a page declaring
  `"diagram": (kind, key)` gets its plate from `plate()`
- [Static Pages](../app/encyclopedia/pages.md) — where the declarations
  live, as a third column beside (name, art)

## The projection

```
screen_x = (x − y) · cos30 · unit
screen_y = (x + y) · sin30 · unit − z · unit
```

Classic 30° isometric: no two of the 27 integer cells ever land on the
same point, and the three axes stay visually equal — which matters,
because the canon insists no axis outranks another. +z is UP, so
Self-Regard stands vertical exactly as CUBE.md draws it.

## The drawers

| Kind | Pages | What it draws |
|---|---|---|
| `axis` | 12 | the cube faint, ONE axis lit through the centre, both poles named |
| `cube` | 1 | all 27 cells in their own hues, The One lit |
| `axes` | 1 | all thirteen lines at once — 3 face, 4 corner, 6 edge |
| `hexagram` | 1 | the view down the Sacred Axis: six corners on a hexagram |
| `banknote` | 1 | the three face axes, the banknote's own reading |

## The colour law

A face pole wears its sealed Rose hue (`cube.ROSE_POLE_HUE`); The One
wears the dial's accent; **every other cell is the average of the poles
it stands between** — computed, so a re-tuned palette moves the whole
cube at once and no hex is ever hand-picked here (Rule #4).

## Design Decisions

- **One master, scaled.** `plate()` caches per (kind, key, size) and the
  reader always asks for `CUBE_DIAGRAM_SIDE_PX`, then scales the result
  to the page — one drawing serves every zoom level (Rule #19's own
  master-plus-transform pattern).
- **Labels are clamped inside the plate.** The first render pushed long
  pole names off the edge, where they were silently lost; `_clamped`
  makes that unrepresentable.
- **Every ratio is a share of the plate's side** — nothing here is a
  pixel constant, so one figure serves a 200px card and a full-screen
  reader alike.

## Not yet drawn

Seven pages still wait for their own drawers — the term grid, the three
sets, the two triangles, the union table, the chiasm and the two ciphers
(`tree.PLATELESS_PAGES` names them). They are data-driven figures too,
so none of them is a prompt either.
