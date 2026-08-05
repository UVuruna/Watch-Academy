# Hands Section

**Script:** [Hands Section (script)](../hands.py) · **Flow:** [diagram](../__flow/hands.md)

## Purpose
The Watch Face window's Hands page (R-14): a gallery of hand packs,
each tile showing the pack's OWN hours-hand image LARGE (the image
dominates the tile, the name sits under it) — the same data
`design_window.DesignDialog._hands_tab` reads, through
`thumbs.art_thumbnail`'s disk-cached 256px source instead of a raw
`QIcon(path)` load, scaled up to a larger on-tile icon size than the
other galleries use.

## Connections

### Uses
- [Watch Face Thumbnails](thumbs.md) — `art_thumbnail`
- [Watch Face Shared Widgets](widgets.md) — `tile`
- [Hands (data)](../../../data/__about/hands.md) — `hand_packs`

### Used by
- `app.watch_face.window` — registered as the Hands section's builder
