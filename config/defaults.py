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
DEFAULT_DIAL_DIAMETER = 720          # logical px, before DPI scaling
                                     # (owner install-default list 2026-07-12)
MIN_DIAL_DIAMETER = 120
MAX_DIAL_DIAMETER = 2000             # roomy above the largest preset (1440)
SIZE_PRESETS = (360, 540, 720, 1080, 1440)   # owner spec (FINAL.txt #3)

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

# --- Tray / app presentation ---------------------------------------------------
# The owner's gold watch (logo.svg) is the app face: tray icon now, EXE
# icon and installer art in M7; logo-setup.svg is the rose-gold variant.
TRAY_ICON_SIZE = 64                  # px of the rasterized tray pixmap
LOGO_ASSET = paths.assets_dir() / "logo.svg"
LOGO_SETUP_ASSET = paths.assets_dir() / "logo-setup.svg"

# --- Ring faces -------------------------------------------------------------------
# Ring PRESETS are data now (Database/ring_presets.json + the user's
# custom cards in settings, loaded by data/rings.py — owner spec): a
# card is {name, positions, letters}; its positions signature picks the
# LAYOUT (constants.RING_LAYOUTS) whose FACE file lives here.
RING_FACE_DIR = paths.assets_dir() / "ring"

# --- Ring tint (owner spec, FINAL.txt #6) ------------------------------------------
# One hue recolors the WHOLE clock body: the ring art, the hands and
# the Umbra are channel-multiplied by it (gray stays gray under None).
# The letters are separate art and are never tinted. Preset hues below
# are STARTING VALUES — the owner tunes them here. Settings shows them
# as a grid of color circles (Paint style — owner spec 2026-07-11);
# the name appears in the circle's hover tooltip.
RING_TINT_PRESETS = {
    "Gray": None,                       # the untouched owner art
    "Gold": "#D4AF37",
    "Silver": "#C9CDD3",
    "Copper": "#B87333",
    "Purple": "#8E55B9",
    "Ocean": "#4E7A9E",
    # The owner's gold palette (his reference swatches, 2026-07-11).
    "Naples Yellow": "#FFE169",
    "Sunglow": "#FFD235",
    "Mikado Yellow": "#FFC300",
    "Satin Gold": "#C9980B",
    "Golden Brown": "#926C15",
    # Pipetted from the owner's Clock_OuterColors.png (21 ring variants,
    # 3x7 grid, mode color of each hour band — 2026-07-11).
    "Charcoal": "#36454F",
    "Glaucous": "#6082B6",
    "Slate Gray": "#708090",
    "Black Coral": "#54626F",
    "Steel": "#71797E",
    "Roman Silver": "#808992",
    "Cadet Gray": "#91A3B0",
    "Deep Pine": "#253529",
    "Sage Steel": "#5E716A",
    "Smoke": "#738276",
    "Ebony": "#545851",
    "Smoky Plum": "#66606D",
    "Periwinkle": "#9090C0",
    "Lavender Gray": "#A7A6BA",
    "Espresso": "#342523",
    "Anthracite": "#494F55",
    "Granite": "#625D5D",
    "Dim Gray": "#6B6B6B",
    "Stone": "#928E85",
    "Nevada": "#6C7174",
    "Aluminium": "#888B8D",
}
RING_TINT_SWATCH_PX = 22             # diameter of one tint circle
RING_TINT_SWATCHES_PER_ROW = 11
PALETTE_SWATCH_PX = 34               # pointer palette circles (owner:
                                     # bigger than the tint swatches)

# The ring TICK band hover (owner spec 2026-07-12): any of the 360
# arrows answers with what its ANGLE means on each wheel — the 24h
# time, the year-wheel date and the moon-cycle phase. The band spans
# these dial-radius fractions (the arrows' own zone on the ring art).
TICK_HOVER_INNER_FRACTION = 0.86
TICK_HOVER_OUTER_FRACTION = 0.945

# The owner's GOLD letter art (a full latin/greek library for future
# ring presets), overlaid on the ring by calculation so the tint never
# touches them; the silver look is derived by desaturation at load.
RING_LETTER_ART_DIR = paths.assets_dir() / "ring" / "letters"
RING_LETTER_RADIUS_FRACTION = 0.943  # letter center = the middle of the OUTER
                                     # hour band alone (owner spec; measured
                                     # 0.888–0.998 on both ring faces — the
                                     # seconds scale is NOT part of the band)
RING_LETTER_ART_SCALE = 0.075        # letter height, of the dial diameter
                                     # (deliberate slight oversize — owner
                                     # default; the Settings slider scales it)
# Letter shadow (owner spec): a tight, intense dark halo on all sides —
# a gradient border, as if lit from above. Stamped as N offset copies of
# the blackened letter at `alpha` each, `radius` of the letter height.
RING_LETTER_SHADOW_RADIUS = 0.05     # of the letter height
RING_LETTER_SHADOW_ALPHA = 0.55      # per stamp (stamps overlap -> intense)
RING_LETTER_SHADOW_SAMPLES = 8       # offsets around the circle

# --- Hand sizing (owner spec 2026-07-12) -------------------------------------------
# Sizing uses TIP-TO-PIVOT lengths only: the seconds tip reaches the
# ring (the end of the 360-dot scale), the minutes tip the minute
# arrows, and the hours follow each pack's own hours/minutes tip
# ratio. Values derived from the CLASSIC look (285/275-unit tips at
# the old shared 0.88 reach) so existing dials render unchanged.
HAND_SECOND_REACH_FRACTION = 0.88
HAND_MINUTE_REACH_FRACTION = 0.849

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
_CROSS_SEASONS = ("#D9D900", "#D4330F", "#0A70D8", "#129412")
# The TRIO carries the theological trio (owner spec, FINAL.txt #7) and,
# like the cross, ONE palette under both styles: Faith yellow at 12h,
# Love red at 20h, Hope blue at 4h — the hexa paint hues at the M, Y, D
# ring-letter positions.
_TRINITY = ("#F8E600", "#B60000", "#002FFF")
PALETTE_PRESETS = {
    ("hexa", "paint"): (
        "#F8E600", "#DC9600", "#B60000", 
        "#542E85", "#002FFF", "#007E00",
    ),
    ("hexa", "light"): (
        "#00DC00", "#FFFF00", "#FF0000", 
        "#BD00BD", "#0040FF", "#00DDDD",
    ),
    # COMPASS palettes (owner dual-Sunday round 2026-07-12): the wheel
    # is the day's arc from light to dark — North (12h) wears the
    # Ruler's white-gold, the hues descend through afternoon zeal,
    # dusk, evening passion to the SOUTH (24h) Servant: near-black
    # with a silver hint in paint; in the LIGHT world the south is
    # not black but MOONLIGHT silver — pigment loses the light at
    # midnight, light finds the Moon there. W dawn cyan (Hope) and
    # E dusk red-orange (Longing) keep their canon seats.
    ("octa", "paint"): (
        "#FFE9A8", "#ECB800", "#DC5A00", "#B4143C",
        "#20202A", "#00368C", "#00DCDC", "#00C850",
    ),
    ("octa", "light"): (
        "#FFFFFF", "#FFDC00", "#FF6400", "#FF2864",
        "#C8D7F0", "#2850FF", "#00E1FF", "#00FF64",
    ),
    ("cross", "paint"): _CROSS_SEASONS,
    ("cross", "light"): _CROSS_SEASONS,
    ("trio", "paint"): _TRINITY,
    ("trio", "light"): _TRINITY,
    # AURORA (owner spec 2026-07-12): [dawn, five day hues, dusk] —
    # paint = azure/green/yellow/orange/red, light = azure/cyan/green/
    # yellow/red; twilight left (dawn) blue, right (dusk) brown.
    ("aurora", "paint"): (
        "#002FFF", "#0080FF", "#007E00", "#F8E600", "#DC9600",
        "#BC0000", "#5D1212",
    ),
    ("aurora", "light"): (
        "#0040FF", "#0080FF", "#00DCDC", "#00DC00", "#FFFF00",
        "#FF2828", "#720017",
    ),
}

# Elements switch "Colorful" OFF (owner spec, FINAL.txt #5): the day and
# twilight arcs are still indicated, but as plain white transparency
# instead of the pointer-palette hues.
COLORFUL_OFF_COLOR = "#FFFFFF"

# Octa bottom-arm text (time/date/...): sized to span this fraction of
# the slot width (owner: big font, must not overflow the slot).
TIME_TEXT_WIDTH_FRACTION = 0.95

# Article hovers (owner spec, FINAL.txt hover rework + EXTRAS): the
# entity's art rides on top of its article, larger and clearer than on
# the dial; the prose wraps at a fixed width so QToolTip stays a column.
ARTICLE_IMAGE_WIDTH_PX = 192         # owner: at least 2x — the details must read
ARTICLE_TEXT_WIDTH_PX = 460          # owner 2026-07-13 round two: the prose is
                                     # JUSTIFIED inside a fixed-width column
                                     # (Qt reflows it — no manual wrapping)
ARTICLE_COLUMN_WIDTH_PX = 400        # the hexa TWO-COLUMN legend: each sign's
                                     # column; two of them + spacing must fit
                                     # LEGEND_MAX_WIDTH_FRACTION of a 1080p
                                     # screen (0.45 × 1920 = 864)
# Subheading spacing (owner 2026-07-14 round two): the heading sits
# CENTERED and visibly closer to ITS paragraph than to the previous one
# — Qt collapses adjacent block margins to the larger, so the paragraph
# after a heading carries the same small top margin.
ARTICLE_SUBHEAD_GAP_ABOVE_PX = 18
ARTICLE_SUBHEAD_GAP_BELOW_PX = 2

# The Judas–Lucifer scale badges (owner 2026-07-13): the two triangle
# medallions illustrating "The Two Triangles" — wired before the art
# lands; the Encyclopedia hides missing files.
SCALE_ART_DIR = paths.assets_dir() / "badge" / "scale"
INSTRUMENT_ART_DIR = paths.assets_dir() / "instrument"
# The Astrology/Ascendant hover image trio (owner 2026-07-13): the
# ACTIVE style's art large in the middle, the two remaining styles
# small at its sides.
ASTRO_MAIN_IMAGE_PX = 256
ASTRO_SIDE_IMAGE_FRACTION = 0.35
PERIOD_EARTH_IMAGE_PX = 128          # the Day/Night hover carries a mini Earth
                                     # of the active region (owner 2026-07-12)
ARTICLE_TITLE_PX = 17                # the entity NAME above the article (owner
                                     # spec 2026-07-11: a slightly bigger title,
                                     # then a margin, then the prose)

# --- Legend term highlighting (owner spec 2026-07-12) ------------------------------
# Canon terms POP inside article prose: virtues bold blue, vices bold
# red, moods/emotions bold yellow, color words bold in their own color.
# Applied at RENDER time over the English and Serbian originals (the
# machine-translated languages read plain); hex notes like "(#F8E600)"
# are stripped from the display. Patterns are regex fragments, ALL
# matched case-insensitively (owner report 2026-07-12: a lowercase
# "gordost" must burn red too); Serbian fragments cover the case
# endings including the -šću instrumentals.
LEGEND_VIRTUE_COLOR = "#6FA8FF"
LEGEND_VICE_COLOR = "#FF6B6B"
LEGEND_MOOD_COLOR = "#FFD34D"
LEGEND_TERM_PATTERNS = {
    "virtue": (
        "Humility", "Justice", "Generosity", "Wisdom", "Courage",
        "Serenity", "Love", "Patience", "Faith", "Hope",
        "Poniznost(?:i)?", "Poniznošću", "Pravednost(?:i)?", "Pravednošću",
        "Velikodušnost(?:i)?", "Velikodušnošću",
        "Mudrost(?:i)?", "Mudrošću", "Hrabrost(?:i)?", "Hrabrošću",
        "Spokoj(?:a|u|em)?", "Ljubav(?:i|lju)?", "Strpljenj[eau]",
        "Strpljenjem", "Ver[aeiu]", "Verom", "Nad[aeiu]", "Nadom",
    ),
    "vice": (
        "Pride", "Servility", "Excess", "Greed", "Wrath", "Fear",
        "Jealousy", "Envy",
        "Gordost(?:i)?", "Gordošću", "Pokornost(?:i)?", "Pokornošću",
        "Neumerenost(?:i)?", "Neumerenošću",
        "Pohlep[aeiou]", "Pohlepom", "Gnev(?:a|u|om)?", "Strah(?:a|u|om)?",
        "Ljubomor[aeiou]", "Ljubomorom", "Zavist(?:i)?", "Zavišću",
    ),
    "mood": (
        "Joy", "Zeal", "Passion", "Sorrow", "Calm", "Renewal", "Glory",
        # Awe is the renamed servant mood (2026-07-14); Eclipse stays
        # matchable for The Ninth Mood's own article.
        "Awe", "Eclipse", "Longing",
        "Radost(?:i)?", "Radošću", "Žar(?:a|u|om)?",
        "Strast(?:i)?", "Strašću",
        "Tug[aeiou]", "Tugom", "Mir(?:a|u|om)?", "Obnov[aeiou]", "Obnovom",
        "Sjaj(?:a|u|em)?", "Strahopoštovanj[eau]", "Strahopoštovanjem",
        "Pomračenj[eau]", "Pomračenjem",
        "Čežnj[aeiou]", "Čežnjom",
    ),
}
# Color WORDS wear their own hue — but ONLY the hue(s) of the entity's
# own diamond (owner correction 2026-07-12: in the Soldier's article
# only "orange" colors, in the Merchant's only "purple"; "the red
# planet" or gold-as-money stay plain). Keyed patterns; the accent
# tables below say which keys an article may light up.
LEGEND_COLOR_PATTERNS = {
    "yellow": ((r"yellow\w*", r"žut\w*"), "#F8E600"),
    "gold": ((r"golden|gold\w*", r"zlat\w*"), "#E8C24A"),
    "amber": ((r"amber", r"ćilibar\w*"), "#ECB800"),
    "orange": ((r"orange\w*", r"narandžast\w*"), "#E88A20"),
    "red": ((r"red(?:s|der|dish|dens)?", r"crimson", r"crven\w*"), "#F04040"),
    "purple": ((r"purple\w*", r"violet\w*", r"purpur\w*", r"ljubičast\w*"),
               "#A968E0"),
    "magenta": ((r"magenta", r"magent\w*"), "#E858E8"),
    "blue": ((r"blue\w*", r"plav\w*"), "#5C86FF"),
    "azure": ((r"azure", r"azur\w*"), "#4AA8FF"),
    "green": ((r"green\w*", r"zelen\w*"), "#3ECC3E"),
    "cyan": ((r"cyan", r"cijan\w*"), "#00DCDC"),
    "white": ((r"white\w*", r"bel(?:o|a|e|i|u|im|om|og|oj)\b"), "#FFFFFF"),
    "silver": ((r"silver\w*", r"srebrn\w*"), "#C9CDD3"),
}
# Which color keys each weekday BODY may light up: the union of its
# arm's hues across the palettes (hexa/octa, paint/light) — never a
# color that merely appears in the prose.
BODY_ACCENT_HUES = {
    "sun": ("white", "gold", "yellow", "green"),
    "moon": ("blue",),
    "mars": ("orange", "amber", "yellow"),
    "mercury": ("purple", "magenta", "red"),
    "jupiter": ("yellow", "green", "cyan"),
    "venus": ("red", "orange"),
    "saturn": ("green", "cyan", "azure"),
}
# Zodiac signs inherit their hexa arm's (paint, light) pair; the trio
# virtues their own hue.
SIGN_ACCENT_HUES = {
    "Gemini": ("yellow", "green"), "Cancer": ("yellow", "green"),
    "Leo": ("orange", "yellow"), "Virgo": ("orange", "yellow"),
    "Libra": ("red",), "Scorpio": ("red",),
    "Sagittarius": ("purple", "magenta"), "Capricorn": ("purple", "magenta"),
    "Aquarius": ("blue",), "Pisces": ("blue",),
    "Aries": ("green", "cyan"), "Taurus": ("green", "cyan"),
}
TRIO_ACCENT_HUES = {"Faith": ("yellow",), "Love": ("red",), "Hope": ("blue",)}
# South of the equator the mirrored year wheel seats every sign on the
# OPPOSITE arm (owner spec 2026-07-12) — its accents follow that arm.
_SIGN_OPPOSITE = {
    "Gemini": "Sagittarius", "Cancer": "Capricorn",
    "Leo": "Aquarius", "Virgo": "Pisces",
    "Libra": "Aries", "Scorpio": "Taurus",
}
_SIGN_OPPOSITE.update({south: north for north, south in _SIGN_OPPOSITE.items()})
SIGN_ACCENT_HUES_SOUTH = {
    sign: SIGN_ACCENT_HUES[_SIGN_OPPOSITE[sign]] for sign in SIGN_ACCENT_HUES
}

# The Legend popup (replaces QToolTip, owner decision): capped to these
# screen fractions — taller content scrolls instead of clipping off a
# small screen; dark tooltip styling.
LEGEND_MAX_WIDTH_FRACTION = 0.45
LEGEND_MAX_HEIGHT_FRACTION = 0.85
LEGEND_CURSOR_OFFSET_PX = 14
LEGEND_PADDING_PX = 8
LEGEND_BG = "#2B2B2B"
LEGEND_BORDER = "#6E6E6E"
LEGEND_TEXT = "#FFFFFF"

# The Encyclopedia article view (owner UX rounds 2026-07-12/13): the
# text BLOCK hugs the LEFT edge and spans this fraction of the window
# width — the prose reflows to fill it (no fixed wrap); the font grows
# with the width at a gentle em-like coefficient between the base and
# the cap.
ENCYCLOPEDIA_TEXT_WIDTH_FRACTION = 0.9
ENCYCLOPEDIA_BASE_FONT_PX = 13
ENCYCLOPEDIA_FONT_GROWTH = 0.006     # extra px per viewport px above the base width
ENCYCLOPEDIA_FONT_BASE_WIDTH = 560   # viewport width where the base font applies
ENCYCLOPEDIA_MAX_FONT_PX = 21
# The topic gallery cards (owner 2026-07-13: everything centered, the
# thumbnails RESPONSIVE — they grow/shrink with the window between the
# two bounds; below the minimum the scrollbar takes over).
ENCYCLOPEDIA_TOPIC_ICON_MIN_PX = 72
ENCYCLOPEDIA_TOPIC_ICON_MAX_PX = 200
# Modern reader buttons (owner 2026-07-14: "veći, upečatljiviji,
# življih boja — ne kao app iz 1990-e"): vivid gradient pills shared by
# the Encyclopedia and the Guide. Each role owns a (top, bottom)
# gradient pair; hover lightens and pressed darkens the same pair.
UI_BUTTON_FONT_PX = 17
UI_BUTTON_RADIUS_PX = 12
UI_BUTTON_PADDING_PX = (10, 26)         # vertical, horizontal
UI_BUTTON_SMALL_FONT_PX = 14            # the per-entry look arrows
UI_BUTTON_SMALL_PADDING_PX = (5, 12)
UI_BUTTON_COLORS = {
    "home": ("#4FACFE", "#1565C0"),         # blue — the way back
    "previous": ("#FFB75E", "#E65100"),     # orange
    "next": ("#7EDB7B", "#2E7D32"),         # green
    "download": ("#CE93D8", "#6A1B9A"),     # violet — save the entry
    "neutral": ("#B0BEC5", "#546E7A"),      # the look arrows
}
# Reader image ceiling (owner imperative 2026-07-14): no article or
# Guide image may eat the page — anything taller than this fraction of
# the viewport height scales down to it, leaving room for the text.
# Round two: the WHOLE image grid shares the ceiling — stacked rows
# split it, so the Week's Sunday pairs still leave the text visible.
READER_IMAGE_MAX_HEIGHT_FRACTION = 0.35
# The unlocked hidden mode (owner 2026-07-14): hovering within this
# many degrees of the 12h/24h ring letters opens the Four Greetings.
# The hit zone is the LETTER band OUTSIDE the tick scale (owner round
# two: the ticks at those angles must keep their own day/year/moon
# reading), and the stanzas breathe with a small margin, not a full
# blank line.
GREETINGS_LETTER_HALF_DEG = 6.0
GREETINGS_LETTER_OUTER_FRACTION = 1.08
GREETINGS_STANZA_GAP_PX = 6

# Time Travel QUICK JUMPS (owner 2026-07-14): one-click presets under
# the Time Travel menu — sun/moon turning points, the poles, and the
# Royal Observatory itself. Same rules as the dialog:
# TIME_TRAVEL_DURATION_S, then back to the present; the jumps CHAIN
# from the running simulation. The places are REAL coordinates with
# their REAL clocks (the poles ride UTC).
QUICK_JUMP_POLE_LATITUDE = 89.99     # exact 90 divides astral by zero
GREENWICH_LATITUDE = 51.4779
GREENWICH_LONGITUDE = 0.0
GREENWICH_TIMEZONE = "Europe/London"

# The slot ROUNDEL (owner 2026-07-14, watch-subdial inspiration):
# every TEXT display and the flat astrology art (sign / logo /
# constellation) sit on a subdial — a circle in the ring's own face
# color (sampled from the active ring art), rimmed in the letter
# FINISH metal; circular plates (medallions, planets, colored badges)
# stay bare.
SLOT_ROUNDEL_BORDER_FRACTION = 0.045     # rim width, of the diameter
SLOT_ROUNDEL_CONTENT_FRACTION = 0.78     # content size inside the rim
SLOT_ROUNDEL_FILL_FALLBACK = "#39434D"   # unreadable/missing ring art
SLOT_ROUNDEL_BORDER_COLORS = {
    "gold": "#FFD235",
    "silver": "#C9CDD3",
    "bronze": "#CD7F32",
}

# The Guide window (owner spec: a paged, RESIZABLE help book): pages
# group related images (pages.json), captions.json holds per-image
# Title\ntext; images open at 540 px (75% of the 720 originals) and
# scale live with the window.
GUIDE_DIR = paths.assets_dir() / "guide"
GUIDE_INITIAL_IMAGE_PX = 540
GUIDE_TITLE_PX = 22
GUIDE_SUBTITLE_PX = 17
GUIDE_BODY_PX = 14        # owner 2026-07-14: the caption text was tiny
GUIDE_SPACING_PX = 8

# Translation (owner spec: translate-once-then-cache, no accounts, no
# keys): the keyless Google gtx endpoint; the per-language cache lives
# beside settings.json in %APPDATA%/DOMY Watch/translations/.
TRANSLATE_ENDPOINT = "https://translate.googleapis.com/translate_a/single"
TRANSLATE_TIMEOUT_S = 15

# Transparent margin around the dial INSIDE the window (owner bug
# report: M and Omega touch the window square and their overhang and
# shadow get clipped). Sized for the worst case: ring letters at the
# 200% slider maximum reach ~7.9% beyond the dial radius plus their
# halo (~9.4% total) — 6% of the DIAMETER per side (= 12% of the
# radius) leaves real headroom; 5% left only ~2 px at 800 px.
DIAL_WINDOW_MARGIN_FRACTION = 0.06

# Umbra contrast spans, (lightest, darkest) window bounds. Owner spec:
#   full  — the whole gray range: sectioned ladders run endpoint-
#           inclusive (16 shades -> 255..0 step 17, matching his art);
#   half  — the MIDDLE half [64, 192]; light — the BRIGHT half
#           [128, 255]; dark — the DARK half [0, 127]. These three take
#           the centers of N equal bins (exact step 8 for 16 shades:
#           half 188..68, light 252..132, dark 124..4).
# The gradient form sweeps the same spans continuously.
UMBRA_CONTRAST_SPANS = {
    "full": (255, 0),
    "half": (192, 64),
    "light": (256, 128),
    "dark": (128, 0),
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
# The cross-cure emblem logos (owner Gemini art 2026-07-12): one PNG
# per virtue/sin/mood, Capitalized stems, 8 per family (Sunday twice).
EMBLEM_ART_DIRS = {
    "virtues": paths.assets_dir() / "emblem" / "virtue",
    "sins": paths.assets_dir() / "emblem" / "sin",
    "moods": paths.assets_dir() / "emblem" / "mood",
    "intelligence": paths.assets_dir() / "emblem" / "intelligence",
}
# The trinity and season badge families (owner Gemini art 2026-07-13):
# Faith/Hope/Love triskelions; the Goethe-axis seasons with the
# tropics' Wet_Season/Dry_Season, plus turning_point/ (the solstices
# and the one Equinox) and meteorological/ (the measured twins).
TRINITY_ART_DIR = paths.assets_dir() / "badge" / "trinity"
SEASON_ART_DIR = paths.assets_dir() / "badge" / "season"
# Arm-hover badge width (the trio/cardinal/diagonal tooltips carry
# their emblem above the text — smaller than the article plates).
HOVER_BADGE_WIDTH_PX = 128

# --- Weekday body themes (SYMBOLISM.md canon) -----------------------------------
# Display names per theme, body -> name (the weekday hover reads
# "Wednesday, Odin" in the norse theme). "planets" keeps the skin's own
# unit untouched. Saturday has no Norse god — the Sabbath stands in
# (canon). Art: assets/weekday/<theme>/<Entity>.png (files carry the
# ENTITY names; the two Norse diacritics fold to ASCII on disk).
WEEKDAY_THEME_NAMES = {
    # The owner's planet GLYPHS (☿ ♃ …) — same entities as "planets",
    # body-named files, planet display names.
    "planet_signs": {
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
    },
    # Display names carry the NATIVE script (owner 2026-07-12: "da
    # koristimo ta slova" — like the Japanese kanji and the Slavic
    # diacritics); the files keep plain ASCII stems via the explicit
    # overrides below.
    "greek": {
        "sun": "Helios (Ἥλιος)",
        "moon": "Selene (Σελήνη)",
        "mars": "Ares (Ἄρης)",
        "mercury": "Hermes (Ἑρμῆς)",
        "jupiter": "Zeus (Ζεύς)",
        "venus": "Aphrodite (Ἀφροδίτη)",
        "saturn": "Cronus (Κρόνος)",
    },
    "norse": {
        "sun": "Sól",
        "moon": "Máni",
        "mars": "Tyr (Týr)",
        "mercury": "Odin (Óðinn)",
        "jupiter": "Thor (Þórr)",
        "venus": "Freya (Freyja)",
        "saturn": "Loki",     # owner decision (FINAL.txt #2): Loki stands
                              # on Saturday — the bound trickster as
                              # Cronus' northern mirror
    },
    # Egyptian gods (owner art 2026-07-11, per the approved mapping):
    # Ra's Sunday, Khonsu the moon-walker, Montu the war falcon, Thoth
    # the scribe on the messenger's day, Amun the king of gods, Hathor
    # love and beauty, Osiris — harvest, patience and rebirth on
    # Saturn's day.
    "egypt": {
        "sun": "Ra",
        "moon": "Khonsu",
        "mars": "Montu",
        "mercury": "Thoth",
        "jupiter": "Amun",
        "venus": "Hathor",
        "saturn": "Osiris",
    },
    # Slavic gods (owner art 2026-07-12, per the approved mapping):
    # Dažbog the giving sun, Hors the night-walker, Svetovid's four
    # faces and white war-horse on Tuesday, Veles the horned trader-
    # trickster mirroring Odin and Hermes, Perun's oak and thunder at
    # noon, Mokoš spinning on the day her cult kept as Friday, Morana
    # — winter drowned each spring — on the arm of Renewal.
    "slavic": {
        "sun": "Dažbog",
        "moon": "Hors",
        "mars": "Svetovid",
        "mercury": "Veles",
        "jupiter": "Perun",
        "venus": "Mokoš",
        "saturn": "Morana",
    },
    # The seven metals of alchemy (owner art 2026-07-12): the classical
    # planet-metal correspondence — every medallion the same still life
    # of bars, nuggets and coiled wire, each wearing its own metal.
    "alchemy": {
        "sun": "Gold",
        "moon": "Silver",
        "mars": "Iron",
        "mercury": "Quicksilver",
        "jupiter": "Tin",
        "venus": "Copper",
        "saturn": "Lead",
    },
    # The Japanese week (owner art 2026-07-12, Gemini from our prompts):
    # the yōbi day names ARE the planetary week — sun, moon, then the
    # five Wu Xing element stars (fire=Mars, water=Mercury, wood=
    # Jupiter, metal=Venus, earth=Saturn). Display names KEEP the
    # kanji (owner instruction); files are folded ASCII overrides.
    "japan": {
        "sun": "Nichiyōbi (日曜日)",
        "moon": "Getsuyōbi (月曜日)",
        "mars": "Kayōbi (火曜日)",
        "mercury": "Suiyōbi (水曜日)",
        "jupiter": "Mokuyōbi (木曜日)",
        "venus": "Kin'yōbi (金曜日)",
        "saturn": "Doyōbi (土曜日)",
    },
    # NARRATIVE-FIRST remap (owner decision 2026-07-12): each religion
    # sits on the day its OWN canon points to, not its rest day —
    # Freemasonry's quest for Light under the All-Seeing Eye takes the
    # Sun (its Sunday DOUBLE = the rough vs the perfect ashlar);
    # Islam's calendar IS the moon (Quran 2:189); Buddhism wins the
    # war-day without weapons (Mara, Dhammapada 103); Christianity's
    # forgiving love lands on Venus's Friday (Good Friday, agape).
    "religion": {
        "sun": "Freemasonry",       # owner: replaces Zoroastrianism in
                                    # the basic seven (now an alternate)
        "moon": "Islam",
        "mars": "Buddhism",
        "mercury": "Taoism",
        "jupiter": "Hinduism",
        "venus": "Christianity",
        "saturn": "Judaism",
    },
    # The ALTERNATE religion set — each on the day it fits best (canon
    # in SYMBOLISM.md; Egypt and Babylon per the owner's 2026-07-10 art:
    # Ra's Sunday, Ishtar IS Venus and Babylon invented the 7-day week).
    "religion_alt": {
        "sun": "Mithraism",     # owner decision 2026-07-12: replaces Egypt
                                # (a duplicate once the Egyptian gods became
                                # a full theme) — Sol Invictus IS dies Solis
        "moon": "Druidism",
        "mars": "Zoroastrianism",
        "mercury": "Shamanism",
        "jupiter": "Sikhism",
        "venus": "Babylon",
        "saturn": "Voodoo",
    },
    "profession": {
        "sun": "Ruler · Servant",   # the yin-yang center (owner spec
                                    # 2026-07-12): one figure, two faces
        "moon": "Physician",
        "mars": "Soldier",
        "mercury": "Merchant",
        "jupiter": "Priest",
        "venus": "Artist",
        "saturn": "Farmer",
    },
    # THE ANIMAL SOCIETIES (owner 2026-07-13) — three orders of order:
    # the pack ranks, the hive works by age (the career IS the clock),
    # the herd remembers (the leader is the one who holds the map).
    "wolf": {
        "sun": "Alpha · Omega",     # the first and the last of the pack
                                    # — M at noon, Ω at midnight
        "moon": "Luna",
        "mars": "Hunter",
        "mercury": "Scout",
        "jupiter": "Beta",
        "venus": "Mate",
        "saturn": "Elder",
    },
    "bee": {
        "sun": "Queen · Cleaner",   # the mother of the hive and the
                                    # day-one daughter at her birth cell
        "moon": "Nurse",
        "mars": "Guard",
        "mercury": "Scout",
        "jupiter": "Builder",
        "venus": "Drone",
        "saturn": "Forager",
    },
    "elephant": {
        "sun": "Matriarch · Memory",  # the ruler and the REMEMBERED
                                      # ruler — the bones that taught her
        "moon": "Allomother",
        "mars": "Musth",
        "mercury": "Caller",
        "jupiter": "Mentor",
        "venus": "Reunion",
        "saturn": "Elder",
    },
    # The SCRIPTURE family (owner 2026-07-14): three stained-glass sets.
    "bible": {
        "sun": "Ancient of Days · Son",
        "moon": "Mary",
        "mars": "David",
        "mercury": "Moses",
        "jupiter": "Solomon",
        "venus": "Adam & Eve",
        "saturn": "Joseph",
    },
    "bible2": {
        "sun": "Abraham · Isaac",
        "moon": "Jonah",
        "mars": "Samson",
        "mercury": "Jacob",
        "jupiter": "Noah",
        "venus": "Ruth",
        "saturn": "Job",
    },
    "bible_dark": {
        "sun": "Lucifer · Judas",
        "moon": "Lilith",
        "mars": "Goliath",
        "mercury": "The Serpent",
        "jupiter": "Herod",
        "venus": "Delilah",
        "saturn": "Cain",
    },
    # The DEEP SKY (owner 2026-07-14): star-chart medallions.
    "cosmos": {
        "sun": "Sun · Black Hole",
        "moon": "Nebula",
        "mars": "Supernova",
        "mercury": "Pulsar",
        "jupiter": "Galaxy",
        "venus": "Binary Stars",
        "saturn": "Comet",
    },
    # The Planets MEDALLION look — same entities, bronze art.
    "planets_art": {
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
    },
    # THE INNER WHEEL on the dial (owner 2026-07-14): the days ARE
    # their virtues / vices / hour-moods.
    "virtues": {
        "sun": "Justice · Humility",
        "moon": "Serenity",
        "mars": "Courage",
        "mercury": "Wisdom",
        "jupiter": "Generosity",
        "venus": "Love",
        "saturn": "Patience",
    },
    "sins": {
        "sun": "Pride · Servility",
        "moon": "Fear",
        "mars": "Wrath",
        "mercury": "Greed",
        "jupiter": "Excess",
        "venus": "Jealousy",
        "saturn": "Envy",
    },
    "moods": {
        "sun": "Glory · Awe",
        "moon": "Calm",
        "mars": "Zeal",
        "mercury": "Sorrow",
        "jupiter": "Joy",
        "venus": "Passion",
        "saturn": "Renewal",
    },
}

# File stems on disk: the display names folded to ASCII (Sól -> Sol,
# Dažbog -> dazbog); the owner's religion, planet-sign, egypt, slavic
# and alchemy art uses lowercase file names.
_ASCII_FOLD = str.maketrans("óážš", "oazs")
_LOWERCASE_THEMES = (
    "religion", "religion_alt", "planet_signs", "egypt", "slavic", "alchemy",
    "wolf",                        # the owner's wolf art uses lowercase stems
)
# Theme -> art folder under assets/weekday/: both religion sets share
# the ONE religion/ folder (all fourteen owner medallions together).
# FAMILY/VARIANT tree (owner restructure 2026-07-14): every theme dir
# is <family>/<variant> — related themes share a family (religion =
# primary Creeds + secondary Mysteries; planets = primary photos +
# signs glyphs + art medallions; bible = primary/secondary/dark), and
# a variant's colored arc is its SIBLING <family>/colored with dual/
# INSIDE each variant.
WEEKDAY_THEME_DIRS = {
    "planet_signs": "planets/signs",
    "greek": "greek/primary",
    "norse": "norse/primary",
    "egypt": "egypt/primary",
    "slavic": "slavic/primary",
    "alchemy": "alchemy/primary",
    "japan": "japan/primary",
    "religion": "religion/primary",
    "religion_alt": "religion/secondary",
    "profession": "profession/primary",
    "wolf": "wolf/primary",
    "bee": "bee/primary",
    "elephant": "elephant/primary",
    "bible": "bible/primary",
    "bible2": "bible/secondary",
    "bible_dark": "bible/dark",
    "cosmos": "cosmos/primary",
    "planets_art": "planets/art",
    # The emblem families live OUTSIDE assets/weekday/ — the relative
    # step-up reaches assets/emblem/ (owner 2026-07-14).
    "virtues": "../emblem/virtue",
    "sins": "../emblem/sin",
    "moods": "../emblem/mood",
}
WEEKDAY_THEME_FILES = {
    theme: {
        body: (
            name.translate(_ASCII_FOLD).lower()
            if theme in _LOWERCASE_THEMES
            else name.translate(_ASCII_FOLD)
        )
        for body, name in names.items()
    }
    for theme, names in WEEKDAY_THEME_NAMES.items()
}
# The dual center shows both faces in the hover title, but the owner's
# medallion file keeps the single name.
WEEKDAY_THEME_FILES["profession"]["sun"] = "Ruler"
WEEKDAY_THEME_FILES["wolf"]["sun"] = "alpha"
WEEKDAY_THEME_FILES["bee"]["sun"] = "Queen"
WEEKDAY_THEME_FILES["elephant"]["sun"] = "Matriarch"
# The metal reads Quicksilver, the owner's file keeps the element name.
WEEKDAY_THEME_FILES["alchemy"]["mercury"] = "mercury"
# The Greek and Norse display names carry native-script parentheticals
# now — the files stay on the plain ASCII stems.
WEEKDAY_THEME_FILES["greek"] = {
    "sun": "Helios", "moon": "Selene", "mars": "Ares",
    "mercury": "Hermes", "jupiter": "Zeus", "venus": "Aphrodite",
    "saturn": "Cronus",
}
WEEKDAY_THEME_FILES["norse"] = {
    "sun": "Sol", "moon": "Mani", "mars": "Tyr",
    "mercury": "Odin", "jupiter": "Thor", "venus": "Freya",
    "saturn": "Loki",
}
# The Japanese display names carry kanji — the files are the romaji
# day names folded to plain ASCII (macrons and the apostrophe dropped).
WEEKDAY_THEME_FILES["japan"] = {
    "sun": "nichiyobi",
    "moon": "getsuyobi",
    "mars": "kayobi",
    "mercury": "suiyobi",
    "jupiter": "mokuyobi",
    "venus": "kinyobi",
    "saturn": "doyobi",
}
# The text-wave themes (owner 2026-07-14): explicit lowercase stems —
# the display names carry duals ("·") and compounds ("Adam & Eve").
WEEKDAY_THEME_FILES["bible"] = {
    "sun": "ancient_of_days", "moon": "mary", "mars": "david",
    "mercury": "moses", "jupiter": "solomon", "venus": "adam_and_eve",
    "saturn": "joseph",
}
WEEKDAY_THEME_FILES["bible2"] = {
    "sun": "abraham", "moon": "jonah", "mars": "samson",
    "mercury": "jacob", "jupiter": "noah", "venus": "ruth",
    "saturn": "job",
}
WEEKDAY_THEME_FILES["bible_dark"] = {
    "sun": "lucifer", "moon": "lilith", "mars": "goliath",
    "mercury": "serpent", "jupiter": "herod", "venus": "delilah",
    "saturn": "cain",
}
WEEKDAY_THEME_FILES["cosmos"] = {
    "sun": "sun", "moon": "nebula", "mars": "supernova",
    "mercury": "pulsar", "jupiter": "galaxy", "venus": "binary_stars",
    "saturn": "comet",
}
WEEKDAY_THEME_FILES["planets_art"] = {
    "sun": "sun", "moon": "moon", "mars": "mars",
    "mercury": "mercury", "jupiter": "jupiter", "venus": "venus",
    "saturn": "saturn",
}
# The emblem stems ARE the single names (Capitalized) — only the dual
# sun display titles need the override.
WEEKDAY_THEME_FILES["virtues"] = {
    "sun": "Justice", "moon": "Serenity", "mars": "Courage",
    "mercury": "Wisdom", "jupiter": "Generosity", "venus": "Love",
    "saturn": "Patience",
}
WEEKDAY_THEME_FILES["sins"] = {
    "sun": "Pride", "moon": "Fear", "mars": "Wrath",
    "mercury": "Greed", "jupiter": "Excess", "venus": "Jealousy",
    "saturn": "Envy",
}
WEEKDAY_THEME_FILES["moods"] = {
    "sun": "Glory", "moon": "Calm", "mars": "Zeal",
    "mercury": "Sorrow", "jupiter": "Joy", "venus": "Passion",
    "saturn": "Renewal",
}

# THE DUAL SUNDAY (owner 2026-07-12): every theme's center day has a
# SECOND face — the Servant to the Ruler. On the Compass and the
# Seasons both faces shine (Ruler north 12h, Servant south 24h — two
# persons, a union); the Trinity and the Prism keep ONE image (two
# persons in one body) with both faces in the hover. Paths are
# relative to WEEKDAY_ART_DIR without the extension; the metal themes'
# COLORED look inserts a colored/ folder before the file name (the
# profession Servant is a full eighth plate living beside the Ruler).
# The two FACE NAMES of each theme's Sunday (hover titles: the north
# face and the south face; the combined single-image legend keeps the
# theme's own dual display name).
WEEKDAY_DUAL_NAMES = {
    "planets": ("Sun", "Eclipsed Sun"),
    "planet_signs": ("Sun", "Eclipsed Sun"),
    "greek": ("Helios", "Phaethon"),
    "norse": ("Sól", "Skoll"),
    "egypt": ("Ra", "Afu-Ra"),
    "slavic": ("Young Dažbog", "Old Dažbog"),
    "alchemy": ("Gold", "Raw Ore"),
    "japan": ("Amaterasu", "Ama-no-Iwato"),
    "religion": ("Freemasonry", "The Rough Ashlar"),
    "religion_alt": ("Mithraism", "Corax"),
    "profession": ("Ruler", "Servant"),
    "wolf": ("Alpha", "Omega"),
    "bee": ("Queen", "Cleaner"),
    "elephant": ("Matriarch", "Memory"),
    "bible": ("Ancient of Days", "Son"),
    "bible2": ("Abraham", "Isaac"),
    "bible_dark": ("Lucifer", "Judas"),
    "cosmos": ("Sun", "Black Hole"),
    "planets_art": ("Sun", "Eclipsed Sun"),
    "virtues": ("Justice", "Humility"),
    "sins": ("Pride", "Servility"),
    "moods": ("Glory", "Awe"),
}
# Dual paths live INSIDE the theme's variant dir; the colored dual is
# the same path with the variant segment swapped to colored/ (owner
# restructure 2026-07-14).
WEEKDAY_DUAL_FILES = {
    "planets": "planets/primary/dual/sun_eclipse",
    "planet_signs": "planets/signs/dual/sun_eclipse",
    "greek": "greek/primary/dual/Phaethon",
    "norse": "norse/primary/dual/Skoll",
    "egypt": "egypt/primary/dual/afu_ra",
    "slavic": "slavic/primary/dual/dazbog_old",
    "alchemy": "alchemy/primary/dual/ore",
    "japan": "japan/primary/dual/ama_no_iwato",
    "religion": "religion/primary/dual/rough_ashlar",
    "religion_alt": "religion/secondary/dual/corax",
    "profession": "profession/primary/dual/Servant",
    "wolf": "wolf/primary/dual/omega",
    "bee": "bee/primary/dual/Cleaner",
    "elephant": "elephant/primary/dual/Memory",
    "bible": "bible/primary/dual/son_servant",
    "bible2": "bible/secondary/dual/isaac",
    "bible_dark": "bible/dark/dual/judas",
    "cosmos": "cosmos/primary/dual/black_hole",
    "planets_art": "planets/art/dual/sun_eclipse",
    "virtues": "../emblem/virtue/Humility",
    "sins": "../emblem/sin/Servility",
    "moods": "../emblem/mood/Awe",
}

# The metal SWAP for the bronze-plate art (owner insight 2026-07-12:
# the medallions mix bronze details with GRAY stone and engravings —
# only the warm bronze pixels may change, the gray stays). Detection =
# a warm-hue window with soft edges + a saturation ramp; per-target
# hue/saturation/value mapping. Bronze = the art as drawn (no swap).
METAL_SWAP_HUE_WINDOW = (10.0, 60.0)   # degrees, warm bronze range
METAL_SWAP_HUE_SOFT = 8.0              # soft edge width outside the window
METAL_SWAP_SAT_RAMP = (0.10, 0.28)     # smoothstep: below gray, above bronze
METAL_SWAP_TARGETS = {
    "gold": {"hue": 48.0, "sat_mul": 1.25, "val_mul": 1.25},
    "silver": {"hue": 220.0, "sat_mul": 0.06, "val_mul": 1.22},
}
# Bronze ring LETTERS are PRE-RENDERED from the silver ones
# (setup/make_bronze_letters.py). Final recipe = a STRAIGHT multiply
# with classic bronze, no brightness/contrast change (owner verdict
# revised on the live dial 2026-07-12: the darkened candidates sat
# darker than the bronze medallions — candidate C matches).
BRONZE_LETTER_TINT = "#CD7F32"
BRONZE_LETTER_BRIGHTNESS = 1.0
BRONZE_LETTER_CONTRAST = 1.0

# ONE menu/encyclopedia/settings title per theme (English; translated
# through the ui/ overlay at display) — every theme list iterates this.
WEEKDAY_THEME_TITLES = {
    "planets": "Planets",
    "planet_signs": "Planet signs",
    "greek": "Greek gods",
    "norse": "Norse gods",
    "egypt": "Egyptian gods",
    "slavic": "Slavic gods",
    "alchemy": "Alchemy",
    "japan": "Japanese week",
    # Owner renames 2026-07-13: masonry and voodoo are creeds and
    # mysteries, not strictly religions — and "Religions II" is gone.
    "religion": "Creeds",
    "religion_alt": "Mysteries",
    "profession": "Professions",
    "wolf": "Wolf Pack",
    "bee": "Bee Hive",
    "elephant": "Elephant Herd",
    # The text-wave themes (owner 2026-07-14). planets_art carries NO
    # title on purpose: it nests as the Planets "Art" option in the
    # menu and rides the Planets encyclopedia topic as a look.
    "bible": "Bible",
    "bible2": "Bible II",
    "bible_dark": "Bible Dark",
    "cosmos": "Cosmos",
    # The Inner Wheel dial themes; their ENCYCLOPEDIA topics stay the
    # emblem pages (the later family pass overwrites the weekday
    # topics built from these titles — deliberate).
    "virtues": "Virtues",
    "sins": "Sins",
    "moods": "Moods",
}

# The Weekday submenu GROUPS (owner menu rework 2026-07-13): kinship
# submenus instead of the flat theme list. Planets nests its SIGN look
# as a second option (planet_signs stays its own theme underneath);
# The Inner Wheel (Virtues/Sins/Moods) joins once those themes gain
# their dial texts.
WEEKDAY_MENU_GROUPS = (
    ("Ancient Gods", ("egypt", "greek", "norse", "slavic")),
    ("Society", ("profession", "religion", "religion_alt")),
    # The Scripture family (owner 2026-07-14).
    ("Scripture", ("bible", "bible2", "bible_dark")),
    ("Animals", ("wolf", "elephant", "bee")),
    # The emblem families on the dial (owner 2026-07-14).
    ("The Inner Wheel", ("virtues", "sins", "moods")),
    ("Arcana", ("planets", "alchemy", "japan", "cosmos")),
)

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
        # Owner defaults 2026-07-12: sunlight 36%, twilight 12%.
        day_alpha=0.36,
        twilight_alpha=0.12,
        # TWO independent radii for fine tuning (fractions of the dial
        # radius; the ring art's inner edge sits at 0.858):
        umbra_radius_fraction=0.90,     # the gray wheel
        aura_radius_fraction=0.90,      # the colored wedges
    ),
    star=StarSpec(
        day_alpha=1.0,                  # full opacity (owner default 2026-07-12)
        twilight_alpha=0.55,
        border_alpha=0.85,              # colored outlines run the full circle
        border_width_fraction=0.008,
        radius_fraction=0.86,           # star tips touch the ring's inner edge too
    ),
    ring=RingSpec(
        # A face placeholder only — the controller's build_skin ALWAYS
        # overlays the chosen ring preset card (face + letters + letter
        # art) from Database/ring_presets.json at build time.
        asset=RING_FACE_DIR / "domy.png",
        fill="#4A4E57",
        text_color="#F0F0F0",
        letter_color="#E8B84B",
        width_fraction=0.16,
        letters={12: "M", 20: "Y", 0: "Ω", 4: "D"},
    ),
    weekday_set=WeekdaySpec(
        bodies={name: WEEKDAY_ART_DIR / "planets" / "primary" / f"{name}.png" for name in (
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
        moon_asset=WEEKDAY_ART_DIR / "planets" / "primary" / "moon.png",
        moon_lit_color="#E8E4D8",
        moon_dark_color="#2A2D36",
        moon_shadow_alpha=0.82,
        moon_orbit_fraction=0.75,       # rides the same rim as the Earth
        moon_scale=0.08,                # ~72% of the Earth marker (owner spec)
    ),
    hands=HandsSpec(
        # A PLACEHOLDER only — build_skin ALWAYS resolves the chosen
        # hand pack (assets/hands/<pack>/ or a user pack) into a full
        # HandsSpec; these are the CLASSIC pack's values (the owner's
        # PNG exports, every pivot 17 px above the bottom).
        hour=HandSpec(
            asset=paths.assets_dir() / "hands" / "classic" / "hours.png",
            natural_height=246, pivot_y=17,
        ),
        minute=HandSpec(
            asset=paths.assets_dir() / "hands" / "classic" / "minutes.png",
            natural_height=295, pivot_y=17,
        ),
        second=HandSpec(
            asset=paths.assets_dir() / "hands" / "classic" / "seconds.png",
            natural_height=306, pivot_y=17,
        ),
        minute_reach_fraction=HAND_MINUTE_REACH_FRACTION,
        second_reach_fraction=HAND_SECOND_REACH_FRACTION,
    ),
)
