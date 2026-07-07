"""The computation core and the data layer must stay pure — Qt-free and
free of wall-clock reads. That is what makes them deterministic, testable
headless and reusable outside the widget.

core/__main__.py is exempt from the wall-clock rule: it is CLI entry-point
glue whose documented default is "now".
"""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WALL_CLOCK_CALLS = {"now", "today"}      # datetime.now(), date.today()


def _sources(package: str):
    return sorted((PROJECT_ROOT / package).glob("*.py"))


def _wall_clock_calls(source: Path) -> list[str]:
    """Actual call sites only — docstrings and comments don't count."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else (
                func.id if isinstance(func, ast.Name) else None
            )
            if name in WALL_CLOCK_CALLS:
                hits.append(f"line {node.lineno}: {name}()")
            elif name == "time" and isinstance(func, ast.Attribute):
                # time.time() — but not the datetime.time constructor
                if isinstance(func.value, ast.Name) and func.value.id == "time":
                    hits.append(f"line {node.lineno}: time.time()")
    return hits


def test_core_and_data_do_not_touch_qt():
    offenders = [
        str(source.relative_to(PROJECT_ROOT))
        for package in ("core", "data")
        for source in _sources(package)
        if "PySide6" in source.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_core_and_data_do_not_read_the_wall_clock():
    offenders = [
        f"{source.relative_to(PROJECT_ROOT)} ({hit})"
        for package in ("core", "data")
        for source in _sources(package)
        if source.name != "__main__.py"
        for hit in _wall_clock_calls(source)
    ]
    assert offenders == []
