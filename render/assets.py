"""Asset cache — rasterize each image once per (path, pixel height).

PNG and SVG are both accepted (detected by extension); SVG goes through
QSvgRenderer so user vector hands stay sharp at any size. The explicit
QtSvg import also guarantees PyInstaller bundles the Svg plugin.
"""

from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


class AssetCache:
    def __init__(self):
        self._pixmaps: dict[tuple[str, int], QPixmap] = {}

    def pixmap_by_height(self, path: Path, logical_height: float, dpr: float) -> QPixmap:
        """The image scaled (aspect preserved) so its logical height is
        `logical_height`, rasterized at device resolution. Raises
        ValueError for missing/unreadable assets — a broken skin must be
        visible, never silently blank."""
        px_height = max(1, round(logical_height * dpr))
        key = (str(path), px_height)
        if key not in self._pixmaps:
            self._pixmaps[key] = self._rasterize(path, px_height, dpr)
        return self._pixmaps[key]

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
