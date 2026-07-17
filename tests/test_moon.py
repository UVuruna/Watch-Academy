"""Moon-phase golden values against the LIVE moon phases database."""

from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from core.deep_time import canonical_proxy
from core.moon import illumination, nominal_illumination, phase_fraction
from data.moon_phases import MoonPhaseRepository

RESEARCH_DB = (
    Path(__file__).resolve().parents[1]
    / "research" / "ephemeris" / "events.sqlite"
)


@pytest.fixture(scope="module")
def window_2026():
    return MoonPhaseRepository().moon_window(2026)


def test_reference_moment(window_2026):
    """2026-07-07: interpolated fraction 0.7400 (astral cross-check 0.7401)."""
    now = datetime(2026, 7, 7, 12, 0, tzinfo=timezone.utc)
    assert phase_fraction(now, window_2026) == pytest.approx(0.74, abs=0.01)


def test_exact_at_anchors(window_2026):
    full_moons = [t for t, f in window_2026.events if f == 0.5 and t.year == 2026]
    assert full_moons, "2026 must contain full moons"
    assert phase_fraction(full_moons[0], window_2026) == pytest.approx(0.5, abs=1e-9)


def test_waning_segment_runs_forward(window_2026):
    """Third Quarter → New Moon spans 0.75 → 1.0, NOT 0.75 → 0.0 backward:
    2026-07-10 noon sits mid-segment at ≈0.85 (a natural refactor to
    (f1−f0) interpolation would render it as near-full 0.44 instead of a
    waning crescent — this pins the direction)."""
    now = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)
    assert phase_fraction(now, window_2026) == pytest.approx(0.852, abs=0.002)


def test_wrap_to_zero_at_new_moon_anchor(window_2026):
    new_moons = [t for t, f in window_2026.events if f == 0.0 and t.year == 2026]
    assert new_moons, "2026 must contain new moons"
    assert phase_fraction(new_moons[0], window_2026) == pytest.approx(0.0, abs=1e-9)


def test_moon_rise_set_belgrade():
    """Belgrade 2026-07-10 (waning crescent): the moon rises just after
    midnight and sets mid-afternoon — 00:43 / 16:33 local per astral
    (minute resolution). The Moon hover's od–do line reads these."""
    from datetime import date
    from zoneinfo import ZoneInfo

    import astral

    from config import defaults
    from core.moon import moon_rise_set

    city = defaults.DEFAULT_CITY
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    rise, setting = moon_rise_set(
        observer, date(2026, 7, 10), ZoneInfo(city["timezone"])
    )
    assert rise.strftime("%H:%M") == "00:43"
    assert setting.strftime("%H:%M") == "16:33"
    assert rise.tzinfo is not None and setting.tzinfo is not None


def test_chinese_cusp_judged_in_chinas_frame(window_2026):
    """Review fix: the Chinese year flips on CHINA's calendar date (CNY
    2026 = Feb 17 China time, new moon 12:01 UTC). An Auckland (UTC+13)
    midnight on their Feb 17 is still Feb 16 in China — the OLD Wood
    Snake year; the old observer-local comparison already reported the
    Fire Horse a day early."""
    from zoneinfo import ZoneInfo

    from core.moon import chinese_zodiac

    auckland = ZoneInfo("Pacific/Auckland")
    before = datetime(2026, 2, 17, 0, 0, tzinfo=auckland)
    name, _, _ = chinese_zodiac(before, window_2026)
    assert name == "Wood Snake"
    after = datetime(2026, 2, 18, 12, 0, tzinfo=auckland)
    name, start, _ = chinese_zodiac(after, window_2026)
    assert name == "Fire Horse"
    assert start.strftime("%d %b %Y") == "17 Feb 2026"


def test_meteorological_summer_2026():
    """Cross-arm hover bounds (owner spec): summer runs from halfway
    spring-equinox→summer-solstice to halfway summer-solstice→autumn-
    equinox — 2026: 5 May 23:35 to 7 Aug 04:14 (UTC anchors carry
    seconds, so the printed anchor minutes round differently)."""
    from core.year_wheel import meteorological_span
    from data.seasons import SeasonsRepository

    anchors = SeasonsRepository().year_anchors(2026)
    start, end = meteorological_span(anchors, 360.0)   # the summer solstice
    assert start.strftime("%d %b %H:%M") == "05 May 23:35"
    assert end.strftime("%d %b %H:%M") == "07 Aug 04:14"


def test_outside_window_fails_loudly(window_2026):
    with pytest.raises(ValueError, match="outside the moon window"):
        phase_fraction(datetime(2031, 1, 1, tzinfo=timezone.utc), window_2026)


def test_coverage_edge_year_still_interpolates():
    """1551 has no 1550 neighbor — the 2-year window must still bracket
    instants inside the year itself."""
    window = MoonPhaseRepository().moon_window(1551)
    assert window.events[0][0].year == 1551
    mid = datetime(1551, 7, 1, tzinfo=timezone.utc)
    assert 0.0 <= phase_fraction(mid, window) < 1.0


def test_may_2026_has_five_events(window_2026):
    may = [(t, f) for t, f in window_2026.events if (t.year, t.month) == (2026, 5)]
    assert len(may) == 5
    assert sum(1 for _, f in may if f == 0.5) == 2  # two full moons


def test_third_quarter_normalization(window_2026):
    fractions = {f for _, f in window_2026.events}
    assert fractions == {0.0, 0.25, 0.5, 0.75}


def test_window_spans_neighbor_years(window_2026):
    assert window_2026.events[0][0].year == 2025
    assert window_2026.events[-1][0].year == 2027


def test_phase_names_follow_the_common_convention():
    """A principal name holds only around its instant; the day after the
    Third Quarter (owner checked online for 8 July 2026) the moon must
    already read Waning Crescent."""
    from core.moon import phase_name

    assert phase_name(0.75) == "Third Quarter"          # the instant itself
    assert phase_name(0.76) == "Third Quarter"          # within +-half a day
    assert phase_name(0.774) == "Waning Crescent"       # ~0.7 days after
    assert phase_name(0.0) == "New Moon"
    assert phase_name(0.98) == "Waning Crescent"
    assert phase_name(0.99) == "New Moon"               # approaching the instant
    assert phase_name(0.12) == "Waxing Crescent"
    assert phase_name(0.35) == "Waxing Gibbous"
    assert phase_name(0.5) == "Full Moon"
    assert phase_name(0.6) == "Waning Gibbous"


def test_nominal_illumination_curve():
    """The ring's own cosine mapping of a cycle POSITION — kept for the
    hypothetical ring-tick hover only (Session 16); the live moon reads
    the analytic illumination below."""
    assert nominal_illumination(0.0) == pytest.approx(0.0)
    assert nominal_illumination(0.25) == pytest.approx(0.5)
    assert nominal_illumination(0.5) == pytest.approx(1.0)
    assert nominal_illumination(0.75) == pytest.approx(0.5)


# --- TRUE analytic illumination (Session 16, owner slike 4-7) -----------------


def test_analytic_illumination_at_bundled_principal_instants(window_2026):
    """At every 2026 principal-phase instant the analytic series must
    read ~0/50/100/50 — the compact Meeus 48.4 form against the
    DE441-derived bundled instants (measured max deviation 0.35 p.p.
    in the modern era; the bound here is 0.6 p.p. + the exact-0/1
    cosine flatness near new/full)."""
    for instant, fraction in window_2026.events:
        k = illumination(instant)
        expected = {0.0: 0.0, 0.25: 0.5, 0.5: 1.0, 0.75: 0.5}[fraction]
        assert k == pytest.approx(expected, abs=0.006), (instant, fraction)


def test_analytic_illumination_owner_cross_check():
    """Owner slike 4-7 (2026-07-17 10:11 UTC+2): our dial read 10.3%
    from the linear interpolation while the true value is ~11.5% — the
    analytic form must land within ±0.5 p.p. of the truth."""
    when = datetime(2026, 7, 17, 10, 11, tzinfo=ZoneInfo("Europe/Belgrade"))
    assert illumination(when) * 100 == pytest.approx(11.5, abs=0.5)


def test_analytic_illumination_unshifts_the_deep_proxy_frame():
    """In deep travel the proxy datetime carries a 400-year shift; the
    series must evaluate at the REAL epoch — the same proxy instant
    with and without cycles answers differently, and the deep answer
    stays a sane fraction."""
    proxy, cycles = canonical_proxy(-4499, 6, 21, 12, 0)
    when = proxy.replace(tzinfo=timezone.utc)
    deep = illumination(when, cycles)
    modern = illumination(when)
    assert 0.0 <= deep <= 1.0
    assert deep != pytest.approx(modern, abs=1e-6)


@pytest.mark.skipif(not RESEARCH_DB.exists(), reason="research db not built")
def test_analytic_illumination_against_the_research_span():
    """The spec's golden: at research-database principal instants the
    analytic illumination reads ~0/50/100/50 — tight in the modern era,
    within 3 p.p. at the ±13000-year edges (ΔT model dominated;
    measured 2.4 p.p. max on 2026-07-17)."""
    import sqlite3

    expected = {0: 0.0, 90: 0.5, 180: 1.0, 270: 0.5}
    con = sqlite3.connect(f"file:{RESEARCH_DB.as_posix()}?mode=ro", uri=True)
    for like, bound in (
        ("+02026-%", 0.006),
        ("-04499-%", 0.01),
        ("-12990-%", 0.03),
        ("+16990-%", 0.03),
    ):
        rows = con.execute(
            "SELECT iso_ut, type FROM moon_events WHERE iso_ut LIKE ?",
            (like,),
        ).fetchall()
        assert rows, like
        for iso, event_type in rows:
            year = int(iso[:6])
            month, day = int(iso[7:9]), int(iso[10:12])
            hh, mm, ss = int(iso[13:15]), int(iso[16:18]), int(iso[19:21])
            proxy, k = canonical_proxy(year, month, day, hh, mm)
            when = proxy.replace(second=ss, tzinfo=timezone.utc)
            assert illumination(when, k) == pytest.approx(
                expected[event_type], abs=bound
            ), iso
