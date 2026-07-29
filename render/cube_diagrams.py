"""The Cube's own DIAGRAMS, drawn by the program (owner verdict
2026-07-29).

The Session 27 coverage law says every article carries an image. Twenty
three Encyclopedia pages are COMPOSITIONS, not scenes — an axis is its
two poles through the centre, the term grid is a table, a cipher is a
word — and the canon exempted exactly those from generation in writing
(CUBE.md, Session 25, under root Rule #19: compute, don't generate).
The owner's verdict closed the circle: they are neither generated nor
left blank, they are DRAWN HERE, live, from `config.cube`'s own
coordinates. Change a term in the canon table and every diagram that
shows it changes with it — which is the whole point of computing an
asset instead of storing one.

This module holds the CUBE GEOMETRY diagrams (the isometric cube, one
axis lit, all thirteen, the hexagram projection, the banknote axes).
The tables and word-figures live next door in
[Canon Diagrams](canon_diagrams.md).

Layer: render (Qt allowed; no wall clock, no settings). Documentation:
cube_diagrams.md.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap

from config import cube, defaults

# THE ISOMETRIC EYE. A cube of 27 cells read on a flat page needs a
# projection that never lets two different cells land on the same point;
# the classic 30° isometric does that for every integer coordinate here,
# and keeps the three axes visually equal — which matters, because the
# canon insists no axis outranks another.
_COS30 = math.cos(math.radians(30.0))
_SIN30 = math.sin(math.radians(30.0))

_ONE_HUE = defaults.THEME_COLORS["accent"]


def _project(coords, unit: float) -> QPointF:
    """(x, y, z) -> the point on the page. +z is UP (the Self-Regard
    axis stands vertical, as every drawing of the Cube in CUBE.md has
    it); x and y fall away to the right and left."""
    x, y, z = coords
    return QPointF(
        (x - y) * _COS30 * unit,
        (x + y) * _SIN30 * unit - z * unit,
    )


def _hue(coords) -> QColor:
    """A cell's own colour. The six face poles wear their sealed Rose
    hue (`cube.ROSE_POLE_HUE`); the centre wears the dial's accent; every
    other cell is a blend of the poles it stands between — computed, so
    a re-tuned palette moves the whole cube at once."""
    if coords == (0, 0, 0):
        return QColor(_ONE_HUE)
    index = cube.ROSE_POLE_HUE.get(coords)
    if index is not None:
        return QColor(defaults.ROSE_PALETTE[index])
    reds = greens = blues = count = 0
    for axis, value in enumerate(coords):
        if value == 0:
            continue
        pole = [0, 0, 0]
        pole[axis] = value
        pole_index = cube.ROSE_POLE_HUE.get(tuple(pole))
        if pole_index is None:
            continue
        colour = QColor(defaults.ROSE_PALETTE[pole_index])
        reds += colour.red()
        greens += colour.green()
        blues += colour.blue()
        count += 1
    if not count:
        return QColor(_ONE_HUE)
    return QColor(reds // count, greens // count, blues // count)


def _canvas(size: int) -> tuple[QPixmap, QPainter]:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    painter.translate(size / 2, size / 2)
    return pixmap, painter


def _label_font(unit: float) -> QFont:
    font = QFont()
    font.setPixelSize(max(9, round(unit * defaults.CUBE_DIAGRAM_LABEL_RATIO)))
    font.setBold(True)
    return font


def _draw_frame(painter: QPainter, unit: float) -> None:
    """The cube's twelve edges, faint — the room the axes live in."""
    pen = QPen(QColor(defaults.THEME_COLORS["text_secondary"]))
    pen.setWidthF(max(1.0, unit * 0.012))
    painter.setPen(pen)
    painter.setOpacity(defaults.CUBE_DIAGRAM_FRAME_OPACITY)
    corners = [
        (x, y, z)
        for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)
    ]
    for start in corners:
        for axis in range(3):
            if start[axis] != -1:
                continue
            end = list(start)
            end[axis] = 1
            painter.drawLine(_project(start, unit), _project(tuple(end), unit))
    painter.setOpacity(1.0)


def _draw_cells(painter: QPainter, unit: float, lit=()) -> None:
    """All twenty-seven cells as dots — the lit ones full, the rest
    faint, so a single axis reads at a glance against its own cube."""
    lit = set(lit)
    for x in (-1, 0, 1):
        for y in (-1, 0, 1):
            for z in (-1, 0, 1):
                coords = (x, y, z)
                point = _project(coords, unit)
                radius = unit * (
                    defaults.CUBE_DIAGRAM_NODE_RATIO * (
                        1.6 if coords in lit else 1.0
                    )
                )
                painter.setOpacity(1.0 if coords in lit else
                                   defaults.CUBE_DIAGRAM_DIM_OPACITY)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(_hue(coords))
                painter.drawEllipse(point, radius, radius)
    painter.setOpacity(1.0)


def _draw_axis_line(painter: QPainter, unit: float, cold, warm,
                    strong: bool = True) -> None:
    pen = QPen(_hue(warm if strong else cold))
    pen.setWidthF(max(1.2, unit * (0.030 if strong else 0.014)))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setOpacity(1.0 if strong else defaults.CUBE_DIAGRAM_DIM_OPACITY)
    painter.drawLine(_project(cold, unit), _project(warm, unit))
    painter.setOpacity(1.0)


def _draw_end_label(painter: QPainter, unit: float, coords, text: str) -> None:
    """A pole's name, pushed OUTWARD from the centre so it never sits on
    the cube it belongs to."""
    point = _project(coords, unit)
    outward = QPointF(point)
    length = math.hypot(outward.x(), outward.y()) or 1.0
    push = unit * defaults.CUBE_DIAGRAM_LABEL_PUSH
    anchor = QPointF(
        point.x() + outward.x() / length * push,
        point.y() + outward.y() / length * push,
    )
    painter.setFont(_label_font(unit))
    painter.setPen(QPen(QColor(defaults.THEME_COLORS["text_primary"])))
    metrics = painter.fontMetrics()
    width = metrics.horizontalAdvance(text)
    height = metrics.height()
    box = QRectF(
        anchor.x() - width / 2, anchor.y() - height / 2, width, height,
    )
    painter.drawText(_clamped(box, painter), Qt.AlignmentFlag.AlignCenter, text)


def _clamped(box: QRectF, painter: QPainter) -> QRectF:
    """Keep a label inside the plate. The painter is centred, so the page
    runs from -half to +half; a long pole name pushed outward from a
    corner would otherwise be drawn off the edge and silently lost —
    which is exactly what the first render of these diagrams did."""
    device = painter.device()
    half_w = device.width() / 2 - defaults.CUBE_DIAGRAM_MARGIN_PX
    half_h = device.height() / 2 - defaults.CUBE_DIAGRAM_MARGIN_PX
    left = min(max(box.left(), -half_w), half_w - box.width())
    top = min(max(box.top(), -half_h), half_h - box.height())
    return QRectF(left, top, box.width(), box.height())


def axis(name: str, size: int) -> QPixmap:
    """ONE axis lit inside its own cube — the two poles named, the line
    through The One drawn, the other twelve axes left as faint dots.

    This is the page the canon refused to generate art for, and the
    reason it gave is exactly what the drawing shows: the axis IS its
    two ends through the centre."""
    entry = next((a for a in cube.AXES if a.name == name), None)
    if entry is None:
        return QPixmap()
    pixmap, painter = _canvas(size)
    unit = size * defaults.CUBE_DIAGRAM_UNIT_RATIO
    _draw_frame(painter, unit)
    _draw_axis_line(painter, unit, entry.cold.coords, entry.warm.coords)
    _draw_cells(painter, unit, lit=(entry.cold.coords, entry.warm.coords,
                                    (0, 0, 0)))
    _draw_end_label(painter, unit, entry.cold.coords, entry.cold.luminous)
    _draw_end_label(painter, unit, entry.warm.coords, entry.warm.luminous)
    _draw_end_label(painter, unit, (0, 0, 0), cube.THE_ONE.luminous)
    painter.end()
    return pixmap


def pole(name: str, size: int) -> QPixmap:
    """ONE END of an axis lit inside its own cube — the seat named, its
    own line drawn faintly through the centre to the pole it answers.

    The six face poles used to read the Character wheel's lancets, and
    two of them (Composure, Vigor) never had one: their axis is the
    depth the flat wheel drops. The owner sent that whole family to the
    rotating 3D previewer (decree 2026-07-29), so until it lands the
    page shows where the seat STANDS — which is the one thing a flat
    figure can honestly say about a 3D position."""
    entry = next(
        (
            (a, end)
            for a in cube.AXES
            for end in (a.cold, a.warm)
            if end.luminous == name
        ),
        None,
    )
    if entry is None:
        return QPixmap()
    axis_entry, end = entry
    other = axis_entry.warm if end is axis_entry.cold else axis_entry.cold
    pixmap, painter = _canvas(size)
    unit = size * defaults.CUBE_DIAGRAM_UNIT_RATIO
    _draw_frame(painter, unit)
    _draw_axis_line(painter, unit, end.coords, other.coords)
    _draw_cells(painter, unit, lit=(end.coords, (0, 0, 0)))
    _draw_end_label(painter, unit, end.coords, end.luminous)
    _draw_end_label(painter, unit, (0, 0, 0), cube.THE_ONE.luminous)
    painter.end()
    return pixmap


def whole_cube(size: int) -> QPixmap:
    """The Cube itself — twenty-seven cells in their own hues, the
    centre lit, no axis singled out."""
    pixmap, painter = _canvas(size)
    unit = size * defaults.CUBE_DIAGRAM_UNIT_RATIO
    _draw_frame(painter, unit)
    _draw_cells(painter, unit, lit=[(0, 0, 0)])
    _draw_end_label(painter, unit, (0, 0, 0), cube.THE_ONE.luminous)
    painter.end()
    return pixmap


def thirteen_axes(size: int) -> QPixmap:
    """All thirteen lines through The One at once — the figure the
    doctrine page argues: three through the faces, four through the
    corners, six through the edges."""
    pixmap, painter = _canvas(size)
    unit = size * defaults.CUBE_DIAGRAM_UNIT_RATIO
    _draw_frame(painter, unit)
    for entry in cube.AXES:
        _draw_axis_line(
            painter, unit, entry.cold.coords, entry.warm.coords, strong=False,
        )
    _draw_cells(painter, unit, lit=[(0, 0, 0)])
    painter.end()
    return pixmap


def hexagram_projection(size: int) -> QPixmap:
    """What the Cube becomes when the eye stands ON the Sacred Axis: the
    six remaining corners fall on a hexagram, the two sacred ends
    collapse into the centre — the page's whole claim, drawn by looking
    down that axis instead of describing it."""
    pixmap, painter = _canvas(size)
    unit = size * defaults.CUBE_DIAGRAM_UNIT_RATIO
    radius = unit * 1.5
    # The six non-sacred corners, in ring order around the diagonal.
    ring = [
        (1, 1, -1), (1, -1, -1), (1, -1, 1),
        (-1, -1, 1), (-1, 1, 1), (-1, 1, -1),
    ]
    points = [
        QPointF(radius * math.cos(math.radians(-90 + 60 * index)),
                radius * math.sin(math.radians(-90 + 60 * index)))
        for index in range(6)
    ]
    for step in (0, 1):
        pen = QPen(QColor(defaults.ROSE_PALETTE[0 if step == 0 else 6]))
        pen.setWidthF(max(1.2, unit * 0.022))
        painter.setPen(pen)
        triangle = [points[step], points[step + 2], points[step + 4]]
        for index in range(3):
            painter.drawLine(triangle[index], triangle[(index + 1) % 3])
    for coords, point in zip(ring, points):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_hue(coords))
        painter.drawEllipse(point, unit * 0.09, unit * 0.09)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(_ONE_HUE))
    painter.drawEllipse(QPointF(0, 0), unit * 0.12, unit * 0.12)
    painter.setFont(_label_font(unit))
    painter.setPen(QPen(QColor(defaults.THEME_COLORS["text_primary"])))
    for coords, point in zip(ring, points):
        name = next(
            (cell.luminous
             for entry in cube.AXES
             for cell in (entry.cold, entry.warm)
             if cell.coords == coords),
            "",
        )
        metrics = painter.fontMetrics()
        width = metrics.horizontalAdvance(name)
        push = unit * defaults.CUBE_DIAGRAM_LABEL_PUSH
        length = math.hypot(point.x(), point.y()) or 1.0
        painter.drawText(
            _clamped(QRectF(
                point.x() + point.x() / length * push - width / 2,
                point.y() + point.y() / length * push
                - metrics.height() / 2,
                width, metrics.height(),
            ), painter),
            Qt.AlignmentFlag.AlignCenter, name,
        )
    painter.end()
    return pixmap


def banknote_axes(size: int) -> QPixmap:
    """The three axes the banknote's own figure carries — the same cube,
    read through the Dollar's eye: the vertical Self-Regard, and the two
    that cross it on the pyramid's base."""
    pixmap, painter = _canvas(size)
    unit = size * defaults.CUBE_DIAGRAM_UNIT_RATIO
    _draw_frame(painter, unit)
    primary = [a for a in cube.AXES if a.name in (
        "Activation", "Moral Scope", "Self-Regard",
    )]
    for entry in primary:
        _draw_axis_line(painter, unit, entry.cold.coords, entry.warm.coords)
    lit = [c for entry in primary
           for c in (entry.cold.coords, entry.warm.coords)]
    _draw_cells(painter, unit, lit=lit + [(0, 0, 0)])
    for entry in primary:
        _draw_end_label(painter, unit, entry.cold.coords, entry.cold.luminous)
        _draw_end_label(painter, unit, entry.warm.coords, entry.warm.luminous)
    painter.end()
    return pixmap


# The ONE dispatcher every page goes through — an entry declares
# `"diagram": (kind, key)` and the reader asks here, so no screen knows
# which drawer answers which kind (Rule #5).
_DRAWERS = {
    "axis": axis,
    "pole": pole,
    "cube": lambda _key, size: whole_cube(size),
    "axes": lambda _key, size: thirteen_axes(size),
    "hexagram": lambda _key, size: hexagram_projection(size),
    "banknote": lambda _key, size: banknote_axes(size),
}

_CACHE: dict = {}


def plate(kind: str, key: str, size: int) -> QPixmap:
    """The diagram for one page, cached per (kind, key, size). Drawing
    is cheap, but a page turn must never repaint the same figure twice —
    the reader re-fits on every resize."""
    cached = _CACHE.get((kind, key, size))
    if cached is None:
        drawer = _DRAWERS.get(kind)
        if drawer is None:
            return QPixmap()
        cached = drawer(key, size)
        _CACHE[(kind, key, size)] = cached
    return cached


def kinds() -> tuple:
    """Every kind this module answers — the coverage test reads it so a
    page can never declare a diagram nobody draws."""
    return tuple(_DRAWERS)
