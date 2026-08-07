"""The Watch Face thumbnail service (R-33, see thumbs.md) — every
gallery in the Watch Face window (Ring, Hands, Pointer's Earth tiles)
draws its icon from here, never loading a raw `QIcon(path)` itself.

Disk cache: REUSES `render.raster_store`'s content-fingerprint naming
(`source_prefix`/`atomic_save`) verbatim — the SAME cache convention the
ring-jewel metal recolor cache (`render/asset_recolor.py`) already
uses (Rule #5, no second cache mechanism). A cached thumbnail survives a
git checkout exactly like the jewel cache does, and `raster_store.
collect_garbage` sweeps a stale one the same way.

Honest fallback (R-33, documented rather than faked): POINTER variants
carry NO dedicated preview art — `design_window.md`'s own asset-honesty
note already establishes this (they are procedural/abstract) — and no
render path in `render/layers/*.py` or `render/skin_geometry.py` can
compose a small preview without a fully-built `Skin` (every `Layer.
draw()` takes the complete object; there is no bounded
"just a pointer + a palette" entry point). `pointer_swatch_icon`
therefore composes a preview from the pointer's OWN active palette
wheel (`config.palette.PALETTE_PRESETS`) instead — real derived content,
not invented art.
"""

import hashlib
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap

from config import constants, dial, palette, paths
from core import angles
from render import letter_plates, raster_store
from render.painting import dial_point

# The source render size every thumbnail is produced at — every gallery
# displays it scaled down through Qt's own icon scaling, so one cached
# raster serves every tile size a section might want.
THUMB_SOURCE_PX = 256
# Bumped whenever the paint recipe below changes, so a stale pre-bump
# cache file is never mistaken for the new recipe's output.
_THUMB_CACHE_VERSION = 1


def _cache_dir() -> Path:
    return paths.settings_path().parent / "raster_cache"


def art_thumbnail(source: Path | None) -> QIcon | None:
    """A 256px-source, disk-cached thumbnail of an existing art file (a
    ring preset's face, a hand pack's hours image). Returns `None` when
    the source is missing or unreadable — the caller's own documented
    no-icon fallback (matching `design_window._tile`'s contract: a
    missing source shows a bare label, never a broken icon)."""
    resolved = paths.art_file(source) if source is not None else None
    if resolved is None or not resolved.exists():
        return None
    cache_path = (
        _cache_dir()
        / f"{raster_store.source_prefix(resolved)}_thumb_v{_THUMB_CACHE_VERSION}.png"
    )
    if cache_path.exists():
        return QIcon(str(cache_path))
    image = QImage(str(resolved))
    if image.isNull():
        return None
    scaled = image.scaled(
        THUMB_SOURCE_PX, THUMB_SOURCE_PX,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    try:
        raster_store.atomic_save(scaled, cache_path)
    except OSError:
        # A cold cache is only slower, never wrong (the repository's
        # documented fallback contract) — still hand back the icon.
        return QIcon(QPixmap.fromImage(scaled))
    return QIcon(str(cache_path))


def ring_preset_thumbnail(card: dict) -> QIcon | None:
    """The RING PRESET PICKER's own mini preview (ring_rework §5, owner
    ruling 2026-08-06: "preset picker: name + mini SVG preview + the
    About" — SVG in the ledger's shorthand, PNG in this codebase's
    actual asset library; owner law "compute, don't generate" is kept:
    this composes the card's OWN outer plate and OWN jewel masters at
    thumbnail scale, never a stored/generated image). Geometry mirrors
    `render.layers.ring.RingLayer._draw_jewels` at zero world
    offset (a picker preview is never mid-rotation) — gold masters only
    (no recolor pass: identification, not a faithful finish preview).
    Disk-cached like every other thumbnail; the cache name folds in
    every source file's own content fingerprint (Rule #5's "computed
    name" convention `pointer_swatch_icon` already uses, extended with
    a real fingerprint since — unlike a palette wheel's own Python
    values — these sources are art files that DO change on disk)."""
    outer = constants.RING_OUTERS[card["outer"]]
    outer_path = paths.art_file(dial.RING_OUTER_ART_DIR / outer["file"])
    if outer_path is None or not outer_path.exists():
        return None
    sources = [outer_path]
    for jewel in card["jewels"]:
        jewel_path = paths.art_file(
            letter_plates.plate_path(jewel)
        )
        if jewel_path is not None and jewel_path.exists():
            sources.append(jewel_path)
    digest = hashlib.sha1(
        "|".join(raster_store.source_prefix(p) for p in sources).encode("utf-8")
    ).hexdigest()[:16]
    cache_path = (
        _cache_dir()
        / f"ring_preview_{card['name']}_{digest}_v{_THUMB_CACHE_VERSION}.png"
    )
    if cache_path.exists():
        return QIcon(str(cache_path))
    outer_image = QImage(str(outer_path)).scaled(
        THUMB_SOURCE_PX, THUMB_SOURCE_PX,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    if outer_image.isNull():
        return None
    canvas = QImage(
        outer_image.width(), outer_image.height(), QImage.Format.Format_ARGB32
    )
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.translate(canvas.width() / 2.0, canvas.height() / 2.0)
    painter.drawImage(
        QPointF(-outer_image.width() / 2.0, -outer_image.height() / 2.0),
        outer_image,
    )
    radius = canvas.width() / 2.0
    jewel_height = 2 * radius * dial.RING_JEWEL_ART_SCALE
    for position, jewel in zip(card["positions"], card["jewels"]):
        jewel_path = paths.art_file(
            letter_plates.plate_path(jewel)
        )
        if jewel_path is None or not jewel_path.exists():
            continue
        glyph = QImage(str(jewel_path))
        if glyph.isNull():
            continue
        glyph = glyph.scaledToHeight(
            max(1, round(jewel_height)),
            Qt.TransformationMode.SmoothTransformation,
        )
        theta = angles.ring_position_angle(position)
        center = dial_point(theta, radius * dial.RING_JEWEL_RADIUS_FRACTION)
        painter.drawImage(
            QPointF(
                center.x() - glyph.width() / 2.0,
                center.y() - glyph.height() / 2.0,
            ),
            glyph,
        )
    painter.end()
    try:
        raster_store.atomic_save(canvas, cache_path)
    except OSError:
        return QIcon(QPixmap.fromImage(canvas))
    return QIcon(str(cache_path))


def pointer_swatch_icon(pointer: str, style: str) -> QIcon:
    """The honest pointer-variant fallback (see module docstring): a
    pie of the pointer's ACTIVE palette wheel's own hues, drawn once at
    `THUMB_SOURCE_PX` and disk-cached under a COMPUTED name — there is
    no source file to fingerprint, so the cache name carries no stamp
    prefix, the SAME "computed icon" convention
    `render.asset_variants.calendar_wheel_icon_file` already uses (kept,
    never swept, by `raster_store.collect_garbage`'s own carve-out for
    names whose first field is not a 16-hex stamp)."""
    style = palette.effective_palette_style(pointer, style)
    hues = palette.PALETTE_PRESETS.get((pointer, style))
    if not hues:
        return QIcon()
    cache_path = (
        _cache_dir()
        / f"pointer_swatch_{pointer}_{style}_v{_THUMB_CACHE_VERSION}.png"
    )
    if cache_path.exists():
        return QIcon(str(cache_path))
    image = _paint_swatch(hues)
    try:
        raster_store.atomic_save(image, cache_path)
    except OSError:
        return QIcon(QPixmap.fromImage(image))
    return QIcon(str(cache_path))


def _paint_swatch(hues: tuple) -> QImage:
    """A simple pie chart of `hues`, one wedge per hue, clockwise from
    the top — cheap, bounded, no numpy/oklab work (unlike the letter
    metal recolor this deliberately does NOT reuse: that recipe needs a
    real source alpha mask this procedural swatch has none of)."""
    image = QImage(
        THUMB_SOURCE_PX, THUMB_SOURCE_PX, QImage.Format.Format_ARGB32
    )
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    margin = THUMB_SOURCE_PX * 0.05
    rect = QRectF(
        margin, margin, THUMB_SOURCE_PX - 2 * margin, THUMB_SOURCE_PX - 2 * margin
    )
    painter.setPen(Qt.PenStyle.NoPen)
    span = round(360 * 16 / len(hues))
    # Qt's drawPie angles are counter-clockwise from the 3 o'clock mark;
    # started at the top (90 * 16) to match the dial's own convention
    # (degrees clockwise from the top).
    start = 90 * 16
    for hue in hues:
        painter.setBrush(QColor(hue))
        painter.drawPie(rect, start, -span)
        start -= span
    painter.end()
    return image
