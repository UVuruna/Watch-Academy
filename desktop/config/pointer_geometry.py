"""What a pointer IS as a shape.

The pointer is the star at the middle of the dial. This module holds
the numbers that decide its FORM and nothing else: how many arms and
wedges each pointer draws, how wide an arm is at the hub, whether it
is drawn as a star or a polygon, and how a polygon's edges curve or
notch. Its twelve calendar wedges and their month names sit here too
- the wedge count IS geometry and the names ride one wedge each.

What a pointer is CALLED lives next door in `pointer_names.py`; what
a wheel SEATS lives in `config/registry/slots.py` and
`config/archetypes.py`.

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

# ═══════════════════════════ POINTER ARM & WEDGE COUNTS ═══════════════════════════
# Pointer variants: how many arms the star has — and with how many hues
# the day's periods are measured (owner spec: trio 3x120, cross 4x90,
# hexa 6x60, octa 8x45).
# "aurora" (owner spec 2026-07-12) draws NO geometric pointer at all —
# its 7 entries are the PALETTE size: a dawn hue, five day hues spread
# EVENLY across the actual sunrise-sunset arc, and a dusk hue.
# "calendar" (owner 2026-07-16, CANON §The Dozen) divides the 24h dial
# into TWELVE 2-hour wedges and, like Aurora, draws NO star arms — its
# 12 entries are the PALETTE size (one hue per wedge). Its two wheels
# ride the wheel slot: primary = the Zodiac Dozen, secondary = the
# Almanac (Month) Dozen. It has NO arm HALF-ANGLE (armless, like
# Aurora): the star geometry and the arm hovers skip it explicitly.
# "rose" (owner spec 2026-07-27, CUBE.md §The Rose) is the SEVENTH
# pointer: THREE octa stars 15° apart — 8 hues, one star's worth, worn
# by all three (`ROSE_STAR_OFFSETS` places them, `ROSE_STAR_SETS` says
# which figure set each carries). Its palette size is 8 like the octa's
# — the three stars are the same star drawn three times, never 24
# independent hues (Rule #19: one rule, not 24 entries).
POINTER_POINTS = {
    "hexa": 6, "cross": 4, "octa": 8, "trio": 3, "aurora": 7,
    "calendar": 12, "rose": 8,
}

# What the READER counts on the dial — which is NOT always the palette
# size above (owner correction 2026-07-28: "on pokazuje 24, kalendar
# pokazuje 12"). The Rose draws its one eight-arm star THREE times at
# 15° pitch, so twenty-four rays stand on the glass while eight hues
# dress them; `POINTER_POINTS` stays the hue count that
# `settings_store._load_palettes` validates against, and this table is
# what the Design window prints and sorts by. Every pointer names its
# own number — the Calendar's twelve wedges and Aurora's seven bands are
# as countable as any star's arms.
POINTER_DIAL_COUNTS = {
    "trio": 3, "cross": 4, "hexa": 6, "aurora": 7, "octa": 8,
    "calendar": 12, "rose": 24,
}
CALENDAR_WEDGES = 12
CALENDAR_WEDGE_DEG = 360.0 / CALENDAR_WEDGES        # 30° per 2-hour wedge
# THE LIT WEDGE IS GONE (owner decree 2026-07-29, Pointers REWORK phase
# 2): "Osvetljavanje part koji prolazi sat ili zemlja iskljuciti —
# obrisati tu funkcionalnost". The Calendar no longer lights the wedge
# under the hour hand or under today's month/sign; it follows the SAME
# visibility law as every other pointer (the day/night law plus its own
# DAYLIGHT_SWITCH_POINTERS entry). `CALENDAR_LIGHTING_MODES`,
# `Settings.calendar_lighting`, `render.calendar_mount.calendar_lit_index` and
# `defaults.CALENDAR_WEDGE_LIT_DELTA` died with it — an old settings
# file that still carries the stale `calendar_lighting` key simply
# loads without it (the loader reads keys it knows, never rejects
# extras — pinned by tests/test_calendar.py).
#
# THE CALENDAR MOUNT (owner DESIGN ZODIAC law, R9a round 2026-07-21;
# GENERALIZED 2026-07-29): the set of figures that rides the Calendar's
# twelve wedges is no longer a hand-kept quartet. The ONE registry both
# the picker and the renderer read is `calendar_mounts.CALENDAR_MOUNTS` — it
# lives in `defaults` because it is the only module that sees BOTH the
# canon rosters declared here and `calendar_mounts.SLAVIC_MONTHS`; the legal
# setting values are `calendar_mounts.CALENDAR_MOUNT_MODES`, derived from it.
#
# The Gregorian months, January first — the ONE list every month-keyed
# mount rotates into Almanac seat order (Rule #19: the June-first order
# is computed by `calendar_mounts.almanac_seat_order`, never written twice).
GREGORIAN_MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)

# ═══════════════════════════ ARM HALF-ANGLES ═══════════════════════════
# Star arm (diamond) half-angles. Hexa/octa are the regular N-star
# values (180/N, adjacent arms touch at the inner vertices); the CROSS
# uses the OCTA arm shape — "octa without the 4 diagonal arms" (owner
# spec, design/background/cross.png) — slim diamonds with gaps between
# them, never the fat rhombi a regular 4-star would give. The TRIO is
# likewise "half of hexa" (owner spec, FINAL.txt #7): three hexa-shaped
# arms at 12h/4h/20h — where the ring jewels M, D, Y point — with
# gaps; its three hues center on the arms (thirds 8-16 / 16-24 / 0-8).
POINTER_ARM_HALF_ANGLE_DEG = {
    "hexa": 30.0, "cross": 22.5, "octa": 22.5, "trio": 30.0,
    # The ROSE is three OCTA stars — the same arm shape, so its rays sit
    # 15° apart while each is 45° wide and neighbors OVERLAP, exactly as
    # the owner draws them (CUBE.md §The Rose).
    "rose": 22.5,
}

# ═══════════════════════════ POINTER SHAPE & POLYGON EDGES ═══════════════════════════
# THE POINTER SHAPE (Pointers REWORK phase 1, owner sheet
# UV/Pointers.png, 2026-07-29) — ONE global choice for the drawn wheel:
#   "star"    — the standing diamond stars (the shape shipped so far).
#   "polygon" — the PLAIN polygon of the pointer's own arm count: the
#               Quaternity a SQUARE, the Prism a HEXAGON, the Compass an
#               OCTAGON, with one VERTEX per arm tip and each arm's hue
#               filling its kite from the center out to that vertex
#               (boundaries run center -> edge midpoint). The TRINITY is
#               the owner's one exception: instead of a triangle it draws
#               the CUBE — the hexagon of three rhombi the Cube look
#               already builds (`CUBE_LOOK_WHEELS`), rhombus tips on the
#               trio's three arms.
# The armless AURORA draws no pointer at all and ignores the choice. The
# CALENDAR and the ROSE read it as "one touching star instead of two /
# three overlapping ones" — see CALENDAR_STAR_ARMS below and
# POINTER_DIAL_COUNTS above for the ray counts.
POINTER_SHAPES = ("star", "polygon")
POINTER_SHAPE_DEFAULT = "star"

# The pointers whose "polygon" really IS a polygon (3/4/6/8 arms) — the
# only ones the CURVATURE slider touches. The Calendar's twelve-point
# and the Rose's twenty-four-point polygons are STARS whose adjacent
# arms merely touch, and a star never curves (owner spec).
POLYGON_POINTERS = ("trio", "cross", "hexa", "octa")

# THE EDGE PULL (owner sheet: "Original straight edge / Smooth concave
# edge / V-notched edge"): 0.0 leaves the plain polygon; toward 1.0 each
# OUTER edge's midpoint is pulled inward along its own radius, until at
# 1.0 it sits exactly where the pointer's OWN star seats its inner
# vertices — so the silhouette lands on the star's concave profile. The
# color-boundary edges INSIDE the figure never curve.
POLYGON_CURVATURE_RANGE = (0.0, 1.0)
POLYGON_CURVATURE_DEFAULT = 0.0
# How a pulled edge is drawn: "smooth" — one quadratic arc THROUGH the
# pulled midpoint; "notched" — two straight segments meeting there (the
# V-notch).
POLYGON_EDGE_MODES = ("smooth", "notched")
POLYGON_EDGE_DEFAULT = "smooth"
