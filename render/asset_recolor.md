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
through `AssetCache._recolored` (the SAME door badge medallions use,
Rule #5 — see [Assets](assets.md)) with the WHOLE
opaque glyph as the mask — a ring letter mixes no gray stone the way a
medallion does, so unlike the badge's hue-window detection every
alpha>0 pixel simply IS a metal pixel. The active SHADE per metal comes
from `config.paths.metal_shade` (a Settings choice, not a parameter
here — same reasoning as `subdial_plate_file`'s active set). Disk-
cached like every other derived asset, keyed by shade and `defaults.
METAL_SWAP_VERSION`.

**The metal-variant family is LAZY since the 2026-07-26 owner order**
("the Encyclopedia BLOCKED the main thread for minutes"): naming a
variant and building its pixels are two separate steps.

`metal_variant_path(path, metal)` — PURE: computes the cache path
(keyed by the file's mtime, the active SHADE and `defaults.
METAL_SWAP_VERSION`) and records the (source, metal) recipe in a
module ledger; no pixel work. `None` or a non-swap metal returns the
original path; a source MISSING from disk returns the canonical path
unchanged (graceful-absent — the old eager code crashed on the
unguarded `stat()`, which is exactly what an art rename wave did to
the Encyclopedia's open).

`ensure_variant(path)` — the ONE place the pixel work happens:
materializes a recorded, still-missing variant on first actual use
(any thread — QImage end to end, the R1b law; per-path locks make a
GUI-thread first display and the background warm meeting on the SAME
file build it once). Unrecorded paths pass through untouched.

`variant_pending(path)` — True for a recorded, not-yet-built variant;
the Encyclopedia's exists() filter counts such a path as present.

`metal_variant_file(path, metal)` (owner bug 2026-07-13: the legend/
Encyclopedia `<img>` always showed the BRONZE file even under the gold/
silver look — QToolTip embeds files, not pixmaps): the EAGER door —
`ensure_variant(metal_variant_path(...))` in one call — for callers
that embed the file path immediately (the compositor's tooltip `<img>`
tags, the hover warm sweep).

Pseudocode of the split (Rule #21):

```
metal_variant_path(source, metal):
    IF metal is not a swap target OR source missing → return source as-is
    cache = raster_cache / hash(source) + mtime + metal + shade + version
    ledger[cache] = (source, metal)      ← recipe recorded, no pixels
    return cache

ensure_variant(path):
    IF path not in ledger OR already on disk → return path
    LOCK path → recolor source with the metal kernel → save to path
    return path (source on a failed write — slower, never wrong)
```

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
- [Assets](assets.md) — `AssetCache._recolored`, `AssetCache._tinted`
  (the metal/tint recolor doors
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
  legend `<img>` tags, which embed files, not pixmaps — the eager door)
- [Encyclopedia (subfolder)](../app/encyclopedia/___encyclopedia.md) — `metal_variant_path` (the
  Bronze/Gold/Silver look-arrow cycle records paths only),
  `ensure_variant` (first display / Download), `variant_pending` (the
  reader's exists-or-pending filter)
- [Encyclopedia Warm](../app/encyclopedia_warm.md) — `ensure_variant` /
  `variant_pending` (the background pre-materialization walk)
- [Watch Controller](../app/controller.md) — `letter_metal_file`
  (skin assembly, gold-master metal resolution)
- [Tray Controller](../app/tray.md) — `tinted_pixmap` only (ADD WATCH
  round, owner INSTRUCTION.txt item 2B): the same tritone recolor a
  per-watch tray icon needs, reached without pulling in the whole
  render pipeline

## Functions

- `letter_metal_file(path, metal)`: disk-cached ring letter finish,
  derived from the gold master
- `metal_variant_path(path, metal)`: PURE cache-path computation +
  recipe ledger entry — no pixel work
- `ensure_variant(path)`: materialize a recorded variant on first use
  (any thread; per-path locks)
- `variant_pending(path)`: recorded-but-not-yet-built test for
  exists() filters
- `metal_variant_file(path, metal)`: the eager door — path + ensure in
  one call (tooltip `<img>` embedders)
- `_recolored_plate(master, finish, tint=None)`: the subdial plate's
  bezel/field recolor, `subdial_plate_file`'s private helper
- `tinted_pixmap(source, tint)`: the public door to the TRITONE
  gradient-map recolor
