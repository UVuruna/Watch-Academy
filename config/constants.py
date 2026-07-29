"""Product-defining invariants. These values NEVER change at runtime
and are not user-tunable — they define what DOMY Watch is.
from config import palette

Tunables (things a developer might reasonably adjust) live in defaults.py.
Win32 API literals live in winapi.py.
"""

APP_NAME = "DOMY Watch"
ORGANIZATION = "UVuruna"
SINGLE_INSTANCE_MUTEX = "DOMYWatch.SingleInstance"
# Windows taskbar/AppUserModelID identity (owner screenshot 2026-07-20):
# without an explicit ID, Windows groups every window this interpreter
# opens under python.exe's OWN identity and can fall back to ITS icon
# for the taskbar button — see app.native.set_app_user_model_id.
APP_USER_MODEL_ID = "UVuruna.DOMYWatch"

# --- Dial identity -----------------------------------------------------------
# The dial is a 24-hour clock face, CLOCKWISE, with 12:00 noon at the TOP
# and 00:00 midnight at the BOTTOM (18:00 right, 06:00 left).
HOURS_PER_REVOLUTION = 24
DIAL_TOP_HOUR = 12

SECONDS_PER_DAY = 86_400
SECONDS_PER_HOUR = 3_600

# Raw time-of-day angle has 00:00 at the top; the dial puts noon there.
DIAL_OFFSET_DEG = 180.0
SOLAR_NOON_SECS = 43_200            # 12:00 as seconds since local midnight
SECONDS_PER_DEGREE = SECONDS_PER_DAY / 360.0    # 240 s of day per dial degree

# Owner's hand-design convention: every hand rotates about a point
# exactly this many design units above its canvas bottom.
HAND_HUB_OFFSET_UNITS = 15

# --- Sun ----------------------------------------------------------------------
CIVIL_DEPRESSION = 6.0              # degrees below horizon for dawn/dusk
HORIZON_ELEVATION_DEG = -0.833      # solar disc touches the horizon (refraction)
CIVIL_TWILIGHT_ELEVATION_DEG = -6.0

# --- Year wheel ----------------------------------------------------------------
# Unwrapped dial angles of the six season anchors bracketing one calendar
# year in seasons_utc.json: previous December solstice, spring equinox,
# summer solstice (top of dial after mod 360), autumn equinox, December
# solstice, next spring equinox. Clockwise, 0 deg = summer solstice = top.
YEAR_ANCHOR_ANGLES = (180.0, 270.0, 360.0, 450.0, 540.0, 630.0)

# --- Hidden mode ----------------------------------------------------------------
# Typing this character sequence while the dial has focus unlocks the
# hidden extras (owner 2026-07-14) — for now the Four Greetings verses
# page in the Encyclopedia's Trinity topic. The owner sets the final
# sequence here; the unlock persists in settings.
HIDDEN_MODE_SECRET = "36m36u36v"

# --- Artwork sources -----------------------------------------------------------
# The Gemini and ChatGPT generations COEXIST (owner 2026-07-14). Since
# the RESTRUCTURE (2026-07-22) the source is NO LONGER a folder segment
# — it is a terminal filename SUFFIX (`<Figure>[_vN]_<src>.png`, source
# last: `_gem`/`_gpt`). The user picks the active source in Settings;
# `config.paths.art_file` resolves the suffix at every disk boundary,
# falling back to the other source and then the suffix-less name (owner
# hand-made art). There is no longer a per-root registry — every PNG is
# resolved uniformly by filename suffix.
ART_SOURCES = ("gemini", "chatgpt")
ART_SOURCE_DEFAULT = "gemini"
ART_SOURCE_TITLES = {"gemini": "Gemini", "chatgpt": "ChatGPT"}

# --- Moon ----------------------------------------------------------------------
SYNODIC_MONTH_DAYS = 29.53           # mean lunar cycle length

# A principal phase name (New/First Quarter/Full/Third Quarter) applies
# only around the instant itself (±half a day, the common convention) —
# afterwards the intermediate name takes over (e.g. Waning Crescent the
# day after the Third Quarter).
MOON_PRINCIPAL_WINDOW = 0.5 / SYNODIC_MONTH_DAYS

# Octant names by cycle fraction (windows of 1/8 centered on the anchors).
MOON_PHASE_NAMES = (
    "New Moon",
    "Waxing Crescent",
    "First Quarter",
    "Waxing Gibbous",
    "Full Moon",
    "Waning Gibbous",
    "Third Quarter",
    "Waning Crescent",
)

# Principal phase -> cycle fraction ("Last Quarter" is normalized to
# "Third Quarter" by the repository on load).
MOON_PHASE_FRACTIONS = {
    "New Moon": 0.0,
    "First Quarter": 0.25,
    "Full Moon": 0.5,
    "Third Quarter": 0.75,
}
MOON_CYCLE_QUARTER = 0.25           # fraction between consecutive principal phases

# The bundled databases' coverage is READ FROM THE DATA, never hardcoded
# (Rule #4): SeasonsRepository.coverage() / MoonPhaseRepository.coverage()
# return the min/max year keys, so a Deep Time pack widens coverage by
# swapping the JSON alone. Time Travel intersects the two and validates
# every target before the day build (app/time_travel.py, controller).

# --- Deep Time (Session 16, owner 2026-07-17) --------------------------------------
# The optional full-span data pack (Database/deep_time.sqlite, built by
# setup/make_deep_time.py, gitignored — ships only with the FULL
# installation). Detected at startup; the season/moon repositories CHAIN
# to it when the bundled coverage is exceeded. Its own coverage is read
# from its meta table, never hardcoded.
DEEP_TIME_DB_FILENAME = "deep_time.sqlite"

# Era notation (Settings, owner amendment 2026-07-17): governs ONLY the
# OFFICIAL year form's labels — "bce_ce" (default) or "bc_ad". Positive
# years render BARE ("2026", as the world writes it) unless the user
# opts into the suffix (Settings show_era_suffix); negative years ALWAYS
# carry their label ("44 BCE"). The ANNO LUCIS year is NOT a mode: it
# ALWAYS accompanies the official year in legends/hovers/the Time
# Travel header ("2026 · 6105. Anno Lucis") — see
# core.deep_time.format_year_line, the ONE pairing place.
ERA_NOTATIONS = ("bce_ce", "bc_ad")
ERA_NOTATION_TITLES = {"bce_ce": "BCE / CE", "bc_ad": "BC / AD"}

# The Earth marker's label mode (owner 2026-07-18, ROADMAP 15h — the FOUR
# exclusive Design ▸ Earth toggles, replacing the old show_earth_date/
# earth_weekday bool pair): "off" (no label), "date" ("8 Jul"), "weekday"
# ("FRI"), "date_weekday" (the date over the abbreviated weekday — the
# OLD combined "Full Date" meaning) and "full" (the date over the YEAR,
# the true Full Date, reusing the deep-travel year row's two-row shape).
EARTH_LABEL_MODES = ("off", "date", "weekday", "date_weekday", "full")

# Visibility Z modes (owner 2026-07-17, ROADMAP 15d; Settings z_mode):
# "bottom" — the clock stays BELOW every window except the desktop
# (WindowStaysOnBottomHint, the default); "top" — always ON TOP of
# everything (WindowStaysOnTopHint, a small clock the user always sees).
Z_MODES = ("bottom", "normal", "top")
Z_MODE_TITLES = {
    "bottom": "Below all windows (desktop layer)",
    "normal": "Normal window (above when focused)",
    "top": "Always on top",
}
# (current era, before era) labels per notation.
ERA_NAMES = {"bce_ce": ("CE", "BCE"), "bc_ad": ("AD", "BC")}
# ANNO LUCIS — the owner's measured world-era (SEALED 2026-07-16):
# A.L. 1 = 4079 BCE, the first year of the unbroken light era, so
# A.L. = CE + 4079 (2026 CE = A.L. 6105). Details in
# research/ephemeris/anno_lucis.json.
ANNO_LUCIS_OFFSET = 4079
ANNO_LUCIS_LABEL = "Anno Lucis"      # "6105. Anno Lucis" (owner's form)

# The Age of Light / Age of Darkness boundary (SEALED 2026-07-16, the
# doctrine research/ephemeris/anno_lucis.json measures): the current
# reigning age runs astronomical −4078…6423 inclusive (= 4079 BCE →
# 6423 CE, 10,501 unbroken years); every other covered year is the Age
# of Darkness. Owner fix-round B, 2026-07-19 (Earth hover card).
AGE_OF_LIGHT_START_YEAR = -4078
AGE_OF_LIGHT_END_YEAR = 6423

# The optional THIRD calendar on the year line (owner amendment
# 2026-07-17, Settings third_era; default none; "chinese" added owner
# fix-round B 2026-07-19 — "zašto nismo ubacili kineski"). Offsets live
# on the ASTRONOMICAL axis (1 BCE = 0), where every "CE + N" convention
# becomes a uniform +N: AUC 1 = 753 BCE = astro −752 (+753 → 1 ✓);
# Byzantine A.M. 1 = 5509 BCE (September epoch — tooltip note only);
# Hebrew A.M. counts from Tishri 3761 BCE (civil-axis convention
# CE + 3760 — tooltip note only). Anno Hegirae is LUNAR and has no
# fixed offset — displayed via the standard display-grade
# approximation AH ≈ (CE − 622) × 33/32 (core.deep_time). The Chinese
# (Huangdi) count uses the CE + 2697 convention (2026 CE → 4723) — the
# most common modern reading; sources spread 2695–2698 (the Encyclopedia's
# own "Eras of the World" article already flags the epoch drift). Kali
# Yuga (ERA-TRIO round, owner 2026-07-20) is a uniform CE + 3101 offset
# like the four above — epoch 3102 BCE = astro −3101 (the night of
# 17/18 February, Puranic tradition) — but its own Hindu luni-solar new
# year (Chaitra, in spring, not January) makes the reading ±1
# conventional near that boundary, the same class of honesty as the
# Chinese spread note above.
# THREE third eras are FORMATTERS rather than offsets, each a
# different shape: "maya" (MAYA round, owner 2026-07-20: "Jel Maje
# nisu imale kalendar?") is a TRUE DAY COUNT from a fixed epoch (no
# year concept at all) — `core.deep_time.maya_long_count` walks the
# real calendar date's Julian Day Number. "unix" (ERA-TRIO round) is
# likewise a day/second count, not a year — seconds since the Unix
# epoch (1970-01-01 00:00 UTC) at the displayed date's OWN midnight UTC
# — `core.deep_time.unix_epoch_seconds`. "olympiad" (ERA-TRIO round)
# needs only the YEAR, like the offset eras, but is not a uniform "CE +
# N": it is a 4-year CYCLE count from the first Olympiad (776 BCE,
# astro −775) — `core.deep_time.olympiad_year`. None of the three has a
# THIRD_ERA_OFFSETS entry and none is handled by `third_era_year` —
# `format_year_line` special-cases all three branches.
THIRD_ERAS = (
    "none", "auc", "byzantine", "hebrew", "hegirae", "chinese", "maya",
    "kali", "olympiad", "unix",
)
THIRD_ERA_TITLES = {
    "none": "None",
    "auc": "Ab Urbe Condita (Rome)",
    "byzantine": "Byzantine Anno Mundi",
    "hebrew": "Hebrew Anno Mundi",
    "hegirae": "Anno Hegirae (Islamic)",
    "chinese": "Huangdi (China)",
    "maya": "Maya Long Count",
    "kali": "Kali Yuga (Hindu)",
    "olympiad": "Olympiad (Ancient Greece)",
    "unix": "Unix Epoch (Computing)",
}
THIRD_ERA_OFFSETS = {
    "auc": 753, "byzantine": 5509, "hebrew": 3760, "chinese": 2697,
    "kali": 3101,
}
THIRD_ERA_LABELS = {
    "auc": "AUC",
    "byzantine": "Byzantine A.M.",
    "hebrew": "Hebrew A.M.",
    "hegirae": "AH",
    "chinese": "Huangdi",
    "maya": "Long Count",
    "kali": "Kali Yuga",
    # "olympiad"/"unix" embed their own label mid-string rather than
    # appending it (their display shape differs from every offset
    # era's "value. LABEL" — see `core.deep_time.olympiad_year`/
    # `format_year_line`'s unix branch) — kept here anyway (Rule #4)
    # so the words themselves stay data, not a second hardcoded copy.
    "olympiad": "Olympiad",
    "unix": "Unix",
}
# Epoch fine print for the Settings combo tooltips (owner amendment:
# tooltip only, never on the year line).
THIRD_ERA_NOTES = {
    "byzantine": "Year starts 1 September (5509 BCE epoch).",
    "hebrew": "Year starts at Tishri (autumn); civil convention CE + 3760.",
    "hegirae": "Lunar years — displayed via the AH ≈ (CE − 622) × 33/32 "
               "approximation; exact AH needs lunisolar math.",
    "chinese": "Continuous count from the Yellow Emperor's reign — "
               "sources spread 2695–2698 BCE; this dial uses CE + 2697.",
    "maya": "A true day count (baktun.katun.tun.uinal.kin), not a year "
            "offset — GMT correlation epoch 11 Aug 3114 BCE; 21 Dec 2012 "
            "was 13.0.0.0.0, a cycle rolling over, not an ending.",
    "kali": "The fourth and current age of Hindu cosmology — epoch "
            "3102 BCE; the Chaitra (spring) new year makes CE + 3101 a "
            "±1 approximation near the boundary.",
    "olympiad": "A 4-year cycle from the first Games, 776 BCE; the "
                "historical midsummer games-boundary is approximated "
                "by the calendar year.",
    "unix": "Seconds since 1970-01-01 00:00 UTC, read at this date's "
            "own midnight UTC — a day-level count, not the exact "
            "instant.",
}
# The Maya Long Count's GMT correlation constant (Goodman-Martinez-
# Thompson, the most widely accepted): Julian Day Number 584,283 =
# Long Count 0.0.0.0.0 = 11 August 3114 BCE proleptic Gregorian (6
# September 3114 BCE Julian). `core.deep_time.maya_long_count` golden-
# tested against two independently known, mutually consistent anchors
# (tests/test_deep_time.py): 21 Dec 2012 = 13.0.0.0.0, 1 Jan 2000 =
# 12.19.6.15.2.
MAYA_EPOCH_JDN = 584283
# The Olympiad's own epoch (ERA-TRIO round, owner 2026-07-20): the
# first Olympiad's Games, summer 776 BCE = astronomical year −775
# (`core.deep_time.astro_from_display`: 1 − 776 = −775). Golden-tested
# against a second, independent anchor: the classical chronographers'
# own running count reached the 293rd Olympiad in 393 CE, the
# conventional date of the last ancient Games under Theodosius I —
# `core.deep_time.olympiad_year` reproduces that number exactly from
# this same epoch (tests/test_deep_time.py).
OLYMPIAD_EPOCH_YEAR = -775

# The 400-year proleptic-Gregorian cycle (146,097 days — exactly 20,871
# weeks): shifting a moment by whole cycles preserves leap structure,
# weekdays and all intervals, which is what lets datetime (years 1-9999)
# carry Deep Time moments. Proxy years land in [PROXY_WINDOW_FIRST,
# PROXY_WINDOW_FIRST + GREGORIAN_CYCLE_YEARS) — opened at 2000 for
# modern tzdata rules and the sun model's reference era.
GREGORIAN_CYCLE_YEARS = 400
PROXY_WINDOW_FIRST = 2000

# --- Geography -------------------------------------------------------------------
LATITUDE_RANGE = (-90.0, 90.0)
LONGITUDE_RANGE = (-180.0, 180.0)

# City-name folding for search: NFKD decomposition strips most diacritics
# (š, č, ž, ü, ...) but NOT these single-codepoint letters — the bundled
# city names are ASCII transliterations, so native spellings must fold to
# match ("Tromsø" -> "tromso", "Đakovica" -> "dakovica").
CITY_NAME_TRANSLITERATIONS = {
    "ø": "o",
    "đ": "d",
    "ł": "l",
    "æ": "ae",
    "œ": "oe",
    "ß": "ss",
    "þ": "th",
    "ð": "d",
}

# Weekday index (datetime.weekday(): Monday=0) -> celestial body.
# Sunday's body (Sun) sits in the dial center on the hexa pointer; the
# other bodies occupy the star's arm slots.
WEEKDAY_BODIES = (
    "moon",      # Monday
    "mars",      # Tuesday
    "mercury",   # Wednesday
    "jupiter",   # Thursday
    "venus",     # Friday
    "saturn",    # Saturday
    "sun",       # Sunday
)

# Label written in white ON each body: the weekday SHORT name, never the
# planet-name abbreviation (owner spec). Larger dials show the full name.
WEEKDAY_LABELS = {
    "moon": "MON",
    "mars": "TUE",
    "mercury": "WED",
    "jupiter": "THU",
    "venus": "FRI",
    "saturn": "SAT",
    "sun": "SUN",
}
WEEKDAY_FULL_NAMES = {
    "moon": "Monday",
    "mars": "Tuesday",
    "mercury": "Wednesday",
    "jupiter": "Thursday",
    "venus": "Friday",
    "saturn": "Saturday",
    "sun": "Sunday",
}

# Pointer variants: how many arms the star has — and with how many hues
# the day's periods are measured (owner spec: trio 3x120, cross 4x90,
# hexa 6x60, octa 8x45).
# "aurora" (owner spec 2026-07-12) draws NO geometric pointer at all —
# its 7 entries are the PALETTE size: a dawn hue, five day hues spread
# EVENLY across the actual sunrise-sunset arc, and a dusk hue.
# "calendar" (owner 2026-07-16, CANON §The Dozen) divides the 24h dial
# into TWELVE 2-hour wedges and, like Aurora, draws NO star arms — its
# 12 entries are the PALETTE size (one hue per wedge). Its two wheels
# ride the wheel slot: primary = the Zodiac Dozen, secondary = the
# Almanac (Month) Dozen. It has NO arm HALF-ANGLE (armless, like
# Aurora): the star geometry and the arm hovers skip it explicitly.
# "rose" (owner spec 2026-07-27, CUBE.md §The Rose) is the SEVENTH
# pointer: THREE octa stars 15° apart — 8 hues, one star's worth, worn
# by all three (`ROSE_STAR_OFFSETS` places them, `ROSE_STAR_SETS` says
# which figure set each carries). Its palette size is 8 like the octa's
# — the three stars are the same star drawn three times, never 24
# independent hues (Rule #19: one rule, not 24 entries).
POINTER_POINTS = {
    "hexa": 6, "cross": 4, "octa": 8, "trio": 3, "aurora": 7,
    "calendar": 12, "rose": 8,
}

# What the READER counts on the dial — which is NOT always the palette
# size above (owner correction 2026-07-28: "on pokazuje 24, kalendar
# pokazuje 12"). The Rose draws its one eight-arm star THREE times at
# 15° pitch, so twenty-four rays stand on the glass while eight hues
# dress them; `POINTER_POINTS` stays the hue count that
# `settings_store._load_palettes` validates against, and this table is
# what the Design window prints and sorts by. Every pointer names its
# own number — the Calendar's twelve wedges and Aurora's seven bands are
# as countable as any star's arms.
POINTER_DIAL_COUNTS = {
    "trio": 3, "cross": 4, "hexa": 6, "aurora": 7, "octa": 8,
    "calendar": 12, "rose": 24,
}
CALENDAR_WEDGES = 12
CALENDAR_WEDGE_DEG = 360.0 / CALENDAR_WEDGES        # 30° per 2-hour wedge
# THE LIT WEDGE IS GONE (owner decree 2026-07-29, Pointers REWORK phase
# 2): "Osvetljavanje part koji prolazi sat ili zemlja iskljuciti —
# obrisati tu funkcionalnost". The Calendar no longer lights the wedge
# under the hour hand or under today's month/sign; it follows the SAME
# visibility law as every other pointer (the day/night law plus its own
# DAYLIGHT_SWITCH_POINTERS entry). `CALENDAR_LIGHTING_MODES`,
# `Settings.calendar_lighting`, `render.layers.calendar_lit_index` and
# `defaults.CALENDAR_WEDGE_LIT_DELTA` died with it — an old settings
# file that still carries the stale `calendar_lighting` key simply
# loads without it (the loader reads keys it knows, never rejects
# extras — pinned by tests/test_calendar.py).
#
# THE CALENDAR MOUNT (owner DESIGN ZODIAC law, R9a round 2026-07-21;
# GENERALIZED 2026-07-29): the set of figures that rides the Calendar's
# twelve wedges is no longer a hand-kept quartet. The ONE registry both
# the picker and the renderer read is `defaults.CALENDAR_MOUNTS` — it
# lives in `defaults` because it is the only module that sees BOTH the
# canon rosters declared here and `defaults.SLAVIC_MONTHS`; the legal
# setting values are `defaults.CALENDAR_MOUNT_MODES`, derived from it.
#
# The Gregorian months, January first — the ONE list every month-keyed
# mount rotates into Almanac seat order (Rule #19: the June-first order
# is computed by `defaults.almanac_seat_order`, never written twice).
GREGORIAN_MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)

# Display names chosen by the owner (FINAL.txt #8): the internal keys
# stay hexa/cross/octa/trio (settings and code stability); the menu and
# the docs speak these.
POINTER_DISPLAY_NAMES = {
    "trio": "Trinity",
    # QUATERNITY (owner seal 2026-07-28). "Seasons" stepped down to be
    # one of this pointer's three wheels, so the pointer needed a name
    # that can hold all three — the Elements, the Temperaments and the
    # Seasons are one fourfold read three ways, and only a word for
    # four-in-one holds them without favouring any. It answers Trinity
    # across the dial: three arms there, four here.
    "cross": "Quaternity",
    "hexa": "Prism",
    "octa": "Compass",
    "aurora": "Aurora",     # no arms — the day itself painted in bands
    "calendar": "Calendar",  # no arms — the year/day in twelve wedges
    "rose": "Rose",         # three octa stars, 15° apart (CUBE.md)
}

# The wheel LABELS per pointer (owner 2026-07-17, ROADMAP 11; naming
# refinements 2026-07-17/19; the CUBE third wheels sealed 2026-07-26,
# CUBE.md §Double Trinity/§Character Wheel) — RAW English, the ONE table
# both the Design window's palette-style row (`app.design_window`,
# `tr()`-wrapped at build time) and the watch TITLE row
# (`app.controller.watch_title`, untranslated — a name, not chrome)
# read (Rule #5: one source, two readers). Index 0 = "primary", index 1
# = "secondary", index 2 (where present) = "tertiary" — the slot keys
# are POSITIONAL (owner decree 2026-07-28); the MEANING of a wheel lives
# only in the name below (`palette_styles_for` tells which pointers
# carry a third).

# THE PRISM-LIGHT THEME NAME (owner seal 2026-07-27, closing the last
# open naming decision of `research/bond_theme.md`): the theme KEEPS ALL
# THREE candidate names. Wherever the theme is titled it shows the
# triple — `ONE_SOUL_THEME_TITLE`, the Encyclopedia heading — and
# wherever ONE name has to stand alone (the Design window's wheel row,
# the menus, the watch title, any label) it is `ONE_SOUL_THEME_NAME`,
# "One Soul". One declaration, both readers (Rule #5); the Aristotle
# anchor behind the pick — "one soul dwelling in two bodies" (Diogenes
# Laertius V.20) — lives in the theme's own article.
ONE_SOUL_THEME_NAME = "One Soul"
ONE_SOUL_THEME_TITLE = "One Soul — The Vow — The Bond"

POINTER_PALETTE_LABELS = {
    "trio": ("Court", "Family", "Genesis"),
    # THE QUATERNITY'S THREE (owner seal 2026-07-28): the same four arms
    # read as the body's humours, as the world's matter, and as the
    # year's quarters. Seasons comes LAST because it is the plainest
    # reading — and because the two older wheels keep the slots they
    # have always had.
    "cross": ("Temperaments", "Elements", "Seasons"),
    # WALKS, not "Walks of Life" (owner 2026-07-28): the tail was added
    # in 2026-07-19 only to kill the hereditary-caste reading, and the
    # walking metaphor does that work by itself — a walk is taken, an
    # estate is inherited. Beside Ages and Character the short form
    # cannot be misread, and the watch title stops saying "Walks of Life
    # Compass". CANON's own sealed table already read "Compass | Walks |
    # Ages".
    "octa": ("Walks", "Ages", "Character"),
    # The hexa SECONDARY slot speaks the theme's sealed single name
    # (owner 2026-07-27); its PRIMARY slot says PERSONS since the same
    # day (owner "ok."), because that wheel IS the Persons — CANON.md
    # names it so. The generic TRIPLE under "default" serves any pointer
    # with no named wheels of its own; it counts three because the slot
    # has three positions (owner 2026-07-28 — the old pair was two
    # labels for a three-state slot).
    "hexa": ("Persons", ONE_SOUL_THEME_NAME, "Council"),
    "aurora": ("Warm", "Cool"),
    "calendar": ("Zodiac", "Almanac"),
    # THE ROSE'S TWO WHEELS (owner seal 2026-07-27, CUBE.md §The Rose).
    # Both seat the SAME three sets on the same two anchors — Modern on
    # the 0° star, Historical on the −15° star — and the wheel is named
    # for where the MYTH star goes: LEGACY puts it at −30° (the deepest
    # past, everything behind the hour), PROPHECY at +15° (ahead of the
    # hour, symmetric). The hues are identical on both (the wheel turns
    # geometry and figures, not colors — the Seasons pointer already
    # serves one palette under both styles).
    "rose": ("Legacy", "Prophecy"),
    "default": ("Primary palette", "Secondary palette", "Tertiary palette"),
}

# What each palette circle COLORS (owner spec 2026-07-11: hovering a
# palette swatch in Settings names its arm position). Order matches
# PALETTE_PRESETS — clockwise from the top arm; the Compass speaks in
# cardinal directions, the others in dial positions.
POINTER_ARM_LABELS = {
    "trio": ("Top", "Right", "Left"),
    # The Genesis wheel's inverted arms (trio + "tertiary" style — the
    # settings palette editor reads this via `defaults.
    # pointer_arm_labels`): 24h bottom, 08h upper-left, 16h upper-right.
    "trio_tertiary": ("Bottom", "Left", "Right"),
    "cross": ("Top", "Right", "Bottom", "Left"),
    "hexa": (
        "Top", "Top Right", "Bottom Right",
        "Bottom", "Bottom Left", "Top Left",
    ),
    "octa": (
        "North", "North-East", "East", "South-East",
        "South", "South-West", "West", "North-West",
    ),
    # Aurora speaks in day phases: the dawn band, five day hues from
    # sunrise to sunset, the dusk band.
    "aurora": (
        "Dawn", "Morning", "Forenoon", "Noon", "Afternoon", "Evening",
        "Dusk",
    ),
    # The ROSE speaks the YEAR (CUBE.md §The Rose — the Sunday axis):
    # its four cardinals are the sun's turning points and its four
    # diagonals the season centres, landing exactly where
    # `core.year_wheel` puts them. Clockwise from 12h.
    "rose": (
        "Summer Solstice", "Summer", "Autumn Equinox", "Autumn",
        "Winter Solstice", "Winter", "Spring Equinox", "Spring",
    ),
    # Calendar wedges, clockwise from the TOP wedge. The two wheels
    # differ (Zodiac = signs from the top boundary, Almanac = months
    # from the top center), so the palette-editor labels stay NEUTRAL — the
    # ordinal position of each wedge (owner spec: the swatch names its
    # place, the wheel gives the meaning).
    "calendar": tuple(f"Wedge {index + 1}" for index in range(12)),
}

# Star arm (diamond) half-angles. Hexa/octa are the regular N-star
# values (180/N, adjacent arms touch at the inner vertices); the CROSS
# uses the OCTA arm shape — "octa without the 4 diagonal arms" (owner
# spec, design/background/cross.png) — slim diamonds with gaps between
# them, never the fat rhombi a regular 4-star would give. The TRIO is
# likewise "half of hexa" (owner spec, FINAL.txt #7): three hexa-shaped
# arms at 12h/4h/20h — where the ring letters M, D, Y point — with
# gaps; its three hues center on the arms (thirds 8-16 / 16-24 / 0-8).
POINTER_ARM_HALF_ANGLE_DEG = {
    "hexa": 30.0, "cross": 22.5, "octa": 22.5, "trio": 30.0,
    # The ROSE is three OCTA stars — the same arm shape, so its rays sit
    # 15° apart while each is 45° wide and neighbors OVERLAP, exactly as
    # the owner draws them (CUBE.md §The Rose).
    "rose": 22.5,
}

# THE POINTER SHAPE (Pointers REWORK phase 1, owner sheet
# UV/Pointers.png, 2026-07-29) — ONE global choice for the drawn wheel:
#   "star"    — the standing diamond stars (the shape shipped so far).
#   "polygon" — the PLAIN polygon of the pointer's own arm count: the
#               Quaternity a SQUARE, the Prism a HEXAGON, the Compass an
#               OCTAGON, with one VERTEX per arm tip and each arm's hue
#               filling its kite from the center out to that vertex
#               (boundaries run center -> edge midpoint). The TRINITY is
#               the owner's one exception: instead of a triangle it draws
#               the CUBE — the hexagon of three rhombi the Cube look
#               already builds (`CUBE_LOOK_WHEELS`), rhombus tips on the
#               trio's three arms.
# The armless AURORA draws no pointer at all and ignores the choice. The
# CALENDAR and the ROSE read it as "one touching star instead of two /
# three overlapping ones" — see CALENDAR_STAR_ARMS below and
# POINTER_DIAL_COUNTS above for the ray counts.
POINTER_SHAPES = ("star", "polygon")
POINTER_SHAPE_DEFAULT = "star"

# The pointers whose "polygon" really IS a polygon (3/4/6/8 arms) — the
# only ones the CURVATURE slider touches. The Calendar's twelve-point
# and the Rose's twenty-four-point polygons are STARS whose adjacent
# arms merely touch, and a star never curves (owner spec).
POLYGON_POINTERS = ("trio", "cross", "hexa", "octa")

# THE EDGE PULL (owner sheet: "Original straight edge / Smooth concave
# edge / V-notched edge"): 0.0 leaves the plain polygon; toward 1.0 each
# OUTER edge's midpoint is pulled inward along its own radius, until at
# 1.0 it sits exactly where the pointer's OWN star seats its inner
# vertices — so the silhouette lands on the star's concave profile. The
# color-boundary edges INSIDE the figure never curve.
POLYGON_CURVATURE_RANGE = (0.0, 1.0)
POLYGON_CURVATURE_DEFAULT = 0.0
# How a pulled edge is drawn: "smooth" — one quadratic arc THROUGH the
# pulled midpoint; "notched" — two straight segments meeting there (the
# V-notch).
POLYGON_EDGE_MODES = ("smooth", "notched")
POLYGON_EDGE_DEFAULT = "smooth"

# THE CALENDAR'S TWO SHAPES (owner sheet 2026-07-29): "star" draws TWO
# HEXAGRAMS 30° apart — six of the twelve wedge hues on each, the one
# standing on the EVEN wedge centers painted on top (the Rose's z-stack
# pattern); "polygon" draws ONE twelve-point star (POINTER_DIAL_COUNTS)
# whose adjacent arms touch, one hue per 2h wedge, tips on the wedge
# centers. Both ride the active wheel's own wedge geometry
# (`render.layers.calendar_wedge_bounds`) and, like the wedges
# themselves, are calendar-FIXED — they never take the solar rotation.
CALENDAR_STAR_ARMS = 6

# THE ROSE'S THREE STARS (owner seal 2026-07-27, CUBE.md §The Rose) —
# star angles in DRAW ORDER, first painted (bottom of the z-stack) to
# last painted (topmost). The 0° star is ALWAYS last on both wheels, so
# the dominant fully-visible arm points at true 12h and the dial keeps
# its own axis: solstices vertical, equinoxes horizontal.
#   LEGACY  (primary): −30° · −15° · 0° — everything behind the hour; the
#           deepest past lies lowest.
#   PROPHECY (secondary): −15° · +15° · 0° — the PAST lies deepest, the
#           FUTURE rides over it (owner: the middle z-layer is the
#           future star), the present covers both.
ROSE_STAR_OFFSETS = {
    "primary": (-30.0, -15.0, 0.0),
    "secondary": (-15.0, 15.0, 0.0),
}

# THE AURA WEDGE ANCHOR (owner's correction round 2026-07-29, his exact
# numbers) — where a hue's BACKGROUND wedge stands relative to that
# hue's LEAD RAY (the direction it wears on the topmost, 0° star), in
# FRACTIONS of the hue's own share of the circle (360/hues). The star
# tips themselves NEVER move: both Rose wheels keep every ray on a full
# hour (`ROSE_STAR_OFFSETS`) — the per-wheel law lives here, in the
# background alone.
#
#   DEFAULT (every one-star pointer): the wedge is CENTERED on the arm,
#           the standing behavior — one ray, one wedge.
#   LEGACY  (Rose primary): the wedge TRAILS its lead ray — boundaries
#           ON the lead-ray hours, because the past lies behind the hour.
#           Owner's numbers: tips 10h/11h/12h, background 9h -> 12h.
#   PROPHECY (Rose secondary): the wedge is CENTERED on the lead ray —
#           past and future symmetric. Owner's numbers: tips 11h/12h/13h,
#           background 10:30 -> 13:30.
#
# `render.layers.aura_wedge_anchor` is the ONE reader (Rule #5).
AURA_WEDGE_ANCHOR_DEFAULT = (-0.5, 0.5)
ROSE_AURA_WEDGE_ANCHOR = {
    "primary": (-1.0, 0.0),
    "secondary": (-0.5, 0.5),
}

# Which figure SET each Rose star carries, keyed by its offset (CUBE.md
# §The Rose — the two wheels share both anchors and move only the myth):
# Modern rides the true hours, Historical one ray back, the Myth set on
# whichever ray its wheel sends it to.
# The three words are `cube.FIGURE_SETS` itself (Session 24): the star,
# the roster and the disk register now speak ONE vocabulary — the myth
# star carries the ARCHETYPAL set, which is what it always held.
ROSE_STAR_SETS = {
    0.0: "modern",
    -15.0: "historical",
    -30.0: "archetypal",    # Legacy — the myth we inherited
    15.0: "archetypal",     # Prophecy — the myth that comes
}

# The Rose's arm CHARACTER system per wheel (CUBE.md §The Rose): Legacy
# reads the 2D Character wheel (four poles and their four blends),
# Prophecy the 3D Cube (its eight vertices, all three axes at once).
ROSE_ARM_SYSTEMS = {"primary": "character_2d", "secondary": "vertices_3d"}

# THE DAYLIGHT SWITCH (owner 2026-07-27): these two pointers let the
# reader turn the day/night law OFF and stand in flat full color — the
# Calendar's twelve wedges and the Rose's three stars are read as a
# WHEEL first and a clock second. Every other pointer always runs
# day/night (`render.layers.lit_regions`); `Settings.daylight` is
# ignored on them so the stored choice survives a pointer switch.
DAYLIGHT_SWITCH_POINTERS = ("calendar", "rose")

# The trio's theological themes per arm angle (SYMBOLISM.md trio canon:
# Faith vertical toward God, Hope on the dawn side, Love with Venus).
# Like every pointer, the arm tip is the CENTER of its hue (owner
# correction 2026-07-10): Faith yellow spans 8h-16h, Love red 16h-24h,
# Hope blue 0h-8h.
TRIO_ARM_THEMES = {0.0: "Faith", 120.0: "Love", 240.0: "Hope"}

# The GENESIS wheel's offices per arm angle (CUBE.md §Double Trinity,
# SEALED 2026-07-26): the same three persons who judge on the Court
# create on the inverted triangle — God the Creator at 24h, Jesus the
# Preserver at 08h, the Devil the Destroyer at 16h. The arm hover
# speaks (person, office); the articles are Session 21's.
GENESIS_ARM_OFFICES = {
    180.0: ("God", "Creator"),
    300.0: ("Jesus", "Preserver"),
    60.0: ("the Devil", "Destroyer"),
}

# The UMBRA (gray brightness wheel) ships in three user-selectable
# forms (owner spec). Sectioned forms follow one structure: the LIGHTEST
# and DARKEST sections are single, CENTERED on the star's top tip (true
# solar noon) and bottom (true midnight); every other shade appears
# twice, mirrored left/right — so shades = sections/2 + 1:
#   fine   — 30 sections of 12 deg, 16 shades (measured from the
#            owner's art, design/background/gray.png);
#   coarse — 24 sections of 15 deg, 13 shades;
#   gradient — no sections at all: a continuous per-pixel sweep,
#            lightest at the top, darkest at the bottom, mirrored.
UMBRA_FORMS = ("fine", "coarse", "gradient")
UMBRA_SECTION_COUNTS = {"fine": 30, "coarse": 24}

# Each form comes in four contrasts (owner spec): "full" spans the
# whole gray range, "half" the middle half of the scale, "light" the
# bright half (128-255), "dark" the dark half (0-127).
UMBRA_CONTRAST_VARIANTS = ("full", "half", "light", "dark")

# The WHEEL SLOTS a pointer's palette row can hold. The keys are
# POSITIONAL and carry NO meaning of their own (owner decree
# 2026-07-28, closing the "paint"/"light" era: those two words named a
# subtractive-vs-additive distinction that stopped being true the moment
# the slots started carrying the Zodiac, the Persons, the Walks of Life
# and the Rose's Legacy). A wheel's MEANING lives in exactly one place —
# `POINTER_PALETTE_LABELS` above. The third slot exists ONLY on the
# pointers `palette_styles_for` names; everywhere else a stored
# "tertiary" normalizes back to "primary"
# (`palette.effective_palette_style`).
PALETTE_STYLES = ("primary", "secondary", "tertiary")
# The pointers whose wheel row carries a THIRD wheel: trio — Genesis
# (the creation trio, drawn INVERTED); cross — Seasons (owner seal
# 2026-07-28, the wheel the pointer used to be named after); hexa —
# Council (all six Double-Trinity offices); octa — Character (the Cube
# at depth zero), CUBE.md. The law is the arm count: the pointers that
# draw 3, 4, 6 or 8 arms carry three wheels; the armless ones and the
# Rose (7, 12, 24) carry two — eighteen wheels in all.
THIRD_WHEEL_POINTERS = ("trio", "cross", "hexa", "octa")


def palette_styles_for(pointer: str) -> tuple[str, ...]:
    """The wheel slots THIS pointer actually serves — ("primary",
    "secondary") everywhere, plus "tertiary" on the three-wheel
    pointers. The ONE gate the Design window's wheel row, the settings
    normalization and the tests all read (Rule #5)."""
    if pointer in THIRD_WHEEL_POINTERS:
        return PALETTE_STYLES
    return PALETTE_STYLES[:2]


# THE GENESIS INVERSION (owner: "trougao ka dole", CUBE.md §Double
# Trinity): the trio's TERTIARY wheel draws its three arms on the OPPOSITE
# seats — 24h/16h/08h instead of 12h/20h/04h — one arm-angle offset fed
# through render.layers.arm_offset_deg into the star diamonds, the Aura
# wedges, the weekday slots, the lit-index math and the arm hit-test.
GENESIS_ARM_OFFSET_DEG = 180.0

# THE SEASONS ROTATION (Pointers REWORK phase 1, owner spec 2026-07-29):
# the cross's TERTIARY wheel — the Seasons — turns its four arms by half
# a wedge, so the color BOUNDARIES land exactly on 12h/3h/6h/9h and the
# wheel reads ASTRONOMICAL seasons (a season begins at its turning
# point) instead of the meteorological quarters the primary
# (Temperaments) and secondary (Elements) wheels keep.
SEASONS_ARM_OFFSET_DEG = 45.0

# Every WHEEL that seats its arms off the pointer's own default angles,
# keyed (pointer, wheel slot) — the ONE table `render.layers.
# arm_offset_deg` reads, so a new offset wheel is a line here rather
# than a branch in the renderer (Rule #5).
WHEEL_ARM_OFFSET_DEG = {
    ("trio", "tertiary"): GENESIS_ARM_OFFSET_DEG,
    ("cross", "tertiary"): SEASONS_ARM_OFFSET_DEG,
}

# THE CUBE LOOK (owner seal 2026-07-26, CUBE.md §Display laws): the
# Double-Trinity FAMILY wheels — the Court (trio primary), Genesis (trio
# tertiary) and the Council (hexa tertiary) — render in TWO looks: "Diamond"
# (the slim arm diamonds, the current form) and "Cube" (the owner's
# corner-view: the arm diamonds widen to 180/N half-angles, so the
# three/six rhombi tile the hexagon exactly — three visible cube faces
# on the trio wheels, the two interlocked corners on the Council).
# `Settings.cube_look` toggles it; render.layers.cube_look_active gates.
CUBE_LOOK_WHEELS = (
    ("trio", "primary"), ("trio", "tertiary"), ("hexa", "tertiary"),
)

# The SOUTH SLOT (menu name; the internal octa_* keys stay for settings
# and code stability, like the pointer keys): user-selected info near
# the dial bottom. On the Compass it IS the reserved bottom arm; the
# Trinity always has room at the south gap between its blue and red
# diamonds; Aurora always shows it (images only); Prism and Seasons
# gain it once the Weekday element is off (owner matrix 2026-07-12).
# The four image modes draw the owner's PNG art
# (assets/calendars/<dir>) and fall back to the text form until the art
# exists (documented fallback).
# COMPOSITE model (owner 2026-07-12): a top-level MODE plus a per-
# family STYLE dropdown — Astrology picks sign/logo/constellation/text
# ("colored" joins when the owner's art lands), the Chinese zodiac
# picks text/colored/gold/silver/bronze (the metals run the selective
# swap on the bronze logo, colored uses the fresh full-color badges).
# "ascendant" (owner request 2026-07-12): the RISING sign right now —
# the natal podznak, cycling through all twelve signs daily; it wears
# the zodiac styles through its own ascendant_style dropdown.
# "weekday" in the INFO slot (owner 2026-07-12): a SECOND weekday body
# — its own theme via info_slot_theme — so the pinned pair can read
# e.g. Norse left, Greek right, both showing today.
# "seconds" (owner 2026-07-14): a SMALL-SECONDS complication — the
# active hand set's seconds hand rotating inside the subdial (the big
# Elements seconds hand yields while a slot shows it).
OCTA_SLOT_MODES = (
    "time", "date", "day_length", "seconds", "weekday", "zodiac",
    "ascendant", "chinese",
)
# The DAY SLOT can carry an astrology badge instead of the bodies
# (owner 2026-07-12) — in the PINNED layouts (Aurora, or the Pointer
# element off): it stands at the usual bottom spot, so the pair can
# read official sign left, ascendant right. Elsewhere the bodies rule.
WEEKDAY_SLOT_MODES = (
    "weekday", "time", "date", "day_length", "seconds", "zodiac",
    "ascendant", "chinese",
)
# Display titles for the four COMPLICATION modes (owner spec) — the ONE
# table both the (retired) menu's Complications dropdown and the new
# Slot Theme window's own tab read (Rule #5). "weekday"/"zodiac"/
# "ascendant"/"chinese" are not complications — they get their own
# picker (the Weekday grid / the zodiac-style / Chinese-style groups).
SLOT_COMPLICATION_TITLES = {
    "time": "Digital Time",
    "date": "Date",
    "day_length": "Day length",
    "seconds": "Seconds",
}
# SLOT SEATS (owner matrix 2026-07-14): the fixed dial angles the
# multi-slot layouts use — the top (12h), the 20h/4h arm pair (the
# Trinity/Prism red and blue arms) and the 21h/3h between-arms pair;
# 24h (SOUTH_SLOT_ANGLE) hosts a lone pinned slot. Seats ride the
# star's rotation.
SLOT_SEAT_TOP_ANGLE = 0.0
SLOT_SEAT_RIGHT_ARM_ANGLE = 120.0      # the 20h arm (red on paint)
SLOT_SEAT_LEFT_ARM_ANGLE = 240.0       # the 4h arm (blue on paint)
ZODIAC_SLOT_STYLES = ("sign", "logo", "constellation", "text", "colored")
CHINESE_SLOT_STYLES = ("text", "colored", "gold", "silver", "bronze")
# Each SLOT carries its OWN style (owner 2026-07-12: the shared
# per-family fields collapsed both slots onto one look) — one value
# from either family's set, interpreted per the active family.
SLOT_STYLE_VALUES = tuple(dict.fromkeys(
    ZODIAC_SLOT_STYLES + CHINESE_SLOT_STYLES
))
# style -> art folder under assets/calendars/ (text styles draw no art).
# Family/variant tree (owner restructure 2026-07-14): astrology's
# plain logo is its PRIMARY variant.
ZODIAC_STYLE_ART_DIRS = {
    "sign": "zodiac/astrology/primary/sign",
    "logo": "zodiac/astrology/primary/logo",
    "constellation": "zodiac/astrology/primary/constellation",
    "colored": "zodiac/astrology/primary/colored",
}
CHINESE_STYLE_ART_DIRS = {
    "colored": "zodiac/chinese/primary/colored",
    "gold": "zodiac/chinese/primary/bronze",
    "silver": "zodiac/chinese/primary/bronze",
    "bronze": "zodiac/chinese/primary/bronze",
}

# Earth marker style: the owner ships every continent in a clean and an
# atmosphere version.
EARTH_STYLES = ("clean", "atmo")

# Ring letters and layouts (owner spec 2026-07-10, data-driven): ring
# presets live in Database/ring_presets.json (+ the user's custom ones
# in settings) as {name, positions, letters}; the POSITIONS signature
# picks a LAYOUT — the ring face with matching gaps and the metal
# rules. Finish rules (owner correction): the trio of ONE metal always
# forms a TRIANGLE — the GOLD finish puts the layout's triangle in gold
# and the rest in silver, the SILVER finish is the exact inverse; on
# the hexagram BOTH metals form triangles (12/20/4 vs 24/8/16). Silver
# and bronze letters are derived from the gold master AT LOAD (owner
# 2026-07-19, render.asset_recolor.letter_metal_file).
RING_FINISHES = ("gold", "silver", "bronze", "thematic")
# THE THEMATIC FINISH (ENLARGE/THEMATIC round, owner 2026-07-27,
# "četvrta opcija za ring THEMATIC ... bojiti PREKO NOVOG PROGRAMA"):
# the 4th ring letter finish — instead of a metal, the letters wear the
# ACTIVE PRESET's own theme color, drawn by the SAME recolor
# transformer (a colored RAMP beside the metal ramps in
# recolor/presets/metals.json — "adding a metal costs one entry and
# zero code"). Per-preset shade (the ramp names double as shade names,
# METAL_SHADE_NAMES["thematic"]); a custom/unknown ring falls back to
# the moon indigo (the app's own signature hue). Outside the ring band
# (subdial borders, hands, follow-the-ring theme metals) the thematic
# finish reads as GOLD — the color belongs to the letters and the
# words, not to every metal surface (documented containment).
RING_THEMATIC_SHADES = {
    "DOMY": "cross_red",        # the suffering cross
    "PILOT": "cross_blue",      # the salvation cross
    "Dollar": "dollar_green",   # the banknote's ink
    "The One": "moon_indigo",   # the winter-solstice violet
    "Templar": "templar_black", # the Beauceant
}

# THE METAL SHADES (R8a round, owner spec 2026-07-21 night — the retry
# after the adaptive-percentile attempt was reverted for flattening
# every relief into a wash, see config.defaults's NOTE above
# METAL_SHADES): each metal offers several SELECTABLE shades, picked in
# Settings (app.settings_dialog.themes_section._build_metal_shade_group)
# and stored one per metal (`Settings.metal_shade_gold/_bronze/_silver`).
# Names here are the validation/enumeration source; the numeric (hue, saturation,
# reference value) recipe per shade lives in `config.defaults.
# METAL_SHADES` — kept in `defaults` because it depends on nothing else,
# same split as SUBDIAL_SETS (names, here) vs SUBDIAL_RECOLOR_COLORS
# (recipe, defaults).
METAL_SHADE_NAMES = {
    "gold": ("dark_amber", "amber", "classic", "pale", "champagne"),
    "bronze": ("dark_bronze", "bronze", "light_bronze"),
    "silver": ("gunmetal", "silver", "platinum"),
    # The THEMATIC pseudo-metal (ENLARGE/THEMATIC round, owner
    # 2026-07-27; widened for CUSTOM rings same day): its "shades" are
    # ALL the transformer's ramps — the five ring theme colors
    # (`RING_THEMATIC_SHADES`) PLUS every metal ramp (owner: "iron,
    # copper... sve") — so a custom card's own `thematic` pick can name
    # any of them. Bundled presets resolve automatically from
    # `RING_THEMATIC_SHADES`; never offered in the Settings shade
    # pickers. This tuple mirrors `recolor/presets/metals.json` and is
    # guarded against drift by `tests/test_skins.py`
    # (test_thematic_choices_mirror_the_recolor_presets) — constants.py
    # stays a pure-literals file (its own docstring law), the test is
    # the sync.
    "thematic": (
        "cross_red", "cross_blue", "dollar_green",
        "moon_indigo", "templar_black",
        "gold", "gold_dark_amber", "gold_amber", "gold_pale",
        "gold_champagne",
        "silver", "bronze", "bronze_dark", "bronze_light",
        "copper", "brass", "rose_gold", "steel", "gunmetal",
        "platinum", "pewter", "iron",
    ),
}
METAL_SHADE_DEFAULT = {
    "gold": "classic", "bronze": "bronze", "silver": "silver",
    "thematic": "moon_indigo",
}
METAL_SHADE_TITLES = {
    "dark_amber": "Dark amber", "amber": "Amber", "classic": "Classic gold",
    "pale": "Pale gold", "champagne": "Champagne",
    "dark_bronze": "Dark bronze", "bronze": "Bronze", "light_bronze": "Light bronze",
    "gunmetal": "Gunmetal", "silver": "Silver", "platinum": "Platinum",
    "cross_red": "Cross red", "cross_blue": "Cross blue",
    "dollar_green": "Dollar green", "moon_indigo": "Moon indigo",
    "templar_black": "Templar black",
    # The remaining transformer ramps, pickable by a CUSTOM ring's own
    # thematic choice (ENLARGE/THEMATIC round, widened same day):
    "gold": "Gold", "gold_dark_amber": "Gold dark amber",
    "gold_amber": "Gold amber", "gold_pale": "Gold pale",
    "gold_champagne": "Gold champagne",
    "bronze_dark": "Dark bronze (ramp)", "bronze_light": "Light bronze (ramp)",
    "copper": "Copper", "brass": "Brass", "rose_gold": "Rose gold",
    "steel": "Steel", "pewter": "Pewter", "iron": "Iron",
}

# The subdial PLATE styles (owner 2026-07-15, his A/B spec): "theme" —
# the tapisserie field wears the clock tint (the AP design in the
# theme color) and the tick circle joins the finish metal; "black" —
# the standard dark AP field as drawn, white ticks. Both: rim, mini
# hand and complication texts in the letter-finish metal, shadowed.
SUBDIAL_STYLES = ("theme", "black")

# The subdial PLATE SETS (owner decree 2026-07-21, Rsub round —
# retires the Rule #19 one-master-per-source model): the plate is its
# OWN shared thing now, not a Gemini/ChatGPT split — five hand-picked
# sets live under assets/subdial/ (see assets/___assets.md for why
# that root sits OUTSIDE ART_SOURCED_ROOTS). "set1".."set4" are each
# three hand-drawn finishes (no recolor); "solo" ships one hand-drawn
# silver file and the algorithm derives gold/bronze from it exactly
# like before.
SUBDIAL_SETS = ("set1", "set2", "set3", "set4", "solo")
SUBDIAL_SET_DEFAULT = "set1"
SUBDIAL_SET_TITLES = {
    "set1": "1", "set2": "2", "set3": "3", "set4": "4", "solo": "Solo",
}

# The two figure ROSTERS (owner doctrine 2026-07-15): "planetary" —
# the day-ruler counterparts (the shipped canon); "pantheon" — the
# culture's own hierarchy seated on our archetypes. Themes without a
# pantheon table fall back to planetary (documented).
FIGURE_ROSTERS = ("planetary", "pantheon")

RING_LAYOUTS = {
    # Owner naming (2026-07-10): the up-triangle is the masculine
    # Flame, the down-triangle the feminine Chalice, and their union —
    # the hexagram — the Seal.
    "flame": {
        "positions": (12, 20, 24, 4),
        "face": "domy.png",
        "triangle": (12, 20, 4),     # points UP
        "theme": "Masculine",
    },
    "chalice": {
        "positions": (12, 16, 24, 8),
        "face": "morph.png",
        "triangle": (8, 16, 24),     # points DOWN
        "theme": "Feminine",
    },
    "seal": {
        "positions": (12, 16, 20, 24, 4, 8),
        "face": "hexagram.png",
        "triangle": (),              # the Seal wears ONE metal on all six
        "theme": "Union",
    },
}
# THE METAL-SPLIT OPTION (TASK 3, MASON/ICONS round, owner verdicts
# 2026-07-19, third batch): for every seal preset that carries its own
# `triangle` override (Mason/Omega/Templar today — `data.rings.
# validate_preset`'s optional card field) the owner can choose EITHER
# the 3-3 two-metal split OR one finish on all six
# (`app.controller._ring_two_metals`, `Settings.ring_two_metals`). This
# is the per-preset DEFAULT when the user has never touched the toggle
# for that preset — Mason keeps its pre-Task-3 split look, every other
# eligible preset starts single-metal (documented owner spec: "default
# matching today's look"). A preset absent here (or one with no
# `triangle` at all) simply defaults to False — ineligible presets
# never read this table.
RING_TWO_METALS_DEFAULT = {"Dollar": True}
# THE EYE AT THE APEX (DOLLAR/EYE round, owner decree 2026-07-27): the
# Dollar preset's 12h seat wears the EYE OF PROVIDENCE instead of the
# letter G (CANON.md §The Banknote, CUBE.md §The Banknote Seal). "👁"
# is the ADAPTIVE glyph — its canonical Eye.png resolves to
# Eye_gem/Eye_gpt per the Settings art source (config.paths.art_file),
# and the per-preset "Shine" toggle (Settings.ring_eye_shine,
# app.controller._ring_eye_shine — same resolution shape as the
# two-metals toggle above) swaps the whole stem for the glory-of-rays
# master Eye_shine.png. The four EXPLICIT variants in the letter
# library below are the CUSTOM ring builder's own picks (owner: "any
# of the four") — source and rays baked into the chosen glyph,
# ignoring both switches.
RING_EYE_GLYPH = "👁"
RING_EYE_SHINE_FILE = "Eye_shine.png"
RING_EYE_SHINE_DEFAULT = {"Dollar": True}
# THE SHINE ENLARGE FACTOR (owner UV inbox 2026-07-27, "slika 2 kada
# ima SHINE mora da bude veca"; corrected same day — the first
# measurement trusted the alpha channel, but the glory of rays is
# ITSELF opaque, so it read the whole glow as "triangle" and landed on
# a uselessly small ~1.16): the factor is the ratio of the TRIANGLE's
# frame fraction between the no-light and shine masters, measured on
# the triangle's actual apex/base rows. The shine masters are also
# PADDED on disk so the triangle sits at the exact frame center
# (originally it rode high, which would have drawn the zoomed triangle
# off-seat). ChatGPT: plain 0.97 vs shine 0.46 of frame -> 2.11;
# Gemini: 0.98 vs 0.59 -> 1.67. `app.controller.build_skin` stamps the
# factor into `SkinDefinition.ring.letter_zoom` for the shine stems so
# the triangle draws the SAME size and only the rays extend beyond it.
RING_EYE_SHINE_ENLARGE = {"gem": 1.67, "gpt": 2.11}
# The full letter library (glyph -> art file) — presets and the custom
# ring builder choose from these, GOLD masters only; silver and bronze
# are derived from the gold master at load (owner 2026-07-19,
# render.asset_recolor.letter_metal_file — no more pre-rendered files). The
# library is GROUPED (owner spec 2026-07-11):
# the builder shows Latin / Greek / Numbers / Symbols sections. Numbers
# exist ONLY for the six ring positions they belong to (owner decision:
# a number makes no sense away from its own hour) — 24h wears Ω in the
# NUMBERS bundled preset.
_LATIN_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_RING_NUMBERS = ("4", "8", "12", "16", "20")
RING_LETTER_GROUPS = {
    "Latin": tuple(_LATIN_LETTERS),
    "Greek": ("Ω", "Π", "Φ", "Ψ", "Σ", "Θ"),
    "Numbers": _RING_NUMBERS,
    "Symbols": (
        "✠",
        "👁 ChatGPT", "👁 ChatGPT ☀", "👁 Gemini", "👁 Gemini ☀",
    ),
}
RING_LETTER_FILES = {
    # The WHOLE library is PNG at 512 px height (owner decision
    # 2026-07-12 — the traced SVGs parsed in seconds; 512 covers every
    # on-dial size with room to spare).
    **{letter: f"{letter}.png" for letter in _LATIN_LETTERS},
    "Ω": "Omega.png",
    "Π": "Pi.png",
    "Φ": "Phi.png",
    "Ψ": "Psi.png",
    "Σ": "Sigma.png",
    "Θ": "Theta.png",
    **{number: f"{number}.png" for number in _RING_NUMBERS},
    # Symbols (the owner is growing this set for custom rings):
    "✠": "templar.png",
    # The Eye of Providence (DOLLAR/EYE round, 2026-07-27): the
    # adaptive glyph (the Dollar's own — source and shine resolved by
    # the switches) plus the four explicit custom-builder variants.
    "👁": "Eye.png",
    "👁 ChatGPT": "Eye_gpt.png",
    "👁 ChatGPT ☀": "Eye_shine_gpt.png",
    "👁 Gemini": "Eye_gem.png",
    "👁 Gemini ☀": "Eye_shine_gem.png",
}

# Weekday body themes (SYMBOLISM.md canon): "planets" uses the skin's
# own weekday unit; the others swap in the owner's themed art from
# assets/skins/domy/weekday/<theme>/ with the canon display names.
WEEKDAY_THEMES = (
    "planets",
    "planet_signs",
    "greek",
    "norse",
    "egypt",
    "slavic",
    "alchemy",
    "japan",
    "religion",
    "religion_alt",
    "profession",
    # The ANIMAL SOCIETIES (owner 2026-07-13) — three orders of order:
    # the pack by RANK, the hive by FUNCTION AND AGE, the herd by
    # MEMORY.
    "wolf",
    "bee",
    "elephant",
    # The TEXT WAVE themes (owner 2026-07-14): the three Scripture
    # sets, the deep sky, and the Planets medallion look.
    "bible",
    "bible2",
    "bible_dark",
    "cosmos",
    "planets_art",
    # THE CONTINENTS (owner-sealed matrix 2026-07-21): the six weekday
    # columns ride the six continents — the dial's OWN Earth-marker faces
    # (assets/earth/) elevated to a weekday theme (owner exception to the
    # one-image-one-place law, sealed: quality art never shown large
    # elsewhere). Bodies follow the user's earth_style and the live sky's
    # day/night at render (config.defaults.continents_body_art); the
    # Sunday dual is the two poles (Antarctic Ruler / Arctic Servant), the
    # Ninth is Zealandia with the Pangea easter-egg (core.continents).
    "continents",
    # The Inner Wheel on the dial (owner 2026-07-14): the emblem
    # families as weekday themes — the art lives in assets/emblem/.
    "virtues",
    "sins",
    "moods",
    # COMPLETION WAVE I (Session 31, 2026-07-29): three casts whose art
    # had been generated and correctly placed for a week without ever
    # being registered here — the failure THE THEME COMPLETION LAW
    # (project CLAUDE.md) was written for. Each ships wired, worded and
    # seated in the Encyclopedia in the same round.
    "age_of_heroes",       # Greek Monsters — the Olympians' bestiary
    "celestial_court",     # Chinese Mythology — gods, immortals, one rebel
    "corporate",           # The Corporation — the executive committee
    # COMPLETION WAVE II (Session 32, 2026-07-29): the World of Warcraft
    # franchise. THREE casts riding the SAME nine seats with different
    # figures — three THEMES on the dial (backlog structural answer 1:
    # FIGURE_ROSTERS is a two-value GLOBAL switch, so a franchise's
    # blocks can only be themes), ONE card in the Encyclopedia with a
    # three-way switcher (answer 2).
    "wow_alliance",        # the Grand Alliance's own command
    "wow_horde",           # the new Horde's leadership
    "wow_evil",            # the enemies both were made against
    # COMPLETION WAVE II, second half (Session 32, 2026-07-29): the
    # Cyberpunk 2077 franchise, the SAME three-casts-one-week shape as
    # the Warcraft half above — three THEMES on the dial, ONE card in
    # the Encyclopedia. These three are the only casts in the registry
    # whose seats carry a ROSTER: a seat may hold several named
    # factions/figures and rotate through them daily
    # (`defaults.WEEKDAY_SEAT_ROSTERS`).
    "cp_gangs",            # the factions that hold Night City's ground
    "cp_street",           # the people who live on it
    "cp_corpo",            # the powers that move behind both
)

# The bronze-plate themes (owner 2026-07-12): their medallions can wear
# a METAL — bronze is the art as drawn, gold and silver are runtime
# tritone tints. All other themes are full-color and never tint.
METAL_THEMES = (
    "greek", "norse", "profession", "wolf", "bee", "elephant",
    "cosmos",              # bronze star-chart medallions + colored arc
    "planets_art",         # the Planets "Art" look (owner 2026-07-18)
    # Completion wave I (Session 31): all three casts ship a bronze
    # primary register with a colored/ sibling, so all four looks are
    # available — no THEME_METALS_OVERRIDE needed for any of them.
    "age_of_heroes", "celestial_court", "corporate",
    # Completion wave II (Session 32): the three WoW casts are bronze
    # carved relief in primary/bronze with a full-paint colored/ sibling
    # per plate — the same cameo-master shape, so all four looks apply.
    "wow_alliance", "wow_horde", "wow_evil",
    # Completion wave II, Cyberpunk half (Session 32): aged-bronze
    # carved relief in primary/bronze with a full-repaint neon-noir
    # colored/ sibling per plate (the sheet's own two-register law), so
    # all four looks apply here too.
    "cp_gangs", "cp_street", "cp_corpo",
)
# "colored" (owner 2026-07-12) is the FOURTH look: fresh full-color
# badges from the theme's colored/ subfolder — separate art, no swap.
THEME_METALS = ("gold", "bronze", "silver", "colored")
# Per-theme override (owner 2026-07-18): planets_art is bronze-plate
# medallion art like the pantheon sets, but its source has NO colored/
# subfolder — a half-available look must never be offered, so it drops
# "colored" from its own allowed set. Absent entries fall back to the
# full THEME_METALS tuple; every call site that offers a theme's metal
# choices (menu, Settings dialog, settings validation, tests) must read
# through `theme_metals()` rather than the flat tuple.
THEME_METALS_OVERRIDE: dict[str, tuple[str, ...]] = {
    "planets_art": ("gold", "bronze", "silver"),
}


def theme_metals(theme: str) -> tuple[str, ...]:
    """The metal looks `theme` may wear — THEME_METALS unless the theme
    overrides it (documented exceptions only, see THEME_METALS_OVERRIDE)."""
    return THEME_METALS_OVERRIDE.get(theme, THEME_METALS)

# Theme -> symbolism.json blurb key (the encyclopedic text under the
# hexa diamond hover follows the active theme).
WEEKDAY_THEME_BLURBS = {
    "planets": "day",
    "planet_signs": "day",
    "greek": "greek",
    "norse": "norse",
    "egypt": "egypt",
    "slavic": "slavic",
    "alchemy": "alchemy",
    "japan": "japan",
    "religion": "religion",
    "religion_alt": "religion_alt",
    "profession": "profession",
    # The animal societies reuse the generic day blurb (the legacy
    # blurb path never grew theme sets of its own).
    "wolf": "day",
    "bee": "day",
    "elephant": "day",
    "bible": "day",
    "bible2": "day",
    "bible_dark": "day",
    "cosmos": "day",
    "planets_art": "day",
    # The continents reuse the generic day blurb (the hexa-diamond
    # blurb path never grew a themed set of its own — its rich text
    # lives in the article, not the one-line arm blurb).
    "continents": "day",
    "virtues": "day",
    "sins": "day",
    "moods": "day",
    # Completion wave I (Session 31): each cast carries its OWN arm
    # blurb set — a figure cast whose members are not the planets has
    # nothing to say through the generic day line.
    "age_of_heroes": "age_of_heroes",
    "celestial_court": "celestial_court",
    "corporate": "corporate",
    # Completion wave II (Session 32): one blurb set per CAST, never one
    # per franchise — the three ride the same seats with different
    # people, and the hover line names the person (CUBE.md Charter
    # rule 5).
    "wow_alliance": "wow_alliance",
    "wow_horde": "wow_horde",
    "wow_evil": "wow_evil",
    # Completion wave II, Cyberpunk half (Session 32): same law again —
    # one blurb set per CAST. A rotating seat's line names every member
    # of its roster, so the hover never describes a figure the dial is
    # not currently able to show.
    "cp_gangs": "cp_gangs",
    "cp_street": "cp_street",
    "cp_corpo": "cp_corpo",
}

# Theme -> symbolism.json article set (the glyph theme shares the
# planet articles — same entities, different art).
WEEKDAY_THEME_ARTICLES = {
    "planets": "planets",
    "planet_signs": "planets",
    "greek": "greek",
    "norse": "norse",
    "egypt": "egypt",
    "slavic": "slavic",
    "alchemy": "alchemy",
    "japan": "japan",
    "religion": "religion",
    "religion_alt": "religion_alt",
    "profession": "profession",
    "wolf": "wolf",
    "bee": "bee",
    "elephant": "elephant",
    "bible": "bible",
    "bible2": "bible2",
    "bible_dark": "bible_dark",
    "cosmos": "cosmos",
    # The medallion look shares the planet articles — same entities,
    # different art (like the glyphs).
    "planets_art": "planets",
    "continents": "continents",
    "virtues": "virtues",
    "sins": "sins",
    "moods": "moods",
    # Completion wave I (Session 31): own article set per cast.
    "age_of_heroes": "age_of_heroes",
    "celestial_court": "celestial_court",
    "corporate": "corporate",
    # Completion wave II (Session 32): own article set per cast, for the
    # same reason — three sets on one seat are three different people,
    # and each article argues THAT person's own deed.
    "wow_alliance": "wow_alliance",
    "wow_horde": "wow_horde",
    "wow_evil": "wow_evil",
    # Completion wave II, Cyberpunk half (Session 32): own article set
    # per cast. Where a seat carries a roster the article argues every
    # member of it — they are not one faction seen twice, they are two
    # answers to the question the seat asks.
    "cp_gangs": "cp_gangs",
    "cp_street": "cp_street",
    "cp_corpo": "cp_corpo",
}

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
WEEKDAY_THEME_NINTHS = {
    "wolf": ("Sigma", "wolf/primary/bronze/Sigma.png"),
    "bee": ("The Swarm", "bee/primary/bronze/Swarm.png"),
    "elephant": ("The Graveyard", "elephant/primary/bronze/Graveyard.png"),
    "cosmos": ("The Big Bang", "cosmos/primary/bronze/Big_Bang.png"),
    "greek": ("Gaia", "greek/pantheon/bronze/Gaia.png"),
    "norse": ("Yggdrasil", "norse/pantheon/bronze/Yggdrasil.png"),
    "egypt": ("The Pharaoh", "egypt/pantheon/bronze/Pharaoh.png"),
    # TRIGLAV IS ONE PLATE, NOT TWO (Rule #19, fixed 2026-07-29): the
    # Round Four adjudication locks him as the ninth in BOTH roster
    # modes, and his sheet drops the art in the PRIMARY register — the
    # pantheon copy would be the same image under a second name. The
    # table pointed at that never-drawn copy while `Triglav_gem.png`
    # sat on disk in `primary/`, so the seat read as pending art.
    "slavic": ("Triglav", "slavic/primary/bronze/Triglav.png"),
    "alchemy": ("The Philosopher's Stone", "alchemy/primary/colored/Stone.png"),
    "profession": ("The Polymath", "profession/primary/bronze/Polymath.png"),
    "religion": ("Freemasonry", "creeds/primary/colored/Freemasonry.png"),
    "religion_alt": (
        "The Unknown God", "creeds/secondary/colored/Unknown_God.png",
    ),
    "bible": ("The Holy Trinity", "bible/primary/colored/Holy_Trinity.png"),
    "bible2": ("Melchizedek", "bible/secondary/colored/Melchizedek.png"),
    "bible_dark": ("The Ninth Circle", "bible/dark/colored/Ninth_Circle.png"),
    # THE CONTINENTS' NINTH (owner-sealed matrix 2026-07-21): ZEALANDIA,
    # the literal Unfound — a true continent 94% drowned, unrecognized
    # until 2017. Its plate is wired ahead of the owner's art (relative
    # to WEEKDAY_ART_DIR, reaching the earth family: assets/earth/),
    # graceful-absent until it lands, exactly like Triglav.
    "continents": ("Zealandia", "../earth/zealandia.png"),
    # COMPLETION WAVE I (Session 31): three Excluded ninths, each argued
    # in its own sheet — Pegasus is born OF the Monday seat and belongs
    # to neither the monster line nor the god line; the Buddha is the one
    # being who could tell the Sunday dual's two faces apart (and the one
    # who extinguished the Ninth's own sin, WISH); the Founder is the
    # origin an org chart no longer names.
    "age_of_heroes": ("Pegasus", "age_of_heroes/primary/bronze/Pegasus.png"),
    "celestial_court": ("Buddha", "celestial_court/primary/bronze/Buddha.png"),
    "corporate": ("The Founder", "corporate/primary/bronze/Founder.png"),
    # COMPLETION WAVE II (Session 32): three Excluded ninths, each argued
    # in the franchise's own sheet — Turalyon kept the same oath for a
    # thousand years with no Alliance in reach to keep it for; Rexxar
    # belongs to no people at all and came anyway; Medivh is the one
    # figure of the Evil cast who never chose what he became and is
    # nevertheless responsible for most of it.
    "wow_alliance": ("Turalyon", "wow_alliance/primary/bronze/Turalyon.png"),
    "wow_horde": ("Rexxar", "wow_horde/primary/bronze/Rexxar.png"),
    "wow_evil": ("Medivh", "wow_evil/primary/bronze/Medivh.png"),
    # COMPLETION WAVE II, Cyberpunk half (Session 32): three Excluded
    # ninths, each argued in the sheet's own terms — NetWatch is the
    # only power in the Gangs cast with no ground at all; V is the one
    # figure the Street cast is entirely about and the circle has no
    # chair for; Alt Cunningham has had no body since 2013 and is the
    # demonstration of what the Power cast is actually fighting over.
    # The Alt seat ROTATES with Rache Bartmoss in lockstep with the
    # Throne and the Mirror (`defaults.WEEKDAY_SEAT_ROSTERS`).
    "cp_gangs": ("NetWatch", "cp_gangs/primary/bronze/Netwatch.png"),
    "cp_street": ("V", "cp_street/primary/bronze/V.png"),
    "cp_corpo": (
        "Alt Cunningham", "cp_corpo/primary/bronze/Alt_Cunningham.png",
    ),
}

# THE PANGEA EASTER EGG (owner-sealed matrix 2026-07-21): Pangea shows
# INSTEAD of Zealandia on the Ninth seat ONLY when the sky is doing
# something on the traveled day — an eclipse, a season turning point, or
# a full/new moon day (~1/11 of the year). Same story, deeper time: was
# once ALL, split, and by the supercontinent cycle will return. The LAW
# lives in core.continents; render.layers.theme_ninth reads this alt
# table when the law fires. Plate wired ahead of the owner's art
# (graceful-absent), same earth-family home as Zealandia.
WEEKDAY_THEME_NINTH_EASTER_EGG = {
    "continents": ("Pangea", "../earth/pangea.png"),
}

# THE DUAL/NINTH TIME WINDOW (owner seal 2026-07-29, superseding
# INSTRUCTION #5's hour widths): half an hour either side of the day's
# SOLAR anchors (never wall-clock — `core.angles.hours_between` reads
# the actual `DayContext.sun.noon`), i.e. solar 11:30-12:30 and
# 23:30-00:30. In BOTH windows the NINTH shows; outside them the
# CENTER seat follows the sky itself — DAYLIGHT the Ruler, NIGHT the
# Servant (`render.layers.center_face`) — and a two-badge Sunday swaps
# ONE seat per window (`render.layers.dual_seat_ninth`: near noon the
# Ninth replaces the SERVANT beside the Ruler, near midnight the RULER
# beside the Servant). Themes with no Ninth ignore the windows.
CENTER_WINDOW_HOURS = 0.5

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
# month, so — exactly like defaults.SLAVIC_MONTHS mounts by Gregorian
# month rather than by the true (locally-drifting) bloom date — this
# table fixes ONE animal per Gregorian month for the static 12-wedge
# mount; the LIVE lunar month (core.moon.chinese_zodiac) is unaffected.
CHINESE_MONTH_BRANCH_ANIMALS = {
    1: "Ox", 2: "Tiger", 3: "Rabbit", 4: "Dragon", 5: "Snake", 6: "Horse",
    7: "Goat", 8: "Monkey", 9: "Rooster", 10: "Dog", 11: "Pig", 12: "Rat",
}

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
# read by both the dial (render.layers.thirteenth_plate) and its hover
# (render.compositor). "chinese" (The Cat) is NOT solar-triggered — see
# core.blue_moon.chinese_leap_month — it shares this table only because
# it shares the CENTER seat.
#
# THE AXLE LAW (CANON.md §The Axle, owner-sealed 2026-07-29) extends this
# SAME table with the PERSON-CENTERS — Hestia/Jesus/Prudence/Cunning/Peace
# — the throne/hiding-place axles of the Olympians, Apostles, Virtue Wheel
# (both registers) and Emotions Dozens. Unlike the four members above,
# they carry NO year-rule at all: `PERSON_CENTERS` below marks them
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
}
# THE AXLE LAW's ALWAYS-PRESENT half (CANON §The Axle: "PERSON-CENTERS
# stand ALWAYS... no moon count, no window") — every key here is
# unconditionally a member of `core.blue_moon.thirteenth_candidates` on
# every date, regardless of year or window, unlike the four calendar-
# driven keys above (whose sealed year-rules are untouched by this set).
PERSON_CENTERS = frozenset({"hestia", "jesus", "prudence", "cunning", "peace"})
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

# Eclipse VISIBILITY (owner verdict "može", fix round E, 2026-07-19):
# a SOLAR eclipse is visible to the observer only within this great-
# circle distance of the catalog's greatest-eclipse point (the path of
# totality/partiality does not reach much farther); LUNAR visibility has
# no distance term — a lunar eclipse is visible from the whole night
# hemisphere, so only "Moon above the horizon" gates it.
ECLIPSE_SOLAR_VISIBILITY_KM = 3500.0
EARTH_RADIUS_KM = 6371.0            # mean radius — the great-circle distance basis

# Year-wheel anchor angle (mod 360) -> season event name, PER CLIMATE
# ZONE (owner decision 2026-07-10): the southern hemisphere flips the
# seasonal names (their Summer Solstice is the December one) and the
# tropics use the neutral month names (June/December Solstice,
# March/September Equinox). SEASON_EVENT_NAMES keeps the northern table
# as the canonical angle map.
SEASON_EVENT_NAMES = {
    0: "Summer Solstice",
    90: "Autumn Equinox",
    180: "Winter Solstice",
    270: "Spring Equinox",
}
ZONE_SEASON_EVENT_NAMES = {
    "north": SEASON_EVENT_NAMES,
    "south": {
        0: "Winter Solstice",
        90: "Spring Equinox",
        180: "Summer Solstice",
        270: "Autumn Equinox",
    },
    "tropics": {
        0: "June Solstice",
        90: "September Equinox",
        180: "December Solstice",
        270: "March Equinox",
    },
}

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
# HSV saturation (`render.layers.palette_for`).
POINTER_SATURATION_RANGE = (0.0, 1.0)
POINTER_SATURATION_SLIDER_STEP = 1
# RING (new, Session 21-D): the ring band art's HSV saturation — the
# ring plate AND its letter/numeral overlay (`render.layers.RingLayer`,
# after the ring_tint recolor). The Umbra and hands do not read this —
# see layers.md's RingLayer note for the ground-truthed scope.
RING_SATURATION_RANGE = (0.0, 1.0)
RING_SATURATION_SLIDER_STEP = 1

# The tropics span the Tropic of Cancer to the Tropic of Capricorn;
# their year splits into WET and DRY halves bounded by the equinoxes
# (owner decision) — the wet half centers on the hemisphere's high sun.
TROPIC_LATITUDE_DEG = 23.44
# One tropical year — used only to SYNTHESIZE an equinox instant that
# falls just before the bundled anchor span (day-count display accuracy).
TROPICAL_YEAR_DAYS = 365.2422

# Body -> Sunday-first weekday index (the owner's numbering used by the
# shared-slot priority rule: the occupant whose day comes NEXT wins).
SUNDAY_FIRST_INDEX = {
    "sun": 0,
    "moon": 1,
    "mars": 2,
    "mercury": 3,
    "jupiter": 4,
    "venus": 5,
    "saturn": 6,
}

# Weekday slots per pointer: (dial degrees from the pointer's TOP vertex,
# occupant bodies). Slots rotate WITH the star (owner decision). Owner's
# layouts: hexa = one body per arm, Sun in the center; cross = pairs on
# 6/12/18 with Wednesday alone at the bottom; octa = one per arm with the
# bottom arm showing the digital time instead of a body.
POINTER_WEEKDAY_SLOTS = {
    "hexa": (
        (0.0, ("jupiter",)),
        (60.0, ("mars",)),
        (120.0, ("venus",)),
        (180.0, ("mercury",)),
        (240.0, ("moon",)),
        (300.0, ("saturn",)),
    ),
    "cross": (
        (0.0, ("jupiter", "sun")),
        (90.0, ("mars", "venus")),
        (180.0, ("mercury",)),
        (270.0, ("moon", "saturn")),
    ),
    "octa": (
        (0.0, ("sun",)),
        (45.0, ("mars",)),
        (90.0, ("venus",)),
        (135.0, ("mercury",)),
        (225.0, ("moon",)),
        (270.0, ("saturn",)),
        (315.0, ("jupiter",)),
    ),
    # TRIO (owner-approved pairing, 2026-07-10): Faith 12h = Jupiter
    # (the Priest) + Saturn (faith tried by time); Love 20h = Venus +
    # Mars (the classic pair); Hope 4h = Moon + Mercury (the dawn
    # herald). Sunday's Sun sits in the center, like the hexa layout.
    "trio": (
        (0.0, ("jupiter", "saturn")),
        (120.0, ("venus", "mars")),
        (240.0, ("moon", "mercury")),
    ),
    # AURORA (owner spec 2026-07-12): one FIXED slot at the imagined
    # south — the dial bottom, above the Omega — showing today's body
    # only (all seven occupants -> the priority rule always picks
    # today). It never rotates with the sun.
    "aurora": (
        (180.0, ("sun", "moon", "mars", "mercury", "jupiter", "venus",
                 "saturn")),
    ),
    # CALENDAR (owner 2026-07-16): no weekday model of its own — it uses
    # the PINNED slot layout (like Aurora / the pointer-off case), one
    # fixed slot at the dial bottom above the Omega showing today alone.
    "calendar": (
        (180.0, ("sun", "moon", "mars", "mercury", "jupiter", "venus",
                 "saturn")),
    ),
    # THE ROSE'S COLOR LAW (owner seal 2026-07-27, CUBE.md §The Rose).
    # The seat is the HUE, not the position: it is the Prism primary canon
    # with the two Sunday hues lightened, because Sunday needs blue and
    # red for its own two faces. Bodies ride their BADGES as always —
    # never painted into the diamonds.
    #   12h yellow THU · 15h orange TUE · 18h red SUN (Ruler)
    #   21h rose  FRI · 24h purple WED · 03h cyan  MON
    #   06h blue  SUN (Servant, `servant_seat_angle`) · 09h green SAT
    # Six weekdays plus the dual Sunday fill all EIGHT arms, so no arm
    # is reserved for anything else and Thursday and Wednesday keep
    # their canonical color seats. The 06h SERVANT seat is absent from
    # this table on purpose — exactly as 24h is absent from the octa's:
    # the seat is the Servant face's alone and
    # `render.layers.servant_holds_the_seat` hands it to him.
    "rose": (
        (0.0, ("jupiter",)),        # 12h yellow — Thursday
        (45.0, ("mars",)),          # 15h orange — Tuesday
        (90.0, ("sun",)),           # 18h red    — Sunday, the Ruler
        (135.0, ("venus",)),        # 21h rose   — Friday
        (180.0, ("mercury",)),      # 24h purple — Wednesday
        (225.0, ("moon",)),         # 03h cyan   — Monday
        (315.0, ("saturn",)),       # 09h green  — Saturday
    ),
}

# The SOUTH SLOT home angle and the Aurora DUAL layout (owner spec
# 2026-07-12): with BOTH the weekday body and the slot on, they flank
# the bottom ±45° — the weekday at 3h on the left, the slot at 21h on
# the right.
#
# STALE-COMMENT CORRECTION (owner 2026-07-27): this comment used to
# claim "the Compass reserves this bottom arm for it". It has not been
# true since the dual-Sunday round — the Compass shows all EIGHT arms,
# and its 24h seat belongs to the SERVANT face of Sunday
# (`render.layers.servant_holds_the_seat`), which is exactly why
# `POINTER_WEEKDAY_SLOTS["octa"]` has no 180° entry. A later change
# moved the truth and left the old sentence standing, and a session
# read it and believed it. When behavior moves, the sentence that
# described the old behavior DIES WITH IT.
SOUTH_SLOT_ANGLE = 180.0
# The SERVANT face's own seat per pointer (owner 2026-07-27): 24h
# everywhere the dual Sunday has always sat, but the ROSE seats him on
# the BLUE arm at 06h — blue is Judas's hue and the servant's, red is
# Lucifer's and the master's, and 6 + 6 + 6 lands the pair on 06h and
# 18h (CUBE.md §The Rose). `render.layers.servant_seat_angle` is the
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
# over unchanged. `render.layers.ruler_seat_angle`/`servant_seat_angle`
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
