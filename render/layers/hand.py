"""The HAND layer — one class, three instances (hour/minute/second)."""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from render.context import Cadence, Layer, RenderContext
from skins.manifest import HandSpec, SkinDefinition


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
