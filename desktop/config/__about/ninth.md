# Ninth

**Script:** [Ninth (script)](../ninth.py) · **Flow:** [diagram](../__flow/ninth.md)

## Purpose

THE NINTH — the seat outside the circle. Eight bodies ride the dial; the
Ninth stands outside them (CANON.md, "The Ninth — Outside the Circle"; the
owner's 8+1 doctrine of 2026-07-14). Everything that seat needs, and
nothing else.

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

- **`WEEKDAY_THEME_NINTHS`** — theme → (display name, plate), derived
  from THE REGISTRY. Themes absent from it run DUAL-only: two faces, no
  Ninth. The zodiac-only ninths (the Chinese Cat, Ophiuchus) stay out on
  purpose — they carry no weekday Sunday duality.
- **The two ALT tables** — `WEEKDAY_THEME_NINTH_EASTER_EGG` (THE PANGEA
  EASTER EGG: Pangea instead of Zealandia when the sky is doing
  something on the traveled day) and `WEEKDAY_THEME_NINTH_NIGHT` (THE
  DYAD'S NIGHT FACE).
- **`NINTH_MECHANISMS` / `NINTH_MECHANISM_KINDS`** — THE DOUBLE NINTH
  LAW's dispatch: a theme may mount two faces contending for the ONE
  seat only with a DEFINED alternation mechanism (`easter_egg`,
  `daynight`, `term_weekly`), and every reader shows only the currently
  active face. `tests/test_ninth_mechanisms.py` fails the build if a
  mechanism is named outside the vocabulary.
- **`CENTER_WINDOW_HOURS`** — THE DUAL/NINTH TIME WINDOW: half an hour
  either side of the day's SOLAR anchors (never wall-clock), i.e. solar
  11:30–12:30 and 23:30–00:30.

## Connections

### Uses
- [The Registry](../registry/___registry.md) — `registry.NINTHS`,
  `registry.NINTH_EASTER_EGG`, `registry.NINTH_NIGHT`,
  `registry.MECHANISMS`. No other sibling is imported.

### Used by
- [Render (folder)](../../render/___render.md) — `render.ninths`, the
  compositor's centre seat, the tooltips
- [Pantheon](pantheon.md) — the rotating-art cadence override
- [App (folder)](../../app/___app.md) — the Encyclopedia's ninths pass
- `shared/research/build_roster.py` — the generated roster

## Design Decisions

- **The time window is not geometry.** It decides WHICH FACE the centre
  seat wears, and it is read by the same `render.ninths` code as the
  tables above it — so it belongs here, not in `config/dial.py`.
- **The tables are derived, not declared.** THE REGISTRY holds one entry
  per theme and computes each of these in a single assignment; this
  module names them and documents the doctrine each one serves.
