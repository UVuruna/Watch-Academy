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
tuples), and `subdial_plate_file(finish, tint=None)` — reworked in
the Rsub round (owner decree 2026-07-21), which RETIRES Rule #19's
first enforcement (owner decree 2026-07-20, "Compute, Don't Generate")
for this family: the subdial plate stops being a Rule #19
one-master-per-art-source case at all. It reads the ACTIVE SET off
`config.paths.subdial_set()` — a module global mirroring the
art-source switch exactly (set by `app.controller.
apply_display_settings` from `Settings.subdial_set`), chosen this way
specifically so the function's OWN signature never had to change and
[Layers](layers.md)`.draw_slot_roundel`'s existing call stays
untouched. Five hand-picked sets live under `assets/subdial/` (see
[Assets (folder)](../assets/___assets.md) for why that root sits
OUTSIDE `ART_SOURCED_ROOTS`): for "set1".."set4" the matching
hand-drawn file (`assets/subdial/<set>/<finish>.png`) returns AS
DRAWN — no recolor, no cache entry. For "solo" the one hand-drawn file
(silver, `defaults.SUBDIAL_SOLO_FINISH`) returns AS DRAWN; gold/bronze
are `_recolored_plate()`-ed from it live, built the SAME recipe the
ring letters use (Rule #5): SILVER is the achromatic VALUE alone (no
stored hue, whatever metal the source itself is), GOLD/BRONZE tint
that same value by their own color — masked to only the bright,
low-saturation brushed rim (numpy, `SUBDIAL_RECOLOR_*` knobs,
disk-cached in `raster_cache/`). A TINT (the "theme" plate style,
owner A/B spec 2026-07-15) colorizes the dark tapisserie field to the
clock tint the same way, lifted by the field gain so the hue reads —
that pass runs on top of WHICHEVER plate above was resolved, even an
already-correct hand-drawn finish, into its own cache entry. Returns
None when no plate art exists for the active set — the layer then
draws the procedural circle. The SEAT still never reaches the file at
all, only the LIVE shadow the layer draws
([Layers](layers.md)`._draw_subdial_shadow`, keyed off the seat's own
dial position, unchanged since Rule #19's first enforcement).

## Connections

### Uses
- PySide6 QtGui/QtSvg

### Used by
- [Layers](layers.md) — hands, hexagram, weekday bodies, year marker
- [Watch Controller](../app/controller.md) — owns the instance, flushed via
  the compositor on screen change
- [Tray Controller](../app/tray.md) — `tinted_pixmap()` only (ADD WATCH
  round, owner INSTRUCTION.txt item 2B): the SAME tritone recolor a
  per-watch tray icon needs, reached without pulling in the whole
  render pipeline

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

## Functions

- `tinted_pixmap(source, tint)` (ADD WATCH round): the public door to
  `AssetCache._tinted`'s own tritone recipe — module-level so a caller
  outside render/ (`app.tray.logo_icon`) can reach it without touching
  a private method on a class it does not otherwise use.
