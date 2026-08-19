"""One WATCH ACADEMY WINDOW — the four things every one of them does.

Seven top-level dialogs open off the dial: the Encyclopedia, the
Observatory, the Report, the Shortcuts table, Time Travel, Settings and
the Watch Face window. Every one of them opened by writing the same four
incantations again — the translation overlay, a `tr` over it, the
`"Watch Academy — <name>"` title, and the stay-on-top flag — which is
why the OOP audit of 2026-08-18 listed "top-level dialog" as a kind with
EIGHT instances and NO base class.

A window now declares what it is called and whether it floats; the rest
is inherited. Adding an eighth is subclassing, not remembering.

What is deliberately NOT here:

* **`apply_theme(self)`.** Its POSITION is load-bearing and differs by
  window: the Watch Face window themes BEFORE it builds, because it
  computes its own minimum from the pages' size hints and the QSS
  paddings are part of the real size (measured 20px on the Colors
  groups); the others theme after their content exists. Pulling it into
  `__init__` would silently move every one of those measurements.
* **The opening size and the computed minimum.** Each window measures
  its own content — a nav column plus the widest panel, a chart's
  aspect ratio, a table's rows. There is no arithmetic to share.
* **`TintPopover`.** The audit counted it as the eighth QDialog, but it
  is a frameless `Qt.Popup` that RECEIVES its `tr` from the section
  building it: no title bar, no stay-on-top, no overlay of its own. It
  is a picker, not a window, and it stays as it is.

Layer: app. Documentation: __about/dialog_base.md.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from config import identity
from config.ui_text import ui


class AcademyDialog(QDialog):
    """A top-level Watch Academy window.

    `title` is the plain-English chrome name (`"Observatory"`), which is
    translated here and hung after the app name. `stay_on_top` is the
    controller's `z_mode == "top"` reading: a NORMAL window by default
    (owner 2026-07-13 — a window must yield to whatever has focus), but
    in "top" z-mode the dial forces itself to the TRUE top of the
    Z-order (`native.assert_topmost`, HWND_TOPMOST) and an ordinary
    window would open UNDER it (owner verdict 2026-07-19). The windows
    that are always modal ask for it outright."""

    def __init__(self, title: str, overlay: dict | None = None,
                 stay_on_top: bool = False, parent=None):
        super().__init__(parent)
        self._overlay = overlay or {}
        self.setWindowTitle(f"{identity.APP_NAME} — {self._tr(title)}")
        if stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

    def _tr(self, text: str) -> str:
        """The active language's form of a chrome string."""
        return ui(self._overlay, text)
