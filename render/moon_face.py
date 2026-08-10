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

from collections.abc import Callable

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

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
# Moon. `TRAVEL` is how far off-centre magnitude 0 pushes it (past the
# limb, i.e. no bite at all); `RISE` tilts the approach so the edge
# does not look like a mirror of the terminator.
_SWEEP_RADIUS_FRACTION = 1.35
_SWEEP_TRAVEL_FRACTION = 2.10
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
    """The Moon's disc in one of `constants.MOON_DARK_STYLES`, centred
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
        painter.restore()


def draw_umbra_sweep(
    painter: QPainter, radius: float, state: str, magnitude: float | None,
) -> None:
    """Earth's shadow as an ACTUAL curved edge crossing the face — the
    owner's chosen lunar treatment, replacing a uniform dimming that
    showed the same picture for a 20 % partial and a totality at
    different brightness.

    `magnitude` is None only for a malformed catalog row (the schema
    always writes it); as in `render.eclipse_glow.eclipse_glow_strength`
    that reads as the STRONGEST case rather than a guessed middle, so a
    broken row over-reports the event instead of hiding it.
    """
    covered = 1.0 if magnitude is None else max(0.0, min(1.0, magnitude))
    travel = (1.0 - covered) * _SWEEP_TRAVEL_FRACTION * radius
    centre = QPointF(travel, -travel * _SWEEP_RISE)
    shadow_radius = radius * _SWEEP_RADIUS_FRACTION
    painter.save()
    disc = QPainterPath()
    disc.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
    painter.setClipPath(disc)
    painter.setPen(Qt.PenStyle.NoPen)
    if state == "lunar_penumbral":
        painter.setBrush(_with_alpha(
            palette.ECLIPSE_PENUMBRAL_WASH, palette.ECLIPSE_PENUMBRAL_ALPHA
        ))
    else:
        painter.setBrush(_with_alpha(
            palette.ECLIPSE_TOTAL_MOON_TINT, palette.ECLIPSE_UMBRA_ALPHA
        ))
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
