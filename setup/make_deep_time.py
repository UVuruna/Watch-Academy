"""Deep Time pack generator — one-time, rerunnable (Session 16).

Builds the compact APP-SIDE database `Database/deep_time.sqlite` from
the research extraction `research/ephemeris/events.sqlite` (gitignored,
~92 MB — rerun the research pipeline first if it is missing):

    python setup/make_deep_time.py

Contents over the full usable span (read from the data, ~−12998…+16992):
  * sun_events     — every solstice/equinox instant (type = crossing
                     degree: 0 March eq, 90 June sol, 180 Sept eq,
                     270 Dec sol)
  * moon_events    — every principal moon phase instant (type =
                     elongation degree: 0 new, 90 first quarter,
                     180 full, 270 third quarter)
  * solar_eclipses — instant, type, magnitude, greatest-eclipse lat/lon
  * lunar_eclipses — instant, type, magnitude
  * meta           — coverage_first/coverage_last (the years the app may
                     render: both tables' extents trimmed by one year so
                     season anchors and moon windows always have their
                     neighbors), source, build stamp, row counts

Instants are stored as ASTRONOMICAL calendar fields (year, month, day,
second-of-day, UT) because datetime/fromisoformat cannot carry negative
years; eclipses also keep jd_ut as the monotonic ordering key. The pack
is gitignored (~60–90 MB) and ships only with the FULL installation
(M7); the app detects it at startup via config.paths.deep_time_path().
"""

import re
import sqlite3
import sys
import time
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "research" / "ephemeris" / "events.sqlite"
TARGET = PROJECT_ROOT / "Database" / "deep_time.sqlite"

# The research pipeline stamps proleptic-Gregorian UT instants as
# "±YYYYY-MM-DDTHH:MM:SSZ" (signed, zero-padded years).
_ISO = re.compile(r"^([+-]\d{5})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)Z$")

_PROGRESS_EVERY = 100_000            # rows between progress lines (Rule #10)


def _parse(iso_ut: str) -> tuple[int, int, int, int]:
    """(astronomical year, month, day, second-of-day) of a research
    ISO stamp — loud on any drift in the pipeline's format (Rule #1)."""
    match = _ISO.match(iso_ut)
    if match is None:
        raise ValueError(f"unexpected iso_ut format: {iso_ut!r}")
    year, month, day, hh, mm, ss = (int(part) for part in match.groups())
    return year, month, day, hh * 3600 + mm * 60 + ss


def _copy(source, target, select, insert, transform, label, total):
    start = time.time()
    batch = []
    done = 0
    for row in source.execute(select):
        batch.append(transform(row))
        done += 1
        if len(batch) >= 10_000:
            target.executemany(insert, batch)
            batch.clear()
        if done % _PROGRESS_EVERY == 0:
            elapsed = time.time() - start
            rate = done / elapsed if elapsed > 0 else 0
            print(
                f"[{elapsed:6.1f}s] {label}: {done:,}/{total:,} "
                f"({done / total * 100:.1f}%) | {rate:,.0f}/sec"
            )
    if batch:
        target.executemany(insert, batch)
    print(f"{label}: {done:,} rows copied")
    return done


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(
            f"research events database is missing: {SOURCE}\n"
            f"Run the research/ephemeris pipeline first "
            f"(see research/ephemeris/___ephemeris.md)."
        )
    source = sqlite3.connect(f"file:{SOURCE.as_posix()}?mode=ro", uri=True)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        TARGET.unlink()                  # rerunnable: rebuild from scratch
    target = sqlite3.connect(TARGET)
    target.executescript(
        """
        PRAGMA page_size = 4096;
        PRAGMA journal_mode = OFF;
        PRAGMA synchronous = OFF;
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
        """
    )

    def event_row(row):
        year, month, day, sod = _parse(row[0])
        return (year, month, day, sod, int(row[1]))

    def solar_row(row):
        year, month, day, sod = _parse(row[1])
        return (row[0], year, month, day, sod, row[2], row[3], row[4], row[5])

    def lunar_row(row):
        year, month, day, sod = _parse(row[1])
        return (row[0], year, month, day, sod, row[2], row[3])

    counts = {}
    for table, select, insert, transform in (
        (
            "sun_events",
            "SELECT iso_ut, type FROM sun_events ORDER BY jd_ut",
            "INSERT INTO sun_events VALUES (?,?,?,?,?)",
            event_row,
        ),
        (
            "moon_events",
            "SELECT iso_ut, type FROM moon_events ORDER BY jd_ut",
            "INSERT INTO moon_events VALUES (?,?,?,?,?)",
            event_row,
        ),
        (
            "solar_eclipses",
            "SELECT jd_ut, iso_ut, type, magnitude, lat, lon "
            "FROM solar_eclipses ORDER BY jd_ut",
            "INSERT INTO solar_eclipses VALUES (?,?,?,?,?,?,?,?,?)",
            solar_row,
        ),
        (
            "lunar_eclipses",
            "SELECT jd_ut, iso_ut, type, magnitude "
            "FROM lunar_eclipses ORDER BY jd_ut",
            "INSERT INTO lunar_eclipses VALUES (?,?,?,?,?,?,?)",
            lunar_row,
        ),
    ):
        total = source.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        counts[table] = _copy(
            source, target, select, insert, transform, table, total
        )

    # Coverage = the years the APP may render, read from the data
    # (Rule #4). A year Y needs: the December solstice of Y−1 and the
    # March equinox of Y+1 (season anchors), and the JANUARY–FEBRUARY
    # moon events of Y−1 and Y+1 (the Chinese New Year cusp — verified
    # trap 2026-07-17: the scan starts mid-year, so the first moon year
    # has no January and the naive extents-trimmed-by-one bound let the
    # edge year crash the day build). A March event in a year proves
    # its January–February are fully scanned.
    def one(sql):
        return target.execute(sql).fetchone()[0]

    coverage_first = max(
        one("SELECT MIN(year) FROM sun_events WHERE type = 270") + 1,
        one("SELECT MIN(year) FROM moon_events WHERE month = 1") + 1,
    )
    coverage_last = min(
        one("SELECT MAX(year) FROM sun_events WHERE type = 270"),
        one("SELECT MAX(year) FROM sun_events WHERE type = 0") - 1,
        one("SELECT MAX(year) FROM moon_events WHERE month = 3") - 1,
    )

    print("indexing...")
    target.executescript(
        """
        CREATE INDEX idx_sun_year ON sun_events(year);
        CREATE INDEX idx_moon_year ON moon_events(year);
        CREATE INDEX idx_solar_jd ON solar_eclipses(jd_ut);
        CREATE INDEX idx_lunar_jd ON lunar_eclipses(jd_ut);
        """
    )
    target.executemany(
        "INSERT INTO meta VALUES (?, ?)",
        [
            ("schema", "1"),
            ("coverage_first", str(coverage_first)),
            ("coverage_last", str(coverage_last)),
            ("source", "research/ephemeris/events.sqlite (DE441 via Swiss Ephemeris)"),
            ("built", date.today().isoformat()),
            *((f"count_{table}", str(count)) for table, count in counts.items()),
        ],
    )
    target.commit()
    print("vacuum...")
    target.execute("VACUUM")
    target.close()
    size_mb = TARGET.stat().st_size / 1_048_576
    print(
        f"done: {TARGET}\n"
        f"coverage {coverage_first}..{coverage_last} | "
        + " | ".join(f"{table} {count:,}" for table, count in counts.items())
        + f" | {size_mb:.1f} MB"
    )


if __name__ == "__main__":
    sys.exit(main())
