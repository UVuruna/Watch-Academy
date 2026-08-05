"""Watch Face Pointer section (R-04/R-05/R-06) regressions — ported from
the now-DELETED `tests/test_design_window.py` (Phase 6 FINAL cleanup):
the SHAPE/CURVATURE/EDGE/NIGHT BORDERS rows moved verbatim from
`design_window.DesignDialog._pointer_tab` into `app.watch_face.pointer`,
and this file is their sole remaining coverage.
"""

import dataclasses
from collections import defaultdict

import pytest
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton, QSlider

from app.settings_store import Settings
from app.watch_face import pointer
from config import constants, palette

_ACTIVE_TOP_COLOR = palette.UI_BUTTON_COLORS["next"][0].lower()


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


class _RecordingSetters(dict):
    """Answers ANY key (building the page never KeyErrors) and remembers
    what each key was actually called with — the SAME shape
    `test_design_window.py`'s stub used."""

    def __init__(self):
        super().__init__()
        self.calls: list[tuple[str, tuple]] = []

    def __missing__(self, key):
        def record(*args):
            self.calls.append((key, args))
        self[key] = record
        return record


def _setters() -> dict:
    return defaultdict(lambda: (lambda *_args: None))


def _page(settings: Settings, setters: dict | None = None):
    return pointer.build(settings, setters if setters is not None else _setters(), lambda s: s)


def _pill_texts(widget) -> set[str]:
    return {b.text() for b in widget.findChildren(QPushButton)}


def _active_pill(widget, text: str) -> QPushButton:
    return next(b for b in widget.findChildren(QPushButton) if b.text() == text)


@pytest.mark.parametrize("point", list(constants.POINTER_POINTS))
def test_shape_and_night_borders_rows_show_for_every_pointer_but_aurora(app, point):
    page = _page(dataclasses.replace(Settings(), pointer=point))
    texts = _pill_texts(page)
    has_night_borders = any(
        box.text() == "Hide night borders"
        for box in page.findChildren(QCheckBox)
    )
    if point == "aurora":
        assert not ({"Star", "Polygon"} & texts)
        assert not has_night_borders
    else:
        assert {"Star", "Polygon"} <= texts
        assert has_night_borders


@pytest.mark.parametrize("point", list(constants.POINTER_POINTS))
@pytest.mark.parametrize("shape", constants.POINTER_SHAPES)
def test_curvature_and_edge_rows_gate_on_true_polygons_in_polygon_shape(
    app, point, shape
):
    """Owner sheet: the curvature slider and its edge switch apply ONLY
    to the four TRUE polygons (trio/cross/hexa/octa) and only while
    "Polygon" is the active shape."""
    page = _page(dataclasses.replace(Settings(), pointer=point, pointer_shape=shape))
    expected = point in constants.POLYGON_POINTERS and shape == "polygon"
    assert bool(page.findChildren(QSlider)) is expected
    assert ({"Smooth concave", "V-notched"} <= _pill_texts(page)) is expected


def test_all_three_new_rows_exist_together_on_a_polygon_pointer(app):
    page = _page(dataclasses.replace(Settings(), pointer="octa", pointer_shape="polygon"))
    texts = _pill_texts(page)
    assert {"Star", "Polygon", "Smooth concave", "V-notched"} <= texts
    assert page.findChildren(QSlider)
    assert any(
        box.text() == "Hide night borders" for box in page.findChildren(QCheckBox)
    )


def test_aurora_carries_none_of_the_four_new_controls(app):
    page = _page(dataclasses.replace(Settings(), pointer="aurora", pointer_shape="polygon"))
    texts = _pill_texts(page)
    assert not ({"Star", "Polygon", "Smooth concave", "V-notched"} & texts)
    assert not page.findChildren(QSlider)
    assert not any(
        box.text() == "Hide night borders" for box in page.findChildren(QCheckBox)
    )


def test_clicking_polygon_calls_the_shape_setter(app):
    setters = _RecordingSetters()
    page = _page(dataclasses.replace(Settings(), pointer="octa"), setters)
    _active_pill(page, "Polygon").click()
    assert ("pointer_shape", ("polygon",)) in setters.calls


def test_moving_the_curvature_slider_calls_the_setter_with_a_fraction(app):
    setters = _RecordingSetters()
    page = _page(
        dataclasses.replace(Settings(), pointer="hexa", pointer_shape="polygon"),
        setters,
    )
    slider = page.findChildren(QSlider)[0]
    slider.setValue(65)
    slider.sliderReleased.emit()
    curvature_calls = [args for key, args in setters.calls if key == "polygon_curvature"]
    assert len(curvature_calls) == 1
    assert curvature_calls[0][0] == pytest.approx(0.65)


def test_clicking_v_notched_calls_the_edge_setter(app):
    setters = _RecordingSetters()
    page = _page(
        dataclasses.replace(Settings(), pointer="hexa", pointer_shape="polygon"),
        setters,
    )
    _active_pill(page, "V-notched").click()
    assert ("polygon_edge", ("notched",)) in setters.calls


def test_toggling_night_borders_calls_its_setter(app):
    setters = _RecordingSetters()
    page = _page(dataclasses.replace(Settings(), pointer="hexa"), setters)
    checkbox = next(
        box for box in page.findChildren(QCheckBox) if box.text() == "Hide night borders"
    )
    checkbox.setChecked(True)
    assert ("hide_night_borders", (True,)) in setters.calls


@pytest.mark.parametrize("point", list(constants.POINTER_POINTS))
@pytest.mark.parametrize("daylight", [True, False])
def test_night_borders_greys_out_when_there_is_no_night(app, point, daylight):
    """OWNER CORRECTION 2026-07-29: with the daylight switch OFF on the
    Calendar or the Rose the dial has no night at all, so "Hide night
    borders" can have no effect — the row is DISABLED there and enabled
    in every other state."""
    if point == "aurora":
        pytest.skip("Aurora carries none of the shape rows")
    page = _page(dataclasses.replace(Settings(), pointer=point, daylight=daylight))
    box = next(
        b for b in page.findChildren(QCheckBox) if b.text() == "Hide night borders"
    )
    no_night = not daylight and point in constants.DAYLIGHT_SWITCH_POINTERS
    assert box.isEnabled() is not no_night


def test_daylight_switch_enabled_only_where_it_applies(app):
    """R-05: unlike the retired Settings dialog copy (always enabled),
    the Watch Face copy grays out on pointers with no daylight switch at
    all."""
    for point in constants.POINTER_POINTS:
        page = _page(dataclasses.replace(Settings(), pointer=point))
        box = next(
            b for b in page.findChildren(QCheckBox)
            if b.text() == "Daylight - Night"
        )
        assert box.isEnabled() is (point in constants.DAYLIGHT_SWITCH_POINTERS)
