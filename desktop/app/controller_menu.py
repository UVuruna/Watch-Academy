"""The dial's right-click / tray menu: builds it, and keeps its
checks and gray states in step with the settings.

A mixin of [WatchController](controller.md). Every entry it creates
calls a setter that lives in
[the display mixin](controller_display.md) or a dialog host in
[the dialog mixin](controller_dialogs.md) — this module owns the MENU,
never what an entry does.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QLabel, QMenu, QWidgetAction

from app.skin_builder import slot_seconds, watch_title
from config import archetypes, palette, shortcuts
from config.ui_text import ui


def _guard_exclusive_choice(action: QAction, apply) -> None:
    """Wire one member of an EXCLUSIVE QActionGroup so a click on the
    ALREADY-CHECKED member is a no-op (ROADMAP 15h item 8's surviving
    bug, owner screenshot: Planetary/Pantheon both unchecked). Qt's own
    exclusive QActionGroup only auto-unchecks SIBLINGS when a DIFFERENT
    member becomes checked (a `toggled`, not `triggered`, side effect);
    it does nothing to stop the user clicking the sole checked member
    itself, which flips it straight to unchecked and leaves the whole
    group empty. One member must always hold, so a self-uncheck
    restores the check instead of applying anything — the shared fix
    behind `_add_choice_group` (Pointer/Ring/Umbra/…) AND the slot
    menus' `slot_action` (Weekday themes, Complications, astrology
    families, the roster pairs) — every exclusive QActionGroup in the
    app menu routes through one of those two."""
    def _on_triggered(checked: bool) -> None:
        if not checked:
            action.setChecked(True)
            return
        apply()
    action.triggered.connect(_on_triggered)


class _StayOpenMenu(QMenu):
    """A menu whose CHECKABLE items do not close it (owner menu rework
    2026-07-13: several settings in one visit) — plain actions (Exit,
    Settings…) close as usual; Escape or clicking away closes too.
    Plain actions carrying the "stay_open" property keep it open the
    same way (owner 2026-07-15: chaining Quick Jumps in one visit)."""

    def mouseReleaseEvent(self, event) -> None:
        action = self.actionAt(event.position().toPoint())
        if (
            action is not None
            and action.isEnabled()
            and (action.isCheckable() or action.property("stay_open"))
        ):
            action.trigger()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class _ContextMenuMixin:
    """ContextMenuMixin — see the module docstring."""

    def _refresh_menu_gating(self) -> None:
        """Recompute every gated FLAT menu entry from the CURRENT
        settings without rebuilding (the stay-open menu keeps its
        window; only the gray states move). Phase 6 FINAL cleanup
        retired the Design/Pointer Theme/Slot Theme windows and their
        own per-entry gates — the Watch Face window recomputes its own
        content live on every `refresh()` instead of being gated here.
        What remains gated at the FLAT top level is the
        Show/Archetype/Solar-rotation toggles and the big seconds
        hand."""
        settings = self._settings
        # SHOW (owner 2026-07-18): meaningless outside "normal" z-mode —
        # HIDDEN there, not grayed.
        self._show_action.setVisible(settings.z_mode == "normal")
        # THE ARCHETYPE MODE gating (owner sealed package 2026-07-16):
        # the toggle grays where no archetype exists — Aurora and the
        # Calendar — and with the Pointer element off (no diamonds, no
        # figures).
        archetype_available = (
            settings.show_pointer
            and archetypes.has_archetype(settings.pointer)
        )
        archetype_on = archetype_available and settings.archetype_mode
        self._archetype_action.setEnabled(archetype_available)
        # A seated small-seconds slot cannot silence the big hand
        # while the archetype mode overrides the slots.
        self._seconds_gate_action.setEnabled(
            not (slot_seconds(settings) and not archetype_on)
        )
        self._solar_rotation_action.setEnabled(
            settings.pointer != "aurora"
        )

    def _add_choice_group(
        self, menu: QMenu, submenu: QMenu, options, current, setter, disabled=()
    ) -> list[QAction]:
        """One exclusive check-group appended to `submenu`: options are
        (value, label) pairs; values in `disabled` render grayed out.
        Returns the created actions (owner 2026-07-16: some groups need
        to be re-grayed in place later, e.g. Paint/Light on trio/cross)."""
        group = QActionGroup(menu)
        group.setExclusive(True)
        actions = []
        for value, label in options:
            action = QAction(label, menu)
            action.setCheckable(True)
            action.setChecked(value == current)
            action.setEnabled(value not in disabled)
            _guard_exclusive_choice(action, lambda chosen=value: setter(chosen))
            group.addAction(action)
            submenu.addAction(action)
            actions.append(action)
        return actions

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

    @staticmethod
    def _labeled(text: str, action_id: str) -> str:
        """R5 doubt 4 FOLLOW-UP (R5b round, owner spec): appends the
        shortcut's own "Ctrl+X" combo to a flat menu entry's text via a
        tab character — Qt's own convention for a right-aligned
        accelerator-style hint in a QMenu row, WITHOUT wiring a real
        competing `QAction.setShortcut` (every shortcut already fires
        through `ClockWidget.keyPressEvent` -> `shortcut_triggered`; a
        second Qt-level shortcut on the SAME key would double-dispatch).
        Only entries with a DIRECT, unambiguous 1:1 shortcut (the five
        dialog openers + Archetype) use this — the cycling/Fast-Travel/
        Location shortcuts live inside mini windows or have no menu
        surface of their own at all."""
        return f"{text}\t{shortcuts.shortcut_display(action_id)}"

    def _build_menu(self) -> QMenu:
        menu = _StayOpenMenu()
        settings = self._settings
        tr = self._ui
        # TITLE ROW (owner INSTRUCTION.txt item 2A, R5 MENU REWORK): the
        # watch's own name heads BOTH the right-click and the tray menu
        # (they share this ONE QMenu) — a passive styled header, never
        # clickable/checkable (Rule #8 alternative: a disabled QAction
        # still hover-highlights on some platforms; a QWidgetAction
        # hosting a QLabel reads unambiguously as a header, the SAME
        # pattern the Size slider row below already uses). A single
        # watch shows just its location (`full=False`); ADD WATCH round
        # (owner: "Title ne treba pun naziv ako nema potrebe"): with 2+
        # watches alive (`self._watch_count()`, the manager's live
        # roster size) this row switches to the full multi-attribute
        # form too — the tray HOVER tooltip below stays full regardless
        # of count, always has.
        title_label = QLabel(
            watch_title(
                settings, full=self._watch_count() >= 2,
                location_name=self._active_location_name,
            )
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-weight: 700; font-size: 13px; padding: 6px 12px;"
            f"color: {palette.THEME_COLORS['accent']};"
        )
        title_action = QWidgetAction(menu)
        title_action.setDefaultWidget(title_label)
        menu.addAction(title_action)
        self._title_label = title_label
        # WARM STATUS ROW (0.14.710; owner: "može da da INFO LOADING dok
        # učitava a NIKAKO LAG STUCK SCREEN"): while any background phase
        # is still working — the startup warm or an on-demand art drain —
        # the menu names it, refreshed on every open; hidden when idle.
        # A QWidgetAction-hosted QLabel like the title above (a disabled
        # QAction still hover-highlights on some platforms).
        status_label = QLabel()
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(
            "font-size: 11px; padding: 2px 12px 6px 12px;"
            f"color: {palette.THEME_COLORS['text_secondary']};"
        )
        status_action = QWidgetAction(menu)
        status_action.setDefaultWidget(status_label)
        status_action.setVisible(False)
        menu.addAction(status_action)
        self._warm_status_label = status_label
        self._warm_status_action = status_action
        menu.aboutToShow.connect(self._refresh_warm_status_row)
        menu.addSeparator()
        # ADD WATCH (owner INSTRUCTION.txt item 2, sealed 2026-07-21):
        # "na vrhu... ispod TITLE info" — directly below the title row,
        # on EVERY watch. Seeds a new watch from THIS watch's current
        # settings ([the manager](watch_manager.md)'s `add_watch`);
        # `self._on_add_watch` defaults to a no-op for standalone/test
        # use (no manager attached) and is reassigned by the manager
        # right after construction — the lambda below re-reads it
        # fresh on every click, never binding a stale target.
        add_watch_action = QAction(f"➕ {tr('Add Watch')}", menu)
        add_watch_action.triggered.connect(lambda: self._on_add_watch())
        menu.addAction(add_watch_action)
        # REMOVE THIS WATCH (same round, architecture guidance): watch 1
        # is the anchor and never offers it — only watches 2+ do. One
        # plain Yes/No confirm (`_confirm_remove_watch`), no further
        # dialogs (owner spec).
        if self._watch_index != 1:
            remove_watch_action = QAction(f"➖ {tr('Remove this Watch')}", menu)
            remove_watch_action.triggered.connect(self._confirm_remove_watch)
            menu.addAction(remove_watch_action)
        menu.addSeparator()
        # SHOW (owner 2026-07-18, ROADMAP 15h, Session 21-C): in
        # "normal" z-mode the dial rides above other windows ONLY while
        # focused — the owner loses it under other windows otherwise.
        # This entry raises it on demand; MEANINGLESS in "bottom" (never
        # above anything) and "top" (already always above), so it is
        # HIDDEN there, not merely grayed — `_refresh_menu_gating`
        # updates its visibility on every z_mode change. Sits at the
        # very TOP of the menu (owner: "na samom vrhu").
        self._show_action = QAction(f"👁️ {tr('Show')}", menu)
        self._show_action.triggered.connect(self._show_if_normal_z_mode)
        self._show_action.setVisible(settings.z_mode == "normal")
        menu.addAction(self._show_action)
        menu.addSeparator()
        # Menu rework (owner 2026-07-13): emoji-fronted top level —
        # Design / Primary Slot / Secondary Slot / Elements, then the
        # three switches, the four windows, Exit — and checkable picks
        # keep the menu OPEN. DESIGN = how the instrument looks
        # (Pointer, Ring, Umbra | Hands, Earth | Size).
        # DESIGN / POINTER THEME / SLOT THEME (R5 MENU REWORK item 3,
        # owner spec — the exact "4-5 branching levels stack one over
        # another in a screen corner" complaint that opened this round,
        # `UV/DESIGN/Meni One over Another.png`): ONE flat entry opens
        # the consolidated WATCH FACE window (Phase 6 FINAL cleanup
        # retired the Design/Pointer Theme/Slot Theme mini windows this
        # phase originally sat alongside — see `watch_face/window.md`).
        watch_face_action = QAction(
            self._labeled(f"🕹️ {tr('Watch Face…')}", "open_watch_face"), menu
        )
        watch_face_action.triggered.connect(self._open_watch_face)
        menu.addAction(watch_face_action)
        # Visible (owner spec; renamed from Elements, R5 MENU REWORK
        # item E — Rule #6, every reference below renamed with it):
        # plain on/off switches — the slots enable INSIDE their own
        # submenus now (owner 2026-07-14), so only the star, its
        # colors, the two markers and the seconds hand remain.
        visible_menu = self._submenu(menu, f"🧩 {tr('Visible')}")
        self._visible_toggles: list = []
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
                "show_eclipse", tr("Eclipse"),
                tr("The eclipse body: a solar or lunar eclipse standing at "
                   "the hour it happens, apart from the Earth and the Moon."),
            ),
            (
                "show_seconds", tr("Seconds"),
                tr("The seconds hand. Off: it is not drawn and the dial "
                   "ticks once per minute."),
            ),
        ):
            action = self._add_toggle(
                visible_menu, label, getattr(settings, key),
                lambda checked, key=key: self._set_visible(key, checked),
                tip,
            )
            self._visible_toggles.append((action, key))
            if key == "show_seconds":
                # The big hand yields while a slot runs the
                # small-seconds complication (owner 2026-07-14).
                self._seconds_gate_action = action
                action.setEnabled(not slot_seconds(settings))
        # Clicking the top-level Visible entry flips ALL of them at once
        # (owner 2026-07-17, ROADMAP 15e): the check shows ONLY when every
        # entry is on; a click while all-on turns them all off, otherwise
        # it turns them all on. The submenu still opens on hover/arrow.
        self._visible_menu_action = visible_menu.menuAction()
        self._visible_menu_action.setCheckable(True)
        self._visible_menu_action.triggered.connect(
            lambda checked=False: self._toggle_all_visible()
        )
        self._refresh_visible_check()
        # NAMES (R-09/R-26, Phase 6 FINAL cleanup): the two independent
        # name/title toggles unified beside Visible — the weekday-body
        # day name (owner spec: previously buried, unreachable from any
        # menu) and the archetype figures' names (moved off the Settings
        # dialog's retired Display ▸ Archetype group, same stored key,
        # `archetype_names`). Both write the SAME `Settings` fields every
        # other reader (`render.layers`, the Watch Face window) already
        # uses — no new setting invented.
        names_menu = self._submenu(menu, f"🔤 {tr('Names')}")
        self._add_toggle(
            names_menu, tr("Weekday names"), settings.show_weekday_names,
            lambda checked: self._set_display_choice(
                "show_weekday_names", checked
            ),
            tr("The day name written on the weekday bodies."),
        )
        self._add_toggle(
            names_menu, tr("Archetype names"), settings.archetype_names,
            lambda checked: self._set_display_choice(
                "archetype_names", checked
            ),
            tr("The archetype figures' names."),
        )
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
        # THE ARCHETYPE MODE (owner sealed package 2026-07-16): the
        # stay-open checkable beside Solar rotation — the diamonds fill
        # with the active wheel's archetype figures, the hour hand
        # lights the one whose hour-space it is in, and the weekday
        # model and all three slots step aside (render-level override —
        # the slot settings stay put). Grayed on Aurora/Calendar.
        self._archetype_action = self._add_toggle(
            menu,
            self._labeled(f"🎭 {tr('Archetype')}", "toggle_archetype"),
            settings.archetype_mode,
            lambda checked: self._set_display_choice(
                "archetype_mode", checked
            ),
            tr(
                "The diamonds carry the active wheel's archetype "
                "figures; the hour hand lights the one whose "
                "hour-space it is in. The weekday model and the slots "
                "step aside while it runs."
            ),
        )
        # ARCHETYPE NAMES moved into Settings ▸ Display as its OWN
        # independent switch (owner 2026-07-18, ROADMAP 15h, Session
        # 21-C: "nemoj ispod nego u Settings — ON/OFF") — the menu twin
        # that used to sit here, writing the shared `show_weekday_names`
        # key, is GONE; `archetype_names` is its own setting now,
        # `ArchetypeLayer` reads it directly.
        # (The Earth-weekday toggle moved to Design ▸ Earth as a general
        # option, owner 2026-07-17 slika 10 — it works in both modes now.)
        self._add_toggle(
            menu, f"🖱️ {tr('Click-through')}", self._settings.click_through,
            self._set_click_through,
            tr("The dial takes no clicks at all (they pass to the desktop); "
               "hover info still works. Turn it back off here in the tray."),
        )
        menu.addSeparator()
        settings_action = QAction(
            self._labeled(f"⚙️ {tr('Settings…')}", "open_settings"), menu
        )
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)
        encyclopedia = QAction(
            self._labeled(f"🏛️ {tr('Encyclopedia…')}", "open_encyclopedia"),
            menu,
        )
        encyclopedia.triggered.connect(
            lambda: self._open_encyclopedia_at(None, 0)
        )
        menu.addAction(encyclopedia)
        observatory = QAction(
            self._labeled(f"🔭 {tr('Observatory…')}", "open_observatory"),
            menu,
        )
        observatory.triggered.connect(self._open_observatory)
        menu.addAction(observatory)
        guide = QAction(
            self._labeled(f"📖 {tr('Guide…')}", "open_guide"), menu
        )
        guide.triggered.connect(self._open_guide)
        menu.addAction(guide)
        time_travel = QAction(
            self._labeled(f"🕰️ {tr('Time Travel…')}", "open_time_travel"),
            menu,
        )
        time_travel.triggered.connect(self._open_time_travel)
        menu.addAction(time_travel)
        # R-37: a plain reference window, no shortcut of its own (it is
        # the thing that explains every OTHER row's shortcut column).
        shortcuts_action = QAction(f"⌨️ {tr('Shortcuts…')}", menu)
        shortcuts_action.triggered.connect(self._open_shortcuts)
        menu.addAction(shortcuts_action)
        # QUICK JUMP DIED HERE (owner rounds 2026-07-14/15; Session 16
        # rework, slika 12; RETIRED R5 MENU REWORK item 4 — Rule #6, no
        # both-paths): the deep 4-5-level submenu chain this used to be
        # (`UV/DESIGN/RIGHT CLICK MENU.txt`, `Meni One over Another.png`
        # — the exact complaint that opened this round) is GONE — every
        # motion it held now lives as a ROW inside the Time Travel
        # window itself (item 3A, `app.time_travel._build_jump_section`,
        # wired through `_dialog_jump`/`_compute_jump`), which the entry
        # above already opens.
        menu.addSeparator()
        # The hidden REPORT (owner 2026-07-15): function efficiency
        # statistics, visible only after the session unlock — above
        # Exit ("iznad Izlaza").
        self._report_action = QAction(f"📊 {tr('Report')}", menu)
        self._report_action.setVisible(self._hidden_unlocked)
        self._report_action.triggered.connect(self._open_report)
        menu.addAction(self._report_action)
        exit_action = QAction(f"🚪 {tr('Exit')}", menu)
        # Exit is PROCESS-WIDE (ADD WATCH round: unlike the per-watch
        # Remove entry above, it closes every watch, not just this
        # one) — `self._on_exit` defaults to `self.quit` (standalone
        # use); the manager passes its own `quit_all` instead.
        exit_action.triggered.connect(self._on_exit)
        menu.addAction(exit_action)
        # Normalize every gated state from the CURRENT settings — the
        # one gating implementation serves the fresh build and the
        # in-place refresh alike (Rule #5; the archetype/slot/palette
        # gates all live there).
        self._refresh_menu_gating()
        return menu
