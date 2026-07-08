"""Settings persistence: atomic round-trip, corruption handling, BOM
tolerance (hand-edited files), diameter validation."""

import pytest

from app.settings_store import Settings, SettingsCorruptError, SettingsStore, replace


@pytest.fixture
def store(tmp_path):
    return SettingsStore(tmp_path / "settings.json")


def test_missing_file_yields_defaults(store):
    settings = store.load()
    assert settings == Settings()
    assert settings.window_x is None  # first run: never positioned


def test_round_trip(store):
    saved = replace(Settings(), window_x=-1500, window_y=200, click_through=True)
    store.save(saved)
    assert store.load() == saved
    assert not store.path.with_suffix(".json.tmp").exists()  # atomic write cleaned up


def test_click_through_defaults_false_in_older_files(store):
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    assert store.load().click_through is False


def test_bom_is_tolerated(store):
    store.save(replace(Settings(), window_x=10, window_y=20))
    store.path.write_bytes(b"\xef\xbb\xbf" + store.path.read_bytes())
    assert store.load().window_x == 10


def test_corrupt_json_raises(store):
    store.path.write_text('{"schema_version": 1, "window": {', encoding="utf-8")
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_missing_key_raises(store):
    store.path.write_text('{"schema_version": 1}', encoding="utf-8")
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_diameter_out_of_range_raises(store):
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 20}}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_display_choices_round_trip(store):
    saved = replace(
        Settings(),
        pointer="octa",
        umbra_form="gradient",
        umbra_contrast="half",
        palette_style="light",
        solar_rotation=False,
        octa_slot="zodiac_text",
        earth_style="atmo",
    )
    store.save(saved)
    assert store.load() == saved


@pytest.mark.parametrize(
    "key",
    [
        "pointer",
        "umbra_form",
        "umbra_contrast",
        "palette_style",
        "octa_slot",
        "earth_style",
    ],
)
def test_unknown_display_choice_raises(store, key):
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        f' "{key}": "banana"}}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_location_and_overrides_round_trip(store):
    saved = replace(
        Settings(),
        city_name="Tromso",
        city_path=("Europe", "Northern Europe", "Norway", "Troms", "Tromso"),
        latitude=69.6489,
        longitude=18.9551,
        timezone="Europe/Oslo",
        star_alpha=0.5,
        aura_day_alpha=0.25,
        aura_twilight_alpha=0.6,
        palettes={"hexa_paint": ("#112233",) * 6},
    )
    store.save(saved)
    assert store.load() == saved


@pytest.mark.parametrize(
    "location",
    [
        '{"latitude": 95.0}',
        '{"longitude": 200.0}',
        '{"timezone": "Mars/Olympus"}',
    ],
)
def test_bad_location_raises(store, location):
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        f' "location": {location}}}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


@pytest.mark.parametrize(
    "palettes",
    [
        '{"banana_paint": ["#112233"]}',              # unknown key
        '{"hexa_paint": ["#112233"]}',                # wrong hue count
        '{"hexa_paint": ["red", "#1", "#2", "#3", "#4", "#5"]}',  # bad colors
    ],
)
def test_bad_palettes_raise(store, palettes):
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        f' "palettes": {palettes}}}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_alpha_out_of_range_raises(store):
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "star_alpha": 1.5}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_quarantine_renames_to_bak(store):
    store.path.write_text("garbage", encoding="utf-8")
    backup = store.quarantine()
    assert backup.name == "settings.json.bak"
    assert backup.read_text(encoding="utf-8") == "garbage"
    assert not store.path.exists()
