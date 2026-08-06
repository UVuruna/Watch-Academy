"""THE VISUAL DEFECTS WAVE (owner defects 2026-08-07) — one tooth per
ruling, all five seen on the owner's own screenshots of The One and
Templar.

1. ONE CROWN SIZE LAW — the live time crown took the HOUR BAND's size
   law while NON NOBIS DOMINE beside it took `RING_CROWN_TEXT_SIZE`;
   two size families on one ring, and the live one landed smaller
   still once the font's ink/em ratio was applied. Plus THE CROWN
   ADVANCE LAW: a fixed angular step gave a 0.22-wide colon the room
   of a 1.45-wide M, which read as "scattered".
2. ONE METAL PER CROWN — the colon plate rendered GOLD beside gray
   digits, because the crown BAKES its tiles once and cached the
   background recolor's honest gold fallback forever.
3. THE RULED LOCATION ARC — The One's ruled bottom "City, Country"
   line was served only by a user toggle that is OFF by default and
   draws at the TOP.
4. ONE SEATING LAW — the jewels went through
   `core.angles.readable_rotation_deg` and the numerals through
   `core.numerals.seat_rotation`: two forks of one law, disagreeing on
   exactly the four square angles, so The One's 18 and 6 lay sideways
   beside upright numerals. (Its own teeth live in
   `tests/test_angles.py`, beside the door that was forked.)
5. THE DECOUPLED SCALES — crown height multiplied `ring_jewels_scale`
   AND `crown_text_scale`, so the Jewels slider grew the crown.

PLUS THE REPRESENTATIVE PRESETS LAW — the six bundled presets ship
crown and jewels in ONE metal family.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from app.controller import _location_crown_text, build_skin
from app.settings_store import Settings, replace
from config import constants, dial
from core import numerals
from data.rings import ring_presets
from render import numeral_bands
from render.asset_recolor import (
    ensure_variant, jewel_metal_file, jewel_metal_path,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _crown_spec(app, **overrides):
    """The spec an ON-SCREEN watch of this skin would build — through
    `render.layers.numerals.crown_spec`, never hand-assembled, so a
    change to the size law is caught here rather than mirrored."""
    from render.context import RenderContext
    from render.layers.numerals import crown_spec

    skin = build_skin(replace(Settings(), ring=overrides.pop("ring", "The One")))
    if overrides:
        skin = replace(skin, **overrides)
    ctx = RenderContext(
        radius=360.0, dpr=1.0, skin=skin, cache=None, tick=None, day=None,
    )
    return crown_spec(skin, ctx), skin, ctx


# ------------------------------------------------------ 1. ONE CROWN SIZE LAW

def test_live_crown_box_equals_the_static_crown_text_box(app):
    """The live crown's glyph BOX is bit-identical to the box
    `RingLayer._draw_crown_text` gives a NON NOBIS DOMINE letter at the
    same radius — the whole of the owner's "microscopic" complaint. It
    used to be `numeral_outer_size * NUMERAL_UNIT_FRACTION *
    CROWN_NUMERAL_SIZE_FRACTION`, a law borrowed from the hour band."""
    spec, skin, ctx = _crown_spec(app, ring="Templar")
    static_height = (
        2 * ctx.radius * dial.RING_CROWN_TEXT_SIZE * skin.crown_text_scale
    )
    assert spec.height_px == pytest.approx(static_height * ctx.dpr)
    # And the retired constant really is gone — a leftover would let the
    # two laws drift apart again (Rule #6).
    assert not hasattr(dial, "CROWN_NUMERAL_SIZE_FRACTION")


def test_live_crown_shares_the_static_crown_radius(app):
    """Same radius family, so "23:39" and NON NOBIS DOMINE ride one
    circle rather than two."""
    assert dial.CROWN_RADIUS_FRACTION == dial.RING_CROWN_TEXT_RADIUS_FRACTION


def test_digit_ink_matches_the_jewel_plate_ink(app):
    """A digit's drawn INK fills the same fraction of the box a jewel
    plate's ink fills — the per-face fitting step. `setPixelSize` sets
    the EM box, not the ink, so sizing by pixel size alone drew ~28%
    less ink than the plates beside it on the default face."""
    box_px = 200.0
    font = numeral_bands.crown_font_for_ink_height(
        dial.CROWN_FACE_DEFAULT, box_px * dial.CROWN_PLATE_INK_FRACTION,
    )
    from render import numeral_relief as relief

    heights = [
        relief.glyph_path(digit, font).boundingRect().height()
        for digit in "0123456789"
    ]
    target = box_px * dial.CROWN_PLATE_INK_FRACTION
    # Within 2% of the target. The fit is solved from the face's own
    # ratio, probed at CROWN_FIT_PROBE_PX; the residual is the outline's
    # own grid fitting, which makes the ratio very slightly size
    # dependent. What matters is the ORDER OF MAGNITUDE this replaced:
    # the unfitted law drew 0.717 of the box (a 28% shortfall) on the
    # default face, and a different shortfall on every other face.
    assert max(heights) == pytest.approx(target, rel=0.02)
    # THE DEFECT, stated as the property rather than as one face's
    # number: the UNFITTED law drew `ratio * box` where `ratio` is the
    # face's own ink/em, and that ratio is a per-face constant nothing
    # corrected for — 0.717 on Bahnschrift Bold, 0.685 on Palatino
    # Linotype Bold, 0.80 on Bernard MT Condensed, MEASURED on this
    # machine. (Under the offscreen platform used in CI no real face
    # resolves and every ratio is ~1.0, which is why this asserts the
    # CORRECTION holds rather than asserting one shortfall number.)
    unfitted = numeral_bands.numeral_font(
        "outer", dial.CROWN_FACE_DEFAULT, box_px,
    )
    unfitted_ink = relief.glyph_path("8", unfitted).boundingRect().height()
    assert unfitted_ink <= target * 1.02
    for face in dial.NUMERAL_OUTER_FACES:
        fitted = numeral_bands.crown_font_for_ink_height(face, target)
        drawn = max(
            relief.glyph_path(digit, fitted).boundingRect().height()
            for digit in "0123456789"
        )
        assert drawn == pytest.approx(target, rel=0.03), face


def test_crown_advance_follows_glyph_width_not_a_fixed_step(app):
    """THE CROWN ADVANCE LAW: the colon — far narrower than a digit —
    takes visibly less arc than a digit does. Under the fixed step it
    took exactly as much, which is what opened the gaps in "2 3 : 3 9"."""
    spec, _skin, _ctx = _crown_spec(app, ring="The One")
    numeral_bands.clear_cache()
    try:
        ink = numeral_bands.crown_glyph_ink(spec)
        assert ink[":"] < ink["5"] * 0.75
        tracking = spec.height_px * dial.CROWN_TRACKING_FRACTION
        advances = tuple(
            numerals.arc_degrees(ink[glyph] + tracking, 1000.0)
            for glyph in "23:39"
        )
        seats = numerals.crown_advance_angles(advances, "top")
        gaps = [b - a for a, b in zip(seats, seats[1:])]
        # Every step is positive (the run reads left to right over the
        # top) and the two steps FLANKING the colon are the smallest —
        # it is the narrowest glyph, so it claims the least arc. Under
        # the fixed step all four gaps were identical.
        assert all(gap > 0 for gap in gaps)
        assert sorted(gaps)[:2] == pytest.approx(sorted([gaps[1], gaps[2]]))
        assert max(gaps) > min(gaps) * 1.1
        # And the run really is drawn through this law by the layer.
        composed = numeral_bands.compose_crown(
            numeral_bands.crown_glyph_set(spec), tuple("23:39"), "top",
            ink=ink, radius_px=1000.0, tracking_px=tracking,
        )
        assert [seat for _img, seat, _rot in composed] == pytest.approx(
            [seat % 360.0 for seat in seats]
        )
    finally:
        numeral_bands.clear_cache()


def test_equal_advances_reproduce_the_fixed_step_layout(app):
    """The new law is a strict generalization: feed it equal advances
    and it lays out exactly what `crown_arc_angles` always did."""
    for orientation in ("top", "bottom"):
        step = dial.RING_CROWN_TEXT_LETTER_STEP_DEG
        assert numerals.crown_advance_angles(
            (step,) * 5, orientation,
        ) == pytest.approx(numerals.crown_arc_angles(5, orientation))


# -------------------------------------------------- 2. ONE METAL PER CROWN

def test_crown_cache_key_carries_the_resolved_colon_source(app):
    """THE ROOT CAUSE, pinned. `jewel_metal_file` honestly falls back to
    the GOLD master until the background recolor lands. The crown bakes
    its tiles ONCE, so without the resolved path in the key that
    fallback was frozen in place — gold colon, silver digits — until the
    process restarted."""
    import dataclasses

    spec, _skin, _ctx = _crown_spec(app, ring="Templar")
    assert spec.colon_source
    # It is the file `jewel_metal_file` would hand the ring layer for
    # this metal — not the gold master by name, because a derived
    # variant is content-fingerprinted (`raster_store.source_prefix`).
    assert spec.colon_source == str(
        jewel_metal_file(dial.RING_JEWEL_ART_DIR / "time.png", spec.metal)
    )
    # Two different resolutions are two different cache keys, which is
    # the whole fix: when the background drain replaces the gold
    # fallback with the real metal, the crown rebuilds instead of
    # serving its frozen tiles forever.
    assert dataclasses.replace(spec, colon_source="other.png") != spec
    assert hash(dataclasses.replace(spec, colon_source="other.png")) != hash(spec)


@pytest.mark.parametrize("metal", ["silver", "bronze"])
def test_colon_and_digits_wear_ONE_metal(app, metal):
    """The pixel proof the owner asked for: the colon plate's body hue
    and the digits' body hue are the same metal. The derived variant is
    materialized first (`ensure_variant`) — the real dial reaches this
    state as soon as the background drain lands, and the cache key
    change above is what lets it."""
    shade = constants.METAL_SHADE_DEFAULT[metal]
    derived = jewel_metal_path(dial.RING_JEWEL_ART_DIR / "time.png", metal)
    resolved = ensure_variant(derived)
    if resolved is None or not resolved.exists():
        pytest.skip(f"the {metal} colon variant could not be materialized here")
    spec = numeral_bands.CrownSpec(
        pixels=720, dpr=1.0, face=dial.CROWN_FACE_DEFAULT,
        height_px=720 * dial.RING_CROWN_TEXT_SIZE,
        metal=metal, shade=shade, colon_source=str(resolved),
    )
    numeral_bands.clear_cache()
    try:
        glyphs = numeral_bands.crown_glyph_set(spec)
        colon_hue = _dominant_hue(glyphs[":"])
        digit_hue = _dominant_hue(glyphs["5"])
        body = numeral_bands._crown_metal_body_color(metal, shade)
        # Both bodies read as the SAME metal: their hue-and-saturation
        # signature matches the ramp's own body tone, so neither is the
        # gold master standing in for the other.
        assert _same_metal(colon_hue, digit_hue), (
            f"colon {colon_hue} vs digit {digit_hue} — two metals in one crown"
        )
        assert _same_metal(digit_hue, (body.hue(), body.saturation()))
    finally:
        numeral_bands.clear_cache()


def test_the_one_metal_proof_catches_the_defect_it_was_written_for(app):
    """NEGATIVE CONTROL. A proof that cannot fail proves nothing, so
    this feeds the crown exactly the defect state — SILVER digits with
    the GOLD master standing in for the colon, which is what Templar
    showed the owner — and asserts the proof above rejects it.

    Silver is the case the hue proof can decide, and it is the case the
    owner actually saw. Gold and BRONZE differ by about 7 degrees of
    hue (measured: gold body (201,146,42), bronze (169,112,47)), so a
    bronze crown wearing a gold colon is NOT separable this way; the
    tooth that covers every metal is
    `test_crown_cache_key_carries_the_resolved_colon_source` above,
    which fails whatever metal the fallback happened to be."""
    metal, shade = "silver", constants.METAL_SHADE_DEFAULT["silver"]
    numeral_bands.clear_cache()
    try:
        defective = numeral_bands.CrownSpec(
            pixels=720, dpr=1.0, face=dial.CROWN_FACE_DEFAULT,
            height_px=720 * dial.RING_CROWN_TEXT_SIZE,
            metal=metal, shade=shade,
            # The GOLD master — `jewel_metal_file`'s honest fallback.
            colon_source=str(dial.RING_JEWEL_ART_DIR / "time.png"),
        )
        glyphs = numeral_bands.crown_glyph_set(defective)
        assert not _same_metal(
            _dominant_hue(glyphs[":"]), _dominant_hue(glyphs["5"])
        ), "the one-metal proof passes the very defect it guards"
    finally:
        numeral_bands.clear_cache()


def _dominant_hue(image) -> tuple:
    """The (hue, saturation) of the image's most common OPAQUE body
    color — the shadow stamp is a flat dark tint and never wins, so
    this samples the metal itself."""
    counts = {}
    for y in range(0, image.height()):
        for x in range(0, image.width()):
            color = image.pixelColor(x, y)
            if color.alpha() > 200 and color.value() > 40:
                key = (color.red(), color.green(), color.blue())
                counts[key] = counts.get(key, 0) + 1
    if not counts:
        return (-1, 0)
    red, green, blue = max(counts, key=counts.get)
    body = QColor(red, green, blue)
    return (body.hue(), body.saturation())


def _same_metal(a: tuple, b: tuple) -> bool:
    """Two body tones are the same metal when both are essentially
    achromatic (silver) or their hues are within a narrow window
    (gold/bronze). Gold sits near hue 40 and silver at saturation ~0,
    so this separates exactly the confusion the defect produced."""
    if a[1] < 40 and b[1] < 40:
        return True
    if a[0] < 0 or b[0] < 0:
        return False
    delta = abs(a[0] - b[0]) % 360
    return min(delta, 360 - delta) <= 20 and abs(a[1] - b[1]) <= 90


# ----------------------------------------------- 3. THE RULED LOCATION ARC

def test_the_one_draws_its_bottom_location_arc(app):
    """The ruling: The One's bottom crown arc is "City, Country" of the
    observer. It did not exist — the ledger pointed at a per-ring user
    toggle that is OFF by default and, when ticked, draws at the TOP,
    straight through the live time."""
    assert dial.RING_LIVE_CROWN["The One"]["location"] == "bottom"
    skin = build_skin(
        replace(Settings(), ring="The One"), location_display="Belgrade, Serbia",
    )
    texts = [entry["text"] for entry in skin.ring.crown_text]
    assert texts == ["BELGRADE SERBIA"]
    entry = skin.ring.crown_text[0]
    # Drawn from the JEWEL LETTER PLATES, through the crown-text
    # pipeline — one glyph asset per drawable character.
    assert len(entry["glyphs"]) == len("BELGRADESERBIA")
    for asset, _theta in entry["glyphs"]:
        assert asset.parent == dial.RING_JEWEL_ART_DIR
        assert asset.exists(), asset
    # Bottom orientation, like NON NOBIS DOMINE: every seat is in the
    # lower half of the dial, and the run reads counter-clockwise.
    seats = [theta % 360.0 for _asset, theta in entry["glyphs"]]
    assert all(90.0 < seat < 270.0 for seat in seats), seats
    assert seats == sorted(seats, reverse=True)
    # It carries its own hover, shared with the user toggle (Rule #5).
    assert entry["reading"] == dict(dial.RING_LIVE_CROWN_LOCATION_READING)


def test_the_location_arc_separator_is_a_space_because_no_comma_plate_exists(app):
    """The separator choice, stated as a test: the jewel library has no
    COMMA plate, so the comma is dropped and the gap collapses to one
    space — `_location_crown_text`'s existing behavior, reused rather
    than reinvented."""
    assert "," not in constants.RING_JEWEL_FILES
    assert "," not in constants.RING_CROWN_TEXT_CHARSET
    assert _location_crown_text("Belgrade, Serbia") == "BELGRADE SERBIA"


def test_the_location_arc_re_renders_on_a_location_change(app):
    """Static per LOCATION, not per minute: a different observer
    produces a different arc, and the same observer the same one."""
    def arc(display):
        return [
            entry["text"]
            for entry in build_skin(
                replace(Settings(), ring="The One"), location_display=display,
            ).ring.crown_text
        ]

    assert arc("Belgrade, Serbia") == ["BELGRADE SERBIA"]
    assert arc("Tromsø, Norway") != arc("Belgrade, Serbia")
    assert arc("Belgrade, Serbia") == arc("Belgrade, Serbia")


def test_templar_gains_no_location_arc(app):
    """Templar's bottom arc is NON NOBIS DOMINE — the ruled location arc
    is The One's alone, and must not push a second bottom run onto it."""
    assert dial.RING_LIVE_CROWN["Templar"]["location"] is None
    skin = build_skin(
        replace(Settings(), ring="Templar"), location_display="Belgrade, Serbia",
    )
    assert [entry["text"] for entry in skin.ring.crown_text] == [
        "NON NOBIS DOMINE"
    ]


def test_the_user_toggle_still_wins_when_ticked(app):
    """When the user ticks Location for The One, the toggle's own
    replacement crown is what draws — never that PLUS the ruled arc."""
    settings = replace(
        Settings(), ring="The One", ring_crown_location={"The One": True},
    )
    skin = build_skin(settings, location_display="Belgrade, Serbia")
    assert [entry["text"] for entry in skin.ring.crown_text] == [
        "BELGRADE SERBIA"
    ]


# ------------------------------------------------- 5. THE DECOUPLED SCALES

def test_jewels_slider_no_longer_grows_the_crown(app):
    """The owner's own discovery. Moving Jewels must move jewels only;
    moving Crown Text must move every crown arc, static and live."""
    from render.context import RenderContext
    from render.layers.numerals import crown_spec

    def boxes(jewels_scale, crown_scale):
        skin = replace(
            build_skin(replace(Settings(), ring="Templar")),
            ring_jewels_scale=jewels_scale, crown_text_scale=crown_scale,
        )
        ctx = RenderContext(
            radius=360.0, dpr=1.0, skin=skin, cache=None, tick=None, day=None,
        )
        static = (
            2 * ctx.radius * dial.RING_CROWN_TEXT_SIZE * skin.crown_text_scale
        )
        return static, crown_spec(skin, ctx).height_px

    base = boxes(1.0, 1.0)
    # Jewels doubled: neither crown term moves.
    assert boxes(2.0, 1.0) == base
    # Crown Text doubled: both crown terms double, together.
    assert boxes(1.0, 2.0) == pytest.approx((base[0] * 2, base[1] * 2))


def test_crown_default_size_unchanged_by_the_decoupling(app):
    """THE FOLDED CONSTANT: both sliders default to 1.0, so removing
    `ring_jewels_scale` from the crown's height folds to a factor of
    EXACTLY 1.0 and no default dial changes by a pixel."""
    skin = build_skin(replace(Settings(), ring="Templar"))
    assert skin.ring_jewels_scale == 1.0
    assert skin.crown_text_scale == 1.0
    radius = 360.0
    new_law = 2 * radius * dial.RING_CROWN_TEXT_SIZE * skin.crown_text_scale
    old_law = new_law * skin.ring_jewels_scale
    assert new_law == old_law


# ---------------------------------------- THE REPRESENTATIVE PRESETS LAW
# (owner ruling 2026-08-07): the six BUNDLED presets ship crown and
# jewels in ONE family — the same metal group and treatment per preset.
# A user's own tinkering and custom rings are unrestricted; this is a
# statement about what the product SHIPS.

BUNDLED = ("DOMY", "LOOP", "Dollar", "The One", "Templar", "CHI")


def test_every_bundled_preset_is_registered(app):
    """The roster this law is stated over is the shipped one — a new
    bundled preset must be added here deliberately, never slip past."""
    bundled = tuple(name for name in ring_presets({}) if name in BUNDLED)
    assert sorted(bundled) == sorted(BUNDLED)
    assert sorted(ring_presets({})) == sorted(BUNDLED)


def _accent_metal(finish: str) -> str:
    """The ONE documented accent a preset's own triangle split may wear
    beside its finish (`app.controller._jewel_metal`) — restated here so
    the law is checked against the rule, not against the code."""
    return "gold" if finish == "silver" else "silver"


@pytest.mark.parametrize("ring", BUNDLED)
@pytest.mark.parametrize("finish", ["gold", "silver", "bronze"])
def test_crown_metal_is_the_presets_finish_metal(app, ring, finish):
    """The law's own tooth: whatever finish the watch wears, a bundled
    preset's CROWN wears that finish — and its jewels wear the finish
    and, at most, its ONE documented accent. No third metal, and no
    preset pinning its crown away from the family its jewels are in.

    FINDING (2026-08-07): the Dollar is the one preset whose split is
    3+3 rather than 3+1 — the banknote's own Trinity/Union reading of
    the hexagram (CANON.md §The Banknote), a settled ruling this round
    does not reopen. It still satisfies the law as stated: BOTH its
    groups are the finish and its accent, and the crown is the finish.
    That is why the law is written as "one family", not "a strict
    majority" — a majority test would have condemned a ruled design."""
    skin = build_skin(replace(Settings(), ring=ring, ring_finish=finish))
    crown_metal = skin.ring.crown_text_metal
    assert crown_metal == finish, ring
    metals = [
        skin.ring.jewel_metal.get(hour, "gold") for hour in skin.ring.jewels
    ]
    assert metals, ring
    family = {finish, _accent_metal(finish)}
    assert set(metals) <= family, (
        f"{ring}: jewels wear {sorted(set(metals))}, outside the preset's "
        f"own family {sorted(family)} — per-preset metal drift"
    )
    assert crown_metal in metals, (
        f"{ring}: the crown wears {crown_metal} but NO jewel does — the "
        f"crown and the jewels must be one family"
    )
    # Only a preset with its own ruled triangle split may carry two
    # metals at all; every other bundled preset is strictly one.
    if len(set(metals)) > 1:
        assert ring in ("DOMY", "LOOP", "Dollar"), (
            f"{ring} split its jewels into two metals without a ruled "
            f"triangle — the representative-presets law forbids it"
        )


@pytest.mark.parametrize("ring", BUNDLED)
def test_crown_and_jewels_share_one_treatment(app, ring):
    """Same TREATMENT, not only the same metal: both families are
    stamped by `RingLayer._draw_ring_glyph` from the SAME jewel art
    directory, so no bundled preset can ship a crown drawn by a
    different machine than its jewels."""
    skin = build_skin(replace(Settings(), ring=ring))
    for entry in skin.ring.crown_text:
        for asset, _theta in entry["glyphs"]:
            assert asset.parent == dial.RING_JEWEL_ART_DIR, ring
    for asset in skin.ring.jewel_art.values():
        assert asset.parent == dial.RING_JEWEL_ART_DIR, ring
