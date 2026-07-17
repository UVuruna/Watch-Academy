"""Time Travel dialog goldens: the BCE-capable moment editor (Session
16, owner slika 13), the coverage guard (owner 2026-07-16 — a target
outside the active span is refused INSIDE the dialog), the precision
tier lines and the dual-calendar header."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from app.time_travel import TimeTravelDialog
from data.seasons import SeasonsRepository

BUNDLED = (1560, 2640)           # the seasons ∩ moon intersection
DEEP = (-12997, 16993)           # the real pack's coverage (its meta;
                                 # first bound set by the Chinese-cusp
                                 # January rule — see make_deep_time)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _dialog(year: int, coverage=BUNDLED, deep_pack=False, **kwargs):
    return TimeTravelDialog(
        44.8, 20.5,
        initial_moment=datetime(abs(year) if year > 0 else 2026, 6, 1, 12, 0),
        coverage=coverage,
        core_coverage=BUNDLED,
        deep_pack=deep_pack,
        **kwargs,
    )


def test_far_future_year_is_rejected_without_the_pack(app):
    """Owner screenshot: travelling to 4500 raised ValueError and killed
    the app — the dialog refuses it and stays open, naming the pack."""
    dialog = _dialog(4500)
    assert dialog.moment().year == 4500
    assert dialog.target_within_coverage() is False
    dialog.accept()                                   # the user clicks OK
    assert dialog.result() != QDialog.DialogCode.Accepted   # no travel
    assert not dialog._coverage_warning.isHidden()          # message shown
    assert "not installed" in dialog._coverage_warning.text()


def test_bce_target_accepted_with_the_pack(app):
    """Owner slika 13: 4500 BCE (era combo + year spin) travels once
    the Deep Time pack is present — the moment maps to the 400-year
    proxy frame."""
    dialog = _dialog(2026, coverage=DEEP, deep_pack=True)
    dialog._era.setCurrentIndex(1)                    # BCE
    dialog._year.setValue(4500)
    dialog._month.setCurrentIndex(5)                  # June
    dialog._day.setValue(21)
    assert dialog.astro_year() == -4499               # 1 BCE = year 0
    assert dialog.target_within_coverage() is True
    assert dialog.cycles() == 17
    assert dialog.moment() == datetime(2301, 6, 21, 12, 0)
    dialog.accept()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_beyond_the_pack_names_the_laskar_tier(app):
    """Tier (iii) documented in-app: beyond the Deep Time span the
    refusal explains that only era lengths are known — and the spinbox
    deliberately reaches PAST coverage so the message is readable
    (owner 2026-07-16)."""
    dialog = _dialog(2026, coverage=DEEP, deep_pack=True)
    dialog._era.setCurrentIndex(1)
    assert dialog._year.maximum() == 13001            # advertised span
    dialog._year.setValue(12998)                      # astro -12997 = edge
    assert dialog.target_within_coverage() is True
    dialog._year.setValue(12999)                      # astro -12998: beyond
    assert dialog.target_within_coverage() is False
    dialog.accept()
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert "era lengths" in dialog._coverage_warning.text()


def test_tier_lines_follow_the_entered_year(app):
    dialog = _dialog(2026, coverage=DEEP, deep_pack=True)
    assert "minute-exact" in dialog._tier_line.text()
    dialog._era.setCurrentIndex(1)
    dialog._year.setValue(4500)
    assert "ΔT" in dialog._tier_line.text()
    assert "Coverage:" in dialog._coverage_line.text()
    assert "12998 BCE" in dialog._coverage_line.text()


def test_dual_calendar_header(app):
    """The owner amendment 2026-07-17: the Anno Lucis year ALWAYS
    accompanies the official year in the header."""
    dialog = _dialog(2026, coverage=DEEP, deep_pack=True)
    assert "6105. Anno Lucis" in dialog._header.text()
    dialog._era.setCurrentIndex(1)
    dialog._year.setValue(4079)
    assert "1. Anno Lucis" in dialog._header.text()


def test_third_era_joins_the_header(app):
    dialog = _dialog(
        2026, coverage=DEEP, deep_pack=True, third_era="hebrew",
    )
    assert "5786. Hebrew A.M." in dialog._header.text()


def test_era_notation_governs_the_labels(app):
    dialog = _dialog(2026, coverage=DEEP, deep_pack=True, era_notation="bc_ad")
    assert [dialog._era.itemText(i) for i in range(dialog._era.count())] == [
        "AD", "BC",
    ]


def test_day_clamps_to_the_proleptic_month(app):
    """Feb 29 exists only in leap astronomical years — year 0 (1 BCE)
    IS leap, 4500 BCE (astro -4499) is not."""
    dialog = _dialog(2026, coverage=DEEP, deep_pack=True)
    dialog._month.setCurrentIndex(1)                  # February
    dialog._era.setCurrentIndex(1)
    dialog._year.setValue(1)                          # 1 BCE = astro 0, leap
    assert dialog._day.maximum() == 29
    dialog._year.setValue(4500)                       # astro -4499, common
    assert dialog._day.maximum() == 28


def test_in_range_year_is_accepted(app):
    dialog = _dialog(2100)
    assert dialog.target_within_coverage() is True
    dialog.accept()
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_boundary_years_are_inclusive(app):
    first, last = BUNDLED
    assert _dialog(first).target_within_coverage() is True
    assert _dialog(last).target_within_coverage() is True
    assert _dialog(first - 1).target_within_coverage() is False
    assert _dialog(last + 1).target_within_coverage() is False


def test_no_coverage_means_no_guard(app):
    """Without a coverage bound (defensive default) the dialog imposes
    no restriction — the controller always supplies one in practice."""
    dialog = TimeTravelDialog(
        44.8, 20.5, initial_moment=datetime(4500, 6, 1, 12, 0),
    )
    assert dialog.target_within_coverage() is True


def test_refused_year_is_exactly_what_the_day_build_cannot_render(app):
    """Proof the guard blocks the crash, not something adjacent: the
    year the dialog refuses is the same year year_anchors() raises on
    (without the pack) — so refusing travel is what prevents the
    die-visibly SystemExit path."""
    assert _dialog(4500).target_within_coverage() is False
    with pytest.raises(ValueError, match="no entry for 4500"):
        SeasonsRepository().year_anchors(4500)