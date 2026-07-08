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

# Six hues clockwise from the hexagram-top wedge (owner spec):
# yellow (top), orange, red, purple (bottom), blue, green.
_SECTOR_PALETTE = (
    "#FFD34D",
    "#FF9E3D",
    "#E14B4B",
    "#8E4BC9",
    "#3D7BFF",
    "#4BC96B",
)

_CONTINENTS = ("europe", "north_america", "south_america", "africa", "asia", "oceania")

DEFAULT_SKIN = SkinDefinition(
    name="DOMY",
    z_order=(
        "background",
        "hexagram",
        "weekday_set",
        "ring",
        "year_marker",
        "hands",
    ),                                  # no noon marker: the hexagram tip IS the noon pointer
    background=BackgroundSpec(
        base_asset=_DOMY / "dial" / "base_gray.png",   # 32-section gray wheel, rotates with the hexagram
        base_color="#8A8D93",
        sector_palette=_SECTOR_PALETTE,
        day_alpha=0.55,
        twilight_alpha=0.28,
        radius_fraction=0.76,           # empty breathing space between the disc and the ring
    ),
    hexagram=HexagramSpec(
        colors=_SECTOR_PALETTE,         # owner: procedural "paint" star
        day_alpha=0.92,                 # near-full opacity where the sun is up
        twilight_alpha=0.55,
        border_alpha=0.85,              # colored outlines run the full circle
        border_width_fraction=0.008,
        radius_fraction=0.80,
    ),
    noon_marker=NoonMarkerSpec(
        asset=None,
        color="#FFC838",
        scale=0.045,
    ),
    ring=RingSpec(
        asset=_DOMY / "dial" / "ring.png",   # design/hours/domy.png (gray; gold later)
        fill="#4A4E57",
        text_color="#F0F0F0",
        letter_color="#E8B84B",
        width_fraction=0.16,
        # Letter hour-positions follow the Greek-alphabet ordinal (owner
        # spec, matches the ring art): M at 12, Y at 20, Omega at 0, D at 4.
        letters={12: "M", 20: "Y", 0: "Ω", 4: "D"},
    ),
    weekday_set=WeekdaySpec(
        bodies={name: _DOMY / "weekday" / f"{name}.png" for name in (
            "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"
        )},
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
        mode="earth",                   # "moon" and "both" selectable (M6 settings)
        variants={
            f"{continent}_{phase}": _DOMY / "year_marker" / f"earth_clean_{continent}_{phase}.png"
            for continent in _CONTINENTS
            for phase in ("day", "night")
        },
        default_variant="europe",
        day_color="#4B86C9",
        night_color="#20344F",
        # Owner spec: the date marker orbits along the INSIDE of the dial,
        # not on the ring band, and is the same size as the weekday planets.
        orbit_fraction=0.66,
        scale=0.11,
        moon_asset=_DOMY / "weekday" / "moon.png",
        moon_lit_color="#E8E4D8",
        moon_dark_color="#2A2D36",
        moon_shadow_alpha=0.82,
        moon_orbit_fraction=0.60,
        moon_scale=0.065,
    ),
    hands=HandsSpec(
        # Owner spec: both hands rotate about a hub 15 px from the image
        # bottom (hub circle radius 15 px), horizontally centered.
        hour=HandSpec(
            asset=_DOMY / "hands" / "hour.png",
            pivot=(0.5, (142 - 15) / 142),      # image 47x142
            length_fraction=0.34,
        ),
        minute=HandSpec(
            asset=_DOMY / "hands" / "minute.png",
            pivot=(0.5, (201 - 15) / 201),      # image 30x201
            length_fraction=0.60,
        ),
    ),
)
