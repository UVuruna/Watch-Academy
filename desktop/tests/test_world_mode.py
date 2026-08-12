"""THE TWO WORLD-MODES — golden values (research/ring_rework.md §1).

Every expectation below is HAND-COMPUTED in its own comment from the
ledger's own numbers, never read back off the implementation:

* Belgrade's DST pair — the star at **-4.17 deg** on 2026-03-28 and at
  **+10.76 deg** on 2026-03-29 (`tests/test_sun.py`'s own golden values)
  — recast as BAND OFFSETS.
* The 2026-07-07 moon at cycle fraction **0.7400** recast under the
  night phase.
* The phase boundary at Belgrade's real sunrise/sunset, and BOTH polar
  regimes at Tromso, where the boundary never arrives at all.

The GEOCENTRIC mode is proved by construction here (both resolvers
reproduce the pre-mode formula exactly, and the world offset is
literally 0.0, so every `+ ctx.world_offset` term in the render layer is
an arithmetic no-op) and by the whole pre-existing suite staying green
untouched.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

from config import defaults, dial
from core import angles, numerals, world
from core.clock_state import build_day_context, build_tick_state
from core.sun import DaylightRegime, compute_sun_day
from data.locations import LocationRepository
from data.moon_phases import shared_moon_phases
from data.seasons import shared_seasons
from render.assets import AssetCache
from render.compositor import Compositor
from render.context import RenderContext
from render.layers.numerals import band_spec

TROMSO = astral.Observer(latitude=69.6489, longitude=18.9551)
OSLO_TZ = ZoneInfo("Europe/Oslo")

SIZE = 360.0
RADIUS = SIZE / 2.0


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def belgrade():
    matches = LocationRepository().find_city("Belgrade")
    serbian = [record for record in matches if "Serbia" in record.path]
    assert serbian, "Belgrade (Serbia) must exist in the locations database"
    return serbian[0]


def _belgrade_star(record, on_date) -> float:
    observer = astral.Observer(
        latitude=record.latitude, longitude=record.longitude
    )
    sun_day = compute_sun_day(observer, on_date, ZoneInfo(record.timezone))
    return angles.star_rotation_deg(sun_day.noon)


def _frame(now: datetime, observer: astral.Observer):
    """One (day, tick) pair, built the way the running watch builds it."""
    day = build_day_context(
        now,
        observer,
        shared_seasons().year_anchors(now.year),
        shared_moon_phases().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def _compositor(mode: str, day, tick, **skin_kw) -> Compositor:
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, world_mode=mode, **skin_kw)
    compositor = Compositor(skin, AssetCache())
    compositor.set_day(day)
    compositor._last_tick = tick
    compositor.note_daylight(tick.is_daylight, animate=False)
    return compositor


# --- The band offset: Belgrade's own two days --------------------------------------


class TestBelgradeBandOffsets:
    """The ledger's DST pair, recast from a STAR rotation into a BAND
    rotation.

    HAND-COMPUTED, from `star_rotation_deg`'s documented meaning ("the
    dial angle at which true solar noon stands, positive = clockwise"):

        2026-03-28  star = -4.17   ->  band must turn +4.17 to carry
                                       that angle to the top
        2026-03-29  star = +10.76  ->  band must turn -10.76

    and the numeral "12", whose OWN seat is `(12 - 12) * 15 = 0`,
    therefore lands at exactly the band offset. At night both take a
    further +180.
    """

    def test_winter_day_band_turns_clockwise(self, belgrade):
        star = _belgrade_star(belgrade, date(2026, 3, 28))
        assert star == pytest.approx(-4.17, abs=0.1)
        offset = world.world_offset_deg("heliocentric", star, True, 0.0)
        # -(-4.17) = +4.17
        assert offset == pytest.approx(4.17, abs=0.1)
        # The numeral 12 rides to +4.17; the numeral standing AT the top
        # is whichever one's own seat is -4.17 (just short of 12).
        assert numerals.hour_angle(12, offset) == pytest.approx(4.17, abs=0.1)

    def test_dst_day_band_turns_counterclockwise(self, belgrade):
        star = _belgrade_star(belgrade, date(2026, 3, 29))
        assert star == pytest.approx(10.76, abs=0.1)
        offset = world.world_offset_deg("heliocentric", star, True, 0.0)
        # -(+10.76) = -10.76, folded onto the circle = 349.24
        assert offset == pytest.approx(349.24, abs=0.1)
        assert numerals.hour_angle(12, offset) == pytest.approx(-10.76, abs=0.1)

    def test_night_adds_exactly_half_a_circle(self, belgrade):
        star = _belgrade_star(belgrade, date(2026, 3, 29))
        night = world.world_offset_deg("heliocentric", star, True, 180.0)
        # -10.76 + 180 = 169.24
        assert night == pytest.approx(169.24, abs=0.1)
        # and hour 0 — seat (0-12)*15 = -180 — now stands at the top.
        assert numerals.hour_angle(0, night) == pytest.approx(-10.76, abs=0.1)

    def test_solar_rotation_off_leaves_only_the_phase(self, belgrade):
        star = _belgrade_star(belgrade, date(2026, 3, 29))
        assert world.world_offset_deg("heliocentric", star, False, 0.0) == 0.0
        assert world.world_offset_deg(
            "heliocentric", star, False, 180.0
        ) == 180.0


def test_equinox_sanity_night_without_the_solar_part_is_exactly_180():
    """The night inversion works with Solar Rotation OFF (ledger §1:
    "visible even with Solar Rotation OFF") — and it is EXACTLY half a
    circle, no float drift, whatever the star is doing."""
    for star in (-4.17, 0.0, 10.76, 179.0):
        assert world.world_offset_deg(
            "heliocentric", star, False, 180.0
        ) == 180.0
        assert world.pointer_rotation_deg(
            "heliocentric", star, False, 180.0
        ) == 180.0


# --- The phase: the sun's ACTUAL state ---------------------------------------------


def test_phase_flips_at_belgrades_real_sunset_and_sunrise(belgrade):
    """One minute before sunset is DAYLIGHT, one minute after is NIGHT —
    and the same at sunrise. The phase is read off the sun's own state,
    never off a count of flips."""
    tz = ZoneInfo(belgrade.timezone)
    observer = astral.Observer(
        latitude=belgrade.latitude, longitude=belgrade.longitude
    )
    on_date = date(2026, 7, 7)
    sun_day = compute_sun_day(observer, on_date, tz)
    assert sun_day.regime is DaylightRegime.NORMAL
    minute = timedelta(minutes=1)
    for boundary, before, after in (
        (sun_day.sunset, True, False),
        (sun_day.sunrise, False, True),
    ):
        day, _ = _frame(boundary, observer)
        assert build_tick_state(boundary - minute, day).is_daylight is before
        assert build_tick_state(boundary + minute, day).is_daylight is after
        assert world.night_phase_deg(before) == (0.0 if before else 180.0)
        assert world.night_phase_deg(after) == (0.0 if after else 180.0)


@pytest.mark.parametrize(
    ("start", "daylight", "regimes"),
    [
        (
            date(2026, 6, 10), True,
            (DaylightRegime.POLAR_DAY, DaylightRegime.WHITE_NIGHTS),
        ),
        (
            date(2026, 12, 10), False,
            (DaylightRegime.POLAR_NIGHT, DaylightRegime.TWILIGHT_ONLY),
        ),
    ],
)
def test_tromso_polar_regimes_never_transition(start, daylight, regimes):
    """Tromso stands in ONE phase for months and nothing ever fires —
    the whole reason the phase is derived from the sun's state instead
    of counting two flips a day. Five days, every hour: zero
    transitions."""
    states = []
    for offset in range(5):
        on_date = start + timedelta(days=offset)
        assert compute_sun_day(TROMSO, on_date, OSLO_TZ).regime in regimes
        moment = datetime(
            on_date.year, on_date.month, on_date.day, tzinfo=OSLO_TZ
        )
        day, _ = _frame(moment, TROMSO)
        for hour in range(24):
            states.append(
                build_tick_state(
                    moment + timedelta(hours=hour), day
                ).is_daylight
            )
    assert set(states) == {daylight}
    transitions = sum(
        1 for a, b in zip(states, states[1:]) if a != b
    )
    assert transitions == 0


# --- The world offset reaches the drawn dial ---------------------------------------


def test_the_outer_band_plate_is_keyed_on_the_world_offset(app):
    """Wave 3's `offset_deg` finally carries a live value — and the
    INNER band still keys on 0.0, so its plate is SHARED across both
    phases (ledger §2: "the inner band NEVER rotates, in any mode")."""
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, world_mode="heliocentric")
    day, tick = _frame(
        datetime(2026, 3, 29, 12, 0, tzinfo=ZoneInfo("Europe/Belgrade")),
        astral.Observer(latitude=44.7866, longitude=20.4489),
    )
    for phase in (0.0, 180.0):
        offset = world.world_offset_deg(
            "heliocentric", day.star_rotation, True, phase
        )
        ctx = RenderContext(
            skin=skin, day=day, tick=tick, radius=RADIUS,
            cache=AssetCache(), dpr=1.0, world_offset=offset,
        )
        assert band_spec(skin, "outer", ctx).offset_deg == offset
        assert band_spec(skin, "inner", ctx).offset_deg == 0.0


def test_earth_and_moon_take_the_top_at_night(app):
    """EARTH and MOON ride the turning dial face (ledger §1). With the
    solar part off, the night phase is exactly +180, so:

      * the MOON's full phase (cycle fraction 0.5 -> 180 deg, the
        BOTTOM by day) stands at the TOP;
      * the new moon (0.0 -> the top by day) stands at the bottom;
      * the EARTH's own year angle moves half a circle with it, which is
        the winter solstice on top where the summer solstice stood.

    Proved through the compositor's own hit test, which mirrors the
    DRAWN position exactly (its standing invariant)."""
    tz = ZoneInfo("Europe/Belgrade")
    observer = astral.Observer(latitude=44.7866, longitude=20.4489)
    day, tick = _frame(datetime(2026, 7, 7, 23, 30, tzinfo=tz), observer)
    assert tick.is_daylight is False          # a real night, really derived
    night = _compositor(
        "heliocentric", day, tick, solar_rotation=False,
        show_earth=False, show_moon=True,
    )
    assert night._world_offset() == 180.0
    marker = night._skin.year_marker

    from render.painting import dial_point

    def moon_at(fraction: float, angle: float) -> bool:
        # No glow window and no eclipse: the marker keeps its own orbit
        # instead of relocating to the ring centreline.
        night._last_tick = dataclasses.replace(
            tick, moon_fraction=fraction, moon_event=None, eclipse_event=None,
        )
        # THE CLEAR ORBIT LANE (owner verdict 2026-08-09): the DRAWN
        # radius, not the old fixed `moon_orbit_fraction` field.
        orbit = dial.earth_moon_orbit_fraction(
            night._skin.numeral_outer_ring_size,
            max(marker.scale, marker.moon_scale),
        )
        spot = dial_point(angle, RADIUS * orbit)
        return night._element_at(spot, RADIUS, 0.0, "sun") == "moon"

    assert moon_at(0.5, 0.0)          # FULL moon on top at night
    assert moon_at(0.0, 180.0)        # new moon at the bottom at night
    # The 2026-07-07 golden fraction, recast: 0.7400 * 360 = 266.4 by
    # day, + 180 = 86.4 at night.
    assert moon_at(0.7400, 86.4)
    assert not moon_at(0.5, 180.0)    # the DAY seat is empty at night

    # The EARTH the same way: its year angle takes the same half circle,
    # which is the winter solstice standing where the summer one did.
    earth_night = _compositor(
        "heliocentric", day, tick, solar_rotation=False,
        show_earth=True, show_moon=False,
    )
    earth_night._last_tick = dataclasses.replace(
        tick, season_event=None, eclipse_event=None,
    )
    earth_marker = earth_night._skin.year_marker
    # THE CLEAR ORBIT LANE (owner verdict 2026-08-09): the DRAWN radius.
    earth_orbit = dial.earth_moon_orbit_fraction(
        earth_night._skin.numeral_outer_ring_size,
        max(earth_marker.scale, earth_marker.moon_scale),
    )
    for angle, expected in (
        ((tick.year_angle + 180.0) % 360.0, "earth"),
        (tick.year_angle % 360.0, None),
    ):
        spot = dial_point(angle, RADIUS * earth_orbit)
        assert earth_night._element_at(spot, RADIUS, 0.0, "sun") == expected


def test_a_ring_jewel_hit_zone_follows_its_rotated_seat(app):
    """The Omega seat is a ring LETTER at 180 deg. In Heliocentric night
    it stands at the TOP instead — and its hit zone goes with it, or the
    reveal-week double-click would fire on empty ring."""
    tz = ZoneInfo("Europe/Belgrade")
    observer = astral.Observer(latitude=44.7866, longitude=20.4489)
    day, tick = _frame(datetime(2026, 7, 7, 23, 30, tzinfo=tz), observer)
    night = _compositor(
        "heliocentric", day, tick, solar_rotation=False,
    )
    from render.painting import dial_point
    seat = RADIUS * dial.RING_JEWEL_RADIUS_FRACTION
    top = dial_point(0.0, seat)
    bottom = dial_point(180.0, seat)
    assert night.hit_omega(RADIUS + top.x(), RADIUS + top.y(), SIZE)
    assert not night.hit_omega(
        RADIUS + bottom.x(), RADIUS + bottom.y(), SIZE
    )
    # ...and Geocentric keeps it exactly where it has always been.
    plain = _compositor("geocentric", day, tick)
    assert plain.hit_omega(RADIUS + bottom.x(), RADIUS + bottom.y(), SIZE)
    assert not plain.hit_omega(RADIUS + top.x(), RADIUS + top.y(), SIZE)


# --- THE ARC READING LAW -----------------------------------------------------------


class TestTheArcReadingLaw:
    """Ledger §1: "Every member re-seats READABLY at its new position …
    NOTHING IS MIRRORED."

    Found on the real dial, 2026-08-06: DOMY's bottom crown word ANGER
    came up at the top of the night dial spelling **REGNA**. Every
    LETTER was upright — the seating law had done its job — but the WORD
    read backwards, because a text arc only reads left to right thanks
    to dial-x running in OPPOSITE senses across the two halves of the
    circle. Crossing the horizon reverses the run; the reflection about
    the arc's own new centre turns it back."""

    def test_a_bottom_arc_carried_to_the_top_keeps_its_reading_order(self):
        # ANGER's five letters, laid out counter-clockwise under the
        # bottom (the way a bottom arc must read left to right): seats
        # 190, 185, 180, 175, 170 — A leftmost, R rightmost.
        seats = (190.0, 185.0, 180.0, 175.0, 170.0)
        assert world.arc_centre_deg(seats) == pytest.approx(180.0)
        flipped = world.arc_seats(seats, 180.0)
        # HAND-COMPUTED: centre 180 + 180 = 360 ≡ 0; reflection about it
        # gives 2*180 + 180 - seat = 540 - seat, mod 360:
        #   190 -> 350,  185 -> 355,  180 -> 0,  175 -> 5,  170 -> 10
        assert flipped == pytest.approx((350.0, 355.0, 0.0, 5.0, 10.0))
        # A now sits LEFT of R over the top — still A-N-G-E-R.
        assert numerals.fold_angle(flipped[0]) < numerals.fold_angle(flipped[-1])

    def test_a_stay_at_home_arc_is_a_plain_rotation(self):
        """A small solar offset that keeps the arc in its own half must
        NOT reflect — that would mirror a word for no reason."""
        seats = (350.0, 355.0, 0.0, 5.0, 10.0)
        assert world.arc_seats(seats, -10.76) == pytest.approx(
            (339.24, 344.24, 349.24, 354.24, 359.24)
        )

    def test_the_law_reaches_the_live_crown(self, app):
        """`compose_crown` lays 12:35 out over the top; at night the
        same five glyphs must still read 1-2-:-3-5 under the bottom."""
        from render.numeral_bands import compose_crown
        glyph_set = {ch: object() for ch in "0123456789:"}
        sequence = tuple("12:35")
        day = compose_crown(glyph_set, sequence, "top")
        night = compose_crown(glyph_set, sequence, "top", offset_deg=180.0)
        assert [g for g, _a, _r in night] == [g for g, _a, _r in day]
        # "Reads left to right" is a claim about SCREEN X, so measure
        # screen x (`render.painting.dial_point`'s own `sin theta`): it
        # must increase along the sequence in BOTH phases. Before the
        # fix the night arc's x DECREASED — that is what "REGNA" was.
        import math
        for composed in (day, night):
            xs = [math.sin(math.radians(seat)) for _g, seat, _r in composed]
            assert xs == sorted(xs), "the crown must read left to right"
        # ...and every glyph still stands upright at its new seat.
        for _g, seat, rotation in night:
            assert rotation == angles.readable_rotation_deg(seat)

    def test_a_word_hover_zone_follows_its_reflected_word(self, app):
        """The hover centre goes through the SAME map the letters do, so
        the zone lands on the word rather than on its mirror image."""
        centre = 180.0
        for offset in (0.0, -10.76, 180.0, 169.24):
            first = world.arc_seat_deg(190.0, centre, offset)
            last = world.arc_seat_deg(170.0, centre, offset)
            middle = world.arc_seat_deg(180.0, centre, offset)
            # the word's own centre stays exactly between its ends
            span = ((last - first + 180.0) % 360.0) - 180.0
            assert numerals.fold_angle(middle - first) == pytest.approx(
                span / 2.0
            )


# --- The Geocentric regression -----------------------------------------------------


def test_geocentric_reproduces_the_pre_mode_rotation_exactly(app):
    """`world_mode="geocentric"` is a bit-for-bit no-op: the pointer rotation
    is the old one-line formula and the world offset is literally 0.0 —
    so every `+ ctx.world_offset` the render layer gained adds nothing,
    in EITHER phase and with the solar switch either way."""
    tz = ZoneInfo("Europe/Belgrade")
    observer = astral.Observer(latitude=44.7866, longitude=20.4489)
    for hour in (12, 23):
        day, tick = _frame(
            datetime(2026, 3, 29, hour, 30, tzinfo=tz), observer
        )
        for solar in (True, False):
            plain = _compositor("geocentric", day, tick, solar_rotation=solar)
            legacy = day.star_rotation if solar else 0.0
            assert plain._rotation() == legacy
            assert plain._world_offset() == 0.0
            assert plain._phase_target() == 0.0
            # ...whatever the sun is doing: the phase never leaves 0.
            assert plain.note_daylight(False, animate=True) is False
            assert plain.phase_deg() == 0.0


def test_geocentric_keeps_belgrades_two_golden_star_values(belgrade):
    """The ledger's DST pair, held EXACTLY where the pre-mode dial held
    it: `_rotation()` in Geocentric is `day.star_rotation` itself, not a
    value that merely rounds to it — `-4.17` on 2026-03-28 and `+10.76`
    on 2026-03-29 (`tests/test_sun.py`'s own goldens), while the world
    offset stays literally 0.0 in both phases."""
    observer = astral.Observer(
        latitude=belgrade.latitude, longitude=belgrade.longitude
    )
    tz = ZoneInfo(belgrade.timezone)
    for on_date, golden in (
        (date(2026, 3, 28), -4.17), (date(2026, 3, 29), 10.76),
    ):
        star = _belgrade_star(belgrade, on_date)
        assert star == pytest.approx(golden, abs=0.1)
        day, tick = _frame(
            datetime(
                on_date.year, on_date.month, on_date.day, 12, 0, tzinfo=tz
            ),
            observer,
        )
        assert day.star_rotation == pytest.approx(golden, abs=0.1)
        plain = _compositor("geocentric", day, tick)
        assert plain._rotation() == day.star_rotation      # bit for bit
        assert plain._world_offset() == 0.0
        # ...and the SAME star, in Heliocentric, is handed to the world
        # as its exact negation — the two never drift apart.
        turned = _compositor("heliocentric", day, tick)
        assert turned._rotation() == 0.0                   # the star stands
        assert turned._world_offset() == pytest.approx(
            (-day.star_rotation) % 360.0
        )


# --- The equinox: a flip moment that really arrives --------------------------------


def test_the_equinox_day_flips_at_its_own_sunrise_and_sunset(app, belgrade):
    """The 2026 March equinox (`Database/seasons_utc.json`: 2026-03-20
    14:45:57 UTC) over Belgrade — the day the dial's own 90 deg anchor
    falls on. HAND-COMPUTED goldens for that date: sunrise 05:41:55,
    sunset 17:50:10 local, a 12 h 08 m day (the equinox's own few
    minutes over twelve hours, from refraction and the sun's disc).

    Both boundaries are GENUINE transitions, so both animate — and each
    one lands the dial on exactly the other phase."""
    tz = ZoneInfo(belgrade.timezone)
    observer = astral.Observer(
        latitude=belgrade.latitude, longitude=belgrade.longitude
    )
    equinox = shared_seasons().year_anchors(2026).instants[1]
    on_date = equinox.astimezone(tz).date()
    assert on_date == date(2026, 3, 20)
    sun_day = compute_sun_day(observer, on_date, tz)
    assert sun_day.regime is DaylightRegime.NORMAL
    assert sun_day.sunrise.strftime("%H:%M") == "05:41"
    assert sun_day.sunset.strftime("%H:%M") == "17:50"
    assert abs(
        (sun_day.sunset - sun_day.sunrise) - timedelta(hours=12, minutes=8)
    ) < timedelta(minutes=1)

    minute = timedelta(minutes=1)
    day, _ = _frame(sun_day.noon, observer)
    for boundary, before, after in (
        (sun_day.sunrise, False, True),
        (sun_day.sunset, True, False),
    ):
        assert build_tick_state(boundary - minute, day).is_daylight is before
        assert build_tick_state(boundary + minute, day).is_daylight is after
        # The dial standing in `before` and told `after` TURNS, and the
        # turn ends on the other phase exactly.
        watch = _compositor(
            "heliocentric",
            day,
            build_tick_state(boundary - minute, day),
            solar_rotation=False,
        )
        assert watch.phase_deg() == (0.0 if before else 180.0)
        assert watch.note_daylight(after, animate=True, now=0.0) is True
        assert watch.phase_deg(now=dial.WORLD_FLIP_DURATION_S) == (
            0.0 if after else 180.0
        )


# --- The hands: the hour turns, the minute never does ------------------------------


class _RotationRecorder:
    """A duck-typed QPainter that records only what this test asks:
    every angle a layer rotates by. The hand layer's whole visual
    contract is that one number."""

    def __init__(self):
        self.angles: list[float] = []

    def save(self) -> None:
        pass

    def restore(self) -> None:
        pass

    def rotate(self, angle: float) -> None:
        self.angles.append(angle)

    def drawPixmap(self, *args) -> None:      # noqa: N802 — Qt spelling
        pass


def _hand_angle(skin, kind: str, ctx) -> float:
    from render.layers.hand import HandLayer

    recorder = _RotationRecorder()
    HandLayer(skin, kind).paint(recorder, ctx)
    assert len(recorder.angles) == 1
    return recorder.angles[0]


def test_the_hour_hand_takes_the_night_half_turn_and_the_others_do_not(app):
    """Ledger §1: "the HOUR hand takes +180 (minute/seconds hands do not
    — they read the fixed inner band)".

    Proved on the DRAWN angle — the number the layer hands to
    `painter.rotate` — with the solar part off, so the night offset is
    exactly 180 and the expectation is plain addition. Timekeeping
    itself is untouched: `tick.hour_angle` is still zone time in both
    modes, which is what every non-visual consumer reads."""
    tz = ZoneInfo("Europe/Belgrade")
    observer = astral.Observer(latitude=44.7866, longitude=20.4489)
    day, tick = _frame(datetime(2026, 7, 7, 23, 30, tzinfo=tz), observer)
    assert tick.is_daylight is False
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, world_mode="heliocentric",
        solar_rotation=False,
    )

    def context(offset: float):
        return RenderContext(
            skin=skin, day=day, tick=tick, daylight=tick.is_daylight,
            radius=RADIUS, cache=AssetCache(), dpr=1.0, world_offset=offset,
        )

    night = context(180.0)
    assert _hand_angle(skin, "hour", night) == tick.hour_angle + 180.0
    assert _hand_angle(skin, "minute", night) == tick.minute_angle
    assert _hand_angle(skin, "second", night) == tick.second_angle
    # ...and by day (offset 0.0, which is also every Geocentric frame)
    # all three read plain zone time, exactly as before the mode existed.
    daylight = context(0.0)
    assert _hand_angle(skin, "hour", daylight) == tick.hour_angle
    assert _hand_angle(skin, "minute", daylight) == tick.minute_angle
    assert _hand_angle(skin, "second", daylight) == tick.second_angle


# --- The flip ----------------------------------------------------------------------


class TestTheFlip:
    """An ORGANIC transition turns; a clock correction snaps."""

    def _night_compositor(self, day, tick):
        return _compositor("heliocentric", day, tick, solar_rotation=False)

    @pytest.fixture
    def frame(self, app):
        tz = ZoneInfo("Europe/Belgrade")
        observer = astral.Observer(latitude=44.7866, longitude=20.4489)
        return _frame(datetime(2026, 7, 7, 12, 0, tzinfo=tz), observer)

    def test_an_organic_transition_passes_through_intermediate_values(self, frame):
        day, tick = frame
        watch = self._night_compositor(day, tick)
        assert watch.phase_deg() == 0.0                 # daylight, standing
        assert watch.note_daylight(False, animate=True, now=100.0) is True
        assert watch.phase_deg(now=100.0) == 0.0
        half = watch.phase_deg(now=100.0 + dial.WORLD_FLIP_DURATION_S / 2)
        assert 0.0 < half < 180.0
        assert half == pytest.approx(90.0)              # smoothstep midpoint
        quarter = watch.phase_deg(
            now=100.0 + dial.WORLD_FLIP_DURATION_S / 4
        )
        assert 0.0 < quarter < half
        assert watch.flip_active(now=100.0 + 0.1) is True
        assert watch.phase_deg(
            now=100.0 + dial.WORLD_FLIP_DURATION_S
        ) == 180.0
        assert watch.flip_active(
            now=100.0 + dial.WORLD_FLIP_DURATION_S
        ) is False

    def test_a_clock_jump_applies_instantly_with_no_intermediate_frame(self, frame):
        """A WM_TIMECHANGE is not a sunset (owner bug 2026-08-06): the
        phase is THERE, and `flip_active` never becomes True — so the
        controller never arms a frame timer and no hover sweep runs."""
        day, tick = frame
        watch = self._night_compositor(day, tick)
        assert watch.note_daylight(False, animate=False, now=100.0) is False
        assert watch.phase_deg(now=100.0) == 180.0
        assert watch.flip_active(now=100.0) is False
        assert watch._phase_target() == 180.0

    def test_a_phase_that_did_not_change_never_animates(self, frame):
        """Polar day, hour after hour: the same answer, no motion."""
        day, tick = frame
        watch = self._night_compositor(day, tick)
        for _ in range(10):
            assert watch.note_daylight(True, animate=True) is False
        assert watch.flip_active() is False

    def test_the_composite_holds_only_the_two_phase_variants(self, frame):
        """The band plate is re-rendered ONCE at the TARGET offset —
        the move itself rotates finished pixels. Mid-flip the composite
        key must therefore NOT move."""
        day, tick = frame
        watch = self._night_compositor(day, tick)
        watch.render_offscreen(SIZE, 1.0, day, tick)
        daylight_key = watch._composite_key
        assert watch.note_daylight(False, animate=True, now=100.0) is True
        keys = set()
        for step in (0.0, 0.3, 0.6, 0.9, 1.2):
            watch.render_offscreen(SIZE, 1.0, day, tick)
            keys.add(watch._composite_key)
        assert len(keys) == 1, "a flip must not re-key the composite per frame"
        night_key = keys.pop()
        assert night_key != daylight_key
        assert {daylight_key[-1], night_key[-1]} == {0.0, 180.0}
