"""Z-ordered layer stack with cadence-driven caching.

STATIC and DAILY layers are composited into ONE cached pixmap at device
resolution, rebuilt only when the day context, size or DPI changes; the
per-minute paint blits that cache and draws the MINUTE layers (hands,
year marker) live. The same paint path renders offscreen for tests and
the future settings preview.
"""

import html
import json
import math
import re
from datetime import datetime, time, timedelta
from functools import lru_cache
from time import monotonic

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap, QPolygonF

from config import archetypes, constants, defaults, paths, profiling
from config.ui_text import ui
from data.symbolism import SymbolismRepository
from core import angles
from core.clock_state import DayContext, TickState
from core.deep_time import format_year_line, real_year
from core.moon import nominal_illumination, phase_name
from core.year_wheel import (
    instant_at_marker_angle,
    meteorological_span,
    zodiac_span,
)
from render.assets import AssetCache, metal_variant_file, scaled_variant_file
from render.layers import (
    ArchetypeCenterLayer,
    ArchetypeLayer,
    BackgroundLayer,
    Cadence,
    CenterBodyLayer,
    HandLayer,
    Layer,
    RenderContext,
    RingLayer,
    SlotLayer,
    StarLayer,
    WeekdayLayer,
    YearMarkerLayer,
    HoverLiftLayer,
    archetype_active,
    archetype_art_ready,
    archetype_figure_size,
    archetype_key,
    archetype_lit_index,
    dial_point,
    earth_region,
    palette_for,
    servant_holds_the_seat,
    slot_layout,
    slot_seat_orbit,
    slot_seat_rotation,
    slot_seat_scale,
    slot_view,
    sunday_dual_face,
    weekday_body_orbit,
    weekday_body_size,
    today_slot_theta,
    visible_occupant,
    weekday_classic_slot,
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


@lru_cache(maxsize=1)
def _greetings() -> dict:
    """The owner's Four Greetings (Database/verses.json) — Serbian in
    every language, shown only in the unlocked hidden mode."""
    return json.loads(
        (paths.database_dir() / "verses.json").read_text(encoding="utf-8")
    )["trinity"]


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
        if img is not None and paths.art_file(img).exists()
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
    if path is None or not paths.art_file(path).exists():
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
    # LAST: the hover z-lift (owner 2026-07-13) — the enlarged element
    # repaints above everything, hands included.
    layers.append(HoverLiftLayer(skin))
    return layers


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
_ENC_TRIO_ORDER = ("Faith", "Hope", "Love")

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
        self._symbolism = symbolism or SymbolismRepository()
        self._overlay = overlay or {}
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
        # unlocked, the 12h ring letter opens the Four Greetings legend.
        self._hidden_unlocked = False
        # Reveal-week (owner 2026-07-16): an Omega double-click raises
        # every non-active weekday body to full opacity until this
        # monotonic deadline; None = no reveal running.
        self._reveal_until: float | None = None

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

    def set_hidden_unlocked(self, unlocked: bool) -> None:
        self._hidden_unlocked = unlocked

    def hit_omega(self, x: float, y: float, size: float) -> bool:
        """True when (x, y) — widget-local, same coordinates as
        `set_hover`/`tooltip_at` — lands on the Omega (24h) ring seat:
        the FULL ROUND AREA (owner slika 9, 2026-07-17), a circle CENTERED
        on the Omega letter position (180°, the ring letter band) whose
        radius covers the whole letter cell. The old narrow annular wedge
        only answered on the letter glyph itself (practically its lower
        part), so the double-click kept missing; the round area lands
        anywhere on the seat. The toggle semantics are untouched."""
        radius = size / 2
        point = QPointF(x - radius, y - radius)
        center = dial_point(180.0, radius * defaults.RING_LETTER_RADIUS_FRACTION)
        hit_radius = radius * defaults.OMEGA_HIT_RADIUS_FRACTION
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

    def _year(self, when) -> str:
        """A hover date's YEAR through the ONE pairing formatter
        (Session 16, owner amendment 2026-07-17): the official year
        with the Anno Lucis year always beside it — "2026 · 6105. Anno
        Lucis" — plus the optional third calendar; the real
        astronomical year un-shifts the deep proxy frame first. Every
        hover that prints a year prints it via this."""
        return format_year_line(
            real_year(when.year, self._day.deep_cycles),
            self._skin.era_notation,
            self._skin.show_era_suffix,
            self._skin.third_era,
        )

    def set_day(self, day: DayContext) -> None:
        self._day = day
        self._composites = [None] * len(self._cached_groups)

    def invalidate(self) -> None:
        """Size/DPI/screen change: drop the composites and rasterized assets."""
        self._composites = [None] * len(self._cached_groups)
        self._cache.flush()

    def _rotation(self) -> float:
        """Star/Aura/Umbra/slot rotation: solar offset, or 0 upright."""
        return self._day.star_rotation if self._skin.solar_rotation else 0.0

    @profiling.timed("Paint frame")
    def paint(self, painter: QPainter, size: float, dpr: float, tick: TickState) -> None:
        if self._day is None:
            raise RuntimeError("Compositor.paint() before the first day context")
        self._last_tick = tick
        reveal = self.reveal_active()
        # The Calendar's lit wedge (the shichen under the hour hand)
        # changes INTRADAY, so it keys the cached segments too — the
        # wedges live below the ring (BackgroundLayer, cached), and this
        # keeps them relighting ~12 times a day instead of once (owner
        # spec).
        calendar_lit = self._calendar_lit(tick)
        # The archetype hour-space (owner 2026-07-16) turns with the
        # hour hand the same way — but the archetype figures paint LIVE
        # now (ROADMAP 15f), so the lit index no longer keys any cache.
        archetype_lit = self._archetype_lit(tick)
        # The cached segments depend ONLY on size/DPI, the day and the
        # Calendar's lit wedge — NEITHER hover NOR reveal (those live in
        # the hover-variable layers painted live below). This is the
        # whole point of the 15f split: a hover enter/leave rebuilds
        # NOTHING (the count of "Composite rebuild" stays flat).
        key = (round(size * dpr), self._day.cache_key, calendar_lit)
        if self._composite_key != key:
            self._composites = [None] * len(self._cached_groups)
            self._composite_key = key
        # The cached segments carry the window's transparent margin (the
        # ring letters and event glow overhang the dial square) — each is
        # blit back-shifted so the dial lands at (0, 0). The margin is
        # LIVE from the user's settings (owner 2026-07-17), matching the
        # widget's own window sizing.
        overhang = size * defaults.dial_window_margin_fraction(self._skin)
        ctx = RenderContext(
            skin=self._skin, day=self._day, tick=tick,
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self._rotation(), hovered=self._hovered,
            reveal_active=reveal, calendar_lit=calendar_lit,
            archetype_lit=archetype_lit,
        )
        for kind, payload in self._steps:
            if kind == "cache":
                pixmap = self._composites[payload]
                if pixmap is None:
                    with profiling.measure("Composite rebuild"):
                        pixmap = self._render_group(
                            self._cached_groups[payload], size, dpr,
                            calendar_lit,
                        )
                    self._composites[payload] = pixmap
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
            layer.paint(painter, ctx)
            painter.restore()

    @profiling.timed("Hover text")
    def tooltip_at(self, x: float, y: float, size: float) -> str | None:
        """Hover text under the cursor, at every dial size (owner spec):
        today's body, the Earth marker (day/week ordinals, zodiac sign
        with its dates, the date — plus the season event while it glows),
        the Moon marker (phase + illumination, day in the cycle), the
        octa zodiac slot and the twilight bands. The timed shell over
        `_tooltip_at` — the background warm sweep calls the impl
        directly so the owner's Hover text profile keeps measuring
        REAL hovers only."""
        return self._tooltip_at(x, y, size)

    def _tooltip_at(self, x: float, y: float, size: float) -> str | None:
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
            if element.startswith("slot:"):
                # A SEATED slot (owner matrix 2026-07-14) speaks its
                # own content: the sign, the rising sign, the Chinese
                # year, or its theme's weekday article. The digital
                # modes (time/date/day length/seconds) have no reading
                # of their own — the hover-ENLARGE still works, the
                # region hovers take over below.
                mode, style, theme, metal, roster = slot_view(
                    self._skin, int(element[len("slot:"):])
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
                # The classic unit may be DRIVEN by the 2nd slot
                # (owner 2026-07-15) — the hover speaks that theme,
                # in that slot's OWN roster and metal.
                if weekday_classic_slot(self._skin) == 2:
                    return self._weekday_tooltip(
                        body, active=body == today,
                        theme=self._skin.info_slot_theme,
                        slot_metal=self._skin.info_slot_metal,
                        roster=self._skin.info_slot_roster,
                    )
                return self._weekday_tooltip(body, active=body == today)
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
        # pre-empts the day/night period hover below.
        if self._skin.pointer == "calendar":
            calendar = self._calendar_tooltip(point, radius)
            if calendar is not None:
                return calendar
        # Last in the chain (owner rework 5 & 6): the sunlit arc answers
        # with the day, the dark of the wheel with the night.
        return self._period_tooltip(point, radius)

    @profiling.timed("Hover warmup")
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

        if self._day is None or self._last_tick is None:
            return 0
        spoken = 0
        radius = size / 2
        rings = defaults.HOVER_WARM_RADIAL_STEPS
        angles = defaults.HOVER_WARM_ANGLE_STEPS
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
            sleep(defaults.HOVER_WARM_RING_PAUSE_S)
        return spoken

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
        if self._day is None or self._last_tick is None:
            return None
        radius = size / 2
        point = QPointF(x - radius, y - radius)
        rotation = self._rotation()
        today = constants.WEEKDAY_BODIES[self._day.weekday_index]
        element = self._element_at(point, radius, rotation, today)
        if element is not None:
            return self._element_encyclopedia_target(element, today)
        arm = self._arm_encyclopedia_target(point, radius, rotation)
        if arm is not None:
            return arm
        if self._skin.pointer == "calendar":
            return self._calendar_wedge_target(point, radius)
        return None

    def _weekday_encyclopedia_target(
        self, body: str, theme: str
    ) -> tuple[str, int] | None:
        """(theme topic, body page index) for a weekday body dressed in
        `theme` — the classic unit's theme OR a seated slot's own theme.
        None when the theme carries no encyclopedia topic."""
        if body in _ENC_WEEK_ORDER and theme in defaults.WEEKDAY_THEME_TITLES:
            return theme, _ENC_WEEK_ORDER.index(body)
        return None

    def _element_encyclopedia_target(
        self, element: str, today: str
    ) -> tuple[str, int] | None:
        """The page for one enlargeable element (`_element_at` output).
        Seated weekday slots and the pinned classic bodies resolve the
        slot's OWN theme/roster; the Moon opens at its current phase, the
        Earth at its current season."""
        if element == "moon":
            return "moon", constants.MOON_PHASE_NAMES.index(
                phase_name(self._last_tick.moon_fraction)
            )
        if element == "earth":
            return "seasons", self._season_topic_index()
        if element == "archetype:center":
            return None      # the centers have no pages yet (Session 6/8)
        if element.startswith("archetype:"):
            # An archetype ARM figure (owner slika 8): its OWN target —
            # today only the Walks map onto the Professions pages; the
            # rest answer None gracefully (Sessions 6/8 add topics).
            index = int(element[len("archetype:"):])
            return archetypes.figures(archetype_key(self._skin))[index]["enc"]
        if element.startswith("slot:"):
            mode, _style, theme, _metal, _roster = slot_view(
                self._skin, int(element[len("slot:"):])
            )
            if mode == "zodiac":
                return (
                    "astrology",
                    _ENC_ZODIAC_ORDER.index(self._day.zodiac_name),
                )
            if mode == "ascendant":
                return (
                    "astrology",
                    _ENC_ZODIAC_ORDER.index(self._last_tick.ascendant_sign),
                )
            if mode == "chinese":
                animal = self._day.chinese_name.split()[1]
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
                self._skin.info_slot_theme
                if weekday_classic_slot(self._skin) == 2
                else self._skin.weekday_theme
            )
            return self._weekday_encyclopedia_target(body, theme)
        return None

    def _current_season_key(self) -> str:
        """The Encyclopedia SEASONS key for the current date — a
        temperate season ("Spring".."Winter") or a tropical half
        ("Wet_Season"/"Dry_Season"). Mirrors `_season_row`."""
        day = self._day
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

    def _arm_angle_at(
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
        star_tip = radius * self._skin.star.radius_fraction
        if not (radius * 0.08 <= distance <= star_tip):
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        arms = constants.POINTER_POINTS[self._skin.pointer]
        arm_step = 360.0 / arms
        arm_angle = (
            round(((theta - rotation) % 360.0) / arm_step) * arm_step
        ) % 360.0
        half = constants.POINTER_ARM_HALF_ANGLE_DEG[self._skin.pointer]
        inner = star_tip / (2.0 * math.cos(math.radians(half)))
        drawn = arm_angle + rotation
        diamond = QPolygonF([
            QPointF(0.0, 0.0),
            dial_point(drawn - half, inner),
            dial_point(drawn, star_tip),
            dial_point(drawn + half, inner),
        ])
        if not diamond.containsPoint(point, Qt.FillRule.OddEvenFill):
            return None
        return arm_angle

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
        arm_angle = self._arm_angle_at(point, radius, rotation)
        if arm_angle is None:
            return None
        pointer = self._skin.pointer
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        if pointer == "hexa":
            # The cursor's half of the 60° arc picks which of the two signs.
            rel = ((theta - rotation - arm_angle + 180.0) % 360.0) - 180.0
            start_angle = (arm_angle + (-30.0 if rel < 0.0 else 0.0)) % 360.0
            if self._day.southern_hemisphere:
                start_angle = (start_angle + 180.0) % 360.0
            return (
                "astrology",
                _ENC_ZODIAC_ORDER.index(
                    constants.ZODIAC_SIGNS[int(start_angle) // 30][0]
                ),
            )
        if pointer == "trio":
            theme = constants.TRIO_ARM_THEMES[arm_angle]
            return "trinity", _ENC_TRIO_ORDER.index(theme)
        if arm_angle % 90.0 == 0.0:
            # Cardinal arms (cross and octa) point at the turning points.
            anchor_angle = {
                0.0: 360.0, 90.0: 450.0, 180.0: 540.0, 270.0: 270.0
            }[arm_angle]
            if self._day.southern_hemisphere:
                anchor_angle = _SOUTH_ANCHOR_FLIP[anchor_angle]
            index = self._day.year_anchors.angles.index(anchor_angle)
            return "sun", self._sun_topic_index(
                self._day.season_events[index][1]
            )
        # Octa diagonal arms point at the QUARTER centers — the seasons.
        start_angle = {
            315.0: 270.0, 45.0: 360.0, 135.0: 450.0, 225.0: 540.0
        }[arm_angle]
        if self._day.southern_hemisphere:
            start_angle = _SOUTH_ANCHOR_FLIP[start_angle]
        if self._day.zone == "tropics":
            starts_in_march = start_angle in (270.0, 360.0)
            is_wet = starts_in_march != self._day.southern_hemisphere
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
        from render.layers import calendar_wheel

        distance = math.hypot(point.x(), point.y())
        outer = radius * self._skin.background.aura_radius_fraction
        if not (radius * 0.08 <= distance <= outer):
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        step = constants.CALENDAR_WEDGE_DEG
        if calendar_wheel(self._skin) == "almanac":
            index = int((theta + step / 2.0) // step) % 12
            return "chinese", (index - 6) % 12
        start_angle = int(theta // step) * step
        if self._day.southern_hemisphere:
            start_angle = (start_angle + 180.0) % 360.0
        name = constants.ZODIAC_SIGNS[int(start_angle) // 30][0]
        return "astrology", _ENC_ZODIAC_ORDER.index(name)

    @profiling.timed("Hit test")
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

        weekday = self._skin.weekday_set
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
                    radius * weekday.orbit_fraction
                    * slot_seat_orbit(self._skin, seat),
                )
            )
            if hit(
                pos,
                radius * weekday.diamond_scale
                * slot_seat_scale(self._skin),
            ):
                return f"slot:{index}"
        if classic is not None:
            body = self._weekday_body_at(point, radius, rotation, today)
            if body is not None:
                return f"body:{body}"
            if servant_holds_the_seat(self._skin, today) and hit(
                dial_point(
                    constants.SOUTH_SLOT_ANGLE + rotation,
                    radius * weekday_body_orbit(self._skin),
                ),
                radius * weekday.diamond_scale * slot_seat_scale(self._skin),
            ):
                # The SERVANT face at 24h — ghosted all week,
                # opaque on Sunday (owner 2026-07-13).
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
                archetype_figure_size(self._skin, radius, center["file"]) / 2.0,
            ):
                return "archetype:center"
        marker = self._skin.year_marker
        # THE MARKERS OUTRANK THE RING (owner Session 21-C bug, slika
        # 3): during a GLOW window `YearMarkerLayer` RELOCATES the Moon/
        # Earth marker radially to the ring band centerline
        # (`GLOW_RING_RADIUS_FRACTION`, same as the drawn glow) — this
        # hit-test used to check only the marker's NORMAL orbit
        # position, so a relocated marker missed its own hit circle and
        # fell through to the ring TICK band underneath it. Mirroring
        # the SAME relocation `YearMarkerLayer.paint` applies fixes it:
        # hit-test the DRAWN position, whichever radius that is.
        eclipse = self._last_tick.eclipse_event
        moon_orbit = (
            defaults.GLOW_RING_RADIUS_FRACTION
            if self._last_tick.moon_event is not None
            or (eclipse is not None and eclipse.kind == "lunar")
            else marker.moon_orbit_fraction
        )
        if self._skin.show_moon and hit(
            dial_point(
                angles.moon_cycle_angle(self._last_tick.moon_fraction),
                radius * moon_orbit,
            ),
            radius * marker.moon_scale,
        ):
            return "moon"
        earth_orbit = (
            defaults.GLOW_RING_RADIUS_FRACTION
            if self._last_tick.season_event is not None
            or (eclipse is not None and eclipse.kind == "solar")
            else marker.orbit_fraction
        )
        if self._skin.show_earth and hit(
            dial_point(self._last_tick.year_angle, radius * earth_orbit),
            radius * marker.scale,
        ):
            return "earth"
        if archetype_active(self._skin):
            # The archetype ARM figures inherit the slot hover-enlarge
            # (owner slika 8): the whole diamond is the target, the same
            # geometry the arm tooltip uses — checked AFTER the markers so
            # the Earth/Moon (the instrument) keep priority where they
            # overlap an arm.
            arm_angle = self._arm_angle_at(point, radius, rotation)
            if arm_angle is not None:
                return f"archetype:{self._archetype_arm_index(arm_angle)}"
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
        # No composite drop (owner 2026-07-17, ROADMAP 15f): the weekday
        # bodies and archetype figures paint LIVE now, so the enlarge is
        # a handful of cached blits on the next frame — ZERO composite
        # rebuilds per hover enter/leave.
        return True

    def _combo_key(self) -> str:
        """The (pointer, palette) combination the WEEKDAY articles vary
        by — "hexa_paint", "octa_light", "cross", "trio". The trio
        still collapses although it gained the Family LIGHT wheel
        (2026-07-16): the shipped article variants carry one "trio"
        paragraph, and the archetype articles vary by their own grid
        sets instead — a trio_light variant wave is Session 6's call."""
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
            QPointF(0, 0),
            # The hit disc mirrors the DRAWN size (owner 2026-07-18):
            # hexa/trio centers match the diamond bodies; the
            # center-only showcase keeps center_scale — WITHOUT the
            # seat factor this path used to add (the disc overhung the
            # image by 1.5×).
            radius * weekday.center_scale
            if weekday.display_mode == "center_only"
            else weekday_body_size(self._skin, radius) / 2,
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
                angle + rotation, radius * weekday_body_orbit(self._skin)
            )
            if hit(
                slot,
                radius * weekday.diamond_scale * slot_seat_scale(self._skin),
            ):
                return body
        return None

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
        theme = theme or self._skin.weekday_theme
        article_set = constants.WEEKDAY_THEME_ARTICLES[theme]
        article_body = body
        # The weekday-set shortcut holds only while the ROSTER matches
        # too (owner 2026-07-15: slot 1 Greek Planetary beside slot 2
        # Greek Pantheon — same theme, two casts); a caller that names
        # no roster follows the set as dressed.
        same_unit = theme == self._skin.weekday_theme and roster in (
            None,
            "pantheon"
            if self._skin.weekday_set.body_articles is not None
            else "planetary",
        )
        if same_unit and self._skin.weekday_set.body_articles is not None:
            # The PANTHEON roster (owner 2026-07-15): each seat's
            # article follows the FIGURE actually shown there —
            # fallen-back seats keep the planetary text.
            article_set, article_body = (
                self._skin.weekday_set.body_articles[body]
            )
        if same_unit:
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
                defaults.pantheon_seat(theme, body)
                if roster == "pantheon" else None
            )
            if seat is not None:
                image, display_name, (article_set, article_body) = seat
            else:
                display_name = defaults.WEEKDAY_THEME_NAMES[theme][body]
                theme_dir = (
                    defaults.WEEKDAY_ART_DIR
                    / defaults.WEEKDAY_THEME_DIRS[theme]
                )
                if (
                    slot_metal == "colored"
                    and theme in constants.METAL_THEMES
                ):
                    theme_dir = theme_dir.parent / "colored"
                image = (
                    theme_dir
                    / f"{defaults.WEEKDAY_THEME_FILES[theme][body]}.png"
                )
        image = metal_variant_file(image, metal)
        if body == "sun":
            # The dual center's TWO plates in one legend (owner
            # 2026-07-13: "u prism i trinity treba legend sa 2 slike").
            if same_unit:
                dual_image = self._skin.weekday_set.dual_asset
            else:
                dual_rel = defaults.WEEKDAY_DUAL_FILES[theme]
                if roster == "pantheon" and theme in defaults.WEEKDAY_PANTHEON:
                    # The pantheon dual wins only when its plate is on
                    # disk — otherwise the WHOLE planetary pair stays
                    # (the classic unit's Sunday law).
                    candidate = defaults.WEEKDAY_PANTHEON[theme]["dual"][0]
                    if paths.art_file(
                        defaults.WEEKDAY_ART_DIR / f"{candidate}.png"
                    ).exists():
                        dual_rel = candidate
                dual_image = (
                    defaults.WEEKDAY_ART_DIR / f"{dual_rel}.png"
                )
            image = (image, metal_variant_file(dual_image, metal))
        node = self._symbolism.article(article_set, article_body)
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
                f"{self._ord(date.day)} {html.escape(self._month(date))} "
                f"{self._year(date)}"
            )
        return _article_html(
            image, title, text,
            accents=defaults.BODY_ACCENT_HUES[body], tr=self._tr,
        )

    def _archetype_arm_index(self, arm_angle: float) -> int:
        """The figures-tuple index of an unrotated arm angle — the same
        k·(360/N) order archetype_lit_index counts in (Rule #5: one
        ordering shared by lighting, hovers and the Spacebar jump)."""
        arms = constants.POINTER_POINTS[self._skin.pointer]
        return int(round(arm_angle / (360.0 / arms))) % arms

    def _archetype_arm_tooltip(self, index: int) -> str:
        """One arm figure's archetype legend (owner 2026-07-16): the
        TWO-ROW article per the two-row canon — person+calling, member+
        hearth-role, temperament+age, person+quality, pillar+shadow,
        estate+object. EXCEPT the two THREE-SIDE layouts (owner
        2026-07-17): the Ages (compass light) show the age's text and BOTH
        life registers (the Tree + the Menagerie); the Tetramorph (seasons
        light) show the creature + the evangelist + the element."""
        key = archetype_key(self._skin)
        if key == "compass_light":
            return self._archetype_three_side(index)
        if key == "seasons_light":
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
        key = "compass_light"
        registers = archetypes.ARCHETYPES[key]["registers"]
        tree_fig = registers["tree"][index]
        animals_fig = registers["animals"][index]
        set_name = archetypes.ARCHETYPES[key]["articles"]
        node = self._symbolism.archetype_article(set_name, tree_fig["entity"])
        rows = (node or {}).get("rows") or ()
        # Column 1 — the age name and its text (or the pending line).
        text_col = _hover_title(html.escape(self._tr(tree_fig["name"])))
        if rows:
            text_col += _article_paragraphs(rows[0], tr=self._tr)
        else:
            text_col += _centered_html(
                "",
                html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE)),
            )

        def register_column(caption: str, fig: dict) -> str:
            image = ""
            if archetype_art_ready(fig["file"]):
                small = scaled_variant_file(
                    fig["file"], 2 * defaults.ARTICLE_THREE_IMAGE_PX
                )
                image = (
                    f"<div align='center'><img src='{small.as_uri()}' "
                    f"width='{defaults.ARTICLE_THREE_IMAGE_PX}'/></div>"
                )
            return (
                _hover_title(html.escape(self._tr(caption)))
                + image
                + _centered_html(f"<b>{html.escape(self._tr(fig['row2']))}</b>")
            )

        width = defaults.ARTICLE_THREE_COLUMN_WIDTH_PX
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
        key = "seasons_light"
        fig = archetypes.figures(key)[index]
        set_name = archetypes.ARCHETYPES[key]["articles"]
        node = self._symbolism.archetype_article(set_name, fig["entity"])
        rows = (node or {}).get("rows") or ()
        # Column 1 — the creature (glass + name + text).
        creature_col = _hover_title(html.escape(self._tr(fig["name"])))
        if archetype_art_ready(fig["file"]):
            small = scaled_variant_file(
                fig["file"], 2 * defaults.ARTICLE_THREE_IMAGE_PX
            )
            creature_col += (
                f"<div align='center'><img src='{small.as_uri()}' "
                f"width='{defaults.ARTICLE_THREE_IMAGE_PX}'/></div>"
            )
        if rows:
            creature_col += _article_paragraphs(rows[0], tr=self._tr)
        else:
            creature_col += _centered_html(
                "", html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE))
            )
        # Column 2 — the Evangelist: his rondel (real art only), his name
        # (the figure's row-2), then his article (rows[1] when written).
        evangelist_col = _hover_title(html.escape(self._tr("The Evangelist")))
        ev_file = archetypes.tetramorph_evangelist_file(index)
        if archetype_art_ready(ev_file):
            small = scaled_variant_file(
                ev_file, 2 * defaults.ARTICLE_THREE_IMAGE_PX
            )
            evangelist_col += (
                f"<div align='center'><img src='{small.as_uri()}' "
                f"width='{defaults.ARTICLE_THREE_IMAGE_PX}'/></div>"
            )
        evangelist_col += _centered_html(
            f"<b>{html.escape(self._tr(fig['row2']))}</b>"
        )
        if len(rows) > 1:
            evangelist_col += _article_paragraphs(rows[1], tr=self._tr)
        # Column 3 — the Element: the name in its active wheel hue, then
        # its humoral article (rows[2] when written).
        hue = palette_for(self._skin)[index]
        element_col = _hover_title(
            html.escape(self._tr("The Element"))
        ) + _centered_html(
            f"<b style='color: {hue}'>"
            f"{html.escape(self._tr(archetypes.tetramorph_element(index)))}</b>"
        )
        if len(rows) > 2:
            element_col += _article_paragraphs(rows[2], tr=self._tr)
        width = defaults.ARTICLE_THREE_COLUMN_WIDTH_PX
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
        key = archetype_key(self._skin)
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
        node = self._symbolism.archetype_article(set_name, entity)
        badge = _hover_badge(art) if archetype_art_ready(art) else ""
        title = _hover_title(html.escape(self._tr(name)))
        rows = (node or {}).get("rows") or ()
        if rows:
            parts = [badge, title, _article_body_html(rows[0], tr=self._tr)]
            if row2 is not None and len(rows) > 1:
                # The second row, split off by a rule — the same shape
                # as the cross arms' two data sets (owner pattern).
                parts += [
                    "<hr/>",
                    _hover_title(html.escape(self._tr(row2))),
                    _article_body_html(rows[1], tr=self._tr),
                ]
            return "".join(parts)
        subtitle = (
            _centered_html(f"<b>{html.escape(self._tr(row2))}</b>")
            if row2 is not None
            else ""
        )
        return badge + title + subtitle + _centered_html(
            "",
            html.escape(self._tr(archetypes.ARCHETYPE_PENDING_LINE)),
        )

    def _sun_face_tooltip(self, face: str, active: bool) -> str:
        """ONE face of the dual Sunday (owner 2026-07-13): on the
        Compass and the Seasons each face is its own person — its own
        name, its own plate, its own text (articles.<set>.sun.faces;
        the base article stands in until a theme's split lands). The
        Ruler face keeps the pointer/palette variant paragraph."""
        theme = self._skin.weekday_theme
        ruler = face == "ruler"
        dual_names = (
            self._skin.weekday_set.dual_names
            or defaults.WEEKDAY_DUAL_NAMES[theme]
        )
        display_name = dual_names[0 if ruler else 1]
        image = metal_variant_file(
            self._skin.weekday_set.bodies.get("sun")
            if ruler
            else self._skin.weekday_set.dual_asset,
            self._skin.weekday_set.metal,
        )
        node = self._symbolism.article(
            self._skin.weekday_set.article_set
            or constants.WEEKDAY_THEME_ARTICLES[theme],
            "sun",
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
                f"{self._ord(date.day)} {html.escape(self._month(date))} "
                f"{self._year(date)}"
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
        offset from the year-wheel positions. (In archetype mode the ARM
        figures answer through `_element_at`/`tooltip_at`, not here.)"""
        # Only INSIDE the drawn diamond (owner bug report): between the
        # arms the wheel itself answers — the Aura's day or the Umbra's
        # night. The ONE arm-diamond geometry lives in `_arm_angle_at`.
        arm_angle = self._arm_angle_at(point, radius, rotation)
        if arm_angle is None:
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
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
                f"{self._year(instant)} - {instant:%H:%M}",
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
            f"{self._year(day.chinese_start)} – "
            f"{day.chinese_end.day} {self._month_short(day.chinese_end)} "
            f"{self._year(day.chinese_end)}",
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
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        # The unlocked hidden mode (owner 2026-07-16, top-only round):
        # ONLY the 12h ring LETTER — M on DOMY, whatever glyph another
        # ring seats there — opens the Four Greetings. Only the letter
        # band OUTSIDE the tick scale: the ticks at that angle keep
        # their own day/year/moon reading. The 24h (Omega) letter used
        # to share this trigger; it now belongs to the reveal-week
        # double-click instead (see Compositor.hit_omega).
        half = defaults.GREETINGS_LETTER_HALF_DEG
        in_letter_band = (
            radius * defaults.TICK_HOVER_OUTER_FRACTION
            < distance
            <= radius * defaults.GREETINGS_LETTER_OUTER_FRACTION
        )
        if (
            in_letter_band
            and self._hidden_unlocked
            and (theta <= half or theta >= 360.0 - half)
        ):
            return self._greetings_tooltip()
        # The per-letter HOVER LEGEND (owner ROADMAP 15b, "malo legende
        # oko tih naših odabira"): a ring preset may carry a `legend`
        # per position (Database/ring_presets.json — MASON G today) —
        # what that letter stands for, quoted verbatim from CANON.md's
        # Banknote table. Checked on every letter the active preset
        # seats, independent of the hidden-mode unlock (unlike the Four
        # Greetings, this is not an Easter egg); a preset without a
        # legend (DOMY/MORPH/NUMBERS, every custom ring) falls through
        # unchanged.
        if in_letter_band:
            legend = self._ring_letter_legend_tooltip(theta, half)
            if legend is not None:
                return legend
        if not (
            radius * defaults.TICK_HOVER_INNER_FRACTION
            <= distance
            <= radius * defaults.TICK_HOVER_OUTER_FRACTION
        ):
            return None
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
        next_cycle = self._last_tick.moon_fraction > 0.5 and fraction < 0.5
        cycle_day = f"{fraction * constants.SYNODIC_MONTH_DAYS:.1f}"
        line_moon = (
            f"{self._label('Illumination')} "
            f"{nominal_illumination(fraction) * 100:.1f}% - "
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

    def _ring_letter_legend_tooltip(
        self, theta: float, half: float
    ) -> str | None:
        """The per-letter HOVER LEGEND (ROADMAP 15b): `skin.ring.
        letter_legend` is hour -> {name, reading}, built by
        `app.controller.build_skin` from the active ring preset's
        optional `legend` card (`data.rings.validate_preset`) — empty
        for every preset but MASON G today. Finds the legend entry
        whose OWN letter position is within `half` degrees of the
        hovered angle (the same half-width the 12h Four Greetings
        trigger uses — every ring letter occupies the same angular
        slot) and returns its title + reading, or None off any legend
        letter."""
        legend = self._skin.ring.letter_legend
        if not legend:
            return None
        for hour, entry in legend.items():
            letter_theta = ((hour - 12) * 15.0) % 360.0
            delta = min(
                (theta - letter_theta) % 360.0,
                (letter_theta - theta) % 360.0,
            )
            if delta <= half:
                return _hover_title(
                    html.escape(entry["name"])
                ) + _article_body_html(entry["reading"])
        return None

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

    def _greetings_tooltip(self) -> str:
        """The Four Greetings legend (owner 2026-07-14): the verses
        CENTERED in italic with their line breaks kept, then the
        reading and the watchmaker's commentary as a justified column
        — Serbian in every language, on the 12h/24h ring letters."""
        data = _greetings()
        gap = defaults.GREETINGS_STANZA_GAP_PX
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
            _hover_title(html.escape(data["title"]))
            + stanzas
            + _article_body_html(
                data["explanation"] + "\n\n" + data["commentary"]
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
            # _centered_html — the ordinal carries real <sup> markup
            # (owner bug 2026-07-14: it printed literally through the
            # escaping _centered).
            title += _centered_html(
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
        eclipse = tick.eclipse_event
        if eclipse is not None and eclipse.kind == "lunar":
            lines.insert(0, self._eclipse_hover_line(eclipse))
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

    def _eclipse_hover_line(self, eclipse) -> str:
        """The eclipse hover line (ROADMAP 15h item 11, owner spec:
        NAME the eclipse): type + magnitude + local instant, plain
        (non-bold) like the season-event line it stands beside/replaces
        on the Earth/Moon hover.

        `self._ord()` already returns safe HTML (a raw `<sup>` suffix in
        English). It MUST NOT be escaped again — escaping the composed
        line (owner bug 2026-07-18, Session 21-D: the superscript leak)
        turned `<sup>` into the literal text `&lt;sup&gt;...`. Every
        free-form/translated piece is escaped on its OWN before joining;
        the ordinal rides in raw."""
        instant = eclipse.instant.astimezone(self._day.tzinfo)
        title = html.escape(self._tr(
            "Solar Eclipse" if eclipse.kind == "solar" else "Lunar Eclipse"
        ))
        kind = html.escape(self._tr(eclipse.type.capitalize()))
        mag_label = html.escape(self._tr("mag."))
        mag = f"{eclipse.magnitude:.2f}" if eclipse.magnitude is not None else "?"
        return (
            f"{title} ({kind}, {mag_label} {mag}) — "
            f"{self._ord(instant.day)} {html.escape(self._month(instant))} "
            f"{instant:%H:%M}"
        )

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
            f"{html.escape(self._month(date))} {self._year(date)}",
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
        eclipse = self._last_tick.eclipse_event
        if eclipse is not None and eclipse.kind == "solar":
            lines.insert(0, self._eclipse_hover_line(eclipse))
        elif self._last_tick.season_event is not None:
            lines.insert(
                0, html.escape(self._tr(self._last_tick.season_event))
            )
        return _centered_html(*lines)

    def _period_earth_html(self, kind: str) -> str:
        """The active region's own Earth face rides the Day/Night hover
        (owner 2026-07-12): the day art on the Day side, the night art
        on the Night side — atmosphere or clean per the Earth setting."""
        marker = self._skin.year_marker
        region = earth_region(self._day.latitude, marker.default_variant)
        path = marker.variants.get(
            f"{self._skin.earth_style}_{region}_{kind}"
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

    def _calendar_tooltip(self, point: QPointF, radius: float) -> str | None:
        """The Calendar wedge hover (owner 2026-07-16, kept modest —
        full articles arrive with the archetype engine). Almanac: the
        month name and the wedge's Chinese double-hour animal with its
        clock span, above OUR Chinese COLORED medallion of that animal.
        Zodiac: the sign name with its date span (the existing
        year-wheel cusps), above the sign's COLORED LOGO art — never a
        unicode glyph standing in for the art (owner 2026-07-16, ROADMAP
        queue #7)."""
        from render.layers import calendar_wheel, octa_slot_art

        distance = math.hypot(point.x(), point.y())
        outer = radius * self._skin.background.aura_radius_fraction
        if not (radius * 0.08 <= distance <= outer):
            return None
        theta = math.degrees(math.atan2(point.x(), -point.y())) % 360.0
        step = constants.CALENDAR_WEDGE_DEG
        day = self._day
        if calendar_wheel(self._skin) == "almanac":
            index = int((theta + step / 2.0) // step) % 12
            month = (index + 5) % 12 + 1
            animal = constants.CHINESE_ANIMALS[(index - 6) % 12]
            center_hour = (2 * index - 12) % 24
            start_hour, end_hour = (center_hour - 1) % 24, (center_hour + 1) % 24
            art = octa_slot_art(
                constants.CHINESE_STYLE_ART_DIRS["colored"], animal
            )
            return _hover_badge(art) + _centered_html(
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
        name, symbol = constants.ZODIAC_SIGNS[int(start_angle) // 30]
        start, end = zodiac_span(day.year_anchors, start_angle)
        start = start.astimezone(day.tzinfo)
        last = end.astimezone(day.tzinfo) - timedelta(days=1)
        art = octa_slot_art(constants.ZODIAC_STYLE_ART_DIRS["colored"], name)
        return _hover_badge(art) + _centered_html(
            f"<b>{html.escape(symbol)} {html.escape(self._tr(name))}</b>",
            f"{self._ord(start.day)} {html.escape(self._month(start))} - "
            f"{self._ord(last.day)} {html.escape(self._month(last))}",
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

    def _calendar_lit(self, tick: TickState) -> int | None:
        """The Calendar wedge index that lights (owner 2026-07-16), or
        None off the Calendar pointer. Shared by the composite key and
        the wedge render (Rule #5)."""
        if self._skin.pointer != "calendar":
            return None
        from render.layers import calendar_lit_index

        return calendar_lit_index(
            self._skin, self._skin.calendar_lighting,
            tick.hour_angle, self._day,
        )

    def _archetype_lit(self, tick: TickState) -> int | None:
        """The archetype figure whose HOUR-SPACE holds the hour hand
        (owner 2026-07-16), or None off the mode. Shared by the
        composite key and the figure render (Rule #5); the spaces ride
        the drawn arms, so the solar rotation feeds in."""
        if not archetype_active(self._skin):
            return None
        return archetype_lit_index(
            self._skin.pointer, tick.hour_angle, self._rotation()
        )

    def _render_group(
        self, layers: list[Layer], size: float, dpr: float,
        calendar_lit: int | None = None,
    ) -> QPixmap:
        """Rasterize ONE contiguous run of hover-invariant STATIC/DAILY
        layers into a padded pixmap (owner 2026-07-17, ROADMAP 15f).
        These layers include the ring letters, which OVERHANG the dial
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
            radius=size / 2, cache=self._cache, dpr=dpr,
            rotation=self._rotation(), hovered=None,
            reveal_active=False, calendar_lit=calendar_lit,
            archetype_lit=None,
        )
        for layer in layers:
            painter.save()   # isolate pen/brush/opacity/rotation leaks
            layer.paint(painter, ctx)
            painter.restore()
        painter.end()
        pixmap.setDevicePixelRatio(dpr)
        return pixmap
