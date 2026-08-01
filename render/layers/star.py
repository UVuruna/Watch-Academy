"""The STAR layer — the hexagram/polygon arms over the lit day."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen

from config import dial, palette
from render.context import Cadence, Layer, RenderContext
from render.daylight import border_clips, lit_regions
from render.painting import pie_path
from render.shapes import arm_shape_path, drawn_arms
from render.skin_geometry import daylight_active, palette_for, wheel_rotation


class StarLayer(Layer):
    """The drawn wheel — an N-diamond STAR or the plain POLYGON of the
    same arms (owner sheet 2026-07-29) — whose top arm points at true
    solar noon (or straight up with solar rotation off). Colored
    near-full opacity where the sun is up, borders elsewhere (owner
    model). The armless Aurora draws nothing here; the Calendar draws
    its two hexagrams / twelve-point star over its own wedges."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.star
        if ctx.skin.pointer == "aurora":
            return          # no geometry at all — the wheel IS the pointer

        # Colored BORDERS run the full circle so the night arms stay
        # recognizable (owner spec) — unless the reader asked for the
        # night to keep its fills alone (`border_clips`)...
        for clip in border_clips(ctx.skin, ctx.day.sun):
            self._paint_pass(painter, ctx, False, spec.border_alpha, clip)

        # ...while the FILLS appear only where the sun is up — UNLESS
        # the reader switched the daylight law off (owner 2026-07-27:
        # the Calendar and the Rose carry that switch), in which case
        # the whole wheel stands in flat full color.
        if not daylight_active(ctx.skin):
            self._paint_pass(painter, ctx, True, spec.day_alpha, None)
            return
        for start, end, alpha in lit_regions(ctx.day.sun, spec):
            self._paint_pass(painter, ctx, True, alpha, (start, end))

    def _paint_pass(
        self, painter: QPainter, ctx: RenderContext, fill: bool,
        alpha: float, clip: tuple[float, float] | None,
    ) -> None:
        """One whole-wheel pass at `alpha`, optionally clipped to a dial
        arc (the lit regions; None = the full circle). The clip is taken
        in WALL-CLOCK dial space, the wheel drawn inside it in its own
        rotated frame — the standing order."""
        painter.save()
        if clip is not None:
            painter.setClipPath(pie_path(ctx.radius, *clip))
        painter.setOpacity(alpha)
        painter.rotate(wheel_rotation(ctx.skin, ctx.rotation))
        self._draw_arms(painter, ctx, fill)
        painter.restore()

    def _draw_arms(
        self, painter: QPainter, ctx: RenderContext, fill: bool
    ) -> None:
        """Every arm of every pass, in z-order (`drawn_arms`) — the
        Rose's three stars bottom-first, the Calendar's odd hexagram
        under its even one, one pass everywhere else. The SHAPE is the
        arm's own path (`arm_shape_path`); nothing else here knows
        whether a star or a polygon is being drawn."""
        spec = self._skin.star
        tip = ctx.radius * spec.radius_fraction
        border_width = max(1.0, ctx.radius * spec.border_width_fraction)
        lead = QPen(
            QColor(palette.ARM_OUTLINE),
            max(1.0, ctx.radius * dial.ARM_OUTLINE_WIDTH),
        )
        for arms in drawn_arms(ctx.skin, palette_for(ctx.skin)):
            for theta, color in arms:
                shape = arm_shape_path(ctx.skin, tip, theta)
                if fill:
                    # THE LEAD LINE (owner's correction round
                    # 2026-07-29 — the Rose's dark lead was "the good
                    # example", so every pointer wears it now): each arm
                    # or polygon face is stroked AS IT IS FILLED, in
                    # draw order, so the outline follows the z-stack and
                    # the INTERNAL colour boundaries come free — every
                    # face is its own path, and stroking the path draws
                    # the edges it shares with its neighbours. The
                    # armless Aurora never reaches here at all.
                    painter.setPen(lead)
                    painter.setBrush(QColor(color))
                    painter.drawPath(shape)
                else:
                    # Border as PADDING (owner spec): clip to the arm and
                    # stroke at double width, so only the inner half
                    # shows — neighboring arms' borders sit side by side
                    # instead of overpainting each other along shared
                    # edges. INTERSECT, never replace: the pass may
                    # already be clipped to the sunlit arcs
                    # (`hide_night_borders`), and a plain setClipPath
                    # would throw that away and stroke the night too.
                    painter.save()
                    painter.setClipPath(shape, Qt.ClipOperation.IntersectClip)
                    painter.setPen(QPen(QColor(color), 2.0 * border_width))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawPath(shape)
                    painter.restore()
