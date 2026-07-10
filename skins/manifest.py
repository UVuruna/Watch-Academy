"""Typed render configuration — the dial's six unit specs.

Pure dataclasses, importable from config (which builds DEFAULT_SKIN) and
from render (which consumes the built config). The controller overlays
the RING PRESET (DOMY/MORPH are ring preset names — nothing more) and
the user's display choices onto DEFAULT_SKIN at build time. Asset fields
hold absolute paths; a None asset means "draw procedurally".
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class BackgroundSpec:
    """The two background wheels: the UMBRA (gray brightness wheel) and
    the AURA (transparent period-hue wedges over the sunlit part of the
    day); both rotate with the star. base_asset None (the product
    default) draws the 30-section Umbra procedurally — single
    lightest/darkest sections centered on noon/midnight, shades from the
    umbra-contrast setting. Aura hues come from the active palette
    preset, shared with the star diamonds."""

    base_asset: Path | None            # custom Umbra art; None -> procedural
    day_alpha: float                   # Aura opacity over the sunrise->sunset arc
    twilight_alpha: float              # Aura opacity over the dawn/dusk bands
    umbra_radius_fraction: float       # Umbra radius, of the dial radius
    aura_radius_fraction: float        # Aura radius — tune independently


@dataclass(frozen=True)
class StarSpec:
    """Procedural N-diamond star (owner decision: simple geometry is
    drawn at runtime, not shipped as an image). Diamond FILLS appear only
    where the sun is up; the colored BORDERS run the full circle so the
    night diamonds stay recognizable (owner spec: purple hinted at the
    bottom even in the dark). Colors come from the active palette preset
    (config PALETTE_PRESETS), shared with the Aura wedges."""

    day_alpha: float                   # fill opacity over the sunlit arc
    twilight_alpha: float
    border_alpha: float                # full-circle colored outline opacity
    border_width_fraction: float       # of the dial radius
    radius_fraction: float             # tip radius as fraction of the dial radius


@dataclass(frozen=True)
class RingSpec:
    asset: Path | None                 # full dial-ring image; None -> procedural
    fill: str
    text_color: str
    letter_color: str
    width_fraction: float              # ring thickness as fraction of the dial radius
    letters: dict[int, str] = field(default_factory=dict)  # hour -> letter replacing the numeral
    # The owner's letter art overlaid on the ring: hour -> the resolved
    # file for the active finish — built by the controller's build_skin
    # (the preset's accent letter wears the opposite metal; silver files
    # are PRE-RENDERED by setup/make_silver_letters.py). The ring tint
    # never touches them.
    letter_art: dict[int, Path] = field(default_factory=dict)


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
    at the top, full moon at the bottom, clockwise. Which of the two is
    drawn comes from the Elements switches (show_earth / show_moon)."""

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
    z_order: tuple[str, ...]           # layer names bottom-up
    background: BackgroundSpec
    star: StarSpec
    ring: RingSpec
    weekday_set: WeekdaySpec
    year_marker: YearMarkerSpec
    hands: HandsSpec
    # User display choices (tray/settings override whatever the pack
    # declares — see the controller's _apply_display_settings):
    pointer: str = "hexa"              # "hexa" | "cross" | "octa" — arm count
                                       # AND period-hue count (owner spec)
    umbra_form: str = "fine"           # "fine" (30) | "coarse" (24) | "gradient"
    umbra_contrast: str = "full"       # "full" | "half" — Umbra shade span
    palette_style: str = "paint"       # "paint" | "light" — Star+Aura hues
    solar_rotation: bool = True        # False -> Star/Aura/Umbra stand upright
    octa_slot: str = "time"            # octa bottom arm, one of OCTA_SLOT_MODES
    earth_style: str = "clean"         # "clean" | "atmo" — Earth marker art
    weekday_theme: str = "planets"     # WEEKDAY_THEMES: bodies as planets,
                                       # Greek/Norse gods, religions, professions
    legend: bool = True                # False -> NO hovers at all (with
                                       # click-through: zero interaction)
    # Elements switches (owner spec, FINAL.txt #5) — each removes one
    # dial element; what always stays is the day/twilight indication:
    show_earth: bool = True            # the orbiting Earth date marker
    show_moon: bool = True             # the orbiting Moon phase marker
    show_weekday: bool = True          # the weekday bodies (slots + center)
    show_pointer: bool = True          # the star diamonds (Aura colors stay)
    colorful: bool = True              # False -> the Aura wears plain white
                                       # transparency instead of palette hues
    show_seconds: bool = True          # the seconds hand (and its cadence)
    show_octa_slot: bool = True        # the Compass info slot (octa only)
    # Ring recolor (owner spec, FINAL.txt #6): ONE hue multiplies the
    # ring art, the hands and the Umbra (None = untouched gray art);
    # the finish picks the owner's letter art set (gold = M/D/Y/P/H
    # gold + silver Omega; silver = the inverse) — letters never tint.
    ring_tint: str | None = None
    ring_finish: str = "gold"
    # EXTRAS (owner spec): the octa info slot's size multiplier (the
    # Earth/Moon/Weekday multipliers scale their spec values directly
    # in apply_display_settings) and the shared hover-enlarge factor —
    # the element under the cursor draws this much larger.
    octa_slot_scale: float = 1.0
    hover_enlarge: float = 1.2
    ring_letter_scale: float = 1.0     # multiplies RING_LETTER_ART_SCALE
    # Runtime-only (settings dialog): the user's custom hues for the
    # active (pointer, palette_style) — never serialized to skin.json.
    palette_override: tuple[str, ...] | None = None


def missing_assets(skin: SkinDefinition) -> list[Path]:
    """Every referenced asset that does not exist on disk. The caller must
    surface a non-empty result visibly (a missing asset would otherwise
    fail inside paintEvent, where Qt swallows the exception and leaves a
    silently broken dial)."""
    referenced = [
        skin.background.base_asset,
        skin.ring.asset,
        skin.year_marker.moon_asset,
        skin.hands.hour.asset,
        skin.hands.minute.asset,
        skin.hands.second.asset if skin.hands.second else None,
        *skin.ring.letter_art.values(),
        *skin.weekday_set.bodies.values(),
        *skin.year_marker.variants.values(),
    ]
    return [path for path in referenced if path is not None and not path.exists()]
