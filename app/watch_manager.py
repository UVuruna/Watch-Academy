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

Deliberately SEPARATE watch-level singletons (documented limit, not
solved this round): `config.paths`' `art_source`/`subdial_set` are
PER-PROCESS module globals (`render.asset_variants.subdial_plate_file`'s only
reader), set by `app.controller.apply_display_settings` on every skin
install. With several watches this means the ART SOURCE and SUBDIAL
SET are effectively SHARED — whichever watch last touched Settings/
Design wins for every watch's next repaint until another watch installs
its own skin again. Making these genuinely per-watch would mean
threading a parameter through every asset-cache call site building on
`art_file`/`subdial_plate_file` (dozens of call sites across render/),
a MUCH larger change than this round's scope; flagged here rather than
silently left for someone to rediscover as a bug.
"""

import dataclasses
from typing import Callable

from PySide6.QtWidgets import QApplication

from app.controller import WatchController
from app.settings_store import SettingsStore
from config import paths


class AppController:
    """Owns the watch roster and the app-wide window icon. Each
    WatchController is fully self-contained (its own settings/widget/
    tray/menu/skin/compositor/dialogs/scheduler — ARCHITECTURE
    GUIDANCE considered a single SHARED minute scheduler across
    watches; kept per-watch instead, see `discard`'s sibling `quit_all`
    docstring below for why)."""

    def __init__(self, app: QApplication):
        self._app = app
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
        self._refresh_all_titles()

    def remove_watch(self, watch: WatchController) -> None:
        """The Remove/Close entry's callback (watches 2+ only —
        `WatchController` itself never BUILDS the entry on watch 1; the
        index guard below is the belt to that suspender against a
        stale double-click race). Tears the watch down WITHOUT saving
        (`discard()`) and deletes its settings file — no further
        confirmation here, `_confirm_remove_watch` already asked."""
        if watch.watch_index == 1 or watch not in self._watches:
            return
        watch.discard()
        paths.settings_path(watch.watch_index).unlink(missing_ok=True)
        self._watches.remove(watch)
        self._refresh_all_titles()

    # --- lifecycle --------------------------------------------------------------

    def run(self) -> None:
        for watch in self._watches:
            watch.run()

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
        for watch in self._watches:
            watch._prepare_quit()
        self._app.quit()
