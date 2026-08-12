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

# THE THREE-FOLDER MIGRATION (2026-08-12): this guard now lives at
# desktop/tests/, but the navigation chain starts at README.md, which
# stays at the TRUE repo root — one level further up than the desktop
# Python root the other guards anchor on.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
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
# CODE IS NOT A LINK (fixed 2026-08-05). A Python sample inside a fenced
# block — `setters["hands"](name)` — matches _LINK exactly: bracketed
# text followed by a parenthesised token. The guard read eleven such
# samples in `app/watch_face/__flow/` as links to files named `name`,
# `value`, `shape`, and failed the build on documentation that was
# correct. Fenced blocks and inline code spans are stripped before the
# link scan: NO real link is exempted by this — a link inside a code
# fence was never a link — while every doc that shows a call with a
# subscript stops being a false alarm.
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_FENCE_MARKS = ("```", "~~~")


def _prose(text: str) -> str:
    """`text` with code removed — fenced blocks, INDENTED blocks (the
    four-space form, which is what `__flow` pseudocode uses) and inline
    spans. What is left is what a reader, and therefore a link, lives
    in.

    The indented form is only recognised where Markdown itself
    recognises it: a run of >=4-space lines opening after a BLANK line
    and never under a list item (a wrapped list line is indented too,
    and may легitimately carry a link)."""
    kept, fence, indented = [], None, False
    blank_before, in_list = True, False
    for line in text.splitlines():
        stripped = line.lstrip()
        if fence is None:
            mark = next((m for m in _FENCE_MARKS if stripped.startswith(m)), None)
            if mark is not None:
                fence = mark
                blank_before = False
                continue
        elif stripped.startswith(fence):
            fence = None
            continue
        if fence is not None:
            continue

        blank = not stripped
        indent = len(line) - len(stripped)
        if indented:
            # an indented block runs until a non-blank line comes back out
            if blank or indent >= 4:
                blank_before = blank
                continue
            indented = False
        elif blank_before and not in_list and indent >= 4 and not blank:
            indented = True
            blank_before = False
            continue

        if not blank:
            in_list = (indent < 4 and
                       (stripped[:2] in ("- ", "* ", "+ ", "| ")
                        or (stripped[:1].isdigit() and ". " in stripped[:4])))
        blank_before = blank
        kept.append(line)
    return _INLINE_CODE.sub("", "\n".join(kept))


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
    return _LINK.findall(
        _prose(doc.read_text(encoding="utf-8", errors="replace"))
    )


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


def test_code_samples_are_not_read_as_links(tmp_path):
    """A call with a subscript inside a code fence is CODE, not a link.

    The exact shape that failed the build on 2026-08-05:
    `setters["hands"](name)` reads as [hands](name) to the link regex.
    Fenced blocks and inline spans are stripped first, so the sample is
    invisible to the scan while a real link one line below it is not.
    """
    doc = tmp_path / "sample.md"
    doc.write_text(
        "A real link to [the canon](CANON.md).\n"
        "\n"
        "```python\n"
        '    setters["hands"](name)\n'
        '    setters["diameter"](slider.value() / 100)\n'
        "```\n"
        "\n"
        'Inline too: `setters["ring"](name)` stays out of the scan.\n',
        encoding="utf-8",
    )
    assert _links_of(doc) == ["CANON.md"]
