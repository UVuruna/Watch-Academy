"""THE UMBRA WHEEL - the band of shadow around the dial.

The Umbra is the dial's outer band: it carries the moon through its
lunation, darkens for an eclipse, and marks the STATIONS the sun and
the moon pass. One subject, and the largest single section the old
`constants.py` held (74 logic lines under one banner): the band's
forms and section counts, its contrast variants, the moon band /
dark / transit styles with their defaults, the marker pointer shapes,
the solar and lunar eclipse styles with their band durations and
penumbral span, the moon and sun station styles, their glow, their
seasons and life stations, the phase-to-station and event-to-station
maps, the moving-body menus, and the tint modes.

Every one of them answers "what does the Umbra look like right now".

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

# ═══════════════════════════ THE UMBRA WHEEL ═══════════════════════════
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

# THE MOON HORIZON BAND (owner verdict 2026-08-09): the arc on the
# inner tick circle showing when the Moon stands above the horizon.
# "horizon" draws the band AND keeps `moon_hidden_alpha` dimming
# (they coexist); "dim_only" is today's dimming-only behavior with no
# band; "always_full" shows neither — the moon marker never dims.
MOON_BAND_MODES = ("horizon", "dim_only", "always_full")
MOON_BAND_MODE_DEFAULT = "horizon"
# The four owner-approved band styles (`render.layers.moon_band`),
# active only in "horizon" mode. "silver_thread" is THE DEFAULT.
MOON_BAND_STYLES = ("inverted", "silver_thread", "ticks", "glow")
MOON_BAND_STYLE_DEFAULT = "silver_thread"

# ==================================================================
# THE MOVING BODIES — the Moon and the Earth as part of the HANDS
# ==================================================================
# Owner verdict 2026-08-10, ruling on the rendering-proposals page: the
# Moon and the Earth are part of the HANDS system — they are what MOVES
# and points at the time — so every menu below is presented in the Watch
# Face's "Hands & Bodies" section beside the hand packs, not scattered
# through Pointer/Opacity. Each tuple is the picker's roster in display
# order; every option he circled is here and every option he crossed out
# is absent, including two that shipped as the only behavior (the
# translucent unlit half and the translucent transit) — those were the
# defect that opened the round, so they are RETIRED rather than kept as
# a menu entry nobody should choose.

# 1. THE UNLIT HALF. "opaque" fills the shadow region nearly solid;
# "cut_rim" (THE DEFAULT — his circled recommendation) draws the lit
# region alone under a permanent silver hairline around the true disc,
# so a new moon reads as a hollow ring instead of vanishing;
# "cut_ghost" is the same cut over a barely-there dark disc.
MOON_DARK_STYLES = ("cut_rim", "cut_ghost", "opaque")
MOON_DARK_STYLE_DEFAULT = "cut_rim"

# 2. WHEN THE MOON MEETS THE EARTH on the shared orbit lane.
# "lane_split" (THE DEFAULT) never lets them overlap — inside touching
# distance the Moon eases onto a slightly inner lane; "occultation"
# passes the Moon fully opaque in front with a shadow cast on the
# Earth; "shrink_pass" keeps the lane but scales the Moon down while
# it is inside the Earth's disc.
MOON_TRANSIT_STYLES = ("lane_split", "occultation", "shrink_pass")
MOON_TRANSIT_STYLE_DEFAULT = "lane_split"

# 3. THE POSITION POINTER's shape. All three ride the body's OWN dial
# angle (never a fixed "up" — the owner's correction of the proposal
# page, 2026-08-10): "triangle" is the shipped mark, "chevron" an open
# V outside the body, "gem" a faceted diamond seated on the ring line.
MARKER_POINTER_SHAPES = ("triangle", "chevron", "gem")
MARKER_POINTER_SHAPE_DEFAULT = "triangle"

# 4. SOLAR ECLIPSES. "halo" is the shipped glow-only signal; "bite"
# (THE DEFAULT) draws the occulting lunar disc across the Sun so the
# catalog MAGNITUDE becomes geometry — a bite, a ring of fire, a black
# disc in a corona; "magnitude_arc" adds a ring gauge instead.
#
# Owner ballot 2026-08-13 accepted three more, wired here (roster,
# label, settings round-trip) but WITHOUT their own painters yet — see
# `render.eclipse_style.resolve_eclipse_style`, the shared door every
# call site asks before it paints; each of the three below currently
# answers "cannot draw here, fall back to X" rather than pretending to
# be one of the three that already ship:
# "totality_path" (his recommendation) — a thin arc beside the body
# whose LENGTH and BRIGHTNESS say how near the observer stands to the
# path of totality: full and bright means standing IN the band, short
# and dim means the eclipse happens but 3,500 km away.
# "type_emblem" — a small emblem beside the body: a ring for annular,
# a double ring for hybrid.
# "dial_shadow" — for the minutes the eclipse lasts, the WHOLE ring
# loses light. The most aggressive of the six, so the owner's explicit
# instruction stands regardless of roster order: it is never the
# DEFAULT, only ever a selectable style.
ECLIPSE_SOLAR_STYLES = (
    "bite", "magnitude_arc", "halo",
    "totality_path", "type_emblem", "dial_shadow",
)
ECLIPSE_SOLAR_STYLE_DEFAULT = "bite"

# 5. LUNAR ECLIPSES. "halo" is the shipped uniform darkening;
# "umbra_sweep" (THE DEFAULT) draws Earth's shadow as an actual curved
# edge crossing the disc; "horizon_shadow" writes the event on the
# MOON HORIZON BAND instead of the body, which is the owner's own
# placement of it (2026-08-10, his words: not on the dial circle but on
# the line that shows where the Moon stands above the horizon), so it
# shows DURATION, which no halo can. It therefore needs
# `moon_band_mode == "horizon"`; without the band there is nothing to
# write on and it falls back to "halo" through the same door as below.
#
# Owner ballot 2026-08-13 accepted three more, wired here WITHOUT their
# own painters yet — same door, same honesty rule:
# "blood_moon" (his recommendation) — inside the umbra the colour slides
# toward copper in proportion to depth in shadow; the penumbra stays
# grey.
# "danjon_scale" — the Danjon L=0..L=4 brightness scale rendered as
# data, with a legend/text beside it.
# "contact_marks" — the horizon band carries four thin lines, the four
# contacts. It is an ADDITION on top of "horizon_shadow", not a
# replacement, so like it, it needs `moon_band_mode == "horizon"` and
# falls back the same way when the band is absent.
ECLIPSE_LUNAR_STYLES = (
    "umbra_sweep", "horizon_shadow", "halo",
    "blood_moon", "danjon_scale", "contact_marks",
)
ECLIPSE_LUNAR_STYLE_DEFAULT = "umbra_sweep"

# How wide the "horizon_shadow" segment is drawn on the band, in hours,
# centred on the catalog instant. A DOCUMENTED APPROXIMATION, stated
# here rather than hidden in the painter: the catalog stores only the
# instant of GREATEST eclipse, never a start and an end, so the band
# cannot draw the true contact times. Three hours is a typical
# umbral-phase span; the segment is therefore honest about WHEN the
# eclipse peaks and only indicative about how long it runs. If a future
# catalog carries contact times, this constant is what they replace.
ECLIPSE_BAND_DURATION_H = 3.0

# THE PENUMBRAL SPAN, as a MULTIPLE of the umbral one above — the
# "contact_marks" style's four lines are P1, U1, U4, P4, and the outer
# pair needs a span the catalog cannot give either. It is NOT a second
# guess: the shadow radii at the Moon's distance are ~2.6 lunar radii
# for the umbra and ~4.6 for the penumbra, the Moon crosses both on the
# same near-straight track, so the two chords — and therefore the two
# durations — stand in that same ~1.78 ratio (the identical ratio
# `render.moon_face`'s own measured shadow fractions carry, 2.40/1.35).
# So ECLIPSE_BAND_DURATION_H above remains the ONE approximation in the
# program and this derives from it; a catalog that one day carries real
# contact times replaces both at once. The marks are INDICATIVE and the
# docs say so — never presented as observed contact times.
ECLIPSE_PENUMBRAL_SPAN_RATIO = 1.78

# 6. THE MOON'S FOUR STATIONS — new moon is birth, first quarter is
# youth, full moon is the zenith of maturity, last quarter is age.
# "uniform" is the shipped single silver halo; "arc_grammar" (THE
# DEFAULT) gives each station its own mark; "inner_glow" ramps the
# glow's INTENSITY, never its reach (see MOON_STATION_GLOW below).
MOON_STATION_STYLES = ("arc_grammar", "inner_glow", "uniform")
MOON_STATION_STYLE_DEFAULT = "arc_grammar"

# THE INTENSITY RAMP, exactly as the owner specified it (2026-08-10):
# the full moon must not widen its halo into the distance but raise its
# INTENSITY, so it holds the strongest of the four; youth carries a glow
# both inside (on the dark part) and outside, and its OUTER intensity
# equals age's, which has no inner glow at all. So the glow RADIUS is
# constant across all four and only the alpha moves: (outer, inner) as
# fractions of the layer's own peak. Birth carries light INSIDE and
# radiates almost none; zenith has no dark half left to glow into, and
# takes the whole intensity outward.
MOON_STATION_GLOW = {
    "birth": (0.25, 0.55),
    "youth": (0.60, 0.60),
    "zenith": (1.00, 0.00),
    "age": (0.60, 0.00),
}

# 7. THE SUN'S FOUR STATIONS — the same life-arc across the year:
# winter solstice is birth, spring equinox youth, summer solstice the
# zenith, autumn equinox age. "uniform_gold" is the shipped halo;
# "uniform_seasonal" is the SAME halo wearing the season's own hue
# (the owner asked for both to survive, 2026-08-10); "arc_grammar"
# (THE DEFAULT) mirrors the Moon's grammar so one language is learned
# once and read on two clocks; "day_night_wedge" fills a ring to the
# day's own length.
SUN_STATION_STYLES = (
    "arc_grammar", "uniform_seasonal", "day_night_wedge", "uniform_gold",
)
SUN_STATION_STYLE_DEFAULT = "arc_grammar"

# The season each turning point opens, in the order the Sun meets them.
# The COLOURS are not defined here — "uniform_seasonal" reads
# `palette.INSTRUMENT_SEASON_COLORS`, the owner's own sampled season
# values sealed 2026-07-28, so the halo can never drift from the season
# wedge painted under it (THE PALETTE COLOUR LAW).
SUN_STATION_SEASONS = {
    "birth": "winter", "youth": "spring", "zenith": "summer", "age": "autumn",
}

# The four stations both bodies share, in life order — one roster, so a
# station can never exist in one table and be missing from the other.
LIFE_STATIONS = ("birth", "youth", "zenith", "age")

# Which station a principal instant opens. Keyed by the event NAME each
# body already carries (`ClockTick.moon_event` / `.season_event`), not
# by a re-derived angle: the name is what the hemisphere logic above
# already resolved, so a southern observer's Winter Solstice is birth
# for him even though it sits at the wheel angle a northern observer
# calls midsummer. The TROPICS' neutral names carry no season of their
# own, so they read on the northern convention (June Solstice = zenith),
# which is also what their wheel geometry says.
MOON_STATION_OF_PHASE = {
    "New Moon": "birth",
    "First Quarter": "youth",
    "Full Moon": "zenith",
    "Third Quarter": "age",
}
# THE ONE ROSTER of the eight menus above: setting name -> (choices,
# default). Every layer reads THIS instead of re-listing the menus —
# `app.settings_store` loads and saves by iterating it, the controller
# overlays the spec from it, and the Watch Face section builds its
# pickers from it. A menu added here reaches all four at once, and none
# of them can drift from the others (Rule #5, and the defect it
# prevents is concrete: seven near-identical load blocks pushed
# settings_store over THE STRUCTURE LAW's threshold on first writing).
MOVING_BODY_MENUS = {
    "moon_dark_style": (MOON_DARK_STYLES, MOON_DARK_STYLE_DEFAULT),
    "moon_transit_style": (MOON_TRANSIT_STYLES, MOON_TRANSIT_STYLE_DEFAULT),
    "marker_pointer_shape": (
        MARKER_POINTER_SHAPES, MARKER_POINTER_SHAPE_DEFAULT,
    ),
    "eclipse_solar_style": (
        ECLIPSE_SOLAR_STYLES, ECLIPSE_SOLAR_STYLE_DEFAULT,
    ),
    "eclipse_lunar_style": (
        ECLIPSE_LUNAR_STYLES, ECLIPSE_LUNAR_STYLE_DEFAULT,
    ),
    "moon_station_style": (MOON_STATION_STYLES, MOON_STATION_STYLE_DEFAULT),
    "sun_station_style": (SUN_STATION_STYLES, SUN_STATION_STYLE_DEFAULT),
}

SUN_STATION_OF_EVENT = {
    "Winter Solstice": "birth",
    "Spring Equinox": "youth",
    "Summer Solstice": "zenith",
    "Autumn Equinox": "age",
    "December Solstice": "birth",
    "March Equinox": "youth",
    "June Solstice": "zenith",
    "September Equinox": "age",
}

# THE UMBRA COLORING MENU (Watch Face Phase 4, R-22): "follow" reads
# `ring_tint` — today's behavior, unchanged — "custom" reads its own
# `umbra_tint` hue instead, through the SAME tritone recolor
# (`render.painting.tinted_gray`).
UMBRA_TINT_MODES = ("follow", "custom")

# THE AURA COLORLESS MENU (Watch Face Phase 4, R-23): active only while
# the "Colorful" Visible switch is off (`not settings.colorful`) — the
# Aura's day/twilight wedges then wear ONE of these instead of
# `palette.COLORFUL_OFF_COLOR`'s hardcoded white: "follow" tritones the
# ring tint toward white (`tinted_gray`'s own white end), "white"/"black"
# are flat, "custom" reads `aura_off_tint`.
AURA_OFF_TINT_MODES = ("follow", "white", "black", "custom")
