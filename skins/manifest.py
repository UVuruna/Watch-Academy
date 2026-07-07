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
    mode: str                          # "colors" | "light_dark"
    sector_palette: tuple[str, ...]    # 6 hex colors, clockwise from the noon-top sector
    day_base: str                      # base disc color for "light_dark" mode
    twilight_shade: float              # brightness kept in the dawn/dusk bands (0..1)
    night_shade: float                 # brightness kept in the night arc (0..1)
    radius_fraction: float             # of the dial radius (inside the ring)


@dataclass(frozen=True)
class HexagramSpec:
    asset: Path | None                 # None -> procedural star outline
    opacity: float
    radius_fraction: float             # tip radius as fraction of the dial radius


@dataclass(frozen=True)
class NoonMarkerSpec:
    asset: Path | None                 # None -> procedural triangle
    color: str
    scale: float                       # of the dial diameter


@dataclass(frozen=True)
class RingSpec:
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
    mode: str                          # "earth" | "moon_phase"
    variants: dict[str, Path]          # "europe_day" / "europe_night" / ... -> image
    default_variant: str               # e.g. "europe"
    moon_asset: Path | None            # full-moon disc (terminator drawn procedurally)
    day_color: str                     # procedural fallbacks
    night_color: str
    moon_lit_color: str
    moon_dark_color: str
    orbit_fraction: float
    scale: float


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
        skin.hexagram.asset,
        skin.noon_marker.asset,
        skin.year_marker.moon_asset,
        skin.hands.hour.asset,
        skin.hands.minute.asset,
        *skin.weekday_set.bodies.values(),
        *skin.year_marker.variants.values(),
    ]
    return [path for path in referenced if path is not None and not path.exists()]
