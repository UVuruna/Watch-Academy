"""THE ONE COPY RULE's mechanism, written once.

The project law (`CLAUDE.md`): every bundled book and database is loaded
ONCE per process and reached through its `shared_*` accessor; app code
never constructs a repository class. The law was kept — and its four-line
mechanism was retyped eight times, once per repository:

    _SHARED = None
    def shared_x():
        global _SHARED
        if _SHARED is None:
            _SHARED = XRepository()
        return _SHARED

with two variations that made the copies just different enough to keep
copying: the Encyclopedia and the Symbolism book hold one copy PER
LANGUAGE, and the Deep Time pack may legitimately resolve to None, which
forced a second `_DETECTED` flag beside the cell so "absent" would not
be re-detected forever (the OOP audit of 2026-08-18 counted all eight).

`Shared` is that mechanism as an object: a cell, or a cell per key,
filled on first ask and never again. MEMBERSHIP decides, not `is None`,
so None is a perfectly good cached answer and the extra flag is gone.
Each repository keeps its own named accessor — `shared_seasons()`,
`shared_encyclopedia(language)` — because those names ARE the law's
public door and carry their own history in their docstrings.

Layer: data. Pure Python; no Qt, no wall clock, no I/O of its own.
Documentation: __about/_shared.md.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Shared:
    """One process-wide copy of one thing, built on first ask.

    `factory(**kwargs)` builds it. Pass a `key` to `get()` when a
    subject legitimately has more than one copy — the Encyclopedia and
    the Symbolism book keep one per LANGUAGE; everything else leaves the
    key at its default and gets exactly one."""

    def __init__(self, factory: Callable[..., Any]) -> None:
        self._factory = factory
        self._copies: dict[Any, Any] = {}

    def get(self, key: Any = None, **kwargs) -> Any:
        """The copy for `key`, building it on the FIRST ask only —
        which is why `kwargs` are honored on that first call and ignored
        afterwards, the behaviour every one of these accessors already
        documented. A copy that is legitimately None (an uninstalled
        optional pack) is remembered as such and never re-derived."""
        if key not in self._copies:
            self._copies[key] = self._factory(**kwargs)
        return self._copies[key]

    def clear(self) -> None:
        """Drop every copy — the next ask rebuilds. Used when a
        retranslation lands and the cached text is stale."""
        self._copies.clear()
