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
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QImage, QImageReader, QPainter, QPainterPath, QPixmap
from PySide6.QtSvg import QSvgRenderer

from config import defaults, paths, profiling
from config.paths import art_file


_ring_face_colors: dict[str, QColor] = {}


def ring_face_color(path: Path | None) -> QColor:
    """The ring art's own FACE color — the slot-roundel fill (owner
    2026-07-14: 'boja unutar kruga je RING preset boja'). Sampled once
    per file: walk the top center column to the first opaque band,
    then read a ring of pixels a few steps deeper and take the MEDIAN
    by luminance, so numerals and ticks (the bright minority) never
    win. Missing/unreadable art falls back to the documented color."""
    if path is None:
        return QColor(defaults.SLOT_ROUNDEL_FILL_FALLBACK)
    key = str(path)
    cached = _ring_face_colors.get(key)
    if cached is not None:
        return cached
    image = QImage(key)
    color = QColor(defaults.SLOT_ROUNDEL_FILL_FALLBACK)
    if not image.isNull():
        center = image.width() // 2
        top = next(
            (
                y for y in range(image.height() // 2)
                if image.pixelColor(center, y).alpha() > 200
            ),
            None,
        )
        if top is not None:
            depth = top + max(3, image.height() // 40)
            radius = image.height() / 2.0 - depth
            samples = []
            for step in range(0, 360, 9):
                angle = math.radians(step)
                probe = image.pixelColor(
                    round(center + radius * math.sin(angle)),
                    round(image.height() / 2.0 - radius * math.cos(angle)),
                )
                if probe.alpha() > 200:
                    samples.append(probe)
            if samples:
                samples.sort(key=lambda c: c.lightness())
                color = samples[len(samples) // 2]
    _ring_face_colors[key] = color
    return color


# The MOON terminator geometry (owner 2026-07-16; quarter-degeneracy
# fix 2026-07-19, live-render round): the lit region is the half-disc
# on the lit side combined (gibbous) or reduced (crescent) with the
# terminator half-ellipse (semi-axis a = R*|cos(2*pi*f)|). ONE shared
# function — `render.layers.YearMarkerLayer._draw_moon` (the dial) and
# `moon_phase_image` below (the Encyclopedia's live-rendered Moon
# pages) both call it, so the two never drift apart.
MOON_TERMINATOR_EPSILON = 1e-6   # of the radius — the exact-quarter guard


def moon_lit_region(fraction: float, radius: float) -> QPainterPath:
    """The lit region of a moon disc of `radius` centered at the
    origin (waxing, fraction < 0.5, lit on the right). AT THE EXACT
    QUARTERS (fraction 0.25 / 0.75) the terminator semi-axis is
    mathematically zero: Qt's `addEllipse` on a zero-width rect
    degenerates, and routing that through `united`/`subtracted`
    resolves to an EMPTY path — the moon rendered fully dark instead
    of exactly half-lit (the bug the pre-rendered plates shipped with
    at first/third quarter). Fixed by skipping the boolean op
    entirely whenever the semi-axis collapses and returning the
    half-disc outright — the mathematically exact answer at a
    quarter anyway."""
    size = 2.0 * radius
    lit_right = fraction < 0.5
    half = QPainterPath()
    half.moveTo(0.0, -radius)
    # 90 deg is the top in Qt's CCW system; sweep -180 covers the right
    # half, +180 the left half.
    half.arcTo(
        QRectF(-radius, -radius, size, size),
        90.0, -180.0 if lit_right else 180.0,
    )
    half.closeSubpath()
    semi_axis = radius * abs(math.cos(2.0 * math.pi * fraction))
    if semi_axis <= radius * MOON_TERMINATOR_EPSILON:
        return half
    gibbous = 0.25 < fraction < 0.75
    terminator = QPainterPath()
    terminator.addEllipse(QRectF(-semi_axis, -radius, 2.0 * semi_axis, size))
    return half.united(terminator) if gibbous else half.subtracted(terminator)


def moon_phase_image(fraction: float, size: int, master: Path | None = None) -> QImage:
    """The full-moon master art shadowed by `moon_lit_region` for the
    given illuminated FRACTION — the pure render the Encyclopedia's
    Moon pages now call live instead of shipping eight pre-baked
    plates (owner decree 2026-07-19: "bolje crtati na licu mesta nego
    15MB fajlova"). Mirrors `_draw_moon`'s two branches exactly: with
    a master (the shipped default) only the UNLIT half darkens under
    the shadow color/alpha; without one (a missing/placeholder asset)
    a plain dark disc gets the LIT half painted bright instead — the
    same graceful fallback the dial itself falls back to."""
    marker = defaults.DEFAULT_SKIN.year_marker
    resolved = art_file(
        master if master is not None
        else defaults.WEEKDAY_ART_DIR / "planets" / "primary" / "moon.png"
    )
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.translate(size / 2.0, size / 2.0)
    painter.setPen(Qt.PenStyle.NoPen)
    radius = size / 2.0
    lit = moon_lit_region(fraction, radius)
    disc = QPainterPath()
    disc.addEllipse(QRectF(-radius, -radius, size, size))
    has_asset = resolved is not None and resolved.exists()
    if has_asset:
        pixmap = QPixmap(str(resolved)).scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(
            QPointF(-pixmap.width() / 2.0, -pixmap.height() / 2.0), pixmap
        )
        shadow = QColor(marker.moon_dark_color)
        shadow.setAlphaF(marker.moon_shadow_alpha)
        painter.fillPath(disc.subtracted(lit), shadow)
    else:
        painter.setBrush(QColor(marker.moon_dark_color))
        painter.drawEllipse(QPointF(0, 0), radius, radius)
        painter.fillPath(lit, QColor(marker.moon_lit_color))
    painter.end()
    return image


def moon_phase_file(fraction: float, name: str, size: int = 800) -> Path:
    """A disk-cached copy of `moon_phase_image` — the Encyclopedia's
    Moon topic wants a PATH like every other article image (owner
    2026-07-19: the eight pre-baked plates in `assets/moon/` are
    retired; this is the live-render replacement, the cost paid once
    per (phase, size) through the raster cache instead of shipping
    ~7 MB of PNGs)."""
    master = art_file(defaults.WEEKDAY_ART_DIR / "planets" / "primary" / "moon.png")
    stamp = hashlib.sha1(str(master).encode("utf-8")).hexdigest()[:16]
    mtime = int(master.stat().st_mtime) if master.exists() else 0
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{mtime}_moon_{name}_{size}.png"
    )
    if not cache.exists():
        image = moon_phase_image(fraction, size, master)
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            if not image.save(str(cache)):
                raise OSError(f"QImage.save returned False for {cache}")
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(f"moon phase cache write failed: {error}", file=sys.stderr)
            return master
    return cache


def letter_metal_file(path: Path, metal: str) -> Path:
    """The ring letter's SILVER or BRONZE finish, derived AT LOAD from
    the GOLD master (owner decree 2026-07-19: "bolje crtati na licu
    mesta nego 15MB fajlova" — retiring the 76 pre-rendered
    `_silver.png`/`_bronze.png` files and setup/make_silver_letters.py
    / make_bronze_letters.py). The sealed recipes, reproduced exactly:
    silver is a straight grayscale desaturation with the source alpha
    kept (`AssetCache._desaturated`); bronze is a straight per-channel
    multiply with `defaults.BRONZE_LETTER_TINT` off the SILVER result
    (`AssetCache._bronzed`) — brightness/contrast sit at 1.0 (an
    identity step), the owner's verdict that darkened candidates read
    darker than the bronze medallions. `metal="gold"` is a no-op
    passthrough (the gold master IS the art). Disk-cached like every
    other derived asset (`metal_variant_file`'s pattern) — paid once
    per (file, metal), never per paint."""
    path = art_file(path)
    if metal == "gold" or path is None:
        return path
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(path.stat().st_mtime)}_letter_{metal}.png"
    )
    if not cache.exists():
        source = QPixmap(str(path))
        if source.isNull():
            raise ValueError(f"cannot load image asset: {path}")
        silver = AssetCache._desaturated(source)
        result = (
            silver if metal == "silver"
            else AssetCache._bronzed(silver, defaults.BRONZE_LETTER_TINT)
        )
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            if not result.save(str(cache)):
                raise OSError(f"QPixmap.save returned False for {cache}")
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(f"letter metal cache write failed: {error}", file=sys.stderr)
            return path
    return cache


def subdial_plate_file(
    finish: str, tint: str | None = None
) -> Path | None:
    """The owner's ONE subdial master (Rule #19, "Compute, Don't
    Generate" — owner decree 2026-07-20, its first enforcement): the
    twelve-plate sheet (4 seats x 3 finishes) collapsed to a SINGLE
    generated image per source — the directional shadow is one line of
    circle math (`render.layers._draw_subdial_shadow`, keyed off the
    seat's own dial position, nothing to do with the FILE), and the
    seat dimension never touches this function at all any more. His
    master wins AS DRAWN for its own finish (`SUBDIAL_MASTER_FINISH`
    names which); the other two finishes are disk-cached recolors of
    that SAME master, exactly like the ring letters derive silver/
    bronze from gold live. A TINT (the "theme" plate style, owner
    2026-07-15 A/B spec) recolors the dark tapisserie field to the
    clock tint — that pass runs even on the exact finish, into its own
    cache entry. None = no master art at all (the layer then draws the
    procedural circle)."""
    master = paths.art_file(defaults.SUBDIAL_ART_DIR / "master.png")
    if master is None or not master.exists():
        return None
    source = master.relative_to(paths.assets_dir()).parts[1]
    own_finish = defaults.SUBDIAL_MASTER_FINISH[source]
    if finish == own_finish and tint is None:
        return master
    return _recolored_plate(master, finish, tint)


@profiling.timed("Subdial recolor")
def _recolored_plate(
    master: Path, finish: str, tint: str | None = None
) -> Path:
    """The master plate with its brushed metal BEZEL colorized to
    `finish` — built the SAME recipe the ring letters use to derive
    silver/bronze live from gold (Rule #5, `letter_metal_file`): SILVER
    is the achromatic VALUE alone (no hue at all, whatever metal the
    master itself happens to be drawn in — the letters' "straight
    desaturation" rule, masked here to the rim only); GOLD and BRONZE
    tint that same achromatic base by their own color (the letters'
    "tint the desaturated result" rule). Only bright, unsaturated
    pixels INSIDE the radial bezel band take the recolor — the field's
    own specular highlights stay neutral (owner correction 2026-07-15:
    without the radial mask the interiors drank the metal and the
    three finishes stopped matching). With a TINT the interior (the
    tapisserie field) is colorized the same way to the clock tint (the
    "theme" plate style); without one the field stays as drawn."""
    stamp = hashlib.sha1(str(master).encode("utf-8")).hexdigest()[:16]
    tint_tag = f"_{tint.lstrip('#').lower()}" if tint else ""
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(master.stat().st_mtime)}"
        f"_subdial{defaults.SUBDIAL_RECOLOR_VERSION}"
        f"_{finish}{tint_tag}.png"
    )
    if cache.exists():
        return cache
    image = QImage(str(master)).convertToFormat(
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
    value = rgb.max(axis=-1)
    minc = rgb.min(axis=-1)
    sat = np.where(value > 0, (value - minc) / np.maximum(value, 1e-6), 0.0)

    def smoothstep(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    value_low, value_high = defaults.SUBDIAL_RECOLOR_VALUE_RAMP
    sat_low, sat_high = defaults.SUBDIAL_RECOLOR_SAT_CUTOFF
    # The radial bezel band: 0 across the whole field, ramping to 1
    # where the brushed bezel lives — the metal never reaches the
    # interior highlights.
    rim_low, rim_high = defaults.SUBDIAL_RECOLOR_RIM_RADIUS
    ys, xs = np.mgrid[0:height, 0:width]
    radius = np.hypot(
        xs - (width - 1) / 2.0, ys - (height - 1) / 2.0
    ) / (width / 2.0)
    weight = (
        smoothstep((value - value_low) / (value_high - value_low))
        * (1.0 - smoothstep((sat - sat_low) / (sat_high - sat_low)))
        * smoothstep((radius - rim_low) / (rim_high - rim_low))
    )[..., None]
    if finish == "silver":
        # The achromatic base alone, masked to the rim — the same
        # "silver is a straight desaturation" recipe letters use.
        rim = np.repeat(value[..., None], 3, axis=-1)
    else:
        target = QColor(defaults.SUBDIAL_RECOLOR_COLORS[finish])
        finish_rgb = np.array([
            target.redF(), target.greenF(), target.blueF()
        ])
        rim = finish_rgb[None, None, :] * value[..., None]
    if tint:
        # The "theme" plate style: the dark tapisserie field takes the
        # clock tint, luminance-preserving like the rim but lifted by
        # the field gain so the hue actually reads on the dark relief.
        theme = QColor(tint)
        theme_rgb = np.array([
            theme.redF(), theme.greenF(), theme.blueF()
        ])
        lifted = value * defaults.SUBDIAL_RECOLOR_FIELD_GAIN
        field = theme_rgb[None, None, :] * lifted[..., None]
    else:
        field = rgb
    rgba[..., :3] = field * (1.0 - weight) + rim * weight
    out_bytes = np.ascontiguousarray(
        (np.clip(rgba, 0.0, 1.0) * 255.0).round().astype(np.uint8)
    )
    out = QImage(
        out_bytes.tobytes(), width, height, width * 4,
        QImage.Format.Format_RGBA8888,
    ).copy()
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        out.save(str(cache))
    except OSError as error:
        # A cold cache is only slower, never wrong — but say so.
        print(f"subdial recolor cache write failed: {error}", file=sys.stderr)
        return master
    return cache


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
        # QImage end to end — this runs on the background hover-warm
        # thread too, where QPixmap is forbidden (R1b find, 2026-07-20:
        # the one off-GUI-thread QPixmap in the codebase, the prime
        # suspect for the untraced whole-app aborts).
        swapped = AssetCache._metal_swapped(QImage(str(path)), metal)
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            swapped.save(str(cache))
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(f"metal variant cache write failed: {error}", file=sys.stderr)
            return path
    return cache


def _scaled_cache_path(path: Path, width: int) -> Path:
    """Where `path`'s downscaled-to-`width` copy lives. The source
    STEM rides the name — hover tests and humans can read which face
    a derived file came from."""
    stamp = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16]
    return (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(path.stat().st_mtime)}_w{width}_{path.stem}.png"
    )


def working_ceiling(path: Path | None) -> int | None:
    """The WORKING-SET ceiling of an asset (owner 2026-07-15): the
    subtree under assets/ names the largest pixel size the dial can
    ever ask of it — None for trees the dial never draws (guide,
    instrument reader art) and for paths outside assets/."""
    if path is None:
        return None
    try:
        subtree = path.relative_to(paths.assets_dir()).parts[0]
    except ValueError:
        return None
    return defaults.WORKING_SET_CEILINGS.get(subtree)


@profiling.timed("Working set warmup")
def warm_working_set(progress=None) -> int:
    """Generate the DOWNSCALED working copies of every oversized dial
    asset (owner 2026-07-15: the originals ship full-res, the
    installation builds the working set). Runs on a background thread
    at startup — QImage-based, disk-cached like every derived file, a
    no-op once warm. Returns how many copies were (re)built."""
    from time import perf_counter

    start = perf_counter()
    built = 0
    todo: list[tuple[Path, int]] = []
    for subtree, ceiling in defaults.WORKING_SET_CEILINGS.items():
        for source in sorted((paths.assets_dir() / subtree).rglob("*.png")):
            size = QImageReader(str(source)).size()
            if size.isValid() and size.width() > ceiling:
                todo.append((source, ceiling))
    for index, (source, ceiling) in enumerate(todo):
        fresh = not _scaled_cache_path(source, ceiling).exists()
        scaled_variant_file(source, ceiling)
        if fresh:
            built += 1
        if progress is not None and (index + 1) % 10 == 0:
            elapsed = perf_counter() - start
            progress(
                f"[{elapsed:.1f}s] working set {index + 1}/{len(todo)} "
                f"({(index + 1) / len(todo) * 100:.0f}%)"
            )
    if progress is not None and todo:
        progress(
            f"[{perf_counter() - start:.1f}s] working set complete — "
            f"{len(todo)} oversized sources"
        )
    return built


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
    cache = _scaled_cache_path(path, width)
    if not cache.exists():
        # QImage, not QPixmap — the working-set warmup calls this off
        # the GUI thread (QPixmap is main-thread-only).
        scaled = QImage(str(path)).scaledToWidth(
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
        path = art_file(path)
        px_height = max(1, round(logical_height * dpr))
        key = (str(path), px_height, tint, desaturate, metal, saturation)
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
                    self._metal_swapped(pixmap.toImage(), metal)
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
    def _metal_swapped(source: QImage, metal: str) -> QImage:
        """The hue-SELECTIVE metal swap (owner insight 2026-07-12): the
        bronze-plate art mixes warm bronze details with GRAY stone and
        engravings — a soft warm-hue window with a saturation ramp
        selects only the bronze pixels, which take the target metal's
        hue/saturation/value; everything else stays as drawn. numpy
        vectorized (per-pixel Python is banned in the render path).
        QImage in, QImage out (R1b threading find, 2026-07-20): the
        background hover-warm sweep reaches this through
        `metal_variant_file`, and QPixmap must never be touched off the
        GUI thread — GUI-thread callers wrap with QPixmap.fromImage."""
        target = defaults.METAL_SWAP_TARGETS[metal]
        dpr = source.devicePixelRatio()
        image = source.convertToFormat(
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
    def _bronzed(source: QPixmap, tint: str) -> QPixmap:
        """The ring-letter BRONZE recipe (owner decision 2026-07-12,
        retired setup/make_bronze_letters.py — live-derived now):
        `source` is a GRAYSCALE (silver-desaturated) pixmap, R=G=B on
        every opaque pixel; a brightness/contrast LUT (identity at the
        sealed 1.0/1.0 values — darkened candidates read darker than
        the bronze medallions, owner verdict) then a straight
        per-channel multiply with `tint`. Alpha carried through
        unchanged."""
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
        gray = rgba[..., 0]      # grayscale source: R == G == B
        brightness = defaults.BRONZE_LETTER_BRIGHTNESS
        contrast = defaults.BRONZE_LETTER_CONTRAST
        gray = np.clip((gray * brightness - 0.5) * contrast + 0.5, 0.0, 1.0)
        color = QColor(tint)
        tint_rgb = np.array([color.redF(), color.greenF(), color.blueF()])
        rgba[..., :3] = gray[..., None] * tint_rgb[None, None, :]
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
