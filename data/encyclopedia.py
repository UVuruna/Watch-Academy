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

    def _section(self, section: str, key: str) -> dict:
        """{title, base} of one entry in a top-level encyclopedia
        section — the ONE localized lookup shared by every topic
        (Rule #5)."""
        return self._localized(
            f"encyclopedia/{section}/{key}", self._load()[section][key]
        )

    def instrument(self, key: str) -> dict:
        """{title, base} of one functionality article ("dial",
        "twilight", "year_wheel"...)."""
        return self._section("instrument", key)

    def week(self, body: str) -> dict:
        """{title, base} of one WEEK day page (body = sun..saturn)."""
        return self._section("week", body)

    def season(self, key: str) -> dict:
        """{title, base} of one SEASONS article ("Spring", "Wet_Season",
        "Meteorological"...) — owner 2026-07-13; the turning points moved
        to the SUN topic in the 2026-07-16 three-way split."""
        return self._section("seasons", key)

    def sun(self, key: str) -> dict:
        """{title, base} of one SUN article — the equinoxes and
        solstices (owner 2026-07-16, ROADMAP queue #10 split)."""
        return self._section("sun", key)

    def moon(self, key: str) -> dict:
        """{title, base} of one MOON article — the lunations (owner
        2026-07-16, ROADMAP queue #10 split)."""
        return self._section("moon", key)

    def era(self, key: str) -> dict:
        """{title, base} of one ERA article — the Age of Light/Darkness,
        the four Starry Seasons, the comparative Eras of the World
        (ROADMAP 15a3, owner 2026-07-17) and The Great Oscillations (the
        season-length / Milankovitch essay near the Observatory, fix
        round F, owner 2026-07-19)."""
        return self._section("era", key)

    def eclipse(self, key: str) -> dict:
        """{title, base} of one ECLIPSE chapter — the seven categories
        (solar total/annular/partial/hybrid, lunar total/partial/
        penumbral) plus the two per-body overviews (fix round F, owner
        order 2026-07-19: "posebno za mesec i sunce")."""
        return self._section("eclipse", key)

    def theme_title(self, theme: str) -> dict:
        """{title, base} of a weekday theme's OWN opening page (owner
        spec, round R3 restructure: "Sve teme imaju minimum 1 ARTICLE
        TITLE" — every weekday-structured theme's whole-theme overview,
        page ONE)."""
        return self._section("theme_title", theme)

    def week_duality(self, theme: str) -> dict:
        """{title, base} of a weekday theme's WEEK-DUALITY title page
        (owner spec, round R3 restructure: the page introducing Sunday
        as the theme's own dual center, right before the merged Ruler|
        Servant article)."""
        return self._section("week_duality", theme)

    def entry(self, family: str, name: str) -> dict:
        """{base} of one emblem-family article — family is "virtues" |
        "sins" | "moods" | "duality" (the Judas–Lucifer scale, owner
        2026-07-13) | "ninths" | "intelligence" | "wider" (the seatless
        A-list pantheon figures, WORKPLAN Session 8) | "months" (the
        Slavic-months Calendar-pointer set, owner-sealed R7b 2026-07-21),
        name the entry ("Justice", "Lucifer", "Hestia", "Lipanj")."""
        return self._localized(
            f"encyclopedia/{family}/{name}", self._load()[family][name]
        )
