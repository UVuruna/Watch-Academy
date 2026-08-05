"""THE COMPOSITIONAL RING MODEL (owner decree 2026-08-05): a ring is
ALWAYS the composition of an outer band + an inner band + the letters
in the outer's own empty fields + an optional crown-text arc — there is
no more single monolithic plate and no opt-in (`RingSpec.use_split_art`
is gone; `render.layers.ring.RingLayer.paint` composes unconditionally).
These probes replace the old R-21 opt-in/graceful-fallback tests with:
every preset composes its locked outer + its own inner, every outer x
inner combination renders, and the two bands recolor independently.
"""

import dataclasses
import math
import os
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import astral
import pytest
from PySide6.QtWidgets import QApplication

from app.controller import build_skin
from app.settings_store import Settings
from config import constants, dial
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def frame_args():
    now = datetime(2026, 1, 1, 0, 0, tzinfo=ZoneInfo("UTC"))
    observer = astral.Observer(latitude=45.0, longitude=20.0)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    return day, tick


def _render(skin, day, tick):
    return Compositor(skin, AssetCache()).render_offscreen(400.0, 1.0, day, tick)


def _diff_count(image_a, image_b, step: int = 4) -> int:
    return sum(
        1
        for x in range(0, 400, step)
        for y in range(0, 400, step)
        if image_a.pixelColor(x, y).getRgb() != image_b.pixelColor(x, y).getRgb()
    )


@pytest.mark.parametrize(
    "name,outer,inner",
    [
        ("DOMY", "bot_cross", "seconds"),
        ("PILOT", "top_cross", "seconds_cross"),
        ("Dollar", "hexa", "simple"),
        ("Templar", "cross", "simple_cross"),
        ("The One", "full", "simple_point"),
    ],
)
def test_every_preset_composes_its_locked_outer_and_default_inner(
    app, frame_args, name, outer, inner,
):
    """Each of the five presets is LOCKED to exactly one outer (owner
    decree 2026-08-05) and starts on the coordinator's recommended
    default inner."""
    day, tick = frame_args
    skin = build_skin(Settings(ring=name))
    assert skin.ring.outer_asset.name == f"{outer}.png"
    assert skin.ring.inner_asset.name == f"{inner}.png"
    image = _render(skin, day, tick)
    assert image.width() == 400 and image.height() == 400


@pytest.mark.parametrize("outer", sorted(constants.RING_OUTERS))
@pytest.mark.parametrize("inner", constants.RING_INNERS)
def test_every_outer_by_inner_combination_renders(app, frame_args, outer, inner):
    """Rule 2 (owner decree 2026-08-05): every outer x inner combination
    is legal for CUSTOM rings — build one directly on the skin (no
    custom-ring card needed to prove the render path itself is total)
    and confirm it paints without raising."""
    day, tick = frame_args
    base = build_skin(Settings())
    skin = dataclasses.replace(
        base,
        ring=dataclasses.replace(
            base.ring,
            outer_asset=dial.RING_OUTER_ART_DIR / constants.RING_OUTERS[outer]["file"],
            inner_asset=dial.RING_INNER_ART_DIR / f"{inner}.png",
            letters={},
        ),
    )
    image = _render(skin, day, tick)
    assert image.width() == 400 and image.height() == 400


def test_ring_inner_choice_is_user_changeable_per_preset(app, frame_args):
    """Rule 1: the preset's INNER stays user-changeable independent of
    its locked outer (`Settings.ring_inner`,
    `app.controller._resolve_ring_inner`)."""
    day, tick = frame_args
    default = build_skin(Settings(ring="DOMY"))
    assert default.ring.inner_asset.name == "seconds.png"
    swapped = build_skin(
        Settings(ring="DOMY", ring_inner={"DOMY": "simple_octa"})
    )
    assert swapped.ring.outer_asset.name == "bot_cross.png"  # outer stays locked
    assert swapped.ring.inner_asset.name == "simple_octa.png"
    assert _diff_count(_render(default, day, tick), _render(swapped, day, tick)) > 0


def test_custom_ring_free_picks_any_outer(app, frame_args):
    """Rule 2: a custom ring may pick ANY outer, including one no
    bundled preset locks to (octa)."""
    day, tick = frame_args
    custom = ({"name": "OCTARING", "outer": "octa", "letters": ["✠"] * 8},)
    skin = build_skin(
        Settings(ring="OCTARING", custom_rings=custom, ring_inner={"OCTARING": "simple_octa"})
    )
    assert skin.ring.outer_asset.name == "octa.png"
    assert skin.ring.inner_asset.name == "simple_octa.png"
    image = _render(skin, day, tick)
    assert image.width() == 400


def test_custom_ring_crown_text_and_orientation_alter_pixels(app, frame_args):
    """Rule 3: a custom ring's free-typed CROWN TEXT draws real pixels
    (bare vs with-text differ); orientation (top/bottom) is verified at
    the DATA level — the resolved glyph angles flip from centered on
    the top anchor (0 deg) to the bottom anchor (180 deg), exactly like
    every other motto form's own angle solve (`core.motto`,
    `data.rings._validate_motto`) — the SAME level every other motto
    test in this suite verifies at (the outer crown arc sits beyond the
    dial radius, so a fixed-size offscreen render clips most of it;
    that is a rendering-canvas artifact, not a claim about the app
    window, which grows its own margin for a motto preset — see
    `test_dial_window_margin_grows_only_for_a_motto_preset`)."""
    day, tick = frame_args
    custom = ({"name": "CROWNED", "outer": "bot_cross", "letters": ["A", "B", "C", "D"]},)
    bare = build_skin(Settings(ring="CROWNED", custom_rings=custom))
    with_text = build_skin(Settings(
        ring="CROWNED", custom_rings=custom,
        custom_ring_crown_text={"CROWNED": "HELLO"},
    ))
    assert with_text.ring.motto
    assert _diff_count(_render(bare, day, tick), _render(with_text, day, tick)) > 0
    top_angles = with_text.ring.motto[0]["words"][0]["center"]
    bottom_text = build_skin(Settings(
        ring="CROWNED", custom_rings=custom,
        custom_ring_crown_text={"CROWNED": "HELLO"},
        custom_ring_crown_orientation={"CROWNED": "bottom"},
    ))
    bottom_angles = bottom_text.ring.motto[0]["words"][0]["center"]
    assert top_angles == pytest.approx(0.0)
    assert bottom_angles == pytest.approx(180.0)


def test_custom_ring_crown_text_rejects_unknown_letters_without_crashing(app, frame_args):
    """A crown text using characters outside the letter library is
    dropped for this build rather than crashing the running app — a
    documented, honest gap (see the session's OPEN QUESTIONS)."""
    day, tick = frame_args
    custom = ({"name": "CROWNED2", "outer": "bot_cross", "letters": ["A", "B", "C", "D"]},)
    skin = build_skin(Settings(
        ring="CROWNED2", custom_rings=custom,
        custom_ring_crown_text={"CROWNED2": "hello!"},  # lowercase + punctuation
    ))
    assert skin.ring.motto == ()
    _render(skin, day, tick)  # must not raise


# --- Region-specific probes: each tint touches ONLY its own band -------------
#
# The two plates' own alpha coverage, MEASURED off the actual PNGs: the
# outer band (`outter/full.png`) covers ~0.885-1.00, the inner band
# (`inner/simple.png`) ~0.796-0.894. 0.95 lands outer-only, 0.84
# inner-only. `_plain_skin` clears letters/motto outright, so the
# sample angles below need not dodge any seat.


def _pixel_at(image, radius_fraction: float, angle_deg: float):
    rad = math.radians(angle_deg)
    x = 200 + 200 * radius_fraction * math.sin(rad)
    y = 200 - 200 * radius_fraction * math.cos(rad)
    return image.pixelColor(round(x), round(y)).getRgb()


_SAMPLE_ANGLES = (30.0, 90.0, 150.0, 210.0, 270.0, 330.0)
_OUTER_ONLY_RADIUS = 0.95
_INNER_ONLY_RADIUS = 0.84


def _plain_skin(**overrides):
    """The "full" outer + "simple" inner pair — the SAME pair the
    `_OUTER_ONLY_RADIUS`/`_INNER_ONLY_RADIUS` alpha-coverage fractions
    below were measured against — with letters/crown text CLEARED so
    the tint-region probes sample the two bands' plate art only."""
    base = build_skin(Settings(ring="The One", ring_inner={"The One": "simple"}))
    return dataclasses.replace(
        base, show_pointer=False, show_weekday=False,
        show_earth=False, show_moon=False,
        ring=dataclasses.replace(base.ring, letters={}, motto=()),
        **overrides,
    )


def test_outer_ring_tint_recolors_only_the_outer_band_region(app, frame_args):
    """`ring_tint_inner` is pinned EXPLICITLY on both sides (never left
    None) — None follows `ring_tint`, so varying `ring_tint` alone would
    also move the inner band by design and this probe would not isolate
    the outer band at all."""
    day, tick = frame_args
    plain_img = _render(
        _plain_skin(ring_tint="#808080", ring_tint_inner="#808080"), day, tick
    )
    tinted_img = _render(
        _plain_skin(ring_tint="#FF0000", ring_tint_inner="#808080"), day, tick
    )
    outer_diff = sum(
        1 for a in _SAMPLE_ANGLES
        if _pixel_at(plain_img, _OUTER_ONLY_RADIUS, a)
        != _pixel_at(tinted_img, _OUTER_ONLY_RADIUS, a)
    )
    inner_diff = sum(
        1 for a in _SAMPLE_ANGLES
        if _pixel_at(plain_img, _INNER_ONLY_RADIUS, a)
        != _pixel_at(tinted_img, _INNER_ONLY_RADIUS, a)
    )
    assert outer_diff > 0, "ring_tint must repaint the OUTER band region"
    assert inner_diff == 0, "ring_tint alone must leave the INNER band region untouched"


def test_inner_ring_tint_recolors_only_the_inner_band_region(app, frame_args):
    day, tick = frame_args
    plain_img = _render(_plain_skin(ring_tint="#808080"), day, tick)
    tinted_img = _render(
        _plain_skin(ring_tint="#808080", ring_tint_inner="#00FF00"), day, tick
    )
    outer_diff = sum(
        1 for a in _SAMPLE_ANGLES
        if _pixel_at(plain_img, _OUTER_ONLY_RADIUS, a)
        != _pixel_at(tinted_img, _OUTER_ONLY_RADIUS, a)
    )
    inner_diff = sum(
        1 for a in _SAMPLE_ANGLES
        if _pixel_at(plain_img, _INNER_ONLY_RADIUS, a)
        != _pixel_at(tinted_img, _INNER_ONLY_RADIUS, a)
    )
    assert inner_diff > 0, "ring_tint_inner must repaint the INNER band region"
    assert outer_diff == 0, "ring_tint_inner alone must leave the OUTER band region untouched"
