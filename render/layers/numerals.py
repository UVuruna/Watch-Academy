"""The NUMERAL layer family — the band cache keys and the live crown.

THE FIDELITY RULING (owner correction 2026-08-06): the two BAND layers
that used to live here are gone. They stacked a computed plate on top of
`RingLayer`'s printed one, which is exactly the construction the ruling
outlaws — an Ω with a 0 showing under it. The bands are now part of the
ring's own composition ([Ring](ring.md)), which draws his inner base
art, the live inner numbers, the computed outer band, the jewels and
the crown arc in one ordered pass. `band_spec` stayed here, because it
is the shared door BOTH the ring layer and every test go through to ask
for the plate an on-screen watch would get.

`LiveCrownLayer` is the ONE minute-cadence element of this round, and it
is minute-cadence and nothing more — its glyphs were rasterized at
settings-apply time, so a tick costs a sequence lookup, an arc layout
and at most eleven `drawImage` calls.
"""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from config import dial, paths
from core import numerals
from render import letter_plates
from render.context import Cadence, Layer, RenderContext
from render.asset_recolor import jewel_metal_file
from render.numeral_bands import (
    BandSpec, CrownSpec, compose_crown, crown_glyph_ink, crown_glyph_set,
)
from render.painting import dial_point


def band_spec(skin, band: str, ctx: RenderContext) -> BandSpec:
    """The cache key for one band under this skin at this size/DPI —
    the ONE place a skin's numeral settings become a spec (Rule #5,
    shared by the ring layer and by every test that wants the same
    plate an on-screen watch would get).

    `offset_deg` is THE WORLD OFFSET (`core.world`) for the OUTER band
    — the solar offset plus the night inversion, 0.0 in the Geocentric
    mode. The INNER band NEVER rotates, in any mode (ledger §2), so it
    keys on 0.0 and its plate is shared across both phases.

    THE COMPOSITION LAW's own two keys ride here too: the OUTER band
    takes the preset's LETTER seats (so no numeral is drawn where a
    letter stands) and the INNER band takes the picked variant's name
    (so no number is drawn where one of his arrows stands). Both are
    part of the key, because two presets sharing every numeral setting
    still compose different bands."""
    pixels = max(2, round(2 * ctx.radius * ctx.dpr))
    size = (
        skin.numeral_outer_size if band == "outer" else skin.minutes_size
    )
    face = (
        skin.numeral_face if band == "outer" else skin.minutes_face
    )
    tint = (
        skin.ring_tint if band == "outer"
        else (
            skin.ring_tint_inner if skin.ring_tint_inner is not None
            else skin.ring_tint
        )
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
        offset_deg=ctx.world_offset if band == "outer" else 0.0,
        jewel_hours=(
            tuple(sorted(skin.ring.jewels)) if band == "outer" else ()
        ),
        inner_variant="" if band == "outer" else skin.ring.inner_asset.stem,
        tint=tint,
        saturation=skin.ring_saturation,
    )


def crown_spec(skin, ctx: RenderContext) -> CrownSpec:
    """The live crown's own cache key — its glyphs rebuild only
    when one of these changes.

    THE TIME CROWN LOOK (owner correction 2026-08-06, `research/
    ring_rework.md` §3): the crown's own finish is
    `skin.ring.crown_text_metal` — the SAME `settings.ring_finish` the
    ring's own jewels wear (`app.controller.build_skin`) — never the
    outer band's `numeral_relief`/`numeral_depth`/`numeral_light`/
    `numeral_darkness`/`numeral_border` knobs, which no longer reach the
    crown at all. `shade` is resolved here (not left to the glyph
    builder's own ambient read) so it rides the cache key: two watches
    with different active shades must never share one baked tile.

    ONE CROWN SIZE LAW (owner defect 2026-08-07 — the live crown read
    "microscopic" beside NON NOBIS DOMINE): `height_px` is the glyph
    BOX, solved from the SAME expression
    `render.layers.ring.RingLayer._draw_crown_text` uses for the static
    arc — `2 * radius * RING_CROWN_TEXT_SIZE * crown_text_scale` — in
    DEVICE pixels. It replaces `size_units`, which read the HOUR BAND's
    `numeral_outer_size` and put a second, smaller size family on the
    same ring. THE DECOUPLED SCALES (same round): `ring_jewels_scale`
    is deliberately absent — it sizes jewels and nothing else now.

    THE ONE PLATE LAW (owner decree 2026-08-07): `sources` resolves
    EVERY glyph the crown can say to its own plate in the owner's
    library, through the SAME `jewel_metal_file` door a ring jewel goes
    through — one style for every glyph on the dial. No `face` is passed
    any more, because the crown draws no font.

    ONE METAL PER CROWN (same round — the colon rendered GOLD while the
    digits rendered gray): the resolved files ride the KEY, so the
    crown's BAKED tiles cannot outlive the background recolor's gold
    fallback. See `CrownSpec` for the full root cause.
    """
    metal = skin.ring.crown_text_metal
    return CrownSpec(
        pixels=max(2, round(2 * ctx.radius * ctx.dpr)),
        dpr=ctx.dpr,
        height_px=(
            2 * ctx.radius * dial.RING_CROWN_TEXT_SIZE
            * skin.crown_text_scale * ctx.dpr
        ),
        metal=metal,
        shade=paths.metal_shade(metal),
        sources=tuple(
            (glyph, str(jewel_metal_file(letter_plates.plate_path(glyph), metal)))
            for glyph in numerals.crown_glyph_alphabet() if glyph != " "
        ),
    )


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
        spec = crown_spec(self._skin, ctx)
        glyphs = crown_glyph_set(spec)
        radius = ctx.radius * dial.CROWN_RADIUS_FRACTION
        # THE CROWN ADVANCE LAW (owner defect 2026-08-07): the arc is
        # laid out in DEVICE pixels — the ink widths and the tracking
        # both come from `spec.height_px`, which is already device — so
        # the radius is multiplied by `dpr` to match. The ratio is what
        # becomes an angle, so the answer is resolution-independent.
        for image, angle, rotation in compose_crown(
            glyphs, sequence, self._entry["orientation"],
            offset_deg=ctx.world_offset,
            ink=crown_glyph_ink(spec),
            radius_px=radius * ctx.dpr,
            tracking_px=spec.height_px * dial.CROWN_TRACKING_FRACTION,
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
