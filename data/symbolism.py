"""Symbolism repository — blurbs from Database/symbolism.json.

The narrative canon lives in SYMBOLISM.md; this repository serves the
per-body blurb texts the hexa diamond hover shows for the active
weekday theme (planets/greek/norse/religion/profession).
"""

from pathlib import Path

from config import paths
from data._io import load_json_checked


class SymbolismRepository:
    def __init__(self, path: Path | None = None):
        self._path = path or (paths.database_dir() / "symbolism.json")
        self._by_body: dict[str, dict] | None = None

    def arm_blurbs(self, body: str) -> dict:
        """Blurb texts of one weekday body (center included)."""
        if self._by_body is None:
            data = load_json_checked(self._path, "Symbolism database")
            self._by_body = {arm["body"]: arm["blurbs"] for arm in data["arms"]}
            self._by_body[data["center"]["body"]] = data["center"]["blurbs"]
        return self._by_body[body]
