"""The ONE door between a glyph and the owner's plate library
(`assets/instrument/letters/`) — see
[Letter Plates](__about/letter_plates.md).

THE ONE PLATE LAW (owner decree 2026-08-07): every GLYPH the dial draws
— wherever it stands — is a plate from this library, taken as the GOLD
master and recolored by the transformer into one of the app's metals or
thematic colours. One style, one source, one algorithm: never a font,
never a flat colour of its own. This module resolves the glyph; the
caller recolors and draws it exactly as a ring jewel is.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter

from config import constants, dial, paths
from render import raster_store

# ══════════════════════════════ RESOLUTION ═══════════════════════════


class MissingPlate(LookupError):
    """No plate can draw this glyph.

    RAISED, never swallowed (owner decree 2026-08-07, the defect that
    earned this module): the old crown treated an absent plate as the
    trigger for a font fallback, so a whole missing alphabet reported
    nothing at all. A caller that cannot draw a glyph must say so."""


def plate_paths(glyph: str) -> tuple[Path, ...]:
    """The gold master(s) behind `glyph`, in reading order — one entry
    for an ordinary glyph, two for a composed hour number. Resolves the
    Greek twins and the crown's lowercase unit cut through
    `constants.LETTER_PLATE_FILES`'s own aliases (Rule #5: the alias
    lives in the table, the lookup lives here)."""
    files = constants.LETTER_PLATE_FILES.get(glyph)
    if files is None and len(glyph) == 1 and glyph.isalpha():
        # The crown's "12h 35min" cut spells h/m/i/n in lowercase; the
        # library is uppercase (a plate is a shape, not a case).
        files = constants.LETTER_PLATE_FILES.get(glyph.upper())
    if files is None:
        raise MissingPlate(
            f"no letter plate for {glyph!r} — the library at "
            f"{dial.LETTER_ART_DIR} has no master for it"
        )
    return tuple(dial.LETTER_ART_DIR / name for name in files)


def plate_path(glyph: str) -> Path:
    """The ONE drawable gold master for `glyph` — the path every caller
    hands to `asset_recolor.jewel_metal_file`.

    A multi-plate glyph (12, 15, 16, 18, 20, 21) is COMPOSED here and
    cached as a real file, so nothing downstream needs to know that the
    number is two plates: the metal derivation, the ring's
    `pixmap_by_height` and the crown's tile builder all see one
    ordinary master."""
    parts = plate_paths(glyph)
    if len(parts) == 1:
        # `existing_art_file`, not `art_file(...).exists()`: the live
        # crown resolves its whole alphabet on EVERY paint, and THE ONE
        # COPY RULE's second pass (`tests/test_repeat_work.py`) forbids
        # re-stating a file the resolver has already found.
        resolved = paths.existing_art_file(parts[0])
        if resolved is None:
            raise MissingPlate(f"letter plate missing on disk: {parts[0]}")
        return resolved
    return _composed_master(parts)


def has_plate(glyph: str) -> bool:
    """Whether `glyph` resolves at all — for the callers that FILTER a
    typed string (a custom crown text) rather than fail on it."""
    try:
        plate_paths(glyph)
    except MissingPlate:
        return False
    return True


# ═════════════════════════════ COMPOSITION ═══════════════════════════

#: `(source paths) -> the composed master on disk`. Only ever holds what
#: was FOUND or WRITTEN — never a miss, the same rule every cache in
#: `tests/test_repeat_work.py` follows, because art appears at runtime in
#: this app and a remembered absence would outlive it.
_COMPOSED: dict[tuple, object] = {}


def clear_cache() -> None:
    """Forget the composed masters — for tests that write plates into a
    temporary tree (the twin of `config.paths.reset_art_file_cache`)."""
    _COMPOSED.clear()


def _ink_advance(left: QImage, right: QImage, gap_px: float) -> int:
    """How far the RIGHT plate's box must start from the LEFT plate's
    box so the two glyphs' INK clears by `gap_px` at its closest point.

    THE INK GAP, not the box gap (independent grader 2026-08-07, R3 =
    7/10: "the 15 seat shows its 1 and 5 plates touching at the joint").
    The plates are tightly cropped, so spacing their BOXES spaces
    nothing: a 2 and a 0 never reach toward each other and end up 37 px
    apart, while a 1's flag serif and a 5's top bar reach into the same
    rows and end up at 23 — a "12" at 8. Same rule, six different
    spacings, which is exactly what the eye caught.

    Measured per ROW — rightmost ink of the left glyph against leftmost
    ink of the right — with the closest pair deciding the whole advance;
    rows where only one of them has ink cannot collide and are skipped.
    At `dial.LETTER_COMPOSE_INK_GAP_FRACTION` this reproduces the
    owner's own retired `20.png` at exactly 730 px (pinned by
    `tests/test_letter_plates.py`), so his spacing is the one every pair
    now wears."""
    left_edge = _row_extents(left, rightmost=True)
    right_edge = _row_extents(right, rightmost=False)
    shared = [
        (l_x, r_x) for l_x, r_x in zip(left_edge, right_edge)
        if l_x is not None and r_x is not None
    ]
    if not shared:
        # Nothing overlaps vertically: the boxes may sit at the plain gap.
        return left.width() + round(gap_px)
    return max(l_x + 1 + round(gap_px) - r_x for l_x, r_x in shared)


def _row_extents(image: QImage, rightmost: bool) -> list[int | None]:
    """Per ROW, the x of the outermost opaque pixel on one side — the
    glyph's real silhouette, `None` for a row it does not touch."""
    if image.format() != QImage.Format.Format_ARGB32:
        image = image.convertToFormat(QImage.Format.Format_ARGB32)
    buffer = np.frombuffer(
        memoryview(image.constBits()), dtype=np.uint8,
    ).reshape(image.height(), image.bytesPerLine() // 4, 4)
    alpha = buffer[:, :image.width(), 3] > 0
    has_ink = alpha.any(axis=1)
    edge = (
        image.width() - 1 - alpha[:, ::-1].argmax(axis=1) if rightmost
        else alpha.argmax(axis=1)
    )
    return [int(x) if ink else None for x, ink in zip(edge, has_ink)]


def _composed_master(parts: tuple[Path, ...]) -> Path:
    """Two (or more) digit plates side by side, written ONCE into the
    raster cache as a gold master.

    The digit masters are all 512 px tall and tightly cropped, so they
    already share a cap height — the composition is pure placement, no
    scaling and no baseline maths. The spacing is `_ink_advance` at
    `dial.LETTER_COMPOSE_INK_GAP_FRACTION`, solved so that the owner's
    own retired `20.png` comes back at exactly 730 px — his kerning,
    applied evenly to every pair.

    Cache key: every source's own content fingerprint, so re-drawing a
    digit master rebuilds the numbers that use it and
    `raster_store.collect_garbage` can retire the old one."""
    memo = _COMPOSED.get(parts)
    if memo is not None:
        return memo
    sources = []
    for part in parts:
        resolved = paths.existing_art_file(part)
        if resolved is None:
            raise MissingPlate(f"letter plate missing on disk: {part}")
        sources.append(resolved)
    stamp = "_".join(raster_store.source_prefix(source) for source in sources)
    cache = (
        paths.settings_path().parent / "raster_cache"
        / f"{stamp}_compose_v{dial.LETTER_COMPOSE_VERSION}.png"
    )
    if cache.exists():
        _COMPOSED[parts] = cache
        return cache
    images = [QImage(str(source)) for source in sources]
    if any(image.isNull() for image in images):
        raise MissingPlate(f"letter plate unreadable: {sources}")
    height = max(image.height() for image in images)
    gap = height * dial.LETTER_COMPOSE_INK_GAP_FRACTION
    # Place each plate so its INK clears the previous plate's ink by the
    # gap — never so its BOX clears the previous box (`_ink_advance`).
    offsets, x = [0], 0
    for left, right in zip(images, images[1:]):
        x += _ink_advance(left, right, gap)
        offsets.append(x)
    width = offsets[-1] + images[-1].width()
    canvas = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    try:
        for image, x in zip(images, offsets):
            # BOTTOM aligned: the digits share a baseline, and a plate
            # shorter than the tallest one hangs from it, never floats.
            painter.drawImage(x, height - image.height(), image)
    finally:
        painter.end()
    try:
        raster_store.atomic_save(canvas, cache)
    except OSError:
        # A cache that cannot be written is only slower, never wrong —
        # but a composed number has no master to fall back TO, so the
        # caller must hear about it rather than draw a blank seat.
        raise MissingPlate(f"could not write composed plate {cache}")
    _COMPOSED[parts] = cache
    return cache
