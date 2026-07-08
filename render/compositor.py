"""Z-ordered layer stack with cadence-driven caching.

STATIC and DAILY layers are composited into ONE cached pixmap at device
resolution, rebuilt only when the day context, size or DPI changes; the
per-minute paint blits that cache and draws the MINUTE layers (hands,
year marker) live. The same paint path renders offscreen for tests and
the future settings preview.
"""

import html
import math
from datetime import timedelta

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap

from config import constants, defaults
from core import angles
from core.clock_state import DayContext, TickState
from core.moon import phase_name
from core.year_wheel import zodiac_span
from render.assets import AssetCache
from render.layers import (
    BackgroundLayer,
    BottomSlotLayer,
    Cadence,
    CenterBodyLayer,
    HandLayer,
    Layer,
    NoonMarkerLayer,
    RenderContext,
    RingLayer,
    StarLayer,
    WeekdayLayer,
    YearMarkerLayer,
    dial_point,
    today_slot_theta,
)
from skins.manifest import SkinDefinition

_RENDER_HINTS = (
    QPainter.RenderHint.Antialiasing
    | QPainter.RenderHint.SmoothPixmapTransform
    | QPainter.RenderHint.TextAntialiasing
)


def _centered(*lines: str) -> str:
    """Tooltip rich text with CENTERED lines (owner spec — QToolTip
    left-aligns plain text)."""
    body = "<br/>".join(html.escape(line) for line in lines)
    return f"<div align='center'>{body}</div>"


def _build_layers(skin: SkinDefinition) -> list[Layer]:
    factories = {
        "background": lambda: BackgroundLayer(skin),
        "star": lambda: StarLayer(skin),
        "noon_marker": lambda: NoonMarkerLayer(skin),
        "ring": lambda: RingLayer(skin),
        "weekday_set": lambda: WeekdayLayer(skin),
        "year_marker": lambda: YearMarkerLayer(skin),
    }
    layers: list[Layer] = []
    for name in skin.z_order:
        if name == "hands":
            layers.append(HandLayer(skin, "hour"))
            layers.append(HandLayer(skin, "minute"))
            if skin.hands.second is not None and defaults.SECONDS_HAND_ENABLED:
                layers.append(HandLayer(skin, "second"))
        else:
            layers.append(factories[name]())
    if "weekday_set" in skin.z_order:
        # The current day's center body rides ABOVE everything — the
        # hands sweep behind the Sun (owner spec).
        layers.append(CenterBodyLayer(skin))
        if skin.pointer == "octa":
            # The octa bottom arm's info text also draws OVER the hands
            # (owner spec).
            layers.append(BottomSlotLayer(skin))
    return layers


class Compositor:
    def __init__(self, skin: SkinDefinition, cache: AssetCache):
        self._skin = skin
        self._cache = cache
        self._layers = _build_layers(skin)
        self._day: DayContext | None = None
        self._last_tick: TickState | None = None
        self._composite: QPixmap | None = None
        self._composite_key: tuple | None = None

    def set_day(self, day: DayContext) -> None:
        self._day = day
        self._composite = None

    def invalidate(self) -> None:
        """Size/DPI/screen change: drop the composite and rasterized assets."""
        self._composite = None
        self._cache.flush()

    def _rotation(self) -> float:
        """Star/Aura/Umbra/slot rotation: solar offset, or 0 upright."""
        return self._day.star_rotation if self._skin.solar_rotation else 0.0

    def paint(self, painter: QPainter, size: float, dpr: float, tick: TickState) -> None:
        if self._day is None:
            raise RuntimeError("Compositor.paint() before the first day context")
        self._last_tick = tick
        key = (round(size * dpr), self._day.cache_key)
        if self._composite is None or self._composite_key != key:
            self._composite = self._render_composite(size, dpr)
            self._composite_key = key
        painter.drawPixmap(QPointF(0, 0), self._composite)

        painter.save()
        painter.setRenderHints(_RENDER_HINTS)
        painter.translate(size / 2, size / 2)
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=tick,
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self._rotation(),
        )
        for layer in self._layers:
            if layer.cadence is Cadence.MINUTE:
                painter.save()   # isolate pen/brush/opacity/rotation leaks
                layer.paint(painter, ctx)
                painter.restore()
        painter.restore()

    def tooltip_at(self, x: float, y: float, size: float) -> str | None:
        """Hover text under the cursor, at every dial size (owner spec):
        today's body, the Earth marker (day/week ordinals, zodiac sign
        with its dates, the date — plus the season event while it glows),
        the Moon marker (phase + illumination, day in the cycle), the
        octa zodiac slot and the twilight bands."""
        if self._day is None or self._last_tick is None:
            return None
        radius = size / 2
        point = QPointF(x - radius, y - radius)      # center-origin
        day, tick = self._day, self._last_tick
        rotation = self._rotation()

        def hit(center: QPointF, hit_radius: float) -> bool:
            dx, dy = point.x() - center.x(), point.y() - center.y()
            return dx * dx + dy * dy <= hit_radius * hit_radius

        weekday = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[day.weekday_index]
        today_theta = today_slot_theta(self._skin.pointer, today)
        if weekday.display_mode == "center_only" or today_theta is None:
            # center_only mode, or the hexa layout's center Sun
            today_pos = QPointF(0, 0)
            today_radius = radius * weekday.center_scale
        else:
            today_pos = dial_point(
                today_theta + rotation,
                radius * weekday.orbit_fraction,
            )
            today_radius = radius * weekday.diamond_scale
        if hit(today_pos, today_radius):
            # Weekday marker: the day plus the body carrying it in this
            # skin ("Wednesday, Mercury"; a gods skin says "…, Hades") —
            # deliberately different from the Earth marker's date hover.
            return _centered(
                f"{constants.WEEKDAY_FULL_NAMES[today]}, {weekday.body_names[today]}"
            )

        if self._skin.pointer == "octa" and (
            self._skin.octa_slot.startswith("zodiac")
            or self._skin.octa_slot.startswith("chinese")
        ):
            slot_pos = dial_point(
                constants.OCTA_TIME_SLOT_ANGLE + rotation,
                radius * weekday.orbit_fraction,
            )
            if hit(slot_pos, radius * weekday.diamond_scale):
                if self._skin.octa_slot.startswith("chinese"):
                    return self._chinese_text()
                return self._zodiac_text()

        marker = self._skin.year_marker
        moon_angle = angles.moon_cycle_angle(day.moon_fraction)
        if marker.mode in ("moon", "both"):
            moon_pos = dial_point(moon_angle, radius * marker.moon_orbit_fraction)
            if hit(moon_pos, radius * marker.moon_scale):
                # Owner format, two lines: phase + illumination / cycle day.
                cycle_day = day.moon_fraction * constants.SYNODIC_MONTH_DAYS
                return _centered(
                    f"{phase_name(day.moon_fraction)} — "
                    f"{day.moon_illumination * 100:.0f}% lit",
                    f"Day {cycle_day:.1f} of {constants.SYNODIC_MONTH_DAYS}",
                )
        if marker.mode in ("earth", "both") and hit(
            dial_point(tick.year_angle, radius * marker.orbit_fraction),
            radius * marker.scale,
        ):
            return self._earth_text()

        # Twilight bands BEFORE the arm hovers (owner: the dawn/dusk
        # info must never be shadowed — e.g. by a glowing quarter moon
        # sitting right on the 06h/18h band).
        twilight = self._twilight_tooltip(point, radius)
        if twilight is not None:
            return twilight

        return self._arm_tooltip(point, radius, rotation)

    def _arm_tooltip(self, point: QPointF, radius: float, rotation: float) -> str | None:
        """Hover over a star arm (owner spec): hexa arms name their TWO
        zodiac signs; cross/octa cardinal arms give the exact instant of
        the solstice/equinox they point at; octa diagonal arms describe
        their season (dates, duration, the middle date the arrow points
        at). With solar rotation on, a trailing * flags the slight
        offset from the year-wheel positions."""
        distance = math.hypot(point.x(), point.y())
        star_tip = radius * self._skin.star.radius_fraction
        if not (radius * 0.08 <= distance <= star_tip):
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        arms = constants.POINTER_POINTS[self._skin.pointer]
        arm_step = 360.0 / arms
        arm_angle = (round(((theta - rotation) % 360.0) / arm_step) * arm_step) % 360.0
        star = "*" if self._skin.solar_rotation else ""

        if self._skin.pointer == "hexa":
            # The 60-deg arc [arm-30, arm+30] spans exactly two signs —
            # one full line each (owner spec): symbol, name, date span.
            lines = []
            for offset in (-30.0, 0.0):      # the two signs' START angles
                start_angle = (arm_angle + offset) % 360.0
                name, symbol = constants.ZODIAC_SIGNS[int(start_angle) // 30]
                start, end = zodiac_span(self._day.year_anchors, start_angle)
                start = start.astimezone(self._day.tzinfo)
                last = end.astimezone(self._day.tzinfo) - timedelta(days=1)
                lines.append(
                    f"{symbol} {name} — {start.day} {start:%b} – {last.day} {last:%b}"
                )
            lines[0] += star
            return _centered(*lines)
        if arm_angle % 90.0 == 0.0:
            # Cardinal arms (cross and octa) point at the season events.
            anchor_angle = {0.0: 360.0, 90.0: 450.0, 180.0: 540.0, 270.0: 270.0}[
                arm_angle
            ]
            name = constants.SEASON_EVENT_NAMES[round(anchor_angle) % 360]
            instant = self._anchor_instant(anchor_angle).astimezone(self._day.tzinfo)
            return _centered(
                f"{name}{star}",
                f"{instant.day} {instant:%b %Y} — {instant:%H:%M}",
            )
        # Octa diagonal arms point at the season CENTERS.
        season, start_angle = {
            315.0: ("Spring", 270.0),
            45.0: ("Summer", 360.0),
            135.0: ("Autumn", 450.0),
            225.0: ("Winter", 540.0),
        }[arm_angle]
        start = self._anchor_instant(start_angle).astimezone(self._day.tzinfo)
        end = self._anchor_instant(start_angle + 90.0).astimezone(self._day.tzinfo)
        middle = start + (end - start) / 2
        days = round((end - start).total_seconds() / 86400)
        return _centered(
            f"{season}{star}",
            f"{start.day} {start:%b} – {end.day} {end:%b} — {days} days",
            f"Middle: {middle.day} {middle:%b}",
        )

    def _anchor_instant(self, unwrapped_angle: float):
        """Season-anchor instant at an unwrapped year-wheel angle."""
        anchors = self._day.year_anchors
        return anchors.instants[anchors.angles.index(unwrapped_angle)]

    def _chinese_text(self) -> str:
        """Slot hover, two lines (owner spec): name, then the year span."""
        day = self._day
        return _centered(
            day.chinese_name,
            f"{day.chinese_start.day} {day.chinese_start:%b %Y} – "
            f"{day.chinese_end.day} {day.chinese_end:%b %Y}",
        )

    def _zodiac_line(self) -> str:
        """"♋ Cancer — 21 Jun – 22 Jul" (sign with its date span)."""
        day = self._day
        last = day.zodiac_end - timedelta(days=1)    # end is the next sign's first day
        return (
            f"{day.zodiac_symbol} {day.zodiac_name} — "
            f"{day.zodiac_start.day} {day.zodiac_start:%b} – {last.day} {last:%b}"
        )

    def _zodiac_text(self) -> str:
        """Slot hover, two lines (owner spec): name, then the date span."""
        day = self._day
        last = day.zodiac_end - timedelta(days=1)
        return _centered(
            f"{day.zodiac_symbol} {day.zodiac_name}",
            f"{day.zodiac_start.day} {day.zodiac_start:%b} – {last.day} {last:%b}",
        )

    def _earth_text(self) -> str:
        """Owner format, three lines: day/week ordinals, the zodiac sign
        with its dates, the date — plus the season event name on top
        while the marker glows."""
        day, date = self._day, self._day.local_date
        lines = [
            f"Day {date.timetuple().tm_yday} — Week {date.isocalendar().week}",
            self._zodiac_line(),
            f"{date.day} {date:%B %Y}",
        ]
        if self._last_tick.season_event is not None:
            lines.insert(0, self._last_tick.season_event)
        return _centered(*lines)

    def _twilight_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Hovering a twilight band names its boundary times (owner spec):
        the morning band reads dawn/sunrise, the evening band sunset/dusk."""
        import math

        sun = self._day.sun
        distance = math.hypot(point.x(), point.y())
        if distance > radius * self._skin.background.aura_radius_fraction:
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0

        def within(start: float, end: float) -> bool:
            span_end = end if end > start else end + 360.0
            value = theta if theta >= start else theta + 360.0
            return start <= value <= span_end

        angle = angles.time_to_dial_angle
        if sun.dawn is not None and sun.sunrise is not None and within(
            angle(sun.dawn), angle(sun.sunrise)
        ):
            return _centered(f"Dawn {sun.dawn:%H:%M} — Sunrise {sun.sunrise:%H:%M}")
        if sun.sunset is not None and sun.dusk is not None and within(
            angle(sun.sunset), angle(sun.dusk)
        ):
            return _centered(f"Sunset {sun.sunset:%H:%M} — Dusk {sun.dusk:%H:%M}")
        return None

    def render_offscreen(
        self, size: float, dpr: float, day: DayContext, tick: TickState
    ) -> QImage:
        """Full frame into a QImage — tests and the settings preview."""
        self.set_day(day)
        px = round(size * dpr)
        image = QImage(px, px, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        image.setDevicePixelRatio(dpr)
        painter = QPainter(image)
        self.paint(painter, size, dpr, tick)
        painter.end()
        return image

    def _render_composite(self, size: float, dpr: float) -> QPixmap:
        px = round(size * dpr)
        pixmap = QPixmap(px, px)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHints(_RENDER_HINTS)
        painter.scale(dpr, dpr)
        painter.translate(size / 2, size / 2)
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=None,
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self._rotation(),
        )
        for layer in self._layers:
            if layer.cadence is not Cadence.MINUTE:
                painter.save()   # isolate pen/brush/opacity/rotation leaks
                layer.paint(painter, ctx)
                painter.restore()
        painter.end()
        pixmap.setDevicePixelRatio(dpr)
        return pixmap
