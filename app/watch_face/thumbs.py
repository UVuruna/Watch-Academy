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
from PySide6.QtGui import (
    QBrush, QColor, QConicalGradient, QFont, QIcon, QImage, QPainter,
    QPixmap,
)

from config import constants, dial, palette, paths
from core import angles
from render import letter_plates, raster_store
from render.daylight import umbra_ladder
from render.painting import dial_point, draw_pie, tinted_gray

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


def _computed_icon(name: str, paint) -> QIcon:
    """The shared skeleton every COMPUTED (sourceless) preview follows
    (Rule #5, the `pointer_swatch_icon` convention): a transparent
    `THUMB_SOURCE_PX` canvas handed to `paint(painter)`, disk-cached
    under a computed name (kept, never swept — no 16-hex stamp)."""
    cache_path = _cache_dir() / f"{name}_v{_THUMB_CACHE_VERSION}.png"
    if cache_path.exists():
        return QIcon(str(cache_path))
    image = QImage(
        THUMB_SOURCE_PX, THUMB_SOURCE_PX, QImage.Format.Format_ARGB32
    )
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.translate(THUMB_SOURCE_PX / 2.0, THUMB_SOURCE_PX / 2.0)
    try:
        paint(painter)
    finally:
        painter.end()
    try:
        raster_store.atomic_save(image, cache_path)
    except OSError:
        return QIcon(QPixmap.fromImage(image))
    return QIcon(str(cache_path))


def umbra_icon(form: str, contrast: str) -> QIcon:
    """The Umbra form/contrast preview — THE REAL ALGORITHM at
    thumbnail scale (owner order 2026-08-09: every picker shows what it
    picks; Rule #19 compute-don't-fake): the same `umbra_ladder`,
    `UMBRA_CONTRAST_SPANS` window and conical gradient the dial's
    BackgroundLayer paints, untinted (the preview is about FORM and
    CONTRAST — the tint is a different picker)."""
    radius = THUMB_SOURCE_PX * 0.46

    def paint(painter: QPainter) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        lightest, darkest = dial.UMBRA_CONTRAST_SPANS[contrast]
        lightest = min(255, lightest)
        if form == "gradient":
            gradient = QConicalGradient(QPointF(0.0, 0.0), 90.0)
            gradient.setColorAt(0.0, tinted_gray(lightest, None))
            gradient.setColorAt(0.5, tinted_gray(darkest, None))
            gradient.setColorAt(1.0, tinted_gray(lightest, None))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
            return
        sections = constants.UMBRA_SECTION_COUNTS[form]
        span = 360.0 / sections
        shades = umbra_ladder(sections // 2 + 1, contrast)
        for k, value in enumerate(shades):
            painter.setBrush(tinted_gray(value, None))
            center = k * span
            draw_pie(painter, radius, center - span / 2, center + span / 2)
            if 0 < k < len(shades) - 1:
                draw_pie(
                    painter, radius,
                    360.0 - center - span / 2, 360.0 - center + span / 2,
                )

    return _computed_icon(f"umbra_{form}_{contrast}", paint)


def complication_icon(mode: str) -> QIcon:
    """The Complications picker's honest sketches (owner order
    2026-08-09; his own instruction allows "sliku ILI skicu"): each
    option draws COMPUTED content on the dial (text, a tick ring — the
    recon proved there is no bounded per-complication render door), so
    the preview draws the same KIND of content on a slot-like roundel."""
    radius = THUMB_SOURCE_PX * 0.42

    def roundel(painter: QPainter) -> None:
        painter.setPen(QColor(palette.THEME_COLORS["border"]))
        painter.setBrush(QColor(palette.THEME_COLORS["surface_2"]))
        painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))

    def text_center(painter: QPainter, text: str, px: int) -> None:
        font = QFont()
        font.setPixelSize(px)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(palette.THEME_COLORS["text_primary"]))
        painter.drawText(
            QRectF(-radius, -radius, 2 * radius, 2 * radius),
            Qt.AlignmentFlag.AlignCenter, text,
        )

    def paint(painter: QPainter) -> None:
        roundel(painter)
        if mode == "time":
            text_center(painter, "12:34", int(radius * 0.62))
        elif mode == "date":
            text_center(painter, "9 AUG", int(radius * 0.4))
        elif mode == "day_length":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(palette.THEME_COLORS["accent"]))
            draw_pie(painter, radius * 0.8, -100.0, 100.0)
            painter.setBrush(QColor(palette.THEME_COLORS["surface_1"]))
            draw_pie(painter, radius * 0.8, 100.0, 260.0)
            text_center(painter, "14h", int(radius * 0.45))
        elif mode == "seconds":
            painter.setPen(QColor(palette.THEME_COLORS["text_secondary"]))
            for k in range(8):
                theta = k * 45.0
                outer = dial_point(theta, radius * 0.82)
                inner = dial_point(theta, radius * 0.66)
                painter.drawLine(outer, inner)
            painter.setPen(QColor(palette.THEME_COLORS["accent"]))
            painter.drawLine(QPointF(0, 0), dial_point(215.0, radius * 0.74))

    return _computed_icon(f"complication_{mode}", paint)


def text_style_icon(label: str) -> QIcon:
    """The zodiac/chinese "Text" style's sketch — that style draws the
    NAME instead of art, so the preview is a name on the slot roundel."""
    radius = THUMB_SOURCE_PX * 0.42

    def paint(painter: QPainter) -> None:
        painter.setPen(QColor(palette.THEME_COLORS["border"]))
        painter.setBrush(QColor(palette.THEME_COLORS["surface_2"]))
        painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
        font = QFont()
        font.setPixelSize(int(radius * 0.42))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(palette.THEME_COLORS["text_primary"]))
        painter.drawText(
            QRectF(-radius, -radius, 2 * radius, 2 * radius),
            Qt.AlignmentFlag.AlignCenter, label,
        )

    return _computed_icon(f"textstyle_{label}", paint)


def metal_swatch_icon(hue: str) -> QIcon:
    """A small round swatch of one metal SHADE's own hue — the Metal
    shades combos show WHAT each shade looks like (owner order
    2026-08-09), straight from the ramp color, never hand-picked."""
    radius = THUMB_SOURCE_PX * 0.34

    def paint(painter: QPainter) -> None:
        painter.setPen(QColor(palette.THEME_COLORS["border"]))
        painter.setBrush(QColor(hue))
        painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))

    return _computed_icon(f"metal_swatch_{hue.lstrip('#')}", paint)


def subdial_set_icon(set_name: str) -> QIcon | None:
    """One Subdial plate SET's preview — the set's OWN three metal
    plates (gold | bronze | silver) side by side in one icon (owner
    order 2026-08-09: "slicicu kako izgleda taj odabir za sve 3
    verzije"). Sets 1-4 read their three hand-drawn files; the solo
    set's gold/bronze are DERIVED from its silver master through the
    same recolor door the dial itself uses (`render.asset_variants.
    subdial_plate_file` under a per-set display context) — computed,
    never invented. Missing art -> None (honest blank tile)."""
    from render.asset_variants import subdial_plate_file

    sources = []
    for finish in ("gold", "bronze", "silver"):
        try:
            with paths.display(paths.display_context(subdial_set=set_name)):
                resolved = subdial_plate_file(finish)
        except Exception:
            resolved = None
        if resolved is None or not Path(resolved).exists():
            return None
        sources.append(Path(resolved))
    digest = hashlib.sha1("|".join(
        raster_store.source_prefix(source) for source in sources
    ).encode("utf-8")).hexdigest()[:16]
    cache_path = (
        _cache_dir()
        / f"subdial_set_{set_name}_{digest}_v{_THUMB_CACHE_VERSION}.png"
    )
    if cache_path.exists():
        return QIcon(str(cache_path))
    slot = THUMB_SOURCE_PX // 3
    canvas = QImage(
        THUMB_SOURCE_PX, THUMB_SOURCE_PX, QImage.Format.Format_ARGB32
    )
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    for index, source in enumerate(sources):
        image = QImage(str(source))
        if image.isNull():
            painter.end()
            return None
        scaled = image.scaled(
            slot, THUMB_SOURCE_PX,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawImage(
            QPointF(
                index * slot + (slot - scaled.width()) / 2.0,
                (THUMB_SOURCE_PX - scaled.height()) / 2.0,
            ),
            scaled,
        )
    painter.end()
    try:
        raster_store.atomic_save(canvas, cache_path)
    except OSError:
        return QIcon(QPixmap.fromImage(canvas))
    return QIcon(str(cache_path))


def art_source_icon(source: str, theme: str) -> QIcon | None:
    """The Artwork picker's preview (owner order 2026-08-09): the
    ACTIVE weekday theme's Sun plate resolved UNDER `source`
    (gemini/chatgpt), falling back to the generic planetary Sun when
    the theme has no plate in that source — exactly the fallback the
    dial itself runs."""
    from datetime import date

    from config import pantheon

    with paths.display(paths.display_context(art_source=source)):
        candidate = paths.art_file(pantheon.weekday_theme_body_art(
            theme, "sun", on_date=date.today(),
        ))
        if candidate is None or not candidate.exists():
            candidate = paths.art_file(
                pantheon.weekday_theme_body_art("planets", "sun")
            )
    return art_thumbnail(candidate)


def art_source_dual_icon(source: str, theme: str) -> QIcon | None:
    """The theme's SUNDAY DUAL under `source`, when the theme carries
    one on disk — None otherwise (the gallery simply shows no dual
    row; graceful absence, never a stand-in)."""
    from config import pantheon

    rel = pantheon.WEEKDAY_DUAL_FILES.get(theme)
    if rel is None:
        return None
    with paths.display(paths.display_context(art_source=source)):
        candidate = paths.existing_art_file(pantheon.weekday_art(f"{rel}.png"))
    if candidate is None:
        return None
    return art_thumbnail(candidate)


def shade_hue(metal: str, shade: str) -> str | None:
    """One metal SHADE's representative hue — the ramp's own mid stop
    (~0.55) read straight from `recolor/presets/metals.json` through
    the SAME name mapping the dial's recolor uses
    (`defaults.METAL_SHADES`). Never hand-picked; None when the ramp
    is absent (honest no-icon)."""
    import json

    from config import defaults
    from recolor.recipe import PRESETS

    ramp_name = defaults.METAL_SHADES.get(metal, {}).get(shade)
    if ramp_name is None:
        return None
    try:
        data = json.loads(Path(PRESETS).read_text(encoding="utf-8"))
        stops = data["metals"][ramp_name]["stops"]
    except (OSError, KeyError, ValueError):
        return None
    return min(stops, key=lambda stop: abs(stop[0] - 0.55))[1]
