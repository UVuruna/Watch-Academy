"""The @timed statistics store (owner 2026-07-15) and the Report's
readable units — cumulative aggregates, session recents, atomic
persistence, and the ns → µs → ms → s formatting spec."""

import json

from app.report import format_ns
from config import profiling


def test_timed_records_and_persists(tmp_path, monkeypatch):
    monkeypatch.setattr(
        profiling, "_store_path", lambda: tmp_path / "profiling.json"
    )
    monkeypatch.setattr(profiling, "_stats", {})
    monkeypatch.setattr(profiling, "_recent", {})
    monkeypatch.setattr(profiling, "_loaded", True)
    monkeypatch.setattr(profiling, "_dirty", False)

    @profiling.timed("Golden")
    def work():
        return 7

    assert work() == 7
    with profiling.measure("Golden"):
        pass
    entry = profiling.snapshot()["Golden"]
    assert entry["count"] == 2
    assert entry["total_ns"] >= entry["max_ns"] >= entry["min_ns"] > 0
    assert entry["last_ns"] in range(
        entry["min_ns"], entry["max_ns"] + 1
    )
    assert len(entry["recent"]) == 2
    profiling.flush()
    saved = json.loads(
        (tmp_path / "profiling.json").read_text(encoding="utf-8")
    )
    assert saved["Golden"]["count"] == 2
    assert "recent" not in saved["Golden"]   # session-only, never stored
    # Reset empties the lifetime store on disk too.
    profiling.reset()
    assert profiling.snapshot() == {}
    assert json.loads(
        (tmp_path / "profiling.json").read_text(encoding="utf-8")
    ) == {}


def test_format_ns_readable_units():
    """The owner's unit spec: whatever the function's speed, the
    number reads — ns whole, µs/ms at two decimals, s at three."""
    assert format_ns(720) == "720 ns"
    assert format_ns(15_300) == "15.30 µs"
    assert format_ns(2_450_000) == "2.45 ms"
    assert format_ns(3_200_000_000) == "3.200 s"
