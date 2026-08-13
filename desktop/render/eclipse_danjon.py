"""THE DANJON SCALE as a lunar eclipse display style (owner ballot
2026-08-13, his note beside the option: it wants a table and text with
it).

L=0..L=4 is the eyeball brightness scale an observer estimates for a
totally eclipsed Moon at mid-totality. It is NOT in the catalog and it
is not computable — it depends on the state of Earth's stratosphere on
the night (the December 1992 eclipse, after Pinatubo, came in at L=0
where the geometry alone would have said L=3). So nothing here invents
an observation: `indicative_danjon` derives an INDICATIVE value from the
one real datum the catalog carries, the umbral magnitude, by the
accepted proxy of DEPTH IN THE UMBRA — and the gauge marks it with a
DASHED marker, which is this program's way of saying "estimate".

Full reasoning, the scale's own five descriptions and what this style
honestly cannot know: __about/eclipse_danjon.md. Layer: render.
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

from config import glow, palette
from render.letter_plates import plate_text_pixmap
from render.painting import tinted_gray

# THE TOTALITY WINDOW the indicative L is read across. Totality begins
# at umbral magnitude 1.0 — the Moon grazing the umbra's bright outer
# edge, the BRIGHTEST case, L=4 — and the deepest possible central
# eclipse reaches the magnitude at concentric immersion. That ceiling is
# MEASURED, not chosen: Earth's umbra at the Moon's distance is ~2.65
# lunar radii, so the magnitude there is (R + r) / 2r = (2.65 + 1) / 2 =
# 1.825. Deeper means darker, so L runs DOWN across this window.
TOTALITY_MAGNITUDE_MIN = 1.0
DEEPEST_UMBRAL_MAGNITUDE = 1.83
DANJON_MAX_STEP = 4

# THE GAUGE, in fractions of the Moon body's own radius — every number
# below is measured against the body it hangs under, so the mark scales
# with the marker and never needs a second set for the picker tile or
# the Encyclopedia plate. The deepest point the gauge reaches is
# `_BAR_TOP + _BAR_HEIGHT` = 2.30 r, which still clears the Encyclopedia
# plate's night ground (body 0.30 of the plate, ground 0.49 — 2.30 x
# 0.15 = 0.35 of the plate against a 0.49 ground). The label sits
# BETWEEN the body and the ladder and the three bands never overlap:
# 1.12-1.58 text, 1.76-2.06 ladder, 2.18-2.30 bar. The 0.18 gap under
# the text is not slack — the selected cell's DASHED marker is drawn
# `_MARKER_INSET` (0.07) OUTSIDE its cell, and at a 0.08 gap the render
# showed the digit's tail sitting on the marker's top edge.
_LADDER_HALF_WIDTH = 1.20
_LADDER_TOP = 1.76
_CELL_HEIGHT = 0.30
_CELL_GAP = 0.06
_FRAME_WIDTH = 0.035
_MARKER_INSET = 0.07
_MARKER_DASH = (2.0, 2.0)              # in pen widths
_TEXT_HEIGHT = 0.46
# MEASURED off the first render: at 1.02 the label's top sat inside the
# body's own glow and, in bronze, a dark-red L3 stood on a dark-red
# disc — unreadable. It clears the body entirely at 1.12 and wears
# SILVER, the brightest plate metal, because this label is the one part
# of the mark that must be READ rather than recognised.
_TEXT_TOP = 1.12
_TEXT_METAL = "silver"
_BAR_TOP = 2.18                        # the partial's magnitude bar
_BAR_HEIGHT = 0.12
_EMPTY_ALPHA = 0.55                    # the partial's unfilled ladder
_PENUMBRAL_ALPHA = 0.28                # fainter still: no umbral phase


def indicative_danjon(state: str, magnitude: float | None) -> int | None:
    """The INDICATIVE Danjon L (0-4) for a lunar eclipse, or None when
    the scale does not apply.

    INDICATIVE, and the word is load-bearing: the catalog carries no
    observed L and no computation can produce one (see the module
    docstring and `__about/eclipse_danjon.md`). This is the accepted
    proxy — depth in the umbra — mapped linearly across the totality
    window above, and it must never be presented as an observation.

    None for every state but "lunar_total", because the scale is defined
    for the appearance at MID-TOTALITY: a partial eclipse has no
    totality to rate and a penumbral one has no umbral phase at all.
    None also for a magnitude-less (malformed) catalog row — the reading
    is withheld rather than guessed, which is the honest direction here:
    unlike a glow strength, a WRONG L would be a stated fact.
    """
    if state != "lunar_total" or magnitude is None:
        return None
    span = DEEPEST_UMBRAL_MAGNITUDE - TOTALITY_MAGNITUDE_MIN
    depth = (magnitude - TOTALITY_MAGNITUDE_MIN) / span
    step = round(DANJON_MAX_STEP * (1.0 - depth))
    return max(0, min(DANJON_MAX_STEP, step))


def draw_danjon_scale(
    painter: QPainter, radius: float, state: str, magnitude: float | None,
) -> None:
    """The whole style, centred on the painter's current origin: the
    Moon's disc wearing the indicated step's own colour, and the five-
    cell legend beneath it.

    Three pictures, one per lunar type, because the scale genuinely says
    three different things:
    * TOTAL — filled colour ladder, dashed marker under the indicative
      step, the value spelled beside it in letter plates.
    * PARTIAL — the ladder as empty outlines (no reading exists) with a
      bar beneath showing the umbral magnitude, the datum that IS real.
    * PENUMBRAL — no umbral phase to rate: faint outlines, struck
      through.
    """
    step = indicative_danjon(state, magnitude)
    _multiply_disc(painter, radius, state, step)
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _draw_ladder(painter, radius, state, step)
    if step is not None:
        _draw_value(painter, radius, step)
    elif state == "lunar_partial":
        _draw_magnitude_bar(painter, radius, magnitude)
    else:
        _strike_through(painter, radius)
    painter.restore()


def _multiply_disc(
    painter: QPainter, radius: float, state: str, step: int | None,
) -> None:
    """The disc takes the indicated step's OWN colour under a multiply —
    the same five colours the ladder shows, so the Moon and the legend
    can never disagree. Where no L exists the disc falls back to the
    state's shipped brightness (`glow.ECLIPSE_STATE_MOON_BRIGHTNESS`),
    which is the honest picture: the style has nothing of its own to say
    about a partial or a penumbral eclipse's colour."""
    disc = QPainterPath()
    disc.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
    if step is None:
        value = round(255 * glow.ECLIPSE_STATE_MOON_BRIGHTNESS[state])
        color = tinted_gray(value, None)
    else:
        color = QColor(palette.ECLIPSE_DANJON_COLORS[step])
    painter.save()
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
    painter.fillPath(disc, color)
    painter.restore()


def _cell_rects(radius: float) -> list[QRectF]:
    """The five legend cells, left to right, L0 first."""
    total = 2.0 * _LADDER_HALF_WIDTH * radius
    gap = _CELL_GAP * radius
    width = (total - gap * DANJON_MAX_STEP) / (DANJON_MAX_STEP + 1)
    top = _LADDER_TOP * radius
    height = _CELL_HEIGHT * radius
    left = -_LADDER_HALF_WIDTH * radius
    return [
        QRectF(left + index * (width + gap), top, width, height)
        for index in range(DANJON_MAX_STEP + 1)
    ]


def _draw_ladder(
    painter: QPainter, radius: float, state: str, step: int | None,
) -> None:
    frame = QPen(QColor(palette.ECLIPSE_DANJON_FRAME_COLOR))
    frame.setWidthF(max(1.0, radius * _FRAME_WIDTH))
    # No reading: the cells stay EMPTY OUTLINES. A partial eclipse's
    # ladder is merely unfilled; a penumbral one is fainter still,
    # because there is not even an umbral phase to rate.
    if step is None:
        faded = QColor(palette.ECLIPSE_DANJON_FRAME_COLOR)
        faded.setAlphaF(
            _PENUMBRAL_ALPHA if state == "lunar_penumbral" else _EMPTY_ALPHA
        )
        frame.setColor(faded)
    for index, rect in enumerate(_cell_rects(radius)):
        painter.setPen(frame)
        painter.setBrush(
            Qt.BrushStyle.NoBrush if step is None
            else QColor(palette.ECLIPSE_DANJON_COLORS[index])
        )
        painter.drawRect(rect)
    if step is None:
        return
    # THE MARKER IS DASHED — the reading is INDICATIVE (module
    # docstring), and a solid outline would claim an observation the
    # program does not have.
    marker = QPen(QColor(palette.ECLIPSE_DANJON_MARKER_COLOR))
    marker.setWidthF(max(1.0, radius * _FRAME_WIDTH * 1.6))
    marker.setDashPattern(list(_MARKER_DASH))
    painter.setPen(marker)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    inset = radius * _MARKER_INSET
    painter.drawRect(_cell_rects(radius)[step].adjusted(
        -inset, -inset, inset, inset
    ))


def _draw_value(painter: QPainter, radius: float, step: int) -> None:
    """`L3`, in LETTER PLATES — THE ONE PLATE LAW, never a font. Every
    glyph this needs (`L` and the five digits) has a plate, so a missing
    one would be a real defect and `plate_text_pixmap` raises on it."""
    height = max(1, round(radius * _TEXT_HEIGHT))
    pixmap = plate_text_pixmap(f"L{step}", height, _TEXT_METAL)
    painter.drawPixmap(
        QPointF(-pixmap.width() / 2.0, radius * _TEXT_TOP), pixmap
    )


def _draw_magnitude_bar(
    painter: QPainter, radius: float, magnitude: float | None,
) -> None:
    """A PARTIAL eclipse has no Danjon reading, but it does carry a real
    umbral magnitude — how much of the Moon's diameter entered the
    umbra. The bar fills that fraction of the ladder's own width, so the
    picture still says something true instead of standing empty."""
    total = 2.0 * _LADDER_HALF_WIDTH * radius
    left = -_LADDER_HALF_WIDTH * radius
    top = radius * _BAR_TOP
    height = radius * _BAR_HEIGHT
    frame = QPen(QColor(palette.ECLIPSE_DANJON_FRAME_COLOR))
    frame.setWidthF(max(1.0, radius * _FRAME_WIDTH))
    painter.setPen(frame)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRect(QRectF(left, top, total, height))
    filled = total * max(0.0, min(1.0, magnitude or 0.0))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette.ECLIPSE_TOTAL_MOON_TINT))
    painter.drawRect(QRectF(left, top, filled, height))


def _strike_through(painter: QPainter, radius: float) -> None:
    """A PENUMBRAL eclipse never enters the umbra, so there is no umbral
    phase for the scale to rate at all — one diagonal across the whole
    ladder, the plainest way to draw "does not apply"."""
    cells = _cell_rects(radius)
    pen = QPen(QColor(palette.ECLIPSE_DANJON_MARKER_COLOR))
    pen.setWidthF(max(1.0, radius * _FRAME_WIDTH * 1.6))
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawLine(
        QPointF(cells[0].left(), cells[0].bottom()),
        QPointF(cells[-1].right(), cells[-1].top()),
    )
