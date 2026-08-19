"""THE SOLAR ECLIPSE's own geometry — every picture the Sun side of an
eclipse can draw, in one place.

It was born out of `render.marker_marks` on 2026-08-13, when the
owner's three ballot-accepted styles (`totality_path`, `type_emblem`,
`dial_shadow`) were painted and that module crossed THE STRUCTURE LAW's
threshold. The split is by RESPONSIBILITY, not by size: `marker_marks`
draws what belongs to a BODY ON ITS ORBIT — the position pointer and
the four life stations, marks the Earth and the Moon wear on ordinary
days — while everything here belongs to the eclipse, the third body
that only exists on the day of an event.

THE SIX SOLAR PICTURES, and the ONE rule they share: every one of them
tells the four catalog TYPES apart, and none of them may draw the same
picture as another (owner order 2026-08-13, "skoro sve slikamo isto ...
zato i treba rework" — lang-ok: the owner's own sentence, quoted so the
requirement cannot be re-derived wrongly; the tooth is
`tests/test_eclipse_distinctness.py`).

  bite           the owner's two body plates composited — the geometry
                 itself, across the face
  magnitude_arc  the covered fraction as a ring gauge, body untouched
  halo           the same fraction written OUTSIDE the body as light
  totality_path  how near THIS OBSERVER stands to the eclipse — the one
                 style that depends on where the watch is
  type_emblem    a small badge of the TYPE on the body's lower limb
  dial_shadow    the one style that takes light away instead of adding
                 it; never the default, by the owner's explicit order

`render.eclipse_style.resolve_eclipse_style` stays THE DOOR every call
site asks before it paints — a style that cannot draw itself in some
context says so rather than silently becoming another one.

Layer: render. Documentation: __about/solar_eclipse.md.
"""

import math
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QRadialGradient

from config import defaults, glow, palette
from render.assets import shared_cache

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
# 1. THE CORONA — retired 2026-08-13 by the owner's own decision. The
#    rework's procedural corona was totality's picture for one day; he
#    then drew his two body plates and ruled that totality is his Sun
#    plate with the yellow disc completely covered, rays alone
#    remaining. See `_bite`.
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
# The hybrid BITE's ghost ring (see `_ghost_ring`): its WIDTH is
# measured off the owner's Moon plate; only its strength is a choice,
# and the choice is narrower than it looks. The ring is the ONE thing
# separating a hybrid from a total eclipse now that both cover the disc,
# so it must clear `tests/test_eclipse_distinctness.py`'s structure
# floor — measured: 0.171 at alpha 0.55 (BELOW the 0.20 floor, i.e. the
# same picture), 0.221 at 0.70, 0.291 at 0.90. It stays a TRACE all the
# same: a fifth the width of the annular ring of fire and in the hotter
# orange rather than the Sun's own yellow, which is what
# `test_the_hybrid_ghost_ring_is_a_trace_not_the_annular_ring` measures.
_HYBRID_GHOST_ALPHA = 0.90

# ══════════════════════════════════════════════════════════════════
# THE BALLOT'S THREE SOLAR STYLES (owner ballot 2026-08-13), painted
# ══════════════════════════════════════════════════════════════════
#
# 4. THE TOTALITY PATH — "a thin arc beside the body whose LENGTH and
#    BRIGHTNESS say how near the observer is to the path of totality:
#    full and bright means standing IN the band of totality, short and
#    dim means it is happening but 3,500 km away".
#
#    WHAT THE DATA ACTUALLY KNOWS, and what it does not (this is an
#    astronomical instrument — a mark may not claim more than its
#    source supports):
#      * `core.clock_state.EclipseEvent.distance_km` is REAL and it is
#        the honest quantity here: the observer's haversine great-circle
#        distance to the catalog's GREATEST-ECLIPSE ground point,
#        stamped by `_with_visibility` from the Deep Time pack's
#        `solar_eclipses.lat/lon`.
#      * It is NOT the distance to the nearest point of the central
#        PATH. The catalog stores one point per eclipse, not the track,
#        so an observer standing squarely ON the path but 2,000 km
#        along it from greatest eclipse reads 2,000 km here. The mark
#        therefore UNDER-reads for such an observer, never over-reads —
#        the safe direction for an instrument.
#      * Local magnitude/obscuration for THIS observer does not exist
#        anywhere in the program. The catalog magnitude is the
#        eclipse's greatest magnitude somewhere on Earth, so it cannot
#        stand in for a local reading; it is used only where no ground
#        point exists at all, and then the arc is drawn DASHED to say
#        out loud that it is an estimate rather than a measurement.
#      * Lunar rows and solar rows whose finder reported no surface
#        point carry `distance_km is None` — the dashed case above.
#
#    The scale is `glow.ECLIPSE_SOLAR_VISIBILITY_KM` (3,500 km),
#    the SAME number the visibility flag and the hover reason already
#    use — the owner's own "3,500 km away" is that constant, so the arc
#    empties exactly where the app already says the eclipse cannot be
#    seen from here, and cannot drift from it.
_TOTALITY_ARC_RADIUS = 1.30      # clear of the 1.18 magnitude gauge lane
_TOTALITY_ARC_WIDTH = 0.13
_TOTALITY_PARTIAL_WIDTH = 0.55   # of the width above — see `_totality_path`
_TOTALITY_ARC_ALPHA_MIN = 0.28
_TOTALITY_ARC_ALPHA_MAX = 1.0
_TOTALITY_ARC_MIN_SPAN_DEG = 6.0  # so "nowhere near" is still a visible tick
_TOTALITY_HYBRID_INNER = 0.83    # the hybrid's second lane, of the radius
_TOTALITY_ESTIMATE_DASH = (3.0, 3.0)   # in pen widths — the "not measured" say
#
# 5. THE TYPE EMBLEM — "a small emblem beside the body: a ring for
#    annular, a double ring for hybrid" (his two; the other two are
#    decided here and justified).
#    ANNULAR  one ring          — the ring of fire, his own word.
#    HYBRID   two rings         — his own word: annular AND total.
#    TOTAL    a filled disc     — the one type where nothing of the Sun
#                                 is left; the ring's centre closes.
#    PARTIAL  a bitten disc     — a filled disc with a disc-sized bite
#                                 out of one side, the same geometry
#                                 `_bite` draws large, drawn small. It
#                                 is the type where the Sun is never
#                                 centrally covered, so the emblem is
#                                 never symmetric.
#    One grammar, learned once: how much of the emblem's centre is open
#    says how much of the Sun survives.
#    THE SEAT is the body's lower limb in the mark's OWN frame (this
#    module's frame is translated to the body but never rotated, so
#    every other mark here is radially symmetric and no direction was
#    ever claimed). Centred ON the limb rather than outside it because
#    the window margin wall (`glow.MARK_REACH_LIMIT`) leaves no room for a
#    legible badge past 1.38 body radii — measured: a badge at the
#    smallest radius the 8x8 distinctness block can still read is 0.30
#    body radii, and 1.00 + 0.30 = 1.30 is the outermost seat that fits.
_EMBLEM_SEAT = 0.92
_EMBLEM_RADIUS = 0.45
_EMBLEM_RING_WIDTH = 0.30        # of the emblem radius
_EMBLEM_INNER_RING = 0.55        # the hybrid's second ring, of the emblem
_EMBLEM_BITE_OFFSET = 0.85       # the partial bite's centre, of the emblem
_EMBLEM_BACKING_ALPHA = 0.80     # the night disc the emblem is stamped on
#
# 6. THE DIAL SHADOW — "for the minutes the eclipse lasts, the WHOLE
#    ring loses light". OFF by default and never a default (his
#    explicit order; `tests/test_eclipse_style_completion.py` pins it).
#
#    WHAT THIS MARK CAN REACH: a mark is painted in the eclipse BODY's
#    own frame, inside the transparent window margin the widget
#    reserves (`glow.MARK_REACH_LIMIT`). So the shadow drawn here is the
#    eclipse's own darkness falling AROUND its body — deepest on the
#    body, fading to nothing by the wall. Dimming the ring band, the
#    numerals and the jewels as well needs a veil composited ABOVE
#    those layers, which lives in `render/compositor.py` and
#    `render/layers/ring.py` — neither of them this round's to touch.
#    See `__about/marker_marks.md` for exactly what that would take.
_SHADOW_REACH_MIN = 1.05         # at covered 0
_SHADOW_REACH_MAX = 1.36         # at covered 1 — inside the 1.38 wall
_SHADOW_ALPHA_MIN = 0.25
_SHADOW_ALPHA_MAX = 0.80
_SHADOW_RIM_WIDTH = 0.06         # the annular/hybrid rim, of the body radius
_SHADOW_RIM_ALPHA = 0.95
_SHADOW_HYBRID_INNER = 0.78      # the hybrid's second rim, of the reach

# ══════════════════════════════════════════════════════════════════
# THE TWO BODY PLATES — MEASURED, NEVER GUESSED
# ══════════════════════════════════════════════════════════════════
# The owner drew `defaults.ECLIPSE_BODY_SUN_ART` and
# `ECLIPSE_BODY_MOON_ART` and the composition has to know where each
# picture's DISC ends, because his one composition rule is stated in
# terms of it: the dark disc covers the Sun's yellow disc and NEVER its
# rays. So the four numbers below were measured off the files rather
# than eyeballed — 1,440 samples per radius ring, as a fraction of the
# image half-size, `tests/test_eclipse_plates.py` re-measures them:
#
#   eclipse_body_sun.png  (576x576)
#     0.623  the last ring that is solid yellow all the way round —
#            the DISC's edge; past it the ink breaks into spokes
#     0.889  the outermost ring carrying any ink at all — the ray tips
#   eclipse_body_moon.png (360x360)
#     0.925  the last ring of pure black — the Moon's own limb
#     1.000  his rim glow reaches the frame edge and is cut there,
#            which is why the plate is drawn to its full square
_SUN_PLATE_DISC_FRACTION = 0.623
_SUN_PLATE_RAY_FRACTION = 0.889
_MOON_PLATE_DISC_FRACTION = 0.925
_MOON_PLATE_GLOW_FRACTION = 1.000

# THE SHINE IS NOT A MARK (owner verdict 2026-08-16, asked directly and
# answered "shine SME slobodno preko svega" — the shine may go freely
# over everything). His rule for the eclipsed Sun is two-part and the
# two parts obey different laws:
#
#   the DISC  — exactly the body radius, the same roundel every other
#               weekday body is drawn at. That is `_SUN_PLATE_DISC_
#               FRACTION` normalizing the plate, unchanged.
#   the SHINE — EXTRA, over and beyond that measure, over neighbouring
#               sectors and the hands alike. Not clipped, not shrunk.
#
# So this reaches the plate's own 0.889/0.623 = 1.427 body radii. It
# used to be `min(...)`-ed down to `glow.MARK_REACH_LIMIT` (1.38), which
# bit the outer 3 % of the ray tips off. That limit is `GLOW_RADIUS_
# SCALE * 0.92`, and the 0.92 is HEADROOM held back for marks that are
# OPAQUE STROKES — a gauge arc or a halo ring touching the window edge
# shows as a hard cut line. These ray tips are the opposite case: faded
# spokes at under half alpha over ~13 % of the limb, with no continuous
# ink that could form an edge. The window itself reserves the full
# `GLOW_RADIUS_SCALE` (1.5), so 1.427 stands INSIDE the transparent
# margin — the shine is freed from our own headroom, never from the
# window, and THE SPACE & LEGIBILITY LAW is untouched.
_SUN_PLATE_REACH = _SUN_PLATE_RAY_FRACTION / _SUN_PLATE_DISC_FRACTION


# THE WALL, checked at import (`tests/test_moving_bodies.py` also pins
# it, but a module that cannot even load is the louder failure): the
# outermost pixel any eclipse mark can touch, against
# `glow.MARK_REACH_LIMIT` — the ONE wall both mark modules read.
# The Sun plate's SHINE is deliberately not in this list — see
# `_SUN_PLATE_REACH`: the headroom below is held back for opaque strokes
# that would cut a hard line at the window edge, which faded ray tips
# cannot do. It answers to the window's own reserve instead, asserted
# separately underneath.
_OUTERMOST_MARK = max(
    _GAUGE_RADIUS + _GAUGE_WIDTH_FRACTION / 2,
    _HALO_RING_MAX + _HALO_RING_WIDTH_MAX,
    _TOTALITY_ARC_RADIUS + _TOTALITY_ARC_WIDTH / 2,
    _EMBLEM_SEAT + _EMBLEM_RADIUS,
    _SHADOW_REACH_MAX,
)
assert _OUTERMOST_MARK <= glow.MARK_REACH_LIMIT, (
    f"a solar eclipse mark reaches {_OUTERMOST_MARK:.3f} of the body radius, "
    f"past the {glow.MARK_REACH_LIMIT:.3f} the window margin reserves — it "
    "would be clipped by the transparent window edge (THE SPACE & "
    "LEGIBILITY LAW)"
)
assert _SUN_PLATE_REACH <= glow.GLOW_RADIUS_SCALE, (
    f"the eclipsed Sun's shine reaches {_SUN_PLATE_REACH:.3f} of the body "
    f"radius, past the {glow.GLOW_RADIUS_SCALE:.3f} the transparent window "
    "margin itself reserves (`defaults.dial_window_margin_fraction`) — the "
    "shine may cross sectors and hands freely (owner 2026-08-16), but not "
    "the window edge (THE SPACE & LEGIBILITY LAW)"
)



def draw_solar_eclipse(
    painter: QPainter, style: str, radius: float, state: str,
    magnitude: float | None, color: str, origin: QPointF | None = None,
    distance_km: float | None = None,
) -> None:
    """The Sun-side eclipse in one of `umbra.ECLIPSE_SOLAR_STYLES`,
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

    Owner ballot 2026-08-13 accepted three more solar styles, painted
    the same day the plumbing landed: "totality_path" reads the
    observer's own distance to the eclipse (the ONLY style here that
    depends on WHERE the watch stands — hence `distance_km`),
    "type_emblem" stamps a small badge of the type on the body's limb,
    and "dial_shadow" takes light away instead of adding it.
    `render.eclipse_style.resolve_eclipse_style` remains THE DOOR every
    call site asks first, so a style that cannot draw itself in a given
    context still says so rather than silently becoming the default.

    `distance_km` is the observer's great-circle distance to the
    catalog's greatest-eclipse ground point
    (`core.clock_state.EclipseEvent.distance_km`), or None when there is
    no observer in hand (the Encyclopedia plates, the picker thumbnails)
    or no catalog ground point. Only "totality_path" reads it, and it
    says out loud — with a dashed arc — when it had to estimate; see the
    long note beside `_TOTALITY_ARC_RADIUS`.
    """
    from render.eclipse_style import resolve_eclipse_style

    covered = 1.0 if magnitude is None else max(0.0, min(1.0, magnitude))
    effective_style, _fallback_reason = resolve_eclipse_style("solar", style)
    painter.save()
    if origin is not None:
        painter.translate(origin)
    try:
        _solar_eclipse_body(
            painter, effective_style, radius, state, covered, color,
            distance_km,
        )
    finally:
        painter.restore()


def _solar_eclipse_body(
    painter: QPainter, style: str, radius: float, state: str,
    covered: float, color: str, distance_km: float | None = None,
) -> None:
    # `color` is the caller's own Sun gold. Nothing reads it any more:
    # since the owner's two body plates arrived (2026-08-13) the bite
    # carries its own colour and the other two styles never touched the
    # body. The parameter stays because `draw_solar_eclipse` is called
    # positionally from the year-marker layer and from the thumbs.
    del color
    if style == "magnitude_arc":
        _magnitude_gauge(painter, radius, state, covered)
        return
    if style == "halo":
        _magnitude_ring(painter, radius, state, covered)
        return
    if style == "totality_path":
        _totality_path(painter, radius, state, covered, distance_km)
        return
    if style == "type_emblem":
        _type_emblem(painter, radius, state)
        return
    if style == "dial_shadow":
        _dial_shadow(painter, radius, state, covered)
        return
    if style != "bite":
        raise ValueError(f"unknown solar eclipse style {style!r}")
    _bite(painter, radius, state, covered)


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


def totality_path_reach(
    covered: float, distance_km: float | None,
) -> tuple[float, bool]:
    """(0..1 nearness, measured) for the "totality_path" style — module
    level and pure so the dial, the plates and the teeth read the SAME
    number instead of each pinning its own arithmetic.

    MEASURED (`distance_km` in hand): the observer's great-circle
    distance to the catalog's greatest-eclipse ground point, mapped
    linearly onto `glow.ECLIPSE_SOLAR_VISIBILITY_KM` — 1.0 standing
    on the point, 0.0 at or past the 3,500 km the app already calls
    "cannot be seen from here". Read the honesty note beside
    `_TOTALITY_ARC_RADIUS` before changing this: it is a distance to ONE
    point, not to the central path, so it under-reads for an observer
    who stands on the path far along it. Under-reading is the safe
    direction; over-reading would be a lie.

    ESTIMATED (no ground point, or no observer at all — the Encyclopedia
    plates and the picker tiles): the catalog magnitude, which is the
    eclipse's GREATEST magnitude somewhere on Earth and therefore says
    what is on offer rather than what this observer gets. The caller
    draws that case dashed."""
    if distance_km is None:
        return max(0.0, min(1.0, covered)), False
    span = glow.ECLIPSE_SOLAR_VISIBILITY_KM
    return max(0.0, min(1.0, 1.0 - distance_km / span)), True


def _totality_path(
    painter: QPainter, radius: float, state: str, covered: float,
    distance_km: float | None,
) -> None:
    """THE BAND OF TOTALITY, as an arc the observer can read at a
    glance: LENGTH and BRIGHTNESS both rise with nearness, exactly as
    the owner asked (2026-08-13).

    It is centred on the TOP of the mark and grows symmetrically, which
    is deliberately NOT the "magnitude_arc" gauge's clockwise sweep from
    the top: the two styles must never be mistaken for each other, and
    they sit on different lanes as well (1.30 body radii here against
    that gauge's 1.18).

    The type is carried the way every other style in this module carries
    it — a HYBRID wears two lanes (annular along part of its track,
    total along the rest), an ANNULAR wears the ring-of-fire orange, and
    a PARTIAL wears a THINNER arc because a partial eclipse has no band
    of totality anywhere on Earth: there is a nearest point of greatest
    eclipse to stand near, but nothing to stand inside, and the mark
    must not promise one."""
    reach, measured = totality_path_reach(covered, distance_km)
    span = max(_TOTALITY_ARC_MIN_SPAN_DEG, reach * 360.0)
    alpha = _TOTALITY_ARC_ALPHA_MIN + reach * (
        _TOTALITY_ARC_ALPHA_MAX - _TOTALITY_ARC_ALPHA_MIN
    )
    width = radius * _TOTALITY_ARC_WIDTH
    if state == "solar_partial":
        width *= _TOTALITY_PARTIAL_WIDTH
    painter.save()
    painter.setBrush(Qt.BrushStyle.NoBrush)
    lane = radius * _TOTALITY_ARC_RADIUS
    if state == "solar_hybrid":
        # THE HYBRID SPLITS ITS ARC, the both-at-once rule this module
        # applies everywhere: the eclipse is total along part of its
        # track and annular along the rest, so it gets HALF the arc in
        # the eclipse red at the top and half in the ring-of-fire orange
        # on the inner lane at the bottom. Two half-arcs on two lanes
        # can never be mistaken for a total eclipse's single full one —
        # a second concentric lane in a different hue could be, and was
        # (measured: structure 0.098 against `solar_total_totality_path`,
        # well under the 0.20 floor; 0.36 after the split).
        _totality_lane(
            painter, lane, width, span / 2.0, 90.0, alpha,
            palette.ECLIPSE_CORONA_COLOR, measured,
        )
        _totality_lane(
            painter, lane * _TOTALITY_HYBRID_INNER, width, span / 2.0,
            270.0, alpha, palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR, measured,
        )
    else:
        _totality_lane(
            painter, lane, width, span, 90.0, alpha,
            _totality_light(state), measured,
        )
    painter.restore()


def _totality_light(state: str) -> str:
    """THE COLOUR OF THE LIGHT WAITING AT THE CENTRE LINE — what an
    observer who reached the path would actually see there, which is the
    one thing this arc is about.

    TOTAL   the corona's pearl: it is visible ONLY from inside the band
            of totality, so it is exactly what standing in the band buys.
    ANNULAR the ring of fire's orange, for the same reason — that is
            what the centre line offers there, and there is no corona.
    PARTIAL the plain eclipse red: a partial eclipse has no central
            light to travel toward at all.
    HYBRID  both, one per lane (see `_totality_path`).

    It is deliberately NOT `_state_color`, which the gauge and the limb
    use. Measured on the distinctness thumbnails: at totality the arc
    and the "magnitude_arc" gauge are both a full ring, and at 64 px the
    1.18 and 1.30 lanes land in the SAME 8x8 block — so radius could
    never separate them (structure 0.194 and 0.180 at two different
    widths, both under the 0.20 floor) and only a genuine hue change
    could. Pearl against red scores 0.055 on the colour axis, comfortably
    over its 0.035 floor, and it means something rather than being a
    colour picked to pass a test."""
    if state == "solar_annular":
        return palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
    if state == "solar_partial":
        return palette.GLOW_ECLIPSE_SOLAR_COLOR
    return palette.ECLIPSE_CORONA_COLOR


def _totality_lane(
    painter: QPainter, lane: float, width: float, span_deg: float,
    centre_deg: float, alpha: float, color: str, measured: bool,
) -> None:
    """One lane of the totality arc, centred on the top of the mark.

    A lane drawn from an ESTIMATE is DASHED — the honesty requirement of
    the owner's own ballot item, made visible instead of only written
    down: a solid arc is a measured distance to a real ground point, a
    dashed one is the catalog magnitude standing in for one."""
    colour = QColor(color)
    colour.setAlphaF(alpha)
    pen = QPen(colour)
    pen.setWidthF(max(1.0, width))
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    if not measured:
        pen.setDashPattern(list(_TOTALITY_ESTIMATE_DASH))
    painter.setPen(pen)
    rect = QRectF(-lane, -lane, 2 * lane, 2 * lane)
    # Qt's angles are CCW from 3 o'clock in 1/16 degrees; `centre_deg`
    # is the middle of the arc (90 = the top of the mark) and it opens
    # the same amount to either side of it.
    painter.drawArc(
        rect, round((centre_deg + span_deg / 2.0) * 16), round(-span_deg * 16)
    )


def _type_emblem(painter: QPainter, radius: float, state: str) -> None:
    """THE TYPE'S OWN BADGE on the body's lower limb — one ring for
    annular and two for hybrid (the owner's own two), a filled disc for
    total and a bitten disc for partial (decided here, reasoned beside
    `_EMBLEM_SEAT`).

    It is stamped on a night backing disc rather than straight onto the
    Sun art, for the same reason `_magnitude_ring` is pearl and not red:
    a mark that only reads against one background is a mark that
    silently disappears on the others."""
    centre = QPointF(0.0, radius * _EMBLEM_SEAT)
    size = radius * _EMBLEM_RADIUS
    colour = QColor(_state_color(state))
    backing = QColor(palette.NIGHT_WEDGE_GROUND)
    backing.setAlphaF(_EMBLEM_BACKING_ALPHA)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(backing)
    painter.drawEllipse(centre, size, size)
    if state == "solar_total":
        # Nothing of the Sun is left — the emblem's centre closes.
        painter.setBrush(colour)
        painter.drawEllipse(centre, size, size)
    elif state == "solar_partial":
        # The one type that is never central: a disc with an offset
        # disc-sized bite out of it, `_bite`'s geometry in miniature.
        disc = QPainterPath()
        disc.addEllipse(centre, size, size)
        bite = QPainterPath()
        bite.addEllipse(
            QPointF(centre.x() + size * _EMBLEM_BITE_OFFSET, centre.y()),
            size, size,
        )
        painter.setBrush(colour)
        painter.drawPath(disc.subtracted(bite))
    else:
        # ANNULAR one ring, HYBRID the same ring plus a second inside it.
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(colour)
        pen.setWidthF(max(1.0, size * _EMBLEM_RING_WIDTH))
        painter.setPen(pen)
        inset = size * (1.0 - _EMBLEM_RING_WIDTH) / 2.0
        painter.drawEllipse(centre, size - inset, size - inset)
        if state == "solar_hybrid":
            second = (size - inset) * _EMBLEM_INNER_RING
            painter.drawEllipse(centre, second, second)
    painter.restore()


def _dial_shadow(
    painter: QPainter, radius: float, state: str, covered: float,
) -> None:
    """THE SHADOW ON THE FACE — the one style that takes light away
    instead of adding it (owner ballot 2026-08-13; never the default,
    by his explicit order).

    Its REACH and its DEPTH both rise with the covered fraction, so a
    62 % partial is a soft local dimming and totality is a black well
    out to the window margin. Both had to move: depth alone is a global
    brightness change, and a global brightness change is precisely what
    `tests/test_eclipse_distinctness.py` is blind to on purpose — the
    owner's own condemned pair was two pictures that differed by nothing
    else.

    HOW FAR THIS REACHES, honestly: a mark is painted in the eclipse
    body's own frame, so the darkness here falls on the dial AROUND the
    body and fades out by `glow.MARK_REACH_LIMIT`. Taking the light off the
    whole ring band, the numerals and the jewels needs a veil composited
    above those layers — `render/compositor.py` and
    `render/layers/ring.py`, neither of them this round's to touch; see
    `__about/marker_marks.md`."""
    reach = radius * (
        _SHADOW_REACH_MIN + covered * (_SHADOW_REACH_MAX - _SHADOW_REACH_MIN)
    )
    alpha = _SHADOW_ALPHA_MIN + covered * (
        _SHADOW_ALPHA_MAX - _SHADOW_ALPHA_MIN
    )
    gradient = QRadialGradient(QPointF(0.0, 0.0), reach)
    core = QColor(palette.MOON_SHADOW_BLACK)
    core.setAlphaF(alpha)
    edge = QColor(palette.MOON_SHADOW_BLACK)
    edge.setAlphaF(0.0)
    gradient.setColorAt(0.0, core)
    gradient.setColorAt(0.72, core)
    gradient.setColorAt(1.0, edge)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawEllipse(QPointF(0.0, 0.0), reach, reach)
    # THE LIGHT THAT SURVIVES: the same both-at-once rule the other
    # styles apply. An annular eclipse never goes fully dark — its ring
    # of fire is written as a rim at the shadow's own edge — and a
    # hybrid, annular along part of its track, wears that rim twice.
    if state in ("solar_annular", "solar_hybrid"):
        rim = QColor(palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR)
        rim.setAlphaF(_SHADOW_RIM_ALPHA)
        pen = QPen(rim)
        pen.setWidthF(max(1.0, radius * _SHADOW_RIM_WIDTH))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0.0, 0.0), reach, reach)
        if state == "solar_hybrid":
            inner = reach * _SHADOW_HYBRID_INNER
            painter.drawEllipse(QPointF(0.0, 0.0), inner, inner)
    painter.restore()


def _bite(painter: QPainter, radius: float, state: str, covered: float) -> None:
    """THE BITE IS THE OWNER'S OWN TWO BODIES, COMPOSITED (his art and
    his rule, 2026-08-13) — ONE composition for all four solar types,
    and the type is carried entirely by how big the dark disc is and
    how far off centre it sits.

    His rule, and it is uniform:
    lang-ok: the owner's own specification of the composition, quoted
    verbatim so it cannot be re-derived wrongly.
    *"u totalnoj eklipsi ces prekriti cijeli onaj disk a ostavit ces
    samo zrake da se vide; u svim onim drugim crni ces smanjiti koliko
    je vec smanjen i ostaviti dakle pored zraka i deo suncevog diska"* —
    at totality the dark disc covers the whole yellow disc and only the
    rays remain; at every other type it is smaller (or offset), so part
    of the yellow disc survives beside the rays.

    Which is exactly `solar_occulter_geometry`, already: the SIZE RATIO
    decides how big the Moon is and the magnitude carries the coverage
    as an OFFSET. So there is nothing procedural left in this style —
    no drawn crescent, no drawn ring of fire, no procedural corona. The
    corona spikes and the `_corona`/`_ring_of_fire` pair that replaced
    them are both retired: the owner was shown that his yellow rays are
    not what a real corona looks like and answered
    lang-ok: his verdict on the corona question, quoted for the record.
    *"i da nisu tako je mi predstavljamo i tacka"* — it is his
    instrument, and this is how it represents an eclipse.

    The four types, in the geometry he confirmed:
    ANNULAR — the Moon IS centred; it is simply too far away to be big
    enough, so the dark disc shrinks and stays put. PARTIAL — the Moon
    does not cross the centre, so a disc of the Sun's OWN size is
    offset, and the dark edge is the real circular arc of that disc at
    its real offset, never an approximation of the bite. TOTAL — the
    disc is covered and the rays alone remain. HYBRID — total at the
    epicentre, which is the instant we draw, plus the ghost ring
    (`_ghost_ring`).

    ONLY THE PNGs ARE EVER READ. The `.svg` twins beside them are the
    owner's own dead ends twice over: Qt renders SVG Tiny 1.2 and drops
    `mask`/`filter`/`feColorMatrix`, so his Moon comes out a flat olive
    disc — and by his own account his exporter mangles them anyway
    ("napravim jedno a onda kada eksportujem dobijem drugo"), which is
    why he redrew both as PNG. Never wire the SVG back in.
    """
    occulter, distance = solar_occulter_geometry(state, radius, covered)
    if state == "solar_annular":
        # THE LEGIBILITY EXAGGERATION, unchanged in meaning and now
        # expressed as the plate's SIZE instead of a stroke's width: at
        # the true 0.95 ratio the ring of fire is two pixels wide on a
        # dial mark and no one can tell which type they are looking at.
        # `_SOLAR_SIZE_RATIO` stays the physics; this is how thick the
        # physics is drawn. The OFFSET is left exactly as computed, so
        # the ring is very slightly richer on one limb — which is what a
        # real annular eclipse does.
        occulter = radius * _ANNULAR_SHRINK
    painter.save()
    # NO WALL AROUND THE SHINE (owner verdict 2026-08-16). A circular
    # clip at `_SUN_PLATE_REACH` used to sit here, biting the outer ray
    # tips off; the plate is now drawn at its own full extent, which is
    # what "shine EXTRA, over and beyond the disc" means. The disc below
    # is still exactly the body radius — that half of his rule is the
    # one this must not touch.
    _draw_body_plate(
        painter, defaults.ECLIPSE_BODY_SUN_ART,
        radius / _SUN_PLATE_DISC_FRACTION, 0.0,
    )
    # HIS ONE COMPOSITION RULE, enforced by a clip rather than by care:
    # the dark disc may cover the Sun's YELLOW DISC and never its rays.
    # `tests/test_eclipse_plates.py` re-proves it on the rendered pixels.
    painter.save()
    painter.setClipPath(_disc(radius, 0.0), Qt.ClipOperation.IntersectClip)
    _draw_body_plate(
        painter, defaults.ECLIPSE_BODY_MOON_ART,
        occulter / _MOON_PLATE_DISC_FRACTION, distance,
    )
    painter.restore()
    if state == "solar_hybrid":
        _ghost_ring(painter, occulter, distance)
    painter.restore()


def _ghost_ring(painter: QPainter, occulter: float, distance: float) -> None:
    """THE GHOST RING — a hybrid eclipse's own mark, and the only thing
    that separates it from a total one (owner reasoning 2026-08-13).

    We draw ONE picture, at greatest eclipse, and his own sentence
    settles what that picture is:
    lang-ok: the owner's own statement of the constraint, quoted so the
    reasoning behind this mark cannot be lost.
    *"mozes da predstavis i onako kako ona jeste a to je da razlicito
    vreme prikazujemo razlicito stanje ali to ne mozemo zato sto uvek
    prikazujemo sa jednom slikom i to kada je njen epicentar"* — a
    hybrid begins annular, turns total across the middle of its path
    and ends annular, so AT THE EPICENTRE IT IS TOTAL. The honest
    picture is therefore the total composition, and the second half of
    its nature has to be carried by an added MARK rather than by faking
    a geometry no observer ever sees. (The half-and-half split this
    replaced was geometrically fictional — no eclipse looks like that
    from anywhere — and leaning on the 1.00 against 1.05 size ratio
    alone is far too subtle: that is precisely how hybrid collapsed
    into total before the rework.)

    So: a thin, faint ring of fire hugging the inside of the dark
    limb — dimmer and thinner than the annular ring, unmistakably a
    TRACE of one rather than the thing itself. It says totality here,
    the ring of fire elsewhere along this path, and it is true.

    Its thickness is measured, not chosen: exactly the width of the rim
    glow the owner drew on his own Moon plate
    (`_MOON_PLATE_GLOW_FRACTION - _MOON_PLATE_DISC_FRACTION`), so the
    trace is as thick as the finest edge in his own visual language and
    a little over half the annular ring's `1 - _ANNULAR_SHRINK`."""
    width = occulter * (_MOON_PLATE_GLOW_FRACTION - _MOON_PLATE_DISC_FRACTION)
    edge = occulter - width / 2.0
    colour = QColor(palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR)
    colour.setAlphaF(_HYBRID_GHOST_ALPHA)
    pen = QPen(colour)
    pen.setWidthF(max(1.0, width))
    painter.save()
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QPointF(distance, 0.0), edge, edge)
    painter.restore()


def _draw_body_plate(
    painter: QPainter, path: Path, half_size: float, offset_x: float,
) -> None:
    """One of the owner's two body plates, centred at `offset_x` on the
    line of centres and drawn so the plate's square has `half_size`.

    Rasterized through `render.assets.shared_cache` — the one
    process-wide decoded-image cache (THE ONE COPY RULE), keyed by the
    pixel height it is asked for, so a dial repainting every minute
    decodes each file once per session and not once per tick. That call
    also runs `paths.art_file`, the single door through which a
    canonical `.png` finds a baked `.webp`.

    A MISSING PLATE RAISES. That is THE ONE PLATE LAW's own rule and it
    is not defensive noise: a silent fallback is exactly how a whole
    missing digit alphabet once shipped as font-drawn text with every
    test green."""
    height = 2.0 * half_size
    dpr = painter.device().devicePixelRatioF()
    pixmap = shared_cache().pixmap_by_height(path, height, dpr)
    if pixmap is None or pixmap.isNull():
        raise ValueError(f"the eclipse body plate {path} could not be drawn")
    painter.drawPixmap(
        QRectF(offset_x - half_size, -half_size, height, height),
        pixmap, QRectF(pixmap.rect()),
    )


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
