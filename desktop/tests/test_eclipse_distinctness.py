"""NO TWO ECLIPSE DISPLAYS MAY DRAW THE SAME PICTURE (owner order
2026-08-13, "skoro sve slikamo isto ... zato i treba rework").

Seven catalog types, six display styles, and before the rework four
combinations rendered ONE byte-identical image while two more pairs
were visually indistinguishable. A SHA-256 comparison found the first
group and missed the second: `solar_partial_halo` (magnitude 0.62) and
`solar_total_halo` (1.05) differed in a handful of alpha values and were
the same picture to the eye — the owner saw it, the hash did not.

So this tooth measures what a PERSON would call "the same picture",
never a hash. Every plate is composited on black and reduced to a 64x64
thumbnail — the scale at which fine detail stops mattering and only
shape, size and colour are left — and then compared on TWO axes that
are deliberately blind to the thing the eye is blind to:

* STRUCTURE — the luma thumbnail normalized to zero mean and unit
  contrast, then differenced. A picture that is only DIMMER than
  another scores zero here, which is the whole point: the pre-rework
  `solar_partial_halo` and `solar_total_halo` differed by nothing but a
  global alpha (0.71 vs 1.0 glow strength), a plain mean-difference
  measure scored them 1.76/255 apart, and the owner still called them
  one picture. He was right and the plain measure was wrong.
* COLOUR — each pixel's chroma normalized by its own brightness, then
  differenced. This is what separates the annular ring-of-fire orange
  from the eclipse red and the blood-moon copper from a grey wash,
  again regardless of how bright either is.

A pair counts as TWO pictures if it clears EITHER floor; it is "the
same picture" only when it clears neither. The floors are calibrated
against the known-bad pair rather than chosen for comfort — see
`test_the_measure_flags_the_owners_pair_on_the_old_geometry`, which
reconstructs the pre-rework halo and requires the measure to condemn it.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from render import eclipse_plates
from render.eclipse_style import NOT_YET_PAINTED_STYLES

# The thumbnail the comparison is made at, and the two floors a pair
# must clear to count as two different pictures. Both are in units of
# their own axis (see the module docstring), and clearing EITHER is
# enough — a pair that differs only in shape, or only in colour, is
# still two pictures.
THUMB_PX = 64
BLOCK_PX = 8                # the region the worst-block search works in
STRUCTURE_FLOOR = 0.20      # worst-block normalized-luma difference
COLOUR_FLOOR = 0.035        # worst-block normalized-chroma difference


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def plate_signature(image: QImage) -> tuple[list[float], list[float]]:
    """One plate reduced to what the eye keeps: composited on the black
    the dial itself sits on (so a difference in ALPHA counts exactly as
    much as it will on screen, never more), scaled down to `THUMB_PX`,
    and split into the two brightness-blind axes the module docstring
    describes — (normalized luma, normalized chroma)."""
    ground = QImage(image.size(), QImage.Format.Format_ARGB32)
    ground.fill(0xFF000000)
    painter = QPainter(ground)
    painter.drawImage(0, 0, image)
    painter.end()
    thumb = ground.scaled(
        THUMB_PX, THUMB_PX,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    ).convertToFormat(QImage.Format.Format_RGB32)
    raw = thumb.constBits().tobytes()
    # RGB32 is BGRx on every platform Qt builds this format for; the
    # fourth byte is a constant and is dropped.
    luma = []
    chroma = []
    for index in range(0, len(raw), 4):
        blue, green, red = raw[index], raw[index + 1], raw[index + 2]
        value = 0.299 * red + 0.587 * green + 0.114 * blue
        luma.append(value)
        # Chroma normalized by the pixel's OWN brightness, so a dim red
        # and a bright red are the same colour and only a genuine hue
        # shift moves the number. +1 keeps black pixels finite.
        total = red + green + blue + 1.0
        chroma.append(red / total)
        chroma.append(green / total)
    mean = sum(luma) / len(luma)
    spread = (sum((v - mean) ** 2 for v in luma) / len(luma)) ** 0.5
    # Unit contrast: a plate that is merely a dimmer copy of another
    # lands on the same normalized luma, which is exactly the blindness
    # this measure needs (the owner's own pair, module docstring).
    normalized = [(v - mean) / max(spread, 1e-6) for v in luma]
    return normalized, chroma


def _block_max(first: list[float], second: list[float], stride: int) -> float:
    """The LARGEST difference any one region of the picture carries.

    Averaged over the whole plate, every real change drowns: the plate
    is mostly night ground, and a mark that occupies 2 % of it moves a
    whole-image average by almost nothing — which is how the first cut
    of this measure scored a genuine ring of fire lower than the noise
    between two identical pictures. A person does not average; a person
    notices the ONE place where the two pictures disagree. So the
    thumbnail is cut into `BLOCK_PX` squares and the worst block wins.
    """
    worst = 0.0
    for top in range(0, THUMB_PX, BLOCK_PX):
        for left in range(0, THUMB_PX, BLOCK_PX):
            total = 0.0
            count = 0
            for row in range(top, top + BLOCK_PX):
                base = row * THUMB_PX * stride
                for column in range(left, left + BLOCK_PX):
                    for channel in range(stride):
                        index = base + column * stride + channel
                        total += abs(first[index] - second[index])
                        count += 1
            worst = max(worst, total / count)
    return worst


def similarity(
    first: tuple[list[float], list[float]],
    second: tuple[list[float], list[float]],
) -> tuple[float, float]:
    """(structure distance, colour distance) — small numbers on BOTH
    axes mean a person would call the two plates one picture."""
    return (
        _block_max(first[0], second[0], 1),
        _block_max(first[1], second[1], 2),
    )


def _every_plate() -> dict[str, QImage]:
    plates = {}
    for kind, types in eclipse_plates.TYPES.items():
        for type_ in types:
            for style in eclipse_plates.STYLES[kind]:
                plates[f"{kind}_{type_}_{style}"] = eclipse_plates._draw_plate(
                    kind, type_, style
                )
    return plates


def _name_parts(name: str) -> tuple[str, str, str]:
    """`"{kind}_{type}_{style}"` -> `(kind, type, style)`, parsed against
    the real rosters rather than guessed from underscores — a style
    name may itself contain one (`magnitude_arc`, `blood_moon`, ...)."""
    kind, rest = name.split("_", 1)
    for type_ in eclipse_plates.TYPES[kind]:
        if rest == type_ or rest.startswith(type_ + "_"):
            style = rest[len(type_) + 1:]
            return kind, type_, style
    raise ValueError(f"unparsable plate name {name!r}")


def _is_declared_not_yet_painted(name: str) -> bool:
    """True when `name` names a style still listed in
    `render.eclipse_style.NOT_YET_PAINTED_STYLES` — the ballot's six
    new names (owner 2026-08-13) that currently borrow another style's
    picture ON PURPOSE, declared and reasoned in that module rather
    than a silent alias."""
    kind, _type, style = _name_parts(name)
    return (kind, style) in NOT_YET_PAINTED_STYLES


def test_no_two_eclipse_displays_render_the_same_picture(app):
    """Every legal (kind, type, style) against every other. A failure
    names the pair and its numbers, because the fix is always either a
    style that ignores the type or a type aliased onto another.

    EXEMPTION (owner ballot 2026-08-13): the six new display styles
    with no painter yet (`render.eclipse_style.NOT_YET_PAINTED_STYLES`)
    are ALLOWED to render the same picture as the style they borrow —
    that sameness is this round's declared, honest state, not the
    silent alias this law exists to catch. The exemption shrinks on its
    own as painters land: removing a name from that module's fallback
    table drops it from the exemption too, and this law starts holding
    it to the same bar as every native style."""
    plates = _every_plate()
    # 4 solar types x 6 solar styles + 3 lunar types x 6 lunar styles —
    # the matrix grew with the ballot's six new names (was 4x3 + 3x3).
    assert len(plates) == 42, "the legal matrix is 4x6 solar + 3x6 lunar"
    signatures = {name: plate_signature(image) for name, image in plates.items()}
    names = sorted(signatures)
    same = []
    for index, first in enumerate(names):
        for second in names[index + 1:]:
            if _is_declared_not_yet_painted(first) or _is_declared_not_yet_painted(second):
                continue
            structure, colour = similarity(
                signatures[first], signatures[second]
            )
            if structure < STRUCTURE_FLOOR and colour < COLOUR_FLOOR:
                same.append(f"{first} == {second} (structure {structure:.3f}, "
                            f"colour {colour:.4f})")
    assert not same, (
        "these eclipse displays draw the same picture:\n  " + "\n  ".join(same)
    )


def test_the_owners_own_pair_is_far_apart(app):
    """The pair his eye caught and the hash did not, pinned by name: a
    62 % partial Sun and a totally eclipsed one, both in the "halo"
    style, must be clearly different pictures — the style has to read
    the magnitude."""
    partial = plate_signature(eclipse_plates._draw_plate("solar", "partial", "halo"))
    total = plate_signature(eclipse_plates._draw_plate("solar", "total", "halo"))
    structure, colour = similarity(partial, total)
    assert structure > STRUCTURE_FLOOR or colour > COLOUR_FLOOR, (
        f"the halo style is magnitude-blind again (structure {structure:.3f}, "
        f"colour {colour:.4f})"
    )


def test_the_measure_flags_the_owners_pair_on_the_old_geometry(app, monkeypatch):
    """THE CALIBRATION, kept executable instead of written down.

    A distinctness measure is only worth its floors if it CONDEMNS the
    picture the owner condemned. So the pre-rework "halo" is rebuilt
    here — the style drew no mark at all, leaving only the caller's
    glow, whose strength was the sole difference between a 62 % partial
    and totality — and the measure must call the two one picture. If a
    later round loosens these floors far enough to let that pair pass,
    this test fails and says why.
    """
    from render import marker_marks

    monkeypatch.setattr(
        marker_marks, "draw_solar_eclipse",
        lambda *args, **kwargs: None,       # the style as it was: silent
    )
    partial = plate_signature(eclipse_plates._draw_plate("solar", "partial", "halo"))
    total = plate_signature(eclipse_plates._draw_plate("solar", "total", "halo"))
    structure, colour = similarity(partial, total)
    assert structure < STRUCTURE_FLOOR and colour < COLOUR_FLOOR, (
        "the floors have drifted so far that the owner's own known-bad "
        f"pair would now pass (structure {structure:.3f}, colour {colour:.4f})"
    )


def test_hybrid_is_not_an_alias_of_total(app):
    """A hybrid eclipse is total on part of its track and annular on the
    rest. It used to be MAPPED onto the total state, which made the two
    identical in every style at once."""
    from config import glow

    assert glow.ECLIPSE_TYPE_STATE[("solar", "hybrid")] == "solar_hybrid"
    for style in eclipse_plates.STYLES["solar"]:
        hybrid = plate_signature(eclipse_plates._draw_plate("solar", "hybrid", style))
        total = plate_signature(eclipse_plates._draw_plate("solar", "total", style))
        structure, colour = similarity(hybrid, total)
        assert structure > STRUCTURE_FLOOR or colour > COLOUR_FLOOR, (
            f"hybrid and total draw the same {style} picture "
            f"(structure {structure:.3f}, colour {colour:.4f})"
        )
