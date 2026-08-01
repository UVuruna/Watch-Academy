"""Skin -> geometry queries: the dial's shape read off a skin.

Every "what does THIS skin say" question a layer asks — palettes, arm
counts and half-angles, the wheel and its dualities, the seat angles,
which laws are active (daylight, cube look, archetype) and where the
weekday slots sit. Pure functions of a `SkinDefinition`; no painting.
"""

from PySide6.QtGui import QColor

from config import archetypes, constants, palette
from render.context import RenderContext
from skins.manifest import SkinDefinition

def palette_for(skin: SkinDefinition) -> tuple:
    """The active Star+Aura BASE palette — ONE source for both the star
    diamonds and the background wedges (owner spec): the user's custom
    hues when set (settings dialog), otherwise the owner preset. RAW —
    no saturation applied here any more (owner fix round E, 2026-07-19,
    slika 2: the Saturation slider must move the AURA only, never the
    star diamonds). `StarLayer` reads THIS function directly; the Aura
    consumption path reads `aura_palette_for` below instead."""
    return (
        skin.palette_override if skin.palette_override is not None
        else palette.PALETTE_PRESETS[(skin.pointer, skin.palette_style)]
    )


def aura_palette_for(skin: SkinDefinition) -> tuple:
    """`palette_for(skin)` with the Aura Saturation slider applied (owner
    fix round E, 2026-07-19, slika 2: re-scoped from "Pointer" — the
    slider now scales ONLY the colored period wedges behind/around the
    diamonds, `BackgroundLayer`'s Aura, never the star diamonds
    themselves). The storage key stays `pointer_saturation` (Settings ▸
    Colors label renamed to "Aura"; migrating the persisted key would
    add a settings-migration path for a purely internal name with zero
    user-visible benefit, so the field keeps its name — this docstring
    is the pointer). 1.0 leaves the hues untouched."""
    hues = palette_for(skin)
    if skin.pointer_saturation == 1.0:
        return hues
    return tuple(_saturate_hue(hue, skin.pointer_saturation) for hue in hues)


def _saturate_hue(hue: str, factor: float) -> str:
    """Scale one `#RRGGBB` hue's HSV saturation by `factor` (0.0..1.0,
    clamped) — value and hue untouched, so 0.0 grays the color to its
    OWN brightness rather than to a flat white/black."""
    color = QColor(hue)
    h, s, v, a = color.getHsvF()
    color.setHsvF(max(h, 0.0), max(0.0, min(1.0, s * factor)), v, a)
    return color.name()


def arm_offset_deg(skin: SkinDefinition) -> float:
    """THE OFFSET WHEELS (`constants.WHEEL_ARM_OFFSET_DEG`) — the wheels
    that seat their arms off the pointer's own default angles, read by
    every arm consumer through this ONE function (Rule #5): the star
    diamonds and polygon faces, the Aura wedges, the weekday slots, the
    lit-index math and the arm hit-test.

    - THE GENESIS INVERSION (owner: "trougao ka dole", CUBE.md): the
      trio's TERTIARY wheel swings 180°, onto 24h/16h/08h.
    - THE SEASONS ROTATION (owner 2026-07-29): the cross's TERTIARY
      wheel turns 45°, half a wedge, so its color BOUNDARIES land on
      12h/3h/6h/9h — the astronomical seasons, each beginning at its
      turning point. The cross's other two wheels stay centered on the
      cardinals (meteorological).

    0 on every other wheel."""
    return constants.WHEEL_ARM_OFFSET_DEG.get(
        (skin.pointer, skin.palette_style), 0.0
    )


def aura_wedge_anchor(skin: SkinDefinition) -> tuple[float, float]:
    """Where a hue's Aura WEDGE stands relative to that hue's LEAD RAY,
    as (low, high) FRACTIONS of the hue's own share of the circle —
    `constants.AURA_WEDGE_ANCHOR_DEFAULT` and, on the Rose,
    `constants.ROSE_AURA_WEDGE_ANCHOR` (owner's correction round
    2026-07-29, his exact numbers).

    The lead ray is the direction the hue wears on the topmost (0°)
    star, which on a one-star pointer is simply its arm — so the default
    (−½, +½) is the standing arm-centered wedge. The Rose wears each hue
    on THREE rays and its two wheels read them differently: LEGACY's
    wedge TRAILS the lead ray (−1, 0 — the past lies behind the hour, so
    the boundaries land ON the lead-ray hours), PROPHECY's stands
    CENTERED on it (−½, +½ — past and future symmetric).

    THE PROPHECY SHIFT IS GONE (owner correction 2026-07-29): the star
    tips never move, both wheels keep every ray on a full hour, and the
    per-wheel difference lives HERE, in the background alone."""
    if skin.pointer != "rose":
        return constants.AURA_WEDGE_ANCHOR_DEFAULT
    return constants.ROSE_AURA_WEDGE_ANCHOR[
        palette.effective_palette_style(skin.pointer, skin.palette_style)
    ]


def polygon_shape(skin: SkinDefinition) -> bool:
    """Whether the reader asked for the POLYGON shape on a pointer that
    HAS one (owner sheet 2026-07-29). Aurora draws no pointer at all, so
    the setting is inert there — never rewritten, the
    `effective_palette_style` pattern."""
    return skin.pointer_shape == "polygon" and skin.pointer != "aurora"


def polygon_faces(skin: SkinDefinition) -> bool:
    """Whether the drawn arm is a POLYGON FACE — the kite filling its
    share of a plain 3/4/6/8-gon — rather than a star diamond. The
    Calendar's twelve-point and the Rose's twenty-four-point "polygons"
    are STARS with touching arms, so they answer False and take the
    star construction (and, with it, no curvature)."""
    return polygon_shape(skin) and skin.pointer in constants.POLYGON_POINTERS


def drawn_arm_count(skin: SkinDefinition) -> int:
    """How many arms the drawn wheel really carries — which is NOT
    always the palette size: the polygon shape counts what the READER
    counts (`POINTER_DIAL_COUNTS` — the Rose's 24 rays, the Calendar's
    12), the star shape counts one star's arms (the Rose draws its 8
    three times; the Calendar's two hexagrams carry 6 each)."""
    if polygon_shape(skin):
        return constants.POINTER_DIAL_COUNTS[skin.pointer]
    if skin.pointer == "calendar":
        return constants.CALENDAR_STAR_ARMS
    return constants.POINTER_POINTS[skin.pointer]


def arm_half_deg(skin: SkinDefinition) -> float:
    """The drawn arm half-angle: the pointer's slim-diamond value —
    EXCEPT wherever the arms fill their whole share of the circle, where
    the half is the regular `180/N` of the DRAWN arm count:

    - the CUBE look, whose three (trio) or six (hexa) rhombi tile the
      hexagon exactly — the corner-view cube's visible faces (CUBE.md);
    - the POLYGON shape, whose faces meet edge to edge (the square's 45°,
      the hexagon's 30°, the octagon's 22.5°, the cube hexagon's 60°) and
      whose Calendar/Rose stars have adjacent arms exactly touching
      (15° on twelve rays, 7.5° on twenty-four);
    - the CALENDAR's star shape, whose two hexagrams are regular
      six-point stars (30°).

    The star geometry formula (inner = tip / 2cos(half)) lands the side
    vertices exactly where each of those figures needs them — the shapes
    are pure angle math, never new art."""
    if polygon_shape(skin) or cube_look_active(skin):
        return 180.0 / drawn_arm_count(skin)
    if skin.pointer == "calendar":
        return 180.0 / constants.CALENDAR_STAR_ARMS
    return constants.POINTER_ARM_HALF_ANGLE_DEG[skin.pointer]


def rose_star_offsets(skin: SkinDefinition) -> tuple:
    """THE ROSE'S THREE STARS in DRAW ORDER (owner seal 2026-07-27,
    CUBE.md §The Rose) — bottom of the z-stack first, topmost last.
    Legacy leans wholly behind the hour (−30°, −15°, 0°); Prophecy is
    symmetric and rides the FUTURE over the PAST (−15°, +15°, 0°). The
    0° star is last on both, so the fully visible arm always points at
    true 12h. `()` on every other pointer — a one-star pointer draws
    its single star through the same loop with no offset."""
    if skin.pointer != "rose":
        return ()
    return constants.ROSE_STAR_OFFSETS[
        palette.effective_palette_style(skin.pointer, skin.palette_style)
    ]


def rose_star_set(offset: float) -> str:
    """Which figure set the Rose star at `offset` carries (CUBE.md §The
    Rose): "modern" on the true hours, "historical" one ray back, and
    "archetypal" wherever its wheel sent the myth star — −30° on Legacy
    (the myth we inherited), +15° on Prophecy (the myth that comes). The
    three words are `cube.FIGURE_SETS`, so the star names the very set
    the roster and the disk register name (Session 24)."""
    return constants.ROSE_STAR_SETS[offset]


def _wheel(skin: SkinDefinition) -> str:
    """The skin's EFFECTIVE wheel slot — the stored palette_style
    normalized to what this pointer actually serves (Rule #5: the same
    `palette.effective_palette_style` every other wheel reader uses)."""
    return palette.effective_palette_style(skin.pointer, skin.palette_style)


def horizontal_duality(skin: SkinDefinition) -> bool:
    """Whether this skin's Sunday duality rides the HORIZONTAL blue<->red
    axis — Servant on blue 06h left, Ruler on red 18h right (owner seal
    2026-07-29): the Rose on BOTH its wheels, plus the wheels
    `constants.HORIZONTAL_DUALITY_WHEELS` names (the Compass's Character
    wheel, which wears the same ROSE_PALETTE hues)."""
    return (
        skin.pointer == "rose"
        or (skin.pointer, _wheel(skin)) in constants.HORIZONTAL_DUALITY_WHEELS
    )


def center_duality(skin: SkinDefinition) -> bool:
    """Whether this skin's Sunday duality lives in ONE CENTER image —
    the Trinity and the Prism on every wheel, plus the wheels
    `constants.CENTER_DUALITY_WHEELS` names (the Quaternity's Seasons
    wheel: its arms turn onto the diagonals, so no 12h/24h seat exists
    to hold a second face — owner seal 2026-07-29)."""
    return (
        skin.pointer in ("hexa", "trio")
        or (skin.pointer, _wheel(skin)) in constants.CENTER_DUALITY_WHEELS
    )


def _base_weekday_slots(skin: SkinDefinition) -> tuple:
    """The raw weekday table this skin reads BEFORE offsets and flips:
    the pointer's own — except the horizontal-duality wheels of other
    pointers (the Compass's Character wheel), which take the ROSE's
    hue-seated table wholesale, because their arms wear the Rose's own
    hues and the seat is the HUE (owner seal 2026-07-29)."""
    if (skin.pointer, _wheel(skin)) in constants.HORIZONTAL_DUALITY_WHEELS:
        return constants.POINTER_WEEKDAY_SLOTS["rose"]
    return constants.POINTER_WEEKDAY_SLOTS[skin.pointer]


def _duality_ruler_default_angle(skin: SkinDefinition) -> float:
    """The Ruler's (the "sun" occupant's) UNFLIPPED seat — wherever the
    skin's own weekday table seats him, before any flip
    (`_duality_flipped`) swaps it with the Servant's."""
    return next(
        angle
        for angle, occupants in _base_weekday_slots(skin)
        if "sun" in occupants
    )


def _duality_servant_default_angle(skin: SkinDefinition) -> float:
    """The Servant's UNFLIPPED seat, before any flip: the blue 06h/270°
    arm on every horizontal-duality wheel (`constants.SERVANT_SEAT_
    ANGLE`), the 24h bottom everywhere else."""
    if horizontal_duality(skin):
        return constants.SERVANT_SEAT_ANGLE["rose"]
    return constants.SOUTH_SLOT_ANGLE


def _duality_flipped(skin: SkinDefinition) -> bool:
    """Whether this theme swaps the Ruler's and the Servant's seats on
    this skin (the two faces swap ARMS, never names or articles):
    on a HORIZONTAL wheel, the Sacred-Axis themes (`constants.DUALITY_
    RULER_ON_COLD_POLE` — Christianity pulls to the cold blue pole,
    Satanism to the warm red); on a VERTICAL wheel, the geographic
    themes (`constants.DUALITY_SERVANT_ON_TOP` — the Arctic IS the
    north, owner seal 2026-07-29). A CENTER duality has no seats to
    swap."""
    if center_duality(skin):
        return False
    if horizontal_duality(skin):
        return skin.weekday_theme in constants.DUALITY_RULER_ON_COLD_POLE
    return skin.weekday_theme in constants.DUALITY_SERVANT_ON_TOP


def ruler_seat_angle(skin: SkinDefinition) -> float:
    """The angle the RULER face of Sunday occupies — normally wherever
    the pointer's own weekday table seats the "sun" occupant, UNLESS
    the Duality-Axes config flips this theme (`_duality_flipped`), in
    which case the Ruler takes the Servant's default seat instead —
    the two faces swap ARMS, never their names or articles."""
    if _duality_flipped(skin):
        return _duality_servant_default_angle(skin)
    return _duality_ruler_default_angle(skin)


def servant_seat_angle(skin: SkinDefinition) -> float:
    """The angle the SERVANT face of Sunday occupies (Rule #5 — the ONE
    reader of `constants.SERVANT_SEAT_ANGLE`). The 24h bottom on the
    vertical wheels (Quaternity/Compass primary+secondary); the BLUE
    06h arm on every horizontal wheel (the Rose and the Compass's
    Character wheel), because blue is the servant's hue and red the
    master's (CUBE.md §The Rose) — UNLESS the theme flips
    (`_duality_flipped`: the Sacred Axis pulls Christianity to blue and
    Satanism to red on the horizontal; the geographic flip sends the
    Arctic up top on the vertical), in which case the Servant takes the
    Ruler's default seat instead."""
    if _duality_flipped(skin):
        return _duality_ruler_default_angle(skin)
    return _duality_servant_default_angle(skin)


def daylight_active(skin: SkinDefinition) -> bool:
    """Whether the day/night law paints this dial (owner 2026-07-27).
    Every pointer but the Calendar and the Rose ALWAYS runs day/night;
    those two carry the reader's own switch, because their wheels are
    read as a wheel first and a clock second. The stored setting is
    ignored — never rewritten — on the other five, so it survives a
    pointer switch untouched (the `effective_palette_style` pattern).

    With it False NOTHING on the disc reads the sun (owner correction
    2026-07-29): the star paints once at full day alpha, the Umbra
    stands at flat noon and the Aura wears full color over the whole
    circle. The FIGURE faces are untouched — they keep reading the real
    sky. It answers on the two fields alone (`pointer`, `daylight`), so
    the Design window can ask it of the raw `Settings` object it holds
    and the ONE law serves both (Rule #5)."""
    if skin.pointer not in constants.DAYLIGHT_SWITCH_POINTERS:
        return True
    return skin.daylight


def cube_look_active(skin: SkinDefinition) -> bool:
    """Whether the CUBE look dresses the drawn wheel (owner seal
    2026-07-26, CUBE.md §Display laws): the settings toggle is on AND
    the active wheel belongs to the Double-Trinity family — the Court
    (trio primary), Genesis (trio tertiary) or the Council (hexa tertiary)."""
    return (
        skin.cube_look
        and skin.show_pointer
        and (skin.pointer, skin.palette_style) in constants.CUBE_LOOK_WHEELS
    )


def weekday_slots(skin: SkinDefinition) -> tuple:
    """The skin's weekday slots as DRAWN — every consumer of
    `constants.POINTER_WEEKDAY_SLOTS` reads through this (Rule #5).
    Three transforms, in order: the wheel's own arm offset (slots ride
    the DRAWN arms — pure geometry: each occupant pair stays glued to
    its arm as the Genesis/Seasons wheels swing it; no re-pairing
    doctrine is invented here); the CENTER-duality wheels lift the Sun
    OUT (he stands in the center there — owner seal 2026-07-29); and a
    flipped theme (`_duality_flipped`) relocates the Sun alone onto the
    Servant's default seat — the Servant's own seat is never IN this
    table (drawn separately), and on a shared slot only the SUN moves:
    his slot-mates keep their arm (the cross's Jupiter stays put when
    continents sends the Ruler down to 24h)."""
    slots = _base_weekday_slots(skin)
    offset = arm_offset_deg(skin)
    if offset != 0.0:
        slots = tuple(
            ((angle + offset) % 360.0, occupants) for angle, occupants in slots
        )
    if center_duality(skin):
        return tuple(
            (angle, occupants) for angle, occupants in (
                (angle, tuple(o for o in occupants if o != "sun"))
                for angle, occupants in slots
            )
            if occupants
        )
    if _duality_flipped(skin):
        target = (_duality_servant_default_angle(skin) + offset) % 360.0
        moved, merged = [], False
        for angle, occupants in slots:
            occupants = tuple(o for o in occupants if o != "sun")
            if not occupants:
                continue
            if angle == target:
                occupants, merged = occupants + ("sun",), True
            moved.append((angle, occupants))
        if not merged:
            moved.append((target, ("sun",)))
        slots = tuple(moved)
    return slots


def hover_factor(ctx: "RenderContext", element: str) -> float:
    """The hover-enlarge multiplier when `element` is under the cursor
    (owner EXTRAS: one shared factor for every element), else 1.0."""
    return ctx.skin.hover_enlarge if ctx.hovered == element else 1.0


def visible_occupant(occupants: tuple[str, ...], today: str) -> str:
    """Shared-slot priority (owner rule): the occupant whose weekday comes
    NEXT from today wins — and today itself always wins (distance 0)."""
    today_index = constants.SUNDAY_FIRST_INDEX[today]
    return min(
        occupants,
        key=lambda body: (constants.SUNDAY_FIRST_INDEX[body] - today_index) % 7,
    )


def today_slot_theta(skin: SkinDefinition, today: str) -> float | None:
    """Unrotated dial angle of the slot showing today's body, or None
    when today lives in the center (the hexa pointer keeps the Sun
    there). Reads the DRAWN slots (`weekday_slots` — the Genesis
    inversion moves the trio's slots with its arms)."""
    for angle, occupants in weekday_slots(skin):
        if today in occupants:
            return angle
    return None


def archetype_key(skin: SkinDefinition) -> str | None:
    """The ACTIVE archetype — the grid entry of (pointer, wheel) while
    the mode is ON and the pointer is drawn; None otherwise (mode off,
    the archetype-less Aurora/Calendar, or the Pointer element off —
    the figures ride the diamonds, no arms means no archetype)."""
    if not (skin.archetype_mode and skin.show_pointer):
        return None
    return archetypes.grid_key(skin.pointer, skin.palette_style)


def archetype_active(skin: SkinDefinition) -> bool:
    """True while the ARCHETYPE MODE overrides the dial (owner sealed
    package 2026-07-16) — the weekday model and all three slots are
    OFF for rendering and hit-testing, without touching settings."""
    return archetype_key(skin) is not None


# --- THE DRAWN WHEEL (Pointers REWORK phase 1, owner sheet 2026-07-29) -------
# One arm is one PATH. Which path — a star diamond or a polygon face —
# is the only difference between the two shapes; the palette, the wheel
# offsets, the rotation, the day/night law and the borders are shared
# code below (Rule #5).


def wheel_rotation(skin: SkinDefinition, rotation: float) -> float:
    """The rotation the drawn wheel rides: the solar offset — except on
    the CALENDAR, whose figure stands on the wedges it colors and is
    therefore calendar-FIXED like the wedges themselves (owner spec)."""
    return 0.0 if skin.pointer == "calendar" else rotation
