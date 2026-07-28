"""The Cube's ROSTERS (WORKPLAN Session 24, CUBE.md §The Rosters): who
holds each of the twenty-six human cells in each of the three figure
sets, and who echoes the two sacred corners.

The canon file is the SOURCE and this module is the transcription, so
the pins run in that direction: every name the engine speaks must stand
in CUBE.md, the sealed 108 seats must be unchanged, and the 52 seats
this round added are pinned whole. The one structural law the round
discovered — a figure repeats only between a vertex and its own flat
shadow — is proved from the coordinates rather than listed by hand.
"""

import pathlib

import pytest

from config import archetypes, constants, cube

CUBE_CANON = (
    pathlib.Path(__file__).resolve().parent.parent / "CUBE.md"
).read_text(encoding="utf-8")

HUMAN_CELLS = {
    end.coords for axis in cube.AXES for end in (axis.cold, axis.warm)
}
# The Character wheel is the Cube at depth zero, so its four combos are
# exactly the edges with x == 0; the eight edges that commit X are the
# ones Session 24 peopled. Derived, never listed (root Rule 19).
NEW_EDGES = {
    cell for cell in HUMAN_CELLS
    if sum(1 for v in cell if v) == 2 and cell[0] != 0
}


def _people(cell) -> list[str]:
    return [name for pair in cube.ROSTER[cell].values() for name in pair]


# --- completeness ---------------------------------------------------------------
def test_the_roster_seats_every_human_cell_and_nothing_else():
    """26 cells, no invention and no gap — the sacred corners' own
    figures live in their own table, never as a 27th cell."""
    assert set(cube.ROSTER) == HUMAN_CELLS
    assert len(cube.ROSTER) == 26
    assert cube.THE_ONE.coords not in cube.ROSTER


def test_every_cell_carries_all_three_sets_with_both_readings():
    for cell, sets in cube.ROSTER.items():
        assert tuple(sets) == cube.FIGURE_SETS, cell
        for register, pair in sets.items():
            assert len(pair) == 2, (cell, register)
            assert all(name.strip() for name in pair), (cell, register)


def test_three_sets_are_three_different_people():
    """Charter rule 5: three sets on one seat are three DIFFERENT people
    holding one office, never one character read three ways."""
    for cell, sets in cube.ROSTER.items():
        for reading in (0, 1):                  # luminous, then fallen
            people = {sets[register][reading] for register in cube.FIGURE_SETS}
            assert len(people) == 3, (cell, reading)
        for register, (luminous, fallen) in sets.items():
            assert luminous != fallen, (cell, register)


# --- the canon is the source ----------------------------------------------------
def test_every_figure_the_engine_speaks_stands_in_the_canon():
    """CUBE.md is the source; config/cube.py is its transcription. A name
    that drifts here (a typo, a quiet swap) fails the moment it cannot be
    found in the canon file."""
    spoken = {name for cell in cube.ROSTER for name in _people(cell)}
    spoken |= {
        figure
        for registers in cube.SACRED_FIGURES.values()
        for figure in registers.values()
    }
    missing = sorted(name for name in spoken if name not in CUBE_CANON)
    assert not missing, missing


def test_the_sealed_seats_are_transcribed_not_rewritten():
    """Session 24 peopled the new edges; it touched no sealed seat. Spot
    pins across all three sealed families (pole, vertex, carried edge)."""
    assert cube.roster((0, 1, 0), "archetypal") == ("Penelope", "David")
    assert cube.roster((0, 0, 1), "modern") == ("T'Challa", "Lord Voldemort")
    assert cube.roster((-1, -1, -1), "historical") == ("Leo Tolstoy", "Nicholas II")
    assert cube.roster((1, 1, 1), "archetypal") == ("Beowulf", "Agamemnon")
    assert cube.roster((0, 1, -1), "modern") == (
        "Alfred Pennyworth", "Severus Snape",
    )
    assert cube.roster((0, -1, -1), "historical") == ("Thomas More", "Simone Weil")


def test_the_eight_new_edges_carry_the_session_24_round():
    """The whole round, pinned: 8 cells × 3 sets × 2 readings = 48 seats."""
    assert len(NEW_EDGES) == 8
    assert cube.ROSTER[(-1, -1, 0)] == {          # Prudence / Indifference
        "archetypal": ("Solomon", "Pontius Pilate"),
        "historical": ("Elizabeth I", "Adolf Eichmann"),
        "modern": ("Spock", "Dr. Manhattan"),
    }
    assert cube.ROSTER[(1, 1, 0)] == {            # Ardor / Vendetta
        "archetypal": ("Romeo", "Medea"),
        "historical": ("Joan of Arc", "Genghis Khan"),
        "modern": ("Katniss Everdeen", "Inigo Montoya"),
    }
    assert cube.ROSTER[(-1, 1, 0)] == {           # Steadfastness / Machination
        "archetypal": ("Ruth", "Iago"),
        "historical": ("Rosa Parks", "Cardinal Richelieu"),
        "modern": ("Brienne of Tarth", "Petyr Baelish"),
    }
    assert cube.ROSTER[(1, -1, 0)] == {           # Reform / Zealotry
        "archetypal": ("Nehemiah", "Saul of Tarsus"),
        "historical": ("Abraham Lincoln", "Oliver Cromwell"),
        "modern": ("Hermione Granger", "Rorschach"),
    }
    assert cube.ROSTER[(-1, 0, -1)] == {          # Meekness / Despair
        "archetypal": ("Isaac", "Cain"),
        "historical": ("Francis of Assisi", "Vincent van Gogh"),
        "modern": ("Frodo Baggins", "Théoden"),
    }
    assert cube.ROSTER[(1, 0, 1)] == {            # Aspiration / Megalomania
        "archetypal": ("Daedalus", "Icarus"),
        "historical": ("Muhammad Ali", "Alexander the Great"),
        "modern": ("Rocky Balboa", "Tony Stark"),
    }
    assert cube.ROSTER[(-1, 0, 1)] == {           # Self-Mastery / Disdain
        "archetypal": ("Odysseus", "Coriolanus"),
        "historical": ("Bruce Lee", "Diogenes"),
        "modern": ("Uncle Iroh", "Tywin Lannister"),
    }
    assert cube.ROSTER[(1, 0, -1)] == {           # Diligence / Servility
        "archetypal": ("Martha of Bethany", "Uriah Heep"),
        "historical": ("Mother Teresa", "Vidkun Quisling"),
        "modern": ("Andy Dufresne", "Dobby"),
    }


# --- the repeat law -------------------------------------------------------------
def test_a_figure_repeats_only_between_a_vertex_and_its_flat_shadow():
    """CUBE.md §The Rosters: one figure, one seat — with exactly one
    exception SHAPE. Two cells may share a person when they differ only
    in X, because that is the same seat read with the depth axis dropped
    (the Character wheel is the Cube at depth zero). Proved from the
    coordinates, so a careless reuse anywhere else fails here."""
    seats: dict[str, list[tuple[int, int, int]]] = {}
    for cell in cube.ROSTER:
        for name in _people(cell):
            seats.setdefault(name, []).append(cell)
    for name, cells in seats.items():
        unique = sorted(set(cells))
        assert len(unique) <= 2, (name, unique)
        if len(unique) == 2:
            first, second = unique
            assert first[1:] == second[1:], (name, unique)   # only X differs


def test_the_new_round_seats_every_person_exactly_once():
    """The 48 new edge seats and the 4 sacred echoes introduce 52 people,
    each new to the canon: no new figure repeats, and none takes a seat
    the sealed 108 already hold."""
    sealed = {
        name
        for cell in cube.ROSTER if cell not in NEW_EDGES
        for name in _people(cell)
    }
    fresh = [name for cell in sorted(NEW_EDGES) for name in _people(cell)]
    fresh += [
        figure
        for seat in ("Jesus Christ", "The Devil")
        for register, figure in cube.SACRED_FIGURES[seat].items()
        if register != "archetypal"          # the principals ARE the myth set
    ]
    assert len(fresh) == 52
    assert len(set(fresh)) == 52, "a new figure was seated twice"
    assert not (set(fresh) & sealed), set(fresh) & sealed


# --- the sacred corners ---------------------------------------------------------
def test_the_sacred_corners_hold_their_principals_and_two_echoes():
    """Owner 2026-07-28: the mythic principals are Jesus and the Devil
    themselves; the other two registers carry echoes."""
    for seat in ("Jesus Christ", "The Devil"):
        assert cube.sacred_figure(seat, "archetypal") == seat
    assert cube.sacred_figure("Jesus Christ", "historical") == "Maximilian Kolbe"
    assert cube.sacred_figure("Jesus Christ", "modern") == "Aslan"
    assert cube.sacred_figure("The Devil", "historical") == "Nero"
    assert cube.sacred_figure("The Devil", "modern") == "Sauron"


def test_the_centre_takes_no_figure_in_any_register():
    """The One contains all six powers without being ruled by any, and
    every human exemplar is ruled by something — the empty Exemplar
    column is doctrine, not a gap (owner verdict 2026-07-28)."""
    assert cube.THE_ONE_SEAT in cube.SACRED_TRIO_NAMES
    assert cube.THE_ONE_SEAT not in cube.SACRED_FIGURES
    for register in cube.FIGURE_SETS:
        assert cube.sacred_figure(cube.THE_ONE_SEAT, register) is None


def test_an_unknown_seat_or_register_raises_instead_of_guessing():
    """Rule #1: the grid is complete by construction, so a miss is a bug
    and must be loud."""
    with pytest.raises(KeyError):
        cube.roster((0, 1, 0), "mythical")
    with pytest.raises(KeyError):
        cube.roster((0, 0, 0), "archetypal")        # the centre is no cell
    with pytest.raises(KeyError):
        cube.sacred_figure("Lucifer", "modern")


# --- the wiring -----------------------------------------------------------------
def test_the_rose_reads_forty_eight_seats_through_the_roster():
    """CUBE.md §The Rose's ~~OPEN~~: the eight 2D characters and the eight
    3D vertices in three sets — the 48 seats — resolve through the ONE
    roster table, Legacy and Prophecy alike."""
    seen = set()
    for wheel in ("paint", "light"):
        key = archetypes.grid_key("rose", wheel)
        for index in range(len(archetypes.figures(key))):
            for register in cube.FIGURE_SETS:
                luminous, fallen = archetypes.roster_names(key, index, register)
                assert luminous and fallen
                seen.add((key, index, register))
    assert len(seen) == 48


def test_the_two_cube_wheels_seat_the_cells_their_names_claim():
    """Each arm's `cell` must be the cube seat its own two names hold —
    the wheel and the canon table cannot drift apart."""
    for key in ("compass_character", "rose_vertices"):
        for fig in archetypes.figures(key):
            cell = fig["cell"]
            axis = next(
                a for a in cube.AXES
                if cell in (a.cold.coords, a.warm.coords)
            )
            end = axis.cold if axis.cold.coords == cell else axis.warm
            assert (fig["name"], fig["row2"]) == (end.luminous, end.fallen)


def test_only_the_cube_wheels_answer_the_roster():
    """An archetype whose arms are not cube seats raises rather than
    inventing a figure for them."""
    with pytest.raises(KeyError):
        archetypes.roster_names("trinity_paint", 0, "archetypal")


def test_the_star_the_roster_and_the_register_speak_one_word():
    """Session 24 retired the star map's private "myth": the three Rose
    stars name the very sets the roster and the disk registers name."""
    assert set(constants.ROSE_STAR_SETS.values()) == set(cube.FIGURE_SETS)
    assert cube.FIGURE_SETS == ("archetypal", "historical", "modern")
