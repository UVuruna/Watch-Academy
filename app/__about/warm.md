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
- [Raster Store](../../render/__about/raster_store.md) — phase 5
  (0.14.709), `_collect_cache_garbage`: fingerprint the asset tree,
  sweep every cache entry no current source claims (the measured
  backlog was 10,039 files / 10.0 GB)
- [Config (folder)](../../config/___config.md) — `paths` (the asset
  walk and the cache directory)

### Used by
- [Watch Manager](watch_manager.md) — owns the background thread and arms it
  once every watch's first frame has painted

## Functions

### `run_warm(hover_sweeps=(), progress=None, on_art_ready=None, should_stop=None)`
Walks the five phases in order, on ONE background thread. `hover_sweeps`
is one callable per watch (each closes over its own compositor/dial
size) — they run one after another, never in parallel, so N
concurrent pure-Python sweeps never compete with each other for the GIL.
`should_stop` is checked between phases so Exit does not wait for a
90-second cold walk to finish (the thread is a daemon and would die with
the process anyway; the check just means it stops between files instead
of mid-write).

## Design Decisions
- **A free function, not a class** — it holds no state; the phases are
  ordered calls, and everything they need is passed in. The thread, the
  roster and the stop flag belong to [Watch Manager](watch_manager.md).
- **A background THREAD does not shield the GUI from image work** —
  the correction the 0.14.706 round wrote in blood: this doc used to
  claim "the image phases release the GIL around their C-level codec
  calls", and they DON'T — a multi-MB `QImage` decode/scale/encode
  holds the GIL for seconds, which is exactly the owner's 75-second
  unmovable window. That is why the working set's COLD builds now run
  in subprocesses ([Asset Variants](../../render/__about/asset_variants.md));
  numpy (the recolors) genuinely does release the GIL, so the art drain
  may stay on threads.
- **Hover articles run after the builds, deliberately** — pure Python,
  so it is the phase that competes hardest with the GUI thread for the
  GIL. Running it first is what made a freshly launched dial feel stuck.
- **Cache GC runs dead last** — pure disk hygiene must never delay a
  pixel anyone is waiting for, and running after every build phase
  means a freshly-built cache is never the thing being judged stale.
