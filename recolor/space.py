"""Color space math for the metal transformer — sRGB <-> linear light,
linear RGB <-> Oklab, and hex parsing. Pure numpy, fully vectorized (no
per-pixel Python anywhere in this package). See [Color Space Math]
(space.md).

WHY LINEAR AND WHY OKLAB: the retired kernel did all its mixing on
gamma-encoded sRGB values, which is why its midtones behaved
unpredictably and its one global gain clipped so much. Physical mixing
(blending, gain, gradient interpolation) belongs in LINEAR light; the
perceptual decisions (what "the same lightness" means, how a ramp
should interpolate) belong in OKLAB, whose L is uniform and whose a/b
plane gives a hue angle that stays meaningful in deep shadow — exactly
where HSV hue turns to noise.
"""

import numpy as np

# sRGB transfer function constants (IEC 61966-2-1).
_SRGB_LINEAR_CUT = 0.04045
_SRGB_ENCODED_CUT = 0.0031308
_SRGB_SLOPE = 12.92
_SRGB_ALPHA = 0.055
_SRGB_GAMMA = 2.4

# Rec.709 / sRGB linear luminance weights.
#
# FLOAT32 CONSTANTS (0.14.705): the pipeline runs in float32 — the
# filter passes are memory-bandwidth-bound, so halving the traffic is a
# measured win — and numpy's promotion rules mean ONE float64 constant
# in a matmul silently upcasts the whole downstream image back to
# float64, so the matrices must carry the dtype themselves. float32's
# 24-bit mantissa is ~7 decimal digits against an 8-bit output
# quantum of 1/255 — verified: max |delta| vs the float64 pipeline is
# far below half a quantum on real letter art.
LUMA_WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

# Oklab forward: linear sRGB -> LMS, then cube root, then LMS' -> Lab.
_LMS_FROM_RGB = np.array([
    [0.4122214708, 0.5363325363, 0.0514459929],
    [0.2119034982, 0.6806995451, 0.1073969566],
    [0.0883024619, 0.2817188376, 0.6299787005],
], dtype=np.float32)
_LAB_FROM_LMS = np.array([
    [0.2104542553, 0.7936177850, -0.0040720468],
    [1.9779984951, -2.4285922050, 0.4505937099],
    [0.0259040371, 0.7827717662, -0.8086757660],
], dtype=np.float32)
_LMS_FROM_LAB = np.array([
    [1.0, 0.3963377774, 0.2158037573],
    [1.0, -0.1055613458, -0.0638541728],
    [1.0, -0.0894841775, -1.2914855480],
], dtype=np.float32)
_RGB_FROM_LMS = np.array([
    [4.0767416621, -3.3077115913, 0.2309699292],
    [-1.2684380046, 2.6097574011, -0.3413193965],
    [-0.0041960863, -0.7034186147, 1.7076147010],
], dtype=np.float32)


def srgb_to_linear(srgb: np.ndarray) -> np.ndarray:
    """Gamma-encoded sRGB in [0,1] -> linear light."""
    srgb = np.clip(srgb, 0.0, 1.0)
    return np.where(
        srgb <= _SRGB_LINEAR_CUT,
        srgb / _SRGB_SLOPE,
        ((srgb + _SRGB_ALPHA) / (1.0 + _SRGB_ALPHA)) ** _SRGB_GAMMA,
    )


def linear_to_srgb(linear: np.ndarray) -> np.ndarray:
    """Linear light -> gamma-encoded sRGB in [0,1]."""
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(
        linear <= _SRGB_ENCODED_CUT,
        linear * _SRGB_SLOPE,
        (1.0 + _SRGB_ALPHA) * linear ** (1.0 / _SRGB_GAMMA) - _SRGB_ALPHA,
    )


def luminance(linear_rgb: np.ndarray) -> np.ndarray:
    """Linear relative luminance Y of a (..., 3) linear RGB array."""
    return linear_rgb @ LUMA_WEIGHTS


def linear_to_oklab(linear_rgb: np.ndarray) -> np.ndarray:
    """(..., 3) linear RGB -> (..., 3) Oklab (L, a, b).

    Negative LMS cannot occur for in-gamut non-negative input, but the
    de-tint step can push a channel slightly negative; clamping at zero
    before the cube root keeps that a graceful clip rather than a NaN
    (Rule #1: a documented, explicit bound, not a hidden fallback).
    """
    lms = np.clip(linear_rgb @ _LMS_FROM_RGB.T, 0.0, None)
    return np.cbrt(lms) @ _LAB_FROM_LMS.T


def oklab_to_linear(lab: np.ndarray) -> np.ndarray:
    """(..., 3) Oklab -> (..., 3) linear RGB (may be out of gamut)."""
    lms = (lab @ _LMS_FROM_LAB.T) ** 3
    return lms @ _RGB_FROM_LMS.T


def oklab_chroma_hue(lab: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Chroma (>= 0) and hue in DEGREES [0, 360) from an Oklab array."""
    a, b = lab[..., 1], lab[..., 2]
    chroma = np.hypot(a, b)
    hue = np.degrees(np.arctan2(b, a)) % 360.0
    return chroma, hue


def hue_distance(hue: np.ndarray, center: float) -> np.ndarray:
    """Shortest angular distance in degrees [0, 180] to `center`."""
    delta = np.abs((hue - center + 180.0) % 360.0 - 180.0)
    return delta


def hex_to_linear(value: str) -> np.ndarray:
    """`"#RRGGBB"` -> a (3,) linear-light array."""
    text = value.lstrip("#")
    if len(text) != 6:
        raise ValueError(f"expected a #RRGGBB color, got {value!r}")
    srgb = np.array([int(text[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0
    return srgb_to_linear(srgb)


def smoothstep(x: np.ndarray) -> np.ndarray:
    """The classic Hermite ramp, clamped to [0,1] outside the edges."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)
