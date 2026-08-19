"""The canon tables that are neither coordinates nor wheels.

`config/cube.py` holds the Cube as COORDINATES; `config/archetypes.py`
holds the dial's WHEELS. Two canon figures fit neither and lived only in
prose until now — CUBE.md §The Two Crosses and the Double Trinity's
twenty-four fields. The Session 27 diagram wave needed them as data
(root Rule #19: a drawing computed from the canon, never a picture of
it), and a diagram must never parse an article to find its own content.

Every line here is transcribed from the sealed text — CUBE.md §The Path
of Light / §The Path of Darkness / §The chiasm, and the encyclopedia's
own FALL and STAR, DOMY and SAFE and The Twenty-Four Fields articles.
The hours are the dial's own arms.

Layer: config (pure — no Qt, no wall clock). Documentation:
config/doctrine.md.
"""

from typing import NamedTuple


# ═══════════════════════════ JOURNEY STATION TYPE ═══════════════════════════
class Station(NamedTuple):
    """One stop on a four-station journey: the arm it stands on, the
    station's own name, and the letter the cipher takes from it."""

    hour: int
    name: str
    letter: str


# ═══════════════════════════ THE TWO CROSSES ═══════════════════════════
# THE TWO CROSSES (CUBE.md §The Path of Light / §The Path of Darkness).
# A seat is what an arm IS; a STATION is where a traveller stands at that
# hour of the journey — which is why both crosses can walk the same six
# arms without displacing the Prism's own occupants. Order is WALKING
# order, and it is the whole argument: the bright road ends at midnight
# and the dark road at noon, so neither journey terminates in its own
# kind of hour (the chiasm).
# RE-SEATED (owner decree 2026-08-09): Faith 08h, Love 12h, Hope 16h.
# Faith stands where the day begins because faith answers something
# ALREADY GIVEN — testimony, promise, event; it is the morning and the
# past. Love crowns noon because love is the only one of the three that
# must be ACTUAL to exist at all: not "I loved" or "I will love" but
# "do I love now". Hope takes the evening arm because hope is needed
# exactly where the light withdraws, and because its own object IS
# salvation — so it must be the LAST station before the summit at 24h,
# never the furthest from it.
PATH_OF_LIGHT = (
    Station(8, "Faith", "F"),
    Station(12, "Love", "L"),
    Station(16, "Hope", "H"),
    Station(24, "Salvation", "S"),
)
PATH_OF_DARKNESS = (
    Station(20, "Fear", "F"),
    Station(24, "Anger", "A"),
    Station(4, "Hate", "H"),
    Station(12, "Suffering", "S"),
)

# ═══════════════════════════ FALL AND STAR MNEMONICS ═══════════════════════════
# THE ENGLISH MNEMONICS (encyclopedia, "FALL and STAR"). The words are
# the journeys' own verbs and destinations — FALL is the descent's
# motion, STAR the ascent's aim. The substitutions are canon: Loathing
# for Hate and Lament for Suffering carry the same content in the
# letters the descent requires; Spark names hope at the size the station
# actually claims.
FALL = (
    Station(20, "Fear", "F"),
    Station(24, "Anger", "A"),
    Station(4, "Loathing", "L"),
    Station(12, "Lament", "L"),
)
# The hours follow the re-seating; the WORD does not move — STAR is
# assembled from the letters, not walked in hour order, so each name
# simply travels with the station it renames (Trust=Faith 08h,
# Affection=Love 12h, Spark=Hope 16h).
STAR = (
    Station(16, "Spark", "S"),
    Station(8, "Trust", "T"),
    Station(12, "Affection", "A"),
    Station(24, "Redemption", "R"),
)

# ═══════════════════════════ DOMY AND SAFE CIPHERS & PAGE REGISTRY ═══════════════════════════
# THE ASSEMBLED CIPHERS (encyclopedia, "DOMY and SAFE"). Built by
# ASSEMBLY rather than walking order, exactly as MASON is assembled from
# the jewels ringing the Banknote's hexagram: the application's own name
# is the dark cross, and the word for its purpose is the bright cross
# read back down from the summit.
DOMY = (
    Station(12, "Dolor", "D"),
    Station(4, "Odium", "O"),
    Station(20, "Metus", "M"),
    Station(24, "Hybris", "Y"),      # the littera Pythagorica, the fork
)
SAFE = (
    Station(24, "Salus", "S"),
    Station(12, "Agape", "A"),
    Station(8, "Fides", "F"),
    Station(16, "Elpis", "E"),
)

# The pairs a page draws: (page name, bright reading, dark reading).
CROSS_PAGES = {
    "The Two Crosses": (PATH_OF_LIGHT, PATH_OF_DARKNESS),
    "FALL and STAR": (STAR, FALL),
    "DOMY and SAFE": (SAFE, DOMY),
}


# ═══════════════════════════ FIELD TYPE & THE TWENTY-FOUR FIELDS ═══════════════════════════
class Field(NamedTuple):
    """One of the twenty-four: an office (what the person DOES) and the
    process it works on the object (what HAPPENS to it)."""

    office: str
    process: str


# THE TWENTY-FOUR FIELDS (encyclopedia, "The Twenty-Four Fields"): three
# persons, four offices each, every office paired with its process — so
# each field reads as an act and its effect. The six core seats of the
# Council are simply the two most characteristic of each person's four.
UNION_FIELDS = {
    "God": (
        Field("Judge", "Justice"),
        Field("Avenger", "Retribution"),
        Field("Creator", "Reinvention"),
        Field("Lawgiver", "Reform"),
    ),
    "The Devil": (
        Field("Destroyer", "Punishment"),
        Field("Tempter", "Ruin"),
        Field("Prosecutor", "Guilt"),
        Field("Catalyst", "Critique"),
    ),
    "Jesus": (
        Field("Redeemer", "Renewal"),
        Field("Advocate", "Salvation"),
        Field("Shepherd", "Mercy"),
        Field("Preserver", "Stewardship"),
    ),
}


# The arm angles themselves are NOT computed here: `core.angles.
# ring_position_angle` is the one mapping every fixed ring hour already
# shares (Rule #5), and a station stands on a ring hour like any other
# seat. The diagram asks core for the angle; this module only says WHICH
# hour each station stands on.


# --- THE RING LETTERS' OWN REASON ---------------------------------------------
# D O M Y spells the clock's name on the outer ring, and the O is a
# Greek Ω — but the real rule is arithmetic: each of the four is a GREEK
# letter standing at the hour equal to its PLACE in the Greek alphabet
# (Δ delta 4th at 04h, M mu 12th crowning 12h, Y upsilon 20th at 20h, Ω
# omega 24th and last at the bottom, 24h). The table lives here because
# the ring-letters article states it and the computed ring-letter
# diagram draws it — one source, so the figure can never disagree with
# the prose it stands beside.
RING_JEWEL_SEATS = (
    ("Δ", 4),
    ("M", 12),
    ("Y", 20),
    ("Ω", 24),
)

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
