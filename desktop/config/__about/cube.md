# Character Cube — Canon Data

**Script:** [Character Cube (script)](../cube.py) · **Flow:** [diagram](../__flow/cube.md)

## Purpose

The Character Cube's canon TABLE, as data: the thirteen axes with both
their ends, every end's luminous and fallen name, the six poles'
sealed Rose hues, and the two seatings' constants. It is the single
source of the cube's words — nothing here is computed, and nothing
computable is stored here (root Rule #19: the geometry lives in
`core.cube_seating`, which derives families, indices, kinship and
antipodes from these coordinates alone).

The canon it transcribes is `CUBE.md` §The Thirteen Axes: 13 axis
names + 26 extremities × (luminous, fallen) = the 65 sealed terms. The
centre — The One — carries no fall, and its cell is the only one whose
`fallen` is empty.

Layer: config — pure, no Qt, no wall clock.

## Connections

### Uses
- [Palette](palette.md) — `ROSE_PALETTE` supplies the eight hues
  `ROSE_POLE_HUE` indexes into (one palette, never a second copy)

### Used by
- [Archetypes](archetypes.md) — `FIGURE_SETS` and `ROSTER`: the three
  registers and the people who hold each cube seat (`roster_names`)
- [Cube Seating](../../core/__about/cube_seating.md) — derives the
  geometry and proves both seatings against these coordinates
- The project's Cube Seating tests — the golden tests pin every seat

## Classes

### CubeCell
One of the 27 cells: its integer coordinates in `{-1, 0, +1}³` and the
two names the radial law gives it.

#### Attributes
- `coords`: the cell's `(x, y, z)` — X Activation, Y Moral Scope, Z
  Self-Regard; `-1` is the cold pole, `+1` the warm one
- `luminous`: the name of the direction held in measure
- `fallen`: the name of the same direction walked past its measure
  (empty only for The One)

### CubeAxis
One of the thirteen lines through the centre.

#### Attributes
- `name`: the sealed axis name
- `cold`: the cell at the cold end (canon's left-hand column)
- `warm`: the cell at the warm end

## Data Tables

- `AXES` — all thirteen, the Sacred Axis first
- `THE_ONE` — the centre cell `(0, 0, 0)`
- `FIGURE_SETS` — the three registers every seat carries (`archetypal`,
  `historical`, `modern`), declared ONCE here: the roster, the disk
  registers (`<group>/<set>/colored/`) and the Rose's three stars
  (`constants.ROSE_STAR_SETS`) all read this tuple
- `ROSTER` — every human cell → its three sets → `(luminous person,
  fallen person)`; the sealed 108 transcribed from the canon tables,
  plus 48 more edge seats
- `SACRED_TRIO_NAMES`, `THE_ONE_SEAT` — the Sacred Axis's three names
  in reading order
- `SACRED_FIGURES` — the two sacred corners' three registers (the
  principals themselves in the archetypal set, echoes in the other
  two); the centre is deliberately absent
- `ROSE_POLE_HUE` — the six poles' sealed Rose hue INDEX into
  `palette.ROSE_PALETTE`
- `ROSE_24_SEATING` — the 24 human cells in ray order, ray 0 = 12h
- `CALENDAR_WEDGES_BY_FAMILY` — the symmetry law's three groups of arms
  (triangle · opposite triangle · hexagon = the hexagram)
- `CALENDAR_AXIS_ORDER` — which axis of a family takes which of its
  own arms; the SECOND criterion, argued month by month in `CUBE.md`
- `CALENDAR_CENTRE` — the Calendar's centre medallion, `THE_ONE` alone

## Functions

PSEUDOCODE — the two readers of the roster (root Rule #21: algorithms
are described language-neutrally):

    roster(cell, register):
        RETURN the pair (luminous person, fallen person) seated on that cell
        UNKNOWN cell OR register -> RAISE (the grid is complete; a silent
        miss would be a lie)

    sacred_figure(seat, register):
        IF seat is THE CENTRE -> RETURN nothing
            (doctrine: The One contains all six powers without being
             ruled by any, and every human exemplar is ruled by something)
        ELSE -> RETURN that corner's figure in that register

## Design Decisions

- **Coordinates, not colour names.** Every cell is stored as a
  coordinate triple, so kinship, antipodes, family and index are all
  derivable; the hue is a lookup, never a stored attribute of a seat.
- **The canon file is the source, this file the transcription.** No
  figure is invented here.
- **One seat per person, one exception SHAPE.** A figure may hold two
  cells only when they differ in X alone — the same seat with the
  depth axis dropped, which is what the Character wheel is.
- **The seatings are results, not taste.** `ROSE_24_SEATING` is the
  single survivor of an exhaustive search under five laws, and the
  tests re-run that search rather than trusting the constant. The
  Calendar-12 seating is not stored at all — it is computed from the
  two laws above.
