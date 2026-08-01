# Static Pages

**Script:** [Static Pages (script)](../pages.py) · **Flow:** [diagram](../__flow/pages.md)

## Purpose
WHAT pages exist and which plate each one wears — the seasons, the
sun's turning points, the eras and their calendar strip, both eclipse
families, the four Cube-canon topic sets, and the week/emblem/instrument
tables. No widgets, no clock: these tuples are data the builders next
door walk.

Split out of the old 2,766-line `app/encyclopedia.py` in the Session 27
rework (root Rule #20). The tables moved VERBATIM — their comments carry
the owner decisions that argued every entry, and the entry ORDER of
several of them is a contract.

## Connections

### Uses
- config `archetypes`, `constants`, `pantheon` — art directories and roster tables

### Used by
- [Topic Builders](builders.md), [Topic Tree](tree.md)

## Contracts kept here
- **`_CUBE_ENTRIES`'s ORDER is a contract** — `config/archetypes.py`
  aims the Cube wheels' Spacebar jumps at positions in this run, and
  `tree.cube_target` re-aims them across the four split cards. An
  inserted entry goes at the END, or the wheels are re-aimed in the same
  commit; `tests/test_cube_encyclopedia.py` pins the pairs BY NAME.
- **`_ONE_SOUL_ENTRIES`'s ORDER is a contract** —
  `config/archetypes.py`'s prism-secondary figures address these pages
  by index; `tests/test_one_soul_theme.py` pins both ends.
- **`NINTH_SEAT_PHILOSOPHICAL_NAME`** — "The Unfound" (owner decree,
  round R3); the rejected alternatives (The Uncalled, The Ninth Door,
  The Seeker, The Unclaimed) are argued in the comment beside it.
- **`_ECLIPSE_SOLAR_ENTRIES`/`_ECLIPSE_LUNAR_ENTRIES`'s chapter order**
  must stay in lockstep with `render.compositor`'s own eclipse-category
  order, so the Spacebar jump indexes the active eclipse's chapter correctly.
