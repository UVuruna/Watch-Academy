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
the preset's own letter seats included.

Nothing here runs on the paint path and nothing here touches the disk:
the plates are COMPUTED. The layers only ever blit what they find.
"""

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainterPath

from config import dial, palette
from core import numerals
from render import numeral_relief as relief
from render.asset_recolor import ring_recolored_image
from render.numeral_fonts import assert_covers, numeral_font
from render.painting import dial_point


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
    # THE COMPOSITION LAW's own two keys. `letter_hours` are the OUTER
    # seats the preset's letter art holds (ring counting, midnight =
    # 24) — no numeral is drawn on them. `inner_variant` names the
    # INNER plate the user picked, which decides which five-minute
    # seats carry a number and which carry one of his arrows.
    letter_hours: tuple = ()
    inner_variant: str = ""
    # The ring's own two recolors, so a COMPUTED plate answers the
    # sliders exactly as the printed plate it replaces did.
    tint: str | None = None
    saturation: float = 1.0


@dataclass(frozen=True)
class CrownSpec:
    """The live crown's own key — the eleven glyphs are rasterized once
    per change of it."""

    pixels: int
    dpr: float
    face: str
    size_units: float
    relief_style: str = dial.NUMERAL_RELIEF_DEFAULT
    depth_units: float = dial.NUMERAL_DEPTH_DEFAULT
    light: str = dial.NUMERAL_LIGHT_DEFAULT
    darkness: float = dial.NUMERAL_DARKNESS_DEFAULT
    border_units: float = dial.NUMERAL_BORDER_DEFAULT


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
            for hour in numerals.numeral_hours(spec.letter_hours)
        ]
    else:
        fraction = dial.NUMERAL_INNER_RADIUS_FRACTION
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
        painter.setBrush(QColor(palette.NUMERAL_INNER_INK))
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


def crown_glyph_set(spec: CrownSpec) -> dict:
    """The crown's glyphs, rasterized ONCE per settings change into
    tightly-cropped little images, keyed by glyph.

    The ELEVEN the ledger counts (digits 0-9 and the colon) are always
    built; the `"12h 35min"` format's h/min cut adds its three lowercase
    letters, drawn from the SAME face at
    `dial.CROWN_SMALL_CUT_FRACTION` of the digit size — the plate
    library has no lowercase, which is exactly why the crown's default
    face is chosen for coverage rather than inherited from the hour
    band."""
    glyphs = _CROWNS.get(spec)
    if glyphs is not None:
        return glyphs
    alphabet = numerals.crown_glyph_alphabet()
    assert_covers("outer", spec.face, alphabet)
    unit = _unit_px(spec.pixels)
    full_px = spec.size_units * unit * dial.CROWN_NUMERAL_SIZE_FRACTION
    small_px = full_px * dial.CROWN_SMALL_CUT_FRACTION
    depth_px = spec.depth_units * unit * dial.CROWN_NUMERAL_SIZE_FRACTION
    border_px = spec.border_units * unit * dial.CROWN_NUMERAL_SIZE_FRACTION
    built = {}
    for glyph, small in zip(alphabet, numerals.crown_small_cut(alphabet)):
        if glyph == " ":
            continue
        font = numeral_font("outer", spec.face, small_px if small else full_px)
        built[glyph] = _crown_glyph_image(
            glyph, font, spec, depth_px, border_px,
        )
    _CROWNS[spec] = built
    return built


def _crown_glyph_image(
    glyph: str, font, spec: CrownSpec, depth_px: float, border_px: float,
) -> QImage:
    """One crown glyph on its own little transparent tile, upright, with
    its relief already baked in. The RELIEF is thrown STRAIGHT OUTWARD
    (the crown arc's own radial direction is the glyph's own up, once
    the arc rotation is applied at compose time), so the tile can be
    rotated as a whole without bending its own shadow."""
    path = relief.glyph_path(glyph, font)
    bounds = path.boundingRect()
    pad = depth_px + border_px + 2.0
    side = int(math.ceil(max(bounds.width(), bounds.height()) + 2 * pad))
    tile = relief.blank_plate(max(2, side))
    painter = relief.plate_painter(tile)
    throw = numerals.light_offset(0.0, depth_px, spec.light)
    relief.draw_relief(
        painter, path, spec.relief_style, depth_px, throw, spec.darkness,
    )
    relief.draw_body(painter, path, numerals.parity_role("0"), border_px)
    painter.end()
    return relief.stamp_dpr(tile, spec.dpr)


def compose_crown(
    glyph_set: dict, sequence: tuple, orientation: str,
    step_deg: float | None = None, offset_deg: float = 0.0,
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
    every angle exactly where it always was."""
    from core.angles import readable_rotation_deg
    from core.world import arc_seats

    angles = numerals.crown_arc_angles(len(sequence), orientation, step_deg)
    return tuple(
        (glyph_set[glyph], seat, readable_rotation_deg(seat))
        for glyph, seat in zip(sequence, arc_seats(angles, offset_deg))
        if glyph != " "
    )
