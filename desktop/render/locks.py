"""One lock per key, grown on demand — the whole of this module.

Two independent derived-asset families need the same guarantee: the same
key must never be generated twice at once, and two different keys must
never wait for each other. `render/asset_recolor.py` (metal variants) and
`render/asset_variants.py` (working-set downscales) each wrote their own
table, their own guard and their own six-line accessor for it; the OOP
audit of 2026-08-18 listed the pair as clone C2. It is one kind, so it is
one class.

Layer: render (no Qt, no wall clock, no settings). Documentation: locks.md.
"""

from __future__ import annotations

import threading


class KeyedLocks:
    """A lazily grown table of `threading.Lock`, one per key.

    `locks = KeyedLocks()` then `with locks("some-key"):`. The table's
    own guard is held only while the per-key lock is looked up or
    created, never while the caller holds it — so slow work under one
    key never blocks the creation of another."""

    def __init__(self) -> None:
        self._guard = threading.Lock()
        self._locks: dict[str, threading.Lock] = {}

    def __call__(self, key: str) -> threading.Lock:
        with self._guard:
            lock = self._locks.get(key)
            if lock is None:
                lock = self._locks[key] = threading.Lock()
            return lock
