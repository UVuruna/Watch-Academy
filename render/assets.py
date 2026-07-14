"""Asset cache — rasterize each image once per (path, pixel height, tint).

PNG and SVG are both accepted (detected by extension); SVG goes through
QSvgRenderer so user vector hands stay sharp at any size. The explicit
QtSvg import also guarantees PyInstaller bundles the Svg plugin. An
optional tint recolors the rasterized image with a TRITONE gradient map
(black -> tint -> white; owner spec 2026-07-11): whites and blacks stay
untouched so ring numerals keep their contrast — only the gray midtones
take the hue. Source alpha is preserved.
"""

import hashlib
import math
import sys
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QImage, QImageReader, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from config import defaults, paths
from config.paths import art_file


def metal_variant_file(path: Path, metal: str | None) -> Path:
    """A DISK copy of `path` with the hue-selective metal swap applied
    (owner bug 2026-07-13: the legend/Encyclopedia <img> always showed
    the BRONZE file even under the gold/silver look — QToolTip embeds
    files, not pixmaps). Cached in the raster cache keyed by the file's
    mtime; None or a non-swap metal returns the original path."""
    path = art_file(path)
    if path is None or metal not in defaults.METAL_SWAP_TARGETS:
        return path
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(path.stat().st_mtime)}_{metal}.png"
    )
    if not cache.exists():
        swapped = AssetCache._metal_swapped(QPixmap(str(path)), metal)
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            swapped.save(str(cache))
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(f"metal variant cache write failed: {error}", file=sys.stderr)
            return path
    return cache


def scaled_variant_file(path: Path | None, width: int) -> Path | None:
    """A DISK copy of `path` downscaled to `width` px — the hover
    performance fix (owner 2026-07-13: every first hover decoded the
    full 800×800 plate synchronously inside the tooltip's rich text
    while the popup shows at most a quarter of that; callers pass 2×
    the display width so the tooltip still downsamples for
    crispness). Cached by mtime; sources already small enough return
    the original (the header read costs no pixel decode)."""
    path = art_file(path)
    if path is None or not path.exists():
        return path
    source = QImageReader(str(path)).size()
    if not source.isValid() or source.width() <= width:
        return path
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(path.stat().st_mtime)}_w{width}.png"
    )
    if not cache.exists():
        scaled = QPixmap(str(path)).scaledToWidth(
            width, Qt.TransformationMode.SmoothTransformation
        )
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            scaled.save(str(cache))
        except OSError as error:
            print(
                f"scaled variant cache write failed: {error}",
                file=sys.stderr,
            )
            return path
    return cache


class AssetCache:
    # SVG MASTERS survive across instances AND flush() (owner bug
    # 2026-07-12: traced letter SVGs parse in 1.3-1.6 s EACH — the
    # NUMBERS ring froze startup and every monitor switch re-paid it).
    # A file is parsed+rendered ONCE per session at master resolution,
    # persisted to a disk cache for the next launch, and every
    # requested size scales down from the master (dial letters stay
    # far below it).
    _svg_masters: dict[str, tuple[QImage, int]] = {}
    MASTER_MIN_PX = 1024
    MASTER_STEP_PX = 512

    def __init__(self):
        self._pixmaps: dict[tuple[str, int, str | None], QPixmap] = {}

    def pixmap_by_height(
        self,
        path: Path,
        logical_height: float,
        dpr: float,
        tint: str | None = None,
        desaturate: bool = False,
        metal: str | None = None,
    ) -> QPixmap:
        """The image scaled (aspect preserved) so its logical height is
        `logical_height`, rasterized at device resolution, optionally
        DESATURATED (user hand packs: colored art grays out so the
        clock tint has gray to work on), optionally tinted, and
        optionally METAL-SWAPPED (bronze-plate medallions: only the
        warm bronze pixels turn gold/silver — the gray stone stays;
        owner insight 2026-07-12). Raises ValueError for missing/
        unreadable assets — a broken skin must be visible, never
        silently blank. (Silver and bronze ring letters are
        PRE-RENDERED files — setup/make_*_letters.py — not runtime
        effects.)"""
        path = art_file(path)
        px_height = max(1, round(logical_height * dpr))
        key = (str(path), px_height, tint, desaturate, metal)
        if key not in self._pixmaps:
            pixmap = self._rasterize(path, px_height, dpr)
            if metal is not None:
                pixmap = self._metal_swapped(pixmap, metal)
            if desaturate:
                pixmap = self._desaturated(pixmap)
            if tint is not None:
                pixmap = self._tinted(pixmap, tint)
            self._pixmaps[key] = pixmap
        return self._pixmaps[key]

    @staticmethod
    def _metal_swapped(source: QPixmap, metal: str) -> QPixmap:
        """The hue-SELECTIVE metal swap (owner insight 2026-07-12): the
        bronze-plate art mixes warm bronze details with GRAY stone and
        engravings — a soft warm-hue window with a saturation ramp
        selects only the bronze pixels, which take the target metal's
        hue/saturation/value; everything else stays as drawn. numpy
        vectorized (per-pixel Python is banned in the render path)."""
        target = defaults.METAL_SWAP_TARGETS[metal]
        dpr = source.devicePixelRatio()
        image = source.toImage().convertToFormat(
            QImage.Format.Format_RGBA8888
        )
        width, height = image.width(), image.height()
        stride = image.bytesPerLine() // 4
        buffer = np.frombuffer(image.constBits(), dtype=np.uint8)
        rgba = (
            buffer.reshape(height, stride, 4)[:, :width, :]
            .astype(np.float64) / 255.0
        )
        rgb = rgba[..., :3]
        maxc = rgb.max(axis=-1)
        minc = rgb.min(axis=-1)
        span = maxc - minc
        sat = np.where(maxc > 0, span / np.maximum(maxc, 1e-6), 0.0)
        rc = (maxc - rgb[..., 0]) / np.maximum(span, 1e-6)
        gc = (maxc - rgb[..., 1]) / np.maximum(span, 1e-6)
        bc = (maxc - rgb[..., 2]) / np.maximum(span, 1e-6)
        hue = np.where(
            maxc == rgb[..., 0], bc - gc,
            np.where(maxc == rgb[..., 1], 2.0 + rc - bc, 4.0 + gc - rc),
        )
        hue = np.where(span > 0, (hue / 6.0) % 1.0, 0.0) * 360.0

        def smoothstep(x):
            x = np.clip(x, 0.0, 1.0)
            return x * x * (3.0 - 2.0 * x)

        low, high = defaults.METAL_SWAP_HUE_WINDOW
        soft = defaults.METAL_SWAP_HUE_SOFT
        sat_lo, sat_hi = defaults.METAL_SWAP_SAT_RAMP
        weight = (
            smoothstep((hue - (low - soft)) / soft)
            * (1.0 - smoothstep((hue - high) / soft))
            * smoothstep((sat - sat_lo) / (sat_hi - sat_lo))
        )[..., None]

        new_sat = np.clip(sat * target["sat_mul"], 0.0, 1.0)
        new_val = np.clip(maxc * target["val_mul"], 0.0, 1.0)
        sector = (target["hue"] % 360.0) / 60.0
        index = int(sector) % 6
        fraction = sector - int(sector)
        p = new_val * (1.0 - new_sat)
        q = new_val * (1.0 - new_sat * fraction)
        t = new_val * (1.0 - new_sat * (1.0 - fraction))
        order = [
            (new_val, t, p), (q, new_val, p), (p, new_val, t),
            (p, q, new_val), (t, p, new_val), (new_val, p, q),
        ][index]
        swapped = np.stack(order, axis=-1)

        rgba[..., :3] = rgb * (1.0 - weight) + swapped * weight
        out_bytes = np.ascontiguousarray(
            (np.clip(rgba, 0.0, 1.0) * 255.0).round().astype(np.uint8)
        )
        out = QImage(
            out_bytes.tobytes(), width, height, width * 4,
            QImage.Format.Format_RGBA8888,
        ).copy()
        out.setDevicePixelRatio(dpr)
        return QPixmap.fromImage(out)

    @staticmethod
    def _desaturated(source: QPixmap) -> QPixmap:
        """Grayscale luminance with the source alpha re-applied (the
        transparent-canvas pattern — fromImage of an opaque gray would
        drop the alpha channel)."""
        gray = source.toImage().convertToFormat(
            QImage.Format.Format_Grayscale8
        ).convertToFormat(QImage.Format.Format_ARGB32)
        result = QPixmap(source.size())
        result.setDevicePixelRatio(source.devicePixelRatio())
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.drawImage(0, 0, gray)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationIn
        )
        painter.drawPixmap(0, 0, source)
        painter.end()
        return result

    @staticmethod
    def _tinted(source: QPixmap, tint: str) -> QPixmap:
        """TRITONE gradient map black -> tint -> white (owner spec
        2026-07-11 — the plain channel multiply turned WHITE ring
        numerals into the tint color): luminance L keeps black at 0
        and white at 1, the exact midtone lands on the tint —
        out = SCREEN(max(2L-1, 0), MULTIPLY(min(2L, 1), tint)).
        Composed entirely from native blend modes (Plus / Multiply /
        Screen / invertPixels — no per-pixel Python, the review lesson);
        alpha restored from the source at the end.

        PURE BLACK is a SILHOUETTE, not a tritone (owner bug
        2026-07-12: the letter shadow tints with #000000, and the
        tritone left bright gold pixels bright — a red halo instead of
        a dark one): the source alpha filled solid black."""
        if QColor(tint).lightness() == 0:
            silhouette = QPixmap(source.size())
            silhouette.setDevicePixelRatio(source.devicePixelRatio())
            silhouette.fill(Qt.GlobalColor.transparent)
            painter = QPainter(silhouette)
            painter.drawPixmap(0, 0, source)
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceIn
            )
            painter.fillRect(silhouette.rect(), QColor(tint))
            painter.end()
            return silhouette
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
        """Drop the sized pixmaps (screen/DPI or skin change) — the SVG
        masters are resolution-independent pixels and stay."""
        self._pixmaps.clear()

    @classmethod
    def _svg_master(cls, path: Path, px_height: int) -> QImage:
        """The file rendered ONCE at master resolution (quantized, at
        least MASTER_MIN_PX) — parsed at most once per session and
        persisted to a disk cache so the next launch skips the parse
        entirely (traced SVGs cost seconds to parse)."""
        target = max(
            cls.MASTER_MIN_PX,
            math.ceil(px_height / cls.MASTER_STEP_PX) * cls.MASTER_STEP_PX,
        )
        key = str(path)
        cached = cls._svg_masters.get(key)
        if cached is not None and cached[1] >= max(px_height, cls.MASTER_MIN_PX):
            return cached[0]
        stamp = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
        disk = (
            paths.settings_path().parent / "raster_cache"
            / f"{stamp}_{int(path.stat().st_mtime)}_{target}.png"
        )
        image = QImage(str(disk)) if disk.exists() else QImage()
        if image.isNull():
            renderer = QSvgRenderer(key)
            if not renderer.isValid():
                raise ValueError(f"cannot load SVG asset: {path}")
            size = renderer.defaultSize()
            width = max(1, round(target * size.width() / size.height()))
            image = QImage(width, target, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)
            painter = QPainter(image)
            renderer.render(painter, QRectF(0, 0, width, target))
            painter.end()
            try:
                disk.parent.mkdir(parents=True, exist_ok=True)
                image.save(str(disk))
            except OSError as error:     # a cold cache is only slower,
                print(                   # never wrong — but say so
                    f"raster cache write failed: {disk}: {error}",
                    file=sys.stderr,
                )
        cls._svg_masters[key] = (image, target)
        return image

    @classmethod
    def _rasterize(cls, path: Path, px_height: int, dpr: float) -> QPixmap:
        if path.suffix.lower() == ".svg":
            master = cls._svg_master(path, px_height)
            image = (
                master
                if master.height() == px_height
                else master.scaledToHeight(
                    px_height, Qt.TransformationMode.SmoothTransformation
                )
            )
            pixmap = QPixmap.fromImage(image)
        else:
            source = QPixmap(str(path))
            if source.isNull():
                raise ValueError(f"cannot load image asset: {path}")
            pixmap = source.scaledToHeight(
                px_height, Qt.TransformationMode.SmoothTransformation
            )
        pixmap.setDevicePixelRatio(dpr)
        return pixmap
