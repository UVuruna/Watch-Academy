"""Dial geometry and window sizing — the drawn ring, its letters,
the motto arc, hand reach, procedural fallback geometry, subdial
seating and the transparent window's own margin computation.

Layer: config — pure, no Qt, no wall clock.
"""

from config import paths


# --- Window ------------------------------------------------------------------
DEFAULT_DIAL_DIAMETER = 720          # logical px, before DPI scaling
                                     # (owner install-default list 2026-07-12)
MIN_DIAL_DIAMETER = 120
MAX_DIAL_DIAMETER = 2000             # roomy above the largest preset (1440)
SIZE_PRESETS = (360, 540, 720, 1080, 1440)   # owner spec (FINAL.txt #3)
# The compact SIZE slider living in the right-click menu itself (owner
# ROADMAP 15h item 12): coarse is fine — fine tuning stays in Settings —
# so a wide step and a narrow on-screen width are deliberate; it applies
# ONLY on release (never mid-drag).
MENU_SIZE_SLIDER_STEP = 10
MENU_SIZE_SLIDER_WIDTH_PX = 130

# Dials at or above this diameter write the date on the Earth marker;
# the FULL weekday name needs more room and appears only from the largest
# preset (owner: at 540 the full name is too small — keep the short one).
# Below the full-name threshold the markers get hover tooltips instead.
FULL_TEXT_MIN_DIAMETER = 540
WEEKDAY_FULL_NAME_MIN_DIAMETER = 720
EARTH_DATE_TEXT_SIZE = 0.30          # fraction of the marker size

LABEL_OUTLINE_WIDTH = 0.05           # fraction of the font pixel size

# Watchdog delay for undoing a spontaneous (OS-initiated) hide/minimize.
# NOTE, verified on Windows 11 24H2: Win+D does NOT hide or minimize this
# window (no Qt events arrive) — it raises the desktop layer above every
# window (even TOPMOST cannot pierce it), and the widget returns by itself
# the moment Show Desktop mode ends. The watchdog therefore only covers
# other shell actions that genuinely hide/minimize; true visibility DURING
# Show Desktop requires the WorkerW glue mode (optional, M4).
WATCHDOG_RESHOW_MS = 200


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

# ONE on-dial NAME-label cap, shared by the weekday bodies AND the
# archetype figures (owner ROADMAP 15h item 4b, 2026-07-18): both paths
# fit text to the available width (measured, never guessed) — without a
# ceiling a SHORT name (e.g. "TUE") inflates far past a LONG one (e.g.
# "Wednesday") at the same spot. Reasoned from the current 720-dial
# short-weekday "TUE" look (~40 px at the default skin) — a flat pixel
# ceiling on purpose, symmetric with BODY_LABEL_MIN_PX's flat floor
# above, not a fraction of the dial (a giant dial must not grow giant
# single-word labels either). The two-line WRAP the owner asked for on
# 2026-07-18 was REVOKED the same day (Session 21-C, his slika: a huge
# "Youth" beside a tiny "Childhood" reads ugly) — replaced by the
# SET-UNIFORM law: every name sharing a ring wears the size of the
# SMALLEST fitted member (`render.weekday_body.weekday_label_set_px` /
# `archetype_label_set_px`), so no per-line offset constant is needed.
NAME_LABEL_MAX_PX = 40
NAME_LABEL_WIDTH_FRACTION = 0.92     # of the available width (arm/body)
MARKER_BORDER_WIDTH = 0.05           # fraction of the marker size

# --- Moon/Earth rim transit (year marker, "both" mode) -------------------------
# The smaller Moon passes OVER the Earth at reduced opacity when they meet
# on the shared rim — like an eclipse (owner decision; both stay visible).
MOON_TRANSIT_OPACITY = 0.5


# --- Ring faces -------------------------------------------------------------------
# Ring PRESETS are data now (Database/ring_presets.json + the user's
# custom cards in settings, loaded by data/rings.py — owner spec): a
# card is {name, positions, letters}; its positions signature picks the
# LAYOUT (constants.RING_LAYOUTS) whose FACE file lives here.
RING_FACE_DIR = paths.assets_dir() / "instrument" / "ring"

RING_TINT_SWATCH_PX = 22             # diameter of one tint circle
RING_TINT_SWATCHES_PER_ROW = 11
PALETTE_SWATCH_PX = 34               # pointer palette circles (owner:


# The ring TICK band hover (owner spec 2026-07-12): any of the 360
# arrows answers with what its ANGLE means on each wheel — the 24h
# time, the year-wheel date and the moon-cycle phase. The band spans
# these dial-radius fractions (the arrows' own zone on the ring art).
TICK_HOVER_INNER_FRACTION = 0.86
TICK_HOVER_OUTER_FRACTION = 0.945

# The owner's GOLD letter art (a full latin/greek library for future
# ring presets), overlaid on the ring by calculation so the tint never
# touches them; the silver look is derived by desaturation at load.
RING_LETTER_ART_DIR = paths.assets_dir() / "instrument" / "ring" / "letters"
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

# The outer GREAT SEAL MOTTO ARC (TASK 1, owner "može radi" 2026-07-19,
# CANON.md §The Banknote; corrected MOTO-FIX round, owner correction
# 2026-07-19, the dollar's Great Seal reference image): curved text
# OUTSIDE the ring band, reusing the SAME letter-art library/finish/
# shadow stamp as the ring's own six letters
# (`render.layers.ring.RingLayer._draw_ring_glyph`), just smaller and
# further out — decorative inscription, not the primary Dollar seats.
# ONE SHARED RADIUS (MOTO-FIX round): the first round's design had both
# mottos' pinned letters land on the SAME angle (O at noon, S at 16h),
# needing two concentric radii to coexist; the corrected layout puts
# ANNUIT COEPTIS over the TOP and NOVUS ORDO SECLORUM under the BOTTOM
# instead — angularly DISJOINT arcs that never collide, so both now
# draw at this one radius (`core.motto.md`'s Design Decisions).
RING_MOTTO_SIZE = 0.0375             # motto letter height, of the dial
                                     # diameter — half RING_LETTER_ART_SCALE
                                     # (decorative, smaller than the six
                                     # primary banknote letters)
# The WORD-HOVER band (owner 2026-07-27, "HOVER tekst osim na slova
# treba i na reči"): how far above/below the motto radius (fraction of
# the dial RADIUS) a hover still answers as an arc WORD — the motto
# letter height is 2*RING_MOTTO_SIZE of the radius (0.075), so ±0.05
# covers the glyphs with a little air.
RING_MOTTO_HOVER_HALF_FRACTION = 0.05
RING_MOTTO_RADIUS_FRACTION = 1.13    # BOTH arcs (MOTO-FIX round) — clears
                                     # the primary letters' own max reach
                                     # (~1.0255 with shadow at scale 1.0)
                                     # AND the ring-letter hover ceiling
                                     # (GREETINGS_LETTER_OUTER_FRACTION,
                                     # 1.08) with margin

# ANNUIT WORD-GAP round (owner correction 2026-07-19, third batch): the
# TIGHT per-character step every motto letter now advances at, derived
# from NOVUS ORDO SECLORUM's own pin geometry (two 60 deg segments over
# 9 characters each = 6.667 deg/char). A motto pinned only at its first
# and last character (ANNUIT COEPTIS) advances every letter at this
# fixed step from BOTH pins inward (`core.motto._tight_two_pin_angles`)
# instead of spreading the whole span evenly — the owner's "too wide"
# complaint — letting the single interior word gap absorb whatever
# angular slack remains, so the eye/G area breathes like the Great
# Seal's own gap over the eye.
RING_MOTTO_LETTER_STEP_DEG = 60.0 / 9

# --- Hand sizing (owner spec 2026-07-12) -------------------------------------------
# Sizing uses TIP-TO-PIVOT lengths only: the seconds tip reaches the
# ring (the end of the 360-dot scale), the minutes tip the minute
# arrows, and the hours follow each pack's own hours/minutes tip
# ratio. Values derived from the CLASSIC look (285/275-unit tips at
# the old shared 0.88 reach) so existing dials render unchanged.
HAND_SECOND_REACH_FRACTION = 0.88
HAND_MINUTE_REACH_FRACTION = 0.849


# THE LEAD LINE's width, a fraction of the dial radius — the twin of
# `palette.ARM_OUTLINE`, worn by every drawn arm and polygon face
# (owner's correction round 2026-07-29).
ARM_OUTLINE_WIDTH = 0.0035               # of the dial radius


# Octa bottom-arm text (time/date/...): sized to span this fraction of
# the slot width (owner: big font, must not overflow the slot).
TIME_TEXT_WIDTH_FRACTION = 0.95


# Omega (24h) double-click (owner 2026-07-16; hit region reworked
# 2026-07-17, slika 9): the hit is the FULL ROUND AREA at the 24h ring
# seat — a circle CENTERED on the Omega letter position (180°, the ring
# letter band) with a radius covering the whole letter cell. The old
# narrow annular wedge only answered on the letter glyph itself (its
# lower part), so the double-click kept missing; the round area is
# derived from the ring-letter art size (a letter spans ~2× its
# ART_SCALE of the radius, so 1.5× the ART_SCALE comfortably covers the
# cell and its corners without reaching the 22h/2h numerals). Tunable.
OMEGA_HIT_RADIUS_FRACTION = RING_LETTER_ART_SCALE * 1.5


# The slot ROUNDEL (owner 2026-07-14, watch-subdial inspiration):
# every TEXT display and the flat astrology art (sign / logo /
# constellation) sit on a subdial; with no art at all the PROCEDURAL
# circle takes over — the ring's own face color, rimmed in the letter
# FINISH metal. Circular plates (medallions, planets, colored badges)
# stay bare.
#
# THE FIVE SETS (owner decree 2026-07-21, Rsub round — retires the
# Rule #19 "one master per source" model this constant used to name):
# the plate is its OWN shared thing now, no longer split by art
# source. Five hand-picked sets live under assets/subdial/ (see
# assets/___assets.md for why that root sits OUTSIDE
# ART_SOURCED_ROOTS): "set1".."set4" are each three hand-drawn
# finishes (`render.asset_variants.subdial_plate_file` returns the matching
# file directly, no recolor); "solo" ships ONE hand-drawn file
# (SUBDIAL_SOLO_FINISH) and the algorithm derives the other two live,
# same recipe as before. The user picks the SET in Settings
# (`Settings.subdial_set`); the letter FINISH (ring_finish, tray Design
# menu) still decides which color draws within it. The SEAT never
# touches the file at all, only the LIVE shadow
# (`render.subdial._draw_subdial_shadow`) — unchanged since Rule #19's
# first enforcement.
SUBDIAL_ROOT_DIR = paths.assets_dir() / "instrument" / "subdial"
SUBDIAL_SOLO_FINISH = "silver"      # the solo set's one hand-drawn file
SLOT_ROUNDEL_BORDER_FRACTION = 0.045     # rim width, of the diameter
SLOT_ROUNDEL_CONTENT_FRACTION = 0.78     # content size inside the rim
# The SMALL-SECONDS complication (owner 2026-07-14): eight tick marks
# just inside the subdial rim — four larger at the cardinals, four
# smaller between — with a soft shadow, never touching the bezel; the
# mini hand's tip stays inside the tick ring. Colors (owner 2026-07-15
# A/B spec): the mini hand always wears the letter FINISH metal over
# its own drop shadow; the ticks are white on the "black" plate style
# and finish-colored on the "theme" style.
SMALL_SECONDS_TICK_OUTER_FRACTION = 0.80
SMALL_SECONDS_TICK_MAJOR_FRACTION = 0.18
SMALL_SECONDS_TICK_MINOR_FRACTION = 0.11
SMALL_SECONDS_HAND_SHADOW_OFFSET_FRACTION = 0.035   # of the subdial radius
SMALL_SECONDS_HAND_SHADOW_OPACITY = 0.55

SUBDIAL_TEXT_SHADOW_OFFSET_FRACTION = 0.06          # of the font pixel size

# Per-pointer SLOT sizing (owner 2026-07-15): the diamonds differ —
# the slim-armed Seasons and Compass carry 125%, the big-diamond
# Trinity/Prism, Aurora and the pointer-off layouts 150%; on the slim
# arms the seat also shifts OUTWARD to the diamond's widest point
# (the between-arm 3h/21h seats stay put).
SLOT_SIZE_BY_POINTER = {
    "trio": 1.50, "hexa": 1.50, "aurora": 1.50,
    # The Rose is three OCTA stars — the octa's own slim-arm sizing.
    "cross": 1.25, "octa": 1.25, "rose": 1.25,
    # Calendar rides the PINNED layout (no arms) — the big-slot size.
    "calendar": 1.50,
}
SLOT_SIZE_PINNED = 1.50
SLOT_SEAT_OUTWARD = {"cross": 1.12, "octa": 1.12, "rose": 1.12}

# The weekday-by-colors unit rides the ROMB CENTER of its diamond (owner
# 2026-07-15): the star tip sits at star.radius_fraction and a diamond's
# diagonals cross at EXACTLY half the tip on every pointer (inner =
# tip / (2 cos half) ⇒ projection = tip/2), so the by-colors body centers
# in the romb at this fraction of the tip — uniformly, whatever the
# pointer (Trinity/Prism/Seasons/Compass all inherit the same position).
WEEKDAY_ROMB_CENTER_OF_TIP = 0.5

SUBDIAL_SHADOW_OFFSET_FRACTION = 0.05    # of the subdial diameter
SUBDIAL_SHADOW_SPREAD = 1.04             # shadow radius vs the plate's


# Transparent margin around the dial INSIDE the window (owner bug
# report: M and Omega touch the window square and their overhang and
# shadow get clipped; owner 2026-07-16: the event glow at the bottom of
# the ring was square-cut too). It is COMPUTED LIVE from the user's
# settings — see dial_window_margin_fraction() in the event-glow section
# below (it needs GLOW_* which are defined there), so any size/hover/
# letter slider re-sizes the window to fit exactly (owner 2026-07-17).

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

GLOW_RING_RADIUS_FRACTION = RING_LETTER_RADIUS_FRACTION  # ring band centerline
