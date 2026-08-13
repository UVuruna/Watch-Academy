"""THE MOON HORIZON BAND layer (owner verdict 2026-08-09) — an arc on
the dial's inner tick circle showing WHEN the Moon stands above the
horizon today, in one of four owner-approved visual styles.

Geometry comes entirely from `core.moon.moon_horizon_arcs` (Rule #5,
never re-derived here); this module only paints it.

THE HOUR FRAME RULE (owner order 2026-08-13). This docstring used to
say the band "NEVER rotates with `ctx.world_offset` in any world
mode", citing the Fidelity Ruling — and that was WRONG, in a way
worth naming because the mistake is a whole class. The band's radius
is the inner circle's for a GEOMETRIC reason (THE LAST LINE, below:
it must slice no inner-ring element); the round that placed it there
read the radius as membership and concluded the band belongs to the
fixed inner art. It does not. The outer circle is the HOURS and the
inner is minutes/seconds/calendar, and this band draws a span of
HOURS, so it rides the outer circle's frame however far from it it
happens to be painted. The owner saw the failure on his own dial and
named the law: everything that draws something happening in HOURS
follows the outer circle. `core.moon.shift_arcs` is the single door,
shared with `RingLayer._draw_band_redress` and the eclipse segment
below so the three halves of this band can never answer differently.

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

from config import constants, dial, glow, palette
from core import angles
from core.moon import MoonArc, moon_horizon_arcs, shift_arcs
from render.context import Cadence, Layer, RenderContext
from render.eclipse_glow import eclipse_render_state
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
# THE SEGMENT READS THE TYPE (eclipse rework, owner order 2026-08-13).
# Until the rework this mark was one copper bar drawn identically for a
# total, a partial and a penumbral eclipse, so choosing "horizon_shadow"
# meant the three lunar types became one picture. The DEPTH of the
# shadow is now the segment's WEIGHT — a full-thickness bar for
# totality, a slimmer one for a partial, a pale hairline for a
# penumbral eclipse, which is honest about how little of one there is
# to see.
_ECLIPSE_SEGMENT_STATE_WEIGHT = {
    "lunar_total": 1.0,
    "lunar_partial": 0.50,
    "lunar_penumbral": 0.22,
}
_ECLIPSE_SEGMENT_PENUMBRAL_DASH = (2.0, 2.0)   # in pen widths
# THE FOUR CONTACTS (owner ballot 2026-08-13, "contact_marks"): lines
# across the band at P1, U1, U4, P4, each seated with a diamond — the
# SAME diamond vocabulary the silver thread's culmination mark already
# speaks, so a moment marked on this band always looks like a moment
# marked on this band.
#
# The radial reach is stated as a multiple of the SEGMENT's own full
# width, so the marks and the bar they straddle can never drift apart.
# The umbral pair are longer, wider and copper; the penumbral pair
# shorter, thinner and grey — which is how the picture says which pair
# is which without a legend.
#
# MEASURED, not eyeballed, and the trail is worth keeping because it is
# the whole argument for the numbers. Cut 1 used hairlines (0.011 of the
# band radius, reach 1.10) and the distinctness tooth scored it 0.030
# structure against the plain "horizon_shadow" segment — far under the
# 0.20 floor, i.e. the same picture. Cut 2 (the widths below, plus the
# diamonds) reached 0.048-0.079: better, still one picture. What finally
# carried was not more ink on the four lines but the PENUMBRAL SPAN ARC
# below — the thing this style knows and "horizon_shadow" does not —
# which took the three lunar types to 0.229/0.238/0.248. A mark too
# faint for that measure is a mark too faint to see.
_CONTACT_UMBRAL_REACH = 2.40       # of the full segment width, each side
_CONTACT_PENUMBRAL_REACH = 1.60
_CONTACT_UMBRAL_WIDTH_FRACTION = 0.024    # of the band radius
_CONTACT_PENUMBRAL_WIDTH_FRACTION = 0.016
_CONTACT_UMBRAL_DIAMOND_FRACTION = 0.055  # radial half-LENGTH, of the radius
_CONTACT_PENUMBRAL_DIAMOND_FRACTION = 0.038
# THE PENUMBRAL SPAN the outer pair brackets, drawn as a thin dashed arc
# just outside the copper bar — P1 to P4. It is the one thing this style
# says that "horizon_shadow" cannot: the eclipse's WHOLE duration, not
# only its umbral part. Dashed, because like every time on this band it
# is INDICATIVE (see `draw_contact_marks`).
_CONTACT_SPAN_ARC_WIDTH_FRACTION = 0.042   # of the band radius
_CONTACT_SPAN_ARC_OFFSET = 2.05            # of the full segment width, outward
_CONTACT_SPAN_ARC_DASH = (4.0, 1.6)        # in pen widths


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
        arcs = shift_arcs(
            moon_horizon_arcs(ctx.day.moonrise, ctx.day.moonset),
            ctx.world_offset,
        )
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
        # THE DOOR (owner ballot 2026-08-13): every lunar style asks
        # `render.eclipse_style.resolve_eclipse_style` what actually
        # paints. The band is up here (the mode gate above already
        # returned otherwise), so `band_available=True`.
        from render.eclipse_style import resolve_eclipse_style

        effective_style, _fallback_reason = resolve_eclipse_style(
            "lunar", spec.eclipse_lunar_style, band_available=True,
        )
        if effective_style in ("horizon_shadow", "contact_marks"):
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
                # THE HOUR FRAME RULE again: these marks say WHEN the
                # eclipse happens, so they turn with the band they are
                # laid over — the eclipse BODY on the ring already did
                # (`year_marker.eclipse_body_angle`), and the marks of
                # one event must never stand at two different hours.
                centre_deg = (
                    angles.time_to_dial_angle(local_instant)
                    + ctx.world_offset
                )
                state = eclipse_render_state(event)
                self.draw_eclipse_segment(painter, radius, centre_deg, state)
                if effective_style == "contact_marks":
                    # AN ADDITION, never a replacement (owner ballot
                    # 2026-08-13): the segment above still draws and
                    # these four lines bracket it.
                    self.draw_contact_marks(
                        painter, radius, centre_deg, state
                    )
        painter.restore()

    def draw_eclipse_segment(
        self, painter: QPainter, radius: float, centre_deg: float,
        state: str,
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
        contact times would be inventing them.

        `state` is the eclipse's own render state, and it decides the
        segment's WEIGHT and colour (`_ECLIPSE_SEGMENT_STATE_WEIGHT`):
        the three lunar types drew one identical bar until the rework,
        which made "horizon_shadow" type-blind."""
        half = constants.ECLIPSE_BAND_DURATION_H / 24.0 * 360.0 / 2.0
        width = radius * _ECLIPSE_SEGMENT_WIDTH_FRACTION * (
            _ECLIPSE_SEGMENT_STATE_WEIGHT[state]
        )
        rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
        # A penumbral eclipse never wears the blood copper — nothing on
        # the Moon turns copper in the penumbra — so it takes the same
        # pale grey the "cannot be seen from here" muting uses.
        pen = QPen(QColor(
            palette.GLOW_ECLIPSE_INVISIBLE_COLOR
            if state == "lunar_penumbral" else palette.ECLIPSE_TOTAL_MOON_TINT
        ))
        pen.setWidthF(width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        if state == "lunar_penumbral":
            # BROKEN, because a penumbral eclipse has no sharp edge to
            # draw anywhere: the Moon only fades. A dashed hairline says
            # "faint and indistinct" where a solid bar would claim a
            # shadow that never falls.
            pen.setDashPattern(list(_ECLIPSE_SEGMENT_PENUMBRAL_DASH))
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(pen)
        painter.drawArc(
            rect, round((90.0 - (centre_deg - half)) * 16), round(-2 * half * 16)
        )
        # The turquoise rim at each end — the SAME ozone colour the disc
        # treatments wear, so one eclipse reads as one event wherever it
        # is drawn, and withheld from a penumbral eclipse for the same
        # reason the disc withholds it (`glow.ECLIPSE_STATE_FRINGE`:
        # there is no darkened sky rim to show).
        if not glow.ECLIPSE_STATE_FRINGE[state]:
            painter.restore()
            return
        edge = QPen(QColor(palette.ECLIPSE_LUNAR_FRINGE_COLOR))
        edge.setWidthF(width * _ECLIPSE_SEGMENT_EDGE_FRACTION)
        painter.setPen(edge)
        for end in (centre_deg - half, centre_deg + half):
            inner = dial_point(end % 360.0, radius - width / 2.0)
            outer = dial_point(end % 360.0, radius + width / 2.0)
            painter.drawLine(inner, outer)
        painter.restore()

    def draw_contact_marks(
        self, painter: QPainter, radius: float, centre_deg: float,
        state: str,
    ) -> None:
        """THE FOUR CONTACTS (owner ballot 2026-08-13, "contact_marks"):
        P1, U1, U4, P4 as four thin lines across the band. It is an
        ADDITION on top of "horizon_shadow", never a replacement — the
        copper segment is still drawn, and these bracket it.

        THE APPROXIMATION IS NOT UPGRADED INTO A CLAIM. The catalog
        stores only the instant of GREATEST eclipse (see
        `constants.ECLIPSE_BAND_DURATION_H`'s own note), so these are
        NOT observed contact times and the docs say so in those words.
        The umbral pair sit at half of that same documented span either
        side of the peak — the identical approximation the segment
        already draws, kept in the one place — and the penumbral pair at
        `constants.ECLIPSE_PENUMBRAL_SPAN_RATIO` times that, a ratio
        derived from the two shadow radii rather than guessed a second
        time.

        A PENUMBRAL eclipse draws only P1 and P4: the Moon never enters
        the umbra, so U1 and U4 do not exist, and drawing them would be
        the invention this whole note exists to refuse."""
        umbral_half = constants.ECLIPSE_BAND_DURATION_H / 24.0 * 360.0 / 2.0
        penumbral_half = umbral_half * constants.ECLIPSE_PENUMBRAL_SPAN_RATIO
        width = radius * _ECLIPSE_SEGMENT_WIDTH_FRACTION
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # THE PENUMBRAL SPAN first, under the ticks that bracket it: a
        # thin dashed arc from P1 to P4, just outside the copper bar.
        # This is what the four contacts are FOR — the umbral bar shows
        # the deep phase, this shows the whole event, and "horizon_
        # shadow" shows only the first.
        span_radius = radius + width * _CONTACT_SPAN_ARC_OFFSET
        span_pen = QPen(QColor(palette.ECLIPSE_CONTACT_PENUMBRAL_COLOR))
        span_pen.setWidthF(max(1.0, radius * _CONTACT_SPAN_ARC_WIDTH_FRACTION))
        span_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        span_pen.setDashPattern(list(_CONTACT_SPAN_ARC_DASH))
        painter.setPen(span_pen)
        self._stroke_arc(
            painter, span_radius,
            MoonArc(
                centre_deg - penumbral_half, centre_deg + penumbral_half,
                centre_deg,
            ),
        )
        marks = [
            (penumbral_half, _CONTACT_PENUMBRAL_REACH,
             _CONTACT_PENUMBRAL_WIDTH_FRACTION,
             _CONTACT_PENUMBRAL_DIAMOND_FRACTION,
             palette.ECLIPSE_CONTACT_PENUMBRAL_COLOR),
        ]
        if state != "lunar_penumbral":
            marks.append((
                umbral_half, _CONTACT_UMBRAL_REACH,
                _CONTACT_UMBRAL_WIDTH_FRACTION,
                _CONTACT_UMBRAL_DIAMOND_FRACTION,
                palette.ECLIPSE_TOTAL_MOON_TINT,
            ))
        for half, reach, width_fraction, diamond, color in marks:
            pen = QPen(QColor(color))
            pen.setWidthF(max(1.0, radius * width_fraction))
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            for end in (centre_deg - half, centre_deg + half):
                theta = end % 360.0
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawLine(
                    dial_point(theta, radius - width * reach),
                    dial_point(theta, radius + width * reach),
                )
                self._draw_diamond(
                    painter, theta, radius, radius * diamond, QColor(color),
                )
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
