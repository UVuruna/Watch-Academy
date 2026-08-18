"""Window registry for `uv shot` (root rules/tools/uv.py).

The factories are NOT written twice: `desktop/tests/test_layout_audit.py`
already builds every top-level window in its fullest realistic state (real
settings, real skin, real rosters) for the runtime half of THE SPACE &
LEGIBILITY LAW, and this file points the runner at those same builders. One
window built two ways is two windows in practice, and the audit's one is the
one the law is written about.

Registered here: the four windows the owner opens most, plus the three the
OOP-audit refactor round of 2026-08-18 touched (EncyclopediaDialog for R8's
screen base, ObservatoryDialog for R12's package split, TimeTravelDialog for
R9's dialog base) - exactly as this file has always instructed: add a window
below when a session touches it. LegendPopup stays in the pytest audit only.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = PROJECT_ROOT / "desktop"          # the Python root: app/, config/
TESTS_ROOT = DESKTOP_ROOT / "tests"              # layout_checks_qt, layout_drive_qt

for entry in (DESKTOP_ROOT, TESTS_ROOT):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

TOOLKIT = "qt"                                   # PySide6

# rules/devices.json - neither is the owner's machine (we build for others).
MANDATORY_PROFILES = ["laptop-avg", "pc-low"]


def prepare() -> None:
    """Offscreen Qt starts with an EMPTY font database and paints every label
    as tofu; the project's own provisioner fills it from the machine's fonts."""
    from tests.offscreen_fonts import provision

    provision()


def _audit_factory(name: str):
    """The builder of `name` from the pytest layout audit's registry."""
    from tests.test_layout_audit import WINDOWS as AUDIT_WINDOWS

    for window_name, factory, _states in AUDIT_WINDOWS:
        if window_name == name:
            return factory
    raise KeyError(f"{name} is not in desktop/tests/test_layout_audit.py "
                   "WINDOWS")


def make_watch_face():
    return _audit_factory("WatchFaceDialog")()


def make_settings_dialog():
    return _audit_factory("SettingsDialog")()


def make_shortcuts():
    return _audit_factory("ShortcutsDialog")()


def make_report():
    return _audit_factory("ReportDialog")()


def make_encyclopedia():
    return _audit_factory("EncyclopediaDialog")()


def make_observatory():
    return _audit_factory("ObservatoryDialog")()


def make_time_travel():
    return _audit_factory("TimeTravelDialog")()


WINDOWS = {
    "WatchFaceDialog": make_watch_face,
    "SettingsDialog": make_settings_dialog,
    "ShortcutsDialog": make_shortcuts,
    "ReportDialog": make_report,
    "EncyclopediaDialog": make_encyclopedia,
    "ObservatoryDialog": make_observatory,
    "TimeTravelDialog": make_time_travel,
}
