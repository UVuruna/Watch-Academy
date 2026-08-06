"""The two band plates and the crown's glyph set — built ONCE per
settings change, cached process-wide, blitted every frame.

THE ONE COPY RULE (owner 2026-07-28, extended 2026-08-06): `_PLATES` and
`_CROWNS` are module-level, so N watches showing the same settings hold
ONE copy of each plate — exactly like `render.assets.shared_cache` and
every other shared book. The SPEC dataclasses below are the cache keys:
they carry precisely what can make two plates differ, `offset_deg`
included, so wave 4's Heliocentric rotation re-renders a band without
changing any caller's shape.

Nothing here runs on the paint path and nothing here touches the disk:
the plates are COMPUTED. The layers only ever blit what they find.
"""

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainterPath

from config import dial
from core import numerals
from render import numeral_relief as relief
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
    offset_deg: float = 0.0    # the Heliocentric band rotation (wave 4)


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
    """The band's finished plate, built at most once per spec."""
    plate = _PLATES.get(spec)
    if plate is None:
        plate = (
            _build_outer(spec) if spec.band == "outer" else _build_inner(spec)
        )
        _PLATES[spec] = plate
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


def _seats(spec: BandSpec) -> tuple[tuple[str, float, QPointF], ...]:
    """`(label, seat angle, page-space centre)` for every numeral of the
    band. The OUTER band's angles carry `offset_deg`; the INNER band
    NEVER rotates, in any mode (ledger §2)."""
    radius = spec.pixels / 2.0
    if spec.band == "outer":
        fraction = outer_centreline(spec.ring_size)
        pairs = [
            (label, numerals.hour_angle(hour, spec.offset_deg))
            for hour, label in enumerate(numerals.hour_labels())
        ]
    else:
        fraction = dial.NUMERAL_INNER_RADIUS_FRACTION
        pairs = [
            (label, numerals.minute_angle(int(label)))
            for label in numerals.minute_labels()
        ]
    return tuple(
        (label, angle, dial_point(angle, radius * fraction))
        for label, angle in pairs
    )


def _build_outer(spec: BandSpec) -> QImage:
    """The 24 hour numerals, in relief, on transparency.

    Three passes, in this order: the CONTACT BLUR (a whole-band
    silhouette, blurred once — never a per-glyph halo and never N
    stamped copies), the RELIEF copies, then the bodies. Doing the blur
    as one band-wide layer is what keeps the edge smooth at 1440p; the
    radius comes from the plate's own pixel size, so it scales by
    construction."""
    assert_covers("outer", spec.face, numerals.hour_labels())
    unit = _unit_px(spec.pixels)
    font = numeral_font("outer", spec.face, spec.size_units * unit)
    depth_px = spec.depth_units * unit
    border_px = spec.border_units * unit
    seats = _seats(spec)
    paths = tuple(
        (
            label,
            angle,
            relief.seated_path(
                label, font, center,
                numerals.seat_rotation(angle, spec.seating),
            ),
        )
        for label, angle, center in seats
    )
    plate = relief.blank_plate(spec.pixels)
    blur_px = spec.contact_blur_units * unit
    if blur_px > 0.0:
        silhouette = relief.blank_plate(spec.pixels)
        painter = relief.plate_painter(silhouette)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(Qt.GlobalColor.black)
        for _label, _angle, path in paths:
            painter.drawPath(path)
        painter.end()
        relief.composite(
            plate, relief.box_blur_alpha(silhouette, blur_px), 1.0,
            dial.NUMERAL_GLOW_PASSES,
        )
    painter = relief.plate_painter(plate)
    for _label, angle, path in paths:
        relief.draw_relief(
            painter, path, spec.relief_style, depth_px,
            numerals.light_offset(
                angle, depth_px, spec.light,
                tuple(value * unit for value in spec.fixed_offset),
            ),
            spec.darkness,
        )
    for label, _angle, path in paths:
        relief.draw_body(painter, path, numerals.parity_role(label), border_px)
    painter.end()
    return relief.stamp_dpr(plate, spec.dpr)


def _tick_path(kind: str, angle: float, radius: float) -> QPainterPath:
    """One tick LINE as a path: a radial stroke running inward from the
    band's outer edge, its length and width from the kind's own row in
    `config.dial`. The POINTER kind is the quarter ARROW — the same
    radial run, closed into a head at its inner end."""
    outer = radius * dial.NUMERAL_TICK_OUTER_FRACTION
    inner = outer - radius * dial.NUMERAL_TICK_LENGTHS[kind]
    half = radius * dial.NUMERAL_TICK_WIDTHS[kind] / 2.0
    start = dial_point(angle, outer)
    end = dial_point(angle, inner)
    path = QPainterPath()
    direction = QPointF(end.x() - start.x(), end.y() - start.y())
    length = math.hypot(direction.x(), direction.y()) or 1.0
    normal = QPointF(-direction.y() / length * half, direction.x() / length * half)
    if kind == numerals.TICK_POINTER:
        head = QPointF(
            start.x() + direction.x() * dial.NUMERAL_POINTER_HEAD_FRACTION,
            start.y() + direction.y() * dial.NUMERAL_POINTER_HEAD_FRACTION,
        )
        wide = QPointF(normal.x() * dial.NUMERAL_POINTER_HEAD_WIDTH,
                       normal.y() * dial.NUMERAL_POINTER_HEAD_WIDTH)
        path.moveTo(start + wide)
        path.lineTo(head + normal)
        path.lineTo(end + normal)
        path.lineTo(end - normal)
        path.lineTo(head - normal)
        path.lineTo(start - wide)
        path.closeSubpath()
        return path
    path.moveTo(start + normal)
    path.lineTo(end + normal)
    path.lineTo(end - normal)
    path.lineTo(start - normal)
    path.closeSubpath()
    return path


def _build_inner(spec: BandSpec) -> QImage:
    """The minute numerals plus the five families of tick LINE, all in
    WHITE GLOW (ring_rework §2: small radius, strong intensity, a
    border+glow, never a diffuse halo — the same recipe for every inner
    element). The glow is one band-wide blurred silhouette composited
    `NUMERAL_GLOW_PASSES` times: several small passes read as a tight
    bright edge where one wide pass reads as smoke."""
    assert_covers("inner", spec.face, numerals.minute_labels())
    unit = _unit_px(spec.pixels)
    radius = spec.pixels / 2.0
    font = numeral_font("inner", spec.face, spec.size_units * unit)
    border_px = dial.NUMERAL_GLOW_BORDER_UNITS * unit
    elements = [
        _tick_path(kind, angle, radius)
        for angle, kind in numerals.inner_tick_plan()
    ]
    elements += [
        relief.seated_path(
            label, font, center, numerals.seat_rotation(angle, spec.seating),
        )
        for label, angle, center in _seats(spec)
    ]
    plate = relief.blank_plate(spec.pixels)
    silhouette = relief.blank_plate(spec.pixels)
    painter = relief.plate_painter(silhouette)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(Qt.GlobalColor.white)
    for path in elements:
        painter.drawPath(path)
    painter.end()
    relief.composite(
        plate,
        relief.box_blur_alpha(silhouette, dial.NUMERAL_GLOW_RADIUS_UNITS * unit),
        1.0, dial.NUMERAL_GLOW_PASSES,
    )
    painter = relief.plate_painter(plate)
    for path in elements:
        relief.draw_inner_ink(painter, path, border_px)
    painter.end()
    return relief.stamp_dpr(plate, spec.dpr)


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
    glyph_set: dict, sequence: tuple, orientation: str, step_deg: float | None = None,
) -> tuple[tuple[QImage, float, float], ...]:
    """The per-MINUTE work of the live crown: `(image, dial angle, glyph
    rotation)` for every glyph of `sequence`, laid out along the crown
    arc. A dictionary lookup and some arithmetic — no shaping, no
    rasterization — which is what lets a MINUTE-cadence layer afford it
    every tick. Spaces consume a slot and draw nothing, exactly as they
    do in every other crown arc."""
    from core.angles import readable_rotation_deg

    angles = numerals.crown_arc_angles(len(sequence), orientation, step_deg)
    return tuple(
        (glyph_set[glyph], angle % 360.0, readable_rotation_deg(angle % 360.0))
        for glyph, angle in zip(sequence, angles)
        if glyph != " "
    )
