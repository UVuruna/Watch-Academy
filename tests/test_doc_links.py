"""THE DOCS LAW's second guard — the navigation chain.

Root `rules/DOCS.md` -> Navigation Chain: "From the project `README.md`
you must be able to reach EVERY `.md` file by following links". A doc
nobody can reach is a doc nobody reads; a link that 404s is a doc that
lies about where its neighbours live.

Two assertions:

1. **No broken relative link.** Every relative link target inside a
   project `.md` must exist on disk (any extension -- `.md` docs, the
   "(script)" links to `.py`, data files). Absolute URLs, mailto: and
   pure `#anchor` links are ignored; a `#fragment` on a relative target
   is stripped before the existence check (anchors are not verified --
   GitHub/VSCode generate them differently, which is why the convention
   demands explicit `<a id="...">` tags).
2. **No orphan doc.** Breadth-first from `README.md` over `.md` -> `.md`
   links, every project `.md` must be reached.

Excluded from BOTH checks: directories that are not project
documentation (build output, virtualenvs, caches, the owner's private
`UV/` inbox, agent tooling under `.claude/`).
"""

import re
from collections import deque
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
README = PROJECT_ROOT / "README.md"

# Not project documentation -- never scanned, never required to be reachable.
EXCLUDED_DIR_NAMES = {
    ".git",
    ".claude",          # agent tooling (skills), not project docs
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "build",
    "dist",
    "UV",               # the owner's gitignored inbox (Rule #18)
}

# Markdown inline links: [text](target). Reference-style links and bare
# autolinks are not used by this project's convention.
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def _is_external(target: str) -> bool:
    return (
        target.startswith("#")
        or "://" in target
        or target.startswith("mailto:")
        or target.startswith("www.")
    )


def _doc_files() -> list[Path]:
    return sorted(
        path
        for path in PROJECT_ROOT.rglob("*.md")
        if not any(part in EXCLUDED_DIR_NAMES for part in path.parts)
    )


def _links_of(doc: Path) -> list[str]:
    return _LINK.findall(doc.read_text(encoding="utf-8", errors="replace"))


def _resolve(doc: Path, target: str) -> Path:
    """Absolute path a relative link from `doc` points at (fragment and
    percent-encoded spaces removed)."""
    clean = target.split("#", 1)[0].replace("%20", " ")
    return (doc.parent / clean).resolve()


def test_no_broken_relative_links():
    """Every relative link target in every project doc exists on disk."""
    broken = []
    for doc in _doc_files():
        rel_doc = doc.relative_to(PROJECT_ROOT).as_posix()
        for target in _links_of(doc):
            if _is_external(target):
                continue
            if not target.split("#", 1)[0]:      # pure "#anchor"
                continue
            resolved = _resolve(doc, target)
            # A link INTO an excluded tree is not verifiable and never
            # will be: `UV/` is the owner's gitignored inbox (Rule #18),
            # so a prompt sheet citing a reference image he dropped there
            # resolves on his machine and on no clone. We refuse to scan
            # those trees; we equally refuse to assert on links into them.
            if any(part in EXCLUDED_DIR_NAMES for part in resolved.parts):
                continue
            if not resolved.exists():
                broken.append(f"{rel_doc} -> {target}")
    assert not broken, (
        "THE DOCS LAW (rules/DOCS.md -> Navigation Chain): these relative "
        "links point at files that do not exist:\n  " + "\n  ".join(broken)
    )


def test_every_doc_is_reachable_from_the_readme():
    """Breadth-first from README.md over .md links -- no orphan docs."""
    assert README.exists(), "the project has no README.md to start the chain from"

    reached = {README.resolve()}
    queue = deque([README])
    while queue:
        doc = queue.popleft()
        for target in _links_of(doc):
            if _is_external(target) or not target.split("#", 1)[0]:
                continue
            resolved = _resolve(doc, target)
            if resolved.suffix.lower() != ".md" or resolved in reached:
                continue
            if not resolved.exists():
                continue                          # the other test reports it
            reached.add(resolved)
            queue.append(resolved)

    orphans = sorted(
        doc.relative_to(PROJECT_ROOT).as_posix()
        for doc in _doc_files()
        if doc.resolve() not in reached
    )
    assert not orphans, (
        "THE DOCS LAW (rules/DOCS.md -> Navigation Chain): these docs "
        "cannot be reached from README.md by following links -- link them "
        "from their folder doc (or delete them if they are dead):\n  "
        + "\n  ".join(orphans)
    )
