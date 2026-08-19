"""The INSTRUMENT's own diagrams — the clock explaining itself.

Ten Encyclopedia pages describe how this dial works: the 24-hour face,
the star's solar tilt, the two world modes, the twilight bands, the year
wheel, the moon's lunations, the three metals, the ring jewels, the six
ring presets and the seven pointers. Every one of them is a
FIGURE OF THE PROGRAM'S OWN GEOMETRY — the same numbers the dial is
drawn from — so root Rule #19 answers before any prompt sheet does:
compute, never generate. An eleventh page joins them from the far end of
the same instrument, the Great Oscillations, drawn from the very
envelope the Observatory charts; a twelfth, CHI (wave 5), is the odd one
out among them — not a SKETCH of the program's geometry but the real
`"full"` outer plate composed live and the X master recolored through
the actual asset cache, because that article's whole point is what the
ceramic finish looks like.

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

from config import constants, dial, doctrine, encyclopedia_ui, palette, paths
from core import angles
from render import letter_plates
from render.diagram_bank import DiagramBank

# The twelve figures this module draws, in the order the Instrument topic
# reads them. `app.encyclopedia.tree` imports this tuple rather than
# keeping a second list of the same names (Rule #5) — a page can only
# declare a diagram that exists here.
INSTRUMENT_FIGURES = (
    "dial",
    "solar_rotation",
    "world_modes",
    "twilight",
    "year_wheel",
    "moon_lunations",
    "metals",
    "ring_jewels",
    "ring_presets",
    "pointers",
    "oscillations",
    "chi",
)

_INK = palette.THEME_COLORS["text_primary"]
_FAINT = palette.THEME_COLORS["text_secondary"]
_ACCENT = palette.THEME_COLORS["accent"]


# --- shared drawing primitives ------------------------------------------------

def _canvas(size: int, aspect: float = 1.0) -> tuple[QPixmap, QPainter]:
    """The plate a figure is drawn on. `size` is its WIDTH; `aspect` is
    width/height, so the nine square figures keep their square and the
    three ROW figures get the wide canvas THE SPACE & LEGIBILITY LAW
    asks for (see `encyclopedia_ui.INSTRUMENT_DIAGRAM_GRIDS`)."""
    pixmap = QPixmap(size, max(1, round(size / aspect)))
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
    return _pen_px(color, size * ratio)


def _pen_px(color: str, width: float) -> QPen:
    """The same pen, given its width outright — what a TILE needs, whose
    only honest frame of reference is its own radius rather than the
    plate it happens to be standing on."""
    pen = QPen(QColor(color))
    pen.setWidthF(max(1.0, width))
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
          color: str = None, height: int = None) -> None:
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
    # `size` is the plate's WIDTH; a ROW figure's plate is shorter than
    # it is wide, so the vertical clamp needs its own bound or a label
    # would be "clamped" against an edge that is not there.
    bottom = size if height is None else height
    x = min(max(point.x(), margin + half_w), size - margin - half_w)
    y = min(max(point.y(), margin + half_h), bottom - margin - half_h)
    painter.drawText(
        QRectF(x - half_w, y - half_h, half_w * 2, half_h * 2),
        Qt.AlignmentFlag.AlignCenter,
        text,
    )


def _caption(painter: QPainter, size: int, text: str,
             height: int = None, font_px: int = None,
             band: float = None) -> None:
    """The one line under every figure that says what it is measuring.

    A ROW figure passes its own (shorter) `height` and the pixel size its
    band was budgeted for — the square figures' `..._CAPTION_RATIO` is a
    share of the SIDE, and on a plate four times wider than it is tall
    that same share would draw a caption taller than the tiles."""
    bottom = size if height is None else height
    if font_px is None:
        font = _font(size, encyclopedia_ui.INSTRUMENT_DIAGRAM_CAPTION_RATIO, False)
        top = bottom * encyclopedia_ui.INSTRUMENT_DIAGRAM_CAPTION_Y
    else:
        font = QFont()
        font.setPixelSize(max(9, font_px))
        top = bottom * (1.0 - (
            encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_CAPTION_BAND
            if band is None else band
        ))
    box = QRectF(
        encyclopedia_ui.INSTRUMENT_DIAGRAM_MARGIN_PX,
        top,
        size - 2 * encyclopedia_ui.INSTRUMENT_DIAGRAM_MARGIN_PX,
        bottom - top,
    )
    flags = (Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
             | Qt.TextFlag.TextWordWrap)
    # SHRINK TO FIT, never clip (THE SPACE & LEGIBILITY LAW: "if it
    # renders, it renders whole"). A caption that outgrew its band used
    # to be drawn straight past both edges of the plate and lost its
    # first and last words in silence — which is exactly the defect the
    # law names, and no reader could tell it had happened.
    while font.pixelSize() > 9:
        wrapped = QFontMetricsF(font).boundingRect(box, flags, text)
        if wrapped.width() <= box.width() and wrapped.height() <= box.height():
            break
        font.setPixelSize(font.pixelSize() - 1)
    painter.setFont(font)
    painter.setPen(QPen(QColor(_FAINT)))
    painter.drawText(box, flags, text)


def _dial_face(painter: QPainter, center: QPointF, radius: float,
               size: int) -> None:
    """The bare 24-hour face every instrument figure stands on: the ring,
    a tick per hour, the four cardinal hours named."""
    painter.setPen(_pen(_FAINT, size, 0.005))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(center, radius, radius)
    for hour in range(dial.HOURS_PER_REVOLUTION):
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
    seconds = hour * dial.SECONDS_PER_HOUR + minute * 60
    hour_angle = (
        seconds / dial.SECONDS_PER_DAY * 360.0 + dial.DIAL_OFFSET_DEG
    ) % 360.0
    minute_angle = (minute * 60) / dial.SECONDS_PER_HOUR * 360.0
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


def _ring_jewels(_key: str, size: int) -> QPixmap:
    """D · Ω · M · Y — and the reason: each is a Greek letter standing
    at the hour equal to its PLACE in the Greek alphabet. The seats come
    from `config.doctrine`, so the figure cannot drift from the canon
    table the article quotes."""
    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size / 2)
    radius = size * encyclopedia_ui.INSTRUMENT_DIAGRAM_RING_RATIO
    _dial_face(painter, center, radius, size)
    painter.setFont(_font(size, encyclopedia_ui.INSTRUMENT_DIAGRAM_GLYPH_RATIO))
    for glyph, place in doctrine.RING_JEWEL_SEATS:
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


# --- the three PICKER figures -------------------------------------------------
# The owner's three picker pages (2026-08-13): what a ring preset is,
# what the two world modes do, and what a pointer is. All three read the
# program's OWN tables — `data.rings.ring_presets`, `core.world`,
# `config.constants`/`config.palette` — so a preset added, a mode
# renamed or a pointer palette re-picked redraws the page rather than
# dating it.

class _Row:
    """One ROW figure's whole geometry, derived once from its entry in
    `encyclopedia_ui.INSTRUMENT_DIAGRAM_GRIDS` and the master width.

    Everything here is arithmetic, never a taste: the plate's height is
    the width over the declared aspect; the label stack, the top margin
    and the caption band take their declared shares of that height; and
    the tile RADIUS is exactly what those shares leave over. Add a label
    line and the circles shrink to make room — they can never overlap,
    because the same subtraction that places the labels sizes the
    circle."""

    __slots__ = ("size", "height", "columns", "radius", "pitch",
                 "label_px", "gap", "step", "caption_px", "caption_band")

    def __init__(self, kind: str, size: int):
        grid = encyclopedia_ui.INSTRUMENT_DIAGRAM_GRIDS[kind]
        self.size = size
        self.height = max(1, round(size / grid["aspect"]))
        self.columns = grid["columns"]
        self.pitch = size / self.columns
        self.label_px = round(
            self.height * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_LABEL_RATIO
        )
        self.gap = self.height * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_LABEL_GAP
        self.step = self.height * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_LABEL_STEP
        self.caption_px = round(
            self.height * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_CAPTION_RATIO
        )
        self.caption_band = grid.get(
            "caption_band", encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_CAPTION_BAND
        )
        spent = (
            encyclopedia_ui.INSTRUMENT_DIAGRAM_ROW_TOP
            + encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_LABEL_GAP
            + grid["label_lines"] * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_LABEL_STEP
            + self.caption_band
        )
        self.radius = self.height * max(0.02, (1.0 - spent) / 2.0)

    def center(self, index: int) -> QPointF:
        """The centre of tile `index` — one row, evenly pitched."""
        return QPointF(
            self.pitch * (index + 0.5),
            self.height * encyclopedia_ui.INSTRUMENT_DIAGRAM_ROW_TOP + self.radius,
        )


def _tile_labels(painter: QPainter, center: QPointF, row: "_Row",
                 lines: tuple) -> None:
    """A tile's caption stack, under its own circle — at the pixel size
    the row's own budget reserved for it."""
    font = QFont()
    font.setPixelSize(max(9, row.label_px))
    font.setBold(True)
    painter.setFont(font)
    for index, (line, color) in enumerate(lines):
        _text(painter,
              QPointF(center.x(),
                      center.y() + row.radius + row.gap + index * row.step),
              line, row.size, color=color, height=row.height)


def _ring_presets(_key: str, size: int) -> QPixmap:
    """The six bundled seatings, each on its own band. The dial has
    twenty-four hour seats; an OUTER leaves some of them EMPTY, and the
    preset's JEWELS take exactly those — every other seat wears its hour
    numeral. Drawn from `data.rings.ring_presets` and the outers'
    own position tuples, so a seventh preset would draw itself."""
    from data.rings import ring_presets

    row = _Row("ring_presets", size)
    pixmap, painter = _canvas(size, size / row.height)
    # The picker's own order — plain name sort, which is what the
    # Settings list shows (CHI, DOMY, Dollar, LOOP, Templar, The One).
    cards = [ring_presets()[name] for name in sorted(ring_presets())]
    radius = row.radius
    jewel_dot = radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_JEWEL_SEAT_RATIO
    numeral_dot = radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_NUMERAL_SEAT_RATIO
    for index, card in enumerate(cards):
        center = row.center(index)
        painter.setPen(_pen_px(
            _FAINT, radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_RING_PEN))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
        seats = set(card["positions"])
        painter.setPen(Qt.PenStyle.NoPen)
        for hour in range(1, dial.HOURS_PER_REVOLUTION + 1):
            jewel = hour in seats
            painter.setBrush(QColor(_ACCENT if jewel else _FAINT))
            dot = jewel_dot if jewel else numeral_dot
            painter.drawEllipse(
                _on_dial(center, radius, angles.ring_position_angle(hour)), dot, dot
            )
        count = len(card["jewels"])
        _tile_labels(painter, center, row, (
            (card["name"], _INK),
            (card["outer"], _FAINT),
            (f"{count} {'jewel' if count == 1 else 'jewels'}", _ACCENT),
        ))
    _caption(painter, size,
             "the outer's EMPTY fields carry the jewels · every other "
             "seat wears its hour numeral",
             height=row.height, font_px=row.caption_px, band=row.caption_band)
    painter.end()
    return pixmap


def _world_modes(_key: str, size: int) -> QPixmap:
    """The two modes side by side, at the same solar tilt: NOON_UP turns
    the STAR and leaves the band still, SKY_UP stands the star up and
    turns the BAND the other way. The offsets come from `core.world`
    itself, so the figure is the program's own arithmetic."""
    from core import world
    from core.numerals import fold_angle

    row = _Row("world_modes", size)
    pixmap, painter = _canvas(size, size / row.height)
    tilt = encyclopedia_ui.INSTRUMENT_DIAGRAM_SAMPLE_TILT_DEG
    radius = row.radius
    hour_font = QFont()
    hour_font.setPixelSize(max(9, row.label_px))
    hour_font.setBold(True)
    for index, mode in enumerate(dial.WORLD_MODES):
        center = row.center(index)
        offset = world.world_offset_deg(mode, tilt, True, 0.0)
        turn = world.pointer_rotation_deg(mode, tilt, True, 0.0)
        # The BAND: the four cardinal hours, carried by the world offset.
        painter.setPen(_pen_px(
            _FAINT, radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_BAND_PEN))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
        painter.setFont(hour_font)
        for hour in (12, 18, 24, 6):
            seat = angles.ring_position_angle(hour) + offset
            painter.setPen(_pen_px(
                _INK, radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_BAND_PEN))
            painter.drawLine(_on_dial(center, radius * 0.90, seat),
                             _on_dial(center, radius, seat))
            # Only the VERTICAL pair is named: 06h and 18h stand where
            # the two dials face each other, and two labels there would
            # be read as one. The figure's whole argument is vertical.
            # Both sit just INSIDE the band (clear of the star, whose
            # arms reach 0.62r): outside it, the 00h label landed on top
            # of the tile's own name once the row figure tightened the
            # gap under the circle.
            if hour in (12, 24):
                _text(painter, _on_dial(center, radius * 0.72, seat),
                      f"{hour % dial.HOURS_PER_REVOLUTION:02d}h", size,
                      height=row.height)
        # The STAR: the hexagram, turned by its own rotation.
        painter.setPen(_pen_px(
            _ACCENT, radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_STAR_PEN))
        for start in (0.0, 60.0):
            painter.drawPolygon([
                _on_dial(center, radius * 0.62, start + turn + step * 120.0)
                for step in range(3)
            ])
        painter.setPen(_pen_px(
            _ACCENT, radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_HAIRLINE_PEN))
        painter.drawLine(center, _on_dial(center, radius * 0.62, turn))
        # Where true solar noon ends up is the same seat in both modes —
        # that is the whole point of the two numbers cancelling.
        upright = _pen_px(
            _FAINT, radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_HAIRLINE_PEN)
        upright.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(upright)
        painter.drawLine(center, _on_dial(center, radius, 0.0))
        name, _, term = dial.WORLD_MODE_LABELS[mode].partition(" (")
        # Both numbers FOLDED to ±180 for the reader: `world_offset_deg`
        # answers modulo 360, and "349.24°" hides that this is the exact
        # negative of the star's own tilt, which is the whole lesson.
        # The two of them share ONE line: the row's height budget buys a
        # bigger circle with every label line it does not have to seat,
        # and these two numbers are read as a pair anyway.
        _tile_labels(painter, center, row, (
            (name, _INK),
            (f"({term}" if term else "", _FAINT),
            (f"star {fold_angle(turn):+.2f}°   "
             f"world {fold_angle(offset):+.2f}°", _ACCENT),
        ))
    _caption(painter, size,
             "never turned: the minute hand · the inner minute band · the "
             "year wheel · the moon cycle — true solar noon sits under the "
             "star's top arm in BOTH",
             height=row.height, font_px=row.caption_px, band=row.caption_band)
    painter.end()
    return pixmap


def _pointer_arms(painter: QPainter, center: QPointF, radius: float,
                  key: str, hues: tuple, outline: float) -> None:
    """One armed pointer's standing diamonds, at its own arm half-angle
    — and the Rose's three stars at their own 15° pitch."""
    half = constants.POINTER_ARM_HALF_ANGLE_DEG[key]
    waist = radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_ARM_WAIST_RATIO
    arms = constants.POINTER_POINTS[key]
    stars = (
        constants.ROSE_STAR_OFFSETS["primary"] if key == "rose" else (0.0,)
    )
    for star in stars:
        for index in range(arms):
            angle = star + index * 360.0 / arms
            painter.setPen(_pen_px(palette.ARM_OUTLINE, outline))
            painter.setBrush(QColor(hues[index % len(hues)]))
            painter.drawPolygon([
                center,
                _on_dial(center, waist, angle - half),
                _on_dial(center, radius, angle),
                _on_dial(center, waist, angle + half),
            ])


def _pointers(_key: str, size: int) -> QPixmap:
    """The seven pointers in the picker's own order — fewest divisions
    first. Each wears the hues its OWN default wheel ships
    (`palette.PALETTE_PRESETS`), so the figure changes when the palette
    does; the number under each is what a reader counts on the glass
    (`constants.POINTER_DIAL_COUNTS`), which for the Rose is
    twenty-four rays worn by eight hues."""
    row = _Row("pointers", size)
    pixmap, painter = _canvas(size, size / row.height)
    order = sorted(constants.POINTER_DIAL_COUNTS,
                   key=lambda key: constants.POINTER_DIAL_COUNTS[key])
    radius = row.radius
    outline = radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_TILE_OUTLINE_PEN
    for index, key in enumerate(order):
        center = row.center(index)
        hues = palette.PALETTE_PRESETS[(key, "primary")]
        if key in constants.POINTER_ARM_HALF_ANGLE_DEG:
            _pointer_arms(painter, center, radius, key, hues, outline)
        elif key == "calendar":
            # Twelve equal two-hour wedges — no arms at all.
            box = QRectF(center.x() - radius, center.y() - radius,
                         radius * 2, radius * 2)
            painter.setPen(_pen_px(palette.ARM_OUTLINE, outline))
            for index in range(constants.CALENDAR_WEDGES):
                painter.setBrush(QColor(hues[index % len(hues)]))
                painter.drawPie(box, int((90 - (index + 1) * constants.CALENDAR_WEDGE_DEG) * 16),
                                int(constants.CALENDAR_WEDGE_DEG * 16))
        else:
            # AURORA seats nothing: its hues run dawn to dusk across the
            # day's own arc, so a wheel of equal wedges would be a lie.
            strip = radius * encyclopedia_ui.INSTRUMENT_DIAGRAM_AURORA_STRIP_HEIGHT
            width = radius * 2 / len(hues)
            painter.setPen(_pen_px(palette.ARM_OUTLINE, outline))
            for band, hue in enumerate(hues):
                painter.setBrush(QColor(hue))
                painter.drawRect(QRectF(
                    center.x() - radius + band * width,
                    center.y() - strip / 2, width, strip,
                ))
        # The NAME and the COUNT only. The wheel names (Court, Family,
        # Genesis…) are longer than a tile is wide and belong to the
        # article, which lists every one of them per pointer.
        _tile_labels(painter, center, row, (
            (constants.POINTER_DISPLAY_NAMES[key], _INK),
            (str(constants.POINTER_DIAL_COUNTS[key]), _ACCENT),
        ))
    _caption(painter, size,
             "the parts each wheel cuts the dial into · Palette gives "
             "its meaning, Shape its outline",
             height=row.height, font_px=row.caption_px, band=row.caption_band)
    painter.end()
    return pixmap


# --- the CHI band ---------------------------------------------------------

def _chi(_key: str, size: int) -> QPixmap:
    """The composed CHI band itself, not a diagram OF it: the real
    `"full"` outer plate (`constants.RING_OUTERS["full"]`) with its
    hour numerals built by the SAME fidelity engine the dial's own ring
    composes with (`render.numeral_bands.band_plate`, the plate the
    `dial`/`ring_jewels` figures only sketch the geometry of) — every
    hour but the 24th, which the letter owns — and the X master
    recolored to CHI's own ceramic thematic shade
    (`constants.RING_THEMATIC_SHADES["CHI"]`) through the SAME asset
    cache the dial's own ring jewels recolor through
    (`render.assets.shared_cache`, THE ONE COPY RULE). Root Rule #19
    rules out a hand-drawn stand-in here specifically: the article is
    ABOUT what the porcelain finish looks like, so only the real
    recolored pixels teach it — never `jewel_metal_file`'s deferred
    door (built for the live dial's first-paint budget), because a
    plate cached once at import time must never freeze on the GOLD
    fallback it returns before a background warm-up finishes."""
    from render.assets import shared_cache
    from render.numeral_bands import BandSpec, band_plate

    pixmap, painter = _canvas(size)
    center = QPointF(size / 2, size / 2)
    radius = size / 2.0

    outer_spec = BandSpec(
        band="outer", pixels=size, dpr=1.0,
        face=dial.NUMERAL_OUTER_FACE_DEFAULT,
        size_units=float(dial.NUMERAL_OUTER_SIZE_DEFAULT),
        jewel_hours=(24,),
    )
    painter.drawImage(QPointF(0, 0), band_plate(outer_spec))

    with paths.display(paths.display_context(
        metal_shades={"thematic": constants.RING_THEMATIC_SHADES["CHI"]}
    )):
        glyph = shared_cache().pixmap_by_height(
            letter_plates.plate_path("X"),
            2 * radius * dial.RING_JEWEL_ART_SCALE, 1.0, metal="thematic",
        )
    # Letter plates carry no WORKING-SET ceiling (owner bar 2026-08-09),
    # so `pixmap_by_height` cannot return None here — asserted, not
    # silently skipped, for the same reason the docstring above already
    # rules out a deferred stand-in: this figure is cached once at
    # import time and must show the real pixels or fail loudly, never a
    # blank glyph nobody notices.
    assert glyph is not None, "the CHI band's X glyph must resolve eagerly"
    theta = angles.ring_position_angle(24)
    painter.save()
    painter.translate(_on_dial(center, radius * dial.RING_JEWEL_RADIUS_FRACTION, theta))
    painter.rotate(angles.readable_rotation_deg(theta))
    painter.drawPixmap(QPointF(-glyph.width() / 2.0, -glyph.height() / 2.0), glyph)
    painter.restore()

    painter.setFont(_font(size))
    _caption(painter, size,
             "the full outer band, computed live · X in its own "
             "ceramic thematic shade")
    painter.end()
    return pixmap


# --- the deep-time figure -----------------------------------------------------

def _oscillations(_key: str, size: int) -> QPixmap:
    """The Great Oscillations: the La2004 amplitude envelope the
    Observatory already plots, drawn here from the SAME bundle. A
    painted version of this chart would be a picture of a number that
    changes when the bundle changes — the plainest Rule #19 case in the
    whole book."""
    from data.observatory import shared_observatory

    pixmap, painter = _canvas(size)
    envelope = shared_observatory().laskar_envelope()
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
    "ring_jewels": _ring_jewels,
    "ring_presets": _ring_presets,
    "pointers": _pointers,
    "world_modes": _world_modes,
    "oscillations": _oscillations,
    "chi": _chi,
}
# The KEY names the figure here, not the kind: all twelve live under the
# one kind "instrument".
_BANK = DiagramBank(_DRAWERS, key_by="key", answers=("instrument",))

plate = _BANK.plate
kinds = _BANK.kinds
