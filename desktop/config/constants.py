"""Product-defining invariants. These values NEVER change at runtime
and are not user-tunable — they define what Watch Academy is.

The WEEKDAY theme tables here are DERIVED: `config.registry` holds one
entry per theme and every table below is computed from it in a single
assignment (owner decree 2026-08-01). The names stay because the
program reads them everywhere; the data has exactly one home.

Tunables (things a developer might reasonably adjust) live in defaults.py.
Win32 API literals live in winapi.py.
"""

from config import registry

# ═══════════════════════════ APP IDENTITY ═══════════════════════════

# ═══════════════════════════ WEEKDAY THEMES ═══════════════════════════
# Weekday body themes (SYMBOLISM.md canon): "planets" uses the skin's
# own weekday unit; the others swap in the owner's themed art from
# assets/skins/domy/weekday/<theme>/ with the canon display names.
WEEKDAY_THEMES = registry.THEMES

# ═══════════════════════════ THEME BLURBS & ARTICLES ═══════════════════════════
# Theme -> symbolism.json blurb key (the encyclopedic text under the
# hexa diamond hover follows the active theme).
WEEKDAY_THEME_BLURBS = registry.BLURBS

# Theme -> symbolism.json article set (the glyph theme shares the
# planet articles — same entities, different art).
WEEKDAY_THEME_ARTICLES = registry.ARTICLES

# ═══════════════════════════ THE NINTH TABLES ═══════════════════════════
# THE NINTH per weekday theme (CANON.md "The Ninth — Outside the
# Circle"; owner 8+1 doctrine 2026-07-14): (display name, plate path
# RELATIVE to WEEKDAY_ART_DIR). Themes absent from this table (planets,
# planet_signs, japan, virtues, sins, moods) run DUAL-only — two faces,
# no Ninth. Extracted round R3b (item 3) as the ONE shared table the
# Encyclopedia's ninths pass (app.encyclopedia) and the CENTER seat's
# solar-window face law (render.layers/compositor) both read — a
# parallel copy would drift the moment either side's roster changes
# (Rule #5). The zodiac-only ninths (Chinese "The Cat", Astrology
# "Ophiuchus") stay OUT of this table on purpose — they carry no
# weekday Sunday duality, so the render side never needs them.
WEEKDAY_THEME_NINTHS = registry.NINTHS

# THE PANGEA EASTER EGG (owner-sealed matrix 2026-07-21; trigger WIDENED
# to every principal moon phase 2026-07-29): Pangea shows INSTEAD of
# Zealandia on the Ninth seat ONLY when the sky is doing something on
# the traveled day — an eclipse, a season turning point, or a principal
# moon-phase day (full, new, or either quarter — core.continents'
# `pangea_over_zealandia`). Same story, deeper time: was once ALL,
# split, and by the supercontinent cycle will return. The LAW lives in
# core.continents; render.ninths.theme_ninth reads this alt table when
# the law fires (mechanism "easter_egg" below). Plate wired ahead of the
# owner's art (graceful-absent), same earth-family home as Zealandia.
WEEKDAY_THEME_NINTH_EASTER_EGG = registry.NINTH_EASTER_EGG

# THE DYAD'S NIGHT FACE (owner Double-Ninth verdict, 2026-07-29):
# sw_dyad's Ninth is a DAYLIGHT/NIGHT switch, not a date rotation — day
# shows the canonical `WEEKDAY_THEME_NINTHS["sw_dyad"]` entry (The
# Ghosts, the good side), night shows Exegol from this table (the
# owner's words: "the duality of that theme pulling the actors to one
# of two sides"). Mirrors `WEEKDAY_THEME_NINTH_EASTER_EGG`'s shape —
# theme -> (display name, plate) — read by `render.ninths.theme_ninth`
# when the mechanism dispatch (`NINTH_MECHANISMS` below) resolves to
# "daynight". Plate wired ahead of the owner's art (graceful-absent);
# neither Ghosts nor Exegol has landed yet.
WEEKDAY_THEME_NINTH_NIGHT = registry.NINTH_NIGHT

# ═══════════════════════════ NINTH MECHANISMS ═══════════════════════════
# THE DOUBLE NINTH LAW (standing law, owner decree 2026-07-29): a theme
# may mount a DOUBLE NINTH — two faces contending for the ONE seat —
# only with a DEFINED alternation mechanism, and every reader (the dial,
# its hover, the Encyclopedia) shows ONLY the currently active face,
# never both at once. `NINTH_MECHANISMS` names, per theme, WHICH
# mechanism governs its double Ninth (and, for "term_weekly", its whole
# synchronized Throne/Mirror/Ninth triple — the name stays "NINTH_" for
# historical continuity with the seat it was coined for):
#
# - "easter_egg"  — a SKY trigger (`core.continents.pangea_over_
#   zealandia`): the alt face surfaces only when an eclipse, a turning
#   point or a principal moon phase lands on the traveled day.
# - "daynight"    — the SAME daylight state `render.ninths.center_face`
#   reads (`TickState.is_daylight`): day the canonical face, night the
#   alt (`WEEKDAY_THEME_NINTH_NIGHT`).
# - "term_weekly" — cp_corpo's WEEKLY MANDATE: the traveled date's ISO
#   calendar week PARITY decides which half of the seat roster rules —
#   even week the canonical (Arasaka) triple, odd week the alternate
#   (NUSA) triple — for its Throne, Mirror AND Ninth together (the
#   existing `WEEKDAY_SEAT_ROSTERS`/`rotating_art_file` chokepoint,
#   cadence swapped from daily to weekly; `config.defaults.
#   _pick_weekly_mandate`). No separate alt TABLE — the roster already
#   names both halves, only the picker's cadence changes.
#
# A theme absent from this table has no double Ninth at all (the plain
# single canonical entry in `WEEKDAY_THEME_NINTHS`). `NINTH_MECHANISM_
# KINDS` is the vocabulary every dispatch above actually implements
# (`render.ninths.ninth_table_for`/`ninth_alt_active`, `render.
# compositor._center_ninth_alt`, `config.pantheon.rotating_art_file`'s
# cadence override) — `tests/test_ninth_mechanisms.py` fails the build
# if `NINTH_MECHANISMS` ever names anything outside it, or if a double
# Ninth found in ANY registry above has no entry here at all.
NINTH_MECHANISMS = registry.MECHANISMS
NINTH_MECHANISM_KINDS = frozenset({"easter_egg", "daynight", "term_weekly"})

# ═══════════════════════════ DUAL/NINTH TIME WINDOW ═══════════════════════════
# THE DUAL/NINTH TIME WINDOW (owner seal 2026-07-29, superseding
# INSTRUCTION #5's hour widths): half an hour either side of the day's
# SOLAR anchors (never wall-clock — `core.angles.hours_between` reads
# the actual `DayContext.sun.noon`), i.e. solar 11:30-12:30 and
# 23:30-00:30. In BOTH windows the NINTH shows; outside them the
# CENTER seat follows the sky itself — DAYLIGHT the Ruler, NIGHT the
# Servant (`render.ninths.center_face`) — and a two-badge Sunday swaps
# ONE seat per window (`render.ninths.dual_seat_ninth`: near noon the
# Ninth replaces the SERVANT beside the Ruler, near midnight the RULER
# beside the Servant). Themes with no Ninth ignore the windows.
CENTER_WINDOW_HOURS = 0.5

# ═══════════════════════════ ZODIAC & CHINESE CALENDAR ═══════════════════════════
# Chinese zodiac (sexagenary cycle): the animal repeats every 12 years,
# the element every 10 (two years per element). Year N maps via
# (N - 4) % 12 and ((N - 4) % 10) // 2 — 2026 = Fire Horse. The Chinese
# year starts at the new moon falling between Jan 21 and Feb 20 (China
# time), derived from the bundled principal-phase instants.
CHINESE_ANIMALS = (
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig",
)
CHINESE_ELEMENTS = ("Wood", "Fire", "Earth", "Metal", "Water")
CHINESE_NEW_YEAR_WINDOW = ((1, 21), (2, 20))   # (month, day) bounds, China time
CHINA_UTC_OFFSET_HOURS = 8

# THE CHINESE MONTH-BRANCH ANIMALS (owner R12, "Mount Chinese zodiac"):
# the traditional solar-term month branches — Yin (Tiger) begins at
# lichun (start of spring, ~Feb 4) and each subsequent branch begins at
# the next "jie" solar term, ~30 days apart; Zi (Rat) begins at daxue
# (~Dec 7) and so holds the December solstice, which is why the
# classical calendar calls that lunar month "the eleventh"
# (core.blue_moon.chinese_leap_month reads the SAME fact). Each solar
# term's start nearly always falls in the FIRST week of its Gregorian
# month, so — exactly like calendar_mounts.SLAVIC_MONTHS mounts by Gregorian
# month rather than by the true (locally-drifting) bloom date — this
# table fixes ONE animal per Gregorian month for the static 12-wedge
# mount; the LIVE lunar month (core.moon.chinese_zodiac) is unaffected.
CHINESE_MONTH_BRANCH_ANIMALS = {
    1: "Ox", 2: "Tiger", 3: "Rabbit", 4: "Dragon", 5: "Snake", 6: "Horse",
    7: "Goat", 8: "Monkey", 9: "Rooster", 10: "Dog", 11: "Pig", 12: "Rat",
}
# THE BRANCH'S TRUE SPAN (owner 2026-08-05: "na hoveru će stajati tačan
# datum od kad do kad"). A branch does NOT run from the 1st to the 31st:
# it opens on its own "jie" solar term and closes the day before the
# next one. Gregorian month -> (month, day, the term's name) of the day
# it OPENS; the CLOSE is computed as the day before the next branch's
# term (`chinese_branch_span`), so the twelve can never disagree about
# a boundary.
#
# The dates are the traditional Gregorian ones and drift by about a day
# with the leap cycle — which is why the hover says "approx." and why
# the MOUNT itself stays keyed to the Gregorian month (the wedge is a
# fixed seat; only the words are the astronomy).
CHINESE_BRANCH_TERMS = {
    1: (1, 6, "Xiaohan"),      # Minor Cold — the Ox
    2: (2, 4, "Lichun"),       # Start of Spring — the Tiger opens the cycle
    3: (3, 6, "Jingzhe"),      # Awakening of Insects — the Rabbit
    4: (4, 5, "Qingming"),     # Clear and Bright — the Dragon
    5: (5, 6, "Lixia"),        # Start of Summer — the Snake
    6: (6, 6, "Mangzhong"),    # Grain in Ear — the Horse
    7: (7, 7, "Xiaoshu"),      # Minor Heat — the Goat
    8: (8, 8, "Liqiu"),        # Start of Autumn — the Monkey
    9: (9, 8, "Bailu"),        # White Dew — the Rooster
    10: (10, 8, "Hanlu"),      # Cold Dew — the Dog
    11: (11, 7, "Lidong"),     # Start of Winter — the Pig
    12: (12, 7, "Daxue"),      # Major Snow — the Rat, which is why the
                               # classical calendar calls that lunar
                               # month "the eleventh"
}

def chinese_branch_span(month: int) -> tuple[tuple[int, int], tuple[int, int], str]:
    """((open month, open day), (close month, close day), term name) of
    one branch — the close is the day before the NEXT branch's term, so
    the twelve tile the year with no gap and no overlap."""
    open_month, open_day, term = CHINESE_BRANCH_TERMS[month]
    next_month, next_day, _next_term = CHINESE_BRANCH_TERMS[month % 12 + 1]
    if next_day > 1:
        close = (next_month, next_day - 1)
    else:                       # a term on the 1st closes the month before
        close = ((next_month - 2) % 12 + 1, 28)
    return (open_month, open_day), close, term

# Tropical zodiac: (name, symbol), indexed by dial angle // 30 on the
# year wheel — Cancer's first point IS the summer solstice (dial top),
# Capricorn's the winter solstice (bottom), Aries' the spring equinox.
# Sign boundaries are exact 30-deg arcs of the same piecewise-linear
# year wheel, i.e. anchored on the REAL season instants.
ZODIAC_SIGNS = (
    ("Cancer", "♋"),
    ("Leo", "♌"),
    ("Virgo", "♍"),
    ("Libra", "♎"),
    ("Scorpio", "♏"),
    ("Sagittarius", "♐"),
    ("Capricorn", "♑"),
    ("Aquarius", "♒"),
    ("Pisces", "♓"),
    ("Aries", "♈"),
    ("Taurus", "♉"),
    ("Gemini", "♊"),
)
ZODIAC_SPAN_DEG = 30.0

# --- THE BLUE MOON LAW (owner-sealed 2026-07-22) ------------------------------
# The 13th member of every 12-set — hidden except in a blue-moon year
# (core.blue_moon.thirteen_moon_year: the calendar year holds 13 Full
# Moons, ~37% of years) AND inside its own short date window. `key` ->
# (display name, encyclopedia family, encyclopedia entry name) — the
# SAME two-level lookup WEEKDAY_THEME_NINTHS uses for its (name, path),
# read by both the dial (render.ninths.thirteenth_plate) and its hover
# (render.compositor). "chinese" (The Cat) is NOT solar-triggered — see
# core.blue_moon.chinese_leap_month — it shares this table only because
# it shares the CENTER seat.
#
# THE AXLE LAW (CANON.md §The Axle, owner-sealed 2026-07-29) extends this
# SAME table with the ALWAYS-CENTERS — Hestia/Jesus/Prudence/Cunning/
# Peace/Hardness of Heart — the throne/hiding-place axles of the
# Olympians, Apostles, Virtue Wheel (both registers), Emotions and Sins
# Dozens. (Named `PERSON_CENTERS` on 2026-07-29 and RENAMED the same
# day: Peace and Hardness of Heart are STATES, not persons — the seam
# THE AXLE LAW draws is "not a leftover month", never personhood.)
# Unlike the four members above,
# they carry NO year-rule at all: `AXLE_ALWAYS_CENTERS` below marks them
# unconditionally present (core.blue_moon.thirteenth_candidates unions it
# in, never gated by a trigger+window). `family`/`article` are `None`
# where no Encyclopedia article has been written yet (Hestia alone
# already has one, under "wider" — the A-list pantheon figures written
# for exactly this axle story) — a caller reading THIRTEENTHS must treat
# `None` the SAME graceful-absent way a missing art plate is treated
# (render.compositor._thirteenth_tooltip skips the encyclopedia lookup
# entirely rather than crash on an unwritten entry).
THIRTEENTHS = {
    "ophiuchus": ("Ophiuchus", "ninths", "Ophiuchus"),
    "chinese": ("The Cat", "ninths", "The Cat"),
    "sol": ("Sol", "months", "Sol"),
    "modrenik": ("Modrenik", "months", "Modrenik"),
    "hestia": ("Hestia", "wider", "Hestia"),
    "jesus": ("Jesus", None, None),
    "prudence": ("Prudence", None, None),
    "cunning": ("Cunning", None, None),
    "peace": ("Peace", None, None),
    "hardness_of_heart": ("Hardness of Heart", None, None),
}
# THE AXLE LAW's ALWAYS-PRESENT half (CANON §The Axle: "ALWAYS-CENTERS
# stand on EVERY date... no moon count, no window") — every key here is
# unconditionally a member of `core.blue_moon.thirteenth_candidates` on
# every date, regardless of year or window, unlike the four calendar-
# driven keys above (whose sealed year-rules are untouched by this set).
AXLE_ALWAYS_CENTERS = frozenset({
    "hestia", "jesus", "prudence", "cunning", "peace", "hardness_of_heart",
})
# Year-agnostic (month, day) bounds, inclusive both ends — core.blue_moon
# stamps the trigger year on. Ophiuchus: the astronomical transit (the
# Sun's real path through the constellation, Nov 29 - Dec 17). Sol:
# carries the June solstice (International Fixed Calendar's Year Day
# analogue — CANON's "the Sun's thirteenth at the year's top").
OPHIUCHUS_WINDOW = ((11, 29), (12, 17))
SOL_WINDOW = ((6, 18), (7, 15))
# Modrenik has no fixed calendar dates — it is computed FROM the real
# December solstice instant (core.year_wheel.YearAnchors), this many
# days either side ("CANON's the Moon's thirteenth at the year's
# bottom" — honest across years, unlike a fixed MM-DD pair).
MODRENIK_WINDOW_HALF_DAYS = 14

# ═══════════════════════════ GLOW WINDOWS & ECLIPSE VISIBILITY ═══════════════════════════
# Season/moon event glow windows (owner spec): the Earth marker glows
# ±12 h around the four season instants, the Moon marker ±6 h around the
# four principal phase instants. The phase NAME window stays ±12 h
# (MOON_PRINCIPAL_WINDOW above).
SEASON_GLOW_WINDOW_H = 12.0
MOON_GLOW_WINDOW_H = 6.0
# Eclipse display (owner 2026-07-18, ROADMAP 15h item 11): the sealed
# ±3h window, same shape as the season/moon windows above but its own
# constant (the owner's spec is explicitly ±3h, not the moon's ±6h).
ECLIPSE_GLOW_WINDOW_H = 3.0
# THE ECLIPSE BODY's own, WIDER window (owner ballot verdict 2026-08-12,
# option B2 with his written correction "+-12h"): the eclipse now stands
# on the dial as a THIRD celestial body at the hour it happens
# (`render.layers.year_marker.YearMarkerLayer._draw_eclipse_body`), and a
# body that only appeared three hours before its own instant would keep
# the dial silent for most of the day that carries the eclipse. Twelve
# hours is his number, and it is the SEASON window's number too — half a
# day either side, so an eclipse is on the dial for the whole span in
# which its own date is the current one.
ECLIPSE_BODY_WINDOW_H = 12.0

# Eclipse VISIBILITY (owner verdict "može", fix round E, 2026-07-19):
# a SOLAR eclipse is visible to the observer only within this great-
# circle distance of the catalog's greatest-eclipse point (the path of
# totality/partiality does not reach much farther); LUNAR visibility has
# no distance term — a lunar eclipse is visible from the whole night
# hemisphere, so only "Moon above the horizon" gates it.
ECLIPSE_SOLAR_VISIBILITY_KM = 3500.0
EARTH_RADIUS_KM = 6371.0            # mean radius — the great-circle distance basis

# ═══════════════════════════ TRANSLATION LANGUAGES ═══════════════════════════
# Languages offered in Settings (owner: "all the provider offers") —
# the Google-translate codes the gtx endpoint accepts, code -> English
# display name. ORIGINALS (owner decision 2026-07-11) ship hand-written
# in the app (Database/translations/) and sit pinned at the top of the
# combo; every other language machine-translates on first pick.
TRANSLATION_ORIGINALS = ("en", "sr-Latn")
TRANSLATION_LANGUAGES = {
    "en": "English",
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "hy": "Armenian", "az": "Azerbaijani", "eu": "Basque",
    "be": "Belarusian", "bn": "Bengali", "bs": "Bosnian",
    "bg": "Bulgarian", "ca": "Catalan", "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)", "hr": "Croatian", "cs": "Czech",
    "da": "Danish", "nl": "Dutch", "eo": "Esperanto", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "gl": "Galician", "ka": "Georgian",
    "de": "German", "el": "Greek", "gu": "Gujarati", "he": "Hebrew",
    "hi": "Hindi", "hu": "Hungarian", "is": "Icelandic",
    "id": "Indonesian", "ga": "Irish", "it": "Italian", "ja": "Japanese",
    "kn": "Kannada", "kk": "Kazakh", "ko": "Korean", "lv": "Latvian",
    "lt": "Lithuanian", "mk": "Macedonian", "ms": "Malay",
    "ml": "Malayalam", "mt": "Maltese", "mr": "Marathi",
    "mn": "Mongolian", "ne": "Nepali", "no": "Norwegian",
    "fa": "Persian", "pl": "Polish", "pt": "Portuguese",
    "pa": "Punjabi", "ro": "Romanian", "ru": "Russian",
    "sr": "Serbian (Cyrillic)", "sr-Latn": "Serbian (Latin)",
    "sk": "Slovak", "sl": "Slovenian", "es": "Spanish",
    "sw": "Swahili", "sv": "Swedish", "ta": "Tamil", "te": "Telugu",
    "th": "Thai", "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu",
    "uz": "Uzbek", "vi": "Vietnamese", "cy": "Welsh",
}

# ═══════════════════════════ UI SCALE & SATURATION RANGES ═══════════════════════════
# The Encyclopedia's Ctrl+MouseWheel ZOOM (owner round R8b item 5b:
# "uvodimo novu funkcionalnost CTRL + MOUSHE WHEEL... za smanjenje
# svega ili povecanje" — one factor scaling fonts, images and gallery
# tiles together). The RANGE bounds are the fixed product invariant
# (same pattern as ELEMENT_SCALE_RANGE above); the live factor itself
# is session-only state on `app.encyclopedia` (never written to
# settings — the owner asked for "the session at least", not
# persistence across restarts). STEP is the zoom delta per wheel notch
# (Qt reports ±120 angleDelta per notch — one notch = one STEP).
ENCYCLOPEDIA_ZOOM_RANGE = (0.6, 2.5)
ENCYCLOPEDIA_ZOOM_STEP = 0.1

# Element size multipliers (Settings sliders, owner EXTRAS) and the
# shared hover-enlarge factor (the element under the cursor draws this
# much larger; 1.0 disables the effect).
ELEMENT_SCALE_RANGE = (0.5, 2.0)
HOVER_ENLARGE_RANGE = (1.0, 2.0)
# The Saturation sliders (owner 2026-07-18, Settings ▸ Colors, Session
# 21-D — moved out of Display/Element sizes into their OWN "Saturation"
# group beside Palette + Ring tint): 0.0 grays the target to its own
# brightness, 1.0 is the owner preset unchanged. The slider itself is
# 0-100; the stored setting is the 0.0-1.0 factor.
# POINTER (formerly "palette_saturation" — renamed for clarity now that
# a second, independent RING slider exists): the Star+Aura palette's
# HSV saturation (`render.skin_geometry.palette_for`).
POINTER_SATURATION_RANGE = (0.0, 1.0)
POINTER_SATURATION_SLIDER_STEP = 1
# RING (new, Session 21-D): the ring band art's HSV saturation — the
# ring plate AND its letter/numeral overlay (`render.layers.ring.RingLayer`,
# after the ring_tint recolor). The Umbra and hands do not read this —
# see layers.md's RingLayer note for the ground-truthed scope.
RING_SATURATION_RANGE = (0.0, 1.0)
RING_SATURATION_SLIDER_STEP = 1
# HANDS (Watch Face Phase 4, R-25): the hand pack's own HSV saturation,
# independent of the ring's — `render.layers.hand.HandLayer` reads it
# alongside its existing `desaturate`/`tint` pipeline (the SAME
# `AssetCache.pixmap_by_height` saturation parameter the ring already
# uses, a bounded reuse — no new recolor math).
HANDS_SATURATION_RANGE = (0.0, 1.0)
HANDS_SATURATION_SLIDER_STEP = 1
# UMBRA (Watch Face Phase 4, R-25): scales the Umbra TINT's own HSV
# saturation before the black->tint->white tritone map runs
# (`render.skin_geometry.saturate_hue`, reused from the Aura's — Rule
# #5) — 0.0 grays the active tint to a plain neutral, 1.0 unchanged.
# A no-op while the Umbra follows Gray (tint is None): there is no hue
# to desaturate.
UMBRA_SATURATION_RANGE = (0.0, 1.0)
UMBRA_SATURATION_SLIDER_STEP = 1

# ═══════════════════════════ DUALITY SEATING ═══════════════════════════
# The SOUTH SLOT home angle and the Aurora DUAL layout (owner spec
# 2026-07-12): with BOTH the weekday body and the slot on, they flank
# the bottom ±45° — the weekday at 3h on the left, the slot at 21h on
# the right.
#
# STALE-COMMENT CORRECTION (owner 2026-07-27): this comment used to
# claim "the Compass reserves this bottom arm for it". It has not been
# true since the dual-Sunday round — the Compass shows all EIGHT arms,
# and its 24h seat belongs to the SERVANT face of Sunday
# (`render.slot_layout.servant_holds_the_seat`), which is exactly why
# `POINTER_WEEKDAY_SLOTS["octa"]` has no 180° entry. A later change
# moved the truth and left the old sentence standing, and a session
# read it and believed it. When behavior moves, the sentence that
# described the old behavior DIES WITH IT.
SOUTH_SLOT_ANGLE = 180.0
# The SERVANT face's own seat per pointer (owner 2026-07-27): 24h
# everywhere the dual Sunday has always sat, but the ROSE seats him on
# the BLUE arm at 06h — blue is Judas's hue and the servant's, red is
# Lucifer's and the master's, and 6 + 6 + 6 lands the pair on 06h and
# 18h (CUBE.md §The Rose). `render.skin_geometry.servant_seat_angle` is the
# ONE reader (Rule #5); absent = SOUTH_SLOT_ANGLE.
SERVANT_SEAT_ANGLE = {"rose": 270.0}
AURORA_DUAL_WEEKDAY_ANGLE = 225.0    # 3h — bottom left
AURORA_DUAL_SLOT_ANGLE = 135.0       # 21h — bottom right

# THE DUALITY-AXES CONFIG (owner decree 2026-07-28, CUBE.md §The
# Thirteen Axes — Display Plans). Every weekday theme's Sunday duality
# rides an axis whose two ends are Cube poles: VERTICAL (yellow-top/
# 12h <-> purple-bottom/24h) on the Compass and the Seasons, HORIZONTAL
# (blue-06h <-> red-18h, the Sunday axis) on the Rose instead. The
# default law is unconditional on the vertical axis — the Ruler
# (`WEEKDAY_DUAL_NAMES[theme][0]`) always pulls to the warm pole
# (yellow/top) there, no per-theme override exists or is needed. Only
# the HORIZONTAL axis is per-theme, because a blind carryover of that
# same default (Ruler -> warm/red) is wrong wherever the Sacred Axis
# (CUBE.md §The Thirteen Axes) already assigns a member to the COLD
# trio: Christianity is the LUMINOUS COLD member (blue), Satanism the
# FALLEN WARM one (red) — the reverse of the blind default, which
# today seats Satanism blue and Christianity red. Listed themes pull
# their RULER to the cold pole instead; absent = the default carries
# over unchanged. `render.skin_geometry.ruler_seat_angle`/`servant_seat_angle`
# are the two readers (Rule #5) — they swap which of the Ruler's/
# Servant's figures rides which arm, never their names or articles.
DUALITY_RULER_ON_COLD_POLE = frozenset({"religion"})

# THE DUAL SUNDAY WHEEL MAP (owner seal 2026-07-29, closing the Session
# 23 miss — the per-WHEEL split was the whole point of the Duality-Axes
# decree and the Compass's third wheel never received it). Sunday's
# duality displays one of THREE ways, and the way is a property of the
# WHEEL, not only the pointer:
#   CENTER (one image; daylight Ruler / night Servant / Ninth in the
#     solar windows) — the Trinity and the Prism (all wheels), PLUS the
#     wheels below: the Quaternity's Seasons wheel turns its arms onto
#     the diagonals, leaving no 12h/24h seat to stand on.
#   VERTICAL 12h/24h (Ruler top in the light, Servant bottom in the
#     dark) — the Quaternity and the Compass, primary + secondary.
#   HORIZONTAL 06h/18h (Servant on blue left, Ruler on red right) — the
#     Rose (both wheels) PLUS the wheels below: the Compass's Character
#     wheel wears the very ROSE_PALETTE hues, so its Sunday rides the
#     same blue<->red axis and its bodies take the Rose's own hue seats
#     (`render.layers` reads POINTER_WEEKDAY_SLOTS["rose"] for it).
CENTER_DUALITY_WHEELS = frozenset({("cross", "tertiary")})
HORIZONTAL_DUALITY_WHEELS = frozenset({("octa", "tertiary")})

# THE GEOGRAPHIC VERTICAL FLIP (owner seal 2026-07-29, theme poll 23/23):
# themes whose VERTICAL duality seats the SERVANT on top — continents,
# because the Arctic IS the north and a globe reads north-up: Arctic
# (Servant) 12h, Antarctica (Ruler) 24h. The horizontal axis stays
# standard (18h red Antarctica, 06h blue Arctic). Same reader pair as
# DUALITY_RULER_ON_COLD_POLE; every OTHER theme was polled and sealed
# STANDARD the same day (Ruler top+red, Servant bottom+blue).
DUALITY_SERVANT_ON_TOP = frozenset({"continents"})
