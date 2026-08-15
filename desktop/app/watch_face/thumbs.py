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
from datetime import date, datetime
from datetime import time as _dt_time
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush, QColor, QConicalGradient, QFont, QIcon, QImage,
    QLinearGradient, QPainter, QPainterPath, QPen, QPixmap,
    QRadialGradient,
)

from config import constants, dial, glow, palette, paths
from core import angles
from render import letter_plates, marker_marks, moon_face, raster_store
from render.daylight import umbra_ladder
from render.eclipse_glow import draw_event_glow
from render.painting import dial_point, draw_pie, tinted_gray

# The source render size every thumbnail is produced at — every gallery
# displays it scaled down through Qt's own icon scaling, so one cached
# raster serves every tile size a section might want.
THUMB_SOURCE_PX = 256
# Bumped whenever the paint recipe below changes, so a stale pre-bump
# cache file is never mistaken for the new recipe's output.
_THUMB_CACHE_VERSION = 7   # 7: the ballot's six eclipse styles got real painters (2026-08-13)


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
    `render.asset_variants.calendar_sheet_icon_file` already uses (kept,
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


def _computed_icon(name: str, paint, ground: str | None = None) -> QIcon:
    """The shared skeleton every COMPUTED (sourceless) preview follows
    (Rule #5, the `pointer_swatch_icon` convention): a
    `THUMB_SOURCE_PX` canvas handed to `paint(painter)`, disk-cached
    under a computed name (kept, never swept — no 16-hex stamp).

    `ground` fills the canvas with an opaque colour instead of leaving
    it transparent. THE DEFECT THAT EARNED IT (visual proof round
    2026-08-10): a QToolButton that is NOT the selected tile paints a
    LIGHT background, so any preview drawn for the dial's dark sky —
    a silver moon, a silver horizon thread, a faint ghost disc — went
    from unreadable to actively misleading the moment it was not the
    current pick. Photo-sourced tiles never showed this because their
    art carries its own opaque ground. A preview of something that only
    exists against the night must bring the night with it."""
    cache_path = _cache_dir() / f"{name}_v{_THUMB_CACHE_VERSION}.png"
    if cache_path.exists():
        return QIcon(str(cache_path))
    image = QImage(
        THUMB_SOURCE_PX, THUMB_SOURCE_PX, QImage.Format.Format_ARGB32
    )
    if ground is not None:
        image.fill(QColor(ground))
    else:
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


# How far past the tile the band preview's dial radius is pushed. At 1.0
# the whole ring fits and the fine styles blur together (see
# `moon_band_style_icon`); this is the magnification that makes one tick
# and one bloom readable at the displayed size.
_BAND_PREVIEW_ZOOM = 1.5

_MOON_BAND_DEMO_RISE = _dt_time(6, 0)
_MOON_BAND_DEMO_SET = _dt_time(18, 0)
# THE DANJON TILE's own body size and lift, MEASURED against
# `render.eclipse_danjon`'s gauge rather than eyeballed: the gauge stops
# 2.30 body radii below centre, so the whole mark is 3.30 radii tall and
# 2.40 wide. The tile is `THUMB_SOURCE_PX` square and the other lunar
# tiles draw at 0.40 of it, so the body here shrinks to 0.72 of that
# (3.30 x 0.70 x 0.40 = 0.92 of the tile, height being the binding
# dimension) and rises by (2.30 - 1) / 2 = 0.65 body radii to centre the
# drawn extent.
_DANJON_TILE_BODY_SCALE = 0.70
_DANJON_TILE_LIFT = 0.65


def moon_band_style_icon(style: str) -> QIcon:
    """The Moon Horizon Band style picker's preview — THE REAL
    ALGORITHM at thumbnail scale (owner order 2026-08-09): calls
    `render.layers.moon_band.MoonBandLayer`'s own `_draw_*` style
    methods directly on a bare canvas (they take only a painter, a
    radius and a `MoonArc` — no full `RenderContext` — so this is the
    SAME code the dial paints with, not a redrawn sketch of it) against
    a fixed demo arc (06:00-18:00, a plain daytime-visible span with no
    None-day branch to illustrate)."""
    from core.moon import moon_horizon_arcs
    from render.layers.moon_band import MoonBandLayer

    radius = THUMB_SOURCE_PX * _BAND_PREVIEW_ZOOM
    arc = moon_horizon_arcs(
        datetime.combine(date(2000, 1, 1), _MOON_BAND_DEMO_RISE),
        datetime.combine(date(2000, 1, 1), _MOON_BAND_DEMO_SET),
    )[0]
    layer = MoonBandLayer.__new__(MoonBandLayer)
    dispatch = {
        "inverted": layer._draw_inverted,
        "ticks": layer._draw_ticks,
        "glow": layer._draw_glow,
    }.get(style, layer._draw_silver_thread)

    def paint(painter: QPainter) -> None:
        # DRAWN MAGNIFIED, as a SEGMENT of the band rather than the whole
        # ring. Fitting the entire circle into the tile collapsed two of
        # the four styles into the same picture — the ticks (one per
        # degree, matching the baked art) packed into a solid line and
        # the glow's bloom shrank below a pixel; an independent grader
        # diffed the two tiles and found them indistinguishable to the
        # eye, a straight violation of "every tile shows what it picks".
        # This is the SAME code and the same real geometry, simply seen
        # closer — what a preview of a fine texture has to do. The dial's
        # own appearance is untouched.
        painter.translate(0.0, radius)
        pen = QPen(QColor(palette.NUMERAL_RING_GROUND))
        pen.setWidthF(max(1.0, radius * 0.006))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
        dispatch(painter, radius, arc)

    return _computed_icon(
        f"moon_band_style_{style}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


def moon_band_mode_icon(mode: str) -> QIcon:
    """The Moon Horizon Band MODE picker's preview: "horizon" shows the
    same real silver-thread arc `moon_band_style_icon` draws (the band
    IS the mode's defining feature); "dim_only" shows a dimmed moon
    disc (today's `moon_hidden_alpha` behavior, no band); "always_full"
    shows a full-brightness disc, no band — matching what each mode
    actually changes on the dial."""
    from core.moon import moon_horizon_arcs
    from render.layers.moon_band import MoonBandLayer

    radius = THUMB_SOURCE_PX * 0.46

    def paint(painter: QPainter) -> None:
        pen = QPen(QColor(palette.NUMERAL_RING_GROUND))
        pen.setWidthF(radius * 0.03)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
        if mode == "horizon":
            arc = moon_horizon_arcs(
                datetime.combine(date(2000, 1, 1), _MOON_BAND_DEMO_RISE),
                datetime.combine(date(2000, 1, 1), _MOON_BAND_DEMO_SET),
            )[0]
            layer = MoonBandLayer.__new__(MoonBandLayer)
            layer._draw_silver_thread(painter, radius, arc)
            return
        moon_radius = radius * 0.16
        color = QColor(palette.MOON_SILVER)
        if mode == "dim_only":
            color.setAlphaF(0.5)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(QPointF(0.0, 0.0), moon_radius, moon_radius)

    return _computed_icon(
        f"moon_band_mode_{mode}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


def moon_dark_style_icon(style: str) -> QIcon:
    """THE UNLIT HALF picker's preview (owner verdict 2026-08-10) — THE
    REAL ALGORITHM at thumbnail scale: `moon_face.draw_moon_disc` at a
    thin crescent (fraction 0.08 — the styles read almost identically
    at half-full, the whole point of "opaque"/"cut_ghost"/"cut_rim" is
    how they treat a near-empty disc)."""
    radius = THUMB_SOURCE_PX * 0.4

    def paint_face(target: QPainter) -> None:
        target.setBrush(QColor(palette.SKIN_MOON_LIT))
        target.drawEllipse(QPointF(0.0, 0.0), radius, radius)

    def paint(painter: QPainter) -> None:
        moon_face.draw_moon_disc(
            painter, 0.08, radius, style, paint_face, palette.SKIN_MOON_DARK,
        )

    return _computed_icon(
        f"moon_dark_style_{style}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


def moon_transit_style_icon(style: str) -> QIcon:
    """THE CROSSING picker's preview: the same lane-split/shrink-pass
    fractions `render.layers.year_marker.YearMarkerLayer` reads off
    `config.dial` at a fixed deep-transit position (the two bodies
    meeting head-on), a bigger Earth disc and a smaller Moon disc drawn
    with `moon_face.draw_moon_disc` — the real disc paint, only the
    two bodies' RELATIVE placement is reproduced here since the layer
    has no bounded "just the crossing" render door of its own."""
    earth_radius = THUMB_SOURCE_PX * 0.32
    moon_radius = earth_radius * 0.5
    touch = earth_radius + moon_radius

    def paint(painter: QPainter) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(palette.SKIN_EARTH_DAY))
        painter.drawEllipse(QPointF(0.0, 0.0), earth_radius, earth_radius)
        if style == "lane_split":
            # The lane eases INWARD but the two discs never overlap —
            # shown just short of touching distance.
            moon_x = touch * (1.0 - dial.MOON_LANE_SPLIT_FRACTION * 2)
            this_moon_radius = moon_radius
        elif style == "shrink_pass":
            # Deep inside the Earth's disc, scaled DOWN by the ramp's
            # own depth constant.
            moon_x = earth_radius * 0.15
            this_moon_radius = moon_radius * (1.0 - dial.MOON_SHRINK_PASS_DEPTH)
        else:
            if style != "occultation":
                raise ValueError(f"unknown moon transit style {style!r}")
            # Fully opaque, in front, with a soft shadow cast on Earth.
            moon_x = earth_radius * 0.30
            this_moon_radius = moon_radius
            shadow = QColor(palette.SKIN_MOON_DARK)
            shadow.setAlphaF(0.35)
            painter.setBrush(shadow)
            painter.drawEllipse(
                QPointF(moon_x, 0.0), this_moon_radius * 1.25, this_moon_radius * 1.25,
            )

        def paint_face(target: QPainter) -> None:
            target.setBrush(QColor(palette.SKIN_MOON_LIT))
            target.drawEllipse(
                QPointF(0.0, 0.0), this_moon_radius, this_moon_radius
            )

        painter.save()
        painter.translate(moon_x, 0.0)
        moon_face.draw_moon_disc(
            painter, 0.8, this_moon_radius, "opaque", paint_face,
            palette.SKIN_MOON_DARK,
        )
        painter.restore()

    return _computed_icon(
        f"moon_transit_style_{style}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


def marker_pointer_shape_icon(shape: str) -> QIcon:
    """THE POSITION POINTER's own preview — `marker_marks.draw_pointer`
    at angle 0 (straight up in this icon's own frame) plus a thin ring
    line marking the orbit lane it straddles, so the shape reads in
    context rather than floating alone."""
    dial_radius = THUMB_SOURCE_PX * 0.42
    orbit_fraction = 0.55
    half_size_fraction = 0.16

    def paint(painter: QPainter) -> None:
        pen = QPen(QColor(palette.THEME_COLORS["border"]))
        pen.setWidthF(dial_radius * 0.02)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        orbit_radius = dial_radius * orbit_fraction
        painter.drawEllipse(
            QRectF(-orbit_radius, -orbit_radius, 2 * orbit_radius, 2 * orbit_radius)
        )
        body_radius = dial_radius * half_size_fraction
        body_center = dial_point(0.0, orbit_radius)
        painter.setPen(QPen(QColor(*palette.MARKER_BORDER_RGBA)))
        painter.setBrush(QColor(palette.SKIN_EARTH_DAY))
        painter.drawEllipse(body_center, body_radius, body_radius)
        marker_marks.draw_pointer(
            painter, shape, 0.0, dial_radius, orbit_fraction,
            half_size_fraction, palette.GLOW_MOON_COLOR,
        )

    return _computed_icon(
        f"marker_pointer_shape_{shape}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


def eclipse_solar_style_icon(style: str) -> QIcon:
    """THE SOLAR ECLIPSE picker's preview — a plain Sun disc under
    `marker_marks.draw_solar_eclipse` at a fixed demo (partial,
    magnitude 0.6, THE REAL ALGORITHM). "halo" draws nothing onto the
    body itself (the glow behind IS that style, `render.eclipse_glow.
    draw_event_glow` — drawn here too so the tile is not a bare Sun).
    The three ballot-accepted names with no painter yet
    (`totality_path`/`type_emblem`/`dial_shadow`, owner ballot
    2026-08-13) preview whatever `draw_solar_eclipse` falls back to —
    it asks `render.eclipse_style.resolve_eclipse_style` itself, so
    this tile needs no branch of its own."""
    radius = THUMB_SOURCE_PX * 0.36

    def paint(painter: QPainter) -> None:
        draw_event_glow(
            painter, QPointF(0.0, 0.0), radius,
            palette.GLOW_ECLIPSE_SOLAR_COLOR, 1.0,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(palette.GLOW_SUN_COLOR))
        painter.drawEllipse(QPointF(0.0, 0.0), radius, radius)
        marker_marks.draw_solar_eclipse(
            painter, style, radius, "solar_partial", 0.6,
            palette.GLOW_SUN_COLOR,
        )

    return _computed_icon(
        f"eclipse_solar_style_{style}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


def eclipse_lunar_style_icon(style: str) -> QIcon:
    """THE LUNAR ECLIPSE picker's preview at a fixed demo (partial,
    magnitude 0.6). "umbra_sweep" calls `moon_face.draw_umbra_sweep`
    (THE REAL ALGORITHM); "halo" reproduces the SAME multiply-darken
    `YearMarkerLayer._draw_moon` applies; "horizon_shadow" draws the
    Moon Horizon Band's own silver-thread arc instead of touching the
    disc at all — the owner's own placement of that option (2026-08-10)
    — reusing `MoonBandLayer._draw_silver_thread` exactly like
    `moon_band_mode_icon` already does. The three ballot-accepted names
    with no painter yet (`blood_moon`/`danjon_scale`/`contact_marks`,
    owner ballot 2026-08-13) preview whatever
    `render.eclipse_style.resolve_eclipse_style` falls back to."""
    from datetime import date, datetime

    from core.moon import moon_horizon_arcs
    from render.eclipse_style import resolve_eclipse_style
    from render.layers.moon_band import MoonBandLayer

    radius = THUMB_SOURCE_PX * 0.4
    # THE DOOR (owner ballot 2026-08-13): `blood_moon`/`danjon_scale`/
    # `contact_marks` have no painters yet — the tile previews whatever
    # `resolve_eclipse_style` says (band presumed up, same as the
    # Encyclopedia plates), so a new picker entry never crashes and
    # never shows a picture it does not actually draw.
    effective_style, _fallback_reason = resolve_eclipse_style(
        "lunar", style, band_available=True,
    )

    def paint(painter: QPainter) -> None:
        if effective_style in ("horizon_shadow", "contact_marks"):
            pen = QPen(QColor(palette.NUMERAL_RING_GROUND))
            pen.setWidthF(radius * 0.03)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
            arc = moon_horizon_arcs(
                datetime.combine(date(2000, 1, 1), _MOON_BAND_DEMO_RISE),
                datetime.combine(date(2000, 1, 1), _MOON_BAND_DEMO_SET),
            )[0]
            layer = MoonBandLayer.__new__(MoonBandLayer)
            layer._draw_silver_thread(painter, radius, arc)
            # THE ECLIPSE ITSELF, not merely the band it is written on.
            # The first cut of this tile drew the bare arc and an
            # independent grader read it as an empty circle — it
            # advertised nothing, which is the exact failure the
            # "every tile shows what it picks" rule exists to prevent.
            centre_deg = angles.time_to_dial_angle(_dt_time(12, 0))
            layer.draw_eclipse_segment(
                painter, radius, centre_deg, "lunar_total",
            )
            if effective_style == "contact_marks":
                # An ADDITION on top of the segment (owner ballot
                # 2026-08-13) — the tile shows exactly that, so the two
                # band styles never advertise the same picture.
                layer.draw_contact_marks(
                    painter, radius, centre_deg, "lunar_total",
                )
            return
        if effective_style == "danjon_scale":
            from render import eclipse_danjon
            from render.eclipse_plates import TYPICAL_MAGNITUDE

            # THE GAUGE HANGS BELOW THE BODY, so this one tile draws a
            # SMALLER Moon and slides it up to make room — the mark is
            # the style, and a tile that clipped its own legend would
            # advertise nothing (the exact failure the band tile above
            # already records). The two numbers are measured against
            # `render.eclipse_danjon`'s own reach: the gauge stops at
            # 2.10 body radii below centre, so the drawn height is 3.10
            # radii and the body's centre must sit 0.55 radii above the
            # tile's middle for the whole mark to be centred.
            body = radius * _DANJON_TILE_BODY_SCALE
            painter.save()
            painter.translate(0.0, -body * _DANJON_TILE_LIFT)

            def paint_danjon_face(target: QPainter) -> None:
                target.setBrush(QColor(palette.SKIN_MOON_LIT))
                target.drawEllipse(QPointF(0.0, 0.0), body, body)

            moon_face.draw_moon_disc(
                painter, 1.0, body, "cut_rim", paint_danjon_face,
                palette.SKIN_MOON_DARK,
            )
            # A TOTAL demo for this one tile: the Danjon scale is defined
            # at mid-totality, so the partial demo every other lunar tile
            # uses would show the style's own "does not apply" picture.
            # The magnitude is the Encyclopedia plate's typical totality,
            # read from there rather than restated.
            eclipse_danjon.draw_danjon_scale(
                painter, body, "lunar_total",
                TYPICAL_MAGNITUDE[("lunar", "total")],
            )
            painter.restore()
            return
        # `effective_style` is always one of the native painters here —
        # `resolve_eclipse_style` guarantees it — so this is a plain
        # dispatch, not a validity check.

        def paint_face(target: QPainter) -> None:
            target.setBrush(QColor(palette.SKIN_MOON_LIT))
            target.drawEllipse(QPointF(0.0, 0.0), radius, radius)

        moon_face.draw_moon_disc(
            painter, 1.0, radius, "cut_rim", paint_face, palette.SKIN_MOON_DARK,
        )
        if effective_style == "umbra_sweep":
            moon_face.draw_umbra_sweep(painter, radius, "lunar_partial", 0.6)
            return
        if effective_style == "blood_moon":
            moon_face.draw_blood_moon(painter, radius, "lunar_partial", 0.6)
            return
        disc = _full_disc_path(radius)
        brightness = glow.ECLIPSE_STATE_MOON_BRIGHTNESS["lunar_partial"]
        value = round(255 * brightness)
        painter.save()
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_Multiply
        )
        painter.fillPath(disc, tinted_gray(value, None))
        painter.restore()

    return _computed_icon(
        f"eclipse_lunar_style_{style}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


def _full_disc_path(radius: float) -> QPainterPath:
    path = QPainterPath()
    path.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
    return path


def moon_station_style_icon(style: str) -> QIcon:
    """THE MOON'S FOUR STATIONS picker's preview, at "youth" (the
    station `_arc_grammar` and the intensity ramp treat most distinctly
    from the other three) — THE REAL ALGORITHM at thumbnail scale.

    The mark has TWO halves and the tile draws both, in the dial's own
    order: `draw_station_mark` behind the body, then the disc, then
    `draw_station_inner_glow` on top. Youth is the station whose inner
    glow the owner specifically asked for, so a preview that drew only
    the background half would advertise the one thing this style does
    not appear to do. The moon disc is drawn at a WAXING quarter so
    there is a real dark half for the inner glow to sit in — a full
    disc would hide it exactly the way the dial's first cut did."""
    body_radius = THUMB_SOURCE_PX * 0.18

    def paint(painter: QPainter) -> None:
        marker_marks.draw_station_mark(
            painter, style, "youth", body_radius, palette.GLOW_MOON_COLOR,
            fraction=0.25,
        )
        moon_face.draw_moon_disc(
            painter, 0.25, body_radius, constants.MOON_DARK_STYLE_DEFAULT,
            _plain_moon_face(body_radius), palette.SKIN_MOON_DARK,
        )
        marker_marks.draw_station_inner_glow(
            painter, style, "youth", body_radius, palette.GLOW_MOON_COLOR,
            0.25,
        )

    return _computed_icon(
        f"moon_station_style_{style}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


def _plain_moon_face(radius: float):
    """A flat lit disc standing in for the moon plate — the `paint_face`
    callable `render.moon_face.draw_moon_disc` takes, so a preview runs
    the dial's own code without resolving any art."""
    def paint_face(target: QPainter) -> None:
        target.setPen(Qt.PenStyle.NoPen)
        target.setBrush(QColor(palette.SKIN_MOON_LIT))
        target.drawEllipse(QPointF(0.0, 0.0), radius, radius)

    return paint_face


def sun_station_style_icon(style: str) -> QIcon:
    """THE SUN'S FOUR STATIONS picker's preview, at "youth"/spring — the
    same station chosen for the Moon's twin, so the two galleries read
    as one grammar learned once. `day_fraction=0.6` gives the
    "day_night_wedge" style room to visibly differ from a 50/50 split."""
    body_radius = THUMB_SOURCE_PX * 0.18

    def paint(painter: QPainter) -> None:
        marker_marks.draw_sun_station_mark(
            painter, style, "youth", body_radius, palette.GLOW_SUN_COLOR, 0.6,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(palette.GLOW_SUN_COLOR))
        painter.drawEllipse(QPointF(0.0, 0.0), body_radius, body_radius)

    return _computed_icon(
        f"sun_station_style_{style}", paint,
        ground=palette.THUMB_NIGHT_GROUND,
    )


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


def _shade_ramp(metal: str, shade: str) -> list | None:
    """One metal SHADE's whole ramp — the stops the dial's own recolor
    uses (`recolor/presets/metals.json` through `defaults.METAL_SHADES`),
    sorted dark to light. None when the ramp is absent."""
    import json

    from config import defaults
    from recolor.recipe import PRESETS

    ramp_name = defaults.METAL_SHADES.get(metal, {}).get(shade)
    if ramp_name is None:
        return None
    try:
        data = json.loads(Path(PRESETS).read_text(encoding="utf-8"))
        entry = data["metals"][ramp_name]
    except (OSError, KeyError, ValueError):
        return None
    stops = sorted(entry.get("stops") or [], key=lambda stop: stop[0])
    if len(stops) < 2:
        return None
    return stops


def metal_roundel_icon(metal: str, shade: str) -> QIcon | None:
    """ONE METAL SHADE AS A ROUNDEL — a struck disc that catches the
    light, not a name in a dropdown (owner order 2026-08-15: "napravi
    ROUNDEL koji ce simulirati metalnu plocu sa odsjajem i prikazivati
    te opcije kako izgledaju").

    Everything drawn here is READ from the shade's own ramp, never
    hand-picked: the disc is a top-left-to-bottom-right linear sweep
    through the ramp's real stops, so a pale gold and a dark amber
    differ here exactly as much as they differ on the dial. The
    highlight arc uses the ramp's lightest stop and the rim its
    darkest, which is what gives a flat circle the read of a struck
    plate. None when the ramp is absent — an honest blank tile."""
    stops = _shade_ramp(metal, shade)
    if stops is None:
        return None
    radius = THUMB_SOURCE_PX * 0.44

    def paint(painter) -> None:
        # The plate: the ramp swept corner to corner, dark rim to lit
        # edge, exactly the direction a struck disc is lit from.
        sweep = QLinearGradient(-radius, -radius, radius, radius)
        for position, colour in stops:
            sweep.setColorAt(max(0.0, min(1.0, float(position))), QColor(colour))
        painter.setBrush(QBrush(sweep))
        painter.setPen(QPen(QColor(stops[0][1]), radius * 0.06))
        painter.drawEllipse(QPointF(0.0, 0.0), radius, radius)
        # The specular: a soft crescent of the ramp's lightest stop
        # riding the upper-left edge, the way light sits on metal.
        gloss = QRadialGradient(
            QPointF(-radius * 0.35, -radius * 0.4), radius * 1.1
        )
        highlight = QColor(stops[-1][1])
        highlight.setAlpha(150)
        gloss.setColorAt(0.0, highlight)
        faded = QColor(highlight)
        faded.setAlpha(0)
        gloss.setColorAt(0.75, faded)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gloss))
        painter.drawEllipse(QPointF(0.0, 0.0), radius, radius)

    return _computed_icon(f"metal_roundel_{metal}_{shade}", paint)


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
