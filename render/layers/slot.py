"""The SLOT layer — the subdial complications."""

from datetime import date

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter

from config import constants, defaults, dial, pantheon, paths
from render.context import Cadence, Layer, RenderContext
from render.painting import dial_point, draw_pixmap_centered
from render.skin_geometry import hover_factor
from render.slot_layout import slot_layout, slot_seat_orbit, slot_seat_rotation, slot_seat_scale, slot_view
from render.subdial import display_year, draw_fitted_text, draw_slot_roundel, draw_small_seconds, draw_two_lines, octa_slot_art, slot_text
from render.weekday_body import draw_body_label, draw_weekday_body
from skins.manifest import SkinDefinition

class SlotLayer(Layer):
    """Every SEATED slot (owner matrix 2026-07-14): the 1st/2nd/3rd
    contents at their matrix positions — angles ride the star's
    rotation, "center" sits on the hub; the classic weekday unit
    belongs to WeekdayLayer. MINUTE cadence — the ascendant moves
    hourly and the small-seconds hand repaints on the per-second
    tick. Two instances share the class: the below-hands one draws
    the ANGLE seats, the above-hands one the CENTER seat (owner: the
    center occludes the hands); the hover-lift twin draws whatever is
    hovered."""

    cadence = Cadence.MINUTE

    def __init__(
        self, skin: SkinDefinition, centered: bool = False,
        lift: bool = False,
    ):
        super().__init__(skin, lift=lift)
        self._centered = centered

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.weekday_set
        for index, seat in slot_layout(ctx.skin).items():
            if seat == "classic":
                continue
            if not self._lift and (seat == "center") != self._centered:
                continue                 # the other instance draws it
            element = f"slot:{index}"
            if not self._gate(ctx, element):
                continue                 # hover z-lift repaints on top
            if seat == "center":
                pos = QPointF(0.0, 0.0)
            else:
                pos = dial_point(
                    seat + slot_seat_rotation(ctx.skin, ctx.rotation),
                    ctx.radius * spec.orbit_fraction
                    * slot_seat_orbit(ctx.skin, seat),
                )
            size = (
                2 * ctx.radius * spec.diamond_scale
                * slot_seat_scale(ctx.skin)
                * hover_factor(ctx, element)
            )
            self._draw_slot(painter, ctx, index, pos, size)

    def _draw_slot(
        self, painter: QPainter, ctx: RenderContext, index: int,
        pos: QPointF, size: float,
    ) -> None:
        mode, style, theme, metal, roster = slot_view(ctx.skin, index)
        inner = size * dial.SLOT_ROUNDEL_CONTENT_FRACTION
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        if mode == "seconds":
            # The SMALL-SECONDS complication (owner 2026-07-14).
            draw_slot_roundel(painter, ctx, pos, size)
            draw_small_seconds(painter, ctx, pos, size)
            return
        if mode == "date":
            # The full date in two rows (owner 2026-07-14); the year
            # row wears the era notation (Session 16 dual calendar).
            draw_slot_roundel(painter, ctx, pos, size)
            draw_two_lines(
                painter, ctx, pos, inner,
                slot_text("date", ctx), display_year(ctx),
            )
            return
        if mode in ("time", "day_length"):
            draw_slot_roundel(painter, ctx, pos, size)
            draw_fitted_text(painter, ctx, pos, inner, slot_text(mode, ctx))
            return
        if mode == "weekday":
            self._draw_weekday_slot(
                painter, ctx, index, pos, size, theme, metal, roster,
                today,
            )
            return
        if mode in ("zodiac", "ascendant"):
            sign = (
                ctx.tick.ascendant_sign
                if mode == "ascendant"
                else ctx.day.zodiac_name
            )
            if style in constants.ZODIAC_STYLE_ART_DIRS:
                asset = octa_slot_art(
                    constants.ZODIAC_STYLE_ART_DIRS[style], sign
                )
                if asset is not None:
                    if style == "colored":
                        draw_pixmap_centered(painter, ctx, asset, pos, size)
                    else:
                        # Flat glyph art rides the subdial (owner
                        # 2026-07-14); the colored badge stays bare.
                        draw_slot_roundel(painter, ctx, pos, size)
                        draw_pixmap_centered(
                            painter, ctx, asset, pos, inner
                        )
                    return
            # TEXT style, and the documented fallback until the art
            # lands — the Ascendant speaks the FULL word (owner
            # 2026-07-13, never the "Asc" shorthand).
            draw_slot_roundel(painter, ctx, pos, size)
            if mode == "ascendant":
                draw_two_lines(painter, ctx, pos, inner, "Ascendant", sign)
            else:
                draw_fitted_text(painter, ctx, pos, inner, sign)
            return
        # Chinese zodiac: the plates stay bare, text and the fallback
        # ride the subdial as element-over-animal (owner 2026-07-12).
        animal = ctx.day.chinese_name.split()[-1]
        if style in constants.CHINESE_STYLE_ART_DIRS:
            asset = octa_slot_art(
                constants.CHINESE_STYLE_ART_DIRS[style], animal
            )
            if asset is not None:
                draw_pixmap_centered(
                    painter, ctx, asset, pos, size,
                    metal=(
                        style if style in defaults.METAL_SWAP_TARGETS
                        else None
                    ),
                )
                return
        draw_slot_roundel(painter, ctx, pos, size)
        draw_two_lines(
            painter, ctx, pos, inner, ctx.day.chinese_name.split()[0], animal
        )

    def _draw_weekday_slot(
        self, painter: QPainter, ctx: RenderContext, index: int,
        pos: QPointF, size: float, theme: str, metal: str | None,
        roster: str, today: str,
    ) -> None:
        """Today's body in a SEAT, in that slot's own theme AND roster
        (owner 2026-07-12: e.g. Norse left, Greek right, both showing
        today; owner 2026-07-15: the roster is the slot's own too)."""
        if index == 1:
            # The 1st slot's unit is already themed on the skin.
            draw_weekday_body(painter, ctx, today, pos, size, 1.0)
            return
        seat = (
            pantheon.pantheon_seat(theme, today)
            if roster == "pantheon" else None
        )
        if seat is not None:
            # The PANTHEON figure on this seat (owner 2026-07-15) —
            # the shared safety law: no plate on disk means the
            # planetary bundle below stays whole.
            asset = seat[0]
        else:
            # THE ONE weekday-body resolver (Rule #5 — this used to
            # re-type the theme_dir/colored-folder/planets-branch
            # expression inline; now shared with `app.controller` and
            # `render.compositor`'s hover legend). colored is the
            # variant SIBLING (owner restructure 2026-07-14:
            # <family>/colored).
            asset = pantheon.weekday_theme_body_art(
                theme, today,
                colored=(metal == "colored" and theme in constants.METAL_THEMES),
            )
        # THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20,
        # weekday ALT ROTATION round 2026-07-20/21): resolved fresh
        # every paint already (this slot is never baked at settings
        # time), so the day's own `_v2`/`alt/` pick applies directly —
        # a no-op for every body/seat with no siblings.
        asset = pantheon.rotating_art_file(asset, ctx.day.local_date) or asset
        if paths.art_file(asset).exists():
            draw_pixmap_centered(
                painter, ctx, asset, pos, size,
                metal=(
                    metal
                    if theme in constants.METAL_THEMES
                    and metal in defaults.METAL_SWAP_TARGETS
                    else None
                ),
            )
            if ctx.skin.show_info_slot_names and theme != "planet_signs":
                draw_body_label(painter, ctx, today, pos, size)
            return
        # Documented fallback until the theme art lands.
        draw_slot_roundel(painter, ctx, pos, size)
        draw_fitted_text(
            painter, ctx, pos,
            size * dial.SLOT_ROUNDEL_CONTENT_FRACTION,
            constants.WEEKDAY_LABELS[today],
        )
