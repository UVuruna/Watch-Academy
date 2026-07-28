"""The Character Cube's canon table, as data (CUBE.md §The Thirteen
Axes). Thirteen axes, twenty-six extremities, the centre — the 65 sealed
terms. Coordinates only: every family, index, kinship and antipode is
DERIVED in `core.cube_seating` (root Rule 19), never stored here.

Axes: X Activation, Y Moral Scope, Z Self-Regard. -1 is the cold pole,
+1 the warm one, 0 the measure.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CubeCell:
    """One cell of the 27: where it stands, and the two names the radial
    law gives that standing — held in measure, and walked past it."""

    coords: tuple[int, int, int]
    luminous: str
    fallen: str = ""            # empty for The One alone: no fall touches him


@dataclass(frozen=True)
class CubeAxis:
    """One of the thirteen lines through The One. `cold` and `warm` are
    canon's own two columns, not a claim about every end's hue: on the
    four axes whose X is zero the words name the column, not the
    temperature (CUBE.md's own tables)."""

    name: str
    cold: CubeCell
    warm: CubeCell


THE_ONE = CubeCell((0, 0, 0), "The One")

# The thirteen. The Sacred Axis leads: it is the only one whose two ends
# leave the human circle (CUBE.md §The Sacred Axis — 3 sacred + 24 human).
AXES: tuple[CubeAxis, ...] = (
    # --- tertiary: the four vertex axes ---------------------------------------
    CubeAxis(
        "The Sacred Axis",
        CubeCell((-1, -1, -1), "Contemplative Sage", "Paralyzed Purist"),
        CubeCell((1, 1, 1), "Charismatic Champion", "Tribal Warlord"),
    ),
    CubeAxis(
        "Vow ↔ Vision",
        CubeCell((-1, 1, -1), "Quiet Devotee", "Submissive Enabler"),
        CubeCell((1, -1, 1), "Visionary Founder", "Messianic Tyrant"),
    ),
    CubeAxis(
        "Preservation ↔ Revolution",
        CubeCell((-1, 1, 1), "Steady Guardian", "Complacent Nepotist"),
        CubeCell((1, -1, -1), "Principled Reformer", "Puritanical Zealot"),
    ),
    CubeAxis(
        "Crown ↔ Shield",
        CubeCell((-1, -1, 1), "Wise Statesman", "Cold Elitist"),
        CubeCell((1, 1, -1), "Sacrificial Protector", "Fanatical Martyr"),
    ),
    # --- primary: the three face axes -----------------------------------------
    CubeAxis(
        "Activation",
        CubeCell((-1, 0, 0), "Composure", "Lethargy"),
        CubeCell((1, 0, 0), "Vigor", "Frenzy"),
    ),
    CubeAxis(
        "Moral Scope",
        CubeCell((0, -1, 0), "Integrity", "Legalism"),
        CubeCell((0, 1, 0), "Loyalty", "Tribalism"),
    ),
    CubeAxis(
        "Self-Regard",
        CubeCell((0, 0, -1), "Humility", "Self-Annihilation"),
        CubeCell((0, 0, 1), "Dignity", "Self-Worship"),
    ),
    # --- secondary: the six edge axes -----------------------------------------
    CubeAxis(
        "Reason ↔ Emotion",
        CubeCell((-1, -1, 0), "Prudence", "Indifference"),
        CubeCell((1, 1, 0), "Ardor", "Vendetta"),
    ),
    CubeAxis(
        "Pragmatism ↔ Idealism",
        CubeCell((-1, 1, 0), "Steadfastness", "Machination"),
        CubeCell((1, -1, 0), "Reform", "Zealotry"),
    ),
    CubeAxis(
        "Person ↔ Cause",
        CubeCell((0, 1, -1), "Devotion", "Martyrdom"),
        CubeCell((0, -1, 1), "Conviction", "Dogmatism"),
    ),
    CubeAxis(
        "Hearth ↔ Desert",
        CubeCell((0, 1, 1), "Patronage", "Favoritism"),
        CubeCell((0, -1, -1), "Renunciation", "Mortification"),
    ),
    CubeAxis(
        "Lion ↔ Lamb",
        CubeCell((-1, 0, -1), "Meekness", "Despair"),
        CubeCell((1, 0, 1), "Aspiration", "Megalomania"),
    ),
    CubeAxis(
        "Servant ↔ Sovereign",
        CubeCell((-1, 0, 1), "Self-Mastery", "Disdain"),
        CubeCell((1, 0, -1), "Diligence", "Servility"),
    ),
)

# The sacred trio, in the order the Sacred Axis reads them (CUBE.md
# §The Sacred Axis): the LUMINOUS cold corner, the centre, the FALLEN
# warm corner. The Rose seats all three at the axle — the Being view
# projects the whole axis onto the single centre point.
SACRED_TRIO_NAMES = ("Jesus Christ", "God — The One", "The Devil")

# THE SIX POLES' SEALED ROSE HUES (CUBE.md §The Sunday axis, the
# "Consequence for the Cube" table) as indices into
# `defaults.ROSE_PALETTE` — yellow 0, orange 1, red 2, rose 3, purple 4,
# cyan 5, blue 6, green 7. Blue and red are NOT cube hues on the Rose:
# they are Sunday's two seats (Servant blue 06h, Ruler red 18h).
ROSE_POLE_HUE = {
    (0, 1, 0): 0,        # Loyalty        yellow
    (1, 0, 0): 1,        # Vigor          orange
    (0, 0, 1): 3,        # Dignity        rose
    (0, -1, 0): 4,       # Integrity      purple-gray
    (-1, 0, 0): 5,       # Composure      cyan
    (0, 0, -1): 7,       # Humility       green
}

# THE SYMMETRY LAW (owner decree 2026-07-28): "Primarna je simetrija,
# sekundarna je simbolika" — symmetry decides WHICH KIND of axis stands
# where; symbolism only decides which axis of that kind. The cube's three
# families count 3 face axes, 6 edge axes and 3 human vertex axes, and on
# a twelve-fold and a twenty-four-fold dial alike that admits exactly ONE
# fully regular answer: two opposed EQUILATERAL TRIANGLES with a HEXAGON
# between them — which is the hexagram, this dial's own emblem.
#
# THE ROSE-24 SEATING (Session 26, re-solved under the symmetry law).
# The 24 human cells in RAY order, ray 0 = 12h, one ray every 15°
# clockwise. Ray % 4 == 0 carries a POLE (the owner's hexagram pairs
# 12h-24h, 4h-16h, 20h-8h), ray % 4 == 2 a CORNER, every odd ray an EDGE.
# The single survivor of the exhaustive search; `core.cube_seating`
# re-derives it and `tests/test_cube_seating.py` re-runs the whole search
# rather than trusting this constant.
ROSE_24_SEATING: tuple[tuple[int, int, int], ...] = (
    (0, 1, 0),       # ray  0  12h  yellow  POLE    Loyalty / Tribalism
    (0, 1, 1),       # ray  1  13h  yellow  edge    Patronage / Favoritism
    (-1, 1, 1),      # ray  2  14h  orange  corner  Steady Guardian / Compl. Nepotist
    (-1, 1, 0),      # ray  3  15h  orange  edge    Steadfastness / Machination
    (-1, 0, 0),      # ray  4  16h  orange  POLE    Composure / Lethargy
    (-1, -1, 0),     # ray  5  17h  red     edge    Prudence / Indifference
    (-1, -1, 1),     # ray  6  18h  red     corner  Wise Statesman / Cold Elitist
    (-1, 0, 1),      # ray  7  19h  red     edge    Self-Mastery / Disdain
    (0, 0, 1),       # ray  8  20h  rose    POLE    Dignity / Self-Worship
    (1, 0, 1),       # ray  9  21h  rose    edge    Aspiration / Megalomania
    (1, -1, 1),      # ray 10  22h  rose    corner  Visionary Founder / Mess. Tyrant
    (0, -1, 1),      # ray 11  23h  purple  edge    Conviction / Dogmatism
    (0, -1, 0),      # ray 12  00h  purple  POLE    Integrity / Legalism
    (0, -1, -1),     # ray 13  01h  purple  edge    Renunciation / Mortification
    (1, -1, -1),     # ray 14  02h  cyan    corner  Principled Reformer / Purit. Zealot
    (1, -1, 0),      # ray 15  03h  cyan    edge    Reform / Zealotry
    (1, 0, 0),       # ray 16  04h  cyan    POLE    Vigor / Frenzy
    (1, 1, 0),       # ray 17  05h  blue    edge    Ardor / Vendetta
    (1, 1, -1),      # ray 18  06h  blue    corner  Sacrificial Protector / Fan. Martyr
    (1, 0, -1),      # ray 19  07h  blue    edge    Diligence / Servility
    (0, 0, -1),      # ray 20  08h  green   POLE    Humility / Self-Annihilation
    (-1, 0, -1),     # ray 21  09h  green   edge    Meekness / Despair
    (-1, 1, -1),     # ray 22  10h  green   corner  Quiet Devotee / Submissive Enabler
    (0, 1, -1),      # ray 23  11h  yellow  edge    Devotion / Martyrdom
)

# THE CALENDAR-12 LAWS (Session 26, re-solved under the symmetry law).
# The Almanac wheel's twelve wedges (June centred on the top, wedge w at
# hour 12 + 2w) carry the three families in the same hexagram figure:
#   - the three FACE axes on the PURE-COLOUR arms — June green 12h,
#     October red 20h, February blue 4h — an exact equilateral triangle;
#   - the three human VERTEX axes on the arms of the mixed primaries —
#     August yellow 16h, December magenta 24h, April cyan 8h — the
#     opposite triangle;
#   - the six EDGE axes on the six remaining arms — a regular hexagon.
# The INVERTED version swaps the two triangles (the owner's second
# version: the pure-colour arms become the corners' and the mixed ones
# the poles'). Nothing else is stored — `calendar_seating()` computes it.
CALENDAR_WEDGES_BY_FAMILY = {
    "primary": (0, 4, 8),                  # June, October, February
    "tertiary": (2, 6, 10),                # August, December, April
    "secondary": (1, 3, 5, 7, 9, 11),      # Jul, Sep, Nov, Jan, Mar, May
}
# Which axis of a family takes which of its arms — the SECONDARY
# criterion (symbolism), argued month by month in CUBE.md §The Seatings.
CALENDAR_AXIS_ORDER = {
    "primary": ("Moral Scope", "Self-Regard", "Activation"),
    "tertiary": ("Crown ↔ Shield", "Vow ↔ Vision", "Preservation ↔ Revolution"),
    "secondary": ("Person ↔ Cause", "Servant ↔ Sovereign",
                  "Pragmatism ↔ Idealism", "Hearth ↔ Desert",
                  "Lion ↔ Lamb", "Reason ↔ Emotion"),
}

# The Calendar's centre medallion is a SINGLE slot and holds The One
# alone; the Rose's axle holds all three sacred seats (the Being view).
CALENDAR_CENTRE = THE_ONE
