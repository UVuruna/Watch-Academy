"""WORKPLAN Session 28 (SECOND attempt) — the 3D Preview integration.

Pins three things:

1. **THE EXPORTER.** `data.cube_model_export.build_model()` produces a
   dict that validates against the sibling gadget's own schema
   (`shared/model_schema.json`), every register names every seat, the
   centre never carries a fabricated persona, and every one of the
   owner views plus the per-axis/per-pole solo views mounts real
   content.
2. **THE FALLBACK LAW.** `render.cube_preview3d.build_widget()` returns
   `None` for a kind outside this session's amended scope, and for
   EVERY kind when the gadget is unreachable — exactly what the reader
   falls back to its computed 2D plate on.
3. **THE FOUR PAGE FAMILIES.** The Cube, The Thirteen Axes, each of the
   12 human axis pages and the Composure/Vigor poles all resolve to a
   live 3D panel through the REAL Encyclopedia dialog when the gadget
   is present; a page the gadget does not cover (The Sacred Axis, real
   art; the hexagram/banknote pages, out of scope) never grows one.

Tests that need the real gadget SKIP (not fail) when
`render.cube_preview3d.available()` is False — a checkout without the
sibling `Gadgets/3D Preview` folder is a legitimate, documented state
(the fallback IS the point), never a broken one.
"""

import pytest
from PySide6.QtWidgets import QApplication

from app.encyclopedia.dialog import EncyclopediaDialog
from config import cube, paths
from core import cube_seating
from data import cube_model_export
from render import cube_preview3d


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


def _gadget_or_skip():
    if not cube_preview3d.available():
        pytest.skip("3D Preview gadget not present beside this checkout")
    import preview3d
    return preview3d


# --- 1. the exporter -----------------------------------------------------------

def test_exported_model_validates_against_the_gadget_schema():
    gadget = _gadget_or_skip()
    model = cube_model_export.build_model()
    validated = gadget.validate(model)
    assert validated is model
    assert len(model["axes"]) == 13
    assert len(model["cells"]) == 27          # 26 seats + the centre


def test_every_register_names_every_seat():
    """No switcher position can find nothing to say — the schema's own
    requirement, checked directly against DOMY's register set."""
    model = cube_model_export.build_model()
    registers = set(model["registers"])
    assert registers == {"canon", "myth", "historical", "movie"}
    for cell in model["cells"]:
        assert set(cell["names"]) == registers
        for reading in cell["names"].values():
            assert reading["luminous"]
            assert reading["fallen"]
    for axis in model["axes"]:
        for end in axis["ends"]:
            assert set(end["names"]) == registers


def test_the_centre_carries_no_persona_in_any_figure_register():
    """Doctrine (CUBE.md §The Rosters): The One is ruled by nothing, so
    the centre's figure-register readings repeat its own name rather
    than fabricate a persona no canon table names."""
    model = cube_model_export.build_model()
    centre = next(cell for cell in model["cells"] if cell["id"] == "centre")
    for register in ("myth", "historical", "movie"):
        reading = centre["names"][register]
        assert reading["luminous"] == reading["fallen"] == cube.THE_ONE_SEAT


def test_the_sacred_seats_carry_one_persona_each_not_two():
    """Jesus Christ / The Devil name ONE figure per register at their
    own vertex (CUBE.md: no separate "fallen Jesus"), so both readings
    of that seat repeat the one name."""
    model = cube_model_export.build_model()
    sacred_ids = {"+x+y+z", "-x-y-z"}
    sacred = [end for axis in model["axes"] if axis["tier"] == "sacred"
              for end in axis["ends"] if end["direction"] in sacred_ids]
    assert len(sacred) == 2
    for end in sacred:
        for register in ("myth", "historical", "movie"):
            reading = end["names"][register]
            assert reading["luminous"] == reading["fallen"]


def test_every_view_mounts_real_content(app):
    gadget = _gadget_or_skip()
    model = cube_model_export.build_model()
    widget = gadget.Preview3DLightWidget()
    view_names = {view["name"] for view in model["views"]}
    # the four owner models + 13 axis-solo + 26 pole-solo
    assert len(view_names) == 4 + 13 + 26
    for name in view_names:
        widget.show_model(model, name)
        assert widget.list_parts()


# --- 2. the fallback law --------------------------------------------------------

def test_build_widget_refuses_a_kind_outside_this_sessions_scope():
    """The hexagram/banknote/terms/sets pages stay computed 2D no
    matter what — this holds even without the gadget present, since
    the kind check comes before any gadget work."""
    assert cube_preview3d.build_widget("hexagram", "") is None
    assert cube_preview3d.build_widget("banknote", "") is None
    assert cube_preview3d.build_widget("terms", "") is None
    assert cube_preview3d.build_widget("sets", "") is None


def test_build_widget_falls_back_silently_when_the_gadget_is_unreachable(
    app, monkeypatch,
):
    """THE FALLBACK LAW: an unreachable gadget must never raise —
    every kind this bridge would otherwise answer for comes back None."""
    monkeypatch.setattr(paths, "preview3d_gadget_dir", lambda: None)
    monkeypatch.setattr(cube_preview3d, "_gadget", None)
    monkeypatch.setattr(cube_preview3d, "_gadget_load_attempted", False)
    monkeypatch.setattr(cube_preview3d, "_model", None)
    monkeypatch.setattr(cube_preview3d, "_model_build_attempted", False)
    assert cube_preview3d.available() is False
    for kind, key in (("cube", ""), ("axes", ""), ("axis", "Activation"),
                      ("pole", "Composure")):
        assert cube_preview3d.build_widget(kind, key) is None


# --- 3. the four page families, through the real dialog -------------------------

_HUMAN_AXIS_NAMES = frozenset(axis.name for axis in cube_seating.HUMAN_AXES)


def _diagram_pages(reader, key):
    return [
        (index, entry["diagram"])
        for index, entry in enumerate(reader._topics[key]["entries"])
        if entry.get("diagram")
    ]


def test_the_cube_and_thirteen_axes_pages_show_3d(app):
    _gadget_or_skip()
    dialog = EncyclopediaDialog(initial_topic="cube_doctrine", initial_entry=0)
    reader = dialog._reader
    reader.open_topic("cube_doctrine", 0)       # The Cube
    assert len(reader._preview3d_widgets) == 1
    reader.open_topic("cube_doctrine", 1)       # The Thirteen Axes
    assert len(reader._preview3d_widgets) == 1


def test_every_human_axis_page_shows_3d(app):
    _gadget_or_skip()
    dialog = EncyclopediaDialog(initial_topic="cube_axes", initial_entry=0)
    reader = dialog._reader
    seen = set()
    for key in ("cube_axes", "cube_figures"):
        for index, (kind, name) in _diagram_pages(reader, key):
            if kind != "axis":
                continue
            reader.open_topic(key, index)
            assert len(reader._preview3d_widgets) == 1, name
            seen.add(name)
    assert seen == set(_HUMAN_AXIS_NAMES)


def test_composure_and_vigor_show_3d(app):
    _gadget_or_skip()
    dialog = EncyclopediaDialog(initial_topic="cube_axes", initial_entry=0)
    reader = dialog._reader
    poles = [
        (index, name) for index, (kind, name) in _diagram_pages(reader, "cube_axes")
        if kind == "pole"
    ]
    assert {name for _, name in poles} == {"Composure", "Vigor"}
    for index, name in poles:
        reader.open_topic("cube_axes", index)
        assert len(reader._preview3d_widgets) == 1, name


def test_a_page_outside_this_sessions_scope_keeps_its_2d_plate(app):
    """The hexagram/banknote pages are computed but out of the amended
    Session 28 scope, and The Sacred Axis carries real art — none of
    the three may ever grow a 3D widget."""
    _gadget_or_skip()
    dialog = EncyclopediaDialog(initial_topic="cube_projections", initial_entry=0)
    reader = dialog._reader
    reader.open_topic("cube_projections", 0)   # the hexagram
    assert reader._preview3d_widgets == []
    assert len(reader._diagram_labels) == 1
    reader.open_topic("cube_doctrine", 3)      # The Sacred Axis — real art
    assert reader._preview3d_widgets == []
    assert reader._diagram_labels == []
