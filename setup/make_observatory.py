"""Observatory series generator — one-time, rerunnable (Session 17).

Builds the compact, COMMITTED app-side JSON bundles the Observatory
dialog charts from the research extraction
`research/ephemeris/events.sqlite` (gitignored, ~92 MB — rerun the
research pipeline first if it is missing):

    python setup/make_observatory.py

Unlike the multi-megabyte sqlite packs these bundles are small and
COMMITTED — the Observatory never requires deep_time.sqlite, it reads
only these files (the eclipse timeline may additionally use the Deep
Time pack for exact nearest-eclipse instants when it is installed).

Outputs (into Database/):
  * observatory_seasons.json  — the four northern astronomical season
    durations (spring/summer/autumn/winter, TT days) BIN-MEAN decimated
    over the full usable span, from sun_events. The light/dark
    half-years are spring+summer and autumn+winter (derived in-app, and
    validated here against research/ephemeris/season_halves.json). Carries
    an `eras` block (Anno Lucis + the sealed starry-season transitions)
    from research/ephemeris/anno_lucis.json.
  * observatory_eclipses.json — solar/lunar eclipse COUNTS per time
    bucket over the span (the always-available density timeline) plus the
    per-type summary from research/ephemeris/eclipses_summary.json.

Decimation is bin-mean (the millennial Age-of-Light/Darkness trend is
preserved to well under chart resolution; the raw per-year series lives
in research/ephemeris/season_halves.json). Rule #10 progress logging.
"""

import json
import re
import sqlite3
import sys
import time
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EPHEMERIS = PROJECT_ROOT / "research" / "ephemeris"
SOURCE = EPHEMERIS / "events.sqlite"
SEASON_HALVES = EPHEMERIS / "season_halves.json"
ANNO_LUCIS = EPHEMERIS / "anno_lucis.json"
ECLIPSES_SUMMARY = EPHEMERIS / "eclipses_summary.json"
TARGET_SEASONS = PROJECT_ROOT / "Database" / "observatory_seasons.json"
TARGET_ECLIPSES = PROJECT_ROOT / "Database" / "observatory_eclipses.json"

# Decimation windows (generation params — these files are chart fodder,
# not the measured record; the raw series stays in research/).
SEASON_BIN_YEARS = 20            # bin-mean stride for the season durations
ECLIPSE_BUCKET_YEARS = 500       # count bucket for the eclipse density

# sun_events.type is the ecliptic crossing degree: 0 March equinox,
# 90 June solstice, 180 September equinox, 270 December solstice — so a
# season STARTS at each crossing and runs to the next.
_MARCH, _JUNE, _SEPTEMBER, _DECEMBER = 0, 90, 180, 270
_SEASON_OF_START = {
    _MARCH: "spring",       # March equinox  -> June solstice
    _JUNE: "summer",        # June solstice  -> September equinox
    _SEPTEMBER: "autumn",   # September eq.   -> December solstice
    _DECEMBER: "winter",    # December sol.   -> next March equinox
}
_SEASON_ORDER = ("spring", "summer", "autumn", "winter")

_ISO_YEAR = re.compile(r"^([+-]\d{5})-")
_PROGRESS_EVERY = 200_000


def _year(iso_ut: str) -> int:
    match = _ISO_YEAR.match(iso_ut)
    if match is None:
        raise ValueError(f"unexpected iso_ut format: {iso_ut!r}")
    return int(match.group(1))


def _season_durations(source: sqlite3.Connection) -> dict[int, dict[str, float]]:
    """{astronomical year: {spring,summer,autumn,winter: TT days}} for
    every year whose four crossings AND the next March equinox are
    present (a season is one crossing-to-crossing jd_tt gap)."""
    start = time.time()
    total = source.execute("SELECT COUNT(*) FROM sun_events").fetchone()[0]
    rows = source.execute("SELECT jd_tt, iso_ut, type FROM sun_events ORDER BY jd_tt")
    by_year: dict[int, dict[str, float]] = {}
    prev = None
    done = 0
    for jd_tt, iso_ut, kind in rows:
        if prev is not None:
            p_jd, p_iso, p_kind = prev
            season = _SEASON_OF_START[p_kind]
            by_year.setdefault(_year(p_iso), {})[season] = jd_tt - p_jd
        prev = (jd_tt, iso_ut, kind)
        done += 1
        if done % _PROGRESS_EVERY == 0:
            elapsed = time.time() - start
            rate = done / elapsed if elapsed else 0
            print(
                f"[{elapsed:6.1f}s] seasons: {done:,}/{total:,} "
                f"({done / total * 100:.1f}%) | {rate:,.0f}/sec"
            )
    return {
        year: parts
        for year, parts in by_year.items()
        if all(name in parts for name in _SEASON_ORDER)
    }


def _bin_mean(durations: dict[int, dict[str, float]]) -> dict:
    """Bin-mean the per-year season durations into SEASON_BIN_YEARS
    windows — columnar, one center-year per bin."""
    years = sorted(durations)
    bins: dict[int, list[int]] = {}
    for year in years:
        bins.setdefault(year // SEASON_BIN_YEARS, []).append(year)
    out_years: list[int] = []
    series: dict[str, list[float]] = {name: [] for name in _SEASON_ORDER}
    for key in sorted(bins):
        members = bins[key]
        # Skip a sparse edge bin (fewer than half its years measured).
        if len(members) < SEASON_BIN_YEARS // 2:
            continue
        out_years.append(key * SEASON_BIN_YEARS + SEASON_BIN_YEARS // 2)
        for name in _SEASON_ORDER:
            mean = sum(durations[y][name] for y in members) / len(members)
            series[name].append(round(mean, 4))
    return {"years": out_years, **series}


def _eras() -> dict:
    """The era markers from anno_lucis.json + the owner-sealed starry-
    season transitions (ROADMAP queue #12) — everything the light−dark
    chart marks, sourced from the measured record."""
    anno = json.loads(ANNO_LUCIS.read_text(encoding="utf-8"))
    light = anno["light_era"]
    return {
        "anno_lucis_year": anno["anno_lucis_year"],       # -4078 (4079 BCE)
        "anno_lucis_label": anno["anno_lucis_label"],
        "age_of_light": [light["from"], light["to"]],     # -4078 .. 6423
        "next_anno_lucis": 16429,                          # the next dawn
        # The prior dark era's peak (ROADMAP: -9561 BCE, -9.1 d).
        "dark_peak_prev": -9560,
        # Starry seasons — the sealed transitions inside the eras
        # (ROADMAP queue #12; the owner's "~1000" landed exactly):
        "starry_transitions": {
            "spring_peak": 1000,        # +7.94 d, the light peak
            "summer_end": 6423,         # the Age of Light ends
            "autumn_peak": 10990,       # -5.5 d, the coming dark peak
            "winter_end": 16429,        # the next dawn
        },
    }


def _write_seasons(source: sqlite3.Connection) -> None:
    durations = _season_durations(source)
    binned = _bin_mean(durations)
    span = (min(durations), max(durations))
    # Validate the derived halves against season_halves.json on a couple
    # of raw years (Rule #1 — loud if the geometry drifted).
    halves = json.loads(SEASON_HALVES.read_text(encoding="utf-8"))
    for year in (2026, 0, 1000):
        if str(year) in halves and year in durations:
            parts = durations[year]
            light = parts["spring"] + parts["summer"]
            dark = parts["autumn"] + parts["winter"]
            ref_light, ref_dark = halves[str(year)]
            if abs(light - ref_light) > 1e-3 or abs(dark - ref_dark) > 1e-3:
                raise ValueError(
                    f"season sum disagrees with season_halves.json at {year}: "
                    f"{light:.4f}/{dark:.4f} vs {ref_light}/{ref_dark}"
                )
    payload = {
        "meta": {
            "what": "Northern astronomical season durations (TT days), "
                    "bin-mean decimated; light half = spring+summer, "
                    "dark half = autumn+winter.",
            "source": "research/ephemeris/events.sqlite (DE441 via Swiss "
                      "Ephemeris) sun_events crossing gaps.",
            "bin_years": SEASON_BIN_YEARS,
            "span_years": [span[0], span[1]],
            "n_bins": len(binned["years"]),
            "units": "days",
            "eras": _eras(),
            "built": date.today().isoformat(),
        },
        **binned,
    }
    TARGET_SEASONS.write_text(
        json.dumps(payload, separators=(",", ":")), encoding="utf-8"
    )
    size_kb = TARGET_SEASONS.stat().st_size / 1024
    print(
        f"seasons: {payload['meta']['n_bins']} bins over "
        f"{span[0]}..{span[1]} | {size_kb:.0f} KB -> {TARGET_SEASONS.name}"
    )


def _write_eclipses(source: sqlite3.Connection) -> None:
    summary = json.loads(ECLIPSES_SUMMARY.read_text(encoding="utf-8"))
    buckets: dict[int, dict[str, int]] = {}
    start = time.time()
    for table, kind in (("solar_eclipses", "solar"), ("lunar_eclipses", "lunar")):
        for (iso_ut,) in source.execute(f"SELECT iso_ut FROM {table}"):
            key = _year(iso_ut) // ECLIPSE_BUCKET_YEARS
            buckets.setdefault(key, {"solar": 0, "lunar": 0})[kind] += 1
    years, solar, lunar = [], [], []
    for key in sorted(buckets):
        years.append(key * ECLIPSE_BUCKET_YEARS + ECLIPSE_BUCKET_YEARS // 2)
        solar.append(buckets[key]["solar"])
        lunar.append(buckets[key]["lunar"])
    payload = {
        "meta": {
            "what": "Eclipse COUNTS per time bucket (the always-available "
                    "density timeline) + the per-type summary. Exact "
                    "nearest-eclipse instants need the Deep Time pack.",
            "source": "research/ephemeris/events.sqlite eclipse catalogs.",
            "bucket_years": ECLIPSE_BUCKET_YEARS,
            "span_years": summary["span_years"],
            "per_century": {
                "solar": summary["solar"]["per_century"],
                "lunar": summary["lunar"]["per_century"],
            },
            "counts_by_type": {
                "solar": summary["solar"]["counts_by_type"],
                "lunar": summary["lunar"]["counts_by_type"],
            },
            "totals": {
                "solar": summary["solar"]["total"],
                "lunar": summary["lunar"]["total"],
                "combined": summary["combined_total"],
            },
            "delta_t_caveat": summary["delta_t_caveat"],
            "built": date.today().isoformat(),
        },
        "years": years,
        "solar": solar,
        "lunar": lunar,
    }
    TARGET_ECLIPSES.write_text(
        json.dumps(payload, separators=(",", ":")), encoding="utf-8"
    )
    elapsed = time.time() - start
    size_kb = TARGET_ECLIPSES.stat().st_size / 1024
    print(
        f"eclipses: {len(years)} buckets, {payload['meta']['totals']['combined']:,} "
        f"events [{elapsed:.1f}s] | {size_kb:.0f} KB -> {TARGET_ECLIPSES.name}"
    )


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(
            f"research events database is missing: {SOURCE}\n"
            f"Run the research/ephemeris pipeline first "
            f"(see research/ephemeris/___ephemeris.md)."
        )
    TARGET_SEASONS.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(f"file:{SOURCE.as_posix()}?mode=ro", uri=True)
    _write_seasons(source)
    _write_eclipses(source)
    source.close()
    print("done.")


if __name__ == "__main__":
    sys.exit(main())
