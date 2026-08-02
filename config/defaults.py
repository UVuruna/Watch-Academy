"""Developer tunables — values a developer may adjust while tuning the app.

Everything here is read-only at runtime. User-changeable state (window
position, chosen city, chosen skin) lives in the user settings file owned
by app/settings_store.py.

Layer: config — pure, no Qt, no wall clock.

Session 36 (WORKPLAN-STRUCTURE.md, "The Config Split") carved six
single-responsibility modules out of this file (dial, shortcuts,
pantheon, calendar_mounts, encyclopedia_ui, glow) plus continents.py
(the pantheon deterministic fallback) -- see config/___config.md for
the remnant's own true contents. What stays here: app-level tunables
that don't fit any one new module's charter, and a handful of
COORDINATOR values/functions that legitimately need more than one new
module's data (dial_window_margin_fraction combines dial.py's ring/
letter/motto geometry with glow.py's own glow extent; ECLIPSE_SOLAR_ART
needs pantheon.py's weekday_art) -- the fixed import DAG lets a new
module import only stdlib + config.{paths, constants, palette}, never
each other and never this file, so a value two new modules both need
either gets duplicated (forbidden) or stays here, which the remnant may
import downhill from any of them.
"""

import re
from datetime import date
from pathlib import Path
from typing import NamedTuple

from config import (
    calendar_mounts,
    constants,
    continents,
    dial,
    encyclopedia_ui,
    glow,
    palette,
    pantheon,
    paths,
)
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

# ═══════════════════════════ COORDINATOR VALUES ═══════════════════════════
# ECLIPSE_SOLAR_ART lives here, not in glow.py: its value is
# `pantheon.weekday_art(...)`, and a new module may never import
# another new module (the fixed DAG) -- this is the one place
# that may import pantheon.py downhill.
ECLIPSE_SOLAR_ART = pantheon.weekday_art(
    "planets/primary/photo/Sun_Eclipse.png"
)                                            # source-mapped by paths.art_file

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


# --- Settings persistence ----------------------------------------------------
SETTINGS_SCHEMA_VERSION = 1
SETTINGS_WRITE_DEBOUNCE_MS = 750     # collapse rapid moveEvent bursts while dragging


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


# THE PER-TYPE ECLIPSE ICONS (ART-INFRA round, owner 2026-07-20/21) —
# small dial-chrome badges distinct from the big category EMBLEM plate
# (glow.ECLIPSE_ART_DIR, untouched — these ride the hover-card's own
# eclipse LINE, `render.compositor._eclipse_hover_line`). LUNAR is the
# owner-APPROVED mapping: red=TOTAL, gold=PARTIAL, blue=PENUMBRAL —
# `assets/icons/moon_eclipse_{red,gold,blue}.png`. Lives here (not
# glow.py): it keys off ICON_DIR, which glow.py may not import (the
# fixed DAG — new modules never import each other).
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

                                     # bigger than the tint swatches)

# ═══════════════════════════ SETTINGS NAV & WORKING SET CEILINGS ═══════════════════════════
# The Settings dialog's NAVIGATION COLUMN (owner ROADMAP 15h item 1,
# 2026-07-18): a left list of section TITLES, each opening its panel on
# the right — replacing the old one-long-scroll layout.
SETTINGS_NAV_WIDTH_PX = 170


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

# ═══════════════════════════ BACKGROUND WARM ═══════════════════════════
# The art-ledger drain's thread pool CAP (0.14.704, the slow-render
# session): numpy releases the GIL inside its C loops, so N letter
# recolors genuinely overlap; capped low because each worker holds a
# full-plate float pipeline in memory and the drain shares the machine
# with the GUI thread. The effective count is min(cap, cpu_count).
ART_DRAIN_WORKERS = 4

# ═══════════════════════════ TIME TRAVEL & REVEAL TIMING ═══════════════════════════
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


# ═══════════════════════════ SUBDIAL SOLO RECOLOR ═══════════════════════════
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

# ═══════════════════════════ THE REPORT WINDOW ═══════════════════════════
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
        dial.GLOW_RING_RADIUS_FRACTION
        + marker * glow.GLOW_RADIUS_SCALE * skin.hover_enlarge
    )
    letter_extent = (
        dial.RING_LETTER_RADIUS_FRACTION
        + dial.RING_LETTER_ART_SCALE * skin.ring_letter_scale
        * (1.0 + 2.0 * dial.RING_LETTER_SHADOW_RADIUS)
    )
    motto_extent = 0.0
    if skin.ring.motto:
        motto_extent = (
            dial.RING_MOTTO_RADIUS_FRACTION
            + dial.RING_MOTTO_SIZE * skin.ring_letter_scale
            * (1.0 + 2.0 * dial.RING_LETTER_SHADOW_RADIUS)
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


# ═══════════════════════════ METAL SHADE RAMPS ═══════════════════════════
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


# --- Default render config --------------------------------------------------------
# The ONE typed SkinDefinition the compositor consumes; the controller
# overlays the ring preset and the user's display choices onto it.

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
        asset=dial.RING_FACE_DIR / "domy.png",
        fill=palette.SKIN_RING_FILL,
        text_color=palette.SKIN_RING_TEXT,
        letter_color=palette.SKIN_RING_LETTER,
        width_fraction=0.16,
        letters={12: "M", 20: "Y", 0: "Ω", 4: "D"},
    ),
    weekday_set=WeekdaySpec(
        bodies={name: pantheon.weekday_art(f"planets/primary/photo/{name.capitalize()}.png") for name in (
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
            f"{style}_{continent}_{phase}": continents.EARTH_ART_DIR
            / f"earth_{style}_{continent}_{phase}.png"
            for style in ("clean", "atmo")
            for continent in continents._CONTINENTS
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
        moon_asset=pantheon.weekday_art("planets/primary/photo/Moon.png"),
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
        minute_reach_fraction=dial.HAND_MINUTE_REACH_FRACTION,
        second_reach_fraction=dial.HAND_SECOND_REACH_FRACTION,
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
