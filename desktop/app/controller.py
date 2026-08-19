"""Composition root for ONE watch — the only object that knows
everyone ELSE inside it.

Owns settings, the clock window, the tray, the repositories, the
compositor and the minute scheduler. Tick flow: read the wall clock
fresh -> rebuild the day context when (local date, UTC offset) changed
-> build the tick state -> repaint.

ADD WATCH round (owner INSTRUCTION.txt item 2, sealed 2026-07-21): a
process can hold SEVERAL of these, one per watch, each fully
self-contained — [app.watch_manager.AppController](watch_manager.md)
is the thin process-wide owner that builds the roster, and reaches
each `WatchController` only through the three callbacks its
constructor takes (`watch_count`, `on_add_watch`, `on_remove_watch`) —
a `WatchController` itself still knows nothing about its siblings.
"""

import dataclasses
import hashlib
import sys
import threading
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Callable
from zoneinfo import ZoneInfo

import astral

from PySide6.QtCore import QObject, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import QApplication, QMessageBox

from app import native
from app.controller_dialogs import _DialogHostsMixin
from app.controller_display import _DisplaySettingsMixin
from app.controller_menu import _ContextMenuMixin
from app.controller_shortcuts import (
    _ShortcutActionsMixin, _location_flash_text,
)
from app.controller_simulation import _TimeTravelMixin
from app.watch_face.window import WatchFaceDialog
from app.encyclopedia import EncyclopediaDialog
from app.fast_travel_flash import FastTravelFlash
from app.observatory import ObservatoryDialog
from app.legend_popup import LegendPopup
from app.scheduler import MinuteScheduler
from app.skin_builder import build_skin, slot_seconds, watch_title
from app.settings_store import (
    Settings, SettingsCorruptError, SettingsStore, replace,
)
from app.tray import TrayController, logo_icon, window_icon
from app.widget import ClockWidget
from config import constants, defaults, dial, identity, paths, profiling
from core.clock_state import build_day_context, build_tick_state
from core.deep_time import real_year
from core.moon import chinese_name_of_year
from data.deep_time import shared_deep_time
from data.moon_phases import shared_moon_phases
from data.seasons import shared_seasons
from data.encyclopedia import (
    EncyclopediaRepository, reset_shared_encyclopedia, shared_encyclopedia,
)
from data.symbolism import (
    SymbolismRepository, reset_shared_symbolism, shared_symbolism,
)
from data.translations import (
    TranslationStore, claim_translation, collect_corpus, release_translation,
    translate_texts,
)
from render.assets import shared_cache
from render.compositor import Compositor
from skins.manifest import missing_assets


class WatchController(
    _ShortcutActionsMixin,
    _ContextMenuMixin,
    _DisplaySettingsMixin,
    _DialogHostsMixin,
    _TimeTravelMixin,
    QObject,
):
    #: A background recolor landed — emitted FROM the warm thread, so it
    #: must be a real Qt signal: the connection to `apply_pending_art`
    #: below crosses threads and Qt queues it onto the GUI thread (owner
    #: decree 2026-07-28; QTimer.singleShot would silently never fire,
    #: having no event loop on the worker thread to arm itself in).
    art_ready = Signal()

    def __init__(
        self,
        app: QApplication,
        watch_index: int = 1,
        settings_path: Path | None = None,
        watch_count: Callable[[], int] = lambda: 1,
        on_add_watch: Callable[[], None] = lambda: None,
        on_remove_watch: Callable[["WatchController"], None] = lambda watch: None,
        on_exit: Callable[[], None] | None = None,
    ):
        """`watch_index`/`settings_path`/`watch_count`/`on_add_watch`/
        `on_remove_watch`/`on_exit` are the ADD WATCH round's seams to
        [the manager](watch_manager.md) — every default reproduces the
        pre-ADD-WATCH single-watch behavior exactly (watch 1, its own
        `settings.json`, a title that never goes full, Add Watch a
        no-op, Exit quits just this instance), so standalone
        construction (every test in this suite before this round, and
        any test that does not care about multi-watch specifics) needs
        no changes beyond the class rename."""
        super().__init__()
        self._app = app
        self._watch_index = watch_index
        self._watch_count = watch_count
        self._on_add_watch = on_add_watch
        self._on_remove_watch = on_remove_watch
        self._on_exit = on_exit if on_exit is not None else self.quit
        self._store = SettingsStore(settings_path or paths.settings_path(watch_index))
        self._settings = self._load_settings_or_recover()
        self._save_failed = False
        # R-31: the tray tooltip/menu TITLE's own LIVE location word —
        # starts as the home city, moved by `_flash_location` on every
        # location change (Settings preset pick, Quick Jump, Time
        # Travel, Greenwich, the poles) and restored by `_end_simulation`
        # when a simulation ends. Never re-derived from `self._settings`
        # directly, so a running simulation (which never touches the
        # home Settings) does not leave the title frozen on the old city.
        self._active_location_name = self._settings.place.name
        # THE LOCATION CROWN's own text (RING VERDICTS round, owner
        # decree 2026-08-05): "CITY, COUNTRY", resolved through the SAME
        # `_location_flash_text` formatter R-30's flash uses (Rule #5 —
        # one source, never a duplicate). Kept in lockstep with
        # `_active_location_name` above at every one of its own update
        # points (`_flash_location`, `_end_simulation`) so `build_skin`
        # always sees the CURRENT active place, never the home city
        # frozen mid-simulation.
        self._active_location_display = _location_flash_text(
            self._settings.place.name, self._settings.place.path,
            self._settings.place.timezone,
        )
        #: Set by `discard()` (Remove Watch). A discarded watch is DEAD:
        #: its settings file has just been deleted by the manager, so it
        #: must never write it again — see `_flush_position`.
        self._discarded = False

        # The cached overlay loads BEFORE the menu builds, so the menu
        # speaks the chosen language from the very first frame (Phase 2);
        # _apply_language below only starts the background fetch for
        # entries the cache does not know yet.
        self._translation_overlay: dict = {}
        if self._settings.language != "en":
            self._translation_overlay = TranslationStore().load(
                self._settings.language
            )
        self._retired_menu = None       # keeps a replaced OPEN menu alive
        # The hidden-mode unlock is SESSION-only (owner 2026-07-15):
        # every launch starts locked — the code must be typed again.
        # Lives BEFORE the menu build: the Report entry reads it.
        self._hidden_unlocked = False
        # DEEP TIME detection (Session 16) also lives BEFORE the menu
        # build — the eclipse jump entries gray without the pack.
        self._deep = shared_deep_time()
        # Time Travel state also lives BEFORE the menu build now (fix
        # round E, 2026-07-19): the Quick Jump pole labels read the
        # traveled date via `_effective_travel_date`, which checks
        # `self._simulation`. No simulation can be running yet at
        # startup, but the attribute must EXIST for that check.
        self._simulation: tuple[datetime, astral.Observer] | None = None
        # THE WATCH FACE WINDOW (Phase ①+②, R-01; the sole survivor after
        # Phase 6 FINAL cleanup retired Design/Pointer Theme/Slot Theme)
        # also lives BEFORE the menu build: `_refresh_menu_gating` (called
        # at the end of `_build_menu`) pushes a live gate into it if open,
        # so the attribute must EXIST (None — nothing can be open yet at
        # startup).
        self._watch_face: WatchFaceDialog | None = None
        # FAST TRAVEL / LOCATIONS shortcut state (R5b round, owner spec,
        # sealed 2026-07-21) — SESSION-only, like the hidden-mode unlock:
        # the theme/option cursors and the custom-city cursor start fresh
        # on every launch, nothing here is persisted to settings.
        self._fast_travel_theme_index = 0
        self._fast_travel_option_indices: dict[str, int] = {}
        self._jump_city_index = 0
        # The warm-status provider (0.14.710) — wired by the manager
        # AFTER construction, exactly like `_on_add_watch`; a watch
        # built stand-alone (tests) simply never shows the row.
        self._warm_status_provider = None
        # The hover-warm handoff (owner bug 2026-08-06), wired by the
        # manager the same way. A watch that HAS a manager never starts
        # its own sweep thread — it queues the sweep on the ONE shared
        # warm worker, because the sweep is pure Python and N of them
        # running at once fight each other for the GIL and starve the
        # GUI threads. A stand-alone watch (every test) falls back to
        # its own thread, exactly as before.
        self._on_hover_warm = None
        self._menu = self._build_menu()
        self._legend = LegendPopup()
        self._fast_travel_flash = FastTravelFlash()
        self._widget = ClockWidget(
            self._settings.diameter, self._menu, self._legend, self._show_action
        )
        try:
            self._tray = TrayController(self._menu, logo_icon(self._watch_index))
            # The FULL name form backs the tray hover tooltip from the
            # very first frame (owner INSTRUCTION.txt item 2A) —
            # `_title_label` already exists (set inside the `_build_menu`
            # call above).
            self._tray.set_tooltip(
                watch_title(
                    self._settings, full=True,
                    location_name=self._active_location_name,
                )
            )
            # Every dialog title bar (Settings, Time Travel, Guide,
            # Encyclopedia, Observatory) inherits this MULTI-RESOLUTION
            # icon instead of the generic Windows icon (owner report
            # 2026-07-11; multi-res + AppUserModelID fix owner
            # screenshot 2026-07-20 — see app.native.set_app_user_model_id
            # for the taskbar-grouping half of that fix); the built EXE
            # additionally gets the M7 ICO on top.
            self._app.setWindowIcon(window_icon())
            # SHOW on tray DOUBLE-CLICK (owner 2026-07-18, ROADMAP 15h):
            # the same "normal" z-mode-only affordance as the menu entry
            # above it.
            self._tray.on_double_click(self._show_if_normal_z_mode)
        except ValueError as error:
            # A broken/missing logo must be SEEN (review finding) — in a
            # windowed build a bare traceback dies with no window at all.
            self._critical_box(
                f"The tray icon could not be loaded:\n{error}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
            raise SystemExit(1) from error

        self._tz = ZoneInfo(self._settings.place.timezone)
        self._observer = astral.Observer(
            latitude=self._settings.place.latitude,
            longitude=self._settings.place.longitude,
        )
        # DEEP TIME (Session 16): the pack detected once above (the ONE
        # resolution point) is injected into both repositories; present
        # → Time Travel spans the full pack coverage and the eclipse
        # jumps are alive; absent → the bundled span with the friendly
        # clamp.
        self._seasons = shared_seasons(deep=self._deep)
        self._moon_phases = shared_moon_phases(deep=self._deep)
        # Translation overlay (owner spec): apply whatever the cache
        # already holds; missing entries translate in the background.
        self._translation_thread: threading.Thread | None = None
        self._translation_error: Exception | None = None
        self._translation_poller = QTimer(self)
        self._translation_poller.setInterval(1000)
        self._translation_poller.timeout.connect(self._poll_translation)
        # Theme rotation (owner spec 2026-07-12): cycle the selected
        # weekday themes every N minutes.
        self._theme_rotation_timer = QTimer(self)
        self._theme_rotation_timer.timeout.connect(self._rotate_theme)
        self._configure_theme_rotation()
        self._skin = build_skin(self._settings, self._active_location_display)
        missing = missing_assets(self._skin)
        if missing:
            # Checked up front: a missing asset would otherwise raise
            # inside paintEvent, where Qt swallows it — silently broken dial.
            listing = "\n".join(str(path) for path in missing)
            self._critical_box(
                f"Skin assets are missing:\n{listing}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
            raise SystemExit(1)
        if self._settings.language != "en":
            self._apply_language(start_missing=True)
        self._compositor = Compositor(
            self._skin, shared_cache(), self._symbolism(),
            overlay=self._translation_overlay,
            encyclopedia=self._encyclopedia_repository(),
        )
        self._day = None
        # Time Travel: a frozen (moment, observer) rendered instead of the
        # present until the deadline passes (`self._simulation` itself is
        # initialized earlier, before the menu build). Deep travel carries
        # the moment in the 400-year PROXY frame; _sim_cycles is its cycle
        # count (0 = the ordinary frame).
        self._simulation_ends: float = 0.0
        # TIME FLOWS THROUGH THE TRAVEL WINDOW (owner spec 2026-08-11:
        # after any jump the clock KEEPS RUNNING through the travel
        # minute — "sometimes we want to watch how a transition
        # unfolds, e.g. day into night"): the stored simulation moment
        # is the ANCHOR; every read advances it by the real seconds
        # since the jump landed (`_simulated_moment`).
        self._sim_started: float = 0.0
        self._sim_cycles: int = 0
        self._widget.set_renderer(self._compositor)
        seconds_hand = (
            self._skin.hands.second is not None
            and self._settings.show_seconds
        ) or slot_seconds(self._settings)
        self._scheduler = MinuteScheduler(self._on_tick, self, per_second=seconds_hand)
        # Resume-from-sleep and clock/zone changes refresh immediately —
        # the scheduled tick never fired while the machine slept.
        self._power_filter = native.PowerEventFilter(self._on_wake)
        app.installNativeEventFilter(self._power_filter)
        # THE WAKE COALESCER (owner bug 2026-08-06). Windows BROADCASTS
        # WM_TIMECHANGE to every top-level window, and Qt runs every
        # native message through EVERY installed filter — with N watches
        # that is N deliveries x N filters, so one SYNC used to fire this
        # watch's refresh up to N^2 times. A restartable single-shot
        # collapses the whole burst into ONE refresh; restarting an
        # already-active QTimer re-aims it instead of queuing a second.
        self._wake_timer = QTimer(self)
        self._wake_timer.setSingleShot(True)
        self._wake_timer.setInterval(defaults.WAKE_COALESCE_MS)
        self._wake_timer.timeout.connect(self._refresh_after_jump)

        # THE FLIP (ring_rework §1): a GENUINE sunrise/sunset turns the
        # world through one short eased move, so for exactly that long —
        # and never a millisecond more — the dial needs animation-cadence
        # repaints instead of its minute tick. The compositor owns the
        # motion's own clock; this timer only asks for frames, and stops
        # itself the moment the move is over.
        self._flip_timer = QTimer(self)
        self._flip_timer.setInterval(dial.WORLD_FLIP_FRAME_MS)
        self._flip_timer.timeout.connect(self._on_flip_frame)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(defaults.SETTINGS_WRITE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self._flush_position)
        # The profiling store flushes once per minute (dirty-guarded —
        # measuring itself never costs an I/O) and again at quit.
        self._profiling_timer = QTimer(self)
        self._profiling_timer.setInterval(60_000)
        self._profiling_timer.timeout.connect(profiling.flush)
        self._profiling_timer.start()
        self._widget.moved.connect(self._on_widget_moved)
        # The art-ready DEBOUNCE (0.14.707): the pooled drain lands
        # finishes in bursts — one quiet window, one composite rebuild.
        self._art_repaint_timer = QTimer(self)
        self._art_repaint_timer.setSingleShot(True)
        self._art_repaint_timer.setInterval(defaults.ART_REPAINT_DEBOUNCE_MS)
        self._art_repaint_timer.timeout.connect(self._apply_art_now)
        self.art_ready.connect(self.apply_pending_art)
        # The hidden-mode code listener (owner 2026-07-14): printable
        # keys typed on the focused dial roll through a buffer.
        self._secret_buffer = ""
        self._widget.typed.connect(self._collect_secret)
        # Spacebar over a themed hover target opens the Encyclopedia on
        # that topic's page (owner 2026-07-16, ROADMAP queue #8).
        self._widget.open_encyclopedia.connect(self._open_encyclopedia_at)
        # KEYBOARD SHORTCUTS (R5 MENU REWORK, `shortcuts.SHORTCUTS`) —
        # fired by the focused `ClockWidget.keyPressEvent`; dispatched
        # by action_id in `_on_shortcut`.
        self._widget.shortcut_triggered.connect(self._on_shortcut)
        # NON-MODAL Encyclopedia/Guide/Observatory (ITEM 1, R4 owner
        # instruction batch 2026-07-20): these three now `.show()`
        # instead of `.exec()` — the dial stays fully interactive
        # (hover, right-click, move) while any of them is open. Each
        # attribute holds the ONE live instance of its dialog type (or
        # None); a second open request RAISES it instead of stacking a
        # duplicate (the Encyclopedia's old re-entrancy guard becomes
        # "focus the live one" — a SPACE jump while it is open now
        # NAVIGATES it to the new target, `EncyclopediaDialog.navigate_
        # to`, a strict improvement over the old modal no-op). Settings
        # and Time Travel are UNCHANGED — they still `.exec()` (they
        # mutate state transactionally and must not be left half-applied
        # by a stray close).
        self._encyclopedia: EncyclopediaDialog | None = None
        self._observatory: ObservatoryDialog | None = None
        # THE WATCH FACE WINDOW — the SAME non-modal, one-live-instance
        # lifecycle as the pair above (see watch_face/window.md for why
        # it is LIVE-APPLY rather than transactional) — is initialized
        # EARLIER, before the first `_build_menu()` call (its gating
        # pass reads it).

        # In click-through mode the window receives no mouse input, so the
        # hover tooltips are driven by polling the global cursor instead.
        self._hover_poller = QTimer(self)
        self._hover_poller.setInterval(defaults.CLICK_THROUGH_HOVER_POLL_MS)
        self._hover_poller.timeout.connect(self._poll_hover)
        self._last_hover_tip: str | None = None
        # Hover article warm sweeps (owner 2026-07-18): the generation
        # counter obsoletes a running sweep when the skin or day it was
        # warming is replaced.
        self._hover_warm_generation = 0

    # --- ADD WATCH identity (owner INSTRUCTION.txt item 2, sealed 2026-07-21) ---

    @property
    def watch_index(self) -> int:
        """This watch's own 1-based slot number — the anchor (1) can
        never be removed, and every tray-color/settings-file rule
        (`app.tray.logo_icon`, `config.paths.settings_path`) reads it."""
        return self._watch_index

    @property
    def settings_path(self) -> Path:
        """This watch's own settings file — the manager deletes it on
        Remove Watch (`discard()` tears down the LIVE watch first)."""
        return self._store.path

    def refresh_title(self) -> None:
        """Public hook for the manager: re-render the TITLE row and the
        tray tooltip after the watch ROSTER changes (Add/Remove Watch)
        — the short/full split depends on `watch_count()`, which just
        moved for every surviving watch, not only this one."""
        self._refresh_watch_title()

    def _confirm_remove_watch(self) -> None:
        """The Remove/Close entry's own click handler (watches 2+ only
        — `_build_menu` never builds the action on watch 1): one plain
        Yes/No confirm, no further dialogs (owner spec) — a Yes calls
        the manager's `remove_watch(self)`, which tears this watch down
        and deletes its settings file; `self._on_remove_watch` defaults
        to a no-op for standalone/test use (no manager attached)."""
        box = QMessageBox(
            QMessageBox.Icon.Question, identity.APP_NAME,
            self._ui("Remove this watch? Its settings file will be deleted."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        box.setDefaultButton(QMessageBox.StandardButton.No)
        box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        if box.exec() == QMessageBox.StandardButton.Yes:
            self._on_remove_watch(self)

    # --- Lifecycle --------------------------------------------------------------

    def run(self) -> None:
        self._on_tick(clock_jumped=False)   # first frame BEFORE show()
        # Reserve the window margin for the ACTIVE skin (the compositor is
        # built in __init__, bypassing _install_skin) and apply the
        # visibility Z mode BEFORE the first show() — window flags must be
        # set before show() on Windows (owner 2026-07-17).
        self._widget.set_dial_diameter(
            self._settings.diameter,
            defaults.dial_window_margin_fraction(self._skin),
        )
        self._widget.set_z_mode(self._settings.z_mode)
        self._position_widget()
        self._widget.show()
        # TRUE topmost is re-asserted natively after the first show (owner
        # 2026-07-17): Qt's StaysOnTop hint alone degrades to normal
        # stacking once the window has been shown.
        self._widget.reassert_z_order()
        self._tray.show()
        self._scheduler.start()
        # windowHandle() exists only after show(); a monitor/DPI change
        # invalidates every rasterized cache.
        self._last_dpr = self._widget.devicePixelRatioF()
        self._widget.windowHandle().screenChanged.connect(self._on_screen_changed)
        if self._settings.click_through:
            self._widget.set_click_through(True)
            self._hover_poller.start()
        # NO warm thread is started here any more (owner 2026-07-28).
        # Every watch used to launch its own, duplicating identical work
        # N times AND competing with its own first frame; the process now
        # runs exactly ONE warm, started by `app.watch_manager` after
        # EVERY watch has painted — see [Warm](warm.md) for the order.

    def first_painted(self):
        """This watch's "my dial is on screen" signal (the widget's own,
        forwarded) — the manager connects to it and starts the ONE shared
        warm thread once every watch has fired (owner 2026-07-28)."""
        return self._widget.first_painted

    def apply_pending_art(self) -> None:
        """A background recolor finished: schedule the repaint that
        replaces a GOLD-MASTER stand-in with its real metal (owner
        decree 2026-07-28: "Kad završi prikaže"). Runs on the GUI
        thread — the warm thread reaches it through a queued Qt
        connection, never by touching a QPixmap itself.

        DEBOUNCED, not immediate (0.14.707): the pooled drain lands a
        burst of finishes back to back, and a full composite rebuild
        per landed file (62 ms each, up to 17 per burst) repainted
        nothing the trailing rebuild would not show anyway. The restart
        pattern is `_save_timer`'s — the LAST arrival wins the one
        rebuild; arrivals slower than the window still repaint one by
        one."""
        self._art_repaint_timer.start()

    def _apply_art_now(self) -> None:
        """The debounce window closed: rebuild the composites (assets
        stay — the landed finish resolves under a NEW cache key, so
        nothing rasterized needs re-decoding) and repaint.

        Also gives the asset cache's PENDING working-set markers (owner
        bar 2026-08-09, MIGRATE-GUI Phase 1 — `AssetCache.clear_pending`)
        one more chance to resolve: a working-set miss stood in blank
        the last frame, and this signal — the SAME debounced repaint a
        landed metal recolor already rides — is exactly the moment a
        background build might have landed. Reached through the
        compositor's own cache rather than a new `Compositor` method:
        `render/compositor.py` is mid-edit by another session's
        celestial-geometry round this session must not touch."""
        self._compositor._cache.clear_pending()
        self._compositor.refresh_composites()
        self._widget.update()

    def _refresh_warm_status_row(self) -> None:
        """The menu is opening: show the manager's live warm/drain
        status line, or hide the row when the process is idle
        (0.14.710 — the menu tells the user WHAT is loading instead of
        the dial silently standing in gold)."""
        provider = self._warm_status_provider
        status = provider() if provider is not None else None
        self._warm_status_action.setVisible(status is not None)
        if status is not None:
            self._warm_status_label.setText(status)

    def hover_warm_signature(self):
        """What this watch's hover sweep would BUILD, as a hashable key —
        or None when it cannot be computed, in which case the caller must
        run the sweep (owner bug 2026-08-06; accuracy > speed, so an
        unknown signature never means "skip").

        Two watches whose signatures match would walk the same 7,201
        probes to the same articles and the same images, so the second
        walk is pure waste. Everything `Compositor.warm_hover_articles`
        actually reads goes in:

        - the SKIN, which decides every seat, figure, ring and palette;
        - the DAY context's cache key (a new day speaks new articles);
        - `is_daylight`, because the day/night mechanism swaps whole
          depictions (Ghosts/Exegol, virtue/vice) — two watches in
          different cities can share a date and still differ here;
        - the DIAMETER, which decides the pixel heights that get built.

        The daylight state comes from `_effective_is_daylight()` — the
        controller's own answer, honoring a running Time Travel
        simulation — rather than the compositor's `_last_tick`, which is
        only populated by a real paint and would leave the signature
        permanently None in any headless context.

        The skin enters through its `repr`, not through `hash`: several
        of its specs hold dicts, so the object is genuinely unhashable,
        and hashing a hand-picked subset of fields would silently stop
        noticing whichever field someone adds next. The repr covers
        every field automatically, carries no object addresses (pinned
        by `tests/test_sync_freeze.py`), and is identical for two
        watches built from the same settings. Anything unexpected
        returns None, and None always means SWEEP."""
        if self._day is None or not self._skin.legend:
            return None
        try:
            material = repr((
                repr(self._skin),
                self._day.cache_key,
                self._effective_is_daylight(),
                float(self._settings.diameter),
            ))
        except Exception:
            return None
        return hashlib.sha1(material.encode("utf-8")).hexdigest()

    def hover_sweep(self):
        """This watch's hover warm as a callable, for the shared warm
        thread to run LAST (owner 2026-07-28: "HOVER odloži dok se ne
        učita"). Bound late — the compositor it sweeps is whichever one
        is installed when the sweep actually starts."""
        return self._warm_hover_articles

    def _start_hover_warm(self) -> None:
        """Obsolete any running sweep and start a fresh one — called on
        skin install and day change (a new skin/day speaks new articles;
        a warm re-run costs header reads only).

        With a manager attached the sweep is QUEUED on the one shared
        warm worker rather than given a thread of its own; see
        `_on_hover_warm`."""
        if self._discarded:
            return
        self._hover_warm_generation += 1
        if self._on_hover_warm is not None:
            self._on_hover_warm(self)
            return
        threading.Thread(
            target=self._warm_hover_articles, daemon=True
        ).start()

    def _warm_hover_articles(self) -> None:
        compositor = self._compositor
        generation = self._hover_warm_generation
        compositor.warm_hover_articles(
            float(self._settings.diameter),
            should_stop=lambda: self._hover_warm_generation != generation
            or self._compositor is not compositor,
            progress=print,
        )

    def _teardown_windows(self) -> None:
        """Close every open dialog, stop the scheduler and the
        debounced save timer, hide the tray — the shared first half of
        `_prepare_quit()` (Exit: also saves) and `discard()` (Remove
        Watch, ADD WATCH round: never saves — the settings file is
        about to be deleted). The non-modal sextet (ITEM 1, R4 + the
        three R5 mini windows) can now be open at teardown time; close
        them explicitly instead of leaving them to the process
        teardown, so their own `finished` handlers (and
        WA_DeleteOnClose) run the ordinary way rather than being cut
        off mid-flight.

        The hover poller and the legend popup are torn down here too
        (bug 2026-07-29): for Exit the dying process hid them, but a
        REMOVED watch would otherwise keep polling the global cursor
        and could leave its tooltip window on screen with no watch
        behind it."""
        self._widget.mark_closing()
        for dialog in (
            self._encyclopedia, self._observatory, self._watch_face,
        ):
            if dialog is not None:
                dialog.close()
        self._scheduler.stop()
        # THE LEAKED FILTER (owner bug 2026-08-06, root cause found in
        # his crash.log: 640 `Internal C++ object (ClockWidget) already
        # deleted` tracebacks, every one of them from
        # `native.py -> _on_wake`). A native event filter is installed on
        # the APPLICATION, so it outlives the watch that installed it —
        # every REMOVED watch left a zombie behind that kept ticking a
        # dead dial on every clock change for the rest of the session,
        # and each one made the next SYNC storm worse. Uninstall it in
        # the one teardown both Exit and Remove Watch run through.
        self._app.removeNativeEventFilter(self._power_filter)
        if self._wake_timer.isActive():
            self._wake_timer.stop()
        if self._flip_timer.isActive():
            self._flip_timer.stop()
        if self._save_timer.isActive():
            self._save_timer.stop()
        self._hover_poller.stop()
        self._legend.dismiss()
        self._tray.hide()

    def discard(self) -> None:
        """Remove Watch's own teardown (ADD WATCH round, owner
        INSTRUCTION.txt item 2, sealed 2026-07-21): identical window/
        scheduler/tray teardown as Exit but deliberately skips the
        save — [the manager](watch_manager.md) deletes this watch's
        settings file right after this call returns, so writing it
        first would just recreate what is about to be removed.

        THE DIAL ITSELF DIES HERE (owner bug 2026-07-29, root cause).
        `_teardown_windows()` alone hides the TRAY icon and stops the
        scheduler but leaves the WINDOW on screen — invisible on Exit,
        where the process death takes it, but on Remove Watch it left
        a live ghost dial the user could still see and DRAG. Dragging
        it fired `moved` → `_on_widget_moved` → the debounced
        `_flush_position`, which RE-CREATED the settings file the
        manager had just deleted, so the removed watch came back on the
        next launch. Closing the window kills both symptoms at the
        source; `_discarded` is the belt to that suspender (any
        already-queued save is refused)."""
        self._discarded = True
        self._teardown_windows()
        self._widget.close()
        self._widget.deleteLater()
        self._legend.deleteLater()

    def _prepare_quit(self) -> None:
        """Everything Exit needs from THIS watch except the final
        shared `app.quit()` — split out (ADD WATCH round) so the
        manager's `quit_all()` can run it for every watch before
        quitting the process exactly once."""
        self._teardown_windows()
        self._capture_position()
        try:
            self._store.save(self._settings)
        except OSError as error:
            # Last chance to be seen — the tray balloon would die with the
            # process, so this one failure mode gets a blocking dialog.
            self._critical_box(
                f"Settings could not be saved on exit:\n{self._store.path}\n\n{error}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
        profiling.flush()

    def quit(self) -> None:
        """Standalone Exit (no manager attached — every test in this
        suite predating ADD WATCH, and the default `on_exit` a bare
        `WatchController` falls back to): this watch's own teardown,
        then quit the process."""
        self._prepare_quit()
        self._app.quit()

    # --- Clock ------------------------------------------------------------------

    @profiling.timed("Tick")
    def _on_tick(self, clock_jumped: bool) -> None:
        if self._simulation is not None and monotonic() >= self._simulation_ends:
            self._simulation = None
            self._sim_cycles = 0
            self._day = None                # force the rebuild back to the present
        if self._simulation is not None:
            now = self._simulated_moment()
            observer = self._simulation[1]
            cycles = self._sim_cycles
        else:
            now = datetime.now(self._tz)
            observer = self._observer
            cycles = 0
        day_key = (now.date(), now.utcoffset())
        first_day_build = self._day is None
        # A CLOCK JUMP AND A NEW DAY ARE NOT THE SAME EVENT (owner bug
        # 2026-08-06, measured). Both rebuild the day context — a jump
        # may have crossed midnight, a zone, or a Time Travel target —
        # but only a genuinely NEW DAY speaks new ARTICLES. A Windows
        # NTP correction of 5-10 s changes not one hover text, and the
        # sweep it used to trigger is the most expensive thing this app
        # owns: 7,201 pure-Python probes per watch (the owner's
        # profiling.json: "Hover warmup" max 58.2 s), started by every
        # watch at once. Five watches x one SYNC = a two-minute freeze.
        day_changed = first_day_build or self._day.cache_key != day_key
        if day_changed or clock_jumped:
            try:
                with profiling.measure("Day context"):
                    # The repositories take the REAL astronomical year
                    # (deep travel un-shifts the proxy frame) and answer
                    # in the SAME frame — canonical_proxy and the repos
                    # share proxy_cycles, so the anchors always bracket.
                    astro_year = real_year(now.year, cycles)
                    # The eclipse catalog (ROADMAP 15h item 11) is the
                    # ONLY Deep Time feed with no bundled fallback —
                    # absent the pack, no eclipse ever draws (the
                    # documented absence rule, Rule #1).
                    eclipses = (
                        self._deep.eclipses_near(now, cycles)
                        if self._deep is not None
                        else ()
                    )
                    self._day = build_day_context(
                        now,
                        observer,
                        self._seasons.year_anchors(astro_year),
                        self._moon_phases.moon_window(astro_year),
                        eclipses,
                    )
                    if cycles:
                        # Stamp the frame on the context (display sites
                        # un-shift years; the illumination evaluates at
                        # the real epoch) and rename the Chinese year
                        # from the REAL year — a 400-year shift moves
                        # the sexagenary cycle by 40.
                        self._day = dataclasses.replace(
                            self._day,
                            deep_cycles=cycles,
                            chinese_name=chinese_name_of_year(
                                real_year(self._day.chinese_start.year, cycles)
                            ),
                        )
            except Exception as error:
                # Bundled data unreadable, out of coverage, or schema-
                # malformed (KeyError/TypeError from a bad year entry) —
                # nothing the app can do; die visibly, never tick a wrong
                # dial and never freeze silently.
                self._critical_box(
                    f"Astronomical data unavailable:\n{error!r}",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok,
                )
                raise SystemExit(1) from error
            self._compositor.set_day(self._day)
            if day_changed and not first_day_build:
                # A NEW day (or a travel jump that landed on a different
                # date) speaks new articles — the startup chain already
                # covers the first build, and a bare clock correction
                # inside the SAME day speaks nothing new at all.
                self._start_hover_warm()
        tick = build_tick_state(now, self._day)
        # THE NIGHT INVERSION (ring_rework §1): report the SUN'S ACTUAL
        # STATE — above the horizon or below — and say whether the dial
        # may TURN to meet it. A clock jump is not a sunset and a
        # day-context rebuild is not a transition (owner bug
        # 2026-08-06), so both APPLY the phase instantly, with no
        # intermediate frame and no hover sweep. On a polar day or a
        # polar night nothing ever changes here and nothing ever fires.
        if self._compositor.note_daylight(
            tick.is_daylight, animate=not (clock_jumped or day_changed)
        ):
            self._flip_timer.start()
        self._widget.set_tick(tick)

    def _on_flip_frame(self) -> None:
        """One frame of the turning move — and the last one stops the
        timer, so animation-cadence repaints exist ONLY for the move's
        own ~1.5 s."""
        if self._discarded:
            # A discarded watch has no window left to repaint — the
            # timer is stopped in `_teardown_windows` too, this is the
            # in-flight frame that was already queued when it went.
            self._flip_timer.stop()
            return
        if not self._compositor.flip_active():
            self._flip_timer.stop()
        self._widget.update()

    def _on_wake(self) -> None:
        """Resume-from-sleep / system clock change. Runs inside the
        native event filter, so it does the cheapest possible thing:
        re-aim the coalescing shot and return. See `_wake_timer`."""
        if self._discarded:
            return
        self._wake_timer.start()

    def _refresh_after_jump(self) -> None:
        """The coalesced burst's ONE refresh."""
        self._on_tick(clock_jumped=True)

    def _on_screen_changed(self) -> None:
        """Qt fires this for ANY monitor crossing — but two identical
        screens (the owner's 2x 4K/32") share one pixel density, and
        crossing between them must cost NOTHING. The rasterized caches
        only die when the DPR actually changes."""
        dpr = self._widget.devicePixelRatioF()
        if dpr == self._last_dpr:
            return
        self._last_dpr = dpr
        self._compositor.invalidate()
        self._widget.update()

    # --- Settings ---------------------------------------------------------------

    def _load_settings_or_recover(self) -> Settings:
        try:
            return self._store.load()
        except SettingsCorruptError as error:
            choice = self._critical_box(
                (
                    f"The settings file is corrupt and cannot be read:\n"
                    f"{error.path}\n\n{error.cause}\n\n"
                    f"Reset settings (the broken file is kept as a .bak backup)?"
                ),
                QMessageBox.StandardButton.Reset | QMessageBox.StandardButton.Abort,
                QMessageBox.StandardButton.Reset,
            )
            if choice != QMessageBox.StandardButton.Reset:
                raise SystemExit(1) from error
            try:
                self._store.quarantine()
                fresh = Settings()
                self._store.save(fresh)
            except OSError as os_error:
                self._critical_box(
                    f"Settings could not be reset:\n{self._store.path}\n\n{os_error}",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok,
                )
                raise SystemExit(1) from os_error
            return fresh
        except OSError as error:
            # Unreadable (locked / permission denied) is not corrupt — the
            # file is left untouched and defaults are used for this session.
            choice = self._critical_box(
                (
                    f"The settings file cannot be read:\n"
                    f"{self._store.path}\n\n{error}\n\n"
                    f"Continue with default settings for this session "
                    f"(the file is left untouched)?"
                ),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Abort,
                QMessageBox.StandardButton.Ok,
            )
            if choice != QMessageBox.StandardButton.Ok:
                raise SystemExit(1) from error
            return Settings()

    def _on_widget_moved(self) -> None:
        self._save_timer.start()

    def _collect_secret(self, char: str) -> None:
        """Typing HIDDEN_MODE_SECRET on the focused dial unlocks the
        hidden extras — the Four Greetings on the ring jewels, in the
        Encyclopedia's Trinity topic, and, bound to their CANONICAL
        home (ROADMAP queue #6), a second reading in the Encyclopedia's
        Seasons topic. The unlock lives for THIS SESSION only (owner
        2026-07-15: every launch asks for the code again — nothing
        persists)."""
        if self._hidden_unlocked:
            return
        secret = identity.HIDDEN_MODE_SECRET
        self._secret_buffer = (self._secret_buffer + char)[-len(secret):]
        if self._secret_buffer != secret:
            return
        self._secret_buffer = ""
        self._hidden_unlocked = True
        self._compositor.set_hidden_unlocked(True)
        self._report_action.setVisible(True)   # the Report above Exit
        self._tray.notify(
            self._ui("Hidden mode unlocked"),
            self._ui(
                "The Four Greetings await in the Encyclopedia — "
                "Trinity and Seasons."
            ),
            critical=False,
        )

    def _capture_position(self) -> None:
        self._settings = replace(
            self._settings,
            window_x=self._widget.x(),
            window_y=self._widget.y(),
        )

    def _flush_position(self) -> None:
        # A REMOVED watch never writes again (owner bug 2026-07-29): the
        # manager deleted this file the moment `discard()` returned, and
        # a late save would resurrect the watch on the next launch.
        if self._discarded:
            return
        self._capture_position()
        try:
            self._store.save(self._settings)
        except OSError as error:
            print(f"settings save failed: {error}", file=sys.stderr)
            # One balloon per failure streak — a dialog for every debounced
            # save during a drag would storm the user.
            if not self._save_failed:
                self._save_failed = True
                self._tray.notify(
                    self._ui("Settings could not be saved"),
                    f"{self._store.path}\n{error}",
                )
        else:
            self._save_failed = False

    def _position_widget(self) -> None:
        if self._settings.window_x is not None and self._settings.window_y is not None:
            remembered = QRect(
                self._settings.window_x,
                self._settings.window_y,
                self._widget.width(),
                self._widget.height(),
            )
            # Any attached screen showing part of the dial is good enough —
            # clamping to the primary screen would destroy multi-monitor
            # placements on every restart.
            for screen in QGuiApplication.screens():
                if screen.availableGeometry().intersects(remembered):
                    self._widget.move(remembered.topLeft())
                    return
        # First run, or the remembered spot is on no attached screen
        # (monitors unplugged/rearranged): center on the primary screen.
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self._widget.move(
            screen.center().x() - self._widget.width() // 2,
            screen.center().y() - self._widget.height() // 2,
        )

    # --- Menu ---------------------------------------------------------------------

    def _symbolism(self) -> SymbolismRepository:
        """The article source with the active language's overlay laid
        over the English originals (owner spec: we ship only English;
        the user's machine translates once and caches).

        PROCESS-WIDE, one per language (owner bug 2026-08-06). This used
        to return a NEW repository on every call, and `_install_skin`
        calls it — so a 1.12 MB parse was discarded and redone on every
        settings change, on every watch. The book is the same book."""
        return shared_symbolism(
            self._settings.language, self._translation_overlay or None
        )

    def _encyclopedia_repository(self) -> EncyclopediaRepository:
        """`_symbolism`'s sibling for the Encyclopedia's own content —
        process-wide, one per language, for the same reason. Passed
        explicitly into every `Compositor`: left to its own default the
        compositor builds a private one, and a compositor is rebuilt on
        every skin install."""
        return shared_encyclopedia(
            self._settings.language, self._translation_overlay or None
        )

    def _refresh_watch_title(self) -> None:
        """Keep the menu's TITLE header and the tray hover tooltip in
        sync with the live settings (owner INSTRUCTION.txt item 2A) —
        called from `_install_skin`, the ONE choke point every
        ring/pointer/palette/location change already runs through
        (Rule #5), rather than a full menu rebuild: a stay-open menu
        must never close just because its own header text changed
        underneath it. A fresh `_build_menu()` (Settings OK, language
        switch) replaces `_title_label` wholesale and calls this again
        via the `_install_skin` it always runs first — either path ends
        with a correct label. Public entry point: `refresh_title()`
        (ADD WATCH round — the manager calls it on every SURVIVING
        watch after the roster changes). The LOCATION word itself reads
        `self._active_location_name` (R-31), not `settings.city_name`
        directly — a running simulation moves it without ever touching
        the home `Settings`."""
        self._title_label.setText(
            watch_title(
                self._settings, full=self._watch_count() >= 2,
                location_name=self._active_location_name,
            )
        )
        self._tray.set_tooltip(
            watch_title(
                self._settings, full=True,
                location_name=self._active_location_name,
            )
        )

    def _refresh_open_mini_windows(self) -> None:
        """Keep an OPEN Watch Face window in step with the live settings
        — called from `_install_skin` (the SAME choke point
        `_refresh_watch_title` uses) so a change made through ANY path
        (a keyboard shortcut, Settings) never leaves an already-open
        window showing a stale pick. The window's own `refresh()` already
        runs after a pick made THROUGH it (Rule #5 — this is the belt to
        that suspender for every OTHER path)."""
        if self._watch_face is not None:
            self._watch_face.refresh(self._settings, self._watch_face_setters())

    def _install_skin(self, skin) -> None:
        """Swap the rendered skin: fresh compositor, current day kept."""
        self._skin = skin
        self._refresh_watch_title()
        self._refresh_open_mini_windows()
        # Re-reserve the transparent window margin from the LIVE settings
        # (owner slike 1–3, 2026-07-17): earth/moon scale, hover-enlarge
        # and letter scale all feed it, so the window re-sizes to fit
        # exactly (no waste, no clip) on every skin install — the ONE
        # point where a size/hover/letter slider takes effect.
        self._widget.set_dial_diameter(
            self._settings.diameter,
            defaults.dial_window_margin_fraction(skin),
        )
        self._compositor = Compositor(
            skin, shared_cache(), self._symbolism(),
            overlay=self._translation_overlay,
            encyclopedia=self._encyclopedia_repository(),
        )
        self._compositor.set_hidden_unlocked(self._hidden_unlocked)
        self._widget.set_renderer(self._compositor)
        if self._day is not None:
            self._compositor.set_day(self._day)
        # The Seconds element switch also changes the tick cadence —
        # and so does the small-seconds slot (owner 2026-07-14).
        self._scheduler.set_per_second(
            (skin.hands.second is not None and self._settings.show_seconds)
            or slot_seconds(self._settings)
        )
        self._widget.update()
        if self._day is not None:
            # The new skin speaks new articles (theme, slots, pointer) —
            # re-warm them in the background (owner 2026-07-18).
            self._start_hover_warm()

    # --- Translation (owner spec: translate once, cache, display) -----------------

    def _apply_language(self, start_missing: bool) -> None:
        """Load the cached overlay for the chosen language and, when
        entries are missing (first pick, or the English corpus grew),
        translate them in a background thread — the dial keeps running
        and the texts switch when the cache completes."""
        language = self._settings.language
        if language == "en":
            self._translation_overlay = {}
            return
        store = TranslationStore()
        self._translation_overlay = store.load(language)
        if not start_missing or self._translation_thread is not None:
            return
        # ONE RUN PER LANGUAGE FOR THE WHOLE PROCESS (owner bug
        # 2026-08-06). `_translation_thread` is per WATCH, so five
        # watches sharing a language each started a worker: the same
        # corpus translated five times through the same endpoint, and
        # five writers on one cache file. The claim is taken BEFORE the
        # corpus is built so the 1.5 MB of reading behind `missing()`
        # happens once too.
        if not claim_translation(language):
            return
        started = False
        try:
            if store.missing(language, collect_corpus()):
                self._translation_thread = threading.Thread(
                    target=self._translate_worker, args=(language,), daemon=True
                )
                self._translation_thread.start()
                started = True
        finally:
            if not started:
                release_translation(language)
        if started:
            self._translation_poller.start()
            self._tray.notify(
                self._ui("Translating"),
                self._ui(
                    "Preparing {language} — the clock keeps running; "
                    "texts switch when ready."
                ).format(language=constants.TRANSLATION_LANGUAGES[language]),
                critical=False,
            )

    def _translate_worker(self, language: str) -> None:
        """Background thread: translate the missing corpus entries in
        resumable chunks — every chunk persists, so a network failure
        mid-run continues where it stopped on the next attempt."""
        try:
            store = TranslationStore()
            corpus = collect_corpus()
            while True:
                missing = store.missing(language, corpus)
                if not missing:
                    break
                chunk = dict(list(missing.items())[:20])
                store.save(language, chunk, translate_texts(chunk, language))
            self._translation_error = None
        except Exception as error:      # network/JSON — surfaced by the poller
            self._translation_error = error
        finally:
            # Always hand the language back, success or failure — a claim
            # left standing would block every later retry for the rest of
            # the session (the run is resumable by design).
            release_translation(language)

    def _poll_translation(self) -> None:
        thread = self._translation_thread
        if thread is None or thread.is_alive():
            return
        self._translation_poller.stop()
        self._translation_thread = None
        failed = self._translation_error
        self._translation_error = None
        language = self._settings.language
        if language != "en":
            # Apply whatever completed (chunks persist) either way —
            # including the menu, whose chrome strings live in the
            # same overlay (Phase 2).
            self._translation_overlay = TranslationStore().load(language)
            # Fresh text landed: the process-wide repositories cached for
            # this language now hold the PRE-translation strings, so drop
            # them before the skin install below reads them again.
            reset_shared_symbolism()
            reset_shared_encyclopedia()
            self._install_skin(build_skin(self._settings, self._active_location_display))
            self._menu = self._build_menu()
            self._widget.set_menu(self._menu)
            self._widget.set_show_action(self._show_action)
            self._tray.set_menu(self._menu)
        if failed is not None:
            self._tray.notify(
                self._ui("Translation incomplete"),
                self._ui(
                    "{error} — finished parts are shown; pick the language "
                    "again in Settings to resume."
                ).format(error=failed),
            )
        elif language != "en":
            self._tray.notify(
                self._ui("Translation ready"),
                self._ui("{language} is active.").format(
                    language=constants.TRANSLATION_LANGUAGES[language]
                ),
                critical=False,
            )

    def _show_if_normal_z_mode(self) -> None:
        """The tray double-click / menu "Show" gesture (owner
        2026-07-18, ROADMAP 15h): a no-op outside "normal" z-mode,
        where raising the dial is meaningless (bottom never rides above
        anything, top already does)."""
        if self._settings.z_mode == "normal":
            self._widget.raise_and_focus()

    def _set_click_through(self, enabled: bool) -> None:
        self._widget.set_click_through(enabled)
        if enabled:
            self._hover_poller.start()
        else:
            self._hover_poller.stop()
            self._legend.dismiss()
            # The poller was the only hover driver in this mode — clear
            # its target or the last element stays enlarged (review
            # finding: the cursor sits on the tray, not the dial).
            if self._compositor.set_hover(
                -1.0e9, -1.0e9, float(self._widget.dial_diameter)
            ):
                self._widget.update()
        self._settings = replace(self._settings, click_through=enabled)
        self._flush_position()

    def _poll_hover(self) -> None:
        cursor = QCursor.pos()
        if self._legend.isVisible() and self._legend.geometry().contains(cursor):
            return                      # the user is scrolling the article
        local = self._widget.mapFromGlobal(cursor)
        size = float(self._widget.dial_diameter)
        margin = self._widget.margin_px
        x, y = local.x() - margin, local.y() - margin
        tip = None
        inside = 0 <= x < size and 0 <= y < size
        if QApplication.queryKeyboardModifiers() & getattr(
            Qt.KeyboardModifier, defaults.HOVER_BYPASS_MODIFIER
        ):
            # The held bypass key silences hovers in click-through
            # mode too (owner 2026-07-16) — same rule as the widget's
            # mouseMoveEvent.
            inside = False
        if self._compositor.set_hover(
            x if inside else -1.0e9,
            y if inside else -1.0e9,
            size,
        ):
            self._widget.update()       # hover-enlarge in click-through mode
        if inside:
            tip = self._compositor.tooltip_at(x, y, size)
        if tip:
            if tip != self._last_hover_tip:
                self._legend.show_html(tip, cursor)
        elif self._last_hover_tip:
            self._legend.dismiss()
        self._last_hover_tip = tip

    def _set_diameter(self, diameter: int) -> None:
        if diameter == self._settings.diameter:
            return
        self._settings = replace(self._settings, diameter=diameter)
        # The four Earth label pills and the compact slider live inside
        # the Design window now (R5 MENU REWORK) — its own `refresh()`
        # re-reads `settings.diameter`/`earth_label` fresh, so nothing
        # here needs mirroring into a controller-held widget any more.
        self._widget.set_dial_diameter(diameter)
        self._compositor.invalidate()
        self._widget.update()
        self._flush_position()          # persists position AND the new diameter

    @staticmethod
    def _critical_box(text: str, buttons, default) -> int:
        box = QMessageBox(QMessageBox.Icon.Critical, identity.APP_NAME, text, buttons)
        box.setDefaultButton(default)
        # Without a parent window the box can open buried under other
        # windows (verified on Windows 11) — the error must be seen.
        box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        return box.exec()
