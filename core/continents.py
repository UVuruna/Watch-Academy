"""The Continents theme's Ninth easter-egg law (owner-sealed matrix
2026-07-21; WIDENED to every principal moon phase, owner verdict
2026-07-29 — see `pangea_over_zealandia`).

The Ninth seat of the Continents theme is ZEALANDIA — the literal
Unfound, a true continent 94% drowned, unrecognized until 2017. On days
when the sky is DOING something, PANGEA shows in its place: same story,
deeper time — the supercontinent that was once ALL, split, and by the
supercontinent cycle will return.

The LAW is one boolean over three triggers (an eclipse, a season
turning point, or a PRINCIPAL moon-phase day — full, new, or either
quarter). It is fed by TWO thin wrappers that never recompute astronomy:

- the DIAL reads the flags already on its own `DayContext`
  (`season_events`/`moon_events`, the pre-built anchor lists) and
  `TickState` (`eclipse_event`) — see `*_from_events`;
- the ENCYCLOPEDIA, which only holds a traveled DATE, derives the same
  two calendar flags from the bundled Seasons/Moon repositories — see
  `*_from_repos`.

Pure module (no Qt, no wall clock) — purity-gated by tests/test_purity.
"""

from datetime import date, datetime

from config import constants

# All FOUR principal phases (owner verdict 2026-07-29, widening the
# original New/Full-only trigger): New Moon, First Quarter, Full Moon,
# Third Quarter — the same table `data.moon_phases` normalizes "Last
# Quarter" onto (module docstring: "'Last Quarter' is normalized to
# 'Third Quarter' by the repository on load"). Read from the canon
# fraction table (Rule #4), never hardcoded here.
_PRINCIPAL_PHASE_FRACTIONS = frozenset(constants.MOON_PHASE_FRACTIONS.values())
_PRINCIPAL_PHASE_NAMES = frozenset(constants.MOON_PHASE_FRACTIONS)


def pangea_over_zealandia(
    has_eclipse: bool, is_turning_point: bool, is_principal_phase: bool
) -> bool:
    """THE LAW: Pangea replaces Zealandia on the Ninth seat while the sky
    is doing something on the traveled day — an eclipse near the moment,
    a season turning point (solstice/equinox day), or a PRINCIPAL
    moon-phase day (owner verdict 2026-07-29: every eclipse, the four
    solar turning points, AND every principal phase — full, new, and
    the two quarters, not full/new alone). Otherwise the Ninth stays
    Zealandia. One force, three triggers — the single place the
    easter-egg rule lives.

    THE WIDER FRACTION (recomputed honestly against the bundled 2026
    data, `Database/moonPhases_utc.json`): four principal phases a
    lunation land on 50 distinct calendar days in 2026 (was 25 for
    full/new alone) — with the four turning points that is 54 trigger
    days out of 365, roughly ONE DAY IN SEVEN (was ~one in thirteen,
    the old docstring's "~1/11" ballpark). An eclipse widens it further
    on any day the optional Deep Time pack's catalog names one."""
    return has_eclipse or is_turning_point or is_principal_phase


def date_has_turning_point(
    on_date: date, season_events: tuple[tuple[datetime, str], ...]
) -> bool:
    """A solstice/equinox falls ON `on_date` — the DIAL form, reading the
    `DayContext.season_events` anchor list already built for the day (no
    astronomy recomputed). Instants are UTC; the day is their UTC date,
    the same convention the Earth marker's glow already uses."""
    return any(instant.date() == on_date for instant, _name in season_events)


def date_has_principal_phase(
    on_date: date, moon_events: tuple[tuple[datetime, str], ...]
) -> bool:
    """A PRINCIPAL moon phase — New, First Quarter, Full, or Third
    Quarter (owner verdict 2026-07-29, widened from New/Full alone) —
    falls ON `on_date` — the DIAL form, reading the `DayContext.
    moon_events` principal-instant list (names, not fractions, on this
    side)."""
    return any(
        instant.date() == on_date and name in _PRINCIPAL_PHASE_NAMES
        for instant, name in moon_events
    )


def turning_point_on(on_date: date, seasons_repo) -> bool:
    """A solstice/equinox falls ON `on_date` — the ENCYCLOPEDIA form,
    derived from the bundled Seasons repository for a traveled date.
    `year_anchors(N)` already brackets year N with the December solstices
    of N-1 and N and the spring equinox of N+1, so a single year's
    anchors cover every date inside it; a date outside the bundle's
    coverage answers False (graceful — the deep pack is optional)."""
    try:
        anchors = seasons_repo.year_anchors(on_date.year)
    except (ValueError, KeyError):
        return False
    return any(instant.date() == on_date for instant in anchors.instants)


def principal_phase_on(on_date: date, moon_repo) -> bool:
    """A PRINCIPAL moon phase — New, First Quarter, Full, or Third
    Quarter (owner verdict 2026-07-29, widened from New/Full alone) —
    falls ON `on_date` — the ENCYCLOPEDIA form, derived from the bundled
    Moon repository (`moon_window(N)` carries year N plus its
    neighbours). Fractions on this side (0.0/0.25/0.5/0.75); a date
    outside coverage answers False."""
    try:
        window = moon_repo.moon_window(on_date.year)
    except (ValueError, KeyError):
        return False
    return any(
        instant.date() == on_date and fraction in _PRINCIPAL_PHASE_FRACTIONS
        for instant, fraction in window.events
    )


def ninth_is_pangea_from_events(
    on_date: date,
    season_events: tuple[tuple[datetime, str], ...],
    moon_events: tuple[tuple[datetime, str], ...],
    has_eclipse: bool,
) -> bool:
    """THE DIAL wrapper: is the Ninth Pangea (not Zealandia) right now?
    Built from the render context's OWN pre-computed day flags — the
    eclipse event, the day's season anchors and its moon anchors — never
    recomputing astronomy (owner constraint)."""
    return pangea_over_zealandia(
        has_eclipse,
        date_has_turning_point(on_date, season_events),
        date_has_principal_phase(on_date, moon_events),
    )


def ninth_is_pangea_from_repos(
    on_date: date, seasons_repo, moon_repo, has_eclipse: bool = False
) -> bool:
    """THE ENCYCLOPEDIA wrapper: is the traveled day a Pangea day? Derives
    the two calendar triggers from the bundled Seasons/Moon repositories.
    `has_eclipse` defaults False — the eclipse catalog lives in the
    optional Deep Time pack, so the Encyclopedia's page follows the two
    always-available triggers (the dial, which holds a live eclipse
    event, passes the real flag through `ninth_is_pangea_from_events`)."""
    return pangea_over_zealandia(
        has_eclipse,
        turning_point_on(on_date, seasons_repo),
        principal_phase_on(on_date, moon_repo),
    )
