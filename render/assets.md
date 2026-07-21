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

**THE METAL SHADES (R8a round, owner spec 2026-07-21 night — the redo
after an ADAPTIVE PERCENTILE-STRETCH attempt was reverted the SAME day
it landed, `git show 013b5ca` for the corpse):** that first attempt
contrast-stretched each source's own masked-region lightness onto a
fixed 5-step ramp per pixel RANK — a nonlinear per-pixel remap that
flattened every relief (engraving lines, drapery folds, background
texture) into a detail-free yellow wash ("nemamo kontrast, sve je
svetlo, izgubili smo sve moguće detalje," owner verdict). `git show
11a993e` reverted the algorithm to the pre-ramp recipes verbatim; THIS
round replaces those pre-ramp recipes for good with a properly designed
one, following the owner's law instead of guessing at it: hue and
saturation are REPLACED outright by a chosen SHADE's fixed target —
never scaled from the source's own unreliable hue/saturation — while
VALUE is the source pixel's OWN, multiplied by ONE bounded GLOBAL
scalar gain (a single number for the whole masked region, computed from
its own mean so differently-lit source plates land near the same shade
brightness, clamped to `defaults.METAL_RECOLOR_GAIN_RANGE`). A straight
multiply preserves every relative light/dark relationship in the relief
exactly — nothing here remaps by percentile RANK the way the reverted
attempt did. This is precisely why the pre-round SILVER recipe already
read as "solidan u oba" (solid in both, badge and letter): it always
scaled the source's own value by a near-identity multiplier instead of
replacing it — gold and bronze now follow the same philosophy with
their own hue/saturation.

`AssetCache._recolor_to_shade(rgb, weight, value, hue_deg, sat_target,
ref_value)` is the ONE kernel implementing this (Rule #5/#19) — every
metal recolor in the codebase calls it:
- `AssetCache._metal_swapped(source, metal)` (badge medallions): the
  hue-window + saturation-ramp MASK is UNCHANGED from before this round
  ("the mask stays") — only warm bronze-plate pixels are detected, gray
  stone and engravings never move. `metal` resolves its active SHADE
  through `config.paths.metal_shade(metal)` (a Settings choice, see
  below), looks the `(hue_deg, sat_target, ref_value)` triple up in
  `defaults.METAL_SHADES[metal][shade]`, and feeds the kernel.
  `defaults.METAL_SWAP_TARGETS` is now just the membership tuple
  `("gold", "silver")` — badges never bronze-swap; bronze medallions
  stay the art as drawn, unaffected by the bronze shade pick (out of
  this round's scope — the owner's two complaints were badge GOLD and
  letter BRONZE, never badge bronze). [Asset Recolor](asset_recolor.md)`.
  metal_variant_file` is its disk-cached, path-in/path-out door.
- `AssetCache._letter_recolored(source, metal, shade)` (ring letters,
  called from [Asset Recolor](asset_recolor.md)`.letter_metal_file`):
  the mask is the WHOLE opaque glyph (weight 1 wherever alpha > 0) — a
  letter mixes no gray stone the way a medallion does, so every drawn
  pixel already IS the metal. ALL THREE metals run through this now,
  including gold — the old "gold is a no-op passthrough" shortcut is
  gone now that gold itself has five selectable shades; the DEFAULT
  "classic" shade is tuned to read close to the retired passthrough's
  look.

Each metal offers several SELECTABLE shades (`defaults.METAL_SHADES`,
names validated against `config.constants.METAL_SHADE_NAMES`): GOLD's
five bands are sampled directly off the owner's reference swatch
(`UV/DESIGN/gold pallete.png`, `QColor.getHsvF()` at each band's
center — hue flat ~44.9deg across all five, only saturation/reference-
value step dark-amber to pale/champagne); BRONZE is a 3-step ramp
around `BRONZE_LETTER_TINT`'s own hue/saturation (~30deg/0.76); SILVER
is a 3-step ramp at saturation EXACTLY 0.0 (hue is irrelevant there —
this is what makes `_letter_recolored`'s silver output exact R==G==B,
not merely close). The bright gold bands (classic/pale/champagne) use
`reference_value` 0.85 rather than the palette swatch's own flat-color
1.00: a flat color swatch has no relief to protect, but a real ring
LETTER is already bright (masked mean ~0.88) — chasing 1.00 there
forces a gain that clips a big share of the glyph to solid white for no
visual gain, found during this round's verification sweep on the real
`assets/ring/letters/*.png` files; badge medallions are far darker
(masked mean ~0.40) and hit the SAME gain ceiling either way, so this
was a strict win — zero change to badges, less needless letter
clipping. Every derived cache filename folds in the metal, the active
SHADE and `defaults.METAL_SWAP_VERSION` ([Asset Recolor](asset_recolor.md)`.
letter_metal_file`, `.metal_variant_file`) so a shade switch or a future
recolor-math change never serves a stale PNG.

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

### Used by
- [Layers](layers.md) — hands, hexagram, weekday bodies, year marker
- [Watch Controller](../app/controller.md) — owns the instance, flushed via
  the compositor on screen change
- [Asset Recolor](asset_recolor.md) — `AssetCache._letter_recolored`,
  `._metal_swapped`, `._tinted` (the recolor kernels this module owns)
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
- `flush()`: drop everything (screen/DPI or skin change)
