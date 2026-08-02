"""The orchestrator — the ONE public entry that runs the whole pipeline.
numpy in, numpy out; no Qt, no file I/O, no wall clock. See
[Transform](transform.md).

    rgba (sRGB, float 0..1)
      -> decode to linear light
      -> mask.metal_weight        which pixels are the source metal
      -> tone.relief              neutral relief -> mapped lightness
      -> ramp.sample              the target metal's color at that
                                  lightness, interpolated in Oklab
      -> ramp.add_specular        highlights roll off toward white
      -> composite under the mask, encode back to sRGB
    rgba (sRGB, float 0..1), alpha untouched
"""

import numpy as np

from recolor import mask, ramp, space, tone
from recolor.recipe import Recipe


def recolor(
    rgba: np.ndarray,
    source: str,
    target: str,
    recipe: Recipe,
    mask_mode: str = "chroma",
    image_key: str | None = None,
) -> np.ndarray:
    """`rgba` (H, W, 4) float in [0,1], sRGB-encoded, from a plate drawn
    in the `source` metal, rendered as the `target` metal.

    `mask_mode` is `"chroma"` for art that mixes metal with neutral stone
    (badge medallions) and `"alpha"` for art where every opaque pixel is
    metal (ring letters and numerals). `image_key` is the source file's
    stem, consulted ONLY for the per-image backup overrides that the
    shared formula is supposed to make unnecessary.
    """
    recipe = recipe.for_image(image_key)
    source_metal = recipe.metal(source)
    target_metal = recipe.metal(target)
    tuning = recipe.tuning

    # FLOAT32 pipeline (0.14.705): the filter passes are bandwidth-bound
    # and every color matrix in `space` is float32 — one entry cast keeps
    # the whole image in single precision end to end. Verified against
    # the float64 pipeline: max |delta| far under half an 8-bit quantum.
    rgba = np.asarray(rgba, dtype=np.float32)
    linear = space.srgb_to_linear(rgba[..., :3])
    alpha = rgba[..., 3]

    weight = mask.metal_weight(
        linear,
        alpha,
        ramp.body_color(source_metal, tuning.body_position),
        tuning,
        mask_mode,
    )
    lightness = tone.relief(
        linear, weight, tuning,
        target_metal.gamma, target_metal.contrast, target_metal.detail_gain,
    )
    painted = ramp.add_specular(
        ramp.sample(target_metal, lightness),
        lightness,
        target_metal.specular,
    )

    blended = linear * (1.0 - weight[..., None]) + painted * weight[..., None]
    out = np.empty_like(rgba)
    out[..., :3] = space.linear_to_srgb(blended)
    out[..., 3] = alpha
    return out
