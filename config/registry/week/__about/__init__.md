# Week Registry (package)

**Script:** [Week Registry (script)](../__init__.py) · **Flow:** [diagram](../__flow/__init__.md)

## Purpose

THE WEEK REGISTRY — the **6+3 kind**. Six weekday seats, then Sunday's
three: the Ruler who holds the centre by day, the Servant who holds it
by night, the Ninth who takes the seat inside the solar half-hour
windows. A theme with no Ninth runs dual-only. 35 themes today.

## Contents

- **`ORDER`** — the dial's registration order, what
  `constants.WEEKDAY_THEMES` has always been. Kept explicitly so the
  file layout can never silently reorder a user-visible list.
- **`WEEK`** — `{key: entry}` assembled from the group modules in
  `ORDER`. A theme missing from its group module raises here rather
  than vanishing from the dial.
- **`MENU_TOP` / `MENU`** — the picker's top entries and kinship groups
  in display order; a theme's group is DERIVED from this and declared
  nowhere else.

## The shape of one entry

Required: `title`, `art`, `articles`, `blurbs`, `seats` (the six
weekdays), `sunday`. Optional and meaningful by absence: `metals`,
`ninth`, `pantheon`, `title_plate`.

A seat is keyed by the **English day name** and carries its planetary
`body` as the seat's second name — both conventions are canon (owner
2026-08-04). An occupant is always a **list** where it can rotate:
`rotates` names the whole roster, canonical member first, and declared
order IS rotation order.

## The group files

| Module | Themes |
|--------|--------|
| [Celestial bodies](celestial_bodies.md) | 5 |
| [Mythologies](myth.md) | 6 |
| [Faith](faith.md) | 5 |
| [Cultures & crafts](crafts.md) | 4 |
| [Animal societies](societies.md) | 3 |
| [The Inner Wheel](inner_wheel.md) | 3 |
| [Gaming](gaming.md) | 6 |
| [Films](films.md) | 3 |

## Connections

### Used by
- [Registry derivation](../../__about/__init__.md)
