"""The HOVER Z-LIFT layer — repaints only the hovered element, last."""

from PySide6.QtGui import QPainter

from render.context import Cadence, Layer, RenderContext
from render.layers.archetype import ArchetypeCenterLayer, ArchetypeLayer
from render.layers.slot import SlotLayer
from render.layers.weekday import WeekdayLayer
from render.layers.year_marker import YearMarkerLayer
from skins.manifest import SkinDefinition


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
