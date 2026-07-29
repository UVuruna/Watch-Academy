"""The Encyclopedia's TOPIC TREE — every card the reader can open.

Two layers:

1. `_build_topics` — the flat topic table exactly as the browser always
   built it (moved VERBATIM from the old `app/encyclopedia.py`): one
   entry per page, article refs resolved lazily so the overlay always
   applies.
2. The **Session 27 laws** on top of it (owner-sealed 2026-07-28) —
   the Cube's 42-page run split into its four cards, the register
   merges (Bible x3, Creeds x2, Eclipses x2) folded into one card each,
   and EVERY topic sealed with a `variants` tuple the reader's switcher
   walks.

The shape a screen receives:

    {"title", "tile_title"?, "icon", "entries": [...],
     "variants": ((label, start, stop), ...)}

`variants` is ALWAYS present — a topic with one variant carries
`(("", 0, len(entries)),)` and its switcher stays hidden, so no screen
needs a special case (Rule #7).

Layer: app. Documentation: tree.md.
"""

from datetime import date

from config import archetypes, constants, defaults
from config import encyclopedia_tree as tree
from render.asset_recolor import metal_variant_path
from render.asset_variants import moon_phase_file
from render.instrument_diagrams import INSTRUMENT_FIGURES

from app.encyclopedia.builders import (
    _PANTHEON_BLOCK_SIZE,
    _guide_topic,
    _PANTHEON_MERGED_THEMES,
    _continents_topic,
    _live_ninth_face,
    _ninth_looks,
    _pantheon_topic,
    _theme_body_art,
    _theme_dual_art,
    _weekday_topic,
    _wider_topic,
)
from app.encyclopedia.pages import (
    _ARCHETYPE_TOPICS,
    _GOD_TOPIC_GALLERY_TITLES,
    _WEEKDAY_DUAL_PAGE_INDEX,
    _WEEKDAY_RESTRUCTURED_TOPICS,
    _ECLIPSE_TOPICS,
    _ERA_ENTRIES,
    _INSTRUMENT_KEYS,
    _SEASON_ENTRIES,
    _SUN_ENTRIES,
    _VSM_DAYS,
    _WEEK_EMBLEMS,
    _WEEK_ORDER,
)

def _build_topics(
    travel_date: date | None = None, is_daylight: bool = True,
) -> dict:
    """topic key -> {title, icon, entries}; article refs resolve lazily
    against the repository so the overlay always applies. Every entry
    carries an `images` TUPLE — Astrology pairs the sign logo with its
    constellation (owner spec: both, side by side). `travel_date`
    drives the Scale rotation (owner decree 2026-07-19/20, "koje cemo
    koristiti na smenu") AND cp_corpo's WEEKLY MANDATE (owner decree
    2026-07-29) — defaults to today when the caller has no Time Travel
    moment to hand in. `is_daylight` feeds sw_dyad's DAYLIGHT/NIGHT
    Ninth switch (same verdict) — defaults True (day, The Ghosts) so a
    caller with no live sky state (the warm cache) still resolves."""
    if travel_date is None:
        travel_date = date.today()
    topics: dict = {}
    for theme, title in defaults.WEEKDAY_THEME_TITLES.items():
        icon, entries = _weekday_topic(theme, travel_date)
        topics[theme] = {"title": title, "icon": icon, "entries": entries}
    # THE CONTINENTS overwrite its generic weekday build with the custom
    # topic (world-map title, look switcher, living Ninth) — same 11-page
    # order, so the Spacebar remap below still lands (owner-sealed matrix
    # 2026-07-21). Its Ninth is built HERE, so the shared ninths loop
    # skips it (see the guard there).
    topics["continents"] = _continents_topic(travel_date)
    topics["astrology"] = {
        "title": "Astrology",
        "icon": defaults.ZODIAC_ART_DIR / "zodiac" / "astrology" / "primary" / "sign" / "Leo.png",
        "entries": [
            {
                # Owner defaults 2026-07-13: the logo+constellation pair
                # leads; the arrows reach the colored logo and the sign.
                "looks": (
                    ("Logo & Constellation", ((
                        defaults.ZODIAC_ART_DIR / "zodiac" / "astrology" / "primary" / "logo"
                        / f"{sign}.png",
                        defaults.ZODIAC_ART_DIR / "zodiac" / "astrology"
                        / "primary" / "constellation" / f"{sign}.png",
                    ),)),
                    ("Colored", ((
                        defaults.ZODIAC_ART_DIR / "zodiac" / "astrology" / "primary" / "colored"
                        / f"{sign}.png",
                    ),)),
                    ("Sign", ((
                        defaults.ZODIAC_ART_DIR / "zodiac" / "astrology" / "primary" / "sign"
                        / f"{sign}.png",
                    ),)),
                ),
                "name": sign,
                "article": ("zodiac", sign),
            }
            for sign in (
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn",
                "Aquarius", "Pisces",
            )
        ],
    }
    chinese_primary = defaults.ZODIAC_ART_DIR / "zodiac" / "chinese" / "primary" / "bronze"
    topics["chinese"] = {
        "title": "Chinese zodiac",
        "icon": chinese_primary / "Dragon.png",
        "entries": [
            {
                "name": animal,
                "article": ("chinese", animal),
                # The animals wear the four looks too — BRONZE first
                # (owner default 2026-07-13), the swaps and the
                # colored art on the arrows.
                "looks": tuple(
                    (label, ((path,),))
                    for label, path in (
                        ("Bronze", chinese_primary / f"{animal}.png"),
                        ("Gold", metal_variant_path(
                            chinese_primary / f"{animal}.png", "gold")),
                        ("Silver", metal_variant_path(
                            chinese_primary / f"{animal}.png", "silver")),
                        ("Colored",
                         defaults.ZODIAC_ART_DIR / "zodiac" / "chinese" / "primary" / "colored"
                         / f"{animal}.png"),
                    )
                ),
            }
            for animal in constants.CHINESE_ANIMALS
        ] + [
            {
                # THE FIVE ELEMENTS (Session 27 coverage law, owner
                # 2026-07-28): their own `elements` REGISTER beside the
                # twelve animals — an element is a parallel reading of
                # the same zodiac, never a thirteenth animal.
                "images": (
                    defaults.ZODIAC_ART_DIR / "zodiac" / "chinese"
                    / "elements" / "colored" / f"{element}.png",
                ),
                "name": element,
                "article": ("element", element),
            }
            for element in constants.CHINESE_ELEMENTS
        ],
    }
    # THE CLOCK (owner expansion 2026-07-13): the Week day pages and
    # the Instrument functionality articles — names and texts live in
    # Database/encyclopedia.json and resolve lazily per entry. The
    # image strip GROUPS by kinship on the arrows (owner: "nećemo da
    # nabacamo sve teme — grupišemo po srodnosti"): the canon strip
    # (planet, sign and the day's emblems), then the gods, the
    # religions and the craft themes; Sunday puts every pair SIDE BY
    # SIDE — Ruler immediately left of its Servant (owner correction
    # 2026-07-13: never stacked).
    def _week_theme_rows(body: str, themes: tuple) -> tuple:
        # Sunday STACKS each pair (owner 2026-07-14: "Sun pa ispod
        # Eclipse, pa sledeća kolona nova tematika") — Rulers across
        # the top row, each Servant directly UNDER its Ruler.
        if body != "sun":
            return (tuple(_theme_body_art(t, body) for t in themes),)
        return (
            tuple(_theme_body_art(t, "sun") for t in themes),
            tuple(_theme_dual_art(t) for t in themes),
        )

    def _week_canon_rows(body: str) -> tuple:
        virtue, sin, mood = _WEEK_EMBLEMS[body]
        if body != "sun":
            return ((
                _theme_body_art("planets", body),
                _theme_body_art("planet_signs", body),
                defaults.EMBLEM_ART_DIRS["virtues"] / f"{virtue[0]}.png",
                defaults.EMBLEM_ART_DIRS["sins"] / f"{sin[0]}.png",
                defaults.EMBLEM_ART_DIRS["moods"] / f"{mood[0]}.png",
            ),)
        return (
            (
                _theme_body_art("planets", "sun"),
                _theme_body_art("planet_signs", "sun"),
                defaults.EMBLEM_ART_DIRS["virtues"] / f"{virtue[0]}.png",
                defaults.EMBLEM_ART_DIRS["sins"] / f"{sin[0]}.png",
                defaults.EMBLEM_ART_DIRS["moods"] / f"{mood[0]}.png",
            ),
            (
                _theme_dual_art("planets"),
                _theme_dual_art("planet_signs"),
                defaults.EMBLEM_ART_DIRS["virtues"] / f"{virtue[1]}.png",
                defaults.EMBLEM_ART_DIRS["sins"] / f"{sin[1]}.png",
                defaults.EMBLEM_ART_DIRS["moods"] / f"{mood[1]}.png",
            ),
        )

    topics["week"] = {
        "title": "The Week",
        "icon": defaults.weekday_art("planets/primary/photo/Sun.png"),
        "entries": [
            {
                "looks": (
                    ("Canon", _week_canon_rows(body)),
                    ("Gods", _week_theme_rows(
                        body, ("greek", "norse", "egypt", "slavic")
                    )),
                    ("Religions", _week_theme_rows(
                        body, ("religion", "religion_alt")
                    )),
                    ("Themes", _week_theme_rows(
                        body, ("profession", "alchemy", "japan")
                    )),
                    ("Animals", _week_theme_rows(
                        body, ("wolf", "bee", "elephant")
                    )),
                ),
                "name": ("week_title", body),
                "article": ("week", body),
            }
            for body in _WEEK_ORDER
        ],
    }
    topics["instrument"] = {
        "title": "The Instrument",
        # The owner's gear-tooth section logo (2026-07-13); article
        # images join per key as they land (missing files stay hidden).
        "icon": defaults.INSTRUMENT_ART_DIR / "logo.png",
        "entries": [
            {
                # THE INSTRUMENT DRAWS ITSELF (owner verdict 2026-07-29,
                # root Rule #19): every page here whose figure is this
                # program's own geometry declares a DRAWER, not a file —
                # move `DIAL_OFFSET_DEG` and a painted dial would become
                # a lie while this one turns with it. `paint_light` is
                # the one page holding a real picture, and it keeps it.
                **(
                    {"diagram": ("instrument", key)}
                    if key in INSTRUMENT_FIGURES
                    else {"images": (defaults.INSTRUMENT_ART_DIR / f"{key}.png",)}
                ),
                "name": ("instrument_title", key),
                "article": ("instrument", key),
            }
            for key in _INSTRUMENT_KEYS
        ],
    }
    # THE INNER WHEEL: one entry per emblem, its logo above its text.
    for family in ("virtues", "sins", "moods"):
        topics[family] = {
            "title": family.capitalize(),
            "icon": (
                defaults.EMBLEM_ART_DIRS[family]
                / f"{_VSM_DAYS[family][0]}.png"
            ),
            "entries": [
                {
                    "images": (
                        defaults.EMBLEM_ART_DIRS[family]
                        / f"{name}.png",
                    ),
                    "name": name,
                    "article": ("emblem", family, name),
                }
                for name in _VSM_DAYS[family]
            ],
        }
    # The comparative WHEEL article leads the Moods topic (owner GO
    # 2026-07-14): humors -> Plutchik -> the dial's own eight, with
    # the owner's wheel plate as the illustration.
    topics["moods"]["entries"].insert(0, {
        "images": (
            defaults.EMBLEM_ART_DIRS["moods"] / "Wheel_of_Moods.png",
        ),
        "name": "The Wheel of Moods",
        "article": ("emblem", "moods", "The Wheel of Moods"),
    })
    # THE NINTH MOOD closes it (owner 8+1 structure, 2026-07-14):
    # Eclipse keeps its plate as the EVENT mood outside the eight
    # hours — the moment the Servant crosses the Ruler.
    topics["moods"]["entries"].append({
        "images": (defaults.EMBLEM_ART_DIRS["moods"] / "Eclipse.png",),
        "name": "The Ninth Mood",
        "article": ("emblem", "moods", "The Ninth Mood"),
    })
    # THE NINE INTELLIGENCES (owner GO 2026-07-13; canon-web REWRITE +
    # WEEKDAY-LAW reseat, owner-sealed R7b 2026-07-21): Gardner's nine
    # move onto the seats the clock already keeps — SIX on the weekday
    # arms (Mon Interpersonal, Tue Bodily-Kinesthetic, Wed Linguistic,
    # Thu Logical-Mathematical, Fri Musical, Sat Naturalist), THREE on
    # the Sun's own faces (RULER = Visual-Spatial, the all-seeing king;
    # SERVANT = Intrapersonal, the self-mirror at solar midnight; NINTH
    # = Existential, The Unfound, the question itself at the noon
    # window). The page order follows the weekday law like every
    # restructured theme: title -> Mon..Sat -> Ruler -> Servant ->
    # Ninth (no separate trio-title page — the title page's own "The
    # Sun's Three Faces" subhead introduces the trio; the flat emblem
    # machinery wants none). The badge art stems are unchanged — only
    # the DIAL SEAT of each intelligence moved, not the plate.
    intel = defaults.EMBLEM_ART_DIRS["intelligence"]
    topics["intelligences"] = {
        "title": "The Nine Intelligences",
        "icon": intel / "Existential.png",
        "entries": [{
            "images": (defaults.theme_title_art("intelligences"),),
            "name": "The Nine Intelligences",
            "article": ("emblem", "intelligence", "The Nine Intelligences"),
        }] + [
            {
                "images": (intel / f"{stem}.png",),
                "name": name,
                "article": ("emblem", "intelligence", name),
            }
            for name, stem in (
                ("Interpersonal", "Interpersonal"),               # Monday
                ("Bodily-Kinesthetic", "Bodily_Kinesthetic"),     # Tuesday
                ("Linguistic", "Linguistic"),                     # Wednesday
                ("Logical-Mathematical", "Logical_Mathematical"), # Thursday
                ("Musical", "Musical"),                           # Friday
                ("Naturalist", "Naturalist"),                     # Saturday
                ("Spatial", "Spatial"),                           # Sun · Ruler
                ("Intrapersonal", "Intrapersonal"),               # Sun · Servant
                ("Existential", "Existential"),                   # Ninth
            )
        ],
    }
    # THE SLAVIC MONTHS (owner-sealed R7b 2026-07-21): the Croatian
    # months as a Calendar-pointer 12-set + its own topic — the year's
    # own wheel of labour (etymology, the pan-Slavic siblings, the mark's
    # place on the Calendar pointer wedge). Built from
    # `defaults.SLAVIC_MONTHS` (Rule #4/#5 — one config table drives the
    # display name, the article key and the plate stem). Plates are a
    # FUTURE prompt sheet under the canonical sourceless `months/` root
    # (defaults.MONTHS_ART_DIR, graceful-absent). Rides The Celestial
    # Engine hall (the year's own wheel — see _TOPIC_GROUPS).
    topics["months"] = {
        "title": "The Slavic Months",
        # The Linden Month (June, the wheel's crown) fronts the gallery
        # card — graceful-absent like every month plate until the art
        # lands, so the card shows its name until then.
        "icon": defaults.MONTHS_ART_DIR / "Lipanj.png",
        "entries": [{
            # The reserved `Title` stem in the months' own register —
            # the seat `research/prompts/titles/theme_title_prompts.md`
            # has been writing a brief against since R8c.
            "images": (defaults.MONTHS_ART_DIR / "Title.png",),
            "name": "The Slavic Months",
            "article": ("emblem", "months", "The Slavic Months"),
        }] + [
            {
                "images": (defaults.MONTHS_ART_DIR / f"{stem}.png",),
                "name": f"{croatian} ({gloss})",
                "article": ("emblem", "months", croatian),
            }
            for croatian, gloss, stem, _month in defaults.SLAVIC_MONTHS
        ] + [
            # THE BLUE MOON LAW's SOL/MODRENIK (owner-sealed 2026-07-22,
            # R12): the year's own THIRTEENTH pair — closes the topic
            # exactly like a Ninth closes every other one (the wheel
            # itself stays twelve; these two live ONLY in the dial
            # CENTER, in a blue-moon year, inside their own short
            # window — core.blue_moon). Same graceful-absent contract
            # as the twelve above: the plate is a future prompt sheet.
            {
                # ONE GENERIC THIRTEENTH (owner decree 2026-07-29):
                # every twelve-based set on this instrument says the
                # same thing when a thirteenth arrives — the count does
                # not close — and it says it once, in the instrument's
                # own furniture rather than in each set's register.
                "images": (defaults.THIRTEENTH_GENERIC_ART,),
                "name": name,
                "article": ("emblem", "months", key),
            }
            for key, name in (
                ("Sol", "Sol (the Sun's Month)"),
                ("Modrenik", "Modrenik (the Blue Moon Month)"),
            )
        ],
    }
    # THE NINTHS close their topics (owner 8+1 doctrine 2026-07-14):
    # the excluded member, the event, the myth, the legend — plates
    # wired ahead of the art (missing files stay hidden). Their shared
    # philosophical NAME is NINTH_SEAT_PHILOSOPHICAL_NAME (module level,
    # above) — see there for the discussed alternatives.
    _z = defaults.ZODIAC_ART_DIR
    # Round-four/five verdicts (owner 2026-07-15): the Union ninths —
    # Gaia/Yggdrasil/Triglav/the Pharaoh/the Polymath/the Holy Trinity/
    # the Ninth Circle/Freemasonry — supersede the old exile ninths;
    # Melchizedek relocates to Bible II, the Unknown God to the
    # Ancient set. Retired entries stay in encyclopedia.json for the
    # Wider-Pantheon wave. The 15 WEEKDAY themes' ninths now live in
    # `constants.WEEKDAY_THEME_NINTHS` (round R3b item 3 — the SAME
    # table the CENTER seat's solar-window face law reads, Rule #5);
    # the two ZODIAC-only ninths (no weekday Sunday duality) stay
    # local, since render never needs them.
    for topic_key, name, plate in (
        *(
            (theme, *_live_ninth_face(
                theme, name, defaults.weekday_art(rel), is_daylight, travel_date,
            ))
            for theme, (name, rel) in constants.WEEKDAY_THEME_NINTHS.items()
            # THE CONTINENTS builds its own LIVING Ninth inside
            # `_continents_topic` (Zealandia/Pangea by the traveled day),
            # so this shared static append must skip it (owner-sealed
            # matrix 2026-07-21).
            if theme != "continents"
        ),
        ("chinese", "The Cat", _z / "zodiac/chinese/primary/bronze/Cat.png"),
        ("astrology", "Ophiuchus",
         _z / "zodiac/astrology/primary/sign/Ophiuchus.png"),
    ):
        ninth_entry = {
            "images": (plate,),
            "name": name,
            "article": ("emblem", "ninths", name),
        }
        # THE NINTH'S OWN FINISH SWITCHER (owner bug, Gaia screenshot —
        # round R3): every metal-plate theme's Ninth gets the SAME
        # Colored/Bronze/Gold/Silver cycle as its seated eight.
        ninth_looks = _ninth_looks(topic_key, plate)
        if ninth_looks is not None:
            ninth_entry["looks"] = ninth_looks
        topics[topic_key]["entries"].append(ninth_entry)
    # THE PANTHEON/PLANETARY MERGE (round R3b item 2): pages 12-22 —
    # the SAME 11-page shape all over again, in the culture's OWN
    # hierarchy roster, reusing the ninth entry the loop above JUST
    # appended (`entries[-1]`) rather than building a second one — the
    # SAME figure closes both blocks (CANON.md: one Ninth per theme).
    # THE WIDER COURT (round R8d) then trails as a third block, page 23
    # onward — see `_wider_topic` above.
    for theme in _PANTHEON_MERGED_THEMES:
        entries = topics[theme]["entries"]
        assert len(entries) == _PANTHEON_BLOCK_SIZE, (
            theme, len(entries)
        )  # every Pantheon culture also names a Ninth (documented)
        entries.extend(_pantheon_topic(theme))
        entries.append(entries[_PANTHEON_BLOCK_SIZE - 1])
        entries.extend(_wider_topic(theme))
    # THE TWO TRIANGLES (owner 2026-07-13): the Judas–Lucifer scale —
    # the two fallen extremes of self and the zero no individual
    # reaches. The badge art is wired ahead of its landing (missing
    # files stay hidden); the Union pairs both triangles.
    # THE SCALE ROTATION (owner decree 2026-07-19/20, CANON.md
    # one-image-one-place amendment — Judas-Lucifer is a MAIN theme,
    # "koje cemo koristiti na smenu"): Lucifer and Judas each keep
    # MULTIPLE generated versions on disk; the shown face advances
    # with `travel_date` instead of freezing on one master. Only the
    # two poles rotate — the Union stays fixed.
    topics["duality"] = {
        "title": "The Two Triangles",
        "icon": defaults.SCALE_ART_DIR / "primary" / "colored" / "Union.png",
        "entries": [
            {
                "images": (
                    defaults.scale_variant_file("Lucifer", travel_date)
                    or defaults.SCALE_ART_DIR / "primary" / "colored" / "Lucifer.png",
                ),
                "name": "Lucifer",
                "article": ("emblem", "duality", "Lucifer"),
            },
            {
                "images": (
                    defaults.scale_variant_file("Judas", travel_date)
                    or defaults.SCALE_ART_DIR / "primary" / "colored" / "Judas.png",
                ),
                "name": "Judas",
                "article": ("emblem", "duality", "Judas"),
            },
            {
                # The owner's hexagram badge (2026-07-13): the two
                # triangles interlocked, the white circle at the cross.
                "images": (defaults.SCALE_ART_DIR / "primary" / "colored" / "Union.png",),
                "name": "The Union",
                "article": ("emblem", "duality", "The Union"),
            },
        ],
    }
    topics["trinity"] = {
        "title": "Trinity",
        "icon": defaults.TRINITY_ART_DIR / "Faith.png",
        "entries": [
            {
                # The trinity badges landed 2026-07-13 — each virtue
                # wears its triskelion emblem above the article.
                "images": (defaults.TRINITY_ART_DIR / f"{virtue}.png",),
                "name": virtue,
                "article": ("trio", virtue),
            }
            for virtue in ("Faith", "Hope", "Love")
        ],
    }
    # THE MOON (owner 2026-07-16, ROADMAP queue #8b): EIGHT phase pages —
    # the four principal phases and the four between them — in cycle
    # order, each a house-voice article carrying the phase's geometry,
    # its myth and the tides (spring at new/full, neap at the quarters).
    # The order is constants.MOON_PHASE_NAMES, so the Spacebar jump
    # (compositor._element_encyclopedia_target) indexes a hovered phase
    # straight into this list. Every page wears ITS OWN phase plate,
    # rendered LIVE (owner decree 2026-07-19: "bolje crtati na licu
    # mesta nego 15MB fajlova") from the full-moon master with the
    # dial's own terminator geometry — moon_phase_file, disk-cached.
    moon_plate = defaults.weekday_art("planets/primary/photo/Moon.png")
    topics["moon"] = {
        "title": "Moon",
        "icon": moon_plate,
        "entries": [
            {
                "images": (
                    moon_phase_file(
                        index / len(constants.MOON_PHASE_NAMES),
                        phase.lower().replace(" ", "_"),
                    ),
                ),
                "name": ("moon_title", phase),
                "article": ("moon", phase),
            }
            for index, phase in enumerate(constants.MOON_PHASE_NAMES)
        ],
    }
    topics["seasons"] = {
        "title": "Seasons",
        "icon": defaults.SEASON_ART_DIR / "Summer.png",
        "entries": [
            {
                "images": (
                    tuple(
                        defaults.SEASON_ART_DIR / "meteorological"
                        / f"{season}.png"
                        for season in ("Spring", "Summer", "Autumn",
                                       "Winter")
                    )
                    if art is None
                    else (defaults.SEASON_ART_DIR / art,)
                ),
                "name": ("season_title", key),
                "article": ("season", key),
            }
            for key, art in _SEASON_ENTRIES
        ],
    }
    # THE SUN (owner 2026-07-16, ROADMAP queue #10): the turning points
    # — the solstices and the equinoxes and their glow.
    topics["sun"] = {
        "title": "Sun",
        "icon": defaults.SEASON_ART_DIR / "turning_point"
        / "Summer_Solstice.png",
        "entries": [
            {
                "images": (defaults.SEASON_ART_DIR / art,),
                "name": ("sun_title", key),
                "article": ("sun", key),
            }
            for key, art in _SUN_ENTRIES
        ],
    }
    # THE ERA TERMS (ROADMAP 15a3, owner 2026-07-17): the Age of Light,
    # the Age of Darkness and the four Starry Seasons, closed by the
    # comparative "Eras of the World" essay (no plate of its own).
    def _era_image(art: str):
        """One rotating era emblem (THE UNIVERSAL ROTATION CONVENTION,
        owner decree 2026-07-20): the canonical file plus any `_v2`
        siblings and its `alt/` twin feed one daily pool, keyed by
        `travel_date` exactly like the Scale rotation above. Zero
        candidates (art not landed yet) keeps the plain canonical path
        — graceful-absent, the Encyclopedia hides missing art. Used for
        BOTH the six single Age/Starry-Season entries below AND every
        emblem in the "Eras of the World" calendar strip (ERA-TRIO
        round, owner 2026-07-20 — ground-truthed: the calendar strip
        used to bypass rotation entirely, a straight `ERA_ART_DIR / a`
        with no `rotating_art_file` call, so a `calendar/alt/*`
        sibling like the Byzantine v2 emblem would never have been
        found; fixed the same round, since the convention is
        universal)."""
        canonical = defaults.ERA_ART_DIR / art
        return defaults.rotating_art_file(canonical, travel_date) or canonical

    topics["era"] = {
        "title": "Eras & Ages",
        "icon": defaults.ERA_ART_DIR / "Age_of_Light.png",
        "entries": [
            {
                "images": (
                    tuple(_era_image(a) for a in row[1])
                    if isinstance(row[1], tuple)
                    else (_era_image(row[1]),) if row[1] else ()
                ),
                # A row is (key, art) or (key, art, diagram) — the same
                # shape the Cube's own pages use for a COMPUTED figure.
                **({"diagram": row[2]} if len(row) > 2 else {}),
                "name": ("era_title", row[0]),
                "article": ("era", row[0]),
            }
            for row in _ERA_ENTRIES
        ],
    }
    # THE ECLIPSES (fix round F, owner order 2026-07-19): two topics —
    # Solar and Lunar — one per body, each an overview page then a
    # category chapter per kind. Every category chapter wears its own
    # emblem; the overview strings its body's emblems as a strip
    # (isinstance tuple), graceful-absent until the art lands.
    for topic_key, title, icon_stem, entry_specs in _ECLIPSE_TOPICS:
        topics[topic_key] = {
            "title": title,
            "icon": defaults.ECLIPSE_ART_DIR / icon_stem,
            "entries": [
                {
                    "images": (
                        tuple(defaults.ECLIPSE_ART_DIR / a for a in art)
                        if isinstance(art, tuple)
                        else (defaults.ECLIPSE_ART_DIR / art,)
                    ),
                    "name": ("eclipse_title", key),
                    "article": ("eclipse", key),
                }
                for key, art in entry_specs
            ],
        }
    # THE ARCHETYPES HALL (the Cube canon — WORKPLAN Session 21, owner
    # seal 2026-07-26, CUBE.md — plus One Soul, owner verdict
    # 2026-07-27). Every entry ORDER here is contractual:
    # `config/archetypes.py` addresses these pages by INDEX in the Cube
    # wheels' and the prism-secondary wheel's `enc` targets (the Spacebar
    # jump), exactly as the Walks address the Professions;
    # `tests/test_cube_encyclopedia.py` and `tests/test_one_soul_theme.py`
    # pin both ends.
    for topic_key, title, tile, icon, family, entry_specs in _ARCHETYPE_TOPICS:
        topics[topic_key] = {
            "title": title,
            "icon": icon,
            # A row is (name, art) or (name, art, diagram): the COMPUTED
            # pages (owner verdict 2026-07-29) name a drawer instead of
            # a file — the axes, the Cube's own figures and the two
            # projections are compositions the canon exempted from
            # generation, and the program draws them from
            # `config.cube`'s coordinates (root Rule #19).
            "entries": [
                {
                    "images": () if row[1] is None else (row[1],),
                    "name": row[0],
                    "article": ("emblem", family, row[0]),
                    **({"diagram": row[2]} if len(row) > 2 else {}),
                }
                for row in entry_specs
            ],
        }
        if tile is not None:
            topics[topic_key]["tile_title"] = tile
    return topics


# =============================================================================
# THE SESSION 27 LAWS (owner-sealed 2026-07-28)
# =============================================================================
# Everything above builds the flat table the browser always had. The four
# functions below are the whole of the reorganization: the Cube split, the
# register merges, the god-block labels, and the seal that gives EVERY
# topic a `variants` tuple so no screen needs a special case.

# The four Cube cards' own gallery plates. Each is a page THIS card
# already owns (Rule #5, no new art): The One opens the doctrine, the
# Integrity glass stands for the axes, the Meekness cell for the eight
# figures, the Sacred Axis for the projections. The figures' own eleven
# pages carry no plate yet, so that card borrows the neighbouring edge
# cell rather than showing an empty tile.
_CUBE_CARD_ICONS = {
    "cube_doctrine": archetypes.SACRED_ART_DIR / "The_One.png",
    "cube_axes": archetypes.CHARACTER_ART_DIR / "Integrity.png",
    "cube_figures": archetypes.EDGES_ART_DIR / "Meekness.png",
    "cube_projections": archetypes.SACRED_ART_DIR / "Sacred_Axis.png",
}


def _split_cube(topics: dict) -> None:
    """The 42-page Cube run becomes the four cards of
    `tree.CUBE_TOPICS` — the doctrine, the thirteen axes with their
    poles and cells, the eight vertex figures, the two projections. The
    ENTRY ORDER of `_CUBE_ENTRIES` is untouched (it is a contract: the
    dial's Cube wheels still address pages by their old flat index and
    `tree.cube_target` re-aims them here)."""
    cube = topics.pop("cube")
    for key, title, start, stop in tree.CUBE_TOPICS:
        topics[key] = {
            "title": title,
            "icon": _CUBE_CARD_ICONS[key],
            "entries": cube["entries"][start:stop],
        }


def _merge_variants(topics: dict) -> None:
    """THE VARIANT LAW: registers of ONE subject become ONE card, their
    blocks concatenated in declaration order and their boundaries kept
    as the variant ranges. The card inherits the FIRST register's icon —
    always a plate that already exists, so the merge needs no new art."""
    for key, (title, sources) in tree.VARIANT_SOURCES.items():
        entries: list = []
        variants: list = []
        for label, source in sources:
            block = topics[source]["entries"]
            variants.append((label, len(entries), len(entries) + len(block)))
            entries.extend(block)
        icon = topics[sources[0][1]]["icon"]
        for _label, source in sources:
            del topics[source]
        topics[key] = {
            "title": title,
            "icon": icon,
            "entries": entries,
            "variants": tuple(variants),
        }


def _label_god_variants(topics: dict) -> None:
    """The four merged god themes ALREADY build as three contiguous
    blocks (planetary, pantheon, the wider court's trailing run) — the
    retired roster button walked them by arithmetic. They only need
    their labels, and the same switcher then drives them."""
    for theme in _PANTHEON_MERGED_THEMES:
        entries = topics[theme]["entries"]
        # The CARD wears the bare demonym (owner round R8b item 6:
        # "Ubuduce posto ce biti podnaslov Gods onda ce nazivi biti samo
        # Greek, Egypt, Norse") — with the whole's own name above it,
        # the "gods" suffix on a fixed-size label is noise. The reader's
        # header still titles the theme in full.
        topics[theme]["tile_title"] = _GOD_TOPIC_GALLERY_TITLES[theme]
        span = _PANTHEON_BLOCK_SIZE
        topics[theme]["variants"] = (
            (tree.GOD_VARIANT_LABELS[0], 0, span),
            (tree.GOD_VARIANT_LABELS[1], span, 2 * span),
            (tree.GOD_VARIANT_LABELS[2], 2 * span, len(entries)),
        )


def _drop_look_topics(topics: dict) -> None:
    """`planet_signs` is not a theme — it is one of the Planets card's
    three LOOKS (RESTRUCTURE §Themes vs looks). The old flat gallery
    kept it as an unreachable topic purely so a dial slot dressed in it
    could resolve a Spacebar jump; `tree.TOPIC_ALIASES` does that now,
    so the ghost card goes (Rule #6 — no dead path left behind). With
    it gone the table matches the tree EXACTLY, which is what
    `tests/test_encyclopedia_tree.py` pins."""
    topics.pop("planet_signs", None)


def _seal_variants(topics: dict) -> None:
    """Every remaining topic is a single run of pages — one nameless
    variant. With this, `topic["variants"]` is total: the reader reads
    it unconditionally and hides the switcher when there is only one."""
    for topic in topics.values():
        topic.setdefault("variants", (("", 0, len(topic["entries"])),))


def topics(
    travel_date: date | None = None,
    overlay: dict | None = None,
    is_daylight: bool = True,
) -> dict:
    """The topic table the three screens read — the built table with the
    Session 27 laws applied, in the order they must run (the Cube split
    first, so the merges and the seal see the four cards).

    `overlay` is the active language bundle; only the Guide needs it at
    BUILD time, because its prose lives in the help book's own JSON
    rather than in `encyclopedia.json` (Rule #5 — one copy of the
    content, read where it already is). `is_daylight` is THE DOUBLE
    NINTH LAW's daynight mechanism (owner decree 2026-07-29, sw_dyad) —
    defaults True (day) so a caller with no live sky state still
    resolves; see `_build_topics`."""
    built = _build_topics(travel_date, is_daylight)
    built["guide"] = _guide_topic(overlay or {})
    _split_cube(built)
    _merge_variants(built)
    _label_god_variants(built)
    _drop_look_topics(built)
    _seal_variants(built)
    return built


# --- Reading the variants ----------------------------------------------------

def variant_at(topic: dict, index: int) -> int:
    """Which variant the given page sits in."""
    for position, (_label, start, stop) in enumerate(topic["variants"]):
        if start <= index < stop:
            return position
    return 0


def switch_variant(topic: dict, index: int, delta: int) -> int:
    """THE OFFSET LAW (owner spec, 2026-07-28: "promena kao do sada
    pamti poziciju dana tj redni broj stranice"): stepping the switcher
    keeps the reader's position INSIDE the variant — Monday stays
    Monday when the roster changes. A shorter variant (the Wider Court
    runs 4 pages against Planetary's 11) clamps to its own last page
    instead of overrunning into the next block."""
    variants = topic["variants"]
    current = variant_at(topic, index)
    offset = index - variants[current][1]
    _label, start, stop = variants[(current + delta) % len(variants)]
    return start + min(offset, stop - start - 1)


def resolve_target(all_topics: dict, key: str, entry: int) -> tuple | None:
    """(topic key, page index) for a jump addressed the OLD way — by a
    dial theme key and a raw page index. Three rules, one path:

    1. **The Cube's flat index** — re-aimed across the four cards
       (`tree.cube_target`), so `config/archetypes.py`'s wheel table
       keeps working untouched.
    2. **The weekday dual remap** — the compositor still emits index 0
       for the Sun body (`_ENC_WEEK_ORDER`, unaware of the R3
       restructure); it lands on the Ruler half's own seat.
    3. **A merged register** — `bible_dark` opens the Bible card at its
       third variant's first page, `religion_alt` the Creeds card at
       its second.

    Returns None for an unknown key: the caller is the dial, and a
    stale target must leave the window where it is, never raise."""
    if key == "cube":
        return tree.cube_target(entry)
    if key in _WEEKDAY_RESTRUCTURED_TOPICS and entry == 0:
        entry = _WEEKDAY_DUAL_PAGE_INDEX
    if key in tree.TOPIC_ALIASES:
        topic_key, variant = tree.TOPIC_ALIASES[key]
        if topic_key not in all_topics:
            return None
        return topic_key, all_topics[topic_key]["variants"][variant][1] + entry
    if key in all_topics:
        return key, entry
    return None
