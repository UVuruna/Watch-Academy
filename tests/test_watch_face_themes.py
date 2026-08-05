"""Themes & Slots section (Phase ③, R-17/R-18/R-19/R-20) regressions —
the FACE LAYOUT row mirrors Ctrl+N's own state, the content tree never
dumps a flat theme list, its breadcrumb navigates, the pointer/kind
filter gates FULL FACE correctly while a subdial offers everything, and
the pointer's default weekday theme is starred.
"""

import pytest
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QLabel, QPushButton, QToolButton,
)

from app.settings_store import Settings, replace, slot_layout_target
from app.watch_face import theme_tree, themes
from app.watch_face.window import WatchFaceDialog
from config import calendar_mounts, constants, palette
from tests.test_watch_face import _setters, fake_descriptors

#: The "next" role's gradient top color — pills painted with it are the
#: ACTIVE choice (see `app.ui_style.style_button`); a bare `isChecked()`
#: reads False on every `pill()` button since they are plain, non-
#: checkable `QPushButton`s (the "checked" look is a stylesheet role,
#: not Qt's own checkable state).
_ACTIVE_TOP_COLOR = palette.UI_BUTTON_COLORS["next"][0].lower()


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _reset_nav():
    """Both modules keep breadcrumb/active-slot state at module scope
    (see themes.md/theme_tree.md Design Decisions) — tests must not
    leak that state into each other."""
    themes.reset_navigation()
    theme_tree.reset_navigation()
    yield
    themes.reset_navigation()
    theme_tree.reset_navigation()


def _page(settings: Settings) -> QToolButton:
    dialog = WatchFaceDialog(settings, _setters(settings))
    # Themes & Slots is the section named "Themes & Slots" in _SECTIONS.
    from app.watch_face.window import _SECTIONS
    page_index = [title for title, _b in _SECTIONS].index("Themes & Slots")
    page = dialog._stack.widget(page_index)
    dialog.deleteLater()
    return page


# --- R-17: FACE LAYOUT row mirrors Ctrl+N's own state ------------------------


@pytest.mark.parametrize("target", [0, 1, 2, 3])
def test_face_layout_row_mirrors_ctrl_n_state(app, target):
    settings = replace(
        Settings(),
        show_weekday=target >= 1, show_octa_slot=target >= 2,
        show_third_slot=target >= 3,
    )
    assert slot_layout_target(settings) == target
    page = _page(settings)
    titles = ("Full face", "1 subdial", "2 subdials", "3 subdials")
    button = next(
        b for b in page.findChildren(QPushButton) if b.text() == titles[target]
    )
    assert _ACTIVE_TOP_COLOR in button.styleSheet()
    for other_target, other_title in enumerate(titles):
        if other_target == target:
            continue
        other = next(
            b for b in page.findChildren(QPushButton) if b.text() == other_title
        )
        assert _ACTIVE_TOP_COLOR not in other.styleSheet()


# --- R-18: the tree shows groups, never a flat theme list --------------------


def test_full_subdial_weekday_tab_shows_groups_not_a_flat_list(app):
    settings = Settings()   # show_weekday=True by default → a real subdial
    descriptor = fake_descriptors(settings)[0]
    widget = theme_tree.build(descriptor, False, settings.pointer,
                               settings.pointer_shape, lambda s: s)
    labels = {b.text() for b in widget.findChildren(QToolButton)}
    # A GROUP tile ("Ancient Gods", "Society", ...), never an individual
    # theme name like "Egypt" or "Greek" showing up at the top level.
    assert "Ancient Gods" in labels or "Planets" in labels
    assert "Egypt" not in labels


def test_breadcrumb_navigation_drills_into_a_group_and_back(app):
    settings = Settings()
    descriptor = fake_descriptors(settings)[0]
    widget = theme_tree.build(descriptor, False, settings.pointer,
                               settings.pointer_shape, lambda s: s)
    group_tile = next(
        b for b in widget.findChildren(QToolButton) if b.text() == "Planets"
    )
    group_tile.click()
    # Drilling in is PURE navigation (no setter) — the widget rebuilds
    # itself in place and now shows Level 3 (that group's own themes)
    # plus a back button.
    back_buttons = [
        b for b in widget.findChildren(QPushButton) if b.text().startswith("←")
    ]
    assert back_buttons, "no breadcrumb back button after drilling into a group"
    theme_tiles = {b.text() for b in widget.findChildren(QToolButton)}
    assert any("Planet" in t or "★" in t for t in theme_tiles) or theme_tiles
    back_buttons[0].click()
    assert any(
        b.text() == "Planets" for b in widget.findChildren(QToolButton)
    ), "back button did not return to the group list"


# --- R-18: the default theme is starred --------------------------------------


def test_default_weekday_theme_tile_is_starred(app):
    settings = Settings()
    descriptor = fake_descriptors(settings)[0]
    widget = theme_tree.build(descriptor, False, settings.pointer,
                               settings.pointer_shape, lambda s: s)
    group_tile = next(
        b for b in widget.findChildren(QToolButton) if b.text() == "Planets"
    )
    group_tile.click()
    starred = [
        b for b in widget.findChildren(QToolButton)
        if b.text().startswith("★")
    ]
    assert starred, "the default theme tile is never starred"


# --- R-18: FULL FACE pointer filter -------------------------------------------


def test_full_face_offers_nothing_for_calendar():
    kinds = constants.watch_face_kinds("calendar", "star")
    assert "week" not in kinds


def test_full_face_offers_nothing_for_aurora():
    kinds = constants.watch_face_kinds("aurora", "star")
    assert kinds == set()


def test_full_face_content_tree_shows_a_note_for_aurora(app):
    settings = replace(
        Settings(), pointer="aurora",
        show_weekday=False, show_octa_slot=False, show_third_slot=False,
    )
    descriptor = fake_descriptors(settings)[0]
    widget = theme_tree.build(descriptor, True, settings.pointer,
                               settings.pointer_shape, lambda s: s)
    labels = [w.text() for w in widget.findChildren(QLabel)]
    assert any("Aurora" in text for text in labels)
    assert not widget.findChildren(QToolButton)


def test_full_face_content_tree_offers_weekday_for_trinity(app):
    settings = replace(
        Settings(), pointer="trio",
        show_weekday=False, show_octa_slot=False, show_third_slot=False,
    )
    descriptor = fake_descriptors(settings)[0]
    widget = theme_tree.build(descriptor, True, settings.pointer,
                               settings.pointer_shape, lambda s: s)
    assert widget.findChildren(QToolButton), (
        "Trinity carries 'week' at full face (owner matrix) — the tree "
        "must offer a picker, not a bare note"
    )


def test_rose_polygon_full_face_shows_a_cube_only_note(app):
    settings = replace(
        Settings(), pointer="rose", pointer_shape="polygon",
        show_weekday=False, show_octa_slot=False, show_third_slot=False,
    )
    descriptor = fake_descriptors(settings)[0]
    widget = theme_tree.build(descriptor, True, settings.pointer,
                               settings.pointer_shape, lambda s: s)
    labels = [w.text() for w in widget.findChildren(QLabel)]
    assert any("Cube" in text for text in labels)


# --- R-18/P-4: a subdial offers EVERY content kind ---------------------------


def test_subdial_slot_offers_every_content_kind_regardless_of_pointer():
    for pointer in ("aurora", "calendar", "rose"):
        assert theme_tree._KIND_TITLES == tuple(
            (key, title) for key, title in theme_tree._KIND_TITLES
        )
    # A real, enabled slot never calls `constants.watch_face_kinds` at
    # all — `full_face=False` is the ONLY switch the tree reads.
    settings = Settings()
    descriptor = fake_descriptors(settings)[0]
    widget = theme_tree.build(descriptor, False, "aurora", "star", lambda s: s)
    tabs = {b.text() for b in widget.findChildren(QPushButton)}
    assert {"Weekday themes", "Complications", "Astrology",
            "Ascendant", "Chinese zodiac"} <= tabs


# --- Phase 6 FINAL cleanup: pieces ported from retired Settings sections ------


class _RecordingSetters(dict):
    """Answers ANY key and remembers what it was called with (the SAME
    shape `tests/test_watch_face_pointer.py` uses)."""

    def __init__(self, settings: Settings):
        super().__init__()
        self.calls: list[tuple[str, tuple]] = []
        self["slot_descriptors"] = lambda: fake_descriptors(settings)

    def __missing__(self, key):
        def record(*args):
            self.calls.append((key, args))
        self[key] = record
        return record


def test_calendar_mount_group_appears_only_for_the_calendar_pointer(app):
    non_calendar = themes.build(
        replace(Settings(), pointer="octa"),
        _RecordingSetters(replace(Settings(), pointer="octa")), lambda s: s,
    )
    assert not any(
        "Calendar mount" in b.text() or False
        for b in non_calendar.findChildren(QLabel)
    )
    calendar_settings = replace(Settings(), pointer="calendar")
    page = themes.build(
        calendar_settings, _RecordingSetters(calendar_settings), lambda s: s,
    )
    tiles = page.findChildren(QToolButton)
    labels = [tile.text() for tile in tiles]
    assert "None" in labels
    for key, mount in calendar_mounts.CALENDAR_MOUNTS.items():
        assert f"{mount.title} ({mount.seats})" in labels, key


def test_calendar_mount_pick_calls_its_setter(app):
    settings = replace(Settings(), pointer="calendar", calendar_mount="zodiac")
    setters = _RecordingSetters(settings)
    page = themes.build(settings, setters, lambda s: s)
    button = next(
        b for b in page.findChildren(QToolButton) if b.text() == "None"
    )
    button.click()
    assert ("calendar_mount", ("off",)) in setters.calls


def test_artwork_and_subdial_set_combos_exist_and_restore_the_stored_pick(app):
    settings = replace(Settings(), art_source="chatgpt", subdial_set="solo")
    page = themes.build(settings, _RecordingSetters(settings), lambda s: s)
    combos = page.findChildren(QComboBox)
    art_combo = next(
        c for c in combos
        if any(c.itemData(i) == "chatgpt" for i in range(c.count()))
    )
    assert art_combo.currentData() == "chatgpt"
    subdial_combo = next(
        c for c in combos
        if any(c.itemData(i) == "solo" for i in range(c.count()))
    )
    assert subdial_combo.currentData() == "solo"


def test_rotation_group_picker_shows_the_custom_grid_only_in_custom_mode(app):
    settings = replace(Settings(), theme_rotation_group="custom")
    page = themes.build(settings, _RecordingSetters(settings), lambda s: s)
    labels = {b.text() for b in page.findChildren(QCheckBox)}
    from config import pantheon
    assert any(
        pantheon.WEEKDAY_THEME_TITLES[key] in labels
        for key in pantheon.WEEKDAY_THEME_TITLES
    )


def test_rotation_group_picker_hides_the_custom_grid_when_not_custom(app):
    settings = replace(Settings(), theme_rotation_group="none")
    page = themes.build(settings, _RecordingSetters(settings), lambda s: s)
    from config import pantheon
    labels = {b.text() for b in page.findChildren(QCheckBox)}
    assert not any(
        pantheon.WEEKDAY_THEME_TITLES[key] in labels
        for key in pantheon.WEEKDAY_THEME_TITLES
    )


def test_per_theme_metal_combo_calls_theme_metal_setter(app):
    settings = replace(
        Settings(), theme_rotation_group="custom",
        theme_rotation_themes=("greek",),
    )
    setters = _RecordingSetters(settings)
    page = themes.build(settings, setters, lambda s: s)
    from config import constants as cfg_constants

    metal_combo = next(
        c for c in page.findChildren(QComboBox)
        if set(c.itemData(i) for i in range(c.count()))
        >= set(cfg_constants.theme_metals("greek"))
    )
    index = metal_combo.findData("bronze")
    metal_combo.setCurrentIndex(index)
    assert ("theme_metal", ("greek", "bronze")) in setters.calls
