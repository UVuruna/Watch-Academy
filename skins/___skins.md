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

Owner-specified dial pointer variants for M5 skins: **hexa** (6-point —
points at both solstices, equinoxes fall between the vertices; the current
default), **cross** (4-point — points at both solstices AND both
equinoxes) and **octa** (8-point — solstices + equinoxes + midpoints).
The pointer shape also sets HOW MANY colors measure the day's periods:
cross = 4 hues × 90°, hexa = 6 hues × 60°, octa = 8 hues × 45° — the
background wedges and the star diamonds share the same palette count.
The year wheel already guarantees each season spans exactly 90° with a
per-season daily rate.

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
