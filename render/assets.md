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

**The working set** (owner 2026-07-15): originals ship at full
resolution; the dial decodes through a once-per-file DOWNSCALED copy
instead — `working_ceiling()` names each assets subtree's largest
possible on-dial size (`WORKING_SET_CEILINGS`: earth/weekday 800 px,
zodiac/badge 1200 px, from 1440 dial × 200% scale × 200% enlarge),
`warm_working_set()` pre-builds the copies on a background thread at
startup (idempotent, progress-logged), and `pixmap_by_height` routes
any request that fits under the ceiling through the copy — oversized
requests keep the original, small sources stay untouched.

Module helpers beyond the cache: `ring_face_color()` (the ring art's
median-luminance face sample, the procedural subdial fill),
`metal_variant_file()` / `scaled_variant_file()` (disk-cached derived
images), and `subdial_plate_file(finish, seat, tint=None)` — the
owner's subdial plate for a (letter finish, seat) pair: his art wins
as drawn, a missing seat borrows the center plate, and a missing
FINISH is `_recolored_plate()`-ed from another finish's master (numpy
colorize: only the bright, low-saturation brushed rim takes the
finish color × its own luminance; `SUBDIAL_RECOLOR_*` knobs,
disk-cached in `raster_cache/`). A TINT (the "theme" plate style,
owner A/B spec 2026-07-15) colorizes the dark tapisserie field to the
clock tint the same way, lifted by the field gain so the hue reads —
that pass runs even on the exact finish, into its own cache entry.
Returns None when no plate art exists at all — the layer then draws
the procedural circle.

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
