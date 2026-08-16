"""THE DISC IS THE MEASURE, THE SHINE IS EXTRA (owner order 2026-08-16).

Measured against the SHIPPED plates, not a fixture: the whole defect was
that a real file's body filled two thirds of its frame while the code
sized the frame.
"""

import pytest

from config import dial, paths
from render.body_disc import disc_match_scale, filled_disc_fraction

ECLIPSE = paths.assets_dir() / "weeks/celestial_bodies/planets/primary/photo/Sun_Eclipse_gpt.png"
SUN = paths.assets_dir() / "weeks/celestial_bodies/planets/primary/photo/Sun.png"
MOON = paths.assets_dir() / "weeks/celestial_bodies/planets/primary/photo/Moon.png"


def _present(asset):
    return paths.existing_art_file(asset) is not None


@pytest.mark.skipif(not _present(MOON), reason="bundled art absent")
def test_an_ordinary_body_fills_its_frame():
    """The premise the whole rule rests on: a plain body plate IS its
    frame, so nothing about it needs correcting."""
    assert filled_disc_fraction(MOON) > 0.95
    assert filled_disc_fraction(SUN) > 0.9
    assert disc_match_scale(MOON) == 1.0
    assert disc_match_scale(SUN) == 1.0


@pytest.mark.skipif(not _present(ECLIPSE), reason="bundled art absent")
def test_the_eclipsed_sun_is_measured_by_its_disc():
    """His defect, in numbers: the black disc reaches 0.70 of the plate's
    half-size while the Moon beside it reaches 0.99, so stamping the
    FRAME drew a Sunday two thirds the size of its neighbours."""
    filled = filled_disc_fraction(ECLIPSE)
    assert 0.6 < filled < 0.8, filled
    scale = disc_match_scale(ECLIPSE)
    assert scale > 1.2, scale
    # the corrected stamp puts the DISC on the roundel's own diameter
    assert filled * scale == pytest.approx(
        dial.BODY_DISC_REFERENCE_FILL, abs=0.02
    )


def test_the_correction_is_a_list_and_never_shrinks():
    """A rule for every body would resize the instrument to fix one
    plate — and the planet SIGNS, a thin glyph in a wide frame, would
    blow up fourfold. Nothing unlisted moves, and nothing ever gets
    smaller than the seat it sits in."""
    assert dial.BODY_DISC_MATCH_PREFIXES == ("Sun_Eclipse",)
    sign = paths.assets_dir() / "weeks/celestial_bodies/planets/primary/sign/Sun_gem.png"
    assert disc_match_scale(sign) == 1.0
    for asset in (MOON, SUN, sign):
        assert disc_match_scale(asset) >= 1.0
    assert disc_match_scale(ECLIPSE) <= dial.BODY_DISC_MATCH_MAX
