"""Typed render configuration — the dial's six unit specs.

Pure dataclasses, importable from config (which builds DEFAULT_SKIN) and
from render (which consumes the built config). The controller overlays
the RING PRESET (DOMY/LOOP are ring preset names — nothing more) and
the user's display choices onto DEFAULT_SKIN at build time. Asset fields
hold absolute paths; a None asset means "draw procedurally".
"""

from dataclasses import dataclass, field
from pathlib import Path

from config import constants, dial, palette, paths


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
    """THE COMPOSITIONAL RING MODEL (owner decree 2026-08-05): a ring is
    ALWAYS the composition of an OUTER band + an INNER band + the
    jewels in the outer's own empty fields + an optional crown-text arc — there is no more single monolithic plate and no
    procedural fallback; `render.layers.ring.RingLayer.paint` composes
    `outer_asset` then `inner_asset` unconditionally."""

    outer_asset: Path                  # the outer band plate (empty jewel fields)
    inner_asset: Path                  # the inner minute-track band
    jewels: dict[int, str] = field(default_factory=dict)  # hour -> jewel glyph replacing the numeral
    # The owner's GOLD jewel art: hour -> the master file, ALWAYS gold
    # (built by the controller's build_skin). The ring tint never
    # touches it.
    jewel_art: dict[int, Path] = field(default_factory=dict)
    # hour -> the active FINISH ("gold"/"silver"/"bronze", the preset's
    # accent jewel wearing the opposite metal) — silver/bronze are
    # derived from the gold master AT LOAD (owner 2026-07-19,
    # `render.asset_recolor.jewel_metal_file`; retired the ~15 MB of
    # pre-rendered `_silver.png`/`_bronze.png` files).
    jewel_metal: dict[int, str] = field(default_factory=dict)
    # hour -> a HEIGHT multiplier for that seat's jewel art (CROSS-
    # WORDS/SHINE round, owner UV inbox 2026-07-27): the Eye's shine
    # masters pad the triangle with the glory of rays, so build_skin
    # stamps `constants.RING_EYE_SHINE_ENLARGE[source]` here and the
    # triangle draws the SAME size as the no-light master — only the
    # rays extend beyond it. Absent hour = 1.0 (every plain jewel).
    jewel_zoom: dict[int, float] = field(default_factory=dict)
    # hour -> True when that seat's baked-in art already carries its own
    # light (SHADOW/SHINE round, owner ruling 2026-08-06: "the Eye with
    # SHINE renders NO shadow — the baked shine replaces it"): the Dollar's
    # Eye-of-Providence glory-of-rays master IS the light, so the ring's
    # own cast-shadow stamp would fight it. Stamped by `build_skin`
    # alongside `jewel_zoom` (Rule #5, same per-hour plumbing shape,
    # SAME condition — any seat whose resolved art stem starts with
    # "Eye_shine", toggle-driven or an explicit custom pick alike).
    # Absent hour = False (every ordinary jewel keeps its shadow).
    jewel_no_shadow: dict[int, bool] = field(default_factory=dict)
    # The per-jewel HOVER LEGEND (ROADMAP 15b, owner "malo legende"):
    # hour -> {name, reading} for a preset that carries one (the
    # Dollar, DOMY and LOOP today — CROSS-WORDS round 2026-07-27;
    # empty {} for The One/Templar and any custom ring) — see
    # data.rings.validate_preset and render.compositor's ring-band
    # hover.
    jewel_legend: dict[int, dict] = field(default_factory=dict)
    # The outer GREAT SEAL CROWN TEXT ARC (TASK 1, owner "može radi"
    # 2026-07-19, CANON.md §The Banknote; corrected MOTO-FIX round,
    # owner correction 2026-07-19, the dollar's Great Seal reference
    # image): built once by app.controller.build_skin from the preset's
    # own `crown_text` card field (data.rings.validate_preset ->
    # core.crown_text.crown_glyph_angles) — curved text just outside the
    # ring band, its pinned jewels landing on the SAME six hexagram
    # seats the ring's own banknote jewels occupy (MASON outside, the
    # Eye inside at the crown — the G's seat before the DOLLAR/EYE
    # round). Each entry: {"text": the crown text string (spaces included,
    # for reference), "glyphs": a tuple of (gold_asset_path, dial_angle)
    # pairs, ONE per non-space character, ready for render.layers.
    # RingLayer to draw — spaces are already filtered out here, so the
    # render loop never checks for them. Empty for every preset but
    # the Dollar today; both entries now draw at the SAME
    # RING_CROWN_TEXT_RADIUS_FRACTION — the two arcs are angularly disjoint
    # (ANNUIT COEPTIS over the top, NOVUS ORDO SECLORUM under the
    # bottom) so they never collide; the old two-radius-by-list-order
    # scheme is gone.
    crown_text: tuple[dict, ...] = ()
    # The SINGLE finish every crown text glyph wears (owner: "in the ring
    # jewel metal/color family") — the same settings.ring_finish the
    # ring's own Trinity-triangle jewels wear, resolved once in
    # build_skin. Unlike `jewel_metal` this is NOT per-hour: the crown text
    # is read as ONE continuous inscription, not a seat-by-seat split.
    crown_text_metal: str = "gold"


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
    day_color: str                     # procedural Earth fallbacks
    night_color: str
    # NOMINAL orbit only (THE CLEAR ORBIT LANE, owner verdict 2026-08-09)
    # — read solely by `render.daylight.moon_transit_opacity`'s touch-
    # angle approximation. The DRAWN orbit is computed live by
    # `config.dial.earth_moon_orbit_fraction`, never this field.
    orbit_fraction: float
    scale: float                       # Earth size, fraction of the dial diameter
    moon_asset: Path | None            # full-moon disc image (terminator drawn over it)
    moon_lit_color: str                # procedural moon fallback
    moon_dark_color: str
    moon_shadow_alpha: float           # darkness of the unlit part over the image
    moon_orbit_fraction: float         # same NOMINAL-only retirement as orbit_fraction
    moon_scale: float                  # smaller than the Earth (owner: ~72%)
    moon_hidden_alpha: float = 0.5     # marker opacity while the moon is
                                       # BELOW the horizon (owner spec
                                       # 2026-07-12; Settings slider)
    # THE MOON TRANSIT OPACITY (Watch Face Phase 4, R-35): the rim-
    # transit dimming `render.daylight.moon_transit_opacity` applies
    # while the Moon marker meets the Earth marker — was a bare
    # `dial.MOON_TRANSIT_OPACITY` constant, now a per-skin field an
    # override can replace (`settings.moon_transit_alpha`).
    transit_alpha: float = dial.MOON_TRANSIT_OPACITY


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
    palette_style: str = "primary"       # "primary" | "secondary" | "tertiary" —
                                       # Star+Aura hues; "cube" is the Cube
                                       # canon's third wheel (Genesis/Council/
                                       # Character, trio/hexa/octa ONLY —
                                       # palette.effective_palette_style
                                       # normalizes it away elsewhere); on the
                                       # Calendar pointer the style PICKS THE
                                       # WHEEL: paint = Zodiac, light = Almanac
    calendar_mount: str = "zodiac"     # the DESIGN ZODIAC law's MOUNT (R9a,
                                       # GENERALIZED 2026-07-29): "off" or any
                                       # config.constants.CALENDAR_MOUNTS key —
                                       # twelve wedges of marks at CALENDAR_
                                       # MOUNT_RADIUS_FRACTION (a 24-set seats
                                       # TWO per wedge), independent of
                                       # palette_style. The old `calendar_
                                       # lighting` sibling is DELETED: the
                                       # Calendar no longer lights a wedge.
    # THE ARCHETYPE MODE (owner sealed package 2026-07-16): the active
    # (pointer, palette_style) shows ITS archetype — the diamonds carry
    # the stained-glass figures, the hour hand lights the one whose
    # hour-space it is in, and the weekday model and ALL THREE SLOTS
    # switch OFF at the render level (render.slot_layout.enabled_slots) —
    # the user's slot settings stay untouched, so toggling back
    # restores everything. Aurora/Calendar have no archetype: the mode
    # is inert there.
    archetype_mode: bool = False
    # THE CUBE LOOK (owner seal 2026-07-26, CUBE.md §Display laws): the
    # Double-Trinity family wheels — Court (trio primary), Genesis (trio
    # cube), Council (hexa tertiary) — render as the corner-view CUBE when
    # True: the arm diamonds widen to the regular 180/N halves and tile
    # the hexagon into the visible cube faces
    # (render.skin_geometry.cube_look_active / arm_half_deg). False = Diamond,
    # the slim-arm medallion form. Inert on every other wheel.
    cube_look: bool = False
    # THE DAYLIGHT SWITCH (owner 2026-07-27): the Calendar and the Rose
    # let the reader turn the day/night law off and stand in flat full
    # color — their wheels are read as a wheel first and a clock second.
    # Inert on every other pointer, which always runs day/night
    # (render.skin_geometry.daylight_active).
    daylight: bool = True
    # THE POINTER SHAPE (Pointers REWORK phase 1, owner sheet
    # UV/Pointers.png 2026-07-29): "star" — the diamond stars shipped so
    # far; "polygon" — the plain polygon of the same arms (square /
    # hexagon / octagon, the CUBE hexagon on the Trinity), the Calendar's
    # twelve-point and the Rose's twenty-four-point touching stars.
    # `config.constants.POINTER_SHAPES`; the armless Aurora ignores it
    # (render.skin_geometry.polygon_shape).
    pointer_shape: str = constants.POINTER_SHAPE_DEFAULT
    # THE EDGE PULL of the true polygons (trio/cross/hexa/octa only —
    # render.shapes.polygon_curvature): 0.0 the plain polygon, toward
    # 1.0 each outer edge's midpoint pulled inward to the star's own
    # inner radius; `polygon_edge` draws that pull as one concave arc
    # ("smooth") or as two straight segments meeting in a V ("notched").
    polygon_curvature: float = constants.POLYGON_CURVATURE_DEFAULT
    polygon_edge: str = constants.POLYGON_EDGE_DEFAULT
    # HIDE NIGHT BORDERS (owner option 2026-07-29): with the day/night
    # law running, the arm/polygon OUTLINE strokes are drawn only over
    # the sunlit arcs — the night keeps its fills and loses the border
    # mesh (render.daylight.border_clips). False = today's law, borders
    # around the whole circle.
    hide_night_borders: bool = False
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
    # THE TWO WORLD-MODES (ring_rework.md §1, `core.world`): which of the
    # two turns. "geocentric" is the dial every release before this one
    # drew — the star travels toward true solar noon, the hour band and
    # every numeral stay fixed, 12 on top. "heliocentric" stands the
    # star still and turns the WORLD instead, and inverts the whole dial
    # at night. Solar Rotation below stays its OWN independent switch.
    # Named in full — a bare `mode` beside `archetype_mode`/`z_mode` in
    # a flat namespace names nothing at all.
    world_mode: str = dial.WORLD_MODE_DEFAULT
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
    # the finish picks the owner's jewel art set (gold = M/D/Y/P/H
    # gold + silver Omega; silver = the inverse) — jewels never tint.
    ring_tint: str | None = None
    # THE OUTER/INNER SPLIT TINT (R-21, owner correction 2026-08-05):
    # None (default) makes the inner minute-track band follow
    # `ring_tint` exactly like every release before the split art
    # existed; a hex overrides it independently. Read only when the
    # split art is on disk (`render.layers.ring.RingLayer.paint`) — a
    # no-op on the single-plate fallback.
    ring_tint_inner: str | None = None
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
    ring_jewels_scale: float = 1.0     # multiplies RING_JEWEL_ART_SCALE
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
    # `render.skin_geometry.aura_palette_for` — the star diamonds
    # (`render.skin_geometry.palette_for`, now RAW) no longer move with it.
    # 1.0 unchanged, 0.0 grays every Aura hue to its own brightness.
    pointer_saturation: float = 1.0
    # RING (new, Session 21-D): scales the RING BAND art's (the ring
    # plate + its jewel/numeral overlay) HSV saturation in
    # `render.layers.ring.RingLayer`, applied AFTER the ring_tint recolor —
    # 1.0 unchanged, 0.0 grays it to its own brightness. The Umbra and
    # hands do not read this (see layers.md's RingLayer note).
    ring_saturation: float = 1.0
    # THE UMBRA COLORING MENU (Watch Face Phase 4, R-22, see
    # `render.layers.background.BackgroundLayer._draw_umbra`): "follow"
    # (default) reads `ring_tint` like every release before this one;
    # "custom" reads `umbra_tint` instead. `umbra_saturation` scales the
    # active tint's HSV saturation before the tritone map runs.
    umbra_tint_mode: str = "follow"
    umbra_tint: str | None = None
    umbra_saturation: float = 1.0
    # THE UMBRA OPACITY (Watch Face Phase 4, R-15, owner-requested): a
    # plain layer-alpha multiplier at composite time — 1.0 unchanged.
    umbra_alpha: float = 1.0
    # THE AURA COLORLESS COLORING (Watch Face Phase 4, R-23): read only
    # while `colorful` is off (`BackgroundLayer.paint`'s existing
    # colorless branch) — "follow"/"white"/"black"/"custom".
    aura_off_tint_mode: str = "white"
    aura_off_tint: str | None = None
    # THE HANDS FREE COLOR + SATURATION (Watch Face Phase 4, R-24/R-25):
    # None follows `ring_tint` like every hand always has; a hex
    # overrides it independently. Saturation scales the hand pack's own
    # HSV, the same parameter the ring plate already uses.
    hands_tint: str | None = None
    hands_saturation: float = 1.0
    # THE INDICES FREE COLOR (Watch Face Phase 4, R-24): an EXTRA tint
    # layered over the ring jewels' metal finish in
    # `render.layers.ring.RingLayer._draw_ring_glyph` — None (default)
    # leaves the metal finish untouched, exactly as today.
    jewels_tint: str | None = None
    # CROWN TEXT (R-24/Phase-6-debt correction, owner 2026-08-05: "Crown
    # tekst je onaj tekst koji piše oko sata — faith, hope, suffering")
    # — the outer Great Seal CROWN TEXT arc (`RingSpec.crown_text`,
    # `render.layers.ring.RingLayer._draw_crown_text`) IS this element; these
    # three fields are its own opacity/size/color controls, independent
    # of the ring jewels' own `ring_jewels_scale`/`jewels_tint`:
    #   * `crown_text_alpha` — a plain layer-alpha multiplier, 1.0 = today's
    #     full opacity (no skin varies this yet, so a direct value like
    #     `umbra_alpha`, not a None-override).
    #   * `crown_text_scale` — multiplies `dial.RING_CROWN_TEXT_SIZE` ON TOP OF
    #     `ring_jewels_scale` (which still scales it too, unchanged) —
    #     1.0 = today's size. `config.defaults.dial_window_margin_
    #     fraction` reads this so the window never clips a scaled-up
    #     Crown Text.
    #   * `crown_text_tint` — an EXTRA tint layered over the crown text glyphs'
    #     metal finish, resolved INDEPENDENTLY of `jewels_tint` (the two
    #     controls no longer share one recolor): None (default) follows
    #     `ring_tint`, like the hands; a hex overrides it.
    # A no-op for every preset without a crown text (The One, Templar, every
    # custom ring) — nothing draws, nothing to grey but the control.
    crown_text_alpha: float = 1.0
    crown_text_scale: float = 1.0
    crown_text_tint: str | None = None
    # THE LIVE NUMERAL BANDS (ring_rework.md §2/§5 + hour_numerals.md
    # §8): the dial's two numeral bands are RENDERED — at startup and on
    # every settings change, never per frame — so every knob the ledger
    # SETTLED rides the skin the way every other display choice does.
    # `render.layers.numerals.band_spec` turns these into the band cache
    # key; `config.dial` holds the rosters, ranges and SETTLED defaults.
    #   * `numeral_outer_size` / `minutes_size` — the two bands'
    #     numeral heights, in the ledger's own units (§8), so a setting
    #     survives any change of dial resolution.
    #   * `numeral_outer_ring_size` — the WIDTH of the band the jewels
    #     and numbers stand in, as a multiplier of the measured band.
    #   * `numeral_face` / `minutes_face` — the two rosters (§7). The
    #     LIVE CROWN has no face at all any more (THE ONE PLATE LAW,
    #     owner decree 2026-08-07): it draws the letter plates, so its
    #     old `crown_face` pick went with the font it chose.
    #   * `numeral_seating` — `arc` or `upright` (§4); the inner band
    #     follows the outer's pick.
    #   * `numeral_relief` / `numeral_depth` / `numeral_light` /
    #     `numeral_darkness` / `numeral_contact_blur` / `numeral_border`
    #     — the relief and light model (§5, §6) at its SETTLED defaults.
    #   * `crown_time_format` — `hh:mm` (the standard default) or
    #     `12h 35min`, whose h/min ride a smaller cut of the same
    #     plates (`dial.CROWN_SMALL_CUT_FRACTION`).
    numeral_outer_size: int = dial.NUMERAL_OUTER_SIZE_DEFAULT
    minutes_size: int = dial.MINUTES_SIZE_DEFAULT
    numeral_outer_ring_size: float = dial.NUMERAL_OUTER_RING_SIZE_DEFAULT
    numeral_face: str = dial.NUMERAL_OUTER_FACE_DEFAULT
    minutes_face: str = dial.MINUTES_FACE_DEFAULT
    numeral_seating: str = dial.NUMERAL_SEATING_DEFAULT
    numeral_relief: str = dial.NUMERAL_RELIEF_DEFAULT
    numeral_depth: float = dial.NUMERAL_DEPTH_DEFAULT
    numeral_light: str = dial.NUMERAL_LIGHT_DEFAULT
    numeral_darkness: float = dial.NUMERAL_DARKNESS_DEFAULT
    numeral_contact_blur: float = dial.NUMERAL_CONTACT_BLUR_DEFAULT
    numeral_border: float = dial.NUMERAL_BORDER_DEFAULT
    crown_time_format: str = dial.CROWN_TIME_FORMAT_DEFAULT
    # The ACTIVE ring preset's name — the ONE thing the numeral layers
    # need from the card, so `dial.RING_LIVE_CROWN` can say whether this
    # watch carries a live crown at all (The One, Templar) without the
    # render layer reaching back into `data.rings`.
    ring_name: str = ""
    # THE DISPLAY CONTEXT (owner bug 2026-07-28, multi-watch colour
    # leak): this watch's OWN art source, subdial plate set and metal
    # shades — see `config.paths.DisplayContext`. It rides the SKIN
    # because the skin is what a watch hands to its compositor, and it
    # is what every render/hover/dialog entry point installs
    # (`with paths.display(skin.display)`) before resolving any art.
    # Three watches, three contexts, no shared process state.
    display: paths.DisplayContext = paths.DEFAULT_DISPLAY


def missing_assets(skin: SkinDefinition) -> list[Path]:
    """Every referenced asset that does not exist on disk. The caller must
    surface a non-empty result visibly (a missing asset would otherwise
    fail inside paintEvent, where Qt swallows the exception and leaves a
    silently broken dial)."""
    referenced = [
        skin.background.base_asset,
        skin.ring.outer_asset,
        skin.ring.inner_asset,
        skin.year_marker.moon_asset,
        skin.hands.hour.asset,
        skin.hands.minute.asset,
        skin.hands.second.asset if skin.hands.second else None,
        *skin.ring.jewel_art.values(),
        *(path for crown_entry in skin.ring.crown_text for path, _ in crown_entry["glyphs"]),
        *skin.weekday_set.bodies.values(),
        *skin.year_marker.variants.values(),
    ]
    # Canonical paths resolve through the active ART SOURCE first
    # (owner 2026-07-14: assets/<root>/<source>/... with fallback).
    return [
        path for path in referenced
        if path is not None and not paths.art_file(path).exists()
    ]
