"""Keyboard input and the fast-travel it drives — the shortcut
table, Fast Travel's theme/option jumps and the transient Flash
overlay that announces them.

Layer: config — pure, no Qt, no wall clock.
"""

# --- Keyboard shortcuts (R5 MENU REWORK, owner "OSMISLITI ŠTA SVE" —
# design the whole map; R5b FINAL MAP round, owner spec sealed
# 2026-07-21, extends and partly REPLACES the R5 draft — Rule #6, no
# leftovers) -------------------------------------------------------------
# ONE table, pinned by tests/test_shortcuts.py, rendered into each menu
# entry's shortcut column too (`app.controller._build_menu`). Every
# shortcut needs the dial to hold KEYBOARD FOCUS — wired through the
# EXISTING focused `ClockWidget.keyPressEvent` path (owner constraint:
# no new global OS-level hook this round beyond the existing SPACE
# hook; a click on the dial already gives it focus, `ClickFocus`).
# Every combo carries a MODIFIER on purpose: a bare letter would
# collide with the HIDDEN_MODE_SECRET typed-sequence buffer, which
# only ever sees PRINTABLE NO-MODIFIER text — a held modifier routes
# the key event around that buffer entirely by construction (see
# `app.widget.ClockWidget.keyPressEvent`), so no combo here can ever
# feed it. `key` is a `Qt.Key` enum NAME and `modifiers` a tuple of
# `Qt.KeyboardModifier` enum NAMES (config stays Qt-free — the SAME
# convention `HOVER_BYPASS_MODIFIER` above already uses); `app.widget`
# resolves both once at import time. An action_id may appear TWICE
# (`fast_travel_future`, below) when the owner wants two physical combos
# to fire the SAME action — `app.widget` already loops the whole table,
# so a second row needs no special casing there.
#
# Chosen mnemonics: R=Ring, W=Weekday, N=Number of slots, E=Encyclopedia,
# G=Guide, M=Menu/Settings (Ctrl+, DIED this round — R5b sealed map,
# freeing the comma; M is the mnemonic that survives every layout),
# O=Observatory, T=Time Travel, A=Archetype; Ctrl+Home ("go home") is
# the FULL reset now — now AND the home location, replacing R5's
# time-only return (R5b, Rule #6: the old time-only meaning is gone, not
# kept alongside). 1/2/3 = the three Slots (bare = Complication,
# +Alt = Weekday theme); [ ] = step the Fast Travel THEME/OPTION picker
# (bracket keys read left-to-right as "theme, then its option", the
# SAME visual order the picker itself is read in); minus/plus = step a
# Fast Travel jump back/forward in time (the universal past/future
# sense); arrows = the four LOCATIONS compass directions (Up/Down poles,
# Left/Right custom cities) plus Space for Greenwich (a bare tap "there
# and back", already free — SPACE's own unmodified Encyclopedia jump
# only fires with NO modifier, see `app.widget.ClockWidget.keyPressEvent`).
# A z-mode shortcut was CONSIDERED and DROPPED (Ctrl+Z carries a strong
# pre-existing "Undo" expectation this app has no Undo to honor — better
# no binding than a confusing one).
SHORTCUTS = (
    # (action_id, key name, modifier names, description)
    (
        "cycle_ring", "Key_R", ("ControlModifier",),
        "Cycle to the next Ring preset",
    ),
    (
        "cycle_weekday_theme", "Key_W", ("ControlModifier",),
        "Cycle to the next Weekday theme (only while it is displayed "
        "on the diamonds)",
    ),
    (
        "cycle_slots", "Key_N", ("ControlModifier",),
        "Cycle the number of visible Slots (0→1→2→3→0)",
    ),
    (
        "open_encyclopedia", "Key_E", ("ControlModifier",),
        "Open the Encyclopedia",
    ),
    ("open_guide", "Key_G", ("ControlModifier",), "Open the Guide"),
    ("open_settings", "Key_M", ("ControlModifier",), "Open Settings"),
    (
        "open_observatory", "Key_O", ("ControlModifier",),
        "Open the Observatory",
    ),
    (
        "open_time_travel", "Key_T", ("ControlModifier",),
        "Open Time Travel",
    ),
    (
        "return_to_now", "Key_Home", ("ControlModifier",),
        "End the running simulation — the full reset: now, at the "
        "home location",
    ),
    (
        "toggle_archetype", "Key_A", ("ControlModifier",),
        "Toggle Archetype mode",
    ),
    # SLOTS (R5b round): the COMPLICATION cycle (Digital Time -> Date ->
    # Day length -> Seconds, `SLOT_COMPLICATION_TITLES`'s own order) and
    # the WEEKDAY THEME cycle, once per slot — both strict no-ops while
    # their own slot is not active/visible (`WatchController._slot_active`).
    (
        "cycle_slot1_complication", "Key_1", ("ControlModifier",),
        "Cycle the 1st Slot's Complication",
    ),
    (
        "cycle_slot2_complication", "Key_2", ("ControlModifier",),
        "Cycle the 2nd Slot's Complication",
    ),
    (
        "cycle_slot3_complication", "Key_3", ("ControlModifier",),
        "Cycle the 3rd Slot's Complication",
    ),
    (
        "cycle_slot1_theme", "Key_1", ("ControlModifier", "AltModifier"),
        "Cycle the 1st Slot's Weekday theme",
    ),
    (
        "cycle_slot2_theme", "Key_2", ("ControlModifier", "AltModifier"),
        "Cycle the 2nd Slot's Weekday theme",
    ),
    (
        "cycle_slot3_theme", "Key_3", ("ControlModifier", "AltModifier"),
        "Cycle the 3rd Slot's Weekday theme",
    ),
    # FAST TRAVEL (R5b round): the theme/option pickers flash the theme's
    # logo (`app.fast_travel_flash.FastTravelFlash`); the past/future
    # step rides the SAME `_compute_jump` machinery Quick Jump uses,
    # chained from the ACTIVE simulation. Ctrl+plus is bound to BOTH the
    # main-row "=" key (no Shift needed) and the numpad "+" (owner:
    # "Ctrl++ needs Shift on most layouts" — `app.widget` masks out
    # `KeypadModifier` before matching, so the numpad's OWN modifier
    # flag never blocks the match).
    (
        "fast_travel_theme", "Key_BracketLeft", ("ControlModifier",),
        "Cycle the Fast Travel theme (Sun / Moon / Calendar)",
    ),
    (
        "fast_travel_option", "Key_BracketRight", ("ControlModifier",),
        "Cycle the option within the active Fast Travel theme",
    ),
    (
        "fast_travel_past", "Key_Minus", ("ControlModifier",),
        "Fast Travel one step into the past",
    ),
    (
        "fast_travel_future", "Key_Equal", ("ControlModifier",),
        "Fast Travel one step into the future",
    ),
    (
        "fast_travel_future", "Key_Plus", ("ControlModifier",),
        "Fast Travel one step into the future (numpad +)",
    ),
    # LOCATIONS (R5b round): the poles and Greenwich ride `_compute_jump`
    # kinds that never clamp; the custom-city cycle is a strict no-op
    # with none defined (`WatchController._cycle_jump_city`).
    (
        "location_north_pole", "Key_Up", ("ControlModifier",),
        "Travel to the North Pole",
    ),
    (
        "location_south_pole", "Key_Down", ("ControlModifier",),
        "Travel to the South Pole",
    ),
    (
        # MOVED off Ctrl+Space 2026-07-27 (CUBE.md §Display laws, THE
        # ARTICLE-DEPTH LAW): Space and its modifiers now belong wholly
        # to the article jump — SPACE primary, Shift+SPACE secondary,
        # Ctrl+SPACE tertiary. Greenwich takes the ZERO meridian's own
        # digit (Ctrl+G was already the Guide — caught by
        # `test_no_two_shortcuts_share_a_chord`, which exists BECAUSE
        # this move first collided there).
        "location_greenwich", "Key_0", ("ControlModifier",),
        "Travel to Greenwich",
    ),
    (
        "location_prev_city", "Key_Left", ("ControlModifier",),
        "Cycle to the previous custom Quick Jump city",
    ),
    (
        "location_next_city", "Key_Right", ("ControlModifier",),
        "Cycle to the next custom Quick Jump city",
    ),
)
_SHORTCUT_MODIFIER_DISPLAY = {"ControlModifier": "Ctrl", "AltModifier": "Alt"}
# Symbol/special keys whose Qt enum NAME does not read as its own
# display glyph (everything else strips the "Key_" prefix verbatim —
# "Key_R" -> "R", "Key_Up" -> "Up").
_SHORTCUT_KEY_DISPLAY_OVERRIDES = {
    "Key_Home": "Home",
    "Key_BracketLeft": "[",
    "Key_BracketRight": "]",
    "Key_Minus": "-",
    "Key_Equal": "=",
    "Key_Plus": "+",
}


def shortcut_display(action_id: str) -> str:
    """The combo's human-readable label ("Ctrl+R") for the menu's
    shortcut column — Qt-free, resolved from `SHORTCUTS` alone."""
    for entry_id, key, modifiers, _description in SHORTCUTS:
        if entry_id == action_id:
            key_label = _SHORTCUT_KEY_DISPLAY_OVERRIDES.get(
                key, key.removeprefix("Key_")
            )
            mod_label = "+".join(
                _SHORTCUT_MODIFIER_DISPLAY[modifier] for modifier in modifiers
            )
            return f"{mod_label}+{key_label}"
    raise KeyError(action_id)


# --- Fast Travel (R5b round, owner spec sealed 2026-07-21) -------------------
# Ctrl+[ cycles the THEME, Ctrl+] the OPTION inside it (`WatchController.
# _cycle_fast_travel_theme`/`_cycle_fast_travel_option`); Ctrl+minus/plus
# step the ACTIVE (theme, option) one unit past/future, riding the SAME
# `_compute_jump` kinds Quick Jump already uses (Rule #5) — every
# option's `jump_stem` is what `_compute_jump` sees as
# f"next_{stem}"/f"prev_{stem}". ONE table (owner: a config table he
# will keep tuning) — `icon_key` reuses an EXISTING `ICON_FILES` entry
# (UI chrome may legitimately answer more than one spot, unlike the
# dial's own one-image-one-place ART); a theme with no dedicated file
# yet (Calendar — nothing "calendar-ish" has landed in assets/icons/)
# falls back to its own documented `emoji` (Rule #1, the SAME
# graceful-absent contract `icon_path()` already guarantees).
FAST_TRAVEL_THEMES = (
    {
        "id": "sun", "title": "Sun", "icon_key": "eclipse_sun", "emoji": "☀️",
        "options": (
            {"id": "any", "title": "Any turning point", "jump_stem": "sun"},
            {
                "id": "solstice", "title": "Solstices only",
                "jump_stem": "sun_solstice",
            },
            {
                "id": "equinox", "title": "Equinoxes only",
                "jump_stem": "sun_equinox",
            },
        ),
    },
    {
        "id": "moon", "title": "Moon", "icon_key": "eclipse_moon", "emoji": "🌙",
        "options": (
            {"id": "full", "title": "Full", "jump_stem": "moon_full"},
            {"id": "new", "title": "New", "jump_stem": "moon_new"},
            {"id": "quarter", "title": "Quarters", "jump_stem": "moon_quarter"},
            # The lunar catalog specifically (paired thematically with
            # the Moon; the Sun theme carries no eclipse option of its
            # own) — the SAME kind `_ECLIPSE_JUMPS` already serves.
            {"id": "eclipse", "title": "Eclipse", "jump_stem": "lunar_eclipse"},
        ),
    },
    {
        "id": "calendar", "title": "Calendar", "icon_key": None, "emoji": "📅",
        "options": (
            {"id": "day", "title": "Day", "jump_stem": "day"},
            {"id": "month", "title": "Month", "jump_stem": "month"},
            {"id": "year", "title": "Year", "jump_stem": "year"},
            {"id": "century", "title": "Century", "jump_stem": "century"},
            {"id": "millennium", "title": "Millennium", "jump_stem": "millennium"},
        ),
    },
)

# --- Fast Travel FLASH (R5b round, owner spec) --------------------------------
# The small transient overlay ([Fast Travel Flash](../app/fast_travel_flash.md))
# flashed above the dial on every Ctrl+[ / Ctrl+] theme/option change —
# icon + option text, auto-fading, falling BELOW the dial instead when
# the dial hugs the screen top.
FAST_TRAVEL_FLASH_DURATION_S = 1.2   # total time on screen (hold + fade)
FAST_TRAVEL_FLASH_FADE_MS = 250      # the trailing fade-out's own span
FAST_TRAVEL_FLASH_GAP_PX = 12        # gap between the flash and the dial edge
FAST_TRAVEL_FLASH_ICON_PX = 28
FAST_TRAVEL_FLASH_FONT_PX = 15
FAST_TRAVEL_FLASH_PADDING_PX = 10
FAST_TRAVEL_FLASH_RADIUS_PX = 10

# THE CALENDAR WHEEL ICON (ECLIPSE ICON WIRING round, owner 2026-07-20/
# 21 — "ADD a computed calendar icon... so the 📅 fallback dies"): the
# Calendar Fast Travel theme is the one FAST_TRAVEL_THEMES entry with
# no dedicated art file (Sun/Moon keep their eclipse glyphs, untouched
# this round) — Rule #19, COMPUTE rather than commission a 12th art
# file for a plain wheel mark. `render.asset_variants.calendar_wheel_icon_file`
# draws it: 12 alternating wedges in the app's own gold ramp (the SAME
# two sampled steps the ADAPTIVE GOLD/BRONZE round reads off
# `UV/DESIGN/gold pallete.png` — Rule #5, one palette, reused) with a
# thin dark ring for contrast against the flash's own dark background.
CALENDAR_ICON_WEDGE_COUNT = 12
CALENDAR_ICON_RING_WIDTH_FRACTION = 0.06   # of the icon radius


# Time Travel (scenario tester in the menu): the dial renders the entered
# moment/position for this long, then returns to the present by itself.
TIME_TRAVEL_DURATION_S = 60
DEEP_TIME_YEAR_RANGE = (-13000, 17000)   # the coming pack's advertised span
