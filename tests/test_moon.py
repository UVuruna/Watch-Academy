"""Moon-phase golden values against the LIVE moon phases database, plus
(below) the RENDER geometry pins for the live-render round (owner
decree 2026-07-19: "bolje crtati na licu mesta nego 15MB fajlova") —
the shared terminator geometry `render.asset_variants.moon_lit_region` and its
callers `moon_phase_image` (the Encyclopedia's live Moon pages,
replacing the retired pre-baked plates) and the dial's own
`YearMarkerLayer._draw_moon`."""

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


# --- RENDER geometry (owner 2026-07-19, live-render round) -------------------


def test_moon_lit_region_quarter_is_exact_half_disc():
    """The exact-quarter degeneracy fix: at fraction 0.25/0.75 the
    terminator semi-axis (radius * |cos(2*pi*f)|) is mathematically
    zero — Qt's `addEllipse` on a zero-width rect used to degenerate
    the `united`/`subtracted` boolean op to an EMPTY path (the moon
    rendering fully DARK instead of exactly half-lit — the bug the
    retired pre-baked plates shipped with). `moon_lit_region` must
    resolve to the exact half-disc instead."""
    from PySide6.QtCore import QPointF

    from render.asset_variants import moon_lit_region

    radius = 100.0
    # fraction < 0.5 -> lit on the right (+x); >= 0.5 -> lit on the left.
    for fraction, lit_x in ((0.25, 1.0), (0.75, -1.0)):
        region = moon_lit_region(fraction, radius)
        assert not region.isEmpty(), fraction
        assert region.contains(QPointF(lit_x * radius * 0.5, 0.0))
        assert not region.contains(QPointF(-lit_x * radius * 0.5, 0.0))
        bounds = region.boundingRect()
        assert bounds.width() == pytest.approx(radius, abs=1.0), fraction


def _mean_lightness(image, x_range, y_step=5):
    total, n = 0, 0
    for x in x_range:
        for y in range(0, image.height(), y_step):
            pixel = image.pixelColor(x, y)
            if pixel.alpha() > 0:
                total += pixel.lightness()
                n += 1
    assert n > 0
    return total / n


def test_moon_phase_image_new_and_full_are_dark_and_lit():
    """The pure QImage render (owner 2026-07-19, replacing the retired
    `assets/moon/` plates): New Moon reads much darker than Full Moon
    over the whole disc."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from render.asset_variants import moon_phase_image

    QApplication.instance() or QApplication([])
    size = 200
    new = moon_phase_image(0.0, size)
    full = moon_phase_image(0.5, size)
    assert _mean_lightness(new, range(0, size, 5)) < (
        _mean_lightness(full, range(0, size, 5)) - 30
    )


def test_moon_phase_image_quarter_is_half_lit_not_fully_dark():
    """The regression pin for the fixed bug: at fraction 0.25 (First
    Quarter) and 0.75 (Third Quarter) the left/right halves must read
    STRONGLY different brightness — not both dark."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from render.asset_variants import moon_phase_image

    QApplication.instance() or QApplication([])
    size = 200
    for fraction in (0.25, 0.75):
        image = moon_phase_image(fraction, size)
        left = _mean_lightness(image, range(0, size // 2, 5))
        right = _mean_lightness(image, range(size // 2, size, 5))
        assert abs(left - right) > 20, fraction


def test_dial_moon_stays_half_lit_at_exact_quarter():
    """End-to-end pin: the dial's OWN `YearMarkerLayer._draw_moon`
    shares `moon_lit_region` with the Encyclopedia's live render — at
    tick.moon_fraction == 0.25 the drawn marker must not collapse to a
    uniform dark disc either."""
    import dataclasses
    import os
    from datetime import datetime
    from zoneinfo import ZoneInfo

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import astral
    from PySide6.QtWidgets import QApplication

    from config import defaults
    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository
    from render.assets import AssetCache
    from render.compositor import Compositor

    QApplication.instance() or QApplication([])
    tz = ZoneInfo("Europe/Belgrade")
    now = datetime(2026, 7, 10, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=44.82, longitude=20.46)
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    quarter = dataclasses.replace(
        tick, moon_fraction=0.25, moon_event=None, eclipse_event=None,
    )
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    image = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quarter
    )
    radius = 270.0
    import math

    moon_angle = math.radians(quarter.moon_fraction * 360.0)
    orbit = radius * defaults.DEFAULT_SKIN.year_marker.moon_orbit_fraction
    cx = round(radius + orbit * math.sin(moon_angle))
    cy = round(radius - orbit * math.cos(moon_angle))
    marker_size = round(
        2 * radius * defaults.DEFAULT_SKIN.year_marker.moon_scale
    )
    half = max(1, marker_size // 2 - 2)

    def crop_mean(x_range, y_range):
        total, n = 0, 0
        for x in x_range:
            for y in y_range:
                pixel = image.pixelColor(x, y)
                if pixel.alpha() > 0:
                    total += pixel.lightness()
                    n += 1
        assert n > 0
        return total / n

    y_span = range(cy - half, cy + half, 2)
    left = crop_mean(range(cx - half, cx, 2), y_span)
    right = crop_mean(range(cx, cx + half, 2), y_span)
    assert abs(left - right) > 15


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
