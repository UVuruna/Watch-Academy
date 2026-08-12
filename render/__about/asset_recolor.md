# Asset Recolor

**Script:** [Asset Recolor (script)](../asset_recolor.py) · **Flow:** [diagram](../__flow/asset_recolor.md)

## Purpose
Disk-cached recolors derived from a single master file: the ring
jewel's GOLD/SILVER/BRONZE finish, the subdial plate's bezel/field
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

## `ring_recolored_image`

A COMPUTED band plate ([Numeral Bands](numeral_bands.md)) is not a file, so
it cannot go through `AssetCache.pixmap_by_height` — but it must still
answer the Ring TINT and Ring SATURATION sliders exactly as the printed
plate it replaced did. This is that one door: the tritone tint first, the
HSV saturation after, the same order `pixmap_by_height` uses (Rule #5).
Both no-ops return the image untouched, which is the common case — the
tint is `None` and the saturation `1.0` on every default skin, so a plain
band never pays for it.

### Uses
- [Assets](assets.md) — `AssetCache._recolored`, `AssetCache._tinted`
  (the recolor doors this module wraps in a disk-cached, path-in/
  path-out interface)
- [Raster Store](raster_store.md) — `ensure_variant` and
  `_recolored_plate` write atomically (owner crash 2026-07-31: the GUI
  thread's unlocked `exists()` check raced a direct `QImage.save` and
  painted a truncated PNG)
- the STALE NOTIFIER (`set_art_stale_notifier`) — `jewel_metal_file`
  rings it on every observed miss, so a finish/shade/theme switch after
  the startup warm still gets its recipes built ([Watch
  Manager](../../app/__about/watch_manager.md)'s `kick_art_warm`; owner
  bug 2026-08-02: the startup-only drain left switched dials gold until
  restart)
- [Letter Bake](letter_bake.md) — `jewel_metal_path` consults
  `baked_file` BEFORE recording a recipe (0.14.950, owner order
  2026-08-12: the plate library ships pre-rendered in every metal and
  thematic colour). A hit returns there and then, so the dial's FIRST
  paint is the real metal — no gold stand-in, no ledger entry, no
  background drain
- [Config (folder)](../../config/___config.md) — `paths` (`art_file`,
  `metal_shade`, `settings_path`), `defaults`, `profiling`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `jewel_metal_file`
  (ring jewel finish at paint time)
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
  (Encyclopedia look-cycle and warm sweep), `jewel_metal_file` (skin
  assembly), `tinted_pixmap` (the per-watch tray icon tint)

## Functions
- `letter_cache_name(master, metal, shade)`: THE name a letter finish is
  filed under — `<path stamp>_<content fingerprint>_letter_<metal>_
  <shade>_v<METAL_SWAP_VERSION>.png`. The ONE naming function for this
  family (Rule #5), shared by the runtime cache, the shipped bake and
  the baker that writes it. Because the name carries the master's
  fingerprint and the recolor version, the bake needs no manifest: a
  re-drawn plate or bumped math simply stops matching, and the finish
  derives live again ([Letter Bake](letter_bake.md)).
- `bake_letter_finish(master, metal, shade, destination)`: derive one
  finish for an EXPLICIT (metal, shade) and write it — the SETUP
  baker's door ([Make Letter Bake](../../setup/__about/make_letter_bake.md)),
  and the only caller that names a shade instead of reading it from a
  watch's display context. Same kernel `ensure_variant` runs.
- `jewel_metal_file(path, metal)`: disk-cached ring jewel finish,
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
