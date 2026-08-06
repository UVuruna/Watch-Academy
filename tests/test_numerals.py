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
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from app.controller import build_skin
from app.settings_store import Settings, SettingsStore
from config import dial, palette
from core import numerals
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render import numeral_bands, numeral_fonts
from render.numeral_bands import outer_centreline
from render.assets import AssetCache
from render.compositor import Compositor, _build_layers
from render.context import Cadence, RenderContext
from render.layers.numerals import (
    InnerNumeralLayer,
    LiveCrownLayer,
    OuterNumeralLayer,
    band_spec,
)
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


# ------------------------------------------------------------ the tick vocabulary

def test_inner_tick_plan_names_all_five_kinds_at_the_right_counts():
    plan = numerals.inner_tick_plan()
    assert len(plan) == 360                              # the DAY ticks
    kinds = [kind for _, kind in plan]
    assert kinds.count(numerals.TICK_POINTER) == 4        # the quarter arrows
    assert kinds.count(numerals.TICK_LONG) == 8           # 12 minus the 4 pointers
    assert kinds.count(numerals.TICK_SHORT) == 24         # two beside each LONG
    assert set(kinds) == {
        numerals.TICK_DAY, numerals.TICK_SECOND, numerals.TICK_SHORT,
        numerals.TICK_LONG, numerals.TICK_POINTER,
    }


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
    assert OuterNumeralLayer.cadence is Cadence.STATIC
    assert InnerNumeralLayer.cadence is Cadence.STATIC


def test_both_numeral_bands_are_stacked_above_the_ring(app):
    layers = _build_layers(build_skin(Settings(ring="The One")))
    kinds = [type(layer).__name__ for layer in layers]
    assert kinds.index("RingLayer") < kinds.index("InnerNumeralLayer")
    assert kinds.index("InnerNumeralLayer") < kinds.index("OuterNumeralLayer")


# ------------------------------------------------------------------ the fonts

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


def _installed(family: str) -> bool:
    return family in set(QFontDatabase.families())


def test_the_crown_default_face_draws_every_one_of_the_eleven(app):
    """The crown needs the colon, and the hour band's own default face
    cannot draw one on this install — so the crown's default is picked
    for coverage. If this fails, the pick in config/dial.py is stale."""
    _require_a_font_database()
    family = dial.NUMERAL_OUTER_FACES[dial.CROWN_FACE_DEFAULT][0]
    assert _installed(family), f"{family} is not installed on this machine"
    assert numeral_fonts.missing_glyphs(
        "outer", dial.CROWN_FACE_DEFAULT, numerals.crown_glyph_alphabet()
    ) == ()


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

def _band_image(band: str, pixels: int, app, frame_args, **overrides):
    day, tick = frame_args
    skin = build_skin(Settings(ring="The One", **overrides))
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


def test_a_1440_outer_band_carries_ink_at_every_hour_seat(app, frame_args):
    image = _band_image("outer", 1440, app, frame_args)
    assert image.width() == 1440
    radius = 720 * dial.NUMERAL_OUTER_RADIUS_FRACTION
    for hour in range(24):
        angle = numerals.hour_angle(hour)
        assert _ink_near(image, angle, radius) > 0, f"hour {hour} is blank"


def test_the_outer_band_is_empty_between_the_seats(app, frame_args):
    """Half-way between two hour seats there is nothing — proof the ink
    above is the numerals themselves, not a filled band."""
    image = _band_image("outer", 1440, app, frame_args)
    radius = 720 * dial.NUMERAL_OUTER_RADIUS_FRACTION
    between = numerals.hour_angle(12) + dial.NUMERAL_HOUR_STEP_DEG / 2.0
    assert _ink_near(image, between, radius, box=6) == 0


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


def test_outer_ring_size_moves_the_bands_outer_edge_alone():
    """ring_rework §5's "outer ring size" is the WIDTH of the band the
    letters and numbers stand in. The inner edge is fixed — it abuts the
    minute band — so the width multiplier moves the outer edge, and the
    centreline follows by half the change."""
    width = dial.NUMERAL_OUTER_BAND_WIDTH_FRACTION
    assert outer_centreline(1.0) == pytest.approx(
        dial.NUMERAL_OUTER_RADIUS_FRACTION
    )
    assert outer_centreline(2.0) == pytest.approx(
        dial.NUMERAL_OUTER_RADIUS_FRACTION + width / 2.0
    )
    assert outer_centreline(0.5) == pytest.approx(
        dial.NUMERAL_OUTER_RADIUS_FRACTION - width / 4.0
    )


def test_a_wider_outer_ring_really_draws_further_out(app, frame_args):
    wide = _band_image(
        "outer", 1440, app, frame_args, numeral_outer_ring_size=2.0,
    )
    far = 720 * outer_centreline(2.0)
    near = 720 * outer_centreline(1.0)
    assert _ink_near(wide, numerals.hour_angle(12), far) > 0
    assert _ink_near(wide, numerals.hour_angle(12), far) > _ink_near(
        wide, numerals.hour_angle(12), near - 40
    )


def test_the_inner_band_wears_a_white_glow_around_its_ink(app, frame_args):
    """ring_rework §2: the inner band's relief is a WHITE GLOW — so a
    ring of PARTIAL alpha must surround the solid ink of a numeral, and
    it must be white, not black."""
    image = _band_image("inner", 1440, app, frame_args)
    radius = 720 * dial.NUMERAL_INNER_RADIUS_FRACTION
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
    assert loaded.numeral_inner_face == dial.NUMERAL_INNER_FACE_DEFAULT
    assert loaded.numeral_seating == "arc"
    assert loaded.numeral_relief == "extrude"
    assert loaded.numeral_depth == 3.0
    assert loaded.numeral_light == "radial"
    assert loaded.numeral_darkness == 1.0
    assert loaded.numeral_contact_blur == 0.5
    assert loaded.numeral_border == 0.0
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
