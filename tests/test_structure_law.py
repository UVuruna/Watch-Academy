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
    # `render/layers.py` (3,881 lines) LEFT this list on 2026-08-01: split
    # into `render/layers/` (one module per layer) plus twelve
    # responsibility modules beside it (context, painting, subdial,
    # skin_geometry, calendar_mount, shapes, daylight, eclipse_glow,
    # slot_layout, archetype_geometry, ninths, weekday_body). The ratchet
    # shrinks; it never grows back.
    "app/controller.py": (
        "3,449 lines: ~780 of module-level skin building (build_skin, "
        "apply_display_settings, display_for, watch_title and their "
        "helpers) plus a 2,577-line WatchController carrying the window/"
        "tray/menu shell, dialog opening, shortcuts, time travel and tick "
        "plumbing. The 2026-08-01 split session mapped it but did NOT cut "
        "it: the free functions lift out cleanly into app/skin_builder.py, "
        "but the controller itself needs responsibility MIXINS or "
        "collaborator objects, and every step costs an 18-minute suite run",
        "a dedicated app-controller split session — start with "
        "app/skin_builder.py (self-contained, 15 test files import those "
        "four names directly), then the class",
    ),
    "render/compositor.py": (
        "3,311 lines carrying THREE responsibilities: layer stacking with "
        "cadence-driven caching (~450 lines), hit-testing (_element_at, "
        "_weekday_body_at, _arm_angle_at, set_hover, encyclopedia_target "
        "and its targeters), and a ~2,000-line bank of tooltip/article "
        "HTML builders. The 2026-08-01 session split render/layers.py and "
        "mapped this one, but the tooltip bank is METHODS reading self._"
        "skin/_day/_tick and the repositories — extracting it means a "
        "collaborator object, not a file move",
        "a dedicated compositor split session — lift the free HTML "
        "helpers to render/article_html.py first, then the tooltip bank "
        "into a TooltipComposer, then hit-testing",
    ),
    "config/constants.py": (
        "the second config god-file; Session 36's map covers defaults.py only",
        "a constants split round after Session 36, same snapshot method",
    ),
    "config/pantheon.py": (
        "the weekday theme registry outgrew Session 36's estimate — twelve "
        "wave casts plus the roster/rotation engine total ~1.55k lines even "
        "after the continents carve (math in config/pantheon.md); entry "
        "APPROVED by the owner 2026-07-29 in the coordination session",
        "a pantheon split round — static tables vs the rotation engine vs "
        "the cast tables; not yet scheduled",
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
