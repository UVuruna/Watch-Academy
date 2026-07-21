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
    assert canonical.name == "cain.png"
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
    canonical = defaults.WEEKDAY_ART_DIR / f"{defaults.WEEKDAY_DUAL_FILES['bible_dark']}.png"
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


def test_weekday_theme_body_art_colored_flag_still_works():
    """The `colored` flag (the metal themes' sibling folder swap, moved
    into this function from the three call sites it used to be re-typed
    at) is untouched by adding `on_date` — a metal theme's colored/
    plate still resolves under its own subfolder."""
    bronze = defaults.weekday_theme_body_art("greek", "sun")
    colored = defaults.weekday_theme_body_art("greek", "sun", colored=True)
    assert bronze != colored
    assert colored.parent.name == "colored"
