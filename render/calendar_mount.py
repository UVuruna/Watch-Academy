"""The calendar wheel and the 12-SET pointer mounts.

The wheel a skin's calendar pointer runs on, its wedge bounds and day
arrow, plus the DESIGN ZODIAC law's 12-set mounts (zodiac, months,
Chinese animals, Slavic months): each mount's wheel, per-index angle,
mark height, art entries and the currently-lit index.
"""

from pathlib import Path

from PySide6.QtGui import QPainter, QPolygonF

from config import calendar_mounts, constants
from core.clock_state import DayContext, TickState
from core.year_wheel import almanac_marker_angle, almanac_month_index
from render.context import RenderContext
from render.painting import dial_point, draw_name_label, draw_pixmap_centered, name_label_px
from render.subdial import octa_slot_art
from skins.manifest import SkinDefinition

def calendar_wheel(skin: SkinDefinition) -> str:
    """Which of the Calendar's two wheels is active (owner 2026-07-16):
    the palette_style CARRIES the wheel — paint = the Zodiac Dozen,
    light = the Almanac (Month) Dozen."""
    return "zodiac" if skin.palette_style == "primary" else "almanac"


def calendar_wedge_bounds(wheel: str) -> list[tuple[float, float]]:
    """The twelve wedge (start, end) dial angles, index 0 first (the top
    wedge), clockwise (owner 2026-07-16). ZODIAC boundaries sit ON the
    cardinal axes — the top wedge STARTS at the top (12h line); ALMANAC
    wedges are CENTERED on the axes — the top wedge is centered on the
    top (shifted half a wedge earlier). Starts may be negative; draw_pie
    handles the clockwise sweep."""
    step = constants.CALENDAR_WEDGE_DEG
    offset = 0.0 if wheel == "zodiac" else -step / 2.0
    return [(k * step + offset, k * step + offset + step) for k in range(12)]


def calendar_day_arrow(angle_deg: float, radius: float) -> QPolygonF:
    """The Almanac Earth day-arrow (owner 2026-07-16): a small triangle
    at `angle_deg`, tip toward the ring ticks, base inward — the ring
    reads today's date to the day. Tunables in defaults."""
    tip = radius * calendar_mounts.CALENDAR_ARROW_TIP_FRACTION
    base = tip - radius * calendar_mounts.CALENDAR_ARROW_LENGTH_FRACTION
    half = calendar_mounts.CALENDAR_ARROW_HALF_DEG
    return QPolygonF(
        [
            dial_point(angle_deg, tip),
            dial_point(angle_deg - half, base),
            dial_point(angle_deg + half, base),
        ]
    )


# --- Calendar-pointer 12-SET MOUNT (DESIGN ZODIAC law, R9a round 2026-07-21) --
# "Zodiac i sve što ima 12 TREBA da bude moguće da se AKTIVIRA na CALENDAR
# POINTER" (UV/DESIGN/DESIGN INSTRUCTIONS.txt): twelve small marks, one
# per wedge, mounted at CALENDAR_MOUNT_RADIUS_FRACTION — clear of the
# rim-riding Earth/Moon and the center subdial. A mount rides its OWN
# fixed wheel geometry (calendar_mount_wheel), independent of whichever
# wheel the background wedges currently paint (palette_style) — so the
# marks never jump when the owner switches Zodiac/Almanac colors.


def calendar_mount_wheel(mount: str) -> str:
    """Which `calendar_wedge_bounds` geometry a mount set's marks ride —
    read from the roster's own DOZEN SYSTEM (CANON.md §The Two Dozen
    Systems, `calendar_mounts.CalendarMount.system`): System "A" rides the
    ZODIAC wheel's cardinal-START wedges (boundaries on the cardinals,
    so the twelve fall into six pairs — sign i's wedge IS its own 30-deg
    arc), System "B" the ALMANAC wheel's cardinal-CENTERED wedges (one
    crown at 12h, one root at 24h, six opposition axes)."""
    return "zodiac" if calendar_mounts.CALENDAR_MOUNTS[mount].system == "A" else "almanac"


def calendar_mount_angle(mount: str, index: int) -> float:
    """Dial angle (clockwise from top) of mount seat `index`,
    Calendar-fixed (no rotation, matching the wedges themselves).

    THE SEAT LAW (owner decree 2026-07-29), one formula for both sizes
    (Rule #19 — no per-seat table exists for either):

        wedge      = index // seats_per_wedge
        pitch      = CALENDAR_WEDGE_DEG / seats_per_wedge
        angle      = wedge_center - (wedge_span - pitch) / 2 + slot·pitch

    A 12-set has one seat per wedge, the bracket vanishes and the seat
    IS the wedge center. A 24-set has two, and they land a quarter wedge
    either side of that center — a 15-deg pitch across the whole dial,
    the same pitch the Rose's three stars already stand on."""
    per_wedge = calendar_mounts.CALENDAR_MOUNT_SEATS_PER_WEDGE[
        calendar_mounts.CALENDAR_MOUNTS[mount].seats
    ]
    start, end = calendar_wedge_bounds(calendar_mount_wheel(mount))[
        index // per_wedge
    ]
    pitch = constants.CALENDAR_WEDGE_DEG / per_wedge
    first = (start + end) / 2.0 - (constants.CALENDAR_WEDGE_DEG - pitch) / 2.0
    return first + (index % per_wedge) * pitch


def calendar_mount_mark_height(mount: str, radius: float) -> float:
    """A mount mark's drawn height. `CALENDAR_MOUNT_MARK_SCALE` is sized
    so twelve marks never touch at the mount radius; a 24-set halves the
    seat pitch, so its marks halve with it (Rule #19: the size follows
    the seat law, it is not a second tunable). Shared by the paint pass
    and the compositor's own hit target (Rule #5)."""
    per_wedge = calendar_mounts.CALENDAR_MOUNT_SEATS_PER_WEDGE[
        calendar_mounts.CALENDAR_MOUNTS[mount].seats
    ]
    return 2 * radius * calendar_mounts.CALENDAR_MOUNT_MARK_SCALE / per_wedge


def calendar_mount_entries(mount: str) -> tuple[tuple[str, Path | None], ...]:
    """A mount set's (display_name, art_path_or_None) pairs in SEAT
    ORDER — twelve of them for a Dozen, twenty-four for a 24-set. Every
    field comes from the roster's own `calendar_mounts.CALENDAR_MOUNTS` entry
    (Rule #5: ONE registry, no per-roster branch survives here).

    Art is ALWAYS graceful-absent (the owner's R7b contract, now the
    universal rule): a plate that is not on disk resolves to None and
    routes the caller to the name-fallback, never a gap. `art_stems`
    covers the sets whose plates are not named for the member (the
    Slavic months are Croatian proper nouns with ASCII stems)."""
    entry = calendar_mounts.CALENDAR_MOUNTS[mount]
    return tuple(
        (name, octa_slot_art(entry.art_dir, stem))
        for name, stem in zip(entry.members, entry.stems)
    )


def calendar_mount_current_index(mount: str, day: DayContext) -> int | None:
    """The seat index TODAY owns on the mount's own wheel — the mark
    that earns the emphasis (owner spec: "the mark can inherit that
    brightness") — or None where the roster names no today, and every
    mark rests at the same opacity.

    WHAT counts as today is the roster's own `follows` declaration:
    "sign" reads the running zodiac sign, "month" the running Gregorian
    month (every month-keyed roster — the Chinese animals emphasize the
    same wedge the Slavic months do). Never hemisphere-mirrored: the
    mark sits on its OWN fixed wedge identity, matching what is drawn
    there, unlike the Earth marker's orbit."""
    entry = calendar_mounts.CALENDAR_MOUNTS[mount]
    if entry.follows == "sign":
        return entry.members.index(day.zodiac_name)
    if entry.follows == "month":
        return almanac_month_index(day.local_date.month)
    return None


def chinese_mount_dimmed_index(day: DayContext) -> int | None:
    """THE CAT'S DIMMING LAW (owner spec, item 5, R12): the wedge index
    to DIM on the "chinese" mount while The Cat holds the CENTER —
    "the first pass of the month belongs to its animal, the second
    pass — the month that does not exist — belongs to the Cat". None
    outside a Chinese-leap-month window (`DayContext.
    chinese_leap_month_number` is None then, the same field the CENTER
    seat itself reads)."""
    number = day.chinese_leap_month_number
    if number is None:
        return None
    # The doubled LUNAR month's own animal — lunar month N always names
    # CHINESE_ANIMALS[(N + 1) % 12] (month 1 = Tiger, index 2; month 11
    # = Rat, index 0; month 12 = Ox, index 1 — the fixed jianyin
    # numbering core.blue_moon.chinese_leap_month itself counts in) —
    # then the seat that animal holds on the mount's own wheel.
    animal = constants.CHINESE_ANIMALS[(number + 1) % 12]
    return calendar_mounts.CALENDAR_MOUNTS["chinese"].members.index(animal)


def _draw_calendar_mount(
    painter: QPainter, ctx: "RenderContext", mount: str
) -> None:
    """The mounted set's marks — one per SEAT (twelve for a Dozen,
    twenty-four for a 24-set), DAILY cadence (the current-mark emphasis
    is a day computation, never per-tick). Missing art falls back to the
    entity's NAME, the SAME convention archetype figures/weekday bodies
    use (`draw_archetype_figure`) — never a blank gap. On the "chinese"
    mount, the doubled month's own animal DIMS below its resting alpha
    while The Cat holds the center (`chinese_mount_dimmed_index`) —
    checked BEFORE the current-month emphasis, so the two never both
    apply to the one mark. A roster that names no today
    (`CalendarMount.follows` None) simply has no emphasized mark."""
    mount_radius = ctx.radius * calendar_mounts.CALENDAR_MOUNT_RADIUS_FRACTION
    mark_height = calendar_mount_mark_height(mount, ctx.radius)
    current = calendar_mount_current_index(mount, ctx.day)
    dimmed = chinese_mount_dimmed_index(ctx.day) if mount == "chinese" else None
    for index, (name, art) in enumerate(calendar_mount_entries(mount)):
        pos = dial_point(calendar_mount_angle(mount, index), mount_radius)
        if index == dimmed:
            alpha = calendar_mounts.CALENDAR_MOUNT_DIMMED_ALPHA
        else:
            alpha = calendar_mounts.CALENDAR_MOUNT_ALPHA + (
                calendar_mounts.CALENDAR_MOUNT_LIT_DELTA if index == current else 0.0
            )
        painter.save()
        painter.setOpacity(min(1.0, alpha))
        if art is not None:
            draw_pixmap_centered(painter, ctx, art, pos, mark_height)
        else:
            draw_name_label(painter, name, pos, name_label_px(name, mark_height))
        painter.restore()
