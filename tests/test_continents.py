"""THE CONTINENTS theme (owner-sealed matrix 2026-07-21, round R7a).

Pins the theme registration (six weekday continents + the polar dual +
the Zealandia/Pangea Ninth), the Ninth easter-egg LAW golden-tested on
known 2026 dates, the Encyclopedia topic's page order / title image /
look switcher, and the live-dial body art (earth_style x day/night).
"""

from datetime import date

from config import constants, defaults, paths
from core import continents


# --- 1. THEME REGISTRATION ---------------------------------------------------

def test_continents_registered_everywhere():
    """The theme is a first-class weekday theme: in the dial roster, in a
    menu group, with a title, an article set, blurb, dual and Ninth."""
    assert "continents" in constants.WEEKDAY_THEMES
    assert defaults.WEEKDAY_THEME_TITLES["continents"] == "Continents"
    assert constants.WEEKDAY_THEME_ARTICLES["continents"] == "continents"
    assert constants.WEEKDAY_THEME_BLURBS["continents"] == "day"
    assert defaults.WEEKDAY_DUAL_NAMES["continents"] == ("Antarctica", "Arctic")
    # It rides a menu group so the dial can offer it.
    grouped = {key for _t, keys in defaults.WEEKDAY_MENU_GROUPS for key in keys}
    assert "continents" in grouped


def test_continents_body_and_dual_plates_exist_on_disk():
    """Every one of the seven weekday bodies resolves to an EXISTING Earth
    face (the sealed owner exception — the dial's own art reused), and so
    does the Arctic Servant dual (test_every_theme_skeleton's law)."""
    for body in constants.WEEKDAY_BODIES:
        plate = defaults.weekday_theme_body_art("continents", body)
        assert paths.art_file(plate).exists(), body
    rel = defaults.WEEKDAY_DUAL_FILES["continents"]
    dual = defaults.weekday_art(f"{rel}.png")
    assert paths.art_file(dual).exists()


def test_continents_ninth_wired_zealandia_and_pangea():
    """The Ninth is Zealandia by default with Pangea as the easter-egg
    face; both plates are wired ahead of the owner's art (graceful-
    absent, like Triglav) — the render `theme_ninth` returns None until
    they land, for both faces."""
    from render.layers import theme_ninth

    assert constants.WEEKDAY_THEME_NINTHS["continents"][0] == "Zealandia"
    assert constants.WEEKDAY_THEME_NINTH_EASTER_EGG["continents"][0] == "Pangea"
    assert theme_ninth("continents") is None            # Zealandia pending
    assert theme_ninth("continents", active_alt=True) is None  # Pangea pending


def test_continent_regions_cover_the_six_columns_and_the_poles():
    """The sealed matrix's continent-to-weekday assignment, pinned."""
    assert defaults.CONTINENTS_REGIONS == {
        "moon": "oceania", "mars": "europe", "mercury": "asia",
        "jupiter": "africa", "venus": "south_america",
        "saturn": "north_america", "sun": "south_pole",
    }
    assert defaults.CONTINENTS_DUAL_REGION == "north_pole"


# --- 2. THE EASTER-EGG LAW (golden dates against the bundled data) -----------

def test_pangea_over_zealandia_truth_table():
    """The LAW is the OR of the three triggers, nothing more."""
    assert not continents.pangea_over_zealandia(False, False, False)
    assert continents.pangea_over_zealandia(True, False, False)     # eclipse
    assert continents.pangea_over_zealandia(False, True, False)     # turning pt
    assert continents.pangea_over_zealandia(False, False, True)     # principal phase


def test_easter_egg_golden_dates():
    """Owner-sealed golden dates against the BUNDLED season/moon data:
    a 2026 full-moon day and a solstice day show PANGEA; an ordinary day
    shows ZEALANDIA. Widened 2026-07-29: a First AND a Third Quarter day
    ALSO show Pangea now — the two dates the OLD full/new-only law would
    have missed."""
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    sr, mr = SeasonsRepository(), MoonPhaseRepository()
    full_moon = date(2026, 1, 3)          # a 2026 Full Moon (bundled)
    first_quarter = date(2026, 1, 26)     # a 2026 First Quarter (bundled)
    third_quarter = date(2026, 1, 10)     # a 2026 Third Quarter (bundled)
    summer_solstice = date(2026, 6, 21)   # a 2026 turning point (bundled)
    # 2026-07-07 (the old "moon-golden day", fraction 0.74) is ITSELF a
    # Third Quarter day now that the law covers all four principal
    # phases — 2026-07-11 sits mid-way to the next event (July 14 New
    # Moon) and is genuinely ordinary.
    ordinary = date(2026, 7, 11)          # neither trigger

    assert continents.ninth_is_pangea_from_repos(full_moon, sr, mr)
    assert continents.ninth_is_pangea_from_repos(first_quarter, sr, mr)
    assert continents.ninth_is_pangea_from_repos(third_quarter, sr, mr)
    assert continents.ninth_is_pangea_from_repos(summer_solstice, sr, mr)
    assert not continents.ninth_is_pangea_from_repos(ordinary, sr, mr)
    # The individual triggers, separately.
    assert continents.principal_phase_on(full_moon, mr)
    assert continents.principal_phase_on(first_quarter, mr)
    assert continents.principal_phase_on(third_quarter, mr)
    assert continents.turning_point_on(summer_solstice, sr)
    assert not continents.principal_phase_on(ordinary, mr)
    assert not continents.turning_point_on(ordinary, sr)


def test_easter_egg_from_events_matches_repos():
    """The DIAL wrapper (reading pre-built event lists) agrees with the
    ENCYCLOPEDIA wrapper (reading the repos) on the same day, and the
    live eclipse flag alone forces Pangea. `moon_events` is built with
    the SAME fraction->name mapping `core.clock_state`'s real
    `DayContext` uses (`constants.MOON_PHASE_FRACTIONS` inverted, all
    FOUR principal phases) — not a hand-rolled full/new-only ternary."""
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    sr, mr = SeasonsRepository(), MoonPhaseRepository()
    full_moon = date(2026, 1, 3)
    first_quarter = date(2026, 1, 26)
    names_by_fraction = {
        frac: name for name, frac in constants.MOON_PHASE_FRACTIONS.items()
    }
    # Build the event lists the DayContext would carry, from the repos.
    season_events = tuple(
        (instant, "anchor") for instant in sr.year_anchors(2026).instants
    )
    moon_events = tuple(
        (instant, names_by_fraction[frac % 1.0])
        for instant, frac in mr.moon_window(2026).events
    )
    assert continents.ninth_is_pangea_from_events(
        full_moon, season_events, moon_events, has_eclipse=False
    )
    # A quarter day — the WIDENED trigger (owner verdict 2026-07-29) —
    # forces Pangea exactly like full/new does.
    assert continents.ninth_is_pangea_from_events(
        first_quarter, season_events, moon_events, has_eclipse=False
    )
    # An ordinary day + a live eclipse still forces Pangea. 2026-07-11
    # (not 07-07, itself a Third Quarter day under the widened law).
    assert continents.ninth_is_pangea_from_events(
        date(2026, 7, 11), season_events, moon_events, has_eclipse=True
    )
    assert not continents.ninth_is_pangea_from_events(
        date(2026, 7, 11), season_events, moon_events, has_eclipse=False
    )


def test_easter_egg_graceful_outside_coverage():
    """A date outside the bundle answers False, never a crash (the deep
    pack is optional)."""
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    sr, mr = SeasonsRepository(), MoonPhaseRepository()
    assert not continents.ninth_is_pangea_from_repos(date(9999, 1, 1), sr, mr)


# --- 3/4. THE ENCYCLOPEDIA TOPIC (order, title image, look switcher) ---------

def test_topic_page_order():
    """The R3b restructured order: title, Monday..Saturday, duality
    title, Antarctic Ruler, Arctic Servant, living Ninth — 11 pages."""
    from app.encyclopedia import topics as _topics

    entries = _topics(date(2026, 7, 7))["continents"]["entries"]
    assert len(entries) == 11
    assert entries[0]["name"] == ("theme_title", "continents")
    mon_sat = [e["name"] for e in entries[1:7]]
    assert mon_sat == [
        "Oceania", "Europe", "Asia", "Africa",
        "South America", "North America",
    ]
    assert entries[7]["name"] == ("week_duality_title", "continents")
    assert entries[8]["name"] == "Antarctica"
    assert entries[8]["article"] == ("article_face", "continents", "sun", "ruler")
    assert entries[9]["name"] == "Arctic"
    assert entries[9]["article"] == ("article_face", "continents", "sun", "servant")


def test_topic_title_image_present():
    """The title page carries the world map (the whole Earth seen at
    once), copied into the earth family as a PNG."""
    from app.encyclopedia import topics as _topics

    topic = _topics(date(2026, 7, 7))["continents"]
    assert paths.art_file(topic["icon"]).exists()
    title = topic["entries"][0]
    assert title["images"] == (defaults.CONTINENTS_TITLE_IMAGE,)
    assert paths.art_file(defaults.CONTINENTS_TITLE_IMAGE).exists()


def test_topic_look_switcher_atmosphere_clean_day_night():
    """Every earth-face page (continents + poles) offers the four looks —
    Atmosphere/Clean crossed with Day/Night — each resolving to an
    EXISTING earth face."""
    from app.encyclopedia import topics as _topics

    entries = _topics(date(2026, 7, 7))["continents"]["entries"]
    face_pages = entries[1:7] + [entries[8], entries[9]]   # continents + poles
    expected_labels = [
        "Atmosphere", "Atmosphere · Night", "Clean", "Clean · Night",
    ]
    for entry in face_pages:
        labels = [label for label, _rows in entry["looks"]]
        assert labels == expected_labels, entry["name"]
        for _label, rows in entry["looks"]:
            (image,) = rows[0]
            assert paths.art_file(image).exists()


def test_topic_ninth_is_living():
    """The Ninth page follows the traveled day: Zealandia normally,
    Pangea on a Pangea day (a principal moon phase / turning point /
    eclipse — widened 2026-07-29 from full/new alone)."""
    from app.encyclopedia import topics as _topics

    # 2026-07-11 sits mid-way between the July 7 Third Quarter and the
    # July 14 New Moon — genuinely ordinary under the WIDENED law
    # (2026-07-07 itself is a Third Quarter day now, no longer safe).
    ordinary = _topics(date(2026, 7, 11))["continents"]["entries"][10]
    assert ordinary["name"] == "Zealandia"
    assert ordinary["article"] == ("emblem", "ninths", "Zealandia")
    pangea = _topics(date(2026, 1, 3))["continents"]["entries"][10]   # full moon
    assert pangea["name"] == "Pangea"
    assert pangea["article"] == ("emblem", "ninths", "Pangea")


def test_topic_rides_the_cosmos():
    """Gallery placement (owner: the Earth takes its seat among the far
    sky's other bodies — reseated from the old Celestial Engine into
    `cosmos` by Session 35, 2026-07-29)."""
    from config.encyclopedia_tree import WHOLES

    cosmos = {whole.key: whole for whole in WHOLES}["cosmos"]
    assert "continents" in cosmos.themes
    every = [theme for whole in WHOLES for theme in whole.themes]
    assert every.count("continents") == 1        # not scattered into two wholes


# --- 5. THE LIVE-DIAL BODY ART (earth_style x day/night) ---------------------

def test_continents_body_art_follows_style_and_sky():
    """On the dial the continent follows the user's earth_style (one
    setting) and the live sky's day/night — the atmo-day still frame is
    only the baked preview."""
    # Europe (Mars) by day in atmosphere, by night in clean.
    assert defaults.continents_body_art("mars", "atmo", True).name == (
        "earth_atmo_europe_day.png"
    )
    assert defaults.continents_body_art("mars", "clean", False).name == (
        "earth_clean_europe_night.png"
    )
    # The Ruler center (sun -> south_pole) and the Arctic Servant.
    assert defaults.continents_body_art("sun", "clean", True).name == (
        "earth_clean_south_pole_day.png"
    )
    assert defaults.continents_dual_art("atmo", False).name == (
        "earth_atmo_north_pole_night.png"
    )
    # Every live combination resolves to an existing face.
    for body in constants.WEEKDAY_BODIES:
        for style in defaults.CONTINENTS_PREVIEW_STYLE, "clean":
            for day in (True, False):
                assert paths.art_file(
                    defaults.continents_body_art(body, style, day)
                ).exists(), (body, style, day)


def test_body_articles_resolve_with_faces():
    """All seven articles exist (dial hover + Encyclopedia), the Sunday
    body carries distinct Ruler/Servant faces, and the two Ninth articles
    resolve."""
    from data.encyclopedia import EncyclopediaRepository
    from data.symbolism import SymbolismRepository

    sym = SymbolismRepository()
    for body in constants.WEEKDAY_BODIES:
        assert len(sym.article("continents", body)["base"]) > 250, body
    faces = sym.article("continents", "sun")["faces"]
    assert set(faces) == {"ruler", "servant"}
    assert faces["ruler"] != faces["servant"]
    enc = EncyclopediaRepository()
    assert enc.theme_title("continents")["title"] == "Continents"
    assert enc.week_duality("continents")["title"] == "The Two Poles"
    assert "2017" in enc.entry("ninths", "Zealandia")["base"]     # recognition year
    assert "supercontinent" in enc.entry("ninths", "Pangea")["base"].lower()
