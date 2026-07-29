"""THE UNIVERSAL ROTATION CONVENTION reaches the weekday tree (weekday
ALT ROTATION round, owner 2026-07-20/21): the owner dropped
`assets/weekday/{gemini,chatgpt}/bible/dark/alt/` (11 files each,
mirroring every canonical bible_dark file 1:1) — the first weekday
register to carry `alt/` siblings. These tests drive the REAL bundled
assets (not a synthetic tmp tree — `test_scale_rotation.py` already
pins the generic `rotating_art_file` mechanism in isolation; this file
is the WIRING test: does the weekday resolution chokepoint actually
call it) against `config.defaults.weekday_theme_body_art` and
`render.layers.theme_ninth`, the two functions every weekday-body-art
draw/hover call site now shares (Rule #5 — no more per-call-site
`theme_dir / f"{...}.png"` duplicates)."""

from datetime import date

from config import defaults, paths
from render.layers import theme_ninth

# Two ordinally-consecutive dates, chosen arbitrarily — with exactly two
# candidates (canonical + one alt/ sibling) any consecutive pair must
# land on different picks (ordinal % 2 alternates).
DAY_A = date(2026, 7, 20)
DAY_B = date(2026, 7, 21)


def test_bible_dark_body_rotates_across_consecutive_ordinals():
    """Every bible_dark BODY (the 7 weekday roster entries) has an
    `alt/` twin on disk now — consecutive days must show a DIFFERENT
    file, and both files must actually exist."""
    for body in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"):
        first = defaults.weekday_theme_body_art("bible_dark", body, on_date=DAY_A)
        second = defaults.weekday_theme_body_art("bible_dark", body, on_date=DAY_B)
        assert first != second, body
        assert first.exists(), body
        assert second.exists(), body


def test_bible_dark_body_without_on_date_stays_canonical():
    """The `on_date=None` default (every caller before this round —
    the Encyclopedia gallery, the theme picker grids) is UNCHANGED: the
    plain canonical file, no rotation applied."""
    canonical = defaults.weekday_theme_body_art("bible_dark", "saturn")
    assert canonical.name == "Cain.png"
    assert canonical == defaults.weekday_theme_body_art("bible_dark", "saturn")


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
    canonical = defaults.weekday_art(f"{defaults.WEEKDAY_DUAL_FILES['bible_dark']}.png")
    first = defaults.rotating_art_file(canonical, DAY_A)
    second = defaults.rotating_art_file(canonical, DAY_B)
    assert first != second
    assert first.exists() and second.exists()


def test_theme_without_alt_is_untouched():
    """A theme whose folder ships NO `alt/`/`_v2` siblings (Greek, the
    theme this round shipped no new art for) must return the SAME file
    every day — rotation is a strict no-op when there is nothing to
    rotate between."""
    picks = {
        defaults.weekday_theme_body_art("greek", "sun", on_date=date(2026, 7, 20 + o))
        for o in range(5)
    }
    assert len(picks) == 1
    # `on_date` also resolves the active art SOURCE (rotating_art_file
    # runs the path through `paths.art_file` first) — with zero
    # rotation candidates besides itself, the single pick must still be
    # the source-resolved canonical file, not a different one.
    assert picks == {
        paths.art_file(defaults.weekday_theme_body_art("greek", "sun"))
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
    """Every stem declared in `defaults.WEEKDAY_SEAT_ROSTERS` must
    actually appear on the dial within one full turn of its own roster
    — the whole point of the table."""
    from config import constants

    for theme, seats in defaults.WEEKDAY_SEAT_ROSTERS.items():
        directory = defaults.weekday_art(defaults.WEEKDAY_THEME_DIRS[theme])
        for seat, stems in seats.items():
            canonical = directory / f"{stems[0]}.png"
            shown = {
                defaults.rotating_art_file(canonical, date(2026, 7, 20 + o)).stem
                for o in range(len(stems))
            }
            for stem in stems:
                resolved = paths.art_file(directory / f"{stem}.png")
                assert resolved.exists(), (theme, seat, stem)
                assert resolved.stem in shown, (theme, seat, stem)
        # The canonical stem of every BODY seat is the roster's first
        # member, so the two tables can never drift apart.
        for body in constants.WEEKDAY_BODIES:
            if body in seats:
                assert defaults.WEEKDAY_THEME_FILES[theme][body] == seats[body][0]


def test_cp_corpo_throne_mirror_and_ninth_turn_in_lockstep():
    """The sheet's SYNCHRONIZED PAIR ROTATION: the Power cast's Throne,
    Mirror and Ninth each hold exactly two members, so one date lands on
    the same INDEX in all three — Saburo, Yorinobu and Alt Cunningham
    stand together, Rosalind Myers, Kurt Hansen and Rache Bartmoss stand
    together. It falls out of `_pick_rotation`'s shared modulo and equal
    roster lengths, with no synchronisation flag anywhere; what this
    pins is that the DECLARED order is what rotates, since resolving the
    pools alphabetically would pair Saburo with Rache instead."""
    directory = defaults.weekday_art(defaults.WEEKDAY_THEME_DIRS["cp_corpo"])
    pairs = {
        "sun": ("Saburo_Arasaka", "Rosalind_Myers"),
        "dual": ("Yorinobu", "Kurt_Hansen"),
        "ninth": ("Alt_Cunningham", "Rache_Bartmoss"),
    }
    assert defaults.WEEKDAY_SEAT_ROSTERS["cp_corpo"] == pairs
    seen = set()
    for day in (DAY_A, DAY_B):
        index = (day.toordinal() // defaults.ROTATION_DAYS) % 2
        seen.add(index)
        for seat, stems in pairs.items():
            picked = defaults.rotating_art_file(
                directory / f"{stems[0]}.png", day
            ).stem
            assert picked.startswith(stems[index]), (seat, day, picked, index)
    assert seen == {0, 1}, "the two probe dates must cover both turns"


def test_seat_roster_never_captures_a_plate_outside_its_own_theme():
    """The lookup is keyed on (theme folder, stem), so a roster in one
    cast can never pull a same-named plate out of another — and a
    theme with no roster at all keeps the plain `_v2` behaviour. Both
    Cyberpunk casts seat an 'Arasaka' plate under different stems, which
    is the collision this key shape exists for."""
    gangs = defaults.weekday_art(defaults.WEEKDAY_THEME_DIRS["cp_gangs"])
    # cp_gangs' Sunday Ruler is NOT in a roster: it must not rotate.
    picks = {
        defaults.rotating_art_file(gangs / "Arasaka.png", date(2026, 7, 20 + o))
        for o in range(4)
    }
    assert len(picks) == 1
    assert defaults._seat_roster_of(gangs / "Arasaka.png") is None
    # ... while the Power cast's own Saburo plate does.
    corpo = defaults.weekday_art(defaults.WEEKDAY_THEME_DIRS["cp_corpo"])
    assert defaults._seat_roster_of(corpo / "Saburo_Arasaka.png") is not None


def test_seat_roster_rotates_the_colored_register_too():
    """The colored/ sibling is the same seat wearing a different look,
    so it must show the same figure on the same day — otherwise the
    'Colored' menu option would silently show a different member of the
    roster than the bronze one."""
    for theme in ("cp_gangs", "cp_street", "cp_corpo"):
        for body in ("moon", "mars", "mercury", "venus", "saturn", "sun"):
            for offset in range(3):
                day = date(2026, 7, 20 + offset)
                bronze = defaults.weekday_theme_body_art(theme, body, on_date=day)
                colored = defaults.weekday_theme_body_art(
                    theme, body, on_date=day, colored=True,
                )
                assert colored.parent.name == "colored", (theme, body)
                assert bronze.name == colored.name, (theme, body, day)


def test_weekday_theme_body_art_colored_flag_still_works():
    """The `colored` flag (the metal themes' sibling folder swap, moved
    into this function from the three call sites it used to be re-typed
    at) is untouched by adding `on_date` — a metal theme's colored/
    plate still resolves under its own subfolder."""
    bronze = defaults.weekday_theme_body_art("greek", "sun")
    colored = defaults.weekday_theme_body_art("greek", "sun", colored=True)
    assert bronze != colored
    assert colored.parent.name == "colored"
