# Warm

**Script:** [Warm (script)](../warm.py) · **Flow:** [diagram](../__flow/warm.md)

## Purpose
The ONE background warm for the whole process (owner ruling 2026-07-28:
every watch used to run its own warm thread, so N watches walked the
SAME working-set files, Encyclopedia paths and hover probes N times —
visible in the startup log as every progress line printed two/three
times). The watches share one asset tree, one raster cache and one
`AssetCache`, so the work is done ONCE, in a fixed priority order.

## Connections

### Uses
- [Art Warm](../../render/__about/art_warm.md) — phase 1, the letter recolors
- [Asset Variants](../../render/__about/asset_variants.md) — phase 2, working-set downscales
- [Encyclopedia Warm](encyclopedia_warm.md) — phase 3
- [Compositor](../../render/__about/compositor.md) — phase 4, through each watch's
  own `hover_sweep()` callable

### Used by
- [Watch Manager](watch_manager.md) — owns the background thread and arms it
  once every watch's first frame has painted

## Functions

### `run_warm(hover_sweeps=(), progress=None, on_art_ready=None, should_stop=None)`
Walks the four phases in order, on ONE background thread. `hover_sweeps`
is one callable per watch (each closes over its own compositor/dial
size) — they run last, one after another, never in parallel, so N
concurrent pure-Python sweeps never compete with each other for the GIL.
`should_stop` is checked between phases so Exit does not wait for a
90-second cold walk to finish (the thread is a daemon and would die with
the process anyway; the check just means it stops between files instead
of mid-write).

## Design Decisions
- **A free function, not a class** — it holds no state; the phases are
  ordered calls, and everything they need is passed in. The thread, the
  roster and the stop flag belong to [Watch Manager](watch_manager.md).
- **Hover articles run LAST, deliberately** — it is the one phase that
  is pure Python (the image phases release the GIL around their C-level
  codec/numpy calls; hover's `tooltip_at` dispatch does not), so it is
  the one phase that genuinely competes with the GUI thread. Running it
  first is what made a freshly launched dial feel stuck.
