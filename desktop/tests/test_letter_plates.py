"""THE ONE PLATE LAW (owner decree 2026-08-07) — the tooth for the
failure that produced it.

Everything drawn from the owner's plate library — the JEWELS, the whole
CROWN, the DUALS — is a plate taken as the GOLD master and recolored by
the transformer into one of the app's metals or thematic colours. One
style, one source, one algorithm: never a font, never a flat colour of
its own. (The band NUMERALS and MINUTES are the ring's OTHER half —
computed, their own rosters, even/odd parity by design. "JEWELS !=
NUMERALS", owner 2026-08-07.)

WHY THE FAILURE WAS SILENT — the part worth keeping. The crown's digits
were font outlines because the library had no `0`-`9` plates, and
`numeral_fonts.assert_covers` proved that the FONT could draw them.
Nothing anywhere proved a PLATE existed, so a missing alphabet was not an
error at all: it was the documented trigger for a fallback. The renderer
had nothing to report, and reported nothing.

This module is the missing proof. It walks every glyph the library
declares and every glyph the crown can compose, and asserts the file is
really on disk — so an alphabet that is not there fails the suite in the
session that removed it.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from config import constants, dial
from core import numerals
from render import letter_plates


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


# ------------------------------------------------- EVERY GLYPH HAS A PLATE

def test_every_declared_glyph_resolves_to_a_real_file(app):
    """The whole library, glyph by glyph — aliases and composed numbers
    included. This is the assertion whose absence let a missing
    alphabet pass as a design decision."""
    for glyph in constants.LETTER_PLATE_FILES:
        master = letter_plates.plate_path(glyph)
        assert master.exists(), f"{glyph!r} -> {master}"
        assert not QImage(str(master)).isNull(), glyph


def test_every_crown_glyph_has_a_plate(app):
    """The live crown's own alphabet — the ten digits, the colon and the
    `h`/`m`/`i`/`n` of the "12h 35min" cut. The digits are the ones that
    were missing; the lowercase unit letters resolve to their uppercase
    plate, since a plate is a shape and not a case."""
    for glyph in numerals.crown_glyph_alphabet():
        if glyph == " ":
            continue
        assert letter_plates.plate_path(glyph).exists(), glyph


def test_a_missing_plate_raises_instead_of_falling_back(app):
    """The behavioural half of the law. A glyph with no plate is an
    ERROR the caller must handle, never a quiet substitution — that
    substitution is exactly what shipped a font-drawn crown."""
    with pytest.raises(letter_plates.MissingPlate):
        letter_plates.plate_path("☃")           # a snowman has no plate
    assert not letter_plates.has_plate("☃")
    assert letter_plates.has_plate("A")


# ------------------------------------------------------- THE GREEK TWINS

def test_the_greek_twins_share_the_latin_plate_and_add_no_file(app):
    """Fourteen Greek capitals are drawn exactly like a Latin letter, so
    they are an ALIAS, never a second file — THE ONE COPY RULE. Between
    them and the ten with a shape of their own, the Greek alphabet is
    complete."""
    for greek, latin in constants.GREEK_LATIN_TWINS.items():
        assert letter_plates.plate_path(greek) == letter_plates.plate_path(latin)
    assert len(constants.GREEK_LATIN_TWINS) + len(constants.GREEK_OWN_PLATES) == 24
    assert set(constants.LETTER_PLATE_GROUPS["Greek"]) == (
        set(constants.GREEK_LATIN_TWINS) | set(constants.GREEK_OWN_PLATES)
    )
    # And no duplicate file was quietly added beside the alias.
    greek_dir = dial.LETTER_ART_DIR / "greek"
    on_disk = {path.stem for path in greek_dir.glob("*.png")}
    assert on_disk == set(constants.GREEK_OWN_PLATES.values())


# --------------------------------------------------- THE COMPOSED NUMBERS

def test_two_digit_numbers_are_composed_from_the_digit_plates(app):
    """The library holds single digits only (owner 2026-08-07). Each
    two-digit hour seat is built from its own two digits, at their own
    native height, spaced by their INK — and the spacing is his, not an
    invention: at `LETTER_COMPOSE_INK_GAP_FRACTION` the composed "20"
    comes back at exactly the 730x512 he drew."""
    for number in ("12", "15", "16", "18", "20", "21"):
        assert len(constants.LETTER_PLATE_FILES[number]) == 2
        composed = QImage(str(letter_plates.plate_path(number)))
        assert not composed.isNull(), number
        assert composed.height() == 512, number
    assert QImage(str(letter_plates.plate_path("20"))).size().toTuple() == (730, 512)


def test_every_composed_pair_keeps_the_same_ink_clearance(app):
    """ONE STYLE means one SPACING. Spacing the plate BOXES gave every
    pair a different optical gap — measured on the masters, 8 px of real
    clearance between the 1 and the 2 of "12" against 37 between the 2
    and the 0 of "20" — and an independent grader caught the tightest of
    them as "touching" on the live dial. Measured per row, the closest
    ink of the two glyphs must now clear by the same amount in every
    composed number."""
    target = round(512 * dial.LETTER_COMPOSE_INK_GAP_FRACTION)
    for number in ("12", "15", "16", "18", "20", "21"):
        left, right = (
            QImage(str(letter_plates.plate_path(digit))) for digit in number
        )
        advance = letter_plates._ink_advance(
            left, right, 512 * dial.LETTER_COMPOSE_INK_GAP_FRACTION,
        )
        clearance = min(
            advance + r_x - l_x - 1
            for l_x, r_x in zip(
                letter_plates._row_extents(left, rightmost=True),
                letter_plates._row_extents(right, rightmost=False),
            )
            if l_x is not None and r_x is not None
        )
        assert clearance == target, (number, clearance, target)


def test_no_multi_digit_plate_lingers_on_disk(app):
    """The composites the owner deleted may not creep back: `numerals/`
    holds the ten digits and nothing else, or the composition law has a
    second, drifting source of truth (Rule #6)."""
    numerals_dir = dial.LETTER_ART_DIR / "numerals"
    assert sorted(path.stem for path in numerals_dir.glob("*.png")) == list("0123456789")


# ------------------------------------------------------ THE LIBRARY'S HOME

def test_the_library_is_not_under_the_ring(app):
    """It moved out on the owner's ruling — "nije mu to mesto jer nisu
    oni samo za ring" — because the ring jewels, all four crown surfaces
    and (planned) the subdial read the same plates."""
    assert dial.LETTER_ART_DIR == (
        dial.LETTER_ART_DIR.parent / "letters"
    )
    assert dial.LETTER_ART_DIR.parent.name == "instrument"
    assert not (dial.RING_FACE_DIR / "letters").exists()
    assert sorted(
        path.name for path in dial.LETTER_ART_DIR.iterdir() if path.is_dir()
    ) == ["emblems", "greek", "latin", "numerals", "symbols"]


def test_emblems_are_picked_never_typed(app):
    """The line the owner asked to be drawn ("u symbols je i eye... mozda
    ne pripada tu, odluci"): SYMBOLS are characters a crown text can
    spell, EMBLEMS are seat art you pick. So no emblem may reach the
    crown-text whitelist, and the typeable symbols all must."""
    for glyph, plates in constants.LETTER_PLATE_FILES.items():
        if plates[0].startswith("emblems/"):
            assert glyph not in constants.RING_CROWN_TEXT_CHARSET, glyph
        elif len(glyph) == 1:
            assert glyph in constants.RING_CROWN_TEXT_CHARSET, glyph
    assert all(
        constants.LETTER_PLATE_FILES[glyph][0].startswith("emblems/")
        for glyph in constants.LETTER_PLATE_GROUPS["Emblems"]
    )
