"""Composition root for ONE watch — the only object that knows
everyone ELSE inside it.

Owns settings, the clock window, the tray, the repositories, the
compositor and the minute scheduler. Tick flow: read the wall clock
fresh -> rebuild the day context when (local date, UTC offset) changed
-> build the tick state -> repaint.

ADD WATCH round (owner INSTRUCTION.txt item 2, sealed 2026-07-21): a
process can hold SEVERAL of these, one per watch, each fully
self-contained — [app.watch_manager.AppController](watch_manager.md)
is the thin process-wide owner that builds the roster, and reaches
each `WatchController` only through the three callbacks its
constructor takes (`watch_count`, `on_add_watch`, `on_remove_watch`) —
a `WatchController` itself still knows nothing about its siblings.
"""

import dataclasses
import re
import sys
import random
import threading
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from time import monotonic
from typing import Callable
from zoneinfo import ZoneInfo

import astral

from PySide6.QtCore import QObject, QRect, Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QCursor, QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QSlider,
    QWidget,
    QWidgetAction,
)

from app import native
from app.design_window import DesignDialog
from app.encyclopedia import EncyclopediaDialog
from app.fast_travel_flash import FastTravelFlash
from app.observatory import ObservatoryDialog
from app.guide import GuideDialog
from app.legend_popup import LegendPopup
from app.pointer_theme import PointerThemeDialog
from app.report import ReportDialog
from app.scheduler import MinuteScheduler
from app.settings_dialog import SettingsDialog
from app.settings_store import (
    Settings,
    SettingsCorruptError,
    SettingsStore,
    replace,
    rotation_themes,
)
from app.slot_theme import SlotDescriptor, SlotThemeDialog
from app.time_travel import TimeTravelDialog
from app.tray import TrayController, logo_icon, window_icon
from app.widget import ClockWidget
from config import archetypes, constants, defaults, paths, profiling
from config.ui_text import ui
from core.clock_state import build_day_context, build_tick_state
from core.deep_time import (
    canonical_proxy,
    julian_day_of,
    proxy_cycles,
    real_year,
    shift_calendar,
)
from core.moon import chinese_name_of_year
from data.deep_time import DeepTimeRepository
from data.hands import HAND_NAMES, hand_packs
from data.moon_phases import MoonPhaseRepository
from data.rings import ring_presets
from data.seasons import SeasonsRepository
from data.symbolism import SymbolismRepository
from data.translations import TranslationStore, collect_corpus, translate_texts
from render.assets import AssetCache
from render.asset_variants import calendar_wheel_icon_file, warm_working_set
from render.compositor import Compositor
from skins.manifest import HandSpec, HandsSpec, missing_assets


def _letter_metal(position: int, layout: dict, finish: str) -> str:
    """The owner's metal rules (extended with bronze 2026-07-12):
    4-letter layouts — the trio of one metal forms the layout's
    TRIANGLE and the remaining letter wears the ACCENT metal (gold ->
    3 gold + 1 silver; silver -> 3 silver + 1 gold; bronze -> 3 bronze
    + 1 silver); the SEAL wears the ONE finish metal on all six —
    UNLESS the ring preset overrides the triangle (ROADMAP 15b, Mason:
    CANON.md §The Banknote reads the hexagram as TWO triangles, the
    Trinity 12/20/4 and the Union 16/24/8 — `build_skin` passes the
    preset's own `triangle` here when it carries one AND the owner's
    per-preset "Two metals" toggle is on (TASK 3, MASON/ICONS round,
    `_ring_two_metals`), so the Trinity vertices wear the finish metal
    and the Union vertices the accent, the same rule as the 4-letter
    layouts applied to a 3+3 split; DOMY/MORPH's own triangle-less seal
    presets, and any eligible preset with the toggle off, keep the plain
    one-metal reading)."""
    if not layout["triangle"] or position in layout["triangle"]:
        return finish
    return "gold" if finish == "silver" else "silver"


def _ring_two_metals(settings: Settings, card: dict) -> bool:
    """Whether the ACTIVE preset splits into its own 3-3 two-metal
    triangle or wears one finish on all six (TASK 3, MASON/ICONS round,
    owner verdicts 2026-07-19, third batch) — only presets that carry
    their OWN `triangle` override are eligible at all (Mason/Omega/
    Templar today, `data.rings.validate_preset`'s optional card field);
    every other preset (DOMY/MORPH's own 4-letter triangle already
    always applies through the LAYOUT, not this switch; a custom seal
    with no override) is untouched by this toggle and always reads
    False here. The user's stored per-preset choice
    (`Settings.ring_two_metals`) wins; absent, the owner's documented
    per-preset default (`constants.RING_TWO_METALS_DEFAULT`, Mason
    True, everything else False)."""
    if card["triangle"] is None:
        return False
    return settings.ring_two_metals.get(
        card["name"], constants.RING_TWO_METALS_DEFAULT.get(card["name"], False)
    )


def watch_title(settings: Settings, full: bool = False) -> str:
    """The watch's own display NAME (owner INSTRUCTION.txt item 2A,
    R5 MENU REWORK round). A single watch shows just its LOCATION in
    the right-click/tray menus (`full=False`, the default); the FULL
    multi-attribute form backs the tray hover TOOLTIP always —
    f"{location}-{ring_finish} {ring}-{palette label} {pointer}", e.g.
    "Belgrade-Gold DOMY-Family Trinity". With 2+ watches (ADD WATCH
    round) the menu TITLE row and tray-menu title switch to the full
    form too — `WatchController` decides `full` from its own
    `watch_count()` callback at every call site; this function stays
    the ONE place that KNOWS the format, so that round only had to
    loop it, never reinvent it.

    Deliberately UNTRANSLATED (no `tr`): a NAME is an identifier, not
    UI chrome — the same treatment the ring preset name and the
    pointer's own `POINTER_DISPLAY_NAMES` already get (protected proper
    nouns, invariant across languages). The palette label is the
    pointer's own wheel-pair (`constants.POINTER_PALETTE_LABELS`), read
    by the ACTIVE `palette_style` — the SAME table the Design menu's
    pair labels translate from (Rule #5, one source)."""
    if not full:
        return settings.city_name
    pair = constants.POINTER_PALETTE_LABELS.get(
        settings.pointer, constants.POINTER_PALETTE_LABELS["default"]
    )
    palette_label = pair[0 if settings.palette_style == "paint" else 1]
    pointer_name = constants.POINTER_DISPLAY_NAMES[settings.pointer]
    return (
        f"{settings.city_name}-{settings.ring_finish.capitalize()} "
        f"{settings.ring}-{palette_label} {pointer_name}"
    )


def _guard_exclusive_choice(action: QAction, apply) -> None:
    """Wire one member of an EXCLUSIVE QActionGroup so a click on the
    ALREADY-CHECKED member is a no-op (ROADMAP 15h item 8's surviving
    bug, owner screenshot: Planetary/Pantheon both unchecked). Qt's own
    exclusive QActionGroup only auto-unchecks SIBLINGS when a DIFFERENT
    member becomes checked (a `toggled`, not `triggered`, side effect);
    it does nothing to stop the user clicking the sole checked member
    itself, which flips it straight to unchecked and leaves the whole
    group empty. One member must always hold, so a self-uncheck
    restores the check instead of applying anything — the shared fix
    behind `_add_choice_group` (Pointer/Ring/Umbra/…) AND the slot
    menus' `slot_action` (Weekday themes, Complications, astrology
    families, the roster pairs) — every exclusive QActionGroup in the
    app menu routes through one of those two."""
    def _on_triggered(checked: bool) -> None:
        if not checked:
            action.setChecked(True)
            return
        apply()
    action.triggered.connect(_on_triggered)


def _theme_metal(settings: Settings, theme: str) -> str:
    """The METAL a bronze-plate theme wears (owner 2026-07-12):
    follow-the-ring wins, then the per-theme Settings choice, then
    bronze — the art as drawn. Non-metal themes are always bronze."""
    if theme not in constants.METAL_THEMES:
        return "bronze"
    if settings.theme_metal_follow_ring:
        return settings.ring_finish
    return settings.theme_metals.get(theme, "bronze")


class _StayOpenMenu(QMenu):
    """A menu whose CHECKABLE items do not close it (owner menu rework
    2026-07-13: several settings in one visit) — plain actions (Exit,
    Settings…) close as usual; Escape or clicking away closes too.
    Plain actions carrying the "stay_open" property keep it open the
    same way (owner 2026-07-15: chaining Quick Jumps in one visit)."""

    def mouseReleaseEvent(self, event) -> None:
        action = self.actionAt(event.position().toPoint())
        if (
            action is not None
            and action.isEnabled()
            and (action.isCheckable() or action.property("stay_open"))
        ):
            action.trigger()
            event.accept()
            return
        super().mouseReleaseEvent(event)


def _next_rotation_theme(current: str, selected: tuple[str, ...]) -> str:
    """The theme AFTER `current` in the rotation list (cyclic); a
    current theme outside the list starts it from the top."""
    if current in selected:
        return selected[(selected.index(current) + 1) % len(selected)]
    return selected[0]


# FAST TRAVEL (R5b round, owner spec sealed 2026-07-21): the Sun/Moon
# Quick Jump kinds gained an optional PHASE FILTER suffix so the SAME
# `_compute_jump` branch that already answers "next_sun"/"prev_sun"/
# "next_moon"/"prev_moon" (any turning point/phase — the Time Travel
# dialog's own rows, unchanged) also answers the narrower
# "next_sun_solstice"/"next_sun_equinox"/"next_moon_new"/
# "next_moon_full"/"next_moon_quarter" kinds `defaults.
# FAST_TRAVEL_THEMES` builds its `jump_stem`s from — one path, not a
# second copy (Rule #5).
_SUN_MOON_JUMP_PATTERN = re.compile(
    r"^(next|prev)_(sun|moon)(?:_(solstice|equinox|new|full|quarter))?$"
)
# Index into `SeasonsRepository.year_anchors().instants` (the 6 anchors,
# `constants.YEAR_ANCHOR_ANGLES` order: prev Dec solstice, spring
# equinox, summer solstice, autumn equinox, this Dec solstice, next
# spring equinox) — solstices sit at the EVEN indices, equinoxes at the
# ODD.
_SOLSTICE_ANCHOR_INDICES = (0, 2, 4)
_EQUINOX_ANCHOR_INDICES = (1, 3, 5)
# MoonWindow events carry the phase as a FRACTION
# (constants.MOON_PHASE_FRACTIONS): New 0.0, First Quarter 0.25, Full
# 0.5, Third Quarter 0.75.
_QUARTER_MOON_FRACTIONS = (0.25, 0.75)


def _filtered_sun_anchors(
    instants: tuple[datetime, ...], phase_filter: str | None
) -> tuple[datetime, ...]:
    """The year's 6 season anchors, narrowed to solstices/equinoxes only
    when `phase_filter` asks for it — None (the plain "any turning
    point" row) keeps all six, unchanged from before this filter
    existed."""
    if phase_filter == "solstice":
        return tuple(instants[i] for i in _SOLSTICE_ANCHOR_INDICES)
    if phase_filter == "equinox":
        return tuple(instants[i] for i in _EQUINOX_ANCHOR_INDICES)
    return instants


def _filtered_moon_events(
    events: tuple[tuple[datetime, float], ...], phase_filter: str | None
) -> tuple[datetime, ...]:
    """The year's principal-phase events, narrowed to New/Full/Quarter
    only when `phase_filter` asks for it — None keeps every phase,
    unchanged from before this filter existed."""
    if phase_filter == "new":
        return tuple(when for when, fraction in events if fraction == 0.0)
    if phase_filter == "full":
        return tuple(when for when, fraction in events if fraction == 0.5)
    if phase_filter == "quarter":
        return tuple(
            when
            for when, fraction in events
            if fraction in _QUARTER_MOON_FRACTIONS
        )
    return tuple(when for when, _fraction in events)


def _earth_continent(settings: Settings) -> str:
    """The Earth-marker art variant for the ACTIVE location (owner bug
    2026-07-12: the marker was always Europe). The picker's continent
    decides ("Americas" splits by latitude — the art has north and
    south); hand-tuned coordinates without a picked city fall back to
    a coarse geographic estimate."""
    picker = settings.city_path[0] if settings.city_path else None
    if picker == "Americas":
        # Owner rule: Central America and the Caribbean wear the
        # north_america art — only the South America subregion goes south.
        subregion = settings.city_path[1] if len(settings.city_path) > 1 else ""
        return (
            "south_america" if subregion == "South America" else "north_america"
        )
    named = {
        "Africa": "africa", "Asia": "asia",
        "Europe": "europe", "Oceania": "oceania",
    }
    if picker in named:
        return named[picker]
    lat, lon = settings.latitude, settings.longitude
    if lon < -30.0:
        return "north_america" if lat >= 8.5 else "south_america"
    if lat < -10.0 and lon >= 110.0:
        return "oceania"
    if lon < 35.0:
        return "europe" if lat >= 35.0 else "africa"
    if lon < 52.0 and lat < 12.0:
        return "africa"                  # the Horn and Madagascar
    return "europe" if lon < 45.0 and lat >= 40.0 else "asia"


def _resolve_hands(settings: Settings):
    """The chosen HAND PACK (owner spec 2026-07-12) resolved into a
    HandsSpec: image sizes read here (header-only), pivots and z-order
    from the pack's hands.json; tip reach targets from defaults. A
    vanished USER pack falls back to CLASSIC with a stderr note
    (documented — an uninstalled pack must not brick the startup);
    user-pack art is desaturated so the clock tint can recolor it."""
    from PySide6.QtGui import QImageReader

    packs = hand_packs()
    chosen = next(
        (name for name in packs if name.lower() == settings.hands.lower()),
        None,
    )
    if chosen is None:
        print(
            f"hand pack {settings.hands!r} is gone — using CLASSIC",
            file=sys.stderr,
        )
        chosen = "CLASSIC"
    pack = packs[chosen]
    specs = {}
    for hand in HAND_NAMES:
        path = pack["files"][hand]
        size = QImageReader(str(path)).size()
        if size.height() <= 0:
            raise ValueError(f"hand pack {chosen!r}: unreadable {path}")
        x, y = pack["pivots"][hand]
        specs[hand] = HandSpec(
            asset=path,
            natural_height=float(size.height()),
            pivot_y=y,
            pivot_x_fraction=None if x is None else x / size.width(),
        )
    bundled = pack["dir"].parent == paths.assets_dir() / "hands"
    return HandsSpec(
        hour=specs["hours"],
        minute=specs["minutes"],
        second=specs["seconds"],
        minute_reach_fraction=defaults.HAND_MINUTE_REACH_FRACTION,
        second_reach_fraction=defaults.HAND_SECOND_REACH_FRACTION,
        z_order=pack["z_order"],
        desaturate=not bundled,
    )


@profiling.timed("Build skin")
def build_skin(settings: Settings):
    """The ONE render config: DEFAULT_SKIN with the chosen RING PRESET
    CARD (Database/ring_presets.json + the user's custom cards — owner
    spec: {name, positions, letters}, the positions signature picks the
    layout/face), the letter art of the chosen finish, the chosen HAND
    PACK and the user's display choices overlaid."""
    card = ring_presets(settings.custom_rings)[settings.ring]
    layout = constants.RING_LAYOUTS[card["layout"]]
    # A preset may override the seal layout's own (empty) triangle —
    # ROADMAP 15b, Mason's Trinity/Union metal split — but only when the
    # owner's per-preset "Two metals" toggle is actually on (TASK 3,
    # MASON/ICONS round) — see `_letter_metal`'s and `_ring_two_metals`'s
    # docstrings.
    triangle_override = card["triangle"] if _ring_two_metals(settings, card) else None
    metal_layout = {"triangle": triangle_override or layout["triangle"]}
    letters = {}
    letter_art = {}
    letter_metal = {}
    letter_legend = {}
    for position, glyph in zip(card["positions"], card["letters"]):
        hour = position % 24                     # cards say 24, hours say 0
        letters[hour] = glyph
        # The letter art is ALWAYS the gold master — silver/bronze are
        # derived from it AT LOAD (owner 2026-07-19,
        # render.asset_recolor.letter_metal_file), never pre-rendered files.
        letter_art[hour] = (
            defaults.RING_LETTER_ART_DIR / constants.RING_LETTER_FILES[glyph]
        )
        letter_metal[hour] = _letter_metal(position, metal_layout, settings.ring_finish)
        if position in card["legend"]:
            letter_legend[hour] = card["legend"][position]
    # The outer GREAT SEAL MOTTO ARC (TASK 1, owner "može radi"
    # 2026-07-19): the preset's own `motto` card already carries the
    # resolved per-glyph angles (data.rings.validate_preset ->
    # core.motto.motto_glyph_angles) — here we only pair each non-space
    # character with its gold-master asset path (spaces are dropped, so
    # RingLayer's draw loop never has to check for them) and pick the
    # ONE finish the whole inscription wears (the same settings.
    # ring_finish the Trinity-triangle letters use — the motto is read
    # as one continuous inscription, not a seat-by-seat split).
    motto = tuple(
        {
            "text": entry["text"],
            "glyphs": tuple(
                (defaults.RING_LETTER_ART_DIR / constants.RING_LETTER_FILES[char], angle)
                for char, angle in zip(entry["text"], entry["angles"])
                if char != " "
            ),
        }
        for entry in card["motto"]
    )
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        ring=dataclasses.replace(
            defaults.DEFAULT_SKIN.ring,
            asset=defaults.RING_FACE_DIR / layout["face"],
            letters=letters,
            letter_art=letter_art,
            letter_metal=letter_metal,
            letter_legend=letter_legend,
            motto=motto,
            motto_metal=settings.ring_finish,
        ),
        hands=_resolve_hands(settings),
    )
    return apply_display_settings(skin, settings)


def _slot_seconds(settings: Settings) -> bool:
    """Whether any ENABLED slot runs the small-seconds complication
    (owner 2026-07-14) — the big hand yields and its Visible toggle
    grays out."""
    if settings.show_weekday and settings.weekday_slot == "seconds":
        return True
    if settings.show_octa_slot and settings.octa_slot == "seconds":
        return True
    return (
        settings.show_third_slot
        and settings.show_octa_slot
        and settings.third_slot == "seconds"
    )


def _effective_weekday_slot(settings: Settings) -> str:
    """The 1st slot's effective mode. Under the owner's SLOT MATRIX
    (2026-07-14) every mode is real under every pointer — the matrix
    gives it a seat. The single lock: the Seasons with all THREE
    slots up keep the 1st on the weekday unit (owner: mora 1st da
    bude weekday)."""
    if (
        settings.pointer == "cross"
        and settings.show_pointer
        and settings.show_octa_slot
        and settings.show_third_slot
    ):
        return "weekday"
    return settings.weekday_slot


def _classic_slot_theme(settings: Settings) -> tuple[str, str | None]:
    """The (theme, metal) DRESSING the classic weekday unit: normally
    the 1st slot's — except the Seasons/Compass two-slot case where
    only the 2ND is weekday, so the 2nd rides the rotation in its own
    theme (owner 2026-07-15)."""
    if (
        settings.pointer in ("cross", "octa")
        and settings.show_pointer
        and settings.show_weekday
        and settings.show_octa_slot
        and not settings.show_third_slot
        and _effective_weekday_slot(settings) != "weekday"
        and settings.octa_slot == "weekday"
    ):
        theme = settings.info_slot_theme
        return theme, _theme_metal(settings, theme), settings.info_slot_roster
    theme = settings.weekday_theme
    return theme, _theme_metal(settings, theme), settings.weekday_roster


def _themed_weekday_set(base, theme: str, metal: str | None):
    """The weekday unit dressed in `theme` wearing `metal` — the
    SYMBOLISM canon swap (entity-named files, canon display names;
    "planets" keeps the pack's own unit), the hue-SELECTIVE metal at
    render, and the Sunday Servant dual (the COLORED look swaps in
    the sibling variant; owner restructure 2026-07-14)."""
    weekday = base
    if theme != "planets":
        names = defaults.WEEKDAY_THEME_NAMES[theme]
        weekday = dataclasses.replace(
            weekday,
            # PENDING art (documented): a seat whose plate the owner
            # has not generated yet (the Ancient set's Eleusis today)
            # maps to None — the manifest contract draws the
            # procedural colored disc with the name label instead of
            # crashing on a missing file. The candidate path itself
            # comes from the ONE shared resolver (Rule #5 — this used
            # to re-type the theme_dir/colored-folder expression);
            # no `on_date` here — this dict is BAKED once at settings-
            # apply time, so a daily rotation pick would go stale
            # across a multi-day run. `render.layers.draw_weekday_body`
            # re-resolves the LIVE rotation on top of whichever
            # canonical file lands here (same law as its own CONTINENTS
            # live override, right below it).
            bodies={
                body: (
                    candidate
                    if paths.art_file(candidate).exists()
                    else None
                )
                for body in names
                for candidate in (
                    defaults.weekday_theme_body_art(
                        theme, body, colored=(metal == "colored")
                    ),
                )
            },
            body_names=dict(names),
        )
    if metal in defaults.METAL_SWAP_TARGETS:
        weekday = dataclasses.replace(weekday, metal=metal)
    dual_rel = defaults.WEEKDAY_DUAL_FILES[theme]
    if metal == "colored" and theme in constants.METAL_THEMES:
        dual_rel = dual_rel.replace("/primary/", "/colored/")
    dual = defaults.WEEKDAY_ART_DIR / f"{dual_rel}.png"
    if not paths.art_file(dual).exists():
        # PENDING art (documented): a rework can point the dual at a
        # plate the owner has not generated yet (the Creeds' Satanism
        # dual today) — the Sunday runs single-faced until it lands,
        # never wearing a wrong plate.
        dual = None
    return dataclasses.replace(weekday, dual_asset=dual)


def _pantheon_weekday_set(base, theme: str, metal: str | None):
    """The PANTHEON roster's weekday set (owner doctrine 2026-07-15):
    per seat the first EXISTING candidate plate wins with the pantheon
    identity (name + pantheon article); a seat whose art has not
    landed yet falls back to the PLANETARY bundle — file, name and
    article TOGETHER, so a half-generated pantheon never pairs a
    wrong figure with a wrong text. The Sunday dual and its names
    follow the same rule."""
    table = defaults.WEEKDAY_PANTHEON[theme]
    planetary = _themed_weekday_set(base, theme, metal)
    bodies: dict = {}
    names: dict = {}
    articles: dict = {}
    for body in constants.WEEKDAY_BODIES:
        seat = defaults.pantheon_seat(theme, body)
        if seat is not None:
            bodies[body], names[body], articles[body] = seat
        else:
            bodies[body] = planetary.bodies[body]
            names[body] = planetary.body_names[body]
            articles[body] = (
                constants.WEEKDAY_THEME_ARTICLES[theme], body
            )
    dual_rel = table["dual"][0]
    dual = defaults.WEEKDAY_ART_DIR / f"{dual_rel}.png"
    if paths.art_file(dual).exists():
        dual_names = table["dual_names"]
        faces_set = table["articles"]
    else:
        # The pantheon dual's plate has not landed — the WHOLE Sunday
        # pair falls back together (plate, names AND face texts), so
        # the hover never says Hades over a Phaethon plate.
        dual = planetary.dual_asset
        dual_names = defaults.WEEKDAY_DUAL_NAMES[theme]
        faces_set = None
    return dataclasses.replace(
        planetary,
        bodies=bodies,
        body_names=names,
        dual_asset=dual,
        article_set=faces_set,
        body_articles=articles,
        dual_names=dual_names,
    )


def apply_display_settings(skin, settings: Settings):
    """The user's choices win over whatever the skin pack declares:
    the tray display scalars, the opacity overrides (twilight alphas
    scale proportionally with the day alphas) and the custom palette
    for the active (pointer, style). Module-level — testable without
    a controller."""
    # The ART SOURCE switch (owner 2026-07-14: Gemini vs ChatGPT) —
    # every disk boundary resolves canonical paths through it.
    paths.set_art_source(settings.art_source)
    # THE SUBDIAL SET switch (owner decree 2026-07-21, Rsub round) —
    # mirrors the art-source switch above; render.assets.
    # subdial_plate_file reads it directly (its only reader).
    paths.set_subdial_set(settings.subdial_set)
    # THE METAL SHADES (R8a round, owner spec 2026-07-21 night) — same
    # module-global pattern: render.assets._metal_swapped and
    # letter_metal_file read paths.metal_shade(metal) directly.
    paths.set_metal_shade("gold", settings.metal_shade_gold)
    paths.set_metal_shade("bronze", settings.metal_shade_bronze)
    paths.set_metal_shade("silver", settings.metal_shade_silver)
    # THE ARCHETYPE MODE (owner sealed package 2026-07-16): active
    # while the drawn pointer carries an archetype. The overriding
    # itself happens at the RENDER level (render.layers.enabled_slots
    # answers empty), so every slot/weekday setting below stays the
    # user's own — toggling the mode back restores everything.
    archetype_on = (
        settings.archetype_mode
        and settings.show_pointer
        and archetypes.has_archetype(settings.pointer)
    )
    star = skin.star
    if settings.star_alpha is not None:
        star = dataclasses.replace(
            star,
            day_alpha=settings.star_alpha,
            twilight_alpha=settings.star_alpha
            * (star.twilight_alpha / star.day_alpha),
        )
    weekday = skin.weekday_set
    if settings.slot_scale != 1.0:
        # ONE slot size (owner 2026-07-14): the multiplier scales the
        # spec values directly — bodies, subdials, hit regions alike.
        weekday = dataclasses.replace(
            weekday,
            diamond_scale=weekday.diamond_scale * settings.slot_scale,
            center_scale=weekday.center_scale * settings.slot_scale,
        )
    # The CLASSIC unit wears the theme of the slot that DRIVES it
    # (owner 2026-07-15): on the Seasons/Compass with two slots where
    # only the 2nd is weekday, that slot rides the rotation in ITS
    # OWN theme.
    theme, metal, roster = _classic_slot_theme(settings)
    if roster == "pantheon" and theme in defaults.WEEKDAY_PANTHEON:
        weekday = _pantheon_weekday_set(weekday, theme, metal)
    else:
        weekday = _themed_weekday_set(weekday, theme, metal)
    background = skin.background
    if settings.aura_day_alpha is not None or settings.aura_twilight_alpha is not None:
        # The Aura's sunlight and twilight opacities are INDEPENDENT
        # overrides (owner spec) — no coupling ratio between them.
        background = dataclasses.replace(
            background,
            day_alpha=(
                settings.aura_day_alpha
                if settings.aura_day_alpha is not None
                else background.day_alpha
            ),
            twilight_alpha=(
                settings.aura_twilight_alpha
                if settings.aura_twilight_alpha is not None
                else background.twilight_alpha
            ),
        )
    marker = skin.year_marker
    if settings.earth_scale != 1.0 or settings.moon_scale != 1.0:
        marker = dataclasses.replace(
            marker,
            scale=marker.scale * settings.earth_scale,
            moon_scale=marker.moon_scale * settings.moon_scale,
        )
    marker = dataclasses.replace(
        marker,
        moon_hidden_alpha=settings.moon_hidden_alpha,
        # The Earth marker wears the ACTIVE location's continent art
        # (owner bug 2026-07-12: it was pinned to Europe).
        default_variant=_earth_continent(settings),
    )
    return dataclasses.replace(
        skin,
        star=star,
        background=background,
        weekday_set=weekday,
        year_marker=marker,
        pointer=settings.pointer,
        umbra_form=settings.umbra_form,
        umbra_contrast=settings.umbra_contrast,
        palette_style=settings.palette_style,
        calendar_lighting=settings.calendar_lighting,
        calendar_mount=settings.calendar_mount,
        # Aurora is ALWAYS solar-rotated (owner spec 2026-07-12): its
        # bands anchor to the real sun events, so the whole wheel keeps
        # the solar frame regardless of the toggle.
        solar_rotation=(
            True if settings.pointer == "aurora" else settings.solar_rotation
        ),
        octa_slot=settings.octa_slot,
        day_slot_style=settings.day_slot_style,
        info_slot_style=settings.info_slot_style,
        info_slot_theme=settings.info_slot_theme,
        info_slot_metal=_theme_metal(settings, settings.info_slot_theme),
        info_slot_roster=settings.info_slot_roster,
        weekday_slot=_effective_weekday_slot(settings),
        third_slot=settings.third_slot,
        third_slot_style=settings.third_slot_style,
        third_slot_theme=settings.third_slot_theme,
        third_slot_metal=_theme_metal(settings, settings.third_slot_theme),
        third_slot_roster=settings.third_slot_roster,
        # The slots enable IN ORDER (owner 2026-07-14): the third
        # exists only on top of the second.
        show_third_slot=settings.show_third_slot and settings.show_octa_slot,
        earth_style=settings.earth_style,
        weekday_theme=settings.weekday_theme,
        legend=settings.legend,
        era_notation=settings.era_notation,
        show_era_suffix=settings.show_era_suffix,
        third_era=settings.third_era,
        show_earth=settings.show_earth,
        show_moon=settings.show_moon,
        show_weekday=settings.show_weekday,
        show_pointer=settings.show_pointer,
        colorful=settings.colorful,
        # The big seconds hand YIELDS while a slot runs the
        # small-seconds complication (owner 2026-07-14) — except in
        # archetype mode, where the slots are overridden OFF and the
        # big hand returns.
        show_seconds=settings.show_seconds
        and not (_slot_seconds(settings) and not archetype_on),
        archetype_mode=settings.archetype_mode,
        archetype_names=settings.archetype_names,
        earth_label=settings.earth_label,
        show_octa_slot=settings.show_octa_slot,
        show_weekday_names=settings.show_weekday_names,
        show_info_slot_names=settings.show_info_slot_names,
        ring_tint=settings.ring_tint,
        ring_finish=settings.ring_finish,
        subdial_style=settings.subdial_style,
        ring_letter_scale=settings.ring_letter_scale,
        hover_enlarge=settings.hover_enlarge,
        palette_override=settings.palettes.get(
            f"{settings.pointer}_{settings.palette_style}"
        ),
        pointer_saturation=settings.pointer_saturation,
        ring_saturation=settings.ring_saturation,
    )


class WatchController(QObject):
    def __init__(
        self,
        app: QApplication,
        watch_index: int = 1,
        settings_path: Path | None = None,
        watch_count: Callable[[], int] = lambda: 1,
        on_add_watch: Callable[[], None] = lambda: None,
        on_remove_watch: Callable[["WatchController"], None] = lambda watch: None,
        on_exit: Callable[[], None] | None = None,
    ):
        """`watch_index`/`settings_path`/`watch_count`/`on_add_watch`/
        `on_remove_watch`/`on_exit` are the ADD WATCH round's seams to
        [the manager](watch_manager.md) — every default reproduces the
        pre-ADD-WATCH single-watch behavior exactly (watch 1, its own
        `settings.json`, a title that never goes full, Add Watch a
        no-op, Exit quits just this instance), so standalone
        construction (every test in this suite before this round, and
        any test that does not care about multi-watch specifics) needs
        no changes beyond the class rename."""
        super().__init__()
        self._app = app
        self._watch_index = watch_index
        self._watch_count = watch_count
        self._on_add_watch = on_add_watch
        self._on_remove_watch = on_remove_watch
        self._on_exit = on_exit if on_exit is not None else self.quit
        self._store = SettingsStore(settings_path or paths.settings_path(watch_index))
        self._settings = self._load_settings_or_recover()
        self._save_failed = False

        # The cached overlay loads BEFORE the menu builds, so the menu
        # speaks the chosen language from the very first frame (Phase 2);
        # _apply_language below only starts the background fetch for
        # entries the cache does not know yet.
        self._translation_overlay: dict = {}
        if self._settings.language != "en":
            self._translation_overlay = TranslationStore().load(
                self._settings.language
            )
        self._retired_menu = None       # keeps a replaced OPEN menu alive
        # The hidden-mode unlock is SESSION-only (owner 2026-07-15):
        # every launch starts locked — the code must be typed again.
        # Lives BEFORE the menu build: the Report entry reads it.
        self._hidden_unlocked = False
        # DEEP TIME detection (Session 16) also lives BEFORE the menu
        # build — the eclipse jump entries gray without the pack.
        self._deep = DeepTimeRepository.detect()
        # Time Travel state also lives BEFORE the menu build now (fix
        # round E, 2026-07-19): the Quick Jump pole labels read the
        # traveled date via `_effective_travel_date`, which checks
        # `self._simulation`. No simulation can be running yet at
        # startup, but the attribute must EXIST for that check.
        self._simulation: tuple[datetime, astral.Observer] | None = None
        # THE THREE MINI WINDOWS (R5 MENU REWORK item 3) also live
        # BEFORE the menu build now: `_refresh_menu_gating` (called at
        # the end of `_build_menu`) pushes a live gate into whichever
        # of these is currently open, so the attribute must EXIST
        # (None — nothing can be open yet at startup).
        self._design: DesignDialog | None = None
        self._pointer_theme: PointerThemeDialog | None = None
        self._slot_theme: SlotThemeDialog | None = None
        # FAST TRAVEL / LOCATIONS shortcut state (R5b round, owner spec,
        # sealed 2026-07-21) — SESSION-only, like the hidden-mode unlock:
        # the theme/option cursors and the custom-city cursor start fresh
        # on every launch, nothing here is persisted to settings.
        self._fast_travel_theme_index = 0
        self._fast_travel_option_indices: dict[str, int] = {}
        self._jump_city_index = 0
        self._menu = self._build_menu()
        self._legend = LegendPopup()
        self._fast_travel_flash = FastTravelFlash()
        self._widget = ClockWidget(
            self._settings.diameter, self._menu, self._legend, self._show_action
        )
        try:
            self._tray = TrayController(self._menu, logo_icon(self._watch_index))
            # The FULL name form backs the tray hover tooltip from the
            # very first frame (owner INSTRUCTION.txt item 2A) —
            # `_title_label` already exists (set inside the `_build_menu`
            # call above).
            self._tray.set_tooltip(watch_title(self._settings, full=True))
            # Every dialog title bar (Settings, Time Travel, Guide,
            # Encyclopedia, Observatory) inherits this MULTI-RESOLUTION
            # icon instead of the generic Windows icon (owner report
            # 2026-07-11; multi-res + AppUserModelID fix owner
            # screenshot 2026-07-20 — see app.native.set_app_user_model_id
            # for the taskbar-grouping half of that fix); the built EXE
            # additionally gets the M7 ICO on top.
            self._app.setWindowIcon(window_icon())
            # SHOW on tray DOUBLE-CLICK (owner 2026-07-18, ROADMAP 15h):
            # the same "normal" z-mode-only affordance as the menu entry
            # above it.
            self._tray.on_double_click(self._show_if_normal_z_mode)
        except ValueError as error:
            # A broken/missing logo must be SEEN (review finding) — in a
            # windowed build a bare traceback dies with no window at all.
            self._critical_box(
                f"The tray icon could not be loaded:\n{error}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
            raise SystemExit(1) from error

        self._tz = ZoneInfo(self._settings.timezone)
        self._observer = astral.Observer(
            latitude=self._settings.latitude, longitude=self._settings.longitude
        )
        # DEEP TIME (Session 16): the pack detected once above (the ONE
        # resolution point) is injected into both repositories; present
        # → Time Travel spans the full pack coverage and the eclipse
        # jumps are alive; absent → the bundled span with the friendly
        # clamp.
        self._seasons = SeasonsRepository(deep=self._deep)
        self._moon_phases = MoonPhaseRepository(deep=self._deep)
        # Translation overlay (owner spec): apply whatever the cache
        # already holds; missing entries translate in the background.
        self._translation_thread: threading.Thread | None = None
        self._translation_error: Exception | None = None
        self._translation_poller = QTimer(self)
        self._translation_poller.setInterval(1000)
        self._translation_poller.timeout.connect(self._poll_translation)
        # Theme rotation (owner spec 2026-07-12): cycle the selected
        # weekday themes every N minutes.
        self._theme_rotation_timer = QTimer(self)
        self._theme_rotation_timer.timeout.connect(self._rotate_theme)
        self._configure_theme_rotation()
        self._skin = build_skin(self._settings)
        missing = missing_assets(self._skin)
        if missing:
            # Checked up front: a missing asset would otherwise raise
            # inside paintEvent, where Qt swallows it — silently broken dial.
            listing = "\n".join(str(path) for path in missing)
            self._critical_box(
                f"Skin assets are missing:\n{listing}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
            raise SystemExit(1)
        if self._settings.language != "en":
            self._apply_language(start_missing=True)
        self._compositor = Compositor(
            self._skin, AssetCache(), self._symbolism(),
            overlay=self._translation_overlay,
        )
        self._day = None
        # Time Travel: a frozen (moment, observer) rendered instead of the
        # present until the deadline passes (`self._simulation` itself is
        # initialized earlier, before the menu build). Deep travel carries
        # the moment in the 400-year PROXY frame; _sim_cycles is its cycle
        # count (0 = the ordinary frame).
        self._simulation_ends: float = 0.0
        self._sim_cycles: int = 0
        self._widget.set_renderer(self._compositor)
        seconds_hand = (
            self._skin.hands.second is not None
            and self._settings.show_seconds
        ) or _slot_seconds(self._settings)
        self._scheduler = MinuteScheduler(self._on_tick, self, per_second=seconds_hand)
        # Resume-from-sleep and clock/zone changes refresh immediately —
        # the scheduled tick never fired while the machine slept.
        self._power_filter = native.PowerEventFilter(self._on_wake)
        app.installNativeEventFilter(self._power_filter)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(defaults.SETTINGS_WRITE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self._flush_position)
        # The profiling store flushes once per minute (dirty-guarded —
        # measuring itself never costs an I/O) and again at quit.
        self._profiling_timer = QTimer(self)
        self._profiling_timer.setInterval(60_000)
        self._profiling_timer.timeout.connect(profiling.flush)
        self._profiling_timer.start()
        self._widget.moved.connect(self._on_widget_moved)
        # The hidden-mode code listener (owner 2026-07-14): printable
        # keys typed on the focused dial roll through a buffer.
        self._secret_buffer = ""
        self._widget.typed.connect(self._collect_secret)
        # Spacebar over a themed hover target opens the Encyclopedia on
        # that topic's page (owner 2026-07-16, ROADMAP queue #8).
        self._widget.open_encyclopedia.connect(self._open_encyclopedia_at)
        # KEYBOARD SHORTCUTS (R5 MENU REWORK, `defaults.SHORTCUTS`) —
        # fired by the focused `ClockWidget.keyPressEvent`; dispatched
        # by action_id in `_on_shortcut`.
        self._widget.shortcut_triggered.connect(self._on_shortcut)
        # NON-MODAL Encyclopedia/Guide/Observatory (ITEM 1, R4 owner
        # instruction batch 2026-07-20): these three now `.show()`
        # instead of `.exec()` — the dial stays fully interactive
        # (hover, right-click, move) while any of them is open. Each
        # attribute holds the ONE live instance of its dialog type (or
        # None); a second open request RAISES it instead of stacking a
        # duplicate (the Encyclopedia's old re-entrancy guard becomes
        # "focus the live one" — a SPACE jump while it is open now
        # NAVIGATES it to the new target, `EncyclopediaDialog.navigate_
        # to`, a strict improvement over the old modal no-op). Settings
        # and Time Travel are UNCHANGED — they still `.exec()` (they
        # mutate state transactionally and must not be left half-applied
        # by a stray close).
        self._encyclopedia: EncyclopediaDialog | None = None
        self._observatory: ObservatoryDialog | None = None
        self._guide: GuideDialog | None = None
        # THE THREE MINI WINDOWS (R5 MENU REWORK item 3) — the SAME
        # non-modal, one-live-instance lifecycle as the trio above, see
        # design_window.md/pointer_theme.md/slot_theme.md for why they
        # are LIVE-APPLY rather than transactional — are initialized
        # EARLIER, before the first `_build_menu()` call (its gating
        # pass reads them).

        # In click-through mode the window receives no mouse input, so the
        # hover tooltips are driven by polling the global cursor instead.
        self._hover_poller = QTimer(self)
        self._hover_poller.setInterval(defaults.CLICK_THROUGH_HOVER_POLL_MS)
        self._hover_poller.timeout.connect(self._poll_hover)
        self._last_hover_tip: str | None = None
        # Hover article warm sweeps (owner 2026-07-18): the generation
        # counter obsoletes a running sweep when the skin or day it was
        # warming is replaced.
        self._hover_warm_generation = 0

    # --- ADD WATCH identity (owner INSTRUCTION.txt item 2, sealed 2026-07-21) ---

    @property
    def watch_index(self) -> int:
        """This watch's own 1-based slot number — the anchor (1) can
        never be removed, and every tray-color/settings-file rule
        (`app.tray.logo_icon`, `config.paths.settings_path`) reads it."""
        return self._watch_index

    @property
    def settings_path(self) -> Path:
        """This watch's own settings file — the manager deletes it on
        Remove Watch (`discard()` tears down the LIVE watch first)."""
        return self._store.path

    def refresh_title(self) -> None:
        """Public hook for the manager: re-render the TITLE row and the
        tray tooltip after the watch ROSTER changes (Add/Remove Watch)
        — the short/full split depends on `watch_count()`, which just
        moved for every surviving watch, not only this one."""
        self._refresh_watch_title()

    def _confirm_remove_watch(self) -> None:
        """The Remove/Close entry's own click handler (watches 2+ only
        — `_build_menu` never builds the action on watch 1): one plain
        Yes/No confirm, no further dialogs (owner spec) — a Yes calls
        the manager's `remove_watch(self)`, which tears this watch down
        and deletes its settings file; `self._on_remove_watch` defaults
        to a no-op for standalone/test use (no manager attached)."""
        box = QMessageBox(
            QMessageBox.Icon.Question, constants.APP_NAME,
            self._ui("Remove this watch? Its settings file will be deleted."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        box.setDefaultButton(QMessageBox.StandardButton.No)
        box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        if box.exec() == QMessageBox.StandardButton.Yes:
            self._on_remove_watch(self)

    # --- Lifecycle --------------------------------------------------------------

    def run(self) -> None:
        self._on_tick(clock_jumped=False)   # first frame BEFORE show()
        # Reserve the window margin for the ACTIVE skin (the compositor is
        # built in __init__, bypassing _install_skin) and apply the
        # visibility Z mode BEFORE the first show() — window flags must be
        # set before show() on Windows (owner 2026-07-17).
        self._widget.set_dial_diameter(
            self._settings.diameter,
            defaults.dial_window_margin_fraction(self._skin),
        )
        self._widget.set_z_mode(self._settings.z_mode)
        self._position_widget()
        self._widget.show()
        # TRUE topmost is re-asserted natively after the first show (owner
        # 2026-07-17): Qt's StaysOnTop hint alone degrades to normal
        # stacking once the window has been shown.
        self._widget.reassert_z_order()
        self._tray.show()
        self._scheduler.start()
        # windowHandle() exists only after show(); a monitor/DPI change
        # invalidates every rasterized cache.
        self._last_dpr = self._widget.devicePixelRatioF()
        self._widget.windowHandle().screenChanged.connect(self._on_screen_changed)
        if self._settings.click_through:
            self._widget.set_click_through(True)
            self._hover_poller.start()
        # The WORKING SET warms in the background (owner 2026-07-15:
        # full-res originals ship, the downscaled dial copies build at
        # start) — a no-op once every derived file exists. The HOVER
        # ARTICLE sweep chains right after it on the same thread (owner
        # 2026-07-18, asked twice): every article the dial can speak
        # today pre-builds slowly, image by image, so the user's FIRST
        # hover is instant.
        threading.Thread(target=self._warm_caches, daemon=True).start()

    def _warm_caches(self) -> None:
        warm_working_set(progress=print)
        self._warm_hover_articles()

    def _start_hover_warm(self) -> None:
        """Obsolete any running sweep and start a fresh one — called on
        skin install and day change (a new skin/day speaks new articles;
        a warm re-run costs header reads only)."""
        self._hover_warm_generation += 1
        threading.Thread(
            target=self._warm_hover_articles, daemon=True
        ).start()

    def _warm_hover_articles(self) -> None:
        compositor = self._compositor
        generation = self._hover_warm_generation
        compositor.warm_hover_articles(
            float(self._settings.diameter),
            should_stop=lambda: self._hover_warm_generation != generation
            or self._compositor is not compositor,
            progress=print,
        )

    def _teardown_windows(self) -> None:
        """Close every open dialog, stop the scheduler and the
        debounced save timer, hide the tray — the shared first half of
        `_prepare_quit()` (Exit: also saves) and `discard()` (Remove
        Watch, ADD WATCH round: never saves — the settings file is
        about to be deleted). The non-modal sextet (ITEM 1, R4 + the
        three R5 mini windows) can now be open at teardown time; close
        them explicitly instead of leaving them to the process
        teardown, so their own `finished` handlers (and
        WA_DeleteOnClose) run the ordinary way rather than being cut
        off mid-flight."""
        self._widget.mark_closing()
        for dialog in (
            self._encyclopedia, self._observatory, self._guide,
            self._design, self._pointer_theme, self._slot_theme,
        ):
            if dialog is not None:
                dialog.close()
        self._scheduler.stop()
        if self._save_timer.isActive():
            self._save_timer.stop()
        self._tray.hide()

    def discard(self) -> None:
        """Remove Watch's own teardown (ADD WATCH round, owner
        INSTRUCTION.txt item 2, sealed 2026-07-21): identical window/
        scheduler/tray teardown as Exit but deliberately skips the
        save — [the manager](watch_manager.md) deletes this watch's
        settings file right after this call returns, so writing it
        first would just recreate what is about to be removed."""
        self._teardown_windows()

    def _prepare_quit(self) -> None:
        """Everything Exit needs from THIS watch except the final
        shared `app.quit()` — split out (ADD WATCH round) so the
        manager's `quit_all()` can run it for every watch before
        quitting the process exactly once."""
        self._teardown_windows()
        self._capture_position()
        try:
            self._store.save(self._settings)
        except OSError as error:
            # Last chance to be seen — the tray balloon would die with the
            # process, so this one failure mode gets a blocking dialog.
            self._critical_box(
                f"Settings could not be saved on exit:\n{self._store.path}\n\n{error}",
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok,
            )
        profiling.flush()

    def quit(self) -> None:
        """Standalone Exit (no manager attached — every test in this
        suite predating ADD WATCH, and the default `on_exit` a bare
        `WatchController` falls back to): this watch's own teardown,
        then quit the process."""
        self._prepare_quit()
        self._app.quit()

    # --- Clock ------------------------------------------------------------------

    @profiling.timed("Tick")
    def _on_tick(self, clock_jumped: bool) -> None:
        if self._simulation is not None and monotonic() >= self._simulation_ends:
            self._simulation = None
            self._sim_cycles = 0
            self._day = None                # force the rebuild back to the present
        if self._simulation is not None:
            now, observer = self._simulation
            cycles = self._sim_cycles
        else:
            now = datetime.now(self._tz)
            observer = self._observer
            cycles = 0
        day_key = (now.date(), now.utcoffset())
        first_day_build = self._day is None
        if first_day_build or self._day.cache_key != day_key or clock_jumped:
            try:
                with profiling.measure("Day context"):
                    # The repositories take the REAL astronomical year
                    # (deep travel un-shifts the proxy frame) and answer
                    # in the SAME frame — canonical_proxy and the repos
                    # share proxy_cycles, so the anchors always bracket.
                    astro_year = real_year(now.year, cycles)
                    # The eclipse catalog (ROADMAP 15h item 11) is the
                    # ONLY Deep Time feed with no bundled fallback —
                    # absent the pack, no eclipse ever draws (the
                    # documented absence rule, Rule #1).
                    eclipses = (
                        self._deep.eclipses_near(now, cycles)
                        if self._deep is not None
                        else ()
                    )
                    self._day = build_day_context(
                        now,
                        observer,
                        self._seasons.year_anchors(astro_year),
                        self._moon_phases.moon_window(astro_year),
                        eclipses,
                    )
                    if cycles:
                        # Stamp the frame on the context (display sites
                        # un-shift years; the illumination evaluates at
                        # the real epoch) and rename the Chinese year
                        # from the REAL year — a 400-year shift moves
                        # the sexagenary cycle by 40.
                        self._day = dataclasses.replace(
                            self._day,
                            deep_cycles=cycles,
                            chinese_name=chinese_name_of_year(
                                real_year(self._day.chinese_start.year, cycles)
                            ),
                        )
            except Exception as error:
                # Bundled data unreadable, out of coverage, or schema-
                # malformed (KeyError/TypeError from a bad year entry) —
                # nothing the app can do; die visibly, never tick a wrong
                # dial and never freeze silently.
                self._critical_box(
                    f"Astronomical data unavailable:\n{error!r}",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok,
                )
                raise SystemExit(1) from error
            self._compositor.set_day(self._day)
            if not first_day_build:
                # A NEW day (or travel jump) speaks new articles — the
                # startup chain already covers the first build.
                self._start_hover_warm()
        self._widget.set_tick(build_tick_state(now, self._day))

    def _on_wake(self) -> None:
        """Resume-from-sleep / system clock change: full refresh now."""
        self._on_tick(clock_jumped=True)

    def _on_screen_changed(self) -> None:
        """Qt fires this for ANY monitor crossing — but two identical
        screens (the owner's 2x 4K/32") share one pixel density, and
        crossing between them must cost NOTHING. The rasterized caches
        only die when the DPR actually changes."""
        dpr = self._widget.devicePixelRatioF()
        if dpr == self._last_dpr:
            return
        self._last_dpr = dpr
        self._compositor.invalidate()
        self._widget.update()

    # --- Settings ---------------------------------------------------------------

    def _load_settings_or_recover(self) -> Settings:
        try:
            return self._store.load()
        except SettingsCorruptError as error:
            choice = self._critical_box(
                (
                    f"The settings file is corrupt and cannot be read:\n"
                    f"{error.path}\n\n{error.cause}\n\n"
                    f"Reset settings (the broken file is kept as a .bak backup)?"
                ),
                QMessageBox.StandardButton.Reset | QMessageBox.StandardButton.Abort,
                QMessageBox.StandardButton.Reset,
            )
            if choice != QMessageBox.StandardButton.Reset:
                raise SystemExit(1) from error
            try:
                self._store.quarantine()
                fresh = Settings()
                self._store.save(fresh)
            except OSError as os_error:
                self._critical_box(
                    f"Settings could not be reset:\n{self._store.path}\n\n{os_error}",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok,
                )
                raise SystemExit(1) from os_error
            return fresh
        except OSError as error:
            # Unreadable (locked / permission denied) is not corrupt — the
            # file is left untouched and defaults are used for this session.
            choice = self._critical_box(
                (
                    f"The settings file cannot be read:\n"
                    f"{self._store.path}\n\n{error}\n\n"
                    f"Continue with default settings for this session "
                    f"(the file is left untouched)?"
                ),
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Abort,
                QMessageBox.StandardButton.Ok,
            )
            if choice != QMessageBox.StandardButton.Ok:
                raise SystemExit(1) from error
            return Settings()

    def _on_widget_moved(self) -> None:
        self._save_timer.start()

    def _collect_secret(self, char: str) -> None:
        """Typing HIDDEN_MODE_SECRET on the focused dial unlocks the
        hidden extras — the Four Greetings on the ring letters, in the
        Encyclopedia's Trinity topic, and, bound to their CANONICAL
        home (ROADMAP queue #6), a second reading in the Encyclopedia's
        Seasons topic. The unlock lives for THIS SESSION only (owner
        2026-07-15: every launch asks for the code again — nothing
        persists)."""
        if self._hidden_unlocked:
            return
        secret = constants.HIDDEN_MODE_SECRET
        self._secret_buffer = (self._secret_buffer + char)[-len(secret):]
        if self._secret_buffer != secret:
            return
        self._secret_buffer = ""
        self._hidden_unlocked = True
        self._compositor.set_hidden_unlocked(True)
        self._report_action.setVisible(True)   # the Report above Exit
        self._tray.notify(
            self._ui("Hidden mode unlocked"),
            self._ui(
                "The Four Greetings await in the Encyclopedia — "
                "Trinity and Seasons."
            ),
            critical=False,
        )

    # --- Keyboard shortcuts (R5 MENU REWORK, `defaults.SHORTCUTS`) -------------

    #: Ordered exactly like the Weekday submenu (owner menu rework
    #: 2026-07-13): Planets first and flat, then the kinship groups.
    _WEEKDAY_THEME_ORDER = defaults.WEEKDAY_MENU_TOP + tuple(
        key for _title, keys in defaults.WEEKDAY_MENU_GROUPS for key in keys
    )
    #: The 4 Complication modes, in `constants.SLOT_COMPLICATION_TITLES`'s
    #: own dict order (Digital Time -> Date -> Day length -> Seconds) —
    #: the R5b SLOTS shortcuts (Ctrl+1/2/3) cycle through exactly this.
    _SLOT_COMPLICATION_ORDER = tuple(constants.SLOT_COMPLICATION_TITLES)

    def _on_shortcut(self, action_id: str) -> None:
        """Dispatch one `defaults.SHORTCUTS` entry (owner "OSMISLITI ŠTA
        SVE"; R5b FINAL MAP round for the SLOTS/FAST TRAVEL/LOCATIONS
        additions — the full map is designed and pinned by
        `tests/test_shortcuts.py`). Every shortcut needs the dial to
        hold keyboard focus (`ClockWidget.keyPressEvent` is the only
        source of this signal)."""
        handlers = {
            "cycle_ring": self._cycle_ring,
            "cycle_weekday_theme": self._cycle_weekday_theme,
            "cycle_slots": self._cycle_slots,
            "open_encyclopedia": lambda: self._open_encyclopedia_at(None, 0),
            "open_guide": self._open_guide,
            "open_settings": self._open_settings,
            "open_observatory": self._open_observatory,
            "open_time_travel": self._open_time_travel,
            "return_to_now": self._end_simulation,
            "toggle_archetype": self._toggle_archetype_shortcut,
            "cycle_slot1_complication": lambda: self._cycle_slot_complication(1),
            "cycle_slot2_complication": lambda: self._cycle_slot_complication(2),
            "cycle_slot3_complication": lambda: self._cycle_slot_complication(3),
            "cycle_slot1_theme": lambda: self._cycle_slot_weekday_theme(1),
            "cycle_slot2_theme": lambda: self._cycle_slot_weekday_theme(2),
            "cycle_slot3_theme": lambda: self._cycle_slot_weekday_theme(3),
            "fast_travel_theme": self._cycle_fast_travel_theme,
            "fast_travel_option": self._cycle_fast_travel_option,
            "fast_travel_past": lambda: self._step_fast_travel(-1),
            "fast_travel_future": lambda: self._step_fast_travel(1),
            "location_north_pole": lambda: self._jump_to_place("north_pole"),
            "location_south_pole": lambda: self._jump_to_place("south_pole"),
            "location_greenwich": lambda: self._jump_to_place("greenwich"),
            "location_prev_city": lambda: self._cycle_jump_city(-1),
            "location_next_city": lambda: self._cycle_jump_city(1),
        }
        handlers[action_id]()

    def _cycle_ring(self) -> None:
        """Ctrl+R: the next Ring preset, alphabetically — the SAME
        order the Design window's Ring tab lists them in. `_set_ring`
        runs `_install_skin`, which refreshes any open mini window in
        place (`_refresh_open_mini_windows`) — no separate call needed
        here."""
        names = sorted(ring_presets(self._settings.custom_rings))
        current = names.index(self._settings.ring)
        self._set_ring(names[(current + 1) % len(names)])

    def _weekday_theme_on_diamonds(self) -> bool:
        """True when the 1st Slot's `weekday_theme` is the theme
        actually PAINTED on the star's diamonds right now (R5b round,
        owner spec for Ctrl+W: "ONLY when the theme is displayed on the
        DIAMONDS"). Four conditions: the pointer HAS diamonds at all
        (Aurora/Calendar draw none — `constants.POINTER_ARM_HALF_ANGLE_DEG`'s
        own membership is the existing test for that), the Pointer
        element is visible, the 1st Slot is visible, and its EFFECTIVE
        mode is "weekday" (`_effective_weekday_slot`) rather than a
        digital/astrology complication. Under this last condition
        `_classic_slot_theme` ALWAYS returns `weekday_theme` — its own
        Seasons/Compass redirect to `info_slot_theme` fires ONLY when
        `_effective_weekday_slot` is NOT "weekday" (see that function's
        docstring) — so nothing else can be silently wearing a
        DIFFERENT theme on the diamonds while this predicate holds."""
        settings = self._settings
        return (
            settings.pointer in constants.POINTER_ARM_HALF_ANGLE_DEG
            and settings.show_pointer
            and settings.show_weekday
            and _effective_weekday_slot(settings) == "weekday"
        )

    def _cycle_weekday_theme(self) -> None:
        """Ctrl+W: the next Weekday theme (the 1st Slot's own —
        `_WEEKDAY_THEME_ORDER`, the Weekday grid's own order); the
        roster/metal the theme is already wearing stays untouched, like
        clicking the plain theme tile. STRICT NO-OP (R5b round, owner
        spec) unless `_weekday_theme_on_diamonds()` — cycling a theme
        nobody can see would be a silent, invisible state change.
        `_set_weekday_theme` runs `_install_skin`, which refreshes the
        Pointer Theme / Slot Theme windows in place when either happens
        to be open."""
        if not self._weekday_theme_on_diamonds():
            return
        order = self._WEEKDAY_THEME_ORDER
        current = order.index(self._settings.weekday_theme)
        self._set_weekday_theme(order[(current + 1) % len(order)])

    # --- SLOTS shortcuts (R5b round, owner spec) --------------------------------

    def _slot_active(self, index: int) -> bool:
        """Whether Slot `index` (1/2/3) is currently active/visible —
        the SAME effective enablement `apply_display_settings` renders
        with (the 3rd only counts on top of the 2nd, `show_third_slot
        and show_octa_slot` — the "slots enable IN ORDER" rule)."""
        settings = self._settings
        if index == 1:
            return settings.show_weekday
        if index == 2:
            return settings.show_octa_slot
        return settings.show_third_slot and settings.show_octa_slot

    def _slot_mode_state(self, index: int) -> tuple[str, Callable[[str], None]]:
        """(current mode, setter) for Slot `index`'s own MODE field —
        the SAME setters `_slot_descriptors()` wires the Slot Theme
        window's own mode picker through (Rule #5)."""
        settings = self._settings
        if index == 1:
            return settings.weekday_slot, (
                lambda mode: self._set_display_choice("weekday_slot", mode)
            )
        if index == 2:
            return settings.octa_slot, self._set_south_slot
        return settings.third_slot, self._set_third_slot

    def _slot_theme_state(self, index: int) -> tuple[str, Callable[[str], None]]:
        """(current weekday theme, setter) for Slot `index` — the setter
        ALSO switches that slot's mode to "weekday" as a side effect
        (the SAME `_set_weekday_theme`/`_set_south_slot`/
        `_set_third_slot` behavior the Slot Theme window's own theme
        picker already relies on), so cycling the theme via the
        keyboard is also how you switch a slot INTO weekday-display
        mode with one repeated press."""
        settings = self._settings
        if index == 1:
            return settings.weekday_theme, self._set_weekday_theme
        if index == 2:
            return settings.info_slot_theme, (
                lambda theme: self._set_south_slot("weekday", theme=theme)
            )
        return settings.third_slot_theme, (
            lambda theme: self._set_third_slot("weekday", theme=theme)
        )

    def _cycle_slot_complication(self, index: int) -> None:
        """Ctrl+1/2/3: the next Complication (Digital Time -> Date ->
        Day length -> Seconds, `_SLOT_COMPLICATION_ORDER`) in Slot
        `index` — a strict no-op while that slot is not active/visible
        (`_slot_active`). A slot currently showing a NON-complication
        (Weekday/Zodiac/Ascendant/Chinese) starts the cycle from the
        top, the SAME "outside the list starts fresh" rule
        `_next_rotation_theme` already applies to theme rotation."""
        if not self._slot_active(index):
            return
        mode, setter = self._slot_mode_state(index)
        setter(_next_rotation_theme(mode, self._SLOT_COMPLICATION_ORDER))

    def _cycle_slot_weekday_theme(self, index: int) -> None:
        """Ctrl+Alt+1/2/3: the next Weekday theme in Slot `index`
        (`_WEEKDAY_THEME_ORDER`) — a strict no-op while that slot is not
        active/visible (`_slot_active`). Unlike Ctrl+W this carries NO
        "already displaying a theme" guard: the setter itself switches
        the slot's mode to "weekday" (see `_slot_theme_state`), so one
        press both picks the next theme AND makes it visible — the
        direct route into weekday-display mode for slots 2/3, which
        have no dedicated "show weekday bodies here" toggle of their
        own beyond picking a theme."""
        if not self._slot_active(index):
            return
        theme, setter = self._slot_theme_state(index)
        setter(_next_rotation_theme(theme, self._WEEKDAY_THEME_ORDER))

    # --- FAST TRAVEL shortcuts (R5b round, owner spec) --------------------------

    def _fast_travel_theme(self) -> dict:
        return defaults.FAST_TRAVEL_THEMES[self._fast_travel_theme_index]

    def _fast_travel_option_index(self, theme_id: str) -> int:
        """The REMEMBERED option cursor for `theme_id` (owner spec: each
        theme keeps its own pick across Ctrl+[ switches) — 0 (the
        theme's first option) for a theme never touched this session."""
        return self._fast_travel_option_indices.get(theme_id, 0)

    def _cycle_fast_travel_theme(self) -> None:
        """Ctrl+[: the next Fast Travel theme (Sun -> Moon -> Calendar
        -> Sun, `defaults.FAST_TRAVEL_THEMES`'s own order) — flashes the
        NEW theme's logo (owner spec: every Ctrl+[ / Ctrl+] change
        flashes)."""
        self._fast_travel_theme_index = (
            self._fast_travel_theme_index + 1
        ) % len(defaults.FAST_TRAVEL_THEMES)
        self._flash_fast_travel()

    def _cycle_fast_travel_option(self) -> None:
        """Ctrl+]: the next OPTION inside the ACTIVE theme — flashes it
        (owner spec)."""
        theme = self._fast_travel_theme()
        count = len(theme["options"])
        index = self._fast_travel_option_index(theme["id"])
        self._fast_travel_option_indices[theme["id"]] = (index + 1) % count
        self._flash_fast_travel()

    def _flash_fast_travel(self) -> None:
        """Show the ACTIVE (theme, option)'s icon + option text above
        THIS watch's own dial (owner spec: "per-watch — the focused
        watch flashes its own" — trivially true here since a shortcut
        only ever reaches the FOCUSED widget's `_on_shortcut` to begin
        with). Calendar carries no `icon_key` (Sun/Moon keep their
        eclipse glyphs, untouched this round) — its icon is COMPUTED
        instead (`render.asset_variants.calendar_wheel_icon_file`, Rule #19),
        killing the plain 📅 fallback the owner asked to retire."""
        theme = self._fast_travel_theme()
        option = theme["options"][self._fast_travel_option_index(theme["id"])]
        if theme["id"] == "calendar":
            icon_path = calendar_wheel_icon_file(defaults.FAST_TRAVEL_FLASH_ICON_PX)
        else:
            icon_key = theme["icon_key"]
            icon_path = (
                defaults.icon_path(icon_key) if icon_key is not None else None
            )
        self._fast_travel_flash.flash(
            self._widget, icon_path, theme["emoji"], self._ui(option["title"])
        )

    def _step_fast_travel(self, direction: int) -> None:
        """Ctrl+minus/Ctrl+plus: one step past (`direction=-1`)/future
        (`direction=1`) along the ACTIVE (theme, option) — riding the
        SAME `_compute_jump` kinds Quick Jump uses (owner spec:
        "chaining law — each jump starts from the active simulation",
        `_active_simulation_or_now`). No flash on a step (owner spec
        scopes the flash to the Ctrl+[ / Ctrl+] PICKERS only)."""
        theme = self._fast_travel_theme()
        option = theme["options"][self._fast_travel_option_index(theme["id"])]
        kind = f"{'next' if direction > 0 else 'prev'}_{option['jump_stem']}"
        moment, observer, cycles = self._active_simulation_or_now()
        self._apply_jump(moment, observer, cycles, kind)

    # --- LOCATIONS shortcuts (R5b round, owner spec) -----------------------------

    def _jump_to_place(self, kind: str) -> None:
        """Ctrl+Up/Down/Space: jump the ACTIVE simulation (or, absent
        one, the live now) to `kind` ("north_pole"/"south_pole"/
        "greenwich") — the SAME `_compute_jump` kinds the Time Travel
        dialog's own place buttons use (Rule #5), applied straight to
        the live dial instead of a dialog draft."""
        moment, observer, cycles = self._active_simulation_or_now()
        self._apply_jump(moment, observer, cycles, kind)

    def _cycle_jump_city(self, direction: int) -> None:
        """Ctrl+Left/Right: step through the user's own CUSTOM Quick
        Jump cities (owner spec) — a STRICT no-op with none defined (no
        index change, no jump). `_jump_city_index` names the city THIS
        press lands on (shown first, THEN advanced for the NEXT press)
        — so the very FIRST press, either direction, lands on the
        FIRST custom city (index 0, the natural "nothing chosen yet"
        starting point) and only the SECOND press actually reveals which
        direction was held. Session-only cursor, like the Fast Travel
        theme/option cursors."""
        cities = self._settings.jump_cities
        if not cities:
            return
        count = len(cities)
        city = cities[self._jump_city_index % count]
        self._jump_city_index = (self._jump_city_index + direction) % count
        moment, observer, cycles = self._active_simulation_or_now()
        self._apply_jump(moment, observer, cycles, "city", dict(city))

    def _cycle_slots(self) -> None:
        """Ctrl+N: the number of visible Slots, 0 → 1 → 2 → 3 → 0 (the
        SAME 1 → 2 → 3 chain the menu's own ordinals enforce — cycling
        can only ever pass through legal states). `_install_skin`
        refreshes the Slot Theme window in place when it happens to be
        open."""
        settings = self._settings
        count = (
            int(settings.show_weekday)
            + int(settings.show_weekday and settings.show_octa_slot)
            + int(
                settings.show_weekday and settings.show_octa_slot
                and settings.show_third_slot
            )
        )
        target = (count + 1) % 4
        self._settings = replace(
            self._settings,
            show_weekday=target >= 1,
            show_octa_slot=target >= 2,
            show_third_slot=target >= 3,
        )
        self._install_skin(build_skin(self._settings))
        self._refresh_menu_gating()
        self._flush_position()

    def _toggle_archetype_shortcut(self) -> None:
        """Ctrl+A: the SAME toggle as the menu's own Archetype entry — a
        no-op where it is unavailable (Aurora/Calendar, or the Pointer
        element hidden), never a silent state change."""
        settings = self._settings
        available = settings.show_pointer and archetypes.has_archetype(
            settings.pointer
        )
        if not available:
            return
        self._set_display_choice("archetype_mode", not settings.archetype_mode)
        # The menu's OWN checkable Archetype action is a SEPARATE view
        # of the same state (the shortcut bypasses its `toggled` signal
        # entirely) — mirror it without re-entering the handler: block
        # signals, set, unblock.
        self._archetype_action.blockSignals(True)
        self._archetype_action.setChecked(self._settings.archetype_mode)
        self._archetype_action.blockSignals(False)

    def _capture_position(self) -> None:
        self._settings = replace(
            self._settings,
            window_x=self._widget.x(),
            window_y=self._widget.y(),
        )

    def _flush_position(self) -> None:
        self._capture_position()
        try:
            self._store.save(self._settings)
        except OSError as error:
            print(f"settings save failed: {error}", file=sys.stderr)
            # One balloon per failure streak — a dialog for every debounced
            # save during a drag would storm the user.
            if not self._save_failed:
                self._save_failed = True
                self._tray.notify(
                    self._ui("Settings could not be saved"),
                    f"{self._store.path}\n{error}",
                )
        else:
            self._save_failed = False

    def _position_widget(self) -> None:
        if self._settings.window_x is not None and self._settings.window_y is not None:
            remembered = QRect(
                self._settings.window_x,
                self._settings.window_y,
                self._widget.width(),
                self._widget.height(),
            )
            # Any attached screen showing part of the dial is good enough —
            # clamping to the primary screen would destroy multi-monitor
            # placements on every restart.
            for screen in QGuiApplication.screens():
                if screen.availableGeometry().intersects(remembered):
                    self._widget.move(remembered.topLeft())
                    return
        # First run, or the remembered spot is on no attached screen
        # (monitors unplugged/rearranged): center on the primary screen.
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self._widget.move(
            screen.center().x() - self._widget.width() // 2,
            screen.center().y() - self._widget.height() // 2,
        )

    # --- Menu ---------------------------------------------------------------------

    def _symbolism(self) -> SymbolismRepository:
        """The article source with the active language's overlay laid
        over the English originals (owner spec: we ship only English;
        the user's machine translates once and caches)."""
        return SymbolismRepository(overlay=self._translation_overlay or None)

    def _refresh_watch_title(self) -> None:
        """Keep the menu's TITLE header and the tray hover tooltip in
        sync with the live settings (owner INSTRUCTION.txt item 2A) —
        called from `_install_skin`, the ONE choke point every
        ring/pointer/palette/location change already runs through
        (Rule #5), rather than a full menu rebuild: a stay-open menu
        must never close just because its own header text changed
        underneath it. A fresh `_build_menu()` (Settings OK, language
        switch) replaces `_title_label` wholesale and calls this again
        via the `_install_skin` it always runs first — either path ends
        with a correct label. Public entry point: `refresh_title()`
        (ADD WATCH round — the manager calls it on every SURVIVING
        watch after the roster changes)."""
        self._title_label.setText(
            watch_title(self._settings, full=self._watch_count() >= 2)
        )
        self._tray.set_tooltip(watch_title(self._settings, full=True))

    def _refresh_open_mini_windows(self) -> None:
        """Keep any OPEN Design/Pointer Theme/Slot Theme window in step
        with the live settings — called from `_install_skin` (the SAME
        choke point `_refresh_watch_title` uses) so a change made
        through ANY path (a keyboard shortcut, Settings, a pick inside
        a DIFFERENT one of the three windows) never leaves an already-
        open window showing a stale pick. Each window's own `refresh()`
        already runs after a pick made THROUGH it (Rule #5 — this is
        the belt to that suspender for every OTHER path)."""
        if self._design is not None:
            self._design.refresh(self._settings, self._design_setters())
        if self._pointer_theme is not None:
            self._pointer_theme.refresh(self._settings.weekday_theme)
        if self._slot_theme is not None:
            self._slot_theme.refresh(self._slot_descriptors())

    def _install_skin(self, skin) -> None:
        """Swap the rendered skin: fresh compositor, current day kept."""
        self._skin = skin
        self._refresh_watch_title()
        self._refresh_open_mini_windows()
        # Re-reserve the transparent window margin from the LIVE settings
        # (owner slike 1–3, 2026-07-17): earth/moon scale, hover-enlarge
        # and letter scale all feed it, so the window re-sizes to fit
        # exactly (no waste, no clip) on every skin install — the ONE
        # point where a size/hover/letter slider takes effect.
        self._widget.set_dial_diameter(
            self._settings.diameter,
            defaults.dial_window_margin_fraction(skin),
        )
        self._compositor = Compositor(
            skin, AssetCache(), self._symbolism(),
            overlay=self._translation_overlay,
        )
        self._compositor.set_hidden_unlocked(self._hidden_unlocked)
        self._widget.set_renderer(self._compositor)
        if self._day is not None:
            self._compositor.set_day(self._day)
        # The Seconds element switch also changes the tick cadence —
        # and so does the small-seconds slot (owner 2026-07-14).
        self._scheduler.set_per_second(
            (skin.hands.second is not None and self._settings.show_seconds)
            or _slot_seconds(self._settings)
        )
        self._widget.update()
        if self._day is not None:
            # The new skin speaks new articles (theme, slots, pointer) —
            # re-warm them in the background (owner 2026-07-18).
            self._start_hover_warm()

    def _set_ring(self, ring: str) -> None:
        if ring == self._settings.ring:
            return
        self._settings = replace(self._settings, ring=ring)
        self._install_skin(build_skin(self._settings))
        self._flush_position()
        # The "Two metals" toggle's own eligibility/checked state
        # depends on the ACTIVE preset (TASK 3) — re-gate in place, the
        # same stay-open pattern every other menu re-sync uses.
        self._refresh_menu_gating()

    def _set_ring_two_metals(self, checked: bool) -> None:
        """TASK 3 (MASON/ICONS round): the active preset's own metal-
        split choice, stored keyed by preset name
        (`Settings.ring_two_metals`, like `theme_metals`)."""
        metals = dict(self._settings.ring_two_metals)
        metals[self._settings.ring] = checked
        self._settings = replace(self._settings, ring_two_metals=metals)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_hands(self, hands: str) -> None:
        if hands == self._settings.hands:
            return
        self._settings = replace(self._settings, hands=hands)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_weekday_badge(self, mode: str, style: str) -> None:
        """Day slot content + its OWN style in one click (owner
        2026-07-12: the slots are independent — this never touches the
        info slot's look)."""
        self._settings = replace(
            self._settings, weekday_slot=mode, day_slot_style=style
        )
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _metal_updates(self, theme: str, metal: str | None) -> dict:
        """The settings delta of an EXPLICIT metal pick (either slot's
        Weekday submenu): remembers the theme's metal and releases
        follow-the-ring, otherwise the ring finish would silently
        override it. Empty when no metal was chosen."""
        if metal is None:
            return {}
        metals = dict(self._settings.theme_metals)
        metals[theme] = metal
        return {"theme_metals": metals, "theme_metal_follow_ring": False}

    def _set_south_slot(
        self, mode: str, style: str | None = None,
        theme: str | None = None, metal: str | None = None,
        roster: str | None = None,
    ) -> None:
        """Info slot content + its OWN style/theme/metal/roster in one
        click (owner 2026-07-12: independent of the day slot's look)."""
        updates: dict = {"octa_slot": mode}
        if style is not None:
            updates["info_slot_style"] = style
        if theme is not None:
            updates["info_slot_theme"] = theme
            updates.update(self._metal_updates(theme, metal))
        if roster is not None:
            updates["info_slot_roster"] = roster
        self._settings = replace(self._settings, **updates)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_third_slot(
        self, mode: str, style: str | None = None,
        theme: str | None = None, metal: str | None = None,
        roster: str | None = None,
    ) -> None:
        """The 3rd slot's content (owner 2026-07-14) — the same shape
        as the other two, its own style/theme/metal/roster."""
        updates: dict = {"third_slot": mode}
        if style is not None:
            updates["third_slot_style"] = style
        if theme is not None:
            updates["third_slot_theme"] = theme
            updates.update(self._metal_updates(theme, metal))
        if roster is not None:
            updates["third_slot_roster"] = roster
        self._settings = replace(self._settings, **updates)
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_weekday_theme(
        self, theme: str, metal: str | None = None,
        roster: str | None = None,
    ) -> None:
        """Day slot back to the WEEKDAY BODIES wearing `theme` (owner
        menu 2026-07-12: the theme list lives inside Day slot ▸ Weekday,
        so picking a theme also picks the mode; bronze-plate themes
        pick their metal in the same click, pantheon themes their
        roster)."""
        self._settings = replace(
            self._settings,
            weekday_slot="weekday",
            weekday_theme=theme,
            **({"weekday_roster": roster} if roster is not None else {}),
            **self._metal_updates(theme, metal),
        )
        self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _configure_theme_rotation(self) -> None:
        """Start/stop the rotation timer per the settings (called at
        startup and after every Settings OK). The GROUP dropdown picks
        what cycles (owner 2026-07-14: a kinship family, the custom
        checkbox list, or none at all); the ORDER is shuffled fresh
        each time (owner spec 2026-07-12: never the same sequence
        twice)."""
        self._rotation_order = list(rotation_themes(self._settings))
        random.shuffle(self._rotation_order)
        if len(self._rotation_order) >= 2:
            self._theme_rotation_timer.start(
                self._settings.theme_rotation_minutes * 60 * 1000
            )
        else:
            self._theme_rotation_timer.stop()

    def _rotate_theme(self) -> None:
        """One rotation step: the next theme of the SHUFFLED order goes
        live (and the menu checkmarks follow)."""
        self._set_display_choice(
            "weekday_theme",
            _next_rotation_theme(
                self._settings.weekday_theme,
                tuple(self._rotation_order),
            ),
        )
        # The timer can fire while the user is browsing the menu —
        # close and RETAIN the replaced one so Qt never deletes a
        # visible popup (stay-open menus, owner 2026-07-13).
        retired = self._menu
        self._menu = self._build_menu()
        self._widget.set_menu(self._menu)
        self._widget.set_show_action(self._show_action)
        self._tray.set_menu(self._menu)
        retired.close()
        self._retired_menu = retired

    def _set_display_choice(self, key: str, value) -> None:
        """Shared setter behind every display choice: persist and
        REBUILD the render config from scratch — a bare scalar replace
        is not enough for choices that swap assets (the weekday theme
        replaces the body images inside apply_display_settings; a
        scalar-only update left the planets on screen — owner bug
        report, FINAL.txt #6)."""
        if getattr(self._settings, key) == value:
            return
        self._settings = replace(self._settings, **{key: value})
        self._install_skin(build_skin(self._settings))
        self._flush_position()
        if key in (
            "pointer", "show_weekday", "show_pointer",
            "show_octa_slot", "show_third_slot", "archetype_mode",
        ):
            # These move the whole enablement matrix (the South slot's
            # availability, the weekday-badge availability, Aurora's
            # image-only modes, the Solar rotation lock, the enable
            # chain and the slot check marks) — re-gray the gated
            # entries IN PLACE (owner 2026-07-13: switching the
            # pointer or an element must not close the open menu).
            # `show_weekday_names` dropped OUT of this list (Session
            # 21-C): the menu twin it needed resyncing against is gone —
            # Archetype names is its own Settings switch now
            # (`archetype_names`), so the buried Weekday ▸ Names toggle
            # needs no special re-gating beyond the ordinary slot gating.
            self._refresh_menu_gating()

    def _set_earth_label(self, mode: str, checked: bool) -> None:
        """FOUR mutually exclusive Earth label options (owner 2026-07-18,
        ROADMAP 15h: Date / Weekday / Date & Weekday / Full Date, stored
        as the single `earth_label` enum): `checked=True` selects `mode`
        outright, `checked=False` (clicking the ALREADY active pill
        again) turns the label off entirely. One skin install for the
        whole change; the Design window's own `refresh()` re-reads the
        result fresh (R5 MENU REWORK — no controller-held toggle
        widgets to mirror any more)."""
        new_mode = mode if checked else "off"
        if self._settings.earth_label != new_mode:
            self._settings = replace(self._settings, earth_label=new_mode)
            self._install_skin(build_skin(self._settings))
        self._flush_position()

    def _set_visible(self, key: str, checked: bool) -> None:
        """One Visible toggle (owner 2026-07-17; renamed from Elements,
        R5 MENU REWORK item E): the shared display setter, then the
        top-level Visible check follows (it shows only while every
        entry is on)."""
        self._set_display_choice(key, checked)
        self._refresh_visible_check()

    def _refresh_visible_check(self) -> None:
        """The Visible ordinal is checked ONLY when every entry in the
        dropdown is on (owner 2026-07-17, ROADMAP 15e)."""
        self._visible_menu_action.setChecked(
            all(getattr(self._settings, key) for _, key in self._visible_toggles)
        )

    def _toggle_all_visible(self) -> None:
        """Clicking the Visible top-level entry (owner 2026-07-17): all
        on → all off, otherwise → all on. One skin install for the whole
        batch; the child checkboxes and the gating follow."""
        keys = [key for _, key in self._visible_toggles]
        target = not all(getattr(self._settings, key) for key in keys)
        changes = {
            key: target for key in keys if getattr(self._settings, key) != target
        }
        if not changes:
            self._refresh_visible_check()
            return
        self._settings = replace(self._settings, **changes)
        for action, key in self._visible_toggles:
            # Mirror the children without re-entering their handlers.
            action.blockSignals(True)
            action.setChecked(target)
            action.blockSignals(False)
        self._install_skin(build_skin(self._settings))
        # Toggling the Pointer/Seconds elements moves the gating matrix.
        self._refresh_menu_gating()
        self._refresh_visible_check()
        self._flush_position()

    def _refresh_menu_gating(self) -> None:
        """Recompute every gated FLAT menu entry from the CURRENT
        settings without rebuilding (the stay-open menu keeps its
        window; only the gray states move). R5 MENU REWORK shrank this
        considerably: everything that used to gate a WIDGET INSIDE the
        old Design/Slot submenu chains (the palette-style label swap,
        the Calendar-lighting visibility, the Two-metals toggle, the
        1 → 2 → 3 slot-enable chain, the Seasons three-slot lock) now
        lives INSIDE the three mini windows themselves, recomputed
        fresh on every `_build()`/`refresh()` call there instead of
        gated in place here — what remains gated at the FLAT top level
        is the Show/Archetype/Solar-rotation toggles, the big seconds
        hand, and the three window-opening entries' own availability."""
        settings = self._settings
        # SHOW (owner 2026-07-18): meaningless outside "normal" z-mode —
        # HIDDEN there, not grayed.
        self._show_action.setVisible(settings.z_mode == "normal")
        # THE ARCHETYPE MODE gating (owner sealed package 2026-07-16):
        # the toggle grays where no archetype exists — Aurora and the
        # Calendar — and with the Pointer element off (no diamonds, no
        # figures).
        archetype_available = (
            settings.show_pointer
            and archetypes.has_archetype(settings.pointer)
        )
        archetype_on = archetype_available and settings.archetype_mode
        self._archetype_action.setEnabled(archetype_available)
        # A seated small-seconds slot cannot silence the big hand
        # while the archetype mode overrides the slots.
        self._seconds_gate_action.setEnabled(
            not (_slot_seconds(settings) and not archetype_on)
        )
        self._solar_rotation_action.setEnabled(
            settings.pointer != "aurora"
        )
        self._refresh_pointer_theme_gate()
        self._refresh_slot_theme_gate()

    def _refresh_pointer_theme_gate(self) -> None:
        """The Pointer Theme entry/window's own availability (item 3B,
        agent interpretation — see pointer_theme.md): grayed while
        Archetype mode overrides the diamonds, while the Pointer
        element itself is hidden in Visible, or while the 1st Slot
        (the layer this window themes) is off."""
        settings = self._settings
        archetype_on = (
            settings.show_pointer
            and archetypes.has_archetype(settings.pointer)
            and settings.archetype_mode
        )
        if archetype_on:
            reason = self._ui(
                "The Archetype mode is on — the diamonds carry its own figures."
            )
        elif not settings.show_pointer:
            reason = self._ui("The Pointer is hidden in Visible.")
        elif not settings.show_weekday:
            reason = self._ui("The 1st Slot is off — nothing wears this theme.")
        else:
            reason = ""
        available = not reason
        self._pointer_theme_action.setEnabled(available)
        self._pointer_theme_action.setToolTip(reason)
        if self._pointer_theme is not None:
            self._pointer_theme.set_gate(available, reason)

    def _refresh_slot_theme_gate(self) -> None:
        """The Slot Theme entry/window's own availability (item 3C,
        owner spec: "moze da bude GRAY ako nisu vidljivi slotovi") —
        grayed when NO slot is visible at all (the 1 → 2 → 3 chain
        means the 1st is the bootstrap: `Ctrl+N`, `_cycle_slots`, turns
        it back on) or while Archetype mode overrides every slot."""
        settings = self._settings
        archetype_on = (
            settings.show_pointer
            and archetypes.has_archetype(settings.pointer)
            and settings.archetype_mode
        )
        if archetype_on:
            reason = self._ui(
                "The Archetype mode is on — the diamonds carry its own figures."
            )
        elif not settings.show_weekday:
            reason = self._ui("No Slot is visible.")
        else:
            reason = ""
        available = not reason
        self._slot_theme_action.setEnabled(available)
        self._slot_theme_action.setToolTip(reason)
        if self._slot_theme is not None:
            self._slot_theme.set_gate(available, reason)

    def _add_choice_group(
        self, menu: QMenu, submenu: QMenu, options, current, setter, disabled=()
    ) -> list[QAction]:
        """One exclusive check-group appended to `submenu`: options are
        (value, label) pairs; values in `disabled` render grayed out.
        Returns the created actions (owner 2026-07-16: some groups need
        to be re-grayed in place later, e.g. Paint/Light on trio/cross)."""
        group = QActionGroup(menu)
        group.setExclusive(True)
        actions = []
        for value, label in options:
            action = QAction(label, menu)
            action.setCheckable(True)
            action.setChecked(value == current)
            action.setEnabled(value not in disabled)
            _guard_exclusive_choice(action, lambda chosen=value: setter(chosen))
            group.addAction(action)
            submenu.addAction(action)
            actions.append(action)
        return actions

    def _submenu(self, parent: QMenu, title: str) -> QMenu:
        """One stay-open submenu attached to `parent` (owner menu
        rework 2026-07-13: every level keeps checkable picks open)."""
        submenu = _StayOpenMenu(title, parent)
        parent.addMenu(submenu)
        return submenu

    def _add_choice_submenu(self, menu: QMenu, title: str, options, current, setter) -> QMenu:
        """One exclusive check-group submenu: options are (value, label)."""
        submenu = self._submenu(menu, title)
        self._add_choice_group(menu, submenu, options, current, setter)
        return submenu

    def _add_toggle(
        self, menu: QMenu, title: str, checked: bool, setter, tooltip: str | None = None
    ) -> QAction:
        """One checkable on/off action appended to `menu`."""
        action = QAction(title, menu)
        action.setCheckable(True)
        action.setChecked(checked)
        if tooltip is not None:
            action.setToolTip(tooltip)
        action.toggled.connect(setter)
        menu.addAction(action)
        return action

    def _ui(self, text: str) -> str:
        """The active language's form of a chrome string (Phase 2)."""
        return ui(self._translation_overlay, text)

    @staticmethod
    def _labeled(text: str, action_id: str) -> str:
        """R5 doubt 4 FOLLOW-UP (R5b round, owner spec): appends the
        shortcut's own "Ctrl+X" combo to a flat menu entry's text via a
        tab character — Qt's own convention for a right-aligned
        accelerator-style hint in a QMenu row, WITHOUT wiring a real
        competing `QAction.setShortcut` (every shortcut already fires
        through `ClockWidget.keyPressEvent` -> `shortcut_triggered`; a
        second Qt-level shortcut on the SAME key would double-dispatch).
        Only entries with a DIRECT, unambiguous 1:1 shortcut (the five
        dialog openers + Archetype) use this — the cycling/Fast-Travel/
        Location shortcuts live inside mini windows or have no menu
        surface of their own at all."""
        return f"{text}\t{defaults.shortcut_display(action_id)}"

    def _build_menu(self) -> QMenu:
        menu = _StayOpenMenu()
        settings = self._settings
        tr = self._ui
        # TITLE ROW (owner INSTRUCTION.txt item 2A, R5 MENU REWORK): the
        # watch's own name heads BOTH the right-click and the tray menu
        # (they share this ONE QMenu) — a passive styled header, never
        # clickable/checkable (Rule #8 alternative: a disabled QAction
        # still hover-highlights on some platforms; a QWidgetAction
        # hosting a QLabel reads unambiguously as a header, the SAME
        # pattern the Size slider row below already uses). A single
        # watch shows just its location (`full=False`); ADD WATCH round
        # (owner: "Title ne treba pun naziv ako nema potrebe"): with 2+
        # watches alive (`self._watch_count()`, the manager's live
        # roster size) this row switches to the full multi-attribute
        # form too — the tray HOVER tooltip below stays full regardless
        # of count, always has.
        title_label = QLabel(watch_title(settings, full=self._watch_count() >= 2))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-weight: 700; font-size: 13px; padding: 6px 12px;"
            f"color: {defaults.THEME_COLORS['accent']};"
        )
        title_action = QWidgetAction(menu)
        title_action.setDefaultWidget(title_label)
        menu.addAction(title_action)
        self._title_label = title_label
        menu.addSeparator()
        # ADD WATCH (owner INSTRUCTION.txt item 2, sealed 2026-07-21):
        # "na vrhu... ispod TITLE info" — directly below the title row,
        # on EVERY watch. Seeds a new watch from THIS watch's current
        # settings ([the manager](watch_manager.md)'s `add_watch`);
        # `self._on_add_watch` defaults to a no-op for standalone/test
        # use (no manager attached) and is reassigned by the manager
        # right after construction — the lambda below re-reads it
        # fresh on every click, never binding a stale target.
        add_watch_action = QAction(f"➕ {tr('Add Watch')}", menu)
        add_watch_action.triggered.connect(lambda: self._on_add_watch())
        menu.addAction(add_watch_action)
        # REMOVE THIS WATCH (same round, architecture guidance): watch 1
        # is the anchor and never offers it — only watches 2+ do. One
        # plain Yes/No confirm (`_confirm_remove_watch`), no further
        # dialogs (owner spec).
        if self._watch_index != 1:
            remove_watch_action = QAction(f"➖ {tr('Remove this Watch')}", menu)
            remove_watch_action.triggered.connect(self._confirm_remove_watch)
            menu.addAction(remove_watch_action)
        menu.addSeparator()
        # SHOW (owner 2026-07-18, ROADMAP 15h, Session 21-C): in
        # "normal" z-mode the dial rides above other windows ONLY while
        # focused — the owner loses it under other windows otherwise.
        # This entry raises it on demand; MEANINGLESS in "bottom" (never
        # above anything) and "top" (already always above), so it is
        # HIDDEN there, not merely grayed — `_refresh_menu_gating`
        # updates its visibility on every z_mode change. Sits at the
        # very TOP of the menu (owner: "na samom vrhu").
        self._show_action = QAction(f"👁️ {tr('Show')}", menu)
        self._show_action.triggered.connect(self._show_if_normal_z_mode)
        self._show_action.setVisible(settings.z_mode == "normal")
        menu.addAction(self._show_action)
        menu.addSeparator()
        # Menu rework (owner 2026-07-13): emoji-fronted top level —
        # Design / Primary Slot / Secondary Slot / Elements, then the
        # three switches, the four windows, Exit — and checkable picks
        # keep the menu OPEN. DESIGN = how the instrument looks
        # (Pointer, Ring, Umbra | Hands, Earth | Size).
        # DESIGN / POINTER THEME / SLOT THEME (R5 MENU REWORK item 3,
        # owner spec — the exact "4-5 branching levels stack one over
        # another in a screen corner" complaint that opened this round,
        # `UV/DESIGN/Meni One over Another.png`): each ONE flat entry
        # now opens its own mini WINDOW (`app.design_window`,
        # `app.pointer_theme`, `app.slot_theme`) instead of the deep
        # nested chains this used to be (Rule #6 — no both-paths; the
        # windows are LIVE-APPLY, exactly like the chains they replace,
        # see each module's own docstring for the modal-vs-non-modal
        # justification). Gating lives in `_refresh_menu_gating` /
        # `_refresh_pointer_theme_gate` / `_refresh_slot_theme_gate`.
        design_action = QAction(f"🎨 {tr('Design…')}", menu)
        design_action.triggered.connect(self._open_design)
        menu.addAction(design_action)
        self._pointer_theme_action = QAction(
            f"✨ {tr('Pointer Theme…')}", menu
        )
        self._pointer_theme_action.triggered.connect(self._open_pointer_theme)
        menu.addAction(self._pointer_theme_action)
        self._slot_theme_action = QAction(f"🥇 {tr('Slot Theme…')}", menu)
        self._slot_theme_action.triggered.connect(self._open_slot_theme)
        menu.addAction(self._slot_theme_action)
        # Visible (owner spec; renamed from Elements, R5 MENU REWORK
        # item E — Rule #6, every reference below renamed with it):
        # plain on/off switches — the slots enable INSIDE their own
        # submenus now (owner 2026-07-14), so only the star, its
        # colors, the two markers and the seconds hand remain.
        visible_menu = self._submenu(menu, f"🧩 {tr('Visible')}")
        self._visible_toggles: list = []
        for key, label, tip in (
            (
                "show_pointer", tr("Pointer"),
                tr("The star diamonds. Off: the Aura colors stay, only the "
                   "pointer disappears."),
            ),
            (
                "colorful", tr("Colorful"),
                tr("The Aura palette hues. Off: the day and twilight arcs "
                   "are drawn as plain white transparency."),
            ),
            (
                "show_earth", tr("Earth"),
                tr("The Earth marker riding the year wheel and showing "
                   "the date."),
            ),
            (
                "show_moon", tr("Moon"),
                tr("The Moon marker riding its cycle and showing the phase."),
            ),
            (
                "show_seconds", tr("Seconds"),
                tr("The seconds hand. Off: it is not drawn and the dial "
                   "ticks once per minute."),
            ),
        ):
            action = self._add_toggle(
                visible_menu, label, getattr(settings, key),
                lambda checked, key=key: self._set_visible(key, checked),
                tip,
            )
            self._visible_toggles.append((action, key))
            if key == "show_seconds":
                # The big hand yields while a slot runs the
                # small-seconds complication (owner 2026-07-14).
                self._seconds_gate_action = action
                action.setEnabled(not _slot_seconds(settings))
        # Clicking the top-level Visible entry flips ALL of them at once
        # (owner 2026-07-17, ROADMAP 15e): the check shows ONLY when every
        # entry is on; a click while all-on turns them all off, otherwise
        # it turns them all on. The submenu still opens on hover/arrow.
        self._visible_menu_action = visible_menu.menuAction()
        self._visible_menu_action.setCheckable(True)
        self._visible_menu_action.triggered.connect(
            lambda checked=False: self._toggle_all_visible()
        )
        self._refresh_visible_check()
        menu.addSeparator()
        self._add_toggle(
            menu, f"📜 {tr('Legend')}", settings.legend,
            lambda checked: self._set_display_choice("legend", checked),
            tr("All hover texts. Off: the dial shows nothing on hover — "
               "combined with Click-through it has zero interaction."),
        )
        self._solar_rotation_action = self._add_toggle(
            menu, f"🔆 {tr('Solar rotation')}", settings.solar_rotation,
            lambda checked: self._set_display_choice("solar_rotation", checked),
            tr("On: the star points at true solar noon. Off: Star, Aura and "
               "Umbra stand upright (12/24 at the top) for reading exact "
               "planet and season positions."),
        )
        # Aurora is ALWAYS solar-rotated (owner spec 2026-07-12) — the
        # bands anchor to the real sun events, the toggle has no say.
        self._solar_rotation_action.setEnabled(settings.pointer != "aurora")
        # THE ARCHETYPE MODE (owner sealed package 2026-07-16): the
        # stay-open checkable beside Solar rotation — the diamonds fill
        # with the active wheel's archetype figures, the hour hand
        # lights the one whose hour-space it is in, and the weekday
        # model and all three slots step aside (render-level override —
        # the slot settings stay put). Grayed on Aurora/Calendar.
        self._archetype_action = self._add_toggle(
            menu,
            self._labeled(f"🎭 {tr('Archetype')}", "toggle_archetype"),
            settings.archetype_mode,
            lambda checked: self._set_display_choice(
                "archetype_mode", checked
            ),
            tr(
                "The diamonds carry the active wheel's archetype "
                "figures; the hour hand lights the one whose "
                "hour-space it is in. The weekday model and the slots "
                "step aside while it runs."
            ),
        )
        # ARCHETYPE NAMES moved into Settings ▸ Display as its OWN
        # independent switch (owner 2026-07-18, ROADMAP 15h, Session
        # 21-C: "nemoj ispod nego u Settings — ON/OFF") — the menu twin
        # that used to sit here, writing the shared `show_weekday_names`
        # key, is GONE; `archetype_names` is its own setting now,
        # `ArchetypeLayer` reads it directly.
        # (The Earth-weekday toggle moved to Design ▸ Earth as a general
        # option, owner 2026-07-17 slika 10 — it works in both modes now.)
        self._add_toggle(
            menu, f"🖱️ {tr('Click-through')}", self._settings.click_through,
            self._set_click_through,
            tr("The dial takes no clicks at all (they pass to the desktop); "
               "hover info still works. Turn it back off here in the tray."),
        )
        menu.addSeparator()
        settings_action = QAction(
            self._labeled(f"⚙️ {tr('Settings…')}", "open_settings"), menu
        )
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)
        encyclopedia = QAction(
            self._labeled(f"🏛️ {tr('Encyclopedia…')}", "open_encyclopedia"),
            menu,
        )
        encyclopedia.triggered.connect(
            lambda: self._open_encyclopedia_at(None, 0)
        )
        menu.addAction(encyclopedia)
        observatory = QAction(
            self._labeled(f"🔭 {tr('Observatory…')}", "open_observatory"),
            menu,
        )
        observatory.triggered.connect(self._open_observatory)
        menu.addAction(observatory)
        guide = QAction(
            self._labeled(f"📖 {tr('Guide…')}", "open_guide"), menu
        )
        guide.triggered.connect(self._open_guide)
        menu.addAction(guide)
        time_travel = QAction(
            self._labeled(f"🕰️ {tr('Time Travel…')}", "open_time_travel"),
            menu,
        )
        time_travel.triggered.connect(self._open_time_travel)
        menu.addAction(time_travel)
        # QUICK JUMP DIED HERE (owner rounds 2026-07-14/15; Session 16
        # rework, slika 12; RETIRED R5 MENU REWORK item 4 — Rule #6, no
        # both-paths): the deep 4-5-level submenu chain this used to be
        # (`UV/DESIGN/RIGHT CLICK MENU.txt`, `Meni One over Another.png`
        # — the exact complaint that opened this round) is GONE — every
        # motion it held now lives as a ROW inside the Time Travel
        # window itself (item 3A, `app.time_travel._build_jump_section`,
        # wired through `_dialog_jump`/`_compute_jump`), which the entry
        # above already opens.
        menu.addSeparator()
        # The hidden REPORT (owner 2026-07-15): function efficiency
        # statistics, visible only after the session unlock — above
        # Exit ("iznad Izlaza").
        self._report_action = QAction(f"📊 {tr('Report')}", menu)
        self._report_action.setVisible(self._hidden_unlocked)
        self._report_action.triggered.connect(self._open_report)
        menu.addAction(self._report_action)
        exit_action = QAction(f"🚪 {tr('Exit')}", menu)
        # Exit is PROCESS-WIDE (ADD WATCH round: unlike the per-watch
        # Remove entry above, it closes every watch, not just this
        # one) — `self._on_exit` defaults to `self.quit` (standalone
        # use); the manager passes its own `quit_all` instead.
        exit_action.triggered.connect(self._on_exit)
        menu.addAction(exit_action)
        # Normalize every gated state from the CURRENT settings — the
        # one gating implementation serves the fresh build and the
        # in-place refresh alike (Rule #5; the archetype/slot/palette
        # gates all live there).
        self._refresh_menu_gating()
        return menu

    def _open_report(self) -> None:
        # The hidden debug Report stays MODAL — an admin/statistics
        # snapshot the owner never asked to leave open alongside the
        # dial (item 1's non-modal trio is Encyclopedia/Guide/
        # Observatory only).
        ReportDialog(self._translation_overlay).exec()

    def _open_guide(self) -> None:
        """Open (or raise) the [Guide](guide.md) — NON-MODAL (ITEM 1, R4
        owner instruction batch 2026-07-20): `.show()` instead of
        `.exec()`, so the dial stays interactive while it is open. A
        second open request RAISES the ONE live instance instead of
        stacking a duplicate."""
        if self._guide is not None:
            self._guide.raise_()
            self._guide.activateWindow()
            return
        dialog = GuideDialog(self._translation_overlay)
        dialog.finished.connect(self._on_guide_closed)
        self._guide = dialog
        dialog.show()

    def _on_guide_closed(self, _result: int = 0) -> None:
        self._guide = None

    # --- The three mini windows (R5 MENU REWORK item 3) -------------------------

    def _open_design(self) -> None:
        """Open (or raise) the [Design Window](design_window.md) —
        NON-MODAL, LIVE-APPLY (see its own docstring): a second open
        request raises the ONE live instance."""
        if self._design is not None:
            self._design.raise_()
            self._design.activateWindow()
            return
        dialog = DesignDialog(
            self._settings, self._design_setters(),
            overlay=self._translation_overlay,
            stay_on_top=self._settings.z_mode == "top",
        )
        dialog.finished.connect(self._on_design_closed)
        self._design = dialog
        dialog.show()

    def _on_design_closed(self, _result: int = 0) -> None:
        self._design = None

    def _design_setters(self) -> dict:
        """One setter per Design tab, each wrapped so a pick BOTH
        applies (through the SAME `_set_*` methods the old menu chain
        used, Rule #5) AND refreshes the open window with the new
        live state — the window itself is stateless between picks."""
        def wrap(setter):
            def wrapped(*args, **kwargs):
                setter(*args, **kwargs)
                if self._design is not None:
                    self._design.refresh(self._settings, self._design_setters())
            return wrapped

        return {
            "pointer": wrap(lambda v: self._set_display_choice("pointer", v)),
            "palette_style": wrap(
                lambda v: self._set_display_choice("palette_style", v)
            ),
            "calendar_lighting": wrap(
                lambda v: self._set_display_choice("calendar_lighting", v)
            ),
            "calendar_mount": wrap(
                lambda v: self._set_display_choice("calendar_mount", v)
            ),
            "ring": wrap(self._set_ring),
            "ring_finish": wrap(
                lambda v: self._set_display_choice("ring_finish", v)
            ),
            "ring_two_metals": wrap(self._set_ring_two_metals),
            "umbra_form": wrap(
                lambda v: self._set_display_choice("umbra_form", v)
            ),
            "umbra_contrast": wrap(
                lambda v: self._set_display_choice("umbra_contrast", v)
            ),
            "subdial_style": wrap(
                lambda v: self._set_display_choice("subdial_style", v)
            ),
            "hands": wrap(self._set_hands),
            "earth_style": wrap(
                lambda v: self._set_display_choice("earth_style", v)
            ),
            "earth_label": wrap(self._set_earth_label),
            "diameter": wrap(self._set_diameter),
        }

    def _open_pointer_theme(self) -> None:
        """Open (or raise) the [Pointer Theme](pointer_theme.md) window
        — NON-MODAL, LIVE-APPLY: a second open request raises the ONE
        live instance."""
        if self._pointer_theme is not None:
            self._pointer_theme.raise_()
            self._pointer_theme.activateWindow()
            return
        dialog = PointerThemeDialog(
            self._settings.weekday_theme, self._pick_pointer_theme,
            overlay=self._translation_overlay,
            stay_on_top=self._settings.z_mode == "top",
        )
        dialog.finished.connect(self._on_pointer_theme_closed)
        self._pointer_theme = dialog
        self._refresh_pointer_theme_gate()
        dialog.show()

    def _on_pointer_theme_closed(self, _result: int = 0) -> None:
        self._pointer_theme = None

    def _pick_pointer_theme(self, theme: str) -> None:
        self._set_weekday_theme(theme)
        if self._pointer_theme is not None:
            self._pointer_theme.refresh(theme)

    def _open_slot_theme(self) -> None:
        """Open (or raise) the [Slot Theme](slot_theme.md) window —
        NON-MODAL, LIVE-APPLY: a second open request raises the ONE
        live instance."""
        if self._slot_theme is not None:
            self._slot_theme.raise_()
            self._slot_theme.activateWindow()
            return
        dialog = SlotThemeDialog(
            self._slot_descriptors(),
            overlay=self._translation_overlay,
            stay_on_top=self._settings.z_mode == "top",
        )
        dialog.finished.connect(self._on_slot_theme_closed)
        self._slot_theme = dialog
        self._refresh_slot_theme_gate()
        dialog.show()

    def _on_slot_theme_closed(self, _result: int = 0) -> None:
        self._slot_theme = None

    def _slot_descriptors(self) -> tuple:
        """One `SlotDescriptor` per slot, built fresh from the LIVE
        settings — each carries its OWN setter, wrapped so a pick
        BOTH applies (through the SAME `_set_weekday_theme`/
        `_set_south_slot`/`_set_third_slot`/`_set_display_choice`
        methods the old menu chain used, Rule #5) AND re-supplies the
        window with a fresh triple."""
        settings = self._settings

        def wrap(setter):
            def wrapped(*args, **kwargs):
                setter(*args, **kwargs)
                if self._slot_theme is not None:
                    self._slot_theme.refresh(self._slot_descriptors())
            return wrapped

        return (
            SlotDescriptor(
                index=1, title="1st Slot",
                mode_value=settings.weekday_slot,
                style_value=settings.day_slot_style,
                theme_value=settings.weekday_theme,
                roster_value=settings.weekday_roster,
                names_value=settings.show_weekday_names,
                enabled_value=settings.show_weekday,
                set_mode=wrap(
                    lambda mode: self._set_display_choice("weekday_slot", mode)
                ),
                set_style_mode=wrap(self._set_weekday_badge),
                set_weekday=wrap(self._set_weekday_theme),
                set_names=wrap(
                    lambda checked: self._set_display_choice(
                        "show_weekday_names", checked
                    )
                ),
            ),
            SlotDescriptor(
                index=2, title="2nd Slot",
                mode_value=settings.octa_slot,
                style_value=settings.info_slot_style,
                theme_value=settings.info_slot_theme,
                roster_value=settings.info_slot_roster,
                names_value=settings.show_info_slot_names,
                enabled_value=settings.show_octa_slot,
                set_mode=wrap(self._set_south_slot),
                set_style_mode=wrap(
                    lambda mode, style: self._set_south_slot(mode, style=style)
                ),
                set_weekday=wrap(
                    lambda theme, metal=None, roster=None: self._set_south_slot(
                        "weekday", theme=theme, metal=metal, roster=roster
                    )
                ),
                set_names=wrap(
                    lambda checked: self._set_display_choice(
                        "show_info_slot_names", checked
                    )
                ),
            ),
            SlotDescriptor(
                index=3, title="3rd Slot",
                mode_value=settings.third_slot,
                style_value=settings.third_slot_style,
                theme_value=settings.third_slot_theme,
                roster_value=settings.third_slot_roster,
                names_value=settings.show_info_slot_names,
                enabled_value=settings.show_third_slot,
                set_mode=wrap(self._set_third_slot),
                set_style_mode=wrap(
                    lambda mode, style: self._set_third_slot(mode, style=style)
                ),
                set_weekday=wrap(
                    lambda theme, metal=None, roster=None: self._set_third_slot(
                        "weekday", theme=theme, metal=metal, roster=roster
                    )
                ),
                set_names=wrap(
                    lambda checked: self._set_display_choice(
                        "show_info_slot_names", checked
                    )
                ),
            ),
        )

    def _open_observatory(self) -> None:
        """Open (or raise) the [Observatory](observatory.md) with the
        EFFECTIVE moment/observer — the frozen Time Travel tuple when
        simulating, else the live present — and the optional Deep Time
        pack (exact nearest-eclipse instants when installed).
        NON-MODAL (ITEM 1, R4): `.show()` instead of `.exec()`, so the
        dial stays interactive while it is open; a second open request
        RAISES the ONE live instance (its own Enlarge flow already runs
        non-modal too — see `ObservatoryDialog._open_enlarged`)."""
        if self._observatory is not None:
            self._observatory.raise_()
            self._observatory.activateWindow()
            return
        if self._simulation is not None:
            now, observer = self._simulation
            cycles = self._sim_cycles
        else:
            now = datetime.now(self._tz)
            observer = self._observer
            cycles = 0
        dialog = ObservatoryDialog(
            now, observer, self._tz, cycles=cycles,
            deep=self._deep, translations=self._translation_overlay,
            # FIX ROUND A (owner verdict 2026-07-19): in "top" z-mode
            # the dial is natively HWND_TOPMOST — this dialog must also
            # carry WindowStaysOnTopHint to open ABOVE it, matching
            # Settings/Time Travel/Guide; every other z-mode stays a
            # normal window (owner 2026-07-13 intent, unchanged).
            stay_on_top=self._settings.z_mode == "top",
        )
        dialog.finished.connect(self._on_observatory_closed)
        self._observatory = dialog
        dialog.show()

    def _on_observatory_closed(self, _result: int = 0) -> None:
        self._observatory = None

    def _open_encyclopedia_at(
        self, topic: str | None = None, entry: int = 0
    ) -> None:
        """Open (or navigate) the Encyclopedia — from the menu (topic
        None = the gallery) or on a Spacebar jump to a hovered topic's
        entry (owner 2026-07-16, ROADMAP queue #8). NON-MODAL (ITEM 1,
        R4 owner instruction batch 2026-07-20): `.show()` instead of
        `.exec()`, so the dial stays interactive while it is open. The
        old re-entrancy guard (owner 15h item 3C) becomes "act on the
        live one" — a THEMED second jump (a real topic — a held key's
        auto-repeat, or a fresh SPACE press over a different target)
        NAVIGATES the live window to the new target
        (`EncyclopediaDialog.navigate_to`, a strict improvement over the
        old modal no-op); the menu's plain "Encyclopedia…" re-open
        (topic=None) just raises it without disturbing what the user is
        already browsing."""
        if self._encyclopedia is not None:
            self._encyclopedia.navigate_to(topic, entry)
            self._encyclopedia.raise_()
            self._encyclopedia.activateWindow()
            return
        dialog = EncyclopediaDialog(
            self._translation_overlay,
            hidden_unlocked=self._hidden_unlocked,
            initial_topic=topic,
            initial_entry=entry,
            # FIX ROUND A (owner verdict 2026-07-19): see the
            # matching Observatory comment — "top" z-mode needs
            # WindowStaysOnTopHint to clear the dial's native
            # HWND_TOPMOST; every other z-mode stays normal.
            stay_on_top=self._settings.z_mode == "top",
            # The Scale rotation (owner decree 2026-07-19/20) reads
            # the same TRAVELED date as the poles' light/dark glyph
            # law — a running Time Travel simulation, else today.
            travel_date=self._effective_travel_date(),
        )
        dialog.finished.connect(self._on_encyclopedia_closed)
        self._encyclopedia = dialog
        dialog.show()

    def _on_encyclopedia_closed(self, _result: int = 0) -> None:
        self._encyclopedia = None

    def _open_settings(self) -> None:
        dialog = SettingsDialog(
            self._settings, self._skin, self._translation_overlay
        )
        if dialog.exec() != SettingsDialog.DialogCode.Accepted:
            return
        new_settings = dialog.result_settings()
        location_changed = (
            new_settings.latitude,
            new_settings.longitude,
            new_settings.timezone,
        ) != (self._settings.latitude, self._settings.longitude, self._settings.timezone)
        language_changed = new_settings.language != self._settings.language
        self._settings = new_settings
        if language_changed:
            self._apply_language(start_missing=True)
        if location_changed:
            self._tz = ZoneInfo(new_settings.timezone)
            self._observer = astral.Observer(
                latitude=new_settings.latitude, longitude=new_settings.longitude
            )
            self._day = None                # full rebuild for the new place
        # Rebuild from DEFAULT_SKIN so cleared overrides (back to "skin
        # default") actually clear instead of sticking.
        self._install_skin(build_skin(self._settings))
        # The visibility Z mode may have changed (owner 2026-07-17): swap
        # the window flags (a no-op when unchanged). The swap recreates the
        # native window and DROPS the screenChanged connection (the S18
        # caveat) — reconnect it on the fresh handle when it actually
        # swapped; set_z_mode itself re-asserts native topmost for "top".
        if self._widget.set_z_mode(self._settings.z_mode):
            self._widget.windowHandle().screenChanged.connect(
                self._on_screen_changed
            )
        self._on_tick(clock_jumped=False)
        # The menu mirrors the settings (checkmarks, custom rings in
        # Theme > Ring) — rebuild it wholesale after every dialog OK.
        self._menu = self._build_menu()
        self._widget.set_menu(self._menu)
        self._widget.set_show_action(self._show_action)
        self._tray.set_menu(self._menu)
        self._configure_theme_rotation()
        native.set_autostart(dialog.autostart_selected())
        self._flush_position()

    def _bundled_coverage(self) -> tuple[int, int]:
        """The INTERSECTION of the two bundled databases' coverage —
        the minute-exact core tier (both are needed to build a day).
        Read from the data, never hardcoded."""
        seasons_first, seasons_last = self._seasons.coverage()
        moon_first, moon_last = self._moon_phases.coverage()
        return max(seasons_first, moon_first), min(seasons_last, moon_last)

    def _travel_coverage(self) -> tuple[int, int]:
        """The years Time Travel can render: the bundled intersection,
        widened to the Deep Time pack's own coverage when the pack is
        present (Session 16) — both spans read from their data."""
        first, last = self._bundled_coverage()
        if self._deep is not None:
            deep_first, deep_last = self._deep.coverage()
            return min(first, deep_first), max(last, deep_last)
        return first, last

    def _active_simulation_or_now(self) -> tuple[datetime, astral.Observer, int]:
        """The (moment, observer, cycles) every LIVE travel path chains
        from (owner spec, R5b round: "each jump starts from the active
        simulation") — the running simulation while one is live, else
        the real wall clock at the home observer. Used directly by
        every keyboard Fast Travel/Location shortcut
        (`_jump_to_place`/`_cycle_jump_city`/`_step_fast_travel`) and, by
        `_open_time_travel` below, to seed the DIALOG'S own fields —
        the SAME rule this round factored out of that seeding (Rule #5:
        one source for "what does 'right now' mean while travelling")."""
        if self._simulation is not None:
            moment, observer = self._simulation
            return moment, observer, self._sim_cycles
        return datetime.now(self._tz), self._observer, 0

    def _apply_jump(
        self, moment: datetime, observer, cycles: int, kind: str,
        city: dict | None = None,
    ) -> None:
        """One `_compute_jump` step, applied straight to the LIVE dial
        (`_start_simulation`) instead of a dialog draft — the shared
        tail every keyboard travel shortcut uses. A clamp (`None`) is a
        silent no-op, matching every other Quick Jump caller."""
        result = self._compute_jump(moment, observer, cycles, kind, city)
        if result is not None:
            self._start_simulation(*result)

    def _open_time_travel(self) -> None:
        # A running simulation SEEDS the dialog (owner 2026-07-14):
        # after a quick jump the offered coordinates and moment are
        # the simulated ones, not the home city's.
        moment, observer, cycles = self._active_simulation_or_now()
        initial = moment.astimezone(self._tz).replace(tzinfo=None)
        latitude, longitude = observer.latitude, observer.longitude
        dialog = TimeTravelDialog(
            latitude, longitude,
            overlay=self._translation_overlay,
            initial_moment=initial,
            initial_cycles=cycles,
            coverage=self._travel_coverage(),
            core_coverage=self._bundled_coverage(),
            era_notation=self._settings.era_notation,
            show_era_suffix=self._settings.show_era_suffix,
            third_era=self._settings.third_era,
            deep_pack=self._deep is not None,
            # ITEM 3A (R5 MENU REWORK): the dialog's own Quick Jump
            # rows — the old deep submenu chain's replacement.
            jump_callback=self._dialog_jump,
            jump_cities=self._settings.jump_cities,
        )
        result = dialog.exec()
        if result == TimeTravelDialog.RETURN_TO_NOW:
            self._end_simulation()
            return
        if result != TimeTravelDialog.DialogCode.Accepted:
            return
        moment = dialog.moment().replace(tzinfo=self._tz)
        observer = astral.Observer(
            latitude=dialog.latitude(), longitude=dialog.longitude()
        )
        self._start_simulation(moment, observer, dialog.cycles())

    def _effective_travel_date(self) -> date:
        """The date driving the poles' Quick Jump light/dark glyph
        (owner revocation, fix round E, 2026-07-19, slika 6): the
        DISPLAYED moment — the Time Travel traveled date while a
        simulation runs, else today's wall-clock date."""
        if self._simulation is not None:
            moment, _observer = self._simulation
            return moment.date()
        return date.today()

    def _end_simulation(self) -> None:
        """NOW (owner 2026-07-15): back to the present immediately —
        the running simulation ends and the dial rebuilds from the
        real wall clock; a no-op when nothing is simulated."""
        self._simulation = None
        self._sim_cycles = 0
        self._day = None
        self._on_tick(clock_jumped=False)

    def _start_simulation(self, moment: datetime, observer, cycles: int = 0) -> None:
        """Render the (moment, observer) situation for the standard
        Time Travel minute, then return to the present — any new
        travel restarts the minute (owner 2026-07-14). The moment is
        FIRST re-canonicalized (Session 16): a jump or a timezone
        conversion may have drifted the proxy year across a canonical
        window edge, and the repositories answer in the canonical frame
        — one enforcement point keeps every path consistent. Final
        coverage backstop (owner 2026-07-16): a moment the databases
        cannot render is refused here, so no travel path can reach the
        day build's die-visibly box — the dialog already explained why;
        a quick jump simply stays put."""
        astro_year = real_year(moment.year, cycles)
        canonical = proxy_cycles(astro_year)
        if canonical != cycles:
            moment = moment.replace(
                year=astro_year + canonical * constants.GREGORIAN_CYCLE_YEARS
            )
            cycles = canonical
        first, last = self._travel_coverage()
        if not (first <= astro_year <= last):
            return
        self._simulation = (moment, observer)
        self._sim_cycles = cycles
        self._simulation_ends = monotonic() + defaults.TIME_TRAVEL_DURATION_S
        self._day = None                    # rebuild with the simulated situation
        self._on_tick(clock_jumped=False)

    # Quick Jump unit table (owner slika 12): kind -> (unit, sign).
    _UNIT_JUMPS = {
        "next_day": ("day", 1), "prev_day": ("day", -1),
        "next_month": ("month", 1), "prev_month": ("month", -1),
        "next_year": ("year", 1), "prev_year": ("year", -1),
        "next_century": ("century", 1), "prev_century": ("century", -1),
        "next_millennium": ("millennium", 1), "prev_millennium": ("millennium", -1),
    }
    _ECLIPSE_JUMPS = {
        "next_solar_eclipse": ("solar", 1), "prev_solar_eclipse": ("solar", -1),
        "next_lunar_eclipse": ("lunar", 1), "prev_lunar_eclipse": ("lunar", -1),
    }

    def _compute_jump(
        self, base_moment: datetime, base_observer, base_cycles: int,
        kind: str, city: dict | None = None,
    ) -> tuple[datetime, "astral.Observer", int] | None:
        """The PURE computation behind every jump preset (owner rounds
        2026-07-14; Session 16 rework, owner slika 12; EXTRACTED from
        the old immediate-jump `_quick_jump`, R5 MENU REWORK — the
        Quick Jump submenu itself died with the deep-nesting complaint,
        `UV/DESIGN/Meni One over Another.png`, Rule #6). Returns the
        LANDED (moment, observer, cycles) or None when the jump clamps
        at the active coverage edge (a no-op, never a crash) — the
        caller decides what to DO with the result: `_dialog_jump`
        applies it to the Time Travel window's own fields (chaining
        from ITS current state, never the live simulation), nothing
        else calls this anymore now that the immediate-apply menu path
        is gone. Places are REAL coordinates with their REAL clocks:
        Greenwich and the user's Quick Jump cities in their own
        timezones, the poles on UTC. Deep travel runs in the 400-year
        proxy frame — event instants are REBASED into the caller's
        frame before comparing, and the caller re-canonicalizes the
        landing (`_start_simulation` for a live jump; `_dialog_jump`
        for a dialog-local one)."""
        moment, observer, cycles = base_moment, base_observer, base_cycles
        first, last = self._travel_coverage()
        astro_base = real_year(base_moment.year, base_cycles)
        sun_moon_match = _SUN_MOON_JUMP_PATTERN.match(kind)
        if sun_moon_match:
            direction, body, phase_filter = sun_moon_match.groups()
            # Gather turning points only from years the databases cover, so
            # the anchor lookup itself never steps off the edge (owner
            # 2026-07-16). year_anchors(N) already reaches into N-1/N+1.
            # Each year answers in ITS canonical proxy frame — candidates
            # are compared on the frame-free JULIAN DAY (rebasing the
            # datetimes themselves would overflow years 0/10000 at the
            # datetime boundaries) and the landing re-canonicalizes.
            years = [
                year
                for year in (astro_base - 1, astro_base, astro_base + 1)
                if first <= year <= last
            ]
            candidates: dict[float, tuple[datetime, int]] = {}
            for year in years:
                cycles_of_year = proxy_cycles(year)
                if body == "sun":
                    source = _filtered_sun_anchors(
                        self._seasons.year_anchors(year).instants, phase_filter
                    )
                else:
                    source = _filtered_moon_events(
                        self._moon_phases.moon_window(year).events, phase_filter
                    )
                for when in source:
                    candidates[julian_day_of(when, cycles_of_year)] = (
                        when, cycles_of_year,
                    )
            base_jd = julian_day_of(base_moment, base_cycles)
            # The simulated moment is floored to the minute, so the
            # landed-on instant lies seconds AHEAD of it — the strict
            # one-minute guard keeps "next" from re-picking it.
            if direction == "next":
                order = sorted(jd for jd in candidates if jd > base_jd + 1.0 / 1440.0)
            else:
                order = sorted(
                    (jd for jd in candidates if jd < base_jd), reverse=True
                )
            for jd in order:
                when, cycles_of_year = candidates[jd]
                proxy, cycles = canonical_proxy(
                    real_year(when.year, cycles_of_year), when.month,
                    when.day, when.hour, when.minute,
                )
                landing = proxy.replace(tzinfo=timezone.utc).astimezone(
                    base_moment.tzinfo
                )
                # Never LAND on an instant whose LOCAL year the databases
                # can't render — the day build would die visibly.
                if first <= real_year(landing.year, cycles) <= last:
                    moment = landing
                    break
            else:
                return None             # clamp: already at the coverage edge
        elif kind in self._ECLIPSE_JUMPS:
            # The eclipse navigation (owner 2026-07-16, ROADMAP 12/14a)
            # — fed by the Deep Time pack; the caller grays its entry
            # without it, this guard is the belt to that suspender.
            if self._deep is None:
                return None
            eclipse_kind, direction = self._ECLIPSE_JUMPS[kind]
            jd = julian_day_of(base_moment, base_cycles)
            if direction > 0:
                # The same one-minute guard as the event jumps: the
                # landed minute-floored moment must not re-pick itself.
                event = self._deep.eclipse_after(jd + 1.0 / 1440.0, eclipse_kind)
            else:
                event = self._deep.eclipse_before(jd, eclipse_kind)
            if event is None or not first <= event.year <= last:
                return None             # clamp: catalog edge
            proxy, cycles = canonical_proxy(
                event.year, event.month, event.day,
                event.second_of_day // 3600,
                (event.second_of_day % 3600) // 60,
            )
            moment = proxy.replace(tzinfo=timezone.utc).astimezone(
                base_moment.tzinfo
            )
        elif kind in self._UNIT_JUMPS:
            # Year · Month · Day and Century · Millennium (owner slika
            # 12): calendar arithmetic on the REAL astronomical date —
            # the wall time stays, day clamps to the target month.
            unit, sign = self._UNIT_JUMPS[kind]
            if unit == "day":
                target_date = base_moment.date() + timedelta(days=sign)
                y = real_year(target_date.year, base_cycles)
                m, d = target_date.month, target_date.day
            else:
                years = {"year": 1, "century": 100, "millennium": 1000}
                y, m, d = shift_calendar(
                    astro_base, base_moment.month, base_moment.day,
                    years=years.get(unit, 0) * sign,
                    months=sign if unit == "month" else 0,
                )
            if not first <= y <= last:
                return None             # clamp: coverage edge, stay put
            proxy, cycles = canonical_proxy(
                y, m, d, base_moment.hour, base_moment.minute
            )
            moment = proxy.replace(tzinfo=base_moment.tzinfo)
        elif kind in ("north_pole", "south_pole"):
            sign = 1 if kind == "north_pole" else -1
            observer = astral.Observer(
                latitude=sign * defaults.QUICK_JUMP_POLE_LATITUDE,
                longitude=0.0,
            )
            moment = base_moment.astimezone(timezone.utc)
        elif kind == "city":                # the user's own place (slika 12)
            observer = astral.Observer(
                latitude=city["latitude"], longitude=city["longitude"]
            )
            moment = base_moment.astimezone(ZoneInfo(city["timezone"]))
        else:                               # greenwich — the REAL place
            observer = astral.Observer(
                latitude=defaults.GREENWICH_LATITUDE,
                longitude=defaults.GREENWICH_LONGITUDE,
            )
            moment = base_moment.astimezone(
                ZoneInfo(defaults.GREENWICH_TIMEZONE)
            )
        return moment.replace(second=0, microsecond=0), observer, cycles

    def _dialog_jump(
        self, moment: datetime, cycles: int, latitude: float, longitude: float,
        kind: str, city: dict | None,
    ) -> tuple[datetime, int, float, float] | None:
        """The Time Travel window's OWN Quick Jump rows (item 3A, R5
        MENU REWORK — the rows the old deep Quick Jump submenu chain
        used to hold, `UV/DESIGN/RIGHT CLICK MENU.txt`) — TT LIVE TRAVEL
        (owner round R8b item 1, slika 1-6: "ono sto smo radili na uvek
        Quick Jump dok je bio na right clicku" — a jump row/arrow inside
        the dialog must travel the WATCH immediately, exactly like the
        old right-click menu did, not sit as a draft the owner has to
        OK before anything moves; "ne kao sada da moram svaki put da
        kliknem okej pa da se vratimo taj meni" — no more click-OK-
        reopen per jump). Chains from the DIALOG'S own current fields
        (so a jump chain still reads consistently even mid-travel) —
        `_compute_jump` is the SAME pure computation the old menu's
        immediate jumps used (Rule #5) — but now ALSO starts/refreshes
        the LIVE simulation with the landed moment via `_start_simulation`,
        the exact tail `_apply_jump` uses for every keyboard travel
        shortcut. The dialog then mirrors the SAME fields back onto its
        own widgets (`_on_jump`/`_apply_moment`, app/time_travel.py) so
        it never drifts from what the dial is actually showing — OK
        (`_open_time_travel` below) simply re-asserts whatever the
        fields hold when clicked (a no-op if nothing changed since the
        last jump), Return to Now still ends the simulation outright.
        `moment` is naive (the dialog's own editor, interpreted in the
        configured timezone, same convention `_open_time_travel`
        already uses); returns naive too."""
        observer = astral.Observer(latitude=latitude, longitude=longitude)
        result = self._compute_jump(
            moment.replace(tzinfo=self._tz), observer, cycles, kind, city,
        )
        if result is None:
            return None
        new_moment, new_observer, new_cycles = result
        self._start_simulation(new_moment, new_observer, new_cycles)
        return (
            new_moment.astimezone(self._tz).replace(tzinfo=None), new_cycles,
            new_observer.latitude, new_observer.longitude,
        )

    # --- Translation (owner spec: translate once, cache, display) -----------------

    def _apply_language(self, start_missing: bool) -> None:
        """Load the cached overlay for the chosen language and, when
        entries are missing (first pick, or the English corpus grew),
        translate them in a background thread — the dial keeps running
        and the texts switch when the cache completes."""
        language = self._settings.language
        if language == "en":
            self._translation_overlay = {}
            return
        store = TranslationStore()
        self._translation_overlay = store.load(language)
        if not start_missing or self._translation_thread is not None:
            return
        if store.missing(language, collect_corpus()):
            self._translation_thread = threading.Thread(
                target=self._translate_worker, args=(language,), daemon=True
            )
            self._translation_thread.start()
            self._translation_poller.start()
            self._tray.notify(
                self._ui("Translating"),
                self._ui(
                    "Preparing {language} — the clock keeps running; "
                    "texts switch when ready."
                ).format(language=constants.TRANSLATION_LANGUAGES[language]),
                critical=False,
            )

    def _translate_worker(self, language: str) -> None:
        """Background thread: translate the missing corpus entries in
        resumable chunks — every chunk persists, so a network failure
        mid-run continues where it stopped on the next attempt."""
        try:
            store = TranslationStore()
            corpus = collect_corpus()
            while True:
                missing = store.missing(language, corpus)
                if not missing:
                    break
                chunk = dict(list(missing.items())[:20])
                store.save(language, chunk, translate_texts(chunk, language))
            self._translation_error = None
        except Exception as error:      # network/JSON — surfaced by the poller
            self._translation_error = error

    def _poll_translation(self) -> None:
        thread = self._translation_thread
        if thread is None or thread.is_alive():
            return
        self._translation_poller.stop()
        self._translation_thread = None
        failed = self._translation_error
        self._translation_error = None
        language = self._settings.language
        if language != "en":
            # Apply whatever completed (chunks persist) either way —
            # including the menu, whose chrome strings live in the
            # same overlay (Phase 2).
            self._translation_overlay = TranslationStore().load(language)
            self._install_skin(build_skin(self._settings))
            self._menu = self._build_menu()
            self._widget.set_menu(self._menu)
            self._widget.set_show_action(self._show_action)
            self._tray.set_menu(self._menu)
        if failed is not None:
            self._tray.notify(
                self._ui("Translation incomplete"),
                self._ui(
                    "{error} — finished parts are shown; pick the language "
                    "again in Settings to resume."
                ).format(error=failed),
            )
        elif language != "en":
            self._tray.notify(
                self._ui("Translation ready"),
                self._ui("{language} is active.").format(
                    language=constants.TRANSLATION_LANGUAGES[language]
                ),
                critical=False,
            )

    def _show_if_normal_z_mode(self) -> None:
        """The tray double-click / menu "Show" gesture (owner
        2026-07-18, ROADMAP 15h): a no-op outside "normal" z-mode,
        where raising the dial is meaningless (bottom never rides above
        anything, top already does)."""
        if self._settings.z_mode == "normal":
            self._widget.raise_and_focus()

    def _set_click_through(self, enabled: bool) -> None:
        self._widget.set_click_through(enabled)
        if enabled:
            self._hover_poller.start()
        else:
            self._hover_poller.stop()
            self._legend.dismiss()
            # The poller was the only hover driver in this mode — clear
            # its target or the last element stays enlarged (review
            # finding: the cursor sits on the tray, not the dial).
            if self._compositor.set_hover(
                -1.0e9, -1.0e9, float(self._widget.dial_diameter)
            ):
                self._widget.update()
        self._settings = replace(self._settings, click_through=enabled)
        self._flush_position()

    def _poll_hover(self) -> None:
        cursor = QCursor.pos()
        if self._legend.isVisible() and self._legend.geometry().contains(cursor):
            return                      # the user is scrolling the article
        local = self._widget.mapFromGlobal(cursor)
        size = float(self._widget.dial_diameter)
        margin = self._widget.margin_px
        x, y = local.x() - margin, local.y() - margin
        tip = None
        inside = 0 <= x < size and 0 <= y < size
        if QApplication.queryKeyboardModifiers() & getattr(
            Qt.KeyboardModifier, defaults.HOVER_BYPASS_MODIFIER
        ):
            # The held bypass key silences hovers in click-through
            # mode too (owner 2026-07-16) — same rule as the widget's
            # mouseMoveEvent.
            inside = False
        if self._compositor.set_hover(
            x if inside else -1.0e9,
            y if inside else -1.0e9,
            size,
        ):
            self._widget.update()       # hover-enlarge in click-through mode
        if inside:
            tip = self._compositor.tooltip_at(x, y, size)
        if tip:
            if tip != self._last_hover_tip:
                self._legend.show_html(tip, cursor)
        elif self._last_hover_tip:
            self._legend.dismiss()
        self._last_hover_tip = tip

    def _set_diameter(self, diameter: int) -> None:
        if diameter == self._settings.diameter:
            return
        self._settings = replace(self._settings, diameter=diameter)
        # The four Earth label pills and the compact slider live inside
        # the Design window now (R5 MENU REWORK) — its own `refresh()`
        # re-reads `settings.diameter`/`earth_label` fresh, so nothing
        # here needs mirroring into a controller-held widget any more.
        self._widget.set_dial_diameter(diameter)
        self._compositor.invalidate()
        self._widget.update()
        self._flush_position()          # persists position AND the new diameter

    @staticmethod
    def _critical_box(text: str, buttons, default) -> int:
        box = QMessageBox(QMessageBox.Icon.Critical, constants.APP_NAME, text, buttons)
        box.setDefaultButton(default)
        # Without a parent window the box can open buried under other
        # windows (verified on Windows 11) — the error must be seen.
        box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        return box.exec()
