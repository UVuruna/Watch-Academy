"""Typed render configuration — the dial's six unit specs.

Pure dataclasses, importable from config (which builds DEFAULT_SKIN) and
from render (which consumes the built config). The controller overlays
the RING PRESET (DOMY/MORPH are ring preset names — nothing more) and
the user's display choices onto DEFAULT_SKIN at build time. Asset fields
hold absolute paths; a None asset means "draw procedurally".
"""

from dataclasses import dataclass, field
from pathlib import Path

from config import paths


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
    # The owner's GOLD letter art: hour -> the master file, ALWAYS gold
    # (built by the controller's build_skin). The ring tint never
    # touches it.
    letter_art: dict[int, Path] = field(default_factory=dict)
    # hour -> the active FINISH ("gold"/"silver"/"bronze", the preset's
    # accent letter wearing the opposite metal) — silver/bronze are
    # derived from the gold master AT LOAD (owner 2026-07-19,
    # `render.assets.letter_metal_file`; retired the ~15 MB of
    # pre-rendered `_silver.png`/`_bronze.png` files).
    letter_metal: dict[int, str] = field(default_factory=dict)
    # The per-letter HOVER LEGEND (ROADMAP 15b, owner "malo legende"):
    # hour -> {name, reading} for a preset that carries one (MASON G
    # today; empty {} for DOMY/MORPH/NUMBERS and any custom ring) — see
    # data.rings.validate_preset and render.compositor's ring-band hover.
    letter_legend: dict[int, dict] = field(default_factory=dict)
    # The outer GREAT SEAL MOTTO ARC (TASK 1, owner "može radi"
    # 2026-07-19, CANON.md §The Banknote; corrected MOTO-FIX round,
    # owner correction 2026-07-19, the dollar's Great Seal reference
    # image): built once by app.controller.build_skin from the preset's
    # own `motto` card field (data.rings.validate_preset ->
    # core.motto.motto_glyph_angles) — curved text just outside the
    # ring band, its pinned letters landing on the SAME six hexagram
    # seats the ring's own MASON-G letters occupy (MASON outside, G
    # inside). Each entry: {"text": the motto string (spaces included,
    # for reference), "glyphs": a tuple of (gold_asset_path, dial_angle)
    # pairs, ONE per non-space character, ready for render.layers.
    # RingLayer to draw — spaces are already filtered out here, so the
    # render loop never checks for them. Empty for every preset but
    # MASON G today; both entries now draw at the SAME
    # RING_MOTTO_RADIUS_FRACTION — the two arcs are angularly disjoint
    # (ANNUIT COEPTIS over the top, NOVUS ORDO SECLORUM under the
    # bottom) so they never collide; the old two-radius-by-list-order
    # scheme is gone.
    motto: tuple[dict, ...] = ()
    # The SINGLE finish every motto glyph wears (owner: "in the ring
    # letter metal/color family") — the same settings.ring_finish the
    # ring's own Trinity-triangle letters wear, resolved once in
    # build_skin. Unlike `letter_metal` this is NOT per-hour: the motto
    # is read as ONE continuous inscription, not a seat-by-seat split.
    motto_metal: str = "gold"


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
    # The bronze-plate themes (greek/norse/profession) can wear a METAL
    # (owner 2026-07-12): "gold"/"silver" run the hue-SELECTIVE swap at
    # render (only the warm bronze pixels change — the gray stone and
    # engravings stay); None = bronze, the art as drawn.
    metal: str | None = None
    # The SERVANT face of the theme's Sunday (owner dual-Sunday round
    # 2026-07-12) — resolved from WEEKDAY_DUAL_FILES with the metal in
    # apply_display_settings; drawn at 24h on the Compass/Seasons.
    dual_asset: Path | None = None
    # The PANTHEON roster (owner 2026-07-15) overrides these; None =
    # the constants tables (the planetary canon).
    article_set: str | None = None     # hover articles' set name
    body_articles: dict | None = None  # per-body (set, body) — seats
                                       # that FELL BACK to a planetary
                                       # figure keep its article
    dual_names: tuple | None = None    # the Sunday pair's hover names


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
    moon_hidden_alpha: float = 0.5     # marker opacity while the moon is
                                       # BELOW the horizon (owner spec
                                       # 2026-07-12; Settings slider)


@dataclass(frozen=True)
class HandSpec:
    """One hand image pointing UP with its rotation PIVOT (owner spec
    2026-07-12): x from the left (None = the image middle, the default
    for symmetric hands), y ABOVE the image bottom — both in the
    image's own units (pixels, or viewBox units for SVG)."""

    asset: Path
    natural_height: float              # full image height in its own units
    pivot_y: float                     # rotation center above the bottom
    pivot_x_fraction: float | None = None   # of the width; None = centered


@dataclass(frozen=True)
class HandsSpec:
    """A hand PACK resolved for the renderer. Sizing uses TIP-TO-PIVOT
    lengths only (owner spec): the seconds tip reaches
    `second_reach_fraction` of the dial radius (the ring), the minutes
    tip `minute_reach_fraction` (the minute arrows) and the hours
    follow the pack's own hours/minutes tip ratio. `z_order` draws
    bottom-up; `desaturate` grays colored user art so the clock tint
    can recolor it."""

    hour: HandSpec
    minute: HandSpec
    minute_reach_fraction: float
    second_reach_fraction: float
    second: HandSpec | None = None     # optional; enabled via settings
    z_order: tuple[str, ...] = ("hours", "minutes", "seconds")
    desaturate: bool = False


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
    palette_style: str = "paint"       # "paint" | "light" — Star+Aura hues;
                                       # on the Calendar pointer it PICKS THE
                                       # WHEEL: paint = Zodiac, light = Almanac
    calendar_lighting: str = "hour"    # "hour" (the shichen under the hand) |
                                       # "year" (the current month/sign wedge)
    calendar_mount: str = "zodiac"     # the DESIGN ZODIAC law's 12-SET MOUNT
                                       # (R9a, config.constants.CALENDAR_MOUNT_
                                       # MODES): "off" | "zodiac" | "months" —
                                       # twelve marks at CALENDAR_MOUNT_RADIUS_
                                       # FRACTION, independent of palette_style
    # THE ARCHETYPE MODE (owner sealed package 2026-07-16): the active
    # (pointer, palette_style) shows ITS archetype — the diamonds carry
    # the stained-glass figures, the hour hand lights the one whose
    # hour-space it is in, and the weekday model and ALL THREE SLOTS
    # switch OFF at the render level (render.layers.enabled_slots) —
    # the user's slot settings stay untouched, so toggling back
    # restores everything. Aurora/Calendar have no archetype: the mode
    # is inert there.
    archetype_mode: bool = False
    # Whether the archetype FIGURES carry their display name (owner
    # 2026-07-18, ROADMAP 15h, Session 21-C) — an INDEPENDENT switch,
    # its own Settings ▸ Display checkbox, no longer sharing
    # `show_weekday_names` with the weekday bodies. `ArchetypeLayer`
    # reads THIS key exclusively for the figures' names.
    archetype_names: bool = True
    # The Earth marker's label MODE (owner 2026-07-18, ROADMAP 15h — FOUR
    # exclusive Design ▸ Earth toggles, replacing the old show_earth_date/
    # earth_weekday bool pair, `constants.EARTH_LABEL_MODES`): "off",
    # "date" ("8 Jul"), "weekday" ("FRI"), "date_weekday" (date over the
    # abbreviated weekday) or "full" (date over the YEAR). A GENERAL
    # Earth option — works in BOTH normal and archetype mode.
    earth_label: str = "date"
    solar_rotation: bool = True        # False -> Star/Aura/Umbra stand upright
    octa_slot: str = "time"            # South slot MODE (OCTA_SLOT_MODES)
    day_slot_style: str = "sign"       # the DAY slot badge's own style
    info_slot_style: str = "sign"      # the INFO slot's own style
    info_slot_theme: str = "planets"   # the INFO slot's weekday theme
    info_slot_metal: str = "bronze"    # that theme's metal (bronze = as drawn,
                                       # "colored" = the colored/ art)
    info_slot_roster: str = "planetary"  # that theme's FIGURE roster —
                                       # per slot (owner 2026-07-15:
                                       # slot 1 Greek Planetary, slot 2
                                       # Greek Pantheon)
    weekday_slot: str = "weekday"      # weekday POSITION: bodies, or an
                                       # astrology badge (hexa/aurora only)
    # The THIRD slot (owner 2026-07-14: the 1st/2nd/3rd Slot system).
    third_slot: str = "date"
    third_slot_style: str = "sign"
    third_slot_theme: str = "planets"
    third_slot_metal: str = "bronze"
    third_slot_roster: str = "planetary"
    show_third_slot: bool = False
    earth_style: str = "clean"         # "clean" | "atmo" — Earth marker art
    weekday_theme: str = "planets"     # WEEKDAY_THEMES: bodies as planets,
                                       # Greek/Norse gods, religions, professions
    legend: bool = True                # False -> NO hovers at all (with
                                       # click-through: zero interaction)
    # THE YEAR LINE (Session 16, owner amendment 2026-07-17): the
    # official form's labels (BCE/CE vs BC/AD), the optional suffix on
    # positive years, and the optional third calendar — consumed by
    # core.deep_time.format_year_line/format_official, the ONE
    # formatting place (hovers pair the official year with Anno Lucis;
    # the compact dial texts stay official-only).
    era_notation: str = "bce_ce"
    show_era_suffix: bool = False
    third_era: str = "none"
    # Elements switches (owner spec, FINAL.txt #5) — each removes one
    # dial element; what always stays is the day/twilight indication:
    show_earth: bool = True            # the orbiting Earth date marker
    show_moon: bool = True             # the orbiting Moon phase marker
    show_weekday: bool = True          # the weekday bodies (slots + center)
    show_pointer: bool = True          # the star diamonds (Aura colors stay)
    colorful: bool = True              # False -> the Aura wears plain white
                                       # transparency instead of palette hues
    show_seconds: bool = True          # the seconds hand (and its cadence)
    show_octa_slot: bool = False       # canon 2026-07-14: ONE slot only
    show_weekday_names: bool = True    # the day-name text on the weekday
                                       # bodies (owner spec 2026-07-12:
                                       # its own switch under Theme ▸
                                       # Weekday, like the Earth date)
    show_info_slot_names: bool = True  # the SAME switch for the info
                                       # slot's second body (owner bug
                                       # 2026-07-13: the two slots must
                                       # toggle independently)
    # Ring recolor (owner spec, FINAL.txt #6): ONE hue multiplies the
    # ring art, the hands and the Umbra (None = untouched gray art);
    # the finish picks the owner's letter art set (gold = M/D/Y/P/H
    # gold + silver Omega; silver = the inverse) — letters never tint.
    ring_tint: str | None = None
    ring_finish: str = "gold"
    subdial_style: str = "black"       # complication plates (owner A/B
                                       # 2026-07-15): "theme" tints the
                                       # tapisserie field to the clock
                                       # tint, "black" keeps the
                                       # standard dark AP field
    # EXTRAS (owner spec): the octa info slot's size multiplier (the
    # Earth/Moon/Weekday multipliers scale their spec values directly
    # in apply_display_settings) and the shared hover-enlarge factor —
    # the element under the cursor draws this much larger.
    hover_enlarge: float = 1.2
    ring_letter_scale: float = 1.0     # multiplies RING_LETTER_ART_SCALE
    # Runtime-only (settings dialog): the user's custom hues for the
    # active (pointer, palette_style) — never serialized to skin.json.
    palette_override: tuple[str, ...] | None = None
    # SATURATION (owner 2026-07-18, Settings ▸ Colors, Session 21-D —
    # moved out of Display and split into two independent sliders):
    # field name kept as `pointer_saturation` (Rule #6 would normally
    # demand a rename, but this is a persisted settings key with zero
    # user-visible spelling — migrating it buys nothing) but RE-SCOPED
    # and RELABELED "Aura" (owner fix round E, 2026-07-19, slika 2): it
    # scales ONLY the Aura wedges' HSV saturation, via
    # `render.layers.aura_palette_for` — the star diamonds
    # (`render.layers.palette_for`, now RAW) no longer move with it.
    # 1.0 unchanged, 0.0 grays every Aura hue to its own brightness.
    pointer_saturation: float = 1.0
    # RING (new, Session 21-D): scales the RING BAND art's (the ring
    # plate + its letter/numeral overlay) HSV saturation in
    # `render.layers.RingLayer`, applied AFTER the ring_tint recolor —
    # 1.0 unchanged, 0.0 grays it to its own brightness. The Umbra and
    # hands do not read this (see layers.md's RingLayer note).
    ring_saturation: float = 1.0


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
        *(path for motto in skin.ring.motto for path, _ in motto["glyphs"]),
        *skin.weekday_set.bodies.values(),
        *skin.year_marker.variants.values(),
    ]
    # Canonical paths resolve through the active ART SOURCE first
    # (owner 2026-07-14: assets/<root>/<source>/... with fallback).
    return [
        path for path in referenced
        if path is not None and not paths.art_file(path).exists()
    ]
