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
    """No magic number: the jewel's wedge is its stamped size on its
    stamped radius, and the unmeasured numeral's is half a seat pitch."""
    radius = dial.outer_centreline(1.0) / 2.0
    assert jewel_half == pytest.approx(
        numerals.ink_arc_half_deg(
            dial.RING_JEWEL_ART_SCALE, dial.RING_JEWEL_ART_SCALE, radius,
        )
    )
    assert numerals.numeral_arc_half_deg() == dial.NUMERAL_HOUR_STEP_DEG / 2.0
    # The jewels-size slider is part of the answer — a bigger letter
    # covers more of the band, and the occlusion must know it.
    assert numerals.jewel_arc_half_deg(jewels_scale=2.0) > 1.9 * jewel_half
    # The CORNER, not the centreline: a plate's near corner leans
    # further around the dial than the middle of its top edge, so the
    # honest wedge is wider than the flat-arc reading it replaced.
    assert jewel_half > numerals.arc_degrees(
        dial.RING_JEWEL_ART_SCALE, radius,
    ) / 2.0


def test_the_jewel_wedge_follows_the_plates_own_shape():
    """THE INK WEDGE (owner order 2026-08-13): the square assumption is
    gone. `M.png` is 750 x 512 on the owner's masters and `I.png` is
    287 x 512 — the same height, and nothing like the same width."""
    square = numerals.jewel_arc_half_deg()
    wide = numerals.jewel_arc_half_deg(aspect=750 / 512)
    narrow = numerals.jewel_arc_half_deg(aspect=287 / 512)
    assert narrow < square < wide
    # The Eye's shine masters are stamped larger than a plain letter
    # (`RingSkin.jewel_zoom`), and the wedge must know that too.
    assert numerals.jewel_arc_half_deg(zoom=1.5) > square


def test_the_tilt_turns_the_ink_and_the_wedge_turns_with_it():
    """The TILT term: an `upright` numeral stands level with the screen
    while the band curves away under it, so its ink no longer lies along
    the arc and the wedge must be read from the turned rectangle. Which
    way that goes is the SHAPE's business — a wide glyph reaches
    furthest lying flat, a tall one when it is stood across the band —
    and the geometry is mirror-symmetric, because a seat left of the top
    leans exactly as far as its twin on the right."""
    radius = dial.outer_centreline(1.0) / 2.0
    wide = (0.11, 0.055)
    tall = (0.055, 0.11)
    assert numerals.ink_arc_half_deg(*wide, radius, 90.0) < (
        numerals.ink_arc_half_deg(*wide, radius, 0.0)
    )
    assert numerals.ink_arc_half_deg(*tall, radius, 90.0) > (
        numerals.ink_arc_half_deg(*tall, radius, 0.0)
    )
    assert numerals.ink_arc_half_deg(*wide, radius, -37.0) == pytest.approx(
        numerals.ink_arc_half_deg(*wide, radius, 37.0)
    )


def test_a_measured_seat_may_carry_its_number_where_the_wedge_hid_it():
    """The owner's whole complaint in one assertion: a NARROW jewel and
    a single-digit numeral do not touch at a distance the old
    whole-seat rule called a collision."""
    narrow = numerals.jewel_arc_half_deg(aspect=287 / 512)      # an I
    single_digit = {hour: 3.54 for hour in range(24)}           # measured
    gap = -6.5                                                  # deg apart
    assert 12 in numerals.occluded_numeral_hours(
        (12,), gap, numerals.jewel_arc_half_deg(),
    ), "the old square-against-whole-seat rule hid it"
    assert 12 not in numerals.occluded_numeral_hours(
        (12,), gap, narrow, single_digit,
    ), "the measured ink leaves it standing"


def test_the_midpoint_is_where_two_numerals_still_fall():
    """His own words for the rare case, now that the rule measures:
    both numerals go when the jewel falls exactly BETWEEN two seats —
    but only when the ink really reaches that far. A wide letter beside
    two-digit numbers does; a narrow letter beside single digits does
    not touch either, which is exactly the hole this round removed."""
    midway = -dial.NUMERAL_HOUR_STEP_DEG / 2.0        # 12:30 on his dial
    wide = numerals.jewel_arc_half_deg(aspect=750 / 512)
    two_digit = {hour: 7.06 for hour in range(24)}
    assert set(numerals.occluded_numeral_hours(
        (12,), midway, wide, two_digit,
    )) == {12, 13}
    narrow = numerals.jewel_arc_half_deg(aspect=287 / 512)
    single_digit = {hour: 3.54 for hour in range(24)}
    assert numerals.occluded_numeral_hours(
        (12,), midway, narrow, single_digit,
    ) == (), "neither neighbour is touched — the rare case stays rare"


def test_each_seat_may_carry_its_own_measured_half():
    """Both halves accept a per-hour mapping, and an hour the mapping
    forgot falls back to the plain wedge — so a measured caller and an
    unmeasured one can share the same loop."""
    halves = {12: 0.1}
    assert numerals.occluded_numeral_hours((12,), -6.0, halves, halves) == ()
    # Hour 12 is missing from this jewel mapping, so it falls back to
    # nothing at all, while the numeral mapping's own default (the seat
    # wedge) still stands.
    assert numerals.occluded_numeral_hours((12,), 0.0, {}, None) == (12,)


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
