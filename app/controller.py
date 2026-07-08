"""Composition root — the only object that knows everyone.

Owns settings, the clock window, the tray, the repositories, the
compositor and the minute scheduler. Tick flow: read the wall clock
fresh -> rebuild the day context when (local date, UTC offset) changed
-> build the tick state -> repaint.
"""

import dataclasses
import sys
from datetime import datetime
from time import monotonic
from zoneinfo import ZoneInfo

import astral

from PySide6.QtCore import QObject, QRect, Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QCursor, QGuiApplication
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QToolTip

from app import native
from app.scheduler import MinuteScheduler
from app.settings_store import Settings, SettingsCorruptError, SettingsStore, replace
from app.time_travel import TimeTravelDialog
from app.tray import TrayController
from app.widget import ClockWidget
from config import constants, defaults, paths
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from skins import resolver
from skins.manifest import missing_assets
from skins.packs import SkinValidationError


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
        self._skin = self._resolve_skin_or_recover(self._settings.skin)
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
        self._compositor = Compositor(self._skin, AssetCache())
        self._day = None
        # Time Travel: a frozen (moment, observer) rendered instead of the
        # present until the deadline passes.
        self._simulation: tuple[datetime, astral.Observer] | None = None
        self._simulation_ends: float = 0.0
        self._widget.set_renderer(self._compositor)
        seconds_hand = (
            self._skin.hands.second is not None and defaults.SECONDS_HAND_ENABLED
        )
        self._scheduler = MinuteScheduler(self._on_tick, self, per_second=seconds_hand)
        # Resume-from-sleep and clock/zone changes refresh immediately —
        # the scheduled tick never fired while the machine slept.
        self._power_filter = native.PowerEventFilter(self._on_wake)
        app.installNativeEventFilter(self._power_filter)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(defaults.SETTINGS_WRITE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self._flush_position)
        self._widget.moved.connect(self._on_widget_moved)

        # In click-through mode the window receives no mouse input, so the
        # hover tooltips are driven by polling the global cursor instead.
        self._hover_poller = QTimer(self)
        self._hover_poller.setInterval(defaults.CLICK_THROUGH_HOVER_POLL_MS)
        self._hover_poller.timeout.connect(self._poll_hover)
        self._last_hover_tip: str | None = None

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
        if self._settings.click_through:
            self._widget.set_click_through(True)
            self._hover_poller.start()

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
        if self._simulation is not None and monotonic() >= self._simulation_ends:
            self._simulation = None
            self._day = None                # force the rebuild back to the present
        if self._simulation is not None:
            now, observer = self._simulation
        else:
            now = datetime.now(self._tz)
            observer = self._observer
        day_key = (now.date(), now.utcoffset())
        if self._day is None or self._day.cache_key != day_key or clock_jumped:
            try:
                self._day = build_day_context(
                    now,
                    observer,
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

    def _on_wake(self) -> None:
        """Resume-from-sleep / system clock change: full refresh now."""
        self._on_tick(clock_jumped=True)

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

    def _resolve_skin_or_recover(self, name: str):
        try:
            skin = resolver.resolve(name)
        except (KeyError, SkinValidationError) as error:
            self._critical_box(
                f"Skin {name!r} cannot be loaded:\n{error}\n\n"
                f"Continuing with the built-in DOMY skin.",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
            skin = defaults.DEFAULT_SKIN
        return self._apply_display_settings(skin)

    def _apply_display_settings(self, skin):
        """The user's tray choices (pointer variant, gray-wheel contrast)
        win over whatever the skin pack declares."""
        return dataclasses.replace(
            skin,
            pointer=self._settings.pointer,
            gray_contrast=self._settings.gray_contrast,
        )

    def _install_skin(self, skin) -> None:
        """Swap the rendered skin: fresh compositor, current day kept."""
        self._skin = skin
        self._compositor = Compositor(skin, AssetCache())
        self._widget.set_renderer(self._compositor)
        if self._day is not None:
            self._compositor.set_day(self._day)
        self._widget.update()

    def _set_skin(self, name: str) -> None:
        if name == self._settings.skin:
            return
        try:
            skin = resolver.resolve(name)
        except (KeyError, SkinValidationError) as error:
            self._critical_box(
                f"Skin {name!r} cannot be loaded:\n{error}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
            return
        self._install_skin(self._apply_display_settings(skin))
        self._settings = replace(self._settings, skin=name)
        self._flush_position()

    def _set_pointer(self, pointer: str) -> None:
        if pointer == self._settings.pointer:
            return
        self._settings = replace(self._settings, pointer=pointer)
        self._install_skin(dataclasses.replace(self._skin, pointer=pointer))
        self._flush_position()

    def _set_gray_contrast(self, contrast: str) -> None:
        if contrast == self._settings.gray_contrast:
            return
        self._settings = replace(self._settings, gray_contrast=contrast)
        self._install_skin(dataclasses.replace(self._skin, gray_contrast=contrast))
        self._flush_position()

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        skin_menu = menu.addMenu("Skin")
        skin_group = QActionGroup(menu)
        skin_group.setExclusive(True)
        for name in sorted(resolver.discover()):
            action = QAction(name.upper(), menu)
            action.setCheckable(True)
            action.setChecked(name == self._settings.skin)
            action.triggered.connect(lambda checked, skin=name: self._set_skin(skin))
            skin_group.addAction(action)
            skin_menu.addAction(action)
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
        pointer_menu = menu.addMenu("Pointer")
        pointer_group = QActionGroup(menu)
        pointer_group.setExclusive(True)
        for variant, arms in sorted(
            constants.POINTER_POINTS.items(), key=lambda item: item[1]
        ):
            action = QAction(f"{variant.capitalize()} ({arms})", menu)
            action.setCheckable(True)
            action.setChecked(variant == self._settings.pointer)
            action.triggered.connect(
                lambda checked, pointer=variant: self._set_pointer(pointer)
            )
            pointer_group.addAction(action)
            pointer_menu.addAction(action)
        contrast_menu = menu.addMenu("Gray wheel")
        contrast_group = QActionGroup(menu)
        contrast_group.setExclusive(True)
        for variant in constants.GRAY_CONTRAST_VARIANTS:
            action = QAction(f"{variant.capitalize()} contrast", menu)
            action.setCheckable(True)
            action.setChecked(variant == self._settings.gray_contrast)
            action.triggered.connect(
                lambda checked, contrast=variant: self._set_gray_contrast(contrast)
            )
            contrast_group.addAction(action)
            contrast_menu.addAction(action)
        menu.addSeparator()
        time_travel = QAction("Time Travel…", menu)
        time_travel.triggered.connect(self._open_time_travel)
        menu.addAction(time_travel)
        click_through = QAction("Click-through", menu)
        click_through.setCheckable(True)
        click_through.setChecked(self._settings.click_through)
        click_through.setToolTip(
            "The dial takes no clicks at all (they pass to the desktop); "
            "hover info still works. Turn it back off here in the tray."
        )
        click_through.toggled.connect(self._set_click_through)
        menu.addAction(click_through)
        menu.addSeparator()
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self.quit)
        menu.addAction(exit_action)
        return menu

    def _open_time_travel(self) -> None:
        dialog = TimeTravelDialog()
        if dialog.exec() != TimeTravelDialog.DialogCode.Accepted:
            return
        moment = dialog.moment().replace(second=0, microsecond=0, tzinfo=self._tz)
        observer = astral.Observer(
            latitude=dialog.latitude(), longitude=dialog.longitude()
        )
        self._simulation = (moment, observer)
        self._simulation_ends = monotonic() + defaults.TIME_TRAVEL_DURATION_S
        self._day = None                    # rebuild with the simulated situation
        self._on_tick(clock_jumped=False)

    def _set_click_through(self, enabled: bool) -> None:
        self._widget.set_click_through(enabled)
        if enabled:
            self._hover_poller.start()
        else:
            self._hover_poller.stop()
            QToolTip.hideText()
        self._settings = replace(self._settings, click_through=enabled)
        self._flush_position()

    def _poll_hover(self) -> None:
        cursor = QCursor.pos()
        local = self._widget.mapFromGlobal(cursor)
        size = float(min(self._widget.width(), self._widget.height()))
        tip = None
        if 0 <= local.x() < self._widget.width() and 0 <= local.y() < self._widget.height():
            tip = self._compositor.tooltip_at(local.x(), local.y(), size)
        if tip:
            if tip != self._last_hover_tip:
                QToolTip.showText(cursor, tip, self._widget)
        elif self._last_hover_tip:
            QToolTip.hideText()
        self._last_hover_tip = tip

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
