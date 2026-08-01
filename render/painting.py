"""Low-level QPainter primitives shared by every layer.

Pure drawing and dial-coordinate helpers: no skin knowledge, no
astronomy. `dial_point` and `pie_path`/`draw_pie` are the ONE place the
project's clockwise-from-top dial angle is converted to Qt's
counterclockwise-from-3-o'clock convention.
"""

import math
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QPen

from config import dial, palette
from render.context import RenderContext


                                     # the figure whose HOUR-SPACE holds the
                                     # hour hand draws FULL, the rest ghost —
                                     # computed from the live tick like the
                                     # calendar wedge, keying the composite


def dial_point(theta_deg: float, distance: float) -> QPointF:
    """Point at dial angle theta (clockwise from top) and given distance."""
    rad = math.radians(theta_deg)
    return QPointF(distance * math.sin(rad), -distance * math.cos(rad))


def draw_pie(painter: QPainter, radius: float, start_deg: float, end_deg: float) -> None:
    """Filled pie between two dial angles going CLOCKWISE (end > start,
    possibly beyond 360 for wrap-around arcs)."""
    rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
    qt_start = int(round((90.0 - start_deg) * 16))
    qt_span = int(round(-(end_deg - start_deg) * 16))
    painter.drawPie(rect, qt_start, qt_span)


def draw_pixmap_centered(
    painter: QPainter, ctx: "RenderContext", asset: Path, pos: QPointF,
    height: float, tint: str | None = None, desaturate: bool = False,
    metal: str | None = None, saturation: float = 1.0,
) -> None:
    """Asset rasterized to `height` and drawn centered at `pos` — the one
    shared image path of weekday bodies and the year marker (Rule #5).
    `tint` tritone-maps the image; `desaturate` grays it first;
    `metal` runs the hue-SELECTIVE bronze-to-gold/silver swap (only the
    warm bronze pixels change — owner insight 2026-07-12); `saturation`
    scales the FINAL pixmap's HSV saturation (owner 2026-07-18, Session
    21-D — the Ring saturation slider's one recolor spot; 1.0 is a
    no-op for every OTHER caller, which never passes it)."""
    pixmap = ctx.cache.pixmap_by_height(
        asset, height, ctx.dpr, tint, desaturate, metal, saturation
    )
    logical_w = pixmap.width() / ctx.dpr
    painter.drawPixmap(QPointF(pos.x() - logical_w / 2, pos.y() - height / 2), pixmap)


def draw_outlined_text(
    painter: QPainter, center: QPointF, text: str, font: QFont
) -> None:
    """White label with a black outline (readable over bright bodies) —
    the one shared text style of the weekday and date markers (Rule #5)."""
    metrics = QFontMetricsF(font)
    baseline = QPointF(
        center.x() - metrics.horizontalAdvance(text) / 2,
        center.y() + (metrics.ascent() - metrics.descent()) / 2,
    )
    path = QPainterPath()
    path.addText(baseline, font, text)
    outline_width = max(1.0, font.pixelSize() * dial.LABEL_OUTLINE_WIDTH)
    painter.setPen(QPen(QColor(*palette.LABEL_OUTLINE_RGBA), outline_width))
    painter.setBrush(QColor(*palette.LABEL_FILL_RGBA))
    painter.drawPath(path)


def tinted_gray(value: int, tint: str | None) -> QColor:
    """A gray of brightness `value` through the TRITONE map
    black -> tint -> white (owner spec 2026-07-11: whites stay white,
    blacks stay black, the exact midtone lands on the tint) — the
    Umbra's share of the ring recolor; None = plain gray. The scalar
    twin of AssetCache._tinted."""
    if tint is None:
        return QColor(value, value, value)
    hue = QColor(tint)

    def channel(c: int) -> int:
        if value <= 127:
            return c * (value * 2) // 255                    # black -> tint
        return c + (255 - c) * (value * 2 - 255) // 255      # tint -> white

    return QColor(channel(hue.red()), channel(hue.green()), channel(hue.blue()))


def name_label_px(name: str, target_width: float) -> int:
    """The measured pixel font size that fits `name` within
    `target_width`, capped at `dial.NAME_LABEL_MAX_PX`, floored at
    `dial.BODY_LABEL_MIN_PX` — the shared per-name fit (Rule #5):
    a SHORT text no longer inflates past a sane ceiling, a LONG one
    still shrinks to fit (measured, never guessed)."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(100)
    metrics = QFontMetricsF(font)
    width = metrics.horizontalAdvance(name)
    fitted = (
        math.floor(100.0 * target_width / width) if width > 0
        else dial.NAME_LABEL_MAX_PX
    )
    return max(
        dial.BODY_LABEL_MIN_PX, min(fitted, dial.NAME_LABEL_MAX_PX)
    )


def draw_name_label(
    painter: QPainter, name: str, pos: QPointF, label_px: float,
) -> None:
    """ONE on-dial name-label draw shared by the weekday bodies and the
    archetype figures (Rule #5, ROADMAP 15h item 4): draws `name` as a
    SINGLE outlined line at `label_px` (owner REVOKED the two-line wrap
    2026-07-18 — every name is one line again). `label_px` is decided
    by the CALLER, never measured here: the SET-UNIFORM law (owner
    verdict 2026-07-18) says every name sharing a ring (a dial's
    weekday bodies, an archetype layout's figures) wears the size of
    the SMALLEST fitted member of its set — computed ONCE per paint via
    `name_label_px` over the whole set, not per label."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(round(label_px))
    draw_outlined_text(painter, pos, name, font)


def pie_path(radius: float, start_deg: float, end_deg: float) -> QPainterPath:
    """Clip path for the pie between two dial angles going clockwise."""
    path = QPainterPath()
    path.moveTo(0.0, 0.0)
    rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
    path.arcTo(rect, 90.0 - start_deg, -(end_deg - start_deg))
    path.closeSubpath()
    return path


def draw_shadowed_text(
    painter: QPainter, center: QPointF, text: str, font: QFont,
    color: QColor,
) -> None:
    """A finish-colored label over a DROP SHADOW (owner 2026-07-15:
    subdial texts are never white — the metal color like the hand,
    shadowed so they read on both plate styles)."""
    metrics = QFontMetricsF(font)
    baseline = QPointF(
        center.x() - metrics.horizontalAdvance(text) / 2,
        center.y() + (metrics.ascent() - metrics.descent()) / 2,
    )
    path = QPainterPath()
    path.addText(baseline, font, text)
    offset = max(
        1.0,
        font.pixelSize() * dial.SUBDIAL_TEXT_SHADOW_OFFSET_FRACTION,
    )
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(*palette.SUBDIAL_TEXT_SHADOW_RGBA))
    painter.drawPath(path.translated(offset, offset))
    painter.setBrush(color)
    painter.drawPath(path)
    painter.restore()
