"""Execution-time statistics for the key functionalities (owner
2026-07-15): @timed / measure() record perf_counter_ns durations into
a cumulative install-lifetime store — the hidden Report reads it.

Bottom-layer module (config) so data/render/app can all instrument
themselves; core stays pure and is never decorated. Recording is
lock-guarded and only marks the store dirty — the controller flushes
once per minute and at quit.
"""

import functools
import json
import os
import threading
import time
from collections import deque
from contextlib import contextmanager

from config import paths

RECENT_KEEP = 120                    # session-only sparkline window

_lock = threading.Lock()
_stats: dict[str, dict] = {}         # name -> aggregate dict (ns ints)
_recent: dict[str, deque] = {}       # name -> recent durations (session)
_dirty = False
_loaded = False


def _store_path():
    return paths.settings_path().parent / "profiling.json"


def _ensure_loaded() -> None:
    """Lazy first read — called under the lock."""
    global _loaded
    if _loaded:
        return
    _loaded = True
    path = _store_path()
    if not path.exists():
        return
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        # A corrupt stats file must not take the clock down — start
        # fresh but say so (Rule #1).
        print(f"profiling store unreadable, starting fresh: {error}")
        return
    for name, entry in raw.items():
        _stats[name] = {
            "count": int(entry["count"]),
            "total_ns": int(entry["total_ns"]),
            "min_ns": int(entry["min_ns"]),
            "max_ns": int(entry["max_ns"]),
            "last_ns": int(entry["last_ns"]),
        }


def _record(name: str, elapsed_ns: int) -> None:
    global _dirty
    with _lock:
        _ensure_loaded()
        entry = _stats.get(name)
        if entry is None:
            entry = _stats[name] = {
                "count": 0, "total_ns": 0,
                "min_ns": elapsed_ns, "max_ns": elapsed_ns,
                "last_ns": elapsed_ns,
            }
        entry["count"] += 1
        entry["total_ns"] += elapsed_ns
        entry["min_ns"] = min(entry["min_ns"], elapsed_ns)
        entry["max_ns"] = max(entry["max_ns"], elapsed_ns)
        entry["last_ns"] = elapsed_ns
        _recent.setdefault(name, deque(maxlen=RECENT_KEEP)).append(
            elapsed_ns
        )
        _dirty = True


def timed(name: str):
    """Decorator: every call of the wrapped function is measured under
    `name` — exceptions still count (the time was spent)."""
    def decorate(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            start = time.perf_counter_ns()
            try:
                return function(*args, **kwargs)
            finally:
                _record(name, time.perf_counter_ns() - start)
        return wrapper
    return decorate


@contextmanager
def measure(name: str):
    """Inline block measurement — for spots a decorator cannot sit
    (e.g. the day-context rebuild branch inside the tick)."""
    start = time.perf_counter_ns()
    try:
        yield
    finally:
        _record(name, time.perf_counter_ns() - start)


def snapshot() -> dict[str, dict]:
    """A display copy: aggregates + the session's recent durations."""
    with _lock:
        _ensure_loaded()
        return {
            name: {**entry, "recent": list(_recent.get(name, ()))}
            for name, entry in _stats.items()
        }


def flush() -> None:
    """Atomic save when dirty — called by the controller once per
    minute and at quit; a failure prints and retries next flush."""
    global _dirty
    with _lock:
        if not _dirty:
            return
        payload = json.dumps(_stats, ensure_ascii=False, indent=1)
        _dirty = False
    path = _store_path()
    tmp = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, path)
    except OSError as error:
        print(f"profiling store save failed: {error}")
        with _lock:
            _dirty = True


def reset() -> None:
    """Clear the lifetime store (the Report's Reset button)."""
    global _dirty
    with _lock:
        _ensure_loaded()
        _stats.clear()
        _recent.clear()
        _dirty = True
    flush()
