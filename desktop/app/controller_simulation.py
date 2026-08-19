"""The moment the watch is showing when it is not now.

A mixin of [WatchController](controller.md): the jump arithmetic
(`_compute_jump` — every Quick Jump kind, unit step, eclipse and
sun/moon phase filter), the simulation lifecycle (`_start_simulation` /
`_end_simulation`) and the Time Travel dialog that drives them. It reads
the same repositories the live tick does, so a traveled dial and a live
dial are never two code paths.
"""

import re
from datetime import date, datetime, timedelta, timezone
from time import monotonic
from zoneinfo import ZoneInfo

import astral

from app.time_travel import TimeTravelDialog
from config import constants, defaults, shortcuts
from core.clock_state import build_tick_state
from core.continents import date_is_solstice
from core.deep_time import (
    canonical_proxy, julian_day_of, proxy_cycles, real_year, shift_calendar,
)

# FAST TRAVEL (R5b round, owner spec sealed 2026-07-21): the Sun/Moon
# Quick Jump kinds gained an optional PHASE FILTER suffix so the SAME
# `_compute_jump` branch that already answers "next_sun"/"prev_sun"/
# "next_moon"/"prev_moon" (any turning point/phase — the Time Travel
# dialog's own rows, unchanged) also answers the narrower
# "next_sun_solstice"/"next_sun_equinox"/"next_moon_new"/
# "next_moon_full"/"next_moon_quarter" kinds `defaults.
# FAST_TRAVEL_THEMES` builds its `jump_stem`s from — one path, not a
# second copy (Rule #5).
_SUN_MOON_JUMP_PATTERN = re.compile(
    r"^(next|prev)_(sun|moon)(?:_(solstice|equinox|new|full|quarter))?$"
)
# Index into `SeasonsRepository.year_anchors().instants` (the 6 anchors,
# `sky.YEAR_ANCHOR_ANGLES` order: prev Dec solstice, spring
# equinox, summer solstice, autumn equinox, this Dec solstice, next
# spring equinox) — solstices sit at the EVEN indices, equinoxes at the
# ODD.
_SOLSTICE_ANCHOR_INDICES = (0, 2, 4)
_EQUINOX_ANCHOR_INDICES = (1, 3, 5)
# MoonWindow events carry the phase as a FRACTION
# (sky.MOON_PHASE_FRACTIONS): New 0.0, First Quarter 0.25, Full
# 0.5, Third Quarter 0.75.
_QUARTER_MOON_FRACTIONS = (0.25, 0.75)


def _filtered_sun_anchors(
    instants: tuple[datetime, ...], phase_filter: str | None
) -> tuple[datetime, ...]:
    """The year's 6 season anchors, narrowed to solstices/equinoxes only
    when `phase_filter` asks for it — None (the plain "any turning
    point" row) keeps all six, unchanged from before this filter
    existed."""
    if phase_filter == "solstice":
        return tuple(instants[i] for i in _SOLSTICE_ANCHOR_INDICES)
    if phase_filter == "equinox":
        return tuple(instants[i] for i in _EQUINOX_ANCHOR_INDICES)
    return instants


def _filtered_moon_events(
    events: tuple[tuple[datetime, float], ...], phase_filter: str | None
) -> tuple[datetime, ...]:
    """The year's principal-phase events, narrowed to New/Full/Quarter
    only when `phase_filter` asks for it — None keeps every phase,
    unchanged from before this filter existed."""
    if phase_filter == "new":
        return tuple(when for when, fraction in events if fraction == 0.0)
    if phase_filter == "full":
        return tuple(when for when, fraction in events if fraction == 0.5)
    if phase_filter == "quarter":
        return tuple(
            when
            for when, fraction in events
            if fraction in _QUARTER_MOON_FRACTIONS
        )
    return tuple(when for when, _fraction in events)


class _TimeTravelMixin:
    """TimeTravelMixin — see the module docstring."""

    def _simulated_moment(self) -> datetime:
        """The travel window's FLOWING clock (owner spec 2026-08-11):
        the landed moment plus the real seconds since the jump — so a
        traveled dial shows a running transition (day into night, an
        eclipse closing) instead of a frozen frame. Callers must have
        checked `self._simulation is not None`."""
        moment, _observer = self._simulation
        return moment + timedelta(seconds=monotonic() - self._sim_started)

    def _active_simulation_or_now(self) -> tuple[datetime, astral.Observer, int]:
        """The (moment, observer, cycles) every LIVE travel path chains
        from (owner spec, R5b round: "each jump starts from the active
        simulation") — the running simulation while one is live, else
        the real wall clock at the home observer. Used directly by
        every keyboard Fast Travel/Location shortcut
        (`_jump_to_place`/`_cycle_jump_city`/`_step_fast_travel`) and, by
        `_open_time_travel` below, to seed the DIALOG'S own fields —
        the SAME rule this round factored out of that seeding (Rule #5:
        one source for "what does 'right now' mean while travelling")."""
        if self._simulation is not None:
            return (
                self._simulated_moment(), self._simulation[1],
                self._sim_cycles,
            )
        return datetime.now(self._tz), self._observer, 0

    def _apply_jump(
        self, moment: datetime, observer, cycles: int, kind: str,
        city: dict | None = None,
    ) -> None:
        """One `_compute_jump` step, applied straight to the LIVE dial
        (`_start_simulation`) instead of a dialog draft — the shared
        tail every keyboard travel shortcut uses. A clamp (`None`) is a
        silent no-op, matching every other Quick Jump caller. Flashes
        the landed-on place (R-30) when `kind` actually changed the
        location — never on a clamp."""
        result = self._compute_jump(moment, observer, cycles, kind, city)
        if result is not None:
            self._start_simulation(*result)
            self._flash_jump_location(kind, city)

    def _open_time_travel(self) -> None:
        # A running simulation SEEDS the dialog (owner 2026-07-14):
        # after a quick jump the offered coordinates and moment are
        # the simulated ones, not the home city's.
        moment, observer, cycles = self._active_simulation_or_now()
        initial = moment.astimezone(self._tz).replace(tzinfo=None)
        latitude, longitude = observer.latitude, observer.longitude
        dialog = TimeTravelDialog(
            latitude, longitude,
            overlay=self._translation_overlay,
            initial_moment=initial,
            initial_cycles=cycles,
            coverage=self._travel_coverage(),
            core_coverage=self._bundled_coverage(),
            era_notation=self._settings.era_notation,
            show_era_suffix=self._settings.show_era_suffix,
            third_era=self._settings.third_era,
            deep_pack=self._deep is not None,
            # ITEM 3A (R5 MENU REWORK): the dialog's own Quick Jump
            # rows — the old deep submenu chain's replacement.
            jump_callback=self._dialog_jump,
            jump_cities=self._settings.jump_cities,
        )
        result = dialog.exec()
        if result == TimeTravelDialog.RETURN_TO_NOW:
            self._end_simulation()
            return
        if result != TimeTravelDialog.DialogCode.Accepted:
            return
        moment = dialog.moment().replace(tzinfo=self._tz)
        observer = astral.Observer(
            latitude=dialog.latitude(), longitude=dialog.longitude()
        )
        self._start_simulation(moment, observer, dialog.cycles())

    def _verses_in_the_open(self) -> bool:
        """THE POEM'S OWN DAYS (owner decree 2026-08-11): True when the
        DISPLAYED day (the traveled day while a simulation runs, else
        today) is a summer or winter solstice — the only days the Four
        Greetings show without the cipher. Reads the day context's own
        season anchors; no day built yet means no poem, never a crash."""
        if self._day is None:
            return False
        return date_is_solstice(
            self._effective_travel_date(), self._day.season_events
        )

    def _effective_travel_date(self) -> date:
        """The date driving the poles' Quick Jump light/dark glyph
        (owner revocation, fix round E, 2026-07-19, slika 6): the
        DISPLAYED moment — the Time Travel traveled date while a
        simulation runs, else today's wall-clock date."""
        if self._simulation is not None:
            return self._simulated_moment().date()
        return date.today()

    def _effective_is_daylight(self) -> bool:
        """THE DOUBLE NINTH LAW's daynight state (owner decree
        2026-07-29): the SAME (moment, observer) `_on_tick` already
        resolves — a running Time Travel simulation, else the wall
        clock — fed through `build_tick_state`, the identical function
        every ordinary tick calls; `self._day.sun` is already built, so
        this reads it rather than recomputing sunrise/sunset. True
        (day) before the first day build, matching every other
        graceful-absent default here."""
        if self._day is None:
            return True
        now = (
            self._simulated_moment() if self._simulation is not None
            else datetime.now(self._tz)
        )
        return build_tick_state(now, self._day).is_daylight

    def _end_simulation(self) -> None:
        """NOW (owner 2026-07-15): back to the present immediately —
        the running simulation ends and the dial rebuilds from the
        real wall clock; a no-op when nothing is simulated. Also
        restores the tray tooltip/menu TITLE's location word (R-31) to
        the home city — a jump's `_flash_location` moved it away from
        `settings.city_name` without ever touching the home Settings,
        so ending the simulation must move it back the same way."""
        self._simulation = None
        self._sim_cycles = 0
        self._day = None
        # HOME NAMES ITSELF TOO (owner order 2026-08-12: "Ctrl+Home
        # should write the location just like Ctrl+arrow or Ctrl+0 for
        # Greenwich"). Every OTHER way of changing the observer flashed
        # where it landed; the way BACK was the one silent one, so the
        # reader was left to infer the return from the dial alone.
        # `_flash_location` is the same single door those paths use — it
        # restores `_active_location_name`, the Location crown's display
        # text, the tray title and the skin in one call, which is exactly
        # what this method used to open-code.
        self._flash_location(
            self._settings.place.name, self._settings.place.path,
            self._settings.place.timezone,
        )
        self._on_tick(clock_jumped=False)

    def _start_simulation(self, moment: datetime, observer, cycles: int = 0) -> None:
        """Render the (moment, observer) situation for the standard
        Time Travel minute, then return to the present — any new
        travel restarts the minute (owner 2026-07-14). The moment is
        FIRST re-canonicalized (Session 16): a jump or a timezone
        conversion may have drifted the proxy year across a canonical
        window edge, and the repositories answer in the canonical frame
        — one enforcement point keeps every path consistent. Final
        coverage backstop (owner 2026-07-16): a moment the databases
        cannot render is refused here, so no travel path can reach the
        day build's die-visibly box — the dialog already explained why;
        a quick jump simply stays put."""
        astro_year = real_year(moment.year, cycles)
        canonical = proxy_cycles(astro_year)
        if canonical != cycles:
            moment = moment.replace(
                year=astro_year + canonical * constants.GREGORIAN_CYCLE_YEARS
            )
            cycles = canonical
        first, last = self._travel_coverage()
        if not (first <= astro_year <= last):
            return
        self._simulation = (moment, observer)
        self._sim_cycles = cycles
        self._simulation_ends = monotonic() + shortcuts.TIME_TRAVEL_DURATION_S
        # The travel minute FLOWS from the landed instant (owner spec
        # 2026-08-11) — anchor the wall clock here.
        self._sim_started = monotonic()
        self._day = None                    # rebuild with the simulated situation
        self._on_tick(clock_jumped=False)

    # Quick Jump unit table (owner slika 12): kind -> (unit, sign).
    _UNIT_JUMPS = {
        "next_day": ("day", 1), "prev_day": ("day", -1),
        "next_month": ("month", 1), "prev_month": ("month", -1),
        "next_year": ("year", 1), "prev_year": ("year", -1),
        "next_century": ("century", 1), "prev_century": ("century", -1),
        "next_millennium": ("millennium", 1), "prev_millennium": ("millennium", -1),
    }
    # THE TYPED ECLIPSE JUMPS (owner selector spec 2026-08-11, "sve
    # verzije ili svaka redom"): the bare kinds stay ("any"), and every
    # catalog TYPE gets its own kind — total/annular/partial/hybrid for
    # solar, total/partial/penumbral for lunar — one regex, one branch.
    _ECLIPSE_JUMP_PATTERN = re.compile(
        r"^(next|prev)_(solar|lunar)_eclipse"
        r"(?:_(total|annular|partial|hybrid|penumbral))?$"
    )
    # THE TIME-UNIT JUMPS (owner spec 2026-08-11, category "Time"):
    # hour/minute/second steps — plain timedeltas on the flowing moment.
    _TIME_JUMPS = {
        "next_hour": ("hour", 1), "prev_hour": ("hour", -1),
        "next_minute": ("minute", 1), "prev_minute": ("minute", -1),
        "next_second": ("second", 1), "prev_second": ("second", -1),
    }

    def _compute_jump(
        self, base_moment: datetime, base_observer, base_cycles: int,
        kind: str, city: dict | None = None,
    ) -> tuple[datetime, "astral.Observer", int] | None:
        """The PURE computation behind every jump preset (owner rounds
        2026-07-14; Session 16 rework, owner slika 12; EXTRACTED from
        the old immediate-jump `_quick_jump`, R5 MENU REWORK — the
        Quick Jump submenu itself died with the deep-nesting complaint,
        `UV/DESIGN/Meni One over Another.png`, Rule #6). Returns the
        LANDED (moment, observer, cycles) or None when the jump clamps
        at the active coverage edge (a no-op, never a crash) — the
        caller decides what to DO with the result: `_dialog_jump`
        applies it to the Time Travel window's own fields (chaining
        from ITS current state, never the live simulation), nothing
        else calls this anymore now that the immediate-apply menu path
        is gone. Places are REAL coordinates with their REAL clocks:
        Greenwich and the user's Quick Jump cities in their own
        timezones, the poles on UTC. Deep travel runs in the 400-year
        proxy frame — event instants are REBASED into the caller's
        frame before comparing, and the caller re-canonicalizes the
        landing (`_start_simulation` for a live jump; `_dialog_jump`
        for a dialog-local one)."""
        moment, observer, cycles = base_moment, base_observer, base_cycles
        first, last = self._travel_coverage()
        astro_base = real_year(base_moment.year, base_cycles)
        sun_moon_match = _SUN_MOON_JUMP_PATTERN.match(kind)
        if sun_moon_match:
            direction, body, phase_filter = sun_moon_match.groups()
            # Gather turning points only from years the databases cover, so
            # the anchor lookup itself never steps off the edge (owner
            # 2026-07-16). year_anchors(N) already reaches into N-1/N+1.
            # Each year answers in ITS canonical proxy frame — candidates
            # are compared on the frame-free JULIAN DAY (rebasing the
            # datetimes themselves would overflow years 0/10000 at the
            # datetime boundaries) and the landing re-canonicalizes.
            years = [
                year
                for year in (astro_base - 1, astro_base, astro_base + 1)
                if first <= year <= last
            ]
            candidates: dict[float, tuple[datetime, int]] = {}
            for year in years:
                cycles_of_year = proxy_cycles(year)
                if body == "sun":
                    source = _filtered_sun_anchors(
                        self._seasons.year_anchors(year).instants, phase_filter
                    )
                else:
                    source = _filtered_moon_events(
                        self._moon_phases.moon_window(year).events, phase_filter
                    )
                for when in source:
                    candidates[julian_day_of(when, cycles_of_year)] = (
                        when, cycles_of_year,
                    )
            base_jd = julian_day_of(base_moment, base_cycles)
            # The simulated moment is floored to the minute, so the
            # landed-on instant lies seconds AHEAD of it — the strict
            # one-minute guard keeps "next" from re-picking it.
            if direction == "next":
                order = sorted(jd for jd in candidates if jd > base_jd + 1.0 / 1440.0)
            else:
                order = sorted(
                    (jd for jd in candidates if jd < base_jd), reverse=True
                )
            for jd in order:
                when, cycles_of_year = candidates[jd]
                proxy, cycles = canonical_proxy(
                    real_year(when.year, cycles_of_year), when.month,
                    when.day, when.hour, when.minute,
                )
                landing = proxy.replace(tzinfo=timezone.utc).astimezone(
                    base_moment.tzinfo
                )
                # Never LAND on an instant whose LOCAL year the databases
                # can't render — the day build would die visibly.
                if first <= real_year(landing.year, cycles) <= last:
                    moment = landing
                    break
            else:
                return None             # clamp: already at the coverage edge
        elif eclipse_match := self._ECLIPSE_JUMP_PATTERN.match(kind):
            # The eclipse navigation (owner 2026-07-16, ROADMAP 12/14a;
            # typed per the 2026-08-11 selector spec) — fed by the Deep
            # Time pack; the caller grays its entry without it, this
            # guard is the belt to that suspender.
            if self._deep is None:
                return None
            direction_word, eclipse_kind, eclipse_type = eclipse_match.groups()
            jd = julian_day_of(base_moment, base_cycles)
            if direction_word == "next":
                # The same one-minute guard as the event jumps: the
                # landed minute-floored moment must not re-pick itself.
                event = self._deep.eclipse_after(
                    jd + 1.0 / 1440.0, eclipse_kind, eclipse_type,
                )
            else:
                event = self._deep.eclipse_before(jd, eclipse_kind, eclipse_type)
            if event is None or not first <= event.year <= last:
                return None             # clamp: catalog edge
            proxy, cycles = canonical_proxy(
                event.year, event.month, event.day,
                event.second_of_day // 3600,
                (event.second_of_day % 3600) // 60,
            )
            moment = proxy.replace(tzinfo=timezone.utc).astimezone(
                base_moment.tzinfo
            )
        elif kind in self._TIME_JUMPS:
            # Hour / Minute / Second (owner spec 2026-08-11): a plain
            # timedelta on the base moment. Returned WITHOUT the
            # minute-flooring tail — flooring a one-second step would
            # erase it — and the seconds keep flowing either way.
            unit, sign = self._TIME_JUMPS[kind]
            step = {
                "hour": timedelta(hours=1),
                "minute": timedelta(minutes=1),
                "second": timedelta(seconds=1),
            }[unit]
            moment = base_moment + sign * step
            if not first <= real_year(moment.year, cycles) <= last:
                return None
            return moment.replace(microsecond=0), observer, cycles
        elif kind in self._UNIT_JUMPS:
            # Year · Month · Day and Century · Millennium (owner slika
            # 12): calendar arithmetic on the REAL astronomical date —
            # the wall time stays, day clamps to the target month.
            unit, sign = self._UNIT_JUMPS[kind]
            if unit == "day":
                target_date = base_moment.date() + timedelta(days=sign)
                y = real_year(target_date.year, base_cycles)
                m, d = target_date.month, target_date.day
            else:
                years = {"year": 1, "century": 100, "millennium": 1000}
                y, m, d = shift_calendar(
                    astro_base, base_moment.month, base_moment.day,
                    years=years.get(unit, 0) * sign,
                    months=sign if unit == "month" else 0,
                )
            if not first <= y <= last:
                return None             # clamp: coverage edge, stay put
            proxy, cycles = canonical_proxy(
                y, m, d, base_moment.hour, base_moment.minute
            )
            moment = proxy.replace(tzinfo=base_moment.tzinfo)
        elif kind in ("north_pole", "south_pole"):
            sign = 1 if kind == "north_pole" else -1
            observer = astral.Observer(
                latitude=sign * defaults.QUICK_JUMP_POLE_LATITUDE,
                longitude=0.0,
            )
            moment = base_moment.astimezone(timezone.utc)
        elif kind == "city":                # the user's own place (slika 12)
            observer = astral.Observer(
                latitude=city.latitude, longitude=city.longitude
            )
            moment = base_moment.astimezone(ZoneInfo(city.timezone))
        else:                               # greenwich — the REAL place
            observer = astral.Observer(
                latitude=defaults.GREENWICH_LATITUDE,
                longitude=defaults.GREENWICH_LONGITUDE,
            )
            moment = base_moment.astimezone(
                ZoneInfo(defaults.GREENWICH_TIMEZONE)
            )
        return moment.replace(second=0, microsecond=0), observer, cycles

    def _dialog_jump(
        self, moment: datetime, cycles: int, latitude: float, longitude: float,
        kind: str, city: dict | None,
    ) -> tuple[datetime, int, float, float] | None:
        """The Time Travel window's OWN Quick Jump rows (item 3A, R5
        MENU REWORK — the rows the old deep Quick Jump submenu chain
        used to hold, `UV/DESIGN/RIGHT CLICK MENU.txt`) — TT LIVE TRAVEL
        (owner round R8b item 1, slika 1-6: "ono sto smo radili na uvek
        Quick Jump dok je bio na right clicku" — a jump row/arrow inside
        the dialog must travel the WATCH immediately, exactly like the
        old right-click menu did, not sit as a draft the owner has to
        OK before anything moves; "ne kao sada da moram svaki put da
        kliknem okej pa da se vratimo taj meni" — no more click-OK-
        reopen per jump). Chains from the DIALOG'S own current fields
        (so a jump chain still reads consistently even mid-travel) —
        `_compute_jump` is the SAME pure computation the old menu's
        immediate jumps used (Rule #5) — but now ALSO starts/refreshes
        the LIVE simulation with the landed moment via `_start_simulation`,
        the exact tail `_apply_jump` uses for every keyboard travel
        shortcut. The dialog then mirrors the SAME fields back onto its
        own widgets (`_on_jump`/`_apply_moment`, app/time_travel.py) so
        it never drifts from what the dial is actually showing — OK
        (`_open_time_travel` below) simply re-asserts whatever the
        fields hold when clicked (a no-op if nothing changed since the
        last jump), Return to Now still ends the simulation outright.
        `moment` is naive (the dialog's own editor, interpreted in the
        configured timezone, same convention `_open_time_travel`
        already uses); returns naive too."""
        observer = astral.Observer(latitude=latitude, longitude=longitude)
        result = self._compute_jump(
            moment.replace(tzinfo=self._tz), observer, cycles, kind, city,
        )
        if result is None:
            return None
        new_moment, new_observer, new_cycles = result
        self._start_simulation(new_moment, new_observer, new_cycles)
        self._flash_jump_location(kind, city)      # R-30
        return (
            new_moment.astimezone(self._tz).replace(tzinfo=None), new_cycles,
            new_observer.latitude, new_observer.longitude,
        )
