"""The ring OUTER/INNER split tint (R-21, owner correction 2026-08-05):
`RingLayer.paint` optionally composes the owner's new
`assets/instrument/ring/outter/`+`inner/` plates instead of the single
baked `spec.asset` band, each independently tintable
(`ring_tint`/`ring_tint_inner`). The split is gated on BOTH the active
preset's own `RingSpec.use_split_art` opt-in (False for every preset
that ships today — the art landing on disk must never by itself
repaint an existing preset) AND the art files' presence on disk
(`config.dial.RING_OUTER_ASSET`/`RING_INNER_ASSET`) — either failing
falls back to today's single-plate render, never a crash."""

import dataclasses
import math
import os
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import defaults, dial
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


def _split_art_present() -> bool:
    return dial.RING_OUTER_ASSET.exists() and dial.RING_INNER_ASSET.exists()


def test_default_preset_ignores_split_art_even_when_present_on_disk(
    app, frame_args, monkeypatch,
):
    """The owner's split art may already sit on disk (untracked); a
    preset that has NOT opted in (`use_split_art=False`, every bundled
    preset today) must render byte-identical whether the files exist or
    not — the art landing is never itself a verdict."""
    day, tick = frame_args
    base = defaults.DEFAULT_SKIN
    assert base.ring.use_split_art is False
    with_files = _render(base, day, tick)
    monkeypatch.setattr(dial, "RING_OUTER_ASSET", dial.RING_OUTER_ASSET.parent / "missing.png")
    monkeypatch.setattr(dial, "RING_INNER_ASSET", dial.RING_INNER_ASSET.parent / "missing.png")
    without_files = _render(base, day, tick)
    assert _diff_count(with_files, without_files) == 0, (
        "a preset that never opted into the split must not care whether "
        "the split art exists on disk"
    )


@pytest.mark.skipif(not _split_art_present(), reason="owner's split art not on disk")
def test_opted_in_preset_composes_the_split_plate(app, frame_args):
    """A preset that flips `use_split_art=True` (none do today; this
    probe builds one) draws the two independently-tinted bands instead
    of the single plate — the outer tint and the NEW inner tint each
    alter the composed pixels on their own."""
    day, tick = frame_args
    single = defaults.DEFAULT_SKIN
    split_ring = dataclasses.replace(single.ring, use_split_art=True)
    split = dataclasses.replace(single, ring=split_ring, ring_tint="#3050E0")

    differing_from_single = _diff_count(_render(single, day, tick), _render(split, day, tick))
    assert differing_from_single > 0, (
        "an opted-in preset with the split art present must repaint "
        "differently from the single-plate render"
    )

    inner_tinted = dataclasses.replace(split, ring_tint_inner="#E03050")
    differing_inner = _diff_count(_render(split, day, tick), _render(inner_tinted, day, tick))
    assert differing_inner > 0, (
        "ring_tint_inner must repaint the inner band independently of ring_tint"
    )


def test_opted_in_preset_falls_back_gracefully_without_the_art_files(
    app, frame_args, monkeypatch,
):
    """`use_split_art=True` with the art missing from disk (a preset
    shipped/opted-in ahead of the owner committing the files, or this
    session's own dev checkout before they land) must fall back to the
    single-plate render — never raise, never draw nothing."""
    day, tick = frame_args
    single = defaults.DEFAULT_SKIN
    split_ring = dataclasses.replace(single.ring, use_split_art=True)
    split = dataclasses.replace(single, ring=split_ring)

    monkeypatch.setattr(dial, "RING_OUTER_ASSET", dial.RING_OUTER_ASSET.parent / "missing.png")
    monkeypatch.setattr(dial, "RING_INNER_ASSET", dial.RING_INNER_ASSET.parent / "missing.png")

    fallback = _render(split, day, tick)
    baseline = _render(single, day, tick)
    assert _diff_count(fallback, baseline) == 0, (
        "opting in without the art files on disk must render identically "
        "to the single-plate baseline, not crash or draw blank"
    )


# --- Region-specific probes: each tint touches ONLY its own band -------------
#
# The two plates' own alpha coverage, MEASURED off the actual PNGs
# (radius fraction of each plate's own half-width, which
# `draw_pixmap_centered` scales 1:1 onto the dial radius): the outer
# band (`outter/full.png`) covers ~0.885-1.00, the inner band
# (`inner/simple.png`) ~0.796-0.894. 0.95 lands outer-only, 0.84
# inner-only. DOMY's own six letter seats sit at 0/60/120/180/240/300
# deg (clockwise from top); sampling halfway between them keeps the
# letter art and the (further-out) motto arc off these plate-only
# probes.


def _pixel_at(image, radius_fraction: float, angle_deg: float):
    rad = math.radians(angle_deg)
    x = 200 + 200 * radius_fraction * math.sin(rad)
    y = 200 - 200 * radius_fraction * math.cos(rad)
    return image.pixelColor(round(x), round(y)).getRgb()


_SAMPLE_ANGLES = (30.0, 90.0, 150.0, 210.0, 270.0, 330.0)
_OUTER_ONLY_RADIUS = 0.95
_INNER_ONLY_RADIUS = 0.84


def _split_skin(**overrides):
    ring = dataclasses.replace(defaults.DEFAULT_SKIN.ring, use_split_art=True)
    return dataclasses.replace(
        defaults.DEFAULT_SKIN, ring=ring, show_pointer=False, show_weekday=False,
        show_earth=False, show_moon=False, **overrides,
    )


@pytest.mark.skipif(not _split_art_present(), reason="owner's split art not on disk")
def test_outer_ring_tint_recolors_only_the_outer_band_region(app, frame_args):
    """`ring_tint_inner` is pinned EXPLICITLY on both sides (never left
    None) — None follows `ring_tint`, so varying `ring_tint` alone would
    also move the inner band by design and this probe would not isolate
    the outer band at all."""
    day, tick = frame_args
    plain_img = _render(
        _split_skin(ring_tint="#808080", ring_tint_inner="#808080"), day, tick
    )
    tinted_img = _render(
        _split_skin(ring_tint="#FF0000", ring_tint_inner="#808080"), day, tick
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


@pytest.mark.skipif(not _split_art_present(), reason="owner's split art not on disk")
def test_inner_ring_tint_recolors_only_the_inner_band_region(app, frame_args):
    day, tick = frame_args
    plain_img = _render(_split_skin(ring_tint="#808080"), day, tick)
    tinted_img = _render(
        _split_skin(ring_tint="#808080", ring_tint_inner="#00FF00"), day, tick
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
