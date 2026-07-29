"""DesignDialog regressions — the live-apply picker window.

THE TAB BOUNCE (owner fix 2026-07-26): every pick routes through the
controller's `refresh()`, which rebuilds the whole QTabWidget — and a
fresh QTabWidget always opens at index 0, so changing a value on any
tab other than Pointer bounced the window back to the first tab.
`_build` now carries the open tab across rebuilds.
"""

import dataclasses
from collections import defaultdict

import pytest
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QPushButton, QSlider, QTabWidget,
)

from app.design_window import DesignDialog
from app.settings_store import Settings
from config import constants


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _setters() -> dict:
    """A stub for the controller's setter table — every key answers a
    no-op (the real dialog wires live setters; since the DOMY default
    ring grew its own Two-metals checkbox in the ENLARGE/THEMATIC
    round, an empty dict would KeyError at build)."""
    return defaultdict(lambda: (lambda *_args: None))


class _RecordingSetters(dict):
    """Like `_setters()` above (answers ANY key so building the other
    six tabs never KeyErrors) but remembers what each key was actually
    called with — the Pointers REWORK phase 3 widget tests assert on
    `.calls` to pin which control talks to which setter, with which
    value."""

    def __init__(self):
        super().__init__()
        self.calls: list[tuple[str, tuple]] = []

    def __missing__(self, key):
        def record(*args):
            self.calls.append((key, args))
        self[key] = record
        return record


def _dialog(settings: Settings | None = None) -> DesignDialog:
    return DesignDialog(
        settings if settings is not None else Settings(), _setters()
    )


def _pointer_tab_widget(settings: Settings, setters: dict | None = None):
    """The built Pointer tab (always index 0 — `_build` adds it first)
    plus its owning dialog; the caller must keep the dialog alive (Qt
    parents the tab's widgets to it) and `deleteLater()` it when done,
    matching every other test in this module."""
    dialog = DesignDialog(
        settings, setters if setters is not None else _setters()
    )
    return dialog, dialog._tabs.widget(0)


def _pill_texts(widget) -> set[str]:
    return {button.text() for button in widget.findChildren(QPushButton)}


def test_refresh_keeps_the_open_tab(app):
    dialog = _dialog()
    assert dialog._tabs.currentIndex() == 0  # first build opens on Pointer
    dialog._tabs.setCurrentIndex(4)          # the owner browses Hands
    dialog.refresh(Settings(), _setters())
    rebuilt = dialog._tabs                   # the REBUILT widget, not the corpse
    assert isinstance(rebuilt, QTabWidget)
    assert rebuilt.currentIndex() == 4       # the pick no longer bounces
    dialog.deleteLater()


def test_refresh_clamps_a_stale_tab_index(app):
    """Defensive only against OUR OWN rebuild arithmetic: a remembered
    index beyond the rebuilt count clamps to the last tab instead of
    Qt silently ignoring the set."""
    dialog = _dialog()
    dialog._tabs.setCurrentIndex(dialog._tabs.count() - 1)
    dialog.refresh(Settings(), _setters())
    rebuilt = dialog._tabs
    assert rebuilt.currentIndex() == rebuilt.count() - 1
    dialog.deleteLater()


# --- Pointers REWORK phase 3: the Pointer tab's new rows (owner sheet
# UV/Pointers.png, 2026-07-29) — shape, curvature/edge, night borders ----------------


@pytest.mark.parametrize("pointer", list(constants.POINTER_POINTS))
def test_shape_and_night_borders_rows_show_for_every_pointer_but_aurora(
    app, pointer
):
    """The SHAPE switch and the Hide-night-borders toggle are global —
    every pointer gets them EXCEPT the armless Aurora, which draws no
    pointer at all and ignores both choices outright."""
    dialog, tab = _pointer_tab_widget(
        dataclasses.replace(Settings(), pointer=pointer)
    )
    texts = _pill_texts(tab)
    has_night_borders = any(
        box.text() == "Hide night borders"
        for box in tab.findChildren(QCheckBox)
    )
    if pointer == "aurora":
        assert not ({"Star", "Polygon"} & texts)
        assert not has_night_borders
    else:
        assert {"Star", "Polygon"} <= texts
        assert has_night_borders
    dialog.deleteLater()


@pytest.mark.parametrize("pointer", list(constants.POINTER_POINTS))
@pytest.mark.parametrize("shape", constants.POINTER_SHAPES)
def test_curvature_and_edge_rows_gate_on_true_polygons_in_polygon_shape(
    app, pointer, shape
):
    """Owner sheet: the curvature slider and its edge switch apply ONLY
    to the four TRUE polygons (trio/cross/hexa/octa) and only while
    "Polygon" is the active shape — the Calendar's and the Rose's own
    "polygon" reading are touching-arm STARS that never curve, and the
    star shape has no edge to pull in the first place."""
    dialog, tab = _pointer_tab_widget(
        dataclasses.replace(Settings(), pointer=pointer, pointer_shape=shape)
    )
    expected = pointer in constants.POLYGON_POINTERS and shape == "polygon"
    assert bool(tab.findChildren(QSlider)) is expected
    assert ({"Smooth concave", "V-notched"} <= _pill_texts(tab)) is expected
    dialog.deleteLater()


def test_all_three_new_rows_exist_together_on_a_polygon_pointer(app):
    dialog, tab = _pointer_tab_widget(
        dataclasses.replace(Settings(), pointer="octa", pointer_shape="polygon")
    )
    texts = _pill_texts(tab)
    assert {"Star", "Polygon", "Smooth concave", "V-notched"} <= texts
    assert tab.findChildren(QSlider)
    assert any(
        box.text() == "Hide night borders"
        for box in tab.findChildren(QCheckBox)
    )
    dialog.deleteLater()


def test_aurora_carries_none_of_the_four_new_controls(app):
    dialog, tab = _pointer_tab_widget(
        dataclasses.replace(Settings(), pointer="aurora", pointer_shape="polygon")
    )
    texts = _pill_texts(tab)
    assert not ({"Star", "Polygon", "Smooth concave", "V-notched"} & texts)
    assert not tab.findChildren(QSlider)
    assert not any(
        box.text() == "Hide night borders"
        for box in tab.findChildren(QCheckBox)
    )
    dialog.deleteLater()


def test_clicking_polygon_calls_the_shape_setter(app):
    setters = _RecordingSetters()
    dialog, tab = _pointer_tab_widget(
        dataclasses.replace(Settings(), pointer="octa"), setters
    )
    button = next(
        b for b in tab.findChildren(QPushButton) if b.text() == "Polygon"
    )
    button.click()
    assert ("pointer_shape", ("polygon",)) in setters.calls
    dialog.deleteLater()


def test_moving_the_curvature_slider_calls_the_setter_with_a_fraction(app):
    setters = _RecordingSetters()
    dialog, tab = _pointer_tab_widget(
        dataclasses.replace(Settings(), pointer="hexa", pointer_shape="polygon"),
        setters,
    )
    slider = tab.findChildren(QSlider)[0]
    slider.setValue(65)
    slider.sliderReleased.emit()
    curvature_calls = [
        args for key, args in setters.calls if key == "polygon_curvature"
    ]
    assert len(curvature_calls) == 1
    assert curvature_calls[0][0] == pytest.approx(0.65)
    dialog.deleteLater()


def test_clicking_v_notched_calls_the_edge_setter(app):
    setters = _RecordingSetters()
    dialog, tab = _pointer_tab_widget(
        dataclasses.replace(Settings(), pointer="hexa", pointer_shape="polygon"),
        setters,
    )
    button = next(
        b for b in tab.findChildren(QPushButton) if b.text() == "V-notched"
    )
    button.click()
    assert ("polygon_edge", ("notched",)) in setters.calls
    dialog.deleteLater()


def test_toggling_night_borders_calls_its_setter(app):
    setters = _RecordingSetters()
    dialog, tab = _pointer_tab_widget(
        dataclasses.replace(Settings(), pointer="hexa"), setters
    )
    checkbox = next(
        box for box in tab.findChildren(QCheckBox)
        if box.text() == "Hide night borders"
    )
    checkbox.setChecked(True)
    assert ("hide_night_borders", (True,)) in setters.calls
    dialog.deleteLater()
