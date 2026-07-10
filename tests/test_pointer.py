"""Pointer variants (hexa/cross/octa): slot layouts, shared-slot
priority, palette presets, the octa bottom slot, the Umbra and the
solar-rotation toggle."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
import math
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import constants, defaults
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor, _build_layers
from render.layers import (
    BottomSlotLayer,
    HandLayer,
    palette_for,
    today_slot_theta,
    umbra_ladder,
    visible_occupant,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def july_wednesday(app):
    """2026-07-08 (a Wednesday) at noon in Belgrade."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    day = build_day_context(
        now,
        observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


# --- Slot layouts ---------------------------------------------------------------


def test_every_layout_seats_the_whole_week():
    for pointer, slots in constants.POINTER_WEEKDAY_SLOTS.items():
        seated = [body for _, occupants in slots for body in occupants]
        if pointer in ("hexa", "trio"):
            seated.append("sun")     # hexa and trio center the Sun
        assert sorted(seated) == sorted(constants.WEEKDAY_BODIES), pointer


def test_slot_angles_sit_on_the_pointer_arms():
    for pointer, slots in constants.POINTER_WEEKDAY_SLOTS.items():
        arm_step = 360.0 / constants.POINTER_POINTS[pointer]
        for angle, _ in slots:
            assert angle % arm_step == 0.0, (pointer, angle)


def test_octa_reserves_the_bottom_arm_for_the_info_slot():
    occupied = [angle for angle, _ in constants.POINTER_WEEKDAY_SLOTS["octa"]]
    assert constants.OCTA_TIME_SLOT_ANGLE not in occupied


# --- Shared-slot priority (owner rule) --------------------------------------------


def test_shared_slot_shows_the_next_upcoming_day():
    """Owner's example, Wednesday: of the pairs {Mon|Sat}, {Thu|Sun},
    {Tue|Fri} the visible bodies are Sat, Thu, Fri — the smaller forward
    distance from today wins."""
    assert visible_occupant(("moon", "saturn"), "mercury") == "saturn"
    assert visible_occupant(("jupiter", "sun"), "mercury") == "jupiter"
    assert visible_occupant(("mars", "venus"), "mercury") == "venus"


def test_today_always_wins_its_shared_slot():
    assert visible_occupant(("jupiter", "sun"), "sun") == "sun"
    assert visible_occupant(("jupiter", "sun"), "jupiter") == "jupiter"
    assert visible_occupant(("moon", "saturn"), "saturn") == "saturn"


def test_today_slot_positions():
    assert today_slot_theta("hexa", "sun") is None       # center, not an arm
    assert today_slot_theta("hexa", "mercury") == 180.0
    assert today_slot_theta("cross", "sun") == 0.0       # shares the top arm
    assert today_slot_theta("cross", "mercury") == 180.0  # Wednesday alone at the bottom
    assert today_slot_theta("octa", "sun") == 0.0
    assert today_slot_theta("octa", "mercury") == 135.0


# --- Star geometry -----------------------------------------------------------------


def test_cross_arms_borrow_the_octa_shape():
    """Owner spec (cross.png): the cross is the octa star WITHOUT the
    four diagonal arms — slim diamonds with gaps, not a fat 4-star."""
    half_angles = constants.POINTER_ARM_HALF_ANGLE_DEG
    assert half_angles["cross"] == half_angles["octa"]
    for pointer in ("hexa", "octa"):
        assert half_angles[pointer] == 180.0 / constants.POINTER_POINTS[pointer]


# --- Palette presets (owner: 5 — hexa/octa paint+light, cross seasons) -------------


def test_palette_presets_cover_every_pointer_and_style():
    for pointer, arms in constants.POINTER_POINTS.items():
        for style in constants.PALETTE_STYLES:
            palette = defaults.PALETTE_PRESETS[(pointer, style)]
            assert len(palette) == arms, (pointer, style)


def test_cross_serves_one_seasons_palette_under_both_styles():
    assert (
        defaults.PALETTE_PRESETS[("cross", "paint")]
        == defaults.PALETTE_PRESETS[("cross", "light")]
    )


def test_palette_for_selects_the_skin_choice():
    paint = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa")
    light = dataclasses.replace(paint, palette_style="light")
    assert palette_for(paint) == defaults.PALETTE_PRESETS[("octa", "paint")]
    assert palette_for(light) == defaults.PALETTE_PRESETS[("octa", "light")]


# --- Octa bottom slot ----------------------------------------------------------------


def test_bottom_slot_layer_rides_only_the_octa_stack():
    octa = _build_layers(dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa"))
    hexa = _build_layers(defaults.DEFAULT_SKIN)
    assert any(isinstance(layer, BottomSlotLayer) for layer in octa)
    assert not any(isinstance(layer, BottomSlotLayer) for layer in hexa)
    # The slot text draws OVER the hands (owner spec), like the center body.
    slot_index = next(
        i for i, layer in enumerate(octa) if isinstance(layer, BottomSlotLayer)
    )
    last_hand = max(
        i for i, layer in enumerate(octa) if isinstance(layer, HandLayer)
    )
    assert slot_index > last_hand


@pytest.mark.parametrize("mode", constants.OCTA_SLOT_MODES)
def test_octa_slot_modes_render(july_wednesday, mode):
    day, tick = july_wednesday
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa", octa_slot=mode)
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200        # painted, no crash


# --- Render smoke -------------------------------------------------------------------


@pytest.mark.parametrize("pointer", ["cross", "octa", "trio"])
def test_pointer_variants_render(july_wednesday, pointer):
    day, tick = july_wednesday
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer=pointer)
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(2, 2).alpha() == 0           # corners stay transparent
    assert image.pixelColor(180, 8).alpha() > 200        # ring painted
    assert image.pixelColor(333, 180).alpha() > 200      # disc touches the ring


def test_trio_centers_the_sun_and_pairs_the_week():
    """Owner-approved trio pairing: Faith 12h = Jupiter+Saturn, Love 20h
    = Venus+Mars, Hope 4h = Moon+Mercury; Sunday's Sun in the center."""
    from render.layers import today_slot_theta

    assert today_slot_theta("trio", "sun") is None
    slots = dict(constants.POINTER_WEEKDAY_SLOTS["trio"])
    assert slots[0.0] == ("jupiter", "saturn")
    assert slots[120.0] == ("venus", "mars")
    assert slots[240.0] == ("moon", "mercury")


def test_trio_aura_thirds_center_on_the_arms(july_wednesday):
    """The trio's hues center on the arms like every pointer (owner
    correction 2026-07-10): upright, yellow spans 8h-16h, red 16h-24h,
    blue 0h-8h. Probed at 14h (yellow), 18h (red) and 6h (blue), away
    from the diamonds (arms sit at 0/120/240 deg)."""
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="trio", solar_rotation=False,
        show_weekday=False, show_earth=False, show_moon=False,
    )
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    at_14h = image.pixelColor(234, 87)          # dial 30 deg, radius 0.6R
    assert at_14h.red() > at_14h.blue() + 30             # Faith yellow
    at_18h = image.pixelColor(288, 180)         # dial 90 deg
    assert at_18h.red() > at_18h.green() + 30            # Love red
    assert at_18h.red() > at_18h.blue() + 30
    at_6h = image.pixelColor(72, 180)           # dial 270 deg
    assert at_6h.blue() > at_6h.red() + 30               # Hope blue


def test_hover_rework_moon_and_earth_formats(july_wednesday):
    """Owner hover rework: raised ordinal suffixes, illumination to one
    decimal, the moonrise-moonset span and the season row (Belgrade,
    8 July 2026 = 189th day, 18th day of a 94-day summer)."""
    day, tick = july_wednesday
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    moon = compositor._moon_text()
    assert "Illumination 42.8%" in moon       # one decimal (owner spec)
    assert "of 29.53" in moon
    # 8 Jul 2026 is a SKIP day in Belgrade — the moon sets at 13:53 but
    # does not rise (rises again just after midnight on the 9th); the
    # hover shows the side that exists.
    assert "Sets 13:53" in moon
    earth = compositor._earth_text()
    assert "8<sup>th</sup> July 2026" in earth
    assert "189<sup>th</sup> Day - 28<sup>th</sup> Week" in earth
    assert "Summer 18<sup>th</sup> of 94 Days" in earth
    assert "Cancer (21<sup>st</sup> June - 21<sup>st</sup> July)" in earth


def test_upright_mode_disarms_the_rotation(july_wednesday):
    """With solar rotation OFF the Star/Aura/Umbra stand upright — the
    render differs from the solar one (Belgrade July tilts ~+14 deg) and
    the today-slot hover sits at the exact unrotated angle."""
    day, tick = july_wednesday
    solar = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    upright_skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    upright_compositor = Compositor(upright_skin, AssetCache())
    upright = upright_compositor.render_offscreen(360.0, 1.0, day, tick)
    assert solar != upright
    # Wednesday=mercury sits at exactly 180 deg when upright: hover at the
    # unrotated slot center must hit it (orbit 0.38 * 180 px below center).
    # Hover rework: the ACTIVE body leads with the date and carries its
    # LEFT-aligned article (base + the active combination's paragraph).
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = upright_compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert "Wednesday, 8<sup>th</sup> July 2026" in tip
    assert "align='left'" in tip
    assert "Mercury" in tip                    # the planets article text
    assert "align='center'" in tip           # hover text is centered (owner spec)


def _day_and_tick(latitude, longitude, tz_name):
    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    tz = ZoneInfo(tz_name)
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    day = build_day_context(
        now,
        astral.Observer(latitude=latitude, longitude=longitude),
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    return day, build_tick_state(now, day)


def test_climate_zones_name_the_events_and_seasons(app):
    """Owner decision: the south flips the seasonal event names (their
    Summer Solstice is the December one), the tropics use the neutral
    month names and read their WET/DRY halves instead of seasons."""
    sydney, tick = _day_and_tick(-33.8688, 151.2093, "Australia/Sydney")
    assert sydney.zone == "south"
    names = [name for _, name in sydney.season_events]
    assert "Winter Solstice" in names and "Summer Solstice" in names
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, sydney, tick)
    earth = compositor._earth_text()
    assert "Winter 18<sup>th</sup> of 94 Days" in earth   # July = their winter

    singapore, tick = _day_and_tick(1.3521, 103.8198, "Asia/Singapore")
    assert singapore.zone == "tropics"
    names = [name for _, name in singapore.season_events]
    assert "June Solstice" in names and "December Solstice" in names
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, singapore, tick)
    earth = compositor._earth_text()
    assert "Wet season 111<sup>th</sup> of 186 Days" in earth


def test_trio_arm_hover_carries_the_virtue_article(july_wednesday):
    """The Trinity arm hover: theme, third, pair — then the virtue's
    article (owner request): Faith's speaks of the vertical line."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="trio", solar_rotation=False,
            show_weekday=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    tip = compositor.tooltip_at(180.0, 72.0, 360.0)       # top arm = Faith
    assert "Faith" in tip and "08:00 - 16:00" in tip
    assert "Thursday" in tip and "Saturday" in tip
    assert "align='left'" in tip and "vertical line" in tip


def test_day_and_night_period_hovers(july_wednesday):
    """Hover rework 5 & 6: the sunlit arc answers with the day duration
    and both spans (sun + twilight-extended), the dark of the wheel
    with the night — probed upright at 14h (day) and just off midnight
    (night), away from arms, bodies and markers."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_weekday=False, show_earth=False, show_moon=False,
            show_pointer=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    at_day = compositor.tooltip_at(234.0, 87.0, 360.0)     # dial 30 deg = 14h
    assert "Day 15h" in at_day and "Sunrise" in at_day and "Dusk" in at_day
    at_night = compositor.tooltip_at(162.0, 285.0, 360.0)  # near the bottom
    assert "Night 8h" in at_night
    assert "Sunset" in at_night and "Dawn" in at_night


def test_arm_hover_only_inside_the_diamond(july_wednesday):
    """Owner bug report: the diamond hover must not swallow the wheel —
    BETWEEN the arms the Aura/Umbra day-night hover answers; the arm
    text appears only inside the drawn diamond polygon."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_weekday=False, show_earth=False, show_moon=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    on_arm = compositor.tooltip_at(180.0, 72.0, 360.0)     # top arm axis, 0.6R
    assert "Gemini" in on_arm                              # diamond answers
    # Dial 30 deg (between the 0 and 60 arms) at 0.7R: the gap — the
    # day hover answers there (14h is deep in the July daylight arc).
    between = compositor.tooltip_at(243.0, 70.9, 360.0)
    assert between is not None and "Day 15h" in between
    assert "Gemini" not in between and "Leo" not in between


def test_ghost_body_hover_shows_the_article_alone(july_wednesday):
    """Hover rework: ghost (non-current) bodies are hover targets too,
    showing their article WITHOUT the date line (owner spec) — probed on
    Jupiter's top slot on a Wednesday."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False), AssetCache()
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = upright.tooltip_at(180.0, 180.0 - orbit, 360.0)   # top slot = jupiter
    assert tip is not None and "align='left'" in tip
    assert "Jupiter" in tip                    # its planets article
    assert "July 2026" not in tip              # no date line on ghosts


# --- Arm hovers (owner spec) -----------------------------------------------------------


def test_hexa_arm_hover_names_its_two_signs(july_wednesday):
    """Each hexa diamond spans exactly TWO zodiac signs (the owner's
    proposed list had Aquarius doubled on the bottom arm — corrected:
    bottom = Sagittarius + Capricorn), one full line each: symbol,
    name, date span. Upright → no asterisk."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False), AssetCache()
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    top = upright.tooltip_at(180.0, 72.0, 360.0)          # top diamond, 0.6R up
    assert "Gemini" in top and "Cancer" in top and "*" not in top
    assert "<br/>" in top                                 # one sign per line
    assert "May" in top and "Jun" in top                  # each with its dates
    bottom = upright.tooltip_at(180.0, 288.0, 360.0)      # below mercury's slot
    assert "Sagittarius" in bottom and "Capricorn" in bottom
    assert "Nov" in bottom and "Dec" in bottom


def test_octa_arm_hovers_events_and_seasons(july_wednesday):
    """Octa cardinals give the exact event instant; diagonals describe
    their season with dates, duration and the middle date. Solar
    rotation ON adds the imprecision asterisk."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", solar_rotation=False
        ),
        AssetCache(),
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    cardinal = upright.tooltip_at(180.0, 72.0, 360.0)     # top arm
    assert "Summer Solstice" in cardinal
    assert "2026" in cardinal and ":" in cardinal         # exact date + minutes
    assert "*" not in cardinal
    assert "h " in cardinal and "min" in cardinal         # day length line
    diagonal = upright.tooltip_at(256.0, 104.0, 360.0)    # 45 deg arm, 0.6R
    assert "Summer" in diagonal and "Days)" in diagonal and "Heart" in diagonal
    assert "<sup>" in diagonal                            # raised ordinals
    solar = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa"), AssetCache()
    )
    solar.render_offscreen(360.0, 1.0, day, tick)
    rotation = day.star_rotation
    theta = math.radians(45.0 + rotation)
    tilted = solar.tooltip_at(
        180.0 + 108.0 * math.sin(theta), 180.0 - 108.0 * math.cos(theta), 360.0
    )
    assert tilted is not None and "*" in tilted


def test_chinese_slot_hover(july_wednesday):
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN,
            pointer="octa",
            solar_rotation=False,
            octa_slot="chinese_text",
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert "Fire Horse" in tip and "2026" in tip and "2027" in tip
    assert "<br/>" in tip                     # name / span on separate lines


def test_twilight_band_beats_the_arm_hover(july_wednesday):
    """Owner: dawn/dusk info must never be shadowed by the star-arm
    hovers — the band keeps priority inside the star region."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    # Mid-dusk angle (sunset 20:25 → dusk 21:02), probe at 0.6R.
    sunset_angle = (
        (day.sun.sunset.hour * 3600 + day.sun.sunset.minute * 60) / 86400 * 360 + 180
    ) % 360
    dusk_angle = (
        (day.sun.dusk.hour * 3600 + day.sun.dusk.minute * 60) / 86400 * 360 + 180
    ) % 360
    theta = math.radians((sunset_angle + dusk_angle) / 2)
    tip = compositor.tooltip_at(
        180.0 + 108.0 * math.sin(theta), 180.0 - 108.0 * math.cos(theta), 360.0
    )
    assert tip is not None and "Sunset" in tip and "Dusk" in tip


# --- Umbra ----------------------------------------------------------------------------


def test_umbra_forms_structure():
    """Sectioned forms (owner spec): fine 30 sections/16 shades (his
    measured art), coarse 24/13 — single lightest/darkest + mirror
    pairs; the gradient form has no sections at all."""
    assert constants.UMBRA_SECTION_COUNTS == {"fine": 30, "coarse": 24}
    for form, sections in constants.UMBRA_SECTION_COUNTS.items():
        shades = sections // 2 + 1
        assert 1 + 2 * (shades - 2) + 1 == sections, form
    assert "gradient" in constants.UMBRA_FORMS
    assert "gradient" not in constants.UMBRA_SECTION_COUNTS


def test_umbra_ladders_hit_the_owner_values():
    """full = endpoint-inclusive over 0..255 (16 shades -> step 17);
    half = bin centers of the middle half 64..192 (16 -> 188..68 step 8,
    every value + its mirror = 256)."""
    full16 = umbra_ladder(16, "full")
    assert full16 == tuple(255 - 17 * k for k in range(16))
    half16 = umbra_ladder(16, "half")
    assert half16 == tuple(188 - 8 * k for k in range(16))
    assert all(a + b == 256 for a, b in zip(half16, reversed(half16)))
    # Owner spec: light = the bright half (128-255), dark = the dark
    # half (0-127) — bin centers, exact step 8 like "half".
    light16 = umbra_ladder(16, "light")
    assert light16 == tuple(252 - 8 * k for k in range(16))
    assert light16[-1] == 132 and all(0 <= v <= 255 for v in light16)
    dark16 = umbra_ladder(16, "dark")
    assert dark16 == tuple(124 - 8 * k for k in range(16))
    assert dark16[-1] == 4
    full13 = umbra_ladder(13, "full")
    assert full13[0] == 255 and full13[-1] == 0 and full13[6] == 128
    half13 = umbra_ladder(13, "half")
    assert half13[0] == 187 and half13[-1] == 69 and half13[6] == 128
    for ladder in (full16, half16, full13, half13):
        assert list(ladder) == sorted(ladder, reverse=True)
        assert len(set(ladder)) == len(ladder)


def test_event_glow_is_visible_even_over_the_yellow_wedge(app):
    """Owner report: no glow on the summer solstice. The solstice Earth
    always sits in the bright yellow wedge — the halo must remain
    visible there (white core). A/B: the same moment with and without
    the event window must differ around the marker."""
    import dataclasses as dc

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    solstice_noon = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        solstice_noon,
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    glowing = build_tick_state(solstice_noon, day)
    assert glowing.season_event == "Summer Solstice"
    # Clear BOTH events: on this date the moon's first quarter is also
    # within its window and its halo would contaminate the comparison.
    quiet = dc.replace(glowing, season_event=None, moon_event=None)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    with_glow = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, glowing
    )
    without = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quiet
    )
    # Upright + solstice noon: the Earth rides at the dial top, orbit
    # 0.75R. Probe DIAGONALLY below-right of the marker: inside the 2x
    # halo, outside the disc, off the noon hand shafts on the vertical
    # and BELOW the marker's date-text line (which renders as wide tofu
    # boxes under the offscreen platform and would mask the comparison).
    # The white core lifts the blue channel over the blue-free yellow.
    marker_y = 270 - round(270 * defaults.DEFAULT_SKIN.year_marker.orbit_fraction)
    lit = with_glow.pixelColor(300, marker_y + 30)
    plain = without.pixelColor(300, marker_y + 30)
    assert lit.blue() - plain.blue() >= 8


def test_moon_event_glow_renders(app):
    """Owner report: the moon glow "doesn't work" — pin that the halo
    really draws at a principal instant (it only shows within ±6 h of
    one; his Time Travel likely landed outside a window)."""
    import dataclasses as dc

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    seasons = SeasonsRepository().year_anchors(2026)
    window = MoonPhaseRepository().moon_window(2026)
    reference = datetime(2026, 7, 7, 12, 0, tzinfo=tz)
    scout = build_day_context(reference, observer, seasons, window)
    instant, name = min(
        scout.moon_events, key=lambda event: abs(event[0] - reference)
    )
    local = instant.astimezone(tz)
    day = build_day_context(local, observer, seasons, window)
    glowing = build_tick_state(local, day)
    assert glowing.moon_event == name
    quiet = dc.replace(glowing, moon_event=None, season_event=None)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    with_glow = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, glowing
    )
    without = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quiet
    )
    # At the instant the moon sits exactly on its cycle angle; probe
    # 30 px above the marker center — inside the 2x halo, off the disc.
    moon_angle = math.radians(day.moon_fraction * 360.0)
    orbit = 270 * defaults.DEFAULT_SKIN.year_marker.moon_orbit_fraction
    moon_x = 270 + orbit * math.sin(moon_angle)
    moon_y = 270 - orbit * math.cos(moon_angle)
    lit = with_glow.pixelColor(round(moon_x), round(moon_y) - 30)
    plain = without.pixelColor(round(moon_x), round(moon_y) - 30)
    assert (
        lit.red() - plain.red() >= 8
        or lit.green() - plain.green() >= 8
        or lit.blue() - plain.blue() >= 8
    )


def test_half_contrast_renders_a_gentler_night(july_wednesday):
    """The bottom of the dial (solar midnight, no hue overlay in July) is
    near-black on full contrast and clearly lifted on half."""
    day, tick = july_wednesday
    full = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    half_skin = dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="half")
    half = Compositor(half_skin, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    # 90 px below center: inside the darkest sections (plus the star's
    # slight solar rotation), away from body slots and diamond borders.
    full_pixel = full.pixelColor(180, 270)
    half_pixel = half.pixelColor(180, 270)
    assert full_pixel.alpha() > 200 and half_pixel.alpha() > 200
    assert full_pixel.red() < 50
    assert half_pixel.red() >= 55
    # Light contrast lifts the night far higher (window 128-255); dark
    # keeps it near-black (window 0-127).
    light = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="light"),
        AssetCache(),
    ).render_offscreen(360.0, 1.0, day, tick)
    dark = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="dark"),
        AssetCache(),
    ).render_offscreen(360.0, 1.0, day, tick)
    assert light.pixelColor(180, 270).red() >= 120
    assert dark.pixelColor(180, 270).red() < 50


@pytest.mark.parametrize("form", ["coarse", "gradient"])
def test_umbra_forms_render(july_wednesday, form):
    day, tick = july_wednesday
    upright = dataclasses.replace(
        defaults.DEFAULT_SKIN, umbra_form=form, solar_rotation=False
    )
    image = Compositor(upright, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    assert image.pixelColor(180, 8).alpha() > 200
    if form == "gradient":
        # Upright: lightest straight up, darkest straight down; the
        # sweep must be mirror-symmetric. Probes at 0.62R: top/bottom on
        # the vertical, the mirror pair at dial angles 150/210 deg —
        # night side in July, so pure Umbra with no Aura wedge over it.
        top = image.pixelColor(180, 68).red()
        bottom = image.pixelColor(180, 292).red()
        night_right = image.pixelColor(236, 277).red()
        night_left = image.pixelColor(124, 277).red()
        assert bottom < 40 < top                 # dark bottom, light top...
        assert abs(night_left - night_right) <= 2    # ...mirrored sides
