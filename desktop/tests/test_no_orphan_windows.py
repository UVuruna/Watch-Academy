"""NOTHING THIS PROGRAM BUILDS OR DESTROYS IS EVER A WINDOW NOBODY ASKED FOR.

The owner reported the same defect twice — "FLASH sa otvaranjem nekog
prozora u sredini", 2026-08-15 and again 2026-08-16 — because the first
round fixed one half of it and pinned its own theory instead of the
symptom.

The mechanism is one sentence of Qt: **an orphan QWidget IS a top-level
window.** It can be born one (constructed with no parent and made visible
before it is adopted) or become one (a VISIBLE child handed
`setParent(None)`, which Windows then places at the default screen-centre
spot until `deleteLater` is reached a repaint later). The first round
closed the first door. This file closes the room.

Two teeth, on purpose:

- `test_no_module_spells_its_own_teardown` — STATIC. `app.rebuild` is the
  only place allowed to say `setParent(None)`, so a new window cannot
  reintroduce the bug by writing the old three lines out by hand.
- `test_no_top_level_window_is_shown_during_a_rebuild` — RUNTIME, and
  this is the one that matters. It watches what the OWNER sees: a global
  `Show`/`PlatformSurface` spy over a real `WatchController`, driving
  every knob and every page of the Watch Face window. The previous
  round's tooth asserted that two widgets were CONSTRUCTED with a parent
  — true, and true while the bug was still there, because the widget
  that flashed had already stopped being a child and so was invisible to
  `findChildren`.
"""

import ast
from pathlib import Path
from unittest import mock

import pytest
from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QApplication, QWidget

from app import rebuild

APP_DIR = Path(__file__).resolve().parent.parent / "app"


# --- the static tooth --------------------------------------------------------


def _bare_teardowns(source: str) -> list[int]:
    """Lines calling `<something>.setParent(None)`."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if not isinstance(target, ast.Attribute) or target.attr != "setParent":
            continue
        if len(node.args) != 1:
            continue
        only = node.args[0]
        if isinstance(only, ast.Constant) and only.value is None:
            found.append(node.lineno)
    return found


def test_no_module_spells_its_own_teardown():
    """`app.rebuild.discard` is the ONE door.

    Seven sites used to write the teardown out by hand and every one of
    them omitted the `hide()` that makes the window impossible:
    `watch_face/window.py`, `watch_face/themes.py`,
    `watch_face/theme_tree.py`, `encyclopedia/cards.py` (three, and
    without even a `deleteLater`) and `encyclopedia/reader.py`."""
    offenders = {}
    for module in sorted(APP_DIR.rglob("*.py")):
        if module.name == "rebuild.py":
            continue                      # the door itself
        lines = _bare_teardowns(module.read_text(encoding="utf-8"))
        if lines:
            offenders[module.relative_to(APP_DIR).as_posix()] = lines
    assert offenders == {}, (
        "setParent(None) outside app/rebuild.py — a VISIBLE widget handed "
        "to it becomes a top-level window at the centre of the owner's "
        f"screen. Call rebuild.discard / rebuild.clear_layout instead: {offenders}"
    )


def test_the_door_hides_before_it_unparents():
    """Order is the fix; a refactor that reorders these three calls
    brings the flash back with every test still green."""
    source = (APP_DIR / "rebuild.py").read_text(encoding="utf-8")
    body = ast.parse(source)
    discard = next(
        node for node in body.body
        if isinstance(node, ast.FunctionDef) and node.name == "discard"
    )
    calls = [
        node.func.attr for node in ast.walk(discard)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    ]
    assert calls == ["hide", "setParent", "deleteLater"]


# --- the runtime tooth -------------------------------------------------------


class _WindowSpy(QObject):
    """Every top-level window that is given a native surface or shown."""

    def __init__(self):
        super().__init__()
        self.seen: list[tuple[str, str]] = []

    def eventFilter(self, obj, event):    # noqa: N802 — Qt override
        if (
            event.type() in (QEvent.Type.Show, QEvent.Type.PlatformSurface)
            and isinstance(obj, QWidget)
            and obj.isWindow()
        ):
            self.seen.append((event.type().name, type(obj).__name__))
        return False


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_no_top_level_window_is_shown_during_a_rebuild(app, tmp_path_factory,
                                                       monkeypatch):
    """The owner's own reproduction, in a test.

    He double-clicked a knob, typed an exact value, and a window opened
    and shut in the middle of the screen. The exact-entry dialog is not
    special: OK runs `_commit()` -> the live setter -> `refresh()` ->
    `_build()` -> the teardown. Only four of the twenty-five knobs
    request a full rebuild, which is precisely why the defect looked
    like it "happens only in some places" — so this drives ALL of them,
    and every sidebar page after that."""
    from app.controller import WatchController
    from app.watch_face import controls

    # Never the owner's real profile: this test WRITES settings.
    monkeypatch.setenv("APPDATA", str(tmp_path_factory.mktemp("profile")))

    spy = _WindowSpy()
    controller = WatchController(app)
    try:
        controller._open_watch_face()
        app.processEvents()
        dialog = controller._watch_face
        app.installEventFilter(spy)

        for knob in dialog.findChildren(controls.ValueKnob):
            with mock.patch(
                "PySide6.QtWidgets.QInputDialog.getDouble",
                staticmethod(lambda *args, **_kwargs: (args[3], True)),
            ):
                knob.mouseDoubleClickEvent(None)
            app.processEvents()
            assert not spy.seen, (
                f"a top-level window was shown while committing the "
                f"{knob.title!r} knob: {spy.seen}"
            )

        for row in range(dialog._nav_list.count()):
            dialog._nav_list.setCurrentRow(row)
            app.processEvents()
            assert not spy.seen, (
                f"a top-level window was shown on sidebar row {row}: {spy.seen}"
            )
    finally:
        app.removeEventFilter(spy)
        if controller._watch_face is not None:
            controller._watch_face.close()


def test_discard_hides_a_visible_widget_before_it_is_orphaned(app):
    """The unit-level counter-proof of the same fact: after `discard`
    the widget is not visible, so orphaning it can create no window."""
    parent = QWidget()
    child = QWidget(parent)
    parent.show()
    app.processEvents()
    assert child.isVisible()

    rebuild.discard(child)
    assert not child.isVisible()
    assert child.parent() is None
    parent.close()
