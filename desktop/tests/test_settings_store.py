"""Settings persistence: atomic round-trip, corruption handling, BOM
tolerance (hand-edited files), diameter validation."""

import json

import pytest

from app.settings_store import Settings, SettingsCorruptError, SettingsStore, replace
from config import calendar_mounts, constants, paths


@pytest.fixture
def store(tmp_path):
    return SettingsStore(tmp_path / "settings.json")


# --- multi-watch settings file scheme (ADD WATCH round, owner INSTRUCTION.txt
# item 2, sealed 2026-07-21) --------------------------------------------------


def test_settings_path_scheme_for_multiple_watches(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    # Watch 1 keeps the pre-multi-watch filename — existing installs'
    # settings.json is picked up untouched, with no index argument at all.
    assert paths.settings_path() == paths.settings_path(1)
    assert paths.settings_path(1).name == "settings.json"
    assert paths.settings_path(2).name == "settings.2.json"
    assert paths.settings_path(7).name == "settings.7.json"
    # Every watch's file lives in the SAME per-user directory.
    assert paths.settings_path(1).parent == paths.settings_path(2).parent


def test_multi_watch_settings_round_trip_independently(tmp_path, monkeypatch):
    """Each watch's own settings file is a fully independent
    SettingsStore — writing watch 2's file must never touch watch 1's."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    store1 = SettingsStore(paths.settings_path(1))
    store2 = SettingsStore(paths.settings_path(2))
    store1.save(replace(Settings(), city_name="Belgrade", diameter=360))
    store2.save(replace(Settings(), city_name="Tromso", diameter=480))
    assert store1.load().city_name == "Belgrade"
    assert store1.load().diameter == 360
    assert store2.load().city_name == "Tromso"
    assert store2.load().diameter == 480


def test_discover_watch_indices_finds_every_numbered_file(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.user_dir().mkdir(parents=True)
    SettingsStore(paths.settings_path(1)).save(Settings())
    SettingsStore(paths.settings_path(3)).save(Settings())
    assert paths.discover_watch_indices() == [1, 3]


def test_discover_watch_indices_ignores_temp_and_backup_files(tmp_path, monkeypatch):
    """A quarantined `.bak` and an in-flight atomic-write `.tmp` must
    never be mistaken for a real watch."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.user_dir().mkdir(parents=True)
    SettingsStore(paths.settings_path(1)).save(Settings())
    (paths.user_dir() / "settings.json.bak").write_text("{}", encoding="utf-8")
    (paths.user_dir() / "settings.2.json.tmp").write_text("{}", encoding="utf-8")
    assert paths.discover_watch_indices() == [1]


def test_discover_watch_indices_empty_dir_yields_just_the_anchor(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert paths.discover_watch_indices() == [1]


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


def test_pointer_saturation_out_of_range_raises(store):
    """The Saturation sliders (owner 2026-07-18, Session 21-C/D) are
    0.0..1.0 factors — same corrupt-on-out-of-range law as every other
    size multiplier. The OLD key ("palette_saturation") still validates
    too, since it feeds the new key's fallback default."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "pointer_saturation": 1.5}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "palette_saturation": 1.5}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_ring_saturation_out_of_range_raises(store):
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "ring_saturation": -0.1}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_pointer_saturation_migrates_from_the_old_key(store):
    """Rename (Session 21-D, owner clarity request now that RING has its
    own independent slider): an older file's "palette_saturation" carries
    over as pointer_saturation; the new key wins when both are present."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "palette_saturation": 0.3}',
        encoding="utf-8",
    )
    assert store.load().pointer_saturation == pytest.approx(0.3)
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "palette_saturation": 0.3, "pointer_saturation": 0.7}',
        encoding="utf-8",
    )
    assert store.load().pointer_saturation == pytest.approx(0.7)
    # Neither key present: default stays 1.0.
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    assert store.load().pointer_saturation == pytest.approx(1.0)
    # Saving after a migration writes ONLY the new key.
    store.save(store.load())
    raw = store.path.read_text(encoding="utf-8")
    assert '"palette_saturation"' not in raw
    assert '"pointer_saturation"' in raw


def test_display_choices_round_trip(store):
    saved = replace(
        Settings(),
        pointer="octa",
        umbra_form="gradient",
        umbra_contrast="half",
        palette_style="secondary",
        archetype_mode=True,
        archetype_names=False,
        pointer_saturation=0.4,
        ring_saturation=0.6,
        earth_label="weekday",
        z_mode="top",
        solar_rotation=False,
        octa_slot="ascendant",
        day_slot_style="colored",
        info_slot_style="constellation",
        info_slot_theme="norse",
        earth_style="atmo",
        ring_tint="#8E55B9",
        ring_finish="silver",
        earth_scale=1.5,
        moon_scale=0.8,
        slot_scale=1.25,
        ring_jewels_scale=1.3,
        hover_enlarge=1.4,
        show_earth=False,
        show_moon=False,
        show_marker_pointer=True,
        show_weekday=False,
        show_pointer=False,
        colorful=False,
        show_seconds=False,
        show_octa_slot=False,
        language="sr-Latn",
        ring="LOOP",
        ring_eye_shine={"Dollar": False},
        theme_metals={"greek": "gold", "norse": "silver"},
        theme_metal_follow_ring=True,
    )
    store.save(saved)
    assert store.load() == saved
    # An unknown theme or metal is dropped on load, never crashes.
    lenient = replace(Settings(), theme_metals={"greek": "gold"})
    store.save(lenient)
    raw = store.path.read_text(encoding="utf-8").replace(
        '"greek": "gold"', '"greek": "banana", "egypt": "gold"'
    )
    store.path.write_text(raw, encoding="utf-8")
    assert store.load().theme_metals == {}
    # planets_art (owner 2026-07-18): metal-capable like the pantheon
    # sets, but its art has no colored/ subfolder — gold/bronze/silver
    # are accepted, "colored" is dropped like an unknown theme/metal.
    planets_art_metals = replace(
        Settings(),
        theme_metals={"planets_art": "gold"},
    )
    store.save(planets_art_metals)
    assert store.load().theme_metals == {"planets_art": "gold"}
    store.save(replace(Settings(), theme_metals={"planets_art": "silver"}))
    assert store.load().theme_metals == {"planets_art": "silver"}
    store.save(replace(Settings(), theme_metals={"planets_art": "bronze"}))
    assert store.load().theme_metals == {"planets_art": "bronze"}
    store.save(replace(Settings(), theme_metals={"planets_art": "colored"}))
    raw = store.path.read_text(encoding="utf-8")
    assert '"colored"' in raw               # written as-is (unvalidated write)
    assert store.load().theme_metals == {}  # but rejected on load
    # The six OLD combined South-slot values migrate to mode + style
    # (2026-07-12) instead of raising SettingsCorruptError.
    raw = store.path.read_text(encoding="utf-8").replace(
        '"octa_slot": "time"', '"octa_slot": "chinese_logo"'
    ).replace('"info_slot_style": "sign",', '')   # a true legacy file
    store.path.write_text(raw, encoding="utf-8")
    migrated = store.load()
    assert migrated.octa_slot == "chinese"
    assert migrated.info_slot_style == "bronze"


def test_ring_renames_migrate_stored_settings(store):
    """TASK 2 (MASON/ICONS round, owner verdicts 2026-07-19, third
    batch) + DOLLAR/EYE round (owner decree 2026-07-27): the bundled
    ring presets renamed "MASON G" -> "Mason" -> "Dollar" and
    "NUMBERS" -> "Omega" -> "The One" (external user data, not an API
    shim, Rule #6) — an older settings file naming ANY generation's
    old value loads onto the current one instead of raising
    SettingsCorruptError. "MORPH"/"Morph" -> "PILOT" (CROSS-WORDS
    round, owner UV inbox + PILOT pick 2026-07-27) -> "LOOP" (LOOP
    round, owner ruling 2026-08-06) chains three generations onto the
    current name — the fold alone bridges only a pure-case rename."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "MASON G"}',
        encoding="utf-8",
    )
    assert store.load().ring == "Dollar"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "Mason"}',
        encoding="utf-8",
    )
    assert store.load().ring == "Dollar"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "NUMBERS"}',
        encoding="utf-8",
    )
    assert store.load().ring == "The One"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "Omega"}',
        encoding="utf-8",
    )
    assert store.load().ring == "The One"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "MORPH"}',
        encoding="utf-8",
    )
    assert store.load().ring == "LOOP"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "Morph"}',
        encoding="utf-8",
    )
    assert store.load().ring == "LOOP"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "PILOT"}',
        encoding="utf-8",
    )
    assert store.load().ring == "LOOP"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "no such preset"}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_crown_text_keys_migrate_from_the_old_motto_names(store):
    """TASK 1 (owner ruling 2026-08-06, "one term for one thing"): a
    settings file saved before the rename carries `motto_alpha`/
    `motto_scale`/`motto_tint` — `load()` must read them as the
    fallback default for the new `crown_text_alpha`/`crown_text_scale`/
    `crown_text_tint` fields instead of silently reverting to 1.0/1.0/
    None (data loss) or raising SettingsCorruptError."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "motto_alpha": 0.4, "motto_scale": 1.5, "motto_tint": "#123456"}',
        encoding="utf-8",
    )
    loaded = store.load()
    assert loaded.crown_text_alpha == pytest.approx(0.4)
    assert loaded.crown_text_scale == pytest.approx(1.5)
    assert loaded.crown_text_tint == "#123456"
    # The NEW keys win when both are present (post-migration re-save).
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "motto_alpha": 0.4, "crown_text_alpha": 0.9}',
        encoding="utf-8",
    )
    assert store.load().crown_text_alpha == pytest.approx(0.9)
    # A file that never carried either key keeps the ordinary defaults.
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    fresh = store.load()
    assert fresh.crown_text_alpha == pytest.approx(1.0)
    assert fresh.crown_text_scale == pytest.approx(1.0)
    assert fresh.crown_text_tint is None
    # save() writes only the new keys — a re-save fully migrates the file.
    store.save(loaded)
    assert "motto_alpha" not in store.path.read_text(encoding="utf-8")
    assert "crown_text_alpha" in store.path.read_text(encoding="utf-8")


def test_custom_ring_card_motto_field_migrates_to_crown_text(store):
    """TASK 1: `app.settings_ring.migrate_legacy_ring_card` upgrades a
    stored custom-ring card's old `motto` field onto `crown_text` before
    `validate_preset` runs — `data.rings.validate_preset` only reads
    `crown_text` now, so an unmigrated card would silently lose its
    crown-arc entries (an optional field, no loud failure) rather than
    read as corrupt."""
    from app.settings_ring import migrate_legacy_ring_card

    legacy_card = {
        "name": "OLDCROWN", "outer": "bot_cross", "jewels": ["A", "B", "C", "D"],
        "motto": [{"text": "AB", "orientation": "top"}],
    }
    migrated = migrate_legacy_ring_card(legacy_card)
    assert "motto" not in migrated
    assert migrated["crown_text"] == [{"text": "AB", "orientation": "top"}]
    # A card already carrying `crown_text` is left untouched (no
    # clobbering a fresh save with a stale `motto` sibling key).
    fresh_card = {
        "name": "NEWCROWN", "outer": "bot_cross", "jewels": ["A", "B", "C", "D"],
        "crown_text": [{"text": "CD", "orientation": "bottom"}],
    }
    assert migrate_legacy_ring_card(fresh_card) == fresh_card


def test_jewel_keys_migrate_from_the_old_letter_names(store):
    """JEWELS naming sweep (owner ruling 2026-08-06, "one term for one
    thing"): a settings file saved before the rename carries
    `ring_letter_scale`/`letter_tint` — `load()` must read them as the
    fallback default for the new `ring_jewels_scale`/`jewels_tint`
    fields instead of silently reverting to 1.0/None (data loss) or
    raising SettingsCorruptError."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring_letter_scale": 1.4, "letter_tint": "#654321"}',
        encoding="utf-8",
    )
    loaded = store.load()
    assert loaded.ring_jewels_scale == pytest.approx(1.4)
    assert loaded.jewels_tint == "#654321"
    # The NEW keys win when both are present (post-migration re-save).
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring_letter_scale": 1.4, "ring_jewels_scale": 0.8}',
        encoding="utf-8",
    )
    assert store.load().ring_jewels_scale == pytest.approx(0.8)
    # A file that never carried either key keeps the ordinary defaults.
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    fresh = store.load()
    assert fresh.ring_jewels_scale == pytest.approx(1.0)
    assert fresh.jewels_tint is None
    # save() writes only the new keys — a re-save fully migrates the file.
    store.save(loaded)
    assert "ring_letter_scale" not in store.path.read_text(encoding="utf-8")
    assert "letter_tint" not in store.path.read_text(encoding="utf-8")
    assert "ring_jewels_scale" in store.path.read_text(encoding="utf-8")
    assert "jewels_tint" in store.path.read_text(encoding="utf-8")


def test_minutes_keys_migrate_from_the_old_inner_names(store):
    """MINUTES naming sweep (owner ruling 2026-08-06, "one term for one
    thing"): a settings file saved before the rename carries
    `numeral_inner_size`/`numeral_inner_face` — `load()` must read them
    as the fallback default for the new `minutes_size`/`minutes_face`
    fields instead of silently reverting to the SETTLED defaults (data
    loss) or raising SettingsCorruptError."""
    from config import dial

    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "numeral_inner_size": 100, "numeral_inner_face": "Unispace"}',
        encoding="utf-8",
    )
    loaded = store.load()
    assert loaded.minutes_size == 100
    assert loaded.minutes_face == "Unispace"
    # The NEW keys win when both are present (post-migration re-save).
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "numeral_inner_size": 100, "minutes_size": 90,'
        ' "numeral_inner_face": "Unispace", "minutes_face": "Arial Black"}',
        encoding="utf-8",
    )
    both = store.load()
    assert both.minutes_size == 90
    assert both.minutes_face == "Arial Black"
    # A file that never carried either key keeps the ordinary defaults.
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    fresh = store.load()
    assert fresh.minutes_size == dial.MINUTES_SIZE_DEFAULT
    assert fresh.minutes_face == dial.MINUTES_FACE_DEFAULT
    # save() writes only the new keys — a re-save fully migrates the file.
    store.save(loaded)
    saved_text = store.path.read_text(encoding="utf-8")
    assert "numeral_inner_size" not in saved_text
    assert "numeral_inner_face" not in saved_text
    assert '"minutes_size": 100' in saved_text
    assert '"minutes_face": "Unispace"' in saved_text


def test_custom_ring_card_letters_field_migrates_to_jewels(store):
    """JEWELS naming sweep (owner ruling 2026-08-06): a stored
    custom-ring card's old `letters` field is read as the fallback in
    `data.rings.validate_preset` — an unmigrated card would otherwise
    raise (zero jewels for N positions) rather than load."""
    from data.rings import validate_preset

    legacy_card = {
        "name": "OLDLETTERS", "outer": "bot_cross",
        "letters": ["A", "B", "C", "D"],
    }
    card = validate_preset(legacy_card)
    assert card["jewels"] == ("A", "B", "C", "D")
    # The NEW key wins when both are present.
    both_card = {
        "name": "BOTHKEYS", "outer": "bot_cross",
        "letters": ["A", "B", "C", "D"], "jewels": ["W", "X", "Y", "Z"],
    }
    assert validate_preset(both_card)["jewels"] == ("W", "X", "Y", "Z")


def test_stale_ring_two_metals_key_is_silently_ignored_on_load(store):
    """TWO METALS RETIRED (owner decree 2026-08-11): a settings file
    written by an older build still carries a `ring_two_metals` key —
    the loader must not choke on it, since it simply never reads that
    key any more (unknown keys in the raw JSON are never validated)."""
    store.save(Settings())
    raw = store.path.read_text(encoding="utf-8").replace(
        "{", '{"ring_two_metals": {"Dollar": false, "Ghost": true}, ', 1
    )
    store.path.write_text(raw, encoding="utf-8")
    assert store.load() == Settings()


def test_custom_ring_thematic_pick_round_trips(store):
    """CUSTOM-THEMATIC widening (owner 2026-07-27): a custom card's own
    `thematic` color pick persists through save/load; a card without
    one stays byte-identical (no key invented)."""
    saved = replace(Settings(), custom_rings=(
        {"name": "IRONRING", "outer": "bot_cross",
         "jewels": ["I", "R", "O", "N"], "thematic": "iron"},
        {"name": "PLAINRING", "outer": "bot_cross",
         "jewels": ["A", "B", "C", "D"]},
    ))
    store.save(saved)
    loaded = store.load()
    assert loaded.custom_rings[0]["thematic"] == "iron"
    assert "thematic" not in loaded.custom_rings[1]


def test_a_pre_compositional_settings_file_loads_cleanly(store):
    """THE COMPOSITIONAL RING MODEL SETTINGS MIGRATION (owner decree
    2026-08-05): a settings file written BEFORE this round — `ring`
    plus a custom card in the old `{name, positions, letters}` shape,
    no `ring_inner`/`custom_ring_crown_*` keys at all — must load
    cleanly and resolve to the SAME preset the user had, with the new
    fields defaulting empty (never renaming the stored `ring` key,
    per the settings-corruption law)."""
    import json

    payload = {
        "schema_version": 1,
        "window": {"x": None, "y": None, "diameter": 720},
        "click_through": False,
        "ring": "domy",  # pre-existing case-insensitive fold
        "custom_rings": [
            {"name": "OLDRING", "positions": [12, 20, 24, 4],
             "jewels": ["A", "B", "C", "D"]},
        ],
    }
    store._path.parent.mkdir(parents=True, exist_ok=True)
    store._path.write_text(json.dumps(payload), encoding="utf-8")
    loaded = store.load()
    assert loaded.ring == "DOMY"
    assert loaded.ring_inner == {}
    assert loaded.custom_ring_crown_text == {}
    assert loaded.custom_ring_crown_orientation == {}
    assert loaded.custom_rings[0]["outer"] == "bot_cross"
    assert "positions" not in loaded.custom_rings[0]


def test_earth_label_migrates_from_the_old_bool_pair(store):
    """Session 21-E (owner 2026-07-18, ROADMAP 15h): the old
    show_earth_date/earth_weekday bool pair migrates onto the new
    earth_label enum — T,F -> "date"; F,T -> "weekday"; T,T ->
    "date_weekday" (the OLD combined "Full Date" meaning, before "full"
    meant date+year); F,F -> "off". The pre-rename archetype_earth_day
    key still feeds the weekday side when earth_weekday itself is
    absent. The new earth_label key wins outright when present."""
    base = '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
    store.path.write_text(
        base + ' "show_earth_date": true, "earth_weekday": false}',
        encoding="utf-8",
    )
    assert store.load().earth_label == "date"
    store.path.write_text(
        base + ' "show_earth_date": false, "earth_weekday": true}',
        encoding="utf-8",
    )
    assert store.load().earth_label == "weekday"
    store.path.write_text(
        base + ' "show_earth_date": true, "earth_weekday": true}',
        encoding="utf-8",
    )
    assert store.load().earth_label == "date_weekday"
    store.path.write_text(
        base + ' "show_earth_date": false, "earth_weekday": false}',
        encoding="utf-8",
    )
    assert store.load().earth_label == "off"
    # A brand-new file with none of the old keys keeps the enum default.
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    assert store.load().earth_label == "date"
    # The pre-rename key still feeds the weekday side when earth_weekday
    # itself is absent.
    store.path.write_text(
        base + ' "show_earth_date": false, "archetype_earth_day": true}',
        encoding="utf-8",
    )
    assert store.load().earth_label == "weekday"
    # The new key wins outright when present, regardless of the old pair.
    store.path.write_text(
        base + ' "show_earth_date": true, "earth_weekday": false,'
        ' "earth_label": "full"}',
        encoding="utf-8",
    )
    assert store.load().earth_label == "full"


def test_earth_label_modes_round_trip(store):
    """All FIVE earth_label values persist through save/load (owner
    2026-07-18, ROADMAP 15h: Date / Weekday / Date & Weekday / Full
    Date, plus off) and an unknown value raises visibly (Rule #1)."""
    for mode in ("off", "date", "weekday", "date_weekday", "full"):
        store.save(replace(Settings(), earth_label=mode))
        assert store.load().earth_label == mode
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "earth_label": "bogus"}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_z_mode_round_trip_and_default(store):
    """Visibility Z mode (owner 2026-07-17): all THREE modes persist
    (ROADMAP 15e added 'normal'), defaults to 'bottom' in older files, and
    rejects an unknown value."""
    for mode in ("bottom", "normal", "top"):
        store.save(replace(Settings(), z_mode=mode))
        assert store.load().z_mode == mode
    store.save(replace(Settings(), z_mode="top"))
    assert store.load().z_mode == "top"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    assert store.load().z_mode == "bottom"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "z_mode": "sideways"}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_subdial_set_round_trip_and_default(store):
    """The SUBDIAL PLATE SET (owner decree 2026-07-21, Rsub round): all
    FIVE sets persist, default to "set1" in older files, and reject an
    unknown value."""

    for name in constants.SUBDIAL_SETS:
        store.save(replace(Settings(), subdial_set=name))
        assert store.load().subdial_set == name
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    assert store.load().subdial_set == "set1"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "subdial_set": "set9"}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_metal_shade_round_trip_and_default(store):
    """THE METAL SHADES (R8a round, owner spec 2026-07-21 night): every
    shade of every metal persists, older files default to
    config.constants.METAL_SHADE_DEFAULT, and an unknown shade name
    raises loudly (Rule #1) rather than silently falling back."""

    for metal, names in constants.METAL_SHADE_NAMES.items():
        if metal == "thematic":
            # The THEMATIC pseudo-metal (ENLARGE/THEMATIC round, owner
            # 2026-07-27) is NOT a user setting — its shade follows the
            # active ring preset (`constants.RING_THEMATIC_SHADES`,
            # resolved in `app.controller.apply_display_settings`).
            continue
        field = f"metal_shade_{metal}"
        for shade in names:
            store.save(replace(Settings(), **{field: shade}))
            assert getattr(store.load(), field) == shade
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360}}',
        encoding="utf-8",
    )
    loaded = store.load()
    assert loaded.metal_shade_gold == constants.METAL_SHADE_DEFAULT["gold"]
    assert loaded.metal_shade_bronze == constants.METAL_SHADE_DEFAULT["bronze"]
    assert loaded.metal_shade_silver == constants.METAL_SHADE_DEFAULT["silver"]
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "metal_shade_gold": "rose_gold"}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_year_line_and_jump_cities_round_trip(store):
    """Session 16: the era labels, the suffix opt-in, the third
    calendar and the Quick Jump cities persist and validate."""
    saved = replace(
        Settings(),
        era_notation="bc_ad",
        show_era_suffix=True,
        third_era="hebrew",
        jump_cities=(
            {
                "name": "Tromso", "latitude": 69.6489,
                "longitude": 18.9551, "timezone": "Europe/Oslo",
            },
        ),
    )
    store.save(saved)
    assert store.load() == saved


def test_chinese_third_era_round_trips(store):
    """Owner fix-round B, 2026-07-19: the Huangdi count validates and
    persists exactly like every other third calendar."""
    saved = replace(Settings(), third_era="chinese")
    store.save(saved)
    assert store.load() == saved


def test_bad_jump_city_raises(store):
    store.save(Settings())
    raw = store.path.read_text(encoding="utf-8").replace(
        '"jump_cities": []',
        '"jump_cities": [{"name": "X", "latitude": 200, '
        '"longitude": 0, "timezone": "Europe/Oslo"}]',
    )
    store.path.write_text(raw, encoding="utf-8")
    with pytest.raises(SettingsCorruptError):
        store.load()


@pytest.mark.parametrize(
    "key",
    [
        "pointer",
        "umbra_form",
        "umbra_contrast",
        "palette_style",
        "octa_slot",
        "earth_style",
        "ring_finish",
        "ring_tint",
        "era_notation",
        "third_era",
        "subdial_set",
        "calendar_mount",
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


def test_calendar_mount_round_trips_and_defaults_to_zodiac(store):
    """The 12-SET MOUNT (DESIGN ZODIAC law, R9a round; "chinese" added
    owner R12, Blue Moon round): "zodiac" ships as the default (the
    owner's law names the Calendar pointer as the 12-set's default
    home) — a fresh settings file, and every other choice, round-trip
    through save/load."""
    assert Settings().calendar_mount == "zodiac"
    assert calendar_mounts.CALENDAR_MOUNT_MODES[0] == "off"
    assert set(calendar_mounts.CALENDAR_MOUNT_MODES[1:]) == set(calendar_mounts.CALENDAR_MOUNTS)
    for mount in calendar_mounts.CALENDAR_MOUNT_MODES:
        saved = replace(Settings(), calendar_mount=mount)
        store.save(saved)
        assert store.load().calendar_mount == mount


def test_string_boolean_is_corrupt(store):
    """Review fix (Rule #1): a hand-edited "false" STRING must raise,
    not silently coerce to True and re-enable the element."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "show_seconds": "false"}',
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
        palettes={"hexa_primary": ("#112233",) * 6},
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
        '{"hexa_primary": ["#112233"]}',                # wrong hue count
        '{"hexa_primary": ["red", "#1", "#2", "#3", "#4", "#5"]}',  # bad colors
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


def test_retired_slot_names_migrate_instead_of_corrupting_the_file(store):
    """REGRESSION (owner report 2026-07-28). The paint/light/cube →
    primary/secondary/tertiary slot rename first shipped WITHOUT a data
    migration, so every settings file written before it failed to load
    ("palette_style 'light' unknown") and the app offered a reset that
    would have wiped all three of the owner's watches. A file carrying
    the retired words must load, with each word read as its positional
    successor — never as corruption."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "palette_style": "light",'
        ' "palettes": {"hexa_paint": ["#112233", "#223344", "#334455",'
        ' "#445566", "#556677", "#667788"]}}',
        encoding="utf-8",
    )
    loaded = store.load()
    assert loaded.palette_style == "secondary"
    assert set(loaded.palettes) == {"hexa_primary"}
    assert loaded.palettes["hexa_primary"][0] == "#112233"
    # The third slot travels the same road.
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "pointer": "trio", "palette_style": "cube"}',
        encoding="utf-8",
    )
    assert store.load().palette_style == "tertiary"


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


# --- THE TWO WORLD-MODES' own key (ring_rework.md §1) ------------------------


def test_world_mode_defaults_to_geocentric_in_a_file_that_predates_it(store):
    """THE MIGRATION-SAFE DEFAULT: every watch stored before this round
    has no world-mode key at all, and must load as the dial it was —
    Geocentric, bit for bit — never as a corrupt file."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 12, "y": 34, "diameter": 360}}',
        encoding="utf-8",
    )
    loaded = store.load()
    assert loaded.world_mode == "noon_up"
    assert (loaded.window_x, loaded.window_y, loaded.diameter) == (12, 34, 360)


def test_world_mode_round_trips_and_rejects_an_unknown_value(store):
    store.save(replace(Settings(), world_mode="sky_up"))
    assert store.load().world_mode == "sky_up"
    assert '"world_mode"' in store.path.read_text(encoding="utf-8")
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "world_mode": "ptolemaic"}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_a_foreign_top_level_mode_key_can_never_become_the_world_mode(store):
    """THE COLLISION THIS KEY'S NAME EXISTS TO KILL (2026-08-06): the
    world mode is stored as `world_mode`, never the bare `mode` its
    first round wrote. A file carrying somebody ELSE's top-level `mode`
    — a hand-seeded profile, another tool's leftover — must load
    cleanly and leave the dial Geocentric, no matter what that value
    says. `mode` is simply not a key this loader reads."""
    for foreign in ("sky_up", "dark", "12h", True, 7):
        store.path.write_text(
            '{"schema_version": 1,'
            ' "window": {"x": 0, "y": 0, "diameter": 360},'
            f' "mode": {json.dumps(foreign)}}}',
            encoding="utf-8",
        )
        loaded = store.load()
        assert loaded.world_mode == "noon_up"
    # ...and the app's own key still works in the very same file.
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 0, "y": 0, "diameter": 360},'
        ' "mode": "sky_up", "world_mode": "sky_up"}',
        encoding="utf-8",
    )
    assert store.load().world_mode == "sky_up"


# --- The identity markers (2026-08-06 escalation) ----------------------------


def test_a_file_without_the_identity_markers_names_what_it_is_missing(store):
    """The exact shape that cost a session (a hand-seeded verify
    profile): a flat `{diameter, location, mode, x, y}` object, valid
    JSON and no generation of this app's settings file — this app has
    written `schema_version` + a nested `window` section since
    0.14.001.

    It is corrupt, deliberately — defaulting the identity markers would
    turn an unreadable file into a SILENT reset of every stored
    setting. What it must NOT be is a riddle: the message names the
    missing keys AND the file's own top-level keys, so the next reader
    sees at a glance that this is not a settings file rather than
    "the code now demands a section it never wrote"."""
    store.path.write_text(
        json.dumps({
            "diameter": 540,
            "location": {"name": "Belgrade"},
            "mode": "sky_up",
            "x": 100,
            "y": 200,
        }),
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError) as caught:
        store.load()
    message = str(caught.value)
    assert "not a Watch Academy settings file" in message
    assert "'schema_version'" in message and "'window'" in message
    # its OWN keys, so the reader can see what it really is
    assert "'diameter'" in message and "'location'" in message
    # ...and a file the app itself wrote is never touched by this check.
    store.save(Settings())
    assert store.load().diameter == Settings().diameter


def test_a_json_root_that_is_not_an_object_says_so(store):
    store.path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(SettingsCorruptError) as caught:
        store.load()
    assert "the JSON root is list" in str(caught.value)
