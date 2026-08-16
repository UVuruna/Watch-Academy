"""THE CROWN LETTER STANDS OVER ITS OWN JEWEL (owner defect 2026-08-16).

His words, and the whole test in one line: "M from the ring and M from
MUNDORUM do not line up, O from the ring and O from ORDO do not line
up" — against a DAY screenshot where the same pins land perfectly.

A pinned crown letter is pinned to a JEWEL'S SEAT. Whatever the world
offset does to the ring it must do to both of them equally, so the two
can never drift apart. The defect was the reflection's AXIS: it came
from the DRAWN glyphs, which drop spaces, so an arc whose spaces sit
asymmetrically (MUNDORUM ORDO NUMEN, two of them) reflected about a
centre 1.41 deg off its own and carried every letter twice that. SANCIT
FŒDERA never showed it — its one space sits in the middle, so both axes
agree — which is why the misalignment looked arbitrary rather than
systematic.
"""

import json

import pytest

from config import paths
from core import angles as core_angles
from core import world
from core.crown_text import _occurrence_index
from data.rings import ring_presets

NIGHT = world.night_phase_deg(False)
# day and night, each with a real city's solar term in both signs
# (Belgrade's own golden pair, +10.76 / -4.17)
OFFSETS = (0.0, 10.76, -4.17, NIGHT, NIGHT + 10.76, NIGHT - 4.17)


def _raw_dollar():
    raw = json.loads(
        (paths.database_dir() / "ring_presets.json").read_text(encoding="utf-8")
    )
    return next(p for p in raw["presets"] if p["name"] == "Dollar")


# A pin's POSITION is not the jewel the letter belongs to. The night
# arcs are authored on the opposite half of the band frame — the mirror
# is what carries them over the top — so SANCIT's S is pinned to the 8h
# seat and only LANDS on the S jewel once the arc has been reflected.
# What the owner reads off the dial is the letter, not the seat, so that
# is what this checks: the crown's M over the ring's M, its O over Ω.
JEWEL_OF_LETTER = {"A": "A", "S": "S", "N": "N", "M": "M", "O": "Ω"}


def _pins(raw_entry):
    """`{letter index among the DRAWN letters: pinned letter}` — resolved
    exactly as `core.crown_text` resolves them, then re-indexed past the
    spaces the glyph list drops."""
    text = raw_entry["text"]
    out = {}
    for letter, occurrence, _position in raw_entry["pins"]:
        index = _occurrence_index(text, letter, occurrence)
        drawn = index - text[:index].count(" ")
        out[drawn] = letter
    return out


def _letters(entry):
    return [
        (char, angle)
        for char, angle in zip(entry["text"], entry["angles"])
        if char != " "
    ]


def _seats(entry, offset):
    """Exactly what `RingLayer._draw_crown_text` draws: the DRAWN glyphs
    (spaces dropped) reflected about the WHOLE run's own centre."""
    centre = world.arc_centre_deg(entry["angles"])
    return world.arc_seats(
        [angle for _char, angle in _letters(entry)], offset, centre,
    )


@pytest.mark.parametrize("offset", OFFSETS)
def test_every_pinned_crown_letter_stands_over_its_jewel(offset):
    preset = ring_presets()["Dollar"]
    raw = {entry["text"]: entry for entry in
           _raw_dollar()["crown_text"] + _raw_dollar()["crown_text_night"]}
    jewels = {
        jewel: core_angles.ring_position_angle(hour)
        for hour, jewel in zip(preset["positions"], preset["jewels"])
    }
    night = preset["crown_text_night"]
    checked = 0
    for entry, crossed_draws in (
        [(e, False) for e in preset["crown_text"]]
        + [(e, True) for e in night]
    ):
        centre = world.arc_centre_deg(entry["angles"])
        # the arc that is not on screen at this offset has nothing to say
        if world.arc_crosses_horizon(centre, offset) != crossed_draws:
            continue
        seats = _seats(entry, offset)
        letters = _letters(entry)
        for index, letter in _pins(raw[entry["text"]]).items():
            char, _angle = letters[index]
            jewel = JEWEL_OF_LETTER[letter]
            drift = abs(
                ((seats[index] - (jewels[jewel] + offset) + 540.0) % 360.0)
                - 180.0
            )
            assert drift < 0.01, (
                f"{entry['text']!r}: {char} sits {drift:.2f} deg from the "
                f"{jewel} jewel at offset {offset:.2f}"
            )
            checked += 1
    assert checked >= 5, f"only {checked} pins were on screen at {offset}"


def test_the_axis_is_the_whole_runs_and_the_subset_would_be_wrong():
    """The defect itself, pinned so it cannot come back."""
    entry = next(
        e for e in ring_presets()["Dollar"]["crown_text_night"]
        if e["text"] == "MUNDORUM ORDO NUMEN"
    )
    drawn = [angle for _char, angle in _letters(entry)]
    whole = world.arc_centre_deg(entry["angles"])
    subset = world.arc_centre_deg(drawn)
    assert abs(whole - subset) == pytest.approx(1.41, abs=0.02)
    off_axis = world.arc_seats(drawn, NIGHT)[0] % 360.0
    on_axis = world.arc_seats(drawn, NIGHT, whole)[0] % 360.0
    assert abs(off_axis - on_axis) == pytest.approx(2.82, abs=0.05)
