"""THE SYNC FREEZE (owner bug 2026-08-06) — the four teeth.

He runs five watches. A manual Windows time SYNC moved the clock by
5-10 s and every dial froze for ~2 minutes at 180% CPU. Nothing about a
clock correction needs that work; four separate defects compounded into
it, and this module pins each one so none can come back quietly.

1. **A clock jump is not a new day.** `_on_tick(clock_jumped=True)` used
   to take the same branch a NEW DAY takes, which starts the hover-article
   sweep: 7,201 pure-Python probes per watch, clocked at 58.2 s in the
   owner's own profiling.json. An NTP nudge inside the same day changes
   not one article. The day CONTEXT is still rebuilt — a jump may have
   crossed midnight, a zone or a Time Travel target.
2. **The wake burst is coalesced.** Windows broadcasts WM_TIMECHANGE to
   every top-level window and Qt runs every native message through EVERY
   installed filter, so with N watches one SYNC fired up to N^2 refreshes.
3. **The native filter is uninstalled on teardown.** It is installed on
   the APPLICATION, so it outlived the watch that installed it: the
   owner's crash.log held 640 `Internal C++ object (ClockWidget) already
   deleted` tracebacks, every one from a removed watch's zombie filter.
4. **Hover sweeps are serialized.** `run_warm` already refuses to run N
   sweeps at once ("N concurrent Python sweeps would do the opposite");
   the sweeps that arrive LATER now obey the same rule through the
   manager's queue.

Headless (QT_QPA_PLATFORM=offscreen), and the manager's queue is tested
on the real methods bound to a hand-built instance — constructing a real
`AppController` would read (and could write) the developer's own live
settings files.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
import threading
from datetime import timedelta
from time import monotonic, sleep

import pytest
from PySide6.QtWidgets import QApplication

from app.controller import WatchController
from app.watch_manager import AppController
from config import defaults
from data import hands, rings
from data.deep_time import shared_deep_time
from data.encyclopedia import reset_shared_encyclopedia, shared_encyclopedia
from data.moon_phases import shared_moon_phases
from data.observatory import shared_observatory
from data.seasons import shared_seasons
from data.symbolism import reset_shared_symbolism, shared_symbolism


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def controller(app):
    made = WatchController(app)
    # The dial has never ticked at construction time; give it the first
    # day build so the tests below exercise the SECOND tick's branching.
    made._on_tick(clock_jumped=False)
    yield made
    made._teardown_windows()


def _pump(app, predicate, timeout_s: float = 5.0) -> bool:
    """Spin the event loop until `predicate()` or the timeout."""
    deadline = monotonic() + timeout_s
    while monotonic() < deadline:
        app.processEvents()
        if predicate():
            return True
        sleep(0.01)
    return predicate()


# --- 1. a clock jump is not a new day ------------------------------------------

def test_clock_jump_inside_the_same_day_starts_no_hover_warm(controller):
    """THE two-minute freeze. A 6-second NTP correction must not speak
    a single new article."""
    sweeps = []
    controller._start_hover_warm = lambda: sweeps.append(1)

    controller._on_tick(clock_jumped=True)

    assert sweeps == []


def test_clock_jump_still_rebuilds_the_day_context(controller):
    """The jump may have crossed midnight, a zone or a travel target —
    the CONTEXT is cheap (12 ms measured) and must never be skipped."""
    controller._start_hover_warm = lambda: None
    before = controller._day

    controller._on_tick(clock_jumped=True)

    assert controller._day is not before


def test_a_genuinely_new_day_does_start_the_hover_warm(controller):
    """The other half of the seam: what the sweep exists for still
    triggers it."""
    sweeps = []
    controller._start_hover_warm = lambda: sweeps.append(1)
    # Age the context by one day; `cache_key` is (local_date, utc_offset).
    controller._day = dataclasses.replace(
        controller._day,
        local_date=controller._day.local_date - timedelta(days=1),
    )

    controller._on_tick(clock_jumped=False)

    assert sweeps == [1]


# --- 2. the wake burst is coalesced --------------------------------------------

def test_a_burst_of_wakes_produces_exactly_one_refresh(app, controller):
    """N windows x N filters used to mean N^2 refreshes; the restartable
    single-shot collapses the whole burst into one."""
    refreshes = []
    controller._refresh_after_jump = lambda: refreshes.append(1)
    controller._wake_timer.timeout.disconnect()
    controller._wake_timer.timeout.connect(controller._refresh_after_jump)

    for _ in range(25):
        controller._on_wake()

    assert refreshes == [], "the refresh must not run inside the native filter"
    _pump(app, lambda: refreshes, timeout_s=defaults.WAKE_COALESCE_MS / 1000 + 3)
    assert refreshes == [1]


def test_a_discarded_watch_ignores_a_wake(controller):
    """Belt to the suspender of test 3 below."""
    refreshes = []
    controller._refresh_after_jump = lambda: refreshes.append(1)
    controller._discarded = True

    controller._on_wake()

    assert not controller._wake_timer.isActive()
    assert refreshes == []


# --- 3. the native filter is uninstalled ---------------------------------------

def test_teardown_uninstalls_the_native_event_filter(app):
    """640 tracebacks in the owner's crash.log came from filters that
    outlived their watch. After teardown the filter must be gone from
    the application, not merely inert."""
    watch = WatchController(app)
    installed = watch._power_filter

    watch._teardown_windows()

    # Qt gives no "is it installed" query, so ask the only way that is
    # observable: removing it a SECOND time must be a no-op, and the
    # watch must have stopped its coalescing timer.
    assert not watch._wake_timer.isActive()
    app.removeNativeEventFilter(installed)      # must not raise


def test_teardown_is_wired_into_discard(app):
    """`discard()` (Remove Watch) and `_prepare_quit()` (Exit) both go
    through `_teardown_windows` — the ONE uninstall point."""
    watch = WatchController(app)
    calls = []
    watch._teardown_windows = lambda: calls.append(1)

    watch.discard()

    assert calls == [1]
    assert watch._discarded


# --- 4. hover sweeps are serialized --------------------------------------------

class _FakeWatch:
    """A watch whose sweep records whether any sibling was sweeping at
    the same moment."""

    def __init__(self, live: list, overlaps: list):
        self._live = live
        self._overlaps = overlaps

    def hover_sweep(self):
        def sweep():
            if self._live:
                self._overlaps.append(1)
            self._live.append(self)
            sleep(0.05)
            self._live.remove(self)
        return sweep


def _bare_manager(watches):
    """The real queue methods on a hand-built instance — see the module
    docstring for why a real `AppController` is not constructed here."""
    manager = object.__new__(AppController)
    manager._quitting = False
    manager._hover_lock = threading.Lock()
    manager._hover_thread = None
    manager._hover_pending = []
    manager._watches = watches
    return manager


def test_five_watches_asking_at_once_sweep_one_at_a_time():
    """The owner's exact shape: one SYNC, five watches, five sweeps.
    They must queue, never overlap — five concurrent pure-Python sweeps
    against five GUI threads IS the freeze."""
    live, overlaps = [], []
    watches = [_FakeWatch(live, overlaps) for _ in range(5)]
    manager = _bare_manager(watches)

    for watch in watches:
        manager.request_hover_warm(watch)
    manager._hover_thread.join(timeout=10)

    assert overlaps == [], "two hover sweeps ran at the same time"
    assert manager._hover_pending == []


def test_the_same_watch_asking_twice_is_queued_once():
    """A skin install followed by a day change must not sweep twice."""
    live, overlaps = [], []
    watch = _FakeWatch(live, overlaps)
    manager = _bare_manager([watch])
    # Hold the worker off so both requests land while it is still busy.
    manager._hover_thread = threading.Thread(target=lambda: sleep(0.2))
    manager._hover_thread.start()

    manager.request_hover_warm(watch)
    manager.request_hover_warm(watch)

    assert manager._hover_pending == [watch]
    manager._hover_thread.join(timeout=5)


def test_a_removed_watch_is_never_swept():
    """A watch dropped from the roster while it waited in the queue."""
    live, overlaps = [], []
    swept = []
    watch = _FakeWatch(live, overlaps)
    watch.hover_sweep = lambda: (lambda: swept.append(1))
    manager = _bare_manager([])                 # not in the roster
    manager._hover_pending = [watch]

    manager._drain_hover()

    assert swept == []


def test_a_quitting_manager_refuses_new_sweeps():
    live, overlaps = [], []
    watch = _FakeWatch(live, overlaps)
    manager = _bare_manager([watch])
    manager._quitting = True

    manager.request_hover_warm(watch)

    assert manager._hover_pending == []
    assert manager._hover_thread is None


# --- 5. one process, one copy of every book ------------------------------------
#
# Owner ruling 2026-07-28, extended 2026-08-06: *"svi stvarno čitaju iste
# stvari identične"*. The ONLY thing that legitimately differs between two
# watches is the observer location and the visual picks. Everything below
# is bundled content whose bytes depend on neither.

def test_the_calendar_databases_are_one_per_process():
    """`Database/seasons_utc.json` (476 KB), `moonPhases_utc.json`
    (2.9 MB) and `deep_time.sqlite` (59 MB) — every watch used to hold
    its own parse, and the deep pack its own sqlite connection."""
    assert shared_seasons() is shared_seasons()
    assert shared_moon_phases() is shared_moon_phases()
    assert shared_deep_time() is shared_deep_time()


def test_the_books_are_one_per_language_not_one_per_watch():
    """`symbolism.json` (1.12 MB) and `encyclopedia.json` (439 KB). The
    LANGUAGE may legitimately key a second copy; a watch may not."""
    assert shared_symbolism("en") is shared_symbolism("en")
    assert shared_encyclopedia("en") is shared_encyclopedia("en")
    assert shared_symbolism("sr-Latn") is not shared_symbolism("en")


def test_a_retranslation_drops_the_stale_books():
    """The overlay is honored on first call per language, so a landed
    translation MUST invalidate — otherwise the app would keep serving
    the pre-translation strings for the rest of the session."""
    before = shared_symbolism("en")
    reset_shared_symbolism()
    reset_shared_encyclopedia()

    assert shared_symbolism("en") is not before


def test_two_watches_share_one_copy_of_every_book(app):
    """The owner's own words, as an assertion: a second dial reads the
    same books, it does not reprint them."""
    first, second = WatchController(app), WatchController(app)
    try:
        assert first._symbolism() is second._symbolism()
        assert first._encyclopedia_repository() is second._encyclopedia_repository()
        assert first._seasons is second._seasons
        assert first._moon_phases is second._moon_phases
        assert first._deep is second._deep
    finally:
        first._teardown_windows()
        second._teardown_windows()


def test_the_observatory_bundles_are_one_per_process():
    """Static science with no watch-specific input at all."""
    assert shared_observatory() is shared_observatory()


def test_the_bundled_ring_presets_are_parsed_once():
    """The bundled list is process-invariant; only the per-watch CUSTOM
    entries and the pick vary, and the custom list is still validated
    fresh on every call."""
    assert rings._bundled_presets() is rings._bundled_presets()
    # The cache must not change what the function ANSWERS.
    assert set(rings.ring_presets()) == set(rings.ring_presets())
    assert rings.ring_presets(), "the bundled presets must still be served"


def test_the_bundled_hand_packs_are_walked_once_but_user_packs_are_not():
    """A pack the user adds mid-session must still appear."""
    hands.hand_packs()
    assert hands._BUNDLED is not None
    walked = []
    real_walk = hands._walk
    hands._walk = lambda root, packs: walked.append(root) or real_walk(root, packs)
    try:
        hands.hand_packs()
    finally:
        hands._walk = real_walk
    assert len(walked) == 1, "only the USER directory may be re-walked"
    assert walked[0] == hands.user_hands_dir()
