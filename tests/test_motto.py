"""The outer Great Seal motto arc — per-glyph angle math (TASK 1, owner
"može radi" 2026-07-19, CANON.md §The Banknote; corrected MOTO-FIX
round, owner correction 2026-07-19, the dollar's Great Seal reference
image)."""

import pytest

from core.angles import readable_rotation_deg
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
    """MOTO-FIX round (owner correction 2026-07-19, the Great Seal
    reference image): the TOP arc — A pinned at 8h, S at 16h, reading
    CLOCKWISE over the top through noon. Only 2 pins now (the previous
    round's own O-at-noon pin is GONE) — no motto letter pins 12h
    anymore, the arc simply passes over the G between two characters."""
    text = "ANNUIT COEPTIS"
    angles = motto_glyph_angles(text, (("A", 1, 8), ("S", 1, 16)))
    assert len(angles) == len(text)
    assert angles[0] == pytest.approx(300.0)     # A -> 8h
    assert angles[13] == pytest.approx(420.0)    # S -> 16h (unwrapped)
    # Even spacing across the WHOLE run — only one segment now (2 pins).
    step = 120.0 / 13
    spacing = [angles[i + 1] - angles[i] for i in range(0, 13)]
    assert spacing == pytest.approx([step] * 13)
    # Monotonically increasing (reads clockwise); no character lands
    # exactly on noon/360 — the arc passes OVER the G, never pins to it.
    assert all(b > a for a, b in zip(angles, angles[1:]))
    assert all(angle % 360.0 != pytest.approx(0.0) for angle in angles)


def test_novus_ordo_seclorum_pinned_letters_land_on_their_seats():
    """MOTO-FIX round (owner correction 2026-07-19): the BOTTOM arc — N
    pinned at 4h, ORDO's own final O (the 3rd "O" overall) pinned at
    the bottom (24h), M at 20h — reading COUNTERCLOCKWISE
    (`clockwise=False`), left-to-right THROUGH the bottom, same as
    reading a coin's lower banner."""
    text = "NOVUS ORDO SECLORUM"
    angles = motto_glyph_angles(
        text, (("N", 1, 4), ("O", 3, 24), ("M", 1, 20)), clockwise=False
    )
    assert len(angles) == len(text)
    assert angles[0] == pytest.approx(240.0)     # N -> 4h
    assert angles[9] == pytest.approx(180.0)     # O (3rd, ORDO's own) -> 24h
    assert angles[18] == pytest.approx(120.0)    # M -> 20h (unwrapped down)
    # Even spacing WITHIN each pin-to-pin segment — both segments span
    # exactly 9 character-steps and 60 deg, so both steps match exactly.
    first_segment = [angles[i + 1] - angles[i] for i in range(0, 9)]
    assert first_segment == pytest.approx([-60.0 / 9] * 9)
    second_segment = [angles[i + 1] - angles[i] for i in range(9, 18)]
    assert second_segment == pytest.approx([-60.0 / 9] * 9)
    # The whole run is monotonically DEcreasing (reads counterclockwise
    # — the bottom arc's own direction, core/motto.md's Design
    # Decisions).
    assert all(b < a for a, b in zip(angles, angles[1:]))
    # The bottom arc stays entirely within its own 120/240 span; the top
    # arc (recomputed here) stays entirely within its own 300/60 span —
    # MOTO-FIX round: the two mottos no longer share ANY angle (the
    # first round's "MASON reads twice" shared-O/shared-S design is
    # gone, the arcs are now angularly disjoint).
    assert all(120.0 <= (angle % 360.0) <= 240.0 for angle in angles)
    annuit = motto_glyph_angles("ANNUIT COEPTIS", (("A", 1, 8), ("S", 1, 16)))
    assert all((angle % 360.0) >= 300.0 or (angle % 360.0) <= 60.0 for angle in annuit)


def test_bottom_arc_glyph_orientation_points_top_toward_center():
    """MOTO-FIX round: `readable_rotation_deg` (shared by every ring
    glyph, `render.layers._draw_ring_glyph`) needs no new flag for the
    bottom arc's own "tops inward" convention — it already derives this
    from the angle alone, unchanged by this round. At the bottom dead
    center (180 deg, ORDO's own O pin) the rotation is 0: with no
    rotation applied, the glyph's own top edge points toward screen-up,
    which at the BOTTOM of the dial is toward the CENTER (inward) — the
    classic coin bottom-arc orientation, unlike the top (0 deg, the G's
    own seat) where screen-up is also dial-outward."""
    assert readable_rotation_deg(180.0) == pytest.approx(0.0)
    # Symmetric either side of bottom-dead-center, within the bottom arc.
    assert readable_rotation_deg(240.0) == pytest.approx(60.0)    # N's own seat
    assert readable_rotation_deg(120.0) == pytest.approx(-60.0)   # M's own seat
    # Contrast with the TOP arc's own pins — tops point outward there.
    assert readable_rotation_deg(300.0) == pytest.approx(-60.0)   # A's own seat
    assert readable_rotation_deg(60.0) == pytest.approx(60.0)     # S's own seat


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
