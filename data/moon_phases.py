"""Moon phase repository — windowed extraction over moonPhases_utc.json.

Year entries mix month dicts ('1'..'12') with year-level aggregate count
keys ('New Moon': 12, ...), so month keys are filtered with isdigit().
Event names use 'Third Quarter' while aggregates say 'Last Quarter' —
normalized on load.
"""

from datetime import datetime
from pathlib import Path

from config import constants, paths
from core.moon import MoonWindow
from data._io import load_json_checked, year_bounds


class MoonPhaseRepository:
    def __init__(self, path: Path | None = None):
        self._path = path or (paths.database_dir() / "moonPhases_utc.json")
        self._cache: dict[int, MoonWindow] = {}

    def coverage(self) -> tuple[int, int]:
        """The inclusive (first, last) calendar years the bundled moon
        database actually holds, read from the data — Time Travel
        intersects this with the seasons coverage to validate a target
        before the day build (owner 2026-07-16)."""
        return year_bounds(load_json_checked(self._path, "Moon phases database"))

    def moon_window(self, year: int) -> MoonWindow:
        """All principal-phase events of `year` plus its neighbor years,
        so any instant inside `year` has bracketing events."""
        if year not in self._cache:
            data = load_json_checked(self._path, "Moon phases database")
            if str(year) not in data:
                low, high = year_bounds(data)
                raise ValueError(
                    f"Moon phases database covers {low}-{high}; no entry for {year}"
                )
            events: list[tuple[datetime, float]] = []
            for neighbor in (year - 1, year, year + 1):
                entry = data.get(str(neighbor))
                if entry is None:
                    continue  # documented: coverage edge years use a 2-year window
                for month_key, month_events in entry.items():
                    if not month_key.isdigit():
                        continue  # year-level aggregate count keys
                    for iso, name in month_events.items():
                        if name == "Last Quarter":
                            name = "Third Quarter"
                        events.append(
                            (
                                datetime.fromisoformat(iso),
                                constants.MOON_PHASE_FRACTIONS[name],
                            )
                        )
            events.sort(key=lambda event: event[0])
            self._cache[year] = MoonWindow(events=tuple(events))
        return self._cache[year]
