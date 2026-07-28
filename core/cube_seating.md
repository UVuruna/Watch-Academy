# Cube Seating — the geometry of the two display plans

**Script:** [Cube Seating (script)](cube_seating.py)

## Purpose

The Character Cube's pure geometry, and the two seatings Session 26
solved with it: **Calendar-12** (twelve arms, one human axis each) and
**Rose-24** (twenty-four rays, one human seat each). Everything the
coordinates can decide is decided here — kinship, antipodes, families,
indices, ray hues — so that [Character Cube](../config/cube.md) can stay
a table of words.

## Connections

### Uses
- [Character Cube](../config/cube.md) — the thirteen axes, the sealed
  pole hues and the two seatings' constants

### Used by
- [Cube Seating Tests](../tests/___tests.md) — re-runs the whole search
  and pins every seat
- [Research (folder)](../research/___research.md) — the offscreen
  preview generator draws both seatings from here

## The laws

### THE FIRST LAW — symmetry (owner decree 2026-07-28)
*"Primarna je simetrija, sekundarna je simbolika."* Symmetry decides
which KIND of axis stands where; symbolism only decides which axis of
that kind. The families count 3 face axes, 6 edge axes and 3 human vertex
axes, so both wheels wear the same regular figure — two opposed
equilateral triangles with a hexagon between them, which is the hexagram.

```
ROSE      ray % 4 == 0 -> a POLE      (12h 16h 20h 24h 4h 8h)
          ray % 4 == 2 -> a CORNER    (14h 18h 22h  2h 6h 10h)
          any odd ray  -> an EDGE     (twelve, one every 30 degrees)

CALENDAR  the pure-primary arms  (June 12h, October 20h, February 4h) -> the 3 face axes
          the mixed-primary arms (August 16h, December 24h, April 8h) -> the 3 vertex axes
          the six remaining arms                                      -> the 6 edge axes
          (INVERTED: the two triangles swap)
```

### The one-grade law (kinship)
Two cells are KIN when they differ in exactly one coordinate, by exactly
one grade. One step around a wheel therefore changes exactly ONE axis by
ONE grade — the generalisation of the Prophecy wheel's "neighbouring arms
differ in exactly one axis".

```
KIN(a, b) := the multiset |a - b| is {0, 0, 1}
```

### The antipodal law
Ray *k* and ray *k+12* hold the two ends of ONE axis: every extreme faces
its exact opposite THROUGH God, and the dial's axle IS The One.

### The parity theorem
Each kinship step changes a cell's nonzero-count by one, so the kinship
graph is bipartite: faces and vertices on one side (14 cells), edges on
the other (12). A closed ring must alternate, so it needs the two sides
equal — **no ring can seat all 26 cells.** Removing two odd-side cells
balances it at 12 + 12, and canon had already removed exactly two: the
Sacred vertices. Geometry does not choose WHICH two; it only says that
without such a removal the human circle cannot close.

### The colour laws (the Rose)
1. Each primary axis holds its own sealed hue DIAGONAL (X cyan ↔ orange,
   Y yellow ↔ purple, Z green ↔ rose). Under the symmetry law this comes
   free — the six pole rays ARE the six cube-coloured rays.
2. Each of the six poles sits on its own hue — 4 of 6 is the proven
   ceiling, and the pair that misses is always one axis's own.

### The symbolism (the second criterion, used only to break ties)
The crown on Sunday's Ruler (Wise Statesman on red 18h, Sacrificial
Protector on blue 06h), and the doubling on the invisible axis (red and
blue hold Activation's two households as their second home).

## Algorithms

### `antipodal_rings()` — the exhaustive search
```
FOR each path c[0..11] of twelve cells, one from each human axis:
    require rank(c[k]) == the symmetry law's rank for ray k
    require KIN(c[k], c[k+1]) for every step
    require KIN(c[11], -c[0])            # the ring closes through the antipode
    emit c[0..11] + (-c[0] .. -c[11])    # ray k+12 is ray k's antipode
```
48 ray assignments survive; with the symmetry law switched off (as the
tests do, to measure what it costs) 1056 do.

### `calendar_seating(inverted)` — computed, never stored
```
FOR each family in primary, secondary, tertiary:
    arms := that family's wedges       # the triangle / triangle / hexagon
    IF inverted -> swap the two triangles
    FOR each (arm, axis name) zipped in the family's argued order:
        month := the Almanac wheel's month at that wedge
        outward end := the end whose first non-zero of (x, z, y) is +1
```

## Classes

### `RoseSeat`
One ray of the Rose-24.

#### Attributes
- `ray`: 0..23, ray 0 = 12h, one ray every 15° clockwise
- `hour`: the dial hour the ray points at
- `star`: which of the three octa stars owns it (`0`, `+15`, `-15`)
- `hue_index`: index into `defaults.ROSE_PALETTE`
- `cell`, `axis`: the seat and the axis it ends

### `CalendarArm`
One arm of the Calendar-12.

#### Attributes
- `month`, `wedge`, `hour`: the Gregorian month, its Almanac wedge
  (0 = June) and the dial hour that wedge is centred on
- `family`: primary / secondary / tertiary — which of the figure's three
  groups of arms this one belongs to
- `axis`, `inner`, `outer`: the axis and its two ends, by radius

## Design Decisions

- **Pure and Qt-free.** No wall clock, no widgets — the seatings are
  facts about a cube, not about a running clock.
- **The search is re-run by the tests, not at import.** The sealed
  seating is a constant in config; `solve_rose_seating()` proves it. That
  keeps startup free while leaving no room for the constant to drift.
- **Nothing derivable is stored** (root Rule 19): families, indices, ray
  hues, the Calendar's entire twelve arms are computed from coordinates.
