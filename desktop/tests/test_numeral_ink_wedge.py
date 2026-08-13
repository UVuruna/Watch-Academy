"""THE INK WEDGE, wired end to end (owner order 2026-08-13).

The pure geometry is pinned without Qt in
[the angular wedge](test_numeral_occlusion.py); what is pinned HERE is
that the live dial actually measures — that `occluded_hours` reads each
plate's own aspect and each numeral's own ink instead of the square
letter and the whole seat it shipped with that morning, and that the
measured rule hides FEWER numerals than the assumed one on the very
skin the owner was looking at.
"""

import os
from dataclasses import replace
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from app.controller import build_skin
from app.settings_store import Settings
from config import dial
from core import numerals
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.rings import ring_presets
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.context import RenderContext
from render.layers.numerals import (
    jewel_ink_halves, occluded_hours, plate_aspect,
)
from render.numeral_bands import numeral_ink_halves


@pytest.fixture(scope="module")
def app():
    existing = QApplication.instance()
    if existing is not None:
        return existing
    try:
        return QApplication([])
    except Exception:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        return QApplication([])


@pytest.fixture(scope="module")
def frame_args():
    now = datetime(2026, 1, 1, 12, 35, tzinfo=ZoneInfo("Europe/Belgrade"))
    observer = astral.Observer(latitude=44.8, longitude=20.5)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def _context(skin, day, tick, world_offset: float) -> RenderContext:
    """A frame with the band stood at a chosen offset — the occlusion
    reads `ctx.world_offset` and nothing else about the moment, so this
    suite can walk a whole turn without a solar calculation of its
    own."""
    return RenderContext(
        skin=skin, day=day, tick=tick, radius=400.0, cache=AssetCache(),
        dpr=1.0, world_offset=world_offset,
    )


def _turning_skin(scope: str = "numerals_turn"):
    return build_skin(replace(
        Settings(), world_mode="sky_up", world_rotation_scope=scope,
    ))


def test_a_plates_aspect_is_read_from_the_picture(app):
    """Not a constant and not a guess: the number comes from the file's
    own header (through the asset index where it is already known), and
    the owner's own masters disagree with the square it replaced."""
    from render import letter_plates

    wide = plate_aspect(letter_plates.plate_path("M"))
    narrow = plate_aspect(letter_plates.plate_path("I"))
    assert wide > 1.0 > narrow
    assert plate_aspect(letter_plates.plate_path("M")) == wide  # cached


def test_every_jewel_seat_gets_its_own_wedge(app):
    """One number per seated jewel, each built from THAT plate — a ring
    whose letters differ in width may not hand back one wedge for all
    of them."""
    skin = _turning_skin()
    halves = jewel_ink_halves(skin)
    assert set(halves) == {
        hour % dial.NUMERAL_HOUR_COUNT for hour in skin.ring.jewel_art
    }
    assert all(half > 0.0 for half in halves.values())
    square = numerals.jewel_arc_half_deg(
        skin.numeral_outer_ring_size, skin.ring_jewels_scale,
    )
    assert any(half != pytest.approx(square) for half in halves.values()), (
        "a ring of real plates cannot measure exactly square everywhere"
    )


def test_a_single_digit_claims_far_less_than_its_seat(app):
    """The number behind the owner's holes: the old rule gave every
    numeral the whole 7.5-degree half seat. A one-digit numeral does not
    come close to filling it, and a two-digit one nearly does — which is
    why the fix shows up on the single digits first."""
    halves = numeral_ink_halves(
        1200, dial.NUMERAL_OUTER_FACE_DEFAULT,
        float(dial.NUMERAL_OUTER_SIZE_DEFAULT),
        dial.NUMERAL_OUTER_RING_SIZE_DEFAULT,
        dial.NUMERAL_SEATING_DEFAULT, 0.0,
    )
    seat_wedge = numerals.numeral_arc_half_deg()
    assert halves[1] < 0.6 * seat_wedge
    assert halves[1] < halves[23] < seat_wedge
    # Bigger numerals cover more band — the size slider is in the answer.
    bigger = numeral_ink_halves(
        1200, dial.NUMERAL_OUTER_FACE_DEFAULT,
        float(dial.NUMERAL_OUTER_SIZE_DEFAULT) * 1.5,
        dial.NUMERAL_OUTER_RING_SIZE_DEFAULT,
        dial.NUMERAL_SEATING_DEFAULT, 0.0,
    )
    assert bigger[1] > halves[1]


@pytest.mark.parametrize("ring", sorted(ring_presets()))
def test_every_ring_draws_more_numbers_than_the_assumed_wedge_allowed(
    app, frame_args, ring
):
    """THE ROUND'S OWN CLAIM, on the live path and on every ring the
    program ships: over a full turn of the band the measured rule hides
    FEWER numerals than the assumed one did.

    Stated as an average on purpose, because measuring cuts BOTH ways
    and saying otherwise would be a lie: an M is 1.46 times wider than
    the square it used to be called, so at some offsets it now covers a
    neighbour the old rule left standing — which means the old rule was
    printing that numeral half under a letter, the very thing THE
    FIDELITY RULING forbids. Narrow glyphs and single digits win far
    more often than wide ones lose, and the net is what the owner sees.
    """
    day, tick = frame_args
    skin = build_skin(replace(
        Settings(), ring=ring, world_mode="sky_up",
        world_rotation_scope="numerals_turn",
    ))
    jewels = tuple(sorted(skin.ring.jewels))
    assumed_half = numerals.jewel_arc_half_deg(
        skin.numeral_outer_ring_size, skin.ring_jewels_scale,
    )
    measured = assumed = 0
    for step in range(0, 360, 5):
        offset = float(step)
        measured += len(occluded_hours(skin, _context(skin, day, tick, offset)))
        assumed += len(numerals.occluded_numeral_hours(
            jewels, offset, assumed_half,
        ))
    assert measured < assumed, (
        f"{ring}: measuring the ink drew no numbers back"
    )


def test_his_own_dial_gets_five_numbers_back(app, frame_args):
    """The owner's own screenshot, reproduced: the Dollar hexagram
    standing 2.6 degrees off its seats. The assumed wedge took TWO
    numerals per jewel — twelve gone, exactly the dial he photographed.
    The measured one takes five or six fewer, so the odd seats between
    the letters carry their numbers again.

    Counted, not enumerated: one seat of the six sits within a tenth of
    a degree of the decision and flips with the plate resolution, and a
    pinned set would make this tooth a resolution detector instead of a
    rule."""
    day, tick = frame_args
    skin = build_skin(replace(
        Settings(), ring="Dollar", world_mode="sky_up",
        world_rotation_scope="numerals_turn",
    ))
    assumed = set(numerals.occluded_numeral_hours(
        tuple(sorted(skin.ring.jewels)), 2.6,
        numerals.jewel_arc_half_deg(
            skin.numeral_outer_ring_size, skin.ring_jewels_scale,
        ),
    ))
    measured = set(occluded_hours(skin, _context(skin, day, tick, 2.6)))
    assert len(assumed) == 12, "the dial he photographed lost two per jewel"
    assert len(assumed - measured) >= 5
    assert not measured - assumed, "measuring may not add a hole here"


def test_the_shine_rays_light_a_numeral_instead_of_erasing_it(app):
    """`jewel_zoom` is padding, not letter: `RING_EYE_SHINE_ENLARGE`
    enlarges the Eye's stamp so the TRIANGLE still draws a plain
    letter's size, and the glory of rays fills the difference. Counting
    that padding as ink cost the Dollar two more numerals beside the
    Eye — a hole put back by the round that exists to remove holes."""
    skin = build_skin(replace(
        Settings(), ring="Dollar", world_mode="sky_up",
        world_rotation_scope="numerals_turn",
    ))
    zoomed = [hour for hour, z in skin.ring.jewel_zoom.items() if z != 1.0]
    assert zoomed, "the Dollar's Eye must still carry a shine zoom"
    halves = jewel_ink_halves(skin)
    for hour in zoomed:
        assert halves[hour % dial.NUMERAL_HOUR_COUNT] == pytest.approx(
            numerals.jewel_arc_half_deg(
                skin.numeral_outer_ring_size, skin.ring_jewels_scale,
                aspect=plate_aspect(skin.ring.jewel_art[hour]),
            )
        )


def test_the_other_scope_still_measures_nothing(app, frame_args):
    """`all_turn` is untouched: the jewels ride their own seats there,
    so no collision is possible and no measurement is paid for."""
    day, tick = frame_args
    skin = _turning_skin("all_turn")
    assert occluded_hours(skin, _context(skin, day, tick, 37.0)) == ()
