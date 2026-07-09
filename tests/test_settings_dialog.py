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


def test_every_theme_skeleton_is_complete():
    """Every theme folder ships all seven ENTITY-named files
    (placeholders until the owner pastes his vectors over them); the
    Norse diacritics fold to ASCII on disk (Sól -> Sol.png)."""
    from config import constants

    for theme in constants.WEEKDAY_THEMES:
        if theme == "planets":
            continue
        folder = defaults.WEEKDAY_ART_DIR / theme
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


def test_hexa_arm_hover_appends_the_theme_blurb(app):
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
    top = compositor.tooltip_at(180.0, 72.0, 360.0)      # top arm = jupiter
    assert "Gemini" in top and "Cancer" in top           # the two signs stay
    assert "guru of the gods" in top                     # profession blurb below
    greek = Compositor(
        dc.replace(skin, weekday_theme="greek"), AssetCache()
    )
    greek.render_offscreen(360.0, 1.0, day, tick)
    top_greek = greek.tooltip_at(180.0, 72.0, 360.0)
    assert "Olympus" in top_greek                        # theme switches the text


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
    pointer/palette combination (religion variants arrive with the
    owner's preset decision)."""
    import json

    from config import constants, paths

    data = json.loads(
        (paths.database_dir() / "symbolism.json").read_text(encoding="utf-8")
    )
    combos = {"hexa_paint", "hexa_light", "octa_paint", "octa_light", "cross"}
    for theme in constants.WEEKDAY_THEMES:
        article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
        for body in constants.WEEKDAY_BODIES:
            article = data["articles"][article_set][body]
            assert len(article["base"]) > 250, (theme, body)
            if article_set != "religion":     # religion rewrite awaits the
                assert "\n\n" in article["base"], (theme, body)  # preset call
                assert set(article["variants"]) == combos, (theme, body)


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
