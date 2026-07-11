"""Asset cache — rasterize each image once per (path, pixel height, tint).

PNG and SVG are both accepted (detected by extension); SVG goes through
QSvgRenderer so user vector hands stay sharp at any size. The explicit
QtSvg import also guarantees PyInstaller bundles the Svg plugin. An
optional tint recolors the rasterized image with a TRITONE gradient map
(black -> tint -> white; owner spec 2026-07-11): whites and blacks stay
untouched so ring numerals keep their contrast — only the gray midtones
take the hue. Source alpha is preserved.
"""

from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


class AssetCache:
    def __init__(self):
        self._pixmaps: dict[tuple[str, int, str | None], QPixmap] = {}

    def pixmap_by_height(
        self,
        path: Path,
        logical_height: float,
        dpr: float,
        tint: str | None = None,
    ) -> QPixmap:
        """The image scaled (aspect preserved) so its logical height is
        `logical_height`, rasterized at device resolution and optionally
        tinted (channel multiply, source alpha kept). Raises ValueError
        for missing/unreadable assets — a broken skin must be visible,
        never silently blank. (Silver ring letters are PRE-RENDERED
        files — setup/make_silver_letters.py — not a runtime effect.)"""
        px_height = max(1, round(logical_height * dpr))
        key = (str(path), px_height, tint)
        if key not in self._pixmaps:
            pixmap = self._rasterize(path, px_height, dpr)
            if tint is not None:
                pixmap = self._tinted(pixmap, tint)
            self._pixmaps[key] = pixmap
        return self._pixmaps[key]

    @staticmethod
    def _tinted(source: QPixmap, tint: str) -> QPixmap:
        """TRITONE gradient map black -> tint -> white (owner spec
        2026-07-11 — the plain channel multiply turned WHITE ring
        numerals into the tint color): luminance L keeps black at 0
        and white at 1, the exact midtone lands on the tint —
        out = SCREEN(max(2L-1, 0), MULTIPLY(min(2L, 1), tint)).
        Composed entirely from native blend modes (Plus / Multiply /
        Screen / invertPixels — no per-pixel Python, the review lesson);
        alpha restored from the source at the end."""
        device = source.size()               # device pixels; DPR reapplied at the end

        def opaque(fill: Qt.GlobalColor) -> QImage:
            image = QImage(device, QImage.Format.Format_ARGB32_Premultiplied)
            image.setDevicePixelRatio(source.devicePixelRatio())
            image.fill(fill)                 # same DPR everywhere -> 1:1 blits
            return image

        gray = opaque(Qt.GlobalColor.black)  # transparent areas read black;
        painter = QPainter(gray)             # alpha is reapplied last
        painter.drawPixmap(0, 0, source)
        painter.end()

        dark = gray.copy()                   # min(2L, 1)
        painter = QPainter(dark)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        painter.drawImage(0, 0, gray)
        painter.end()

        inverted = gray.copy()               # max(2L-1, 0) = 1 - min(2(1-L), 1)
        inverted.invertPixels()
        light = inverted.copy()
        painter = QPainter(light)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        painter.drawImage(0, 0, inverted)
        painter.end()
        light.invertPixels()

        painter = QPainter(dark)             # dark half toward the tint...
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
        painter.fillRect(dark.rect(), QColor(tint))
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
        painter.drawImage(0, 0, light)       # ...light half toward white
        painter.end()

        result = QPixmap(device)
        result.setDevicePixelRatio(source.devicePixelRatio())
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.drawImage(0, 0, dark)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationIn
        )
        painter.drawPixmap(0, 0, source)
        painter.end()
        return result

    def flush(self) -> None:
        """Drop everything (screen/DPI or skin change)."""
        self._pixmaps.clear()

    @staticmethod
    def _rasterize(path: Path, px_height: int, dpr: float) -> QPixmap:
        if path.suffix.lower() == ".svg":
            renderer = QSvgRenderer(str(path))
            if not renderer.isValid():
                raise ValueError(f"cannot load SVG asset: {path}")
            size = renderer.defaultSize()
            px_width = max(1, round(px_height * size.width() / size.height()))
            pixmap = QPixmap(px_width, px_height)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter, QRectF(0, 0, px_width, px_height))
            painter.end()
        else:
            source = QPixmap(str(path))
            if source.isNull():
                raise ValueError(f"cannot load image asset: {path}")
            pixmap = source.scaledToHeight(
                px_height, Qt.TransformationMode.SmoothTransformation
            )
        pixmap.setDevicePixelRatio(dpr)
        return pixmap
