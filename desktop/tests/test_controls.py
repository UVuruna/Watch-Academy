"""THE ELEMENT CLASSES' teeth (owner ballot verdicts 2026-08-14):
OptionCard/CardGroup pin the sealed grammar — reserved border, radio
exclusivity on the GROUP, independent switches, the radio/switch
divider, mandatory blurb, icon clamp and growth, grayed-never-hidden."""

import pytest
from PySide6.QtWidgets import QApplication

from app.watch_face.controls import (
    CardGroup, CardKind, MIN_ICON_PX, OptionCard, divider_present,
    picture_group,
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


def test_on_reset_replaces_the_plain_commit(app):
    """The override rows' Skin-default law: the notch stores None via
    on_reset, and the plain on_change does NOT also fire."""
    committed, resets = [], []
    knob = _knob(
        on_change=committed.append, default_value=36,
        on_reset=lambda: resets.append(None),
    )
    knob.set_value(80)
    knob.reset()
    assert knob.value() == 36
    assert resets == [None]
    assert committed == []


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


# ── THE MIGRATION'S OWN TEETH (the gallery move, 2026-08-14) ──────────
# `picture_group` is the ONE door every picture gallery walks through
# now; these pin what a section may rely on when it hands over entries.


def test_picture_group_checks_the_current_key(app):
    group = picture_group(
        "Group", "Sentence.",
        [("a", "Alpha", "First.", None), ("b", "Beta", "Second.", None)],
        "b", lambda key: None,
    )
    assert group.value() == "b"


def test_picture_group_leaves_nothing_checked_without_a_current(app):
    """A branch whose family is not the active one shows no pick —
    `theme_tree._style_branch` passes None exactly for that case."""
    group = picture_group(
        "Group", "Sentence.", [("a", "Alpha", "First.", None)],
        None, lambda key: None,
    )
    assert group.value() is None


def test_picture_group_reports_the_picked_key(app):
    picked = []
    group = picture_group(
        "Group", "Sentence.",
        [("a", "Alpha", "First.", None), ("b", "Beta", "Second.", None)],
        "a", picked.append,
    )
    group._cards["b"].click()
    assert picked == ["b"]


def test_picture_group_switches_carry_their_own_state(app):
    """The Moon's crossing switches: three independent toggles, each
    pre-lit from its own setting, no radio exclusivity between them."""
    flips = []
    group = picture_group(
        "Group", "Sentence.", [], None, None,
        switches=[
            ("shadow", "Shadow", "Casts.", None, True),
            ("shrink", "Shrink", "Shrinks.", None, False),
        ],
        on_toggle=lambda key, on: flips.append((key, on)),
    )
    assert group.values() == frozenset({"shadow"})
    group._switches["shrink"].click()
    assert flips == [("shrink", True)]
    assert group.values() == frozenset({"shadow", "shrink"})


def test_picture_group_grows_the_divider_only_when_both_kinds_meet(app):
    """The same divider law, reached through the migration door."""
    radios_only = picture_group(
        "Group", "Sentence.", [("a", "Alpha", "First.", None)],
        "a", lambda key: None,
    )
    assert not divider_present(radios_only)
    mixed = picture_group(
        "Group", "Sentence.", [("a", "Alpha", "First.", None)], "a",
        lambda key: None,
        switches=[("s", "Switch", "Toggles.", None, False)],
        on_toggle=lambda key, on: None,
    )
    assert divider_present(mixed)


def test_a_group_with_no_switches_hides_the_switch_host(app):
    """An empty host is not space: it once held the column's spacing and
    was reported by the audit as a zero-height widget over its sibling."""
    group = picture_group(
        "Group", "Sentence.", [("a", "Alpha", "First.", None)],
        "a", lambda key: None,
    )
    assert not group._switch_host.isVisibleTo(group)
    assert group._card_host.isVisibleTo(group)


def test_the_group_states_the_height_its_wrapped_cards_need(app):
    """The clip that started the height work: QGroupBox computes its
    minimum from the flow's ONE-ROW minimum, so a wrapped gallery must
    answer for itself — and never above what the column will be given,
    which is the other half of the same bug."""
    group = picture_group(
        "Group", "Sentence.",
        [(f"k{i}", f"Option {i}", "Blurb.", None) for i in range(9)],
        "k0", lambda key: None,
    )
    group.resize(400, 100)
    narrow = group.heightForWidth(400)
    wide = group.heightForWidth(2000)
    assert narrow > wide, "more rows at a narrower width"
    assert group.minimumSizeHint().height() == group.heightForWidth(400)
