"""WatchFaceDialog (Phase ①+②) regressions — the window frame, the
sidebar-selection persistence across a live-apply rebuild (the SAME
"a fresh container reopens at row 0" fix `design_window.DesignDialog`
carries for its `QTabWidget`), and that the real sections list the same
variants `design_window.py`'s tabs already do (so nothing was dropped in
the split into `app/watch_face/`).
"""

from collections import defaultdict

import pytest
from PySide6.QtWidgets import QApplication, QListWidget, QToolButton

from app.settings_store import Settings
from app.slot_descriptor import SlotDescriptor
from app.watch_face.window import WatchFaceDialog, _SECTIONS
from config import constants, shortcuts
from data.hands import hand_packs
from data.rings import ring_presets


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _noop(*_args, **_kwargs) -> None:
    return None


def fake_descriptors(settings: Settings) -> tuple:
    """A `SlotDescriptor` triple matching `settings`' OWN enablement —
    the same shape `app.controller._slot_descriptors()` builds, stubbed
    with no-op setters (Rule #5's test-side twin: see `_RecordingSetters`
    in test_design_window.py for the analogous stub)."""
    return (
        SlotDescriptor(
            index=1, title="1st Slot", mode_value=settings.weekday_slot,
            style_value=settings.day_slot_style,
            theme_value=settings.weekday_theme,
            roster_value=settings.weekday_roster,
            names_value=settings.show_weekday_names,
            enabled_value=settings.show_weekday,
            set_mode=_noop, set_style_mode=_noop, set_weekday=_noop,
            set_names=_noop,
        ),
        SlotDescriptor(
            index=2, title="2nd Slot", mode_value=settings.octa_slot,
            style_value=settings.info_slot_style,
            theme_value=settings.info_slot_theme,
            roster_value=settings.info_slot_roster,
            names_value=settings.show_info_slot_names,
            enabled_value=settings.show_weekday and settings.show_octa_slot,
            set_mode=_noop, set_style_mode=_noop, set_weekday=_noop,
            set_names=_noop,
        ),
        SlotDescriptor(
            index=3, title="3rd Slot", mode_value=settings.third_slot,
            style_value=settings.third_slot_style,
            theme_value=settings.third_slot_theme,
            roster_value=settings.third_slot_roster,
            names_value=settings.show_info_slot_names,
            enabled_value=(
                settings.show_weekday and settings.show_octa_slot
                and settings.show_third_slot
            ),
            set_mode=_noop, set_style_mode=_noop, set_weekday=_noop,
            set_names=_noop,
        ),
    )


def fake_opacity_defaults() -> dict:
    """The Opacity section's data PROVIDER stub (Watch Face Phase 4,
    Rule #5 — the same shape `slot_descriptors` established): a plain
    dict of skin-default alphas, since a test stub carries no real
    `WatchController._skin` to read."""
    return {
        "star_alpha": 1.0,
        "aura_day_alpha": 0.5,
        "aura_twilight_alpha": 0.3,
        "moon_transit_alpha": 0.5,
        "ghost_alpha": 0.3,
    }


def _setters(settings: Settings | None = None) -> dict:
    """Every key answers a no-op — the real dialog wires live setters
    through the controller (see `_RecordingSetters` in
    test_design_window.py for the analogous stub). `slot_descriptors`
    and `opacity_skin_defaults` are DATA PROVIDERS, not scalar setters
    (Rule #5), so they need a real return value, not a no-op."""
    base = defaultdict(lambda: _noop)
    base["slot_descriptors"] = lambda: fake_descriptors(
        settings if settings is not None else Settings()
    )
    base["opacity_skin_defaults"] = fake_opacity_defaults
    return base


def _dialog(settings: Settings | None = None) -> WatchFaceDialog:
    settings = settings if settings is not None else Settings()
    return WatchFaceDialog(settings, _setters(settings))


# --- R-01: the frame ---------------------------------------------------------


def test_window_builds_with_all_nine_sidebar_entries(app):
    """NUMERALS joined the sidebar with the live numeral bands
    (ring_rework.md §5) — it sits right after Ring, since it settles how
    that same band is written."""
    dialog = _dialog()
    assert dialog._nav_list.count() == 9
    titles = [dialog._nav_list.item(i).text() for i in range(9)]
    assert titles == [
        "Pointer", "Ring", "Numerals", "Hands", "Umbra & Aura", "Opacity",
        "Themes & Slots", "Colors", "Size",
    ]
    assert dialog._stack.count() == 9
    dialog.deleteLater()


def test_no_placeholder_pages_remain(app):
    """Phase ④ (Colors + Opacity) closed the last two placeholders —
    every `_SECTIONS` entry now carries a real builder."""
    assert all(builder is not None for _title, builder in _SECTIONS)


def test_refresh_keeps_the_selected_sidebar_row(app):
    dialog = _dialog()
    assert dialog._nav_list.currentRow() == 0
    dialog._nav_list.setCurrentRow(5)          # the owner browses Colors
    dialog.refresh(Settings(), _setters())
    rebuilt = dialog._nav_list                 # the REBUILT widget, not the corpse
    assert isinstance(rebuilt, QListWidget)
    assert rebuilt.currentRow() == 5
    dialog.deleteLater()


def test_refresh_clamps_a_stale_row_index(app):
    dialog = _dialog()
    dialog._nav_list.setCurrentRow(dialog._nav_list.count() - 1)
    dialog.refresh(Settings(), _setters())
    rebuilt = dialog._nav_list
    assert rebuilt.currentRow() == rebuilt.count() - 1
    dialog.deleteLater()


# --- R-04/R-10/R-14: the real sections list the same variants ---------------


def test_pointer_section_lists_every_pointer_variant(app):
    dialog = _dialog()
    page = dialog._stack.widget(0)              # Pointer is index 0
    tiles = page.findChildren(QToolButton)
    names = {tile.text() for tile in tiles}
    expected = {
        f"{constants.POINTER_DISPLAY_NAMES[variant]} ({count})"
        for variant, count in constants.POINTER_DIAL_COUNTS.items()
    }
    assert expected <= names
    dialog.deleteLater()


def test_ring_section_lists_every_ring_preset(app):
    settings = Settings()
    dialog = _dialog(settings)
    page = dialog._stack.widget(1)               # Ring is index 1
    tiles = page.findChildren(QToolButton)
    names = {tile.text() for tile in tiles}
    expected = set(ring_presets(settings.custom_rings))
    assert expected <= names
    dialog.deleteLater()


def test_ring_section_shows_the_active_presets_about_text(app):
    """ring_rework §5 (owner ruling 2026-08-06, "preset picker: name +
    mini preview + the About"): the picker carries a word-wrapped label
    with the ACTIVE preset's own About — switching the active ring
    (a fresh `refresh`, exactly like the sidebar-selection tests above)
    must show the newly active card's own text, not the old one's."""
    from PySide6.QtWidgets import QLabel

    settings = Settings(ring="CHI")
    dialog = _dialog(settings)
    page = dialog._stack.widget(1)               # Ring is index 1
    labels = [label.text() for label in page.findChildren(QLabel)]
    assert any("Chi" in text and "letter" in text for text in labels)
    dialog.deleteLater()


def test_ring_section_tiles_carry_a_computed_preview_icon(app):
    """Every preset tile's icon comes from `thumbs.ring_preset_thumbnail`
    (COMPUTED from the card's own outer + letters, never a stored or
    generated image) — a non-null icon for every bundled preset."""
    dialog = _dialog(Settings())
    page = dialog._stack.widget(1)
    tiles = {
        tile.text(): tile for tile in page.findChildren(QToolButton)
    }
    for name in ring_presets(Settings().custom_rings):
        assert name in tiles
        assert not tiles[name].icon().isNull(), name
    dialog.deleteLater()


def test_hands_section_lists_every_hand_pack(app):
    dialog = _dialog()
    page = dialog._stack.widget(3)                # Hands is index 3
    tiles = page.findChildren(QToolButton)
    names = {tile.text() for tile in tiles}
    expected = set(hand_packs())
    assert expected <= names
    dialog.deleteLater()


# --- Wiring: the Ctrl+F shortcut exists and is dispatched --------------------


def test_open_watch_face_shortcut_is_registered():
    action_ids = {entry[0] for entry in shortcuts.SHORTCUTS}
    assert "open_watch_face" in action_ids
    assert shortcuts.shortcut_display("open_watch_face") == "Ctrl+F"


def test_open_watch_face_shortcut_never_collides_with_an_existing_combo():
    combos = [
        (key, tuple(sorted(modifiers)))
        for _action_id, key, modifiers, _description in shortcuts.SHORTCUTS
    ]
    assert len(combos) == len(set(combos)), (
        "two SHORTCUTS entries bind the same physical combo"
    )
