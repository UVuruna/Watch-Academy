"""Roster label -> a real, PROVEN QFont.

The two rosters of [The Dial Numerals](../research/hour_numerals.md) §7
name faces the way a designer does ("Bahnschrift Bold", "Arial Black"),
but Qt sees a FAMILY plus a STYLE. `config.dial.NUMERAL_OUTER_FACES` /
`NUMERAL_INNER_FACES` hold that mapping and this module is the only
place that reads it.

WHY THE COVERAGE PROOF EXISTS (verified failure, 2026-08-06): the two
default faces were recovered from `illustrator/Clock 24h.ai` and
installed by hand, and a recovered face can carry a character in its
cmap while its OUTLINE is empty. `QRawFont.supportsCharacter(':')`
answers True for `Bernard MT Condensed` on this machine and the colon
draws nothing at all — as do '.', 'h', 'm' and 'i'. Its ten digits are
perfect. So coverage is proved by GEOMETRY here (the glyph's own path
bounding rect, with a render-and-count-non-blank-pixels fallback), never
by the cmap, and the consequence is written into `config.dial`: the
crown's default face is chosen for full coverage instead of inherited
from the hour band, which needs digits only.
"""

from functools import lru_cache

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QRawFont

from config import dial


class NumeralFontError(Exception):
    """A picked face cannot draw a glyph the band needs — raised at
    settings-apply time so a broken pick names itself loudly there and
    never silently draws a gap mid-paint (Rule #1)."""


def _roster(band: str) -> dict:
    if band == "outer":
        return dial.NUMERAL_OUTER_FACES
    if band == "inner":
        return dial.NUMERAL_INNER_FACES
    raise ValueError(f"unknown numeral band {band!r}")


def face_names(band: str) -> tuple[str, ...]:
    """The roster labels of one band, in the ledger's own order (the
    first is that band's SETTLED default)."""
    return tuple(_roster(band))


def numeral_font(band: str, face: str, pixel_size: float) -> QFont:
    """The roster label `face` of `band` as a QFont at `pixel_size`
    DEVICE pixels. An unknown label raises rather than silently falling
    back to the system font — a settings file naming a face the roster
    dropped must say so."""
    table = _roster(band)
    if face not in table:
        raise NumeralFontError(
            f"{band} numeral face {face!r} is not in the roster "
            f"({sorted(table)})"
        )
    family, style = table[face]
    font = QFont(family)
    font.setPixelSize(max(1, round(pixel_size)))
    if style:
        font.setStyleName(style)
    return font


@lru_cache(maxsize=64)
def glyph_coverage(band: str, face: str, glyphs: tuple[str, ...]) -> dict:
    """`glyph -> True/False`, proved by GEOMETRY: the glyph's own
    `QRawFont.pathForGlyph` bounding rect must have a non-zero area.
    A face whose outlines Qt refuses to hand back (bitmap-only, or a
    backend without path extraction) falls back to rendering the glyph
    and counting non-blank pixels — the same proof by a slower road, so
    a True answer always means "this actually drew something".

    Memoized: a coverage proof is pure in (band, face, glyphs) and the
    settings-apply path asks for it on every change."""
    font = numeral_font(band, face, dial.NUMERAL_COVERAGE_PROBE_PX)
    raw = QRawFont.fromFont(font)
    result = {}
    for glyph in glyphs:
        if glyph == " ":
            result[glyph] = True
            continue
        indexes = raw.glyphIndexesForString(glyph)
        drawn = False
        if len(indexes):
            rect = raw.pathForGlyph(indexes[0]).boundingRect()
            drawn = rect.width() > 0.0 and rect.height() > 0.0
        if not drawn:
            drawn = _renders_non_blank(font, glyph)
        result[glyph] = drawn
    return result


def _renders_non_blank(font: QFont, glyph: str) -> bool:
    """The fallback proof: draw the glyph on transparency and ask
    whether ANY pixel got alpha. Slower than the outline check and used
    only when the outline is unavailable."""
    side = int(dial.NUMERAL_COVERAGE_PROBE_PX) * 2
    image = QImage(side, side, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setFont(font)
    painter.setPen(QColor(dial.NUMERAL_COVERAGE_PROBE_INK))
    painter.drawText(image.rect(), Qt.AlignmentFlag.AlignCenter, glyph)
    painter.end()
    for y in range(0, side, 2):
        for x in range(0, side, 2):
            if image.pixelColor(x, y).alpha() > 0:
                return True
    return False


def missing_glyphs(band: str, face: str, glyphs: tuple[str, ...]) -> tuple[str, ...]:
    """The glyphs of `glyphs` this face cannot draw — empty when the
    face covers what it is being asked for."""
    coverage = glyph_coverage(band, face, glyphs)
    return tuple(glyph for glyph in glyphs if not coverage[glyph])


def assert_covers(band: str, face: str, glyphs: tuple[str, ...]) -> None:
    """Loud failure at settings-apply time when a picked face cannot
    draw what its band needs. No silent substitution: a face that
    cannot say the time must not quietly become another face the user
    never chose."""
    gaps = missing_glyphs(band, face, glyphs)
    if gaps:
        raise NumeralFontError(
            f"{band} numeral face {face!r} draws empty glyphs for "
            f"{list(gaps)} on this install — pick another roster face"
        )


def first_covering_face(band: str, glyphs: tuple[str, ...]) -> str:
    """The FIRST roster face of `band` that provably draws every glyph
    in `glyphs` — the honest way to choose a default for a band whose
    own preferred face is broken on this install (see this module's
    docstring). Raises when the whole roster fails, because at that
    point there is nothing true left to draw."""
    for face in face_names(band):
        if not missing_glyphs(band, face, glyphs):
            return face
    raise NumeralFontError(
        f"no {band} roster face on this install can draw {list(glyphs)}"
    )
