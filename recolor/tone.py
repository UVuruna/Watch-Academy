"""The relief map — steps 2 to 7: strip the source metal's own cast,
measure a perceptual lightness, separate form from detail, anchor the
form to a known window, shape it, and put the detail back. See
[Tone](tone.md).

Everything a metal change must NOT destroy lives here. No color is
chosen in this module at all — its output is a single lightness channel
in [0,1] that `ramp.py` then paints.
"""

import numpy as np

from recolor import filters, space
from recolor.recipe import Tuning

# Weight above which a pixel counts as metal when measuring the source's
# own cast and percentiles — a soft mask edge must not drag the
# statistics toward the background.
_STAT_FLOOR = 0.5


def detint(
    linear_rgb: np.ndarray, weight: np.ndarray, strength: float
) -> np.ndarray:
    """Divide out the SOURCE metal's own chromaticity, measured from its
    own masked pixels — the step that makes the transform work from ANY
    metal to any other (gold masters -> bronze/silver for ring letters,
    bronze masters -> gold/silver for badges) through one code path.

    The reference is normalized to unit luminance before dividing, so
    the operation removes the CAST and leaves overall brightness alone.
    What survives is an honest neutral relief built from all THREE
    channels — the retired kernel instead took `max(R,G,B)`, which for
    warm bronze art is the RED channel alone (measured: mean R 0.3721 vs
    mean V 0.3740 on the owner's plate), discarding two thirds of the
    information before any recolor even began.
    """
    total = weight.sum()
    if total <= 0.0:
        return linear_rgb
    reference = (linear_rgb * weight[..., None]).sum(axis=(0, 1)) / total
    cast = reference / max(space.luminance(reference), 1e-6)
    neutral = linear_rgb / np.maximum(cast, 1e-4)
    return linear_rgb * (1.0 - strength) + neutral * strength


def anchor(
    base: np.ndarray, weight: np.ndarray, tuning: Tuning
) -> tuple[np.ndarray, float]:
    """Rescale `base` so the masked region's robust percentiles land at
    0 and 1. Returns `(anchored, scale)`.

    THIS IS NOT THE REVERTED PERCENTILE REMAP (`013b5ca`, reverted the
    same day the owner saw it): that one replaced each pixel's value by
    its RANK in the histogram, a non-uniform remap that flattened every
    relief into a detail-free wash. This is a single multiply and a
    single offset shared by every pixel — strictly monotone, and it
    preserves every light/dark relationship in the source exactly, the
    way the straight multiply it replaces did. What it fixes is that the
    multiply was chosen from a MEAN chasing a fixed reference value,
    which on dark medallion art hit the 1.90 ceiling and clipped ~12% of
    the plate to one flat maximum.

    The stretch is bounded by `anchor_scale_range` so a low-contrast
    source is never blown into a poster, and it pivots on the window's
    MIDPOINT so a clamped stretch stays centered instead of sliding the
    whole plate dark or bright.
    """
    values = base[weight > _STAT_FLOOR]
    if values.size == 0:
        return np.clip(base, 0.0, 1.0), 1.0
    low, high = np.percentile(values, tuning.anchor_percentiles)
    scale_low, scale_high = tuning.anchor_scale_range
    scale = float(np.clip(1.0 / max(high - low, 1e-6), scale_low, scale_high))
    midpoint = (low + high) / 2.0
    return np.clip(0.5 + (base - midpoint) * scale, 0.0, 1.0), scale


def shape(lightness: np.ndarray, gamma: float, contrast: float) -> np.ndarray:
    """The per-metal tonal character: a gamma, then a monotone S-curve.

    The S-curve is `t + contrast*(smoothstep(t) - t)` — it fixes 0 and 1
    exactly and stays monotone for contrast in [-2, 1], so it can add
    punch (silver, steel, gunmetal need far more than gold) without ever
    inverting a light/dark relationship.
    """
    curved = np.clip(lightness, 0.0, 1.0) ** gamma
    return curved + contrast * (space.smoothstep(curved) - curved)


def relief(
    linear_rgb: np.ndarray, weight: np.ndarray, tuning: Tuning,
    gamma: float, contrast: float, detail_gain: float,
) -> np.ndarray:
    """The whole tonal half of the pipeline: neutral relief -> perceptual
    lightness -> form/detail split -> anchor -> curve -> detail back.

    Returns the mapped lightness in [0,1] that `ramp.sample` paints.
    """
    neutral = detint(linear_rgb, weight, tuning.detint_strength)
    lab = space.linear_to_oklab(neutral)
    lightness = lab[..., 0]

    radius = max(
        tuning.detail_radius_min,
        int(round(min(lightness.shape) * tuning.detail_radius_fraction)),
    )
    base, detail = filters.guided_split(
        lightness, radius, tuning.detail_epsilon
    )
    anchored, scale = anchor(base, weight, tuning)
    curved = shape(anchored, gamma, contrast)

    # Detail rides on top of the curve at the SAME scale the form was
    # stretched by, so its relative strength is preserved. Near the two
    # ends a share of it would only be clipped away, so it is eased down
    # there instead of being thrown at a wall.
    headroom = tuning.detail_headroom
    ease = 0.25 + 0.75 * np.clip(
        np.minimum(curved, 1.0 - curved) / max(headroom, 1e-6), 0.0, 1.0
    )
    result = curved + detail * scale * detail_gain * ease

    if tuning.chroma_detail_gain > 0.0:
        result = result - tuning.chroma_detail_gain * _chroma_texture(
            neutral, lab, radius, tuning
        )
    return np.clip(result, 0.0, 1.0)


def _chroma_texture(
    neutral: np.ndarray, lab: np.ndarray, radius: int, tuning: Tuning
) -> np.ndarray:
    """The high-frequency part of what chroma SURVIVED the de-tint —
    ink on a page, patina, painted marks. On a neutral target such as
    silver these would otherwise vanish entirely, since the target has
    no chroma to carry them; re-injected as a small DARKENING they keep
    reading as marks on the metal.

    Signed and high-pass, so a large evenly-colored area is untouched —
    only local chromatic contrast against its own surroundings counts.
    """
    chroma = space.oklab_chroma_hue(lab)[0]
    saturation = chroma / np.maximum(lab[..., 0], 1e-4)
    return filters.guided_split(saturation, radius, tuning.detail_epsilon)[1]
