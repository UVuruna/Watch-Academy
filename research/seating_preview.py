"""Offscreen previews of the two Session-26 seatings, for the owner's
eyes (CUBE.md §The Seatings). Not part of the app — a research renderer
that draws what `core.cube_seating` computes, so the geometry can be
LOOKED at before any pointer is wired to it.

    python research/seating_preview.py            # writes research/seating/*.png
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QPointF, QRectF, Qt                # noqa: E402
from PySide6.QtGui import (QColor, QFont, QFontDatabase,       # noqa: E402
                           QImage, QPainter, QPen, QPolygonF)
from PySide6.QtWidgets import QApplication                     # noqa: E402

from config import constants, cube, defaults                   # noqa: E402
from core import cube_seating as seating                       # noqa: E402

SIZE = 1400
BACKDROP = QColor("#0B0D12")
INK = QColor("#EDEFF5")
MUTED = QColor("#8A93A6")
OUT_DIR = Path(__file__).resolve().parent / "seating"
FONT_FAMILY = "Segoe UI"
# The QT_QPA_PLATFORM=offscreen plugin ships an EMPTY font database on
# this machine — every glyph renders as a tofu box, silently. The script
# therefore paints under the native plugin (into a QImage; no window is
# ever shown) and, if it is ever driven truly headless, registers a
# system TTF rather than writing an unreadable picture.
FALLBACK_FONT = Path("C:/Windows/Fonts/segoeui.ttf")


def _at(centre: QPointF, angle_deg: float, radius: float) -> QPointF:
    """Degrees CLOCKWISE from the top — the project's dial convention."""
    rad = math.radians(angle_deg)
    return QPointF(centre.x() + radius * math.sin(rad),
                   centre.y() - radius * math.cos(rad))


def _diamond(centre: QPointF, angle: float, tip: float, half: float) -> QPolygonF:
    """One octa arm: tip at the star radius, inner vertices at
    tip / 2cos(half) — the Rose's own sealed arm shape."""
    inner = tip / (2.0 * math.cos(math.radians(half)))
    return QPolygonF([centre, _at(centre, angle - half, inner),
                      _at(centre, angle, tip), _at(centre, angle + half, inner)])


def _radial_label(painter: QPainter, centre: QPointF, angle: float, radius: float,
                  lines: list[tuple[str, QColor, int]]) -> None:
    """A label that lies ALONG its arm — the only layout that gives twelve
    wedges room near the axle. Arms pointing into the lower half are
    turned a further 180° so the text never stands on its head."""
    flipped = 90.0 < angle % 360.0 < 270.0
    painter.save()
    painter.translate(centre)
    painter.rotate(angle + (180.0 if flipped else 0.0))
    _label(painter, QPointF(0.0, radius if flipped else -radius), lines,
           width=radius * 0.95, clamp=False)
    painter.restore()


def _canvas() -> tuple[QImage, QPainter]:
    image = QImage(SIZE, SIZE, QImage.Format_ARGB32)
    image.fill(BACKDROP)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    return image, painter


def _label(painter: QPainter, point: QPointF, lines: list[tuple[str, QColor, int]],
           align=Qt.AlignHCenter, width: float = 320.0,
           clamp: bool = True) -> None:
    """Rows of text hung on a point. The horizontal alignment says which
    way the text GROWS, so rim labels can run outward instead of over
    their neighbours. `clamp` is off inside a rotated frame, where the
    canvas bounds mean nothing."""
    left = {Qt.AlignHCenter: point.x() - width / 2,
            Qt.AlignLeft: point.x(),
            Qt.AlignRight: point.x() - width}[align]
    if clamp:
        left = min(max(left, 8.0), SIZE - width - 8.0)   # never run off the canvas
    top = point.y() - sum(size + 5 for _, _, size in lines) / 2
    for text, color, size in lines:
        font = QFont(FONT_FAMILY, size)
        font.setBold(color is INK or size >= 15)
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(QRectF(left, top, width, size + 8),
                         align | Qt.AlignVCenter, text)
        top += size + 5


def draw_rose() -> QImage:
    """Rose-24: three octa stars 15° apart, one human seat per ray, the
    three sacred seats at the axle."""
    image, painter = _canvas()
    centre = QPointF(SIZE / 2, SIZE / 2 + 14)
    tip = SIZE * 0.245
    half = constants.POINTER_ARM_HALF_ANGLE_DEG["rose"]
    # the three stars' labels stand at three radii, so a hue's triple of
    # neighbouring rays never writes over itself
    label_reach = {"0": SIZE * 0.275, "+15": SIZE * 0.355, "-15": SIZE * 0.435}

    # bottom -> top, so the 0° star (the true hours) stands on top
    for star in ("-15", "+15", "0"):
        for seat in seating.rose_seating():
            if seat.star != star:
                continue
            hue = QColor(defaults.ROSE_PALETTE[seat.hue_index])
            hue.setAlphaF(0.92 if star == "0" else 0.72)
            painter.setBrush(hue)
            painter.setPen(QPen(QColor(defaults.ROSE_ARM_OUTLINE), 2.0))
            painter.drawPolygon(_diamond(centre, seat.angle_deg, tip, half))

    # Three rays 15° apart can hang their labels on the same line, so the
    # anchors are laid out as a LADDER per side: sorted by height, then
    # pushed apart to a minimum gap.
    gap, placed = 62.0, {}
    for side in (range(1, 12), range(13, 24), (0, 12)):
        rung = sorted(side, key=lambda ray: _at(centre, ray * seating.RAY_STEP_DEG,
                                                label_reach[seating.ray_star(ray)]).y())
        top = None
        for ray in rung:
            anchor = _at(centre, ray * seating.RAY_STEP_DEG,
                         label_reach[seating.ray_star(ray)])
            if top is not None and anchor.y() < top + gap:
                anchor.setY(top + gap)
            top = anchor.y()
            placed[ray] = anchor

    for seat in seating.rose_seating():
        mark = "  ●" if seat.sings else ""
        align = (Qt.AlignHCenter if seat.ray in (0, 12)
                 else Qt.AlignLeft if seat.ray < 12 else Qt.AlignRight)
        _label(painter, placed[seat.ray], [
            (f"{seat.hour:02d}h  {seat.cell.luminous}{mark}", INK, 15),
            (seat.cell.fallen, MUTED, 12),
            (f"{seat.axis.name}   {seat.cell.coords}", QColor("#5C6478"), 10),
        ], align=align, width=300.0)

    painter.setBrush(QColor("#12151D"))
    painter.setPen(QPen(QColor("#3A4152"), 2))
    painter.drawEllipse(centre, SIZE * 0.072, SIZE * 0.072)
    for row, name in enumerate(cube.SACRED_TRIO_NAMES):
        _label(painter, QPointF(centre.x(), centre.y() - 24 + row * 24),
               [(name, INK if row == 1 else MUTED, 12)], width=260.0)

    _label(painter, QPointF(SIZE / 2, 40), [
        ("THE ROSE OF THE TWENTY-FOUR — the human circle", INK, 22),
        ("adjacency = kinship (one axis, one grade)   ·   ray k faces ray k+12 "
         "through The One   ·   ● = the ray sings its own hue", MUTED, 12),
    ], width=SIZE - 40)
    painter.end()
    return image


def draw_calendar() -> QImage:
    """Calendar-12: one human axis per month, its two ends by radius —
    Restraint at the axle, Mobilization at the rim."""
    image, painter = _canvas()
    centre = QPointF(SIZE / 2, SIZE / 2 + 20)
    reach = SIZE * 0.40
    palette = defaults.PALETTE_PRESETS[("calendar", "light")]
    legend = ("3 face axes on the pure-colour arms — an equilateral triangle",
              "3 corner axes on the mixed-primary arms — the opposite triangle",
              "6 edge axes on the hexagon between")

    for arm in seating.calendar_seating():
        hue = QColor(palette[arm.wedge])
        start = 90.0 - (arm.angle_deg + 15.0)          # Qt: CCW from 3 o'clock
        painter.setBrush(QColor(hue.red(), hue.green(), hue.blue(), 46))
        painter.setPen(QPen(QColor(hue.red(), hue.green(), hue.blue(), 150), 1.5))
        painter.drawPie(QRectF(centre.x() - reach, centre.y() - reach,
                               reach * 2, reach * 2), int(start * 16), int(30 * 16))

    for arm in seating.calendar_seating():
        hue = QColor(palette[arm.wedge]).lighter(125)
        month = ("June", "July", "August", "September", "October", "November",
                 "December", "January", "February", "March", "April",
                 "May")[arm.wedge]
        _radial_label(painter, centre, arm.angle_deg, reach * 0.90,
                      [(f"{arm.outer.luminous}   ↑", hue, 16),
                       (arm.outer.fallen, MUTED, 11)])
        _radial_label(painter, centre, arm.angle_deg, reach * 0.655,
                      [(arm.axis.name, INK, 13),
                       (f"{month}  ·  {arm.hour:02d}h  ·  {arm.family}",
                        QColor("#6E7688"), 10)])
        _radial_label(painter, centre, arm.angle_deg, reach * 0.43,
                      [(arm.inner.luminous, hue, 13),
                       (arm.inner.fallen, MUTED, 10)])

    painter.setBrush(QColor("#12151D"))
    painter.setPen(QPen(QColor("#3A4152"), 2))
    painter.drawEllipse(centre, SIZE * 0.062, SIZE * 0.062)
    _label(painter, centre, [(cube.CALENDAR_CENTRE.luminous, INK, 15),
                             ("the centre medallion", MUTED, 11)])

    _label(painter, QPointF(SIZE / 2, 44), [
        ("THE CALENDAR OF THE TWELVE — one axis per month", INK, 22),
        ("   ·   ".join(legend), MUTED, 12),
        ("the axis the flat dial cannot show becomes the RADIUS: "
         "Restraint at the axle, Mobilization at the rim", MUTED, 12),
    ], width=SIZE - 40)
    painter.end()
    return image


def _ensure_a_readable_font() -> None:
    global FONT_FAMILY
    if QFontDatabase.families():
        return
    if not FALLBACK_FONT.exists():
        raise RuntimeError(
            f"no font families and no {FALLBACK_FONT} — the preview would "
            "render every label as an empty box; install a font or run under "
            "the native platform plugin")
    loaded = QFontDatabase.addApplicationFont(str(FALLBACK_FONT))
    FONT_FAMILY = QFontDatabase.applicationFontFamilies(loaded)[0]
    print(f"empty font database — fell back to {FONT_FAMILY}")


def main() -> None:
    QApplication.instance() or QApplication([])
    _ensure_a_readable_font()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, draw in (("rose_24", draw_rose), ("calendar_12", draw_calendar)):
        path = OUT_DIR / f"{name}.png"
        draw().save(str(path))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
