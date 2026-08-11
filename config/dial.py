"""Dial geometry and window sizing — the drawn ring, its jewels,
the crown text arc, hand reach, procedural fallback geometry, subdial
seating and the transparent window's own margin computation.

Layer: config — pure, no Qt, no wall clock.
"""

import math

from config import constants, paths


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
RING_JEWEL_SIZE = 0.105
RING_TEXT_BOX = 0.16                 # square text-layout box
RING_MINUTE_SIZE = 0.05
RING_MINUTE_RADIUS = 0.92            # fraction of the ring inner radius
RING_NUMERAL_MIN_PX = 7              # legibility floors at tiny dial sizes
RING_JEWEL_MIN_PX = 8
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

# THE 360 DAY TICKS' OWN RADIAL HOME, measured on the owner's inner base
# plates (radial alpha sweep of `simple.png`, angles between the 6-degree
# strokes): the one-per-degree tick segments run 0.854 -> 0.889 of the
# plate radius, their free TIPS pointing INWARD at 0.854. These are the
# "mini pointers" of the owner's correction below — every band line and
# marker arrow reasons from these two numbers, never from a re-guess.
RING_INNER_TICK_INNER_FRACTION = 0.854   # the tick TIPS (facing the centre)
RING_INNER_TICK_OUTER_FRACTION = 0.889   # their roots, at the hour band
# The DEEPEST inner-ring content: the five-minute strokes/arrows run
# 0.798 -> 0.888 of the radius (measured on the plates; the same number
# `render.numeral_bands._build_inner`'s occlusion note records) and the
# minute NUMBERS stand over their inner half — so 0.798 is THE LAST
# LINE that cuts NO inner-ring element (owner correction 2026-08-11,
# third round: every band line and both bodies follow the final line
# that slices no inner-ring element — not the tick tips, not the hour
# band edge, both of which earlier re-cuts wrongly used).
RING_INNER_CONTENT_INNER_FRACTION = 0.798

# THE LINE AND THE BODIES (owner corrections 2026-08-10 and 2026-08-11
# — the second round decoded the first: "the top of the pointers" is
# the little ticks' OUTER ROOT, the end of the inner circle where the
# hexagram vertex, the big strokes and the numerals all stop — NOT
# their inward-facing tips, which the first cut used and he rejected;
# this SUPERSEDES the 2026-08-09 "clear orbit lane" clearance): the
# Moon Horizon Band's thread/glow LINE rides
# `RING_INNER_TICK_OUTER_FRACTION` (the tick roots), the 360 little
# pointers hang INWARD from it with their free tips at
# `RING_INNER_TICK_INNER_FRACTION` — and EACH of the Earth and the
# Moon rides so its OWN disc touches the LITTLE POINTERS' line (the
# tips) from inside, per-body tangent, both touching. The
# position-pointer arrow sits BEHIND its body ("IZA NE ISPRED
# ZEMLJE"), bridging the tick zone: base hidden under the disc, tip on
# the thread line at the roots. Pinned by
# `tests/test_earth_moon_orbit.py`.

# THE STAR/POLYGON TIP (moved here from `config.defaults`'s DEFAULT_SKIN
# literal, owner correction round 2026-08-09 — the orbit lane needs to
# reason about it, and `config.dial` may not import `config.defaults`,
# the direction the flow already runs): where the pointer's own star or
# polygon shape's OUTER vertices sit, a fraction of the dial radius —
# "star tips touch the ring's inner edge too" (`skins.manifest.StarSpec.
# radius_fraction`'s own docstring). `config.defaults.DEFAULT_SKIN`
# reads this constant instead of repeating the literal.
STAR_RADIUS_FRACTION = 0.86

def earth_moon_orbit_fraction(ring_size: float, half_size: float) -> float:
    """One marker's orbit radius — TANGENT TO THE LITTLE POINTERS' LINE
    (owner corrections 2026-08-10/11, see THE LINE AND THE BODIES
    above; this retired the 2026-08-09 clearance lane and its
    hexagram-apothem floor). `half_size` is THIS body's own current
    half-size (its scale slider included) — each body is tangent to
    THE LAST LINE (`RING_INNER_CONTENT_INNER_FRACTION`, owner third
    round 2026-08-11: the body must never slice ANY inner-ring element,
    so it stays outside the band entirely), and the Earth and the Moon
    ride slightly different radii so BOTH touch. The position-pointer
    arrow bridges from here across the band to the small ticks' tips."""
    line_edge = RING_INNER_CONTENT_INNER_FRACTION * interior_scale(ring_size)
    return line_edge - half_size


# THE POSITION POINTER (owner feature 2026-08-09, Settings ▸ Earth, off
# by default): a small triangle straddling each marker's OWN edge at its
# exact angle — the same triangle language `render.calendar_mount.
# calendar_day_arrow` uses for the Almanac's day mark — so a small
# Earth/Moon marker stays easy to find. Drawn OVER the body itself
# (visual proof correction round 2026-08-09 — the first cut drew it
# UNDER the body, so only a thin sliver of tip peeked past the sphere's
# own edge and read as a rendering glitch rather than an intentional
# marker). BEHIND THE BODY, TIP ON THE LINE (owner corrections
# 2026-08-10/11 — "IZA NE ISPRED ZEMLJE, Z INDEX MANJI": the arrow is
# drawn BEFORE the body, its outward tip flush with the tick-root line
# the body itself touches, so only its flanks show beside the disc's
# curve; and every dimension is PROPORTIONAL to the body's own
# half-size — the fixed-size first cut looked enormous next to a
# small-scaled body, his "strelice i trougao preveliki". The gem is
# the opposite correction: "DIJAMANT PREMALI" — proportional now too,
# still longer than wide with NO hairline to the body.
# `MARKER_POINTER_OUTLINE_RGBA` (the white `palette.MARKER_BORDER_RGBA`
# stroke, the SAME outline the Earth's procedural disc wears) stays —
# it is what makes the shape read against any wedge.
MARKER_POINTER_LENGTH_RATIO = 0.80    # triangle depth, of the body's half-size
MARKER_POINTER_WIDTH_RATIO = 0.45     # its tangential half-width, of the half-size
MARKER_POINTER_OUTLINE_WIDTH_FRACTION = 0.0025   # stroke width, of the dial radius
MARKER_GEM_LENGTH_RATIO = 0.55        # gem HALF-length, of the body's half-size
MARKER_GEM_WIDTH_RATIO = 0.45         # its tangential half-width, OF that length

# THE CROSSING (owner verdict 2026-08-10, `constants.MOON_TRANSIT_STYLES`)
# — how far each non-overlapping style moves the Moon while it meets the
# Earth on the shared lane, scaled by `render.daylight.
# moon_transit_nearness` (0 clear, 1 concentric). "lane_split" eases the
# Moon INWARD by this fraction of the dial radius: inward, because the
# outward direction is the ring band's own lane and belongs to the
# numerals. "shrink_pass" instead takes this fraction off the Moon's
# size at the deepest point — enough that it reads as "in front and
# further", not so much that it becomes a dot.
MOON_LANE_SPLIT_FRACTION = 0.085
MOON_SHRINK_PASS_DEPTH = 0.35


# THE AURA COLORLESS MENU's "follow" option (Watch Face Phase 4, R-23):
# the brightness fed to `render.painting.tinted_gray` so "follow ring"
# reads as the tint's OWN near-white end rather than the tint itself —
# high enough that every preset still reads recognizably pale.
AURA_OFF_FOLLOW_VALUE = 224


# --- Ring faces -------------------------------------------------------------------
# Ring PRESETS are data (Database/ring_presets.json + the user's custom
# cards in settings, loaded by data/rings.py — THE COMPOSITIONAL RING
# MODEL, owner decree 2026-08-05): a card is {name, outer, letters};
# `outer` names a `constants.RING_OUTERS` entry directly, whose file
# lives under `RING_OUTER_ART_DIR` below.
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

# The owner's GOLD plate library — latin, greek, the ten digits, the
# typeable symbols and the picked-only emblems — overlaid on the ring
# by calculation so the tint never touches it; every other finish is
# derived from the gold master at load. NOT under `ring/` (owner
# 2026-08-07: "nije mu to mesto jer nisu oni samo za ring") — the ring
# jewels, all four crown surfaces and, planned, the subdial read the
# SAME plates. Its glyph table is `constants.LETTER_PLATE_FILES`; the
# resolver that turns a glyph into a drawable gold master (aliases,
# composed two-digit numbers) is `render.letter_plates`.
LETTER_ART_DIR = paths.assets_dir() / "instrument" / "letters"
# A two-digit hour seat (12, 15, 16, 18, 20, 21) has NO plate of its
# own any more (owner 2026-08-07: "izbacio sam sve one kompleksne
# brojeve koje kombinuju 1 ili više osnovnih") — `render.letter_plates`
# composes it from the digit masters.
#
# THE INK GAP, and it is SOLVED from the owner's own retired composite
# rather than guessed. `20.png` was 730 x 512; at this clearance between
# the 2's and the 0's nearest INK, `_ink_advance` reproduces that width
# to the pixel. The first attempt used the 8 px of fully-transparent
# COLUMNS visible in that file, which is a different quantity — it is
# what two digits that never reach toward each other happen to leave,
# and applying it as a BOX gap gave every pair a different optical
# spacing (measured: 8 px of real clearance on "12" against 37 on "20").
# That is what an independent grader saw as "the 15's plates touching".
# One clearance for every pair is what "one style" means.
LETTER_COMPOSE_INK_GAP_FRACTION = 37 / 512
# Bump to re-compose every cached number after a change to the
# composition itself.
LETTER_COMPOSE_VERSION = 3
RING_JEWEL_RADIUS_FRACTION = 0.943  # letter center = the middle of the OUTER
                                     # hour band alone (owner spec; measured
                                     # 0.888–0.998 on both ring faces — the
                                     # seconds scale is NOT part of the band)
RING_JEWEL_ART_SCALE = 0.075        # letter height, of the dial diameter
                                     # (deliberate slight oversize — owner
                                     # default; the Settings slider scales it)
# Letter shadow (owner spec): a tight, intense dark halo on all sides —
# a gradient border, as if lit from above. Stamped as N offset copies of
# the blackened letter at `alpha` each, `radius` of the letter height.
RING_JEWEL_SHADOW_RADIUS = 0.05     # of the letter height
RING_JEWEL_SHADOW_ALPHA = 0.55      # per stamp AT THE FLOOR sample count
                                     # (`RING_JEWEL_SHADOW_SAMPLES`) — the
                                     # per-stamp alpha actually drawn is
                                     # renormalized when more samples are
                                     # added (`render.layers.ring.
                                     # _normalized_shadow_alpha`) so the
                                     # composited darkness stays this look
                                     # at any sample count.
RING_JEWEL_SHADOW_SAMPLES = 8       # offsets around the circle — the
                                     # FLOOR: today's look at ordinary
                                     # dial sizes, never fewer
# PIXELATION FIX (1440p owner bug, 2026-08-06): at large dial sizes the
# fixed 8 stamps separate into a scalloped, jagged ring because their
# PIXEL spacing grows with the dial's pixel radius while the sample
# count stayed constant. `render.layers.ring._shadow_sample_count`
# grows the sample count so adjacent stamps stay under this many
# device pixels apart along the stamp circle (built once per skin/size/
# DPI change, like the rest of this STATIC layer — never per frame).
RING_JEWEL_SHADOW_MAX_GAP_PX = 1.0

# The outer GREAT SEAL CROWN TEXT ARC (TASK 1, owner "može radi" 2026-07-19,
# CANON.md §The Banknote; corrected MOTO-FIX round, owner correction
# 2026-07-19, the dollar's Great Seal reference image): curved text
# OUTSIDE the ring band, reusing the SAME letter-art library/finish/
# shadow stamp as the ring's own six jewels
# (`render.layers.ring.RingLayer._draw_ring_glyph`), just smaller and
# further out — decorative inscription, not the primary Dollar seats.
# ONE SHARED RADIUS (MOTO-FIX round): the first round's design had both
# crown texts' pinned jewels land on the SAME angle (O at noon, S at 16h),
# needing two concentric radii to coexist; the corrected layout puts
# ANNUIT COEPTIS over the TOP and NOVUS ORDO SECLORUM under the BOTTOM
# instead — angularly DISJOINT arcs that never collide, so both now
# draw at this one radius (`core/__about/crown_text.md`'s Design Decisions).
RING_CROWN_TEXT_SIZE = 0.0375             # crown text letter height, of the dial
                                     # diameter — half RING_JEWEL_ART_SCALE
                                     # (decorative, smaller than the six
                                     # primary banknote jewels)
# The WORD-HOVER band (owner 2026-07-27, "HOVER tekst osim na slova
# treba i na reči"): how far above/below the crown text radius (fraction of
# the dial RADIUS) a hover still answers as an arc WORD — the crown text
# letter height is 2*RING_CROWN_TEXT_SIZE of the radius (0.075), so ±0.05
# covers the glyphs with a little air.
RING_CROWN_TEXT_HOVER_HALF_FRACTION = 0.05
RING_CROWN_TEXT_RADIUS_FRACTION = 1.13    # BOTH arcs (MOTO-FIX round) — clears
                                     # the primary letters' own max reach
                                     # (~1.0255 with shadow at scale 1.0)
                                     # AND the ring-letter hover ceiling
                                     # (GREETINGS_JEWEL_OUTER_FRACTION,
                                     # 1.08) with margin

# ANNUIT WORD-GAP round (owner correction 2026-07-19, third batch): the
# TIGHT per-character step every crown text letter now advances at, derived
# from NOVUS ORDO SECLORUM's own pin geometry (two 60 deg segments over
# 9 characters each = 6.667 deg/char). A crown text pinned only at its first
# and last character (ANNUIT COEPTIS) advances every letter at this
# fixed step from BOTH pins inward (`core.crown_text._tight_two_pin_angles`)
# instead of spreading the whole span evenly — the owner's "too wide"
# complaint — letting the single interior word gap absorb whatever
# angular slack remains, so the eye/G area breathes like the Great
# Seal's own gap over the eye.
RING_CROWN_TEXT_LETTER_STEP_DEG = 60.0 / 9

# --- Ring OUTER/INNER composition (owner decree 2026-08-05) -----------------------
# THE COMPOSITIONAL RING MODEL: a ring is ALWAYS the composition of an
# OUTER band (`RING_OUTER_ART_DIR`, `constants.RING_OUTERS[name]["file"]`
# — the hour-tick band with the preset's own empty jewel fields) + an
# INNER band (`RING_INNER_ART_DIR`, `constants.RING_INNERS` — the
# minute-track band, independently tintable via `ring_tint_inner`) +
# the jewels + an optional crown-text crown text arc. There is no single
# monolithic plate and no procedural fallback any more — the old
# `domy.png`/`morph.png`/`hexagram.png` faces are DELETED;
# `render.layers.ring.RingLayer.paint` always composes both bands.
RING_OUTER_ART_DIR = paths.assets_dir() / "instrument" / "ring" / "outter"
RING_INNER_ART_DIR = paths.assets_dir() / "instrument" / "ring" / "inner"

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
# seat — a circle CENTERED on the Omega jewel position (180°, the ring
# jewel band) with a radius covering the whole jewel cell. The old
# narrow annular wedge only answered on the jewel glyph itself (its
# lower part), so the double-click kept missing; the round area is
# derived from the ring-jewel art size (a letter spans ~2× its
# ART_SCALE of the radius, so 1.5× the ART_SCALE comfortably covers the
# cell and its corners without reaching the 22h/2h numerals). Tunable.
OMEGA_HIT_RADIUS_FRACTION = RING_JEWEL_ART_SCALE * 1.5


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

GLOW_RING_RADIUS_FRACTION = RING_JEWEL_RADIUS_FRACTION  # ring band centerline


# --- The dial NUMERALS (research/hour_numerals.md) ---------------------------------
# THE LIVE NUMERAL BANDS (ring_rework.md §2): the two numeral bands are
# RENDERED — at startup and on every settings change, never per frame —
# rather than shipped as art, because the outer band ROTATES in the
# Heliocentric mode and a numeral's seat belongs to the ANGLE it lands
# on, not to the hour it carries. `core.numerals` owns the mathematics,
# `render/numeral_*.py` the paint; everything tunable is here.
#
# THE FIDELITY RULING (owner correction 2026-08-06, ring_rework.md §2):
# the live band COMPOSES the whole ring — it never paints over a printed
# plate's own content, and the style it draws in is not a designer's
# choice but a MEASUREMENT of the owner's own art. Every geometry
# number in this section that carries a "measured" note was read off
# `assets/instrument/ring/outter/*.png` and
# `assets/instrument/ring/inner/*.png` at their native 3600 px
# (`tests/test_numerals.py` re-measures the plates and fails if a
# constant drifts away from them).

NUMERAL_HOUR_COUNT = 24              # 0 .. 23, bare labels, no leading zero
NUMERAL_HOUR_STEP_DEG = 15.0         # deg(h) = (h - 12) * 15
NUMERAL_MINUTE_STEP_DEG = 6.0        # one minute / one second mark
NUMERAL_MINUTE_LABEL_STEP = 5        # the inner band labels every 5th minute

# One "unit" is the ledger's own length unit (§8: "lengths are in the
# same units as the numeral's own size, so a setting survives any change
# of dial resolution"). This is what one unit is worth as a fraction of
# the DIAL DIAMETER.
NUMERAL_UNIT_FRACTION = 0.040 / 90.0

# The band the OUTER numerals stand in — its centreline and its width, as
# fractions of the dial RADIUS. The centreline is the hour band's own
# middle, the same measurement `RING_JEWEL_RADIUS_FRACTION` names; the
# width is what the "Outer ring size" setting scales (a multiplier, 1.0 =
# the measured band). MEASURED on the owner's outer plates: the metal
# runs 0.8858 -> 0.9998 of the radius on all six, so the centreline is
# 0.9428 (RING_JEWEL_RADIUS_FRACTION's own 0.943) and the width 0.114.
NUMERAL_OUTER_RADIUS_FRACTION = RING_JEWEL_RADIUS_FRACTION


def outer_band_edges(ring_size: float) -> tuple[float, float]:
    """THE INWARD-GROWTH LAW's pure geometry (owner verdict 2026-08-09;
    lives HERE beside its constants so `defaults` can measure the
    window margin without touching render — the one-way flow law).
    Above 1.0 the OUTER edge is pinned at the measured rim and the
    multiplier moves the INNER edge toward the centre; at and below
    1.0 the measured band's INNER edge stays fixed and the outer edge
    comes inward — every release's own behavior, kept (the opus
    verification caught an unconditional pin dragging a THIN band
    outward to the rim and clipping its numerals)."""
    width = NUMERAL_OUTER_BAND_WIDTH_FRACTION
    inner_default = NUMERAL_OUTER_RADIUS_FRACTION - width / 2.0
    if ring_size <= 1.0:
        return inner_default, inner_default + width * ring_size
    outer_edge = inner_default + width
    return outer_edge - width * ring_size, outer_edge


def outer_centreline(ring_size: float) -> float:
    """The OUTER band's centreline for `ring_size` — the midpoint of
    `outer_band_edges`, `NUMERAL_OUTER_RADIUS_FRACTION` exactly at
    1.0."""
    inner_edge, outer_edge = outer_band_edges(ring_size)
    return (inner_edge + outer_edge) / 2.0


def band_ride_shift(ring_size: float) -> float:
    """How far a BAND-RIDING member's radius fraction moves with the
    band's centreline (Earth/Moon markers, the jewel hover disc) —
    0.0 at `ring_size` <= 1.0."""
    if ring_size <= 1.0:
        return 0.0
    return outer_centreline(ring_size) - outer_centreline(1.0)


def interior_scale(ring_size: float) -> float:
    """How much the world INSIDE the hour band yields when the band
    grows inward — new inner edge over the default one; 1.0 at and
    below `ring_size` 1.0 (a thinner band leaves the interior exactly
    where the measured art expects it)."""
    if ring_size <= 1.0:
        return 1.0
    default_inner, _outer = outer_band_edges(1.0)
    new_inner, _outer = outer_band_edges(ring_size)
    return max(0.1, new_inner / default_inner)
NUMERAL_OUTER_BAND_WIDTH_FRACTION = 0.114
NUMERAL_OUTER_RING_SIZE_RANGE = (0.5, 2.0)
NUMERAL_OUTER_RING_SIZE_DEFAULT = 1.0
# THE BAND'S OWN BASE (the Fidelity Ruling's first law): the engine draws
# the metal the numerals stand on instead of blitting a plate that already
# carries printed numerals under them. MEASURED: a FLAT #656A70
# (`palette.NUMERAL_RING_GROUND`, 83.7% of every plate's band pixels is
# that exact value — there is no gradient and no bevel to reproduce) with
# a hard black rim on its OUTER edge alone.
NUMERAL_BAND_RIM_FRACTION = 0.0035   # rim width, of the dial radius

# The INNER band's ONLY live geometry: the minute numerals' own
# centreline, a fraction of the dial radius. Everything else on that band
# — the 360 day ticks, the 60 minute strokes and the quarter/octa ARROWS
# — is the owner's own art, blitted from `RING_INNER_COMPOSITION`'s
# numberless base plate (the Fidelity Ruling's second law: his art is
# used directly wherever it exists), and a number OCCLUDES the inner half
# of the five-minute stroke it stands on exactly as it does in his own
# numbered plates, which needs no geometry here at all.
MINUTES_RADIUS_FRACTION = 0.8215

# THE INNER BAND'S COMPOSITION (the Fidelity Ruling): every shipped inner
# variant is exactly ONE numberless base plate of the owner's plus a set
# of five-minute seats that carry a NUMBER — which is precisely how his
# numbered plates were drawn (`seconds.png` IS `simple_point.png` with
# the numbers set into it). The engine blits the base and composes the
# numbers live, so the user's font/size pick changes WHAT stands in the
# seat and never HOW the band looks. A seat that carries an arrow in the
# base never carries a number: one content per seat, never stacked.
RING_INNER_COMPOSITION = {
    "simple": {"base": "simple", "numbers": ()},
    "simple_point": {"base": "simple_point", "numbers": ()},
    "simple_cross": {"base": "simple_cross", "numbers": ()},
    "simple_octa": {"base": "simple_octa", "numbers": ()},
    "seconds": {
        "base": "simple_point",
        "numbers": (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55),
    },
    "seconds_cross": {
        "base": "simple_cross",
        "numbers": (5, 10, 20, 25, 35, 40, 50, 55),
    },
    "seconds_octa": {
        "base": "simple_octa",
        "numbers": (5, 10, 20, 25, 35, 40, 50, 55),
    },
    "simple_seconds": {"base": "simple_point", "numbers": (15, 30, 45)},
}

# THE FACES (ledger §7) — roster label -> (Qt family, Qt style). Qt sees a
# family plus a style where a designer says "Bahnschrift Bold", so this
# table is the ONE mapping (`render.numeral_fonts`); no caller builds a
# QFont from a roster label itself.
#
# VERIFIED ON THIS MACHINE 2026-08-06 (render.numeral_fonts.glyph_coverage,
# by GLYPH GEOMETRY, not by cmap): the recovered `Bernard MT Condensed`
# draws all ten digits perfectly and draws NOTHING AT ALL for ':' '.' 'h'
# 'm' 'i' — zero-area outlines with non-zero advances, while
# QRawFont.supportsCharacter answers True for every one of them. It
# therefore stays the hour band's default (digits are the hour band's
# whole job) and is NOT the crown's default, since the crown needs the
# colon and the h/min cut. `Eras Bold ITC` covers every glyph.
NUMERAL_OUTER_FACES = {
    "Bernard MT Condensed": ("Bernard MT Condensed", ""),
    "Bahnschrift Bold": ("Bahnschrift", "Bold"),
    "Poppins SemiBold": ("Poppins", "SemiBold"),
    "Poppins Black": ("Poppins", "Black"),
    "Roboto Bold": ("Roboto", "Bold"),
    "Impact": ("Impact", ""),
    "Palatino Linotype Bold": ("Palatino Linotype", "Bold"),
}
MINUTES_FACES = {
    "Eras Bold ITC": ("Eras Bold ITC", ""),
    "Unispace": ("Unispace", "Bold"),
    "Poppins Black": ("Poppins", "Black"),
    "Arial Black": ("Arial", "Black"),
    "Segoe UI Black": ("Segoe UI", "Black"),
}
NUMERAL_OUTER_FACE_DEFAULT = "Bernard MT Condensed"
MINUTES_FACE_DEFAULT = "Eras Bold ITC"
# The CROWN has NO face (THE ONE PLATE LAW, owner decree 2026-08-07):
# it draws the owner's letter plates like the jewels and the crown text
# beside it, so the pick that used to stand here — and the whole
# coverage worry behind it — went with the font.
# The size the coverage proof rasterizes/measures at — large enough that a
# hairline glyph still reports a non-zero outline, small enough to be free.
NUMERAL_COVERAGE_PROBE_PX = 80

# THE SETTLED SETTINGS (ledger §8). The DEFAULTS are the owner's own art
# (the Fidelity Ruling): size, border and the shadow below were fitted
# against `outter/full.png` glyph by glyph, not chosen — the ledger's
# first-pass guesses (size 90, border 0) drew a band visibly lighter and
# thinner than the plates they replace, and an odd numeral at border 0
# has no white outline at all, which is the single loudest difference
# between his art and wave 3's screen. The RANGES are untouched, so a
# user who wants the recessed look still has it.
NUMERAL_SEATINGS = ("arc", "upright")
NUMERAL_SEATING_DEFAULT = "arc"
NUMERAL_RELIEF_STYLES = ("cast", "extrude", "emboss")
NUMERAL_RELIEF_DEFAULT = "extrude"
NUMERAL_LIGHTS = ("radial", "fixed")
NUMERAL_LIGHT_DEFAULT = "radial"
NUMERAL_SIZE_RANGE = (40, 140)
NUMERAL_OUTER_SIZE_DEFAULT = 124     # measured: cap height 0.0436 of the
                                     # dial diameter on every outer plate
MINUTES_SIZE_DEFAULT = 84     # measured against inner/seconds.png
NUMERAL_BORDER_RANGE = (0.0, 16.0)
NUMERAL_BORDER_DEFAULT = 4.0         # measured: his odd numerals' white ring
                                     # is 2.4 px mean-thick at 3600 px; this
                                     # pen reproduces it to within 2%
NUMERAL_DEPTH_RANGE = (0.0, 16.0)
NUMERAL_DEPTH_DEFAULT = 3.0          # the ledger's own SETTLED depth, kept:
                                     # the directional relief lies INSIDE the
                                     # measured halo and only emerges when the
                                     # user asks for a deeper one
NUMERAL_DARKNESS_RANGE = (0.0, 1.0)
NUMERAL_DARKNESS_DEFAULT = 1.0
NUMERAL_CONTACT_BLUR_RANGE = (0.0, 8.0)
NUMERAL_CONTACT_BLUR_DEFAULT = 2.0   # measured: the halo's own soft edge
NUMERAL_EMBOSS_LIT_FACTOR = -0.6     # ledger §5: the lit rim, the other way

# THE OUTER BAND'S BLACK HALO — the thing the owner's numerals actually
# wear. MEASURED across his eight upright-ish even seats: the black
# reaches 11.1 px beyond the glyph outward and 11.3 px inward at 3600 px
# — SYMMETRIC, so his relief is an outer glow and not a cast light — and
# covers 0.53 of the glyph's own area. A blurred silhouette alone cannot
# make that plateau (a blur wide enough to reach 11 px is smoke at its
# edge), so the halo is a DILATION: the glyph stroked with a pen this
# many units wide under everything else, `NUMERAL_CONTACT_BLUR_DEFAULT`
# softening its edge. This is the band's own style, not a user setting;
# the DEPTH setting's directional relief is drawn over it and stays
# inside it until the user raises depth past this reach.
NUMERAL_SHADOW_REACH_UNITS = 2.8     # beyond the border, in numeral units

# The INNER band's own relief is not the outer's black shadow but a WHITE
# GLOW (ring_rework §2) — small radius, strong intensity, a border+glow
# and never a diffuse halo — worn by its numerals AND its stubs alike.
NUMERAL_GLOW_RADIUS_UNITS = 4.0      # in numeral units, like every length
NUMERAL_GLOW_PASSES = 3              # composited copies = the intensity
NUMERAL_GLOW_BORDER_UNITS = 9.0      # the crisp white border under the glow —
                                     # MEASURED: thick enough that two digits'
                                     # rims MERGE the way his do, so no minute
                                     # stroke shows through the gap between them

# THE LIVE CROWN (ring_rework §3): the time in the arc, rendered as
# exactly the digits-and-colon set ONCE per settings change and merely
# re-composed once a minute. `zone` None is this watch's own civil time;
# a named zone is resolved through tzdata in core.clock_state.
CROWN_TIME_FORMATS = ("hh:mm", "12h 35min")
CROWN_TIME_FORMAT_DEFAULT = "hh:mm"
CROWN_SMALL_CUT_FRACTION = 0.62      # the h/min cut, of the digit size
CROWN_RADIUS_FRACTION = RING_CROWN_TEXT_RADIUS_FRACTION
# ONE CROWN SIZE LAW (owner defect 2026-08-07 — the live time crown read
# "microscopic, scattered" beside NON NOBIS DOMINE): the live crown's
# glyph BOX is `RING_CROWN_TEXT_SIZE` exactly like the static arc's, so
# `CROWN_NUMERAL_SIZE_FRACTION` (which sized it off the HOUR BAND
# instead) is retired. These two constants are what turn that shared box
# into a drawn glyph.
#
# Every glyph is a PLATE scaled to that box by its height, exactly as
# `RingLayer._draw_ring_glyph` scales a jewel — so a 3 and an N read as
# one family because they ARE one family. The per-face ink fitting that
# used to live here (CROWN_PLATE_INK_FRACTION / CROWN_FIT_PROBE_PX) is
# retired with the font it existed to size.
# ADVANCE: the crown lays glyphs out by their OWN ink width plus this
# much tracking (of the glyph box height) — never a fixed angular step,
# which spaced a 0.22-wide colon exactly as far as a 1.45-wide M and was
# half of what the owner saw as "scattered". MEASURED to reproduce
# today's static-arc spacing on average: the static step
# (RING_CROWN_TEXT_LETTER_STEP_DEG at RING_CROWN_TEXT_RADIUS_FRACTION)
# is 1.753 glyph-heights of arc, and the mean letter-plate ink width is
# 1.19 glyph-heights — the difference is the tracking below.
CROWN_TRACKING_FRACTION = 0.56
# `location` (THE RULED LOCATION ARC, owner defect 2026-08-07 — "The
# One's bottom location line does not exist"): the orientation of a
# location arc the PRESET itself owns, drawn whatever the user's own
# per-ring `Settings.ring_crown_location` toggle says. Until this round
# the ledger's "its bottom arc is City, Country" was served only by that
# toggle — which is OFF by default and, when ticked, draws at the TOP,
# straight through the live time. A preset's ruled arc is not a user
# pick, so it lives here; None (the default, every other preset) leaves
# the toggle as the only source, unchanged.
RING_LIVE_CROWN = {
    # The One — the top arc keeps this watch's OWN civil time; the bottom
    # arc names the city and country the watch is set to.
    "The One": {"zone": None, "orientation": "top", "location": "bottom"},
    # Templar — the top arc keeps the hour of JERUSALEM; its bottom arc,
    # NON NOBIS DOMINE, is a static plate arc declared in the preset card.
    "Templar": {"zone": "Asia/Jerusalem", "orientation": "top", "location": None},
}
CROWN_TIME_ZONES = {
    entry["zone"] or "local": entry["zone"]
    for entry in RING_LIVE_CROWN.values()
}
# THE LIVE CROWN'S OWN HOVER (ring_rework §3, owner ruling 2026-08-06 —
# "the live time/location crowns say whose hour they keep"): the live
# glyphs (`render.layers.numerals.LiveCrownLayer`) carry no `crown_text`
# card entry to hang a `reading` on, so their hover text lives here,
# read by `render.compositor._live_crown_tooltip`. Verbatim from
# research/crown_content.md §1.
RING_LIVE_CROWN_READING = {
    "The One": {
        "title": "the civil hour of your own city",
        "text": (
            "the top arc reads whatever a clock on your own wall would "
            "read, in your own timezone — The One is the hour ring, so "
            "its live text is the plainest possible statement of its "
            "doctrine: the wheel telling you what hour it already is."
        ),
    },
    "Templar": {
        "title": "the hour of Jerusalem, the city of the vow",
        "text": (
            "the top arc keeps a second zone regardless of where the "
            "watch itself sits — a knight's watch was always measured "
            "against the city his order swore to, not against wherever "
            "he was standing."
        ),
    },
}
# THE LOCATION ARC's own hover — verbatim from research/crown_content.md
# §1, the counterpart to RING_LIVE_CROWN_READING above. Stated ONCE here
# (Rule #5) and read by BOTH the preset's ruled bottom arc and the user's
# own per-ring Location toggle in `app.controller._compose_skin`; before
# the 2026-08-07 round it was a dict literal inlined in that one branch,
# so the ruled arc would have had to copy it.
RING_LIVE_CROWN_LOCATION_READING = {
    "title": "City, Country",
    "text": (
        "the bottom arc names the city and country the watch is set "
        "to: the counterpart to the live hour above it — WHERE anchors "
        "WHEN, the two lines that make a clock a fact about a specific "
        "place rather than an abstraction."
    ),
}
# Generous half-angle (Rule #7 — no per-glyph geometry solved for text
# that is rasterized fresh every minute): comfortably covers the widest
# live format ("12h 35min", CROWN_TIME_FORMATS) at the crown texts' own
# fixed per-glyph step.
RING_LIVE_CROWN_HOVER_HALF_DEG = RING_CROWN_TEXT_LETTER_STEP_DEG * 6.0

# THE ONE COPY RULE's ceiling on the process-wide plate cache
# (`render.numeral_bands._PLATES`). A plate's key carries the band's
# ROTATION, and in the Heliocentric mode that rotation changes with the
# solar offset — i.e. once a DAY, twice with the night phase. Without a
# ceiling a watch left running for a year would hold a year of plates;
# with it the cache keeps the working set (a couple of watches x two
# phases x a transient size) and drops the oldest beyond it.
NUMERAL_PLATE_CACHE_MAX = 16

# --- THE TWO WORLD-MODES (research/ring_rework.md §1) ------------------------------
# Which of the two turns: the sky, or the world. GEOCENTRIC is the dial
# every release before this one drew — the observer stands still and the
# sun travels, so the star/pointer rotates toward true solar noon while
# the hour band and every numeral stay fixed, 12 always on top.
# HELIOCENTRIC stands the star still and turns the WORLD beneath it: the
# outer band, the jewels, the crown text, the aura and umbra, the
# weekday seats, the Earth and Moon markers and the hour hand all ride
# ONE world offset — and the whole dial turns over at night.
#
# Solar Rotation stays its OWN switch: it says whether the solar part of
# that offset is taken at all, in either mode. `core.world` owns the
# mathematics; no other module may name these strings.
WORLD_MODES = ("geocentric", "heliocentric")
WORLD_MODE_DEFAULT = "geocentric"
WORLD_MODE_LABELS = {
    "geocentric": "Geocentric (Ptolemy)",
    "heliocentric": "Heliocentric (Copernicus)",
}
# THE NIGHT INVERSION: night is daylight moved half a circle — 0h stands
# where 12 stood, noon at the bottom, every glyph re-seated readably at
# its new angle by the seating law.
WORLD_NIGHT_PHASE_DEG = 180.0
# THE FLIP. A GENUINE transition (a real sunset, a real sunrise) turns
# the world through one short eased move. A clock correction is NOT a
# transition and NOT a new day (owner bug 2026-08-06) — it snaps.
WORLD_FLIP_DURATION_S = 1.5
WORLD_FLIP_FRAME_MS = 16             # ~60 fps, armed for the move alone
