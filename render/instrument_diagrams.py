"""The INSTRUMENT's own diagrams — the clock explaining itself.

Seven Encyclopedia pages describe how this dial works: the 24-hour face,
the star's solar tilt, the twilight bands, the year wheel, the moon's
lunations, the three metals and the ring letters. Every one of them is a
FIGURE OF THE PROGRAM'S OWN GEOMETRY — the same numbers the dial is
drawn from — so root Rule #19 answers before any prompt sheet does:
compute, never generate. An eighth page joins them from the far end of
the same instrument, the Great Oscillations, drawn from the very
envelope the Observatory charts.

That is the whole test applied here: if changing a constant would make
the painted plate a LIE, the plate must not be painted. Move
`DIAL_OFFSET_DEG` and a commissioned dial illustration silently becomes
wrong; this one turns with it.

Layer: render (Qt allowed; no wall clock, no settings). Documentation:
instrument_diagrams.md.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor, QFont, QFontMetricsF, QPainter, QPen, QPixmap,
)

from config import constants, doctrine, encyclopedia_ui, palette
from core import angles

# The eight figures this module draws, in the order the Instrument topic
# reads them. `app.encyclopedia.tree` imports this tuple rather than
# keeping a second list of the same names (Rule #5) — a page can only
# declare a diagram that exists here.
INSTRUMENT_FIGURES = (
    "dial",
    "solar_rotation",
    "twilight",
    "year_wheel",
    "moon_lunations",
    "metals",
    "ring_letters",
    "oscillations",
)

_INK = palette.THEME_COLORS["text_primary"]
_FAINT = palette.THEME_COLORS["text_secondary"]
_ACCENT = palette.THEME_COLORS["accent"]


# --- shared drawing primitives ------------------------------------------------

def _canvas(size: int) -> tuple[QPixmap, QPainter]:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    return pixmap, painter


def _font(size: int, ratio: float = None, bold: bool = True) -> QFont:
    font = QFont()
    ratio = encyclopedia_ui.INSTRUMENT_DIAGRAM_LABEL_RATIO if ratio is None else ratio
    font.setPixelSize(max(9, round(size * ratio)))
    font.setBold(bold)
    return font


def _pen(color: str, size: int, ratio: float = 0.004) -> QPen:
    pen = QPen(QColor(color))
    pen.setWidthF(max(1.0, size * ratio))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    return pen


def _on_dial(center: QPointF, radius: float, dial_deg: float) -> QPointF:
    """A point at a DIAL angle — degrees clockwise from the top, the one
    convention this whole program is built on."""
    theta = math.radians(dial_deg - 90.0)
    return QPointF(
        center.x() + radius * math.cos(theta),
        center.y() + radius * math.sin(theta),
    )


def _text(painter: QPainter, point: QPointF, text: str, size: int,
          color: str = None) -> None:
    """A label centred on `point` and CLAMPED to the plate — a label
    drawn past the edge is silently lost, which is how the Cube's first
    axis figures shipped with half their names missing.

    The box is measured from the FONT, never guessed: a guessed width
    clamps a short label to the middle of the plate (the "06h" bug this
    replaced), because the clamp can only be as honest as the width it
    is given."""
    painter.setPen(QPen(QColor(color or _INK)))
    metrics = QFontMetricsF(painter.font())
    half_w = metrics.horizontalAdvance(text) / 2 + size * 0.006
    half_h = metrics.height() / 2
    margin = encyclopedia_ui.INSTRUMENT_DIAGRAM_MARGIN_PX
    x = min(max(point.x(), margin + half_w), size - margin - half_w)
    y = min(max(point.y(), margin + half_h), size - margin - half_h)
    painter.drawText(
        QRectF(x - half_w, y - half_h, half_w * 2, half_h * 2),
        Qt.AlignmentFlag.AlignCenter,
        text,
    )


def _caption(painter: QPainter, size: int, text: str) -> None:
    """The one line under every figure that says what it is measuring."""
    painter.setFont(_font(size, encyclopedia_ui.INSTRUMENT_DIAGRAM_CAPTION_RATIO, False))
    painter.setPen(QPen(QColor(_FAINT)))
    painter.drawText(
        QRectF(
            encyclopedia_ui.INSTRUMENT_DIAGRAM_MARGIN_PX,
            size * encyclopedia_ui.INSTRUMENT_DIAGRAM_CAPTION_Y,
            size - 2 * encyclopedia_ui.INSTRUMENT_DIAGRAM_MARGIN_PX,
            size * 0.08,
        ),
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
        text,
    )


def _dial_face(painter: QPainter, center: QPointF, radius: float,
               size: int) -> None:
    """The bare 24-hour face every instrument figure stands on: the ring,
    a tick per hour, the four cardinal hours named."""
    painter.setPen(_pen(_FAINT, size, 0.005))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(center, radius, radius)
    for hour in range(constants.HOURS_PER_REVOLUTION):
        cardinal = hour % 6 == 0
        angle = angles.ring_position_angle(hour)
        inner = radius * (0.90 if cardinal else 0.95)
        painter.setPen(_pen(_INK if cardinal else _FAINT, size,
                            0.006 if cardinal else 0.003))
        painter.drawLine(
            _on_dial(center, inner, angle), _on_dial(center, radius, angle)
        )
    painter.setFont(_font(size))
    for hour, label in (
        (12, "12h — noon"), (18, "18h"), (0, "24h — midnight"), (6, "06h"),
    ):
        angle = angles.ring_position_angle(hour)
        point = _on_dial(center, radius * 1.12, angle)
        _text(painter, point, label, size)


# --- the seven dial figures ---------------------------------------------------

def _dial(_key: str, size: int) -> QPixmap:
    """The face itself: twenty-four hours on ONE turn, and the two hands
    at the sample moment — the hour hand once round per DAY, the minute
    hand once round per HOUR, no seconds hand."""
    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size / 2)
    radius = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_RING_RATIO
    _dial_face(painter, center, radius, size)
    hour, minute = encyclopedia_ui.INSTRUMENT_DIAGRAM_SAMPLE_TIME
    seconds = hour * constants.SECONDS_PER_HOUR + minute * 60
    hour_angle = (
        seconds / constants.SECONDS_PER_DAY * 360.0 + constants.DIAL_OFFSET_DEG
    ) % 360.0
    minute_angle = (minute * 60) / constants.SECONDS_PER_HOUR * 360.0
    painter.setPen(_pen(_ACCENT, size, 0.011))
    painter.drawLine(center, _on_dial(center, radius * 0.60, hour_angle))
    painter.setPen(_pen(_INK, size, 0.006))
    painter.drawLine(center, _on_dial(center, radius * 0.86, minute_angle))
    painter.setBrush(QColor(_ACCENT))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(center, size * 0.012, size * 0.012)
    painter.setFont(_font(size))
    _text(painter, _on_dial(center, radius * 0.46, hour_angle),
          f"{hour:02d}:{minute:02d}", size, color=_ACCENT)
    _caption(painter, size,
             "one turn = one day · the hour hand 1 rev/24h, "
             "the minute hand 1 rev/h")
    painter.end()
    return pixmap


def _solar_rotation(_key: str, size: int) -> QPixmap:
    """Why the star stands tipped: its top vertex points at TRUE solar
    noon, and the tilt is `(noon − 12:00) / 240` degrees. Drawn at the
    project's own golden value so the figure is a measurement, not a
    decoration."""
    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size / 2)
    radius = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_RING_RATIO
    painter.setPen(_pen(_FAINT, size, 0.004))
    painter.drawEllipse(center, radius, radius)
    tilt = encyclopedia_ui.INSTRUMENT_DIAGRAM_SAMPLE_TILT_DEG
    # Clock noon — where an untipped star would point.
    dashed = _pen(_FAINT, size, 0.004)
    dashed.setStyle(Qt.PenStyle.DashLine)
    painter.setPen(dashed)
    painter.drawLine(center, _on_dial(center, radius, 0.0))
    # The hexagram: two triangles, six vertices 60° apart, turned by the
    # day's own offset.
    painter.setPen(_pen(_ACCENT, size, 0.007))
    for start in (0.0, 60.0):
        points = [
            _on_dial(center, radius * 0.92, start + tilt + step * 120.0)
            for step in range(3)
        ]
        painter.drawPolygon(points)
    # The TOP VERTEX is the pointer — the line only makes that visible,
    # it is not a needle of its own.
    painter.setPen(_pen(_ACCENT, size, 0.004))
    painter.drawLine(center, _on_dial(center, radius * 0.92, tilt))
    painter.setFont(_font(size))
    _text(painter, _on_dial(center, radius * 1.18, -14.0), "clock noon", size,
          color=_FAINT)
    _text(painter, _on_dial(center, radius * 1.18, tilt + 16.0),
          f"solar noon  +{tilt:.2f}°", size, color=_ACCENT)
    _caption(painter, size,
             "tilt = (solar noon − 12:00) ÷ 240 s/° · zone longitude + "
             "the equation of time + DST")
    painter.end()
    return pixmap


def _twilight(_key: str, size: int) -> QPixmap:
    """The three bands under the horizon, at their real depressions —
    and the one DOMY actually draws."""
    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size / 2)
    radius = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_RING_RATIO
    bands = tuple(
        (start, end, f"{name}  {start:.0f}–{end:.0f}°",
         palette.INSTRUMENT_TWILIGHT_COLORS[name])
        for start, end, name in encyclopedia_ui.INSTRUMENT_TWILIGHT_BANDS
    )
    box = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
    painter.setPen(Qt.PenStyle.NoPen)
    # The lit sky above the horizon, the dark world below it...
    painter.setBrush(QColor(palette.INSTRUMENT_TWILIGHT_COLORS["day"]))
    painter.drawPie(box, 0, 180 * 16)
    painter.setBrush(QColor(palette.INSTRUMENT_TWILIGHT_COLORS["night"]))
    painter.drawPie(box, 180 * 16, 180 * 16)
    # ...and the three bands as wedges under the WEST horizon, each one
    # exactly as deep as its own definition. Qt measures 1/16° counter-
    # clockwise from 3 o'clock, so "below the horizon on the right" is a
    # negative start angle.
    for start, end, _label, color in bands:
        painter.setBrush(QColor(color))
        painter.drawPie(box, int(-end * 16), int((end - start) * 16))
    painter.setPen(_pen(_INK, size, 0.004))
    painter.drawLine(
        QPointF(center.x() - radius * 1.06, center.y()),
        QPointF(center.x() + radius * 1.06, center.y()),
    )
    # The sun setting into the bands.
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette.INSTRUMENT_TWILIGHT_COLORS["sun"]))
    painter.drawEllipse(
        _on_dial(center, radius, 90.0), size * 0.022, size * 0.022
    )
    painter.setFont(_font(size))
    _text(painter, QPointF(center.x() - radius * 0.55, center.y() - size * 0.03),
          "the horizon", size, color=_INK)
    # The legend: the wedges are only degrees wide, so each band says its
    # own name beside its own colour rather than inside a sliver.
    swatch = size * 0.020
    for index, (_start, _end, label, color) in enumerate(bands):
        y = center.y() + radius * (0.42 + index * 0.22)
        x = center.x() - radius * 0.72
        painter.setPen(_pen(_FAINT, size, 0.002))
        painter.setBrush(QColor(color))
        painter.drawEllipse(QPointF(x, y), swatch, swatch)
        painter.setFont(_font(size))
        metrics = QFontMetricsF(painter.font())
        _text(painter,
              QPointF(x + swatch * 2 + metrics.horizontalAdvance(label) / 2, y),
              label, size, color=_INK)
    _caption(painter, size,
             "the sun's depression below the horizon · DOMY draws the "
             "CIVIL band")
    painter.end()
    return pixmap


def _year_wheel(_key: str, size: int) -> QPixmap:
    """The second, slower hand: the year on the same face. Every season
    is drawn as an EQUAL quarter (owner spec) while its anchors sit on
    the real astronomical instants — the two facts the article puts side
    by side, so the figure has to show both."""
    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size / 2)
    # A tighter ring than the other figures: the four anchor names are
    # long, and two of them stand at the widest point of the disc.
    radius = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_YEAR_RING_RATIO
    # Anchor -> the season that BEGINS there and runs clockwise to the
    # next anchor. Summer opens at the top with the June solstice, so
    # the top-right quarter is summer's own, and each quarter wears that
    # season's hue from the pointer palette.
    seasons = (
        ("summer solstice", "summer"), ("autumn equinox", "autumn"),
        ("winter solstice", "winter"), ("spring equinox", "spring"),
    )
    box = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
    painter.setPen(Qt.PenStyle.NoPen)
    for index, (_anchor, season) in enumerate(seasons):
        painter.setBrush(QColor(palette.INSTRUMENT_SEASON_COLORS[season]))
        # Qt measures counter-clockwise from 3 o'clock; the dial runs
        # clockwise from the top, so a quarter starting at dial angle
        # `index * 90` begins at 90 − that.
        painter.drawPie(box, int((90 - index * 90 - 90) * 16), int(90 * 16))
    painter.setPen(_pen(_INK, size, 0.005))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(center, radius, radius)
    painter.setFont(_font(size))
    for index, (anchor, season) in enumerate(seasons):
        angle = index * 90.0
        painter.setPen(_pen(_INK, size, 0.006))
        painter.drawLine(
            _on_dial(center, radius * 0.88, angle),
            _on_dial(center, radius, angle),
        )
        _text(painter, _on_dial(center, radius * 1.34, angle), anchor, size)
        seat = _on_dial(center, radius * 0.62, angle + 45.0)
        _text(painter, seat, season, size)
        _text(painter, QPointF(seat.x(), seat.y() + size * 0.035), "90°", size)
    _caption(painter, size,
             "four equal quarters on the face · each anchor on its real "
             "astronomical instant")
    painter.end()
    return pixmap


def _moon_lunations(_key: str, size: int) -> QPixmap:
    """The month around the face: the phase drawn from its own fraction
    — the terminator is an ellipse whose width is `cos(2πf)`, which is
    the same maths the dial's own moon marker uses."""
    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size / 2)
    radius = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_RING_RATIO
    steps = encyclopedia_ui.INSTRUMENT_DIAGRAM_PHASE_STEPS
    disc = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_MOON_RATIO
    painter.setPen(_pen(_FAINT, size, 0.003))
    painter.drawEllipse(center, radius, radius)
    painter.setFont(_font(size))
    for step in range(steps):
        fraction = step / steps
        seat = _on_dial(center, radius, angles.moon_cycle_angle(fraction))
        _draw_phase(painter, seat, disc, fraction, size)
        if step % (steps // 4) == 0:
            name = constants.MOON_PHASE_NAMES[step // (steps // 4) * 2]
            # INSIDE the ring: the quarters sit at the plate's own edge,
            # so a name hung outside them lands on top of its own moon.
            _text(painter, _on_dial(center, radius * 0.62,
                                    angles.moon_cycle_angle(fraction)),
                  name, size)
    _caption(painter, size,
             "one lunation = 29.53 days · new at the top, full at the "
             "bottom, clockwise")
    painter.end()
    return pixmap


def _draw_phase(painter: QPainter, center: QPointF, radius: float,
                fraction: float, size: int) -> None:
    """One moon at phase `fraction` (0 new, 0.5 full): the dark disc,
    then the lit part built from a half-disc and the terminator ellipse
    — added when the moon is gaining, cut away when it is losing."""
    theta = 2 * math.pi * fraction
    painter.setPen(_pen(_FAINT, size, 0.002))
    painter.setBrush(QColor(palette.INSTRUMENT_MOON_COLORS["dark"]))
    painter.drawEllipse(center, radius, radius)
    if abs(fraction - 0.0) < 1e-9:
        return
    lit = QColor(palette.INSTRUMENT_MOON_COLORS["lit"])
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(lit)
    box = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
    # The waxing half is on the RIGHT, the waning half on the LEFT.
    waxing = fraction < 0.5
    painter.drawPie(box, int((-90 if waxing else 90) * 16), int(180 * 16))
    half_width = radius * abs(math.cos(theta))
    ellipse = QRectF(
        center.x() - half_width, center.y() - radius, half_width * 2, radius * 2
    )
    gibbous = 0.25 < fraction < 0.75
    painter.setBrush(lit if gibbous
                     else QColor(palette.INSTRUMENT_MOON_COLORS["dark"]))
    painter.drawEllipse(ellipse)


def _metals(_key: str, size: int) -> QPixmap:
    """Two metals of TIME and three of FINISH. The star wears gold at
    noon and silver at midnight; the three finishes below are the same
    art recoloured, which is exactly why no plate of them is painted."""
    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size * 0.34)
    radius = size * 0.22
    painter.setPen(_pen(_FAINT, size, 0.004))
    for start in (0.0, 60.0):
        points = [
            _on_dial(center, radius, start + step * 120.0) for step in range(3)
        ]
        painter.drawPolygon(points)
    finishes = palette.ENCYCLOPEDIA_FINISH_BORDER_COLORS
    painter.setPen(Qt.PenStyle.NoPen)
    for angle, name in ((0.0, "Gold"), (180.0, "Silver")):
        tip = _on_dial(center, radius, angle)
        painter.setBrush(QColor(finishes[name]))
        painter.drawEllipse(tip, size * 0.030, size * 0.030)
    painter.setFont(_font(size))
    top, bottom = _on_dial(center, radius, 0.0), _on_dial(center, radius, 180.0)
    _text(painter, QPointF(top.x(), top.y() - size * 0.045), "gold — noon", size)
    _text(painter, QPointF(bottom.x(), bottom.y() + size * 0.045),
          "silver — midnight", size)
    swatch = size * 0.075
    order = ("Bronze", "Gold", "Silver")
    for index, name in enumerate(order):
        x = size * (0.5 + (index - 1) * 0.24)
        y = size * 0.72
        painter.setPen(_pen(_FAINT, size, 0.003))
        painter.setBrush(QColor(finishes[name]))
        painter.drawEllipse(QPointF(x, y), swatch, swatch)
        _text(painter, QPointF(x, y + swatch * 1.7), name, size)
    _caption(painter, size,
             "one master, three finishes — the bronze art recoloured "
             "live, never three files")
    painter.end()
    return pixmap


def _ring_letters(_key: str, size: int) -> QPixmap:
    """D · Ω · M · Y — and the reason: each is a Greek letter standing
    at the hour equal to its PLACE in the Greek alphabet. The seats come
    from `config.doctrine`, so the figure cannot drift from the canon
    table the article quotes."""
    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size / 2)
    radius = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_RING_RATIO
    _dial_face(painter, center, radius, size)
    painter.setFont(_font(size, encyclopedia_ui.INSTRUMENT_DIAGRAM_GLYPH_RATIO))
    for glyph, place in doctrine.RING_LETTER_SEATS:
        angle = angles.ring_position_angle(place)
        _text(painter, _on_dial(center, radius * 0.78, angle), glyph, size, color=_ACCENT)
        painter.setFont(_font(size))
        _text(painter, _on_dial(center, radius * 0.55, angle),
              f"{place}th letter · {place:02d}h", size, color=_INK)
        painter.setFont(_font(size, encyclopedia_ui.INSTRUMENT_DIAGRAM_GLYPH_RATIO))
    _caption(painter, size,
             "each letter sits at the hour of its own place in the "
             "Greek alphabet")
    painter.end()
    return pixmap


# --- the deep-time figure -----------------------------------------------------

def _oscillations(_key: str, size: int) -> QPixmap:
    """The Great Oscillations: the La2004 amplitude envelope the
    Observatory already plots, drawn here from the SAME bundle. A
    painted version of this chart would be a picture of a number that
    changes when the bundle changes — the plainest Rule #19 case in the
    whole book."""
    from data.observatory import ObservatoryData

    pixmap, painter = _canvas(size)
    envelope = ObservatoryData().laskar_envelope()
    years = envelope["years"]
    high = envelope["envelope_days"]
    signed = envelope["signed_days"]
    inset = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_CHART_INSET
    plot = QRectF(inset, inset, size - 2 * inset,
                  size * encyclopedia_ui.INSTRUMENT_DIAGRAM_CHART_HEIGHT)
    span = max(years) - min(years)
    peak = max(max(high), abs(min(signed)), max(signed)) or 1.0

    def point(year: float, value: float) -> QPointF:
        return QPointF(
            plot.left() + (year - min(years)) / span * plot.width(),
            plot.center().y() - value / peak * plot.height() / 2,
        )

    painter.setPen(_pen(_FAINT, size, 0.003))
    painter.drawRect(plot)
    painter.drawLine(point(min(years), 0.0), point(max(years), 0.0))
    # NOW, the one moment the reader is standing on.
    zero = _pen(_FAINT, size, 0.003)
    zero.setStyle(Qt.PenStyle.DashLine)
    painter.setPen(zero)
    painter.drawLine(QPointF(point(0.0, 0.0).x(), plot.top()),
                     QPointF(point(0.0, 0.0).x(), plot.bottom()))
    for series, color, width in (
        (signed, palette.OBSERVATORY_LASKAR_SIGNED_COLOR, 0.0025),
        (high, palette.OBSERVATORY_LASKAR_ENVELOPE_COLOR, 0.004),
        ([-value for value in high],
         palette.OBSERVATORY_LASKAR_ENVELOPE_COLOR, 0.004),
    ):
        painter.setPen(_pen(color, size, width))
        previous = None
        for year, value in zip(years, series):
            current = point(year, value)
            if previous is not None:
                painter.drawLine(previous, current)
            previous = current
    painter.setFont(_font(size))
    _text(painter, QPointF(point(0.0, 0.0).x(), plot.bottom() + size * 0.035),
          "now", size, color=_FAINT)
    _text(painter, QPointF(plot.left() + size * 0.10, plot.top() - size * 0.03),
          f"±{peak:.1f} days", size, color=_INK)
    _text(painter, QPointF(plot.center().x(), plot.bottom() + size * 0.10),
          f"{min(years):+,.0f} … {max(years):+,.0f} years", size, color=_INK)
    _caption(painter, size,
             "the light half-year breathing against the dark · "
             "La2004, an envelope, not dated events")
    painter.end()
    return pixmap


_DRAWERS = {
    "dial": _dial,
    "solar_rotation": _solar_rotation,
    "twilight": _twilight,
    "year_wheel": _year_wheel,
    "moon_lunations": _moon_lunations,
    "metals": _metals,
    "ring_letters": _ring_letters,
    "oscillations": _oscillations,
}
_CACHE: dict = {}


def plate(kind: str, key: str, size: int) -> QPixmap:
    """The figure for one page, cached per (kind, key, size) — the
    reader re-fits on every resize and must never redraw the same
    figure twice. `kind` is always "instrument"; the KEY names the
    figure."""
    cached = _CACHE.get((kind, key, size))
    if cached is None:
        drawer = _DRAWERS.get(key)
        if drawer is None:
            return QPixmap()
        cached = drawer(key, size)
        _CACHE[(kind, key, size)] = cached
    return cached


def kinds() -> tuple:
    """The one kind this module answers — the facade reads it to route a
    page's declaration here."""
    return ("instrument",)
