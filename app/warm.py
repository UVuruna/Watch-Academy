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
4. **Hover articles** — LAST, and only after the dials are dressed
   (owner: *"HOVER odloži dok se ne učita"*). It is the one phase that is
   pure Python, so it is the one phase that genuinely competes with the
   GUI thread for the GIL; running it first is what used to make a
   freshly launched dial feel stuck.

See [Warm](warm.md).
"""

from render.art_warm import warm_pending_art
from render.asset_variants import warm_working_set

from app.encyclopedia_warm import warm_encyclopedia


def run_warm(
    hover_sweeps=(), progress=None, on_art_ready=None, should_stop=None
) -> None:
    """Walk the four phases in order on ONE background thread.

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
