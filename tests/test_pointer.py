"""Pointer variants (hexa/cross/octa): slot layouts, shared-slot
priority, palette presets, the octa bottom slot, the Umbra and the
solar-rotation toggle."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
import math
from datetime import datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import constants, defaults
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor, _build_layers
from render.layers import (
    BottomSlotLayer,
    HandLayer,
    palette_for,
    today_slot_theta,
    umbra_ladder,
    visible_occupant,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def july_wednesday(app):
    """2026-07-08 (a Wednesday) at noon in Belgrade."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    observer = astral.Observer(latitude=city["latitude"], longitude=city["longitude"])
    day = build_day_context(
        now,
        observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


# --- Slot layouts ---------------------------------------------------------------


def test_every_layout_seats_the_whole_week():
    for pointer, slots in constants.POINTER_WEEKDAY_SLOTS.items():
        seated = [body for _, occupants in slots for body in occupants]
        if pointer in ("hexa", "trio"):
            seated.append("sun")     # hexa and trio center the Sun
        assert sorted(seated) == sorted(constants.WEEKDAY_BODIES), pointer


def test_slot_angles_sit_on_the_pointer_arms():
    for pointer, slots in constants.POINTER_WEEKDAY_SLOTS.items():
        if pointer == "aurora":
            # No arms exist — the single slot is pinned to the dial
            # bottom, above the Omega (owner spec 2026-07-12).
            assert slots == ((180.0, constants.WEEKDAY_BODIES),) or [
                angle for angle, _ in slots
            ] == [180.0]
            continue
        arm_step = 360.0 / constants.POINTER_POINTS[pointer]
        for angle, _ in slots:
            assert angle % arm_step == 0.0, (pointer, angle)


def test_octa_reserves_the_bottom_arm_for_the_info_slot():
    occupied = [angle for angle, _ in constants.POINTER_WEEKDAY_SLOTS["octa"]]
    assert constants.SOUTH_SLOT_ANGLE not in occupied


def test_south_slot_matrix():
    """Owner matrix (dual-Sunday round 2026-07-12): the Compass and
    the Seasons carry the slot in the CENTER (their 24h arm belongs to
    the Sunday pair) — weekday off frees the bottom, so it moves to
    24h; the Trinity and the Prism have NO room while the star is up;
    Aurora and the pointer-off pinned layouts keep the bottom rules;
    plus Aurora's images-only mode fallback."""
    import dataclasses

    from render.layers import (
        pinned_weekday_theta, south_slot_available, south_slot_centered,
        south_slot_theta, south_slot_view,
    )

    def skin(**kw):
        return dataclasses.replace(defaults.DEFAULT_SKIN, **kw)

    # Availability: octa/cross yes, trio/hexa NO while the star is up.
    assert south_slot_available(skin(pointer="octa"))
    assert south_slot_available(skin(pointer="cross", show_weekday=True))
    assert not south_slot_available(skin(pointer="trio", show_weekday=True))
    assert not south_slot_available(skin(pointer="hexa", show_weekday=True))
    assert not south_slot_available(skin(pointer="hexa", show_weekday=False))
    assert south_slot_available(skin(pointer="trio", show_pointer=False))
    assert south_slot_available(skin(pointer="aurora", show_weekday=True))
    assert not south_slot_available(
        skin(pointer="octa", show_octa_slot=False)
    )
    # Center vs bottom: weekday up -> center; weekday off -> the 24h
    # arm (rotating); pinned layouts never center.
    assert south_slot_centered(skin(pointer="octa"))
    assert south_slot_centered(skin(pointer="cross"))
    assert not south_slot_centered(skin(pointer="octa", show_weekday=False))
    assert not south_slot_centered(skin(pointer="octa", show_pointer=False))
    assert not south_slot_centered(skin(pointer="aurora"))
    assert south_slot_theta(
        skin(pointer="octa", show_weekday=False), 14.0
    ) == 194.0
    # Pointer element off + weekday still on -> the pair FLANKS the
    # bottom (owner extension); weekday off as well -> plain south.
    assert south_slot_theta(
        skin(pointer="hexa", show_pointer=False), 14.0
    ) == constants.AURORA_DUAL_SLOT_ANGLE
    assert south_slot_theta(
        skin(pointer="hexa", show_pointer=False, show_weekday=False), 14.0
    ) == 180.0
    # Aurora: south alone, flanking pair with the weekday on.
    lone = skin(pointer="aurora", show_weekday=False)
    both = skin(pointer="aurora", show_weekday=True, show_octa_slot=True)
    assert south_slot_theta(lone, 14.0) == 180.0
    assert south_slot_theta(both, 14.0) == constants.AURORA_DUAL_SLOT_ANGLE
    assert pinned_weekday_theta(both) == constants.AURORA_DUAL_WEEKDAY_ANGLE
    assert pinned_weekday_theta(
        skin(pointer="aurora", show_octa_slot=False)
    ) == 180.0
    # Aurora shows images only — plain and text modes coerce to logos.
    assert south_slot_view(
        skin(pointer="aurora", octa_slot="time")
    ) == ("zodiac", "logo")
    assert south_slot_view(
        skin(pointer="aurora", octa_slot="zodiac", info_slot_style="text")
    ) == ("zodiac", "logo")
    assert south_slot_view(
        skin(pointer="aurora", octa_slot="chinese", info_slot_style="text")
    ) == ("chinese", "colored")
    assert south_slot_view(
        skin(pointer="aurora", octa_slot="chinese", info_slot_style="gold")
    ) == ("chinese", "gold")
    assert south_slot_view(
        skin(pointer="octa", octa_slot="time")
    ) == ("time", None)
    assert south_slot_view(
        skin(pointer="octa", octa_slot="zodiac", info_slot_style="sign")
    ) == ("zodiac", "sign")


def test_dual_sunday_two_faces_on_compass_and_seasons(app, july_wednesday):
    """Owner corrections 2026-07-13: the SERVANT face is NOT
    Sunday-only — it stands at 24h all week like every other body
    (ghosted; opaque on Sunday) and speaks ITS OWN face text with its
    own name; the north sun speaks the RULER face; on the Seasons the
    Servant shares mercury's 180 seat by the standard priority; the
    Trinity/Prism single image carries BOTH plates in its legend.
    Every theme's dual art is ON DISK, colored variants too."""
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace
    from render.layers import (
        servant_holds_the_seat, south_slot_centered, sunday_dual_face,
    )

    # The art table is complete: all twelve themes + colored variants.
    for theme in constants.WEEKDAY_THEMES:
        rel = defaults.WEEKDAY_DUAL_FILES[theme]
        assert (defaults.WEEKDAY_ART_DIR / f"{rel}.png").exists(), theme
        assert theme in defaults.WEEKDAY_DUAL_NAMES
    for theme in constants.METAL_THEMES:
        # The colored dual is the SIBLING variant (owner restructure
        # 2026-07-14): the variant segment swaps to colored/.
        rel = defaults.WEEKDAY_DUAL_FILES[theme].replace(
            "/primary/", "/colored/"
        )
        assert (defaults.WEEKDAY_ART_DIR / f"{rel}.png").exists(), theme
    # ...and so are the SPLIT FACE TEXTS (owner: no identical text on
    # the two faces) — every article set's sun carries distinct
    # ruler/servant prose.
    import json as _json

    from config import paths
    data = _json.loads(
        (paths.database_dir() / "symbolism.json").read_text(encoding="utf-8")
    )
    for article_set in set(constants.WEEKDAY_THEME_ARTICLES.values()):
        faces = data["articles"][article_set]["sun"].get("faces")
        assert faces is not None, article_set
        assert set(faces) == {"ruler", "servant"}, article_set
        assert faces["ruler"] != faces["servant"], article_set

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 7, 12, 12, 0, tzinfo=tz)          # a Sunday
    day = build_day_context(
        now,
        astral.Observer(
            latitude=city["latitude"], longitude=city["longitude"]
        ),
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    for pointer in ("octa", "cross"):
        skin = apply_display_settings(
            defaults.DEFAULT_SKIN,
            replace(Settings(), pointer=pointer, solar_rotation=False),
        )
        assert skin.weekday_set.dual_asset is not None
        assert sunday_dual_face(skin)
        assert servant_holds_the_seat(skin, "sun"), pointer
        compositor = Compositor(skin, AssetCache())
        compositor.render_offscreen(360.0, 1.0, day, tick)
        orbit = 180.0 * skin.weekday_set.orbit_fraction
        south = compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
        north = compositor.tooltip_at(180.0, 180.0 - orbit, 360.0)
        # Each face speaks its OWN name and text (owner: no more
        # identical Ruler text on the Servant).
        assert south is not None and "Eclipsed Sun" in south, pointer
        assert north is not None and "Eclipsed Sun" not in north, pointer
        # The hover embeds the SCALED cache copy of the servant plate
        # (performance round 2026-07-13) — pin the exact resolved uri.
        from render.assets import scaled_variant_file

        eclipse_uri = scaled_variant_file(
            defaults.WEEKDAY_ART_DIR
            / f"{defaults.WEEKDAY_DUAL_FILES['planets']}.png",
            2 * defaults.ARTICLE_IMAGE_WIDTH_PX,
        ).as_uri()
        assert eclipse_uri in south and eclipse_uri not in north
    # The SERVANT stands as a ghost on ORDINARY days too (a Wednesday):
    # on the Compass the free 24h seat is his; on the Seasons mercury
    # is TODAY on Wednesday and keeps his own seat.
    wed_day, wed_tick = july_wednesday
    octa = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(Settings(), pointer="octa", solar_rotation=False),
    )
    assert servant_holds_the_seat(octa, "mercury")
    ghost = Compositor(octa, AssetCache())
    ghost.render_offscreen(360.0, 1.0, wed_day, wed_tick)
    orbit = 180.0 * octa.weekday_set.orbit_fraction
    tip = ghost.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert tip is not None and "Eclipsed Sun" in tip
    cross = apply_display_settings(
        defaults.DEFAULT_SKIN, replace(Settings(), pointer="cross")
    )
    assert not servant_holds_the_seat(cross, "mercury")   # Wednesday: his seat
    # On a Friday Sunday is nearer than Wednesday — the Servant wins.
    assert servant_holds_the_seat(cross, "venus")
    # The Prism keeps one image — but its legend carries BOTH plates.
    hexa = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(Settings(), pointer="hexa", solar_rotation=False),
    )
    assert not sunday_dual_face(hexa)
    prism = Compositor(hexa, AssetCache())
    prism.render_offscreen(360.0, 1.0, day, tick)
    center = prism.tooltip_at(180.0, 180.0, 360.0)
    assert center is not None and center.count("<img") == 2
    # center_only keeps the center for the body — no dual, slot at 24h.
    center_only = dataclasses.replace(
        octa,
        weekday_set=dataclasses.replace(
            octa.weekday_set, display_mode="center_only"
        ),
    )
    assert not sunday_dual_face(center_only)
    assert not south_slot_centered(center_only)


# --- Shared-slot priority (owner rule) --------------------------------------------


def test_shared_slot_shows_the_next_upcoming_day():
    """Owner's example, Wednesday: of the pairs {Mon|Sat}, {Thu|Sun},
    {Tue|Fri} the visible bodies are Sat, Thu, Fri — the smaller forward
    distance from today wins."""
    assert visible_occupant(("moon", "saturn"), "mercury") == "saturn"
    assert visible_occupant(("jupiter", "sun"), "mercury") == "jupiter"
    assert visible_occupant(("mars", "venus"), "mercury") == "venus"


def test_today_always_wins_its_shared_slot():
    assert visible_occupant(("jupiter", "sun"), "sun") == "sun"
    assert visible_occupant(("jupiter", "sun"), "jupiter") == "jupiter"
    assert visible_occupant(("moon", "saturn"), "saturn") == "saturn"


def test_today_slot_positions():
    assert today_slot_theta("hexa", "sun") is None       # center, not an arm
    assert today_slot_theta("hexa", "mercury") == 180.0
    assert today_slot_theta("cross", "sun") == 0.0       # shares the top arm
    assert today_slot_theta("cross", "mercury") == 180.0  # Wednesday alone at the bottom
    assert today_slot_theta("octa", "sun") == 0.0
    assert today_slot_theta("octa", "mercury") == 135.0


# --- Star geometry -----------------------------------------------------------------


def test_cross_arms_borrow_the_octa_shape():
    """Owner spec (cross.png): the cross is the octa star WITHOUT the
    four diagonal arms — slim diamonds with gaps, not a fat 4-star."""
    half_angles = constants.POINTER_ARM_HALF_ANGLE_DEG
    assert half_angles["cross"] == half_angles["octa"]
    for pointer in ("hexa", "octa"):
        assert half_angles[pointer] == 180.0 / constants.POINTER_POINTS[pointer]


# --- Palette presets (owner: 5 — hexa/octa paint+light, cross seasons) -------------


def test_palette_presets_cover_every_pointer_and_style():
    for pointer, arms in constants.POINTER_POINTS.items():
        for style in constants.PALETTE_STYLES:
            palette = defaults.PALETTE_PRESETS[(pointer, style)]
            assert len(palette) == arms, (pointer, style)


def test_cross_serves_one_seasons_palette_under_both_styles():
    assert (
        defaults.PALETTE_PRESETS[("cross", "paint")]
        == defaults.PALETTE_PRESETS[("cross", "light")]
    )


def test_palette_for_selects_the_skin_choice():
    paint = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa")
    light = dataclasses.replace(paint, palette_style="light")
    assert palette_for(paint) == defaults.PALETTE_PRESETS[("octa", "paint")]
    assert palette_for(light) == defaults.PALETTE_PRESETS[("octa", "light")]


# --- Aurora (owner spec 2026-07-12) -------------------------------------------------


def test_weekday_badge_gating_and_pointer_off_flank():
    """Owner 2026-07-12 (revised): the astrology badge lives under
    AURORA ONLY (the Prism variant was dropped — the 2-signs-per-
    diamond mapping is average-only); AND with the Pointer element OFF
    the South slot exists on EVERY mode, flanking the south-dwelling
    body Aurora-style on Prism/Seasons."""
    import dataclasses

    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace
    from render.layers import (
        pinned_weekday_theta, south_slot_available, south_slot_theta,
        weekday_pinned,
    )

    for pointer in ("hexa", "octa", "cross", "trio"):
        skin = apply_display_settings(
            defaults.DEFAULT_SKIN,
            replace(Settings(), pointer=pointer, weekday_slot="ascendant"),
        )
        assert skin.weekday_slot == "weekday", pointer   # bodies forced
        # ...but with the Pointer element OFF the pinned layout exists,
        # so the badge survives on every mode (owner 2026-07-12).
        pinned = apply_display_settings(
            defaults.DEFAULT_SKIN,
            replace(
                Settings(), pointer=pointer, weekday_slot="ascendant",
                show_pointer=False,
            ),
        )
        assert pinned.weekday_slot == "ascendant", pointer
    for mode in ("zodiac", "ascendant", "chinese"):
        aurora = apply_display_settings(
            defaults.DEFAULT_SKIN,
            replace(Settings(), pointer="aurora", weekday_slot=mode),
        )
        assert aurora.weekday_slot == mode
    # The Chinese badge carries its metal into the selective swap.
    from render.layers import weekday_badge

    class _Tick:
        ascendant_sign = "Virgo"

    class _Day:
        zodiac_name = "Cancer"
        chinese_name = "Fire Horse"

    import dataclasses as _dc

    gold_badge = weekday_badge(
        _dc.replace(
            defaults.DEFAULT_SKIN, pointer="aurora",
            weekday_slot="chinese", day_slot_style="gold",
        ),
        _Day, _Tick,
    )
    assert gold_badge == ("Horse", "chinese/primary", "gold")
    colored_badge = weekday_badge(
        _dc.replace(
            defaults.DEFAULT_SKIN, pointer="aurora",
            weekday_slot="chinese", day_slot_style="colored",
        ),
        _Day, _Tick,
    )
    assert colored_badge == ("Horse", "chinese/colored", None)
    asc_badge = weekday_badge(
        _dc.replace(
            defaults.DEFAULT_SKIN, pointer="aurora",
            weekday_slot="ascendant", day_slot_style="colored",
        ),
        _Day, _Tick,
    )
    assert asc_badge == ("Virgo", "astrology/colored", None)

    def skin(**kw):
        return dataclasses.replace(defaults.DEFAULT_SKIN, **kw)

    # Pointer element OFF -> UNIFORM pinned rule on every mode (owner
    # correction: no diamonds, no slot positions): with the weekday on
    # the pair flanks the bottom (body 3h, slot 21h); alone the slot
    # (or the body) stands straight south.
    for pointer in ("hexa", "cross", "trio", "octa"):
        off = skin(pointer=pointer, show_pointer=False, show_weekday=True)
        assert weekday_pinned(off), pointer
        assert south_slot_available(off), pointer
        assert south_slot_theta(off, 14.0) == constants.AURORA_DUAL_SLOT_ANGLE
        assert pinned_weekday_theta(off) == constants.AURORA_DUAL_WEEKDAY_ANGLE
        lone = skin(pointer=pointer, show_pointer=False, show_weekday=False)
        assert south_slot_theta(lone, 14.0) == constants.SOUTH_SLOT_ANGLE
    # The body alone (slot element off) pins straight south.
    body_only = skin(
        pointer="hexa", show_pointer=False, show_octa_slot=False,
    )
    assert pinned_weekday_theta(body_only) == constants.SOUTH_SLOT_ANGLE
    # With the star drawn nothing is pinned.
    assert not weekday_pinned(skin(pointer="hexa", show_pointer=True))


def test_ring_tick_hover_reads_all_three_wheels(july_wednesday):
    """Owner spec 2026-07-12: hovering the ring tick band answers with
    the angle on every wheel — the 24h time, the year-wheel date (with
    the season, and the event on an anchor day) and the moon-cycle
    reading (new at the top, exactly as the Moon marker rides)."""
    import math as m

    from core.year_wheel import instant_at_marker_angle, year_marker_angle

    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    band = 180.0 * (
        defaults.TICK_HOVER_INNER_FRACTION
        + defaults.TICK_HOVER_OUTER_FRACTION
    ) / 2
    top = compositor.tooltip_at(180.0, 180.0 - band, 360.0)     # theta 0
    # Formatting round 2026-07-12: bold labels, the exact dial degree
    # and the day-period word on the time line; blank rows between the
    # D/Y/M sections.
    assert "12:00" in top and "Time:" in top
    assert "Angle:" in top and "0.0°" in top
    assert "&nbsp;" in top                     # the section separators
    # The top of the year wheel IS the summer solstice anchor.
    assert "Summer Solstice" in top and "Summer" in top
    assert "Date:" in top and "Season:" in top
    assert "June" in top and "2026" in top
    # Moon wheel: new at the top — 0% illumination, day 0 of the cycle.
    assert "0.0%" in top and "New Moon" in top
    theta = 250.0                              # ((250-180)/15)h = 04:40
    rad = m.radians(theta)
    side = compositor.tooltip_at(
        180.0 + band * m.sin(rad), 180.0 - band * m.cos(rad), 360.0
    )
    assert "04:40" in side and "250.0°" in side
    assert "February" in side and "Winter" in side   # 250 deg on the year wheel
    assert "Waning Gibbous" in side                  # 250/360 of the moon cycle
    # Inverse golden: the ANGLE round-trips exactly (the December
    # solstice angle legitimately has two dates a year apart — the
    # inverse picks the span's earlier one, so compare angles).
    for when, name in day.season_events:
        angle = year_marker_angle(when, day.year_anchors)
        back = instant_at_marker_angle(day.year_anchors, angle)
        assert abs(
            year_marker_angle(back, day.year_anchors) - angle
        ) % 360.0 < 0.01, name
    # Southern mirror: the same angle un-mirrors +180.
    south = instant_at_marker_angle(day.year_anchors, 0.0, southern=True)
    north_bottom = instant_at_marker_angle(day.year_anchors, 180.0)
    assert south == north_bottom


def test_aurora_bands_spread_the_day_hues_evenly():
    """The five DAY hues split the actual sunrise-sunset arc into equal
    bands — ALL of them visible on the shortest and the longest day
    alike — dawn wears the palette's first hue (blue), dusk its last
    (brown); the weekday slot is pinned to the dial bottom and the
    pointer is always solar-rotated."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    import astral

    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace
    from core.clock_state import build_day_context
    from core import angles
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository
    from render.layers import aurora_bands, today_slot_theta

    palette = defaults.PALETTE_PRESETS[("aurora", "paint")]
    tz = ZoneInfo(defaults.DEFAULT_CITY["timezone"])
    observer = astral.Observer(
        latitude=defaults.DEFAULT_CITY["latitude"],
        longitude=defaults.DEFAULT_CITY["longitude"],
    )
    seasons = SeasonsRepository()
    moons = MoonPhaseRepository()
    for date in (datetime(2026, 6, 21, 12, 0, tzinfo=tz),      # longest day
                 datetime(2026, 12, 21, 12, 0, tzinfo=tz)):    # shortest day
        day = build_day_context(
            date, observer,
            seasons.year_anchors(date.year), moons.moon_window(date.year),
        )
        bands, solar_frame = aurora_bands(day.sun, palette, 0.55)
        assert solar_frame is False
        assert len(bands) == 7, date                 # dawn + 5 day + dusk
        assert bands[0][2] == palette[0]             # dawn blue
        assert bands[-1][2] == palette[-1]           # dusk brown
        # No separate twilight opacity under Aurora (owner: the color
        # carries the meaning) — the whole arc wears the day alpha.
        assert bands[0][3] == bands[-1][3] == 0.55
        day_bands = bands[1:-1]
        assert [hue for _, _, hue, _ in day_bands] == list(palette[1:-1])
        rise = angles.time_to_dial_angle(day.sun.sunrise)
        sets = angles.time_to_dial_angle(day.sun.sunset)
        span = (sets - rise) % 360.0
        widths = [end - start for start, end, _, alpha in day_bands]
        assert all(abs(w - span / 5) < 1e-9 for w in widths), date
        assert abs(day_bands[0][0] - rise) < 1e-9
        assert all(alpha == 0.55 for _, _, _, alpha in day_bands)
    # The weekday slot never rotates: pinned at the bottom, above Omega.
    for body in constants.WEEKDAY_BODIES:
        assert today_slot_theta("aurora", body) == 180.0
    # Aurora is ALWAYS solar-rotated, whatever the toggle says.
    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(Settings(), pointer="aurora", solar_rotation=False),
    )
    assert skin.solar_rotation is True
    assert skin.pointer == "aurora"


# --- Octa bottom slot ----------------------------------------------------------------


def test_bottom_slot_layer_stack_positions():
    """Owner dual-Sunday round 2026-07-12: on the Compass/Seasons the
    info slot is CENTERED and rides ABOVE the hands (the center
    occludes them — his accepted cost); in the pinned layouts it sits
    at the bottom BELOW the hands (the old bug report: the seconds
    hand passed behind the zodiac art); the Prism has none at all."""
    octa = _build_layers(dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa"))
    hexa = _build_layers(defaults.DEFAULT_SKIN)
    assert any(isinstance(layer, BottomSlotLayer) for layer in octa)
    assert not any(isinstance(layer, BottomSlotLayer) for layer in hexa)
    slot_index = next(
        i for i, layer in enumerate(octa) if isinstance(layer, BottomSlotLayer)
    )
    last_hand = max(
        i for i, layer in enumerate(octa) if isinstance(layer, HandLayer)
    )
    assert slot_index > last_hand            # centered -> above the hands
    pinned = _build_layers(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", show_pointer=False,
        )
    )
    slot_index = next(
        i for i, layer in enumerate(pinned) if isinstance(layer, BottomSlotLayer)
    )
    first_hand = min(
        i for i, layer in enumerate(pinned) if isinstance(layer, HandLayer)
    )
    assert slot_index < first_hand           # bottom -> below the hands


@pytest.mark.parametrize("mode", constants.OCTA_SLOT_MODES)
def test_octa_slot_modes_render(july_wednesday, mode):
    day, tick = july_wednesday
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa", octa_slot=mode)
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200        # painted, no crash


@pytest.mark.parametrize("style", constants.ZODIAC_SLOT_STYLES)
def test_zodiac_slot_styles_render(july_wednesday, style):
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="octa",
        octa_slot="zodiac", info_slot_style=style,
    )
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200


@pytest.mark.parametrize("style", constants.CHINESE_SLOT_STYLES)
def test_chinese_slot_styles_render(july_wednesday, style):
    """Every Chinese dropdown style paints (owner 2026-07-12): text in
    two lines, colored from its own folder, gold/silver through the
    selective swap, bronze as drawn."""
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="octa",
        octa_slot="chinese", info_slot_style=style,
    )
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200


def test_day_slot_text_modes_need_the_pointer_off(july_wednesday):
    """Owner 2026-07-12: Time/Date/Day length join the DAY slot — but
    like the badges they are gray in Pointer mode, and Aurora keeps
    the day slot images-only, so they draw only with the Pointer
    element OFF (at the pinned spot, answering no hover, exactly like
    the info slot's text modes)."""
    from PySide6.QtCore import QPointF

    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace

    for mode in ("time", "date", "day_length"):
        drawn = apply_display_settings(
            defaults.DEFAULT_SKIN,
            replace(Settings(), pointer="hexa", weekday_slot=mode),
        )
        assert drawn.weekday_slot == "weekday"      # star up: bodies rule
        aurora = apply_display_settings(
            defaults.DEFAULT_SKIN,
            replace(Settings(), pointer="aurora", weekday_slot=mode),
        )
        assert aurora.weekday_slot == "weekday"     # aurora: images only
        pinned = apply_display_settings(
            defaults.DEFAULT_SKIN,
            replace(
                Settings(), pointer="octa", weekday_slot=mode,
                show_pointer=False,
            ),
        )
        assert pinned.weekday_slot == mode
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_pointer=False, weekday_slot="time", show_octa_slot=False,
        ),
        AssetCache(),
    )
    image = compositor.render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(180, 8).alpha() > 200        # painted, no crash
    # The pinned spot answers NO hover in a text mode — no body, no badge.
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    assert compositor._element_at(
        QPointF(0.0, orbit), 180.0, 0.0, "mercury"
    ) is None


def test_info_slot_weekday_wears_its_theme_metal(july_wednesday):
    """Owner 2026-07-12 (identical Weekday submenus): the info slot's
    second body carries ITS OWN theme's metal — resolved from
    theme_metals in apply_display_settings, run through the selective
    swap (or the colored/ art) on the info body alone."""
    from app.controller import apply_display_settings
    from app.settings_store import Settings, replace

    skin = apply_display_settings(
        defaults.DEFAULT_SKIN,
        replace(
            Settings(), pointer="octa", octa_slot="weekday",
            info_slot_theme="greek", theme_metals={"greek": "gold"},
        ),
    )
    assert skin.info_slot_metal == "gold"
    assert skin.weekday_theme == "planets"       # the day slot untouched
    day, tick = july_wednesday
    image = Compositor(skin, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    assert image.pixelColor(180, 8).alpha() > 200


# --- Render smoke -------------------------------------------------------------------


@pytest.mark.parametrize("pointer", ["cross", "octa", "trio"])
def test_pointer_variants_render(july_wednesday, pointer):
    day, tick = july_wednesday
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, pointer=pointer)
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    assert image.pixelColor(2, 2).alpha() == 0           # corners stay transparent
    assert image.pixelColor(180, 8).alpha() > 200        # ring painted
    assert image.pixelColor(333, 180).alpha() > 200      # disc touches the ring


def test_trio_centers_the_sun_and_pairs_the_week():
    """Owner-approved trio pairing: Faith 12h = Jupiter+Saturn, Love 20h
    = Venus+Mars, Hope 4h = Moon+Mercury; Sunday's Sun in the center."""
    from render.layers import today_slot_theta

    assert today_slot_theta("trio", "sun") is None
    slots = dict(constants.POINTER_WEEKDAY_SLOTS["trio"])
    assert slots[0.0] == ("jupiter", "saturn")
    assert slots[120.0] == ("venus", "mars")
    assert slots[240.0] == ("moon", "mercury")


def test_trio_aura_thirds_center_on_the_arms(july_wednesday):
    """The trio's hues center on the arms like every pointer (owner
    correction 2026-07-10): upright, yellow spans 8h-16h, red 16h-24h,
    blue 0h-8h. Probed at 14h (yellow), 18h (red) and 6h (blue), away
    from the diamonds (arms sit at 0/120/240 deg)."""
    day, tick = july_wednesday
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN, pointer="trio", solar_rotation=False,
        show_weekday=False, show_earth=False, show_moon=False,
    )
    image = Compositor(skin, AssetCache()).render_offscreen(360.0, 1.0, day, tick)
    at_14h = image.pixelColor(234, 87)          # dial 30 deg, radius 0.6R
    assert at_14h.red() > at_14h.blue() + 30             # Faith yellow
    at_18h = image.pixelColor(288, 180)         # dial 90 deg
    assert at_18h.red() > at_18h.green() + 30            # Love red
    assert at_18h.red() > at_18h.blue() + 30
    at_6h = image.pixelColor(72, 180)           # dial 270 deg
    assert at_6h.blue() > at_6h.red() + 30               # Hope blue


def test_hover_rework_moon_and_earth_formats(july_wednesday):
    """Owner hover rework: raised ordinal suffixes, illumination to one
    decimal, the moonrise-moonset span and the season row (Belgrade,
    8 July 2026 = 189th day, 18th day of a 94-day summer)."""
    day, tick = july_wednesday
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    moon = compositor._moon_text()
    # Formatting round 2026-07-13: the phase NAME is the title — no
    # "Phase:" label anywhere, the name rides the bigger bold line.
    assert "Phase:</b>" not in moon
    assert "font-weight:bold" in moon
    assert "Waning" in moon or "Waxing" in moon or "Moon" in moon
    assert "Illumination:</b> 42.8%" in moon   # one decimal (owner spec)
    assert "of 29.53" in moon and "&nbsp;" in moon
    # 8 Jul 2026 is a SKIP day in Belgrade — the moon sets at 13:53 but
    # does not rise (rises again just after midnight on the 9th); the
    # hover shows the side that exists.
    assert "Moonset:</b> 13:53" in moon
    earth = compositor._earth_text()
    assert "Date:</b> 8<sup>th</sup> July 2026" in earth
    assert "Season:</b>" in earth and "Sign:</b>" in earth
    assert "189<sup>th</sup> Day - 28<sup>th</sup> Week" in earth
    assert "Summer 18<sup>th</sup> of 94 Days" in earth
    assert "Cancer (21<sup>st</sup> June - 21<sup>st</sup> July)" in earth


def test_lunation_before_the_years_first_new_moon(app, july_wednesday):
    """Owner correction 2026-07-12: the year's 1st Moon = the first New
    Moon on/after Jan 1, so the early-January days still riding the
    December lunation read as the PREVIOUS year's LAST — 2025 began 12
    lunations (Dec 20 was its 12th), and 5 Jan 2026 is inside it. Only
    roughly one year in three reaches 13."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = datetime(2026, 1, 5, 12, 0, tzinfo=tz)
    day = build_day_context(
        now,
        astral.Observer(
            latitude=city["latitude"], longitude=city["longitude"]
        ),
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, day, tick)
    january = compositor._lunation_ordinal()
    assert "12" in january and "2025" in january
    # ...and a mid-year date counts within its own year (first 2026
    # New Moon 18 Jan; by 8 July SIX lunations have started — July's
    # own new moon has not fallen yet).
    july_day, july_tick = july_wednesday
    compositor.render_offscreen(360.0, 1.0, july_day, july_tick)
    july = compositor._lunation_ordinal()
    assert "6" in july and "2026" in july


def test_lunation_ordinal_reads_the_ring_side(app):
    """Owner logic 2026-07-13 (his 11 July screenshot): with the Moon
    on the dial's LEFT — second half of its cycle — the ring past 12h
    already belongs to the NEXT moon (hovering right of the top must
    read the 7th, not the running 6th); and December wraps into the
    new year's 1st."""
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )

    def ordinals(now):
        day = build_day_context(
            now, observer,
            SeasonsRepository().year_anchors(now.year),
            MoonPhaseRepository().moon_window(now.year),
        )
        tick = build_tick_state(now, day)
        assert tick.moon_fraction > 0.5     # premise: Moon on the LEFT
        compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
        compositor.render_offscreen(360.0, 1.0, day, tick)
        return (
            compositor._lunation_ordinal(),
            compositor._lunation_ordinal(next_cycle=True),
        )

    current, following = ordinals(datetime(2026, 7, 11, 12, 0, tzinfo=tz))
    assert "6" in current and "2026" in current
    assert "7" in following and "2026" in following
    december, january = ordinals(datetime(2026, 12, 28, 12, 0, tzinfo=tz))
    assert "12" in december and "2026" in december
    assert "1<sup>st</sup>" in january and "2027" in january


def test_upright_mode_disarms_the_rotation(july_wednesday):
    """With solar rotation OFF the Star/Aura/Umbra stand upright — the
    render differs from the solar one (Belgrade July tilts ~+14 deg) and
    the today-slot hover sits at the exact unrotated angle."""
    day, tick = july_wednesday
    solar = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    upright_skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    upright_compositor = Compositor(upright_skin, AssetCache())
    upright = upright_compositor.render_offscreen(360.0, 1.0, day, tick)
    assert solar != upright
    # Wednesday=mercury sits at exactly 180 deg when upright: hover at the
    # unrotated slot center must hit it (orbit 0.38 * 180 px below center).
    # Hover rework: the ACTIVE body leads with the date and carries its
    # JUSTIFIED article (base + the active combination's paragraph).
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = upright_compositor.tooltip_at(180.0, 180.0 + orbit, 360.0)
    assert "Wednesday, 8<sup>th</sup> July 2026" in tip
    assert "align='justify'" in tip
    assert "Mercury" in tip                    # the planets article text
    assert "align='center'" in tip           # hover text is centered (owner spec)


def _day_and_tick(latitude, longitude, tz_name):
    from core.clock_state import build_day_context, build_tick_state
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    tz = ZoneInfo(tz_name)
    now = datetime(2026, 7, 8, 12, 0, tzinfo=tz)
    day = build_day_context(
        now,
        astral.Observer(latitude=latitude, longitude=longitude),
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    return day, build_tick_state(now, day)


def test_southern_hemisphere_mirrors_the_arm_anchors(app):
    """Owner bug 2026-07-12 (Sydney screenshots): the year wheel runs
    MIRRORED in the south, so the TOP cardinal arm must read the
    DECEMBER solstice — their Summer Solstice — and the diagonals the
    mirrored quarters; the north keeps June at the top."""
    import dataclasses

    sydney, tick = _day_and_tick(-33.8688, 151.2093, "Australia/Sydney")
    upright = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", solar_rotation=False
        ),
        AssetCache(),
    )
    upright.render_offscreen(360.0, 1.0, sydney, tick)
    top = upright.tooltip_at(180.0, 72.0, 360.0)
    assert "Summer Solstice" in top                  # the south's own name
    assert "December" in top                         # at the DECEMBER instant
    bottom = upright.tooltip_at(180.0, 288.0, 360.0)
    assert "Winter Solstice" in bottom and "June" in bottom
    diagonal = upright.tooltip_at(256.0, 104.0, 360.0)    # 45 deg arm
    assert "December" in diagonal or "January" in diagonal or "February" in diagonal


def test_southern_hemisphere_mirrors_the_diamond_signs(app):
    """Owner spec 2026-07-12: in the south the Earth passes the TOP
    diamond in December — its hover must name Sagittarius/Capricorn
    (with their universal dates) and highlight in the arm it actually
    occupies; the north keeps Gemini/Cancer at the top."""
    import dataclasses

    sydney, tick = _day_and_tick(-33.8688, 151.2093, "Australia/Sydney")
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        AssetCache(),
    )
    upright.render_offscreen(360.0, 1.0, sydney, tick)
    top = upright.tooltip_at(180.0, 72.0, 360.0)          # top diamond
    assert "Sagittarius" in top and "Capricorn" in top
    assert "December" in top                              # universal dates
    assert "Gemini" not in top


def test_climate_zones_name_the_events_and_seasons(app):
    """Owner decision: the south flips the seasonal event names (their
    Summer Solstice is the December one), the tropics use the neutral
    month names and read their WET/DRY halves instead of seasons."""
    sydney, tick = _day_and_tick(-33.8688, 151.2093, "Australia/Sydney")
    assert sydney.zone == "south"
    names = [name for _, name in sydney.season_events]
    assert "Winter Solstice" in names and "Summer Solstice" in names
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, sydney, tick)
    earth = compositor._earth_text()
    assert "Winter 18<sup>th</sup> of 94 Days" in earth   # July = their winter

    singapore, tick = _day_and_tick(1.3521, 103.8198, "Asia/Singapore")
    assert singapore.zone == "tropics"
    names = [name for _, name in singapore.season_events]
    assert "June Solstice" in names and "December Solstice" in names
    compositor = Compositor(defaults.DEFAULT_SKIN, AssetCache())
    compositor.render_offscreen(360.0, 1.0, singapore, tick)
    earth = compositor._earth_text()
    assert "Wet season 111<sup>th</sup> of 186 Days" in earth


def test_trio_arm_hover_carries_the_virtue_article(july_wednesday):
    """The Trinity arm hover: theme, third, pair — then the virtue's
    article (owner request): Faith's speaks of the vertical line."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="trio", solar_rotation=False,
            show_weekday=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    tip = compositor.tooltip_at(180.0, 72.0, 360.0)       # top arm = Faith
    assert "Faith" in tip and "08:00 - 16:00" in tip
    assert "Thursday" in tip and "Saturday" in tip
    assert "align='justify'" in tip and "vertical line" in tip


def test_day_and_night_period_hovers(july_wednesday):
    """Hover rework 5 & 6 + formatting round 2026-07-12: the sunlit arc
    answers with a bold Day title, labeled sun span and the twilight
    span under its With Twilight title — plus a mini Earth of the
    active region (day art on the day side, night art on the night
    side); the dark of the wheel mirrors it as Night / Complete Dark."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_weekday=False, show_earth=False, show_moon=False,
            show_pointer=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    at_day = compositor.tooltip_at(234.0, 87.0, 360.0)     # dial 30 deg = 14h
    assert "<b>Day</b> 15h" in at_day
    assert "Sunrise:" in at_day and "Dusk:" in at_day
    assert "With Twilight" in at_day
    assert "<img" in at_day and "_day" in at_day           # the region's day face
    at_night = compositor.tooltip_at(162.0, 285.0, 360.0)  # near the bottom
    assert "<b>Night</b> 8h" in at_night
    assert "Sunset:" in at_night and "Dawn:" in at_night
    assert "Complete Dark" in at_night
    assert "<img" in at_night and "_night" in at_night


def test_twilight_band_format_and_tick_priority(july_wednesday):
    """Owner formatting round 2026-07-12: the twilight hover carries a
    bold Morning/Evening Twilight title, the labeled bounds and the
    band's span in minutes AND dial degrees (15°/h); where the ring
    tick band overlaps the twilight wedge (0.86–0.90 R), the CIRCLE
    outranks the wedge."""
    from core import angles

    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_weekday=False, show_earth=False, show_moon=False,
            show_pointer=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    sun = day.sun
    theta = math.radians(
        (angles.time_to_dial_angle(sun.dawn)
         + angles.time_to_dial_angle(sun.sunrise)) / 2
    )

    def probe(fraction):
        return compositor.tooltip_at(
            180.0 + 180.0 * fraction * math.sin(theta),
            180.0 - 180.0 * fraction * math.cos(theta),
            360.0,
        )

    below_band = probe((defaults.TICK_HOVER_INNER_FRACTION - 0.02))
    assert "Morning Twilight" in below_band
    assert "Dawn:" in below_band and "Sunrise:" in below_band
    span = round((sun.sunrise - sun.dawn).total_seconds() / 60)
    assert f"{span} min - {span / 4:.2f}°" in below_band
    # The band names its astronomical definition (owner 2026-07-12).
    assert "Civil twilight" in below_band
    # Same wedge angle, but INSIDE the tick annulus (which overlaps the
    # aura up to 0.90 R): the circle answers, not the wedge.
    aura = compositor._skin.background.aura_radius_fraction
    in_band = probe((defaults.TICK_HOVER_INNER_FRACTION + aura) / 2)
    assert "Time:" in in_band and "Date:" in in_band


def test_arm_hover_only_inside_the_diamond(july_wednesday):
    """Owner bug report: the diamond hover must not swallow the wheel —
    BETWEEN the arms the Aura/Umbra day-night hover answers; the arm
    text appears only inside the drawn diamond polygon."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, solar_rotation=False,
            show_weekday=False, show_earth=False, show_moon=False,
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    on_arm = compositor.tooltip_at(180.0, 72.0, 360.0)     # top arm axis, 0.6R
    assert "Gemini" in on_arm                              # diamond answers
    # Dial 30 deg (between the 0 and 60 arms) at 0.7R: the gap — the
    # day hover answers there (14h is deep in the July daylight arc).
    between = compositor.tooltip_at(243.0, 70.9, 360.0)
    assert between is not None and "<b>Day</b> 15h" in between
    assert "Gemini" not in between and "Leo" not in between


def test_ghost_body_hover_shows_the_article_alone(july_wednesday):
    """Hover rework: ghost (non-current) bodies are hover targets too,
    showing their article WITHOUT the date line (owner spec) — probed on
    Jupiter's top slot on a Wednesday."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False), AssetCache()
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    orbit = 180.0 * defaults.DEFAULT_SKIN.weekday_set.orbit_fraction
    tip = upright.tooltip_at(180.0, 180.0 - orbit, 360.0)   # top slot = jupiter
    assert tip is not None and "align='justify'" in tip
    assert "Jupiter" in tip                    # its planets article
    assert "July 2026" not in tip              # no date line on ghosts


# --- Arm hovers (owner spec) -----------------------------------------------------------


def test_hexa_arm_hover_names_its_two_signs(july_wednesday):
    """Each hexa diamond spans exactly TWO zodiac signs (the owner's
    proposed list had Aquarius doubled on the bottom arm — corrected:
    bottom = Sagittarius + Capricorn), side by side as two COLUMNS
    (owner 2026-07-13): bold title with the date span, no glyph.
    Upright → no asterisk."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False), AssetCache()
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    top = upright.tooltip_at(180.0, 72.0, 360.0)          # top diamond, 0.6R up
    assert "Gemini" in top and "Cancer" in top and "*" not in top
    assert top.count("<td width=") == 2                   # two sign columns
    assert "♊" not in top and "♋" not in top              # titles wear no glyph
    assert "May" in top and "Jun" in top                  # each with its dates
    bottom = upright.tooltip_at(180.0, 288.0, 360.0)      # below mercury's slot
    assert "Sagittarius" in bottom and "Capricorn" in bottom
    assert "Nov" in bottom and "Dec" in bottom


def test_octa_arm_hovers_events_and_seasons(july_wednesday):
    """Octa cardinals give the exact event instant; diagonals describe
    their season with dates, duration and the middle date. Solar
    rotation ON adds the imprecision asterisk."""
    day, tick = july_wednesday
    upright = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN, pointer="octa", solar_rotation=False
        ),
        AssetCache(),
    )
    upright.render_offscreen(360.0, 1.0, day, tick)
    cardinal = upright.tooltip_at(180.0, 72.0, 360.0)     # top arm
    assert "Summer Solstice" in cardinal
    assert "2026" in cardinal and ":" in cardinal         # exact date + minutes
    assert "*" not in cardinal
    assert "h " in cardinal and "min" in cardinal         # day length line
    diagonal = upright.tooltip_at(256.0, 104.0, 360.0)    # 45 deg arm, 0.6R
    assert "Summer" in diagonal and "Days)" in diagonal and "Heart" in diagonal
    assert "<sup>" in diagonal                            # raised ordinals
    solar = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, pointer="octa"), AssetCache()
    )
    solar.render_offscreen(360.0, 1.0, day, tick)
    rotation = day.star_rotation
    theta = math.radians(45.0 + rotation)
    tilted = solar.tooltip_at(
        180.0 + 108.0 * math.sin(theta), 180.0 - 108.0 * math.cos(theta), 360.0
    )
    assert tilted is not None and "*" in tilted


def test_chinese_slot_hover(july_wednesday):
    """The info slot lives in the CENTER on the Compass (owner
    dual-Sunday round 2026-07-12) — the hover answers at (0,0)."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(
            defaults.DEFAULT_SKIN,
            pointer="octa",
            solar_rotation=False,
            octa_slot="chinese",
            info_slot_style="text",
        ),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    tip = compositor.tooltip_at(180.0, 180.0, 360.0)      # dial center
    assert "Fire Horse" in tip and "2026" in tip and "2027" in tip
    assert "<br/>" in tip                     # name / span on separate lines


def test_twilight_band_beats_the_arm_hover(july_wednesday):
    """Owner: dawn/dusk info must never be shadowed by the star-arm
    hovers — the band keeps priority inside the star region."""
    day, tick = july_wednesday
    compositor = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False),
        AssetCache(),
    )
    compositor.render_offscreen(360.0, 1.0, day, tick)
    # Mid-dusk angle (sunset 20:25 → dusk 21:02), probe at 0.6R.
    sunset_angle = (
        (day.sun.sunset.hour * 3600 + day.sun.sunset.minute * 60) / 86400 * 360 + 180
    ) % 360
    dusk_angle = (
        (day.sun.dusk.hour * 3600 + day.sun.dusk.minute * 60) / 86400 * 360 + 180
    ) % 360
    theta = math.radians((sunset_angle + dusk_angle) / 2)
    tip = compositor.tooltip_at(
        180.0 + 108.0 * math.sin(theta), 180.0 - 108.0 * math.cos(theta), 360.0
    )
    assert tip is not None and "Sunset" in tip and "Dusk" in tip


# --- Umbra ----------------------------------------------------------------------------


def test_umbra_forms_structure():
    """Sectioned forms (owner spec): fine 30 sections/16 shades (his
    measured art), coarse 24/13 — single lightest/darkest + mirror
    pairs; the gradient form has no sections at all."""
    assert constants.UMBRA_SECTION_COUNTS == {"fine": 30, "coarse": 24}
    for form, sections in constants.UMBRA_SECTION_COUNTS.items():
        shades = sections // 2 + 1
        assert 1 + 2 * (shades - 2) + 1 == sections, form
    assert "gradient" in constants.UMBRA_FORMS
    assert "gradient" not in constants.UMBRA_SECTION_COUNTS


def test_umbra_ladders_hit_the_owner_values():
    """full = endpoint-inclusive over 0..255 (16 shades -> step 17);
    half = bin centers of the middle half 64..192 (16 -> 188..68 step 8,
    every value + its mirror = 256)."""
    full16 = umbra_ladder(16, "full")
    assert full16 == tuple(255 - 17 * k for k in range(16))
    half16 = umbra_ladder(16, "half")
    assert half16 == tuple(188 - 8 * k for k in range(16))
    assert all(a + b == 256 for a, b in zip(half16, reversed(half16)))
    # Owner spec: light = the bright half (128-255), dark = the dark
    # half (0-127) — bin centers, exact step 8 like "half".
    light16 = umbra_ladder(16, "light")
    assert light16 == tuple(252 - 8 * k for k in range(16))
    assert light16[-1] == 132 and all(0 <= v <= 255 for v in light16)
    dark16 = umbra_ladder(16, "dark")
    assert dark16 == tuple(124 - 8 * k for k in range(16))
    assert dark16[-1] == 4
    full13 = umbra_ladder(13, "full")
    assert full13[0] == 255 and full13[-1] == 0 and full13[6] == 128
    half13 = umbra_ladder(13, "half")
    assert half13[0] == 187 and half13[-1] == 69 and half13[6] == 128
    for ladder in (full16, half16, full13, half13):
        assert list(ladder) == sorted(ladder, reverse=True)
        assert len(set(ladder)) == len(ladder)


def test_event_glow_is_visible_even_over_the_yellow_wedge(app):
    """Owner report: no glow on the summer solstice. The solstice Earth
    always sits in the bright yellow wedge — the halo must remain
    visible there (white core). A/B: the same moment with and without
    the event window must differ around the marker."""
    import dataclasses as dc

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    solstice_noon = datetime(2026, 6, 21, 12, 0, tzinfo=tz)
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        solstice_noon,
        observer,
        SeasonsRepository().year_anchors(2026),
        MoonPhaseRepository().moon_window(2026),
    )
    glowing = build_tick_state(solstice_noon, day)
    assert glowing.season_event == "Summer Solstice"
    # Clear BOTH events: on this date the moon's first quarter is also
    # within its window and its halo would contaminate the comparison.
    quiet = dc.replace(glowing, season_event=None, moon_event=None)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    with_glow = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, glowing
    )
    without = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quiet
    )
    # Upright + solstice noon: the Earth rides at the dial top, orbit
    # 0.75R. Probe DIAGONALLY below-right of the marker: inside the 2x
    # halo, outside the disc, off the noon hand shafts on the vertical
    # and BELOW the marker's date-text line (which renders as wide tofu
    # boxes under the offscreen platform and would mask the comparison).
    # The white core lifts the blue channel over the blue-free yellow.
    marker_y = 270 - round(270 * defaults.DEFAULT_SKIN.year_marker.orbit_fraction)
    lit = with_glow.pixelColor(300, marker_y + 30)
    plain = without.pixelColor(300, marker_y + 30)
    assert lit.blue() - plain.blue() >= 8


def test_moon_event_glow_renders(app):
    """Owner report: the moon glow "doesn't work" — pin that the halo
    really draws at a principal instant (it only shows within ±6 h of
    one; his Time Travel likely landed outside a window)."""
    import dataclasses as dc

    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    seasons = SeasonsRepository().year_anchors(2026)
    window = MoonPhaseRepository().moon_window(2026)
    reference = datetime(2026, 7, 7, 12, 0, tzinfo=tz)
    scout = build_day_context(reference, observer, seasons, window)
    instant, name = min(
        scout.moon_events, key=lambda event: abs(event[0] - reference)
    )
    local = instant.astimezone(tz)
    day = build_day_context(local, observer, seasons, window)
    glowing = build_tick_state(local, day)
    assert glowing.moon_event == name
    quiet = dc.replace(glowing, moon_event=None, season_event=None)
    skin = dataclasses.replace(defaults.DEFAULT_SKIN, solar_rotation=False)
    with_glow = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, glowing
    )
    without = Compositor(skin, AssetCache()).render_offscreen(
        540.0, 1.0, day, quiet
    )
    # At the instant the moon sits exactly on its cycle angle; probe
    # 30 px above the marker center — inside the 2x halo, off the disc.
    moon_angle = math.radians(glowing.moon_fraction * 360.0)
    orbit = 270 * defaults.DEFAULT_SKIN.year_marker.moon_orbit_fraction
    moon_x = 270 + orbit * math.sin(moon_angle)
    moon_y = 270 - orbit * math.cos(moon_angle)
    lit = with_glow.pixelColor(round(moon_x), round(moon_y) - 30)
    plain = without.pixelColor(round(moon_x), round(moon_y) - 30)
    assert (
        lit.red() - plain.red() >= 8
        or lit.green() - plain.green() >= 8
        or lit.blue() - plain.blue() >= 8
    )


def test_half_contrast_renders_a_gentler_night(july_wednesday):
    """The bottom of the dial (solar midnight, no hue overlay in July) is
    near-black on full contrast and clearly lifted on half."""
    day, tick = july_wednesday
    full = Compositor(defaults.DEFAULT_SKIN, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    half_skin = dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="half")
    half = Compositor(half_skin, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    # 90 px below center: inside the darkest sections (plus the star's
    # slight solar rotation), away from body slots and diamond borders.
    full_pixel = full.pixelColor(180, 270)
    half_pixel = half.pixelColor(180, 270)
    assert full_pixel.alpha() > 200 and half_pixel.alpha() > 200
    assert full_pixel.red() < 50
    assert half_pixel.red() >= 55
    # Light contrast lifts the night far higher (window 128-255); dark
    # keeps it near-black (window 0-127).
    light = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="light"),
        AssetCache(),
    ).render_offscreen(360.0, 1.0, day, tick)
    dark = Compositor(
        dataclasses.replace(defaults.DEFAULT_SKIN, umbra_contrast="dark"),
        AssetCache(),
    ).render_offscreen(360.0, 1.0, day, tick)
    assert light.pixelColor(180, 270).red() >= 120
    assert dark.pixelColor(180, 270).red() < 50


@pytest.mark.parametrize("form", ["coarse", "gradient"])
def test_umbra_forms_render(july_wednesday, form):
    day, tick = july_wednesday
    upright = dataclasses.replace(
        defaults.DEFAULT_SKIN, umbra_form=form, solar_rotation=False
    )
    image = Compositor(upright, AssetCache()).render_offscreen(
        360.0, 1.0, day, tick
    )
    assert image.pixelColor(180, 8).alpha() > 200
    if form == "gradient":
        # Upright: lightest straight up, darkest straight down; the
        # sweep must be mirror-symmetric. Probes at 0.62R: top/bottom on
        # the vertical, the mirror pair at dial angles 150/210 deg —
        # night side in July, so pure Umbra with no Aura wedge over it.
        top = image.pixelColor(180, 68).red()
        bottom = image.pixelColor(180, 292).red()
        night_right = image.pixelColor(236, 277).red()
        night_left = image.pixelColor(124, 277).red()
        assert bottom < 40 < top                 # dark bottom, light top...
        assert abs(night_left - night_right) <= 2    # ...mirrored sides
