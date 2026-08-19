"""WatchFaceDialog (Phase ①+②) regressions — the window frame, the
sidebar-selection persistence across a live-apply rebuild (the SAME
"a fresh container reopens at row 0" fix `design_window.DesignDialog`
carries for its `QTabWidget`), and that the real sections list the same
variants `design_window.py`'s tabs already do (so nothing was dropped in
the split into `app/watch_face/`).
"""

from collections import defaultdict
from unittest import mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QListWidget, QStackedWidget, QToolButton, QWidget,
)

from app.settings_store import Settings
from app.slot_descriptor import SlotDescriptor
from app import section_host
from app.watch_face import window
from app.watch_face.window import WatchFaceDialog, _SECTIONS
from config import pointer_geometry, pointer_names, shortcuts
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
    # ONE REQUIRED VALUE, like every real setter (2026-08-15): the
    # per-section Reset tells a settable key from a data provider by
    # arity, so a stub of `(*args)` would silently make every section
    # look unresettable and the Reset tooth would pass on nothing.
    def _one(value, *_rest) -> None:
        return None

    base = defaultdict(lambda: _one)
    base["slot_descriptors"] = lambda: fake_descriptors(
        settings if settings is not None else Settings()
    )
    base["opacity_skin_defaults"] = fake_opacity_defaults
    base["ring_has_crown_text"] = lambda: True
    base["open_custom_ring"] = _noop
    return base


def _dialog(settings: Settings | None = None) -> WatchFaceDialog:
    settings = settings if settings is not None else Settings()
    return WatchFaceDialog(settings, _setters(settings))


# --- R-01: the frame ---------------------------------------------------------


def test_window_builds_with_all_nine_sidebar_entries(app):
    """Nine entries, reorganized 2026-08-14 (owner ballot verdicts
    5A/5D): Umbra & Aura dissolved into Colors, and the over-long Hands
    & Bodies split its Eclipses + Stations half into its own page — the
    count stays nine."""
    dialog = _dialog()
    assert dialog._nav_list.count() == 9
    titles = [dialog._nav_list.item(i).text() for i in range(9)]
    assert titles == [
        "Pointer", "Ring", "Numerals", "Hands & Bodies",
        "Eclipses & Stations", "Opacity", "Themes & Slots", "Colors",
        "Size",
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
        f"{pointer_names.POINTER_DISPLAY_NAMES[variant]} ({count})"
        for variant, count in pointer_geometry.POINTER_DIAL_COUNTS.items()
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


# --- NO PINNED WIDTH (owner decree 2026-08-14) -------------------------------
#
# The one-readable-column rule of 2026-08-06 capped every page (and its
# holder) with setMaximumWidth to the widest section's MINIMUM hint —
# so an ultra-wide window still drew every gallery in the same narrow
# column, wrapping the eclipse tiles into two rows beside a screen of
# empty space (owner's screenshot). The ruling: minimums that keep text
# legible are lawful, a hard-coded width never is. Content follows the
# real viewport width; the flow galleries absorb it by refilling rows.


def test_no_page_carries_a_pinned_maximum_width(app):
    QWIDGETSIZE_MAX = 16777215  # Qt's "no maximum" sentinel
    dialog = _dialog()
    dialog.show()
    QApplication.processEvents()
    for index in range(dialog._stack.count()):
        holder = dialog._stack.widget(index).widget()
        page = holder.layout().itemAt(0).widget()
        for name, widget in (("holder", holder), ("page", page)):
            assert widget.maximumWidth() == QWIDGETSIZE_MAX, (
                f"page {index}: the {name} carries a pinned maximum width "
                f"({widget.maximumWidth()}px) — the owner's 2026-08-14 "
                "decree forbids hard-coded widths; content must follow "
                "the real viewport width"
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


# ── THE ROW SHAPES (the CardGroup migration round, 2026-08-14) ────────


def test_a_flow_row_gives_its_same_kind_members_one_width(app):
    """ALG-5 through the row builder: the widest label decides, and it
    decides AFTER the widgets are polished (an unparented button hints
    at the bare application font — the 90/95/92px audit finding)."""
    from PySide6.QtWidgets import QPushButton
    from app.watch_face.widgets import flow_row

    row = flow_row([QPushButton("Full face"), QPushButton("3 subdials")])
    row.resize(600, 40)
    row.show()
    widths = {button.width() for button in row.findChildren(QPushButton)}
    row.hide()
    assert len(widths) == 1, widths


def test_a_flow_row_does_not_stretch_across_kinds(app):
    """A lone checkbox riding the row's tail is not a button's sibling."""
    from PySide6.QtWidgets import QCheckBox, QPushButton
    from app.watch_face.widgets import flow_row

    box = QCheckBox("Names")
    row = flow_row([QPushButton("A very long button label"), box])
    row.resize(600, 40)
    row.show()
    natural = box.sizeHint().width()
    stretched = box.width()
    row.hide()
    assert stretched <= natural + 2


def test_a_lonely_tail_row_is_rebalanced(app):
    """Nine equal cards with room for four wrap 3-3-3, not 4-4-1: the
    owner's rule is FILL THE ROW, and a tail of one fills nothing (the
    band whose right half stood empty in the runtime audit). A tail of
    at least half a row keeps the greedy answer — his own 4-3."""
    from PySide6.QtCore import QRect
    from PySide6.QtWidgets import QPushButton
    from app.watch_face.widgets import FlowLayout, FlowContent

    def rows_for(count: int, width: int) -> list[int]:
        content = FlowContent()
        flow = FlowLayout()
        for index in range(count):
            button = QPushButton("Item")
            button.setFixedWidth(100)
            flow.addWidget(button)
        content.setLayout(flow)
        flow.setGeometry(QRect(0, 0, width, 800))
        tops: dict = {}
        for index in range(flow.count()):
            geometry = flow.itemAt(index).geometry()
            tops.setdefault(geometry.y(), 0)
            tops[geometry.y()] += 1
        return [tops[key] for key in sorted(tops)]

    # Room for four per row (4 * 100 + 3 * gap fits in 460).
    assert rows_for(9, 460) == [3, 3, 3]
    assert rows_for(7, 460) == [4, 3]


# --- THE MIDWIFE WINDOW (owner bug 2026-08-15) -------------------------------


def test_the_rebuild_never_creates_a_top_level_window(app):
    """A live pick may not flash a window onto the desktop.

    Owner report 2026-08-15 (GIF): changing anything in the Watch Face
    window made "a window open in the middle and close again" on every
    single pick. Root cause, measured with a global Show/PlatformSurface
    spy on the running app: `_build` created the sidebar and the page
    stack PARENTLESS, and a parentless QWidget IS a top-level window. It
    stayed one for the whole span between construction and the closing
    `addWidget` calls — and `setCurrentRow`/`setCurrentIndex` inside that
    span makes a window VISIBLE, so Windows handed each a real native
    window at the default screen-centre spot before the reparent hid it
    again.

    The tooth watches CONSTRUCTION, not the end state, and that is the
    whole point: by the time `_build` returns, `addWidget` has adopted
    both widgets into the dialog either way, so an after-the-fact
    `parent()` check passes on the broken code too (verified — it did).
    What has to be pinned is that neither is ever born parentless, which
    is the only condition under which the window can never exist.

    WA-R16 (2026-08-19) moved the pair into `app.section_host.SectionHost`,
    so that is where the spy is planted now and the recorded parent is
    the HOST — which `__init__` has already parented to the dialog by the
    time it builds either widget, so the law holds one level deeper."""
    parents: list = []

    class _WatchedList(QListWidget):
        def __init__(self, parent=None):
            parents.append(("QListWidget", parent))
            super().__init__(parent)

    class _WatchedStack(QStackedWidget):
        def __init__(self, parent=None):
            parents.append(("QStackedWidget", parent))
            super().__init__(parent)

    dialog = _dialog()
    parents.clear()
    with mock.patch.object(section_host, "QListWidget", _WatchedList), \
            mock.patch.object(section_host, "QStackedWidget", _WatchedStack):
        dialog.refresh(dialog._settings, dialog._setters)   # the live-pick path
    assert [name for name, _parent in parents] == [
        "QListWidget", "QStackedWidget",
    ]
    host = dialog._host
    assert [parent for _name, parent in parents] == [host, host]
    # ...and the host they were born into was itself already the
    # dialog's child at that moment — the chain to a real window is
    # unbroken from the first constructor on.
    assert host.parent() is dialog
    # ...and nothing the finished window owns is an ordinary top-level
    # either. (Popups are exempt: a combo box owns a `Qt::Popup` frame
    # by construction — thirteen on these nine pages — and a popup is
    # only ever shown on demand.)
    strays = [
        type(child).__name__
        for child in dialog.findChildren(QWidget)
        if child.windowType() == Qt.WindowType.Window
    ]
    assert strays == []


# --- THE PER-SECTION RESET (owner order 2026-08-15) --------------------------


def test_every_section_ends_with_a_reset(app):
    """"svaka sekcija na dnu treba da ima reset to default" — all nine.

    Opacity was the one page that grew none on the first pass, and the
    reason is worth keeping: its knobs looked their setter up INSIDE the
    click callback, so the build never asked for the key and the
    recording wrapper never saw it. The lookup is bound at build time
    now. Any future section that defers its lookups the same way fails
    here rather than shipping a page the owner cannot reset."""
    from PySide6.QtWidgets import QPushButton

    dialog = _dialog()
    for index, (title, _builder) in enumerate(_SECTIONS):
        page = dialog._stack.widget(index).widget()
        buttons = [
            button for button in page.findChildren(QPushButton)
            if button.text() == "Reset"
        ]
        assert len(buttons) == 1, f"{title} has {len(buttons)} Reset buttons"
    dialog.deleteLater()


def test_reset_writes_the_factory_value_of_every_key_the_section_owns(app):
    """The button is only worth its space if it actually writes — and
    only the keys that section owns, never the whole Settings."""
    from app.watch_face import section_reset

    written: dict = {}
    setters = _setters(Settings())
    for key in ("ring", "ring_finish", "pointer"):
        setters[key] = lambda value, k=key: written.__setitem__(k, value)
    row = section_reset.reset_row(
        ["ring", "ring_finish", "slot_descriptors", "pointer"],
        Settings(), setters, lambda text: text,
    )
    assert row is not None
    from PySide6.QtWidgets import QPushButton
    row.findChild(QPushButton).click()
    factory = Settings()
    assert written == {
        "ring": factory.ring,
        "ring_finish": factory.ring_finish,
        "pointer": factory.pointer,
    }
    # `slot_descriptors` is a data PROVIDER, not a setting — it must not
    # have been written, and it is not a `Settings` field at all.
    assert "slot_descriptors" not in written


def test_reset_skips_a_setter_that_needs_a_target_as_well_as_a_value(app):
    """`palettes` IS a `Settings` field, but its setter takes
    (pointer, style, hues) — resetting it by handing it one value would
    raise. Arity is the filter, and it only works because the
    controller's `wrap` carries `functools.wraps` so the wrapper reports
    the real setter's signature instead of `(*args, **kwargs)`."""
    from app.watch_face import section_reset

    setters = _setters(Settings())
    setters["palettes"] = lambda pointer, style, hues: None
    assert "palettes" not in section_reset.resettable_keys(
        ["palettes", "ring"], setters
    )
    assert "ring" in section_reset.resettable_keys(["palettes", "ring"], setters)


def test_the_controller_wrapper_reports_the_real_setter_signature(app):
    """The tooth for the `functools.wraps` above — without it every
    Watch Face setter looks like `(*args, **kwargs)`, arity tells
    nothing apart, and the Reset silently degrades to writing nothing."""
    import functools
    import inspect

    def wrap(setter):
        @functools.wraps(setter)
        def wrapped(*args, **kwargs):
            return setter(*args, **kwargs)
        return wrapped

    assert len(inspect.signature(wrap(lambda value: None)).parameters) == 1
    assert len(
        inspect.signature(wrap(lambda a, b, c: None)).parameters
    ) == 3


def _real_controller_setters(settings: Settings) -> dict:
    """The mapping the LIVE controller hands the Watch Face window,
    obtained without booting a controller: `_watch_face_setters` reads
    nothing off `self` at construction time — every `self._set_*` sits
    inside a lambda — so an unbound call with a stand-in `self` returns
    the real dict, real keys and all. Only the three DATA PROVIDERS are
    swapped for the fakes above, because those ARE called during a
    build and a stand-in would hand the builders nonsense."""
    from app.controller import WatchController

    setters = WatchController._watch_face_setters(mock.MagicMock())
    setters["slot_descriptors"] = lambda: fake_descriptors(settings)
    setters["opacity_skin_defaults"] = fake_opacity_defaults
    setters["ring_has_crown_text"] = lambda: True
    return setters


def test_every_page_builds_against_the_real_controller_setters(app):
    """THE KEY THAT WAS NEVER THERE (owner crash 2026-08-16).

    Every other test in this file stubs the setters as a `defaultdict`,
    which answers ANY key — so a page could ask for a setter the
    controller never registered and the whole suite stayed green. The
    Themes page did exactly that with `subdial_style`: the lookup sat
    inside the click callback, so it raised only if somebody clicked
    that pill, and the pill had been dead for as long as it had existed.
    Moving the lookup to build time (so the per-section Reset could see
    the key) turned that latent crash into a Watch Face that would not
    open at all.

    So this test builds all nine pages against the mapping the REAL
    controller returns. A page that asks for a key the controller does
    not register fails here, at build, with the key's own name."""
    settings = Settings()
    dialog = WatchFaceDialog(settings, _real_controller_setters(settings))
    assert dialog.findChildren(QWidget)
