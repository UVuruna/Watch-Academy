# Hands Section

**Script:** [Hands Section (script)](../hands.py) · **Flow:** [diagram](../__flow/hands.md)

## Purpose
The Watch Face window's Hands page (R-14): a gallery of hand packs,
each tile showing the pack's OWN hours-hand image LARGE (the image
dominates the tile, the name sits under it) — the same data
`design_window.DesignDialog._hands_tab` reads, through
`thumbs.art_thumbnail`'s disk-cached 256px source instead of a raw
`QIcon(path)` load. Its "image dominates" icon size was promoted to
EVERY gallery on 2026-08-08 (`widgets.TILE_ICON_PX`, set inside the
shared tile builder), so this section no longer carries a private size
constant.

## Connections

### Uses
- [Watch Face Thumbnails](thumbs.md) — `art_thumbnail`
- [Watch Face Shared Widgets](widgets.md) — `tile`
- [Hands (data)](../../../data/__about/hands.md) — `hand_packs`

### Used by
- `app.watch_face.window` — registered as the Hands section's builder
