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

THE MEASURE LIVES IN ONE PLACE (WA-R15, 2026-08-19). This guard used to
count total lines minus declarative tables — comments included — while
the monorepo tool wired into the same `run_guards.py` FULL counted
non-blank, non-comment lines. The two read `app/controller.py` as 1,218
and 899, and the disagreement kept a file on the ratchet a whole
refactor after it had earned its way off. Both now read
`tests/line_measure.py`, which starts from the monorepo's definition and
keeps the owner's 2026-08-05 ruling that a declarative table is not
behaviour.
"""

from pathlib import Path

from tests.line_measure import behaviour_lines, raw_lines

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_LINES = 1000
# "worktrees" (2026-08-12): `.claude/worktrees/<agent-id>/` holds a git
# WORKTREE — a second checkout of this same repository that an isolated
# agent run left behind. Its files are copies of files this guard already
# measures at their real paths, so scanning them measures the same source
# twice and reports a RATCHETED file (app/controller.py) as a brand-new
# violation under a path no ratchet key can match. This narrows WHERE the
# law looks, never WHAT it forbids.
EXCLUDED_DIR_NAMES = {
    ".venv", "venv", "node_modules", "__pycache__", ".git", "worktrees",
}

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
    # THREE ENTRIES LEFT THIS LIST ON 2026-08-19, when WA-R15 gave the
    # project ONE arithmetic (tests/line_measure.py) instead of three:
    #   app/controller.py   885 — WA-R14 cut it into five mixins
    #   render/compositor.py 740 — WA-R13 lifted the tooltip bank out
    #   config/constants.py  125 — 645 of its 770 logic lines are
    #     declarative tables, and the owner ruled on 2026-08-05 that a
    #     table is not behaviour. Its SIZE is settled; its SHAPE is not:
    #     38 top-level sections is a junk drawer, not a directory, and
    #     the topic split is recorded as a responsibility debt in
    #     docs/ENFORCEMENT.md — it repoints 1,070 references across 142
    #     files, so the module names need the owner's own vocabulary
    #     (CANON.md), not an agent's guess.
    # The ratchet only shrinks; none of the three may come back without
    # the owner's word in that same session.
    # `render/tooltip_composer.py` (2,239 logic lines) LEFT this list on
    # 2026-08-19, and with it the LAST non-test entry: the owner ruled the
    # cut BY TOOLTIP FAMILY and it landed — render/tooltip_sky.py (624),
    # render/tooltip_ring.py (748), render/tooltip_calendar.py (514) and
    # render/encyclopedia_targets.py (262) are MIXINS on the composer, which
    # is down to 278 and keeps the two text doors, the dispatch and the six
    # shared formatting helpers (`encyclopedia_target`'s BODY rides in the
    # targets mixin; the NAME is still the composer's, by inheritance). One holder of the dial, not four; the HTML
    # of 959 hover points is proven byte-identical by
    # tests/test_tooltip_families.py, recorded BEFORE the cut. The
    # machine-readable twin (tests/structure_ratchet.json) is now EMPTY.
    # `config/pantheon.py` (1,549 lines) LEFT this list on 2026-08-05 without
    # being touched: the threshold now measures LOGIC, and 962 of its lines
    # are the declarative cast tables. Its 587 lines of actual behaviour —
    # the rotation engine, the seat resolvers, the title-plate resolver —
    # were never the god-file the law was written against. The ratchet
    # shrinks; it never grows back.
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


def _logic_lines(path: Path) -> int:
    """What the threshold actually measures — `tests/line_measure.py`
    holds the definition and the reason for every clause in it."""
    return behaviour_lines(path)


def test_no_file_crosses_the_threshold_outside_the_ratchet():
    """No new god-file, ever: every .py over MAX_LINES must be a named,
    owner-approved ratchet entry — otherwise the build fails."""
    offenders = []
    for path in _python_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if rel in RATCHET:
            continue
        logic = _logic_lines(path)
        if logic > MAX_LINES:
            offenders.append(
                f"{rel} ({logic} lines of logic, {raw_lines(path)} total)"
            )
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
        elif _logic_lines(path) <= MAX_LINES:
            stale.append(f"{rel} (healed — {_logic_lines(path)} lines of logic)")
    assert not stale, (
        "THE STRUCTURE LAW ratchet must SHRINK: delete these entries — "
        + ", ".join(sorted(stale))
    )
