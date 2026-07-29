"""THE UNIVERSAL ROTATION CONVENTION reaches the weekday tree (weekday
ALT ROTATION round, owner 2026-07-20/21): the owner dropped
`assets/weekday/{gemini,chatgpt}/bible/dark/alt/` (11 files each,
mirroring every canonical bible_dark file 1:1) — the first weekday
register to carry `alt/` siblings. These tests drive the REAL bundled
assets (not a synthetic tmp tree — `test_scale_rotation.py` already
pins the generic `rotating_art_file` mechanism in isolation; this file
is the WIRING test: does the weekday resolution chokepoint actually
call it) against `config.pantheon.weekday_theme_body_art` and
`render.layers.theme_ninth`, the two functions every weekday-body-art
draw/hover call site now shares (Rule #5 — no more per-call-site
`theme_dir / f"{...}.png"` duplicates). Also pins THE WEEKLY MANDATE
(owner decree 2026-07-29): cp_corpo's own seat rosters (sun/dual/ninth)
turn by the ISO calendar week's PARITY instead of the daily ordinal
every other roster still uses — `_probe_days` picks the right cadence
per theme so the shared cycle-coverage test still proves every roster
member is reachable."""

from datetime import date, timedelta

from config import constants, pantheon, paths
from render.layers import ninth_table_for, theme_ninth

# Two ordinally-consecutive dates, chosen arbitrarily — with exactly two
# candidates (canonical + one alt/ sibling) any consecutive pair must
# land on different picks (ordinal % 2 alternates).
DAY_A = date(2026, 7, 20)
DAY_B = date(2026, 7, 21)


def _probe_days(theme: str, count: int) -> list:
    """The right PROBE DATES to exercise `count` picks of `theme`'s own
    seat rosters: WEEKLY steps for THE WEEKLY MANDATE (owner decree
    2026-07-29, cp_corpo — `constants.NINTH_MECHANISMS[theme] ==
    "term_weekly"`, ISO week parity), ordinary consecutive days for
    every daily-cadence theme (every other roster). `DAY_A` (2026-07-20,
    ISO week 30, even) anchors either way."""
    if constants.NINTH_MECHANISMS.get(theme) == "term_weekly":
        return [DAY_A + timedelta(weeks=o) for o in range(count)]
    return [date(2026, 7, 20 + o) for o in range(count)]


def test_bible_dark_body_rotates_across_consecutive_ordinals():
    """Every bible_dark BODY (the 7 weekday roster entries) has an
    `alt/` twin on disk now — consecutive days must show a DIFFERENT
    file, and both files must actually exist."""
    for body in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"):
        first = pantheon.weekday_theme_body_art("bible_dark", body, on_date=DAY_A)
        second = pantheon.weekday_theme_body_art("bible_dark", body, on_date=DAY_B)
        assert first != second, body
        assert first.exists(), body
        assert second.exists(), body


def test_bible_dark_body_without_on_date_stays_canonical():
    """The `on_date=None` default (every caller before this round —
    the Encyclopedia gallery, the theme picker grids) is UNCHANGED: the
    plain canonical file, no rotation applied."""
    canonical = pantheon.weekday_theme_body_art("bible_dark", "saturn")
    assert canonical.name == "Cain.png"
    assert canonical == pantheon.weekday_theme_body_art("bible_dark", "saturn")


def test_bible_dark_ninth_circle_rotates():
    """The Ninth plate (`theme_ninth`) shares the exact same wiring —
    `ninth_circle.png` also shipped an `alt/` twin."""
    first = theme_ninth("bible_dark", on_date=DAY_A)
    second = theme_ninth("bible_dark", on_date=DAY_B)
    assert first is not None and second is not None
    name_a, asset_a = first
    name_b, asset_b = second
    assert name_a == name_b == "The Ninth Circle"
    assert asset_a != asset_b
    assert asset_a.exists() and asset_b.exists()


def test_bible_dark_dual_judas_rotates():
    """The Sunday Servant face (WEEKDAY_DUAL_FILES["bible_dark"], the
    same `judas.png` reused as a weekday BODY too) rotates through the
    generic resolver exactly like every other draw-adjacent call site —
    pinned directly here since it has no dedicated per-body wrapper."""
    canonical = pantheon.weekday_art(f"{pantheon.WEEKDAY_DUAL_FILES['bible_dark']}.png")
    first = pantheon.rotating_art_file(canonical, DAY_A)
    second = pantheon.rotating_art_file(canonical, DAY_B)
    assert first != second
    assert first.exists() and second.exists()


def test_theme_without_alt_is_untouched():
    """A theme whose folder ships NO `alt/`/`_v2` siblings (Greek, the
    theme this round shipped no new art for) must return the SAME file
    every day — rotation is a strict no-op when there is nothing to
    rotate between."""
    picks = {
        pantheon.weekday_theme_body_art("greek", "sun", on_date=date(2026, 7, 20 + o))
        for o in range(5)
    }
    assert len(picks) == 1
    # `on_date` also resolves the active art SOURCE (rotating_art_file
    # runs the path through `paths.art_file` first) — with zero
    # rotation candidates besides itself, the single pick must still be
    # the source-resolved canonical file, not a different one.
    assert picks == {
        paths.art_file(pantheon.weekday_theme_body_art("greek", "sun"))
    }


def test_theme_ninth_without_alt_is_untouched():
    """Same no-op law for a Ninth plate with no `alt/` sibling (Gaia,
    the Greek Ninth)."""
    picks = {
        theme_ninth("greek", on_date=date(2026, 7, 20 + o))[1]
        for o in range(5)
    }
    assert len(picks) == 1


# --- THE SEAT ROSTER (completion wave II, Cyberpunk half, Session 32) ---------
# The `_v2` convention above rotates ONE figure's second artwork; a seat
# roster rotates DIFFERENT named figures across one seat. Twelve
# Cyberpunk plates are reachable through this mechanism and through
# nothing else, so these are theme-completeness regressions, not
# nice-to-haves: without the roster they sit on disk unseen, which is the
# exact failure THE THEME COMPLETION LAW was written for.


def test_seat_roster_shows_every_member_across_its_cycle():
    """Every stem declared in `pantheon.WEEKDAY_SEAT_ROSTERS` whose plate
    is on disk must actually appear on the dial within one full turn of
    its own roster — the whole point of the table. A cast the ART DEBT
    REGISTRY names (`tests/art_debt.py`) may be wired ahead of its
    plates: `_roster_candidates` skips a member that is not on disk, so
    the seat shows nothing until art arrives and there is nothing yet to
    rotate between. Every OTHER cast must have all of its members."""
    from tests.art_debt import PENDING_ROSTERS

    for theme, seats in pantheon.WEEKDAY_SEAT_ROSTERS.items():
        directory = pantheon.weekday_art(pantheon.WEEKDAY_THEME_DIRS[theme])
        for seat, stems in seats.items():
            on_disk = [
                stem for stem in stems
                if paths.art_file(directory / f"{stem}.png").exists()
            ]
            if theme not in PENDING_ROSTERS:
                assert on_disk == list(stems), (theme, seat)
            canonical = directory / f"{stems[0]}.png"
            if not paths.art_file(canonical).exists():
                continue                    # art owed, nothing to rotate
            shown = {
                pantheon.rotating_art_file(canonical, day).stem
                for day in _probe_days(theme, len(stems))
            }
            for stem in on_disk:
                resolved = paths.art_file(directory / f"{stem}.png")
                assert resolved.stem in shown, (theme, seat, stem)
        # The canonical stem of every BODY seat is the roster's first
        # member, so the two tables can never drift apart.
        for body in constants.WEEKDAY_BODIES:
            if body in seats:
                assert pantheon.WEEKDAY_THEME_FILES[theme][body] == seats[body][0]


def test_sw_dyad_ninth_is_a_daylight_night_switch():
    """Owner Double-Ninth verdicts (2026-07-29): the Dyad's Ninth is a
    DAYLIGHT/NIGHT switch, not a date rotation — day shows The Ghosts
    (the good side), night shows Exegol (the owner's own words: "the
    duality of that theme pulling the actors to one of two sides").
    SUPERSEDES Session 33's PROVISIONAL date rotation this test used to
    pin under the name `test_sw_dyad_ninth_rotates_through_the_seat_
    roster` — the seat-roster mechanism it proved is now explicitly
    GONE (see the negative assertions below).

    Art-free on purpose: neither plate exists yet, so the assertion is
    on the MECHANISM DISPATCH (`ninth_table_for` — which table
    `theme_ninth` would consult) rather than on a rendered file."""
    assert constants.NINTH_MECHANISMS["sw_dyad"] == "daynight"
    day_name, day_rel = constants.WEEKDAY_THEME_NINTHS["sw_dyad"]
    night_name, night_rel = constants.WEEKDAY_THEME_NINTH_NIGHT["sw_dyad"]
    assert (day_name, day_rel) == (
        "The Ghosts", "sw_dyad/primary/bronze/Ghosts.png",
    )
    assert (night_name, night_rel) == (
        "Exegol", "sw_dyad/primary/bronze/Exegol.png",
    )
    # THE DISPATCH: no alt face at all when inactive; the "daynight"
    # mechanism reaches EXACTLY the night table when active — never the
    # easter-egg one, never both.
    assert ninth_table_for("sw_dyad", active_alt=False) is None
    assert (
        ninth_table_for("sw_dyad", active_alt=True)
        is constants.WEEKDAY_THEME_NINTH_NIGHT
    )
    # The date-rotation path this ninth used to ride is GONE.
    assert "ninth" not in pantheon.WEEKDAY_SEAT_ROSTERS["sw_dyad"]
    assert pantheon._seat_roster_of(pantheon.weekday_art(day_rel)) is None
    assert "sw_dyad" not in constants.WEEKDAY_THEME_NINTH_EASTER_EGG


def test_cp_corpo_throne_mirror_and_ninth_turn_in_lockstep():
    """THE WEEKLY MANDATE (owner decree 2026-07-29) elevates the
    sheet's SYNCHRONIZED PAIR ROTATION from a daily to a WEEKLY
    lockstep: the Power cast's Throne, Mirror and Ninth each hold
    exactly two members, and one ISO calendar week's PARITY lands on
    the same INDEX in all three — Saburo, Yorinobu and Alt Cunningham
    (Arasaka) stand together on EVEN weeks, Rosalind Myers, Kurt Hansen
    and Rache Bartmoss (NUSA) together on ODD ones. It falls out of
    `_pick_weekly_mandate`'s shared modulo and equal roster lengths,
    with no synchronisation flag anywhere; what this pins is that the
    DECLARED order is what rotates, since resolving the pools
    alphabetically would pair Saburo with Rache instead."""
    directory = pantheon.weekday_art(pantheon.WEEKDAY_THEME_DIRS["cp_corpo"])
    pairs = {
        "sun": ("Saburo_Arasaka", "Rosalind_Myers"),
        "dual": ("Yorinobu", "Kurt_Hansen"),
        "ninth": ("Alt_Cunningham", "Rache_Bartmoss"),
    }
    assert pantheon.WEEKDAY_SEAT_ROSTERS["cp_corpo"] == pairs
    even_week, odd_week = date(2026, 7, 26), date(2026, 7, 27)  # ISO 30, 31
    assert even_week.isocalendar()[1] == 30      # Sunday, still week 30
    assert odd_week.isocalendar()[1] == 31        # the very next day
    seen = set()
    for day in (even_week, odd_week):
        index = day.isocalendar()[1] % 2
        seen.add(index)
        for seat, stems in pairs.items():
            picked = pantheon.rotating_art_file(
                directory / f"{stems[0]}.png", day
            ).stem
            assert picked.startswith(stems[index]), (seat, day, picked, index)
    assert seen == {0, 1}, "the two probe dates must cover both turns"


def test_cp_corpo_weekly_mandate_flips_at_the_week_boundary_not_daily():
    """The cadence is WEEKLY, not daily (owner decree 2026-07-29): every
    day INSIDE the same ISO week must show the SAME ruling triple — the
    OLD daily law (`_pick_rotation`) would have flipped Monday vs
    Tuesday — and only a genuine week-boundary crossing (Sunday week 30
    -> Monday week 31) actually flips it."""
    canonical = pantheon.weekday_art(
        "cp_corpo/primary/bronze/Saburo_Arasaka.png"
    )
    monday_w30 = date(2026, 7, 20)
    tuesday_w30 = date(2026, 7, 21)
    sunday_w30 = date(2026, 7, 26)
    monday_w31 = date(2026, 7, 27)
    assert (
        monday_w30.isocalendar()[1]
        == tuesday_w30.isocalendar()[1]
        == sunday_w30.isocalendar()[1]
        == 30
    )
    assert monday_w31.isocalendar()[1] == 31
    ruling_w30 = {
        pantheon.rotating_art_file(canonical, d).stem
        for d in (monday_w30, tuesday_w30, sunday_w30)
    }
    assert len(ruling_w30) == 1, "every day inside week 30 rules the SAME triple"
    assert next(iter(ruling_w30)).startswith("Saburo_Arasaka")
    ruling_w31 = pantheon.rotating_art_file(canonical, monday_w31).stem
    assert ruling_w31.startswith("Rosalind_Myers")


def test_seat_roster_never_captures_a_plate_outside_its_own_theme():
    """The lookup is keyed on (theme folder, stem), so a roster in one
    cast can never pull a same-named plate out of another — and a
    theme with no roster at all keeps the plain `_v2` behaviour. Both
    Cyberpunk casts seat an 'Arasaka' plate under different stems, which
    is the collision this key shape exists for."""
    gangs = pantheon.weekday_art(pantheon.WEEKDAY_THEME_DIRS["cp_gangs"])
    # cp_gangs' Sunday Ruler is NOT in a roster: it must not rotate.
    picks = {
        pantheon.rotating_art_file(gangs / "Arasaka.png", date(2026, 7, 20 + o))
        for o in range(4)
    }
    assert len(picks) == 1
    assert pantheon._seat_roster_of(gangs / "Arasaka.png") is None
    # ... while the Power cast's own Saburo plate does.
    corpo = pantheon.weekday_art(pantheon.WEEKDAY_THEME_DIRS["cp_corpo"])
    assert pantheon._seat_roster_of(corpo / "Saburo_Arasaka.png") is not None


def test_seat_roster_rotates_the_colored_register_too():
    """The colored/ sibling is the same seat wearing a different look,
    so it must show the same figure on the same day — otherwise the
    'Colored' menu option would silently show a different member of the
    roster than the bronze one."""
    for theme in ("cp_gangs", "cp_street", "cp_corpo"):
        for body in ("moon", "mars", "mercury", "venus", "saturn", "sun"):
            for offset in range(3):
                day = date(2026, 7, 20 + offset)
                bronze = pantheon.weekday_theme_body_art(theme, body, on_date=day)
                colored = pantheon.weekday_theme_body_art(
                    theme, body, on_date=day, colored=True,
                )
                assert colored.parent.name == "colored", (theme, body)
                assert bronze.name == colored.name, (theme, body, day)


def test_weekday_theme_body_art_colored_flag_still_works():
    """The `colored` flag (the metal themes' sibling folder swap, moved
    into this function from the three call sites it used to be re-typed
    at) is untouched by adding `on_date` — a metal theme's colored/
    plate still resolves under its own subfolder."""
    bronze = pantheon.weekday_theme_body_art("greek", "sun")
    colored = pantheon.weekday_theme_body_art("greek", "sun", colored=True)
    assert bronze != colored
    assert colored.parent.name == "colored"
