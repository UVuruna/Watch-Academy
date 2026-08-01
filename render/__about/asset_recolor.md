# Asset Recolor

**Script:** [Asset Recolor (script)](../asset_recolor.py) · **Flow:** [diagram](../__flow/asset_recolor.md)

## Purpose
Disk-cached recolors derived from a single master file: the ring
letter's GOLD/SILVER/BRONZE finish, the subdial plate's bezel/field
recolor, and the public door to `AssetCache`'s TRITONE tint. A surgical
sibling of [Assets](assets.md) (God-File Split Phase 2), which keeps
`AssetCache` itself at its own unchanged import path.

**The metal-variant family is LAZY** (owner order 2026-07-26, "the
Encyclopedia BLOCKED the main thread for minutes"): naming a variant
and building its pixels are two separate steps — `metal_variant_path`
records a (source, metal) recipe in a module ledger with zero pixel
work; `ensure_variant` materializes a recorded, still-missing variant
on first actual use, from any thread (QImage end to end). A source
missing from disk, or a cache write failure, degrades gracefully to the
original/master path rather than crashing (Rule #1).

## Connections

### Uses
- [Assets](assets.md) — `AssetCache._recolored`, `AssetCache._tinted`
  (the recolor doors this module wraps in a disk-cached, path-in/
  path-out interface)
- [Config (folder)](../../config/___config.md) — `paths` (`art_file`,
  `metal_shade`, `settings_path`), `defaults`, `profiling`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `letter_metal_file`
  (ring letter finish at paint time)
- [Asset Variants](asset_variants.md) — `_recolored_plate`
  (`subdial_plate_file`'s recolor step), `tinted_pixmap`
  (`eclipse_solar_type_icon`'s annular tint) — the reverse edge the
  split created
- [Compositor](compositor.md) — `metal_variant_file` (hover-card/
  legend `<img>` tags, which embed file paths, not pixmaps)
- [Art Warm](art_warm.md) — `pending_art()`, `ensure_variant()` (the
  background drain)
- `app.encyclopedia`, `app.encyclopedia_warm`, `app.controller`,
  `app.tray` — `metal_variant_path`/`ensure_variant`/`variant_pending`
  (Encyclopedia look-cycle and warm sweep), `letter_metal_file` (skin
  assembly), `tinted_pixmap` (the per-watch tray icon tint)

## Functions
- `letter_metal_file(path, metal)`: disk-cached ring letter finish,
  derived from the gold master, shade-aware.
- `metal_variant_path(path, metal)`: PURE cache-path computation + a
  ledger recipe entry — no pixel work.
- `ensure_variant(path)`: materializes a recorded variant on first use,
  per-path locked.
- `variant_pending(path)`: recorded-but-not-yet-built test, read by the
  Encyclopedia's exists-or-pending filter.
- `metal_variant_file(path, metal)`: the EAGER door — path + ensure in
  one call, for callers that embed a file path immediately.
- `_recolored_plate(master, finish, tint=None)`: the subdial plate's
  own bezel/field recolor.
- `tinted_pixmap(source, tint)`: the public door to the TRITONE
  gradient-map recolor.

## Design Decisions
- **Two-phase lazy recolor, not eager.** Every variant is NAMED at
  settings/skin-assembly time and BUILT only on first actual paint or
  embed — the split that ended the multi-minute Encyclopedia block.
- **Every derived path is disk-cached**, keyed by the source, the
  active shade and `defaults.METAL_SWAP_VERSION`, so a shade switch or
  a future recolor-math change never serves a stale PNG.
