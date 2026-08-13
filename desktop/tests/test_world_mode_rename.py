"""THE WORLD-MODE RENAME (owner verdict 2026-08-13, option B).

The two modes were renamed from `geocentric`/`heliocentric` — which
named them backwards — to `noon_up`/`sky_up`. The owner's standing
order is that a rename goes ALL THE WAY and never throws his own
setting away on the way, so an older settings file must load onto the
mode that BEHAVES the same, not reset to the default and not map by
matching words.

Its own file rather than an appendix to `test_settings_store.py`: that
file sits just under THE STRUCTURE LAW's threshold, and this is a
distinct responsibility — one rename, its migration, and the silent
failure mode it has to rule out.
"""
#
# The two modes were renamed from `geocentric`/`heliocentric` — which named
# them backwards — to `noon_up`/`sky_up`. The owner's standing order is that
# a rename goes all the way AND never throws his own setting away on the way,
# so an older settings file must LOAD ONTO THE MODE THAT BEHAVES THE SAME,
# not reset to the default and not map by matching words.


def test_a_legacy_world_mode_migrates_onto_the_same_behaviour(tmp_path):
    from app.settings_fields import load_world_mode

    # The old "geocentric" was the fixed-noon dial -> noon_up.
    # The old "heliocentric" turned the world -> sky_up.
    assert load_world_mode({"world_mode": "geocentric"}) == "noon_up"
    assert load_world_mode({"world_mode": "heliocentric"}) == "sky_up"


def test_the_migration_never_silently_resets_the_owners_pick(tmp_path):
    """The failure this guards is the quiet one: a legacy value falling
    through to the DEFAULT would look like the app forgetting his
    setting. `heliocentric` is the non-default mode, so a reset shows."""
    from app.settings_fields import load_world_mode

    from config import dial

    migrated = load_world_mode({"world_mode": "heliocentric"})
    assert migrated != dial.WORLD_MODE_DEFAULT, (
        "an old 'heliocentric' profile fell back to the default — the "
        "owner's chosen mode was silently thrown away by the rename"
    )


def test_a_current_world_mode_still_loads_and_an_unknown_one_still_raises():
    import pytest as _pytest

    from app.settings_fields import load_world_mode

    assert load_world_mode({"world_mode": "sky_up"}) == "sky_up"
    assert load_world_mode({}) == "noon_up"          # absent = the default
    with _pytest.raises(ValueError):
        load_world_mode({"world_mode": "ptolemy"})
