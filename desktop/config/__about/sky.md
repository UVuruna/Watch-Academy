# Sky

**Script:** [Sky (script)](../sky.py) · **Flow:** [diagram](../__flow/sky.md)

## Purpose

The sky the dial reads — every invariant of the real sun, moon and year
this instrument reports. It is deliberately NOT `dial.py`: those are the
numbers of the DRAWN face (its geometry and its convention), these are the
numbers of the sky the face is about.

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

- **The sun** — `CIVIL_DEPRESSION` (6° below the horizon for dawn and
  dusk), `HORIZON_ELEVATION_DEG` (−0.833°, the refracted moment the
  disc touches the horizon) and `CIVIL_TWILIGHT_ELEVATION_DEG`.
- **The year wheel** — `YEAR_ANCHOR_ANGLES`, the six UNWRAPPED dial
  angles bracketing one calendar year: previous December solstice,
  spring equinox, summer solstice (the top of the dial after mod 360),
  autumn equinox, December solstice, next spring equinox.
- **The moon** — `SYNODIC_MONTH_DAYS`, the `MOON_PRINCIPAL_WINDOW` in
  which a principal phase name still applies (±half a day),
  `MOON_PHASE_NAMES` (the eight octants in cycle order),
  `MOON_PHASE_FRACTIONS` (the four principal anchors) and
  `MOON_CYCLE_QUARTER`.
- **Deep Time** — `DEEP_TIME_DB_FILENAME`, the optional full-span pack
  the season and moon repositories CHAIN to when the bundled coverage
  runs out. Its own coverage is read from its meta table, never
  hardcoded (Rule #4).
- **Season event names** — `SEASON_EVENT_NAMES` and
  `ZONE_SEASON_EVENT_NAMES`: what each hemisphere and the tropics CALL
  a turning point, because a June solstice is not "summer" south of the
  equator and the tropics read wet and dry rather than four seasons.
- **The tropics** — `TROPIC_LATITUDE_DEG` (23.44°) and
  `TROPICAL_YEAR_DAYS`, the latter used only to synthesise an equinox
  instant just before the bundled anchor span.

## Connections

### Uses
- nothing — a leaf module.

### Used by
- [Core (folder)](../../core/___core.md) — the sun, moon, year-wheel
  and continent computations
- [Data (folder)](../../data/___data.md) — the Deep Time chain
- [Encyclopedia UI](encyclopedia_ui.md) — the twilight diagram
- [App (folder)](../../app/___app.md) — the moon topic, the simulation
  jumps

## Design Decisions

- **The tropics ride with the season names, not with geometry.** Both
  answer "what is this turning point called HERE"; splitting them would
  put one question in two modules.
- **Deep Time's FILENAME lives here, its coverage does not.** The
  filename is a fixed product fact; the coverage is read from the data
  itself, which is Rule #4's whole point.
