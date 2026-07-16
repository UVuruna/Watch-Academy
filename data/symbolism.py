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
    def __init__(self, path: Path | None = None, overlay: dict | None = None):
        """`overlay` = the active language's translated texts (key →
        text, from the TranslationStore) laid over the English
        originals; entries not yet translated fall back to English."""
        self._path = path or (paths.database_dir() / "symbolism.json")
        self._overlay = overlay or {}
        self._data: dict | None = None
        self._by_body: dict[str, dict] | None = None

    def _localized(self, prefix: str, node: dict) -> dict:
        if not self._overlay:
            return node
        out = dict(node)
        out["base"] = self._overlay.get(f"{prefix}/base", node["base"])
        if "variants" in node:
            out["variants"] = {
                combo: self._overlay.get(f"{prefix}/variants/{combo}", text)
                for combo, text in node["variants"].items()
            }
        if "faces" in node:
            # The dual Sunday's Ruler/Servant face texts (owner
            # 2026-07-13) ride the same overlay path.
            out["faces"] = {
                face: self._overlay.get(f"{prefix}/faces/{face}", text)
                for face, text in node["faces"].items()
            }
        return out

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
        """{base, variants[, faces]} of one entity — article_set is a
        WEEKDAY_THEME_ARTICLES value (planets/greek/norse/religion/
        …/greek_pantheon/…). A `$ref` entry (a PANTHEON reseat — the
        same figure serving a new seat) resolves to its SOURCE
        entity's article, localized under the SOURCE keys so the text
        translates exactly once; the reseat's OWN faces (the pantheon
        Sunday duals) override and localize under the reseat's keys."""
        node = self._load()["articles"][article_set][body]
        prefix = f"articles/{article_set}/{body}"
        if "$ref" in node:
            ref_set, ref_body = node["$ref"]
            merged = dict(self.article(ref_set, ref_body))
            merged.pop("faces", None)
            if "variants" in node:
                # A CROSS-SEAT reseat: the source's variants describe
                # its old positions, so the reseat carries its own —
                # localized under the reseat's keys.
                merged["variants"] = {
                    combo: self._overlay.get(
                        f"{prefix}/variants/{combo}", text
                    )
                    for combo, text in node["variants"].items()
                }
            if "faces" in node:
                merged["faces"] = {
                    face: self._overlay.get(f"{prefix}/faces/{face}", text)
                    for face, text in node["faces"].items()
                }
            return merged
        return self._localized(prefix, node)

    def archetype_article(self, article_set: str, entity: str) -> dict | None:
        """The TWO-ROW archetype article (owner sealed package
        2026-07-16): `articles.<article_set>.<entity>` with
        `{"rows": [row1, row2]}` — the set names live in
        config/archetypes.py (archetype_trinity_paint …), the entity
        keys per figure plus "center". Session 6 writes the texts;
        until a set/entity exists this returns None and the hover
        shows the figure's name with the pending line — the DOCUMENTED
        graceful path (never a KeyError inside a hover)."""
        node = self._load()["articles"].get(article_set, {}).get(entity)
        if node is None:
            return None
        if not self._overlay or "rows" not in node:
            return node
        prefix = f"articles/{article_set}/{entity}"
        out = dict(node)
        out["rows"] = [
            self._overlay.get(f"{prefix}/rows/{i}", text)
            for i, text in enumerate(node["rows"])
        ]
        return out

    def zodiac_article(self, sign: str) -> dict:
        """{base, variants{paint, light}} of one tropical sign."""
        return self._localized(
            f"zodiac_articles/{sign}", self._load()["zodiac_articles"][sign]
        )

    def trio_article(self, virtue: str) -> dict:
        """{base} of one Trinity arm virtue (Faith / Hope / Love)."""
        return self._localized(
            f"trio_articles/{virtue}", self._load()["trio_articles"][virtue]
        )

    def chinese_article(self, animal: str) -> dict:
        """{base} of one Chinese zodiac animal ("Horse")."""
        return self._localized(
            f"chinese_articles/{animal}",
            self._load()["chinese_articles"][animal],
        )

    def chinese_element(self, element: str) -> dict:
        """{base} of one Wu Xing element ("Fire")."""
        return self._localized(
            f"chinese_elements/{element}",
            self._load()["chinese_elements"][element],
        )
