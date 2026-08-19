# Ring

**Script:** [Ring (script)](../ring.py) · **Flow:** [diagram](../__flow/ring.md)

## Purpose

THE RING VOCABULARY's own tables. The ring is four different things and
never variants of one (project law, [The Dial](../../../docs/DIAL.md#ring-vocabulary)):
JEWELS, NUMERALS, MINUTES and the CROWN. This module is the ring's
declarative half — everything it is MADE of. Its geometry stays in
[Dial](dial.md), which owns everything measured in pixels.

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

- **Finishes and metals** — `RING_FINISHES`, `RING_THEMATIC_SHADES`,
  `METAL_SHADE_NAMES` (the shade ramps every metal-bearing surface
  reads), `METAL_SHADE_DEFAULT`, `METAL_SHADE_TITLES`.
- **Subdial plates** — `SUBDIAL_STYLES`, `SUBDIAL_SETS`,
  `SUBDIAL_SET_DEFAULT`, `SUBDIAL_SET_TITLES`.
- **Outers, inners and the Eye** — `RING_OUTERS` (which hour fields a
  ring layout leaves EMPTY for letters), `RING_OUTER_LOCK` (each
  bundled preset is locked to exactly one outer), `RING_INNERS`,
  `RING_INNER_PRESET_DEFAULT`, `RING_INNER_DEFAULT`, and the Eye of
  Providence's `RING_EYE_GLYPH` / `_SHINE_FILE` / `_SHINE_DEFAULT` /
  `_SHINE_ENLARGE`.
- **Letters** — `LETTER_PLATE_GROUPS` and `LETTER_PLATE_FILES`, the
  glyph→plate tables THE ONE PLATE LAW resolves every drawn glyph
  through (`render.letter_plates` is the single door), with the Greek
  twins and own-plate sets behind them; `RING_CROWN_TEXT_CHARSET` bounds
  what a crown arc may spell.
- **Theme metal looks** — `METAL_THEMES` (derived from THE REGISTRY:
  which themes wear a metal at all), `THEME_METALS`,
  `THEME_METALS_OVERRIDE` and the `theme_metals()` gate every caller
  must read rather than the flat tuple.

## Connections

### Uses
- [The Registry](../registry/___registry.md) — `registry.METAL_THEMES`,
  the one table THE REGISTRY owns. No other sibling is imported.

### Used by
- [Paths](paths.md) — the metal-shade and subdial-set art directories
- [Dial](dial.md) — quoted by name in its geometry comments
- [Render (folder)](../../render/___render.md) — the ring layer, the
  letter plates, the asset variants and recolor
- [App (folder)](../../app/___app.md) — the Watch Face ring page, the
  Design window, the settings store
- `shared/Database/ring_presets.json` — the six bundled presets name
  `RING_OUTERS` entries and `RING_INNER_PRESET_DEFAULT` directly

## Design Decisions

- **The theme METAL LOOKS are a ring decision wearing a theme's name.**
  They pick which metal a theme's medallions may be tinted to, and the
  tint is the ring family's own machinery — so they live with the metal
  shades rather than with the theme registry.
- **`config/paths.py` may import this module.** `ring.py` imports only
  `config.registry`, which imports only its own leaves, so the chain
  `paths → ring → registry` closes without touching `paths` again.
