# Zodiac

**Script:** [Zodiac (script)](../zodiac.py) · **Flow:** [diagram](../__flow/zodiac.md)

## Purpose

ZODIAC & CHINESE CALENDAR — the two sign systems. Both answer the same
question ("which sign is this instant in") and both are ridden by the same
seats, so they were one section and stay one module.

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

- **Chinese** — `CHINESE_ANIMALS` and `CHINESE_ELEMENTS` (the
  sexagenary cycle: the animal repeats every 12 years, the element every
  10), `CHINESE_NEW_YEAR_WINDOW` and `CHINA_UTC_OFFSET_HOURS` (the year
  starts at the new moon between Jan 21 and Feb 20, China time),
  `CHINESE_MONTH_BRANCH_ANIMALS`, `CHINESE_BRANCH_TERMS` and
  `chinese_branch_span()` — the solar-term bounds of each branch month.
- **Western** — `ZODIAC_SIGNS` and `ZODIAC_SPAN_DEG`.
- **THE THIRTEENTHS** — `THIRTEENTHS` (Ophiuchus and Sol, the signs a
  thirteen-seat mount adds), `AXLE_ALWAYS_CENTERS` (the axle rule),
  `OPHIUCHUS_WINDOW`, `SOL_WINDOW` and `MODRENIK_WINDOW_HALF_DAYS`.

## Connections

### Uses
- nothing — a leaf module.

### Used by
- [Calendar Mounts](calendar_mounts.md) — the twelve wedges the signs
  ride, and the axle
- [Core (folder)](../../core/___core.md) — the ascendant and the
  chinese-calendar computation
- [Render (folder)](../../render/___render.md) — the mount wedges and
  their tooltips
- [App (folder)](../../app/___app.md) — the Encyclopedia and the
  Watch Face slot pages
- `shared/research/build_roster.py` — the sign and animal rosters

## Design Decisions

- **One module for two systems, on purpose.** They are read together
  (a mount may carry either; the ascendant readout offers both) and the
  thirteenth of each is the same design idea. Two modules would have
  meant two imports at every seat that offers a choice.
- **The WEDGES are not here, and neither are the STYLES.** Geometry is
  `config/calendar_mounts.py`; what a slot draws a sign in is
  `config/complications.py`.
