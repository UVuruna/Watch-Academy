"""Background pre-materialization of the Encyclopedia's derived art
(owner order 2026-07-26: opening the Encyclopedia BLOCKED the main
thread for minutes whenever an art wave invalidated the mtime-keyed
raster cache — the metal recolors used to build eagerly at dialog
construction). The topic table now records paths only; THIS walk, on
the controller's existing warm thread, builds every recorded metal
variant, the Moon phase plates and the decode-ceiling downscales the
gallery/reader read — so a dialog open finds everything ready, and a
user who outruns the warm pays at most the OPEN page's few images.
See [Encyclopedia Warm](encyclopedia_warm.md).
"""

from time import perf_counter

from config import encyclopedia_ui, paths, profiling
from render.asset_recolor import ensure_variant, variant_pending
from render.asset_variants import scaled_variant_file

from app.encyclopedia import topics as encyclopedia_topics


def _jobs() -> list:
    """(path, decode ceiling) for everything the Encyclopedia can show,
    DEDUPLICATED, gallery card icons first (the first screen every open
    shows), then every entry's look/image paths in topic order.
    `app.encyclopedia.topics()` is the single inventory (Rule #5) — no
    second theme/plate list to drift out of sync. Building it here also
    renders the eight Moon phase plates into the raster cache (QImage
    end to end — safe off the GUI thread)."""
    topics = encyclopedia_topics()
    jobs: list = []
    seen: set[str] = set()

    def add(raw, ceiling: int) -> None:
        if raw is None or str(raw) in seen:
            return
        seen.add(str(raw))
        jobs.append((raw, ceiling))

    for topic in topics.values():
        add(topic["icon"], encyclopedia_ui.ENCYCLOPEDIA_CARD_ICON_DECODE_PX)
    for topic in topics.values():
        for entry in topic["entries"]:
            looks = entry.get("looks") or (
                ("", (tuple(entry.get("images", ())),)),
            )
            for _label, rows in looks:
                for row in rows:
                    for path in row:
                        add(
                            path,
                            encyclopedia_ui.ENCYCLOPEDIA_READER_DECODE_CEILING_PX,
                        )
    return jobs


@profiling.timed("Encyclopedia warmup")
def warm_encyclopedia(progress=None, should_stop=None) -> int:
    """Materialize every recorded-but-missing metal variant and every
    oversized source's decode-ceiling downscale — a no-op once warm.
    Returns how many missing metal variants were materialized (the
    downscales build too, uncounted — `scaled_variant_file` is its own
    cheap no-op once cached). Progress (Rule #10): one line per 25
    jobs with elapsed, done/total, percentage and rate."""
    start = perf_counter()
    jobs = _jobs()
    total = len(jobs)
    built = 0
    for index, (raw, ceiling) in enumerate(jobs):
        if should_stop is not None and should_stop():
            return built
        path = paths.art_file(raw)
        if path is None:
            continue
        if variant_pending(path):
            ensure_variant(path)
            built += 1
        if path.exists():
            scaled_variant_file(path, ceiling)
        if progress is not None and (index + 1) % 25 == 0:
            elapsed = perf_counter() - start
            rate = (index + 1) / elapsed if elapsed > 0 else 0.0
            progress(
                f"[{elapsed:.1f}s] encyclopedia warm {index + 1}/{total} "
                f"({(index + 1) / total * 100:.0f}%) | {rate:.0f}/sec"
            )
    if progress is not None and total:
        progress(
            f"[{perf_counter() - start:.1f}s] encyclopedia warm complete — "
            f"{total} paths walked"
        )
    return built
