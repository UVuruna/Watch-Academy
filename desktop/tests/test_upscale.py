"""THE ON-THE-SPOT UPSCALER's teeth (owner decree 2026-08-13).

The bargain this module exists to keep: every ordinary user carries a
512 px tree, and the one person who zooms past it still gets a good
picture. These tests hold both halves of that — that it declines when
there is nothing to do, and that when it does act, it acts correctly and
only once.
"""

import numpy as np
import pytest
from PySide6.QtGui import QImage

from render import upscale


def _image(width=64, height=64, colour=(200, 60, 40, 255)) -> QImage:
    image = QImage(width, height, QImage.Format.Format_RGBA8888)
    image.fill(0)
    for y in range(height):
        for x in range(width):
            image.setPixel(x, y, 0)
    array = np.zeros((height, width, 4), dtype=np.uint8)
    array[:, :] = colour
    array[:, width // 2:, :3] = 20        # a hard vertical edge to sharpen
    return QImage(
        array.tobytes(), width, height, width * 4,
        QImage.Format.Format_RGBA8888,
    ).copy()


# ═══════════════════════════ THE BLUR ═══════════════════════════
def test_a_flat_field_survives_the_blur_unchanged():
    """The summed-area off-by-one shows up exactly here: a constant
    field must stay constant, including on the very first row and
    column, or every blurred plate wears a one-pixel seam."""
    flat = np.full((16, 24), 137.0, dtype=np.float32)
    blurred = upscale._box_blur(flat, 2)
    assert np.allclose(blurred, 137.0, atol=1e-3)


def test_the_blur_actually_blurs():
    step = np.zeros((8, 8), dtype=np.float32)
    step[:, 4:] = 100.0
    blurred = upscale._box_blur(step, 1)
    # The column at the edge must land strictly between the two levels.
    assert 0.0 < blurred[4, 3] < 100.0
    assert 0.0 < blurred[4, 4] < 100.0


def test_a_zero_radius_blur_is_a_no_op():
    field = np.arange(36, dtype=np.float32).reshape(6, 6)
    assert np.array_equal(upscale._box_blur(field, 0), field)


# ═══════════════════════════ THE UPSCALE ═══════════════════════════
def test_it_declines_when_there_is_nothing_to_do():
    """This module upscales and nothing else. Handling downscales too
    would make it a second scaling policy beside the working set."""
    image = _image(64, 64)
    assert upscale.stepped_upscale(image, 64) is image
    assert upscale.stepped_upscale(image, 32) is image


def test_it_reaches_exactly_the_requested_height():
    image = _image(64, 64)
    for target in (65, 100, 128, 512, 1200):
        assert upscale.stepped_upscale(image, target).height() == target


def test_it_preserves_the_aspect_ratio():
    image = _image(80, 40)
    enlarged = upscale.stepped_upscale(image, 200)
    assert enlarged.height() == 200
    assert enlarged.width() == pytest.approx(400, abs=2)


def test_the_alpha_channel_is_never_sharpened():
    """An unsharp pass over alpha would ring the plate's own silhouette
    — a bright halo and a dark bite around every figure on the dial."""
    array = np.zeros((32, 32, 4), dtype=np.uint8)
    array[:, :, :3] = 180
    array[8:24, 8:24, 3] = 255           # an opaque square on transparency
    image = QImage(
        array.tobytes(), 32, 32, 32 * 4, QImage.Format.Format_RGBA8888
    ).copy()
    enlarged = upscale.stepped_upscale(image, 128)
    out = np.frombuffer(
        enlarged.constBits(), dtype=np.uint8,
        count=enlarged.height() * enlarged.width() * 4,
    ).reshape(enlarged.height(), enlarged.width(), 4)
    # Sharpening alpha would overshoot past the legal range and clip,
    # producing values that are neither 0 nor 255 at the FLAT interior.
    assert out[64, 64, 3] == 255, "the opaque interior stopped being opaque"
    assert out[2, 2, 3] == 0, "the transparent border gained alpha"


def test_sharpening_raises_edge_contrast_above_the_plain_scale():
    """The whole reason this module is not just Qt's own scale."""
    from PySide6.QtCore import Qt

    image = _image(64, 64)
    plain = image.scaledToHeight(
        256, Qt.TransformationMode.SmoothTransformation
    ).convertToFormat(QImage.Format.Format_RGBA8888)
    ours = upscale.stepped_upscale(image, 256).convertToFormat(
        QImage.Format.Format_RGBA8888
    )

    def edge_contrast(img):
        array = np.frombuffer(
            img.constBits(), dtype=np.uint8,
            count=img.height() * img.width() * 4,
        ).reshape(img.height(), img.width(), 4).astype(np.float32)
        row = array[img.height() // 2, :, 0]
        return float(np.abs(np.diff(row)).max())

    assert edge_contrast(ours) > edge_contrast(plain), (
        "the stepped+sharpened upscale is no crisper than a plain "
        "bilinear one — the module is buying nothing"
    )


# ═══════════════════════════ THE CACHE ═══════════════════════════
def test_the_result_is_cached_and_reused(tmp_path, monkeypatch):
    from config import paths

    monkeypatch.setattr(
        paths, "settings_path",
        lambda watch_index=1: tmp_path / "settings.json",
    )
    source = tmp_path / "small.png"
    _image(64, 64).save(str(source))

    first = upscale.upscaled_image(source, 256)
    assert first is not None and first.height() == 256
    cache = upscale.cache_path(source, 256)
    assert cache.exists(), "the upscale was not remembered"

    stamp = cache.stat().st_mtime_ns
    second = upscale.upscaled_image(source, 256)
    assert second is not None and second.height() == 256
    assert cache.stat().st_mtime_ns == stamp, "it was computed twice"


def test_a_corrupt_cache_entry_is_rebuilt_not_trusted(tmp_path, monkeypatch):
    from config import paths

    monkeypatch.setattr(
        paths, "settings_path",
        lambda watch_index=1: tmp_path / "settings.json",
    )
    source = tmp_path / "small.png"
    _image(64, 64).save(str(source))
    upscale.upscaled_image(source, 256)
    upscale.cache_path(source, 256).write_bytes(b"not an image")

    again = upscale.upscaled_image(source, 256)
    assert again is not None and again.height() == 256


def test_no_upscale_is_needed_returns_none(tmp_path, monkeypatch):
    from config import paths

    monkeypatch.setattr(
        paths, "settings_path",
        lambda watch_index=1: tmp_path / "settings.json",
    )
    source = tmp_path / "big.png"
    _image(512, 512).save(str(source))
    assert upscale.upscaled_image(source, 256) is None
    assert upscale.upscaled_image(source, 512) is None
