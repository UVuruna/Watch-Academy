# Hand Packs

**Script:** [Hand Packs (script)](../hands.py)

## Purpose

Loads HAND PACKS (owner spec 2026-07-12): a folder of `hours.*`,
`minutes.*`, `seconds.*` images pointing UP plus `hands.json` — the
display `name`, the per-hand `pivot` (`x` from the left, `null` = the
image middle; `y` in pixels FROM THE BOTTOM) and the bottom-up
`z_order` (default `hours, minutes, seconds`). Bundled packs live under
`assets/instrument/hands/`; the user's own packs live beside the
settings file, in a `hands/` subfolder the Settings builder writes.
Validation is loud (Rule #1): a missing image, a malformed `hands.json`
or a bad `z_order` raises naming the offending pack.

Sizing is NOT decided here — the renderer measures tip-to-pivot length
from the image and pivot alone.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `paths.assets_dir()` /
  `paths.settings_path()`

### Used by
- [Watch Controller](../../app/__about/controller.md) — `build_skin` resolves
  the chosen pack into `HandsSpec`; the Design ▸ Hands menu lists every
  loaded name
- [Custom Art Section](../../app/settings_dialog/__about/custom_art_section.md)
  — the Custom hands builder validates against and writes user packs

## Functions

- `user_hands_dir()`: where the Settings builder writes new packs
  (`<settings dir>/hands`).
- `hand_packs()`: `name → pack` for every bundled + user pack (`dir`,
  `files{hand: Path}`, `pivots{hand: (x|None, y)}`, `z_order`);
  duplicate names raise loudly.
- `_load_pack(directory)` (private): reads and validates one pack's
  `hands.json` — checks `name`, that all three hand images exist (`.png`
  or `.svg`), that every hand has a `pivot.y`, and that `z_order`
  (if present) is a permutation of `HAND_NAMES`.
