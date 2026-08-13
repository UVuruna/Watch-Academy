"""The two band plates and the crown's glyph set — built ONCE per
settings change, cached process-wide, blitted every frame.

THE FIDELITY RULING (owner correction 2026-08-06, ring_rework.md §2) is
what this module now implements, in its own three laws:

1. **The band COMPOSES; it never stacks.** The outer plate is the metal
   AND the numerals, drawn together, with a numeral at every hour the
   preset does not seat a LETTER on — so the old printed plate is gone
   from under it and an Ω never again stands over a 0. The inner plate
   is the numbers alone, composed into the empty five-minute seats of
   the owner's own numberless base art.
2. **His art is the look.** Every tick, every arrow and every day
   hairline on the inner band IS his plate, blitted (`RingLayer`); what
   this module draws — the numerals, the metal, the stubs — was fitted
   glyph by glyph against `assets/instrument/ring/outter/full.png` and
   `inner/seconds.png` rather than styled.
3. **Render time changes WHAT, never HOW.** The user's picks decide the
   content of a seat; `config.dial`'s measured constants decide the
   style.

THE ONE COPY RULE (owner 2026-07-28, extended 2026-08-06): `_PLATES` and
`_CROWNS` are module-level, so N watches showing the same settings hold
ONE copy of each plate — exactly like `render.assets.shared_cache` and
every other shared book. The SPEC dataclasses below are the cache keys:
they carry precisely what can make two plates differ, `offset_deg` and
the preset's own jewel seats included.

Nothing here runs on the paint path and nothing here touches the disk:
the plates are COMPUTED. The layers only ever blit what they find.
"""

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QTransform

from config import dial, palette
from config.dial import (   # noqa: F401 — the law's public home; re-exported
    band_ride_shift, interior_scale, outer_band_edges, outer_centreline,
)
from core import numerals
from render import numeral_relief as relief
from render.asset_recolor import ring_recolored_image
from render.numeral_fonts import assert_covers, numeral_font
from render.painting import dial_point


# ------------------------------------------------------- THE LETTER SHADOW LAW
# The stamped-shadow math every RING GLYPH wears has MOVED AGAIN, to
# `render.glyph_shadow` (0.14.960, the owner's dense-shadow order of
# 2026-08-12). It came here from `render.layers.ring` on 2026-08-06 so
# the crown's baked tiles could share the jewels' halo; it leaves for the
# same reason and a THIRD caller — the on-dial NAME LABELS, drawn by
# `render.painting`, which THIS module imports (`dial_point`), so this
# module could never be their shared home without a cycle.
#
# Re-exported here deliberately: `render.layers.ring` imports these two
# names from `render.numeral_bands` and there is no reason to churn its
# import line. Same names, same numbers, one definition.
from render.glyph_shadow import (   # noqa: F401 — re-export, see above
    image_silhouette as _image_silhouette,
    normalized_shadow_alpha,
    shadow_sample_count,
    stamp_shadow as _stamp_shadow,
)


@dataclass(frozen=True)
class BandSpec:
    """Everything that can make two band plates differ. Frozen and
    hashable — it IS the cache key."""

    band: str                  # "outer" | "inner"
    pixels: int                # the plate's DEVICE pixel diameter
    dpr: float
    face: str
    size_units: float
    ring_size: float = 1.0     # the outer band's width multiplier
    seating: str = dial.NUMERAL_SEATING_DEFAULT
    relief_style: str = dial.NUMERAL_RELIEF_DEFAULT
    depth_units: float = dial.NUMERAL_DEPTH_DEFAULT
    light: str = dial.NUMERAL_LIGHT_DEFAULT
    fixed_offset: tuple = (0.0, 0.0)
    darkness: float = dial.NUMERAL_DARKNESS_DEFAULT
    contact_blur_units: float = dial.NUMERAL_CONTACT_BLUR_DEFAULT
    border_units: float = dial.NUMERAL_BORDER_DEFAULT
    offset_deg: float = 0.0    # the Heliocentric band rotation
    # THE COMPOSITION LAW's own two keys. `jewel_hours` are the OUTER
    # seats the preset's jewel art holds (ring counting, midnight =
    # 24) — no numeral is drawn on them. `inner_variant` names the
    # INNER plate the user picked, which decides which five-minute
    # seats carry a number and which carry one of his arrows.
    jewel_hours: tuple = ()
    # THE ANGULAR WEDGE's own key (owner ballot verdict 2026-08-13).
    # In the `numerals_turn` scope the jewels do NOT ride the band, so
    # `jewel_hours` is empty — the jewels no longer own a SEAT, they own
    # a place on the SCREEN — and this instead carries the hours whose
    # numerals a fixed jewel currently covers
    # (`core.numerals.occluded_numeral_hours`). It is a second key and
    # not a reuse of the field above because the two say different
    # things: one is "this seat belongs to a letter", the other is
    # "this numeral happens to be underneath one right now", and only
    # the second changes as the world turns.
    occluded_hours: tuple = ()
    inner_variant: str = ""
    # The ring's own two recolors, so a COMPUTED plate answers the
    # sliders exactly as the printed plate it replaces did.
    tint: str | None = None
    saturation: float = 1.0


@dataclass(frozen=True)
class CrownSpec:
    """The live crown's own key — its glyphs are rasterized once per
    change of it.

    THE TIME CROWN LOOK (owner correction 2026-08-06, `research/
    ring_rework.md` §3): the crown no longer carries the outer band's
    own relief/depth/light/darkness/border knobs — those styled the
    parity plate-and-frame look the owner ruled OFF the time crown
    entirely. What replaces them is the SAME two things every ring
    letter answers to: `metal` (the crown's own finish,
    `RingSpec.crown_text_metal` — gold/silver/bronze/thematic) and its
    active `shade`, both resolved once by `render.layers.numerals.
    crown_spec` and carried here so two watches with different shades
    never collide in the shared `_CROWNS` cache.

    ONE CROWN SIZE LAW (owner defect 2026-08-07): `height_px` is the
    glyph BOX in DEVICE pixels, handed in already solved by
    `render.layers.numerals.crown_spec` from the SAME
    `RING_CROWN_TEXT_SIZE * crown_text_scale` law the static arc beside
    it uses. It replaces the old `size_units`, which read the HOUR
    BAND's own numeral size and made the live crown a second, smaller
    size family on the same ring.

    THE ONE PLATE LAW (owner decree 2026-08-07): `sources` is the whole
    crown — one `(glyph, resolved plate file)` pair per glyph the crown
    can say, resolved by `render.layers.numerals.crown_spec` through
    the SAME `jewel_metal_file` door a ring jewel goes through. There is
    no `face` any more: the crown asks no font for anything.

    ONE METAL PER CROWN (same round — the colon rendered GOLD while the
    digits rendered gray): the resolved paths are IN the key, not
    looked up at build time. The metal variant is derived on a
    background thread (`render.art_warm`), so before the drain lands
    `jewel_metal_file` honestly falls back to the GOLD master — and the
    crown BAKES its tiles once and caches them, which would freeze that
    fallback in place forever. With the paths in the KEY, the drain's
    arrival is a new key and the crown rebuilds in the metal the rest of
    the ring is already wearing."""

    pixels: int
    dpr: float
    height_px: float
    metal: str = "gold"
    shade: str = ""
    tint: str | None = None
    alpha: float = 1.0
    saturation: float = 1.0
    sources: tuple[tuple[str, str], ...] = ()


_PLATES: dict[BandSpec, QImage] = {}
_CROWNS: dict[CrownSpec, dict] = {}


def clear_cache() -> None:
    """Drop every built plate (a screen/DPI change, or a test that wants
    a cold build). The specs carry the pixel size, so this is never
    needed for correctness — only to give memory back."""
    _PLATES.clear()
    _CROWNS.clear()


def _unit_px(spec_pixels: int) -> float:
    """One numeral "unit" in DEVICE pixels for a plate of this size —
    the ledger's own resolution-independent length (§8)."""
    return spec_pixels * dial.NUMERAL_UNIT_FRACTION


def band_plate(spec: BandSpec) -> QImage:
    """The band's finished plate, built at most once per spec.

    THE ONE COPY RULE's own ceiling rides here (`NUMERAL_PLATE_CACHE_MAX`):
    the key carries `offset_deg`, and in the Heliocentric mode that
    offset moves with the solar noon — once a day, twice with the night
    phase. Unbounded, a watch left running for a year would hold a year
    of plates; bounded, it holds the working set and drops the OLDEST
    inserted beyond it (Python dicts keep insertion order, so this is
    the whole eviction)."""
    plate = _PLATES.get(spec)
    if plate is None:
        plate = (
            _build_outer(spec) if spec.band == "outer" else _build_inner(spec)
        )
        _PLATES[spec] = plate
        while len(_PLATES) > dial.NUMERAL_PLATE_CACHE_MAX:
            del _PLATES[next(iter(_PLATES))]
    return plate


def outer_band_plate(spec: BandSpec) -> QImage:
    return band_plate(spec)


def inner_band_plate(spec: BandSpec) -> QImage:
    return band_plate(spec)


def inner_number_seat_angles(spec: BandSpec) -> tuple[float, ...]:
    """The dial angle of every composed minute NUMBER on the inner band
    — the seats whose big stroke the clear region masks away, and where
    `render.layers.ring` therefore stands the small white-bordered SEAT
    TICK (owner correction 2026-08-11, slika 1)."""
    return tuple(angle for _label, angle, _center in _seats(spec))


def inner_number_clear_regions(spec: BandSpec) -> QPainterPath:
    """THE NUMBER'S OWN RECTANGLE (owner correction 2026-08-11, the
    '15' screenshot: the plate's big five-minute stroke showed BETWEEN
    the digits — "nothing renders inside the imagined rectangle of the
    numeral"). One padded, seat-rotated rectangle per minute numeral,
    in LOGICAL dial-centred coordinates — `render.layers.ring.RingLayer`
    clips the base-plate blit with the complement, so the owner's art
    is masked there instead of drawn over. Empty for a variant whose
    seats all carry arrows.

    TWO BOUNDS on the cut (owner same-day corrections, slika 1 and 8):

    1. **The 360 hairlines are the cutting limit** ("oni ne smeju biti
       iseceni"): the whole region is capped INSIDE the hairline tips'
       circle (`dial.RING_INNER_TICK_INNER_FRACTION`), so a padded or
       rotated rectangle can never reach into the little points.
    2. **No shortened big stroke** ("ovaj skraceni tick treba da ne
       prikazuje... ali da prikazuje ova 2 360 ticka levo i desno"):
       the cap alone would leave the seat's own big stroke as a cut
       stub floating above the numeral, so a NARROW radial wedge at
       the seat's exact angle removes that stroke WHOLE — from below
       the content line to past the tick roots — while its two
       neighbouring hairlines (a full degree away, outside the
       wedge's ±0.7 deg) stay visible."""
    shrink = interior_scale(spec.ring_size)
    unit = _unit_px(spec.pixels) * shrink
    font = numeral_font("inner", spec.face, spec.size_units * unit)
    pad = unit * dial.NUMERAL_GLOW_BORDER_UNITS * 2.0
    scale = 1.0 / spec.dpr
    half_px = spec.pixels / 2.0
    region = QPainterPath()
    # WINDING fill: the seat wedge OVERLAPS the numeral's rectangle,
    # and the default odd-even rule would cancel the overlap into a
    # hole — the stroke's middle would render through the mask.
    region.setFillRule(Qt.FillRule.WindingFill)
    for label, angle, center in _seats(spec):
        local = relief.glyph_path(label, font).boundingRect()
        local = local.adjusted(-pad, -pad, pad, pad)
        # `_seats` centres are DIAL-CENTRED device px (the plate
        # painter's own origin) — only the DPR separates them from the
        # layer's logical space.
        transform = QTransform()
        transform.scale(scale, scale)
        transform.translate(center.x(), center.y())
        transform.rotate(numerals.seat_rotation(angle, spec.seating))
        rect_path = QPainterPath()
        rect_path.addRect(local)
        region.addPath(transform.map(rect_path))
    if region.isEmpty():
        return region
    # Bound 1: cap the whole region inside the hairline tips' circle.
    limit = half_px * shrink * dial.RING_INNER_TICK_INNER_FRACTION * 0.995
    disc = QPainterPath()
    disc.addEllipse(QPointF(0.0, 0.0), limit, limit)
    to_logical = QTransform()
    to_logical.scale(scale, scale)
    region = region.intersected(to_logical.map(disc))
    # Bound 2: the seat's own big stroke goes WHOLE — one narrow wedge
    # per number seat, sparing the hairlines one degree to either side.
    r0 = half_px * shrink * dial.RING_INNER_CONTENT_INNER_FRACTION * 0.99
    r1 = half_px * shrink * dial.RING_INNER_TICK_OUTER_FRACTION * 1.02
    for _label, angle, _center in _seats(spec):
        wedge = QPainterPath()
        wedge.moveTo(dial_point(angle - 0.7, r0))
        wedge.lineTo(dial_point(angle - 0.7, r1))
        wedge.lineTo(dial_point(angle + 0.7, r1))
        wedge.lineTo(dial_point(angle + 0.7, r0))
        wedge.closeSubpath()
        # `united`, never `addPath`: the wedge overlaps the numeral's
        # rectangle, and BOTH fill rules can cancel an overlap of
        # subpaths (odd-even always, winding when the windings oppose) —
        # the union is overlap-proof by construction.
        region = region.united(to_logical.map(wedge))
    return region


def _clamped_to_dial(
    path: QPainterPath, center: QPointF, radius: float,
    reserve: float = 0.0,
) -> QPainterPath:
    """THE DIAL-CIRCLE CLAMP (extremes round, 2026-08-09): a numeral
    whose SEATED path would leave the dial circle is scaled down about
    its own seat until it fits — the plate canvas IS the dial square,
    so anything past 1.0R gets CUT (the owner's octagon defect class),
    and glyph metrics vary by FONT ENVIRONMENT (the offscreen QPA's
    substitute faces run wider than the roster faces and clipped at
    max numeral size where the real fonts did not). Render time
    changes WHAT, never HOW — a too-big glyph is drawn smaller, never
    sliced. Identity for every glyph that already fits."""
    box = path.boundingRect()
    reach = max(
        math.hypot(x, y)
        for x in (box.left(), box.right())
        for y in (box.top(), box.bottom())
    )
    limit = radius * 0.999 - reserve
    if reach <= limit or reach <= 0.0:
        return path
    factor = limit / reach
    transform = QTransform()
    transform.translate(center.x(), center.y())
    transform.scale(factor, factor)
    transform.translate(-center.x(), -center.y())
    return transform.map(path)


def _annulus(radius: float, inner: float, outer: float) -> QPainterPath:
    """The ring between two radius fractions, as an even-odd path."""
    path = QPainterPath()
    path.setFillRule(Qt.FillRule.OddEvenFill)
    for fraction in (outer, inner):
        span = radius * fraction
        path.addEllipse(QRectF(-span, -span, 2 * span, 2 * span))
    return path


def _seats(spec: BandSpec) -> tuple[tuple[str, float, QPointF], ...]:
    """`(label, seat angle, page-space centre)` for every numeral of the
    band — THE COMPOSITION LAW's own list, so a seat that carries other
    content simply is not in it.

    The OUTER band's angles carry `offset_deg` and skip the preset's
    LETTER seats (`core.numerals.numeral_hours`) PLUS whatever a fixed
    jewel currently covers (`occluded_hours`, THE ANGULAR WEDGE — empty
    in the `all_turn` scope, where the jewels ride their own seats and
    nothing can ever be covered); the INNER band NEVER rotates in any
    mode (ledger §2) and carries only the five-minute seats its variant
    leaves empty of arrows."""
    radius = spec.pixels / 2.0
    if spec.band == "outer":
        fraction = outer_centreline(spec.ring_size)
        pairs = [
            (str(hour), numerals.hour_angle(hour, spec.offset_deg))
            for hour in numerals.numeral_hours(
                tuple(spec.jewel_hours) + tuple(spec.occluded_hours)
            )
        ]
    else:
        # THE INWARD-GROWTH LAW: the minute seats live in the interior
        # world and yield with it when the hour band grows inward.
        fraction = dial.MINUTES_RADIUS_FRACTION * interior_scale(spec.ring_size)
        pairs = list(numerals.inner_number_seats(spec.inner_variant))
    return tuple(
        (label, angle, dial_point(angle, radius * fraction))
        for label, angle in pairs
    )


def _build_outer(spec: BandSpec) -> QImage:
    """The whole OUTER band: the metal, then the hour numerals standing
    on it — THE FIDELITY RULING's first law. No printed plate is blitted
    under this any more, so nothing the engine draws can collide with
    something already baked into a PNG.

    Four passes, in this order: the BASE (a flat `NUMERAL_RING_GROUND`
    annulus with the black rim on its outer edge — measured, not
    designed), the HALO (every glyph dilated by
    `NUMERAL_SHADOW_REACH_UNITS`, thrown by the light, blurred ONCE as
    one band-wide layer and composited `NUMERAL_GLOW_PASSES` times), the
    RELIEF copies, then the bodies in their parity colours. Doing the
    blur band-wide is what keeps the edge smooth at 1440p; every radius
    comes from the plate's own pixel size, so it scales by
    construction."""
    assert_covers("outer", spec.face, numerals.hour_labels())
    unit = _unit_px(spec.pixels)
    radius = spec.pixels / 2.0
    font = numeral_font("outer", spec.face, spec.size_units * unit)
    depth_px = spec.depth_units * unit
    border_px = spec.border_units * unit
    paths = tuple(
        (
            label,
            angle,
            _clamped_to_dial(
                relief.seated_path(
                    label, font, center,
                    numerals.seat_rotation(angle, spec.seating),
                ),
                center, radius,
                # The relief copies, the halo dilation+blur and the
                # border all paint BEYOND the base path — reserve the
                # pipeline's OWN maxima (the halo formula below, its
                # box blur doubled for the composite's alpha spread,
                # the full relief throw, the body pen), or the clamp
                # bounds a path whose ink still leaves the circle.
                reserve=(
                    (border_px / 2.0 + dial.NUMERAL_SHADOW_REACH_UNITS * unit)
                    + 2.0 * spec.contact_blur_units * unit
                    + depth_px + border_px
                ),
            ),
        )
        for label, angle, center in _seats(spec)
    )
    plate = relief.blank_plate(spec.pixels)
    painter = relief.plate_painter(plate)
    inner_edge, outer_edge = outer_band_edges(spec.ring_size)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette.NUMERAL_RING_GROUND))
    painter.drawPath(_annulus(radius, inner_edge, outer_edge))
    painter.setBrush(QColor(palette.NUMERAL_BAND_RIM))
    painter.drawPath(
        _annulus(
            radius, outer_edge - dial.NUMERAL_BAND_RIM_FRACTION, outer_edge,
        )
    )
    painter.end()
    throws = {
        label: numerals.light_offset(
            angle, depth_px, spec.light,
            tuple(value * unit for value in spec.fixed_offset),
        )
        for label, angle, _path in paths
    }
    halo_px = border_px / 2.0 + dial.NUMERAL_SHADOW_REACH_UNITS * unit
    if halo_px > 0.0 and paths:
        # The halo takes NO throw — MEASURED on his plates, where the
        # black reaches 11.1 px outward and 11.3 px inward of a numeral:
        # symmetric to within a fifth of a pixel at 3600. The LIGHT is
        # the ledger's own directional relief (`draw_relief` below),
        # which at the settled depth lies inside this halo and only
        # emerges when the user asks for a deeper one.
        silhouette = relief.blank_plate(spec.pixels)
        painter = relief.plate_painter(silhouette)
        for _label, _angle, path in paths:
            relief.draw_dilated(
                painter, path, halo_px, palette.NUMERAL_SHADE_COLOR,
            )
        painter.end()
        blur_px = spec.contact_blur_units * unit
        relief.composite(
            plate, relief.box_blur_alpha(silhouette, blur_px), spec.darkness,
            dial.NUMERAL_GLOW_PASSES,
        )
    painter = relief.plate_painter(plate)
    for label, _angle, path in paths:
        relief.draw_relief(
            painter, path, spec.relief_style, depth_px, throws[label],
            spec.darkness,
        )
    for label, _angle, path in paths:
        relief.draw_body(painter, path, numerals.parity_role(label), border_px)
    painter.end()
    return relief.stamp_dpr(
        ring_recolored_image(plate, spec.tint, spec.saturation), spec.dpr,
    )


def _build_inner(spec: BandSpec) -> QImage:
    """The INNER band's live half: the minute NUMBERS, in the WHITE
    BORDER + GLOW every element of the owner's inner plates wears
    (ring_rework §2: small radius, strong intensity, a border+glow,
    never a diffuse halo). The glow is one band-wide blurred silhouette
    composited `NUMERAL_GLOW_PASSES` times: several small passes read as
    a tight bright edge where one wide pass reads as smoke.

    The band's ticks and arrows are NOT here — `RingLayer` blits them
    from his numberless base plate first, and these numbers compose into
    it. They also OCCLUDE, exactly as they do in his own numbered
    plates: a five-minute stroke runs 0.798 to 0.888 of the radius and a
    number stands over its inner half, leaving the outer stub showing.
    Reproducing that needs no extra geometry at all — the number is
    opaque and simply covers what it covers. A variant whose seats all
    carry arrows (`simple`, `simple_octa`) builds an EMPTY plate, which
    is correct: the whole band is then his art, untouched."""
    assert_covers("inner", spec.face, numerals.minute_labels())
    # THE INWARD-GROWTH LAW's second pass (opus verification finding
    # F2, 2026-08-09): the minute glyphs shrink WITH their track — the
    # seat alone used to scale, so a full-size digit overhung its
    # shrunken five-minute stroke and slid under the widened band.
    shrink = interior_scale(spec.ring_size)
    unit = _unit_px(spec.pixels) * shrink
    font = numeral_font("inner", spec.face, spec.size_units * unit)
    border_px = dial.NUMERAL_GLOW_BORDER_UNITS * unit
    seats = _seats(spec)
    elements = [
        relief.seated_path(
            label, font, center,
            # THE FLOWING SIDES (owner amendment 2026-08-11) are the
            # seating law itself now — both bands, no per-band flag.
            numerals.seat_rotation(angle, spec.seating),
        )
        for label, angle, center in seats
    ]
    plate = relief.blank_plate(spec.pixels)
    if elements:
        silhouette = relief.blank_plate(spec.pixels)
        painter = relief.plate_painter(silhouette)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(palette.MINUTES_INK))
        for path in elements:
            painter.drawPath(path)
        painter.end()
        relief.composite(
            plate,
            relief.box_blur_alpha(
                silhouette, dial.NUMERAL_GLOW_RADIUS_UNITS * unit
            ),
            1.0, dial.NUMERAL_GLOW_PASSES,
        )
        painter = relief.plate_painter(plate)
        for path in elements:
            relief.draw_inner_ink(painter, path, border_px)
        painter.end()
    return relief.stamp_dpr(
        ring_recolored_image(plate, spec.tint, spec.saturation), spec.dpr,
    )


def crown_glyph_ink(spec: CrownSpec) -> dict:
    """`glyph -> its own ink WIDTH in device pixels` — what THE CROWN
    ADVANCE LAW (`core.numerals.crown_advance_angles`) lays the arc out
    by. Built and cached alongside the tiles themselves, because the
    tile carries shadow padding on every side and its image width is
    therefore NOT the glyph's width."""
    _build_crown(spec)
    return _CROWNS[spec]["ink"]


def crown_glyph_set(spec: CrownSpec) -> dict:
    """The crown's glyphs, rasterized ONCE per settings change into
    tightly-cropped little images, keyed by glyph.

    THE ONE PLATE LAW (owner decree 2026-08-07): EVERY glyph comes from
    HIS plate library, through the exact pipeline every ring jewel goes
    through (`_crown_plate_image`) — one style for every glyph on the
    dial, gold master in, chosen metal out. The colon is
    `symbols/colon.png`, built "precisely for this"; the ten digits are
    `numerals/0-9.png`, shipped the day the owner saw them drawn by a
    font instead. The `"12h 35min"` format's h/min small cut takes the
    UPPERCASE plate at `dial.CROWN_SMALL_CUT_FRACTION` of the box — the
    library is caseless, and a plate is a shape.

    ONE CROWN SIZE LAW (owner defect 2026-08-07): the box every glyph is
    built into is `spec.height_px` — the static crown arc's own
    `RING_CROWN_TEXT_SIZE` box, so a digit and an N of NON NOBIS DOMINE
    are one size family. Every plate is scaled to that box exactly as
    `RingLayer._draw_ring_glyph` scales a letter plate to it, because
    they are now the same kind of thing."""
    _build_crown(spec)
    return _CROWNS[spec]["images"]


def _build_crown(spec: CrownSpec) -> None:
    """Rasterize (once) the crown's tiles and record each glyph's own
    ink width — the shared build behind `crown_glyph_set` and
    `crown_glyph_ink` (Rule #5: one build, two views of it).

    THE ONE PLATE LAW (owner decree 2026-08-07): EVERY glyph is a plate
    from the letter library, resolved to its metal finish by
    `render.layers.numerals.crown_spec` and carried in `spec.sources`.
    No font is consulted — there is no `assert_covers` call here any
    more, because the crown asks no face for an outline."""
    if spec in _CROWNS:
        return
    alphabet = numerals.crown_glyph_alphabet()
    sources = dict(spec.sources)
    full_px = spec.height_px
    small_px = full_px * dial.CROWN_SMALL_CUT_FRACTION
    images, ink = {}, {}
    for glyph, small in zip(alphabet, numerals.crown_small_cut(alphabet)):
        if glyph == " ":
            continue
        box_px = small_px if small else full_px
        images[glyph], ink[glyph] = _crown_plate_image(
            spec, box_px, sources[glyph],
        )
    _CROWNS[spec] = {"images": images, "ink": ink}


def _crown_plate_image(
    spec: CrownSpec, box_px: float, resolved: str,
) -> tuple[QImage, float]:
    """ONE crown glyph, from HIS plate — resolved through the exact same
    door every ring jewel resolves its finish through
    (`render.asset_recolor.jewel_metal_file`), scaled to the crown's own
    glyph BOX and finished with THE LETTER SHADOW LAW's stamped halo.
    Returns the tile and the plate's own ink width for THE CROWN ADVANCE
    LAW.

    THE ONE PLATE LAW (owner decree 2026-08-07): this is the WHOLE crown
    now, not just the colon. The digits used to be font outlines filled
    with a flat ramp tone, which is why the live time never wore the
    metal the letters beside it wore. Since the owner shipped
    `numerals/0-9.png` there is a plate for every glyph the crown can
    say, and a face is never asked for an outline again.

    ONE METAL PER CROWN (same decree, earlier defect): the path comes
    from `spec.sources`, which `render.layers.numerals.crown_spec`
    resolved and put in the CACHE KEY. Resolving it here instead would
    rebake the background recolor's gold fallback into a cache entry
    that outlives the drain — exactly the defect that made the colon
    gold while the digits went gray on Templar."""
    source = QImage(str(resolved))
    if source.isNull():
        raise ValueError(f"crown plate unreadable: {resolved}")
    scaled = source.scaledToHeight(
        max(1, round(box_px)), Qt.TransformationMode.SmoothTransformation,
    )
    # THE ONE KITCHEN (owner defect 2026-08-07): the tint and the ring
    # saturation are applied HERE, through the same `ring_recolored_image`
    # the live arc reaches via `AssetCache.pixmap_by_height` — tritone
    # first, saturation after. Baking the tile is a CADENCE decision (a
    # minute layer cannot recolor per frame); it was never licence to
    # wear a different finish, which is exactly what it did.
    scaled = ring_recolored_image(scaled, spec.tint, spec.saturation)
    shadow_radius_px = box_px * dial.RING_JEWEL_SHADOW_RADIUS
    pad = shadow_radius_px + 2.0
    tile = relief.blank_plate(
        max(2, int(math.ceil(scaled.width() + 2 * pad))),
        max(2, int(math.ceil(scaled.height() + 2 * pad))),
    )
    painter = relief.plate_painter(tile)
    silhouette = _image_silhouette(scaled, palette.SHADOW_STAMP_TINT)
    half_w, half_h = scaled.width() / 2.0, scaled.height() / 2.0
    _stamp_shadow(
        painter, shadow_radius_px,
        lambda dx, dy: painter.drawImage(
            QPointF(-half_w + dx, -half_h + dy), silhouette,
        ),
    )
    painter.drawImage(QPointF(-half_w, -half_h), scaled)
    painter.end()
    if spec.alpha != 1.0:
        # The arc's own `opacity` term, applied to the finished tile so
        # the glyph and its halo fade together exactly as they do live.
        faded = relief.blank_plate(tile.width(), tile.height())
        fade_painter = QPainter(faded)
        fade_painter.setOpacity(max(0.0, min(1.0, spec.alpha)))
        fade_painter.drawImage(0, 0, tile)
        fade_painter.end()
        tile = faded
    return relief.stamp_dpr(tile, spec.dpr), float(scaled.width())


def compose_crown(
    glyph_set: dict, sequence: tuple, orientation: str,
    step_deg: float | None = None, offset_deg: float = 0.0,
    ink: dict | None = None, radius_px: float = 0.0,
    tracking_px: float = 0.0,
) -> tuple[tuple[QImage, float, float], ...]:
    """The per-MINUTE work of the live crown: `(image, dial angle, glyph
    rotation)` for every glyph of `sequence`, laid out along the crown
    arc. A dictionary lookup and some arithmetic — no shaping, no
    rasterization — which is what lets a MINUTE-cadence layer afford it
    every tick. Spaces consume a slot and draw nothing, exactly as they
    do in every other crown arc.

    `offset_deg` is THE WORLD OFFSET (`core.world`): the live crown is
    crown text like any other, so it rides the turning world with the
    letters beside it. The seats go through `world.arc_seats`, not a
    bare addition — THE ARC READING LAW (ledger §1, "nothing is
    mirrored"): an offset that carries the arc across the horizon
    reverses which way the run reads, and the reflection puts the time
    back the right way round. `0.0` — the Geocentric answer — leaves
    every angle exactly where it always was.

    THE CROWN ADVANCE LAW (owner defect 2026-08-07 — "2 3 : 3 9" read
    scattered on The One): given `ink` (`crown_glyph_ink`), the crown's
    own `radius_px` and `tracking_px`, every glyph advances by its OWN
    ink width plus the tracking, through
    `core.numerals.crown_advance_angles`. The fixed angular step this
    replaces gave the 0.22-wide colon exactly the room of a 1.45-wide
    M, which is what opened the gaps between the digits. Called WITHOUT
    `ink` (the world-mode golden tests, which pin the arc's DIRECTION
    rather than its metrics) the old fixed-step layout is unchanged —
    and feeding equal advances reproduces it exactly in any case."""
    from core.angles import readable_rotation_deg
    from core.world import arc_seats

    if ink and radius_px > 0.0:
        angles = numerals.crown_advance_angles(
            tuple(
                numerals.arc_degrees(
                    ink.get(glyph, 0.0) + tracking_px, radius_px,
                )
                for glyph in sequence
            ),
            orientation,
        )
    else:
        angles = numerals.crown_arc_angles(len(sequence), orientation, step_deg)
    return tuple(
        (glyph_set[glyph], seat, readable_rotation_deg(seat))
        for glyph, seat in zip(sequence, arc_seats(angles, offset_deg))
        if glyph != " "
    )
