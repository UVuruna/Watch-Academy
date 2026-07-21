"""THE BLUE MOON LAW (owner-sealed 2026-07-22, R12): the 13th member of
every 12-set. Pins `thirteen_moon_year` against published full-moon
counts, each 13th's own window (boundary days both sides), The Cat's
REAL lunisolar leap month against two independently verified years, the
center precedence (13th over a dual-less theme, over the Ninth, on any
weekday), the graceful-absent contract for Sol/Modrenik, and the
DayContext wiring. Purity (no Qt, no wall clock) is covered generically
by tests/test_purity.py's core/*.py glob — not re-pinned here.
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
    active_thirteenth,
    chinese_leap_month,
    modrenik_window,
    ophiuchus_window,
    sol_window,
    thirteen_moon_year,
)
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import center_seat_body_key, thirteenth_plate


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


# --- 3. active_thirteenth: boundary days, both sides --------------------------


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
    assert active_thirteenth(lo - timedelta(days=1), window, anchors, leap) != key
    assert active_thirteenth(lo, window, anchors, leap) == key
    assert active_thirteenth(hi, window, anchors, leap) == key
    assert active_thirteenth(hi + timedelta(days=1), window, anchors, leap) != key


def test_modrenik_window_boundaries_are_inclusive_and_cross_new_year():
    """Modrenik's window crosses the New Year in a blue-moon December
    (2026's solstice window runs into Jan 2027) — checked on its
    UNAMBIGUOUS tail, past Ophiuchus's own Dec 17 close, so no
    precedence tiebreak is in play here (the overlapping HEAD is
    covered by test_ophiuchus_outranks_modrenik_in_their_overlap_band)."""
    mr, sr = MoonPhaseRepository(), SeasonsRepository()
    window26, anchors26 = mr.moon_window(2026), sr.year_anchors(2026)
    leap26 = chinese_leap_month(anchors26, window26)
    lo, hi = modrenik_window(anchors26.instants[4])
    assert lo.year == 2026 and hi.year == 2027            # crosses the New Year
    unambiguous = date(2026, 12, 19)                      # past Ophiuchus's Dec 17
    assert lo <= unambiguous <= hi
    assert active_thirteenth(unambiguous, window26, anchors26, leap26) == "modrenik"
    # `hi` falls in 2027 — read through 2027's own YearAnchors/MoonWindow
    # (instants[0] is the SAME December solstice; MoonPhaseRepository
    # always brackets year-1, so 2026's Full Moons are still present).
    window27, anchors27 = mr.moon_window(2027), sr.year_anchors(2027)
    leap27 = chinese_leap_month(anchors27, window27)
    assert active_thirteenth(hi, window27, anchors27, leap27) == "modrenik"
    assert active_thirteenth(hi + timedelta(days=1), window27, anchors27, leap27) != "modrenik"


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
    assert active_thirteenth(date(2025, 7, 1), window, anchors, leap) is None


def test_no_thirteenth_on_an_ordinary_date():
    mr, sr = MoonPhaseRepository(), SeasonsRepository()
    window, anchors = mr.moon_window(2026), sr.year_anchors(2026)
    leap = chinese_leap_month(anchors, window)
    assert active_thirteenth(date(2026, 3, 15), window, anchors, leap) is None


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
    assert active_thirteenth(leap.start - timedelta(days=1), window, anchors, leap) != "chinese"
    assert active_thirteenth(leap.start, window, anchors, leap) == "chinese"
    assert active_thirteenth(leap.end, window, anchors, leap) == "chinese"
    assert active_thirteenth(leap.end + timedelta(days=1), window, anchors, leap) != "chinese"


# --- 5. Precedence -------------------------------------------------------------


def test_ophiuchus_outranks_modrenik_in_their_overlap_band():
    """The one genuine overlap (owner-documented tiebreak, R12): both
    ride the SAME thirteen_moon_year trigger, and their windows share
    the Dec 7-17 band of a blue-moon December — Ophiuchus (the real
    transit) wins there; Modrenik only takes over once Ophiuchus's own
    window closes."""
    mr, sr = MoonPhaseRepository(), SeasonsRepository()
    window, anchors = mr.moon_window(2026), sr.year_anchors(2026)
    leap = chinese_leap_month(anchors, window)
    assert thirteen_moon_year(2026, window)
    o_lo, o_hi = ophiuchus_window(2026)
    m_lo, m_hi = modrenik_window(anchors.instants[4])
    assert m_lo <= o_hi < m_hi                             # the windows truly overlap
    for probe in (m_lo, o_hi):
        assert active_thirteenth(probe, window, anchors, leap) == "ophiuchus"
    assert active_thirteenth(o_hi + timedelta(days=1), window, anchors, leap) == "modrenik"


# --- 6. DayContext wiring (computed once a day, never per-minute) -------------


def test_day_context_carries_the_resolved_thirteenth():
    sol_day, _tick = _day_tick(datetime(2026, 7, 8, 12, 0))   # inside Sol's window
    assert sol_day.active_thirteenth == "sol"
    assert sol_day.chinese_leap_month_number is None

    cat_day, _tick = _day_tick(datetime(2025, 8, 1, 12, 0))   # inside the Cat's window
    assert cat_day.active_thirteenth == "chinese"
    assert cat_day.chinese_leap_month_number == 6

    plain_day, _tick = _day_tick(datetime(2026, 3, 15, 12, 0))
    assert plain_day.active_thirteenth is None
    assert plain_day.chinese_leap_month_number is None


# --- 7. The registry + graceful-absent art ------------------------------------


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


# --- 8. The dial CENTER: outranks the ordinary face, on ANY weekday ----------


def test_thirteenth_outranks_a_dual_less_theme_on_any_weekday(app):
    """DEFAULT_SKIN's "planets" theme carries NO Ruler/Servant duality
    at all — the 13th must still claim the center: its trigger is a
    calendar fact, never gated on whether the theme even has a
    duality (unlike `center_dual_face`, which core_seat_body_key does
    NOT require)."""
    assert defaults.DEFAULT_SKIN.weekday_set.dual_asset is None
    day, tick = _day_tick(datetime(2026, 7, 8, 12, 0))     # a Wednesday, Sol's window
    today = constants.WEEKDAY_BODIES[day.weekday_index]
    assert today != "sun"
    assert center_seat_body_key(defaults.DEFAULT_SKIN, today) == "sun"
    comp = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    hover = comp.tooltip_at(180.0, 180.0, 360.0)
    assert hover is not None and "Sol" in hover


def test_thirteenth_outranks_the_ninth_on_the_real_sunday(app):
    """A Sunday inside Ophiuchus's window, on a Greek-themed hexa dial
    that would otherwise show Gaia (the Ninth) near solar noon — item
    7's precedence: the 13th still wins, and the hover names what
    stepped aside."""
    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(
            Settings(), weekday_theme="greek", pointer="hexa",
            solar_rotation=False,
        ),
    )
    day, tick = _day_tick(datetime(2026, 12, 13, 12, 0))   # a Sunday, Ophiuchus window
    assert constants.WEEKDAY_BODIES[day.weekday_index] == "sun"
    assert day.active_thirteenth == "ophiuchus"
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    hover = comp.tooltip_at(180.0, 180.0, 360.0)
    assert hover is not None
    assert "Ophiuchus" in hover and "Gaia" not in hover
    assert "steps aside" in hover


def test_center_only_mode_also_shows_the_thirteenth(app):
    """The center_only showcase is the OTHER seat the law reuses (item
    7: "the Sunday-seat mechanic Prism/Trinity use") — confirmed on a
    non-hexa/trio pointer too."""
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        weekday_set=dataclasses.replace(
            defaults.DEFAULT_SKIN.weekday_set, display_mode="center_only",
        ),
        pointer="octa",
    )
    day, tick = _day_tick(datetime(2026, 7, 8, 12, 0))
    today = constants.WEEKDAY_BODIES[day.weekday_index]
    assert center_seat_body_key(skin, today) == today
    comp = Compositor(skin, AssetCache())
    comp.render_offscreen(360.0, 1.0, day, tick)
    assert comp.tooltip_at(180.0, 180.0, 360.0) is not None


def test_no_center_seat_means_no_thirteenth_forced():
    """Cross/octa WITHOUT center_only mode have no center seat at all —
    the law only reuses an existing seat, it never invents one."""
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa")
    assert center_seat_body_key(skin, "sun") is None
    assert center_seat_body_key(skin, "mars") is None
