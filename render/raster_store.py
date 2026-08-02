"""The disk raster cache's safety layer — atomic writes for every
derived image (see [Raster Store](__about/raster_store.md)).

Owner crash 2026-07-31: `ensure_variant` wrote a letter recolor straight
to its final cache path while the GUI thread was painting; the path
"existed" the moment the encoder opened it, `letter_metal_file` handed
the half-written PNG to `pixmap_by_height`, and the resulting
`ValueError` escaped `paintEvent` with the `QPainter` still active —
a cascade of `QBackingStore::endPaint` errors and a dead window. The
invariant this module owns: a cache file on disk is either COMPLETE or
ABSENT, never in between.

Deliberately dependency-light (standard library only): the working-set
subprocess workers import this without dragging anything else in.
"""

import os
from pathlib import Path


def atomic_save(image, path: Path) -> None:
    """Save `image` (any Qt image object whose `.save(str)` returns a
    success bool — `QImage`, `QPixmap`) to `path` so that the
    destination appears ATOMICALLY: the encoder writes a sibling
    `.part` file and `os.replace` publishes it in one step. A reader
    that sees `path` exist can always decode it.

    Raises `OSError` on an encode or rename failure, with the partial
    file removed first — callers keep their documented "a cold cache is
    only slower, never wrong" master-path fallbacks.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    try:
        if not image.save(str(partial), "PNG"):
            raise OSError(f"image encode returned False for {path}")
        os.replace(partial, path)
    except OSError:
        partial.unlink(missing_ok=True)
        raise
