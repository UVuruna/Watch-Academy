"""Drawing ONE weekday body with its name label.

Shared by the weekday ring, the slots and the centre seat: the label
text for a body, the single label size the whole set shares, and the
body+label draw call itself.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter

from config import constants, continents as continents_theme, dial, pantheon, paths
from core import continents
from render.context import RenderContext
from render.painting import draw_name_label, draw_pixmap_centered, name_label_px
from render.skin_geometry import center_duality, servant_seat_angle, visible_occupant, weekday_slots
from render.slot_layout import servant_holds_the_seat, weekday_body_size

def weekday_label_text(ctx: RenderContext, body: str) -> str:
    """The displayed weekday text for `body`: short until the largest
    preset, full from `WEEKDAY_FULL_NAME_MIN_DIAMETER`."""
    full_text = 2 * ctx.radius >= dial.WEEKDAY_FULL_NAME_MIN_DIAMETER
    return (
        constants.WEEKDAY_FULL_NAMES[body] if full_text
        else constants.WEEKDAY_LABELS[body]
    )


def weekday_label_set_px(ctx: RenderContext) -> int:
    """The SET-UNIFORM label size (owner verdict 2026-07-18, ROADMAP
    15h) for the weekday bodies of THIS dial: every name sharing the
    ring — the diamond slot occupants, and the hexa/trio center Sun
    whichever of WeekdayLayer/CenterBodyLayer draws it this frame —
    wears the size of the SMALLEST fitted member, computed once here
    (a pure, cheap text-measurement pass) rather than per label. Two
    separate paint passes (WeekdayLayer is DAILY, CenterBodyLayer is
    MINUTE) call this same pure function and agree on one size without
    sharing mutable state."""
    spec = ctx.skin.weekday_set
    today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
    if spec.display_mode == "center_only":
        # A set of one — its own fit is the whole answer.
        text = weekday_label_text(ctx, today)
        width = (
            2 * ctx.radius * spec.center_scale
            * dial.NAME_LABEL_WIDTH_FRACTION
        )
        return name_label_px(text, width)
    slot_size = weekday_body_size(ctx.skin, ctx.radius)
    target_width = slot_size * dial.NAME_LABEL_WIDTH_FRACTION
    servant = servant_holds_the_seat(ctx.skin, today)
    bodies = set()
    for slot_angle, occupants in weekday_slots(ctx.skin):
        if servant and slot_angle == servant_seat_angle(ctx.skin):
            continue
        bodies.add(visible_occupant(occupants, today))
    if center_duality(ctx.skin):
        bodies.add("sun")     # the ghost/opaque center Sun joins the set
    texts = {weekday_label_text(ctx, body) for body in bodies}
    return min(name_label_px(text, target_width) for text in texts)


def draw_body_label(
    painter: QPainter, ctx: RenderContext, body: str,
    pos: QPointF, size: float, label_px: float | None = None,
) -> None:
    """The weekday-name label on a body — shared by the weekday unit
    and the info slot's second body (Rule #5). `label_px` is the SET-
    UNIFORM size (owner verdict 2026-07-18) the caller computed once
    per paint via `weekday_label_set_px`, already hover-scaled; when
    omitted (a standalone single-body caller — the info slot's own
    seated body is a set of one) this body's own fit is used."""
    label = weekday_label_text(ctx, body)
    px = (
        label_px if label_px is not None
        else name_label_px(label, size * dial.NAME_LABEL_WIDTH_FRACTION)
    )
    draw_name_label(painter, label, pos, px)


def draw_weekday_body(
    painter: QPainter,
    ctx: RenderContext,
    body: str,
    pos: QPointF,
    size: float,
    opacity: float,
    label_px: float | None = None,
) -> None:
    """One weekday body with its white outlined label — shared by the
    diamond slots and the above-the-hands center pass (Rule #5). The
    label is the weekday name (owner spec): short until the largest
    preset, full from WEEKDAY_FULL_NAME_MIN_DIAMETER. `label_px`
    threads the SET-UNIFORM size through to `draw_body_label` (owner
    verdict 2026-07-18)."""
    spec = ctx.skin.weekday_set
    painter.save()
    painter.setOpacity(opacity)
    # The planet-SIGN glyphs wear NO text at all (owner correction
    # 2026-07-12 — supersedes the earlier stacked-above rule).
    names_on = (
        ctx.skin.show_weekday_names
        and ctx.skin.weekday_theme != "planet_signs"
    )
    asset = spec.bodies.get(body)
    if ctx.skin.weekday_theme == "continents" and body in continents_theme.CONTINENTS_REGIONS:
        # THE CONTINENTS live art (owner-sealed matrix 2026-07-21): the
        # baked skin body is only the atmo-day still frame — on the dial
        # the continent follows the user's earth_style (one setting, whole
        # instrument) and the SKY'S OWN day/night (`ctx.tick.is_daylight`,
        # the same sun-elevation law the Earth marker already computes,
        # never recomputed here). Graceful-absent if the face is missing.
        live = continents_theme.continents_body_art(
            body, ctx.skin.earth_style, ctx.tick.is_daylight
        )
        if paths.art_file(live).exists():
            asset = live
    if asset is not None:
        # THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20,
        # weekday ALT ROTATION round 2026-07-20/21): whichever canonical
        # file `spec.bodies`/the continents live override landed above
        # rotates daily among its OWN `_v2`/`alt/` siblings if it has
        # any — a no-op for every body that has none (the vast
        # majority today).
        asset = pantheon.rotating_art_file(asset, ctx.day.local_date) or asset
    if asset is not None:
        # The theme's metal (owner 2026-07-12): the hue-selective swap
        # turns only the bronze details gold/silver; None = as drawn.
        draw_pixmap_centered(
            painter, ctx, asset, pos, size, metal=spec.metal,
        )
    else:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(spec.body_colors[body]))
        painter.drawEllipse(pos, size / 2, size / 2)
    if names_on:
        draw_body_label(painter, ctx, body, pos, size, label_px)
    painter.restore()
