"""The BACKGROUND layer — umbra, aura and the calendar wedge."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QConicalGradient, QPainter

from config import constants, dial, palette
from render.calendar_mount import _draw_calendar_mount, calendar_wedge_bounds, calendar_wheel
from render.context import Cadence, Layer, RenderContext
from render.daylight import aurora_bands, lit_regions, umbra_ladder
from render.painting import draw_pie, draw_pixmap_centered, pie_path, tinted_gray
from render.shapes import aura_wedge_bounds
from render.skin_geometry import aura_palette_for, daylight_active

class BackgroundLayer(Layer):
    """The UMBRA (gray brightness wheel) and the AURA (transparent hue
    wedges over the sunlit part of the day); both rotate with the star
    — or stand upright when solar rotation is off.

    THE DAYLIGHT SWITCH REACHES HERE (owner correction 2026-07-29): with
    `daylight_active(skin)` False — only ever the Calendar and the Rose
    — day and night vanish from the WHOLE dial, not just the star:

    ```
    IF the daylight law runs:
        Umbra = the brightness wheel, lightest on solar noon
        Aura  = the hues inside the lit arcs only, night stays gray
    ELSE:                                # flat noon everywhere
        Umbra = ONE full circle in the contrast span's LIGHTEST shade
        Aura  = full colour over the WHOLE circle at the day alpha
    ```

    The FIGURE faces (the Sunday Ruler/Servant, the Earth's day/night
    face, `center_face`) keep reading the real sun — the switch flattens
    the DISK COLOURING alone (owner seal)."""

    cadence = Cadence.DAILY

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.background
        umbra_radius = ctx.radius * spec.umbra_radius_fraction
        aura_radius = ctx.radius * spec.aura_radius_fraction
        painter.setPen(Qt.PenStyle.NoPen)

        # The Umbra rotates WITH the star (owner spec): the lightest
        # section centers on the star's top tip — true solar noon — and
        # the darkest on solar midnight. Its radius is tuned
        # independently of the Aura.
        painter.save()
        painter.rotate(ctx.rotation)
        if spec.base_asset is not None:
            draw_pixmap_centered(
                painter, ctx, spec.base_asset, QPointF(0, 0), 2 * umbra_radius
            )
        else:
            self._draw_umbra(painter, ctx, umbra_radius)
        painter.restore()

        # AURORA (owner spec 2026-07-12): no geometric pointer — the
        # day hues spread evenly across the actual sunrise-sunset arc,
        # dawn blue on the left, dusk brown on the right, so every hue
        # stays visible on the shortest and the longest day alike.
        if ctx.skin.colorful and ctx.skin.pointer == "aurora":
            bands, solar_frame = aurora_bands(
                ctx.day.sun, aura_palette_for(ctx.skin), spec.day_alpha,
            )
            for start, end, hue, alpha in bands:
                painter.save()
                if solar_frame:
                    painter.rotate(ctx.rotation)
                painter.setOpacity(alpha)
                painter.setBrush(QColor(hue))
                draw_pie(painter, aura_radius, start, end)
                painter.restore()
            return

        # CALENDAR (owner 2026-07-16, CANON §The Dozen): TWELVE 2-hour
        # wedges — the Aura carries the wedge colors, no star arms (like
        # Aurora). Calendar-FIXED: the wedges never ride the solar
        # rotation (owner spec), so they paint at rotation 0 — otherwise
        # they are the SAME Aura every other pointer draws (owner
        # correction 2026-07-29: the Calendar's own always-full-circle
        # fixed-alpha path is GONE, it follows the day/night law like
        # everyone else). The lit-wedge feature — the shichen under the
        # hour hand, the month/sign under the Earth — died with the
        # earlier decree.
        if ctx.skin.pointer == "calendar":
            self._paint_aura(
                painter, ctx, aura_radius, aura_palette_for(ctx.skin),
                calendar_wedge_bounds(calendar_wheel(ctx.skin)), 0.0,
            )
            if ctx.skin.calendar_mount != "off":
                _draw_calendar_mount(painter, ctx, ctx.skin.calendar_mount)
            return

        # Colorful off (Elements switch): the day/twilight arcs are still
        # indicated, but in plain white — a one-entry palette draws a
        # single full wedge under the same clip and alphas.
        aura_hues = (
            aura_palette_for(ctx.skin)
            if ctx.skin.colorful
            else (palette.COLORFUL_OFF_COLOR,)


        )
        # THE BACKGROUND FOLLOWS THE STAR (`aura_wedge_bounds` — the
        # owner's fix 2026-07-29): each hue's wedge is anchored on its
        # own LEAD RAY, wheel offset included, so a wedge can never
        # stand half behind one hue's rays and half behind the next.
        self._paint_aura(
            painter, ctx, aura_radius, aura_hues,
            aura_wedge_bounds(ctx.skin, aura_hues), ctx.rotation,
        )

    def _paint_aura(
        self, painter: QPainter, ctx: RenderContext, radius: float,
        hues: tuple, wedges: list[tuple[float, float]], rotation: float,
    ) -> None:
        """The colored wedges — ONE law for every pointer that has them
        (Rule #5): the Calendar's twelve calendar-FIXED wedges pass
        rotation 0, every star pointer passes the solar rotation.

        ```
        IF the daylight law runs (daylight_active):
            FOR EACH (start, end, alpha) lit arc of the day:
                clip to the arc, then draw every wedge at that alpha
        ELSE:                                  # the switch is off
            draw every wedge over the WHOLE circle at the day alpha
        ```
        """
        spec = self._skin.background
        if not daylight_active(ctx.skin):
            painter.save()
            painter.setOpacity(spec.day_alpha)
            painter.rotate(rotation)
            for color, (wedge_start, wedge_end) in zip(hues, wedges):
                painter.setBrush(QColor(color))
                draw_pie(painter, radius, wedge_start, wedge_end)
            painter.restore()
            return
        for start, end, alpha in lit_regions(ctx.day.sun, spec):
            painter.save()
            painter.setClipPath(pie_path(radius, start, end))
            painter.setOpacity(alpha)
            painter.rotate(rotation)
            for color, (wedge_start, wedge_end) in zip(hues, wedges):
                painter.setBrush(QColor(color))
                draw_pie(painter, radius, wedge_start, wedge_end)
            painter.restore()

    def _draw_umbra(
        self, painter: QPainter, ctx: RenderContext, radius: float
    ) -> None:
        """The brightness wheel, drawn in the already-rotated frame:
        lightest at the top (true solar noon), darkest at the bottom
        (true midnight), mirrored left/right. Forms (owner spec): fine
        30 / coarse 24 sections — single lightest/darkest sections
        centered on top/bottom, the rest in mirror pairs — or the
        continuous per-pixel gradient.

        With the daylight switch OFF (the Calendar and the Rose only,
        owner correction 2026-07-29) there is no night to shade: the
        whole disc stands at FLAT NOON — one full circle in the contrast
        span's LIGHTEST shade, through the same tint map every form
        uses."""
        contrast = ctx.skin.umbra_contrast
        tint = ctx.skin.ring_tint            # the Umbra follows the ring hue
        lightest, darkest = dial.UMBRA_CONTRAST_SPANS[contrast]
        lightest = min(255, lightest)            # spans store window BOUNDS
        if not daylight_active(ctx.skin):
            painter.setBrush(tinted_gray(lightest, tint))
            painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
            return
        if ctx.skin.umbra_form == "gradient":
            # Conical sweep from the top: symmetric stops make the
            # left/right sides exact mirrors, per-pixel smooth.
            gradient = QConicalGradient(QPointF(0.0, 0.0), 90.0)
            gradient.setColorAt(0.0, tinted_gray(lightest, tint))
            gradient.setColorAt(0.5, tinted_gray(darkest, tint))
            gradient.setColorAt(1.0, tinted_gray(lightest, tint))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QRectF(-radius, -radius, 2 * radius, 2 * radius))
            return
        sections = constants.UMBRA_SECTION_COUNTS[ctx.skin.umbra_form]
        span = 360.0 / sections
        shades = umbra_ladder(sections // 2 + 1, contrast)
        for k, value in enumerate(shades):
            painter.setBrush(tinted_gray(value, tint))
            center = k * span
            draw_pie(painter, radius, center - span / 2, center + span / 2)
            if 0 < k < len(shades) - 1:
                # Mirrored partner on the left side; the lightest and
                # darkest stay single.
                draw_pie(
                    painter, radius, 360.0 - center - span / 2, 360.0 - center + span / 2
                )
