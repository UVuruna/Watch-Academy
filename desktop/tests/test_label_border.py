"""THE ON-DIAL LABEL BORDER — the owner's correction, pinned.

Owner order 2026-08-12: the weekday names and the Earth's date label come
from the plate library, and they carry an edge that works on any ground —
his case being the LOOP theme's blue date over the blue Earth.

The FIRST CUT of that reused the ring's soft halo, widened to be
"dense", and he rejected it in the same session for two reasons that are
now two tests each:

  1. it VANISHED on the dim bodies (SATURDAY / TUESDAY / MONDAY /
     WEDNESDAY) — a dark cushion around dark ink on a dark ground
     separates nothing;
  2. it grew with the letter height until it "covered the whole
     ROUNDEL or whatever it is written over".

His replacement, quoted: a BORDER — short radius, a couple of px,
intensity 100%, white AND black so it works everywhere.
lang-ok: the owner's own correction is the specification these tests
enforce, and it is quoted in `render/glyph_shadow.py`.

So these tests do not check that a border "looks nice" — they check the
four properties that made the first cut fail, so it cannot come back.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QApplication

from config import dial, palette
from config.registry import week as week_registry
from render import glyph_shadow, letter_plates, painting


@pytest.fixture(autouse=True)
def app():
    instance = QApplication.instance() or QApplication([])
    glyph_shadow.clear_cache()
    yield instance
    glyph_shadow.clear_cache()


def _opaque_colors(image: QImage) -> list[QColor]:
    return [
        image.pixelColor(x, y)
        for y in range(image.height())
        for x in range(image.width())
        if image.pixelColor(x, y).alpha() > 200
    ]


def _has_near(colors, target: str, tolerance: int = 26) -> bool:
    want = QColor(target)
    return any(
        abs(c.red() - want.red()) <= tolerance
        and abs(c.green() - want.green()) <= tolerance
        and abs(c.blue() - want.blue()) <= tolerance
        for c in colors
    )


def test_a_label_carries_BOTH_contour_colours():
    """PROPERTY 1 — the reason the first cut failed. One colour cannot be
    ground-independent: a dark edge dies on a dark body, a light edge on
    a light one. Both must be present in the composed label."""
    label = glyph_shadow.bordered_plate_text("MONDAY", 34, "thematic", 1.0)
    colors = _opaque_colors(label.toImage())
    assert _has_near(colors, palette.SHADOW_STAMP_TINT), (
        "no DARK contour — the label will vanish on a pale body"
    )
    assert _has_near(colors, palette.SHADOW_STAMP_TINT_LIGHT), (
        "no LIGHT contour — the label will vanish on a dark body, which "
        "is exactly what the owner rejected on SATURDAY/TUESDAY/MONDAY/"
        "WEDNESDAY"
    )


def test_the_border_does_not_grow_with_the_letter_height():
    """PROPERTY 2 — "necu veliki halo koji prekriva ceo ROUNDEL". The
    border is DEVICE PIXELS. Quadruple the ink and the padding around it
    must stay put; a fraction-of-height edge is what swallowed the
    roundel."""
    small = glyph_shadow.bordered_plate_text("MONDAY", 20, "thematic", 1.0)
    glyph_shadow.clear_cache()
    large = glyph_shadow.bordered_plate_text("MONDAY", 80, "thematic", 1.0)
    ink_small = letter_plates.plate_text_pixmap(
        "MONDAY",
        max(1, round(20 * glyph_shadow.PLATE_INK_HEIGHT_FRACTION)),
        "thematic", 1.0,
    )
    ink_large = letter_plates.plate_text_pixmap(
        "MONDAY",
        max(1, round(80 * glyph_shadow.PLATE_INK_HEIGHT_FRACTION)),
        "thematic", 1.0,
    )
    pad_small = small.height() - ink_small.height()
    pad_large = large.height() - ink_large.height()
    assert pad_small == pad_large, (
        f"the border grew with the text: {pad_small}px of padding at "
        f"20px ink, {pad_large}px at 80px — it must be device pixels, "
        "not a fraction of the letter height"
    )
    ceiling = 2 * (dial.LABEL_BORDER_LIGHT_PX + 2) + 1
    assert pad_large <= ceiling, (
        f"{pad_large}px of border around the ink is not 'kretak radijus "
        f"par px' (ceiling {ceiling}px)"
    )


def test_the_border_is_opaque_not_a_faded_glow():
    """PROPERTY 3 — "intenzitet 100%". `solid_contour` must draw at full
    alpha; `stamp_shadow`'s renormalized alpha is the SOFT halo the ring
    wears and is what made the first cut read as a scattered glow."""
    ink = letter_plates.plate_text_pixmap("M", 40, "thematic", 1.0).toImage()
    contour = glyph_shadow.solid_contour(ink, 3.0, palette.SHADOW_STAMP_TINT)
    solid = [
        c for c in _opaque_colors(contour)
        if c.red() < 40 and c.green() < 40 and c.blue() < 40
    ]
    assert solid, "the contour has no fully opaque pixels at all"
    # ...and the SOFT twin must still be soft, so the ring's own look is
    # untouched by this round.
    assert glyph_shadow.normalized_shadow_alpha(
        dial.RING_JEWEL_SHADOW_SAMPLES
    ) == pytest.approx(dial.RING_JEWEL_SHADOW_ALPHA), (
        "the ring's soft halo changed — this round must not touch it"
    )


def test_the_label_reads_on_a_black_ground_and_on_a_white_one():
    """PROPERTY 4, the whole point: ONE label, both extremes. Composited
    over near-black and over near-white, each result must differ from its
    own background where the label sits — which is what "radice svuda"
    means, measured."""
    for ground in ("#050508", "#F2F2F2"):
        canvas = QImage(360, 90, QImage.Format.Format_ARGB32_Premultiplied)
        canvas.fill(QColor(ground))
        painter = QPainter(canvas)
        glyph_shadow.draw_bordered_plate_text(
            painter, QPointF(180, 45), "MONDAY", 34, "thematic", 1.0,
        )
        painter.end()
        base = QColor(ground)
        differing = sum(
            1
            for y in range(canvas.height())
            for x in range(canvas.width())
            if abs(canvas.pixelColor(x, y).red() - base.red()) > 60
        )
        assert differing > 400, (
            f"on {ground} the label barely separates from its ground "
            f"({differing} strongly-differing pixels) — this is the "
            "measurement the first cut failed"
        )


def test_a_plateless_glyph_falls_back_instead_of_killing_the_paint():
    """THE ONE PLATE LAW's raise governs the library DOOR, not a paint
    layer. An exception escaping `paintEvent` with a live QPainter is the
    2026-07-31 crash class, so the label door must catch it, draw with
    the font, and NAME the character.

    "The Lord's Day" is the real case — the one string in the whole
    program the library cannot compose (no apostrophe plate)."""
    with pytest.raises(letter_plates.MissingPlate):
        letter_plates.plate_text_pixmap("The Lord's Day", 30, "gold", 1.0)

    canvas = QImage(400, 90, QImage.Format.Format_ARGB32_Premultiplied)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    painting.draw_name_label(          # must NOT raise
        painter, "The Lord's Day", QPointF(200, 45), 28,
    )
    painter.end()
    assert _opaque_colors(canvas), "the fallback drew nothing at all"


def test_every_weekday_label_and_figure_stem_composes_from_plates():
    """The fallback above is for ONE known string. Everything else on the
    dial must take the plate road — a second name quietly falling back
    would be the font creeping back in, which is what THE ONE PLATE LAW
    exists to stop."""
    import re
    from pathlib import Path

    from config import constants, paths

    labels = set(week_registry.WEEKDAY_LABELS.values())
    labels |= set(week_registry.WEEKDAY_FULL_NAMES.values())
    for source in paths.art_files_under(paths.assets_dir()):
        if "_baked" in source.parts or "_state" in source.parts:
            continue
        stem = re.sub(r"_v\d+$", "", re.sub(r"_(gem|gpt)$", "", source.stem))
        labels.add(stem.replace("_", " "))

    plateless = sorted(
        name for name in labels
        if any(
            ch != " " and not letter_plates.has_plate(ch)
            for ch in name.upper()
        )
    )
    assert plateless == [], (
        f"{len(plateless)} dial label(s) cannot be plate-composed and "
        f"would fall back to the font: {plateless[:8]}"
    )


def test_a_label_composed_from_gold_standins_is_not_served_after_the_metal_lands(
    tmp_path, monkeypatch,
):
    """THE 2026-08-02 CLASS OF DEFECT, caught by this round's own
    render-equality proof rather than by a user.

    `jewel_metal_file` returns the GOLD MASTER when a finish is not on
    disk yet — its documented, visible stand-in. The label cache was
    first keyed only by (text, size, metal, dpr), so on a cold cache it
    froze whatever the first paint saw: the labels were composed from
    gold masters and STAYED gold, because the background drain landing
    the real metal changes no part of that key. Measured as 1,549
    differing pixels between a baked dial and a live-recolored one at
    1200px; zero after the fix.

    The fix is structural — the resolved FILES are in the key, so a
    stale composition cannot be found, let alone served. This test
    proves the key moves when the file does."""
    from render import asset_recolor, letter_bake
    from config import paths

    monkeypatch.setattr(
        paths, "settings_path", lambda index=1: tmp_path / "settings.json"
    )
    monkeypatch.setattr(asset_recolor.paths, "settings_path", paths.settings_path)
    monkeypatch.setattr(asset_recolor, "_PENDING_VARIANTS", {})
    empty = tmp_path / "no_bake"
    empty.mkdir()
    monkeypatch.setattr(letter_bake, "bake_dir", lambda: empty)
    letter_bake.refresh()
    glyph_shadow.clear_cache()

    # COLD: every finish is missing, so the label composes from masters.
    cold = glyph_shadow.bordered_plate_text("MONDAY", 34, "silver", 1.0)
    assert asset_recolor.pending_art(), (
        "nothing was deferred — this test needs a genuinely cold cache "
        "to have anything to prove"
    )

    # The drain lands the real metal, exactly as the warm thread does.
    from render.art_warm import warm_pending_art
    assert warm_pending_art() > 0

    warm = glyph_shadow.bordered_plate_text("MONDAY", 34, "silver", 1.0)
    assert warm is not cold, (
        "the cache served the GOLD-MASTER composition after the real "
        "silver had landed — the dial would stay gold until restart, "
        "which is the defect the stale notifier was created for"
    )
