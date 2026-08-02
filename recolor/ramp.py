"""The gradient map — steps 8 and 9 of the pipeline: turn a mapped
lightness into the target metal's actual color, then roll the top of the
range toward white so the metal has a specular. See [Ramp](ramp.md).

THE LAW: a metal's chroma is HIGHEST in its body and FALLS toward both
ends — shadows go dark and slightly desaturated, highlights roll off to
near-white. The retired kernel used a flat `S=1.0` for gold at every
lightness, which made a white highlight impossible and is the entire
reason it read as a highlighter rather than as metal.

Interpolation happens in OKLAB, not in linear RGB and not in sRGB:
between two ramp stops Oklab moves in a straight perceptual line, so the
midtones never go muddy (linear RGB's failure) and the hue never drifts
(sRGB's failure).
"""

from functools import lru_cache

import numpy as np

from recolor import space
from recolor.recipe import Metal, Specular

# The specular target — linear white (float32, like every constant in
# `space` — one float64 operand would upcast the whole blend back).
_WHITE = np.ones(3, dtype=np.float32)


@lru_cache(maxsize=64)
def _stops_oklab(metal: Metal) -> tuple[np.ndarray, np.ndarray]:
    """A metal's stop positions and their Oklab colors, position-sorted.
    Cached per `Metal` (frozen, hashable): the same handful of ramps is
    re-sampled on every recolor call, and the hex→linear→Oklab hop for
    five stops is pure recomputation. Returned read-only — `sample`
    only reads them."""
    positions = np.array([position for position, _ in metal.stops])
    colors = np.array([space.hex_to_linear(color) for _, color in metal.stops])
    order = np.argsort(positions)
    sorted_positions = positions[order]
    lab_stops = space.linear_to_oklab(colors[order])
    sorted_positions.setflags(write=False)
    lab_stops.setflags(write=False)
    return sorted_positions, lab_stops


def body_color(metal: Metal, position: float) -> np.ndarray:
    """The metal's BODY color as linear RGB — its ramp sampled at
    `position`. This one point is both the hue the mask centers on when
    the metal is a SOURCE and the cast the de-tint divides out, so a
    metal is described exactly once (its ramp) and never twice."""
    return sample(metal, np.array(position)).reshape(3)


def sample(metal: Metal, lightness: np.ndarray) -> np.ndarray:
    """Map `lightness` in [0,1] through `metal`'s ramp -> linear RGB of
    the same leading shape. Piecewise-linear in Oklab; `np.interp` clamps
    outside the stop range, which is what we want at both ends."""
    positions, lab_stops = _stops_oklab(metal)
    lab = np.stack(
        [
            np.interp(lightness, positions, lab_stops[:, channel])
            for channel in range(3)
        ],
        axis=-1,
    )
    # np.interp always answers in float64 — fold back to the caller's
    # own precision so the float32 pipeline stays float32 downstream.
    lab = lab.astype(lightness.dtype, copy=False)
    return np.clip(space.oklab_to_linear(lab), 0.0, None)


def add_specular(
    linear_rgb: np.ndarray, lightness: np.ndarray, specular: Specular
) -> np.ndarray:
    """Roll the top of the lightness range toward white. `start` is where
    the roll-off begins and `strength` how far it goes; the smoothstep
    keeps it confined to the genuine highlights instead of washing the
    whole upper half."""
    if specular.strength <= 0.0:
        return linear_rgb
    span = max(1.0 - specular.start, 1e-6)
    weight = (
        space.smoothstep((lightness - specular.start) / span)
        * specular.strength
    )[..., None]
    return linear_rgb * (1.0 - weight) + _WHITE * weight
