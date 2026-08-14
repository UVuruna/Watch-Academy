"""THE ELEMENT CLASSES' teeth (owner ballot verdicts 2026-08-14):
OptionCard/CardGroup pin the sealed grammar — reserved border, radio
exclusivity on the GROUP, independent switches, the radio/switch
divider, mandatory blurb, icon clamp and growth, grayed-never-hidden."""

import pytest
from PySide6.QtWidgets import QApplication

from app.watch_face.controls import (
    CardGroup, CardKind, MIN_ICON_PX, OptionCard, divider_present,
)
from app.watch_face.widgets import TILE_ICON_PX


@pytest.fixture(scope="module")
def app():
    application = QApplication.instance() or QApplication([])
    yield application


def _group(**kwargs) -> CardGroup:
    group = CardGroup("Test group", "One sentence of description.", **kwargs)
    group.add_card("a", "Alpha", "First option.")
    group.add_card("b", "Beta", "Second option.")
    return group


def test_blurb_is_a_required_argument(app):
    """Owner order: the hover description ALWAYS exists — omitting it
    is a TypeError, never a silent blank."""
    with pytest.raises(TypeError):
        OptionCard("k", "Label")  # no blurb


def test_blurb_becomes_the_tooltip(app):
    card = OptionCard("k", "Label", "What this option does.")
    assert "What this option does." in card.toolTip()


def test_selection_border_never_moves_the_box(app):
    """The reserved-border law: picking colors the border, the widget's
    size hint stays identical."""
    card = OptionCard("k", "Label", "Blurb.")
    before = card.sizeHint()
    card.set_checked(True)
    assert card.sizeHint() == before


def test_radio_pick_is_exclusive_and_fires_once(app):
    picks = []
    group = _group(on_pick=picks.append)
    group.set_value("a")
    group._pick("b")
    assert group.value() == "b"
    assert not group._cards["a"].is_checked()
    assert picks == ["b"]
    # Clicking the checked card keeps it checked and fires nothing.
    group._pick("b")
    assert group.value() == "b"
    assert picks == ["b"]


def test_switches_toggle_independently(app):
    flips = []
    group = CardGroup("Switches", on_toggle=lambda k, on: flips.append((k, on)))
    group.add_switch("x", "X", "Toggle X.")
    group.add_switch("y", "Y", "Toggle Y.")
    group._flip("x")
    assert group.values() == frozenset({"x"})
    group._flip("y")
    assert group.values() == frozenset({"x", "y"})
    group._flip("x")
    assert group.values() == frozenset({"y"})
    assert flips == [("x", True), ("y", True), ("x", False)]


def test_divider_appears_only_when_both_kinds_meet(app):
    group = _group()
    assert not divider_present(group)
    group.add_switch("s", "Switch", "A toggle.")
    assert divider_present(group)


def test_kinds_wear_their_own_border_color(app):
    radio = OptionCard("r", "R", "Radio.", kind=CardKind.RADIO)
    switch = OptionCard("s", "S", "Switch.", kind=CardKind.SWITCH)
    radio.set_checked(True)
    switch.set_checked(True)
    assert radio.styleSheet() != switch.styleSheet()


def test_icon_px_clamps_to_the_sealed_range(app):
    card = OptionCard("k", "Label", "Blurb.")
    card.set_icon_px(10_000)
    assert card.iconSize().width() == TILE_ICON_PX
    card.set_icon_px(1)
    assert card.iconSize().width() == MIN_ICON_PX


def test_icons_grow_when_the_group_widens(app):
    group = _group()
    group.finish()
    group.show()
    QApplication.processEvents()
    group.resize(300, 260)
    QApplication.processEvents()
    narrow = group._cards["a"].iconSize().width()
    group.resize(1600, 260)
    QApplication.processEvents()
    wide = group._cards["a"].iconSize().width()
    assert wide > narrow
    assert wide == TILE_ICON_PX
    group.deleteLater()


def test_disable_with_reason_grays_and_explains(app):
    group = _group()
    group.disable_with_reason("This theme has no such choice.")
    assert not group.isEnabled()
    assert "no such choice" in group.toolTip()


# ═══════════════════════════ the value knobs ═══════════════════════════

from app.watch_face.controls import (  # noqa: E402 — grouped with their tests
    KnobKind, ValueKnob, ValueUnit,
)


def _knob(**kwargs) -> ValueKnob:
    defaults = dict(
        unit=ValueUnit.PERCENT, low=0, high=100, family="opacity",
        kind=KnobKind.K270D, default_value=100,
    )
    defaults.update(kwargs)
    return ValueKnob("k", "Opacity", "How solid it draws.", **defaults)


def test_k270d_requires_a_default_for_its_notch(app):
    with pytest.raises(ValueError):
        _knob(default_value=None)


def test_value_clamps_to_the_arc_ends(app):
    knob = _knob()
    knob.set_value(250)
    assert knob.value() == 100
    knob.set_value(-5)
    assert knob.value() == 0


def test_k360_wraps_instead_of_clamping(app):
    knob = _knob(kind=KnobKind.K360, unit=ValueUnit.PLAIN, low=0, high=360,
                 default_value=None)
    knob.set_value(370)
    assert knob.value() == 10
    knob.set_value(-30)
    assert knob.value() == 330


def test_notch_reset_commits_the_factory_value(app):
    committed = []
    knob = _knob(on_change=committed.append, default_value=36)
    knob.set_value(80)
    knob.reset()
    assert knob.value() == 36
    assert committed == [36]


def test_unit_formatting(app):
    assert _knob().value_text() == "0%"
    factor = _knob(unit=ValueUnit.FACTOR, low=0.5, high=2.0,
                   default_value=1.0, decimals=2)
    factor.set_value(1.24)
    assert factor.value_text() == "1.24"


def test_arc_geometry_maps_bottom_left_to_min_and_bottom_right_to_max(app):
    knob = _knob()
    knob.resize(96, 96)
    # Bottom-left corner direction = travel start; bottom-right = end.
    low = knob._pos_to_value(10, 86)
    high = knob._pos_to_value(86, 86)
    assert low is not None and low < 5
    assert high is not None and high > 95
    # Straight down is the dead wedge — no value there.
    assert knob._pos_to_value(48, 95) is None


def test_family_color_comes_from_the_palette_and_unknown_raises(app):
    from config import palette

    assert _knob().ring_color == palette.KNOB_FAMILY_COLORS["opacity"]
    with pytest.raises(KeyError):
        _knob(family="no-such-family")
