"""The YEAR MARKER layer — earth, moon, THE ECLIPSE and the event bodies.

THE THIRD BODY (owner order 2026-08-12, ballot options A1/B2/C1/D1/E1/F1
— and his first sentence of that day, which this layer had failed to
obey: "solarna eklipsa treba da se prikaze odvojeno od EARTH, na mestu na
kruznici u koliko sati se dogadja"). lang-ok: the owner's own sentence,
quoted so the rule cannot be re-derived wrongly a second time.

Until this round an eclipse had no body of its own: a solar eclipse was a
COSTUME the Earth marker wore and a lunar eclipse a costume the Moon
marker wore, so the eclipse stood at the Earth's YEAR angle (the date) or
the Moon's CYCLE angle (the phase) — never at the hour it happens — and
hiding the Earth hid the eclipse with it. Now:

- the eclipse is a THIRD celestial body, seated at
  `angles.time_to_dial_angle` of its own greatest-eclipse instant in
  local time, on the same orbit lane the Earth and the Moon ride;
- the Earth keeps its own art at its own seat, and the Moon keeps its
  phase at its own seat, on the eclipse day like on any other (D1);
- the body stands for `constants.ECLIPSE_BODY_WINDOW_H` (±12 h) around
  that instant (B2 as he corrected it), through its OWN switch,
  `skin.show_eclipse` (C1);
- when it would overlap a marker — the new moon at the top for a solar
  eclipse, the full moon at the bottom for a lunar one — the ECLIPSE
  moves out to the ring band and the marker keeps the ordinary circle
  (E1 + F1, `dial.ECLIPSE_BODY_CLEARANCE`).

The eclipse STYLES did not change: `eclipse_solar_style` and
`eclipse_lunar_style` draw exactly what they drew before, on the new body
instead of on a marker. `horizon_shadow` is unchanged in both senses —
it already wrote at the true hour, on the Moon Horizon Band.
"""

import math


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
from render.painting import (
    dial_point, draw_name_label, draw_outlined_text, draw_pixmap_centered,
    tinted_gray,
)
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


def eclipse_body_angle(ctx: RenderContext, event) -> float:
    """The eclipse body's dial angle: the HOUR of greatest eclipse in the
    watch's own local time, plus the world offset every body on the
    turning face takes (owner order 2026-08-12).

    Module-level and pure so the dial and its teeth read the SAME number
    — a test that recomputed this would be pinning its own arithmetic
    rather than the app's."""
    local_instant = event.instant.astimezone(ctx.day.tzinfo)
    return (
        angles.time_to_dial_angle(local_instant) + ctx.world_offset
    ) % 360.0


def eclipse_body_scale(ctx: RenderContext, solar: bool) -> float:
    """The eclipse body's half-size as a fraction of the dial radius: the
    EARTH's for a solar eclipse, the MOON's for a lunar one, hover
    included — so the third body never reads as a fourth kind of object,
    only as the one whose event it is."""
    spec = ctx.skin.year_marker
    base = spec.scale if solar else spec.moon_scale
    return base * hover_factor(ctx, "eclipse")


def eclipse_body_orbit(ctx: RenderContext, angle: float, scale: float) -> float:
    """The eclipse body's orbit radius — the bodies' own lane, or THE
    RING BAND when it would touch a marker there (owner rule 2026-08-12,
    E1 + F1).

    His rule, in his own words: a solar eclipse happens at new moon,
    whose seat is the TOP, and a lunar eclipse at full moon, whose seat
    is the BOTTOM, so the two fight for one spot whenever the event's
    hour matches that seat. Then "the ECLIPSE goes on the OUTER RING and
    the moon is shown on the ordinary circle as on any other day, only
    now with the graphic that represents the new or full moon".
    lang-ok: the owner's own sentence, the rule this function is.

    So the escape is one-directional and never negotiated: the eclipse
    takes the band, the marker takes the circle — `marker_yields_band`
    is the other half, and it is why the collision is measured against
    the markers' LANE seats rather than wherever they happen to be
    standing. A first cut measured their CURRENT radius instead and the
    render showed why that is wrong: a full Moon is itself relocated to
    the band for six hours around the instant a lunar eclipse happens,
    so the eclipse escaped from on top of the Moon to on top of the
    Moon.

    F1 is what "the same spot" means — TOUCHING DISTANCE, measured
    between centres in dial units, never an angular threshold (the same
    angle means a different distance on a different lane). A hidden
    marker is no obstacle: with the Moon switched off there is nothing
    to escape from and the body stays on the lane where it belongs."""
    lane = dial.earth_moon_orbit_fraction(
        ctx.skin.numeral_outer_ring_size, scale,
    )
    if _lane_seat_is_clear(ctx, angle, scale, lane):
        return lane
    return dial.GLOW_RING_RADIUS_FRACTION


def marker_yields_band(ctx: RenderContext, element: str) -> bool:
    """True when THIS marker must give the ring band up to the eclipse
    and stand on the ordinary circle instead — the second half of the
    owner's rule above.

    It fires only while an eclipse body is actually on the dial AND that
    body has been pushed to the band by this very marker. Without an
    eclipse, or with one that sits happily on the lane, a marker keeps
    its own event relocation exactly as before: this round changed where
    an ECLIPSE stands, never where a solstice or a full moon does."""
    event = ctx.tick.eclipse_body_event if ctx.tick is not None else None
    if event is None or not ctx.skin.show_eclipse:
        return False
    scale = eclipse_body_scale(ctx, event.kind == "solar")
    angle = eclipse_body_angle(ctx, event)
    lane = dial.earth_moon_orbit_fraction(
        ctx.skin.numeral_outer_ring_size, scale,
    )
    return not _seat_is_clear(ctx, angle, scale, lane, _marker_seat(ctx, element))


def _marker_seat(
    ctx: RenderContext, element: str,
) -> tuple[float, float] | None:
    """(angle, half-size) of one marker at its ORDINARY circle, or None
    when it is switched off — a hidden marker is nothing to avoid."""
    spec = ctx.skin.year_marker
    if element == "earth":
        if not ctx.skin.show_earth:
            return None
        return earth_marker_angle(ctx), spec.scale
    if not ctx.skin.show_moon:
        return None
    return (
        (angles.moon_cycle_angle(ctx.tick.moon_fraction)
         + ctx.world_offset) % 360.0,
        spec.moon_scale,
    )


def _lane_seat_is_clear(
    ctx: RenderContext, angle: float, scale: float, lane: float,
) -> bool:
    return all(
        _seat_is_clear(ctx, angle, scale, lane, _marker_seat(ctx, element))
        for element in ("earth", "moon")
    )


def _seat_is_clear(
    ctx: RenderContext, angle: float, scale: float, orbit: float,
    seat: tuple[float, float] | None,
) -> bool:
    """True when a body of half-size `scale` at (`angle`, `orbit`) keeps
    `dial.ECLIPSE_BODY_CLEARANCE` from `seat`, which stands on its own
    ordinary circle. Measured between CENTRES in dial units — never as
    an angular threshold, because the same angle means a different
    distance on a different lane."""
    if seat is None:
        return True
    seat_angle, seat_scale = seat
    centre = dial_point(angle, ctx.radius * orbit)
    other = dial_point(
        seat_angle,
        ctx.radius * dial.earth_moon_orbit_fraction(
            ctx.skin.numeral_outer_ring_size, seat_scale,
        ),
    )
    gap = math.hypot(centre.x() - other.x(), centre.y() - other.y())
    reach = ctx.radius * (scale + seat_scale) * dial.ECLIPSE_BODY_CLEARANCE
    return gap >= reach


def earth_marker_angle(ctx: RenderContext) -> float:
    """The Earth marker's own dial angle, world offset included.

    Its OWN function because two callers need the same number and may
    never drift: the marker itself, and the eclipse body's collision test
    above — an Earth on the Almanac wheel stands somewhere else entirely,
    and a test that used the plain year angle there would let the eclipse
    sit on top of it.

    The Calendar's ALMANAC wheel carries its OWN real-calendar year
    mapping (owner 2026-07-16): the Earth marker rides the month wedges
    (one tick ≈ one day) instead of the shared six-anchor season wheel —
    every OTHER pointer, the Zodiac wheel included, keeps the shared
    wheel. THE WORLD OFFSET (core.world): the year wheel is drawn ON the
    turning dial face, so the Earth rides it — the summer solstice stands
    at the top by day and the WINTER solstice takes the top at night
    (ledger §1). 0.0 in Geocentric."""
    base = (
        almanac_marker_angle(ctx.day.local_date)
        if almanac_wheel_active(ctx)
        else ctx.tick.year_angle
    )
    return (base + ctx.world_offset) % 360.0


def moon_marker_angle(ctx: RenderContext) -> float:
    """The Moon marker's own dial angle, world offset included — the twin
    of `earth_marker_angle`, and for the same reason."""
    return (
        angles.moon_cycle_angle(ctx.tick.moon_fraction) + ctx.world_offset
    ) % 360.0


def _moon_transit_nearness_now(ctx: RenderContext) -> float:
    """How close the Moon is to crossing the Earth's disc right now, 0..1
    — the ONE measure all three crossing switches read. Zero with the
    Earth switched off: there is nothing to cross."""
    if not ctx.skin.show_earth:
        return 0.0
    return moon_transit_nearness(
        ctx.skin.year_marker,
        ctx.tick.year_angle,
        angles.moon_cycle_angle(ctx.tick.moon_fraction),
    )


def moon_marker_scale(ctx: RenderContext) -> float:
    """The Moon marker's DRAWN half-size as a fraction of the dial radius
    — its own scale, the hover enlargement and the transit shrink, in the
    order the painting applies them."""
    spec = ctx.skin.year_marker
    factor = hover_factor(ctx, "moon")
    if spec.transit_shrink:
        factor *= 1.0 - _moon_transit_nearness_now(ctx) * dial.MOON_SHRINK_PASS_DEPTH
    return spec.moon_scale * factor


def moon_marker_orbit(ctx: RenderContext) -> float:
    """The Moon marker's DRAWN orbit radius: the ring band during its own
    event window, the ordinary circle otherwise — eased inward while it
    rides the rim past the Earth, and given up to an eclipse that this
    very marker pushed onto the band (`marker_yields_band`)."""
    spec = ctx.skin.year_marker
    glowing = ctx.tick.moon_event is not None
    if glowing and not marker_yields_band(ctx, "moon"):
        return dial.GLOW_RING_RADIUS_FRACTION
    orbit = dial.earth_moon_orbit_fraction(
        ctx.skin.numeral_outer_ring_size, spec.moon_scale,
    )
    if spec.transit_rim and not glowing:
        orbit -= _moon_transit_nearness_now(ctx) * dial.MOON_LANE_SPLIT_FRACTION
    return orbit


def earth_marker_scale(ctx: RenderContext) -> float:
    """The Earth marker's DRAWN half-size, hover enlargement included."""
    return ctx.skin.year_marker.scale * hover_factor(ctx, "earth")


def earth_marker_orbit(ctx: RenderContext) -> float:
    """The Earth marker's DRAWN orbit radius — the ring band while a
    season event glows, the ordinary circle otherwise, and the circle
    again when an eclipse has taken the band from it."""
    if (
        ctx.tick.season_event is not None
        and not marker_yields_band(ctx, "earth")
    ):
        return dial.GLOW_RING_RADIUS_FRACTION
    return dial.earth_moon_orbit_fraction(
        ctx.skin.numeral_outer_ring_size, ctx.skin.year_marker.scale,
    )


def almanac_wheel_active(ctx: RenderContext) -> bool:
    return (
        ctx.skin.pointer == "calendar"
        and calendar_wheel(ctx.skin) == "almanac"
    )


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
            moon_angle = moon_marker_angle(ctx)
            # The rim transit only exists while the Earth is also shown.
            # THE CROSSING (owner verdict 2026-08-10): the translucent
            # pass is RETIRED — he crossed it out on the proposals page,
            # and it was never legible anyway (two bodies bleeding
            # through each other). All three surviving styles read ONE
            # measure, `moon_transit_nearness`, and none of them dims.
            nearness = _moon_transit_nearness_now(ctx)
            # NO OPACITY ON THE MOON (owner correction 2026-08-11,
            # "mesec opet ima OPACITY!!!" — this retires the 2026-07-12
            # below-horizon dimming): the Moon Horizon Band is what says
            # whether the Moon is up now; the disc itself is always
            # painted solid. `moon_hidden_alpha` stays a stored field so
            # old settings files load, but nothing reads it here.
            # ONE SEAT, TWO READERS (owner question 2026-08-12: "how is
            # the hover not simply every time the cursor crosses that
            # element's own dimensions — what imaginary space is it
            # following?"). It followed a SECOND, hand-written copy of
            # this geometry living in the hit test, and every time the
            # paint moved a marker the copy stayed where it was. So the
            # seat, the lane and the size are module functions now, and
            # `Compositor._element_at` calls these very ones: what is
            # drawn IS what answers the cursor, by construction.
            factor = moon_marker_scale(ctx) / spec.moon_scale
            # During its ±6 h event window the Moon RELOCATES radially to
            # the ring band centerline (owner 2026-07-16), keeping its
            # cycle angle, so the SILVER halo straddles the ring.
            #
            # THE COSTUME IS GONE (owner order 2026-08-12, D1): a lunar
            # eclipse no longer darkens THIS disc and no longer paints it
            # bronze. The Moon keeps its phase here on an eclipse day
            # exactly as on any other day — his words, "mesec je svejedno
            # na kruznici, da li je pun ili prazan" — and the eclipse is
            # drawn as its own body at its own hour by
            # `_draw_eclipse_body` below.
            # lang-ok: the owner's own sentence, quoted as the rule.
            station = marker_marks.station_of_moon_event(ctx.tick.moon_event)
            glowing = ctx.tick.moon_event is not None
            # THE MOON YIELDS THE BAND (owner rule 2026-08-12): during
            # its own event window the Moon relocates to the ring band
            # as always — EXCEPT when an eclipse has been pushed out
            # there by this very Moon, and his sentence says which of
            # the two the ring belongs to then: the eclipse takes it and
            # the Moon "is shown on the ordinary circle as on any other
            # day, only now with the graphic of the new or full moon".
            # lang-ok: the owner's own sentence, quoted as the rule.
            #
            # THE CROSSING SWITCHES (owner ballot verdict 2026-08-11):
            # three independent toggles replacing the one-of styles —
            # shrink, ride-the-rim and cast-shadow compose freely, all
            # three on by default; with none on, the plain Moon simply
            # passes over. The first two live in `moon_marker_scale` and
            # `moon_marker_orbit` above; the shadow is drawn below.
            orbit = moon_marker_orbit(ctx)
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
            if station is not None:
                # THE FOUR STATIONS take the halo's place at a principal
                # instant: birth, youth, the zenith of maturity, age.
                marker_marks.draw_station_mark(
                    painter, spec.moon_station_style, station,
                    ctx.radius * spec.moon_scale * factor,
                    palette.GLOW_MOON_COLOR, ctx.tick.moon_fraction,
                    origin=pos,
                )
            elif glowing:
                draw_event_glow(
                    painter,
                    pos,
                    ctx.radius * spec.moon_scale * factor,
                    palette.GLOW_MOON_COLOR,
                    1.0,
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
            )
            if station is not None:
                # The station's FOREGROUND half — light inside the dark
                # part, which only reads if it is drawn after the disc.
                marker_marks.draw_station_inner_glow(
                    painter, spec.moon_station_style, station,
                    ctx.radius * spec.moon_scale * factor,
                    palette.GLOW_MOON_COLOR, ctx.tick.moon_fraction,
                    origin=pos,
                )
            painter.restore()
        # THE THIRD BODY, drawn LAST so it stands above both markers on
        # the day it belongs to (owner order 2026-08-12).
        if ctx.skin.show_eclipse and self._gate(ctx, "eclipse"):
            self._draw_eclipse_body(painter, ctx)

    # -- the eclipse body ----------------------------------------------

    def _draw_eclipse_body(self, painter: QPainter, ctx: RenderContext) -> None:
        """The eclipse as a body of its own, at the HOUR of greatest
        eclipse (owner order 2026-08-12, ballot A1/B2/C1/D1/E1/F1).

        Nothing about HOW an eclipse looks changed this round: the solar
        styles (`eclipse_solar_style`) and the lunar ones
        (`eclipse_lunar_style`) draw exactly what they drew on the
        markers. What changed is WHERE — `angles.time_to_dial_angle` of
        the event's own local instant, the same reading the hour hand
        gives — and that it no longer borrows another body's seat.

        `horizon_shadow` is deliberately absent here: that style writes
        the eclipse on the Moon Horizon Band, where it can show DURATION
        (his own placement, 2026-08-10), so the band keeps drawing it and
        this body shows the plain face beside it rather than a second,
        contradicting picture of the same event."""
        event = ctx.tick.eclipse_body_event
        if event is None:
            return
        spec = self._skin.year_marker
        state = eclipse_render_state(event)
        solar = event.kind == "solar"
        scale = eclipse_body_scale(ctx, solar)
        angle = eclipse_body_angle(ctx, event)
        orbit = eclipse_body_orbit(ctx, angle, scale)
        pos = dial_point(angle, ctx.radius * orbit)
        size = 2 * ctx.radius * scale
        color, strength = self._eclipse_glow_paint(event, state, solar)
        draw_event_glow(
            painter, pos, size / 2, color, strength,
            fringe_color=(
                palette.ECLIPSE_LUNAR_FRINGE_COLOR
                if not solar and glow.ECLIPSE_STATE_FRINGE[state]
                else None
            ),
        )
        if spec.pointer_enabled:
            # The SAME pointer grammar both markers wear, behind the body
            # (owner correction 2026-08-11: under, never on top).
            marker_marks.draw_pointer(
                painter, spec.marker_pointer_shape, angle,
                ctx.radius, orbit, scale, spec.pointer_color,
                tip_radius=(
                    ctx.radius * ctx.interior_scale
                    * dial.RING_INNER_TICK_INNER_FRACTION
                ),
            )
        if solar:
            # THE OWNER'S OWN ECLIPSE ART, drawn WHOLE (his correction
            # 2026-08-11: the eclipse wears the icon we made). No disc
            # clip here, unlike the Earth marker: that clip exists
            # because the Earth renders ship on an opaque space square,
            # while `sun_eclipse.png` is a black disc IN RAYS on
            # transparency — clipping it to the disc would cut the rays
            # off, which is most of what makes it read as an eclipse.
            draw_pixmap_centered(
                painter, ctx, defaults.ECLIPSE_SOLAR_ART, pos, size
            )
            marker_marks.draw_solar_eclipse(
                painter, spec.eclipse_solar_style, size / 2,
                state, event.magnitude, palette.GLOW_SUN_COLOR, origin=pos,
            )
            return
        self._draw_moon(
            painter, ctx, pos, size,
            darken_state=state, lunar_magnitude=event.magnitude,
        )

    def _eclipse_glow_paint(
        self, event, state: str, solar: bool,
    ) -> tuple[str, float]:
        """The eclipse body's halo colour and strength — the SAME rules
        the markers used to apply, moved here with the body: red for a
        solar eclipse and amber for an annular one, blood-moon bronze for
        a lunar one, each at its state's own strength.

        INVISIBLE-FROM-HERE muting (owner verdict, fix round E,
        2026-07-19) survives unchanged: the event is real, so the body
        and its geometry stay, but the observer cannot actually see it —
        the halo mutes to a desaturated silver at half strength."""
        if solar:
            color = (
                palette.GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR
                if state == "solar_annular"
                else palette.GLOW_ECLIPSE_SOLAR_COLOR
            )
        else:
            color = palette.GLOW_ECLIPSE_LUNAR_COLOR
        strength = eclipse_state_glow_strength(state, event.magnitude)
        if not event.visible:
            color = palette.GLOW_ECLIPSE_INVISIBLE_COLOR
            strength *= glow.ECLIPSE_INVISIBLE_STRENGTH_FACTOR
        return color, strength

    def _draw_earth(self, painter: QPainter, ctx: RenderContext) -> None:
        spec = self._skin.year_marker
        almanac = almanac_wheel_active(ctx)
        year_angle = earth_marker_angle(ctx)
        # During its ±12 h event window the Earth RELOCATES radially to the
        # ring band centerline (owner 2026-07-16), keeping its year-wheel
        # angle, so the GOLDEN halo straddles the ring.
        #
        # THE COSTUME IS GONE (owner order 2026-08-12, A1): a solar
        # eclipse no longer relocates this marker, no longer paints it
        # red and no longer swaps its art. The Earth shows the date on an
        # eclipse day exactly as on any other; the eclipse is its own
        # body at its own hour (`_draw_eclipse_body`).
        glowing = ctx.tick.season_event is not None
        # THE EARTH YIELDS THE BAND on the same rule as the Moon above
        # (owner 2026-08-12): a solstice halo gives way to an eclipse
        # that has been pushed onto the ring by this marker. Both the
        # lane and the size are `earth_marker_orbit`/`earth_marker_scale`
        # so the hit test can read the SAME numbers — see the note in the
        # Moon block above.
        orbit = earth_marker_orbit(ctx)
        pos = dial_point(year_angle, ctx.radius * orbit)
        size = 2 * ctx.radius * earth_marker_scale(ctx)
        station = marker_marks.station_of_season_event(ctx.tick.season_event)
        if station is not None:
            # THE FOUR STATIONS of the year take the halo's place at a
            # turning point — the same grammar the Moon wears, so the
            # language is learned once and read on two clocks.
            marker_marks.draw_sun_station_mark(
                painter, spec.sun_station_style, station, size / 2,
                palette.GLOW_SUN_COLOR, _day_fraction(ctx.day.day_length),
                origin=pos,
            )
        elif glowing:
            draw_event_glow(
                painter, pos, size / 2, palette.GLOW_SUN_COLOR, 1.0
            )
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
        asset = spec.variants.get(variant)
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
        # THE PLATES, WITH THE RING'S HALO (owner order 2026-08-12) —
        # this marker is the case he named: the LOOP theme's blue date
        # over the blue Earth, where the old white-font-with-black-outline
        # left one hairline holding the glyph apart from a same-value
        # field. Every row below now goes through `draw_name_label`, the
        # ONE on-dial label door, which composes from the plate library
        # and stamps the jewels' own dense halo around it.
        deep_travel = ctx.day.deep_cycles != 0
        today = constants.WEEKDAY_BODIES[ctx.day.weekday_index]
        mode = ctx.skin.earth_label
        date_px = max(
            dial.BODY_LABEL_MIN_PX, round(size * dial.EARTH_DATE_TEXT_SIZE)
        )
        if mode == "weekday":
            # Weekday ALONE — a single centered row (owner: "FRI" must work
            # without the date). Uses the date size (it is the only row,
            # so it gets the full label size).
            draw_name_label(
                painter, constants.WEEKDAY_LABELS[today], pos, date_px, ctx=ctx,
            )
            return
        # "date", "date_weekday" and "full" all lead with the date row.
        text = f"{ctx.day.local_date.day} {ctx.day.local_date:%b}"
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
            draw_name_label(painter, text, pos, date_px, ctx=ctx)
            return
        offset = size * archetypes.ARCHETYPE_EARTH_DAY_OFFSET
        draw_name_label(
            painter, text, QPointF(pos.x(), pos.y() - offset), date_px,
            ctx=ctx,
        )
        draw_name_label(
            painter, second_row, QPointF(pos.x(), pos.y() + offset),
            max(
                dial.BODY_LABEL_MIN_PX,
                round(size * archetypes.ARCHETYPE_EARTH_DAY_TEXT_SIZE),
            ),
            ctx=ctx,
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
