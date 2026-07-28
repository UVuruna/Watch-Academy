# Static Pages

**Script:** [Static Pages (script)](pages.py)

## Purpose
WHAT pages exist and which plate each one wears — the seasons, the sun's
turning points, the eras and their calendar strip, both eclipse families,
the four Cube-canon sets, and the week/emblem/instrument tables.

No widgets, no clock: these tuples are data the builders walk.

## Connections

### Used by
- [Topic Builders](builders.md), [Topic Tree](tree.md)

## Contracts kept here
- **`_CUBE_ENTRIES`' ORDER is a contract** — `config/archetypes.py` aims
  the Cube wheels' Spacebar jumps at positions in this run, and
  `cube_target` re-aims them across the four cards. An inserted entry
  goes at the END, or the wheels are re-aimed in the same commit.
- **`NINTH_SEAT_PHILOSOPHICAL_NAME`** — "The Unfound" (owner decree,
  round R3), with the rejected alternatives argued in the comment beside
  it.
