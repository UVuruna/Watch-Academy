"""THE DIAL LAW's guard — a dial seat is 1:1, measured on the file.

Owner decree 2026-08-04, and the reason it is a MEASURING test rather
than a written rule: the owner asked repeatedly for round plates on the
dial, and every session drew the tall stained-glass lancets anyway —
because the opposite rule was written INTO the code as "THE TWO-TYPE
LAW" (config/archetypes.py, 2026-07-18), and a session reads the law it
finds. That law is deleted; this test replaces it, and it opens the
actual PNG.

The law: a seat on the dial may hold ONLY a round — or square — plate,
aspect 1:1. Never a lancet, never anything stretched. Documented
exception: wide art whose overflow is the point (Saturn's rings).
"""

import pytest

from config import archetypes, paths

# How far a plate may stray from square before it is not a round plate.
# The generated badges measure 0.99-1.03; a lancet measures 0.37-0.58,
# so anything in between is a mistake rather than a style.
ASPECT_TOLERANCE = 0.12

# The ONE documented exception (owner: "planeta istih dimenzija kao
# ostale, prstenovi vire") — art whose overflow beyond the frame IS the
# subject. Stems, not paths: the exemption follows the figure.
WIDE_ART_EXEMPT = frozenset({"Saturn"})


def _dial_plates():
    """(archetype key, figure name, resolved dial plate) for every seat
    the dial can draw, centres included."""
    for key, spec in archetypes.ARCHETYPES.items():
        figures = list(archetypes.figures(key))
        centre = archetypes.center(key)
        if centre:
            figures.append(centre)
        for fig in figures:
            plate = archetypes.dial_plate(fig["file"])
            yield key, fig.get("name", "?"), plate


def test_every_dial_plate_resolves_to_the_circle_register():
    """The seat's plate is its family's `circle` register — computed by
    `archetypes.dial_plate`, never tabulated. A path that still points
    at the lancet register would draw a lancet on the dial."""
    offenders = [
        f"{key} / {name}: {plate}"
        for key, name, plate in _dial_plates()
        if plate.parts[-3] != "circle"
    ]
    assert not offenders, (
        "THE DIAL LAW (owner decree 2026-08-04): these seats resolve to "
        "something other than their family's circle register — the dial "
        "holds round plates only: " + ", ".join(offenders)
    )


def test_every_dial_plate_on_disk_is_square():
    """THE MEASURE, not the promise: open the file the dial will draw
    and check its sides. A plate that has not been generated is skipped
    — the renderer's graceful-absent law draws the figure's NAME, which
    is the honest outcome and never a lancet."""
    QtGui = pytest.importorskip("PySide6.QtGui")
    offenders = []
    measured = 0
    for key, name, plate in _dial_plates():
        resolved = paths.art_file(plate)
        if resolved is None or not resolved.exists():
            continue
        if resolved.stem.split("_")[0] in WIDE_ART_EXEMPT:
            continue
        image = QtGui.QImage(str(resolved))
        if image.isNull() or not image.height():
            continue
        measured += 1
        aspect = image.width() / image.height()
        if abs(aspect - 1.0) > ASPECT_TOLERANCE:
            offenders.append(
                f"{key} / {name}: {resolved.name} is {image.width()}x"
                f"{image.height()} (aspect {aspect:.2f})"
            )
    assert not offenders, (
        "THE DIAL LAW (owner decree 2026-08-04): these plates are not "
        "1:1 and a dial seat may hold nothing else. Regenerate them "
        "square, or — if the overflow is the subject, as with Saturn's "
        "rings — add the stem to WIDE_ART_EXEMPT with the owner's word: "
        + ", ".join(offenders)
    )
    assert measured, (
        "no dial plate was measured at all — the resolver or the asset "
        "tree moved, and this guard silently stopped guarding"
    )


def test_the_two_type_law_is_gone():
    """The deleted law must STAY deleted: while a portrait branch exists
    anywhere, a future session can read it and obey it instead of the
    owner. This is the whole reason the instruction kept failing."""
    for dead in (
        "ARCHETYPE_PORTRAIT_ASPECT_MAX", "ARCHETYPE_PORTRAIT_STANDARD_ASPECT",
    ):
        assert not hasattr(archetypes, dead), (
            f"{dead} is back — THE TWO-TYPE LAW was deleted on 2026-08-04 "
            "because sessions obeyed it instead of the owner's own "
            "instruction. Reinstating it needs the owner's word."
        )
    from render import archetype_geometry

    assert not hasattr(archetype_geometry, "archetype_portrait_height"), (
        "archetype_portrait_height is back — the dial has one size for "
        "every seat now (the slot size), and a second one would be the "
        "lancet path returning."
    )
