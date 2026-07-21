"""Developer tunables — values a developer may adjust while tuning the app.

Everything here is read-only at runtime. User-changeable state (window
position, chosen city, chosen skin) lives in the user settings file owned
by app/settings_store.py.
"""

import re
from datetime import date
from pathlib import Path

from config import paths
from skins.manifest import (
    BackgroundSpec,
    HandSpec,
    HandsSpec,
    RingSpec,
    SkinDefinition,
    StarSpec,
    WeekdaySpec,
    YearMarkerSpec,
)

# --- Window ------------------------------------------------------------------
DEFAULT_DIAL_DIAMETER = 720          # logical px, before DPI scaling
                                     # (owner install-default list 2026-07-12)
MIN_DIAL_DIAMETER = 120
MAX_DIAL_DIAMETER = 2000             # roomy above the largest preset (1440)
SIZE_PRESETS = (360, 540, 720, 1080, 1440)   # owner spec (FINAL.txt #3)
# The compact SIZE slider living in the right-click menu itself (owner
# ROADMAP 15h item 12): coarse is fine — fine tuning stays in Settings —
# so a wide step and a narrow on-screen width are deliberate; it applies
# ONLY on release (never mid-drag).
MENU_SIZE_SLIDER_STEP = 10
MENU_SIZE_SLIDER_WIDTH_PX = 130

# Dials at or above this diameter write the date on the Earth marker;
# the FULL weekday name needs more room and appears only from the largest
# preset (owner: at 540 the full name is too small — keep the short one).
# Below the full-name threshold the markers get hover tooltips instead.
FULL_TEXT_MIN_DIAMETER = 540
WEEKDAY_FULL_NAME_MIN_DIAMETER = 720
EARTH_DATE_TEXT_SIZE = 0.30          # fraction of the marker size

# White label text carries a black outline so it stays readable over
# bright bodies (owner spec — "WED" on Mercury washed out without it).
LABEL_FILL_RGBA = (255, 255, 255, 240)
LABEL_OUTLINE_RGBA = (0, 0, 0, 210)
LABEL_OUTLINE_WIDTH = 0.05           # fraction of the font pixel size

# Watchdog delay for undoing a spontaneous (OS-initiated) hide/minimize.
# NOTE, verified on Windows 11 24H2: Win+D does NOT hide or minimize this
# window (no Qt events arrive) — it raises the desktop layer above every
# window (even TOPMOST cannot pierce it), and the widget returns by itself
# the moment Show Desktop mode ends. The watchdog therefore only covers
# other shell actions that genuinely hide/minimize; true visibility DURING
# Show Desktop requires the WorkerW glue mode (optional, M4).
WATCHDOG_RESHOW_MS = 200

# --- Location (until the picker arrives in M6) --------------------------------
# Owner-approved preset; values taken verbatim from world_locations.json.
DEFAULT_CITY = {
    "name": "Belgrade",
    "latitude": 44.82,
    "longitude": 20.46,
    "timezone": "Europe/Belgrade",
}

# --- Tick scheduling -----------------------------------------------------------
TICK_EPSILON_MS = 50                 # fire just past the minute/second boundary
CLOCK_JUMP_THRESHOLD_S = 5           # actual vs expected tick time -> full refresh

# True click-through: the window takes NO mouse input (recovery via the
# tray only). Hover info survives through a cursor poller that shows the
# tooltips itself at this interval.
CLICK_THROUGH_HOVER_POLL_MS = 200

# Holding this key SILENCES the hover system while the cursor travels
# (owner 2026-07-16): near the screen edge a large neighbour legend —
# e.g. the hexa zodiac diamond's — covers the smaller weekday body, so
# the target could never be reached; hold, glide past, release inside
# the wanted element. A Qt.KeyboardModifier NAME (config stays
# Qt-free); the widget resolves it.
HOVER_BYPASS_MODIFIER = "ControlModifier"

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
        "location_greenwich", "Key_Space", ("ControlModifier",),
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
FAST_TRAVEL_FLASH_BG = "rgba(20, 20, 26, 220)"
FAST_TRAVEL_FLASH_TEXT_COLOR = "#F0F0F0"


# Time Travel (scenario tester in the menu): the dial renders the entered
# moment/position for this long, then returns to the present by itself.
TIME_TRAVEL_DURATION_S = 60
# A target outside the bundled coverage is refused inline (owner
# 2026-07-16). The warning names the future Deep Time pack's reach; the
# actual coverage comes from the databases (SeasonsRepository/
# MoonPhaseRepository .coverage()), never hardcoded.
TIME_TRAVEL_WARNING_COLOR = "#C8553D"    # warm red-clay — reads on the dialog
DEEP_TIME_YEAR_RANGE = (-13000, 17000)   # the coming pack's advertised span

# --- Settings persistence ----------------------------------------------------
SETTINGS_SCHEMA_VERSION = 1
SETTINGS_WRITE_DEBOUNCE_MS = 750     # collapse rapid moveEvent bursts while dragging

# --- Procedural FALLBACK geometry (fractions of the dial radius unless noted) --
# NOT legacy: these drive the painter-drawn ring/labels used whenever a
# skin ships no ring art (user drop-in skins, validate previews). The DOMY
# skin itself uses ring.png, so these do not affect it.
RING_TICK_WIDTH = 0.004
RING_TICK_REACH = 1.03               # tick end, fraction of the ring inner radius
RING_NUMERAL_SIZE = 0.085            # font pixel size
RING_LETTER_SIZE = 0.105
RING_TEXT_BOX = 0.16                 # square text-layout box
RING_MINUTE_SIZE = 0.05
RING_MINUTE_RADIUS = 0.92            # fraction of the ring inner radius
RING_NUMERAL_MIN_PX = 7              # legibility floors at tiny dial sizes
RING_LETTER_MIN_PX = 8
RING_MINUTE_MIN_PX = 6
BODY_LABEL_MIN_PX = 6

# ONE on-dial NAME-label cap, shared by the weekday bodies AND the
# archetype figures (owner ROADMAP 15h item 4b, 2026-07-18): both paths
# fit text to the available width (measured, never guessed) — without a
# ceiling a SHORT name (e.g. "TUE") inflates far past a LONG one (e.g.
# "Wednesday") at the same spot. Reasoned from the current 720-dial
# short-weekday "TUE" look (~40 px at the default skin) — a flat pixel
# ceiling on purpose, symmetric with BODY_LABEL_MIN_PX's flat floor
# above, not a fraction of the dial (a giant dial must not grow giant
# single-word labels either). The two-line WRAP the owner asked for on
# 2026-07-18 was REVOKED the same day (Session 21-C, his slika: a huge
# "Youth" beside a tiny "Childhood" reads ugly) — replaced by the
# SET-UNIFORM law: every name sharing a ring wears the size of the
# SMALLEST fitted member (`render.layers.weekday_label_set_px` /
# `archetype_label_set_px`), so no per-line offset constant is needed.
NAME_LABEL_MAX_PX = 40
NAME_LABEL_WIDTH_FRACTION = 0.92     # of the available width (arm/body)
MARKER_BORDER_WIDTH = 0.05           # fraction of the marker size
MARKER_BORDER_RGBA = (255, 255, 255, 200)

# --- Moon/Earth rim transit (year marker, "both" mode) -------------------------
# The smaller Moon passes OVER the Earth at reduced opacity when they meet
# on the shared rim — like an eclipse (owner decision; both stay visible).
MOON_TRANSIT_OPACITY = 0.5

# --- Tray / app presentation ---------------------------------------------------
# The owner's gold watch (logo.svg) is the app face: tray icon now, EXE
# icon and installer art in M7; logo-setup.svg is the rose-gold variant.
TRAY_ICON_SIZE = 64                  # px of the rasterized tray pixmap
LOGO_ASSET = paths.assets_dir() / "logo.svg"
LOGO_SETUP_ASSET = paths.assets_dir() / "logo-setup.svg"
# The app-wide WINDOW icon (title bar, Alt-Tab, taskbar button) needs
# several resolutions in ONE QIcon — Windows picks whichever matches the
# context instead of blurrily scaling a single size (owner screenshot
# 2026-07-20: dialogs showed python's own logo in the taskbar). Mirrors
# the documented EXE-icon ladder (root CLAUDE.md Build Pipeline).
WINDOW_ICON_SIZES_PX = (16, 24, 32, 48, 64, 128, 256)

# TRAY ICON COLOR WHEEL (ADD WATCH round, owner INSTRUCTION.txt item 2B,
# sealed 2026-07-21): watch 1 keeps the gold master untouched, watch 2
# wears the pre-existing rose-gold master (LOGO_SETUP_ASSET, a second
# master — not a recolor); watch 3+ tint the GOLD master (the same
# tritone recipe `render.assets.tinted_pixmap` already uses for ring/
# hand recolors, Rule #5) cycling this wheel forever. The 12 hues are
# the CALENDAR pointer's own MONTH wheel (`UV/Color Wheels.png`,
# January..December) read starting at January — the owner's own worked
# example, PURPLE #8000FF (R:G:B 1:0:2) then BLUE #0000FF (R:G:B 0:0:1),
# identifies the wheel and the starting point at once (Rule #19 —
# computed from the one wheel already in the codebase, no new palette).
TRAY_COLOR_WHEEL = (
    "#8000FF", "#0000FF", "#0080FF", "#00FFFF", "#00FF80", "#00FF00",
    "#80FF00", "#FFFF00", "#FFBF00", "#FF0000", "#FF0080", "#FF00FF",
)

# --- UI icon chrome (TASK 4, MASON/ICONS round, owner icon list
# 2026-07-19 approvals) -------------------------------------------------
# Reusable UI GLYPHS — menu rows, hover badges — copied from the owner's
# UV/icons/ staging folder (his approved four) with canonical names.
# Distinct from the dial's own ART: the one-image-one-place law
# (owner 2026-07-19) applies to ART, never to UI chrome — the SAME icon
# file may legitimately answer in more than one menu spot. Every
# consumer reads through `icon_path(name)`, which is None when the
# file has not landed (a partial install) — the documented fallback is
# the spot's own PRE-EXISTING emoji, never a broken/blank icon
# (Rule #1).
ICON_DIR = paths.assets_dir() / "icons"
ICON_FILES = {
    "light": ICON_DIR / "light.png",           # Quick Jump pole row: polar DAY
    "dark": ICON_DIR / "dark.svg",              # Quick Jump pole row: polar NIGHT
    "eclipse_sun": ICON_DIR / "eclipse_sun.svg",    # Quick Jump Sun's own eclipse entries
    "eclipse_moon": ICON_DIR / "eclipse_moon.png",  # Quick Jump Moon's own eclipse entries
    # R5 MENU REWORK (Time Travel mini-window rows, item 3A): the
    # owner's dedicated per-row icons — a tinted compass rose per pole
    # (navy = North, red = South) and a plain one for Greenwich (the
    # Prime Meridian, a compass reference point rather than a pole or
    # a sun/moon event). Same graceful-absent contract as the pair
    # above: `icon_path` returns None until the file lands, and every
    # row keeps its documented emoji fallback (❄/🌐) either way.
    "north_pole": ICON_DIR / "north_pole.png",
    "south_pole": ICON_DIR / "south_pole.png",
    "compass": ICON_DIR / "compass.png",
}


def icon_path(name: str) -> Path | None:
    """The UI icon file for `name` (a key of `ICON_FILES`), or None when
    it has not landed on disk yet — graceful-absent (Rule #1), so every
    caller keeps drawing its documented emoji fallback instead of a
    broken icon."""
    path = ICON_FILES[name]
    return path if path.exists() else None

# --- Ring faces -------------------------------------------------------------------
# Ring PRESETS are data now (Database/ring_presets.json + the user's
# custom cards in settings, loaded by data/rings.py — owner spec): a
# card is {name, positions, letters}; its positions signature picks the
# LAYOUT (constants.RING_LAYOUTS) whose FACE file lives here.
RING_FACE_DIR = paths.assets_dir() / "ring"

# --- Ring tint (owner spec, FINAL.txt #6) ------------------------------------------
# One hue recolors the WHOLE clock body: the ring art, the hands and
# the Umbra are channel-multiplied by it (gray stays gray under None).
# The letters are separate art and are never tinted. Preset hues below
# are STARTING VALUES — the owner tunes them here. Settings shows them
# as a grid of color circles (Paint style — owner spec 2026-07-11);
# the name appears in the circle's hover tooltip.
# The swatches split into TWO groupings (owner 2026-07-15: "podeli na
# svetlije i tamnije" — the whole palette read too light), each its own
# labeled grid. The Darker group grew a fashion row (owner: subtle,
# understated, "gospodske" hues — navy/teget, petrol, graphite and the
# silver-leaning darks).
RING_TINT_GROUPS = {
    "Lighter": {
        "Gray": None,                   # the untouched owner art
        # The owner's gold palette (his reference swatches, 2026-07-11).
        "Naples Yellow": "#FFE169",
        "Sunglow": "#FFD235",
        "Mikado Yellow": "#FFC300",
        "Gold": "#D4AF37",
        "Satin Gold": "#C9980B",
        "Copper": "#B87333",
        "Silver": "#C9CDD3",
        "Lavender Gray": "#A7A6BA",
        "Periwinkle": "#9090C0",
        "Cadet Gray": "#91A3B0",
        "Stone": "#928E85",
        "Aluminium": "#888B8D",
        "Roman Silver": "#808992",
        "Glaucous": "#6082B6",
        "Slate Gray": "#708090",
        "Smoke": "#738276",
        "Steel": "#71797E",
    },
    "Darker": {
        # Pipetted from the owner's Clock_OuterColors.png (21 ring
        # variants, 3x7 grid, mode color per hour band — 2026-07-11).
        "Nevada": "#6C7174",
        "Dim Gray": "#6B6B6B",
        "Granite": "#625D5D",
        "Pewter": "#565B5F",
        "Ebony": "#545851",
        "Anthracite": "#494F55",
        "Iron": "#4C4E52",
        "Graphite": "#3B3F44",
        "Gunmetal": "#2A3439",
        "Charcoal": "#36454F",
        "Black Coral": "#54626F",
        # The fashion darks (owner 2026-07-15): muted wardrobe hues.
        "Ocean": "#4E7A9E",
        "Petrol": "#2F4550",
        "Navy": "#1B2A41",
        "Oxford Blue": "#14213D",
        "Sage Steel": "#5E716A",
        "Dark Olive": "#3C3F33",
        "Deep Pine": "#253529",
        "Smoky Plum": "#66606D",
        "Aubergine": "#3D3242",
        "Bordeaux": "#4E3238",
        "Purple": "#8E55B9",
        "Golden Brown": "#926C15",
        "Espresso": "#342523",
    },
}
RING_TINT_SWATCH_PX = 22             # diameter of one tint circle
RING_TINT_SWATCHES_PER_ROW = 11
PALETTE_SWATCH_PX = 34               # pointer palette circles (owner:
                                     # bigger than the tint swatches)

# The Settings dialog's NAVIGATION COLUMN (owner ROADMAP 15h item 1,
# 2026-07-18): a left list of section TITLES, each opening its panel on
# the right — replacing the old one-long-scroll layout.
SETTINGS_NAV_WIDTH_PX = 170

# The ring TICK band hover (owner spec 2026-07-12): any of the 360
# arrows answers with what its ANGLE means on each wheel — the 24h
# time, the year-wheel date and the moon-cycle phase. The band spans
# these dial-radius fractions (the arrows' own zone on the ring art).
TICK_HOVER_INNER_FRACTION = 0.86
TICK_HOVER_OUTER_FRACTION = 0.945

# The owner's GOLD letter art (a full latin/greek library for future
# ring presets), overlaid on the ring by calculation so the tint never
# touches them; the silver look is derived by desaturation at load.
RING_LETTER_ART_DIR = paths.assets_dir() / "ring" / "letters"
RING_LETTER_RADIUS_FRACTION = 0.943  # letter center = the middle of the OUTER
                                     # hour band alone (owner spec; measured
                                     # 0.888–0.998 on both ring faces — the
                                     # seconds scale is NOT part of the band)
RING_LETTER_ART_SCALE = 0.075        # letter height, of the dial diameter
                                     # (deliberate slight oversize — owner
                                     # default; the Settings slider scales it)
# Letter shadow (owner spec): a tight, intense dark halo on all sides —
# a gradient border, as if lit from above. Stamped as N offset copies of
# the blackened letter at `alpha` each, `radius` of the letter height.
RING_LETTER_SHADOW_RADIUS = 0.05     # of the letter height
RING_LETTER_SHADOW_ALPHA = 0.55      # per stamp (stamps overlap -> intense)
RING_LETTER_SHADOW_SAMPLES = 8       # offsets around the circle

# The outer GREAT SEAL MOTTO ARC (TASK 1, owner "može radi" 2026-07-19,
# CANON.md §The Banknote; corrected MOTO-FIX round, owner correction
# 2026-07-19, the dollar's Great Seal reference image): curved text
# OUTSIDE the ring band, reusing the SAME letter-art library/finish/
# shadow stamp as the ring's own six letters
# (`render.layers.RingLayer._draw_ring_glyph`), just smaller and
# further out — decorative inscription, not the primary MASON G seats.
# ONE SHARED RADIUS (MOTO-FIX round): the first round's design had both
# mottos' pinned letters land on the SAME angle (O at noon, S at 16h),
# needing two concentric radii to coexist; the corrected layout puts
# ANNUIT COEPTIS over the TOP and NOVUS ORDO SECLORUM under the BOTTOM
# instead — angularly DISJOINT arcs that never collide, so both now
# draw at this one radius (`core.motto.md`'s Design Decisions).
RING_MOTTO_SIZE = 0.0375             # motto letter height, of the dial
                                     # diameter — half RING_LETTER_ART_SCALE
                                     # (decorative, smaller than the six
                                     # primary MASON-G letters)
RING_MOTTO_RADIUS_FRACTION = 1.13    # BOTH arcs (MOTO-FIX round) — clears
                                     # the primary letters' own max reach
                                     # (~1.0255 with shadow at scale 1.0)
                                     # AND the ring-letter hover ceiling
                                     # (GREETINGS_LETTER_OUTER_FRACTION,
                                     # 1.08) with margin

# ANNUIT WORD-GAP round (owner correction 2026-07-19, third batch): the
# TIGHT per-character step every motto letter now advances at, derived
# from NOVUS ORDO SECLORUM's own pin geometry (two 60 deg segments over
# 9 characters each = 6.667 deg/char). A motto pinned only at its first
# and last character (ANNUIT COEPTIS) advances every letter at this
# fixed step from BOTH pins inward (`core.motto._tight_two_pin_angles`)
# instead of spreading the whole span evenly — the owner's "too wide"
# complaint — letting the single interior word gap absorb whatever
# angular slack remains, so the eye/G area breathes like the Great
# Seal's own gap over the eye.
RING_MOTTO_LETTER_STEP_DEG = 60.0 / 9

# --- Hand sizing (owner spec 2026-07-12) -------------------------------------------
# Sizing uses TIP-TO-PIVOT lengths only: the seconds tip reaches the
# ring (the end of the 360-dot scale), the minutes tip the minute
# arrows, and the hours follow each pack's own hours/minutes tip
# ratio. Values derived from the CLASSIC look (285/275-unit tips at
# the old shared 0.88 reach) so existing dials render unchanged.
HAND_SECOND_REACH_FRACTION = 0.88
HAND_MINUTE_REACH_FRACTION = 0.849

# --- Default render config --------------------------------------------------------
# The ONE typed SkinDefinition the compositor consumes; the controller
# overlays the ring preset and the user's display choices onto it.

# --- The PANTHEON roster (owner doctrine 2026-07-15) --------------------------
# Per theme: each seat lists CANDIDATE art paths (relative to
# assets/weekday/, first existing wins) — a seat with NO existing
# candidate falls back to the PLANETARY bundle (file + name + article
# together) so a half-generated pantheon never shows a wrong
# (figure, article) pair. Colored variants live under
# <theme>/pantheon/colored/ mirroring the bronze stems.
WEEKDAY_PANTHEON = {
    "greek": {
        "articles": "greek_pantheon",
        "files": {
            "sun": ("greek/pantheon/zeus", "greek/primary/Zeus"),
            "moon": ("greek/pantheon/poseidon",),
            "mars": ("greek/pantheon/artemis",),
            "mercury": ("greek/pantheon/athena",),
            "jupiter": ("greek/pantheon/apollo",),
            "venus": ("greek/pantheon/hera",),
            "saturn": ("greek/pantheon/demeter",),
        },
        "names": {
            "sun": "Zeus (\u0396\u03b5\u03cd\u03c2)",
            "moon": "Poseidon (\u03a0\u03bf\u03c3\u03b5\u03b9\u03b4\u1ff6\u03bd)",
            "mars": "Artemis (\u1f0c\u03c1\u03c4\u03b5\u03bc\u03b9\u03c2)",
            "mercury": "Athena (\u1f08\u03b8\u03b7\u03bd\u1fb6)",
            "jupiter": "Apollo (\u1f08\u03c0\u03cc\u03bb\u03bb\u03c9\u03bd)",
            "venus": "Hera (\u1f2d\u03c1\u03b1)",
            "saturn": "Demeter (\u0394\u03b7\u03bc\u03ae\u03c4\u03b7\u03c1)",
        },
        "dual": ("greek/pantheon/hades",),
        "dual_names": ("Zeus", "Hades"),
    },
    "norse": {
        "articles": "norse_pantheon",
        "files": {
            "sun": ("norse/pantheon/Odin",),
            "moon": ("norse/pantheon/Hel",),
            "mars": ("norse/primary/Thor",),
            "mercury": ("norse/primary/Loki",),
            "jupiter": ("norse/primary/Tyr",),
            "venus": ("norse/pantheon/Frigg",),
            "saturn": ("norse/pantheon/Freyr",),
        },
        "names": {
            "sun": "Odin (\u00d3\u00f0inn)", "moon": "Hel",
            "mars": "Thor (\u00de\u00f3rr)", "mercury": "Loki",
            "jupiter": "Tyr (T\u00fdr)", "venus": "Frigg",
            "saturn": "Freyr",
        },
        "dual": ("norse/primary/Odin",),
        "dual_names": ("Odin", "The Wanderer"),
    },
    "egypt": {
        "articles": "egypt_pantheon",
        "files": {
            "sun": ("egypt/primary/ra",),
            "moon": ("egypt/pantheon/isis",),
            "mars": ("egypt/pantheon/horus",),
            "mercury": ("egypt/primary/thoth",),
            "jupiter": ("egypt/pantheon/anubis",),
            "venus": ("egypt/pantheon/bastet",),
            "saturn": ("egypt/primary/osiris",),
        },
        "names": {
            "sun": "Ra", "moon": "Isis", "mars": "Horus",
            "mercury": "Thoth", "jupiter": "Anubis",
            "venus": "Bastet", "saturn": "Osiris",
        },
        "dual": ("egypt/primary/afu_ra",),
        "dual_names": ("Ra", "Afu-Ra"),
    },
    "slavic": {
        "articles": "slavic_pantheon",
        "files": {
            "sun": ("slavic/primary/perun",),
            "moon": ("slavic/primary/mokos",),
            "mars": ("slavic/primary/svetovid",),
            "mercury": ("slavic/pantheon/svarog",),
            "jupiter": ("slavic/primary/dazbog",),
            "venus": ("slavic/pantheon/lada",),
            "saturn": ("slavic/primary/morana",),
        },
        "names": {
            "sun": "Perun", "moon": "Moko\u0161", "mars": "Svetovid",
            "mercury": "Svarog", "jupiter": "Da\u017ebog",
            "venus": "Lada", "saturn": "Morana",
        },
        "dual": ("slavic/primary/veles",),
        "dual_names": ("Perun", "Veles"),
    },
}

def pantheon_seat(theme: str, body: str):
    """The PANTHEON seat bundle for (theme, body) — (art_path, name,
    (article_set, body)) with the safety law: the first EXISTING
    candidate plate wins with the pantheon identity; NO existing
    candidate returns None and the caller keeps the PLANETARY bundle
    whole (file + name + article together). Shared by the classic
    unit, the seated slots and the hover resolution."""
    from config import paths as _paths

    table = WEEKDAY_PANTHEON.get(theme)
    if table is None:
        return None
    for rel in table["files"][body]:
        path = WEEKDAY_ART_DIR / f"{rel}.png"
        if _paths.art_file(path).exists():
            return (
                path,
                table["names"][body],
                (table["articles"], body),
            )
    return None



_CONTINENTS = (
    "europe", "north_america", "south_america", "africa", "asia",
    "oceania",
    # The polar views (owner 2026-07-15: the Quick Jump flips the
    # planet onto its poles, so the marker follows).
    "north_pole", "south_pole",
)
# Beyond this |latitude| the Earth marker wears the POLE art instead of
# the continent's — high enough that ordinary cities keep their
# continent view, low enough that the pole jumps (±89.99°) and the far
# polar settlements honestly see the pole.
EARTH_POLE_LATITUDE = 75.0

# The WORKING SET (owner 2026-07-15): originals ship at full
# resolution; the dial reads a once-per-file DOWNSCALED copy instead —
# quality and performance both, for a little disk. Ceilings per assets
# subtree, from the worst case the dial can ask for (1440 dial ×
# 200% element scale × 200% hover enlarge ≈ 800 px for the round
# bodies; the slot seats with their 150% pointer factor ≈ 1200 px).
# Sources at or under the ceiling stay as they are.
WORKING_SET_CEILINGS = {
    "earth": 800,
    "weekday": 800,
    "zodiac": 1200,
    "badge": 1200,
}

# Star + Aura palettes, (pointer, style) -> hues clockwise from the top
# arm. Measured directly from the owner's reference art
# (design/background/{hexa,octa}_{paint,light}.png): paint = subtractive
# primaries (yellow at the top), light = additive primaries (green at
# the top — owner: that IS the point of the two styles). The cross has
# ONE seasons palette (owner's own values: summer yellow top, autumn red
# right, winter blue bottom, spring green left — solstices/equinoxes at
# the arm centers), served under both styles.
_CROSS_SEASONS = ("#D9D900", "#D4330F", "#0A70D8", "#129412")
# The Seasons' SECOND wheel — the FOUR ELEMENTS (owner 2026-07-17,
# CANON §Seasons light): the cross PAINT stays the seasons temperaments
# palette, the cross LIGHT becomes the elements, seating the Tetramorph
# (Lion/Ox/Eagle/Man). Hues clockwise from the top arm — the SAME arm
# order as _CROSS_SEASONS (summer top, autumn right, winter bottom,
# spring left) — so each element lands on its canonical season arm:
#   * summer arm (top)    = FIRE  — a hot flame red-orange, hotter than
#     autumn's blood red so the two cross wheels never read alike;
#   * autumn arm (right)  = EARTH — an olive green-brown, the soil (a
#     muddy green, distinct from spring's pure green in the paint wheel);
#   * winter arm (bottom) = WATER — a deep water blue;
#   * spring arm (left)   = AIR   — a pale white-yellow, the luminous
#     lightest of the four (owner: "air spring-arm white-yellow").
# The classical Western element colours (fire red, air yellow/white,
# water blue, earth green) laid on the seasons the fixed-cross zodiac
# already ties them to (Leo/Taurus/Scorpio/Aquarius).
_CROSS_ELEMENTS = ("#E8391E", "#6B8E3A", "#1E74D0", "#EFE9B0")
# The TRIO's PAINT wheel carries the theological trio (owner spec,
# FINAL.txt #7): Faith yellow at 12h, Love red at 20h, Hope blue at
# 4h — the hexa paint hues at the M, Y, D ring-letter positions. Its
# LIGHT wheel is the FAMILY triangle (CANON, placement APPROVED
# 2026-07-16): the same derivation from the hexa LIGHT primaries at
# 12/20/4 — green at the top (the Child) — with the parents' hues
# LIGHTENED per the owner's member table ("light blue" the Father,
# "light red" the Mother; hue tuning licensed to the agent,
# 2026-07-16). Two wheels, so Paint/Light is LIVE on the Trinity now
# (the Court/Family pair) — only the Seasons keep one palette.
_TRINITY = ("#F8E600", "#B60000", "#002FFF")
_FAMILY = ("#00DC00", "#FF8080", "#7FB2FF")
PALETTE_PRESETS = {
    ("hexa", "paint"): (
        "#F8E600", "#DC9600", "#B60000",
        "#542E85", "#002FFF", "#007E00",
    ),
    ("hexa", "light"): (
        "#00DC00", "#FFFF00", "#FF0000",
        "#BD00BD", "#0040FF", "#00DDDD",
    ),
    # COMPASS palettes (owner rework 2026-07-16): the two octa presets
    # were essentially one wheel with nuance shifts — each palette now
    # ties to its archetype's substance. PAINT = the Walks' materials
    # (King gold, Merchant copper, Soldier iron-blood, Artist velvet,
    # Wanderer road-dust, Scholar lamp ink, Farmer field green, Priest
    # alb ivory). LIGHT = the Wheel of a Life, the Eight Ages (owner
    # shift 2026-07-16: Death at midnight wears pure WHITE — in the
    # light register death goes INTO the light; the moonlight silver
    # moved to the Unborn at 03h, the predawn mist to Birth at 06h;
    # the dawn rose retired). Both keep the day-arc.
    ("octa", "paint"): (
        "#F0C420", "#C87533", "#A02020", "#7A2E8E",
        "#262636", "#1F5FA8", "#3E8914", "#EDEDE0",
    ),
    ("octa", "light"): (
        "#FFE800", "#FFB400", "#FF6A3C", "#9C6BD4",
        "#FFFFFF", "#C8D7F0", "#8FA8C8", "#7CE577",
    ),
    ("cross", "paint"): _CROSS_SEASONS,
    ("cross", "light"): _CROSS_ELEMENTS,
    ("trio", "paint"): _TRINITY,
    ("trio", "light"): _FAMILY,
    # AURORA (owner spec 2026-07-12): [dawn, five day hues, dusk] —
    # paint = azure/green/yellow/orange/red, light = azure/cyan/green/
    # yellow/red; twilight left (dawn) blue, right (dusk) brown.
    ("aurora", "paint"): (
        "#002FFF", "#0080FF", "#007E00", "#F8E600", "#DC9600",
        "#BC0000", "#5D1212",
    ),
    ("aurora", "light"): (
        "#0040FF", "#0080FF", "#00DCDC", "#00DC00", "#FFFF00",
        "#FF2828", "#720017",
    ),
    # CALENDAR (owner 2026-07-16, CANON §The Dozen). TWELVE hues,
    # clockwise from the TOP wedge (the tuple convention for the two
    # wheels differs — see below). paint = the ZODIAC Dozen (boundaries
    # ON the cardinal axes; the RGB circle rotated 15° so no pure
    # primary shows): the FIRST hue fills the wedge that STARTS at the
    # top (12h line), i.e. Cancer, then Leo, Virgo … clockwise. light =
    # the ALMANAC (Month) Dozen (wedges CENTERED on the axes; pure
    # primaries allowed): the FIRST hue fills the wedge CENTERED on the
    # top, i.e. June, then July, August … clockwise.
    ("calendar", "paint"): (
        "#40FF00", "#BFFF00", "#FFBF00", "#FF4000", "#FF0040", "#FF00C0",
        "#BF00FF", "#4000FF", "#0040FF", "#00BFFF", "#00FFBF", "#00FF40",
    ),
    ("calendar", "light"): (
        "#00FF00", "#80FF00", "#FFFF00", "#FFBF00", "#FF0000", "#FF0080",
        "#FF00FF", "#8000FF", "#0000FF", "#0080FF", "#00FFFF", "#00FF80",
    ),
}

# Elements switch "Colorful" OFF (owner spec, FINAL.txt #5): the day and
# twilight arcs are still indicated, but as plain white transparency
# instead of the pointer-palette hues.
COLORFUL_OFF_COLOR = "#FFFFFF"

# --- Calendar pointer (owner 2026-07-16, CANON §The Dozen) ---------------------
# The twelve wedges paint at a base opacity; the LIT wedge (the shichen
# under the hour hand, or the current month/sign) raises it by the
# delta. Calendar-fixed — the wedges never ride the solar rotation.
CALENDAR_WEDGE_ALPHA = 0.30          # every wedge's resting opacity
CALENDAR_WEDGE_LIT_DELTA = 0.50      # extra opacity on the lit wedge
CALENDAR_WEDGE_RADIUS_FRACTION = 0.90  # wedge reach, of the dial radius
# The Earth DAY-ARROW on the Almanac wheel (owner 2026-07-16: "one tick
# ≈ one day"): a small triangle at the marker's exact tick, pointing
# from inside the dial OUTWARD toward the ring so the ring reads today's
# date to the day. Drawn procedurally (the ring numeral arrow is the
# visual reference).
CALENDAR_ARROW_TIP_FRACTION = 0.845  # arrow tip radius (just inside the ticks)
CALENDAR_ARROW_LENGTH_FRACTION = 0.06  # tip-to-base length, of the dial radius
CALENDAR_ARROW_HALF_DEG = 2.4        # half-width of the base, in dial degrees
CALENDAR_ARROW_COLOR = "#FFD235"     # gold, matching the ring letters/ticks

# Octa bottom-arm text (time/date/...): sized to span this fraction of
# the slot width (owner: big font, must not overflow the slot).
TIME_TEXT_WIDTH_FRACTION = 0.95

# Article hovers (owner spec, FINAL.txt hover rework + EXTRAS): the
# entity's art rides on top of its article, larger and clearer than on
# the dial; the prose wraps at a fixed width so QToolTip stays a column.
ARTICLE_IMAGE_WIDTH_PX = 192         # owner: at least 2x — the details must read
ARTICLE_TEXT_WIDTH_PX = 460          # owner 2026-07-13 round two: the prose is
                                     # JUSTIFIED inside a fixed-width column
                                     # (Qt reflows it — no manual wrapping)
ARTICLE_COLUMN_WIDTH_PX = 400        # the hexa TWO-COLUMN legend: each sign's
                                     # column; two of them + spacing must fit
                                     # LEGEND_MAX_WIDTH_FRACTION of a 1080p
                                     # screen (0.45 × 1920 = 864)
# The THREE-SIDE article (owner 2026-07-17): a three-column layout whose
# TOTAL width stays the two-column width (2 × ARTICLE_COLUMN_WIDTH_PX) —
# each column narrower so the text wraps more. First consumer: the Ages
# archetype hover (age text + the Tree register + the Menagerie
# register, "oba odmah"). The image columns scale their register art to
# the column width.
ARTICLE_THREE_COLUMN_WIDTH_PX = round(2 * ARTICLE_COLUMN_WIDTH_PX / 3)   # ≈ 267
ARTICLE_THREE_IMAGE_PX = 240         # each register image in its column
# Subheading spacing (owner 2026-07-14 round two): the heading sits
# CENTERED and visibly closer to ITS paragraph than to the previous one
# — Qt collapses adjacent block margins to the larger, so the paragraph
# after a heading carries the same small top margin.
ARTICLE_SUBHEAD_GAP_ABOVE_PX = 18
ARTICLE_SUBHEAD_GAP_BELOW_PX = 2

# THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20, sealed
# alongside Rule #19 "Compute, Don't Generate" — this is the sanctioned
# way an asset family gets MULTIPLE generated versions instead of one
# frozen master, so it never re-grows into another twelve-plate
# mistake): beside any canonical asset `<dir>/<Name>.png`, additional
# versions live EITHER as `<dir>/<Name>_v2.png`-style suffix siblings
# OR same-named files inside a `<dir>/alt/` subfolder — both pools
# merge into ONE daily rotation, picked deterministically by the
# traveled date's proleptic ordinal modulo the candidate count. Opt-in
# ONLY (never on the hot `art_file` path): a consumer calls
# `rotating_art_file` explicitly. The cadence — how many days each
# shown file stays before advancing (1 = a new face every day) — is
# shared by every rotating family.
ROTATION_DAYS = 1
_VERSION_SUFFIX = re.compile(r"^_v\d*$", re.IGNORECASE)


def _rotation_candidates_in(
    directory: Path, stems: tuple[str, ...]
) -> list[Path]:
    """Every file DIRECTLY inside `directory` matching a bare stem or a
    `stem_v*` sibling, for any stem in `stems` — the single-folder glob
    behind `_rotation_candidates`, factored out so a synthetic tmp tree
    can exercise the naming tolerance directly (no dependency on the
    real bundled assets)."""
    if not directory.is_dir():
        return []
    candidates: list[Path] = []
    seen_names: set[str] = set()
    for stem in stems:
        stem_lower = stem.lower()
        for entry in directory.iterdir():
            if entry.name in seen_names or entry.suffix.lower() != ".png":
                continue
            name_stem = entry.stem
            if not name_stem.lower().startswith(stem_lower):
                continue
            suffix = name_stem[len(stem):]
            if suffix == "" or _VERSION_SUFFIX.match(suffix):
                candidates.append(entry)
                seen_names.add(entry.name)
    return candidates


def _rotation_candidates(
    directories: tuple[Path, ...], stems: tuple[str, ...]
) -> list[Path]:
    """Every version found across `directories` (each searched
    independently, non-recursively — a second register, e.g. an
    `alt/` subfolder, counts exactly like the canonical directory,
    they simply live in different folders), sorted by (filename, full
    path) for a rotation order that is deterministic even when two
    registers share a basename."""
    candidates = [
        entry
        for directory in directories
        for entry in _rotation_candidates_in(directory, stems)
    ]
    candidates.sort(key=lambda p: (p.name, str(p)))
    return candidates


def _pick_rotation(candidates: list[Path], on_date: date) -> Path | None:
    """The ONE shared date-modulo pick every rotating family uses: zero
    candidates -> None (the caller keeps its own fallback), exactly one
    -> that one every day (nothing to rotate), otherwise the SAME date
    always yields the SAME file and consecutive dates advance through
    the set."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    index = (on_date.toordinal() // ROTATION_DAYS) % len(candidates)
    return candidates[index]


def rotating_art_file(canonical_path: Path, on_date: date) -> Path | None:
    """ONE asset from a rotating family, THE UNIVERSAL CONVENTION above
    applied generically: `canonical_path` (a sourceless `<dir>/<Name>
    .png`, exactly like every other config path table entry) resolves
    through the active art SOURCE first (`paths.art_file`), then the
    candidate pool is the resolved directory's own `<Name>` /
    `<Name>_v*` siblings UNION the same search one level down in
    `alt/`. Opt-in per consumer (scale duality, the era emblems,
    tetramorph figures) — never called from the hot `art_file` path
    itself. None when the canonical path itself does not resolve to an
    existing file (nothing to rotate at all, not even a master)."""
    resolved = paths.art_file(canonical_path)
    if resolved is None or not resolved.exists():
        return None
    directory = resolved.parent
    candidates = _rotation_candidates(
        (directory, directory / "alt"), (resolved.stem,)
    )
    return _pick_rotation(candidates, on_date)


# The Judas–Lucifer scale badges (owner 2026-07-13): the two triangle
# medallions illustrating "The Two Triangles" — wired before the art
# lands; the Encyclopedia hides missing files.
SCALE_ART_DIR = paths.assets_dir() / "badge" / "scale"
# SCALE ROTATION (owner decree 2026-07-19, CANON.md one-image-one-place
# amendment — "koje cemo koristiti na smenu"): Judas-Lucifer is a MAIN
# theme, every being living between excessive self-criticism and
# excessive self-love, so BOTH poles keep MULTIPLE generated versions
# instead of freezing on one master — the FIRST family the universal
# rotation convention above was generalized FROM (2026-07-20); it keeps
# its own naming-zoo tolerance (more than one valid STEM per figure,
# `glass/` instead of `alt/` — an established second STYLE register,
# not a generic version pool) rather than becoming a plain
# `rotating_art_file` caller.
# Known filename STEMS per figure, inside SCALE_ART_DIR for the active
# source — the owner's batches landed under more than one stem (the
# canonical "_Triangle" master beside a later lowercase refresh);
# scale_variant_file globs "<stem>.png" and "<stem>_v*.png" for EVERY
# stem below and merges the matches into one rotation.
SCALE_ART_STEMS = {
    "Judas": ("Judas_Triangle", "judas"),
    "Lucifer": ("Lucifer_Triangle", "lucifer"),
}


def scale_variant_file(figure: str, on_date: date) -> Path | None:
    """One Scale badge file for `figure` ("Judas"/"Lucifer") on
    `on_date` — DISCOVERS what actually exists on disk for the ACTIVE
    art source at call time (`_rotation_candidates` against
    SCALE_ART_DIR AND its `glass/` register — the metal cameo and the
    stained-glass windows are two parallel batches of the SAME two
    figures, tolerant of the owner's naming zoo: more than one valid
    STEM per figure, "_v", "_v1", "_v2", "_v3" all count as versions),
    picked by the SHARED `_pick_rotation` — the SAME date always
    yields the SAME file, consecutive dates advance through the set,
    and Lucifer/Judas called with the SAME date stay IN STEP (one
    index driving two independent counts, since both figures' counts
    move together as art lands). Deep travel: the caller passes the
    TRAVELED date, consistent with the poles' light/dark glyph law
    (`controller._effective_travel_date`)."""
    root = paths.art_file(SCALE_ART_DIR)
    candidates = _rotation_candidates(
        (root, root / "glass"), SCALE_ART_STEMS[figure]
    )
    return _pick_rotation(candidates, on_date)


INSTRUMENT_ART_DIR = paths.assets_dir() / "instrument"
# The Astrology/Ascendant hover image trio (owner 2026-07-13): the
# ACTIVE style's art large in the middle, the two remaining styles
# small at its sides.
ASTRO_MAIN_IMAGE_PX = 256
ASTRO_SIDE_IMAGE_FRACTION = 0.35
PERIOD_EARTH_IMAGE_PX = 128          # the Day/Night hover carries a mini Earth
                                     # of the active region (owner 2026-07-12)
ARTICLE_TITLE_PX = 17                # the entity NAME above the article (owner
                                     # spec 2026-07-11: a slightly bigger title,
                                     # then a margin, then the prose)

# --- Legend term highlighting (owner spec 2026-07-12) ------------------------------
# Canon terms POP inside article prose: virtues bold blue, vices bold
# red, moods/emotions bold yellow, color words bold in their own color.
# Applied at RENDER time over the English and Serbian originals (the
# machine-translated languages read plain); hex notes like "(#F8E600)"
# are stripped from the display. Patterns are regex fragments, ALL
# matched case-insensitively (owner report 2026-07-12: a lowercase
# "gordost" must burn red too); Serbian fragments cover the case
# endings including the -šću instrumentals.
LEGEND_VIRTUE_COLOR = "#6FA8FF"
LEGEND_VICE_COLOR = "#FF6B6B"
LEGEND_MOOD_COLOR = "#FFD34D"
LEGEND_TERM_PATTERNS = {
    "virtue": (
        "Humility", "Justice", "Generosity", "Wisdom", "Courage",
        "Serenity", "Love", "Patience", "Faith", "Hope",
        "Poniznost(?:i)?", "Poniznošću", "Pravednost(?:i)?", "Pravednošću",
        "Velikodušnost(?:i)?", "Velikodušnošću",
        "Mudrost(?:i)?", "Mudrošću", "Hrabrost(?:i)?", "Hrabrošću",
        "Spokoj(?:a|u|em)?", "Ljubav(?:i|lju)?", "Strpljenj[eau]",
        "Strpljenjem", "Ver[aeiu]", "Verom", "Nad[aeiu]", "Nadom",
    ),
    "vice": (
        "Pride", "Servility", "Excess", "Greed", "Wrath", "Fear",
        "Jealousy", "Envy",
        "Gordost(?:i)?", "Gordošću", "Pokornost(?:i)?", "Pokornošću",
        "Neumerenost(?:i)?", "Neumerenošću",
        "Pohlep[aeiou]", "Pohlepom", "Gnev(?:a|u|om)?", "Strah(?:a|u|om)?",
        "Ljubomor[aeiou]", "Ljubomorom", "Zavist(?:i)?", "Zavišću",
    ),
    "mood": (
        "Joy", "Zeal", "Passion", "Sorrow", "Calm", "Renewal", "Glory",
        # Awe is the renamed servant mood (2026-07-14); Eclipse stays
        # matchable for The Ninth Mood's own article.
        "Awe", "Eclipse", "Longing",
        "Radost(?:i)?", "Radošću", "Žar(?:a|u|om)?",
        "Strast(?:i)?", "Strašću",
        "Tug[aeiou]", "Tugom", "Mir(?:a|u|om)?", "Obnov[aeiou]", "Obnovom",
        "Sjaj(?:a|u|em)?", "Strahopoštovanj[eau]", "Strahopoštovanjem",
        "Pomračenj[eau]", "Pomračenjem",
        "Čežnj[aeiou]", "Čežnjom",
    ),
}
# Color WORDS wear their own hue — but ONLY the hue(s) of the entity's
# own diamond (owner correction 2026-07-12: in the Soldier's article
# only "orange" colors, in the Merchant's only "purple"; "the red
# planet" or gold-as-money stay plain). Keyed patterns; the accent
# tables below say which keys an article may light up.
LEGEND_COLOR_PATTERNS = {
    "yellow": ((r"yellow\w*", r"žut\w*"), "#F8E600"),
    "gold": ((r"golden|gold\w*", r"zlat\w*"), "#E8C24A"),
    "amber": ((r"amber", r"ćilibar\w*"), "#ECB800"),
    "orange": ((r"orange\w*", r"narandžast\w*"), "#E88A20"),
    "red": ((r"red(?:s|der|dish|dens)?", r"crimson", r"crven\w*"), "#F04040"),
    "purple": ((r"purple\w*", r"violet\w*", r"purpur\w*", r"ljubičast\w*"),
               "#A968E0"),
    "magenta": ((r"magenta", r"magent\w*"), "#E858E8"),
    "blue": ((r"blue\w*", r"plav\w*"), "#5C86FF"),
    "azure": ((r"azure", r"azur\w*"), "#4AA8FF"),
    "green": ((r"green\w*", r"zelen\w*"), "#3ECC3E"),
    "cyan": ((r"cyan", r"cijan\w*"), "#00DCDC"),
    "white": ((r"white\w*", r"bel(?:o|a|e|i|u|im|om|og|oj)\b"), "#FFFFFF"),
    "silver": ((r"silver\w*", r"srebrn\w*"), "#C9CDD3"),
}
# Which color keys each weekday BODY may light up: the union of its
# arm's hues across the palettes (hexa/octa, paint/light) — never a
# color that merely appears in the prose.
BODY_ACCENT_HUES = {
    "sun": ("white", "gold", "yellow", "green"),
    "moon": ("blue",),
    "mars": ("orange", "amber", "yellow"),
    "mercury": ("purple", "magenta", "red"),
    "jupiter": ("yellow", "green", "cyan"),
    "venus": ("red", "orange"),
    "saturn": ("green", "cyan", "azure"),
}
# Zodiac signs inherit their hexa arm's (paint, light) pair; the trio
# virtues their own hue.
SIGN_ACCENT_HUES = {
    "Gemini": ("yellow", "green"), "Cancer": ("yellow", "green"),
    "Leo": ("orange", "yellow"), "Virgo": ("orange", "yellow"),
    "Libra": ("red",), "Scorpio": ("red",),
    "Sagittarius": ("purple", "magenta"), "Capricorn": ("purple", "magenta"),
    "Aquarius": ("blue",), "Pisces": ("blue",),
    "Aries": ("green", "cyan"), "Taurus": ("green", "cyan"),
}
TRIO_ACCENT_HUES = {"Faith": ("yellow",), "Love": ("red",), "Hope": ("blue",)}
# South of the equator the mirrored year wheel seats every sign on the
# OPPOSITE arm (owner spec 2026-07-12) — its accents follow that arm.
_SIGN_OPPOSITE = {
    "Gemini": "Sagittarius", "Cancer": "Capricorn",
    "Leo": "Aquarius", "Virgo": "Pisces",
    "Libra": "Aries", "Scorpio": "Taurus",
}
_SIGN_OPPOSITE.update({south: north for north, south in _SIGN_OPPOSITE.items()})
SIGN_ACCENT_HUES_SOUTH = {
    sign: SIGN_ACCENT_HUES[_SIGN_OPPOSITE[sign]] for sign in SIGN_ACCENT_HUES
}

# The Legend popup (replaces QToolTip, owner decision): capped to these
# screen fractions — taller content scrolls instead of clipping off a
# small screen; dark tooltip styling.
LEGEND_MAX_WIDTH_FRACTION = 0.45
LEGEND_MAX_HEIGHT_FRACTION = 0.85
LEGEND_CURSOR_OFFSET_PX = 14
LEGEND_PADDING_PX = 8
LEGEND_BG = "#2B2B2B"
LEGEND_BORDER = "#6E6E6E"
LEGEND_TEXT = "#FFFFFF"

# The Encyclopedia article view (owner UX rounds 2026-07-12/13): the
# text BLOCK hugs the LEFT edge and spans this fraction of the window
# width — the prose reflows to fill it (no fixed wrap); the font grows
# with the width at a gentle em-like coefficient between the base and
# the cap.
ENCYCLOPEDIA_TEXT_WIDTH_FRACTION = 0.9
ENCYCLOPEDIA_BASE_FONT_PX = 13
ENCYCLOPEDIA_FONT_GROWTH = 0.006     # extra px per viewport px above the base width
ENCYCLOPEDIA_FONT_BASE_WIDTH = 560   # viewport width where the base font applies
ENCYCLOPEDIA_MAX_FONT_PX = 21
# The topic gallery cards (owner 2026-07-13: everything centered, the
# thumbnails RESPONSIVE — they grow/shrink with the window between the
# two bounds; below the minimum the scrollbar takes over).
ENCYCLOPEDIA_TOPIC_ICON_MIN_PX = 72
ENCYCLOPEDIA_TOPIC_ICON_MAX_PX = 200
# LAYOUT fix round R3 (owner: "788px width, tiles clipping" — that class
# dies here): a group NEVER spills more than this many cards per row —
# it WRAPS instead, never a horizontal scrollbar. The single-tile unit
# a card claims at the minimum icon size (the icon plus the existing
# `_rescale_topics` label/padding allowance) times this many columns is
# the dialog's own MIN WIDTH (owner: "MIN WIDTH = 4 * pojedinacni
# karton"), enforced once in `EncyclopediaDialog.__init__`.
ENCYCLOPEDIA_GALLERY_MAX_COLUMNS = 4
ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX = 40   # matches _rescale_topics' + 40/+44
# THE FINISH SWITCHER (owner fix round R3: moved to the top row, in
# line with Home/Download; restyled from filled gradient pills to
# border-only frames in the finish's OWN color — Colored/Bronze/Gold/
# Silver read at a glance instead of hiding behind a generic caption).
# Bronze matches BRONZE_LETTER_TINT (below, out of definition order —
# copied as a literal rather than forward-referenced) so the switcher
# border and the ring-letter bronze read as the SAME bronze; gold/
# silver are the classic heraldic metals, unused as a plain hex
# anywhere else in the palette tables.
ENCYCLOPEDIA_FINISH_BORDER_COLORS = {
    "Bronze": "#CD7F32",         # == BRONZE_LETTER_TINT
    "Gold": "#D4AF37",
    "Silver": "#C0C0C0",
}
# The COLORED option's border (owner correction 2026-07-21: the full
# seven-stop spectrum "baš loše ispao" — a plain two-stop sweep reads
# cleaner): BLUE on the left flowing to RED on the right.
ENCYCLOPEDIA_FINISH_GRADIENT = ("#3B5FE0", "#D8362A")
# Modern reader buttons (owner 2026-07-14: "veći, upečatljiviji,
# življih boja — ne kao app iz 1990-e"): vivid gradient pills shared by
# the Encyclopedia and the Guide. Each role owns a (top, bottom)
# gradient pair; hover lightens and pressed darkens the same pair.
UI_BUTTON_FONT_PX = 17
UI_BUTTON_RADIUS_PX = 12
UI_BUTTON_PADDING_PX = (10, 26)         # vertical, horizontal
UI_BUTTON_SMALL_FONT_PX = 14            # the per-entry look arrows
UI_BUTTON_SMALL_PADDING_PX = (5, 12)
UI_BUTTON_COLORS = {
    "home": ("#4FACFE", "#1565C0"),         # blue — the way back
    "previous": ("#FFB75E", "#E65100"),     # orange
    "next": ("#7EDB7B", "#2E7D32"),         # green
    "download": ("#CE93D8", "#6A1B9A"),     # violet — save the entry
    "neutral": ("#B0BEC5", "#546E7A"),      # the look arrows
}
# Dialog theme (Rule #16 POLISH round, 2026-07-18): the dark-first
# palette for the Settings dialog's chrome (nav column, group-box
# cards, sliders/combos/spinboxes/checkboxes) and the other dialogs'
# base surface — see monorepo DESIGN.md. Anchored on the dial's own
# slate identity (`#2A3439` family) with the gold accent the owner's
# opacity-slider screenshot already wears; `app/theme.py` is the only
# consumer — every other file reaches colors through THEME_COLORS, no
# hex literals scattered in widget code (Rule #4).
THEME_COLORS = {
    "surface_0": "#1A1F22",     # dialog window background
    "surface_1": "#20272B",     # group-box cards
    "surface_2": "#2A3439",     # inputs, nav column (the dial's slate)
    "surface_3": "#333F45",     # hover / raised elevation
    "border": "rgba(255, 255, 255, 28)",
    "text_primary": "#F2F3F4",
    "text_secondary": "#A6B0B4",
    "accent": "#E8B23D",        # gold — the dial's own opacity-slider hue
}
THEME_RADIUS_CONTROL_PX = 8      # buttons, inputs, combos
THEME_RADIUS_CARD_PX = 14        # group-box cards
THEME_RADIUS_PILL_PX = 999       # nav selection pill, checkbox indicator
# Reader image ceiling (owner imperative 2026-07-14): no article or
# Guide image may eat the page — anything taller than this fraction of
# the viewport height scales down to it, leaving room for the text.
# Round two: the WHOLE image grid shares the ceiling — stacked rows
# split it, so the Week's Sunday pairs still leave the text visible.
READER_IMAGE_MAX_HEIGHT_FRACTION = 0.35
# The unlocked hidden mode (owner 2026-07-16, top-only round): hovering
# within this many degrees of the 12h ring letter opens the Four
# Greetings. The hit zone is the LETTER band OUTSIDE the tick scale
# (owner round two: the ticks at that angle must keep their own
# day/year/moon reading), and the stanzas breathe with a small margin,
# not a full blank line. The 24h (Omega) letter no longer answers this
# hover — that spot now carries the reveal-week double-click below.
GREETINGS_LETTER_HALF_DEG = 6.0
GREETINGS_LETTER_OUTER_FRACTION = 1.08
GREETINGS_STANZA_GAP_PX = 6

# Omega (24h) double-click (owner 2026-07-16; hit region reworked
# 2026-07-17, slika 9): the hit is the FULL ROUND AREA at the 24h ring
# seat — a circle CENTERED on the Omega letter position (180°, the ring
# letter band) with a radius covering the whole letter cell. The old
# narrow annular wedge only answered on the letter glyph itself (its
# lower part), so the double-click kept missing; the round area is
# derived from the ring-letter art size (a letter spans ~2× its
# ART_SCALE of the radius, so 1.5× the ART_SCALE comfortably covers the
# cell and its corners without reaching the 22h/2h numerals). Tunable.
OMEGA_HIT_RADIUS_FRACTION = RING_LETTER_ART_SCALE * 1.5
REVEAL_WEEK_DURATION_S = 60.0

# Time Travel QUICK JUMPS (owner 2026-07-14): one-click presets under
# the Time Travel menu — sun/moon turning points, the poles, and the
# Royal Observatory itself. Same rules as the dialog:
# TIME_TRAVEL_DURATION_S, then back to the present; the jumps CHAIN
# from the running simulation. The places are REAL coordinates with
# their REAL clocks (the poles ride UTC).
QUICK_JUMP_POLE_LATITUDE = 89.99     # exact 90 divides astral by zero
GREENWICH_LATITUDE = 51.4779
GREENWICH_LONGITUDE = 0.0
GREENWICH_TIMEZONE = "Europe/London"

# Time Travel MINI WINDOW rows (item 3A, R5 MENU REWORK — the deep
# Quick Jump submenu chain, `UV/DESIGN/Meni One over Another.png`,
# grows DOWN into the dialog itself instead): the row icon/arrow-button
# pixel sizes, TUNABLE (Rule #4 — no bare numbers in the row builder).
TIME_TRAVEL_ROW_ICON_PX = 26
TIME_TRAVEL_ARROW_BUTTON_PX = 34

# The slot ROUNDEL (owner 2026-07-14, watch-subdial inspiration):
# every TEXT display and the flat astrology art (sign / logo /
# constellation) sit on a subdial; with no art at all the PROCEDURAL
# circle takes over — the ring's own face color, rimmed in the letter
# FINISH metal. Circular plates (medallions, planets, colored badges)
# stay bare.
#
# THE FIVE SETS (owner decree 2026-07-21, Rsub round — retires the
# Rule #19 "one master per source" model this constant used to name):
# the plate is its OWN shared thing now, no longer split by art
# source. Five hand-picked sets live under assets/subdial/ (see
# assets/___assets.md for why that root sits OUTSIDE
# ART_SOURCED_ROOTS): "set1".."set4" are each three hand-drawn
# finishes (`render.assets.subdial_plate_file` returns the matching
# file directly, no recolor); "solo" ships ONE hand-drawn file
# (SUBDIAL_SOLO_FINISH) and the algorithm derives the other two live,
# same recipe as before. The user picks the SET in Settings
# (`Settings.subdial_set`); the letter FINISH (ring_finish, tray Design
# menu) still decides which color draws within it. The SEAT never
# touches the file at all, only the LIVE shadow
# (`render.layers._draw_subdial_shadow`) — unchanged since Rule #19's
# first enforcement.
SUBDIAL_ROOT_DIR = paths.assets_dir() / "subdial"
SUBDIAL_SOLO_FINISH = "silver"      # the solo set's one hand-drawn file
SLOT_ROUNDEL_BORDER_FRACTION = 0.045     # rim width, of the diameter
SLOT_ROUNDEL_CONTENT_FRACTION = 0.78     # content size inside the rim
SLOT_ROUNDEL_FILL_FALLBACK = "#39434D"   # unreadable/missing ring art
SLOT_ROUNDEL_BORDER_COLORS = {
    "gold": "#FFD235",
    "silver": "#C9CDD3",
    "bronze": "#CD7F32",
}
# The SMALL-SECONDS complication (owner 2026-07-14): eight tick marks
# just inside the subdial rim — four larger at the cardinals, four
# smaller between — with a soft shadow, never touching the bezel; the
# mini hand's tip stays inside the tick ring. Colors (owner 2026-07-15
# A/B spec): the mini hand always wears the letter FINISH metal over
# its own drop shadow; the ticks are white on the "black" plate style
# and finish-colored on the "theme" style.
SMALL_SECONDS_TICK_OUTER_FRACTION = 0.80
SMALL_SECONDS_TICK_MAJOR_FRACTION = 0.18
SMALL_SECONDS_TICK_MINOR_FRACTION = 0.11
SMALL_SECONDS_TICK_RGBA = (255, 255, 255, 235)
SMALL_SECONDS_TICK_SHADOW_RGBA = (0, 0, 0, 140)
SMALL_SECONDS_HAND_SHADOW_OFFSET_FRACTION = 0.035   # of the subdial radius
SMALL_SECONDS_HAND_SHADOW_OPACITY = 0.55

# Complication TEXTS on the subdials (owner 2026-07-15): always the
# letter-finish metal color — never white — over a drop shadow so they
# read on both plate styles.
SUBDIAL_TEXT_SHADOW_RGBA = (0, 0, 0, 180)
SUBDIAL_TEXT_SHADOW_OFFSET_FRACTION = 0.06          # of the font pixel size

# Per-pointer SLOT sizing (owner 2026-07-15): the diamonds differ —
# the slim-armed Seasons and Compass carry 125%, the big-diamond
# Trinity/Prism, Aurora and the pointer-off layouts 150%; on the slim
# arms the seat also shifts OUTWARD to the diamond's widest point
# (the between-arm 3h/21h seats stay put).
SLOT_SIZE_BY_POINTER = {
    "trio": 1.50, "hexa": 1.50, "aurora": 1.50,
    "cross": 1.25, "octa": 1.25,
    # Calendar rides the PINNED layout (no arms) — the big-slot size.
    "calendar": 1.50,
}
SLOT_SIZE_PINNED = 1.50
SLOT_SEAT_OUTWARD = {"cross": 1.12, "octa": 1.12}

# The weekday-by-colors unit rides the ROMB CENTER of its diamond (owner
# 2026-07-15): the star tip sits at star.radius_fraction and a diamond's
# diagonals cross at EXACTLY half the tip on every pointer (inner =
# tip / (2 cos half) ⇒ projection = tip/2), so the by-colors body centers
# in the romb at this fraction of the tip — uniformly, whatever the
# pointer (Trinity/Prism/Seasons/Compass all inherit the same position).
WEEKDAY_ROMB_CENTER_OF_TIP = 0.5

# The subdial's live SHADOW (owner 2026-07-15: the sun lives at the
# dial center, the shadow is RENDERED, never baked) — offset outward
# from the center, none on the center seat.
SUBDIAL_SHADOW_RGBA = (0, 0, 0, 100)
SUBDIAL_SHADOW_OFFSET_FRACTION = 0.05    # of the subdial diameter
SUBDIAL_SHADOW_SPREAD = 1.04             # shadow radius vs the plate's

# Recoloring the SOLO set's silver master to the other two letter
# finishes (owner 2026-07-15 recipe, still live for the solo set after
# the Rsub round, 2026-07-21 — sets 1-4 are hand-drawn per finish and
# never reach this function for their finish, only for the optional
# "theme" tint pass): only BRIGHT, LOW-SATURATION pixels take the
# finish color multiplied by their own luminance — and ONLY inside the
# radial BEZEL band (owner correction, his three side-by-side grabs:
# without the radial mask the field's own specular highlights drank
# the metal and the three finishes' interiors stopped matching).
# Measured on the solo master: the field runs to r≈0.85, the brushed
# bezel starts there.
SUBDIAL_RECOLOR_VALUE_RAMP = (0.30, 0.60)
SUBDIAL_RECOLOR_SAT_CUTOFF = (0.10, 0.30)
SUBDIAL_RECOLOR_RIM_RADIUS = (0.82, 0.87)   # radial ramp, of plate radius
SUBDIAL_RECOLOR_VERSION = 3      # cache tag — bump on recolor math changes
# The "theme" plate style multiplies the DARK field by the clock tint;
# the raw luminance (~0.2) would leave the hue barely readable, so the
# field brightens by this gain before the tint lands (texture intact).
SUBDIAL_RECOLOR_FIELD_GAIN = 1.9
# SILVER has no entry here on purpose (2026-07-20 rework): it is the
# achromatic VALUE alone, the exact letter-metal "straight desaturation"
# recipe (`letter_metal_file`) — never a stored target color like gold/
# bronze, so it can never drift toward a hue by accident.
SUBDIAL_RECOLOR_COLORS = {
    "gold": "#FFD235",
    "bronze": "#CD7F32",
}

# The hidden REPORT window (owner 2026-07-15): function efficiency
# statistics — table + two QPainter charts in one quiet gold hue
# (single-series marks; identity lives in the row labels, exact
# numbers in the table).
REPORT_REFRESH_MS = 1000
REPORT_BAR_TOP_N = 10
REPORT_CHART_HEIGHT_PX = 170
REPORT_MARK_COLOR = "#C9980B"        # satin gold — the one series hue
REPORT_MARK_DIM_COLOR = "#6E5A18"    # unselected bars
REPORT_INK_COLOR = "#E8EAED"         # primary text on the chart
REPORT_MUTED_COLOR = "#9AA0A6"       # secondary text / axis
REPORT_SURFACE_COLOR = "#202124"     # chart surface

# ─── THE OBSERVATORY (Session 17, owner 2026-07-16) ────────────────────
# The statistics sibling of the Encyclopedia ("kao enciklopedija, samo
# sa statistikom"): dark, QPainter-drawn interactive charts over the
# long ephemeris data. Series data ships as compact BUNDLED JSON under
# Database/ (setup/make_observatory.py). Colors are canon and FIXED per
# series (color fidelity — never re-colored when a checkbox hides one):
# the four seasons wear their cross-wheel ELEMENT hues, the light/dark
# half-years gold vs slate; surface/ink/grid reuse the dark dialog
# palette (THEME_COLORS) so the window wears apply_theme like every
# other reader dialog.
OBSERVATORY_BUNDLE_SEASONS = "observatory_seasons.json"
OBSERVATORY_BUNDLE_ECLIPSES = "observatory_eclipses.json"
OBSERVATORY_BUNDLE_ENVELOPE = "observatory_envelope.json"
OBSERVATORY_CHART_MIN_HEIGHT_PX = 240
OBSERVATORY_SURFACE_COLOR = THEME_COLORS["surface_0"]      # chart body
OBSERVATORY_INK_COLOR = THEME_COLORS["text_primary"]       # labels
OBSERVATORY_MUTED_COLOR = THEME_COLORS["text_secondary"]   # axis / ticks
OBSERVATORY_GRID_COLOR = "#3A464C"                          # recessive grid
OBSERVATORY_CROSSHAIR_COLOR = "#E8B23D"                     # hover crosshair
OBSERVATORY_LINE_WIDTH_PX = 2
OBSERVATORY_GRID_WIDTH_PX = 1
OBSERVATORY_MARK_RADIUS_PX = 3
# The four seasons' canonical cross-wheel hues (Spring=air, Summer=fire,
# Autumn=earth, Winter=water — the same _CROSS_ELEMENTS the Seasons
# pointer paints) plus the two half-years (gold light, slate dark).
OBSERVATORY_SERIES_COLORS = {
    "spring": _CROSS_ELEMENTS[3],       # air — pale white-yellow
    "summer": _CROSS_ELEMENTS[0],       # fire — red
    "autumn": _CROSS_ELEMENTS[1],       # earth — olive green-brown
    "winter": _CROSS_ELEMENTS[2],       # water — deep blue
    "light": "#E8B23D",                 # the light half-year — gold
    "dark": "#6E7B82",                  # the dark half-year — slate
}
# The eras painted on the light−dark chart: the Age of Light band gold,
# the Age of Darkness band slate (low alpha wash), the Anno Lucis /
# transition verticals in muted ink. (hex, alpha) — alpha applied live.
OBSERVATORY_ERA_LIGHT_BAND = ("#E8B23D", 26)
OBSERVATORY_ERA_DARK_BAND = ("#6E7B82", 30)
OBSERVATORY_ERA_MARK_COLOR = "#C9CDD3"
# The eclipse timeline: solar gold, lunar the blood-moon copper (the
# same BRONZE family the on-dial lunar eclipse wears — color fidelity).
OBSERVATORY_ECLIPSE_COLORS = {"solar": "#E8B23D", "lunar": "#B87333"}
OBSERVATORY_NOW_MARK_COLOR = "#E8391E"          # the traveled moment line
# The eclipse timeline's zoom (Deep Time mode): the nearest N eclipses
# of EACH kind on EACH side of the moment (~2.4 of each kind per year,
# so 60 ≈ a ±25-year window around the moment).
OBSERVATORY_ECLIPSE_WINDOW_N = 60
# The day-length curve at the current location: one gold line over the
# year; astral is asked once every N days (a smooth curve, cheap open).
# The step itself is set below (Fix round R1a, Item 5 — 1-day ticks).
OBSERVATORY_DAYLENGTH_COLOR = "#E8B23D"

# ─── Fix round D (owner verdicts 2026-07-19) ───────────────────────────
# Task 1 — mouse-wheel zoom, centered on the cursor's x, on every chart;
# double-click resets to the full span. The Y axis auto-fits whatever x
# slice is visible after each zoom change (owner: min at the bottom, max
# at the top, with a little padding — matching the un-zoomed pad below).
OBSERVATORY_ZOOM_FACTOR = 0.85          # per wheel notch (in); 1/factor = out
OBSERVATORY_ZOOM_MIN_FRACTION = 0.01    # narrowest view, fraction of full x-span
OBSERVATORY_Y_FIT_PAD_FRACTION = 0.08   # y padding above/below the visible slice

# Task 2 — the Days<->Hours switch for every "light - dark" readout (the
# envelope's y-axis/crosshair, the season chart's light/dark delta line).
# Pure display transform (x24); the underlying series always stay in days.
OBSERVATORY_UNITS_DEFAULT = "days"

# Task 3 — every light/dark peak of the envelope gets a label (not just
# the four sealed era marks); at full zoom, labels closer than this many
# pixels are thinned (kept when zoomed in, where there is room). The
# extrema finder needs a WINDOW wider than the season bundle's bin-mean
# decimation stride (20 yr, setup/make_observatory.py SEASON_BIN_YEARS)
# — a bare neighbor comparison flags the bin-to-bin rounding noise near
# every true peak as dozens of spurious extrema; a candidate must be the
# most extreme point within this many years on each side (the real
# oscillation's half-period is ~10,000 years, so this comfortably
# separates true peaks without merging two of them together).
OBSERVATORY_VMARK_MIN_SPACING_PX = 46
OBSERVATORY_EXTREMA_WINDOW_YEARS = 1000

# Task 4 — the fifth chart: the La2004 Laskar long envelope (amplitude
# only, charts-only doctrine — ROADMAP 15a2). Colors echo the research
# plot (research/ephemeris/long_envelope.py): gold amplitude band, muted
# silver signed oscillation, teal DE441-measured-window wash.
OBSERVATORY_LASKAR_ENVELOPE_COLOR = "#E8B23D"
OBSERVATORY_LASKAR_SIGNED_COLOR = "#C7CDD6"
OBSERVATORY_LASKAR_DE441_BAND = ("#4FB0C6", 30)

# ─── Fix round G (owner verdicts 2026-07-19, slika 8 + addendum) ───────
# Task 1 — the x/y tick PITCH must adapt to the visible span on every
# chart. The chooser is the classic "nice number" ladder (1-2-5 per
# decade — 1/2/5/10/20/50/100/200/500/1k/2k/5k/10k/20k/50k/… — generated
# arithmetically, not hardcoded, so it also covers the fractional range
# below 1 for small y-spans), picking the smallest rung that keeps the
# tick count at/under the target; once even the ladder's finest rung
# (1, in whatever unit the axis is in) exceeds the target count, that
# rung is used anyway — more ticks than the target, but nothing finer
# is meaningful. Separate targets for X (time) and Y (value) — X sits
# a little denser, matching how a wide time axis reads.
OBSERVATORY_TARGET_X_TICKS = 8
OBSERVATORY_TARGET_Y_TICKS = 6
# The zoom clamp (OBSERVATORY_ZOOM_MIN_FRACTION above) is a FRACTION of
# each chart's own full span — fine for the day-length curve (365 days
# -> ~3.6-day floor) but on the multi-millennial charts (season/
# envelope/Laskar, tens to hundreds of thousands of years) 1% is still
# hundreds to thousands of years, so the tick ladder could never reach
# its 1-year rung no matter how far the user zoomed (owner's complaint,
# "TICK na 1 GODINU" at max zoom). This ABSOLUTE floor is combined with
# the fraction — whichever is SMALLER wins — so max zoom on every chart
# reaches a handful of units, comfortably inside the target-8 threshold
# where the ladder bottoms out at its finest (1-unit) rung.
OBSERVATORY_ZOOM_MIN_SPAN_FLOOR = 6

# Task 2 — every chart gets a QSplitter handle so the owner can stretch
# it vertically; sizes remember the SESSION only (a module-level cache
# in app/observatory.py, cleared on app restart) — no settings key,
# matching that this dialog's own window size already isn't persisted
# across opens.

# Task 3 — the per-chart "Enlarge" button opens a maximized dialog
# hosting the SAME chart widget (reparented, not copied — so zoom/pan/
# checkbox state carries over for free) plus an extended legend and an
# info strip. No new tokens needed — colors/fonts reuse the surface/ink/
# muted triad above.

# ─── Fix round R1a (owner instruction batch 2026-07-20) ────────────────
# Item 1 — the Enlarge dialog no longer maximizes; it opens at a fixed
# ASPECT (16:9) sized to a FRACTION of the screen's available height
# (0.5 -> exactly 25% of screen AREA on a 16:9 screen, the owner's own
# arithmetic, since area = (fraction*H)^2 * (w/h) and on a 16:9 screen
# H*(w/h) = W, collapsing to fraction^2 regardless of the screen's own
# size). Still resizable/maximizable by hand (the window hints stay).
OBSERVATORY_ENLARGE_HEIGHT_FRACTION = 0.5
OBSERVATORY_ENLARGE_ASPECT_W = 16
OBSERVATORY_ENLARGE_ASPECT_H = 9

# Item 2 — the eclipse legend recolor (owner: "lakše razlikuje... mesec
# PLAVIM a Sunce ZUTIM"): solar kinds walk yellow->orange->red (mildest
# to most total), lunar kinds walk navy->blue->cyan (faintest penumbral
# to most total) — the ground-truthed type vocabulary is pinned by
# tests/test_eclipse.py::test_type_state_mapping_covers_the_ground_truthed_vocabulary.
OBSERVATORY_ECLIPSE_KIND_COLORS = {
    "solar": {
        "partial": "#F4D35E",
        "annular": "#F2994A",
        "hybrid": "#EB5E28",
        "total": "#D62828",
    },
    "lunar": {
        "penumbral": "#2E4A7A",
        "partial": "#2F6FED",
        "total": "#4FD5E8",
    },
}
# One honest sentence per kind for the Enlarge info panel's eclipse
# legend rows (owner: "sa strane tekst o svakoj ukratko opisano šta
# označava").
OBSERVATORY_ECLIPSE_KIND_INFO = {
    ("solar", "partial"): "The Moon covers only part of the Sun's disc.",
    ("solar", "annular"): (
        "The Moon's disc is too small to fully cover the Sun — a bright ring remains."
    ),
    ("solar", "hybrid"): "The eclipse shifts between annular and total along its path.",
    ("solar", "total"): "The Moon fully covers the Sun's disc.",
    ("lunar", "penumbral"): "The Moon crosses only Earth's faint outer shadow.",
    ("lunar", "partial"): "Part of the Moon enters Earth's dark umbral shadow.",
    ("lunar", "total"): (
        'The Moon fully enters Earth\'s dark umbral shadow (a "blood moon").'
    ),
}

# Item 5 — the day-length curve now samples every REAL day (was every 2)
# so the chart's own data genuinely supports a 1-day tick pitch at deep
# zoom (owner: "MIN TICK ... Day Length" — the old 2-day stride made a
# 1-day pitch a lie the ladder could still draw). Cheap: 365 astral
# lookups once per dialog open, not a hot path.
OBSERVATORY_DAYLENGTH_STEP_DAYS = 1
# Fix round R1a Task 5's floor for the day chart's tick ladder: never
# subdivide a whole calendar day (see _DayLengthChart._x_ticks) — its
# "Mon D" labels round to the nearest day, so any finer pitch would
# print duplicate labels on distinct gridlines.
OBSERVATORY_DAYLENGTH_MIN_TICK_DAYS = 1.0

# The Enlarge dialog's collapsible right-side info panel (Item 2).
OBSERVATORY_INFO_PANEL_WIDTH_PX = 280

# The Observatory's own splitter/collapse bug fix (Item 7 — "RESIZE ne
# radi"): `_ChartBase` is a bare-painted QWidget with NO layout of its
# own, so its default sizeHint() is invalid (-1,-1) and every panel's
# NATURAL size collapses to exactly its `OBSERVATORY_CHART_MIN_HEIGHT_PX`
# floor — meaning every panel sits pinned at its own minimum the moment
# the dialog is smaller than the splitter's full natural height (the
# QScrollArea then gives the splitter ONLY its natural size, no stretch
# slack, and `setChildrenCollapsible(False)` forbids shrinking anything
# further) — so an interactive drag has NOTHING to redistribute and
# silently does nothing (confirmed with a real QTest mouse-press/move/
# release drive at the dialog's own default size). A real `sizeHint()`
# genuinely larger than the floor gives every panel headroom to trade
# with its neighbor regardless of window size.
OBSERVATORY_CHART_PREFERRED_HEIGHT_PX = 320

# The Guide window (owner spec: a paged, RESIZABLE help book): pages
# DIALOG OPENING SIZES (owner DESIGN #1, R4 instruction batch
# 2026-07-20): Encyclopedia and Observatory open A4-PORTRAIT shaped
# (the 210:297mm paper ratio) at this fraction of the screen's
# available height; Settings and Guide open perfectly SQUARE (1:1) at
# this fraction — `app.theme.size_to_screen` applies both. Every one
# of the four dialogs stays a normal resizable/maximizable window past
# this first paint; only the OPENING size is fixed here.
DIALOG_A4_HEIGHT_FRACTION = 0.8
DIALOG_A4_ASPECT_W = 210
DIALOG_A4_ASPECT_H = 297
DIALOG_SQUARE_HEIGHT_FRACTION = 0.5

# group related images (pages.json), captions.json holds per-image
# Title\ntext; images open at 540 px (75% of the 720 originals) and
# scale live with the window.
GUIDE_DIR = paths.assets_dir() / "guide"
GUIDE_INITIAL_IMAGE_PX = 540
GUIDE_TITLE_PX = 22
GUIDE_SUBTITLE_PX = 17
GUIDE_BODY_PX = 14        # owner 2026-07-14: the caption text was tiny
GUIDE_SPACING_PX = 8

# Translation (owner spec: translate-once-then-cache, no accounts, no
# keys): the keyless Google gtx endpoint; the per-language cache lives
# beside settings.json in %APPDATA%/DOMY Watch/translations/.
TRANSLATE_ENDPOINT = "https://translate.googleapis.com/translate_a/single"
TRANSLATE_TIMEOUT_S = 15

# Transparent margin around the dial INSIDE the window (owner bug
# report: M and Omega touch the window square and their overhang and
# shadow get clipped; owner 2026-07-16: the event glow at the bottom of
# the ring was square-cut too). It is COMPUTED LIVE from the user's
# settings — see dial_window_margin_fraction() in the event-glow section
# below (it needs GLOW_* which are defined there), so any size/hover/
# letter slider re-sizes the window to fit exactly (owner 2026-07-17).

# Umbra contrast spans, (lightest, darkest) window bounds. Owner spec:
#   full  — the whole gray range: sectioned ladders run endpoint-
#           inclusive (16 shades -> 255..0 step 17, matching his art);
#   half  — the MIDDLE half [64, 192]; light — the BRIGHT half
#           [128, 255]; dark — the DARK half [0, 127]. These three take
#           the centers of N equal bins (exact step 8 for 16 shades:
#           half 188..68, light 252..132, dark 124..4).
# The gradient form sweeps the same spans continuously.
UMBRA_CONTRAST_SPANS = {
    "full": (255, 0),
    "half": (192, 64),
    "light": (256, 128),
    "dark": (128, 0),
}

# --- Season/moon event glow rendering (windows live in constants) ---------------
# Turning-point glow REWORK (owner 2026-07-16): at a GLOW event the
# glowing marker relocates RADIALLY to the ring band centerline — the
# radius where the hour numerals and ring letters sit — keeping its event
# ANGLE (New Moon still at the 12h reading). The compact halo then
# STRADDLES the ring, shining both inside and outside the circle, so it
# reads over any background (a white Compass tip, the bright yellow top
# arms) without needing to be huge. New colors: the Sun's events (the
# Earth marker at a solstice/equinox) glow GOLDEN, the Moon's phases glow
# SILVER — starting values the owner tunes here.
GLOW_RING_RADIUS_FRACTION = RING_LETTER_RADIUS_FRACTION  # ring band centerline
GLOW_SUN_COLOR = "#FFCC33"           # golden — distinct from the yellow arms
GLOW_MOON_COLOR = "#E8EBEE"          # silver — bright, reads on the dark ring
GLOW_CORE_ALPHA = 1.0
GLOW_MID_ALPHA = 0.85
GLOW_MID_STOP = 0.75                 # gradient position of the mid alpha
GLOW_RADIUS_SCALE = 1.5              # halo radius, multiple of the marker radius

# The transparent window margin (owner slike 1–3, 2026-07-17): LIVE from
# the user's ACTUAL settings, not a fixed max-everything constant. The
# margin per side (a fraction of the window DIAMETER) must cover BOTH
# things that overhang the dial square, or either gets a hard square cut
# at the window edge:
#   * the event GLOW — the glowing marker (the LARGER of the Earth/Moon,
#     each carrying the user's earth/moon scale) relocates to the ring
#     band (GLOW_RING_RADIUS_FRACTION), is hover-enlarged by the user's
#     hover_enlarge, and its halo reaches GLOW_RADIUS_SCALE further
#     (owner 2026-07-16 bug: a full-moon halo at the bottom of the ring
#     was square-cut);
#   * ring LETTERS — at the user's letter-scale slider, the Omega/M
#     overhang the ring by their half-height plus the shadow halo.
# The extents are fractions of the dial RADIUS; the margin is a fraction
# of the DIAMETER applied per side, i.e. half the radius-fraction overhang
# beyond 1.0, plus a small safety epsilon so anti-aliasing never bleeds
# into the outermost row. The OLD fixed value was 0.1465 (max markers ×
# max hover); at default settings this shrinks well below it, and at max
# settings it grows past it — exact reservation, no waste, no clip.
#
# MARGIN GAP DIAGNOSIS (owner slika 4, 2026-07-17: a hovered glowing Earth
# stopped visibly short of the window edge). Term by term, the reserved
# window half-extent equals `max(glow_extent, letter_extent) + 2·EPSILON`
# (radius fractions), against the marker+glow that actually reaches
# `glow_extent`. Auditing each candidate:
#   * the EPSILON — this was the whole gap. At 0.01 of the DIAMETER it
#     reserves 2·0.01 = 0.02 of the RADIUS beyond the glow, i.e. ~7 px at
#     a 720 dial, ~14 px at 1440. That fixed slab is the "stops visibly
#     short". Tightened to 0.003 → ~2 px at 720, still a sub-pixel-safe
#     anti-aliasing guard so the faint halo tail never hard-clips.
#   * max(earth, moon) — NOT waste: BOTH markers relocate to the ring band
#     (GLOW_RING_RADIUS_FRACTION) and glow there — the Earth at a
#     sun event (golden), the Moon at a moon event (silver) — so the
#     LARGER of the two is the genuine worst case for a square window.
#   * the glow-halo × hover product — NOT waste: slika 4 IS a hovered
#     glowing marker, so hover and glow do stack; the halo reaches
#     GLOW_RADIUS_SCALE past the hover-enlarged marker and must be covered.
#   * the ring-letter floor — NOT waste: the letters overhang the ring by
#     half their height plus the shadow; taken as the max against the glow
#     because either can be the binding radius on the square window.
# So the single real over-reservation was the epsilon; everything else is
# an exact bound. After the tighten the hovered glowing marker lands within
# ~1–2 px of the edge and never clips (pinned both ways by the pixel test).
DIAL_WINDOW_MARGIN_EPSILON = 0.003   # anti-aliasing safety (owner: small)


def dial_window_margin_fraction(skin) -> float:
    """The per-side transparent window margin (fraction of the dial
    DIAMETER) for the CURRENT skin (owner 2026-07-17). Recomputed on
    every skin install so moving a size/hover/letter slider re-sizes the
    window to fit exactly. `skin.year_marker.scale`/`.moon_scale` already
    carry the user's earth/moon multiplier (apply_display_settings).

    TASK 1 (owner "može radi" 2026-07-19): a preset with a `motto` arc
    (MASON G today) reaches further out than the plain ring letters —
    `motto_extent` is 0.0 (a no-op term in the max()) for every OTHER
    preset, exactly the graceful-absence pattern `triangle`/`legend`
    already use, so this never grows the margin for DOMY/MORPH/NUMBERS
    or a custom ring. MOTO-FIX round (owner correction 2026-07-19): both
    mottos now share ONE radius (the two arcs are angularly disjoint),
    so this measures from `RING_MOTTO_RADIUS_FRACTION` alone —
    `RING_MOTTO_RADIUS_STEP` is gone."""
    marker = max(skin.year_marker.scale, skin.year_marker.moon_scale)
    glow_extent = (
        GLOW_RING_RADIUS_FRACTION
        + marker * GLOW_RADIUS_SCALE * skin.hover_enlarge
    )
    letter_extent = (
        RING_LETTER_RADIUS_FRACTION
        + RING_LETTER_ART_SCALE * skin.ring_letter_scale
        * (1.0 + 2.0 * RING_LETTER_SHADOW_RADIUS)
    )
    motto_extent = 0.0
    if skin.ring.motto:
        motto_extent = (
            RING_MOTTO_RADIUS_FRACTION
            + RING_MOTTO_SIZE * skin.ring_letter_scale
            * (1.0 + 2.0 * RING_LETTER_SHADOW_RADIUS)
        )
    return (
        max(glow_extent, letter_extent, motto_extent) - 1.0
    ) / 2.0 + DIAL_WINDOW_MARGIN_EPSILON

# --- Shared app content (NOT skin-specific — a skin is a dial design) -----------
# Skeleton folders with 1x1 placeholders ship in the repo; the owner
# pastes his vector renders OVER them (same names). A missing file
# still falls back to the text form (documented).
ZODIAC_ART_DIR = paths.assets_dir() / "zodiac"
WEEKDAY_ART_DIR = paths.assets_dir() / "weekday"
# The cross-cure emblem logos (owner Gemini art 2026-07-12): one PNG
# per virtue/sin/mood, Capitalized stems, 8 per family (Sunday twice).
EMBLEM_ART_DIRS = {
    "virtues": paths.assets_dir() / "emblem" / "virtue",
    "sins": paths.assets_dir() / "emblem" / "sin",
    "moods": paths.assets_dir() / "emblem" / "mood",
    "intelligence": paths.assets_dir() / "emblem" / "intelligence",
}
# The trinity and season badge families (owner Gemini art 2026-07-13):
# Faith/Hope/Love triskelions; the Goethe-axis seasons with the
# tropics' Wet_Season/Dry_Season, plus turning_point/ (the solstices
# and the one Equinox) and meteorological/ (the measured twins).
TRINITY_ART_DIR = paths.assets_dir() / "badge" / "trinity"
SEASON_ART_DIR = paths.assets_dir() / "badge" / "season"
# The ERA TERMS emblems (ROADMAP 15a3, owner 2026-07-17): one per Age
# (Light/Darkness) and per Starry Season (Spring/Summer/Autumn/Winter)
# — the "Eras of the World" comparative article carries no plate of
# its own. Prompt sheet: research/prompts/era/era_prompts.md.
ERA_ART_DIR = paths.assets_dir() / "era"
# Arm-hover badge width (the trio/cardinal/diagonal tooltips carry
# their emblem above the text — smaller than the article plates).
HOVER_BADGE_WIDTH_PX = 128

# --- Hover article warm sweep (owner 2026-07-18) --------------------------------
# The background pre-build of every hover article (compositor
# .warm_hover_articles): a polar probe grid over the whole dial, walked
# through the real tooltip dispatch. 180 angles x 40 rings keeps the
# pitch under half the smallest hover target (the Moon marker) at every
# supported diameter; the per-ring pause keeps the sweep slow and
# polite — image by image, never a CPU burst at startup.
HOVER_WARM_ANGLE_STEPS = 180
HOVER_WARM_RADIAL_STEPS = 40
HOVER_WARM_RING_PAUSE_S = 0.05

# --- Weekday body themes (SYMBOLISM.md canon) -----------------------------------
# Display names per theme, body -> name (the weekday hover reads
# "Wednesday, Odin" in the norse theme). "planets" keeps the skin's own
# unit untouched. Saturday has no Norse god — the Sabbath stands in
# (canon). Art: assets/weekday/<theme>/<Entity>.png (files carry the
# ENTITY names; the two Norse diacritics fold to ASCII on disk).
WEEKDAY_THEME_NAMES = {
    # The owner's planet GLYPHS (☿ ♃ …) — same entities as "planets",
    # body-named files, planet display names.
    "planet_signs": {
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
    },
    # Display names carry the NATIVE script (owner 2026-07-12: "da
    # koristimo ta slova" — like the Japanese kanji and the Slavic
    # diacritics); the files keep plain ASCII stems via the explicit
    # overrides below.
    "greek": {
        "sun": "Helios (Ἥλιος)",
        "moon": "Selene (Σελήνη)",
        "mars": "Ares (Ἄρης)",
        "mercury": "Hermes (Ἑρμῆς)",
        "jupiter": "Zeus (Ζεύς)",
        "venus": "Aphrodite (Ἀφροδίτη)",
        "saturn": "Cronus (Κρόνος)",
    },
    "norse": {
        "sun": "Sól",
        "moon": "Máni",
        "mars": "Tyr (Týr)",
        "mercury": "Odin (Óðinn)",
        "jupiter": "Thor (Þórr)",
        "venus": "Freya (Freyja)",
        "saturn": "Loki",     # owner decision (FINAL.txt #2): Loki stands
                              # on Saturday — the bound trickster as
                              # Cronus' northern mirror
    },
    # Egyptian gods (owner art 2026-07-11, per the approved mapping):
    # Ra's Sunday, Khonsu the moon-walker, Montu the war falcon, Thoth
    # the scribe on the messenger's day, Amun the king of gods, Hathor
    # love and beauty, Osiris — harvest, patience and rebirth on
    # Saturn's day.
    "egypt": {
        "sun": "Ra",
        "moon": "Khonsu",
        "mars": "Montu",
        "mercury": "Thoth",
        "jupiter": "Amun",
        "venus": "Hathor",
        "saturn": "Osiris",
    },
    # Slavic gods (owner art 2026-07-12, per the approved mapping):
    # Dažbog the giving sun, Hors the night-walker, Svetovid's four
    # faces and white war-horse on Tuesday, Veles the horned trader-
    # trickster mirroring Odin and Hermes, Perun's oak and thunder at
    # noon, Mokoš spinning on the day her cult kept as Friday, Morana
    # — winter drowned each spring — on the arm of Renewal.
    "slavic": {
        "sun": "Dažbog",
        "moon": "Hors",
        "mars": "Svetovid",
        "mercury": "Veles",
        "jupiter": "Perun",
        "venus": "Mokoš",
        "saturn": "Morana",
    },
    # The seven metals of alchemy (owner art 2026-07-12): the classical
    # planet-metal correspondence — every medallion the same still life
    # of bars, nuggets and coiled wire, each wearing its own metal.
    "alchemy": {
        "sun": "Gold",
        "moon": "Silver",
        "mars": "Iron",
        "mercury": "Quicksilver",
        "jupiter": "Tin",
        "venus": "Copper",
        "saturn": "Lead",
    },
    # The Japanese week (owner art 2026-07-12, Gemini from our prompts):
    # the yōbi day names ARE the planetary week — sun, moon, then the
    # five Wu Xing element stars (fire=Mars, water=Mercury, wood=
    # Jupiter, metal=Venus, earth=Saturn). Display names KEEP the
    # kanji (owner instruction); files are folded ASCII overrides.
    "japan": {
        "sun": "Nichiyōbi (日曜日)",
        "moon": "Getsuyōbi (月曜日)",
        "mars": "Kayōbi (火曜日)",
        "mercury": "Suiyōbi (水曜日)",
        "jupiter": "Mokuyōbi (木曜日)",
        "venus": "Kin'yōbi (金曜日)",
        "saturn": "Doyōbi (土曜日)",
    },
    # NARRATIVE-FIRST remap (owner decision 2026-07-12): each religion
    # sits on the day its OWN canon points to, not its rest day —
    # Freemasonry's quest for Light under the All-Seeing Eye takes the
    # Sun (its Sunday DOUBLE = the rough vs the perfect ashlar);
    # Islam's calendar IS the moon (Quran 2:189); Buddhism wins the
    # war-day without weapons (Mara, Dhammapada 103); Christianity's
    # forgiving love lands on Venus's Friday (Good Friday, agape).
    "religion": {
        "sun": "Christianity",       # owner: replaces Zoroastrianism in
                                    # the basic seven (now an alternate)
        "moon": "Islam",
        "mars": "Buddhism",
        "mercury": "Taoism",
        "jupiter": "Hinduism",
        "venus": "Sikhism",
        "saturn": "Judaism",
    },
    # The ALTERNATE religion set — each on the day it fits best (canon
    # in SYMBOLISM.md; Egypt and Babylon per the owner's 2026-07-10 art:
    # Ra's Sunday, Ishtar IS Venus and Babylon invented the 7-day week).
    "religion_alt": {
        "sun": "Mithraism",     # owner decision 2026-07-12: replaces Egypt
                                # (a duplicate once the Egyptian gods became
                                # a full theme) — Sol Invictus IS dies Solis
        "moon": "Druidism",
        "mars": "Zoroastrianism",
        "mercury": "Shamanism",
        "jupiter": "Eleusinian Mysteries",
        "venus": "Babylon",
        "saturn": "Voodoo",
    },
    "profession": {
        "sun": "Ruler · Servant",   # the yin-yang center (owner spec
                                    # 2026-07-12): one figure, two faces
        "moon": "Physician",
        "mars": "Soldier",
        "mercury": "Merchant",
        "jupiter": "Priest",
        "venus": "Artist",
        "saturn": "Farmer",
    },
    # THE ANIMAL SOCIETIES (owner 2026-07-13) — three orders of order:
    # the pack ranks, the hive works by age (the career IS the clock),
    # the herd remembers (the leader is the one who holds the map).
    "wolf": {
        "sun": "Leader (Alpha) · Omega",     # the first and the last of the pack
                                    # — M at noon, Ω at midnight
        "moon": "Luna",
        "mars": "Hunter (Gamma)",
        "mercury": "Scout (Delta)",
        "jupiter": "Beta",
        "venus": "Mate",
        "saturn": "Elder",
    },
    "bee": {
        "sun": "Queen · Cleaner",   # the mother of the hive and the
                                    # day-one daughter at her birth cell
        "moon": "Nurse",
        "mars": "Guard",
        "mercury": "Scout",
        "jupiter": "Builder",
        "venus": "Drone",
        "saturn": "Forager",
    },
    "elephant": {
        "sun": "Matriarch · Memory",  # the ruler and the REMEMBERED
                                      # ruler — the bones that taught her
        "moon": "Allomother",
        "mars": "Musth",
        "mercury": "Caller",
        "jupiter": "Mentor",
        "venus": "Reunion",
        "saturn": "Elder",
    },
    # The SCRIPTURE family (owner 2026-07-14): three stained-glass sets.
    "bible": {
        "sun": "Ancient of Days · Son",
        "moon": "Mary",
        "mars": "David",
        "mercury": "Moses",
        "jupiter": "Solomon",
        "venus": "Adam & Eve",
        "saturn": "Joseph",
    },
    "bible2": {
        "sun": "Abraham · Isaac",
        "moon": "Jonah",
        "mars": "Samson",
        "mercury": "Jacob",
        "jupiter": "Noah",
        "venus": "Ruth",
        "saturn": "Job",
    },
    "bible_dark": {
        "sun": "Lucifer · Judas",
        "moon": "Lilith",
        "mars": "Goliath",
        "mercury": "The Serpent",
        "jupiter": "Herod",
        "venus": "Delilah",
        "saturn": "Cain",
    },
    # The DEEP SKY (owner 2026-07-14): star-chart medallions.
    "cosmos": {
        "sun": "Sun · Black Hole",
        "moon": "Nebula",
        "mars": "Supernova",
        "mercury": "Pulsar",
        "jupiter": "Galaxy",
        "venus": "Binary Stars",
        "saturn": "Comet",
    },
    # The Planets MEDALLION look — same entities, bronze art.
    "planets_art": {
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
    },
    # THE INNER WHEEL on the dial (owner 2026-07-14): the days ARE
    # their virtues / vices / hour-moods.
    "virtues": {
        "sun": "Justice · Humility",
        "moon": "Serenity",
        "mars": "Courage",
        "mercury": "Wisdom",
        "jupiter": "Generosity",
        "venus": "Love",
        "saturn": "Patience",
    },
    "sins": {
        "sun": "Pride · Servility",
        "moon": "Fear",
        "mars": "Wrath",
        "mercury": "Greed",
        "jupiter": "Excess",
        "venus": "Jealousy",
        "saturn": "Envy",
    },
    "moods": {
        "sun": "Glory · Awe",
        "moon": "Calm",
        "mars": "Zeal",
        "mercury": "Sorrow",
        "jupiter": "Joy",
        "venus": "Passion",
        "saturn": "Renewal",
    },
}

# File stems on disk: the display names folded to ASCII (Sól -> Sol,
# Dažbog -> dazbog); the owner's religion, planet-sign, egypt, slavic
# and alchemy art uses lowercase file names.
_ASCII_FOLD = str.maketrans("óážš", "oazs")
_LOWERCASE_THEMES = (
    "religion", "religion_alt", "planet_signs", "egypt", "slavic", "alchemy",
    "wolf",                        # the owner's wolf art uses lowercase stems
)
# Theme -> art folder under assets/weekday/: both religion sets share
# the ONE religion/ folder (all fourteen owner medallions together).
# FAMILY/VARIANT tree (owner restructure 2026-07-14): every theme dir
# is <family>/<variant> — related themes share a family (religion =
# primary Creeds + secondary Mysteries; planets = primary photos +
# signs glyphs + art medallions; bible = primary/secondary/dark), and
# a variant's colored arc is its SIBLING <family>/colored (owner DUAL
# FLATTEN 2026-07-19: every file, dual included, sits FLAT inside its
# variant — no dual/ subfolder anywhere; WHO a file is lives only in
# WEEKDAY_DUAL_FILES/WEEKDAY_PANTHEON, never in a folder name).
WEEKDAY_THEME_DIRS = {
    "planet_signs": "planets/signs",
    "greek": "greek/primary",
    "norse": "norse/primary",
    "egypt": "egypt/primary",
    "slavic": "slavic/primary",
    "alchemy": "alchemy/primary",
    "japan": "japan/primary",
    "religion": "religion/primary",
    "religion_alt": "religion/secondary",
    "profession": "profession/primary",
    "wolf": "wolf/primary",
    "bee": "bee/primary",
    "elephant": "elephant/primary",
    "bible": "bible/primary",
    "bible2": "bible/secondary",
    "bible_dark": "bible/dark",
    "cosmos": "cosmos/primary",
    "planets_art": "planets/art",
    # The emblem families live OUTSIDE assets/weekday/ — the relative
    # step-up reaches assets/emblem/ (owner 2026-07-14).
    "virtues": "../emblem/virtue",
    "sins": "../emblem/sin",
    "moods": "../emblem/mood",
}
WEEKDAY_THEME_FILES = {
    theme: {
        body: (
            name.translate(_ASCII_FOLD).lower()
            if theme in _LOWERCASE_THEMES
            else name.translate(_ASCII_FOLD)
        )
        for body, name in names.items()
    }
    for theme, names in WEEKDAY_THEME_NAMES.items()
}
# The dual center shows both faces in the hover title, but the owner's
# medallion file keeps the single name.
WEEKDAY_THEME_FILES["profession"]["sun"] = "Ruler"
WEEKDAY_THEME_FILES["wolf"]["sun"] = "alpha"
WEEKDAY_THEME_FILES["bee"]["sun"] = "Queen"
WEEKDAY_THEME_FILES["elephant"]["sun"] = "Matriarch"
# The metal reads Quicksilver, the owner's file keeps the element name.
WEEKDAY_THEME_FILES["alchemy"]["mercury"] = "mercury"
# The reworked Creeds and the wolf rank parentheticals keep plain stems.
WEEKDAY_THEME_FILES["religion_alt"]["jupiter"] = "eleusis"
WEEKDAY_THEME_FILES["wolf"]["mars"] = "hunter"
WEEKDAY_THEME_FILES["wolf"]["mercury"] = "scout"
# The Greek and Norse display names carry native-script parentheticals
# now — the files stay on the plain ASCII stems.
WEEKDAY_THEME_FILES["greek"] = {
    "sun": "Helios", "moon": "Selene", "mars": "Ares",
    "mercury": "Hermes", "jupiter": "Zeus", "venus": "Aphrodite",
    "saturn": "Cronus",
}
WEEKDAY_THEME_FILES["norse"] = {
    "sun": "Sol", "moon": "Mani", "mars": "Tyr",
    "mercury": "Odin", "jupiter": "Thor", "venus": "Freya",
    "saturn": "Loki",
}
# The Japanese display names carry kanji — the files are the romaji
# day names folded to plain ASCII (macrons and the apostrophe dropped).
WEEKDAY_THEME_FILES["japan"] = {
    "sun": "nichiyobi",
    "moon": "getsuyobi",
    "mars": "kayobi",
    "mercury": "suiyobi",
    "jupiter": "mokuyobi",
    "venus": "kinyobi",
    "saturn": "doyobi",
}
# The text-wave themes (owner 2026-07-14): explicit lowercase stems —
# the display names carry duals ("·") and compounds ("Adam & Eve").
WEEKDAY_THEME_FILES["bible"] = {
    "sun": "ancient_of_days", "moon": "mary", "mars": "david",
    "mercury": "moses", "jupiter": "solomon", "venus": "adam_and_eve",
    "saturn": "joseph",
}
WEEKDAY_THEME_FILES["bible2"] = {
    "sun": "abraham", "moon": "jonah", "mars": "samson",
    "mercury": "jacob", "jupiter": "noah", "venus": "ruth",
    "saturn": "job",
}
WEEKDAY_THEME_FILES["bible_dark"] = {
    "sun": "lucifer", "moon": "lilith", "mars": "goliath",
    "mercury": "serpent", "jupiter": "herod", "venus": "delilah",
    "saturn": "cain",
}
WEEKDAY_THEME_FILES["cosmos"] = {
    "sun": "sun", "moon": "nebula", "mars": "supernova",
    "mercury": "pulsar", "jupiter": "galaxy", "venus": "binary_stars",
    "saturn": "comet",
}
WEEKDAY_THEME_FILES["planets_art"] = {
    "sun": "sun", "moon": "moon", "mars": "mars",
    "mercury": "mercury", "jupiter": "jupiter", "venus": "venus",
    "saturn": "saturn",
}
# The emblem stems ARE the single names (Capitalized) — only the dual
# sun display titles need the override.
WEEKDAY_THEME_FILES["virtues"] = {
    "sun": "Justice", "moon": "Serenity", "mars": "Courage",
    "mercury": "Wisdom", "jupiter": "Generosity", "venus": "Love",
    "saturn": "Patience",
}
WEEKDAY_THEME_FILES["sins"] = {
    "sun": "Pride", "moon": "Fear", "mars": "Wrath",
    "mercury": "Greed", "jupiter": "Excess", "venus": "Jealousy",
    "saturn": "Envy",
}
WEEKDAY_THEME_FILES["moods"] = {
    "sun": "Glory", "moon": "Calm", "mars": "Zeal",
    "mercury": "Sorrow", "jupiter": "Joy", "venus": "Passion",
    "saturn": "Renewal",
}

# THE DUAL SUNDAY (owner 2026-07-12): every theme's center day has a
# SECOND face — the Servant to the Ruler. On the Compass and the
# Seasons both faces shine (Ruler north 12h, Servant south 24h — two
# persons, a union); the Trinity and the Prism keep ONE image (two
# persons in one body) with both faces in the hover. Paths are
# relative to WEEKDAY_ART_DIR without the extension; the metal themes'
# COLORED look inserts a colored/ folder before the file name (the
# profession Servant is a full eighth plate living beside the Ruler).
# The two FACE NAMES of each theme's Sunday (hover titles: the north
# face and the south face; the combined single-image legend keeps the
# theme's own dual display name).
WEEKDAY_DUAL_NAMES = {
    "planets": ("Sun", "Eclipsed Sun"),
    "planet_signs": ("Sun", "Eclipsed Sun"),
    "greek": ("Helios", "Phaethon"),
    "norse": ("Sól", "Skoll"),
    "egypt": ("Ra", "Afu-Ra"),
    "slavic": ("Young Dažbog", "Old Dažbog"),
    "alchemy": ("Gold", "Raw Ore"),
    "japan": ("Amaterasu", "Ama-no-Iwato"),
    "religion": ("Christianity", "Satanism"),
    "religion_alt": ("Mithraism", "Corax"),
    "profession": ("Ruler", "Servant"),
    "wolf": ("Alpha", "Omega"),
    "bee": ("Queen", "Cleaner"),
    "elephant": ("Matriarch", "Memory"),
    "bible": ("Ancient of Days", "Son"),
    "bible2": ("Abraham", "Isaac"),
    "bible_dark": ("Lucifer", "Judas"),
    "cosmos": ("Sun", "Black Hole"),
    "planets_art": ("Sun", "Eclipsed Sun"),
    "virtues": ("Justice", "Humility"),
    "sins": ("Pride", "Servility"),
    "moods": ("Glory", "Awe"),
}
# Dual paths live FLAT inside the theme's variant dir (owner DUAL
# FLATTEN 2026-07-19: the dual/ folder carried zero semantic weight at
# runtime — the config table already IS the identity, so the folder
# only added a navigation step); the colored dual is the same path
# with the variant segment swapped to colored/ (owner restructure
# 2026-07-14, unaffected by the flatten — the swap only ever touched
# the "primary"/"colored" segment).
WEEKDAY_DUAL_FILES = {
    "planets": "planets/primary/sun_eclipse",
    "planet_signs": "planets/signs/sun_eclipse",
    "greek": "greek/primary/Phaethon",
    "norse": "norse/primary/Skoll",
    "egypt": "egypt/primary/afu_ra",
    "slavic": "slavic/primary/dazbog_old",
    "alchemy": "alchemy/primary/ore",
    "japan": "japan/primary/ama_no_iwato",
    "religion": "religion/primary/satanism",
    "religion_alt": "religion/secondary/corax",
    # profession's flat "Servant" stem collides with an already-flat,
    # unreferenced orphan file the owner has separately at
    # profession/primary/Servant.png (different art, different hash —
    # a true collision found flattening this round) — config-side
    # rename to "Servant_dual" resolves it without touching the
    # unrelated orphan (Rule #3: never delete without the owner's own
    # look).
    "profession": "profession/primary/Servant_dual",
    "wolf": "wolf/primary/omega",
    "bee": "bee/primary/Cleaner",
    "elephant": "elephant/primary/Memory",
    "bible": "bible/primary/son_servant",
    "bible2": "bible/secondary/isaac",
    "bible_dark": "bible/dark/judas",
    "cosmos": "cosmos/primary/black_hole",
    "planets_art": "planets/art/sun_eclipse",
    "virtues": "../emblem/virtue/Humility",
    "sins": "../emblem/sin/Servility",
    "moods": "../emblem/mood/Awe",
}


def weekday_theme_body_art(theme: str, body: str) -> Path:
    """One theme's plate for one weekday body (bronze / canon file) —
    moved here from `app.encyclopedia._theme_body_art` (R5 MENU REWORK,
    Rule #5): the Encyclopedia gallery AND the new Pointer/Slot Theme
    picker windows both need a representative preview per theme, so the
    resolution lives ONCE in config and both readers import it."""
    if theme == "planets":
        return WEEKDAY_ART_DIR / "planets" / "primary" / f"{body}.png"
    return (
        WEEKDAY_ART_DIR / WEEKDAY_THEME_DIRS[theme]
        / f"{WEEKDAY_THEME_FILES[theme][body]}.png"
    )

# The metal SWAP for the bronze-plate art (owner insight 2026-07-12:
# the medallions mix bronze details with GRAY stone and engravings —
# only the warm bronze pixels may change, the gray stays). Detection =
# a warm-hue window with soft edges + a saturation ramp; per-target
# hue/saturation/value mapping. Bronze = the art as drawn (no swap).
METAL_SWAP_HUE_WINDOW = (10.0, 60.0)   # degrees, warm bronze range
METAL_SWAP_HUE_SOFT = 8.0              # soft edge width outside the window
METAL_SWAP_SAT_RAMP = (0.10, 0.28)     # smoothstep: below gray, above bronze
METAL_SWAP_TARGETS = {
    "gold": {"hue": 48.0, "sat_mul": 1.25, "val_mul": 1.25},
    "silver": {"hue": 220.0, "sat_mul": 0.06, "val_mul": 1.22},
}
# Bronze ring LETTERS are derived AT LOAD from the silver ones
# (owner 2026-07-19, `render.assets.letter_metal_file` — retired the
# pre-rendered files). Final recipe = a STRAIGHT multiply with classic
# bronze, no brightness/contrast change (owner verdict revised on the
# live dial 2026-07-12: the darkened candidates sat darker than the
# bronze medallions — candidate C matches).
BRONZE_LETTER_TINT = "#CD7F32"
BRONZE_LETTER_BRIGHTNESS = 1.0
BRONZE_LETTER_CONTRAST = 1.0

# ECLIPSE DISPLAY (owner 2026-07-18, ROADMAP 15h item 11 — refines the
# sealed glow-metal triad; the Deep Time pack's eclipse catalog is the
# OPTIONAL data source, see data/deep_time.md — absent it, none of this
# ever draws). A SOLAR eclipse turns the Earth marker's OWN event glow
# RED (instead of GLOW_SUN_COLOR) and swaps its art to the Planets
# theme's Eclipsed-Sun dual; a LUNAR eclipse turns the Moon marker's
# glow the blood-moon COPPER (the bronze metal tint, reused verbatim —
# physically true, not a new color) and darkens the disc with the same
# tint. Both ride the EXISTING relocation-to-ring-band mechanic
# (GLOW_RING_RADIUS_FRACTION) — only the color/art/strength differ.
GLOW_ECLIPSE_SOLAR_COLOR = "#FF3B30"       # red — the eclipsed Sun's glow
# The "ring of fire" (owner decree 2026-07-19, fix round C): an ANNULAR
# solar eclipse keeps the black-sun art but its glow shifts to a hotter
# orange-red than the plain total/partial red, so the two read distinct.
GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR = "#FF7A1A"
GLOW_ECLIPSE_LUNAR_COLOR = BRONZE_LETTER_TINT  # bronze copper — blood moon
# INVISIBLE-FROM-HERE muting (owner verdict "može", fix round E,
# 2026-07-19): an eclipse the observer cannot actually see (below the
# horizon, or — solar only — too far from the ground track) still
# shows — the event is real — but its glow swaps to a desaturated
# silver at HALF strength instead of its normal color, and the hover
# names the reason. The art swap/moon-darkening stay untouched (the
# type-driven state is a catalog fact, not an observer fact).
GLOW_ECLIPSE_INVISIBLE_COLOR = "#8A9096"       # desaturated silver-gray
ECLIPSE_INVISIBLE_STRENGTH_FACTOR = 0.5
ECLIPSE_SOLAR_ART = (
    WEEKDAY_ART_DIR / "planets" / "primary" / "sun_eclipse.png"
)                                            # source-mapped by paths.art_file
# LUNAR ECLIPSE OPTION C (owner sealed 2026-07-18): the blackened moon +
# bronze glow gains a thin TURQUOISE FRINGE at the glow's OUTER edge —
# the real ozone-band color at the umbra's rim during totality. A
# turquoise ring, not a flat teal, so it reads distinctly against the
# warm bronze on the dark dial.
ECLIPSE_LUNAR_FRINGE_COLOR = "#40E0D0"
ECLIPSE_LUNAR_FRINGE_STOP = 0.92              # gradient position (0..1 of halo radius)
ECLIPSE_LUNAR_FRINGE_HALF_WIDTH = 0.05        # ring thickness either side of the stop
ECLIPSE_LUNAR_FRINGE_ALPHA = 0.85             # peak alpha before the magnitude scale
# Glow STRENGTH scales with the catalog MAGNITUDE (owner idea, ROADMAP
# 15h item 11): magnitude 0 (grazing partial) maps to the MIN fraction
# of the normal glow alpha, magnitude at/above MAX (a comfortable
# totality margin) maps to the full alpha — linear between, clamped
# outside (Rule #4: config-driven, no magic numbers at the call site).
# Fix round C (owner decree 2026-07-19) narrows this mapping to ONE
# remaining caller — the SOLAR PARTIAL state — every other state's glow
# strength is now a fixed TYPE constant below.
ECLIPSE_MAGNITUDE_MIN = 0.0
ECLIPSE_MAGNITUDE_MAX = 1.2
ECLIPSE_GLOW_STRENGTH_MIN = 0.4
ECLIPSE_GLOW_STRENGTH_MAX = 1.0

# THE ECLIPSE STATE TABLE (owner decree 2026-07-19, fix round C — the
# lunar "translucent bronze wash" complaint: the old darkening scaled a
# translucent overlay's ALPHA by magnitude, so a bright moon under a
# weak wash still read as "a visible moon shining bronze". The fix: the
# catalog TYPE (ground-truthed from Database/deep_time.sqlite's actual
# rows — solar {partial, annular, total, hybrid}, lunar {partial,
# penumbral, total}) selects ONE fixed render STATE. The state alone
# sets the disc BRIGHTNESS (never translucency, never magnitude); it
# also sets the glow STRENGTH for every state except "solar_partial",
# which keeps the original magnitude-linear mapping
# (`render.layers.eclipse_glow_strength`) — the owner's one named
# exception ("SOLAR partial: art + glow scaled by magnitude").
#
# `hybrid` (annular-total transitional, ~3.2k of ~70k solar rows) has no
# dedicated owner state — it is mapped to "solar_total" (not the
# unknown-type fallback): a hybrid eclipse shows true totality along
# most of its ground track, the closer of the two sealed states.
ECLIPSE_TYPE_STATE = {
    ("lunar", "total"): "lunar_total",
    ("lunar", "partial"): "lunar_partial",
    ("lunar", "penumbral"): "lunar_penumbral",
    ("solar", "total"): "solar_total",
    ("solar", "hybrid"): "solar_total",       # nearest sealed state, see above
    ("solar", "annular"): "solar_annular",
    ("solar", "partial"): "solar_partial",
}
# Unknown/missing catalog type (should not occur — the generator only
# ever writes the vocabulary above) documented fallback: the kind's
# PARTIAL state — a plausible middle ground, never a crash (Rule #1).
ECLIPSE_STATE_FALLBACK = {"solar": "solar_partial", "lunar": "lunar_partial"}

# Moon-disc BRIGHTNESS as a fraction of full value (0..1) — a true
# multiply-darken of the rendered disc, not an alpha wash (owner: "DARKEN
# means BRIGHTNESS DOWN... unmistakably an eclipse"). Solar states are
# absent — the solar disc art (the eclipsed-Sun dual) never darkens,
# only its glow color/strength change.
ECLIPSE_STATE_MOON_BRIGHTNESS = {
    "lunar_total": 0.07,       # near-black disc
    "lunar_partial": 0.18,
    "lunar_penumbral": 0.60,   # real penumbral eclipses are barely visible
}
# BLOOD MOON DISC (owner verdict "može", fix round E, 2026-07-19): the
# TOTAL state's multiply-darken uses this deep copper-red instead of
# neutral gray — `render.layers.tinted_gray`'s black->tint->white
# tritone at `ECLIPSE_STATE_MOON_BRIGHTNESS["lunar_total"]` (~7%) reads
# dark AND visibly red, the real "blood moon" look; partial/penumbral
# keep the plain neutral gray (only totality dims the WHOLE face enough
# for a color cast to read honestly).
ECLIPSE_TOTAL_MOON_TINT = "#8B2E12"
# Fixed glow-strength fraction per state (0..1, same scale as
# `eclipse_glow_strength`'s return). "solar_partial" is intentionally
# absent — it keeps the magnitude-linear mapping instead.
ECLIPSE_STATE_GLOW_STRENGTH = {
    "lunar_total": 1.0,
    "lunar_partial": 0.6,
    "lunar_penumbral": 0.25,
    "solar_total": 1.0,
    "solar_annular": 1.0,
}
# The turquoise ozone fringe (Option C) reads only where totality/near-
# totality actually darkens the sky rim — real penumbral eclipses show
# no such band, so the fringe is withheld there (owner spec, this round).
ECLIPSE_STATE_FRINGE = {
    "lunar_total": True,
    "lunar_partial": True,
    "lunar_penumbral": False,
}

# The ECLIPSES ENCYCLOPEDIA category emblems (fix round F, owner order
# 2026-07-19): one rose-window night-window medallion per category we
# distinguish, at assets/eclipse/<Stem>.png — graceful-absent until
# PromptPainter generates them (research/prompts/eclipse/eclipse_prompts.md).
# The SAME emblem backs the chapter page (app.encyclopedia) AND the
# eclipse-window hover badge on the Earth/Moon card (render.compositor).
ECLIPSE_ART_DIR = paths.assets_dir() / "eclipse"
# (kind, type) -> category emblem stem. `hybrid` keeps its OWN chapter
# and emblem here even though the RENDER state table folds it into
# solar_total — the reader still gets the distinct hybrid page; an
# unknown/missing type resolves to None (no badge, graceful — the
# render state table already documents its own fallback).
ECLIPSE_TYPE_EMBLEM = {
    ("solar", "total"): "Solar_Total",
    ("solar", "annular"): "Solar_Annular",
    ("solar", "partial"): "Solar_Partial",
    ("solar", "hybrid"): "Solar_Hybrid",
    ("lunar", "total"): "Lunar_Total",
    ("lunar", "partial"): "Lunar_Partial",
    ("lunar", "penumbral"): "Lunar_Penumbral",
}

# ONE menu/encyclopedia/settings title per theme (English; translated
# through the ui/ overlay at display) — every theme list iterates this.
WEEKDAY_THEME_TITLES = {
    "planets": "Planets",
    "planet_signs": "Planet signs",
    "greek": "Greek gods",
    "norse": "Norse gods",
    "egypt": "Egyptian gods",
    "slavic": "Slavic gods",
    "alchemy": "Alchemy",
    "japan": "Japanese week",
    # Owner renames 2026-07-13: masonry and voodoo are creeds and
    # mysteries, not strictly religions — and "Religions II" is gone.
    "religion": "Creeds",
    "religion_alt": "Ancient religions",
    "profession": "Professions",
    "wolf": "Wolf Pack",
    "bee": "Bee Hive",
    "elephant": "Elephant Herd",
    # The text-wave themes (owner 2026-07-14). planets_art carries NO
    # title on purpose: it nests as the Planets "Art" option in the
    # menu and rides the Planets encyclopedia topic as a look.
    "bible": "Bible",
    "bible2": "Bible II",
    "bible_dark": "Bible Dark",
    "cosmos": "Cosmos",
    # The Inner Wheel dial themes; their ENCYCLOPEDIA topics stay the
    # emblem pages (the later family pass overwrites the weekday
    # topics built from these titles — deliberate).
    "virtues": "Virtues",
    "sins": "Sins",
    "moods": "Moods",
}

# The Weekday submenu's TOP entries (owner 2026-07-18): rendered FIRST,
# flat, ABOVE the kinship groups below — Planets is the DEFAULT theme
# and no longer hides inside Arcana. Nests Image/Sign plain plus the
# metal-capable Art look (planet_signs stays its own theme underneath;
# planets_art carries its Gold/Bronze/Silver dropdown via METAL_THEMES).
WEEKDAY_MENU_TOP = ("planets",)

# The Weekday submenu GROUPS (owner menu rework 2026-07-13): kinship
# submenus below the top entries. The Inner Wheel (Virtues/Sins/Moods)
# joins once those themes gain their dial texts.
WEEKDAY_MENU_GROUPS = (
    ("Ancient Gods", ("egypt", "greek", "norse", "slavic")),
    ("Society", ("profession", "religion", "religion_alt")),
    # The Scripture family (owner 2026-07-14).
    ("Scripture", ("bible", "bible2", "bible_dark")),
    ("Animals", ("wolf", "elephant", "bee")),
    # The emblem families on the dial (owner 2026-07-14).
    ("The Inner Wheel", ("virtues", "sins", "moods")),
    # Planets moved to WEEKDAY_MENU_TOP (owner 2026-07-18) — Arcana now
    # holds only the remaining three.
    ("Arcana", ("alchemy", "japan", "cosmos")),
)

DEFAULT_SKIN = SkinDefinition(
    z_order=(
        "background",
        "star",
        "weekday_set",
        "ring",
        "year_marker",
        "hands",
    ),                                  # the star's top tip IS the noon pointer
    background=BackgroundSpec(
        # Procedural Umbra (owner spec/art): drawn at runtime so the
        # contrast setting can reshade it.
        base_asset=None,
        # Owner defaults 2026-07-12: sunlight 36%, twilight 12%.
        day_alpha=0.36,
        twilight_alpha=0.12,
        # TWO independent radii for fine tuning (fractions of the dial
        # radius; the ring art's inner edge sits at 0.858):
        umbra_radius_fraction=0.90,     # the gray wheel
        aura_radius_fraction=0.90,      # the colored wedges
    ),
    star=StarSpec(
        day_alpha=1.0,                  # full opacity (owner default 2026-07-12)
        twilight_alpha=0.55,
        border_alpha=0.85,              # colored outlines run the full circle
        border_width_fraction=0.008,
        radius_fraction=0.86,           # star tips touch the ring's inner edge too
    ),
    ring=RingSpec(
        # A face placeholder only — the controller's build_skin ALWAYS
        # overlays the chosen ring preset card (face + letters + letter
        # art) from Database/ring_presets.json at build time.
        asset=RING_FACE_DIR / "domy.png",
        fill="#4A4E57",
        text_color="#F0F0F0",
        letter_color="#E8B84B",
        width_fraction=0.16,
        letters={12: "M", 20: "Y", 0: "Ω", 4: "D"},
    ),
    weekday_set=WeekdaySpec(
        bodies={name: WEEKDAY_ART_DIR / "planets" / "primary" / f"{name}.png" for name in (
            "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"
        )},
        body_names={
            "sun": "Sun",
            "moon": "Moon",
            "mars": "Mars",
            "mercury": "Mercury",
            "jupiter": "Jupiter",
            "venus": "Venus",
            "saturn": "Saturn",
        },
        body_colors={
            "sun": "#FFC838",
            "jupiter": "#E8C25A",
            "mars": "#C96A3D",
            "venus": "#E1934B",
            "mercury": "#9B8F86",
            "moon": "#C9CDD4",
            "saturn": "#D4B27A",
        },
        display_mode="ghost",           # owner default; "center_only" selectable
        ghost_opacity=0.15,
        center_scale=0.132,             # center_only showcase ONLY (owner
                                        # 2026-07-18: the hexa/trio center
                                        # matches the diamond bodies —
                                        # layers.weekday_body_size; this
                                        # retired the "Sun is 1.20x" note)
        diamond_scale=0.11,
        orbit_fraction=0.38,
    ),
    year_marker=YearMarkerSpec(
        # Both styles bundled; the earth_style display choice picks one.
        variants={
            f"{style}_{continent}_{phase}": paths.assets_dir() / "earth"
            / f"earth_{style}_{continent}_{phase}.png"
            for style in ("clean", "atmo")
            for continent in _CONTINENTS
            for phase in ("day", "night")
        },
        default_variant="europe",
        day_color="#4B86C9",
        night_color="#20344F",
        # Owner spec: the Earth's outer edge TOUCHES the ring's inner
        # edge (0.75 + 0.11 = 0.86 = the disc radius), same size as the
        # weekday planets.
        orbit_fraction=0.75,
        scale=0.11,
        moon_asset=WEEKDAY_ART_DIR / "planets" / "primary" / "moon.png",
        moon_lit_color="#E8E4D8",
        moon_dark_color="#2A2D36",
        moon_shadow_alpha=0.82,
        moon_orbit_fraction=0.75,       # rides the same rim as the Earth
        moon_scale=0.08,                # ~72% of the Earth marker (owner spec)
    ),
    hands=HandsSpec(
        # A PLACEHOLDER only — build_skin ALWAYS resolves the chosen
        # hand pack (assets/hands/<pack>/ or a user pack) into a full
        # HandsSpec; these are the CLASSIC pack's values (the owner's
        # PNG exports, every pivot 17 px above the bottom).
        hour=HandSpec(
            asset=paths.assets_dir() / "hands" / "classic" / "hours.png",
            natural_height=246, pivot_y=17,
        ),
        minute=HandSpec(
            asset=paths.assets_dir() / "hands" / "classic" / "minutes.png",
            natural_height=295, pivot_y=17,
        ),
        second=HandSpec(
            asset=paths.assets_dir() / "hands" / "classic" / "seconds.png",
            natural_height=306, pivot_y=17,
        ),
        minute_reach_fraction=HAND_MINUTE_REACH_FRACTION,
        second_reach_fraction=HAND_SECOND_REACH_FRACTION,
    ),
)

# --- Pole light/dark emoji windows (ROADMAP 15h item 10, fix round A
# owner reminder 2026-07-19) -----------------------------------------------------
# The North/South Pole rows in the location picker/Quick-Jump submenu
# carry a season-dependent emoji switching between POLAR DAY and POLAR
# NIGHT — owner: NOT the sun emoji used elsewhere, 🔆 for the light
# half and 🌑 for the dark half. Computed from a simple CALENDAR date
# window (the pole is lit while the sun's declination sits on ITS
# hemisphere, roughly the ±6° civil-twilight boundary) — no astronomy
# call needed, just a date-in-range check. (month, day) pairs, inclusive
# both ends; the North window sits wholly inside one calendar year, the
# South window WRAPS across the year boundary.
POLE_LIGHT_WINDOW = {
    "north": ((3, 3), (10, 9)),      # Mar 3 - Oct 9
    "south": ((9, 7), (4, 5)),       # Sep 7 - Apr 5 (wraps New Year's)
}
# Fix round E (owner verdict 2026-07-19, slika 6, angry): 🔆/🌑 violate
# the owner's standing "no sun/moon emojis" law. NEUTRAL interim glyphs
# until dedicated SVG icons land (owner icon list, 2026-07-19) — a
# plain filled/empty circle carries the light/dark contrast without
# borrowing a sun or moon pictograph.
POLE_LIGHT_EMOJI = "⚪"
POLE_DARK_EMOJI = "⚫"
POLE_COLD_EMOJI = "❄"                # left-side glyph, both poles
GREENWICH_EMOJI = "🌐"                # sealed owner pick


def pole_is_light(pole: str, on_date: date) -> bool:
    """Whether `pole` ("north"/"south") sits in its LIT half of the
    year on `on_date` — the `POLE_LIGHT_WINDOW` calendar approximation
    (no astronomy call). The South window wraps the year boundary
    (Sep 7 -> Dec 31 -> Apr 5)."""
    start, end = POLE_LIGHT_WINDOW[pole]
    today = (on_date.month, on_date.day)
    if start <= end:
        return start <= today <= end
    return today >= start or today <= end


def pole_emoji(pole: str, on_date: date) -> str:
    """The season-dependent RIGHT-side emoji for one pole's row —
    `POLE_LIGHT_EMOJI` through the lit half, `POLE_DARK_EMOJI` through
    the dark half, by `pole_is_light`."""
    return POLE_LIGHT_EMOJI if pole_is_light(pole, on_date) else POLE_DARK_EMOJI


def pole_icon_name(pole: str, on_date: date) -> str:
    """The `ICON_FILES` key for one pole's row (TASK 4, MASON/ICONS
    round) — "light"/"dark" by the SAME `pole_is_light` split
    `pole_emoji` already uses, so the icon and its documented emoji
    fallback never disagree."""
    return "light" if pole_is_light(pole, on_date) else "dark"
