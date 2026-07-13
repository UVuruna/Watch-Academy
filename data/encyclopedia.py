"""Encyclopedia repository — the Encyclopedia's OWN content from
Database/encyclopedia.json (owner expansion 2026-07-13): the
INSTRUMENT functionality articles, the WEEK day pages and the
VIRTUES/SINS/MOODS emblem entries. Localized through the same overlay
mechanism as the dial articles (encyclopedia/<section>/<key>/... keys).
"""

from config import paths
from data._io import load_json_checked


class EncyclopediaRepository:
    def __init__(self, overlay: dict | None = None):
        self._path = paths.database_dir() / "encyclopedia.json"
        self._overlay = overlay or {}
        self._data: dict | None = None

    def _load(self) -> dict:
        if self._data is None:
            self._data = load_json_checked(
                self._path, "Encyclopedia database"
            )
        return self._data

    def _localized(self, prefix: str, node: dict) -> dict:
        if not self._overlay:
            return node
        out = dict(node)
        for field in ("title", "base"):
            if field in node:
                out[field] = self._overlay.get(
                    f"{prefix}/{field}", node[field]
                )
        return out

    def instrument(self, key: str) -> dict:
        """{title, base} of one functionality article ("dial",
        "twilight", "year_wheel"...)."""
        return self._localized(
            f"encyclopedia/instrument/{key}",
            self._load()["instrument"][key],
        )

    def week(self, body: str) -> dict:
        """{title, base} of one WEEK day page (body = sun..saturn)."""
        return self._localized(
            f"encyclopedia/week/{body}", self._load()["week"][body]
        )

    def entry(self, family: str, name: str) -> dict:
        """{base} of one virtue/sin/mood emblem article — family is
        "virtues" | "sins" | "moods", name the emblem ("Justice")."""
        return self._localized(
            f"encyclopedia/{family}/{name}", self._load()[family][name]
        )
