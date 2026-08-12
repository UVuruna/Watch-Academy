"""THE SHIPPED PRE-BAKE of the letter finishes — see
[Letter Bake](__about/letter_bake.md).

Owner order 2026-08-12: the whole plate library must be rendered into
every standard metal and every thematic colour AT SETUP, into a folder
the program READS, never one it recomputes on every launch — by now the
program uses those letters constantly, and uses all of them. There is
no installer on this machine yet, so `setup/make_letter_bake.py`
performs the bake and the result is committed.

THE KEY CANNOT DRIFT: a baked file is named by
`asset_recolor.letter_cache_name`, the same and only function that
names the runtime cache entry. The name therefore carries the master's
content fingerprint, the metal, the shade and `METAL_SWAP_VERSION` — so
a re-drawn plate or a bumped recolor version makes the bake simply stop
matching, and the finish is derived live exactly as before it existed.
No manifest, nothing to keep in sync, and no way to paint a stale
letter onto the dial.

Deliberately tiny and Qt-free: it answers one question, on the path
resolution hot path, with a dict.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from config import paths

_names: frozenset[str] | None = None
_lock = threading.Lock()


def bake_dir() -> Path:
    """`assets/_baked/letters/` — under `assets/` because it SHIPS (an
    installed program cannot write to its own program folder and must
    not need to), under a leading underscore because it is DERIVED, not
    art, the same convention `assets/_state/` already uses."""
    return paths.assets_dir() / "_baked" / "letters"


def refresh() -> None:
    """Drop the listing so the next lookup re-reads the folder — the
    baker (which creates files while the module may already have
    listed an empty folder) and tests."""
    global _names
    with _lock:
        _names = None


def _listing() -> frozenset[str]:
    """The folder's names, listed ONCE per process. A single directory
    read of ~1,300 entries, against one `Path.exists()` per glyph per
    paint forever — `config.paths` measured that same per-draw stat
    habit at ~30 filesystem calls a second, per watch, which is why its
    own resolution cache exists."""
    global _names
    with _lock:
        if _names is not None:
            return _names
        try:
            _names = frozenset(os.listdir(bake_dir()))
        except OSError:
            # No bake shipped, or an unreadable folder: the program
            # derives every finish live, exactly as it did before the
            # bake existed (Rule #1 — slower, never wrong).
            _names = frozenset()
        return _names


def baked_file(name: str) -> Path | None:
    """The shipped finish for a runtime cache NAME, or None. One dict
    lookup — no stat, no build, no recipe."""
    return bake_dir() / name if name in _listing() else None


def baked_count() -> int:
    """How many finishes shipped — the baker's report and the tooth."""
    return len(_listing())
