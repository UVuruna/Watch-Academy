"""The three NUMERAL layers — the two live-rendered bands and the live
crown.

`RingLayer` still draws everything it always drew (the outer plate PNG,
the inner plate PNG, the preset's letter art and the static `crown_text`
stamps); these layers ADD the hand-drawn numerals on top of that
composition. Nothing was replaced.

The two band layers are STATIC, so the compositor bakes them into its
cached pixmap and they cost nothing per frame: each asks
[Numeral Bands](../__about/numeral_bands.md) for a plate keyed by the
skin's numeral settings and the plate's own pixel size, and blits it
centred on the dial origin. `LiveCrownLayer` is the ONE minute-cadence
element of this round, and it is minute-cadence and nothing more — its
glyphs were rasterized at settings-apply time, so a tick costs a
sequence lookup, an arc layout and at most eleven `drawImage` calls.
"""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from config import dial
from core import numerals
from render.context import Cadence, Layer, RenderContext
from render.numeral_bands import BandSpec, CrownSpec, band_plate, compose_crown, crown_glyph_set
from render.painting import dial_point


def band_spec(skin, band: str, ctx: RenderContext) -> BandSpec:
    """The cache key for one band under this skin at this size/DPI —
    the ONE place a skin's numeral settings become a spec (Rule #5,
    shared by both band layers and by every test that wants the same
    plate an on-screen watch would get).

    `offset_deg` is the OUTER band's Heliocentric rotation. It is 0.0
    today (wave 4 plugs in the solar offset and the night inversion),
    but it rides the key from the start so turning the band on rebuilds
    the plate without changing this function's shape."""
    pixels = max(2, round(2 * ctx.radius * ctx.dpr))
    size = (
        skin.numeral_outer_size if band == "outer" else skin.numeral_inner_size
    )
    face = (
        skin.numeral_face if band == "outer" else skin.numeral_inner_face
    )
    return BandSpec(
        band=band,
        pixels=pixels,
        dpr=ctx.dpr,
        face=face,
        size_units=float(size),
        ring_size=skin.numeral_outer_ring_size,
        seating=skin.numeral_seating,
        relief_style=skin.numeral_relief,
        depth_units=skin.numeral_depth,
        light=skin.numeral_light,
        darkness=skin.numeral_darkness,
        contact_blur_units=skin.numeral_contact_blur,
        border_units=skin.numeral_border,
        offset_deg=0.0,
    )


def crown_spec(skin, ctx: RenderContext) -> CrownSpec:
    """The live crown's own cache key — the eleven glyphs rebuild only
    when one of these changes."""
    return CrownSpec(
        pixels=max(2, round(2 * ctx.radius * ctx.dpr)),
        dpr=ctx.dpr,
        face=skin.crown_face,
        size_units=float(skin.numeral_outer_size),
        relief_style=skin.numeral_relief,
        depth_units=skin.numeral_depth,
        light=skin.numeral_light,
        darkness=skin.numeral_darkness,
        border_units=skin.numeral_border,
    )


class _BandLayer(Layer):
    """The shared blit (Rule #5): both bands differ only in which spec
    they ask for."""

    cadence = Cadence.STATIC
    band = "outer"

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        plate = band_plate(band_spec(self._skin, self.band, ctx))
        logical = plate.width() / plate.devicePixelRatio()
        painter.drawImage(QPointF(-logical / 2.0, -logical / 2.0), plate)


class OuterNumeralLayer(_BandLayer):
    """The 24 hour numerals, in relief, at whatever angle the moment
    demands."""

    band = "outer"


class InnerNumeralLayer(_BandLayer):
    """The minute numerals plus the LONG/SHORT/POINTER/SECOND/DAY tick
    lines, in white glow. Never rotates, in any mode."""

    band = "inner"


class LiveCrownLayer(Layer):
    """The crown's live time (ring_rework §3).

    The One keeps its own civil time; Templar keeps the hour of
    Jerusalem. Which preset carries which is `dial.RING_LIVE_CROWN`'s
    business, and the tick already carries every crown zone's `HH:MM`
    (`core.clock_state.build_tick_state`), so this layer never touches
    a clock or a timezone itself — it reads a string and composes."""

    cadence = Cadence.MINUTE

    def __init__(self, skin, ring_name: str, lift: bool = False):
        super().__init__(skin, lift)
        self._entry = dial.RING_LIVE_CROWN[ring_name]

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        if ctx.tick is None:
            return                     # STATIC/DAILY compositing pass
        zone_key = self._entry["zone"] or "local"
        stamp = ctx.tick.crown_zone_hm.get(zone_key)
        if stamp is None:
            return                     # a tick built before this zone existed
        hour, minute = (int(part) for part in stamp.split(":"))
        sequence = numerals.crown_sequence(
            hour, minute, self._skin.crown_time_format
        )
        glyphs = crown_glyph_set(crown_spec(self._skin, ctx))
        radius = ctx.radius * dial.CROWN_RADIUS_FRACTION
        for image, angle, rotation in compose_crown(
            glyphs, sequence, self._entry["orientation"],
        ):
            logical_w = image.width() / image.devicePixelRatio()
            logical_h = image.height() / image.devicePixelRatio()
            painter.save()
            painter.translate(dial_point(angle, radius))
            painter.rotate(rotation)
            painter.drawImage(
                QPointF(-logical_w / 2.0, -logical_h / 2.0), image
            )
            painter.restore()
