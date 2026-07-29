"""The Calendar pointer (owner 2026-07-16, CANON §The Dozen): the two
wheels' palettes, the Almanac's own real-calendar year mapping (one tick
≈ one day), the Earth day-arrow, the pinned slot layout, and the
no-solar-rotation of the wedges. The lit-wedge feature it once carried
is DELETED (owner decree 2026-07-29) — its grave is guarded by the
`test_lit_wedge_*` regressions below."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import dataclasses
import json
import math
from datetime import date, datetime
from zoneinfo import ZoneInfo

import astral
import pytest
from PySide6.QtWidgets import QApplication

from config import constants, defaults, palette
from core.clock_state import build_day_context, build_tick_state
from core.year_wheel import almanac_marker_angle, almanac_month_index
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor
from render.layers import (
    calendar_day_arrow,
    calendar_mount_angle,
    calendar_mount_current_index,
    calendar_mount_entries,
    calendar_mount_mark_height,
    calendar_mount_wheel,
    calendar_wedge_bounds,
    calendar_wheel,
    chinese_mount_dimmed_index,
    dial_point,
    slot_layout,
    slot_seat_rotation,
    weekday_classic_slot,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _day_tick(app, when):
    city = defaults.DEFAULT_CITY
    tz = ZoneInfo(city["timezone"])
    now = when.replace(tzinfo=tz)
    observer = astral.Observer(
        latitude=city["latitude"], longitude=city["longitude"]
    )
    day = build_day_context(
        now, observer,
        SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    return day, build_tick_state(now, day)


def _calendar_skin(**kw):
    return dataclasses.replace(defaults.DEFAULT_SKIN, pointer="calendar", **kw)


# --- Palettes --------------------------------------------------------------------


def test_calendar_palettes_pin_the_two_wheels():
    """The twelve hues of each wheel, clockwise from the top wedge —
    Zodiac (paint) opens on Cancer, Almanac (light) on June."""
    assert palette.PALETTE_PRESETS[("calendar", "primary")] == (
        "#40FF00", "#BFFF00", "#FFBF00", "#FF4000", "#FF0040", "#FF00C0",
        "#BF00FF", "#4000FF", "#0040FF", "#00BFFF", "#00FFBF", "#00FF40",
    )
    assert palette.PALETTE_PRESETS[("calendar", "secondary")] == (
        "#00FF00", "#80FF00", "#FFFF00", "#FFBF00", "#FF0000", "#FF0080",
        "#FF00FF", "#8000FF", "#0000FF", "#0080FF", "#00FFFF", "#00FF80",
    )
    # Both wheels carry exactly twelve hues (the palette-length invariant).
    for style in ("primary", "secondary"):
        assert len(palette.PALETTE_PRESETS[("calendar", style)]) == 12


def test_calendar_wheel_follows_the_palette_style():
    assert calendar_wheel(_calendar_skin(palette_style="primary")) == "zodiac"
    assert calendar_wheel(_calendar_skin(palette_style="secondary")) == "almanac"


def test_wedge_bounds_place_the_top_wedge():
    """Zodiac boundaries sit ON the axes (top wedge starts at 0°);
    Almanac wedges are CENTERED on them (top wedge centered on 0°)."""
    zodiac = calendar_wedge_bounds("zodiac")
    assert zodiac[0] == (0.0, 30.0)
    assert len(zodiac) == 12 and zodiac[-1] == (330.0, 360.0)
    almanac = calendar_wedge_bounds("almanac")
    assert almanac[0] == (-15.0, 15.0)          # centered on the top
    assert almanac[1] == (15.0, 45.0)


# --- The Almanac's own year mapping ----------------------------------------------


def test_almanac_month_index_orders_from_june():
    assert almanac_month_index(6) == 0          # June at the top
    assert almanac_month_index(12) == 6         # December
    assert almanac_month_index(1) == 7          # January
    assert almanac_month_index(5) == 11         # May, the last wedge


def test_january_first_sits_on_the_01h_line():
    """January 1 lands exactly on the 01:00h line = dial 195°
    (owner spec: the 1st of each month on its wedge-start line)."""
    assert almanac_marker_angle(date(2026, 1, 1)) == pytest.approx(195.0)


def test_june_first_sits_on_the_11h_line():
    """June 1 lands on the 11:00h line = 15° before the top (345°)."""
    assert almanac_marker_angle(date(2026, 6, 1)) == pytest.approx(345.0)


def test_summer_solstice_lands_a_few_ticks_past_the_top():
    """The June 21 solstice sits ~5-6 ticks (≈ days) clockwise past the
    top — the natural consequence of anchoring June 1 to the 11h line
    (owner spec: not a concession)."""
    angle = almanac_marker_angle(date(2026, 6, 21))
    assert 4.0 <= angle <= 7.0                   # ~5-6°, one tick per day


def test_february_day_tempo_uses_the_real_calendar():
    """February covers its 30° in 28 (or 29) real days — day D sits
    (D-1)/days_in_month into the wedge, so 2028's leap February runs a
    hair slower than 2026's."""
    common = almanac_marker_angle(date(2026, 2, 15))
    leap = almanac_marker_angle(date(2028, 2, 15))
    # Feb is wedge index 8 -> start 8*30-15 = 225°.
    assert common == pytest.approx(225.0 + 14 / 28 * 30.0)
    assert leap == pytest.approx(225.0 + 14 / 29 * 30.0)
    assert leap < common                         # slower tempo, earlier tick


# --- The Earth day-arrow ---------------------------------------------------------


def test_day_arrow_points_outward_at_the_marker_tick():
    """The arrow's tip lands at the marker's exact angle on the ring-tick
    radius; its base sits inward (pointing OUT)."""
    radius = 180.0
    angle = almanac_marker_angle(date(2026, 7, 16))
    arrow = calendar_day_arrow(angle, radius)
    tip = arrow[0]
    expected = dial_point(angle, radius * defaults.CALENDAR_ARROW_TIP_FRACTION)
    assert tip.x() == pytest.approx(expected.x())
    assert tip.y() == pytest.approx(expected.y())
    tip_r = math.hypot(tip.x(), tip.y())
    base_r = math.hypot(arrow[1].x(), arrow[1].y())
    assert tip_r > base_r                        # tip outward, base inward


# --- THE LIT WEDGE IS DELETED (owner decree 2026-07-29) --------------------------
# "Osvetljavanje part koji prolazi sat ili zemlja iskljuciti — obrisati
# tu funkcionalnost". These regressions guard the grave: no key, no
# constant, no render path, no wedge that paints brighter than its
# siblings — and an old settings file carrying the stale key still loads.


def test_lit_wedge_feature_names_are_all_gone():
    """No `calendar_lighting` setting, no `CALENDAR_LIGHTING_MODES`, no
    `calendar_lit_index`, no `CALENDAR_WEDGE_LIT_DELTA`, no
    `RenderContext.calendar_lit` — Rule #6, the whole feature deleted
    rather than wrapped."""
    import render.layers as layers_module
    from app.settings_store import Settings
    from skins.manifest import SkinDefinition

    def field_names(cls) -> set[str]:
        return {f.name for f in dataclasses.fields(cls)}

    assert "calendar_lighting" not in field_names(Settings)
    assert "calendar_lighting" not in field_names(SkinDefinition)
    assert "calendar_lit" not in field_names(layers_module.RenderContext)
    assert not hasattr(constants, "CALENDAR_LIGHTING_MODES")
    assert not hasattr(defaults, "CALENDAR_WEDGE_LIT_DELTA")
    assert not hasattr(layers_module, "calendar_lit_index")
    assert not hasattr(Compositor, "_calendar_lit")


def test_every_calendar_wedge_paints_at_the_same_opacity(app):
    """The RENDER proof, not just the API proof: at 12:15 — the exact
    moment the old "hour" mode lit the top wedge and the old "year" mode
    lit July's — no wedge stands out. Sampling the mount-free mid-radius
    of all twelve wedges gives twelve equal alphas."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    comp = Compositor(_calendar_skin(calendar_mount="off"), AssetCache())
    image = comp.render_offscreen(360.0, 1.0, day, tick)
    alphas = []
    for index in range(12):
        angle = index * constants.CALENDAR_WEDGE_DEG + 15.0
        point = dial_point(angle, 150.0)
        alphas.append(
            image.pixelColor(
                round(180.0 + point.x()), round(180.0 + point.y())
            ).alpha()
        )
    assert min(alphas) > 0                       # every wedge really painted
    assert max(alphas) - min(alphas) <= 1        # and none of them lights


def test_composite_key_is_daily_again_without_the_lit_wedge(app):
    """The lit wedge was the ONE intraday term in the cached-composite
    key — deleting it makes the key purely (size, day). Two ticks eight
    hours apart on the same day must NOT invalidate the composite."""
    day, morning = _day_tick(app, datetime(2026, 7, 16, 8, 15))
    _, evening = _day_tick(app, datetime(2026, 7, 16, 16, 30))
    comp = Compositor(_calendar_skin(), AssetCache())
    comp.render_offscreen(360.0, 1.0, day, morning)
    first = comp._composite_key
    comp.render_offscreen(360.0, 1.0, day, evening)
    assert comp._composite_key == first


def test_settings_file_with_the_stale_lighting_key_still_loads(tmp_path):
    """THE SETTINGS-MIGRATION LAW (this project was burned by it before,
    MEMORY "Settings migration on rename"): every file written before
    2026-07-29 carries `calendar_lighting`. The loader must IGNORE the
    stale key — never read the file as corrupt and offer a reset."""
    from app.settings_store import SettingsStore

    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    store.save(dataclasses.replace(store.load(), calendar_mount="chinese"))
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert "calendar_lighting" not in raw          # never written again
    raw["calendar_lighting"] = "year"              # an old file's leftover
    path.write_text(json.dumps(raw), encoding="utf-8")
    loaded = SettingsStore(path).load()            # must NOT raise
    assert loaded.calendar_mount == "chinese"      # and the rest survived


# --- Slots & rotation ------------------------------------------------------------


def test_calendar_uses_the_pinned_slot_layout():
    """No weekday model: the pinned 24h slot alone, exactly as Aurora /
    the pointer-off case — the weekday mode sits in a seat, never the
    classic unit."""
    skin = _calendar_skin()
    assert slot_layout(skin) == {1: constants.SOUTH_SLOT_ANGLE}
    assert weekday_classic_slot(skin) is None
    assert slot_layout(_calendar_skin(show_octa_slot=True)) == {
        1: constants.AURORA_DUAL_WEEKDAY_ANGLE,
        2: constants.AURORA_DUAL_SLOT_ANGLE,
    }


def test_calendar_wedges_never_rotate_with_the_sun():
    """The wedges are calendar-fixed (owner spec): the slot seats do not
    ride the solar offset even with solar_rotation on, exactly like the
    pinned layouts."""
    assert slot_seat_rotation(_calendar_skin(solar_rotation=True), 10.76) == 0.0


def test_calendar_renders_and_the_hover_reads_the_wheel(app):
    """Both wheels paint without a crash, and a wedge hover answers: the
    Almanac names the month + double-hour animal, the Zodiac the sign +
    dates."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    for style in ("primary", "secondary"):
        skin = _calendar_skin(palette_style=style)
        comp = Compositor(skin, AssetCache())
        image = comp.render_offscreen(360.0, 1.0, day, tick)
        assert image.pixelColor(180, 8).alpha() > 200        # ring painted
        assert image.pixelColor(180, 120).alpha() > 0        # a wedge painted
    # Almanac wedge hover at the top (June/July border region): probe the
    # top wedge center — the month + animal answer.
    almanac = Compositor(_calendar_skin(palette_style="secondary"), AssetCache())
    almanac.render_offscreen(360.0, 1.0, day, tick)
    top = almanac.tooltip_at(180.0, 120.0, 360.0)            # inside the top wedge
    assert top is not None and "June" in top and "Horse" in top
    # The wedge WEARS OUR ART (owner 2026-07-16, ROADMAP queue #7): the
    # Chinese COLORED medallion (a real image tag), never a plain-text
    # stand-in — the src is the scaled raster-cache copy of the colored
    # animal medallion.
    assert "<img" in top and "raster_cache" in top
    # Zodiac wedge hover at the top: Cancer with its dates + the sign's
    # COLORED LOGO art.
    zodiac = Compositor(_calendar_skin(palette_style="primary"), AssetCache())
    zodiac.render_offscreen(360.0, 1.0, day, tick)
    top_sign = zodiac.tooltip_at(200.0, 120.0, 360.0)        # top-right wedge
    assert top_sign is not None and (
        "Cancer" in top_sign or "Leo" in top_sign
    )
    assert "<img" in top_sign and "raster_cache" in top_sign


def test_spacebar_encyclopedia_target_maps_the_hovered_wheel(app):
    """The Spacebar jump (owner 2026-07-16, ROADMAP queue #8): the
    ONE element→topic mapping opens the hovered Calendar wedge's page —
    the Almanac's Chinese animal, the Zodiac's sign — indexing the
    topic's own entry order. Works with the legend OFF (geometry, not
    tooltip text)."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    almanac = Compositor(
        _calendar_skin(palette_style="secondary", legend=False), AssetCache()
    )
    almanac.render_offscreen(360.0, 1.0, day, tick)
    assert almanac.tooltip_at(180.0, 120.0, 360.0) is None     # legend off
    # The top Almanac wedge is the Horse double-hour → Chinese entry 6.
    assert almanac.encyclopedia_target(180.0, 120.0, 360.0) == ("chinese", 6)
    zodiac = Compositor(_calendar_skin(palette_style="primary"), AssetCache())
    zodiac.render_offscreen(360.0, 1.0, day, tick)
    topic, index = zodiac.encyclopedia_target(200.0, 120.0, 360.0)
    assert topic == "astrology" and 0 <= index < 12
    # Off any target (dial center) there is nothing to open.
    assert zodiac.encyclopedia_target(180.0, 180.0, 360.0) is None


# --- The 12-SET MOUNT (DESIGN ZODIAC law, R9a round 2026-07-21) ------------------
# "Zodiac i sve što ima 12 TREBA da bude moguće da se AKTIVIRA na CALENDAR
# POINTER (TO MU JE DEFAULT)": twelve marks, one per wedge, at 60-70% of
# the dial radius, independent of which wheel paints the background.


def test_mount_wheel_is_independent_of_the_active_background_wheel():
    """Zodiac marks always ride the ZODIAC wheel's own cardinal-START
    wedges (sign i's wedge IS its own 30-deg arc — the honest alignment
    already used for the wedge-lit law, no separate approximation);
    months always ride the ALMANAC wheel's cardinal-CENTERED wedges."""
    assert calendar_mount_wheel("zodiac") == "zodiac"
    assert calendar_mount_wheel("months") == "almanac"
    assert calendar_mount_angle("zodiac", 0) == pytest.approx(15.0)   # Cancer wedge center
    assert calendar_mount_angle("months", 0) == pytest.approx(0.0)    # June, on the axis
    # Twelve marks, evenly spaced 30 deg apart, on EITHER geometry.
    for mount in ("zodiac", "months"):
        angles = [calendar_mount_angle(mount, i) for i in range(12)]
        assert len(set(angles)) == 12
        gaps = {
            round((angles[i + 1] - angles[i]) % 360.0, 6) for i in range(11)
        }
        assert gaps == {30.0}


def test_zodiac_mount_entries_carry_the_real_committed_badges():
    """The zodiac mount reads the SAME astrology COLORED badges the
    background wedge hover already shows (Rule #5) — real art, shipped
    today, never a gap."""
    entries = calendar_mount_entries("zodiac")
    assert len(entries) == 12
    assert [name for name, _art in entries] == [
        name for name, _symbol in constants.ZODIAC_SIGNS
    ]
    assert all(art is not None and art.exists() for _name, art in entries)


def test_months_mount_entries_are_graceful_absent_and_wedge_aligned():
    """The Slavic months mount in the Almanac's own June-leads order
    (index 0 = Lipanj/June, matching almanac_month_index) with NO art
    yet (owner R7b: the prompt sheet has not landed) — the name is
    always present so the caller never draws a gap."""
    entries = calendar_mount_entries("months")
    assert len(entries) == 12
    assert entries[0][0] == "Lipanj"                 # June leads
    assert entries[almanac_month_index(1)][0] == "Siječanj"   # January
    assert all(name for name, _art in entries)       # every wedge named
    # The owner's ChatGPT drop landed some month plates (RESTRUCTURE
    # 2026-07-22 relocated them to calendars/slavic_months/); each wedge
    # either resolves to a real suffixed plate or stays graceful-absent.
    assert all(art is None or art.exists() for _name, art in entries)


def test_mount_current_index_matches_todays_sign_and_month_no_hemisphere_flip(app):
    """The emphasis mark says "you are here" on the MOUNTED ROSTER — it
    outlived the deleted wedge lighting (owner 2026-07-29) because it
    marks a roster member, not dial paint. Never hemisphere-mirrored:
    the mark sits on its own fixed wedge identity (unlike the Earth
    marker's orbit)."""
    day, _tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    names = [name for name, _symbol in constants.ZODIAC_SIGNS]
    assert calendar_mount_current_index("zodiac", day) == names.index(day.zodiac_name)
    assert calendar_mount_current_index("months", day) == almanac_month_index(
        day.local_date.month
    )


def test_mount_lit_delta_raises_the_current_mark_to_full_opacity():
    """"the mark can inherit that brightness" (owner spec) — the same
    base+delta shape the wedges once used, sized so the current mark
    reaches (but never exceeds) full opacity."""
    assert 0.0 < defaults.CALENDAR_MOUNT_ALPHA < 1.0
    assert defaults.CALENDAR_MOUNT_ALPHA + defaults.CALENDAR_MOUNT_LIT_DELTA == (
        pytest.approx(1.0)
    )


def test_calendar_mount_renders_and_a_mark_hover_outranks_the_wedge(app):
    """The mount paints without a crash and a mark's own small hit
    target wins over the broader whole-wedge hover beneath it: zodiac
    speaks sign + dates + its colored badge, months speaks the Croatian
    name + English gloss (graceful-absent art, never a broken image)."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    radius = 180.0

    def px(mount: str, index: int) -> tuple[float, float]:
        point = dial_point(
            calendar_mount_angle(mount, index),
            radius * defaults.CALENDAR_MOUNT_RADIUS_FRACTION,
        )
        return radius + point.x(), radius + point.y()

    zodiac = Compositor(
        _calendar_skin(palette_style="primary", calendar_mount="zodiac"),
        AssetCache(),
    )
    zodiac.render_offscreen(360.0, 1.0, day, tick)
    x, y = px("zodiac", 0)                       # Cancer's own mark
    text = zodiac.tooltip_at(x, y, 360.0)
    assert text is not None and "Cancer" in text and "<img" in text

    months = Compositor(
        _calendar_skin(palette_style="secondary", calendar_mount="months"),
        AssetCache(),
    )
    months.render_offscreen(360.0, 1.0, day, tick)
    x2, y2 = px("months", 0)                     # Lipanj's own mark
    text2 = months.tooltip_at(x2, y2, 360.0)
    assert text2 is not None and "Lipanj" in text2 and "Linden" in text2
    # The month plates LANDED (owner art wave 2026-07-26) — the tooltip
    # now legitimately embeds the real image; the pre-art assertion
    # ("graceful-absent: no broken image") retired with the drop.
    assert "<img" in text2


def test_calendar_mount_off_speaks_no_mark_hover(app):
    """Off leaves the position to the broader wedge hover instead — the
    mark-specific hit test is simply absent, never a crash."""
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    skin = _calendar_skin(calendar_mount="off")
    comp = Compositor(skin, AssetCache())
    comp.set_day(day)
    comp._last_tick = tick
    point = dial_point(15.0, 180.0 * defaults.CALENDAR_MOUNT_RADIUS_FRACTION)
    assert comp._calendar_mount_tooltip(point, 180.0) is None


def test_calendar_mount_modes_are_derived_from_the_registry():
    """THE GENERALIZED OFFER (owner decree 2026-07-29): the legal
    setting values are no longer a hand-kept tuple — they fall out of
    `defaults.CALENDAR_MOUNTS`, so registering a roster makes it
    settable with no second edit (Rule #5)."""
    assert defaults.CALENDAR_MOUNT_MODES == ("off",) + tuple(
        defaults.CALENDAR_MOUNTS
    )
    assert defaults.DEFAULT_SKIN.calendar_mount in defaults.CALENDAR_MOUNT_MODES
    assert not hasattr(constants, "CALENDAR_MOUNT_MODES")   # moved, not copied


def test_every_registered_mount_is_canon_shaped():
    """Each entry declares a sealed DOZEN SYSTEM (CANON §The Two Dozen
    Systems), a seat count the seat law knows how to place, members in
    seat order with no blanks, and a centre that is either a real
    `THIRTEENTHS` key or None."""
    for key, mount in defaults.CALENDAR_MOUNTS.items():
        assert mount.system in ("A", "B"), key
        assert mount.seats in defaults.CALENDAR_MOUNT_SEATS_PER_WEDGE, key
        assert len(mount.members) == len(set(mount.members)) == mount.seats, key
        assert all(mount.members), key
        assert len(mount.stems) == mount.seats, key
        assert mount.centre is None or mount.centre in constants.THIRTEENTHS, key
        assert mount.follows in (None, "sign", "month"), key


def test_the_new_dozens_are_seated_exactly_where_canon_says():
    """The two rosters this round added, both against CANON's own words.

    The MONTH DOZEN is System B — "June centered on noon" — so June
    leads and December roots the bottom. The EMOTIONS DOZEN is System B
    with canon's hour list read verbatim ("Love 12h, Hope 14h, Courage
    16h, Ambition 18h, Pride 20h, Envy 22h, Hatred 24h, Despair 02h,
    Fear 04h, Doubt 06h, Humility 08h, Gratitude 10h") — and because a
    System B wedge is CENTERED on its hour, seat k IS hour 12 + 2k."""
    almanac = defaults.CALENDAR_MOUNTS["almanac"]
    assert almanac.system == "B"
    assert almanac.members[0] == "June"                      # the crown
    assert almanac.members[6] == "December"                  # the root
    assert almanac.members[almanac_month_index(1)] == "January"
    emotions = defaults.CALENDAR_MOUNTS["emotions"]
    assert emotions.system == "B"
    assert emotions.members[0] == "Love"                     # crown, 12h
    assert emotions.members[6] == "Hatred"                   # root, 24h
    # Canon's six opposition axes: every wedge faces its exact opposite.
    for k, (near, far) in enumerate(zip(emotions.members, emotions.members[6:])):
        assert (near, far) in (
            ("Love", "Hatred"), ("Hope", "Despair"), ("Courage", "Fear"),
            ("Ambition", "Doubt"), ("Pride", "Humility"), ("Envy", "Gratitude"),
        ), k
    # Both wear real committed art — never the name fallback.
    for key in ("almanac", "emotions"):
        entries = calendar_mount_entries(key)
        assert all(art is not None and art.exists() for _n, art in entries), key


def test_the_four_new_dozens_are_seated_exactly_where_canon_says():
    """Golden seat pins straight from CANON.md §The Two Dozen Systems
    (all four sealed 2026-07-29): member order lands on the CANON wedge
    for BOTH dozen systems — System A's boundary-start wedges
    (Olympians/Apostles, six pairs) and System B's cardinal-centered
    wedges (the Virtue Wheel's two registers, one crown + one root)."""
    olympians = defaults.CALENDAR_MOUNTS["olympians"]
    assert olympians.system == "A" and olympians.centre == "hestia"
    assert olympians.members[0] == "Zeus"              # 12-14h, opens the crown
    assert olympians.members[11] == "Hera"             # 10-12h, closes the crown
    assert olympians.members[6] == "Poseidon"          # 00-02h, the root
    assert olympians.members[5] == "Demeter"           # 22-24h, the root's mate

    apostles = defaults.CALENDAR_MOUNTS["apostles"]
    assert apostles.system == "A" and apostles.centre == "jesus"
    assert apostles.members[0] == "Peter"              # 12-14h, opens the crown
    assert apostles.members[11] == "Andrew"            # 10-12h, closes the crown
    assert apostles.members[5] == "Judas Iscariot"     # 22-24h, the root
    assert apostles.members[6] == "Simon the Zealot"   # 00-02h, the root's mate

    virtues = defaults.CALENDAR_MOUNTS["virtues"]
    assert virtues.system == "B" and virtues.centre == "prudence"
    assert virtues.members[0] == "Magnanimity"         # 12h, the crown
    assert virtues.members[6] == "Just Indignation"    # 24h, the root

    vices = defaults.CALENDAR_MOUNTS["vices"]
    assert vices.system == "B" and vices.centre == "cunning"
    assert vices.members[0] == "Vanity"                # 12h, the crown
    assert vices.members[6] == "Envy"                  # 24h, the root

    # The golden ANGLES themselves (not just tuple order) — proof each
    # figure's seat lands on its CANON-sealed wedge center.
    def hour_of(mount: str, index: int) -> float:
        return (12.0 + calendar_mount_angle(mount, index) / 15.0) % 24.0

    assert hour_of("olympians", 0) == pytest.approx(13.0)    # Zeus, 12-14h
    assert hour_of("olympians", 11) == pytest.approx(11.0)   # Hera, 10-12h
    assert hour_of("apostles", 5) == pytest.approx(23.0)     # Judas, 22-24h
    assert hour_of("virtues", 0) == pytest.approx(12.0)      # Magnanimity, crown
    assert hour_of("vices", 6) == pytest.approx(0.0)         # Envy, root (24h≡0h)


def test_the_sins_dozen_is_seated_exactly_where_canon_says():
    """Golden seat pins for the FIFTH Dozen, straight from CANON.md
    §The Sins Dozen (owner-sealed 2026-07-29). System B, so seat k IS
    hour 12 + 2k: **Pride crowns at 12h** (Gregory's root returned to
    the rim, Vainglory FOLDED INTO IT — there is no Vainglory seat),
    **Treachery roots at 24h** (the root law; Judas' own midnight on
    the Apostles Dozen), **Lust at 20h** (the red arm's appetite), and
    **Violence at 16h** (the 16h call, delegated and ruled — Cruelty is
    NOT a member). The centre is HARDNESS OF HEART, the anti-Peace."""
    sins = defaults.CALENDAR_MOUNTS["sins"]
    assert sins.system == "B" and sins.centre == "hardness_of_heart"
    assert sins.members == (
        "Pride", "Hypocrisy", "Violence", "Avarice", "Lust", "Envy",
        "Treachery", "Despair", "Wrath", "Idolatry", "Gluttony", "Acedia",
    )
    assert "Vainglory" not in sins.members      # folded into Pride by the seal
    assert "Cruelty" not in sins.members        # weighed and set aside
    assert sins.follows is None                 # there is no "today's sin"

    def hour_of(index: int) -> float:
        return (12.0 + calendar_mount_angle("sins", index) / 15.0) % 24.0

    assert hour_of(0) == pytest.approx(12.0)    # Pride, the crown
    assert hour_of(6) == pytest.approx(0.0)     # Treachery, the root (24h = 0h)
    assert hour_of(4) == pytest.approx(20.0)    # Lust
    assert hour_of(2) == pytest.approx(16.0)    # Violence
    # Canon's six opposition axes: every seat faces its exact opposite.
    for k, (near, far) in enumerate(zip(sins.members, sins.members[6:])):
        assert (near, far) in (
            ("Pride", "Treachery"), ("Hypocrisy", "Despair"),
            ("Violence", "Wrath"), ("Avarice", "Idolatry"),
            ("Lust", "Gluttony"), ("Envy", "Acedia"),
        ), k
    # The axle is a real THIRTEENTHS key and an ALWAYS-CENTER — no
    # trigger, no window (THE AXLE LAW).
    assert constants.THIRTEENTHS["hardness_of_heart"][0] == "Hardness of Heart"
    assert "hardness_of_heart" in constants.AXLE_ALWAYS_CENTERS


def test_the_sins_mount_is_settable_and_survives_a_settings_round_trip(tmp_path):
    """Registering the roster makes it a legal `calendar_mount` value
    with no second edit (THE GENERALIZED OFFER) — and a saved file
    carrying it loads back unchanged, never read as corrupt (THE
    SETTINGS-MIGRATION LAW, MEMORY "Settings migration on rename")."""
    from app.settings_store import SettingsStore

    assert "sins" in defaults.CALENDAR_MOUNT_MODES
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    store.save(dataclasses.replace(store.load(), calendar_mount="sins"))
    assert json.loads(path.read_text(encoding="utf-8"))["calendar_mount"] == "sins"
    assert SettingsStore(path).load().calendar_mount == "sins"


def test_new_dozens_rim_members_carry_real_committed_art():
    """The twelve RIM members of all four new Dozens landed real art
    ahead of this wiring round (owner PromptPainter drop under
    `assets/calendars/{olympians,apostles,virtues,vices}/`) — never the
    name fallback, exactly like the zodiac/chinese mounts."""
    for key in ("olympians", "apostles", "virtues", "vices"):
        entries = calendar_mount_entries(key)
        assert len(entries) == 12
        assert all(art is not None and art.exists() for _n, art in entries), key


def test_new_dozens_axle_plate_is_graceful_absent():
    """The AXLE's own plate has not landed on disk for ANY of the six
    always-centers — `thirteenth_plate` must resolve `None`, never
    crash, with the name still speaking (the SAME graceful-absent
    contract Sol/Modrenik carried before their own art landed). The
    Sins Dozen's axle also proves the axle STEM rule: a display name
    with spaces resolves through the underscored filename, the same
    no-space rule `art_stems` applies to `Just_Indignation`."""
    from render.layers import thirteenth_plate

    for key in constants.AXLE_ALWAYS_CENTERS:
        resolved_name, art = thirteenth_plate(key)
        assert resolved_name == constants.THIRTEENTHS[key][0], key
        assert art is None, key
    assert thirteenth_plate("hardness_of_heart")[0] == "Hardness of Heart"


def test_seat_law_places_twelve_one_per_wedge_and_twentyfour_two(app):
    """THE SEAT LAW (owner decree 2026-07-29). A 12-set sits one per
    wedge, ON the wedge center; a 24-set sits TWO per wedge, a quarter
    wedge either side of it — a 15° pitch across the whole dial. One
    formula serves both (`calendar_mount_angle`), so this test drives it
    through a real registry entry for 12 and through a 24-seat entry for
    24, proving the placement rather than a table."""
    step = constants.CALENDAR_WEDGE_DEG
    # 12 → one per wedge, exactly on the wedge center.
    for key in defaults.CALENDAR_MOUNTS:
        mount = defaults.CALENDAR_MOUNTS[key]
        angles = [calendar_mount_angle(key, i) for i in range(mount.seats)]
        bounds = calendar_wedge_bounds(calendar_mount_wheel(key))
        assert angles == [
            pytest.approx((start + end) / 2.0) for start, end in bounds
        ], key
    # 24 → two per wedge. Registered through the SAME registry so the
    # engine is exercised, not a parallel code path.
    two_per = defaults.CalendarMount(
        title="Twenty-four", system="B",
        members=tuple(f"S{i:02d}" for i in range(24)),
        art_dir="emotions/primary/colored",
    )
    defaults.CALENDAR_MOUNTS["_test24"] = two_per
    try:
        angles = [calendar_mount_angle("_test24", i) for i in range(24)]
        assert len(angles) == 24
        gaps = {round((angles[i + 1] - angles[i]) % 360.0, 6) for i in range(23)}
        assert gaps == {step / 2.0}                  # a 15-deg ray pitch
        centers = [
            (start + end) / 2.0
            for start, end in calendar_wedge_bounds(calendar_mount_wheel("_test24"))
        ]
        for wedge, center in enumerate(centers):
            assert angles[2 * wedge] == pytest.approx(center - step / 4.0)
            assert angles[2 * wedge + 1] == pytest.approx(center + step / 4.0)
        # And the marks SHRINK with the pitch, so twenty-four never touch.
        assert calendar_mount_mark_height("_test24", 180.0) == pytest.approx(
            calendar_mount_mark_height("emotions", 180.0) / 2.0
        )
    finally:
        del defaults.CALENDAR_MOUNTS["_test24"]


def test_centre_rule_is_per_roster_and_never_unconditional(app):
    """THE CENTER, for a CALENDAR-DRIVEN centre (owner: "and NOT
    always"). A roster's `centre` names WHICH thirteenth may take the
    dial center — the appearance rule itself stays `core.blue_moon`'s,
    so a calendar-driven centre's seat is empty on almost every day.
    Golden pair for Ophiuchus: Dec 5 2026 is inside a 13-full-moon year
    AND inside its Nov 29 - Dec 17 window, so it shows; Dec 5 2025 is
    not a 13-full-moon year, so the very same wheel, mount and calendar
    day show NOTHING. (An ALWAYS-CENTER roster's own centre is EXEMPT
    from this — THE AXLE LAW, owner-sealed 2026-07-29, tested separately
    below in `test_axle_always_centers_are_unconditionally_present`; every
    roster registered today names a real centre, so the "names none"
    branch is exercised here through a SYNTHETIC mount, the same way
    `test_seat_law_places_twelve_one_per_wedge_and_twentyfour_two`
    exercises its own synthetic 24-seat entry.)"""
    from render.layers import active_thirteenth

    shows, _t = _day_tick(app, datetime(2026, 12, 5, 12, 0))
    hides, _t2 = _day_tick(app, datetime(2025, 12, 5, 12, 0))
    skin = _calendar_skin(palette_style="primary", calendar_mount="zodiac")
    assert active_thirteenth(skin, shows) == "ophiuchus"
    assert active_thirteenth(skin, hides) is None
    # A roster canon gives NO thirteenth of its own claims nothing, so
    # resolution falls through to the WHEEL underneath exactly like
    # "off" — the documented law, unchanged by the generalization.
    defaults.CALENDAR_MOUNTS["_test_no_centre"] = defaults.CALENDAR_MOUNTS[
        "emotions"
    ]._replace(centre=None)
    try:
        no_centre = _calendar_skin(
            palette_style="primary", calendar_mount="_test_no_centre"
        )
        assert active_thirteenth(no_centre, shows) == "ophiuchus"  # the wheel's
        assert active_thirteenth(no_centre, hides) is None
    finally:
        del defaults.CALENDAR_MOUNTS["_test_no_centre"]
    # ...and the Emotions Dozen itself emphasizes no MARK — there is no
    # "today's emotion" (`follows` is None, untouched by the Axle seal).
    assert calendar_mount_current_index("emotions", shows) is None
    # A roster that DOES name a CALENDAR-DRIVEN centre outranks the
    # wheel (the owner's tiebreak): the same zodiac wheel, same day, the
    # Slavic months mount on top — Modrenik's own window has not opened
    # on Dec 5, so the center is empty rather than falling back to
    # Ophiuchus.
    months = _calendar_skin(palette_style="primary", calendar_mount="months")
    assert defaults.CALENDAR_MOUNTS["months"].centre == "modrenik"
    assert active_thirteenth(months, shows) is None


def test_axle_always_centers_are_unconditionally_present(app):
    """THE AXLE LAW's always-present half (CANON §The Axle, owner-sealed
    2026-07-29): Hestia/Jesus/Prudence/Cunning/Peace/Hardness of Heart
    carry NO trigger and NO window — unlike Ophiuchus/Sol/Modrenik/The
    Cat, they show on an ARBITRARY ordinary date, every one of the six
    at once, while Ophiuchus stays rule-driven on that very same day
    (the existing golden pair keeps passing: present 2026-12-05, absent
    2025-12-05). The constant is named for the LAW, not for personhood
    (renamed 2026-07-29): Peace and Hardness of Heart are STATES, and
    the seam THE AXLE LAW actually draws is "not a leftover month"."""
    from render.layers import active_thirteenth

    ordinary, _t = _day_tick(app, datetime(2026, 3, 15, 12, 0))
    assert constants.AXLE_ALWAYS_CENTERS <= ordinary.thirteenth_candidates
    assert "ophiuchus" not in ordinary.thirteenth_candidates    # still rule-driven
    for mount, centre in (
        ("olympians", "hestia"), ("apostles", "jesus"),
        ("virtues", "prudence"), ("vices", "cunning"),
        ("emotions", "peace"), ("sins", "hardness_of_heart"),
    ):
        assert defaults.CALENDAR_MOUNTS[mount].centre == centre, mount
        skin = _calendar_skin(calendar_mount=mount)
        assert active_thirteenth(skin, ordinary) == centre, mount
    # The existing Ophiuchus golden pair, unaffected by the Axle seal.
    shows, _t2 = _day_tick(app, datetime(2026, 12, 5, 12, 0))
    hides, _t3 = _day_tick(app, datetime(2025, 12, 5, 12, 0))
    zodiac_skin = _calendar_skin(palette_style="primary", calendar_mount="zodiac")
    assert active_thirteenth(zodiac_skin, shows) == "ophiuchus"
    assert active_thirteenth(zodiac_skin, hides) is None


# --- The Chinese MONTHLY-animal mount (owner R12, Blue Moon round) --------------


def test_chinese_mount_wheel_and_entries_are_gregorian_fixed_with_real_art():
    """The Chinese mount (owner R12: "Mount Chinese zodiac") rides the
    SAME Gregorian-fixed Almanac geometry as the months mount, keyed by
    `constants.CHINESE_MONTH_BRANCH_ANIMALS` — real, committed COLORED
    badges (Rule #5), never a gap. June leads with the Horse (the
    branch that begins ~Jun 6), December with the Rat (the branch that
    holds the winter solstice — core.blue_moon.chinese_leap_month reads
    the SAME fact)."""
    assert calendar_mount_wheel("chinese") == "almanac"
    entries = calendar_mount_entries("chinese")
    assert len(entries) == 12
    assert entries[0][0] == "Horse"                      # June
    assert entries[almanac_month_index(12)][0] == "Rat"   # December
    assert entries[almanac_month_index(2)][0] == "Tiger"  # February
    assert all(art is not None and art.exists() for _name, art in entries)


def test_chinese_mount_current_index_matches_todays_month(app):
    day, _tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    assert calendar_mount_current_index("chinese", day) == almanac_month_index(7)


def test_chinese_mount_dims_the_doubled_months_animal_during_a_leap_month(app):
    """THE CAT'S DIMMING LAW (owner spec, item 5): while a Chinese leap
    month holds the center, the mount mark of the DOUBLED month's own
    animal — never the current-month mark — dims below its resting
    alpha. 2025 is a real leap-6th-month year (Jul 25 - Aug 22): the
    doubled lunar month is the 6th, whose branch animal is the Goat
    (jianyin numbering: L1 Tiger .. L6 Goat .. L11 Rat .. L12 Ox), whose
    Gregorian mount seat is July."""
    from core.blue_moon import chinese_leap_month
    from data.moon_phases import MoonPhaseRepository
    from data.seasons import SeasonsRepository

    anchors = SeasonsRepository().year_anchors(2025)
    window = MoonPhaseRepository().moon_window(2025)
    leap = chinese_leap_month(anchors, window)
    assert leap is not None and leap.number == 6

    inside = _day_tick(app, datetime(2025, 8, 1, 12, 0))[0]
    assert inside.chinese_leap_month_number == 6
    dimmed = chinese_mount_dimmed_index(inside)
    assert dimmed == almanac_month_index(7)                # the Goat's own July seat

    outside = _day_tick(app, datetime(2025, 3, 1, 12, 0))[0]
    assert outside.chinese_leap_month_number is None
    assert chinese_mount_dimmed_index(outside) is None


def test_chinese_mount_renders_and_hover_names_the_animal(app):
    day, tick = _day_tick(app, datetime(2026, 7, 16, 12, 15))
    radius = 180.0
    chinese = Compositor(
        _calendar_skin(palette_style="secondary", calendar_mount="chinese"),
        AssetCache(),
    )
    chinese.render_offscreen(360.0, 1.0, day, tick)
    point = dial_point(
        calendar_mount_angle("chinese", 0), radius * defaults.CALENDAR_MOUNT_RADIUS_FRACTION
    )
    text = chinese.tooltip_at(radius + point.x(), radius + point.y(), 360.0)
    assert text is not None and "Horse" in text and "<img" in text
    assert "June" in text                     # "animal + its month" (owner spec)
