# Hand Packs

**Script:** [Hand Packs (script)](hands.py)

## Purpose
Loads the HAND PACKS (owner spec 2026-07-12): a pack is one folder
holding `hours.*`, `minutes.*`, `seconds.*` (images pointing UP; the
bundled CLASSIC keeps its SVGs, user packs are PNG) plus `hands.json`
with the display `name`, the per-hand `pivot` (rotation center —
`x` from the left, `null` = the image middle for symmetric hands;
`y` in pixels FROM THE BOTTOM) and the `z_order` (draw order
bottom-up, default `hours → minutes → seconds`).

Bundled packs live in `assets/hands/<pack>/`; the user's own in
`%APPDATA%/DOMY Watch/hands/<pack>/` (the Settings builder writes
them). Validation is loud: a missing image, a malformed json, an
unknown z-order entry or a duplicate name raises with the offending
pack named.

Sizing is NOT stored here — the renderer measures TIP-TO-PIVOT
lengths (image height − pivot y) and scales so the seconds tip
touches the ring, the minutes tip the minute arrows, and the hours
follow the pack's own hours/minutes ratio
(`defaults.HAND_*_REACH_FRACTION`).

## Connections

### Uses
- Shared JSON loading ([Data (folder)](___data.md))
- [Config (folder)](../config/___config.md) — bundled/user directories

### Used by
- [App Controller](../app/controller.md) — `build_skin` resolves the
  chosen pack into `HandsSpec` (image sizes read there, Qt side); the
  Design ▸ Hands menu lists every loaded name
- [Settings Dialog](../app/settings_dialog.md) — the Custom hands
  builder validates against and writes user packs

## Functions

- `hand_packs()`: name → `{dir, files{hand: Path}, pivots{hand:
  (x|None, y)}, z_order}` for every bundled + user pack
- `user_hands_dir()`: where the Settings builder writes new packs
