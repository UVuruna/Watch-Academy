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
    """Fixed base wheel + transparent hue wedges that ROTATE WITH the
    hexagram and are drawn only over the sunlit part of the day."""

    base_asset: Path | None            # fixed gray wheel; None -> flat disc
    base_color: str                    # procedural fallback disc color
    sector_palette: tuple[str, ...]    # 6 hues, clockwise from the hexagram-top wedge
    day_alpha: float                   # hue opacity over the sunrise->sunset arc
    twilight_alpha: float              # hue opacity over the dawn/dusk bands
    radius_fraction: float             # of the dial radius (inside the ring)


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
    moon_scale: float


@dataclass(frozen=True)
class HandSpec:
    asset: Path
    pivot: tuple[float, float]         # (x, y) fractions of the image size — MANDATORY
    length_fraction: float             # tip-to-pivot reach as fraction of the dial radius


@dataclass(frozen=True)
class HandsSpec:
    hour: HandSpec
    minute: HandSpec


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
        *skin.weekday_set.bodies.values(),
        *skin.year_marker.variants.values(),
    ]
    return [path for path in referenced if path is not None and not path.exists()]
