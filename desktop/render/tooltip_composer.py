"""THE TOOLTIP COMPOSER — everything the dial SAYS.

Every hover the dial answers is built here: the arm legends, the weekday
bodies, the tick readout, the ring's jewels and words, the crown, the
moon, the eclipses, the Earth, the calendar wedges, the twilight bands —
and the Encyclopedia TARGET each of them jumps to when the reader presses
SPACE.

It was ~2,400 lines inside `render/compositor.py`, a module whose job is
to stack paint layers and answer hit tests (OOP audit 2026-08-18, section
3: "measured method by method: 2,126 lines of tooltip / article HTML, 775
of paint and geometry"). Two responsibilities, one file, and the audit
graded the cut HIGH RISK for a reason: these are METHODS over shared
state, not free functions.

So this is a COLLABORATOR, not a file move. It holds the dial and asks it
for two things, and nothing else:

* **STATE**, through the dial's own read-only properties — `skin`, `day`,
  `tick`, `overlay`, `encyclopedia`, `symbolism`, `hidden_unlocked`. Read
  live on every call, so a re-installed skin or a new day context can
  never leave a stale copy here. That is why the composer holds the DIAL
  and not the values.
* **GEOMETRY**, through nine public questions — `element_at`,
  `interior_hit`, `world_theta`, `world_offset`, `rotation`,
  `jewel_offset`, `jewel_theta`, `arm_angle_at`, `band_hit`. A tooltip
  must name the same thing the paint drew, so it asks the painter rather
  than re-deriving the angles.

The dial keeps `tooltip_at`, `encyclopedia_target` and
`warm_hover_articles` as one-line doors, because that is what the widget
and twenty test files call.

Layer: render. Documentation: __about/tooltip_composer.md.
"""

import html
import json
import math
from datetime import datetime, time, timedelta
from functools import lru_cache

from PySide6.QtCore import QPointF

from config import archetypes, calendar_mounts, complications, constants, defaults, dial, encyclopedia_ui, glow, pantheon, paths, pointer_geometry, profiling, sky
from config.ui_text import ui
from config.registry import week as week_registry
from core import angles, continents, world
from core.deep_time import (
    format_anno_lucis, format_official, format_year_line, is_age_of_light,
    real_year,
)
from core.moon import nominal_illumination, phase_name
from core.year_wheel import (
    instant_at_marker_angle, meteorological_span, zodiac_span,
)
from render.article_html import (
    article_body_html, article_html, article_paragraphs, centered,
    centered_html, hover_badge, hover_title, learn_more_footer, ordinal,
    teaser,
)
from render.asset_recolor import metal_variant_file
from render.asset_variants import eclipse_solar_type_icon, scaled_variant_file
from render.archetype_geometry import archetype_art_ready
from render.calendar_mount import chinese_mount_dimmed_index
from render.layers.year_marker import earth_region
from render.ninths import (
    active_thirteenth, center_face, dual_seat_ninth, ninth_window_anchor,
    theme_ninth, thirteenth_plate,
)
from render.painting import dial_point
from render.skin_geometry import archetype_key, palette_for, weekday_slots
from render.slot_layout import (
    center_dual_face, slot_view, sunday_dual_face, weekday_classic_slot,
)


def _crown_arc_centre(entry: dict) -> float:
    """One crown-text entry's own arc centre — the axis THE ARC READING
    LAW reflects about (`core.world.arc_centre_deg`). Computed from the
    SAME glyph seats `render.layers.ring.RingLayer._draw_crown_text`
    passes to `arc_seats` (Rule #5), so a word's hover zone and its
    drawn letters can never disagree about where the arc went."""
    return world.arc_centre_deg([theta for _asset, theta in entry["glyphs"]])


@lru_cache(maxsize=1)
def _greetings() -> dict:
    """The owner's Four Greetings (Database/verses.json) — Serbian in
    every language, shown only in the unlocked hidden mode."""
    return json.loads(
        (paths.database_dir() / "verses.json").read_text(encoding="utf-8")
    )["trinity"]


# South of the equator the year wheel runs mirrored (+180°) — these
# unwrapped anchor angles trade places (June solstice <-> December,
# March equinox <-> September).
_SOUTH_ANCHOR_FLIP = {270.0: 450.0, 360.0: 540.0, 450.0: 270.0, 540.0: 360.0}

# The Astrology encyclopedia topic lists its signs in astronomical
# order (Aries first), NOT the year-wheel order of constants.ZODIAC_SIGNS
# — the Spacebar jump (owner 2026-07-16, ROADMAP queue #8) indexes into
# this order to open the hovered sign's page.
_ENC_ZODIAC_ORDER = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

# The weekday encyclopedia topics list their seven bodies in this order
# (Sun first) — the Spacebar jump indexes a hovered body's page by it,
# mirroring app.encyclopedia._WEEK_ORDER.
_ENC_WEEK_ORDER = (
    "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
)

# The SEASONS / SUN / TRINITY encyclopedia topics list their entries in
# these fixed orders (app.encyclopedia._SEASON_ENTRIES / _SUN_ENTRIES /
# the trinity topic) — the Spacebar jump (owner 2026-07-16, "sve znači
# SVE") indexes the hovered season / turning point / virtue by them.
_ENC_SEASON_ORDER = (
    "Spring", "Summer", "Autumn", "Winter",
    "Wet_Season", "Dry_Season", "Meteorological",
)
_ENC_SUN_ORDER = ("Summer_Solstice", "Winter_Solstice", "Equinox")
# THE ORDER LAW (owner decree 2026-08-09): Faith — Love — Hope in
# every display; mirrors the trinity topic's own entry order.
_ENC_TRIO_ORDER = ("Faith", "Love", "Hope")

# The ECLIPSE chapter order per body (fix round F, owner order
# 2026-07-19) — the Spacebar jump indexes an active eclipse's TYPE
# (capitalized) into these, mirroring app.encyclopedia's
# `_ECLIPSE_SOLAR_ENTRIES`/`_ECLIPSE_LUNAR_ENTRIES` (entry-zero is the
# body Overview). `hybrid` keeps its OWN chapter here — the render state
# table folds it into solar_total, but the reader gets the distinct
# page. An unknown/missing type falls to the Overview (index 0).
_ENC_ECLIPSE_SOLAR_ORDER = ("Overview", "Total", "Annular", "Partial", "Hybrid")
_ENC_ECLIPSE_LUNAR_ORDER = ("Overview", "Total", "Partial", "Penumbral")

# THE BLUE MOON LAW's four members' own Spacebar page (owner overrule,
# CORRECTED 2026-07-2X): `app.encyclopedia._topics`' ONE FIXED append
# order, mirrored here exactly like every other `_ENC_*_ORDER` constant
# above. Ophiuchus/The Cat close the "astrology"/"chinese" GALLERY
# topics (their shared ninth-append loop's LAST entries — their
# ARTICLE TEXT family is "ninths", `constants.THIRTEENTHS`, but the
# gallery page that opens lives in their own zodiac topic, never a
# literal "ninths" topic, which does not exist); Sol/Modrenik close
# "months" (the Overview entry, the twelve Slavic months, THEN the
# pair, `app.encyclopedia._topics`'s own append order).
_ENC_OPHIUCHUS_INDEX = len(_ENC_ZODIAC_ORDER)
_ENC_CAT_INDEX = len(constants.CHINESE_ANIMALS) + len(constants.CHINESE_ELEMENTS)
_ENC_SOL_INDEX = len(calendar_mounts.SLAVIC_MONTHS) + 1
_ENC_MODRENIK_INDEX = _ENC_SOL_INDEX + 1

_ENC_THIRTEENTH_TARGET = {
    "ophiuchus": ("astrology", _ENC_OPHIUCHUS_INDEX),
    "chinese": ("chinese", _ENC_CAT_INDEX),
    "sol": ("months", _ENC_SOL_INDEX),
    "modrenik": ("months", _ENC_MODRENIK_INDEX),
}

_MONTHS = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)
_MONTHS_SHORT = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
    "Oct", "Nov", "Dec",
)


class TooltipComposer:
    """Everything the dial says, over the dial it says it about."""

    def __init__(self, dial):
        #: The `Compositor` this composer speaks for. Held rather than
        #: copied from, so every answer reads the LIVE skin, day and tick.
        self._dial = dial

    @property
    def _skin(self):
        """THE DISPLAY CONTEXT's hook: `config.paths.in_display` reads
        `self._skin.display` off whatever object it decorates, and three
        of the entry points below wear it. Named the way that decorator
        expects ("the two classes name the field identically"), and
        resolved through the dial, so it is never a stale copy."""
        return self._dial.skin

    def _tr(self, text: str) -> str:
        """The active language's form of a hover label (Phase 2b)."""
        return ui(self._dial.overlay, text)

    def _ord(self, n: int) -> str:
        """English keeps the raised suffix (owner spec); every other
        language reads the standard European "12."."""
        return f"{n}." if self._dial.overlay else ordinal(n)

    def _month(self, when) -> str:
        return self._tr(_MONTHS[when.month - 1])

    def _month_short(self, when) -> str:
        return self._tr(_MONTHS_SHORT[when.month - 1])

    def _year(self, when) -> str:
        """A hover date's YEAR through the ONE pairing formatter
        (Session 16, owner amendment 2026-07-17): the official year
        with the Anno Lucis year always beside it — "2026 · 6105. Anno
        Lucis" — plus the optional third calendar; the real
        astronomical year un-shifts the deep proxy frame first. Every
        hover that prints a year prints it via this."""
        return format_year_line(
            real_year(when.year, self._dial.day.deep_cycles),
            self._dial.skin.era_notation,
            self._dial.skin.show_era_suffix,
            self._dial.skin.third_era,
            when.month,
            when.day,
        )

    @profiling.timed("Hover text")
    @paths.in_display
    def tooltip_at(self, x: float, y: float, size: float) -> str | None:
        """Hover text under the cursor, at every dial size (owner spec):
        today's body, the Earth marker (day/week ordinals, zodiac sign
        with its dates, the date — plus the season event while it glows),
        the Moon marker (phase + illumination, day in the cycle), the
        octa zodiac slot and the twilight bands. The timed shell over
        `_tooltip_at` — the background warm sweep calls the impl
        directly so the owner's Hover text profile keeps measuring
        REAL hovers only. THE HOVER TEASER LAW's footer rides HERE:
        every hover that owns an Encyclopedia page closes with the
        clickable LEARN MORE link and the SPACE hint (the warm sweep,
        calling the impl, never builds footers)."""
        tip = self._tooltip_at(x, y, size)
        if tip is None:
            return None
        if self.encyclopedia_target(x, y, size) is not None:
            tip += learn_more_footer(self._tr)
        return tip

    def _tooltip_at(self, x: float, y: float, size: float) -> str | None:
        if self._dial.day is None or self._dial.tick is None:
            return None
        if not self._dial.skin.legend:
            # Legend off (owner spec): NO hovers at all — combined with
            # click-through the dial has zero interaction.
            return None
        radius = size / 2
        point = QPointF(x - radius, y - radius)      # center-origin
        rotation = self._dial.rotation()
        today = week_registry.WEEKDAY_BODIES[self._dial.day.weekday_index]

        element = self._dial.element_at(point, radius, rotation, today)
        if element is not None:
            if element == "thirteenth":
                # THE BLUE MOON LAW (owner overrule, CORRECTED
                # 2026-07-2X): the Calendar pointer's OWN dial center,
                # otherwise empty — its own element, never piggybacking
                # on a weekday body key (no other pointer carries this
                # seat at all now).
                return self._thirteenth_tooltip(self._active_thirteenth())
            if element.startswith("slot:"):
                # A SEATED slot (owner matrix 2026-07-14) speaks its
                # own content: the sign, the rising sign, the Chinese
                # year, or its theme's weekday article. The digital
                # modes (time/date/day length/seconds) have no reading
                # of their own — the hover-ENLARGE still works, the
                # region hovers take over below.
                mode, style, theme, metal, roster = slot_view(
                    self._dial.skin, int(element[len("slot:"):])
                )
                if mode == "ascendant":
                    return self._ascendant_text(style)
                if mode == "chinese":
                    return self._chinese_text(style)
                if mode == "zodiac":
                    return self._zodiac_text(style)
                if mode == "weekday":
                    return self._weekday_tooltip(
                        today, active=True, theme=theme,
                        slot_metal=metal, roster=roster,
                    )
            if element == "archetype:center":
                # The Eye / Hearth / Seal / Union / Throne speak their
                # CANON paragraph — gracefully pending until Session 6
                # writes the set (owner 2026-07-16).
                return self._archetype_center_tooltip()
            if element.startswith("archetype:"):
                # An archetype ARM figure (owner slika 8): its TWO-ROW
                # article — or the three-side Ages layout (owner slika 6).
                return self._archetype_arm_tooltip(
                    int(element[len("archetype:"):])
                )
            if element == "sun_servant":
                # The SERVANT face at his seat (owner 2026-07-13): its
                # own name, its own plate, its own text — except in the
                # solar NOON window (owner seal 2026-07-29), when the
                # NINTH borrows this seat and the card speaks the pair
                # actually standing (GOOD + NINTH), like the center law.
                if self._dual_seat_taken() == "servant":
                    return self._dual_face_columns(
                        self._dial.skin.weekday_theme, ("ruler", "ninth")
                    )
                return self._sun_face_tooltip(
                    "servant", active=today == "sun"
                )
            if element.startswith("body:"):
                # Weekday hover rework (owner spec): the ACTIVE body
                # leads with the date, ghosts show their article alone.
                body = element[len("body:"):]
                if body == "sun" and sunday_dual_face(self._dial.skin):
                    # The Ruler's seat speaks the RULER face alone
                    # (owner 2026-07-13) — the Servant's seat has its
                    # own hover — except in the solar MIDNIGHT window
                    # (owner seal 2026-07-29), when the NINTH borrows
                    # this seat and the card speaks the standing pair.
                    if self._dual_seat_taken() == "ruler":
                        return self._dual_face_columns(
                            self._dial.skin.weekday_theme, ("servant", "ninth")
                        )
                    return self._sun_face_tooltip(
                        "ruler", active=today == "sun"
                    )
                if body == "sun" and center_dual_face(self._dial.skin):
                    # The Prism/Trinity/center_only CENTER seat (round
                    # R3b items 3/4): a 2-face theme speaks BOTH sides
                    # always; a 3-face theme speaks GOOD alone outside
                    # its solar windows, the matching TWO-COLUMN card
                    # inside them.
                    return self._center_dual_tooltip(active=today == "sun")
                # The classic unit may be DRIVEN by the 2nd slot
                # (owner 2026-07-15) — the hover speaks that theme,
                # in that slot's OWN roster and metal.
                if weekday_classic_slot(self._dial.skin) == 2:
                    return self._weekday_tooltip(
                        body, active=body == today,
                        theme=self._dial.skin.info_slot_theme,
                        slot_metal=self._dial.skin.info_slot_metal,
                        roster=self._dial.skin.info_slot_roster,
                    )
                return self._weekday_tooltip(body, active=body == today)
            if element == "eclipse":
                # THE THIRD BODY SPEAKS FOR ITSELF (owner correction
                # 2026-08-12) — never the Earth's card again.
                return self._eclipse_text()
            if element == "moon":
                return self._moon_text()
            if element == "earth":
                return self._earth_text()
            # The digital slots fall through to the region hovers.

        # The ring TICK band FIRST (owner 2026-07-12: in that narrow
        # annulus the circle outranks the twilight wedge under it) —
        # the 360 arrows answer with what their ANGLE means on every
        # wheel.
        tick = self._tick_tooltip(point, radius)
        if tick is not None:
            return tick
        # Twilight bands BEFORE the arm hovers (owner: the dawn/dusk
        # info must never be shadowed — e.g. by a glowing quarter moon
        # sitting right on the 06h/18h band).
        twilight = self._twilight_tooltip(point, radius)
        if twilight is not None:
            return twilight

        arm = self._arm_tooltip(point, radius, rotation)
        if arm is not None:
            return arm
        # The Calendar wedges (owner 2026-07-16): a lit-capable wedge
        # answers with its month + double-hour animal (Almanac) or its
        # sign + dates (Zodiac). The wheel covers the whole dial, so it
        # pre-empts the day/night period hover below. The MOUNTED 12-set
        # mark (DESIGN ZODIAC law, R9a round) is a smaller, more specific
        # target sitting INSIDE that same area — it outranks the broad
        # wedge hover, checked first.
        if self._dial.skin.pointer == "calendar":
            mount = self._calendar_mount_tooltip(point, radius)
            if mount is not None:
                return mount
            calendar = self._calendar_tooltip(point, radius)
            if calendar is not None:
                return calendar
        # Last in the chain (owner rework 5 & 6): the sunlit arc answers
        # with the day, the dark of the wheel with the night.
        return self._period_tooltip(point, radius)

    @profiling.timed("Hover warmup")
    @paths.in_display
    def warm_hover_articles(
        self, size: float, should_stop=None, progress=None
    ) -> int:
        """Pre-build EVERY hover article this skin can speak TODAY, off
        the GUI thread (owner 2026-07-18, asked twice: the user never
        hovers in the first seconds after launch — spend them loading,
        so the FIRST hover is as instant as the tenth). The sweep walks
        a dense polar grid through the REAL `_tooltip_at` dispatch — no
        second file-resolution path to drift — so every article builds
        once and every embedded image's downscaled variant lands in the
        disk cache (and the OS file cache: that IS the in-RAM copy the
        tooltip loads instantly afterwards). Grid pitch ≈ half the
        smallest hover target (the Moon marker), so nothing slips
        between probes; a probe that finds no element costs
        microseconds. Ring-paced with a short sleep — slow and polite,
        image by image, per the owner's spec. Re-run on skin install
        and day change (`should_stop` aborts a sweep the controller
        obsoleted); a warm re-run costs header reads only. Returns how
        many probes spoke an article."""
        from time import sleep

        if self._dial.day is None or self._dial.tick is None:
            return 0
        if not self._dial.skin.legend:
            # LEGEND OFF speaks no hovers at all (owner spec — see
            # `_tooltip_at`'s own guard), so every probe below would
            # return None. Measured on the owner's 2026-07-28 startup
            # log: three watches, all with the legend off, each walking
            # 7,201 probes to report "0 articles spoken" — pure Python,
            # pure GIL, pure waste. Warming what cannot be shown is a
            # bug; the sweep stands down instead.
            return 0
        spoken = 0
        radius = size / 2
        rings = encyclopedia_ui.HOVER_WARM_RADIAL_STEPS
        angles = encyclopedia_ui.HOVER_WARM_ANGLE_STEPS
        # Center first (the hexa/trio Sun, center seats), then the rings.
        if self._tooltip_at(radius, radius, size) is not None:
            spoken += 1
        for ring in range(1, rings + 1):
            fraction = ring / rings
            for step in range(angles):
                if should_stop is not None and should_stop():
                    return spoken
                theta = math.radians(step * 360.0 / angles)
                if self._tooltip_at(
                    radius + math.sin(theta) * radius * fraction,
                    radius - math.cos(theta) * radius * fraction,
                    size,
                ) is not None:
                    spoken += 1
            if progress is not None and ring % 10 == 0:
                progress(
                    f"hover warmup ring {ring}/{rings} "
                    f"({spoken} articles spoken)"
                )
            sleep(encyclopedia_ui.HOVER_WARM_RING_PAUSE_S)
        return spoken

    @paths.in_display
    def encyclopedia_target(
        self, x: float, y: float, size: float
    ) -> tuple[str, int] | None:
        """The (topic key, entry index) the Encyclopedia should open on
        for the element under the cursor — the ONE element→topic mapping
        (owner 2026-07-16, ROADMAP queue #8; "sve znači SVE" correction):
        EVERY hover that speaks a text with an encyclopedia page opens
        it. Works whether or not the legend is visible (it reuses the
        hover GEOMETRY, not the tooltip text). Priority mirrors
        `tooltip_at`: the enlargeable elements first (weekday bodies —
        classic AND seated slots, each in its OWN theme/roster — the
        zodiac / ascendant / Chinese slots, the Moon at its phase, the
        Earth at its season), then the star arms (hexa signs, cross/octa
        solstice-equinox and season events, trio virtues), then the
        Calendar wedges. Elements with no page — the digital slots, the
        twilight bands, the ring band — return None."""
        if self._dial.day is None or self._dial.tick is None:
            return None
        radius = size / 2
        point = QPointF(x - radius, y - radius)
        rotation = self._dial.rotation()
        today = week_registry.WEEKDAY_BODIES[self._dial.day.weekday_index]
        element = self._dial.element_at(point, radius, rotation, today)
        if element is not None:
            return self._element_encyclopedia_target(element, today)
        arm = self._arm_encyclopedia_target(point, radius, rotation)
        if arm is not None:
            return arm
        if self._dial.skin.pointer == "calendar":
            return self._calendar_wedge_target(point, radius)
        return None

    def _weekday_encyclopedia_target(
        self, body: str, theme: str
    ) -> tuple[str, int] | None:
        """(theme topic, body page index) for a weekday body dressed in
        `theme` — the classic unit's theme OR a seated slot's own theme.
        None when the theme carries no encyclopedia topic."""
        if body in _ENC_WEEK_ORDER and theme in pantheon.WEEKDAY_THEME_TITLES:
            return theme, _ENC_WEEK_ORDER.index(body)
        return None

    def _element_encyclopedia_target(
        self, element: str, today: str
    ) -> tuple[str, int] | None:
        """The page for one enlargeable element (`_element_at` output).
        Seated weekday slots and the pinned classic bodies resolve the
        slot's OWN theme/roster; the Moon opens at its current phase, the
        Earth at its current season."""
        if element == "thirteenth":
            # THE BLUE MOON LAW (owner overrule, CORRECTED 2026-07-2X):
            # each of the four members opens ITS OWN gallery page —
            # `_ENC_THIRTEENTH_TARGET` mirrors app.encyclopedia._topics'
            # fixed append order, exactly like every other _ENC_*_ORDER
            # lookup in this module. None only if hovered without a live
            # `_active_thirteenth` (should not happen — the hit-test
            # itself is already gated on it), never a crash.
            key = self._active_thirteenth()
            return _ENC_THIRTEENTH_TARGET.get(key) if key is not None else None
        if element == "eclipse":
            # THE ECLIPSE'S OWN JUMP (owner order 2026-08-12): Space over
            # the third body opens ITS chapter. It used to hang off the
            # Earth/Moon markers, which is exactly the confusion the owner
            # named — the marker's own page is its own again below.
            eclipse = self._dial.tick.eclipse_body_event
            return (
                None if eclipse is None
                else self._eclipse_encyclopedia_target(eclipse)
            )
        if element == "moon":
            return "moon", sky.MOON_PHASE_NAMES.index(
                phase_name(self._dial.tick.moon_fraction)
            )
        if element == "earth":
            return "seasons", self._season_topic_index()
        if element == "archetype:center":
            # THE CENTRE'S OWN TARGET (One Soul round 2026-07-27): a
            # center table may declare an `enc` exactly like an arm
            # figure does — the One Soul wheel's Union is the first that
            # has a page to land on. Every other centre simply carries no
            # `enc` and answers None, unchanged.
            center = archetypes.center(archetype_key(self._dial.skin))
            return None if center is None else center.get("enc")
        if element.startswith("archetype:"):
            # An archetype ARM figure (owner slika 8): its OWN target —
            # today only the Walks map onto the Professions pages; the
            # rest answer None gracefully (Sessions 6/8 add topics).
            index = int(element[len("archetype:"):])
            return archetypes.figures(archetype_key(self._dial.skin))[index]["enc"]
        if element.startswith("slot:"):
            mode, _style, theme, _metal, _roster = slot_view(
                self._dial.skin, int(element[len("slot:"):])
            )
            if mode == "zodiac":
                return (
                    "astrology",
                    _ENC_ZODIAC_ORDER.index(self._dial.day.zodiac_name),
                )
            if mode == "ascendant":
                return (
                    "astrology",
                    _ENC_ZODIAC_ORDER.index(self._dial.tick.ascendant_sign),
                )
            if mode == "chinese":
                animal = self._dial.day.chinese_name.split()[1]
                return "chinese", constants.CHINESE_ANIMALS.index(animal)
            if mode == "weekday":
                # A seated weekday slot shows TODAY's body in the slot's
                # OWN theme (owner failing case: Zeus / the Egyptian body
                # seated at 4h/20h) — its page is that theme's body page.
                return self._weekday_encyclopedia_target(today, theme)
            return None                       # a digital face — no page
        if element.startswith("body:") or element == "sun_servant":
            body = "sun" if element == "sun_servant" else element[len("body:"):]
            # The classic unit may be DRIVEN by the 2nd slot (owner
            # 2026-07-15) — its page then follows THAT slot's theme,
            # including under the Calendar's pinned layout.
            theme = (
                self._dial.skin.info_slot_theme
                if weekday_classic_slot(self._dial.skin) == 2
                else self._dial.skin.weekday_theme
            )
            return self._weekday_encyclopedia_target(body, theme)
        return None

    def _current_season_key(self) -> str:
        """The Encyclopedia SEASONS key for the current date — a
        temperate season ("Spring".."Winter") or a tropical half
        ("Wet_Season"/"Dry_Season"). Mirrors `_season_row`."""
        day = self._dial.day
        noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
        if day.zone == "tropics":
            _start, _end, is_wet = self._wet_dry_span_at(noon)
            return "Wet_Season" if is_wet else "Dry_Season"
        events = day.season_events
        index = max(
            i for i, (instant, _) in enumerate(events) if instant <= noon
        )
        return events[index][1].split()[0]    # the season STARTS at its event

    def _season_topic_index(self) -> int:
        """The Earth marker's SEASONS page (owner 2026-07-16): the
        current season's entry, or the topic head when none matches."""
        key = self._current_season_key()
        return _ENC_SEASON_ORDER.index(key) if key in _ENC_SEASON_ORDER else 0

    def _sun_topic_index(self, event_name: str) -> int:
        """The SUN page for a cardinal-arm turning point — the event
        name is zone-correct (south already flips it)."""
        if "Equinox" in event_name:
            return _ENC_SUN_ORDER.index("Equinox")
        if "Summer" in event_name:
            return _ENC_SUN_ORDER.index("Summer_Solstice")
        return _ENC_SUN_ORDER.index("Winter_Solstice")

    def _eclipse_encyclopedia_target(self, eclipse) -> tuple[str, int]:
        """The (topic, entry) for the active eclipse's CATEGORY chapter
        (fix round F, owner order 2026-07-19) — the SOLAR topic for a
        solar eclipse, LUNAR for lunar, indexed by the eclipse's TYPE
        (the same vocabulary the state table maps). An unknown/missing
        type lands on the body Overview (index 0), never a crash — the
        catalog only ever writes the known vocabulary, so this is the
        documented fallback, not an expected path."""
        if eclipse.kind == "solar":
            topic, order = "eclipse_solar", _ENC_ECLIPSE_SOLAR_ORDER
        else:
            topic, order = "eclipse_lunar", _ENC_ECLIPSE_LUNAR_ORDER
        label = eclipse.type.capitalize()
        return topic, order.index(label) if label in order else 0

    def _eclipse_emblem(self, eclipse):
        """The active eclipse's category emblem Path (fix round F, owner
        slika 7 — the hover-card badge), or None for an unknown type;
        `hover_badge(None)` degrades to empty, so a missing/unknown
        emblem simply shows no image (graceful-absent)."""
        stem = glow.ECLIPSE_TYPE_EMBLEM.get((eclipse.kind, eclipse.type))
        return glow.ECLIPSE_ART_DIR / f"{stem}.png" if stem else None

    def _arm_encyclopedia_target(
        self, point: QPointF, radius: float, rotation: float
    ) -> tuple[str, int] | None:
        """The page for the star arm under the cursor (owner 2026-07-16,
        "sve znači SVE"): hexa diamonds → the zodiac sign; cross/octa
        CARDINAL arms → the Sun topic's solstice/equinox; octa DIAGONAL
        arms → the Seasons topic's season (or tropical half); trio arms →
        the Trinity virtue. None off the arms or on the pointer-less
        wheels. (In archetype mode the ARM figures answer through
        `_element_at`/`_element_encyclopedia_target`, not here.)"""
        arm_angle = self._dial.arm_angle_at(point, radius, rotation)
        if arm_angle is None:
            return None
        pointer = self._dial.skin.pointer
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        if pointer == "hexa":
            # The cursor's half of the 60° arc picks which of the two signs.
            rel = ((theta - rotation - arm_angle + 180.0) % 360.0) - 180.0
            start_angle = (arm_angle + (-30.0 if rel < 0.0 else 0.0)) % 360.0
            if self._dial.day.southern_hemisphere:
                start_angle = (start_angle + 180.0) % 360.0
            return (
                "astrology",
                _ENC_ZODIAC_ORDER.index(
                    constants.ZODIAC_SIGNS[int(start_angle) // 30][0]
                ),
            )
        if pointer == "trio":
            if self._dial.skin.palette_style == "tertiary":
                # The Genesis offices have no Encyclopedia pages yet
                # (Session 21 writes the Cube section) — the Spacebar
                # jump does nothing here, gracefully, exactly like the
                # figure targets of every unwritten archetype.
                return None
            theme = archetypes.TRIO_ARM_THEMES[arm_angle]
            return "trinity", _ENC_TRIO_ORDER.index(theme)
        if arm_angle % 90.0 == 0.0:
            # Cardinal arms (cross and octa) point at the turning points.
            anchor_angle = {
                0.0: 360.0, 90.0: 450.0, 180.0: 540.0, 270.0: 270.0
            }[arm_angle]
            if self._dial.day.southern_hemisphere:
                anchor_angle = _SOUTH_ANCHOR_FLIP[anchor_angle]
            index = self._dial.day.year_anchors.angles.index(anchor_angle)
            return "sun", self._sun_topic_index(
                self._dial.day.season_events[index][1]
            )
        # Octa diagonal arms point at the QUARTER centers — the seasons.
        start_angle = {
            315.0: 270.0, 45.0: 360.0, 135.0: 450.0, 225.0: 540.0
        }[arm_angle]
        if self._dial.day.southern_hemisphere:
            start_angle = _SOUTH_ANCHOR_FLIP[start_angle]
        if self._dial.day.zone == "tropics":
            starts_in_march = start_angle in (270.0, 360.0)
            is_wet = starts_in_march != self._dial.day.southern_hemisphere
            return "seasons", _ENC_SEASON_ORDER.index(
                "Wet_Season" if is_wet else "Dry_Season"
            )
        return "seasons", _ENC_SEASON_ORDER.index(
            self._season_name_for(start_angle)
        )

    def _calendar_wedge_target(
        self, point: QPointF, radius: float
    ) -> tuple[str, int] | None:
        """The (topic, entry) for the Calendar wedge under the cursor
        (owner 2026-07-16, the Spacebar jump) — Almanac wedges open the
        Chinese animal, Zodiac wedges the sign. Mirrors the
        _calendar_tooltip angle math."""
        from render.calendar_mount import calendar_wheel

        distance = math.hypot(point.x(), point.y())
        outer = radius * self._dial.interior_hit(self._dial.skin.background.aura_radius_fraction)
        if not (radius * self._dial.interior_hit(0.08) <= distance <= outer):
            return None
        theta = self._dial.world_theta(point)
        step = pointer_geometry.CALENDAR_WEDGE_DEG
        if calendar_wheel(self._dial.skin) == "almanac":
            index = int((theta + step / 2.0) // step) % 12
            return "chinese", (index - 6) % 12
        start_angle = int(theta // step) * step
        if self._dial.day.southern_hemisphere:
            start_angle = (start_angle + 180.0) % 360.0
        name = constants.ZODIAC_SIGNS[int(start_angle) // 30][0]
        return "astrology", _ENC_ZODIAC_ORDER.index(name)

    def _combo_key(self) -> str:
        """The (pointer, palette) combination the WEEKDAY articles vary
        by — "hexa_primary", "octa_secondary", "cross", "trio". The trio
        still collapses although it gained the Family SECONDARY wheel
        (2026-07-16): the shipped article variants carry one "trio"
        paragraph, and the archetype articles vary by their own grid
        sets instead — a trio_secondary variant wave is Session 6's call."""
        pointer = self._dial.skin.pointer
        if pointer in ("cross", "trio"):
            return pointer
        return f"{pointer}_{self._dial.skin.palette_style}"

    def _weekday_tooltip(
        self, body: str, active: bool, theme: str | None = None,
        slot_metal: str | None = None, roster: str | None = None,
    ) -> str:
        """The body's ARTICLE — its themed art on top, then the entity
        NAME as a bigger title (owner spec 2026-07-11: the god / planet
        / calling the medallion shows), base plus the paragraph of the
        ACTIVE (pointer, palette) combination; the active day adds
        "Thursday, 9th July 2026" under the name (owner spec), ghosts
        show name and article alone. `theme` overrides the main theme
        (the info slot's second weekday, owner 2026-07-12). The SUN
        shows BOTH Sunday plates side by side wherever it appears as
        one image (owner 2026-07-13) — the extended base text already
        tells the two faces."""
        theme = theme or self._dial.skin.weekday_theme
        article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
        article_body = body
        # THE UNIVERSAL ROTATION CONVENTION (weekday ALT ROTATION round
        # 2026-07-20/21): `self._dial.day` is None before the first tick
        # (this method is unit-tested directly, `self._dial.day` unset —
        # `test_seated_slot_wears_its_own_roster`) — the SAME graceful-
        # absent guard `_center_ninth_alt` already uses for the identical
        # hazard.
        on_date = self._dial.day.local_date if self._dial.day is not None else None
        # The weekday-set shortcut holds only while the ROSTER matches
        # too (owner 2026-07-15: slot 1 Greek Planetary beside slot 2
        # Greek Pantheon — same theme, two casts); a caller that names
        # no roster follows the set as dressed.
        same_unit = theme == self._dial.skin.weekday_theme and roster in (
            None,
            "pantheon"
            if self._dial.skin.weekday_set.body_articles is not None
            else "planetary",
        )
        if same_unit and self._dial.skin.weekday_set.body_articles is not None:
            # The PANTHEON roster (owner 2026-07-15): each seat's
            # article follows the FIGURE actually shown there —
            # fallen-back seats keep the planetary text.
            article_set, article_body = (
                self._dial.skin.weekday_set.body_articles[body]
            )
        if same_unit:
            display_name = self._dial.skin.weekday_set.body_names[body]
            image = self._dial.skin.weekday_set.bodies.get(body)
            metal = self._dial.skin.weekday_set.metal
        elif theme == "planets":
            display_name = defaults.DEFAULT_SKIN.weekday_set.body_names[body]
            image = pantheon.weekday_theme_body_art(
                "planets", body, on_date=on_date,
            )
            metal = None
        else:
            # A SEATED slot's SECOND weekday: resolve the art exactly
            # like its layer — the slot's OWN metal, colored/ included
            # (owner bug 2026-07-13: the legend always showed bronze),
            # and the slot's OWN roster (owner 2026-07-15): a pantheon
            # seat speaks the figure actually shown there, a seat
            # whose plate has not landed keeps the planetary bundle
            # whole — the same safety law as the classic unit.
            metal = (
                slot_metal
                if theme in constants.METAL_THEMES
                and slot_metal in defaults.METAL_SWAP_TARGETS
                else None
            )
            seat = (
                pantheon.pantheon_seat(theme, body)
                if roster == "pantheon" else None
            )
            if seat is not None:
                image, display_name, (article_set, article_body) = seat
                if on_date is not None:
                    image = pantheon.rotating_art_file(image, on_date) or image
            else:
                display_name = pantheon.WEEKDAY_THEME_NAMES[theme][body]
                # THE ONE weekday-body resolver (Rule #5 — shared with
                # `app.controller` and `render.weekday_body._draw_weekday_slot`;
                # `on_date` wires THE UNIVERSAL ROTATION CONVENTION so
                # the legend never shows a different day's pick than the
                # slot it describes).
                image = pantheon.weekday_theme_body_art(
                    theme, body, on_date=on_date,
                    colored=(
                        slot_metal == "colored"
                        and theme in constants.METAL_THEMES
                    ),
                )
        if same_unit and image is not None and on_date is not None:
            # `spec.bodies` is BAKED at settings-apply time (never per
            # day) — re-resolve the live rotation on top of it, exactly
            # like `render.weekday_body.draw_weekday_body`'s own override.
            image = pantheon.rotating_art_file(image, on_date) or image
        image = metal_variant_file(image, metal)
        if body == "sun":
            # The dual center's TWO plates in one legend (owner
            # 2026-07-13: "u prism i trinity treba legend sa 2 slike").
            if same_unit:
                dual_image = self._dial.skin.weekday_set.dual_asset
            else:
                # ONE DOOR for "which Sunday does this roster wear"
                # (`pantheon.weekday_dual_rel`, extracted 2026-08-15):
                # the pantheon dual wins only when its plate is on
                # disk, otherwise the WHOLE planetary pair stays (the
                # classic unit's Sunday law). The Artwork previews ask
                # the same door — they used to ask nothing at all and
                # drew the planetary dual for both rosters.
                dual_rel = (
                    pantheon.weekday_dual_rel(theme, roster)
                    or pantheon.WEEKDAY_DUAL_FILES[theme]
                )
                dual_image = pantheon.weekday_art(f"{dual_rel}.png")
            image = (image, metal_variant_file(dual_image, metal))
        node = self._dial.symbolism.article(article_set, article_body)
        text = node["base"]
        variant = node["variants"].get(self._combo_key())
        if variant:
            text += "\n\n" + variant
        title = (
            f"<span style='font-size: {encyclopedia_ui.ARTICLE_TITLE_PX}px'>"
            f"<b>{html.escape(self._tr(display_name))}</b>"
            f"</span>"
        )
        if active:
            date = self._dial.day.local_date
            title += (
                f"<br/>{html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES[body]))}, "
                f"{self._ord(date.day)} {html.escape(self._month(date))} "
                f"{self._year(date)}"
            )
        else:
            # THE WEEKDAY-TITLE LAW (owner, repeated many times —
            # CUBE.md §Display and Legend Laws): every weekday-bound
            # badge names ITS day beside the title; the active body's
            # full date line above already carries it.
            title += (
                f"<br/>"
                f"{html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES[body]))}"
            )
        return article_html(image, title, text, tr=self._tr)

    def _archetype_arm_tooltip(self, index: int) -> str:
        """One arm figure's archetype legend (owner 2026-07-16): the
        TWO-ROW article per the two-row canon — person+calling, member+
        hearth-role, temperament+age, person+quality, pillar+shadow,
        estate+object. EXCEPT the two THREE-SIDE layouts (owner
        2026-07-17): the Ages (compass light) show the age's text and BOTH
        life registers (the Tree + the Menagerie); the Tetramorph (seasons
        light) show the creature + the evangelist + the element."""
        key = archetype_key(self._dial.skin)
        if key == "compass_secondary":
            return self._archetype_three_side(index)
        if key == "quaternity_secondary":
            return self._tetramorph_three_side(index)
        fig = archetypes.figures(key)[index]
        return self._archetype_two_rows(
            key, fig["name"], fig["row2"], fig["entity"], fig["file"]
        )

    def _archetype_three_side(self, index: int) -> str:
        """The AGES three-side hover (owner 2026-07-17, "oba odmah"): a
        THREE-COLUMN article whose total width stays the TWO-SIDE width —
        the age's text, the Tree register (image + being), the Menagerie
        register (image + being). Each register image resolves from its
        own life/<register> path and shows only when REAL art has landed
        (placeholders fall back to the being name, gracefully as before)."""
        key = "compass_secondary"
        registers = archetypes.ARCHETYPES[key]["registers"]
        tree_fig = registers["tree"][index]
        animals_fig = registers["animals"][index]
        set_name = archetypes.ARCHETYPES[key]["articles"]
        node = self._dial.symbolism.archetype_article(set_name, tree_fig["entity"])
        rows = (node or {}).get("rows") or ()
        # Column 1 — the age name and its text (or the pending line).
        text_col = hover_title(html.escape(self._tr(tree_fig["name"])))
        if rows:
            text_col += article_paragraphs(teaser(rows[0]), tr=self._tr)
        else:
            text_col += centered_html(
                "",
                html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE)),
            )

        def register_column(caption: str, fig: dict) -> str:
            image = ""
            if archetype_art_ready(fig["file"]):
                small = scaled_variant_file(
                    fig["file"], 2 * encyclopedia_ui.ARTICLE_THREE_IMAGE_PX
                )
                image = (
                    f"<div align='center'><img src='{small.as_uri()}' "
                    f"width='{encyclopedia_ui.ARTICLE_THREE_IMAGE_PX}'/></div>"
                )
            return (
                hover_title(html.escape(self._tr(caption)))
                + image
                + centered_html(f"<b>{html.escape(self._tr(fig['row2']))}</b>")
            )

        width = encyclopedia_ui.ARTICLE_THREE_COLUMN_WIDTH_PX
        return (
            "<table cellspacing='10'><tr>"
            f"<td width='{width}'>{text_col}</td>"
            f"<td width='{width}'>{register_column('The Tree', tree_fig)}</td>"
            f"<td width='{width}'>"
            f"{register_column('The Menagerie', animals_fig)}</td>"
            "</tr></table>"
        )

    def _tetramorph_three_side(self, index: int) -> str:
        """The TETRAMORPH three-side hover (owner 2026-07-17, ROADMAP 15e:
        "sva 3 ako se podudaraju"): a THREE-COLUMN article — the same
        machinery and total width as the Ages three-side — carrying the
        CREATURE (its glass, name and text), the EVANGELIST it became
        (Mark/Luke/John/Matthew, with his rondel and article), and the
        ELEMENT its fixed-cross season arm holds (Fire/Earth/Water/Air,
        the name in its own wheel hue, with its humoral article). The
        creature node carries the three columns' prose as its rows —
        rows[0] the creature, rows[1] the evangelist, rows[2] the element
        (Session 6 + the Tetramorph completion round); each column
        degrades to its bare title/name when its row (or the evangelist
        rondel) has not landed — never a KeyError."""
        key = "quaternity_secondary"
        fig = archetypes.figures(key)[index]
        set_name = archetypes.ARCHETYPES[key]["articles"]
        node = self._dial.symbolism.archetype_article(set_name, fig["entity"])
        rows = (node or {}).get("rows") or ()
        # Column 1 — the creature (glass + name + text).
        creature_col = hover_title(html.escape(self._tr(fig["name"])))
        if archetype_art_ready(fig["file"]):
            small = scaled_variant_file(
                fig["file"], 2 * encyclopedia_ui.ARTICLE_THREE_IMAGE_PX
            )
            creature_col += (
                f"<div align='center'><img src='{small.as_uri()}' "
                f"width='{encyclopedia_ui.ARTICLE_THREE_IMAGE_PX}'/></div>"
            )
        if rows:
            creature_col += article_paragraphs(teaser(rows[0]), tr=self._tr)
        else:
            creature_col += centered_html(
                "", html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE))
            )
        # Column 2 — the Evangelist: his rondel (real art only), his name
        # (the figure's row-2), then his article (rows[1] when written).
        evangelist_col = hover_title(html.escape(self._tr("The Evangelist")))
        ev_file = archetypes.tetramorph_evangelist_file(index)
        if archetype_art_ready(ev_file):
            small = scaled_variant_file(
                ev_file, 2 * encyclopedia_ui.ARTICLE_THREE_IMAGE_PX
            )
            evangelist_col += (
                f"<div align='center'><img src='{small.as_uri()}' "
                f"width='{encyclopedia_ui.ARTICLE_THREE_IMAGE_PX}'/></div>"
            )
        evangelist_col += centered_html(
            f"<b>{html.escape(self._tr(fig['row2']))}</b>"
        )
        if len(rows) > 1:
            evangelist_col += article_paragraphs(teaser(rows[1]), tr=self._tr)
        # Column 3 — the Element: the name in its active wheel hue, then
        # its humoral article (rows[2] when written).
        hue = palette_for(self._dial.skin)[index]
        element_col = hover_title(
            html.escape(self._tr("The Element"))
        ) + centered_html(
            f"<b style='color: {hue}'>"
            f"{html.escape(self._tr(archetypes.tetramorph_element(index)))}</b>"
        )
        if len(rows) > 2:
            element_col += article_paragraphs(teaser(rows[2]), tr=self._tr)
        width = encyclopedia_ui.ARTICLE_THREE_COLUMN_WIDTH_PX
        return (
            "<table cellspacing='10'><tr>"
            f"<td width='{width}'>{creature_col}</td>"
            f"<td width='{width}'>{evangelist_col}</td>"
            f"<td width='{width}'>{element_col}</td>"
            "</tr></table>"
        )

    def _archetype_center_tooltip(self) -> str:
        """The archetype center's legend — the Eye / the Hearth / the
        Seal / the Union / the Throne speak their CANON paragraph."""
        key = archetype_key(self._dial.skin)
        center = archetypes.center(key)
        return self._archetype_two_rows(
            key, center["name"], None, center["entity"], center["file"]
        )

    def _archetype_two_rows(
        self, key: str, name: str, row2: str | None, entity: str, art,
    ) -> str:
        """One archetype legend: the stained glass on top (real art
        only — a 1×1 placeholder never stretches into the popup), the
        figure's name as the title, then the TWO ROWS from the
        archetype's article set. Until Session 6 writes the set the
        hover shows the name, the second-row name and the one-line
        pending stand-in — the documented graceful path, never a
        KeyError."""
        set_name = archetypes.ARCHETYPES[key]["articles"]
        node = self._dial.symbolism.archetype_article(set_name, entity)
        badge = hover_badge(art) if archetype_art_ready(art) else ""
        title = hover_title(html.escape(self._tr(name)))
        rows = (node or {}).get("rows") or ()
        if rows:
            parts = [
                badge, title,
                article_body_html(teaser(rows[0]), tr=self._tr),
            ]
            if row2 is not None and len(rows) > 1:
                # The second row, split off by a rule — the same shape
                # as the cross arms' two data sets (owner pattern).
                parts += [
                    "<hr/>",
                    hover_title(html.escape(self._tr(row2))),
                    article_body_html(teaser(rows[1]), tr=self._tr),
                ]
            return "".join(parts)
        subtitle = (
            centered_html(f"<b>{html.escape(self._tr(row2))}</b>")
            if row2 is not None
            else ""
        )
        return badge + title + subtitle + centered_html(
            "",
            html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE)),
        )

    def _sun_face_tooltip(self, face: str, active: bool) -> str:
        """ONE face of the dual Sunday (owner 2026-07-13): on the
        Compass and the Seasons each face is its own person — its own
        name, its own plate, its own text (articles.<set>.sun.faces;
        the base article stands in until a theme's split lands). The
        Ruler face keeps the pointer/palette variant paragraph."""
        theme = self._dial.skin.weekday_theme
        ruler = face == "ruler"
        dual_names = (
            self._dial.skin.weekday_set.dual_names
            or pantheon.WEEKDAY_DUAL_NAMES[theme]
        )
        display_name = dual_names[0 if ruler else 1]
        image = metal_variant_file(
            self._dial.skin.weekday_set.bodies.get("sun")
            if ruler
            else self._dial.skin.weekday_set.dual_asset,
            self._dial.skin.weekday_set.metal,
        )
        node = self._dial.symbolism.article(
            self._dial.skin.weekday_set.article_set
            or constants.WEEKDAY_THEME_ARTICLES[theme],
            "sun",
        )
        text = node.get("faces", {}).get(face) or node["base"]
        if ruler:
            variant = node["variants"].get(self._combo_key())
            if variant:
                text += "\n\n" + variant
        title = (
            f"<span style='font-size: {encyclopedia_ui.ARTICLE_TITLE_PX}px'>"
            f"<b>{html.escape(self._tr(display_name))}</b>"
            f"</span>"
        )
        if active:
            date = self._dial.day.local_date
            title += (
                f"<br/>{html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES['sun']))}, "
                f"{self._ord(date.day)} {html.escape(self._month(date))} "
                f"{self._year(date)}"
            )
        else:
            # THE WEEKDAY-TITLE LAW: the Sunday faces are Sunday-bound.
            title += (
                f"<br/>"
                f"{html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES['sun']))}"
            )
        return article_html(image, title, text, tr=self._tr)

    def _dual_face_columns(self, theme: str, faces: tuple[str, str]) -> str:
        """The CENTER seat's TWO-FACE hover CARD (owner verdict B, round
        R3b items 2/4 — "po principu ZODIAC na PRISM diamond hover"):
        two texts side by side, a divider between, each under its own
        emblem — the SAME two-column table `_arm_tooltip`'s hexa
        zodiac-diamond hover builds below (Rule #5), fed by `faces`, a
        pair picked from up to three: "ruler" (GOOD), "servant" (EVIL),
        "ninth" (THE UNFOUND)."""
        spec = self._dial.skin.weekday_set
        dual_names = spec.dual_names or pantheon.WEEKDAY_DUAL_NAMES[theme]
        article_set = spec.article_set or constants.WEEKDAY_THEME_ARTICLES[theme]
        columns = []
        sunday = html.escape(self._tr(week_registry.WEEKDAY_FULL_NAMES["sun"]))
        for face in faces:
            if face == "ninth":
                name, asset = theme_ninth(
                    theme, self._center_ninth_alt(), on_date=self._dial.day.local_date
                )
                text = self._dial.encyclopedia.entry("ninths", name)["base"]
                # The Ninth stands OUTSIDE the circle — no weekday line.
                day_line = ""
            else:
                ruler = face == "ruler"
                name = dual_names[0 if ruler else 1]
                raw = spec.bodies.get("sun") if ruler else spec.dual_asset
                if raw is not None:
                    raw = pantheon.rotating_art_file(raw, self._dial.day.local_date) or raw
                asset = metal_variant_file(raw, spec.metal)
                node = self._dial.symbolism.article(article_set, "sun")
                text = node.get("faces", {}).get(face) or node["base"]
                if ruler:
                    variant = node["variants"].get(self._combo_key())
                    if variant:
                        text += "\n\n" + variant
                # THE WEEKDAY-TITLE LAW: both throne faces are Sunday's.
                day_line = f"<br/>{sunday}"
            columns.append(
                hover_badge(asset)
                + hover_title(
                    f"<b>{html.escape(self._tr(name))}</b>{day_line}"
                )
                + article_paragraphs(teaser(text), tr=self._tr)
            )
        return (
            "<table cellspacing='12'><tr>"
            f"<td width='{encyclopedia_ui.ARTICLE_COLUMN_WIDTH_PX}'>{columns[0]}</td>"
            f"<td width='{encyclopedia_ui.ARTICLE_COLUMN_WIDTH_PX}'>{columns[1]}</td>"
            "</tr></table>"
        )

    def _active_thirteenth(self) -> str | None:
        """THE BLUE MOON LAW's resolved 13th for today+mode (owner
        overrule, CORRECTED 2026-07-2X) — calls the SAME pure resolver
        the paint pass calls (`render.ninths.active_thirteenth`, fed
        the pre-computed `DayContext.thirteenth_candidates` fact set);
        None before the first day build (mirrors `_center_ninth_alt`'s own
        graceful guard)."""
        if self._dial.day is None:
            return None
        daylight = self._dial.tick.is_daylight if self._dial.tick is not None else True
        return active_thirteenth(self._dial.skin, self._dial.day, daylight)

    def _thirteenth_tooltip(self, key: str) -> str:
        """THE BLUE MOON LAW's 13th (owner overrule, CORRECTED
        2026-07-2X): its own article and badge lead, drawn at the
        Calendar pointer's OWN dial center (`render.layers.
        active_thirteenth` gates this to `skin.pointer == "calendar"`
        alone, so no OTHER theme's center face is ever displaced; the
        old "steps aside" closing line is retired with R12's global
        law).

        THE AXLE LAW (CANON §The Axle) splits the closing line in two:
        a calendar-driven 13th is a blue-moon guest, empty every other
        day; an ALWAYS-CENTER (`constants.AXLE_ALWAYS_CENTERS`) is the
        axle the twelve turn on, present on literally every date
        instead. An always-center whose Encyclopedia article is not written yet
        (`family is None` in `constants.THIRTEENTHS` — the graceful-
        absent contract, same as a missing art plate) skips the
        `entry()` lookup entirely rather than crash on an unwritten
        family/article pair, and the closing line itself becomes the
        teaser (`teaser` reads the text BEFORE the first blank line —
        appending the closing note after an empty base would tease a
        bare " …", not this line)."""
        name, asset = thirteenth_plate(key)
        _display, family, article_name = constants.THIRTEENTHS[key]
        axle = key in constants.AXLE_ALWAYS_CENTERS
        closing = (
            "The one who does not turn with the twelve: always present, "
            "the Calendar pointer's own dial center." if axle else
            "A blue-moon guest: the Calendar pointer's own dial center, "
            "empty every other day."
        )
        if family is not None:
            marker = "[[The Axle]]" if axle else "[[The Thirteenth]]"
            text = self._dial.encyclopedia.entry(family, article_name)["base"]
            text += f"\n\n{marker} {closing}"
        else:
            text = closing
        title = (
            f"<span style='font-size: {encyclopedia_ui.ARTICLE_TITLE_PX}px'>"
            f"<b>{html.escape(self._tr(name))}</b></span>"
        )
        return article_html(asset, title, text, tr=self._tr)

    def _dual_seat_taken(self) -> str | None:
        """Which TWO-BADGE seat the Ninth borrows RIGHT NOW ("ruler" /
        "servant" / None — owner seal 2026-07-29): mirrors
        `WeekdayLayer`'s own gate exactly (Sunday, `sunday_dual_face`,
        a Ninth that resolves, `dual_seat_ninth`'s solar windows) so
        the hover card and the dial can never disagree."""
        if self._dial.day is None or self._dial.tick is None:
            return None
        today = week_registry.WEEKDAY_BODIES[self._dial.day.weekday_index]
        if today != "sun" or not sunday_dual_face(self._dial.skin):
            return None
        if theme_ninth(
            self._dial.skin.weekday_theme, self._center_ninth_alt(),
            on_date=self._dial.day.local_date,
        ) is None:
            return None
        return dual_seat_ninth(self._dial.day, self._dial.tick)

    def _center_ninth_alt(self) -> bool:
        """THE DOUBLE NINTH's alt-face flag for the hover (owner
        Double-Ninth verdicts, 2026-07-29 — was `_center_pangea`,
        continents-only, before the law generalized): dispatches by the
        theme's OWN `constants.NINTH_MECHANISMS` entry, fed from this
        compositor's own day and last tick so the card and the dial
        never disagree.

        - "easter_egg" reads the SAME `core.continents` sky law the
          paint pass reads.
        - "daynight" reads the SAME `TickState.is_daylight` `center_face`
          reads — night is the alt face.
        - every other mechanism (or none) answers False."""
        if self._dial.day is None:
            return False
        mechanism = constants.NINTH_MECHANISMS.get(self._dial.skin.weekday_theme)
        if mechanism == "easter_egg":
            return continents.ninth_is_pangea_from_events(
                self._dial.day.local_date,
                self._dial.day.season_events,
                self._dial.day.moon_events,
                (
                    self._dial.tick.eclipse_event is not None
                    if self._dial.tick is not None
                    else False
                ),
            )
        if mechanism == "daynight":
            return (
                self._dial.tick is not None and not self._dial.tick.is_daylight
            )
        return False

    def _center_dual_tooltip(self, active: bool) -> str:
        """The CENTER seat's Sunday duality hover (owner INSTRUCTION #5,
        re-shaped by the 2026-07-29 seal): a ghost read on a non-Sunday
        day stays the single GOOD/Ruler article; on the real Sunday, a
        theme with only TWO faces ALWAYS speaks BOTH side by side
        (owner: "HOVER su uvek OBA jedan pored drugog"), a theme with a
        NINTH speaks the showing face alone outside the solar windows
        (GOOD in daylight, EVIL at night — `center_face`) and the
        matching TWO-COLUMN pair inside them (GOOD+NINTH near solar
        noon, EVIL+NINTH near solar midnight — `ninth_window_anchor`)."""
        if not active:
            return self._sun_face_tooltip("ruler", active=False)
        theme = self._dial.skin.weekday_theme
        ninth = theme_ninth(
            theme, self._center_ninth_alt(), on_date=self._dial.day.local_date
        )
        if ninth is None:
            return self._dual_face_columns(theme, ("ruler", "servant"))
        face = center_face(self._dial.day, self._dial.tick, has_ninth=True)
        if face == "ninth":
            beside = (
                "ruler"
                if ninth_window_anchor(self._dial.day, self._dial.tick) == "noon"
                else "servant"
            )
            return self._dual_face_columns(theme, (beside, "ninth"))
        return self._sun_face_tooltip(face, active=True)

    def _arm_tooltip(self, point: QPointF, radius: float, rotation: float) -> str | None:
        """Hover over a star arm (owner spec): hexa arms name their TWO
        zodiac signs; cross/octa cardinal arms give the exact instant of
        the solstice/equinox they point at; octa diagonal arms describe
        their season (dates, duration, the middle date the arrow points
        at). With solar rotation on, a trailing * flags the slight
        offset from the year-wheel positions. (In archetype mode the ARM
        figures answer through `_element_at`/`tooltip_at`, not here.)"""
        # Only INSIDE the drawn diamond (owner bug report): between the
        # arms the wheel itself answers — the Aura's day or the Umbra's
        # night. The ONE arm-diamond geometry lives in `_arm_angle_at`.
        arm_angle = self._dial.arm_angle_at(point, radius, rotation)
        if arm_angle is None:
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        star = "*" if self._dial.skin.solar_rotation else ""

        if self._dial.skin.pointer == "hexa":
            # The 60-deg arc [arm-30, arm+30] spans exactly two signs.
            # Hover rework (owner 2026-07-13 round two): the two signs
            # stand LEFT/RIGHT as two columns — each with its bold
            # title (name + dates, NO glyph), its COLORED logo, then
            # ITS article (base + the active palette's paragraph).
            from render.subdial import octa_slot_art

            style = self._dial.skin.palette_style
            columns = []
            south = self._dial.day.southern_hemisphere
            for offset in (-30.0, 0.0):      # the two signs' START angles
                start_angle = (arm_angle + offset) % 360.0
                if south:
                    # The mirrored year wheel (owner spec 2026-07-12):
                    # the diamond the Earth passes must name the signs
                    # it actually passes there — the opposite half.
                    start_angle = (start_angle + 180.0) % 360.0
                name, _symbol = constants.ZODIAC_SIGNS[int(start_angle) // 30]
                start, end = zodiac_span(self._dial.day.year_anchors, start_angle)
                start = start.astimezone(self._dial.day.tzinfo)
                last = end.astimezone(self._dial.day.tzinfo) - timedelta(days=1)
                header = (
                    f"{html.escape(self._tr(name))} "
                    f"({self._ord(start.day)} {html.escape(self._month(start))} - "
                    f"{self._ord(last.day)} {html.escape(self._month(last))})"
                )
                if offset == -30.0 and star:
                    header += html.escape(star)
                colored = octa_slot_art(
                    complications.ZODIAC_STYLE_ART_DIRS["colored"], name
                )
                plate = ""
                if colored is not None and colored.exists():
                    small = scaled_variant_file(
                        colored, 2 * encyclopedia_ui.ARTICLE_IMAGE_WIDTH_PX
                    )
                    plate = (
                        f"<div align='center'><img src='{small.as_uri()}' "
                        f"width='{encyclopedia_ui.ARTICLE_IMAGE_WIDTH_PX}'/></div>"
                    )
                article = self._dial.symbolism.zodiac_article(name)
                text = article["base"]
                # South of the equator the sign wears the opposite
                # arm's hue — its own SOUTH variant paragraph (falls
                # back to the northern one until translated/edited).
                variant = (
                    article["variants"].get(f"{style}_south")
                    if south else None
                ) or article["variants"].get(style)
                if variant:
                    text += "\n\n" + variant
                columns.append(
                    hover_title(header)
                    + plate
                    + article_paragraphs(teaser(text), tr=self._tr)
                )
            # ONE flat table, both columns width-declared (nested
            # tables measured wrong — the popup honors these cells).
            return (
                "<table cellspacing='12'><tr>"
                f"<td width='{encyclopedia_ui.ARTICLE_COLUMN_WIDTH_PX}'>"
                f"{columns[0]}</td>"
                f"<td width='{encyclopedia_ui.ARTICLE_COLUMN_WIDTH_PX}'>"
                f"{columns[1]}</td>"
                "</tr></table>"
            )
        if self._dial.skin.pointer == "trio":
            # Trio arm (owner spec): its theological theme, the day
            # third it CENTERS (the arm tip is the middle of its hue),
            # the weekday pair it carries — and the virtue's ARTICLE.
            start_hour = int((((arm_angle + 180.0) % 360.0) // 15 - 4) % 24)
            end_hour = int((start_hour + 8) % 24)
            bodies = next(
                occupants
                for angle, occupants in weekday_slots(self._dial.skin)
                if angle == arm_angle
            )
            days = " · ".join(
                self._tr(week_registry.WEEKDAY_FULL_NAMES[body]) for body in bodies
            )
            if self._dial.skin.palette_style == "tertiary":
                # The GENESIS wheel (CUBE.md §Double Trinity): the arm
                # speaks its creation office — person, office, hours,
                # days. The office articles are Session 21's writers'
                # work; until they land the hover carries the canon
                # pending line, never a KeyError (the same graceful
                # path every unwritten archetype article walks).
                person, office = archetypes.GENESIS_ARM_OFFICES[arm_angle]
                header = centered_html(
                    f"<b>{html.escape(self._tr(office))}</b>"
                    f"{html.escape(star)}",
                    html.escape(self._tr(person)),
                    f"{start_hour:02d}:00 - {end_hour:02d}:00",
                    html.escape(days),
                )
                return header + "<br/>" + article_body_html(
                    archetypes.ARCHETYPE_PENDING_LINE, tr=self._tr
                )
            theme = archetypes.TRIO_ARM_THEMES[arm_angle]
            header = centered_html(
                f"<b>{html.escape(self._tr(theme))}</b>{html.escape(star)}",
                f"{start_hour:02d}:00 - {end_hour:02d}:00",
                html.escape(days),
            )
            article = self._dial.symbolism.trio_article(theme)
            return (
                hover_badge(defaults.TRINITY_ART_DIR / f"{theme}.png")
                + header + "<br/>"
                + article_body_html(teaser(article["base"]), tr=self._tr)
            )
        if arm_angle % 90.0 == 0.0:
            # Cardinal arms (cross and octa) point at the season events:
            # the exact instant, plus the DAY LENGTH on that date (owner
            # rework). The cross additionally describes its
            # METEOROLOGICAL season — bounds halfway between the anchors,
            # so the season centers on its solstice/equinox.
            anchor_angle = {0.0: 360.0, 90.0: 450.0, 180.0: 540.0, 270.0: 270.0}[
                arm_angle
            ]
            if self._dial.day.southern_hemisphere:
                # The year wheel runs MIRRORED south of the equator
                # (the Earth marker already does) — the arms must point
                # at the mirrored anchors too (owner bug 2026-07-12:
                # Sydney's TOP arm must read the DECEMBER solstice).
                anchor_angle = _SOUTH_ANCHOR_FLIP[anchor_angle]
            index = self._dial.day.year_anchors.angles.index(anchor_angle)
            name = self._dial.day.season_events[index][1]      # zone-correct name
            instant = self._anchor_instant(anchor_angle).astimezone(self._dial.day.tzinfo)
            hours, minutes = self._dial.day.anchor_day_lengths[index].split(":")
            # First block (owner format 2026-07-13: image → title →
            # space → data; both equinoxes share the ONE balance
            # emblem): the turning point with its labeled day length.
            badge = (
                "Equinox" if "Equinox" in name else name.replace(" ", "_")
            )
            head = hover_badge(
                defaults.SEASON_ART_DIR / "turning_point" / f"{badge}.png"
            ) + hover_title(
                f"{html.escape(self._tr(name))}{html.escape(star)}"
            ) + centered_html(
                "",
                f"{self._ord(instant.day)} {html.escape(self._month(instant))} "
                f"{self._year(instant)} - {instant:%H:%M}",
                f"{self._label('Daylight')} {int(hours)}h {int(minutes)}min",
            )
            if self._dial.skin.pointer != "cross":
                return head
            # Second block, split off by a RULE (owner 2026-07-13:
            # two data sets, a line between them): the meteorological
            # season — or the tropics' wet/dry half-year — wearing its
            # own badge.
            if self._dial.day.zone == "tropics":
                # Tropics (owner decision): the cross arms describe
                # the equinox-bounded WET/DRY halves — the solstice
                # arms CENTER theirs, the equinox arms START theirs.
                span_start = 270.0 if anchor_angle in (270.0, 360.0) else 450.0
                is_wet, block = self._wet_dry_block(span_start)
                return head + "<hr/>" + hover_badge(
                    defaults.SEASON_ART_DIR
                    / f"{'Wet' if is_wet else 'Dry'}_Season.png"
                ) + block
            season = self._season_name_for(anchor_angle)
            met_start, met_end = meteorological_span(
                self._dial.day.year_anchors, anchor_angle
            )
            met_start = met_start.astimezone(self._dial.day.tzinfo)
            met_end = met_end.astimezone(self._dial.day.tzinfo)
            met_days = (met_end - met_start).total_seconds() / 86400
            return head + "<hr/>" + hover_badge(
                defaults.SEASON_ART_DIR / "meteorological" / f"{season}.png"
            ) + hover_title(
                html.escape(
                    self._tr("Meteorological {season}").format(
                        season=self._tr(season)
                    )
                )
            ) + centered_html(
                "",
                f"<b>{self._tr('From')}</b> {self._ord(met_start.day)} "
                f"{self._month(met_start)} {self._year(met_start)} - "
                f"{met_start:%H:%M}",
                f"<b>{self._tr('To')}</b> {self._ord(met_end.day)} "
                f"{self._month(met_end)} {self._year(met_end)} - "
                f"{met_end:%H:%M}",
                f"{self._label('Duration')} {met_days:.1f} "
                f"{html.escape(self._tr('Days'))}",
            )
        # Octa diagonal arms point at the QUARTER centers: the four
        # temperate seasons — or, in the tropics, the halves of the
        # wet/dry seasons (owner spec: TL is the first part of the
        # season the top arms span, TR the second...).
        start_angle = {315.0: 270.0, 45.0: 360.0, 135.0: 450.0, 225.0: 540.0}[
            arm_angle
        ]
        if self._dial.day.southern_hemisphere:
            # Mirrored wheel (see the cardinal arms): the quarters the
            # diagonal arms span flip with it.
            start_angle = _SOUTH_ANCHOR_FLIP[start_angle]
        start = self._anchor_instant(start_angle).astimezone(self._dial.day.tzinfo)
        end = self._anchor_instant(start_angle + 90.0).astimezone(self._dial.day.tzinfo)
        middle = start + (end - start) / 2
        days = (end - start).total_seconds() / 86400
        if self._dial.day.zone == "tropics":
            starts_in_march = start_angle in (270.0, 360.0)
            is_wet = starts_in_march != self._dial.day.southern_hemisphere
            if self._dial.overlay:
                half = self._tr("(1st half)" if start_angle in (270.0, 450.0)
                                else "(2nd half)")
            else:
                half = (
                    "(1<sup>st</sup> half)"
                    if start_angle in (270.0, 450.0)
                    else "(2<sup>nd</sup> half)"
                )
            season_line = (
                f"<b>{html.escape(self._tr('Wet season' if is_wet else 'Dry season'))}</b> "
                f"{half}{html.escape(star)}"
            )
            _, whole = self._wet_dry_block(270.0 if starts_in_march else 450.0)
            return hover_badge(
                defaults.SEASON_ART_DIR
                / f"{'Wet' if is_wet else 'Dry'}_Season.png"
            ) + centered_html(
                season_line,
                self._span_line(start, end, days),
                f"{self._tr('Heart:')} {self._ord(middle.day)} "
                f"{self._month(middle)}",
            ) + "<hr/>" + whole
        season = self._season_name_for(start_angle)
        return hover_badge(
            defaults.SEASON_ART_DIR / f"{season}.png"
        ) + centered_html(
            f"<b>{html.escape(self._tr(season))}</b>{html.escape(star)}",
            self._span_line(start, end, days),
            f"{self._tr('Heart:')} {self._ord(middle.day)} {self._month(middle)}",
        )

    def _span_line(self, start, end, days: float) -> str:
        """"21st December - 20th March (89.3 Days)" in the active
        language."""
        return (
            f"{self._ord(start.day)} {self._month(start)} - "
            f"{self._ord(end.day)} {self._month(end)} "
            f"({days:.1f} {self._tr('Days')})"
        )

    def _wet_dry_block(self, span_start_angle: float) -> tuple[bool, str]:
        """The whole wet/dry season block (tropics), in the owner's
        2026-07-13 season format — title → space → bold From/To bounds
        → labeled Duration; returns (is_wet, html) so the caller can
        pick the badge."""
        start = self._anchor_instant(span_start_angle).astimezone(self._dial.day.tzinfo)
        end = self._anchor_instant(span_start_angle + 180.0).astimezone(
            self._dial.day.tzinfo
        )
        starts_in_march = span_start_angle % 360.0 == 270.0
        is_wet = starts_in_march != self._dial.day.southern_hemisphere
        days = (end - start).total_seconds() / 86400
        return is_wet, hover_title(
            html.escape(self._tr("Wet season" if is_wet else "Dry season"))
        ) + centered_html(
            "",
            f"<b>{self._tr('From')}</b> {self._ord(start.day)} "
            f"{self._month(start)} {self._year(start)}",
            f"<b>{self._tr('To')}</b> {self._ord(end.day)} "
            f"{self._month(end)} {self._year(end)}",
            f"{self._label('Duration')} {days:.1f} "
            f"{html.escape(self._tr('Days'))}",
        )

    def _season_name_for(self, start_anchor_angle: float) -> str:
        """The temperate season STARTING at an unwrapped anchor angle —
        read from the zone-correct event names (the south already flips
        them): "Autumn Equinox" starts Autumn."""
        index = self._dial.day.year_anchors.angles.index(start_anchor_angle)
        return self._dial.day.season_events[index][1].split()[0]

    def _anchor_instant(self, unwrapped_angle: float):
        """Season-anchor instant at an unwrapped year-wheel angle."""
        anchors = self._dial.day.year_anchors
        return anchors.instants[anchors.angles.index(unwrapped_angle)]

    def _chinese_text(self, style: str | None = None) -> str:
        """Chinese slot hover (owner rework): the year name and span,
        then the animal's ARTICLE with the owner's medallion on top —
        in the ACTIVE style's look (owner bug 2026-07-13: the legend
        always showed the bronze plate): colored takes its own art,
        gold/silver ride the selective swap."""
        from render.subdial import octa_slot_art

        day = self._dial.day
        element, animal = day.chinese_name.split()
        header = centered(
            self._tr("{element} {animal}").format(
                element=self._tr(element), animal=self._tr(animal)
            ),
            f"{day.chinese_start.day} {self._month_short(day.chinese_start)} "
            f"{self._year(day.chinese_start)} – "
            f"{day.chinese_end.day} {self._month_short(day.chinese_end)} "
            f"{self._year(day.chinese_end)}",
        )
        # The animal's article, then the ELEMENT paragraph qualifying
        # THIS return of it (owner spec — each return wears a new one).
        text = (
            self._dial.symbolism.chinese_article(animal)["base"]
            + "\n\n"
            + self._dial.symbolism.chinese_element(element)["base"]
        )
        folder = complications.CHINESE_STYLE_ART_DIRS.get(style, "zodiac/chinese/primary/bronze")
        image = metal_variant_file(
            octa_slot_art(folder, animal),
            style if style in defaults.METAL_SWAP_TARGETS else None,
        )
        return header + "<br/>" + article_html(
            image, None, text, tr=self._tr,
        )

    def _zodiac_line(self) -> str:
        """"♋ Cancer — 21 Jun – 22 Jul" (sign with its date span)."""
        day = self._dial.day
        last = day.zodiac_end - timedelta(days=1)    # end is the next sign's first day
        return (
            f"{day.zodiac_symbol} {self._tr(day.zodiac_name)} — "
            f"{day.zodiac_start.day} {self._month_short(day.zodiac_start)} – "
            f"{last.day} {self._month_short(last)}"
        )

    def _zodiac_image_trio(self, style: str | None, sign: str) -> str:
        """The Astrology hover's image row (owner 2026-07-13): the
        ACTIVE style's art LARGE in the middle — filling the image
        band — and the two remaining styles small at its sides (text
        mode leads with the colored logo)."""
        from render.subdial import octa_slot_art

        dirs = complications.ZODIAC_STYLE_ART_DIRS
        main_style = style if style in dirs else "colored"
        sides = {
            "logo": ("sign", "constellation"),
            "colored": ("sign", "constellation"),
            "sign": ("logo", "constellation"),
            "constellation": ("sign", "logo"),
        }[main_style]
        side_px = round(
            encyclopedia_ui.ASTRO_MAIN_IMAGE_PX * encyclopedia_ui.ASTRO_SIDE_IMAGE_FRACTION
        )

        def img(folder: str, px: int) -> str:
            path = octa_slot_art(folder, sign)
            if path is None or not path.exists():
                return ""
            small = scaled_variant_file(path, 2 * px)
            return f"<img src='{small.as_uri()}' width='{px}' align='middle'/>"

        return (
            "<div align='center'>"
            + img(dirs[sides[0]], side_px)
            + img(dirs[main_style], encyclopedia_ui.ASTRO_MAIN_IMAGE_PX)
            + img(dirs[sides[1]], side_px)
            + "</div>"
        )

    def _zodiac_text(self, style: str | None = None) -> str:
        """Zodiac slot hover (owner rework, formatting 2026-07-13):
        the sign name as the bold title with its span beneath, the
        image TRIO led by the active style, then the sign's ARTICLE
        (base only — the palette variants speak in hexa arm colors)."""
        day = self._dial.day
        last = day.zodiac_end - timedelta(days=1)
        header = hover_title(html.escape(self._tr(day.zodiac_name))) + centered(
            f"{day.zodiac_start.day} {self._month_short(day.zodiac_start)} – "
            f"{last.day} {self._month_short(last)}",
        )
        article = self._dial.symbolism.zodiac_article(day.zodiac_name)
        return (
            header
            + self._zodiac_image_trio(style, day.zodiac_name)
            + article_body_html(teaser(article["base"]), tr=self._tr)
        )

    def _lunation_ordinal(self, next_cycle: bool = False) -> str:
        """"7<sup>th</sup> Moon of 2026" — which lunation of the
        calendar year is running, counted from the year's FIRST New
        Moon (owner correction 2026-07-12): the days BEFORE it still
        ride the lunation that started in December, so they read as
        the PREVIOUS year's last — 12th or 13th, however many that
        year really began (13 roughly one year in three).
        `next_cycle` reads the FOLLOWING lunation instead (owner logic
        2026-07-13: with the Moon on the dial's left — second half of
        its cycle — the ring past 12h already belongs to the NEXT
        moon, December wrapping into the new year's 1st)."""
        day = self._dial.day
        noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
        if next_cycle:
            # Slide the reading instant just past the next New Moon —
            # the moon_window covers the neighbor years, so the event
            # is always in the data.
            noon = min(
                when for when, name in day.moon_events
                if name == "New Moon" and when > noon
            ) + timedelta(hours=1)
        year = noon.astimezone(day.tzinfo).year
        count = sum(
            1 for when, name in day.moon_events
            if name == "New Moon" and when.year == year and when <= noon
        )
        if count == 0:
            # Early January, before the year's first New Moon — the
            # moon_window covers the neighbor years (data guarantee).
            year -= 1
            count = sum(
                1 for when, name in day.moon_events
                if name == "New Moon" and when.year == year
            )
        return self._tr("{ordinal} Moon of {year}").format(
            ordinal=self._ord(count), year=year
        )

    def _period_word(self, minutes: int) -> str:
        """The day-period a wall-clock minute falls in on THIS date
        (owner approved 2026-07-12): Day, Night or one of the
        twilights — read off today's sun bounds."""
        sun = self._dial.day.sun

        def mins(when: datetime) -> int:
            return when.hour * 60 + when.minute

        if sun.sunrise is not None and sun.sunset is not None:
            if (
                sun.dawn is not None
                and mins(sun.dawn) <= minutes < mins(sun.sunrise)
            ):
                return self._tr("Morning Twilight")
            if mins(sun.sunrise) <= minutes < mins(sun.sunset):
                return self._tr("Day")
            if (
                sun.dusk is not None
                and mins(sun.sunset) <= minutes < mins(sun.dusk)
            ):
                return self._tr("Evening Twilight")
            return self._tr("Night")
        # Polar day / night spans the whole wheel.
        return self._tr("Day" if self._dial.day.day_length == "24:00" else "Night")

    def _tick_tooltip(self, point: QPointF, radius: float) -> str | None:
        """The ring tick band (owner spec 2026-07-12, organized to the
        DOMY letters, formatting round two): hovering any of the 360
        arrows reads that ANGLE on every wheel in titled sections
        separated by blank lines — DAY (labeled time and degree plus
        the day-period word), YEAR (labeled date with the anchor event,
        labeled season with the day/week ordinals) and MOON (the
        running lunation, then the cycle reading at that angle — new
        at the top, full at the bottom, as the marker rides)."""
        distance = math.hypot(point.x(), point.y())
        theta = self._dial.world_theta(point)
        # The unlocked hidden mode (owner 2026-07-16, top-only round):
        # ONLY the 12h ring LETTER — M on DOMY, whatever glyph another
        # ring seats there — opens the Four Greetings. Only the letter
        # band OUTSIDE the tick scale: the ticks at that angle keep
        # their own day/year/moon reading. The 24h (Omega) letter used
        # to share this trigger; it now belongs to the reveal-week
        # double-click instead (see Compositor.hit_omega).
        half = encyclopedia_ui.GREETINGS_JEWEL_HALF_DEG
        # THE INWARD-GROWTH LAW (owner verdict 2026-08-09): the jewel
        # band rides the hour band's centreline, so its inner boundary
        # moves inward with it; the tick reading zone below scales with
        # the interior world. Both are identity at ring_size <= 1.0.
        in_jewel_band = (
            radius * self._dial.band_hit(dial.TICK_HOVER_OUTER_FRACTION)
            < distance
            <= radius * self._dial.band_hit(encyclopedia_ui.GREETINGS_JEWEL_OUTER_FRACTION)
        )
        # The 12h seat is a JEWEL, so the trigger is read in the jewels'
        # own frame (the identity in `all_turn`).
        jewel_theta = self._dial.jewel_theta(theta)
        if (
            in_jewel_band
            and self._dial.hidden_unlocked
            and (jewel_theta <= half or jewel_theta >= 360.0 - half)
        ):
            return self._greetings_tooltip()
        # The per-letter HOVER LEGEND (owner ROADMAP 15b, "malo legende
        # oko tih naših odabira"): a ring preset may carry a `legend`
        # per position (Database/ring_presets.json — the Dollar, DOMY
        # and LOOP today, CROSS-WORDS round 2026-07-27) — what that
        # letter stands for, quoted verbatim from CANON.md's Banknote
        # table. Checked on every letter the active preset seats,
        # independent of the hidden-mode unlock (unlike the Four
        # Greetings, this is not an Easter egg); a preset without a
        # legend (The One/Templar, every custom ring) falls through
        # unchanged.
        if in_jewel_band:
            legend = self._ring_jewel_legend_tooltip(theta, half)
            if legend is not None:
                return legend
        # The arc WORDS answer too (WORD-HOVER round, owner 2026-07-27:
        # "HOVER tekst osim na slova treba i na reči") — the band just
        # outside the ring where the crown-text/station words draw.
        word_legend = self._ring_word_legend_tooltip(theta, distance, radius)
        if word_legend is not None:
            return word_legend
        live_crown = self._live_crown_tooltip(theta, distance, radius)
        if live_crown is not None:
            return live_crown
        if not (
            radius * self._dial.interior_hit(dial.TICK_HOVER_INNER_FRACTION)
            <= distance
            <= radius * self._dial.band_hit(dial.TICK_HOVER_OUTER_FRACTION)
        ):
            return None
        minutes = round((((theta - 180.0) % 360.0) / 15.0) * 60) % (24 * 60)
        line_time = (
            f"{self._label('Time')} {minutes // 60:02d}:{minutes % 60:02d} - "
            f"{self._label('Angle')} {theta:.1f}° - "
            + html.escape(self._period_word(minutes))
        )

        day = self._dial.day
        instant = instant_at_marker_angle(
            day.year_anchors, theta, day.southern_hemisphere
        )
        local = instant.astimezone(day.tzinfo)
        line_date = (
            f"{self._label('Date')} {self._ord(local.day)} "
            f"{html.escape(self._month(local))} {self._year(local)}"
        )
        event = next(
            (
                name for when, name in day.season_events
                if when.astimezone(day.tzinfo).date() == local.date()
            ),
            None,
        )
        if event is not None:
            line_date += f" - {html.escape(self._tr(event))}"
        line_year = html.escape(
            self._tr("{ordinal} Day - {ordinal_week} Week")
        ).format(
            ordinal=self._ord(local.timetuple().tm_yday),
            ordinal_week=self._ord(local.isocalendar().week),
        )
        if day.zone != "tropics":
            passed = [
                (when, name) for when, name in day.season_events
                if when <= instant
            ] or [day.season_events[0]]
            season = max(passed)[1].split()[0]
            line_year = (
                f"{self._label('Season')} "
                f"{html.escape(self._tr(season))} - {line_year}"
            )

        fraction = theta / 360.0
        # Which lunation the hovered ANGLE belongs to (owner logic
        # 2026-07-13): the cycle runs one full ring from the 12h New
        # Moon point. Moon on the LEFT (second half) → the right half
        # of the ring, past 12h again, is already the NEXT moon; Moon
        # on the RIGHT (first half) → the whole ring is the current
        # one (behind it the young past, ahead of it the rest).
        next_cycle = self._dial.tick.moon_fraction > 0.5 and fraction < 0.5
        cycle_day = f"{fraction * sky.SYNODIC_MONTH_DAYS:.1f}"
        line_moon = (
            f"{self._label('Illumination')} "
            f"{nominal_illumination(fraction) * 100:.1f}% - "
            f"{html.escape(self._tr(phase_name(fraction)))} - "
            + html.escape(
                self._tr("Day {day} of {total}").format(
                    day=cycle_day, total=sky.SYNODIC_MONTH_DAYS
                )
            )
        )
        return centered_html(
            f"<b>{html.escape(self._tr('Day'))}</b>",
            line_time,
            "",
            f"<b>{html.escape(self._tr('Year'))}</b>",
            line_date,
            line_year,
            "",
            f"<b>{html.escape(self._tr('Moon'))}</b>",
            self._lunation_ordinal(next_cycle=next_cycle),
            line_moon,
        )

    def _ring_jewel_legend_tooltip(
        self, theta: float, half: float
    ) -> str | None:
        """The per-letter HOVER LEGEND (ROADMAP 15b): `skin.ring.
        jewel_legend` is hour -> {name, reading}, built by
        `app.skin_builder.build_skin` from the active ring preset's
        optional `legend` card (`data.rings.validate_preset`) — the
        Dollar, DOMY and LOOP today (CROSS-WORDS round). Finds the legend entry
        whose OWN jewel position is within `half` degrees of the
        hovered angle (the same half-width the 12h Four Greetings
        trigger uses — every ring jewel occupies the same angular
        slot) and returns its title + reading, or None off any legend
        letter."""
        legend = self._dial.skin.ring.jewel_legend
        if not legend:
            return None
        # WHAT THE ROTATION CARRIES: the cursor arrives in the WORLD
        # frame; a jewel lives in its own (identical in `all_turn`).
        theta = self._dial.jewel_theta(theta)
        for hour, entry in legend.items():
            jewel_theta = angles.ring_position_angle(hour)
            delta = min(
                (theta - jewel_theta) % 360.0,
                (jewel_theta - theta) % 360.0,
            )
            if delta <= half:
                return hover_title(
                    html.escape(entry["name"])
                ) + article_body_html(entry["reading"])
        return None

    def _ring_word_legend_tooltip(
        self, theta: float, distance: float, radius: float
    ) -> str | None:
        """The per-WORD hover on the outer arc text.

        THE ONE TERM ONE HOVER LAW (ring_rework §3, owner ruling
        2026-08-06 — "every crown text carries ITS OWN hover"): when
        the crown-text entry itself carries a `reading` (Database/
        ring_presets.json, `data.rings._validate_crown_text`), every
        word of THAT entry answers with the entry's own reading —
        ANNUIT COEPTIS explains the Latin motto itself, never the
        Anointed Aegis legend of the letter it happens to hang on (the
        exact reported bug the WORD-HOVER round shipped, corrected
        here). Only entries carrying no `reading` of their own (a
        custom ring's free-typed/location crown) fall back to the old
        behaviour: the legend of the SEAT that word belongs to — the
        station words sit ON their station's seat, and the Dollar's
        five words each carry exactly one pinned letter (ANNUIT→A,
        COEPTIS→S, NOVUS→N, ORDO→Ω, SECLORUM→M: the five words spell
        the five letters). Geometry is pre-solved by
        `app.skin_builder.build_skin` into `ring.crown_text[…]["words"]`
        (angular center + half-span per word); here only the band/angle
        test and the reading/legend lookup run. A word with no seat and
        no entry reading, or a seat without a legend entry, stays
        silent — the graceful-absence pattern the letter legend already
        uses."""
        crown_text = self._dial.skin.ring.crown_text
        night_text = self._dial.skin.ring.crown_text_night
        if not crown_text and not night_text:
            return None
        band = dial.RING_CROWN_TEXT_RADIUS_FRACTION
        half_band = dial.RING_CROWN_TEXT_HOVER_HALF_FRACTION
        if not (
            radius * (band - half_band)
            <= distance
            <= radius * (band + half_band)
        ):
            return None
        legend = self._dial.skin.ring.jewel_legend
        # THE ARC READING LAW reaches the hover too (core.world): the
        # drawn arc is REFLECTED, not merely rotated, whenever the world
        # offset carries it across the horizon — so the stored word
        # centre is mapped FORWARD through the same map and compared in
        # screen space, instead of un-rotating the cursor. `_world_theta`
        # already took the offset off, so it goes back on here. Both are
        # identities in Geocentric.
        # WHAT THE ROTATION CARRIES: the SCREEN angle is always the
        # world frame plus the world offset, but the arc itself is
        # placed by the CROWN's own offset — the same number in
        # `all_turn`, 0.0 in `numerals_turn` where the arc stands still.
        screen_theta = (theta + self._dial.world_offset()) % 360.0
        offset = self._dial.jewel_offset()
        # THE INVERTED CROWN TEXTS (owner verdict 2026-08-14): the hover
        # answers for the arcs that are DRAWN — a day entry falls silent
        # once its arc crossed the horizon and its night twin took the
        # seat, by the SAME predicate RingLayer._draw_crown_text paints
        # with (Rule #5: the words and their letters can never disagree
        # about which motto is up).
        for entry, crossed_draws in (
            [(e, False) for e in crown_text]
            + [(e, True) for e in night_text]
        ):
            arc_centre = _crown_arc_centre(entry)
            if night_text and world.arc_crosses_horizon(
                arc_centre, offset
            ) != crossed_draws:
                continue
            entry_reading = entry.get("reading")
            for word in entry.get("words", ()):
                center = world.arc_seat_deg(word["center"], arc_centre, offset)
                delta = min(
                    (screen_theta - center) % 360.0,
                    (center - screen_theta) % 360.0,
                )
                if delta > word["half"]:
                    continue
                if entry_reading is not None:
                    # THE ONE TERM ONE HOVER LAW: the entry speaks for
                    # itself, regardless of which (if any) seat this
                    # word happens to hang on.
                    return hover_title(
                        html.escape(entry_reading["title"])
                    ) + article_body_html(entry_reading["text"])
                if word["seat"] is None:
                    continue
                seat_entry = legend.get(word["seat"] % 24)
                if seat_entry is None:
                    return None
                title = f'{word["text"]} · {seat_entry["name"]}'
                return hover_title(
                    html.escape(title)
                ) + article_body_html(seat_entry["reading"])
        return None

    def _live_crown_tooltip(
        self, theta: float, distance: float, radius: float
    ) -> str | None:
        """The LIVE crown's own hover (ring_rework §1/§3, owner ruling
        2026-08-06 — "the live time/location crowns say whose hour they
        keep"): The One's civil-hour top arc and Templar's Jerusalem-
        hour top arc (`render.layers.numerals.LiveCrownLayer`,
        `dial.RING_LIVE_CROWN`) carry no `crown_text` card entry at all
        — they are rasterized fresh every minute — so their hover text
        lives HERE, in `dial.RING_LIVE_CROWN_READING`, rather than in
        any card. Geometry is approximate on purpose (Rule #7 — the
        live glyphs are never solved into named word spans the way a
        static crown-text entry is): the whole top half of the crown
        band answers, generously covering every digit format the
        setting allows (`hh:mm` / `12h 35min`)."""
        if self._dial.skin.ring_name not in dial.RING_LIVE_CROWN:
            return None
        entry = dial.RING_LIVE_CROWN[self._dial.skin.ring_name]
        band = dial.RING_CROWN_TEXT_RADIUS_FRACTION
        half_band = dial.RING_CROWN_TEXT_HOVER_HALF_FRACTION
        if not (
            radius * (band - half_band)
            <= distance
            <= radius * (band + half_band)
        ):
            return None
        offset = self._dial.world_offset()
        screen_theta = (theta + offset) % 360.0
        anchor = 0.0 if entry["orientation"] == "top" else 180.0
        delta = min(
            (screen_theta - anchor) % 360.0, (anchor - screen_theta) % 360.0
        )
        if delta > dial.RING_LIVE_CROWN_HOVER_HALF_DEG:
            return None
        reading = dial.RING_LIVE_CROWN_READING.get(self._dial.skin.ring_name)
        if reading is None:
            return None
        return hover_title(
            html.escape(reading["title"])
        ) + article_body_html(reading["text"])

    def _ascendant_text(self, style: str | None = None) -> str:
        """The Ascendant hover (owner request 2026-07-12, formatting
        2026-07-13): "Ascendant" as the bold title, the rising sign
        beneath it, the image TRIO led by the active style, then the
        sign's article."""
        sign = self._dial.tick.ascendant_sign
        symbol = dict(constants.ZODIAC_SIGNS)[sign]
        header = hover_title(
            html.escape(self._tr("Ascendant"))
        ) + centered(f"{symbol} {self._tr(sign)}")
        article = self._dial.symbolism.zodiac_article(sign)
        return (
            header
            + self._zodiac_image_trio(style, sign)
            + article_body_html(teaser(article["base"]), tr=self._tr)
        )

    def _greetings_tooltip(self) -> str:
        """The Four Greetings legend (owner 2026-07-14): the verses
        CENTERED in italic with their line breaks kept, then the
        reading and the watchmaker's commentary as a justified column
        — Serbian in every language, on the 12h/24h ring jewels."""
        data = _greetings()
        gap = encyclopedia_ui.GREETINGS_STANZA_GAP_PX
        # Small margins, not blank lines (owner round two) — Qt
        # collapses the adjacent margins to the larger one.
        stanzas = "".join(
            f"<div align='center' style='margin-top:{gap}px;"
            f"margin-bottom:{gap}px'><i>"
            + "<br/>".join(
                html.escape(line) for line in stanza.split("\n")
            )
            + "</i></div>"
            for stanza in data["verses"].split("\n\n")
        )
        return (
            hover_title(html.escape(data["title"]))
            + stanzas
            + article_body_html(
                data["explanation"] + "\n\n" + data["commentary"]
            )
        )

    def _moon_text(self) -> str:
        """Moon hover (owner formatting rounds 2026-07-12/13): the
        PHASE NAME is the title — bigger, bold, no label — with the
        principal-phase instant beneath it, then the labeled data."""
        day = self._dial.day
        tick = self._dial.tick
        name = phase_name(tick.moon_fraction)
        title = hover_title(html.escape(self._tr(name)))
        if name in sky.MOON_PHASE_FRACTIONS:
            # A principal phase name holds ±12 h around its instant —
            # show that instant (the nearest principal event by name),
            # dated like the weekday tooltip (owner 2026-07-14:
            # "14th July", not "14 Jul").
            noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
            instant = min(
                (event for event in day.moon_events if event[1] == name),
                key=lambda event: abs(event[0] - noon),
            )[0].astimezone(day.tzinfo)
            # centered_html — the ordinal carries real <sup> markup
            # (owner bug 2026-07-14: it printed literally through the
            # escaping centered).
            title += centered_html(
                f"{self._ord(instant.day)} {html.escape(self._month(instant))}"
                f" - {instant:%H:%M}"
            )
        lines = [
            f"{self._label('Illumination')} "
            f"{tick.moon_illumination * 100:.1f}%",
        ]
        if day.moonrise is not None and day.moonset is not None:
            lines.append(
                f"{self._label('Moonrise')} {day.moonrise:%H:%M} - "
                f"{self._label('Moonset')} {day.moonset:%H:%M}"
            )
        elif day.moonrise is not None:
            # The moon skips a rise or a set roughly once a month —
            # show the side that exists on this date.
            lines.append(f"{self._label('Moonrise')} {day.moonrise:%H:%M}")
        elif day.moonset is not None:
            lines.append(f"{self._label('Moonset')} {day.moonset:%H:%M}")
        # NO ECLIPSE LINE HERE ANY MORE (owner correction 2026-08-12):
        # the eclipse is its own body with its own card (`_eclipse_text`),
        # so this one speaks the PHASE — which is all the Moon marker
        # shows on an eclipse day, exactly as on any other.
        cycle_day = tick.moon_fraction * sky.SYNODIC_MONTH_DAYS
        return title + centered_html(
            "",
            *lines,
            "",
            html.escape(
                self._tr("Day {day} of {total}").format(
                    day=f"{cycle_day:.1f}",
                    total=sky.SYNODIC_MONTH_DAYS,
                )
            ),
            self._lunation_ordinal(),
        )

    def _season_row(self) -> str:
        """"Summer 20<sup>th</sup> of 94 Days" — the season at the
        current date. The event names already carry the climate zone
        (south flips them), so the season is the starting event's first
        word; the TROPICS read their WET/DRY halves instead (owner
        decision — bounded by the equinoxes, wet centered on the
        hemisphere's high sun)."""
        day = self._dial.day
        noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
        if day.zone == "tropics":
            start, end, is_wet = self._wet_dry_span_at(noon)
            day_no = (day.local_date - start.astimezone(day.tzinfo).date()).days + 1
            total = round((end - start).total_seconds() / 86400)
            return self._tr("{season} {ordinal} of {total} Days").format(
                season=self._tr("Wet season" if is_wet else "Dry season"),
                ordinal=self._ord(day_no), total=total,
            )
        events = day.season_events
        index = max(
            i for i, (instant, _) in enumerate(events) if instant <= noon
        )
        start, name = events[index]
        end = events[index + 1][0]
        season = name.split()[0]        # the season STARTS at its event
        day_no = (day.local_date - start.astimezone(day.tzinfo).date()).days + 1
        total = round((end - start).total_seconds() / 86400)
        return self._tr("{season} {ordinal} of {total} Days").format(
            season=self._tr(season), ordinal=self._ord(day_no), total=total,
        )

    def _wet_dry_span_at(self, noon) -> tuple:
        """(start, end, is_wet) of the tropical half-year at `noon`:
        equinox-bounded, wet = the March→September half north of the
        equator and the September→March half south of it. The one
        boundary that can precede the anchor span (the previous
        September equinox, needed in January–March) is synthesized one
        tropical year before its bundled successor — day-count display
        accuracy."""
        anchors = self._dial.day.year_anchors
        equinoxes = [
            (instant, angle)
            for instant, angle in zip(anchors.instants, anchors.angles)
            if angle % 180.0 == 90.0    # 270 / 450 / 630 — the equinoxes
        ]
        synthetic = (
            equinoxes[1][0] - timedelta(days=sky.TROPICAL_YEAR_DAYS),
            equinoxes[1][1] - 360.0,    # the September equinox before the span
        )
        equinoxes.insert(0, synthetic)
        index = max(
            i for i, (instant, _) in enumerate(equinoxes) if instant <= noon
        )
        start, start_angle = equinoxes[index]
        end = equinoxes[index + 1][0]
        starts_in_march = start_angle % 360.0 == 270.0
        is_wet = starts_in_march != self._dial.day.southern_hemisphere
        return start, end, is_wet

    def _eclipse_type_icon_tag(self, eclipse) -> str:
        """The small per-TYPE eclipse icon (ECLIPSE ICON WIRING round,
        owner 2026-07-20/21) riding inline before the hover-card's
        eclipse line's own title — distinct from the big category
        EMBLEM plate (`_eclipse_emblem`, untouched): LUNAR reads the
        owner-approved red/gold/blue set, SOLAR the proposed shape-
        matched set (`defaults.eclipse_lunar_type_icon` /
        `render.asset_variants.eclipse_solar_type_icon`). Empty string — never
        a broken `<img>` — when the icon has not landed (Rule #1)."""
        icon = (
            defaults.eclipse_lunar_type_icon(eclipse.type)
            if eclipse.kind == "lunar"
            else eclipse_solar_type_icon(eclipse.type)
        )
        if icon is None:
            return ""
        px = glow.ECLIPSE_TYPE_ICON_PX
        small = scaled_variant_file(icon, 2 * px)
        return f"<img src='{small.as_uri()}' width='{px}' align='middle'/> "

    def _eclipse_visibility_text(self, eclipse) -> str:
        """What the observer can actually make of this eclipse: "Visible
        from here", or the REASON it is not (fix round E, 2026-07-19).

        The event is real either way — the body still stands on the dial,
        muted — so the card never simply omits it. A SOLAR eclipse failing
        the distance gate names the distance; everything else (any lunar
        miss, or a solar sun-down miss) reads "below the horizon", the
        only other gate either kind can fail. Round numbers; the km
        threshold itself is never printed (owner spec: config, not UI
        text)."""
        if eclipse.visible:
            return html.escape(self._tr("Visible from here"))
        if (
            eclipse.kind == "solar"
            and eclipse.distance_km is not None
            and eclipse.distance_km > constants.ECLIPSE_SOLAR_VISIBILITY_KM
        ):
            return html.escape(
                self._tr("path {km} km away").format(
                    km=round(eclipse.distance_km)
                )
            )
        return html.escape(self._tr("below the horizon"))

    def _eclipse_text(self) -> str:
        """THE ECLIPSE'S OWN CARD (owner correction 2026-08-12: "the hover
        should show info about the eclipse, not the same as the earth
        hover").

        Until this round the eclipse had no hover of its own for the same
        reason it had no body of its own: it was a costume, so it spoke
        through the Earth's or the Moon's card — one extra line under a
        date or a phase the reader had not asked about. Now the third body
        answers for itself: its own emblem, its own title, and the four
        things an eclipse actually is — which type, how deep, when it
        peaks here, and whether this observer can see it — closed by the
        chapter's own thesis (THE HOVER TEASER LAW; Space opens the rest).

        `self._ord()` returns safe HTML (a raw `<sup>` in English) and
        MUST NOT be escaped again — escaping a composed line (owner bug
        2026-07-18, Session 21-D) once printed the literal `&lt;sup&gt;`.
        Every free-form piece is escaped on its own before joining."""
        eclipse = self._dial.tick.eclipse_body_event
        if eclipse is None:                      # hover raced the minute
            return ""
        instant = eclipse.instant.astimezone(self._dial.day.tzinfo)
        article = self._eclipse_article(eclipse)
        title = (
            article["title"] if article is not None
            else ("Solar Eclipse" if eclipse.kind == "solar" else "Lunar Eclipse")
        )
        mag = (
            f"{eclipse.magnitude:.2f}" if eclipse.magnitude is not None
            else html.escape(self._tr("unknown"))
        )
        card = (
            hover_badge(self._eclipse_emblem(eclipse))
            + hover_title(html.escape(self._tr(title)))
            + centered_html(
                "",
                f"{self._eclipse_type_icon_tag(eclipse)}"
                f"{self._label('Type')} "
                f"{html.escape(self._tr(eclipse.type.capitalize()))}",
                f"{self._label('Magnitude')} {mag}",
                # THE HOUR IS THE SEAT (owner order 2026-08-12, A1): the
                # instant printed here is the very number the body's dial
                # angle is computed from, so the card explains where the
                # reader is looking.
                f"{self._label('Greatest eclipse')} "
                f"{self._ord(instant.day)} {html.escape(self._month(instant))} "
                f"{instant:%H:%M}",
                f"{self._label('Visibility')} "
                f"{self._eclipse_visibility_text(eclipse)}",
                "",
            )
        )
        if article is not None:
            card += article_body_html(teaser(article["base"]), self._tr)
        return card

    def _eclipse_article(self, eclipse) -> dict | None:
        """The eclipse chapter this body belongs to — "Solar_Total",
        "Lunar_Penumbral" and the rest of the catalog's own vocabulary.
        None (never a crash) for a type no chapter was written for: the
        card then keeps its data rows and simply says less."""
        name = f"{eclipse.kind.capitalize()}_{eclipse.type.capitalize()}"
        try:
            return self._dial.encyclopedia.entry("eclipse", name)
        except KeyError:
            return None

    def _label(self, text: str) -> str:
        """A BOLD hover label with its colon (owner formatting round
        2026-07-12: labels bold, values plain)."""
        return f"<b>{html.escape(self._tr(text))}:</b>"

    def _earth_text(self) -> str:
        """Earth hover (owner fix-round B, 2026-07-19, SLIKA 4 — the
        card rework): a Date TITLE over the date/day-of-year/week-of-
        year rows, a blank row, the ERA badge (Age of Light/Darkness
        per the CURRENT real year — deep-travel aware, `real_year`
        un-shifts the proxy frame) over an era TITLE and its Anno
        Lucis year line, a blank row, the SEASON badge (the turning-
        point badge while a season event glows, else the current
        season's own badge — the exact art the arm hovers use) over
        the existing Season:/Sign: lines. Three HTML blocks are
        concatenated directly (never passed as `centered_html` LINES)
        — `hover_title`/`hover_badge` already emit their own centered
        div, matching how every other hover in this file layers badge +
        title + `centered_html` (the cardinal-arm block a few hundred
        lines up). The eclipse/season-event line rides ahead of the
        Season: line — inside the season block, right before it — not
        at the very top of the whole card any more, since the card now
        has sections above it."""
        day, date = self._dial.day, self._dial.day.local_date
        last = day.zodiac_end - timedelta(days=1)
        real = real_year(date.year, day.deep_cycles)
        light = is_age_of_light(real)
        era_name = "Age of Light" if light else "Age of Darkness"
        era_file = "Age_of_Light.png" if light else "Age_of_Darkness.png"

        # Fix round E (owner verdict 2026-07-19, slika 1): this row is
        # ONLY the plain date — no bold "Date:" label prefix (the title
        # above already says "Date") and no Anno Lucis pairing (the era
        # block right below restates it via `format_anno_lucis`). The
        # official year alone, deep-travel aware (`real_year` un-shifts
        # the proxy frame first, matching every other year read here).
        date_block = hover_title(html.escape(self._tr("Date"))) + centered_html(
            f"{self._ord(date.day)} {html.escape(self._month(date))} "
            f"{html.escape(format_official(real, self._dial.skin.era_notation, self._dial.skin.show_era_suffix))}",
            self._tr("{ordinal} Day - {ordinal_week} Week").format(
                ordinal=self._ord(date.timetuple().tm_yday),
                ordinal_week=self._ord(date.isocalendar().week),
            ),
            "",
        )

        # THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20):
        # the canonical era badge plus any `_v2`/`alt/` siblings rotate
        # daily by the VIEWED date — the same one the card's own date
        # row reads (deep-travel aware, `real` already un-shifted it).
        era_art = pantheon.rotating_art_file(
            defaults.ERA_ART_DIR / era_file, date
        ) or defaults.ERA_ART_DIR / era_file
        era_block = (
            hover_badge(era_art)
            + hover_title(html.escape(self._tr(era_name)))
            + centered_html(html.escape(format_anno_lucis(real)), "")
        )

        season_event = self._dial.tick.season_event
        if season_event is not None:
            badge = (
                "Equinox" if "Equinox" in season_event
                else season_event.replace(" ", "_")
            )
            season_art = defaults.SEASON_ART_DIR / "turning_point" / f"{badge}.png"
        else:
            season_art = defaults.SEASON_ART_DIR / f"{self._current_season_key()}.png"

        # NO ECLIPSE LINE HERE ANY MORE (owner correction 2026-08-12):
        # this card is the DATE's, and the eclipse now has a body and a
        # card of its own (`_eclipse_text`) — the season event keeps the
        # row it always had.
        tail = []
        if season_event is not None:
            tail.append(html.escape(self._tr(season_event)))
        tail.append(f"{self._label('Season')} {self._season_row()}")
        tail.append(
            f"{self._label('Sign')} {html.escape(day.zodiac_symbol)} "
            f"{html.escape(self._tr(day.zodiac_name))} "
            f"({self._ord(day.zodiac_start.day)} "
            f"{html.escape(self._month(day.zodiac_start))} - "
            f"{self._ord(last.day)} {html.escape(self._month(last))})"
        )
        season_block = hover_badge(season_art) + centered_html(*tail)

        return date_block + era_block + season_block

    def _period_earth_html(self, kind: str) -> str:
        """The active region's own Earth face rides the Day/Night hover
        (owner 2026-07-12): the day art on the Day side, the night art
        on the Night side — atmosphere or clean per the Earth setting."""
        marker = self._dial.skin.year_marker
        region = earth_region(self._dial.day.latitude, self._dial.day.longitude)
        path = marker.variants.get(
            f"{self._dial.skin.earth_style}_{region}_{kind}"
        )
        if path is None:
            return ""
        small = scaled_variant_file(
            path, 2 * encyclopedia_ui.PERIOD_EARTH_IMAGE_PX
        )
        return (
            f"<div align='center'><img src='{small.as_uri()}' "
            f"width='{encyclopedia_ui.PERIOD_EARTH_IMAGE_PX}'/></div>"
        )

    def _calendar_tooltip(self, point: QPointF, radius: float) -> str | None:
        """The Calendar wedge hover (owner 2026-07-16, kept modest —
        full articles arrive with the archetype engine). Almanac: the
        month name and the wedge's Chinese double-hour animal with its
        clock span, above OUR Chinese COLORED medallion of that animal.
        Zodiac: the sign name with its date span (the existing
        year-wheel cusps), above the sign's COLORED LOGO art — never a
        unicode glyph standing in for the art (owner 2026-07-16, ROADMAP
        queue #7)."""
        from render.calendar_mount import calendar_wheel
        from render.subdial import octa_slot_art

        distance = math.hypot(point.x(), point.y())
        outer = radius * self._dial.interior_hit(self._dial.skin.background.aura_radius_fraction)
        if not (radius * self._dial.interior_hit(0.08) <= distance <= outer):
            return None
        theta = self._dial.world_theta(point)
        step = pointer_geometry.CALENDAR_WEDGE_DEG
        day = self._dial.day
        if calendar_wheel(self._dial.skin) == "almanac":
            index = int((theta + step / 2.0) // step) % 12
            month = (index + 5) % 12 + 1
            animal = constants.CHINESE_ANIMALS[(index - 6) % 12]
            center_hour = (2 * index - 12) % 24
            start_hour, end_hour = (center_hour - 1) % 24, (center_hour + 1) % 24
            art = octa_slot_art(
                complications.CHINESE_STYLE_ART_DIRS["colored"], animal
            )
            return hover_badge(art) + centered_html(
                f"<b>{html.escape(self._tr(_MONTHS[month - 1]))}</b>",
                "",
                html.escape(self._tr(animal)),
                f"{start_hour:02d}:00 - {end_hour:02d}:00",
            )
        # Zodiac: the sign whose wedge starts at this angle (south mirrors
        # the wheel, as the star-arm hover does).
        start_angle = int(theta // step) * step
        if day.southern_hemisphere:
            start_angle = (start_angle + 180.0) % 360.0
        return self._zodiac_wedge_html(int(start_angle) // 30)

    def _zodiac_wedge_html(self, index: int) -> str:
        """Sign name + date span + the COLORED badge for the FIXED
        `constants.ZODIAC_SIGNS[index]` wedge identity — factored out of
        `_calendar_tooltip`'s own zodiac branch (Rule #5) so the mounted
        zodiac mark hover (`_calendar_mount_tooltip`, drawn on this exact
        wedge, never hemisphere-mirrored) speaks the identical text the
        background wedge hover already does."""
        from render.subdial import octa_slot_art

        day = self._dial.day
        name, symbol = constants.ZODIAC_SIGNS[index]
        start, end = zodiac_span(
            day.year_anchors, index * pointer_geometry.CALENDAR_WEDGE_DEG
        )
        start = start.astimezone(day.tzinfo)
        last = end.astimezone(day.tzinfo) - timedelta(days=1)
        art = octa_slot_art(complications.ZODIAC_STYLE_ART_DIRS["colored"], name)
        return hover_badge(art) + centered_html(
            f"<b>{html.escape(symbol)} {html.escape(self._tr(name))}</b>",
            f"{self._ord(start.day)} {html.escape(self._month(start))} - "
            f"{self._ord(last.day)} {html.escape(self._month(last))}",
        )

    def _months_wedge_html(self, index: int) -> str:
        """The mounted Slavic-months mark's hover (owner spec: "month
        name + gloss"): the Croatian proper noun as the bold title, the
        English gloss beneath, above the plate art — graceful-absent
        (owner R7b contract) via the SAME `hover_badge` empty-string
        rule every other emblem uses until the prompt sheet lands."""
        month = (index + 5) % 12 + 1
        croatian, gloss, stem, _gregorian = next(
            entry for entry in calendar_mounts.SLAVIC_MONTHS if entry[3] == month
        )
        art = paths.art_file(defaults.MONTHS_ART_DIR / f"{stem}.png")
        art = art if art.exists() else None
        return hover_badge(art) + centered_html(
            f"<b>{html.escape(self._tr(croatian))}</b>",
            html.escape(self._tr(gloss)),
        )

    def _chinese_mount_wedge_html(self, index: int) -> str:
        """The mounted Chinese MONTHLY animal's hover (owner R12: "animal
        + its month"): the animal's name over its own colored badge,
        its Gregorian month beneath — the SAME register the year-zodiac
        Chinese slot hover already reads. While this exact wedge is the
        one lending its month to The Cat (`chinese_mount_dimmed_index`),
        a short note says so."""
        from render.subdial import octa_slot_art

        gregorian = (index + 5) % 12 + 1
        animal = constants.CHINESE_MONTH_BRANCH_ANIMALS[gregorian]
        art = octa_slot_art("zodiac/chinese/primary/colored", animal)
        # THE BRANCH'S TRUE SPAN (owner 2026-08-05): the wedge is a
        # Gregorian seat, but the branch itself opens on its own solar
        # term and closes the day before the next — so the hover says
        # from when to when, and says "approx." because the term drifts
        # about a day with the leap cycle.
        (open_m, open_d), (close_m, close_d), term = (
            constants.chinese_branch_span(gregorian)
        )
        lines = [
            f"<b>{html.escape(self._tr(animal))}</b>",
            html.escape(self._tr(_MONTHS[gregorian - 1])),
            "≈ {0} {1} – {2} {3} · {4}".format(
                open_d, html.escape(self._tr(_MONTHS_SHORT[open_m - 1])),
                close_d, html.escape(self._tr(_MONTHS_SHORT[close_m - 1])),
                html.escape(term),
            ),
        ]
        if self._dial.day is not None and index == chinese_mount_dimmed_index(self._dial.day):
            lines.append(
                html.escape(self._tr("lending its month to The Cat this year"))
            )
        return hover_badge(art) + centered_html(*lines)

    def _mount_seat_html(self, mount: str, index: int) -> str:
        """The generic mounted-seat hover: the member's name over its own
        plate, graceful-absent through the SAME `hover_badge`
        empty-string rule every other emblem uses. Serves every roster
        that has nothing richer to say than its name (the Emotions
        Dozen, the Month Dozen) — the three sets that DO (a sign's dates,
        a month's gloss, an animal's month) keep their own writers
        above."""
        from render.calendar_mount import calendar_mount_entries

        daylight = self._dial.tick.is_daylight if self._dial.tick is not None else True
        name, art = calendar_mount_entries(mount, daylight)[index]
        # A TWO-DEPICTION seat names BOTH faces (owner ruling 2026-08-05):
        # the dial can only show one at a time, so the hover is where a
        # vice is read at noon. The SHOWN face leads, its opposite follows.
        other = calendar_mounts.CALENDAR_MOUNTS[mount].paint
        if other is not None:
            opposite = (
                other.members[index] if daylight
                else calendar_mounts.CALENDAR_MOUNTS[mount].members[index]
            )
            title = (
                f"<b>{html.escape(self._tr(name))}</b>"
                f" · {html.escape(self._tr(opposite))}"
            )
        else:
            title = f"<b>{html.escape(self._tr(name))}</b>"
        return hover_badge(art) + centered_html(title)

    def _calendar_mount_tooltip(self, point: QPointF, radius: float) -> str | None:
        """The mounted set's seat under the cursor (DESIGN ZODIAC law,
        R9a round; GENERALIZED 2026-07-29) — a small circular target at
        CALENDAR_MOUNT_RADIUS_FRACTION, outranking the broader
        whole-wedge hover beneath it (checked first in `_tooltip_at`).
        Off while no set is mounted. The seat COUNT comes from the
        roster's own registry entry, so a 24-set is hit-tested on all
        twenty-four of its seats without a second loop."""
        mount = self._dial.skin.calendar_mount
        if mount == "off":
            return None
        from render.calendar_mount import calendar_mount_angle, calendar_mount_mark_height
        from render.painting import dial_point

        mount_radius = radius * self._dial.interior_hit(calendar_mounts.CALENDAR_MOUNT_RADIUS_FRACTION)
        hit_radius = calendar_mount_mark_height(mount, radius) / 2.0
        for index in range(calendar_mounts.CALENDAR_MOUNTS[mount].seats):
            center = dial_point(calendar_mount_angle(mount, index), mount_radius)
            dx, dy = point.x() - center.x(), point.y() - center.y()
            if dx * dx + dy * dy <= hit_radius * hit_radius:
                if mount == "zodiac":
                    return self._zodiac_wedge_html(index)
                if mount == "chinese":
                    return self._chinese_mount_wedge_html(index)
                if mount == "months":
                    return self._months_wedge_html(index)
                return self._mount_seat_html(mount, index)
        return None

    def _period_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Aura/Umbra hovers (owner formatting round 2026-07-12): a mini
        Earth of the active region on top, then a bold Day/Night title
        with the duration, the labeled sun span, a blank line, and the
        twilight-extended span under its own With Twilight / Complete
        Dark title. Polar days/nights cover the whole wheel."""
        sun = self._dial.day.sun
        distance = math.hypot(point.x(), point.y())
        theta = self._dial.world_theta(point)
        angle = angles.time_to_dial_angle

        def within(start: float, end: float) -> bool:
            span_end = end if end > start else end + 360.0
            value = theta if theta >= start else theta + 360.0
            return start <= value <= span_end

        hours, minutes = (int(part) for part in self._dial.day.day_length.split(":"))
        if sun.sunrise is not None and sun.sunset is not None:
            in_day = within(angle(sun.sunrise), angle(sun.sunset))
        else:
            in_day = self._dial.day.day_length == "24:00"    # polar day / night
        if in_day:
            if distance > radius * self._dial.interior_hit(self._dial.skin.background.aura_radius_fraction):
                return None
            lines = [
                f"<b>{html.escape(self._tr('Day'))}</b> "
                f"{hours}h {minutes:02d}min"
            ]
            if sun.sunrise is not None and sun.sunset is not None:
                lines.append(
                    f"{self._label('Sunrise')} {sun.sunrise:%H:%M} - "
                    f"{self._label('Sunset')} {sun.sunset:%H:%M}"
                )
            if sun.dawn is not None and sun.dusk is not None:
                lines += [
                    "",
                    f"<b>{html.escape(self._tr('With Twilight'))}</b>",
                    f"{self._label('Dawn')} {sun.dawn:%H:%M} - "
                    f"{self._label('Dusk')} {sun.dusk:%H:%M}",
                ]
            return self._period_earth_html("day") + centered_html(*lines)
        if distance > radius * self._dial.interior_hit(self._dial.skin.background.umbra_radius_fraction):
            return None
        night = 24 * 60 - (hours * 60 + minutes)
        lines = [
            f"<b>{html.escape(self._tr('Night'))}</b> "
            f"{night // 60}h {night % 60:02d}min"
        ]
        if sun.sunset is not None and sun.sunrise is not None:
            lines.append(
                f"{self._label('Sunset')} {sun.sunset:%H:%M} - "
                f"{self._label('Sunrise')} {sun.sunrise:%H:%M}"
            )
        if sun.dusk is not None and sun.dawn is not None:
            lines += [
                "",
                f"<b>{html.escape(self._tr('Complete Dark'))}</b>",
                f"{self._label('Dusk')} {sun.dusk:%H:%M} - "
                f"{self._label('Dawn')} {sun.dawn:%H:%M}",
            ]
        return self._period_earth_html("night") + centered_html(*lines)

    def _twilight_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Hovering a twilight band (owner formatting round 2026-07-12):
        a bold Morning/Evening Twilight title, the labeled boundary
        times in the order the light moves, and the band's span in
        minutes AND dial degrees (15° per hour)."""
        import math

        sun = self._dial.day.sun
        distance = math.hypot(point.x(), point.y())
        if distance > radius * self._dial.interior_hit(self._dial.skin.background.aura_radius_fraction):
            return None
        theta = self._dial.world_theta(point)

        def within(start: float, end: float) -> bool:
            span_end = end if end > start else end + 360.0
            value = theta if theta >= start else theta + 360.0
            return start <= value <= span_end

        def band(title: str, a: str, first: datetime,
                 b: str, second: datetime) -> str:
            span = round((second - first).total_seconds() / 60)
            return centered_html(
                f"<b>{html.escape(self._tr(title))}</b>",
                f"{self._label(a)} {first:%H:%M} - "
                f"{self._label(b)} {second:%H:%M}",
                html.escape(f"{span} min - {span / 4:.2f}°"),
                # Owner 2026-07-12 ("add that info somewhere, in a few
                # words"): the band is CIVIL twilight — the 6° is the
                # Sun's depth, not a dial angle.
                html.escape(
                    self._tr("Civil twilight (Sun 6° below the horizon)")
                ),
            )

        angle = angles.time_to_dial_angle
        if sun.dawn is not None and sun.sunrise is not None and within(
            angle(sun.dawn), angle(sun.sunrise)
        ):
            return band(
                "Morning Twilight", "Dawn", sun.dawn, "Sunrise", sun.sunrise
            )
        if sun.sunset is not None and sun.dusk is not None and within(
            angle(sun.sunset), angle(sun.dusk)
        ):
            return band(
                "Evening Twilight", "Sunset", sun.sunset, "Dusk", sun.dusk
            )
        return None
