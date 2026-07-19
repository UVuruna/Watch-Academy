"""The outer Great Seal motto arc — per-glyph angle math (TASK 1, owner
"može radi" 2026-07-19, CANON.md §The Banknote)."""

import pytest

from core.motto import _occurrence_index, motto_glyph_angles


def test_occurrence_index_finds_the_nth_appearance():
    text = "NOVUS ORDO SECLORUM"
    assert _occurrence_index(text, "N", 1) == 0
    # O appears at 1, 6, 9, 15 — the 3rd is the one ENDING "ORDO".
    assert _occurrence_index(text, "O", 1) == 1
    assert _occurrence_index(text, "O", 2) == 6
    assert _occurrence_index(text, "O", 3) == 9
    assert _occurrence_index(text, "O", 4) == 15
    # S appears at 4, 11 — the 2nd STARTS "SECLORUM".
    assert _occurrence_index(text, "S", 2) == 11
    assert _occurrence_index(text, "M", 1) == 18


def test_occurrence_index_raises_when_not_enough_occurrences():
    with pytest.raises(ValueError):
        _occurrence_index("NOVUS ORDO SECLORUM", "O", 5)
    with pytest.raises(ValueError):
        _occurrence_index("NOVUS ORDO SECLORUM", "A", 1)   # no A at all


# --- The two Great Seal mottos, exactly as Database/ring_presets.json ships them ---


def test_annuit_coeptis_pinned_letters_land_on_their_seats():
    """A on 8h, O on noon, S on 16h — within a fraction of a degree
    (owner requirement) means exactly, since this is closed-form math."""
    text = "ANNUIT COEPTIS"
    angles = motto_glyph_angles(text, (("A", 1, 8), ("O", 1, 12), ("S", 1, 16)))
    assert len(angles) == len(text)
    assert angles[0] == pytest.approx(300.0)     # A -> 8h
    assert angles[8] == pytest.approx(360.0)     # O -> noon (unwrapped)
    assert angles[13] == pytest.approx(420.0)    # S -> 16h (unwrapped)
    # Even spacing WITHIN each pin-to-pin segment.
    first_segment = [angles[i + 1] - angles[i] for i in range(0, 8)]
    assert first_segment == pytest.approx([7.5] * 8)
    second_segment = [angles[i + 1] - angles[i] for i in range(8, 13)]
    assert second_segment == pytest.approx([12.0] * 5)
    # The whole run is monotonically increasing (reads clockwise).
    assert all(b > a for a, b in zip(angles, angles[1:]))


def test_novus_ordo_seclorum_pinned_letters_land_on_their_seats():
    """N on 4h, O on noon (the 3rd O — ending "ORDO"), S on 16h (the
    2nd S — starting "SECLORUM"), M on 20h."""
    text = "NOVUS ORDO SECLORUM"
    angles = motto_glyph_angles(
        text, (("N", 1, 4), ("O", 3, 12), ("S", 2, 16), ("M", 1, 20))
    )
    assert len(angles) == len(text)
    assert angles[0] == pytest.approx(240.0)     # N -> 4h
    assert angles[9] == pytest.approx(360.0)     # O (3rd) -> noon
    assert angles[11] == pytest.approx(420.0)    # S (2nd) -> 16h
    assert angles[18] == pytest.approx(480.0)    # M -> 20h (unwrapped)
    first_segment = [angles[i + 1] - angles[i] for i in range(0, 9)]
    assert first_segment == pytest.approx([120.0 / 9] * 9)
    third_segment = [angles[i + 1] - angles[i] for i in range(11, 18)]
    assert third_segment == pytest.approx([60.0 / 7] * 7)
    assert all(b > a for a, b in zip(angles, angles[1:]))
    # The two mottos' shared pins (O at noon, S at 16h) land at the
    # IDENTICAL mod-360 angle as ANNUIT COEPTIS's own — the "MASON
    # reads twice" design (core/motto.md's Design Decisions).
    annuit = motto_glyph_angles(
        "ANNUIT COEPTIS", (("A", 1, 8), ("O", 1, 12), ("S", 1, 16))
    )
    assert angles[9] % 360.0 == pytest.approx(annuit[8] % 360.0)
    assert angles[11] % 360.0 == pytest.approx(annuit[13] % 360.0)


def test_pins_must_cover_first_and_last_character():
    with pytest.raises(ValueError):
        # Missing the final character's pin.
        motto_glyph_angles("ANNUIT COEPTIS", (("A", 1, 8), ("O", 1, 12)))
    with pytest.raises(ValueError):
        # Missing the first character's pin.
        motto_glyph_angles("ANNUIT COEPTIS", (("O", 1, 12), ("S", 1, 16)))


def test_pins_need_at_least_two_and_must_not_collide():
    with pytest.raises(ValueError):
        motto_glyph_angles("ANNUIT COEPTIS", (("A", 1, 8),))
    with pytest.raises(ValueError):
        # Two different pins resolving to the SAME character index.
        motto_glyph_angles(
            "ANNUIT COEPTIS",
            (("A", 1, 8), ("A", 1, 12), ("S", 1, 16)),
        )


def test_pins_out_of_reading_order_still_resolve_by_index():
    """`pins` may be given in any order — resolution sorts by the
    RESOLVED character index, not by argument order."""
    forward = motto_glyph_angles(
        "ANNUIT COEPTIS", (("A", 1, 8), ("O", 1, 12), ("S", 1, 16))
    )
    shuffled = motto_glyph_angles(
        "ANNUIT COEPTIS", (("S", 1, 16), ("A", 1, 8), ("O", 1, 12))
    )
    assert forward == shuffled
