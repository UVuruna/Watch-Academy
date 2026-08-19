"""WHAT ARTICLE an element opens — never what it says. One of the four
families `render/tooltip_composer.py` was cut into (owner 2026-08-19),
and the one that answers a different QUESTION rather than a different
subject.

`encyclopedia_target(x, y, size)` is the Spacebar jump and the hover
footer's LEARN MORE link: it maps the element under the cursor to a
(topic, index) pair in the Encyclopedia's own entry order. Everything
here exists to index those orders — the `_ENC_*_ORDER` tables mirror the
Encyclopedia's own listing per topic, and the four `_ENC_*_INDEX`
constants place the thirteenths at the end of the galleries they close.

It works with the LEGEND OFF, which is exactly why it is its own family:
it is geometry and indexing, never text, and it must keep answering when
every tooltip in the other three families is silent.

**How the dial is held: it is NOT.** This is a MIXIN on
`TooltipComposer` — see `render/tooltip_sky.py` for the whole
argument. One holder of the dial, `self._dial`, and every method here
reads it live.

**The door is still `render/tooltip_composer.py`.** `encyclopedia_target`
is a public name on the composer and twenty test files plus the widget
call it there; this module is where its body lives, not where it is
addressed.

Layer: render. Documentation: __about/encyclopedia_targets.md.
"""

import math

from PySide6.QtCore import QPointF

from config import (
    archetypes, calendar_mounts, pantheon, paths, pointer_geometry, sky,
    zodiac,
)
from config.registry import week as week_registry
from core.moon import phase_name
from render.skin_geometry import archetype_key
from render.slot_layout import slot_view, weekday_classic_slot
from render.tooltip_ring import _SOUTH_ANCHOR_FLIP


# The Astrology encyclopedia topic lists its signs in astronomical
# order (Aries first), NOT the year-wheel order of zodiac.ZODIAC_SIGNS
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
# ARTICLE TEXT family is "ninths", `zodiac.THIRTEENTHS`, but the
# gallery page that opens lives in their own zodiac topic, never a
# literal "ninths" topic, which does not exist); Sol/Modrenik close
# "months" (the Overview entry, the twelve Slavic months, THEN the
# pair, `app.encyclopedia._topics`'s own append order).
_ENC_OPHIUCHUS_INDEX = len(_ENC_ZODIAC_ORDER)


_ENC_CAT_INDEX = len(zodiac.CHINESE_ANIMALS) + len(zodiac.CHINESE_ELEMENTS)


_ENC_SOL_INDEX = len(calendar_mounts.SLAVIC_MONTHS) + 1


_ENC_MODRENIK_INDEX = _ENC_SOL_INDEX + 1


_ENC_THIRTEENTH_TARGET = {
    "ophiuchus": ("astrology", _ENC_OPHIUCHUS_INDEX),
    "chinese": ("chinese", _ENC_CAT_INDEX),
    "sol": ("months", _ENC_SOL_INDEX),
    "modrenik": ("months", _ENC_MODRENIK_INDEX),
}


class EncyclopediaTargets:
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
                return "chinese", zodiac.CHINESE_ANIMALS.index(animal)
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
                    zodiac.ZODIAC_SIGNS[int(start_angle) // 30][0]
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
        name = zodiac.ZODIAC_SIGNS[int(start_angle) // 30][0]
        return "astrology", _ENC_ZODIAC_ORDER.index(name)
