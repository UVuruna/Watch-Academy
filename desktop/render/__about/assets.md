# Assets

**Script:** [Assets (script)](../assets.py) · **Flow:** [diagram](../__flow/assets.md)

## Purpose
`AssetCache` — rasterize each skin image once per (path, pixel height,
tint): PNG scaled smoothly, SVG rendered via `QSvgRenderer`. An optional
tint channel-multiplies the rasterized image with the source alpha
restored (the ring/hand recolor). Missing/unreadable assets raise
`ValueError` — a broken skin must be visible, never silently blank.
Every disk boundary resolves canonical paths through
`config.paths.art_file` (the Gemini/ChatGPT art-source switch).

**Surgical sibling split** (God-File Split Phase 2): a dozen
module-level helpers that used to live here now live in two siblings —
[Asset Recolor](asset_recolor.md) (the metal finish/tint family) and
[Asset Variants](asset_variants.md) (the working-set downscale, moon
render, subdial resolver and computed-icon families) — while
`AssetCache` stays here at its own unchanged import path for its 20+
callers. `pixmap_by_height` reads `working_ceiling`/`scaled_variant_file`
back from `asset_variants.py` (a genuine two-way edge), resolved with a
LOCAL import inside that one method so the three files' top-level
imports never form an unresolvable cycle.

**The working set** (owner 2026-07-15): `pixmap_by_height` routes any
request that fits under the asset's subtree ceiling through a
once-per-file DOWNSCALED copy instead of the full-resolution original
(oversized requests keep the original; the ceiling lookup and the
downscale itself are [Asset Variants](asset_variants.md) functions).

**A cold working-set miss NEVER builds inline** (owner bar 2026-08-09,
MIGRATE-GUI Phase 1 — "the 75-second dead clock"): this used to call
`scaled_variant_file(path, ceiling)` with `build=True` right here,
decoding a multi-MB PNG INSIDE `paintEvent`. Now a miss only NAMES the
copy (`working_variant_path`, a header-only check — a source already at
or under its ceiling is returned UNCHANGED and never enters the ledger
at all), records the recipe, rings the ledger's stale notifier and
returns `None`; `render.painting.draw_pixmap_centered` is the one
chokepoint every art layer draws through, and it simply skips the
element for that frame. The pixels build off the GUI thread
(`render.asset_variants.drain_pending_working`, called by `app.warm.
run_warm`'s VISIBLE-FIRST phase and by `app.watch_manager.
AppController.kick_working_warm` on demand) and land through the SAME
debounced repaint a metal recolor already rides
(`app.controller.WatchController.apply_pending_art`/`_apply_art_now`).
A still-pending element caches `None` under its own key — THE ONE COPY
RULE (`tests/test_repeat_work.py`) — so a steady-state repaint never
repeats the `exists()` stat; `clear_pending()` purges exactly those
`None` markers (never a real rasterized pixmap) whenever a background
build might have landed, giving the element one more chance to resolve.

**The metal recolor** moved to the standalone, Qt-free `recolor/`
package (owner verdict "prihvaceno", 2026-07-27) — `_recolored` is a
thin QImage-in/QImage-out adapter over `recolor.transform.recolor`; see
[Recolor (folder)](../../recolor/___recolor.md) for the pipeline itself
and the measured autopsy of the retired kernel it replaced.

## Connections

### Uses
- PySide6 QtGui/QtSvg
- [Recolor (folder)](../../recolor/___recolor.md) — the metal
  transformer `_recolored` adapts to QImage
- [Raster Store](raster_store.md) — the SVG master's disk write is
  atomic (a half-written cache PNG must never be visible)

### Used by
- [Layers (subfolder)](../layers/___layers.md) — hands, hexagram,
  weekday bodies, year marker
- `app.controller` — owns the instance, flushed via the compositor on
  screen change
- [Asset Recolor](asset_recolor.md) — `_recolored`, `_tinted`
- [Asset Variants](asset_variants.md) — the reverse `pixmap_by_height`
  edge
- [Instrument Diagrams](instrument_diagrams.md) — `shared_cache` recolors
  the `chi` figure's own X master to its ceramic thematic shade

## Classes

### AssetCache
- `pixmap_by_height(path, logical_height, dpr, tint=None,
  desaturate=False, metal=None, saturation=1.0) -> QPixmap | None`:
  aspect-preserving, device-resolution pixmap with `devicePixelRatio`
  set; `saturation` (Ring Saturation slider) scales the FINAL pixmap's
  HSV saturation, applied AFTER `tint`. Returns `None` for a pending
  working-set miss (owner bar 2026-08-09) — every caller must guard it.
- `_recolored(source, metal, source_metal, mask_mode)`: the ONE metal
  recolor door — resolves the active shade to a ramp name and hands the
  pixels to `recolor.transform.recolor` (mask modes: `"chroma"` for
  badges mixing metal with gray stone, `"alpha"` for glyphs where every
  opaque pixel IS metal).
- `_tinted(source, tint)`: the TRITONE gradient-map recolor
  (black→tint→white).
- `flush()`: drop everything on screen/DPI or skin change.
- `clear_pending()`: drop only the `None` pending markers (owner bar
  2026-08-09) — every rasterized pixmap survives; called from
  `app.controller.WatchController._apply_art_now` whenever a background
  build might have landed.

## Design Decisions
- **Every metal recolor calls the ONE `_recolored` door** (Rule #5) —
  callers differ only in `source_metal`/`mask_mode`, never in a
  separate function per material.
- **Cost is deliberately accepted, never avoided at paint time.** The
  Oklab-based recolor is an order of magnitude slower than the retired
  HSV kernel; every result is disk-cached and built lazily off the GUI
  thread ([Art Warm](art_warm.md)), paid once per asset, never per
  paint.
