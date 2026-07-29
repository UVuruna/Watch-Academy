"""The seven dial layers (closed set) with cadence-driven caching.

Every layer paints in a coordinate system whose origin is the dial
center; dial angles are degrees CLOCKWISE from the top (the core
convention), converted to Qt's counterclockwise-from-3-o'clock only
inside the pie/position helpers here.
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QFont,
    QFontMetricsF,
    QImageReader,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)

from config import archetypes, constants, defaults, palette, paths
from core import angles, continents
from core.clock_state import DayContext, TickState
from core.deep_time import format_official, real_year
from core.sun import DaylightRegime, SunDay
from core.year_wheel import almanac_marker_angle, almanac_month_index
from render.assets import AssetCache
from render.asset_recolor import letter_metal_file
from render.asset_variants import moon_lit_region, ring_face_color, subdial_plate_file
from skins.manifest import HandSpec, SkinDefinition


class Cadence(Enum):
    STATIC = "static"    # rebuild on skin/size/DPI change
    DAILY = "daily"      # rebuild on DayContext change
    MINUTE = "minute"    # painted live every tick


@dataclass(frozen=True)
class RenderContext:
    skin: SkinDefinition
    day: DayContext
    tick: TickState | None           # None while compositing STATIC/DAILY layers
    radius: float                    # logical px, dial radius
    cache: AssetCache
    dpr: float
    rotation: float = 0.0            # Star/Aura/Umbra/slot rotation: the solar
                                     # offset, or 0 in upright mode (the noon
                                     # marker stays solar — day.star_rotation)
    hovered: str | None = None       # element under the cursor ("earth",
                                     # "moon", "octa_slot", "body:<name>") —
                                     # drawn hover_enlarge times larger
    reveal_active: bool = False      # reveal-week (owner 2026-07-16): an
                                     # Omega double-click raises every
                                     # non-active weekday body to full
                                     # opacity for REVEAL_WEEK_DURATION_S
    archetype_lit: int | None = None  # Archetype mode (owner 2026-07-16):
                                     # the figure whose HOUR-SPACE holds the
                                     # hour hand draws FULL, the rest ghost —
                                     # computed from the live tick like the
                                     # calendar wedge, keying the composite


def dial_point(theta_deg: float, distance: float) -> QPointF:
    """Point at dial angle theta (clockwise from top) and given distance."""
    rad = math.radians(theta_deg)
    return QPointF(distance * math.sin(rad), -distance * math.cos(rad))


def draw_pie(painter: QPainter, radius: float, start_deg: float, end_deg: float) -> None:
    """Filled pie between two dial angles going CLOCKWISE (end > start,
    possibly beyond 360 for wrap-around arcs)."""
    rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
    qt_start = int(round((90.0 - start_deg) * 16))
    qt_span = int(round(-(end_deg - start_deg) * 16))
    painter.drawPie(rect, qt_start, qt_span)


def draw_pixmap_centered(
    painter: QPainter, ctx: "RenderContext", asset: Path, pos: QPointF,
    height: float, tint: str | None = None, desaturate: bool = False,
    metal: str | None = None, saturation: float = 1.0,
) -> None:
    """Asset rasterized to `height` and drawn centered at `pos` — the one
    shared image path of weekday bodies and the year marker (Rule #5).
    `tint` tritone-maps the image; `desaturate` grays it first;
    `metal` runs the hue-SELECTIVE bronze-to-gold/silver swap (only the
    warm bronze pixels change — owner insight 2026-07-12); `saturation`
    scales the FINAL pixmap's HSV saturation (owner 2026-07-18, Session
    21-D — the Ring saturation slider's one recolor spot; 1.0 is a
    no-op for every OTHER caller, which never passes it)."""
    pixmap = ctx.cache.pixmap_by_height(
        asset, height, ctx.dpr, tint, desaturate, metal, saturation
    )
    logical_w = pixmap.width() / ctx.dpr
    painter.drawPixmap(QPointF(pos.x() - logical_w / 2, pos.y() - height / 2), pixmap)


def draw_outlined_text(
    painter: QPainter, center: QPointF, text: str, font: QFont
) -> None:
    """White label with a black outline (readable over bright bodies) —
    the one shared text style of the weekday and date markers (Rule #5)."""
    metrics = QFontMetricsF(font)
    baseline = QPointF(
        center.x() - metrics.horizontalAdvance(text) / 2,
        center.y() + (metrics.ascent() - metrics.descent()) / 2,
    )
    path = QPainterPath()
    path.addText(baseline, font, text)
    outline_width = max(1.0, font.pixelSize() * defaults.LABEL_OUTLINE_WIDTH)
    painter.setPen(QPen(QColor(*palette.LABEL_OUTLINE_RGBA), outline_width))
    painter.setBrush(QColor(*palette.LABEL_FILL_RGBA))
    painter.drawPath(path)


def moon_transit_opacity(spec, year_angle: float, moon_angle: float) -> float:
    """Opacity of the Moon marker while the Earth is also shown: when the
    smaller Moon meets the Earth on the shared rim (their discs would
    overlap) it passes OVER the Earth at reduced opacity — an eclipse-like
    transit where both stay visible (owner decision). The caller skips
    this when the Earth element is switched off."""
    delta = abs(year_angle - moon_angle) % 360.0
    delta = min(delta, 360.0 - delta)
    # Angular size at which the two discs touch on the shared orbit.
    touch_deg = math.degrees((spec.scale + spec.moon_scale) / spec.orbit_fraction)
    return 1.0 if delta >= touch_deg else defaults.MOON_TRANSIT_OPACITY


def palette_for(skin: SkinDefinition) -> tuple:
    """The active Star+Aura BASE palette — ONE source for both the star
    diamonds and the background wedges (owner spec): the user's custom
    hues when set (settings dialog), otherwise the owner preset. RAW —
    no saturation applied here any more (owner fix round E, 2026-07-19,
    slika 2: the Saturation slider must move the AURA only, never the
    star diamonds). `StarLayer` reads THIS function directly; the Aura
    consumption path reads `aura_palette_for` below instead."""
    return (
        skin.palette_override if skin.palette_override is not None
        else palette.PALETTE_PRESETS[(skin.pointer, skin.palette_style)]
    )


def aura_palette_for(skin: SkinDefinition) -> tuple:
    """`palette_for(skin)` with the Aura Saturation slider applied (owner
    fix round E, 2026-07-19, slika 2: re-scoped from "Pointer" — the
    slider now scales ONLY the colored period wedges behind/around the
    diamonds, `BackgroundLayer`'s Aura, never the star diamonds
    themselves). The storage key stays `pointer_saturation` (Settings ▸
    Colors label renamed to "Aura"; migrating the persisted key would
    add a settings-migration path for a purely internal name with zero
    user-visible benefit, so the field keeps its name — this docstring
    is the pointer). 1.0 leaves the hues untouched."""
    hues = palette_for(skin)
    if skin.pointer_saturation == 1.0:
        return hues
    return tuple(_saturate_hue(hue, skin.pointer_saturation) for hue in hues)


def _saturate_hue(hue: str, factor: float) -> str:
    """Scale one `#RRGGBB` hue's HSV saturation by `factor` (0.0..1.0,
    clamped) — value and hue untouched, so 0.0 grays the color to its
    OWN brightness rather than to a flat white/black."""
    color = QColor(hue)
    h, s, v, a = color.getHsvF()
    color.setHsvF(max(h, 0.0), max(0.0, min(1.0, s * factor)), v, a)
    return color.name()


def arm_offset_deg(skin: SkinDefinition) -> float:
    """THE OFFSET WHEELS (`constants.WHEEL_ARM_OFFSET_DEG`) — the wheels
    that seat their arms off the pointer's own default angles, read by
    every arm consumer through this ONE function (Rule #5): the star
    diamonds and polygon faces, the Aura wedges, the weekday slots, the
    lit-index math and the arm hit-test.

    - THE GENESIS INVERSION (owner: "trougao ka dole", CUBE.md): the
      trio's TERTIARY wheel swings 180°, onto 24h/16h/08h.
    - THE SEASONS ROTATION (owner 2026-07-29): the cross's TERTIARY
      wheel turns 45°, half a wedge, so its color BOUNDARIES land on
      12h/3h/6h/9h — the astronomical seasons, each beginning at its
      turning point. The cross's other two wheels stay centered on the
      cardinals (meteorological).

    0 on every other wheel."""
    return constants.WHEEL_ARM_OFFSET_DEG.get(
        (skin.pointer, skin.palette_style), 0.0
    )


def aura_wedge_anchor(skin: SkinDefinition) -> tuple[float, float]:
    """Where a hue's Aura WEDGE stands relative to that hue's LEAD RAY,
    as (low, high) FRACTIONS of the hue's own share of the circle —
    `constants.AURA_WEDGE_ANCHOR_DEFAULT` and, on the Rose,
    `constants.ROSE_AURA_WEDGE_ANCHOR` (owner's correction round
    2026-07-29, his exact numbers).

    The lead ray is the direction the hue wears on the topmost (0°)
    star, which on a one-star pointer is simply its arm — so the default
    (−½, +½) is the standing arm-centered wedge. The Rose wears each hue
    on THREE rays and its two wheels read them differently: LEGACY's
    wedge TRAILS the lead ray (−1, 0 — the past lies behind the hour, so
    the boundaries land ON the lead-ray hours), PROPHECY's stands
    CENTERED on it (−½, +½ — past and future symmetric).

    THE PROPHECY SHIFT IS GONE (owner correction 2026-07-29): the star
    tips never move, both wheels keep every ray on a full hour, and the
    per-wheel difference lives HERE, in the background alone."""
    if skin.pointer != "rose":
        return constants.AURA_WEDGE_ANCHOR_DEFAULT
    return constants.ROSE_AURA_WEDGE_ANCHOR[
        palette.effective_palette_style(skin.pointer, skin.palette_style)
    ]


def polygon_shape(skin: SkinDefinition) -> bool:
    """Whether the reader asked for the POLYGON shape on a pointer that
    HAS one (owner sheet 2026-07-29). Aurora draws no pointer at all, so
    the setting is inert there — never rewritten, the
    `effective_palette_style` pattern."""
    return skin.pointer_shape == "polygon" and skin.pointer != "aurora"


def polygon_faces(skin: SkinDefinition) -> bool:
    """Whether the drawn arm is a POLYGON FACE — the kite filling its
    share of a plain 3/4/6/8-gon — rather than a star diamond. The
    Calendar's twelve-point and the Rose's twenty-four-point "polygons"
    are STARS with touching arms, so they answer False and take the
    star construction (and, with it, no curvature)."""
    return polygon_shape(skin) and skin.pointer in constants.POLYGON_POINTERS


def drawn_arm_count(skin: SkinDefinition) -> int:
    """How many arms the drawn wheel really carries — which is NOT
    always the palette size: the polygon shape counts what the READER
    counts (`POINTER_DIAL_COUNTS` — the Rose's 24 rays, the Calendar's
    12), the star shape counts one star's arms (the Rose draws its 8
    three times; the Calendar's two hexagrams carry 6 each)."""
    if polygon_shape(skin):
        return constants.POINTER_DIAL_COUNTS[skin.pointer]
    if skin.pointer == "calendar":
        return constants.CALENDAR_STAR_ARMS
    return constants.POINTER_POINTS[skin.pointer]


def arm_half_deg(skin: SkinDefinition) -> float:
    """The drawn arm half-angle: the pointer's slim-diamond value —
    EXCEPT wherever the arms fill their whole share of the circle, where
    the half is the regular `180/N` of the DRAWN arm count:

    - the CUBE look, whose three (trio) or six (hexa) rhombi tile the
      hexagon exactly — the corner-view cube's visible faces (CUBE.md);
    - the POLYGON shape, whose faces meet edge to edge (the square's 45°,
      the hexagon's 30°, the octagon's 22.5°, the cube hexagon's 60°) and
      whose Calendar/Rose stars have adjacent arms exactly touching
      (15° on twelve rays, 7.5° on twenty-four);
    - the CALENDAR's star shape, whose two hexagrams are regular
      six-point stars (30°).

    The star geometry formula (inner = tip / 2cos(half)) lands the side
    vertices exactly where each of those figures needs them — the shapes
    are pure angle math, never new art."""
    if polygon_shape(skin) or cube_look_active(skin):
        return 180.0 / drawn_arm_count(skin)
    if skin.pointer == "calendar":
        return 180.0 / constants.CALENDAR_STAR_ARMS
    return constants.POINTER_ARM_HALF_ANGLE_DEG[skin.pointer]


def rose_star_offsets(skin: SkinDefinition) -> tuple:
    """THE ROSE'S THREE STARS in DRAW ORDER (owner seal 2026-07-27,
    CUBE.md §The Rose) — bottom of the z-stack first, topmost last.
    Legacy leans wholly behind the hour (−30°, −15°, 0°); Prophecy is
    symmetric and rides the FUTURE over the PAST (−15°, +15°, 0°). The
    0° star is last on both, so the fully visible arm always points at
    true 12h. `()` on every other pointer — a one-star pointer draws
    its single star through the same loop with no offset."""
    if skin.pointer != "rose":
        return ()
    return constants.ROSE_STAR_OFFSETS[
        palette.effective_palette_style(skin.pointer, skin.palette_style)
    ]


def rose_star_set(offset: float) -> str:
    """Which figure set the Rose star at `offset` carries (CUBE.md §The
    Rose): "modern" on the true hours, "historical" one ray back, and
    "archetypal" wherever its wheel sent the myth star — −30° on Legacy
    (the myth we inherited), +15° on Prophecy (the myth that comes). The
    three words are `cube.FIGURE_SETS`, so the star names the very set
    the roster and the disk register name (Session 24)."""
    return constants.ROSE_STAR_SETS[offset]


def _wheel(skin: SkinDefinition) -> str:
    """The skin's EFFECTIVE wheel slot — the stored palette_style
    normalized to what this pointer actually serves (Rule #5: the same
    `palette.effective_palette_style` every other wheel reader uses)."""
    return palette.effective_palette_style(skin.pointer, skin.palette_style)


def horizontal_duality(skin: SkinDefinition) -> bool:
    """Whether this skin's Sunday duality rides the HORIZONTAL blue<->red
    axis — Servant on blue 06h left, Ruler on red 18h right (owner seal
    2026-07-29): the Rose on BOTH its wheels, plus the wheels
    `constants.HORIZONTAL_DUALITY_WHEELS` names (the Compass's Character
    wheel, which wears the same ROSE_PALETTE hues)."""
    return (
        skin.pointer == "rose"
        or (skin.pointer, _wheel(skin)) in constants.HORIZONTAL_DUALITY_WHEELS
    )


def center_duality(skin: SkinDefinition) -> bool:
    """Whether this skin's Sunday duality lives in ONE CENTER image —
    the Trinity and the Prism on every wheel, plus the wheels
    `constants.CENTER_DUALITY_WHEELS` names (the Quaternity's Seasons
    wheel: its arms turn onto the diagonals, so no 12h/24h seat exists
    to hold a second face — owner seal 2026-07-29)."""
    return (
        skin.pointer in ("hexa", "trio")
        or (skin.pointer, _wheel(skin)) in constants.CENTER_DUALITY_WHEELS
    )


def _base_weekday_slots(skin: SkinDefinition) -> tuple:
    """The raw weekday table this skin reads BEFORE offsets and flips:
    the pointer's own — except the horizontal-duality wheels of other
    pointers (the Compass's Character wheel), which take the ROSE's
    hue-seated table wholesale, because their arms wear the Rose's own
    hues and the seat is the HUE (owner seal 2026-07-29)."""
    if (skin.pointer, _wheel(skin)) in constants.HORIZONTAL_DUALITY_WHEELS:
        return constants.POINTER_WEEKDAY_SLOTS["rose"]
    return constants.POINTER_WEEKDAY_SLOTS[skin.pointer]


def _duality_ruler_default_angle(skin: SkinDefinition) -> float:
    """The Ruler's (the "sun" occupant's) UNFLIPPED seat — wherever the
    skin's own weekday table seats him, before any flip
    (`_duality_flipped`) swaps it with the Servant's."""
    return next(
        angle
        for angle, occupants in _base_weekday_slots(skin)
        if "sun" in occupants
    )


def _duality_servant_default_angle(skin: SkinDefinition) -> float:
    """The Servant's UNFLIPPED seat, before any flip: the blue 06h/270°
    arm on every horizontal-duality wheel (`constants.SERVANT_SEAT_
    ANGLE`), the 24h bottom everywhere else."""
    if horizontal_duality(skin):
        return constants.SERVANT_SEAT_ANGLE["rose"]
    return constants.SOUTH_SLOT_ANGLE


def _duality_flipped(skin: SkinDefinition) -> bool:
    """Whether this theme swaps the Ruler's and the Servant's seats on
    this skin (the two faces swap ARMS, never names or articles):
    on a HORIZONTAL wheel, the Sacred-Axis themes (`constants.DUALITY_
    RULER_ON_COLD_POLE` — Christianity pulls to the cold blue pole,
    Satanism to the warm red); on a VERTICAL wheel, the geographic
    themes (`constants.DUALITY_SERVANT_ON_TOP` — the Arctic IS the
    north, owner seal 2026-07-29). A CENTER duality has no seats to
    swap."""
    if center_duality(skin):
        return False
    if horizontal_duality(skin):
        return skin.weekday_theme in constants.DUALITY_RULER_ON_COLD_POLE
    return skin.weekday_theme in constants.DUALITY_SERVANT_ON_TOP


def ruler_seat_angle(skin: SkinDefinition) -> float:
    """The angle the RULER face of Sunday occupies — normally wherever
    the pointer's own weekday table seats the "sun" occupant, UNLESS
    the Duality-Axes config flips this theme (`_duality_flipped`), in
    which case the Ruler takes the Servant's default seat instead —
    the two faces swap ARMS, never their names or articles."""
    if _duality_flipped(skin):
        return _duality_servant_default_angle(skin)
    return _duality_ruler_default_angle(skin)


def servant_seat_angle(skin: SkinDefinition) -> float:
    """The angle the SERVANT face of Sunday occupies (Rule #5 — the ONE
    reader of `constants.SERVANT_SEAT_ANGLE`). The 24h bottom on the
    vertical wheels (Quaternity/Compass primary+secondary); the BLUE
    06h arm on every horizontal wheel (the Rose and the Compass's
    Character wheel), because blue is the servant's hue and red the
    master's (CUBE.md §The Rose) — UNLESS the theme flips
    (`_duality_flipped`: the Sacred Axis pulls Christianity to blue and
    Satanism to red on the horizontal; the geographic flip sends the
    Arctic up top on the vertical), in which case the Servant takes the
    Ruler's default seat instead."""
    if _duality_flipped(skin):
        return _duality_ruler_default_angle(skin)
    return _duality_servant_default_angle(skin)


def daylight_active(skin: SkinDefinition) -> bool:
    """Whether the day/night law paints this dial (owner 2026-07-27).
    Every pointer but the Calendar and the Rose ALWAYS runs day/night;
    those two carry the reader's own switch, because their wheels are
    read as a wheel first and a clock second. The stored setting is
    ignored — never rewritten — on the other five, so it survives a
    pointer switch untouched (the `effective_palette_style` pattern).

    With it False NOTHING on the disc reads the sun (owner correction
    2026-07-29): the star paints once at full day alpha, the Umbra
    stands at flat noon and the Aura wears full color over the whole
    circle. The FIGURE faces are untouched — they keep reading the real
    sky. It answers on the two fields alone (`pointer`, `daylight`), so
    the Design window can ask it of the raw `Settings` object it holds
    and the ONE law serves both (Rule #5)."""
    if skin.pointer not in constants.DAYLIGHT_SWITCH_POINTERS:
        return True
    return skin.daylight


def cube_look_active(skin: SkinDefinition) -> bool:
    """Whether the CUBE look dresses the drawn wheel (owner seal
    2026-07-26, CUBE.md §Display laws): the settings toggle is on AND
    the active wheel belongs to the Double-Trinity family — the Court
    (trio primary), Genesis (trio tertiary) or the Council (hexa tertiary)."""
    return (
        skin.cube_look
        and skin.show_pointer
        and (skin.pointer, skin.palette_style) in constants.CUBE_LOOK_WHEELS
    )


def weekday_slots(skin: SkinDefinition) -> tuple:
    """The skin's weekday slots as DRAWN — every consumer of
    `constants.POINTER_WEEKDAY_SLOTS` reads through this (Rule #5).
    Three transforms, in order: the wheel's own arm offset (slots ride
    the DRAWN arms — pure geometry: each occupant pair stays glued to
    its arm as the Genesis/Seasons wheels swing it; no re-pairing
    doctrine is invented here); the CENTER-duality wheels lift the Sun
    OUT (he stands in the center there — owner seal 2026-07-29); and a
    flipped theme (`_duality_flipped`) relocates the Sun alone onto the
    Servant's default seat — the Servant's own seat is never IN this
    table (drawn separately), and on a shared slot only the SUN moves:
    his slot-mates keep their arm (the cross's Jupiter stays put when
    continents sends the Ruler down to 24h)."""
    slots = _base_weekday_slots(skin)
    offset = arm_offset_deg(skin)
    if offset != 0.0:
        slots = tuple(
            ((angle + offset) % 360.0, occupants) for angle, occupants in slots
        )
    if center_duality(skin):
        return tuple(
            (angle, occupants) for angle, occupants in (
                (angle, tuple(o for o in occupants if o != "sun"))
                for angle, occupants in slots
            )
            if occupants
        )
    if _duality_flipped(skin):
        target = (_duality_servant_default_angle(skin) + offset) % 360.0
        moved, merged = [], False
        for angle, occupants in slots:
            occupants = tuple(o for o in occupants if o != "sun")
            if not occupants:
                continue
            if angle == target:
                occupants, merged = occupants + ("sun",), True
            moved.append((angle, occupants))
        if not merged:
            moved.append((target, ("sun",)))
        slots = tuple(moved)
    return slots


def calendar_wheel(skin: SkinDefinition) -> str:
    """Which of the Calendar's two wheels is active (owner 2026-07-16):
    the palette_style CARRIES the wheel — paint = the Zodiac Dozen,
    light = the Almanac (Month) Dozen."""
    return "zodiac" if skin.palette_style == "primary" else "almanac"


def calendar_wedge_bounds(wheel: str) -> list[tuple[float, float]]:
    """The twelve wedge (start, end) dial angles, index 0 first (the top
    wedge), clockwise (owner 2026-07-16). ZODIAC boundaries sit ON the
    cardinal axes — the top wedge STARTS at the top (12h line); ALMANAC
    wedges are CENTERED on the axes — the top wedge is centered on the
    top (shifted half a wedge earlier). Starts may be negative; draw_pie
    handles the clockwise sweep."""
    step = constants.CALENDAR_WEDGE_DEG
    offset = 0.0 if wheel == "zodiac" else -step / 2.0
    return [(k * step + offset, k * step + offset + step) for k in range(12)]


def calendar_day_arrow(angle_deg: float, radius: float) -> QPolygonF:
    """The Almanac Earth day-arrow (owner 2026-07-16): a small triangle
    at `angle_deg`, tip toward the ring ticks, base inward — the ring
    reads today's date to the day. Tunables in defaults."""
    tip = radius * defaults.CALENDAR_ARROW_TIP_FRACTION
    base = tip - radius * defaults.CALENDAR_ARROW_LENGTH_FRACTION
    half = defaults.CALENDAR_ARROW_HALF_DEG
    return QPolygonF(
        [
            dial_point(angle_deg, tip),
            dial_point(angle_deg - half, base),
            dial_point(angle_deg + half, base),
        ]
    )


# --- Calendar-pointer 12-SET MOUNT (DESIGN ZODIAC law, R9a round 2026-07-21) --
# "Zodiac i sve što ima 12 TREBA da bude moguće da se AKTIVIRA na CALENDAR
# POINTER" (UV/DESIGN/DESIGN INSTRUCTIONS.txt): twelve small marks, one
# per wedge, mounted at CALENDAR_MOUNT_RADIUS_FRACTION — clear of the
# rim-riding Earth/Moon and the center subdial. A mount rides its OWN
# fixed wheel geometry (calendar_mount_wheel), independent of whichever
# wheel the background wedges currently paint (palette_style) — so the
# marks never jump when the owner switches Zodiac/Almanac colors.


def calendar_mount_wheel(mount: str) -> str:
    """Which `calendar_wedge_bounds` geometry a mount set's marks ride —
    read from the roster's own DOZEN SYSTEM (CANON.md §The Two Dozen
    Systems, `defaults.CalendarMount.system`): System "A" rides the
    ZODIAC wheel's cardinal-START wedges (boundaries on the cardinals,
    so the twelve fall into six pairs — sign i's wedge IS its own 30-deg
    arc), System "B" the ALMANAC wheel's cardinal-CENTERED wedges (one
    crown at 12h, one root at 24h, six opposition axes)."""
    return "zodiac" if defaults.CALENDAR_MOUNTS[mount].system == "A" else "almanac"


def calendar_mount_angle(mount: str, index: int) -> float:
    """Dial angle (clockwise from top) of mount seat `index`,
    Calendar-fixed (no rotation, matching the wedges themselves).

    THE SEAT LAW (owner decree 2026-07-29), one formula for both sizes
    (Rule #19 — no per-seat table exists for either):

        wedge      = index // seats_per_wedge
        pitch      = CALENDAR_WEDGE_DEG / seats_per_wedge
        angle      = wedge_center - (wedge_span - pitch) / 2 + slot·pitch

    A 12-set has one seat per wedge, the bracket vanishes and the seat
    IS the wedge center. A 24-set has two, and they land a quarter wedge
    either side of that center — a 15-deg pitch across the whole dial,
    the same pitch the Rose's three stars already stand on."""
    per_wedge = defaults.CALENDAR_MOUNT_SEATS_PER_WEDGE[
        defaults.CALENDAR_MOUNTS[mount].seats
    ]
    start, end = calendar_wedge_bounds(calendar_mount_wheel(mount))[
        index // per_wedge
    ]
    pitch = constants.CALENDAR_WEDGE_DEG / per_wedge
    first = (start + end) / 2.0 - (constants.CALENDAR_WEDGE_DEG - pitch) / 2.0
    return first + (index % per_wedge) * pitch


def calendar_mount_mark_height(mount: str, radius: float) -> float:
    """A mount mark's drawn height. `CALENDAR_MOUNT_MARK_SCALE` is sized
    so twelve marks never touch at the mount radius; a 24-set halves the
    seat pitch, so its marks halve with it (Rule #19: the size follows
    the seat law, it is not a second tunable). Shared by the paint pass
    and the compositor's own hit target (Rule #5)."""
    per_wedge = defaults.CALENDAR_MOUNT_SEATS_PER_WEDGE[
        defaults.CALENDAR_MOUNTS[mount].seats
    ]
    return 2 * radius * defaults.CALENDAR_MOUNT_MARK_SCALE / per_wedge


def calendar_mount_entries(mount: str) -> tuple[tuple[str, Path | None], ...]:
    """A mount set's (display_name, art_path_or_None) pairs in SEAT
    ORDER — twelve of them for a Dozen, twenty-four for a 24-set. Every
    field comes from the roster's own `defaults.CALENDAR_MOUNTS` entry
    (Rule #5: ONE registry, no per-roster branch survives here).

    Art is ALWAYS graceful-absent (the owner's R7b contract, now the
    universal rule): a plate that is not on disk resolves to None and
    routes the caller to the name-fallback, never a gap. `art_stems`
    covers the sets whose plates are not named for the member (the
    Slavic months are Croatian proper nouns with ASCII stems)."""
    entry = defaults.CALENDAR_MOUNTS[mount]
    return tuple(
        (name, octa_slot_art(entry.art_dir, stem))
        for name, stem in zip(entry.members, entry.stems)
    )


def calendar_mount_current_index(mount: str, day: DayContext) -> int | None:
    """The seat index TODAY owns on the mount's own wheel — the mark
    that earns the emphasis (owner spec: "the mark can inherit that
    brightness") — or None where the roster names no today, and every
    mark rests at the same opacity.

    WHAT counts as today is the roster's own `follows` declaration:
    "sign" reads the running zodiac sign, "month" the running Gregorian
    month (every month-keyed roster — the Chinese animals emphasize the
    same wedge the Slavic months do). Never hemisphere-mirrored: the
    mark sits on its OWN fixed wedge identity, matching what is drawn
    there, unlike the Earth marker's orbit."""
    entry = defaults.CALENDAR_MOUNTS[mount]
    if entry.follows == "sign":
        return entry.members.index(day.zodiac_name)
    if entry.follows == "month":
        return almanac_month_index(day.local_date.month)
    return None


def chinese_mount_dimmed_index(day: DayContext) -> int | None:
    """THE CAT'S DIMMING LAW (owner spec, item 5, R12): the wedge index
    to DIM on the "chinese" mount while The Cat holds the CENTER —
    "the first pass of the month belongs to its animal, the second
    pass — the month that does not exist — belongs to the Cat". None
    outside a Chinese-leap-month window (`DayContext.
    chinese_leap_month_number` is None then, the same field the CENTER
    seat itself reads)."""
    number = day.chinese_leap_month_number
    if number is None:
        return None
    # The doubled LUNAR month's own animal — lunar month N always names
    # CHINESE_ANIMALS[(N + 1) % 12] (month 1 = Tiger, index 2; month 11
    # = Rat, index 0; month 12 = Ox, index 1 — the fixed jianyin
    # numbering core.blue_moon.chinese_leap_month itself counts in) —
    # then the seat that animal holds on the mount's own wheel.
    animal = constants.CHINESE_ANIMALS[(number + 1) % 12]
    return defaults.CALENDAR_MOUNTS["chinese"].members.index(animal)


def _draw_calendar_mount(
    painter: QPainter, ctx: "RenderContext", mount: str
) -> None:
    """The mounted set's marks — one per SEAT (twelve for a Dozen,
    twenty-four for a 24-set), DAILY cadence (the current-mark emphasis
    is a day computation, never per-tick). Missing art falls back to the
    entity's NAME, the SAME convention archetype figures/weekday bodies
    use (`draw_archetype_figure`) — never a blank gap. On the "chinese"
    mount, the doubled month's own animal DIMS below its resting alpha
    while The Cat holds the center (`chinese_mount_dimmed_index`) —
    checked BEFORE the current-month emphasis, so the two never both
    apply to the one mark. A roster that names no today
    (`CalendarMount.follows` None) simply has no emphasized mark."""
    mount_radius = ctx.radius * defaults.CALENDAR_MOUNT_RADIUS_FRACTION
    mark_height = calendar_mount_mark_height(mount, ctx.radius)
    current = calendar_mount_current_index(mount, ctx.day)
    dimmed = chinese_mount_dimmed_index(ctx.day) if mount == "chinese" else None
    for index, (name, art) in enumerate(calendar_mount_entries(mount)):
        pos = dial_point(calendar_mount_angle(mount, index), mount_radius)
        if index == dimmed:
            alpha = defaults.CALENDAR_MOUNT_DIMMED_ALPHA
        else:
            alpha = defaults.CALENDAR_MOUNT_ALPHA + (
                defaults.CALENDAR_MOUNT_LIT_DELTA if index == current else 0.0
            )
        painter.save()
        painter.setOpacity(min(1.0, alpha))
        if art is not None:
            draw_pixmap_centered(painter, ctx, art, pos, mark_height)
        else:
            draw_name_label(painter, name, pos, name_label_px(name, mark_height))
        painter.restore()


def tinted_gray(value: int, tint: str | None) -> QColor:
    """A gray of brightness `value` through the TRITONE map
    black -> tint -> white (owner spec 2026-07-11: whites stay white,
    blacks stay black, the exact midtone lands on the tint) — the
    Umbra's share of the ring recolor; None = plain gray. The scalar
    twin of AssetCache._tinted."""
    if tint is None:
        return QColor(value, value, value)
    hue = QColor(tint)

    def channel(c: int) -> int:
        if value <= 127:
            return c * (value * 2) // 255                    # black -> tint
        return c + (255 - c) * (value * 2 - 255) // 255      # tint -> white

    return QColor(channel(hue.red()), channel(hue.green()), channel(hue.blue()))


def umbra_ladder(shades: int, contrast: str) -> tuple[int, ...]:
    """Shade values, lightest first (owner spec): full contrast runs
    endpoint-inclusive over the whole range (16 shades -> 255..0 step
    17); half contrast takes the CENTERS of N equal bins of the middle
    half [64, 192] (16 -> 188..68 step 8, symmetric about 128)."""
    lightest, darkest = defaults.UMBRA_CONTRAST_SPANS[contrast]
    if contrast == "full":
        return tuple(
            round(lightest - k * (lightest - darkest) / (shades - 1))
            for k in range(shades)
        )
    width = lightest - darkest
    return tuple(
        round(lightest - (k + 0.5) * width / shades) for k in range(shades)
    )


def draw_event_glow(
    painter: QPainter, pos: QPointF, marker_radius: float, color: str,
    strength: float = 1.0, fringe_color: str | None = None,
) -> None:
    """Radial halo behind a year marker relocated to the ring band
    centerline during a season/moon/eclipse event window (owner rework
    2026-07-16): compact — the halo diameter is twice the marker's — and
    intense, so it reads over any background while STRADDLING the ring.
    `color` is GOLDEN for the Sun's events, SILVER for the Moon's, and
    RED/bronze for an eclipse (ROADMAP 15h item 11). `strength` (0..1)
    scales the core/mid alpha — the eclipse call scales it by the
    catalog MAGNITUDE (`eclipse_glow_strength`); every other caller
    passes the default 1.0, unchanged from before.

    `fringe_color` (LUNAR ECLIPSE OPTION C, owner sealed 2026-07-18): an
    optional thin RING of a second color layered at the OUTER edge of
    the glow — the ozone-band turquoise at the umbra's rim during
    totality — three extra gradient stops (transparent -> peak ->
    transparent) straddling `ECLIPSE_LUNAR_FRINGE_STOP`, added AFTER the
    mid stop and BEFORE the fully-transparent edge so it reads as a
    separate ring rather than a blend with the bronze core. None for
    every other caller, unchanged."""
    halo = marker_radius * defaults.GLOW_RADIUS_SCALE
    gradient = QRadialGradient(pos, halo)
    core = QColor(color)
    core.setAlphaF(defaults.GLOW_CORE_ALPHA * strength)
    mid = QColor(color)
    mid.setAlphaF(defaults.GLOW_MID_ALPHA * strength)
    edge = QColor(color)
    edge.setAlphaF(0.0)
    gradient.setColorAt(0.0, core)
    gradient.setColorAt(defaults.GLOW_MID_STOP, mid)
    if fringe_color is not None:
        fringe_transparent = QColor(fringe_color)
        fringe_transparent.setAlphaF(0.0)
        fringe_peak = QColor(fringe_color)
        fringe_peak.setAlphaF(defaults.ECLIPSE_LUNAR_FRINGE_ALPHA * strength)
        stop = defaults.ECLIPSE_LUNAR_FRINGE_STOP
        half_width = defaults.ECLIPSE_LUNAR_FRINGE_HALF_WIDTH
        gradient.setColorAt(stop - half_width, fringe_transparent)
        gradient.setColorAt(stop, fringe_peak)
        gradient.setColorAt(stop + half_width, fringe_transparent)
    gradient.setColorAt(1.0, edge)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawEllipse(pos, halo, halo)
    painter.restore()


def eclipse_glow_strength(magnitude: float | None) -> float:
    """Glow intensity (0..1 fraction of the normal alpha) scaled by the
    catalog MAGNITUDE (owner idea, ROADMAP 15h item 11): clamped to
    `ECLIPSE_MAGNITUDE_MIN/MAX`, linearly mapped to
    `ECLIPSE_GLOW_STRENGTH_MIN/MAX`. `magnitude` is None only for a
    malformed catalog row — the schema always writes it, so a None
    here reads as the strongest glow rather than guessing (Rule #7:
    no defensive branch for a scenario the schema does not produce)."""
    if magnitude is None:
        return defaults.ECLIPSE_GLOW_STRENGTH_MAX
    lo, hi = defaults.ECLIPSE_MAGNITUDE_MIN, defaults.ECLIPSE_MAGNITUDE_MAX
    fraction = max(0.0, min(1.0, (magnitude - lo) / (hi - lo)))
    lo_strength = defaults.ECLIPSE_GLOW_STRENGTH_MIN
    hi_strength = defaults.ECLIPSE_GLOW_STRENGTH_MAX
    return lo_strength + fraction * (hi_strength - lo_strength)


def eclipse_render_state(event) -> str:
    """The catalog (kind, type) -> render STATE lookup (owner decree
    2026-07-19, fix round C — `defaults.ECLIPSE_TYPE_STATE`). An
    unknown/missing type (should not occur — see the config comment)
    documented-falls-back to the kind's PARTIAL state rather than
    raising, since a malformed catalog row must still render something
    plausible (Rule #1: visible degradation, not a crash)."""
    state = defaults.ECLIPSE_TYPE_STATE.get((event.kind, event.type))
    if state is not None:
        return state
    return defaults.ECLIPSE_STATE_FALLBACK[event.kind]


def eclipse_state_glow_strength(state: str, magnitude: float | None) -> float:
    """Glow strength for an eclipse render STATE: every state carries a
    fixed TYPE-driven fraction (`defaults.ECLIPSE_STATE_GLOW_STRENGTH`)
    EXCEPT "solar_partial", the owner's one named exception, which keeps
    the original magnitude-linear mapping (`eclipse_glow_strength`)."""
    if state == "solar_partial":
        return eclipse_glow_strength(magnitude)
    return defaults.ECLIPSE_STATE_GLOW_STRENGTH[state]


def hover_factor(ctx: "RenderContext", element: str) -> float:
    """The hover-enlarge multiplier when `element` is under the cursor
    (owner EXTRAS: one shared factor for every element), else 1.0."""
    return ctx.skin.hover_enlarge if ctx.hovered == element else 1.0


def visible_occupant(occupants: tuple[str, ...], today: str) -> str:
    """Shared-slot priority (owner rule): the occupant whose weekday comes
    NEXT from today wins — and today itself always wins (distance 0)."""
    today_index = constants.SUNDAY_FIRST_INDEX[today]
    return min(
        occupants,
        key=lambda body: (constants.SUNDAY_FIRST_INDEX[body] - today_index) % 7,
    )


def today_slot_theta(skin: SkinDefinition, today: str) -> float | None:
    """Unrotated dial angle of the slot showing today's body, or None
    when today lives in the center (the hexa pointer keeps the Sun
    there). Reads the DRAWN slots (`weekday_slots` — the Genesis
    inversion moves the trio's slots with its arms)."""
    for angle, occupants in weekday_slots(skin):
        if today in occupants:
            return angle
    return None


def archetype_key(skin: SkinDefinition) -> str | None:
    """The ACTIVE archetype — the grid entry of (pointer, wheel) while
    the mode is ON and the pointer is drawn; None otherwise (mode off,
    the archetype-less Aurora/Calendar, or the Pointer element off —
    the figures ride the diamonds, no arms means no archetype)."""
    if not (skin.archetype_mode and skin.show_pointer):
        return None
    return archetypes.grid_key(skin.pointer, skin.palette_style)


def archetype_active(skin: SkinDefinition) -> bool:
    """True while the ARCHETYPE MODE overrides the dial (owner sealed
    package 2026-07-16) — the weekday model and all three slots are
    OFF for rendering and hit-testing, without touching settings."""
    return archetype_key(skin) is not None


def archetype_lit_index(
    pointer: str, hour_angle: float, rotation: float = 0.0,
    offset: float = 0.0,
) -> int:
    """The figure whose HOUR-SPACE contains the hour hand (owner
    2026-07-16): the circle divides by arms — trio 3×8h, cross 4×6h,
    hexa 6×4h, octa 8×3h — each space CENTERED on its arm (the arm tip
    is the center of its hue, the standing convention). The spaces
    ride the drawn arms, so the solar rotation shifts them exactly as
    it shifts the diamonds; index = the figures-tuple position.
    `offset` is the Genesis inversion (`arm_offset_deg`) — the trio's
    tertiary wheel counts its spaces from the 24h arm."""
    arms = constants.POINTER_POINTS[pointer]
    step = 360.0 / arms
    return int(
        round(((hour_angle - rotation - offset) % 360.0) / step)
    ) % arms


def archetype_center_lit(hour_angle: float, noon_angle: float) -> bool:
    """Whether the archetype CENTER burns FULL (owner seal 2026-07-18):
    true while the hour hand sits within
    `archetypes.ARCHETYPE_CENTER_WINDOW_DEG` of TRUE solar noon OR
    solar midnight (noon + 180). `noon_angle` is `day.star_rotation` —
    the hexagram's top vertex, the SOLAR noon angle, correct in both
    upright and rotating modes (never the drawn rotation). The circular
    distance to noon folds through the midnight mirror to give the
    distance to the noon-midnight AXIS, gated against the window."""
    dist_noon = abs(hour_angle - noon_angle) % 360.0
    dist_noon = min(dist_noon, 360.0 - dist_noon)
    dist_axis = min(dist_noon, 180.0 - dist_noon)
    return dist_axis <= archetypes.ARCHETYPE_CENTER_WINDOW_DEG


def archetype_art_size(path):
    """The pixel size of REAL archetype art (the owner's glass) — or
    None when the file is missing or a committed 1×1 placeholder (the
    WORKPLAN missing-art rule, ARCHETYPE_ART_MIN_PX). The one place the
    header is read; readiness AND the two-type classification both
    derive from it."""
    resolved = paths.art_file(path)
    if resolved is None or not resolved.exists():
        return None
    size = QImageReader(str(resolved)).size()
    if (
        not size.isValid()
        or size.width() <= archetypes.ARCHETYPE_ART_MIN_PX
        or size.height() <= archetypes.ARCHETYPE_ART_MIN_PX
    ):
        return None
    return size


def archetype_art_ready(path) -> bool:
    """Whether REAL archetype art is on disk (larger than the committed
    1×1 placeholders). While it is not, the renderer draws the figure's
    NAME instead — never a stretched pixel or a crash."""
    return archetype_art_size(path) is not None


def archetype_portrait_height(tip: float, tan_half: float) -> float:
    """The PORTRAIT figure height that exactly INSCRIBES the STANDARD
    aspect (`archetypes.ARCHETYPE_PORTRAIT_STANDARD_ASPECT`, 1:2) into
    its arm's diamond — the old `archetype_fit_height` formula (15g
    clamp era), reintroduced here for ONE purpose only: sizing the
    UNIFORM portrait at the standard aspect, never per-art (owner
    two-type law round two, 2026-07-18, fix round A 2026-07-19). The
    diamond is a rhombus centered at the romb center with along-arm
    half-diagonal tip/2 and perpendicular half-diagonal tip*tan(half)/2;
    a centered inscribed rectangle of half a×b fits iff a/p + b/q <= 1,
    so a figure of aspect `a` scaled to height h (width = a*h) fits up
    to h = tip*tan(half)/(a + tan(half)) — evaluated at the STANDARD
    aspect so a 1:2 lancet inscribes its diamond EXACTLY; art wider than
    1:2 may still overflow sideways until the owner reforces it to the
    standard (transitional, documented, not clamped)."""
    return tip * tan_half / (
        archetypes.ARCHETYPE_PORTRAIT_STANDARD_ASPECT + tan_half
    )


def archetype_figure_size(
    skin: SkinDefinition, radius: float, art_file,
) -> float:
    """THE ONE sizing entry for every archetype figure — arms AND center
    (owner two-type law, 2026-07-18 round two; height law fixed round A
    2026-07-19): the art divides into TWO TYPES by its OWN aspect ratio
    (width/height), classified once — no per-art clamp, no set-minimum.

    - CIRCLE type (aspect >= `ARCHETYPE_PORTRAIT_ASPECT_MAX` — rondels,
      medallions, the square Scale glass, and WIDE art like Saturn's
      rings) wears the SLOT size, `weekday_body_size()` — IDENTICAL to
      the weekday bodies; wide art stays height-based ON PURPOSE (owner:
      "planeta istih dimenzija kao ostale, prstenovi vire" — the ball
      matches every other circle, the rings overflow the frame,
      deliberately — no clamp).
    - PORTRAIT type (aspect < the threshold — the tall lancet vitraž
      windows: persons, temperaments) wears `archetype_portrait_height()`
      — the height inscribing the STANDARD aspect (not the art's own)
      into the diamond, UNIFORM for every portrait in the set.

    Missing/placeholder art (the name-fallback path) reads CIRCLE-sized
    — there is no art to classify."""
    size = archetype_art_size(art_file)
    if size is None or (
        size.width() / size.height() >= archetypes.ARCHETYPE_PORTRAIT_ASPECT_MAX
    ):
        return weekday_body_size(skin, radius)
    tip = radius * skin.star.radius_fraction
    # The DRAWN half-angle (the Cube look widens the family wheels'
    # arms to full rhombi — a lancet inscribes the fatter face).
    tan_half = math.tan(math.radians(arm_half_deg(skin)))
    return archetype_portrait_height(tip, tan_half)


def draw_archetype_figure(
    painter: QPainter, ctx: "RenderContext", fig: dict, pos: QPointF,
    height: float, opacity: float, named: bool, label_px: float,
) -> None:
    """One archetype figure in its diamond: the stained glass scaled
    into the arm (color visible around it) at `opacity`. `height` is
    already TYPE-CLASSIFIED (`archetype_figure_size` — circle vs
    portrait) and hover-scaled by the caller; `label_px` is the SET-
    UNIFORM label size (owner verdict 2026-07-18, ROADMAP 15h — the
    caller computed it once per paint via `archetype_label_set_px`,
    already hover-scaled). `named` adds the display name in the label
    style. Missing/placeholder art draws the NAME alone — the
    documented fallback until the owner's glass lands."""
    painter.save()
    painter.setOpacity(opacity)
    ready = archetype_art_ready(fig["file"])
    if ready:
        draw_pixmap_centered(painter, ctx, fig["file"], pos, height)
    if named or not ready:
        draw_name_label(painter, fig["name"], pos, label_px)
    painter.restore()


def name_label_px(name: str, target_width: float) -> int:
    """The measured pixel font size that fits `name` within
    `target_width`, capped at `defaults.NAME_LABEL_MAX_PX`, floored at
    `defaults.BODY_LABEL_MIN_PX` — the shared per-name fit (Rule #5):
    a SHORT text no longer inflates past a sane ceiling, a LONG one
    still shrinks to fit (measured, never guessed)."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(100)
    metrics = QFontMetricsF(font)
    width = metrics.horizontalAdvance(name)
    fitted = (
        math.floor(100.0 * target_width / width) if width > 0
        else defaults.NAME_LABEL_MAX_PX
    )
    return max(
        defaults.BODY_LABEL_MIN_PX, min(fitted, defaults.NAME_LABEL_MAX_PX)
    )


def draw_name_label(
    painter: QPainter, name: str, pos: QPointF, label_px: float,
) -> None:
    """ONE on-dial name-label draw shared by the weekday bodies and the
    archetype figures (Rule #5, ROADMAP 15h item 4): draws `name` as a
    SINGLE outlined line at `label_px` (owner REVOKED the two-line wrap
    2026-07-18 — every name is one line again). `label_px` is decided
    by the CALLER, never measured here: the SET-UNIFORM law (owner
    verdict 2026-07-18) says every name sharing a ring (a dial's
    weekday bodies, an archetype layout's figures) wears the size of
    the SMALLEST fitted member of its set — computed ONCE per paint via
    `name_label_px` over the whole set, not per label."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(round(label_px))
    draw_outlined_text(painter, pos, name, font)


def enabled_slots(skin: SkinDefinition) -> tuple[tuple[int, str], ...]:
    """The ENABLED slots in order — (index, mode) pairs. They enable
    STRICTLY 1 → 2 → 3 (owner 2026-07-14: "ne može da uključi samo
    third"). In ARCHETYPE MODE (owner 2026-07-16) the answer is EMPTY:
    the mode overrides the weekday model and all three slots at this
    one shared gate — rendering, hit-testing and layer building all
    read the slot chain through here — while the user's settings stay
    untouched, so toggling the mode back restores everything."""
    if archetype_active(skin):
        return ()
    slots = []
    if skin.show_weekday:
        slots.append((1, skin.weekday_slot))
        if skin.show_octa_slot:
            slots.append((2, skin.octa_slot))
            if skin.show_third_slot:
                slots.append((3, skin.third_slot))
    return tuple(slots)


def slot_layout(skin: SkinDefinition) -> dict:
    """The owner's SLOT POSITION MATRIX (2026-07-14), slot index →
    seat: "classic" (the full weekday unit — arms rotation, ghosts,
    center, in that slot's theme), "center", or the seat's unrotated
    dial ANGLE (seats ride the star's rotation).

    One slot: weekday = the classic unit (Trinity/Prism keep their
    center rules); anything else sits at 24h on the Trinity and the
    pinned layouts, in the CENTER elsewhere. Two slots: the Seasons
    and the Compass give the (first) weekday slot the classic unit
    and the other the center — with no weekday both flank at 3h/21h;
    the Trinity and the Prism seat the pair on the 4h/20h arms. Three
    slots: the 1st on top (the Seasons lock it to the classic unit
    instead), the 2nd on the right, the 3rd on the left."""
    slots = enabled_slots(skin)
    if not slots:
        return {}
    order = [index for index, _ in slots]
    count = len(slots)
    pinned = (
        skin.pointer in ("aurora", "calendar") or not skin.show_pointer
    )
    if pinned:
        seats = {
            1: (constants.SOUTH_SLOT_ANGLE,),
            2: (constants.AURORA_DUAL_WEEKDAY_ANGLE,
                constants.AURORA_DUAL_SLOT_ANGLE),
            3: (constants.SLOT_SEAT_TOP_ANGLE,
                constants.SLOT_SEAT_RIGHT_ARM_ANGLE,
                constants.SLOT_SEAT_LEFT_ARM_ANGLE),
        }[count]
        return dict(zip(order, seats))
    if skin.pointer in ("trio", "hexa"):
        if count == 1:
            index, mode = slots[0]
            if mode == "weekday":
                return {index: "classic"}
            return {
                index: (
                    constants.SOUTH_SLOT_ANGLE
                    if skin.pointer == "trio"
                    else "center"
                )
            }
        if count == 2:
            return {
                order[0]: constants.SLOT_SEAT_LEFT_ARM_ANGLE,
                order[1]: constants.SLOT_SEAT_RIGHT_ARM_ANGLE,
            }
        return {
            order[0]: constants.SLOT_SEAT_TOP_ANGLE,
            order[1]: constants.SLOT_SEAT_RIGHT_ARM_ANGLE,
            order[2]: constants.SLOT_SEAT_LEFT_ARM_ANGLE,
        }
    # The Seasons (cross) and the Compass (octa): the weekday unit
    # keeps priority.
    if count == 1:
        index, mode = slots[0]
        return {index: "classic" if mode == "weekday" else "center"}
    if count == 2:
        weekday_indexes = [index for index, mode in slots if mode == "weekday"]
        if weekday_indexes:
            classic = weekday_indexes[0]      # both weekday → the 1st
            other = next(index for index in order if index != classic)
            return {classic: "classic", other: "center"}
        return {
            order[0]: constants.AURORA_DUAL_WEEKDAY_ANGLE,
            order[1]: constants.AURORA_DUAL_SLOT_ANGLE,
        }
    if skin.pointer == "cross":
        # The 1st is LOCKED to the weekday unit (owner; coerced in
        # apply_display_settings) — the other two flank at 3h/21h.
        return {
            order[0]: "classic",
            order[1]: constants.AURORA_DUAL_SLOT_ANGLE,
            order[2]: constants.AURORA_DUAL_WEEKDAY_ANGLE,
        }
    return {
        order[0]: constants.SLOT_SEAT_TOP_ANGLE,
        order[1]: constants.AURORA_DUAL_SLOT_ANGLE,
        order[2]: constants.AURORA_DUAL_WEEKDAY_ANGLE,
    }


def slot_seat_rotation(skin: SkinDefinition, rotation: float) -> float:
    """Seats ride the star's rotation ONLY while the pointer is drawn
    (owner 2026-07-15: without a pointer — Aurora included — the
    positions stay on natural round angles; the tilt exists solely to
    keep seats between the diamonds)."""
    if skin.show_pointer and skin.pointer not in ("aurora", "calendar"):
        return rotation
    return 0.0


def slot_seat_scale(skin: SkinDefinition) -> float:
    """The per-pointer slot SIZE factor (owner 2026-07-15): 125% on
    the slim-armed Seasons/Compass, 150% elsewhere."""
    if not skin.show_pointer:
        return defaults.SLOT_SIZE_PINNED
    return defaults.SLOT_SIZE_BY_POINTER[skin.pointer]


def weekday_body_size(skin: SkinDefinition, radius: float) -> float:
    """ONE size for EVERY weekday body — the diamond slot bodies AND the
    hexa/trio center Sun, in the normal state and during the reveal
    window alike (owner 2026-07-18, measured on his own dial: the center
    rendered `center_scale × seat factor` (~170 px against 144 px arms)
    normally and `center_scale` alone (~114 px) during the reveal —
    three formulas for one thing; supersedes the earlier "Sun is 1.20×"
    note that `center_scale` carried). The center-only showcase keeps
    `center_scale` — it has no diamond bodies to match."""
    return (
        2 * radius * skin.weekday_set.diamond_scale * slot_seat_scale(skin)
    )


def weekday_body_orbit(skin: SkinDefinition) -> float:
    """Orbit fraction (of the dial radius) that centers the weekday-by-
    colors body in its diamond: a romb's diagonals cross at EXACTLY half
    the star tip on every pointer (tip = star.radius_fraction), so the
    by-colors body rides that radius uniformly (owner 2026-07-15 — this
    one slot always sits at the romb center, whatever the pointer; the
    seated 2nd/3rd slots keep their own arm geometry)."""
    return skin.star.radius_fraction * defaults.WEEKDAY_ROMB_CENTER_OF_TIP


def slot_seat_orbit(skin: SkinDefinition, seat) -> float:
    """The seat's orbit factor: on the slim-armed pointers an ANGLE
    seat shifts outward to the diamond's widest point (owner
    2026-07-15); the center and the pinned layouts stay put."""
    if (
        seat not in ("classic", "center")
        and skin.show_pointer
        and skin.pointer in defaults.SLOT_SEAT_OUTWARD
    ):
        return defaults.SLOT_SEAT_OUTWARD[skin.pointer]
    return 1.0


def weekday_classic_slot(skin: SkinDefinition) -> int | None:
    """Which slot drives the CLASSIC weekday unit — None when every
    enabled slot sits in a seat."""
    return next(
        (
            index for index, seat in slot_layout(skin).items()
            if seat == "classic"
        ),
        None,
    )


def slot_view(skin: SkinDefinition, index: int) -> tuple:
    """(mode, style, theme, metal, roster) of slot 1 / 2 / 3 — the
    roster is PER SLOT (owner 2026-07-15: slot 1 Greek Planetary next
    to slot 2 Greek Pantheon); the 1st slot's roster is whatever the
    weekday set was dressed in."""
    if index == 1:
        return (
            skin.weekday_slot, skin.day_slot_style,
            skin.weekday_theme, skin.weekday_set.metal,
            (
                "pantheon"
                if skin.weekday_set.body_articles is not None
                else "planetary"
            ),
        )
    if index == 2:
        return (
            skin.octa_slot, skin.info_slot_style,
            skin.info_slot_theme, skin.info_slot_metal,
            skin.info_slot_roster,
        )
    return (
        skin.third_slot, skin.third_slot_style,
        skin.third_slot_theme, skin.third_slot_metal,
        skin.third_slot_roster,
    )


def sunday_dual_face(skin: SkinDefinition) -> bool:
    """True while the SERVANT face holds its own seat on the Compass,
    the Seasons or the ROSE (owner correction 2026-07-13: NOT
    Sunday-only — it stands there all week like every other body,
    ghosted, and turns opaque on Sunday: "two persons, a union"). The
    seat itself is `servant_seat_angle` — 24h on the first two, the
    blue 06h arm on the Rose. The Trinity and the Prism keep one image
    ("two persons in one body") and speak the second face in the hover.
    Needs the CLASSIC unit up and the theme's dual art on disk
    (documented: no art, no second face). The CENTER-duality wheels of
    these pointers (the Quaternity's Seasons wheel) resolve through
    `center_dual_face` instead (owner seal 2026-07-29)."""
    spec = skin.weekday_set
    return (
        skin.pointer in ("octa", "cross", "rose")
        and not center_duality(skin)
        and weekday_classic_slot(skin) is not None
        and spec.display_mode != "center_only"
        and spec.dual_asset is not None
        and paths.art_file(spec.dual_asset).exists()
    )


def servant_holds_the_seat(skin: SkinDefinition, today: str) -> bool:
    """Whether the Servant face WINS his seat today (`servant_seat_angle`
    — 24h on the Compass/Seasons, the blue 06h arm on the Rose): on the
    Compass and the Rose the seat is his alone; on the Seasons he shares
    it with Mercury's slot and the standard shared-slot priority decides
    (the Servant counts as an eighth body whose day is Sunday)."""
    if not sunday_dual_face(skin):
        return False
    seat = next(
        (
            occupants
            for angle, occupants in weekday_slots(skin)
            if angle == servant_seat_angle(skin)
        ),
        (),
    )
    return not seat or visible_occupant(seat + ("sun",), today) == "sun"


def center_dual_face(skin: SkinDefinition) -> bool:
    """True while the Sunday duality lives in ONE CENTER image instead
    of the Compass/Seasons' two separate seats (round R3b item 3) — the
    complementary case to `sunday_dual_face`: the Prism and Trinity
    ALWAYS merge the classic unit's Sun into the center (their own
    docstring above: "keep one image... speak the second face in the
    hover"), and `center_only` mode merges it for EVERY pointer (there
    are no slot seats to hold a second face there). Given a dual asset
    exists, a theme's Sunday resolves through EXACTLY one of these two
    laws — never both, never neither."""
    spec = skin.weekday_set
    if weekday_classic_slot(skin) is None:
        return False
    if spec.dual_asset is None or not paths.art_file(spec.dual_asset).exists():
        return False
    if spec.display_mode == "center_only":
        return True
    return center_duality(skin)


def center_seat_body_key(skin: SkinDefinition, today: str) -> str | None:
    """The weekday-body KEY occupying the classic unit's CENTER seat on
    this skin, or None where no such seat exists — "sun" for the
    Prism/Trinity hexa/trio layouts (the ONLY body ever drawn there —
    `WeekdayLayer` seats every other body on an arm), `today` for the
    center_only showcase (its one and only seat, no arms at all). Both
    `CenterBodyLayer` and the compositor's hover read this to resolve
    the ordinary Sunday dual/Ninth face — independent of whether the
    theme carries a Ruler/Servant duality at all (`center_dual_face`
    additionally requires a `dual_asset`, which this key does not)."""
    if weekday_classic_slot(skin) is None:
        return None
    if skin.weekday_set.display_mode == "center_only":
        return today
    if center_duality(skin):
        return "sun"
    return None


def thirteenth_plate(key: str) -> tuple[str, Path | None]:
    """(display name, resolved asset path or None) of the Blue Moon
    Law's 13th `key` (one of `constants.THIRTEENTHS`) — mirrors
    `theme_ninth`'s graceful-absent contract (Rule #5): the caller draws
    the name-only fallback when the path is None. Ophiuchus/The Cat
    resolve through the SAME zodiac/chinese registers every sign/animal
    already uses (the "sign"/"primary" looks, matching the Encyclopedia
    ninth-entry icon exactly); Sol/Modrenik read the sourceless
    MONTHS_ART_DIR, exactly like the twelve Slavic months (graceful-
    absent until the owner's prompt sheet lands).

    THE AXLE LAW's ALWAYS-CENTERS (Hestia/Jesus/Prudence/Cunning/Peace/
    Hardness of Heart, CANON §The Axle) resolve through the SAME
    `art_dir` as their OWN roster's twelve rim members — every prompt
    sheet drops the axle's plate in that one folder beside them, so
    there is no second art-dir table to keep in sync (Rule #19). The ONE
    registered `defaults.CalendarMount` whose own `centre` names this
    key supplies it; every art_dir may legitimately be missing that one
    extra file (art landed for the twelve rim members well ahead of the
    axle's own plate on every one of the four older Dozens, and the
    Sins Dozen has no art at all yet), same graceful-absent contract as
    everything else here. The axle's STEM follows the one no-space rule
    `CalendarMount.art_stems` already applies to its rim members
    (`Just_Indignation`): a filename cannot carry a space, so
    "Hardness of Heart" drops as `Hardness_of_Heart.png` — one rule, no
    second table (Rule #19); single-word axles are unaffected."""
    name, _family, _article = constants.THIRTEENTHS[key]
    if key == "ophiuchus":
        art = octa_slot_art("zodiac/astrology/primary/sign", name)
    elif key == "chinese":
        art = octa_slot_art("zodiac/chinese/primary/bronze", "Cat")
    elif key in ("sol", "modrenik"):
        resolved = paths.art_file(defaults.MONTHS_ART_DIR / f"{name}.png")
        art = resolved if resolved.exists() else None
    else:
        mount = next(
            m for m in defaults.CALENDAR_MOUNTS.values() if m.centre == key
        )
        art = octa_slot_art(mount.art_dir, name.replace(" ", "_"))
    return name, art


def active_thirteenth(skin: SkinDefinition, day: DayContext) -> str | None:
    """THE BLUE MOON LAW's CORRECTED resolution (owner overrule,
    retiring R12's global "any pointer, any theme" law — its own
    screenshot caught Ophiuchus on the hexa pointer with the Greek
    theme). A 13th ever claims the dial CENTER ONLY on the Calendar
    pointer (`skin.pointer == "calendar"`), in the ONE mode that owns
    it; every other pointer's ordinary center laws (the Sunday dual/
    Ninth windows) reign untouched, unconditionally — this function
    returns None before even looking at `day`.

    `day.thirteenth_candidates` (`core.blue_moon.thirteenth_candidates`,
    computed once a day) is an unordered FACT SET — resolving it to the
    Calendar pointer's OWN showing member reads the ACTIVE settings
    shape, never a date-only "which is more real" tiebreak (that R12
    notion is retired with the precedence machinery itself):

    - A MOUNT that names a thirteenth of its own
      (`defaults.CalendarMount.centre`) OUTRANKS the wheel whenever both
      are active at once — a mount is a more deliberate SECOND choice
      layered on top of the wheel (owner-documented tiebreak,
      ground-truthed against the settings model: `calendar_mount` is
      fully independent of `palette_style`, so both CAN be active
      together, e.g. the zodiac wheel with the chinese mount).
    - A mount that names NONE and the "off" case both fall through to
      the WHEEL (`calendar_wheel`, palette_style-picked): the zodiac
      wheel claims Ophiuchus, the almanac wheel claims Sol. Every roster
      registered today names a centre (the Emotions Dozen's is PEACE,
      sealed 2026-07-29 — CANON §The Axle), so this branch currently
      fires only for "off"; it stays live for a future roster that seals
      no centre — the Sins Dozen was the last candidate and it was
      sealed WITH its axle (Hardness of Heart) on 2026-07-29, so the
      branch is exercised by a synthetic mount in the tests.

    Whether the claimed member actually SHOWS is still its own
    appearance rule's business — `day.thirteenth_candidates` holds the
    calendar-driven members only on their own trigger+window (so on
    almost every day of the year one of THOSE returns None), but holds
    the ALWAYS-CENTERS (`constants.AXLE_ALWAYS_CENTERS`)
    UNCONDITIONALLY (CANON §The Axle: "ALWAYS-CENTERS stand on EVERY
    date") — so a mount whose `centre` is an axle (Hestia/Jesus/
    Prudence/Cunning/Peace/Hardness of Heart) shows it on literally
    every date, never gated by a window at all."""
    if skin.pointer != "calendar":
        return None
    candidates = day.thirteenth_candidates
    mount = defaults.CALENDAR_MOUNTS.get(skin.calendar_mount)
    key = mount.centre if mount is not None and mount.centre else (
        "ophiuchus" if calendar_wheel(skin) == "zodiac" else "sol"
    )
    return key if key in candidates else None


def ninth_table_for(theme: str, active_alt: bool) -> dict | None:
    """Which ALT-NINTH TABLE `theme_ninth` consults, or None to keep the
    canonical `constants.WEEKDAY_THEME_NINTHS` entry — THE MECHANISM
    DISPATCH itself (owner Double-Ninth verdicts, 2026-07-29), extracted
    so the WIRING is directly testable without needing a plate to exist
    on disk (`tests/test_weekday_rotation.py`'s art-free pins). Reads
    `constants.NINTH_MECHANISMS`:

    - "easter_egg"  -> `constants.WEEKDAY_THEME_NINTH_EASTER_EGG`
      (continents' Pangea).
    - "daynight"    -> `constants.WEEKDAY_THEME_NINTH_NIGHT` (sw_dyad's
      Exegol).
    - "term_weekly" -> None always: cp_corpo's weekly mandate reads NO
      alt table — the canonical entry's OWN seat roster already names
      both halves, and `on_date` alone (via `rotating_art_file`'s cadence
      override) picks between them (Rule #5, one rotation mechanism).
    - no mechanism, or `active_alt` False -> None (the plain canonical
      plate, unconditionally)."""
    if not active_alt:
        return None
    mechanism = constants.NINTH_MECHANISMS.get(theme)
    if mechanism == "easter_egg":
        return constants.WEEKDAY_THEME_NINTH_EASTER_EGG
    if mechanism == "daynight":
        return constants.WEEKDAY_THEME_NINTH_NIGHT
    return None


def theme_ninth(
    theme: str, active_alt: bool = False, on_date: date | None = None,
) -> tuple[str, Path] | None:
    """(display name, resolved asset path) of `theme`'s Ninth plate, or
    None when the theme names no Ninth (`constants.WEEKDAY_THEME_NINTHS`)
    or its plate has not landed on disk yet — the ONE existence-gated
    lookup `CenterBodyLayer` (paint) and the compositor's hover share
    (Rule #5), matching the graceful-absent law every other Ninth plate
    already follows.

    `active_alt` is the DOUBLE NINTH's alt-face switch (owner Double-
    Ninth verdicts, 2026-07-29 — was `pangea`, continents-only, before
    the law generalized): when True, `ninth_table_for` resolves WHICH
    alt table (if any) `theme`'s own `NINTH_MECHANISMS` entry names —
    continents' Pangea, sw_dyad's Exegol — same graceful-absent gate,
    its own alt plate. cp_corpo's "term_weekly" mechanism never reaches
    an alt table (see `ninth_table_for`); its rotation rides `on_date`
    alone, like every other seat roster.

    `on_date` opts the resolved plate into THE UNIVERSAL ROTATION
    CONVENTION (weekday ALT ROTATION round 2026-07-20/21 — bible_dark's
    Ninth Circle is the first Ninth to ship `alt/` siblings, cp_corpo's
    weekly mandate the first to ride a WEEKLY cadence instead of daily);
    None (every caller before this round) keeps the plain canonical
    file."""
    table = ninth_table_for(theme, active_alt)
    entry = table.get(theme) if table is not None else None
    if entry is None:
        entry = constants.WEEKDAY_THEME_NINTHS.get(theme)
    if entry is None:
        return None
    name, rel = entry
    asset = defaults.weekday_art(rel)
    if not paths.art_file(asset).exists():
        return None
    if on_date is not None:
        asset = defaults.rotating_art_file(asset, on_date) or asset
    return name, asset


def ninth_alt_active(ctx: RenderContext) -> bool:
    """Whether `ctx.skin.weekday_theme`'s Ninth shows its ALT face right
    now — THE MECHANISM DISPATCH the paint pass reads (owner Double-
    Ninth verdicts, 2026-07-29), replacing the old `weekday_theme ==
    "continents"` gate the two `theme_ninth` call sites below used to
    repeat (Rule #5 — one dispatch, not a copy per call site):

    - "easter_egg" reads `core.continents`'s sky law from the day's OWN
      pre-built anchors and the live eclipse flag (never recomputed).
    - "daynight" reads the SAME `TickState.is_daylight` `center_face`
      already reads — night is the alt face.
    - every other mechanism (or none) answers False; `theme_ninth` then
      falls back to the canonical plate, rotated by `on_date` alone."""
    mechanism = constants.NINTH_MECHANISMS.get(ctx.skin.weekday_theme)
    if mechanism == "easter_egg":
        return continents.ninth_is_pangea_from_events(
            ctx.day.local_date, ctx.day.season_events, ctx.day.moon_events,
            ctx.tick.eclipse_event is not None,
        )
    if mechanism == "daynight":
        return not ctx.tick.is_daylight
    return False


def ninth_window_anchor(day: DayContext, tick: TickState) -> str | None:
    """Which SOLAR anchor's ±`constants.CENTER_WINDOW_HOURS` window the
    hour hand stands in right now — "noon", "midnight", or None outside
    both. SOLAR, not wall-clock: `day.sun.noon` is the SAME anchor the
    hexagram's own rotation reads (`star_rotation_deg`) — reused via
    `angles.hours_between`, never a parallel clock (Rule #5/#6)."""
    noon_angle = angles.time_to_dial_angle(day.sun.noon)
    if (
        abs(angles.hours_between(tick.hour_angle, noon_angle))
        <= constants.CENTER_WINDOW_HOURS
    ):
        return "noon"
    midnight_angle = (noon_angle + 180.0) % 360.0
    if (
        abs(angles.hours_between(tick.hour_angle, midnight_angle))
        <= constants.CENTER_WINDOW_HOURS
    ):
        return "midnight"
    return None


def center_face(day: DayContext, tick: TickState, has_ninth: bool) -> str:
    """Which face the CENTER seat's Sunday duality shows RIGHT NOW
    (owner seal 2026-07-29, superseding INSTRUCTION #5's shape): the sky
    itself decides — DAYLIGHT the "ruler" (GOOD), NIGHT the "servant"
    (EVIL) — and a theme that names a Ninth shows "ninth" in BOTH solar
    windows (11:30-12:30 and 23:30-00:30 solar, `ninth_window_anchor`).
    Themes with no Ninth ignore the windows: day Ruler, night Servant,
    nothing else."""
    if has_ninth and ninth_window_anchor(day, tick) is not None:
        return "ninth"
    return "ruler" if tick.is_daylight else "servant"


def dual_seat_ninth(day: DayContext, tick: TickState) -> str | None:
    """Which SEAT the Ninth's badge takes over RIGHT NOW on a TWO-BADGE
    Sunday (owner seal 2026-07-29 — the rule the center windows always
    had, extended to the 12h/24h and 06h/18h displays): near solar NOON
    he replaces the "servant" (and stands beside the Ruler), near solar
    MIDNIGHT the "ruler" (and stands beside the Servant); None outside
    the windows. Callers gate on Sunday, `sunday_dual_face` and a theme
    that actually names a Ninth."""
    anchor = ninth_window_anchor(day, tick)
    if anchor == "noon":
        return "servant"
    if anchor == "midnight":
        return "ruler"
    return None


def pie_path(radius: float, start_deg: float, end_deg: float) -> QPainterPath:
    """Clip path for the pie between two dial angles going clockwise."""
    path = QPainterPath()
    path.moveTo(0.0, 0.0)
    rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
    path.arcTo(rect, 90.0 - start_deg, -(end_deg - start_deg))
    path.closeSubpath()
    return path


# --- THE DRAWN WHEEL (Pointers REWORK phase 1, owner sheet 2026-07-29) -------
# One arm is one PATH. Which path — a star diamond or a polygon face —
# is the only difference between the two shapes; the palette, the wheel
# offsets, the rotation, the day/night law and the borders are shared
# code below (Rule #5).


def wheel_rotation(skin: SkinDefinition, rotation: float) -> float:
    """The rotation the drawn wheel rides: the solar offset — except on
    the CALENDAR, whose figure stands on the wedges it colors and is
    therefore calendar-FIXED like the wedges themselves (owner spec)."""
    return 0.0 if skin.pointer == "calendar" else rotation


def drawn_arms(
    skin: SkinDefinition, colors: tuple
) -> tuple[tuple[tuple[float, str], ...], ...]:
    """The whole drawn wheel as (angle, hue) arms grouped into PASSES in
    z-order — the bottom of the stack first, the topmost last. One loop
    draws every pointer and both shapes (Rule #5):

    ```
    offset = arm_offset_deg(skin)                # the wheel's own turn
    IF pointer is CALENDAR:
        centres = centre of each of the twelve wedges of the ACTIVE wheel
        IF shape is polygon → ONE pass: all twelve, hue i on wedge i
        ELSE                → TWO passes: the ODD wedges' hexagram first,
                              the EVEN one painted over it
    ELSE:
        stars = rose_star_offsets(skin) OR (0,)  # the Rose's three
        arm k of star s sits at offset + s + k * 360/len(colors)
        IF shape is polygon on the ROSE → ONE pass of all 24 rays
                              (they touch instead of overlapping, so
                              there is no z-stack left to order)
        ELSE                → one pass per star, in the table's order
    ```
    """
    offset = arm_offset_deg(skin)
    if skin.pointer == "calendar":
        centers = [
            offset + (start + end) / 2.0
            for start, end in calendar_wedge_bounds(calendar_wheel(skin))
        ]
        if polygon_shape(skin):
            return (tuple((centers[i], colors[i]) for i in range(len(centers))),)
        # TWO HEXAGRAMS 30° apart (owner sheet): the star standing on the
        # EVEN wedge centers is painted last, so it reads over the other.
        return tuple(
            tuple(
                (centers[i], colors[i])
                for i in range(parity, len(centers), 2)
            )
            for parity in (1, 0)
        )
    span = 360.0 / len(colors)
    stars = rose_star_offsets(skin) or (0.0,)
    arms = tuple(
        tuple(
            (offset + star + k * span, color)
            for k, color in enumerate(colors)
        )
        for star in stars
    )
    if polygon_shape(skin) and len(stars) > 1:
        return (tuple(arm for star_arms in arms for arm in star_arms),)
    return arms


def aura_wedge_bounds(
    skin: SkinDefinition, palette: tuple
) -> list[tuple[float, float]]:
    """THE BACKGROUND FOLLOWS THE STAR (owner's correction round
    2026-07-29) — the (start, end) dial angles of every hue's Aura
    wedge, hue index 0 first. ONE law: a wedge is anchored on its own
    hue's LEAD RAY, and how it sits on that ray is the pointer's
    per-wheel anchor.

    ```
    span  = 360 / number of hues
    lead  = arm_offset_deg(skin) + hue index * span   # the hue's own ray
    low, high = aura_wedge_anchor(skin)               # in spans
    wedge = (lead + low * span, lead + high * span)
    ```

    On every one-star pointer the lead ray IS the arm and the anchor is
    (−½, +½) — the standing arm-centered wedge. On the ROSE, whose eight
    hues each wear three rays, the owner's own numbers apply: LEGACY's
    wedge trails its lead ray (hue 0: 9h -> 12h, boundaries ON the
    lead-ray hours), PROPHECY's stands centered on it (hue 0: 10:30 ->
    13:30). Every wedge still tiles the circle exactly — adjacent wedges
    share a boundary, none overlaps."""
    span = 360.0 / len(palette)
    offset = arm_offset_deg(skin)
    low, high = aura_wedge_anchor(skin)
    return [
        (offset + index * span + low * span, offset + index * span + high * span)
        for index in range(len(palette))
    ]


def star_inner_radius(skin: SkinDefinition, tip: float) -> float:
    """Where the pointer's OWN star seats its inner vertices —
    `tip / (2·cos(half))`, the regular-star value (tip/√3 for the
    hexagram). It is both the star diamond's own side vertex and the
    radius a polygon's edge midpoint is pulled to at full curvature, so
    the two shapes meet there (Rule #5)."""
    half = constants.POINTER_ARM_HALF_ANGLE_DEG[skin.pointer]
    return tip / (2.0 * math.cos(math.radians(half)))


def polygon_curvature(skin: SkinDefinition) -> float:
    """The edge pull actually applied: the reader's slider on a TRUE
    polygon (trio/cross/hexa/octa), 0 everywhere else — the Calendar's
    and the Rose's polygons are stars, and a star never curves (owner
    spec). One gate, so the stored value stays untouched on the shapes
    that ignore it."""
    return skin.polygon_curvature if polygon_faces(skin) else 0.0


def polygon_boundary_radius(skin: SkinDefinition, tip: float) -> float:
    """The radius of a polygon face's two COLOR-BOUNDARY corners.

    On the plain N-gon that corner IS the outer edge's midpoint, so it
    sits on the apothem `tip·cos(180/N)` — and travels inward with the
    curvature exactly as the edge does. The TRINITY's CUBE is the
    owner's exception: its boundary corners are hexagon VERTICES at the
    full tip (three rhombi, six vertices), and the curvature bites into
    the six edges BETWEEN them instead."""
    if skin.pointer == "trio":
        return tip
    apothem = tip * math.cos(math.radians(arm_half_deg(skin)))
    return apothem + polygon_curvature(skin) * (
        star_inner_radius(skin, tip) - apothem
    )


def _pulled_midpoint(
    skin: SkinDefinition, a: QPointF, b: QPointF, tip: float
) -> QPointF:
    """One outer edge's midpoint pulled INWARD along its own radius:
    the chord midpoint at curvature 0 (a straight edge), the star's own
    inner radius at 1. The angle never moves — only the distance."""
    mid = QPointF((a.x() + b.x()) / 2.0, (a.y() + b.y()) / 2.0)
    length = math.hypot(mid.x(), mid.y())
    target = star_inner_radius(skin, tip)
    return mid * ((length + polygon_curvature(skin) * (target - length)) / length)


def _append_edge(
    path: QPainterPath, edge_mode: str, a: QPointF, b: QPointF,
    mid: QPointF, part: str,
) -> None:
    """Append the outer edge a→b, bent through its pulled `mid`, to a
    path already standing at the piece's start point. `part` is "full"
    (the whole edge), "first" (a→mid) or "second" (mid→b) — a polygon
    FACE owns half of each of its two edges, the cube's rhombus owns
    both of its edges whole.

    "notched" draws the two straight segments meeting at `mid`;
    "smooth" draws the quadratic whose CURVE passes through `mid`
    (control = 2·mid − chord midpoint), split at t=0.5 by de Casteljau
    when only half of it is wanted. At curvature 0 `mid` is the chord
    midpoint itself, the control collapses onto the chord and both
    modes draw the plain straight edge."""
    if edge_mode == "notched":
        if part in ("full", "first"):
            path.lineTo(mid)
        if part in ("full", "second"):
            path.lineTo(b)
        return
    chord = QPointF((a.x() + b.x()) / 2.0, (a.y() + b.y()) / 2.0)
    control = mid * 2.0 - chord
    if part == "full":
        path.quadTo(control, b)
    elif part == "first":
        path.quadTo((a + control) / 2.0, mid)
    else:
        path.quadTo((control + b) / 2.0, b)


def star_diamond_path(
    skin: SkinDefinition, tip: float, theta: float
) -> QPainterPath:
    """One star arm: the diamond from the center out to `theta`, its
    side vertices at `arm_half_deg` either side on the star radius."""
    half = arm_half_deg(skin)
    inner = tip / (2.0 * math.cos(math.radians(half)))
    path = QPainterPath()
    path.moveTo(0.0, 0.0)
    path.lineTo(dial_point(theta - half, inner))
    path.lineTo(dial_point(theta, tip))
    path.lineTo(dial_point(theta + half, inner))
    path.closeSubpath()
    return path


def polygon_face_path(
    skin: SkinDefinition, tip: float, theta: float
) -> QPainterPath:
    """One polygon FACE: the kite from the center out to the polygon's
    vertex at `theta`, widening between the two color boundaries at
    `theta ± 180/N`. Straight-edged at curvature 0 it is literally the
    polygon's own slice.

    ```
    half = 180 / drawn arm count
    IF pointer is TRINITY (the CUBE):
        the face is a RHOMBUS of the hexagon — its boundary corners are
        hexagon VERTICES at the tip radius, and it owns TWO WHOLE
        hexagon edges (boundary → vertex → boundary)
    ELSE:
        the face owns HALF of each of the two polygon edges meeting at
        its vertex; its boundary corners ARE those edges' midpoints and
        travel inward with the curvature
    ```
    """
    half = arm_half_deg(skin)
    # With NO pull the two forms are the same straight edge — drawn as
    # segments, so the plain polygon really is a polygon of straight
    # lines rather than a curve that happens to be flat.
    edge_mode = skin.polygon_edge if polygon_curvature(skin) else "notched"
    boundary = polygon_boundary_radius(skin, tip)
    vertex = dial_point(theta, tip)
    before = dial_point(theta - half, boundary)
    after = dial_point(theta + half, boundary)
    path = QPainterPath()
    path.moveTo(0.0, 0.0)
    path.lineTo(before)
    if skin.pointer == "trio":
        _append_edge(
            path, edge_mode, before, vertex,
            _pulled_midpoint(skin, before, vertex, tip), "full",
        )
        _append_edge(
            path, edge_mode, vertex, after,
            _pulled_midpoint(skin, vertex, after, tip), "full",
        )
    else:
        # The boundary corner IS the pulled midpoint of the edge it
        # halves — `polygon_boundary_radius` and `_pulled_midpoint`
        # agree there by construction.
        _append_edge(
            path, edge_mode, dial_point(theta - 2.0 * half, tip), vertex,
            before, "second",
        )
        _append_edge(
            path, edge_mode, vertex, dial_point(theta + 2.0 * half, tip),
            after, "first",
        )
    path.closeSubpath()
    return path


def arm_shape_path(
    skin: SkinDefinition, tip: float, theta: float
) -> QPainterPath:
    """THE ONE arm-geometry entry (Rule #5): the polygon face where the
    reader asked for a true polygon, the star diamond everywhere else —
    including the Calendar's and the Rose's polygons, which are stars
    with touching arms."""
    if polygon_faces(skin):
        return polygon_face_path(skin, tip, theta)
    return star_diamond_path(skin, tip, theta)


def lit_regions(sun: SunDay, spec) -> list[tuple[float, float, float]]:
    """(start, end_unwrapped, hue_alpha) arcs of the SUNLIT part of the day
    in wall-clock dial space — full alpha between sunrise and sunset, the
    twilight alpha over the dawn/dusk bands, nothing at night (the fixed
    gray base shows through). On transitional high-latitude days a
    boundary can be missing even in NORMAL/WHITE_NIGHTS regimes — each
    missing boundary coalesces to its neighbor (the band collapses to zero
    width and is dropped) instead of crashing mid-paint."""

    def arc(a: float, b: float, alpha: float) -> tuple[float, float, float]:
        return (a, b if b > a else b + 360.0, alpha)

    angle = angles.time_to_dial_angle
    regime = sun.regime
    if regime is DaylightRegime.NORMAL:
        rise = angle(sun.sunrise) if sun.sunrise else angle(sun.dawn)
        sets = angle(sun.sunset) if sun.sunset else angle(sun.dusk)
        dawn = angle(sun.dawn) if sun.dawn else rise
        dusk = angle(sun.dusk) if sun.dusk else sets
        regions = [
            arc(dawn, rise, spec.twilight_alpha),
            arc(rise, sets, spec.day_alpha),
            arc(sets, dusk, spec.twilight_alpha),
        ]
        return [region for region in regions if region[0] != region[1]]
    if regime is DaylightRegime.WHITE_NIGHTS:
        if sun.sunrise is None or sun.sunset is None:
            # One-sided transition into/out of polar day: the sun is up
            # nearly the whole day.
            return [(0.0, 360.0, spec.day_alpha)]
        return [
            arc(angle(sun.sunrise), angle(sun.sunset), spec.day_alpha),
            arc(angle(sun.sunset), angle(sun.sunrise), spec.twilight_alpha),
        ]
    if regime is DaylightRegime.TWILIGHT_ONLY:
        if sun.dawn is not None and sun.dusk is not None:
            return [arc(angle(sun.dawn), angle(sun.dusk), spec.twilight_alpha)]
        return [(0.0, 360.0, spec.twilight_alpha)]
    if regime is DaylightRegime.POLAR_DAY:
        return [(0.0, 360.0, spec.day_alpha)]
    return []                                            # POLAR_NIGHT


def border_clips(
    skin: SkinDefinition, sun: SunDay
) -> tuple[tuple[float, float] | None, ...]:
    """Where the drawn wheel's OUTLINE strokes are allowed (owner option
    2026-07-29, `Settings.hide_night_borders`): `(None,)` — the whole
    circle, no clip — is the standing law, and stays the answer whenever
    the daylight law itself is off (the Calendar's and the Rose's
    switch: with the wheel in flat full color EVERYTHING counts as lit).
    With the option on, the SUNLIT arcs alone: the night keeps its fills
    exactly as before but loses the border mesh — on the Rose, where 24
    overlapping rays each carry a lead line, that mesh is what the
    reader sees at night instead of the wheel. Polar night lights
    nothing, so nothing is stroked."""
    if not skin.hide_night_borders or not daylight_active(skin):
        return (None,)
    return tuple(
        (start, end) for start, end, _alpha in lit_regions(sun, skin.star)
    )


def aurora_bands(
    sun: SunDay, palette: tuple, day_alpha: float
) -> tuple[list[tuple[float, float, str, float]], bool]:
    """The AURORA pointer's color bands (owner spec 2026-07-12): the
    five DAY hues spread EVENLY across the actual sunrise-sunset arc —
    every hue visible on the shortest and the longest day alike — with
    the dawn band in the palette's FIRST hue (left, blue) and the dusk
    band in its LAST (right, brown). The twilight bands have NO
    separate opacity (owner: the dedicated dawn/dusk COLORS carry the
    meaning) — everything follows the daylight alpha. Returns (bands,
    solar_frame): bands are (start, end_unwrapped, hue, alpha) in
    wall-clock dial space; solar_frame=True marks the boundary-less
    regimes (polar day, one-sided white nights, boundary-less
    twilight-only) whose bands run midnight-to-midnight in the SOLAR
    frame — the caller rotates them with the star."""
    dawn_hue, day_hues, dusk_hue = palette[0], palette[1:-1], palette[-1]
    twilight_alpha = day_alpha           # one opacity for the whole arc

    def arc(a: float, b: float) -> tuple[float, float]:
        return a, b if b > a else b + 360.0

    def spread(a: float, b: float, alpha: float) -> list:
        step = (b - a) / len(day_hues)
        return [
            (a + k * step, a + (k + 1) * step, hue, alpha)
            for k, hue in enumerate(day_hues)
        ]

    angle = angles.time_to_dial_angle
    regime = sun.regime
    if regime is DaylightRegime.NORMAL:
        rise = angle(sun.sunrise) if sun.sunrise else angle(sun.dawn)
        sets = angle(sun.sunset) if sun.sunset else angle(sun.dusk)
        dawn = angle(sun.dawn) if sun.dawn else rise
        dusk = angle(sun.dusk) if sun.dusk else sets
        bands = []
        if dawn != rise:
            bands.append((*arc(dawn, rise), dawn_hue, twilight_alpha))
        bands.extend(spread(*arc(rise, sets), day_alpha))
        if sets != dusk:
            bands.append((*arc(sets, dusk), dusk_hue, twilight_alpha))
        return bands, False
    if regime is DaylightRegime.WHITE_NIGHTS:
        if sun.sunrise is None or sun.sunset is None:
            return spread(180.0, 540.0, day_alpha), True
        rise, sets = angle(sun.sunrise), angle(sun.sunset)
        bands = spread(*arc(rise, sets), day_alpha)
        night_a, night_b = arc(sets, rise)
        middle = (night_a + night_b) / 2.0
        # The bright night: dusk brown into the sunset half, dawn blue
        # out of the sunrise half.
        bands.append((night_a, middle, dusk_hue, twilight_alpha))
        bands.append((middle, night_b, dawn_hue, twilight_alpha))
        return bands, False
    if regime is DaylightRegime.TWILIGHT_ONLY:
        if sun.dawn is not None and sun.dusk is not None:
            return (
                spread(*arc(angle(sun.dawn), angle(sun.dusk)), twilight_alpha),
                False,
            )
        return spread(180.0, 540.0, twilight_alpha), True
    if regime is DaylightRegime.POLAR_DAY:
        return spread(180.0, 540.0, day_alpha), True
    return [], False                                     # POLAR_NIGHT


class Layer(ABC):
    cadence: Cadence
    # HOVER-VARIABLE layers (owner 2026-07-17, ROADMAP 15f): even though
    # their content is DAILY, their APPEARANCE changes with the hover-
    # enlarge target and the reveal window, so the compositor NEVER bakes
    # them into the cached composite — it draws them LIVE every frame
    # (their pixmaps are already rasterize-cached). A hover enter/leave or
    # an Omega reveal then rebuilds NOTHING. The WeekdayLayer and the
    # ArchetypeLayer set this True.
    hover_variable: bool = False

    def __init__(self, skin: SkinDefinition, lift: bool = False):
        self._skin = skin
        # The hover Z-LIFT (owner 2026-07-13): the enlarged element must
        # ride ABOVE the hands. A base layer (lift=False) skips its
        # hovered element; HoverLiftLayer owns lift=True twins that
        # draw ONLY it, stacked last.
        self._lift = lift

    def _gate(self, ctx: "RenderContext", element: str) -> bool:
        """True when THIS pass draws `element`: the base pass draws all
        but the hovered one, the lift pass only the hovered one."""
        return (ctx.hovered == element) == self._lift

    @abstractmethod
    def paint(self, painter: QPainter, ctx: RenderContext) -> None: ...


class BackgroundLayer(Layer):
    """The UMBRA (gray brightness wheel) and the AURA (transparent hue
    wedges over the sunlit part of the day); both rotate with the star
    — or stand upright when solar rotation is off.

    THE DAYLIGHT SWITCH REACHES HERE (owner correction 2026-07-29): with
    `daylight_active(skin)` False — only ever the Calendar and the Rose
    — day and night vanish from the WHOLE dial, not just the star:

    ```
    IF the daylight law runs:
        Umbra = the brightness wheel, lightest on solar noon
        Aura  = the hues inside the lit arcs only, night stays gray
    ELSE:                                # flat noon everywhere
        Umbra = ONE full circle in the contrast span's LIGHTEST shade
        Aura  = full colour over the WHOLE circle at the day alpha
    ```

    The FIGURE faces (the Sunday Ruler/Servant, the Earth's day/night
    face, `center_face`) keep reading the real sun — the switch flattens
    the DISK COLOURING alone (owner seal)."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.background
        umbra_radius = ctx.radius * spec.umbra_radius_fraction
        aura_radius = ctx.radius * spec.aura_radius_fraction
        painter.setPen(Qt.PenStyle.NoPen)

        # The Umbra rotates WITH the star (owner spec): the lightest
        # section centers on the star's top tip — true solar noon — and
        # the darkest on solar midnight. Its radius is tuned
        # independently of the Aura.
        painter.save()
        painter.rotate(ctx.rotation)
        if spec.base_asset is not None:
            draw_pixmap_centered(
                painter, ctx, spec.base_asset, QPointF(0, 0), 2 * umbra_radius
            )
        else:
            self._draw_umbra(painter, ctx, umbra_radius)
        painter.restore()

        # AURORA (owner spec 2026-07-12): no geometric pointer — the
        # day hues spread evenly across the actual sunrise-sunset arc,
        # dawn blue on the left, dusk brown on the right, so every hue
        # stays visible on the shortest and the longest day alike.
        if ctx.skin.colorful and ctx.skin.pointer == "aurora":
            bands, solar_frame = aurora_bands(
                ctx.day.sun, aura_palette_for(ctx.skin), spec.day_alpha,
            )
            for start, end, hue, alpha in bands:
                painter.save()
                if solar_frame:
                    painter.rotate(ctx.rotation)
                painter.setOpacity(alpha)
                painter.setBrush(QColor(hue))
                draw_pie(painter, aura_radius, start, end)
                painter.restore()
            return

        # CALENDAR (owner 2026-07-16, CANON §The Dozen): TWELVE 2-hour
        # wedges — the Aura carries the wedge colors, no star arms (like
        # Aurora). Calendar-FIXED: the wedges never ride the solar
        # rotation (owner spec), so they paint at rotation 0 — otherwise
        # they are the SAME Aura every other pointer draws (owner
        # correction 2026-07-29: the Calendar's own always-full-circle
        # fixed-alpha path is GONE, it follows the day/night law like
        # everyone else). The lit-wedge feature — the shichen under the
        # hour hand, the month/sign under the Earth — died with the
        # earlier decree.
        if ctx.skin.pointer == "calendar":
            self._paint_aura(
                painter, ctx, aura_radius, aura_palette_for(ctx.skin),
                calendar_wedge_bounds(calendar_wheel(ctx.skin)), 0.0,
            )
            if ctx.skin.calendar_mount != "off":
                _draw_calendar_mount(painter, ctx, ctx.skin.calendar_mount)
            return

        # Colorful off (Elements switch): the day/twilight arcs are still
        # indicated, but in plain white — a one-entry palette draws a
        # single full wedge under the same clip and alphas.
        aura_hues = (
            aura_palette_for(ctx.skin)
            if ctx.skin.colorful
            else (palette.COLORFUL_OFF_COLOR,)
        )
        # THE BACKGROUND FOLLOWS THE STAR (`aura_wedge_bounds` — the
        # owner's fix 2026-07-29): each hue's wedge is anchored on its
        # own LEAD RAY, wheel offset included, so a wedge can never
        # stand half behind one hue's rays and half behind the next.
        self._paint_aura(
            painter, ctx, aura_radius, aura_hues,
            aura_wedge_bounds(ctx.skin, aura_hues), ctx.rotation,
        )

    def _paint_aura(
        self, painter: QPainter, ctx: RenderContext, radius: float,
        hues: tuple, wedges: list[tuple[float, float]], rotation: float,
    ) -> None:
        """The colored wedges — ONE law for every pointer that has them
        (Rule #5): the Calendar's twelve calendar-FIXED wedges pass
        rotation 0, every star pointer passes the solar rotation.

        ```
        IF the daylight law runs (daylight_active):
            FOR EACH (start, end, alpha) lit arc of the day:
                clip to the arc, then draw every wedge at that alpha
        ELSE:                                  # the switch is off
            draw every wedge over the WHOLE circle at the day alpha
        ```
        """
        spec = self._skin.background
        if not daylight_active(ctx.skin):
            painter.save()
            painter.setOpacity(spec.day_alpha)
            painter.rotate(rotation)
            for color, (wedge_start, wedge_end) in zip(hues, wedges):
                painter.setBrush(QColor(color))
                draw_pie(painter, radius, wedge_start, wedge_end)
            painter.restore()
            return
        for start, end, alpha in lit_regions(ctx.day.sun, spec):
            painter.save()
            painter.setClipPath(pie_path(radius, start, end))
            painter.setOpacity(alpha)
            painter.rotate(rotation)
            for color, (wedge_start, wedge_end) in zip(hues, wedges):
                painter.setBrush(QColor(color))
                draw_pie(painter, radius, wedge_start, wedge_end)
            painter.restore()

    def _draw_umbra(
        self, painter: QPainter, ctx: RenderContext, radius: float
    ) -> None:
        """The brightness wheel, drawn in the already-rotated frame:
        lightest at the top (true solar noon), darkest at the bottom
        (true midnight), mirrored left/right. Forms (owner spec): fine
        30 / coarse 24 sections — single lightest/darkest sections
        centered on top/bottom, the rest in mirror pairs — or the
        continuous per-pixel gradient.

        With the daylight switch OFF (the Calendar and the Rose only,
        owner correction 2026-07-29) there is no night to shade: the
        whole disc stands at FLAT NOON — one full circle in the contrast
        span's LIGHTEST shade, through the same tint map every form
        uses."""
        contrast = ctx.skin.umbra_contrast
        tint = ctx.skin.ring_tint            # the Umbra follows the ring hue
        lightest, darkest = defaults.UMBRA_CONTRAST_SPANS[contrast]
        lightest = min(255, lightest)            # spans store window BOUNDS
        if not daylight_active(ctx.skin):
            painter.setBrush(tinted_gray(lightest, tint))
            painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
            return
        if ctx.skin.umbra_form == "gradient":
            # Conical sweep from the top: symmetric stops make the
            # left/right sides exact mirrors, per-pixel smooth.
            gradient = QConicalGradient(QPointF(0.0, 0.0), 90.0)
            gradient.setColorAt(0.0, tinted_gray(lightest, tint))
            gradient.setColorAt(0.5, tinted_gray(darkest, tint))
            gradient.setColorAt(1.0, tinted_gray(lightest, tint))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
            return
        sections = constants.UMBRA_SECTION_COUNTS[ctx.skin.umbra_form]
        span = 360.0 / sections
        shades = umbra_ladder(sections // 2 + 1, contrast)
        for k, value in enumerate(shades):
            painter.setBrush(tinted_gray(value, tint))
            center = k * span
            draw_pie(painter, radius, center - span / 2, center + span / 2)
            if 0 < k < len(shades) - 1:
                # Mirrored partner on the left side; the lightest and
                # darkest stay single.
                draw_pie(
                    painter, radius, 360.0 - center - span / 2, 360.0 - center + span / 2
                )


class StarLayer(Layer):
    """The drawn wheel — an N-diamond STAR or the plain POLYGON of the
    same arms (owner sheet 2026-07-29) — whose top arm points at true
    solar noon (or straight up with solar rotation off). Colored
    near-full opacity where the sun is up, borders elsewhere (owner
    model). The armless Aurora draws nothing here; the Calendar draws
    its two hexagrams / twelve-point star over its own wedges."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.star
        if ctx.skin.pointer == "aurora":
            return          # no geometry at all — the wheel IS the pointer

        # Colored BORDERS run the full circle so the night arms stay
        # recognizable (owner spec) — unless the reader asked for the
        # night to keep its fills alone (`border_clips`)...
        for clip in border_clips(ctx.skin, ctx.day.sun):
            self._paint_pass(painter, ctx, False, spec.border_alpha, clip)

        # ...while the FILLS appear only where the sun is up — UNLESS
        # the reader switched the daylight law off (owner 2026-07-27:
        # the Calendar and the Rose carry that switch), in which case
        # the whole wheel stands in flat full color.
        if not daylight_active(ctx.skin):
            self._paint_pass(painter, ctx, True, spec.day_alpha, None)
            return
        for start, end, alpha in lit_regions(ctx.day.sun, spec):
            self._paint_pass(painter, ctx, True, alpha, (start, end))

    def _paint_pass(
        self, painter: QPainter, ctx: RenderContext, fill: bool,
        alpha: float, clip: tuple[float, float] | None,
    ) -> None:
        """One whole-wheel pass at `alpha`, optionally clipped to a dial
        arc (the lit regions; None = the full circle). The clip is taken
        in WALL-CLOCK dial space, the wheel drawn inside it in its own
        rotated frame — the standing order."""
        painter.save()
        if clip is not None:
            painter.setClipPath(pie_path(ctx.radius, *clip))
        painter.setOpacity(alpha)
        painter.rotate(wheel_rotation(ctx.skin, ctx.rotation))
        self._draw_arms(painter, ctx, fill)
        painter.restore()

    def _draw_arms(
        self, painter: QPainter, ctx: RenderContext, fill: bool
    ) -> None:
        """Every arm of every pass, in z-order (`drawn_arms`) — the
        Rose's three stars bottom-first, the Calendar's odd hexagram
        under its even one, one pass everywhere else. The SHAPE is the
        arm's own path (`arm_shape_path`); nothing else here knows
        whether a star or a polygon is being drawn."""
        spec = self._skin.star
        tip = ctx.radius * spec.radius_fraction
        border_width = max(1.0, ctx.radius * spec.border_width_fraction)
        lead = QPen(
            QColor(palette.ARM_OUTLINE),
            max(1.0, ctx.radius * defaults.ARM_OUTLINE_WIDTH),
        )
        for arms in drawn_arms(ctx.skin, palette_for(ctx.skin)):
            for theta, color in arms:
                shape = arm_shape_path(ctx.skin, tip, theta)
                if fill:
                    # THE LEAD LINE (owner's correction round
                    # 2026-07-29 — the Rose's dark lead was "the good
                    # example", so every pointer wears it now): each arm
                    # or polygon face is stroked AS IT IS FILLED, in
                    # draw order, so the outline follows the z-stack and
                    # the INTERNAL colour boundaries come free — every
                    # face is its own path, and stroking the path draws
                    # the edges it shares with its neighbours. The
                    # armless Aurora never reaches here at all.
                    painter.setPen(lead)
                    painter.setBrush(QColor(color))
                    painter.drawPath(shape)
                else:
                    # Border as PADDING (owner spec): clip to the arm and
                    # stroke at double width, so only the inner half
                    # shows — neighboring arms' borders sit side by side
                    # instead of overpainting each other along shared
                    # edges. INTERSECT, never replace: the pass may
                    # already be clipped to the sunlit arcs
                    # (`hide_night_borders`), and a plain setClipPath
                    # would throw that away and stroke the night too.
                    painter.save()
                    painter.setClipPath(shape, Qt.ClipOperation.IntersectClip)
                    painter.setPen(QPen(QColor(color), 2.0 * border_width))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawPath(shape)
                    painter.restore()


class RingLayer(Layer):
    """Outer ring: donut, hour ticks, 24h numerals with per-skin letters,
    minute numbers along the inner edge."""

    cadence = Cadence.STATIC

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.ring
        if spec.asset is not None:
            # The ring art carries numerals and minutes; the ring tint
            # multiplies the art. The LETTERS are the owner's separate
            # gold/silver art, overlaid by calculation so the tint never
            # touches them (1x1 placeholders until his files land). The
            # RING SATURATION slider (owner 2026-07-18, Session 21-D)
            # scales the plate's saturation AFTER the tint recolor — the
            # plate is grayscale-mastered, so saturating the pre-tint
            # source would be a no-op; the tinted OUTPUT is what actually
            # carries hue.
            draw_pixmap_centered(
                painter, ctx, spec.asset, QPointF(0, 0), 2 * ctx.radius,
                tint=ctx.skin.ring_tint, saturation=ctx.skin.ring_saturation,
            )
            self._draw_letter_art(painter, ctx)
            self._draw_motto(painter, ctx)
            return
        outer, inner = ctx.radius, ctx.radius * (1.0 - spec.width_fraction)

        ring = QPainterPath()
        # (procedural fallback ring below — no tint, no letter art)
        ring.addEllipse(QRectF(-outer, -outer, 2 * outer, 2 * outer))
        ring.addEllipse(QRectF(-inner, -inner, 2 * inner, 2 * inner))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(ring, QColor(spec.fill))

        # Explicit QPen — copying painter.pen() would inherit the NoPen
        # STYLE set for the donut fill and the ticks would never render.
        painter.setPen(
            QPen(QColor(spec.text_color), max(1.0, ctx.radius * defaults.RING_TICK_WIDTH))
        )
        for hour in range(constants.HOURS_PER_REVOLUTION):
            theta = (hour * 15.0 + constants.DIAL_OFFSET_DEG) % 360.0
            painter.drawLine(
                dial_point(theta, inner),
                dial_point(theta, inner * defaults.RING_TICK_REACH),
            )

        numeral_font = QFont()
        numeral_font.setPixelSize(
            max(defaults.RING_NUMERAL_MIN_PX, round(ctx.radius * defaults.RING_NUMERAL_SIZE))
        )
        numeral_font.setBold(True)
        letter_font = QFont()
        letter_font.setPixelSize(
            max(defaults.RING_LETTER_MIN_PX, round(ctx.radius * defaults.RING_LETTER_SIZE))
        )
        letter_font.setBold(True)
        mid = (outer + inner) / 2
        box = ctx.radius * defaults.RING_TEXT_BOX
        for hour in range(constants.HOURS_PER_REVOLUTION):
            theta = (hour * 15.0 + constants.DIAL_OFFSET_DEG) % 360.0
            center = dial_point(theta, mid)
            rect = QRectF(center.x() - box / 2, center.y() - box / 2, box, box)
            letter = spec.letters.get(hour)
            if letter is not None:
                painter.setFont(letter_font)
                painter.setPen(QColor(spec.letter_color))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, letter)
            else:
                painter.setFont(numeral_font)
                painter.setPen(QColor(spec.text_color))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(hour))

        minute_font = QFont()
        minute_font.setPixelSize(
            max(defaults.RING_MINUTE_MIN_PX, round(ctx.radius * defaults.RING_MINUTE_SIZE))
        )
        painter.setFont(minute_font)
        painter.setPen(QColor(spec.text_color))
        minute_radius = inner * defaults.RING_MINUTE_RADIUS
        for minute in range(5, 60, 5):
            center = dial_point(minute * 6.0, minute_radius)
            rect = QRectF(center.x() - box / 2, center.y() - box / 2, box, box)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(minute))

    def _draw_ring_glyph(
        self, painter: QPainter, ctx: RenderContext, gold_asset: Path,
        metal: str, theta: float, radius_fraction: float, height: float,
    ) -> None:
        """One letter-art glyph stamped on the ring circle — the shared
        stamp (Rule #5) behind BOTH the ring's own six banknote letters
        (`_draw_letter_art`) and the outer motto arc (`_draw_motto`,
        TASK 1, owner "može radi" 2026-07-19): the metal finish (derived
        from the gold master, `render.asset_recolor.letter_metal_file`), a
        tight dark halo (owner spec: a gradient border, lit from above)
        and a tangential ROTATION that flips 180° through the lower half
        so text never reads upside down (Ω stands upright at the
        bottom — `core.angles.readable_rotation_deg`). UNTINTED by the
        ring hue either way, but the RING SATURATION slider still grays
        it (owner 2026-07-18, Session 21-D: "the ring plate + its
        letters" is one target); the shadow copy skips it — a pure
        black silhouette has no saturation to scale."""
        shadow_radius = height * defaults.RING_LETTER_SHADOW_RADIUS
        samples = defaults.RING_LETTER_SHADOW_SAMPLES
        # Silver/bronze are derived from the gold master AT LOAD (owner
        # 2026-07-19), disk-cached like every other derived asset — the
        # shadow silhouette is metal-invariant (same alpha mask on every
        # finish), so it always reads the gold file directly.
        asset = letter_metal_file(gold_asset, metal)
        pixmap = ctx.cache.pixmap_by_height(
            asset, height, ctx.dpr, saturation=ctx.skin.ring_saturation
        )
        shadow = ctx.cache.pixmap_by_height(
            gold_asset, height, ctx.dpr, tint=palette.SHADOW_STAMP_TINT
        )
        logical_w = pixmap.width() / ctx.dpr
        pos = dial_point(theta, ctx.radius * radius_fraction)
        rotation = angles.readable_rotation_deg(theta)
        painter.save()
        painter.translate(pos)
        painter.rotate(rotation)
        painter.setOpacity(defaults.RING_LETTER_SHADOW_ALPHA)
        for k in range(samples):
            angle = 2.0 * math.pi * k / samples
            painter.drawPixmap(
                QPointF(
                    -logical_w / 2 + shadow_radius * math.cos(angle),
                    -height / 2 + shadow_radius * math.sin(angle),
                ),
                shadow,
            )
        painter.setOpacity(1.0)
        painter.drawPixmap(QPointF(-logical_w / 2, -height / 2), pixmap)
        painter.restore()

    def _draw_letter_art(self, painter: QPainter, ctx: RenderContext) -> None:
        """The owner's letter art at the preset's hour positions — gold
        masters, silver/bronze derived at load (the accent letter wears
        the opposite metal, owner spec). Stamped by `_draw_ring_glyph`
        (Rule #5, shared with the outer motto arc)."""
        height = (
            2 * ctx.radius * defaults.RING_LETTER_ART_SCALE
            * ctx.skin.ring_letter_scale
        )
        for hour, gold_asset in self._skin.ring.letter_art.items():
            theta = angles.ring_position_angle(hour)
            metal = self._skin.ring.letter_metal.get(hour, "gold")
            # The Eye's SHINE ENLARGE (owner UV inbox 2026-07-27):
            # build_skin stamps a per-hour height multiplier for the
            # shine masters so the triangle stays the no-light size and
            # only the rays extend beyond it (1.0 for plain letters).
            self._draw_ring_glyph(
                painter, ctx, gold_asset, metal, theta,
                defaults.RING_LETTER_RADIUS_FRACTION,
                height * self._skin.ring.letter_zoom.get(hour, 1.0),
            )

    def _draw_motto(self, painter: QPainter, ctx: RenderContext) -> None:
        """The outer GREAT SEAL MOTTO ARC (MOTO-FIX round, owner
        correction 2026-07-19, the dollar's Great Seal reference
        image): each character of the preset's `motto` texts —
        pre-solved to its own dial angle by `data.rings`/`core.motto`
        (ANNUIT COEPTIS's own A/S pin the TOP arc at 8h/16h, NOVUS ORDO
        SECLORUM's own N/O/M pin the BOTTOM arc at 4h/24h/20h — MASON
        outside, G inside) — drawn via the SAME stamp the ring's own
        six letters use (`_draw_ring_glyph`, Rule #5), just smaller
        (`RING_MOTTO_SIZE`) and further out. The two arcs are angularly
        DISJOINT (top 300-360-60 deg, bottom 120-180-240 deg) so both
        share ONE radius (`RING_MOTTO_RADIUS_FRACTION`) — no more two
        concentric rings of text. Empty (no-op) for every preset
        without a motto."""
        mottos = self._skin.ring.motto
        if not mottos:
            return
        height = (
            2 * ctx.radius * defaults.RING_MOTTO_SIZE * ctx.skin.ring_letter_scale
        )
        metal = self._skin.ring.motto_metal
        for motto in mottos:
            for gold_asset, theta in motto["glyphs"]:
                self._draw_ring_glyph(
                    painter, ctx, gold_asset, metal, theta % 360.0,
                    defaults.RING_MOTTO_RADIUS_FRACTION, height,
                )


def weekday_label_text(ctx: RenderContext, body: str) -> str:
    """The displayed weekday text for `body`: short until the largest
    preset, full from `WEEKDAY_FULL_NAME_MIN_DIAMETER`."""
    full_text = 2 * ctx.radius >= defaults.WEEKDAY_FULL_NAME_MIN_DIAMETER
    return (
        constants.WEEKDAY_FULL_NAMES[body] if full_text
        else constants.WEEKDAY_LABELS[body]
    )


def weekday_label_set_px(ctx: RenderContext) -> int:
    """The SET-UNIFORM label size (owner verdict 2026-07-18, ROADMAP
    15h) for the weekday bodies of THIS dial: every name sharing the
    ring — the diamond slot occupants, and the hexa/trio center Sun
    whichever of WeekdayLayer/CenterBodyLayer draws it this frame —
    wears the size of the SMALLEST fitted member, computed once here
    (a pure, cheap text-measurement pass) rather than per label. Two
    separate paint passes (WeekdayLayer is DAILY, CenterBodyLayer is
    MINUTE) call this same pure function and agree on one size without
    sharing mutable state."""
    spec = ctx.skin.weekday_set
    today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
    if spec.display_mode == "center_only":
        # A set of one — its own fit is the whole answer.
        text = weekday_label_text(ctx, today)
        width = (
            2 * ctx.radius * spec.center_scale
            * defaults.NAME_LABEL_WIDTH_FRACTION
        )
        return name_label_px(text, width)
    slot_size = weekday_body_size(ctx.skin, ctx.radius)
    target_width = slot_size * defaults.NAME_LABEL_WIDTH_FRACTION
    servant = servant_holds_the_seat(ctx.skin, today)
    bodies = set()
    for slot_angle, occupants in weekday_slots(ctx.skin):
        if servant and slot_angle == servant_seat_angle(ctx.skin):
            continue
        bodies.add(visible_occupant(occupants, today))
    if center_duality(ctx.skin):
        bodies.add("sun")     # the ghost/opaque center Sun joins the set
    texts = {weekday_label_text(ctx, body) for body in bodies}
    return min(name_label_px(text, target_width) for text in texts)


def draw_body_label(
    painter: QPainter, ctx: RenderContext, body: str,
    pos: QPointF, size: float, label_px: float | None = None,
) -> None:
    """The weekday-name label on a body — shared by the weekday unit
    and the info slot's second body (Rule #5). `label_px` is the SET-
    UNIFORM size (owner verdict 2026-07-18) the caller computed once
    per paint via `weekday_label_set_px`, already hover-scaled; when
    omitted (a standalone single-body caller — the info slot's own
    seated body is a set of one) this body's own fit is used."""
    label = weekday_label_text(ctx, body)
    px = (
        label_px if label_px is not None
        else name_label_px(label, size * defaults.NAME_LABEL_WIDTH_FRACTION)
    )
    draw_name_label(painter, label, pos, px)


def draw_weekday_body(
    painter: QPainter,
    ctx: RenderContext,
    body: str,
    pos: QPointF,
    size: float,
    opacity: float,
    label_px: float | None = None,
) -> None:
    """One weekday body with its white outlined label — shared by the
    diamond slots and the above-the-hands center pass (Rule #5). The
    label is the weekday name (owner spec): short until the largest
    preset, full from WEEKDAY_FULL_NAME_MIN_DIAMETER. `label_px`
    threads the SET-UNIFORM size through to `draw_body_label` (owner
    verdict 2026-07-18)."""
    spec = ctx.skin.weekday_set
    painter.save()
    painter.setOpacity(opacity)
    # The planet-SIGN glyphs wear NO text at all (owner correction
    # 2026-07-12 — supersedes the earlier stacked-above rule).
    names_on = (
        ctx.skin.show_weekday_names
        and ctx.skin.weekday_theme != "planet_signs"
    )
    asset = spec.bodies.get(body)
    if ctx.skin.weekday_theme == "continents" and body in defaults.CONTINENTS_REGIONS:
        # THE CONTINENTS live art (owner-sealed matrix 2026-07-21): the
        # baked skin body is only the atmo-day still frame — on the dial
        # the continent follows the user's earth_style (one setting, whole
        # instrument) and the SKY'S OWN day/night (`ctx.tick.is_daylight`,
        # the same sun-elevation law the Earth marker already computes,
        # never recomputed here). Graceful-absent if the face is missing.
        live = defaults.continents_body_art(
            body, ctx.skin.earth_style, ctx.tick.is_daylight
        )
        if paths.art_file(live).exists():
            asset = live
    if asset is not None:
        # THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20,
        # weekday ALT ROTATION round 2026-07-20/21): whichever canonical
        # file `spec.bodies`/the continents live override landed above
        # rotates daily among its OWN `_v2`/`alt/` siblings if it has
        # any — a no-op for every body that has none (the vast
        # majority today).
        asset = defaults.rotating_art_file(asset, ctx.day.local_date) or asset
    if asset is not None:
        # The theme's metal (owner 2026-07-12): the hue-selective swap
        # turns only the bronze details gold/silver; None = as drawn.
        draw_pixmap_centered(
            painter, ctx, asset, pos, size, metal=spec.metal,
        )
    else:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(spec.body_colors[body]))
        painter.drawEllipse(pos, size / 2, size / 2)
    if names_on:
        draw_body_label(painter, ctx, body, pos, size, label_px)
    painter.restore()


class WeekdayLayer(Layer):
    """Weekday bodies on the pointer's arm slots (rotating WITH the star,
    owner decision), BELOW the hands. The hexa and trio pointers keep
    the Sun in the center; cross/octa give every body a slot — shared
    slots show only the priority winner (see visible_occupant). Modes: "ghost" (all
    visible slots, non-current faint) and "center_only" (only the current
    day's body, in the center). Whenever the CENTER image is the current
    day it is drawn by CenterBodyLayer instead — ABOVE the hands (owner
    spec; slot images are unaffected)."""

    cadence = Cadence.DAILY
    # Hover-enlarge and the reveal window both change these bodies, so
    # the compositor draws the layer LIVE, never in the cached composite
    # (owner 2026-07-17, ROADMAP 15f) — a hover no longer rebuilds it.
    hover_variable = True

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]

        if weekday_classic_slot(ctx.skin) is None:
            return   # every slot sits in a SEAT (the slot layer draws)

        if spec.display_mode == "center_only":
            return                       # the center pass draws it above the hands

        # SET-UNIFORM label size (owner verdict 2026-07-18, ROADMAP 15h):
        # computed ONCE per paint for the whole weekday ring, never per
        # label — the hover-enlarged twin scales this same base size.
        names_on = (
            ctx.skin.show_weekday_names
            and ctx.skin.weekday_theme != "planet_signs"
        )
        base_label_px = weekday_label_set_px(ctx) if names_on else None

        if (
            center_duality(ctx.skin)
            and today != "sun"
            and not ctx.reveal_active
            and self._gate(ctx, "body:sun")
        ):
            # The center-duality wheels (hexa/trio, and the Quaternity's
            # Seasons wheel — owner seal 2026-07-29) center the Sun; on
            # Sundays — or during the reveal window (owner 2026-07-16) —
            # the CENTER pass draws it opaque ABOVE the hands instead.
            hf = hover_factor(ctx, "body:sun")
            center_size = weekday_body_size(ctx.skin, ctx.radius) * hf
            draw_weekday_body(
                painter, ctx, "sun", QPointF(0, 0), center_size,
                spec.ghost_opacity,
                base_label_px * hf if base_label_px is not None else None,
            )
        orbit = ctx.radius * weekday_body_orbit(ctx.skin)
        slot_size = weekday_body_size(ctx.skin, ctx.radius)
        servant = servant_holds_the_seat(ctx.skin, today)
        # THE TWO-BADGE NINTH WINDOWS (owner seal 2026-07-29 — the law
        # the center seat always had, extended to the two-seat Sundays):
        # near solar noon the Ninth borrows the SERVANT's seat (and
        # stands beside the Ruler), near solar midnight the RULER's
        # (beside the Servant). Existence-gated like every Ninth plate;
        # themes naming none keep both faces all Sunday.
        seat_taken, ninth_plate = None, None
        if servant and today == "sun" and not ctx.reveal_active:
            ninth_plate = theme_ninth(
                ctx.skin.weekday_theme, ninth_alt_active(ctx),
                on_date=ctx.day.local_date,
            )
            if ninth_plate is not None:
                seat_taken = dual_seat_ninth(ctx.day, ctx.tick)
        for slot_angle, occupants in weekday_slots(ctx.skin):
            if servant and slot_angle == servant_seat_angle(ctx.skin):
                continue     # the Servant won that seat today
            body = visible_occupant(occupants, today)
            if not self._gate(ctx, f"body:{body}"):
                continue
            theta = slot_angle + ctx.rotation
            hf = hover_factor(ctx, f"body:{body}")
            if seat_taken == "ruler" and body == "sun":
                # The midnight window: the Ninth's plate on the Ruler's
                # seat — image only, the label belongs to the faces.
                draw_pixmap_centered(
                    painter, ctx, ninth_plate[1], dial_point(theta, orbit),
                    slot_size * hf, metal=spec.metal,
                )
                continue
            draw_weekday_body(
                painter, ctx, body, dial_point(theta, orbit),
                slot_size * hf,
                1.0 if body == today or ctx.reveal_active else spec.ghost_opacity,
                base_label_px * hf if base_label_px is not None else None,
            )
        if servant and self._gate(ctx, "sun_servant"):
            # THE SERVANT FACE at 24h (owner 2026-07-13): it stands all
            # week like every other body — ghosted, OPAQUE on Sunday or
            # during the reveal window — two persons, a union; the
            # metal themes' swap recolors it exactly like the Ruler
            # plate. Image only — the Names label belongs to the Ruler
            # face.
            servant_asset = spec.dual_asset
            if ctx.skin.weekday_theme == "continents":
                # The Arctic Servant follows earth_style + live sky like
                # the six arms (owner-sealed matrix 2026-07-21).
                live = defaults.continents_dual_art(
                    ctx.skin.earth_style, ctx.tick.is_daylight
                )
                if paths.art_file(live).exists():
                    servant_asset = live
            # THE UNIVERSAL ROTATION CONVENTION (weekday ALT ROTATION
            # round 2026-07-20/21): the dual's own `_v2`/`alt/` siblings
            # (e.g. bible_dark's Judas) rotate daily like the Ruler face.
            servant_asset = (
                defaults.rotating_art_file(servant_asset, ctx.day.local_date)
                or servant_asset
            )
            if seat_taken == "servant":
                # The noon window: the Ninth's plate on the Servant's
                # seat (owner seal 2026-07-29) — `theme_ninth` already
                # resolved rotation and the Pangea easter egg above.
                servant_asset = ninth_plate[1]
            painter.save()
            painter.setOpacity(
                1.0 if today == "sun" or ctx.reveal_active else spec.ghost_opacity
            )
            draw_pixmap_centered(
                painter, ctx, servant_asset,
                dial_point(
                    servant_seat_angle(ctx.skin) + ctx.rotation, orbit
                ),
                slot_size * hover_factor(ctx, "sun_servant"),
                metal=spec.metal,
            )
            painter.restore()


class SlotLayer(Layer):
    """Every SEATED slot (owner matrix 2026-07-14): the 1st/2nd/3rd
    contents at their matrix positions — angles ride the star's
    rotation, "center" sits on the hub; the classic weekday unit
    belongs to WeekdayLayer. MINUTE cadence — the ascendant moves
    hourly and the small-seconds hand repaints on the per-second
    tick. Two instances share the class: the below-hands one draws
    the ANGLE seats, the above-hands one the CENTER seat (owner: the
    center occludes the hands); the hover-lift twin draws whatever is
    hovered."""

    cadence = Cadence.MINUTE

    def __init__(
        self, skin: SkinDefinition, centered: bool = False,
        lift: bool = False,
    ):
        super().__init__(skin, lift=lift)
        self._centered = centered

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        for index, seat in slot_layout(ctx.skin).items():
            if seat == "classic":
                continue
            if not self._lift and (seat == "center") != self._centered:
                continue                 # the other instance draws it
            element = f"slot:{index}"
            if not self._gate(ctx, element):
                continue                 # hover z-lift repaints on top
            if seat == "center":
                pos = QPointF(0.0, 0.0)
            else:
                pos = dial_point(
                    seat + slot_seat_rotation(ctx.skin, ctx.rotation),
                    ctx.radius * spec.orbit_fraction
                    * slot_seat_orbit(ctx.skin, seat),
                )
            size = (
                2 * ctx.radius * spec.diamond_scale
                * slot_seat_scale(ctx.skin)
                * hover_factor(ctx, element)
            )
            self._draw_slot(painter, ctx, index, pos, size)

    def _draw_slot(
        self, painter: QPainter, ctx: RenderContext, index: int,
        pos: QPointF, size: float,
    ) -> None:
        mode, style, theme, metal, roster = slot_view(ctx.skin, index)
        inner = size * defaults.SLOT_ROUNDEL_CONTENT_FRACTION
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        if mode == "seconds":
            # The SMALL-SECONDS complication (owner 2026-07-14).
            draw_slot_roundel(painter, ctx, pos, size)
            draw_small_seconds(painter, ctx, pos, size)
            return
        if mode == "date":
            # The full date in two rows (owner 2026-07-14); the year
            # row wears the era notation (Session 16 dual calendar).
            draw_slot_roundel(painter, ctx, pos, size)
            draw_two_lines(
                painter, ctx, pos, inner,
                slot_text("date", ctx), display_year(ctx),
            )
            return
        if mode in ("time", "day_length"):
            draw_slot_roundel(painter, ctx, pos, size)
            draw_fitted_text(painter, ctx, pos, inner, slot_text(mode, ctx))
            return
        if mode == "weekday":
            self._draw_weekday_slot(
                painter, ctx, index, pos, size, theme, metal, roster,
                today,
            )
            return
        if mode in ("zodiac", "ascendant"):
            sign = (
                ctx.tick.ascendant_sign
                if mode == "ascendant"
                else ctx.day.zodiac_name
            )
            if style in constants.ZODIAC_STYLE_ART_DIRS:
                asset = octa_slot_art(
                    constants.ZODIAC_STYLE_ART_DIRS[style], sign
                )
                if asset is not None:
                    if style == "colored":
                        draw_pixmap_centered(painter, ctx, asset, pos, size)
                    else:
                        # Flat glyph art rides the subdial (owner
                        # 2026-07-14); the colored badge stays bare.
                        draw_slot_roundel(painter, ctx, pos, size)
                        draw_pixmap_centered(
                            painter, ctx, asset, pos, inner
                        )
                    return
            # TEXT style, and the documented fallback until the art
            # lands — the Ascendant speaks the FULL word (owner
            # 2026-07-13, never the "Asc" shorthand).
            draw_slot_roundel(painter, ctx, pos, size)
            if mode == "ascendant":
                draw_two_lines(painter, ctx, pos, inner, "Ascendant", sign)
            else:
                draw_fitted_text(painter, ctx, pos, inner, sign)
            return
        # Chinese zodiac: the plates stay bare, text and the fallback
        # ride the subdial as element-over-animal (owner 2026-07-12).
        animal = ctx.day.chinese_name.split()[-1]
        if style in constants.CHINESE_STYLE_ART_DIRS:
            asset = octa_slot_art(
                constants.CHINESE_STYLE_ART_DIRS[style], animal
            )
            if asset is not None:
                draw_pixmap_centered(
                    painter, ctx, asset, pos, size,
                    metal=(
                        style if style in defaults.METAL_SWAP_TARGETS
                        else None
                    ),
                )
                return
        draw_slot_roundel(painter, ctx, pos, size)
        draw_two_lines(
            painter, ctx, pos, inner, ctx.day.chinese_name.split()[0], animal
        )

    def _draw_weekday_slot(
        self, painter: QPainter, ctx: RenderContext, index: int,
        pos: QPointF, size: float, theme: str, metal: str | None,
        roster: str, today: str,
    ) -> None:
        """Today's body in a SEAT, in that slot's own theme AND roster
        (owner 2026-07-12: e.g. Norse left, Greek right, both showing
        today; owner 2026-07-15: the roster is the slot's own too)."""
        if index == 1:
            # The 1st slot's unit is already themed on the skin.
            draw_weekday_body(painter, ctx, today, pos, size, 1.0)
            return
        seat = (
            defaults.pantheon_seat(theme, today)
            if roster == "pantheon" else None
        )
        if seat is not None:
            # The PANTHEON figure on this seat (owner 2026-07-15) —
            # the shared safety law: no plate on disk means the
            # planetary bundle below stays whole.
            asset = seat[0]
        else:
            # THE ONE weekday-body resolver (Rule #5 — this used to
            # re-type the theme_dir/colored-folder/planets-branch
            # expression inline; now shared with `app.controller` and
            # `render.compositor`'s hover legend). colored is the
            # variant SIBLING (owner restructure 2026-07-14:
            # <family>/colored).
            asset = defaults.weekday_theme_body_art(
                theme, today,
                colored=(metal == "colored" and theme in constants.METAL_THEMES),
            )
        # THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20,
        # weekday ALT ROTATION round 2026-07-20/21): resolved fresh
        # every paint already (this slot is never baked at settings
        # time), so the day's own `_v2`/`alt/` pick applies directly —
        # a no-op for every body/seat with no siblings.
        asset = defaults.rotating_art_file(asset, ctx.day.local_date) or asset
        if paths.art_file(asset).exists():
            draw_pixmap_centered(
                painter, ctx, asset, pos, size,
                metal=(
                    metal
                    if theme in constants.METAL_THEMES
                    and metal in defaults.METAL_SWAP_TARGETS
                    else None
                ),
            )
            if ctx.skin.show_info_slot_names and theme != "planet_signs":
                draw_body_label(painter, ctx, today, pos, size)
            return
        # Documented fallback until the theme art lands.
        draw_slot_roundel(painter, ctx, pos, size)
        draw_fitted_text(
            painter, ctx, pos,
            size * defaults.SLOT_ROUNDEL_CONTENT_FRACTION,
            constants.WEEKDAY_LABELS[today],
        )


class CenterBodyLayer(Layer):
    """The current day's CENTER image drawn ABOVE the hands — the opaque
    Sun on Sundays in ghost mode (hexa and trio pointers; cross/octa
    seat the Sun on an arm slot), or the day's body in center_only mode
    — so the hands sweep behind it (owner spec; the slot images never
    move up here). During the reveal-week window (owner 2026-07-16) the
    ghost center Sun also rises here, opaque, on every day of the week —
    that IS the z-order lift the reveal promises.

    **THE BLUE MOON LAW (owner-sealed 2026-07-22, CORRECTED 2026-07-2X)
    — checked FIRST, independent of everything below:** `active_
    thirteenth(skin, day)` names the 13th (if any) the Calendar
    pointer's OWN mode is showing today — gated to `skin.pointer ==
    "calendar"` alone, so it can NEVER fire on hexa/trio/center_only
    (R12's global law is retired; see [Blue Moon](../core/blue_moon.md)).
    The Calendar pointer never carries a classic weekday seat at all
    (its slot layout is always "pinned" — `render.layers.slot_layout`),
    so its own dial center is otherwise EMPTY; a showing 13th draws
    there, at the same (0, 0) origin every other center face uses."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        thirteenth = active_thirteenth(ctx.skin, ctx.day)
        if thirteenth is not None:
            self._draw_thirteenth(painter, ctx, thirteenth)
            return
        if weekday_classic_slot(ctx.skin) is None:
            return          # every slot sits in a seat
        ghost_reveal = (
            ctx.reveal_active
            and spec.display_mode != "center_only"
            and center_duality(ctx.skin)
        )
        if spec.display_mode != "center_only" and not (
            center_duality(ctx.skin) and today == "sun"
        ) and not ghost_reveal:
            return
        # ONE body size (owner 2026-07-18, his screenshots): the hexa/
        # trio center matches the diamond bodies — normal state and
        # reveal alike (this path used to drop the seat factor, so the
        # double-click SHRANK the center). Only the center-only
        # showcase, with no diamond bodies to match, keeps its own
        # `center_scale`.
        center_size = (
            2 * ctx.radius * spec.center_scale
            if spec.display_mode == "center_only"
            else weekday_body_size(ctx.skin, ctx.radius)
        )
        hf = hover_factor(ctx, f"body:{today}")
        center_size *= hf
        body = "sun" if ghost_reveal else today
        names_on = (
            ctx.skin.show_weekday_names
            and ctx.skin.weekday_theme != "planet_signs"
        )
        # SET-UNIFORM label size (owner verdict 2026-07-18): the SAME
        # pure computation WeekdayLayer uses, agreeing on one size
        # across the two separate paint passes without shared state.
        label_px = weekday_label_set_px(ctx) * hf if names_on else None
        # THE DUAL/NINTH CENTER TIME WINDOWS (owner INSTRUCTION #5 +
        # solar amendment, round R3b item 3): on an ACTUAL Sunday
        # (never the ghost-reveal Sun, which always reads plain — the
        # reveal promises the ordinary "two persons, a union" read) the
        # SOLAR clock, not the wall clock, may swap the center's face
        # to EVIL (the Servant) or — where the theme names one — THE
        # UNFOUND (the Ninth). `center_dual_face` is the complementary
        # law to `sunday_dual_face` (Compass/Seasons keep their own
        # two-seat mechanic, untouched).
        if today == "sun" and not ghost_reveal and center_dual_face(self._skin):
            # THE DOUBLE NINTH's alt face (owner Double-Ninth verdicts,
            # 2026-07-29): `ninth_alt_active` dispatches by the theme's
            # OWN `constants.NINTH_MECHANISMS` entry — continents' sky
            # trigger, sw_dyad's daylight/night switch, or neither.
            ninth = theme_ninth(
                ctx.skin.weekday_theme, ninth_alt_active(ctx),
                on_date=ctx.day.local_date,
            )
            face = center_face(ctx.day, ctx.tick, ninth is not None)
            if face != "ruler":
                if face == "servant":
                    asset = spec.dual_asset
                    if ctx.skin.weekday_theme == "continents":
                        # The Arctic Servant follows earth_style + live
                        # sky like the Ruler and the six arms.
                        live = defaults.continents_dual_art(
                            ctx.skin.earth_style, ctx.tick.is_daylight
                        )
                        if paths.art_file(live).exists():
                            asset = live
                    # THE UNIVERSAL ROTATION CONVENTION (weekday ALT
                    # ROTATION round 2026-07-20/21).
                    asset = (
                        defaults.rotating_art_file(asset, ctx.day.local_date)
                        or asset
                    )
                    name = (
                        spec.dual_names
                        or defaults.WEEKDAY_DUAL_NAMES[ctx.skin.weekday_theme]
                    )[1]
                else:
                    name, asset = ninth
                painter.save()
                painter.setOpacity(1.0)
                draw_pixmap_centered(
                    painter, ctx, asset, QPointF(0, 0), center_size,
                    metal=spec.metal,
                )
                if names_on:
                    draw_name_label(
                        painter, name, QPointF(0, 0),
                        name_label_px(
                            name, center_size * defaults.NAME_LABEL_WIDTH_FRACTION
                        ),
                    )
                painter.restore()
                return
        draw_weekday_body(
            painter, ctx, body, QPointF(0, 0), center_size, 1.0, label_px
        )

    def _draw_thirteenth(
        self, painter: QPainter, ctx: RenderContext, key: str,
    ) -> None:
        """THE BLUE MOON LAW's 13th (owner-sealed 2026-07-22, CORRECTED
        2026-07-2X) — drawn at the dial's literal (0, 0) center, opaque,
        ABOVE the hands (`active_thirteenth` already gates this to
        `skin.pointer == "calendar"`, whose own center is otherwise
        empty — see the class docstring). Its own hover element is
        "thirteenth" (`render.compositor._element_at`), never a
        `center_seat_body_key` piggyback (that key names a DIFFERENT
        seat — the classic weekday unit's — which the Calendar pointer
        never carries). Graceful-absent like the calendar mount's own
        months (a NAME-ONLY fallback, never a hidden feature) — UNLIKE
        `theme_ninth`, whose missing plate makes a theme act as if it
        carried no Ninth at all: the 13th's whole point is its
        trigger+window, which must read provably even before Sol/
        Modrenik's art lands."""
        spec = self._skin.weekday_set
        name, asset = thirteenth_plate(key)
        center_size = (
            2 * ctx.radius * spec.center_scale
            if spec.display_mode == "center_only"
            else weekday_body_size(ctx.skin, ctx.radius)
        )
        center_size *= hover_factor(ctx, "thirteenth")
        painter.save()
        painter.setOpacity(1.0)
        if asset is not None:
            draw_pixmap_centered(painter, ctx, asset, QPointF(0, 0), center_size)
        if asset is None or ctx.skin.show_weekday_names:
            draw_name_label(
                painter, name, QPointF(0, 0),
                name_label_px(
                    name, center_size * defaults.NAME_LABEL_WIDTH_FRACTION
                ),
            )
        painter.restore()


def archetype_label_set_px(
    ctx: RenderContext, key: str, arm_width: float,
) -> int:
    """The SET-UNIFORM label size (owner verdict 2026-07-18, ROADMAP
    15h) for ONE archetype layout: every name — the arm figures AND the
    center, kept in the SAME set on purpose (owner's slika showed the
    center joining the arms' ring for uniformity) — wears the size of
    the SMALLEST fitted member. A pure, cheap (text measurement only)
    function so ArchetypeLayer (DAILY) and ArchetypeCenterLayer
    (MINUTE) — two separate paint passes — agree on one size without
    sharing mutable state."""
    target = arm_width * defaults.NAME_LABEL_WIDTH_FRACTION
    fits = [name_label_px(fig["name"], target) for fig in archetypes.figures(key)]
    center = archetypes.center(key)
    if center is not None:
        center_height = archetype_figure_size(ctx.skin, ctx.radius, center["file"])
        fits.append(
            name_label_px(
                center["name"], center_height * defaults.NAME_LABEL_WIDTH_FRACTION,
            )
        )
    return min(fits)


class ArchetypeLayer(Layer):
    """THE ARCHETYPE MODE's arm figures (owner sealed package
    2026-07-16): each diamond carries its archetype's stained glass,
    scaled into the arm with the color visible around it, at the romb
    center — the same radius the weekday-by-colors unit rides. The
    figure whose HOUR-SPACE holds the hour hand (ctx.archetype_lit)
    draws FULL; the rest ghost at the weekday ghost opacity — an
    ARCHETYPE CLOCK, not a gallery. During the reveal window every
    figure is full (the "show me everything" gesture). With Names on
    the LIT figure carries its display name (all of them during the
    reveal); missing/placeholder art always falls back to the name.
    DAILY cadence — the lit index keys the composite exactly like the
    Calendar's shichen wedge."""

    cadence = Cadence.DAILY
    # The lit figure, the reveal window and the hover-enlarge all change
    # the figures, so the compositor draws this layer LIVE, never in the
    # cached composite (owner 2026-07-17, ROADMAP 15f).
    hover_variable = True

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        key = archetype_key(ctx.skin)
        if key is None:
            return
        orbit = ctx.radius * weekday_body_orbit(ctx.skin)
        tip = ctx.radius * ctx.skin.star.radius_fraction
        half = arm_half_deg(ctx.skin)         # Cube look widens the arms
        arm_width = tip * math.tan(math.radians(half))   # diamond's widest
        # The archetype names switch is now its OWN Settings on/off
        # (owner 2026-07-18, ROADMAP 15h — replaces the buried menu twin
        # that shared `show_weekday_names`).
        names_on = ctx.skin.archetype_names
        # SET-UNIFORM label size (owner verdict 2026-07-18): computed
        # ONCE per paint for the whole layout (arms AND the center),
        # never per label — the hover-enlarged twin scales this base.
        label_px = archetype_label_set_px(ctx, key, arm_width)
        for index, fig in enumerate(archetypes.figures(key)):
            # Per-arm hover target (owner slika 8): the base pass skips
            # the hovered figure, the HoverLift twin redraws it enlarged
            # above — exactly like the slots.
            element = f"archetype:{index}"
            if not self._gate(ctx, element):
                continue
            lit = ctx.reveal_active or index == ctx.archetype_lit
            hf = hover_factor(ctx, element)
            # THE UNIVERSAL ROTATION CONVENTION (owner decree
            # 2026-07-20): a figure that opted in (currently the
            # Tetramorph alone) resolves its file fresh every paint —
            # ArchetypeLayer is hover_variable/painted LIVE already, so
            # a day change re-resolves with no extra invalidation.
            if fig.get("rotates"):
                resolved = defaults.rotating_art_file(
                    fig["file"], ctx.day.local_date
                )
                if resolved is not None:
                    fig = {**fig, "file": resolved}
            # THE TWO-TYPE LAW (owner decree 2026-07-18, round two): each
            # figure's OWN art aspect decides CIRCLE (the slot size) vs
            # PORTRAIT (the per-pointer lancet fraction) — classified
            # per figure, not once for the whole layout.
            height = archetype_figure_size(ctx.skin, ctx.radius, fig["file"])
            draw_archetype_figure(
                painter, ctx, fig,
                dial_point(fig["angle"] + ctx.rotation, orbit),
                height * hf,
                1.0 if lit else ctx.skin.weekday_set.ghost_opacity,
                named=names_on and lit,
                label_px=label_px * hf,
            )


class ArchetypeCenterLayer(Layer):
    """The archetype's CENTER — the Eye / the Hearth / the Seal / the
    Union / the Throne (the Compass has none) — drawn where the
    weekday center body used to live: ABOVE the hands. Placeholder art
    falls back to the center's name; the hover-enlarge lift twin
    joins HoverLiftLayer under the "archetype:center" element. THE
    WINDOW (owner seal 2026-07-18): it burns FULL only while the hour
    hand stands within `ARCHETYPE_CENTER_WINDOW_DEG` of TRUE solar noon
    OR solar midnight (`archetype_center_lit`) — 4 of the 24 hours — and
    draws at the weekday `ghost_opacity` the rest of the day, exactly
    like an un-lit arm figure; the reveal window ("show me everything")
    still forces it full regardless."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        key = archetype_key(ctx.skin)
        if key is None:
            return
        center = archetypes.center(key)
        if center is None or not self._gate(ctx, "archetype:center"):
            return
        # THE TWO-TYPE LAW (owner decree 2026-07-18, round two): the
        # center follows its OWN art's type — `archetype_figure_size`
        # classifies it exactly like an arm figure (circle = the slot
        # size, portrait = the lancet fraction) — no longer the weekday
        # Sun's center_scale, and the reveal window can no longer resize
        # it (the helper has no reveal term).
        height = (
            archetype_figure_size(ctx.skin, ctx.radius, center["file"])
            * hover_factor(ctx, "archetype:center")
        )
        # THE WINDOW (owner seal 2026-07-18): full at solar noon/midnight
        # (±ARCHETYPE_CENTER_WINDOW_DEG), ghost otherwise — the reveal
        # gesture overrides regardless (short-circuits before touching
        # ctx.tick, which the compositor guarantees on this MINUTE layer).
        lit = ctx.reveal_active or archetype_center_lit(
            ctx.tick.hour_angle, ctx.day.star_rotation
        )
        opacity = 1.0 if lit else ctx.skin.weekday_set.ghost_opacity
        painter.save()
        painter.setOpacity(opacity)
        if archetype_art_ready(center["file"]):
            draw_pixmap_centered(
                painter, ctx, center["file"], QPointF(0, 0), height
            )
        else:
            # SET-UNIFORM label size (owner verdict 2026-07-18): the
            # SAME pure computation ArchetypeLayer uses (the center
            # shares the arms' set), agreeing on one size across the
            # two separate paint passes without shared state.
            tip = ctx.radius * ctx.skin.star.radius_fraction
            half = arm_half_deg(ctx.skin)
            arm_width = tip * math.tan(math.radians(half))
            label_px = (
                archetype_label_set_px(ctx, key, arm_width)
                * hover_factor(ctx, "archetype:center")
            )
            draw_name_label(painter, center["name"], QPointF(0, 0), label_px)
        painter.restore()


def octa_slot_art(folder: str, name: str) -> Path | None:
    """The PNG for an image slot style — `folder` is a subdirectory of
    assets/calendars/ (the RESTRUCTURE 2026-07-22 home; the old
    assets/zodiac/ root is abolished): "zodiac/astrology/primary/sign",
    ".../logo", ".../constellation", "zodiac/chinese/primary/bronze",
    "zodiac/chinese/primary/colored" — the family/variant tree. `name` is the
    entity ("Cancer" / "Horse") — or None while the owner's art folder
    does not have it yet."""
    path = paths.art_file(defaults.ZODIAC_ART_DIR / folder / f"{name}.png")
    return path if path.exists() else None


def slot_text(mode: str, ctx: RenderContext) -> str:
    """The INFO TEXT of a slot's time/date/day-length mode — shared by
    the info slot and the day slot's text modes (Rule #5)."""
    if mode == "time":
        return ctx.tick.time_hm
    if mode == "date":
        return f"{ctx.day.local_date.day} {ctx.day.local_date:%b}"
    return ctx.day.day_length            # "day_length" (validated set)


def display_year(ctx: RenderContext) -> str:
    """Today's year for the COMPACT dial texts (the date
    complication's year row, the Earth marker's deep-travel row): the
    OFFICIAL form only — the subdials cannot carry the full paired
    line; the Anno Lucis pairing lives in the hovers/legends
    (compositor, owner amendment 2026-07-17). The real astronomical
    year un-shifts the deep proxy frame first."""
    return format_official(
        real_year(ctx.day.local_date.year, ctx.day.deep_cycles),
        ctx.skin.era_notation,
        ctx.skin.show_era_suffix,
    )


def _draw_subdial_shadow(
    painter: QPainter, pos: QPointF, diameter: float
) -> None:
    """The subdial's LIVE shadow (owner 2026-07-15: the sun lives at
    the dial center, the shadow is rendered — never baked; reaffirmed
    under Rule #19, 2026-07-20 — this one function is WHY the
    twelve-plate seat/finish sheet was pure waste): offset OUTWARD
    from the center — the seat's own dial angle, south straight down,
    an arm seat toward its own outward corner — symmetric on the
    center seat (distance 0, no offset at all)."""
    distance = math.hypot(pos.x(), pos.y())
    if distance > 1.0:
        offset = diameter * defaults.SUBDIAL_SHADOW_OFFSET_FRACTION
        shifted = QPointF(
            pos.x() + pos.x() / distance * offset,
            pos.y() + pos.y() / distance * offset,
        )
    else:
        shifted = pos
    radius = diameter / 2.0 * defaults.SUBDIAL_SHADOW_SPREAD
    gradient = QRadialGradient(shifted, radius)
    shade = QColor(*palette.SUBDIAL_SHADOW_RGBA)
    gradient.setColorAt(0.75, shade)
    fade = QColor(shade)
    fade.setAlpha(0)
    gradient.setColorAt(1.0, fade)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawEllipse(shifted, radius, radius)
    painter.restore()


def draw_slot_roundel(
    painter: QPainter, ctx: RenderContext, pos: QPointF, diameter: float
) -> None:
    """The watch-face SUBDIAL behind flat slot content (owner
    2026-07-14) — worn by every text mode and by the flat astrology
    art (sign / logo / constellation); the circular plates
    (medallions, planets, colored badges) stay bare. THE MASTER (Rule
    #19, owner decree 2026-07-20) draws whenever it exists — a missing
    finish is RECOLORED from it live — under a LIVE outward shadow
    keyed off THIS seat's own dial position (owner 2026-07-15: one
    master plate, the code paints the metals and the light; the seat
    never reaches the FILE any more, only the shadow). The "theme"
    plate style (owner A/B spec) colorizes the tapisserie field to
    the clock tint; "black" keeps the standard dark field. With no
    art at all: the procedural circle, the ring's own face color
    rimmed in the finish metal."""
    _draw_subdial_shadow(painter, pos, diameter)
    plate = subdial_plate_file(
        ctx.skin.ring_finish,
        tint=(
            ctx.skin.ring_tint
            if ctx.skin.subdial_style == "theme"
            else None
        ),
    )
    if plate is not None:
        draw_pixmap_centered(painter, ctx, plate, pos, diameter)
        return
    rim = QColor(
        palette.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish]
    )
    width = max(1.5, diameter * defaults.SLOT_ROUNDEL_BORDER_FRACTION)
    painter.save()
    painter.setPen(QPen(rim, width))
    painter.setBrush(ring_face_color(paths.art_file(ctx.skin.ring.asset)))
    inner = (diameter - width) / 2.0
    painter.drawEllipse(pos, inner, inner)
    painter.restore()


def _finish_color(ctx: RenderContext) -> QColor:
    """The letter-finish metal color — the ONE hue of every subdial
    accent: the mini hand, the theme-style ticks and all complication
    texts (owner 2026-07-15: 'u boji kao i kazaljka')."""
    return QColor(
        palette.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish]
    )


def draw_shadowed_text(
    painter: QPainter, center: QPointF, text: str, font: QFont,
    color: QColor,
) -> None:
    """A finish-colored label over a DROP SHADOW (owner 2026-07-15:
    subdial texts are never white — the metal color like the hand,
    shadowed so they read on both plate styles)."""
    metrics = QFontMetricsF(font)
    baseline = QPointF(
        center.x() - metrics.horizontalAdvance(text) / 2,
        center.y() + (metrics.ascent() - metrics.descent()) / 2,
    )
    path = QPainterPath()
    path.addText(baseline, font, text)
    offset = max(
        1.0,
        font.pixelSize() * defaults.SUBDIAL_TEXT_SHADOW_OFFSET_FRACTION,
    )
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(*palette.SUBDIAL_TEXT_SHADOW_RGBA))
    painter.drawPath(path.translated(offset, offset))
    painter.setBrush(color)
    painter.drawPath(path)
    painter.restore()


def draw_fitted_text(
    painter: QPainter, ctx: RenderContext, pos: QPointF,
    slot_size: float, text: str,
) -> None:
    """Fit-to-width slot text in the finish metal over a shadow: the
    largest bold font whose text spans the slot's width fraction —
    measured, not guessed, so it never overflows (Rule #5)."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(100)
    advance = QFontMetricsF(font).horizontalAdvance(text)
    target = slot_size * defaults.TIME_TEXT_WIDTH_FRACTION
    font.setPixelSize(
        max(defaults.BODY_LABEL_MIN_PX, math.floor(100.0 * target / advance))
    )
    draw_shadowed_text(painter, pos, text, font, _finish_color(ctx))


def draw_two_lines(
    painter: QPainter, ctx: RenderContext, pos: QPointF,
    slot_size: float, top: str, bottom: str,
) -> None:
    """Two stacked finish-metal lines sharing one fit-to-width font —
    the Chinese year ("Fire" / "Horse"), the Ascendant ("Ascendant" /
    "Virgo") and the two-row date ("14 Jul" / "2026") (Rule #5)."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(100)
    widest = max(
        QFontMetricsF(font).horizontalAdvance(line)
        for line in (top, bottom)
    )
    target = slot_size * defaults.TIME_TEXT_WIDTH_FRACTION
    font.setPixelSize(
        max(defaults.BODY_LABEL_MIN_PX, math.floor(100.0 * target / widest))
    )
    offset = font.pixelSize() * 0.62
    color = _finish_color(ctx)
    draw_shadowed_text(
        painter, QPointF(pos.x(), pos.y() - offset), top, font, color
    )
    draw_shadowed_text(
        painter, QPointF(pos.x(), pos.y() + offset), bottom, font, color
    )


def draw_small_seconds(
    painter: QPainter, ctx: RenderContext, pos: QPointF, diameter: float
) -> None:
    """The SMALL-SECONDS complication (owner 2026-07-14): the active
    set's own seconds hand rotating inside the subdial, behind eight
    tick marks just inside the rim — four LARGER at the cardinal
    points, four smaller between them. Colors (owner 2026-07-15 A/B
    spec): the hand ALWAYS wears the letter-finish metal over its own
    drop shadow; the ticks are white on the "black" plate style and
    finish-colored on the "theme" style — shadowed either way."""
    spec = ctx.skin.hands.second
    radius = diameter / 2.0
    outer = radius * defaults.SMALL_SECONDS_TICK_OUTER_FRACTION
    tick_color = (
        _finish_color(ctx)
        if ctx.skin.subdial_style == "theme"
        else QColor(*palette.SMALL_SECONDS_TICK_RGBA)
    )
    painter.save()
    painter.translate(pos)
    for step in range(8):
        major = step % 2 == 0
        length = radius * (
            defaults.SMALL_SECONDS_TICK_MAJOR_FRACTION
            if major
            else defaults.SMALL_SECONDS_TICK_MINOR_FRACTION
        )
        width = max(1.0, radius * (0.07 if major else 0.05))
        angle = math.radians(step * 45.0)
        ux, uy = math.sin(angle), -math.cos(angle)
        start = QPointF(ux * (outer - length), uy * (outer - length))
        end = QPointF(ux * outer, uy * outer)
        shadow = QPointF(width * 0.35, width * 0.35)
        painter.setPen(QPen(
            QColor(*palette.SMALL_SECONDS_TICK_SHADOW_RGBA), width,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
        ))
        painter.drawLine(start + shadow, end + shadow)
        painter.setPen(QPen(
            tick_color, width,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
        ))
        painter.drawLine(start, end)
    if spec is not None:
        # The mini hand — the pack's own seconds hand, pivot math
        # identical to the big HandLayer, tip inside the tick ring —
        # in the FINISH metal (never the clock tint) over a drop
        # shadow (owner 2026-07-15).
        tip_units = spec.natural_height - spec.pivot_y
        target_tip = outer - radius * 0.06
        height = spec.natural_height * (target_tip / tip_units)
        pixmap = ctx.cache.pixmap_by_height(
            spec.asset, height, ctx.dpr,
            tint=palette.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish],
            desaturate=ctx.skin.hands.desaturate,
        )
        silhouette = ctx.cache.pixmap_by_height(
            spec.asset, height, ctx.dpr, tint=palette.SHADOW_STAMP_TINT,
            desaturate=ctx.skin.hands.desaturate,
        )
        logical_w = pixmap.width() / ctx.dpr
        pivot_x = logical_w * (
            0.5 if spec.pivot_x_fraction is None else spec.pivot_x_fraction
        )
        offset = radius * defaults.SMALL_SECONDS_HAND_SHADOW_OFFSET_FRACTION
        painter.rotate(ctx.tick.second_angle)
        painter.setOpacity(defaults.SMALL_SECONDS_HAND_SHADOW_OPACITY)
        painter.drawPixmap(
            QPointF(-pivot_x + offset, -target_tip + offset), silhouette
        )
        painter.setOpacity(1.0)
        painter.drawPixmap(QPointF(-pivot_x, -target_tip), pixmap)
    painter.restore()


def earth_region(latitude: float, default: str) -> str:
    """The Earth marker's ART REGION: the active location's continent
    — except at extreme latitudes, where the planet honestly shows its
    POLE (owner 2026-07-15: the Quick Jump flips onto the poles). The
    latitude rides the day context, so a running simulation carries
    its own observer here."""
    if latitude >= defaults.EARTH_POLE_LATITUDE:
        return "north_pole"
    if latitude <= -defaults.EARTH_POLE_LATITUDE:
        return "south_pole"
    return default


class YearMarkerLayer(Layer):
    """Date markers along the INSIDE of the dial. Earth rides the year
    wheel (summer solstice at the top); the Moon rides its own cycle (new
    moon at the top, full at the bottom, clockwise) showing the current
    illumination. The Elements switches pick which of the two is drawn."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        if ctx.skin.show_earth and self._gate(ctx, "earth"):
            self._draw_earth(painter, ctx)
        if ctx.skin.show_moon and self._gate(ctx, "moon"):
            moon_angle = angles.moon_cycle_angle(ctx.tick.moon_fraction)
            # The rim transit only exists while the Earth is also shown.
            opacity = (
                moon_transit_opacity(spec, ctx.tick.year_angle, moon_angle)
                if ctx.skin.show_earth
                else 1.0
            )
            if not ctx.tick.is_moon_up:
                # Below the horizon the marker DIMS (owner spec
                # 2026-07-12; the Settings ▸ Opacity slider).
                opacity *= spec.moon_hidden_alpha
            factor = hover_factor(ctx, "moon")
            # During its ±6 h event window the Moon RELOCATES radially to
            # the ring band centerline (owner 2026-07-16), keeping its
            # cycle angle, so the SILVER halo straddles the ring. A LUNAR
            # eclipse (ROADMAP 15h item 11) rides the SAME relocation with
            # the blood-moon BRONZE glow instead, scaled by its magnitude,
            # and darkens the disc.
            eclipse = ctx.tick.eclipse_event
            lunar_eclipse = (
                eclipse if eclipse is not None and eclipse.kind == "lunar" else None
            )
            lunar_state = (
                eclipse_render_state(lunar_eclipse)
                if lunar_eclipse is not None
                else None
            )
            glowing = ctx.tick.moon_event is not None or lunar_state is not None
            orbit = (
                defaults.GLOW_RING_RADIUS_FRACTION
                if glowing
                else spec.moon_orbit_fraction
            )
            pos = dial_point(moon_angle, ctx.radius * orbit)
            if glowing:
                color = (
                    palette.GLOW_ECLIPSE_LUNAR_COLOR
                    if lunar_state is not None
                    else palette.GLOW_MOON_COLOR
                )
                strength = (
                    eclipse_state_glow_strength(lunar_state, lunar_eclipse.magnitude)
                    if lunar_state is not None
                    else 1.0
                )
                # INVISIBLE-FROM-HERE muting (owner verdict "može", fix
                # round E, 2026-07-19): the event is real (the disc
                # darkening/art swap below stay untouched) but the
                # observer cannot actually see it — mute the glow to a
                # desaturated silver at half strength instead.
                if lunar_state is not None and not lunar_eclipse.visible:
                    color = palette.GLOW_ECLIPSE_INVISIBLE_COLOR
                    strength *= defaults.ECLIPSE_INVISIBLE_STRENGTH_FACTOR
                draw_event_glow(
                    painter,
                    pos,
                    ctx.radius * spec.moon_scale * factor,
                    color,
                    strength,
                    fringe_color=(
                        palette.ECLIPSE_LUNAR_FRINGE_COLOR
                        if lunar_state is not None
                        and defaults.ECLIPSE_STATE_FRINGE[lunar_state]
                        else None
                    ),
                )
            painter.save()
            painter.setOpacity(painter.opacity() * opacity)
            self._draw_moon(
                painter, ctx, pos, 2 * ctx.radius * spec.moon_scale * factor,
                darken_state=lunar_state,
            )
            painter.restore()

    def _draw_earth(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        # The Calendar's ALMANAC wheel carries its OWN real-calendar year
        # mapping (owner 2026-07-16): the Earth marker rides the month
        # wedges (one tick ≈ one day) instead of the shared six-anchor
        # season wheel — every OTHER pointer, the Zodiac wheel included,
        # keeps the shared wheel.
        almanac = (
            ctx.skin.pointer == "calendar"
            and calendar_wheel(ctx.skin) == "almanac"
        )
        year_angle = (
            almanac_marker_angle(ctx.day.local_date)
            if almanac
            else ctx.tick.year_angle
        )
        # During its ±12 h event window the Earth RELOCATES radially to the
        # ring band centerline (owner 2026-07-16), keeping its year-wheel
        # angle, so the GOLDEN halo straddles the ring. A SOLAR eclipse
        # (ROADMAP 15h item 11) rides the SAME relocation with the RED
        # glow instead, scaled by its magnitude, and swaps the Earth's
        # art to the Planets theme's Eclipsed-Sun dual.
        eclipse = ctx.tick.eclipse_event
        solar_eclipse = (
            eclipse if eclipse is not None and eclipse.kind == "solar" else None
        )
        glowing = ctx.tick.season_event is not None or solar_eclipse is not None
        orbit = (
            defaults.GLOW_RING_RADIUS_FRACTION if glowing else spec.orbit_fraction
        )
        pos = dial_point(year_angle, ctx.radius * orbit)
        size = 2 * ctx.radius * spec.scale * hover_factor(ctx, "earth")
        if glowing:
            solar_state = (
                eclipse_render_state(solar_eclipse)
                if solar_eclipse is not None
                else None
            )
            if solar_state is None:
                color = palette.GLOW_SUN_COLOR
                strength = 1.0
            else:
                color = (
                    palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
                    if solar_state == "solar_annular"
                    else palette.GLOW_ECLIPSE_SOLAR_COLOR
                )
                strength = eclipse_state_glow_strength(
                    solar_state, solar_eclipse.magnitude
                )
                # INVISIBLE-FROM-HERE muting (owner verdict "može", fix
                # round E, 2026-07-19) — same rule as the lunar marker.
                if not solar_eclipse.visible:
                    color = palette.GLOW_ECLIPSE_INVISIBLE_COLOR
                    strength *= defaults.ECLIPSE_INVISIBLE_STRENGTH_FACTOR
            draw_event_glow(painter, pos, size / 2, color, strength)
        if almanac:
            # The day-ARROW at the marker's exact tick (owner 2026-07-16):
            # a small procedural triangle pointing from inside the dial
            # OUTWARD at the ring, so the ring reads today's date.
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(palette.CALENDAR_ARROW_COLOR))
            painter.drawPolygon(calendar_day_arrow(year_angle, ctx.radius))
            painter.restore()
        variant = (
            f"{ctx.skin.earth_style}_"
            f"{earth_region(ctx.day.latitude, spec.default_variant)}_"
            f"{'day' if ctx.tick.is_daylight else 'night'}"
        )
        asset = (
            defaults.ECLIPSE_SOLAR_ART
            if solar_eclipse is not None
            else spec.variants.get(variant)
        )
        if asset is not None:
            # The Earth renders ship on an opaque space background — clip
            # to the marker disc so only the globe shows.
            clip = QPainterPath()
            clip.addEllipse(pos, size / 2, size / 2)
            painter.save()
            painter.setClipPath(clip)
            draw_pixmap_centered(painter, ctx, asset, pos, size)
            painter.restore()
            if (
                2 * ctx.radius >= defaults.FULL_TEXT_MIN_DIAMETER
                and ctx.skin.earth_label != "off"
            ):
                # The Earth label — FOUR exclusive modes (owner
                # 2026-07-18: Date / Weekday / Date & Weekday / Full
                # Date) — never fits below the full-text threshold anyway.
                self._draw_earth_label(painter, ctx, pos, size)
        else:
            color = spec.day_color if ctx.tick.is_daylight else spec.night_color
            painter.setPen(
                QPen(
                    QColor(*palette.MARKER_BORDER_RGBA),
                    max(1.0, size * defaults.MARKER_BORDER_WIDTH),
                )
            )
            painter.setBrush(QColor(color))
            painter.drawEllipse(pos, size / 2, size / 2)

    def _draw_earth_label(self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float) -> None:
        """The Earth marker's text — FOUR exclusive modes (owner
        2026-07-18, the Design ▸ Earth submenu: Date / Weekday / Date &
        Weekday / Full Date), stored as `skin.earth_label`: "weekday"
        writes "FRI" centered (must work without the date); "date"
        writes "8 Jul" centered; "date_weekday" stacks the date over the
        abbreviated weekday (the OLD combined "Full Date" meaning,
        renamed); "full" stacks the date over the YEAR — the TRUE Full
        Date, reusing `display_year` (already un-shifts a deep-travel
        proxy frame), the same two-row shape the deep-travel year already
        uses on this marker. During a DEEP travel (Session 16, deep proxy
        frame active) the YEAR row OUTRANKS the weekday in "date_weekday"
        mode — far from the present the marker must say WHEN; "full"
        mode already shows the year, so a deep travel is a no-op
        difference there."""
        bold_font = QFont()
        bold_font.setBold(True)
        deep_travel = ctx.day.deep_cycles != 0
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        mode = ctx.skin.earth_label
        if mode == "weekday":
            # Weekday ALONE — a single centered row (owner: "FRI" must work
            # without the date). Uses the date font size (it is the only
            # row, so it gets the full label size).
            bold_font.setPixelSize(
                max(
                    defaults.BODY_LABEL_MIN_PX,
                    round(size * defaults.EARTH_DATE_TEXT_SIZE),
                )
            )
            draw_outlined_text(
                painter, pos, constants.WEEKDAY_LABELS[today], bold_font
            )
            return
        # "date", "date_weekday" and "full" all lead with the date row.
        text = f"{ctx.day.local_date.day} {ctx.day.local_date:%b}"
        bold_font.setPixelSize(
            max(defaults.BODY_LABEL_MIN_PX, round(size * defaults.EARTH_DATE_TEXT_SIZE))
        )
        if mode == "full":
            second_row = display_year(ctx)
        elif mode == "date_weekday":
            second_row = (
                display_year(ctx) if deep_travel
                else constants.WEEKDAY_LABELS[today]
            )
        else:
            second_row = None
        if second_row is None:
            draw_outlined_text(painter, pos, text, bold_font)
            return
        offset = size * archetypes.ARCHETYPE_EARTH_DAY_OFFSET
        draw_outlined_text(
            painter, QPointF(pos.x(), pos.y() - offset), text, bold_font
        )
        row_font = QFont()
        row_font.setPixelSize(
            max(
                defaults.BODY_LABEL_MIN_PX,
                round(size * archetypes.ARCHETYPE_EARTH_DAY_TEXT_SIZE),
            )
        )
        row_font.setBold(True)
        draw_outlined_text(
            painter, QPointF(pos.x(), pos.y() + offset), second_row,
            row_font,
        )

    def _draw_moon(
        self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float,
        darken_state: str | None = None,
    ) -> None:
        """Moon image (or procedural disc) with the unlit part shadowed:
        the lit region is the half-disc on the lit side combined with the
        terminator half-ellipse (semi-axis a = R*|cos 2pi*f|) — union when
        gibbous, difference when crescent; everything else is darkened.

        `darken_state` (a LUNAR eclipse render STATE, fix round C
        2026-07-19 — `render.layers.eclipse_render_state`) is a TRUE
        brightness reduction of the WHOLE disc — lit and unlit halves
        alike, since totality dims the full face — via
        `QPainter.CompositionMode_Multiply` against an OPAQUE gray whose
        value is `defaults.ECLIPSE_STATE_MOON_BRIGHTNESS[darken_state]`
        (0..1 of full value). Multiplying by a NEUTRAL gray scales R/G/B
        equally, i.e. it is exactly "value down" with the hue untouched —
        the owner's fix for the old translucent bronze wash
        (`SourceOver` at a magnitude-scaled alpha), which let a bright
        moon bleed through and read as "still shining, just tinted".
        Fully opaque, TYPE-driven only — magnitude never reaches here."""
        spec = self._skin.year_marker
        fraction = ctx.tick.moon_fraction
        radius = size / 2
        painter.save()
        painter.translate(pos)
        if ctx.day.southern_hemisphere:
            # From the southern hemisphere the moon appears upside down —
            # the lit side swaps left/right (owner spec).
            painter.rotate(180.0)
        painter.setPen(Qt.PenStyle.NoPen)

        if spec.moon_asset is not None:
            draw_pixmap_centered(painter, ctx, spec.moon_asset, QPointF(0, 0), size)
        else:
            painter.setBrush(QColor(spec.moon_dark_color))
            painter.drawEllipse(QPointF(0, 0), radius, radius)

        lit = moon_lit_region(fraction, radius)

        if spec.moon_asset is not None:
            disc = QPainterPath()
            disc.addEllipse(QRectF(-radius, -radius, size, size))
            shadow = QColor(spec.moon_dark_color)
            shadow.setAlphaF(spec.moon_shadow_alpha)
            painter.fillPath(disc.subtracted(lit), shadow)
        else:
            painter.fillPath(lit, QColor(spec.moon_lit_color))
        if darken_state is not None:
            disc = QPainterPath()
            disc.addEllipse(QRectF(-radius, -radius, size, size))
            brightness = defaults.ECLIPSE_STATE_MOON_BRIGHTNESS[darken_state]
            value = round(255 * brightness)
            # BLOOD MOON (owner verdict "može", fix round E, 2026-07-19):
            # TOTAL alone wears a deep COPPER tone instead of neutral
            # gray — `tinted_gray`'s tritone at this brightness reads
            # dark AND red-dominant; partial/penumbral stay neutral.
            tint = (
                palette.ECLIPSE_TOTAL_MOON_TINT
                if darken_state == "lunar_total"
                else None
            )
            painter.save()
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_Multiply
            )
            painter.fillPath(disc, tinted_gray(value, tint))
            painter.restore()
        painter.restore()


class HoverLiftLayer(Layer):
    """The hover Z-LIFT (owner 2026-07-13: "kad radim hover hoću da u
    trenutku enlarge bude iznad kazaljki"): stacked LAST, it repaints
    ONLY the hovered element through lift=True twins of the element
    layers — each base layer skips its hovered element via
    Layer._gate, so nothing draws twice."""

    cadence = Cadence.MINUTE

    def __init__(self, skin: SkinDefinition):
        super().__init__(skin)
        self._twins = (
            WeekdayLayer(skin, lift=True),
            SlotLayer(skin, lift=True),
            YearMarkerLayer(skin, lift=True),
            # The archetype ARM figures and the CENTER enlarge like the
            # slots and the old center body (owner 2026-07-16/17) — both
            # inert off the mode.
            ArchetypeLayer(skin, lift=True),
            ArchetypeCenterLayer(skin, lift=True),
        )

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        if not ctx.hovered:
            return
        for twin in self._twins:
            twin.paint(painter, ctx)


class HandLayer(Layer):
    """One class, three instances — rotates a hand image about its
    pack-defined PIVOT (owner spec 2026-07-12). Sizing uses
    TIP-TO-PIVOT lengths only: the seconds tip reaches the ring
    (second_reach_fraction), the minutes tip the minute arrows
    (minute_reach_fraction) and the hours follow the pack's own
    hours/minutes tip ratio — the counterweight below the pivot just
    comes along at the same scale."""

    cadence = Cadence.MINUTE

    def __init__(self, skin: SkinDefinition, kind: str):
        super().__init__(skin)
        self._kind = kind

    @property
    def _spec(self) -> HandSpec:
        hands = self._skin.hands
        return {"hour": hands.hour, "minute": hands.minute, "second": hands.second}[
            self._kind
        ]

    def _tip_reach_fraction(self) -> float:
        """The dial-radius fraction this hand's TIP must touch."""
        hands = self._skin.hands
        if self._kind == "second":
            return hands.second_reach_fraction
        if self._kind == "minute":
            return hands.minute_reach_fraction
        hour_tip = hands.hour.natural_height - hands.hour.pivot_y
        minute_tip = hands.minute.natural_height - hands.minute.pivot_y
        return hands.minute_reach_fraction * hour_tip / minute_tip

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._spec
        angle = {
            "hour": ctx.tick.hour_angle,
            "minute": ctx.tick.minute_angle,
            "second": ctx.tick.second_angle,
        }[self._kind]
        tip_units = spec.natural_height - spec.pivot_y
        target_tip = self._tip_reach_fraction() * ctx.radius
        height = spec.natural_height * (target_tip / tip_units)
        # The hands follow the clock tint (owner spec: one hue recolors
        # the whole body); colored USER art is desaturated first so the
        # tint has gray to work on.
        pixmap = ctx.cache.pixmap_by_height(
            spec.asset, height, ctx.dpr, tint=ctx.skin.ring_tint,
            desaturate=self._skin.hands.desaturate,
        )
        logical_w = pixmap.width() / ctx.dpr
        pivot_x = logical_w * (
            0.5 if spec.pivot_x_fraction is None else spec.pivot_x_fraction
        )
        painter.save()
        painter.rotate(angle)
        painter.drawPixmap(QPointF(-pivot_x, -target_tip), pixmap)
        painter.restore()
