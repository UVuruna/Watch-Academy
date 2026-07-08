"""Typed skin definition — the six overridable units plus the noon marker.

Pure dataclasses, importable from config (which builds DEFAULT_SKIN) and
from render (which consumes a resolved skin). Asset fields hold absolute
paths at runtime; a None asset means "draw procedurally". Hand pivots are
MANDATORY fractions of the image size — the measured default hands prove
pivots are non-uniform (0.68 vs 0.92 of height, the hour hand has a
counterweight tail below the hub).
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class BackgroundSpec:
    """Base brightness wheel + transparent hue wedges; BOTH rotate with
    the star and the wedges are drawn only over the sunlit part of the
    day. base_asset None (the product default) draws the 30-section gray
    wheel procedurally — single lightest/darkest sections centered on
    noon/midnight, shades from the gray-contrast setting."""

    base_asset: Path | None            # custom wheel art; None -> procedural gray wheel
    sector_palette: tuple[str, ...]    # period hues, clockwise from the top-arm wedge
    day_alpha: float                   # hue opacity over the sunrise->sunset arc
    twilight_alpha: float              # hue opacity over the dawn/dusk bands
    base_radius_fraction: float        # GRAY wheel radius, of the dial radius
    radius_fraction: float             # COLORED wedges radius — tune independently


@dataclass(frozen=True)
class HexagramSpec:
    """Procedural six-diamond star (owner decision: simple geometry is
    drawn at runtime, not shipped as an image). Diamond FILLS appear only
    where the sun is up; the colored BORDERS run the full circle so the
    night diamonds stay recognizable (owner spec: purple hinted at the
    bottom even in the dark)."""

    colors: tuple[str, ...]            # 6 diamond colors, clockwise from top
    day_alpha: float                   # fill opacity over the sunlit arc
    twilight_alpha: float
    border_alpha: float                # full-circle colored outline opacity
    border_width_fraction: float       # of the dial radius
    radius_fraction: float             # tip radius as fraction of the dial radius


@dataclass(frozen=True)
class NoonMarkerSpec:
    asset: Path | None                 # None -> procedural triangle
    color: str
    scale: float                       # of the dial diameter


@dataclass(frozen=True)
class RingSpec:
    asset: Path | None                 # full dial-ring image; None -> procedural
    fill: str
    text_color: str
    letter_color: str
    width_fraction: float              # ring thickness as fraction of the dial radius
    letters: dict[int, str] = field(default_factory=dict)  # hour -> letter replacing the numeral


@dataclass(frozen=True)
class WeekdaySpec:
    bodies: dict[str, Path | None]     # body name -> image (None -> procedural disc)
    body_names: dict[str, str]         # display names for hover ("Mercury"; a
                                       # gods skin would say "Hades")
    body_colors: dict[str, str]        # procedural disc colors
    display_mode: str                  # "ghost" | "center_only"
    ghost_opacity: float
    center_scale: float                # of the dial diameter
    diamond_scale: float
    orbit_fraction: float              # slot distance from center, of the dial radius


@dataclass(frozen=True)
class YearMarkerSpec:
    """Date markers along the INSIDE of the dial: Earth rides the year
    wheel (solstice-calibrated); the Moon rides its own cycle — new moon
    at the top, full moon at the bottom, clockwise."""

    mode: str                          # "earth" | "moon" | "both"
    variants: dict[str, Path]          # "europe_day" / "europe_night" / ... -> image
    default_variant: str               # e.g. "europe"
    day_color: str                     # procedural Earth fallbacks
    night_color: str
    orbit_fraction: float              # Earth orbit, fraction of the dial radius
    scale: float                       # Earth size, fraction of the dial diameter
    moon_asset: Path | None            # full-moon disc image (terminator drawn over it)
    moon_lit_color: str                # procedural moon fallback
    moon_dark_color: str
    moon_shadow_alpha: float           # darkness of the unlit part over the image
    moon_orbit_fraction: float
    moon_scale: float                  # smaller than the Earth (owner: ~72%)


@dataclass(frozen=True)
class HandSpec:
    """Owner convention: every hand canvas is exactly as designed (a
    faint reference circle keeps the export from trimming it) and the
    rotation center sits HAND_HUB_OFFSET_UNITS above the canvas bottom."""

    asset: Path
    design_height: float               # canvas height in design units (viewBox)


@dataclass(frozen=True)
class HandsSpec:
    """All hands share ONE scale so their designed proportions are never
    deformed: the LONGEST hand's tip reaches `reach_fraction` of the dial
    radius and the others follow at their drawn ratios."""

    hour: HandSpec
    minute: HandSpec
    reach_fraction: float
    second: HandSpec | None = None     # optional; enabled via settings


@dataclass(frozen=True)
class SkinDefinition:
    name: str
    z_order: tuple[str, ...]           # layer names bottom-up
    background: BackgroundSpec
    hexagram: HexagramSpec
    noon_marker: NoonMarkerSpec
    ring: RingSpec
    weekday_set: WeekdaySpec
    year_marker: YearMarkerSpec
    hands: HandsSpec
    pointer: str = "hexa"              # "hexa" | "cross" | "octa" — arm count
                                       # AND period-hue count (owner spec)
    gray_contrast: str = "full"        # "full" | "soft" — gray wheel shade range


def missing_assets(skin: SkinDefinition) -> list[Path]:
    """Every referenced asset that does not exist on disk. The caller must
    surface a non-empty result visibly (a missing asset would otherwise
    fail inside paintEvent, where Qt swallows the exception and leaves a
    silently broken dial)."""
    referenced = [
        skin.background.base_asset,
        skin.ring.asset,
        skin.noon_marker.asset,
        skin.year_marker.moon_asset,
        skin.hands.hour.asset,
        skin.hands.minute.asset,
        skin.hands.second.asset if skin.hands.second else None,
        *skin.weekday_set.bodies.values(),
        *skin.year_marker.variants.values(),
    ]
    return [path for path in referenced if path is not None and not path.exists()]
