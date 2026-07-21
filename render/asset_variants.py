"""Disk-cached derived images that are not metal recolors — the
"working set" downscale family, the moon-phase live render, the
subdial plate resolver, and the two computed icon families (calendar
wheel, solar eclipse type). Split out of `assets.py` (surgical sibling
extraction, `research/REFACTOR_PLAN.md` §8). See
[Asset Variants](asset_variants.md) for the full recipe.

`AssetCache.pixmap_by_height` (`assets.py`) reads `working_ceiling`/
`scaled_variant_file` back from this module — a genuine two-way edge
between the two files, since `AssetCache` stays in `assets.py` while
these helpers moved here. `assets.py` resolves it with a LOCAL import
inside `pixmap_by_height` instead of a module-level one, so the two
modules' top-level imports never form a cycle; see that method's own
comment for why.
"""

import hashlib
import math
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (
    QColor, QImage, QImageReader, QPainter, QPainterPath, QPen, QPixmap,
)

from config import defaults, paths, profiling
from config.paths import art_file
from render.asset_recolor import _recolored_plate, tinted_pixmap


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


def subdial_plate_file(
    finish: str, tint: str | None = None
) -> Path | None:
    """The active SUBDIAL SET's plate for `finish` (owner decree
    2026-07-21, Rsub round — retires the Rule #19 one-master-per-source
    model this function used to implement). The set itself is picked in
    Settings and lives as a `config.paths` module global
    (`paths.subdial_set()`, mirroring the art-source switch exactly) —
    it is NOT threaded as a parameter here since this is its only
    reader, keeping `render.layers.draw_slot_roundel`'s existing call
    untouched.

    Sets 1-4 are three hand-drawn finishes each: the matching file
    returns AS DRAWN, no recolor, no cache — the seat dimension never
    touched this function even before (only the LIVE shadow,
    `render.layers._draw_subdial_shadow`, keyed off the seat's own dial
    position, does). The SOLO set ships one hand-drawn file
    (`defaults.SUBDIAL_SOLO_FINISH`, silver): silver wins AS DRAWN,
    gold/bronze are disk-cached live recolors of it, exactly like the
    ring letters derive silver/bronze from gold. A TINT (the "theme"
    plate style, owner 2026-07-15 A/B spec) recolors the dark
    tapisserie field to the clock tint on TOP of whichever plate above
    was resolved — that pass runs even on an already-correct finish,
    into its own cache entry. None = no plate art at all for the active
    set (the layer then draws the procedural circle)."""
    active_set = paths.subdial_set()
    if active_set == "solo":
        master = (
            defaults.SUBDIAL_ROOT_DIR / "solo"
            / f"{defaults.SUBDIAL_SOLO_FINISH}.png"
        )
        if not master.exists():
            return None
        if finish == defaults.SUBDIAL_SOLO_FINISH and tint is None:
            return master
        return _recolored_plate(master, finish, tint)
    plate = defaults.SUBDIAL_ROOT_DIR / active_set / f"{finish}.png"
    if not plate.exists():
        return None
    if tint is None:
        return plate
    return _recolored_plate(plate, finish, tint)


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


def eclipse_solar_type_icon(type_: str) -> Path | None:
    """The small per-type SOLAR eclipse icon (ECLIPSE ICON WIRING round,
    owner 2026-07-20/21 — the solar pick is PROPOSED, not yet owner-
    confirmed the way lunar's red/gold/blue set is; see
    `defaults.ECLIPSE_SOLAR_TYPE_ICON_SOURCE`'s docstring for the shape-
    matched mapping). Total and partial ride their source file AS
    DRAWN; annular is TRITONE-tinted toward
    `defaults.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR` (the SAME "ring of
    fire" color the dial's own annular glow already uses — Rule #5, one
    color, two places) via `tinted_pixmap`, disk-cached like every
    other derived asset. None for an unknown type or a source that has
    not landed (Rule #1, graceful-absent)."""
    source = defaults.ECLIPSE_SOLAR_TYPE_ICON_SOURCE.get(type_)
    if source is None or not source.exists():
        return None
    if type_ != "annular":
        return source
    stamp = hashlib.sha1(str(source).encode("utf-8")).hexdigest()[:16]
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_{int(source.stat().st_mtime)}_eclipse_annular_tint.png"
    )
    if not cache.exists():
        pixmap = QPixmap(str(source))
        if pixmap.isNull():
            raise ValueError(f"cannot load image asset: {source}")
        tinted = tinted_pixmap(
            pixmap, defaults.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
        )
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            if not tinted.save(str(cache)):
                raise OSError(f"QPixmap.save returned False for {cache}")
        except OSError as error:
            # A cold cache is only slower, never wrong — but say so.
            print(
                f"eclipse annular icon cache write failed: {error}",
                file=sys.stderr,
            )
            return source
    return cache


def calendar_wheel_icon_file(size: int) -> Path:
    """A COMPUTED 12-wedge wheel glyph at `size` px (Rule #19 — no new
    art file) for the Fast Travel Flash's Calendar theme, replacing the
    plain 📅 emoji fallback (owner ask, ECLIPSE ICON WIRING round
    2026-07-20/21): 12 alternating wedges in `defaults.
    CALENDAR_ICON_WEDGE_COLORS` (the app's own gold ramp) with a thin
    dark ring for contrast against the flash's dark background. Disk-
    cached by SIZE alone — the drawing has no other input, so a given
    size paints exactly once per install. There is no source master to
    fall back to on a write failure (unlike every other cache function
    here), so a failed save raises rather than silently returning an
    uncached path (Rule #1)."""
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"calendar_wheel_icon_{size}.png"
    )
    if cache.exists():
        return cache
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    ring_width = max(1.0, size * defaults.CALENDAR_ICON_RING_WIDTH_FRACTION)
    radius = size / 2.0 - ring_width
    rect = QRectF(
        size / 2.0 - radius, size / 2.0 - radius, 2.0 * radius, 2.0 * radius
    )
    wedges = defaults.CALENDAR_ICON_WEDGE_COUNT
    colors = [QColor(c) for c in defaults.CALENDAR_ICON_WEDGE_COLORS]
    span_deg = 360.0 / wedges
    painter.setPen(Qt.PenStyle.NoPen)
    for index in range(wedges):
        painter.setBrush(colors[index % len(colors)])
        # QPainter angles are in 1/16ths of a degree, counterclockwise
        # from 3 o'clock — the exact sweep direction/units are cosmetic
        # here (a symmetric wheel reads identically either way).
        painter.drawPie(rect, round(index * span_deg * 16), round(span_deg * 16))
    painter.setPen(QPen(QColor(defaults.CALENDAR_ICON_RING_COLOR), ring_width))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(rect)
    painter.end()
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        if not image.save(str(cache)):
            raise OSError(f"QImage.save returned False for {cache}")
    except OSError as error:
        print(f"calendar wheel icon cache write failed: {error}", file=sys.stderr)
        raise
    return cache
