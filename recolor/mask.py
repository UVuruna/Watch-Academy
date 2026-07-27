"""Which pixels are metal — step 1 of the pipeline. See [Mask](mask.md).

Two modes, because the two callers genuinely differ and NOTHING else
about them does (Rule #5 — the retired code had two near-copies of the
whole recolor for exactly this one difference):

- `"chroma"` — badge medallions, whose art mixes warm metal relief with
  GRAY stone and engravings. A soft hue window around the SOURCE metal's
  own body hue, times a saturation ramp that leaves the neutral stone
  alone. (Owner insight 2026-07-12; the window idea survives the rewrite
  untouched, only its color space changed.)
- `"alpha"` — ring letters and numerals, where every opaque pixel simply
  IS metal: a glyph mixes no stone, so there is nothing to detect.

WHY OKLAB AND WHY A RATIO: HSV hue is computed from `max-min` over a
tiny denominator, so in the deep shadows of a relief it is numeric
noise, and a mask built on it drops exactly the dark metal it should
keep. Oklab's hue angle stays meaningful down to near-black. Saturation
is taken as chroma OVER lightness rather than chroma alone, because
Oklab chroma scales with lightness — an absolute chroma threshold would
again cut the shadows off.
"""

import numpy as np

from recolor import space
from recolor.recipe import Tuning

# Below this lightness the hue angle carries no usable information at
# any precision, so a pixel simply cannot be claimed as metal.
_BLACK_FLOOR = 1e-4


def metal_weight(
    linear_rgb: np.ndarray,
    alpha: np.ndarray,
    body_linear: np.ndarray,
    tuning: Tuning,
    mode: str,
) -> np.ndarray:
    """A per-pixel weight in [0,1]: how much this pixel is the source
    metal. Transparent pixels are always 0."""
    opaque = (alpha > 0.0).astype(np.float64)
    if mode == "alpha":
        return opaque
    if mode != "chroma":
        raise ValueError(f"unknown mask mode {mode!r} (want 'alpha'/'chroma')")

    lab = space.linear_to_oklab(linear_rgb)
    lightness = lab[..., 0]
    chroma, hue = space.oklab_chroma_hue(lab)
    saturation = chroma / np.maximum(lightness, _BLACK_FLOOR)

    body_hue = space.oklab_chroma_hue(
        space.linear_to_oklab(body_linear)
    )[1]
    distance = space.hue_distance(hue, float(body_hue))

    soft = max(tuning.hue_soft_deg, 1e-6)
    hue_weight = 1.0 - space.smoothstep(
        (distance - tuning.hue_half_width_deg) / soft
    )
    sat_low, sat_high = tuning.saturation_ramp
    sat_weight = space.smoothstep(
        (saturation - sat_low) / max(sat_high - sat_low, 1e-6)
    )
    return hue_weight * sat_weight * opaque
