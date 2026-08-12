"""Rewrite every literal `assets/...` path in the prompt sheets, the
COVERAGE ledger and the sheet-path lint whitelist onto the tree law —
the directory map is derived from the EXECUTED migration commit's own
rename records (`git show -M --name-status`), so the rewrite is exact
by construction, never a guessed regex. One-shot companion of
[Migrate Tree Law](migrate_tree_law.md); kept as the record of how the
text side moved.

Usage: python research/rewrite_look_paths.py <tree-commit-hash>
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def dir_map(commit: str) -> dict[str, str]:
    out = subprocess.run(
        ["git", "show", "-M", "--name-status", "--format=", commit],
        cwd=ROOT, check=True, capture_output=True, text=True,
        encoding="utf-8",
    ).stdout
    mapping: dict[str, str] = {}
    for line in out.splitlines():
        if not line.startswith("R"):
            continue
        _, old, new = line.split("\t")
        old_dir = old.rsplit("/", 1)[0] + "/"
        new_dir = new.rsplit("/", 1)[0] + "/"
        if old_dir != new_dir:
            mapping[old_dir] = new_dir
    return mapping


def main() -> int:
    commit = sys.argv[1]
    mapping = sorted(dir_map(commit).items(), key=lambda kv: -len(kv[0]))
    print(f"{len(mapping)} directory renames from {commit}")
    targets = sorted((ROOT / "research" / "prompts").rglob("*.md"))
    targets.append(ROOT / "tests" / "test_prompt_paths.py")
    total = 0
    for target in targets:
        text = target.read_text(encoding="utf-8")
        original = text
        for old_dir, new_dir in mapping:
            text = text.replace(old_dir, new_dir)
            # Whitelist entries are assets-relative (no "assets/").
            if old_dir.startswith("assets/"):
                text = text.replace(
                    f'"{old_dir[len("assets/"):]}', f'"{new_dir[len("assets/"):]}'
                )
        if text != original:
            target.write_text(text, encoding="utf-8")
            changed = sum(
                1 for a, b in zip(original.splitlines(), text.splitlines())
                if a != b
            )
            total += changed
            print(f"rewrote {target.relative_to(ROOT)} (~{changed} lines)")
    print(f"done — ~{total} lines rewritten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
