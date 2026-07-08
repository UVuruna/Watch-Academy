"""Product-defining invariants. These values NEVER change at runtime
and are not user-tunable — they define what DOMY Watch is.

Tunables (things a developer might reasonably adjust) live in defaults.py.
Win32 API literals live in winapi.py.
"""

APP_NAME = "DOMY Watch"
ORGANIZATION = "UVuruna"

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

# Regular hexagram geometry: the star's inner-hexagon vertices sit at
# tip_radius / sqrt(3) — each of the six diamonds spans (center, tip-30deg
# inner vertex, tip, tip+30deg inner vertex).
HEXAGRAM_INNER_FRACTION = 3 ** -0.5

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
# Sunday's body (Sun) sits in the dial center; the other six occupy the
# hexagram diamonds at fixed slots.
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

# Diamond slot of each orbiting body: dial degrees from the hexagram's TOP
# vertex, clockwise. The slots rotate WITH the hexagram (owner decision) —
# the bodies stay inside their diamonds. Sun has no slot (center).
WEEKDAY_SLOT_ANGLES = {
    "jupiter": 0.0,      # top    / yellow
    "mars": 60.0,        # upper-right / orange
    "venus": 120.0,      # lower-right / red
    "mercury": 180.0,    # bottom / purple
    "moon": 240.0,       # lower-left  / blue
    "saturn": 300.0,     # upper-left  / green
}
