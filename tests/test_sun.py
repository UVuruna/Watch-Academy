"""Golden sun values, empirically verified against astral 3.2.

Includes the Belgrade DST hexagram jump, the four Tromso daylight
regimes, Longyearbyen polar night (solar noon still computable) and the
mockup day from the design screenshots.
"""

from datetime import date
from zoneinfo import ZoneInfo

import astral
import pytest

from core import angles
from core.sun import DaylightRegime, compute_sun_day
from data.locations import LocationRepository

TROMSO = astral.Observer(latitude=69.6489, longitude=18.9551)
LONGYEARBYEN = astral.Observer(latitude=78.2232, longitude=15.6267)
OSLO_TZ = ZoneInfo("Europe/Oslo")


@pytest.fixture(scope="module")
def belgrade():
    matches = LocationRepository().find_city("Belgrade")
    serbian = [record for record in matches if "Serbia" in record.path]
    assert serbian, "Belgrade (Serbia) must exist in the locations database"
    return serbian[0]


def _sun_day(record, on_date):
    observer = astral.Observer(latitude=record.latitude, longitude=record.longitude)
    return compute_sun_day(observer, on_date, ZoneInfo(record.timezone))


class TestBelgradeDst:
    """Across 2026's spring-forward the hexagram legitimately jumps +15 deg."""

    def test_day_before_transition(self, belgrade):
        sun_day = _sun_day(belgrade, date(2026, 3, 28))
        assert sun_day.regime is DaylightRegime.NORMAL
        assert angles.hexagram_rotation_deg(sun_day.noon) == pytest.approx(-4.17, abs=0.1)

    def test_day_after_transition(self, belgrade):
        sun_day = _sun_day(belgrade, date(2026, 3, 29))
        assert angles.hexagram_rotation_deg(sun_day.noon) == pytest.approx(10.76, abs=0.1)


class TestDaylightRegimes:
    def test_tromso_twilight_only_in_january(self):
        sun_day = compute_sun_day(TROMSO, date(2026, 1, 15), OSLO_TZ)
        assert sun_day.regime is DaylightRegime.TWILIGHT_ONLY
        assert sun_day.sunrise is None and sun_day.sunset is None
        assert sun_day.dawn is not None and sun_day.dusk is not None
        assert sun_day.dawn.strftime("%H:%M") == "08:56"
        assert sun_day.dusk.strftime("%H:%M") == "14:51"

    def test_tromso_white_nights_in_may(self):
        sun_day = compute_sun_day(TROMSO, date(2026, 5, 10), OSLO_TZ)
        assert sun_day.regime is DaylightRegime.WHITE_NIGHTS
        assert sun_day.sunrise is not None and sun_day.sunset is not None
        assert sun_day.dawn is None and sun_day.dusk is None

    def test_tromso_polar_day_in_late_may(self):
        sun_day = compute_sun_day(TROMSO, date(2026, 5, 25), OSLO_TZ)
        assert sun_day.regime is DaylightRegime.POLAR_DAY
        assert sun_day.sunrise is None and sun_day.dawn is None

    def test_longyearbyen_polar_night_keeps_solar_noon(self):
        sun_day = compute_sun_day(LONGYEARBYEN, date(2026, 12, 21), OSLO_TZ)
        assert sun_day.regime is DaylightRegime.POLAR_NIGHT
        assert sun_day.noon.strftime("%H:%M") == "11:55"
        assert angles.hexagram_rotation_deg(sun_day.noon) == pytest.approx(-1.2, abs=0.1)

    def test_belgrade_normal_day(self, belgrade):
        sun_day = _sun_day(belgrade, date(2026, 7, 7))
        assert sun_day.regime is DaylightRegime.NORMAL
        assert None not in (sun_day.dawn, sun_day.sunrise, sun_day.sunset, sun_day.dusk)


class TestSolarNoonOffsets:
    """Cities far from their zone meridian tilt the hexagram hard."""

    def test_santiago_de_compostela_summer(self):
        observer = astral.Observer(latitude=42.8782, longitude=-8.5449)
        sun_day = compute_sun_day(observer, date(2026, 6, 21), ZoneInfo("Europe/Madrid"))
        assert angles.hexagram_rotation_deg(sun_day.noon) == pytest.approx(39.76, abs=1.5)

    def test_santiago_de_compostela_winter(self):
        # No DST in December, so the offset is ~15 deg smaller than in
        # summer; 23.0 is this project's pinned value for 2026-12-21 (the
        # equation of time moves it a degree or two through the winter).
        observer = astral.Observer(latitude=42.8782, longitude=-8.5449)
        sun_day = compute_sun_day(observer, date(2026, 12, 21), ZoneInfo("Europe/Madrid"))
        assert angles.hexagram_rotation_deg(sun_day.noon) == pytest.approx(23.0, abs=1.0)

    def test_kamchatka(self):
        observer = astral.Observer(latitude=53.0452, longitude=158.6483)
        sun_day = compute_sun_day(observer, date(2026, 6, 21), ZoneInfo("Asia/Kamchatka"))
        assert angles.hexagram_rotation_deg(sun_day.noon) == pytest.approx(22.57, abs=1.5)


class TestExtremeZones:
    def test_kiritimati_noon_stays_on_the_requested_local_day(self):
        """UTC+14: astral's raw noon() lands on the NEXT local day —
        compute_sun_day must re-anchor it so all five events share one
        local calendar date and absolute ordering holds."""
        observer = astral.Observer(latitude=1.87, longitude=-157.44)
        sun_day = compute_sun_day(
            observer, date(2026, 7, 7), ZoneInfo("Pacific/Kiritimati")
        )
        assert sun_day.noon.date() == date(2026, 7, 7)
        assert sun_day.sunrise < sun_day.noon < sun_day.sunset


class TestMockupDay:
    """The design screenshot header for 20.6.2025: '4:52 - 20:27 (12:39)'."""

    def test_sunrise_and_sunset_match_screenshot(self, belgrade):
        sun_day = _sun_day(belgrade, date(2025, 6, 20))
        assert sun_day.sunrise.strftime("%H:%M") in {"04:51", "04:52", "04:53"}
        assert sun_day.sunset.strftime("%H:%M") in {"20:26", "20:27", "20:28"}
