"""World locations repository — lazy over the 4 MB world_locations.json.

The hierarchy is Continent -> Subregion -> Country -> [Admin ->] City with
MIXED depth: 121 of the 241 countries contain both direct city leaves and
admin sub-dicts in the same children mapping. Every child is therefore
classified by shape ("latitude" in value = city leaf), never by depth.
The nine chaotic countries (UK's 186 counties etc.) were re-nested under
small standard macro-region sets in the 2026-07 curation.

The file is loaded only while the location picker needs it and released
afterwards; the chosen Place is the only thing the rest of the app
ever sees.
"""

import unicodedata
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

from config import constants, defaults, paths
from data._io import load_json_checked
from data._shared import Shared


@dataclass(frozen=True)
class Place:
    """WHERE A WATCH IS — one whole thing, never five loose fields
    (owner decree 2026-08-16, "Beograd u Burundiju").

    A location used to live in `Settings` as `city_name` + `city_path` +
    `latitude` + `longitude` + `timezone`, five independent fields that
    nothing held together. The Settings dialog took the name and the
    coordinates from the stored settings but read the PATH back off its
    own combo boxes, so a dialog opened on a watch that had never picked
    a city (`city_path = ()`, the default of every new watch) saved
    whatever the cascade happened to show — alphabetically first, i.e.
    Africa/Eastern Africa/Burundi/Bubanza — beside the name "Belgrade",
    and the crown then drew CITY from one field and COUNTRY from the
    other: "BELGRADE BURUNDI".

    A test that CATCHES that mismatch would be a smoke detector on a
    house built of petrol. The fix is that the half-location has nowhere
    to be written: name, path and coordinates travel together or not at
    all, they come out of the city database (`_make_record`) or through
    the ONE door for stored/untrusted data (`place_from_mapping`), and
    `path` is either the record's real path or empty — never another
    city's.
    """

    path: tuple[str, ...]           # (continent, subregion, country[, admin], city)
    name: str
    latitude: float
    longitude: float
    timezone: str                   # IANA name

    @property
    def country(self) -> str:
        """The country segment, or "" when this place carries no path (a
        Quick Jump city saved before paths were stored). The crown's
        "CITY, COUNTRY" asks HERE instead of indexing `path[2]` itself,
        so there is one answer to "which country is this" in the app."""
        return self.path[2] if len(self.path) > 2 else ""


@dataclass(frozen=True)
class LocationNode:
    """One child at some level of the tree: either a navigable group
    (continent/subregion/country/admin) or a selectable city."""

    name: str
    record: Place | None            # set only for city leaves

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
        #: How many pickers are currently holding the tree. The file is
        #: 5.6 MB and this repository is process-wide (owner bug
        #: 2026-08-06): two watches with Settings open at once used to
        #: hold two independent parsed trees, and reopening the SAME
        #: dialog reparsed from scratch every time. Releasing on a
        #: plain flag would then let the FIRST picker to close pull the
        #: tree out from under the second — hence a count, not a bool.
        self._holders = 0

    def load(self) -> None:
        """Ensure the tree is parsed. Every query calls this, so it must
        NOT count as taking a hold — see `acquire`."""
        if self._tree is None:
            self._tree = load_json_checked(self._path, "World locations database")

    def acquire(self) -> None:
        """A picker is opening: take a hold and make sure the tree is
        there. Paired with `release`."""
        self._holders += 1
        self.load()

    def release(self) -> None:
        """Drop the parsed tree once the LAST holder is done with it
        (the owner's original intent: the 5.6 MB tree must not sit in
        RAM for the life of the process just because Settings was opened
        once). Extra releases are ignored rather than driving the count
        negative — and a release while a SIBLING picker is still open
        keeps the tree, which is the whole point of counting."""
        self._holders = max(0, self._holders - 1)
        if self._holders == 0:
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

    def find_city(self, name: str) -> list[Place]:
        """All cities whose folded name matches (full walk — picker search
        box and the core CLI selftest). Diacritic spellings match their
        ASCII transliterations: "Niš" finds "Nis", "Tromsø" finds "Tromso".
        """
        self.load()
        wanted = fold_name(name)
        matches: list[Place] = []
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
    def _make_record(node_path: tuple[str, ...], leaf: dict) -> Place:
        return Place(
            path=node_path,
            name=node_path[-1],
            latitude=float(leaf["latitude"]),
            longitude=float(leaf["longitude"]),
            timezone=leaf["timezone"],
        )


def default_place() -> Place:
    """The Belgrade preset as a WHOLE place — the factory location of a
    watch that has never picked one, and the repair value when a stored
    location cannot be trusted. Its path is the real database path
    (verified against `world_locations.json`), so a fresh watch is
    already coherent instead of carrying a name with no path."""
    return Place(
        path=tuple(defaults.DEFAULT_CITY["path"]),
        name=str(defaults.DEFAULT_CITY["name"]),
        latitude=float(defaults.DEFAULT_CITY["latitude"]),
        longitude=float(defaults.DEFAULT_CITY["longitude"]),
        timezone=str(defaults.DEFAULT_CITY["timezone"]),
    )


#: How close a stored coordinate must be to a database record to be
#: called the same city. Generous on purpose: the point is to tell
#: Belgrade/Serbia from Belgrade/Montana (hundreds of km apart), not to
#: re-verify a coordinate the user may have nudged by hand.
_SAME_CITY_DEG = 1.0


def _resolve_path(name: str, latitude: float, longitude: float) -> tuple[str, ...]:
    """The database's own path for a city known only by name and
    coordinates. Empty when the name is unknown, when no record sits
    near those coordinates (a hand-tuned position — genuinely pathless),
    or when the database cannot be read at all: a missing path is an
    honest answer the crown already knows how to render, so this must
    never be able to fail the load it serves.

    THE ONE COPY RULE, and a real crash it caused: `find_city` parses
    the 5.6 MB tree if it is not there, but taking no HOLD leaves it
    resident afterwards — a repair on the settings-load path therefore
    left the largest JSON in the app parked in RAM for the life of the
    process, and repeated across a test session it aborted the
    interpreter mid-collection. The acquire/release pair is the same
    counted hold the picker takes: the tree is dropped again the moment
    this lookup is done, unless a picker is genuinely holding it."""
    repository = shared_locations()
    try:
        repository.acquire()
        candidates = repository.find_city(name)
    except Exception:
        return ()
    finally:
        repository.release()
    for record in candidates:
        if (
            abs(record.latitude - latitude) <= _SAME_CITY_DEG
            and abs(record.longitude - longitude) <= _SAME_CITY_DEG
        ):
            return record.path
    return ()


def place_from_mapping(raw: object) -> Place | None:
    """THE ONE DOOR for a location that comes from OUTSIDE the database
    — a stored `settings.json`, a hand edit, a file written by an older
    version. Answers with a whole `Place` or with None; there is no
    third outcome and no partial result, which is the entire point.

    `path` is optional (a Quick Jump city stored before 2026-08-16
    carried only name/lat/lon/timezone) but it may never belong to a
    DIFFERENT city than `name`: that combination is precisely the
    "BELGRADE BURUNDI" defect, and it is rejected here rather than
    detected later. Coordinate ranges and the IANA zone are checked in
    the same breath, because a place is not whole without them either.
    """
    if not isinstance(raw, dict):
        return None
    name = str(raw.get("name", "")).strip()
    if not name:
        return None
    try:
        latitude = float(raw["latitude"])
        longitude = float(raw["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
    if not constants.LATITUDE_RANGE[0] <= latitude <= constants.LATITUDE_RANGE[1]:
        return None
    if not constants.LONGITUDE_RANGE[0] <= longitude <= constants.LONGITUDE_RANGE[1]:
        return None
    timezone = str(raw.get("timezone", ""))
    try:
        ZoneInfo(timezone)
    except Exception:
        return None
    path = tuple(str(segment) for segment in raw.get("path", ()) or ())
    if path and fold_name(path[-1]) != fold_name(name):
        # THE LYING PATH — the one combination that produced "BELGRADE
        # BURUNDI": a path naming a different city than the name beside
        # it. The name, the coordinates and the zone are the trustworthy
        # half (they always came from a picked record; only the path was
        # read off the combo boxes), so the path is discarded and the
        # database asked for the real one. The place then comes back
        # WHOLE — the crown reads "BELGRADE, SERBIA" again instead of
        # falling back to the zone region.
        #
        # ONLY here. An ABSENT path is not damage and is not repaired:
        # a Quick Jump city stored before 2026-08-16 never had one, and
        # neither does a hand-tuned coordinate. Resolving those too
        # would parse the 5.6 MB city tree on ordinary settings loads —
        # measured, not feared: it aborted the interpreter mid-
        # collection during a full test run. We repair what WE broke,
        # and we do not invent a path for a place that never had one.
        path = _resolve_path(name, latitude, longitude)
    return Place(
        path=path,
        name=name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
    )


#: THE process-wide city database (owner bug 2026-08-06). The bundled
#: file is 5.6 MB — the largest JSON in the app — and the tree it parses
#: to is identical for every watch: what differs is only the city each
#: one PICKS out of it. Two Settings dialogs open at once used to hold
#: two independent parsed trees, and reopening the same dialog reparsed
#: from scratch every time.
_SHARED = Shared(LocationRepository)


def shared_locations() -> "LocationRepository":
    """The one city database this process uses. It still RELEASES when
    the last picker closes (`LocationRepository.release`) — shared does
    not mean resident forever."""
    return _SHARED.get()

