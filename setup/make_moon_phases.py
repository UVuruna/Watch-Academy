"""One-time (rerunnable) generator: the EIGHT moon-phase plates for
the Encyclopedia (owner 2026-07-16), rendered from the full-moon
master with the SAME terminator geometry the dial uses (render.layers
_draw_moon): the lit region is the half-disc on the lit side combined
with the terminator half-ellipse (semi-axis a = R*|cos 2pi*f|) —
union when gibbous, difference when crescent; everything else darkens
under the year-marker shadow color/alpha. Rerun whenever the moon
master or the shadow tunables change.

Usage: python setup/make_moon_phases.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import QApplication

from config import constants, defaults

# Matches the weekday working-set ceiling — the Encyclopedia never
# asks for more.
SIZE = 800


def phase_stem(name: str) -> str:
    return name.lower().replace(" ", "_")


def render_phase(master: Path, fraction: float, out: Path) -> None:
    image = QImage(SIZE, SIZE, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.translate(SIZE / 2, SIZE / 2)
    painter.setPen(Qt.PenStyle.NoPen)

    radius = SIZE / 2
    pixmap = QPixmap(str(master)).scaled(
        SIZE, SIZE,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    painter.drawPixmap(
        QPointF(-pixmap.width() / 2, -pixmap.height() / 2), pixmap
    )

    # The dial's terminator geometry, verbatim (render.layers._draw_moon).
    lit_right = fraction < 0.5
    gibbous = 0.25 < fraction < 0.75
    half = QPainterPath()
    half.moveTo(0.0, -radius)
    half.arcTo(
        QRectF(-radius, -radius, SIZE, SIZE),
        90.0, -180.0 if lit_right else 180.0,
    )
    half.closeSubpath()
    semi_axis = radius * abs(math.cos(2.0 * math.pi * fraction))
    terminator = QPainterPath()
    terminator.addEllipse(QRectF(-semi_axis, -radius, 2 * semi_axis, SIZE))
    lit = half.united(terminator) if gibbous else half.subtracted(terminator)

    marker = defaults.DEFAULT_SKIN.year_marker
    disc = QPainterPath()
    disc.addEllipse(QRectF(-radius, -radius, SIZE, SIZE))
    shadow = QColor(marker.moon_dark_color)
    shadow.setAlphaF(marker.moon_shadow_alpha)
    painter.fillPath(disc.subtracted(lit), shadow)
    painter.end()

    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(out))
    print(f"  {out.name}  (fraction {fraction:.3f})")


def main() -> None:
    QApplication(sys.argv)
    assets = defaults.WEEKDAY_ART_DIR.parent
    for source in ("gemini", "chatgpt"):
        master = (
            assets / "weekday" / source / "planets" / "primary" / "moon.png"
        )
        if not master.exists():
            print(f"{source}: no moon master — skipped (art_file falls back)")
            continue
        print(f"{source}:")
        out_dir = assets / "moon" / source
        for index, name in enumerate(constants.MOON_PHASE_NAMES):
            render_phase(
                master,
                index / len(constants.MOON_PHASE_NAMES),
                out_dir / f"{phase_stem(name)}.png",
            )


if __name__ == "__main__":
    main()
