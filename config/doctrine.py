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


class Station(NamedTuple):
    """One stop on a four-station journey: the arm it stands on, the
    station's own name, and the letter the cipher takes from it."""

    hour: int
    name: str
    letter: str


# THE TWO CROSSES (CUBE.md §The Path of Light / §The Path of Darkness).
# A seat is what an arm IS; a STATION is where a traveller stands at that
# hour of the journey — which is why both crosses can walk the same six
# arms without displacing the Prism's own occupants. Order is WALKING
# order, and it is the whole argument: the bright road ends at midnight
# and the dark road at noon, so neither journey terminates in its own
# kind of hour (the chiasm).
PATH_OF_LIGHT = (
    Station(8, "Hope", "H"),
    Station(12, "Faith", "F"),
    Station(16, "Love", "L"),
    Station(24, "Salvation", "S"),
)
PATH_OF_DARKNESS = (
    Station(20, "Fear", "F"),
    Station(24, "Anger", "A"),
    Station(4, "Hate", "H"),
    Station(12, "Suffering", "S"),
)

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
STAR = (
    Station(8, "Spark", "S"),
    Station(12, "Trust", "T"),
    Station(16, "Affection", "A"),
    Station(24, "Redemption", "R"),
)

# THE ASSEMBLED CIPHERS (encyclopedia, "DOMY and SAFE"). Built by
# ASSEMBLY rather than walking order, exactly as MASON is assembled from
# the letters ringing the Banknote's hexagram: the application's own name
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
    Station(16, "Agape", "A"),
    Station(12, "Fides", "F"),
    Station(8, "Elpis", "E"),
)

# The pairs a page draws: (page name, bright reading, dark reading).
CROSS_PAGES = {
    "The Two Crosses": (PATH_OF_LIGHT, PATH_OF_DARKNESS),
    "FALL and STAR": (STAR, FALL),
    "DOMY and SAFE": (SAFE, DOMY),
}


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
