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
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF

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


class Layer(ABC):
    cadence: Cadence

    def __init__(self, skin: SkinDefinition):
        self._skin = skin

    @abstractmethod
    def paint(self, painter: QPainter, ctx: RenderContext) -> None: ...


class BackgroundLayer(Layer):
    """Six 4-hour sectors, then darkening overlays for twilight and night.
    Always painter-drawn — the daylight arc changes every day."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.background
        radius = ctx.radius * spec.radius_fraction
        painter.setPen(Qt.PenStyle.NoPen)

        if spec.mode == "colors":
            for i, color in enumerate(spec.sector_palette):
                painter.setBrush(QColor(color))
                draw_pie(painter, radius, i * 60.0 - 30.0, i * 60.0 + 30.0)
        else:  # "light_dark"
            painter.setBrush(QColor(spec.day_base))
            painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))

        for start, end, shade in self._bands(ctx.day.sun):
            overlay = QColor(0, 0, 0, round((1.0 - shade) * 255))
            painter.setBrush(overlay)
            draw_pie(painter, radius, start, end)

    def _bands(self, sun: SunDay) -> list[tuple[float, float, float]]:
        """(start, end, brightness-kept) arcs; day arcs are omitted (no
        overlay). End angles are unwrapped past 360 where the arc crosses
        the dial top/bottom. On transitional high-latitude days a boundary
        can be missing even in NORMAL/WHITE_NIGHTS regimes — each missing
        boundary coalesces to its neighbor (the band collapses to zero
        width and is dropped) instead of crashing mid-paint."""
        spec = self._skin.background

        def arc(a: float, b: float, shade: float) -> tuple[float, float, float]:
            return (a, b if b > a else b + 360.0, shade)

        angle = angles.time_to_dial_angle
        regime = sun.regime
        if regime is DaylightRegime.NORMAL:
            rise = angle(sun.sunrise) if sun.sunrise else angle(sun.dawn)
            sets = angle(sun.sunset) if sun.sunset else angle(sun.dusk)
            dawn = angle(sun.dawn) if sun.dawn else rise
            dusk = angle(sun.dusk) if sun.dusk else sets
            bands = [
                arc(sets, dusk, spec.twilight_shade),
                arc(dusk, dawn, spec.night_shade),
                arc(dawn, rise, spec.twilight_shade),
            ]
            return [band for band in bands if band[0] != band[1]]
        if regime is DaylightRegime.WHITE_NIGHTS:
            if sun.sunrise is None or sun.sunset is None:
                # One-sided transition into/out of polar day: the sun is up
                # nearly the whole day — render it as all daylight.
                return []
            return [arc(angle(sun.sunset), angle(sun.sunrise), spec.twilight_shade)]
        if regime is DaylightRegime.TWILIGHT_ONLY:
            if sun.dawn is not None and sun.dusk is not None:
                return [
                    arc(angle(sun.dawn), angle(sun.dusk), spec.twilight_shade),
                    arc(angle(sun.dusk), angle(sun.dawn), spec.night_shade),
                ]
            return [(0.0, 360.0, spec.twilight_shade)]  # all-day twilight band
        if regime is DaylightRegime.POLAR_DAY:
            return []
        return [(0.0, 360.0, spec.night_shade)]          # POLAR_NIGHT


class HexagramLayer(Layer):
    """Six-point star whose top vertex always points at true solar noon."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.hexagram
        tip_radius = ctx.radius * spec.radius_fraction
        painter.save()
        painter.rotate(ctx.day.hexagram_rotation)
        painter.setOpacity(spec.opacity)
        if spec.asset is not None:
            pixmap = ctx.cache.pixmap_by_height(spec.asset, 2 * tip_radius, ctx.dpr)
            logical_w = pixmap.width() / ctx.dpr
            painter.drawPixmap(QPointF(-logical_w / 2, -tip_radius), pixmap)
        else:
            # Explicit QPen — copying painter.pen() would inherit the
            # NoPen STYLE left by a previous layer and draw nothing.
            painter.setPen(
                QPen(
                    QColor(*defaults.HEXAGRAM_PEN_RGBA),
                    max(1.0, ctx.radius * defaults.HEXAGRAM_PEN_WIDTH),
                )
            )
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for offset in (0.0, 60.0):
                triangle = QPolygonF(
                    [dial_point(offset + k * 120.0, tip_radius) for k in range(3)]
                )
                painter.drawPolygon(triangle)
        painter.restore()


class NoonMarkerLayer(Layer):
    """Small marker in the ring band at the solar-noon angle."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.noon_marker
        inner = ctx.radius * (1.0 - self._skin.ring.width_fraction)
        size = 2 * ctx.radius * spec.scale
        painter.save()
        painter.rotate(ctx.day.hexagram_rotation)
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


class WeekdayLayer(Layer):
    """Seven bodies: Sun in the center, six in the hexagram diamonds.
    The diamond slots rotate WITH the hexagram (owner decision). Modes:
    "ghost" (all visible, non-current faint) and "center_only" (only the
    current day's body, in the center)."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        center_size = 2 * ctx.radius * spec.center_scale

        if spec.display_mode == "center_only":
            self._draw_body(painter, ctx, today, QPointF(0, 0), center_size, 1.0)
            return

        self._draw_body(
            painter, ctx, "sun", QPointF(0, 0), center_size,
            1.0 if today == "sun" else spec.ghost_opacity,
        )
        orbit = ctx.radius * spec.orbit_fraction
        slot_size = 2 * ctx.radius * spec.diamond_scale
        for body, slot_angle in constants.WEEKDAY_SLOT_ANGLES.items():
            theta = slot_angle + ctx.day.hexagram_rotation
            self._draw_body(
                painter, ctx, body, dial_point(theta, orbit), slot_size,
                1.0 if body == today else spec.ghost_opacity,
            )

    def _draw_body(
        self,
        painter: QPainter,
        ctx: RenderContext,
        body: str,
        pos: QPointF,
        size: float,
        opacity: float,
    ) -> None:
        spec = self._skin.weekday_set
        painter.save()
        painter.setOpacity(opacity)
        asset = spec.bodies.get(body)
        if asset is not None:
            draw_pixmap_centered(painter, ctx, asset, pos, size)
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(spec.body_colors[body]))
            painter.drawEllipse(pos, size / 2, size / 2)
            font = QFont()
            font.setPixelSize(max(defaults.BODY_LABEL_MIN_PX, round(size * defaults.BODY_LABEL_SIZE)))
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor(*defaults.BODY_LABEL_RGBA))
            rect = QRectF(pos.x() - size / 2, pos.y() - size / 2, size, size)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, body[:3].capitalize())
        painter.restore()


class YearMarkerLayer(Layer):
    """Earth (day/night variant) or Moon-with-phase icon riding the ring
    once per year — summer solstice at the top."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        pos = dial_point(ctx.tick.year_angle, ctx.radius * spec.orbit_fraction)
        size = 2 * ctx.radius * spec.scale
        if spec.mode == "moon_phase":
            self._draw_moon(painter, ctx, pos, size)
            return
        variant = f"{spec.default_variant}_{'day' if ctx.tick.is_daylight else 'night'}"
        asset = spec.variants.get(variant)
        if asset is not None:
            draw_pixmap_centered(painter, ctx, asset, pos, size)
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

    def _draw_moon(self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float) -> None:
        """Full disc in the dark color, then the lit region: half-disc on
        the lit side combined with the terminator half-ellipse
        (semi-axis a = R*|cos 2pi*f|) — union when gibbous, difference
        when crescent."""
        spec = self._skin.year_marker
        fraction = ctx.day.moon_fraction
        radius = size / 2
        painter.save()
        painter.translate(pos)
        painter.setPen(Qt.PenStyle.NoPen)
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
        painter.fillPath(lit, QColor(spec.moon_lit_color))
        painter.restore()


class HandLayer(Layer):
    """One class, two instances — rotates the hand image about its
    skin-declared pivot; the tip reaches length_fraction of the radius."""

    cadence = Cadence.MINUTE

    def __init__(self, skin: SkinDefinition, kind: str):
        super().__init__(skin)
        self._kind = kind

    @property
    def _spec(self) -> HandSpec:
        return self._skin.hands.hour if self._kind == "hour" else self._skin.hands.minute

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._spec
        angle = ctx.tick.hour_angle if self._kind == "hour" else ctx.tick.minute_angle
        # The tip-to-pivot distance is pivot_y of the image height.
        height = (spec.length_fraction * ctx.radius) / spec.pivot[1]
        pixmap = ctx.cache.pixmap_by_height(spec.asset, height, ctx.dpr)
        logical_w = pixmap.width() / ctx.dpr
        painter.save()
        painter.rotate(angle)
        painter.drawPixmap(
            QPointF(-spec.pivot[0] * logical_w, -spec.pivot[1] * height), pixmap
        )
        painter.restore()
