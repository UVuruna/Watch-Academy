"""THE COLOUR LAW — every colour in DOMY Watch, and nothing else.

**One file, one rule: a colour value exists in exactly one place, here.**
No hex literal, no RGBA tuple and no colour table lives anywhere else in
the program — `tests/test_palette_law.py` fails the build if one appears.
Before this file (owner verdict 2026-07-29) the hues were strewn across
3,500 lines of `config/defaults.py` between window sizes and timer
intervals: the PRISM pointer kept its primary and secondary wheels at
line 961 and its THIRD wheel — the Council — 36 lines further down,
inside another pointer's block. Looking a colour up meant grepping.

**The order is the law, and it is fixed.** New colours join the section
they belong to; nothing is ever appended to the end of the file.

  1. THE NAMED HUES — hues the canon names, referenced by the rest
  2. THE POINTER WHEELS — one block per pointer, ALL its wheels
     together (primary, secondary, tertiary), pointers in dial order;
     `PALETTE_PRESETS` then assembles the named wheels and holds no
     literal of its own
  3. THE RING — the ring-tint groups
  4. THE DIAL — labels, markers, the calendar pointer, glows, eclipses,
     the instrument's own bands
  5. THE SUBDIAL AND THE SLOTS
  6. THE DEFAULT SKIN's own hues
  7. THE TRAY AND THE FAST-TRAVEL FLASH
  8. THE UI CHROME — dialog theme, buttons, legend, encyclopedia
  9. THE CHARTS — the Report and the Observatory

Two things deliberately stay in [Defaults](defaults.md), because they
are NOT colours: the numeric shaping of a recolor (`SUBDIAL_RECOLOR_
VALUE_RAMP` and its neighbours — ramps, cutoffs, gains) and every width,
alpha fraction and radius that merely happens to sit beside a hue.

Layer: config (pure — no Qt, no wall clock). Documentation: palette.md.
"""

from config import constants


# ==================================================================
# 1. THE NAMED HUES
# ==================================================================
# Hues the canon names in its own words; every wheel below
# that wants one references it rather than repeating a value.

# THE CUBE WHEELS (owner seal 2026-07-26, CUBE.md). The moon-gray
# violet is the Purple-Gray hue law's ONE purple (~#666699 — the Moon,
# midnight, the Winter Solstice; NEVER royal purple).
MOON_GRAY_VIOLET = "#666699"

# THE MOON'S OWN FACE (Session 35, owner: "boja Silver kao moon" — the
# nine-whole Encyclopedia's ninth accent wears the Moon's own hue, not a
# hand-picked silver). Promoted from the dial's Moon body
# (`SKIN_PLANET_BODY_COLORS["moon"]`, §6, which now references it) so a
# retune of the Moon's own colour moves both readers together (Rule #5,
# one value).
MOON_SILVER = "#C9CDD4"


# ════════════════════════════════════════════════════════════════════
# 2. THE POINTER WHEELS
# ════════════════════════════════════════════════════════════════════
# THE LAW OF THIS SECTION: one block per pointer, and a pointer's
# wheels NEVER separate — primary, then secondary, then tertiary, in
# that order, every time. `PALETTE_PRESETS` at the end of the section
# only NAMES them; it carries no colour of its own, so a wheel can be
# read, reviewed and re-tuned in one place.
#
# A wheel's tuple runs CLOCKWISE from the 12h arm, matching the drawn
# pointer (the dial convention: degrees clockwise from the top).

# --- hexa — THE PRISM, six arms, three wheels -----------------------
# PRIMARY: the hexa primary hues — the dial's own six.
HEXA_PRIMARY = (
    "#F8E600", "#DC9600", "#B60000",
    "#542E85", "#002FFF", "#007E00",
)
# SECONDARY: the light-primaries wheel, green at the top.
HEXA_SECONDARY = (
    "#00DC00", "#FFFF00", "#FF0000",
    "#BD00BD", "#0040FF", "#00DDDD",
)
# TERTIARY — THE COUNCIL (owner seal 2026-07-26, CUBE.md): all six
# Double-Trinity offices at once — the hexa primary wheel with the 24h
# arm re-dressed per the Purple-Gray hue law (the Creator's arm is the
# Rose's violet, never royal).
COUNCIL = (
    "#F8E600", "#DC9600", "#B60000",
    MOON_GRAY_VIOLET, "#002FFF", "#007E00",
)

# --- trio — THE TRINITY, three arms, three wheels -------------------
# PRIMARY: the theological trio (owner spec, FINAL.txt #7) — Faith
# yellow at 12h, Love red at 20h, Hope blue at 4h, the hexa primary
# hues at the M, Y, D ring-letter positions.
TRINITY = ("#F8E600", "#B60000", "#002FFF")
# SECONDARY: the FAMILY triangle (CANON, placement APPROVED
# 2026-07-16) — the same derivation from the hexa SECONDARY primaries
# at 12/20/4, green at the top (the Child), the parents' hues LIGHTENED
# per the owner's member table ("light blue" the Father, "light red"
# the Mother; hue tuning licensed to the agent, 2026-07-16).
FAMILY = ("#00DC00", "#FF8080", "#7FB2FF")
# TERTIARY — GENESIS (owner seal 2026-07-26, CUBE.md): the creation
# trio on the INVERTED triangle, tuple order following the drawn arms
# (offset 180°) — 24h Creator in the moon-gray violet, 08h Preserver in
# the dial's green, 16h Destroyer in the dial's orange.
GENESIS = (MOON_GRAY_VIOLET, "#007E00", "#DC9600")

# --- cross — THE QUATERNITY, four arms, three wheels ----------------
# The four arms are read three ways, and each reading owns its own hues
# instead of borrowing (owner seal 2026-07-28). Every wheel keeps the
# SAME arm order — summer/fire/choleric top, autumn/earth/melancholic
# right, winter/water/phlegmatic bottom, spring/air/sanguine left — so
# a figure never moves seat when the reader turns the wheel.
#
# PRIMARY — TEMPERAMENTS: the humours name their own colours inside
# their own words, the most literal fidelity available: sanguis = blood
# = red; cholē = yellow bile; melan-cholē = BLACK bile; phlegm = the
# pale humour. Yellow, black, white and red are also Apelles'
# four-colour palette as Pliny records it (NH 35.50).
#   * summer arm (top)    = CHOLERIC    — saffron amber, bile's own
#     gold rather than the season's lemon (hot & dry);
#   * autumn arm (right)  = MELANCHOLIC — burnt umber, for *atra bilis
#     adusta* is an adust, earthy black, never printer's black (a pure
#     black arm is a hole in a transparent widget) (cold & dry);
#   * winter arm (bottom) = PHLEGMATIC  — white with a cold blue-grey
#     cast, the pale moist humour (cold & moist);
#   * spring arm (left)   = SANGUINE    — a true blood crimson, deeper
#     and bluer than autumn's leaf-red (warm & moist).
# The diagonals stay opposed in BOTH qualities, as CANON requires: gold
# against pale, blood against burnt black.
TEMPERAMENTS = ("#E5A81F", "#3B2C28", "#D9E5EC", "#B21E30")
# SECONDARY — ELEMENTS (owner 2026-07-17, CANON §the elements wheel):
# the classical assignment, seating the Tetramorph (Lion/Ox/Eagle/Man).
#   * summer arm (top)    = FIRE  — a hot flame red-orange, hotter than
#     autumn's leaf red so no two wheels of the three read alike;
#   * autumn arm (right)  = EARTH — an olive green-brown, the soil (a
#     muddy green, distinct from spring's pure green on the Seasons);
#   * winter arm (bottom) = WATER — a deep water blue;
#   * spring arm (left)   = AIR   — a pale white-yellow, the luminous
#     lightest of the four (owner: "air spring-arm white-yellow").
# The classical Western element colours (fire red, air yellow/white,
# water blue, earth green) laid on the seasons the fixed-cross zodiac
# already ties them to (Leo/Taurus/Scorpio/Aquarius).
ELEMENTS = ("#E8391E", "#6B8E3A", "#1E74D0", "#EFE9B0")
# TERTIARY — SEASONS: the owner's own sampled values, unchanged. They
# were always a season palette; until the 2026-07-28 seal they merely
# sat under the Temperaments' label (summer yellow top, autumn red
# right, winter blue bottom, spring green left — solstices and
# equinoxes at the arm centres).
SEASONS = ("#D9D900", "#D4330F", "#0A70D8", "#129412")

# --- octa — THE COMPASS, eight arms, three wheels -------------------
# The two octa presets used to be one wheel with nuance shifts; each
# palette now ties to its archetype's substance (owner rework
# 2026-07-16).
#
# PRIMARY — PAINT: the Walks' materials (King gold, Merchant copper,
# Soldier iron-blood, Artist velvet, Wanderer road-dust, Scholar lamp
# ink, Farmer field green, Priest alb ivory).
COMPASS_PAINT = (
    "#F0C420", "#C87533", "#A02020", "#7A2E8E",
    "#262636", "#1F5FA8", "#3E8914", "#EDEDE0",
)
# SECONDARY — LIGHT: the Wheel of a Life, the Eight Ages (owner shift
# 2026-07-16: Death at midnight wears pure WHITE — in the light
# register death goes INTO the light; the moonlight silver moved to the
# Unborn at 03h, the predawn mist to Birth at 06h; the dawn rose
# retired). Both keep the day-arc.
COMPASS_LIGHT = (
    "#FFE800", "#FFB400", "#FF6A3C", "#9C6BD4",
    "#FFFFFF", "#C8D7F0", "#8FA8C8", "#7CE577",
)
# TERTIARY — the CHARACTER wheel, which is ROSE_PALETTE below (Rule #5,
# one source, three readers).

# --- rose — THE ROSE, two wheels, one palette -----------------------

# CHARACTER / THE ROSE (octa tertiary) — the palette EXACTLY as the Rose is
# drawn (owner seal: "kept for the beauty of the arrangement"; values
# sampled from UV/simbolika/slike/24 ROSE (3 x octa).png): the four
# poles wear yellow / red / moon-purple / BLUE (the Scale's own Judas-
# Lucifer axis), the four blends follow nature — green of blue+yellow,
# orange of yellow+red, pink and cyan are red and blue thinned by the
# neighboring pole's moonlight. Clockwise from the 12h arm. This ONE
# tuple rules BOTH the Character wheel and the ROSE POINTER's three
# stars (CUBE.md §The Rose — Rule #5, one source). Clockwise from 12h
# it is also the year: cardinals = the turning points (summer solstice
# yellow, autumn equinox red, winter solstice purple, spring equinox
# blue), diagonals = the season centres (orange, rose, cyan, green) —
# exactly where `core.year_wheel` puts them.
ROSE_PALETTE = (
    "#FCEE21", "#F7931E", "#F03232", "#FF7BAC",
    MOON_GRAY_VIOLET, "#29ABE2", "#0078DC", "#39B54A",
)

# THE LEAD LINE — the dark outline of the owner's own drawing, worn by
# EVERY drawn arm and polygon face (owner's correction round
# 2026-07-29: the Rose's lead was "the good example", so it becomes the
# law of the whole pointer family). It separates the trio's cube faces,
# the cross/hexa/octa arms, the Calendar's two hexagrams and its
# twelve-point star, and the Rose's three overlapping stars alike — in
# the star and polygon shapes both, and on the INTERNAL colour
# boundaries too, since every arm/face is stroked as its own path. The
# armless Aurora is the one exception: it has no arms to outline, only
# day bands.
ARM_OUTLINE = "#1A1A1A"

# Both ROSE wheels wear the SAME eight hues (owner seal 2026-07-27,
# CUBE.md §The Rose): Legacy and Prophecy turn the star GEOMETRY and
# the figure sets, never the colours — the Seasons pointer already
# serves one palette under both styles.

# --- aurora — the day arc, two wheels -------------------------------
# AURORA (owner spec 2026-07-12): [dawn, five day hues, dusk] — paint =
# azure/green/yellow/orange/red, light = azure/cyan/green/yellow/red;
# twilight left (dawn) blue, right (dusk) brown.
AURORA_PAINT = (
    "#002FFF", "#0080FF", "#007E00", "#F8E600", "#DC9600",
    "#BC0000", "#5D1212",
)
AURORA_LIGHT = (
    "#0040FF", "#0080FF", "#00DCDC", "#00DC00", "#FFFF00",
    "#FF2828", "#720017",
)

# --- calendar — the Dozen, two wheels -------------------------------
# CALENDAR (owner 2026-07-16, CANON §The Dozen). TWELVE hues, clockwise
# from the TOP wedge — the tuple convention differs between the two
# wheels, which is why each says its own starting wedge.
#
# PAINT — the ZODIAC Dozen (boundaries ON the cardinal axes; the RGB
# circle rotated 15° so no pure primary shows): the FIRST hue fills the
# wedge that STARTS at the top (12h line), i.e. Cancer, then Leo,
# Virgo … clockwise.
CALENDAR_ZODIAC = (
    "#40FF00", "#BFFF00", "#FFBF00", "#FF4000", "#FF0040", "#FF00C0",
    "#BF00FF", "#4000FF", "#0040FF", "#00BFFF", "#00FFBF", "#00FF40",
)
# LIGHT — the ALMANAC (Month) Dozen (wedges CENTERED on the axes; pure
# primaries allowed): the FIRST hue fills the wedge CENTERED on the
# top, i.e. June, then July, August … clockwise.
CALENDAR_ALMANAC = (
    "#00FF00", "#80FF00", "#FFFF00", "#FFBF00", "#FF0000", "#FF0080",
    "#FF00FF", "#8000FF", "#0000FF", "#0080FF", "#00FFFF", "#00FF80",
)

# --- the assembly ---------------------------------------------------
# Pointer by pointer, wheel by wheel — NAMES only. A new pointer adds
# its own block above and its own contiguous run here; nothing is ever
# appended out of order.
PALETTE_PRESETS = {
    ("hexa", "primary"): HEXA_PRIMARY,
    ("hexa", "secondary"): HEXA_SECONDARY,
    ("hexa", "tertiary"): COUNCIL,

    ("trio", "primary"): TRINITY,
    ("trio", "secondary"): FAMILY,
    ("trio", "tertiary"): GENESIS,

    ("cross", "primary"): TEMPERAMENTS,
    ("cross", "secondary"): ELEMENTS,
    ("cross", "tertiary"): SEASONS,

    ("octa", "primary"): COMPASS_PAINT,
    ("octa", "secondary"): COMPASS_LIGHT,
    ("octa", "tertiary"): ROSE_PALETTE,

    ("rose", "primary"): ROSE_PALETTE,
    ("rose", "secondary"): ROSE_PALETTE,

    ("aurora", "primary"): AURORA_PAINT,
    ("aurora", "secondary"): AURORA_LIGHT,

    ("calendar", "primary"): CALENDAR_ZODIAC,
    ("calendar", "secondary"): CALENDAR_ALMANAC,
}


def effective_palette_style(pointer: str, palette_style: str) -> str:
    """The wheel slot AS RENDERED for this pointer: "tertiary" holds
    only where the pointer actually serves a third wheel
    (`constants.palette_styles_for`); everywhere else — a stored
    "tertiary" left behind by a pointer switch — it normalizes to
    "primary". The ONE normalization point (Rule #5): `app.controller.
    apply_display_settings`, the settings dialog's palette group and
    `watch_title` all read the style through here, so no consumer ever
    indexes PALETTE_PRESETS with a pair that does not exist."""
    if palette_style in constants.palette_styles_for(pointer):
        return palette_style
    return "primary"

def pointer_arm_labels(pointer: str, palette_style: str) -> tuple:
    """The palette-editor arm labels for the ACTIVE wheel — the
    Genesis wheel (trio + tertiary) speaks its inverted seats
    ("trio_tertiary"), every other wheel its pointer's own row."""
    if (pointer, palette_style) == ("trio", "tertiary"):
        return constants.POINTER_ARM_LABELS["trio_tertiary"]
    return constants.POINTER_ARM_LABELS[pointer]

# Elements switch "Colorful" OFF (owner spec, FINAL.txt #5): the day and
# twilight arcs are still indicated, but as plain white transparency
# instead of the pointer-palette hues.
COLORFUL_OFF_COLOR = "#FFFFFF"


# ==================================================================
# 3. THE RING
# ==================================================================

# --- Ring tint (owner spec, FINAL.txt #6) ------------------------------------------
# One hue recolors the WHOLE clock body: the ring art, the hands and
# the Umbra are channel-multiplied by it (gray stays gray under None).
# The letters are separate art and are never tinted. Preset hues below
# are STARTING VALUES — the owner tunes them here. Settings shows them
# as a grid of color circles (Paint style — owner spec 2026-07-11);
# the name appears in the circle's hover tooltip.
# The swatches split into TWO groupings (owner 2026-07-15: "podeli na
# svetlije i tamnije" — the whole palette read too light), each its own
# labeled grid. The Darker group grew a fashion row (owner: subtle,
# understated, "gospodske" hues — navy/teget, petrol, graphite and the
# silver-leaning darks).
RING_TINT_GROUPS = {
    "Lighter": {
        "Gray": None,                   # the untouched owner art
        # The owner's gold palette (his reference swatches, 2026-07-11).
        "Naples Yellow": "#FFE169",
        "Sunglow": "#FFD235",
        "Mikado Yellow": "#FFC300",
        "Gold": "#D4AF37",
        "Satin Gold": "#C9980B",
        "Copper": "#B87333",
        "Silver": "#C9CDD3",
        "Lavender Gray": "#A7A6BA",
        "Periwinkle": "#9090C0",
        "Cadet Gray": "#91A3B0",
        "Stone": "#928E85",
        "Aluminium": "#888B8D",
        "Roman Silver": "#808992",
        "Glaucous": "#6082B6",
        "Slate Gray": "#708090",
        "Smoke": "#738276",
        "Steel": "#71797E",
    },
    "Darker": {
        # Pipetted from the owner's Clock_OuterColors.png (21 ring
        # variants, 3x7 grid, mode color per hour band — 2026-07-11).
        "Nevada": "#6C7174",
        "Dim Gray": "#6B6B6B",
        "Granite": "#625D5D",
        "Pewter": "#565B5F",
        "Ebony": "#545851",
        "Anthracite": "#494F55",
        "Iron": "#4C4E52",
        "Graphite": "#3B3F44",
        "Gunmetal": "#2A3439",
        "Charcoal": "#36454F",
        "Black Coral": "#54626F",
        # The fashion darks (owner 2026-07-15): muted wardrobe hues.
        "Ocean": "#4E7A9E",
        "Petrol": "#2F4550",
        "Navy": "#1B2A41",
        "Oxford Blue": "#14213D",
        "Sage Steel": "#5E716A",
        "Dark Olive": "#3C3F33",
        "Deep Pine": "#253529",
        "Smoky Plum": "#66606D",
        "Aubergine": "#3D3242",
        "Bordeaux": "#4E3238",
        "Purple": "#8E55B9",
        "Golden Brown": "#926C15",
        "Espresso": "#342523",
    },
}


# ==================================================================
# 4. THE DIAL
# ==================================================================

# White label text carries a black outline so it stays readable over
# bright bodies (owner spec — "WED" on Mercury washed out without it).
LABEL_FILL_RGBA = (255, 255, 255, 240)

LABEL_OUTLINE_RGBA = (0, 0, 0, 210)

MARKER_BORDER_RGBA = (255, 255, 255, 200)

CALENDAR_ARROW_COLOR = "#FFD235"     # gold, matching the ring letters/ticks

CALENDAR_ICON_WEDGE_COLORS = ("#A67C00", "#FFBF00")

CALENDAR_ICON_RING_COLOR = "#1A1A1A"

# Bronze ring LETTERS are derived AT LOAD from the gold master (owner
# 2026-07-19, `render.asset_recolor.letter_metal_file` — retired the
# pre-rendered files); BRONZE_LETTER_TINT anchors the "bronze" shade's
# hue/saturation above and still supplies the eclipse glow color below —
# it is a COLOR CONSTANT, not a recipe (the recipe itself is METAL_SHADES).
BRONZE_LETTER_TINT = "#CD7F32"

# The shadow STAMP's tint: a pixmap re-rendered pure black and offset
# under the real art (ring letters, weekday bodies). Black is not a
# design choice here but the definition of a cast shadow — it is named
# so the shadow pass owns no literal of its own.
SHADOW_STAMP_TINT = "#000000"

GLOW_SUN_COLOR = "#FFCC33"           # golden — distinct from the yellow arms

GLOW_MOON_COLOR = "#E8EBEE"          # silver — bright, reads on the dark ring

# ECLIPSE DISPLAY (owner 2026-07-18, ROADMAP 15h item 11 — refines the
# sealed glow-metal triad; the Deep Time pack's eclipse catalog is the
# OPTIONAL data source, see data/deep_time.md — absent it, none of this
# ever draws). A SOLAR eclipse turns the Earth marker's OWN event glow
# RED (instead of GLOW_SUN_COLOR) and swaps its art to the Planets
# theme's Eclipsed-Sun dual; a LUNAR eclipse turns the Moon marker's
# glow the blood-moon COPPER (the bronze metal tint, reused verbatim —
# physically true, not a new color) and darkens the disc with the same
# tint. Both ride the EXISTING relocation-to-ring-band mechanic
# (GLOW_RING_RADIUS_FRACTION) — only the color/art/strength differ.
GLOW_ECLIPSE_SOLAR_COLOR = "#FF3B30"       # red — the eclipsed Sun's glow

# The "ring of fire" (owner decree 2026-07-19, fix round C): an ANNULAR
# solar eclipse keeps the black-sun art but its glow shifts to a hotter
# orange-red than the plain total/partial red, so the two read distinct.
GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR = "#FF7A1A"

GLOW_ECLIPSE_LUNAR_COLOR = BRONZE_LETTER_TINT  # bronze copper — blood moon

# INVISIBLE-FROM-HERE muting (owner verdict "može", fix round E,
# 2026-07-19): an eclipse the observer cannot actually see (below the
# horizon, or — solar only — too far from the ground track) still
# shows — the event is real — but its glow swaps to a desaturated
# silver at HALF strength instead of its normal color, and the hover
# names the reason. The art swap/moon-darkening stay untouched (the
# type-driven state is a catalog fact, not an observer fact).
GLOW_ECLIPSE_INVISIBLE_COLOR = "#8A9096"       # desaturated silver-gray

# LUNAR ECLIPSE OPTION C (owner sealed 2026-07-18): the blackened moon +
# bronze glow gains a thin TURQUOISE FRINGE at the glow's OUTER edge —
# the real ozone-band color at the umbra's rim during totality. A
# turquoise ring, not a flat teal, so it reads distinctly against the
# warm bronze on the dark dial.
ECLIPSE_LUNAR_FRINGE_COLOR = "#40E0D0"

# BLOOD MOON DISC (owner verdict "može", fix round E, 2026-07-19): the
# TOTAL state's multiply-darken uses this deep copper-red instead of
# neutral gray — `render.painting.tinted_gray`'s black->tint->white
# tritone at `ECLIPSE_STATE_MOON_BRIGHTNESS["lunar_total"]` (~7%) reads
# dark AND visibly red, the real "blood moon" look; partial/penumbral
# keep the plain neutral gray (only totality dims the WHOLE face enough
# for a color cast to read honestly).
ECLIPSE_TOTAL_MOON_TINT = "#8B2E12"

INSTRUMENT_TWILIGHT_COLORS = {
    "day": "#7FA8D9",
    "civil": "#4A6FA5",
    "nautical": "#2C4570",
    "astronomical": "#1A2440",
    "night": "#0C0F1A",
    "sun": "#F2C14E",
}

INSTRUMENT_MOON_COLORS = {"lit": "#EFEAD8", "dark": "#2A2E38"}

# The year wheel's quarters read the POINTER palette's own season hues
# (`("cross", "tertiary")`, summer/autumn/winter/spring clockwise from
# the top) — one palette, so a re-tuned season colour moves the diagram
# with the dial.
INSTRUMENT_SEASON_COLORS = dict(zip(
    ("summer", "autumn", "winter", "spring"),
    PALETTE_PRESETS[("cross", "tertiary")],
))


# ==================================================================
# 5. THE SUBDIAL AND THE SLOTS
# ==================================================================

SLOT_ROUNDEL_FILL_FALLBACK = "#39434D"   # unreadable/missing ring art

SLOT_ROUNDEL_BORDER_COLORS = {
    "gold": "#FFD235",
    "silver": "#C9CDD3",
    "bronze": "#CD7F32",
}

SMALL_SECONDS_TICK_RGBA = (255, 255, 255, 235)

SMALL_SECONDS_TICK_SHADOW_RGBA = (0, 0, 0, 140)

# Complication TEXTS on the subdials (owner 2026-07-15): always the
# letter-finish metal color — never white — over a drop shadow so they
# read on both plate styles.
SUBDIAL_TEXT_SHADOW_RGBA = (0, 0, 0, 180)

# The subdial's live SHADOW (owner 2026-07-15: the sun lives at the
# dial center, the shadow is RENDERED, never baked) — offset outward
# from the center, none on the center seat.
SUBDIAL_SHADOW_RGBA = (0, 0, 0, 100)

# SILVER has no entry here on purpose (2026-07-20 rework): it is the
# achromatic VALUE alone, the exact letter-metal "straight desaturation"
# recipe (`letter_metal_file`) — never a stored target color like gold/
# bronze, so it can never drift toward a hue by accident.
SUBDIAL_RECOLOR_COLORS = {
    "gold": "#FFD235",
    "bronze": "#CD7F32",
}

# ════════════════════════════════════════════════════════════════════
# 6. THE DEFAULT SKIN's OWN HUES
# ════════════════════════════════════════════════════════════════════
# `defaults.DEFAULT_SKIN` is a SKIN, not a palette — it stays where it
# is and reads its colours from here, so the ring's slate and the seven
# planet bodies are tunable in the one place colours live.

# The procedural ring face (a placeholder only — `build_skin` always
# overlays the chosen ring preset card from Database/ring_presets.json).
SKIN_RING_FILL = "#4A4E57"
SKIN_RING_TEXT = "#F0F0F0"
SKIN_RING_LETTER = "#E8B84B"
# The seven weekday planet bodies, each a photographic body's own cast.
SKIN_PLANET_BODY_COLORS = {
    "sun": "#FFC838",
    "jupiter": "#E8C25A",
    "mars": "#C96A3D",
    "venus": "#E1934B",
    "mercury": "#9B8F86",
    "moon": MOON_SILVER,
    "saturn": "#D4B27A",
}
# The Continents face: the lit hemisphere and the night one.
SKIN_EARTH_DAY = "#4B86C9"
SKIN_EARTH_NIGHT = "#20344F"
# The year-marker Moon: its lit limb and its shadowed one.
SKIN_MOON_LIT = "#E8E4D8"
SKIN_MOON_DARK = "#2A2D36"


# ==================================================================
# 7. THE TRAY AND THE FAST-TRAVEL FLASH
# ==================================================================

# TRAY ICON COLOR WHEEL (ADD WATCH round, owner INSTRUCTION.txt item 2B,
# sealed 2026-07-21): watch 1 keeps the gold master untouched, watch 2
# wears the pre-existing rose-gold master (LOGO_SETUP_ASSET, a second
# master — not a recolor); watch 3+ tint the GOLD master (the same
# tritone recipe `render.asset_recolor.tinted_pixmap` already uses for ring/
# hand recolors, Rule #5) cycling this wheel forever. The 12 hues are
# the CALENDAR pointer's own MONTH wheel (`UV/Color Wheels.png`,
# January..December) read starting at January — the owner's own worked
# example, PURPLE #8000FF (R:G:B 1:0:2) then BLUE #0000FF (R:G:B 0:0:1),
# identifies the wheel and the starting point at once (Rule #19 —
# computed from the one wheel already in the codebase, no new palette).
TRAY_COLOR_WHEEL = (
    "#8000FF", "#0000FF", "#0080FF", "#00FFFF", "#00FF80", "#00FF00",
    "#80FF00", "#FFFF00", "#FFBF00", "#FF0000", "#FF0080", "#FF00FF",
)

FAST_TRAVEL_FLASH_BG = "rgba(20, 20, 26, 220)"

FAST_TRAVEL_FLASH_TEXT_COLOR = "#F0F0F0"


# ==================================================================
# 8. THE UI CHROME
# ==================================================================

# Dialog theme (Rule #16 POLISH round, 2026-07-18): the dark-first
# palette for the Settings dialog's chrome (nav column, group-box
# cards, sliders/combos/spinboxes/checkboxes) and the other dialogs'
# base surface — see monorepo DESIGN.md. Anchored on the dial's own
# slate identity (`#2A3439` family) with the gold accent the owner's
# opacity-slider screenshot already wears; `app/theme.py` is the only
# consumer — every other file reaches colors through THEME_COLORS, no
# hex literals scattered in widget code (Rule #4).
THEME_COLORS = {
    "surface_0": "#1A1F22",     # dialog window background
    "surface_1": "#20272B",     # group-box cards
    "surface_2": "#2A3439",     # inputs, nav column (the dial's slate)
    "surface_3": "#333F45",     # hover / raised elevation
    "border": "rgba(255, 255, 255, 28)",
    "text_primary": "#F2F3F4",
    "text_secondary": "#A6B0B4",
    "accent": "#E8B23D",        # gold — the dial's own opacity-slider hue
}

UI_BUTTON_COLORS = {
    "home": ("#4FACFE", "#1565C0"),         # blue — the way back
    "previous": ("#FFB75E", "#E65100"),     # orange
    "next": ("#7EDB7B", "#2E7D32"),         # green
    "download": ("#CE93D8", "#6A1B9A"),     # violet — save the entry
    "neutral": ("#B0BEC5", "#546E7A"),      # the look arrows
}

LEGEND_BG = "#2B2B2B"

LEGEND_BORDER = "#6E6E6E"

LEGEND_TEXT = "#FFFFFF"

LEGEND_MORE_LINK_COLOR = "#8FB8FF"

LEGEND_MORE_HINT_COLOR = "#9A9A9A"

# THE FINISH SWITCHER (owner fix round R3: moved to the top row, in
# line with Home/Download; restyled from filled gradient pills to
# border-only frames in the finish's OWN color — Colored/Bronze/Gold/
# Silver read at a glance instead of hiding behind a generic caption).
# Bronze matches BRONZE_LETTER_TINT (below, out of definition order —
# copied as a literal rather than forward-referenced) so the switcher
# border and the ring-letter bronze read as the SAME bronze; gold/
# silver are the classic heraldic metals, unused as a plain hex
# anywhere else in the palette tables.
ENCYCLOPEDIA_FINISH_BORDER_COLORS = {
    "Bronze": "#CD7F32",         # == BRONZE_LETTER_TINT
    "Gold": "#D4AF37",
    "Silver": "#C0C0C0",
}

# The COLORED option's border (owner correction 2026-07-21: the full
# seven-stop spectrum "baš loše ispao" — a plain two-stop sweep reads
# cleaner): BLUE on the left flowing to RED on the right.
ENCYCLOPEDIA_FINISH_GRADIENT = ("#3B5FE0", "#D8362A")

# A target outside the bundled coverage is refused inline (owner
# 2026-07-16). The warning names the future Deep Time pack's reach; the
# actual coverage comes from the databases (SeasonsRepository/
# MoonPhaseRepository .coverage()), never hardcoded.
TIME_TRAVEL_WARNING_COLOR = "#C8553D"    # warm red-clay — reads on the dialog

# The LOOK chips in the settings dialog (`app.ui_style`) — the two
# finishes that are not a metal, so they cannot borrow their fill from
# ENCYCLOPEDIA_FINISH_BORDER_COLORS above. Atmosphere is a two-stop
# sweep (sky into low sun); Clean is a solid ocean teal by day and the
# SAME navy by night. The chip's TEXT colour is never named — it is
# computed from the fill's YIQ luminance, so a retune here can never
# make a chip illegible.
LOOK_FILL_ATMOSPHERE = ("#4FC3F7", "#FFB74D")
LOOK_FILL_ATMOSPHERE_NIGHT = ("#0B1F3A", "#3B5FE0")
LOOK_FILL_CLEAN = "#0E6B8C"
LOOK_FILL_CLEAN_NIGHT = "#0B1F3A"

# The hairline every gradient UI button wears, so its fill never bleeds
# into the surface behind it.
UI_BUTTON_EDGE_RGBA = "rgba(0, 0, 0, 130)"

# The ring-tint picker's two neutrals: the swatch the OS colour dialog
# opens on when no tint is chosen yet, and the chip that stands for
# "no tint" (the bare art gray) in the swatch row.
RING_TINT_PICKER_SEED = "#808080"
RING_TINT_NONE_SWATCH = "#9A9A9A"


# ==================================================================
# 9. THE CHARTS
# ==================================================================

REPORT_MARK_COLOR = "#C9980B"        # satin gold — the one series hue

REPORT_MARK_DIM_COLOR = "#6E5A18"    # unselected bars

REPORT_INK_COLOR = "#E8EAED"         # primary text on the chart

REPORT_MUTED_COLOR = "#9AA0A6"       # secondary text / axis

REPORT_SURFACE_COLOR = "#202124"     # chart surface

OBSERVATORY_SURFACE_COLOR = THEME_COLORS["surface_0"]      # chart body

OBSERVATORY_INK_COLOR = THEME_COLORS["text_primary"]       # labels

OBSERVATORY_MUTED_COLOR = THEME_COLORS["text_secondary"]   # axis / ticks

OBSERVATORY_GRID_COLOR = "#3A464C"                          # recessive grid

OBSERVATORY_CROSSHAIR_COLOR = "#E8B23D"                     # hover crosshair

# The four seasons' canonical cross-wheel hues (Spring=air, Summer=fire,
# Autumn=earth, Winter=water — the same ELEMENTS the Seasons
# pointer paints) plus the two half-years (gold light, slate dark).
OBSERVATORY_SERIES_COLORS = {
    "spring": ELEMENTS[3],       # air — pale white-yellow
    "summer": ELEMENTS[0],       # fire — red
    "autumn": ELEMENTS[1],       # earth — olive green-brown
    "winter": ELEMENTS[2],       # water — deep blue
    "light": "#E8B23D",                 # the light half-year — gold
    "dark": "#6E7B82",                  # the dark half-year — slate
}

# The eras painted on the light−dark chart: the Age of Light band gold,
# the Age of Darkness band slate (low alpha wash), the Anno Lucis /
# transition verticals in muted ink. (hex, alpha) — alpha applied live.
OBSERVATORY_ERA_LIGHT_BAND = ("#E8B23D", 26)

OBSERVATORY_ERA_DARK_BAND = ("#6E7B82", 30)

OBSERVATORY_ERA_MARK_COLOR = "#C9CDD3"

# The eclipse timeline: solar gold, lunar the blood-moon copper (the
# same BRONZE family the on-dial lunar eclipse wears — color fidelity).
OBSERVATORY_ECLIPSE_COLORS = {"solar": "#E8B23D", "lunar": "#B87333"}

OBSERVATORY_NOW_MARK_COLOR = "#E8391E"          # the traveled moment line

# The day-length curve at the current location: one gold line over the
# year; astral is asked once every N days (a smooth curve, cheap open).
# The step itself is set below (Fix round R1a, Item 5 — 1-day ticks).
OBSERVATORY_DAYLENGTH_COLOR = "#E8B23D"

# Task 4 — the fifth chart: the La2004 Laskar long envelope (amplitude
# only, charts-only doctrine — ROADMAP 15a2). Colors echo the research
# plot (research/ephemeris/long_envelope.py): gold amplitude band, muted
# silver signed oscillation, teal DE441-measured-window wash.
OBSERVATORY_LASKAR_ENVELOPE_COLOR = "#E8B23D"

OBSERVATORY_LASKAR_SIGNED_COLOR = "#C7CDD6"

OBSERVATORY_LASKAR_DE441_BAND = ("#4FB0C6", 30)

# Item 2 — the eclipse legend recolor (owner: "lakše razlikuje... mesec
# PLAVIM a Sunce ZUTIM"): solar kinds walk yellow->orange->red (mildest
# to most total), lunar kinds walk navy->blue->cyan (faintest penumbral
# to most total) — the ground-truthed type vocabulary is pinned by
# tests/test_eclipse.py::test_type_state_mapping_covers_the_ground_truthed_vocabulary.
OBSERVATORY_ECLIPSE_KIND_COLORS = {
    "solar": {
        "partial": "#F4D35E",
        "annular": "#F2994A",
        "hybrid": "#EB5E28",
        "total": "#D62828",
    },
    "lunar": {
        "penumbral": "#2E4A7A",
        "partial": "#2F6FED",
        "total": "#4FD5E8",
    },
}
