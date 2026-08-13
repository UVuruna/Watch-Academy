"""THE ANGULAR WEDGE — the fixed-jewel occlusion (owner ballot verdict
2026-08-13).

Pure geometry, no Qt anywhere in this file: the rule lives in
`core.numerals` precisely so it can be pinned without a QApplication.
Three things are held here — the owner's own worked example, his
partial-cut rule, and the promise that the DEFAULT scope changes
nothing.
"""

import pytest

from config import dial
from core import numerals


TEMPLAR_JEWELS = (6, 12, 18, 24)          # ring counting, midnight = 24
# The owner's example: solar noon falls at 13h, so the star stands at
# +15 deg and the world offset that brings it to the top is its NEGATIVE
# (`core.world.solar_part_deg`). One hour of rotation, exactly.
ONE_HOUR_OFFSET = -dial.NUMERAL_HOUR_STEP_DEG


@pytest.fixture
def jewel_half() -> float:
    return numerals.jewel_arc_half_deg()


def test_the_wedge_halves_come_from_the_rings_own_seating(jewel_half):
    """No magic number: the jewel's wedge is its stamped height on its
    stamped radius, and the numeral's is half a seat pitch."""
    assert jewel_half == pytest.approx(
        numerals.arc_degrees(
            dial.RING_JEWEL_ART_SCALE, dial.outer_centreline(1.0) / 2.0
        ) / 2.0
    )
    assert numerals.numeral_arc_half_deg() == dial.NUMERAL_HOUR_STEP_DEG / 2.0
    # The jewels-size slider is part of the answer — a bigger letter
    # covers more of the band, and the occlusion must know it.
    assert numerals.jewel_arc_half_deg(jewels_scale=2.0) == pytest.approx(
        2.0 * jewel_half
    )


def test_the_owners_worked_example(jewel_half):
    """Templar's jewels at 6/12/18/24, one hour of rotation with solar
    noon at 13h: the numerals 7, 13, 19 and 1 slide under the four
    jewels and are not drawn."""
    hidden = numerals.occluded_numeral_hours(
        TEMPLAR_JEWELS, ONE_HOUR_OFFSET, jewel_half
    )
    assert set(hidden) == {1, 7, 13, 19}


def test_the_vacated_seats_finally_carry_their_numbers(jewel_half):
    """The other half of his order: with the jewels fixed, the labels
    6, 12, 18 and 0 — never drawn on any release before, because a
    jewel sat on each — are composed into the band, and midnight reads
    "0"."""
    hidden = numerals.occluded_numeral_hours(
        TEMPLAR_JEWELS, ONE_HOUR_OFFSET, jewel_half
    )
    drawn = numerals.numeral_hours(hidden)
    assert {0, 6, 12, 18} <= set(drawn)
    assert numerals.hour_labels()[0] == "0"


def test_a_jewel_that_clips_two_numerals_suppresses_both(jewel_half):
    """His partial-cut rule. Half an hour of rotation stands every jewel
    exactly between two seats, so each one clips two numerals — and both
    go. Never half a numeral under a letter."""
    hidden = numerals.occluded_numeral_hours(
        TEMPLAR_JEWELS, ONE_HOUR_OFFSET / 2.0, jewel_half
    )
    assert set(hidden) == {0, 1, 6, 7, 12, 13, 18, 19}
    # Eight suppressed, sixteen drawn — and never a THIRD neighbour.
    assert len(numerals.numeral_hours(hidden)) == 16


def test_no_rotation_hides_exactly_the_seats_the_jewels_stand_on(jewel_half):
    """At offset 0 the new scope must agree with the old one: the four
    jewel seats carry no numeral, everything else does."""
    hidden = numerals.occluded_numeral_hours(TEMPLAR_JEWELS, 0.0, jewel_half)
    assert set(hidden) == {0, 6, 12, 18}
    assert set(hidden) == set(numerals.occluded_numeral_hours(
        TEMPLAR_JEWELS, 360.0, jewel_half
    )), "a full turn is the same dial"


def test_touching_arcs_do_not_overlap(jewel_half):
    """"Overlap at all" is strict: two arcs that merely touch leave the
    numeral standing. Pinned so a later `<=` cannot quietly widen the
    rule by one seat."""
    reach = jewel_half + numerals.numeral_arc_half_deg()
    # Offset -reach puts hour 12's own seat exactly `reach` away from the
    # jewel standing at 12: the arcs touch and nothing overlaps.
    assert 12 not in numerals.occluded_numeral_hours(
        (12,), -reach, jewel_half
    )
    assert 12 in numerals.occluded_numeral_hours(
        (12,), -(reach - 1e-9), jewel_half
    )


def test_the_scopes_are_named_for_what_they_do():
    assert dial.WORLD_ROTATION_SCOPES == ("all_turn", "numerals_turn")
    assert dial.WORLD_ROTATION_SCOPE_DEFAULT == "all_turn"
    assert set(dial.WORLD_ROTATION_SCOPE_LABELS) == set(
        dial.WORLD_ROTATION_SCOPES
    )


def test_an_older_settings_file_loads_clean_on_the_default(tmp_path):
    """THE STANDING ORDER: a new setting absent from a stored file is
    the DEFAULT, and the default is today's behaviour — the owner sees
    nothing change until he picks. Proven on a REAL file with the key
    deleted, not on the dataclass alone."""
    import json

    from app.settings_store import Settings, SettingsStore

    assert Settings().world_rotation_scope == "all_turn"
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    store.save(Settings())
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw.pop("world_rotation_scope") == "all_turn"
    path.write_text(json.dumps(raw), encoding="utf-8")
    assert SettingsStore(path).load().world_rotation_scope == "all_turn"
