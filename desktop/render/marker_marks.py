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

# The solar eclipse's own geometry. (The occulter-circle travel and
# the procedural corona spikes are RETIRED — owner correction
# 2026-08-11: the bite is the Moon algorithm's bright crescent over
# his own icon, which carries its rays itself.)
_ANNULAR_SHRINK = 0.86      # the ring of fire's inner edge, of the disc
_GAUGE_RADIUS = 1.18
_GAUGE_WIDTH_FRACTION = 0.14

# THE SIZE RATIO — the Moon's apparent diameter divided by the Sun's, per
# solar eclipse type (owner bug 2026-08-13: "kruznica delimicnog
# pomracenja je manja od kruznice sunca"). This is the number that
# DECIDES the type in nature: the two discs are within a few percent of
# each other at every solar eclipse, and which side of 1.0 the ratio
# falls on is exactly what makes an eclipse total, annular or hybrid.
# Typical reference values (Espenak/NASA eclipse catalogue ranges):
#   total   1.03-1.06  the Moon apparently LARGER — hence totality and
#                      the corona
#   hybrid  ~1.00      the knife edge, annular at the track's ends and
#                      total in its middle
#   annular 0.94-0.97  the Moon apparently SMALLER — hence the ring of
#                      fire, and the ONE type whose occulter is genuinely
#                      a smaller circle
#   partial ~1.00      a partial eclipse is a near-MISS in ALIGNMENT, not
#                      a small Moon. The occulter is the same apparent
#                      size; it simply does not pass centrally.
# Drawing a partial occulter small was the bug: it said "a small object
# crossed the Sun", and it gave the bite a tight little curvature instead
# of the Sun's own.
_SOLAR_SIZE_RATIO = {
    "solar_total": 1.05,
    "solar_hybrid": 1.00,
    "solar_annular": 0.95,
    "solar_partial": 1.00,
}
# (`_ANNULAR_SHRINK` above stays a deliberate LEGIBILITY exaggeration of
# the annular ratio: at a true 0.95 the ring of fire is two pixels wide
# on a dial mark and no one can see which type they are looking at. The
# ratio table is the physics; that constant is how thick the physics is
# drawn.)

# THE ECLIPSE REWORK (owner order 2026-08-13, "skoro sve slikamo isto
# ... zato i treba rework"). Three collapses died here; these are the
# numbers that replaced them.
#
# 1. THE CORONA — totality's own picture in the "bite" style. Before the
#    rework "bite" RETURNED EARLY at totality, so a total eclipse drew
#    the bare icon: byte-identical to "halo", which is how four
#    combinations came to render one single image.
_CORONA_REACH = 1.30        # of the body radius, the pearly ring's fade-out
_CORONA_PEAK = 1.06         # where it is brightest — just off the limb
_CORONA_ALPHA = 0.90
#
# 2. THE MAGNITUDE RING — the "halo" style's own reading of how much of
#    the Sun is gone. The style must leave the BODY alone (that is what
#    the owner picks it for), so the magnitude is written OUTSIDE the
#    disc: a soft ring that grows, thickens and brightens with the
#    covered fraction. Before the rework "halo" drew nothing at all and
#    a 62 % partial was the same picture as totality.
_HALO_RING_MIN = 0.98       # peak radius at covered 0
_HALO_RING_MAX = 1.20       # peak radius at covered 1
_HALO_RING_WIDTH_MIN = 0.05
_HALO_RING_WIDTH_MAX = 0.16
_HALO_RING_ALPHA_MIN = 0.35
_HALO_RING_ALPHA_MAX = 1.0
#
# 3. THE HYBRID SPLIT — a hybrid eclipse is total along part of its
#    ground track and annular along the rest, so it is drawn as BOTH AT
#    ONCE: half the mark carries the total picture, half the annular
#    one. One rule, applied in all three styles, so the reader learns it
#    once.
_HYBRID_SPLIT_DEG = 180.0
_HYBRID_INNER_RING = 0.78   # the hybrid halo's second ring, of the outer peak
_HYBRID_INNER_GAUGE = 0.84  # the hybrid gauge's annular lane, of the gauge

# THE WALL, checked at import (`tests/test_moving_bodies.py` also pins
# it, but a module that cannot even load is the louder failure): the
# outermost pixel any mark here can touch, against the limit above.
_OUTERMOST_MARK = max(
    1.0 + _MARK_GAP + _CORONA_LENGTH + _MARK_WIDTH_FRACTION / 2,
    _WEDGE_RADIUS + _WEDGE_WIDTH_FRACTION / 2,
    _GAUGE_RADIUS + _GAUGE_WIDTH_FRACTION / 2,
    _CORONA_REACH,
    _HALO_RING_MAX + _HALO_RING_WIDTH_MAX,
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
    tip_radius: float | None = None,
) -> None:
    """One of `constants.MARKER_POINTER_SHAPES` BEHIND the body (owner
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

    All three styles read the catalog MAGNITUDE, and all three tell the
    four solar TYPES apart — that is the whole point of the rework
    (owner order 2026-08-13): "bite" lays the geometry across the face
    (a bright crescent when partial, a ring of fire when annular, a
    black disc in a corona at totality, both at once for a hybrid);
    "magnitude_arc" reads the covered fraction off a ring gauge without
    touching the body; "halo" leaves the body completely alone and
    writes the same fraction as a soft ring OUTSIDE it, which is what
    makes it the quiet option rather than the empty one.

    Until this rework "halo" returned here without drawing anything, so
    it showed the same picture for a 62 % partial and for totality, and
    at totality "bite" returned too — leaving the two styles
    byte-identical.
    """
    covered = 1.0 if magnitude is None else max(0.0, min(1.0, magnitude))
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
        _magnitude_gauge(painter, radius, state, covered)
        return
    if style == "halo":
        _magnitude_ring(painter, radius, state, covered)
        return
    if style != "bite":
        raise ValueError(f"unknown solar eclipse style {style!r}")
    _bite(painter, radius, state, covered, color)


def _state_color(state: str) -> str:
    """The eclipse red every solar state wears, except the annular ring
    of fire's hotter orange — the ONE place that choice is made on this
    side of the render, so the gauge, the ring and the limb can never
    disagree about which type is which colour."""
    if state == "solar_annular":
        return palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
    return palette.GLOW_ECLIPSE_SOLAR_COLOR


def _magnitude_gauge(
    painter: QPainter, radius: float, state: str, covered: float,
) -> None:
    """The covered fraction as a ring gauge, the body untouched.

    A HYBRID reads as TWO LANES: the annular half of its track on an
    inner ring in the ring-of-fire orange, the total half on the outer
    ring in the eclipse red. A colour split alone was not enough — a
    hybrid and a total both fill their gauge completely, so with one
    lane the two gauges were the same picture in everything but hue,
    and the distinctness measure said so."""
    gauge = radius * _GAUGE_RADIUS
    pen = QPen()
    pen.setWidthF(radius * _GAUGE_WIDTH_FRACTION)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    span = covered * 360.0
    painter.save()
    painter.setBrush(Qt.BrushStyle.NoBrush)
    if state == "solar_hybrid":
        annular_span = min(span, _HYBRID_SPLIT_DEG)
        _gauge_lane(
            painter, pen, gauge * _HYBRID_INNER_GAUGE, 90.0, annular_span,
            palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR,
        )
        _gauge_lane(
            painter, pen, gauge, 90.0 - annular_span, span - annular_span,
            palette.GLOW_ECLIPSE_SOLAR_COLOR,
        )
    else:
        _gauge_lane(painter, pen, gauge, 90.0, span, _state_color(state))
    painter.restore()


def _gauge_lane(
    painter: QPainter, pen: QPen, gauge: float, start_deg: float,
    span_deg: float, color: str,
) -> None:
    """One lane of the magnitude gauge: the unfilled night ring, then
    the filled sweep over it. Qt's angles are CCW from 3 o'clock in
    1/16 degrees, and the sweep runs CLOCKWISE from the top like the
    dial itself."""
    rect = QRectF(-gauge, -gauge, 2 * gauge, 2 * gauge)
    pen.setColor(QColor(palette.NIGHT_WEDGE_GROUND))
    painter.setPen(pen)
    painter.drawEllipse(rect)
    pen.setColor(QColor(color))
    painter.setPen(pen)
    painter.drawArc(rect, round(start_deg * 16), round(-span_deg * 16))


def _magnitude_ring(
    painter: QPainter, radius: float, state: str, covered: float,
) -> None:
    """THE QUIET OPTION, but not a blind one: a soft ring outside the
    body whose radius, thickness and alpha all rise with the covered
    fraction, so a 62 % partial reads visibly smaller and fainter than
    totality without a single pixel of the body being touched. A HYBRID
    wears TWO rings — the same both-at-once rule the other two styles
    apply, one limb for each of the eclipse's two halves.

    THE RING IS PEARL, NOT THE TYPE'S OWN COLOUR. The first cut drew it
    in the eclipse red, and it vanished: the caller's halo is already a
    red gradient out to 1.5 body radii, so a red ring inside it was a
    red mark on red ground and the style stayed magnitude-blind after
    the "fix". Pearl is the light that survives an eclipse and it reads
    over the red halo, the annular orange one and the lunar bronze
    alike; the TYPE is still carried by the halo's own colour under it.
    """
    peak = _HALO_RING_MIN + covered * (_HALO_RING_MAX - _HALO_RING_MIN)
    width = _HALO_RING_WIDTH_MIN + covered * (
        _HALO_RING_WIDTH_MAX - _HALO_RING_WIDTH_MIN
    )
    alpha = _HALO_RING_ALPHA_MIN + covered * (
        _HALO_RING_ALPHA_MAX - _HALO_RING_ALPHA_MIN
    )
    _soft_ring(
        painter, radius, peak, width, alpha, palette.ECLIPSE_CORONA_COLOR,
    )
    if state == "solar_hybrid":
        _soft_ring(
            painter, radius, peak * _HYBRID_INNER_RING, width, alpha,
            palette.ECLIPSE_CORONA_COLOR,
        )
    elif state == "solar_annular":
        # The ring of fire is what an annular eclipse IS, and the halo
        # style is the one that never touches the body — so the annular
        # rim is written at the body's own edge as a hairline of the
        # same orange, which the pearl ring above cannot be confused
        # with and which a total eclipse never gets.
        _soft_ring(
            painter, radius, 1.0, _HALO_RING_WIDTH_MIN, alpha,
            palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR,
        )


def _soft_ring(
    painter: QPainter, radius: float, peak: float, width: float,
    alpha: float, color: str,
) -> None:
    """One gradient ring centred on the body: transparent at the body's
    own edge, `color` at `peak`, transparent again by `peak + width` —
    a band of light, never a drawn stroke, so it belongs to the same
    visual family as `render.eclipse_glow`'s halo."""
    outer = radius * (peak + width)
    gradient = QRadialGradient(QPointF(0.0, 0.0), outer)
    clear = QColor(color)
    clear.setAlphaF(0.0)
    lit = QColor(color)
    lit.setAlphaF(alpha)
    gradient.setColorAt(0.0, clear)
    gradient.setColorAt(max(0.0, (peak - width) / (peak + width)), clear)
    gradient.setColorAt(peak / (peak + width), lit)
    gradient.setColorAt(1.0, clear)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawEllipse(QPointF(0.0, 0.0), outer, outer)
    painter.restore()


def _bite(
    painter: QPainter, radius: float, state: str, covered: float, color: str,
) -> None:
    # THE BITE IS DRAWN AS IT IS SEEN (owner correction 2026-08-11,
    # slika 4: a black occulting circle over the already-black eclipse
    # art was invisible — "ne moze crni isecak na crnoj eklipsi... vec
    # znamo kako se pokazuje, crta isjecak na mjesecu imamo algoritam"):
    # the VISIBLE remainder of the Sun is painted BRIGHT over the dark
    # art, rather than a dark occulter being painted over dark art. Its
    # shape is the true two-disc difference (`solar_occulter_geometry`,
    # owner bug 2026-08-13) — the earlier lunar-phase construction is
    # retired, because a phase terminator is an ellipse that narrows
    # with the magnitude and the Moon's apparent size does not. The base
    # art under this is the owner's own eclipse icon (a black disc in
    # rays), so:
    #  - annular paints the ring of fire around the black disc;
    #  - a partial phase paints the bright visible crescent over it;
    #  - totality paints the CORONA around the silhouette (the rework:
    #    it used to paint nothing, which made it "halo" twice);
    #  - a hybrid paints the corona AND a ring of fire along half the
    #    limb — total on one side of its track, annular on the other.
    painter.save()
    if state == "solar_annular":
        _ring_of_fire(painter, radius, 0.0, 360.0)
    elif covered >= 1.0 and state in ("solar_total", "solar_hybrid"):
        _corona(painter, radius)
        if state == "solar_hybrid":
            _ring_of_fire(painter, radius, 90.0, _HYBRID_SPLIT_DEG)
    else:
        # TWO DISCS OF NEAR-EQUAL RADIUS, OFFSET (owner bug 2026-08-13).
        # What is left of the Sun is the Sun's disc MINUS the occulter's,
        # and nothing else — so the bite's curved edge carries the
        # occulter's true curvature, which at a partial eclipse is the
        # Sun's own. The old construction asked `moon_lit_region` for a
        # lunar PHASE of the matching area instead, and a phase's
        # terminator is a half-ellipse of semi-axis r*|cos 2*pi*f|: at
        # magnitude 0.62 that collapsed to 0.24 r, drawing an occulter a
        # quarter of the Sun's size. Area alone was never the claim.
        occulter, distance = solar_occulter_geometry(state, radius, covered)
        sun = _disc(radius, 0.0)
        moon = _disc(occulter, distance)
        painter.setPen(Qt.PenStyle.NoPen)
        # The COVERED lune first, in the same silhouette colour totality
        # wears (`_corona`), clipped to the Sun so it can never claim
        # ground outside the body. Without it the Sun's disc ends at the
        # bite and the halo shows through, which reads as a SMALLER Sun —
        # the very impression the fix is here to remove. It is not the
        # black-on-black the owner rejected in 2026-08-11: that was a
        # dark occulter over the dark icon with nothing bright beside
        # it; here the bright remainder draws the limb around it.
        painter.setBrush(QColor(palette.ECLIPSE_OCCULTER_COLOR))
        painter.drawPath(sun.intersected(moon))
        painter.setBrush(QColor(color))
        painter.drawPath(sun.subtracted(moon))
    painter.restore()


def solar_occulter_geometry(
    state: str, radius: float, covered: float,
) -> tuple[float, float]:
    """(occulter radius, centre distance) for a solar eclipse of `state`
    covering `covered` of the Sun's DIAMETER, over a Sun of `radius`.

    The same reasoning `render.moon_face.draw_umbra_sweep` uses on the
    lunar side, and deliberately the same shape of formula so the two
    can be read against each other: magnitude is a fraction of the
    ECLIPSED body's diameter, so with the eclipsed body at radius R and
    the occulter at r,

        d = R + r - 2 * R * magnitude

    — magnitude 0 lands exactly on tangency (d = R + r, no bite at all)
    and total coverage lands on d = 0, the two discs concentric. The
    lunar side writes `2 * r` there because THERE the moon is the body
    being eclipsed; here the Sun is, so it is `2 * R`. The occulter's
    own radius comes from `_SOLAR_SIZE_RATIO`, never from the magnitude:
    coverage is a matter of ALIGNMENT, and shrinking the disc to fake it
    is the bug this function exists to make impossible.
    """
    occulter = radius * _SOLAR_SIZE_RATIO[state]
    distance = max(0.0, radius + occulter - 2.0 * radius * covered)
    return occulter, distance


def _disc(radius: float, offset_x: float) -> QPainterPath:
    path = QPainterPath()
    path.addEllipse(
        QRectF(offset_x - radius, -radius, 2 * radius, 2 * radius)
    )
    return path


def _ring_of_fire(
    painter: QPainter, radius: float, start_deg: float, span_deg: float,
) -> None:
    """The uncovered rim of an annular eclipse, over `span_deg` of the
    limb (the whole circle for a true annular, half of it for a
    hybrid). Qt's angles are CCW from 3 o'clock in 1/16 degrees."""
    ring = QPen(QColor(palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR))
    ring.setWidthF(max(1.0, radius * (1.0 - _ANNULAR_SHRINK)))
    edge_r = radius * (1.0 + _ANNULAR_SHRINK) / 2.0
    rect = QRectF(-edge_r, -edge_r, 2 * edge_r, 2 * edge_r)
    painter.save()
    painter.setPen(ring)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    if span_deg >= 360.0:
        painter.drawEllipse(QPointF(0.0, 0.0), edge_r, edge_r)
    else:
        painter.drawArc(rect, round(start_deg * 16), round(span_deg * 16))
    painter.restore()


def _corona(painter: QPainter, radius: float) -> None:
    """TOTALITY'S OWN PICTURE: the Moon's silhouette laid over the icon
    and the pearly corona around it — the one thing a person actually
    sees during totality, and the only reason to pick "bite" for a
    total eclipse at all."""
    _soft_ring(
        painter, radius, _CORONA_PEAK, _CORONA_REACH - _CORONA_PEAK,
        _CORONA_ALPHA, palette.ECLIPSE_CORONA_COLOR,
    )
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette.ECLIPSE_OCCULTER_COLOR))
    painter.drawEllipse(QPointF(0.0, 0.0), radius, radius)
    painter.restore()
