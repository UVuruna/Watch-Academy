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
    HexagramSpec,
    NoonMarkerSpec,
    RingSpec,
    SkinDefinition,
    WeekdaySpec,
    YearMarkerSpec,
)

# --- Window ------------------------------------------------------------------
DEFAULT_DIAL_DIAMETER = 360          # logical px, before DPI scaling
MIN_DIAL_DIAMETER = 120
MAX_DIAL_DIAMETER = 1200

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
TICK_EPSILON_MS = 50                 # fire just past the minute boundary
CLOCK_JUMP_THRESHOLD_S = 5           # actual vs expected tick time -> full refresh

# --- Settings persistence ----------------------------------------------------
SETTINGS_SCHEMA_VERSION = 1
SETTINGS_WRITE_DEBOUNCE_MS = 750     # collapse rapid moveEvent bursts while dragging

# --- Procedural render geometry (fractions of the dial radius unless noted) ----
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
HEXAGRAM_PEN_WIDTH = 0.006           # procedural star outline
HEXAGRAM_PEN_RGBA = (255, 255, 255, 140)
BODY_LABEL_SIZE = 0.34               # fraction of the body size
BODY_LABEL_RGBA = (255, 255, 255, 230)
MARKER_BORDER_WIDTH = 0.05           # fraction of the marker size
MARKER_BORDER_RGBA = (255, 255, 255, 200)

# --- Tray --------------------------------------------------------------------
TRAY_ICON_SIZE = 64                  # px of the procedurally drawn tray pixmap
TRAY_ICON_MARGIN = 0.08              # fraction of the icon size
TRAY_DISC_RGB = (18, 22, 34)
TRAY_MARK_RGB = (255, 211, 77)
TRAY_MARK_SIZE = 0.10                # fraction of the icon size

# --- Default skin ---------------------------------------------------------------
# Typed against skins/manifest.py from day one: extracting it into
# assets/skins/domy/skin.json in M5 is serialization, not redesign.
_DOMY = paths.bundled_skins_dir() / "domy"

DEFAULT_SKIN = SkinDefinition(
    name="DOMY",
    z_order=(
        "background",
        "hexagram",
        "weekday_set",
        "ring",
        "noon_marker",
        "year_marker",
        "hands",
    ),
    background=BackgroundSpec(
        mode="colors",
        # Clockwise from the noon-top sector: yellow (10-14h), orange,
        # red, purple (22-02h), blue, green — matching the mockups.
        sector_palette=(
            "#FFD34D",
            "#FF9E3D",
            "#E14B4B",
            "#8E4BC9",
            "#3D7BFF",
            "#4BC96B",
        ),
        day_base="#F2EFE6",
        twilight_shade=0.55,
        night_shade=0.25,
        radius_fraction=0.84,
    ),
    hexagram=HexagramSpec(
        asset=_DOMY / "dial" / "hexagram.png",
        opacity=0.85,
        radius_fraction=0.80,
    ),
    noon_marker=NoonMarkerSpec(
        asset=None,
        color="#FFC838",
        scale=0.045,
    ),
    ring=RingSpec(
        fill="#4A4E57",
        text_color="#F0F0F0",
        letter_color="#E8B84B",
        width_fraction=0.16,
        # Letter hour-positions follow the Greek-alphabet ordinal (owner
        # spec, matches design/hours/domy.png): M at 12, Y at 20, Omega at
        # 0, D at 4 — an inverted cross, NOT the 6/18 axis.
        letters={12: "M", 20: "Y", 0: "Ω", 4: "D"},
    ),
    weekday_set=WeekdaySpec(
        bodies={
            "sun": None,
            "moon": None,
            "mars": None,
            "mercury": None,
            "jupiter": None,
            "venus": None,
            "saturn": None,
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
        mode="earth",
        variants={},                    # owner drops earth_<continent>_<day|night>.png in M5
        default_variant="europe",
        moon_asset=None,
        day_color="#4B86C9",
        night_color="#20344F",
        moon_lit_color="#E8E4D8",
        moon_dark_color="#2A2D36",
        # Owner spec: the date marker orbits along the INSIDE of the dial,
        # not on the ring band.
        orbit_fraction=0.74,
        scale=0.075,
    ),
    hands=HandsSpec(
        hour=HandSpec(
            asset=_DOMY / "hands" / "hour.png",
            pivot=(0.5, 0.68),          # measured: hub at 68% height, tail below
            length_fraction=0.34,
        ),
        minute=HandSpec(
            asset=_DOMY / "hands" / "minute.png",
            pivot=(0.5, 0.92),          # measured: hub at 92% height
            length_fraction=0.60,
        ),
    ),
)
