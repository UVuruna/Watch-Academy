"""Z-ordered layer stack with cadence-driven caching.

STATIC and DAILY layers are composited into ONE cached pixmap at device
resolution, rebuilt only when the day context, size or DPI changes; the
per-minute paint blits that cache and draws the MINUTE layers (hands,
year marker) live. The same paint path renders offscreen for tests and
the future settings preview.
"""

import html
import math
import re
import textwrap
from datetime import datetime, time, timedelta

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap, QPolygonF

from config import constants, defaults
from config.ui_text import ui
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
    aurora_weekday_theta,
    dial_point,
    south_slot_available,
    south_slot_mode,
    south_slot_theta,
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
    left-aligns plain text). Every line keeps its full width — QToolTip
    would otherwise wrap long lines at its own narrow heuristic (owner
    bug report: "Dusk 21:01" broke onto a new line)."""
    return _centered_html(*(html.escape(line) for line in lines))


def _centered_html(*lines: str) -> str:
    """Centered tooltip from lines that are ALREADY safe HTML (ordinal
    superscripts etc.) — the caller escapes any free-form data. Each
    line is wrapped in a no-wrap div so it owns one full-width row."""
    body = "".join(
        f"<div style='white-space:nowrap'>{line if line else '&nbsp;'}</div>"
        for line in lines
    )
    return f"<div align='center'>{body}</div>"


def _ordinal(n: int) -> str:
    """"9<sup>th</sup>" — the raised ordinal suffix of the hover rework
    (owner spec: the suffix rides above the line)."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}<sup>{suffix}</sup>"


# Canon terms POP in the article prose (owner spec 2026-07-12):
# virtues bold blue, vices bold red, moods bold yellow — always; color
# words ONLY when they are the entity's OWN diamond hue (owner
# correction: the Soldier lights up "orange", never "the red planet";
# `accents` names the allowed color keys). Hex notes like " (#F8E600)"
# never display. Rules are owner-tunable in defaults; matching runs
# over the shipped ORIGINALS (English + Serbian) — machine-translated
# languages read plain.
_HEX_NOTE = re.compile(r"\s*\(#[0-9A-Fa-f]{6}\)")
_TERM_RULES = [
    (
        re.compile(
            rf"\b(?:{'|'.join(defaults.LEGEND_TERM_PATTERNS[category])})\b",
            re.IGNORECASE,
        ),
        hue,
    )
    for category, hue in (
        ("virtue", defaults.LEGEND_VIRTUE_COLOR),
        ("vice", defaults.LEGEND_VICE_COLOR),
        ("mood", defaults.LEGEND_MOOD_COLOR),
    )
]
_COLOR_RULES = {
    key: (re.compile(rf"\b(?:{'|'.join(patterns)})\b", re.IGNORECASE), hue)
    for key, (patterns, hue) in defaults.LEGEND_COLOR_PATTERNS.items()
}


def _highlight_terms(escaped: str, accents: tuple[str, ...] = ()) -> str:
    """Wrap every canon term of an ESCAPED prose line in its colored
    bold span (the markup the rules insert never re-matches a rule);
    color words light up only for the `accents` keys."""
    rules = _TERM_RULES + [_COLOR_RULES[key] for key in accents]
    for pattern, hue in rules:
        escaped = pattern.sub(
            lambda match, hue=hue: (
                f"<b style=\"color:{hue}\">{match.group(0)}</b>"
            ),
            escaped,
        )
    return escaped


def _article_body_html(text: str, accents: tuple[str, ...] = ()) -> str:
    """LEFT-aligned article prose (owner spec — unlike every other
    hover, which is centered): paragraphs separated by a blank line,
    each wrapped to a fixed width so QToolTip stays a column; canon
    terms highlighted (color words only per `accents`), hex notes
    stripped."""
    text = _HEX_NOTE.sub("", text)
    paragraphs = [
        "<br/>".join(
            _highlight_terms(html.escape(line), accents)
            for line in textwrap.wrap(paragraph, width=defaults.ARTICLE_WRAP_CHARS)
        )
        for paragraph in text.split("\n\n")
    ]
    return f"<div align='left'>{'<br/><br/>'.join(paragraphs)}</div>"


def _article_html(
    image, title_html: str | None, text: str,
    accents: tuple[str, ...] = (),
) -> str:
    """One full article hover: the entity's art on top (larger and
    clearer than on the dial — owner EXTRAS), an optional centered
    title line, then the left-aligned prose (color words light up only
    per `accents` — the entity's own diamond hues)."""
    parts = []
    if image is not None and image.exists():
        parts.append(
            f"<div align='center'><img src='{image.as_uri()}' "
            f"width='{defaults.ARTICLE_IMAGE_WIDTH_PX}'/></div>"
        )
    if title_html is not None:
        parts.append(f"<div align='center'>{title_html}</div><br/>")
    parts.append(_article_body_html(text, accents))
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
            if south_slot_available(skin):
                # The SOUTH slot draws BELOW the hands (owner bug
                # report: the seconds hand passed behind the zodiac art)
                # and SURVIVES the Pointer element switch — it has its
                # OWN Elements switch (owner spec + availability matrix
                # 2026-07-12: Compass/Trinity/Aurora always, Prism and
                # Seasons once the Weekday element is off).
                layers.append(BottomSlotLayer(skin))
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
        elif not skipped.get(name, False):
            layers.append(factories[name]())
    if "weekday_set" in skin.z_order and skin.show_weekday:
        # The current day's center body rides ABOVE everything — the
        # hands sweep behind the Sun (owner spec).
        layers.append(CenterBodyLayer(skin))
    return layers


# South of the equator the year wheel runs mirrored (+180°) — these
# unwrapped anchor angles trade places (June solstice <-> December,
# March equinox <-> September).
_SOUTH_ANCHOR_FLIP = {270.0: 450.0, 360.0: 540.0, 450.0: 270.0, 540.0: 360.0}

_MONTHS = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)
_MONTHS_SHORT = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
    "Oct", "Nov", "Dec",
)


class Compositor:
    def __init__(
        self,
        skin: SkinDefinition,
        cache: AssetCache,
        symbolism: SymbolismRepository | None = None,
        overlay: dict | None = None,
    ):
        self._skin = skin
        self._cache = cache
        self._layers = _build_layers(skin)
        # The controller passes a repository with the active language's
        # translation overlay; standalone uses read the originals. The
        # same overlay (Phase 2b) also translates the hover INFO lines
        # — labels, day/month/sign/phase names.
        self._symbolism = symbolism or SymbolismRepository()
        self._overlay = overlay or {}
        self._day: DayContext | None = None
        self._last_tick: TickState | None = None
        self._composite: QPixmap | None = None
        self._composite_key: tuple | None = None
        self._hovered: str | None = None    # hover-enlarge target

    def _tr(self, text: str) -> str:
        """The active language's form of a hover label (Phase 2b)."""
        return ui(self._overlay, text)

    def _ord(self, n: int) -> str:
        """English keeps the raised suffix (owner spec); every other
        language reads the standard European "12."."""
        return f"{n}." if self._overlay else _ordinal(n)

    def _month(self, when) -> str:
        return self._tr(_MONTHS[when.month - 1])

    def _month_short(self, when) -> str:
        return self._tr(_MONTHS_SHORT[when.month - 1])

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
        # The composite carries the window's transparent margin (the
        # ring letters overhang the dial square) — blit it back-shifted
        # so the dial lands at (0, 0).
        overhang = size * defaults.DIAL_WINDOW_MARGIN_FRACTION
        painter.drawPixmap(QPointF(-overhang, -overhang), self._composite)

        painter.save()
        painter.setRenderHints(_RENDER_HINTS)
        painter.translate(size / 2, size / 2)
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=tick,
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self._rotation(), hovered=self._hovered,
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
        rotation = self._rotation()
        today = constants.WEEKDAY_BODIES[self._day.weekday_index]

        element = self._element_at(point, radius, rotation, today)
        if element is not None:
            if element.startswith("body:"):
                # Weekday hover rework (owner spec): the ACTIVE body
                # leads with the date, ghosts show their article alone.
                body = element[len("body:"):]
                return self._weekday_tooltip(body, active=body == today)
            if element == "moon":
                return self._moon_text()
            if element == "earth":
                return self._earth_text()
            # The EFFECTIVE mode (Aurora shows images only — a text
            # mode falls back to the zodiac logo, and the hover must
            # describe what is actually drawn).
            slot_mode = south_slot_mode(self._skin)
            if slot_mode.startswith("chinese"):
                return self._chinese_text()
            if slot_mode.startswith("zodiac"):
                return self._zodiac_text()
            # The time/date/day-length slot has no tooltip of its own —
            # fall through to the region hovers.

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

    def _element_at(
        self, point: QPointF, radius: float, rotation: float, today: str
    ) -> str | None:
        """The enlargeable element under the cursor, in hover priority
        (Rule #5: ONE geometry shared by the tooltips and the
        hover-enlarge effect): a weekday body ("body:<name>"), the octa
        info slot, the Moon, the Earth."""

        def hit(center: QPointF, hit_radius: float) -> bool:
            dx, dy = point.x() - center.x(), point.y() - center.y()
            return dx * dx + dy * dy <= hit_radius * hit_radius

        if self._skin.show_weekday:
            body = self._weekday_body_at(point, radius, rotation, today)
            if body is not None:
                return f"body:{body}"
        weekday = self._skin.weekday_set
        if south_slot_available(self._skin) and hit(
            dial_point(
                south_slot_theta(self._skin, rotation),
                radius * weekday.orbit_fraction,
            ),
            radius * weekday.diamond_scale * self._skin.octa_slot_scale,
        ):
            return "octa_slot"
        marker = self._skin.year_marker
        if self._skin.show_moon and hit(
            dial_point(
                angles.moon_cycle_angle(self._day.moon_fraction),
                radius * marker.moon_orbit_fraction,
            ),
            radius * marker.moon_scale,
        ):
            return "moon"
        if self._skin.show_earth and hit(
            dial_point(self._last_tick.year_angle, radius * marker.orbit_fraction),
            radius * marker.scale,
        ):
            return "earth"
        return None

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
            today = constants.WEEKDAY_BODIES[self._day.weekday_index]
            hovered = self._element_at(point, radius, self._rotation(), today)
        if hovered == self._hovered:
            return False
        self._hovered = hovered
        # Weekday bodies live in the cached DAILY composite — one
        # rebuild per hover change, not per frame.
        self._composite = None
        return True

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
            # Aurora pins the body near the Omega — un-rotated, and
            # shifted to 3h when the south slot shares the bottom; the
            # hit test must match the drawn position.
            if self._skin.pointer == "aurora":
                theta = aurora_weekday_theta(self._skin)
            else:
                theta = angle + rotation
            slot = dial_point(theta, radius * weekday.orbit_fraction)
            if hit(slot, radius * weekday.diamond_scale):
                return body
        return None

    def _weekday_tooltip(self, body: str, active: bool) -> str:
        """The body's ARTICLE — its themed art on top, then the entity
        NAME as a bigger title (owner spec 2026-07-11: the god / planet
        / calling the medallion shows), base plus the paragraph of the
        ACTIVE (pointer, palette) combination; the active day adds
        "Thursday, 9th July 2026" under the name (owner spec), ghosts
        show name and article alone."""
        article_set = constants.WEEKDAY_THEME_ARTICLES[self._skin.weekday_theme]
        node = self._symbolism.article(article_set, body)
        text = node["base"]
        variant = node["variants"].get(self._combo_key())
        if variant:
            text += "\n\n" + variant
        title = (
            f"<span style='font-size: {defaults.ARTICLE_TITLE_PX}px'>"
            f"<b>{html.escape(self._tr(self._skin.weekday_set.body_names[body]))}</b>"
            f"</span>"
        )
        if active:
            date = self._day.local_date
            title += (
                f"<br/>{html.escape(self._tr(constants.WEEKDAY_FULL_NAMES[body]))}, "
                f"{self._ord(date.day)} {html.escape(self._month(date))} {date.year}"
            )
        return _article_html(
            self._skin.weekday_set.bodies.get(body), title, text,
            accents=defaults.BODY_ACCENT_HUES[body],
        )

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
        if self._skin.pointer == "aurora":
            return None      # no arms exist (owner spec 2026-07-12)
        distance = math.hypot(point.x(), point.y())
        star_tip = radius * self._skin.star.radius_fraction
        if not (radius * 0.08 <= distance <= star_tip):
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        arms = constants.POINTER_POINTS[self._skin.pointer]
        arm_step = 360.0 / arms
        arm_angle = (round(((theta - rotation) % 360.0) / arm_step) * arm_step) % 360.0
        # Only INSIDE the drawn diamond (owner bug report): between the
        # arms the wheel itself answers — the Aura's day or the Umbra's
        # night. Same polygon as StarLayer draws.
        half = constants.POINTER_ARM_HALF_ANGLE_DEG[self._skin.pointer]
        inner = star_tip / (2.0 * math.cos(math.radians(half)))
        drawn = arm_angle + rotation
        diamond = QPolygonF(
            [
                QPointF(0.0, 0.0),
                dial_point(drawn - half, inner),
                dial_point(drawn, star_tip),
                dial_point(drawn + half, inner),
            ]
        )
        if not diamond.containsPoint(point, Qt.FillRule.OddEvenFill):
            return None
        star = "*" if self._skin.solar_rotation else ""

        if self._skin.pointer == "hexa":
            # The 60-deg arc [arm-30, arm+30] spans exactly two signs.
            # Hover rework (owner spec): each sign gets its header line
            # ("♋ Cancer (21st June - 21st July)") followed by ITS
            # article (base + the active palette's paragraph), signs
            # separated by a blank line.
            style = self._skin.palette_style
            parts = []
            south = self._day.southern_hemisphere
            for offset in (-30.0, 0.0):      # the two signs' START angles
                start_angle = (arm_angle + offset) % 360.0
                if south:
                    # The mirrored year wheel (owner spec 2026-07-12):
                    # the diamond the Earth passes must name the signs
                    # it actually passes there — the opposite half.
                    start_angle = (start_angle + 180.0) % 360.0
                name, symbol = constants.ZODIAC_SIGNS[int(start_angle) // 30]
                start, end = zodiac_span(self._day.year_anchors, start_angle)
                start = start.astimezone(self._day.tzinfo)
                last = end.astimezone(self._day.tzinfo) - timedelta(days=1)
                header = (
                    f"{html.escape(symbol)} {html.escape(self._tr(name))} "
                    f"({self._ord(start.day)} {html.escape(self._month(start))} - "
                    f"{self._ord(last.day)} {html.escape(self._month(last))})"
                )
                if offset == -30.0 and star:
                    header += html.escape(star)
                article = self._symbolism.zodiac_article(name)
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
                accents = (
                    defaults.SIGN_ACCENT_HUES_SOUTH
                    if south else defaults.SIGN_ACCENT_HUES
                )[name]
                parts.append(
                    f"<div align='center'>{header}</div>"
                    + _article_body_html(text, accents=accents)
                )
            return "<br/>".join(parts)
        if self._skin.pointer == "trio":
            # Trio arm (owner spec): its theological theme, the day
            # third it CENTERS (the arm tip is the middle of its hue),
            # the weekday pair it carries — and the virtue's ARTICLE.
            theme = constants.TRIO_ARM_THEMES[arm_angle]
            start_hour = int((((arm_angle + 180.0) % 360.0) // 15 - 4) % 24)
            end_hour = int((start_hour + 8) % 24)
            bodies = next(
                occupants
                for angle, occupants in constants.POINTER_WEEKDAY_SLOTS["trio"]
                if angle == arm_angle
            )
            days = " · ".join(
                self._tr(constants.WEEKDAY_FULL_NAMES[body]) for body in bodies
            )
            header = _centered_html(
                f"{html.escape(self._tr(theme))}{html.escape(star)}",
                f"{start_hour:02d}:00 - {end_hour:02d}:00",
                html.escape(days),
            )
            article = self._symbolism.trio_article(theme)
            return header + "<br/>" + _article_body_html(
                article["base"], accents=defaults.TRIO_ACCENT_HUES[theme]
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
            if self._day.southern_hemisphere:
                # The year wheel runs MIRRORED south of the equator
                # (the Earth marker already does) — the arms must point
                # at the mirrored anchors too (owner bug 2026-07-12:
                # Sydney's TOP arm must read the DECEMBER solstice).
                anchor_angle = _SOUTH_ANCHOR_FLIP[anchor_angle]
            index = self._day.year_anchors.angles.index(anchor_angle)
            name = self._day.season_events[index][1]      # zone-correct name
            instant = self._anchor_instant(anchor_angle).astimezone(self._day.tzinfo)
            hours, minutes = self._day.anchor_day_lengths[index].split(":")
            lines = [
                f"{html.escape(self._tr(name))}{html.escape(star)}",
                f"{self._ord(instant.day)} {html.escape(self._month(instant))} "
                f"{instant.year} - {instant:%H:%M}",
                f"{int(hours)}h {int(minutes)}min",
            ]
            if self._skin.pointer == "cross":
                lines.append("")
                if self._day.zone == "tropics":
                    # Tropics (owner decision): the cross arms describe
                    # the equinox-bounded WET/DRY halves — the solstice
                    # arms CENTER theirs, the equinox arms START theirs.
                    span_start = 270.0 if anchor_angle in (270.0, 360.0) else 450.0
                    lines += self._wet_dry_block(span_start)
                else:
                    season = self._season_name_for(anchor_angle)
                    met_start, met_end = meteorological_span(
                        self._day.year_anchors, anchor_angle
                    )
                    met_start = met_start.astimezone(self._day.tzinfo)
                    met_end = met_end.astimezone(self._day.tzinfo)
                    lines += [
                        self._tr("Meteorological {season}").format(
                            season=self._tr(season)
                        ),
                        f"{self._tr('From')} {self._ord(met_start.day)} "
                        f"{self._month(met_start)} {met_start.year} - "
                        f"{met_start:%H:%M}",
                        f"{self._tr('To')} {self._ord(met_end.day)} "
                        f"{self._month(met_end)} {met_end.year} - "
                        f"{met_end:%H:%M}",
                    ]
            return _centered_html(*lines)
        # Octa diagonal arms point at the QUARTER centers: the four
        # temperate seasons — or, in the tropics, the halves of the
        # wet/dry seasons (owner spec: TL is the first part of the
        # season the top arms span, TR the second...).
        start_angle = {315.0: 270.0, 45.0: 360.0, 135.0: 450.0, 225.0: 540.0}[
            arm_angle
        ]
        if self._day.southern_hemisphere:
            # Mirrored wheel (see the cardinal arms): the quarters the
            # diagonal arms span flip with it.
            start_angle = _SOUTH_ANCHOR_FLIP[start_angle]
        start = self._anchor_instant(start_angle).astimezone(self._day.tzinfo)
        end = self._anchor_instant(start_angle + 90.0).astimezone(self._day.tzinfo)
        middle = start + (end - start) / 2
        days = (end - start).total_seconds() / 86400
        if self._day.zone == "tropics":
            starts_in_march = start_angle in (270.0, 360.0)
            is_wet = starts_in_march != self._day.southern_hemisphere
            if self._overlay:
                half = self._tr("(1st half)" if start_angle in (270.0, 450.0)
                                else "(2nd half)")
            else:
                half = (
                    "(1<sup>st</sup> half)"
                    if start_angle in (270.0, 450.0)
                    else "(2<sup>nd</sup> half)"
                )
            season_line = (
                f"{self._tr('Wet season' if is_wet else 'Dry season')} {half}"
                f"{html.escape(star)}"
            )
            whole = self._wet_dry_block(270.0 if starts_in_march else 450.0)
            return _centered_html(
                season_line,
                self._span_line(start, end, days),
                f"{self._tr('Heart:')} {self._ord(middle.day)} "
                f"{self._month(middle)}",
                "",
                *whole,
            )
        season = self._season_name_for(start_angle)
        return _centered_html(
            f"{html.escape(self._tr(season))}{html.escape(star)}",
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

    def _wet_dry_block(self, span_start_angle: float) -> list[str]:
        """The whole wet/dry season lines (tropics): name and its
        equinox-to-equinox span with the duration."""
        start = self._anchor_instant(span_start_angle).astimezone(self._day.tzinfo)
        end = self._anchor_instant(span_start_angle + 180.0).astimezone(
            self._day.tzinfo
        )
        starts_in_march = span_start_angle % 360.0 == 270.0
        is_wet = starts_in_march != self._day.southern_hemisphere
        days = (end - start).total_seconds() / 86400
        return [
            self._tr("Wet season" if is_wet else "Dry season"),
            self._span_line(start, end, days),
        ]

    def _season_name_for(self, start_anchor_angle: float) -> str:
        """The temperate season STARTING at an unwrapped anchor angle —
        read from the zone-correct event names (the south already flips
        them): "Autumn Equinox" starts Autumn."""
        index = self._day.year_anchors.angles.index(start_anchor_angle)
        return self._day.season_events[index][1].split()[0]

    def _anchor_instant(self, unwrapped_angle: float):
        """Season-anchor instant at an unwrapped year-wheel angle."""
        anchors = self._day.year_anchors
        return anchors.instants[anchors.angles.index(unwrapped_angle)]

    def _chinese_text(self) -> str:
        """Chinese slot hover (owner rework): the year name and span,
        then the animal's ARTICLE with the owner's medallion on top."""
        from render.layers import octa_slot_art

        day = self._day
        element, animal = day.chinese_name.split()
        header = _centered(
            self._tr("{element} {animal}").format(
                element=self._tr(element), animal=self._tr(animal)
            ),
            f"{day.chinese_start.day} {self._month_short(day.chinese_start)} "
            f"{day.chinese_start.year} – "
            f"{day.chinese_end.day} {self._month_short(day.chinese_end)} "
            f"{day.chinese_end.year}",
        )
        # The animal's article, then the ELEMENT paragraph qualifying
        # THIS return of it (owner spec — each return wears a new one).
        text = (
            self._symbolism.chinese_article(animal)["base"]
            + "\n\n"
            + self._symbolism.chinese_element(element)["base"]
        )
        return header + "<br/>" + _article_html(
            octa_slot_art("chinese_logo", animal), None, text
        )

    def _zodiac_line(self) -> str:
        """"♋ Cancer — 21 Jun – 22 Jul" (sign with its date span)."""
        day = self._day
        last = day.zodiac_end - timedelta(days=1)    # end is the next sign's first day
        return (
            f"{day.zodiac_symbol} {self._tr(day.zodiac_name)} — "
            f"{day.zodiac_start.day} {self._month_short(day.zodiac_start)} – "
            f"{last.day} {self._month_short(last)}"
        )

    def _zodiac_text(self) -> str:
        """Zodiac slot hover (owner rework): the sign and its span, then
        the sign's ARTICLE (base only — the palette variants speak in
        hexa arm colors) with the owner's sign art on top."""
        from render.layers import octa_slot_art

        day = self._day
        last = day.zodiac_end - timedelta(days=1)
        header = _centered(
            f"{day.zodiac_symbol} {self._tr(day.zodiac_name)}",
            f"{day.zodiac_start.day} {self._month_short(day.zodiac_start)} – "
            f"{last.day} {self._month_short(last)}",
        )
        article = self._symbolism.zodiac_article(day.zodiac_name)
        return header + "<br/>" + _article_html(
            octa_slot_art("zodiac_sign", day.zodiac_name), None,
            article["base"],
            accents=defaults.SIGN_ACCENT_HUES[day.zodiac_name],
        )

    def _moon_text(self) -> str:
        """Moon hover (owner rework): the phase — with the exact instant
        in parentheses while a principal name holds — then illumination
        to one decimal, the rise–set span, and the cycle day."""
        day = self._day
        name = phase_name(day.moon_fraction)
        lines = [self._tr(name)]
        if name in constants.MOON_PHASE_FRACTIONS:
            # A principal phase name holds ±12 h around its instant —
            # show that instant (the nearest principal event by name).
            noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
            instant = min(
                (event for event in day.moon_events if event[1] == name),
                key=lambda event: abs(event[0] - noon),
            )[0].astimezone(day.tzinfo)
            lines.append(
                f"({instant.day} {self._month_short(instant)} {instant.year}"
                f" - {instant:%H:%M})"
            )
        lines.append(
            f"{self._tr('Illumination')} {day.moon_illumination * 100:.1f}%"
        )
        if day.moonrise is not None and day.moonset is not None:
            lines.append(f"{day.moonrise:%H:%M} - {day.moonset:%H:%M}")
        elif day.moonrise is not None:
            # The moon skips a rise or a set roughly once a month —
            # show the side that exists on this date.
            lines.append(f"{self._tr('Rises')} {day.moonrise:%H:%M}")
        elif day.moonset is not None:
            lines.append(f"{self._tr('Sets')} {day.moonset:%H:%M}")
        cycle_day = day.moon_fraction * constants.SYNODIC_MONTH_DAYS
        lines.append(
            self._tr("Day {day} of {total}").format(
                day=f"{cycle_day:.1f}", total=constants.SYNODIC_MONTH_DAYS
            )
        )
        return _centered(*lines)

    def _season_row(self) -> str:
        """"Summer 20<sup>th</sup> of 94 Days" — the season at the
        current date. The event names already carry the climate zone
        (south flips them), so the season is the starting event's first
        word; the TROPICS read their WET/DRY halves instead (owner
        decision — bounded by the equinoxes, wet centered on the
        hemisphere's high sun)."""
        day = self._day
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
        anchors = self._day.year_anchors
        equinoxes = [
            (instant, angle)
            for instant, angle in zip(anchors.instants, anchors.angles)
            if angle % 180.0 == 90.0    # 270 / 450 / 630 — the equinoxes
        ]
        synthetic = (
            equinoxes[1][0] - timedelta(days=constants.TROPICAL_YEAR_DAYS),
            equinoxes[1][1] - 360.0,    # the September equinox before the span
        )
        equinoxes.insert(0, synthetic)
        index = max(
            i for i, (instant, _) in enumerate(equinoxes) if instant <= noon
        )
        start, start_angle = equinoxes[index]
        end = equinoxes[index + 1][0]
        starts_in_march = start_angle % 360.0 == 270.0
        is_wet = starts_in_march != self._day.southern_hemisphere
        return start, end, is_wet

    def _earth_text(self) -> str:
        """Earth hover (owner rework), four lines with raised ordinal
        suffixes: the date, day/week ordinals, the season row and the
        zodiac sign with its span in parentheses — plus the season event
        name on top while the marker glows."""
        day, date = self._day, self._day.local_date
        last = day.zodiac_end - timedelta(days=1)
        lines = [
            f"{self._ord(date.day)} {html.escape(self._month(date))} {date.year}",
            self._tr("{ordinal} Day - {ordinal_week} Week").format(
                ordinal=self._ord(date.timetuple().tm_yday),
                ordinal_week=self._ord(date.isocalendar().week),
            ),
            self._season_row(),
            f"{html.escape(day.zodiac_symbol)} "
            f"{html.escape(self._tr(day.zodiac_name))} "
            f"({self._ord(day.zodiac_start.day)} "
            f"{html.escape(self._month(day.zodiac_start))} - "
            f"{self._ord(last.day)} {html.escape(self._month(last))})",
        ]
        if self._last_tick.season_event is not None:
            lines.insert(
                0, html.escape(self._tr(self._last_tick.season_event))
            )
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
            lines = [f"{self._tr('Day')} {hours}h {minutes:02d}min"]
            if sun.sunrise is not None and sun.sunset is not None:
                lines.append(
                    f"{self._tr('Sunrise')} {sun.sunrise:%H:%M} - "
                    f"{self._tr('Sunset')} {sun.sunset:%H:%M}"
                )
            if sun.dawn is not None and sun.dusk is not None:
                lines.append(
                    f"{self._tr('With twilight:')} {self._tr('Dawn')} "
                    f"{sun.dawn:%H:%M} - {self._tr('Dusk')} {sun.dusk:%H:%M}"
                )
            return _centered(*lines)
        if distance > radius * self._skin.background.umbra_radius_fraction:
            return None
        night = 24 * 60 - (hours * 60 + minutes)
        lines = [f"{self._tr('Night')} {night // 60}h {night % 60:02d}min"]
        if sun.sunset is not None and sun.sunrise is not None:
            lines.append(
                f"{self._tr('Sunset')} {sun.sunset:%H:%M} - "
                f"{self._tr('Sunrise')} {sun.sunrise:%H:%M}"
            )
        if sun.dusk is not None and sun.dawn is not None:
            lines.append(
                f"{self._tr('Dark:')} {self._tr('Dusk')} {sun.dusk:%H:%M} - "
                f"{self._tr('Dawn')} {sun.dawn:%H:%M}"
            )
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
        # Two lines per band (owner spec), in the order the light moves.
        if sun.dawn is not None and sun.sunrise is not None and within(
            angle(sun.dawn), angle(sun.sunrise)
        ):
            return _centered(
                f"{self._tr('Dawn')} {sun.dawn:%H:%M}",
                f"{self._tr('Sunrise')} {sun.sunrise:%H:%M}",
            )
        if sun.sunset is not None and sun.dusk is not None and within(
            angle(sun.sunset), angle(sun.dusk)
        ):
            return _centered(
                f"{self._tr('Sunset')} {sun.sunset:%H:%M}",
                f"{self._tr('Dusk')} {sun.dusk:%H:%M}",
            )
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
        # STATIC/DAILY layers include the ring letters, which OVERHANG
        # the dial square (owner spec) — the composite is padded by the
        # same margin the window carries, or they clip right here (owner
        # bug report: the Omega's bottom was cut flat).
        overhang = size * defaults.DIAL_WINDOW_MARGIN_FRACTION
        px = round((size + 2 * overhang) * dpr)
        pixmap = QPixmap(px, px)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHints(_RENDER_HINTS)
        painter.scale(dpr, dpr)
        painter.translate(size / 2 + overhang, size / 2 + overhang)
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=None,
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self._rotation(), hovered=self._hovered,
        )
        for layer in self._layers:
            if layer.cadence is not Cadence.MINUTE:
                painter.save()   # isolate pen/brush/opacity/rotation leaks
                layer.paint(painter, ctx)
                painter.restore()
        painter.end()
        pixmap.setDevicePixelRatio(dpr)
        return pixmap
