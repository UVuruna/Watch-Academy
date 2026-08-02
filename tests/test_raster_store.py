"""THE HALF-WRITTEN CACHE FILE (owner crash log 2026-07-31) — the pins.

The background art warm used to write a letter recolor STRAIGHT to its
final cache path; the GUI thread's unlocked `exists()` check saw the
path the moment the encoder opened it, `pixmap_by_height` decoded a
truncated PNG, and the `ValueError` escaped `paintEvent` with the
`QPainter` still active — `QBackingStore::endPaint` cascade, dead
window (`UV/starting_log.txt`). The law pinned here: a raster-cache
file on disk is either COMPLETE or ABSENT — the encoder writes a
`.part` sibling and `os.replace` publishes it in one atomic step.
"""

import os

import pytest
from PySide6.QtGui import QColor, QImage

from render.raster_store import atomic_save, fingerprint, source_prefix


def _image() -> QImage:
    image = QImage(4, 4, QImage.Format.Format_ARGB32)
    image.fill(QColor("#C9CDD4"))
    return image


def test_atomic_save_publishes_a_complete_decodable_file(tmp_path):
    target = tmp_path / "cache" / "letter_gold_classic_v6.png"
    atomic_save(_image(), target)

    assert target.exists()
    assert not QImage(str(target)).isNull(), "published file must decode"
    assert list(tmp_path.rglob("*.part")) == [], "no partial file left behind"


def test_the_encoder_never_touches_the_final_path(tmp_path):
    """The mechanism itself: pixels stream into the `.part` sibling; the
    final path appears only through `os.replace` — so a concurrent
    reader can never observe a half-written destination."""
    target = tmp_path / "variant.png"
    seen = []

    class Encoder:
        def save(self, path, _format=None):
            seen.append(path)
            with open(path, "wb") as handle:
                handle.write(b"pixels")
            return True

    atomic_save(Encoder(), target)

    assert seen == [str(target.with_name(target.name + ".part"))]
    assert target.read_bytes() == b"pixels"


def test_a_failed_encode_leaves_nothing_and_raises(tmp_path):
    """A cold cache is only slower, never wrong (Rule #1) — but a FAILED
    write must not leave a corpse the next `exists()` check trusts."""
    target = tmp_path / "variant.png"

    class BrokenEncoder:
        def save(self, path, _format=None):
            with open(path, "wb") as handle:
                handle.write(b"trunc")   # the crash scenario: partial bytes
            return False

    with pytest.raises(OSError):
        atomic_save(BrokenEncoder(), target)

    assert not target.exists()
    assert list(tmp_path.rglob("*.part")) == [], "partial file must be removed"


def test_fingerprint_survives_a_git_touch(tmp_path):
    """THE COLD-START CAUSE (0.14.708): cache names carried the source
    mtime, and a git checkout rewrites mtimes without changing a pixel
    — one checkout orphaned the whole multi-GB cache. The law: same
    bytes, same fingerprint, whatever the timestamps say; changed
    bytes, new fingerprint."""
    source = tmp_path / "letter.png"
    source.write_bytes(b"\x89PNG-golden-letter-bytes" * 100)
    original = fingerprint(source)

    stat = source.stat()
    os.utime(source, (stat.st_atime + 3600, stat.st_mtime + 3600))
    assert fingerprint(source) == original, "a touch must not orphan the cache"

    source.write_bytes(b"\x89PNG-changed-letter-bytes" * 100)
    assert fingerprint(source) != original, "an edit MUST orphan the cache"


def test_source_prefix_is_stamp_underscore_fingerprint(tmp_path):
    """The one naming function every cache-path builder and the GC
    share: 16-hex path stamp, underscore, 12-hex content fingerprint —
    and the documented graceful-absent `_0` for a missing source."""
    source = tmp_path / "plate.png"
    source.write_bytes(b"subdial-master")
    prefix = source_prefix(source)
    stamp, digest = prefix.split("_")
    assert len(stamp) == 16 and int(stamp, 16) >= 0
    assert len(digest) == 12 and int(digest, 16) >= 0
    assert source_prefix(tmp_path / "missing.png").endswith("_0")
