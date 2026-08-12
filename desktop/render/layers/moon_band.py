"""THE MOON HORIZON BAND layer (owner verdict 2026-08-09) — an arc on
the dial's inner tick circle showing WHEN the Moon stands above the
horizon today, in one of four owner-approved visual styles.

Geometry comes entirely from `core.moon.moon_horizon_arcs` (Rule #5,
never re-derived here); this module only paints it. That band NEVER
rotates with `ctx.world_offset` in any world mode (the Fidelity
Ruling, `render.layers.numerals`'s own "ledger §2"), so this layer
does not apply the world offset either; it stays in registration with
the fixed tick art underneath.

THE LAST LINE (owner third round, 2026-08-11 — his explicit words
after two wrong re-cuts): every style's line follows the INNER side
of the INNER ring — `dial.RING_INNER_CONTENT_INNER_FRACTION`, the
measured radius where the five-minute strokes/arrows/numbers stop, so
the line slices NO inner-ring element. The Earth/Moon orbit is
tangent to the SAME line from inside (`dial.earth_moon_orbit_
fraction`), the position-pointer arrow bridges from there across the
band to the small ticks' tips, and this whole layer sits BELOW the
ring in the z-order (his z decree: hands+bodies, then ring elements,
then these circles).

Per style, all four re-cut to his screenshot corrections of 2026-08-10:
- "inverted" fills ONLY the belt from the line out to the hour band
  (the ticks' own zone — "where the pointers are"), never the whole
  interior, using `CompositionMode_Difference` (a true RGB invert of
  the baked tick art — the honesty note: the ticks are the owner's own
  PNG plate, there is no per-tick recolor hook to reach into).
- "silver_thread" keeps its dots but the culmination diamond is LONGER
  than wide (radially seated), never the squat square of the first cut.
- "ticks" draws one discrete GRAY segment per degree spanning exactly
  the plate's own tick zone (`palette.MOON_BAND_TICK_GRAY` — his
  words: "the gray lines that show the 360 steps in the INNER RING"),
  with NOTHING connecting them (his 2026-08-09 correction, kept).
- "glow" is stroked soft-capped arcs — the first cut's stacked filled
  wedges read as a pixelated smear with chopped-off ends.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF

from config import constants, dial, palette
from core import angles
from core.moon import MoonArc, moon_horizon_arcs
from render.context import Cadence, Layer, RenderContext
from render.painting import dial_point

# Radial geometry (fractions of the LINE radius — the tick ROOTS, the
# end of the inner circle; owner correction 2026-08-11). The little
# pointers hang INWARD from the line; their tips' radius is not a free
# choice but the measured plate geometry, so it derives from the two
# `config.dial` measurements and never drifts from the art.
_TICKS_FROM_LINE_RATIO = (
    dial.RING_INNER_TICK_INNER_FRACTION / dial.RING_INNER_CONTENT_INNER_FRACTION
)
_TICK_ROOTS_FROM_LINE_RATIO = (
    dial.RING_INNER_TICK_OUTER_FRACTION / dial.RING_INNER_CONTENT_INNER_FRACTION
)
# THE SPARED SEATS (owner correction 2026-08-11, slika 1/2: the invert
# and the gray ticks touch ONLY the background aura/umbra and the 360
# little points — never the big strokes, the arrows or the numbers).
# MEASURED, not assumed (owner slika 6/7 repeat, 2026-08-11): the first
# cut spared every 6th degree, but pixel-sampling the plate itself
# (`simple_point.png`, opaque runs at 0.80 of plate radius) shows the
# BIG strokes stand every FIFTEEN degrees (24 of them, ~1 deg wide with
# their white border), so segments kept landing straight on the big
# pointers at 15, 45, 75... A one-degree shoulder around every 15-degree
# seat clears the stroke and its border while the 360 hairlines at all
# other integer degrees stay dressable.
def _seat_spared(degree: int) -> bool:
    return min(degree % 15, 15 - degree % 15) <= 1
_GRAY_TICK_SEGMENT_WIDTH_FRACTION = 0.010  # each discrete tick's own line width (style 3)
_THREAD_WIDTH_FRACTION = 0.006         # style 2's thin thread
_DOT_RADIUS_FRACTION = 0.014
_DIAMOND_HALF_LENGTH_FRACTION = 0.022  # culmination diamond, radial half-LENGTH
_DIAMOND_WIDTH_RATIO = 0.45            # its tangential half-width, OF that length
_GLOW_LAYERS = 8
_GLOW_MAX_WIDTH_FRACTION = 0.08
_GLOW_MAX_ALPHA = 88       # of 255, innermost layer
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
        # THE LAST LINE (owner third round 2026-08-11, finally explicit:
        # every band line follows the INNER side of the INNER ring —
        # the last line that slices no inner-ring element, where the
        # five-minute strokes/arrows/numbers stop). Two earlier re-cuts
        # used the tick tips and then the hour-band edge; both wrong.
        radius = ctx.radius * dial.RING_INNER_CONTENT_INNER_FRACTION
        style = spec.moon_band_style
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for arc in arcs:
            # THE SPLIT ACROSS THE RING (owner z decree + slika 2,
            # 2026-08-11): this layer sits BELOW the ring, so it paints
            # only the parts that live OUTSIDE the plate — the line,
            # the glow, the thread's dots/diamond. The per-degree tick
            # redress of "inverted"/"ticks" must touch the plate's own
            # 360 points, so it paints INSIDE the ring layer instead
            # (`RingLayer._draw_band_redress`, between base plate and
            # content) — it REPLACES the ticks' style at those places,
            # which is his own definition of those two styles.
            if style == "inverted":
                self._stroke_thread(painter, radius, arc)
            elif style == "ticks":
                pass                     # segments only — upper layer
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
                # ONLY THE DISPLAYED DAY'S OWN ECLIPSE (owner bug
                # 2026-08-11, slika 3: the copper segment stood on the
                # band on a plain day — `day.eclipses` carries the
                # NEAREST catalog events, months away included, and the
                # first cut drew a segment for every one of them. The
                # band shows TODAY; an eclipse that is not today's has
                # no seat on it).
                local_instant = event.instant.astimezone(ctx.day.tzinfo)
                if local_instant.date() != ctx.day.local_date:
                    continue
                self.draw_eclipse_segment(
                    painter, radius,
                    angles.time_to_dial_angle(local_instant),
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

    def _draw_invert_segments(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        """THE INVERTED BELT (owner corrections 2026-08-10/11): only
        the little pointers' zone inside the line, and inside it ONLY
        the background and the little points themselves — one Difference
        wedge per non-spared degree, so the big strokes, the arrows and
        the numbers are never inverted (slika 1's exact complaint: the
        first re-cut ran the invert across everything in the belt).
        A true RGB Difference against the baked art (the honesty note
        in the module docstring), plus the line itself."""
        tick_inner = radius * _TICKS_FROM_LINE_RATIO
        tick_outer = radius * _TICK_ROOTS_FROM_LINE_RATIO
        painter.save()
        pen = QPen(QColor(255, 255, 255))
        # One near-degree-wide radial segment per spared-degree — a
        # thick Difference stroke, never a centre-anchored pie wedge (a
        # 1-degree pie-minus-pie path degenerates and leaks rays to the
        # dial centre; the segment is the honest shape of one step).
        pen.setWidthF(radius * math.radians(1.0) * 0.85)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Difference)
        first = math.ceil(arc.start_deg)
        last = math.floor(arc.end_deg)
        for degree in range(first, last + 1):
            if _seat_spared(degree % 360):
                continue
            theta = degree % 360.0
            painter.drawLine(
                dial_point(theta, tick_inner), dial_point(theta, tick_outer)
            )
        painter.restore()

    def _draw_inverted(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        """The preview/one-canvas path: both halves of the style — the
        thread and the invert segments — on one painter. The dial
        splits them across the ring (`paint` above /
        `RingLayer._draw_band_redress`)."""
        self._draw_invert_segments(painter, radius, arc)
        self._stroke_thread(painter, radius, arc)

    # -- style 2: silver thread (THE DEFAULT) ------------------------------

    def _draw_silver_thread(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        silver = QColor(palette.MOON_SILVER)
        pen = self._line_pen(radius)
        self._stroke_thread(painter, radius, arc)

        dot_r = radius * _DOT_RADIUS_FRACTION
        start_pt = dial_point(arc.start_deg % 360.0, radius)
        end_pt = dial_point(arc.end_deg % 360.0, radius)
        edge = QPen(QColor(palette.MOON_BAND_LINE_EDGE))
        edge.setWidthF(pen.widthF() * 0.8)
        # Filled dot at moonrise, edged so it reads on a light plate too.
        painter.setPen(edge)
        painter.setBrush(silver)
        painter.drawEllipse(start_pt, dot_r, dot_r)
        # Hollow dot at moonset.
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(end_pt, dot_r, dot_r)
        # Diamond at culmination (the arc's own midpoint — see
        # `core.moon.MoonArc`'s documented approximation), seated
        # RADIALLY: longer than wide (owner correction 2026-08-10 —
        # the first cut shipped the proportion inverted).
        if not arc.full_circle:
            self._draw_diamond(
                painter, arc.culmination_deg % 360.0, radius,
                radius * _DIAMOND_HALF_LENGTH_FRACTION, silver,
            )

    # -- style 3: moon ticks ------------------------------------------------

    def _draw_ticks(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        """GRAY TICKS ON THE PLATE'S OWN STEPS (owner corrections
        2026-08-09 and 2026-08-10): one discrete GRAY radial segment
        per degree — the SAME 1-per-degree spacing the baked tick art
        uses, spanning exactly the plate's own measured tick zone, so
        the style reads as the clock's own 360 steps lighting up in
        gray, not as loose white lines crossing the band. NOTHING
        connects them (the 2026-08-09 correction, kept): no arc, no
        thread."""
        pen = QPen(QColor(palette.MOON_BAND_TICK_GRAY))
        pen.setWidthF(radius * _GRAY_TICK_SEGMENT_WIDTH_FRACTION)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        tick_inner = radius * _TICKS_FROM_LINE_RATIO
        tick_outer = radius * _TICK_ROOTS_FROM_LINE_RATIO
        first = math.ceil(arc.start_deg)
        last = math.floor(arc.end_deg)
        for degree in range(first, last + 1):
            if _seat_spared(degree % 360):
                # The seats keep the plate's own strokes/numbers/arrows
                # (owner correction 2026-08-11, slika 2) — this style
                # only re-dresses the little points themselves.
                continue
            theta = degree % 360.0
            painter.drawLine(
                dial_point(theta, tick_inner), dial_point(theta, tick_outer)
            )

    # -- style 4: moon glow ---------------------------------------------------

    def _draw_glow(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        """Soft-capped STROKED arcs (owner correction 2026-08-10: the
        first cut's stacked filled wedges read as a pixelated smear
        with chopped-off flat ends). Concentric round-capped strokes of
        tapering width build the bloom; the round caps ARE the soft
        ends, and each layer's span retreats by its own cap radius so
        the ends taper instead of stacking into a wall."""
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        span = arc.end_deg - arc.start_deg
        for i in range(_GLOW_LAYERS):
            frac = 1.0 - i / _GLOW_LAYERS         # widest outermost, thin innermost
            width = radius * _GLOW_MAX_WIDTH_FRACTION * frac
            alpha = round(_GLOW_MAX_ALPHA * (i + 1) / _GLOW_LAYERS)
            color = QColor(palette.MOON_SILVER)
            color.setAlpha(alpha)
            pen = QPen(color)
            pen.setWidthF(width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            # The cap's own angular radius at this width — the retreat
            # that tapers the ends. A full circle never retreats.
            inset_deg = (
                0.0 if arc.full_circle
                else math.degrees(width / (2.0 * radius))
            )
            inset_deg = min(inset_deg, span / 2.0)
            self._stroke_arc(
                painter, radius,
                MoonArc(
                    arc.start_deg + inset_deg, arc.end_deg - inset_deg,
                    arc.culmination_deg, full_circle=arc.full_circle,
                ),
            )
        painter.restore()

    # -- shared drawing helpers -----------------------------------------

    def _line_pen(self, radius: float) -> QPen:
        pen = QPen(QColor(palette.MOON_SILVER))
        pen.setWidthF(radius * _THREAD_WIDTH_FRACTION)
        return pen

    def _stroke_thread(self, painter: QPainter, radius: float, arc: MoonArc) -> None:
        """THE LINE itself, two-tone: a slate under-stroke below the
        silver so it reads on a light inner plate as well as a dark one
        (`palette.MOON_BAND_LINE_EDGE`'s own note)."""
        painter.setBrush(Qt.BrushStyle.NoBrush)
        under = QPen(QColor(palette.MOON_BAND_LINE_EDGE))
        under.setWidthF(radius * _THREAD_WIDTH_FRACTION * 2.4)
        painter.setPen(under)
        self._stroke_arc(painter, radius, arc)
        painter.setPen(self._line_pen(radius))
        self._stroke_arc(painter, radius, arc)

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
        self, painter: QPainter, angle_deg: float, radius: float,
        half_length: float, color: QColor,
    ) -> None:
        """The culmination diamond, seated RADIALLY on the line at its
        own dial angle: its long axis points along the radius and its
        width is `_DIAMOND_WIDTH_RATIO` of the length — longer than
        wide by construction (owner correction 2026-08-10)."""
        theta = math.radians(angle_deg)
        radial = QPointF(math.sin(theta), -math.cos(theta))
        tangent = QPointF(-radial.y(), radial.x())
        center = dial_point(angle_deg, radius)
        half_width = half_length * _DIAMOND_WIDTH_RATIO
        points = QPolygonF([
            center + radial * half_length,
            center + tangent * half_width,
            center - radial * half_length,
            center - tangent * half_width,
        ])
        edge = QPen(QColor(palette.MOON_BAND_LINE_EDGE))
        edge.setWidthF(radius * _THREAD_WIDTH_FRACTION * 0.8)
        painter.setPen(edge)
        painter.setBrush(color)
        painter.drawPolygon(points)


# The former MoonBandTicksLayer is RETIRED (owner repeat correction
# 2026-08-11, slika 5-7): a whole layer above the ring inverted the
# jewels and the big pointers with it. The per-degree redress paints in
# `render.layers.ring.RingLayer._draw_band_redress` now — between the
# base plate and every ring element — calling `_draw_invert_segments`/
# `_draw_ticks` above (Rule #5, one drawing, one home).
