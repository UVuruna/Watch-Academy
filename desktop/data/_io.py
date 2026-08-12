"""Shared JSON loading — a plain function, not a base class (two small
repositories do not justify a hierarchy)."""

import json
from pathlib import Path


def load_json_checked(path: Path, description: str) -> dict:
    """Load a bundled JSON database, failing loudly with context."""
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"{description} is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{description} is not valid JSON: {path} ({exc})") from exc


def year_bounds(data: dict) -> tuple[int, int]:
    """The inclusive (first, last) integer year keys of a bundled
    database — the coverage read straight from the data (Rule #4: never
    hardcoded), so a future Deep Time pack simply widens the file and
    every consumer follows. Non-year keys are ignored; negative years
    (deep past) are supported."""
    years = [int(key) for key in data if key.lstrip("-").isdigit()]
    return min(years), max(years)
