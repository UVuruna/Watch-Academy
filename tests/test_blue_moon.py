"""THE BLUE MOON LAW (owner-sealed 2026-07-22, CORRECTED 2026-07-2X): the
13th member of every 12-set. Pins `thirteen_moon_year` against published
full-moon counts, each 13th's own window (boundary days both sides), The
Cat's REAL lunisolar leap month against two independently verified
years, the DayContext wiring (a plain fact set, no precedence), the
graceful-absent contract for Sol/Modrenik, and — the owner's correction —
`render.layers.active_thirteenth`'s FOUR INDEPENDENT MODE gate: a 13th
shows ONLY on the Calendar pointer, in the ONE mode that owns it, NEVER
on any other pointer. Purity (no Qt, no wall clock) is covered
generically by tests/test_purity.py's core/*.py glob — not re-pinned
here.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from app.controller import apply_display_settings
from app.settings_store import Settings, replace
from config import constants, defaults, paths
from core.blue_moon import (
    ChineseLeapMonth,
    chinese_leap_month,
    modrenik_window,
    ophiuchus_window,
    sol_window,
    thirteen_moon_year,
    thirteenth_candidates,
)
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import active_thirteenth, center_seat_body_key, thirteenth_plate


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _day_tick(when: datetime):
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = when.replace(tzinfo=tz)
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def _calendar_skin(**kw):
    return dataclasses.replace(defaults.DEFAULT_SKIN, pointer="calendar", **kw)


# --- 1. thirteen_moon_year: the shared trigger --------------------------------


def test_thirteen_moon_year_matches_published_full_moon_counts():
    """Golden years against the bundled ephemeris: 2020 (the Halloween
    blue moon) and 2023 (the Aug 30/31 blue moon) both publicly carried
    13 Full Moons; 2019, 2021 and 2025 the ordinary 12."""
    mr = MoonPhaseRepository()
    golden = {
        2019: False, 2020: True, 2021: False, 2023: True,
        2025: False, 2026: True,
    }
    for year, expected in golden.items():
        assert thirteen_moon_year(year, mr.moon_window(year)) == expected, year


def test_thirteen_moon_year_never_anything_but_twelve_or_thirteen():
    """365.24 / 29.53 = 12.37 cycles/year bounds the count to 12 or 13,
    never fewer or more — a real invariant of the two periods, checked
    directly against the bundled data across twenty consecutive years."""
    mr = MoonPhaseRepository()
    for year in range(2015, 2035):
        window = mr.moon_window(year)
        count = sum(
            1 for instant, fraction in window.events
            if fraction == 0.5 and instant.year == year
        )
        assert count in (12, 13), year


# --- 2. Each solar-triggered 13th's own window --------------------------------


def test_ophiuchus_window_bounds():
    assert ophiuchus_window(2026) == (date(2026, 11, 29), date(2026, 12, 17))


def test_sol_window_bounds_span_four_weeks():
    lo, hi = sol_window(2026)
    assert (lo, hi) == (date(2026, 6, 18), date(2026, 7, 15))
    assert (hi - lo).days + 1 == 28              # Sol's own historical month length


def test_modrenik_window_is_computed_from_the_real_solstice_not_a_fixed_date():
    anchors = SeasonsRepository().year_anchors(2026)
    solstice = anchors.instants[4]
    lo, hi = modrenik_window(solstice)
    assert lo == solstice.date() - timedelta(days=14)
    assert hi == solstice.date() + timedelta(days=14)
    # 14 before + the solstice day itself + 14 after = 29 days total —
    # ONE more than Sol's own 28 (Sol has no "center day" of its own);
    # 29 is instead a synodic lunar month's own length, fittingly for
    # the MOON's thirteenth.
    assert (hi - lo).days + 1 == 29


# --- 3. thirteenth_candidates: boundary days, both sides -----------------------


@pytest.mark.parametrize(
    "window_fn, key", [(ophiuchus_window, "ophiuchus"), (sol_window, "sol")],
)
def test_fixed_window_boundaries_are_inclusive(window_fn, key):
    """2026 is a blue-moon year: day before OFF, first day ON, last day
    ON, day after OFF."""
    mr, sr = MoonPhaseRepository(), SeasonsRepository()
    window, anchors = mr.moon_window(2026), sr.year_anchors(2026)
    leap = chinese_leap_month(anchors, window)
    lo, hi = window_fn(2026)
    assert key not in thirteenth_candidates(lo - timedelta(days=1), window, anchors, leap)
    assert key in thirteenth_candidates(lo, window, anchors, leap)
    assert key in thirteenth_candidates(hi, window, anchors, leap)
    assert key not in thirteenth_candidates(hi + timedelta(days=1), window, anchors, leap)


def test_modrenik_window_boundaries_are_inclusive_and_cross_new_year():
    """Modrenik's window crosses the New Year in a blue-moon December
    (2026's solstice window runs into Jan 2027) — checked on its
    UNAMBIGUOUS tail, past Ophiuchus's own Dec 17 close, so no other
    candidate is in play here (the overlapping HEAD is covered by
    test_ophiuchus_and_modrenik_windows_can_both_be_true_facts)."""
    mr, sr = MoonPhaseRepository(), SeasonsRepository()
    window26, anchors26 = mr.moon_window(2026), sr.year_anchors(2026)
    leap26 = chinese_leap_month(anchors26, window26)
    lo, hi = modrenik_window(anchors26.instants[4])
    assert lo.year == 2026 and hi.year == 2027            # crosses the New Year
    unambiguous = date(2026, 12, 19)                      # past Ophiuchus's Dec 17
    assert lo <= unambiguous <= hi
    assert "modrenik" in thirteenth_candidates(unambiguous, window26, anchors26, leap26)
    # `hi` falls in 2027 — read through 2027's own YearAnchors/MoonWindow
    # (instants[0] is the SAME December solstice; MoonPhaseRepository
    # always brackets year-1, so 2026's Full Moons are still present).
    window27, anchors27 = mr.moon_window(2027), sr.year_anchors(2027)
    leap27 = chinese_leap_month(anchors27, window27)
    assert "modrenik" in thirteenth_candidates(hi, window27, anchors27, leap27)
    assert "modrenik" not in thirteenth_candidates(
        hi + timedelta(days=1), window27, anchors27, leap27
    )


def test_window_alone_is_not_enough_without_the_trigger():
    """A date inside Sol's calendar window in a NON-blue-moon year must
    not trigger — 2025 fails thirteen_moon_year even though it is
    itself a Chinese-leap-month year (the two triggers are genuinely
    independent, core.blue_moon's own design decision)."""
    mr, sr = MoonPhaseRepository(), SeasonsRepository()
    window, anchors = mr.moon_window(2025), sr.year_anchors(2025)
    assert not thirteen_moon_year(2025, window)
    leap = chinese_leap_month(anchors, window)
    assert leap is not None and leap.number == 6          # 2025 IS a Cat year
    # Jul 1 sits inside Sol's Jun18-Jul15 span and safely before the
    # Cat's own Jul25-Aug22 leap window.
    assert thirteenth_candidates(date(2025, 7, 1), window, anchors, leap) == frozenset()


def test_no_thirteenth_candidate_on_an_ordinary_date():
    mr, sr = MoonPhaseRepository(), SeasonsRepository()
    window, anchors = mr.moon_window(2026), sr.year_anchors(2026)
    leap = chinese_leap_month(anchors, window)
    assert thirteenth_candidates(date(2026, 3, 15), window, anchors, leap) == frozenset()


def test_ophiuchus_and_modrenik_windows_can_both_be_true_facts():
    """The one genuine window overlap (owner-documented): both ride
    `thirteen_moon_year` and share the Dec 7-17 band of a blue-moon
    December. UNLIKE R12, core.blue_moon picks no winner here — both are
    reported as true FACTS; resolving to ONE mode-owned member is
    render.layers.active_thirteenth's job, from the ACTIVE skin, never a
    date-only tiebreak (see test_mount_outranks_the_wheel_when_both_claim
    below)."""
    mr, sr = MoonPhaseRepository(), SeasonsRepository()
    window, anchors = mr.moon_window(2026), sr.year_anchors(2026)
    leap = chinese_leap_month(anchors, window)
    assert thirteen_moon_year(2026, window)
    o_lo, o_hi = ophiuchus_window(2026)
    m_lo, m_hi = modrenik_window(anchors.instants[4])
    assert m_lo <= o_hi < m_hi                             # the windows truly overlap
    candidates = thirteenth_candidates(date(2026, 12, 13), window, anchors, leap)
    assert candidates == frozenset({"ophiuchus", "modrenik"})


# --- 4. THE CAT: the real lunisolar leap month --------------------------------


def test_chinese_leap_month_matches_two_independently_verified_years():
    """2023 leap 2nd month (Mar 22 - Apr 19) and 2025 leap 6th month
    (Jul 25 - Aug 22) — both independently confirmed against published
    Chinese-calendar references, reproduced exactly (day for day, not
    just the month number) against the bundled ephemeris."""
    sr, mr = SeasonsRepository(), MoonPhaseRepository()
    golden = {
        2023: ChineseLeapMonth(2, date(2023, 3, 22), date(2023, 4, 19)),
        2025: ChineseLeapMonth(6, date(2025, 7, 25), date(2025, 8, 22)),
    }
    for year, expected in golden.items():
        leap = chinese_leap_month(sr.year_anchors(year), mr.moon_window(year))
        assert leap == expected, year


def test_chinese_leap_month_none_in_an_ordinary_sui():
    sr, mr = SeasonsRepository(), MoonPhaseRepository()
    assert chinese_leap_month(sr.year_anchors(2026), mr.moon_window(2026)) is None


def test_cat_boundary_days_are_inclusive():
    sr, mr = SeasonsRepository(), MoonPhaseRepository()
    anchors, window = sr.year_anchors(2025), mr.moon_window(2025)
    leap = chinese_leap_month(anchors, window)
    before = thirteenth_candidates(leap.start - timedelta(days=1), window, anchors, leap)
    assert "chinese" not in before
    assert "chinese" in thirteenth_candidates(leap.start, window, anchors, leap)
    assert "chinese" in thirteenth_candidates(leap.end, window, anchors, leap)
    after = thirteenth_candidates(leap.end + timedelta(days=1), window, anchors, leap)
    assert "chinese" not in after


# --- 5. DayContext wiring (computed once a day, never per-minute) -------------


def test_day_context_carries_the_candidate_fact_set():
    sol_day, _tick = _day_tick(datetime(2026, 7, 8, 12, 0))   # inside Sol's window
    assert sol_day.thirteenth_candidates == frozenset({"sol"})
    assert sol_day.chinese_leap_month_number is None

    cat_day, _tick = _day_tick(datetime(2025, 8, 1, 12, 0))   # inside the Cat's window
    assert cat_day.thirteenth_candidates == frozenset({"chinese"})
    assert cat_day.chinese_leap_month_number == 6

    plain_day, _tick = _day_tick(datetime(2026, 3, 15, 12, 0))
    assert plain_day.thirteenth_candidates == frozenset()
    assert plain_day.chinese_leap_month_number is None


# --- 6. The registry + graceful-absent art ------------------------------------


def test_thirteenths_registry_is_exhaustive():
    assert set(constants.THIRTEENTHS) == {"ophiuchus", "sol", "modrenik", "chinese"}
    for _name, family, article in constants.THIRTEENTHS.values():
        assert family in ("ninths", "months")
        assert article


def test_ophiuchus_and_cat_resolve_real_committed_art():
    """The zodiac-only 13ths already shipped (owner R7b/R8d rounds) —
    thirteenth_plate must resolve real art, never fall back to
    name-only."""
    name, asset = thirteenth_plate("ophiuchus")
    assert name == "Ophiuchus" and asset is not None and asset.exists()
    name, asset = thirteenth_plate("chinese")
    assert name == "The Cat" and asset is not None and asset.exists()


def test_sol_and_modrenik_are_graceful_absent():
    """Wired ahead of the owner's prompt sheet (item 3/4 contract): the
    name resolves, the plate does not exist yet, and the sourceless
    MONTHS_ART_DIR path passes through paths.art_file untouched —
    exactly like the twelve real Slavic months (test_months.py)."""
    for key, expected in (("sol", "Sol"), ("modrenik", "Modrenik")):
        name, asset = thirteenth_plate(key)
        assert name == expected
        assert asset is None
        plate = defaults.MONTHS_ART_DIR / f"{expected}.png"
        assert paths.art_file(plate) == plate
        assert not plate.exists()


# --- 7. THE CORRECTED LAW: a 13th shows ONLY on the Calendar pointer ----------


def test_no_thirteenth_ever_off_the_calendar_pointer(app):
    """THE OWNER'S CORRECTION (sealed): R12 wrongly showed the 13th on
    ANY pointer carrying a classic/center weekday seat — its OWN
    screenshot caught Ophiuchus on the hexa pointer with the Greek
    theme. A 13th now NEVER shows off the Calendar pointer: the ordinary
    Sunday dual/Ninth law reigns untouched, even deep inside Ophiuchus's
    own window, on the exact reproduction of that bug."""
    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(
            Settings(), weekday_theme="greek", pointer="hexa",
            solar_rotation=False,
        ),
    )
    day, tick = _day_tick(datetime(2026, 12, 13, 12, 0))   # Sunday, Ophiuchus's window
    assert constants.WEEKDAY_BODIES[day.weekday_index] == "sun"
    assert "ophiuchus" in day.thirteenth_candidates        # the date fact still holds
    assert active_thirteenth(skin, day) is None             # but hexa never shows it
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    hover = comp.tooltip_at(180.0, 180.0, 360.0)
    assert hover is not None
    assert "Ophiuchus" not in hover and "steps aside" not in hover
    assert "Gaia" in hover        # the Ninth claims solar noon as usual, undisplaced


def test_center_only_mode_shows_no_thirteenth_off_the_calendar_pointer(app):
    """The center_only showcase was the OTHER seat R12 wrongly used —
    confirmed dead on a non-Calendar pointer even with an active window."""
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        weekday_set=dataclasses.replace(
            defaults.DEFAULT_SKIN.weekday_set, display_mode="center_only",
        ),
        pointer="octa",
    )
    day, tick = _day_tick(datetime(2026, 7, 8, 12, 0))     # inside Sol's window
    assert "sol" in day.thirteenth_candidates
    assert center_seat_body_key(skin, constants.WEEKDAY_BODIES[day.weekday_index]) is not None
    assert active_thirteenth(skin, day) is None
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    hover = comp.tooltip_at(180.0, 180.0, 360.0)
    assert hover is not None and "Sol" not in hover


def test_no_center_seat_means_no_thirteenth_forced():
    """Cross/octa WITHOUT center_only mode have no center seat at all —
    the ordinary weekday law never invents one, and the Blue Moon Law
    stays gated on the pointer regardless."""
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa")
    assert center_seat_body_key(skin, "sun") is None
    assert center_seat_body_key(skin, "mars") is None


# --- 8. THE CALENDAR POINTER'S FOUR INDEPENDENT MODES --------------------------


def test_zodiac_wheel_claims_ophiuchus():
    skin = _calendar_skin(palette_style="paint", calendar_mount="off")
    day, _tick = _day_tick(datetime(2026, 12, 5, 12, 0))
    assert "ophiuchus" in day.thirteenth_candidates
    assert active_thirteenth(skin, day) == "ophiuchus"


def test_almanac_wheel_claims_sol():
    skin = _calendar_skin(palette_style="light", calendar_mount="off")
    day, _tick = _day_tick(datetime(2026, 7, 8, 12, 0))
    assert "sol" in day.thirteenth_candidates
    assert active_thirteenth(skin, day) == "sol"


def test_months_mount_claims_modrenik():
    skin = _calendar_skin(palette_style="paint", calendar_mount="months")
    day, _tick = _day_tick(datetime(2026, 12, 19, 12, 0))   # past Ophiuchus's close
    assert "modrenik" in day.thirteenth_candidates
    assert active_thirteenth(skin, day) == "modrenik"


def test_chinese_mount_claims_the_cat():
    skin = _calendar_skin(palette_style="light", calendar_mount="chinese")
    day, _tick = _day_tick(datetime(2025, 8, 1, 12, 0))
    assert "chinese" in day.thirteenth_candidates
    assert active_thirteenth(skin, day) == "chinese"


def test_zodiac_mount_names_no_thirteenth_of_its_own():
    """calendar_mount == "zodiac" names no 13th (Ophiuchus already
    belongs to the WHEEL, not the mount) — resolution falls through to
    the wheel exactly like "off"."""
    skin = _calendar_skin(palette_style="paint", calendar_mount="zodiac")
    day, _tick = _day_tick(datetime(2026, 12, 5, 12, 0))
    assert active_thirteenth(skin, day) == "ophiuchus"


def test_mount_outranks_the_wheel_when_both_claim():
    """THE OWNER'S TIEBREAK, ground-truthed from the settings model:
    `calendar_mount` is fully independent of `palette_style`, so BOTH
    can be active at once. Dec 13 2026 sits inside BOTH Ophiuchus's and
    Modrenik's windows (test_ophiuchus_and_modrenik_windows_can_both_be_
    true_facts above) — the zodiac WHEEL alone claims Ophiuchus, but the
    "months" MOUNT on top of that same wheel claims Modrenik instead:
    the mount is the more deliberate second choice, so it wins."""
    day, _tick = _day_tick(datetime(2026, 12, 13, 12, 0))
    assert {"ophiuchus", "modrenik"} <= day.thirteenth_candidates
    zodiac_only = _calendar_skin(palette_style="paint", calendar_mount="off")
    assert active_thirteenth(zodiac_only, day) == "ophiuchus"
    with_months_mount = _calendar_skin(palette_style="paint", calendar_mount="months")
    assert active_thirteenth(with_months_mount, day) == "modrenik"


def test_no_thirteenth_on_the_calendar_pointer_off_its_own_window():
    """The Calendar pointer alone is not enough — the date must still
    fall inside the claiming member's own trigger+window."""
    skin = _calendar_skin(palette_style="paint", calendar_mount="off")
    day, _tick = _day_tick(datetime(2026, 3, 15, 12, 0))
    assert day.thirteenth_candidates == frozenset()
    assert active_thirteenth(skin, day) is None


# --- 9. Hover + Spacebar on the Calendar pointer's own dial center ------------


def test_ophiuchus_hover_and_encyclopedia_target(app):
    skin = _calendar_skin(palette_style="paint", calendar_mount="off")
    day, tick = _day_tick(datetime(2026, 12, 5, 12, 0))
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    hover = comp.tooltip_at(180.0, 180.0, 360.0)
    assert hover is not None and "Ophiuchus" in hover
    # "astrology" topic: 12 zodiac signs (0-11) then Ophiuchus at 12
    # (app.encyclopedia._topics' own ninth-append order).
    assert comp.encyclopedia_target(180.0, 180.0, 360.0) == ("astrology", 12)


def test_sol_hover_and_encyclopedia_target(app):
    skin = _calendar_skin(palette_style="light", calendar_mount="off")
    day, tick = _day_tick(datetime(2026, 7, 8, 12, 0))
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    hover = comp.tooltip_at(180.0, 180.0, 360.0)
    assert hover is not None and "Sol" in hover
    # "months" topic: the Overview (0) + twelve Slavic months (1-12),
    # then Sol at 13, Modrenik at 14.
    assert comp.encyclopedia_target(180.0, 180.0, 360.0) == ("months", 13)


def test_modrenik_hover_and_encyclopedia_target(app):
    skin = _calendar_skin(palette_style="paint", calendar_mount="months")
    day, tick = _day_tick(datetime(2026, 12, 19, 12, 0))
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    hover = comp.tooltip_at(180.0, 180.0, 360.0)
    assert hover is not None and "Modrenik" in hover
    assert comp.encyclopedia_target(180.0, 180.0, 360.0) == ("months", 14)


def test_cat_hover_and_encyclopedia_target(app):
    skin = _calendar_skin(palette_style="light", calendar_mount="chinese")
    day, tick = _day_tick(datetime(2025, 8, 1, 12, 0))
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    hover = comp.tooltip_at(180.0, 180.0, 360.0)
    assert hover is not None and "Cat" in hover
    # "chinese" topic: 12 animals (0-11) + 5 elements (12-16), then The
    # Cat at 17 (app.encyclopedia._topics' own ninth-append order).
    assert comp.encyclopedia_target(180.0, 180.0, 360.0) == ("chinese", 17)
