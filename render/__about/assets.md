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

### Used by
- [Layers (subfolder)](../layers/___layers.md) — hands, hexagram,
  weekday bodies, year marker
- `app.controller` — owns the instance, flushed via the compositor on
  screen change
- [Asset Recolor](asset_recolor.md) — `_recolored`, `_tinted`
- [Asset Variants](asset_variants.md) — the reverse `pixmap_by_height`
  edge

## Classes

### AssetCache
- `pixmap_by_height(path, logical_height, dpr, tint=None,
  desaturate=False, metal=None, saturation=1.0)`: aspect-preserving,
  device-resolution pixmap with `devicePixelRatio` set; `saturation`
  (Ring Saturation slider) scales the FINAL pixmap's HSV saturation,
  applied AFTER `tint`.
- `_recolored(source, metal, source_metal, mask_mode)`: the ONE metal
  recolor door — resolves the active shade to a ramp name and hands the
  pixels to `recolor.transform.recolor` (mask modes: `"chroma"` for
  badges mixing metal with gray stone, `"alpha"` for glyphs where every
  opaque pixel IS metal).
- `_tinted(source, tint)`: the TRITONE gradient-map recolor
  (black→tint→white).
- `flush()`: drop everything on screen/DPI or skin change.

## Design Decisions
- **Every metal recolor calls the ONE `_recolored` door** (Rule #5) —
  callers differ only in `source_metal`/`mask_mode`, never in a
  separate function per material.
- **Cost is deliberately accepted, never avoided at paint time.** The
  Oklab-based recolor is an order of magnitude slower than the retired
  HSV kernel; every result is disk-cached and built lazily off the GUI
  thread ([Art Warm](art_warm.md)), paid once per asset, never per
  paint.
