"""THE AVAILABILITY FIELD's guard (owner-sealed ballot 2026-08-12).

Pins the base/locked split so a future edit to either `WEEK` or
`AVAILABILITY` cannot silently drift the other out of coverage, and
pins the owner's exact 10-key base list by name — not by count, so a
swap of one key for another still fails here.
"""

from config.registry import availability
from config.registry.week import WEEK

EXACT_BASE_KEYS = frozenset({
    "planets",
    "planet_signs",
    "planets_art",
    "cosmos",
    "continents",
    "profession",
    "corporate",
    "virtues",
    "sins",
    "moods",
})


def test_every_availability_key_is_a_real_week_key_and_vice_versa():
    assert set(availability.AVAILABILITY) == set(WEEK)


def test_the_exact_base_list_the_owner_sealed():
    assert availability.BASE_THEME_KEYS == EXACT_BASE_KEYS


def test_base_and_locked_partition_the_whole_set():
    base = availability.BASE_THEME_KEYS
    locked = availability.LOCKED_THEME_KEYS
    assert base & locked == frozenset()
    assert base | locked == set(WEEK)
    for key, tier in availability.AVAILABILITY.items():
        assert tier in ("base", "locked")
        assert (tier == "base") == (key in base)
        assert (tier == "locked") == (key in locked)


def test_is_theme_unlocked_reads_the_table():
    from config import registry

    for key in EXACT_BASE_KEYS:
        assert registry.is_theme_unlocked(key) is True
    locked_key = next(iter(availability.LOCKED_THEME_KEYS))
    assert registry.is_theme_unlocked(locked_key) is False
    assert registry.is_theme_unlocked(locked_key, all_unlocked=True) is True
    assert registry.is_theme_unlocked("nonesuch") is False


def test_base_theme_keys_accessor_matches_the_table():
    from config import registry

    assert registry.base_theme_keys() == availability.BASE_THEME_KEYS
