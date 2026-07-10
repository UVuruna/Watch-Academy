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
POINTER_POINTS = {"hexa": 6, "cross": 4, "octa": 8, "trio": 3}

# Display names chosen by the owner (FINAL.txt #8): the internal keys
# stay hexa/cross/octa/trio (settings and code stability); the menu and
# the docs speak these.
POINTER_DISPLAY_NAMES = {
    "trio": "Trinity",
    "cross": "Seasons",
    "hexa": "Prism",
    "octa": "Compass",
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

# What the octa pointer's bottom arm shows (user-selectable). The four
# image modes draw the owner's PNG art (assets/skins/domy/zodiac/<dir>)
# and fall back to the text form until the art exists (documented
# fallback; the tray disables them while the folder is empty).
OCTA_SLOT_MODES = (
    "time",
    "date",
    "day_length",
    "zodiac_sign",
    "zodiac_logo",
    "zodiac_constellation",
    "zodiac_text",
    "chinese_logo",
    "chinese_text",
)
OCTA_SLOT_ART_DIRS = {
    "zodiac_sign": "sign",
    "zodiac_logo": "logo",
    "zodiac_constellation": "constellation",
    "chinese_logo": "chinese",
}

# Earth marker style: the owner ships every continent in a clean and an
# atmosphere version.
EARTH_STYLES = ("clean", "atmo")

# Ring letter FINISH (owner spec, FINAL.txt #6): the letters are the
# owner's separate art (assets/ring/letters/<File>_<finish>.png),
# positioned by code so the ring tint never touches them. "gold" =
# M/D/Y/P/H gold with a silver Omega; "silver" = the inverse.
RING_FINISHES = ("gold", "silver")
RING_LETTER_FILES = {"M": "M", "D": "D", "Y": "Y", "Π": "P", "H": "H", "Ω": "Omega"}

# Weekday body themes (SYMBOLISM.md canon): "planets" uses the skin's
# own weekday unit; the others swap in the owner's themed art from
# assets/skins/domy/weekday/<theme>/ with the canon display names.
WEEKDAY_THEMES = (
    "planets",
    "planet_signs",
    "greek",
    "norse",
    "religion",
    "profession",
)

# Theme -> symbolism.json blurb key (the encyclopedic text under the
# hexa diamond hover follows the active theme).
WEEKDAY_THEME_BLURBS = {
    "planets": "day",
    "planet_signs": "day",
    "greek": "greek",
    "norse": "norse",
    "religion": "religion",
    "profession": "profession",
}

# Theme -> symbolism.json article set (the glyph theme shares the
# planet articles — same entities, different art).
WEEKDAY_THEME_ARTICLES = {
    "planets": "planets",
    "planet_signs": "planets",
    "greek": "greek",
    "norse": "norse",
    "religion": "religion",
    "profession": "profession",
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

# Year-wheel anchor angle (mod 360) -> season event name shown in the
# Earth hover during the glow window.
SEASON_EVENT_NAMES = {
    0: "Summer Solstice",
    90: "Autumn Equinox",
    180: "Winter Solstice",
    270: "Spring Equinox",
}

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
}
OCTA_TIME_SLOT_ANGLE = 180.0         # the bottom arm carries the digital time
