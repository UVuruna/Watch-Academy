# skins/

**Planned — implemented in M5.** Skin identity, validation and merging —
Qt-free so it is pytest-testable. Until M5 all rendering is driven by
`DEFAULT_SKIN` in [Config (folder)](../config/___config.md) (typed against
this module's dataclasses from day one, so M5 "extraction" is serialization,
not redesign).

A skin is a folder under `assets/skins/<name>/` (bundled) or
`%APPDATA%/DOMY Watch/skins/<name>/` (user drop-in) with a `skin.json`
manifest. Exactly SIX override-able logical units (closed set):
`background`, `hexagram`, `ring`, `weekday_set`, `year_marker`, `hands`.
Ring letters are per-skin (may be blank). Hand pivot fractions are MANDATORY
whenever hands are defined. Partial manifests (e.g. hands only) are valid as
override sources. A broken override raises visibly — never a silent fallback.

## Planned Files

### `manifest.py` — SkinDefinition + Validation
Per-unit dataclasses; `load_skin(folder)`; `SkinValidationError` that lists
ALL problems at once.

### `resolver.py` — Skin Resolver
Discovers packs, merges base ← chosen pack ← per-unit overrides
(`{"skin": name, "params": {...}}`), re-validates the merged result.

### `validate.py` — CLI
`python -m skins.validate <folder>` — check a pack without launching the app.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — paths, DEFAULT_SKIN

### Used by
- [Render (folder)](../render/___render.md) — consumes `ResolvedSkin`
- [App (folder)](../app/___app.md) — settings dialog (M6)
