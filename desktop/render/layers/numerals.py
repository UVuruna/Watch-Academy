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
from PySide6.QtGui import QImageReader, QPainter

from functools import lru_cache
from pathlib import Path

from config import dial, paths
from core import numerals
from render import asset_index, letter_plates
from render.context import Cadence, Layer, RenderContext
from render.asset_recolor import jewel_metal_file
from render.numeral_bands import (
    BandSpec, CrownSpec, compose_crown, crown_glyph_ink, crown_glyph_set,
    numeral_ink_halves,
)
from render.painting import dial_point


def jewel_offset(skin, world_offset: float) -> float:
    """How far the JEWELS and the CROWN have turned — THE ONE DOOR for
    WHAT THE ROTATION CARRIES (owner ballot verdict 2026-08-13, Rule
    #5).

    `all_turn` hands back the world offset unchanged, so the jewels and
    the crown ride the band exactly as in every release before this one.
    `numerals_turn` hands back 0.0: they hold their place on screen and
    only the numerals travel. Every site that places a jewel, a crown
    glyph or their hover zones asks HERE — the ring layer, the live
    crown, the Omega hit circle and the compositor's two crown hovers —
    so the drawn dial and the hit zones cannot disagree."""
    return 0.0 if skin.world_rotation_scope == "numerals_turn" else world_offset


@lru_cache(maxsize=256)
def plate_aspect(asset: Path) -> float:
    """One jewel plate's WIDTH over its HEIGHT — the number the square
    assumption used to stand in for (owner order 2026-08-13).

    Read from the startup asset index first, which knows every picture's
    size without opening it; only a file the index has never seen costs
    a header read, and one that will not decode falls back to 1.0 — the
    old assumption, still a usable wedge. Cached per path, because a
    plate's aspect cannot change while the program runs."""
    resolved = paths.art_file(asset)
    size = asset_index.image_size(resolved)
    if size is None:
        reader = QImageReader(str(resolved))
        raw = reader.size()
        size = (raw.width(), raw.height()) if raw.isValid() else None
    if not size or size[1] <= 0:
        return 1.0
    return size[0] / size[1]


def jewel_ink_halves(skin) -> dict:
    """`hour -> half the arc that seat's JEWEL really covers` — the
    jewel half of THE INK WEDGE.

    Every term is the one `render.layers.ring.RingLayer._draw_jewels`
    stamps with — the `RING_JEWEL_ART_SCALE * ring_jewels_scale` height,
    the `outer_centreline` radius — plus the PLATE'S OWN ASPECT, so an M
    claims the width of an M and an I the width of an I instead of both
    claiming a square.

    `jewel_zoom` is DELIBERATELY LEFT OUT, and the reason is the reason
    it exists: `RING_EYE_SHINE_ENLARGE` pads the Eye's shine master with
    the glory of rays and enlarges the stamp so the TRIANGLE still draws
    the size a plain letter would (`skins.manifest.RingSkin.jewel_zoom`).
    The zoom is therefore padding, not letter. A numeral standing in the
    rays is lit, not covered — erasing it would put back exactly the
    kind of hole this round was ordered to remove — so the wedge is the
    letter's own size and the light shines over whatever it reaches."""
    scale = skin.ring_jewels_scale
    ring_size = skin.numeral_outer_ring_size
    return {
        hour % dial.NUMERAL_HOUR_COUNT: numerals.jewel_arc_half_deg(
            ring_size, scale, aspect=plate_aspect(asset),
        )
        for hour, asset in skin.ring.jewel_art.items()
    }


def occluded_hours(skin, ctx: RenderContext) -> tuple:
    """The outer band's hours whose numeral a FIXED jewel covers right
    now — `()` in the `all_turn` scope, where the jewels ride their own
    seats and a collision is impossible by construction.

    BOTH halves of the wedge are MEASURED (owner order 2026-08-13, THE
    INK WEDGE, replacing the square-jewel-against-whole-seat rule that
    shipped the same morning): `jewel_ink_halves` reads each plate's own
    aspect and zoom, `render.numeral_bands.numeral_ink_halves` the ink
    the chosen face paints at the chosen size, and every term still
    comes from the same seating data the ring stamps with — so a
    jewel-size or numeral-size slider move re-solves the occlusion in
    the same breath it re-sizes the glyph.

    Why it had to change, in his own measurement: a whole seat wedge
    (7.5 deg) against a square jewel (4.56 deg) reached 12.06 deg of the
    15-deg seat pitch, so a jewel took TWO numerals unless it stood
    within 2.94 deg of a seat. His hexagram lost 0, 4, 9, 12, 16 and 20
    with room to spare for all six."""
    if skin.world_rotation_scope != "numerals_turn":
        return ()
    return numerals.occluded_numeral_hours(
        tuple(sorted(skin.ring.jewels)),
        ctx.world_offset,
        jewel_ink_halves(skin),
        numeral_ink_halves(
            max(2, round(2 * ctx.radius * ctx.dpr)),
            skin.numeral_face,
            float(skin.numeral_outer_size),
            skin.numeral_outer_ring_size,
            skin.numeral_seating,
            ctx.world_offset,
        ),
    )


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
            tuple(sorted(skin.ring.jewels))
            if band == "outer" and skin.world_rotation_scope == "all_turn"
            else ()
        ),
        occluded_hours=(
            occluded_hours(skin, ctx) if band == "outer" else ()
        ),
        inner_variant="" if band == "outer" else skin.ring.inner_asset.stem,
        tint=tint,
        saturation=skin.ring_saturation,
    )


@lru_cache(maxsize=None)
def _crown_sources(metal: str, shade: str, art_source: str) -> tuple:
    """The crown alphabet's resolved plate files, ONCE per
    (metal, shade, art source) — `crown_spec` runs on the MINUTE paint
    path and each `jewel_metal_file` resolution stats the disk
    (`raster_store.source_prefix`), so an uncached map cost two stats
    per live-crown frame and failed the steady-state repaint tooth the
    moment the owner's live ring became The One (2026-08-09; the same
    latent-per-profile class as the Sunday dual probe). The letters are
    bundled instrument art — process-lifetime caching is the ONE COPY
    RULE's own pattern. `shade`/`art_source` ride the key so a display
    change never serves a stale map.'"""
    return tuple(
        (glyph, str(jewel_metal_file(letter_plates.plate_path(glyph), metal)))
        for glyph in numerals.crown_glyph_alphabet() if glyph != " "
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
    finish = letter_plates.crown_finish(skin)
    metal = finish.metal
    return CrownSpec(
        pixels=max(2, round(2 * ctx.radius * ctx.dpr)),
        dpr=ctx.dpr,
        height_px=(
            2 * ctx.radius * dial.RING_CROWN_TEXT_SIZE
            * skin.crown_text_scale * ctx.dpr
        ),
        metal=metal,
        shade=paths.metal_shade(metal),
        tint=finish.tint,
        alpha=finish.alpha,
        saturation=finish.saturation,
        sources=_crown_sources(
            metal, paths.metal_shade(metal), paths.art_source(),
        ),
    )


class LiveCrownLayer(Layer):
    """The crown's live time (ring_rework §3).

    The One keeps its own civil time; Templar keeps the hour of
    Jerusalem. Which preset carries which is `dial.RING_LIVE_CROWN`'s
    business, and the tick already carries every crown zone's `HH:MM`
    (`core.clock_state.build_tick_state`), so this layer never touches
    a clock or a timezone itself — it reads a string and composes."""

    frame = "rim"

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
            # WHAT THE ROTATION CARRIES: the live crown is crown text,
            # so it holds its place in the `numerals_turn` scope.
            offset_deg=jewel_offset(self._skin, ctx.world_offset),
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
