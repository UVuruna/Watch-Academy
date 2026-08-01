# Encyclopedia Warm

**Script:** [Encyclopedia Warm (script)](../encyclopedia_warm.py) · **Flow:** [diagram](../__flow/encyclopedia_warm.md)

## Purpose
Background pre-materialization of everything the Encyclopedia can ever
show: every recorded metal variant (gold/silver recolors), the eight
live-rendered Moon phase plates, and the disk-cached downscales the
gallery cards and reader pages decode from. Runs once per app start on
the shared warm thread (phase 3 of [Warm](warm.md)), right after the
working-set warmup — a no-op once every derived file already exists.

The other half of the never-block guarantee lives in the Encyclopedia
itself: its topic table records paths only, and a page's first display
materializes just its own few images — so a user who opens the
Encyclopedia before this warm has finished never waits for more than the
open page.

## Connections

### Uses
- [Encyclopedia (subfolder)](../encyclopedia/___encyclopedia.md) —
  `topics()` is the single inventory: every topic's card icon and every
  entry's look/image paths, walked here exactly as the dialog would
  resolve them
- [Asset Recolor](../../render/__about/asset_recolor.md) — `ensure_variant` /
  `variant_pending` materialize the recorded gold/silver recolors
- [Asset Variants](../../render/__about/asset_variants.md) — `scaled_variant_file`
  builds the decode-ceiling downscales the reader later reads with
  `build=False`
- [Config (folder)](../../config/___config.md) — the two decode ceilings
  (`encyclopedia_ui.ENCYCLOPEDIA_CARD_ICON_DECODE_PX`,
  `ENCYCLOPEDIA_READER_DECODE_CEILING_PX`)

### Used by
- [Watch Controller](controller.md) — chains this after the working-set
  warmup and the hover-article sweep, on the same daemon thread
- [Warm](warm.md) — phase 3 of the shared background walk

## Functions

### `_jobs() -> list[(path, decode_ceiling)]`
Every path the Encyclopedia can show, DEDUPLICATED — gallery card icons
first (the first screen every open shows), then every entry's look/image
paths in topic order. `app.encyclopedia.topics()` is the single
inventory (Rule #5) — no second theme/plate list to drift out of sync.

### `warm_encyclopedia(progress=None, should_stop=None) -> int`
Walks `_jobs()`: for each still-missing recorded metal variant, builds
it now (`ensure_variant`); for each file wider than its decode ceiling,
builds its disk-cached downscale. Returns how many new metal variants
were materialized. Progress every 25 jobs (Rule #10: elapsed,
done/total, percentage, rate).

## Design Decisions
- **A separate module, not folded into a bigger one** — the warm walk is
  its own responsibility (background I/O, no widgets) and must be
  importable without the Encyclopedia dialog machinery.
- **Gallery icons warm first** — the gallery is the first screen every
  open shows.
- **`topics()` is the single inventory** (Rule #5) — whatever the dialog
  would show is exactly what warms; no second theme/plate list exists to
  drift out of sync.
- Thread-safe by construction: QImage end to end, per-path locks inside
  `ensure_variant` — the GUI thread's first-display build and this
  background warm meeting on the SAME file build it exactly once.
