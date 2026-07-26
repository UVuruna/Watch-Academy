"""One-shot PascalCase stem unification (tree law rule 5's case half,
owner-approved 2026-07-26): every figure stem in the three figure
categories reads as a NAME — `anubis` -> `Anubis`, `afu_ra` -> `Afu_Ra`,
`big_bang` -> `Big_Bang` — while `_vN` version and `_gem`/`_gpt` source
suffixes ride along verbatim and tokens that already carry a capital
(`Yggdrasil`, `KaliYuga`) stay exactly as drawn. Case-only renames go
through a two-step `git mv` (Windows' case-insensitive filesystem
swallows a direct one). Dry-run by default; `--execute` moves.
Companion of [Migrate Tree Law](migrate_tree_law.md) — same contract:
explicit plan, collision abort, before/after counts, text rewrites
derive from the executed commit's own rename records afterwards.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
AREAS = ("weeks", "calendars", "archetypes")
_SOURCES = {"gem", "gpt"}
_VERSION = re.compile(r"v\d+$")


def pascal_name(filename: str) -> str:
    stem, dot, ext = filename.rpartition(".")
    tokens = stem.split("_")
    tail: list[str] = []
    if tokens and tokens[-1] in _SOURCES:
        tail.insert(0, tokens.pop())
    if tokens and _VERSION.fullmatch(tokens[-1]):
        tail.insert(0, tokens.pop())
    figure = [
        t if any(c.isupper() for c in t) else (t[:1].upper() + t[1:])
        for t in tokens
    ]
    return "_".join(figure + tail) + dot + ext


def plan() -> list[tuple[Path, Path]]:
    moves = []
    for area in AREAS:
        for file in sorted((ASSETS / area).rglob("*.png")):
            new = pascal_name(file.name)
            if new != file.name:
                moves.append((file, file.parent / new))
    return moves


def main() -> int:
    execute = "--execute" in sys.argv
    moves = plan()
    before = sum(
        1 for a in AREAS for _ in (ASSETS / a).rglob("*.png")
    )
    # Collisions: two sources mapping onto one target, or a target that
    # already exists as a DIFFERENT file (not the case-only self).
    targets: dict[str, Path] = {}
    collisions = []
    for src, dst in moves:
        key = str(dst).lower()
        if key in targets:
            collisions.append((src, dst))
        elif dst.exists() and str(src).lower() != key:
            collisions.append((src, dst))
        targets[key] = src
    print(f"planned renames: {len(moves)}   files before: {before}")
    for src, dst in collisions:
        print(f"COLLISION: {src.relative_to(ASSETS)} -> {dst.name}")
    if collisions:
        print("ABORT: resolve collisions by hand first (law: zero loss).")
        return 1
    if not execute:
        for src, dst in moves:
            print(f"PLAN {src.relative_to(ASSETS)}  ->  {dst.name}")
        print("dry run — nothing touched; rerun with --execute")
        return 0
    for index, (src, dst) in enumerate(moves):
        if str(src).lower() == str(dst).lower():
            # Case-only: two-step through a temp name.
            tmp = src.with_name(src.name + ".__case__")
            subprocess.run(["git", "mv", str(src), str(tmp)], cwd=ROOT,
                           check=True, capture_output=True)
            subprocess.run(["git", "mv", str(tmp), str(dst)], cwd=ROOT,
                           check=True, capture_output=True)
        else:
            subprocess.run(["git", "mv", str(src), str(dst)], cwd=ROOT,
                           check=True, capture_output=True)
        if (index + 1) % 100 == 0:
            print(f"renamed {index + 1}/{len(moves)}")
    after = sum(1 for a in AREAS for _ in (ASSETS / a).rglob("*.png"))
    print(f"files after: {after} (before {before})")
    if after != before:
        print("COUNT MISMATCH — investigate before committing!")
        return 1
    print("execute complete — counts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
