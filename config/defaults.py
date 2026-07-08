"""Developer tunables — values a developer may adjust while tuning the app.

Everything here is read-only at runtime. User-changeable state (window
position, chosen city, chosen skin) lives in the user settings file owned
by app/settings_store.py.
"""

from config import paths
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

# --- Window ------------------------------------------------------------------
DEFAULT_DIAL_DIAMETER = 360          # logical px, before DPI scaling
MIN_DIAL_DIAMETER = 120
MAX_DIAL_DIAMETER = 1200
SIZE_PRESETS = (360, 540, 720)       # owner spec: three dial versions

# Dials at or above this diameter write the date on the Earth marker;
# the FULL weekday name needs more room and appears only from the largest
# preset (owner: at 540 the full name is too small — keep the short one).
# Below the full-name threshold the markers get hover tooltips instead.
FULL_TEXT_MIN_DIAMETER = 540
WEEKDAY_FULL_NAME_MIN_DIAMETER = 720
EARTH_DATE_TEXT_SIZE = 0.30          # fraction of the marker size

# White label text carries a black outline so it stays readable over
# bright bodies (owner spec — "WED" on Mercury washed out without it).
LABEL_FILL_RGBA = (255, 255, 255, 240)
LABEL_OUTLINE_RGBA = (0, 0, 0, 210)
LABEL_OUTLINE_WIDTH = 0.05           # fraction of the font pixel size

# Watchdog delay for undoing a spontaneous (OS-initiated) hide/minimize.
# NOTE, verified on Windows 11 24H2: Win+D does NOT hide or minimize this
# window (no Qt events arrive) — it raises the desktop layer above every
# window (even TOPMOST cannot pierce it), and the widget returns by itself
# the moment Show Desktop mode ends. The watchdog therefore only covers
# other shell actions that genuinely hide/minimize; true visibility DURING
# Show Desktop requires the WorkerW glue mode (optional, M4).
WATCHDOG_RESHOW_MS = 200

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

# Seconds hand: default ON for the owner's preview; becomes a settings
# toggle (default OFF per the original decision) with the M6 dialog.
SECONDS_HAND_ENABLED = True

# True click-through: the window takes NO mouse input (recovery via the
# tray only). Hover info survives through a cursor poller that shows the
# tooltips itself at this interval.
CLICK_THROUGH_HOVER_POLL_MS = 200

# Time Travel (scenario tester in the menu): the dial renders the entered
# moment/position for this long, then returns to the present by itself.
TIME_TRAVEL_DURATION_S = 60

# --- Settings persistence ----------------------------------------------------
SETTINGS_SCHEMA_VERSION = 1
SETTINGS_WRITE_DEBOUNCE_MS = 750     # collapse rapid moveEvent bursts while dragging

# --- Procedural FALLBACK geometry (fractions of the dial radius unless noted) --
# NOT legacy: these drive the painter-drawn ring/labels used whenever a
# skin ships no ring art (user drop-in skins, validate previews). The DOMY
# skin itself uses ring.png, so these do not affect it.
RING_TICK_WIDTH = 0.004
RING_TICK_REACH = 1.03               # tick end, fraction of the ring inner radius
RING_NUMERAL_SIZE = 0.085            # font pixel size
RING_LETTER_SIZE = 0.105
RING_TEXT_BOX = 0.16                 # square text-layout box
RING_MINUTE_SIZE = 0.05
RING_MINUTE_RADIUS = 0.92            # fraction of the ring inner radius
RING_NUMERAL_MIN_PX = 7              # legibility floors at tiny dial sizes
RING_LETTER_MIN_PX = 8
RING_MINUTE_MIN_PX = 6
BODY_LABEL_MIN_PX = 6
BODY_LABEL_SIZE = 0.34               # fraction of the body size
MARKER_BORDER_WIDTH = 0.05           # fraction of the marker size
MARKER_BORDER_RGBA = (255, 255, 255, 200)

# --- Moon/Earth rim transit (year marker, "both" mode) -------------------------
# The smaller Moon passes OVER the Earth at reduced opacity when they meet
# on the shared rim — like an eclipse (owner decision; both stay visible).
MOON_TRANSIT_OPACITY = 0.5

# --- Tray --------------------------------------------------------------------
TRAY_ICON_SIZE = 64                  # px of the procedurally drawn tray pixmap
TRAY_ICON_MARGIN = 0.08              # fraction of the icon size
TRAY_DISC_RGB = (18, 22, 34)
TRAY_MARK_RGB = (255, 211, 77)
TRAY_MARK_SIZE = 0.10                # fraction of the icon size

# --- Ring presets ----------------------------------------------------------------
# DOMY and MORPH are RING PRESET names — nothing more (owner decision):
# a ring face plus its Greek-ordinal letter positions. The owner may add
# more rings (drop the art into assets/ring/ and add an entry here).
RING_PRESETS = {
    "domy": {
        "asset": paths.assets_dir() / "ring" / "domy.png",
        "letters": {12: "M", 20: "Y", 0: "Ω", 4: "D"},
    },
    "morph": {
        "asset": paths.assets_dir() / "ring" / "morph.png",
        "letters": {12: "M", 16: "Π", 8: "H", 0: "Ω"},
    },
}

# --- Default render config --------------------------------------------------------
# The ONE typed SkinDefinition the compositor consumes; the controller
# overlays the ring preset and the user's display choices onto it.

_CONTINENTS = ("europe", "north_america", "south_america", "africa", "asia", "oceania")

# Star + Aura palettes, (pointer, style) -> hues clockwise from the top
# arm. Measured directly from the owner's reference art
# (design/background/{hexa,octa}_{paint,light}.png): paint = subtractive
# primaries (yellow at the top), light = additive primaries (green at
# the top — owner: that IS the point of the two styles). The cross has
# ONE seasons palette (owner's own values: summer yellow top, autumn red
# right, winter blue bottom, spring green left — solstices/equinoxes at
# the arm centers), served under both styles.
_CROSS_SEASONS = ("#D9D900", "#D40F0F", "#0A70D8", "#10CE10")
PALETTE_PRESETS = {
    ("hexa", "paint"): (
        "#FFEE00", "#FFAA00", "#FF0000", "#8E55B9", "#0073E6", "#00B500",
    ),
    ("hexa", "light"): (
        "#00DC00", "#DCDC00", "#DC0000", "#DC00DC", "#0000DC", "#00DCDC",
    ),
    ("octa", "paint"): (
        "#DCDC00", "#DC9600", "#DC3C00", "#DC0000",
        "#783CF0", "#005ADC", "#00DCDC", "#00DC00",
    ),
    ("octa", "light"): (
        "#00DC00", "#DCDC00", "#DC7800", "#DC0000",
        "#DC00DC", "#0000DC", "#0078DC", "#00DCDC",
    ),
    ("cross", "paint"): _CROSS_SEASONS,
    ("cross", "light"): _CROSS_SEASONS,
}

# Octa bottom-arm text (time/date/...): sized to span this fraction of
# the slot width (owner: big font, must not overflow the slot).
TIME_TEXT_WIDTH_FRACTION = 0.95

# Umbra contrast spans, (lightest, darkest). Owner spec:
#   full — the whole gray range: sectioned ladders run endpoint-
#   inclusive (16 shades -> 255..0 step 17, matching his art);
#   half — the MIDDLE HALF of the scale [64, 192]: sectioned ladders
#   take the centers of N equal bins (16 -> 188..68 step 8, symmetric
#   about 128 — every value + its mirror = 256).
# The gradient form sweeps the same spans continuously.
UMBRA_CONTRAST_SPANS = {
    "full": (255, 0),
    "half": (192, 64),
}

# --- Season/moon event glow rendering (windows live in constants) ---------------
# Owner spec: pure WHITE, compact and intense — the halo diameter is
# twice the marker's, i.e. halo radius = 2x marker radius.
GLOW_COLOR = "#FFFFFF"
GLOW_CORE_ALPHA = 1.0
GLOW_MID_ALPHA = 0.7
GLOW_MID_STOP = 0.55                 # gradient position of the mid alpha
GLOW_RADIUS_SCALE = 2.0              # halo radius, multiple of the marker radius

# --- Shared app content (NOT skin-specific — a skin is a dial design) -----------
# Skeleton folders with 1x1 placeholders ship in the repo; the owner
# pastes his vector renders OVER them (same names). A missing file
# still falls back to the text form (documented).
ZODIAC_ART_DIR = paths.assets_dir() / "zodiac"
WEEKDAY_ART_DIR = paths.assets_dir() / "weekday"

# --- Weekday body themes (SYMBOLISM.md canon) -----------------------------------
# Display names per theme, body -> name (the weekday hover reads
# "Wednesday, Odin" in the norse theme). "planets" keeps the skin's own
# unit untouched. Saturday has no Norse god — the Sabbath stands in
# (canon). Art: assets/weekday/<theme>/<Entity>.png (files carry the
# ENTITY names; the two Norse diacritics fold to ASCII on disk).
WEEKDAY_THEME_NAMES = {
    "greek": {
        "sun": "Helios",
        "moon": "Selene",
        "mars": "Ares",
        "mercury": "Hermes",
        "jupiter": "Zeus",
        "venus": "Aphrodite",
        "saturn": "Cronus",
    },
    "norse": {
        "sun": "Sól",
        "moon": "Máni",
        "mars": "Tyr",
        "mercury": "Odin",
        "jupiter": "Thor",
        "venus": "Freya",
        "saturn": "Sabbath",
    },
    "religion": {
        "sun": "Christianity",
        "moon": "Buddhism",
        "mars": "Zoroastrianism",
        "mercury": "Taoism",
        "jupiter": "Hinduism",
        "venus": "Islam",
        "saturn": "Judaism",
    },
    "profession": {
        "sun": "Ruler",
        "moon": "Physician",
        "mars": "Soldier",
        "mercury": "Merchant",
        "jupiter": "Priest",
        "venus": "Artist",
        "saturn": "Farmer",
    },
}

# File stems on disk: the display names folded to ASCII (Sól -> Sol).
_ASCII_FOLD = str.maketrans("óá", "oa")
WEEKDAY_THEME_FILES = {
    theme: {body: name.translate(_ASCII_FOLD) for body, name in names.items()}
    for theme, names in WEEKDAY_THEME_NAMES.items()
}

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
        day_alpha=0.55,
        twilight_alpha=0.28,
        # TWO independent radii for fine tuning (fractions of the dial
        # radius; the ring art's inner edge sits at 0.858):
        umbra_radius_fraction=0.90,     # the gray wheel
        aura_radius_fraction=0.90,      # the colored wedges
    ),
    star=StarSpec(
        day_alpha=0.92,                 # near-full opacity where the sun is up
        twilight_alpha=0.55,
        border_alpha=0.85,              # colored outlines run the full circle
        border_width_fraction=0.008,
        radius_fraction=0.86,           # star tips touch the ring's inner edge too
    ),
    ring=RingSpec(
        # The DOMY preset by default; the controller swaps in the chosen
        # ring preset (asset + letter positions) at build time.
        asset=RING_PRESETS["domy"]["asset"],
        fill="#4A4E57",
        text_color="#F0F0F0",
        letter_color="#E8B84B",
        width_fraction=0.16,
        letters=RING_PRESETS["domy"]["letters"],
    ),
    weekday_set=WeekdaySpec(
        bodies={name: WEEKDAY_ART_DIR / "planets" / f"{name}.png" for name in (
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
        body_colors={
            "sun": "#FFC838",
            "jupiter": "#E8C25A",
            "mars": "#C96A3D",
            "venus": "#E1934B",
            "mercury": "#9B8F86",
            "moon": "#C9CDD4",
            "saturn": "#D4B27A",
        },
        display_mode="ghost",           # owner default; "center_only" selectable
        ghost_opacity=0.15,
        center_scale=0.132,             # owner spec: Sun is 1.20x the others
        diamond_scale=0.11,
        orbit_fraction=0.38,
    ),
    year_marker=YearMarkerSpec(
        mode="both",                    # owner preview default; selectable in M6 settings
        # Both styles bundled; the earth_style display choice picks one.
        variants={
            f"{style}_{continent}_{phase}": paths.assets_dir() / "earth"
            / f"earth_{style}_{continent}_{phase}.png"
            for style in ("clean", "atmo")
            for continent in _CONTINENTS
            for phase in ("day", "night")
        },
        default_variant="europe",
        day_color="#4B86C9",
        night_color="#20344F",
        # Owner spec: the Earth's outer edge TOUCHES the ring's inner
        # edge (0.75 + 0.11 = 0.86 = the disc radius), same size as the
        # weekday planets.
        orbit_fraction=0.75,
        scale=0.11,
        moon_asset=WEEKDAY_ART_DIR / "planets" / "moon.png",
        moon_lit_color="#E8E4D8",
        moon_dark_color="#2A2D36",
        moon_shadow_alpha=0.82,
        moon_orbit_fraction=0.75,       # rides the same rim as the Earth
        moon_scale=0.08,                # ~72% of the Earth marker (owner spec)
    ),
    hands=HandsSpec(
        # Owner's vector hands at HIS exact canvas sizes (240/290/300; a
        # faint reference circle keeps the export from trimming them).
        # ONE shared scale preserves the designed proportions; every
        # rotation center is 15 design units above its canvas bottom.
        hour=HandSpec(asset=paths.assets_dir() / "hands" / "hour.svg", design_height=240),
        minute=HandSpec(
            asset=paths.assets_dir() / "hands" / "minute.svg", design_height=290
        ),
        second=HandSpec(
            asset=paths.assets_dir() / "hands" / "second.svg", design_height=300
        ),
        # The longest hand's (seconds) tip reach, fraction of the dial
        # radius — aimed at the end of the 360-dot scale lines.
        reach_fraction=0.88,
    ),
)
