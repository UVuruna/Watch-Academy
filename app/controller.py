"""Composition root — the only object that knows everyone.

Owns settings, the clock window, the tray, the repositories, the
compositor and the minute scheduler. Tick flow: read the wall clock
fresh -> rebuild the day context when (local date, UTC offset) changed
-> build the tick state -> repaint.
"""

import dataclasses
import sys
import random
import threading
from datetime import datetime, timedelta, timezone
from time import monotonic
from zoneinfo import ZoneInfo

import astral

from PySide6.QtCore import QObject, QRect, Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QCursor, QGuiApplication
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox

from app import native
from app.encyclopedia import EncyclopediaDialog
from app.guide import GuideDialog
from app.legend_popup import LegendPopup
from app.scheduler import MinuteScheduler
from app.settings_dialog import SettingsDialog
from app.settings_store import (
    Settings,
    SettingsCorruptError,
    SettingsStore,
    replace,
    rotation_themes,
)
from app.time_travel import TimeTravelDialog
from app.tray import TrayController, logo_icon
from app.widget import ClockWidget
from config import constants, defaults, paths
from config.ui_text import ui
from core.clock_state import build_day_context, build_tick_state
from data.hands import HAND_NAMES, hand_packs
from data.moon_phases import MoonPhaseRepository
from data.rings import ring_presets
from data.seasons import SeasonsRepository
from data.symbolism import SymbolismRepository
from data.translations import TranslationStore, collect_corpus, translate_texts
from render.assets import AssetCache
from render.compositor import Compositor
from skins.manifest import HandSpec, HandsSpec, missing_assets


def _letter_metal(position: int, layout: dict, finish: str) -> str:
    """The owner's metal rules (extended with bronze 2026-07-12):
    4-letter layouts — the trio of one metal forms the layout's
    TRIANGLE and the remaining letter wears the ACCENT metal (gold ->
    3 gold + 1 silver; silver -> 3 silver + 1 gold; bronze -> 3 bronze
    + 1 silver); the SEAL wears the ONE finish metal on all six."""
    if not layout["triangle"] or position in layout["triangle"]:
        return finish
    return "gold" if finish == "silver" else "silver"


def _theme_metal(settings: Settings, theme: str) -> str:
    """The METAL a bronze-plate theme wears (owner 2026-07-12):
    follow-the-ring wins, then the per-theme Settings choice, then
    bronze — the art as drawn. Non-metal themes are always bronze."""
    if theme not in constants.METAL_THEMES:
        return "bronze"
    if settings.theme_metal_follow_ring:
        return settings.ring_finish
    return settings.theme_metals.get(theme, "bronze")


class _StayOpenMenu(QMenu):
    """A menu whose CHECKABLE items do not close it (owner menu rework
    2026-07-13: several settings in one visit) — plain actions (Exit,
    Settings…) close as usual; Escape or clicking away closes too."""

    def mouseReleaseEvent(self, event) -> None:
        action = self.actionAt(event.position().toPoint())
        if (
            action is not None
            and action.isCheckable()
            and action.isEnabled()
        ):
            action.trigger()
            event.accept()
            return
        super().mouseReleaseEvent(event)


def _next_rotation_theme(current: str, selected: tuple[str, ...]) -> str:
    """The theme AFTER `current` in the rotation list (cyclic); a
    current theme outside the list starts it from the top."""
    if current in selected:
        return selected[(selected.index(current) + 1) % len(selected)]
    return selected[0]


def _earth_continent(settings: Settings) -> str:
    """The Earth-marker art variant for the ACTIVE location (owner bug
    2026-07-12: the marker was always Europe). The picker's continent
    decides ("Americas" splits by latitude — the art has north and
    south); hand-tuned coordinates without a picked city fall back to
    a coarse geographic estimate."""
    picker = settings.city_path[0] if settings.city_path else None
    if picker == "Americas":
        # Owner rule: Central America and the Caribbean wear the
        # north_america art — only the South America subregion goes south.
        subregion = settings.city_path[1] if len(settings.city_path) > 1 else ""
        return (
            "south_america" if subregion == "South America" else "north_america"
        )
    named = {
        "Africa": "africa", "Asia": "asia",
        "Europe": "europe", "Oceania": "oceania",
    }
    if picker in named:
        return named[picker]
    lat, lon = settings.latitude, settings.longitude
    if lon < -30.0:
        return "north_america" if lat >= 8.5 else "south_america"
    if lat < -10.0 and lon >= 110.0:
        return "oceania"
    if lon < 35.0:
        return "europe" if lat >= 35.0 else "africa"
    if lon < 52.0 and lat < 12.0:
        return "africa"                  # the Horn and Madagascar
    return "europe" if lon < 45.0 and lat >= 40.0 else "asia"


def _resolve_hands(settings: Settings):
    """The chosen HAND PACK (owner spec 2026-07-12) resolved into a
    HandsSpec: image sizes read here (header-only), pivots and z-order
    from the pack's hands.json; tip reach targets from defaults. A
    vanished USER pack falls back to CLASSIC with a stderr note
    (documented — an uninstalled pack must not brick the startup);
    user-pack art is desaturated so the clock tint can recolor it."""
    from PySide6.QtGui import QImageReader

    packs = hand_packs()
    chosen = next(
        (name for name in packs if name.lower() == settings.hands.lower()),
        None,
    )
    if chosen is None:
        print(
            f"hand pack {settings.hands!r} is gone — using CLASSIC",
            file=sys.stderr,
        )
        chosen = "CLASSIC"
    pack = packs[chosen]
    specs = {}
    for hand in HAND_NAMES:
        path = pack["files"][hand]
        size = QImageReader(str(path)).size()
        if size.height() <= 0:
            raise ValueError(f"hand pack {chosen!r}: unreadable {path}")
        x, y = pack["pivots"][hand]
        specs[hand] = HandSpec(
            asset=path,
            natural_height=float(size.height()),
            pivot_y=y,
            pivot_x_fraction=None if x is None else x / size.width(),
        )
    bundled = pack["dir"].parent == paths.assets_dir() / "hands"
    return HandsSpec(
        hour=specs["hours"],
        minute=specs["minutes"],
        second=specs["seconds"],
        minute_reach_fraction=defaults.HAND_MINUTE_REACH_FRACTION,
        second_reach_fraction=defaults.HAND_SECOND_REACH_FRACTION,
        z_order=pack["z_order"],
        desaturate=not bundled,
    )


def build_skin(settings: Settings):
    """The ONE render config: DEFAULT_SKIN with the chosen RING PRESET
    CARD (Database/ring_presets.json + the user's custom cards — owner
    spec: {name, positions, letters}, the positions signature picks the
    layout/face), the letter art of the chosen finish, the chosen HAND
    PACK and the user's display choices overlaid."""
    card = ring_presets(settings.custom_rings)[settings.ring]
    layout = constants.RING_LAYOUTS[card["layout"]]
    letters = {}
    letter_art = {}
    for position, glyph in zip(card["positions"], card["letters"]):
        hour = position % 24                     # cards say 24, hours say 0
        letters[hour] = glyph
        filename = constants.RING_LETTER_FILES[glyph]
        metal = _letter_metal(position, layout, settings.ring_finish)
        if metal != "gold":
            # Silver and bronze letters are PRE-RENDERED art (owner
            # decision — setup/make_silver_letters.py and
            # make_bronze_letters.py), not a runtime effect.
            filename = f"{filename.rsplit('.', 1)[0]}_{metal}.png"
        letter_art[hour] = defaults.RING_LETTER_ART_DIR / filename
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        ring=dataclasses.replace(
            defaults.DEFAULT_SKIN.ring,
            asset=defaults.RING_FACE_DIR / layout["face"],
            letters=letters,
            letter_art=letter_art,
        ),
        hands=_resolve_hands(settings),
    )
    return apply_display_settings(skin, settings)


def _slot_seconds(settings: Settings) -> bool:
    """Whether any ENABLED slot runs the small-seconds complication
    (owner 2026-07-14) — the big hand yields and its Elements toggle
    grays out."""
    if settings.show_weekday and settings.weekday_slot == "seconds":
        return True
    if settings.show_octa_slot and settings.octa_slot == "seconds":
        return True
    return (
        settings.show_third_slot
        and settings.show_octa_slot
        and settings.third_slot == "seconds"
    )


def _effective_weekday_slot(settings: Settings) -> str:
    """The 1st slot's effective mode. Under the owner's SLOT MATRIX
    (2026-07-14) every mode is real under every pointer — the matrix
    gives it a seat. The single lock: the Seasons with all THREE
    slots up keep the 1st on the weekday unit (owner: mora 1st da
    bude weekday)."""
    if (
        settings.pointer == "cross"
        and settings.show_pointer
        and settings.show_octa_slot
        and settings.show_third_slot
    ):
        return "weekday"
    return settings.weekday_slot


def _classic_slot_theme(settings: Settings) -> tuple[str, str | None]:
    """The (theme, metal) DRESSING the classic weekday unit: normally
    the 1st slot's — except the Seasons/Compass two-slot case where
    only the 2ND is weekday, so the 2nd rides the rotation in its own
    theme (owner 2026-07-15)."""
    if (
        settings.pointer in ("cross", "octa")
        and settings.show_pointer
        and settings.show_weekday
        and settings.show_octa_slot
        and not settings.show_third_slot
        and _effective_weekday_slot(settings) != "weekday"
        and settings.octa_slot == "weekday"
    ):
        theme = settings.info_slot_theme
        return theme, _theme_metal(settings, theme)
    theme = settings.weekday_theme
    return theme, _theme_metal(settings, theme)


def _themed_weekday_set(base, theme: str, metal: str | None):
    """The weekday unit dressed in `theme` wearing `metal` — the
    SYMBOLISM canon swap (entity-named files, canon display names;
    "planets" keeps the pack's own unit), the hue-SELECTIVE metal at
    render, and the Sunday Servant dual (the COLORED look swaps in
    the sibling variant; owner restructure 2026-07-14)."""
    weekday = base
    if theme != "planets":
        theme_dir = (
            defaults.WEEKDAY_ART_DIR / defaults.WEEKDAY_THEME_DIRS[theme]
        )
        if metal == "colored":
            theme_dir = theme_dir.parent / "colored"
        names = defaults.WEEKDAY_THEME_NAMES[theme]
        files = defaults.WEEKDAY_THEME_FILES[theme]
        weekday = dataclasses.replace(
            weekday,
            bodies={body: theme_dir / f"{files[body]}.png" for body in names},
            body_names=dict(names),
        )
    if metal in defaults.METAL_SWAP_TARGETS:
        weekday = dataclasses.replace(weekday, metal=metal)
    dual_rel = defaults.WEEKDAY_DUAL_FILES[theme]
    if metal == "colored" and theme in constants.METAL_THEMES:
        dual_rel = dual_rel.replace("/primary/", "/colored/")
    return dataclasses.replace(
        weekday, dual_asset=defaults.WEEKDAY_ART_DIR / f"{dual_rel}.png"
    )


def apply_display_settings(skin, settings: Settings):
    """The user's choices win over whatever the skin pack declares:
    the tray display scalars, the opacity overrides (twilight alphas
    scale proportionally with the day alphas) and the custom palette
    for the active (pointer, style). Module-level — testable without
    a controller."""
    # The ART SOURCE switch (owner 2026-07-14: Gemini vs ChatGPT) —
    # every disk boundary resolves canonical paths through it.
    paths.set_art_source(settings.art_source)
    star = skin.star
    if settings.star_alpha is not None:
        star = dataclasses.replace(
            star,
            day_alpha=settings.star_alpha,
            twilight_alpha=settings.star_alpha
            * (star.twilight_alpha / star.day_alpha),
        )
    weekday = skin.weekday_set
    if settings.slot_scale != 1.0:
        # ONE slot size (owner 2026-07-14): the multiplier scales the
        # spec values directly — bodies, subdials, hit regions alike.
        weekday = dataclasses.replace(
            weekday,
            diamond_scale=weekday.diamond_scale * settings.slot_scale,
            center_scale=weekday.center_scale * settings.slot_scale,
        )
    # The CLASSIC unit wears the theme of the slot that DRIVES it
    # (owner 2026-07-15): on the Seasons/Compass with two slots where
    # only the 2nd is weekday, that slot rides the rotation in ITS
    # OWN theme.
    theme, metal = _classic_slot_theme(settings)
    weekday = _themed_weekday_set(weekday, theme, metal)
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
    marker = skin.year_marker
    if settings.earth_scale != 1.0 or settings.moon_scale != 1.0:
        marker = dataclasses.replace(
            marker,
            scale=marker.scale * settings.earth_scale,
            moon_scale=marker.moon_scale * settings.moon_scale,
        )
    marker = dataclasses.replace(
        marker,
        moon_hidden_alpha=settings.moon_hidden_alpha,
        # The Earth marker wears the ACTIVE location's continent art
        # (owner bug 2026-07-12: it was pinned to Europe).
        default_variant=_earth_continent(settings),
    )
    return dataclasses.replace(
        skin,
        star=star,
        background=background,
        weekday_set=weekday,
        year_marker=marker,
        pointer=settings.pointer,
        umbra_form=settings.umbra_form,
        umbra_contrast=settings.umbra_contrast,
        palette_style=settings.palette_style,
        # Aurora is ALWAYS solar-rotated (owner spec 2026-07-12): its
        # bands anchor to the real sun events, so the whole wheel keeps
        # the solar frame regardless of the toggle.
        solar_rotation=(
            True if settings.pointer == "aurora" else settings.solar_rotation
        ),
        octa_slot=settings.octa_slot,
        day_slot_style=settings.day_slot_style,
        info_slot_style=settings.info_slot_style,
        info_slot_theme=settings.info_slot_theme,
        info_slot_metal=_theme_metal(settings, settings.info_slot_theme),
        weekday_slot=_effective_weekday_slot(settings),
        third_slot=settings.third_slot,
        third_slot_style=settings.third_slot_style,
        third_slot_theme=settings.third_slot_theme,
        third_slot_metal=_theme_metal(settings, settings.third_slot_theme),
        # The slots enable IN ORDER (owner 2026-07-14): the third
        # exists only on top of the second.
        show_third_slot=settings.show_third_slot and settings.show_octa_slot,
        earth_style=settings.earth_style,
        weekday_theme=settings.weekday_theme,
        legend=settings.legend,
        show_earth=settings.show_earth,
        show_moon=settings.show_moon,
        show_weekday=settings.show_weekday,
        show_pointer=settings.show_pointer,
        colorful=settings.colorful,
        # The big seconds hand YIELDS while a slot runs the
        # small-seconds complication (owner 2026-07-14).
        show_seconds=settings.show_seconds and not _slot_seconds(settings),
        show_octa_slot=settings.show_octa_slot,
        show_earth_date=settings.show_earth_date,
        show_weekday_names=settings.show_weekday_names,
        show_info_slot_names=settings.show_info_slot_names,
        ring_tint=settings.ring_tint,
        ring_finish=settings.ring_finish,
        ring_letter_scale=settings.ring_letter_scale,
        hover_enlarge=settings.hover_enlarge,
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
        self._menu = self._build_menu()
        self._legend = LegendPopup()
        self._widget = ClockWidget(self._settings.diameter, self._menu, self._legend)
        try:
            icon = logo_icon()
            self._tray = TrayController(self._menu, icon)
            # Every dialog title bar (Settings, Time Travel, Guide)
            # inherits this instead of the generic Windows icon (owner
            # report 2026-07-11); the built EXE gets the M7 ICO on top.
            self._app.setWindowIcon(icon)
        except ValueError as error:
            # A broken/missing logo must be SEEN (review finding) — in a
            # windowed build a bare traceback dies with no window at all.
            self._critical_box(
                f"The tray icon could not be loaded:\n{error}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
            raise SystemExit(1) from error

        self._tz = ZoneInfo(self._settings.timezone)
        self._observer = astral.Observer(
            latitude=self._settings.latitude, longitude=self._settings.longitude
        )
        self._seasons = SeasonsRepository()
        self._moon_phases = MoonPhaseRepository()
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
        if self._settings.language != "en":
            self._apply_language(start_missing=True)
        self._compositor = Compositor(
            self._skin, AssetCache(), self._symbolism(),
            overlay=self._translation_overlay,
        )
        # SESSION-only (owner 2026-07-15): every launch starts locked —
        # the code must be typed again.
        self._hidden_unlocked = False
        self._day = None
        # Time Travel: a frozen (moment, observer) rendered instead of the
        # present until the deadline passes.
        self._simulation: tuple[datetime, astral.Observer] | None = None
        self._simulation_ends: float = 0.0
        self._widget.set_renderer(self._compositor)
        seconds_hand = (
            self._skin.hands.second is not None
            and self._settings.show_seconds
        ) or _slot_seconds(self._settings)
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
        # The hidden-mode code listener (owner 2026-07-14): printable
        # keys typed on the focused dial roll through a buffer.
        self._secret_buffer = ""
        self._widget.typed.connect(self._collect_secret)

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
        self._last_dpr = self._widget.devicePixelRatioF()
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
        hidden extras — for now the Four Greetings on the ring letters
        and in the Encyclopedia's Trinity topic. The unlock lives for
        THIS SESSION only (owner 2026-07-15: every launch asks for the
        code again — nothing persists)."""
        if self._hidden_unlocked:
            return
        secret = constants.HIDDEN_MODE_SECRET
        self._secret_buffer = (self._secret_buffer + char)[-len(secret):]
        if self._secret_buffer != secret:
            return
        self._secret_buffer = ""
        self._hidden_unlocked = True
        self._compositor.set_hidden_unlocked(True)
        self._tray.notify(
            self._ui("Hidden mode unlocked"),
            self._ui("The Four Greetings await in the Encyclopedia — Trinity."),
            critical=False,
        )

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
        the user's machine translates once and caches)."""
        return SymbolismRepository(overlay=self._translation_overlay or None)

    def _install_skin(self, skin) -> None:
        """Swap the rendered skin: fresh compositor, current day kept."""
        self._skin = skin
        self._compositor = Compositor(
            skin, AssetCache(), self._symbolism(),
            overlay=self._translation_overlay,
        )
        self._compositor.set_hidden_unlocked(self._hidden_unlocked)
        self._widget.set_renderer(self._compositor)
        if self._day is not None:
            self._compositor.set_day(self._day)
        # The Seconds element switch also changes the tick cadence —
        # and so does the small-seconds slot (owner 2026-07-14).
        self._scheduler.set_per_second(
            (skin.hands.second is not None and self._settings.show_seconds)
            or _slot_seconds(self._settings)
        )
        self._widget.update()

    def _set_ring(self, ring: str) -> None:
        if ring == self._settings.ring:
            return
        self._settings = replace(self._settings, ring=ring)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_hands(self, hands: str) -> None:
        if hands == self._settings.hands:
            return
        self._settings = replace(self._settings, hands=hands)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_weekday_badge(self, mode: str, style: str) -> None:
        """Day slot content + its OWN style in one click (owner
        2026-07-12: the slots are independent — this never touches the
        info slot's look)."""
        self._settings = replace(
            self._settings, weekday_slot=mode, day_slot_style=style
        )
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _metal_updates(self, theme: str, metal: str | None) -> dict:
        """The settings delta of an EXPLICIT metal pick (either slot's
        Weekday submenu): remembers the theme's metal and releases
        follow-the-ring, otherwise the ring finish would silently
        override it. Empty when no metal was chosen."""
        if metal is None:
            return {}
        metals = dict(self._settings.theme_metals)
        metals[theme] = metal
        return {"theme_metals": metals, "theme_metal_follow_ring": False}

    def _set_south_slot(
        self, mode: str, style: str | None = None,
        theme: str | None = None, metal: str | None = None,
    ) -> None:
        """Info slot content + its OWN style/theme/metal in one click
        (owner 2026-07-12: independent of the day slot's look)."""
        updates: dict = {"octa_slot": mode}
        if style is not None:
            updates["info_slot_style"] = style
        if theme is not None:
            updates["info_slot_theme"] = theme
            updates.update(self._metal_updates(theme, metal))
        self._settings = replace(self._settings, **updates)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_third_slot(
        self, mode: str, style: str | None = None,
        theme: str | None = None, metal: str | None = None,
    ) -> None:
        """The 3rd slot's content (owner 2026-07-14) — the same shape
        as the other two, its own style/theme/metal."""
        updates: dict = {"third_slot": mode}
        if style is not None:
            updates["third_slot_style"] = style
        if theme is not None:
            updates["third_slot_theme"] = theme
            updates.update(self._metal_updates(theme, metal))
        self._settings = replace(self._settings, **updates)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_weekday_theme(self, theme: str, metal: str | None = None) -> None:
        """Day slot back to the WEEKDAY BODIES wearing `theme` (owner
        menu 2026-07-12: the theme list lives inside Day slot ▸ Weekday,
        so picking a theme also picks the mode; bronze-plate themes
        pick their metal in the same click)."""
        self._settings = replace(
            self._settings,
            weekday_slot="weekday",
            weekday_theme=theme,
            **self._metal_updates(theme, metal),
        )
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _configure_theme_rotation(self) -> None:
        """Start/stop the rotation timer per the settings (called at
        startup and after every Settings OK). The GROUP dropdown picks
        what cycles (owner 2026-07-14: a kinship family, the custom
        checkbox list, or none at all); the ORDER is shuffled fresh
        each time (owner spec 2026-07-12: never the same sequence
        twice)."""
        self._rotation_order = list(rotation_themes(self._settings))
        random.shuffle(self._rotation_order)
        if len(self._rotation_order) >= 2:
            self._theme_rotation_timer.start(
                self._settings.theme_rotation_minutes * 60 * 1000
            )
        else:
            self._theme_rotation_timer.stop()

    def _rotate_theme(self) -> None:
        """One rotation step: the next theme of the SHUFFLED order goes
        live (and the menu checkmarks follow)."""
        self._set_display_choice(
            "weekday_theme",
            _next_rotation_theme(
                self._settings.weekday_theme,
                tuple(self._rotation_order),
            ),
        )
        # The timer can fire while the user is browsing the menu —
        # close and RETAIN the replaced one so Qt never deletes a
        # visible popup (stay-open menus, owner 2026-07-13).
        retired = self._menu
        self._menu = self._build_menu()
        self._widget.set_menu(self._menu)
        self._tray.set_menu(self._menu)
        retired.close()
        self._retired_menu = retired

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
        if key in ("pointer", "show_weekday", "show_pointer"):
            # These move the whole enablement matrix (the South slot's
            # availability, the weekday-badge availability, Aurora's
            # image-only modes, the Solar rotation lock) — re-gray the
            # gated entries IN PLACE (owner 2026-07-13: switching the
            # pointer or an element must not close the open menu).
            self._refresh_menu_gating()

    def _refresh_menu_gating(self) -> None:
        """Recompute every gated menu entry from the CURRENT settings
        without rebuilding (the stay-open menu keeps its window; only
        the gray states move). The slot matrix (owner 2026-07-14)
        seats every mode under every pointer — what remains gated:
        the Seasons' three-slot 1st-slot lock, the 1 → 2 → 3 enable
        order, and the big seconds hand while a slot runs the
        small-seconds complication."""
        settings = self._settings
        locked = (
            settings.pointer == "cross"
            and settings.show_pointer
            and settings.show_octa_slot
            and settings.show_third_slot
        )
        for item in self._menu_gates["first_lock"]:
            item.setEnabled(not locked)
        self._menu_gates["enable2"].setEnabled(settings.show_weekday)
        self._menu_gates["enable3"].setEnabled(
            settings.show_weekday and settings.show_octa_slot
        )
        self._menu_gates["seconds"].setEnabled(
            not _slot_seconds(settings)
        )
        self._solar_rotation_action.setEnabled(
            settings.pointer != "aurora"
        )

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

    def _submenu(self, parent: QMenu, title: str) -> QMenu:
        """One stay-open submenu attached to `parent` (owner menu
        rework 2026-07-13: every level keeps checkable picks open)."""
        submenu = _StayOpenMenu(title, parent)
        parent.addMenu(submenu)
        return submenu

    def _add_choice_submenu(self, menu: QMenu, title: str, options, current, setter) -> QMenu:
        """One exclusive check-group submenu: options are (value, label)."""
        submenu = self._submenu(menu, title)
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

    def _ui(self, text: str) -> str:
        """The active language's form of a chrome string (Phase 2)."""
        return ui(self._translation_overlay, text)

    def _build_menu(self) -> QMenu:
        menu = _StayOpenMenu()
        settings = self._settings
        tr = self._ui
        # Menu rework (owner 2026-07-13): emoji-fronted top level —
        # Design / Primary Slot / Secondary Slot / Elements, then the
        # three switches, the four windows, Exit — and checkable picks
        # keep the menu OPEN. DESIGN = how the instrument looks
        # (Pointer, Ring, Umbra | Hands, Earth | Size).
        design_menu = self._submenu(menu, f"🎨 {tr('Design')}")
        # Pointer variant and palette style share ONE dropdown (owner
        # spec), two exclusive groups like the Umbra submenu.
        pointer_menu = self._add_choice_submenu(
            design_menu, tr("Pointer"),
            [
                # Owner-chosen display names (FINAL.txt #8): Trinity,
                # Seasons, Prism, Compass — protected brand terms, the
                # same in every language. Aurora has no arms — no count
                # after its name, and it sits LAST, below the Compass
                # (owner spec 2026-07-12).
                (
                    variant,
                    constants.POINTER_DISPLAY_NAMES[variant]
                    if variant == "aurora"
                    else f"{constants.POINTER_DISPLAY_NAMES[variant]} ({arms})",
                )
                for variant, arms in sorted(
                    constants.POINTER_POINTS.items(),
                    key=lambda item: (item[0] == "aurora", item[1]),
                )
            ],
            settings.pointer,
            lambda value: self._set_display_choice("pointer", value),
        )
        pointer_menu.addSeparator()
        self._add_choice_group(
            design_menu, pointer_menu,
            [
                (style, tr(f"{style.capitalize()} palette"))
                for style in constants.PALETTE_STYLES
            ],
            settings.palette_style,
            lambda value: self._set_display_choice("palette_style", value),
        )
        ring_menu = self._add_choice_submenu(
            design_menu, tr("Ring"),
            [
                (name, name)
                for name in sorted(ring_presets(settings.custom_rings))
            ],
            settings.ring, self._set_ring,
        )
        ring_menu.addSeparator()
        # The letter FINISH (owner rules): gold = the triangle letters
        # gold + the remaining one silver; silver = the exact inverse;
        # the Seal wears one metal. The tint itself lives in Settings.
        self._add_choice_group(
            design_menu, ring_menu,
            [(finish, tr(f"{finish.capitalize()} letters"))
             for finish in constants.RING_FINISHES],
            settings.ring_finish,
            lambda value: self._set_display_choice("ring_finish", value),
        )
        umbra_menu = self._add_choice_submenu(
            design_menu, tr("Umbra"),
            [
                ("fine", tr("Fine (16 shades)")),
                ("coarse", tr("Coarse (13 shades)")),
                ("gradient", tr("Gradient")),
            ],
            settings.umbra_form,
            lambda value: self._set_display_choice("umbra_form", value),
        )
        umbra_menu.addSeparator()
        self._add_choice_group(
            design_menu, umbra_menu,
            [
                (variant, tr(f"{variant.capitalize()} contrast"))
                for variant in constants.UMBRA_CONTRAST_VARIANTS
            ],
            settings.umbra_contrast,
            lambda value: self._set_display_choice("umbra_contrast", value),
        )
        design_menu.addSeparator()
        # The HAND PACKS (owner spec 2026-07-12): bundled CLASSIC and
        # STEEL plus whatever the user added via Settings.
        self._add_choice_submenu(
            design_menu, tr("Hands"),
            [(name, name) for name in sorted(hand_packs())],
            settings.hands, self._set_hands,
        )
        # EARTH lives inside Design now (owner menu rework 2026-07-13).
        earth_menu = self._add_choice_submenu(
            design_menu, tr("Earth"),
            [("clean", tr("Clean")), ("atmo", tr("Atmosphere"))],
            settings.earth_style,
            lambda value: self._set_display_choice("earth_style", value),
        )
        earth_menu.addSeparator()
        # The date label ON the Earth marker (owner spec): its own
        # switch, grayed out below the size that can draw it at all.
        self._earth_date_toggle = self._add_toggle(
            earth_menu, tr("Date"), settings.show_earth_date,
            lambda checked: self._set_display_choice("show_earth_date", checked),
            tr(
                "The date written on the Earth marker (shown from "
                "{size} px up)."
            ).format(size=defaults.FULL_TEXT_MIN_DIAMETER),
        )
        self._earth_date_toggle.setEnabled(
            settings.diameter >= defaults.FULL_TEXT_MIN_DIAMETER
        )
        design_menu.addSeparator()
        self._add_choice_submenu(
            design_menu, tr("Size"),
            [(preset, f"{preset} px") for preset in defaults.SIZE_PRESETS],
            settings.diameter, self._set_diameter,
        )
        # The THREE SLOTS at the TOP level (owner 2026-07-14: the
        # 1st/2nd/3rd Slot system, superscripts in the labels). Every
        # slot has the same shape — the Weekday themes, the
        # COMPLICATIONS dropdown (Digital Time / Date / Day length /
        # Seconds), the astrology families — and its own ENABLE below
        # the separator; they enable strictly 1 → 2 → 3.
        day_slot_menu = self._submenu(menu, f"🥇 {tr('1ˢᵗ Slot')}")
        info_slot_menu = self._submenu(menu, f"🥈 {tr('2ⁿᵈ Slot')}")
        third_slot_menu = self._submenu(menu, f"🥉 {tr('3ʳᵈ Slot')}")

        # Gating buckets (owner 2026-07-13: pointer/element switches
        # must NOT close the menu — no rebuild; _refresh_menu_gating
        # re-grays these lists in place).
        self._menu_gates = {
            "first_lock": [],
        }

        def slot_action(
            parent: QMenu, group: QActionGroup, label: str,
            checked: bool, handler, enabled: bool = True,
        ) -> QAction:
            action = QAction(label, menu)
            action.setCheckable(True)
            action.setChecked(checked)
            action.setEnabled(enabled)
            action.triggered.connect(handler)
            group.addAction(action)
            parent.addAction(action)
            return action

        def add_weekday_submenu(
            parent: QMenu, group: QActionGroup,
            active: bool, current_theme: str, on_theme, names_key: str,
        ) -> None:
            """The IDENTICAL Weekday submenu of both slots, in KINSHIP
            GROUPS (owner menu rework 2026-07-13: Ancient Gods /
            Society / Animals / Arcana): the bronze-plate themes open
            their metal dropdown in place, Planets nests its Image and
            Sign looks — plus the slot's OWN Names switch. Picking a
            theme also picks the slot's weekday mode."""
            sub = self._submenu(parent, tr("Weekday"))
            for group_title, keys in defaults.WEEKDAY_MENU_GROUPS:
                group_menu = self._submenu(sub, tr(group_title))
                for key in keys:
                    title = defaults.WEEKDAY_THEME_TITLES[key]
                    if key == "planets":
                        # Image/Sign/Art as three options of ONE entry
                        # (owner: planet_signs and planets_art stay
                        # themes underneath, nested).
                        planet_menu = self._submenu(group_menu, tr(title))
                        for pkey, plabel in (
                            ("planets", tr("Image")),
                            ("planet_signs", tr("Sign")),
                            ("planets_art", tr("Art")),
                        ):
                            slot_action(
                                planet_menu, group, plabel,
                                active and current_theme == pkey,
                                lambda checked, t=pkey: on_theme(t),
                            )
                    elif key in constants.METAL_THEMES:
                        metal_menu = self._submenu(group_menu, tr(title))
                        for metal in constants.THEME_METALS:
                            slot_action(
                                metal_menu, group, tr(metal.capitalize()),
                                active and current_theme == key
                                and _theme_metal(settings, key) == metal,
                                lambda checked, t=key, m=metal: on_theme(t, m),
                            )
                    else:
                        slot_action(
                            group_menu, group, tr(title),
                            active and current_theme == key,
                            lambda checked, t=key: on_theme(t),
                        )
            sub.addSeparator()
            self._add_toggle(
                sub, tr("Names"), getattr(settings, names_key),
                lambda checked, key=names_key: self._set_display_choice(
                    key, checked
                ),
                tr("The day name written on the weekday bodies."),
            )

        zodiac_styles = (
            ("sign", tr("Sign")),
            ("logo", tr("Logo")),
            ("constellation", tr("Constellation")),
            ("colored", tr("Colored")),
        )

        def build_slot_menu(
            slot_menu, index: int, mode_value: str, style_value: str,
            theme_value: str, names_key: str, enabled_value: bool,
            enable_key: str, set_mode, set_style_mode, set_theme,
        ):
            """One slot submenu (owner 2026-07-14: all three share the
            shape): Weekday themes, the COMPLICATIONS dropdown, the
            astrology families — and the slot's own ENABLE below the
            separator. Returns (enable action, the 1st-slot lockable
            entries)."""
            group = QActionGroup(menu)
            group.setExclusive(True)
            lockable = []
            add_weekday_submenu(
                slot_menu, group,
                mode_value == "weekday", theme_value, set_theme, names_key,
            )
            comps = self._submenu(slot_menu, tr("Complications"))
            lockable.append(comps.menuAction())
            for mode, label in (
                ("time", tr("Digital Time")),
                ("date", tr("Date")),
                ("day_length", tr("Day length")),
                ("seconds", tr("Seconds")),
            ):
                slot_action(
                    comps, group, label, mode_value == mode,
                    lambda checked, chosen=mode: set_mode(chosen),
                )
            for family, family_title in (
                ("zodiac", tr("Astrology")),
                # The ASCENDANT (owner request 2026-07-12): the sign
                # rising on the eastern horizon right now.
                ("ascendant", tr("Ascendant")),
            ):
                family_menu = self._submenu(slot_menu, family_title)
                lockable.append(family_menu.menuAction())
                for style, label in (
                    *zodiac_styles,
                    ("text", tr("Text")),
                ):
                    slot_action(
                        family_menu, group, label,
                        mode_value == family and style_value == style,
                        lambda checked, m=family, s=style:
                        set_style_mode(m, s),
                    )
            chinese_menu = self._submenu(slot_menu, tr("Chinese zodiac"))
            lockable.append(chinese_menu.menuAction())
            for style, label in (
                ("colored", tr("Colored")),
                ("gold", tr("Gold")),
                ("silver", tr("Silver")),
                ("bronze", tr("Bronze")),
                ("text", tr("Text")),
            ):
                slot_action(
                    chinese_menu, group, label,
                    mode_value == "chinese" and style_value == style,
                    lambda checked, s=style: set_style_mode("chinese", s),
                )
            slot_menu.addSeparator()
            enable = self._add_toggle(
                slot_menu, tr("Enable"), enabled_value,
                lambda checked, key=enable_key: self._set_display_choice(
                    key, checked
                ),
                tr("The slots enable in order — 1st, then 2nd, then 3rd."),
            )
            return enable, lockable

        _, first_lockable = build_slot_menu(
            day_slot_menu, 1,
            settings.weekday_slot, settings.day_slot_style,
            settings.weekday_theme, "show_weekday_names",
            settings.show_weekday, "show_weekday",
            lambda mode: self._set_display_choice("weekday_slot", mode),
            self._set_weekday_badge,
            self._set_weekday_theme,
        )
        # The Seasons with all three slots LOCK the 1st on the weekday
        # unit (owner 2026-07-14) — everything but Weekday grays.
        self._menu_gates["first_lock"] = first_lockable
        enable2, _ = build_slot_menu(
            info_slot_menu, 2,
            settings.octa_slot, settings.info_slot_style,
            settings.info_slot_theme, "show_info_slot_names",
            settings.show_octa_slot, "show_octa_slot",
            self._set_south_slot,
            lambda mode, style: self._set_south_slot(mode, style=style),
            lambda theme, metal=None: self._set_south_slot(
                "weekday", theme=theme, metal=metal
            ),
        )
        enable3, _ = build_slot_menu(
            third_slot_menu, 3,
            settings.third_slot, settings.third_slot_style,
            settings.third_slot_theme, "show_info_slot_names",
            settings.show_third_slot, "show_third_slot",
            self._set_third_slot,
            lambda mode, style: self._set_third_slot(mode, style=style),
            lambda theme, metal=None: self._set_third_slot(
                "weekday", theme=theme, metal=metal
            ),
        )
        self._menu_gates["enable2"] = enable2
        self._menu_gates["enable3"] = enable3
        enable2.setEnabled(settings.show_weekday)
        enable3.setEnabled(settings.show_weekday and settings.show_octa_slot)
        # Elements (owner spec): plain on/off switches — the slots
        # enable INSIDE their own submenus now (owner 2026-07-14), so
        # only the star, its colors, the two markers and the seconds
        # hand remain.
        elements_menu = self._submenu(menu, f"🧩 {tr('Elements')}")
        for key, label, tip in (
            (
                "show_pointer", tr("Pointer"),
                tr("The star diamonds. Off: the Aura colors stay, only the "
                   "pointer disappears."),
            ),
            (
                "colorful", tr("Colorful"),
                tr("The Aura palette hues. Off: the day and twilight arcs "
                   "are drawn as plain white transparency."),
            ),
            (
                "show_earth", tr("Earth"),
                tr("The Earth marker riding the year wheel and showing "
                   "the date."),
            ),
            (
                "show_moon", tr("Moon"),
                tr("The Moon marker riding its cycle and showing the phase."),
            ),
            (
                "show_seconds", tr("Seconds"),
                tr("The seconds hand. Off: it is not drawn and the dial "
                   "ticks once per minute."),
            ),
        ):
            action = self._add_toggle(
                elements_menu, label, getattr(settings, key),
                lambda checked, key=key: self._set_display_choice(key, checked),
                tip,
            )
            if key == "show_seconds":
                # The big hand yields while a slot runs the
                # small-seconds complication (owner 2026-07-14).
                self._menu_gates["seconds"] = action
                action.setEnabled(not _slot_seconds(settings))
        menu.addSeparator()
        self._add_toggle(
            menu, f"📜 {tr('Legend')}", settings.legend,
            lambda checked: self._set_display_choice("legend", checked),
            tr("All hover texts. Off: the dial shows nothing on hover — "
               "combined with Click-through it has zero interaction."),
        )
        self._solar_rotation_action = self._add_toggle(
            menu, f"🔆 {tr('Solar rotation')}", settings.solar_rotation,
            lambda checked: self._set_display_choice("solar_rotation", checked),
            tr("On: the star points at true solar noon. Off: Star, Aura and "
               "Umbra stand upright (12/24 at the top) for reading exact "
               "planet and season positions."),
        )
        # Aurora is ALWAYS solar-rotated (owner spec 2026-07-12) — the
        # bands anchor to the real sun events, the toggle has no say.
        self._solar_rotation_action.setEnabled(settings.pointer != "aurora")
        self._add_toggle(
            menu, f"🖱️ {tr('Click-through')}", self._settings.click_through,
            self._set_click_through,
            tr("The dial takes no clicks at all (they pass to the desktop); "
               "hover info still works. Turn it back off here in the tray."),
        )
        menu.addSeparator()
        settings_action = QAction(f"⚙️ {tr('Settings…')}", menu)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)
        encyclopedia = QAction(f"🏛️ {tr('Encyclopedia…')}", menu)
        encyclopedia.triggered.connect(
            lambda: EncyclopediaDialog(
                self._translation_overlay,
                hidden_unlocked=self._hidden_unlocked,
            ).exec()
        )
        menu.addAction(encyclopedia)
        guide = QAction(f"📖 {tr('Guide…')}", menu)
        guide.triggered.connect(
            lambda: GuideDialog(self._translation_overlay).exec()
        )
        menu.addAction(guide)
        time_travel = QAction(f"🕰️ {tr('Time Travel…')}", menu)
        time_travel.triggered.connect(self._open_time_travel)
        menu.addAction(time_travel)
        # QUICK JUMP (owner 2026-07-14): one-click Time Travel presets
        # right below the dialog entry — same minute-then-back rules.
        jumps = self._submenu(menu, f"⚡ {tr('Quick Jump')}")
        # Short arrow labels (owner 2026-07-14: "Next Sun Turning
        # Point" was a mouthful) — → walks forward, ← backward, and
        # repeated clicks CHAIN through the years.
        for kind, label in (
            ("next_sun", f"☀️ {tr('Sun')} →"),
            ("prev_sun", f"☀️ {tr('Sun')} ←"),
            ("next_moon", f"🌙 {tr('Moon')} →"),
            ("prev_moon", f"🌙 {tr('Moon')} ←"),
            (None, None),
            ("north_pole", tr("North Pole")),
            ("south_pole", tr("South Pole")),
            (None, None),
            ("greenwich", tr("Greenwich")),
        ):
            if kind is None:
                jumps.addSeparator()
                continue
            action = QAction(label, jumps)
            action.triggered.connect(
                lambda checked=False, kind=kind: self._quick_jump(kind)
            )
            jumps.addAction(action)
        menu.addSeparator()
        exit_action = QAction(f"🚪 {tr('Exit')}", menu)
        exit_action.triggered.connect(self.quit)
        menu.addAction(exit_action)
        return menu

    def _open_settings(self) -> None:
        dialog = SettingsDialog(
            self._settings, self._skin, self._translation_overlay
        )
        if dialog.exec() != SettingsDialog.DialogCode.Accepted:
            return
        new_settings = dialog.result_settings()
        location_changed = (
            new_settings.latitude,
            new_settings.longitude,
            new_settings.timezone,
        ) != (self._settings.latitude, self._settings.longitude, self._settings.timezone)
        language_changed = new_settings.language != self._settings.language
        self._settings = new_settings
        if language_changed:
            self._apply_language(start_missing=True)
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
        # The menu mirrors the settings (checkmarks, custom rings in
        # Theme > Ring) — rebuild it wholesale after every dialog OK.
        self._menu = self._build_menu()
        self._widget.set_menu(self._menu)
        self._tray.set_menu(self._menu)
        self._configure_theme_rotation()
        native.set_autostart(dialog.autostart_selected())
        self._flush_position()

    def _open_time_travel(self) -> None:
        # A running simulation SEEDS the dialog (owner 2026-07-14):
        # after a quick jump the offered coordinates and moment are
        # the simulated ones, not the home city's.
        if self._simulation is not None:
            sim_moment, sim_observer = self._simulation
            initial = sim_moment.astimezone(self._tz).replace(tzinfo=None)
            latitude = sim_observer.latitude
            longitude = sim_observer.longitude
        else:
            initial = None
            latitude = self._settings.latitude
            longitude = self._settings.longitude
        dialog = TimeTravelDialog(
            latitude, longitude,
            overlay=self._translation_overlay,
            initial_moment=initial,
        )
        if dialog.exec() != TimeTravelDialog.DialogCode.Accepted:
            return
        moment = dialog.moment().replace(second=0, microsecond=0, tzinfo=self._tz)
        observer = astral.Observer(
            latitude=dialog.latitude(), longitude=dialog.longitude()
        )
        self._start_simulation(moment, observer)

    def _start_simulation(self, moment: datetime, observer) -> None:
        """Render the (moment, observer) situation for the standard
        Time Travel minute, then return to the present — any new
        travel restarts the minute (owner 2026-07-14)."""
        self._simulation = (moment, observer)
        self._simulation_ends = monotonic() + defaults.TIME_TRAVEL_DURATION_S
        self._day = None                    # rebuild with the simulated situation
        self._on_tick(clock_jumped=False)

    def _quick_jump(self, kind: str) -> None:
        """One-click Time Travel presets (owner rounds 2026-07-14).
        The jumps CHAIN: while a simulation runs, the next jump starts
        from the SIMULATED situation — a time jump keeps the simulated
        PLACE, a place jump keeps the simulated MOMENT — so repeated
        "→ Sun" walks the turning points year after year, and a pole
        or Greenwich pick stays under you while you travel. The three
        places are REAL coordinates with their REAL clocks: Greenwich
        at the observatory in its own timezone (BST in summer — the
        sun honestly culminates near 13:00 then), the poles on UTC.
        Every jump restarts the standard minute-then-back."""
        if self._simulation is not None:
            base_moment, base_observer = self._simulation
        else:
            base_moment = datetime.now(self._tz)
            base_observer = self._observer
        moment, observer = base_moment, base_observer
        if kind in ("next_sun", "prev_sun", "next_moon", "prev_moon"):
            if kind.endswith("sun"):
                instants = sorted({
                    instant
                    for year in (base_moment.year - 1, base_moment.year,
                                 base_moment.year + 1)
                    for instant in self._seasons.year_anchors(year).instants
                })
            else:
                instants = [
                    when for when, _ in
                    self._moon_phases.moon_window(base_moment.year).events
                ]
            # The simulated moment is floored to the minute, so the
            # landed-on instant lies seconds AHEAD of it — the strict
            # one-minute guard keeps "next" from re-picking it.
            if kind.startswith("next"):
                moment = min(
                    w for w in instants
                    if w > base_moment + timedelta(minutes=1)
                )
            else:
                moment = max(w for w in instants if w < base_moment)
            moment = moment.astimezone(base_moment.tzinfo)
        elif kind in ("north_pole", "south_pole"):
            sign = 1 if kind == "north_pole" else -1
            observer = astral.Observer(
                latitude=sign * defaults.QUICK_JUMP_POLE_LATITUDE,
                longitude=0.0,
            )
            moment = base_moment.astimezone(timezone.utc)
        else:                               # greenwich — the REAL place
            observer = astral.Observer(
                latitude=defaults.GREENWICH_LATITUDE,
                longitude=defaults.GREENWICH_LONGITUDE,
            )
            moment = base_moment.astimezone(
                ZoneInfo(defaults.GREENWICH_TIMEZONE)
            )
        self._start_simulation(
            moment.replace(second=0, microsecond=0), observer
        )

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
        if store.missing(language, collect_corpus()):
            self._translation_thread = threading.Thread(
                target=self._translate_worker, args=(language,), daemon=True
            )
            self._translation_thread.start()
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
            self._install_skin(build_skin(self._settings))
            self._menu = self._build_menu()
            self._widget.set_menu(self._menu)
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
        # The Earth date switch only applies where the label can draw.
        self._earth_date_toggle.setEnabled(
            diameter >= defaults.FULL_TEXT_MIN_DIAMETER
        )
        self._widget.set_dial_diameter(diameter)
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
