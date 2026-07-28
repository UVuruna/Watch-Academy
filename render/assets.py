"""Asset cache — rasterize each image once per (path, pixel height, tint).

PNG and SVG are both accepted (detected by extension); SVG goes through
QSvgRenderer so user vector hands stay sharp at any size. The explicit
QtSvg import also guarantees PyInstaller bundles the Svg plugin. An
optional tint recolors the rasterized image with a TRITONE gradient map
(black -> tint -> white; owner spec 2026-07-11): whites and blacks stay
untouched so ring numerals keep their contrast — only the gray midtones
take the hue. Source alpha is preserved.

Surgical sibling split (`research/REFACTOR_PLAN.md` §8): this file now
holds ONLY `AssetCache` — every module-level helper that used to live
alongside it moved to [Asset Recolor](asset_recolor.md) (the metal/tint
family: `letter_metal_file`, `metal_variant_file`, `tinted_pixmap`,
`_recolored_plate`) or [Asset Variants](asset_variants.md) (everything
else: `ring_face_color`, the moon-phase family, `subdial_plate_file`,
the working-set family, the two computed icons). `AssetCache`'s own
import path is unchanged — every existing caller keeps working as is.

`pixmap_by_height` reads `working_ceiling`/`scaled_variant_file` back
from `asset_variants.py` — a genuine two-way edge between the split
files (that module in turn imports `asset_recolor.py`, which imports
`AssetCache` from here). Resolved with a LOCAL import inside
`pixmap_by_height` rather than a module-level one, so the three files'
top-level imports never form a cycle; see that method's own comment.
"""

import hashlib
import math
import sys
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from config import defaults, paths
from config.paths import art_file
from recolor import recolor
from recolor.recipe import load as recolor_recipe


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
        self._pixmaps: dict[tuple, QPixmap] = {}

    def pixmap_by_height(
        self,
        path: Path,
        logical_height: float,
        dpr: float,
        tint: str | None = None,
        desaturate: bool = False,
        metal: str | None = None,
        saturation: float = 1.0,
    ) -> QPixmap:
        """The image scaled (aspect preserved) so its logical height is
        `logical_height`, rasterized at device resolution, optionally
        DESATURATED (user hand packs: colored art grays out so the
        clock tint has gray to work on), optionally tinted, optionally
        METAL-SWAPPED (bronze-plate medallions: only the warm bronze
        pixels turn gold/silver — the gray stone stays; owner insight
        2026-07-12), and optionally SATURATION-scaled (owner 2026-07-18,
        Session 21-D — the Ring saturation slider: multiplies the FINAL
        pixmap's HSV saturation, after any tint, so a tinted ring plate
        actually grays; 1.0 is a no-op, the default for every OTHER
        caller). Raises ValueError for missing/unreadable assets — a
        broken skin must be visible, never silently blank. (Silver and
        bronze ring letters are PRE-RENDERED files —
        setup/make_*_letters.py — not runtime effects.)"""
        # Deferred (not module-level) on purpose: asset_variants.py
        # imports asset_recolor.py, which imports AssetCache from this
        # very module — a module-level import here would close that
        # loop into an unresolvable cycle. A call-time import is safe
        # because by the time any AssetCache method actually RUNS, all
        # three modules have already finished loading (see this file's
        # own module docstring).
        from render.asset_variants import scaled_variant_file, working_ceiling

        path = art_file(path)
        px_height = max(1, round(logical_height * dpr))
        # The SHADE is part of the key, not just the metal family (owner
        # 2026-07-28): one cache now serves every watch, and two watches
        # may both ask for "gold" while meaning different ramps.
        key = (
            str(path), px_height, tint, desaturate, metal, saturation,
            paths.metal_shade(metal) if metal is not None else None,
        )
        if key not in self._pixmaps:
            # The WORKING SET (owner 2026-07-15): a full-res original
            # decodes through its downscaled working copy whenever the
            # requested size fits under the subtree's ceiling — the
            # warmup pre-builds these, and a cold copy builds here
            # once. Oversized requests keep the original.
            ceiling = working_ceiling(path)
            source = path
            if ceiling is not None and px_height <= ceiling:
                source = scaled_variant_file(path, ceiling)
            pixmap = self._rasterize(source, px_height, dpr)
            if metal is not None:
                pixmap = QPixmap.fromImage(
                    self._recolored(
                        pixmap.toImage(), metal,
                        defaults.METAL_SOURCE_BADGE, defaults.METAL_MASK_BADGE,
                    )
                )
            if desaturate:
                pixmap = self._desaturated(pixmap)
            if tint is not None:
                pixmap = self._tinted(pixmap, tint)
            if saturation != 1.0:
                pixmap = self._saturated(pixmap, saturation)
            self._pixmaps[key] = pixmap
        return self._pixmaps[key]

    @staticmethod
    def _recolored(
        source: QImage, metal: str, source_metal: str, mask_mode: str,
        shade: str | None = None,
    ) -> QImage:
        """THE metal recolor door — a thin Qt adapter over the `recolor`
        package, which owns the algorithm (see
        [Recolor (folder)](../recolor/___recolor.md)).

        `metal` is the user-facing family (gold/silver/bronze); its
        active SHADE comes from `config.paths.metal_shade` and resolves
        through `defaults.METAL_SHADES` to a named RAMP in
        `recolor/presets/metals.json`. `source_metal` is the metal the
        art was DRAWN in — badges in bronze, ring letters on the gold
        master — because the transform is source-agnostic and must be
        told where it starts. `mask_mode` is `"chroma"` for art that
        mixes metal with gray stone and `"alpha"` for glyphs, which is
        the ONLY difference between the badge and letter paths (Rule #5
        — the retired code carried two near-copies of the whole recolor
        for exactly this one parameter).

        QImage in, QImage out (R1b threading find, 2026-07-20): the
        background hover-warm sweep reaches this through
        `metal_variant_file`, and QPixmap must never be touched off the
        GUI thread — GUI-thread callers wrap with QPixmap.fromImage.
        """
        # The shade is normally the ACTIVE watch's (its display context),
        # but the background art warm passes it EXPLICITLY: the ledger
        # recipe was recorded under one watch's context and is built on a
        # thread that has none, so reading the ambient value there would
        # silently recolor to the shipped default (owner bug 2026-07-28 —
        # the same leak the DisplayContext exists to end).
        shade = shade or paths.metal_shade(metal)
        ramp = defaults.METAL_SHADES[metal][shade]
        dpr = source.devicePixelRatio()
        image = source.convertToFormat(QImage.Format.Format_RGBA8888)
        width, height = image.width(), image.height()
        stride = image.bytesPerLine() // 4
        buffer = np.frombuffer(image.constBits(), dtype=np.uint8)
        rgba = (
            buffer.reshape(height, stride, 4)[:, :width, :]
            .astype(np.float64) / 255.0
        )

        result = recolor(
            rgba, source_metal, ramp, recolor_recipe(),
            mask_mode=mask_mode,
        )

        out_bytes = np.ascontiguousarray(
            (np.clip(result, 0.0, 1.0) * 255.0).round().astype(np.uint8)
        )
        out = QImage(
            out_bytes.tobytes(), width, height, width * 4,
            QImage.Format.Format_RGBA8888,
        ).copy()
        out.setDevicePixelRatio(dpr)
        return out

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
    def _saturated(source: QPixmap, factor: float) -> QPixmap:
        """Scale every pixel's HSV SATURATION by `factor` (owner
        2026-07-18, Session 21-D — the Ring saturation slider's one
        recolor spot), hue and value untouched: lerping each RGB channel
        toward the pixel's OWN max channel (= V in HSV) by `1 - factor`
        is exactly the HSV saturation scale (the same "gray to its own
        brightness" law as `_saturate_hue`'s flat-color twin) —
        vectorized like the metal swap, no per-pixel Python in the
        render path. Alpha is untouched."""
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
        value = rgb.max(axis=-1, keepdims=True)
        rgba[..., :3] = np.clip(value + (rgb - value) * factor, 0.0, 1.0)
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


_SHARED_CACHE: AssetCache | None = None


def shared_cache() -> AssetCache:
    """THE process-wide rasterized-image cache.

    Owner ruling 2026-07-28: *"čovjek dakle samo 1 treba da se učitava u
    ram u slike ili god"*. Every watch used to build its OWN `AssetCache`,
    and built a FRESH one on every skin install — so three watches held
    three decoded copies of the same ring plate, and changing a setting
    threw all of them away and re-decoded from scratch. The watches draw
    from the same asset tree, so they share the same RAM.

    Safe to share because the key already carries everything that can
    make two requests differ — the resolved path (which encodes the art
    source), the device pixel height, tint, desaturation, metal AND its
    shade, and saturation.
    """
    global _SHARED_CACHE
    if _SHARED_CACHE is None:
        _SHARED_CACHE = AssetCache()
    return _SHARED_CACHE
