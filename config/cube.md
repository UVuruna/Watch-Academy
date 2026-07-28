# Character Cube — Canon Data

**Script:** [Character Cube (script)](cube.py)

## Purpose

The Character Cube's canon TABLE, as data: the thirteen axes with both
their ends, every end's luminous and fallen name, the six poles' sealed
Rose hues, and the two seatings' constants. It is the single source of
the cube's words — nothing here is computed, and nothing computable is
stored here (root Rule 19: the geometry lives in
[Cube Seating](../core/cube_seating.md), which derives families,
indices, kinship and antipodes from these coordinates alone).

The canon it transcribes is [The Cube Canon](../CUBE.md) §The Thirteen
Axes: 13 axis names + 26 extremities × (luminous, fallen) = the 65
sealed terms. The centre — The One — carries no fall, and its cell is
the only one whose `fallen` is empty.

## Connections

### Uses
- [Config (folder)](___config.md) — `defaults.ROSE_PALETTE` supplies the
  eight hues the pole map indexes into (one palette, never a second copy)

### Used by
- [Cube Seating](../core/cube_seating.md) — derives the geometry and
  proves both seatings against these coordinates
- [Cube Seating Tests](../tests/___tests.md) — the golden tests pin every
  seat

## Data

### `CubeCell`
One of the 27 cells: its integer coordinates in `{-1, 0, +1}³` and the
two names the radial law gives it.

#### Attributes
- `coords`: the cell's `(x, y, z)` — X Activation, Y Moral Scope,
  Z Self-Regard; `-1` is the cold pole, `+1` the warm one
- `luminous`: the name of the direction held in measure
- `fallen`: the name of the same direction walked past its measure
  (empty only for The One)

### `CubeAxis`
One of the thirteen lines through the centre.

#### Attributes
- `name`: the sealed axis name
- `cold`: the cell at the cold end (canon's left-hand column)
- `warm`: the cell at the warm end

### Tables
- `AXES` — all thirteen, the Sacred Axis first
- `THE_ONE` — the centre cell `(0, 0, 0)`
- `ROSE_POLE_HUE` — the six poles' sealed Rose hue INDEX into
  `defaults.ROSE_PALETTE` (CUBE.md §The Sunday axis: X wears cyan ↔
  orange, Y yellow ↔ purple, Z green ↔ rose)
- `ROSE_24_SEATING` — the 24 human cells in ray order, ray 0 = 12h
- `CALENDAR_WEDGES_BY_FAMILY` — the symmetry law's three groups of arms
  (triangle · opposite triangle · hexagon = the hexagram)
- `CALENDAR_AXIS_ORDER` — which axis of a family takes which of its own
  arms; the SECOND criterion, argued month by month in CUBE.md

## Design Decisions

- **Coordinates, not colour names.** Every cell is stored as a coordinate
  triple, so kinship, antipodes, family and index are all derivable; the
  hue is a lookup, never a stored attribute of a seat.
- **The seatings are results, not taste.** `ROSE_24_SEATING` is the
  single survivor of an exhaustive search under five laws, and the tests
  re-run that search rather than trusting the constant. The Calendar-12
  seating is not stored at all — it is computed from the two laws above.
