"""Z-ordered layer stack with cadence-driven caching.

STATIC and DAILY layers are composited into ONE cached pixmap at device
resolution, rebuilt only when the day context, size or DPI changes; the
per-minute paint blits that cache and draws the MINUTE layers (hands,
year marker) live. The same paint path renders offscreen for tests and
the future settings preview.
"""

import math
from time import monotonic

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap

from config import archetypes, calendar_mounts, constants, defaults, dial, paths, profiling
from config.registry import week as week_registry
from data.encyclopedia import EncyclopediaRepository, shared_encyclopedia
from data.symbolism import SymbolismRepository, shared_symbolism
from core import world
from core.clock_state import DayContext, TickState
from render.assets import AssetCache
from render.tooltip_composer import TooltipComposer
from render.archetype_geometry import archetype_figure_size, archetype_lit_index
from render.context import Cadence, Layer, RenderContext, ctx_for_frame
from render import numeral_bands
from render.layers.archetype import ArchetypeCenterLayer, ArchetypeLayer
from render.layers.background import BackgroundLayer
from render.layers.center_body import CenterBodyLayer
from render.layers.hand import HandLayer
from render.layers.hover_lift import HoverLiftLayer
from render.layers.moon_band import MoonBandLayer
from render.layers import numerals as layer_numerals
from render.layers.numerals import LiveCrownLayer
from render.layers.ring import RingLayer
from render.layers.slot import SlotLayer
from render.layers.star import StarLayer
from render.layers.weekday import WeekdayLayer
from render.layers.year_marker import YearMarkerLayer, earth_marker_angle, earth_marker_orbit, earth_marker_scale, eclipse_body_angle, eclipse_body_orbit, eclipse_body_scale, moon_marker_angle, moon_marker_orbit, moon_marker_scale
from render.ninths import active_thirteenth
from render.painting import dial_point
from render.shapes import arm_shape_path
from render.skin_geometry import archetype_active, archetype_key, arm_offset_deg, servant_seat_angle, visible_occupant, weekday_slots
from render.slot_layout import servant_holds_the_seat, slot_layout, slot_seat_orbit, slot_seat_rotation, slot_seat_scale, weekday_body_orbit, weekday_body_size
from skins.manifest import SkinDefinition

_RENDER_HINTS = (
    QPainter.RenderHint.Antialiasing
    | QPainter.RenderHint.SmoothPixmapTransform
    | QPainter.RenderHint.TextAntialiasing
)


def _build_layers(skin: SkinDefinition) -> list[Layer]:
    factories = {
        "background": lambda: BackgroundLayer(skin),
        "star": lambda: StarLayer(skin),
        "ring": lambda: RingLayer(skin),
        "weekday_set": lambda: WeekdayLayer(skin),
        "year_marker": lambda: YearMarkerLayer(skin),
        "moon_band": lambda: MoonBandLayer(skin),
        # "moon_band_ticks" is retired from the z vocabulary (owner
        # repeat correction 2026-08-11): the redress paints inside
        # RingLayer now. A stale name in a stored z_order is skipped.
        "moon_band_ticks": lambda: None,
    }
    # Elements switches (owner spec): a switched-off element is simply
    # not built. The YearMarkerLayer gates Earth/Moon internally (one
    # layer, two markers). THE MOON HORIZON BAND (owner verdict
    # 2026-08-09) is skipped outright unless the Moon is shown AND its
    # own mode is "horizon" — `MoonBandLayer.paint` re-checks the mode
    # too (belt and suspenders), but never builds the layer at all here
    # is the cheaper, and cleaner, no-op.
    skipped = {
        "star": not skin.show_pointer,
        "weekday_set": not skin.show_weekday,
        # THREE bodies now, not two (owner verdict 2026-08-12, C1): the
        # eclipse body has its own switch and its own seat, so the layer
        # must still be built when both markers are hidden.
        "year_marker": not (
            skin.show_earth or skin.show_moon or skin.show_eclipse
        ),
        "moon_band": not (
            skin.show_moon and skin.year_marker.moon_band_mode == "horizon"
        ),
        "moon_band_ticks": True,        # retired — see the factory note
    }
    seats = [
        seat for seat in slot_layout(skin).values() if seat != "classic"
    ]
    layers: list[Layer] = []
    for name in skin.z_order:
        if name == "hands":
            if any(seat != "center" for seat in seats):
                # The SEATED slots draw BELOW the hands (owner bug
                # report: the seconds hand passed behind the zodiac
                # art); the layer walks the owner's position matrix
                # (2026-07-14) internally.
                layers.append(SlotLayer(skin))
            # The hand pack's own z_order draws bottom-up (owner spec
            # 2026-07-12; default hours -> minutes -> seconds).
            kinds = {"hours": "hour", "minutes": "minute", "seconds": "second"}
            for hand in skin.hands.z_order:
                kind = kinds[hand]
                if kind == "second" and (
                    skin.hands.second is None or not skin.show_seconds
                ):
                    continue
                layers.append(HandLayer(skin, kind))
        elif name == "weekday_set" and archetype_active(skin):
            # THE ARCHETYPE MODE (owner sealed package 2026-07-16):
            # the archetype figures take the weekday model's z spot —
            # the weekday unit and the slots are overridden OFF at the
            # render level (enabled_slots), never in settings.
            layers.append(ArchetypeLayer(skin))
        elif not skipped.get(name, False):
            layers.append(factories[name]())
    if (
        "weekday_set" in skin.z_order and skin.show_weekday
        and not archetype_active(skin)
    ):
        # The current day's center body rides ABOVE everything — the
        # hands sweep behind the Sun (owner spec).
        layers.append(CenterBodyLayer(skin))
    if archetype_active(skin):
        # The archetype CENTER — the Eye / Hearth / Seal / Union /
        # Throne — draws where the weekday center used to: above the
        # hands, per the existing center z-order (owner 2026-07-16).
        layers.append(ArchetypeCenterLayer(skin))
    if "center" in seats:
        # A CENTER-seated slot (owner dual-Sunday round 2026-07-12)
        # rides ABOVE the hands like the center body — "the center
        # occludes the hands", his accepted cost.
        layers.append(SlotLayer(skin, centered=True))
    if skin.ring_name in dial.RING_LIVE_CROWN:
        # THE LIVE CROWN (ring_rework.md §3): only The One and Templar
        # keep a time in the arc, and only they build this layer — the
        # ONE minute-cadence element of the numeral round.
        layers.append(LiveCrownLayer(skin, skin.ring_name))
    # LAST: the hover z-lift (owner 2026-07-13) — the enlarged element
    # repaints above everything, hands included.
    layers.append(HoverLiftLayer(skin))
    return layers


class Compositor:
    def __init__(
        self,
        skin: SkinDefinition,
        cache: AssetCache,
        symbolism: SymbolismRepository | None = None,
        overlay: dict | None = None,
        encyclopedia: EncyclopediaRepository | None = None,
    ):
        self._skin = skin
        self._cache = cache
        self._layers = _build_layers(skin)
        # The z-ordered stack is partitioned into paint STEPS (owner
        # 2026-07-17, ROADMAP 15f): each maximal run of hover-INVARIANT
        # STATIC/DAILY layers becomes ONE cached pixmap; the MINUTE and
        # the HOVER-VARIABLE layers (the weekday bodies, the archetype
        # figures) paint LIVE. Because the default z_order seats the
        # weekday_set BELOW the ring (a STATIC layer), pulling it out
        # splits the cache into two segments — the base (background,
        # star) below the live bodies and the ring above them — so the
        # z-order is preserved to the pixel while a hover enter/leave or
        # an Omega reveal rebuilds NOTHING.
        self._cached_groups, self._steps = self._plan_steps(self._layers)
        # The controller passes a repository with the active language's
        # translation overlay; standalone uses read the originals. The
        # same overlay (Phase 2b) also translates the hover INFO lines
        # — labels, day/month/sign/phase names.
        # THE ONE COPY RULE (owner 2026-08-06): the controller always
        # passes the process-wide repositories in. The fallbacks below
        # exist for direct construction (tests, tools) and reach for the
        # SHARED English books — a private copy only when an overlay
        # makes the text genuinely different from the shared one.
        self._overlay = overlay or {}
        self._symbolism = symbolism or (
            SymbolismRepository(overlay=self._overlay)
            if self._overlay else shared_symbolism()
        )
        # THE NINTH's own article family lives in encyclopedia.json, not
        # symbolism.json (round R3b item 3/4: the CENTER seat's solar-
        # window hover speaks it) — the SAME overlay, a sibling
        # repository, never a second translation path.
        self._encyclopedia = encyclopedia or (
            EncyclopediaRepository(overlay=self._overlay)
            if self._overlay else shared_encyclopedia()
        )
        self._day: DayContext | None = None
        self._last_tick: TickState | None = None
        # One cached pixmap per hover-invariant segment (None = needs a
        # rebuild); the shared key covers size/DPI, the day and the
        # Calendar's intraday lit wedge — NOT hover or reveal.
        self._composites: list[QPixmap | None] = [None] * len(
            self._cached_groups
        )
        self._composite_key: tuple | None = None
        self._hovered: str | None = None    # hover-enlarge target
        # Hidden mode (owner 2026-07-14, top-only round 2026-07-16):
        # unlocked, the 12h ring jewel opens the Four Greetings legend.
        self._hidden_unlocked = False
        #: Everything this dial SAYS (R13, 2026-08-18).
        self._tooltips = TooltipComposer(self)
        # Reveal-week (owner 2026-07-16): an Omega double-click raises
        # every non-active weekday body to full opacity until this
        # monotonic deadline; None = no reveal running.
        self._reveal_until: float | None = None
        # THE NIGHT INVERSION's own state (ring_rework §1, core.world).
        # `_flip_target` is the phase this dial belongs at RIGHT NOW —
        # 0 by day, 180 by night, always 0 in Geocentric — and None only
        # before the first tick has ever been seen (the first paint
        # SNAPS it into place). `_flip_started` is the monotonic instant
        # a GENUINE transition began, or None when the phase is simply
        # standing (which is every moment of a polar day or a polar
        # night, and every moment after a clock correction snapped).
        self._flip_from: float = 0.0
        self._flip_target: float | None = None
        self._flip_started: float | None = None
        # THE TURNING CROSSFADE (owner order 2026-08-14 — perfect the
        # flip animation): while a flip runs, the DEPARTING phase's
        # cached segments are kept here and painted ON TOP of the
        # arriving phase's, fading out as the turn progresses — so a
        # mirrored numeral, a re-seated jewel or the Dollar's swapped
        # night motto (THE INVERTED CROWN TEXTS) never snaps at the
        # flip's first frame; it dissolves mid-turn while both variants
        # ride the same rotation. None whenever no flip is in flight —
        # the steady state pays nothing.
        self._flip_from_composites: list | None = None
        self._flip_from_phase: float = 0.0

    @staticmethod
    def _plan_steps(
        layers: list[Layer],
    ) -> tuple[list[list[Layer]], list[tuple[str, object]]]:
        """Partition the z-ordered stack into paint steps (owner
        2026-07-17, ROADMAP 15f). A layer is CACHEABLE when its cadence
        is not MINUTE AND it is not hover-variable; consecutive cacheable
        layers coalesce into one group (one cached pixmap). MINUTE and
        hover-variable layers become LIVE steps painted every frame. The
        steps preserve the exact z-order — a cache blit and a live layer
        interleave in list order — so the split is invisible on screen.
        Returns (cached_groups, steps): a step is ("cache", group_index)
        or ("live", layer)."""
        groups: list[list[Layer]] = []
        steps: list[tuple[str, object]] = []
        current: list[Layer] | None = None
        for layer in layers:
            cacheable = (
                layer.cadence is not Cadence.MINUTE
                and not layer.hover_variable
            )
            if cacheable:
                if current is None:
                    current = []
                    groups.append(current)
                    steps.append(("cache", len(groups) - 1))
                current.append(layer)
            else:
                current = None
                steps.append(("live", layer))
        return groups, steps

    # ── what the tooltip composer asks for ────────────────────────────
    #: The live typed skin the dial is painted from.
    skin = property(lambda self: self._skin)
    #: The day context (sun arc, season, zodiac, hemisphere...).
    day = property(lambda self: self._day)
    #: The last tick state a paint or a hit test observed.
    tick = property(lambda self: self._last_tick)
    #: The active language's translation overlay.
    overlay = property(lambda self: self._overlay)
    #: The two shared books, one copy per process (THE ONE COPY RULE).
    encyclopedia = property(lambda self: self._encyclopedia)
    symbolism = property(lambda self: self._symbolism)
    #: Whether the hidden mode's cipher has been entered this session.
    hidden_unlocked = property(lambda self: self._hidden_unlocked)

    def tooltip_at(self, x: float, y: float, size: float) -> str | None:
        """The hover text under the cursor — built by
        [Tooltip Composer](tooltip_composer.md)."""
        return self._tooltips.tooltip_at(x, y, size)

    def encyclopedia_target(
        self, x: float, y: float, size: float
    ) -> tuple[str, int] | None:
        """The (topic key, entry index) the SPACE jump opens for the
        element under the cursor."""
        return self._tooltips.encyclopedia_target(x, y, size)

    def warm_hover_articles(
        self, size: float, should_stop=None, progress=None
    ) -> int:
        """Pre-build every hover article this skin can speak today, off
        the GUI thread."""
        return self._tooltips.warm_hover_articles(size, should_stop, progress)

    def set_hidden_unlocked(self, unlocked: bool) -> None:
        self._hidden_unlocked = unlocked

    @paths.in_display
    def hit_omega(self, x: float, y: float, size: float) -> bool:
        """True when (x, y) — widget-local, same coordinates as
        `set_hover`/`tooltip_at` — lands on the Omega (24h) ring seat:
        the FULL ROUND AREA (owner slika 9, 2026-07-17), a circle CENTERED
        on the Omega jewel position (180°, the ring jewel band) whose
        radius covers the whole jewel cell. The old narrow annular wedge
        only answered on the jewel glyph itself (practically its lower
        part), so the double-click kept missing; the round area lands
        anywhere on the seat. The toggle semantics are untouched."""
        radius = size / 2
        point = QPointF(x - radius, y - radius)
        # The Omega seat is a ring LETTER, so it rides THE WORLD OFFSET
        # with the band it stands on (0.0 in Geocentric).
        center = dial_point(
            (180.0 + self.jewel_offset()) % 360.0,
            radius * dial.outer_centreline(self._skin.numeral_outer_ring_size),
        )
        hit_radius = radius * dial.OMEGA_HIT_RADIUS_FRACTION
        return math.hypot(
            point.x() - center.x(), point.y() - center.y()
        ) <= hit_radius

    def trigger_reveal_week(self, now: float | None = None) -> bool:
        """The Omega double-click, REPURPOSED (owner seal 2026-07-16):
        it HIDES THE HANDS for REVEAL_WEEK_DURATION_S — or until the
        NEXT double-click, a TOGGLE-OFF, not a restart — so the whole
        theme, pointer and dial can be seen clean. Where the weekday
        model is on, the ghost-reveal folds into the same gesture
        (ghosts to full + hands hidden together); in archetype mode
        every figure draws full the same way. Returns True when the
        window STARTED, False when this click ended it."""
        moment = monotonic() if now is None else now
        if self.reveal_active(moment):
            self._reveal_until = None
            # No composite drop (owner 2026-07-17, ROADMAP 15f): the
            # ghosts/figures live in the LIVE weekday/archetype layers now
            # — the next paint reflects the toggle-off with zero rebuild.
            return False
        self._reveal_until = moment + defaults.REVEAL_WEEK_DURATION_S
        return True

    def reveal_active(self, now: float | None = None) -> bool:
        """True while the reveal window from the last Omega double-click
        is still running (toggled off or expired = False)."""
        if self._reveal_until is None:
            return False
        moment = monotonic() if now is None else now
        if moment >= self._reveal_until:
            return False
        return True

    def set_day(self, day: DayContext) -> None:
        self._day = day
        self.refresh_composites()

    def refresh_composites(self) -> None:
        """Drop the cached composite groups ALONE — the rasterized
        assets stay. The art-ready repaint path (0.14.707): a
        background-built finish changes WHICH file the ring resolves,
        so the composites must rebuild, but flushing the whole
        `AssetCache` for one landed letter re-decoded every subdial,
        body and plate — measured as a 62 ms full rebuild per letter,
        17 times per drain burst."""
        self._composites = [None] * len(self._cached_groups)

    def invalidate(self) -> None:
        """Size/DPI/screen change: drop the composites and rasterized assets."""
        self.refresh_composites()
        self._cache.flush()

    def _two_faced_mount(self, tick: TickState) -> bool | None:
        """The daylight state, but ONLY while a two-depiction mount is
        the one riding the wedges — otherwise None, so the composite key
        stays purely daily (owner 2026-07-29's deletion of the lit wedge
        is not undone by this)."""
        if self._skin.pointer != "calendar":
            return None
        mount = calendar_mounts.CALENDAR_MOUNTS.get(self._skin.calendar_mount)
        if mount is None or mount.paint is None:
            return None
        return tick.is_daylight

    # --- THE TWO WORLD-MODES (ring_rework §1, core.world) ---------------------

    def note_daylight(
        self, is_daylight: bool, animate: bool, now: float | None = None,
    ) -> bool:
        """Report the sun's ACTUAL state and say whether the dial may
        TURN to meet it. Returns True when a flip animation started, so
        the caller can arm its frame timer for exactly that long.

        `animate=False` is the SNAP, and it is not an optimization: a
        WM_TIMECHANGE clock correction is not a sunset and a day-context
        rebuild is not a transition (owner bug 2026-08-06), so both
        apply the phase instantly, with no intermediate frame and no
        hover sweep. `animate=True` is only ever a genuine sunrise or
        sunset — an ordinary day has two, polar day and polar night have
        ZERO for months and this method simply keeps answering False."""
        target = (
            world.night_phase_deg(is_daylight)
            if self._skin.world_mode == "sky_up"
            else 0.0
        )
        if self._flip_target is None or not animate:
            self._flip_from = target
            self._flip_target = target
            self._flip_started = None
            return False
        if target == self._flip_target:
            # THE CUT-SHORT FLIP (owner bug 2026-08-13, root cause).
            # The sun's state is re-reported on EVERY scheduler tick —
            # once a second while the seconds hand runs — so a 1.5 s
            # sunset flip is asked this question mid-move with the same
            # answer it started on. Snapping the state here ended the
            # move at whatever angle it had reached (measured: 132 deg)
            # and teleported the dial to 180. Already standing at the
            # target, or already TURNING to it, are both "nothing to
            # do": leave the running move alone and let it finish.
            return False
        self._flip_from = self.phase_deg(now)
        self._flip_target = target
        self._flip_started = monotonic() if now is None else now
        return True

    def phase_deg(self, now: float | None = None) -> float:
        """The night phase RIGHT NOW — 0 or 180 while standing, an eased
        value in between while a flip runs (`core.world.flip_phase_deg`)."""
        if self._flip_target is None:
            return 0.0
        if self._flip_started is None:
            return self._flip_target
        moment = monotonic() if now is None else now
        return world.flip_phase_deg(
            self._flip_from, self._flip_target, moment - self._flip_started,
        )

    def flip_active(self, now: float | None = None) -> bool:
        """True while the turning move is still moving."""
        if self._flip_started is None:
            return False
        moment = monotonic() if now is None else now
        if moment - self._flip_started >= dial.WORLD_FLIP_DURATION_S:
            self._flip_started = None
            self._flip_from = self._flip_target
            return False
        return True

    def world_theta(self, point: QPointF) -> float:
        """The cursor's dial angle in the WORLD's own frame — the screen
        angle with THE WORLD OFFSET taken back off.

        Every hover that reads the dial BAND (the 360 ticks and their
        time/date/moon readings, the ring jewels and the crown words,
        the day/night and twilight wedges, the Calendar's own wedges)
        answers about a wall-clock mark, so it must ask the question in
        the frame those marks are drawn in. The POINTER's own hovers
        (the star arms) keep the screen frame and their own
        `rotation()` term instead. 0.0 in Geocentric leaves every one
        of them exactly as it was."""
        return (
            math.degrees(math.atan2(point.x(), -point.y()))
            - self.world_offset()
        ) % 360.0

    def interior_hit(self, fraction: float) -> float:
        """A radius FRACTION of the interior world, as the cursor meets it
        (THE INWARD-GROWTH LAW, opus sweep 2026-08-09): the drawn geometry
        scales by interior_scale, so every interior hit test multiplies its
        fraction the same way — one door, never per-site math."""
        return fraction * dial.interior_scale(self._skin.numeral_outer_ring_size)

    def _marker_ctx(self, radius: float) -> RenderContext:
        """The context the HIT TEST reads marker geometry through — built
        exactly as `paint` builds the drawing one, so `year_marker`'s seat
        functions return the same numbers for the cursor as for the brush
        (ONE SEAT, TWO READERS — see `element_at`).

        `hovered` rides along deliberately: a hovered body is DRAWN larger,
        so its target is larger too — which is what makes the enlargement
        stable instead of a body that grows out from under the cursor."""
        return RenderContext(
            skin=self._skin, day=self._day, tick=self._last_tick,
            daylight=(
                self._last_tick.is_daylight
                if self._last_tick is not None else True
            ),
            radius=radius, cache=self._cache, dpr=1.0,
            rotation=self.rotation(),
            world_offset=self.world_offset(),
            hovered=self._hovered,
            reveal_active=False, archetype_lit=None,
            interior_scale=numeral_bands.interior_scale(
                self._skin.numeral_outer_ring_size
            ),
        )

    def band_hit(self, fraction: float) -> float:
        """A band-riding radius FRACTION (jewels disc, Earth/Moon orbits,
        greetings band) — rides the centreline shift, 0.0 at default."""
        return fraction + dial.band_ride_shift(self._skin.numeral_outer_ring_size)

    def _phase_target(self) -> float:
        """The phase the CACHED composite is painted at — never the
        animated value, so the band plate is re-rendered ONCE per phase
        and the move itself is a rotation of finished pixels."""
        return 0.0 if self._flip_target is None else self._flip_target

    def _phase_angle(self, turn, phase_deg: float | None = None) -> float:
        """One of `core.world`'s two phase-driven angles, asked the ONE
        way — the two callers below differ only in which `world`
        function they name (clone C9, OOP audit 2026-08-18)."""
        if self._day is None:
            return 0.0          # before the first day context (hit tests)
        phase = self.phase_deg() if phase_deg is None else phase_deg
        return turn(
            self._skin.world_mode, self._day.star_rotation,
            self._skin.solar_rotation, phase,
        )

    def rotation(self, phase_deg: float | None = None) -> float:
        """THE POINTER ROTATION (`core.world`): Star/Aura/Umbra/slot
        rotation. Geocentric — the solar offset, or 0 upright, exactly
        as every release before this one. Heliocentric — the night phase
        alone: the star stands still and the world turns under it."""
        return self._phase_angle(world.pointer_rotation_deg, phase_deg)

    def world_offset(self, phase_deg: float | None = None) -> float:
        """THE WORLD OFFSET (`core.world`): how far the dial FACE has
        turned — 0.0 in Geocentric, so that mode is a bit-for-bit
        no-op."""
        return self._phase_angle(world.world_offset_deg, phase_deg)

    def jewel_offset(self) -> float:
        """WHAT THE ROTATION CARRIES (owner ballot verdict 2026-08-13):
        how far the JEWELS and the CROWN have turned — the world offset
        in `all_turn`, the NIGHT PHASE ALONE in `numerals_turn` (owner
        order 2026-08-16: the night turns the whole ring over, jewels
        included; only the SOLAR term is what the scope switch chooses
        between). Routed through `render.layers.numerals.jewel_offset`
        so the hit zones here and the glyphs the ring layer draws can
        never answer differently — and it takes the SAME eased phase the
        rest of the flip runs on, so a hit zone cannot lag its glyph
        mid-turn."""
        return layer_numerals.jewel_offset(
            self._skin, self.world_offset(), self.phase_deg(),
        )

    def jewel_theta(self, world_theta: float) -> float:
        """A cursor angle already in the WORLD frame (`world_theta`),
        re-expressed in the frame the JEWELS are seated in — the identity
        in `all_turn`, where the two frames are the same one."""
        return (
            world_theta + self.world_offset() - self.jewel_offset()
        ) % 360.0

    @profiling.timed("Paint frame")
    @paths.in_display
    def paint(self, painter: QPainter, size: float, dpr: float, tick: TickState) -> None:
        if self._day is None:
            raise RuntimeError("Compositor.paint() before the first day context")
        self._last_tick = tick
        if self._flip_target is None:
            # The first frame this compositor ever paints (a fresh skin
            # install, a test's render_offscreen): the phase SNAPS into
            # place — there is no previous state to have turned from.
            self.note_daylight(tick.is_daylight, animate=False)
        reveal = self.reveal_active()
        # The archetype hour-space (owner 2026-07-16) turns with the
        # hour hand — but the archetype figures paint LIVE (ROADMAP
        # 15f), so the lit index keys no cache.
        archetype_lit = self._archetype_lit(tick)
        # The cached segments depend ONLY on size/DPI and the day —
        # NEITHER hover NOR reveal (those live in the hover-variable
        # layers painted live below). This is the whole point of the 15f
        # split: a hover enter/leave rebuilds NOTHING (the count of
        # "Composite rebuild" stays flat). The Calendar's lit wedge used
        # to be the ONE intraday term in this key; deleting it (owner
        # 2026-07-29) makes the composite purely DAILY again.
        # ONE intraday term survives, and only when it is real: a mount
        # with a PAINT face (the Virtue Wheel) shows its light reading by
        # day and its dark one by night, so its cached segment must
        # rebuild when the sky turns. Every other configuration keys
        # purely on the day, exactly as the lit-wedge deletion left it.
        # THE NIGHT PHASE joins the key (ring_rework §1): the cached
        # segments carry the outer band, the jewels, the crown text and
        # the daylight arcs, all of which sit half a circle apart in the
        # two phases. It is the TARGET phase, never the animated one, so
        # a dial ever only holds TWO phase variants — the flip itself is
        # a rotation of these finished pixels, not a re-render per frame.
        key = (
            round(size * dpr), self._day.cache_key,
            self._two_faced_mount(tick), self._phase_target(),
        )
        if self._composite_key != key:
            # THE TURNING CROSSFADE: when ONLY the phase target moved
            # (a genuine flip in flight — same size, same day, same
            # mount face), the outgoing phase's finished segments are
            # kept to fade out over the incoming ones. Any other change
            # (resize, new day, settings rebuild) drops them — there is
            # no turn to dissolve through.
            if (
                self._composite_key is not None
                and self._flip_started is not None
                and self._composite_key[:-1] == key[:-1]
                and len(self._composites) == len(self._cached_groups)
            ):
                self._flip_from_composites = self._composites
                self._flip_from_phase = self._composite_key[-1]
            else:
                self._flip_from_composites = None
            self._composites = [None] * len(self._cached_groups)
            self._composite_key = key
        # The cached segments carry the window's transparent margin (the
        # ring jewels and event glow overhang the dial square) — each is
        # blit back-shifted so the dial lands at (0, 0). The margin is
        # LIVE from the user's settings (owner 2026-07-17), matching the
        # widget's own window sizing.
        overhang = size * defaults.dial_window_margin_fraction(self._skin)
        # THE FLIP, as ONE orchestrated turning move: the live layers
        # take the animated phase directly, and the cached segments —
        # painted once at the TARGET phase — are simply ROTATED by the
        # difference. Every baked member's rotation is phase-linear
        # (band, letters, crown, daylight arcs, umbra, star), so turning
        # the finished pixels is exactly turning all of them, and not
        # one plate is re-rendered mid-move. `flip_delta` is 0.0 the
        # instant the move ends, and always 0.0 in Geocentric.
        phase = self.phase_deg()
        flip_delta = phase - self._phase_target()
        if not flip_delta:
            # The turn is over (or none is running): the departing
            # phase's stashed segments have nothing left to fade.
            self._flip_from_composites = None
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=tick,
            daylight=tick.is_daylight,
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self.rotation(phase),
            world_offset=self.world_offset(phase),
            hovered=self._hovered,
            reveal_active=reveal, archetype_lit=archetype_lit,
            interior_scale=numeral_bands.interior_scale(
                self._skin.numeral_outer_ring_size
            ),
        )
        for kind, payload in self._steps:
            if kind == "cache":
                pixmap = self._composites[payload]
                if pixmap is None:
                    with profiling.measure("Composite rebuild"):
                        pixmap = self._render_group(
                            self._cached_groups[payload], size, dpr,
                        )
                    self._composites[payload] = pixmap
                if flip_delta:
                    painter.save()
                    painter.setRenderHints(_RENDER_HINTS)
                    painter.translate(size / 2, size / 2)
                    painter.rotate(flip_delta)
                    painter.translate(-size / 2, -size / 2)
                    painter.drawPixmap(QPointF(-overhang, -overhang), pixmap)
                    painter.restore()
                    # THE TURNING CROSSFADE: the departing phase's own
                    # finished pixels ride the SAME turn (rotated by
                    # their own delta, which differs by the half-turn)
                    # ON TOP, fading with the flip's eased progress —
                    # opaque over the arriving segment at the first
                    # frame, gone at the last, so the phase-dependent
                    # content (mirrored words, the Dollar's night
                    # mottos) dissolves mid-turn instead of snapping.
                    # Painted OVER the new segment rather than blended
                    # side-by-side, so the composite never dips below
                    # full opacity on the transparent desktop.
                    stash = self._flip_from_composites
                    old = stash[payload] if stash is not None else None
                    if old is not None:
                        painter.save()
                        painter.setRenderHints(_RENDER_HINTS)
                        painter.setOpacity(
                            painter.opacity()
                            * min(1.0, abs(flip_delta) / 180.0)
                        )
                        painter.translate(size / 2, size / 2)
                        painter.rotate(phase - self._flip_from_phase)
                        painter.translate(-size / 2, -size / 2)
                        painter.drawPixmap(
                            QPointF(-overhang, -overhang), old
                        )
                        painter.restore()
                    continue
                painter.drawPixmap(QPointF(-overhang, -overhang), pixmap)
                continue
            layer = payload
            if reveal and isinstance(layer, HandLayer):
                # The reveal window HIDES THE HANDS (owner seal
                # 2026-07-16) — the theme reads clean beneath.
                continue
            painter.save()   # isolate pen/brush/opacity/rotation leaks
            painter.setRenderHints(_RENDER_HINTS)
            painter.translate(size / 2, size / 2)
            layer.paint(painter, ctx_for_frame(ctx, layer.frame))
            painter.restore()

    def arm_angle_at(
        self, point: QPointF, radius: float, rotation: float
    ) -> float | None:
        """The unrotated arm angle whose DIAMOND contains `point`, or None
        (off the arms, Pointer off, or the arm-less Aurora/Calendar) — the
        ONE arm-diamond geometry (Rule #5) shared by the arm tooltip, the
        Spacebar jump and the archetype hover-enlarge."""
        if not self._skin.show_pointer or self._skin.pointer in (
            "aurora", "calendar"
        ):
            return None
        distance = math.hypot(point.x(), point.y())
        star_tip = radius * self.interior_hit(self._skin.star.radius_fraction)
        if not (radius * self.interior_hit(0.08) <= distance <= star_tip):
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        arms = constants.POINTER_POINTS[self._skin.pointer]
        arm_step = 360.0 / arms
        # The DRAWN geometry (Rule #5 with StarLayer): the offset wheels
        # swing their arms (the Genesis inversion, the Seasons rotation),
        # the Cube look widens the family wheels' halves to the full face
        # rhombi — and `arm_shape_path` hands back the very path the
        # layer paints, so the hover follows the star into the POLYGON
        # shape instead of hit-testing a diamond that is no longer there.
        offset = arm_offset_deg(self._skin)
        arm_angle = (
            offset
            + round(((theta - rotation - offset) % 360.0) / arm_step)
            * arm_step
        ) % 360.0
        shape = arm_shape_path(self._skin, star_tip, arm_angle + rotation)
        if not shape.contains(point):
            return None
        return arm_angle

    @profiling.timed("Hit test")
    def element_at(
        self, point: QPointF, radius: float, rotation: float, today: str
    ) -> str | None:
        """The enlargeable element under the cursor, in hover priority
        (Rule #5: ONE geometry shared by the tooltips and the
        hover-enlarge effect): a weekday body ("body:<name>"), the octa
        info slot, the Moon, the Earth."""

        def hit(center: QPointF, hit_radius: float) -> bool:
            dx, dy = point.x() - center.x(), point.y() - center.y()
            return dx * dx + dy * dy <= hit_radius * hit_radius

        weekday = self._skin.weekday_set
        # THE BLUE MOON LAW (owner overrule, CORRECTED 2026-07-2X): the
        # Calendar pointer's own dial center — otherwise EMPTY, since
        # its slot layout is always "pinned" (never "classic"/"center",
        # see render.slot_layout.slot_layout) — is its OWN hit target,
        # checked first; a showing 13th's hit disc mirrors the DRAWN
        # size exactly (`CenterBodyLayer._draw_thirteenth`).
        thirteenth = active_thirteenth(
            self._skin, self._day,
            self._last_tick.is_daylight if self._last_tick is not None else True,
        )
        if thirteenth is not None and hit(
            QPointF(0.0, 0.0),
            radius * self.interior_hit(weekday.center_scale)
            if weekday.display_mode == "center_only"
            else self.interior_hit(weekday_body_size(self._skin, radius) / 2),
        ):
            return "thirteenth"
        classic = None
        for index, seat in slot_layout(self._skin).items():
            if seat == "classic":
                classic = index
                continue
            # A SEATED slot's hit region mirrors the drawn spot exactly
            # (owner 2026-07-14: the hover-enlarge is an inherited
            # trait, whatever the slot shows).
            pos = (
                QPointF(0.0, 0.0)
                if seat == "center"
                else dial_point(
                    seat + slot_seat_rotation(self._skin, rotation),
                    radius * self.interior_hit(
                        weekday.orbit_fraction * slot_seat_orbit(self._skin, seat)
                    ),
                )
            )
            if hit(
                pos,
                radius * self.interior_hit(
                    weekday.diamond_scale * slot_seat_scale(self._skin)
                ),
            ):
                return f"slot:{index}"
        if classic is not None:
            body = self._weekday_body_at(point, radius, rotation, today)
            if body is not None:
                return f"body:{body}"
            if servant_holds_the_seat(self._skin, today) and hit(
                dial_point(
                    servant_seat_angle(self._skin) + rotation,
                    radius * self.interior_hit(weekday_body_orbit(self._skin)),
                ),
                radius * self.interior_hit(weekday.diamond_scale * slot_seat_scale(self._skin)),
            ):
                # The SERVANT face at his own seat — 24h on the
                # Compass/Seasons, the blue 06h/270° arm on the Rose
                # (`servant_seat_angle`) — ghosted all week, opaque on
                # Sunday (owner 2026-07-13; Rose bug fix 2026-07-28:
                # this used to hardcode the 24h Compass seat, so the
                # Rose's hover fired at the legacy bottom instead of
                # its own drawn blue arm).
                return "sun_servant"
        if archetype_active(self._skin):
            # The archetype CENTER (owner decree 2026-07-18, two-type
            # law) sits at the hub; its hit disc matches the DRAWN
            # figure — `archetype_figure_size` classifies the center's
            # OWN art exactly like ArchetypeCenterLayer does, halved to
            # a radius — hover-enlarge included; the Compass has none.
            key = archetype_key(self._skin)
            center = archetypes.center(key)
            if center is not None and hit(
                QPointF(0.0, 0.0),
                self.interior_hit(archetype_figure_size(self._skin, radius) / 2.0),
            ):
                return "archetype:center"
        # ONE SEAT, TWO READERS (owner question 2026-08-12: "how is the
        # hover not simply every time the cursor crosses that element's
        # own dimensions — what imaginary space is it following?"). It
        # was following one: this hit test used to RE-DERIVE where the
        # markers stand, so every relocation the painting learned had to
        # be copied here by hand, and each one that was not — the Moon's
        # rim-riding lane split, the transit shrink, and this round's
        # yielding of the band to an eclipse — left the cursor answering
        # at a seat nothing was drawn at any more. The copy is gone: the
        # three calls below are the SAME functions `YearMarkerLayer.paint`
        # draws with, so the target IS the drawn body, by construction.
        ctx = self._marker_ctx(radius)
        # THE THIRD BODY answers first, exactly as it is drawn last —
        # over both markers on the day it belongs to.
        body_event = self._last_tick.eclipse_body_event
        if self._skin.show_eclipse and body_event is not None:
            scale = eclipse_body_scale(ctx, body_event.kind == "solar")
            angle = eclipse_body_angle(ctx, body_event)
            if hit(
                dial_point(angle, radius * eclipse_body_orbit(ctx, angle, scale)),
                radius * scale,
            ):
                return "eclipse"
        if self._skin.show_moon and hit(
            dial_point(moon_marker_angle(ctx), radius * moon_marker_orbit(ctx)),
            radius * moon_marker_scale(ctx),
        ):
            return "moon"
        if self._skin.show_earth and hit(
            dial_point(earth_marker_angle(ctx), radius * earth_marker_orbit(ctx)),
            radius * earth_marker_scale(ctx),
        ):
            return "earth"
        if archetype_active(self._skin):
            # The archetype ARM figures inherit the slot hover-enlarge
            # (owner slika 8): the whole diamond is the target, the same
            # geometry the arm tooltip uses — checked AFTER the markers so
            # the Earth/Moon (the instrument) keep priority where they
            # overlap an arm.
            arm_angle = self.arm_angle_at(point, radius, rotation)
            if arm_angle is not None:
                return f"archetype:{self._archetype_arm_index(arm_angle)}"
        return None

    @paths.in_display
    def set_hover(self, x: float, y: float, size: float) -> bool:
        """Track the element under the cursor for the HOVER-ENLARGE
        effect (owner EXTRAS) — returns True when the target changed and
        the widget must repaint. Legend off keeps the dial fully inert;
        a factor of 1.0 disables the effect."""
        hovered = None
        if (
            self._day is not None
            and self._last_tick is not None
            and self._skin.legend
            and self._skin.hover_enlarge > 1.0
        ):
            radius = size / 2
            point = QPointF(x - radius, y - radius)
            today = week_registry.WEEKDAY_BODIES[self._day.weekday_index]
            hovered = self.element_at(point, radius, self.rotation(), today)
        if hovered == self._hovered:
            return False
        self._hovered = hovered
        # No composite drop (owner 2026-07-17, ROADMAP 15f): the weekday
        # bodies and archetype figures paint LIVE now, so the enlarge is
        # a handful of cached blits on the next frame — ZERO composite
        # rebuilds per hover enter/leave.
        return True

    def _weekday_body_at(
        self, point: QPointF, radius: float, rotation: float, today: str
    ) -> str | None:
        """The weekday body whose image region contains `point` — the
        visible slot occupants (shared slots resolve to the priority
        winner) plus the centered body (today in center_only mode; the
        Sun on the hexa/trio layouts)."""
        weekday = self._skin.weekday_set

        def hit(center: QPointF, hit_radius: float) -> bool:
            dx, dy = point.x() - center.x(), point.y() - center.y()
            return dx * dx + dy * dy <= hit_radius * hit_radius

        center_body: str | None = None
        if weekday.display_mode == "center_only":
            center_body = today
        elif self._skin.pointer in ("hexa", "trio"):
            center_body = "sun"          # today's opaque Sun or the ghost Sun
        if center_body is not None and hit(
            QPointF(0, 0),
            # The hit disc mirrors the DRAWN size (owner 2026-07-18):
            # hexa/trio centers match the diamond bodies; the
            # center-only showcase keeps center_scale — WITHOUT the
            # seat factor this path used to add (the disc overhung the
            # image by 1.5×).
            radius * self.interior_hit(weekday.center_scale)
            if weekday.display_mode == "center_only"
            else self.interior_hit(weekday_body_size(self._skin, radius) / 2),
        ):
            return center_body
        if weekday.display_mode == "center_only":
            return None                  # no slot bodies in this mode
        dual = servant_holds_the_seat(self._skin, today)
        seat = servant_seat_angle(self._skin)
        for angle, occupants in weekday_slots(self._skin):
            if dual and angle == seat:
                continue     # the Servant won his own seat today
            body = visible_occupant(occupants, today)
            slot = dial_point(
                angle + rotation,
                radius * self.interior_hit(weekday_body_orbit(self._skin)),
            )
            if hit(
                slot,
                radius * self.interior_hit(weekday.diamond_scale * slot_seat_scale(self._skin)),
            ):
                return body
        return None

    def _archetype_arm_index(self, arm_angle: float) -> int:
        """The figures-tuple index of an unrotated arm angle — the same
        k·(360/N) order archetype_lit_index counts in (Rule #5: one
        ordering shared by lighting, hovers and the Spacebar jump)."""
        arms = constants.POINTER_POINTS[self._skin.pointer]
        return int(round(arm_angle / (360.0 / arms))) % arms

    @paths.in_display
    def render_offscreen(
        self, size: float, dpr: float, day: DayContext, tick: TickState
    ) -> QImage:
        """Full frame into a QImage — tests and the settings preview."""
        self.set_day(day)
        px = round(size * dpr)
        image = QImage(px, px, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        image.setDevicePixelRatio(dpr)
        painter = QPainter(image)
        self.paint(painter, size, dpr, tick)
        painter.end()
        return image

    def _archetype_lit(self, tick: TickState) -> int | None:
        """The archetype figure whose HOUR-SPACE holds the hour hand
        (owner 2026-07-16), or None off the mode. Shared by the
        composite key and the figure render (Rule #5); the spaces ride
        the drawn arms, so the solar rotation feeds in."""
        if not archetype_active(self._skin):
            return None
        return archetype_lit_index(
            # The DRAWN hour hand carries the world offset, so the arm
            # it stands in must be judged on the drawn angle; the arms
            # themselves keep the pointer rotation. Both terms are 0 in
            # Geocentric, leaving this exactly what it was.
            self._skin.pointer, tick.hour_angle + self.world_offset(),
            self.rotation(), arm_offset_deg(self._skin),
        )

    def _render_group(
        self, layers: list[Layer], size: float, dpr: float,
    ) -> QPixmap:
        """Rasterize ONE contiguous run of hover-invariant STATIC/DAILY
        layers into a padded pixmap (owner 2026-07-17, ROADMAP 15f).
        These layers include the ring jewels, which OVERHANG the dial
        square (owner spec) — the pixmap is padded by the same LIVE
        margin the window carries (owner 2026-07-17), or they clip right
        here (owner bug report: the Omega's bottom was cut flat). Hover
        and reveal are deliberately ABSENT — those layers paint live — so
        this pixmap survives every hover enter/leave."""
        overhang = size * defaults.dial_window_margin_fraction(self._skin)
        px = round((size + 2 * overhang) * dpr)
        pixmap = QPixmap(px, px)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHints(_RENDER_HINTS)
        painter.scale(dpr, dpr)
        painter.translate(size / 2 + overhang, size / 2 + overhang)
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=None,
            daylight=(self._last_tick.is_daylight
                      if self._last_tick is not None else True),
            radius=size / 2, cache=self._cache, dpr=dpr,
            # The TARGET phase, never the animated one — see `paint`.
            rotation=self.rotation(self._phase_target()),
            world_offset=self.world_offset(self._phase_target()),
            hovered=None,
            reveal_active=False, archetype_lit=None,
            interior_scale=numeral_bands.interior_scale(
                self._skin.numeral_outer_ring_size
            ),
        )
        for layer in layers:
            painter.save()   # isolate pen/brush/opacity/rotation leaks
            layer.paint(painter, ctx_for_frame(ctx, layer.frame))
            painter.restore()
        painter.end()
        pixmap.setDevicePixelRatio(dpr)
        return pixmap
