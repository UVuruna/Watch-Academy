"""The RING layer — the dial face, its letters and word legend."""

import math
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen

from config import constants, dial, palette
from core import angles
from render.asset_recolor import letter_metal_file
from render.context import Cadence, Layer, RenderContext
from render.painting import dial_point, draw_pixmap_centered


class RingLayer(Layer):
    """Outer ring: donut, hour ticks, 24h numerals with per-skin letters,
    minute numbers along the inner edge."""

    cadence = Cadence.STATIC

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.ring
        if spec.asset is not None:
            # The ring art carries numerals and minutes; the ring tint
            # multiplies the art. The LETTERS are the owner's separate
            # gold/silver art, overlaid by calculation so the tint never
            # touches them (1x1 placeholders until his files land). The
            # RING SATURATION slider (owner 2026-07-18, Session 21-D)
            # scales the plate's saturation AFTER the tint recolor — the
            # plate is grayscale-mastered, so saturating the pre-tint
            # source would be a no-op; the tinted OUTPUT is what actually
            # carries hue.
            draw_pixmap_centered(
                painter, ctx, spec.asset, QPointF(0, 0), 2 * ctx.radius,
                tint=ctx.skin.ring_tint, saturation=ctx.skin.ring_saturation,
            )
            self._draw_letter_art(painter, ctx)
            self._draw_motto(painter, ctx)
            return
        outer, inner = ctx.radius, ctx.radius * (1.0 - spec.width_fraction)

        ring = QPainterPath()
        # (procedural fallback ring below — no tint, no letter art)
        ring.addEllipse(QRectF(-outer, -outer, 2 * outer, 2 * outer))
        ring.addEllipse(QRectF(-inner, -inner, 2 * inner, 2 * inner))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(ring, QColor(spec.fill))

        # Explicit QPen — copying painter.pen() would inherit the NoPen
        # STYLE set for the donut fill and the ticks would never render.
        painter.setPen(
            QPen(QColor(spec.text_color), max(1.0, ctx.radius * dial.RING_TICK_WIDTH))
        )
        for hour in range(constants.HOURS_PER_REVOLUTION):
            theta = (hour * 15.0 + constants.DIAL_OFFSET_DEG) % 360.0
            painter.drawLine(
                dial_point(theta, inner),
                dial_point(theta, inner * dial.RING_TICK_REACH),
            )

        numeral_font = QFont()
        numeral_font.setPixelSize(
            max(dial.RING_NUMERAL_MIN_PX, round(ctx.radius * dial.RING_NUMERAL_SIZE))
        )
        numeral_font.setBold(True)
        letter_font = QFont()
        letter_font.setPixelSize(
            max(dial.RING_LETTER_MIN_PX, round(ctx.radius * dial.RING_LETTER_SIZE))
        )
        letter_font.setBold(True)
        mid = (outer + inner) / 2
        box = ctx.radius * dial.RING_TEXT_BOX
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
            max(dial.RING_MINUTE_MIN_PX, round(ctx.radius * dial.RING_MINUTE_SIZE))
        )
        painter.setFont(minute_font)
        painter.setPen(QColor(spec.text_color))
        minute_radius = inner * dial.RING_MINUTE_RADIUS
        for minute in range(5, 60, 5):
            center = dial_point(minute * 6.0, minute_radius)
            rect = QRectF(center.x() - box / 2, center.y() - box / 2, box, box)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(minute))

    def _draw_ring_glyph(
        self, painter: QPainter, ctx: RenderContext, gold_asset: Path,
        metal: str, theta: float, radius_fraction: float, height: float,
    ) -> None:
        """One letter-art glyph stamped on the ring circle — the shared
        stamp (Rule #5) behind BOTH the ring's own six banknote letters
        (`_draw_letter_art`) and the outer motto arc (`_draw_motto`,
        TASK 1, owner "može radi" 2026-07-19): the metal finish (derived
        from the gold master, `render.asset_recolor.letter_metal_file`), a
        tight dark halo (owner spec: a gradient border, lit from above)
        and a tangential ROTATION that flips 180° through the lower half
        so text never reads upside down (Ω stands upright at the
        bottom — `core.angles.readable_rotation_deg`). UNTINTED by the
        ring hue either way, but the RING SATURATION slider still grays
        it (owner 2026-07-18, Session 21-D: "the ring plate + its
        letters" is one target); the shadow copy skips it — a pure
        black silhouette has no saturation to scale."""
        shadow_radius = height * dial.RING_LETTER_SHADOW_RADIUS
        samples = dial.RING_LETTER_SHADOW_SAMPLES
        # Silver/bronze are derived from the gold master AT LOAD (owner
        # 2026-07-19), disk-cached like every other derived asset — the
        # shadow silhouette is metal-invariant (same alpha mask on every
        # finish), so it always reads the gold file directly.
        asset = letter_metal_file(gold_asset, metal)
        pixmap = ctx.cache.pixmap_by_height(
            asset, height, ctx.dpr, saturation=ctx.skin.ring_saturation
        )
        shadow = ctx.cache.pixmap_by_height(
            gold_asset, height, ctx.dpr, tint=palette.SHADOW_STAMP_TINT
        )
        logical_w = pixmap.width() / ctx.dpr
        pos = dial_point(theta, ctx.radius * radius_fraction)
        rotation = angles.readable_rotation_deg(theta)
        painter.save()
        painter.translate(pos)
        painter.rotate(rotation)
        painter.setOpacity(dial.RING_LETTER_SHADOW_ALPHA)
        for k in range(samples):
            angle = 2.0 * math.pi * k / samples
            painter.drawPixmap(
                QPointF(
                    -logical_w / 2 + shadow_radius * math.cos(angle),
                    -height / 2 + shadow_radius * math.sin(angle),
                ),
                shadow,
            )
        painter.setOpacity(1.0)
        painter.drawPixmap(QPointF(-logical_w / 2, -height / 2), pixmap)
        painter.restore()

    def _draw_letter_art(self, painter: QPainter, ctx: RenderContext) -> None:
        """The owner's letter art at the preset's hour positions — gold
        masters, silver/bronze derived at load (the accent letter wears
        the opposite metal, owner spec). Stamped by `_draw_ring_glyph`
        (Rule #5, shared with the outer motto arc)."""
        height = (
            2 * ctx.radius * dial.RING_LETTER_ART_SCALE
            * ctx.skin.ring_letter_scale
        )
        for hour, gold_asset in self._skin.ring.letter_art.items():
            theta = angles.ring_position_angle(hour)
            metal = self._skin.ring.letter_metal.get(hour, "gold")
            # The Eye's SHINE ENLARGE (owner UV inbox 2026-07-27):
            # build_skin stamps a per-hour height multiplier for the
            # shine masters so the triangle stays the no-light size and
            # only the rays extend beyond it (1.0 for plain letters).
            self._draw_ring_glyph(
                painter, ctx, gold_asset, metal, theta,
                dial.RING_LETTER_RADIUS_FRACTION,
                height * self._skin.ring.letter_zoom.get(hour, 1.0),
            )

    def _draw_motto(self, painter: QPainter, ctx: RenderContext) -> None:
        """The outer GREAT SEAL MOTTO ARC (MOTO-FIX round, owner
        correction 2026-07-19, the dollar's Great Seal reference
        image): each character of the preset's `motto` texts —
        pre-solved to its own dial angle by `data.rings`/`core.motto`
        (ANNUIT COEPTIS's own A/S pin the TOP arc at 8h/16h, NOVUS ORDO
        SECLORUM's own N/O/M pin the BOTTOM arc at 4h/24h/20h — MASON
        outside, G inside) — drawn via the SAME stamp the ring's own
        six letters use (`_draw_ring_glyph`, Rule #5), just smaller
        (`RING_MOTTO_SIZE`) and further out. The two arcs are angularly
        DISJOINT (top 300-360-60 deg, bottom 120-180-240 deg) so both
        share ONE radius (`RING_MOTTO_RADIUS_FRACTION`) — no more two
        concentric rings of text. Empty (no-op) for every preset
        without a motto."""
        mottos = self._skin.ring.motto
        if not mottos:
            return
        height = (
            2 * ctx.radius * dial.RING_MOTTO_SIZE * ctx.skin.ring_letter_scale
        )
        metal = self._skin.ring.motto_metal
        for motto in mottos:
            for gold_asset, theta in motto["glyphs"]:
                self._draw_ring_glyph(
                    painter, ctx, gold_asset, metal, theta % 360.0,
                    dial.RING_MOTTO_RADIUS_FRACTION, height,
                )
