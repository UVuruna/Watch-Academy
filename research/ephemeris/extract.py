"""DOMY Watch — Anno Lucis ephemeris pipeline.

Extracts, over the full Swiss Ephemeris span (-13000..+17000):
  1. every solstice/equinox  (Sun ecliptic longitude crossing 0/90/180/270)
  2. every Moon phase         (Sun-Moon elongation crossing 0/90/180/270)
into research/ephemeris/events.sqlite, then derives the northern
LIGHT/DARK half-year durations per year and the ANNO LUCIS year — the year
the light half durably overtakes the dark.

Runs are RESUMABLE: each scan records its last-reached JD in a meta table
and skips forward on restart, so an interruption costs nothing. The Moon
scan is the big one (~1.5M events) and logs progress every 1000 events.

Usage (from the venv python):
  python extract.py sun          # ~120k events, minutes
  python extract.py moon         # ~1.5M events, longer; resumable
  python extract.py halves       # season_halves.json from sun_events
  python extract.py anno         # anno_lucis.json from season_halves
  python extract.py plot         # deviation curve PNG
  python extract.py all          # sun -> moon -> halves -> anno -> plot
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
HALVES_JSON = os.path.join(HERE, "season_halves.json")
ANNO_JSON = os.path.join(HERE, "anno_lucis.json")
PLOT_PNG = os.path.join(HERE, "anno_lucis.png")

TYPE_NAMES = {0: "vernal_equinox", 90: "summer_solstice",
              180: "autumn_equinox", 270: "winter_solstice"}
PHASE_NAMES = {0: "new_moon", 90: "first_quarter",
               180: "full_moon", 270: "last_quarter"}

SUSTAIN_YEARS = 100          # a run this long counts as "durable"
SMOOTH_WINDOW = 71           # rolling-mean window (odd), ~lunar-wiggle killer
SOLAR_YEAR_DAYS = 365.24219  # for progress-total estimates
SYNODIC_DAYS = 29.53059


# --------------------------------------------------------------------------
# database helpers
# --------------------------------------------------------------------------

def open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sun_events(
            jd_tt REAL, jd_ut REAL, iso_ut TEXT, type INTEGER);
        CREATE TABLE IF NOT EXISTS moon_events(
            jd_tt REAL, jd_ut REAL, iso_ut TEXT, type INTEGER);
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
# scanning
# --------------------------------------------------------------------------

def scan(conn, table: str, fn, rate: float, total_estimate: int) -> None:
    ec.init()
    jd_end = min(swe.julday(ec.YEAR_END, 1, 1, 0.0, swe.GREG_CAL),
                 ec.SCAN_JD_CEIL)
    resume_key = f"{table}_last_jd"
    done_key = f"{table}_done"

    if meta_get(conn, done_key):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: already complete ({n:,} events)")
        return

    last = meta_get(conn, resume_key)
    if last is not None:
        jd = float(last)
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: resuming at JD {jd:.5f} ({count:,} events already stored)")
    else:
        jd = max(swe.julday(ec.YEAR_START, 1, 1, 0.0, swe.GREG_CAL),
                 ec.SCAN_JD_FLOOR)
        count = 0
        print(f"{table}: starting fresh at JD {jd:.3f}")

    m = ec.Marcher(fn, jd, rate)
    cur = conn.cursor()
    start_t = time.time()
    batch = []

    while True:
        jc, target = m.next_crossing(jd)
        if jc > jd_end:
            break
        jd_u = ec.jd_ut_of(jc)
        batch.append((jc, jd_u, ec.iso_ut(jd_u), target))
        jd = jc
        count += 1

        if count % 1000 == 0:
            cur.executemany(
                f"INSERT INTO {table}(jd_tt,jd_ut,iso_ut,type) VALUES(?,?,?,?)",
                batch)
            batch.clear()
            meta_set(conn, resume_key, jd)
            conn.commit()
            elapsed = time.time() - start_t
            rate_s = count / elapsed if elapsed > 0 else 0
            pct = count / total_estimate * 100
            print(f"  [{elapsed:6.1f}s] {table}: {count:>9,}/{total_estimate:,} "
                  f"({pct:5.1f}%) | {rate_s:6.0f}/s | JD {jd:.1f}", flush=True)

    if batch:
        cur.executemany(
            f"INSERT INTO {table}(jd_tt,jd_ut,iso_ut,type) VALUES(?,?,?,?)",
            batch)
    meta_set(conn, resume_key, jd)
    meta_set(conn, done_key, 1)
    conn.commit()
    print(f"{table}: DONE — {count:,} events in {time.time()-start_t:.1f}s")


def scan_sun(conn):
    est = int((ec.YEAR_END - ec.YEAR_START) * 4)
    scan(conn, "sun_events", ec.sun_lon, ec.SUN_RATE, est)


def scan_moon(conn):
    span_days = (ec.YEAR_END - ec.YEAR_START) * SOLAR_YEAR_DAYS
    est = int(span_days / SYNODIC_DAYS * 4)
    scan(conn, "moon_events", ec.elongation, ec.ELONG_RATE, est)


# --------------------------------------------------------------------------
# season halves
# --------------------------------------------------------------------------

def build_halves(conn) -> None:
    """Northern LIGHT half = vernal equinox -> autumn equinox; DARK half =
    autumn equinox -> next vernal equinox. Durations in TT days (the physical
    intervals; ΔT nearly cancels and clock-time drift does not touch them)."""
    rows = conn.execute(
        "SELECT jd_tt, type, iso_ut FROM sun_events ORDER BY jd_tt").fetchall()
    # Keep only equinoxes (0 vernal, 180 autumn); pull the year off the ISO.
    seq = [(jd, typ, int(iso.split("-")[0].lstrip("+")) if not iso.startswith("-")
            else -int(iso[1:].split("-")[0]))
           for jd, typ, iso in rows if typ in (0, 180)]

    halves = {}
    for i in range(len(seq) - 2):
        jd_v, t_v, year = seq[i]
        jd_a, t_a, _ = seq[i + 1]
        jd_v2, t_v2, _ = seq[i + 2]
        if t_v != 0 or t_a != 180 or t_v2 != 0:
            continue  # not a clean vernal->autumn->vernal triple
        light = jd_a - jd_v
        dark = jd_v2 - jd_a
        halves[str(year)] = [round(light, 6), round(dark, 6)]

    with open(HALVES_JSON, "w") as f:
        json.dump(halves, f, separators=(",", ":"), sort_keys=False)
    print(f"season_halves.json: {len(halves):,} years "
          f"({os.path.getsize(HALVES_JSON)/1e6:.2f} MB)")


# --------------------------------------------------------------------------
# anno lucis
# --------------------------------------------------------------------------

def _rolling_mean(xs, win):
    half = win // 2
    n = len(xs)
    out = [0.0] * n
    for i in range(n):
        a = max(0, i - half)
        b = min(n, i + half + 1)
        out[i] = sum(xs[a:b]) / (b - a)
    return out


def build_anno(conn) -> None:
    with open(HALVES_JSON) as f:
        halves = json.load(f)
    years = sorted(int(y) for y in halves)
    light = [halves[str(y)][0] for y in years]
    dark = [halves[str(y)][1] for y in years]
    diff = [l - d for l, d in zip(light, dark)]           # light minus dark

    smooth = _rolling_mean(diff, SMOOTH_WINDOW)

    # All smoothed negative->positive crossings; pick the one nearest -4000.
    up_crossings = []
    for i in range(1, len(years)):
        if smooth[i - 1] < 0.0 <= smooth[i]:
            # linear interpolation of the crossing year
            y0, y1 = years[i - 1], years[i]
            s0, s1 = smooth[i - 1], smooth[i]
            yc = y0 + (0 - s0) / (s1 - s0) * (y1 - y0)
            up_crossings.append(yc)
    anno_smoothed = min(up_crossings, key=lambda y: abs(y + 4000)) \
        if up_crossings else None

    # First year of a durable raw run of light>dark, searched near the
    # smoothed crossing (forward in time from before it).
    raw_sustained = None
    idx = {y: k for k, y in enumerate(years)}
    for k, y in enumerate(years):
        if diff[k] > 0 and all(
                (k + j < len(years)) and diff[k + j] > 0
                for j in range(SUSTAIN_YEARS)):
            # nearest such run to the smoothed crossing going forward
            if anno_smoothed is None or y >= anno_smoothed - 2000:
                raw_sustained = y
                break

    def bce_ad(y):
        return f"{-y+1} BCE" if y <= 0 else f"{y} CE"

    result = {
        "anno_lucis_year_smoothed": round(anno_smoothed, 1) if anno_smoothed else None,
        "anno_lucis_year_smoothed_label": bce_ad(round(anno_smoothed)) if anno_smoothed else None,
        "anno_lucis_year_raw_sustained": raw_sustained,
        "anno_lucis_year_raw_sustained_label": bce_ad(raw_sustained) if raw_sustained is not None else None,
        "definition": "Northern LIGHT half = vernal->autumn equinox; DARK = the "
                      "rest. Anno Lucis = the year the light half durably outgrows "
                      "the dark (light-dark crosses 0 upward).",
        "smoothing": f"rolling mean, window {SMOOTH_WINDOW} years, over "
                     f"light-dark; negative->positive crossing nearest 4000 BCE.",
        "raw_criterion": f"first year beginning a run of {SUSTAIN_YEARS} "
                         f"consecutive years with light>dark, near the crossing.",
        "all_smoothed_up_crossings": [round(y, 1) for y in up_crossings],
        "delta_t_caveat": "Event YEARS and season DURATIONS are robust; exact "
                          "local clock times over +/-15 millennia are not (the "
                          "Earth-rotation deltaT model carries hours of "
                          "uncertainty).",
        "span_years": [years[0], years[-1]],
        "n_years": len(years),
    }
    with open(ANNO_JSON, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


# --------------------------------------------------------------------------
# plot
# --------------------------------------------------------------------------

def build_plot() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with open(HALVES_JSON) as f:
        halves = json.load(f)
    years = sorted(int(y) for y in halves)
    light = [halves[str(y)][0] for y in years]
    dark = [halves[str(y)][1] for y in years]
    mean_half = sum(light + dark) / (2 * len(years))
    light_dev = [l - mean_half for l in light]
    dark_dev = [d - mean_half for d in dark]

    anno = None
    if os.path.exists(ANNO_JSON):
        anno = json.load(open(ANNO_JSON)).get("anno_lucis_year_smoothed")

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.axhline(0, color="0.4", lw=0.8)
    ax.plot(years, light_dev, color="#E0A200", lw=0.7,
            label="Light half (vernal→autumn) − mean")
    ax.plot(years, dark_dev, color="#6A3D9A", lw=0.7,
            label="Dark half (autumn→vernal) − mean")
    ax.fill_between(years, light_dev, 0, color="#E0A200", alpha=0.18)
    ax.fill_between(years, dark_dev, 0, color="#6A3D9A", alpha=0.18)
    if anno:
        ax.axvline(anno, color="#C81E1E", lw=1.4, ls="--",
                   label=f"Anno Lucis ≈ {anno:.0f}")
    ax.set_xlabel("Astronomical year (0 = 1 BCE)")
    ax.set_ylabel("Half-year duration deviation (days)")
    ax.set_title("DOMY Watch — Northern light/dark half-year across the "
                 "DE441 span (−13000…+17000)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(PLOT_PNG, dpi=130)
    print(f"plot: {PLOT_PNG} ({os.path.getsize(PLOT_PNG)/1e3:.0f} KB)")


# --------------------------------------------------------------------------
# entry
# --------------------------------------------------------------------------

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    conn = open_db()
    if cmd in ("sun", "all"):
        scan_sun(conn)
    if cmd in ("moon", "all"):
        scan_moon(conn)
    if cmd in ("halves", "all"):
        build_halves(conn)
    if cmd in ("anno", "all"):
        build_anno(conn)
    if cmd in ("plot", "all"):
        build_plot()
    conn.close()


if __name__ == "__main__":
    main()
