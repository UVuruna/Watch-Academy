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
    QFont,
    QFontMetricsF,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)

from config import constants, defaults
from core import angles
from core.clock_state import DayContext, TickState
from core.sun import DaylightRegime, SunDay
from render.assets import AssetCache
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
    painter: QPainter, ctx: "RenderContext", asset: Path, pos: QPointF, height: float
) -> None:
    """Asset rasterized to `height` and drawn centered at `pos` — the one
    shared image path of weekday bodies and the year marker (Rule #5)."""
    pixmap = ctx.cache.pixmap_by_height(asset, height, ctx.dpr)
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
    """Opacity of the Moon marker in "both" mode: when the smaller Moon
    meets the Earth on the shared rim (their discs would overlap) it
    passes OVER the Earth at reduced opacity — an eclipse-like transit
    where both stay visible (owner decision). Shared by the layer and the
    hover hit test (Rule #5)."""
    if spec.mode != "both":
        return 1.0
    delta = abs(year_angle - moon_angle) % 360.0
    delta = min(delta, 360.0 - delta)
    # Angular size at which the two discs touch on the shared orbit.
    touch_deg = math.degrees((spec.scale + spec.moon_scale) / spec.orbit_fraction)
    return 1.0 if delta >= touch_deg else defaults.MOON_TRANSIT_OPACITY


def palette_for(skin: SkinDefinition) -> tuple:
    """The active Star+Aura palette preset — ONE source for both the
    star diamonds and the background wedges (owner spec)."""
    return defaults.PALETTE_PRESETS[(skin.pointer, skin.palette_style)]


def draw_event_glow(painter: QPainter, pos: QPointF, marker_radius: float) -> None:
    """Soft radial halo behind a year marker during a season/moon event
    window (owner spec: a gentle glow, the marker itself unchanged)."""
    halo = marker_radius * defaults.GLOW_RADIUS_SCALE
    gradient = QRadialGradient(pos, halo)
    center = QColor(defaults.GLOW_COLOR)
    center.setAlphaF(defaults.GLOW_ALPHA)
    edge = QColor(defaults.GLOW_COLOR)
    edge.setAlphaF(0.0)
    gradient.setColorAt(0.0, center)
    gradient.setColorAt(1.0, edge)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawEllipse(pos, halo, halo)
    painter.restore()


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


class Layer(ABC):
    cadence: Cadence

    def __init__(self, skin: SkinDefinition):
        self._skin = skin

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

        palette = palette_for(ctx.skin)
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
        """The brightness wheel, drawn in the already-rotated frame
        (owner art, measured): 30 sections of 12 deg — the LIGHTEST and
        DARKEST are single sections CENTERED on the top (true solar
        noon) and bottom (true midnight), the remaining 28 form 14
        mirror-symmetric pairs down the sides. 16 shades on the
        contrast setting's arithmetic ladder."""
        sections = constants.UMBRA_SECTIONS
        lightest, step = defaults.UMBRA_SCALES[ctx.skin.umbra_contrast]
        span = 360.0 / sections
        shades = sections // 2 + 1
        for k in range(shades):
            value = lightest - k * step
            painter.setBrush(QColor(value, value, value))
            center = k * span
            draw_pie(painter, radius, center - span / 2, center + span / 2)
            if 0 < k < shades - 1:
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


class NoonMarkerLayer(Layer):
    """Small marker in the ring band at the solar-noon angle. Always
    SOLAR — a noon marker keeps pointing at true noon even when the
    star stands upright."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.noon_marker
        inner = ctx.radius * (1.0 - self._skin.ring.width_fraction)
        size = 2 * ctx.radius * spec.scale
        painter.save()
        painter.rotate(ctx.day.star_rotation)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(spec.color))
        painter.drawPolygon(
            QPolygonF(
                [
                    QPointF(0.0, -inner),
                    QPointF(-size / 2, -inner - size),
                    QPointF(size / 2, -inner - size),
                ]
            )
        )
        painter.restore()


class RingLayer(Layer):
    """Outer ring: donut, hour ticks, 24h numerals with per-skin letters,
    minute numbers along the inner edge."""

    cadence = Cadence.STATIC

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.ring
        if spec.asset is not None:
            # The ring art carries numerals, minutes and letters itself.
            draw_pixmap_centered(
                painter, ctx, spec.asset, QPointF(0, 0), 2 * ctx.radius
            )
            return
        outer, inner = ctx.radius, ctx.radius * (1.0 - spec.width_fraction)

        ring = QPainterPath()
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
    asset = spec.bodies.get(body)
    if asset is not None:
        draw_pixmap_centered(painter, ctx, asset, pos, size)
    else:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(spec.body_colors[body]))
        painter.drawEllipse(pos, size / 2, size / 2)
    full_text = 2 * ctx.radius >= defaults.WEEKDAY_FULL_NAME_MIN_DIAMETER
    label = (
        constants.WEEKDAY_FULL_NAMES[body]
        if full_text
        else constants.WEEKDAY_LABELS[body]
    )
    font = QFont()
    label_size = size * defaults.BODY_LABEL_SIZE * (0.62 if full_text else 1.0)
    font.setPixelSize(max(defaults.BODY_LABEL_MIN_PX, round(label_size)))
    font.setBold(True)
    draw_outlined_text(painter, pos, label, font)
    painter.restore()


class WeekdayLayer(Layer):
    """Weekday bodies on the pointer's arm slots (rotating WITH the star,
    owner decision), BELOW the hands. The hexa pointer keeps the Sun in
    the center; cross/octa give every body a slot — shared slots show
    only the priority winner (see visible_occupant). Modes: "ghost" (all
    visible slots, non-current faint) and "center_only" (only the current
    day's body, in the center). Whenever the CENTER image is the current
    day it is drawn by CenterBodyLayer instead — ABOVE the hands (owner
    spec; slot images are unaffected)."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]

        if spec.display_mode == "center_only":
            return                       # the center pass draws it above the hands

        if ctx.skin.pointer == "hexa" and today != "sun":
            # Only the hexa layout centers the Sun; on Sundays the center
            # pass draws it opaque above the hands instead.
            center_size = 2 * ctx.radius * spec.center_scale
            draw_weekday_body(
                painter, ctx, "sun", QPointF(0, 0), center_size, spec.ghost_opacity
            )
        orbit = ctx.radius * spec.orbit_fraction
        slot_size = 2 * ctx.radius * spec.diamond_scale
        for slot_angle, occupants in constants.POINTER_WEEKDAY_SLOTS[ctx.skin.pointer]:
            body = visible_occupant(occupants, today)
            theta = slot_angle + ctx.rotation
            draw_weekday_body(
                painter, ctx, body, dial_point(theta, orbit), slot_size,
                1.0 if body == today else spec.ghost_opacity,
            )


class CenterBodyLayer(Layer):
    """The current day's CENTER image drawn ABOVE the hands — the opaque
    Sun on Sundays in ghost mode (hexa pointer only; cross/octa seat the
    Sun on an arm slot), or the day's body in center_only mode — so the
    hands sweep behind it (owner spec; the slot images never move up
    here)."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        if spec.display_mode != "center_only" and not (
            ctx.skin.pointer == "hexa" and today == "sun"
        ):
            return
        center_size = 2 * ctx.radius * spec.center_scale
        draw_weekday_body(painter, ctx, today, QPointF(0, 0), center_size, 1.0)


class BottomSlotLayer(Layer):
    """The octa pointer's bottom arm carries user-selected info instead
    of a weekday body (owner spec): the digital time "12:24" (no seconds
    — the font stays BIG), the date "8 Jul", the day length "15:35" or
    the zodiac sign name. Text is sized to fill the slot width and drawn
    ABOVE the hands like the center body."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        theta = constants.OCTA_TIME_SLOT_ANGLE + ctx.rotation
        pos = dial_point(theta, ctx.radius * spec.orbit_fraction)
        slot_size = 2 * ctx.radius * spec.diamond_scale
        mode = ctx.skin.octa_slot
        if mode == "time":
            text = ctx.tick.time_hm
        elif mode == "date":
            text = f"{ctx.day.local_date.day} {ctx.day.local_date:%b}"
        elif mode == "day_length":
            text = ctx.day.day_length
        else:                            # "zodiac" (validated closed set)
            text = ctx.day.zodiac_name
        # Fit-to-width: the largest font whose text spans the slot's
        # width fraction — measured, not guessed, so it never overflows.
        font = QFont()
        font.setBold(True)
        font.setPixelSize(100)
        advance = QFontMetricsF(font).horizontalAdvance(text)
        target = slot_size * defaults.TIME_TEXT_WIDTH_FRACTION
        font.setPixelSize(
            max(defaults.BODY_LABEL_MIN_PX, math.floor(100.0 * target / advance))
        )
        draw_outlined_text(painter, pos, text, font)


class YearMarkerLayer(Layer):
    """Date markers along the INSIDE of the dial. Earth rides the year
    wheel (summer solstice at the top); the Moon rides its own cycle (new
    moon at the top, full at the bottom, clockwise) showing the current
    illumination. Modes: "earth", "moon", "both"."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        if spec.mode in ("earth", "both"):
            self._draw_earth(painter, ctx)
        if spec.mode in ("moon", "both"):
            moon_angle = angles.moon_cycle_angle(ctx.day.moon_fraction)
            opacity = moon_transit_opacity(spec, ctx.tick.year_angle, moon_angle)
            pos = dial_point(moon_angle, ctx.radius * spec.moon_orbit_fraction)
            if ctx.tick.moon_event is not None:
                # ±6 h around a principal phase instant (owner spec).
                draw_event_glow(painter, pos, ctx.radius * spec.moon_scale)
            painter.save()
            painter.setOpacity(painter.opacity() * opacity)
            self._draw_moon(painter, ctx, pos, 2 * ctx.radius * spec.moon_scale)
            painter.restore()

    def _draw_earth(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        pos = dial_point(ctx.tick.year_angle, ctx.radius * spec.orbit_fraction)
        size = 2 * ctx.radius * spec.scale
        if ctx.tick.season_event is not None:
            # ±12 h around a solstice/equinox instant (owner spec).
            draw_event_glow(painter, pos, size / 2)
        variant = f"{spec.default_variant}_{'day' if ctx.tick.is_daylight else 'night'}"
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
            if 2 * ctx.radius >= defaults.FULL_TEXT_MIN_DIAMETER:
                self._draw_date(painter, ctx, pos, size)
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

    def _draw_date(self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float) -> None:
        """Large dials write the date ("8 Jul") ON the Earth marker."""
        text = f"{ctx.day.local_date.day} {ctx.day.local_date:%b}"
        font = QFont()
        font.setPixelSize(
            max(defaults.BODY_LABEL_MIN_PX, round(size * defaults.EARTH_DATE_TEXT_SIZE))
        )
        font.setBold(True)
        draw_outlined_text(painter, pos, text, font)

    def _draw_moon(self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float) -> None:
        """Moon image (or procedural disc) with the unlit part shadowed:
        the lit region is the half-disc on the lit side combined with the
        terminator half-ellipse (semi-axis a = R*|cos 2pi*f|) — union when
        gibbous, difference when crescent; everything else is darkened."""
        spec = self._skin.year_marker
        fraction = ctx.day.moon_fraction
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


class HandLayer(Layer):
    """One class, three instances — rotates the hand image about the hub
    center (HAND_HUB_OFFSET_UNITS above the image bottom, owner
    convention). ALL hands share one scale so their designed proportions
    are never deformed: the longest hand's tip reaches the skin's
    reach_fraction and the others follow at their drawn ratios."""

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

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._spec
        angle = {
            "hour": ctx.tick.hour_angle,
            "minute": ctx.tick.minute_angle,
            "second": ctx.tick.second_angle,
        }[self._kind]
        hands = self._skin.hands
        # Owner convention: the canvases are exact (a faint reference
        # circle prevents export trimming) and every rotation center is
        # HAND_HUB_OFFSET_UNITS above its canvas bottom.
        hub = constants.HAND_HUB_OFFSET_UNITS
        longest_tip_units = max(
            hand.design_height - hub
            for hand in (hands.hour, hands.minute, hands.second)
            if hand is not None
        )
        units_to_logical = (hands.reach_fraction * ctx.radius) / longest_tip_units
        height = spec.design_height * units_to_logical
        pivot_y = (spec.design_height - hub) / spec.design_height
        pixmap = ctx.cache.pixmap_by_height(spec.asset, height, ctx.dpr)
        logical_w = pixmap.width() / ctx.dpr
        painter.save()
        painter.rotate(angle)
        painter.drawPixmap(QPointF(-logical_w / 2, -pivot_y * height), pixmap)
        painter.restore()
