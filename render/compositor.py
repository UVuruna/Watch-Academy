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
from datetime import datetime, time, timedelta

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap, QPolygonF

from config import constants, defaults
from config.ui_text import ui
from data.symbolism import SymbolismRepository
from core import angles
from core.clock_state import DayContext, TickState
from core.moon import illumination, phase_name
from core.year_wheel import (
    instant_at_marker_angle,
    meteorological_span,
    zodiac_span,
)
from render.assets import AssetCache, metal_variant_file, scaled_variant_file
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
    WeekdayBadgeLayer,
    WeekdayLayer,
    YearMarkerLayer,
    HoverLiftLayer,
    dial_point,
    pinned_weekday_theta,
    servant_holds_the_seat,
    south_slot_available,
    south_slot_centered,
    south_slot_theta,
    south_slot_view,
    sunday_dual_face,
    today_slot_theta,
    visible_occupant,
    weekday_badge,
    weekday_pinned,
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


# Subheadings (owner 2026-07-14): article paragraphs may open with a
# [[Subhead]] marker from the FIXED vocabulary — rendered as a bold
# heading line, translated through the ui catalog.
_SUBHEAD = re.compile(r"^\[\[(.+?)\]\]\s*")


def _article_paragraphs(
    text: str, accents: tuple[str, ...] = (), tr=None,
) -> str:
    """The bare JUSTIFIED paragraphs of an article (owner 2026-07-13
    round two — clean edges on both sides, like a book column): canon
    terms highlighted (color words only per `accents`), hex notes
    stripped, [[Subhead]] markers drawn as bold headings (owner
    2026-07-14; `tr` localizes the label). The caller provides the
    width-constrained cell."""
    text = _HEX_NOTE.sub("", text)
    parts = []
    for p in text.split("\n\n"):
        match = _SUBHEAD.match(p)
        body_style = ""
        if match:
            label = match.group(1)
            if tr is not None:
                label = tr(label)
            # CENTERED, hugging its own paragraph (owner 2026-07-14
            # round two: the gap above must beat the gap below).
            parts.append(
                "<p align='center' style='"
                f"margin-top:{defaults.ARTICLE_SUBHEAD_GAP_ABOVE_PX}px;"
                f"margin-bottom:{defaults.ARTICLE_SUBHEAD_GAP_BELOW_PX}px'>"
                f"<b>{html.escape(label)}</b></p>"
            )
            p = p[match.end():]
            body_style = (
                f" style='margin-top:"
                f"{defaults.ARTICLE_SUBHEAD_GAP_BELOW_PX}px'"
            )
        parts.append(
            f"<p align='justify'{body_style}>"
            f"{_highlight_terms(html.escape(p), accents)}</p>"
        )
    return "".join(parts)


def _article_body_html(
    text: str, accents: tuple[str, ...] = (), tr=None,
) -> str:
    """One article as a single fixed-width column: the paragraphs
    reflow inside the declared table cell (the legend popup measures
    the document and honors this width)."""
    return (
        f"<table><tr><td width='{defaults.ARTICLE_TEXT_WIDTH_PX}'>"
        f"{_article_paragraphs(text, accents, tr)}</td></tr></table>"
    )


def _hover_title(text_html: str) -> str:
    """A hover TITLE line (owner 2026-07-13 round two): bigger and
    bold, centered — the phase name, the Ascendant word, the season
    and turning-point names all wear it."""
    return (
        f"<div align='center'><span style='font-size:"
        f"{defaults.ARTICLE_TITLE_PX}px; font-weight:bold'>"
        f"{text_html}</span></div>"
    )


def _article_html(
    image, title_html: str | None, text: str,
    accents: tuple[str, ...] = (), tr=None,
) -> str:
    """One full article hover: the entity's art on top (larger and
    clearer than on the dial — owner EXTRAS; a TUPLE draws the images
    side by side — the dual Sunday's two plates, owner 2026-07-13), an
    optional centered title line, then the left-aligned prose (color
    words light up only per `accents` — the entity's own diamond
    hues)."""
    parts = []
    images = image if isinstance(image, tuple) else (image,)
    tags = "".join(
        f"<img src='"
        f"{scaled_variant_file(img, 2 * defaults.ARTICLE_IMAGE_WIDTH_PX).as_uri()}' "
        f"width='{defaults.ARTICLE_IMAGE_WIDTH_PX}'/>"
        for img in images
        if img is not None and img.exists()
    )
    if tags:
        parts.append(f"<div align='center'>{tags}</div>")
    if title_html is not None:
        parts.append(f"<div align='center'>{title_html}</div><br/>")
    parts.append(_article_body_html(text, accents, tr))
    return "".join(parts)


def _hover_badge(path) -> str:
    """The emblem above an arm hover (owner 2026-07-13: the trinity,
    season and turning-point badges ride their tooltips) — empty when
    the art is missing."""
    if path is None or not path.exists():
        return ""
    small = scaled_variant_file(path, 2 * defaults.HOVER_BADGE_WIDTH_PX)
    return (
        f"<div align='center'><img src='{small.as_uri()}' "
        f"width='{defaults.HOVER_BADGE_WIDTH_PX}'/></div>"
    )


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
            if skin.show_weekday and skin.weekday_slot != "weekday":
                # The astrology badge in the weekday position (owner
                # 2026-07-12) — MINUTE cadence, below the hands.
                layers.append(WeekdayBadgeLayer(skin))
            if south_slot_available(skin) and not south_slot_centered(skin):
                # The BOTTOM slot draws BELOW the hands (owner bug
                # report: the seconds hand passed behind the zodiac
                # art) and SURVIVES the Pointer element switch — it has
                # its OWN Elements switch (owner matrix, dual-Sunday
                # round 2026-07-12: Compass/Seasons in the center,
                # pinned layouts at the bottom, Trinity/Prism none).
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
    if south_slot_available(skin) and south_slot_centered(skin):
        # The CENTERED info slot (Compass/Seasons, owner dual-Sunday
        # round 2026-07-12) rides ABOVE the hands like the center
        # body — "the center occludes the hands", his accepted cost.
        layers.append(BottomSlotLayer(skin))
    # LAST: the hover z-lift (owner 2026-07-13) — the enlarged element
    # repaints above everything, hands included.
    layers.append(HoverLiftLayer(skin))
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
            if element == "weekday_badge":
                # The badge in the weekday position (owner 2026-07-12):
                # sun sign, the rising sign, or the Chinese year.
                if self._skin.weekday_slot == "ascendant":
                    return self._ascendant_text(self._skin.day_slot_style)
                if self._skin.weekday_slot == "chinese":
                    return self._chinese_text(self._skin.day_slot_style)
                return self._zodiac_text(self._skin.day_slot_style)
            if element == "sun_servant":
                # The SERVANT face at 24h (owner 2026-07-13): its own
                # name, its own plate, its own text.
                return self._sun_face_tooltip(
                    "servant", active=today == "sun"
                )
            if element.startswith("body:"):
                # Weekday hover rework (owner spec): the ACTIVE body
                # leads with the date, ghosts show their article alone.
                body = element[len("body:"):]
                if body == "sun" and sunday_dual_face(self._skin):
                    # The north face on the Compass/Seasons speaks the
                    # RULER face alone (owner 2026-07-13) — the 24h
                    # face has its own hover.
                    return self._sun_face_tooltip(
                        "ruler", active=today == "sun"
                    )
                return self._weekday_tooltip(body, active=body == today)
            if element == "moon":
                return self._moon_text()
            if element == "earth":
                return self._earth_text()
            # The EFFECTIVE mode (Aurora shows images only — text modes
            # coerce to a logo, and the hover must describe what is
            # actually drawn).
            slot_mode, slot_style = south_slot_view(self._skin)
            if slot_mode == "chinese":
                return self._chinese_text(slot_style)
            if slot_mode == "zodiac":
                return self._zodiac_text(slot_style)
            if slot_mode == "ascendant":
                return self._ascendant_text(slot_style)
            if slot_mode == "weekday":
                # The info slot's SECOND weekday speaks its own theme.
                return self._weekday_tooltip(
                    today, active=True, theme=self._skin.info_slot_theme
                )
            # The time/date/day-length slot has no tooltip of its own —
            # fall through to the region hovers.

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
            badge = weekday_badge(self._skin, self._day, self._last_tick)
            if badge is not None:
                # The astrology badge occupies the weekday position —
                # its hit region mirrors the drawn spot exactly.
                weekday = self._skin.weekday_set
                if hit(
                    dial_point(
                        pinned_weekday_theta(self._skin),
                        radius * weekday.orbit_fraction,
                    ),
                    radius * weekday.diamond_scale,
                ):
                    return "weekday_badge"
            elif self._skin.weekday_slot == "weekday":
                # The text modes (time/date/day length in the DAY slot,
                # owner 2026-07-12) draw no bodies and answer no hover.
                body = self._weekday_body_at(point, radius, rotation, today)
                if body is not None:
                    return f"body:{body}"
                if servant_holds_the_seat(self._skin, today) and hit(
                    dial_point(
                        constants.SOUTH_SLOT_ANGLE + rotation,
                        radius * self._skin.weekday_set.orbit_fraction,
                    ),
                    radius * self._skin.weekday_set.diamond_scale,
                ):
                    # The SERVANT face at 24h — ghosted all week,
                    # opaque on Sunday (owner 2026-07-13).
                    return "sun_servant"
        weekday = self._skin.weekday_set
        if south_slot_available(self._skin) and hit(
            QPointF(0.0, 0.0)
            if south_slot_centered(self._skin)
            else dial_point(
                south_slot_theta(self._skin, rotation),
                radius * weekday.orbit_fraction,
            ),
            radius * weekday.diamond_scale * self._skin.octa_slot_scale,
        ):
            return "octa_slot"
        marker = self._skin.year_marker
        if self._skin.show_moon and hit(
            dial_point(
                angles.moon_cycle_angle(self._last_tick.moon_fraction),
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

        if weekday_pinned(self._skin):
            # Pinned layouts (Aurora, or the Pointer element off):
            # today's body alone at the bottom — the hit test mirrors
            # the drawn, un-rotated position.
            if hit(
                dial_point(
                    pinned_weekday_theta(self._skin),
                    radius * weekday.orbit_fraction,
                ),
                radius * weekday.diamond_scale,
            ):
                return today
            return None
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
        dual = servant_holds_the_seat(self._skin, today)
        for angle, occupants in constants.POINTER_WEEKDAY_SLOTS[self._skin.pointer]:
            if dual and angle == constants.SOUTH_SLOT_ANGLE:
                continue     # the Servant won the 24h seat today
            body = visible_occupant(occupants, today)
            slot = dial_point(
                angle + rotation, radius * weekday.orbit_fraction
            )
            if hit(slot, radius * weekday.diamond_scale):
                return body
        return None

    def _weekday_tooltip(
        self, body: str, active: bool, theme: str | None = None
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
        theme = theme or self._skin.weekday_theme
        article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
        if theme == self._skin.weekday_theme:
            display_name = self._skin.weekday_set.body_names[body]
            image = self._skin.weekday_set.bodies.get(body)
            metal = self._skin.weekday_set.metal
        elif theme == "planets":
            display_name = defaults.DEFAULT_SKIN.weekday_set.body_names[body]
            image = (
                defaults.WEEKDAY_ART_DIR / "planets" / "primary"
                / f"{body}.png"
            )
            metal = None
        else:
            # The info slot's SECOND weekday: resolve the art exactly
            # like its layer — the theme's OWN metal, colored/ included
            # (owner bug 2026-07-13: the legend always showed bronze).
            display_name = defaults.WEEKDAY_THEME_NAMES[theme][body]
            theme_dir = (
                defaults.WEEKDAY_ART_DIR / defaults.WEEKDAY_THEME_DIRS[theme]
            )
            slot_metal = self._skin.info_slot_metal
            if slot_metal == "colored" and theme in constants.METAL_THEMES:
                theme_dir = theme_dir.parent / "colored"
            image = (
                theme_dir
                / f"{defaults.WEEKDAY_THEME_FILES[theme][body]}.png"
            )
            metal = (
                slot_metal
                if theme in constants.METAL_THEMES
                and slot_metal in defaults.METAL_SWAP_TARGETS
                else None
            )
        image = metal_variant_file(image, metal)
        if body == "sun":
            # The dual center's TWO plates in one legend (owner
            # 2026-07-13: "u prism i trinity treba legend sa 2 slike").
            if theme == self._skin.weekday_theme:
                dual_image = self._skin.weekday_set.dual_asset
            else:
                dual_image = (
                    defaults.WEEKDAY_ART_DIR
                    / f"{defaults.WEEKDAY_DUAL_FILES[theme]}.png"
                )
            image = (image, metal_variant_file(dual_image, metal))
        node = self._symbolism.article(article_set, body)
        text = node["base"]
        variant = node["variants"].get(self._combo_key())
        if variant:
            text += "\n\n" + variant
        title = (
            f"<span style='font-size: {defaults.ARTICLE_TITLE_PX}px'>"
            f"<b>{html.escape(self._tr(display_name))}</b>"
            f"</span>"
        )
        if active:
            date = self._day.local_date
            title += (
                f"<br/>{html.escape(self._tr(constants.WEEKDAY_FULL_NAMES[body]))}, "
                f"{self._ord(date.day)} {html.escape(self._month(date))} {date.year}"
            )
        return _article_html(
            image, title, text,
            accents=defaults.BODY_ACCENT_HUES[body], tr=self._tr,
        )

    def _sun_face_tooltip(self, face: str, active: bool) -> str:
        """ONE face of the dual Sunday (owner 2026-07-13): on the
        Compass and the Seasons each face is its own person — its own
        name, its own plate, its own text (articles.<set>.sun.faces;
        the base article stands in until a theme's split lands). The
        Ruler face keeps the pointer/palette variant paragraph."""
        theme = self._skin.weekday_theme
        ruler = face == "ruler"
        display_name = defaults.WEEKDAY_DUAL_NAMES[theme][0 if ruler else 1]
        image = metal_variant_file(
            self._skin.weekday_set.bodies.get("sun")
            if ruler
            else self._skin.weekday_set.dual_asset,
            self._skin.weekday_set.metal,
        )
        node = self._symbolism.article(
            constants.WEEKDAY_THEME_ARTICLES[theme], "sun"
        )
        text = node.get("faces", {}).get(face) or node["base"]
        if ruler:
            variant = node["variants"].get(self._combo_key())
            if variant:
                text += "\n\n" + variant
        title = (
            f"<span style='font-size: {defaults.ARTICLE_TITLE_PX}px'>"
            f"<b>{html.escape(self._tr(display_name))}</b>"
            f"</span>"
        )
        if active:
            date = self._day.local_date
            title += (
                f"<br/>{html.escape(self._tr(constants.WEEKDAY_FULL_NAMES['sun']))}, "
                f"{self._ord(date.day)} {html.escape(self._month(date))} {date.year}"
            )
        return _article_html(
            image, title, text, accents=defaults.BODY_ACCENT_HUES["sun"],
            tr=self._tr,
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
            # Hover rework (owner 2026-07-13 round two): the two signs
            # stand LEFT/RIGHT as two columns — each with its bold
            # title (name + dates, NO glyph), its COLORED logo, then
            # ITS article (base + the active palette's paragraph).
            from render.layers import octa_slot_art

            style = self._skin.palette_style
            columns = []
            south = self._day.southern_hemisphere
            for offset in (-30.0, 0.0):      # the two signs' START angles
                start_angle = (arm_angle + offset) % 360.0
                if south:
                    # The mirrored year wheel (owner spec 2026-07-12):
                    # the diamond the Earth passes must name the signs
                    # it actually passes there — the opposite half.
                    start_angle = (start_angle + 180.0) % 360.0
                name, _symbol = constants.ZODIAC_SIGNS[int(start_angle) // 30]
                start, end = zodiac_span(self._day.year_anchors, start_angle)
                start = start.astimezone(self._day.tzinfo)
                last = end.astimezone(self._day.tzinfo) - timedelta(days=1)
                header = (
                    f"{html.escape(self._tr(name))} "
                    f"({self._ord(start.day)} {html.escape(self._month(start))} - "
                    f"{self._ord(last.day)} {html.escape(self._month(last))})"
                )
                if offset == -30.0 and star:
                    header += html.escape(star)
                colored = octa_slot_art(
                    constants.ZODIAC_STYLE_ART_DIRS["colored"], name
                )
                plate = ""
                if colored is not None and colored.exists():
                    small = scaled_variant_file(
                        colored, 2 * defaults.ARTICLE_IMAGE_WIDTH_PX
                    )
                    plate = (
                        f"<div align='center'><img src='{small.as_uri()}' "
                        f"width='{defaults.ARTICLE_IMAGE_WIDTH_PX}'/></div>"
                    )
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
                columns.append(
                    _hover_title(header)
                    + plate
                    + _article_paragraphs(text, accents=accents, tr=self._tr)
                )
            # ONE flat table, both columns width-declared (nested
            # tables measured wrong — the popup honors these cells).
            return (
                "<table cellspacing='12'><tr>"
                f"<td width='{defaults.ARTICLE_COLUMN_WIDTH_PX}'>"
                f"{columns[0]}</td>"
                f"<td width='{defaults.ARTICLE_COLUMN_WIDTH_PX}'>"
                f"{columns[1]}</td>"
                "</tr></table>"
            )
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
                f"<b>{html.escape(self._tr(theme))}</b>{html.escape(star)}",
                f"{start_hour:02d}:00 - {end_hour:02d}:00",
                html.escape(days),
            )
            article = self._symbolism.trio_article(theme)
            return (
                _hover_badge(defaults.TRINITY_ART_DIR / f"{theme}.png")
                + header + "<br/>"
                + _article_body_html(
                    article["base"],
                    accents=defaults.TRIO_ACCENT_HUES[theme],
                    tr=self._tr,
                )
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
            # First block (owner format 2026-07-13: image → title →
            # space → data; both equinoxes share the ONE balance
            # emblem): the turning point with its labeled day length.
            badge = (
                "Equinox" if "Equinox" in name else name.replace(" ", "_")
            )
            head = _hover_badge(
                defaults.SEASON_ART_DIR / "turning_point" / f"{badge}.png"
            ) + _hover_title(
                f"{html.escape(self._tr(name))}{html.escape(star)}"
            ) + _centered_html(
                "",
                f"{self._ord(instant.day)} {html.escape(self._month(instant))} "
                f"{instant.year} - {instant:%H:%M}",
                f"{self._label('Daylight')} {int(hours)}h {int(minutes)}min",
            )
            if self._skin.pointer != "cross":
                return head
            # Second block, split off by a RULE (owner 2026-07-13:
            # two data sets, a line between them): the meteorological
            # season — or the tropics' wet/dry half-year — wearing its
            # own badge.
            if self._day.zone == "tropics":
                # Tropics (owner decision): the cross arms describe
                # the equinox-bounded WET/DRY halves — the solstice
                # arms CENTER theirs, the equinox arms START theirs.
                span_start = 270.0 if anchor_angle in (270.0, 360.0) else 450.0
                is_wet, block = self._wet_dry_block(span_start)
                return head + "<hr/>" + _hover_badge(
                    defaults.SEASON_ART_DIR
                    / f"{'Wet' if is_wet else 'Dry'}_Season.png"
                ) + block
            season = self._season_name_for(anchor_angle)
            met_start, met_end = meteorological_span(
                self._day.year_anchors, anchor_angle
            )
            met_start = met_start.astimezone(self._day.tzinfo)
            met_end = met_end.astimezone(self._day.tzinfo)
            met_days = (met_end - met_start).total_seconds() / 86400
            return head + "<hr/>" + _hover_badge(
                defaults.SEASON_ART_DIR / "meteorological" / f"{season}.png"
            ) + _hover_title(
                html.escape(
                    self._tr("Meteorological {season}").format(
                        season=self._tr(season)
                    )
                )
            ) + _centered_html(
                "",
                f"<b>{self._tr('From')}</b> {self._ord(met_start.day)} "
                f"{self._month(met_start)} {met_start.year} - "
                f"{met_start:%H:%M}",
                f"<b>{self._tr('To')}</b> {self._ord(met_end.day)} "
                f"{self._month(met_end)} {met_end.year} - "
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
                f"<b>{html.escape(self._tr('Wet season' if is_wet else 'Dry season'))}</b> "
                f"{half}{html.escape(star)}"
            )
            _, whole = self._wet_dry_block(270.0 if starts_in_march else 450.0)
            return _hover_badge(
                defaults.SEASON_ART_DIR
                / f"{'Wet' if is_wet else 'Dry'}_Season.png"
            ) + _centered_html(
                season_line,
                self._span_line(start, end, days),
                f"{self._tr('Heart:')} {self._ord(middle.day)} "
                f"{self._month(middle)}",
            ) + "<hr/>" + whole
        season = self._season_name_for(start_angle)
        return _hover_badge(
            defaults.SEASON_ART_DIR / f"{season}.png"
        ) + _centered_html(
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
        start = self._anchor_instant(span_start_angle).astimezone(self._day.tzinfo)
        end = self._anchor_instant(span_start_angle + 180.0).astimezone(
            self._day.tzinfo
        )
        starts_in_march = span_start_angle % 360.0 == 270.0
        is_wet = starts_in_march != self._day.southern_hemisphere
        days = (end - start).total_seconds() / 86400
        return is_wet, _hover_title(
            html.escape(self._tr("Wet season" if is_wet else "Dry season"))
        ) + _centered_html(
            "",
            f"<b>{self._tr('From')}</b> {self._ord(start.day)} "
            f"{self._month(start)} {start.year}",
            f"<b>{self._tr('To')}</b> {self._ord(end.day)} "
            f"{self._month(end)} {end.year}",
            f"{self._label('Duration')} {days:.1f} "
            f"{html.escape(self._tr('Days'))}",
        )

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

    def _chinese_text(self, style: str | None = None) -> str:
        """Chinese slot hover (owner rework): the year name and span,
        then the animal's ARTICLE with the owner's medallion on top —
        in the ACTIVE style's look (owner bug 2026-07-13: the legend
        always showed the bronze plate): colored takes its own art,
        gold/silver ride the selective swap."""
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
        folder = constants.CHINESE_STYLE_ART_DIRS.get(style, "chinese/primary")
        image = metal_variant_file(
            octa_slot_art(folder, animal),
            style if style in defaults.METAL_SWAP_TARGETS else None,
        )
        return header + "<br/>" + _article_html(
            image, None, text, tr=self._tr,
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

    def _zodiac_image_trio(self, style: str | None, sign: str) -> str:
        """The Astrology hover's image row (owner 2026-07-13): the
        ACTIVE style's art LARGE in the middle — filling the image
        band — and the two remaining styles small at its sides (text
        mode leads with the colored logo)."""
        from render.layers import octa_slot_art

        dirs = constants.ZODIAC_STYLE_ART_DIRS
        main_style = style if style in dirs else "colored"
        sides = {
            "logo": ("sign", "constellation"),
            "colored": ("sign", "constellation"),
            "sign": ("logo", "constellation"),
            "constellation": ("sign", "logo"),
        }[main_style]
        side_px = round(
            defaults.ASTRO_MAIN_IMAGE_PX * defaults.ASTRO_SIDE_IMAGE_FRACTION
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
            + img(dirs[main_style], defaults.ASTRO_MAIN_IMAGE_PX)
            + img(dirs[sides[1]], side_px)
            + "</div>"
        )

    def _zodiac_text(self, style: str | None = None) -> str:
        """Zodiac slot hover (owner rework, formatting 2026-07-13):
        the sign name as the bold title with its span beneath, the
        image TRIO led by the active style, then the sign's ARTICLE
        (base only — the palette variants speak in hexa arm colors)."""
        day = self._day
        last = day.zodiac_end - timedelta(days=1)
        header = _hover_title(html.escape(self._tr(day.zodiac_name))) + _centered(
            f"{day.zodiac_start.day} {self._month_short(day.zodiac_start)} – "
            f"{last.day} {self._month_short(last)}",
        )
        article = self._symbolism.zodiac_article(day.zodiac_name)
        return (
            header
            + self._zodiac_image_trio(style, day.zodiac_name)
            + _article_body_html(
                article["base"],
                accents=defaults.SIGN_ACCENT_HUES[day.zodiac_name],
                tr=self._tr,
            )
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
        day = self._day
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
        sun = self._day.sun

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
        return self._tr("Day" if self._day.day_length == "24:00" else "Night")

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
        if not (
            radius * defaults.TICK_HOVER_INNER_FRACTION
            <= distance
            <= radius * defaults.TICK_HOVER_OUTER_FRACTION
        ):
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        minutes = round((((theta - 180.0) % 360.0) / 15.0) * 60) % (24 * 60)
        line_time = (
            f"{self._label('Time')} {minutes // 60:02d}:{minutes % 60:02d} - "
            f"{self._label('Angle')} {theta:.1f}° - "
            + html.escape(self._period_word(minutes))
        )

        day = self._day
        instant = instant_at_marker_angle(
            day.year_anchors, theta, day.southern_hemisphere
        )
        local = instant.astimezone(day.tzinfo)
        line_date = (
            f"{self._label('Date')} {self._ord(local.day)} "
            f"{html.escape(self._month(local))} {local.year}"
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
        next_cycle = self._last_tick.moon_fraction > 0.5 and fraction < 0.5
        cycle_day = f"{fraction * constants.SYNODIC_MONTH_DAYS:.1f}"
        line_moon = (
            f"{self._label('Illumination')} "
            f"{illumination(fraction) * 100:.1f}% - "
            f"{html.escape(self._tr(phase_name(fraction)))} - "
            + html.escape(
                self._tr("Day {day} of {total}").format(
                    day=cycle_day, total=constants.SYNODIC_MONTH_DAYS
                )
            )
        )
        return _centered_html(
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

    def _ascendant_text(self, style: str | None = None) -> str:
        """The Ascendant hover (owner request 2026-07-12, formatting
        2026-07-13): "Ascendant" as the bold title, the rising sign
        beneath it, the image TRIO led by the active style, then the
        sign's article."""
        sign = self._last_tick.ascendant_sign
        symbol = dict(constants.ZODIAC_SIGNS)[sign]
        header = _hover_title(
            html.escape(self._tr("Ascendant"))
        ) + _centered(f"{symbol} {self._tr(sign)}")
        article = self._symbolism.zodiac_article(sign)
        return (
            header
            + self._zodiac_image_trio(style, sign)
            + _article_body_html(
                article["base"], accents=defaults.SIGN_ACCENT_HUES[sign],
                tr=self._tr,
            )
        )

    def _moon_text(self) -> str:
        """Moon hover (owner formatting rounds 2026-07-12/13): the
        PHASE NAME is the title — bigger, bold, no label — with the
        principal-phase instant beneath it, then the labeled data."""
        day = self._day
        tick = self._last_tick
        name = phase_name(tick.moon_fraction)
        title = _hover_title(html.escape(self._tr(name)))
        if name in constants.MOON_PHASE_FRACTIONS:
            # A principal phase name holds ±12 h around its instant —
            # show that instant (the nearest principal event by name),
            # dated like the weekday tooltip (owner 2026-07-14:
            # "14th July", not "14 Jul").
            noon = datetime.combine(day.local_date, time(12, 0), day.tzinfo)
            instant = min(
                (event for event in day.moon_events if event[1] == name),
                key=lambda event: abs(event[0] - noon),
            )[0].astimezone(day.tzinfo)
            title += _centered(
                f"{self._ord(instant.day)} {self._month(instant)}"
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
        cycle_day = tick.moon_fraction * constants.SYNODIC_MONTH_DAYS
        return title + _centered_html(
            "",
            *lines,
            "",
            html.escape(
                self._tr("Day {day} of {total}").format(
                    day=f"{cycle_day:.1f}",
                    total=constants.SYNODIC_MONTH_DAYS,
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

    def _label(self, text: str) -> str:
        """A BOLD hover label with its colon (owner formatting round
        2026-07-12: labels bold, values plain)."""
        return f"<b>{html.escape(self._tr(text))}:</b>"

    def _earth_text(self) -> str:
        """Earth hover (owner formatting round 2026-07-12): a bold
        Date label with the day/week ordinals beneath, a blank line,
        then bold Season and Sign labels — plus the season event on
        top while the marker glows."""
        day, date = self._day, self._day.local_date
        last = day.zodiac_end - timedelta(days=1)
        lines = [
            f"{self._label('Date')} {self._ord(date.day)} "
            f"{html.escape(self._month(date))} {date.year}",
            self._tr("{ordinal} Day - {ordinal_week} Week").format(
                ordinal=self._ord(date.timetuple().tm_yday),
                ordinal_week=self._ord(date.isocalendar().week),
            ),
            "",
            f"{self._label('Season')} {self._season_row()}",
            f"{self._label('Sign')} {html.escape(day.zodiac_symbol)} "
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

    def _period_earth_html(self, kind: str) -> str:
        """The active region's own Earth face rides the Day/Night hover
        (owner 2026-07-12): the day art on the Day side, the night art
        on the Night side — atmosphere or clean per the Earth setting."""
        marker = self._skin.year_marker
        path = marker.variants.get(
            f"{self._skin.earth_style}_{marker.default_variant}_{kind}"
        )
        if path is None:
            return ""
        small = scaled_variant_file(
            path, 2 * defaults.PERIOD_EARTH_IMAGE_PX
        )
        return (
            f"<div align='center'><img src='{small.as_uri()}' "
            f"width='{defaults.PERIOD_EARTH_IMAGE_PX}'/></div>"
        )

    def _period_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Aura/Umbra hovers (owner formatting round 2026-07-12): a mini
        Earth of the active region on top, then a bold Day/Night title
        with the duration, the labeled sun span, a blank line, and the
        twilight-extended span under its own With Twilight / Complete
        Dark title. Polar days/nights cover the whole wheel."""
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
            return self._period_earth_html("day") + _centered_html(*lines)
        if distance > radius * self._skin.background.umbra_radius_fraction:
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
        return self._period_earth_html("night") + _centered_html(*lines)

    def _twilight_tooltip(self, point: QPointF, radius: float) -> str | None:
        """Hovering a twilight band (owner formatting round 2026-07-12):
        a bold Morning/Evening Twilight title, the labeled boundary
        times in the order the light moves, and the band's span in
        minutes AND dial degrees (15° per hour)."""
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

        def band(title: str, a: str, first: datetime,
                 b: str, second: datetime) -> str:
            span = round((second - first).total_seconds() / 60)
            return _centered_html(
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
