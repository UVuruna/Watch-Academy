"""THE PERMANENTLY DEAD WINDOW (owner crash log 2026-07-31) — the pin.

One `ValueError` out of the render stack escaped `paintEvent` with the
`QPainter` still active; every later frame then failed with
`QBackingStore::endPaint() called with active painter` and the widget
never drew again ("QPaintDevice: Cannot destroy paint device that is
being painted" on teardown). The law pinned here: `paintEvent` ends its
painter on EVERY exit path — a failing frame prints its traceback,
stays partially drawn, and the NEXT frame paints normally. This is the
GUI top-level boundary the No-Error-Masking rule explicitly allows.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu

from app.widget import ClockWidget


class _ExplodingRenderer:
    """Stands in for the compositor: fails N times, then paints fine."""

    def __init__(self, failures: int):
        self.failures = failures
        self.calls = 0

    def paint(self, painter, diameter, dpr, tick):
        self.calls += 1
        if self.calls <= self.failures:
            raise ValueError("cannot load image asset: <half-written cache>")


def _widget():
    app = QApplication.instance() or QApplication([])
    menu = QMenu()
    widget = ClockWidget(
        diameter=120, menu=menu, legend=None, show_action=QAction("Show"),
    )
    return app, widget


def test_a_failing_frame_never_kills_the_next_one(capsys):
    """The crash scenario end to end: frame 1 raises inside the render
    stack, frames 2+ must still paint — and the first SUCCESSFUL frame
    is the one that announces `first_painted`."""
    app, widget = _widget()
    # Fail EVERY frame until the pin flips the switch below — the
    # exposure paint(s) show() itself triggers must fail too, so the
    # widget enters the pinned sequence in the crashed state.
    renderer = _ExplodingRenderer(failures=10 ** 9)
    widget.set_renderer(renderer)
    announced = []
    widget.first_painted.connect(lambda: announced.append(True))
    widget.set_tick(object())
    widget.show()
    app.processEvents()                   # deliver the exposure paint(s)

    widget.repaint()                      # one more failing frame, explicit
    failed_frames = renderer.calls
    assert failed_frames >= 1, "the failing frame never painted at all"
    assert "cannot load image asset" in capsys.readouterr().err
    assert announced == [], "a failed frame must not announce first_painted"

    renderer.failures = 0                 # the cache healed (atomic writes)
    widget.repaint()                      # next frame must paint normally
    assert renderer.calls == failed_frames + 1
    assert announced == [True], "the first SUCCESSFUL frame announces once"

    widget.repaint()                      # still alive, no re-announce
    assert renderer.calls == failed_frames + 2
    assert announced == [True]
    widget.close()
