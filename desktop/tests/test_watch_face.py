"""WatchFaceDialog (Phase ①+②) regressions — the window frame, the
sidebar-selection persistence across a live-apply rebuild (the SAME
"a fresh container reopens at row 0" fix `design_window.DesignDialog`
carries for its `QTabWidget`), and that the real sections list the same
variants `design_window.py`'s tabs already do (so nothing was dropped in
the split into `app/watch_face/`).
"""

from collections import defaultdict

import pytest
from PySide6.QtCore import Qt
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
        "Pointer", "Ring", "Numerals", "Hands & Bodies", "Umbra & Aura",
        "Opacity", "Themes & Slots", "Colors", "Size",
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


def test_refresh_keeps_the_scroll_offset_of_every_page(app):
    """THE NO-MOVEMENT DECREE (owner 2026-08-10, third report): a pick
    changes the WATCH and nothing else. The live-apply rebuild used to
    drop every page back to its top, so a pick made halfway down a long
    section threw the owner's place away."""
    dialog = _dialog()
    dialog.show()                              # ranges are 0 until laid out
    app.processEvents()
    dialog._nav_list.setCurrentRow(6)          # Themes & Slots — a long page
    page_scroll = dialog._stack.currentWidget()
    bar = page_scroll.verticalScrollBar()
    app.processEvents()
    if bar.maximum() == 0:                     # a screen too tall to scroll
        dialog.deleteLater()
        pytest.skip("the section fits without scrolling on this screen")
    bar.setValue(bar.maximum() // 2)
    parked = bar.value()
    dialog.refresh(Settings(), _setters())
    app.processEvents()                        # the queued second restore
    assert dialog._stack.currentWidget().verticalScrollBar().value() == parked
    dialog.deleteLater()


def test_refresh_never_hands_focus_to_the_sidebar(app):
    """"Odvede me na levu stranu" — a rebuilt `QListWidget` with the
    default StrongFocus grabbed the caret away from the control the
    owner had just clicked."""
    dialog = _dialog()
    dialog.refresh(Settings(), _setters())
    assert dialog._nav_list.focusPolicy() == Qt.FocusPolicy.TabFocus
    assert not dialog._nav_list.hasFocus()
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


# --- THE HOLDER WEARS THE SAME COLLAR (regression, 2026-08-13) ---------------
#
# The scroll holder measured its content at ITS OWN width while the page
# inside it was capped narrower by the one-readable-column rule. Four
# pixels of difference fit one more tile per gallery row, so the height
# the holder published was a full row short — and the Ring page's
# "Inner (minute track)" group was handed 375px against its own 388px
# minimum, losing its bottom margin. The runtime audit caught it only
# under the owner's live profile; this tooth catches it anywhere.


def test_every_scroll_holder_is_capped_to_the_same_column_as_its_page(app):
    dialog = _dialog()
    dialog.show()
    QApplication.processEvents()
    for index in range(dialog._stack.count()):
        holder = dialog._stack.widget(index).widget()
        page = holder.layout().itemAt(0).widget()
        assert holder.maximumWidth() == page.maximumWidth(), (
            f"page {index}: the holder measures its content at its own "
            f"width ({holder.maximumWidth()}) while the page is drawn at "
            f"{page.maximumWidth()} — a gallery row can wrap differently "
            "between the two, and the published height comes up short"
        )
    dialog.deleteLater()


# --- THE HOLDER WEARS THE SAME COLLAR (nav pill row, regression 2026-08-13) --
#
# The selected-item pill is painted from `QListWidget::item` QSS
# padding/margin in `app/theme.py`, but the sidebar reserved a narrower
# row for each entry than that padding actually painted — the selected
# pill overlapped the row above and below, clipping their text ("Ring" /
# "Hands & Bodies" sliced around a selected "Numerals", owner-reported).
# `window.py` now stamps every nav item's `sizeHint` from the SAME
# padding/margin constants the QSS pill uses, so the reserved row and
# the painted pill can never drift apart again.


def test_nav_sidebar_selection_never_overlaps_a_neighbour_row(app):
    from app.theme import apply_theme

    apply_theme(app)  # the pill IS the QSS in app/theme.py — apply it
    dialog = _dialog()
    dialog.resize(dialog.minimumSize())
    nav = dialog._nav_list
    QApplication.processEvents()
    for selected in range(nav.count()):
        nav.setCurrentRow(selected)
        QApplication.processEvents()
        rects = [nav.visualItemRect(nav.item(i)) for i in range(nav.count())]
        for i in range(1, len(rects)):
            assert rects[i].top() >= rects[i - 1].bottom(), (
                f"with '{nav.item(selected).text()}' selected, row {i} "
                f"('{nav.item(i).text()}') overlaps row {i - 1} "
                f"('{nav.item(i - 1).text()}') — the selected pill is "
                "clipping a neighbour's text"
            )
    dialog.deleteLater()
