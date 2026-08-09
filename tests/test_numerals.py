"""THE LIVE NUMERAL BANDS — the golden tables and the rendering smoke.

Pins every law `research/hour_numerals.md` settles that a machine can
check: the seating rot() piecewise (including the ROTATED-band cases
that are the whole reason the band is computed), the radial light table
at the four square angles, the parity colour assignment, the extrude
step count, the live crown's glyph sequences and its minute cadence,
Jerusalem's own hour, and the process-wide band cache.

Plus the two things only a real render can answer: that a 1440 px outer
band actually carries non-blank numerals at the expected angular seats,
and that the inner band's white GLOW is really there (alpha outside the
ink around a numeral).
"""

import math
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# NO unconditional offscreen default here (2026-08-06): the offscreen
# QPA plugin exposes ZERO font families on this machine, which silently
# turned the two default-face checks at the bottom of this file into
# permanent skips. The `app` fixture asks for the NATIVE platform first
# and falls back to offscreen when there is no desktop to talk to —
# every measurement in this module passes identically either way (both
# platforms rasterize through the same QImage path), so the only thing
# the native platform changes is that the font checks can actually run.

import astral
import pytest
from PySide6.QtGui import QColor, QFontDatabase
from PySide6.QtWidgets import QApplication

from app.controller import build_skin
from app.settings_store import Settings, SettingsStore, replace
from config import dial, palette
from core import numerals
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render import letter_plates, numeral_bands, numeral_fonts
from render.numeral_bands import outer_centreline, outer_band_edges, interior_scale
from render.assets import AssetCache
from render.compositor import Compositor, _build_layers
from render.context import Cadence, RenderContext
from render.layers.numerals import LiveCrownLayer, band_spec
from render.layers.ring import RingLayer
from render.painting import dial_point


@pytest.fixture(scope="module")
def app():
    """Native platform first (real fonts, real DPI), offscreen only when
    there is no desktop — the same native-first pattern
    `tests/test_layout_audit.py` uses, and for the same reason: the
    offscreen plugin measures a different machine than the one the
    product runs on."""
    existing = QApplication.instance()
    if existing is not None:
        return existing
    try:
        return QApplication([])
    except Exception:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        return QApplication([])


@pytest.fixture(scope="module")
def frame_args():
    now = datetime(2026, 1, 1, 12, 35, tzinfo=ZoneInfo("Europe/Belgrade"))
    observer = astral.Observer(latitude=44.8, longitude=20.5)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


# ------------------------------------------------------------ the seating law

def test_seat_rotation_reproduces_the_ledger_piecewise():
    """hour_numerals.md §4: a numeral on a SQUARE angle stands upright,
    every other takes its own angle, and the lower half turns a further
    180 deg so nothing reads upside down."""
    assert numerals.seat_rotation(0.0) == 0.0
    assert numerals.seat_rotation(90.0) == 0.0
    assert numerals.seat_rotation(180.0) == 0.0
    assert numerals.seat_rotation(-90.0) == 0.0
    assert numerals.seat_rotation(45.0) == 45.0
    assert numerals.seat_rotation(-45.0) == -45.0
    assert numerals.seat_rotation(135.0) == 315.0        # the lower half
    assert numerals.seat_rotation(-135.0) == 45.0
    assert numerals.seat_rotation(179.0) == 359.0


def test_upright_seating_never_turns_anything():
    for degree in (0.0, 37.5, 90.0, 123.0, -168.0):
        assert numerals.seat_rotation(degree, "upright") == 0.0


def test_square_on_ring_stands_twelve_eighteen_zero_and_six_up():
    """With the band square-on (offset 0) exactly 12, 18, 0 and 6 are
    upright — the ledger's own worked example."""
    upright = [
        hour for hour in range(24)
        if numerals.seat_rotation(numerals.hour_angle(hour)) == 0.0
    ]
    assert upright == [0, 6, 12, 18]


def test_a_rotated_band_stands_whoever_landed_on_a_square_angle():
    """THE POINT OF THE WHOLE ENGINE (§1/§4): turn the band and the
    four upright numerals CHANGE — a seat belongs to the angle it lands
    on, never to the hour it carries. At +15 deg the band has moved one
    whole hour, so 11/17/23/5 take the square angles."""
    upright = [
        hour for hour in range(24)
        if numerals.seat_rotation(numerals.hour_angle(hour, 15.0)) == 0.0
    ]
    assert upright == [5, 11, 17, 23]
    # And a NON-integer rotation leaves nobody upright at all.
    assert not [
        hour for hour in range(24)
        if numerals.seat_rotation(numerals.hour_angle(hour, 11.25)) == 0.0
    ]


def test_hour_angles_and_labels_are_bare_and_folded():
    assert numerals.hour_labels()[0] == "0"          # no leading zero
    assert numerals.hour_labels()[23] == "23"
    assert numerals.hour_angle(12) == 0.0
    assert numerals.hour_angle(18) == 90.0
    assert numerals.hour_angle(0) == 180.0
    assert numerals.hour_angle(6) == -90.0
    assert numerals.minute_labels() == (
        "0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"
    )


def test_the_inner_band_never_rotates():
    """ring_rework §2: the inner band NEVER rotates, in either mode —
    it takes no offset at all, by construction."""
    assert numerals.minute_angle(15) == 90.0
    assert numerals.minute_angle(30) == 180.0


# ------------------------------------------------------------- the light law

@pytest.mark.parametrize(
    "degree,expected",
    [(0.0, (0.0, 1.0)), (90.0, (1.0, 0.0)), (180.0, (0.0, -1.0)),
     (270.0, (-1.0, 0.0))],
)
def test_radial_light_reproduces_the_ledger_table_exactly(degree, expected):
    """hour_numerals.md §6, y counted positive UPWARD: the four square
    angles must come out (0,+d) (+d,0) (0,-d) (-d,0)."""
    depth = 3.0
    dx, dy = numerals.light_offset(degree, depth)
    assert dx == pytest.approx(expected[0] * depth, abs=1e-9)
    assert dy == pytest.approx(expected[1] * depth, abs=1e-9)


def test_fixed_light_lands_exactly_what_was_typed():
    """§6: what is typed is what lands; `depth` says nothing here."""
    assert numerals.light_offset(137.0, 9.0, "fixed", (2.0, -5.0)) == (2.0, -5.0)


# ------------------------------------------------------------ the relief model

def test_extrude_step_count_is_round_depth():
    assert numerals.extrude_step_count(3.0) == 3
    assert numerals.extrude_step_count(3.4) == 3
    assert numerals.extrude_step_count(3.6) == 4
    assert numerals.extrude_step_count(0.2) == 1       # never fewer than one


def test_extrude_lays_n_copies_out_to_the_full_depth():
    throw = numerals.light_offset(0.0, 4.0)
    offsets = numerals.relief_offsets("extrude", 4.0, throw)
    assert len(offsets) == 4
    assert offsets[0][1] == pytest.approx(4.0)        # far end FIRST
    assert offsets[-1][1] == pytest.approx(1.0)
    assert {role for _, _, role in offsets} == {numerals.SHADE}


def test_cast_is_one_copy_and_emboss_is_a_dark_and_a_lit_one():
    throw = numerals.light_offset(90.0, 3.0)
    cast = numerals.relief_offsets("cast", 3.0, throw)
    assert len(cast) == 1
    assert cast[0][0] == pytest.approx(3.0)
    assert cast[0][1] == pytest.approx(0.0, abs=1e-9)
    assert cast[0][2] == numerals.SHADE
    emboss = numerals.relief_offsets("emboss", 3.0, throw)
    assert len(emboss) == 2
    assert emboss[0][2] == numerals.SHADE
    assert emboss[1][2] == numerals.LIT
    assert emboss[1][0] == pytest.approx(-0.6 * 3.0)


def test_fixed_light_extrude_counts_steps_from_the_offsets_own_length():
    """§6: in fixed light `depth` says nothing, so the step count comes
    from the throw itself."""
    offsets = numerals.relief_offsets("extrude", 0.0, (3.0, 4.0))
    assert len(offsets) == 5                            # hypot(3, 4)


# ---------------------------------------------------------------- the parity

def test_parity_roles_and_their_colours():
    """§3: even = a white plate laid on the ring; odd = a cut-out, the
    ring seen through the numeral."""
    assert [numerals.parity_role(label) for label in ("0", "1", "12", "23")] == [
        "even", "odd", "even", "odd"
    ]
    even = palette.NUMERAL_PARITY_COLORS["even"]
    odd = palette.NUMERAL_PARITY_COLORS["odd"]
    assert even["body"] == palette.NUMERAL_WHITE
    assert even["border"] == palette.NUMERAL_RING_GROUND
    assert odd["body"] == palette.NUMERAL_RING_GROUND
    assert odd["border"] == palette.NUMERAL_WHITE
    assert palette.NUMERAL_RING_GROUND == "#656A70"


# --------------------------------------------------------- THE COMPOSITION LAW

def test_a_jewel_seat_carries_no_numeral():
    """THE FIDELITY RULING's first law (ring_rework §2): the composition
    places EITHER the preset's letter OR a numeral at a position, never
    both. An Ω with a 0 under it is the defect it was issued for."""
    assert 24 not in numerals.numeral_hours((12, 20, 24, 4))   # DOMY
    assert 0 not in numerals.numeral_hours((12, 20, 24, 4))    # 24 folds to 0
    assert numerals.numeral_hours((24,)) == tuple(range(1, 24))  # CHI: X at 24h
    assert numerals.numeral_hours(()) == tuple(range(24))
    # Every hour is accounted for exactly once, whatever the preset.
    for seats in ((12, 16, 20, 24, 4, 8), (12, 15, 18, 21, 24, 3, 6, 9)):
        drawn = numerals.numeral_hours(seats)
        assert len(set(drawn)) == len(drawn)
        assert set(drawn) | {seat % 24 for seat in seats} == set(range(24))


def test_every_shipped_inner_variant_composes_from_a_real_base_plate():
    """The INNER half of the composition law: each variant is one of the
    owner's NUMBERLESS plates plus the seats that carry a number — and a
    seat that carries one of his arrows never carries a number."""
    from config import constants
    assert set(dial.RING_INNER_COMPOSITION) == set(constants.RING_INNERS)
    arrow_seats = {
        "simple": (), "simple_point": (0,), "simple_cross": (0, 15, 30, 45),
        "simple_octa": (0, 15, 30, 45),
    }
    for variant, entry in dial.RING_INNER_COMPOSITION.items():
        base = dial.RING_INNER_ART_DIR / f"{entry['base']}.png"
        assert base.exists(), f"{variant} names a base plate that is not there"
        assert entry["base"] in constants.RING_INNERS
        numbers = set(entry["numbers"])
        assert not numbers & set(arrow_seats[entry["base"]]), variant
        assert numbers <= set(range(0, 60, dial.NUMERAL_MINUTE_LABEL_STEP))


def test_the_inner_seats_are_labelled_bare_and_never_rotate():
    seats = dict(numerals.inner_number_seats("seconds"))
    assert seats["5"] == 30.0 and seats["30"] == 180.0
    assert "0" not in seats                    # the arrow holds the top seat
    assert numerals.inner_number_seats("simple") == ()
    assert numerals.inner_composition("a-custom-file")["numbers"] == ()


# --------------------------------------------------------------- the live crown

def test_crown_sequences_for_both_shipped_formats():
    assert numerals.crown_sequence(12, 35, "hh:mm") == ("1", "2", ":", "3", "5")
    assert numerals.crown_sequence(12, 35, "12h 35min") == (
        "1", "2", "h", " ", "3", "5", "m", "i", "n"
    )
    assert numerals.crown_sequence(9, 5, "hh:mm") == ("0", "9", ":", "0", "5")
    # The bare hour follows the hour band's own no-leading-zero rule.
    assert numerals.crown_sequence(9, 5, "12h 35min")[0] == "9"


def test_the_crown_alphabet_is_the_eleven_plus_the_small_cut():
    assert numerals.crown_digits_and_colon() == tuple("0123456789:")
    assert len(numerals.crown_digits_and_colon()) == 11
    alphabet = numerals.crown_glyph_alphabet()
    # ALL ten digits, never only the ones one sample minute happens to
    # show — the crown must be able to say every minute.
    assert set(numerals.crown_digits_and_colon()).issubset(set(alphabet))
    assert set("hmin").issubset(set(alphabet))
    assert " " not in alphabet


def test_the_small_cut_covers_only_the_unit_words():
    sequence = numerals.crown_sequence(12, 35, "12h 35min")
    small = numerals.crown_small_cut(sequence)
    assert [g for g, s in zip(sequence, small) if s] == ["h", "m", "i", "n"]


def test_crown_arc_is_centered_on_its_anchor_and_reads_left_to_right():
    top = numerals.crown_arc_angles(5, "top")
    assert sum(top) == pytest.approx(0.0)               # centered on the top
    assert top[0] < top[-1]                             # clockwise
    bottom = numerals.crown_arc_angles(5, "bottom")
    assert sum(bottom) / 5 == pytest.approx(180.0)
    assert bottom[0] > bottom[-1]                       # counter-clockwise


def test_jerusalem_is_resolved_for_the_templar_crown(frame_args):
    """Templar keeps the hour of JERUSALEM (ring_rework §4 row E) — via
    tzdata, on the tick, never on the paint path."""
    _day, tick = frame_args
    assert tick.crown_zone_hm["local"] == "12:35"
    assert tick.crown_zone_hm["Asia/Jerusalem"] == "13:35"
    assert dial.RING_LIVE_CROWN["Templar"]["zone"] == "Asia/Jerusalem"
    assert dial.RING_LIVE_CROWN["The One"]["zone"] is None


def test_only_the_two_live_crown_presets_build_the_layer(app):
    for name, expected in (
        ("The One", 1), ("Templar", 1), ("DOMY", 0), ("Dollar", 0), ("LOOP", 0),
    ):
        layers = _build_layers(build_skin(Settings(ring=name)))
        assert sum(
            isinstance(layer, LiveCrownLayer) for layer in layers
        ) == expected, name


def test_the_live_crown_is_the_only_minute_cadence_numeral_layer():
    assert LiveCrownLayer.cadence is Cadence.MINUTE
    assert RingLayer.cadence is Cadence.STATIC


def test_the_bands_are_no_longer_layers_of_their_own(app):
    """THE FIDELITY RULING replaced stacking with composition: the two
    band layers that used to sit on top of `RingLayer` are gone, and the
    ring composes both itself. A band layer reappearing in the stack IS
    the stacking defect coming back."""
    kinds = [
        type(layer).__name__
        for layer in _build_layers(build_skin(Settings(ring="The One")))
    ]
    assert "RingLayer" in kinds
    assert not [name for name in kinds if "NumeralLayer" in name]


# ------------------------------------------------------------------ the fonts

def _installed(family: str) -> bool:
    return family in set(QFontDatabase.families())


def test_the_crown_has_no_face_to_pick(app):
    """THE ONE PLATE LAW (owner decree 2026-08-07): the crown draws the
    owner's letter plates, so the whole coverage worry that used to pick
    a special crown FACE is gone — with the setting, the skin field and
    the Watch Face row that offered it."""
    from app.settings_store import Settings as _Settings

    assert not hasattr(dial, "CROWN_FACE_DEFAULT")
    assert not hasattr(_Settings(), "crown_face")


def test_the_hour_band_default_face_draws_every_digit(app):
    """The hour band asks for digits ONLY, which is why the recovered
    Bernard MT Condensed can still be its default despite the empty
    colon/lowercase outlines recorded in hour_numerals.md §7."""
    _require_a_font_database()
    family = dial.NUMERAL_OUTER_FACES[dial.NUMERAL_OUTER_FACE_DEFAULT][0]
    assert _installed(family), f"{family} is not installed on this machine"
    assert numeral_fonts.missing_glyphs(
        "outer", dial.NUMERAL_OUTER_FACE_DEFAULT, numerals.hour_labels()
    ) == ()


def test_an_unknown_face_fails_loudly_instead_of_substituting(app):
    with pytest.raises(numeral_fonts.NumeralFontError):
        numeral_fonts.numeral_font("outer", "Comic Sans MS", 20.0)


# ------------------------------------------------------------------ the cache

def test_the_band_plate_cache_returns_the_same_object(app, frame_args):
    """THE ONE COPY RULE: the same settings must hand back the SAME
    plate — N watches, one copy — and a changed knob must not."""
    day, tick = frame_args
    skin = build_skin(Settings(ring="The One"))
    ctx = RenderContext(
        skin=skin, day=day, tick=tick, radius=200.0, cache=AssetCache(), dpr=1.0,
    )
    spec = band_spec(skin, "outer", ctx)
    assert numeral_bands.band_plate(spec) is numeral_bands.band_plate(spec)
    turned = numeral_bands.BandSpec(**{**spec.__dict__, "offset_deg": 11.25})
    assert numeral_bands.band_plate(turned) is not numeral_bands.band_plate(spec)


def test_a_changed_setting_rebuilds_the_band_key(app, frame_args):
    day, tick = frame_args
    ctx_args = dict(day=day, tick=tick, radius=200.0, cache=AssetCache(), dpr=1.0)
    plain = build_skin(Settings(ring="The One"))
    deeper = build_skin(Settings(ring="The One", numeral_depth=7.0))
    a = band_spec(plain, "outer", RenderContext(skin=plain, **ctx_args))
    b = band_spec(deeper, "outer", RenderContext(skin=deeper, **ctx_args))
    assert a != b


# ----------------------------------------------------------- rendering smoke

def _require_a_font_database() -> None:
    """Skip ONLY for the honest reason, and name it (2026-08-06).

    These two tests used to skip saying "<family> is not installed on
    this machine" — which was FALSE: `C:\\Windows\\Fonts\\bahnschrift.ttf`
    is right there, and under the native platform Qt lists 115 families
    including both defaults. The real cause is the OFFSCREEN QPA plugin
    this module asks for at import: on this machine it exposes ZERO font
    families, so every family reads as missing and the skip hid a check
    that simply could not run.

    So: an EMPTY database is an environment fact and skips, naming the
    platform and how to run the check for real. A NON-empty database
    that lacks the configured default face is a genuine defect — a stale
    pick in `config/dial.py`, exactly what the tests below were written
    to catch — and FAILS."""
    if not QFontDatabase.families():
        pytest.skip(
            "the QPA platform in use exposes no font families at all "
            f"(QT_QPA_PLATFORM="
            f"{os.environ.get('QT_QPA_PLATFORM', 'native')!r}) — run this "
            "module on its own (`python -m pytest tests/test_numerals.py`) "
            "and the native platform answers with every installed family"
        )



def _band_image(band: str, pixels: int, app, frame_args, ring="The One", **overrides):
    day, tick = frame_args
    skin = build_skin(Settings(ring=ring, **overrides))
    ctx = RenderContext(
        skin=skin, day=day, tick=tick, radius=pixels / 2.0,
        cache=AssetCache(), dpr=1.0,
    )
    return numeral_bands.band_plate(band_spec(skin, band, ctx))


def _ink_near(image, angle: float, radius: float, box: int = 26) -> int:
    """Non-transparent pixels in a small box centred on a dial seat."""
    center = dial_point(angle, radius)
    cx = int(image.width() / 2 + center.x())
    cy = int(image.height() / 2 + center.y())
    return sum(
        1
        for y in range(max(0, cy - box), min(image.height(), cy + box))
        for x in range(max(0, cx - box), min(image.width(), cx + box))
        if image.pixelColor(x, y).alpha() > 0
    )


def _glyph_ink(image, angle: float, radius: float, box: int = 26) -> int:
    """Pixels that are NOT the band's own flat metal in a small box on a
    dial seat — i.e. the numeral, its border and its halo. The band now
    carries its own base, so plain alpha would answer "yes" everywhere."""
    ground = QColor(palette.NUMERAL_RING_GROUND)
    center = dial_point(angle, radius)
    cx = int(image.width() / 2 + center.x())
    cy = int(image.height() / 2 + center.y())
    count = 0
    for y in range(max(0, cy - box), min(image.height(), cy + box)):
        for x in range(max(0, cx - box), min(image.width(), cx + box)):
            color = image.pixelColor(x, y)
            if color.alpha() == 0:
                continue
            if abs(color.red() - ground.red()) > 12 or abs(
                color.blue() - ground.blue()
            ) > 12:
                count += 1
    return count


def test_the_bands_seat_list_skips_every_jewel_hour(app, frame_args):
    """THE COMPOSITION LAW where no font can hide it (this one runs on
    any platform): the band builder's own seat list — the exact list it
    turns into paths — carries no letter hour, whatever the preset."""
    day, tick = frame_args
    for ring in ("DOMY", "The One", "Dollar", "CHI"):
        skin = build_skin(Settings(ring=ring))
        ctx = RenderContext(
            skin=skin, day=day, tick=tick, radius=720.0,
            cache=AssetCache(), dpr=1.0,
        )
        spec = band_spec(skin, "outer", ctx)
        assert set(spec.jewel_hours) == set(skin.ring.jewels), ring
        seated = {int(label) for label, _angle, _c in numeral_bands._seats(spec)}
        assert not seated & set(skin.ring.jewels), ring
        assert seated | set(skin.ring.jewels) == set(range(24)), ring


def test_a_1440_outer_band_carries_a_numeral_at_every_free_hour(app, frame_args):
    """THE COMPOSITION LAW on the real plate: a numeral stands at every
    hour The One does not seat a letter on, and NOTHING stands where one
    does."""
    _require_a_font_database()
    skin = build_skin(Settings(ring="The One"))
    image = _band_image("outer", 1440, app, frame_args)
    assert image.width() == 1440
    radius = 720 * dial.NUMERAL_OUTER_RADIUS_FRACTION
    letters = set(skin.ring.jewels)
    assert letters, "The One seats eight letters — the fixture is wrong"
    for hour in range(24):
        angle = numerals.hour_angle(hour)
        ink = _glyph_ink(image, angle, radius)
        if hour in letters:
            assert ink == 0, f"hour {hour} carries a letter AND a numeral"
        else:
            assert ink > 0, f"hour {hour} is blank"


def test_the_omega_seat_carries_no_numeral_under_the_jewel(app, frame_args):
    """The DEFECT THE RULING WAS ISSUED FOR, pinned: DOMY's Ω sits at
    24h, and the band must draw nothing at all there — sampled on the
    real plate, at the seat's own pixels."""
    _require_a_font_database()
    skin = build_skin(Settings(ring="DOMY"))
    assert skin.ring.jewels[0] == "Ω"
    image = _band_image("outer", 1440, app, frame_args, ring="DOMY")
    radius = 720 * dial.NUMERAL_OUTER_RADIUS_FRACTION
    assert _glyph_ink(image, numerals.hour_angle(0), radius, box=34) == 0
    # ... while its neighbours still carry theirs.
    assert _glyph_ink(image, numerals.hour_angle(1), radius) > 0
    assert _glyph_ink(image, numerals.hour_angle(23), radius) > 0


def test_the_outer_band_is_bare_metal_between_the_seats(app, frame_args):
    """Half-way between two hour seats there is only the band's own flat
    ground — proof the ink above is the numerals themselves, and proof
    the base really is the measured flat colour rather than a plate."""
    _require_a_font_database()
    image = _band_image("outer", 1440, app, frame_args)
    radius = 720 * dial.NUMERAL_OUTER_RADIUS_FRACTION
    between = numerals.hour_angle(12) + dial.NUMERAL_HOUR_STEP_DEG / 2.0
    assert _glyph_ink(image, between, radius, box=6) == 0
    center = dial_point(between, radius)
    pixel = image.pixelColor(
        int(image.width() / 2 + center.x()), int(image.height() / 2 + center.y())
    )
    assert pixel.name().upper() == palette.NUMERAL_RING_GROUND
    assert pixel.alpha() == 255


def test_the_band_base_reproduces_the_owners_measured_annulus(app, frame_args):
    """The plates' own geometry, MEASURED at 3600 px and pinned here:
    metal from 0.8858 to 0.9998 of the radius, a black rim on the outer
    edge alone, nothing outside either."""
    image = _band_image("outer", 1440, app, frame_args)
    inner, outer = numeral_bands.outer_band_edges(1.0)
    assert inner == pytest.approx(0.8858, abs=0.001)
    assert outer == pytest.approx(0.9998, abs=0.001)
    between = numerals.hour_angle(12) + dial.NUMERAL_HOUR_STEP_DEG / 2.0

    def at(fraction):
        point = dial_point(between, 720 * fraction)
        return image.pixelColor(
            int(image.width() / 2 + point.x()),
            int(image.height() / 2 + point.y()),
        )

    assert at(inner - 0.006).alpha() == 0                  # nothing inside
    assert at(0.94).name().upper() == palette.NUMERAL_RING_GROUND
    assert at(outer - 0.0015).name().upper() == palette.NUMERAL_BAND_RIM
    assert at(outer + 0.006).alpha() == 0                  # nothing outside


def test_a_rotated_outer_band_moves_its_ink_with_the_hours(app, frame_args):
    """The band key carries `offset_deg`, so a turned band really draws
    its numerals at the turned angles (wave 4's whole contract)."""
    day, tick = frame_args
    skin = build_skin(Settings(ring="The One"))
    ctx = RenderContext(
        skin=skin, day=day, tick=tick, radius=720.0, cache=AssetCache(), dpr=1.0,
    )
    spec = band_spec(skin, "outer", ctx)
    turned = numeral_bands.BandSpec(**{**spec.__dict__, "offset_deg": 30.0})
    image = numeral_bands.band_plate(turned)
    radius = 720 * dial.NUMERAL_OUTER_RADIUS_FRACTION
    assert _ink_near(image, 30.0, radius) > 0          # hour 12 moved to +30
    assert _ink_near(image, 0.0, radius) > 0           # hour 10 took the top


def test_outer_ring_size_grows_the_band_inward():
    """THE INWARD-GROWTH LAW (owner verdict 2026-08-09, superseding the
    outward rule this test used to pin): at 1.0 the band's outer edge
    already stands at the measured rim (0.9998 of the radius), so a
    width multiplier had nowhere outward to go — the owner's own
    screenshot showed the band sliced into an octagon. The OUTER edge is
    pinned; the multiplier moves the INNER edge toward the centre, the
    centreline follows by half the change, and the interior world
    yields by `interior_scale` so the minute track keeps abutting the
    band."""
    width = dial.NUMERAL_OUTER_BAND_WIDTH_FRACTION
    default_inner, default_outer = outer_band_edges(1.0)
    assert outer_centreline(1.0) == pytest.approx(
        dial.NUMERAL_OUTER_RADIUS_FRACTION
    )
    # The rim never moves, at ANY multiplier — the whole point.
    for ring_size in (0.5, 1.0, 1.5, 2.0):
        _inner, outer = outer_band_edges(ring_size)
        assert outer == pytest.approx(default_outer)
        assert outer <= 1.0 + 1e-9
    wide_inner, _outer = outer_band_edges(2.0)
    assert wide_inner == pytest.approx(default_outer - 2.0 * width)
    assert outer_centreline(2.0) == pytest.approx(default_outer - width)
    # The interior yields exactly by the inner edge's own ratio…
    assert interior_scale(2.0) == pytest.approx(wide_inner / default_inner)
    # …and a THINNER band leaves the interior untouched (the default
    # renders bit-for-bit unchanged).
    assert interior_scale(1.0) == 1.0
    assert interior_scale(0.5) == 1.0


def test_a_wider_outer_ring_really_draws_further_in(app, frame_args):
    """Hour 13 — The One seats letters on 12/15/18/21/24/3/6/9, so 13 is
    one of the seats that actually carries a numeral. Under THE
    INWARD-GROWTH LAW a wider band's numerals sit INSIDE the default
    centreline (the band grew toward the centre), and there is ink at
    the new centreline."""
    _require_a_font_database()
    wide = _band_image(
        "outer", 1440, app, frame_args, numeral_outer_ring_size=1.5,
    )
    angle = numerals.hour_angle(13)
    new_centre = 720 * outer_centreline(1.5)
    assert outer_centreline(1.5) < outer_centreline(1.0)
    assert _glyph_ink(wide, angle, new_centre) > 0


def test_an_arrow_seat_carries_no_number(app, frame_args):
    """The INNER half of the composition law on the real plate: The One
    reads `simple_octa`, whose five-minute seats ALL carry one of his
    arrows, so the live plate it composes is empty — the band on screen
    is his art untouched."""
    image = _band_image("inner", 1440, app, frame_args)
    assert not any(
        image.pixelColor(x, y).alpha() > 0
        for y in range(0, 1440, 3) for x in range(0, 1440, 3)
    )


def test_the_inner_band_wears_a_white_glow_around_its_ink(app, frame_args):
    """ring_rework §2: the inner band's relief is a WHITE GLOW — so a
    ring of PARTIAL alpha must surround the solid ink of a numeral, and
    it must be white, not black. DOMY reads `seconds`, which composes a
    number into every five-minute seat but the arrow's own."""
    image = _band_image("inner", 1440, app, frame_args, ring="DOMY")
    radius = 720 * dial.MINUTES_RADIUS_FRACTION
    center = dial_point(numerals.minute_angle(15), radius)
    cx = int(image.width() / 2 + center.x())
    cy = int(image.height() / 2 + center.y())
    partial = [
        image.pixelColor(x, y)
        for y in range(cy - 40, cy + 40)
        for x in range(cx - 40, cx + 40)
        if 0 < image.pixelColor(x, y).alpha() < 255
    ]
    assert partial, "no soft edge at all — the glow pass did not run"
    # A glow, not a shadow: the soft pixels lean bright.
    assert max(color.lightness() for color in partial) > 200


def test_the_whole_dial_still_renders_with_both_bands(app, frame_args):
    day, tick = frame_args
    skin = build_skin(Settings(ring="The One"))
    image = Compositor(skin, AssetCache()).render_offscreen(720.0, 1.0, day, tick)
    assert image.width() == 720
    assert any(
        image.pixelColor(x, 8).alpha() > 0 for x in range(0, 720, 4)
    ), "the top of the dial is empty — the outer band did not compose"


# --------------------------------------------------------------- the settings

def test_a_settings_file_without_the_numeral_keys_loads_clean(tmp_path):
    """Old files must load at the SETTLED defaults, never as corrupt."""
    path = tmp_path / "settings.json"
    path.write_text(
        '{"schema_version": 1, "ring": "DOMY", "window": {"x": null, "y": null, '
        '"diameter": 720}}',
        encoding="utf-8",
    )
    loaded = SettingsStore(path).load()
    assert loaded.numeral_face == dial.NUMERAL_OUTER_FACE_DEFAULT
    assert loaded.minutes_face == dial.MINUTES_FACE_DEFAULT
    assert loaded.numeral_seating == "arc"
    assert loaded.numeral_relief == "extrude"
    assert loaded.numeral_depth == 3.0
    assert loaded.numeral_light == "radial"
    assert loaded.numeral_darkness == 1.0
    # The Fidelity Ruling's own measured defaults, not the ledger's
    # first-pass guesses: an odd numeral needs its white rim and the
    # halo needs its soft edge, or the band is not his art.
    assert loaded.numeral_contact_blur == 2.0
    assert loaded.numeral_border == 4.0
    assert loaded.numeral_outer_size == 124
    assert loaded.minutes_size == 84
    assert loaded.crown_time_format == "hh:mm"


def test_the_numeral_settings_round_trip(tmp_path):
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    store.save(Settings(numeral_relief="emboss", crown_time_format="12h 35min"))
    loaded = store.load()
    assert loaded.numeral_relief == "emboss"
    assert loaded.crown_time_format == "12h 35min"


def test_an_unknown_stored_numeral_choice_is_corrupt_not_silently_default(tmp_path):
    from app.settings_store import SettingsCorruptError

    path = tmp_path / "settings.json"
    path.write_text(
        '{"ring": "DOMY", "window": {"x": null, "y": null, "diameter": 720}, '
        '"numeral_relief": "chiselled"}',
        encoding="utf-8",
    )
    with pytest.raises(SettingsCorruptError):
        SettingsStore(path).load()


# --------------------------------------------------- THE TIME CROWN LOOK
# Crown Polish round (owner correction 2026-08-06, research/ring_rework.md
# §3): the live crown's digits-and-colon wear the SAME look every ring
# letter wears — metal finish + THE LETTER SHADOW LAW's stamped halo —
# never the outer band's parity plate-and-frame.

def _crown_spec(metal="gold", shade="classic"):
    """A crown spec whose plates are the GOLD masters — the hand-built
    twin of what `render.layers.numerals.crown_spec` assembles for a
    real watch (THE ONE PLATE LAW: every glyph is a plate, so the spec
    carries one resolved file per glyph)."""
    return numeral_bands.CrownSpec(
        pixels=720, dpr=1.0, height_px=720 * dial.RING_CROWN_TEXT_SIZE,
        metal=metal, shade=shade,
        sources=tuple(
            (glyph, str(letter_plates.plate_path(glyph)))
            for glyph in numerals.crown_glyph_alphabet() if glyph != " "
        ),
    )


def test_every_crown_glyph_resolves_through_the_jewel_pipeline(app):
    """THE ONE PLATE LAW (owner decree 2026-08-07): no glyph of the live
    crown draws a font outline. Every one of them — the ten digits and
    HIS colon plate alike — is resolved through the exact door every
    ring letter resolves its finish through (`render.asset_recolor.
    jewel_metal_file`, the SAME call `RingLayer._draw_ring_glyph` makes
    for a real letter)."""
    from render.layers import numerals as numeral_layers

    calls = []
    original = numeral_layers.jewel_metal_file

    def spy(path, metal):
        calls.append((path, metal))
        return original(path, metal)

    numeral_layers.jewel_metal_file = spy
    try:
        numeral_bands.clear_cache()
        skin = build_skin(replace(Settings(), ring="The One", ring_finish="silver"))
        ctx = RenderContext(
            radius=360.0, dpr=1.0, skin=skin, cache=None, tick=None, day=None,
        )
        spec = numeral_layers.crown_spec(skin, ctx)
        glyphs = numeral_bands.crown_glyph_set(spec)
    finally:
        numeral_layers.jewel_metal_file = original
        numeral_bands.clear_cache()
    asked = {path for path, _metal in calls}
    for glyph in numerals.crown_glyph_alphabet():
        if glyph == " ":
            continue
        assert letter_plates.plate_path(glyph) in asked, glyph
        assert glyph in glyphs


def test_the_crown_asks_no_font_for_anything(app, monkeypatch):
    """The tooth for the failure that made the owner shout: the crown
    used to prove a FONT could draw its glyphs and never proved a PLATE
    existed, so a missing alphabet was a silent fallback. There is no
    font coverage check left because there is no font left."""
    called = []
    monkeypatch.setattr(
        numeral_bands, "relief",
        _FontTrap(numeral_bands.relief, called),
    )
    numeral_bands.clear_cache()
    try:
        numeral_bands.crown_glyph_set(_crown_spec())
    finally:
        numeral_bands.clear_cache()
    assert called == [], f"the crown drew a font glyph: {called}"


class _FontTrap:
    """`numeral_relief` with `glyph_path` booby-trapped — every other
    attribute passes straight through, so the crown builds normally
    unless it asks for a FONT OUTLINE."""

    def __init__(self, wrapped, log):
        self._wrapped, self._log = wrapped, log

    def __getattr__(self, name):
        if name == "glyph_path":
            def trap(*args, **kwargs):
                self._log.append(args[:1])
                return self._wrapped.glyph_path(*args, **kwargs)
            return trap
        return getattr(self._wrapped, name)


def test_digits_wear_the_ring_metal_never_band_parity(app):
    """A crown digit is a recolored PLATE, so it can never read as the
    outer band's white/ring-ground parity fill
    (`palette.NUMERAL_PARITY_COLORS`) — the look the owner ruled off the
    time crown entirely."""
    numeral_bands.clear_cache()
    digit = numeral_bands.crown_glyph_set(_crown_spec())["5"]
    counts = {}
    for y in range(digit.height()):
        for x in range(digit.width()):
            color = digit.pixelColor(x, y)
            if color.alpha() > 200 and color.value() > 40:
                key = (color.red(), color.green(), color.blue())
                counts[key] = counts.get(key, 0) + 1
    dominant = max(counts, key=counts.get)
    for role in ("even", "odd"):
        parity = QColor(palette.NUMERAL_PARITY_COLORS[role]["body"])
        distance = (
            abs(dominant[0] - parity.red())
            + abs(dominant[1] - parity.green())
            + abs(dominant[2] - parity.blue())
        )
        assert distance > 60, f"the crown digit reads as band-parity {role}"
    numeral_bands.clear_cache()


def test_digit_glyph_carries_the_jewel_shadow_stamp(app, monkeypatch):
    """The stamped halo really is baked into the tile: at
    `RING_JEWEL_SHADOW_RADIUS` 0 every shadow copy lands exactly on the
    glyph's own silhouette (no reach beyond it); at the real radius the
    copies are offset outward and the tile carries MORE opaque pixels
    for the identical glyph."""
    def _opaque_count(image) -> int:
        return sum(
            1
            for y in range(image.height())
            for x in range(image.width())
            if image.pixelColor(x, y).alpha() > 0
        )

    spec = _crown_spec()
    numeral_bands.clear_cache()
    with_shadow = numeral_bands.crown_glyph_set(spec)["5"]

    monkeypatch.setattr(dial, "RING_JEWEL_SHADOW_RADIUS", 0.0)
    numeral_bands.clear_cache()
    without_shadow = numeral_bands.crown_glyph_set(spec)["5"]

    assert _opaque_count(with_shadow) > _opaque_count(without_shadow)
    numeral_bands.clear_cache()


# ------------------------------------------------- THE LIVE CROWN'S MARGIN
# Crown Polish round TASK 2 (owner correction 2026-08-06): The One's top
# crown arc was clipped by the window edge at default size —
# `dial_window_margin_fraction` never reserved for `dial.RING_LIVE_CROWN`.

def test_the_ones_live_crown_stays_inside_the_window_at_default_size(
    app, frame_args,
):
    """The pixel side of the TASK 2 fix, mirroring
    tests/test_pointer.py::test_window_margin_renders_glow_without_clipping's
    own construction: The One's DEFAULT skin, rendered into the LIVE
    margin-sized window at `dial.DEFAULT_DIAL_DIAMETER`. The outermost
    frame must stay fully transparent (the crown never clips) and the
    live glyphs must actually be present near the top (the margin is not
    merely oversized, the arc genuinely reaches close to the edge)."""
    from config import defaults
    from PySide6.QtCore import Qt as _Qt
    from PySide6.QtGui import QImage, QPainter

    day, tick = frame_args
    skin = build_skin(Settings(ring="The One"))
    diameter = dial.DEFAULT_DIAL_DIAMETER
    margin_px = round(diameter * defaults.dial_window_margin_fraction(skin))
    window = diameter + 2 * margin_px

    comp = Compositor(skin, AssetCache())
    comp.set_day(day)
    image = QImage(window, window, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(_Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.translate(margin_px, margin_px)     # the widget's own offset
    comp.paint(painter, float(diameter), 1.0, tick)
    painter.end()

    # NEVER CLIPPED — the outermost 1-px frame is fully transparent.
    border_alpha = max(
        max(
            image.pixelColor(i, 0).alpha(),
            image.pixelColor(i, window - 1).alpha(),
            image.pixelColor(0, i).alpha(),
            image.pixelColor(window - 1, i).alpha(),
        )
        for i in range(window)
    )
    assert border_alpha == 0
    # The live crown genuinely draws SOMETHING near the top of the window
    # (the top arc keeps the civil hour) — not just an oversized margin.
    top_band = any(
        image.pixelColor(x, y).alpha() > 30
        for y in range(0, margin_px + 4)
        for x in range(window // 4, 3 * window // 4)
    )
    assert top_band, "the live crown's top arc never reached near the edge"
