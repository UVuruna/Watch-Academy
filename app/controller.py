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
from app.settings_dialog import SettingsDialog
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
from skins.manifest import missing_assets


def build_skin(settings: Settings):
    """The ONE render config: DEFAULT_SKIN with the chosen RING PRESET
    (DOMY and MORPH are ring preset names — nothing more, owner
    decision) and the user's display choices overlaid."""
    preset = defaults.RING_PRESETS[settings.ring]
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        ring=dataclasses.replace(
            defaults.DEFAULT_SKIN.ring,
            asset=preset["asset"],
            letters=preset["letters"],
        ),
    )
    return apply_display_settings(skin, settings)


def apply_display_settings(skin, settings: Settings):
    """The user's choices win over whatever the skin pack declares:
    the tray display scalars, the opacity overrides (twilight alphas
    scale proportionally with the day alphas) and the custom palette
    for the active (pointer, style). Module-level and pure — testable
    without a controller."""
    star = skin.star
    if settings.star_alpha is not None:
        star = dataclasses.replace(
            star,
            day_alpha=settings.star_alpha,
            twilight_alpha=settings.star_alpha
            * (star.twilight_alpha / star.day_alpha),
        )
    weekday = skin.weekday_set
    if settings.weekday_theme != "planets":
        # Themed bodies (SYMBOLISM.md canon): swap in the shared themed
        # art (files carry the ENTITY names) and the canon display
        # names; "planets" keeps the skin's own weekday unit untouched.
        theme_dir = defaults.WEEKDAY_ART_DIR / settings.weekday_theme
        names = defaults.WEEKDAY_THEME_NAMES[settings.weekday_theme]
        files = defaults.WEEKDAY_THEME_FILES[settings.weekday_theme]
        weekday = dataclasses.replace(
            weekday,
            bodies={body: theme_dir / f"{files[body]}.png" for body in names},
            body_names=dict(names),
        )
    background = skin.background
    if settings.aura_day_alpha is not None or settings.aura_twilight_alpha is not None:
        # The Aura's sunlight and twilight opacities are INDEPENDENT
        # overrides (owner spec) — no coupling ratio between them.
        background = dataclasses.replace(
            background,
            day_alpha=(
                settings.aura_day_alpha
                if settings.aura_day_alpha is not None
                else background.day_alpha
            ),
            twilight_alpha=(
                settings.aura_twilight_alpha
                if settings.aura_twilight_alpha is not None
                else background.twilight_alpha
            ),
        )
    return dataclasses.replace(
        skin,
        star=star,
        background=background,
        weekday_set=weekday,
        pointer=settings.pointer,
        umbra_form=settings.umbra_form,
        umbra_contrast=settings.umbra_contrast,
        palette_style=settings.palette_style,
        solar_rotation=settings.solar_rotation,
        octa_slot=settings.octa_slot,
        earth_style=settings.earth_style,
        weekday_theme=settings.weekday_theme,
        legend=settings.legend,
        show_earth=settings.show_earth,
        show_moon=settings.show_moon,
        show_weekday=settings.show_weekday,
        show_pointer=settings.show_pointer,
        colorful=settings.colorful,
        show_seconds=settings.show_seconds,
        palette_override=settings.palettes.get(
            f"{settings.pointer}_{settings.palette_style}"
        ),
    )


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

        self._tz = ZoneInfo(self._settings.timezone)
        self._observer = astral.Observer(
            latitude=self._settings.latitude, longitude=self._settings.longitude
        )
        self._seasons = SeasonsRepository()
        self._moon_phases = MoonPhaseRepository()
        self._skin = build_skin(self._settings)
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
            self._skin.hands.second is not None and self._settings.show_seconds
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

    def _install_skin(self, skin) -> None:
        """Swap the rendered skin: fresh compositor, current day kept."""
        self._skin = skin
        self._compositor = Compositor(skin, AssetCache())
        self._widget.set_renderer(self._compositor)
        if self._day is not None:
            self._compositor.set_day(self._day)
        # The Seconds element switch also changes the tick cadence.
        self._scheduler.set_per_second(
            skin.hands.second is not None and self._settings.show_seconds
        )
        self._widget.update()

    def _set_ring(self, ring: str) -> None:
        if ring == self._settings.ring:
            return
        self._settings = replace(self._settings, ring=ring)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_display_choice(self, key: str, value) -> None:
        """Shared setter behind every display choice: persist and
        REBUILD the render config from scratch — a bare scalar replace
        is not enough for choices that swap assets (the weekday theme
        replaces the body images inside apply_display_settings; a
        scalar-only update left the planets on screen — owner bug
        report, FINAL.txt #6)."""
        if getattr(self._settings, key) == value:
            return
        self._settings = replace(self._settings, **{key: value})
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _add_choice_group(
        self, menu: QMenu, submenu: QMenu, options, current, setter, disabled=()
    ) -> None:
        """One exclusive check-group appended to `submenu`: options are
        (value, label) pairs; values in `disabled` render grayed out."""
        group = QActionGroup(menu)
        group.setExclusive(True)
        for value, label in options:
            action = QAction(label, menu)
            action.setCheckable(True)
            action.setChecked(value == current)
            action.setEnabled(value not in disabled)
            action.triggered.connect(lambda checked, chosen=value: setter(chosen))
            group.addAction(action)
            submenu.addAction(action)

    def _add_choice_submenu(self, menu: QMenu, title: str, options, current, setter) -> QMenu:
        """One exclusive check-group submenu: options are (value, label)."""
        submenu = menu.addMenu(title)
        self._add_choice_group(menu, submenu, options, current, setter)
        return submenu

    def _add_toggle(
        self, menu: QMenu, title: str, checked: bool, setter, tooltip: str | None = None
    ) -> QAction:
        """One checkable on/off action appended to `menu`."""
        action = QAction(title, menu)
        action.setCheckable(True)
        action.setChecked(checked)
        if tooltip is not None:
            action.setToolTip(tooltip)
        action.toggled.connect(setter)
        menu.addAction(action)
        return action

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        settings = self._settings
        self._add_choice_submenu(
            menu, "Ring",
            [(name, name.upper()) for name in sorted(defaults.RING_PRESETS)],
            settings.ring, self._set_ring,
        )
        self._add_choice_submenu(
            menu, "Size",
            [(preset, f"{preset} px") for preset in defaults.SIZE_PRESETS],
            settings.diameter, self._set_diameter,
        )
        # Pointer variant and palette style share ONE dropdown (owner
        # spec), two exclusive groups like the Umbra submenu.
        pointer_menu = self._add_choice_submenu(
            menu, "Pointer",
            [
                (variant, f"{variant.capitalize()} ({arms})")
                for variant, arms in sorted(
                    constants.POINTER_POINTS.items(), key=lambda item: item[1]
                )
            ],
            settings.pointer,
            lambda value: self._set_display_choice("pointer", value),
        )
        pointer_menu.addSeparator()
        self._add_choice_group(
            menu, pointer_menu,
            [
                (style, f"{style.capitalize()} palette")
                for style in constants.PALETTE_STYLES
            ],
            settings.palette_style,
            lambda value: self._set_display_choice("palette_style", value),
        )
        umbra_menu = self._add_choice_submenu(
            menu, "Umbra",
            [
                ("fine", "Fine (16 shades)"),
                ("coarse", "Coarse (13 shades)"),
                ("gradient", "Gradient"),
            ],
            settings.umbra_form,
            lambda value: self._set_display_choice("umbra_form", value),
        )
        umbra_menu.addSeparator()
        self._add_choice_group(
            menu, umbra_menu,
            [
                (variant, f"{variant.capitalize()} contrast")
                for variant in constants.UMBRA_CONTRAST_VARIANTS
            ],
            settings.umbra_contrast,
            lambda value: self._set_display_choice("umbra_contrast", value),
        )
        self._add_choice_submenu(
            menu, "Octa slot",
            [
                ("time", "Time"),
                ("date", "Date"),
                ("day_length", "Day length"),
                ("zodiac_sign", "Astrology sign"),
                ("zodiac_logo", "Astrology logo"),
                ("zodiac_constellation", "Astrology constellation"),
                ("zodiac_text", "Astrology text"),
                ("chinese_logo", "Chinese zodiac logo"),
                ("chinese_text", "Chinese zodiac text"),
            ],
            settings.octa_slot,
            lambda value: self._set_display_choice("octa_slot", value),
        )
        # Elements (owner spec, FINAL.txt #5): on/off switches removing
        # individual dial elements; Earth also nests its style choice.
        elements_menu = menu.addMenu("Elements")
        earth_menu = elements_menu.addMenu("Earth")
        self._add_toggle(
            earth_menu, "Visible", settings.show_earth,
            lambda checked: self._set_display_choice("show_earth", checked),
            "The Earth marker riding the year wheel and showing the date.",
        )
        earth_menu.addSeparator()
        self._add_choice_group(
            menu, earth_menu,
            [("clean", "Clean"), ("atmo", "Atmosphere")],
            settings.earth_style,
            lambda value: self._set_display_choice("earth_style", value),
        )
        for key, label, tip in (
            (
                "show_moon", "Moon",
                "The Moon marker riding its cycle and showing the phase.",
            ),
            (
                "show_weekday", "Weekday",
                "The weekday bodies — the rotating slots and the center.",
            ),
            (
                "show_pointer", "Pointer",
                "The star diamonds. Off: the Aura colors stay, only the "
                "pointer disappears.",
            ),
            (
                "colorful", "Colorful",
                "The Aura palette hues. Off: the day and twilight arcs "
                "are drawn as plain white transparency.",
            ),
            (
                "show_seconds", "Seconds",
                "The seconds hand. Off: it is not drawn and the dial "
                "ticks once per minute.",
            ),
        ):
            self._add_toggle(
                elements_menu, label, getattr(settings, key),
                lambda checked, key=key: self._set_display_choice(key, checked),
                tip,
            )
        self._add_choice_submenu(
            menu, "Weekday theme",
            [
                ("planets", "Planets"),
                ("planet_signs", "Planet signs"),
                ("greek", "Greek gods"),
                ("norse", "Norse gods"),
                ("religion", "Religions"),
                ("profession", "Professions"),
            ],
            settings.weekday_theme,
            lambda value: self._set_display_choice("weekday_theme", value),
        )
        self._add_toggle(
            menu, "Legend", settings.legend,
            lambda checked: self._set_display_choice("legend", checked),
            "All hover texts. Off: the dial shows nothing on hover — "
            "combined with Click-through it has zero interaction.",
        )
        self._add_toggle(
            menu, "Solar rotation", settings.solar_rotation,
            lambda checked: self._set_display_choice("solar_rotation", checked),
            "On: the star points at true solar noon. Off: Star, Aura and "
            "Umbra stand upright (12/24 at the top) for reading exact "
            "planet and season positions.",
        )
        menu.addSeparator()
        settings_action = QAction("Settings…", menu)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)
        time_travel = QAction("Time Travel…", menu)
        time_travel.triggered.connect(self._open_time_travel)
        menu.addAction(time_travel)
        self._add_toggle(
            menu, "Click-through", self._settings.click_through,
            self._set_click_through,
            "The dial takes no clicks at all (they pass to the desktop); "
            "hover info still works. Turn it back off here in the tray.",
        )
        menu.addSeparator()
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self.quit)
        menu.addAction(exit_action)
        return menu

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self._settings, self._skin)
        if dialog.exec() != SettingsDialog.DialogCode.Accepted:
            return
        new_settings = dialog.result_settings()
        location_changed = (
            new_settings.latitude,
            new_settings.longitude,
            new_settings.timezone,
        ) != (self._settings.latitude, self._settings.longitude, self._settings.timezone)
        self._settings = new_settings
        if location_changed:
            self._tz = ZoneInfo(new_settings.timezone)
            self._observer = astral.Observer(
                latitude=new_settings.latitude, longitude=new_settings.longitude
            )
            self._day = None                # full rebuild for the new place
        # Rebuild from DEFAULT_SKIN so cleared overrides (back to "skin
        # default") actually clear instead of sticking.
        self._install_skin(build_skin(self._settings))
        self._on_tick(clock_jumped=False)
        self._flush_position()

    def _open_time_travel(self) -> None:
        dialog = TimeTravelDialog(
            self._settings.latitude, self._settings.longitude
        )
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
