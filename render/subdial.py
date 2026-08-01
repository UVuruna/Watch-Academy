"""Subdial (complication) drawing — the small roundels and their text.

The slot plates, their drop shadow, the fitted one- and two-line text
and the small-seconds sub-dial. `octa_slot_art` resolves a slot art file
and is shared with the calendar mounts and the thirteenth plates.
"""

import math
from datetime import date
from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPen, QRadialGradient

from config import defaults, dial, palette, paths
from core.deep_time import format_official, real_year
from render.asset_variants import ring_face_color, subdial_plate_file
from render.context import RenderContext
from render.painting import draw_pixmap_centered, draw_shadowed_text


def octa_slot_art(folder: str, name: str) -> Path | None:
    """The PNG for an image slot style — `folder` is a subdirectory of
    assets/calendars/ (the RESTRUCTURE 2026-07-22 home; the old
    assets/zodiac/ root is abolished): "zodiac/astrology/primary/sign",
    ".../logo", ".../constellation", "zodiac/chinese/primary/bronze",
    "zodiac/chinese/primary/colored" — the family/variant tree. `name` is the
    entity ("Cancer" / "Horse") — or None while the owner's art folder
    does not have it yet."""
    path = paths.art_file(defaults.ZODIAC_ART_DIR / folder / f"{name}.png")
    return path if path.exists() else None


def slot_text(mode: str, ctx: RenderContext) -> str:
    """The INFO TEXT of a slot's time/date/day-length mode — shared by
    the info slot and the day slot's text modes (Rule #5)."""
    if mode == "time":
        return ctx.tick.time_hm
    if mode == "date":
        return f"{ctx.day.local_date.day} {ctx.day.local_date:%b}"
    return ctx.day.day_length            # "day_length" (validated set)


def display_year(ctx: RenderContext) -> str:
    """Today's year for the COMPACT dial texts (the date
    complication's year row, the Earth marker's deep-travel row): the
    OFFICIAL form only — the subdials cannot carry the full paired
    line; the Anno Lucis pairing lives in the hovers/legends
    (compositor, owner amendment 2026-07-17). The real astronomical
    year un-shifts the deep proxy frame first."""
    return format_official(
        real_year(ctx.day.local_date.year, ctx.day.deep_cycles),
        ctx.skin.era_notation,
        ctx.skin.show_era_suffix,
    )


def _draw_subdial_shadow(
    painter: QPainter, pos: QPointF, diameter: float
) -> None:
    """The subdial's LIVE shadow (owner 2026-07-15: the sun lives at
    the dial center, the shadow is rendered — never baked; reaffirmed
    under Rule #19, 2026-07-20 — this one function is WHY the
    twelve-plate seat/finish sheet was pure waste): offset OUTWARD
    from the center — the seat's own dial angle, south straight down,
    an arm seat toward its own outward corner — symmetric on the
    center seat (distance 0, no offset at all)."""
    distance = math.hypot(pos.x(), pos.y())
    if distance > 1.0:
        offset = diameter * dial.SUBDIAL_SHADOW_OFFSET_FRACTION
        shifted = QPointF(
            pos.x() + pos.x() / distance * offset,
            pos.y() + pos.y() / distance * offset,
        )
    else:
        shifted = pos
    radius = diameter / 2.0 * dial.SUBDIAL_SHADOW_SPREAD
    gradient = QRadialGradient(shifted, radius)
    shade = QColor(*palette.SUBDIAL_SHADOW_RGBA)
    gradient.setColorAt(0.75, shade)
    fade = QColor(shade)
    fade.setAlpha(0)
    gradient.setColorAt(1.0, fade)
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(gradient)
    painter.drawEllipse(shifted, radius, radius)
    painter.restore()


def draw_slot_roundel(
    painter: QPainter, ctx: RenderContext, pos: QPointF, diameter: float
) -> None:
    """The watch-face SUBDIAL behind flat slot content (owner
    2026-07-14) — worn by every text mode and by the flat astrology
    art (sign / logo / constellation); the circular plates
    (medallions, planets, colored badges) stay bare. THE MASTER (Rule
    #19, owner decree 2026-07-20) draws whenever it exists — a missing
    finish is RECOLORED from it live — under a LIVE outward shadow
    keyed off THIS seat's own dial position (owner 2026-07-15: one
    master plate, the code paints the metals and the light; the seat
    never reaches the FILE any more, only the shadow). The "theme"
    plate style (owner A/B spec) colorizes the tapisserie field to
    the clock tint; "black" keeps the standard dark field. With no
    art at all: the procedural circle, the ring's own face color
    rimmed in the finish metal."""
    _draw_subdial_shadow(painter, pos, diameter)
    plate = subdial_plate_file(
        ctx.skin.ring_finish,
        tint=(
            ctx.skin.ring_tint
            if ctx.skin.subdial_style == "theme"
            else None
        ),
    )
    if plate is not None:
        draw_pixmap_centered(painter, ctx, plate, pos, diameter)
        return
    rim = QColor(
        palette.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish]
    )
    width = max(1.5, diameter * dial.SLOT_ROUNDEL_BORDER_FRACTION)
    painter.save()
    painter.setPen(QPen(rim, width))
    painter.setBrush(ring_face_color(paths.art_file(ctx.skin.ring.asset)))
    inner = (diameter - width) / 2.0
    painter.drawEllipse(pos, inner, inner)
    painter.restore()


def _finish_color(ctx: RenderContext) -> QColor:
    """The letter-finish metal color — the ONE hue of every subdial
    accent: the mini hand, the theme-style ticks and all complication
    texts (owner 2026-07-15: 'u boji kao i kazaljka')."""
    return QColor(
        palette.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish]
    )


def draw_fitted_text(
    painter: QPainter, ctx: RenderContext, pos: QPointF,
    slot_size: float, text: str,
) -> None:
    """Fit-to-width slot text in the finish metal over a shadow: the
    largest bold font whose text spans the slot's width fraction —
    measured, not guessed, so it never overflows (Rule #5)."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(100)
    advance = QFontMetricsF(font).horizontalAdvance(text)
    target = slot_size * dial.TIME_TEXT_WIDTH_FRACTION
    font.setPixelSize(
        max(dial.BODY_LABEL_MIN_PX, math.floor(100.0 * target / advance))
    )
    draw_shadowed_text(painter, pos, text, font, _finish_color(ctx))


def draw_two_lines(
    painter: QPainter, ctx: RenderContext, pos: QPointF,
    slot_size: float, top: str, bottom: str,
) -> None:
    """Two stacked finish-metal lines sharing one fit-to-width font —
    the Chinese year ("Fire" / "Horse"), the Ascendant ("Ascendant" /
    "Virgo") and the two-row date ("14 Jul" / "2026") (Rule #5)."""
    font = QFont()
    font.setBold(True)
    font.setPixelSize(100)
    widest = max(
        QFontMetricsF(font).horizontalAdvance(line)
        for line in (top, bottom)
    )
    target = slot_size * dial.TIME_TEXT_WIDTH_FRACTION
    font.setPixelSize(
        max(dial.BODY_LABEL_MIN_PX, math.floor(100.0 * target / widest))
    )
    offset = font.pixelSize() * 0.62
    color = _finish_color(ctx)
    draw_shadowed_text(
        painter, QPointF(pos.x(), pos.y() - offset), top, font, color
    )
    draw_shadowed_text(
        painter, QPointF(pos.x(), pos.y() + offset), bottom, font, color
    )


def draw_small_seconds(
    painter: QPainter, ctx: RenderContext, pos: QPointF, diameter: float
) -> None:
    """The SMALL-SECONDS complication (owner 2026-07-14): the active
    set's own seconds hand rotating inside the subdial, behind eight
    tick marks just inside the rim — four LARGER at the cardinal
    points, four smaller between them. Colors (owner 2026-07-15 A/B
    spec): the hand ALWAYS wears the letter-finish metal over its own
    drop shadow; the ticks are white on the "black" plate style and
    finish-colored on the "theme" style — shadowed either way."""
    spec = ctx.skin.hands.second
    radius = diameter / 2.0
    outer = radius * dial.SMALL_SECONDS_TICK_OUTER_FRACTION
    tick_color = (
        _finish_color(ctx)
        if ctx.skin.subdial_style == "theme"
        else QColor(*palette.SMALL_SECONDS_TICK_RGBA)
    )
    painter.save()
    painter.translate(pos)
    for step in range(8):
        major = step % 2 == 0
        length = radius * (
            dial.SMALL_SECONDS_TICK_MAJOR_FRACTION
            if major
            else dial.SMALL_SECONDS_TICK_MINOR_FRACTION
        )
        width = max(1.0, radius * (0.07 if major else 0.05))
        angle = math.radians(step * 45.0)
        ux, uy = math.sin(angle), -math.cos(angle)
        start = QPointF(ux * (outer - length), uy * (outer - length))
        end = QPointF(ux * outer, uy * outer)
        shadow = QPointF(width * 0.35, width * 0.35)
        painter.setPen(QPen(
            QColor(*palette.SMALL_SECONDS_TICK_SHADOW_RGBA), width,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
        ))
        painter.drawLine(start + shadow, end + shadow)
        painter.setPen(QPen(
            tick_color, width,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
        ))
        painter.drawLine(start, end)
    if spec is not None:
        # The mini hand — the pack's own seconds hand, pivot math
        # identical to the big HandLayer, tip inside the tick ring —
        # in the FINISH metal (never the clock tint) over a drop
        # shadow (owner 2026-07-15).
        tip_units = spec.natural_height - spec.pivot_y
        target_tip = outer - radius * 0.06
        height = spec.natural_height * (target_tip / tip_units)
        pixmap = ctx.cache.pixmap_by_height(
            spec.asset, height, ctx.dpr,
            tint=palette.SLOT_ROUNDEL_BORDER_COLORS[ctx.skin.ring_finish],
            desaturate=ctx.skin.hands.desaturate,
        )
        silhouette = ctx.cache.pixmap_by_height(
            spec.asset, height, ctx.dpr, tint=palette.SHADOW_STAMP_TINT,
            desaturate=ctx.skin.hands.desaturate,
        )
        logical_w = pixmap.width() / ctx.dpr
        pivot_x = logical_w * (
            0.5 if spec.pivot_x_fraction is None else spec.pivot_x_fraction
        )
        offset = radius * dial.SMALL_SECONDS_HAND_SHADOW_OFFSET_FRACTION
        painter.rotate(ctx.tick.second_angle)
        painter.setOpacity(dial.SMALL_SECONDS_HAND_SHADOW_OPACITY)
        painter.drawPixmap(
            QPointF(-pivot_x + offset, -target_tip + offset), silhouette
        )
        painter.setOpacity(1.0)
        painter.drawPixmap(QPointF(-pivot_x, -target_tip), pixmap)
    painter.restore()
