# Umbra

**Script:** [Umbra (script)](../umbra.py) · **Flow:** [diagram](../__flow/umbra.md)

## Purpose

THE UMBRA WHEEL — the band of shadow around the dial. It carries the
moon through its lunation, darkens for an eclipse, and marks the STATIONS
the sun and the moon pass. Every name here answers one question: what does
the Umbra look like right now.

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

- **The band itself** — `UMBRA_FORMS`, `UMBRA_SECTION_COUNTS`,
  `UMBRA_CONTRAST_VARIANTS`, `UMBRA_TINT_MODES`, `AURA_OFF_TINT_MODES`.
- **The moon on the band** — `MOON_BAND_MODES` / `MOON_BAND_STYLES` /
  `MOON_DARK_STYLES` / `MOON_TRANSIT_STYLES` and each one's `_DEFAULT`,
  plus `MARKER_POINTER_SHAPES` / `_DEFAULT`.
- **Eclipses** — `ECLIPSE_SOLAR_STYLES` and `ECLIPSE_LUNAR_STYLES` with
  their defaults, `ECLIPSE_BAND_DURATION_H` (how much of the band one
  eclipse claims) and `ECLIPSE_PENUMBRAL_SPAN_RATIO`.
- **Stations** — `MOON_STATION_STYLES` / `_DEFAULT` / `MOON_STATION_GLOW`,
  `SUN_STATION_STYLES` / `_DEFAULT` / `SUN_STATION_SEASONS`,
  `LIFE_STATIONS`, and the two resolvers-as-tables that map an event to
  a station: `MOON_STATION_OF_PHASE` and `SUN_STATION_OF_EVENT`.
- **`MOVING_BODY_MENUS`** — what the right-click menu offers for each
  moving body on the band.

## Connections

### Uses
- nothing — a leaf module.

### Used by
- [Render (folder)](../../render/___render.md) — the Umbra layer, the
  eclipse glow, the marker marks, the asset variants
- [App (folder)](../../app/___app.md) — the menu, the Watch Face
  window's Umbra & Aura page, the settings store

## Design Decisions

- **The largest single section became the largest single move.** 31
  names, 74 logic lines, one banner — and one subject. It was never a
  candidate for further splitting: a style and its `_DEFAULT` are one
  fact, and the station maps are read by the same painter as the styles.
- **The eclipse GLOW is not here.** `config/glow.py` owns the eclipse
  type → render-state machine and the glow windows; this module owns the
  Umbra's own eclipse STYLES — what the band looks like, not how bright
  the halo is.
