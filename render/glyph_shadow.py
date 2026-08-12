"""THE LETTER SHADOW LAW's own home — the stamped halo every RING glyph
wears, and the two-colour BORDER the dial's own labels wear. See
[Glyph Shadow](__about/glyph_shadow.md).

The stamp math moved out of `render.layers.ring` into
`render.numeral_bands` on 2026-08-06 so the live crown's tiles could
wear the same halo the ring's jewels wear. It moves again now, for the
same reason and a THIRD caller: the on-dial NAME LABELS need it, and
they are drawn by `render.painting`, which `numeral_bands` already
imports — so `numeral_bands` could never be their shared home without a
cycle. `numeral_bands` re-exports these names, so `render.layers.ring`
keeps importing them from where it always did.

Owner order 2026-08-12: the weekday names and the Earth's date label
come from the plate library like everything else, and they carry their
own edge treatment, because
lang-ok: the owner's own instruction, quoted so it cannot be re-derived
wrongly:
"za situacije gde je boja pozadine kao boja slova npr LOOP tematika
plava na plavom EARTH koji prikazuje datum"

A real failure, not a preference: white-with-a-black-outline is legible
only while the art underneath is neither white nor black, and LOOP's
thematic shade is a dark blue that lands on a blue Earth.

THE FIRST CUT WAS WRONG AND HE CORRECTED IT, which is recorded here
because the correction IS the design. It reused the ring's soft halo,
scaled up to be "dense" — and that failed exactly where it mattered:
SATURDAY, TUESDAY, MONDAY and WEDNESDAY over the dim bodies, where a
dark cushion around dark ink on a dark ground separates nothing, while
the widened radius began to swallow the roundel it sat on. His words:
lang-ok: the owner's own correction, quoted.
"necu veliki halo koji prekriva ceo ROUNDEL ili bilo sta oko cega pise
NEGO VISE KAO BORDER kretak radijus par px i intenzitet 100%"
...and, from the same message, "shadow beli i crni i radice svuda".

So a label wears TWO solid contours at FULL opacity, each a couple of
DEVICE pixels wide: a dark keyline hugging the ink and a light one
immediately outside it. Two colours is what makes it ground-independent
WITHOUT knowing the ground — on a pale body the dark line reads, on a
near-black one the light line does, on a mid tone both do. `stamp_shadow`
(soft, renormalized, for the ring) and `solid_contour` (hard, full alpha,
for the labels) are both here, and the difference between them is the
whole of that correction.
"""

from __future__ import annotations

import math
import threading

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter

from config import dial, palette
from render import numeral_relief as relief

# A plate is its GLYPH with no ascender/descender slack; `QFont.
# setPixelSize` is an em box that has both. Sizing a plate label by the
# caller's font-shaped number would therefore draw a visibly LARGER
# label than the font did, and the SET-UNIFORM sizing law (owner verdict
# 2026-07-18 — every name sharing a ring wears the size of the smallest
# fitted member) would stop meaning what it meant. This maps one onto
# the other: the cap-height share of a typical bold em box.
PLATE_INK_HEIGHT_FRACTION = 0.72

#: Composed labels, keyed by (text, ink height, metal, dpr). These
#: repaint with the dial and composing one walks a plate per character
#: through `jewel_metal_file`, so the walk happens once per distinct
#: label per process.
_LABELS: dict[tuple, object] = {}
_LABELS_LOCK = threading.Lock()


def clear_cache() -> None:
    """Drop the composed labels — a metal/shade switch, an art wave, or
    a test. `render.letter_plates.clear_cache`'s twin for this layer."""
    with _LABELS_LOCK:
        _LABELS.clear()


# ------------------------------------------------------- THE SHADOW STAMP
# Moved verbatim from `render.numeral_bands` (which now re-exports them).


def shadow_sample_count(pixel_radius: float) -> int:
    """Sample count for the shadow stamp ring at `pixel_radius` (DEVICE
    pixels). Below `RING_JEWEL_SHADOW_SAMPLES` (today's look at
    ordinary dial sizes) the stamps overlap and fuse into a smooth halo;
    at large pixel radii that fixed count spreads the same 8 copies far
    enough apart that the gaps between them show as a scalloped, jagged
    edge (THE PIXELATION FIX, 1440p owner bug, 2026-08-06). This grows
    the count so adjacent stamps stay under `RING_JEWEL_SHADOW_MAX_GAP_PX`
    apart along the stamp circle's own circumference — the floor never
    shrinks below the original 8."""
    if pixel_radius <= 0:
        return dial.RING_JEWEL_SHADOW_SAMPLES
    needed = math.ceil(
        2.0 * math.pi * pixel_radius / dial.RING_JEWEL_SHADOW_MAX_GAP_PX
    )
    return max(dial.RING_JEWEL_SHADOW_SAMPLES, needed)


def normalized_shadow_alpha(samples: int) -> float:
    """Per-stamp opacity for `samples` copies so the COMPOSITED darkness
    stays what `RING_JEWEL_SHADOW_SAMPLES` stamps at
    `RING_JEWEL_SHADOW_ALPHA` each look like, whatever `samples` grows
    to (`shadow_sample_count`) — extra stamps close the pixel gaps that
    scallop the edge at large dial sizes, they never darken it. Solves
    the standard "N over-composited equal-alpha layers reach target
    coverage" equation, `target = 1 - (1-a)**n`, backwards for a
    per-stamp `a` at the ACTUAL sample count; at the floor count this is
    `RING_JEWEL_SHADOW_ALPHA` exactly (identity, checked by
    `tests/test_ring_split.py`)."""
    target = (
        1.0
        - (1.0 - dial.RING_JEWEL_SHADOW_ALPHA) ** dial.RING_JEWEL_SHADOW_SAMPLES
    )
    if samples <= 0:
        return 0.0
    return 1.0 - (1.0 - target) ** (1.0 / samples)


def stamp_shadow(painter: QPainter, radius_px: float, draw_copy) -> None:
    """The shared shadow-stamp LOOP: `draw_copy(dx, dy)` paints one
    silhouette copy shifted by `(dx, dy)` from the glyph's own centred
    position; this function only decides HOW MANY copies and at what
    per-stamp opacity, then walks them around the circle of radius
    `radius_px`. Shared by the ring's live jewel stamp, the crown's
    baked plate stamp and the dial's own labels — when the stamp runs
    differs, the stamp law does not (Rule #5)."""
    samples = shadow_sample_count(radius_px)
    painter.save()
    painter.setOpacity(normalized_shadow_alpha(samples))
    for k in range(samples):
        angle = 2.0 * math.pi * k / samples
        draw_copy(radius_px * math.cos(angle), radius_px * math.sin(angle))
    painter.restore()


def image_silhouette(image: QImage, color: str) -> QImage:
    """`image`'s own alpha, filled flat with `color` — the shadow
    stamp's silhouette for a RASTER glyph. The live ring paint path gets
    this for free (`ctx.cache.pixmap_by_height(..., tint=
    SHADOW_STAMP_TINT)`); the crown tiles and these labels are composed
    outside the AssetCache, so the same silhouette is built here."""
    silhouette = QImage(image.size(), QImage.Format.Format_ARGB32_Premultiplied)
    silhouette.fill(QColor(color))
    painter = QPainter(silhouette)
    painter.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_DestinationIn
    )
    painter.drawImage(0, 0, image)
    painter.end()
    return silhouette


# ------------------------------------------------------- THE PLATE LABEL


def solid_contour(glyphs: QImage, radius_px: float, color: str) -> QImage:
    """`glyphs`' silhouette DILATED by `radius_px`, filled solid with
    `color` — a BORDER, not a halo. Returns a canvas padded by
    `ceil(radius_px) + 1` on every side.

    The difference from `stamp_shadow` IS the owner's 2026-08-12
    correction. That function spreads its copies at a RENORMALIZED
    per-stamp alpha so the union reads as a soft cushion; this one draws
    every copy at FULL opacity, so the union is a hard, even outline of
    exactly `radius_px` — his words: a border, short radius, a couple of
    px, intensity 100%, and explicitly NOT a scattered glow covering the
    whole roundel.

    The sample count still comes from `shadow_sample_count`, for the
    reason that function was written (THE PIXELATION FIX): too few
    copies at a large pixel radius leave scalloped gaps between them,
    and a scalloped border is worse than no border."""
    silhouette = image_silhouette(glyphs, color)
    pad = int(math.ceil(radius_px)) + 1
    canvas = relief.blank_plate(
        glyphs.width() + 2 * pad, glyphs.height() + 2 * pad
    )
    painter = QPainter(canvas)
    samples = shadow_sample_count(radius_px)
    for k in range(samples):
        angle = 2.0 * math.pi * k / samples
        painter.drawImage(
            QPointF(
                pad + radius_px * math.cos(angle),
                pad + radius_px * math.sin(angle),
            ),
            silhouette,
        )
    painter.end()
    return canvas


def bordered_plate_text(
    text: str, height_px: float, metal: str = "gold", dpr: float = 1.0,
):
    """Plate-composed `text` wearing the TWO-COLOUR BORDER, as a
    `QPixmap` whose INK height is `height_px` (not its box height — see
    `PLATE_INK_HEIGHT_FRACTION`; the caller passes the font-shaped
    number its own sizing law computed).

    Owner correction 2026-08-12: a dark keyline hugging the ink and a
    light one immediately outside it, both a couple of DEVICE pixels wide
    and both at FULL opacity — a border, not a scattered glow, and never
    something that covers the roundel it sits on. Two colours because
    that is what makes it ground-independent without knowing the ground:
    on a pale body the dark line reads, on a near-black one the light
    line does, on a mid tone both do. One colour cannot, which is why
    the first cut vanished on SATURDAY / TUESDAY / MONDAY / WEDNESDAY.

    Padded by the border width on every side, so a caller centring the
    returned pixmap centres the GLYPHS and not the padding.

    Raises `render.letter_plates.MissingPlate` straight through. The
    decision to fall back to a font belongs to the paint layer, which
    must not die (`render.painting.draw_name_label`), never to this
    function — THE ONE PLATE LAW's raise is the library's contract and
    is not softened here."""
    from PySide6.QtGui import QPixmap

    from render import letter_plates

    ink_px = max(1, round(height_px * PLATE_INK_HEIGHT_FRACTION * dpr))
    key = (text, ink_px, metal, round(dpr, 3))
    with _LABELS_LOCK:
        cached = _LABELS.get(key)
    if cached is not None:
        return cached

    # Composed at DEVICE resolution with a neutral dpr — the finished
    # pixmap carries the real dpr once, at the end (the same shape
    # `letter_plates.plate_text_segments_pixmap` uses).
    glyphs = letter_plates.plate_text_pixmap(text, ink_px, metal, 1.0).toImage()
    # DEVICE pixels, scaled only by dpr: a border is a border at every
    # dial size. A fraction of the letter height is exactly how the first
    # cut grew into something that swallowed the roundel.
    dark_px = max(1.0, dial.LABEL_BORDER_DARK_PX * dpr)
    light_px = max(dark_px + 1.0, dial.LABEL_BORDER_LIGHT_PX * dpr)
    light = solid_contour(glyphs, light_px, palette.SHADOW_STAMP_TINT_LIGHT)
    dark = solid_contour(glyphs, dark_px, palette.SHADOW_STAMP_TINT)

    tile = relief.blank_plate(light.width(), light.height())
    painter = QPainter(tile)
    # Widest first, then inwards, then the ink: the light band ends up as
    # the visible ring OUTSIDE the dark keyline.
    painter.drawImage(0, 0, light)
    inset_dark = (light.width() - dark.width()) / 2.0
    painter.drawImage(QPointF(inset_dark, inset_dark), dark)
    inset_ink = (light.width() - glyphs.width()) / 2.0
    inset_ink_y = (light.height() - glyphs.height()) / 2.0
    painter.drawImage(QPointF(inset_ink, inset_ink_y), glyphs)
    painter.end()
    pixmap = QPixmap.fromImage(relief.stamp_dpr(tile, dpr))
    with _LABELS_LOCK:
        _LABELS[key] = pixmap
    return pixmap


def draw_bordered_plate_text(
    painter: QPainter, center: QPointF, text: str, height_px: float,
    metal: str = "gold", dpr: float = 1.0,
) -> None:
    """`bordered_plate_text` drawn CENTRED on `center` — the shape every
    caller actually wants, so none of them has to know that the pixmap
    carries border padding."""
    pixmap = bordered_plate_text(text, height_px, metal, dpr)
    width = pixmap.width() / pixmap.devicePixelRatio()
    height = pixmap.height() / pixmap.devicePixelRatio()
    painter.drawPixmap(
        QPointF(center.x() - width / 2.0, center.y() - height / 2.0), pixmap,
    )
