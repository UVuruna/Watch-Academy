"""Z-ordered layer stack with cadence-driven caching.

STATIC and DAILY layers are composited into ONE cached pixmap at device
resolution, rebuilt only when the day context, size or DPI changes; the
per-minute paint blits that cache and draws the MINUTE layers (hands,
year marker) live. The same paint path renders offscreen for tests and
the future settings preview.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap

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
