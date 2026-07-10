"""Z-ordered layer stack with cadence-driven caching.

STATIC and DAILY layers are composited into ONE cached pixmap at device
resolution, rebuilt only when the day context, size or DPI changes; the
per-minute paint blits that cache and draws the MINUTE layers (hands,
year marker) live. The same paint path renders offscreen for tests and
the future settings preview.
"""

import html
import math
import textwrap
from datetime import datetime, time, timedelta

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap

from config import constants, defaults
from data.symbolism import SymbolismRepository
from core import angles
from core.clock_state import DayContext, TickState
from core.moon import phase_name
from core.year_wheel import meteorological_span, zodiac_span
from render.assets import AssetCache
from render.layers import (
    BackgroundLayer,
    BottomSlotLayer,
    Cadence,
    CenterBodyLayer,
    HandLayer,
    Layer,
    RenderContext,
    RingLayer,
    StarLayer,
    WeekdayLayer,
    YearMarkerLayer,
    dial_point,
    today_slot_theta,
    visible_occupant,
)
from skins.manifest import SkinDefinition

_RENDER_HINTS = (
    QPainter.RenderHint.Antialiasing
    | QPainter.RenderHint.SmoothPixmapTransform
    | QPainter.RenderHint.TextAntialiasing
)


def _centered(*lines: str) -> str:
    """Tooltip rich text with CENTERED lines (owner spec — QToolTip
    left-aligns plain text)."""
    body = "<br/>".join(html.escape(line) for line in lines)
    return f"<div align='center'>{body}</div>"


def _centered_html(*lines: str) -> str:
    """Centered tooltip from lines that are ALREADY safe HTML (ordinal
    superscripts etc.) — the caller escapes any free-form data."""
    return f"<div align='center'>{'<br/>'.join(lines)}</div>"


def _ordinal(n: int) -> str:
    """"9<sup>th</sup>" — the raised ordinal suffix of the hover rework
    (owner spec: the suffix rides above the line)."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}<sup>{suffix}</sup>"


def _article_body_html(text: str) -> str:
    """LEFT-aligned article prose (owner spec — unlike every other
    hover, which is centered): paragraphs separated by a blank line,
    each wrapped to a fixed width so QToolTip stays a column."""
    paragraphs = [
        "<br/>".join(
            html.escape(line)
            for line in textwrap.wrap(paragraph, width=defaults.ARTICLE_WRAP_CHARS)
        )
        for paragraph in text.split("\n\n")
    ]
    return f"<div align='left'>{'<br/><br/>'.join(paragraphs)}</div>"


def _article_html(image, title_html: str | None, text: str) -> str:
    """One full article hover: the entity's art on top (larger and
    clearer than on the dial — owner EXTRAS), an optional centered
    title line, then the left-aligned prose."""
    parts = []
    if image is not None and image.exists():
        parts.append(
            f"<div align='center'><img src='{image.as_uri()}' "
            f"width='{defaults.ARTICLE_IMAGE_WIDTH_PX}'/></div>"
        )
    if title_html is not None:
        parts.append(f"<div align='center'>{title_html}</div><br/>")
    parts.append(_article_body_html(text))
    return "".join(parts)


def _build_layers(skin: SkinDefinition) -> list[Layer]:
    factories = {
        "background": lambda: BackgroundLayer(skin),
        "star": lambda: StarLayer(skin),
        "ring": lambda: RingLayer(skin),
        "weekday_set": lambda: WeekdayLayer(skin),
        "year_marker": lambda: YearMarkerLayer(skin),
    }
    # Elements switches (owner spec): a switched-off element is simply
    # not built. The YearMarkerLayer gates Earth/Moon internally (one
    # layer, two markers).
    skipped = {
        "star": not skin.show_pointer,
        "weekday_set": not skin.show_weekday,
        "year_marker": not (skin.show_earth or skin.show_moon),
    }
    layers: list[Layer] = []
    for name in skin.z_order:
        if name == "hands":
            layers.append(HandLayer(skin, "hour"))
            layers.append(HandLayer(skin, "minute"))
            if skin.hands.second is not None and skin.show_seconds:
                layers.append(HandLayer(skin, "second"))
        elif not skipped.get(name, False):
            layers.append(factories[name]())
    if "weekday_set" in skin.z_order and skin.show_weekday:
        # The current day's center body rides ABOVE everything — the
        # hands sweep behind the Sun (owner spec).
        layers.append(CenterBodyLayer(skin))
    if skin.pointer == "octa" and skin.show_pointer:
        # The octa bottom arm's info text also draws OVER the hands
        # (owner spec). It lives in the pointer's bottom arm, so it
        # follows the Pointer element switch.
        layers.append(BottomSlotLayer(skin))
    return layers


class Compositor:
    def __init__(self, skin: SkinDefinition, cache: AssetCache):
        self._skin = skin
        self._cache = cache
        self._layers = _build_layers(skin)
        self._symbolism = SymbolismRepository()
        self._day: DayContext | None = None
        self._last_tick: TickState | None = None
        self._composite: QPixmap | None = None
        self._composite_key: tuple | None = None

    def set_day(self, day: DayContext) -> None:
        self._day = day
        self._composite = None

    def invalidate(self) -> None:
        """Size/DPI/screen change: drop the composite and rasterized assets."""
        self._composite = None
        self._cache.flush()

    def _rotation(self) -> float:
        """Star/Aura/Umbra/slot rotation: solar offset, or 0 upright."""
        return self._day.star_rotation if self._skin.solar_rotation else 0.0

    def paint(self, painter: QPainter, size: float, dpr: float, tick: TickState) -> None:
        if self._day is None:
            raise RuntimeError("Compositor.paint() before the first day context")
        self._last_tick = tick
        key = (round(size * dpr), self._day.cache_key)
        if self._composite is None or self._composite_key != key:
            self._composite = self._render_composite(size, dpr)
            self._composite_key = key
        painter.drawPixmap(QPointF(0, 0), self._composite)

        painter.save()
        painter.setRenderHints(_RENDER_HINTS)
        painter.translate(size / 2, size / 2)
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=tick,
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self._rotation(),
        )
        for layer in self._layers:
            if layer.cadence is Cadence.MINUTE:
                painter.save()   # isolate pen/brush/opacity/rotation leaks
                layer.paint(painter, ctx)
                painter.restore()
        painter.restore()

    def tooltip_at(self, x: float, y: float, size: float) -> str | None:
        """Hover text under the cursor, at every dial size (owner spec):
        today's body, the Earth marker (day/week ordinals, zodiac sign
        with its dates, the date — plus the season event while it glows),
        the Moon marker (phase + illumination, day in the cycle), the
        octa zodiac slot and the twilight bands."""
        if self._day is None or self._last_tick is None:
            return None
        if not self._skin.legend:
            # Legend off (owner spec): NO hovers at all — combined with
            # click-through the dial has zero interaction.
            return None
        radius = size / 2
        point = QPointF(x - radius, y - radius)      # center-origin
        day, tick = self._day, self._last_tick
        rotation = self._rotation()

        def hit(center: QPointF, hit_radius: float) -> bool:
            dx, dy = point.x() - center.x(), point.y() - center.y()
            return dx * dx + dy * dy <= hit_radius * hit_radius

        today = constants.WEEKDAY_BODIES[day.weekday_index]
        if self._skin.show_weekday:
            # Weekday hover rework (owner spec): the ACTIVE body leads
            # with the date, ghosts show their article alone — each only
            # within its own image region.
            body = self._weekday_body_at(point, radius, rotation, today)
            if body is not None:
                return self._weekday_tooltip(body, active=body == today)

        if self._skin.pointer == "octa" and self._skin.show_pointer and (
            self._skin.octa_slot.startswith("zodiac")
            or self._skin.octa_slot.startswith("chinese")
        ):
            slot_pos = dial_point(
                constants.OCTA_TIME_SLOT_ANGLE + rotation,
                radius * self._skin.weekday_set.orbit_fraction,
            )
            if hit(slot_pos, radius * self._skin.weekday_set.diamond_scale):
                if self._skin.octa_slot.startswith("chinese"):
                    return self._chinese_text()
                return self._zodiac_text()

        marker = self._skin.year_marker
        moon_angle = angles.moon_cycle_angle(day.moon_fraction)
        if self._skin.show_moon:
            moon_pos = dial_point(moon_angle, radius * marker.moon_orbit_fraction)
            if hit(moon_pos, radius * marker.moon_scale):
                return self._moon_text()
        if self._skin.show_earth and hit(
            dial_point(tick.year_angle, radius * marker.orbit_fraction),
            radius * marker.scale,
        ):
            return self._earth_text()

        # Twilight bands BEFORE the arm hovers (owner: the dawn/dusk
        # info must never be shadowed — e.g. by a glowing quarter moon
        # sitting right on the 06h/18h band).
        twilight = self._twilight_tooltip(point, radius)
        if twilight is not None:
            return twilight

        arm = self._arm_tooltip(point, radius, rotation)
        if arm is not None:
            return arm
        # Last in the chain (owner rework 5 & 6): the sunlit arc answers
        # with the day, the dark of the wheel with the night.
        return self._period_tooltip(point, radius)

    def _combo_key(self) -> str:
        """The (pointer, palette) combination the articles vary by —
        "hexa_paint", "octa_light", "cross", "trio" (cross and trio have
        a single palette under both styles)."""
        pointer = self._skin.pointer
        if pointer in ("cross", "trio"):
            return pointer
        return f"{pointer}_{self._skin.palette_style}"

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
            QPointF(0, 0), radius * weekday.center_scale
        ):
            return center_body
        if weekday.display_mode == "center_only":
            return None                  # no slot bodies in this mode
        for angle, occupants in constants.POINTER_WEEKDAY_SLOTS[self._skin.pointer]:
            body = visible_occupant(occupants, today)
            slot = dial_point(angle + rotation, radius * weekday.orbit_fraction)
            if hit(slot, radius * weekday.diamond_scale):
                return body
        return None

    def _weekday_tooltip(self, body: str, active: bool) -> str:
        """The body's ARTICLE — its themed art on top, base plus the
        paragraph of the ACTIVE (pointer, palette) combination; the
        active day leads with "Thursday, 9th July 2026" (owner spec),
        ghosts show the article alone."""
        article_set = constants.WEEKDAY_THEME_ARTICLES[self._skin.weekday_theme]
        node = self._symbolism.article(article_set, body)
        text = node["base"]
        variant = node["variants"].get(self._combo_key())
        if variant:
            text += "\n\n" + variant
        title = None
        if active:
            date = self._day.local_date
            title = (
                f"{html.escape(constants.WEEKDAY_FULL_NAMES[body])}, "
                f"{_ordinal(date.day)} {date:%B %Y}"
            )
        return _article_html(self._skin.weekday_set.bodies.get(body), title, text)

    def _arm_tooltip(self, point: QPointF, radius: float, rotation: float) -> str | None:
        """Hover over a star arm (owner spec): hexa arms name their TWO
        zodiac signs; cross/octa cardinal arms give the exact instant of
        the solstice/equinox they point at; octa diagonal arms describe
        their season (dates, duration, the middle date the arrow points
        at). With solar rotation on, a trailing * flags the slight
        offset from the year-wheel positions."""
        if not self._skin.show_pointer:
            # Pointer element off: no visible arms, no arm hovers.
            return None
        distance = math.hypot(point.x(), point.y())
        star_tip = radius * self._skin.star.radius_fraction
        if not (radius * 0.08 <= distance <= star_tip):
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        arms = constants.POINTER_POINTS[self._skin.pointer]
        arm_step = 360.0 / arms
        arm_angle = (round(((theta - rotation) % 360.0) / arm_step) * arm_step) % 360.0
        star = "*" if self._skin.solar_rotation else ""

        if self._skin.pointer == "hexa":
            # The 60-deg arc [arm-30, arm+30] spans exactly two signs.
            # Hover rework (owner spec): each sign gets its header line
            # ("♋ Cancer (21st June - 21st July)") followed by ITS
            # article (base + the active palette's paragraph), signs
            # separated by a blank line.
            style = self._skin.palette_style
            parts = []
            for offset in (-30.0, 0.0):      # the two signs' START angles
                start_angle = (arm_angle + offset) % 360.0
                name, symbol = constants.ZODIAC_SIGNS[int(start_angle) // 30]
                start, end = zodiac_span(self._day.year_anchors, start_angle)
                start = start.astimezone(self._day.tzinfo)
                last = end.astimezone(self._day.tzinfo) - timedelta(days=1)
                header = (
                    f"{html.escape(symbol)} {html.escape(name)} "
                    f"({_ordinal(start.day)} {start:%B} - "
                    f"{_ordinal(last.day)} {last:%B})"
                )
                if offset == -30.0 and star:
                    header += html.escape(star)
                article = self._symbolism.zodiac_article(name)
                text = article["base"]
                variant = article["variants"].get(style)
                if variant:
                    text += "\n\n" + variant
                parts.append(
                    f"<div align='center'>{header}</div>"
                    + _article_body_html(text)
                )
            return "<br/>".join(parts)
        if self._skin.pointer == "trio":
            # Trio arm: its theological theme, the day third it CENTERS
            # (the arm tip is the middle of its hue — owner correction)
            # and the weekday pair it carries. The hover rework will
            # grow this.
            theme = constants.TRIO_ARM_THEMES[arm_angle]
            start_hour = int((((arm_angle + 180.0) % 360.0) // 15 - 4) % 24)
            end_hour = int((start_hour + 8) % 24)
            bodies = next(
                occupants
                for angle, occupants in constants.POINTER_WEEKDAY_SLOTS["trio"]
                if angle == arm_angle
            )
            days = " · ".join(
                constants.WEEKDAY_FULL_NAMES[body] for body in bodies
            )
            return _centered(
                f"{theme}{star}",
                f"{start_hour:02d}:00 – {end_hour:02d}:00",
                days,
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
            name = constants.SEASON_EVENT_NAMES[round(anchor_angle) % 360]
            instant = self._anchor_instant(anchor_angle).astimezone(self._day.tzinfo)
            index = self._day.year_anchors.angles.index(anchor_angle)
            hours, minutes = self._day.anchor_day_lengths[index].split(":")
            lines = [
                f"{html.escape(name)}{html.escape(star)}",
                f"{_ordinal(instant.day)} {instant:%B %Y} - {instant:%H:%M}",
                f"{int(hours)}h {int(minutes)}min",
            ]
            if self._skin.pointer == "cross":
                season = self._season_name_for(anchor_angle)
                met_start, met_end = meteorological_span(
                    self._day.year_anchors, anchor_angle
                )
                met_start = met_start.astimezone(self._day.tzinfo)
                met_end = met_end.astimezone(self._day.tzinfo)
                lines += [
                    "",
                    f"Meteorological {season}",
                    f"From {_ordinal(met_start.day)} {met_start:%B %Y} - "
                    f"{met_start:%H:%M}",
                    f"To {_ordinal(met_end.day)} {met_end:%B %Y} - "
                    f"{met_end:%H:%M}",
                ]
            return _centered_html(*lines)
        # Octa diagonal arms point at the season CENTERS.
        start_angle = {315.0: 270.0, 45.0: 360.0, 135.0: 450.0, 225.0: 540.0}[
            arm_angle
        ]
        season = self._season_name_for(start_angle)
        start = self._anchor_instant(start_angle).astimezone(self._day.tzinfo)
        end = self._anchor_instant(start_angle + 90.0).astimezone(self._day.tzinfo)
        middle = start + (end - start) / 2
        days = (end - start).total_seconds() / 86400
        return _centered_html(
            f"{html.escape(season)}{html.escape(star)}",
            f"{_ordinal(start.day)} {start:%B} - {_ordinal(end.day)} {end:%B} "
            f"({days:.1f} Days)",
            f"Heart: {_ordinal(middle.day)} {middle:%B}",
        )

    def _season_name_for(self, start_anchor_angle: float) -> str:
        """The season STARTING at an unwrapped anchor angle, flipped on
        the southern hemisphere (their seasons are opposite)."""
        season = {270.0: "Spring", 360.0: "Summer", 450.0: "Autumn", 540.0: "Winter"}[
            start_anchor_angle
        ]
        if self._day.southern_hemisphere:
            season = {
                "Summer": "Winter", "Winter": "Summer",
                "Spring": "Autumn", "Autumn": "Spring",
            }[season]
        return season

    def _anchor_instant(self, unwrapped_angle: float):
        """Season-anchor instant at an unwrapped year-wheel angle."""
        anchors = self._day.year_anchors
        return anchors.instants[anchors.angles.index(unwrapped_angle)]

    def _chinese_text(self) -> str:
        """Slot hover, two lines (owner spec): name, then the year span."""
        day = self._day
        return _centered(
            day.chinese_name,
            f"{day.chinese_start.day} {day.chinese_start:%b %Y} – "
            f"{day.chinese_end.day} {day.chinese_end:%b %Y}",
        )

    def _zodiac_line(self) -> str:
        """"♋ Cancer — 21 Jun – 22 Jul" (sign with its date span)."""
        day = self._day
        last = day.zodiac_end - timedelta(days=1)    # end is the next sign's first day
        return (
            f"{day.zodiac_symbol} {day.zodiac_name} — "
            f"{day.zodiac_start.day} {day.zodiac_start:%b} – {last.day} {last:%b}"
        )

    def _zodiac_text(self) -> str:
        """Slot hover, two lines (owner spec): name, then the date span."""
        day = self._day
        last = day.zodiac_end - timedelta(days=1)
        return _centered(
            f"{day.zodiac_symbol} {day.zodiac_name}",
            f"{day.zodiac_start.day} {day.zodiac_start:%b} – {last.day} {last:%b}",
        )

    def _moon_text(self) -> str:
        """Moon hover (owner rework): the phase — with the exact instant
        in parentheses while a principal name holds — then illumination
        to one decimal, the rise–set span, and the cycle day."""
        day = self._day
        name = phase_name(day.moon_fraction)
        lines = [name]
        if name in constants.MOON_PHASE_FRACTIONS:
            # A principal phase name holds ±12 h around its instant —
            # show that instant (the nearest principal event by name).
            noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
            instant = min(
                (event for event in day.moon_events if event[1] == name),
                key=lambda event: abs(event[0] - noon),
            )[0].astimezone(day.tzinfo)
            lines.append(
                f"({instant.day} {instant:%b %Y} - {instant:%H:%M})"
            )
        lines.append(f"Illumination {day.moon_illumination * 100:.1f}%")
        if day.moonrise is not None and day.moonset is not None:
            lines.append(f"{day.moonrise:%H:%M} - {day.moonset:%H:%M}")
        elif day.moonrise is not None:
            # The moon skips a rise or a set roughly once a month —
            # show the side that exists on this date.
            lines.append(f"Rises {day.moonrise:%H:%M}")
        elif day.moonset is not None:
            lines.append(f"Sets {day.moonset:%H:%M}")
        cycle_day = day.moon_fraction * constants.SYNODIC_MONTH_DAYS
        lines.append(f"Day {cycle_day:.1f} of {constants.SYNODIC_MONTH_DAYS}")
        return _centered(*lines)

    def _season_row(self) -> str:
        """"Summer 20<sup>th</sup> of 94 Days" — the astronomical season
        at the current date: bracketing anchors by instant, the NAME
        flipped on the southern hemisphere (their seasons are opposite;
        the tropics keep the astronomical row until the owner decides
        the wet/dry split)."""
        day = self._day
        noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
        events = day.season_events
        index = max(
            i for i, (instant, _) in enumerate(events) if instant <= noon
        )
        start, name = events[index]
        end = events[index + 1][0]
        season = name.split()[0]        # the season STARTS at its event
        if day.southern_hemisphere:
            season = {
                "Summer": "Winter", "Winter": "Summer",
                "Spring": "Autumn", "Autumn": "Spring",
            }[season]
        day_no = (day.local_date - start.astimezone(day.tzinfo).date()).days + 1
        total = round((end - start).total_seconds() / 86400)
        return f"{season} {_ordinal(day_no)} of {total} Days"

    def _earth_text(self) -> str:
        """Earth hover (owner rework), four lines with raised ordinal
        suffixes: the date, day/week ordinals, the season row and the
        zodiac sign with its span in parentheses — plus the season event
        name on top while the marker glows."""
        day, date = self._day, self._day.local_date
        last = day.zodiac_end - timedelta(days=1)
        lines = [
            f"{_ordinal(date.day)} {date:%B %Y}",
            f"{_ordinal(date.timetuple().tm_yday)} Day - "
            f"{_ordinal(date.isocalendar().week)} Week",
            self._season_row(),
            f"{html.escape(day.zodiac_symbol)} {html.escape(day.zodiac_name)} "
            f"({_ordinal(day.zodiac_start.day)} {day.zodiac_start:%B} - "
            f"{_ordinal(last.day)} {last:%B})",
        ]
        if self._last_tick.season_event is not None:
            lines.insert(0, html.escape(self._last_tick.season_event))
        return _centered_html(*lines)

    def _period_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Aura/Umbra hovers (owner rework): the sunlit arc gives the
        DAY — duration, the sun span, and the twilight-extended span;
        the dark of the wheel gives the NIGHT — duration (24 h minus
        this date's day length) with the sunset–sunrise and dusk–dawn
        bounds. Polar days/nights cover the whole wheel accordingly."""
        sun = self._day.sun
        distance = math.hypot(point.x(), point.y())
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        angle = angles.time_to_dial_angle

        def within(start: float, end: float) -> bool:
            span_end = end if end > start else end + 360.0
            value = theta if theta >= start else theta + 360.0
            return start <= value <= span_end

        hours, minutes = (int(part) for part in self._day.day_length.split(":"))
        if sun.sunrise is not None and sun.sunset is not None:
            in_day = within(angle(sun.sunrise), angle(sun.sunset))
        else:
            in_day = self._day.day_length == "24:00"    # polar day / night
        if in_day:
            if distance > radius * self._skin.background.aura_radius_fraction:
                return None
            lines = [f"Day {hours}h {minutes:02d}min"]
            if sun.sunrise is not None and sun.sunset is not None:
                lines.append(
                    f"Sunrise {sun.sunrise:%H:%M} - Sunset {sun.sunset:%H:%M}"
                )
            if sun.dawn is not None and sun.dusk is not None:
                lines.append(
                    f"With twilight: Dawn {sun.dawn:%H:%M} - Dusk {sun.dusk:%H:%M}"
                )
            return _centered(*lines)
        if distance > radius * self._skin.background.umbra_radius_fraction:
            return None
        night = 24 * 60 - (hours * 60 + minutes)
        lines = [f"Night {night // 60}h {night % 60:02d}min"]
        if sun.sunset is not None and sun.sunrise is not None:
            lines.append(f"Sunset {sun.sunset:%H:%M} - Sunrise {sun.sunrise:%H:%M}")
        if sun.dusk is not None and sun.dawn is not None:
            lines.append(f"Dark: Dusk {sun.dusk:%H:%M} - Dawn {sun.dawn:%H:%M}")
        return _centered(*lines)

    def _twilight_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Hovering a twilight band names its boundary times (owner spec):
        the morning band reads dawn/sunrise, the evening band sunset/dusk."""
        import math

        sun = self._day.sun
        distance = math.hypot(point.x(), point.y())
        if distance > radius * self._skin.background.aura_radius_fraction:
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0

        def within(start: float, end: float) -> bool:
            span_end = end if end > start else end + 360.0
            value = theta if theta >= start else theta + 360.0
            return start <= value <= span_end

        angle = angles.time_to_dial_angle
        if sun.dawn is not None and sun.sunrise is not None and within(
            angle(sun.dawn), angle(sun.sunrise)
        ):
            return _centered(f"Dawn {sun.dawn:%H:%M} — Sunrise {sun.sunrise:%H:%M}")
        if sun.sunset is not None and sun.dusk is not None and within(
            angle(sun.sunset), angle(sun.dusk)
        ):
            return _centered(f"Sunset {sun.sunset:%H:%M} — Dusk {sun.dusk:%H:%M}")
        return None

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

    def _render_composite(self, size: float, dpr: float) -> QPixmap:
        px = round(size * dpr)
        pixmap = QPixmap(px, px)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHints(_RENDER_HINTS)
        painter.scale(dpr, dpr)
        painter.translate(size / 2, size / 2)
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=None,
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self._rotation(),
        )
        for layer in self._layers:
            if layer.cadence is not Cadence.MINUTE:
                painter.save()   # isolate pen/brush/opacity/rotation leaks
                layer.paint(painter, ctx)
                painter.restore()
        painter.end()
        pixmap.setDevicePixelRatio(dpr)
        return pixmap
