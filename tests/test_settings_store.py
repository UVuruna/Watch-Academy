"""Settings persistence: atomic round-trip, corruption handling, BOM
tolerance (hand-edited files), diameter validation."""

import pytest

from app.settings_store import Settings, SettingsCorruptError, SettingsStore, replace
from config import paths


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
        palette_style="light",
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
        ring_letter_scale=1.3,
        hover_enlarge=1.4,
        show_earth=False,
        show_moon=False,
        show_weekday=False,
        show_pointer=False,
        colorful=False,
        show_seconds=False,
        show_octa_slot=False,
        language="sr-Latn",
        ring="Morph",
        ring_two_metals={"Mason": False, "Omega": True},
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
    batch): the bundled ring presets renamed "MASON G" -> "Mason" and
    "NUMBERS" -> "Omega" (external user data, not an API shim, Rule
    #6) — an older settings file naming either old value loads onto
    the new one instead of raising SettingsCorruptError. "MORPH" ->
    "Morph" is a pure CASE change, already bridged by the pre-existing
    case-insensitive fold (no dedicated migration entry needed)."""
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "MASON G"}',
        encoding="utf-8",
    )
    assert store.load().ring == "Mason"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "NUMBERS"}',
        encoding="utf-8",
    )
    assert store.load().ring == "Omega"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "MORPH"}',
        encoding="utf-8",
    )
    assert store.load().ring == "Morph"
    store.path.write_text(
        '{"schema_version": 1, "window": {"x": 1, "y": 2, "diameter": 360},'
        ' "ring": "no such preset"}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        store.load()


def test_ring_two_metals_round_trips_and_drops_stale_entries(store):
    """TASK 3 (MASON/ICONS round): the per-preset "Two metals" choice
    round-trips keyed by preset name; a non-bool value or a name that
    resolves to nothing loaded is silently dropped on load — the SAME
    lenient policy `theme_metals` already uses, rather than corrupting
    the whole file over one stale entry."""
    saved = replace(
        Settings(), ring_two_metals={"Mason": False, "Omega": True},
    )
    store.save(saved)
    assert store.load() == saved
    raw = store.path.read_text(encoding="utf-8").replace(
        '"Mason": false', '"Mason": false, "MASON G": true, "Ghost": true'
    ).replace('"Omega": true', '"Omega": "yes"')
    store.path.write_text(raw, encoding="utf-8")
    lenient = store.load()
    # "MASON G" folds onto "Mason" (rename migration) but "Mason" was
    # already written first, so the raw dict's OWN later key wins —
    # both resolve to the same True; the unknown "Ghost" name and the
    # non-bool "yes" value are both dropped.
    assert lenient.ring_two_metals == {"Mason": True}


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
    from config import constants

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
    from config import constants

    for metal, names in constants.METAL_SHADE_NAMES.items():
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
    """The 12-SET MOUNT (DESIGN ZODIAC law, R9a round): "zodiac" ships
    as the default (the owner's law names the Calendar pointer as the
    12-set's default home) — a fresh settings file, and every other
    choice, round-trip through save/load."""
    assert Settings().calendar_mount == "zodiac"
    for mount in ("off", "zodiac", "months"):
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
