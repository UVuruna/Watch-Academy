"""Observatory series repository — read-only over the committed bundles
`Database/observatory_seasons.json` and `observatory_eclipses.json`
(setup/make_observatory.py).

These small JSON files ALWAYS ship (committed, unlike the gitignored
deep_time.sqlite), so the Observatory charts never require the Deep Time
pack. The eclipse timeline may ADDITIONALLY use the pack for exact
nearest-eclipse instants when installed; without it only the bundled
density + per-type summary are available.
"""

from config import defaults, paths
from data._io import load_json_checked


class ObservatoryData:
    def __init__(self):
        database = paths.database_dir()
        self._seasons = load_json_checked(
            database / defaults.OBSERVATORY_BUNDLE_SEASONS,
            "Observatory season bundle",
        )
        self._eclipses = load_json_checked(
            database / defaults.OBSERVATORY_BUNDLE_ECLIPSES,
            "Observatory eclipse bundle",
        )
        self._envelope = load_json_checked(
            database / defaults.OBSERVATORY_BUNDLE_ENVELOPE,
            "Observatory Laskar envelope bundle",
        )

    # --- seasons --------------------------------------------------------------

    def season_series(self) -> dict:
        """The four bin-mean season durations plus the two derived
        half-years — parallel arrays over `years` (TT days). Deriving
        light/dark here keeps the file minimal and the linearity
        `light = spring + summer` guaranteed."""
        data = self._seasons
        spring, summer = data["spring"], data["summer"]
        autumn, winter = data["autumn"], data["winter"]
        return {
            "years": data["years"],
            "spring": spring,
            "summer": summer,
            "autumn": autumn,
            "winter": winter,
            "light": [s + u for s, u in zip(spring, summer)],
            "dark": [a + w for a, w in zip(autumn, winter)],
        }

    def season_eras(self) -> dict:
        """The era markers the light−dark chart draws (Anno Lucis, the
        Age of Light span, the starry-season transitions)."""
        return self._seasons["meta"]["eras"]

    def season_span(self) -> tuple[int, int]:
        first, last = self._seasons["meta"]["span_years"]
        return int(first), int(last)

    def light_dark_extrema(self) -> list[tuple[int, float, str]]:
        """Every local peak/trough of light-minus-dark over the whole
        bundled span (Fix round D, Task 3: mark every peak, not just the
        four sealed era marks). `(year, value_days, kind)`, kind is
        "light_peak" or "dark_peak".

        A bare immediate-neighbor comparison flags the bin-mean
        decimation's own rounding noise as dozens of spurious extrema
        clustered around every true peak (measured: 27 "peaks" within a
        few bins of each other, values agreeing to 3 decimals) — so a
        candidate must be the most extreme point within
        OBSERVATORY_EXTREMA_WINDOW_YEARS on each side, and any surviving
        near-duplicates from a flat plateau at the same true extremum
        are merged, keeping the single most extreme point."""
        series = self.season_series()
        years, light, dark = series["years"], series["light"], series["dark"]
        diff = [round(a - b, 4) for a, b in zip(light, dark)]
        n = len(diff)
        if n < 3:
            return []
        bin_width = years[1] - years[0] or 1
        window_bins = max(
            1, round(defaults.OBSERVATORY_EXTREMA_WINDOW_YEARS / bin_width)
        )
        raw: list[tuple[int, float, str]] = []
        for i in range(n):
            lo, hi = max(0, i - window_bins), min(n - 1, i + window_bins)
            neighborhood = diff[lo:hi + 1]
            if diff[i] >= max(neighborhood) and diff[i] > diff[lo] and diff[i] > diff[hi]:
                raw.append((years[i], diff[i], "light_peak"))
            elif diff[i] <= min(neighborhood) and diff[i] < diff[lo] and diff[i] < diff[hi]:
                raw.append((years[i], diff[i], "dark_peak"))
        merge_span = 2 * window_bins * bin_width
        merged: list[tuple[int, float, str]] = []
        for year, value, kind in raw:
            if (merged and merged[-1][2] == kind
                    and year - merged[-1][0] <= merge_span):
                better = (
                    (kind == "light_peak" and value > merged[-1][1])
                    or (kind == "dark_peak" and value < merged[-1][1])
                )
                if better:
                    merged[-1] = (year, value, kind)
            else:
                merged.append((year, value, kind))
        return merged

    # --- eclipses -------------------------------------------------------------

    def eclipse_density(self) -> dict:
        """Eclipse counts per time bucket — the always-available density
        timeline (`years`, `solar`, `lunar`)."""
        data = self._eclipses
        return {
            "years": data["years"],
            "solar": data["solar"],
            "lunar": data["lunar"],
        }

    def eclipse_meta(self) -> dict:
        """Per-century rates, per-type counts, totals and the ΔT caveat."""
        return self._eclipses["meta"]

    # --- Laskar long envelope (Fix round D, Task 4) ----------------------------

    def laskar_envelope(self) -> dict:
        """The La2004 amplitude envelope + the signed oscillation over
        the owner's +/-200,000-year chart window (`years`, `signed_days`,
        `envelope_days`) — charts-only, ROADMAP 15a2."""
        data = self._envelope
        return {
            "years": data["years"],
            "signed_days": data["signed_days"],
            "envelope_days": data["envelope_days"],
        }

    def laskar_envelope_meta(self) -> dict:
        """The DE441 overlap window, the sealed extrema (eccentricity
        minimum etc.) and the honest doctrine caption text."""
        return self._envelope["meta"]
