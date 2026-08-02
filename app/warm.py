"""The ONE background warm — process-wide, priority-ordered.

Owner ruling 2026-07-28: *"zašto bi se stvari učitavale više puta za
svaki sat kada svi dele iste ??? čovjek dakle samo 1 treba da se učitava
u ram u slike ili god !!!"*

Every watch used to start its OWN warm thread in `WatchController.run()`,
so N watches walked the SAME 795 working-set files, the SAME 698
Encyclopedia paths and the SAME hover grid N times over — visible in the
owner's startup log as every progress line printed two and three times.
They share one asset tree, one raster cache and (now) one `AssetCache`,
so the work is done ONCE for the process.

THE ORDER is the priority the owner asked for — what he is looking at
first, what he might look at last:

1. **Dial art** (`render.art_warm`) — the letter recolors the dials are
   currently standing in for with their gold masters. Each one repaints
   the dial the moment it lands.
2. **Working set** — the downscaled dial copies of oversized sources.
3. **Encyclopedia** — every metal variant and decode ceiling a page can
   ask for.
4. **Hover articles** — LAST of the build phases, and only after the
   dials are dressed (owner: *"HOVER odloži dok se ne učita"*). It is
   the one phase that is pure Python, so it is the one phase that
   genuinely competes with the GUI thread for the GIL; running it first
   is what used to make a freshly launched dial feel stuck.
5. **Cache garbage collection** (0.14.709) — dead last, pure disk
   hygiene: sweep `raster_cache` of every entry whose source no longer
   exists with that content (`raster_store.collect_garbage`). Nothing
   ever deleted a stale entry before; the measured backlog was 10,039
   files / 10.0 GB of mtime-era corpses.

See [Warm](warm.md).
"""

from config import paths
from render import raster_store
from render.art_warm import warm_pending_art
from render.asset_variants import warm_working_set

from app.encyclopedia_warm import warm_encyclopedia

#: Source suffixes that can seed a cache entry — the GC walk validates
#: every stamped cache name against these files' current fingerprints.
_GC_SOURCE_SUFFIXES = {".png", ".svg", ".jpg", ".jpeg"}


def _collect_cache_garbage(progress=None, should_stop=None) -> None:
    """Phase 5's body: fingerprint the whole asset tree (memoized
    sampled reads — a few hundred MB scanned once), then sweep every
    cache entry no current source claims. Runs after every build phase
    so a freshly-built cache is never the thing being judged stale."""
    from time import perf_counter

    start = perf_counter()
    valid: set[str] = set()
    for source in paths.assets_dir().rglob("*"):
        if should_stop is not None and should_stop():
            return
        if source.suffix.lower() in _GC_SOURCE_SUFFIXES and source.is_file():
            valid.add(raster_store.source_prefix(source))
    removed, freed = raster_store.collect_garbage(
        paths.settings_path().parent / "raster_cache", valid,
        progress=progress,
    )
    if progress is not None:
        progress(
            f"[{perf_counter() - start:.1f}s] cache gc complete — "
            f"{removed} stale files, {freed / 2**20:.0f} MB freed"
        )


def run_warm(
    hover_sweeps=(), progress=None, on_art_ready=None, should_stop=None
) -> None:
    """Walk the five phases in order on ONE background thread.

    `hover_sweeps` is a callable per watch (each closes over its own
    compositor and dial size); they run last, one after another, never in
    parallel — the point is to stay out of the GUI thread's way, and N
    concurrent Python sweeps would do the opposite.
    """
    warm_pending_art(
        progress=progress, on_ready=on_art_ready, should_stop=should_stop
    )
    if should_stop is not None and should_stop():
        return
    warm_working_set(progress=progress, should_stop=should_stop)
    if should_stop is not None and should_stop():
        return
    warm_encyclopedia(progress=progress, should_stop=should_stop)
    for sweep in hover_sweeps:
        if should_stop is not None and should_stop():
            return
        sweep()
    if should_stop is not None and should_stop():
        return
    _collect_cache_garbage(progress=progress, should_stop=should_stop)
