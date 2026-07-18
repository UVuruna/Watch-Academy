"""The seven dial layers (closed set) with cadence-driven caching.

Every layer paints in a coordinate system whose origin is the dial
center; dial angles are degrees CLOCKWISE from the top (the core
convention), converted to Qt's counterclockwise-from-3-o'clock only
inside the pie/position helpers here.
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
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

from config import archetypes, constants, defaults, paths
from core import angles
from core.clock_state import DayContext, TickState
from core.deep_time import format_official, real_year
from core.sun import DaylightRegime, SunDay
from core.year_wheel import almanac_marker_angle
from render.assets import AssetCache, ring_face_color, subdial_plate_file
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
    calendar_lit: int | None = None  # Calendar pointer: the wedge index
                                     # (0..11 from the top) that LIGHTS —
                                     # the compositor computes it from the
                                     # live tick (the shichen changes intraday,
                                     # so it also keys the DAILY composite)
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
    metal: str | None = None,
) -> None:
    """Asset rasterized to `height` and drawn centered at `pos` — the one
    shared image path of weekday bodies and the year marker (Rule #5).
    `tint` tritone-maps the image; `desaturate` grays it first;
    `metal` runs the hue-SELECTIVE bronze-to-gold/silver swap (only the
    warm bronze pixels change — owner insight 2026-07-12)."""
    pixmap = ctx.cache.pixmap_by_height(
        asset, height, ctx.dpr, tint, desaturate, metal
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
    painter.setPen(QPen(QColor(*defaults.LABEL_OUTLINE_RGBA), outline_width))
    painter.setBrush(QColor(*defaults.LABEL_FILL_RGBA))
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
    """The active Star+Aura palette — ONE source for both the star
    diamonds and the background wedges (owner spec): the user's custom
    hues when set (settings dialog), otherwise the owner preset."""
    if skin.palette_override is not None:
        return skin.palette_override
    return defaults.PALETTE_PRESETS[(skin.pointer, skin.palette_style)]


def calendar_wheel(skin: SkinDefinition) -> str:
    """Which of the Calendar's two wheels is active (owner 2026-07-16):
    the palette_style CARRIES the wheel — paint = the Zodiac Dozen,
    light = the Almanac (Month) Dozen."""
    return "zodiac" if skin.palette_style == "paint" else "almanac"


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


def calendar_lit_index(
    skin: SkinDefinition, lighting: str, hour_angle: float, day: DayContext
) -> int:
    """Which wedge (0..11 from the top) LIGHTS (owner 2026-07-16). "hour"
    — the wedge containing the HOUR HAND (the Chinese double-hour): on
    the Zodiac its own boundary geometry (floor), on the Almanac the
    axis-centered geometry (round). "year" — the current SIGN's wedge on
    the Zodiac (Cancer = 0, aligned with the year wheel), the current
    MONTH's wedge on the Almanac."""
    step = constants.CALENDAR_WEDGE_DEG
    wheel = calendar_wheel(skin)
    if lighting == "hour":
        if wheel == "zodiac":
            return int(hour_angle // step) % 12
        return int((hour_angle + step / 2.0) // step) % 12
    if wheel == "zodiac":
        names = [name for name, _ in constants.ZODIAC_SIGNS]
        return names.index(day.zodiac_name)
    from core.year_wheel import almanac_month_index
    return almanac_month_index(day.local_date.month)


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
    painter: QPainter, pos: QPointF, marker_radius: float, color: str
) -> None:
    """Radial halo behind a year marker relocated to the ring band
    centerline during a season/moon event window (owner rework
    2026-07-16): compact — the halo diameter is twice the marker's — and
    intense, so it reads over any background while STRADDLING the ring.
    `color` is GOLDEN for the Sun's events, SILVER for the Moon's."""
    halo = marker_radius * defaults.GLOW_RADIUS_SCALE
    gradient = QRadialGradient(pos, halo)
    core = QColor(color)
    core.setAlphaF(defaults.GLOW_CORE_ALPHA)
    mid = QColor(color)
    mid.setAlphaF(defaults.GLOW_MID_ALPHA)
    edge = QColor(color)
    edge.setAlphaF(0.0)
    gradient.setColorAt(0.0, core)
    gradient.setColorAt(defaults.GLOW_MID_STOP, mid)
    gradient.setColorAt(1.0, edge)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawEllipse(pos, halo, halo)
    painter.restore()


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


def today_slot_theta(pointer: str, today: str) -> float | None:
    """Unrotated dial angle of the slot showing today's body, or None
    when today lives in the center (the hexa pointer keeps the Sun
    there)."""
    for angle, occupants in constants.POINTER_WEEKDAY_SLOTS[pointer]:
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
    pointer: str, hour_angle: float, rotation: float = 0.0
) -> int:
    """The figure whose HOUR-SPACE contains the hour hand (owner
    2026-07-16): the circle divides by arms — trio 3×8h, cross 4×6h,
    hexa 6×4h, octa 8×3h — each space CENTERED on its arm (the arm tip
    is the center of its hue, the standing convention). The spaces
    ride the drawn arms, so the solar rotation shifts them exactly as
    it shifts the diamonds; index = the figures-tuple position."""
    arms = constants.POINTER_POINTS[pointer]
    step = 360.0 / arms
    return int(round(((hour_angle - rotation) % 360.0) / step)) % arms


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


def archetype_figure_size(
    skin: SkinDefinition, radius: float, art_file,
) -> float:
    """THE ONE sizing entry for every archetype figure — arms AND center
    (owner two-type law, 2026-07-18 round two): the art divides into TWO
    TYPES by its OWN aspect ratio (width/height), classified once — no
    per-art clamp, no set-minimum.

    - CIRCLE type (aspect >= `ARCHETYPE_PORTRAIT_ASPECT_MAX` — rondels,
      medallions, the square Scale glass, and WIDE art like Saturn's
      rings) wears the SLOT size, `weekday_body_size()` — IDENTICAL to
      the weekday bodies; wide art stays height-based ON PURPOSE (owner:
      "planeta istih dimenzija kao ostale, prstenovi vire" — the ball
      matches every other circle, the rings overflow the frame,
      deliberately — no clamp).
    - PORTRAIT type (aspect < the threshold — the tall lancet vitraž
      windows: persons, temperaments) wears the per-pointer desired
      fraction of the star tip (`ARCHETYPE_FIGURE_HEIGHT_OF_TIP`),
      UNIFORM for every portrait in the set.

    Missing/placeholder art (the name-fallback path) reads CIRCLE-sized
    — there is no art to classify."""
    size = archetype_art_size(art_file)
    if size is None or (
        size.width() / size.height() >= archetypes.ARCHETYPE_PORTRAIT_ASPECT_MAX
    ):
        return weekday_body_size(skin, radius)
    tip = radius * skin.star.radius_fraction
    return tip * archetypes.ARCHETYPE_FIGURE_HEIGHT_OF_TIP[skin.pointer]


def draw_archetype_figure(
    painter: QPainter, ctx: "RenderContext", fig: dict, pos: QPointF,
    height: float, arm_width: float, opacity: float, named: bool,
) -> None:
    """One archetype figure in its diamond: the stained glass scaled
    into the arm (color visible around it) at `opacity`. `height` is
    already TYPE-CLASSIFIED (`archetype_figure_size` — circle vs
    portrait) and hover-scaled by the caller; `arm_width` is the
    diamond's widest width (for the name fit). `named` adds the display
    name in the label style. Missing/placeholder art draws the NAME
    alone — the documented fallback until the owner's glass lands."""
    painter.save()
    painter.setOpacity(opacity)
    ready = archetype_art_ready(fig["file"])
    if ready:
        draw_pixmap_centered(painter, ctx, fig["file"], pos, height)
    if named or not ready:
        _draw_archetype_name(painter, fig["name"], pos, arm_width, height)
    painter.restore()


def _draw_archetype_name(
    painter: QPainter, name: str, pos: QPointF, arm_width: float,
    figure_height: float,
) -> None:
    """The figure's name in the outlined label style, FITTED to the
    diamond's width (measured, never guessed — Melancholic must not
    overflow the slim cross arm) and capped against the figure."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(100)
    advance = QFontMetricsF(font).horizontalAdvance(name)
    target = arm_width * archetypes.ARCHETYPE_NAME_WIDTH_FRACTION
    fitted = math.floor(100.0 * target / advance)
    cap = round(figure_height * archetypes.ARCHETYPE_NAME_MAX_OF_FIGURE)
    font.setPixelSize(max(defaults.BODY_LABEL_MIN_PX, min(fitted, cap)))
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
    """True while the SERVANT face holds the 24h seat on the Compass or
    the Seasons (owner correction 2026-07-13: NOT Sunday-only — it
    stands there all week like every other body, ghosted, and turns
    opaque on Sunday: "two persons, a union"). The Trinity and the
    Prism keep one image ("two persons in one body") and speak the
    second face in the hover. Needs the CLASSIC unit up and the
    theme's dual art on disk (documented: no art, no second face)."""
    spec = skin.weekday_set
    return (
        skin.pointer in ("octa", "cross")
        and weekday_classic_slot(skin) is not None
        and spec.display_mode != "center_only"
        and spec.dual_asset is not None
        and paths.art_file(spec.dual_asset).exists()
    )


def servant_holds_the_seat(skin: SkinDefinition, today: str) -> bool:
    """Whether the Servant face WINS the 24h seat today: on the Compass
    the seat is his alone; on the Seasons he shares it with Mercury's
    slot and the standard shared-slot priority decides (the Servant
    counts as an eighth body whose day is Sunday)."""
    if not sunday_dual_face(skin):
        return False
    seat = next(
        (
            occupants
            for angle, occupants in constants.POINTER_WEEKDAY_SLOTS[skin.pointer]
            if angle == constants.SOUTH_SLOT_ANGLE
        ),
        (),
    )
    return not seat or visible_occupant(seat + ("sun",), today) == "sun"


def pie_path(radius: float, start_deg: float, end_deg: float) -> QPainterPath:
    """Clip path for the pie between two dial angles going clockwise."""
    path = QPainterPath()
    path.moveTo(0.0, 0.0)
    rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
    path.arcTo(rect, 90.0 - start_deg, -(end_deg - start_deg))
    path.closeSubpath()
    return path


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
    — or stand upright when solar rotation is off."""

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
                ctx.day.sun, palette_for(ctx.skin), spec.day_alpha,
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
        # rotation (owner spec). The wedge that LIGHTS (the shichen, or
        # the current month/sign) raises its opacity by the delta; the
        # lit index rides the RenderContext (the compositor computes it
        # from the live tick and keys the composite on it).
        if ctx.skin.pointer == "calendar":
            palette = palette_for(ctx.skin)
            wheel = calendar_wheel(ctx.skin)
            cal_radius = ctx.radius * (
                ctx.skin.background.aura_radius_fraction
            )
            base = defaults.CALENDAR_WEDGE_ALPHA
            for index, (start, end) in enumerate(calendar_wedge_bounds(wheel)):
                alpha = base + (
                    defaults.CALENDAR_WEDGE_LIT_DELTA
                    if index == ctx.calendar_lit
                    else 0.0
                )
                painter.save()
                painter.setOpacity(min(1.0, alpha))
                painter.setBrush(QColor(palette[index]))
                draw_pie(painter, cal_radius, start, end)
                painter.restore()
            return

        # Colorful off (Elements switch): the day/twilight arcs are still
        # indicated, but in plain white — a one-entry palette draws a
        # single full wedge under the same clip and alphas.
        palette = (
            palette_for(ctx.skin)
            if ctx.skin.colorful
            else (defaults.COLORFUL_OFF_COLOR,)
        )
        span = 360.0 / len(palette)
        for start, end, alpha in lit_regions(ctx.day.sun, spec):
            painter.save()
            painter.setClipPath(pie_path(aura_radius, start, end))
            painter.setOpacity(alpha)
            painter.rotate(ctx.rotation)
            for i, color in enumerate(palette):
                painter.setBrush(QColor(color))
                draw_pie(
                    painter, aura_radius, i * span - span / 2, i * span + span / 2
                )
            painter.restore()

    def _draw_umbra(
        self, painter: QPainter, ctx: RenderContext, radius: float
    ) -> None:
        """The brightness wheel, drawn in the already-rotated frame:
        lightest at the top (true solar noon), darkest at the bottom
        (true midnight), mirrored left/right. Forms (owner spec): fine
        30 / coarse 24 sections — single lightest/darkest sections
        centered on top/bottom, the rest in mirror pairs — or the
        continuous per-pixel gradient."""
        contrast = ctx.skin.umbra_contrast
        tint = ctx.skin.ring_tint            # the Umbra follows the ring hue
        if ctx.skin.umbra_form == "gradient":
            lightest, darkest = defaults.UMBRA_CONTRAST_SPANS[contrast]
            lightest = min(255, lightest)        # spans store window BOUNDS
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
    """Procedural N-diamond star whose top vertex points at true solar
    noon (or straight up with solar rotation off). Colored near-full
    opacity where the sun is up, borders elsewhere (owner model)."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.star
        if ctx.skin.pointer in ("aurora", "calendar"):
            return          # no geometry at all — the wheel IS the pointer

        # Colored BORDERS run the full circle so the night diamonds stay
        # recognizable (owner spec)...
        painter.save()
        painter.setOpacity(spec.border_alpha)
        painter.rotate(ctx.rotation)
        self._draw_diamonds(painter, ctx, fill=False)
        painter.restore()

        # ...while the FILLS appear only where the sun is up.
        for start, end, alpha in lit_regions(ctx.day.sun, spec):
            painter.save()
            painter.setClipPath(pie_path(ctx.radius, start, end))
            painter.setOpacity(alpha)
            painter.rotate(ctx.rotation)
            self._draw_diamonds(painter, ctx, fill=True)
            painter.restore()

    def _draw_diamonds(self, painter: QPainter, ctx: RenderContext, fill: bool) -> None:
        spec = self._skin.star
        colors = palette_for(ctx.skin)
        count = len(colors)
        half = constants.POINTER_ARM_HALF_ANGLE_DEG[ctx.skin.pointer]
        tip = ctx.radius * spec.radius_fraction
        # Inner vertices at tip / (2 cos(half)) — the regular-star value
        # (1/sqrt(3) of the tip for the hexagram); the cross reuses the
        # octa arm shape, so its arms don't touch (owner spec).
        inner = tip / (2.0 * math.cos(math.radians(half)))
        border_width = max(1.0, ctx.radius * spec.border_width_fraction)
        for k, color in enumerate(colors):
            theta = k * 360.0 / count
            diamond = QPolygonF(
                [
                    QPointF(0.0, 0.0),
                    dial_point(theta - half, inner),
                    dial_point(theta, tip),
                    dial_point(theta + half, inner),
                ]
            )
            if fill:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(color))
                painter.drawPolygon(diamond)
            else:
                # Border as PADDING (owner spec): clip to the diamond and
                # stroke at double width, so only the inner half shows —
                # neighboring diamonds' borders sit side by side instead
                # of overpainting each other along shared edges.
                clip = QPainterPath()
                clip.addPolygon(diamond)
                clip.closeSubpath()
                painter.save()
                painter.setClipPath(clip)
                painter.setPen(QPen(QColor(color), 2.0 * border_width))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawPolygon(diamond)
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
            # touches them (1x1 placeholders until his files land).
            draw_pixmap_centered(
                painter, ctx, spec.asset, QPointF(0, 0), 2 * ctx.radius,
                tint=ctx.skin.ring_tint,
            )
            self._draw_letter_art(painter, ctx)
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

    def _draw_letter_art(self, painter: QPainter, ctx: RenderContext) -> None:
        """The owner's letter art at the preset's hour positions —
        gold masters and PRE-RENDERED silver files (the accent letter
        wears the opposite metal, owner spec). Each letter ROTATES with
        its place on the circle (tangentially; the lower half flips 180°
        to stay readable — Ω stands upright at the bottom), rides a
        tight dark halo (owner spec: a gradient border, lit from above)
        and is UNTINTED by the ring hue."""
        height = (
            2 * ctx.radius * defaults.RING_LETTER_ART_SCALE
            * ctx.skin.ring_letter_scale
        )
        shadow_radius = height * defaults.RING_LETTER_SHADOW_RADIUS
        samples = defaults.RING_LETTER_SHADOW_SAMPLES
        for hour, asset in self._skin.ring.letter_art.items():
            theta = (hour * 15.0 + constants.DIAL_OFFSET_DEG) % 360.0
            rotation = theta - 180.0 if 90.0 < theta < 270.0 else (
                theta if theta <= 90.0 else theta - 360.0
            )
            pixmap = ctx.cache.pixmap_by_height(asset, height, ctx.dpr)
            shadow = ctx.cache.pixmap_by_height(
                asset, height, ctx.dpr, tint="#000000"
            )
            logical_w = pixmap.width() / ctx.dpr
            pos = dial_point(
                theta, ctx.radius * defaults.RING_LETTER_RADIUS_FRACTION
            )
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


def draw_body_label(
    painter: QPainter, ctx: RenderContext, body: str,
    pos: QPointF, size: float,
) -> None:
    """The weekday-name label on a body — shared by the weekday unit
    and the info slot's second body (Rule #5): short until the largest
    preset, full from WEEKDAY_FULL_NAME_MIN_DIAMETER."""
    full_text = 2 * ctx.radius >= defaults.WEEKDAY_FULL_NAME_MIN_DIAMETER
    label_size = size * defaults.BODY_LABEL_SIZE * (0.62 if full_text else 1.0)
    label = (
        constants.WEEKDAY_FULL_NAMES[body]
        if full_text
        else constants.WEEKDAY_LABELS[body]
    )
    font = QFont()
    font.setPixelSize(max(defaults.BODY_LABEL_MIN_PX, round(label_size)))
    font.setBold(True)
    draw_outlined_text(painter, pos, label, font)


def draw_weekday_body(
    painter: QPainter,
    ctx: RenderContext,
    body: str,
    pos: QPointF,
    size: float,
    opacity: float,
) -> None:
    """One weekday body with its white outlined label — shared by the
    diamond slots and the above-the-hands center pass (Rule #5). The
    label is the weekday name (owner spec): short until the largest
    preset, full from WEEKDAY_FULL_NAME_MIN_DIAMETER."""
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
        draw_body_label(painter, ctx, body, pos, size)
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

        if (
            ctx.skin.pointer in ("hexa", "trio")
            and today != "sun"
            and not ctx.reveal_active
            and self._gate(ctx, "body:sun")
        ):
            # The hexa and trio layouts center the Sun; on Sundays — or
            # during the reveal window (owner 2026-07-16) — the CENTER
            # pass draws it opaque ABOVE the hands instead.
            center_size = weekday_body_size(ctx.skin, ctx.radius)
            center_size *= hover_factor(ctx, "body:sun")
            draw_weekday_body(
                painter, ctx, "sun", QPointF(0, 0), center_size, spec.ghost_opacity
            )
        orbit = ctx.radius * weekday_body_orbit(ctx.skin)
        slot_size = weekday_body_size(ctx.skin, ctx.radius)
        servant = servant_holds_the_seat(ctx.skin, today)
        for slot_angle, occupants in constants.POINTER_WEEKDAY_SLOTS[ctx.skin.pointer]:
            if servant and slot_angle == constants.SOUTH_SLOT_ANGLE:
                continue     # the Servant won the 24h seat today
            body = visible_occupant(occupants, today)
            if not self._gate(ctx, f"body:{body}"):
                continue
            theta = slot_angle + ctx.rotation
            draw_weekday_body(
                painter, ctx, body, dial_point(theta, orbit),
                slot_size * hover_factor(ctx, f"body:{body}"),
                1.0 if body == today or ctx.reveal_active else spec.ghost_opacity,
            )
        if servant and self._gate(ctx, "sun_servant"):
            # THE SERVANT FACE at 24h (owner 2026-07-13): it stands all
            # week like every other body — ghosted, OPAQUE on Sunday or
            # during the reveal window — two persons, a union; the
            # metal themes' swap recolors it exactly like the Ruler
            # plate. Image only — the Names label belongs to the Ruler
            # face.
            painter.save()
            painter.setOpacity(
                1.0 if today == "sun" or ctx.reveal_active else spec.ghost_opacity
            )
            draw_pixmap_centered(
                painter, ctx, spec.dual_asset,
                dial_point(
                    constants.SOUTH_SLOT_ANGLE + ctx.rotation, orbit
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
        elif theme == "planets":
            asset = (
                defaults.WEEKDAY_ART_DIR / "planets" / "primary"
                / f"{today}.png"
            )
        else:
            theme_dir = (
                defaults.WEEKDAY_ART_DIR
                / defaults.WEEKDAY_THEME_DIRS[theme]
            )
            if metal == "colored" and theme in constants.METAL_THEMES:
                # colored is the variant SIBLING (owner restructure
                # 2026-07-14: <family>/colored).
                theme_dir = theme_dir.parent / "colored"
            asset = (
                theme_dir
                / f"{defaults.WEEKDAY_THEME_FILES[theme][today]}.png"
            )
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
    that IS the z-order lift the reveal promises."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        if weekday_classic_slot(ctx.skin) is None:
            return          # every slot sits in a seat
        ghost_reveal = (
            ctx.reveal_active
            and spec.display_mode != "center_only"
            and ctx.skin.pointer in ("hexa", "trio")
        )
        if spec.display_mode != "center_only" and not (
            ctx.skin.pointer in ("hexa", "trio") and today == "sun"
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
        center_size *= hover_factor(ctx, f"body:{today}")
        body = "sun" if ghost_reveal else today
        draw_weekday_body(painter, ctx, body, QPointF(0, 0), center_size, 1.0)


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
        half = constants.POINTER_ARM_HALF_ANGLE_DEG[ctx.skin.pointer]
        arm_width = tip * math.tan(math.radians(half))   # diamond's widest
        names_on = ctx.skin.show_weekday_names
        for index, fig in enumerate(archetypes.figures(key)):
            # Per-arm hover target (owner slika 8): the base pass skips
            # the hovered figure, the HoverLift twin redraws it enlarged
            # above — exactly like the slots.
            element = f"archetype:{index}"
            if not self._gate(ctx, element):
                continue
            lit = ctx.reveal_active or index == ctx.archetype_lit
            hf = hover_factor(ctx, element)
            # THE TWO-TYPE LAW (owner decree 2026-07-18, round two): each
            # figure's OWN art aspect decides CIRCLE (the slot size) vs
            # PORTRAIT (the per-pointer lancet fraction) — classified
            # per figure, not once for the whole layout.
            height = archetype_figure_size(ctx.skin, ctx.radius, fig["file"])
            draw_archetype_figure(
                painter, ctx, fig,
                dial_point(fig["angle"] + ctx.rotation, orbit),
                height * hf, arm_width * hf,
                1.0 if lit else ctx.skin.weekday_set.ghost_opacity,
                named=names_on and lit,
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
            _draw_archetype_name(
                painter, center["name"], QPointF(0, 0), height, height
            )
        painter.restore()


def octa_slot_art(folder: str, name: str) -> Path | None:
    """The PNG for an image slot style — `folder` is a subdirectory of
    assets/zodiac/ ("astrology/sign", "astrology/primary",
    "astrology/constellation", "chinese/primary", "chinese/colored" —
    the family/variant tree), `name` the entity ("Cancer" / "Horse") — or
    None while the owner's art folder does not have it yet."""
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


def _subdial_seat(pos: QPointF) -> str:
    """Which subdial PLATE a slot position wears (owner 2026-07-14:
    the sun lives at the dial center, every seat shadows outward):
    the exact center, the 3h seat (lower left), the 21h seat (lower
    right), or the lone southern spot."""
    if abs(pos.x()) < 1.0 and abs(pos.y()) < 1.0:
        return "center"
    theta = math.degrees(math.atan2(pos.x(), -pos.y())) % 360.0
    if abs(theta - constants.AURORA_DUAL_WEEKDAY_ANGLE) <= 30.0:
        return "h3"
    if abs(theta - constants.AURORA_DUAL_SLOT_ANGLE) <= 30.0:
        return "h21"
    return "south"


def _draw_subdial_shadow(
    painter: QPainter, pos: QPointF, diameter: float
) -> None:
    """The subdial's LIVE shadow (owner 2026-07-15: the sun lives at
    the dial center, the shadow is rendered — never baked): offset
    OUTWARD from the center, symmetric on the center seat."""
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
    shade = QColor(*defaults.SUBDIAL_SHADOW_RGBA)
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
    (medallions, planets, colored badges) stay bare. The owner's
    PLATE ART draws whenever ANY plate exists — a missing finish is
    RECOLORED from his master, a missing seat borrows the center
    plate — under a LIVE outward shadow (owner 2026-07-15: one master
    plate, the code paints the metals and the light). The "theme"
    plate style (owner A/B spec) colorizes the tapisserie field to
    the clock tint; "black" keeps the standard dark field. With no
    art at all: the procedural circle, the ring's own face color
    rimmed in the finish metal."""
    _draw_subdial_shadow(painter, pos, diameter)
    plate = subdial_plate_file(
        ctx.skin.ring_finish,
        _subdial_seat(pos),
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
        defaults.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish]
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
        defaults.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish]
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
    painter.setBrush(QColor(*defaults.SUBDIAL_TEXT_SHADOW_RGBA))
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
        else QColor(*defaults.SMALL_SECONDS_TICK_RGBA)
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
            QColor(*defaults.SMALL_SECONDS_TICK_SHADOW_RGBA), width,
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
            tint=defaults.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish],
            desaturate=ctx.skin.hands.desaturate,
        )
        silhouette = ctx.cache.pixmap_by_height(
            spec.asset, height, ctx.dpr, tint="#000000",
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
            # cycle angle, so the SILVER halo straddles the ring.
            glowing = ctx.tick.moon_event is not None
            orbit = (
                defaults.GLOW_RING_RADIUS_FRACTION
                if glowing
                else spec.moon_orbit_fraction
            )
            pos = dial_point(moon_angle, ctx.radius * orbit)
            if glowing:
                draw_event_glow(
                    painter,
                    pos,
                    ctx.radius * spec.moon_scale * factor,
                    defaults.GLOW_MOON_COLOR,
                )
            painter.save()
            painter.setOpacity(painter.opacity() * opacity)
            self._draw_moon(
                painter, ctx, pos, 2 * ctx.radius * spec.moon_scale * factor
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
        # angle, so the GOLDEN halo straddles the ring.
        glowing = ctx.tick.season_event is not None
        orbit = (
            defaults.GLOW_RING_RADIUS_FRACTION if glowing else spec.orbit_fraction
        )
        pos = dial_point(year_angle, ctx.radius * orbit)
        size = 2 * ctx.radius * spec.scale * hover_factor(ctx, "earth")
        if glowing:
            draw_event_glow(painter, pos, size / 2, defaults.GLOW_SUN_COLOR)
        if almanac:
            # The day-ARROW at the marker's exact tick (owner 2026-07-16):
            # a small procedural triangle pointing from inside the dial
            # OUTWARD at the ring, so the ring reads today's date.
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(defaults.CALENDAR_ARROW_COLOR))
            painter.drawPolygon(calendar_day_arrow(year_angle, ctx.radius))
            painter.restore()
        variant = (
            f"{ctx.skin.earth_style}_"
            f"{earth_region(ctx.day.latitude, spec.default_variant)}_"
            f"{'day' if ctx.tick.is_daylight else 'night'}"
        )
        asset = spec.variants.get(variant)
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
                and (ctx.skin.show_earth_date or ctx.skin.earth_weekday)
            ):
                # The Earth label — the date OR the abbreviated weekday
                # (owner 2026-07-17, ROADMAP 15e: the two are EXCLUSIVE) —
                # never fits below the full-text threshold anyway.
                self._draw_earth_label(painter, ctx, pos, size)
        else:
            color = spec.day_color if ctx.tick.is_daylight else spec.night_color
            painter.setPen(
                QPen(
                    QColor(*defaults.MARKER_BORDER_RGBA),
                    max(1.0, size * defaults.MARKER_BORDER_WIDTH),
                )
            )
            painter.setBrush(QColor(color))
            painter.drawEllipse(pos, size / 2, size / 2)

    def _draw_earth_label(self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float) -> None:
        """The Earth marker's text — THREE modes (owner 2026-07-18, the
        accepted trio): WEEKDAY alone writes "FRI" centered; DATE alone
        writes "8 Jul" centered; FULL DATE (both switches on) writes the
        date with the abbreviated weekday BENEATH it as a two-row label.
        During a DEEP travel (Session 16, deep proxy frame active) the
        YEAR row OUTRANKS the weekday — far from the present the marker
        must say WHEN — so Full Date degrades to the date+year pair."""
        bold_font = QFont()
        bold_font.setBold(True)
        deep_travel = ctx.day.deep_cycles != 0
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        if ctx.skin.earth_weekday and not ctx.skin.show_earth_date:
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
        # Date — alone, or over a second row: the deep-travel YEAR
        # (priority), else the Full Date weekday.
        text = f"{ctx.day.local_date.day} {ctx.day.local_date:%b}"
        bold_font.setPixelSize(
            max(defaults.BODY_LABEL_MIN_PX, round(size * defaults.EARTH_DATE_TEXT_SIZE))
        )
        if deep_travel:
            second_row = display_year(ctx)
        elif ctx.skin.earth_weekday:
            second_row = constants.WEEKDAY_LABELS[today]
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

    def _draw_moon(self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float) -> None:
        """Moon image (or procedural disc) with the unlit part shadowed:
        the lit region is the half-disc on the lit side combined with the
        terminator half-ellipse (semi-axis a = R*|cos 2pi*f|) — union when
        gibbous, difference when crescent; everything else is darkened."""
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

        lit_right = fraction < 0.5          # waxing: lit on the right
        gibbous = 0.25 < fraction < 0.75
        half = QPainterPath()
        half.moveTo(0.0, -radius)
        # 90 deg is the top in Qt's CCW system; sweep -180 covers the right
        # half, +180 the left half.
        half.arcTo(QRectF(-radius, -radius, size, size), 90.0, -180.0 if lit_right else 180.0)
        half.closeSubpath()
        semi_axis = radius * abs(math.cos(2.0 * math.pi * fraction))
        terminator = QPainterPath()
        terminator.addEllipse(QRectF(-semi_axis, -radius, 2 * semi_axis, size))
        lit = half.united(terminator) if gibbous else half.subtracted(terminator)

        if spec.moon_asset is not None:
            disc = QPainterPath()
            disc.addEllipse(QRectF(-radius, -radius, size, size))
            shadow = QColor(spec.moon_dark_color)
            shadow.setAlphaF(spec.moon_shadow_alpha)
            painter.fillPath(disc.subtracted(lit), shadow)
        else:
            painter.fillPath(lit, QColor(spec.moon_lit_color))
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
