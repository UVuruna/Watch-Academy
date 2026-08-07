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
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath

from config import dial, palette
from core import numerals
from render import numeral_relief as relief
from render.asset_recolor import ring_recolored_image
from render.numeral_fonts import assert_covers, numeral_font
from render.painting import dial_point


# ------------------------------------------------------- THE LETTER SHADOW LAW
# The stamped-shadow math every RING GLYPH wears — moved here from
# `render.layers.ring` (THE TIME CROWN LOOK, owner correction 2026-08-06,
# `research/ring_rework.md` §3): the live crown's glyph tiles now bake
# the SAME shadow stamp the ring's own jewels wear, and this module (not
# `render.layers.ring`) is the shared home both `RingLayer._draw_ring_glyph`
# (a live stamp, every STATIC repaint) and `_crown_plate_image` below
# (a BAKED stamp, once per settings change) can
# import without a cycle — `render.layers.ring` already imports FROM this
# module, never the other way.
def shadow_sample_count(pixel_radius: float) -> int:
    """Sample count for the shadow stamp ring at `pixel_radius` (DEVICE
    pixels). Below `RING_JEWEL_SHADOW_SAMPLES` (today's look at
    ordinary dial sizes) the stamps overlap and fuse into a smooth halo;
    at large pixel radii that fixed count spreads the same 8 copies far
    enough apart that the gaps between them show as a scalloped, jagged
    edge (THE PIXELATION FIX, 1440p owner bug, 2026-08-06). This grows
    the count so adjacent stamps stay under `RING_JEWEL_SHADOW_MAX_GAP_PX`
    apart along the stamp circle's own circumference — the floor never
    shrinks below the original 8."""
    if pixel_radius <= 0:
        return dial.RING_JEWEL_SHADOW_SAMPLES
    needed = math.ceil(
        2.0 * math.pi * pixel_radius / dial.RING_JEWEL_SHADOW_MAX_GAP_PX
    )
    return max(dial.RING_JEWEL_SHADOW_SAMPLES, needed)


def normalized_shadow_alpha(samples: int) -> float:
    """Per-stamp opacity for `samples` copies so the COMPOSITED darkness
    stays what `RING_JEWEL_SHADOW_SAMPLES` stamps at
    `RING_JEWEL_SHADOW_ALPHA` each look like, whatever `samples` grows
    to (`shadow_sample_count`) — extra stamps close the pixel gaps that
    scallop the edge at large dial sizes, they never darken it. Solves
    the standard "N over-composited equal-alpha layers reach target
    coverage" equation, `target = 1 - (1-a)**n`, backwards for a
    per-stamp `a` at the ACTUAL sample count; at the floor count this is
    `RING_JEWEL_SHADOW_ALPHA` exactly (identity, checked by
    `tests/test_ring_split.py`)."""
    target = 1.0 - (1.0 - dial.RING_JEWEL_SHADOW_ALPHA) ** dial.RING_JEWEL_SHADOW_SAMPLES
    if samples <= 0:
        return 0.0
    return 1.0 - (1.0 - target) ** (1.0 / samples)


def _stamp_shadow(painter: QPainter, radius_px: float, draw_copy) -> None:
    """The shared shadow-stamp LOOP: `draw_copy(dx, dy)` paints one
    silhouette copy shifted by `(dx, dy)` from the glyph's own centred
    position; this function only decides HOW MANY copies and at what
    per-stamp opacity (`shadow_sample_count`/`normalized_shadow_alpha`),
    then walks them around the circle of radius `radius_px`. Shared by
    the ring's live jewel stamp and the crown's baked plate stamp below —
    when the stamp runs differs, the stamp law does not (Rule #5)."""
    samples = shadow_sample_count(radius_px)
    painter.save()
    painter.setOpacity(normalized_shadow_alpha(samples))
    for k in range(samples):
        angle = 2.0 * math.pi * k / samples
        draw_copy(radius_px * math.cos(angle), radius_px * math.sin(angle))
    painter.restore()


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


def outer_centreline(ring_size: float) -> float:
    """The OUTER band's centreline as a fraction of the dial radius, for
    an "Outer ring size" of `ring_size` (ring_rework.md §5 — "the width
    of the band the LETTERS and NUMBERS stand in").

    The band's INNER edge is fixed: it abuts the minute band below it,
    and pushing into that would collide with the ticks. So the width
    multiplier moves the OUTER edge alone, and the centreline follows it
    by half the change. `ring_size` 1.0 is the measured band and returns
    `dial.NUMERAL_OUTER_RADIUS_FRACTION` exactly."""
    width = dial.NUMERAL_OUTER_BAND_WIDTH_FRACTION
    inner_edge = dial.NUMERAL_OUTER_RADIUS_FRACTION - width / 2.0
    return inner_edge + width * ring_size / 2.0


def outer_band_edges(ring_size: float) -> tuple[float, float]:
    """The OUTER band's metal edges — `(inner, outer)` as fractions of
    the dial radius. MEASURED off the owner's six outer plates, which
    all carry the same annulus: 0.8858 to 0.9998. The inner edge is
    fixed and the "Outer ring size" multiplier moves the outer one
    (`outer_centreline`'s own rule, stated once as geometry here)."""
    width = dial.NUMERAL_OUTER_BAND_WIDTH_FRACTION
    inner_edge = dial.NUMERAL_OUTER_RADIUS_FRACTION - width / 2.0
    return inner_edge, inner_edge + width * ring_size


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
    LETTER seats (`core.numerals.numeral_hours`); the INNER band NEVER
    rotates in any mode (ledger §2) and carries only the five-minute
    seats its variant leaves empty of arrows."""
    radius = spec.pixels / 2.0
    if spec.band == "outer":
        fraction = outer_centreline(spec.ring_size)
        pairs = [
            (str(hour), numerals.hour_angle(hour, spec.offset_deg))
            for hour in numerals.numeral_hours(spec.jewel_hours)
        ]
    else:
        fraction = dial.MINUTES_RADIUS_FRACTION
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
            relief.seated_path(
                label, font, center,
                numerals.seat_rotation(angle, spec.seating),
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
    unit = _unit_px(spec.pixels)
    font = numeral_font("inner", spec.face, spec.size_units * unit)
    border_px = dial.NUMERAL_GLOW_BORDER_UNITS * unit
    seats = _seats(spec)
    elements = [
        relief.seated_path(
            label, font, center, numerals.seat_rotation(angle, spec.seating),
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

    THE ONE PLATE LAW (owner decree 2026-08-07 — "JEWELS === CROWN TXT
    (SVE) === CROWN LOCATION === CROWN TIME"): EVERY glyph comes from
    HIS plate library, through the exact letter pipeline every ring
    jewel goes through (`_crown_plate_image`). The colon is
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


def _image_silhouette(image: QImage, color: str) -> QImage:
    """`image`'s own alpha, filled flat with `color` — the shadow
    stamp's silhouette for a RASTER glyph (the colon). The live paint
    path gets this for free (`ctx.cache.pixmap_by_height(...,
    tint=SHADOW_STAMP_TINT)`); the crown bakes its tiles outside the
    AssetCache, so the same silhouette is built directly here."""
    silhouette = QImage(image.size(), QImage.Format.Format_ARGB32_Premultiplied)
    silhouette.fill(QColor(color))
    painter = QPainter(silhouette)
    painter.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_DestinationIn
    )
    painter.drawImage(0, 0, image)
    painter.end()
    return silhouette


def _crown_plate_image(
    spec: CrownSpec, box_px: float, resolved: str,
) -> tuple[QImage, float]:
    """ONE crown glyph, from HIS plate — resolved through the exact same
    door every ring jewel resolves its finish through
    (`render.asset_recolor.jewel_metal_file`), scaled to the crown's own
    glyph BOX and finished with THE LETTER SHADOW LAW's stamped halo.
    Returns the tile and the plate's own ink width for THE CROWN ADVANCE
    LAW.

    THE ONE PLATE LAW (owner decree 2026-08-07: "JEWELS === CROWN TXT
    (SVE) === CROWN LOCATION === CROWN TIME"): this is the WHOLE crown
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
