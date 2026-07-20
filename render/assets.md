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
images), `letter_metal_file(path, metal)` (owner decree 2026-07-19,
"bolje crtati na licu mesta nego 15MB fajlova" — retired the ~15 MB of
pre-rendered `<Stem>_silver.png`/`<Stem>_bronze.png` ring-letter files
and their two generator scripts: silver is a straight grayscale
desaturation of the gold master, `AssetCache._desaturated`; bronze a
straight per-channel multiply with `defaults.BRONZE_LETTER_TINT` off
the silver result, `AssetCache._bronzed` — the sealed recipes,
reproduced exactly, disk-cached like every other derived asset;
`metal="gold"` is a no-op passthrough), `moon_lit_region(fraction,
radius)` / `moon_phase_image(fraction, size, master=None)` /
`moon_phase_file(fraction, name, size=800)` (the SAME retirement for
the Encyclopedia's eight Moon-phase plates: `moon_lit_region` is the
terminator geometry extracted out of
[Layers](layers.md)`.YearMarkerLayer._draw_moon` so the dial and the
Encyclopedia's live render share ONE function — fixing an exact-quarter
degeneracy, `fraction` 0.25/0.75, where Qt's `addEllipse` on a
zero-width terminator rect used to degenerate the union/difference to
an empty path, i.e. a moon rendered fully DARK instead of exactly
half-lit; `moon_phase_image` is the pure QImage render, `moon_phase_file`
its disk-cached path wrapper for the Encyclopedia's path-based image
tuples), and `subdial_plate_file(finish, tint=None)` — Rule #19's
first enforcement (owner decree 2026-07-20, "Compute, Don't Generate"):
the twelve-plate seat×finish sheet collapsed to ONE master per source
(`assets/badge/subdial/master.png`) — the SEAT never reached the file
at all, only the LIVE shadow the layer draws
([Layers](layers.md)`._draw_subdial_shadow`, keyed off the seat's own
dial position), so generating one per seat was pure waste. The
master's own finish (`SUBDIAL_MASTER_FINISH`, one entry per source —
gemini's is silver, chatgpt's is gold) draws AS DRAWN; the other two
are `_recolored_plate()`-ed from it live, built the SAME recipe the
ring letters use (Rule #5): SILVER is the achromatic VALUE alone (no
stored hue, whatever metal the master itself is), GOLD/BRONZE tint
that same value by their own color — masked to only the bright,
low-saturation brushed rim (numpy, `SUBDIAL_RECOLOR_*` knobs,
disk-cached in `raster_cache/`). A TINT (the "theme" plate style,
owner A/B spec 2026-07-15) colorizes the dark tapisserie field to the
clock tint the same way, lifted by the field gain so the hue reads —
that pass runs even on the exact finish, into its own cache entry.
Returns None when no master art exists at all — the layer then draws
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
- `pixmap_by_height(path, logical_height, dpr, tint=None, desaturate=False, metal=None, saturation=1.0)`:
  aspect-preserving, device-resolution pixmap with `devicePixelRatio`
  set; `tint` = #RRGGBB multiply (ring art and hands under a ring tint);
  `saturation` (owner 2026-07-18, Session 21-D — the Ring saturation
  slider) scales the FINAL pixmap's HSV saturation, applied AFTER
  `tint` — 1.0 is a no-op, the default for every caller except
  `RingLayer` (the plate and its letter overlay)
- `flush()`: drop everything (screen/DPI or skin change)
