"""THE TOOLTIP COMPOSER — the ONE DOOR to everything the dial SAYS.

Every hover the dial answers is built BEHIND this class: the arm
legends, the weekday bodies, the tick readout, the ring's jewels and
words, the crown, the moon, the eclipses, the Earth, the calendar
wedges, the twilight bands — and the Encyclopedia TARGET each of them
jumps to when the reader presses SPACE.

It was ~2,400 lines inside `render/compositor.py`, a module whose job is
to stack paint layers and answer hit tests (OOP audit 2026-08-18, section
3: "measured method by method: 2,126 lines of tooltip / article HTML, 775
of paint and geometry"). Two responsibilities, one file, and the audit
graded the cut HIGH RISK for a reason: these are METHODS over shared
state, not free functions.

So this is a COLLABORATOR of the dial, not a file move. It holds the dial
and asks it for two things, and nothing else:

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

THE FAMILY CUT (owner 2026-08-19). At 2,239 logic lines this was the last
file on the structure ratchet, and its entry had already recorded the
natural next cut: BY TOOLTIP FAMILY. The bodies now live in four modules
beside this one — `render/tooltip_sky.py`, `render/tooltip_ring.py`,
`render/tooltip_calendar.py`, `render/encyclopedia_targets.py` — which
this class INHERITS as MIXINS, so the dial is still held exactly ONCE
and not one call site changed. What stays here is what belongs to no
family: the three doors, the `_tooltip_at` dispatch that decides WHICH
family answers, and the six formatting helpers they all use (`_tr`,
`_ord`, `_month`, `_month_short`, `_year`, `_label`). The move is proved
byte-for-byte by `tests/test_tooltip_families.py`, recorded from the
un-split file.

The dial keeps `tooltip_at`, `encyclopedia_target` and
`warm_hover_articles` as one-line doors, because that is what the widget
and seventeen test files call.

Layer: render. Documentation: __about/tooltip_composer.md.
"""

import html
import math

from PySide6.QtCore import QPointF

from config import dial, encyclopedia_ui, paths, profiling, ring
from config.ui_text import ui
from config.registry import week as week_registry
from core import angles
from core.deep_time import format_year_line, real_year
from render.article_html import learn_more_footer, ordinal
from render.slot_layout import (
    center_dual_face, slot_view, sunday_dual_face, weekday_classic_slot,
)
from render.encyclopedia_targets import EncyclopediaTargets
from render.tooltip_calendar import CalendarTooltips, _MONTHS, _MONTHS_SHORT
from render.tooltip_ring import RingTooltips
from render.tooltip_sky import SkyTooltips


class TooltipComposer(
    SkyTooltips, RingTooltips, CalendarTooltips, EncyclopediaTargets
):
    """Everything the dial says, over the dial it says it about.

    THE ONE DOOR. `tooltip_at`, `encyclopedia_target` and
    `warm_hover_articles` are addressed HERE by the widget and by twenty
    test files, and they always will be; the four bases are where the
    bodies live, not where they are called.

    The dial is held ONCE — `self._dial`, set in `__init__` — and every
    family reads the live skin, day and tick through it. That is why the
    families are MIXINS and not collaborators: a collaborator per family
    would be a second, third and fourth holder of the same dial (the
    ratchet entry's own objection, "three holders is three
    back-channels"), and the call graph crosses the families constantly
    — the ring's `_arm_tooltip` calls the sky's `_wet_dry_block`, the
    calendar's `_tick_tooltip` calls the ring's `_live_crown_tooltip` and
    the sky's `_greetings_tooltip`, the targets' `_element_encyclopedia_
    target` calls the ring's `_active_thirteenth`. `self` already is the
    path between them; a collaborator shape would have had to build one
    by hand for each crossing.

    What stays HERE is what belongs to no family: the two doors, the
    dispatch `_tooltip_at` that decides WHICH family answers, the warm
    sweep, and the six formatting helpers every family uses (`_tr`,
    `_ord`, `_month`, `_month_short`, `_year`, `_label`).
    """

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


    def _label(self, text: str) -> str:
        """A BOLD hover label with its colon (owner formatting round
        2026-07-12: labels bold, values plain)."""
        return f"<b>{html.escape(self._tr(text))}:</b>"
