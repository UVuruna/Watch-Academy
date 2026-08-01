"""Where the seats and slots SIT — the dial's seating layout.

Which slots a skin enables, the full slot layout (position, radius and
role per slot), seat rotation/scale/orbit, the classic weekday slot, and
the duality questions that decide who holds the Sunday and the centre
seat.
"""

from config import constants, dial, pantheon, paths
from render.skin_geometry import archetype_active, center_duality, servant_seat_angle, visible_occupant, weekday_slots
from skins.manifest import SkinDefinition


def enabled_slots(skin: SkinDefinition) -> tuple[tuple[int, str], ...]:
    """The ENABLED slots in order — (index, mode) pairs. They enable
    STRICTLY 1 → 2 → 3 (owner 2026-07-14: "ne može da uključi samo
    third"). In ARCHETYPE MODE (owner 2026-07-16) the answer is EMPTY:
    the mode overrides the weekday model and all three slots at this
    one shared gate — rendering, hit-testing and layer building all
    read the slot chain through here — while the user's settings stay
    untouched, so toggling the mode back restores everything."""
    if archetype_active(skin):
        return ()
    slots = []
    if skin.show_weekday:
        slots.append((1, skin.weekday_slot))
        if skin.show_octa_slot:
            slots.append((2, skin.octa_slot))
            if skin.show_third_slot:
                slots.append((3, skin.third_slot))
    return tuple(slots)


def slot_layout(skin: SkinDefinition) -> dict:
    """The owner's SLOT POSITION MATRIX (2026-07-14), slot index →
    seat: "classic" (the full weekday unit — arms rotation, ghosts,
    center, in that slot's theme), "center", or the seat's unrotated
    dial ANGLE (seats ride the star's rotation).

    One slot: weekday = the classic unit (Trinity/Prism keep their
    center rules); anything else sits at 24h on the Trinity and the
    pinned layouts, in the CENTER elsewhere. Two slots: the Seasons
    and the Compass give the (first) weekday slot the classic unit
    and the other the center — with no weekday both flank at 3h/21h;
    the Trinity and the Prism seat the pair on the 4h/20h arms. Three
    slots: the 1st on top (the Seasons lock it to the classic unit
    instead), the 2nd on the right, the 3rd on the left."""
    slots = enabled_slots(skin)
    if not slots:
        return {}
    order = [index for index, _ in slots]
    count = len(slots)
    pinned = (
        skin.pointer in ("aurora", "calendar") or not skin.show_pointer
    )
    if pinned:
        seats = {
            1: (constants.SOUTH_SLOT_ANGLE,),
            2: (constants.AURORA_DUAL_WEEKDAY_ANGLE,
                constants.AURORA_DUAL_SLOT_ANGLE),
            3: (constants.SLOT_SEAT_TOP_ANGLE,
                constants.SLOT_SEAT_RIGHT_ARM_ANGLE,
                constants.SLOT_SEAT_LEFT_ARM_ANGLE),
        }[count]
        return dict(zip(order, seats))
    if skin.pointer in ("trio", "hexa"):
        if count == 1:
            index, mode = slots[0]
            if mode == "weekday":
                return {index: "classic"}
            return {
                index: (
                    constants.SOUTH_SLOT_ANGLE
                    if skin.pointer == "trio"
                    else "center"
                )
            }
        if count == 2:
            return {
                order[0]: constants.SLOT_SEAT_LEFT_ARM_ANGLE,
                order[1]: constants.SLOT_SEAT_RIGHT_ARM_ANGLE,
            }
        return {
            order[0]: constants.SLOT_SEAT_TOP_ANGLE,
            order[1]: constants.SLOT_SEAT_RIGHT_ARM_ANGLE,
            order[2]: constants.SLOT_SEAT_LEFT_ARM_ANGLE,
        }
    # The Seasons (cross) and the Compass (octa): the weekday unit
    # keeps priority.
    if count == 1:
        index, mode = slots[0]
        return {index: "classic" if mode == "weekday" else "center"}
    if count == 2:
        weekday_indexes = [index for index, mode in slots if mode == "weekday"]
        if weekday_indexes:
            classic = weekday_indexes[0]      # both weekday → the 1st
            other = next(index for index in order if index != classic)
            return {classic: "classic", other: "center"}
        return {
            order[0]: constants.AURORA_DUAL_WEEKDAY_ANGLE,
            order[1]: constants.AURORA_DUAL_SLOT_ANGLE,
        }
    if skin.pointer == "cross":
        # The 1st is LOCKED to the weekday unit (owner; coerced in
        # apply_display_settings) — the other two flank at 3h/21h.
        return {
            order[0]: "classic",
            order[1]: constants.AURORA_DUAL_SLOT_ANGLE,
            order[2]: constants.AURORA_DUAL_WEEKDAY_ANGLE,
        }
    return {
        order[0]: constants.SLOT_SEAT_TOP_ANGLE,
        order[1]: constants.AURORA_DUAL_SLOT_ANGLE,
        order[2]: constants.AURORA_DUAL_WEEKDAY_ANGLE,
    }


def slot_seat_rotation(skin: SkinDefinition, rotation: float) -> float:
    """Seats ride the star's rotation ONLY while the pointer is drawn
    (owner 2026-07-15: without a pointer — Aurora included — the
    positions stay on natural round angles; the tilt exists solely to
    keep seats between the diamonds)."""
    if skin.show_pointer and skin.pointer not in ("aurora", "calendar"):
        return rotation
    return 0.0


def slot_seat_scale(skin: SkinDefinition) -> float:
    """The per-pointer slot SIZE factor (owner 2026-07-15): 125% on
    the slim-armed Seasons/Compass, 150% elsewhere."""
    if not skin.show_pointer:
        return dial.SLOT_SIZE_PINNED
    return dial.SLOT_SIZE_BY_POINTER[skin.pointer]


def weekday_body_size(skin: SkinDefinition, radius: float) -> float:
    """ONE size for EVERY weekday body — the diamond slot bodies AND the
    hexa/trio center Sun, in the normal state and during the reveal
    window alike (owner 2026-07-18, measured on his own dial: the center
    rendered `center_scale × seat factor` (~170 px against 144 px arms)
    normally and `center_scale` alone (~114 px) during the reveal —
    three formulas for one thing; supersedes the earlier "Sun is 1.20×"
    note that `center_scale` carried). The center-only showcase keeps
    `center_scale` — it has no diamond bodies to match."""
    return (
        2 * radius * skin.weekday_set.diamond_scale * slot_seat_scale(skin)
    )


def weekday_body_orbit(skin: SkinDefinition) -> float:
    """Orbit fraction (of the dial radius) that centers the weekday-by-
    colors body in its diamond: a romb's diagonals cross at EXACTLY half
    the star tip on every pointer (tip = star.radius_fraction), so the
    by-colors body rides that radius uniformly (owner 2026-07-15 — this
    one slot always sits at the romb center, whatever the pointer; the
    seated 2nd/3rd slots keep their own arm geometry)."""
    return skin.star.radius_fraction * dial.WEEKDAY_ROMB_CENTER_OF_TIP


def slot_seat_orbit(skin: SkinDefinition, seat) -> float:
    """The seat's orbit factor: on the slim-armed pointers an ANGLE
    seat shifts outward to the diamond's widest point (owner
    2026-07-15); the center and the pinned layouts stay put."""
    if (
        seat not in ("classic", "center")
        and skin.show_pointer
        and skin.pointer in dial.SLOT_SEAT_OUTWARD
    ):
        return dial.SLOT_SEAT_OUTWARD[skin.pointer]
    return 1.0


def weekday_classic_slot(skin: SkinDefinition) -> int | None:
    """Which slot drives the CLASSIC weekday unit — None when every
    enabled slot sits in a seat."""
    return next(
        (
            index for index, seat in slot_layout(skin).items()
            if seat == "classic"
        ),
        None,
    )


def slot_view(skin: SkinDefinition, index: int) -> tuple:
    """(mode, style, theme, metal, roster) of slot 1 / 2 / 3 — the
    roster is PER SLOT (owner 2026-07-15: slot 1 Greek Planetary next
    to slot 2 Greek Pantheon); the 1st slot's roster is whatever the
    weekday set was dressed in."""
    if index == 1:
        return (
            skin.weekday_slot, skin.day_slot_style,
            skin.weekday_theme, skin.weekday_set.metal,
            (
                "pantheon"
                if skin.weekday_set.body_articles is not None
                else "planetary"
            ),
        )
    if index == 2:
        return (
            skin.octa_slot, skin.info_slot_style,
            skin.info_slot_theme, skin.info_slot_metal,
            skin.info_slot_roster,
        )
    return (
        skin.third_slot, skin.third_slot_style,
        skin.third_slot_theme, skin.third_slot_metal,
        skin.third_slot_roster,
    )


def sunday_dual_face(skin: SkinDefinition) -> bool:
    """True while the SERVANT face holds its own seat on the Compass,
    the Seasons or the ROSE (owner correction 2026-07-13: NOT
    Sunday-only — it stands there all week like every other body,
    ghosted, and turns opaque on Sunday: "two persons, a union"). The
    seat itself is `servant_seat_angle` — 24h on the first two, the
    blue 06h arm on the Rose. The Trinity and the Prism keep one image
    ("two persons in one body") and speak the second face in the hover.
    Needs the CLASSIC unit up and the theme's dual art on disk
    (documented: no art, no second face). The CENTER-duality wheels of
    these pointers (the Quaternity's Seasons wheel) resolve through
    `center_dual_face` instead (owner seal 2026-07-29)."""
    spec = skin.weekday_set
    return (
        skin.pointer in ("octa", "cross", "rose")
        and not center_duality(skin)
        and weekday_classic_slot(skin) is not None
        and spec.display_mode != "center_only"
        and spec.dual_asset is not None
        and paths.art_file(spec.dual_asset).exists()
    )


def servant_holds_the_seat(skin: SkinDefinition, today: str) -> bool:
    """Whether the Servant face WINS his seat today (`servant_seat_angle`
    — 24h on the Compass/Seasons, the blue 06h arm on the Rose): on the
    Compass and the Rose the seat is his alone; on the Seasons he shares
    it with Mercury's slot and the standard shared-slot priority decides
    (the Servant counts as an eighth body whose day is Sunday)."""
    if not sunday_dual_face(skin):
        return False
    seat = next(
        (
            occupants
            for angle, occupants in weekday_slots(skin)
            if angle == servant_seat_angle(skin)
        ),
        (),
    )
    return not seat or visible_occupant(seat + ("sun",), today) == "sun"


def center_dual_face(skin: SkinDefinition) -> bool:
    """True while the Sunday duality lives in ONE CENTER image instead
    of the Compass/Seasons' two separate seats (round R3b item 3) — the
    complementary case to `sunday_dual_face`: the Prism and Trinity
    ALWAYS merge the classic unit's Sun into the center (their own
    docstring above: "keep one image... speak the second face in the
    hover"), and `center_only` mode merges it for EVERY pointer (there
    are no slot seats to hold a second face there). Given a dual asset
    exists, a theme's Sunday resolves through EXACTLY one of these two
    laws — never both, never neither."""
    spec = skin.weekday_set
    if weekday_classic_slot(skin) is None:
        return False
    if spec.dual_asset is None or not paths.art_file(spec.dual_asset).exists():
        return False
    if spec.display_mode == "center_only":
        return True
    return center_duality(skin)


def center_seat_body_key(skin: SkinDefinition, today: str) -> str | None:
    """The weekday-body KEY occupying the classic unit's CENTER seat on
    this skin, or None where no such seat exists — "sun" for the
    Prism/Trinity hexa/trio layouts (the ONLY body ever drawn there —
    `WeekdayLayer` seats every other body on an arm), `today` for the
    center_only showcase (its one and only seat, no arms at all). Both
    `CenterBodyLayer` and the compositor's hover read this to resolve
    the ordinary Sunday dual/Ninth face — independent of whether the
    theme carries a Ruler/Servant duality at all (`center_dual_face`
    additionally requires a `dual_asset`, which this key does not)."""
    if weekday_classic_slot(skin) is None:
        return None
    if skin.weekday_set.display_mode == "center_only":
        return today
    if center_duality(skin):
        return "sun"
    return None
