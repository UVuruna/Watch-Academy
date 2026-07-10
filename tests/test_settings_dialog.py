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
    assert greek.weekday_set.body_names["mercury"] == "Hermes"
    assert greek.weekday_set.bodies["mercury"].name == "Hermes.png"
    assert "greek" in str(greek.weekday_set.bodies["mercury"])
    assert all(path.exists() for path in greek.weekday_set.bodies.values())
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

    for theme in constants.WEEKDAY_THEMES:
        if theme == "planets":
            continue
        folder = defaults.WEEKDAY_ART_DIR / defaults.WEEKDAY_THEME_DIRS[theme]
        for body in constants.WEEKDAY_BODIES:
            stem = defaults.WEEKDAY_THEME_FILES[theme][body]
            assert (folder / f"{stem}.png").exists(), (theme, body)


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
    # Hover rework (owner spec): the diamond shows each of its TWO
    # signs as a header with the span in parentheses, followed by the
    # sign's LEFT-aligned article (base + the active palette paragraph).
    assert "Gemini" in top and "Cancer" in top
    assert "(21<sup>st</sup> May - 20<sup>th</sup> June)" in top
    assert "align='left'" in top                         # article prose
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
    religion set is a FULL theme (Egypt Sun, Druidism Mon,
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


def test_guide_slides_and_captions_match():
    """Every guide slide has a caption and every caption a slide; each
    caption carries a title line plus a body (owner content)."""
    import json

    from config import defaults as d

    slides = {path.stem for path in d.GUIDE_DIR.glob("*.png")}
    captions = json.loads(
        (d.GUIDE_DIR / "captions.json").read_text(encoding="utf-8")
    )
    assert slides == set(captions)
    assert len(slides) >= 21
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
    arm canon, plus paint and light palette variants (signs live on the
    hexa pointer only)."""
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
        assert set(article["variants"]) == {"paint", "light"}, sign


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
