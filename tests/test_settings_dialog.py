"""M6 settings window: location picker cascade over the real database,
opacity overrides and the palette editor — headless (offscreen)."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from app.controller import apply_display_settings
from app.settings_dialog import SettingsDialog
from app.settings_store import Settings, replace
from config import defaults
from render.layers import palette_for

BELGRADE_PATH = ("Europe", "Southern Europe", "Serbia", "Grad Beograd", "Belgrade")


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_dialog_restores_the_stored_city(app):
    settings = replace(Settings(), city_path=BELGRADE_PATH)
    dialog = SettingsDialog(settings, defaults.DEFAULT_SKIN)
    assert dialog._continent.currentText() == "Europe"
    assert dialog._country.currentText() == "Serbia"
    assert dialog._city.currentText() == "Belgrade"
    result = dialog.result_settings()
    assert result.city_path == BELGRADE_PATH
    assert result.timezone == "Europe/Belgrade"
    dialog.done(0)


def test_dialog_city_pick_fills_coordinates(app):
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    dialog._restore_search(
        ("Europe", "Northern Europe", "Norway", "Troms og Finnmark", "Tromso")
    )
    result = dialog.result_settings()
    assert result.city_name == "Tromso"
    assert result.timezone == "Europe/Oslo"
    assert result.latitude == pytest.approx(69.65, abs=0.05)
    dialog.done(0)


def test_live_search_filters_and_jumps(app):
    """Owner spec (FINAL.txt #1): typing filters a visible result list —
    you always know whether the city exists; clicking a result jumps
    the combos to it. London must be findable."""
    from PySide6.QtCore import Qt

    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    dialog._search.setText("London")
    assert dialog._results.isVisible() or dialog._results.count() > 0
    texts = [dialog._results.item(i).text() for i in range(dialog._results.count())]
    assert any(t.startswith("London") and "United Kingdom" in t for t in texts)
    uk_london = next(
        dialog._results.item(i)
        for i in range(dialog._results.count())
        if "United Kingdom" in dialog._results.item(i).text()
        and dialog._results.item(i).text().startswith("London ")
    )
    dialog._pick_result(uk_london)
    result = dialog.result_settings()
    assert result.city_name == "London"
    assert result.timezone == "Europe/London"
    dialog._search.setText("Xyzzyqq")
    assert dialog._results.count() == 0
    assert dialog._search_status.text() == "not found"
    dialog.done(0)


def test_major_cities_pinned_per_country(app):
    """Agent recommendation: the timezone-reference heuristic pins the
    country's canonical cities — picking the United Kingdom must offer
    London with one click (the owner's complaint)."""
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    for combo, value in (
        (dialog._continent, "Europe"),
        (dialog._subregion, "Northern Europe"),
        (dialog._country, "United Kingdom"),
    ):
        combo.setCurrentIndex(combo.findText(value))
    stars = [dialog._results.item(i).text() for i in range(dialog._results.count())]
    assert "★ London" in stars
    london = next(
        dialog._results.item(i)
        for i in range(dialog._results.count())
        if dialog._results.item(i).text() == "★ London"
    )
    dialog._pick_result(london)
    result = dialog.result_settings()
    assert result.city_name == "London" and result.timezone == "Europe/London"
    dialog.done(0)


def test_major_cities_stay_quiet_until_the_user_acts(app):
    """Owner correction 2026-07-12: opening Settings must NOT pop the
    huge suggestion box — the location is picked once. Suggestions
    appear only after the USER touches the cascade, and the box wraps
    its rows instead of holding a fixed 120 px."""
    settings = replace(Settings(), city_path=BELGRADE_PATH)
    dialog = SettingsDialog(settings, defaults.DEFAULT_SKIN)
    assert dialog._results.count() == 0            # nothing suggested on open
    assert dialog._results.isHidden()
    dialog._country.setCurrentIndex(dialog._country.findText("Italy"))
    assert dialog._results.count() >= 1            # the user acted -> majors
    row = dialog._results.sizeHintForRow(0)
    assert dialog._results.height() <= dialog._results.count() * row + 10
    dialog.done(0)


def test_dialog_defaults_keep_skin_opacities(app):
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    result = dialog.result_settings()
    assert result.star_alpha is None            # untouched slider = skin default
    assert result.aura_day_alpha is None
    assert result.aura_twilight_alpha is None
    dialog.done(0)


def test_dialog_sliders_set_independent_overrides(app):
    """Owner spec: the Aura's sunlight and twilight opacities move
    independently — touching one leaves the other on the skin value."""
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    dialog._star_slider.setValue(40)
    dialog._aura_twilight_slider.setValue(70)
    result = dialog.result_settings()
    assert result.star_alpha == pytest.approx(0.40)
    assert result.aura_day_alpha is None
    assert result.aura_twilight_alpha == pytest.approx(0.70)
    dialog.done(0)


def test_dialog_palette_edit_and_reset(app):
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    dialog._hues[0] = "#123456"
    edited = dialog.result_settings()
    assert edited.palettes["hexa_paint"][0] == "#123456"
    dialog._reset_palette()
    clean = dialog.result_settings()
    assert "hexa_paint" not in clean.palettes   # back to the owner preset
    dialog.done(0)


# --- apply_display_settings (pure) ---------------------------------------------


def test_alpha_overrides():
    """Star: single slider, its twilight scales proportionally. Aura:
    sunlight and twilight are INDEPENDENT (owner spec) — an untouched
    one keeps the skin's own value."""
    settings = replace(Settings(), star_alpha=0.46, aura_twilight_alpha=0.7)
    skin = apply_display_settings(defaults.DEFAULT_SKIN, settings)
    base = defaults.DEFAULT_SKIN
    assert skin.star.day_alpha == pytest.approx(0.46)
    assert skin.star.twilight_alpha == pytest.approx(
        0.46 * base.star.twilight_alpha / base.star.day_alpha
    )
    assert skin.background.day_alpha == base.background.day_alpha  # untouched
    assert skin.background.twilight_alpha == pytest.approx(0.7)
    both = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(Settings(), aura_day_alpha=0.3, aura_twilight_alpha=0.9),
    )
    assert both.background.day_alpha == pytest.approx(0.3)
    assert both.background.twilight_alpha == pytest.approx(0.9)


def test_weekday_theme_swaps_bodies_and_names():
    """The themed art and canon display names replace the skin's unit;
    "planets" leaves the skin untouched."""
    greek = apply_display_settings(
        defaults.DEFAULT_SKIN, replace(Settings(), weekday_theme="greek")
    )
    # Display names carry the native script (owner 2026-07-12); the
    # file stays on the plain ASCII stem.
    assert greek.weekday_set.body_names["mercury"] == "Hermes (Ἑρμῆς)"
    assert greek.weekday_set.bodies["mercury"].name == "Hermes.png"
    assert "greek" in str(greek.weekday_set.bodies["mercury"])
    # Canonical paths resolve through the ART SOURCE (owner 2026-07-14).
    from config import paths as _paths

    assert all(
        _paths.art_file(path).exists()
        for path in greek.weekday_set.bodies.values()
    )
    planets = apply_display_settings(defaults.DEFAULT_SKIN, Settings())
    assert planets.weekday_set.bodies == defaults.DEFAULT_SKIN.weekday_set.bodies


def test_dialog_open_close_keeps_the_location(app):
    """Review fix: merely opening the Settings dialog must not relocate
    the user — the combo cascade lands on the alphabetically first city,
    but the settings' name/timezone/coordinates always win (first run
    AND fine-tuned coordinates with a stored path)."""
    from app.settings_dialog import SettingsDialog
    from config import defaults as d

    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    result = dialog.result_settings()
    dialog.done(0)
    assert result.city_name == d.DEFAULT_CITY["name"]
    assert result.timezone == d.DEFAULT_CITY["timezone"]
    assert result.latitude == d.DEFAULT_CITY["latitude"]
    assert result.longitude == d.DEFAULT_CITY["longitude"]


def test_every_theme_skeleton_is_complete():
    """Every theme folder ships all seven ENTITY-named files
    (placeholders until the owner pastes his vectors over them); the
    Norse diacritics fold to ASCII on disk (Sól -> Sol.png)."""
    from config import constants

    from config import paths as _paths

    for theme in constants.WEEKDAY_THEMES:
        if theme == "planets":
            continue
        folder = defaults.WEEKDAY_ART_DIR / defaults.WEEKDAY_THEME_DIRS[theme]
        for body in constants.WEEKDAY_BODIES:
            stem = defaults.WEEKDAY_THEME_FILES[theme][body]
            if not _paths.art_file(folder / f"{stem}.png").exists():
                # ONLY the Ancient set's Eleusis plate is pending
                # owner art (rework 2026-07-15) — that seat draws the
                # procedural disc until it lands.
                assert (theme, body) == ("religion_alt", "jupiter")
                continue


def test_hidden_mode_unlocks_the_four_greetings(app):
    """Owner 2026-07-14: typing the secret sequence on the focused
    dial unlocks the hidden extras — the Trinity topic gains the Four
    Greetings page (the owner's verses, SERBIAN in every language),
    locked dialogs never show it, and the unlock flag persists in
    settings."""
    from app.encyclopedia import EncyclopediaDialog

    locked = EncyclopediaDialog()
    assert len(locked._topics["trinity"]["entries"]) == 3
    locked.deleteLater()
    unlocked = EncyclopediaDialog(hidden_unlocked=True)
    entries = unlocked._topics["trinity"]["entries"]
    assert len(entries) == 4
    poem = entries[-1]
    assert poem["name"] == "Četiri pozdrava"
    assert poem["poem"] is True
    text = unlocked._article_text(poem["article"])
    assert "Dobar dan" in text and "ponovi sve ovo" in text
    assert "Krug pozdrava je krug ovog sata" in text
    unlocked._show_topic("trinity")
    unlocked._step(-1)                       # wrap onto the poem page
    assert unlocked._counter.text() == "4 / 4"
    unlocked.deleteLater()
    # SESSION-only (owner 2026-07-15): the unlock never persists —
    # the settings know nothing about it.
    assert not hasattr(Settings(), "hidden_unlocked")
    from config import constants

    assert len(constants.HIDDEN_MODE_SECRET) >= 3


def test_art_source_resolves_with_fallback():
    """Owner 2026-07-14: the Gemini and ChatGPT generations coexist
    under assets/<root>/<source>/ — canonical paths resolve into the
    active source, FALL BACK to the other where a file is missing
    (partial ChatGPT coverage), the emblem step-up lands under the
    REAL root, and settings validate the stored value."""
    from config import constants, paths

    canonical = defaults.WEEKDAY_ART_DIR / "greek/primary/Zeus.png"
    resolved = paths.art_file(canonical)
    assert "gemini" in resolved.parts and resolved.exists()
    stepup = paths.art_file(
        defaults.WEEKDAY_ART_DIR / "../emblem/virtue/Justice.png"
    )
    assert stepup.parts[-4:-2] == ("emblem", "gemini")
    assert stepup.exists()
    try:
        paths.set_art_source("chatgpt")
        wolf = paths.art_file(
            defaults.WEEKDAY_ART_DIR / "wolf/primary/alpha.png"
        )
        assert "chatgpt" in wolf.parts and wolf.exists()
        fallback = paths.art_file(canonical)     # no ChatGPT Greek yet
        assert "gemini" in fallback.parts and fallback.exists()
    finally:
        paths.set_art_source(constants.ART_SOURCE_DEFAULT)
    assert Settings().art_source == constants.ART_SOURCE_DEFAULT


def test_legend_off_silences_every_hover(app):
    """Owner spec: Legend off -> no hover anywhere (true zero-interaction
    dial together with click-through)."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import astral

    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository
    from render.assets import AssetCache
    from render.compositor import Compositor

    tz = ZoneInfo(defaults.DEFAULT_CITY["timezone"])
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=defaults.DEFAULT_CITY["latitude"],
        longitude=defaults.DEFAULT_CITY["longitude"],
    )
    day = build_day_context(
        now,
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    tick = build_tick_state(now, day)
    import dataclasses as dc

    silent_skin = dc.replace(
        defaults.DEFAULT_SKIN, legend=False, solar_rotation=False
    )
    compositor = Compositor(silent_skin, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    assert compositor.tooltip_at(180.0, 180.0 + orbit, 360.0) is None  # today body
    assert compositor.tooltip_at(180.0, 72.0, 360.0) is None           # arm
    assert compositor.tooltip_at(180.0, 40.0, 360.0) is None           # marker zone


def test_hexa_arm_hover_carries_the_sign_articles(app):
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import dataclasses as dc
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import astral

    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository
    from render.assets import AssetCache
    from render.compositor import Compositor

    tz = ZoneInfo(defaults.DEFAULT_CITY["timezone"])
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=defaults.DEFAULT_CITY["latitude"],
        longitude=defaults.DEFAULT_CITY["longitude"],
    )
    day = build_day_context(
        now,
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    tick = build_tick_state(now, day)
    skin = dc.replace(
        defaults.DEFAULT_SKIN, solar_rotation=False, weekday_theme="profession"
    )
    compositor = Compositor(skin, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    top = compositor.tooltip_at(180.0, 72.0, 360.0)      # top arm
    # Hover rework (owner 2026-07-13 round two): the diamond's TWO
    # signs stand side by side as columns — bold title with the span
    # in parentheses (no glyph), the colored logo, JUSTIFIED article
    # (base + the active palette paragraph).
    assert "Gemini" in top and "Cancer" in top
    assert "(21<sup>st</sup> May - 20<sup>th</sup> June)" in top
    assert "align='justify'" in top                      # article prose
    # The colored plate rides as the SCALED cache copy (performance
    # round 2026-07-13) — pin the exact resolved uri.
    from render.assets import scaled_variant_file

    gemini_uri = scaled_variant_file(
        defaults.ZODIAC_ART_DIR / "astrology" / "colored" / "Gemini.png",
        2 * defaults.ARTICLE_IMAGE_WIDTH_PX,
    ).as_uri()
    assert gemini_uri in top
    # Two WIDTH-DECLARED sign columns (the popup honors these cells).
    assert top.count(f"<td width='{defaults.ARTICLE_COLUMN_WIDTH_PX}'>") == 2
    assert "Castor" in top or "Pollux" in top            # Gemini article text


def test_symbolism_repository_covers_every_body_and_theme():
    from config import constants
    from data.symbolism import SymbolismRepository

    repo = SymbolismRepository()
    for body in constants.WEEKDAY_BODIES:
        blurbs = repo.arm_blurbs(body)
        for theme, key in constants.WEEKDAY_THEME_BLURBS.items():
            assert blurbs[key], (body, theme)


def test_articles_cover_every_theme_and_body():
    """Encyclopedic articles per theme x body: a multi-paragraph BASE
    (image-aware, canon-woven) plus one VARIANT paragraph per
    pointer/palette combination — including the trio. The alternate
    religion set is a FULL theme (Mithraism Sun, Druidism Mon,
    Zoroastrianism Tue, Shamanism Wed, Sikhism Thu, Babylon Fri,
    Voodoo Sat) whose entries also carry a display `name`."""
    import json

    from config import constants, paths

    data = json.loads(
        (paths.database_dir() / "symbolism.json").read_text(encoding="utf-8")
    )
    combos = {
        "hexa_paint", "hexa_light", "octa_paint", "octa_light", "cross", "trio",
    }
    for theme in constants.WEEKDAY_THEMES:
        article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
        for body in constants.WEEKDAY_BODIES:
            article = data["articles"][article_set][body]
            assert len(article["base"]) > 250, (theme, body)
            assert "\n\n" in article["base"], (theme, body)   # paragraphs
            assert set(article["variants"]) == combos, (theme, body)
    alternates = data["articles"]["religion_alt"]
    assert set(alternates) == set(constants.WEEKDAY_BODIES)
    for body, article in alternates.items():
        assert article["name"], body       # covered by the main loop above,
                                           # plus the display-name field


def test_encyclopedia_expansion_wiring():
    """Owner expansion 2026-07-13: the Encyclopedia opens THE CLOCK
    (Week day pages, Instrument articles) and THE INNER WHEEL
    (virtue/sin/mood emblems), the metal themes cycle four LOOKS, and
    every new article resolves from Database/encyclopedia.json."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog, _topics

    QApplication.instance() or QApplication([])
    topics = _topics()
    assert len(topics["week"]["entries"]) == 7
    assert len(topics["instrument"]["entries"]) == 8
    for family in ("virtues", "sins"):
        assert len(topics[family]["entries"]) == 8
    # Moods leads with the comparative WHEEL article and closes with
    # the 8+1 event mood (owner 2026-07-14).
    from config import paths as _paths

    moods = topics["moods"]["entries"]
    assert len(moods) == 10
    assert moods[0]["name"] == "The Wheel of Moods"
    assert _paths.art_file(moods[0]["images"][0]).exists()
    assert moods[-1]["name"] == "The Ninth Mood"
    assert _paths.art_file(moods[-1]["images"][0]).exists()
    # The metal themes cycle four looks, COLORED FIRST (owner default
    # 2026-07-13); the sun's two plates stand SIDE BY SIDE — Ruler
    # left, Servant right (owner correction 2026-07-13).
    greek_sun = topics["greek"]["entries"][0]
    assert [label for label, _ in greek_sun["looks"]] == [
        "Colored", "Bronze", "Gold", "Silver",
    ]
    assert all(
        len(rows) == 1 and len(rows[0]) == 2
        for _, rows in greek_sun["looks"]
    )
    # Chinese stays BRONZE-first; planets cycle photo/sign; astrology
    # leads with the logo+constellation pair.
    assert [l for l, _ in topics["chinese"]["entries"][0]["looks"]] == [
        "Bronze", "Gold", "Silver", "Colored",
    ]
    assert [l for l, _ in topics["planets"]["entries"][0]["looks"]] == [
        "Planets", "Signs", "Art",
    ]
    assert [l for l, _ in topics["astrology"]["entries"][0]["looks"]] == [
        "Logo & Constellation", "Colored", "Sign",
    ]
    # The Week pages group by kinship; Sunday STACKS each pair (owner
    # 2026-07-14: Ruler on top, its Servant directly UNDER, themes as
    # columns) — supersedes the 2026-07-13 one-row interleave.
    week_sun = topics["week"]["entries"][0]
    assert [l for l, _ in week_sun["looks"]] == [
        "Canon", "Gods", "Religions", "Themes", "Animals",
    ]
    canon_rows = week_sun["looks"][0][1]
    assert len(canon_rows) == 2
    assert len(canon_rows[0]) == 5 and len(canon_rows[1]) == 5
    gods_rows = week_sun["looks"][1][1]
    assert len(gods_rows) == 2                    # rulers over servants
    assert len(gods_rows[0]) == len(gods_rows[1]) == 4
    monday = topics["week"]["entries"][1]
    assert len(monday["looks"][0][1]) == 1        # single row off-Sunday
    # The animal societies are metal themes with the full four looks
    # and their own side-by-side Sunday pairs (owner 2026-07-13).
    for theme in ("wolf", "bee", "elephant"):
        entry = topics[theme]["entries"][0]
        assert [l for l, _ in entry["looks"]] == [
            "Colored", "Bronze", "Gold", "Silver",
        ], theme
        assert all(
            len(rows) == 1 and len(rows[0]) == 2
            for _, rows in entry["looks"]
        ), theme
    # The Two Triangles (owner 2026-07-13): the Judas–Lucifer scale —
    # three entries; the Union pairs both badges, articles resolve.
    duality = topics["duality"]["entries"]
    assert [e["name"] for e in duality] == ["Lucifer", "Judas", "The Union"]
    # The Union wears the owner's hexagram badge (2026-07-13).
    assert duality[2]["images"][0].name == "Union.png"
    assert _paths.art_file(duality[2]["images"][0]).exists()
    from data.encyclopedia import EncyclopediaRepository
    union = EncyclopediaRepository().entry("duality", "The Union")["base"]
    assert "hexagram" in union and "antidote" in union
    # The Seasons topic (badges + articles) and the trinity emblems.
    assert len(topics["seasons"]["entries"]) == 10
    met = topics["seasons"]["entries"][-1]
    assert len(met["images"]) == 4            # the four measured twins
    assert all(
        _paths.art_file(entry["images"][0]).exists()
        for entry in topics["trinity"]["entries"]
    )
    # The dialog renders every new topic without crashing and the
    # texts resolve (a Wednesday page must name its planet).
    dialog = EncyclopediaDialog()
    for key in (
        "week", "instrument", "seasons", "virtues", "sins", "moods",
        "greek", "wolf", "bee", "elephant",
    ):
        dialog._show_topic(key)
    assert "Mercury" in dialog._article_text(("week", "mercury"))
    assert "6°" in dialog._article_text(("instrument", "twilight"))
    assert dialog._article_text(("emblem", "virtues", "Justice"))
    assert "Goethe" in dialog._article_text(("season", "Spring"))
    # The topic SLIDER (owner plan round E, 2026-07-14): one entry per
    # page, ← / → wrap around like the Guide, the pager hides on the
    # gallery and the counter tracks the position.
    dialog._show_topic("greek")
    assert dialog._entry_index == 0
    assert dialog._counter.text() == "1 / 8"      # 7 bodies + Hades
    assert len(dialog._blocks) == 1
    dialog._step(-1)                              # wraps to the Ninth
    assert dialog._entry_index == 7
    assert dialog._counter.text() == "8 / 8"
    dialog._step(+1)
    assert dialog._entry_index == 0
    dialog._show_topics()
    assert dialog._back.isHidden() and dialog._next.isHidden()
    dialog.deleteLater()


def test_guide_pages_cover_every_slide_exactly_once():
    """The page structure covers each slide exactly once; every slide
    has a caption with a title line plus a body (owner content)."""
    import json

    from config import defaults as d

    slides = {path.stem for path in d.GUIDE_DIR.glob("*.png")}
    captions = json.loads(
        (d.GUIDE_DIR / "captions.json").read_text(encoding="utf-8")
    )
    pages = json.loads(
        (d.GUIDE_DIR / "pages.json").read_text(encoding="utf-8")
    )["pages"]
    paged = [stem for page in pages for stem in page["images"]]
    assert slides == set(captions) == set(paged)
    assert len(paged) == len(set(paged))          # no slide twice
    assert len(slides) >= 21
    for page in pages:
        assert page["title"].strip()
        assert page["columns"] in (1, 2)
    for stem, caption in captions.items():
        title, _, body = caption.partition("\n")
        assert title.strip() and len(body) > 100, stem


def test_legend_popup_caps_and_scrolls(app):
    """Owner spec: on small screens the legend must not clip — the popup
    caps its height to a screen fraction and grows a scrollbar for
    taller articles; short content sizes to itself."""
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QGuiApplication

    from app.legend_popup import LegendPopup

    popup = LegendPopup()
    popup.show_html("<div>one line</div>", QPoint(100, 100))
    short_height = popup.height()
    screen = QGuiApplication.primaryScreen().availableGeometry()
    assert short_height < screen.height() * 0.2
    tall = "<div align='left'>" + "line<br/>" * 400 + "</div>"
    popup.show_html(tall, QPoint(100, 100))
    assert popup.height() <= round(
        screen.height() * defaults.LEGEND_MAX_HEIGHT_FRACTION
    )
    assert popup._scroll.verticalScrollBar().maximum() > 0   # it scrolls
    # Owner regression 2026-07-13: justified prose must WRAP inside its
    # declared column — the label must never size to the UNWRAPPED
    # document (kilometer-wide paragraphs).
    prose = (
        f"<table><tr><td width='{defaults.ARTICLE_TEXT_WIDTH_PX}'>"
        "<p align='justify'>" + "word " * 400 + "</p></td></tr></table>"
    )
    popup.show_html(prose, QPoint(100, 100))
    assert popup._label.width() <= defaults.ARTICLE_TEXT_WIDTH_PX + 40
    assert popup._label.height() > 100                # it wrapped tall
    popup.dismiss()
    assert not popup.isVisible()


def test_chinese_articles_and_elements_cover_the_cycle():
    """12 animal articles (image-aware, two paragraphs) and one Wu Xing
    paragraph per element — together the sexagenary 60 (owner spec)."""
    import json

    from config import constants, paths

    data = json.loads(
        (paths.database_dir() / "symbolism.json").read_text(encoding="utf-8")
    )
    assert set(data["chinese_articles"]) == set(constants.CHINESE_ANIMALS)
    for animal, article in data["chinese_articles"].items():
        assert len(article["base"]) > 250, animal
        assert "\n\n" in article["base"], animal
    assert set(data["chinese_elements"]) == set(constants.CHINESE_ELEMENTS)
    for element, article in data["chinese_elements"].items():
        assert len(article["base"]) > 150, element


def test_zodiac_articles_cover_every_sign():
    """12 sign articles: a multi-paragraph base tied to the sign's hexa
    arm canon, plus paint and light palette variants — and, since the
    southern wheel seats every sign on the OPPOSITE arm (owner spec
    2026-07-12), a *_south pair with the color-borrowed reading."""
    import json

    from config import constants, paths

    data = json.loads(
        (paths.database_dir() / "symbolism.json").read_text(encoding="utf-8")
    )
    zodiac = data["zodiac_articles"]
    assert set(zodiac) == {name for name, _ in constants.ZODIAC_SIGNS}
    for sign, article in zodiac.items():
        assert len(article["base"]) > 250, sign
        assert "\n\n" in article["base"], sign
        assert set(article["variants"]) == {
            "paint", "light", "paint_south", "light_south",
        }, sign
        assert "South of the equator" in article["variants"]["paint_south"]


def test_custom_palette_reaches_the_render():
    custom = ("#111111", "#222222", "#333333", "#444444", "#555555", "#666666")
    settings = replace(Settings(), palettes={"hexa_paint": custom})
    skin = apply_display_settings(defaults.DEFAULT_SKIN, settings)
    assert palette_for(skin) == custom
    # A different pointer/style ignores this custom set.
    other = apply_display_settings(
        defaults.DEFAULT_SKIN, replace(settings, palette_style="light")
    )
    assert palette_for(other) == defaults.PALETTE_PRESETS[("hexa", "light")]
