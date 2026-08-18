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

from config import paths
from core.year_wheel import YearAnchors
from data._io import load_json_checked, year_bounds
from data._shared import Shared


#: THE process-wide seasons repository. Owner ruling 2026-07-28, applied
#: here 2026-08-06: *"svi stvarno čitaju iste stvari identične"*. A
#: `year_anchors(year)` answer is calendar data — the same instants no
#: matter which watch asks or where its observer stands — so N watches
#: holding N parses of the same 476 KB file, and N copies of the same
#: extracted anchors, was pure waste. The LOCATION is what differs
#: between watches, never the astronomy database.
_SHARED = Shared(lambda **kwargs: SeasonsRepository(**kwargs))


def shared_seasons(deep=None) -> "SeasonsRepository":
    """The one seasons repository this process uses. `deep` is honored
    on FIRST call only — the Deep Time pack is itself a process-wide
    singleton (`data.deep_time.shared_deep_time`), so every caller
    passes the same one."""
    return _SHARED.get(deep=deep)


class SeasonsRepository:
    def __init__(self, path: Path | None = None, deep=None):
        self._path = path or (paths.database_dir() / "seasons_utc.json")
        self._cache: dict[int, YearAnchors] = {}
        self._coverage: tuple[int, int] | None = None
        # The optional Deep Time pack (Session 16): the controller
        # detects it ONCE at startup and injects it — years the bundled
        # JSON does not hold chain to it; bundled years stay bundled
        # (the minute-exact tier, bit-identical to before).
        self._deep = deep

    def coverage(self) -> tuple[int, int]:
        """The inclusive (first, last) calendar years the bundled seasons
        database actually holds, read from the data — so Time Travel can
        validate a target BEFORE it reaches the day build (owner
        2026-07-16: a far-year jump used to crash the app).

        Cached like `year_anchors` is (owner bug 2026-08-06): the bounds
        are two integers read from a 476 KB file, and every uncached
        call reparsed the whole thing — twice per Time Travel open, per
        watch."""
        if self._coverage is None:
            self._coverage = year_bounds(
                load_json_checked(self._path, "Seasons database")
            )
        return self._coverage

    def year_anchors(self, year: int) -> YearAnchors:
        """Six anchor instants bracketing `year`, parsed once per year;
        the full dict is discarded after extraction."""
        if year not in self._cache:
            data = load_json_checked(self._path, "Seasons database")
            entry = data.get(str(year))
            if entry is None:
                if self._deep is not None:
                    # Beyond the bundle: the Deep Time pack serves the
                    # year (proxy-shifted where datetime cannot hold it).
                    self._cache[year] = self._deep.year_anchors(year)
                    return self._cache[year]
                low, high = year_bounds(data)
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
