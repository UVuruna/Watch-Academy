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
# The centre's own name, kept once (Rule #5): the seat that answers no
# figure in any register.
THE_ONE_SEAT = SACRED_TRIO_NAMES[1]

# --- the rosters (CUBE.md §The Rosters, Session 24) -----------------------------
# THE THREE FIGURE SETS every seat carries (Charter rule 5: three
# DIFFERENT PEOPLE holding one office, never one character read three
# ways) — archetypal (biblical, mythological, classical-literary),
# historical (real persons), modern (fantasy, film, comics). They are
# also the REGISTERS on disk (`<group>/<set>/colored/<Stem>.png`) and the
# three Rose stars' own sets (`constants.ROSE_STAR_SETS`): ONE tuple, all
# three readers.
FIGURE_SETS = ("archetypal", "historical", "modern")

# Every human cell of the cube → the two people who hold it in each set,
# `(luminous, fallen)`. The 108 seats of the poles, the vertices and the
# four carried edges are TRANSCRIBED from the sealed canon tables (§The
# Six Poles, §The Eight Vertices, §The Character Wheel); the 48 seats of
# the eight new edges are Session 24's round under FAME FIRST and its
# ranking addendum. The cells are the same coordinates `AXES` uses, so a
# seat's roster, hue, family, kin and antipode all answer from one key.
ROSTER: dict[tuple[int, int, int], dict[str, tuple[str, str]]] = {
    # --- the six poles ---------------------------------------------------------
    (-1, 0, 0): {                                   # Composure / Lethargy
        "archetypal": ("Siddhartha Gautama", "Ilya Ilyich Oblomov"),
        "historical": ("Marcus Aurelius", "Louis XVI"),
        "modern": ("Yoda", "Jabba the Hutt"),
    },
    (1, 0, 0): {                                    # Vigor / Frenzy
        "archetypal": ("Heracles", "Achilles"),
        "historical": ("Theodore Roosevelt", "Adolf Hitler"),
        "modern": ("Conan the Barbarian", "Hulk"),
    },
    (0, 1, 0): {                                    # Loyalty / Tribalism
        "archetypal": ("Penelope", "David"),
        "historical": ("Ernest Shackleton", "Pope Alexander VI"),
        "modern": ("Samwise Gamgee", "Bellatrix Lestrange"),
    },
    (0, -1, 0): {                                   # Integrity / Legalism
        "archetypal": ("Abraham", "Inspector Javert"),
        "historical": ("Socrates", "Maximilien Robespierre"),
        "modern": ("Batman", "Judge Dredd"),
    },
    (0, 0, -1): {                                   # Humility / Self-Annihilation
        "archetypal": ("Jesus Christ", "Judas Iscariot"),
        "historical": ("Mahatma Gandhi", "Franz Kafka"),
        "modern": ("Superman", "Darth Vader"),
    },
    (0, 0, 1): {                                    # Dignity / Self-Worship
        "archetypal": ("King Arthur", "Lucifer"),
        "historical": ("Nelson Mandela", "Salvador Dalí"),
        "modern": ("T'Challa", "Lord Voldemort"),
    },
    # --- the eight vertices ----------------------------------------------------
    (-1, 1, -1): {                          # Quiet Devotee / Submissive Enabler
        "archetypal": ("Virgin Mary", "Ophelia"),
        "historical": ("Florence Nightingale", "Eva Braun"),
        "modern": ("Faramir", "Peter Pettigrew"),
    },
    (-1, 1, 1): {                           # Steady Guardian / Complacent Nepotist
        "archetypal": ("Hector", "King Lear"),
        "historical": ("Queen Elizabeth II", "Louis XV"),
        "modern": ("Aragorn", "Denethor II"),
    },
    (-1, -1, -1): {                         # Contemplative Sage / Paralyzed Purist
        "archetypal": ("Job", "Hamlet"),
        "historical": ("Leo Tolstoy", "Nicholas II"),
        "modern": ("Gandalf", "Mace Windu"),
    },
    (-1, -1, 1): {                          # Wise Statesman / Cold Elitist
        "archetypal": ("Joseph son of Jacob", "The Grand Inquisitor"),
        "historical": ("George Washington", "Klemens von Metternich"),
        "modern": ("Albus Dumbledore", "Saruman"),
    },
    (1, 1, -1): {                           # Sacrificial Protector / Fanatical Martyr
        "archetypal": ("Moses", "Samson"),
        "historical": ("Harriet Tubman", "Yukio Mishima"),
        "modern": ("Harry Potter", "Kylo Ren"),
    },
    (1, 1, 1): {                            # Charismatic Champion / Tribal Warlord
        "archetypal": ("Beowulf", "Agamemnon"),
        "historical": ("Winston Churchill", "Benito Mussolini"),
        "modern": ("Wonder Woman", "Khal Drogo"),
    },
    (1, -1, -1): {                          # Principled Reformer / Puritanical Zealot
        "archetypal": ("Antigone", "Judge Claude Frollo"),
        "historical": ("Martin Luther King Jr.", "Girolamo Savonarola"),
        "modern": ("Luke Skywalker", "Stannis Baratheon"),
    },
    (1, -1, 1): {                           # Visionary Founder / Messianic Tyrant
        "archetypal": ("Aeneas", "Pharaoh of the Exodus"),
        "historical": ("Mustafa Kemal Atatürk", "Napoleon Bonaparte"),
        "modern": ("Leia Organa", "Paul Atreides"),
    },
    # --- the four CARRIED edges (the Character wheel's own combos) --------------
    (0, 1, -1): {                                   # Devotion / Martyrdom
        "archetypal": ("Moses", "Samson"),
        "historical": ("Janusz Korczak", "Marcus Antonius"),
        "modern": ("Alfred Pennyworth", "Severus Snape"),
    },
    (0, 1, 1): {                                    # Patronage / Favoritism
        "archetypal": ("Boaz", "King Lear"),
        "historical": ("Lorenzo de' Medici", "Nicolae Ceaușescu"),
        "modern": ("Charles Xavier", "Denethor II"),
    },
    (0, -1, 1): {                                   # Conviction / Dogmatism
        "archetypal": ("Elijah", "Creon"),
        "historical": ("Martin Luther", "Joseph Stalin"),
        "modern": ("Steve Rogers", "Dolores Umbridge"),
    },
    (0, -1, -1): {                                  # Renunciation / Mortification
        "archetypal": ("John the Baptist", "Father Ferapont"),
        "historical": ("Thomas More", "Simone Weil"),
        "modern": ("Obi-Wan Kenobi", "Silas"),
    },
    # --- the eight NEW edges (Session 24) --------------------------------------
    (-1, -1, 0): {                                  # Prudence / Indifference
        "archetypal": ("Solomon", "Pontius Pilate"),
        "historical": ("Elizabeth I", "Adolf Eichmann"),
        "modern": ("Spock", "Dr. Manhattan"),
    },
    (1, 1, 0): {                                    # Ardor / Vendetta
        "archetypal": ("Romeo", "Medea"),
        "historical": ("Joan of Arc", "Genghis Khan"),
        "modern": ("Katniss Everdeen", "Inigo Montoya"),
    },
    (-1, 1, 0): {                                   # Steadfastness / Machination
        "archetypal": ("Ruth", "Iago"),
        "historical": ("Rosa Parks", "Cardinal Richelieu"),
        "modern": ("Brienne of Tarth", "Petyr Baelish"),
    },
    (1, -1, 0): {                                   # Reform / Zealotry
        "archetypal": ("Nehemiah", "Saul of Tarsus"),
        "historical": ("Abraham Lincoln", "Oliver Cromwell"),
        "modern": ("Hermione Granger", "Rorschach"),
    },
    (-1, 0, -1): {                                  # Meekness / Despair
        "archetypal": ("Isaac", "Cain"),
        "historical": ("Francis of Assisi", "Vincent van Gogh"),
        "modern": ("Frodo Baggins", "Théoden"),
    },
    (1, 0, 1): {                                    # Aspiration / Megalomania
        "archetypal": ("Daedalus", "Icarus"),
        "historical": ("Muhammad Ali", "Alexander the Great"),
        "modern": ("Rocky Balboa", "Tony Stark"),
    },
    (-1, 0, 1): {                                   # Self-Mastery / Disdain
        "archetypal": ("Odysseus", "Coriolanus"),
        "historical": ("Bruce Lee", "Diogenes"),
        "modern": ("Uncle Iroh", "Tywin Lannister"),
    },
    (1, 0, -1): {                                   # Diligence / Servility
        "archetypal": ("Martha of Bethany", "Uriah Heep"),
        "historical": ("Mother Teresa", "Vidkun Quisling"),
        "modern": ("Andy Dufresne", "Dobby"),
    },
}

# THE TWO SACRED CORNERS (CUBE.md §The Rosters): the mythic principals
# are the persons themselves — the other two registers carry ECHOES,
# never rivals. The CENTRE is deliberately absent: The One contains all
# six powers without being ruled by any, and every human exemplar is
# ruled by something, so `sacred_figure()` answers None for him BY
# DOCTRINE (the documented-fallback exception to Rule #1, not a miss).
SACRED_FIGURES = {
    "Jesus Christ": {
        "archetypal": "Jesus Christ",
        "historical": "Maximilian Kolbe",
        "modern": "Aslan",
    },
    "The Devil": {
        "archetypal": "The Devil",
        "historical": "Nero",
        "modern": "Sauron",
    },
}


def roster(cell: tuple[int, int, int], register: str) -> tuple[str, str]:
    """The two people who hold one human cell in one figure set —
    `(the luminous reading's figure, the fallen reading's figure)`. An
    unknown cell or register raises: the grid is complete by
    construction, and a silent miss would be a lie (Rule #1)."""
    return ROSTER[cell][register]


def sacred_figure(seat: str, register: str) -> str | None:
    """One sacred seat's figure in one set. `None` for the centre alone,
    which takes no figure in any register (owner verdict 2026-07-28)."""
    if seat == THE_ONE_SEAT:
        return None
    return SACRED_FIGURES[seat][register]

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
