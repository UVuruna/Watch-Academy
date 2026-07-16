"""DOMY Watch — Ephemeris Phase II: the ECLIPSE CATALOG.

Extends the Anno Lucis pipeline (extract.py) with every SOLAR and LUNAR
eclipse across the full Swiss Ephemeris span (-13000..+17000), using the
Swiss Ephemeris' direct global finders:

  - solar: swe.sol_eclipse_when_glob  (walk forward; tret[0] = maximum),
    with swe.sol_eclipse_where at the maximum for the TYPE, the MAGNITUDE
    and the GEOGRAPHIC POINT of greatest eclipse (lat/lon);
  - lunar: swe.lun_eclipse_when (tret[0] = maximum), with
    swe.lun_eclipse_how for the umbral / penumbral MAGNITUDE.

Into the SAME research/ephemeris/events.sqlite as phase I — new tables
`solar_eclipses` and `lunar_eclipses`. Runs are RESUMABLE (each scan
records its last-reached JD_UT in the shared `meta` table and skips forward
on restart) and log progress every 500 events (Rule #10).

The finders work in UNIVERSAL TIME; we store both jd_ut (as returned) and
jd_tt (= jd_ut + deltaT). The ΔT caveat is SHARPER than phase I: THAT an
eclipse happens, and its date/type, are robust across the whole span; WHERE
its shadow path falls (the greatest-eclipse longitude) is only trustworthy
within a few millennia of the present, because hours of ΔT slide the path
in longitude. See ROADMAP queue item 12 Phase II.

Usage (from the venv python):
  python extract_eclipses.py solar     # ~70-75k events, resumable
  python extract_eclipses.py lunar     # ~85-90k events, resumable
  python extract_eclipses.py summary   # eclipses_summary.json
  python extract_eclipses.py all       # solar -> lunar -> summary
"""

import os
import sys
import time
import json
import sqlite3

import swisseph as swe

import ephemeris_common as ec

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "events.sqlite")
SUMMARY_JSON = os.path.join(HERE, "eclipses_summary.json")

FLAGS = swe.FLG_SWIEPH

# UT scan bounds. The finders read the ephemeris a little around each probe,
# so we stay a hair inside the usable data window (the TT floor/ceil from
# phase I; ΔT at the extremes is hours << the safety margin used here).
START_JD_UT = ec.SCAN_JD_FLOOR + 400.0   # ~ -12998, safely inside the floor
END_JD_UT = ec.SCAN_JD_CEIL - 400.0      # ~ 16991, safely inside the ceiling

# A step past each maximum before searching for the next eclipse. The global
# minimum gap between successive solar (or successive lunar) eclipses is a bit
# under a synodic month (~29.5 d), so 3 days clears the just-found event
# without any risk of stepping over the next one.
STEP_PAST_MAX = 3.0

PROGRESS_EVERY = 500

# Solar magnitude and geographic point come from sol_eclipse_where's attr[8]
# (NASA magnitude) and geopos[0]/[1] (central line, or greatest-eclipse point
# for partials). Lunar magnitude comes from lun_eclipse_how attr[0] (umbral)
# for total/partial and attr[1] (penumbral) for penumbral eclipses.


# --------------------------------------------------------------------------
# database
# --------------------------------------------------------------------------

def open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS solar_eclipses(
            jd_tt REAL, jd_ut REAL, iso_ut TEXT,
            type TEXT, magnitude REAL, lat REAL, lon REAL);
        CREATE TABLE IF NOT EXISTS lunar_eclipses(
            jd_tt REAL, jd_ut REAL, iso_ut TEXT,
            type TEXT, magnitude REAL);
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
        """
    )
    return conn


def meta_get(conn, key):
    row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else None


def meta_set(conn, key, value):
    conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)",
                 (key, str(value)))


# --------------------------------------------------------------------------
# type decoding
# --------------------------------------------------------------------------

def solar_type(flag: int) -> str:
    """Decode a sol_eclipse_when_glob return flag to a type name. HYBRID
    (annular-total, bit 32) must be tested BEFORE total/annular."""
    if flag & swe.ECL_ANNULAR_TOTAL:   # == ECL_HYBRID (32)
        return "hybrid"
    if flag & swe.ECL_TOTAL:
        return "total"
    if flag & swe.ECL_ANNULAR:
        return "annular"
    if flag & swe.ECL_PARTIAL:
        return "partial"
    raise RuntimeError(f"unrecognized solar eclipse flag {flag}")


def lunar_type(flag: int) -> str:
    if flag & swe.ECL_TOTAL:
        return "total"
    if flag & swe.ECL_PARTIAL:
        return "partial"
    if flag & swe.ECL_PENUMBRAL:
        return "penumbral"
    raise RuntimeError(f"unrecognized lunar eclipse flag {flag}")


# --------------------------------------------------------------------------
# scanning
# --------------------------------------------------------------------------

def _progress(table, count, est, start_t, jd):
    elapsed = time.time() - start_t
    rate_s = count / elapsed if elapsed > 0 else 0
    pct = count / est * 100 if est else 0.0
    print(f"  [{elapsed:6.1f}s] {table}: {count:>7,}/{est:,} "
          f"({pct:5.1f}%) | {rate_s:6.1f}/s | JD_UT {jd:.1f}", flush=True)


def scan_solar(conn) -> None:
    ec.init()
    table = "solar_eclipses"
    resume_key, done_key = f"{table}_last_jd", f"{table}_done"
    est = 73000

    if meta_get(conn, done_key):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: already complete ({n:,} events)")
        return

    last = meta_get(conn, resume_key)
    if last is not None:
        jd = float(last)
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: resuming at JD_UT {jd:.5f} ({count:,} stored)")
    else:
        jd = START_JD_UT
        count = 0
        print(f"{table}: starting fresh at JD_UT {jd:.3f}")

    cur = conn.cursor()
    start_t = time.time()
    batch = []

    while True:
        res, tret = swe.sol_eclipse_when_glob(jd, FLAGS, 0, False)
        tmax = tret[0]
        if tmax > END_JD_UT:
            break
        typ = solar_type(res)
        rf, geopos, attr = swe.sol_eclipse_where(tmax, FLAGS)
        if rf != 0:
            lon, lat, mag = geopos[0], geopos[1], attr[8]
        else:
            # No point on Earth sees this eclipse as central/greatest at the
            # returned max — store the type/time honestly with NULL place.
            lon = lat = mag = None
        jd_tt = tmax + swe.deltat(tmax)
        batch.append((jd_tt, tmax, ec.iso_ut(tmax), typ, mag, lat, lon))
        jd = tmax + STEP_PAST_MAX
        count += 1

        if count % PROGRESS_EVERY == 0:
            cur.executemany(
                f"INSERT INTO {table}(jd_tt,jd_ut,iso_ut,type,magnitude,lat,lon)"
                f" VALUES(?,?,?,?,?,?,?)", batch)
            batch.clear()
            meta_set(conn, resume_key, jd)
            conn.commit()
            _progress(table, count, est, start_t, jd)

    if batch:
        cur.executemany(
            f"INSERT INTO {table}(jd_tt,jd_ut,iso_ut,type,magnitude,lat,lon)"
            f" VALUES(?,?,?,?,?,?,?)", batch)
    meta_set(conn, resume_key, jd)
    meta_set(conn, done_key, 1)
    conn.commit()
    print(f"{table}: DONE — {count:,} events in {time.time()-start_t:.1f}s")


def scan_lunar(conn) -> None:
    ec.init()
    table = "lunar_eclipses"
    resume_key, done_key = f"{table}_last_jd", f"{table}_done"
    est = 88000

    if meta_get(conn, done_key):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: already complete ({n:,} events)")
        return

    last = meta_get(conn, resume_key)
    if last is not None:
        jd = float(last)
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: resuming at JD_UT {jd:.5f} ({count:,} stored)")
    else:
        jd = START_JD_UT
        count = 0
        print(f"{table}: starting fresh at JD_UT {jd:.3f}")

    cur = conn.cursor()
    start_t = time.time()
    batch = []

    while True:
        res, tret = swe.lun_eclipse_when(jd, FLAGS, 0, False)
        tmax = tret[0]
        if tmax > END_JD_UT:
            break
        typ = lunar_type(res)
        # Umbral magnitude for total/partial; penumbral for penumbral. The
        # 'how' attributes are geocentric here (a dummy geopos suffices for
        # the umbral/penumbral magnitudes, which do not depend on location).
        _, attr = swe.lun_eclipse_how(tmax, [0.0, 0.0, 0.0], FLAGS)
        mag = attr[1] if typ == "penumbral" else attr[0]
        jd_tt = tmax + swe.deltat(tmax)
        batch.append((jd_tt, tmax, ec.iso_ut(tmax), typ, mag))
        jd = tmax + STEP_PAST_MAX
        count += 1

        if count % PROGRESS_EVERY == 0:
            cur.executemany(
                f"INSERT INTO {table}(jd_tt,jd_ut,iso_ut,type,magnitude)"
                f" VALUES(?,?,?,?,?)", batch)
            batch.clear()
            meta_set(conn, resume_key, jd)
            conn.commit()
            _progress(table, count, est, start_t, jd)

    if batch:
        cur.executemany(
            f"INSERT INTO {table}(jd_tt,jd_ut,iso_ut,type,magnitude)"
            f" VALUES(?,?,?,?,?)", batch)
    meta_set(conn, resume_key, jd)
    meta_set(conn, done_key, 1)
    conn.commit()
    print(f"{table}: DONE — {count:,} events in {time.time()-start_t:.1f}s")


# --------------------------------------------------------------------------
# summary
# --------------------------------------------------------------------------

def _iso_year(iso: str) -> int:
    # proleptic-Gregorian ISO from ec.iso_ut: "+YYYYY-MM-..." / "-YYYYY-...".
    # The sign is iso[0]; the year runs until the FIRST '-' separator after it.
    sign = -1 if iso[0] == "-" else 1
    year_digits = iso[1:].split("-", 1)[0]
    return sign * int(year_digits)


def build_summary(conn) -> None:
    out = {}
    span_centuries = (END_JD_UT - START_JD_UT) / 365.24219 / 100.0

    for table, key in (("solar_eclipses", "solar"),
                       ("lunar_eclipses", "lunar")):
        rows = conn.execute(
            f"SELECT type, COUNT(*) FROM {table} GROUP BY type").fetchall()
        counts = {t: n for t, n in rows}
        total = sum(counts.values())
        first = conn.execute(
            f"SELECT iso_ut, type FROM {table} ORDER BY jd_ut LIMIT 1"
        ).fetchone()
        last = conn.execute(
            f"SELECT iso_ut, type FROM {table} ORDER BY jd_ut DESC LIMIT 1"
        ).fetchone()
        out[key] = {
            "counts_by_type": counts,
            "total": total,
            "per_century": round(total / span_centuries, 2),
            "first_event": {"iso_ut": first[0], "type": first[1]} if first else None,
            "last_event": {"iso_ut": last[0], "type": last[1]} if last else None,
        }

    out["combined_total"] = out["solar"]["total"] + out["lunar"]["total"]
    out["span_years"] = [_iso_year(out["solar"]["first_event"]["iso_ut"])
                         if out["solar"]["first_event"] else None,
                         _iso_year(out["solar"]["last_event"]["iso_ut"])
                         if out["solar"]["last_event"] else None]
    out["delta_t_caveat"] = (
        "That an eclipse happens, and its DATE and TYPE, are robust across "
        "the whole -13000..+17000 span (they follow the Sun/Moon geometry "
        "DE441 nails). But the SHADOW-PATH LONGITUDE (the greatest-eclipse "
        "lon for solar eclipses) is only trustworthy within a few millennia "
        "of the present: the Earth-rotation deltaT model carries hours of "
        "uncertainty at the extremes, which slides the sub-solar longitude "
        "by tens of degrees. Latitudes and magnitudes stay reliable.")

    with open(SUMMARY_JSON, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


# --------------------------------------------------------------------------
# entry
# --------------------------------------------------------------------------

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    conn = open_db()
    if cmd in ("solar", "all"):
        scan_solar(conn)
    if cmd in ("lunar", "all"):
        scan_lunar(conn)
    if cmd in ("summary", "all"):
        build_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
