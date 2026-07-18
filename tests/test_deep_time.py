"""Deep Time goldens (Session 16): the era formatters (owner amendment
2026-07-17 — Anno Lucis always beside the official year), the
astronomical-year mapping (1 BCE = year 0), the 400-year proxy frame,
the proleptic Julian Day, ΔT, the quick-jump calendar arithmetic, and
the pack repository with detection/chaining/eclipses — all against the
SMALL fixture pack, never the full 92 MB build."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from config import constants
from core.deep_time import (
    astro_from_display,
    canonical_proxy,
    delta_t_seconds,
    display_from_astro,
    format_official,
    format_year_line,
    is_leap,
    julian_day,
    month_length,
    proxy_cycles,
    real_year,
    shift_calendar,
    third_era_year,
)
from data.deep_time import DeepTimeRepository
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from tests.deep_fixture import FIXTURE_COVERAGE, build_fixture_pack

REAL_PACK = Path(__file__).resolve().parents[1] / "Database" / "deep_time.sqlite"


@pytest.fixture(scope="module")
def deep(tmp_path_factory):
    path = build_fixture_pack(tmp_path_factory.mktemp("pack") / "deep_time.sqlite")
    return DeepTimeRepository.detect(path)


# --- Era formatting (owner amendment 2026-07-17) ------------------------------


def test_official_form_positive_years_bare_unless_opted_in():
    assert format_official(2026, "bce_ce") == "2026"
    assert format_official(2026, "bce_ce", show_suffix=True) == "2026 CE"
    assert format_official(2026, "bc_ad", show_suffix=True) == "2026 AD"


def test_official_form_negative_years_always_carry_the_label():
    # Caesar died 44 BCE = astronomical -43; 1 BCE = year 0.
    assert format_official(-43, "bce_ce") == "44 BCE"
    assert format_official(-43, "bc_ad") == "44 BC"
    assert format_official(0, "bce_ce") == "1 BCE"
    assert format_official(-4499, "bce_ce") == "4500 BCE"


def test_year_line_pairs_anno_lucis_always():
    """The owner's sealed pairing: A.L. = CE + 4079, never a mode."""
    assert format_year_line(2026, "bce_ce") == "2026 · 6105. Anno Lucis"
    assert (
        format_year_line(2026, "bce_ce", True, "auc")
        == "2026 CE · 6105. Anno Lucis · 2779. AUC"
    )
    # A.L. 1 = 4079 BCE, the first year of the unbroken light era.
    assert format_year_line(-4078, "bce_ce") == "4079 BCE · 1. Anno Lucis"


def test_third_era_years():
    assert third_era_year(2026, "auc") == 2779
    assert third_era_year(2026, "byzantine") == 7535
    assert third_era_year(2026, "hebrew") == 5786
    # The documented display-grade lunar approximation: mid-2026 sits
    # at the AH 1447→1448 turn.
    assert third_era_year(2026, "hegirae") in (1447, 1448)
    # The Chinese (Huangdi) count, owner fix-round B 2026-07-19: the
    # CE + 2697 convention (sources spread 2695-2698).
    assert third_era_year(2026, "chinese") == 4723


def test_chinese_third_era_joins_the_year_line():
    """The Huangdi count reads on the year line exactly like every
    other third calendar (owner fix-round B 2026-07-19, "zašto nismo
    ubacili kineski")."""
    assert (
        format_year_line(2026, "bce_ce", True, "chinese")
        == "2026 CE · 6105. Anno Lucis · 4723. Huangdi"
    )
    assert "chinese" in constants.THIRD_ERAS
    assert constants.THIRD_ERA_LABELS["chinese"] == "Huangdi"


def test_format_anno_lucis_matches_the_year_line_pairing():
    """`format_anno_lucis` is the SAME derivation `format_year_line`
    reuses — never re-derived (Rule #5)."""
    from core.deep_time import format_anno_lucis

    assert format_anno_lucis(2026) == "6105. Anno Lucis"
    assert format_anno_lucis(-4078) == "1. Anno Lucis"


def test_is_age_of_light_matches_the_sealed_span():
    """research/ephemeris/anno_lucis.json: light_era = [-4078, 6423]
    inclusive; everything else covered is the Age of Darkness."""
    from core.deep_time import is_age_of_light

    assert is_age_of_light(-4078) is True           # first light year
    assert is_age_of_light(2026) is True             # today
    assert is_age_of_light(6423) is True             # last light year
    assert is_age_of_light(6424) is False            # first dark year
    assert is_age_of_light(-4079) is False           # last dark year before
    assert is_age_of_light(10990) is False           # dark era trough
    assert is_age_of_light(-9560) is False           # previous dark era peak


def test_display_era_round_trip_incl_year_zero():
    assert display_from_astro(2026) == (2026, 0)
    assert display_from_astro(0) == (1, 1)          # 1 BCE = astro 0
    assert display_from_astro(-4499) == (4500, 1)
    for astro in (-13000, -4499, -1, 0, 1, 2026, 17000):
        display, era = display_from_astro(astro)
        assert astro_from_display(display, era) == astro


# --- The 400-year proxy frame -------------------------------------------------


def test_proxy_cycles_identity_inside_datetime_range():
    assert proxy_cycles(2026) == 0
    assert proxy_cycles(2) == 0
    assert proxy_cycles(9998) == 0


def test_proxy_cycles_shift_lands_in_the_canonical_window():
    for astro in (-13000, -4499, -1, 0, 1, 9999, 12000, 17000):
        cycles = proxy_cycles(astro)
        proxy = astro + cycles * constants.GREGORIAN_CYCLE_YEARS
        assert constants.PROXY_WINDOW_FIRST <= proxy < (
            constants.PROXY_WINDOW_FIRST + constants.GREGORIAN_CYCLE_YEARS
        )
        assert real_year(proxy, cycles) == astro


def test_proxy_preserves_leap_and_weekday():
    """The whole point of the 400-year cycle: identical calendars."""
    for astro in (-4499, -4400, 0, 10000, 16993):
        cycles = proxy_cycles(astro)
        proxy = astro + cycles * constants.GREGORIAN_CYCLE_YEARS
        assert is_leap(astro) == is_leap(proxy)
        # Weekday golden via the Julian Day: JD+1.5 mod 7 == 0 for
        # Monday-start weekday of the proleptic Gregorian calendar.
        jd_weekday = int(julian_day(astro, 6, 21) + 1.5) % 7
        assert datetime(proxy, 6, 21).weekday() == (jd_weekday - 1) % 7


def test_canonical_proxy_golden():
    proxy, cycles = canonical_proxy(-4499, 6, 21, 12, 0)
    assert (proxy, cycles) == (datetime(2301, 6, 21, 12, 0), 17)
    proxy, cycles = canonical_proxy(2026, 7, 17, 10, 11)
    assert (proxy, cycles) == (datetime(2026, 7, 17, 10, 11), 0)


# --- Julian Day and ΔT --------------------------------------------------------


def test_julian_day_modern_goldens():
    assert julian_day(2000, 1, 1, 0.5) == pytest.approx(2451545.0)
    assert julian_day(1999, 8, 11, 0.0) == pytest.approx(2451401.5)
    assert julian_day(2026, 7, 17, 0.0) == pytest.approx(2461238.5)


@pytest.mark.skipif(not REAL_PACK.exists(), reason="Deep Time pack not built")
def test_julian_day_matches_the_pack_across_the_span():
    """The proleptic-Gregorian JD must reproduce the Swiss Ephemeris
    pipeline's own jd_ut from the stored calendar fields — sampled
    across the whole span, sub-second agreement."""
    import sqlite3

    con = sqlite3.connect(f"file:{REAL_PACK.as_posix()}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT jd_ut, year, month, day, sod FROM solar_eclipses "
        "WHERE rowid % 977 = 0"
    ).fetchall()
    assert len(rows) > 50
    for jd_ut, year, month, day, sod in rows:
        ours = julian_day(year, month, day, sod / 86400.0)
        assert abs(ours - jd_ut) < 1.0 / 86400.0, (year, month, day)


def test_delta_t_sanity():
    assert 60.0 < delta_t_seconds(2026) < 80.0
    # The Swiss Ephemeris values measured from the research database
    # (2026-07-17): −12990 → 198.49 h, +16990 → 202.86 h; the published
    # Espenak-Meeus fit must stay within a few hours of them.
    assert abs(delta_t_seconds(-12990) / 3600.0 - 198.49) < 5.0
    assert abs(delta_t_seconds(16990) / 3600.0 - 202.86) < 5.0


# --- Quick-jump calendar arithmetic ------------------------------------------


def test_shift_calendar_leap_clamps():
    assert shift_calendar(2024, 2, 29, years=1) == (2025, 2, 28)
    assert shift_calendar(2024, 1, 31, months=1) == (2024, 2, 29)
    assert shift_calendar(2023, 1, 31, months=1) == (2023, 2, 28)


def test_shift_calendar_month_rollover_and_units():
    assert shift_calendar(2026, 12, 15, months=1) == (2027, 1, 15)
    assert shift_calendar(2026, 1, 15, months=-1) == (2025, 12, 15)
    assert shift_calendar(2026, 7, 17, years=100) == (2126, 7, 17)
    assert shift_calendar(2026, 7, 17, years=-1000) == (1026, 7, 17)


def test_shift_calendar_era_edge_is_plain_arithmetic():
    """1 BCE = astro 0: crossing the era is ordinary arithmetic in
    astronomical years — no year-0 gap."""
    assert shift_calendar(0, 3, 15, years=1) == (1, 3, 15)
    assert shift_calendar(1, 3, 15, years=-1) == (0, 3, 15)
    assert shift_calendar(0, 1, 15, months=-1) == (-1, 12, 15)
    # Year 0 IS leap (proleptic Gregorian).
    assert is_leap(0)
    assert month_length(0, 2) == 29
    assert shift_calendar(0, 2, 29, years=1) == (1, 2, 28)


# --- The pack repository ------------------------------------------------------


def test_detect_absent_pack_is_none(tmp_path):
    assert DeepTimeRepository.detect(tmp_path / "nope.sqlite") is None


def test_detect_present_pack_reads_meta_coverage(deep):
    assert deep is not None
    assert deep.coverage() == FIXTURE_COVERAGE


def test_year_anchors_proxy_shifted_bce(deep):
    anchors = deep.year_anchors(-4499)
    assert anchors.year == 2301                  # -4499 + 17 cycles
    assert anchors.instants == (
        datetime(2300, 12, 21, 12, 0, tzinfo=timezone.utc),
        datetime(2301, 3, 20, 12, 0, tzinfo=timezone.utc),
        datetime(2301, 6, 21, 12, 0, tzinfo=timezone.utc),
        datetime(2301, 9, 22, 12, 0, tzinfo=timezone.utc),
        datetime(2301, 12, 21, 12, 0, tzinfo=timezone.utc),
        datetime(2302, 3, 20, 12, 0, tzinfo=timezone.utc),
    )


def test_moon_window_brackets_and_fractions(deep):
    window = deep.moon_window(-4499)
    instants = [when for when, _ in window.events]
    assert instants == sorted(instants)
    assert {fraction for _, fraction in window.events} == {0.0, 0.25, 0.5, 0.75}
    # The proxy moment of the deep summer solstice lies inside.
    proxy, _ = canonical_proxy(-4499, 6, 21, 12, 0)
    assert instants[0] <= proxy.replace(tzinfo=timezone.utc) <= instants[-1]


def test_missing_year_inside_coverage_fails_loudly(deep):
    """The fixture's hole between its spans: a year the pack cannot
    serve must name itself, never interpolate silently (Rule #1)."""
    with pytest.raises(ValueError, match="missing sun events"):
        deep.year_anchors(1000)


def test_out_of_coverage_names_the_span(deep):
    with pytest.raises(ValueError, match="-4501-3001"):
        deep.year_anchors(-9000)


def test_repositories_chain_beyond_the_bundle(deep):
    seasons = SeasonsRepository(deep=deep)
    moon = MoonPhaseRepository(deep=deep)
    assert seasons.year_anchors(3000) == deep.year_anchors(3000)
    assert moon.moon_window(3000) == deep.moon_window(3000)
    # Bundled years stay bundled — bit-identical to the no-pack repo.
    assert (
        seasons.year_anchors(2026).instants
        == SeasonsRepository().year_anchors(2026).instants
    )
    # The bundled coverage() is untouched (the widening lives in the
    # controller's _travel_coverage).
    assert seasons.coverage() == SeasonsRepository().coverage()


def test_without_the_pack_the_old_error_stands():
    with pytest.raises(ValueError, match="no entry for 3000"):
        SeasonsRepository().year_anchors(3000)


def test_eclipse_next_prev_from_the_fixture(deep):
    jd = julian_day(-4499, 6, 21, 0.5)
    after = deep.eclipse_after(jd, "solar")
    assert (after.year, after.month, after.day, after.type) == (
        -4499, 9, 12, "hybrid",
    )
    assert after.magnitude == pytest.approx(1.01)
    assert (after.lat, after.lon) == (pytest.approx(-24.1), pytest.approx(117.8))
    before = deep.eclipse_before(jd, "solar")
    assert (before.year, before.month, before.day, before.type) == (
        -4499, 3, 8, "partial",
    )
    lunar = deep.eclipse_before(jd, "lunar")
    assert (lunar.year, lunar.month, lunar.day, lunar.type) == (
        -4499, 4, 2, "total",
    )
    assert lunar.lat is None and lunar.lon is None
    # Strictly after the last catalog eclipse: the edge answers None
    # (the Quick Jump stays put — the standard clamp).
    assert deep.eclipse_after(julian_day(3000, 6, 1, 0.1), "solar") is None
