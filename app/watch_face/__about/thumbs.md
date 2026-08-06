# Watch Face Thumbnails

**Script:** [Thumbnails (script)](../thumbs.py) · **Flow:** [diagram](../__flow/thumbs.md)

## Purpose
R-33: the ONE thumbnail service every gallery in the Watch Face window
draws from — a disk-cached, 256px-source `QIcon` for an existing art
file (a ring preset's face, a hand pack's hours image), plus the honest
fallback for pointer variants, which carry no preview art of their own
(see Design Decisions).

## Connections

### Uses
- [Raster Store](../../../render/__about/raster_store.md) —
  `source_prefix`/`atomic_save`, the SAME content-fingerprint disk cache
  the ring-jewel metal recolor cache uses (Rule #5, no second cache
  mechanism)
- [Config (folder)](../../../config/___config.md) — `paths.art_file`,
  `paths.settings_path`, `palette.PALETTE_PRESETS`,
  `palette.effective_palette_style`

### Used by
- `app.watch_face.ring` — `ring_preset_thumbnail` for each preset's own
  composed preview (fallback `art_thumbnail` on its bare outer plate)
- `app.watch_face.hands` — `art_thumbnail` for each pack's hours image
- `app.watch_face.pointer` — `art_thumbnail` for the Earth style tiles,
  `pointer_swatch_icon` for the pointer gallery

## Functions
- `art_thumbnail(source)`: a 256px-source disk-cached `QIcon` of an
  existing art file, or `None` if the source is missing/unreadable (the
  caller's documented no-icon fallback, matching
  `design_window._tile`'s own contract)
- `ring_preset_thumbnail(card)`: the RING PRESET PICKER's own mini
  preview (ring_rework §5, owner ruling 2026-08-06) — COMPUTED, never
  stored/generated: composes the card's own outer plate PNG with its
  own jewel masters stamped at their real seats (gold, no recolor
  pass — identification, not a finish preview), at thumbnail scale.
  Disk-cached; the cache name folds in every source file's own content
  fingerprint (`raster_store.source_prefix`) so a changed master
  invalidates it.
- `pointer_swatch_icon(pointer, style)`: the honest pointer-variant
  fallback — a pie of the pointer's active palette wheel's own hues

## Design Decisions
- **Asset-honesty fallback (R-33):** pointer variants have no dedicated
  preview art (`design_window.md`'s own note — they are procedural/
  abstract) and no render path in `render/layers/*.py` or
  `render/skin_geometry.py` can produce a small preview without a fully
  built `Skin` (every `Layer.draw()` takes the complete object). Rather
  than fake art or fall back to a blank tile, `pointer_swatch_icon`
  composes a small preview from the pointer's OWN active palette wheel
  (`config.palette.PALETTE_PRESETS[(pointer, style)]`) — real derived
  content (the exact hues that pointer paints), drawn once as a pie and
  disk-cached like any other thumbnail.
- **Cache key for a computed (sourceless) icon:** `pointer_swatch_icon`
  has no source file to fingerprint, so its cache name is a plain
  `pointer_swatch_{pointer}_{style}_v{VERSION}.png` — the SAME "computed
  icon, no stamp/fingerprint prefix" convention
  `render.asset_variants.calendar_wheel_icon_file` already uses, which
  `render.raster_store.collect_garbage` already carves out (files whose
  first field is not a 16-hex stamp are kept, never swept as orphans).
- **Source renders at 256px** (`THUMB_SOURCE_PX`); every gallery tile
  displays it scaled down through Qt's own icon scaling — one cached
  raster serves every tile size a future section might want.
