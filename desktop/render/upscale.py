"""THE ON-THE-SPOT UPSCALER — drawing an image larger than we ship it.
See [Upscale](__about/upscale.md).

Owner decree 2026-08-13, on lowering every working-set ceiling to 512:
an abnormally large display is a situation nobody will ever use, and if
somebody does insist on one, the upscaling should be done on the spot.
So the shipped tree stays small for everyone and this module pays for
the one person who zooms past it — once, on their machine, at the size
they actually asked for.

Qt's `SmoothTransformation` is bilinear: good going down, visibly soft
going up in one leap. Two cheap steps recover most of the difference —
step up in halvings so every pass interpolates between genuinely
adjacent pixels, then an unsharp mask to put the edge definition back.
Neither invents detail; both put the detail that exists where the eye
expects it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from config import paths
from render import raster_store


#: The largest single step the stepped upscale takes. 2.0 is the whole
#: point of the technique: a bilinear pass that never stretches beyond
#: double only ever mixes neighbouring pixels, which is what keeps the
#: result from turning into ramps.
MAX_STEP = 2.0

#: Unsharp mask strength. Deliberately conservative — upscaling spreads
#: edge energy over more pixels and this puts it back, but an aggressive
#: amount turns a soft picture into a crunchy one, which reads as worse
#: rather than sharper.
UNSHARP_AMOUNT = 0.55

#: Blur radius of the unsharp mask, in pixels of the FINAL image.
UNSHARP_RADIUS = 1

#: Bumped when the algorithm changes, so an old cached upscale simply
#: stops being the file anyone asks for — the same no-manifest trick
#: `asset_recolor.letter_cache_name` uses for the letter bake.
UPSCALE_VERSION = 1


def _box_blur(channel: np.ndarray, radius: int) -> np.ndarray:
    """A separable box blur via summed-area along each axis — O(n) per
    axis rather than O(radius), which is the difference between a
    millisecond and a visible stall on a large plate.

    Edges are handled by EDGE PADDING rather than by wrapping or by
    zero-fill: a zero-filled border would darken the outermost pixels
    and show up as a faint dark rim on every upscaled plate, which on
    art with a hard alpha edge is exactly where it would be noticed.
    """
    if radius < 1:
        return channel
    return _blur_axis(_blur_axis(channel, radius, 0), radius, 1)


def _blur_axis(channel: np.ndarray, radius: int, axis: int) -> np.ndarray:
    """One axis of the box blur, as a difference of prefix sums.

    The zero row prepended to the cumulative sum is what makes the
    window arithmetic exact at index 0 instead of off by one — the
    classic summed-area mistake, and one that shows as a one-pixel
    brightness seam along the top/left edge of every blurred plate.
    """
    window = 2 * radius + 1
    padding = [(0, 0), (0, 0)]
    padding[axis] = (radius, radius)
    padded = np.pad(channel, padding, mode="edge")
    cumulative = np.cumsum(padded, axis=axis, dtype=np.float32)
    zero_shape = list(cumulative.shape)
    zero_shape[axis] = 1
    cumulative = np.concatenate(
        [np.zeros(zero_shape, dtype=np.float32), cumulative], axis=axis
    )
    length = channel.shape[axis]
    high = np.take(cumulative, np.arange(window, window + length), axis=axis)
    low = np.take(cumulative, np.arange(0, length), axis=axis)
    return (high - low) / window


def _unsharp(image: QImage, amount: float, radius: int) -> QImage:
    """Sharpen `image` by subtracting a blurred copy of itself.

    Runs on the COLOUR channels only and leaves ALPHA untouched: an
    unsharp pass over the alpha would ring the plate's own silhouette,
    putting a bright halo and a dark bite around the outline of every
    figure on the dial. Colour is also premultiplied-safe here because
    the operation is per-channel and the alpha it would be premultiplied
    against never changes.
    """
    if amount <= 0 or radius < 1:
        return image
    image = image.convertToFormat(QImage.Format.Format_RGBA8888)
    width, height = image.width(), image.height()
    buffer = np.frombuffer(
        image.constBits(), dtype=np.uint8, count=height * width * 4
    ).reshape(height, width, 4).astype(np.float32)

    rgb = buffer[:, :, :3]
    blurred = np.stack(
        [_box_blur(_box_blur(rgb[:, :, c], radius), radius) for c in range(3)],
        axis=2,
    )
    sharpened = np.clip(rgb + amount * (rgb - blurred), 0.0, 255.0)

    out = np.empty_like(buffer, dtype=np.uint8)
    out[:, :, :3] = sharpened.astype(np.uint8)
    out[:, :, 3] = buffer[:, :, 3].astype(np.uint8)     # alpha untouched
    result = QImage(
        out.tobytes(), width, height, width * 4,
        QImage.Format.Format_RGBA8888,
    )
    return result.copy()       # own the buffer; `out` is about to die


def stepped_upscale(image: QImage, px_height: int) -> QImage:
    """`image` enlarged to `px_height`, in halving steps, then sharpened.

    Returns the image UNCHANGED when it is already at or above the
    target: this module upscales and nothing else. An "upscaler" that
    also handled downscales would quietly become a second scaling policy
    beside the working set, and the two would drift.
    """
    if image.isNull() or px_height <= image.height():
        return image
    current = image
    while current.height() * MAX_STEP < px_height:
        current = current.scaledToHeight(
            int(current.height() * MAX_STEP),
            Qt.TransformationMode.SmoothTransformation,
        )
    current = current.scaledToHeight(
        px_height, Qt.TransformationMode.SmoothTransformation
    )
    return _unsharp(current, UNSHARP_AMOUNT, UNSHARP_RADIUS)


def cache_path(source: Path, px_height: int) -> Path:
    """Where `source`'s upscale to `px_height` is remembered. Keyed by
    the source's CONTENT fingerprint, so re-drawn art simply stops
    matching, and by `UPSCALE_VERSION`, so a changed algorithm does
    too."""
    return (
        paths.settings_path().parent / "raster_cache"
        / f"{raster_store.source_prefix(source)}_up{px_height}"
        f"_v{UPSCALE_VERSION}.png"
    )


def upscaled_image(source: Path, px_height: int) -> QImage | None:
    """The disk-cached upscale of `source` to `px_height`.

    `None` when there is nothing to do (the source is already big
    enough) or when anything at all goes wrong — an unreadable source, a
    cache directory that cannot be written. The caller then keeps the
    plain Qt scale it would have used before this module existed: a
    documented fallback, never a silent one, and never a blank dial.
    """
    cache = cache_path(source, px_height)
    if cache.exists():
        cached = QImage(str(cache))
        if not cached.isNull():
            return cached
        # A truncated or unreadable cache file is worth exactly one
        # rebuild, not a permanent fallback to the soft path.
        try:
            cache.unlink()
        except OSError:
            pass

    original = QImage(str(source))
    if original.isNull() or px_height <= original.height():
        return None

    enlarged = stepped_upscale(original, px_height)
    try:
        raster_store.atomic_save(enlarged, cache)
    except OSError as error:
        # Slower next time, never wrong this time.
        print(f"upscale cache write failed: {error}", file=sys.stderr)
    return enlarged
