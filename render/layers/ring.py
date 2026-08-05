"""The RING layer — THE COMPOSITIONAL RING MODEL (owner decree
2026-08-05): a ring is ALWAYS the composition of an outer band, an
inner band, the preset's own letters and an optional crown-text motto
arc. No monolithic single-plate ring face and no procedural fallback
exist any more — every skin's `RingSpec` carries a real
`outer_asset`/`inner_asset` pair (`config.defaults`, `app.controller.
_compose_skin`), so this layer composes unconditionally.
"""

import math
from pathlib import Path

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from config import dial, palette
from core import angles
from render.asset_recolor import letter_metal_file
from render.context import Cadence, Layer, RenderContext
from render.painting import dial_point, draw_pixmap_centered


class RingLayer(Layer):
    """The composed ring: outer band, inner band, the preset's own
    letters (with per-hour metal finish) and the optional crown-text
    motto arc."""

    cadence = Cadence.STATIC

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        self._draw_bands(painter, ctx)
        self._draw_letter_art(painter, ctx)
        self._draw_motto(painter, ctx)

    def _draw_bands(self, painter: QPainter, ctx: RenderContext) -> None:
        """The outer + inner band composition — inner drawn FIRST so the
        outer band's own edge sits on top. `ring_tint_inner` None
        follows `ring_tint`, the SAME "follow-unless-overridden" shape
        `hands_tint` uses — the outer band's tint semantics are the
        product's own long-standing ones (RING SATURATION, owner
        2026-07-18, Session 21-D, scales the plate's saturation AFTER
        the tint recolor — both plates are grayscale-mastered)."""
        spec = self._skin.ring
        inner_tint = (
            ctx.skin.ring_tint_inner
            if ctx.skin.ring_tint_inner is not None
            else ctx.skin.ring_tint
        )
        draw_pixmap_centered(
            painter, ctx, spec.inner_asset, QPointF(0, 0), 2 * ctx.radius,
            tint=inner_tint, saturation=ctx.skin.ring_saturation,
        )
        draw_pixmap_centered(
            painter, ctx, spec.outer_asset, QPointF(0, 0), 2 * ctx.radius,
            tint=ctx.skin.ring_tint, saturation=ctx.skin.ring_saturation,
        )

    def _draw_ring_glyph(
        self, painter: QPainter, ctx: RenderContext, gold_asset: Path,
        metal: str, theta: float, radius_fraction: float, height: float,
        tint: str | None = None, opacity: float = 1.0,
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
        black silhouette has no saturation to scale. `tint`/`opacity`
        are per-CALLER (Crown Text round, owner correction 2026-08-05):
        `_draw_letter_art` passes `letter_tint`/1.0 (unchanged behavior);
        `_draw_motto` resolves its OWN independent `motto_tint`/
        `motto_alpha` — the two controls no longer share one recolor."""
        shadow_radius = height * dial.RING_LETTER_SHADOW_RADIUS
        samples = dial.RING_LETTER_SHADOW_SAMPLES
        # Silver/bronze are derived from the gold master AT LOAD (owner
        # 2026-07-19), disk-cached like every other derived asset — the
        # shadow silhouette is metal-invariant (same alpha mask on every
        # finish), so it always reads the gold file directly.
        asset = letter_metal_file(gold_asset, metal)
        # THE INDICES/CROWN TEXT FREE COLOR (Watch Face Phase 4, R-24;
        # Crown Text correction 2026-08-05): an EXTRA tint layered OVER
        # the metal finish already resolved above (None, the default,
        # leaves it untouched — today's behavior on every release before
        # this one).
        pixmap = ctx.cache.pixmap_by_height(
            asset, height, ctx.dpr, saturation=ctx.skin.ring_saturation,
            tint=tint,
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
        painter.setOpacity(dial.RING_LETTER_SHADOW_ALPHA * opacity)
        for k in range(samples):
            angle = 2.0 * math.pi * k / samples
            painter.drawPixmap(
                QPointF(
                    -logical_w / 2 + shadow_radius * math.cos(angle),
                    -height / 2 + shadow_radius * math.sin(angle),
                ),
                shadow,
            )
        painter.setOpacity(opacity)
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
                tint=ctx.skin.letter_tint,
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
        without a motto.

        CROWN TEXT controls (owner correction 2026-08-05: "Crown tekst
        je onaj tekst koji piše oko sata — faith, hope, suffering", the
        proof this IS the motto arc): `motto_scale` multiplies the
        height ON TOP OF `ring_letter_scale` (which still applies too,
        unchanged); `motto_tint` resolves independently of
        `letter_tint` — None follows `ring_tint`, the SAME
        "follow-unless-overridden" shape `hands_tint` uses;
        `motto_alpha` is a plain opacity multiplier passed straight to
        `_draw_ring_glyph`."""
        mottos = self._skin.ring.motto
        if not mottos:
            return
        height = (
            2 * ctx.radius * dial.RING_MOTTO_SIZE
            * ctx.skin.ring_letter_scale * ctx.skin.motto_scale
        )
        metal = self._skin.ring.motto_metal
        tint = (
            ctx.skin.motto_tint
            if ctx.skin.motto_tint is not None
            else ctx.skin.ring_tint
        )
        for motto in mottos:
            for gold_asset, theta in motto["glyphs"]:
                self._draw_ring_glyph(
                    painter, ctx, gold_asset, metal, theta % 360.0,
                    dial.RING_MOTTO_RADIUS_FRACTION, height,
                    tint=tint, opacity=ctx.skin.motto_alpha,
                )
