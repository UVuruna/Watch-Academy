"""Everything drawn AROUND an Earth/Moon marker — the position
pointer's three shapes and the four life stations' marks (owner verdict
2026-08-10, see `__about/marker_marks.md`).

THE SOLAR ECLIPSE IS NOT HERE any more: its six pictures moved to
`render.solar_eclipse` on 2026-08-13 when the ballot's three new styles
were painted and this file crossed THE STRUCTURE LAW's threshold. The
line is responsibility, not size — this module draws what a body wears
on an ORDINARY day, that one draws the event.

THE ANGLE IS NEVER "UP": every vertex here is a `painting.dial_point`,
so a mark rides the body's real seat on the circle. The owner had to
correct exactly this once (2026-08-10) — the proposals page drew each
pointer straight up, which is only true for a body at the top of the
dial. The shipped code was already radial; the mockup was the thing
that was wrong, and `tests/test_marker_pointer.py` now pins it for all
three shapes so neither can drift again.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QPen, QPolygonF, QRadialGradient,
)

from config import dial, glow, palette, umbra
from render.eclipse_glow import draw_event_glow
from render.moon_face import dark_region
from render.painting import dial_point
# THE SOLAR ECLIPSE MOVED OUT (2026-08-13, THE STRUCTURE LAW): its six
# pictures live in `render.solar_eclipse` now — see that module's
# docstring for the responsibility line. These two names are re-exported
# HERE, unchanged, because every call site in the app and in the teeth
# already reaches them through this module and a rename would be churn
# with no reader benefit. One definition, one door more.
from render.solar_eclipse import (        # noqa: F401 — re-export, see above
    draw_solar_eclipse, solar_occulter_geometry,
)

# ══════════════════════════════════════════════════════════════════
# THE MARK REACH LIMIT — nothing here may grow past the halo
# ══════════════════════════════════════════════════════════════════
# `glow.MARK_REACH_LIMIT` is the outer wall for EVERY mark drawn around
# a body — its derivation and its headroom are documented there, beside
# the halo scale it comes from. The first cut of this module ignored the
# wall: a corona at 1.8x the body radius against a 1.5x margin painted
# an opaque ray straight through the window edge, and `test_pointer.py`'s
# never-clipped tooth caught it. It is asserted below, so a future tweak
# that pushes a mark outward fails at import instead of on the owner's
# screen.

# The station marks' own radial room, as fractions of the body radius.
_MARK_GAP = 0.14            # clear air between the body and its mark
_CORONA_LENGTH = 0.13       # how far the zenith's rays reach past the gap
_CORONA_RAYS = 20
_SEED_DASH = (2.0, 4.0)     # birth's dashed ring, in mark-stroke widths
_MARK_WIDTH_FRACTION = 0.11
_INNER_GLOW_ALPHA = 0.62

# The day/night wedge: the ring the Sun's day-length fills.
_WEDGE_RADIUS = 1.15
_WEDGE_WIDTH_FRACTION = 0.20



# THE WALL, checked at import (`tests/test_moving_bodies.py` also pins
# it, but a module that cannot even load is the louder failure): the
# outermost pixel any mark here can touch, against the limit above.
# `render.solar_eclipse` asserts its own half against the same wall.
_OUTERMOST_MARK = max(
    1.0 + _MARK_GAP + _CORONA_LENGTH + _MARK_WIDTH_FRACTION / 2,
    _WEDGE_RADIUS + _WEDGE_WIDTH_FRACTION / 2,
)
assert _OUTERMOST_MARK <= glow.MARK_REACH_LIMIT, (
    f"a marker mark reaches {_OUTERMOST_MARK:.3f} of the body radius, past "
    f"the {glow.MARK_REACH_LIMIT:.3f} the window margin reserves — it would be "
    "clipped by the transparent window edge (THE SPACE & LEGIBILITY LAW)"
)


def station_of_moon_event(name: str | None) -> str | None:
    """The life station a moon event opens, or None when the tick is
    not sitting on a principal instant at all."""
    return None if name is None else umbra.MOON_STATION_OF_PHASE.get(name)


def station_of_season_event(name: str | None) -> str | None:
    """The Sun's twin of `station_of_moon_event`, resolved from the
    zone-aware event NAME the tick already carries — so a southern
    observer's Winter Solstice is his birth station even though it sits
    at the wheel angle a northern observer calls midsummer."""
    return None if name is None else umbra.SUN_STATION_OF_EVENT.get(name)


# ----------------------------------------------------------------------
# THE POSITION POINTER
# ----------------------------------------------------------------------

def draw_pointer(
    painter: QPainter, shape: str, angle_deg: float, dial_radius: float,
    orbit_fraction: float, half_size_fraction: float, color: str,
    tip_radius: float | None = None,
) -> None:
    """One of `umbra.MARKER_POINTER_SHAPES` BEHIND the body (owner
    correction 2026-08-11, "IZA NE ISPRED ZEMLJE" — the caller draws
    this BEFORE the body's own disc): its tip on the marked point, its
    base hidden under the disc, so only the flanks show beside the
    curve.

    THE DIRECTION FOLLOWS THE BODY (owner correction 2026-08-11, slika
    4/5: "obrni strelicu... jer je sada na RINGU"): `tip_radius` is the
    marked point's own radius — the 360 small pointers' tips. A body on
    its ordinary orbit sits INSIDE that circle, so the arrow points
    OUTWARD; a body relocated onto the ring band (its event window)
    sits OUTSIDE it, so the arrow FLIPS and points INWARD at the same
    marked point. When `tip_radius` is None the measured plate ratio
    reproduces the ordinary outward case exactly.

    `orbit_fraction` and `half_size_fraction` are the CALLER's own
    numbers — this body's own orbit and half-size, each already
    carrying hover-enlarge — and every dimension here is PROPORTIONAL
    to that half-size (the fixed-size first cut read enormous next to
    a small-scaled body). Every shape wears the white
    `MARKER_BORDER_RGBA` outline the Earth's procedural disc wears, so
    it reads against ANY fill colour.
    """
    half_size = dial_radius * half_size_fraction
    if tip_radius is None:
        # THE BRIDGE TO THE SMALL TICKS (owner third round 2026-08-11):
        # the tips/last-line ratio is the measured plate geometry,
        # never a free protrusion.
        tip = dial_radius * (orbit_fraction + half_size_fraction) * (
            dial.RING_INNER_TICK_INNER_FRACTION
            / dial.RING_INNER_CONTENT_INNER_FRACTION
        )
    else:
        tip = tip_radius
    inward = dial_radius * orbit_fraction > tip
    # The body edge the arrow emerges from: the side FACING the marked
    # point, so the base always hides under the disc.
    edge = (
        orbit_fraction - half_size_fraction if inward
        else orbit_fraction + half_size_fraction
    )
    depth = half_size * dial.MARKER_POINTER_LENGTH_RATIO
    half_width = half_size * dial.MARKER_POINTER_WIDTH_RATIO
    base = dial_radius * edge + (depth if inward else -depth)
    half_deg = math.degrees(half_width / max(1.0, base))
    outline = QPen(QColor(*palette.MARKER_BORDER_RGBA))
    outline.setWidthF(
        max(1.0, dial_radius * dial.MARKER_POINTER_OUTLINE_WIDTH_FRACTION)
    )
    painter.save()
    # NOTHING RENDERS INSIDE THE BODY'S OWN CIRCLE (owner correction
    # 2026-08-11, the hollow-crescent screenshot: the shape behind a
    # nearly-empty Moon showed THROUGH the disc and read as an ugly
    # oversized triangle). The disc region is clipped out, so an opaque
    # Earth and a hollow Moon both show only the bridge outside the rim.
    body_center = dial_point(angle_deg, dial_radius * orbit_fraction)
    keep = QPainterPath()
    keep.addRect(QRectF(-dial_radius, -dial_radius, 2 * dial_radius, 2 * dial_radius))
    disc = QPainterPath()
    disc.addEllipse(body_center, half_size, half_size)
    painter.setClipPath(keep.subtracted(disc))
    if shape == "triangle":
        painter.setPen(outline)
        painter.setBrush(QColor(color))
        painter.drawPolygon(QPolygonF([
            dial_point(angle_deg, tip),
            dial_point(angle_deg - half_deg, base),
            dial_point(angle_deg + half_deg, base),
        ]))
    elif shape == "chevron":
        # THE SAME DESIGN AS THE TRIANGLE, LINE ONLY (owner correction
        # 2026-08-10: the open-V first cut was far too wide and looked
        # nothing like the triangle beside it). Identical vertices, no
        # fill — a colour stroke over a thin white understroke so the
        # outline reads against any wedge.
        path = QPainterPath()
        path.moveTo(dial_point(angle_deg, tip))
        path.lineTo(dial_point(angle_deg - half_deg, base))
        path.lineTo(dial_point(angle_deg + half_deg, base))
        path.closeSubpath()
        stroke = QPen()
        stroke.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for pen_color, width in (
            (QColor(*palette.MARKER_BORDER_RGBA), outline.widthF() * 3.0),
            (QColor(color), outline.widthF() * 1.8),
        ):
            stroke.setColor(pen_color)
            stroke.setWidthF(width)
            painter.setPen(stroke)
            painter.drawPath(path)
    elif shape == "gem":
        # THE WHOLE DIAMOND SHOWS (owner correction 2026-08-11, slika
        # 2/3: parts under the disc made it read like the triangle):
        # one vertex touches the body's own edge, the other stands on
        # the marked point — the ENTIRE gem lives between the body's
        # circle and the 360 circle. Its long axis is the radius and
        # height >= width by law (`dial.MARKER_GEM_WIDTH_RATIO` < 1,
        # "ako je ista vrednost moze blago veca visina").
        body_edge = dial_radius * edge
        height = abs(body_edge - tip)
        mid = (body_edge + tip) / 2.0
        half_width_deg = math.degrees(
            height * dial.MARKER_GEM_WIDTH_RATIO / 2.0 / max(1.0, mid)
        )
        painter.setPen(outline)
        painter.setBrush(QColor(color))
        painter.drawPolygon(QPolygonF([
            dial_point(angle_deg, tip),
            dial_point(angle_deg + half_width_deg, mid),
            dial_point(angle_deg, body_edge),
            dial_point(angle_deg - half_width_deg, mid),
        ]))
    else:
        painter.restore()
        raise ValueError(f"unknown marker pointer shape {shape!r}")
    painter.restore()


# ----------------------------------------------------------------------
# THE FOUR STATIONS
# ----------------------------------------------------------------------

def draw_station_mark(
    painter: QPainter, style: str, station: str, radius: float, color: str,
    fraction: float | None = None, origin: QPointF | None = None,
) -> None:
    """The Moon's station mark BEHIND the body — the halo or the arc
    grammar, both of them background ornament.

    THE INNER GLOW IS NOT DRAWN HERE. It belongs inside the dark half,
    which means on TOP of the body, and `draw_station_inner_glow` is
    its own call for exactly that reason. The first cut of this module
    drew both here and the body's own disc then covered the inner glow
    completely — caught not by a test but by opening the render
    (`.claude/shots/hands-and-bodies/proof_stations.png`), which is the
    whole argument for looking at the picture.

    `fraction` is accepted and ignored by the two background styles; it
    is kept in the signature so the caller passes the same arguments to
    both halves of the mark.
    """
    del fraction                      # see the docstring — foreground only
    painter.save()
    if origin is not None:
        painter.translate(origin)
    try:
        if style == "uniform":
            _halo(painter, radius, color, 1.0)
        elif style == "arc_grammar":
            # THE HALO STAYS. The first cut drew the grammar INSTEAD of
            # it and four glow tests fell over — rightly: the halo is
            # what makes an event marker findable at a glance on a
            # transparent widget over an arbitrary desktop, and a thin
            # arc cannot do that job. The grammar answers a different
            # question — WHICH station — so it is drawn on top of the
            # halo, not in place of it.
            _halo(painter, radius, color, 1.0)
            _arc_grammar(painter, station, radius, color)
        elif style == "inner_glow":
            outer, _inner = umbra.MOON_STATION_GLOW[station]
            # THE INTENSITY RAMP (owner spec 2026-08-10): the radius is
            # the SAME for all four stations — a full moon burns
            # brighter, it does not reach further.
            _halo(painter, radius, color, outer)
        else:
            raise ValueError(f"unknown station style {style!r}")
    finally:
        painter.restore()


def draw_station_inner_glow(
    painter: QPainter, style: str, station: str, radius: float, color: str,
    fraction: float, origin: QPointF | None = None,
) -> None:
    """The station mark's FOREGROUND half — light inside the Moon's dark
    part, drawn after the body so the disc cannot cover it.

    Only "inner_glow" has one, and only at the stations whose inner
    strength is non-zero: the owner's ramp gives birth and youth an
    inner glow and leaves age without one, while the zenith has no dark
    half left to glow into at all."""
    if style != "inner_glow":
        return
    _outer, inner = umbra.MOON_STATION_GLOW[station]
    if inner <= 0.0:
        return
    painter.save()
    if origin is not None:
        painter.translate(origin)
    try:
        _inner_glow(painter, radius, color, inner, fraction)
    finally:
        painter.restore()


def draw_sun_station_mark(
    painter: QPainter, style: str, station: str, radius: float,
    gold: str, day_fraction: float, origin: QPointF | None = None,
) -> None:
    """The Sun's station mark. Two styles are its own: "uniform_seasonal"
    wears the season's hue from `palette.INSTRUMENT_SEASON_COLORS` — the
    owner's own sampled season values, so the halo can never drift from
    the season wedge painted under it — and "day_night_wedge" fills a
    ring to `day_fraction`, the day's own share of the 24 hours."""
    painter.save()
    if origin is not None:
        painter.translate(origin)
    try:
        _sun_station_body(painter, style, station, radius, gold, day_fraction)
    finally:
        painter.restore()


def _sun_station_body(
    painter: QPainter, style: str, station: str, radius: float,
    gold: str, day_fraction: float,
) -> None:
    if style == "uniform_gold":
        _halo(painter, radius, gold, 1.0)
        return
    if style == "uniform_seasonal":
        season = umbra.SUN_STATION_SEASONS[station]
        _halo(painter, radius, palette.INSTRUMENT_SEASON_COLORS[season], 1.0)
        return
    if style == "arc_grammar":
        # The halo stays under the grammar — see the Moon's twin above
        # for why (it is what makes an event marker findable at all).
        _halo(painter, radius, gold, 1.0)
        _arc_grammar(painter, station, radius, gold)
        return
    if style != "day_night_wedge":
        raise ValueError(f"unknown sun station style {style!r}")
    _halo(painter, radius, gold, 1.0)
    ring_radius = radius * _WEDGE_RADIUS
    pen = QPen()
    pen.setWidthF(radius * _WEDGE_WIDTH_FRACTION)
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    rect = QRectF(-ring_radius, -ring_radius, 2 * ring_radius, 2 * ring_radius)
    painter.save()
    painter.setBrush(Qt.BrushStyle.NoBrush)
    pen.setColor(QColor(palette.NIGHT_WEDGE_GROUND))
    painter.setPen(pen)
    painter.drawEllipse(rect)
    pen.setColor(QColor(gold))
    painter.setPen(pen)
    span = max(0.0, min(1.0, day_fraction)) * 360.0
    # Qt's angles are CCW from 3 o'clock in 1/16 degrees; the day is
    # centred on the TOP of the mark so night closes at the bottom.
    painter.drawArc(rect, round((90.0 - span / 2) * 16), round(span * 16))
    painter.restore()


def _arc_grammar(
    painter: QPainter, station: str, radius: float, color: str,
) -> None:
    """Birth is a dashed seed ring, youth an arc opening on the waxing
    side, zenith a full corona, age the arc closing from the other
    side — one grammar, learned once on the Moon and read again on the
    Sun."""
    mark_radius = radius * (1.0 + _MARK_GAP)
    width = max(1.0, radius * _MARK_WIDTH_FRACTION)
    pen = QPen(QColor(color))
    pen.setWidthF(width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    rect = QRectF(-mark_radius, -mark_radius, 2 * mark_radius, 2 * mark_radius)
    painter.save()
    painter.setBrush(Qt.BrushStyle.NoBrush)
    if station == "birth":
        pen.setDashPattern(list(_SEED_DASH))
        painter.setPen(pen)
        painter.drawEllipse(rect)
    elif station == "youth":
        painter.setPen(pen)
        painter.drawArc(rect, round(90.0 * 16), round(-180.0 * 16))
    elif station == "age":
        painter.setPen(pen)
        painter.drawArc(rect, round(90.0 * 16), round(180.0 * 16))
    elif station == "zenith":
        painter.setPen(pen)
        painter.drawEllipse(rect)
        reach = mark_radius + radius * _CORONA_LENGTH
        for index in range(_CORONA_RAYS):
            theta = index / _CORONA_RAYS * 2 * math.pi
            painter.drawLine(
                QPointF(math.cos(theta) * mark_radius,
                        math.sin(theta) * mark_radius),
                QPointF(math.cos(theta) * reach, math.sin(theta) * reach),
            )
    else:
        painter.restore()
        raise ValueError(f"unknown station {station!r}")
    painter.restore()


def _halo(
    painter: QPainter, radius: float, color: str, strength: float,
) -> None:
    """The event halo, delegated to `render.eclipse_glow.draw_event_glow`
    — THE SAME function every other event marker uses, never a second
    one of the same shape.

    Written as a copy first, and three window-margin tests caught it: the
    margin the window reserves so a halo is never clipped is computed
    from `glow.GLOW_RADIUS_SCALE`, so a private halo of a different reach
    painted straight through the window edge. One definition means a
    re-tuned glow moves the margin with it (Rule #5).

    `strength` is the station's own intensity ramp — the owner's spec is
    that the full moon burns BRIGHTER, not wider, so this scales alpha
    only and the radius is identical at all four stations."""
    draw_event_glow(painter, QPointF(0.0, 0.0), radius, color, strength)


def _inner_glow(
    painter: QPainter, radius: float, color: str, strength: float,
    fraction: float,
) -> None:
    """Light INSIDE the dark half (owner spec 2026-08-10: youth carries
    a glow on the dark part as well as outside). Clipped to
    `moon_face.dark_region`, so the lit half is never washed out and
    the two modules cannot disagree about where the shadow is."""
    painter.save()
    painter.setClipPath(dark_region(fraction, radius))
    gradient = QRadialGradient(QPointF(0.0, 0.0), radius)
    core = QColor(color)
    core.setAlphaF(_INNER_GLOW_ALPHA * strength)
    edge = QColor(color)
    edge.setAlphaF(0.0)
    gradient.setColorAt(0.0, core)
    gradient.setColorAt(1.0, edge)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawEllipse(QPointF(0.0, 0.0), radius, radius)
    painter.restore()


