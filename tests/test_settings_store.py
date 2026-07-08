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


def test_quarantine_renames_to_bak(store):
    store.path.write_text("garbage", encoding="utf-8")
    backup = store.quarantine()
    assert backup.name == "settings.json.bak"
    assert backup.read_text(encoding="utf-8") == "garbage"
    assert not store.path.exists()
