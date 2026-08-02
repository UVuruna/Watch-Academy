"""The disk raster cache's own module — HOW a derived image lands on
disk safely, and WHAT a cache file is named after (see
[Raster Store](__about/raster_store.md)).

Two invariants live here:

1. **Complete or absent** (owner crash 2026-07-31): `ensure_variant`
   wrote a letter recolor straight to its final cache path while the
   GUI thread was painting; the path "existed" the moment the encoder
   opened it, `letter_metal_file` handed the half-written PNG to
   `pixmap_by_height`, and the resulting `ValueError` escaped
   `paintEvent` with the `QPainter` still active — a cascade of
   `QBackingStore::endPaint` errors and a dead window. `atomic_save`
   is the answer: a reader that sees a cache file can always decode it.

2. **Names follow CONTENT, not mtime** (0.14.708): every cache name
   used to embed the source's `int(st_mtime)`, and every git operation
   rewrites mtimes without changing a pixel — one checkout orphaned the
   ENTIRE multi-GB cache and the next launch re-paid every recolor and
   downscale cold (the owner's 75-second start). `source_prefix` keys a
   name by a sampled content fingerprint instead: a touched-but-equal
   file keeps its cache, a genuinely changed file gets a new name, and
   the orphaned old names are what `collect_garbage` sweeps.

Deliberately dependency-light (standard library only): the working-set
subprocess workers import this without dragging anything else in.
"""

import hashlib
import os
import threading
from pathlib import Path

# The sampled fingerprint window: size + first 64 KiB + last 4 KiB.
# Small sources (every ring letter) are covered whole; for large photo
# art any pixel change ripples the PNG/JPEG compression stream, so the
# head+tail sample catches real edits without reading gigabytes at
# startup. Documented limit: a same-size edit that leaves both windows
# byte-identical keeps the old name — no compressed raster format
# produced by an editor does that in practice.
_FINGERPRINT_HEAD = 64 * 1024
_FINGERPRINT_TAIL = 4 * 1024

# In-process memo: path -> (size, mtime_ns, digest). Keyed by stat, so
# a steady-state fingerprint costs one stat + one dict hit — cheap
# enough for path-resolution call sites on the GUI thread. A file whose
# stat changed is simply re-read (~0.2 ms for the sampled windows).
_FINGERPRINTS: dict[str, tuple[int, int, str]] = {}
_FINGERPRINTS_LOCK = threading.Lock()


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


def fingerprint(path: Path) -> str:
    """A 12-hex CONTENT key for a source file — sha1 over (size, first
    64 KiB, last 4 KiB), memoized by (size, mtime_ns) so the steady
    state costs one `stat`. Survives what mtime keys never did: git
    checkouts, art re-saves with identical bytes, backup restores."""
    stat = path.stat()
    key = str(path)
    with _FINGERPRINTS_LOCK:
        cached = _FINGERPRINTS.get(key)
    if (
        cached is not None
        and cached[0] == stat.st_size
        and cached[1] == stat.st_mtime_ns
    ):
        return cached[2]
    digest = hashlib.sha1(str(stat.st_size).encode("ascii"))
    with open(path, "rb") as handle:
        digest.update(handle.read(_FINGERPRINT_HEAD))
        if stat.st_size > _FINGERPRINT_HEAD + _FINGERPRINT_TAIL:
            handle.seek(-_FINGERPRINT_TAIL, os.SEEK_END)
            digest.update(handle.read(_FINGERPRINT_TAIL))
    value = digest.hexdigest()[:12]
    with _FINGERPRINTS_LOCK:
        _FINGERPRINTS[key] = (stat.st_size, stat.st_mtime_ns, value)
    return value


def source_prefix(path: Path) -> str:
    """THE leading pair every cache name derived from `path` starts
    with: `<16-hex path stamp>_<12-hex content fingerprint>`. The one
    naming function all cache-path builders AND `collect_garbage` share
    — they can never drift apart. A missing source fingerprints as `0`
    (the documented graceful-absent convention)."""
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    if not path.exists():
        return f"{stamp}_0"
    return f"{stamp}_{fingerprint(path)}"
