# Eras

**Script:** [Eras (script)](../eras.py) · **Flow:** [diagram](../__flow/eras.md)

## Purpose

ERA NOTATION & THIRD CALENDARS — how a year is WRITTEN. One subject,
whole: the notation the official year wears, the modes that decide which
year form the dial prints at all, the named eras, and the third calendars
a user may set beside the official one.

Layer: config — pure Python, no Qt, no wall clock.

## Why it exists

`config/constants.py` carried **38 top-level sections** — app identity,
era notation, weekday bodies, pointer geometry, ring finishes, zodiac,
translation languages, UI scale, seating — under one docstring. That is a
junk drawer, not a directory: nobody could say what the module was ABOUT,
and every session that needed one constant read past thirty-seven
subjects it did not care about. The [OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md)'s
R15 asked for a topic split; the owner ruled on **2026-08-19**, naming
each destination module himself, and this file is one of them.

The move was mechanical and total: each section travelled WHOLE, with
its comments, and every caller was repointed to the real module. **No
re-export shim was left behind** (`rules/CODE.md` — No backward
compatibility), and `config/constants.py` was deleted in the same round.

## Contents

- **Notation** — `ERA_NOTATIONS` / `ERA_NOTATION_TITLES` (`bce_ce`
  default, or `bc_ad`); it governs ONLY the official year form's labels.
  Positive years render bare, as the world writes them.
- **Which form shows** — `EARTH_LABEL_MODES`, `Z_MODES`,
  `Z_MODE_TITLES`.
- **Named eras** — `ERA_NAMES`, `ANNO_LUCIS_OFFSET` / `ANNO_LUCIS_LABEL`,
  `AGE_OF_LIGHT_START_YEAR` / `AGE_OF_LIGHT_END_YEAR`.
- **The third calendars** — `THIRD_ERAS` and its four parallel tables:
  `THIRD_ERA_TITLES` (menu names), `THIRD_ERA_OFFSETS` (epoch shifts),
  `THIRD_ERA_LABELS` (the printed form) and `THIRD_ERA_NOTES` (what the
  Encyclopedia says about each). Their two epoch constants —
  `MAYA_EPOCH_JDN` and `OLYMPIAD_EPOCH_YEAR` — sit beside them, with
  `GREGORIAN_CYCLE_YEARS` and `PROXY_WINDOW_FIRST` for the proxy window.
- **What a date is written FOR** — `LATITUDE_RANGE`, `LONGITUDE_RANGE`
  and `CITY_NAME_TRANSLITERATIONS`: the bounds and spellings of the
  place the year is being written for.

## Connections

### Uses
- nothing — a leaf module.

### Used by
- [Data (folder)](../../data/___data.md) — the location repository and
  the Deep Time year forms
- [App (folder)](../../app/___app.md) — Settings' era and calendar
  pickers, Time Travel, the settings store's validation

## Design Decisions

- **Five parallel tables, not one table of records.** The four
  `THIRD_ERA_*` tables are keyed by the same `THIRD_ERAS` tuple and were
  written that way in the original section; folding them into one dict
  of dicts would be a real refactor with its own before/after proof, and
  this round moved code without changing it.
- **The coordinate ranges are not geometry.** They bound the INPUT a
  year is written for (where on Earth), which is this module's subject,
  not the dial's.
