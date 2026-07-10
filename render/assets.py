"""Asset cache — rasterize each image once per (path, pixel height, tint).

PNG and SVG are both accepted (detected by extension); SVG goes through
QSvgRenderer so user vector hands stay sharp at any size. The explicit
QtSvg import also guarantees PyInstaller bundles the Svg plugin. An
optional tint channel-multiplies the rasterized image (the ring recolor:
gray art x hue), preserving the alpha of the source.
"""

from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


class AssetCache:
    def __init__(self):
        self._pixmaps: dict[tuple[str, int, str | None, bool], QPixmap] = {}

    def pixmap_by_height(
        self,
        path: Path,
        logical_height: float,
        dpr: float,
        tint: str | None = None,
        desaturate: bool = False,
    ) -> QPixmap:
        """The image scaled (aspect preserved) so its logical height is
        `logical_height`, rasterized at device resolution and optionally
        tinted (channel multiply, source alpha kept) or desaturated (the
        SILVER look of the owner's gold letter art). Raises ValueError
        for missing/unreadable assets — a broken skin must be visible,
        never silently blank."""
        px_height = max(1, round(logical_height * dpr))
        key = (str(path), px_height, tint, desaturate)
        if key not in self._pixmaps:
            pixmap = self._rasterize(path, px_height, dpr)
            if tint is not None:
                pixmap = self._tinted(pixmap, tint)
            if desaturate:
                pixmap = self._desaturated(pixmap)
            self._pixmaps[key] = pixmap
        return self._pixmaps[key]

    @staticmethod
    def _desaturated(source: QPixmap) -> QPixmap:
        """Grayscale with the alpha kept — turns the owner's gold letter
        art silver (owner-approved derivation). Entirely native Qt
        conversions (review finding: a per-pixel Python loop stalled the
        GUI thread for seconds at large dial sizes): luminance via
        Grayscale8, then the source alpha re-applied as a mask."""
        image = source.toImage()
        gray = image.convertToFormat(
            QImage.Format.Format_Grayscale8
        ).convertToFormat(QImage.Format.Format_ARGB32)
        alpha = image.convertToFormat(QImage.Format.Format_Alpha8)
        result = QPixmap.fromImage(gray)
        painter = QPainter(result)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationIn
        )
        painter.drawImage(0, 0, alpha)
        painter.end()
        result.setDevicePixelRatio(source.devicePixelRatio())
        return result

    @staticmethod
    def _tinted(source: QPixmap, tint: str) -> QPixmap:
        """Channel multiply with `tint`, alpha restored from the source
        — the standard cheap colorize for gray art (white -> the tint,
        mid-gray -> a darker tint)."""
        result = QPixmap(source.size())
        result.setDevicePixelRatio(source.devicePixelRatio())
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.drawPixmap(0, 0, source)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
        painter.fillRect(result.rect(), QColor(tint))
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
