"""Deep Time pack repository — read-only over Database/deep_time.sqlite.

The optional full-span pack (setup/make_deep_time.py; gitignored, ships
only with the FULL installation). Same YearAnchors/MoonWindow shapes as
the bundled repositories, instants proxy-shifted by whole 400-year
Gregorian cycles where datetime cannot hold the real year (see
core/deep_time.py — the shift is exact). Eclipse tables feed the Quick
Jump prev/next navigation, ordered by jd_ut.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from config import constants, paths
from core.clock_state import EclipseEvent
from core.deep_time import julian_day_of, proxy_cycles
from core.moon import MoonWindow
from core.year_wheel import YearAnchors

# sun_events.type is the ecliptic crossing degree: 0 = March equinox,
# 90 = June solstice, 180 = September equinox, 270 = December solstice.
_MARCH, _JUNE, _SEPTEMBER, _DECEMBER = 0, 90, 180, 270


@dataclass(frozen=True)
class DeepEclipse:
    """One catalog eclipse (UT calendar instant in ASTRONOMICAL years)."""

    kind: str                       # "solar" | "lunar"
    year: int
    month: int
    day: int
    second_of_day: int
    type: str                       # total/annular/hybrid/partial/penumbral
    magnitude: float | None
    lat: float | None               # greatest-eclipse point (solar only)
    lon: float | None
    jd_ut: float                    # the catalog ordering key


class DeepTimeRepository:
    def __init__(self, path: Path):
        self._path = path
        # Read-only URI: the pack is immutable app data; a write attempt
        # or a missing file past detection must fail loudly (Rule #1).
        self._con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        row = dict(
            self._con.execute(
                "SELECT key, value FROM meta WHERE key IN "
                "('coverage_first', 'coverage_last')"
            ).fetchall()
        )
        try:
            self._coverage = (int(row["coverage_first"]), int(row["coverage_last"]))
        except KeyError as exc:
            raise ValueError(
                f"Deep Time pack has no coverage meta: {path}"
            ) from exc
        self._anchor_cache: dict[int, YearAnchors] = {}
        self._window_cache: dict[int, MoonWindow] = {}

    @classmethod
    def detect(cls, path: Path | None = None) -> "DeepTimeRepository | None":
        """THE resolution point (owner spec 2026-07-17): the pack file
        exists → repository; absent → None (a supported state — the
        bundled coverage stays authoritative). Called once at startup."""
        path = path or paths.deep_time_path()
        if not path.exists():
            return None
        return cls(path)

    def coverage(self) -> tuple[int, int]:
        """Inclusive (first, last) ASTRONOMICAL years the pack can
        render, read from its meta table (generator-computed from the
        actual event extents — Rule #4)."""
        return self._coverage

    # --- The bundled-shape feeds ----------------------------------------------

    def year_anchors(self, astro_year: int) -> YearAnchors:
        """Six proxy-shifted anchor instants bracketing `astro_year` —
        the same shape SeasonsRepository builds, so build_day_context
        works unchanged."""
        if astro_year not in self._anchor_cache:
            first, last = self._coverage
            if not first <= astro_year <= last:
                raise ValueError(
                    f"Deep Time pack covers {first}-{last}; "
                    f"no entry for {astro_year}"
                )
            shift = proxy_cycles(astro_year) * constants.GREGORIAN_CYCLE_YEARS
            rows = {
                (row[0], row[4]): row
                for row in self._con.execute(
                    "SELECT year, month, day, sod, type FROM sun_events "
                    "WHERE year BETWEEN ? AND ?",
                    (astro_year - 1, astro_year + 1),
                )
            }
            order = (
                (astro_year - 1, _DECEMBER),
                (astro_year, _MARCH),
                (astro_year, _JUNE),
                (astro_year, _SEPTEMBER),
                (astro_year, _DECEMBER),
                (astro_year + 1, _MARCH),
            )
            missing = [key for key in order if key not in rows]
            if missing:
                raise ValueError(
                    f"Deep Time pack is missing sun events {missing} "
                    f"around {astro_year} — regenerate it "
                    f"(setup/make_deep_time.py)"
                )
            self._anchor_cache[astro_year] = YearAnchors(
                year=astro_year + shift,
                instants=tuple(
                    _instant(rows[key], shift) for key in order
                ),
            )
        return self._anchor_cache[astro_year]

    def moon_window(self, astro_year: int) -> MoonWindow:
        """The year ± neighbors' principal phases as (proxy instant,
        cycle fraction) — fraction = crossing degree / 360."""
        if astro_year not in self._window_cache:
            first, last = self._coverage
            if not first <= astro_year <= last:
                raise ValueError(
                    f"Deep Time pack covers {first}-{last}; "
                    f"no entry for {astro_year}"
                )
            shift = proxy_cycles(astro_year) * constants.GREGORIAN_CYCLE_YEARS
            events = tuple(
                (_instant(row, shift), row[4] / 360.0)
                for row in self._con.execute(
                    "SELECT year, month, day, sod, type FROM moon_events "
                    "WHERE year BETWEEN ? AND ? ORDER BY year, month, day, sod",
                    (astro_year - 1, astro_year + 1),
                )
            )
            if not events:
                raise ValueError(
                    f"Deep Time pack has no moon events around {astro_year} "
                    f"— regenerate it (setup/make_deep_time.py)"
                )
            self._window_cache[astro_year] = MoonWindow(events=events)
        return self._window_cache[astro_year]

    # --- The eclipse catalog --------------------------------------------------

    def eclipse_after(self, jd_ut: float, kind: str) -> DeepEclipse | None:
        """The nearest catalog eclipse strictly AFTER a Julian Day —
        None at the catalog edge (the Quick Jump then stays put)."""
        return self._eclipse(jd_ut, kind, "jd_ut > ? ORDER BY jd_ut ASC")

    def eclipse_before(self, jd_ut: float, kind: str) -> DeepEclipse | None:
        """The nearest catalog eclipse strictly BEFORE a Julian Day."""
        return self._eclipse(jd_ut, kind, "jd_ut < ? ORDER BY jd_ut DESC")

    def _eclipse(self, jd_ut: float, kind: str, clause: str) -> DeepEclipse | None:
        if kind == "solar":
            row = self._con.execute(
                f"SELECT jd_ut, year, month, day, sod, type, magnitude, "
                f"lat, lon FROM solar_eclipses WHERE {clause} LIMIT 1",
                (jd_ut,),
            ).fetchone()
        elif kind == "lunar":
            row = self._con.execute(
                f"SELECT jd_ut, year, month, day, sod, type, magnitude, "
                f"NULL, NULL FROM lunar_eclipses WHERE {clause} LIMIT 1",
                (jd_ut,),
            ).fetchone()
        else:
            raise ValueError(f"unknown eclipse kind: {kind!r}")
        if row is None:
            return None
        return DeepEclipse(
            kind=kind, jd_ut=row[0], year=row[1], month=row[2], day=row[3],
            second_of_day=row[4], type=row[5], magnitude=row[6],
            lat=row[7], lon=row[8],
        )

    def eclipses_near(self, now: datetime, cycles: int) -> tuple[EclipseEvent, ...]:
        """The catalog eclipses bracketing `now` (a day-context build
        instant, possibly proxy-shifted) — up to 4 rows: the nearest
        solar/lunar eclipse strictly before and after it, each an
        indexed jd_ut lookup (`eclipse_before`/`eclipse_after`), never a
        table scan. Called ONCE per day-context rebuild; `build_tick_state`
        then only compares instants already in hand — the ONLY DB I/O the
        eclipse display costs. `cycles` un-shifts `now` to the real
        astronomical Julian Day the catalog is ordered by, and re-shifts
        the found instants back into `now`'s own proxy frame so they
        compare directly against every other DayContext datetime."""
        jd = julian_day_of(now, cycles)
        shift = cycles * constants.GREGORIAN_CYCLE_YEARS
        events = []
        for kind in ("solar", "lunar"):
            for eclipse in (
                self.eclipse_before(jd, kind), self.eclipse_after(jd, kind)
            ):
                if eclipse is not None:
                    events.append(_eclipse_event(eclipse, shift))
        return tuple(events)


def _eclipse_event(eclipse: DeepEclipse, shift: int) -> EclipseEvent:
    return EclipseEvent(
        kind=eclipse.kind,
        instant=_instant(
            (eclipse.year, eclipse.month, eclipse.day, eclipse.second_of_day),
            shift,
        ),
        type=eclipse.type,
        magnitude=eclipse.magnitude,
    )


def _instant(row, shift: int) -> datetime:
    """A stored (year, month, day, sod, ...) event row as a tz-aware
    UTC proxy datetime."""
    year, month, day, sod = row[0], row[1], row[2], row[3]
    return datetime(
        year + shift, month, day,
        sod // 3600, (sod % 3600) // 60, sod % 60,
        tzinfo=timezone.utc,
    )
