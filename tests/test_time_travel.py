"""Time Travel coverage guard (owner 2026-07-16): a target outside the
bundled databases is refused INSIDE the dialog, so travelling can never
reach the day build's die-visibly SystemExit box."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from app.time_travel import TimeTravelDialog
from data.seasons import SeasonsRepository

COVERAGE = (1560, 2640)          # the seasons ∩ moon intersection


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _dialog(year: int) -> TimeTravelDialog:
    return TimeTravelDialog(
        44.8, 20.5,
        initial_moment=datetime(year, 6, 1, 12, 0),
        coverage=COVERAGE,
    )


def test_far_future_year_is_rejected(app):
    """Owner screenshot: travelling to 4500 raised ValueError and killed
    the app — now the dialog refuses it and stays open."""
    dialog = _dialog(4500)
    assert dialog.moment().year == 4500
    assert dialog.target_within_coverage() is False
    dialog.accept()                                   # the user clicks OK
    assert dialog.result() != QDialog.DialogCode.Accepted   # no travel
    assert not dialog._coverage_warning.isHidden()          # message shown
    assert dialog._coverage_warning.text()                  # ...with content


def test_ancient_year_is_rejected(app):
    """The other screenshot: ~150 CE, far below coverage, is refused too."""
    dialog = _dialog(150)
    assert dialog.target_within_coverage() is False
    dialog.accept()
    assert dialog.result() != QDialog.DialogCode.Accepted


def test_in_range_year_is_accepted(app):
    """A year the databases cover travels normally (dialog accepts)."""
    dialog = _dialog(2100)
    assert dialog.target_within_coverage() is True
    dialog.accept()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_boundary_years_are_inclusive(app):
    """The first and last covered years are valid; one step past is not."""
    first, last = COVERAGE
    assert _dialog(first).target_within_coverage() is True
    assert _dialog(last).target_within_coverage() is True
    assert _dialog(first - 1).target_within_coverage() is False
    assert _dialog(last + 1).target_within_coverage() is False


def test_no_coverage_means_no_guard(app):
    """Without a coverage bound (defensive default) the dialog imposes no
    restriction — the controller always supplies one in practice."""
    dialog = TimeTravelDialog(
        44.8, 20.5, initial_moment=datetime(4500, 6, 1, 12, 0),
    )
    assert dialog.target_within_coverage() is True


def test_refused_year_is_exactly_what_the_day_build_cannot_render(app):
    """Proof the guard blocks the crash, not something adjacent: the year
    the dialog refuses is the same year year_anchors() raises on — so
    refusing travel is what prevents the die-visibly SystemExit path."""
    assert _dialog(4500).target_within_coverage() is False
    with pytest.raises(ValueError, match="no entry for 4500"):
        SeasonsRepository().year_anchors(4500)
