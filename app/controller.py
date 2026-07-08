"""Composition root — the only object that knows everyone.

Owns settings, the clock window, the tray, the repositories, the
compositor and the minute scheduler. Tick flow: read the wall clock
fresh -> rebuild the day context when (local date, UTC offset) changed
-> build the tick state -> repaint.
"""

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import astral

from PySide6.QtCore import QObject, QRect, Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QGuiApplication
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox

from app.scheduler import MinuteScheduler
from app.settings_store import Settings, SettingsCorruptError, SettingsStore, replace
from app.tray import TrayController
from app.widget import ClockWidget
from config import constants, defaults, paths
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from skins.manifest import missing_assets


class AppController(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self._app = app
        self._store = SettingsStore(paths.settings_path())
        self._settings = self._load_settings_or_recover()
        self._save_failed = False

        self._menu = self._build_menu()
        self._widget = ClockWidget(self._settings.diameter, self._menu)
        self._tray = TrayController(self._menu)

        city = defaults.DEFAULT_CITY
        self._tz = ZoneInfo(city["timezone"])
        self._observer = astral.Observer(
            latitude=city["latitude"], longitude=city["longitude"]
        )
        self._seasons = SeasonsRepository()
        self._moon_phases = MoonPhaseRepository()
        missing = missing_assets(defaults.DEFAULT_SKIN)
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
        self._compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
        self._day = None
        self._widget.set_renderer(self._compositor)
        seconds_hand = (
            defaults.DEFAULT_SKIN.hands.second is not None
            and defaults.SECONDS_HAND_ENABLED
        )
        self._scheduler = MinuteScheduler(self._on_tick, self, per_second=seconds_hand)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(defaults.SETTINGS_WRITE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self._flush_position)
        self._widget.moved.connect(self._on_widget_moved)

    # --- Lifecycle --------------------------------------------------------------

    def run(self) -> None:
        self._on_tick(clock_jumped=False)   # first frame BEFORE show()
        self._position_widget()
        self._widget.show()
        self._tray.show()
        self._scheduler.start()
        # windowHandle() exists only after show(); a monitor/DPI change
        # invalidates every rasterized cache.
        self._widget.windowHandle().screenChanged.connect(self._on_screen_changed)

    def quit(self) -> None:
        self._widget.mark_closing()
        self._scheduler.stop()
        if self._save_timer.isActive():
            self._save_timer.stop()
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
        self._tray.hide()
        self._app.quit()

    # --- Clock ------------------------------------------------------------------

    def _on_tick(self, clock_jumped: bool) -> None:
        now = datetime.now(self._tz)
        day_key = (now.date(), now.utcoffset())
        if self._day is None or self._day.cache_key != day_key or clock_jumped:
            try:
                self._day = build_day_context(
                    now,
                    self._observer,
                    self._seasons.year_anchors(now.year),
                    self._moon_phases.moon_window(now.year),
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
        self._widget.set_tick(build_tick_state(now, self._day))

    def _on_screen_changed(self) -> None:
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

    def _capture_position(self) -> None:
        self._settings = replace(
            self._settings,
            window_x=self._widget.x(),
            window_y=self._widget.y(),
        )

    def _flush_position(self) -> None:
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
                    "Settings could not be saved",
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

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        size_menu = menu.addMenu("Size")
        group = QActionGroup(menu)
        group.setExclusive(True)
        for preset in defaults.SIZE_PRESETS:
            action = QAction(f"{preset} px", menu)
            action.setCheckable(True)
            action.setChecked(preset == self._settings.diameter)
            action.triggered.connect(
                lambda checked, diameter=preset: self._set_diameter(diameter)
            )
            group.addAction(action)
            size_menu.addAction(action)
        menu.addSeparator()
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self.quit)
        menu.addAction(exit_action)
        return menu

    def _set_diameter(self, diameter: int) -> None:
        if diameter == self._settings.diameter:
            return
        self._settings = replace(self._settings, diameter=diameter)
        self._widget.resize(diameter, diameter)
        self._compositor.invalidate()
        self._widget.update()
        self._flush_position()          # persists position AND the new diameter

    @staticmethod
    def _critical_box(text: str, buttons, default) -> int:
        box = QMessageBox(QMessageBox.Icon.Critical, constants.APP_NAME, text, buttons)
        box.setDefaultButton(default)
        # Without a parent window the box can open buried under other
        # windows (verified on Windows 11) — the error must be seen.
        box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        return box.exec()
