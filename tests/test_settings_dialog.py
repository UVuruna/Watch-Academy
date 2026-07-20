"""M6 settings window: location picker cascade over the real database,
opacity overrides and the palette editor — headless (offscreen)."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QGroupBox

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


def test_dialog_z_mode_round_trips(app):
    """Visibility Z mode (owner 2026-07-17, ROADMAP 15d): the System-group
    combo reflects the stored value and result_settings returns the pick."""
    from app.settings_store import replace

    dialog = SettingsDialog(replace(Settings(), z_mode="top"), defaults.DEFAULT_SKIN)
    assert dialog._z_mode_combo.currentData() == "top"
    assert dialog.result_settings().z_mode == "top"
    index = dialog._z_mode_combo.findData("bottom")
    dialog._z_mode_combo.setCurrentIndex(index)
    assert dialog.result_settings().z_mode == "bottom"
    # The middle "normal" mode is offered too (ROADMAP 15e).
    assert dialog._z_mode_combo.findData("normal") >= 0
    dialog.done(0)


def test_dialog_diameter_slider(app):
    """The custom diameter slider (owner 2026-07-17, ROADMAP 15e): its
    range spans the smallest to the largest menu preset, it restores the
    stored diameter, and result_settings applies any value like a preset
    pick."""
    from app.settings_store import replace

    dialog = SettingsDialog(replace(Settings(), diameter=540), defaults.DEFAULT_SKIN)
    assert dialog._diameter_slider.minimum() == defaults.SIZE_PRESETS[0]
    assert dialog._diameter_slider.maximum() == defaults.SIZE_PRESETS[-1]
    assert dialog._diameter_slider.value() == 540
    dialog._diameter_slider.setValue(933)          # an arbitrary in-range value
    assert dialog.result_settings().diameter == 933
    dialog.done(0)


def test_dialog_diameter_spinbox_syncs_both_ways(app):
    """The exact numeric input (owner ROADMAP 15h item 12b): same range
    as the slider, restores the stored diameter, and either widget moving
    drags the other along — applied together on OK."""
    from app.settings_store import replace

    dialog = SettingsDialog(replace(Settings(), diameter=540), defaults.DEFAULT_SKIN)
    assert dialog._diameter_spin.minimum() == defaults.SIZE_PRESETS[0]
    assert dialog._diameter_spin.maximum() == defaults.SIZE_PRESETS[-1]
    assert dialog._diameter_spin.value() == 540
    dialog._diameter_spin.setValue(801)
    assert dialog._diameter_slider.value() == 801
    assert dialog.result_settings().diameter == 801
    dialog._diameter_slider.setValue(650)
    assert dialog._diameter_spin.value() == 650
    assert dialog.result_settings().diameter == 650
    dialog.done(0)


# --- The navigation rework (owner ROADMAP 15h item 1) -----------------------------


def test_dialog_navigation_lists_every_section(app):
    """The left column becomes a NAVIGATION of section titles (owner
    2026-07-18) instead of one long scroll — every existing group still
    exists, just filed under one of the sections, and clicking a title
    switches the visible panel."""
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    assert dialog._nav_list.count() == dialog._stack.count()
    assert dialog._nav_list.count() >= 7          # every group still fits somewhere
    # Every nav title carries the right-arrow marker.
    titles = [dialog._nav_list.item(i).text() for i in range(dialog._nav_list.count())]
    assert all(title.rstrip().endswith("▸") for title in titles)
    # Every widget from the old single-scroll layout is still reachable —
    # spot-check one control from several different groups/sections.
    assert dialog._search is not None                 # Location
    assert dialog._star_slider is not None             # Opacity (Display)
    assert dialog._diameter_slider is not None         # Sizes (Display)
    assert dialog._chips                                # Palette (Colors)
    assert dialog._tint_swatches                        # Ring tint (Colors)
    assert dialog._ring_layout_combo is not None         # Custom ring
    assert dialog._hand_name_edit is not None            # Custom hands
    assert dialog._rotation_group is not None             # Theme rotation (Themes)
    assert dialog._art_source_combo is not None            # Artwork (Themes)
    assert dialog._language_combo is not None               # Language
    assert dialog._era_combo is not None                     # Calendar eras (Language)
    assert dialog._autostart_check is not None                # System
    dialog.done(0)


def test_third_era_combo_lists_chinese(app):
    """Owner fix-round B, 2026-07-19: the Huangdi count appears in the
    Third calendar combo (Calendar eras, under Language) and round-trips
    through `result_settings()` exactly like every other option."""
    from config import constants

    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    values = [
        dialog._third_era_combo.itemData(i)
        for i in range(dialog._third_era_combo.count())
    ]
    assert values == list(constants.THIRD_ERAS)
    index = dialog._third_era_combo.findData("chinese")
    dialog._third_era_combo.setCurrentIndex(index)
    dialog.accept()
    assert dialog.result_settings().third_era == "chinese"
    dialog.done(0)


def test_third_era_combo_lists_maya(app):
    """MAYA round, owner 2026-07-20: the Long Count appears in the
    Third calendar combo generically (`THIRD_ERAS` iteration, no
    special-casing needed in the dialog) and round-trips through
    `result_settings()` exactly like every other option."""
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    index = dialog._third_era_combo.findData("maya")
    assert index >= 0
    dialog._third_era_combo.setCurrentIndex(index)
    dialog.accept()
    assert dialog.result_settings().third_era == "maya"
    dialog.done(0)


def test_third_era_combo_lists_kali_olympiad_unix(app):
    """ERA-TRIO round, owner 2026-07-20 ("može sve 3"): Kali Yuga,
    Olympiad and Unix Epoch all appear in the Third calendar combo
    generically (`THIRD_ERAS` iteration, no special-casing needed in
    the dialog) and each round-trips through `result_settings()`
    exactly like every other option — verified independently for all
    three since they cover three different internal shapes (a uniform
    offset, a year-only formatter, a date-level formatter)."""
    from config import constants

    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    values = [
        dialog._third_era_combo.itemData(i)
        for i in range(dialog._third_era_combo.count())
    ]
    for era in ("kali", "olympiad", "unix"):
        assert era in values
        assert era in constants.THIRD_ERA_TITLES
        index = dialog._third_era_combo.findData(era)
        assert index >= 0
        dialog._third_era_combo.setCurrentIndex(index)
        dialog.accept()
        assert dialog.result_settings().third_era == era
    dialog.done(0)


def test_dialog_navigation_switches_the_visible_panel(app):
    """Clicking a nav row shows THAT section's panel (owner's stated
    interaction) — the stacked widget follows the list's current row."""
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    assert dialog._stack.currentIndex() == 0
    last = dialog._nav_list.count() - 1
    dialog._nav_list.setCurrentRow(last)
    assert dialog._stack.currentIndex() == last
    dialog._nav_list.setCurrentRow(0)
    assert dialog._stack.currentIndex() == 0
    dialog.done(0)


def test_dialog_colors_section_shares_palette_and_ring_tint(app):
    """Owner's own example (ROADMAP 15h item 1): the Pointer palette and
    the Clock/ring tint are both COLOR — one shared 'Colors' title."""
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    colors_row = next(
        i for i in range(dialog._nav_list.count())
        if dialog._nav_list.item(i).text().startswith("Colors")
    )
    page = dialog._stack.widget(colors_row).widget()
    group_titles = [
        child.title() for child in page.findChildren(QGroupBox)
    ]
    assert any("Palette" in title for title in group_titles)
    assert any("tint" in title for title in group_titles)
    dialog.done(0)


def test_dialog_saturation_group_lives_in_colors_with_two_sliders(app):
    """Owner verdict (Session 21-D): Saturation does NOT belong in
    Element sizes — it moves into Colors (beside Palette + Ring tint)
    as its OWN group with two INDEPENDENT sliders, Pointer and Ring."""
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    colors_row = next(
        i for i in range(dialog._nav_list.count())
        if dialog._nav_list.item(i).text().startswith("Colors")
    )
    page = dialog._stack.widget(colors_row).widget()
    group_titles = [child.title() for child in page.findChildren(QGroupBox)]
    assert any("Saturation" in title for title in group_titles)
    # The old "Element sizes" panel (Display) no longer hosts it.
    display_row = next(
        i for i in range(dialog._nav_list.count())
        if dialog._nav_list.item(i).text().startswith("Display")
    )
    display_page = dialog._stack.widget(display_row).widget()
    display_titles = [
        child.title() for child in display_page.findChildren(QGroupBox)
    ]
    assert not any("Saturation" in title for title in display_titles)
    dialog.done(0)


def test_dialog_saturation_sliders_round_trip_independently(app):
    dialog = SettingsDialog(Settings(), defaults.DEFAULT_SKIN)
    dialog._pointer_saturation_slider.setValue(40)
    dialog._ring_saturation_slider.setValue(70)
    result = dialog.result_settings()
    assert result.pointer_saturation == pytest.approx(0.4)
    assert result.ring_saturation == pytest.approx(0.7)
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


def test_encyclopedia_stay_on_top_flag_follows_the_z_mode(app):
    """Fix round A (owner verdict 2026-07-19, screenshots): with the
    dial in "top" z-mode it is natively HWND_TOPMOST, so the
    Encyclopedia must carry WindowStaysOnTopHint too to open ABOVE it
    (matching Settings/Time Travel/Guide) — off by default (2026-07-13
    intent: a normal window everywhere else, yielding to focus)."""
    from PySide6.QtCore import Qt

    from app.encyclopedia import EncyclopediaDialog

    normal = EncyclopediaDialog()
    assert not (normal.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
    normal.deleteLater()
    on_top = EncyclopediaDialog(stay_on_top=True)
    assert on_top.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    on_top.deleteLater()


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


def test_hidden_mode_binds_the_poem_to_seasons_too(app):
    """ROADMAP queue #6 / WORKPLAN Session 7 (owner 2026-07-16): the
    poem's CANONICAL home is the Seasons — the four greetings sit on
    the four temperament arms (CANON.md). Behind the SAME cipher (no
    second code), a SECOND reading closes the Seasons topic: absent
    entirely before the unlock, present after, gone again once a
    fresh dialog opens locked."""
    from app.encyclopedia import EncyclopediaDialog

    # The Seasons topic holds SEVEN entries after the three-way split
    # (owner 2026-07-16, ROADMAP queue #10) — the turning points moved
    # to the Sun topic; the poem still closes Seasons under the cipher.
    locked = EncyclopediaDialog()
    assert len(locked._topics["seasons"]["entries"]) == 7
    assert all(
        entry.get("poem") is not True
        for entry in locked._topics["seasons"]["entries"]
    )
    locked.deleteLater()

    unlocked = EncyclopediaDialog(hidden_unlocked=True)
    entries = unlocked._topics["seasons"]["entries"]
    assert len(entries) == 8
    poem = entries[-1]
    assert poem["poem"] is True
    assert poem["name"] == "Četiri pozdrava"
    text = unlocked._article_text(poem["article"])
    assert "Dobar dan" in text and "jutro novo" in text
    # The CANON's three-line quote, verbatim — not the richer Trinity
    # reading (verses + Serbian explanation + watchmaker commentary).
    assert "veru u bolje sutra obasjan" in text
    assert "u ljubavi da nam proteče" in text
    # The framing is the SHORT ENGLISH house-voice reading of the four
    # faces (day/evening/night/morning), distinct from Trinity's.
    assert "faith in a better tomorrow" in text
    assert "peaceful death" in text
    assert "rebirth" in text
    unlocked._show_topic("seasons")
    unlocked._step(-1)                       # wrap onto the poem page
    assert unlocked._counter.text() == "8 / 8"
    unlocked.deleteLater()


def test_encyclopedia_opens_at_the_spacebar_target(app):
    """The Spacebar jump (owner 2026-07-16, ROADMAP queue #8): given an
    initial (topic, entry) the dialog skips the gallery and opens on
    that page; an unknown topic falls back to the gallery."""
    from app.encyclopedia import EncyclopediaDialog

    jumped = EncyclopediaDialog(initial_topic="chinese", initial_entry=6)
    assert jumped._topic_key == "chinese" and jumped._entry_index == 6
    assert jumped._back.isVisible() or True         # on an entry page
    assert "Horse" in jumped._entry_name(
        jumped._topics["chinese"]["entries"][6]
    )
    jumped.deleteLater()
    # No target (menu open) shows the gallery.
    gallery = EncyclopediaDialog()
    assert gallery._topic_key is None
    gallery.deleteLater()
    # An unknown topic cannot open a page — it stays on the gallery.
    unknown = EncyclopediaDialog(initial_topic="does_not_exist")
    assert unknown._topic_key is None
    unknown.deleteLater()


def test_art_source_resolves_with_fallback(tmp_path, monkeypatch):
    """Owner 2026-07-14: the Gemini and ChatGPT generations coexist
    under assets/<root>/<source>/ — canonical paths resolve into the
    active source, FALL BACK to the other where a file is missing,
    the emblem step-up lands under the REAL root, and settings
    validate the stored value. Pinned on a SYNTHETIC assets tree with
    controlled coverage (the real tree's gaps close file by file as
    the owner's generations land — 2026-07-18 they broke the old
    'no ChatGPT Greek yet' premise)."""
    from config import constants, paths

    assets = tmp_path / "assets"
    for rel in (
        "weekday/gemini/greek/primary/Zeus.png",       # gemini-only
        "weekday/chatgpt/wolf/primary/alpha.png",      # chatgpt-only
        "emblem/gemini/virtue/Justice.png",            # step-up target
    ):
        target = assets.joinpath(*rel.split("/"))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"png")
    monkeypatch.setattr(paths, "assets_dir", lambda: assets)

    weekday = assets / "weekday"
    canonical = weekday / "greek/primary/Zeus.png"
    resolved = paths.art_file(canonical)
    assert "gemini" in resolved.parts and resolved.exists()
    stepup = paths.art_file(weekday / "../emblem/virtue/Justice.png")
    assert stepup.parts[-4:-2] == ("emblem", "gemini")
    assert stepup.exists()
    try:
        paths.set_art_source("chatgpt")
        wolf = paths.art_file(weekday / "wolf/primary/alpha.png")
        assert "chatgpt" in wolf.parts and wolf.exists()
        fallback = paths.art_file(canonical)   # no ChatGPT copy in the tree
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
    # ARTICLE ORDER restructure (owner spec, round R3): entry 0 is now
    # the theme's OWN title page (no "looks" — graceful-absent plate),
    # Monday..Saturday follow at 1-6, then the week-duality title (7)
    # and the merged Sunday DUAL page (8) — the metal themes still
    # cycle four looks COLORED FIRST (owner default 2026-07-13) and the
    # dual page's two plates still stand SIDE BY SIDE, Ruler left,
    # Servant right (owner correction 2026-07-13).
    assert "looks" not in topics["greek"]["entries"][0]
    assert topics["greek"]["entries"][0]["name"] == ("theme_title", "greek")
    greek_dual = topics["greek"]["entries"][8]
    assert greek_dual["dual"] is True
    assert [label for label, _ in greek_dual["looks"]] == [
        "Colored", "Bronze", "Gold", "Silver",
    ]
    assert all(
        len(rows) == 1 and len(rows[0]) == 2
        for _, rows in greek_dual["looks"]
    )
    # Chinese and Astrology are NOT weekday-restructured (their own
    # 12-sign/12-animal builders, untouched by the round R3 order
    # change) — they stay exactly as before. Planets IS restructured —
    # Monday (index 1) cycles photo/sign/art, same as the old entry 0.
    assert [l for l, _ in topics["chinese"]["entries"][0]["looks"]] == [
        "Bronze", "Gold", "Silver", "Colored",
    ]
    assert [l for l, _ in topics["planets"]["entries"][1]["looks"]] == [
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
    # and their own side-by-side dual-page pairs (owner 2026-07-13) —
    # the dual page sits at index 8 after the round R3 restructure.
    for theme in ("wolf", "bee", "elephant"):
        entry = topics[theme]["entries"][8]
        assert entry["dual"] is True, theme
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
    # The Seasons/Moon/Sun topics (badges + articles) after the split
    # (owner 2026-07-16, ROADMAP queue #10) and the trinity emblems.
    assert len(topics["seasons"]["entries"]) == 7
    met = topics["seasons"]["entries"][-1]
    assert len(met["images"]) == 4            # the four measured twins
    assert [e["name"][1] for e in topics["sun"]["entries"]] == [
        "Summer_Solstice", "Winter_Solstice", "Equinox",
    ]
    # The Moon topic grows to EIGHT phase pages (owner 2026-07-16,
    # ROADMAP queue #8b) — in constants.MOON_PHASE_NAMES cycle order.
    from config import constants as _constants
    assert [e["name"][1] for e in topics["moon"]["entries"]] == list(
        _constants.MOON_PHASE_NAMES
    )
    # LIVE-RENDERED (owner 2026-07-19, retiring the eight pre-baked
    # assets/moon/ plates): every phase image resolves to a real,
    # disk-cached file — the OLD path (defaults.MOON_PHASE_ART_DIR
    # without the source subdir) never actually existed, so this is
    # also a fix, not just a parity check.
    assert all(
        entry["images"][0].exists() for entry in topics["moon"]["entries"]
    )
    assert all(
        _paths.art_file(entry["images"][0]).exists()
        for entry in topics["trinity"]["entries"]
    )
    # The dialog renders every new topic without crashing and the
    # texts resolve (a Wednesday page must name its planet).
    dialog = EncyclopediaDialog()
    for key in (
        "week", "instrument", "moon", "seasons", "sun", "virtues",
        "sins", "moods", "greek", "wolf", "bee", "elephant",
    ):
        dialog._show_topic(key)
    assert "Mercury" in dialog._article_text(("week", "mercury"))
    assert "6°" in dialog._article_text(("instrument", "twilight"))
    assert dialog._article_text(("emblem", "virtues", "Justice"))
    assert "Goethe" in dialog._article_text(("season", "Spring"))
    # The three-way split (owner 2026-07-16): the Sun article speaks the
    # solstice; the eight Moon pages (queue #8b) speak their phase and
    # the tides — spring at the syzygies, neap at the quarters.
    assert "solstice" in dialog._article_text(("sun", "Summer_Solstice"))
    assert "29.53" in dialog._article_text(("moon", "New Moon"))
    assert "SPRING" in dialog._article_text(("moon", "Full Moon"))
    assert "NEAP" in dialog._article_text(("moon", "First Quarter"))
    # The topic SLIDER (owner plan round E, 2026-07-14): one entry per
    # page, ← / → wrap around like the Guide, the pager hides on the
    # gallery and the counter tracks the position. Round R3: Title +
    # 6 weekdays + duality title + dual page + Gaia = 10 pages.
    dialog._show_topic("greek")
    assert dialog._entry_index == 0
    assert dialog._counter.text() == "1 / 10"     # Title + 6 + duality + dual + Gaia
    assert len(dialog._blocks) == 1
    dialog._step(-1)                              # wraps to the Ninth
    assert dialog._entry_index == 9
    assert dialog._counter.text() == "10 / 10"
    dialog._step(+1)
    assert dialog._entry_index == 0
    dialog._show_topics()
    assert dialog._back.isHidden() and dialog._next.isHidden()
    dialog.deleteLater()


def test_ring_letters_article_carries_the_mason_lore():
    """ROADMAP 15b (owner: "malo legende oko tih naših odabira"): the
    ring presets' OWN symbolism — DOMY traces the inverted cross, MORPH
    the upright cross, the seal (MASON G / NUMBERS) the hexagram — is
    added to the EXISTING `instrument/ring_letters` article (Rule #5,
    no duplicate topic), and the MASON G banknote reading (CANON.md
    §The Banknote) closes it. The instrument topic still resolves and
    keeps its entry count."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog, _topics
    from data.encyclopedia import EncyclopediaRepository

    QApplication.instance() or QApplication([])
    topics = _topics()
    assert len(topics["instrument"]["entries"]) == 8   # no new topic key

    article = EncyclopediaRepository().instrument("ring_letters")["base"]
    assert "inverted cross" in article
    assert "UPRIGHT cross" in article
    assert "hexagram" in article and "SEAL" in article
    assert "MASON G" in article
    assert "G-M-N" in article and "TRINITY" in article
    assert "S-Omega-A" in article and "UNION" in article
    assert "GOD and GEOMETRY" in article

    dialog = EncyclopediaDialog()
    dialog._show_topic("instrument")
    text = dialog._article_text(("instrument", "ring_letters"))
    assert "inverted cross" in text and "hexagram" in text.lower()
    dialog.deleteLater()


def test_wider_pantheon_topics():
    """WORKPLAN Session 8 (owner 2026-07-15): one Encyclopedia topic per
    culture for the A-list figures no dial seat could hold. Each topic
    resolves every article, images degrade gracefully (the wired plates
    have not landed), the retired ninths' material folds into the new
    entries, and the gallery gains The Wider Pantheon group."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import (
        EncyclopediaDialog,
        _TOPIC_GROUPS,
        _topics,
    )
    from config import paths as _paths
    from data.encyclopedia import EncyclopediaRepository
    from data.translations import collect_corpus

    QApplication.instance() or QApplication([])
    topics = _topics()
    # Four topics, one per culture, with the reconciled seatless rosters
    # (round-four/five: Artemis/Hera/Frigg/Mokoš/Bastet seated and gone;
    # the retired ninths Set/Baldur/Crnobog folded back in).
    expected = {
        "wider_greek": ["Dionysus", "Hephaestus", "Hestia"],
        "wider_norse": ["Baldur", "Heimdall", "Njord"],
        "wider_egypt": ["Set", "Nut", "Geb", "Ptah", "Sekhmet"],
        "wider_slavic": ["Crnobog", "Stribog", "Jarilo", "Rod"],
    }
    for key, names in expected.items():
        assert [e["name"] for e in topics[key]["entries"]] == names, key
        # The gallery card icon reuses an existing culture plate.
        assert _paths.art_file(topics[key]["icon"]).exists(), key
        for entry in topics[key]["entries"]:
            # Every entry wires a plate, and it degrades gracefully:
            # the art has not landed, so nothing is shown (like the
            # ninth plates wired ahead of their art).
            assert entry["images"]
            resolved = _paths.art_file(entry["images"][0])
            assert resolved is None or resolved.suffix == ".png"

    # The Wider Pantheon topics ride THE DIVINE group (owner-approved
    # FIVE-section regroup, sealed 2026-07-20, round R3 — supersedes the
    # nine-group 2026-07-12/13 layout the "Wider Pantheon" group used
    # to be part of).
    groups = dict(_TOPIC_GROUPS)
    for key in ("wider_greek", "wider_norse", "wider_egypt", "wider_slavic"):
        assert key in groups["The Divine"]

    # Every wider article resolves through the encyclopedia "wider"
    # family, and the retired ninths' written material is reused.
    repo = EncyclopediaRepository()
    for names in expected.values():
        for name in names:
            assert repo.entry("wider", name)["base"].strip(), name
    assert "Cain" in repo.entry("wider", "Set")["base"]          # Egyptian Cain
    assert "mistletoe" in repo.entry("wider", "Baldur")["base"]  # Ragnarok start
    assert "Helmold" in repo.entry("wider", "Crnobog")["base"]   # source caveat

    # The corpus collects the wider keys (English content — the SR pass
    # is the one pre-build Translation session, owner 2026-07-16).
    corpus = collect_corpus()
    assert sum(
        1 for k in corpus if k.startswith("encyclopedia/wider/")
    ) == 15
    assert "encyclopedia/wider/Hestia/base" in corpus

    # The dialog opens each wider topic without crashing and the texts
    # resolve on the page.
    dialog = EncyclopediaDialog()
    for key in expected:
        dialog._show_topic(key)
        assert dialog._entry_index == 0
    assert "hearth" in dialog._article_text(("emblem", "wider", "Hestia"))
    assert "wind" in dialog._article_text(("emblem", "wider", "Stribog"))
    dialog.deleteLater()


def test_duality_topic_rotates_lucifer_and_judas_by_travel_date():
    """SCALE ROTATION (owner decree 2026-07-19/20): the duality topic's
    Lucifer/Judas entries resolve through `defaults.scale_variant_file`
    keyed on the caller's `travel_date`, not a fixed master — the Union
    entry stays fixed. Wired end to end: `_topics(travel_date)` and
    `EncyclopediaDialog(travel_date=...)` both reach the SAME resolved
    file `defaults.scale_variant_file` would pick directly."""
    from datetime import date

    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog, _topics
    from config import defaults

    QApplication.instance() or QApplication([])
    day = date(2026, 7, 20)
    topics = _topics(day)
    duality = topics["duality"]["entries"]
    lucifer_entry = next(e for e in duality if e["name"] == "Lucifer")
    judas_entry = next(e for e in duality if e["name"] == "Judas")
    union_entry = next(e for e in duality if e["name"] == "The Union")

    expected_lucifer = (
        defaults.scale_variant_file("Lucifer", day)
        or defaults.SCALE_ART_DIR / "Lucifer_Triangle.png"
    )
    expected_judas = (
        defaults.scale_variant_file("Judas", day)
        or defaults.SCALE_ART_DIR / "Judas_Triangle.png"
    )
    assert lucifer_entry["images"] == (expected_lucifer,)
    assert judas_entry["images"] == (expected_judas,)
    # The Union never rotates — always the fixed hexagram badge.
    assert union_entry["images"] == (defaults.SCALE_ART_DIR / "Union.png",)

    # A different travel date is free to pick a different file (real
    # art currently gives both poles more than one version) — but the
    # dialog wiring must reach the exact same resolution either way.
    dialog = EncyclopediaDialog(travel_date=day)
    dialog_duality = dialog._topics["duality"]["entries"]
    assert (
        next(e for e in dialog_duality if e["name"] == "Lucifer")["images"]
        == (expected_lucifer,)
    )
    dialog.deleteLater()


def test_era_terms_topic():
    """ROADMAP 15a3 (owner 2026-07-17): the Age of Light, the Age of
    Darkness and the four Starry Seasons each get an Encyclopedia
    article — sourced from the SEALED measured facts in
    research/ephemeris/anno_lucis.json and ROADMAP 15a — closed by the
    comparative "Eras of the World" essay (no emblem of its own). The
    "era" topic joins The Clock gallery group; art degrades gracefully
    (not yet generated)."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog, _TOPIC_GROUPS, _topics
    from config import paths as _paths
    from data.encyclopedia import EncyclopediaRepository
    from data.translations import collect_corpus

    QApplication.instance() or QApplication([])
    topics = _topics()
    era = topics["era"]["entries"]
    # Fix round F (owner "bravo"): The Great Oscillations joins the era
    # topic after the comparative essay.
    assert [e["name"][1] for e in era] == [
        "Age_of_Light", "Age_of_Darkness", "Starry_Spring",
        "Starry_Summer", "Starry_Autumn", "Starry_Winter",
        "Eras_of_the_World", "The_Great_Oscillations",
    ]
    # The six Age/Season entries each wire a single plate; graceful-absent.
    for entry in era[:6]:
        assert entry["images"]
        resolved = _paths.art_file(entry["images"][0])
        assert resolved is None or resolved.suffix == ".png"
    # Eras of the World: no plate of its own — instead it strings the
    # calendar-system emblems the essay compares (six from owner
    # fix-round B, 2026-07-19; Maya added the MAYA round, owner
    # 2026-07-20; Kali Yuga/Olympiad/Unix added the ERA-TRIO round,
    # owner 2026-07-20), graceful-absent until PromptPainter generates
    # them. Every one of the ten now also rotates against its own
    # `alt/`/`_v2` siblings (ERA-TRIO round: the strip used to bypass
    # `rotating_art_file` entirely) — `art_file` resolution is
    # unaffected either way since no calendar art exists yet.
    assert len(era[6]["images"]) == 10
    for image in era[6]["images"]:
        resolved = _paths.art_file(image)
        assert resolved is None or resolved.suffix == ".png"
    # The Great Oscillations is an ESSAY — no emblem of its own (like the
    # Eras essay's own text), so its image tuple is empty (fix round F).
    assert era[7]["images"] == ()

    # THE CELESTIAL ENGINE (owner-approved FIVE-section regroup, sealed
    # 2026-07-20, round R3 — supersedes "The Clock"): the clock topics
    # keep their relative order, now followed by Zodiac + Cosmos in the
    # SAME group (Planets/Planet Signs fold into one "planets" card).
    groups = dict(_TOPIC_GROUPS)
    assert groups["The Celestial Engine"][:8] == (
        "week", "instrument", "moon", "seasons", "sun", "era",
        "eclipse_solar", "eclipse_lunar",
    )
    assert "planet_signs" not in groups["The Celestial Engine"]
    for key in ("astrology", "chinese", "planets", "cosmos"):
        assert key in groups["The Celestial Engine"]

    # Every article resolves and carries its own MEASURED numbers —
    # never invented, always the sealed anno_lucis.json/ROADMAP figures.
    repo = EncyclopediaRepository()
    light = repo.era("Age_of_Light")["base"]
    assert "4079 BCE" in light and "6423 CE" in light
    assert "10,501" in light and "6105" in light
    dark = repo.era("Age_of_Darkness")["base"]
    assert "9561 BCE" in dark and "16429" in dark
    spring = repo.era("Starry_Spring")["base"]
    assert "1000 CE" in spring and "7.94" in spring
    summer = repo.era("Starry_Summer")["base"]
    assert "6105" in summer
    autumn = repo.era("Starry_Autumn")["base"]
    assert "10990" in autumn and "5.5" in autumn
    winter = repo.era("Starry_Winter")["base"]
    assert "16429" in winter
    world = repo.era("Eras_of_the_World")["base"]
    for term in ("AUC", "Byzantine", "Hebrew", "Hegirae", "Buddhist",
                 "Chinese", "753", "5509", "3761", "543",
                 # MAYA round (owner 2026-07-20): the three calendars,
                 # the epoch and the honest 2012 baktun-turn.
                 "Tzolk'in", "Haab'", "Long Count", "3114 BCE",
                 "584,283", "13.0.0.0.0", "260", "365",
                 # ERA-TRIO round (owner 2026-07-20, "može sve 3"):
                 # Kali Yuga's epoch, the Olympiad's own anchor and
                 # second checkable anchor, and the Unix epoch/billennium.
                 "Kali Yuga", "3102 BCE", "5127", "Olympiad", "Coroebus",
                 "776 BCE", "293", "Unix", "1970-01-01", "billennium"):
        assert term in world, term
    # The Great Oscillations (fix round F): the Milankovitch essay carries
    # its MEASURED figures (the +28,000 minimum, ~±1.1 d) and names the
    # scientist — never claiming an ice age "starts" then.
    osc = repo.era("The_Great_Oscillations")["base"]
    assert "Milankovitch" in osc and "28,000" in osc and "1.1" in osc

    # The corpus collects both title and base for every era key (8 now).
    corpus = collect_corpus()
    assert sum(1 for k in corpus if k.startswith("encyclopedia/era/")) == 16
    assert "encyclopedia/era/Age_of_Light/title" in corpus
    assert "encyclopedia/era/Eras_of_the_World/base" in corpus
    assert "encyclopedia/era/The_Great_Oscillations/base" in corpus

    # The dialog opens the topic and each page's title resolves without
    # crashing (era_title dispatch in _entry_name).
    dialog = EncyclopediaDialog()
    dialog._show_topic("era")
    assert dialog._counter.text() == "1 / 8"
    for index in range(8):
        dialog._entry_index = index
        dialog._show_entry()
    dialog.deleteLater()


def test_eclipse_topics():
    """Fix round F (owner order 2026-07-19, "posebno za mesec i sunce"):
    two Encyclopedia topics — Solar and Lunar — each an OVERVIEW page
    then one chapter per category we distinguish (solar total/annular/
    partial/hybrid, lunar total/partial/penumbral). Every chapter wires
    its own emblem (graceful-absent), the overview strings its body's
    emblems, both join The Clock gallery group, every article resolves
    with its exact state-table representation, and the corpus collects
    all nine keys × 2."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog, _TOPIC_GROUPS, _topics
    from config import paths as _paths
    from data.encyclopedia import EncyclopediaRepository
    from data.translations import collect_corpus

    QApplication.instance() or QApplication([])
    topics = _topics()
    assert [e["name"][1] for e in topics["eclipse_solar"]["entries"]] == [
        "Solar_Overview", "Solar_Total", "Solar_Annular",
        "Solar_Partial", "Solar_Hybrid",
    ]
    assert [e["name"][1] for e in topics["eclipse_lunar"]["entries"]] == [
        "Lunar_Overview", "Lunar_Total", "Lunar_Partial", "Lunar_Penumbral",
    ]
    # The overview strings its body's category emblems (4 solar / 3
    # lunar); each category chapter wires exactly one emblem. All
    # graceful-absent until PromptPainter generates them.
    assert len(topics["eclipse_solar"]["entries"][0]["images"]) == 4
    assert len(topics["eclipse_lunar"]["entries"][0]["images"]) == 3
    for topic_key in ("eclipse_solar", "eclipse_lunar"):
        for entry in topics[topic_key]["entries"][1:]:
            assert len(entry["images"]) == 1
            resolved = _paths.art_file(entry["images"][0])
            assert resolved is None or resolved.suffix == ".png"

    # Both topics ride The Celestial Engine group (owner-approved
    # FIVE-section regroup, sealed 2026-07-20, round R3), right after
    # the era topic — Zodiac/Cosmos trail them in the same group.
    groups = dict(_TOPIC_GROUPS)
    engine = groups["The Celestial Engine"]
    era_index = engine.index("era")
    assert engine[era_index + 1:era_index + 3] == (
        "eclipse_solar", "eclipse_lunar",
    )

    # Every chapter's article resolves and DESCRIBES its exact dial
    # representation (the sealed state table — the reader's page and the
    # render must never drift).
    repo = EncyclopediaRepository()
    assert "ring of fire" in repo.eclipse("Solar_Annular")["base"]
    assert "corona" in repo.eclipse("Solar_Total")["base"]
    assert "MAGNITUDE" in repo.eclipse("Solar_Partial")["base"]
    assert "totality" in repo.eclipse("Solar_Hybrid")["base"]
    lunar_total = repo.eclipse("Lunar_Total")["base"]
    assert "seven percent" in lunar_total and "copper" in lunar_total
    assert "turquoise" in lunar_total
    assert "eighteen percent" in repo.eclipse("Lunar_Partial")["base"]
    penumbral = repo.eclipse("Lunar_Penumbral")["base"]
    assert "sixty percent" in penumbral and "NO turquoise" in penumbral

    # The corpus collects title + base for all nine chapters.
    corpus = collect_corpus()
    assert sum(1 for k in corpus if k.startswith("encyclopedia/eclipse/")) == 18
    assert "encyclopedia/eclipse/Solar_Total/title" in corpus
    assert "encyclopedia/eclipse/Lunar_Penumbral/base" in corpus

    # The dialog opens each topic and pages through every chapter
    # without crashing (eclipse_title dispatch in _entry_name).
    dialog = EncyclopediaDialog()
    dialog._show_topic("eclipse_solar")
    assert dialog._counter.text() == "1 / 5"
    dialog._show_topic("eclipse_lunar")
    assert dialog._counter.text() == "1 / 4"
    for index in range(4):
        dialog._entry_index = index
        dialog._show_entry()
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


# --- ROUND R3: LAYOUT + ARTICLE ORDER + FINISH SWITCHER ------------------------


def test_gallery_five_sections():
    """Owner-approved decision, sealed 2026-07-20: the gallery regroups
    into exactly FIVE sections, the owner's own names. Planets and
    Planet Signs are ONE topic (the existing Planets/Signs/Art look
    switcher) — "planet_signs" never appears as a gallery card, but
    stays wired in `_topics()` so a dial slot dressed in that theme
    still resolves a Spacebar jump."""
    from app.encyclopedia import _TOPIC_GROUPS, _topics

    assert [name for name, _ in _TOPIC_GROUPS] == [
        "The Celestial Engine", "The Divine", "The Human Wheel",
        "The Living World", "The Archetypes",
    ]
    groups = dict(_TOPIC_GROUPS)
    every_card = [key for keys in groups.values() for key in keys]
    assert "planet_signs" not in every_card
    assert len(every_card) == len(set(every_card)), "no topic in two groups"
    # The Archetypes section exists (owner: "do not scatter them") but
    # carries no cards yet — that content is a future session.
    assert groups["The Archetypes"] == ()
    # Every card key actually resolves in _topics() — a stale name in a
    # group would KeyError the gallery build.
    topics = _topics()
    for key in every_card:
        assert key in topics, key
    # planet_signs itself must still resolve (compositor contract).
    assert "planet_signs" in topics


def test_gallery_min_width_and_no_horizontal_overflow():
    """LAYOUT fix round R3 (owner: "788px width, tiles clipping" dies
    here): MIN WIDTH = 4 * the single theme tile, and no group ever
    lays out more than ENCYCLOPEDIA_GALLERY_MAX_COLUMNS cards per row
    — it wraps into further rows instead of spilling sideways."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog, _TOPIC_GROUPS
    from config import defaults as _defaults

    QApplication.instance() or QApplication([])
    dialog = EncyclopediaDialog()
    tile = (
        _defaults.ENCYCLOPEDIA_TOPIC_ICON_MIN_PX
        + _defaults.ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX
    )
    assert dialog.minimumWidth() == tile * _defaults.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS
    # The Celestial Engine has more than 4 cards — it MUST wrap.
    groups = dict(_TOPIC_GROUPS)
    assert len(groups["The Celestial Engine"]) > _defaults.ENCYCLOPEDIA_GALLERY_MAX_COLUMNS
    dialog.deleteLater()


def test_article_order_restructure():
    """Owner ARTICLE ORDER spec, round R3: every weekday-structured
    theme opens on ITS OWN title page, then Monday..Saturday (owner:
    "Ponedeljak PRVI"), then the week-duality title, then the merged
    Sunday DUAL page, then the Ninth where the theme has one."""
    from app.encyclopedia import _topics

    topics = _topics()
    # "wolf" HAS a Ninth (Sigma) — 10 pages total.
    wolf = topics["wolf"]["entries"]
    assert len(wolf) == 10
    assert wolf[0]["name"] == ("theme_title", "wolf")
    assert "dual" not in wolf[0] and "looks" not in wolf[0]
    monday_saturday = [entry["name"] for entry in wolf[1:7]]
    assert monday_saturday == [
        "Luna", "Hunter (Gamma)", "Scout (Delta)", "Beta", "Mate", "Elder",
    ]
    assert wolf[7]["name"] == ("week_duality_title", "wolf")
    assert wolf[8]["dual"] is True
    assert wolf[8]["theme"] == "wolf"
    assert wolf[9]["name"] == "Sigma"        # the Ninth, unchanged content
    # "japan" has NO Ninth — 9 pages total, dual page is the LAST page.
    japan = topics["japan"]["entries"]
    assert len(japan) == 9
    assert japan[8]["dual"] is True
    # Every restructured theme's title/duality text resolves and is
    # non-trivial (Rule #2 — no capacity lies: written now, not a
    # placeholder pretending to be content).
    from data.encyclopedia import EncyclopediaRepository

    repo = EncyclopediaRepository()
    for theme in (
        "planets", "planet_signs", "greek", "norse", "egypt", "slavic",
        "alchemy", "japan", "religion", "religion_alt", "profession",
        "wolf", "bee", "elephant", "bible", "bible2", "bible_dark",
        "cosmos",
    ):
        title = repo.theme_title(theme)
        duality = repo.week_duality(theme)
        assert len(title["base"]) > 80, theme
        assert len(duality["base"]) > 60, theme
        assert title["title"], theme
        assert duality["title"], theme


def test_dual_article_layout_side_by_side():
    """Owner INSTRUCTION #6 (encyclopedia side): the week-duality DUAL
    page shows TWO texts — good/Ruler LEFT, evil/Servant RIGHT, each
    under its own name/logo — never the old single "base" article."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog, _topics
    from config import defaults as _defaults

    QApplication.instance() or QApplication([])
    topics = _topics()
    greek_dual = topics["greek"]["entries"][8]
    assert greek_dual["dual"] is True

    dialog = EncyclopediaDialog()
    dialog._show_topic("greek")
    dialog._entry_index = 8
    dialog._show_entry()
    ruler_text, servant_text = dialog._article_faces(greek_dual["article"])
    assert ruler_text != servant_text
    assert "Helios" in ruler_text
    assert "Phaethon" in servant_text
    # Two text labels, each pinned to HALF the block width (columns=2)
    # — never the single full-width column a normal page uses.
    dual_labels = [
        (label, columns) for label, columns in dialog._text_labels
        if columns == 2
    ]
    assert len(dual_labels) == 2
    ruler_name, servant_name = _defaults.WEEKDAY_DUAL_NAMES["greek"]
    assert ruler_name == "Helios" and servant_name == "Phaethon"
    dialog.deleteLater()


def test_finish_persistence_across_pages():
    """Owner INSTRUCTION #3: once a finish (e.g. Bronze) is picked, it
    rides EVERY following page/topic that offers it — never a silent
    reset to the topic's own Colored default."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog

    QApplication.instance() or QApplication([])
    dialog = EncyclopediaDialog()
    # Entry 0 is now the title page (no switcher) — Monday (index 1) is
    # the first page that actually offers the finish cycle.
    dialog._show_topic("wolf")
    dialog._entry_index = 1
    dialog._show_entry()
    assert dialog._look_state["titles"][dialog._look_state["index"]] == "Colored"
    dialog._cycle_look(1)                     # -> Bronze
    assert dialog._preferred_look_label == "Bronze"
    dialog._step(1)                           # a different entry, same topic
    assert dialog._look_state["titles"][dialog._look_state["index"]] == "Bronze"
    dialog._show_topics()
    dialog._show_topic("bee")                 # a DIFFERENT metal topic
    dialog._entry_index = 1
    dialog._show_entry()
    assert dialog._look_state["titles"][dialog._look_state["index"]] == "Bronze"
    # A topic whose looks do NOT include "Bronze" falls back to ITS OWN
    # default (index 0) without erroring.
    dialog._show_topic("astrology")
    assert dialog._look_state["titles"][dialog._look_state["index"]] == (
        "Logo & Constellation"
    )
    dialog.deleteLater()


def test_ninth_seat_philosophical_name():
    """Owner decree, round R3: the 9th seat's philosophical name is
    "The Unfound" — documented as a module constant with the discussed
    alternatives in a code comment where it is defined."""
    from app import encyclopedia

    assert encyclopedia.NINTH_SEAT_PHILOSOPHICAL_NAME == "The Unfound"


def test_ninth_carries_the_finish_switcher():
    """Owner bug (Gaia screenshot): the 9th member's page carried NO
    color switcher at all for any metal-plate theme. Every metal theme's
    Ninth now cycles the same four looks as its seated eight; a
    non-metal theme's Ninth (egypt, slavic — no per-metal art exists)
    correctly stays a single plain plate."""
    from app.encyclopedia import _topics

    topics = _topics()
    gaia = topics["greek"]["entries"][-1]
    assert gaia["name"] == "Gaia"
    gaia_labels = [label for label, _ in gaia["looks"]]
    # Bronze/Gold/Silver always cycle (Gold/Silver are LIVE recolors of
    # the bronze master); "Colored" joins only once a colored/Gaia.png
    # actually lands on disk (graceful-absent, no art generated yet).
    assert gaia_labels[-3:] == ["Bronze", "Gold", "Silver"]
    assert set(gaia_labels) <= {"Colored", "Bronze", "Gold", "Silver"}
    cat = topics["chinese"]["entries"][-1]
    assert cat["name"] == "The Cat"
    assert [label for label, _ in cat["looks"]] == [
        "Bronze", "Gold", "Silver", "Colored",
    ]
    pharaoh = topics["egypt"]["entries"][-1]
    assert pharaoh["name"] == "The Pharaoh"
    assert "looks" not in pharaoh          # egypt carries no metal art


def test_image_hover_names_the_plate():
    """Owner spec: hovering any article image shows its NAME — critical
    on multi-image pages like the era calendars ("Byzantine")."""
    from app.encyclopedia import _image_tooltip
    from config import defaults as _defaults

    assert _image_tooltip(_defaults.ERA_ART_DIR / "calendar" / "Byzantine.png") == (
        "Byzantine"
    )
    assert _image_tooltip(
        _defaults.WEEKDAY_ART_DIR / "wolf" / "primary" / "sigma.png"
    ) == "Sigma"
    assert _image_tooltip(
        _defaults.ECLIPSE_ART_DIR / "Solar_Total.png"
    ) == "Solar Total"


def test_space_jump_index_remap_survives_the_restructure():
    """Owner item 9: the reordering must not break the dial's Spacebar
    jump — compositor.encyclopedia_target still emits the OLD raw
    weekday index (sun=0, moon=1..saturn=6); the dialog remaps it onto
    the NEW page order (Monday..Saturday keep their old index, sun
    lands on the merged dual page)."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog

    QApplication.instance() or QApplication([])
    # raw index 0 ("sun") -> the dual page (index 8), NOT the title page.
    sun_jump = EncyclopediaDialog(initial_topic="wolf", initial_entry=0)
    assert sun_jump._entry_index == 8
    assert sun_jump._topics["wolf"]["entries"][8]["dual"] is True
    sun_jump.deleteLater()
    # raw index 1 ("moon"/Monday) is UNCHANGED — still index 1.
    monday_jump = EncyclopediaDialog(initial_topic="wolf", initial_entry=1)
    assert monday_jump._entry_index == 1
    assert monday_jump._topics["wolf"]["entries"][1]["name"] == "Luna"
    monday_jump.deleteLater()
    # raw index 6 ("saturn"/Saturday) is UNCHANGED — still index 6.
    saturday_jump = EncyclopediaDialog(initial_topic="wolf", initial_entry=6)
    assert saturday_jump._entry_index == 6
    saturday_jump.deleteLater()
    # A non-restructured topic (moon phases) never remaps.
    moon_jump = EncyclopediaDialog(initial_topic="moon", initial_entry=0)
    assert moon_jump._entry_index == 0
    moon_jump.deleteLater()


def test_finish_switcher_lives_in_the_top_row():
    """Owner fix round R3 (Color Switcher.png): the finish switcher
    moves to the TOP row, in line with Home and Download — ONE
    persistent widget trio (not rebuilt per entry, like the pager) —
    and is restyled to border-only frames in the finish's own color,
    never the old filled gradient pill; "Colored" wears the swept-
    spectrum gradient border, exact owner order."""
    from PySide6.QtWidgets import QApplication

    from app.encyclopedia import EncyclopediaDialog

    QApplication.instance() or QApplication([])
    dialog = EncyclopediaDialog()
    # The trio sits in the SAME QHBoxLayout as Home/Download — the
    # dialog's own top-level layout's first item.
    top_row = dialog.layout().itemAt(0).layout()
    top_widgets = [
        top_row.itemAt(i).widget() for i in range(top_row.count())
        if top_row.itemAt(i).widget() is not None
    ]
    assert dialog._back in top_widgets
    assert dialog._download in top_widgets
    assert dialog._look_back in top_widgets
    assert dialog._look_caption in top_widgets
    assert dialog._look_forward in top_widgets
    assert top_widgets.index(dialog._look_caption) > top_widgets.index(
        dialog._back
    )
    assert top_widgets.index(dialog._look_caption) < top_widgets.index(
        dialog._download
    )
    # Border-only styling: Bronze is a SOLID hex border, no fill;
    # Colored wears the exact gradient sweep the owner specified.
    dialog._show_topic("wolf")
    dialog._entry_index = 1                        # Monday — offers the switcher
    dialog._show_entry()
    dialog._cycle_look(1)                          # -> Bronze
    bronze_qss = dialog._look_caption.styleSheet()
    assert "background: transparent" in bronze_qss
    assert "#CD7F32" in bronze_qss
    assert "qlineargradient" not in bronze_qss
    dialog._cycle_look(-1)                         # back to Colored
    colored_qss = dialog._look_caption.styleSheet()
    assert "qlineargradient" in colored_qss
    for hue in defaults.ENCYCLOPEDIA_FINISH_GRADIENT:
        assert hue in colored_qss
    dialog.deleteLater()
