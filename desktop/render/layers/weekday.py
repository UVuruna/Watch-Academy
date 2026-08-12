"""The WEEKDAY layer — the seven bodies around the dial."""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from config import constants, continents as continents_theme, pantheon, paths
from core import continents
from render.context import Cadence, Layer, RenderContext
from render.ninths import dual_seat_ninth, ninth_alt_active, theme_ninth
from render.painting import dial_point, draw_pixmap_centered
from render.skin_geometry import center_duality, hover_factor, servant_seat_angle, visible_occupant, weekday_slots
from render.slot_layout import servant_holds_the_seat, weekday_body_orbit, weekday_body_size, weekday_classic_slot
from render.weekday_body import draw_weekday_body, weekday_label_set_px


class WeekdayLayer(Layer):
    """Weekday bodies on the pointer's arm slots (rotating WITH the star,
    owner decision), BELOW the hands. The hexa and trio pointers keep
    the Sun in the center; cross/octa give every body a slot — shared
    slots show only the priority winner (see visible_occupant). Modes: "ghost" (all
    visible slots, non-current faint) and "center_only" (only the current
    day's body, in the center). Whenever the CENTER image is the current
    day it is drawn by CenterBodyLayer instead — ABOVE the hands (owner
    spec; slot images are unaffected)."""

    cadence = Cadence.DAILY
    # Hover-enlarge and the reveal window both change these bodies, so
    # the compositor draws the layer LIVE, never in the cached composite
    # (owner 2026-07-17, ROADMAP 15f) — a hover no longer rebuilds it.
    hover_variable = True

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]

        if weekday_classic_slot(ctx.skin) is None:
            return   # every slot sits in a SEAT (the slot layer draws)

        if spec.display_mode == "center_only":
            return                       # the center pass draws it above the hands

        # SET-UNIFORM label size (owner verdict 2026-07-18, ROADMAP 15h):
        # computed ONCE per paint for the whole weekday ring, never per
        # label — the hover-enlarged twin scales this same base size.
        names_on = (
            ctx.skin.show_weekday_names
            and ctx.skin.weekday_theme != "planet_signs"
        )
        base_label_px = weekday_label_set_px(ctx) if names_on else None

        if (
            center_duality(ctx.skin)
            and today != "sun"
            and not ctx.reveal_active
            and self._gate(ctx, "body:sun")
        ):
            # The center-duality wheels (hexa/trio, and the Quaternity's
            # Seasons wheel — owner seal 2026-07-29) center the Sun; on
            # Sundays — or during the reveal window (owner 2026-07-16) —
            # the CENTER pass draws it opaque ABOVE the hands instead.
            hf = hover_factor(ctx, "body:sun")
            center_size = weekday_body_size(ctx.skin, ctx.radius) * hf
            draw_weekday_body(
                painter, ctx, "sun", QPointF(0, 0), center_size,
                spec.ghost_opacity,
                base_label_px * hf if base_label_px is not None else None,
            )
        orbit = ctx.radius * weekday_body_orbit(ctx.skin)
        slot_size = weekday_body_size(ctx.skin, ctx.radius)
        servant = servant_holds_the_seat(ctx.skin, today)
        # THE TWO-BADGE NINTH WINDOWS (owner seal 2026-07-29 — the law
        # the center seat always had, extended to the two-seat Sundays):
        # near solar noon the Ninth borrows the SERVANT's seat (and
        # stands beside the Ruler), near solar midnight the RULER's
        # (beside the Servant). Existence-gated like every Ninth plate;
        # themes naming none keep both faces all Sunday.
        seat_taken, ninth_plate = None, None
        if servant and today == "sun" and not ctx.reveal_active:
            ninth_plate = theme_ninth(
                ctx.skin.weekday_theme, ninth_alt_active(ctx),
                on_date=ctx.day.local_date,
            )
            if ninth_plate is not None:
                seat_taken = dual_seat_ninth(ctx.day, ctx.tick)
        for slot_angle, occupants in weekday_slots(ctx.skin):
            if servant and slot_angle == servant_seat_angle(ctx.skin):
                continue     # the Servant won that seat today
            body = visible_occupant(occupants, today)
            if not self._gate(ctx, f"body:{body}"):
                continue
            theta = slot_angle + ctx.rotation
            hf = hover_factor(ctx, f"body:{body}")
            if seat_taken == "ruler" and body == "sun":
                # The midnight window: the Ninth's plate on the Ruler's
                # seat — image only, the label belongs to the faces.
                draw_pixmap_centered(
                    painter, ctx, ninth_plate[1], dial_point(theta, orbit),
                    slot_size * hf, metal=spec.metal,
                )
                continue
            draw_weekday_body(
                painter, ctx, body, dial_point(theta, orbit),
                slot_size * hf,
                1.0 if body == today or ctx.reveal_active else spec.ghost_opacity,
                base_label_px * hf if base_label_px is not None else None,
            )
        if servant and self._gate(ctx, "sun_servant"):
            # THE SERVANT FACE at 24h (owner 2026-07-13): it stands all
            # week like every other body — ghosted, OPAQUE on Sunday or
            # during the reveal window — two persons, a union; the
            # metal themes' swap recolors it exactly like the Ruler
            # plate. Image only — the Names label belongs to the Ruler
            # face.
            servant_asset = spec.dual_asset
            if ctx.skin.weekday_theme == "continents":
                # The Arctic Servant follows earth_style + live sky like
                # the six arms (owner-sealed matrix 2026-07-21).
                live = continents_theme.continents_dual_art(
                    ctx.skin.earth_style, ctx.tick.is_daylight
                )
                if paths.art_file(live).exists():
                    servant_asset = live
            # THE UNIVERSAL ROTATION CONVENTION (weekday ALT ROTATION
            # round 2026-07-20/21): the dual's own `_v2`/`alt/` siblings
            # (e.g. bible_dark's Judas) rotate daily like the Ruler face.
            servant_asset = (
                pantheon.rotating_art_file(servant_asset, ctx.day.local_date)
                or servant_asset
            )
            if seat_taken == "servant":
                # The noon window: the Ninth's plate on the Servant's
                # seat (owner seal 2026-07-29) — `theme_ninth` already
                # resolved rotation and the Pangea easter egg above.
                servant_asset = ninth_plate[1]
            painter.save()
            painter.setOpacity(
                1.0 if today == "sun" or ctx.reveal_active else spec.ghost_opacity
            )
            draw_pixmap_centered(
                painter, ctx, servant_asset,
                dial_point(
                    servant_seat_angle(ctx.skin) + ctx.rotation, orbit
                ),
                slot_size * hover_factor(ctx, "sun_servant"),
                metal=spec.metal,
            )
            painter.restore()
