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
        # WATCH FACE round (Phase ①+②, R-01): F="Face" — Ctrl+W was the
        # owner's first-named candidate but is already
        # `cycle_weekday_theme`'s (this table is checked for the
        # collision, never assumed free).
        "open_watch_face", "Key_F", ("ControlModifier",), "Open Watch Face",
    ),
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
        # The six categories of the owner's 2026-08-11 list — the old
        # three-name parenthesis outlived its own table by a round.
        "Cycle the Fast Travel category (eclipses, turning points, "
        "date, time)",
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
# THE SIX CATEGORIES (owner spec 2026-08-11, verbatim list: sun
# eclipse / moon eclipse / turning points sun / turning points moon /
# date / day(hour,min,sec) — with "osmisli bolje nazive"): each
# eclipse category offers ANY plus every catalog type IN TURN ("sve
# verzije ili svaka redom"), which also retires the old absurdity of
# a solar eclipse living as an option under Moon phases ("kako bre
# eklipsa sunca da dobija termin po mesecu"). The flash text is
# "Category (Option)" — `WatchController._flash_fast_travel`.
# THE OWNER'S OWN SIX ICONS (his order 2026-08-12, verbatim list): the
# picker wears HIS art, not the app's generic chrome — `sun_eclipse.png`
# and `moon_eclipse_red.png` for the two eclipse categories (RED always:
# his ballot verdict G1, the blood-moon tone the dial itself paints at
# totality), `sun.svg` and `moon.svg` for the two turning-point
# categories. Date and Time own no file and are COMPUTED instead (Rule
# #19, never commission art for a plain glyph): `computed_icon` names the
# drawing, resolved by `WatchController._flash_fast_travel` through
# `render.asset_variants`. Their old 📅/🕐 emoji stay as the documented
# absent-file fallback and nothing else.
FAST_TRAVEL_THEMES = (
    {
        "id": "solar_eclipse", "title": "Solar Eclipse",
        "icon_key": "sun_eclipse", "emoji": "🌑",
        "options": (
            {"id": "any", "title": "Any", "jump_stem": "solar_eclipse"},
            {"id": "total", "title": "Total", "jump_stem": "solar_eclipse_total"},
            {
                "id": "annular", "title": "Annular",
                "jump_stem": "solar_eclipse_annular",
            },
            {
                "id": "partial", "title": "Partial",
                "jump_stem": "solar_eclipse_partial",
            },
            {
                "id": "hybrid", "title": "Hybrid",
                "jump_stem": "solar_eclipse_hybrid",
            },
        ),
    },
    {
        "id": "lunar_eclipse", "title": "Lunar Eclipse",
        "icon_key": "moon_eclipse_red", "emoji": "🌘",
        "options": (
            {"id": "any", "title": "Any", "jump_stem": "lunar_eclipse"},
            {"id": "total", "title": "Total", "jump_stem": "lunar_eclipse_total"},
            {
                "id": "partial", "title": "Partial",
                "jump_stem": "lunar_eclipse_partial",
            },
            {
                "id": "penumbral", "title": "Penumbral",
                "jump_stem": "lunar_eclipse_penumbral",
            },
        ),
    },
    {
        "id": "sun", "title": "Sun Turning Points",
        "icon_key": "sun", "emoji": "☀️",
        "options": (
            {"id": "any", "title": "Any", "jump_stem": "sun"},
            {
                "id": "solstice", "title": "Solstices",
                "jump_stem": "sun_solstice",
            },
            {
                "id": "equinox", "title": "Equinoxes",
                "jump_stem": "sun_equinox",
            },
        ),
    },
    {
        "id": "moon", "title": "Moon Stations",
        "icon_key": "moon", "emoji": "🌙",
        "options": (
            {"id": "any", "title": "Any", "jump_stem": "moon"},
            {"id": "full", "title": "Full", "jump_stem": "moon_full"},
            {"id": "new", "title": "New", "jump_stem": "moon_new"},
            {"id": "quarter", "title": "Quarters", "jump_stem": "moon_quarter"},
        ),
    },
    {
        "id": "calendar", "title": "Date", "icon_key": None,
        "computed_icon": "calendar_sheet", "emoji": "📅",
        "options": (
            {"id": "day", "title": "Day", "jump_stem": "day"},
            {"id": "month", "title": "Month", "jump_stem": "month"},
            {"id": "year", "title": "Year", "jump_stem": "year"},
            {"id": "century", "title": "Century", "jump_stem": "century"},
            {"id": "millennium", "title": "Millennium", "jump_stem": "millennium"},
        ),
    },
    {
        "id": "clock", "title": "Time", "icon_key": None,
        "computed_icon": "clock_face", "emoji": "🕐",
        "options": (
            {"id": "hour", "title": "Hour", "jump_stem": "hour"},
            {"id": "minute", "title": "Minute", "jump_stem": "minute"},
            {"id": "second", "title": "Second", "jump_stem": "second"},
        ),
    },
)

# --- Fast Travel FLASH (R5b round, owner spec) --------------------------------
# The small transient overlay ([Fast Travel Flash](../app/fast_travel_flash.md))
# flashed above the dial on every Ctrl+[ / Ctrl+] theme/option change —
# icon + option text, auto-fading, falling BELOW the dial instead when
# the dial hugs the screen top. R-30 (2026-08) reuses the SAME overlay,
# `big=True`, for a LOCATION change (Settings preset pick, Quick Jump,
# Time Travel city change): large centered "CITY, COUNTRY" text across
# the middle of the dial instead of the small icon+text popup above it.
FAST_TRAVEL_FLASH_DURATION_S = 1.2   # total time on screen (hold + fade)
FAST_TRAVEL_FLASH_FADE_MS = 250      # the trailing fade-out's own span
FAST_TRAVEL_FLASH_GAP_PX = 12        # gap between the flash and the dial edge
FAST_TRAVEL_FLASH_ICON_PX = 28
FAST_TRAVEL_FLASH_FONT_PX = 15
FAST_TRAVEL_FLASH_PADDING_PX = 10
FAST_TRAVEL_FLASH_RADIUS_PX = 10
LOCATION_FLASH_FONT_PX = 32           # R-30: large letters, dial-center flash

# THE TWO COMPUTED ICONS (ECLIPSE ICON WIRING round, owner 2026-07-20/
# 21 — "ADD a computed calendar icon... so the emoji fallback dies";
# extended 2026-08-12 to the clock face, his ballot options I1+H1).
# Date and Time are the two FAST_TRAVEL_THEMES entries with no art
# file of their own — Rule #19, COMPUTE rather than commission art
# for a plain glyph. `render.asset_variants.calendar_sheet_icon_file`
# and `clock_face_icon_file` draw them, both in the app's own gold
# ramp (the SAME two sampled steps the ADAPTIVE GOLD/BRONZE round
# reads off `UV/DESIGN/gold pallete.png` — Rule #5, one palette,
# reused) with a thin dark ink for contrast against the flash's own
# dark background.
CALENDAR_ICON_RING_WIDTH_FRACTION = 0.06   # of the icon radius
# THE CALENDAR SHEET (owner ballot verdict 2026-08-12, option I1 — the
# 12-wedge wheel is RETIRED, Rule #6: "it reads as an abstract pie, not
# as a date"). A real sheet instead: a bound page with a darker header
# band, a grid of day cells and ONE cell lit in the bright gold step, so
# the glyph says "a day inside a month" at 28 px. All fractions are of
# the icon's own size, so the drawing scales with whatever the flash asks
# for.
CALENDAR_SHEET_MARGIN_FRACTION = 0.10       # blank edge around the page
CALENDAR_SHEET_HEADER_FRACTION = 0.26       # header band, of the page height
CALENDAR_SHEET_RING_COUNT = 2               # binding rings above the header
CALENDAR_SHEET_COLUMNS = 4                  # day cells across
CALENDAR_SHEET_ROWS = 3                     # rows of day cells
CALENDAR_SHEET_LIT_CELL = (2, 1)            # (column, row) of today's cell
# THE 24 h CLOCK FACE (owner ballot verdict 2026-08-12, option H1): there
# is no clock file in assets/instrument/icons/, so the Time category's
# glyph is COMPUTED like the calendar's (Rule #19). It is deliberately a
# TWENTY-FOUR hour face with the hand up at noon — this watch's own
# convention (DIAL_OFFSET_DEG, 12:00 top / 00:00 bottom), never a generic
# 12 h clip-art clock that would teach the wrong dial.
CLOCK_ICON_RIM_WIDTH_FRACTION = 0.09        # of the icon radius
CLOCK_ICON_TICK_COUNT = 24                  # one per hour of THIS dial
CLOCK_ICON_MAJOR_EVERY = 6                  # 12/18/00/06 stand out
CLOCK_ICON_TICK_LENGTH_FRACTION = 0.16      # minor tick, of the radius
CLOCK_ICON_MAJOR_LENGTH_FRACTION = 0.26
CLOCK_ICON_HAND_LENGTH_FRACTION = 0.56      # hour hand, of the radius
CLOCK_ICON_HAND_WIDTH_FRACTION = 0.11
CLOCK_ICON_HAND_ANGLE_DEG = 0.0             # noon: straight up, the top


# Time Travel (scenario tester in the menu): the dial renders the entered
# moment/position for this long, then returns to the present by itself.
TIME_TRAVEL_DURATION_S = 60
DEEP_TIME_YEAR_RANGE = (-13000, 17000)   # the coming pack's advertised span
