"""Product-defining invariants. These values NEVER change at runtime
and are not user-tunable — they define what DOMY Watch is.

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
# The Gemini and ChatGPT generations COEXIST (owner 2026-07-14); every
# sourced asset root holds one subtree per source —
# assets/<root>/<source>/<family>/... — the user picks in Settings and
# a file missing in the chosen source falls back to the other. Code
# keeps building CANONICAL source-less paths; config.paths.art_file
# resolves them at every disk boundary.
ART_SOURCES = ("gemini", "chatgpt")
ART_SOURCE_DEFAULT = "gemini"
ART_SOURCE_TITLES = {"gemini": "Gemini", "chatgpt": "ChatGPT"}
ART_SOURCED_ROOTS = (
    "weekday", "zodiac", "emblem", "badge", "instrument",
    # The archetype stained glass (owner sealed package 2026-07-16):
    # assets/archetype/<source>/<archetype>/<file>.png.
    "archetype",
    # The era/age rose windows (owner fix, 2026-07-20 — the generated
    # files always shipped as assets/era/<source>/<Name>.png, one
    # subtree per source like every other family; this root was simply
    # never added, so `art_file` passed the sourceless canonical path
    # straight through and every era badge silently failed its own
    # existence check).
    "era",
    # The eclipse category emblems (GUIDE shoot find, 2026-07-20 —
    # the same silent-absence class as "era" above: the ChatGPT batch
    # landed as assets/eclipse/chatgpt/<Kind>_<Type>.png, but with the
    # root missing here the encyclopedia chapter plates and the
    # hover-card badges resolved the sourceless path and drew nothing).
    "eclipse",
)

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
# ride the Paint/Light slot: paint = the Zodiac Dozen, light = the
# Almanac (Month) Dozen. It has NO arm HALF-ANGLE (armless, like
# Aurora): the star geometry and the arm hovers skip it explicitly.
POINTER_POINTS = {
    "hexa": 6, "cross": 4, "octa": 8, "trio": 3, "aurora": 7,
    "calendar": 12,
}
CALENDAR_WEDGES = 12
CALENDAR_WEDGE_DEG = 360.0 / CALENDAR_WEDGES        # 30° per 2-hour wedge
# The two lighting modes (owner 2026-07-16, both user-selectable):
# "hour" — the wedge under the HOUR HAND lights (the Chinese
# double-hour, shichen); "year" — the current MONTH's wedge (Almanac)
# or the current SIGN's wedge (Zodiac).
CALENDAR_LIGHTING_MODES = ("hour", "year")

# Display names chosen by the owner (FINAL.txt #8): the internal keys
# stay hexa/cross/octa/trio (settings and code stability); the menu and
# the docs speak these.
POINTER_DISPLAY_NAMES = {
    "trio": "Trinity",
    "cross": "Seasons",
    "hexa": "Prism",
    "octa": "Compass",
    "aurora": "Aurora",     # no arms — the day itself painted in bands
    "calendar": "Calendar",  # no arms — the year/day in twelve wedges
}

# The wheel-pair LABELS per pointer (owner 2026-07-17, ROADMAP 11; naming
# refinements 2026-07-17/19) — RAW English, the ONE table both the Design
# menu's palette-style pair (`app.controller._build_menu`, `tr()`-wrapped
# at build time) and the watch TITLE row (`app.controller.watch_title`,
# untranslated — a name, not chrome) read (Rule #5: one source, two
# readers). Index 0 = "paint" style, index 1 = "light" style
# (`Settings.palette_style`). Every pointer carries two distinct wheels
# now (the Seasons gained the Elements wheel) — never grayed.
POINTER_PALETTE_LABELS = {
    "trio": ("Court", "Family"),
    "cross": ("Temperaments", "Elements"),
    # The FULL idiom (owner pick 2026-07-19: "Walks of Life", not caste —
    # the paths one walks, open to all, against the closed hereditary
    # caste reading).
    "octa": ("Walks of Life", "Ages"),
    "aurora": ("Warm", "Cool"),
    "calendar": ("Zodiac", "Almanac"),
    "default": ("Paint palette", "Light palette"),
}

# What each palette circle COLORS (owner spec 2026-07-11: hovering a
# palette swatch in Settings names its arm position). Order matches
# PALETTE_PRESETS — clockwise from the top arm; the Compass speaks in
# cardinal directions, the others in dial positions.
POINTER_ARM_LABELS = {
    "trio": ("Top", "Right", "Left"),
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
    # Calendar wedges, clockwise from the TOP wedge. The two wheels
    # differ (paint = signs from the top boundary, light = months from
    # the top center), so the palette-editor labels stay NEUTRAL — the
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
POINTER_ARM_HALF_ANGLE_DEG = {"hexa": 30.0, "cross": 22.5, "octa": 22.5, "trio": 30.0}

# The trio's theological themes per arm angle (SYMBOLISM.md trio canon:
# Faith vertical toward God, Hope on the dawn side, Love with Venus).
# Like every pointer, the arm tip is the CENTER of its hue (owner
# correction 2026-07-10): Faith yellow spans 8h-16h, Love red 16h-24h,
# Hope blue 0h-8h.
TRIO_ARM_THEMES = {0.0: "Faith", 120.0: "Love", 240.0: "Hope"}

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

# Star + Aura palette styles (owner: "paint" = subtractive primaries —
# blue/red/yellow mix toward black; "light" = additive primaries —
# blue/red/green mix toward white). The cross pointer has a single
# seasons palette served under both styles.
PALETTE_STYLES = ("paint", "light")

# The SOUTH SLOT (menu name; the internal octa_* keys stay for settings
# and code stability, like the pointer keys): user-selected info near
# the dial bottom. On the Compass it IS the reserved bottom arm; the
# Trinity always has room at the south gap between its blue and red
# diamonds; Aurora always shows it (images only); Prism and Seasons
# gain it once the Weekday element is off (owner matrix 2026-07-12).
# The four image modes draw the owner's PNG art
# (assets/zodiac/<dir>) and fall back to the text form until the art
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
# style -> art folder under assets/zodiac/ (text styles draw no art).
# Family/variant tree (owner restructure 2026-07-14): astrology's
# plain logo is its PRIMARY variant.
ZODIAC_STYLE_ART_DIRS = {
    "sign": "astrology/sign",
    "logo": "astrology/primary",
    "constellation": "astrology/constellation",
    "colored": "astrology/colored",
}
CHINESE_STYLE_ART_DIRS = {
    "colored": "chinese/colored",
    "gold": "chinese/primary",
    "silver": "chinese/primary",
    "bronze": "chinese/primary",
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
# 2026-07-19, render.assets.letter_metal_file).
RING_FINISHES = ("gold", "silver", "bronze")

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
RING_TWO_METALS_DEFAULT = {"Mason": True}
# The full letter library (glyph -> art file) — presets and the custom
# ring builder choose from these, GOLD masters only; silver and bronze
# are derived from the gold master at load (owner 2026-07-19,
# render.assets.letter_metal_file — no more pre-rendered files). The
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
    "Symbols": ("✠",),
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
    # The Inner Wheel on the dial (owner 2026-07-14): the emblem
    # families as weekday themes — the art lives in assets/emblem/.
    "virtues",
    "sins",
    "moods",
)

# The bronze-plate themes (owner 2026-07-12): their medallions can wear
# a METAL — bronze is the art as drawn, gold and silver are runtime
# tritone tints. All other themes are full-color and never tint.
METAL_THEMES = (
    "greek", "norse", "profession", "wolf", "bee", "elephant",
    "cosmos",              # bronze star-chart medallions + colored arc
    "planets_art",         # the Planets "Art" look (owner 2026-07-18)
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
    "virtues": "day",
    "sins": "day",
    "moods": "day",
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
    "virtues": "virtues",
    "sins": "sins",
    "moods": "moods",
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
    "wolf": ("Sigma", "wolf/primary/sigma.png"),
    "bee": ("The Swarm", "bee/primary/swarm.png"),
    "elephant": ("The Graveyard", "elephant/primary/graveyard.png"),
    "cosmos": ("The Big Bang", "cosmos/primary/big_bang.png"),
    "greek": ("Gaia", "greek/pantheon/gaia.png"),
    "norse": ("Yggdrasil", "norse/pantheon/Yggdrasil.png"),
    "egypt": ("The Pharaoh", "egypt/pantheon/pharaoh.png"),
    "slavic": ("Triglav", "slavic/pantheon/triglav.png"),
    "alchemy": ("The Philosopher's Stone", "alchemy/primary/stone.png"),
    "profession": ("The Polymath", "profession/primary/Polymath.png"),
    "religion": ("Freemasonry", "religion/primary/freemasonry.png"),
    "religion_alt": (
        "The Unknown God", "religion/secondary/unknown_god.png",
    ),
    "bible": ("The Holy Trinity", "bible/primary/holy_trinity.png"),
    "bible2": ("Melchizedek", "bible/secondary/melchizedek.png"),
    "bible_dark": ("The Ninth Circle", "bible/dark/ninth_circle.png"),
}

# DUAL/NINTH CENTER TIME WINDOWS (owner INSTRUCTION #5 + solar
# amendment, round R3b item 3): hours either side of the day's SOLAR
# anchors (never wall-clock noon/midnight — `core.angles.hours_between`
# reads the actual `DayContext.sun.noon`) during which the CENTER seat
# of a hexa/trio/center_only weekday unit swaps its Sunday face. A
# theme with a Ninth shows it near solar NOON (owner: "Izmedju 11 i
# 13h"); EVIL (the Servant) shows near solar MIDNIGHT, narrower when a
# Ninth also claims noon ("Izmedju 23 i 1h") than when it is the ONLY
# alternate face a 2-face theme has ("izmedju 22h i 2h").
CENTER_NOON_WINDOW_HOURS = 1.0
CENTER_MIDNIGHT_WINDOW_HOURS = 1.0
CENTER_MIDNIGHT_WINDOW_HOURS_NO_NINTH = 2.0

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
}

# The Calendar lighting modes (owner 2026-07-16, both user-selectable):
# "hour" — the wedge under the HOUR HAND lights (the Chinese
# double-hour, shichen — the animal speaks); "year" — the current
# MONTH's wedge lights on the Almanac, the current SIGN's on the
# Zodiac.
CALENDAR_LIGHTING_MODES = ("hour", "year")
# The SOUTH SLOT home angle (the Compass reserves this bottom arm for
# it) and the Aurora DUAL layout (owner spec 2026-07-12): with BOTH the
# weekday body and the slot on, they flank the bottom ±45° — the
# weekday at 3h on the left, the slot at 21h on the right.
SOUTH_SLOT_ANGLE = 180.0
AURORA_DUAL_WEEKDAY_ANGLE = 225.0    # 3h — bottom left
AURORA_DUAL_SLOT_ANGLE = 135.0       # 21h — bottom right
