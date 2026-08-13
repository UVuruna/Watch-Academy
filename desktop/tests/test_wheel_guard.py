"""Accidental-scroll guard regression (owner bug 2026-08-13): scrolling
the mouse wheel over an unfocused QComboBox/QAbstractSpinBox/QSlider
must NOT change its value — the owner was losing settings by resting
the cursor over a dropdown mid-scroll. The fix is ONE application-level
event filter (`app.theme._install_wheel_guard`, wired through
`apply_theme`) rather than a per-call-site patch, because there is no
shared combo-box factory in this codebase — see `app/theme.py`."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import theme


def _make_combo_in_scroll_area():
    """A QComboBox with 3 items, seated inside a QScrollArea — the real
    shape every settings section builds (a scrollable panel of rows)."""
    app = QApplication.instance() or QApplication([])
    theme.apply_theme(QWidget())  # ensures the guard is installed, as
    # every real dialog does via its own apply_theme(self) call

    scroll = QScrollArea()
    content = QWidget()
    layout = QVBoxLayout(content)
    # A second focusable widget to actually MOVE focus off the combo —
    # under the offscreen test platform a freshly-shown QComboBox is the
    # only focusable widget in its window and quietly keeps focus even
    # after clearFocus(), which would make the "unfocused" case below a
    # no-op test (index 0 can't decrease further either way, and the
    # combo secretly still has focus). A sibling to focus instead.
    other = QPushButton("elsewhere")
    combo = QComboBox()
    combo.addItems(["A", "B", "C"])
    layout.addWidget(combo)
    layout.addWidget(other)
    scroll.setWidget(content)
    scroll.setWidgetResizable(True)
    scroll.resize(200, 200)
    scroll.show()
    return app, scroll, combo, other


def _send_wheel(widget, steps=1) -> None:
    event = QWheelEvent(
        QPointF(5, 5),
        QPointF(5, 5),
        QPoint(0, 0),
        QPoint(0, 120 * steps),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    QApplication.sendEvent(widget, event)


def test_unfocused_combo_ignores_wheel():
    _app, scroll, combo, other = _make_combo_in_scroll_area()
    combo.setCurrentIndex(1)
    scroll.activateWindow()
    other.setFocus(Qt.FocusReason.MouseFocusReason)  # move focus OFF the combo
    QApplication.processEvents()
    assert not combo.hasFocus()

    _send_wheel(combo)

    assert combo.currentIndex() == 1, (
        "an unfocused QComboBox must not change value on mouse wheel"
    )
    scroll.close()


def test_focused_combo_still_responds_to_wheel():
    _app, scroll, combo, _other = _make_combo_in_scroll_area()
    combo.setCurrentIndex(1)
    scroll.activateWindow()
    combo.setFocus(Qt.FocusReason.MouseFocusReason)
    QApplication.processEvents()
    assert combo.hasFocus()

    _send_wheel(combo)  # positive angleDelta().y() == scroll "up" == prev item

    assert combo.currentIndex() == 0, (
        "a deliberately-focused QComboBox keeps normal wheel behaviour"
    )
    scroll.close()
