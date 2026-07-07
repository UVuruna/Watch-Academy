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
