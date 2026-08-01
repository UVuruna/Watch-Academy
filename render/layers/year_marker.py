"""The YEAR MARKER layer — earth, moon and the event bodies."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen

from config import archetypes, constants, continents as continents_theme, defaults, dial, glow, palette
from core import angles
from core.year_wheel import almanac_marker_angle, almanac_month_index
from render.asset_variants import moon_lit_region
from render.calendar_mount import calendar_day_arrow, calendar_wheel
from render.context import Cadence, Layer, RenderContext
from render.daylight import moon_transit_opacity
from render.eclipse_glow import draw_event_glow, eclipse_render_state, eclipse_state_glow_strength
from render.painting import dial_point, draw_outlined_text, draw_pixmap_centered, tinted_gray
from render.skin_geometry import hover_factor
from render.subdial import display_year


def earth_region(latitude: float, default: str) -> str:
    """The Earth marker's ART REGION: the active location's continent
    — except at extreme latitudes, where the planet honestly shows its
    POLE (owner 2026-07-15: the Quick Jump flips onto the poles). The
    latitude rides the day context, so a running simulation carries
    its own observer here."""
    if latitude >= continents_theme.EARTH_POLE_LATITUDE:
        return "north_pole"
    if latitude <= -continents_theme.EARTH_POLE_LATITUDE:
        return "south_pole"
    return default


class YearMarkerLayer(Layer):
    """Date markers along the INSIDE of the dial. Earth rides the year
    wheel (summer solstice at the top); the Moon rides its own cycle (new
    moon at the top, full at the bottom, clockwise) showing the current
    illumination. The Elements switches pick which of the two is drawn."""

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        if ctx.skin.show_earth and self._gate(ctx, "earth"):
            self._draw_earth(painter, ctx)
        if ctx.skin.show_moon and self._gate(ctx, "moon"):
            moon_angle = angles.moon_cycle_angle(ctx.tick.moon_fraction)
            # The rim transit only exists while the Earth is also shown.
            opacity = (
                moon_transit_opacity(spec, ctx.tick.year_angle, moon_angle)
                if ctx.skin.show_earth
                else 1.0
            )
            if not ctx.tick.is_moon_up:
                # Below the horizon the marker DIMS (owner spec
                # 2026-07-12; the Settings ▸ Opacity slider).
                opacity *= spec.moon_hidden_alpha
            factor = hover_factor(ctx, "moon")
            # During its ±6 h event window the Moon RELOCATES radially to
            # the ring band centerline (owner 2026-07-16), keeping its
            # cycle angle, so the SILVER halo straddles the ring. A LUNAR
            # eclipse (ROADMAP 15h item 11) rides the SAME relocation with
            # the blood-moon BRONZE glow instead, scaled by its magnitude,
            # and darkens the disc.
            eclipse = ctx.tick.eclipse_event
            lunar_eclipse = (
                eclipse if eclipse is not None and eclipse.kind == "lunar" else None
            )
            lunar_state = (
                eclipse_render_state(lunar_eclipse)
                if lunar_eclipse is not None
                else None
            )
            glowing = ctx.tick.moon_event is not None or lunar_state is not None
            orbit = (
                dial.GLOW_RING_RADIUS_FRACTION
                if glowing
                else spec.moon_orbit_fraction
            )
            pos = dial_point(moon_angle, ctx.radius * orbit)
            if glowing:
                color = (
                    palette.GLOW_ECLIPSE_LUNAR_COLOR
                    if lunar_state is not None
                    else palette.GLOW_MOON_COLOR
                )
                strength = (
                    eclipse_state_glow_strength(lunar_state, lunar_eclipse.magnitude)
                    if lunar_state is not None
                    else 1.0
                )
                # INVISIBLE-FROM-HERE muting (owner verdict "može", fix
                # round E, 2026-07-19): the event is real (the disc
                # darkening/art swap below stay untouched) but the
                # observer cannot actually see it — mute the glow to a
                # desaturated silver at half strength instead.
                if lunar_state is not None and not lunar_eclipse.visible:
                    color = palette.GLOW_ECLIPSE_INVISIBLE_COLOR
                    strength *= glow.ECLIPSE_INVISIBLE_STRENGTH_FACTOR
                draw_event_glow(
                    painter,
                    pos,
                    ctx.radius * spec.moon_scale * factor,
                    color,
                    strength,
                    fringe_color=(
                        palette.ECLIPSE_LUNAR_FRINGE_COLOR
                        if lunar_state is not None
                        and glow.ECLIPSE_STATE_FRINGE[lunar_state]
                        else None
                    ),
                )
            painter.save()
            painter.setOpacity(painter.opacity() * opacity)
            self._draw_moon(
                painter, ctx, pos, 2 * ctx.radius * spec.moon_scale * factor,
                darken_state=lunar_state,
            )
            painter.restore()

    def _draw_earth(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        # The Calendar's ALMANAC wheel carries its OWN real-calendar year
        # mapping (owner 2026-07-16): the Earth marker rides the month
        # wedges (one tick ≈ one day) instead of the shared six-anchor
        # season wheel — every OTHER pointer, the Zodiac wheel included,
        # keeps the shared wheel.
        almanac = (
            ctx.skin.pointer == "calendar"
            and calendar_wheel(ctx.skin) == "almanac"
        )
        year_angle = (
            almanac_marker_angle(ctx.day.local_date)
            if almanac
            else ctx.tick.year_angle
        )
        # During its ±12 h event window the Earth RELOCATES radially to the
        # ring band centerline (owner 2026-07-16), keeping its year-wheel
        # angle, so the GOLDEN halo straddles the ring. A SOLAR eclipse
        # (ROADMAP 15h item 11) rides the SAME relocation with the RED
        # glow instead, scaled by its magnitude, and swaps the Earth's
        # art to the Planets theme's Eclipsed-Sun dual.
        eclipse = ctx.tick.eclipse_event
        solar_eclipse = (
            eclipse if eclipse is not None and eclipse.kind == "solar" else None
        )
        glowing = ctx.tick.season_event is not None or solar_eclipse is not None
        orbit = (
            dial.GLOW_RING_RADIUS_FRACTION if glowing else spec.orbit_fraction
        )
        pos = dial_point(year_angle, ctx.radius * orbit)
        size = 2 * ctx.radius * spec.scale * hover_factor(ctx, "earth")
        if glowing:
            solar_state = (
                eclipse_render_state(solar_eclipse)
                if solar_eclipse is not None
                else None
            )
            if solar_state is None:
                color = palette.GLOW_SUN_COLOR
                strength = 1.0
            else:
                color = (
                    palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
                    if solar_state == "solar_annular"
                    else palette.GLOW_ECLIPSE_SOLAR_COLOR
                )
                strength = eclipse_state_glow_strength(
                    solar_state, solar_eclipse.magnitude
                )
                # INVISIBLE-FROM-HERE muting (owner verdict "može", fix
                # round E, 2026-07-19) — same rule as the lunar marker.
                if not solar_eclipse.visible:
                    color = palette.GLOW_ECLIPSE_INVISIBLE_COLOR
                    strength *= glow.ECLIPSE_INVISIBLE_STRENGTH_FACTOR
            draw_event_glow(painter, pos, size / 2, color, strength)
        if almanac:
            # The day-ARROW at the marker's exact tick (owner 2026-07-16):
            # a small procedural triangle pointing from inside the dial
            # OUTWARD at the ring, so the ring reads today's date.
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(palette.CALENDAR_ARROW_COLOR))
            painter.drawPolygon(calendar_day_arrow(year_angle, ctx.radius))
            painter.restore()
        variant = (
            f"{ctx.skin.earth_style}_"
            f"{earth_region(ctx.day.latitude, spec.default_variant)}_"
            f"{'day' if ctx.tick.is_daylight else 'night'}"
        )
        asset = (
            defaults.ECLIPSE_SOLAR_ART
            if solar_eclipse is not None
            else spec.variants.get(variant)
        )
        if asset is not None:
            # The Earth renders ship on an opaque space background — clip
            # to the marker disc so only the globe shows.
            clip = QPainterPath()
            clip.addEllipse(pos, size / 2, size / 2)
            painter.save()
            painter.setClipPath(clip)
            draw_pixmap_centered(painter, ctx, asset, pos, size)
            painter.restore()
            if (
                2 * ctx.radius >= dial.FULL_TEXT_MIN_DIAMETER
                and ctx.skin.earth_label != "off"
            ):
                # The Earth label — FOUR exclusive modes (owner
                # 2026-07-18: Date / Weekday / Date & Weekday / Full
                # Date) — never fits below the full-text threshold anyway.
                self._draw_earth_label(painter, ctx, pos, size)
        else:
            color = spec.day_color if ctx.tick.is_daylight else spec.night_color
            painter.setPen(
                QPen(
                    QColor(*palette.MARKER_BORDER_RGBA),
                    max(1.0, size * dial.MARKER_BORDER_WIDTH),
                )
            )
            painter.setBrush(QColor(color))
            painter.drawEllipse(pos, size / 2, size / 2)

    def _draw_earth_label(self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float) -> None:
        """The Earth marker's text — FOUR exclusive modes (owner
        2026-07-18, the Design ▸ Earth submenu: Date / Weekday / Date &
        Weekday / Full Date), stored as `skin.earth_label`: "weekday"
        writes "FRI" centered (must work without the date); "date"
        writes "8 Jul" centered; "date_weekday" stacks the date over the
        abbreviated weekday (the OLD combined "Full Date" meaning,
        renamed); "full" stacks the date over the YEAR — the TRUE Full
        Date, reusing `display_year` (already un-shifts a deep-travel
        proxy frame), the same two-row shape the deep-travel year already
        uses on this marker. During a DEEP travel (Session 16, deep proxy
        frame active) the YEAR row OUTRANKS the weekday in "date_weekday"
        mode — far from the present the marker must say WHEN; "full"
        mode already shows the year, so a deep travel is a no-op
        difference there."""
        bold_font = QFont()
        bold_font.setBold(True)
        deep_travel = ctx.day.deep_cycles != 0
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        mode = ctx.skin.earth_label
        if mode == "weekday":
            # Weekday ALONE — a single centered row (owner: "FRI" must work
            # without the date). Uses the date font size (it is the only
            # row, so it gets the full label size).
            bold_font.setPixelSize(
                max(
                    dial.BODY_LABEL_MIN_PX,
                    round(size * dial.EARTH_DATE_TEXT_SIZE),
                )
            )
            draw_outlined_text(
                painter, pos, constants.WEEKDAY_LABELS[today], bold_font
            )
            return
        # "date", "date_weekday" and "full" all lead with the date row.
        text = f"{ctx.day.local_date.day} {ctx.day.local_date:%b}"
        bold_font.setPixelSize(
            max(dial.BODY_LABEL_MIN_PX, round(size * dial.EARTH_DATE_TEXT_SIZE))
        )
        if mode == "full":
            second_row = display_year(ctx)
        elif mode == "date_weekday":
            second_row = (
                display_year(ctx) if deep_travel
                else constants.WEEKDAY_LABELS[today]
            )
        else:
            second_row = None
        if second_row is None:
            draw_outlined_text(painter, pos, text, bold_font)
            return
        offset = size * archetypes.ARCHETYPE_EARTH_DAY_OFFSET
        draw_outlined_text(
            painter, QPointF(pos.x(), pos.y() - offset), text, bold_font
        )
        row_font = QFont()
        row_font.setPixelSize(
            max(
                dial.BODY_LABEL_MIN_PX,
                round(size * archetypes.ARCHETYPE_EARTH_DAY_TEXT_SIZE),
            )
        )
        row_font.setBold(True)
        draw_outlined_text(
            painter, QPointF(pos.x(), pos.y() + offset), second_row,
            row_font,
        )

    def _draw_moon(
        self, painter: QPainter, ctx: RenderContext, pos: QPointF, size: float,
        darken_state: str | None = None,
    ) -> None:
        """Moon image (or procedural disc) with the unlit part shadowed:
        the lit region is the half-disc on the lit side combined with the
        terminator half-ellipse (semi-axis a = R*|cos 2pi*f|) — union when
        gibbous, difference when crescent; everything else is darkened.

        `darken_state` (a LUNAR eclipse render STATE, fix round C
        2026-07-19 — `render.eclipse_glow.eclipse_render_state`) is a TRUE
        brightness reduction of the WHOLE disc — lit and unlit halves
        alike, since totality dims the full face — via
        `QPainter.CompositionMode_Multiply` against an OPAQUE gray whose
        value is `glow.ECLIPSE_STATE_MOON_BRIGHTNESS[darken_state]`
        (0..1 of full value). Multiplying by a NEUTRAL gray scales R/G/B
        equally, i.e. it is exactly "value down" with the hue untouched —
        the owner's fix for the old translucent bronze wash
        (`SourceOver` at a magnitude-scaled alpha), which let a bright
        moon bleed through and read as "still shining, just tinted".
        Fully opaque, TYPE-driven only — magnitude never reaches here."""
        spec = self._skin.year_marker
        fraction = ctx.tick.moon_fraction
        radius = size / 2
        painter.save()
        painter.translate(pos)
        if ctx.day.southern_hemisphere:
            # From the southern hemisphere the moon appears upside down —
            # the lit side swaps left/right (owner spec).
            painter.rotate(180.0)
        painter.setPen(Qt.PenStyle.NoPen)

        if spec.moon_asset is not None:
            draw_pixmap_centered(painter, ctx, spec.moon_asset, QPointF(0, 0), size)
        else:
            painter.setBrush(QColor(spec.moon_dark_color))
            painter.drawEllipse(QPointF(0, 0), radius, radius)

        lit = moon_lit_region(fraction, radius)

        if spec.moon_asset is not None:
            disc = QPainterPath()
            disc.addEllipse(QRectF(-radius, -radius, size, size))
            shadow = QColor(spec.moon_dark_color)
            shadow.setAlphaF(spec.moon_shadow_alpha)
            painter.fillPath(disc.subtracted(lit), shadow)
        else:
            painter.fillPath(lit, QColor(spec.moon_lit_color))
        if darken_state is not None:
            disc = QPainterPath()
            disc.addEllipse(QRectF(-radius, -radius, size, size))
            brightness = glow.ECLIPSE_STATE_MOON_BRIGHTNESS[darken_state]
            value = round(255 * brightness)
            # BLOOD MOON (owner verdict "može", fix round E, 2026-07-19):
            # TOTAL alone wears a deep COPPER tone instead of neutral
            # gray — `tinted_gray`'s tritone at this brightness reads
            # dark AND red-dominant; partial/penumbral stay neutral.
            tint = (
                palette.ECLIPSE_TOTAL_MOON_TINT
                if darken_state == "lunar_total"
                else None
            )
            painter.save()
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_Multiply
            )
            painter.fillPath(disc, tinted_gray(value, tint))
            painter.restore()
        painter.restore()
