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
pre-builds the downscaled copies at startup — COLD builds run in a
small SUBPROCESS pool (0.14.706; a multi-MB QImage decode/scale/encode
holds the GIL for seconds, and on a mere thread that froze the GUI for
the owner's measured 75 s — child processes have their own GIL), with a
documented in-thread fallback when the pool cannot start;
`scaled_variant_file` is the disk-cached downscale
[Assets](assets.md)`.AssetCache.pixmap_by_height` routes any request
through whenever it fits under the ceiling — the SAME function the
Encyclopedia's hover tooltips call directly. `build=False` mode never
pays a cold decode+encode: it returns the ORIGINAL path when the cache
copy does not exist yet (GUI-thread readers), leaving `build=True` to
the background warm.

**The reverse edge to `assets.py`:** `AssetCache.pixmap_by_height`
reads `working_ceiling`/`working_variant_path`/`working_stale_notify`
back from THIS module — a genuine two-way dependency the split created
(this module in turn imports [Asset Recolor](asset_recolor.md), which
imports `AssetCache` from `assets.py`). `assets.py` breaks the
resulting 3-file cycle with a LOCAL import inside `pixmap_by_height`.

**THE LAZY WORKING-SET LEDGER** (owner bar 2026-08-09, MIGRATE-GUI
Phase 1 — "the 75-second dead clock"): mirrors `asset_recolor.py`'s
`_PENDING_VARIANTS`/`jewel_metal_path`/`pending_art`/`ensure_variant`/
`warm_pending_art` SHAPE for a different resource. Root cause: the GUI
paint path used to call `scaled_variant_file(path, ceiling)` with
`build=True` on a cache MISS — a multi-MB decode INSIDE `paintEvent`.
`working_variant_path(path, ceiling)` now only NAMES a working copy —
a header-only size check (no decode); a source already at or under the
ceiling is returned UNCHANGED and never recorded at all (the bug this
very round shipped once: treating EVERY asset under a covered subtree
as pending, icons and thumbnails included, made those permanently
invisible — `tests/test_startup_warm.py::
test_asset_at_or_under_the_ceiling_is_never_pending` pins the fix).
`pending_working()` lists every recorded recipe still missing —
in practice the ACTIVE skin's own referenced oversized art, because a
paint is what records it. `ensure_working_variant(path)` materializes
ONE entry (any thread, QImage end to end). `drain_pending_working(
progress=None, on_ready=None, should_stop=None)` is the multi-entry,
SUBPROCESS-pool batch drain (same reasoning as `warm_working_set`'s own
pool: a background THREAD doing this decode still starves the GUI
thread waiting for the GIL) — called by `app.warm.run_warm`'s
VISIBLE-FIRST phase (BEFORE the alphabetical whole-tree sweep, since
the ledger already holds exactly what the dial's first paint asked
for) and by `app.watch_manager.AppController.kick_working_warm` on
demand, installed as `set_working_stale_notifier`'s target.
`scaled_variant_file` itself is UNCHANGED and stays in service for its
own callers (hover tooltips, Encyclopedia cards/readers) — a distinct
cache the ledger does not cover.

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
- [Raster Store](raster_store.md) — every disk write is atomic
  (owner crash 2026-07-31: a half-written cache PNG must never be
  visible to a reader)
- [Asset Index](asset_index.md) — `widths_under`, which IS
  `warm_working_set`'s roster since 0.14.950. That sweep used to
  `rglob` five subtrees and open every PNG in them (2,511 files, 3.76
  GB) with `QImageReader` to read one integer per file, on every
  launch — the owner's `[91.6s] working set complete — 961 oversized
  sources, 0 built cold`
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
- `working_ceiling(path)` / `warm_working_set(progress=None,
  should_stop=None)` — its roster comes from
  [Asset Index](asset_index.md)'s `widths_under`, so it opens NOTHING
  to decide what is oversized; only the genuinely cold BUILDS cost
  anything, in their subprocess pool. `tests/test_startup_cost.py`
  asserts both halves of that: zero header reads, and the same
  oversized set the old open-every-file loop selected — speed that
  changed the answer would be worthless.
- `scaled_variant_file(path, width, build=True)` /
  `build_scaled_copy(source, cache, width)`: the working-set family —
  `build_scaled_copy` is the ONE build (plain-string args, no config
  reads) shared by every builder (`ensure_working_variant`,
  `drain_pending_working`'s subprocess workers, `warm_working_set`'s).
- `working_variant_path(path, ceiling)` / `pending_working()` /
  `ensure_working_variant(path)` / `drain_pending_working(progress=None,
  on_ready=None, should_stop=None)` / `set_working_stale_notifier(
  notifier)` / `working_stale_notify()`: THE LAZY WORKING-SET LEDGER
  (owner bar 2026-08-09) — see above.
- `eclipse_solar_type_icon(type_)`: the small per-type solar eclipse
  icon (annular gets a live tritone tint).
- `calendar_wheel_icon_file(size)`: a COMPUTED 12-wedge wheel glyph, no
  new art file (root Rule #19).

## Design Decisions
- **`calendar_wheel_icon_file` raises on a write failure** instead of
  falling back to an original — unlike every other cache function here,
  it has no source master to fall back to (Rule #1).
