"""The computation core and the data layer must stay Qt-free — that is
what makes them testable headless and reusable outside the widget."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_core_and_data_do_not_touch_qt():
    offenders = [
        str(source.relative_to(PROJECT_ROOT))
        for package in ("core", "data")
        for source in (PROJECT_ROOT / package).glob("*.py")
        if "PySide6" in source.read_text(encoding="utf-8")
    ]
    assert offenders == []
