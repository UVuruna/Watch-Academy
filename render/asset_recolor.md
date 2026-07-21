# Asset Recolor

**Script:** [Asset Recolor (script)](asset_recolor.py)

## Purpose
Disk-cached recolors derived from a single master file — the metal
finish/tint family extracted out of `assets.py` (God-File Split Phase 2,
Step 1, `research/REFACTOR_PLAN.md` §8: a surgical sibling of
[Assets](assets.md), which keeps `AssetCache` at its own import path
unchanged for its 20+ callers).

`letter_metal_file(path, metal)` (owner decree 2026-07-19, "bolje
crtati na licu mesta nego 15MB fajlova" — retired the ~15 MB of
pre-rendered `<Stem>_silver.png`/`<Stem>_bronze.png` ring-letter files
and their two generator scripts): the ring letter's GOLD, SILVER or
BRONZE finish, derived AT LOAD from the GOLD master. SHADE-aware (R8a
redo, owner spec 2026-07-21 night): every metal, including gold, runs
through `AssetCache._recolor_to_shade` (the SAME kernel `AssetCache.
_metal_swapped` uses for badge medallions, Rule #5) with the WHOLE
opaque glyph as the mask — a ring letter mixes no gray stone the way a
medallion does, so unlike the badge's hue-window detection every
alpha>0 pixel simply IS a metal pixel. The active SHADE per metal comes
from `config.paths.metal_shade` (a Settings choice, not a parameter
here — same reasoning as `subdial_plate_file`'s active set). Disk-
cached like every other derived asset, keyed by shade and `defaults.
METAL_SWAP_VERSION`.

`metal_variant_file(path, metal)` (owner bug 2026-07-13: the legend/
Encyclopedia `<img>` always showed the BRONZE file even under the gold/
silver look — QToolTip embeds files, not pixmaps): a DISK copy of
`path` with the hue-selective metal swap applied (`AssetCache.
_metal_swapped`). Cached by the file's mtime, the active SHADE and
`defaults.METAL_SWAP_VERSION`; `None` or a non-swap metal returns the
original path.

`_recolored_plate(master, finish, tint=None)` — the subdial plate's
own recolor, called only by [Asset Variants](asset_variants.md)`.
subdial_plate_file`: `master` (the solo set's silver file, or any
set's file under a "theme" tint request) with its brushed metal BEZEL
colorized to `finish` — built the SAME recipe the ring letters use to
derive silver/bronze live from gold (Rule #5): SILVER is the achromatic
VALUE alone (no hue, whatever metal `master` itself happens to be drawn
in); GOLD and BRONZE tint that same achromatic base by their own color.
Only bright, unsaturated pixels INSIDE the radial bezel band take the
recolor — the field's own specular highlights stay neutral (owner
correction 2026-07-15). With a TINT the interior (the tapisserie field)
is colorized the same way to the clock tint (the "theme" plate style);
without one the field stays as drawn. numpy end to end, disk-cached in
`raster_cache/`.

`tinted_pixmap(source, tint)` (ADD WATCH round): the public door to
`AssetCache._tinted`'s TRITONE gradient-map recolor (black -> tint ->
white — see [Assets](assets.md) for the exact recipe) — the render
pipeline's ring/hand recolors call the private method directly (same
class, same cache), but `app.tray.logo_icon` needs the SAME algorithm
for a per-watch tray icon tint and lives outside `render/` entirely
(Rule #5 — one algorithm, a clean non-private door for the second
caller). [Asset Variants](asset_variants.md)'s `eclipse_solar_type_icon`
also reaches it, for the annular solar icon's "ring of fire" tint.

## Connections

### Uses
- [Assets](assets.md) — `AssetCache._letter_recolored`, `AssetCache.
  _metal_swapped`, `AssetCache._tinted` (the metal/tint recolor kernels
  stay on the class; these module functions are their disk-cached,
  path-in/path-out doors)
- `config.paths` (`art_file`, `metal_shade`, `settings_path`),
  `config.defaults`, `config.profiling`
- PySide6 QtGui, numpy

### Used by
- [Layers](layers.md) — `letter_metal_file` (ring letter finish at
  paint time)
- [Asset Variants](asset_variants.md) — `_recolored_plate`
  (`subdial_plate_file`'s recolor step), `tinted_pixmap`
  (`eclipse_solar_type_icon`'s annular tint) — the necessary reverse
  edge the split created; see that module's own docstring
- [Compositor](compositor.md) — `metal_variant_file` (hover-card/
  legend `<img>` tags, which embed files, not pixmaps)
- [Encyclopedia](../app/encyclopedia.md) — `metal_variant_file` (the
  Bronze/Gold/Silver look-arrow cycle on gallery images)
- [Watch Controller](../app/controller.md) — `letter_metal_file`
  (skin assembly, gold-master metal resolution)
- [Tray Controller](../app/tray.md) — `tinted_pixmap` only (ADD WATCH
  round, owner INSTRUCTION.txt item 2B): the same tritone recolor a
  per-watch tray icon needs, reached without pulling in the whole
  render pipeline

## Functions

- `letter_metal_file(path, metal)`: disk-cached ring letter finish,
  derived from the gold master
- `metal_variant_file(path, metal)`: disk-cached hue-selective metal
  swap of any asset (badge medallions, legend `<img>` tags)
- `_recolored_plate(master, finish, tint=None)`: the subdial plate's
  bezel/field recolor, `subdial_plate_file`'s private helper
- `tinted_pixmap(source, tint)`: the public door to the TRITONE
  gradient-map recolor
