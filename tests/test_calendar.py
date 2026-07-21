"""The Calendar pointer (owner 2026-07-16, CANON §The Dozen): the two
wheels' palettes, the Almanac's own real-calendar year mapping (one tick
≈ one day), the Earth day-arrow, the shichen/year lighting, the pinned
slot layout, and the no-solar-rotation of the wedges."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
import math
from datetime import date, datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import constants, defaults
from core.clock_state import build_day_context, build_tick_state
from core.year_wheel import almanac_marker_angle, almanac_month_index
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import (
    calendar_day_arrow,
    calendar_lit_index,
    calendar_mount_angle,
    calendar_mount_current_index,
    calendar_mount_entries,
    calendar_mount_wheel,
    calendar_wedge_bounds,
    calendar_wheel,
    chinese_mount_dimmed_index,
    dial_point,
    slot_layout,
    slot_seat_rotation,
    weekday_classic_slot,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _day_tick(app, when):
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = when.replace(tzinfo=tz)
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def _calendar_skin(**kw):
    return dataclasses.replace(defaults.DEFAULT_SKIN, pointer="calendar", **kw)


# --- Palettes --------------------------------------------------------------------


def test_calendar_palettes_pin_the_two_wheels():
    """The twelve hues of each wheel, clockwise from the top wedge —
    Zodiac (paint) opens on Cancer, Almanac (light) on June."""
    assert defaults.PALETTE_PRESETS[("calendar", "paint")] == (
        "#40FF00", "#BFFF00", "#FFBF00", "#FF4000", "#FF0040", "#FF00C0",
        "#BF00FF", "#4000FF", "#0040FF", "#00BFFF", "#00FFBF", "#00FF40",
    )
    assert defaults.PALETTE_PRESETS[("calendar", "light")] == (
        "#00FF00", "#80FF00", "#FFFF00", "#FFBF00", "#FF0000", "#FF0080",
        "#FF00FF", "#8000FF", "#0000FF", "#0080FF", "#00FFFF", "#00FF80",
    )
    # Both wheels carry exactly twelve hues (the palette-length invariant).
    for style in ("paint", "light"):
        assert len(defaults.PALETTE_PRESETS[("calendar", style)]) == 12


def test_calendar_wheel_follows_the_palette_style():
    assert calendar_wheel(_calendar_skin(palette_style="paint")) == "zodiac"
    assert calendar_wheel(_calendar_skin(palette_style="light")) == "almanac"


def test_wedge_bounds_place_the_top_wedge():
    """Zodiac boundaries sit ON the axes (top wedge starts at 0°);
    Almanac wedges are CENTERED on them (top wedge centered on 0°)."""
    zodiac = calendar_wedge_bounds("zodiac")
    assert zodiac[0] == (0.0, 30.0)
    assert len(zodiac) == 12 and zodiac[-1] == (330.0, 360.0)
    almanac = calendar_wedge_bounds("almanac")
    assert almanac[0] == (-15.0, 15.0)          # centered on the top
    assert almanac[1] == (15.0, 45.0)


# --- The Almanac's own year mapping ----------------------------------------------


def test_almanac_month_index_orders_from_june():
    assert almanac_month_index(6) == 0          # June at the top
    assert almanac_month_index(12) == 6         # December
    assert almanac_month_index(1) == 7          # January
    assert almanac_month_index(5) == 11         # May, the last wedge


def test_january_first_sits_on_the_01h_line():
    """January 1 lands exactly on the 01:00h line = dial 195°
    (owner spec: the 1st of each month on its wedge-start line)."""
    assert almanac_marker_angle(date(2026, 1, 1)) == pytest.approx(195.0)


def test_june_first_sits_on_the_11h_line():
    """June 1 lands on the 11:00h line = 15° before the top (345°)."""
    assert almanac_marker_angle(date(2026, 6, 1)) == pytest.approx(345.0)


def test_summer_solstice_lands_a_few_ticks_past_the_top():
    """The June 21 solstice sits ~5-6 ticks (≈ days) clockwise past the
    top — the natural consequence of anchoring June 1 to the 11h line
    (owner spec: not a concession)."""
    angle = almanac_marker_angle(date(2026, 6, 21))
    assert 4.0 <= angle <= 7.0                   # ~5-6°, one tick per day


def test_february_day_tempo_uses_the_real_calendar():
    """February covers its 30° in 28 (or 29) real days — day D sits
    (D-1)/days_in_month into the wedge, so 2028's leap February runs a
    hair slower than 2026's."""
    common = almanac_marker_angle(date(2026, 2, 15))
    leap = almanac_marker_angle(date(2028, 2, 15))
    # Feb is wedge index 8 -> start 8*30-15 = 225°.
    assert common == pytest.approx(225.0 + 14 / 28 * 30.0)
    assert leap == pytest.approx(225.0 + 14 / 29 * 30.0)
    assert leap < common                         # slower tempo, earlier tick


# --- The Earth day-arrow ---------------------------------------------------------


def test_day_arrow_points_outward_at_the_marker_tick():
    """The arrow's tip lands at the marker's exact angle on the ring-tick
    radius; its base sits inward (pointing OUT)."""
    radius = 180.0
    angle = almanac_marker_angle(date(2026, 7, 16))
    arrow = calendar_day_arrow(angle, radius)
    tip = arrow[0]
    expected = dial_point(angle, radius * defaults.CALENDAR_ARROW_TIP_FRACTION)
    assert tip.x() == pytest.approx(expected.x())
    assert tip.y() == pytest.approx(expected.y())
    tip_r = math.hypot(tip.x(), tip.y())
    base_r = math.hypot(arrow[1].x(), arrow[1].y())
    assert tip_r > base_r                        # tip outward, base inward


# --- Lighting --------------------------------------------------------------------


def test_shichen_horse_wedge_lights_at_noon(app):
    """"hour" lighting at 12:15 lights the noon double-hour — on the
    Almanac that is the Horse wedge (index 0, the top), on the Zodiac the
    12h-14h wedge the hour hand sits in (index 0)."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    almanac = _calendar_skin(palette_style="light", calendar_lighting="hour")
    assert calendar_lit_index(almanac, "hour", tick.hour_angle, day) == 0
    # Index 0 on the Almanac is the Horse (the noon watch).
    assert constants.CHINESE_ANIMALS[(0 - 6) % 12] == "Horse"
    zodiac = _calendar_skin(palette_style="paint", calendar_lighting="hour")
    assert calendar_lit_index(zodiac, "hour", tick.hour_angle, day) == 0


def test_year_lighting_picks_the_month_and_sign(app):
    """"year" lighting: the Almanac lights the current MONTH's wedge, the
    Zodiac the current SIGN's — July 2026 = wedge 1 (July) / Cancer
    (index 0, sign Cancer runs to ~22 July)."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    almanac = _calendar_skin(palette_style="light", calendar_lighting="year")
    assert calendar_lit_index(almanac, "year", tick.hour_angle, day) == 1
    zodiac = _calendar_skin(palette_style="paint", calendar_lighting="year")
    index = calendar_lit_index(zodiac, "year", tick.hour_angle, day)
    names = [name for name, _ in constants.ZODIAC_SIGNS]
    assert names[index] == day.zodiac_name


def test_lighting_mode_switch_changes_the_lit_wedge(app):
    """The two modes really select different wedges away from noon:
    mid-afternoon the hour wedge is not the month wedge."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 16, 30))
    skin = _calendar_skin(palette_style="light")
    by_hour = calendar_lit_index(skin, "hour", tick.hour_angle, day)
    by_year = calendar_lit_index(skin, "year", tick.hour_angle, day)
    assert by_hour != by_year


# --- Slots & rotation ------------------------------------------------------------


def test_calendar_uses_the_pinned_slot_layout():
    """No weekday model: the pinned 24h slot alone, exactly as Aurora /
    the pointer-off case — the weekday mode sits in a seat, never the
    classic unit."""
    skin = _calendar_skin()
    assert slot_layout(skin) == {1: constants.SOUTH_SLOT_ANGLE}
    assert weekday_classic_slot(skin) is None
    assert slot_layout(_calendar_skin(show_octa_slot=True)) == {
        1: constants.AURORA_DUAL_WEEKDAY_ANGLE,
        2: constants.AURORA_DUAL_SLOT_ANGLE,
    }


def test_calendar_wedges_never_rotate_with_the_sun():
    """The wedges are calendar-fixed (owner spec): the slot seats do not
    ride the solar offset even with solar_rotation on, exactly like the
    pinned layouts."""
    assert slot_seat_rotation(_calendar_skin(solar_rotation=True), 10.76) == 0.0


def test_calendar_renders_and_the_hover_reads_the_wheel(app):
    """Both wheels paint without a crash, and a wedge hover answers: the
    Almanac names the month + double-hour animal, the Zodiac the sign +
    dates."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    for style in ("paint", "light"):
        skin = _calendar_skin(palette_style=style)
        comp = Compositor(skin, AssetCache())
        image = comp.render_offscreen(360.0, 1.0, day, tick)
        assert image.pixelColor(180, 8).alpha() > 200        # ring painted
        assert image.pixelColor(180, 120).alpha() > 0        # a wedge painted
    # Almanac wedge hover at the top (June/July border region): probe the
    # top wedge center — the month + animal answer.
    almanac = Compositor(_calendar_skin(palette_style="light"), AssetCache())
    almanac.render_offscreen(360.0, 1.0, day, tick)
    top = almanac.tooltip_at(180.0, 120.0, 360.0)            # inside the top wedge
    assert top is not None and "June" in top and "Horse" in top
    # The wedge WEARS OUR ART (owner 2026-07-16, ROADMAP queue #7): the
    # Chinese COLORED medallion (a real image tag), never a plain-text
    # stand-in — the src is the scaled raster-cache copy of the colored
    # animal medallion.
    assert "<img" in top and "raster_cache" in top
    # Zodiac wedge hover at the top: Cancer with its dates + the sign's
    # COLORED LOGO art.
    zodiac = Compositor(_calendar_skin(palette_style="paint"), AssetCache())
    zodiac.render_offscreen(360.0, 1.0, day, tick)
    top_sign = zodiac.tooltip_at(200.0, 120.0, 360.0)        # top-right wedge
    assert top_sign is not None and (
        "Cancer" in top_sign or "Leo" in top_sign
    )
    assert "<img" in top_sign and "raster_cache" in top_sign


def test_spacebar_encyclopedia_target_maps_the_hovered_wheel(app):
    """The Spacebar jump (owner 2026-07-16, ROADMAP queue #8): the
    ONE element→topic mapping opens the hovered Calendar wedge's page —
    the Almanac's Chinese animal, the Zodiac's sign — indexing the
    topic's own entry order. Works with the legend OFF (geometry, not
    tooltip text)."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    almanac = Compositor(
        _calendar_skin(palette_style="light", legend=False), AssetCache()
    )
    almanac.render_offscreen(360.0, 1.0, day, tick)
    assert almanac.tooltip_at(180.0, 120.0, 360.0) is None     # legend off
    # The top Almanac wedge is the Horse double-hour → Chinese entry 6.
    assert almanac.encyclopedia_target(180.0, 120.0, 360.0) == ("chinese", 6)
    zodiac = Compositor(_calendar_skin(palette_style="paint"), AssetCache())
    zodiac.render_offscreen(360.0, 1.0, day, tick)
    topic, index = zodiac.encyclopedia_target(200.0, 120.0, 360.0)
    assert topic == "astrology" and 0 <= index < 12
    # Off any target (dial center) there is nothing to open.
    assert zodiac.encyclopedia_target(180.0, 180.0, 360.0) is None


def test_calendar_lit_index_none_off_the_pointer(app):
    """The compositor computes no lit wedge for the other pointers (the
    composite key stays clean)."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.set_day(day)
    comp._last_tick = tick
    assert comp._calendar_lit(tick) is None


# --- The 12-SET MOUNT (DESIGN ZODIAC law, R9a round 2026-07-21) ------------------
# "Zodiac i sve što ima 12 TREBA da bude moguće da se AKTIVIRA na CALENDAR
# POINTER (TO MU JE DEFAULT)": twelve marks, one per wedge, at 60-70% of
# the dial radius, independent of which wheel paints the background.


def test_mount_wheel_is_independent_of_the_active_background_wheel():
    """Zodiac marks always ride the ZODIAC wheel's own cardinal-START
    wedges (sign i's wedge IS its own 30-deg arc — the honest alignment
    already used for the wedge-lit law, no separate approximation);
    months always ride the ALMANAC wheel's cardinal-CENTERED wedges."""
    assert calendar_mount_wheel("zodiac") == "zodiac"
    assert calendar_mount_wheel("months") == "almanac"
    assert calendar_mount_angle("zodiac", 0) == pytest.approx(15.0)   # Cancer wedge center
    assert calendar_mount_angle("months", 0) == pytest.approx(0.0)    # June, on the axis
    # Twelve marks, evenly spaced 30 deg apart, on EITHER geometry.
    for mount in ("zodiac", "months"):
        angles = [calendar_mount_angle(mount, i) for i in range(12)]
        assert len(set(angles)) == 12
        gaps = {
            round((angles[i + 1] - angles[i]) % 360.0, 6) for i in range(11)
        }
        assert gaps == {30.0}


def test_zodiac_mount_entries_carry_the_real_committed_badges():
    """The zodiac mount reads the SAME astrology COLORED badges the
    background wedge hover already shows (Rule #5) — real art, shipped
    today, never a gap."""
    entries = calendar_mount_entries("zodiac")
    assert len(entries) == 12
    assert [name for name, _art in entries] == [
        name for name, _symbol in constants.ZODIAC_SIGNS
    ]
    assert all(art is not None and art.exists() for _name, art in entries)


def test_months_mount_entries_are_graceful_absent_and_wedge_aligned():
    """The Slavic months mount in the Almanac's own June-leads order
    (index 0 = Lipanj/June, matching almanac_month_index) with NO art
    yet (owner R7b: the prompt sheet has not landed) — the name is
    always present so the caller never draws a gap."""
    entries = calendar_mount_entries("months")
    assert len(entries) == 12
    assert entries[0][0] == "Lipanj"                 # June leads
    assert entries[almanac_month_index(1)][0] == "Siječanj"   # January
    assert all(name for name, _art in entries)       # every wedge named
    assert all(art is None for _name, art in entries)         # no plates yet


def test_mount_current_index_matches_todays_sign_and_month_no_hemisphere_flip(app):
    """The emphasis mark is the SAME lookup calendar_lit_index's "year"
    branches use (Rule #5) — never hemisphere-mirrored, since the mark
    sits on its own fixed wedge identity (unlike the Earth marker's
    orbit)."""
    day, _tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    names = [name for name, _symbol in constants.ZODIAC_SIGNS]
    assert calendar_mount_current_index("zodiac", day) == names.index(day.zodiac_name)
    assert calendar_mount_current_index("months", day) == almanac_month_index(
        day.local_date.month
    )


def test_mount_lit_delta_raises_the_current_mark_to_full_opacity():
    """"the mark can inherit that brightness" (owner spec) — the SAME
    base+delta shape the wedges use, sized so the current mark reaches
    (but never exceeds) full opacity."""
    assert 0.0 < defaults.CALENDAR_MOUNT_ALPHA < 1.0
    assert defaults.CALENDAR_MOUNT_ALPHA + defaults.CALENDAR_MOUNT_LIT_DELTA == (
        pytest.approx(1.0)
    )


def test_calendar_mount_renders_and_a_mark_hover_outranks_the_wedge(app):
    """The mount paints without a crash and a mark's own small hit
    target wins over the broader whole-wedge hover beneath it: zodiac
    speaks sign + dates + its colored badge, months speaks the Croatian
    name + English gloss (graceful-absent art, never a broken image)."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    radius = 180.0

    def px(mount: str, index: int) -> tuple[float, float]:
        point = dial_point(
            calendar_mount_angle(mount, index),
            radius * defaults.CALENDAR_MOUNT_RADIUS_FRACTION,
        )
        return radius + point.x(), radius + point.y()

    zodiac = Compositor(
        _calendar_skin(palette_style="paint", calendar_mount="zodiac"),
        AssetCache(),
    )
    zodiac.render_offscreen(360.0, 1.0, day, tick)
    x, y = px("zodiac", 0)                       # Cancer's own mark
    text = zodiac.tooltip_at(x, y, 360.0)
    assert text is not None and "Cancer" in text and "<img" in text

    months = Compositor(
        _calendar_skin(palette_style="light", calendar_mount="months"),
        AssetCache(),
    )
    months.render_offscreen(360.0, 1.0, day, tick)
    x2, y2 = px("months", 0)                     # Lipanj's own mark
    text2 = months.tooltip_at(x2, y2, 360.0)
    assert text2 is not None and "Lipanj" in text2 and "Linden" in text2
    assert "<img" not in text2                   # graceful-absent: no broken image


def test_calendar_mount_off_speaks_no_mark_hover(app):
    """Off leaves the position to the broader wedge hover instead — the
    mark-specific hit test is simply absent, never a crash."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    skin = _calendar_skin(calendar_mount="off")
    comp = Compositor(skin, AssetCache())
    comp.set_day(day)
    comp._last_tick = tick
    point = dial_point(15.0, 180.0 * defaults.CALENDAR_MOUNT_RADIUS_FRACTION)
    assert comp._calendar_mount_tooltip(point, 180.0) is None


def test_calendar_mount_modes_and_default():
    assert constants.CALENDAR_MOUNT_MODES == ("off", "zodiac", "months", "chinese")
    assert defaults.DEFAULT_SKIN.calendar_mount in constants.CALENDAR_MOUNT_MODES


# --- The Chinese MONTHLY-animal mount (owner R12, Blue Moon round) --------------


def test_chinese_mount_wheel_and_entries_are_gregorian_fixed_with_real_art():
    """The Chinese mount (owner R12: "Mount Chinese zodiac") rides the
    SAME Gregorian-fixed Almanac geometry as the months mount, keyed by
    `constants.CHINESE_MONTH_BRANCH_ANIMALS` — real, committed COLORED
    badges (Rule #5), never a gap. June leads with the Horse (the
    branch that begins ~Jun 6), December with the Rat (the branch that
    holds the winter solstice — core.blue_moon.chinese_leap_month reads
    the SAME fact)."""
    assert calendar_mount_wheel("chinese") == "almanac"
    entries = calendar_mount_entries("chinese")
    assert len(entries) == 12
    assert entries[0][0] == "Horse"                      # June
    assert entries[almanac_month_index(12)][0] == "Rat"   # December
    assert entries[almanac_month_index(2)][0] == "Tiger"  # February
    assert all(art is not None and art.exists() for _name, art in entries)


def test_chinese_mount_current_index_matches_todays_month(app):
    day, _tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    assert calendar_mount_current_index("chinese", day) == almanac_month_index(7)


def test_chinese_mount_dims_the_doubled_months_animal_during_a_leap_month(app):
    """THE CAT'S DIMMING LAW (owner spec, item 5): while a Chinese leap
    month holds the center, the mount mark of the DOUBLED month's own
    animal — never the current-month mark — dims below its resting
    alpha. 2025 is a real leap-6th-month year (Jul 25 - Aug 22): the
    doubled lunar month is the 6th, whose branch animal is the Goat
    (jianyin numbering: L1 Tiger .. L6 Goat .. L11 Rat .. L12 Ox), whose
    Gregorian mount seat is July."""
    from core.blue_moon import chinese_leap_month
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    anchors = SeasonsRepository().year_anchors(2025)
    window = MoonPhaseRepository().moon_window(2025)
    leap = chinese_leap_month(anchors, window)
    assert leap is not None and leap.number == 6

    inside = _day_tick(app, datetime(2025, 8, 1, 12, 0))[0]
    assert inside.chinese_leap_month_number == 6
    dimmed = chinese_mount_dimmed_index(inside)
    assert dimmed == almanac_month_index(7)                # the Goat's own July seat

    outside = _day_tick(app, datetime(2025, 3, 1, 12, 0))[0]
    assert outside.chinese_leap_month_number is None
    assert chinese_mount_dimmed_index(outside) is None


def test_chinese_mount_renders_and_hover_names_the_animal(app):
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    radius = 180.0
    chinese = Compositor(
        _calendar_skin(palette_style="light", calendar_mount="chinese"),
        AssetCache(),
    )
    chinese.render_offscreen(360.0, 1.0, day, tick)
    point = dial_point(
        calendar_mount_angle("chinese", 0), radius * defaults.CALENDAR_MOUNT_RADIUS_FRACTION
    )
    text = chinese.tooltip_at(radius + point.x(), radius + point.y(), 360.0)
    assert text is not None and "Horse" in text and "<img" in text
    assert "June" in text                     # "animal + its month" (owner spec)
