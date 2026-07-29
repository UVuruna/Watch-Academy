"""THE STRUCTURE LAW's guard — the god-file ratchet.

Root CLAUDE.md, Rule #20 -> THE STRUCTURE LAW (owner decree 2026-07-29,
SUPREME): every project carries a structure guard test that FAILS the
build when any file crosses the Violation threshold (~1,000 lines),
except files named in a RATCHET allowlist that may only SHRINK. Each
entry documents why it is tolerated today and which session owes the
split. A file that heals (drops to or under the threshold) MUST be
deleted from the list — the second test enforces the shrink.

Born the same day the law was: `config/defaults.py` at 3,498 lines with
no section banners and `render/layers.py` at 3,521 had been flagged for
weeks and tolerated, because no test failed. This one fails.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_LINES = 1000
EXCLUDED_DIR_NAMES = {".venv", "venv", "node_modules", "__pycache__", ".git"}

# THE RATCHET — may only SHRINK (THE STRUCTURE LAW, clause 3). Adding an
# entry requires the owner's explicit approval in that same session.
# Entry: posix-relative path -> (why it is tolerated, who owes the split).
RATCHET: dict[str, tuple[str, str]] = {
    "render/layers.py": (
        "every pointer's draw code accreted into one file",
        "the render split session proposed in WORKPLAN §Open Owner Decisions",
    ),
    "config/defaults.py": (
        "the historical config god-file the law was decreed over",
        "Session 36 — the config split (WORKPLAN-STRUCTURE.md)",
    ),
    "app/controller.py": (
        "window shell, menus, tick plumbing and settings glue in one file",
        "an app split round — owed, not yet scheduled",
    ),
    "render/compositor.py": (
        "scene assembly, hover and tooltip logic in one file",
        "the render split session, together with layers.py",
    ),
    "config/constants.py": (
        "the second config god-file; Session 36's map covers defaults.py only",
        "a constants split round after Session 36, same snapshot method",
    ),
    "app/observatory.py": (
        "the statistics window in one file",
        "the app split round",
    ),
    "tests/test_pointer.py": (
        "one test file pins every pointer",
        "a test split-by-subsystem hygiene round — owed, not yet scheduled",
    ),
    "tests/test_settings_dialog.py": (
        "one test file pins the whole settings dialog",
        "the test hygiene round",
    ),
    "tests/test_skins.py": (
        "one test file pins every skin",
        "the test hygiene round",
    ),
    "tests/test_archetype.py": (
        "one test file pins the whole archetype system",
        "the test hygiene round",
    ),
    "tests/test_eclipse.py": (
        "one test file pins the whole eclipse pipeline",
        "the test hygiene round",
    ),
}


def _python_files():
    for path in PROJECT_ROOT.rglob("*.py"):
        if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
            continue
        yield path


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


def test_no_file_crosses_the_threshold_outside_the_ratchet():
    """No new god-file, ever: every .py over MAX_LINES must be a named,
    owner-approved ratchet entry — otherwise the build fails."""
    offenders = []
    for path in _python_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if rel in RATCHET:
            continue
        lines = _line_count(path)
        if lines > MAX_LINES:
            offenders.append(f"{rel} ({lines} lines)")
    assert not offenders, (
        "THE STRUCTURE LAW (root CLAUDE.md, Rule #20): these files crossed "
        f"the {MAX_LINES}-line violation threshold and are NOT in the "
        "ratchet: " + ", ".join(sorted(offenders)) + ". Split by "
        "responsibility, or obtain the owner's explicit ratchet entry in "
        "this same session — never silently."
    )


def test_the_ratchet_only_shrinks():
    """A healed or vanished file must leave the list — the ratchet may
    never hold a file that no longer needs tolerating."""
    stale = []
    for rel in RATCHET:
        path = PROJECT_ROOT / rel
        if not path.exists():
            stale.append(f"{rel} (file no longer exists)")
        elif _line_count(path) <= MAX_LINES:
            stale.append(f"{rel} (healed — {_line_count(path)} lines)")
    assert not stale, (
        "THE STRUCTURE LAW ratchet must SHRINK: delete these entries — "
        + ", ".join(sorted(stale))
    )
