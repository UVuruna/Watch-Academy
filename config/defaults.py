"""Developer tunables — values a developer may adjust while tuning the app.

Everything here is read-only at runtime. User-changeable state (window
position, chosen city, chosen skin) lives in the user settings file owned
by app/settings_store.py.
"""

import re
from datetime import date
from pathlib import Path
from typing import NamedTuple

from config import constants, palette, paths
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
ICON_DIR = paths.assets_dir() / "instrument" / "icons"
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
RING_FACE_DIR = paths.assets_dir() / "instrument" / "ring"

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
RING_LETTER_ART_DIR = paths.assets_dir() / "instrument" / "ring" / "letters"
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
# further out — decorative inscription, not the primary Dollar seats.
# ONE SHARED RADIUS (MOTO-FIX round): the first round's design had both
# mottos' pinned letters land on the SAME angle (O at noon, S at 16h),
# needing two concentric radii to coexist; the corrected layout puts
# ANNUIT COEPTIS over the TOP and NOVUS ORDO SECLORUM under the BOTTOM
# instead — angularly DISJOINT arcs that never collide, so both now
# draw at this one radius (`core.motto.md`'s Design Decisions).
RING_MOTTO_SIZE = 0.0375             # motto letter height, of the dial
                                     # diameter — half RING_LETTER_ART_SCALE
                                     # (decorative, smaller than the six
                                     # primary banknote letters)
# The WORD-HOVER band (owner 2026-07-27, "HOVER tekst osim na slova
# treba i na reči"): how far above/below the motto radius (fraction of
# the dial RADIUS) a hover still answers as an arc WORD — the motto
# letter height is 2*RING_MOTTO_SIZE of the radius (0.075), so ±0.05
# covers the glyphs with a little air.
RING_MOTTO_HOVER_HALF_FRACTION = 0.05
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
# (figure, article) pair. Colored variants live under the register's
# own <register>/colored/ child mirroring the bronze stems (tree law
# 2026-07-26 — identical for pantheon and primary alike).
WEEKDAY_PANTHEON = {
    "greek": {
        "articles": "greek_pantheon",
        "files": {
            "sun": ("greek/pantheon/bronze/Zeus", "greek/primary/bronze/Zeus"),
            "moon": ("greek/pantheon/bronze/Poseidon",),
            "mars": ("greek/pantheon/bronze/Artemis",),
            "mercury": ("greek/pantheon/bronze/Athena",),
            "jupiter": ("greek/pantheon/bronze/Apollo",),
            "venus": ("greek/pantheon/bronze/Hera",),
            "saturn": ("greek/pantheon/bronze/Demeter",),
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
        "dual": ("greek/pantheon/bronze/Hades",),
        "dual_names": ("Zeus", "Hades"),
    },
    "norse": {
        "articles": "norse_pantheon",
        "files": {
            "sun": ("norse/pantheon/bronze/Odin",),
            "moon": ("norse/pantheon/bronze/Hel",),
            "mars": ("norse/primary/bronze/Thor",),
            "mercury": ("norse/primary/bronze/Loki",),
            "jupiter": ("norse/primary/bronze/Tyr",),
            "venus": ("norse/pantheon/bronze/Frigg",),
            "saturn": ("norse/pantheon/bronze/Freyr",),
        },
        "names": {
            "sun": "Odin (\u00d3\u00f0inn)", "moon": "Hel",
            "mars": "Thor (\u00de\u00f3rr)", "mercury": "Loki",
            "jupiter": "Tyr (T\u00fdr)", "venus": "Frigg",
            "saturn": "Freyr",
        },
        "dual": ("norse/primary/bronze/Odin",),
        "dual_names": ("Odin", "The Wanderer"),
    },
    "egypt": {
        "articles": "egypt_pantheon",
        "files": {
            "sun": ("egypt/primary/bronze/Ra",),
            "moon": ("egypt/pantheon/bronze/Isis",),
            "mars": ("egypt/pantheon/bronze/Horus",),
            "mercury": ("egypt/primary/bronze/Thoth",),
            "jupiter": ("egypt/pantheon/bronze/Anubis",),
            "venus": ("egypt/pantheon/bronze/Bastet",),
            "saturn": ("egypt/primary/bronze/Osiris",),
        },
        "names": {
            "sun": "Ra", "moon": "Isis", "mars": "Horus",
            "mercury": "Thoth", "jupiter": "Anubis",
            "venus": "Bastet", "saturn": "Osiris",
        },
        "dual": ("egypt/primary/bronze/Afu_Ra",),
        "dual_names": ("Ra", "Afu-Ra"),
    },
    "slavic": {
        "articles": "slavic_pantheon",
        "files": {
            "sun": ("slavic/primary/bronze/Perun",),
            "moon": ("slavic/primary/bronze/Mokos",),
            "mars": ("slavic/primary/bronze/Svetovid",),
            "mercury": ("slavic/pantheon/bronze/Svarog",),
            "jupiter": ("slavic/primary/bronze/Dazbog",),
            "venus": ("slavic/pantheon/bronze/Lada",),
            "saturn": ("slavic/primary/bronze/Morana",),
        },
        "names": {
            "sun": "Perun", "moon": "Moko\u0161", "mars": "Svetovid",
            "mercury": "Svarog", "jupiter": "Da\u017ebog",
            "venus": "Lada", "saturn": "Morana",
        },
        "dual": ("slavic/primary/bronze/Veles",),
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
        path = weekday_art(f"{rel}.png")
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

# THE CONTINENTS weekday theme (owner-sealed matrix 2026-07-21). The six
# weekday bodies ride the six continents — the dial's OWN Earth-marker
# faces are the theme's bodies (owner exception to the one-image-one-
# place law, sealed). Body -> earth REGION stem (Sunday's "sun" is the
# Ruler pole; the Servant pole is the dual, below). Column assignments
# straight from the sealed matrix: Moon/Oceania, Mars/Europe, Mercury/
# Asia, Jupiter/Africa, Venus/South America, Saturn/North America.
EARTH_ART_DIR = paths.assets_dir() / "celestial" / "earth"
CONTINENTS_REGIONS = {
    "moon": "oceania",
    "mars": "europe",
    "mercury": "asia",
    "jupiter": "africa",
    "venus": "south_america",
    "saturn": "north_america",
    "sun": "south_pole",          # Antarctica — the Ruler face
}
CONTINENTS_DUAL_REGION = "north_pole"   # the Arctic — the Servant face
# The still frame the Encyclopedia gallery/theme picker previews with,
# and the plate baked into the skin as a fallback (the live dial
# overrides both axes at render — see continents_body_art): the owner's
# atmosphere globes lit by day.
CONTINENTS_PREVIEW_STYLE = "atmo"
# THE CONTINENTS TITLE IMAGE (owner-sealed matrix 2026-07-21): the flat
# world map — the whole Earth seen at once, the week's field before it is
# walked. Copied from UV/earth map.jpg into the earth family as a PNG
# (setup/convert step), the canonical home for the theme's own art; the
# Encyclopedia topic uses it for both the gallery card and the title page.
CONTINENTS_TITLE_IMAGE = EARTH_ART_DIR / "world.png"


def earth_face_art(style: str, region: str, phase: str = "day") -> Path:
    """One Earth-marker face on disk — the SAME `{style}_{region}_
    {phase}` naming the YearMarkerSpec variants use (Rule #5), reused as
    the Continents theme's body art (owner exception, sealed 2026-07-21).
    Pure path construction; existence is the caller's concern."""
    return EARTH_ART_DIR / f"earth_{style}_{region}_{phase}.png"


def continents_body_art(body: str, earth_style: str, is_daylight: bool) -> Path:
    """The live Continents body plate for one weekday `body` — the
    earth face for its region in the user's `earth_style` (atmo/clean,
    one setting for the whole instrument) at the sky's current phase
    (`is_daylight` from the render tick — the SAME sun-elevation law the
    Earth marker already computes, never recomputed here). The Sunday
    center resolves through "sun" -> south_pole; the Arctic Servant uses
    `continents_dual_art`."""
    region = CONTINENTS_REGIONS[body]
    return earth_face_art(earth_style, region, "day" if is_daylight else "night")


def continents_dual_art(earth_style: str, is_daylight: bool) -> Path:
    """The live Continents SERVANT plate — the Arctic (north_pole) face,
    the Antarctic Ruler's eternal antiphase mirror — in the user's
    `earth_style` at the sky's current phase (same law as
    `continents_body_art`)."""
    return earth_face_art(
        earth_style, CONTINENTS_DUAL_REGION, "day" if is_daylight else "night"
    )

# The WORKING SET (owner 2026-07-15): originals ship at full
# resolution; the dial reads a once-per-file DOWNSCALED copy instead —
# quality and performance both, for a little disk. Ceilings per assets
# subtree, from the worst case the dial can ask for (1440 dial ×
# 200% element scale × 200% hover enlarge ≈ 800 px for the round
# bodies; the slot seats with their 150% pointer factor ≈ 1200 px).
# Sources at or under the ceiling stay as they are.
WORKING_SET_CEILINGS = {
    "celestial/earth": 800,
    "weeks": 800,
    "calendars": 1200,
    "archetypes": 1200,
    "celestial/seasons": 1200,
}

# THE LEAD LINE's width, a fraction of the dial radius — the twin of
# `palette.ARM_OUTLINE`, worn by every drawn arm and polygon face
# (owner's correction round 2026-07-29).
ARM_OUTLINE_WIDTH = 0.0035               # of the dial radius






# --- Calendar pointer (owner 2026-07-16, CANON §The Dozen) ---------------------
# The twelve wedges are Calendar-fixed — they never ride the solar
# rotation — but otherwise they ARE the standard Aura and wear its
# opacities (`BackgroundSpec.day_alpha` / `twilight_alpha`) under the
# day/night law like every other pointer. Both of the Calendar's own
# opacity constants are therefore gone: `CALENDAR_WEDGE_LIT_DELTA` with
# the lit-wedge feature (owner decree 2026-07-29) and the flat
# `CALENDAR_WEDGE_ALPHA` with its always-full-circle path (owner
# correction 2026-07-29 — the daylight switch must reach the
# background).
CALENDAR_WEDGE_RADIUS_FRACTION = 0.90  # wedge reach, of the dial radius
# The Earth DAY-ARROW on the Almanac wheel (owner 2026-07-16: "one tick
# ≈ one day"): a small triangle at the marker's exact tick, pointing
# from inside the dial OUTWARD toward the ring so the ring reads today's
# date to the day. Drawn procedurally (the ring numeral arrow is the
# visual reference).
CALENDAR_ARROW_TIP_FRACTION = 0.845  # arrow tip radius (just inside the ticks)
CALENDAR_ARROW_LENGTH_FRACTION = 0.06  # tip-to-base length, of the dial radius
CALENDAR_ARROW_HALF_DEG = 2.4        # half-width of the base, in dial degrees

# --- Calendar-pointer 12-sets: the Slavic Months (owner-sealed R7b 2026-07-21) -
# The DESIGN ZODIAC law (UV/DESIGN/DESIGN INSTRUCTIONS.txt): "Zodiac i
# sve što ima 12 TREBA da bude moguće da se AKTIVIRA na CALENDAR POINTER
# (TO MU JE DEFAULT)" — any twelve-fold set may MOUNT on the Calendar
# pointer as twelve marks, one per two-hour wedge, at 60-70% of the dial
# radius (so they clear the Earth/Moon at the rim and the subdials at the
# centre). This table REGISTERS the first such set beyond the zodiac
# signs and Chinese animals the pointer already reads: the twelve
# Croatian months as PROPER NOUNS with the English gloss, one per
# Gregorian month (`gregorian`, 1..12 — the Almanac wheel already maps
# month->wedge via core.year_wheel.almanac_month_index). `stem` is the
# ASCII plate stem under MONTHS_ART_DIR (assets/months/<stem>.png,
# graceful-absent — the mount draws the Croatian name instead until the
# owner's prompt sheet lands, `render.layers.calendar_mount_entries`).
# The MOUNT ITSELF (R9a round, 2026-07-21): drawing the twelve marks at
# CALENDAR_MOUNT_RADIUS_FRACTION and the Settings picker for WHICH
# 12-set mounts are both live now (render.layers.BackgroundLayer,
# app.design_window's Pointer tab) — see config/___config.md and
# app/encyclopedia.md for the Encyclopedia side.
SLAVIC_MONTHS = (
    # (croatian proper noun, english gloss, ascii stem, gregorian month)
    ("Siječanj", "the Month of Felling", "Sijecanj", 1),
    ("Veljača", "the Turning Month", "Veljaca", 2),
    ("Ožujak", "the Lying Month", "Ozujak", 3),
    ("Travanj", "the Grass Month", "Travanj", 4),
    ("Svibanj", "the Dogwood Month", "Svibanj", 5),
    ("Lipanj", "the Linden Month", "Lipanj", 6),
    ("Srpanj", "the Sickle Month", "Srpanj", 7),
    ("Kolovoz", "the Cartage Month", "Kolovoz", 8),
    ("Rujan", "the Reddening Month", "Rujan", 9),
    ("Listopad", "the Leaf-fall Month", "Listopad", 10),
    ("Studeni", "the Cold Month", "Studeni", 11),
    ("Prosinac", "the Month of Shining-Through", "Prosinac", 12),
)

# --- THE CALENDAR MOUNT REGISTRY (owner decree 2026-07-29) ---------------------
# "Zodiac i sve što ima 12 TREBA da bude moguće da se AKTIVIRA na
# CALENDAR POINTER" was implemented in 2026-07-21 as a hand-kept quartet
# of `if mount == ...` branches. It is now ONE TABLE: every roster whose
# membership fits the wedges declares itself here, and the renderer and
# the picker both read this and nothing else (Rule #5, Rule #19 — the
# geometry is computed from the declaration, never enumerated).
#
# THE TWO DOZEN SYSTEMS (CANON.md §The Two Dozen Systems and the Four
# Dozens, owner seal 2026-07-22) decide a mount's GEOMETRY, and every
# roster names the one it belongs to:
#
#   System "A" — the ZODIAC-aligned wheel: wedge BOUNDARIES sit ON the
#     cardinals (12h-14h, 14h-16h, ...), so the twelve fall into SIX
#     PAIRS — two flanking the top, two the bottom, two each side.
#     Carries the dozens that come IN PAIRS.
#   System "B" — the MONTH-aligned wheel: the same twelve 2-hour
#     watches SHIFTED 15° so their CENTERS sit on the cardinals
#     (11h-13h, ...). One CROWN (12h), one ROOT (24h), six OPPOSITION
#     AXES. Carries the dozens defined by OPPOSITES.
#
# THE SEAT LAW (owner decree 2026-07-29): a 12-set seats ONE member per
# wedge, at that wedge's own center; a 24-set seats TWO per wedge, at
# ±a quarter wedge from the center — a 15° pitch, the same the Rose's
# three stars already stand on. Both fall out of one formula in
# `render.layers.calendar_mount_angle`; nothing is tabulated per seat.
#
# THE CENTER (`centre`) is the `constants.THIRTEENTHS` key whose member
# may take the dial CENTER while this mount rides. Two different LAWS
# govern whether the seat actually shows (CANON §The Axle, owner-sealed
# 2026-07-29): a CALENDAR-DRIVEN centre (Ophiuchus/Sol/Modrenik/The Cat)
# keeps its own appearance rule (`core.blue_moon`), empty on almost every
# day of the year; an ALWAYS-CENTRE (`constants.AXLE_ALWAYS_CENTERS` —
# Hestia, Jesus, Prudence, Cunning, Peace, Hardness of Heart) is
# unconditionally present on EVERY date instead — the axle never leaves.
# `None` means the canon seals no thirteenth for this set and the center
# simply stays empty (no roster registered below leaves this None — the
# Sins Dozen, the last that might have, was sealed WITH its axle on
# 2026-07-29 — so the branch is exercised by a synthetic mount in
# `tests/test_calendar.py`).
CALENDAR_MOUNT_SEATS_PER_WEDGE = {12: 1, 24: 2}


class CalendarMount(NamedTuple):
    """One roster that may ride the Calendar's twelve wedges.

    `title` is the picker's label. `system` is "A" or "B" above.
    `members` are the display names in SEAT ORDER (index 0 = this
    mount's own first seat, counting clockwise from the dial top).
    `art_dir` is a subdirectory of `assets/calendars/`; `art_stems`
    names the plate stems only where they differ from the display
    names (the Slavic months are Croatian proper nouns with ASCII
    plates), else None — art is always graceful-absent, a missing
    plate falling back to the member's NAME.
    """

    title: str
    system: str
    members: tuple[str, ...]
    art_dir: str
    centre: str | None = None
    art_stems: tuple[str, ...] | None = None
    # WHICH member is TODAY'S (the mark that earns the emphasis):
    # "sign" — the running zodiac sign; "month" — the running Gregorian
    # month (every month-keyed roster); None — the set names no
    # today (the Emotions Dozen: there is no "today's emotion", so no
    # mark is emphasized and all twelve rest at the same opacity).
    follows: str | None = None

    @property
    def seats(self) -> int:
        return len(self.members)

    @property
    def stems(self) -> tuple[str, ...]:
        return self.art_stems or self.members


def almanac_seat_order(by_month: dict) -> tuple[str, ...]:
    """A Gregorian-month-keyed table in ALMANAC SEAT ORDER — June first,
    its wedge centered on the dial's top. The same rotation
    `core.year_wheel.almanac_month_index` applies, expressed here so
    `config` needs no `core` import (Rule #19: one rotation rule, two
    readers, zero written-out orderings)."""
    return tuple(by_month[(seat + 5) % 12 + 1] for seat in range(12))


# THE EMOTIONS DOZEN (CANON.md §The Two Dozen Systems, System B) — the
# ONE roster canon seats HOUR BY HOUR in its own words: "Love 12h, Hope
# 14h, Courage 16h, Ambition 18h, Pride 20h, Envy 22h, Hatred 24h,
# Despair 02h, Fear 04h, Doubt 06h, Humility 08h, Gratitude 10h". On
# System B geometry the top wedge IS 12h, so the canon hour order IS the
# seat order, one wedge every two hours clockwise — no mapping needed.
EMOTIONS_DOZEN = (
    "Love", "Hope", "Courage", "Ambition", "Pride", "Envy",
    "Hatred", "Despair", "Fear", "Doubt", "Humility", "Gratitude",
)

CALENDAR_MOUNTS = {
    # The Zodiac Dozen — System A (Cancer opens at the summer solstice,
    # the dial's own top). Its thirteenth is Ophiuchus.
    "zodiac": CalendarMount(
        title="Zodiac signs",
        system="A",
        members=tuple(name for name, _symbol in constants.ZODIAC_SIGNS),
        art_dir="zodiac/astrology/primary/colored",
        centre="ophiuchus",
        follows="sign",
    ),
    # The Month Dozen — System B, the Gregorian months the Almanac wheel
    # already paints. Its thirteenth is Sol (the Sun's own month).
    "almanac": CalendarMount(
        title="Months",
        system="B",
        members=almanac_seat_order(
            dict(enumerate(constants.GREGORIAN_MONTH_NAMES, start=1))
        ),
        art_dir="almanac/primary/colored",
        centre="sol",
        follows="month",
    ),
    # The Slavic Months — System B, the Croatian proper nouns with ASCII
    # plate stems. Its thirteenth is Modrenik (the Moon's own month).
    "months": CalendarMount(
        title="Slavic months",
        system="B",
        members=almanac_seat_order(
            {month: croatian for croatian, _gloss, _stem, month in SLAVIC_MONTHS}
        ),
        art_dir="slavic_months/primary/colored",
        centre="modrenik",
        follows="month",
        art_stems=almanac_seat_order(
            {month: stem for _croatian, _gloss, stem, month in SLAVIC_MONTHS}
        ),
    ),
    # The Chinese MONTH-branch animals (owner R12) — System B, NOT the
    # Chinese YEAR zodiac read elsewhere. Its thirteenth is The Cat.
    "chinese": CalendarMount(
        title="Chinese zodiac",
        system="B",
        members=almanac_seat_order(constants.CHINESE_MONTH_BRANCH_ANIMALS),
        art_dir="zodiac/chinese/primary/colored",
        centre="chinese",
        follows="month",
    ),
    # The Emotions Dozen (CANON §The Two Dozen Systems, one of the four
    # sealed Dozens) — System B, seated by canon's own hours. Its centre
    # is PEACE, the still point every emotion runs toward (SEALED
    # 2026-07-29, CANON §The Emotions Dozen) — an ALWAYS-CENTER, always
    # present (`constants.AXLE_ALWAYS_CENTERS`), unlike the calendar-driven
    # thirteenths above.
    "emotions": CalendarMount(
        title="Emotions",
        system="B",
        members=EMOTIONS_DOZEN,
        art_dir="emotions/primary/colored",
        centre="peace",
    ),
    # THE OLYMPIANS (CANON §The Olympians) — System A, the classical
    # Dodekatheon seated two by two, every wedge SEALED 2026-07-29: the
    # crown pair Zeus+Hera flanks the top, Demeter+Poseidon roots the
    # bottom, and Athena+Hephaestus/Artemis+Ares/Hermes+Dionysus/Apollo+
    # Aphrodite hold the four remaining arms. Member order below reads
    # CANON's own table top to bottom (12-14h..10-12h), which — on the
    # ZODIAC wheel's cardinal-START wedges (System A) — IS seat order
    # (seat k spans clock hour 12+2k, matching the existing "zodiac"
    # mount's own Cancer-first convention). Its centre is HESTIA, the
    # hiding-place axle who gave up her seat to Dionysus and kept the
    # hearth — always present, an ALWAYS-CENTER.
    "olympians": CalendarMount(
        title="Olympians",
        system="A",
        members=(
            "Zeus", "Athena", "Hephaestus", "Artemis", "Ares", "Demeter",
            "Poseidon", "Hermes", "Dionysus", "Apollo", "Aphrodite", "Hera",
        ),
        art_dir="olympians/primary/colored",
        centre="hestia",
    ),
    # THE APOSTLES (CANON §The Apostles) — System A, the Twelve sent out
    # two by two (Mark 6:7), every wedge SEALED 2026-07-29: Peter+Andrew
    # crown the top, Judas Iscariot+Simon the Zealot root the bottom.
    # Member order reads CANON's own table top to bottom, same seat-order
    # convention as "olympians" above. `art_stems` covers the four
    # members whose plate stem is not their full display name (the
    # sheet's own filenames). Its centre is JESUS, the throne axle —
    # always present, an ALWAYS-CENTER.
    "apostles": CalendarMount(
        title="Apostles",
        system="A",
        members=(
            "Peter", "James the Greater", "John", "Philip", "Bartholomew",
            "Judas Iscariot", "Simon the Zealot", "Thomas", "Matthew",
            "James of Alphaeus", "Thaddaeus", "Andrew",
        ),
        art_dir="apostles/primary/colored",
        centre="jesus",
        art_stems=(
            "Peter", "James", "John", "Philip", "Bartholomew", "Judas",
            "Simon", "Thomas", "Matthew", "James_Alphaeus", "Thaddaeus",
            "Andrew",
        ),
    ),
    # THE VIRTUE WHEEL (CANON §The Virtue Wheel) — System B, Aristotle's
    # twelve virtues (LIGHT register) and their twelve vices (PAINT
    # register) as TWO ENTRIES of one wheel: a virtue and its vice share
    # ONE seat, re-seated and SEALED 2026-07-29 (Magnanimity·Vanity crown
    # at 12h, Just Indignation·Envy root at 24h). Member order reads
    # CANON's own table top to bottom (12h..10h), the same System-B
    # seat-order convention `EMOTIONS_DOZEN` already uses (seat k = hour
    # 12+2k). `art_stems` covers the three members whose plate stem
    # differs from the display name (a space or hyphen the filename
    # cannot carry). Centres are the axle's two faces, both ALWAYS-
    # CENTERS, present on every date: PRUDENCE (light, the charioteer) and
    # CUNNING (paint, the dark charioteer) — CANON §The Virtue Wheel.
    "virtues": CalendarMount(
        title="Virtues",
        system="B",
        members=(
            "Magnanimity", "Truthfulness", "Courage", "Right Ambition",
            "Magnificence", "Wit", "Just Indignation", "Temperance",
            "Patience", "Modesty", "Generosity", "Friendliness",
        ),
        art_dir="virtues/primary/colored",
        centre="prudence",
        art_stems=(
            "Magnanimity", "Truthfulness", "Courage", "Right_Ambition",
            "Magnificence", "Wit", "Just_Indignation", "Temperance",
            "Patience", "Modesty", "Generosity", "Friendliness",
        ),
    ),
    "vices": CalendarMount(
        title="Vices",
        system="B",
        members=(
            "Vanity", "Boastfulness", "Cowardice", "Over-ambition",
            "Vulgarity", "Buffoonery", "Envy", "Gluttony", "Wrath",
            "Shamelessness", "Greed", "Flattery",
        ),
        art_dir="vices/primary/colored",
        centre="cunning",
        art_stems=(
            "Vanity", "Boastfulness", "Cowardice", "Over_Ambition",
            "Vulgarity", "Buffoonery", "Envy", "Gluttony", "Wrath",
            "Shamelessness", "Greed", "Flattery",
        ),
    ),
    # THE SINS DOZEN (CANON §The Sins Dozen) — the FIFTH Dozen, System
    # B, SEALED 2026-07-29: the Christian tradition's catalogue of SIN
    # (Gregory, Evagrius, Aquinas, Dante) beside — never merged with —
    # the Virtue Wheel's Aristotelian vices. PRIDE crowns at 12h, with
    # Vainglory FOLDED INTO IT (Gregory's root returns to the rim, one
    # seat, the stronger word); TREACHERY roots at 24h under the root
    # law (Judas' own midnight on the Apostles Dozen); VIOLENCE holds
    # 16h (the delegated call — Cruelty weighed and set aside). Member
    # order reads CANON's own table top to bottom (12h..10h), the same
    # System-B seat-order convention `EMOTIONS_DOZEN` uses (seat k =
    # hour 12 + 2k). Its centre is HARDNESS OF HEART, the ANTI-PEACE —
    # an ALWAYS-CENTER, present every date. No art has landed for this
    # roster at all yet (`research/prompts/calendars/sins_prompts.md`
    # is written but ungenerated), so every plate — the twelve and the
    # axle alike — takes the graceful-absent NAME fallback, exactly the
    # contract `art_dir` already documents.
    "sins": CalendarMount(
        title="Sins",
        system="B",
        members=(
            "Pride", "Hypocrisy", "Violence", "Avarice", "Lust", "Envy",
            "Treachery", "Despair", "Wrath", "Idolatry", "Gluttony", "Acedia",
        ),
        art_dir="sins/primary/colored",
        centre="hardness_of_heart",
    ),
}
# The legal `Settings.calendar_mount` values — derived, never hand-kept
# (adding a roster above adds its setting value automatically).
CALENDAR_MOUNT_MODES = ("off",) + tuple(CALENDAR_MOUNTS)
# The mid-radius the DESIGN ZODIAC law fixes for a mounted 12-set's marks
# (60-70% of the dial radius) — clear of the rim-riding Earth/Moon and
# the Calendar's own pinned South subdial (orbit ~0.43R).
CALENDAR_MOUNT_RADIUS_FRACTION = 0.65
# The mark's own drawn HEIGHT, fraction of the dial DIAMETER (the SAME
# unit WeekdaySpec.diamond_scale/YearMarkerSpec.scale use) — sized well
# under the 30-deg wedge's own arc gap at the mount radius (~0.17 of the
# diameter between neighboring mark centers) so twelve marks never touch.
CALENDAR_MOUNT_MARK_SCALE = 0.08
# The mark's resting opacity and the extra the CURRENT sign/month earns
# (owner spec: "the mark can inherit that brightness" — the SAME
# base+delta shape the wedges themselves once used, sized so the current
# mark reaches full opacity). This is the MARK's emphasis, NOT the
# deleted wedge lighting — it survived the 2026-07-29 deletion because
# it says "you are here" on the mounted roster, not on the dial paint.
CALENDAR_MOUNT_ALPHA = 0.65
CALENDAR_MOUNT_LIT_DELTA = 0.35
# THE CAT'S DIMMING LAW (owner spec, item 5, R12 — Blue Moon): the
# "chinese" mount's doubled-month mark while The Cat holds the center —
# well below CALENDAR_MOUNT_ALPHA (present, but visibly lending its
# month away), never zero (a vanished mark would read as a rendering
# bug, not a story).
CALENDAR_MOUNT_DIMMED_ALPHA = 0.20

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


def _sourceless_core(name_stem: str) -> str:
    """A filename stem with its terminal source suffix stripped
    (`Lion_v2_gem` -> `Lion_v2`): the RESTRUCTURE moved the source off the
    folder tree and onto the filename, so version discovery matches the
    base/_vN AFTER dropping `_gem`/`_gpt`."""
    low = name_stem.lower()
    for suffix in ("_gem", "_gpt"):
        if low.endswith(suffix):
            return name_stem[: -len(suffix)]
    return name_stem


def _rotation_candidates_in(
    directory: Path, stems: tuple[str, ...]
) -> list[Path]:
    """Every version FILE directly inside `directory` for any base stem
    in `stems` — SUFFIX-AWARE: a trailing `_gem`/`_gpt` is stripped
    before the bare-stem / `stem_v*` match, so both sources' files are
    recognised (the active-source pick happens in `_rotation_candidates`).
    A synthetic tmp tree with suffix-less names exercises the naming
    tolerance directly (no dependency on the real bundled assets)."""
    if not directory.is_dir():
        return []
    candidates: list[Path] = []
    seen_names: set[str] = set()
    for stem in stems:
        stem_lower = stem.lower()
        for entry in directory.iterdir():
            if entry.name in seen_names or entry.suffix.lower() != ".png":
                continue
            core = _sourceless_core(entry.stem)
            if not core.lower().startswith(stem_lower):
                continue
            tail = core[len(stem):]
            if tail == "" or _VERSION_SUFFIX.match(tail):
                candidates.append(entry)
                seen_names.add(entry.name)
    return candidates


def _rotation_candidates(
    directories: tuple[Path, ...], stems: tuple[str, ...]
) -> list[Path]:
    """The daily-rotation pool across `directories`: every distinct
    SOURCELESS version core (base, base_v2, …; both sources fold to one
    core) resolved through `paths.art_file` to the ACTIVE source's file
    (cross-source / suffix-less fallback), so a two-source directory
    never doubles the pool. Sorted by (filename, full path) for a
    deterministic order even when two registers share a basename."""
    resolved: list[Path] = []
    seen_files: set[Path] = set()
    seen_cores: set[tuple] = set()
    for directory in directories:
        for entry in _rotation_candidates_in(directory, stems):
            core = _sourceless_core(entry.stem)
            key = (directory, core)
            if key in seen_cores:
                continue
            seen_cores.add(key)
            picked = paths.art_file(directory / f"{core}.png")
            if picked is not None and picked.exists() and picked not in seen_files:
                resolved.append(picked)
                seen_files.add(picked)
    resolved.sort(key=lambda p: (p.name, str(p)))
    return resolved


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


def _pick_weekly_mandate(candidates: list[Path], on_date: date) -> Path | None:
    """cp_corpo's WEEKLY MANDATE (owner decree 2026-07-29,
    `constants.NINTH_MECHANISMS["cp_corpo"] == "term_weekly"`): the
    RULING triple flips at the ISO calendar week BOUNDARY, not daily —
    even week rules the canonical (Arasaka) half, odd week the
    alternate (NUSA) half, same graceful degrade as `_pick_rotation`
    (zero -> None, one -> that one every week). A 53-week ISO year
    hands the odd side one extra week — the owner knows and accepts
    it."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    index = on_date.isocalendar()[1] % len(candidates)
    return candidates[index]


# THE SEAT ROSTER (Cyberpunk casts, sheet-sealed 2026-07-22; wired by
# completion wave II's second half, Session 32, 2026-07-29). The
# universal rotation above pools ONE figure's own `_v2` versions — a
# second artwork of the SAME figure, which is all the convention was ever
# asked to mean. The Cyberpunk sheet needs the other shape: a SEAT that
# holds several DIFFERENT named figures and turns through them
# ("figure-first rosters" in the sheet, where every file is named after
# the figure it depicts and never after the seat). Without this table
# twelve of that franchise's plates would sit on disk unreachable — the
# exact failure THE THEME COMPLETION LAW exists to end.
#
# theme -> seat label -> the roster's stems, CANONICAL FIRST. The seat
# label is documentation only (a weekday body, or "dual"/"ninth" for the
# two seats that live in their own tables); the lookup below keys on the
# canonical stem, so one mechanism serves the weekday bodies, the Sunday
# Servant and the Ninth alike.
#
# DECLARED ORDER IS THE ROTATION ORDER, and that is load-bearing for the
# Power cast: its Throne, Mirror and Ninth each hold exactly two members,
# so the shared date modulo lands on the same index for all three on any
# given day (the sheet's "SYNCHRONIZED PAIR ROTATION" — no special-case
# code, a consequence of equal roster lengths). Alphabetical resolution
# would have paired Saburo with Rache instead of with Alt; declared order
# keeps the two empires standing together.
WEEKDAY_SEAT_ROSTERS: dict[str, dict[str, tuple[str, ...]]] = {
    "cp_gangs": {
        "moon": ("Aldecaldos", "Mox"),
        "mars": ("Maelstrom", "Barghest", "Wraiths"),
        "mercury": ("Voodoo_Boys", "6th_Street"),
        "saturn": ("Animals", "Scavengers"),
    },
    "cp_street": {
        "mars": ("Jackie", "Panam", "River"),
        "mercury": ("Wakako", "Padre"),
        "venus": ("Kerry", "Lizzy_Wizzy"),
    },
    "cp_corpo": {
        "sun": ("Saburo_Arasaka", "Rosalind_Myers"),
        "dual": ("Yorinobu", "Kurt_Hansen"),
        "ninth": ("Alt_Cunningham", "Rache_Bartmoss"),
    },
    # COMPLETION WAVE III (Session 33, 2026-07-29). The Star Wars Dyad's
    # rotating PEOPLE seats — Tuesday and Wednesday, ordinary two-way
    # pairs.
    #
    # THE NINTH'S MECHANISM IS RESOLVED (owner verdict 2026-07-29,
    # SEALED, superseding Session 33's PROVISIONAL date rotation): the
    # Ninth is a DAYLIGHT/NIGHT switch, not a seat roster — "the duality
    # of that theme pulling the actors to one of two sides." Day shows
    # The Ghosts (`constants.WEEKDAY_THEME_NINTHS["sw_dyad"]`, the
    # canonical/good face), night shows Exegol
    # (`constants.WEEKDAY_THEME_NINTH_NIGHT`) — dispatched through
    # `constants.NINTH_MECHANISMS["sw_dyad"] == "daynight"` by
    # `render.layers.theme_ninth`/`ninth_alt_active` and `render.
    # compositor._center_ninth_alt`, reading the SAME `TickState.
    # is_daylight` `center_face` already reads. The "ninth" entry that
    # used to live here is GONE — see `research/theme_staging.md` for
    # the closed provisional note.
    "sw_dyad": {
        "mars": ("Finn", "Phasma"),
        "mercury": ("Maz", "DJ"),
    },
}
# (theme FOLDER, canonical stem) -> the whole roster (derived; the one
# lookup `rotating_art_file` performs). Keyed on the folder as well as
# the stem so a roster can never capture a same-named plate in another
# theme.
_SEAT_ROSTER_BY_PLATE = {
    (theme, stems[0]): stems
    for theme, seats in WEEKDAY_SEAT_ROSTERS.items()
    for stems in seats.values()
}


def _seat_roster_of(canonical_path: Path) -> tuple[str, ...] | None:
    """The roster `canonical_path` is the canonical member of, or None
    for every other asset in the program. Weekday plates live at
    `<theme>/<register>/<look>/<Stem>.png`, so the theme folder is the
    third parent — the same shape for bronze and for its colored
    sibling."""
    parts = canonical_path.parts
    if len(parts) < 4:
        return None
    return _SEAT_ROSTER_BY_PLATE.get((parts[-4], canonical_path.stem))


def _roster_candidates(directory: Path, stems: tuple[str, ...]) -> list[Path]:
    """A seat roster's plates, in the roster's DECLARED order, resolved
    to the active art source. A member with nothing on disk is skipped
    rather than raising — the seat then simply rotates through fewer
    figures, which is the same graceful-absent contract every other art
    table here keeps (Rule #1's documented path)."""
    resolved: list[Path] = []
    for stem in stems:
        picked = paths.art_file(directory / f"{stem}.png")
        if picked is not None and picked.exists():
            resolved.append(picked)
    return resolved


def rotating_art_file(canonical_path: Path, on_date: date) -> Path | None:
    """ONE asset from a rotating family, THE UNIVERSAL CONVENTION applied
    generically: `canonical_path` is a SOURCELESS `<dir>/<Name>.png`
    (exactly like every config path-table entry). The pool is the
    directory's own `<Name>` / `<Name>_v*` version siblings, resolved to
    the active art source by `paths.art_file` (RESTRUCTURE 2026-07-22
    retired the `alt/` subfolder — versions are `_v2`-style siblings in
    the SAME source-free folder now) — or, when the plate is the
    canonical member of a SEAT ROSTER above, that roster's own figures in
    declared order — normally by `_pick_rotation`'s daily modulo, except
    cp_corpo's own roster, which reads the ISO week's parity instead
    (`_pick_weekly_mandate`, `constants.NINTH_MECHANISMS["cp_corpo"] ==
    "term_weekly"` — THE WEEKLY MANDATE, owner decree 2026-07-29): ONE
    rotation chokepoint, a per-theme CADENCE rather than a second
    mechanism (Rule #5). Opt-in per consumer (scale duality, era
    emblems, tetramorph figures, every weekday body) — never on the hot
    `art_file` path. This is the ONE chokepoint every weekday consumer
    already calls, which is why the roster hooks in here rather than at
    four call sites. None when the canonical path resolves to nothing on
    disk (not even a master)."""
    resolved = paths.art_file(canonical_path)
    if resolved is None or not resolved.exists():
        return None
    stems = _seat_roster_of(canonical_path)
    if stems is not None:
        theme = canonical_path.parts[-4]
        picker = (
            _pick_weekly_mandate
            if constants.NINTH_MECHANISMS.get(theme) == "term_weekly"
            else _pick_rotation
        )
        return picker(_roster_candidates(canonical_path.parent, stems), on_date)
    candidates = _rotation_candidates(
        (canonical_path.parent,), (canonical_path.stem,)
    )
    return _pick_rotation(candidates, on_date)


# The Judas–Lucifer scale badges (owner 2026-07-13): the two triangle
# medallions illustrating "The Two Triangles" — wired before the art
# lands; the Encyclopedia hides missing files.
SCALE_ART_DIR = paths.assets_dir() / "archetypes" / "scale"
# SCALE ROTATION (owner decree 2026-07-19, CANON.md one-image-one-place
# amendment — "koje cemo koristiti na smenu"): Judas-Lucifer is a MAIN
# theme, every being living between excessive self-criticism and
# excessive self-love, so BOTH poles keep MULTIPLE generated versions
# instead of freezing on one master — the FIRST family the universal
# rotation convention above was generalized FROM (2026-07-20).
# The old naming-zoo tolerance ("_Triangle" masters beside a lowercase
# refresh batch) died in the RESTRUCTURE figure-first sweep
# (2026-07-22): every file now carries the plain figure stem
# (`Judas[_vN]_<src>`, `Lucifer[_vN]_<src>`), so the pool is the one
# universal `<stem>` / `<stem>_v*` search. `glass/` stays a second
# STYLE register (a parallel batch of the same two figures), pooled in.


def scale_variant_file(figure: str, on_date: date) -> Path | None:
    """One Scale badge file for `figure` ("Judas"/"Lucifer") on
    `on_date` — DISCOVERS what actually exists on disk for the ACTIVE
    art source at call time (`_rotation_candidates` against
    SCALE_ART_DIR AND its `glass/` register — the metal cameo and the
    stained-glass windows are two parallel batches of the SAME two
    figures), picked by the SHARED `_pick_rotation` — the SAME date
    always yields the SAME file, consecutive dates advance through the
    set, and Lucifer/Judas called with the SAME date stay IN STEP (one
    index driving two independent counts, since both figures' counts
    move together as art lands). Deep travel: the caller passes the
    TRAVELED date, consistent with the poles' light/dark glyph law
    (`controller._effective_travel_date`)."""
    root = paths.art_file(SCALE_ART_DIR)
    # Tree law 2026-07-26: the cameo batch lives at primary/colored/,
    # the stained-glass batch at glass/colored/ — the two look homes of
    # the same two figures.
    candidates = _rotation_candidates(
        (root / "primary" / "colored", root / "glass" / "colored"),
        (figure,),
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
# THE LEGEND BOLD LAW (owner 2026-07-26, CUBE.md §Display and Legend
# Laws — supersedes the 2026-07-12 rainbow): emphasis in article prose
# is BOLD ONLY, and ONLY on the web's spine — the virtue, the vice, the
# emotion/mood and the WEEKDAY. Everything else (color words, figure
# names) reads plain.
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
    # THE WEEKDAY-TITLE LAW's prose half (owner 2026-07-26): weekday
    # names are part of the spine and pop bold wherever they appear.
    # (Serbian "nedelja" also means "week" — an accepted over-match;
    # the shipped originals rarely use it outside the day sense.)
    "weekday": (
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
        "Ponedeljak", "Ponedeljk(?:a|u|om)",
        "Utorak", "Utork(?:a|u|om)",
        "Sred[aeiou]", "Sredom",
        "Četvrtak", "Četvrtk(?:a|u|om)",
        "Petak", "Petk(?:a|u|om)",
        "Subot[aeiou]", "Subotom",
        "Nedelj[aeiou]", "Nedeljom",
    ),
}

# The Legend popup (replaces QToolTip, owner decision): capped to these
# screen fractions — taller content scrolls instead of clipping off a
# small screen; dark tooltip styling.
LEGEND_MAX_WIDTH_FRACTION = 0.45
LEGEND_MAX_HEIGHT_FRACTION = 0.85
LEGEND_CURSOR_OFFSET_PX = 14
LEGEND_PADDING_PX = 8
# THE HOVER TEASER LAW (owner 2026-07-26, CUBE.md §Display and Legend
# Laws): an article hover speaks only its THESIS — this many sentences
# of the first paragraph — and closes with the LEARN MORE / SPACE
# footer; the full article lives in the Encyclopedia.
LEGEND_TEASER_SENTENCES = 2

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
# DECODE CEILINGS (owner order 2026-07-26: entering the Encyclopedia
# must never block or crash — full-res sources decoded straight into
# QPixmaps both stalled the first paint and piled up RAM). A gallery
# card never SHOWS more than ICON_MAX_PX, a reader image never more
# than the viewport at max zoom — decoding past 2× those sizes buys
# nothing. The background warm (`app.encyclopedia_warm`) pre-builds
# disk-cached downscales at these widths; the dialog reads them when
# present and falls back to the original (full-res, but only until the
# warm catches up) rather than paying a cold downscale on the GUI
# thread.
ENCYCLOPEDIA_CARD_ICON_DECODE_PX = 400    # 2× ENCYCLOPEDIA_TOPIC_ICON_MAX_PX
ENCYCLOPEDIA_READER_DECODE_CEILING_PX = 1600   # ~viewport height × max zoom
# LAYOUT fix round R3 (owner: "788px width, tiles clipping" — that class
# dies here); the WIDTH ARITHMETIC corrected round R8b item 5a (the
# original formula silently dropped the inter-card spacing and the
# gallery column's own margins, reliably overflowing the frame by
# ~100px — the "X scroll again" regression): a group NEVER spills more
# than this many cards per row — it WRAPS instead, never a horizontal
# scrollbar. `app.encyclopedia._gallery_content_width`/
# `_gallery_icon_ceiling` (one matched pair, Rule #5) are the ONE
# correct formula, both for the dialog's own MIN WIDTH
# (`EncyclopediaDialog.__init__`) and the live per-resize icon ceiling
# (`_rescale_topics`, zoom-clamped).
ENCYCLOPEDIA_GALLERY_MAX_COLUMNS = 4
ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX = 40   # matches _rescale_topics' + 40/+44

# --- THE COMPUTED DIAGRAMS (owner verdict 2026-07-29) -----------------------
# Twenty-three Encyclopedia pages are COMPOSITIONS the canon exempted
# from generation (CUBE.md, Session 25, root Rule #19). They are drawn
# live from `config.cube`'s own coordinates instead — see
# `render/cube_diagrams.py`. Every number here is a RATIO of the plate's
# own side, so one drawing serves every zoom level and every window.
CUBE_DIAGRAM_UNIT_RATIO = 0.185     # one cube step, as a share of the side
CUBE_DIAGRAM_NODE_RATIO = 0.055     # a cell's dot radius, per unit
CUBE_DIAGRAM_LABEL_RATIO = 0.30     # a label's pixel size, per unit
CUBE_DIAGRAM_LABEL_PUSH = 0.55      # how far outward a pole's name sits
CUBE_DIAGRAM_FRAME_OPACITY = 0.35   # the cube's twelve edges
CUBE_DIAGRAM_DIM_OPACITY = 0.30     # the cells an axis page does not light
CUBE_DIAGRAM_SIDE_PX = 900          # the drawing's own square, then scaled
CUBE_DIAGRAM_MARGIN_PX = 8          # no label is ever drawn past this edge
# The second diagram wave — the journeys and the tables
# (`render/canon_diagrams.py`).
CANON_DIAGRAM_RING_RATIO = 0.34     # the arms' own radius, per plate side
CANON_DIAGRAM_LABEL_RATIO = 0.026   # a station's name, per plate side
CANON_DIAGRAM_TABLE_RATIO = 0.022   # a table cell, per plate side
CANON_DIAGRAM_TABLE_MARGIN = 0.05   # the table's own inset

# --- THE SESSION 27 REWORK (owner-sealed 2026-07-28) -------------------------
# Three levels — six WHOLES, their THEME cards, then the article slider.
#
# THE WINDOW'S OWN MINIMUM IS THE OWNER'S OPENING SCREEN (his spec:
# "Pocetni ekran 16:9 rezolucija 1280 x 720p", "Prvi ekran nema scroll...
# min size je minimalni zoom out"). Pinning the minimum AT that
# resolution is what turns "the home screen never scrolls" from a hope
# into geometry: the 3x2 grid is measured from the viewport, and the
# viewport can never be smaller than the layout the owner specified.
ENCYCLOPEDIA_MIN_WIDTH_PX = 1280
ENCYCLOPEDIA_MIN_HEIGHT_PX = 720
ENCYCLOPEDIA_HOME_COLUMNS = 3        # 2 rows x 3 columns = the six wholes
# The card itself. The edge is the whole's own Rose accent — a hairline
# at rest (EDGE_ALPHA), lit on hover, with a tinted wash behind it.
ENCYCLOPEDIA_CARD_GAP_PX = 20
ENCYCLOPEDIA_CARD_PAD_PX = 12
ENCYCLOPEDIA_CARD_RADIUS_PX = 14
ENCYCLOPEDIA_CARD_EDGE_PX = 1
ENCYCLOPEDIA_CARD_EDGE_ALPHA = 90         # 0-255, the resting hairline
ENCYCLOPEDIA_CARD_HOVER_WASH_ALPHA = 46   # 0-255, the hover tint
ENCYCLOPEDIA_CARD_MIN_WIDTH_PX = 180
ENCYCLOPEDIA_CARD_MIN_HEIGHT_PX = 150
ENCYCLOPEDIA_CARD_IMAGE_MIN_PX = 60
ENCYCLOPEDIA_CARD_IMAGE_RATIO = 0.62   # plate height per card width (theme grid)
ENCYCLOPEDIA_CARD_FONT_RATIO = 0.038   # card font grows with the card's width
ENCYCLOPEDIA_CARD_TITLE_BUMP = 3       # the title sits this much above the body
# THE HOME CARD'S PLATE — COMPUTED, not generated (root Rule #19): a
# whole's tile is a 2x2 mosaic of its OWN theme plates, built live and
# cached in memory, so the six wholes need no artwork to exist. A hand
# drawn plate dropped at `<whole key>.png` under this directory WINS —
# the same graceful-upgrade contract every derived asset here has.
ENCYCLOPEDIA_WHOLE_ART_DIR = paths.assets_dir() / "instrument" / "wholes"
ENCYCLOPEDIA_MOSAIC_PX = 512           # the composed tile's own side
ENCYCLOPEDIA_MOSAIC_GAP_PX = 6
# Modern reader buttons (owner 2026-07-14: "veći, upečatljiviji,
# življih boja — ne kao app iz 1990-e"): vivid gradient pills shared by
# the Encyclopedia and the Guide. Each role owns a (top, bottom)
# gradient pair; hover lightens and pressed darkens the same pair.
UI_BUTTON_FONT_PX = 17
UI_BUTTON_RADIUS_PX = 12
UI_BUTTON_PADDING_PX = (10, 26)         # vertical, horizontal
UI_BUTTON_SMALL_FONT_PX = 14            # the per-entry look arrows
UI_BUTTON_SMALL_PADDING_PX = (5, 12)
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
# finishes (`render.asset_variants.subdial_plate_file` returns the matching
# file directly, no recolor); "solo" ships ONE hand-drawn file
# (SUBDIAL_SOLO_FINISH) and the algorithm derives the other two live,
# same recipe as before. The user picks the SET in Settings
# (`Settings.subdial_set`); the letter FINISH (ring_finish, tray Design
# menu) still decides which color draws within it. The SEAT never
# touches the file at all, only the LIVE shadow
# (`render.layers._draw_subdial_shadow`) — unchanged since Rule #19's
# first enforcement.
SUBDIAL_ROOT_DIR = paths.assets_dir() / "instrument" / "subdial"
SUBDIAL_SOLO_FINISH = "silver"      # the solo set's one hand-drawn file
SLOT_ROUNDEL_BORDER_FRACTION = 0.045     # rim width, of the diameter
SLOT_ROUNDEL_CONTENT_FRACTION = 0.78     # content size inside the rim
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
SMALL_SECONDS_HAND_SHADOW_OFFSET_FRACTION = 0.035   # of the subdial radius
SMALL_SECONDS_HAND_SHADOW_OPACITY = 0.55

SUBDIAL_TEXT_SHADOW_OFFSET_FRACTION = 0.06          # of the font pixel size

# Per-pointer SLOT sizing (owner 2026-07-15): the diamonds differ —
# the slim-armed Seasons and Compass carry 125%, the big-diamond
# Trinity/Prism, Aurora and the pointer-off layouts 150%; on the slim
# arms the seat also shifts OUTWARD to the diamond's widest point
# (the between-arm 3h/21h seats stay put).
SLOT_SIZE_BY_POINTER = {
    "trio": 1.50, "hexa": 1.50, "aurora": 1.50,
    # The Rose is three OCTA stars — the octa's own slim-arm sizing.
    "cross": 1.25, "octa": 1.25, "rose": 1.25,
    # Calendar rides the PINNED layout (no arms) — the big-slot size.
    "calendar": 1.50,
}
SLOT_SIZE_PINNED = 1.50
SLOT_SEAT_OUTWARD = {"cross": 1.12, "octa": 1.12, "rose": 1.12}

# The weekday-by-colors unit rides the ROMB CENTER of its diamond (owner
# 2026-07-15): the star tip sits at star.radius_fraction and a diamond's
# diagonals cross at EXACTLY half the tip on every pointer (inner =
# tip / (2 cos half) ⇒ projection = tip/2), so the by-colors body centers
# in the romb at this fraction of the tip — uniformly, whatever the
# pointer (Trinity/Prism/Seasons/Compass all inherit the same position).
WEEKDAY_ROMB_CENTER_OF_TIP = 0.5

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

# The hidden REPORT window (owner 2026-07-15): function efficiency
# statistics — table + two QPainter charts in one quiet gold hue
# (single-series marks; identity lives in the row labels, exact
# numbers in the table).
REPORT_REFRESH_MS = 1000
REPORT_BAR_TOP_N = 10
REPORT_CHART_HEIGHT_PX = 170

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
OBSERVATORY_LINE_WIDTH_PX = 2
OBSERVATORY_GRID_WIDTH_PX = 1
OBSERVATORY_MARK_RADIUS_PX = 3
# The eclipse timeline's zoom (Deep Time mode): the nearest N eclipses
# of EACH kind on EACH side of the moment (~2.4 of each kind per year,
# so 60 ≈ a ±25-year window around the moment).
OBSERVATORY_ECLIPSE_WINDOW_N = 60

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
GUIDE_DIR = paths.assets_dir() / "instrument" / "guide"
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
    (the Dollar's Great Seal mottos; DOMY's and PILOT's cross-station
    words since the CROSS-WORDS round, 2026-07-27) reaches further out
    than the plain ring letters — `motto_extent` is 0.0 (a no-op term
    in the max()) for every OTHER preset, exactly the graceful-absence
    pattern `triangle`/`legend` already use, so this never grows the
    margin for The One/Templar or a custom ring. MOTO-FIX round (owner correction 2026-07-19): both
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
# The calendar category root (RESTRUCTURE 2026-07-22): the zodiac's own
# astrology art lives at calendars/zodiac/astrology/..., the Chinese
# badges at calendars/zodiac/chinese/... — ONE base (calendars) with the
# family in the folder path (ZODIAC_STYLE_ART_DIRS carry the "zodiac/"
# prefix, CHINESE_STYLE_ART_DIRS the "chinese/" one). Name kept for
# consumer stability.
ZODIAC_ART_DIR = paths.assets_dir() / "calendars"


def weekday_art(rel) -> Path:
    """Absolute path for a weekday theme-relative art path. The first
    segment names the theme FOLDER; `config.taxonomy` fixes its group,
    so 'greek/primary/Helios.png' -> assets/weeks/myth/greek/primary/...
    The Inner-Wheel and Continents step-ups ('../emblem/...',
    '../earth/...') resolve to their own relocated roots (RESTRUCTURE
    2026-07-22). The suffix-less path is returned; `paths.art_file`
    appends the active source suffix at the disk boundary."""
    from config import taxonomy

    parts = Path(rel).parts
    if parts and parts[0] == "..":
        family = parts[1]
        if family == "emblem":
            return taxonomy.inner_wheel_dir().joinpath(*parts[2:])
        if family == "earth":
            return EARTH_ART_DIR.joinpath(*parts[2:])
    return taxonomy.weeks_dir(parts[0]).joinpath(*parts[1:])


# The Inner Wheel emblem logos (owner Gemini art 2026-07-12): one PNG
# per virtue/sin/mood/intelligence — now under weeks/inner_wheel/
# (RESTRUCTURE 2026-07-22). The FAMILY folders keep their singular names.
_INNER_WHEEL = paths.assets_dir() / "weeks" / "inner_wheel"
EMBLEM_ART_DIRS = {
    "virtues": _INNER_WHEEL / "virtue" / "primary" / "colored",
    "sins": _INNER_WHEEL / "sin" / "primary" / "colored",
    "moods": _INNER_WHEEL / "mood" / "primary" / "colored",
    "intelligence": _INNER_WHEEL / "intelligence" / "primary" / "colored",
}
# The trinity and season badge families (owner Gemini art 2026-07-13):
# Faith/Hope/Love triskelions; the Goethe-axis seasons with the
# tropics' Wet_Season/Dry_Season, plus turning_point/ (the solstices
# and the one Equinox) and meteorological/ (the measured twins).
TRINITY_ART_DIR = (
    paths.assets_dir() / "archetypes" / "trinity" / "badges" / "colored"
)
SEASON_ART_DIR = paths.assets_dir() / "celestial" / "seasons" / "badges"
# The ERA TERMS emblems (ROADMAP 15a3, owner 2026-07-17): one per Age
# (Light/Darkness) and per Starry Season (Spring/Summer/Autumn/Winter)
# — the "Eras of the World" comparative article carries no plate of
# its own. Prompt sheet: research/prompts/era/era_prompts.md.
ERA_ART_DIR = paths.assets_dir() / "celestial" / "era"
# The SLAVIC MONTHS 12-set marks (owner-sealed R7b 2026-07-21). A
# CANONICAL SOURCELESS root — deliberately OUTSIDE
# constants.ART_SOURCED_ROOTS, the subdial precedent (see
# assets/___assets.md): a Calendar-pointer mount set is its OWN shared
# thing, not a Gemini/ChatGPT split. assets/months/<stem>.png,
# graceful-absent until the owner's prompt sheet lands — every consumer
# hides a missing plate, exactly like every other wired-ahead art.
MONTHS_ART_DIR = (
    paths.assets_dir() / "calendars" / "slavic_months" / "primary" / "colored"
)
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
    # COMPLETION WAVE I (Session 31, 2026-07-29). Three casts sealed in
    # their own prompt sheets long before the wiring: the Olympians'
    # bestiary seated by the VICE of each arm rather than the virtue
    # (research/prompts/monsters/), the Chinese court drawn from folk
    # myth, the Three Kingdoms and Journey to the West
    # (research/prompts/chinese/), and the executive committee — the one
    # cast in the book whose members are OFFICES rather than persons
    # (research/prompts/corporate/).
    "age_of_heroes": {
        "sun": "Nemean Lion · Cerberus",
        "moon": "Medusa",
        "mars": "Minotaur",
        "mercury": "Sphinx",
        "jupiter": "Erymanthian Boar",
        "venus": "Sirens",
        "saturn": "Hydra",
    },
    "celestial_court": {
        "sun": "Sun Wukong · Six-Eared Macaque",
        "moon": "Chang'e",
        "mars": "Erlang Shen",
        "mercury": "Guan Yu",
        "jupiter": "Zhu Bajie",
        "venus": "Zhinü",
        "saturn": "Shennong",
    },
    "corporate": {
        "sun": "CEO · Chairman",
        "moon": "CHRO",
        "mars": "COO",
        "mercury": "CFO",
        "jupiter": "CMO",
        "venus": "CDO",
        "saturn": "CTO",
    },
    # COMPLETION WAVE II (Session 32, 2026-07-29). The three World of
    # Warcraft casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/wow/wow_prompts.md: the SAME nine seats held three
    # times over, with the arm bundle fixed and only the person changing
    # (CUBE.md Charter rule 5 — three different people holding one
    # office, never one character read three ways). The Alliance and the
    # Horde are seated by the arm's VIRTUE, the Evil cast by the VICE
    # that virtue is named against.
    "wow_alliance": {
        "sun": "Varian Wrynn · Genn Greymane",
        "moon": "Anduin",
        "mars": "Muradin Bronzebeard",
        "mercury": "Khadgar",
        "jupiter": "Uther the Lightbringer",
        "venus": "Jaina",
        "saturn": "Malfurion",
    },
    "wow_horde": {
        "sun": "Thrall · Garrosh",
        "moon": "Baine",
        "mars": "Grommash Hellscream",
        "mercury": "Gallywix",
        "jupiter": "Vol'jin",
        "venus": "Draka",
        "saturn": "Cairne",
    },
    "wow_evil": {
        "sun": "Arthas · Illidan",
        "moon": "Kel'Thuzad",
        "mars": "Mannoroth",
        "mercury": "Gul'dan",
        "jupiter": "Kil'jaeden the Deceiver",
        "venus": "Sylvanas",
        "saturn": "Deathwing",
    },
    # COMPLETION WAVE II, second half (Session 32, 2026-07-29). The
    # three Cyberpunk 2077 casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/cyberpunk/cyberpunk_prompts.md.
    #
    # THE ROSTER SEATS' DISPLAY LAW: where a seat holds several figures
    # (`WEEKDAY_SEAT_ROSTERS` below) the display name lists them all,
    # separated by the same "·" the Sunday dual already uses. The art
    # rotates daily and the label does not, so a per-figure label would
    # go stale the moment the plate turned; a label naming the WHOLE
    # roster is true on every day of it, and the seat's article argues
    # every member. SUNDAY is the one exception and keeps the
    # Ruler · Servant law every other theme obeys — its rotating
    # partners are named in the two face texts instead.
    "cp_gangs": {
        "sun": "Arasaka · Militech",
        "moon": "Aldecaldos · Mox",
        "mars": "Maelstrom · Barghest · Wraiths",
        "mercury": "Voodoo Boys · 6th Street",
        "jupiter": "Tyger Claws",
        "venus": "Valentinos",
        "saturn": "Animals · Scavengers",
    },
    "cp_street": {
        "sun": "Johnny Silverhand · Rogue",
        "moon": "Viktor Vektor",
        "mars": "Jackie · Panam · River",
        "mercury": "Wakako · Padre",
        "jupiter": "Misty",
        "venus": "Kerry · Lizzy Wizzy",
        "saturn": "Judy",
    },
    "cp_corpo": {
        "sun": "Saburo Arasaka · Yorinobu",
        "moon": "Songbird",
        "mars": "Adam Smasher",
        "mercury": "Dexter DeShawn",
        "jupiter": "Solomon Reed",
        "venus": "Evelyn Parker",
        "saturn": "Takemura",
    },
    # COMPLETION WAVE III (Session 33, 2026-07-29). The three Star Wars
    # casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/starwars/starwars_prompts.md. The same nine seats
    # a third time, and the wave where the repeat rule is most visible:
    # Anakin holds the Sith Mirror and the Jedi Mirror, Leia the Jedi
    # Tuesday and the Dyad Thursday, Han the Jedi Wednesday and the Dyad
    # Friday — three people at two ages each, six seats, six independent
    # arguments (CUBE.md Charter rule 5). The Dyad's Tuesday and
    # Wednesday follow the ROSTER SEATS' DISPLAY LAW stated above: the
    # label names every member because the plate turns and the label
    # does not.
    "sw_jedi": {
        "sun": "Young Luke · Vader",
        "moon": "Obi-Wan Kenobi",
        "mars": "General Leia Organa",
        "mercury": "Han Solo",
        "jupiter": "Qui-Gon Jinn",
        "venus": "Padmé Amidala",
        "saturn": "Chewbacca",
    },
    "sw_sith": {
        "sun": "Palpatine · Anakin",
        "moon": "Grand Moff Tarkin",
        "mars": "General Grievous",
        "mercury": "Jabba the Hutt",
        "jupiter": "Count Dooku",
        "venus": "Maul",
        "saturn": "Boba Fett",
    },
    "sw_dyad": {
        "sun": "Rey · Kylo Ren",
        "moon": "Rose Tico",
        "mars": "Finn · Phasma",
        "mercury": "Maz Kanata · DJ",
        "jupiter": "Old Leia",
        "venus": "Old Han",
        "saturn": "General Hux",
    },
}
# THE CONTINENTS (owner-sealed matrix 2026-07-21): the six weekday
# columns are the six continents; Sunday's body is Antarctica, the
# Ruler face of the polar dual (the Arctic Servant lives in
# WEEKDAY_DUAL_NAMES). Added after the literal so the FILES auto-build
# below still folds every OTHER theme's names; the continents file
# stems are the earth faces, overridden explicitly (like greek/norse).
WEEKDAY_THEME_NAMES["continents"] = {
    "sun": "Antarctica",
    "moon": "Oceania",
    "mars": "Europe",
    "mercury": "Asia",
    "jupiter": "Africa",
    "venus": "South America",
    "saturn": "North America",
}

# File stems on disk: the display names folded to ASCII (Sól -> Sol,
# Dažbog -> Dazbog) and PASCAL-CASED per token (tree law rule 5, the
# case half, owner-approved 2026-07-26: every stem reads as a NAME —
# Afu_Ra, Big_Bang — never a lowercase file token). The themes below
# historically shipped lowercase stems; their names are NORMALIZED
# (lowered, then Pascal-cased) so display-name capitals like "McX"
# can never drift the stem from what the disk rename produced.
_ASCII_FOLD = str.maketrans("óážš", "oazs")
_LOWERCASE_THEMES = (
    "religion", "religion_alt", "planet_signs", "egypt", "slavic", "alchemy",
    "wolf",
)


def _pascal_stem(stem: str) -> str:
    """Tree-law stem casing: capitalize each underscore token unless it
    already carries a capital of its own (Yggdrasil, KaliYuga stay as
    drawn) — the SAME rule research/pascalcase_stems.py renamed the
    disk with, so config and files can never disagree."""
    return "_".join(
        t if any(c.isupper() for c in t) else (t[:1].upper() + t[1:])
        for t in stem.split("_")
    )
# Theme -> art folder under assets/weeks/<group>/: THE TREE LAW
# (owner-approved 2026-07-26) — every theme dir is
# <theme>/<register>/<look>: related themes share a theme folder via
# registers (creeds = primary Creeds + secondary Mysteries; bible =
# primary/secondary/dark; planets = ONE primary register whose looks
# are photo/sign/art), and a register's colored arc is its own CHILD
# <register>/colored — identical at every level, pantheon and primary
# alike (the owner's decree; the old sibling-<family>/colored shape is
# dead). The DUAL FLATTEN law (owner 2026-07-19) still holds: every
# file, dual included, sits FLAT inside its look — WHO a file is lives
# only in WEEKDAY_DUAL_FILES/WEEKDAY_PANTHEON, never in a folder name.
# Cameo-master sets carry bronze/ (gold/silver derive by algorithm);
# as-drawn full-color sets carry colored/ as their single look.
WEEKDAY_THEME_DIRS = {
    "planet_signs": "planets/primary/sign",
    "greek": "greek/primary/bronze",
    "norse": "norse/primary/bronze",
    "egypt": "egypt/primary/bronze",
    "slavic": "slavic/primary/bronze",
    "alchemy": "alchemy/primary/colored",
    "japan": "japan/primary/colored",
    "religion": "creeds/primary/colored",
    "religion_alt": "creeds/secondary/colored",
    "profession": "profession/primary/bronze",
    "wolf": "wolf/primary/bronze",
    "bee": "bee/primary/bronze",
    "elephant": "elephant/primary/bronze",
    "bible": "bible/primary/colored",
    "bible2": "bible/secondary/colored",
    "bible_dark": "bible/dark/colored",
    "cosmos": "cosmos/primary/bronze",
    "planets_art": "planets/primary/art",
    # Completion wave I (Session 31): bronze primary registers with a
    # colored/ sibling apiece — the standard cameo-master shape.
    "age_of_heroes": "age_of_heroes/primary/bronze",
    "celestial_court": "celestial_court/primary/bronze",
    "corporate": "corporate/primary/bronze",
    # Completion wave II (Session 32): the same shape again — a carved
    # bronze relief master per cast with its full-paint colored/ sibling.
    "wow_alliance": "wow_alliance/primary/bronze",
    "wow_horde": "wow_horde/primary/bronze",
    "wow_evil": "wow_evil/primary/bronze",
    # Completion wave II, Cyberpunk half (Session 32): the same shape a
    # third time — one aged-bronze relief master per cast with its
    # neon-noir colored/ sibling. Every roster member's plate lives FLAT
    # in the same look dir beside the canonical one (the sheet's own
    # figure-first naming: a file is named after the figure it depicts,
    # never after the seat).
    "cp_gangs": "cp_gangs/primary/bronze",
    "cp_street": "cp_street/primary/bronze",
    "cp_corpo": "cp_corpo/primary/bronze",
    # Completion wave III (Session 33): the same shape a fourth time —
    # one aged-bronze relief master per cast with its full-paint colored/
    # sibling. The Dyad's roster members live FLAT in the same look dir
    # beside the canonical plate, the sheet's own figure-first naming
    # (the sheet's prose still describes the retired `alt/` subfolder;
    # its DROP PATHS already write Phasma, DJ and Exegol as siblings,
    # which is the shape wired here).
    "sw_jedi": "sw_jedi/primary/bronze",
    "sw_sith": "sw_sith/primary/bronze",
    "sw_dyad": "sw_dyad/primary/bronze",
    # The emblem families live OUTSIDE assets/weekday/ — the relative
    # step-up reaches assets/emblem/ (owner 2026-07-14).
    "virtues": "../emblem/virtue/primary/colored",
    "sins": "../emblem/sin/primary/colored",
    "moods": "../emblem/mood/primary/colored",
    # THE CONTINENTS reuse the dial's OWN Earth faces (assets/earth/,
    # owner exception 2026-07-21) — the relative step-up reaches them,
    # exactly like the emblem families reach assets/emblem/. The stems
    # (overridden below) are the earth_{style}_{region}_{phase} faces.
    "continents": "../earth",
}
WEEKDAY_THEME_FILES = {
    theme: {
        body: _pascal_stem(
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
WEEKDAY_THEME_FILES["wolf"]["sun"] = "Alpha"
WEEKDAY_THEME_FILES["bee"]["sun"] = "Queen"
WEEKDAY_THEME_FILES["elephant"]["sun"] = "Matriarch"
# The Corporation's six weekday stems ARE its display names (the
# acronyms already carry their own capitals, so the Pascal rule leaves
# them alone) — only the dual Sunday title needs the single-name file.
WEEKDAY_THEME_FILES["corporate"]["sun"] = "CEO"
# The metal reads Quicksilver, the owner's file keeps the element name.
WEEKDAY_THEME_FILES["alchemy"]["mercury"] = "Mercury"
# The reworked Creeds and the wolf rank parentheticals keep plain stems.
WEEKDAY_THEME_FILES["religion_alt"]["jupiter"] = "Eleusis"
WEEKDAY_THEME_FILES["wolf"]["mars"] = "Hunter"
WEEKDAY_THEME_FILES["wolf"]["mercury"] = "Scout"
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
    "sun": "Nichiyobi",
    "moon": "Getsuyobi",
    "mars": "Kayobi",
    "mercury": "Suiyobi",
    "jupiter": "Mokuyobi",
    "venus": "Kinyobi",
    "saturn": "Doyobi",
}
# The text-wave themes (owner 2026-07-14): explicit stems — the
# display names carry duals ("·") and compounds ("Adam & Eve");
# PascalCase per the tree law's stem casing (rule 5, 2026-07-26).
WEEKDAY_THEME_FILES["bible"] = {
    "sun": "Ancient_Of_Days", "moon": "Mary", "mars": "David",
    "mercury": "Moses", "jupiter": "Solomon", "venus": "Adam_And_Eve",
    "saturn": "Joseph",
}
WEEKDAY_THEME_FILES["bible2"] = {
    "sun": "Abraham", "moon": "Jonah", "mars": "Samson",
    "mercury": "Jacob", "jupiter": "Noah", "venus": "Ruth",
    "saturn": "Job",
}
WEEKDAY_THEME_FILES["bible_dark"] = {
    "sun": "Lucifer", "moon": "Lilith", "mars": "Goliath",
    "mercury": "Serpent", "jupiter": "Herod", "venus": "Delilah",
    "saturn": "Cain",
}
WEEKDAY_THEME_FILES["cosmos"] = {
    "sun": "Sun", "moon": "Nebula", "mars": "Supernova",
    "mercury": "Pulsar", "jupiter": "Galaxy", "venus": "Binary_Stars",
    "saturn": "Comet",
}
WEEKDAY_THEME_FILES["planets_art"] = {
    "sun": "Sun", "moon": "Moon", "mars": "Mars",
    "mercury": "Mercury", "jupiter": "Jupiter", "venus": "Venus",
    "saturn": "Saturn",
}
# Completion wave I (Session 31): explicit stems — the display names
# carry duals ("·"), spaces (Erymanthian Boar, Sun Wukong) and a
# diacritic (Zhinü) that the ASCII fold does not know.
WEEKDAY_THEME_FILES["age_of_heroes"] = {
    "sun": "Nemean_Lion", "moon": "Medusa", "mars": "Minotaur",
    "mercury": "Sphinx", "jupiter": "Erymanthian_Boar", "venus": "Sirens",
    "saturn": "Hydra",
}
WEEKDAY_THEME_FILES["celestial_court"] = {
    "sun": "Sun_Wukong", "moon": "ChangE", "mars": "Erlang_Shen",
    "mercury": "Guan_Yu", "jupiter": "Zhu_Bajie", "venus": "Zhinu",
    "saturn": "Shennong",
}
# Completion wave II (Session 32): explicit stems for all three WoW
# casts — the display names carry the Sunday dual ("·"), epithets
# (the Lightbringer, the Deceiver), surnames the file drops, and the
# apostrophes of Vol'jin, Kel'Thuzad, Gul'dan and Kil'jaeden that the
# ASCII fold does not know. The stems are the sheet's own drop paths.
WEEKDAY_THEME_FILES["wow_alliance"] = {
    "sun": "Varian", "moon": "Anduin", "mars": "Muradin",
    "mercury": "Khadgar", "jupiter": "Uther", "venus": "Jaina",
    "saturn": "Malfurion",
}
WEEKDAY_THEME_FILES["wow_horde"] = {
    "sun": "Thrall", "moon": "Baine", "mars": "Grommash",
    "mercury": "Gallywix", "jupiter": "Voljin", "venus": "Draka",
    "saturn": "Cairne",
}
WEEKDAY_THEME_FILES["wow_evil"] = {
    "sun": "Arthas", "moon": "Kel_Thuzad", "mars": "Mannoroth",
    "mercury": "Guldan", "jupiter": "Kiljaeden", "venus": "Sylvanas",
    "saturn": "Deathwing",
}
# Completion wave II, Cyberpunk half (Session 32): the stems are the
# CANONICAL member of each seat — the first entry of the seat's roster
# below, and the only one the auto-build could never have guessed, since
# a roster seat's display name lists every member. The stems are the
# sheet's own drop paths.
WEEKDAY_THEME_FILES["cp_gangs"] = {
    "sun": "Arasaka", "moon": "Aldecaldos", "mars": "Maelstrom",
    "mercury": "Voodoo_Boys", "jupiter": "Tyger_Claws",
    "venus": "Valentinos", "saturn": "Animals",
}
WEEKDAY_THEME_FILES["cp_street"] = {
    "sun": "Johnny", "moon": "Viktor", "mars": "Jackie",
    "mercury": "Wakako", "jupiter": "Misty", "venus": "Kerry",
    "saturn": "Judy",
}
WEEKDAY_THEME_FILES["cp_corpo"] = {
    "sun": "Saburo_Arasaka", "moon": "Songbird", "mars": "Adam_Smasher",
    "mercury": "Dexter", "jupiter": "Solomon", "venus": "Evelyn",
    "saturn": "Takemura",
}
# Completion wave III (Session 33): explicit stems for all three Star
# Wars casts — the display names carry the Sunday dual ("·"), the roster
# seats' "·" lists, hyphens (Obi-Wan, Qui-Gon), an age qualifier the file
# drops (Old Leia, Old Han) and the acute of Padmé that the ASCII fold
# does not know. The stems are the sheet's own drop paths, with ONE
# correction: the sheet writes `BobaFett.png`, which breaks the tree
# law's word-separator rule (`tests/test_assets_structure.py`
# test_figure_stems_separate_their_words) — the lawful stem is
# `Boba_Fett`, and the sheet has been corrected to match rather than the
# rule bent to it.
WEEKDAY_THEME_FILES["sw_jedi"] = {
    "sun": "Luke", "moon": "Obi_Wan", "mars": "Leia",
    "mercury": "Han", "jupiter": "Qui_Gon", "venus": "Padme",
    "saturn": "Chewbacca",
}
WEEKDAY_THEME_FILES["sw_sith"] = {
    "sun": "Palpatine", "moon": "Tarkin", "mars": "Grievous",
    "mercury": "Jabba", "jupiter": "Dooku", "venus": "Maul",
    "saturn": "Boba_Fett",
}
WEEKDAY_THEME_FILES["sw_dyad"] = {
    "sun": "Rey", "moon": "Rose", "mars": "Finn",
    "mercury": "Maz", "jupiter": "Leia", "venus": "Han",
    "saturn": "Hux",
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
# THE CONTINENTS' file stems ARE the Earth faces (owner exception
# 2026-07-21): the atmosphere-lit day globe per region is the baked
# preview/fallback stem; the live dial overrides both style and phase
# at render (continents_body_art). Built straight from CONTINENTS_
# REGIONS so the mapping lives in exactly one place (Rule #5).
WEEKDAY_THEME_FILES["continents"] = {
    body: f"earth_{CONTINENTS_PREVIEW_STYLE}_{region}_day"
    for body, region in CONTINENTS_REGIONS.items()
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
    # THE POLAR DUAL (owner-sealed matrix 2026-07-21): ANTARCTICA the
    # Ruler — a true continent, real rock under the ice — and the ARCTIC
    # the Servant — walkable ice with no land beneath, reality and its
    # shadow. The two live in eternal antiphase (polar day on one is
    # polar night on the other): the Ruler/Servant solar-window law made
    # planetary.
    "continents": ("Antarctica", "Arctic"),
    # COMPLETION WAVE I (Session 31). Three duals of one house rather
    # than three oppositions: two literal brothers (both children of
    # Typhon and Echidna), a Sage and his perfect counterfeit, and the
    # two offices company law itself recommends be held apart.
    "age_of_heroes": ("Nemean Lion", "Cerberus"),
    "celestial_court": ("Sun Wukong", "The Six-Eared Macaque"),
    "corporate": ("CEO", "Chairman of the Board"),
    # COMPLETION WAVE II (Session 32). Three duals of one house rather
    # than three oppositions, exactly as the sheet argues them: two
    # kings of the same alliance, a Warchief and the successor he
    # appointed himself, and two men who made the identical bargain and
    # were answered differently for it.
    "wow_alliance": ("Varian Wrynn", "Genn Greymane"),
    "wow_horde": ("Thrall", "Garrosh Hellscream"),
    "wow_evil": ("Arthas, the Lich King", "Illidan Stormrage"),
    # COMPLETION WAVE II, Cyberpunk half (Session 32). Three duals of
    # one house rather than three oppositions, as the sheet argues them:
    # the two corporations that fought the Fourth Corporate War and were
    # left reflecting each other, a legend and the woman who refused the
    # job that made him one, and a founder against the son who strangled
    # him and then sat in the chair.
    "cp_gangs": ("Arasaka", "Militech"),
    "cp_street": ("Johnny Silverhand", "Rogue"),
    "cp_corpo": ("Saburo Arasaka", "Yorinobu"),
    # COMPLETION WAVE III (Session 33). Three duals of one house rather
    # than three oppositions, exactly as the sheet argues them: a son and
    # the father he refused to execute, a master and the apprentice he
    # assembled from a nine-year-old, and the one pair in the whole
    # instrument whose SOURCE material calls them a single power in two
    # bodies.
    "sw_jedi": ("Young Luke", "Vader, the Father"),
    "sw_sith": ("Palpatine", "Anakin"),
    "sw_dyad": ("Rey", "Kylo Ren"),
}
# Dual paths live FLAT inside the theme's look dir (owner DUAL
# FLATTEN 2026-07-19: the dual/ folder carried zero semantic weight at
# runtime — the config table already IS the identity, so the folder
# only added a navigation step); the colored dual is the same path
# with the LOOK segment (the last folder) swapped to colored/ —
# `colored_variant_rel` below is the ONE implementation of that swap
# (tree law 2026-07-26; the old "/primary/" string replace died with
# the sibling-colored shape).
WEEKDAY_DUAL_FILES = {
    "planets": "planets/primary/photo/Sun_Eclipse",
    "planet_signs": "planets/primary/sign/Sun_Eclipse",
    "greek": "greek/primary/bronze/Phaethon",
    "norse": "norse/primary/bronze/Skoll",
    "egypt": "egypt/primary/bronze/Afu_Ra",
    "slavic": "slavic/primary/bronze/Dazbog_Old",
    "alchemy": "alchemy/primary/colored/Ore",
    "japan": "japan/primary/colored/Ama_No_Iwato",
    "religion": "creeds/primary/colored/Satanism",
    "religion_alt": "creeds/secondary/colored/Corax",
    # profession's flat "Servant" stem collides with an already-flat,
    # unreferenced orphan file the owner has separately at
    # profession/primary/Servant.png (different art, different hash —
    # a true collision found flattening this round) — config-side
    # rename to "Servant_dual" resolves it without touching the
    # unrelated orphan (Rule #3: never delete without the owner's own
    # look).
    "profession": "profession/primary/bronze/Servant_Dual",
    "wolf": "wolf/primary/bronze/Omega",
    "bee": "bee/primary/bronze/Cleaner",
    "elephant": "elephant/primary/bronze/Memory",
    "bible": "bible/primary/colored/Son_Servant",
    "bible2": "bible/secondary/colored/Isaac",
    "bible_dark": "bible/dark/colored/Judas",
    "cosmos": "cosmos/primary/bronze/Black_Hole",
    "planets_art": "planets/primary/art/Sun_Eclipse",
    # Completion wave I (Session 31): the servant plate flat inside the
    # theme's own look dir, colored twin via colored_variant_rel.
    "age_of_heroes": "age_of_heroes/primary/bronze/Cerberus",
    "celestial_court": "celestial_court/primary/bronze/Six_Eared_Macaque",
    "corporate": "corporate/primary/bronze/Chairman",
    # Completion wave II (Session 32): the servant plate flat inside the
    # cast's own look dir, colored twin via colored_variant_rel.
    "wow_alliance": "wow_alliance/primary/bronze/Genn",
    "wow_horde": "wow_horde/primary/bronze/Garrosh",
    "wow_evil": "wow_evil/primary/bronze/Illidan",
    # Completion wave II, Cyberpunk half (Session 32): the servant plate
    # flat inside the cast's own look dir, colored twin via
    # colored_variant_rel. The Power cast's Mirror ROTATES (Yorinobu /
    # Kurt Hansen) in lockstep with its Throne and its Ninth.
    "cp_gangs": "cp_gangs/primary/bronze/Militech",
    "cp_street": "cp_street/primary/bronze/Rogue",
    "cp_corpo": "cp_corpo/primary/bronze/Yorinobu",
    # Completion wave III (Session 33): the servant plate flat inside the
    # cast's own look dir, colored twin via colored_variant_rel. None of
    # the three Mirrors ROTATES — the Dyad's rotating seats are Tuesday,
    # Wednesday and its Ninth, never its Sunday.
    "sw_jedi": "sw_jedi/primary/bronze/Vader",
    "sw_sith": "sw_sith/primary/bronze/Anakin",
    "sw_dyad": "sw_dyad/primary/bronze/Kylo",
    "virtues": "../emblem/virtue/primary/colored/Humility",
    "sins": "../emblem/sin/primary/colored/Servility",
    "moods": "../emblem/mood/primary/colored/Awe",
    # THE ARCTIC SERVANT (owner exception 2026-07-21): the north_pole
    # Earth face, the Antarctic Ruler's antiphase mirror — the atmo-day
    # still frame is the baked stem (the live dial overrides style/phase
    # via continents_dual_art). Reaches the earth family with the same
    # "../earth" step-up the emblem duals use.
    "continents":
        f"../earth/earth_{CONTINENTS_PREVIEW_STYLE}_{CONTINENTS_DUAL_REGION}_day",
}


def colored_variant_rel(rel: str) -> str:
    """`rel`'s colored twin — the LOOK segment (the last folder of a
    `<theme>/<register>/<look>/<stem>` relative path) swapped to
    `colored` (tree law 2026-07-26: colored is a CHILD of its register
    at every level). THE ONE implementation — the old
    `.replace("/primary/", "/colored/")` string swap lived in five
    places (encyclopedia, controller, build_roster ×2, and implicitly
    the sibling-dir arithmetic) and silently broke the moment the look
    level appeared."""
    head, _, stem = rel.rpartition("/")
    register, _, _look = head.rpartition("/")
    return f"{register}/colored/{stem}"


# THE TITLE PLATE. A theme's opening page and its week-duality title
# page had no image NAME at all — not a missing file, a missing name, so
# no prompt sheet could even say what to draw (Session 27 coverage law,
# owner 2026-07-28: "svaki clanak mora sliku").
#
# THE SEAT IS THE ONE THE PROJECT ALREADY USES:
# `<theme>/<register>/<look>/Title.png` — `Title` is the reserved stem
# the tree law names, and `research/prompts/titles/theme_title_prompts.md`
# has been writing briefs against exactly these paths since R8c
# (2026-07-21). A parallel `title/` register was tried first and thrown
# out the same day: it would have orphaned twenty-odd already-written
# prompts for the sake of a second convention saying the same thing.
#
# A MERGED theme's three blocks land in their own three registers, which
# is what a register is for: greek/primary, greek/pantheon, greek/wider;
# bible/primary, bible/secondary, bible/dark. The week-duality title is
# the SAME seat under the reserved stem `Duality`.
TITLE_PLATE_STEM = "Title"
DUALITY_PLATE_STEM = "Duality"

# THE TWO GENERIC PLATES (owner decree 2026-07-29). Two pages repeat
# across the whole book with the SAME meaning every time, so they are
# ONE shared image each, not one per theme:
#
#   * the week's DUALITY title page — "one seat, two faces, and a ninth
#     outside the circle". The owner struck the per-theme version down
#     for the reader's sake, not for cost: the two faces open the very
#     next two pages ("njihova slika se sve pojavljuje odmah na sledeće
#     dve strane"), so a title plate that draws them again spends
#     attention on a repeat. The generic plate carries the SHAPE of the
#     idea and no figure at all.
#   * the THIRTEENTH of any twelve-based set (Sol, Modrenik, and
#     whatever else earns a thirteenth) — "the count that does not
#     close".
#
# Both belong to no theme, so they cannot live in a theme's register
# (the tree law has no seat for "everyone's"); they are the
# instrument's own furniture, beside the section logo and the
# paint/light legend. Briefs: research/prompts/instrument/.
DUALITY_GENERIC_ART = INSTRUMENT_ART_DIR / "duality.png"
THIRTEENTH_GENERIC_ART = INSTRUMENT_ART_DIR / "thirteenth.png"
# The ONE documented exception the owner allowed: a theme whose dual
# page presents something none of its three seat-holders already
# describes may claim its OWN plate. Key -> True. EMPTY today; the
# per-theme briefs stay written in `titles/theme_title_prompts.md` so
# claiming one is a one-line change plus a generation.
THEME_OWN_DUALITY_PLATE: dict[str, bool] = {}
# key -> (register, look) where either differs from primary/colored.
TITLE_PLATE_SEATS = {
    "planets": ("primary", "photo"),
    "planet_signs": ("primary", "sign"),
    "planets_art": ("primary", "art"),
    "bible2": ("secondary", "colored"),
    "bible_dark": ("dark", "colored"),
    "religion_alt": ("secondary", "colored"),
}


def theme_title_art(key: str, duality: bool = False) -> "Path":
    """The plate for one theme-title or week-duality-title page. `key` is
    the article key the page already carries — "greek", "greek_pantheon",
    "greek_wider", "bible_dark"."""
    from config import taxonomy

    base, register = key, None
    for suffix in ("_pantheon", "_wider"):
        if base.endswith(suffix):
            base, register = base[: -len(suffix)], suffix[1:]
            break
    # EVERY dual page shares ONE plate unless this theme earned its own
    # (owner decree 2026-07-29) — the block's register does not matter,
    # because the generic plate belongs to no register.
    if duality and not THEME_OWN_DUALITY_PLATE.get(base):
        return DUALITY_GENERIC_ART
    seat_register, look = TITLE_PLATE_SEATS.get(base, ("primary", "colored"))
    register = register or seat_register
    stem = DUALITY_PLATE_STEM if duality else TITLE_PLATE_STEM
    if duality and register == "pantheon":
        # A pantheon block whose dual pair is the SAME pair as the
        # planetary block's would need an identical plate — Egypt's Ra
        # and Afu-Ra sit at the centre of both rosters. Rule #19: the
        # second plate is not a variant to draw, it is the first plate,
        # so the page reads the primary register's own file. Derived,
        # never enumerated: the comparison is the canon's two tables.
        pantheon = WEEKDAY_PANTHEON.get(base, {})
        if pantheon.get("dual_names") == WEEKDAY_DUAL_NAMES.get(base):
            register = seat_register
    # The live CODE keys are still the pre-rename ones (`bible2`,
    # `religion_alt`) — the rename table takes them to the taxonomy's own
    # key, and THEME_FOLDER from there to the folder that holds them.
    renamed = taxonomy.THEME_KEY_RENAMES.get(base, base)
    folder = taxonomy.theme_folder(renamed)
    return weekday_art(f"{folder}/{register}/{look}/{stem}.png")


def weekday_theme_body_art(
    theme: str, body: str, on_date: date | None = None, colored: bool = False,
) -> Path:
    """One theme's plate for one weekday body (bronze / canon file) —
    moved here from `app.encyclopedia._theme_body_art` (R5 MENU REWORK,
    Rule #5): the Encyclopedia gallery AND the new Pointer/Slot Theme
    picker windows both need a representative preview per theme, so the
    resolution lives ONCE in config and both readers import it. THE
    SAME expression used to be re-typed at every render call site
    (`render.layers._draw_weekday_slot`, `render.compositor`'s hover
    legend, `app.controller._themed_weekday_set`'s baked bodies dict) —
    consolidated here (weekday ALT ROTATION round, owner 2026-07-20/21)
    so the universal rotation convention has exactly ONE weekday-body
    chokepoint instead of four copies drifting apart. `colored`
    redirects to the metal theme's `colored/` sibling folder, exactly
    like `app.encyclopedia._theme_dual_art`'s own flag. `on_date` opts
    into THE UNIVERSAL ROTATION CONVENTION (`rotating_art_file`): None
    (every caller before this round) returns the plain canonical file;
    a date resolves the day's pick among the canonical file's `_v2`/
    `alt/` siblings, falling back to canonical when none exist."""
    if theme == "planets":
        canonical = weekday_art(f"planets/primary/photo/{body.capitalize()}.png")
    else:
        theme_dir = weekday_art(WEEKDAY_THEME_DIRS[theme])
        if colored:
            theme_dir = theme_dir.parent / "colored"
        canonical = theme_dir / f"{WEEKDAY_THEME_FILES[theme][body]}.png"
    if on_date is None:
        return canonical
    return rotating_art_file(canonical, on_date) or canonical

# THE METAL SHADES (rewritten 2026-07-27, owner verdict "prihvaceno" on
# the new transformer): the numeric recolor recipe is GONE from this file
# — every shade is now a named RAMP in `recolor/presets/metals.json`, and
# the algorithm that paints it is the `recolor` package (see
# [Recolor (folder)](../recolor/___recolor.md)). What lives here is only
# the MAPPING from a user-selectable shade to the ramp that draws it.
#
# WHAT WAS RETIRED AND WHY (measured on the owner's physician plate):
# the old recipe replaced each masked pixel's hue and saturation with a
# flat constant and scaled its value by one bounded global gain. Gold
# `classic` was HSV(44.9, S=1.000, V), which expands to (V, 0.748V, 0) —
# the BLUE CHANNEL IDENTICALLY ZERO on 52.59% of the plate, and a white
# highlight arithmetically impossible at flat S=1.0 ("drecavo, napadno,
# bez detalja"). Silver was HSV(220, S=0, V) = max(R,G,B), which on warm
# bronze art is the RED channel alone (mean R 0.3721 vs mean V 0.3740).
# The gain hit its 1.90 ceiling on dark medallion art and clipped 11.87%
# (gold) / 8.17% (silver) to one flat maximum — the book page on the
# plate came out with NO information in its top 5% ("kao da joj je neko
# polio krec"). `METAL_RECOLOR_GAIN_RANGE`, `METAL_SWAP_HUE_WINDOW`,
# `METAL_SWAP_HUE_SOFT` and `METAL_SWAP_SAT_RAMP` all belonged to that
# kernel and went with it; the mask's window now lives in the presets'
# `tuning` block, in Oklab.
#
# The SHADE NAMES themselves are unchanged and still validated against
# `config.constants.METAL_SHADE_NAMES` — the user's Settings choice keeps
# working exactly as before. Silver's three shades map to ramps that
# already existed as metals in their own right; gold's and bronze's are
# named `gold_*` / `bronze_*`.
METAL_SHADES = {
    "gold": {
        "dark_amber": "gold_dark_amber",
        "amber":      "gold_amber",
        "classic":    "gold",             # DEFAULT
        "pale":       "gold_pale",
        "champagne":  "gold_champagne",
    },
    "bronze": {
        "dark_bronze":  "bronze_dark",
        "bronze":       "bronze",         # DEFAULT
        "light_bronze": "bronze_light",
    },
    "silver": {
        "gunmetal": "gunmetal",
        "silver":   "silver",             # DEFAULT
        "platinum": "platinum",
    },
    # The THEMATIC pseudo-metal (ENLARGE/THEMATIC round, owner
    # 2026-07-27; widened for CUSTOM rings same day): every thematic
    # choice IS a ramp name — identity-mapped over the whole roster
    # (the five ring theme colors plus every metal ramp, owner: "iron,
    # copper... sve"), exactly the "one entry, zero code" door the
    # transformer promises. moon_indigo stays the DEFAULT / custom
    # fallback (constants.METAL_SHADE_DEFAULT).
    "thematic": {
        name: name for name in constants.METAL_SHADE_NAMES["thematic"]
    },
}
# WHICH METAL THE ART WAS DRAWN IN — the transformer is source-agnostic
# (it measures and divides out whatever cast the source carries), so
# every call must say where it starts from. Badge medallions are drawn
# in bronze mixed with gray stone; ring letters and numerals are drawn on
# the GOLD master (owner 2026-07-19, `render.asset_recolor.
# letter_metal_file` — the pre-rendered silver/bronze files were retired
# then).
METAL_SOURCE_BADGE = "bronze"
METAL_SOURCE_LETTER = "gold"
# The mask mode each art family needs (`recolor.mask`): a medallion
# mixes metal with neutral stone and must be detected; a glyph is metal
# wherever it is opaque.
METAL_MASK_BADGE = "chroma"
METAL_MASK_LETTER = "alpha"

METAL_SWAP_VERSION = 6      # cache tag — bump on recolor math changes

# Badges never bronze-swap: bronze IS the art as drawn (membership only;
# the recolor recipe itself lives in the presets).
METAL_SWAP_TARGETS = ("gold", "silver")

ECLIPSE_INVISIBLE_STRENGTH_FACTOR = 0.5
ECLIPSE_SOLAR_ART = (
    weekday_art("planets/primary/photo/Sun_Eclipse.png")
)                                            # source-mapped by paths.art_file
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
ECLIPSE_ART_DIR = paths.assets_dir() / "celestial" / "eclipse"
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

# THE PER-TYPE ECLIPSE ICONS (ART-INFRA round, owner 2026-07-20/21) —
# small dial-chrome badges distinct from the big category EMBLEM plate
# above (ECLIPSE_ART_DIR, untouched — these ride the hover-card's own
# eclipse LINE, `render.compositor._eclipse_hover_line`). LUNAR is the
# owner-APPROVED mapping: red=TOTAL, gold=PARTIAL, blue=PENUMBRAL —
# `assets/icons/moon_eclipse_{red,gold,blue}.png`.
ECLIPSE_LUNAR_TYPE_ICON = {
    "total": ICON_DIR / "moon_eclipse_red.png",
    "partial": ICON_DIR / "moon_eclipse_gold.png",
    "penumbral": ICON_DIR / "moon_eclipse_blue.png",
}


def eclipse_lunar_type_icon(type_: str) -> Path | None:
    """The small LUNAR eclipse type icon, or None for an unknown type
    or a file that has not landed — the SAME graceful-absent contract
    `icon_path` already guarantees (Rule #1)."""
    path = ECLIPSE_LUNAR_TYPE_ICON.get(type_)
    return path if path is not None and path.exists() else None


# SOLAR is a PROPOSED mapping (NOT owner-confirmed like lunar's red/
# gold/blue — flagged for his eye, COLORS section of DESIGN
# INSTRUCTIONS.txt: "razmotriti... da li treba drugu boju za
# distinktivnost"): the owner's three sun_eclipse variants read almost
# identically at icon size, so the pick follows each file's OWN shape —
# `sun_eclipse1.png` alone shows a bright ring hugging the black disc
# (the real "ring of fire" signature) so it wins ANNULAR; the canonical
# `sun_eclipse.png` (plain corona rays) wins TOTAL; `sun_eclipse2.png`
# (a broader, softer halo) wins PARTIAL. `render.asset_variants.
# eclipse_solar_type_icon` computationally TINTS the annular pick
# toward GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR (#FF7A1A, the SAME "ring of
# fire" color the dial's own annular glow already uses — Rule #5) for a
# clearer at-a-glance read; total/partial stay as drawn.
ECLIPSE_SOLAR_TYPE_ICON_SOURCE = {
    "total": ICON_DIR / "sun_eclipse.png",
    "annular": ICON_DIR / "sun_eclipse1.png",
    "partial": ICON_DIR / "sun_eclipse2.png",
}
ECLIPSE_TYPE_ICON_PX = 22   # the hover-line's small inline badge

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
    # THE CONTINENTS (owner-sealed matrix 2026-07-21): the six lands ride
    # the six weekday columns; its Encyclopedia topic is CUSTOM-built
    # (`app.encyclopedia._continents_topic`) rather than the generic
    # weekday shape, so it can carry the world-map title page and the
    # Atmosphere/Clean · Day/Night look switcher.
    "continents": "Continents",
    # The Inner Wheel dial themes; their ENCYCLOPEDIA topics stay the
    # emblem pages (the later family pass overwrites the weekday
    # topics built from these titles — deliberate).
    "virtues": "Virtues",
    "sins": "Sins",
    "moods": "Moods",
    # COMPLETION WAVE I (Session 31). "Chinese Mythology" is NOT the
    # existing "chinese" topic — that one is the twelve-animal ZODIAC
    # reading years; this is a seven-figure cast holding a week.
    "age_of_heroes": "Greek Monsters",
    "celestial_court": "Chinese Mythology",
    "corporate": "The Corporation",
    # COMPLETION WAVE II (Session 32). Each cast is its OWN dial theme
    # and needs a title that identifies itself in a FLAT list (the
    # Settings rotation grid has no group headings), so the franchise
    # leads and the faction follows. The Encyclopedia is the opposite
    # case and reads "World of Warcraft" once, with Alliance | Horde |
    # Evil on the variant switcher (encyclopedia_tree.VARIANT_SOURCES).
    "wow_alliance": "Warcraft Alliance",
    "wow_horde": "Warcraft Horde",
    "wow_evil": "Warcraft Evil",
    # COMPLETION WAVE II, Cyberpunk half (Session 32). Same rule as the
    # Warcraft half: each cast is its own dial theme and needs a title
    # that identifies itself in a FLAT list, so the franchise leads and
    # the block follows. The Encyclopedia reads "Cyberpunk 2077" once,
    # with Gangs | Street | Power on the variant switcher
    # (encyclopedia_tree.VARIANT_SOURCES).
    "cp_gangs": "Cyberpunk Gangs",
    "cp_street": "Cyberpunk Street",
    "cp_corpo": "Cyberpunk Power",
    # COMPLETION WAVE III (Session 33). Same rule a third time: each cast
    # is its own dial theme and needs a title that identifies itself in a
    # FLAT list, so the franchise leads and the block follows. The
    # Encyclopedia reads "Star Wars" once, with Jedi | Sith | Dyad on the
    # variant switcher (encyclopedia_tree.VARIANT_SOURCES). The sheet's
    # own set names — Svetla, Tamna, Nova — stay in the sheet: the
    # program's language is English (root Rule #17).
    "sw_jedi": "Star Wars Jedi",
    "sw_sith": "Star Wars Sith",
    "sw_dyad": "Star Wars Dyad",
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
    # Completion wave I (Session 31) joins the EXISTING kinship groups
    # rather than opening new ones: the two myth casts sit with the four
    # pantheons (`taxonomy.WEEK_GROUPS["myth"]` already holds all six),
    # and the Corporation sits beside the Professions — the same
    # `crafts` group on disk, and the same subject: offices people hold.
    # The "Films" group belongs to wave III.
    ("Ancient Gods", ("egypt", "greek", "norse", "slavic",
                      "age_of_heroes", "celestial_court")),
    ("Society", ("profession", "corporate", "religion", "religion_alt")),
    # The Scripture family (owner 2026-07-14).
    ("Scripture", ("bible", "bible2", "bible_dark")),
    # GAMING — opened by completion wave II (Session 32), matching
    # `taxonomy.WEEK_GROUPS["gaming"]` on disk. The three WoW casts were
    # its first members; the three Cyberpunk casts joined in the same
    # wave's second half, and the group stays ONE picker submenu for
    # both franchises (the kinship is the medium, not the setting) —
    # the same order `taxonomy.WEEK_GROUPS["gaming"]` already lists.
    ("Gaming", ("wow_alliance", "wow_horde", "wow_evil",
                "cp_gangs", "cp_street", "cp_corpo")),
    # FILMS — opened by completion wave III (Session 33, 2026-07-29),
    # matching `taxonomy.WEEK_GROUPS["films"]` on disk and closing the
    # backlog's list of new picker groups (checklist line 12 named
    # exactly two: Gaming and Films). It stays a group of its own rather
    # than joining Gaming for the reason the Gaming comment gives — the
    # kinship is the MEDIUM, and a film is not a game.
    ("Films", ("sw_jedi", "sw_sith", "sw_dyad")),
    ("Animals", ("wolf", "elephant", "bee")),
    # The emblem families on the dial (owner 2026-07-14).
    ("The Inner Wheel", ("virtues", "sins", "moods")),
    # Planets moved to WEEKDAY_MENU_TOP (owner 2026-07-18) — Arcana now
    # holds only the remaining three, plus the Continents (the world
    # itself, sitting beside the deep-sky Cosmos — owner 2026-07-21).
    ("Arcana", ("alchemy", "japan", "cosmos", "continents")),
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
        fill=palette.SKIN_RING_FILL,
        text_color=palette.SKIN_RING_TEXT,
        letter_color=palette.SKIN_RING_LETTER,
        width_fraction=0.16,
        letters={12: "M", 20: "Y", 0: "Ω", 4: "D"},
    ),
    weekday_set=WeekdaySpec(
        bodies={name: weekday_art(f"planets/primary/photo/{name.capitalize()}.png") for name in (
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
        body_colors=palette.SKIN_PLANET_BODY_COLORS,
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
            f"{style}_{continent}_{phase}": EARTH_ART_DIR
            / f"earth_{style}_{continent}_{phase}.png"
            for style in ("clean", "atmo")
            for continent in _CONTINENTS
            for phase in ("day", "night")
        },
        default_variant="europe",
        day_color=palette.SKIN_EARTH_DAY,
        night_color=palette.SKIN_EARTH_NIGHT,
        # Owner spec: the Earth's outer edge TOUCHES the ring's inner
        # edge (0.75 + 0.11 = 0.86 = the disc radius), same size as the
        # weekday planets.
        orbit_fraction=0.75,
        scale=0.11,
        moon_asset=weekday_art("planets/primary/photo/Moon.png"),
        moon_lit_color=palette.SKIN_MOON_LIT,
        moon_dark_color=palette.SKIN_MOON_DARK,
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
            asset=paths.assets_dir() / "instrument" / "hands" / "classic" / "hours.png",
            natural_height=246, pivot_y=17,
        ),
        minute=HandSpec(
            asset=paths.assets_dir() / "instrument" / "hands" / "classic" / "minutes.png",
            natural_height=295, pivot_y=17,
        ),
        second=HandSpec(
            asset=paths.assets_dir() / "instrument" / "hands" / "classic" / "seconds.png",
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


# --- THE INSTRUMENT'S OWN DIAGRAMS (Session 27 coverage round, 2026-07-29) ----
# The seven "how this clock works" pages plus the Great Oscillations are
# COMPUTED, not painted (root Rule #19 — see render/instrument_diagrams.py).
# These are that module's only tunables; every astronomical number in the
# figures comes from `config.constants` or from the bundles themselves.
INSTRUMENT_DIAGRAM_SIDE_PX = 900        # the drawing's own square, then scaled
INSTRUMENT_DIAGRAM_MARGIN_PX = 8        # no label is drawn past this edge
INSTRUMENT_DIAGRAM_RING_RATIO = 0.34    # the dial circle's radius, per side
INSTRUMENT_DIAGRAM_YEAR_RING_RATIO = 0.27  # ...tighter on the year wheel,
#                                          whose anchor names are long and
#                                          two of them stand at the widest
#                                          point of the disc
INSTRUMENT_DIAGRAM_LABEL_RATIO = 0.026  # a label's pixel size, per side
INSTRUMENT_DIAGRAM_CAPTION_RATIO = 0.022
INSTRUMENT_DIAGRAM_CAPTION_Y = 0.90     # where the one-line caption sits
INSTRUMENT_DIAGRAM_GLYPH_RATIO = 0.075  # a ring letter, per side
INSTRUMENT_DIAGRAM_MOON_RATIO = 0.045   # one phase disc's radius, per side
INSTRUMENT_DIAGRAM_PHASE_STEPS = 8      # phases shown around the lunation
INSTRUMENT_DIAGRAM_CHART_INSET = 0.10   # the envelope plot's own margin
INSTRUMENT_DIAGRAM_CHART_HEIGHT = 0.62  # ...and its height, per side
# The moment drawn on the dial figure — any time whose two hands stand
# clearly apart reads the lesson (the hour hand is on ITS OWN 24-hour
# turn, the minute hand on the hour's).
INSTRUMENT_DIAGRAM_SAMPLE_TIME = (15, 20)
# The solar tilt drawn on the rotation figure: the project's own golden
# value (Belgrade under DST, tests/test_dial.py) rather than a made-up
# angle — the figure is a measurement.
INSTRUMENT_DIAGRAM_SAMPLE_TILT_DEG = 10.76
# THE TWILIGHT BANDS: (from, to, name) in degrees of solar depression.
# Civil comes from `constants.CIVIL_DEPRESSION` — the one the dial
# actually draws; the other two boundaries are the standard astronomical
# definitions and live here because nothing else in the program needs
# them.
INSTRUMENT_TWILIGHT_BANDS = (
    (0.0, constants.CIVIL_DEPRESSION, "civil"),
    (constants.CIVIL_DEPRESSION, 12.0, "nautical"),
    (12.0, 18.0, "astronomical"),
)
