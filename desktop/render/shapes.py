"""Star, polygon and arm PATH geometry.

Builds the QPainterPath/QPolygonF shapes the star and aura layers paint:
which arms are drawn, the aura wedge bounds, star diamonds, curved
polygon faces and the arm shape a skin selects.
"""

import math

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath

from config import constants, palette
from render.calendar_mount import calendar_wedge_bounds, calendar_wheel
from render.painting import dial_point
from render.skin_geometry import arm_half_deg, arm_offset_deg, aura_wedge_anchor, polygon_faces, polygon_shape, rose_star_offsets
from skins.manifest import SkinDefinition

def drawn_arms(
    skin: SkinDefinition, colors: tuple
) -> tuple[tuple[tuple[float, str], ...], ...]:
    """The whole drawn wheel as (angle, hue) arms grouped into PASSES in
    z-order — the bottom of the stack first, the topmost last. One loop
    draws every pointer and both shapes (Rule #5):

    ```
    offset = arm_offset_deg(skin)                # the wheel's own turn
    IF pointer is CALENDAR:
        centres = centre of each of the twelve wedges of the ACTIVE wheel
        IF shape is polygon → ONE pass: all twelve, hue i on wedge i
        ELSE                → TWO passes: the ODD wedges' hexagram first,
                              the EVEN one painted over it
    ELSE:
        stars = rose_star_offsets(skin) OR (0,)  # the Rose's three
        arm k of star s sits at offset + s + k * 360/len(colors)
        IF shape is polygon on the ROSE → ONE pass of all 24 rays
                              (they touch instead of overlapping, so
                              there is no z-stack left to order)
        ELSE                → one pass per star, in the table's order
    ```
    """
    offset = arm_offset_deg(skin)
    if skin.pointer == "calendar":
        centers = [
            offset + (start + end) / 2.0
            for start, end in calendar_wedge_bounds(calendar_wheel(skin))
        ]
        if polygon_shape(skin):
            return (tuple((centers[i], colors[i]) for i in range(len(centers))),)
        # TWO HEXAGRAMS 30° apart (owner sheet): the star standing on the
        # EVEN wedge centers is painted last, so it reads over the other.
        return tuple(
            tuple(
                (centers[i], colors[i])
                for i in range(parity, len(centers), 2)
            )
            for parity in (1, 0)
        )
    span = 360.0 / len(colors)
    stars = rose_star_offsets(skin) or (0.0,)
    arms = tuple(
        tuple(
            (offset + star + k * span, color)
            for k, color in enumerate(colors)
        )
        for star in stars
    )
    if polygon_shape(skin) and len(stars) > 1:
        return (tuple(arm for star_arms in arms for arm in star_arms),)


    return arms


def aura_wedge_bounds(
    skin: SkinDefinition, palette: tuple
) -> list[tuple[float, float]]:
    """THE BACKGROUND FOLLOWS THE STAR (owner's correction round
    2026-07-29) — the (start, end) dial angles of every hue's Aura
    wedge, hue index 0 first. ONE law: a wedge is anchored on its own
    hue's LEAD RAY, and how it sits on that ray is the pointer's
    per-wheel anchor.

    ```
    span  = 360 / number of hues
    lead  = arm_offset_deg(skin) + hue index * span   # the hue's own ray
    low, high = aura_wedge_anchor(skin)               # in spans
    wedge = (lead + low * span, lead + high * span)
    ```

    On every one-star pointer the lead ray IS the arm and the anchor is
    (−½, +½) — the standing arm-centered wedge. On the ROSE, whose eight
    hues each wear three rays, the owner's own numbers apply: LEGACY's
    wedge trails its lead ray (hue 0: 9h -> 12h, boundaries ON the
    lead-ray hours), PROPHECY's stands centered on it (hue 0: 10:30 ->
    13:30). Every wedge still tiles the circle exactly — adjacent wedges
    share a boundary, none overlaps."""
    span = 360.0 / len(palette)
    offset = arm_offset_deg(skin)
    low, high = aura_wedge_anchor(skin)
    return [
        (offset + index * span + low * span, offset + index * span + high * span)
        for index in range(len(palette))
    ]


def star_inner_radius(skin: SkinDefinition, tip: float) -> float:
    """Where the pointer's OWN star seats its inner vertices —
    `tip / (2·cos(half))`, the regular-star value (tip/√3 for the
    hexagram). It is both the star diamond's own side vertex and the
    radius a polygon's edge midpoint is pulled to at full curvature, so
    the two shapes meet there (Rule #5)."""
    half = constants.POINTER_ARM_HALF_ANGLE_DEG[skin.pointer]
    return tip / (2.0 * math.cos(math.radians(half)))


def polygon_curvature(skin: SkinDefinition) -> float:
    """The edge pull actually applied: the reader's slider on a TRUE
    polygon (trio/cross/hexa/octa), 0 everywhere else — the Calendar's
    and the Rose's polygons are stars, and a star never curves (owner
    spec). One gate, so the stored value stays untouched on the shapes
    that ignore it."""
    return skin.polygon_curvature if polygon_faces(skin) else 0.0


def polygon_boundary_radius(skin: SkinDefinition, tip: float) -> float:
    """The radius of a polygon face's two COLOR-BOUNDARY corners.

    On the plain N-gon that corner IS the outer edge's midpoint, so it
    sits on the apothem `tip·cos(180/N)` — and travels inward with the
    curvature exactly as the edge does. The TRINITY's CUBE is the
    owner's exception: its boundary corners are hexagon VERTICES at the
    full tip (three rhombi, six vertices), and the curvature bites into
    the six edges BETWEEN them instead."""
    if skin.pointer == "trio":
        return tip
    apothem = tip * math.cos(math.radians(arm_half_deg(skin)))
    return apothem + polygon_curvature(skin) * (
        star_inner_radius(skin, tip) - apothem
    )


def _pulled_midpoint(
    skin: SkinDefinition, a: QPointF, b: QPointF, tip: float
) -> QPointF:
    """One outer edge's midpoint pulled INWARD along its own radius:
    the chord midpoint at curvature 0 (a straight edge), the star's own
    inner radius at 1. The angle never moves — only the distance."""
    mid = QPointF((a.x() + b.x()) / 2.0, (a.y() + b.y()) / 2.0)
    length = math.hypot(mid.x(), mid.y())
    target = star_inner_radius(skin, tip)
    return mid * ((length + polygon_curvature(skin) * (target - length)) / length)


def _append_edge(
    path: QPainterPath, edge_mode: str, a: QPointF, b: QPointF,
    mid: QPointF, part: str,
) -> None:
    """Append the outer edge a→b, bent through its pulled `mid`, to a
    path already standing at the piece's start point. `part` is "full"
    (the whole edge), "first" (a→mid) or "second" (mid→b) — a polygon
    FACE owns half of each of its two edges, the cube's rhombus owns
    both of its edges whole.

    "notched" draws the two straight segments meeting at `mid`;
    "smooth" draws the quadratic whose CURVE passes through `mid`
    (control = 2·mid − chord midpoint), split at t=0.5 by de Casteljau
    when only half of it is wanted. At curvature 0 `mid` is the chord
    midpoint itself, the control collapses onto the chord and both
    modes draw the plain straight edge."""
    if edge_mode == "notched":
        if part in ("full", "first"):
            path.lineTo(mid)
        if part in ("full", "second"):
            path.lineTo(b)
        return
    chord = QPointF((a.x() + b.x()) / 2.0, (a.y() + b.y()) / 2.0)
    control = mid * 2.0 - chord
    if part == "full":
        path.quadTo(control, b)
    elif part == "first":
        path.quadTo((a + control) / 2.0, mid)
    else:
        path.quadTo((control + b) / 2.0, b)


def star_diamond_path(
    skin: SkinDefinition, tip: float, theta: float
) -> QPainterPath:
    """One star arm: the diamond from the center out to `theta`, its
    side vertices at `arm_half_deg` either side on the star radius."""
    half = arm_half_deg(skin)
    inner = tip / (2.0 * math.cos(math.radians(half)))
    path = QPainterPath()
    path.moveTo(0.0, 0.0)
    path.lineTo(dial_point(theta - half, inner))
    path.lineTo(dial_point(theta, tip))
    path.lineTo(dial_point(theta + half, inner))
    path.closeSubpath()
    return path


def polygon_face_path(
    skin: SkinDefinition, tip: float, theta: float
) -> QPainterPath:
    """One polygon FACE: the kite from the center out to the polygon's
    vertex at `theta`, widening between the two color boundaries at
    `theta ± 180/N`. Straight-edged at curvature 0 it is literally the
    polygon's own slice.

    ```
    half = 180 / drawn arm count
    IF pointer is TRINITY (the CUBE):
        the face is a RHOMBUS of the hexagon — its boundary corners are
        hexagon VERTICES at the tip radius, and it owns TWO WHOLE
        hexagon edges (boundary → vertex → boundary)
    ELSE:
        the face owns HALF of each of the two polygon edges meeting at
        its vertex; its boundary corners ARE those edges' midpoints and
        travel inward with the curvature
    ```
    """
    half = arm_half_deg(skin)
    # With NO pull the two forms are the same straight edge — drawn as
    # segments, so the plain polygon really is a polygon of straight
    # lines rather than a curve that happens to be flat.
    edge_mode = skin.polygon_edge if polygon_curvature(skin) else "notched"
    boundary = polygon_boundary_radius(skin, tip)
    vertex = dial_point(theta, tip)
    before = dial_point(theta - half, boundary)
    after = dial_point(theta + half, boundary)
    path = QPainterPath()
    path.moveTo(0.0, 0.0)
    path.lineTo(before)
    if skin.pointer == "trio":
        _append_edge(
            path, edge_mode, before, vertex,
            _pulled_midpoint(skin, before, vertex, tip), "full",
        )
        _append_edge(
            path, edge_mode, vertex, after,
            _pulled_midpoint(skin, vertex, after, tip), "full",
        )
    else:
        # The boundary corner IS the pulled midpoint of the edge it
        # halves — `polygon_boundary_radius` and `_pulled_midpoint`
        # agree there by construction.
        _append_edge(
            path, edge_mode, dial_point(theta - 2.0 * half, tip), vertex,
            before, "second",
        )
        _append_edge(
            path, edge_mode, vertex, dial_point(theta + 2.0 * half, tip),
            after, "first",
        )
    path.closeSubpath()
    return path


def arm_shape_path(
    skin: SkinDefinition, tip: float, theta: float
) -> QPainterPath:
    """THE ONE arm-geometry entry (Rule #5): the polygon face where the
    reader asked for a true polygon, the star diamond everywhere else —
    including the Calendar's and the Rose's polygons, which are stars
    with touching arms."""
    if polygon_faces(skin):
        return polygon_face_path(skin, tip, theta)
    return star_diamond_path(skin, tip, theta)
