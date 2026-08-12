# Cube Seating — the geometry of the two display plans

**Script:** [Cube Seating (script)](../cube_seating.py) · **Flow:** [diagram](../__flow/cube_seating.md)

## Purpose

The Character Cube's pure geometry, and the two seatings it solves:
**Calendar-12** (twelve arms, one human axis each) and **Rose-24**
(twenty-four rays, one human seat each). Everything the coordinates can
decide is decided here — kinship, antipodes, families, indices, ray
hues — so [Character Cube (config)](../../config/__about/cube.md) can stay a
table of words (root Rule #19 — compute, don't generate).

`cell_color()` and `find_pole()` are the same derivations
[Cube Diagrams](../../render/__about/cube_diagrams.md) draws with — extracted
here, Qt-free, so the 2D diagrams and the 3D model export share one
computation (root Rule #5).

## Connections

### Uses
- [Character Cube (config)](../../config/__about/cube.md) — the thirteen axes
  (`cube.AXES`), the sealed pole hues (`cube.ROSE_POLE_HUE`), the sealed
  Rose-24 seating (`cube.ROSE_24_SEATING`), `cube.CALENDAR_WEDGES_BY_FAMILY`,
  `cube.CALENDAR_AXIS_ORDER`
- [Palette (config)](../../config/__about/palette.md) — `THEME_COLORS["accent"]`,
  `ROSE_PALETTE` (hex colors for `cell_color`)

### Used by
- [Cube Seating Tests](../../tests/___tests.md) — re-runs the whole
  search and pins every seat
- [Research (folder)](../../research/___research.md) — the offscreen
  preview generator draws both seatings from here
- [Cube Diagrams](../../render/__about/cube_diagrams.md) — `cell_color()` and
  `find_pole()`, the 2D drawer's own colour and lookup
- [Cube Model Export](../../data/__about/cube_model_export.md) — the
  same `cell_color()`, plus `family_of`/`SACRED_AXIS` for tier
  assignment (the 3D exporter)

## The laws

### The symmetry law (owner decree 2026-07-28)
Symmetry decides which KIND of axis stands where; symbolism only decides
which axis of that kind. The families count 3 face axes, 6 edge axes and
3 human vertex axes — both wheels wear two opposed equilateral triangles
with a hexagon between them (the hexagram):

```
ROSE      ray % 4 == 0 -> a POLE      (12h 16h 20h 24h 4h 8h)
          ray % 4 == 2 -> a CORNER    (14h 18h 22h  2h 6h 10h)
          any odd ray  -> an EDGE     (twelve, one every 30 degrees)

CALENDAR  the pure-primary arms  (June 12h, October 20h, February 4h) -> the 3 face axes
          the mixed-primary arms (August 16h, December 24h, April 8h) -> the 3 vertex axes
          the six remaining arms                                      -> the 6 edge axes
          (inverted=True swaps the two triangles)
```

### The one-grade law (kinship)
Two cells are kin when they differ in exactly one coordinate, by exactly
one grade: `is_kin(a, b) := sorted(|a_i - b_i]) == [0, 0, 1]`.

### The antipodal law
Ray *k* and ray *k+12* hold the two ends of ONE axis (`antipode`).

### The parity theorem
Each kinship step changes a cell's nonzero-count by one, so the kinship
graph is bipartite (14 face/vertex cells vs. 12 edge cells) — no ring
can seat all 26 cells. Removing the two Sacred vertices balances it at
12 + 12; geometry does not choose WHICH two, only that a removal is
required.

### The colour laws (the Rose)
Each primary axis holds its own sealed hue diagonal (X cyan <-> orange, Y
yellow <-> purple, Z green <-> rose) — under the symmetry law this comes
free, since the six pole rays ARE the six cube-coloured rays.

## Functions

- `antipode(cell)`, `axis_key(cell)`, `is_kin(a, b)`, `rank(cell)` —
  coordinate primitives (1 face / 2 edge / 3 vertex).
- `family_of(axis)` / `index_of(axis)` — which of the three families an
  axis belongs to, and the coordinate letter that names it.
- `ray_hour(ray)` / `ray_star(ray)` / `ray_hue_index(ray)` — the Rose's
  own ray -> hour/star/hue mappings.
- `pole_hues(cell)` — the hues of the poles a cell carries.
- `required_rank(ray)` / `is_symmetric(ring)` — the symmetry law as a
  predicate.
- `antipodal_rings(symmetric=True)` — the exhaustive backtracking search
  over all human-cell seatings.
- `diagonals_held(ring)` / `poles_oriented(ring)` / `rays_singing(ring)`
  — scoring functions used to narrow the search to the sealed seating.
- `solve_rose_seating()` — applies the laws in authority order
  (symmetry+kinship, colour, symbolism) and returns the surviving
  ring(s) — one, in practice.
- `rose_seating()` — the sealed `config.cube.ROSE_24_SEATING` as
  `RoseSeat` objects.
- `calendar_seating(inverted=False)` — the Calendar-12 as `CalendarArm`
  objects, computed fresh (never stored).
- `cell_color(coords)` — a cell's hex colour: the six sealed Rose hues
  for poles, the palette accent for the centre, the channel-average of
  the poles it stands between for everything else.
- `find_pole(name)` — the `(axis, end)` whose luminous name matches, or
  `None`.

## Classes

### RoseSeat
Frozen: `ray` (0..23), `hour`, `star` ("0"/"+15"/"-15"), `hue_index`,
`cell`, `axis`. Properties: `angle_deg` (`ray * 15.0`), `sings` (True
when the ray's own hue is one of the poles its seat carries).

### CalendarArm
Frozen: `month`, `wedge`, `family` (primary/secondary/tertiary), `axis`,
`inner`/`outer` (the two ends, by radius). Properties: `angle_deg`
(`wedge * 30.0`), `hour` (`(12 + 2*wedge) % 24`).

## Design Decisions

- **Pure and Qt-free.** No wall clock, no widgets — the seatings are
  facts about a cube, not about a running clock.
- **The search is re-run by the tests, not at import.** The sealed
  seating is a constant in config; `solve_rose_seating()` proves it —
  startup stays free while the constant cannot drift undetected.
- **Nothing derivable is stored** (root Rule #19): families, indices,
  ray hues, and the Calendar's entire twelve arms are computed from
  coordinates, never enumerated by hand.
