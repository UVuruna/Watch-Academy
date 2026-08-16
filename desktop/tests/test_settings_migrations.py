"""RETIRED NAMES AND THEIR SUCCESSORS — the settings file's own
migrations.

Split out of `test_settings_store.py` when it crossed the structure
law's threshold (2026-08-16). The responsibility is its own: a stored
file is EXTERNAL USER DATA, and every rename the program has ever made
must keep answering to the old word, because the alternative is what
the owner actually got — SettingsCorruptError on launch and a Reset
button as the only way forward, which throws away every stored watch.
"""

import json

from app.settings_store import Settings

from tests.test_settings_store import store          # noqa: F401 — fixture


def test_the_retired_astrology_slot_mode_migrates_to_zodiac(store):
    """FOUND IN THE OWNER'S OWN LIVE FILE (2026-08-16).

    `"astrology"` was a legal `weekday_slot` from 0.14.159 — "the weekday
    POSITION can now carry an astrology badge instead of the bodies:
    Bodies / Astrology / Ascendant". The mode list later renamed it
    `"zodiac"` and no migration was written, so his settings raised
    SettingsCorruptError on every launch and the only thing the program
    offered him was a Reset — losing every stored watch. That is exactly
    the loss `RETIRED_SLOTS` and `MERGED_MOUNTS` already exist to
    prevent; this is the third entry in the same mechanism, not a new
    one.
    """
    store.save(Settings())
    raw = json.loads(store.path.read_text(encoding="utf-8"))
    raw["weekday_slot"] = "astrology"
    raw["third_slot"] = "astrology"
    store.path.write_text(json.dumps(raw), encoding="utf-8")

    migrated = store.load()               # no SettingsCorruptError
    assert migrated.weekday_slot == "zodiac"
    assert migrated.third_slot == "zodiac"
    # ...and a re-save writes only the name in force today.
    store.save(migrated)
    assert "astrology" not in store.path.read_text(encoding="utf-8")


def test_every_retired_name_the_program_still_answers_to_has_a_successor():
    """A rename that forgets its migration is how the owner's file broke.
    Every mapping in the three tables must land on a value the program
    actually accepts today — a typo here would trade a corrupt-file
    dialog for a silently wrong watch."""
    from app.settings_fields import MERGED_MOUNTS, RETIRED_SLOT_MODES
    from config import calendar_mounts, constants

    for retired, successor in RETIRED_SLOT_MODES.items():
        assert retired not in constants.WEEKDAY_SLOT_MODES
        assert retired not in constants.OCTA_SLOT_MODES
        assert successor in constants.WEEKDAY_SLOT_MODES
        assert successor in constants.OCTA_SLOT_MODES
    for retired, successor in MERGED_MOUNTS.items():
        assert retired not in calendar_mounts.CALENDAR_MOUNT_MODES
        assert successor in calendar_mounts.CALENDAR_MOUNT_MODES
