"""DesignDialog regressions — the live-apply picker window.

THE TAB BOUNCE (owner fix 2026-07-26): every pick routes through the
controller's `refresh()`, which rebuilds the whole QTabWidget — and a
fresh QTabWidget always opens at index 0, so changing a value on any
tab other than Pointer bounced the window back to the first tab.
`_build` now carries the open tab across rebuilds.
"""

from collections import defaultdict

import pytest
from PySide6.QtWidgets import QApplication, QTabWidget

from app.design_window import DesignDialog
from app.settings_store import Settings


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _setters() -> dict:
    """A stub for the controller's setter table — every key answers a
    no-op (the real dialog wires live setters; since the DOMY default
    ring grew its own Two-metals checkbox in the ENLARGE/THEMATIC
    round, an empty dict would KeyError at build)."""
    return defaultdict(lambda: (lambda *_args: None))


def _dialog() -> DesignDialog:
    return DesignDialog(Settings(), _setters())


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
