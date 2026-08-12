# Cube Diagrams

**Script:** [Cube Diagrams (script)](../cube_diagrams.py) · **Flow:** [diagram](../__flow/cube_diagrams.md)

## Purpose
The Character Cube's Encyclopedia pages that are COMPOSITIONS rather
than scenes — one axis lit inside its cube, the whole cube, all
thirteen lines, the hexagram projection, the banknote axes — drawn live
from `config.cube`'s own coordinates (owner verdict 2026-07-29:
computed, not generated, and never blank). Change a term in the canon
table and every diagram showing it changes with it — the whole reason
to compute an asset instead of storing one.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `cube` (the thirteen
  axes, their cells, the sealed Rose hue of each face pole)
- [Core (folder)](../../core/___core.md) — `cube_seating.cell_color()`
  (the colour law) and `find_pole()` (the pole lookup), shared with the
  3D model exporter (Rule #5)

### Used by
- [Diagrams](diagrams.md) — a page declaring `"diagram": (kind, key)`
  gets its plate from `plate()`
- [Cube Preview3D Bridge](cube_preview3d.md) — falls back to this
  module's 2D plate whenever the 3D gadget/model is unavailable

## The projection
```
screen_x = (x - y) * cos30 * unit
screen_y = (x + y) * sin30 * unit - z * unit
```
Classic 30° isometric: no two of the 27 integer cells ever land on the
same point, and the three axes stay visually equal — the canon insists
no axis outranks another. +z is UP.

## The drawers
| Kind | Pages | What it draws |
|---|---|---|
| `axis` | 12 | the cube faint, ONE axis lit through the centre, both poles named |
| `cube` | 1 | all 27 cells in their own hues, The One lit |
| `axes` | 1 | all thirteen lines at once — 3 face, 4 corner, 6 edge |
| `hexagram` | 1 | the view down the Sacred Axis: six corners on a hexagram |
| `banknote` | 1 | the three face axes, the banknote's own reading |

The seven pages once listed as "not yet drawn" here (the term grid, the
three sets, the two triangles, the union table, the chiasm, the two
ciphers) are now [Canon Diagrams](canon_diagrams.md)'s five drawers —
this module's own scope is exactly the five kinds above.

## The colour law
A face pole wears its sealed Rose hue (`cube.ROSE_POLE_HUE`); The One
wears the dial's accent; every other cell is the AVERAGE of the poles
it stands between — computed in `core.cube_seating.cell_color()`, so a
re-tuned palette moves the whole cube at once and no hex is ever
hand-picked here (Rule #4).

## Design Decisions
- **One master, scaled.** `plate()` caches per (kind, key, size), but
  the reader always asks for `CUBE_DIAGRAM_SIDE_PX` and scales that one
  pixmap itself — a page turn never repaints the same figure twice, and
  one drawing serves every zoom level.
- **Labels are clamped inside the plate** (`_clamped`) — the first
  render pushed long pole names off the edge, silently lost.
- **Every ratio is a share of the plate's side** — nothing here is a
  pixel constant.
