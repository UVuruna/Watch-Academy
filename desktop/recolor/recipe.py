"""The tunables — every number the transformer uses, loaded from
`presets/metals.json`. NOTHING in this package hardcodes a threshold,
ramp or gain (Rule #4); the JSON is the single source of truth and is
DATA, so a new metal costs one entry and zero lines of code. See
[Recipe](recipe.md).

THE ONE-FORMULA LAW (owner decision 2026-07-27): the same `Tuning` block
must serve every image — the transformer runs on the spot, the user
never fine-tunes. `Recipe.overrides` exists as the documented BACKUP the
owner allowed IF a single parameter set ever proves impossible for some
plate; it is deliberately empty, and any entry added to it is an
admission that the shared formula failed for that file and must say so.
"""

import json
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

PRESETS = Path(__file__).parent / "presets" / "metals.json"


@dataclass(frozen=True)
class Specular:
    """The highlight roll-off — where the near-white specular starts on
    the mapped lightness, and how far toward white it goes. Real metal
    reads as metal because its hottest pixels DESATURATE; the retired
    kernel's flat `S=1.0` made that impossible, which is the whole of
    the "garish" verdict."""
    start: float
    strength: float


@dataclass(frozen=True)
class Metal:
    """One metal, described ONCE — the same entry serves both roles: as a
    SOURCE it supplies the body color the mask centers on and the de-tint
    divides out, as a TARGET it supplies the ramp and the tonal
    character. That is what makes the transform source-agnostic (ring
    letters go gold -> bronze/silver, badges go bronze -> gold/silver,
    one code path)."""
    name: str
    stops: tuple[tuple[float, str], ...]
    gamma: float
    contrast: float
    detail_gain: float
    specular: Specular


@dataclass(frozen=True)
class Tuning:
    """The shared algorithm parameters — identical for every image."""

    # MASK: how far in Oklab hue from the source metal's body color a
    # pixel may sit and still count as that metal, and the saturation
    # (Oklab chroma OVER lightness, so it survives the shadows) below
    # which a pixel is gray stone rather than metal.
    hue_half_width_deg: float
    hue_soft_deg: float
    saturation_ramp: tuple[float, float]
    # Where along a metal's ramp its BODY color is sampled — the mask
    # center and the de-tint reference both come from this one point.
    body_position: float

    # DE-TINT: how completely the source metal's own cast is divided out
    # (1.0 = fully neutral relief).
    detint_strength: float

    # SPLIT: the guided filter's window as a fraction of the smaller
    # image side (so a 256px letter and a 2048px medallion separate the
    # same physical scale of detail), and the variance below which local
    # structure counts as texture rather than as an edge.
    detail_radius_fraction: float
    detail_radius_min: int
    detail_epsilon: float
    # How close to pure black/white the mapped form may come before the
    # detail riding on it is eased down (it would only be clipped there).
    detail_headroom: float

    # ANCHOR: the robust percentiles of the MASKED region that map to 0
    # and 1, and the bound on the resulting stretch factor (a
    # low-contrast source must not be stretched into a poster).
    anchor_percentiles: tuple[float, float]
    anchor_scale_range: tuple[float, float]

    # CHROMA DETAIL: how much of the residual chroma texture left after
    # de-tinting (ink on paper, patina) is re-injected as lightness so it
    # survives into an achromatic target like silver.
    chroma_detail_gain: float


@dataclass(frozen=True)
class Recipe:
    tuning: Tuning
    metals: dict[str, Metal]
    overrides: dict[str, dict]

    def metal(self, name: str) -> Metal:
        try:
            return self.metals[name]
        except KeyError:
            known = ", ".join(sorted(self.metals))
            raise KeyError(f"unknown metal {name!r}; known: {known}") from None

    def for_image(self, stem: str | None) -> "Recipe":
        """This recipe with any per-image BACKUP override applied. Absent
        an entry — the normal case, and the goal — returns self."""
        patch = self.overrides.get(stem or "")
        if not patch:
            return self
        return replace(self, tuning=replace(self.tuning, **patch))


def _metal(name: str, raw: dict) -> Metal:
    return Metal(
        name=name,
        stops=tuple((float(pos), str(color)) for pos, color in raw["stops"]),
        gamma=float(raw["gamma"]),
        contrast=float(raw["contrast"]),
        detail_gain=float(raw["detail_gain"]),
        specular=Specular(
            start=float(raw["specular"]["start"]),
            strength=float(raw["specular"]["strength"]),
        ),
    )


@lru_cache(maxsize=4)
def load(path: Path = PRESETS) -> Recipe:
    """Read `presets/metals.json`. A malformed preset raises — a silent
    fallback to built-in numbers would hide exactly the kind of typo
    that makes every plate look subtly wrong (Rule #1).

    Cached: the render path resolves a recolor per (file, metal, shade)
    and re-parsing the presets for each would be pure waste. Everything
    the recipe holds is frozen, so the shared instance cannot be
    mutated by a caller. A process reads the file once."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    tuning = raw["tuning"]
    return Recipe(
        tuning=Tuning(
            hue_half_width_deg=float(tuning["hue_half_width_deg"]),
            hue_soft_deg=float(tuning["hue_soft_deg"]),
            saturation_ramp=tuple(float(v) for v in tuning["saturation_ramp"]),
            body_position=float(tuning["body_position"]),
            detint_strength=float(tuning["detint_strength"]),
            detail_radius_fraction=float(tuning["detail_radius_fraction"]),
            detail_radius_min=int(tuning["detail_radius_min"]),
            detail_epsilon=float(tuning["detail_epsilon"]),
            detail_headroom=float(tuning["detail_headroom"]),
            anchor_percentiles=tuple(
                float(v) for v in tuning["anchor_percentiles"]
            ),
            anchor_scale_range=tuple(
                float(v) for v in tuning["anchor_scale_range"]
            ),
            chroma_detail_gain=float(tuning["chroma_detail_gain"]),
        ),
        metals={
            name: _metal(name, entry)
            for name, entry in raw["metals"].items()
        },
        overrides=raw.get("overrides", {}),
    )
