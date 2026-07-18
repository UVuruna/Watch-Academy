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
