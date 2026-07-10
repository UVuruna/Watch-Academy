"""Pre-render the SILVER ring letters (owner decision 2026-07-10).

Rasterizes each ACTIVE gold letter (RING_LETTER_FILES) at high
resolution, removes the saturation offline — grayscale luminance with
the source alpha kept — and writes `<Stem>_silver.png` beside the gold
master. Silver is ordinary art afterwards; the app never desaturates
at runtime. Rerun when a new letter becomes active in a ring preset.

    python setup/make_silver_letters.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from config import constants, defaults

RENDER_HEIGHT_PX = 512      # comfortably above any on-dial letter size


def _rasterize(path: Path) -> QImage:
    if path.suffix.lower() == ".svg":
        renderer = QSvgRenderer(str(path))
        if not renderer.isValid():
            raise ValueError(f"cannot load SVG: {path}")
        size = renderer.defaultSize()
        width = max(1, round(RENDER_HEIGHT_PX * size.width() / size.height()))
        image = QImage(
            width, RENDER_HEIGHT_PX, QImage.Format.Format_ARGB32
        )
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        renderer.render(painter, QRectF(0, 0, width, RENDER_HEIGHT_PX))
        painter.end()
        return image
    image = QImage(str(path))
    if image.isNull():
        raise ValueError(f"cannot load image: {path}")
    return image.convertToFormat(QImage.Format.Format_ARGB32)


def _desaturate(image: QImage) -> QImage:
    """Grayscale luminance with the source alpha re-applied — composed
    on an explicitly transparent canvas (QPixmap.fromImage of an opaque
    image would drop the alpha channel)."""
    gray = image.convertToFormat(
        QImage.Format.Format_Grayscale8
    ).convertToFormat(QImage.Format.Format_ARGB32)
    canvas = QPixmap(image.size())
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    painter.drawImage(0, 0, gray)
    painter.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_DestinationIn
    )
    painter.drawImage(0, 0, image)
    painter.end()
    return canvas.toImage()


def main() -> None:
    QGuiApplication(sys.argv)
    for letter, filename in sorted(constants.RING_LETTER_FILES.items()):
        source = defaults.RING_LETTER_ART_DIR / filename
        target = defaults.RING_LETTER_ART_DIR / f"{Path(filename).stem}_silver.png"
        silver = _desaturate(_rasterize(source))
        if not silver.save(str(target)):
            raise ValueError(f"cannot write {target}")
        print(f"{letter}: {source.name} -> {target.name} "
              f"({silver.width()}x{silver.height()})")


if __name__ == "__main__":
    main()
