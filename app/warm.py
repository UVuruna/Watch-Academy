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

1. **Dial art** (`render.art_warm`) — the jewel recolors the dials are
   currently standing in for with their gold masters. Each one repaints
   the dial the moment it lands.
2. **Working set, VISIBLE-FIRST then the rest** (owner bar 2026-08-09,
   MIGRATE-GUI Phase 1 — "the 75-second dead clock"): the ledger drain
   (`render.asset_variants.drain_pending_working`) FIRST, then the
   alphabetical whole-tree sweep (`warm_working_set`). The ledger holds
   exactly what the dial's own first paint(s) already asked for and
   skipped (`render.assets.AssetCache.pixmap_by_height` records a MISS
   instead of decoding the full-res original inline) — draining THAT
   first dresses the on-screen dial in a few seconds even stone-cold,
   instead of waiting on whichever subtree happens to sort first
   alphabetically. `warm_working_set` then finishes the rest (the
   trees/hours nothing has asked for yet); files the ledger already
   built are simply skipped (`cache.exists()`), so nothing doubles.
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

from pathlib import Path

from config import paths
from render import asset_index, raster_store
from render.art_warm import warm_pending_art
from render.asset_variants import drain_pending_working, warm_working_set

from app.encyclopedia_warm import warm_encyclopedia


def _collect_cache_garbage(progress=None, should_stop=None) -> None:
    """Phase 5's body: fingerprint the whole asset tree (memoized
    sampled reads — a few hundred MB scanned once), then sweep every
    cache entry no current source claims. Runs after every build phase
    so a freshly-built cache is never the thing being judged stale."""
    from time import perf_counter

    start = perf_counter()
    # THE INDEX, not a second walk (0.14.950): this used to rglob the
    # whole tree and call `source_prefix` — i.e. OPEN and sample 64 KiB
    # of — every png/svg/jpg in 3.76 GB, on every launch, purely to
    # decide which cache files were corpses. Phase 0 already knows every
    # one of those fingerprints, so `source_prefix` below answers from
    # the index (`raster_store`'s attached hook) without a single open.
    # The prefix is still built by `source_prefix` itself, from the same
    # `assets_dir()/rel` path string the cache writer used — the naming
    # and the collector can never drift apart (Rule #5).
    valid: set[str] = set()
    for path in asset_index.fingerprints_by_path():
        if should_stop is not None and should_stop():
            return
        valid.add(raster_store.source_prefix(Path(path)))
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
    # PHASE 0 — the asset index (0.14.950, the owner's 91.6-second
    # launch). It runs FIRST because every phase after it is a customer:
    # the working-set sweep reads widths from it, the Encyclopedia's
    # hundreds of `source_prefix` calls read fingerprints from it, and
    # the cache GC reads the whole roster from it. One `scandir` walk
    # (~0.015 s on the 3.76 GB tree) replaces three full-tree passes
    # that opened every file, every launch, to re-learn what had not
    # changed. See [Asset Index](../render/__about/asset_index.md).
    asset_index.refresh(should_stop=should_stop, progress=progress)
    if should_stop is not None and should_stop():
        return
    warm_pending_art(
        progress=progress, on_ready=on_art_ready, should_stop=should_stop
    )
    if should_stop is not None and should_stop():
        return
    # VISIBLE-FIRST (owner bar 2026-08-09): the ledger IS the active
    # skin's own referenced working-set art (recorded by the paint that
    # skipped it), so it lands — and repaints — before the exhaustive
    # alphabetical sweep below even starts.
    drain_pending_working(
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
