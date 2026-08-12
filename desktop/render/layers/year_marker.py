"""The YEAR MARKER layer — earth, moon and the event bodies."""


from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen

from config import archetypes, constants, continents as continents_theme, defaults, dial, glow, palette
from core import angles
from core.year_wheel import almanac_marker_angle, almanac_month_index
from render import marker_marks, moon_face
from render.calendar_mount import calendar_day_arrow, calendar_wheel
from render.context import Cadence, Layer, RenderContext
from render.daylight import moon_transit_nearness
from render.eclipse_glow import draw_event_glow, eclipse_render_state, eclipse_state_glow_strength
from render.painting import dial_point, draw_outlined_text, draw_pixmap_centered, tinted_gray
from render.skin_geometry import hover_factor
from render.subdial import display_year


def _day_fraction(day_length: str) -> float:
    """The day's share of the 24 hours, read off the SAME "HH:MM"
    `ClockTick.day_length` the octa's bottom arm already displays
    (`core.sun.day_length_hm`) rather than recomputed — the Sun's
    "day_night_wedge" station is a picture OF that number, so the two
    must never be able to disagree. A polar day/night writes "24:00"
    or "00:00" there and the wedge lawfully fills or empties."""
    hours, _, minutes = day_length.partition(":")
    return (int(hours) + int(minutes) / 60.0) / 24.0


def earth_region(latitude: float, longitude: float) -> str:
    """The Earth marker's ART REGION: the active location's continent,
    computed LIVE from its own coordinates — except at extreme
    latitudes, where the planet honestly shows its POLE (owner
    2026-07-15: the Quick Jump flips onto the poles). Both coordinates
    ride the day context, so a running simulation (Quick Jump, Time
    Travel, Greenwich) carries its own observer here — the marker's
    face is recomputed every paint instead of freezing on whatever
    continent the skin was built with (owner bug R-28, 2026-08)."""
    if latitude >= continents_theme.EARTH_POLE_LATITUDE:
        return "north_pole"
    if latitude <= -continents_theme.EARTH_POLE_LATITUDE:
        return "south_pole"
    return continents_theme.continent_from_coordinates(latitude, longitude)


class YearMarkerLayer(Layer):
    """Date markers along the INSIDE of the dial. Earth rides the year
    wheel (summer solstice at the top); the Moon rides its own cycle (new
    moon at the top, full at the bottom, clockwise) showing the current
    illumination. The Elements switches pick which of the two is drawn."""

    frame = "rim"

    cadence = Cadence.MINUTE

    def paint(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        if ctx.skin.show_earth and self._gate(ctx, "earth"):
            self._draw_earth(painter, ctx)
        if ctx.skin.show_moon and self._gate(ctx, "moon"):
            # THE WORLD OFFSET (core.world): the moon wheel is drawn ON
            # the turning dial face, so the marker rides it. New moon is
            # at the top by day (`moon_cycle_angle`'s own law) and the
            # night's +180 therefore stands the FULL moon there instead
            # (ledger §1). The transit test below keeps the RAW angles —
            # both markers take the same offset, so their separation is
            # unchanged and adding it twice would only invite drift.
            seat = angles.moon_cycle_angle(ctx.tick.moon_fraction)
            moon_angle = (seat + ctx.world_offset) % 360.0
            # The rim transit only exists while the Earth is also shown.
            # THE CROSSING (owner verdict 2026-08-10): the translucent
            # pass is RETIRED — he crossed it out on the proposals page,
            # and it was never legible anyway (two bodies bleeding
            # through each other). All three surviving styles read ONE
            # measure, `moon_transit_nearness`, and none of them dims.
            nearness = (
                moon_transit_nearness(spec, ctx.tick.year_angle, seat)
                if ctx.skin.show_earth
                else 0.0
            )
            # NO OPACITY ON THE MOON (owner correction 2026-08-11,
            # "mesec opet ima OPACITY!!!" — this retires the 2026-07-12
            # below-horizon dimming): the Moon Horizon Band is what says
            # whether the Moon is up now; the disc itself is always
            # painted solid. `moon_hidden_alpha` stays a stored field so
            # old settings files load, but nothing reads it here.
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
            station = marker_marks.station_of_moon_event(ctx.tick.moon_event)
            glowing = ctx.tick.moon_event is not None or lunar_state is not None
            orbit = (
                dial.GLOW_RING_RADIUS_FRACTION
                if glowing
                # THE LINE AND THE BODIES (owner corrections
                # 2026-08-10/11): per-body tangent to the tick-root
                # line — see `config.dial.earth_moon_orbit_fraction`.
                else dial.earth_moon_orbit_fraction(
                    ctx.skin.numeral_outer_ring_size, spec.moon_scale,
                )
            )
            # THE CROSSING SWITCHES (owner ballot verdict 2026-08-11):
            # three independent toggles replacing the one-of styles —
            # shrink, ride-the-rim and cast-shadow compose freely, all
            # three on by default; with none on, the plain Moon simply
            # passes over.
            if spec.transit_shrink:
                factor *= 1.0 - nearness * dial.MOON_SHRINK_PASS_DEPTH
            if spec.transit_rim and not glowing:
                # RIDE THE RIM (owner correction 2026-08-11: this is the
                # ORIGINAL lane-split motion, restored — the projection
                # cut of 0.14.913 pinned the Moon to one spot instead of
                # letting it travel): inside touching distance the Moon
                # eases smoothly onto an inner lane by the SAME nearness
                # measure, so as the cycle angle keeps moving the Moon
                # traces a circle AROUND the Earth's disc and rejoins
                # the shared lane on the far side.
                orbit -= nearness * dial.MOON_LANE_SPLIT_FRACTION
            pos = dial_point(moon_angle, ctx.radius * orbit)
            earth_pos = None
            if nearness > 0.0 and ctx.skin.show_earth:
                earth_pos = dial_point(
                    (ctx.tick.year_angle + ctx.world_offset) % 360.0,
                    ctx.radius * dial.earth_moon_orbit_fraction(
                        ctx.skin.numeral_outer_ring_size, spec.scale,
                    ),
                )
            if spec.transit_shadow and earth_pos is not None:
                # THE CAST SHADOW (owner correction 2026-08-11: "the one
                # that casts a shadow casts none at all") — a soft dark
                # disc clipped to the EARTH's own disc, under the Moon's
                # position, deepening as the crossing closes. Drawn
                # before the Moon so the shadow reads as falling ON the
                # Earth, never as a tint on the Moon itself. Composes
                # with the other two switches for free: a shrunk Moon
                # casts a smaller shadow (`factor` below), a rim-riding
                # one casts it near the Earth's edge (`pos` above).
                earth_half = ctx.radius * spec.scale * hover_factor(ctx, "earth")
                shadow_clip = QPainterPath()
                shadow_clip.addEllipse(earth_pos, earth_half, earth_half)
                shadow = QColor(palette.MOON_SHADOW_BLACK)
                shadow.setAlphaF(0.55 * nearness)
                painter.save()
                painter.setClipPath(shadow_clip)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(shadow)
                shadow_r = ctx.radius * spec.moon_scale * factor * 1.15
                painter.drawEllipse(pos, shadow_r, shadow_r)
                painter.restore()
            if station is not None and lunar_state is None:
                # THE FOUR STATIONS take the halo's place at a principal
                # instant: birth, youth, the zenith of maturity, age.
                marker_marks.draw_station_mark(
                    painter, spec.moon_station_style, station,
                    ctx.radius * spec.moon_scale * factor,
                    palette.GLOW_MOON_COLOR, ctx.tick.moon_fraction,
                    origin=pos,
                )
            elif glowing:
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
            if spec.pointer_enabled:
                # BEHIND the body (owner correction 2026-08-11, "IZA NE
                # ISPRED" — z under): drawn before the disc, so only the
                # tip's peek and the flanks show.
                marker_marks.draw_pointer(
                    painter, spec.marker_pointer_shape, moon_angle,
                    ctx.radius, orbit, spec.moon_scale * factor,
                    spec.pointer_color,
                    # THE MARKED POINT (owner correction 2026-08-11,
                    # slika 4/5): the 360 tips' own radius — a Moon
                    # relocated onto the ring band sits OUTSIDE it, so
                    # the arrow flips inward at the same point.
                    tip_radius=(
                        ctx.radius * ctx.interior_scale
                        * dial.RING_INNER_TICK_INNER_FRACTION
                    ),
                )
            self._draw_moon(
                painter, ctx, pos, 2 * ctx.radius * spec.moon_scale * factor,
                darken_state=lunar_state,
                lunar_magnitude=(
                    lunar_eclipse.magnitude if lunar_eclipse is not None
                    else None
                ),
            )
            if station is not None and lunar_state is None:
                # The station's FOREGROUND half — light inside the dark
                # part, which only reads if it is drawn after the disc.
                marker_marks.draw_station_inner_glow(
                    painter, spec.moon_station_style, station,
                    ctx.radius * spec.moon_scale * factor,
                    palette.GLOW_MOON_COLOR, ctx.tick.moon_fraction,
                    origin=pos,
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
        # THE WORLD OFFSET (core.world): the year wheel is drawn ON the
        # turning dial face, so the Earth rides it — the summer solstice
        # stands at the top by day and the WINTER solstice takes the top
        # at night (ledger §1). 0.0 in Geocentric.
        year_angle = (
            (
                almanac_marker_angle(ctx.day.local_date)
                if almanac
                else ctx.tick.year_angle
            ) + ctx.world_offset
        ) % 360.0
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
            dial.GLOW_RING_RADIUS_FRACTION
            if glowing
            # THE LINE AND THE BODIES (owner corrections 2026-08-10/11):
            # per-body tangent to the tick-root line — see the Moon's
            # own call above.
            else dial.earth_moon_orbit_fraction(
                ctx.skin.numeral_outer_ring_size, spec.scale,
            )
        )
        pos = dial_point(year_angle, ctx.radius * orbit)
        size = 2 * ctx.radius * spec.scale * hover_factor(ctx, "earth")
        solar_state = (
            eclipse_render_state(solar_eclipse)
            if solar_eclipse is not None
            else None
        )
        station = marker_marks.station_of_season_event(ctx.tick.season_event)
        if station is not None and solar_state is None:
            # THE FOUR STATIONS of the year take the halo's place at a
            # turning point — the same grammar the Moon wears, so the
            # language is learned once and read on two clocks.
            marker_marks.draw_sun_station_mark(
                painter, spec.sun_station_style, station, size / 2,
                palette.GLOW_SUN_COLOR, _day_fraction(ctx.day.day_length),
                origin=pos,
            )
        elif glowing:
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
            painter.drawPolygon(calendar_day_arrow(
                year_angle, ctx.radius * ctx.interior_scale,
            ))
            painter.restore()
        if spec.pointer_enabled:
            # BEHIND the body (owner correction 2026-08-11, "IZA NE
            # ISPRED ZEMLJE, Z INDEX MANJI" — his SECOND time saying it;
            # the 2026-08-09 round moved it on top and that was wrong):
            # drawn before the art, so only the tip's peek past the edge
            # and the flanks beside the curve show.
            marker_marks.draw_pointer(
                painter, spec.marker_pointer_shape, year_angle,
                ctx.radius, orbit, size / (2 * ctx.radius),
                spec.pointer_color,
                # Same marked point as the Moon's call — an Earth in its
                # event window rides the ring band and the arrow flips
                # inward (owner correction 2026-08-11, slika 4/5).
                tip_radius=(
                    ctx.radius * ctx.interior_scale
                    * dial.RING_INNER_TICK_INNER_FRACTION
                ),
            )
        variant = (
            f"{ctx.skin.earth_style}_"
            f"{earth_region(ctx.day.latitude, ctx.day.longitude)}_"
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
            if solar_state is not None:
                # THE ECLIPSE'S OWN GEOMETRY, over the swapped art: the
                # occulting disc ("bite") or the ring gauge
                # ("magnitude_arc"). "halo" adds nothing here — the glow
                # already drawn behind the marker IS that style.
                marker_marks.draw_solar_eclipse(
                    painter, spec.eclipse_solar_style, size / 2,
                    solar_state, solar_eclipse.magnitude,
                    palette.GLOW_SUN_COLOR, origin=pos,
                )
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
        darken_state: str | None = None, lunar_magnitude: float | None = None,
    ) -> None:
        """The Moon marker: the face in the chosen unlit-half treatment
        (`render.moon_face`, owner verdict 2026-08-10), plus whatever a
        lunar eclipse adds on top.

        The terminator geometry is unchanged and still lives in
        `asset_variants.moon_lit_region`; what changed is that the
        shadow is no longer a translucent wash over a full disc — see
        `render/__about/moon_face.md` for why that treatment was
        retired rather than kept as a menu entry.

        `darken_state` (a LUNAR eclipse render STATE, fix round C
        2026-07-19 — `render.eclipse_glow.eclipse_render_state`) reaches
        the disc only in the "halo" eclipse style, where it is a TRUE
        brightness reduction of the WHOLE disc — lit and unlit halves
        alike, since totality dims the full face — via
        `QPainter.CompositionMode_Multiply` against an OPAQUE gray whose
        value is `glow.ECLIPSE_STATE_MOON_BRIGHTNESS[darken_state]`
        (0..1 of full value). Multiplying by a NEUTRAL gray scales R/G/B
        equally, i.e. it is exactly "value down" with the hue untouched —
        the owner's fix for the old translucent bronze wash
        (`SourceOver` at a magnitude-scaled alpha), which let a bright
        moon bleed through and read as "still shining, just tinted".
        Fully opaque, TYPE-driven only — magnitude never reaches THAT
        path. The "umbra_sweep" style takes `lunar_magnitude` instead
        and draws the shadow's real edge; "horizon_shadow" leaves the
        disc alone entirely, because the event is written on the Moon
        Horizon Band where it can show DURATION (the owner's own
        placement of that option, 2026-08-10)."""
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

        def paint_face(target: QPainter) -> None:
            """The FULL-moon face — the plate when the skin ships one,
            a flat lit disc when it does not. `moon_face.draw_moon_disc`
            decides whether this is clipped first (the cut styles) or
            covered after (the opaque style), which is why the old
            asset/procedural branch pair collapsed into one path."""
            if spec.moon_asset is not None:
                draw_pixmap_centered(
                    target, ctx, spec.moon_asset, QPointF(0, 0), size
                )
                return
            target.setBrush(QColor(spec.moon_lit_color))
            target.drawEllipse(QPointF(0, 0), radius, radius)

        moon_face.draw_moon_disc(
            painter, fraction, radius, spec.moon_dark_style,
            paint_face, spec.moon_dark_color,
        )
        if (
            darken_state is not None
            and spec.eclipse_lunar_style == "umbra_sweep"
        ):
            # THE UMBRA SWEEP takes the whole eclipse treatment: Earth's
            # shadow as a real curved edge crossing the face, so the
            # magnitude is geometry. The uniform multiply below is the
            # "halo" style's own darkening and must NOT also run, or the
            # face would be dimmed twice.
            moon_face.draw_umbra_sweep(
                painter, radius, darken_state, lunar_magnitude
            )
            painter.restore()
            return
        if darken_state is not None and spec.eclipse_lunar_style == "halo":
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
