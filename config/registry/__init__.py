"""THE REGISTRY — one dictionary of all themes, grouped by KIND.

Owner decree 2026-08-01, designed with the owner 2026-08-04/05. Theme
knowledge used to be scattered over ~20 tables in six modules, and the
~30 `WEEKDAY_THEME_FILES[key] = ...` assignments that followed their own
definition were the visible symptom: they were never exceptions to a
rule, they were DATA with no home. Here every theme declares its whole
contract in one entry, and every table a consumer reads is COMPUTED
from it in ONE assignment — so THE CONFIG SECTION LAW's ban on
post-definition patching holds by construction rather than by care.

The kinds (owner-sealed), and where each one's data lives:

  * **week — 6+3** ([week.py](week.py)): six weekdays, then Sunday's
    three — Ruler, Servant, Ninth. Declared HERE, because it was the
    scattered one: ~20 tables in six modules, with ~30 patches applied
    after their own definition.
  * **dozen — 12+1**: `config.calendar_mounts.CALENDAR_MOUNTS` — twelve
    wedges and an axle, already ONE table in one section.
  * **cube — 24+3**: `config.cube` — and its seating is COMPUTED
    (`core.cube_seating`), re-derived by the suite rather than stored.
  * **wheel — N+centre**: `config.archetypes.ARCHETYPES`.
  * **pointers**: [pointers.py](pointers.py) — not a kind but the
    matrix that says which kinds each pointer may carry, per shape.

THE OTHER THREE ARE NOT MOVED, DELIBERATELY (owner ruling 2026-08-05,
the same ruling that put the week registry back into one file). Each is
already a single declarative table in its own section, breaking no law
and patched nowhere; moving them would buy a tidier import and cost the
thing this project actually pays for — a reader finding the mounts
where the mounts have always been. What the registry owes them is a
NAMED VIEW, so a caller can ask "every kind, every member" without
knowing which module holds which: `KINDS`, `members_of` and
`kind_of` below.

Layer: config — pure. The `week` package imports nothing but the
sentinel, which is what lets
`constants` and `pantheon` both derive from it without a cycle.
"""

from config.registry.sentinel import COMPUTED
from config.registry.week import MENU, MENU_TOP, WEEK

BODIES = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")
# seat key -> the planetary body that is the seat's second name.
DAYS = {
    "sunday": "sun", "monday": "moon", "tuesday": "mars",
    "wednesday": "mercury", "thursday": "jupiter", "friday": "venus",
    "saturday": "saturn",
}
BODY_DAY = {body: day for day, body in DAYS.items()}


def _seats(entry):
    """(body, seat) for the six weekday seats of one theme, in dial
    order — the Sunday seat is the `sunday` block and never here."""
    return [
        (DAYS[day], seat)
        for day, seat in entry["seats"].items()
    ]


def _earth_stems():
    """The Continents' seat stems, COMPUTED from the region table (Rule
    #19). Imported lazily: `config.continents` reads `config.paths`, and
    the registry must stay importable from anywhere in config."""
    from config import continents

    style = continents.CONTINENTS_PREVIEW_STYLE
    stems = {
        body: f"earth_{style}_{region}_day"
        for body, region in continents.CONTINENTS_REGIONS.items()
    }
    dual = f"../earth/earth_{style}_{continents.CONTINENTS_DUAL_REGION}_day"
    return stems, dual


# ═══════════════════════════ DERIVED — THE WEEK KIND ═══════════════════════════
# Every table below is ONE assignment over WEEK. Nothing is patched
# afterwards; a value that used to be an "exception" is now a field.

THEMES = tuple(WEEK)

GROUP_OF = {theme: label for label, themes in MENU for theme in themes}

TITLES = {k: v["title"] for k, v in WEEK.items() if v["title"] is not None}

DIRS = {k: v["art"] for k, v in WEEK.items() if v["art"] is not None}

ARTICLES = {k: v["articles"] for k, v in WEEK.items() if v["articles"]}

BLURBS = {k: v["blurbs"] for k, v in WEEK.items() if v["blurbs"]}

METAL_THEMES = tuple(k for k, v in WEEK.items() if "metals" in v)

METALS = {k: v["metals"] for k, v in WEEK.items() if "metals" in v}

# The Sunday LABEL is its own datum, never "ruler · servant" derived:
# most themes print both faces there ("Nemean Lion · Cerberus") and some
# print one ("Helios (Ἥλιος)"), which is a display decision per theme.
NAMES = {
    theme: {body: seat["name"] for body, seat in _seats(entry)}
           | {"sun": entry["sunday"]["name"]}
    for theme, entry in WEEK.items()
    if entry["sunday"]["name"] is not None
    and all(seat["name"] is not None for _b, seat in _seats(entry))
}

DUAL_NAMES = {
    k: (v["sunday"]["ruler"], v["sunday"]["servant"])
    for k, v in WEEK.items()
    if v["sunday"]["ruler"] is not None
}

NINTHS = {
    k: (v["ninth"]["name"], v["ninth"]["plate"])
    for k, v in WEEK.items() if "ninth" in v
}

MECHANISMS = {
    k: v["ninth"]["mechanism"]
    for k, v in WEEK.items()
    if "ninth" in v and v["ninth"].get("mechanism")
}

# The two ALT tables are one field here, split by the mechanism that
# governs it — a sky trigger surfaces the easter egg, the daylight
# state swaps the night face (`term_weekly` needs no alt table at all:
# its roster already names both halves).
NINTH_ALTS = {
    k: (v["ninth"]["alt"], v["ninth"]["alt_plate"])
    for k, v in WEEK.items() if "ninth" in v and v["ninth"].get("alt")
}
NINTH_EASTER_EGG = {
    k: v for k, v in NINTH_ALTS.items() if MECHANISMS.get(k) == "easter_egg"
}
NINTH_NIGHT = {
    k: v for k, v in NINTH_ALTS.items() if MECHANISMS.get(k) == "daynight"
}

# A seat that holds several figures. The keys are the ROSTER's own
# vocabulary — a weekday body, or "dual"/"ninth" for the two seats that
# live outside the weekday six.
SEAT_ROSTERS = {
    theme: rosters
    for theme, entry in WEEK.items()
    if (rosters := (
        {body: seat["rotates"] for body, seat in _seats(entry) if "rotates" in seat}
        | ({"sun": entry["sunday"]["rotates"]} if "rotates" in entry["sunday"] else {})
        | ({"dual": entry["sunday"]["servant_rotates"]}
           if "servant_rotates" in entry["sunday"] else {})
        | ({"ninth": entry["ninth"]["rotates"]}
           if "ninth" in entry and "rotates" in entry["ninth"] else {})
    ))
}

PANTHEON = {
    theme: {
        "articles": entry["pantheon"]["articles"],
        "files": {DAYS[day]: files
                  for day, (files, _name) in entry["pantheon"]["seats"].items()},
        "names": {DAYS[day]: name
                  for day, (_files, name) in entry["pantheon"]["seats"].items()},
        "dual": entry["pantheon"]["dual"],
        "dual_names": entry["pantheon"]["dual_names"],
    }
    for theme, entry in WEEK.items() if "pantheon" in entry
}

TITLE_PLATE_SEATS = {
    k: v["title_plate"] for k, v in WEEK.items() if "title_plate" in v
}


def _files():
    """Seat file stems per theme, with the COMPUTED sentinels resolved.
    A function rather than a comprehension because the Continents reach
    out of the registry for their stems, and that import must happen at
    call time."""
    earth_stems, earth_dual = None, None
    out = {}
    for theme, entry in WEEK.items():
        stems = {}
        for body, seat in _seats(entry):
            stem = seat["stem"]
            if stem is COMPUTED:
                if earth_stems is None:
                    earth_stems, earth_dual = _earth_stems()
                stem = earth_stems[body]
            stems[body] = stem
        sun = entry["sunday"]["stem"]
        if sun is COMPUTED:
            if earth_stems is None:
                earth_stems, earth_dual = _earth_stems()
            sun = earth_stems["sun"]
        stems["sun"] = sun
        if all(v is not None for v in stems.values()):
            out[theme] = stems
    return out


def _dual_files():
    """The Servant plate per theme, sentinel resolved (see `_files`)."""
    out, earth_dual = {}, None
    for theme, entry in WEEK.items():
        plate = entry["sunday"]["servant_plate"]
        if plate is COMPUTED:
            if earth_dual is None:
                _stems, earth_dual = _earth_stems()
            plate = earth_dual
        if plate is not None:
            out[theme] = plate
    return out


# LAZY, and it has to be (2026-08-05). `constants` reads this module,
# and the Continents' COMPUTED stems reach `config.continents` ->
# `config.paths` -> back to `constants` — a cycle if the resolution runs
# at import time. PEP 562's module `__getattr__` moves it to FIRST
# ACCESS instead, by which point every module in the ring is built. The
# result is cached: the tables are read on every paint.
_CACHE: dict = {}
_LAZY = {"FILES": _files, "DUAL_FILES": _dual_files}


def __getattr__(name: str):
    """`registry.FILES` / `registry.DUAL_FILES`, resolved once."""
    if name in _LAZY:
        return _CACHE.setdefault(name, _LAZY[name]())
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ═══════════════════════════ EVERY KIND, ONE VIEW ═══════════════════════════
# The four kinds and their members, without a caller needing to know
# which module declares which. A VIEW, never a copy: each function reads
# the owning table live, so the registry can never disagree with the
# thing it describes.
from config.registry.pointers import CUBE, DOZEN, KINDS, WEEK as _WEEK_KIND, WHEEL  # noqa: E402


def themes_of(kind: str) -> tuple[str, ...]:
    """Every theme key of one kind, in its own registration order."""
    if kind == _WEEK_KIND:
        return THEMES
    if kind == DOZEN:
        from config import calendar_mounts

        return tuple(calendar_mounts.CALENDAR_MOUNTS)
    if kind == WHEEL:
        from config import archetypes

        return tuple(archetypes.ARCHETYPES)
    if kind == CUBE:
        return ("cube",)          # ONE theme, seated two ways
    return ()


def kinds_of(theme: str) -> tuple[str, ...]:
    """EVERY kind that claims this key — plural on purpose.

    A theme key is scoped to its KIND, not to the program: `virtues`
    and `sins` are each BOTH a week theme (the Inner Wheel's emblem
    families — the days ARE their virtues, their sins) and a Dozen (the
    Virtue Wheel's twelve Aristotelian seats, the Sins Dozen's twelve
    from Gregory and Dante). Different rosters with different members
    that happen to share a word; renaming either would cost a settings
    migration to buy nothing — so the collision is NAMED here instead
    of hidden. A caller that holds a bare key and needs certainty must
    say which kind it means."""
    return tuple(kind for kind in KINDS if theme in themes_of(kind))


def kind_of(theme: str) -> str | None:
    """The FIRST kind claiming this key, or None. Ambiguous by nature
    where a key is shared — see `kinds_of`, which is the honest answer;
    this one is the convenience for the (many) keys that are unique."""
    kinds = kinds_of(theme)
    return kinds[0] if kinds else None


def members_of(theme: str) -> tuple[str, ...]:
    """The display names a theme seats, in seat order — the one call a
    reader makes when it does not care which kind it is holding."""
    kind = kind_of(theme)
    if kind == _WEEK_KIND:
        entry = WEEK[theme]
        seats = [seat["name"] for seat in entry["seats"].values()]
        seats.append(entry["sunday"]["name"])
        if "ninth" in entry:
            seats.append(entry["ninth"]["name"])
        return tuple(name for name in seats if name)
    if kind == DOZEN:
        from config import calendar_mounts

        return tuple(calendar_mounts.CALENDAR_MOUNTS[theme].members)
    if kind == WHEEL:
        from config import archetypes

        return tuple(
            figure.get("name", "")
            for figure in archetypes.ARCHETYPES[theme].get("figures", ())
        )
    if kind == CUBE:
        from config import cube

        return tuple(
            cube.roster(cell, "archetypal")[0] for cell in cube.ROSE_24_SEATING
        )
    return ()
