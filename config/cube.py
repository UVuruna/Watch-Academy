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

# THE SIX POLES' SEALED ROSE HUES (CUBE.md §The Sabbath axis, the
# "Consequence for the Cube" table) as indices into
# `defaults.ROSE_PALETTE` — yellow 0, orange 1, red 2, rose 3, purple 4,
# cyan 5, blue 6, green 7. Blue and red are NOT cube hues on the Rose:
# they are the Sabbath's, which is exactly why the seating leaves them to
# a non-primary axis.
ROSE_POLE_HUE = {
    (0, 1, 0): 0,        # Loyalty        yellow
    (1, 0, 0): 1,        # Vigor          orange
    (0, 0, 1): 3,        # Dignity        rose
    (0, -1, 0): 4,       # Integrity      purple-gray
    (-1, 0, 0): 5,       # Composure      cyan
    (0, 0, -1): 7,       # Humility       green
}

# THE ROSE-24 SEATING (Session 26) — the 24 human cells in RAY order,
# ray 0 = 12h, one ray every 15° clockwise. The single survivor of the
# exhaustive search under the five laws; `core.cube_seating` re-derives
# it and `tests/test_cube_seating.py` re-runs the whole search rather
# than trusting this constant.
ROSE_24_SEATING: tuple[tuple[int, int, int], ...] = (
    (-1, 1, 0),      # ray  0  12h  yellow  Steadfastness / Machination
    (-1, 1, -1),     # ray  1  13h  yellow  Quiet Devotee / Submissive Enabler
    (-1, 0, -1),     # ray  2  14h  orange  Meekness / Despair
    (-1, 0, 0),      # ray  3  15h  orange  Composure / Lethargy
    (-1, -1, 0),     # ray  4  16h  orange  Prudence / Indifference
    (-1, -1, 1),     # ray  5  17h  red     Wise Statesman / Cold Elitist
    (-1, 0, 1),      # ray  6  18h  red     Self-Mastery / Disdain
    (-1, 1, 1),      # ray  7  19h  red     Steady Guardian / Complacent Nepotist
    (0, 1, 1),       # ray  8  20h  rose    Patronage / Favoritism
    (0, 0, 1),       # ray  9  21h  rose    Dignity / Self-Worship
    (0, -1, 1),      # ray 10  22h  rose    Conviction / Dogmatism
    (0, -1, 0),      # ray 11  23h  purple  Integrity / Legalism
    (1, -1, 0),      # ray 12  00h  purple  Reform / Zealotry
    (1, -1, 1),      # ray 13  01h  purple  Visionary Founder / Messianic Tyrant
    (1, 0, 1),       # ray 14  02h  cyan    Aspiration / Megalomania
    (1, 0, 0),       # ray 15  03h  cyan    Vigor / Frenzy
    (1, 1, 0),       # ray 16  04h  cyan    Ardor / Vendetta
    (1, 1, -1),      # ray 17  05h  blue    Sacrificial Protector / Fanatical Martyr
    (1, 0, -1),      # ray 18  06h  blue    Diligence / Servility
    (1, -1, -1),     # ray 19  07h  blue    Principled Reformer / Puritanical Zealot
    (0, -1, -1),     # ray 20  08h  green   Renunciation / Mortification
    (0, 0, -1),      # ray 21  09h  green   Humility / Self-Annihilation
    (0, 1, -1),      # ray 22  10h  green   Devotion / Martyrdom
    (0, 1, 0),       # ray 23  11h  yellow  Loyalty / Tribalism
)

# THE CALENDAR-12 LAWS (Session 26). The twelve human axes fall into four
# families of three, and the year into four seasons of three months — the
# Almanac wheel's own division (June's wedge centred on the top, so wedge
# index // 3 IS the season, wedge index % 3 the position within it).
# Nothing else is stored: `core.cube_seating.calendar_seating()` computes
# every arm from these two dictionaries.
CALENDAR_SEASON_BY_FAMILY = {
    "tertiary": 0,       # Summer  — Jun/Jul/Aug: the fully committed corners
    "discord": 1,        # Autumn  — Sep/Oct/Nov: the ends of mixed sign
    "primary": 2,        # Winter  — Dec/Jan/Feb: the bare three axes
    "concord": 3,        # Spring  — Mar/Apr/May: the ends of like sign
}
CALENDAR_POSITION_BY_INDEX = {"y": 0, "x": 1, "z": 2}

# The Calendar's centre medallion is a SINGLE slot and holds The One
# alone; the Rose's axle holds all three sacred seats (the Being view).
CALENDAR_CENTRE = THE_ONE
