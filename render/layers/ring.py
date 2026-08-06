"""The RING layer — THE COMPOSITIONAL RING MODEL (owner decree
2026-08-05), sharpened into THE FIDELITY RULING (owner correction
2026-08-06, `research/ring_rework.md` §2).

A ring is the composition of five things drawn in ONE ordered pass:

1. the INNER base art — his own numberless plate, carrying the 360 day
   hairlines, the 60 minute strokes and the quarter/octa ARROWS;
2. the live INNER numbers, composed into the five-minute seats that
   base leaves empty;
3. the OUTER band, drawn whole by [Numeral Bands](../__about/numeral_bands.md)
   — the metal AND the hour numerals, with a numeral at every hour the
   preset does not seat a letter on;
4. the preset's own LETTER art, on the seats step 3 left bare;
5. the optional CROWN TEXT arc outside the band.

Nothing is stacked on top of content it can collide with, which is the
ruling's first law: the outer plate PNG is no longer blitted at all (an
Ω with a printed 0 under it was the defect that issued the ruling), and
the inner plate blitted here is the NUMBERLESS one its variant composes
from (`config.dial.RING_INNER_COMPOSITION`).
"""

import math
from pathlib import Path

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from config import dial, palette
from core import angles, numerals, world
from render.asset_recolor import jewel_metal_file
from render.context import Cadence, Layer, RenderContext
from render.layers.numerals import band_spec
from render.numeral_bands import (
    band_plate, normalized_shadow_alpha, shadow_sample_count,
)
from render.painting import dial_point, draw_pixmap_centered


class RingLayer(Layer):
    """The composed ring: his inner base art, the live inner numbers,
    the computed outer band, the preset's own jewels (with per-hour
    metal finish) and the optional crown-text arc."""

    cadence = Cadence.STATIC

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        self._draw_bands(painter, ctx)
        self._draw_jewels(painter, ctx)
        self._draw_crown_text(painter, ctx)

    def _draw_bands(self, painter: QPainter, ctx: RenderContext) -> None:
        """The two bands, inner first so the outer band's own edge sits
        on top — and the ORDER is the composition (THE FIDELITY
        RULING): base art, its numbers, then the whole outer band, and
        only then the jewels `paint` draws next, which need the metal
        under them and nothing over them.

        The INNER art blitted here is the variant's NUMBERLESS BASE, not
        the file the user picked: `seconds.png` IS `simple_point.png`
        with numbers set into it, so blitting the base and composing the
        numbers live reproduces his plate exactly while letting the font
        and size be picks. `ring_tint_inner` None follows `ring_tint`,
        the SAME "follow-unless-overridden" shape `hands_tint` uses —
        the outer band's tint semantics are the product's own
        long-standing ones (RING SATURATION, owner 2026-07-18, Session
        21-D, scales saturation AFTER the tint recolor), and the
        computed plates answer both through their own spec."""
        spec = self._skin.ring
        inner_tint = (
            ctx.skin.ring_tint_inner
            if ctx.skin.ring_tint_inner is not None
            else ctx.skin.ring_tint
        )
        base = numerals.inner_composition(spec.inner_asset.stem)["base"]
        draw_pixmap_centered(
            painter, ctx, dial.RING_INNER_ART_DIR / f"{base}.png",
            QPointF(0, 0), 2 * ctx.radius,
            tint=inner_tint, saturation=ctx.skin.ring_saturation,
        )
        self._blit_band(painter, ctx, "inner")
        self._blit_band(painter, ctx, "outer")

    def _blit_band(
        self, painter: QPainter, ctx: RenderContext, band: str,
    ) -> None:
        """One COMPUTED band plate, centred on the dial origin (Rule #5,
        the shared blit both bands go through). The plate is built at
        most once per settings change and cached process-wide, so this
        is a single `drawImage` on a STATIC layer the compositor bakes."""
        plate = band_plate(band_spec(self._skin, band, ctx))
        logical = plate.width() / plate.devicePixelRatio()
        painter.drawImage(QPointF(-logical / 2.0, -logical / 2.0), plate)

    def _draw_ring_glyph(
        self, painter: QPainter, ctx: RenderContext, gold_asset: Path,
        metal: str, theta: float, radius_fraction: float, height: float,
        tint: str | None = None, opacity: float = 1.0, draw_shadow: bool = True,
    ) -> None:
        """One letter-art glyph stamped on the ring circle — the shared
        stamp (Rule #5) behind BOTH the ring's own six banknote jewels
        (`_draw_jewels`) and the outer crown text arc (`_draw_crown_text`,
        TASK 1, owner "može radi" 2026-07-19): the metal finish (derived
        from the gold master, `render.asset_recolor.jewel_metal_file`), a
        tight dark halo (owner spec: a gradient border, lit from above)
        and a tangential ROTATION that flips 180° through the lower half
        so text never reads upside down (Ω stands upright at the
        bottom — `core.angles.readable_rotation_deg`). UNTINTED by the
        ring hue either way, but the RING SATURATION slider still grays
        it (owner 2026-07-18, Session 21-D: "the ring plate + its
        letters" is one target); the shadow copy skips it — a pure
        black silhouette has no saturation to scale. `tint`/`opacity`
        are per-CALLER (Crown Text round, owner correction 2026-08-05):
        `_draw_jewels` passes `jewels_tint`/1.0 (unchanged behavior);
        `_draw_crown_text` resolves its OWN independent `crown_text_tint`/
        `crown_text_alpha` — the two controls no longer share one recolor.
        `draw_shadow=False` (SHADOW/SHINE round, owner ruling
        2026-08-06) skips the halo stamp entirely — the Dollar's Eye
        with its Shine toggle on already carries its own baked light,
        so the cast shadow would fight the glory of rays instead of
        reading as one glyph. The shadow's own SAMPLE COUNT scales with
        the PIXEL radius (`_shadow_sample_count`, THE PIXELATION FIX,
        1440p owner bug 2026-08-06) — the fixed 8 stamps of every
        earlier release separated into a scalloped edge once the dial
        grew past its usual sizes; growing the count keeps every stamp
        under `RING_JEWEL_SHADOW_MAX_GAP_PX` device pixels from its
        neighbor, and `_normalized_shadow_alpha` renormalizes each
        stamp's opacity so the composited darkness matches today's
        look at the floor count — smoother, never darker."""
        shadow_radius = height * dial.RING_JEWEL_SHADOW_RADIUS
        # Silver/bronze are derived from the gold master AT LOAD (owner
        # 2026-07-19), disk-cached like every other derived asset — the
        # shadow silhouette is metal-invariant (same alpha mask on every
        # finish), so it always reads the gold file directly.
        asset = jewel_metal_file(gold_asset, metal)
        # THE INDICES/CROWN TEXT FREE COLOR (Watch Face Phase 4, R-24;
        # Crown Text correction 2026-08-05): an EXTRA tint layered OVER
        # the metal finish already resolved above (None, the default,
        # leaves it untouched — today's behavior on every release before
        # this one).
        pixmap = ctx.cache.pixmap_by_height(
            asset, height, ctx.dpr, saturation=ctx.skin.ring_saturation,
            tint=tint,
        )
        logical_w = pixmap.width() / ctx.dpr
        pos = dial_point(theta, ctx.radius * radius_fraction)
        rotation = angles.readable_rotation_deg(theta)
        painter.save()
        painter.translate(pos)
        painter.rotate(rotation)
        if draw_shadow:
            shadow = ctx.cache.pixmap_by_height(
                gold_asset, height, ctx.dpr, tint=palette.SHADOW_STAMP_TINT
            )
            pixel_radius = shadow_radius * ctx.dpr
            samples = shadow_sample_count(pixel_radius)
            stamp_alpha = normalized_shadow_alpha(samples)
            painter.setOpacity(stamp_alpha * opacity)
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

    def _draw_jewels(self, painter: QPainter, ctx: RenderContext) -> None:
        """The owner's jewel art at the preset's hour positions — gold
        masters, silver/bronze derived at load (the accent letter wears
        the opposite metal, owner spec). Stamped by `_draw_ring_glyph`
        (Rule #5, shared with the outer crown text arc)."""
        height = (
            2 * ctx.radius * dial.RING_JEWEL_ART_SCALE
            * ctx.skin.ring_jewels_scale
        )
        for hour, gold_asset in self._skin.ring.jewel_art.items():
            # THE WORLD OFFSET (core.world): the jewels are world
            # members — they ride the turning band with the numerals
            # beside them, and `_draw_ring_glyph` derives the readable
            # rotation from the SEATED angle, so a letter carried into
            # the lower half re-seats readably instead of hanging
            # upside down. 0.0 in Geocentric leaves every seat exactly
            # where it always was.
            theta = (
                angles.ring_position_angle(hour) + ctx.world_offset
            ) % 360.0
            metal = self._skin.ring.jewel_metal.get(hour, "gold")
            # The Eye's SHINE ENLARGE (owner UV inbox 2026-07-27):
            # build_skin stamps a per-hour height multiplier for the
            # shine masters so the triangle stays the no-light size and
            # only the rays extend beyond it (1.0 for plain jewels).
            # SHADOW/SHINE round (owner ruling 2026-08-06): the same
            # per-hour plumbing skips the cast shadow for that seat —
            # the baked shine already carries its own light.
            self._draw_ring_glyph(
                painter, ctx, gold_asset, metal, theta,
                dial.RING_JEWEL_RADIUS_FRACTION,
                height * self._skin.ring.jewel_zoom.get(hour, 1.0),
                tint=ctx.skin.jewels_tint,
                draw_shadow=not self._skin.ring.jewel_no_shadow.get(hour, False),
            )

    def _draw_crown_text(self, painter: QPainter, ctx: RenderContext) -> None:
        """The outer GREAT SEAL CROWN TEXT ARC (MOTO-FIX round, owner
        correction 2026-07-19, the dollar's Great Seal reference
        image): each character of the preset's `crown_text` texts —
        pre-solved to its own dial angle by `data.rings`/`core.crown_text`
        (ANNUIT COEPTIS's own A/S pin the TOP arc at 8h/16h, NOVUS ORDO
        SECLORUM's own N/O/M pin the BOTTOM arc at 4h/24h/20h — MASON
        outside, G inside) — drawn via the SAME stamp the ring's own
        six jewels use (`_draw_ring_glyph`, Rule #5), just smaller
        (`RING_CROWN_TEXT_SIZE`) and further out. The two arcs are angularly
        DISJOINT (top 300-360-60 deg, bottom 120-180-240 deg) so both
        share ONE radius (`RING_CROWN_TEXT_RADIUS_FRACTION`) — no more two
        concentric rings of text. Empty (no-op) for every preset
        without crown text.

        CROWN TEXT controls (owner correction 2026-08-05: "Crown tekst
        je onaj tekst koji piše oko sata — faith, hope, suffering", the
        proof this IS the crown text arc): `crown_text_scale` multiplies the
        height ON TOP OF `ring_jewels_scale` (which still applies too,
        unchanged); `crown_text_tint` resolves independently of
        `jewels_tint` — None follows `ring_tint`, the SAME
        "follow-unless-overridden" shape `hands_tint` uses;
        `crown_text_alpha` is a plain opacity multiplier passed straight to
        `_draw_ring_glyph`."""
        crown_texts = self._skin.ring.crown_text
        if not crown_texts:
            return
        height = (
            2 * ctx.radius * dial.RING_CROWN_TEXT_SIZE
            * ctx.skin.ring_jewels_scale * ctx.skin.crown_text_scale
        )
        metal = self._skin.ring.crown_text_metal
        tint = (
            ctx.skin.crown_text_tint
            if ctx.skin.crown_text_tint is not None
            else ctx.skin.ring_tint
        )
        for crown_entry in crown_texts:
            glyphs = crown_entry["glyphs"]
            # THE ARC READING LAW (core.world.arc_seats, ledger §1
            # "nothing is mirrored"): a bare `+ world_offset` keeps every
            # LETTER upright but reverses which way the WORD reads the
            # moment the arc crosses the horizon — observed on the real
            # dial 2026-08-06, where DOMY's ANGER came up "REGNA" in the
            # night phase. The reflection about the arc's own new centre
            # turns the run back around. 0.0 in Geocentric is the
            # identity, so nothing moves there.
            seats = world.arc_seats(
                [theta for _asset, theta in glyphs], ctx.world_offset
            )
            for (gold_asset, _theta), seat in zip(glyphs, seats):
                self._draw_ring_glyph(
                    painter, ctx, gold_asset, metal, seat,
                    dial.RING_CROWN_TEXT_RADIUS_FRACTION, height,
                    tint=tint, opacity=ctx.skin.crown_text_alpha,
                )
