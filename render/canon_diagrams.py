"""The canon's TABLE and JOURNEY figures, drawn by the program.

The second wave of the computed-diagram verdict (owner 2026-07-29). Where
[Cube Diagrams](cube_diagrams.md) draws the Cube's own geometry, this
module draws what the rest of the doctrine is shaped like:

- the two four-station JOURNEYS on the hexagram's arms, and the two
  ciphers that read the same roads as words;
- the DOUBLE TRINITY's two triangles on those same six arms;
- the sixty-five TERMS as the grid they are, and the three figure SETS;
- the twenty-four FIELDS as the table the article describes.

Every one of them is data (`config.doctrine`, `config.cube`,
`config.archetypes`) — nothing here is decorative, and nothing parses an
article to find its own content.

Layer: render (Qt allowed; no wall clock, no settings). Documentation:
canon_diagrams.md.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap

from config import archetypes, cube, defaults, doctrine, palette
from core import angles

_INK = palette.THEME_COLORS["text_primary"]
_MUTED = palette.THEME_COLORS["text_secondary"]
_LIGHT_HUE = palette.ROSE_PALETTE[0]        # 12h yellow — the bright road
_DARK_HUE = palette.ROSE_PALETTE[2]         # 18h red — the dark road


def _canvas(size: int) -> tuple[QPixmap, QPainter]:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    return pixmap, painter


def _font(size: int, ratio: float, bold: bool = True) -> QFont:
    font = QFont()
    font.setPixelSize(max(9, round(size * ratio)))
    font.setBold(bold)
    return font


def _arm_point(centre: QPointF, radius: float, hour: int) -> QPointF:
    """Where an arm's hour stands on the dial — through `core.angles`,
    the one mapping every fixed ring hour already shares (Rule #5), so a
    station and the dial's own seat can never disagree."""
    theta = math.radians(angles.ring_position_angle(hour) - 90.0)
    return QPointF(
        centre.x() + radius * math.cos(theta),
        centre.y() + radius * math.sin(theta),
    )


def _draw_arms(painter: QPainter, centre: QPointF, radius: float,
               size: int) -> None:
    """The six hexagram arms, faint — the room both journeys walk in."""
    pen = QPen(QColor(_MUTED))
    pen.setWidthF(max(1.0, size * 0.002))
    painter.setPen(pen)
    painter.setOpacity(defaults.CUBE_DIAGRAM_FRAME_OPACITY)
    for hour in (12, 16, 20, 24, 4, 8):
        painter.drawLine(centre, _arm_point(centre, radius, hour))
    painter.setOpacity(1.0)


def _draw_journey(painter: QPainter, centre: QPointF, radius: float,
                  size: int, stations, hue: str, inward: float) -> None:
    """One four-station road: the walk drawn in order, each stop a filled
    node with its own name and cipher letter. `inward` pulls a road
    slightly off the arm so the two never overdraw each other where they
    share an hour — which they do twice, and that sharing IS the
    chiasm."""
    ring = radius * inward
    points = [_arm_point(centre, ring, station.hour) for station in stations]
    pen = QPen(QColor(hue))
    pen.setWidthF(max(1.4, size * 0.006))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    for start, end in zip(points, points[1:]):
        painter.drawLine(start, end)
    painter.setFont(_font(size, defaults.CANON_DIAGRAM_LABEL_RATIO))
    metrics = painter.fontMetrics()
    for station, point in zip(stations, points):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(hue))
        painter.drawEllipse(point, size * 0.012, size * 0.012)
        text = f"{station.letter} · {station.name}"
        width = metrics.horizontalAdvance(text)
        push = size * 0.055
        length = math.hypot(point.x() - centre.x(), point.y() - centre.y()) or 1
        anchor = QPointF(
            point.x() + (point.x() - centre.x()) / length * push,
            point.y() + (point.y() - centre.y()) / length * push,
        )
        painter.setPen(QPen(QColor(_INK)))
        painter.drawText(
            _clamped(QRectF(
                anchor.x() - width / 2, anchor.y() - metrics.height() / 2,
                width, metrics.height(),
            ), size),
            Qt.AlignmentFlag.AlignCenter, text,
        )


def _clamped(box: QRectF, size: int) -> QRectF:
    """Keep a label on the plate (the same law the cube diagrams learned
    the hard way — a name pushed off the edge is silently lost)."""
    margin = defaults.CUBE_DIAGRAM_MARGIN_PX
    left = min(max(box.left(), margin), size - margin - box.width())
    top = min(max(box.top(), margin), size - margin - box.height())
    return QRectF(left, top, box.width(), box.height())


def crosses(page: str, size: int) -> QPixmap:
    """THE CHIASM — the bright road and the dark road on the same six
    arms, each ending in the other's hour. One drawer serves all three
    cross pages: the stations themselves, the English mnemonic (FALL /
    STAR) and the assembled cipher (DOMY / SAFE) are the SAME two roads
    read three ways, which is precisely what the articles argue."""
    readings = doctrine.CROSS_PAGES.get(page)
    if readings is None:
        return QPixmap()
    bright, dark = readings
    pixmap, painter = _canvas(size)
    centre = QPointF(size / 2, size / 2)
    radius = size * defaults.CANON_DIAGRAM_RING_RATIO
    _draw_arms(painter, centre, radius, size)
    _draw_journey(painter, centre, radius, size, dark, _DARK_HUE, 0.74)
    _draw_journey(painter, centre, radius, size, bright, _LIGHT_HUE, 1.0)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette.THEME_COLORS["accent"]))
    painter.drawEllipse(centre, size * 0.010, size * 0.010)
    painter.end()
    return pixmap


def double_trinity(size: int) -> QPixmap:
    """The two triangles on the six arms — the Court upright, Genesis
    inverted — and the Council they make together. Drawn from the dial's
    OWN wheels (`config.archetypes`), so the page and the pointer can
    never drift apart."""
    pixmap, painter = _canvas(size)
    centre = QPointF(size / 2, size / 2)
    radius = size * defaults.CANON_DIAGRAM_RING_RATIO
    for key, hue in (("trinity_primary", _LIGHT_HUE),
                     ("trinity_genesis", _DARK_HUE)):
        wheel = archetypes.ARCHETYPES.get(key) or {}
        figures = wheel.get("figures") or ()
        # A wheel figure's `angle` is ALREADY the dial angle (degrees
        # clockwise from the top — `config.archetypes` seats The One's
        # Judge face at 0.0, which is noon). Only Qt's own quarter-turn
        # is taken off; adding the hour-space offset here once put the
        # Court on its head.
        points = [
            QPointF(
                centre.x() + radius * math.cos(
                    math.radians(figure["angle"] - 90.0)),
                centre.y() + radius * math.sin(
                    math.radians(figure["angle"] - 90.0)),
            )
            for figure in figures
        ]
        pen = QPen(QColor(hue))
        pen.setWidthF(max(1.4, size * 0.006))
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        for index, point in enumerate(points):
            painter.drawLine(point, points[(index + 1) % len(points)])
        painter.setFont(_font(size, defaults.CANON_DIAGRAM_LABEL_RATIO))
        metrics = painter.fontMetrics()
        for figure, point in zip(figures, points):
            text = f"{figure['name']} · {figure['row2']}"
            width = metrics.horizontalAdvance(text)
            push = size * 0.055
            length = math.hypot(
                point.x() - centre.x(), point.y() - centre.y()) or 1
            painter.setPen(QPen(QColor(_INK)))
            painter.drawText(
                _clamped(QRectF(
                    point.x() + (point.x() - centre.x()) / length * push
                    - width / 2,
                    point.y() + (point.y() - centre.y()) / length * push
                    - metrics.height() / 2,
                    width, metrics.height(),
                ), size),
                Qt.AlignmentFlag.AlignCenter, text,
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(hue))
            painter.drawEllipse(point, size * 0.012, size * 0.012)
    painter.end()
    return pixmap


def _draw_table(painter: QPainter, size: int, rows, headers) -> None:
    """One table drawer for every table page (Rule #5): a header row,
    then one line per row, columns evenly split, the first column bold."""
    columns = len(headers)
    margin = size * defaults.CANON_DIAGRAM_TABLE_MARGIN
    width = (size - 2 * margin) / columns
    height = (size - 2 * margin) / (len(rows) + 1)
    painter.setFont(_font(size, defaults.CANON_DIAGRAM_TABLE_RATIO))
    metrics = painter.fontMetrics()
    for index, header in enumerate(headers):
        painter.setPen(QPen(QColor(palette.THEME_COLORS["accent"])))
        painter.drawText(
            QRectF(margin + index * width, margin, width, height),
            Qt.AlignmentFlag.AlignCenter, header,
        )
    pen = QPen(QColor(_MUTED))
    pen.setWidthF(max(1.0, size * 0.0015))
    for row_index, row in enumerate(rows, start=1):
        top = margin + row_index * height
        painter.setPen(pen)
        painter.setOpacity(defaults.CUBE_DIAGRAM_FRAME_OPACITY)
        painter.drawLine(
            QPointF(margin, top), QPointF(size - margin, top),
        )
        painter.setOpacity(1.0)
        for index, cell in enumerate(row):
            painter.setPen(QPen(QColor(_INK if index == 0 else _MUTED)))
            box = QRectF(margin + index * width, top, width, height)
            text = metrics.elidedText(
                str(cell), Qt.TextElideMode.ElideRight, round(width * 0.94),
            )
            painter.drawText(box, Qt.AlignmentFlag.AlignCenter, text)


def sixty_five_terms(size: int) -> QPixmap:
    """The canon's own count, drawn as the grid it is: thirteen axis
    names, twenty-six luminous readings, twenty-six falls. 13 + 26 + 26 =
    65, and the page can be counted with a finger."""
    pixmap, painter = _canvas(size)
    rows = [
        (axis.name, axis.cold.luminous, axis.cold.fallen,
         axis.warm.luminous, axis.warm.fallen)
        for axis in cube.AXES
    ]
    _draw_table(
        painter, size, rows,
        ("Axis", "cold", "its fall", "warm", "its fall"),
    )
    painter.end()
    return pixmap


def three_sets(size: int) -> QPixmap:
    """Every seat filled three times — archetypal, historical, modern.
    The three sets are drawn as the three parallel columns they are, with
    the sacred trio standing above them as the one seat all three sets
    agree on."""
    pixmap, painter = _canvas(size)
    rows = [
        ("Archetypal", "biblical, mythological, classical-literary"),
        ("Historical", "real persons, named and dated"),
        ("Modern", "fantasy, film, comics"),
        ("—", ""),
        ("The sacred trio", " · ".join(cube.SACRED_TRIO_NAMES)),
    ]
    _draw_table(painter, size, rows, ("Set", "what fills it"))
    painter.end()
    return pixmap


def union_fields(size: int) -> QPixmap:
    """The twenty-four: three persons, four offices each, every office
    paired with the process it works on its object — an act and its
    effect, read as a table because that is what it is."""
    pixmap, painter = _canvas(size)
    rows = []
    for person, fields in doctrine.UNION_FIELDS.items():
        for index, field in enumerate(fields):
            rows.append((
                person if index == 0 else "",
                field.office,
                field.process,
            ))
    _draw_table(painter, size, rows, ("Person", "office", "process"))
    painter.end()
    return pixmap


_DRAWERS = {
    "crosses": crosses,
    "trinity": lambda _key, size: double_trinity(size),
    "terms": lambda _key, size: sixty_five_terms(size),
    "sets": lambda _key, size: three_sets(size),
    "fields": lambda _key, size: union_fields(size),
}

_CACHE: dict = {}


def plate(kind: str, key: str, size: int) -> QPixmap:
    """The diagram for one page, cached per (kind, key, size)."""
    cached = _CACHE.get((kind, key, size))
    if cached is None:
        drawer = _DRAWERS.get(kind)
        if drawer is None:
            return QPixmap()
        cached = drawer(key, size)
        _CACHE[(kind, key, size)] = cached
    return cached


def kinds() -> tuple:
    return tuple(_DRAWERS)
