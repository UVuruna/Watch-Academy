"""Guard: no shipped file still calls this project DOMY Watch.

The rename landed on 2026-08-11/12 (folder `Applications/WatchAcademy`, out of
`Gadgets/`). Its sibling project's rename failed the first time in a way worth
copying the lesson from: a file type the sweep tool did not know was patched by
hand, the hand searched ONE spelling, and the verification grep then repeated
the same incomplete pattern — so it confirmed the blind spot instead of finding
it. The owner met the old name in a title bar.

So this guard does not grep for a string somebody remembered. It matches EVERY
spelling of the old project name — spaced, hyphenated, underscored, joined, any
case — and treats each hit as a failure unless that exact line is on a short
list with a stated reason.

**DOMY alone is never a hit.** It is the name of the DIAL, it runs through the
canon, the themes and the docs, and it is staying. Only "DOMY Watch" — the
thing this project used to be CALLED — is the old name.
"""

import os
import re

from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".pytest_cache", ".gradle", "bin", "obj", ".claude", "UV", "logs",
    # The owner's own research scratch and generated state: not shipped, and
    # full of dated run logs that name the paths as they were.
    "research", "_state",
}

OLD_NAME = re.compile(r"domy[ _\-]?watch", re.IGNORECASE)

# Permanently correct mentions. A line passes only when its FILE is listed AND
# the line itself matches one of that file's fragments — a whole-file exemption
# is what let the sibling project's bug hide, since the same file also held a
# line that was genuinely wrong.
ALLOWED: dict[str, tuple[str, ...]] = {
    # The settings migration must NAME the folder it carries data out of:
    # %APPDATA%\DOMY Watch is where the app lived for its whole prior life.
    "config/constants.py": ('APP_NAME_LEGACY = "DOMY Watch"',),
    "main.py": ("%APPDATA%/DOMY Watch",),
    "app/__about/warm.md": ("%APPDATA%\\DOMY Watch",),
    "tests/test_system_trio.py": ("%APPDATA%/DOMY Watch",),
    # NOT the project: "a DOMY watch and a LOOP watch" names two WATCHES by
    # the dial each wears — the sentence only reads as the old name because
    # the words happen to sit next to each other. DOMY is staying.
    "config/paths.py": ("a DOMY watch and a LOOP watch",),
    "config/__about/paths.md": ("DOMY watch and a LOOP watch",),
    # Dated records: they say what the project was CALLED then, and rewriting
    # a record falsifies it.
    "WORKPLAN.md": ('(then still "DOMY Watch")',
                    'UNCHANGED item at the time was the disk folder name',
                    "the `%APPDATA%\\DOMY Watch` id the settings"),
}


def _allowed(rel: str, line: str) -> bool:
    return any(fragment in line for fragment in ALLOWED.get(rel, ()))


def test_no_shipped_file_carries_the_old_project_name():
    survivors = []
    for current, directories, files in os.walk(PROJECT):
        directories[:] = [d for d in directories if d not in SKIP_DIRS]
        for name in files:
            path = Path(current) / name
            if path.resolve() == Path(__file__).resolve():
                continue                    # this guard's whole job is to spell it
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue                    # binary or unreadable: not text we ship
            rel = path.relative_to(PROJECT).as_posix()
            for number, line in enumerate(text.splitlines(), 1):
                if OLD_NAME.search(line) and not _allowed(rel, line):
                    survivors.append(f"{rel}:{number}: {line.strip()[:120]}")

    assert not survivors, (
        "THE OLD NAME SURVIVES: these lines still call this project DOMY "
        "Watch, and a user could meet one of them. Fix the line, or add it to "
        "ALLOWED with the reason it is permanently correct — never widen "
        "ALLOWED to a whole file.\n  " + "\n  ".join(survivors)
    )
