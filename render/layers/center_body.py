"""The CENTRE BODY layer — the seat at the dial's middle."""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from config import constants, continents as continents_theme, dial, pantheon, paths
from core import continents
from render.context import Cadence, Layer, RenderContext
from render.ninths import active_thirteenth, center_face, ninth_alt_active, theme_ninth, thirteenth_plate
from render.painting import draw_name_label, draw_pixmap_centered, name_label_px
from render.skin_geometry import center_duality, hover_factor
from render.slot_layout import center_dual_face, weekday_body_size, weekday_classic_slot
from render.weekday_body import draw_weekday_body, weekday_label_set_px


class CenterBodyLayer(Layer):
    """The current day's CENTER image drawn ABOVE the hands — the opaque
    Sun on Sundays in ghost mode (hexa and trio pointers; cross/octa
    seat the Sun on an arm slot), or the day's body in center_only mode
    — so the hands sweep behind it (owner spec; the slot images never
    move up here). During the reveal-week window (owner 2026-07-16) the
    ghost center Sun also rises here, opaque, on every day of the week —
    that IS the z-order lift the reveal promises.

    **THE BLUE MOON LAW (owner-sealed 2026-07-22, CORRECTED 2026-07-2X)
    — checked FIRST, independent of everything below:** `active_
    thirteenth(skin, day)` names the 13th (if any) the Calendar
    pointer's OWN mode is showing today — gated to `skin.pointer ==
    "calendar"` alone, so it can NEVER fire on hexa/trio/center_only
    (R12's global law is retired; see [Blue Moon](../core/blue_moon.md)).
    The Calendar pointer never carries a classic weekday seat at all
    (its slot layout is always "pinned" — `render.slot_layout.slot_layout`),
    so its own dial center is otherwise EMPTY; a showing 13th draws
    there, at the same (0, 0) origin every other center face uses."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        thirteenth = active_thirteenth(ctx.skin, ctx.day)
        if thirteenth is not None:
            self._draw_thirteenth(painter, ctx, thirteenth)
            return
        if weekday_classic_slot(ctx.skin) is None:
            return          # every slot sits in a seat
        ghost_reveal = (
            ctx.reveal_active
            and spec.display_mode != "center_only"
            and center_duality(ctx.skin)
        )
        if spec.display_mode != "center_only" and not (
            center_duality(ctx.skin) and today == "sun"
        ) and not ghost_reveal:
            return
        # ONE body size (owner 2026-07-18, his screenshots): the hexa/
        # trio center matches the diamond bodies — normal state and
        # reveal alike (this path used to drop the seat factor, so the
        # double-click SHRANK the center). Only the center-only
        # showcase, with no diamond bodies to match, keeps its own
        # `center_scale`.
        center_size = (
            2 * ctx.radius * spec.center_scale
            if spec.display_mode == "center_only"
            else weekday_body_size(ctx.skin, ctx.radius)
        )
        hf = hover_factor(ctx, f"body:{today}")
        center_size *= hf
        body = "sun" if ghost_reveal else today
        names_on = (
            ctx.skin.show_weekday_names
            and ctx.skin.weekday_theme != "planet_signs"
        )
        # SET-UNIFORM label size (owner verdict 2026-07-18): the SAME
        # pure computation WeekdayLayer uses, agreeing on one size
        # across the two separate paint passes without shared state.
        label_px = weekday_label_set_px(ctx) * hf if names_on else None
        # THE DUAL/NINTH CENTER TIME WINDOWS (owner INSTRUCTION #5 +
        # solar amendment, round R3b item 3): on an ACTUAL Sunday
        # (never the ghost-reveal Sun, which always reads plain — the
        # reveal promises the ordinary "two persons, a union" read) the
        # SOLAR clock, not the wall clock, may swap the center's face
        # to EVIL (the Servant) or — where the theme names one — THE
        # UNFOUND (the Ninth). `center_dual_face` is the complementary
        # law to `sunday_dual_face` (Compass/Seasons keep their own
        # two-seat mechanic, untouched).
        if today == "sun" and not ghost_reveal and center_dual_face(self._skin):
            # THE DOUBLE NINTH's alt face (owner Double-Ninth verdicts,
            # 2026-07-29): `ninth_alt_active` dispatches by the theme's
            # OWN `constants.NINTH_MECHANISMS` entry — continents' sky
            # trigger, sw_dyad's daylight/night switch, or neither.
            ninth = theme_ninth(
                ctx.skin.weekday_theme, ninth_alt_active(ctx),
                on_date=ctx.day.local_date,
            )
            face = center_face(ctx.day, ctx.tick, ninth is not None)
            if face != "ruler":
                if face == "servant":
                    asset = spec.dual_asset
                    if ctx.skin.weekday_theme == "continents":
                        # The Arctic Servant follows earth_style + live
                        # sky like the Ruler and the six arms.
                        live = continents_theme.continents_dual_art(
                            ctx.skin.earth_style, ctx.tick.is_daylight
                        )
                        if paths.art_file(live).exists():
                            asset = live
                    # THE UNIVERSAL ROTATION CONVENTION (weekday ALT
                    # ROTATION round 2026-07-20/21).
                    asset = (
                        pantheon.rotating_art_file(asset, ctx.day.local_date)
                        or asset
                    )
                    name = (
                        spec.dual_names
                        or pantheon.WEEKDAY_DUAL_NAMES[ctx.skin.weekday_theme]
                    )[1]
                else:
                    name, asset = ninth
                painter.save()
                painter.setOpacity(1.0)
                draw_pixmap_centered(
                    painter, ctx, asset, QPointF(0, 0), center_size,
                    metal=spec.metal,
                )
                if names_on:
                    draw_name_label(
                        painter, name, QPointF(0, 0),
                        name_label_px(
                            name, center_size * dial.NAME_LABEL_WIDTH_FRACTION
                        ),
                    )
                painter.restore()
                return
        draw_weekday_body(
            painter, ctx, body, QPointF(0, 0), center_size, 1.0, label_px
        )

    def _draw_thirteenth(
        self, painter: QPainter, ctx: RenderContext, key: str,
    ) -> None:
        """THE BLUE MOON LAW's 13th (owner-sealed 2026-07-22, CORRECTED
        2026-07-2X) — drawn at the dial's literal (0, 0) center, opaque,
        ABOVE the hands (`active_thirteenth` already gates this to
        `skin.pointer == "calendar"`, whose own center is otherwise
        empty — see the class docstring). Its own hover element is
        "thirteenth" (`render.compositor._element_at`), never a
        `center_seat_body_key` piggyback (that key names a DIFFERENT
        seat — the classic weekday unit's — which the Calendar pointer
        never carries). Graceful-absent like the calendar mount's own
        months (a NAME-ONLY fallback, never a hidden feature) — UNLIKE
        `theme_ninth`, whose missing plate makes a theme act as if it
        carried no Ninth at all: the 13th's whole point is its
        trigger+window, which must read provably even before Sol/
        Modrenik's art lands."""
        spec = self._skin.weekday_set
        name, asset = thirteenth_plate(key)
        center_size = (
            2 * ctx.radius * spec.center_scale
            if spec.display_mode == "center_only"
            else weekday_body_size(ctx.skin, ctx.radius)
        )
        center_size *= hover_factor(ctx, "thirteenth")
        painter.save()
        painter.setOpacity(1.0)
        if asset is not None:
            draw_pixmap_centered(painter, ctx, asset, QPointF(0, 0), center_size)
        if asset is None or ctx.skin.show_weekday_names:
            draw_name_label(
                painter, name, QPointF(0, 0),
                name_label_px(
                    name, center_size * dial.NAME_LABEL_WIDTH_FRACTION
                ),
            )
        painter.restore()
