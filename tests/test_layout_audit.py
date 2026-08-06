"""THE SPACE & LEGIBILITY LAW — the audit (rules/GUI.md).

Three conditions, checked on a REAL constructed window at its declared
minimum AND larger:

1. **Nothing clipped** — every visible child's geometry lies inside its
   parent's contents rect.
2. **No text elided** — every visible `QLabel` that carries text is at
   least as wide as the text it must show.
3. **No scrollbar over empty space** — a visible scrollbar is legal only
   when the content genuinely exceeds the viewport in that same axis. A
   bar shown while the viewport still has room is the exact defect the
   law names.

Headless (QT_QPA_PLATFORM=offscreen). Offscreen Qt lays widgets out for
real — geometries, size hints and scrollbar ranges are all computed —
so the measurements below are the same ones a visible window would give.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QApplication,
    QLabel,
)

from app.encyclopedia.dialog import EncyclopediaDialog
from config import encyclopedia_ui

#: The sizes every window is audited at: its own minimum, and a larger
#: one — the law binds "at the declared minimum AND larger".
_LARGER = (1400, 900)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _settle(dialog, width: int, height: int) -> None:
    dialog.resize(width, height)
    dialog.show()
    QApplication.processEvents()
    # A second pass: the first one installs the layout, the second lets
    # the scroll areas react to the geometry it produced.
    QApplication.processEvents()


def _is_scrolled_content(widget) -> bool:
    """A scroll area's inner widget is SUPPOSED to exceed its viewport —
    that is what makes it scroll, and the content stays reachable. Such
    a widget is governed by `_scrollbar_over_empty_space` instead. Only
    genuinely unreachable overflow counts as clipping."""
    parent = widget.parentWidget()
    if parent is None:
        return False
    grandparent = parent.parentWidget()
    return isinstance(grandparent, QAbstractScrollArea) and (
        grandparent.viewport() is parent
    )


def _clipped(root) -> list[str]:
    faults = []
    for child in root.findChildren(object):
        if not hasattr(child, "geometry") or not hasattr(child, "isVisible"):
            continue
        if not child.isVisible():
            continue
        parent = child.parentWidget()
        if parent is None or _is_scrolled_content(child):
            continue
        area = parent.contentsRect()
        box = child.geometry()
        if not area.contains(box) and box.width() and box.height():
            faults.append(
                f"{type(child).__name__} {box.getRect()} escapes "
                f"{type(parent).__name__} {area.getRect()}"
            )
    return faults


def _elided(root) -> list[str]:
    faults = []
    for label in root.findChildren(QLabel):
        if not label.isVisible() or not label.text().strip():
            continue
        if label.wordWrap() or label.textFormat().name == "RichText":
            continue                      # wrapping labels grow downward
        needed = label.sizeHint().width()
        if needed > label.width() + 1:
            faults.append(
                f"QLabel {label.text()[:40]!r} needs {needed}px, "
                f"has {label.width()}px"
            )
    return faults


def _scrollbar_over_empty_space(root) -> list[str]:
    faults = []
    for area in root.findChildren(QAbstractScrollArea):
        if not area.isVisible():
            continue
        viewport = area.viewport()
        for bar, extent, axis in (
            (area.verticalScrollBar(), viewport.height(), "vertical"),
            (area.horizontalScrollBar(), viewport.width(), "horizontal"),
        ):
            if not bar.isVisible():
                continue
            # A visible bar whose range is empty means it is showing over
            # content that already fits — unused space with a bar on it.
            if bar.maximum() <= bar.minimum():
                faults.append(
                    f"{type(area).__name__}: {axis} scrollbar visible with "
                    f"no range while the viewport is {extent}px"
                )
    return faults


def _audit(dialog) -> list[str]:
    return _clipped(dialog) + _elided(dialog) + _scrollbar_over_empty_space(dialog)


@pytest.fixture
def encyclopedia(app):
    dialog = EncyclopediaDialog()
    yield dialog
    dialog.close()


def _minimum(dialog) -> tuple[int, int]:
    return dialog.minimumWidth(), dialog.minimumHeight()


def test_the_audit_actually_inspects_something(encyclopedia):
    """A green audit that measured nothing is worse than no audit. Pin
    that the window really does present labels and scroll areas to the
    three checks above."""
    labels, areas, widgets = 0, 0, 0
    # Counted across the SAME screens the audit walks — Home carries no
    # scroll area at all, so measuring only there would leave the
    # scrollbar check untested and silently green.
    for show in (
        encyclopedia.show_home,
        lambda: encyclopedia.navigate_to("instrument", 0),
    ):
        show()
        _settle(encyclopedia, *_minimum(encyclopedia))
        labels += len([
            label for label in encyclopedia.findChildren(QLabel)
            if label.isVisible() and label.text().strip()
        ])
        areas += len([
            area for area in encyclopedia.findChildren(QAbstractScrollArea)
            if area.isVisible()
        ])
        widgets += len([
            child for child in encyclopedia.findChildren(object)
            if hasattr(child, "geometry") and hasattr(child, "isVisible")
            and child.isVisible()
        ])
    assert labels, "no visible text — the elision check would be vacuous"
    assert areas, "no scroll area — the scrollbar check would be vacuous"
    assert widgets > 10, f"only {widgets} widgets laid out"


def test_encyclopedia_holds_at_its_declared_minimum(encyclopedia):
    width, height = _minimum(encyclopedia)
    assert height == encyclopedia_ui.ENCYCLOPEDIA_MIN_HEIGHT_PX
    _settle(encyclopedia, width, height)

    assert _audit(encyclopedia) == []


def test_encyclopedia_holds_larger_than_its_minimum(encyclopedia):
    _settle(encyclopedia, *_LARGER)

    assert _audit(encyclopedia) == []


def test_encyclopedia_holds_on_every_screen_it_opens(encyclopedia):
    """Home, the theme galleries and the reader are three different
    layouts inside one window — the law binds all three, not just
    whichever one happens to be showing."""
    width, height = _minimum(encyclopedia)
    for show in (
        encyclopedia.show_home,
        lambda: encyclopedia.navigate_to("instrument", 0),
    ):
        show()
        for size in ((width, height), _LARGER):
            _settle(encyclopedia, *size)
            faults = _audit(encyclopedia)
            assert faults == [], f"at {size}: {faults}"
