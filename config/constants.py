"""Product-defining invariants. These values NEVER change at runtime
and are not user-tunable — they define what DOMY Watch is.

Tunables (things a developer might reasonably adjust) live in defaults.py.
Win32 API literals live in winapi.py.
"""

APP_NAME = "DOMY Watch"
ORGANIZATION = "UVuruna"
SINGLE_INSTANCE_MUTEX = "DOMYWatch.SingleInstance"

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

# --- Bundled database coverage --------------------------------------------------
SEASONS_YEAR_RANGE = (1560, 2640)
MOON_PHASES_YEAR_RANGE = (1551, 2649)

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
POINTER_POINTS = {"hexa": 6, "cross": 4, "octa": 8, "trio": 3, "aurora": 7}

# Display names chosen by the owner (FINAL.txt #8): the internal keys
# stay hexa/cross/octa/trio (settings and code stability); the menu and
# the docs speak these.
POINTER_DISPLAY_NAMES = {
    "trio": "Trinity",
    "cross": "Seasons",
    "hexa": "Prism",
    "octa": "Compass",
    "aurora": "Aurora",     # no arms — the day itself painted in bands
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
OCTA_SLOT_MODES = (
    "time", "date", "day_length", "weekday", "zodiac", "ascendant",
    "chinese",
)
# The DAY SLOT can carry an astrology badge instead of the bodies
# (owner 2026-07-12) — in the PINNED layouts (Aurora, or the Pointer
# element off): it stands at the usual bottom spot, so the pair can
# read official sign left, ascendant right. Elsewhere the bodies rule.
# The TEXT modes (owner 2026-07-12: "time/date/day length can go in the
# day slot too") need the Pointer element OFF — under Aurora the day
# slot stays images-only, exactly like the info slot.
WEEKDAY_SLOT_MODES = (
    "weekday", "time", "date", "day_length", "zodiac", "ascendant",
    "chinese",
)
WEEKDAY_BADGE_POINTERS = ("aurora",)
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
# letters are pre-rendered files (setup/make_silver_letters.py).
RING_FINISHES = ("gold", "silver", "bronze")
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
# The full letter library (glyph -> art file) — presets and the custom
# ring builder choose from these; every glyph also ships a pre-rendered
# <Stem>_silver.png. The library is GROUPED (owner spec 2026-07-11):
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
)

# The bronze-plate themes (owner 2026-07-12): their medallions can wear
# a METAL — bronze is the art as drawn, gold and silver are runtime
# tritone tints. All other themes are full-color and never tint.
METAL_THEMES = ("greek", "norse", "profession", "wolf", "bee", "elephant")
# "colored" (owner 2026-07-12) is the FOURTH look: fresh full-color
# badges from the theme's colored/ subfolder — separate art, no swap.
THEME_METALS = ("gold", "bronze", "silver", "colored")

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
}

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
}
# The SOUTH SLOT home angle (the Compass reserves this bottom arm for
# it) and the Aurora DUAL layout (owner spec 2026-07-12): with BOTH the
# weekday body and the slot on, they flank the bottom ±45° — the
# weekday at 3h on the left, the slot at 21h on the right.
SOUTH_SLOT_ANGLE = 180.0
AURORA_DUAL_WEEKDAY_ANGLE = 225.0    # 3h — bottom left
AURORA_DUAL_SLOT_ANGLE = 135.0       # 21h — bottom right
