"""Every keyboard shortcut the watch answers, and the flashes
they raise on the dial.

A mixin of [WatchController](controller.md): the actions all READ and
WRITE `self._settings`, `self._skin` and the open windows, so they keep
`self` instead of becoming a collaborator with a back-channel (the shape
`app.settings_dialog`'s section mixins already use). The dispatch table
itself is `config.shortcuts.SHORTCUTS`; `_on_shortcut` is its only
reader.
"""

from typing import Callable

from app.controller_display import _next_rotation_theme
from app.skin_builder import build_skin, effective_weekday_slot
from app.settings_store import replace, slot_layout_target
from config import archetypes, constants, defaults, pantheon, shortcuts
from config.registry.slots import SLOT_KEYS
from data.rings import ring_presets
from render.asset_variants import (
    calendar_sheet_icon_file, clock_face_icon_file, eclipse_sun_icon_file,
)


def _location_flash_text(name: str, path: tuple = (), timezone: str = "") -> str:
    """R-30: "CITY, COUNTRY" for the location-change flash. COUNTRY is
    `path[2]` when a full picked-city path is known (`data.locations.
    Place.path` is always (continent, subregion, country[, admin],
    city) — a Settings dialog preset pick carries it). A Quick Jump
    city stores only name/lat/lon/timezone (no path) and a hand-tuned
    coordinate has no picked path either — COUNTRY is genuinely
    unavailable there, so the honest fallback is the IANA timezone's
    own region ("Europe/London" -> "Europe"); a bare name is the last
    resort (the poles carry neither)."""
    if len(path) > 2:
        return f"{name}, {path[2]}"
    if timezone and "/" in timezone:
        region = timezone.split("/", 1)[0].replace("_", " ")
        return f"{name}, {region}"
    return name


class _ShortcutActionsMixin:
    """ShortcutActionsMixin — see the module docstring."""

    # --- Keyboard shortcuts (R5 MENU REWORK, `shortcuts.SHORTCUTS`) -------------

    #: Ordered exactly like the Weekday submenu (owner menu rework
    #: 2026-07-13): Planets first and flat, then the kinship groups.
    _WEEKDAY_THEME_ORDER = pantheon.WEEKDAY_MENU_TOP + tuple(
        key for _title, keys in pantheon.WEEKDAY_MENU_GROUPS for key in keys
    )
    #: The 4 Complication modes, in `constants.SLOT_COMPLICATION_TITLES`'s
    #: own dict order (Digital Time -> Date -> Day length -> Seconds) —
    #: the R5b SLOTS shortcuts (Ctrl+1/2/3) cycle through exactly this.
    _SLOT_COMPLICATION_ORDER = tuple(constants.SLOT_COMPLICATION_TITLES)

    def _on_shortcut(self, action_id: str) -> None:
        """Dispatch one `shortcuts.SHORTCUTS` entry (owner "OSMISLITI ŠTA
        SVE"; R5b FINAL MAP round for the SLOTS/FAST TRAVEL/LOCATIONS
        additions — the full map is designed and pinned by
        `tests/test_shortcuts.py`). Every shortcut needs the dial to
        hold keyboard focus (`ClockWidget.keyPressEvent` is the only
        source of this signal)."""
        handlers = {
            "cycle_ring": self._cycle_ring,
            "cycle_weekday_theme": self._cycle_weekday_theme,
            "cycle_slots": self._cycle_slots,
            "open_encyclopedia": lambda: self._open_encyclopedia_at(None, 0),
            "open_guide": self._open_guide,
            "open_settings": self._open_settings,
            "open_watch_face": self._open_watch_face,
            "open_observatory": self._open_observatory,
            "open_time_travel": self._open_time_travel,
            "return_to_now": self._end_simulation,
            "toggle_archetype": self._toggle_archetype_shortcut,
            "cycle_slot1_complication": lambda: self._cycle_slot_complication(1),
            "cycle_slot2_complication": lambda: self._cycle_slot_complication(2),
            "cycle_slot3_complication": lambda: self._cycle_slot_complication(3),
            "cycle_slot1_theme": lambda: self._cycle_slot_weekday_theme(1),
            "cycle_slot2_theme": lambda: self._cycle_slot_weekday_theme(2),
            "cycle_slot3_theme": lambda: self._cycle_slot_weekday_theme(3),
            "fast_travel_theme": self._cycle_fast_travel_theme,
            "fast_travel_option": self._cycle_fast_travel_option,
            "fast_travel_past": lambda: self._step_fast_travel(-1),
            "fast_travel_future": lambda: self._step_fast_travel(1),
            "location_north_pole": lambda: self._jump_to_place("north_pole"),
            "location_south_pole": lambda: self._jump_to_place("south_pole"),
            "location_greenwich": lambda: self._jump_to_place("greenwich"),
            "location_prev_city": lambda: self._cycle_jump_city(-1),
            "location_next_city": lambda: self._cycle_jump_city(1),
        }
        handlers[action_id]()

    def _cycle_ring(self) -> None:
        """Ctrl+R: the next Ring preset, alphabetically — the SAME
        order the Design window's Ring tab lists them in. `_set_ring`
        runs `_install_skin`, which refreshes any open mini window in
        place (`_refresh_open_mini_windows`) — no separate call needed
        here."""
        names = sorted(ring_presets(self._settings.custom_rings))
        current = names.index(self._settings.ring)
        self._set_ring(names[(current + 1) % len(names)])

    def _weekday_theme_on_diamonds(self) -> bool:
        """True when the 1st Slot's `weekday_theme` is the theme
        actually PAINTED on the star's diamonds right now (R5b round,
        owner spec for Ctrl+W: "ONLY when the theme is displayed on the
        DIAMONDS"). Four conditions: the pointer HAS diamonds at all
        (Aurora/Calendar draw none — `constants.POINTER_ARM_HALF_ANGLE_DEG`'s
        own membership is the existing test for that), the Pointer
        element is visible, the 1st Slot is visible, and its EFFECTIVE
        mode is "weekday" (`effective_weekday_slot`) rather than a
        digital/astrology complication. Under this last condition
        `_classic_slot_theme` ALWAYS returns `weekday_theme` — its own
        Seasons/Compass redirect to `info_slot_theme` fires ONLY when
        `effective_weekday_slot` is NOT "weekday" (see that function's
        docstring) — so nothing else can be silently wearing a
        DIFFERENT theme on the diamonds while this predicate holds."""
        settings = self._settings
        return (
            settings.pointer in constants.POINTER_ARM_HALF_ANGLE_DEG
            and settings.show_pointer
            and settings.show_weekday
            and effective_weekday_slot(settings) == "weekday"
        )

    def _cycle_weekday_theme(self) -> None:
        """Ctrl+W: the next Weekday theme (the 1st Slot's own —
        `_WEEKDAY_THEME_ORDER`, the Weekday grid's own order); the
        roster/metal the theme is already wearing stays untouched, like
        clicking the plain theme tile. STRICT NO-OP (R5b round, owner
        spec) unless `_weekday_theme_on_diamonds()` — cycling a theme
        nobody can see would be a silent, invisible state change.
        `_set_weekday_theme` runs `_install_skin`, which refreshes the
        Watch Face window in place when it happens to be open."""
        if not self._weekday_theme_on_diamonds():
            return
        order = self._WEEKDAY_THEME_ORDER
        current = order.index(self._settings.weekday_theme)
        self._set_weekday_theme(order[(current + 1) % len(order)])

    # --- SLOTS shortcuts (R5b round, owner spec) --------------------------------

    def _slot_active(self, index: int) -> bool:
        """Whether Slot `index` (1/2/3) is currently active/visible —
        the SAME effective enablement `apply_display_settings` renders
        with (the 3rd only counts on top of the 2nd, `show_third_slot
        and show_octa_slot` — the "slots enable IN ORDER" rule)."""
        settings = self._settings
        active = getattr(settings, SLOT_KEYS[index]["enabled"])
        return bool(active and (index != 3 or settings.show_octa_slot))

    def _slot_mode_state(self, index: int) -> tuple[str, Callable[[str], None]]:
        """(current mode, setter) for Slot `index`'s own MODE field —
        the SAME setters `_slot_descriptors()` wires the Watch Face
        window's own mode picker through (Rule #5).

        The DAY slot is the one exception, and it is a real one: its
        mode goes through `_set_display_choice`, whose no-op guard
        skips the whole skin rebuild when the pick did not change —
        `_set_slot` has no such guard, and giving it one would change
        what the other two slots do."""
        mode = getattr(self._settings, SLOT_KEYS[index]["mode"])
        if index == 1:
            return mode, (
                lambda new: self._set_display_choice("weekday_slot", new)
            )
        return mode, (lambda new: self._set_slot(index, new))

    def _slot_theme_state(self, index: int) -> tuple[str, Callable[[str], None]]:
        """(current weekday theme, setter) for Slot `index` — the setter
        ALSO switches that slot's mode to "weekday" as a side effect
        (the SAME `_set_slot` behavior the Watch Face window's own theme
        picker already relies on), so cycling the theme via the
        keyboard is also how you switch a slot INTO weekday-display
        mode with one repeated press."""
        theme = getattr(self._settings, SLOT_KEYS[index]["theme"])
        return theme, (
            lambda new: self._set_slot(index, "weekday", theme=new)
        )

    def _cycle_slot(self, index: int, state, order: tuple) -> None:
        """One step of a slot cycle: read `state(index)`'s current value
        and setter, advance it through `order`, apply. A strict no-op
        while the slot is not active/visible (`_slot_active`), and a
        value OUTSIDE the list starts the cycle from the top — the same
        "outside the list starts fresh" rule `_next_rotation_theme`
        already applies to theme rotation."""
        if not self._slot_active(index):
            return
        current, setter = state(index)
        setter(_next_rotation_theme(current, order))

    def _cycle_slot_complication(self, index: int) -> None:
        """Ctrl+1/2/3: the next Complication (Digital Time -> Date ->
        Day length -> Seconds, `_SLOT_COMPLICATION_ORDER`) in Slot
        `index`. A slot currently showing a NON-complication
        (Weekday/Zodiac/Ascendant/Chinese) starts the cycle from the
        top."""
        self._cycle_slot(index, self._slot_mode_state,
                         self._SLOT_COMPLICATION_ORDER)

    def _cycle_slot_weekday_theme(self, index: int) -> None:
        """Ctrl+Alt+1/2/3: the next Weekday theme in Slot `index`
        (`_WEEKDAY_THEME_ORDER`). Unlike Ctrl+W this carries NO
        "already displaying a theme" guard: the setter itself switches
        the slot's mode to "weekday" (see `_slot_theme_state`), so one
        press both picks the next theme AND makes it visible — the
        direct route into weekday-display mode for slots 2/3, which
        have no dedicated "show weekday bodies here" toggle of their
        own beyond picking a theme."""
        self._cycle_slot(index, self._slot_theme_state,
                         self._WEEKDAY_THEME_ORDER)

    # --- FAST TRAVEL shortcuts (R5b round, owner spec) --------------------------

    def _fast_travel_theme(self) -> dict:
        return shortcuts.FAST_TRAVEL_THEMES[self._fast_travel_theme_index]

    def _fast_travel_option_index(self, theme_id: str) -> int:
        """The REMEMBERED option cursor for `theme_id` (owner spec: each
        theme keeps its own pick across Ctrl+[ switches) — 0 (the
        theme's first option) for a theme never touched this session."""
        return self._fast_travel_option_indices.get(theme_id, 0)

    def _cycle_fast_travel_theme(self) -> None:
        """Ctrl+[: the next Fast Travel theme (Sun -> Moon -> Calendar
        -> Sun, `shortcuts.FAST_TRAVEL_THEMES`'s own order) — flashes the
        NEW theme's logo (owner spec: every Ctrl+[ / Ctrl+] change
        flashes)."""
        self._fast_travel_theme_index = (
            self._fast_travel_theme_index + 1
        ) % len(shortcuts.FAST_TRAVEL_THEMES)
        self._flash_fast_travel()

    def _cycle_fast_travel_option(self) -> None:
        """Ctrl+]: the next OPTION inside the ACTIVE theme — flashes it
        (owner spec)."""
        theme = self._fast_travel_theme()
        count = len(theme["options"])
        index = self._fast_travel_option_index(theme["id"])
        self._fast_travel_option_indices[theme["id"]] = (index + 1) % count
        self._flash_fast_travel()

    def _flash_fast_travel(self) -> None:
        """Show the ACTIVE (theme, option)'s icon + option text above
        THIS watch's own dial (owner spec: "per-watch — the focused
        watch flashes its own" — trivially true here since a shortcut
        only ever reaches the FOCUSED widget's `_on_shortcut` to begin
        with).

        THE OWNER'S OWN SIX (his order 2026-08-12): four categories name a
        file of his in `defaults.ICON_FILES` (`sun_eclipse.png`,
        `moon_eclipse_red.png`, `sun.svg`, `moon.svg`); Date and Time own
        no file and name a COMPUTED drawing through `computed_icon`
        instead (Rule #19) — the calendar sheet and the 24 h clock face,
        which retire the 📅 and 🕐 emoji fallbacks. A theme declaring
        neither still falls back to its own emoji, exactly as before."""
        theme = self._fast_travel_theme()
        option = theme["options"][self._fast_travel_option_index(theme["id"])]
        computed = {
            "calendar_sheet": calendar_sheet_icon_file,
            "clock_face": clock_face_icon_file,
            "eclipse_sun": eclipse_sun_icon_file,
        }.get(theme.get("computed_icon"))
        if computed is not None:
            # Drawn at the SUPERSAMPLE multiple the flash shrinks from,
            # so a computed glyph is never upscaled from its final size
            # only to be scaled back down (owner correction 2026-08-12).
            icon_path = computed(
                shortcuts.FAST_TRAVEL_FLASH_ICON_SUPERSAMPLE
                * shortcuts.FAST_TRAVEL_FLASH_ICON_PX
            )
        else:
            icon_key = theme["icon_key"]
            icon_path = (
                defaults.icon_path(icon_key) if icon_key is not None else None
            )
        # Category then option (owner spec 2026-08-11), composed for
        # THE LETTER PLATES the flash now wears (his same-day
        # correction: the jewels'/crown's plates, never a white font).
        # The plate library has NO parenthesis today, so the pair joins
        # over the COLON plate — the one typeable separator it owns; a
        # parenthesised form needs two new plates in
        # assets/instrument/letters/symbols/ first.
        self._fast_travel_flash.flash(
            self._widget, icon_path, theme["emoji"],
            f"{self._ui(theme['title'])} : {self._ui(option['title'])}",
        )

    # Every `_compute_jump` kind that LANDS somewhere new (R-30) — the
    # unit/eclipse jumps (`_step_fast_travel`) chain through the SAME
    # `_apply_jump`/`_dialog_jump` tails but never appear here, so they
    # stay silent exactly like before this round.
    _LOCATION_JUMP_KINDS = frozenset({"north_pole", "south_pole", "greenwich", "city"})

    # THE LOCATION'S OWN LOGO (owner order 2026-08-12): the poles wear
    # his two compass roses and Greenwich the plain one Time Travel's
    # own rows already use. An ordinary city names none — there is no
    # per-city art and inventing one would be worse than the clean text
    # the flash shows instead (Rule #1, graceful-absent).
    _LOCATION_FLASH_ICONS = {
        "north_pole": "north_pole",
        "south_pole": "south_pole",
        "greenwich": "compass",
    }

    def _flash_location(
        self, name: str, path: tuple = (), timezone: str = "",
        icon_key: str | None = None,
    ) -> None:
        """R-30/R-31: the "CITY, COUNTRY" flash on every LOCATION change
        — the Settings dialog's preset pick (`_apply_settings_dialog_result`),
        every `_compute_jump` landing named in `_LOCATION_JUMP_KINDS`
        (`_apply_jump`/`_dialog_jump`: Quick Jump cycling, Greenwich, the
        poles, Time Travel's own Quick Jump rows) and Ctrl+Home's return
        to the home city.

        ONE FLASH, ONE PLACE (owner order 2026-08-12): this used to be a
        different-looking flash — big white font letters across the
        middle of the dial. It is now the SAME overlay in the SAME spot
        above the dial as the Ctrl+[ picker, wearing the same letter
        plates, with the place's own logo beside it
        (`_LOCATION_FLASH_ICONS`).

        The SAME `name` also becomes `_active_location_name` (R-31), so
        the tray tooltip/menu TITLE follows it too — one location change,
        one call, both symptoms fixed together."""
        display_text = _location_flash_text(name, path, timezone)
        icon_path = (
            defaults.icon_path(icon_key) if icon_key is not None else None
        )
        self._fast_travel_flash.flash(self._widget, icon_path, "", display_text)
        self._active_location_name = name
        # THE LOCATION CROWN (RING VERDICTS round, owner decree
        # 2026-08-05): the SAME resolved text, kept alongside the name
        # so `build_skin` can draw it — a location change must recompose
        # the skin when the active ring's Location crown is on, exactly
        # like the flash/tray title already follow it.
        self._active_location_display = display_text
        self._refresh_watch_title()
        # THE LOCATION CROWN must FOLLOW the change immediately (owner
        # verdict): rebuild the skin here rather than relying on
        # whatever happens to run next — every `_flash_location` caller
        # (Settings dialog preset pick, Quick Jump, Time Travel,
        # Greenwich, the poles) is a genuine location change, so this is
        # never a redundant rebuild on a non-location tick.
        self._install_skin(build_skin(self._settings, self._active_location_display))

    def _flash_jump_location(self, kind: str, city: dict | None) -> None:
        """The shared tail behind `_apply_jump`/`_dialog_jump`: flashes
        the landed-on place when `kind` actually changed the location
        (`_LOCATION_JUMP_KINDS`), silent for every other jump kind (a
        day/month/year/century/millennium/eclipse step never flashes,
        unchanged from before this round)."""
        if kind not in self._LOCATION_JUMP_KINDS:
            return
        if kind == "north_pole":
            self._flash_location(
                self._ui("North Pole"),
                icon_key=self._LOCATION_FLASH_ICONS["north_pole"],
            )
        elif kind == "south_pole":
            self._flash_location(
                self._ui("South Pole"),
                icon_key=self._LOCATION_FLASH_ICONS["south_pole"],
            )
        elif kind == "greenwich":
            self._flash_location(
                "Greenwich", (), defaults.GREENWICH_TIMEZONE,
                icon_key=self._LOCATION_FLASH_ICONS["greenwich"],
            )
        else:                               # "city" — the user's own place
            self._flash_location(city.name, city.path, city.timezone)

    def _step_fast_travel(self, direction: int) -> None:
        """Ctrl+minus/Ctrl+plus: one step past (`direction=-1`)/future
        (`direction=1`) along the ACTIVE (theme, option) — riding the
        SAME `_compute_jump` kinds Quick Jump uses (owner spec:
        "chaining law — each jump starts from the active simulation",
        `_active_simulation_or_now`). No flash on a step (owner spec
        scopes the flash to the Ctrl+[ / Ctrl+] PICKERS only)."""
        theme = self._fast_travel_theme()
        option = theme["options"][self._fast_travel_option_index(theme["id"])]
        kind = f"{'next' if direction > 0 else 'prev'}_{option['jump_stem']}"
        moment, observer, cycles = self._active_simulation_or_now()
        self._apply_jump(moment, observer, cycles, kind)

    # --- LOCATIONS shortcuts (R5b round, owner spec) -----------------------------

    def _jump_to_place(self, kind: str) -> None:
        """Ctrl+Up/Down/Space: jump the ACTIVE simulation (or, absent
        one, the live now) to `kind` ("north_pole"/"south_pole"/
        "greenwich") — the SAME `_compute_jump` kinds the Time Travel
        dialog's own place buttons use (Rule #5), applied straight to
        the live dial instead of a dialog draft."""
        moment, observer, cycles = self._active_simulation_or_now()
        self._apply_jump(moment, observer, cycles, kind)

    def _cycle_jump_city(self, direction: int) -> None:
        """Ctrl+Left/Right: step through the user's own CUSTOM Quick
        Jump cities (owner spec) — a STRICT no-op with none defined (no
        index change, no jump). `_jump_city_index` names the city THIS
        press lands on (shown first, THEN advanced for the NEXT press)
        — so the very FIRST press, either direction, lands on the
        FIRST custom city (index 0, the natural "nothing chosen yet"
        starting point) and only the SECOND press actually reveals which
        direction was held. Session-only cursor, like the Fast Travel
        theme/option cursors."""
        cities = self._settings.jump_cities
        if not cities:
            return
        count = len(cities)
        city = cities[self._jump_city_index % count]
        self._jump_city_index = (self._jump_city_index + direction) % count
        moment, observer, cycles = self._active_simulation_or_now()
        self._apply_jump(moment, observer, cycles, "city", city)

    def _cycle_slots(self) -> None:
        """Ctrl+N: the number of visible Slots, 0 → 1 → 2 → 3 → 0 (the
        SAME 1 → 2 → 3 chain the menu's own ordinals enforce — cycling
        can only ever pass through legal states)."""
        target = (slot_layout_target(self._settings) + 1) % 4
        self._apply_slot_layout(target)

    def _apply_slot_layout(self, target: int) -> None:
        """The shared body behind `_cycle_slots` (Ctrl+N steps it) and
        `_set_slot_layout` (the Watch Face FACE LAYOUT row picks it
        directly) — ONE place computing the flag triple for a legal
        0-3 target (Rule #5). `_install_skin` refreshes the Slot Theme
        window in place when it happens to be open."""
        self._settings = replace(
            self._settings,
            show_weekday=target >= 1,
            show_octa_slot=target >= 2,
            show_third_slot=target >= 3,
        )
        self._install_skin(build_skin(self._settings, self._active_location_display))
        self._refresh_menu_gating()
        self._flush_position()

    def _set_slot_layout(self, target: int) -> None:
        """R-17: the Watch Face FACE LAYOUT row's direct pick — the
        SAME legal 0-3 states `_cycle_slots` steps through, applied at
        once instead of incrementally."""
        if target == slot_layout_target(self._settings):
            return
        self._apply_slot_layout(target)

    def _toggle_archetype_shortcut(self) -> None:
        """Ctrl+A: the SAME toggle as the menu's own Archetype entry — a
        no-op where it is unavailable (Aurora/Calendar, or the Pointer
        element hidden), never a silent state change."""
        settings = self._settings
        available = settings.show_pointer and archetypes.has_archetype(
            settings.pointer
        )
        if not available:
            return
        self._set_display_choice("archetype_mode", not settings.archetype_mode)
        # The menu's OWN checkable Archetype action is a SEPARATE view
        # of the same state (the shortcut bypasses its `toggled` signal
        # entirely) — mirror it without re-entering the handler: block
        # signals, set, unblock.
        self._archetype_action.blockSignals(True)
        self._archetype_action.setChecked(self._settings.archetype_mode)
        self._archetype_action.blockSignals(False)
