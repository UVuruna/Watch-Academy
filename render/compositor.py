"""Z-ordered layer stack with cadence-driven caching.

STATIC and DAILY layers are composited into ONE cached pixmap at device
resolution, rebuilt only when the day context, size or DPI changes; the
per-minute paint blits that cache and draws the MINUTE layers (hands,
year marker) live. The same paint path renders offscreen for tests and
the future settings preview.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap

from config import constants, defaults
from core import angles
from core.clock_state import DayContext, TickState
from render.assets import AssetCache
from render.layers import (
    BackgroundLayer,
    Cadence,
    HandLayer,
    HexagramLayer,
    Layer,
    NoonMarkerLayer,
    RenderContext,
    RingLayer,
    WeekdayLayer,
    YearMarkerLayer,
    dial_point,
)
from skins.manifest import SkinDefinition

_RENDER_HINTS = (
    QPainter.RenderHint.Antialiasing
    | QPainter.RenderHint.SmoothPixmapTransform
    | QPainter.RenderHint.TextAntialiasing
)


def _build_layers(skin: SkinDefinition) -> list[Layer]:
    factories = {
        "background": lambda: BackgroundLayer(skin),
        "hexagram": lambda: HexagramLayer(skin),
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
        else:
            layers.append(factories[name]())
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
        )
        for layer in self._layers:
            if layer.cadence is Cadence.MINUTE:
                painter.save()   # isolate pen/brush/opacity/rotation leaks
                layer.paint(painter, ctx)
                painter.restore()
        painter.restore()

    def tooltip_at(self, x: float, y: float, size: float) -> str | None:
        """Hover text under the cursor. Marker tooltips (today's body,
        Earth, Moon) apply to small dials only — large dials write that
        text directly; the twilight-band tooltips (dawn/sunrise and
        sunset/dusk times) apply at every size."""
        if self._day is None or self._last_tick is None:
            return None
        radius = size / 2
        point = QPointF(x - radius, y - radius)      # center-origin
        day, tick = self._day, self._last_tick
        date = day.local_date

        def hit(center: QPointF, hit_radius: float) -> bool:
            dx, dy = point.x() - center.x(), point.y() - center.y()
            return dx * dx + dy * dy <= hit_radius * hit_radius

        if size < defaults.FULL_TEXT_MIN_DIAMETER:
            weekday = self._skin.weekday_set
            today = constants.WEEKDAY_BODIES[day.weekday_index]
            if weekday.display_mode == "center_only" or today == "sun":
                today_pos = QPointF(0, 0)
                today_radius = radius * weekday.center_scale
            else:
                today_pos = dial_point(
                    constants.WEEKDAY_SLOT_ANGLES[today] + day.hexagram_rotation,
                    radius * weekday.orbit_fraction,
                )
                today_radius = radius * weekday.diamond_scale
            if hit(today_pos, today_radius):
                return f"{constants.WEEKDAY_FULL_NAMES[today]}, {date.day} {date:%B %Y}"

            marker = self._skin.year_marker
            if marker.mode in ("earth", "both") and hit(
                dial_point(tick.year_angle, radius * marker.orbit_fraction),
                radius * marker.scale,
            ):
                return f"{date.day} {date:%B %Y}"
            if marker.mode in ("moon", "both") and hit(
                dial_point(
                    angles.moon_cycle_angle(day.moon_fraction),
                    radius * marker.moon_orbit_fraction,
                ),
                radius * marker.moon_scale,
            ):
                return f"Moon: {day.moon_illumination * 100:.0f}% lit"

        return self._twilight_tooltip(point, radius)

    def _twilight_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Hovering a twilight band names its boundary times (owner spec):
        the morning band reads dawn/sunrise, the evening band sunset/dusk."""
        import math

        sun = self._day.sun
        distance = math.hypot(point.x(), point.y())
        if distance > radius * self._skin.background.radius_fraction:
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
            return f"Dawn {sun.dawn:%H:%M} — Sunrise {sun.sunrise:%H:%M}"
        if sun.sunset is not None and sun.dusk is not None and within(
            angle(sun.sunset), angle(sun.dusk)
        ):
            return f"Sunset {sun.sunset:%H:%M} — Dusk {sun.dusk:%H:%M}"
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
        )
        for layer in self._layers:
            if layer.cadence is not Cadence.MINUTE:
                painter.save()   # isolate pen/brush/opacity/rotation leaks
                layer.paint(painter, ctx)
                painter.restore()
        painter.end()
        pixmap.setDevicePixelRatio(dpr)
        return pixmap
