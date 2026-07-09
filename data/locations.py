"""World locations repository — lazy over the 4 MB world_locations.json.

The hierarchy is Continent -> Subregion -> Country -> [Admin ->] City with
MIXED depth: 121 of the 241 countries contain both direct city leaves and
admin sub-dicts in the same children mapping. Every child is therefore
classified by shape ("latitude" in value = city leaf), never by depth.
The nine chaotic countries (UK's 186 counties etc.) were re-nested under
small standard macro-region sets in the 2026-07 curation.

The file is loaded only while the location picker needs it and released
afterwards; the chosen CityRecord is the only thing the rest of the app
ever sees.
"""

import unicodedata
from dataclasses import dataclass
from pathlib import Path

from config import constants, paths
from data._io import load_json_checked


@dataclass(frozen=True)
class CityRecord:
    path: tuple[str, ...]           # (continent, subregion, country[, admin], city)
    name: str
    latitude: float
    longitude: float
    timezone: str                   # IANA name


@dataclass(frozen=True)
class LocationNode:
    """One child at some level of the tree: either a navigable group
    (continent/subregion/country/admin) or a selectable city."""

    name: str
    record: CityRecord | None       # set only for city leaves

    @property
    def is_city(self) -> bool:
        return self.record is not None


def _is_city_leaf(value: dict) -> bool:
    return "latitude" in value


def fold_name(text: str) -> str:
    """Search folding: the bundled city names are ASCII transliterations,
    so native spellings must match them — NFKD strips combining diacritics
    (š, č, ü, ...), the transliteration table covers the single-codepoint
    letters NFKD cannot decompose (ø, đ, ł, ...)."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    lowered = stripped.casefold()
    return "".join(
        constants.CITY_NAME_TRANSLITERATIONS.get(ch, ch) for ch in lowered
    )


class LocationRepository:
    def __init__(self, path: Path | None = None):
        self._path = path or (paths.database_dir() / "world_locations.json")
        self._tree: dict | None = None

    def load(self) -> None:
        if self._tree is None:
            self._tree = load_json_checked(self._path, "World locations database")

    def release(self) -> None:
        """Drop the parsed tree (call when the picker closes)."""
        self._tree = None

    def children(self, node_path: tuple[str, ...] = ()) -> list[LocationNode]:
        """Children of the node at `node_path` (empty tuple = continents).

        Raises KeyError with the full path when a segment does not exist.
        """
        self.load()
        node = self._tree
        for depth, segment in enumerate(node_path):
            try:
                node = node[segment]
            except KeyError:
                raise KeyError(
                    f"unknown location path segment {segment!r} "
                    f"at depth {depth} of {node_path!r}"
                ) from None
        return [
            LocationNode(
                name=name,
                record=(
                    self._make_record(node_path + (name,), value)
                    if _is_city_leaf(value)
                    else None
                ),
            )
            for name, value in node.items()
        ]

    def all_cities(self) -> list[tuple[str, str, tuple[str, ...]]]:
        """(folded name, display name, path) of EVERY city — one full
        walk, used by the picker's live search filter."""
        self.load()
        cities: list[tuple[str, str, tuple[str, ...]]] = []
        stack: list[tuple[tuple[str, ...], dict]] = [((), self._tree)]
        while stack:
            node_path, node = stack.pop()
            for child_name, value in node.items():
                child_path = node_path + (child_name,)
                if _is_city_leaf(value):
                    cities.append((fold_name(child_name), child_name, child_path))
                else:
                    stack.append((child_path, value))
        return cities

    def find_city(self, name: str) -> list[CityRecord]:
        """All cities whose folded name matches (full walk — picker search
        box and the core CLI selftest). Diacritic spellings match their
        ASCII transliterations: "Niš" finds "Nis", "Tromsø" finds "Tromso".
        """
        self.load()
        wanted = fold_name(name)
        matches: list[CityRecord] = []
        stack: list[tuple[tuple[str, ...], dict]] = [((), self._tree)]
        while stack:
            node_path, node = stack.pop()
            for child_name, value in node.items():
                child_path = node_path + (child_name,)
                if _is_city_leaf(value):
                    if fold_name(child_name) == wanted:
                        matches.append(self._make_record(child_path, value))
                else:
                    stack.append((child_path, value))
        return matches

    @staticmethod
    def _make_record(node_path: tuple[str, ...], leaf: dict) -> CityRecord:
        return CityRecord(
            path=node_path,
            name=node_path[-1],
            latitude=float(leaf["latitude"]),
            longitude=float(leaf["longitude"]),
            timezone=leaf["timezone"],
        )
