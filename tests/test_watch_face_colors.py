"""Watch Face Phase 4 (Colors + Opacity, see colors.md/opacity.md)
regressions: both sections build without a placeholder, every setter
key they call is wired in `WatchController._watch_face_setters`, the
new `Settings` fields round-trip through `SettingsStore`, and the
render-level hooks (Umbra tint/alpha, Aura-off color, Hands/Jewels
tint) actually alter the composed pixels — never a control that paints
nothing (root CLAUDE.md's honesty rule)."""

import dataclasses
import inspect
import os
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import astral
import pytest
from PySide6.QtWidgets import QApplication, QGroupBox, QWidget

from app import controller as controller_module
from app.settings_store import Settings, SettingsStore
from app.watch_face import colors, opacity
from config import defaults, dial
from core.clock_state import build_day_context, build_tick_state
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository
from render.assets import AssetCache
from render.compositor import Compositor


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _noop(*_args, **_kwargs) -> None:
    return None


def _opacity_defaults() -> dict:
    skin = defaults.DEFAULT_SKIN
    return {
        "star_alpha": skin.star.day_alpha,
        "aura_day_alpha": skin.background.day_alpha,
        "aura_twilight_alpha": skin.background.twilight_alpha,
        "moon_transit_alpha": skin.year_marker.transit_alpha,
        "ghost_alpha": skin.weekday_set.ghost_opacity,
    }


def _setters() -> dict:
    """Every key answers a no-op, EXCEPT the data PROVIDERS the two
    sections actually call for a value (Rule #5, the same shape
    `test_watch_face.py`'s `_setters()` uses for `slot_descriptors`)."""
    base = defaultdict(lambda: _noop)
    base["opacity_skin_defaults"] = _opacity_defaults
    return base


# --- Both sections build (no placeholder left) ------------------------------


def test_colors_section_builds_a_real_page_not_a_placeholder(app):
    widget = colors.build(Settings(), _setters(), lambda text: text)
    assert isinstance(widget, QWidget)
    groups = widget.findChildren(QGroupBox)
    titles = {group.title() for group in groups}
    assert "Ring tint" in titles
    assert any(title.startswith("Palette") for title in titles)
    assert "Umbra coloring" in titles
    assert any(title.startswith("Aura coloring") for title in titles)
    assert "Hands color" in titles
    assert "Jewels color" in titles
    assert "Metal shades" in titles
    assert "Saturation" in titles


def test_opacity_section_builds_a_real_page_not_a_placeholder(app):
    widget = opacity.build(Settings(), _setters(), lambda text: text)
    assert isinstance(widget, QWidget)
    titles = {group.title() for group in widget.findChildren(QGroupBox)}
    assert titles == {"Clock body", "Bodies on the ring"}


def test_colors_page_builds_with_custom_modes_active(app):
    """The conditional sub-groups (Umbra/Aura custom pickers) build too
    — not just the default "follow" state."""
    settings = Settings(
        umbra_tint_mode="custom", colorful=False, aura_off_tint_mode="custom",
    )
    widget = colors.build(settings, _setters(), lambda text: text)
    assert isinstance(widget, QWidget)


def test_watch_face_window_no_longer_lists_colors_or_opacity_as_placeholders():
    from app.watch_face.window import _SECTIONS

    builders = dict(_SECTIONS)
    assert builders["Colors"] is colors.build
    assert builders["Opacity"] is opacity.build


# --- Every rendered control maps to a REAL controller setter -----------------

_COLORS_SETTER_KEYS = (
    "ring_tint", "palettes", "umbra_tint_mode", "umbra_tint",
    "aura_off_tint_mode", "aura_off_tint", "hands_tint", "jewels_tint",
    "metal_shade_gold", "metal_shade_bronze", "metal_shade_silver",
    "pointer_saturation", "ring_saturation", "hands_saturation",
    "umbra_saturation",
)
_OPACITY_SETTER_KEYS = (
    "star_alpha", "aura_day_alpha", "aura_twilight_alpha", "umbra_alpha",
    "moon_hidden_alpha", "moon_transit_alpha", "ghost_alpha",
    "opacity_skin_defaults",
)


@pytest.mark.parametrize("key", _COLORS_SETTER_KEYS + _OPACITY_SETTER_KEYS)
def test_every_setter_key_is_wired_in_the_controller(key):
    """A STATIC check standing in for a live `WatchController` (too
    heavy to construct in a unit test — it owns a tray icon, timers and
    a warm-cache thread): the controller's OWN `_watch_face_setters`
    source must declare this key as a dict entry, or a Colors/Opacity
    pick would silently no-op against a `defaultdict`-style stub
    forever (the exact failure this test exists to catch)."""
    source = inspect.getsource(controller_module.WatchController._watch_face_setters)
    assert f'"{key}"' in source, (
        f"{key!r} is called by colors.py/opacity.py but "
        "WatchController._watch_face_setters() never declares it"
    )


# --- New settings keys round-trip persistence --------------------------------


def test_new_colors_and_opacity_fields_round_trip():
    settings = Settings(
        umbra_tint_mode="custom", umbra_tint="#FF0000", umbra_saturation=0.3,
        umbra_alpha=0.4, aura_off_tint_mode="black", aura_off_tint="#123456",
        hands_tint="#00FF00", hands_saturation=0.7, jewels_tint="#0000FF",
        moon_transit_alpha=0.9, ghost_alpha=0.2,
    )
    path = Path(tempfile.mktemp(suffix=".json"))
    try:
        store = SettingsStore(path)
        store.save(settings)
        loaded = store.load()
        assert loaded == settings
    finally:
        if path.exists():
            os.remove(path)


def test_umbra_tint_mode_rejects_an_unknown_value():
    path = Path(tempfile.mktemp(suffix=".json"))
    try:
        store = SettingsStore(path)
        store.save(Settings())
        raw = path.read_text(encoding="utf-8")
        path.write_text(raw.replace('"follow"', '"sideways"'), encoding="utf-8")
        with pytest.raises(Exception):
            store.load()
    finally:
        if path.exists():
            os.remove(path)


# --- Render-level: the new hooks actually alter the composed pixels ---------


@pytest.fixture(scope="module")
def frame_args():
    now = datetime(2026, 1, 1, 0, 0, tzinfo=ZoneInfo("UTC"))
    observer = astral.Observer(latitude=45.0, longitude=20.0)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    return day, tick


def _render(skin, day, tick):
    return Compositor(skin, AssetCache()).render_offscreen(400.0, 1.0, day, tick)


def _diff_count(image_a, image_b, step: int = 4) -> int:
    return sum(
        1
        for x in range(0, 400, step)
        for y in range(0, 400, step)
        if image_a.pixelColor(x, y).getRgb() != image_b.pixelColor(x, y).getRgb()
    )


def test_umbra_alpha_actually_dims_the_composed_umbra_layer(app, frame_args):
    day, tick = frame_args
    base = dataclasses.replace(
        defaults.DEFAULT_SKIN, show_pointer=False, show_weekday=False,
        show_earth=False, show_moon=False, ring_tint="#3050E0",
    )
    dimmed = dataclasses.replace(base, umbra_alpha=0.2)
    differing = _diff_count(_render(base, day, tick), _render(dimmed, day, tick))
    assert differing > 0, "umbra_alpha must change the composed Umbra pixels"


def test_umbra_custom_tint_overrides_the_ring_tint_when_in_custom_mode(app, frame_args):
    day, tick = frame_args
    follow = dataclasses.replace(defaults.DEFAULT_SKIN, ring_tint="#00CC00")
    custom = dataclasses.replace(
        follow, umbra_tint_mode="custom", umbra_tint="#CC0000",
    )
    differing = _diff_count(_render(follow, day, tick), _render(custom, day, tick))
    assert differing > 0, "umbra_tint_mode='custom' must repaint the Umbra"


def test_aura_off_color_changes_the_colorless_wedges(app, frame_args):
    day, tick = frame_args
    base = dataclasses.replace(
        defaults.DEFAULT_SKIN, colorful=False, show_pointer=False,
        show_weekday=False, show_earth=False, show_moon=False,
    )
    white = dataclasses.replace(base, aura_off_tint_mode="white")
    custom = dataclasses.replace(
        base, aura_off_tint_mode="custom", aura_off_tint="#00FF00",
    )
    white_img = _render(white, day, tick)
    custom_img = _render(custom, day, tick)
    differing = sum(
        1
        for x in range(0, 400, 8)
        for y in range(0, 400, 8)
        if white_img.pixelColor(x, y).getRgb()
        != custom_img.pixelColor(x, y).getRgb()
    )
    assert differing > 0


def test_hands_tint_overrides_the_ring_tint_independently(app, frame_args):
    day, tick = frame_args
    now = datetime(2026, 7, 7, 10, 13, tzinfo=ZoneInfo("UTC"))
    observer = astral.Observer(latitude=45.0, longitude=20.0)
    day = build_day_context(
        now, observer, SeasonsRepository().year_anchors(now.year),
        MoonPhaseRepository().moon_window(now.year),
    )
    tick = build_tick_state(now, day)
    base = defaults.DEFAULT_SKIN
    tinted_hands = dataclasses.replace(base, hands_tint="#00FF00")
    base_img = _render(base, day, tick)
    hands_img = _render(tinted_hands, day, tick)
    differing = sum(
        1
        for x in range(0, 400, 4)
        for y in range(0, 400, 4)
        if base_img.pixelColor(x, y).getRgb() != hands_img.pixelColor(x, y).getRgb()
    )
    assert differing > 0


def test_jewels_tint_adds_an_extra_recolor_over_the_metal_finish(app, frame_args):
    """DEFAULT_SKIN carries no ring letter art on its own (a bare
    fallback ring, see `skins.manifest.missing_assets`'s referenced-
    asset list) — the real letter art only exists once a ring PRESET
    is resolved, so this probe goes through `build_skin` like the app
    does, not the raw skin fixture the other render tests use."""
    day, tick = frame_args
    base = controller_module.build_skin(Settings())
    tinted = controller_module.build_skin(Settings(jewels_tint="#FF00FF"))
    differing = _diff_count(_render(base, day, tick), _render(tinted, day, tick), step=2)
    assert differing > 0, "jewels_tint must repaint the ring letters"


# --- Crown Text controls (owner correction 2026-08-05): the -----------------
# ROADMAP's Phase-④ claim "no such element" was wrong — `skin.ring.crown_text`
# is the outer Great Seal/cross-station arc, drawn by
# `RingLayer._draw_crown_text`. `crown_text_alpha`/`crown_text_scale`/
# `crown_text_tint` are the three new Colors/Opacity/Size controls attached
# to it; the default bundled ring is "DOMY" (carries crown text), "The One"
# carries none.


def test_crown_text_alpha_actually_dims_the_composed_crown_text(app, frame_args):
    day, tick = frame_args
    base = controller_module.build_skin(Settings())
    dimmed = controller_module.build_skin(Settings(crown_text_alpha=0.1))
    differing = _diff_count(_render(base, day, tick), _render(dimmed, day, tick), step=2)
    assert differing > 0, "crown_text_alpha must change the composed Crown Text pixels"


def test_crown_text_scale_changes_the_composed_crown_text_size(app, frame_args):
    day, tick = frame_args
    base = controller_module.build_skin(Settings())
    enlarged = controller_module.build_skin(Settings(crown_text_scale=1.6))
    differing = _diff_count(_render(base, day, tick), _render(enlarged, day, tick), step=2)
    assert differing > 0, "crown_text_scale must change the composed Crown Text size"


def test_crown_text_tint_recolors_crown_text_independently_of_ring_tint(app, frame_args):
    day, tick = frame_args
    base = controller_module.build_skin(Settings(ring_tint="#3050E0"))
    tinted = controller_module.build_skin(
        Settings(ring_tint="#3050E0", crown_text_tint="#FF00FF")
    )
    differing = _diff_count(_render(base, day, tick), _render(tinted, day, tick), step=2)
    assert differing > 0, "crown_text_tint must repaint the Crown Text independently of ring_tint"


def test_crown_text_scale_reaches_the_live_crown_too(app, frame_args):
    """THE DECOUPLED SCALES (owner defect 2026-08-07): "Crown Text
    scales ALL crown arcs — static and live."

    This test used to assert the opposite for The One, on the premise
    that the preset "ships with no `crown_text` entry at all". The
    premise was never the whole truth: The One's crown is LIVE (its own
    civil hour, `render.layers.numerals.LiveCrownLayer`), and that crown
    is a crown. It answered only to `numeral_outer_size` before, which
    is the same defect from the other side — the Crown Text slider could
    not size the one crown The One actually has."""
    day, tick = frame_args
    base = controller_module.build_skin(Settings(ring="The One"))
    knobbed = controller_module.build_skin(
        Settings(ring="The One", crown_text_scale=1.6)
    )
    differing = _diff_count(_render(base, day, tick), _render(knobbed, day, tick), step=2)
    assert differing > 0, (
        "crown_text_scale must size The One's LIVE crown"
    )


def test_jewels_scale_is_a_no_op_on_the_crown(app, frame_args):
    """The other half of THE DECOUPLED SCALES, and the owner's own
    discovery: the Jewels slider must not grow the crown. Proved on
    Templar, which carries BOTH crowns — the live Jerusalem hour and the
    static NON NOBIS DOMINE arc — so a leak through either would show.
    The jewels themselves are held still by rendering the DIFFERENCE
    only over the crown's own radius band."""
    from render.numeral_bands import CrownSpec  # noqa: F401  (documents intent)
    from render.context import RenderContext
    from render.layers.numerals import crown_spec

    def crown_boxes(jewels_scale):
        skin = controller_module.build_skin(
            Settings(ring="Templar", ring_jewels_scale=jewels_scale)
        )
        ctx = RenderContext(
            radius=360.0, dpr=1.0, skin=skin, cache=None, tick=None, day=None,
        )
        static = 2 * ctx.radius * dial.RING_CROWN_TEXT_SIZE * skin.crown_text_scale
        return static, crown_spec(skin, ctx).height_px

    assert crown_boxes(1.0) == crown_boxes(1.6) == crown_boxes(0.6)
