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
The year wheel already guarantees each season spans exactly 90° with a
per-season daily rate.

## Planned Files (M5)

### `resolver.py` — Skin Resolver
Discovers `skin.json` packs, merges base ← chosen pack ← per-unit
overrides (`{"skin": name, "params": {...}}`), re-validates the merged
result. Partial manifests (e.g. hands only) are valid as override
sources. A broken override raises visibly — never a silent fallback.

### `validate.py` — CLI
`python -m skins.validate <folder>` — check a pack without launching the
app; `SkinValidationError` lists ALL problems at once.

## Connections

### Uses
- Nothing yet (manifest is dependency-free); M5 adds
  [Config (folder)](../config/___config.md) paths

### Used by
- [Config (folder)](../config/___config.md) — `DEFAULT_SKIN` instance
- [Render (folder)](../render/___render.md) — layers read the specs
- [App (folder)](../app/___app.md) — settings dialog (M6)
