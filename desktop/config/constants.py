"""Product-defining invariants. These values NEVER change at runtime
and are not user-tunable — they define what Watch Academy is.

The WEEKDAY theme tables here are DERIVED: `config.registry` holds one
entry per theme and every table below is computed from it in a single
assignment (owner decree 2026-08-01). The names stay because the
program reads them everywhere; the data has exactly one home.

Tunables (things a developer might reasonably adjust) live in defaults.py.
Win32 API literals live in winapi.py.
"""

from config import registry

# ═══════════════════════════ APP IDENTITY ═══════════════════════════

# ═══════════════════════════ WEEKDAY THEMES ═══════════════════════════
# Weekday body themes (SYMBOLISM.md canon): "planets" uses the skin's
# own weekday unit; the others swap in the owner's themed art from
# assets/skins/domy/weekday/<theme>/ with the canon display names.
WEEKDAY_THEMES = registry.THEMES

# ═══════════════════════════ THEME BLURBS & ARTICLES ═══════════════════════════
# Theme -> symbolism.json blurb key (the encyclopedic text under the
# hexa diamond hover follows the active theme).
WEEKDAY_THEME_BLURBS = registry.BLURBS

# Theme -> symbolism.json article set (the glyph theme shares the
# planet articles — same entities, different art).
WEEKDAY_THEME_ARTICLES = registry.ARTICLES

# ═══════════════════════════ DUALITY SEATING ═══════════════════════════
# The SOUTH SLOT home angle and the Aurora DUAL layout (owner spec
# 2026-07-12): with BOTH the weekday body and the slot on, they flank
# the bottom ±45° — the weekday at 3h on the left, the slot at 21h on
# the right.
#
# STALE-COMMENT CORRECTION (owner 2026-07-27): this comment used to
# claim "the Compass reserves this bottom arm for it". It has not been
# true since the dual-Sunday round — the Compass shows all EIGHT arms,
# and its 24h seat belongs to the SERVANT face of Sunday
# (`render.slot_layout.servant_holds_the_seat`), which is exactly why
# `POINTER_WEEKDAY_SLOTS["octa"]` has no 180° entry. A later change
# moved the truth and left the old sentence standing, and a session
# read it and believed it. When behavior moves, the sentence that
# described the old behavior DIES WITH IT.
SOUTH_SLOT_ANGLE = 180.0
# The SERVANT face's own seat per pointer (owner 2026-07-27): 24h
# everywhere the dual Sunday has always sat, but the ROSE seats him on
# the BLUE arm at 06h — blue is Judas's hue and the servant's, red is
# Lucifer's and the master's, and 6 + 6 + 6 lands the pair on 06h and
# 18h (CUBE.md §The Rose). `render.skin_geometry.servant_seat_angle` is the
# ONE reader (Rule #5); absent = SOUTH_SLOT_ANGLE.
SERVANT_SEAT_ANGLE = {"rose": 270.0}
AURORA_DUAL_WEEKDAY_ANGLE = 225.0    # 3h — bottom left
AURORA_DUAL_SLOT_ANGLE = 135.0       # 21h — bottom right

# THE DUALITY-AXES CONFIG (owner decree 2026-07-28, CUBE.md §The
# Thirteen Axes — Display Plans). Every weekday theme's Sunday duality
# rides an axis whose two ends are Cube poles: VERTICAL (yellow-top/
# 12h <-> purple-bottom/24h) on the Compass and the Seasons, HORIZONTAL
# (blue-06h <-> red-18h, the Sunday axis) on the Rose instead. The
# default law is unconditional on the vertical axis — the Ruler
# (`WEEKDAY_DUAL_NAMES[theme][0]`) always pulls to the warm pole
# (yellow/top) there, no per-theme override exists or is needed. Only
# the HORIZONTAL axis is per-theme, because a blind carryover of that
# same default (Ruler -> warm/red) is wrong wherever the Sacred Axis
# (CUBE.md §The Thirteen Axes) already assigns a member to the COLD
# trio: Christianity is the LUMINOUS COLD member (blue), Satanism the
# FALLEN WARM one (red) — the reverse of the blind default, which
# today seats Satanism blue and Christianity red. Listed themes pull
# their RULER to the cold pole instead; absent = the default carries
# over unchanged. `render.skin_geometry.ruler_seat_angle`/`servant_seat_angle`
# are the two readers (Rule #5) — they swap which of the Ruler's/
# Servant's figures rides which arm, never their names or articles.
DUALITY_RULER_ON_COLD_POLE = frozenset({"religion"})

# THE DUAL SUNDAY WHEEL MAP (owner seal 2026-07-29, closing the Session
# 23 miss — the per-WHEEL split was the whole point of the Duality-Axes
# decree and the Compass's third wheel never received it). Sunday's
# duality displays one of THREE ways, and the way is a property of the
# WHEEL, not only the pointer:
#   CENTER (one image; daylight Ruler / night Servant / Ninth in the
#     solar windows) — the Trinity and the Prism (all wheels), PLUS the
#     wheels below: the Quaternity's Seasons wheel turns its arms onto
#     the diagonals, leaving no 12h/24h seat to stand on.
#   VERTICAL 12h/24h (Ruler top in the light, Servant bottom in the
#     dark) — the Quaternity and the Compass, primary + secondary.
#   HORIZONTAL 06h/18h (Servant on blue left, Ruler on red right) — the
#     Rose (both wheels) PLUS the wheels below: the Compass's Character
#     wheel wears the very ROSE_PALETTE hues, so its Sunday rides the
#     same blue<->red axis and its bodies take the Rose's own hue seats
#     (`render.layers` reads POINTER_WEEKDAY_SLOTS["rose"] for it).
CENTER_DUALITY_WHEELS = frozenset({("cross", "tertiary")})
HORIZONTAL_DUALITY_WHEELS = frozenset({("octa", "tertiary")})

# THE GEOGRAPHIC VERTICAL FLIP (owner seal 2026-07-29, theme poll 23/23):
# themes whose VERTICAL duality seats the SERVANT on top — continents,
# because the Arctic IS the north and a globe reads north-up: Arctic
# (Servant) 12h, Antarctica (Ruler) 24h. The horizontal axis stays
# standard (18h red Antarctica, 06h blue Arctic). Same reader pair as
# DUALITY_RULER_ON_COLD_POLE; every OTHER theme was polled and sealed
# STANDARD the same day (Ruler top+red, Servant bottom+blue).
DUALITY_SERVANT_ON_TOP = frozenset({"continents"})
