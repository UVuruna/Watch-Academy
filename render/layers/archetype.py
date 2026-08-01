"""The ARCHETYPE layers — the arm figures and the centre figure."""

import math

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from config import archetypes, pantheon
from render.archetype_geometry import archetype_art_ready, archetype_center_lit, archetype_figure_size, archetype_label_set_px, draw_archetype_figure
from render.context import Cadence, Layer, RenderContext
from render.painting import dial_point, draw_name_label, draw_pixmap_centered
from render.skin_geometry import archetype_key, arm_half_deg, hover_factor
from render.slot_layout import weekday_body_orbit


class ArchetypeLayer(Layer):
    """THE ARCHETYPE MODE's arm figures (owner sealed package
    2026-07-16): each diamond carries its archetype's stained glass,
    scaled into the arm with the color visible around it, at the romb
    center — the same radius the weekday-by-colors unit rides. The
    figure whose HOUR-SPACE holds the hour hand (ctx.archetype_lit)
    draws FULL; the rest ghost at the weekday ghost opacity — an
    ARCHETYPE CLOCK, not a gallery. During the reveal window every
    figure is full (the "show me everything" gesture). With Names on
    the LIT figure carries its display name (all of them during the
    reveal); missing/placeholder art always falls back to the name.
    DAILY cadence — the lit index keys the composite exactly like the
    Calendar's shichen wedge."""

    cadence = Cadence.DAILY
    # The lit figure, the reveal window and the hover-enlarge all change
    # the figures, so the compositor draws this layer LIVE, never in the
    # cached composite (owner 2026-07-17, ROADMAP 15f).
    hover_variable = True

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        key = archetype_key(ctx.skin)
        if key is None:
            return
        orbit = ctx.radius * weekday_body_orbit(ctx.skin)
        tip = ctx.radius * ctx.skin.star.radius_fraction
        half = arm_half_deg(ctx.skin)         # Cube look widens the arms
        arm_width = tip * math.tan(math.radians(half))   # diamond's widest
        # The archetype names switch is now its OWN Settings on/off
        # (owner 2026-07-18, ROADMAP 15h — replaces the buried menu twin
        # that shared `show_weekday_names`).
        names_on = ctx.skin.archetype_names
        # SET-UNIFORM label size (owner verdict 2026-07-18): computed
        # ONCE per paint for the whole layout (arms AND the center),
        # never per label — the hover-enlarged twin scales this base.
        label_px = archetype_label_set_px(ctx, key, arm_width)
        for index, fig in enumerate(archetypes.figures(key)):
            # Per-arm hover target (owner slika 8): the base pass skips
            # the hovered figure, the HoverLift twin redraws it enlarged
            # above — exactly like the slots.
            element = f"archetype:{index}"
            if not self._gate(ctx, element):
                continue
            lit = ctx.reveal_active or index == ctx.archetype_lit
            hf = hover_factor(ctx, element)
            # THE UNIVERSAL ROTATION CONVENTION (owner decree
            # 2026-07-20): a figure that opted in (currently the
            # Tetramorph alone) resolves its file fresh every paint —
            # ArchetypeLayer is hover_variable/painted LIVE already, so
            # a day change re-resolves with no extra invalidation.
            if fig.get("rotates"):
                resolved = pantheon.rotating_art_file(
                    fig["file"], ctx.day.local_date
                )
                if resolved is not None:
                    fig = {**fig, "file": resolved}
            # THE TWO-TYPE LAW (owner decree 2026-07-18, round two): each
            # figure's OWN art aspect decides CIRCLE (the slot size) vs
            # PORTRAIT (the per-pointer lancet fraction) — classified
            # per figure, not once for the whole layout.
            height = archetype_figure_size(ctx.skin, ctx.radius, fig["file"])
            draw_archetype_figure(
                painter, ctx, fig,
                dial_point(fig["angle"] + ctx.rotation, orbit),
                height * hf,
                1.0 if lit else ctx.skin.weekday_set.ghost_opacity,
                named=names_on and lit,
                label_px=label_px * hf,
            )


class ArchetypeCenterLayer(Layer):
    """The archetype's CENTER — the Eye / the Hearth / the Seal / the
    Union / the Throne (the Compass has none) — drawn where the
    weekday center body used to live: ABOVE the hands. Placeholder art
    falls back to the center's name; the hover-enlarge lift twin
    joins HoverLiftLayer under the "archetype:center" element. THE
    WINDOW (owner seal 2026-07-18): it burns FULL only while the hour
    hand stands within `ARCHETYPE_CENTER_WINDOW_DEG` of TRUE solar noon
    OR solar midnight (`archetype_center_lit`) — 4 of the 24 hours — and
    draws at the weekday `ghost_opacity` the rest of the day, exactly
    like an un-lit arm figure; the reveal window ("show me everything")
    still forces it full regardless."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        key = archetype_key(ctx.skin)
        if key is None:
            return
        center = archetypes.center(key)
        if center is None or not self._gate(ctx, "archetype:center"):
            return
        # THE TWO-TYPE LAW (owner decree 2026-07-18, round two): the
        # center follows its OWN art's type — `archetype_figure_size`
        # classifies it exactly like an arm figure (circle = the slot
        # size, portrait = the lancet fraction) — no longer the weekday
        # Sun's center_scale, and the reveal window can no longer resize
        # it (the helper has no reveal term).
        height = (
            archetype_figure_size(ctx.skin, ctx.radius, center["file"])
            * hover_factor(ctx, "archetype:center")
        )
        # THE WINDOW (owner seal 2026-07-18): full at solar noon/midnight
        # (±ARCHETYPE_CENTER_WINDOW_DEG), ghost otherwise — the reveal
        # gesture overrides regardless (short-circuits before touching
        # ctx.tick, which the compositor guarantees on this MINUTE layer).
        lit = ctx.reveal_active or archetype_center_lit(
            ctx.tick.hour_angle, ctx.day.star_rotation
        )
        opacity = 1.0 if lit else ctx.skin.weekday_set.ghost_opacity
        painter.save()
        painter.setOpacity(opacity)
        if archetype_art_ready(center["file"]):
            draw_pixmap_centered(
                painter, ctx, center["file"], QPointF(0, 0), height
            )
        else:
            # SET-UNIFORM label size (owner verdict 2026-07-18): the
            # SAME pure computation ArchetypeLayer uses (the center
            # shares the arms' set), agreeing on one size across the
            # two separate paint passes without shared state.
            tip = ctx.radius * ctx.skin.star.radius_fraction
            half = arm_half_deg(ctx.skin)
            arm_width = tip * math.tan(math.radians(half))
            label_px = (
                archetype_label_set_px(ctx, key, arm_width)
                * hover_factor(ctx, "archetype:center")
            )
            draw_name_label(painter, center["name"], QPointF(0, 0), label_px)
        painter.restore()
