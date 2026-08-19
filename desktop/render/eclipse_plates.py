"""THE ECLIPSE PLATES — one drawn picture per (kind, type, style), for
the Encyclopedia's own look slider.

Owner order 2026-08-12: "enciklopedija treba da objasni sva stanja i
prikaze, sve slike kako ih prikazujemo, na slajder — isti slajder koji
menja bronze, gold, colored, silver".
lang-ok: the owner's own sentence, quoted so the requirement cannot be
re-derived wrongly.

So the reader's existing look switcher (`app.encyclopedia.reader`, the
arrows that page Colored / Bronze / Gold / Silver) pages the DISPLAY
STYLES of an eclipse instead, on the eclipse chapters: a total lunar
eclipse shows the umbra sweep, then the band's copper segment, then the
halo darkening — the same three pictures the dial itself can draw.

THE PICTURES ARE THE DIAL'S OWN (Rule #5). Nothing here re-implements an
eclipse: the glow comes from `render.eclipse_glow`, the solar overlays
from `render.marker_marks.draw_solar_eclipse`, the lunar face and its
umbra from `render.moon_face`. If a style changes on the dial, these
plates change with it — a hand-drawn illustration would have started
lying the first time the owner corrected a style, which is exactly how
the twelve unwired figure casts happened (THE THEME COMPLETION LAW).

Layer: render. Documentation: __about/eclipse_plates.md.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap

from config import defaults, glow, palette, paths, umbra
from render import marker_marks, moon_face, raster_store
from render.eclipse_glow import (
    draw_event_glow,
    eclipse_state_glow_strength,
)

# The plate is a square night field with the body centred in it — the
# body at this fraction of the plate, the rest breathing room so the
# halo (1.5x the body, `glow.GLOW_RADIUS_SCALE`) and the solar rays are
# never clipped at the edge.
PLATE_SIZE_PX = 512
# Bumped whenever a PAINTER these plates draw through changes, so a
# stale pre-bump cache file on disk is never mistaken for the new
# recipe's output — the same convention, and the same reason, as
# `app.watch_face.thumbs._THUMB_CACHE_VERSION`. Without it the round
# that painted the ballot's six new styles (2026-08-13) would have
# shipped the FALLBACK pictures to every Encyclopedia reader who had
# already opened an eclipse chapter once.
_PLATE_CACHE_VERSION = 2
_BODY_FRACTION = 0.30
_GROUND_RADIUS_FRACTION = 0.49

# The catalog types each kind distinguishes, in the Encyclopedia's own
# chapter order (`app.encyclopedia.pages._ECLIPSE_*_ENTRIES`) — one
# roster, so a plate can never exist for a chapter that does not, or the
# other way round.
TYPES = {
    "solar": ("total", "annular", "partial", "hybrid"),
    "lunar": ("total", "partial", "penumbral"),
}
STYLES = {
    "solar": umbra.ECLIPSE_SOLAR_STYLES,
    "lunar": umbra.ECLIPSE_LUNAR_STYLES,
}
# A TYPICAL catalog magnitude per type — the plate has no real event to
# read, and the geometry styles ("bite", "umbra_sweep", "magnitude_arc")
# are pictures OF a magnitude, so a plate without one would show the
# same picture for every type. These are the values the reference tables
# give for an average eclipse of each kind, stated here rather than
# hidden in the painter (a documented approximation, exactly like
# `umbra.ECLIPSE_BAND_DURATION_H`).
TYPICAL_MAGNITUDE = {
    ("solar", "total"): 1.05,
    ("solar", "annular"): 0.94,
    ("solar", "partial"): 0.62,
    ("solar", "hybrid"): 1.00,
    ("lunar", "total"): 1.30,
    ("lunar", "partial"): 0.66,
    ("lunar", "penumbral"): 0.95,
}


def style_label(style: str) -> str:
    """The slider's caption for one style — the style's own id, read as
    words. Deliberately NOT a prettier invented name: the same word is
    what the Watch Face picker shows and what the docs argue about, and
    two names for one style is how a reader ends up unable to find the
    setting a page is describing."""
    return style.replace("_", " ").capitalize()


def plate_file(kind: str, type_: str, style: str) -> Path:
    """The drawn plate for one (kind, type, style), disk-cached under a
    COMPUTED name — there is no source file to fingerprint, the same
    convention `render.asset_variants.calendar_sheet_icon_file` uses, so
    `raster_store.collect_garbage` leaves it alone (its carve-out for
    names whose first field is not a 16-hex stamp).

    Painted once per install and then reused. A failed save RAISES: an
    Encyclopedia page silently missing the picture it is explaining is
    the failure this whole module exists to prevent."""
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"eclipse_plate_{kind}_{type_}_{style}_{PLATE_SIZE_PX}"
        f"_v{_PLATE_CACHE_VERSION}.png"
    )
    if cache.exists():
        return cache
    image = _draw_plate(kind, type_, style)
    try:
        raster_store.atomic_save(image, cache)
    except OSError as error:
        print(f"eclipse plate cache write failed: {error}", file=sys.stderr)
        raise
    return cache


def looks_for(kind: str, type_: str) -> tuple:
    """The Encyclopedia `looks` tuple for one chapter: one look per
    display style, in the order the Watch Face picker lists them, each a
    single-image row. Shaped exactly like `_metal_looks`' Colored /
    Bronze / Gold / Silver, because it feeds the SAME reader control."""
    return tuple(
        (style_label(style), ((plate_file(kind, type_, style),),))
        for style in STYLES[kind]
    )


def _draw_plate(kind: str, type_: str, style: str) -> QImage:
    size = PLATE_SIZE_PX
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    centre = QPointF(size / 2.0, size / 2.0)
    # A NIGHT FIELD under the body: the dial's own ground. Without it a
    # bronze halo on the reader's pale page would be invisible, and the
    # page would claim to show a picture that cannot be seen.
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(palette.NIGHT_WEDGE_GROUND))
    ground = size * _GROUND_RADIUS_FRACTION
    painter.drawEllipse(centre, ground, ground)
    radius = size * _BODY_FRACTION / 2.0
    state = glow.ECLIPSE_TYPE_STATE[(kind, type_)]
    magnitude = TYPICAL_MAGNITUDE[(kind, type_)]
    if kind == "solar":
        _draw_solar(painter, centre, radius, state, magnitude, style)
    else:
        _draw_lunar(painter, centre, radius, state, magnitude, style)
    painter.end()
    return image


def _draw_solar(
    painter: QPainter, centre: QPointF, radius: float, state: str,
    magnitude: float, style: str,
) -> None:
    color = (
        palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
        if state == "solar_annular"
        else palette.GLOW_ECLIPSE_SOLAR_COLOR
    )
    draw_event_glow(
        painter, centre, radius, color,
        eclipse_state_glow_strength(state, magnitude),
    )
    art = QPixmap(str(defaults.ECLIPSE_SOLAR_ART))
    if not art.isNull():
        scaled = art.scaled(
            round(2 * radius), round(2 * radius),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawPixmap(
            QPointF(
                centre.x() - scaled.width() / 2.0,
                centre.y() - scaled.height() / 2.0,
            ),
            scaled,
        )
    marker_marks.draw_solar_eclipse(
        painter, style, radius, state, magnitude,
        palette.GLOW_SUN_COLOR, origin=centre,
    )


def _draw_lunar(
    painter: QPainter, centre: QPointF, radius: float, state: str,
    magnitude: float, style: str,
) -> None:
    # THE DOOR: every lunar style is resolved through
    # `render.eclipse_style.resolve_eclipse_style` exactly like every
    # other lunar call site, band presumed up (this plate always draws
    # its own band segment for the styles that need one, so it is never
    # the reason a style falls back here). Since the lunar painters
    # round of 2026-08-13 all six styles answer with themselves; the
    # call stays because the BAND context still decides for two of them
    # everywhere else.
    from render.eclipse_style import resolve_eclipse_style

    style, _fallback_reason = resolve_eclipse_style(
        "lunar", style, band_available=True,
    )
    draw_event_glow(
        painter, centre, radius, palette.GLOW_ECLIPSE_LUNAR_COLOR,
        eclipse_state_glow_strength(state, magnitude),
        fringe_color=(
            palette.ECLIPSE_LUNAR_FRINGE_COLOR
            if glow.ECLIPSE_STATE_FRINGE[state] else None
        ),
    )
    painter.save()
    painter.translate(centre)
    painter.setPen(Qt.PenStyle.NoPen)

    def paint_face(target: QPainter) -> None:
        target.setBrush(QColor(palette.MOON_SILVER))
        target.drawEllipse(QPointF(0, 0), radius, radius)

    # A FULL disc: a lunar eclipse only ever happens at full moon, so
    # 0.5 is not a chosen illustration but the phase the event requires.
    moon_face.draw_moon_disc(
        painter, 0.5, radius, umbra.MOON_DARK_STYLE_DEFAULT,
        paint_face, palette.MOON_SILVER,
    )
    if style == "umbra_sweep":
        moon_face.draw_umbra_sweep(painter, radius, state, magnitude)
    elif style == "blood_moon":
        # The depth ramp — copper at the deepest point, grey at the
        # umbra's rim, and grey ONLY in the penumbra (owner ballot
        # 2026-08-13). The opposite ramp to "umbra_sweep" above, which
        # is why the two are two pictures and not one recoloured.
        moon_face.draw_blood_moon(painter, radius, state, magnitude)
    elif style == "danjon_scale":
        from render import eclipse_danjon

        # The disc multiply AND the five-cell legend beneath it. The L
        # it marks is INDICATIVE, derived from the umbral magnitude —
        # no catalog carries an observed one (see
        # `render/__about/eclipse_danjon.md`).
        eclipse_danjon.draw_danjon_scale(painter, radius, state, magnitude)
    elif style == "halo":
        # The uniform multiply — the same brightness ladder the dial
        # applies, read off the one table (0.07 / 0.18 / 0.60).
        brightness = glow.ECLIPSE_STATE_MOON_BRIGHTNESS[state]
        value = round(255 * brightness)
        tint = (
            palette.ECLIPSE_TOTAL_MOON_TINT
            if state == "lunar_total" else None
        )
        painter.save()
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_Multiply
        )
        from render.painting import tinted_gray
        painter.fillPath(_disc_path(radius), tinted_gray(value, tint))
        painter.restore()
    painter.restore()
    if style in ("horizon_shadow", "contact_marks"):
        # THE BAND's own picture: these styles leave the disc alone and
        # write the event where DURATION can be seen (owner placement
        # 2026-08-10), so the plate shows the band arc with its copper
        # segment rather than a second, contradicting disc treatment.
        # `contact_marks` is that same segment plus the four contact
        # lines — an ADDITION, never a replacement.
        _draw_band_segment(painter, centre, radius, state, style)


def _disc_path(radius: float):
    from PySide6.QtGui import QPainterPath

    path = QPainterPath()
    path.addEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
    return path


def _draw_band_segment(
    painter: QPainter, centre: QPointF, radius: float, state: str,
    style: str,
) -> None:
    from render.layers.moon_band import MoonBandLayer

    band = radius * 2.6
    painter.save()
    painter.translate(centre)
    # The layer's own drawing, called directly — one segment, one home
    # (Rule #5). The angle is the plate's illustration choice, not a
    # claim about any real eclipse: it stands where an evening event
    # would, so the arc reads as a span of hours.
    layer = MoonBandLayer.__new__(MoonBandLayer)
    layer.draw_eclipse_segment(painter, band, 60.0, state)
    if style == "contact_marks":
        layer.draw_contact_marks(painter, band, 60.0, state)
    painter.restore()
