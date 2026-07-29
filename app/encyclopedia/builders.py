"""The Encyclopedia's TOPIC BUILDERS.

One responsibility: turn a theme key into (icon, entries) — the weekday
skeleton every theme shares (title, Monday..Saturday, the week-duality
title, the Ruler and Servant halves, the Ninth), the pantheon and
wider-court blocks the four god themes add, and the Continents topic's
own custom build with its four earth looks and its living Ninth.

Split out of the old 2,766-line `app/encyclopedia.py` in the Session 27
rework (root Rule #20). The builders moved VERBATIM — the Session 27
reform changed how topics are GROUPED and READ, never how a page is
built.

Layer: app. Documentation: builders.md.
"""

import json
from datetime import date
from pathlib import Path

from config import constants, defaults, paths
from core import continents
from data.encyclopedia import EncyclopediaRepository
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.asset_recolor import metal_variant_path

from app.encyclopedia.pages import (
    _GOD_TOPIC_GALLERY_TITLES,
    _INSTRUMENT_KEYS,
    _VSM_DAYS,
    _WEEK_EMBLEMS,
    _WEEK_ORDER,
    NINTH_SEAT_PHILOSOPHICAL_NAME,
)

def _metal_looks(base: Path, colored: Path | None) -> tuple:
    """The four LOOKS of a bronze-plate image (owner 2026-07-13),
    COLORED FIRST — the owner's default — then Bronze as drawn and
    the two selective-swap disk-cache variants. PATHS ONLY (owner
    order 2026-07-26: opening the Encyclopedia must never block —
    `metal_variant_path` names the cache file without building it;
    the pixels build in the background warm or on first display
    through `ensure_variant`)."""
    looks = []
    if colored is not None and paths.art_file(colored).exists():
        looks.append(("Colored", colored))
    looks += [
        ("Bronze", base),
        ("Gold", metal_variant_path(base, "gold")),
        ("Silver", metal_variant_path(base, "silver")),
    ]
    return tuple(looks)


def _colored_sibling(path: Path) -> Path:
    """The COLORED twin of a bronze-plate FILE. ONE rule since the
    tree law landed (owner-approved 2026-07-26): every plate lives at
    `<register>/<look>/<File>.png` and its colored twin at the SAME
    register's own `colored/` child — pantheon and primary identically.
    The old two-depth branch (pantheon nested, primary sibling — the
    round R8b item 3 zoo) died with the migration; this is now the
    path twin of `defaults.colored_variant_rel` for resolved Paths."""
    return path.parent.parent / "colored" / path.name


def _ninth_looks(theme: str, plate: Path) -> tuple | None:
    """The Ninth's OWN look switcher (owner bug, "Gaia screenshot":
    the 9th member's page carried the color switcher for NONE of its
    metal-plate themes) — every theme whose seated eight cycle Colored/
    Bronze/Gold/Silver gives its Ninth the SAME cycle, `colored` found
    via `_colored_sibling` (owner round R8b item 3 fix — Gaia/Yggdrasil
    sit under `pantheon/`, the shallow-nested colored twin the old
    unconditional `parent.parent` guess always missed); the Chinese
    Ninth (The Cat) mirrors the OTHER eleven animals' Bronze-first
    order instead. Themes with no per-metal art (egypt, slavic, the
    plain-color families) return None — the Ninth stays the single
    plain plate, same as before, since there is nothing to switch."""
    if theme == "chinese":
        return tuple(
            (label, ((path,),))
            for label, path in (
                ("Bronze", plate),
                ("Gold", metal_variant_path(plate, "gold")),
                ("Silver", metal_variant_path(plate, "silver")),
                ("Colored", _colored_sibling(plate)),
            )
        )
    if theme not in constants.METAL_THEMES:
        return None
    return tuple(
        (label, ((path,),))
        for label, path in _metal_looks(plate, _colored_sibling(plate))
    )


def _live_ninth_face(
    theme: str, name: str, plate: Path, is_daylight: bool, travel_date: date,
) -> tuple[str, Path]:
    """Which (name, plate) `theme`'s shared ninths-loop entry actually
    shows — THE DOUBLE NINTH LAW's Encyclopedia side (owner Double-
    Ninth verdicts, 2026-07-29): the reader shows ONLY the currently
    active face, never both. "daynight" swaps to the NIGHT face when
    `is_daylight` is False (`constants.WEEKDAY_THEME_NINTH_NIGHT`);
    "term_weekly" rotates the SAME canonical plate through its OWN seat
    roster by the traveled date's ISO week
    (`defaults.rotating_art_file`'s cadence override — the identical
    chokepoint the dial reads, Rule #5); every other mechanism (or none)
    keeps `name`/`plate` untouched, the plain static plate every
    non-double Ninth has always shown here."""
    mechanism = constants.NINTH_MECHANISMS.get(theme)
    if mechanism == "daynight" and not is_daylight:
        alt_name, alt_rel = constants.WEEKDAY_THEME_NINTH_NIGHT[theme]
        return alt_name, defaults.weekday_art(alt_rel)
    if mechanism == "term_weekly":
        return name, defaults.rotating_art_file(plate, travel_date) or plate
    return name, plate


# One theme's plate for one body (bronze / canon file) — the
# resolution itself lives in config (Rule #5: `app.pointer_theme` and
# `app.slot_theme` need the SAME preview art for their picker grids).
_theme_body_art = defaults.weekday_theme_body_art


def _theme_dual_art(
    theme: str, colored: bool = False, on_date: date | None = None,
) -> Path:
    """The theme's Sunday SERVANT plate — the colored dual lives in
    the register's own colored/ look (tree law 2026-07-26;
    `colored_variant_rel` is the ONE swap implementation). `on_date`
    opts into THE UNIVERSAL ROTATION CONVENTION (`defaults.
    rotating_art_file`), exactly like the live dial's OWN Servant
    resolution (`render.layers.WeekdayLayer`) — None (every caller
    before THE WEEKLY MANDATE, owner decree 2026-07-29) keeps the plain
    canonical file."""
    rel = defaults.WEEKDAY_DUAL_FILES[theme]
    if colored:
        rel = defaults.colored_variant_rel(rel)
    asset = defaults.weekday_art(f"{rel}.png")
    if on_date is not None:
        asset = defaults.rotating_art_file(asset, on_date) or asset
    return asset


def _weekday_topic(theme: str, travel_date: date | None = None):
    """(icon path, entries) for one weekday theme (owner ARTICLE ORDER
    restructure, round R3; SPLIT into two separate GOOD/EVIL pages,
    round R3b item 1 — owner verdict A, supersedes the R3 MERGED dual
    page): entry 0 is the theme's OWN title page (`theme_title` —
    describes the whole theme; the plate is a documented graceful-
    absent slot for a future theme plate, the TEXT is written now);
    entries 1-6 are Monday..Saturday, in that order (owner: "Ponedeljak
    PRVI"); entry 7 is the WEEK-DUALITY title page (`week_duality`);
    entry 8 is the GOOD (Ruler) half of Sunday, its own ordinary single-
    image page; entry 9 is the EVIL (Servant) half, ALSO its own
    ordinary single-image page with its OWN plate — the R3 two-column-
    in-one-page dual layout is retired (each half is now indistinguish-
    able in shape from a Monday..Saturday page, just fed through
    `evil_looks_for` for the Servant side). The metal themes still
    cycle Colored/Bronze/Gold/Silver on EACH half independently; the
    planets still cycle their photos and the sign glyphs. The Ninth
    (where the theme has one) is appended AFTER this function returns
    (`_topics`' ninths loop), landing last either way.

    `travel_date` feeds THE WEEKLY MANDATE alone (owner decree
    2026-07-29, `constants.NINTH_MECHANISMS[theme] == "term_weekly"` —
    today only cp_corpo): the GOOD/EVIL pages then rotate through the
    seat roster's OWN two halves by the ISO week's parity, exactly like
    the dial. Every OTHER theme ignores `travel_date` completely — its
    Monday..Saturday and Sunday pages stay the frozen canonical plate
    they have always been in the Encyclopedia (Rule #15 — this law
    touches cp_corpo alone, not every theme's static gallery)."""
    article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
    if theme == "planets":
        names = defaults.DEFAULT_SKIN.weekday_set.body_names
    else:
        names = defaults.WEEKDAY_THEME_NAMES[theme]
    metal = theme in constants.METAL_THEMES
    mandate_date = (
        travel_date
        if constants.NINTH_MECHANISMS.get(theme) == "term_weekly"
        else None
    )

    def rows(ruler: Path, servant: Path | None) -> tuple:
        if servant is not None and paths.art_file(servant).exists():
            return ((ruler, servant),)
        return ((ruler,),)

    def looks_for(body: str, on_date: date | None = None) -> tuple:
        """A Monday..Saturday (or GOOD/Ruler) page's own looks — always
        a SINGLE image per look now (round R3b item 1: the old
        `dual=True` two-plate-per-row branch retired with the merged
        page; `evil_looks_for` below is EVIL's own sibling). `on_date`
        (THE WEEKLY MANDATE only — every other caller passes None)
        threads through `_theme_body_art`'s own `on_date`/`colored`
        pair so the bronze base and its colored sibling always agree on
        which roster half is showing (Rule #5 — one resolver, not a
        hand-rolled second path for the colored look)."""
        base = _theme_body_art(theme, body, on_date=on_date)
        if metal:
            colored = _theme_body_art(theme, body, on_date=on_date, colored=True)
            return tuple(
                (label, rows(path, None))
                for label, path in _metal_looks(base, colored)
            )
        if theme == "planets":
            # Owner defaults 2026-07-13: the photos lead, the sign
            # glyphs and the bronze medallions ride the arrows.
            sign = defaults.weekday_art(f"planets/primary/sign/{body.capitalize()}.png")
            art = defaults.weekday_art(f"planets/primary/art/{body.capitalize()}.png")
            return (
                ("Planets", rows(base, None)),
                ("Signs", rows(sign, None)),
                ("Art", rows(art, None)),
            )
        return (("", rows(base, None)),)

    def evil_looks_for(on_date: date | None = None) -> tuple:
        """The EVIL half's OWN page (owner verdict A, round R3b item 1
        — the Servant plate ALONE, never paired with the Ruler's any
        more): mirrors `looks_for`'s per-metal/per-planets-look cycle
        exactly, built from `_theme_dual_art` instead of
        `_theme_body_art` (Rule #5 — the same shapes, the Servant's own
        files). `on_date` is THE WEEKLY MANDATE's own thread, same as
        `looks_for`."""
        servant = _theme_dual_art(theme, on_date=on_date)
        if metal:
            colored = _theme_dual_art(theme, colored=True, on_date=on_date)
            return tuple(
                (label, rows(path, None))
                for label, path in _metal_looks(servant, colored)
            )
        if theme == "planets":
            sign_dual = defaults.weekday_art("planets/primary/sign/Sun_Eclipse.png")
            art_dual = defaults.weekday_art("planets/primary/art/Sun_Eclipse.png")
            return (
                ("Planets", rows(servant, None)),
                ("Signs", rows(sign_dual, None)),
                ("Art", rows(art_dual, None)),
            )
        return (("", rows(servant, None)),)

    def body_entry(body: str) -> dict:
        return {
            "looks": looks_for(body),
            "name": names[body],
            "article": ("article", article_set, body),
            # TITLES CARRY THE DAY (owner round R8b item 8): read by
            # `_entry_name`, the ONE build point that appends it.
            "weekday": constants.WEEKDAY_FULL_NAMES[body],
        }

    def good_entry() -> dict:
        """The GOOD (Ruler) half of Sunday — its OWN page now (owner
        verdict A, round R3b item 1), an ordinary single-image page
        exactly shaped like Monday..Saturday's. THE WEEKLY MANDATE
        (`mandate_date`, cp_corpo only) rotates its plate to the RULING
        week's half; the display NAME stays the theme's static
        `WEEKDAY_DUAL_NAMES` (the established convention every rostered
        Sunday duality already follows — Session 32's own comment: "its
        rotating partners are named in the two face texts instead")."""
        ruler_name, _servant_name = defaults.WEEKDAY_DUAL_NAMES[theme]
        return {
            "looks": looks_for("sun", on_date=mandate_date),
            "name": ruler_name,
            "article": ("article_face", article_set, "sun", "ruler"),
            "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
        }

    def evil_entry() -> dict:
        """The EVIL (Servant) half of Sunday — its OWN page, its OWN
        plate (owner verdict A, round R3b item 1). Same `mandate_date`
        thread as `good_entry`."""
        _ruler_name, servant_name = defaults.WEEKDAY_DUAL_NAMES[theme]
        return {
            "looks": evil_looks_for(on_date=mandate_date),
            "name": servant_name,
            "article": ("article_face", article_set, "sun", "servant"),
            "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
        }

    title_entry = {
        "images": (defaults.theme_title_art(theme),),
        "name": ("theme_title", theme),
        "article": ("theme_title", theme),
    }
    duality_title_entry = {
        "images": (defaults.theme_title_art(theme, duality=True),),
        "name": ("week_duality_title", theme),
        "article": ("week_duality", theme),
    }
    entries = (
        [title_entry]
        + [body_entry(body) for body in _WEEK_ORDER[1:]]   # Monday..Saturday
        + [duality_title_entry, good_entry(), evil_entry()]
    )
    return _theme_body_art(theme, "sun"), entries


# THE PANTHEON/PLANETARY MERGE (Ency INSTRUCTIONS.txt rule 5, round
# R3b item 2): the four themes with a documented Pantheon roster
# (`defaults.WEEKDAY_PANTHEON`) become ONE topic each — pages 1-11 the
# Planetary run `_weekday_topic` already builds (title, Mon..Sat, week-
# duality title, good, evil, ninth), pages 12-22 the SAME 11-page shape
# again for the Pantheon roster (`_pantheon_topic` below), reusing the
# Planetary block's OWN Ninth (CANON.md: a theme names ONE Ninth,
# outside BOTH rosters, never a second seatless figure per roster) —
# both blocks close on the identical Gaia/Yggdrasil/Pharaoh/Triglav
# page. `_PANTHEON_BLOCK_SIZE` is the fixed span every merged theme's
# Planetary block occupies (11 — all four Pantheon cultures also carry
# a Ninth, so the arithmetic never varies): the roster-switch button
# jumps `entry_index +/- _PANTHEON_BLOCK_SIZE`. Page 23 onward is a
# THIRD block, The Wider Court (`_wider_topic` below, round R8d) — see
# there for why it is NOT a third roster the switch button cycles into.
_PANTHEON_BLOCK_SIZE = 11
# The fixed span of BOTH the Planetary and Pantheon blocks together —
# page 23 (0-indexed 22) is where The Wider Court title opens.
_WIDER_BLOCK_START = 2 * _PANTHEON_BLOCK_SIZE
_PANTHEON_MERGED_THEMES = frozenset(defaults.WEEKDAY_PANTHEON)

# THE WIDER COURT'S FIGURES (round R8d, THE WIDER COURT RE-WIRE, owner-
# approved 2026-07-22 — restores WORKPLAN Session 8's content after
# round R8b's `_WIDER_TOPICS` deletion turned out to be a MISDIAGNOSIS:
# the owner's "zasto i dalje imamo ove dve verzije" complaint was about
# the standalone topics sitting as confusing SECOND gallery tiles next
# to the merged culture topics — never about the fifteen articles
# themselves, which stayed untouched in `encyclopedia.json` the whole
# time, simply unreachable from the UI). Same figure roster the deleted
# `_WIDER_TOPICS` carried verbatim — the culture's famous A-list gods
# that NEITHER roster seats (see the old comment preserved in git
# history, commit 4081445, for the full reconciliation reasoning against
# the round-four/five ninth-seat locks).
_WIDER_FIGURES = {
    "greek": ("Dionysus", "Hephaestus", "Hestia"),
    "norse": ("Baldur", "Heimdall", "Njord"),
    "egypt": ("Set", "Nut", "Geb", "Ptah", "Sekhmet"),
    "slavic": ("Crnobog", "Stribog", "Jarilo", "Rod"),
}


def _pantheon_topic(theme: str) -> list[dict]:
    """The PANTHEON roster's OWN 11-page run for `theme` (round R3b
    item 2) — the SAME [title, Monday..Saturday, week-duality title,
    good, evil] shape `_weekday_topic` builds (the Ninth is appended
    separately, shared with the Planetary block — see
    `_PANTHEON_MERGED_THEMES` above), sourced from
    `defaults.WEEKDAY_PANTHEON[theme]` through `defaults.pantheon_seat`
    — the SAME safety law the live dial's Pantheon roster reads (Rule
    #5, CANON.md "Two Rosters"): a seat whose pantheon plate has not
    landed keeps the WHOLE planetary bundle (file + name + article
    together), and a missing pantheon DUAL pulls the whole Sunday pair
    (both faces) back to the planetary bundle too — never a pantheon
    name paired with planetary art or the reverse. Metal cycling
    follows the theme's OWN rule (`theme in constants.METAL_THEMES`) —
    greek/norse cycle Colored/Bronze/Gold/Silver on the Pantheon plates
    too, `_colored_sibling` finding the twin at whichever depth the
    seat's OWN plate lives at (owner round R8b item 3 fix: a seat that
    falls back to the planetary primary plate — Zeus, Thor, Loki, Tyr,
    none of whom grew dedicated Pantheon art — used to silently drop
    Colored, since the old code only ever checked the shallow
    `pantheon/colored/` nesting); egypt/slavic stay a single plain
    plate, like their Planetary block."""
    table = defaults.WEEKDAY_PANTHEON[theme]
    metal = theme in constants.METAL_THEMES

    def seated(body: str) -> tuple[Path, str, str, str]:
        """(plate, name, article_set, article_body) for one body."""
        found = defaults.pantheon_seat(theme, body)
        if found is not None:
            path, name, (article_set, article_body) = found
            return path, name, article_set, article_body
        return (
            _theme_body_art(theme, body),
            defaults.WEEKDAY_THEME_NAMES[theme][body],
            constants.WEEKDAY_THEME_ARTICLES[theme],
            body,
        )

    def looks_for(path: Path) -> tuple:
        if metal:
            return tuple(
                (label, ((one,),))
                for label, one in _metal_looks(path, _colored_sibling(path))
            )
        return (("", ((path,),)),)

    def body_entry(body: str) -> dict:
        path, name, article_set, article_body = seated(body)
        return {
            "looks": looks_for(path),
            "name": name,
            "article": ("article", article_set, article_body),
            "weekday": constants.WEEKDAY_FULL_NAMES[body],
        }

    sun_path, _sun_name, _sun_set, _sun_body = seated("sun")
    dual_path = defaults.weekday_art(f"{table['dual'][0]}.png")
    if paths.art_file(dual_path).exists():
        ruler_name, servant_name = table["dual_names"]
        face_article_set = table["articles"]
    else:
        # The safety law's Sunday half (CANON.md "Two Rosters"): a
        # missing pantheon dual pulls the WHOLE Sunday pair back to
        # the planetary bundle — never a pantheon Ruler over a
        # planetary Servant, or the reverse.
        sun_path = _theme_body_art(theme, "sun")
        dual_path = _theme_dual_art(theme)
        ruler_name, servant_name = defaults.WEEKDAY_DUAL_NAMES[theme]
        face_article_set = constants.WEEKDAY_THEME_ARTICLES[theme]

    title_key = f"{theme}_pantheon"
    title_entry = {
        "images": (defaults.theme_title_art(title_key),),
        "name": ("theme_title", title_key),
        "article": ("theme_title", title_key),
    }
    duality_title_entry = {
        "images": (defaults.theme_title_art(title_key, duality=True),),
        "name": ("week_duality_title", title_key),
        "article": ("week_duality", title_key),
    }
    good_entry = {
        "looks": looks_for(sun_path),
        "name": ruler_name,
        "article": ("article_face", face_article_set, "sun", "ruler"),
        "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
    }
    evil_entry = {
        "looks": looks_for(dual_path),
        "name": servant_name,
        "article": ("article_face", face_article_set, "sun", "servant"),
        "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
    }
    return (
        [title_entry]
        + [body_entry(body) for body in _WEEK_ORDER[1:]]   # Monday..Saturday
        + [duality_title_entry, good_entry, evil_entry]
    )


def _wider_topic(theme: str) -> list[dict]:
    """THE WIDER COURT — a culture's seatless A-list figures, folded
    back in as a TRAILING third block (round R8d, restoring WORKPLAN
    Session 8's content after round R8b deleted its standalone topics
    as misdiagnosed "duplicate tiles" — see `_WIDER_FIGURES` above): a
    section TITLE page (`"<theme>_wider"` in `encyclopedia.json`'s
    `theme_title` family, the SAME family `_pantheon_topic`'s
    `"<theme>_pantheon"` title reads, Rule #5) followed by one ordinary
    single-image page per figure — sourced from the exact same
    `EncyclopediaRepository.entry("wider", name)` family the deleted
    topics read, so the prose is untouched, only its HOME moved. NO
    `looks` key: ground-truthed against the asset tree
    (`assets/weekday/<source>/<theme>/wider/`) — none of the fifteen
    figures has ANY art yet, not even a bronze master, so there is
    nothing to cycle; the page renders on `"images"` alone and stays
    gracefully absent (a name and a text, no plate) exactly like the
    old standalone topics did, until the owner's art lands."""
    title_key = f"{theme}_wider"
    title_entry = {
        "images": (defaults.theme_title_art(title_key),),
        "name": ("theme_title", title_key),
        "article": ("theme_title", title_key),
    }
    figure_entries = [
        {
            "images": (
                defaults.weekday_art(f"{theme}/wider/bronze/{figure.lower()}.png"),
            ),
            "name": figure,
            "article": ("emblem", "wider", figure),
        }
        for figure in _WIDER_FIGURES[theme]
    ]
    return [title_entry] + figure_entries


def _continents_topic(travel_date: date) -> dict:
    """THE CONTINENTS topic (owner-sealed matrix 2026-07-21) — a CUSTOM
    weekday-shaped topic that OVERWRITES the generic `_weekday_topic`
    build so it can carry the world-map TITLE page and the Atmosphere/
    Clean · Day/Night LOOK SWITCHER on every earth-face page (the generic
    build gives a single unlabeled look). The eleven pages keep the same
    ORDER as every restructured theme (title, Monday..Saturday, duality
    title, Antarctic Ruler, Arctic Servant, Ninth) so the Spacebar remap
    and the article-order canon still hold.

    The six continent bodies and the two poles reuse the dial's OWN Earth
    faces (assets/earth/, owner exception, sealed) and their prose is the
    SAME symbolism.json articles the dial hover reads (Rule #5). The Ninth
    is LIVING: Zealandia the Unfound normally, Pangea on a Pangea day
    (`core.continents` against the traveled date and the bundled Seasons/
    Moon data) — both articles exist; the plate is graceful-absent until
    the owner's art lands, like every wired-ahead Ninth.

    THE LOOK-SWITCHER default (honest choice): the static gallery cannot
    read the live sky, so every earth-face page OPENS on "Atmosphere"
    (atmo · day) and offers all four looks; the LIVE-sky default belongs
    to the dial, where `continents_body_art` reads the tick. Finish
    persistence carries the chosen look across the pages exactly as it
    does the metal finishes."""
    def region_looks(region: str) -> tuple:
        return tuple(
            (label, ((defaults.earth_face_art(style, region, phase),),))
            for label, style, phase in (
                ("Atmosphere", "atmo", "day"),
                ("Atmosphere · Night", "atmo", "night"),
                ("Clean", "clean", "day"),
                ("Clean · Night", "clean", "night"),
            )
        )

    def body_entry(body: str) -> dict:
        return {
            "looks": region_looks(defaults.CONTINENTS_REGIONS[body]),
            "name": defaults.WEEKDAY_THEME_NAMES["continents"][body],
            "article": ("article", "continents", body),
            "weekday": constants.WEEKDAY_FULL_NAMES[body],
        }

    ruler_name, servant_name = defaults.WEEKDAY_DUAL_NAMES["continents"]
    title_entry = {
        "images": (defaults.CONTINENTS_TITLE_IMAGE,),
        "name": ("theme_title", "continents"),
        "article": ("theme_title", "continents"),
    }
    duality_title_entry = {
        # The two poles in eternal antiphase, side by side.
        "images": (
            defaults.earth_face_art("atmo", "south_pole", "day"),
            defaults.earth_face_art("atmo", "north_pole", "day"),
        ),
        "name": ("week_duality_title", "continents"),
        "article": ("week_duality", "continents"),
    }
    good_entry = {
        "looks": region_looks("south_pole"),
        "name": ruler_name,
        "article": ("article_face", "continents", "sun", "ruler"),
        "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
    }
    evil_entry = {
        "looks": region_looks("north_pole"),
        "name": servant_name,
        "article": ("article_face", "continents", "sun", "servant"),
        "weekday": constants.WEEKDAY_FULL_NAMES["sun"],
    }
    pangea = continents.ninth_is_pangea_from_repos(
        travel_date, SeasonsRepository(), MoonPhaseRepository()
    )
    ninth_name, ninth_rel = (
        constants.WEEKDAY_THEME_NINTH_EASTER_EGG["continents"]
        if pangea
        else constants.WEEKDAY_THEME_NINTHS["continents"]
    )
    ninth_entry = {
        "images": (defaults.weekday_art(ninth_rel),),
        "name": ninth_name,
        "article": ("emblem", "ninths", ninth_name),
    }
    entries = (
        [title_entry]
        + [body_entry(body) for body in _WEEK_ORDER[1:]]   # Monday..Saturday
        + [duality_title_entry, good_entry, evil_entry, ninth_entry]
    )
    return {
        "title": defaults.WEEKDAY_THEME_TITLES["continents"],
        "icon": defaults.CONTINENTS_TITLE_IMAGE,
        "entries": entries,
    }



def _guide_topic(overlay: dict) -> dict:
    """THE GUIDE as a topic (owner decision 2026-07-28: "Guide postaje
    peta kartica celine The Instrument — jedno mesto za čitanje svega").

    Built from the SAME `assets/instrument/guide/pages.json` +
    `captions.json` the retired GuideDialog read (Rule #5 — the help
    book's content is not copied, re-typed or translated twice): one
    guide PAGE becomes one encyclopedia ENTRY, its images the entry's
    image row, and each image's caption a `[[Title]] body` block, which
    the reader already draws as a centered bold heading over its
    paragraph. The overlay keys are the guide's own (`guide/<stem>`,
    `guide_page/<index>`), so an existing translation keeps working.
    """
    pages = json.loads(
        (defaults.GUIDE_DIR / "pages.json").read_text(encoding="utf-8")
    )["pages"]
    captions_path = defaults.GUIDE_DIR / "captions.json"
    captions = (
        json.loads(captions_path.read_text(encoding="utf-8"))
        if captions_path.exists() else {}
    )
    entries = []
    for index, page in enumerate(pages):
        stems = page["images"]
        blocks = []
        for stem in stems:
            caption = overlay.get(f"guide/{stem}", captions.get(stem, ""))
            if not caption:
                continue
            head, _, body = caption.partition("\n")
            blocks.append(f"[[{head}]]{body}")
        entries.append({
            "images": tuple(
                defaults.GUIDE_DIR / f"{stem}.png" for stem in stems
            ),
            "name": overlay.get(f"guide_page/{index}", page["title"]),
            "article": ("guide", "\n\n".join(blocks)),
        })
    return {
        "title": "The Guide",
        "icon": defaults.GUIDE_DIR / f"{pages[0]['images'][0]}.png",
        "entries": entries,
    }
