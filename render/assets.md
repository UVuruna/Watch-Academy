# Assets

**Script:** [Assets (script)](assets.py)

## Purpose
Rasterize each skin image once per (path, pixel height, tint): PNG scaled
smoothly, SVG rendered via QSvgRenderer (the explicit QtSvg import also
makes PyInstaller bundle the plugin). An optional tint channel-multiplies
the rasterized image with the source alpha restored — the ring recolor
(gray art × hue). Missing/unreadable assets raise
`ValueError` — a broken skin must be visible, never silently blank.
Every disk boundary resolves canonical paths through
`config.paths.art_file` (the Gemini/ChatGPT art-source switch with
cross-source fallback).

Module helpers beyond the cache: `ring_face_color()` (the ring art's
median-luminance face sample, the procedural subdial fill),
`metal_variant_file()` / `scaled_variant_file()` (disk-cached derived
images), and `subdial_plate_file(finish, seat)` — the owner's subdial
plate for a (letter finish, seat) pair: his art wins as drawn, a
missing seat borrows the center plate, and a missing FINISH is
`_recolored_plate()`-ed from another finish's master (numpy colorize:
only the bright, low-saturation brushed rim takes the finish color ×
its own luminance, the dark tapisserie field never moves;
`SUBDIAL_RECOLOR_*` knobs, disk-cached in `raster_cache/`). Returns
None when no plate art exists at all — the layer then draws the
procedural circle.

## Connections

### Uses
- PySide6 QtGui/QtSvg

### Used by
- [Layers](layers.md) — hands, hexagram, weekday bodies, year marker
- [App Controller](../app/controller.md) — owns the instance, flushed via
  the compositor on screen change

## Classes

### AssetCache
- `pixmap_by_height(path, logical_height, dpr, tint=None)`:
  aspect-preserving, device-resolution pixmap with `devicePixelRatio`
  set; `tint` = #RRGGBB multiply (ring art and hands under a ring tint)
- `flush()`: drop everything (screen/DPI or skin change)
