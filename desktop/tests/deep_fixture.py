"""Small Deep Time fixture pack shared by tests and offscreen probes.

Same schema as setup/make_deep_time.py, hand-sized: a few year spans
with synthetic-but-well-formed events (the interpolators need bracketing
and order, not astronomy) and a handful of eclipses whose jd_ut comes
from the same proleptic Julian Day the app orders by. NEVER the full
92 MB build — the golden runs stay fast and repo-independent.
"""

import sqlite3
from pathlib import Path

from core.deep_time import julian_day

# Populated astronomical years: a BCE deep span, the era edge around
# year 0, and a beyond-bundle CE span. meta declares the OUTER bounds;
# the hole between the spans exercises the loud missing-year error.
FIXTURE_SPANS = ((-4502, -4496), (-2, 3), (2998, 3002))
FIXTURE_COVERAGE = (-4501, 3001)

# (year, month, day, second-of-day, type, magnitude, lat, lon)
FIXTURE_SOLAR = (
    (-4499, 3, 8, 30000, "partial", 0.51, 10.0, 20.0),
    (-4499, 9, 12, 40000, "hybrid", 1.01, -24.1, 117.8),
    (3000, 6, 1, 0, "total", 1.02, 45.0, 20.0),
)
# (year, month, day, second-of-day, type, magnitude)
FIXTURE_LUNAR = (
    (-4499, 4, 2, 20000, "total", 1.20),
    (3000, 1, 10, 5000, "penumbral", 0.90),
)


def build_fixture_pack(path: Path) -> Path:
    """Write the fixture pack at `path` and return it."""
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE sun_events(
            year INTEGER, month INTEGER, day INTEGER, sod INTEGER,
            type INTEGER);
        CREATE TABLE moon_events(
            year INTEGER, month INTEGER, day INTEGER, sod INTEGER,
            type INTEGER);
        CREATE TABLE solar_eclipses(
            jd_ut REAL, year INTEGER, month INTEGER, day INTEGER,
            sod INTEGER, type TEXT, magnitude REAL, lat REAL, lon REAL);
        CREATE TABLE lunar_eclipses(
            jd_ut REAL, year INTEGER, month INTEGER, day INTEGER,
            sod INTEGER, type TEXT, magnitude REAL);
        CREATE INDEX idx_sun_year ON sun_events(year);
        CREATE INDEX idx_moon_year ON moon_events(year);
        CREATE INDEX idx_solar_jd ON solar_eclipses(jd_ut);
        CREATE INDEX idx_lunar_jd ON lunar_eclipses(jd_ut);
        """
    )
    sun, moon = [], []
    for first, last in FIXTURE_SPANS:
        for year in range(first, last + 1):
            sun += [
                (year, 3, 20, 43200, 0),
                (year, 6, 21, 43200, 90),
                (year, 9, 22, 43200, 180),
                (year, 12, 21, 43200, 270),
            ]
            for month in range(1, 13):
                moon += [
                    (year, month, 1, 0, 0),
                    (year, month, 8, 0, 90),
                    (year, month, 15, 0, 180),
                    (year, month, 22, 0, 270),
                ]
    con.executemany("INSERT INTO sun_events VALUES (?,?,?,?,?)", sun)
    con.executemany("INSERT INTO moon_events VALUES (?,?,?,?,?)", moon)
    con.executemany(
        "INSERT INTO solar_eclipses VALUES (?,?,?,?,?,?,?,?,?)",
        [
            (julian_day(y, m, d, sod / 86400.0), y, m, d, sod, kind, mag, lat, lon)
            for y, m, d, sod, kind, mag, lat, lon in FIXTURE_SOLAR
        ],
    )
    con.executemany(
        "INSERT INTO lunar_eclipses VALUES (?,?,?,?,?,?,?)",
        [
            (julian_day(y, m, d, sod / 86400.0), y, m, d, sod, kind, mag)
            for y, m, d, sod, kind, mag in FIXTURE_LUNAR
        ],
    )
    con.executemany(
        "INSERT INTO meta VALUES (?,?)",
        [
            ("schema", "1"),
            ("coverage_first", str(FIXTURE_COVERAGE[0])),
            ("coverage_last", str(FIXTURE_COVERAGE[1])),
        ],
    )
    con.commit()
    con.close()
    return path
