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

**ADAPTIVE gold/bronze recolor (owner COLORS verdict 2026-07-20/21,
ART-INFRA round — "SILVER JE SOLIDAN u oba [letter i badge], LETTER
BRONZE i BADGE GOLD" needed a rethink):** the retired flat recipes —
letter bronze's straight per-channel multiply, badge gold's flat
hue/sat/val remap — both read muddy/grayish depending on how bright or
dark the SOURCE art happened to render. Replaced by a shared engine,
module-level (not private to `AssetCache`, both `_bronzed` and
`_metal_swapped` call it): `_metal_ramp_rgb(hue_deg)` builds a 5-step
(saturation, value) ramp at any hue from `defaults.
GOLD_RAMP_SAT_VAL_STEPS` (sampled off the owner's own
`UV/DESIGN/gold pallete.png` reference); `_percentile_stretch(values,
mask, low_pct, high_pct)` contrast-stretches the SOURCE's own masked-
region lightness so its 5th-95th percentile lands on [0, 1] — the
owner's "računamo početno stanje" ask, an over-bright and an over-dark
source both normalize to the same range; `_ramp_lookup(stretched,
ramp)` walks the stretched value through the ramp. `AssetCache.
_bronzed` (letters) and the "gold" branch of `AssetCache.
_metal_swapped` (badges) both run stretch-then-lookup now; SILVER is
UNTOUCHED in both (`_desaturated` and `_metal_swapped`'s "silver"
branch keep their original flat recipes verbatim — the owner's "SILVER
JE SOLIDAN"). Every cache key carrying either recipe's output
(`letter_metal_file`, `metal_variant_file`) folds in
`defaults.ADAPTIVE_METAL_RECOLOR_VERSION` so a future curve change
invalidates stale PNGs instead of serving the old recipe forever.

Module helpers beyond the cache: `ring_face_color()` (the ring art's
median-luminance face sample, the procedural subdial fill),
`metal_variant_file()` / `scaled_variant_file()` (disk-cached derived
images), `letter_metal_file(path, metal)` (owner decree 2026-07-19,
"bolje crtati na licu mesta nego 15MB fajlova" — retired the ~15 MB of
pre-rendered `<Stem>_silver.png`/`<Stem>_bronze.png` ring-letter files
and their two generator scripts: silver is a straight grayscale
desaturation of the gold master, `AssetCache._desaturated`; bronze the
ADAPTIVE ramp recolor off the silver result, `AssetCache._bronzed`
(see above — this WAS a straight per-channel multiply, superseded the
same round the ADAPTIVE engine landed), disk-cached like every other
derived asset; `metal="gold"` is a no-op passthrough),
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
