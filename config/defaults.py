"""Developer tunables — values a developer may adjust while tuning the app.

Everything here is read-only at runtime. User-changeable state (window
position, chosen city, chosen skin) lives in the user settings file owned
by app/settings_store.py.
"""

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

# --- Settings persistence ----------------------------------------------------
SETTINGS_SCHEMA_VERSION = 1
SETTINGS_WRITE_DEBOUNCE_MS = 750     # collapse rapid moveEvent bursts while dragging

# --- M1 placeholder dial (replaced by render/ layers in M3) -------------------
PLACEHOLDER_DISC_RGBA = (18, 22, 34, 150)
PLACEHOLDER_RING_RGBA = (255, 255, 255, 70)
PLACEHOLDER_RING_WIDTH = 2.0         # logical px
PLACEHOLDER_RING_MARGIN = 4.0        # logical px between widget edge and ring
PLACEHOLDER_NOON_MARK_RGBA = (255, 211, 77, 200)
PLACEHOLDER_NOON_MARK_SIZE = 0.05    # fraction of dial diameter
PLACEHOLDER_CENTER_DOT_RGBA = (255, 255, 255, 120)
PLACEHOLDER_CENTER_DOT_SIZE = 0.02   # fraction of dial diameter
PLACEHOLDER_TEXT = "DOMY"
PLACEHOLDER_TEXT_RGBA = (255, 255, 255, 60)
PLACEHOLDER_TEXT_SIZE = 0.09         # fraction of dial diameter
PLACEHOLDER_TEXT_OFFSET_Y = 0.12     # wordmark top, fraction of dial below center
PLACEHOLDER_TEXT_RECT_HEIGHT = 0.2   # wordmark rect height, fraction of dial

# --- Tray --------------------------------------------------------------------
TRAY_ICON_SIZE = 64                  # px of the procedurally drawn tray pixmap
TRAY_ICON_MARGIN = 0.08              # fraction of the icon size
TRAY_NOON_MARK_SCALE = 2.0           # multiplier over PLACEHOLDER_NOON_MARK_SIZE
