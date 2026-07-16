"""Golden checks for the ephemeris pipeline.

Runs under the pipeline's OWN python (the uv-managed 3.11 venv with
pyswisseph). SKIPS cleanly when events.sqlite — or a given table — is
absent, so a checkout without the (gitignored) database stays green.

    research/ephemeris/.venv/Scripts/python.exe -m pytest test_ephemeris.py
"""

import os
import json
import sqlite3

import pytest
import swisseph as swe

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "events.sqlite")
DB_DIR = os.path.dirname(os.path.dirname(HERE))  # project root
SEASONS = os.path.join(DB_DIR, "Database", "seasons_utc.json")
MOONS = os.path.join(DB_DIR, "Database", "moonPhases_utc.json")

DAY_SECONDS = 86400.0


def _conn():
    if not os.path.exists(DB):
        pytest.skip("events.sqlite absent — run extract.py first")
    return sqlite3.connect(DB)


def _iso_to_jd_ut(iso: str) -> float:
    """Parse a bundled ISO-8601 UTC stamp to a UT Julian Day."""
    date, rest = iso.split("T")
    y, mo, d = (int(x) for x in date.split("-"))
    clock = rest.replace("Z", "").split("+")[0]
    hh, mm, ss = clock.split(":")
    ut = int(hh) + int(mm) / 60 + float(ss) / 3600
    return swe.julday(y, mo, d, ut, swe.GREG_CAL)


def _nearest(conn, table, typ, jd_target):
    row = conn.execute(
        f"SELECT jd_ut FROM {table} WHERE type=? "
        f"ORDER BY ABS(jd_ut-?) LIMIT 1", (typ, jd_target)).fetchone()
    return row[0] if row else None


def _table_has_rows(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] > 0


def _scan_done(conn, table):
    row = conn.execute("SELECT value FROM meta WHERE key=?",
                       (f"{table}_done",)).fetchone()
    return bool(row)


def test_summer_solstice_2026_within_a_minute():
    conn = _conn()
    if not _table_has_rows(conn, "sun_events"):
        pytest.skip("sun_events empty")
    bundled = json.load(open(SEASONS))["2026"]["summer"]["start"]
    jd_ref = _iso_to_jd_ut(bundled)
    jd_got = _nearest(conn, "sun_events", 90, jd_ref)
    err_s = abs(jd_got - jd_ref) * DAY_SECONDS
    assert err_s < 60, f"summer solstice 2026 off by {err_s:.1f}s vs {bundled}"


def test_last_quarter_2026_07_07_agrees():
    conn = _conn()
    if not _scan_done(conn, "moon_events"):
        pytest.skip("moon scan not complete — run extract.py moon to finish")
    # Bundled 2026-07-07 phase is a Third/Last Quarter (elongation 270).
    y = json.load(open(MOONS))["2026"]
    ref_iso = None
    for phases in y.values():
        if not isinstance(phases, dict):
            continue
        for ts, name in phases.items():
            if ts.startswith("2026-07-07"):
                ref_iso = ts
    assert ref_iso, "no bundled 2026-07-07 phase found"
    jd_ref = _iso_to_jd_ut(ref_iso.split(".")[0].replace("+00:00", ""))
    jd_got = _nearest(conn, "moon_events", 270, jd_ref)
    err_s = abs(jd_got - jd_ref) * DAY_SECONDS
    assert err_s < 300, f"last quarter 2026-07-07 off by {err_s:.1f}s"


def test_historical_june_solstice_year_1000():
    """Sanity: the June solstice of CE 1000 lands in June. Literature puts
    it near 1000-06-15 JULIAN, which is ~June 21-22 in the PROLEPTIC
    GREGORIAN calendar revjul(GREG_CAL) returns (the two calendars differ by
    ~6 days at CE 1000)."""
    conn = _conn()
    if not _table_has_rows(conn, "sun_events"):
        pytest.skip("sun_events empty")
    jd_1000 = swe.julday(1000, 6, 20, 12.0, swe.GREG_CAL)
    jd_got = _nearest(conn, "sun_events", 90, jd_1000)
    y, mo, d, _ = swe.revjul(jd_got, swe.GREG_CAL)
    assert (y, mo) == (1000, 6), f"CE1000 June solstice landed {y}-{mo}-{d}"
    assert 20 <= d <= 23, f"CE1000 June solstice day {d} out of expected range"


def test_sun_event_cadence():
    conn = _conn()
    if not _table_has_rows(conn, "sun_events"):
        pytest.skip("sun_events empty")
    n = conn.execute("SELECT COUNT(*) FROM sun_events").fetchone()[0]
    span = 16993 - (-12998)
    per_year = n / span
    assert 3.99 < per_year < 4.01, f"sun cadence {per_year:.3f}/yr (want ~4)"


# --------------------------------------------------------------------------
# Phase II — eclipse catalog golden checks
# --------------------------------------------------------------------------

def _table_exists(conn, table):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,)).fetchone()
    return bool(row)


def _nearest_eclipse(conn, table, jd_target, cols):
    row = conn.execute(
        f"SELECT {cols} FROM {table} ORDER BY ABS(jd_ut-?) LIMIT 1",
        (jd_target,)).fetchone()
    return row


def test_solar_eclipse_1999_08_11_total():
    """The great European total of 1999-08-11: maximum ~11:03 UT, greatest
    eclipse near 45.1N 24.3E (Romania)."""
    conn = _conn()
    if not (_table_exists(conn, "solar_eclipses")
            and _table_has_rows(conn, "solar_eclipses")):
        pytest.skip("solar_eclipses absent — run extract_eclipses.py solar")
    jd_ref = swe.julday(1999, 8, 11, 11.05, swe.GREG_CAL)
    iso, typ, mag, lat, lon, jd = _nearest_eclipse(
        conn, "solar_eclipses", jd_ref, "iso_ut,type,magnitude,lat,lon,jd_ut")
    err_min = abs(jd - jd_ref) * DAY_SECONDS / 60.0
    assert err_min < 5, f"1999 solar off by {err_min:.1f} min ({iso})"
    assert typ == "total", f"1999 solar typed {typ}"
    assert abs(lat - 45.1) < 1.0 and abs(lon - 24.3) < 1.0, \
        f"1999 greatest eclipse at {lat:.2f}N {lon:.2f}E"


def test_solar_eclipse_2024_04_08_total():
    """The North American total of 2024-04-08: maximum ~18:17 UT, greatest
    eclipse near 25.3N 104.1W (Mexico)."""
    conn = _conn()
    if not (_table_exists(conn, "solar_eclipses")
            and _table_has_rows(conn, "solar_eclipses")):
        pytest.skip("solar_eclipses absent — run extract_eclipses.py solar")
    jd_ref = swe.julday(2024, 4, 8, 18.29, swe.GREG_CAL)
    iso, typ, mag, lat, lon, jd = _nearest_eclipse(
        conn, "solar_eclipses", jd_ref, "iso_ut,type,magnitude,lat,lon,jd_ut")
    err_min = abs(jd - jd_ref) * DAY_SECONDS / 60.0
    assert err_min < 5, f"2024 solar off by {err_min:.1f} min ({iso})"
    assert typ == "total", f"2024 solar typed {typ}"
    assert abs(lat - 25.3) < 1.0 and abs(lon - (-104.1)) < 1.0, \
        f"2024 greatest eclipse at {lat:.2f}N {lon:.2f}E"


def test_lunar_eclipse_2019_01_21_total():
    """The total lunar of 2019-01-21: maximum ~05:12 UT, umbral magnitude
    ~1.2."""
    conn = _conn()
    if not (_table_exists(conn, "lunar_eclipses")
            and _table_has_rows(conn, "lunar_eclipses")):
        pytest.skip("lunar_eclipses absent — run extract_eclipses.py lunar")
    jd_ref = swe.julday(2019, 1, 21, 5.20, swe.GREG_CAL)
    iso, typ, mag, jd = _nearest_eclipse(
        conn, "lunar_eclipses", jd_ref, "iso_ut,type,magnitude,jd_ut")
    err_min = abs(jd - jd_ref) * DAY_SECONDS / 60.0
    assert err_min < 5, f"2019 lunar off by {err_min:.1f} min ({iso})"
    assert typ == "total", f"2019 lunar typed {typ}"
    assert 1.1 < mag < 1.3, f"2019 lunar umbral magnitude {mag:.3f}"
