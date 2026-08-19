"""The watch's own windows: opens them, re-raises a live one,
forgets a closed one, and builds the payload each is handed.

A mixin of [WatchController](controller.md). The controller holds the
`self._watch_face` / `self._encyclopedia` / `self._observatory` handles;
this module is the only place that assigns them, so "one window at a
time, raised not duplicated" has a single implementation
(`_reopen_live`).
"""

import functools
from datetime import datetime
from zoneinfo import ZoneInfo

import astral

from app import native
from app.watch_face.window import WatchFaceDialog
from app.encyclopedia import EncyclopediaDialog
from app.observatory import ObservatoryDialog
from app.report import ReportDialog
from app.shortcuts_window import ShortcutsDialog
from app.settings_dialog.dialog import SettingsDialog
from app.skin_builder import build_skin
from app.settings_store import replace
from app.slot_descriptor import SlotDescriptor
from config import palette, paths, umbra
from config import watch_face as watch_face_keys
from config.registry.slots import SLOT_KEYS


def _display_choice(set_display_choice, key: str):
    """The ONE setter shape behind every plain Watch Face control:
    store `key` and rebuild the skin.

    A real function of arity ONE, exactly like the fifty-six lambdas it
    replaces — `app.watch_face.section_reset` reads that arity through
    `functools.wraps`'s `__wrapped__` to tell a one-value setting apart
    from a target-plus-value one, so the shape is load-bearing and not
    an implementation detail."""
    def apply(value):
        set_display_choice(key, value)
    return apply


class _DialogHostsMixin:
    """DialogHostsMixin — see the module docstring."""

    def _open_report(self) -> None:
        # The hidden debug Report stays MODAL — an admin/statistics
        # snapshot the owner never asked to leave open alongside the
        # dial (item 1's non-modal trio is Encyclopedia/Guide/
        # Observatory only).
        ReportDialog(self._translation_overlay).exec()

    def _open_shortcuts(self) -> None:
        """⌨️ Shortcuts… (R-37) — a read-only reference table, same
        MODAL treatment as Report: nothing here ever needs to stay open
        alongside the dial."""
        ShortcutsDialog(self._translation_overlay).exec()

    def _open_guide(self) -> None:
        """📖 Guide… — the help book is a CARD in the Encyclopedia now
        (owner decision 2026-07-28, Session 27: "jedno mesto za čitanje
        svega"). The menu entry survives as the SHORTCUT the owner asked
        for: it opens the Encyclopedia straight on that card, instead of
        raising a second reader with its own layout for the same
        content (Rule #6 — the standalone GuideDialog is retired, not
        kept alongside)."""
        self._open_encyclopedia_at("guide", 0)

    # --- The Watch Face window (Phase ①+②, R-01; sole survivor after ------
    # Phase 6 FINAL cleanup retired Design/Pointer Theme/Slot Theme) -------

    @paths.in_display
    def _reopen_live(self, dialog) -> bool:
        """Bring an already-open single-instance window back to the
        front — the shared door for every "open (or raise)" handler
        below (Rule #5). Answers False when the window is NOT actually
        there any more, so the caller drops its stale reference and
        builds a fresh one.

        THE DEAD REFERENCE (owner bug 2026-08-07: "od 6 otvorenih satova
        CHI neće da mi otvori Watch Face, ostali hoće"). These handlers
        used to trust `self._<window> is not None` and call `raise_()`
        alone, which fails in TWO ways that both look identical to the
        user — a menu item that does nothing, on one watch, forever:

        * a window HIDDEN without `done()` never emits `finished`, so
          the reference stayed set while nothing was on screen, and
          `raise_()` on a hidden window shows nothing. Hence `show()`
          first, unconditionally.
        * a window whose C++ object is already gone leaves a live Python
          wrapper behind, and every call on it raises `RuntimeError`
          inside a Qt slot, where it is swallowed. That family is not
          hypothetical here — the owner's own `crash.log` carries 640
          `Internal C++ object (ClockWidget) already deleted`
          tracebacks from the leaked-filter bug. Hence the except."""
        if dialog is None:
            return False
        try:
            dialog.show()
            dialog.raise_()
            dialog.activateWindow()
        except RuntimeError:
            return False
        return True

    def _open_watch_face(self) -> None:
        """Open (or raise) the [Watch Face Window](../watch_face/__about/window.md)
        — NON-MODAL, LIVE-APPLY: a second open request raises the ONE
        live instance (`_reopen_live`, which also rescues a watch whose
        window died behind its reference)."""
        if self._reopen_live(self._watch_face):
            return
        self._watch_face = None
        dialog = WatchFaceDialog(
            self._settings, self._watch_face_setters(),
            overlay=self._translation_overlay,
            stay_on_top=self._settings.z_mode == "top",
        )
        dialog.finished.connect(self._on_watch_face_closed)
        self._watch_face = dialog
        dialog.show()

    def _on_watch_face_closed(self, _result: int = 0) -> None:
        self._watch_face = None

    def _watch_face_setters(self) -> dict:
        """One setter per Watch Face section, wrapped so a pick both
        applies through the SAME `_set_*` controller methods every
        caller shares (Rule #5) and refreshes the open window live,
        plus the two additions this phase's sections need:
        `daylight` (R-05, moved here from the Settings dialog's Archetype
        group — same key) and the per-element scale keys (R- Size
        section — the Settings dialog only ever applied these on OK; here
        they are LIVE, like every other Watch Face pick)."""
        def wrap(setter):
            # `functools.wraps` is not cosmetics here (2026-08-15): it
            # sets `__wrapped__`, so `inspect.signature` sees the REAL
            # setter's arity through the wrapper. The per-section Reset
            # (app.watch_face.section_reset) reads exactly that to tell
            # a one-value setting apart from a target-plus-value one
            # like `palettes` — without it every setter here looks like
            # `(*args, **kwargs)` and the Reset can never be safe.
            @functools.wraps(setter)
            def wrapped(*args, **kwargs):
                setter(*args, **kwargs)
                if self._watch_face is not None:
                    self._watch_face.refresh(
                        self._settings, self._watch_face_setters()
                    )
            return wrapped

        return {
            # THE PLAIN DISPLAY CHOICES — every control whose whole job
            # is "store this key and rebuild the skin" is a ROW in
            # `config.watch_face.DISPLAY_CHOICE_KEYS`, not a block here
            # (OOP audit 2026-08-18: this was written out fifty-six
            # times, the key repeated twice per line). The seven MOVING
            # BODY menus take the same path but are named by their own
            # registry, so a body can never be added in one place and
            # forgotten in the other.
            **{
                key: wrap(_display_choice(self._set_display_choice, key))
                for key in (*watch_face_keys.DISPLAY_CHOICE_KEYS,
                            *umbra.MOVING_BODY_MENUS)
            },
            # --- and the controls that are NOT a plain key write -------
            # Each of these needs a method of its own: it touches more
            # than one key, opens a window, or ANSWERS a question
            # instead of setting anything. One line each, so that being
            # special is visible.
            "ring": wrap(self._set_ring),
            "ring_eye_shine": wrap(self._set_ring_eye_shine),
            "ring_inner": wrap(self._set_ring_inner),
            "custom_ring_crown_text": wrap(self._set_custom_ring_crown_text),
            "custom_ring_crown_orientation": wrap(
                self._set_custom_ring_crown_orientation
            ),
            "ring_crown_location": wrap(self._set_ring_crown_location),
            "open_custom_ring": self._open_custom_ring_editor,
            "hands": wrap(self._set_hands),
            "earth_label": wrap(self._set_earth_label),
            "diameter": wrap(self._set_diameter),
            "slot_layout": wrap(self._set_slot_layout),
            "theme_metal": wrap(self._set_theme_metal),
            "palettes": wrap(self._set_watch_face_palette),
            # A data PROVIDER, not a scalar setter (Rule #5): the
            # Themes & Slots section reuses the EXACT `SlotDescriptor`
            # triple `_slot_descriptors()` builds — its own `wrap()`
            # already refreshes this window (see above), so no second
            # wrapping here.
            "slot_descriptors": self._slot_descriptors,
            # A data PROVIDER too: the Opacity section's None-override
            # sliders (Pointer/Aura/Moon transit/Inactive icons) need
            # the ACTIVE skin's own resolved value to show a true "Skin
            # default" reset target — read here instead of widening
            # `builder(settings, setters, tr)`'s shared shape.
            "opacity_skin_defaults": self._opacity_skin_defaults,
            # A data PROVIDER (the same shape): whether the ACTIVE ring
            # preset carries a Crown Text at all — Opacity/Size/Colors
            # each grey their Crown Text row when this reads False
            # (graceful truth, not a dead control).
            "ring_has_crown_text": lambda: bool(self._skin.ring.crown_text),
        }

    def _opacity_skin_defaults(self) -> dict:
        """The active skin's own opacity values, keyed exactly like
        their matching `Settings` override field."""
        skin = self._skin
        return {
            "star_alpha": skin.star.day_alpha,
            "aura_day_alpha": skin.background.day_alpha,
            "aura_twilight_alpha": skin.background.twilight_alpha,
            "moon_transit_alpha": skin.year_marker.transit_alpha,
            "ghost_alpha": skin.weekday_set.ghost_opacity,
        }

    def _set_theme_metal(self, theme: str, metal: str) -> None:
        """Phase 6 FINAL cleanup: one theme's own metal pick inside the
        Theme rotation group's per-theme combos — the SAME `theme_
        metals` dict `SettingsDialog.result_settings()` used to write
        on OK, applied live instead."""
        metals = dict(self._settings.theme_metals)
        if metals.get(theme) == metal:
            return
        metals[theme] = metal
        self._settings = replace(self._settings, theme_metals=metals)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _set_watch_face_palette(self, pointer: str, style: str, hues: tuple) -> None:
        """R-21 item 2 — the Watch Face Palette chips' LIVE-APPLY twin of
        `SettingsDialog.result_settings`'s palette-on-OK commit: the SAME
        `palettes` dict, keyed `f"{pointer}_{style}"`, with the SAME
        preset-equals-no-override rule (a hue tuple that matches the
        owner preset again is dropped, not stored, so a later preset
        retune keeps reaching this (pointer, style) unless the reader
        chose otherwise)."""
        key = f"{pointer}_{style}"
        preset = palette.PALETTE_PRESETS[(pointer, style)]
        palettes = dict(self._settings.palettes)
        if tuple(hues) != tuple(preset):
            palettes[key] = tuple(hues)
        else:
            palettes.pop(key, None)
        if palettes == self._settings.palettes:
            return
        self._settings = replace(self._settings, palettes=palettes)
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._flush_position()

    def _open_custom_ring_editor(self) -> None:
        """R-13: the Watch Face Ring section's "Custom ring…" button —
        the custom-ring flow itself lives only inside
        `SettingsDialog` (a mixin, not a standalone dialog), so this
        opens THAT dialog navigated straight to its Custom art section
        rather than duplicating its inline widgets. Modal (`exec()`),
        the SAME transactional lifecycle `_open_settings` always used —
        stacking a modal dialog on top of the non-modal Watch Face
        window is ordinary Qt behavior."""
        dialog = SettingsDialog(
            self._settings, self._skin, self._translation_overlay,
            initial_section="Custom art",
        )
        if dialog.exec() != SettingsDialog.DialogCode.Accepted:
            return
        self._apply_settings_dialog_result(dialog)

    def _slot_descriptors(self) -> tuple:
        """One `SlotDescriptor` per slot, built fresh from the LIVE
        settings — each carries its OWN setter, wrapped so a pick
        BOTH applies (through the SAME `_set_slot`/`_set_display_choice`
        methods the keyboard and the old menu chain use, Rule #5) AND
        re-supplies the
        Watch Face window with a fresh triple (R-18, Watch Face
        Phase ③: the content tree is the sole reader since Phase 6
        FINAL cleanup retired the Slot Theme window)."""
        settings = self._settings

        def wrap(setter):
            # `functools.wraps` is not cosmetics here (2026-08-15): it
            # sets `__wrapped__`, so `inspect.signature` sees the REAL
            # setter's arity through the wrapper. The per-section Reset
            # (app.watch_face.section_reset) reads exactly that to tell
            # a one-value setting apart from a target-plus-value one
            # like `palettes` — without it every setter here looks like
            # `(*args, **kwargs)` and the Reset can never be safe.
            @functools.wraps(setter)
            def wrapped(*args, **kwargs):
                setter(*args, **kwargs)
                if self._watch_face is not None:
                    self._watch_face.refresh(
                        self._settings, self._watch_face_setters()
                    )
            return wrapped

        def descriptor(index: int) -> SlotDescriptor:
            keys = SLOT_KEYS[index]
            return SlotDescriptor(
                index=index, title=keys["title"],
                mode_value=getattr(settings, keys["mode"]),
                style_value=getattr(settings, keys["style"]),
                theme_value=getattr(settings, keys["theme"]),
                roster_value=getattr(settings, keys["roster"]),
                names_value=getattr(settings, keys["names"]),
                enabled_value=getattr(settings, keys["enabled"]),
                # The mode setter is the ONE the keyboard cycles through
                # too (`_slot_mode_state`), day slot's no-op guard and
                # all — never a second spelling of the same pick.
                set_mode=wrap(self._slot_mode_state(index)[1]),
                set_style_mode=wrap(
                    lambda mode, style: self._set_slot(index, mode, style=style)
                ),
                set_weekday=wrap(
                    lambda theme, metal=None, roster=None: self._set_slot(
                        index, "weekday", theme=theme, metal=metal,
                        roster=roster,
                    )
                ),
                set_names=wrap(
                    lambda checked, key=keys["names"]:
                    self._set_display_choice(key, checked)
                ),
            )

        return tuple(descriptor(index) for index in sorted(SLOT_KEYS))

    @paths.in_display
    def _open_observatory(self) -> None:
        """Open (or raise) the [Observatory](observatory.md) with the
        EFFECTIVE moment/observer — the frozen Time Travel tuple when
        simulating, else the live present — and the optional Deep Time
        pack (exact nearest-eclipse instants when installed).
        NON-MODAL (ITEM 1, R4): `.show()` instead of `.exec()`, so the
        dial stays interactive while it is open; a second open request
        RAISES the ONE live instance (its own Enlarge flow already runs
        non-modal too — see `ObservatoryDialog._open_enlarged`)."""
        if self._reopen_live(self._observatory):
            return
        self._observatory = None
        if self._simulation is not None:
            now = self._simulated_moment()
            observer = self._simulation[1]
            cycles = self._sim_cycles
        else:
            now = datetime.now(self._tz)
            observer = self._observer
            cycles = 0
        dialog = ObservatoryDialog(
            now, observer, self._tz, cycles=cycles,
            deep=self._deep, translations=self._translation_overlay,
            # FIX ROUND A (owner verdict 2026-07-19): in "top" z-mode
            # the dial is natively HWND_TOPMOST — this dialog must also
            # carry WindowStaysOnTopHint to open ABOVE it, matching
            # Settings/Time Travel/Guide; every other z-mode stays a
            # normal window (owner 2026-07-13 intent, unchanged).
            stay_on_top=self._settings.z_mode == "top",
        )
        dialog.finished.connect(self._on_observatory_closed)
        self._observatory = dialog
        dialog.show()

    def _on_observatory_closed(self, _result: int = 0) -> None:
        self._observatory = None

    @paths.in_display
    def _open_encyclopedia_at(
        self, topic: str | None = None, entry: int = 0
    ) -> None:
        """Open (or navigate) the Encyclopedia — from the menu (topic
        None = the gallery) or on a Spacebar jump to a hovered topic's
        entry (owner 2026-07-16, ROADMAP queue #8). NON-MODAL (ITEM 1,
        R4 owner instruction batch 2026-07-20): `.show()` instead of
        `.exec()`, so the dial stays interactive while it is open. The
        old re-entrancy guard (owner 15h item 3C) becomes "act on the
        live one" — a THEMED second jump (a real topic — a held key's
        auto-repeat, or a fresh SPACE press over a different target)
        NAVIGATES the live window to the new target
        (`EncyclopediaDialog.navigate_to`, a strict improvement over the
        old modal no-op); the menu's plain "Encyclopedia…" re-open
        (topic=None) just raises it without disturbing what the user is
        already browsing."""
        if self._encyclopedia is not None:
            try:
                self._encyclopedia.navigate_to(topic, entry)
            except RuntimeError:
                self._encyclopedia = None      # its C++ object is gone
            if self._reopen_live(self._encyclopedia):
                return
            self._encyclopedia = None
        dialog = EncyclopediaDialog(
            self._translation_overlay,
            hidden_unlocked=self._hidden_unlocked,
            # THE POEM'S OWN DAYS (owner decree 2026-08-11): on the two
            # solstices the Four Greetings stand in the open — the
            # DISPLAYED day's own reading (a running Time Travel
            # simulation counts), from the same season anchors every
            # turning-point badge already reads.
            verses_in_the_open=self._verses_in_the_open(),
            initial_topic=topic,
            initial_entry=entry,
            # FIX ROUND A (owner verdict 2026-07-19): see the
            # matching Observatory comment — "top" z-mode needs
            # WindowStaysOnTopHint to clear the dial's native
            # HWND_TOPMOST; every other z-mode stays normal.
            stay_on_top=self._settings.z_mode == "top",
            # The Scale rotation (owner decree 2026-07-19/20) reads
            # the same TRAVELED date as the poles' light/dark glyph
            # law — a running Time Travel simulation, else today.
            travel_date=self._effective_travel_date(),
            language=self._settings.language,
            # THE DOUBLE NINTH LAW's daynight mechanism (owner decree
            # 2026-07-29, sw_dyad's Ghosts/Exegol): the SAME live sky
            # state the dial's own center seat reads.
            is_daylight=self._effective_is_daylight(),
        )
        dialog.finished.connect(self._on_encyclopedia_closed)
        self._encyclopedia = dialog
        dialog.show()

    def _on_encyclopedia_closed(self, _result: int = 0) -> None:
        self._encyclopedia = None

    @paths.in_display
    def _open_settings(self) -> None:
        dialog = SettingsDialog(
            self._settings, self._skin, self._translation_overlay
        )
        if dialog.exec() != SettingsDialog.DialogCode.Accepted:
            return
        self._apply_settings_dialog_result(dialog)

    def _apply_settings_dialog_result(self, dialog: SettingsDialog) -> None:
        """Everything an ACCEPTED `SettingsDialog` triggers — shared by
        `_open_settings` and the Watch Face Ring section's "Custom
        ring…" button (`_open_custom_ring_editor`, R-13), which opens
        the SAME dialog navigated to a different section (Rule #5: one
        apply path, however the dialog was reached)."""
        new_settings = dialog.result_settings()
        # ONE comparison of ONE object (owner decree 2026-08-16): a
        # location either changed or it did not, and asking three
        # separate fields whether they moved is how the parts drifted
        # apart in the first place. The NAME and the PATH count too —
        # picking a different city at the same coordinates (a renamed
        # record, a Quick Jump city applied as home) is a real change
        # the crown must follow.
        location_changed = new_settings.place != self._settings.place
        language_changed = new_settings.language != self._settings.language
        self._settings = new_settings
        if language_changed:
            self._apply_language(start_missing=True)
        if location_changed:
            self._tz = ZoneInfo(new_settings.place.timezone)
            self._observer = astral.Observer(
                latitude=new_settings.place.latitude,
                longitude=new_settings.place.longitude,
            )
            self._day = None                # full rebuild for the new place
            self._flash_location(          # R-30: the Settings preset pick
                new_settings.place.name,
                new_settings.place.path,
                new_settings.place.timezone,
            )
        # Rebuild from DEFAULT_SKIN so cleared overrides (back to "skin
        # default") actually clear instead of sticking.
        self._install_skin(build_skin(self._settings, self._active_location_display))
        # The visibility Z mode may have changed (owner 2026-07-17): swap
        # the window flags (a no-op when unchanged). The swap recreates the
        # native window and DROPS the screenChanged connection (the S18
        # caveat) — reconnect it on the fresh handle when it actually
        # swapped; set_z_mode itself re-asserts native topmost for "top".
        if self._widget.set_z_mode(self._settings.z_mode):
            self._widget.windowHandle().screenChanged.connect(
                self._on_screen_changed
            )
        self._on_tick(clock_jumped=False)
        # The menu mirrors the settings (checkmarks, custom rings in
        # Theme > Ring) — rebuild it wholesale after every dialog OK.
        self._menu = self._build_menu()
        self._widget.set_menu(self._menu)
        self._widget.set_show_action(self._show_action)
        self._tray.set_menu(self._menu)
        self._configure_theme_rotation()
        native.set_autostart(dialog.autostart_selected())
        self._flush_position()

    def _bundled_coverage(self) -> tuple[int, int]:
        """The INTERSECTION of the two bundled databases' coverage —
        the minute-exact core tier (both are needed to build a day).
        Read from the data, never hardcoded."""
        seasons_first, seasons_last = self._seasons.coverage()
        moon_first, moon_last = self._moon_phases.coverage()
        return max(seasons_first, moon_first), min(seasons_last, moon_last)

    def _travel_coverage(self) -> tuple[int, int]:
        """The years Time Travel can render: the bundled intersection,
        widened to the Deep Time pack's own coverage when the pack is
        present (Session 16) — both spans read from their data."""
        first, last = self._bundled_coverage()
        if self._deep is not None:
            deep_first, deep_last = self._deep.coverage()
            return min(first, deep_first), max(last, deep_last)
        return first, last
