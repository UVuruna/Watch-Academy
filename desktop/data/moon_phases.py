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
from data._shared import Shared


#: THE process-wide moon repository — the twin of
#: `data.seasons.shared_seasons`, and the one that saved the most: the
#: bundled file is 2.9 MB and every watch used to parse its own copy.
_SHARED = Shared(lambda **kwargs: MoonPhaseRepository(**kwargs))


def shared_moon_phases(deep=None) -> "MoonPhaseRepository":
    """The one moon repository this process uses; `deep` is honored on
    FIRST call only (see `data.seasons.shared_seasons`)."""
    return _SHARED.get(deep=deep)


class MoonPhaseRepository:
    def __init__(self, path: Path | None = None, deep=None):
        self._path = path or (paths.database_dir() / "moonPhases_utc.json")
        self._cache: dict[int, MoonWindow] = {}
        self._coverage: tuple[int, int] | None = None
        # The optional Deep Time pack (Session 16) — same chaining rule
        # as SeasonsRepository: bundled years stay bundled, missing
        # years fall through to the pack.
        self._deep = deep

    def coverage(self) -> tuple[int, int]:
        """The inclusive (first, last) calendar years the bundled moon
        database actually holds, read from the data — Time Travel
        intersects this with the seasons coverage to validate a target
        before the day build (owner 2026-07-16).

        Cached like `moon_window` is (owner bug 2026-08-06). This one was
        the app's single most expensive repeat parse: two integers, read
        by reparsing 2.9 MB of JSON, on every call."""
        if self._coverage is None:
            self._coverage = year_bounds(
                load_json_checked(self._path, "Moon phases database")
            )
        return self._coverage

    def moon_window(self, year: int) -> MoonWindow:
        """All principal-phase events of `year` plus its neighbor years,
        so any instant inside `year` has bracketing events."""
        if year not in self._cache:
            data = load_json_checked(self._path, "Moon phases database")
            if str(year) not in data:
                if self._deep is not None:
                    # Beyond the bundle: the Deep Time pack serves the
                    # whole window from one source (never mixed).
                    self._cache[year] = self._deep.moon_window(year)
                    return self._cache[year]
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
