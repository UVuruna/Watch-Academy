"""The DIAL's own derived art, built off the GUI thread.

Owner decree 2026-07-28, after the slow-start measurement: a watch's
first paint on a cold raster cache ran 15 metal recolors — 3.6 s of numpy
(oklab conversion, guided box filter, specular ramp) INSIDE `paintEvent`,
once per open watch, so three watches meant ~15 s before any dial
appeared. The owner's ruling: "FIRST DEFAULT - recolor u pozadini. Kad
završi prikaže."

So the paint no longer recolors. `render.asset_recolor.letter_metal_file`
draws the GOLD MASTER while the derived finish is missing and RECORDS the
recipe in the lazy ledger; this module drains that ledger on the shared
background thread and calls back so the dial repaints in its real metal.

This is the FIRST warm phase — the pixels the user is actually looking at
come before the working-set downscales, the Encyclopedia inventory and
the hover sweep (`app.warm.run_warm` owns that order). It runs once per
PROCESS at startup, never once per watch (every watch shares one raster
cache, so N watches asking for the same file is one job, not N) — and
again ON DEMAND whenever a later paint observes a missing finish: a
finish/shade/theme switch records fresh recipes, `letter_metal_file`
rings `asset_recolor`'s stale notifier, and `app.watch_manager.
AppController.kick_art_warm` drains them (owner bug 2026-08-02 — the
startup-only drain left switched dials gold until restart).

See [Art Warm](art_warm.md).
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter

from config import defaults, profiling
from render.asset_recolor import ensure_variant, pending_art


@profiling.timed("Dial art warmup")
def warm_pending_art(progress=None, on_ready=None, should_stop=None) -> int:
    """Build every recorded-but-missing derived image. Returns how many
    were built.

    The batch runs on a SMALL THREAD POOL (0.14.704 — the owner's "10
    slova 10 sekundi je nedopustivo"): the pixel work is numpy, whose C
    loops release the GIL, so `defaults.ART_DRAIN_WORKERS` recolors
    genuinely overlap; `ensure_variant`'s per-path locks already make
    two threads meeting on the SAME file build it once, and it never
    touches QPixmap (the R1b law), so worker threads are legal.

    `on_ready` fires after EACH completed build (not once at the end) so
    the dial upgrades letter by letter instead of staying gold until the
    whole batch finishes. It is called from THIS thread — the completion
    loop, never a worker — and the controller's slot is connected across
    threads by Qt, so the repaint itself happens on the GUI thread.

    Repeats until the ledger stops growing: the GUI thread records new
    recipes while this runs (a paint that reaches art the previous pass
    had not seen), so one pass is not enough to leave the dial fully
    dressed. Each job is attempted AT MOST ONCE — `ensure_variant`
    returns the source file when a cache write fails (a full disk, a
    locked file), which leaves the job "pending" forever; without the
    attempted set that would be an endless loop instead of a dial that
    simply keeps its master art (Rule #1: degraded, visible, not hung).
    A `should_stop` request makes the not-yet-started jobs no-ops; the
    handful already in flight finish their file and stop."""
    start = perf_counter()
    built = 0
    attempted: set[str] = set()

    def build(path):
        if should_stop is not None and should_stop():
            return False
        ensure_variant(path)
        return True

    while True:
        jobs = [path for path in pending_art() if str(path) not in attempted]
        if not jobs:
            break
        if should_stop is not None and should_stop():
            return built
        attempted.update(str(path) for path in jobs)
        workers = max(1, min(defaults.ART_DRAIN_WORKERS, os.cpu_count() or 1))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(build, path) for path in jobs]
            for index, future in enumerate(as_completed(futures)):
                if not future.result():
                    continue
                built += 1
                if on_ready is not None:
                    on_ready()
                if progress is not None and (index + 1) % 5 == 0:
                    elapsed = perf_counter() - start
                    rate = (index + 1) / elapsed if elapsed > 0 else 0.0
                    progress(
                        f"[{elapsed:.1f}s] dial art {index + 1}/{len(jobs)} "
                        f"({(index + 1) / len(jobs) * 100:.0f}%) | {rate:.1f}/sec"
                    )
    if progress is not None and built:
        progress(
            f"[{perf_counter() - start:.1f}s] dial art complete — "
            f"{built} recolors built"
        )
    return built
