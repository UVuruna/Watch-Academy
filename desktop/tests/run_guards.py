"""The guard runner — the teeth behind the Claude Code hooks.

Root `rules/CODE.md` -> Guards: a rule without a check is a request.
This wrapper runs ONLY the law guards (never the full app suite, which
takes ~18 minutes here), prints failures to stderr and exits **2** — the
exit code that makes a Claude Code hook BLOCKING.

    python desktop/tests/run_guards.py            FULL   (Stop hook)
    python desktop/tests/run_guards.py --fast     cheap  (PostToolUse hook)

`--fast` is what fires after every Edit/Write: the guards that read
source text and finish in a second, so the agent gets blocking feedback
the moment it saves a file.

THE FULL PASS IS SCOPED TO WHAT THE SESSION ACTUALLY TOUCHED
(rules/history/2026-08-18-rework-design.md ch.8 item 2). The one
authority on that is `rules/hooks/changed_files.py`, and its "cannot
tell" answer (no git, no upstream, an unreachable helper) always means
RUN EVERYTHING — a broken helper never silently disables a law.

Three tiers:

* **always** — the cheap guards plus the docs/name laws (~10 s total).
* **art** — `test_art_reachability.py` walks the whole `shared/assets/`
  tree and imports every `config` module; it only has a job when art,
  a config table or the guard itself moved.
* **GUI** — `test_layout_audit.py` BUILDS every registered window and
  measures it. Scoped twice over: it runs only when a GUI file changed,
  and then only for the windows that file belongs to. A session that
  edits `app/report.py` audits ReportDialog, not eight windows.

The full pass also runs the monorepo clone guard against this project's
`tests/clone_ratchet.json` (ONE KIND, ONE CLASS), the monorepo structure
guard against `tests/structure_ratchet.json` (the machine-readable
god-file ratchet other tools read: a file over the wall needs a written
reason, and a ratcheted file may only SHRINK) and the rules-size guard
(`CLAUDE.md` <= 6,000 bytes).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
DESKTOP_ROOT = TESTS_DIR.parent                  # <repo>/desktop
PROJECT_ROOT = DESKTOP_ROOT.parent               # <repo>  (the TRUE root)
REPO_ROOT = PROJECT_ROOT.parents[1]              # the UVuruna monorepo root

# ══════════════════════════════ THE GUARD TIERS ══════════════════════════════

# THE STRUCTURE LAW, THE CONFIG SECTION LAW and the static half of THE
# SPACE & LEGIBILITY LAW read source text only — milliseconds, safe to
# fire after every single edit.
FAST_GUARDS = (
    "test_structure_law.py",
    "test_config_sections.py",
    "test_layout_law.py",
)

# THE DOCS LAW walks every .md; THE OLD NAME NEVER COMES BACK
# (2026-08-12) walks every text file. Both only need to hold when the
# session tries to END.
ALWAYS_FULL_GUARDS = FAST_GUARDS + (
    "test_docs_coverage.py",
    "test_doc_links.py",
    "test_old_name.py",
)

# NO ART SITS UNSEEN over the whole assets tree (owner ruling
# 2026-08-05): it imports every config module and stats thousands of
# files, so it runs when — and only when — one of these moved.
ART_GUARD = "test_art_reachability.py"
ART_TRIGGERS = (
    "shared/assets/",
    "masters/",
    "desktop/config/",
    "desktop/tests/test_art_reachability.py",
)
# The staging ledger is prose the art guard actually READS, so it is the
# one .md that counts as a trigger (see `_code_paths`).
ART_DOC_TRIGGERS = ("shared/research/theme_staging.md",)

# ══════════════════════════════ THE GUI SCOPE ════════════════════════════════

LAYOUT_GUARD = "test_layout_audit.py"

# Which source belongs to which registered window. Paths are
# repo-relative prefixes; a directory prefix ends with "/".
# `rules/hooks/changed_files.is_gui_path` cannot answer this project —
# its markers are gui/ui/widgets/views/qml/windows and this app's GUI
# lives in `desktop/app/` — so the project states its own map. Keep it
# beside `test_layout_audit.WINDOWS`: a new window needs a row here or
# it is never audited.
WINDOW_SOURCES: dict[str, tuple[str, ...]] = {
    "WatchFaceDialog": ("desktop/app/watch_face/",),
    "SettingsDialog": ("desktop/app/settings_dialog/",),
    "EncyclopediaDialog": ("desktop/app/encyclopedia/",),
    "ObservatoryDialog": ("desktop/app/observatory.py",),
    "ReportDialog": ("desktop/app/report.py",),
    "ShortcutsDialog": ("desktop/app/shortcuts_window.py",),
    "TimeTravelDialog": ("desktop/app/time_travel.py",),
    "LegendPopup": ("desktop/app/legend_popup.py",),
}

# GUI ground that belongs to NO single window — the shell, the painting
# stack, the typed render configuration, and the audit's own machinery.
# Touching any of it audits EVERY window: a change here can starve a
# label in a dialog nobody edited.
SHARED_GUI_PREFIXES = (
    "desktop/app/",
    "desktop/render/",
    "desktop/skins/",
    "desktop/tests/test_layout_audit.py",
    "desktop/tests/layout_checks_qt.py",
    "desktop/tests/layout_drive_qt.py",
    "desktop/tests/zubi_baseline.json",
    ".claude/layout-frame.json",
    ".claude/uv_windows.py",
)


def _load(rel_path: str):
    """Load a monorepo-root module by path; None when it cannot be
    reached. Callers MUST treat None as "assume the worst"."""
    path = REPO_ROOT / rel_path
    try:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except (OSError, AttributeError, ImportError, SyntaxError, TypeError):
        return None


def _hits(paths: list[str], prefixes) -> bool:
    return any(p.startswith(prefix) for p in paths for prefix in prefixes)


def _code_paths(paths: list[str]) -> list[str]:
    """`paths` without documentation.

    The art guard stats files and the layout audit measures widgets;
    neither can be broken by editing a `.md` beside the code, and a
    docs round that rewrote a `__about/` file used to pay for the full
    tree walk and eight built windows. The one exception is declared in
    `ART_DOC_TRIGGERS` — a doc the guard itself parses."""
    return [p for p in paths if not p.endswith(".md")]


def windows_to_audit(paths: list[str] | None) -> list[str] | None:
    """Which registered windows this session must re-measure.

    `None` (cannot tell, or shared GUI ground moved) means ALL of them;
    an empty list means the layout audit has no job this session.
    """
    if paths is None:
        return None
    paths = _code_paths(paths)
    named = [name for name, prefixes in WINDOW_SOURCES.items()
             if _hits(paths, prefixes)]
    unowned = [p for p in paths
               if any(p.startswith(prefix) for prefix in SHARED_GUI_PREFIXES)
               and not any(
                   p.startswith(prefix)
                   for prefixes in WINDOW_SOURCES.values()
                   for prefix in prefixes)]
    if unowned:
        return None
    return named


def _pytest(names, extra=()) -> int:
    args = [str(TESTS_DIR / name) for name in names]
    # -p no:cacheprovider keeps the hook from fighting a concurrent test
    # run over .pytest_cache; --no-header -q keeps the hook output short.
    args += [*extra, "-q", "--no-header", "-p", "no:cacheprovider"]
    return pytest.main(args)


def _fail(label: str) -> int:
    print(
        f"\nGUARDS FAILED ({label}) — the laws in the monorepo "
        "constitution are not satisfied. Fix the violation above; do "
        "NOT weaken the guard or add a ratchet entry without the "
        "owner's explicit approval in this same session.",
        file=sys.stderr,
    )
    return 2


def main(argv: list[str]) -> int:
    if "--fast" in argv:
        return 0 if _pytest(FAST_GUARDS) == 0 else _fail("FAST")

    changed = _load("rules/hooks/changed_files.py")
    paths = None if changed is None else changed.changed_files(PROJECT_ROOT)
    if paths is not None and not paths:
        print("guards: session changed no file — full pass skipped")
        return 0

    guards = list(ALWAYS_FULL_GUARDS)
    if (paths is None
            or _hits(_code_paths(paths), ART_TRIGGERS)
            or _hits(paths, ART_DOC_TRIGGERS)):
        guards.append(ART_GUARD)
    if _pytest(guards) != 0:
        return _fail("FULL")

    windows = windows_to_audit(paths)
    if windows is None or windows:
        selection: tuple[str, ...] = ()
        if windows:
            # DESELECT the untouched windows by exact node id rather than
            # filtering with `-k`: a `-k` expression is matched against the
            # whole node id, FILE NAME INCLUDED, so "not test_layout_audit"
            # silently deselects every test in test_layout_audit.py —
            # including the taxonomy and self-checks, which are cheap,
            # window-independent, and must always run.
            skipped = [name for name in WINDOW_SOURCES if name not in windows]
            selection = tuple(
                argument
                for name in skipped
                for argument in ("--deselect",
                                 f"{TESTS_DIR / LAYOUT_GUARD}"
                                 f"::test_layout_audit[{name}]")
            )
            print(f"guards: layout audit scoped to {', '.join(windows)}")
        if _pytest((LAYOUT_GUARD,), selection) != 0:
            return _fail("FULL / layout audit")
    else:
        print("guards: no GUI file changed — layout audit skipped")

    clone_guard = _load("rules/tools/clone_guard.py")
    if clone_guard is not None:
        ratchet = TESTS_DIR / "clone_ratchet.json"
        if clone_guard.run([str(PROJECT_ROOT), "--ratchet", str(ratchet)]) != 0:
            print("\nGUARD FAILURE (FULL) — clone_guard found an "
                  "un-ratcheted duplicate (ONE KIND, ONE CLASS). Extract "
                  "the shared base or registry; the ratchet only shrinks.",
                  file=sys.stderr)
            return 2

    structure_guard = _load("rules/tools/structure_guard.py")
    if structure_guard is not None:
        problems = structure_guard.check(
            DESKTOP_ROOT, TESTS_DIR / "structure_ratchet.json", wall=1000)
        if problems:
            for line in problems:
                print(line, file=sys.stderr)
            print("\nGUARD FAILURE (FULL) — THE STRUCTURE LAW's machine-"
                  "readable ratchet (structure_ratchet.json) rejects this "
                  "tree: a file over the wall with no written reason, or a "
                  "ratcheted file that GREW. Put the code in the module "
                  "whose responsibility it serves; the ratchet only shrinks.",
                  file=sys.stderr)
            return 2

    size_guard = _load("rules/tools/rules_size_guard.py")
    if size_guard is not None:
        rows = size_guard.check(project=PROJECT_ROOT)
        if any(not ok for _, _, _, ok, _ in rows):
            print("\nGUARD FAILURE (FULL) — a rulebook is over its byte "
                  "limit (rules_size_guard). Move the prose into docs/.",
                  file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
