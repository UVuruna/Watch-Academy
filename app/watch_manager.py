"""Process-wide composition root — the ADD WATCH round (owner
INSTRUCTION.txt item 2, sealed 2026-07-21).

ONE QApplication holds an independent roster of
[WatchController](controller.md) instances — each with its own
settings file, dial widget, tray icon, menu, skin and compositor (see
`app.controller`'s own module docstring for what ONE watch owns). This
class is the ONLY object that knows the FULL roster; a WatchController
reaches it only through the three callbacks its own constructor takes
(`watch_count`, `on_add_watch`, `on_remove_watch`) plus `on_exit` — a
WatchController itself still knows nothing about its siblings.

Per-watch settings files (see settings_store.md): watch 1 keeps the
pre-multi-watch `settings.json` (existing installs keep working
untouched); watch N (2+) gets its own `settings.<N>.json`
(`config.paths.settings_path`). A REMOVED watch's number is never
reused while a higher-numbered watch survives — see `_next_index`'s
own docstring — so a watch's tray color (derived straight from its
index) never jumps onto a DIFFERENT watch later in the session.

What is SHARED across watches, deliberately (owner 2026-07-28: *"zašto
bi se stvari učitavale više puta za svaki sat kada svi dele iste"*):

- **ONE `AssetCache`** (`render.assets.shared_cache`) — the watches read
  the same asset tree, so they hold ONE decoded copy of each image
  instead of N.
- **ONE background warm thread** (`app.warm.run_warm`), armed by
  `_arm_warm` below only after every dial has painted.

What is strictly PER WATCH, also deliberately: the display context —
art source, subdial plate set and metal shades
(`config.paths.DisplayContext`, carried on the skin). Those three USED to
be process-wide globals written by `apply_display_settings` on every skin
install, and that was the owner's 2026-07-28 colour bug: with a DOMY and
a PILOT watch both on the `thematic` finish, both dials wore the
LAST-BUILT watch's red. Every render/hover/dialog entry point now
installs its own watch's context (`config.paths.in_display`).
"""

import dataclasses
import threading
from typing import Callable

from PySide6.QtWidgets import QApplication

from app.controller import WatchController
from app.settings_store import SettingsStore
from app.warm import run_warm
from config import paths
from render import asset_recolor
from render.art_warm import warm_pending_art


class AppController:
    """Owns the watch roster and the app-wide window icon. Each
    WatchController is fully self-contained (its own settings/widget/
    tray/menu/skin/compositor/dialogs/scheduler — ARCHITECTURE
    GUIDANCE considered a single SHARED minute scheduler across
    watches; kept per-watch instead, see `discard`'s sibling `quit_all`
    docstring below for why)."""

    def __init__(self, app: QApplication):
        self._app = app
        self._quitting = False
        self._warm_thread: threading.Thread | None = None
        #: The watches the NEXT warm pass covers — the startup roster, or
        #: the single watch a mid-session ADD WATCH just created.
        self._armed: set = set()
        # The on-demand art drain (owner bug 2026-08-02): one thread,
        # re-armed by a rerun flag instead of ever running two at once.
        self._art_lock = threading.Lock()
        self._art_thread: threading.Thread | None = None
        self._art_rerun = False
        #: The live warm/drain progress line every watch's menu shows
        #: while background work runs (0.14.710); None = idle, row
        #: hidden. Written by the warm/drain threads, read on the GUI
        #: thread at menu-open — a single str reference, no lock needed.
        self._warm_status: str | None = None
        asset_recolor.set_art_stale_notifier(self.kick_art_warm)
        self._watches: list[WatchController] = []
        for index in paths.discover_watch_indices():
            self._watches.append(self._build_watch(index))
        # Every watch's OWN construction ran `_build_menu()` before its
        # sibling(s) joined `self._watches` (the title needs the FINAL
        # count, not the count at ITS OWN construction moment) — one
        # pass at the end always lands every title/tooltip correctly
        # regardless of build order.
        self._refresh_all_titles()

    # --- construction -------------------------------------------------------

    def _build_watch(self, index: int) -> WatchController:
        watch = WatchController(
            self._app,
            watch_index=index,
            settings_path=paths.settings_path(index),
            watch_count=lambda: len(self._watches),
            on_remove_watch=self.remove_watch,
            on_exit=self.quit_all,
        )
        # `on_add_watch` needs the WATCH ITSELF as the seed — not
        # available until construction above returns — so it is wired
        # AFTER the fact; `_build_menu` (already run once by now) reads
        # `self._on_add_watch` fresh on every click, never a snapshot
        # taken at connect time (see WatchController._build_menu).
        watch._on_add_watch = lambda: self.add_watch(watch)
        # The menu's warm-status row reads the manager's live progress
        # line the same deferred way (0.14.710).
        watch._warm_status_provider = lambda: self._warm_status
        return watch

    def _next_index(self) -> int:
        """The next watch's own settings-file number: one past the
        HIGHEST number any LIVE watch currently holds. A removed
        watch's number is never reused while a higher one survives —
        simpler and more predictable than compacting the roster, and it
        keeps a watch's tray color (derived straight from its index)
        permanently tied to that one watch for the life of the
        session."""
        return max((watch.watch_index for watch in self._watches), default=0) + 1

    def _refresh_all_titles(self) -> None:
        for watch in self._watches:
            watch.refresh_title()

    # --- roster ---------------------------------------------------------------

    def add_watch(self, seed_watch: WatchController) -> None:
        """Owner INSTRUCTION.txt item 2: a NEW watch seeded from
        `seed_watch`'s CURRENT settings (the user diverges from there
        through the usual controls) — the window position is cleared
        so the new dial re-centers on the primary screen instead of
        landing exactly on top of its seed
        (`WatchController._position_widget`'s existing first-run
        behavior, reused for free rather than reinvented)."""
        index = self._next_index()
        seed = dataclasses.replace(
            seed_watch._settings, window_x=None, window_y=None,
        )
        SettingsStore(paths.settings_path(index)).save(seed)
        watch = self._build_watch(index)
        self._watches.append(watch)
        watch.run()
        # A watch added mid-session brings art the process has never
        # resolved (its own ring letters at its own shade) — give it the
        # same "paint first, warm after" treatment, for itself alone.
        self._armed = {watch}
        self._arm_warm([watch])
        self._refresh_all_titles()

    def remove_watch(self, watch: WatchController) -> None:
        """The Remove/Close entry's callback (watches 2+ only —
        `WatchController` itself never BUILDS the entry on watch 1; the
        index guard below is the belt to that suspender against a
        stale double-click race). Tears the watch down WITHOUT saving
        (`discard()`) and deletes its settings file — no further
        confirmation here, `_confirm_remove_watch` already asked.

        `discard()` closes the dial window as well as the tray icon —
        see its own docstring for the 2026-07-29 ghost-dial bug — and
        the watch is dropped from `_armed` here so the warm set does
        not keep a removed watch alive for the rest of the session."""
        if watch.watch_index == 1 or watch not in self._watches:
            return
        watch.discard()
        paths.settings_path(watch.watch_index).unlink(missing_ok=True)
        self._watches.remove(watch)
        self._armed.discard(watch)
        self._refresh_all_titles()

    # --- lifecycle --------------------------------------------------------------

    def run(self) -> None:
        for watch in self._watches:
            watch.run()
        self._armed = set(self._watches)
        self._arm_warm(self._watches)

    # --- the ONE background warm -------------------------------------------------

    def _arm_warm(self, watches) -> None:
        """Start the shared warm thread once EVERY watch's dial is on
        screen (owner 2026-07-28).

        Two rules the old code broke, both measured:

        - **Once per PROCESS.** Each watch used to start its own thread,
          so the SAME 795 working-set files, 698 Encyclopedia paths and
          7,201 hover probes were walked N times — the owner's log showed
          every progress line printed two and three times. The watches
          share one asset tree, one raster cache and one `AssetCache`;
          the work is shared too.
        - **After the first frame, not before it.** The old thread was
          started inside `run()`, i.e. before the event loop had
          delivered a single paint event, so the warm competed with the
          frame the user was waiting for. Waiting for `first_painted`
          also means the art ledger is fully populated: a dial's paint is
          what RECORDS which derived files it wants.

        Called for the STARTUP roster and again for a single watch added
        mid-session (ADD WATCH): a new dial brings its own ring letters,
        so it needs its own drain — but only for itself, never a second
        walk of what the process already warmed."""
        pending = set(watches)
        for watch in watches:
            watch.first_painted().connect(
                lambda watch=watch: self._watch_painted(watch, pending)
            )

    def _watch_painted(self, watch, pending: set) -> None:
        pending.discard(watch)
        if pending:
            return
        warming = [w for w in self._watches if w in self._armed]
        self._warm_thread = threading.Thread(
            target=self._run_warm, args=(warming,), daemon=True,
            name="DOMY warm",
        )
        self._warm_thread.start()

    def _run_warm(self, watches) -> None:
        """The warm thread's body. `art_ready` is a Qt SIGNAL emitted from
        this thread, never a direct call — Qt queues it onto each watch's
        own (GUI) thread, where repainting is legal."""
        def art_ready() -> None:
            for watch in watches:
                watch.art_ready.emit()

        try:
            run_warm(
                hover_sweeps=[watch.hover_sweep() for watch in watches],
                progress=self._report_progress,
                on_art_ready=art_ready,
                should_stop=lambda: self._quitting,
            )
        finally:
            self._warm_status = None

    def _report_progress(self, line: str) -> None:
        """Every warm/drain progress line goes two places: the console
        (the owner's startup log) and the menus' warm-status row."""
        self._warm_status = line
        print(line)

    # --- the on-demand art drain ---------------------------------------------

    def kick_art_warm(self) -> None:
        """Drain freshly-recorded derived-art recipes on a background
        thread — installed as `render.asset_recolor`'s stale notifier,
        rung the moment a paint observes a MISSING finish (owner bug
        2026-08-02: after the one startup warm finished, a finish/shade/
        theme switch recorded recipes nobody ever built — the dial
        stayed gold until the next process restart).

        Cheap and thread-agnostic on purpose (it runs inside a paint):
        one lock, one flag, at most ONE drain thread alive — a kick
        during a running drain sets the rerun flag and the drain loops
        once more instead of a second thread starting. Before the
        startup warm has been armed and started, the kick stands down:
        that first drain belongs to `run_warm`, AFTER every dial's
        first frame (owner 2026-07-28 — nothing competes with the
        first paint)."""
        if self._quitting or self._warm_thread is None:
            return
        with self._art_lock:
            if self._art_thread is not None and self._art_thread.is_alive():
                self._art_rerun = True
                return
            self._art_rerun = False
            self._art_thread = threading.Thread(
                target=self._drain_art, daemon=True, name="DOMY art drain",
            )
            self._art_thread.start()

    def _drain_art(self) -> None:
        """The kicked drain's body: `warm_pending_art` until the ledger
        is stable, then once more per rerun flag — a kick that arrived
        mid-drain is honored, never lost."""
        try:
            # Small batches finish before their first progress line
            # would print — the row still names the work (0.14.710).
            self._warm_status = "building switched art…"
            while True:
                warm_pending_art(
                    progress=self._report_progress,
                    on_ready=self._emit_art_ready,
                    should_stop=lambda: self._quitting,
                )
                with self._art_lock:
                    if not self._art_rerun:
                        return
                    self._art_rerun = False
        finally:
            self._warm_status = None

    def _emit_art_ready(self) -> None:
        """A recolor landed: every live watch repaints (the art is
        shared, so any dial may be the one standing in with a master).
        Qt queues the cross-thread signal onto each GUI thread."""
        for watch in list(self._watches):
            watch.art_ready.emit()

    def quit_all(self) -> None:
        """The Exit menu action on ANY watch closes the WHOLE process
        (owner architecture: Exit is process-wide; the per-watch Remove
        entry is the surgical one-watch-only teardown) — every watch's
        own `_prepare_quit()` (dialogs, scheduler, debounced save) runs
        before the ONE shared `app.quit()`.

        ARCHITECTURE GUIDANCE considered ONE shared `MinuteScheduler`
        across watches instead of N independent ones. Kept per-watch
        (constructive disagreement, Rule #8): each `MinuteScheduler` is
        one lightweight self-rescheduling `QTimer` — N of them, N being
        a handful of watches in practice, cost nothing measurable on
        Windows — while a SHARED scheduler would force every watch to
        repaint at the FASTEST cadence any sibling's seconds hand/slot
        needs (wasted redraws for a watch that wants minute-only ticks)
        or need its own per-watch cadence bookkeeping bolted onto the
        shared timer for no measured gain (Priorities: an optimization
        with no measurable gain is a net loss). Flagged for the owner
        to confirm or override."""
        # Tell the warm thread to stand down BEFORE the windows go: it
        # is a daemon and would die with the process anyway, but a clean
        # stop means no half-written cache file on the way out.
        self._quitting = True
        for watch in self._watches:
            watch._prepare_quit()
        self._app.quit()
