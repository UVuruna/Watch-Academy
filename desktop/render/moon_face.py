"""The Moon's own DISC — the unlit half's three treatments and the
lunar eclipse's umbra sweep (owner verdict 2026-08-10, see
`__about/moon_face.md`).

The terminator GEOMETRY is never re-derived here: it comes from
`render.asset_variants.moon_lit_region`, the one construction the whole
program shares. Only what happens OUTSIDE the lit region changed — the
shipped translucent wash is retired, because a shadow you can see
through leaves a 5 %-lit Moon reading as a full round disc with a
bright edge, which is the defect this round was opened to fix.

`paint_face` is supplied by the caller rather than resolved here: two
of the three styles must install their CLIP before the face is painted,
so this module has to own the ordering, but resolving a pixmap belongs
to the dial. The dial hands in its moon plate, the picker preview hands
in a plain silver disc, and a test hands in a flat fill — one code
path for all three, which also folded away the old asset/procedural
branch pair.
"""

import math
from collections.abc import Callable

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QPen, QRadialGradient,
)

from config import glow, palette
from render.asset_variants import moon_lit_region

# "ghost" is the barely-there disc the cut sits over, present only so
# a new moon stays findable. ("opaque" carries NO alpha constant any
# more — owner correction 2026-08-10: an alpha-thinned shadow read as
# a "wretched translucent gray" on the dial's coloured wedges; the
# style is now a fully opaque BLACK disc under the lit region,
# `palette.MOON_SHADOW_BLACK`.)
_GHOST_ALPHA = 0.55

# The permanent hairline "cut_rim" draws around the TRUE disc, so the
# body's real size is legible at every phase and a new moon is a hollow
# silver ring instead of an empty patch of sky.
_RIM_ALPHA = 0.55
_RIM_WIDTH_FRACTION = 0.055

# The umbra sweep's shadow circle. It is LARGER than the moon disc so
# its visible edge reads as a gentle curve rather than a small circle
# sitting on the face — Earth's shadow really is far wider than the
# Moon. `RISE` tilts the approach so the edge does not look like a
# mirror of the terminator.
#
# THE OFFSET IS NOW THE REAL GEOMETRY (eclipse rework, owner order
# 2026-08-13). Lunar magnitude is the fraction of the Moon's DIAMETER
# inside the shadow, so with a shadow of radius R and a Moon of radius
# r the centre distance is d = R + r - 2*r*magnitude. That formula
# replaces the old `TRAVEL` fudge (a linear push of 2.10 r), and it is
# not a cosmetic change: magnitude 0 now lands exactly on tangency
# (d = R + r, no bite at all) and a magnitude at or above full immersion
# lands on d = 0, the Moon concentric inside the shadow. A PENUMBRAL
# eclipse is measured against the far wider PENUMBRA, so it uses its own
# radius here rather than over-claiming an umbral bite it never has.
_SWEEP_RADIUS_FRACTION = 1.35
_PENUMBRA_RADIUS_FRACTION = 2.40
_SWEEP_RISE = 0.25
_SWEEP_FRINGE_WIDTH_FRACTION = 0.07


def dark_region(fraction: float, radius: float) -> QPainterPath:
    """The disc MINUS the lit region — the shadow's own shape, shared by
    the opaque fill here and by the stations' inner glow
    (`render.marker_marks`), so the two can never disagree about where
    the dark half is."""
    disc = QPainterPath()
    disc.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
    return disc.subtracted(moon_lit_region(fraction, radius))


def draw_moon_disc(
    painter: QPainter, fraction: float, radius: float, style: str,
    paint_face: Callable[[QPainter], None], dark_color: str,
) -> None:
    """The Moon's disc in one of `umbra.MOON_DARK_STYLES`, centred
    on the painter's current origin.

    `paint_face` draws the FULL-moon face (a pixmap on the dial, a flat
    disc in a preview or a test) filling a circle of `radius` at the
    origin; this function decides whether it is clipped first or
    covered after. An unknown style would be a roster/render drift
    rather than user input, so it raises instead of guessing — the
    same choice `render.letter_plates` makes, and for the same reason:
    a silent fallback is how a whole missing treatment ships green.
    """
    if style == "opaque":
        # THE BLACK DISC UNDER THE MOON (owner correction 2026-08-10):
        # the full disc is laid down first as opaque black — so the
        # body's true size always reads and NOTHING of the desktop or
        # the dial's wedges bleeds through the shadow — and the lit
        # region is painted over it. The first cut washed `dark_color`
        # at 0.97 alpha OVER the face instead, which the owner rightly
        # called a translucent gray, identical to the design he had
        # already rejected.
        disc = QPainterPath()
        disc.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
        painter.fillPath(disc, QColor(palette.MOON_SHADOW_BLACK))
        painter.save()
        painter.setClipPath(moon_lit_region(fraction, radius))
        paint_face(painter)
        painter.restore()
        return
    if style not in ("cut_rim", "cut_ghost"):
        raise ValueError(f"unknown moon dark style {style!r}")
    if style == "cut_ghost":
        ghost = QColor(dark_color)
        ghost.setAlphaF(_GHOST_ALPHA)
        disc = QPainterPath()
        disc.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
        painter.fillPath(disc, ghost)
    painter.save()
    painter.setClipPath(moon_lit_region(fraction, radius))
    paint_face(painter)
    painter.restore()
    if style == "cut_rim":
        pen = QPen(_with_alpha(palette.MOON_SILVER, _RIM_ALPHA))
        pen.setWidthF(max(1.0, radius * _RIM_WIDTH_FRACTION))
        painter.save()
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0.0, 0.0), radius, radius)
        # THE SECOND, INNER LINE (owner correction 2026-08-11): beside
        # the white outer circle, a line marking HOW FAR the lit part
        # reaches — the terminator's own curve — so a 2-3% crescent
        # reads as a crescent instead of an almost-invisible sliver.
        # Stroking the lit region's whole boundary draws the limb arc
        # (over the rim, invisible) and the terminator curve (the new
        # inner line) in one honest path — the geometry stays
        # `moon_lit_region`'s, never a re-guess.
        inner = QPen(_with_alpha(palette.MOON_SILVER, _RIM_ALPHA))
        inner.setWidthF(max(1.0, radius * _RIM_WIDTH_FRACTION * 0.7))
        painter.setPen(inner)
        painter.drawPath(moon_lit_region(fraction, radius))
        painter.restore()


def shadow_placement(
    radius: float, state: str, magnitude: float | None,
) -> tuple[QPointF, float]:
    """Where Earth's shadow stands over a Moon of `radius`, and how big
    it is — `(centre, shadow_radius)` in the disc's own coordinates.

    ONE construction for both shadow styles ("umbra_sweep" and
    "blood_moon"), so the two can differ in COLOUR and in what they
    grade, never in where the shadow is. Lunar magnitude is the fraction
    of the Moon's DIAMETER inside the shadow, so with a shadow of radius
    R and a Moon of radius r the centre distance is
    `d = R + r - 2*r*magnitude`, clamped at zero; `_SWEEP_RISE` tilts
    the approach so the edge is not a mirror of the terminator.

    `magnitude` is None only for a malformed catalog row (the schema
    always writes it); as in `render.eclipse_glow.eclipse_glow_strength`
    that reads as the STRONGEST case rather than a guessed middle, so a
    broken row over-reports the event instead of hiding it — here that
    means full immersion, the magnitude at which the centre distance
    falls to zero."""
    shadow_radius = radius * (
        _PENUMBRA_RADIUS_FRACTION if state == "lunar_penumbral"
        else _SWEEP_RADIUS_FRACTION
    )
    full_immersion = (shadow_radius + radius) / (2.0 * radius)
    depth = full_immersion if magnitude is None else magnitude
    distance = max(0.0, shadow_radius + radius - 2.0 * radius * depth)
    travel = distance / math.hypot(1.0, _SWEEP_RISE)
    return QPointF(travel, -travel * _SWEEP_RISE), shadow_radius


def draw_blood_moon(
    painter: QPainter, radius: float, state: str, magnitude: float | None,
) -> None:
    """THE BLOOD MOON (owner ballot 2026-08-13, his recommendation, his
    own specification): inside the umbra the colour slides toward COPPER
    in proportion to DEPTH IN SHADOW; the penumbra stays GREY.

    His sealed reasoning: a Moon in full umbra is copper, not grey,
    because the only light reaching it has passed through every sunrise
    and sunset on Earth at once. So this style paints DEPTH, and depth
    is a real quantity — for a point at distance `s` from the shadow's
    centre, `depth = 1 - s/R_umbra` inside the umbra, zero at its rim.

    It is NOT `draw_umbra_sweep` in another colour, and the difference
    is the whole point (`tests/test_eclipse_distinctness.py` holds it to
    that). The sweep's ramp runs near-black at the shadow's CENTRE out
    to copper at its RIM — a picture of how dark the shadow is. This one
    runs the other way: the deepest point is the MOST copper and the
    umbra's own edge is neutral grey — a picture of how deep the Moon
    has sunk. And both shadow circles are drawn, so the umbra sits as a
    hard-edged copper core inside a soft grey penumbral field, which the
    sweep never shows at all.

    THE PENUMBRA IS ONLY GREY. A penumbral eclipse therefore carries no
    copper anywhere on the face — its umbra circle never reaches the
    disc — which is exactly what such an eclipse looks like, and is why
    this style stays honest about the type it is drawing."""
    centre, shadow_radius = shadow_placement(radius, state, magnitude)
    # BOTH circles, always, from the ONE placement above. Whichever of
    # the two `shadow_placement` measured the magnitude against is the
    # anchor; the other keeps its true proportion to it (the ~1.78 the
    # measured fractions carry — `umbra.ECLIPSE_PENUMBRAL_SPAN_RATIO`
    # states the same ratio for the band's contact marks).
    if state == "lunar_penumbral":
        penumbra_radius = shadow_radius
        umbra_radius = shadow_radius * (
            _SWEEP_RADIUS_FRACTION / _PENUMBRA_RADIUS_FRACTION
        )
    else:
        umbra_radius = shadow_radius
        penumbra_radius = shadow_radius * (
            _PENUMBRA_RADIUS_FRACTION / _SWEEP_RADIUS_FRACTION
        )
    painter.save()
    disc = QPainterPath()
    disc.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
    painter.setClipPath(disc)
    painter.setPen(Qt.PenStyle.NoPen)
    # THE GREY FIELD first: deepest against the umbra's edge, gone at
    # the penumbra's own rim. The umbra's share of the radius is where
    # it stops mattering, so the ramp is anchored there rather than at
    # the centre — inside the umbra this fill is covered anyway.
    penumbral = QRadialGradient(centre, penumbra_radius)
    umbra_stop = min(1.0, umbra_radius / penumbra_radius)
    penumbral.setColorAt(0.0, _with_alpha(
        palette.ECLIPSE_BLOOD_PENUMBRA_COLOR,
        palette.ECLIPSE_BLOOD_PENUMBRA_ALPHA,
    ))
    penumbral.setColorAt(umbra_stop, _with_alpha(
        palette.ECLIPSE_BLOOD_PENUMBRA_COLOR,
        palette.ECLIPSE_BLOOD_PENUMBRA_ALPHA,
    ))
    penumbral.setColorAt(1.0, _with_alpha(
        palette.ECLIPSE_BLOOD_PENUMBRA_COLOR, 0.0
    ))
    painter.setBrush(penumbral)
    painter.drawEllipse(centre, penumbra_radius, penumbra_radius)
    # THE DEPTH RAMP inside the umbra: copper at the deepest point,
    # neutral grey at depth zero. The stop positions ARE the depth
    # scale read backwards (position p from the centre => depth 1-p).
    umbral = QRadialGradient(centre, umbra_radius)
    umbral.setColorAt(0.0, _with_alpha(
        palette.ECLIPSE_TOTAL_MOON_TINT, palette.ECLIPSE_BLOOD_UMBRA_ALPHA
    ))
    umbral.setColorAt(1.0, _with_alpha(
        palette.ECLIPSE_BLOOD_EDGE_COLOR, palette.ECLIPSE_BLOOD_UMBRA_ALPHA
    ))
    painter.setBrush(umbral)
    painter.drawEllipse(centre, umbra_radius, umbra_radius)
    if glow.ECLIPSE_STATE_FRINGE[state]:
        # The ozone rim, on the UMBRA's edge — the same turquoise every
        # other eclipse treatment wears (owner seal 2026-07-18), so one
        # event reads as one event wherever it is drawn.
        pen = QPen(QColor(palette.ECLIPSE_LUNAR_FRINGE_COLOR))
        pen.setWidthF(max(1.0, radius * _SWEEP_FRINGE_WIDTH_FRACTION))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(centre, umbra_radius, umbra_radius)
    painter.restore()


def draw_umbra_sweep(
    painter: QPainter, radius: float, state: str, magnitude: float | None,
) -> None:
    """Earth's shadow as an ACTUAL curved edge crossing the face — the
    owner's chosen lunar treatment, replacing a uniform dimming that
    showed the same picture for a 20 % partial and a totality at
    different brightness.

    The shadow's placement is `shadow_placement` above — shared with
    "blood_moon" so the two styles can never disagree about WHERE the
    shadow stands, only about what they paint inside it.
    """
    centre, shadow_radius = shadow_placement(radius, state, magnitude)
    painter.save()
    disc = QPainterPath()
    disc.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
    painter.setClipPath(disc)
    painter.setPen(Qt.PenStyle.NoPen)
    if state == "lunar_penumbral":
        # THE PENUMBRA DEEPENS INWARD, and it must be DRAWN that way.
        # A penumbral eclipse's shadow is so wide that at its own
        # magnitude the Moon sits almost entirely inside it, so a flat
        # wash produced a uniformly dimmed disc — pixel for pixel the
        # picture the "halo" style draws by multiplying the whole face.
        # Two styles, one picture, and the distinctness measure caught
        # it. The gradient is not a workaround: the penumbra really is
        # darkest toward the umbra and fades to nothing at its rim.
        gradient = QRadialGradient(centre, shadow_radius)
        gradient.setColorAt(0.0, _with_alpha(
            palette.ECLIPSE_PENUMBRAL_WASH, palette.ECLIPSE_PENUMBRAL_ALPHA
        ))
        gradient.setColorAt(1.0, _with_alpha(
            palette.ECLIPSE_PENUMBRAL_WASH, 0.0
        ))
        painter.setBrush(gradient)
    else:
        # THE SHADOW HAS A CENTRE (eclipse rework): a gradient from the
        # near-black core out to the copper rim, instead of the flat
        # copper circle that left a TOTAL eclipse — the Moon wholly
        # inside the shadow — as a featureless disc with no edge to see.
        # At totality this graded copper IS the picture: the "blood
        # moon" is lit only by the light bent through every sunrise and
        # sunset on Earth at once, and it is brightest toward the rim.
        gradient = QRadialGradient(centre, shadow_radius)
        gradient.setColorAt(0.0, _with_alpha(
            palette.ECLIPSE_UMBRA_CORE_COLOR, palette.ECLIPSE_UMBRA_ALPHA
        ))
        gradient.setColorAt(1.0, _with_alpha(
            palette.ECLIPSE_TOTAL_MOON_TINT, palette.ECLIPSE_UMBRA_ALPHA
        ))
        painter.setBrush(gradient)
    painter.drawEllipse(centre, shadow_radius, shadow_radius)
    if glow.ECLIPSE_STATE_FRINGE[state]:
        # The ozone rim at the umbra's own edge — the SAME turquoise the
        # halo's fringe wears (owner seal 2026-07-18), now drawn where
        # the boundary actually is instead of on a gradient stop.
        pen = QPen(QColor(palette.ECLIPSE_LUNAR_FRINGE_COLOR))
        pen.setWidthF(max(1.0, radius * _SWEEP_FRINGE_WIDTH_FRACTION))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(centre, shadow_radius, shadow_radius)
    painter.restore()


def _with_alpha(color: str, alpha: float) -> QColor:
    value = QColor(color)
    value.setAlphaF(alpha)
    return value
