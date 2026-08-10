"""THE MOON HORIZON BAND layer (owner verdict 2026-08-09) — an arc on
the dial's inner tick circle showing WHEN the Moon stands above the
horizon today, in one of four owner-approved visual styles.

Geometry comes entirely from `core.moon.moon_horizon_arcs` (Rule #5,
never re-derived here); this module only paints it. The band sits on
the INNER band's own radius (`dial.MINUTES_RADIUS_FRACTION`) — that
band NEVER rotates with `ctx.world_offset` in any world mode (the
Fidelity Ruling, `render.layers.numerals`'s own "ledger §2"), so this
layer does not apply the world offset either; both stay in registration
with the fixed tick art underneath.

THE TICK-ART HONESTY NOTE: the 360 day ticks themselves are the
owner's own baked PNG art (`config.dial.RING_INNER_COMPOSITION`'s base
plate), not individually addressable primitives — there is no per-tick
recolor hook to reach into. Style 1 ("inverted") is therefore
approximated as a stroked arc drawn AT the tick radius using
`QPainter.CompositionMode_Difference` (a true RGB invert of whatever
art sits under the stroke, so a light-ink result over dark ticks is
the actual inverted pixels, not a guess). Style 3 ("ticks") is NOT a
continuous stroke — the owner's own correction (2026-08-09, grader
round): a connecting line would make it visually indistinguishable
from "silver_thread" at a glance, which the approved design forbids.
It draws one discrete `MOON_SILVER` radial segment PER DEGREE (the
same 1-per-degree spacing the baked art itself uses — "the 360 day
ticks"), slightly longer than the plate's own ticks, with NOTHING
connecting them — the tick marks themselves are the whole style,
matching the approved design's "no connecting thread/arc line at all".
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF

from config import constants, dial, palette
from core import angles
from core.moon import MoonArc, moon_horizon_arcs
from render.context import Cadence, Layer, RenderContext
from render.painting import dial_point, draw_pie

# Radial geometry (fractions of the band radius; small enough on-dial
# that plain constants read clearly against a lookup table nobody else
# shares).
_TICK_STROKE_WIDTH_FRACTION = 0.012
_SILVER_TICK_SEGMENT_WIDTH_FRACTION = 0.010   # each discrete tick's own line width (style 3)
_SILVER_TICK_HALF_LENGTH_FRACTION = 0.028     # each tick's half-length, centered on the band radius
_THREAD_WIDTH_FRACTION = 0.006         # style 2's thin thread
_THREAD_INSET_FRACTION = 0.035         # just inside the ticks
_DOT_RADIUS_FRACTION = 0.014
_DIAMOND_HALF_FRACTION = 0.016
_INVERT_FILL_ALPHA = 110
_GLOW_LAYERS = 5
_GLOW_MAX_WIDTH_FRACTION = 0.10
_GLOW_MAX_ALPHA = 90       # of 255, at culmination, innermost layer
_ECLIPSE_SEGMENT_WIDTH_FRACTION = 0.075   # the copper band segment's thickness
_ECLIPSE_SEGMENT_EDGE_FRACTION = 0.30     # its turquoise end caps, of that width


class MoonBandLayer(Layer):
    """Draws the Moon Horizon Band for the active `moon_band_style`,
    gated on `moon_band_mode == "horizon"` — the compositor also skips
    building this layer outright in the other two modes (`_build_layers`'s
    `skipped` table); this gate is the belt to that suspenders."""

    frame = "interior"
    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = ctx.skin.year_marker
        if spec.moon_band_mode != "horizon":
            return
        arcs = moon_horizon_arcs(ctx.day.moonrise, ctx.day.moonset)
        radius = ctx.radius * dial.MINUTES_RADIUS_FRACTION
        style = spec.moon_band_style
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for arc in arcs:
            if style == "inverted":
                self._draw_inverted(painter, radius, arc)
            elif style == "ticks":
                self._draw_ticks(painter, radius, arc)
            elif style == "glow":
                self._draw_glow(painter, radius, arc)
            else:
                self._draw_silver_thread(painter, radius, arc)
        if spec.eclipse_lunar_style == "horizon_shadow":
            # THE DAY'S eclipses, not the tick's active one: this layer's
            # cadence is DAILY and `ctx.tick` is None while a cached
            # daily pass composites (`render.context`'s own note). That
            # is not a limitation here but the correct source — the band
            # draws the whole day, so it must mark an eclipse that has
            # not started yet and one that is already over, which is
            # exactly what showing DURATION means. Reading `ctx.tick`
            # cost three failing tests and a hard abort before this was
            # understood; the mistake is recorded so the next reader
            # does not repeat it.
            for event in ctx.day.eclipses:
                if event.kind != "lunar":
                    continue
                self.draw_eclipse_segment(
                    painter, radius,
                    angles.time_to_dial_angle(event.instant),
                )
        painter.restore()

    def draw_eclipse_segment(
        self, painter: QPainter, radius: float, centre_deg: float,
    ) -> None:
        """THE ECLIPSE ON THE BAND (owner placement 2026-08-10): a copper
        segment straddling the band at the eclipse's own hour, so the
        band says WHEN it happens and roughly how long it runs —
        duration is the one thing no halo and no darkened disc can show.

        It is drawn on the band whatever the band's own style is: the
        style decides how the above-horizon arc looks, this is a
        separate mark laid over it. The span comes from
        `constants.ECLIPSE_BAND_DURATION_H`, a documented approximation
        — the catalog stores only the instant of greatest eclipse (see
        that constant's own note), so a segment that claimed exact
        contact times would be inventing them."""
        half = constants.ECLIPSE_BAND_DURATION_H / 24.0 * 360.0 / 2.0
        width = radius * _ECLIPSE_SEGMENT_WIDTH_FRACTION
        rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
        pen = QPen(QColor(palette.ECLIPSE_TOTAL_MOON_TINT))
        pen.setWidthF(width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.drawArc(
            rect, round((90.0 - (centre_deg - half)) * 16), round(-2 * half * 16)
        )
        # The turquoise rim at each end — the SAME ozone colour the disc
        # treatments wear, so one eclipse reads as one event wherever it
        # is drawn.
        edge = QPen(QColor(palette.ECLIPSE_LUNAR_FRINGE_COLOR))
        edge.setWidthF(width * _ECLIPSE_SEGMENT_EDGE_FRACTION)
        painter.setPen(edge)
        for end in (centre_deg - half, centre_deg + half):
            inner = dial_point(end % 360.0, radius - width / 2.0)
            outer = dial_point(end % 360.0, radius + width / 2.0)
            painter.drawLine(inner, outer)
        painter.restore()

    # -- style 1: inverted band -------------------------------------------

    def _draw_inverted(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, _INVERT_FILL_ALPHA))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
        draw_pie(painter, radius, arc.start_deg, arc.end_deg)
        painter.restore()
        # The ticks themselves invert to light ink: a real RGB difference
        # against whatever sits under the stroke (the honesty note above).
        painter.save()
        pen = QPen(QColor(255, 255, 255))
        pen.setWidthF(radius * _TICK_STROKE_WIDTH_FRACTION)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Difference)
        self._stroke_arc(painter, radius, arc)
        painter.restore()

    # -- style 2: silver thread (THE DEFAULT) ------------------------------

    def _draw_silver_thread(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        thread_radius = radius * (1.0 - _THREAD_INSET_FRACTION)
        silver = QColor(palette.MOON_SILVER)
        pen = QPen(silver)
        pen.setWidthF(radius * _THREAD_WIDTH_FRACTION)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        self._stroke_arc(painter, thread_radius, arc)

        dot_r = radius * _DOT_RADIUS_FRACTION
        start_pt = dial_point(arc.start_deg % 360.0, thread_radius)
        end_pt = dial_point(arc.end_deg % 360.0, thread_radius)
        # Filled dot at moonrise.
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(silver)
        painter.drawEllipse(start_pt, dot_r, dot_r)
        # Hollow dot at moonset.
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(end_pt, dot_r, dot_r)
        # Diamond at culmination (the arc's own midpoint — see
        # `core.moon.MoonArc`'s documented approximation).
        if not arc.full_circle:
            culm_pt = dial_point(arc.culmination_deg % 360.0, thread_radius)
            half = radius * _DIAMOND_HALF_FRACTION
            self._draw_diamond(painter, culm_pt, half, silver)

    # -- style 3: moon ticks ------------------------------------------------

    def _draw_ticks(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        """TICKS-ONLY (owner correction 2026-08-09): one discrete
        `MOON_SILVER` radial segment per degree — the SAME 1-per-degree
        spacing the baked tick art already uses — with NOTHING
        connecting them. No arc, no thread: the ticks turning silver
        and slightly longer IS the whole style, so it reads distinctly
        from "silver_thread" at a glance."""
        pen = QPen(QColor(palette.MOON_SILVER))
        pen.setWidthF(radius * _SILVER_TICK_SEGMENT_WIDTH_FRACTION)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        half_len = radius * _SILVER_TICK_HALF_LENGTH_FRACTION
        first = math.ceil(arc.start_deg)
        last = math.floor(arc.end_deg)
        for degree in range(first, last + 1):
            theta = degree % 360.0
            inner = dial_point(theta, radius - half_len)
            outer = dial_point(theta, radius + half_len)
            painter.drawLine(inner, outer)

    # -- style 4: moon glow ---------------------------------------------------

    def _draw_glow(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        base_radius = radius * (1.0 - _THREAD_INSET_FRACTION)
        for i in range(_GLOW_LAYERS):
            frac = 1.0 - i / _GLOW_LAYERS         # widest outermost, thin innermost
            width = radius * _GLOW_MAX_WIDTH_FRACTION * frac
            alpha = round(_GLOW_MAX_ALPHA * (i + 1) / _GLOW_LAYERS)
            color = QColor(palette.MOON_SILVER)
            color.setAlpha(alpha)
            painter.setBrush(color)
            outer = base_radius + width / 2.0
            inner = max(0.0, base_radius - width / 2.0)
            self._draw_ring_wedge(painter, outer, inner, arc)
        painter.restore()

    # -- shared drawing helpers -----------------------------------------

    def _stroke_arc(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
        qt_start = round((90.0 - arc.start_deg) * 16)
        qt_span = round(-(arc.end_deg - arc.start_deg) * 16)
        painter.drawArc(rect, qt_start, qt_span)

    def _draw_ring_wedge(
        self, painter: QPainter, outer_radius: float, inner_radius: float,
        arc: MoonArc,
    ) -> None:
        """A filled donut wedge between two radii, spanning `arc` — the
        glow style's one layered shape: a pie minus a smaller pie IS the
        donut wedge, the same clockwise-from-top sweep `draw_pie` uses."""
        qt_start = (90.0 - arc.start_deg)
        qt_span = -(arc.end_deg - arc.start_deg)
        outer_rect = QRectF(-outer_radius, -outer_radius, 2 * outer_radius, 2 * outer_radius)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.arcTo(outer_rect, qt_start, qt_span)
        path.closeSubpath()
        if inner_radius > 0:
            inner_rect = QRectF(-inner_radius, -inner_radius, 2 * inner_radius, 2 * inner_radius)
            hole = QPainterPath()
            hole.moveTo(0, 0)
            hole.arcTo(inner_rect, qt_start, qt_span)
            hole.closeSubpath()
            path = path.subtracted(hole)
        painter.drawPath(path)

    def _draw_diamond(
        self, painter: QPainter, center: QPointF, half: float, color: QColor,
    ) -> None:
        points = QPolygonF([
            QPointF(center.x(), center.y() - half),
            QPointF(center.x() + half, center.y()),
            QPointF(center.x(), center.y() + half),
            QPointF(center.x() - half, center.y()),
        ])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPolygon(points)
