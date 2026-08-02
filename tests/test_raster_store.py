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

import pytest
from PySide6.QtGui import QColor, QImage

from render.raster_store import atomic_save


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
