"""The sky the dial reads - sun, moon, year.

Every invariant of the real sky this instrument shows: how far below
the horizon dawn and dusk are, where the six season anchors sit on
the unwrapped year wheel, how long a lunation is and what its eight
phases are called, what each hemisphere and the tropics name a
turning point, the latitude that bounds the tropics, and the filename
of the optional Deep Time pack that widens the bundled coverage.

It is deliberately NOT `dial.py`: those are the numbers of the DRAWN
face - its geometry and its convention - and these are the numbers of
the SKY the face reports. `core/` computes with them; `config/dial.py`
never needs one of them.

Born 2026-08-19, when the owner ruled that `config/constants.py`'s
**38 top-level sections** were a junk drawer, not a directory, and gave
the split its module names himself. Nothing here is new data - every
table below stood in `constants.py` under its own section banner and
moved WHOLE, with its comments; the callers were repointed, and no
re-export shim was left behind (`rules/CODE.md` - No backward
compatibility). The whole map, one row per module, is in
[the folder doc](___config.md).

Layer: config - pure Python, no Qt, no wall clock, no sibling import.
"""

# ══════════════════════════════ THE SUN ══════════════════════════════
CIVIL_DEPRESSION = 6.0              # degrees below horizon for dawn/dusk
HORIZON_ELEVATION_DEG = -0.833      # solar disc touches the horizon (refraction)
CIVIL_TWILIGHT_ELEVATION_DEG = -6.0

# ═══════════════════════════ THE YEAR WHEEL ═══════════════════════════
# Unwrapped dial angles of the six season anchors bracketing one calendar
# year in seasons_utc.json: previous December solstice, spring equinox,
# summer solstice (top of dial after mod 360), autumn equinox, December
# solstice, next spring equinox. Clockwise, 0 deg = summer solstice = top.
YEAR_ANCHOR_ANGLES = (180.0, 270.0, 360.0, 450.0, 540.0, 630.0)

# ══════════════════════════════ THE MOON ══════════════════════════════
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

# ═════════════════════════════ DEEP TIME ═════════════════════════════
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

# ═══════════════════════════ SEASON EVENT NAMES ═══════════════════════════
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

# ═══════════════════════════ TROPICS ═══════════════════════════
# The tropics span the Tropic of Cancer to the Tropic of Capricorn;
# their year splits into WET and DRY halves bounded by the equinoxes
# (owner decision) — the wet half centers on the hemisphere's high sun.
TROPIC_LATITUDE_DEG = 23.44
# One tropical year — used only to SYNTHESIZE an equinox instant that
# falls just before the bundled anchor span (day-count display accuracy).
TROPICAL_YEAR_DAYS = 365.2422
