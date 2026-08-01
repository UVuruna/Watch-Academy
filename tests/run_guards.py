"""The guard runner — the teeth behind the Claude Code hooks.

Root `rules/CODE.md` -> Enforcement: a rule without a check is a
request. This wrapper runs ONLY the four law guards (never the full app
suite, which takes tens of minutes here), prints failures to stderr and
exits **2** — the exit code that makes a Claude Code hook BLOCKING.

    python tests/run_guards.py            # all four guards  (Stop hook)
    python tests/run_guards.py --fast     # structure + config only (PostToolUse)

`--fast` is what fires after every Edit/Write: the two guards that read
source files and finish in milliseconds, so the agent gets blocking
feedback the moment it saves a file. The full set adds the two docs
guards and runs when the session tries to stop.
"""

import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent

# THE STRUCTURE LAW and THE CONFIG SECTION LAW read source files only —
# milliseconds, safe to fire after every single edit.
FAST_GUARDS = (
    "test_structure_law.py",
    "test_config_sections.py",
)
# THE DOCS LAW walks every .md in the project — still fast, but it only
# needs to hold when the session tries to END.
FULL_GUARDS = FAST_GUARDS + (
    "test_docs_coverage.py",
    "test_doc_links.py",
)


def main(argv: list[str]) -> int:
    fast = "--fast" in argv
    guards = FAST_GUARDS if fast else FULL_GUARDS
    args = [str(TESTS_DIR / name) for name in guards]
    # -p no:cacheprovider keeps the hook from fighting a concurrent test
    # run over .pytest_cache; --no-header -q keeps the hook output short.
    args += ["-q", "--no-header", "-p", "no:cacheprovider"]

    exit_code = pytest.main(args)
    if exit_code != 0:
        label = "FAST" if fast else "FULL"
        print(
            f"\nGUARDS FAILED ({label}) — the laws in the monorepo "
            "constitution are not satisfied. Fix the violation above; do "
            "NOT weaken the guard or add a ratchet entry without the "
            "owner's explicit approval in this same session.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
