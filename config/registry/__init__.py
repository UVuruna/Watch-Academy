"""THE REGISTRY — one dictionary of all themes, grouped by KIND.

Owner decree 2026-08-01, designed with the owner 2026-08-04/05. Theme
knowledge used to be scattered over ~20 tables in six modules, and the
~30 `WEEKDAY_THEME_FILES[key] = ...` assignments that followed their own
definition were the visible symptom: they were never exceptions to a
rule, they were DATA with no home. Here every theme declares its whole
contract in one entry, and every table a consumer reads is COMPUTED
from it in ONE assignment — so THE CONFIG SECTION LAW's ban on
post-definition patching holds by construction rather than by care.

The kinds (owner-sealed):

  * **week — 6+3** ([week.py](week.py)): six weekdays, then Sunday's
    three — Ruler, Servant, Ninth.
  * **dozen — 12+1**: twelve wedges and an axle. Still declared in
    `config.calendar_mounts`; it already is one table and breaks no
    law, so it moves here when its own round comes.
  * **cube — 24+3** and **wheel — N+centre**: `config.cube` and
    `config.archetypes`, same reasoning.

Layer: config — pure. `week` imports nothing at all, which is what lets
`constants` and `pantheon` both derive from it without a cycle.
Documentation: [registry](registry.md).
"""

from config.registry.week import COMPUTED, MENU, MENU_TOP, WEEK

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


FILES = _files()
DUAL_FILES = _dual_files()
