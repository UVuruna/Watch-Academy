"""Everything drawn AROUND an Earth/Moon marker — the position
pointer's three shapes, the four life stations' marks and the solar
eclipse's own geometry (owner verdict 2026-08-10, see
`__about/marker_marks.md`).

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

from config import constants, dial, glow, palette
from render.eclipse_glow import draw_event_glow
from render.moon_face import dark_region
from render.painting import dial_point

# ══════════════════════════════════════════════════════════════════
# THE MARK REACH LIMIT — nothing here may grow past the halo
# ══════════════════════════════════════════════════════════════════
# The transparent window margin the widget reserves is computed from
# `glow.GLOW_RADIUS_SCALE` (`defaults.dial_window_margin_fraction`), so
# that number is the outer wall for EVERY mark in this module, not a
# suggestion. The first cut ignored it: a corona at 1.8x the body radius
# against a 1.5x margin painted an opaque ray straight through the
# window edge, and `test_pointer.py`'s never-clipped tooth caught it.
# Every radius below therefore stays inside that wall WITH HEADROOM —
# the halo is a gradient that has faded to nothing by its own edge, so
# the margin is tight around it, while these marks are opaque strokes
# that would show as a hard line the moment they touched it.
# `_MARK_REACH_LIMIT` is asserted below, so a future tweak that pushes a
# mark outward fails at import instead of on the owner's screen.
_MARK_REACH_LIMIT = glow.GLOW_RADIUS_SCALE * 0.92

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

# The solar eclipse's own geometry.
_BITE_TRAVEL = 2.0          # magnitude 0 walks the occulter clear of the limb
_BITE_RISE = 0.4
_ANNULAR_SHRINK = 0.86      # the occulter is SMALLER than the Sun — the ring of fire
_CORONA_SPIKE_MIN = 1.02
_CORONA_SPIKE_MAX = 1.22
_CORONA_SPIKES = 24
_GAUGE_RADIUS = 1.18
_GAUGE_WIDTH_FRACTION = 0.14

# THE WALL, checked at import (`tests/test_moving_bodies.py` also pins
# it, but a module that cannot even load is the louder failure): the
# outermost pixel any mark here can touch, against the limit above.
_OUTERMOST_MARK = max(
    1.0 + _MARK_GAP + _CORONA_LENGTH + _MARK_WIDTH_FRACTION / 2,
    _WEDGE_RADIUS + _WEDGE_WIDTH_FRACTION / 2,
    _GAUGE_RADIUS + _GAUGE_WIDTH_FRACTION / 2,
    _CORONA_SPIKE_MAX,
)
assert _OUTERMOST_MARK <= _MARK_REACH_LIMIT, (
    f"a marker mark reaches {_OUTERMOST_MARK:.3f} of the body radius, past "
    f"the {_MARK_REACH_LIMIT:.3f} the window margin reserves — it would be "
    "clipped by the transparent window edge (THE SPACE & LEGIBILITY LAW)"
)


def station_of_moon_event(name: str | None) -> str | None:
    """The life station a moon event opens, or None when the tick is
    not sitting on a principal instant at all."""
    return None if name is None else constants.MOON_STATION_OF_PHASE.get(name)


def station_of_season_event(name: str | None) -> str | None:
    """The Sun's twin of `station_of_moon_event`, resolved from the
    zone-aware event NAME the tick already carries — so a southern
    observer's Winter Solstice is his birth station even though it sits
    at the wheel angle a northern observer calls midsummer."""
    return None if name is None else constants.SUN_STATION_OF_EVENT.get(name)


# ----------------------------------------------------------------------
# THE POSITION POINTER
# ----------------------------------------------------------------------

def draw_pointer(
    painter: QPainter, shape: str, angle_deg: float, dial_radius: float,
    orbit_fraction: float, half_size_fraction: float, color: str,
) -> None:
    """One of `constants.MARKER_POINTER_SHAPES` straddling the body's
    own edge at its own dial angle.

    `orbit_fraction` and `half_size_fraction` are the CALLER's own
    numbers — the shared orbit lane and the body's half-size, each
    already carrying hover-enlarge — so the mark always matches the
    body it points at rather than the lane's own clearance sizing.
    Every shape wears the white `MARKER_BORDER_RGBA` outline the Earth's
    procedural disc wears, so it reads against ANY fill colour: the
    first cut of the triangle was gold-on-gold over a yellow wedge,
    geometrically present and invisible to the eye.
    """
    edge = orbit_fraction + half_size_fraction
    tip = dial_radius * (edge + dial.MARKER_POINTER_PROTRUSION_FRACTION)
    base = dial_radius * (
        edge - half_size_fraction * dial.MARKER_POINTER_RECESS_FRACTION
    )
    half = dial.MARKER_POINTER_HALF_DEG
    outline = QPen(QColor(*palette.MARKER_BORDER_RGBA))
    outline.setWidthF(
        max(1.0, dial_radius * dial.MARKER_POINTER_OUTLINE_WIDTH_FRACTION)
    )
    painter.save()
    if shape == "triangle":
        painter.setPen(outline)
        painter.setBrush(QColor(color))
        painter.drawPolygon(QPolygonF([
            dial_point(angle_deg, tip),
            dial_point(angle_deg - half, base),
            dial_point(angle_deg + half, base),
        ]))
    elif shape == "chevron":
        # An open V OUTSIDE the body: it never covers the face, which
        # is what the triangle does to a small Moon.
        stroke = QPen()
        stroke.setCapStyle(Qt.PenCapStyle.RoundCap)
        stroke.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        path = QPainterPath()
        path.moveTo(dial_point(angle_deg - half * 1.5, tip))
        path.lineTo(dial_point(
            angle_deg, tip + dial_radius
            * dial.MARKER_POINTER_PROTRUSION_FRACTION * 1.6
        ))
        path.lineTo(dial_point(angle_deg + half * 1.5, tip))
        for pen_color, width in (
            (QColor(*palette.MARKER_BORDER_RGBA), outline.widthF() * 4.0),
            (QColor(color), outline.widthF() * 2.0),
        ):
            stroke.setColor(pen_color)
            stroke.setWidthF(width)
            painter.setPen(stroke)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
    elif shape == "gem":
        # A faceted diamond seated ON the ring line, joined to the body
        # by a hairline — the ring's own vocabulary, the same language
        # the Moon Horizon Band's culmination diamond already speaks.
        seat = tip + dial_radius * dial.MARKER_POINTER_PROTRUSION_FRACTION * 2.2
        hair = QPen(QColor(*palette.MARKER_BORDER_RGBA))
        hair.setWidthF(outline.widthF())
        painter.setPen(hair)
        painter.drawLine(dial_point(angle_deg, base), dial_point(angle_deg, seat))
        reach = dial_radius * dial.MARKER_POINTER_PROTRUSION_FRACTION * 1.5
        painter.setPen(outline)
        painter.setBrush(QColor(color))
        painter.drawPolygon(QPolygonF([
            dial_point(angle_deg, seat + reach),
            dial_point(angle_deg + half, seat),
            dial_point(angle_deg, seat - reach),
            dial_point(angle_deg - half, seat),
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
            outer, _inner = constants.MOON_STATION_GLOW[station]
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
    _outer, inner = constants.MOON_STATION_GLOW[station]
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
        season = constants.SUN_STATION_SEASONS[station]
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


# ----------------------------------------------------------------------
# THE SOLAR ECLIPSE
# ----------------------------------------------------------------------

def draw_solar_eclipse(
    painter: QPainter, style: str, radius: float, state: str,
    magnitude: float | None, color: str, origin: QPointF | None = None,
) -> None:
    """The Sun-side eclipse in one of `constants.ECLIPSE_SOLAR_STYLES`,
    drawn as an OVERLAY on a body the caller has already painted.

    "halo" adds nothing here — the glow the caller drew behind the
    marker is the whole of that style. The other two make the catalog
    MAGNITUDE visible: "bite" lays a real occulting disc across the
    face (a bite when partial, a ring of fire when annular, a black
    disc in a corona at totality), "magnitude_arc" reads it off a ring
    gauge without touching the body at all.
    """
    covered = 1.0 if magnitude is None else max(0.0, min(1.0, magnitude))
    if style == "halo":
        return
    painter.save()
    if origin is not None:
        painter.translate(origin)
    try:
        _solar_eclipse_body(painter, style, radius, state, covered, color)
    finally:
        painter.restore()


def _solar_eclipse_body(
    painter: QPainter, style: str, radius: float, state: str,
    covered: float, color: str,
) -> None:
    if style == "magnitude_arc":
        gauge = radius * _GAUGE_RADIUS
        rect = QRectF(-gauge, -gauge, 2 * gauge, 2 * gauge)
        pen = QPen()
        pen.setWidthF(radius * _GAUGE_WIDTH_FRACTION)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen.setColor(QColor(palette.NIGHT_WEDGE_GROUND))
        painter.setPen(pen)
        painter.drawEllipse(rect)
        pen.setColor(QColor(
            palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
            if state == "solar_annular" else palette.GLOW_ECLIPSE_SOLAR_COLOR
        ))
        painter.setPen(pen)
        painter.drawArc(rect, round(90.0 * 16), round(-covered * 360.0 * 16))
        painter.restore()
        return
    if style != "bite":
        raise ValueError(f"unknown solar eclipse style {style!r}")
    if state == "solar_total":
        # Totality is not a bright Sun at all: a black disc ringed by
        # corona. Nothing about a dimmed golden ball says that.
        painter.save()
        pen = QPen(QColor(palette.GLOW_SUN_COLOR))
        pen.setWidthF(max(1.0, radius * 0.08))
        painter.setPen(pen)
        for index in range(_CORONA_SPIKES):
            theta = index / _CORONA_SPIKES * 2 * math.pi
            reach = radius * (
                _CORONA_SPIKE_MIN
                + (_CORONA_SPIKE_MAX - _CORONA_SPIKE_MIN)
                * abs(math.sin(index * 2.1))
            )
            painter.drawLine(
                QPointF(math.cos(theta) * radius * 1.05,
                        math.sin(theta) * radius * 1.05),
                QPointF(math.cos(theta) * reach, math.sin(theta) * reach),
            )
        painter.setPen(QPen(QColor(color), max(1.0, radius * 0.10)))
        painter.setBrush(QColor(palette.ECLIPSE_OCCULTER_COLOR))
        painter.drawEllipse(QPointF(0.0, 0.0), radius, radius)
        painter.restore()
        return
    travel = (1.0 - covered) * _BITE_TRAVEL * radius
    occulter = radius * (_ANNULAR_SHRINK if state == "solar_annular" else 1.0)
    painter.save()
    disc = QPainterPath()
    disc.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
    painter.setClipPath(disc)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette.ECLIPSE_OCCULTER_COLOR))
    painter.drawEllipse(
        QPointF(travel, -travel * _BITE_RISE), occulter, occulter
    )
    painter.restore()
