# Week Registry

**Script:** [Week Registry (script)](../week.py) · **Flow:** [diagram](../__flow/week.md)

## Purpose

THE WEEK REGISTRY — the **6+3 kind**: six weekday seats, then Sunday's
three (the Ruler who holds the centre by day, the Servant who holds it
by night, the Ninth who takes the seat inside the solar half-hour
windows). A theme with no Ninth runs dual-only. 35 entries today.

Layer: config — pure DATA. This module imports nothing at all.

## Contents

- **`MENU_TOP` / `MENU`** — the picker's top entries and its kinship
  groups in display order. A theme's group is DERIVED from this and
  declared nowhere else.
- **`WEEK`** — key → the whole contract:
  - `title`, `art`, `articles`, `blurbs` — required.
  - `seats` — the six weekdays, keyed by the ENGLISH DAY NAME, each
    carrying its planetary `body` as the seat's second name (both
    conventions are canon, owner 2026-08-04), plus `name` and `stem`,
    and `rotates` where the seat holds a roster.
  - `sunday` — `name` (the seat's own label, which most themes print as
    both faces), `ruler`, `servant`, `stem`, `servant_plate`, and
    `rotates` / `servant_rotates` where either face turns.
  - `ninth` — `name`, `plate`, optional `alt`/`alt_plate`, optional
    `mechanism` (`easter_egg`, `daynight`, `term_weekly`), optional
    `rotates`. Absent means dual-only.
  - `metals`, `pantheon`, `title_plate` — optional, meaningful by
    absence.
- **`COMPUTED`** — the sentinel for a value the registry refuses to
  freeze. The Continents' stems ARE the dial's own Earth faces and are
  built from `continents.CONTINENTS_REGIONS` at derivation time
  (Rule #19: compute, don't generate).

## Laws

**DEPICTIONS ARE NOT THEMES** (owner decree 2026-08-04). Several ways of
drawing the SAME figures in the SAME seats with the SAME text are one
theme wearing several looks — `planets`, `planet_signs` and
`planets_art` share the article set `planets`. **The STORY decides**:
the Gregorian and the Slavic months hold identical spans and remain two
themes, exactly as the Greek and the Norse gods hold identical days and
remain two.

**AN OCCUPANT IS ALWAYS A LIST** where it can rotate, and the declared
order IS the rotation order. This is load-bearing for the Power cast,
whose Throne, Mirror and Ninth each hold two members and must land on
the same index on any given day.

## Connections

### Used by
- [Registry derivation](__init__.md) — the only reader; every consumer
  goes through the tables it computes
