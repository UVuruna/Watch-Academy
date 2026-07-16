"""Fetch the Swiss Ephemeris .se1 data files for the full DE441 span.

Astrodienst's old ftp path now just redirects to the maintained GitHub
mirror (aloistr/swisseph). We enumerate the ephe/ folder there, keep only
the Sun/Moon files (sepl* planets incl. Sun, semo* Moon) that the -13000..
+17000 scan needs, and download each with retries into ./ephe/. Files that
already exist with the right size are skipped, so re-runs are cheap.

Coverage is then VERIFIED by probing swe.calc at both temporal extremes.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
EPHE_DIR = os.path.join(HERE, "ephe")

API_URL = "https://api.github.com/repos/aloistr/swisseph/contents/ephe"
RAW_BASE = "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/"

WANT_PREFIXES = ("sepl", "semo")  # planets (Sun lives here) + Moon


def _get(url: str, retries: int = 5, timeout: int = 60) -> bytes:
    last = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "domy-ephe/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            wait = min(2 ** attempt, 30)
            print(f"  retry {attempt}/{retries} after {wait}s ({e})")
            time.sleep(wait)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def list_files() -> list[dict]:
    data = json.loads(_get(API_URL))
    return [
        {"name": f["name"], "size": f["size"]}
        for f in data
        if f["name"].startswith(WANT_PREFIXES) and f["name"].endswith(".se1")
    ]


def download_all() -> None:
    os.makedirs(EPHE_DIR, exist_ok=True)
    files = list_files()
    total = sum(f["size"] for f in files)
    print(f"{len(files)} files, {total / 1e6:.1f} MB total")
    done = 0
    for i, f in enumerate(sorted(files, key=lambda x: x["name"]), 1):
        dest = os.path.join(EPHE_DIR, f["name"])
        if os.path.exists(dest) and os.path.getsize(dest) == f["size"]:
            done += f["size"]
            continue
        blob = _get(RAW_BASE + f["name"])
        with open(dest, "wb") as out:
            out.write(blob)
        done += f["size"]
        print(f"  [{i:3d}/{len(files)}] {f['name']:14s} "
              f"{f['size'] / 1e6:5.2f} MB  ({done / total * 100:5.1f}% of set)")
    print(f"downloaded/verified {done / 1e6:.1f} MB into {EPHE_DIR}")


def verify_coverage() -> None:
    """Probe the Sun at both extremes; a missing file raises inside swe."""
    import swisseph as swe
    swe.set_ephe_path(EPHE_DIR)
    for year in (-12998, 0, 17000):
        jd = swe.julday(year, 6, 21, 12.0, swe.GREG_CAL)
        xx, err = swe.calc(jd, swe.SUN, swe.FLG_SWIEPH)
        if err and "error" in err.lower():
            raise RuntimeError(f"coverage probe failed at year {year}: {err}")
        print(f"  probe year {year:+6d}: sun lon = {xx[0]:8.4f} deg  OK")
    print("coverage verified across the full span")


if __name__ == "__main__":
    download_all()
    verify_coverage()
