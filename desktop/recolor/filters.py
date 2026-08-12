"""The edge-preserving split primitive — an O(1)-per-pixel box filter
built on cumulative sums, and the self-guided filter built on that. See
[Filters](filters.md).

WHY THIS EXISTS: separating a relief into FORM (low frequency) and
DETAIL (high frequency) is the single change that saves the engraving
lines, the drawings on the physician's book page and the hair strands
from any tonal remap — the curve is applied to the form alone and the
detail is added back untouched. A plain Gaussian would do the split too,
but it leaves a bright halo along every strong edge (exactly where a
medallion has its engraved lines), so the guided filter is the right
primitive rather than a luxury.

numpy only, deliberately — no scipy, no OpenCV. This package is the seed
of the Colorize SVG port and must carry nothing that would have to be
unwritten there.
"""

from functools import lru_cache

import numpy as np


def _box_sum(source: np.ndarray, radius: int) -> np.ndarray:
    """Sum over every (2r+1)x(2r+1) window, edges clamped, in O(1) per
    pixel via cumulative sums along each axis."""
    height, width = source.shape
    out = np.empty_like(source)

    cum = np.cumsum(source, axis=0)
    out[:radius + 1] = cum[radius:2 * radius + 1]
    out[radius + 1:height - radius] = (
        cum[2 * radius + 1:height] - cum[:height - 2 * radius - 1]
    )
    out[height - radius:] = (
        cum[height - 1:height] - cum[height - 2 * radius - 1:height - radius - 1]
    )

    cum = np.cumsum(out, axis=1)
    out[:, :radius + 1] = cum[:, radius:2 * radius + 1]
    out[:, radius + 1:width - radius] = (
        cum[:, 2 * radius + 1:width] - cum[:, :width - 2 * radius - 1]
    )
    out[:, width - radius:] = (
        cum[:, width - 1:width]
        - cum[:, width - 2 * radius - 1:width - radius - 1]
    )
    return out


@lru_cache(maxsize=8)
def _box_counts(shape: tuple[int, int], radius: int, dtype: str) -> np.ndarray:
    """The edge-normalization denominator — the box sum over ones. It
    depends ONLY on (shape, radius, dtype), which is identical across
    the four `box_mean` calls inside one `guided_split` AND across the
    two `guided_split` passes per recolor (lightness + chroma texture),
    so recomputing it every call paid the full two-cumsum cost eight
    times over (measured 2026-08-02: caching it cut `guided_split` from
    48.2 ms to 27.0 ms per 512x756 call, output bit-identical). The
    cache is small and bounded — a handful of full-plane arrays — and
    `lru_cache` is thread-safe for the parallel ledger drain. Returned
    read-only: every caller only divides by it."""
    counts = _box_sum(np.ones(shape, dtype=np.dtype(dtype)), radius)
    counts.setflags(write=False)
    return counts


def box_mean(source: np.ndarray, radius: int) -> np.ndarray:
    """Window MEAN with correct edge normalization (the denominator is
    the same box sum over ones, so border pixels average only the
    samples that actually exist)."""
    counts = _box_counts(source.shape, radius, source.dtype.str)
    return _box_sum(source, radius) / counts


def clamp_radius(shape: tuple[int, int], radius: int) -> int:
    """The largest usable radius for `shape` — `_box_sum`'s slicing needs
    at least 2r+2 rows and columns. Returns 0 when the image is too small
    for ANY window (a 2x1 color probe, a 1px icon): such an image has no
    frequencies to separate, and 0 tells `guided_split` to say so rather
    than to slice past the end of an array."""
    limit = (min(shape) - 2) // 2
    return max(0, min(radius, limit))


def guided_split(
    channel: np.ndarray, radius: int, epsilon: float
) -> tuple[np.ndarray, np.ndarray]:
    """Split `channel` into (base, detail) with a SELF-guided filter.

    Self-guided (guide == input) collapses the general guided filter to
    a compact form: within each window the filter is the linear model
    `q = a*I + b` whose `a = var / (var + eps)` — flat regions (var much
    smaller than eps) get a -> 0 and are smoothed to their local mean,
    while regions straddling an edge (var much larger than eps) get
    a -> 1 and pass through unchanged. That is precisely "blur the form,
    keep the edges", and `epsilon` is the variance below which structure
    counts as texture rather than as an edge.

    Returns `(base, channel - base)`; adding them back is exact.

    An image too small to hold a single window (a 2x1 color probe, a 1px
    icon) has no frequencies to separate: it is ALL form, and the detail
    layer is zero. That is the honest answer, not a special case — the
    caller's arithmetic downstream is identical either way.
    """
    radius = clamp_radius(channel.shape, radius)
    if radius == 0:
        return channel, np.zeros_like(channel)
    mean = box_mean(channel, radius)
    mean_square = box_mean(channel * channel, radius)
    variance = np.maximum(mean_square - mean * mean, 0.0)
    slope = variance / (variance + epsilon)
    offset = mean * (1.0 - slope)
    base = box_mean(slope, radius) * channel + box_mean(offset, radius)
    return base, channel - base
