"""Seasons repository — extract-and-discard over seasons_utc.json.

Field semantics (numerically verified): an entry for calendar year N is
self-contained — `start` is the December solstice of year N-1,
spring/summer/autumn `.start` are the instants inside year N,
`winter.start` is the December solstice OF year N, and `end` is the
spring equinox of year N+1. Trap: `winter.duration` describes the winter
that BEGINS the entry, so it must never be paired with `winter.start`.
"""

from datetime import datetime
from pathlib import Path

from config import constants, paths
from core.year_wheel import YearAnchors
from data._io import load_json_checked


class SeasonsRepository:
    def __init__(self, path: Path | None = None):
        self._path = path or (paths.database_dir() / "seasons_utc.json")
        self._cache: dict[int, YearAnchors] = {}

    def year_anchors(self, year: int) -> YearAnchors:
        """Six anchor instants bracketing `year`, parsed once per year;
        the full dict is discarded after extraction."""
        if year not in self._cache:
            data = load_json_checked(self._path, "Seasons database")
            entry = data.get(str(year))
            if entry is None:
                low, high = constants.SEASONS_YEAR_RANGE
                raise ValueError(
                    f"Seasons database covers {low}-{high}; no entry for {year}"
                )
            self._cache[year] = YearAnchors(
                year=year,
                instants=(
                    datetime.fromisoformat(entry["start"]),
                    datetime.fromisoformat(entry["spring"]["start"]),
                    datetime.fromisoformat(entry["summer"]["start"]),
                    datetime.fromisoformat(entry["autumn"]["start"]),
                    datetime.fromisoformat(entry["winter"]["start"]),
                    datetime.fromisoformat(entry["end"]),
                ),
            )
        return self._cache[year]
