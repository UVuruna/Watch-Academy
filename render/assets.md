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

**Surgical sibling split** (God-File Split Phase 2, Step 1, `research/
REFACTOR_PLAN.md` §8): this file used to also hold a dozen module-level
helper functions built on top of `AssetCache`. They now live in two
sibling modules — [Asset Recolor](asset_recolor.md) (the metal finish/
tint family: `letter_metal_file`, `metal_variant_file`, `tinted_pixmap`,
`_recolored_plate`) and [Asset Variants](asset_variants.md) (everything
else: `ring_face_color`, the moon-phase live-render family,
`subdial_plate_file`, the working-set downscale family, and the two
computed icons) — while `AssetCache` itself stays here, at its own
unchanged import path, for its 20+ callers across `render/`, `app/` and
`tests/`. `pixmap_by_height` reads `working_ceiling`/`scaled_variant_file`
back from `asset_variants.py` — a genuine two-way edge between the split
files — resolved with a LOCAL import inside that one method rather than
a module-level one, so the three files' top-level imports never form an
unresolvable cycle (asset_variants.py imports asset_recolor.py, which
imports AssetCache from here).

**The working set** (owner 2026-07-15): originals ship at full
resolution; the dial decodes through a once-per-file DOWNSCALED copy
instead. `pixmap_by_height` routes any request that fits under the
asset's subtree ceiling through that downscaled copy (oversized
requests keep the original, small sources stay untouched) — the
ceiling lookup (`working_ceiling`) and the downscale itself
(`scaled_variant_file`) are [Asset Variants](asset_variants.md)
functions; see that doc for the full recipe (`WORKING_SET_CEILINGS`,
the background warmup, etc.).

**THE METAL RECOLOR (rewritten 2026-07-27, owner verdict
"prihvaceno"):** the algorithm no longer lives in this file at all. It
moved to the standalone, Qt-free [Recolor (folder)](../recolor/___recolor.md)
package — read that doc for the pipeline, the measured autopsy of what it
replaces, and the laws it follows. What lives here is the Qt adapter.

WHY IT WAS REPLACED, measured on the owner's physician plate: the old
kernel replaced each masked pixel's hue AND saturation with a flat
constant and scaled its value by one bounded global gain. Gold `classic`
= `HSV(44.9, S=1.000, V)` expands to `(V, 0.748*V, 0)` — **the blue
channel identically zero on 52.59% of the plate**, and a white highlight
arithmetically impossible at flat `S=1.0` ("drecavo, napadno, bez
detalja"). Silver = `HSV(220, S=0, V)` = `max(R,G,B)`, which on warm
bronze art is **the red channel alone** (mean R 0.3721 vs mean V 0.3740).
The gain hit its 1.90 ceiling on dark medallion art and clipped **11.87%**
(gold) / **8.17%** (silver) of the plate to one flat maximum — the book
page on the plate came out with no information at all in its top 5%
("kao da joj je neko polio krec"). After the rewrite: B=0 on 0.00%,
blown 1.62% / 2.01%, and the book page's lightness range rose from 0.5875
(source) to 0.7342 gold / 0.7619 silver.

`AssetCache._recolored(source, metal, source_metal, mask_mode)` is the
ONE door — a thin QImage-in/QImage-out adapter over
`recolor.transform.recolor`. Every metal recolor in the codebase calls
it, differing only in its arguments (Rule #5 — the retired code carried
`_recolor_to_shade`, `_metal_swapped` AND `_letter_recolored`, three
functions for one algorithm):

| caller | `source_metal` | `mask_mode` |
|--------|----------------|-------------|
| badge medallions (`pixmap_by_height`, [Asset Recolor](asset_recolor.md)`.metal_variant_file`) | `defaults.METAL_SOURCE_BADGE` = bronze | `chroma` — the art mixes metal with GRAY stone, which must never move |
| ring letters and numerals ([Asset Recolor](asset_recolor.md)`.letter_metal_file`) | `defaults.METAL_SOURCE_LETTER` = gold | `alpha` — a glyph mixes no stone, so every opaque pixel IS metal |

The transform is **source-agnostic**: it measures and divides out
whatever cast the source carries before a target is consulted, which is
why letters (gold -> bronze/silver) and badges (bronze -> gold/silver)
share one code path. `defaults.METAL_SWAP_TARGETS` remains the membership
tuple `("gold", "silver")` — badges never bronze-swap; bronze medallions
stay the art as drawn.

**The mask survived the rewrite** (the owner's 2026-07-12 decree, still
law — only warm metal changes, the gray stone never does), and its
arithmetic got sounder: measured against the retired HSV mask on the
physician plate, the Oklab one keeps **100.00%** of the opaque metal
pixels, ADDS 2.55% of the image in dark metal that HSV noise had dropped
in the shadows, claims 0.03% of the stone, and stops recoloring the
27.9% of the old mask's claim that was fully transparent pixels.

**Shades are now RAMPS.** Each metal still offers its SELECTABLE shades
(names validated against `config.constants.METAL_SHADE_NAMES`, unchanged
so the user's Settings pick keeps working), but `defaults.METAL_SHADES`
holds only the MAPPING from a shade to a named ramp in
`recolor/presets/metals.json`; the numbers live there, as data. Silver's
three shades map to ramps that exist as metals in their own right
(gunmetal / silver / platinum); gold's and bronze's are named `gold_*`
and `bronze_*`. Retiring the old recipe also retired
`METAL_RECOLOR_GAIN_RANGE`, `METAL_SWAP_HUE_WINDOW`, `_SOFT` and
`METAL_SWAP_SAT_RAMP` — all of them belonged to that kernel; the mask's
window now lives in the presets' `tuning` block, in Oklab.

**Silver is no longer exactly R==G==B.** That property was a CONSEQUENCE
of the `S=0` recipe and is precisely what the owner rejected: a flat
achromatic lift reads as whitewashed plaster. Real silver carries a cool
cast in the shadows and a near-white specular, so the ramp is
deliberately not neutral — pinned now as "nearly neutral (Oklab chroma
< 0.05) and never warm" instead of an exact channel equality.

**Cost:** ~0.28 s for a 750x512 ring letter, ~0.56 s for an 800x800 badge
— an order of magnitude more than the retired kernel, and deliberately
accepted: every result is DISK-CACHED per (file, metal, shade,
`METAL_SWAP_VERSION`) and built lazily off the GUI thread (the
never-block law, see [Asset Recolor](asset_recolor.md)'s lazy variant
ledger). It is paid once per asset, never per paint. Every derived cache
filename folds in the metal, the active SHADE and
`defaults.METAL_SWAP_VERSION` (bumped to 6 by this rewrite) so a shade
switch or a future math change never serves a stale PNG.

**The Settings side:** `Settings.metal_shade_gold/_bronze/_silver`
(`app/settings_store.md`) persist the pick; `app.controller.
apply_display_settings` pushes them into `config.paths` module globals
(`set_metal_shade`/`metal_shade`, mirroring `set_subdial_set`'s exact
pattern — ONE global per metal because it is a single user preference
reached from many render call sites, never threaded as a parameter);
`app.settings_dialog.themes_section._build_metal_shade_group`
(`app/settings_dialog/themes_section.md`) is the picker, one combo per
metal, filed in Themes beside the Subdial plate picker.

## Connections

### Uses
- PySide6 QtGui/QtSvg
- [Recolor (folder)](../recolor/___recolor.md) — the metal transformer
  algorithm, which `_recolored` adapts to QImage

### Used by
- [Layers](layers.md) — hands, hexagram, weekday bodies, year marker
- [Watch Controller](../app/controller.md) — owns the instance, flushed via
  the compositor on screen change
- [Asset Recolor](asset_recolor.md) — `AssetCache._recolored` and
  `._tinted` (the recolor doors this module owns)
- [Asset Variants](asset_variants.md) — the reverse `pixmap_by_height`
  edge described above (a necessary two-way edge from the split)

## Classes

### AssetCache
- `pixmap_by_height(path, logical_height, dpr, tint=None, desaturate=False, metal=None, saturation=1.0)`:
  aspect-preserving, device-resolution pixmap with `devicePixelRatio`
  set; `tint` = #RRGGBB multiply (ring art and hands under a ring tint);
  `saturation` (owner 2026-07-18, Session 21-D — the Ring saturation
  slider) scales the FINAL pixmap's HSV saturation, applied AFTER
  `tint` — 1.0 is a no-op, the default for every caller except
  `RingLayer` (the plate and its letter overlay)
- `_recolored(source, metal, source_metal, mask_mode)`: the ONE metal
  recolor door — QImage in, QImage out (the R1b threading law: the
  background warm sweep reaches it, and QPixmap must never be touched
  off the GUI thread). Resolves the active SHADE to a ramp name and
  hands the pixels to [Recolor (folder)](../recolor/___recolor.md)
- `flush()`: drop everything (screen/DPI or skin change)
