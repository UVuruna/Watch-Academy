"""THE REGISTRY's proof — the derived tables ARE today's tables.

`config/registry/` (owner decree 2026-08-01, designed 2026-08-04/05)
moves every theme's data into ONE entry per theme and computes each
legacy table from it in ONE assignment. The migration is only worth
anything if the computed value is INDISTINGUISHABLE from the value the
program shipped with — so every table is compared here, field for
field, against the module that declares it today.

While `constants` and `pantheon` still carry their own literals this
test is a DRIFT ALARM: touch one side only and it fails. Once those
modules read the registry, it becomes the pin that keeps the
derivation honest.
"""

from config import constants, pantheon, registry


def test_the_theme_list_and_its_menu():
    assert registry.THEMES == constants.WEEKDAY_THEMES
    assert registry.MENU_TOP == pantheon.WEEKDAY_MENU_TOP
    assert registry.MENU == pantheon.WEEKDAY_MENU_GROUPS
    assert registry.TITLES == pantheon.WEEKDAY_THEME_TITLES


def test_every_seat_name_stem_and_directory():
    assert registry.NAMES == pantheon.WEEKDAY_THEME_NAMES
    assert registry.FILES == pantheon.WEEKDAY_THEME_FILES
    assert registry.DIRS == pantheon.WEEKDAY_THEME_DIRS


def test_the_sunday_three():
    assert registry.DUAL_NAMES == pantheon.WEEKDAY_DUAL_NAMES
    assert registry.DUAL_FILES == pantheon.WEEKDAY_DUAL_FILES
    assert registry.NINTHS == constants.WEEKDAY_THEME_NINTHS
    assert registry.NINTH_EASTER_EGG == constants.WEEKDAY_THEME_NINTH_EASTER_EGG
    assert registry.NINTH_NIGHT == constants.WEEKDAY_THEME_NINTH_NIGHT
    assert registry.MECHANISMS == constants.NINTH_MECHANISMS


def test_rosters_pantheon_and_titles():
    assert registry.SEAT_ROSTERS == pantheon.WEEKDAY_SEAT_ROSTERS
    assert registry.PANTHEON == pantheon.WEEKDAY_PANTHEON
    assert registry.TITLE_PLATE_SEATS == pantheon.TITLE_PLATE_SEATS


def test_text_sets_and_metal_looks():
    assert registry.ARTICLES == constants.WEEKDAY_THEME_ARTICLES
    assert registry.BLURBS == constants.WEEKDAY_THEME_BLURBS
    assert set(registry.METAL_THEMES) == set(constants.METAL_THEMES)
    for theme in registry.METAL_THEMES:
        assert registry.METALS[theme] == constants.theme_metals(theme)


def test_the_contract_is_complete_for_every_theme():
    """What a new theme MUST declare — the payoff the registry exists
    for: it is knowable UPFRONT, and a half-filled entry fails here
    rather than showing a blank seat on the dial."""
    for key, entry in registry.WEEK.items():
        for field in ("title", "art", "articles", "blurbs", "seats", "sunday"):
            assert field in entry, f"{key} declares no {field}"
        assert set(entry["seats"]) == {
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"
        }, f"{key} does not seat exactly the six weekdays"
        for day, seat in entry["seats"].items():
            assert seat["body"] in registry.BODIES, f"{key}/{day} has no body"
            assert registry.DAYS[day] == seat["body"], (
                f"{key}/{day} names the wrong body — the seat's two names "
                "must agree"
            )
        sunday = entry["sunday"]
        for field in ("name", "ruler", "servant", "stem", "servant_plate"):
            assert field in sunday, f"{key}'s Sunday declares no {field}"


def test_a_double_ninth_always_names_its_mechanism():
    """THE DOUBLE NINTH LAW: two faces contending for one seat is only
    legal with a DEFINED alternation. The registry can state the law on
    its own data now — a second face without a mechanism cannot be
    written down without failing here."""
    for key, entry in registry.WEEK.items():
        ninth = entry.get("ninth")
        if not ninth:
            continue
        if ninth.get("alt") or ninth.get("rotates"):
            assert ninth.get("mechanism") in constants.NINTH_MECHANISM_KINDS, (
                f"{key}'s Ninth has a second face and no declared mechanism"
            )


def test_a_rotating_seat_leads_with_its_own_stem():
    """The declared order IS the rotation order, and the canonical
    member is the plate the config table points at — otherwise the
    lookup that resolves a roster (`pantheon._SEAT_ROSTER_BY_PLATE`)
    cannot find it."""
    for key, entry in registry.WEEK.items():
        for day, seat in entry["seats"].items():
            if "rotates" in seat:
                assert seat["rotates"][0] == seat["stem"], (
                    f"{key}/{day} rotates but its canonical member is not "
                    "the seat's own stem"
                )
        sunday = entry["sunday"]
        if "rotates" in sunday:
            assert sunday["rotates"][0] == sunday["stem"]


def test_every_kind_answers_through_one_view():
    """THE FOUR KINDS, one call each. The dozen, the cube and the wheels
    keep their data where it has always been (owner ruling 2026-08-05 —
    each is already one declarative table in its own section, and moving
    it would cost a reader more than it buys); what the registry owes
    them is a NAMED VIEW, so a caller can ask without knowing which
    module holds which."""
    from config import archetypes, calendar_mounts

    assert registry.themes_of(registry.KINDS[0]) == constants.WEEKDAY_THEMES
    assert registry.themes_of("dozen") == tuple(calendar_mounts.CALENDAR_MOUNTS)
    assert registry.themes_of("wheel") == tuple(archetypes.ARCHETYPES)
    assert registry.themes_of("cube") == ("cube",)
    assert registry.themes_of("nonesuch") == ()


# A theme key is scoped to its KIND, not to the program. TWO collisions
# today, named rather than hidden — both between the Inner Wheel (the
# days ARE their virtues / their sins, seven weekday seats) and a Dozen
# (the Virtue Wheel's twelve Aristotelian seats, the Sins Dozen's twelve
# from Gregory and Dante). Different rosters, different members, one
# shared word; renaming either would cost a settings migration to buy
# nothing.
KNOWN_SHARED_KEYS = {
    "virtues": ("week", "dozen"),
    "sins": ("week", "dozen"),
}


def test_the_only_shared_key_is_the_one_we_have_named():
    """A NEW collision means two rosters silently answering to one name
    — the reverse lookup would then hand a caller the wrong roster."""
    shared = {
        theme: registry.kinds_of(theme)
        for kind in registry.KINDS
        for theme in registry.themes_of(kind)
        if len(registry.kinds_of(theme)) > 1
    }
    assert shared == KNOWN_SHARED_KEYS


def test_the_reverse_lookup_places_every_other_theme_in_one_kind():
    seen: dict[str, str] = {}
    for kind in registry.KINDS:
        for theme in registry.themes_of(kind):
            if theme in KNOWN_SHARED_KEYS:
                continue
            assert theme not in seen, f"{theme} claimed by {seen[theme]} and {kind}"
            seen[theme] = kind
    assert registry.kind_of("greek") == "week"
    assert registry.kind_of("zodiac") == "dozen"
    assert registry.kind_of("prism_council") == "wheel"
    assert registry.kind_of("nonesuch") is None


def test_members_of_reads_the_owning_table_live():
    """A VIEW, never a copy — so the registry cannot disagree with the
    thing it describes."""
    from config import calendar_mounts

    assert registry.members_of("emotions") == (
        calendar_mounts.CALENDAR_MOUNTS["emotions"].members
    )
    norse = registry.members_of("norse")
    assert norse[0] == "Máni"            # Monday leads; the six weekdays first
    assert norse[-2] == "Sól"            # then Sunday's label
    assert norse[-1] == "Yggdrasil"      # then the Ninth
    assert len(registry.members_of("cube")) == 24
