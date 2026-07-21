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
  letter BRONZE, never badge bronze).
- `AssetCache._letter_recolored(source, metal, shade)` (ring letters,
  called from the module-level `letter_metal_file`): the mask is the
  WHOLE opaque glyph (weight 1 wherever alpha > 0) — a letter mixes no
  gray stone the way a medallion does, so every drawn pixel already IS
  the metal. ALL THREE metals run through this now, including gold —
  the old "gold is a no-op passthrough" shortcut is gone now that gold
  itself has five selectable shades; the DEFAULT "classic" shade is
  tuned to read close to the retired passthrough's look.

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
SHADE and `defaults.METAL_SWAP_VERSION` (`letter_metal_file`,
`metal_variant_file`) so a shade switch or a future recolor-math change
never serves a stale PNG.

**The Settings side:** `Settings.metal_shade_gold/_bronze/_silver`
(`app/settings_store.md`) persist the pick; `app.controller.
apply_display_settings` pushes them into `config.paths` module globals
(`set_metal_shade`/`metal_shade`, mirroring `set_subdial_set`'s exact
pattern — ONE global per metal because it is a single user preference
reached from many render call sites, never threaded as a parameter);
`app.settings_dialog._build_metal_shade_group` (`app/settings_dialog.md`)
is the picker, one combo per metal, filed in Themes beside the Subdial
plate picker.

Module helpers beyond the cache: `ring_face_color()` (the ring art's
median-luminance face sample, the procedural subdial fill),
`metal_variant_file()` / `scaled_variant_file()` (disk-cached derived
images), `letter_metal_file(path, metal)` (owner decree 2026-07-19,
"bolje crtati na licu mesta nego 15MB fajlova" — retired the ~15 MB of
pre-rendered `<Stem>_silver.png`/`<Stem>_bronze.png` ring-letter files
and their two generator scripts; now SHADE-aware, see above — every
metal, including gold, is disk-cached per (file, metal, shade)),
`eclipse_solar_type_icon(type_)` (ECLIPSE ICON WIRING round — the
small per-type solar icon: total/partial ride their
`assets/icons/sun_eclipse{,'2'}.png` source as drawn, annular is
TRITONE-tinted toward `defaults.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR` via
`tinted_pixmap`, disk-cached; a PROPOSED mapping, not owner-confirmed
the way lunar's red/gold/blue set is — see `defaults.
ECLIPSE_SOLAR_TYPE_ICON_SOURCE`'s own docstring),
`calendar_wheel_icon_file(size)` (Rule #19 — a COMPUTED 12-wedge wheel
glyph, no new art file, replacing the Fast Travel Flash's plain 📅
fallback for the Calendar theme; disk-cached by size alone, no source
master to fall back to on a write failure so a failed save raises),
`moon_lit_region(fraction,
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
