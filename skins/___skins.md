# skins/

Skin identity — Qt-free so it is pytest-testable. All rendering is driven
by `DEFAULT_SKIN` in [Config (folder)](../config/___config.md), an
instance of this package's typed dataclasses.

A skin is a folder under `assets/skins/<name>/` (bundled) or
`%APPDATA%/DOMY Watch/skins/<name>/` (user drop-in). Exactly SIX
override-able logical units (closed set): `background`, `hexagram`,
`ring`, `weekday_set`, `year_marker`, `hands`. Ring letters are per-skin
(may be blank). Hand pivot fractions are MANDATORY whenever hands are
defined.

## Files

### `manifest.py` — Typed Skin Definition
The per-unit dataclasses (`SkinDefinition` + specs). See
[Manifest](manifest.md).

Dial pointer variants (implemented; user-selectable from the tray):
**hexa** (6-point — the default), **cross** (4-point, arms shaped like
octa arms with gaps) and **octa** (8-point). The pointer sets the
palette size (cross = 4 hues × 90°, hexa = 6 × 60°, octa = 8 × 45° —
the Aura wedges and the Star diamonds share ONE palette preset:
hexa/octa in "paint" and "light" styles, cross with its single seasons
palette) and the weekday slot layout: hexa centers the Sun, cross pairs
bodies on three arms (the next-upcoming day wins a shared slot;
Wednesday sits alone at the bottom), octa seats one body per arm with a
user-selected info slot (time/date/day length/zodiac) on the bottom
arm. A pack's `skin.json` may declare the top-level display scalars
(`pointer`, `umbra_contrast`, `palette_style`, `solar_rotation`,
`octa_slot`), but the user's tray choice always wins.

### `packs.py` — skin.json Load/Merge/Serialize
Partial packs merge unit-by-unit onto the DOMY base (MORPH ships only
its ring); `SkinValidationError` lists ALL problems at once; the DOMY
`skin.json` itself is serialized from `DEFAULT_SKIN`, so config stays
the single source of truth.

### `resolver.py` — Skin Resolver
Discovers packs in bundled `assets/skins/` and
`%APPDATA%/DOMY Watch/skins/`; `resolve(name)` returns the merged
definition; unknown names and broken packs raise visibly (the app then
offers the built-in DOMY, never falls back silently).

### `validate.py` — CLI
`python -m skins.validate <folder>` — check a pack without launching the
app (manifest problems, then the merged-asset sweep).

## Connections

### Uses
- Nothing yet (manifest is dependency-free); M5 adds
  [Config (folder)](../config/___config.md) paths

### Used by
- [Config (folder)](../config/___config.md) — `DEFAULT_SKIN` instance
- [Render (folder)](../render/___render.md) — layers read the specs
- [App (folder)](../app/___app.md) — settings dialog (M6)
