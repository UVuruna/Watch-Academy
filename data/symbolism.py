"""Symbolism repository — blurbs and articles from Database/symbolism.json.

The narrative canon lives in SYMBOLISM.md; this repository serves the
per-body blurb texts (short hover lines) and the encyclopedic ARTICLES
— per (article set, body) with a base text and one variant paragraph
per pointer/palette combination — plus the per-sign zodiac articles.
"""

from pathlib import Path

from config import paths
from data._io import load_json_checked


class SymbolismRepository:
    def __init__(self, path: Path | None = None):
        self._path = path or (paths.database_dir() / "symbolism.json")
        self._data: dict | None = None
        self._by_body: dict[str, dict] | None = None

    def _load(self) -> dict:
        if self._data is None:
            self._data = load_json_checked(self._path, "Symbolism database")
        return self._data

    def arm_blurbs(self, body: str) -> dict:
        """Blurb texts of one weekday body (center included)."""
        if self._by_body is None:
            data = self._load()
            self._by_body = {arm["body"]: arm["blurbs"] for arm in data["arms"]}
            self._by_body[data["center"]["body"]] = data["center"]["blurbs"]
        return self._by_body[body]

    def article(self, article_set: str, body: str) -> dict:
        """{base, variants[, name]} of one entity — article_set is a
        WEEKDAY_THEME_ARTICLES value (planets/greek/norse/religion/
        religion_alt/profession)."""
        return self._load()["articles"][article_set][body]

    def zodiac_article(self, sign: str) -> dict:
        """{base, variants{paint, light}} of one tropical sign."""
        return self._load()["zodiac_articles"][sign]

    def trio_article(self, virtue: str) -> dict:
        """{base} of one Trinity arm virtue (Faith / Hope / Love)."""
        return self._load()["trio_articles"][virtue]

    def chinese_article(self, animal: str) -> dict:
        """{base} of one Chinese zodiac animal ("Horse")."""
        return self._load()["chinese_articles"][animal]
