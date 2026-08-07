"""One numeral, painted — body, border and REAL page-space relief.

`core.numerals` decides where a glyph sits, how far it turns and which
way its relief is thrown; this module is the only place those numbers
become paint. Three responsibilities and nothing else:

1. **The glyph path in PAGE space.** The outline is built once with
   `QPainterPath.addText`, centred on its own tight bounding box, then
   transformed by `translate(seat) . rotate(rot)`. The relief copies are
   translated by the light vector AFTER that transform — never before.
   That is the ledger's own rule (§5): the relief is real geometry, so a
   tilted seat must not bend its own shadow and the lower half of the
   ring (which carries the extra 180 deg) must not throw its relief the
   opposite way from the upper half.
2. **The parity colours** (ledger §3) — even numerals a white body with
   a ring-colour border, odd numerals the inverse.
3. **The two soft passes** — the outer band's optional CONTACT BLUR (a
   small, intense black blur with no offset that seats a numeral against
   the metal: a separator, not an atmosphere) and the inner band's WHITE
   GLOW. Both are built as a WHOLE-BAND silhouette layer, blurred ONCE
   and composited under the crisp pass — never per glyph, and never as N
   stamped copies around a circle, which is the construction that
   scalloped the ring jewels' shadow at 1440p.

Every length that reaches a pen or a blur is a DEVICE-pixel length
derived from the plate's own pixel size: no fixed sample counts, no
logical-pixel constants, so a 1440p plate gets a 1440p blur by
construction.

Nothing here is ever called from `paint()`; the band builder
([Numeral Bands](__about/numeral_bands.md)) runs it while a settings
change is being applied.
"""

import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor, QFont, QFontMetricsF, QImage, QPainter, QPainterPath, QPen,
    QTransform,
)

from config import palette
from core import numerals


def glyph_path(text: str, font: QFont) -> QPainterPath:
    """`text` as a path centred on its own TIGHT bounding box, in the
    glyph's own upright frame. Tight, not advance-based: a numeral must
    sit on the ring by its ink, so "1" and "8" centre alike."""
    path = QPainterPath()
    path.addText(QPointF(0.0, 0.0), font, text)
    metrics = QFontMetricsF(font)
    tight = metrics.tightBoundingRect(text)
    return path.translated(
        -(tight.x() + tight.width() / 2.0),
        -(tight.y() + tight.height() / 2.0),
    )


def seated_path(
    text: str, font: QFont, center: QPointF, rotation_deg: float,
) -> QPainterPath:
    """`glyph_path` moved to its seat and turned by `rotation_deg` —
    the PAGE-SPACE path every relief copy below is a plain translation
    of."""
    transform = QTransform()
    transform.translate(center.x(), center.y())
    transform.rotate(rotation_deg)
    return transform.map(glyph_path(text, font))


def to_screen(offset: tuple[float, float]) -> QPointF:
    """A y-UP light offset (`core.numerals.light_offset`) as a y-DOWN
    Qt translation. The one place the two conventions meet."""
    return QPointF(offset[0], -offset[1])


def draw_relief(
    painter: QPainter, path: QPainterPath, style: str, depth_px: float,
    throw_px: tuple[float, float], darkness: float,
) -> None:
    """The relief copies of one glyph, far end FIRST so an `extrude`
    lays its wall down from the far end back to the numeral and the
    copies weld into a solid side wall."""
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    for dx, dy, role in numerals.relief_offsets(style, depth_px, throw_px):
        color = QColor(
            palette.NUMERAL_SHADE_COLOR if role == numerals.SHADE
            else palette.NUMERAL_LIT_COLOR
        )
        color.setAlphaF(max(0.0, min(1.0, darkness)))
        painter.setBrush(color)
        shift = to_screen((dx, dy))
        painter.drawPath(path.translated(shift.x(), shift.y()))
    painter.restore()


def draw_dilated(
    painter: QPainter, path: QPainterPath, reach_px: float, color: str,
) -> None:
    """The glyph GROWN by `reach_px` in every direction and filled flat
    — the outer band's black halo (THE FIDELITY RULING, measured on the
    owner's plates: the black around a numeral runs SOLID for ~10 px at
    3600 and only then fades over ~3).

    A blurred silhouette cannot make that plateau — a blur wide enough
    to reach 10 px is already a smoke cloud at its own edge — so the
    halo is a DILATION: the outline stroked with a pen `2 * reach_px`
    wide (round join and cap, so corners grow round exactly as they do
    in his art) under the same path filled. The soft edge is the
    contact blur laid over this, and that separation is what lets the
    plateau and the falloff be tuned against the plates independently."""
    painter.save()
    pen = QPen(QColor(color))
    pen.setWidthF(max(0.0, 2.0 * reach_px))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen if reach_px > 0.0 else Qt.PenStyle.NoPen)
    painter.setBrush(QColor(color))
    painter.drawPath(path)
    painter.restore()


def draw_body(
    painter: QPainter, path: QPainterPath, role: str, border_px: float,
) -> None:
    """The numeral itself in its PARITY colours (ledger §3). At border 0
    an odd numeral is ring on ring — deliberate: it exists only through
    the relief already laid down beneath it.

    The border is laid down FIRST and the body over it, so the border
    grows OUTWARD only and never eats into the glyph (THE FIDELITY
    RULING, measured: his even numerals' white is the full glyph and
    their ring-ground rim stands outside it; one `drawPath` with both a
    pen and a brush strokes centred instead, which shaved half the pen
    width off every stroke of every numeral)."""
    colors = palette.NUMERAL_PARITY_COLORS[role]
    painter.save()
    if border_px > 0.0:
        pen = QPen(QColor(colors["border"]))
        pen.setWidthF(border_px)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QColor(colors["border"]))
        painter.drawPath(path)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(colors["body"]))
    painter.drawPath(path)
    painter.restore()


def draw_inner_ink(
    painter: QPainter, path: QPainterPath, border_px: float,
) -> None:
    """An INNER-band element (number or stub) exactly as the owner drew
    every element of his inner plates: a RING-GROUND body inside a crisp
    WHITE border. The glow itself is a separate whole-band pass, so this
    stays hard-edged (ring_rework §2: "a white border+glow, never a
    diffuse halo").

    The body is NOT white (THE FIDELITY RULING, measured): his minute
    strokes, arrows and numbers are all the ring's own grey with a white
    rim, and a white body loses that rim entirely — the inner band went
    flat white on wave 3's screen for exactly this reason."""
    painter.save()
    if border_px > 0.0:
        pen = QPen(QColor(palette.MINUTES_BORDER))
        pen.setWidthF(border_px)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QColor(palette.MINUTES_BORDER))
        painter.drawPath(path)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette.MINUTES_INK))
    painter.drawPath(path)
    painter.restore()


def blank_plate(width: int, height: int | None = None) -> QImage:
    """A transparent DEVICE-resolution plate, DPR 1.0 while it is being
    painted. Everything drawn into it is measured in device pixels; the
    DPR stamp is applied at the very end (`stamp_dpr`), so no geometry
    is ever scaled twice. `height` defaults to `width` (every existing
    caller wants a square tile); the live crown's colon tile
    (`render.numeral_bands._crown_plate_image`) is the one caller that
    is not square — `time.png` is a tall narrow plate, not a glyph
    bounding box."""
    image = QImage(
        width, width if height is None else height,
        QImage.Format.Format_ARGB32_Premultiplied,
    )
    image.fill(Qt.GlobalColor.transparent)
    return image


def stamp_dpr(image: QImage, dpr: float) -> QImage:
    """The finished plate marked with its device pixel ratio, so a
    layer's `drawImage` lands it at the right LOGICAL size."""
    image.setDevicePixelRatio(dpr)
    return image


def plate_painter(image: QImage) -> QPainter:
    """A painter on a plate, antialiased, with the ORIGIN AT THE DIAL
    CENTRE — the same coordinate system every layer paints in, so a seat
    angle means the same thing here and on screen."""
    painter = QPainter(image)
    painter.setRenderHints(
        QPainter.RenderHint.Antialiasing
        | QPainter.RenderHint.SmoothPixmapTransform
        | QPainter.RenderHint.TextAntialiasing
    )
    painter.translate(image.width() / 2.0, image.height() / 2.0)
    return painter


def box_blur_alpha(image: QImage, radius_px: float, passes: int = 3) -> QImage:
    """A separable box blur run `passes` times over the ALPHA channel —
    three box passes are the standard good approximation of a gaussian,
    and running it on alpha alone keeps a silhouette a silhouette.

    `radius_px` is in DEVICE pixels, taken from the plate's own pixel
    size by every caller (the 1440p lesson: derive from pixels, never
    from a fixed count). A radius under half a pixel blurs nothing and
    returns the source untouched."""
    radius = int(round(radius_px))
    if radius < 1:
        return image
    source = image.convertToFormat(QImage.Format.Format_RGBA8888)
    width, height = source.width(), source.height()
    stride = source.bytesPerLine() // 4
    buffer = np.frombuffer(source.constBits(), dtype=np.uint8)
    rgba = buffer.reshape(height, stride, 4)[:, :width, :].astype(np.float32)
    alpha = rgba[..., 3] / 255.0
    window = 2 * radius + 1
    for _ in range(passes):
        alpha = _box_pass(alpha, radius, window, axis=1)
        alpha = _box_pass(alpha, radius, window, axis=0)
    rgba[..., 3] = np.clip(alpha, 0.0, 1.0) * 255.0
    out_bytes = np.ascontiguousarray(
        np.clip(rgba, 0.0, 255.0).round().astype(np.uint8)
    )
    result = QImage(
        out_bytes.tobytes(), width, height, width * 4,
        QImage.Format.Format_RGBA8888,
    ).copy()
    result.setDevicePixelRatio(image.devicePixelRatio())
    return result


def _box_pass(
    plane: np.ndarray, radius: int, window: int, axis: int,
) -> np.ndarray:
    """One box pass along `axis`, edges extended (a cumulative-sum box
    filter — O(n) per pass, no per-pixel Python)."""
    padded = np.pad(
        plane, [(radius + 1, radius) if a == axis else (0, 0) for a in (0, 1)],
        mode="edge",
    )
    cumulative = np.cumsum(padded, axis=axis)
    take = lambda start, stop: (            # noqa: E731 — a local slicer
        cumulative[start:stop, :] if axis == 0 else cumulative[:, start:stop]
    )
    size = plane.shape[axis]
    return (take(window, window + size) - take(0, size)) / window


def composite(
    plate: QImage, layer: QImage, opacity: float = 1.0, times: int = 1,
) -> None:
    """Draw `layer` onto `plate` `times` over, at `opacity` each — the
    inner band's glow INTENSITY is exactly this repeat count (a small
    radius composited several times reads as a tight bright edge, where
    one wide pass reads as smoke)."""
    painter = QPainter(plate)
    painter.setOpacity(max(0.0, min(1.0, opacity)))
    for _ in range(max(0, times)):
        painter.drawImage(0, 0, layer)
    painter.end()
