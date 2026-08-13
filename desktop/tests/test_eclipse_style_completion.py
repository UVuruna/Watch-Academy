"""THE ECLIPSE STYLE COMPLETION TOOTH (owner ballot 2026-08-13, ballot
item 14 — "say when the chosen style cannot be drawn"). Six new display
styles were accepted the same round and shipped as PLUMBING only, no
painter yet: `totality_path`/`type_emblem`/`dial_shadow` (solar),
`blood_moon`/`danjon_scale`/`contact_marks` (lunar). This module makes
it impossible for the roster to silently lose a deliverable again — the
same failure THE THEME COMPLETION LAW guards for a weekday theme, here
for one eclipse STYLE roster: every name in
`constants.ECLIPSE_SOLAR_STYLES` / `ECLIPSE_LUNAR_STYLES` must carry (a)
a human picker label, (b) a settings round-trip, (c) a rendered
Encyclopedia plate, and (d) either its own painter or an explicit,
reasoned entry in `render.eclipse_style`'s fallback door.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from app.settings_store import Settings, SettingsStore, replace
from app.watch_face.bodies import _ECLIPSE_LUNAR_TITLES, _ECLIPSE_SOLAR_TITLES
from config import constants
from render.eclipse_plates import TYPES, plate_file
from render.eclipse_style import resolve_eclipse_style


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


_ROSTERS = {
    "solar": (constants.ECLIPSE_SOLAR_STYLES, _ECLIPSE_SOLAR_TITLES),
    "lunar": (constants.ECLIPSE_LUNAR_STYLES, _ECLIPSE_LUNAR_TITLES),
}
_SETTINGS_FIELD = {
    "solar": "eclipse_solar_style", "lunar": "eclipse_lunar_style",
}


# -- (a) every name has a human label -------------------------------------

@pytest.mark.parametrize("kind", ["solar", "lunar"])
def test_every_eclipse_style_has_a_human_label(kind):
    styles, titles = _ROSTERS[kind]
    for style in styles:
        assert style in titles, f"{kind}/{style} has no picker label"


# -- (b) every name survives settings round-trip ---------------------------

@pytest.mark.parametrize("kind", ["solar", "lunar"])
def test_every_eclipse_style_survives_settings_round_trip(kind, tmp_path):
    styles, _titles = _ROSTERS[kind]
    field = _SETTINGS_FIELD[kind]
    store = SettingsStore(tmp_path / f"settings_{kind}.json")
    for style in styles:
        store.save(replace(Settings(), **{field: style}))
        loaded = store.load()
        assert getattr(loaded, field) == style, (
            f"{kind}/{style} did not round-trip through the settings store"
        )


# -- (c) every name renders an Encyclopedia plate ---------------------------

@pytest.mark.parametrize("kind", ["solar", "lunar"])
def test_every_eclipse_style_plate_renders(app, kind):
    styles, _titles = _ROSTERS[kind]
    type_ = TYPES[kind][0]
    for style in styles:
        path = plate_file(kind, type_, style)
        assert path.exists(), f"{kind}/{style} plate was never written"


# -- (d) drawn by its own painter, or honestly declared in the door --------

@pytest.mark.parametrize("kind", ["solar", "lunar"])
def test_every_eclipse_style_is_drawn_or_honestly_declared(kind):
    """THE HONESTY RULE: a style either draws itself (fallback reason is
    None and the door hands back the SAME name) or the door names
    exactly what it falls back to and why — never silence, never a
    style that quietly becomes another one with nothing said."""
    styles, _titles = _ROSTERS[kind]
    for style in styles:
        effective, reason = resolve_eclipse_style(
            kind, style, band_available=True,
        )
        if reason is None:
            assert effective == style, (
                f"{kind}/{style} drew silently as {effective!r}"
            )
        else:
            assert effective in styles
            assert reason, f"{kind}/{style} fell back with no stated reason"


def test_dial_shadow_is_never_the_solar_default():
    """Owner's explicit instruction (owner ballot 2026-08-13): the most
    aggressive style is selectable but never ships as the default."""
    assert constants.ECLIPSE_SOLAR_STYLE_DEFAULT != "dial_shadow"


def test_resolve_eclipse_style_rejects_a_garbage_name():
    """A typo or a stale style name is a bug, not a fallback case — the
    door raises rather than quietly picking something."""
    with pytest.raises(ValueError):
        resolve_eclipse_style("solar", "not_a_real_style")
    with pytest.raises(ValueError):
        resolve_eclipse_style("lunar", "not_a_real_style")


def test_band_only_styles_fall_back_to_halo_without_the_band():
    """`horizon_shadow` and `contact_marks` both need
    `moon_band_mode == "horizon"` — without it both resolve to "halo",
    the one disc-side treatment that needs no band, and both say why."""
    for style in ("horizon_shadow", "contact_marks"):
        effective, reason = resolve_eclipse_style(
            "lunar", style, band_available=False,
        )
        assert effective == "halo"
        assert reason and "band" in reason.lower()
