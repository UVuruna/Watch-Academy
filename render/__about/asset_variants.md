# Asset Variants

**Script:** [Asset Variants (script)](../asset_variants.py) · **Flow:** [diagram](../__flow/asset_variants.md)

## Purpose
Disk-cached derived images that are NOT metal recolors: the working-set
downscale family, the moon-phase live render, the subdial plate
resolver, and two computed icon families (calendar wheel, solar
eclipse type). A surgical sibling of [Assets](assets.md) (God-File
Split Phase 2).

**The working set** (owner 2026-07-15): `working_ceiling(path)` names
each assets subtree's largest possible on-dial size; `warm_working_set`
pre-builds the downscaled copies on a background thread at startup;
`scaled_variant_file` is the disk-cached downscale
[Assets](assets.md)`.AssetCache.pixmap_by_height` routes any request
through whenever it fits under the ceiling — the SAME function the
Encyclopedia's hover tooltips call directly. `build=False` mode never
pays a cold decode+encode: it returns the ORIGINAL path when the cache
copy does not exist yet (GUI-thread readers), leaving `build=True` to
the background warm.

**The reverse edge to `assets.py`:** `AssetCache.pixmap_by_height`
reads `working_ceiling`/`scaled_variant_file` back from THIS module — a
genuine two-way dependency the split created (this module in turn
imports [Asset Recolor](asset_recolor.md), which imports `AssetCache`
from `assets.py`). `assets.py` breaks the resulting 3-file cycle with a
LOCAL import inside `pixmap_by_height`.

`moon_lit_region`/`moon_phase_image`/`moon_phase_file` (owner decree
2026-07-19, "bolje crtati na licu mesta nego 15MB fajlova"): the
terminator geometry shared with `YearMarkerLayer._draw_moon` so the
dial and the Encyclopedia's live render never drift apart, with an
exact-quarter degeneracy fix (fraction 0.25/0.75, where a zero-width Qt
ellipse used to collapse the phase to fully dark).

`subdial_plate_file(finish, tint=None)` reads the ACTIVE SET off
`config.paths.subdial_set()`, resolves a hand-drawn plate as-drawn or
[Asset Recolor](asset_recolor.md)-recolors the solo set live, and
returns `None` when no plate exists (the layer then draws a procedural
circle).

## Connections

### Uses
- [Assets](assets.md) — the reverse `pixmap_by_height` edge
- [Asset Recolor](asset_recolor.md) — `_recolored_plate`
  (`subdial_plate_file`), `tinted_pixmap` (`eclipse_solar_type_icon`)
- [Config (folder)](../../config/___config.md) — `paths`, `defaults`,
  `profiling`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `ring_face_color`,
  `moon_lit_region`, `subdial_plate_file` (paint-time reads)
- [Compositor](compositor.md) — `eclipse_solar_type_icon`,
  `scaled_variant_file` (hover-card image URIs)
- `app.encyclopedia`, `app.encyclopedia_warm` — `moon_phase_file`,
  `scaled_variant_file`
- `app.controller` — `warm_working_set`, `calendar_wheel_icon_file`

## Functions
- `ring_face_color(path)`: the ring art's median-luminance face sample
  (top-center column, ring of pixels a few steps deeper, median by
  luminance).
- `moon_lit_region(fraction, radius)` / `moon_phase_image(...)` /
  `moon_phase_file(...)`: the shared moon terminator geometry, its pure
  QImage render, and the disk-cached path wrapper.
- `subdial_plate_file(finish, tint=None)`: the active subdial set's
  plate, resolved/recolored/tinted as needed.
- `working_ceiling(path)` / `warm_working_set(progress=None)` /
  `scaled_variant_file(path, width, build=True)`: the working-set
  family.
- `eclipse_solar_type_icon(type_)`: the small per-type solar eclipse
  icon (annular gets a live tritone tint).
- `calendar_wheel_icon_file(size)`: a COMPUTED 12-wedge wheel glyph, no
  new art file (root Rule #19).

## Design Decisions
- **`calendar_wheel_icon_file` raises on a write failure** instead of
  falling back to an original — unlike every other cache function here,
  it has no source master to fall back to (Rule #1).
