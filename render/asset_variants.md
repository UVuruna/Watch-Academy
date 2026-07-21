# Asset Variants

**Script:** [Asset Variants (script)](asset_variants.py)

## Purpose
Disk-cached derived images that are NOT metal recolors — downscaled
"working set" copies, the moon-phase live render, the subdial plate
resolver, and the two computed icon families (calendar wheel, solar
eclipse type). Extracted out of `assets.py` (God-File Split Phase 2,
Step 1, `research/REFACTOR_PLAN.md` §8: a surgical sibling of
[Assets](assets.md), which keeps `AssetCache` at its own import path
unchanged for its 20+ callers).

**The working set** (owner 2026-07-15): originals ship at full
resolution; the dial decodes through a once-per-file DOWNSCALED copy
instead — `working_ceiling()` names each assets subtree's largest
possible on-dial size (`defaults.WORKING_SET_CEILINGS`: earth/weekday
800 px, zodiac/badge 1200 px, from 1440 dial x 200% scale x 200%
enlarge), `warm_working_set()` pre-builds the copies on a background
thread at startup (idempotent, progress-logged), and
`scaled_variant_file()` is the underlying disk-cached downscale that
[Assets](assets.md)`.AssetCache.pixmap_by_height` routes any request
through whenever it fits under the ceiling (oversized requests keep
the original, small sources stay untouched) — the SAME function the
Encyclopedia's hover tooltips call directly for their own downscale
(owner 2026-07-13: a hover popup shows at most a quarter of an 800x800
plate; callers pass 2x the display width so the tooltip still
downsamples for crispness). `_scaled_cache_path()` names where a given
(path, width) downscale lives on disk — the source STEM rides the name
so a derived file is human-readable.

**The reverse edge to `assets.py`:** `AssetCache.pixmap_by_height`
reads `working_ceiling`/`scaled_variant_file` back from THIS module —
a genuine two-way dependency the split created (this module in turn
imports [Asset Recolor](asset_recolor.md), which imports `AssetCache`
from `assets.py` — a 3-file cycle if every edge were resolved at
import time). `assets.py` breaks it with a LOCAL import inside
`pixmap_by_height` instead of a module-level one, so by the time that
method is actually CALLED all three modules have already finished
loading regardless of which one a caller happens to import first; see
that method's own comment.

`ring_face_color()` — the ring art's own FACE color, the slot-roundel
fill (owner 2026-07-14: "boja unutar kruga je RING preset boja").
Sampled once per file: walk the top center column to the first opaque
band, then read a ring of pixels a few steps deeper and take the MEDIAN
by luminance, so numerals and ticks (the bright minority) never win.
Missing/unreadable art falls back to the documented color.

`moon_lit_region(fraction, radius)` / `moon_phase_image(fraction, size,
master=None)` / `moon_phase_file(fraction, name, size=800)` (owner
decree 2026-07-19, "bolje crtati na licu mesta nego 15MB fajlova" —
retires the Encyclopedia's eight pre-baked Moon-phase plates):
`moon_lit_region` is the terminator geometry extracted out of
[Layers](layers.md)`.YearMarkerLayer._draw_moon` so the dial and the
Encyclopedia's live render share ONE function and never drift apart —
fixing an exact-quarter degeneracy (fraction 0.25/0.75) where Qt's
`addEllipse` on a zero-width terminator rect used to degenerate the
union/difference to an EMPTY path, i.e. a moon rendered fully DARK
instead of exactly half-lit; `moon_phase_image` is the pure QImage
render (mirrors `_draw_moon`'s two branches exactly, including the
graceful fallback when the master asset is missing); `moon_phase_file`
is its disk-cached path wrapper for the Encyclopedia's path-based image
tuples.

`subdial_plate_file(finish, tint=None)` — reworked in the Rsub round
(owner decree 2026-07-21), which RETIRES Rule #19's first enforcement
(owner decree 2026-07-20, "Compute, Don't Generate") for this family:
the subdial plate stops being a Rule #19 one-master-per-art-source case
at all. It reads the ACTIVE SET off `config.paths.subdial_set()` — a
module global mirroring the art-source switch exactly (set by
`app.controller.apply_display_settings` from `Settings.subdial_set`),
chosen this way specifically so the function's OWN signature never had
to change and [Layers](layers.md)`.draw_slot_roundel`'s existing call
stays untouched. Five hand-picked sets live under `assets/subdial/`
(see [Assets (folder)](../assets/___assets.md) for why that root sits
OUTSIDE `ART_SOURCED_ROOTS`): for "set1".."set4" the matching hand-
drawn file (`assets/subdial/<set>/<finish>.png`) returns AS DRAWN — no
recolor, no cache entry. For "solo" the one hand-drawn file (silver,
`defaults.SUBDIAL_SOLO_FINISH`) returns AS DRAWN; gold/bronze are
[Asset Recolor](asset_recolor.md)`._recolored_plate()`-ed from it live.
A TINT (the "theme" plate style, owner A/B spec 2026-07-15) recolors
the dark tapisserie field to the clock tint on TOP of whichever plate
above was resolved. Returns `None` when no plate art exists for the
active set — the layer then draws the procedural circle. The SEAT
still never reaches the file at all, only the LIVE shadow the layer
draws ([Layers](layers.md)`._draw_subdial_shadow`).

`eclipse_solar_type_icon(type_)` (ECLIPSE ICON WIRING round, owner
2026-07-20/21 — the solar pick is PROPOSED, not yet owner-confirmed the
way lunar's red/gold/blue set is; see `defaults.
ECLIPSE_SOLAR_TYPE_ICON_SOURCE`'s own docstring for the shape-matched
mapping): the small per-type SOLAR eclipse icon. Total and partial ride
their source file AS DRAWN; annular is TRITONE-tinted toward `defaults.
GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR` (the SAME "ring of fire" color the
dial's own annular glow already uses — Rule #5) via [Asset
Recolor](asset_recolor.md)`.tinted_pixmap`, disk-cached. `None` for an
unknown type or a source that has not landed (Rule #1, graceful-
absent).

`calendar_wheel_icon_file(size)` (Rule #19 — a COMPUTED 12-wedge wheel
glyph, no new art file, for the Fast Travel Flash's Calendar theme,
replacing the plain calendar-emoji fallback, owner ask, ECLIPSE ICON
WIRING round 2026-07-20/21): 12 alternating wedges in `defaults.
CALENDAR_ICON_WEDGE_COLORS` (the app's own gold ramp) with a thin dark
ring for contrast against the flash's dark background. Disk-cached by
SIZE alone. There is no source master to fall back to on a write
failure (unlike every other cache function here), so a failed save
raises rather than silently returning an uncached path (Rule #1).

## Connections

### Uses
- [Assets](assets.md) — the reverse `pixmap_by_height` edge described
  above
- [Asset Recolor](asset_recolor.md) — `_recolored_plate`
  (`subdial_plate_file`), `tinted_pixmap` (`eclipse_solar_type_icon`)
- `config.paths` (`art_file`, `subdial_set`, `settings_path`,
  `assets_dir`), `config.defaults`, `config.profiling`
- PySide6 QtGui/QtCore

### Used by
- [Layers](layers.md) — `ring_face_color`, `moon_lit_region`,
  `subdial_plate_file` (paint-time reads)
- [Compositor](compositor.md) — `eclipse_solar_type_icon`,
  `scaled_variant_file` (hover-card image URIs)
- [Encyclopedia](../app/encyclopedia.md) — `moon_phase_file` (the Moon
  topic's live-rendered pages)
- [Watch Controller](../app/controller.md) — `warm_working_set`,
  `calendar_wheel_icon_file` (Calendar Fast Travel icon)
- [Tests (folder)](../tests/___tests.md) — `scaled_variant_file` (hover
  URI pins), `working_ceiling`/`warm_working_set` (working-set golden
  tests)

## Functions

- `ring_face_color(path)`: the ring art's median-luminance face sample
- `moon_lit_region(fraction, radius)`: the shared moon terminator
  geometry
- `moon_phase_image(fraction, size, master=None)`: the pure QImage
  render
- `moon_phase_file(fraction, name, size=800)`: its disk-cached path
  wrapper
- `subdial_plate_file(finish, tint=None)`: the active subdial set's
  plate, resolved/recolored/tinted as needed
- `working_ceiling(path)`: the working-set ceiling for an asset's
  subtree
- `warm_working_set(progress=None)`: background-thread working-set
  warmup
- `scaled_variant_file(path, width)`: a disk-cached downscaled copy
- `eclipse_solar_type_icon(type_)`: the small per-type solar eclipse
  icon
- `calendar_wheel_icon_file(size)`: the computed 12-wedge calendar icon
