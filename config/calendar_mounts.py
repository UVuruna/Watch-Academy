"""The Calendar's dozen, its mounts, and the thirteenths' own
wedge geometry — the Calendar pointer's arrow/wedge constants,
the Slavic Months 12-set, and THE CALENDAR MOUNT REGISTRY (every
roster that may ride the twelve wedges).

Layer: config — pure, no Qt, no wall clock.
"""

from typing import NamedTuple

from config import constants, paths


# --- Calendar pointer (owner 2026-07-16, CANON §The Dozen) ---------------------
# The twelve wedges are Calendar-fixed — they never ride the solar
# rotation — but otherwise they ARE the standard Aura and wear its
# opacities (`BackgroundSpec.day_alpha` / `twilight_alpha`) under the
# day/night law like every other pointer. Both of the Calendar's own
# opacity constants are therefore gone: `CALENDAR_WEDGE_LIT_DELTA` with
# the lit-wedge feature (owner decree 2026-07-29) and the flat
# `CALENDAR_WEDGE_ALPHA` with its always-full-circle path (owner
# correction 2026-07-29 — the daylight switch must reach the
# background).
CALENDAR_WEDGE_RADIUS_FRACTION = 0.90  # wedge reach, of the dial radius
# The Earth DAY-ARROW on the Almanac wheel (owner 2026-07-16: "one tick
# ≈ one day"): a small triangle at the marker's exact tick, pointing
# from inside the dial OUTWARD toward the ring so the ring reads today's
# date to the day. Drawn procedurally (the ring numeral arrow is the
# visual reference).
CALENDAR_ARROW_TIP_FRACTION = 0.845  # arrow tip radius (just inside the ticks)
CALENDAR_ARROW_LENGTH_FRACTION = 0.06  # tip-to-base length, of the dial radius
CALENDAR_ARROW_HALF_DEG = 2.4        # half-width of the base, in dial degrees

# --- Calendar-pointer 12-sets: the Slavic Months (owner-sealed R7b 2026-07-21) -
# The DESIGN ZODIAC law (UV/DESIGN/DESIGN INSTRUCTIONS.txt): "Zodiac i
# sve što ima 12 TREBA da bude moguće da se AKTIVIRA na CALENDAR POINTER
# (TO MU JE DEFAULT)" — any twelve-fold set may MOUNT on the Calendar
# pointer as twelve marks, one per two-hour wedge, at 60-70% of the dial
# radius (so they clear the Earth/Moon at the rim and the subdials at the
# centre). This table REGISTERS the first such set beyond the zodiac
# signs and Chinese animals the pointer already reads: the twelve
# Croatian months as PROPER NOUNS with the English gloss, one per
# Gregorian month (`gregorian`, 1..12 — the Almanac wheel already maps
# month->wedge via core.year_wheel.almanac_month_index). `stem` is the
# ASCII plate stem under MONTHS_ART_DIR (assets/months/<stem>.png,
# graceful-absent — the mount draws the Croatian name instead until the
# owner's prompt sheet lands, `render.calendar_mount.calendar_mount_entries`).
# The MOUNT ITSELF (R9a round, 2026-07-21): drawing the twelve marks at
# CALENDAR_MOUNT_RADIUS_FRACTION and the Settings picker for WHICH
# 12-set mounts are both live now (render.layers.background.BackgroundLayer,
# app.design_window's Pointer tab) — see config/___config.md and
# app/encyclopedia.md for the Encyclopedia side.
SLAVIC_MONTHS = (
    # (croatian proper noun, english gloss, ascii stem, gregorian month)
    ("Siječanj", "the Month of Felling", "Sijecanj", 1),
    ("Veljača", "the Turning Month", "Veljaca", 2),
    ("Ožujak", "the Lying Month", "Ozujak", 3),
    ("Travanj", "the Grass Month", "Travanj", 4),
    ("Svibanj", "the Dogwood Month", "Svibanj", 5),
    ("Lipanj", "the Linden Month", "Lipanj", 6),
    ("Srpanj", "the Sickle Month", "Srpanj", 7),
    ("Kolovoz", "the Cartage Month", "Kolovoz", 8),
    ("Rujan", "the Reddening Month", "Rujan", 9),
    ("Listopad", "the Leaf-fall Month", "Listopad", 10),
    ("Studeni", "the Cold Month", "Studeni", 11),
    ("Prosinac", "the Month of Shining-Through", "Prosinac", 12),
)

# --- THE CALENDAR MOUNT REGISTRY (owner decree 2026-07-29) ---------------------
# "Zodiac i sve što ima 12 TREBA da bude moguće da se AKTIVIRA na
# CALENDAR POINTER" was implemented in 2026-07-21 as a hand-kept quartet
# of `if mount == ...` branches. It is now ONE TABLE: every roster whose
# membership fits the wedges declares itself here, and the renderer and
# the picker both read this and nothing else (Rule #5, Rule #19 — the
# geometry is computed from the declaration, never enumerated).
#
# THE TWO DOZEN SYSTEMS (CANON.md §The Two Dozen Systems and the Four
# Dozens, owner seal 2026-07-22) decide a mount's GEOMETRY, and every
# roster names the one it belongs to:
#
#   System "A" — the ZODIAC-aligned wheel: wedge BOUNDARIES sit ON the
#     cardinals (12h-14h, 14h-16h, ...), so the twelve fall into SIX
#     PAIRS — two flanking the top, two the bottom, two each side.
#     Carries the dozens that come IN PAIRS.
#   System "B" — the MONTH-aligned wheel: the same twelve 2-hour
#     watches SHIFTED 15° so their CENTERS sit on the cardinals
#     (11h-13h, ...). One CROWN (12h), one ROOT (24h), six OPPOSITION
#     AXES. Carries the dozens defined by OPPOSITES.
#
# THE SEAT LAW (owner decree 2026-07-29): a 12-set seats ONE member per
# wedge, at that wedge's own center; a 24-set seats TWO per wedge, at
# ±a quarter wedge from the center — a 15° pitch, the same the Rose's
# three stars already stand on. Both fall out of one formula in
# `render.calendar_mount.calendar_mount_angle`; nothing is tabulated per seat.
#
# THE CENTER (`centre`) is the `constants.THIRTEENTHS` key whose member
# may take the dial CENTER while this mount rides. Two different LAWS
# govern whether the seat actually shows (CANON §The Axle, owner-sealed
# 2026-07-29): a CALENDAR-DRIVEN centre (Ophiuchus/Sol/Modrenik/The Cat)
# keeps its own appearance rule (`core.blue_moon`), empty on almost every
# day of the year; an ALWAYS-CENTRE (`constants.AXLE_ALWAYS_CENTERS` —
# Hestia, Jesus, Prudence, Cunning, Peace, Hardness of Heart) is
# unconditionally present on EVERY date instead — the axle never leaves.
# `None` means the canon seals no thirteenth for this set and the center
# simply stays empty (no roster registered below leaves this None — the
# Sins Dozen, the last that might have, was sealed WITH its axle on
# 2026-07-29 — so the branch is exercised by a synthetic mount in
# `tests/test_calendar.py`).
CALENDAR_MOUNT_SEATS_PER_WEDGE = {12: 1, 24: 2}


class CalendarMount(NamedTuple):
    """One roster that may ride the Calendar's twelve wedges.

    `title` is the picker's label. `system` is "A" or "B" above.
    `members` are the display names in SEAT ORDER (index 0 = this
    mount's own first seat, counting clockwise from the dial top).
    `art_dir` is a subdirectory of `assets/calendars/`; `art_stems`
    names the plate stems only where they differ from the display
    names (the Slavic months are Croatian proper nouns with ASCII
    plates), else None — art is always graceful-absent, a missing
    plate falling back to the member's NAME.
    """

    title: str
    system: str
    members: tuple[str, ...]
    art_dir: str
    centre: str | None = None
    art_stems: tuple[str, ...] | None = None
    # WHICH member is TODAY'S (the mark that earns the emphasis):
    # "sign" — the running zodiac sign; "month" — the running Gregorian
    # month (every month-keyed roster); None — the set names no
    # today (the Emotions Dozen: there is no "today's emotion", so no
    # mark is emphasized and all twelve rest at the same opacity).
    follows: str | None = None

    @property
    def seats(self) -> int:
        return len(self.members)

    @property
    def stems(self) -> tuple[str, ...]:
        return self.art_stems or self.members


def almanac_seat_order(by_month: dict) -> tuple[str, ...]:
    """A Gregorian-month-keyed table in ALMANAC SEAT ORDER — June first,
    its wedge centered on the dial's top. The same rotation
    `core.year_wheel.almanac_month_index` applies, expressed here so
    `config` needs no `core` import (Rule #19: one rotation rule, two
    readers, zero written-out orderings)."""
    return tuple(by_month[(seat + 5) % 12 + 1] for seat in range(12))


# THE EMOTIONS DOZEN (CANON.md §The Two Dozen Systems, System B) — the
# ONE roster canon seats HOUR BY HOUR in its own words: "Love 12h, Hope
# 14h, Courage 16h, Ambition 18h, Pride 20h, Envy 22h, Hatred 24h,
# Despair 02h, Fear 04h, Doubt 06h, Humility 08h, Gratitude 10h". On
# System B geometry the top wedge IS 12h, so the canon hour order IS the
# seat order, one wedge every two hours clockwise — no mapping needed.
EMOTIONS_DOZEN = (
    "Love", "Hope", "Courage", "Ambition", "Pride", "Envy",
    "Hatred", "Despair", "Fear", "Doubt", "Humility", "Gratitude",
)

CALENDAR_MOUNTS = {
    # The Zodiac Dozen — System A (Cancer opens at the summer solstice,
    # the dial's own top). Its thirteenth is Ophiuchus.
    "zodiac": CalendarMount(
        title="Zodiac signs",
        system="A",
        members=tuple(name for name, _symbol in constants.ZODIAC_SIGNS),
        art_dir="zodiac/astrology/primary/colored",
        centre="ophiuchus",
        follows="sign",
    ),
    # The Month Dozen — System B, the Gregorian months the Almanac wheel
    # already paints. Its thirteenth is Sol (the Sun's own month).
    "almanac": CalendarMount(
        title="Months",
        system="B",
        members=almanac_seat_order(
            dict(enumerate(constants.GREGORIAN_MONTH_NAMES, start=1))
        ),
        art_dir="almanac/primary/colored",
        centre="sol",
        follows="month",
    ),
    # The Slavic Months — System B, the Croatian proper nouns with ASCII
    # plate stems. Its thirteenth is Modrenik (the Moon's own month).
    "months": CalendarMount(
        title="Slavic months",
        system="B",
        members=almanac_seat_order(
            {month: croatian for croatian, _gloss, _stem, month in SLAVIC_MONTHS}
        ),
        art_dir="slavic_months/primary/colored",
        centre="modrenik",
        follows="month",
        art_stems=almanac_seat_order(
            {month: stem for _croatian, _gloss, stem, month in SLAVIC_MONTHS}
        ),
    ),
    # The Chinese MONTH-branch animals (owner R12) — System B, NOT the
    # Chinese YEAR zodiac read elsewhere. Its thirteenth is The Cat.
    "chinese": CalendarMount(
        title="Chinese zodiac",
        system="B",
        members=almanac_seat_order(constants.CHINESE_MONTH_BRANCH_ANIMALS),
        art_dir="zodiac/chinese/primary/colored",
        centre="chinese",
        follows="month",
    ),
    # The Emotions Dozen (CANON §The Two Dozen Systems, one of the four
    # sealed Dozens) — System B, seated by canon's own hours. Its centre
    # is PEACE, the still point every emotion runs toward (SEALED
    # 2026-07-29, CANON §The Emotions Dozen) — an ALWAYS-CENTER, always
    # present (`constants.AXLE_ALWAYS_CENTERS`), unlike the calendar-driven
    # thirteenths above.
    "emotions": CalendarMount(
        title="Emotions",
        system="B",
        members=EMOTIONS_DOZEN,
        art_dir="emotions/primary/colored",
        centre="peace",
    ),
    # THE OLYMPIANS (CANON §The Olympians) — System A, the classical
    # Dodekatheon seated two by two, every wedge SEALED 2026-07-29: the
    # crown pair Zeus+Hera flanks the top, Demeter+Poseidon roots the
    # bottom, and Athena+Hephaestus/Artemis+Ares/Hermes+Dionysus/Apollo+
    # Aphrodite hold the four remaining arms. Member order below reads
    # CANON's own table top to bottom (12-14h..10-12h), which — on the
    # ZODIAC wheel's cardinal-START wedges (System A) — IS seat order
    # (seat k spans clock hour 12+2k, matching the existing "zodiac"
    # mount's own Cancer-first convention). Its centre is HESTIA, the
    # hiding-place axle who gave up her seat to Dionysus and kept the
    # hearth — always present, an ALWAYS-CENTER.
    "olympians": CalendarMount(
        title="Olympians",
        system="A",
        members=(
            "Zeus", "Athena", "Hephaestus", "Artemis", "Ares", "Demeter",
            "Poseidon", "Hermes", "Dionysus", "Apollo", "Aphrodite", "Hera",
        ),
        art_dir="olympians/primary/colored",
        centre="hestia",
    ),
    # THE APOSTLES (CANON §The Apostles) — System A, the Twelve sent out
    # two by two (Mark 6:7), every wedge SEALED 2026-07-29: Peter+Andrew
    # crown the top, Judas Iscariot+Simon the Zealot root the bottom.
    # Member order reads CANON's own table top to bottom, same seat-order
    # convention as "olympians" above. `art_stems` covers the four
    # members whose plate stem is not their full display name (the
    # sheet's own filenames). Its centre is JESUS, the throne axle —
    # always present, an ALWAYS-CENTER.
    "apostles": CalendarMount(
        title="Apostles",
        system="A",
        members=(
            "Peter", "James the Greater", "John", "Philip", "Bartholomew",
            "Judas Iscariot", "Simon the Zealot", "Thomas", "Matthew",
            "James of Alphaeus", "Thaddaeus", "Andrew",
        ),
        art_dir="apostles/primary/colored",
        centre="jesus",
        art_stems=(
            "Peter", "James", "John", "Philip", "Bartholomew", "Judas",
            "Simon", "Thomas", "Matthew", "James_Alphaeus", "Thaddaeus",
            "Andrew",
        ),
    ),
    # THE VIRTUE WHEEL (CANON §The Virtue Wheel) — System B, Aristotle's
    # twelve virtues (LIGHT register) and their twelve vices (PAINT
    # register) as TWO ENTRIES of one wheel: a virtue and its vice share
    # ONE seat, re-seated and SEALED 2026-07-29 (Magnanimity·Vanity crown
    # at 12h, Just Indignation·Envy root at 24h). Member order reads
    # CANON's own table top to bottom (12h..10h), the same System-B
    # seat-order convention `EMOTIONS_DOZEN` already uses (seat k = hour
    # 12+2k). `art_stems` covers the three members whose plate stem
    # differs from the display name (a space or hyphen the filename
    # cannot carry). Centres are the axle's two faces, both ALWAYS-
    # CENTERS, present on every date: PRUDENCE (light, the charioteer) and
    # CUNNING (paint, the dark charioteer) — CANON §The Virtue Wheel.
    "virtues": CalendarMount(
        title="Virtues",
        system="B",
        members=(
            "Magnanimity", "Truthfulness", "Courage", "Right Ambition",
            "Magnificence", "Wit", "Just Indignation", "Temperance",
            "Patience", "Modesty", "Generosity", "Friendliness",
        ),
        art_dir="virtues/primary/colored",
        centre="prudence",
        art_stems=(
            "Magnanimity", "Truthfulness", "Courage", "Right_Ambition",
            "Magnificence", "Wit", "Just_Indignation", "Temperance",
            "Patience", "Modesty", "Generosity", "Friendliness",
        ),
    ),
    "vices": CalendarMount(
        title="Vices",
        system="B",
        members=(
            "Vanity", "Boastfulness", "Cowardice", "Over-ambition",
            "Vulgarity", "Buffoonery", "Envy", "Gluttony", "Wrath",
            "Shamelessness", "Greed", "Flattery",
        ),
        art_dir="vices/primary/colored",
        centre="cunning",
        art_stems=(
            "Vanity", "Boastfulness", "Cowardice", "Over_Ambition",
            "Vulgarity", "Buffoonery", "Envy", "Gluttony", "Wrath",
            "Shamelessness", "Greed", "Flattery",
        ),
    ),
    # THE SINS DOZEN (CANON §The Sins Dozen) — the FIFTH Dozen, System
    # B, SEALED 2026-07-29: the Christian tradition's catalogue of SIN
    # (Gregory, Evagrius, Aquinas, Dante) beside — never merged with —
    # the Virtue Wheel's Aristotelian vices. PRIDE crowns at 12h, with
    # Vainglory FOLDED INTO IT (Gregory's root returns to the rim, one
    # seat, the stronger word); TREACHERY roots at 24h under the root
    # law (Judas' own midnight on the Apostles Dozen); VIOLENCE holds
    # 16h (the delegated call — Cruelty weighed and set aside). Member
    # order reads CANON's own table top to bottom (12h..10h), the same
    # System-B seat-order convention `EMOTIONS_DOZEN` uses (seat k =
    # hour 12 + 2k). Its centre is HARDNESS OF HEART, the ANTI-PEACE —
    # an ALWAYS-CENTER, present every date. No art has landed for this
    # roster at all yet (`research/prompts/calendars/sins_prompts.md`
    # is written but ungenerated), so every plate — the twelve and the
    # axle alike — takes the graceful-absent NAME fallback, exactly the
    # contract `art_dir` already documents.
    "sins": CalendarMount(
        title="Sins",
        system="B",
        members=(
            "Pride", "Hypocrisy", "Violence", "Avarice", "Lust", "Envy",
            "Treachery", "Despair", "Wrath", "Idolatry", "Gluttony", "Acedia",
        ),
        art_dir="sins/primary/colored",
        centre="hardness_of_heart",
    ),
}

# ═══════════════════════════ MOUNT RENDER TUNABLES ═══════════════════════════
# The legal `Settings.calendar_mount` values — derived, never hand-kept
# (adding a roster above adds its setting value automatically).
CALENDAR_MOUNT_MODES = ("off",) + tuple(CALENDAR_MOUNTS)
# The mid-radius the DESIGN ZODIAC law fixes for a mounted 12-set's marks
# (60-70% of the dial radius) — clear of the rim-riding Earth/Moon and
# the Calendar's own pinned South subdial (orbit ~0.43R).
CALENDAR_MOUNT_RADIUS_FRACTION = 0.65
# The mark's own drawn HEIGHT, fraction of the dial DIAMETER (the SAME
# unit WeekdaySpec.diamond_scale/YearMarkerSpec.scale use) — sized well
# under the 30-deg wedge's own arc gap at the mount radius (~0.17 of the
# diameter between neighboring mark centers) so twelve marks never touch.
CALENDAR_MOUNT_MARK_SCALE = 0.08
# The mark's resting opacity and the extra the CURRENT sign/month earns
# (owner spec: "the mark can inherit that brightness" — the SAME
# base+delta shape the wedges themselves once used, sized so the current
# mark reaches full opacity). This is the MARK's emphasis, NOT the
# deleted wedge lighting — it survived the 2026-07-29 deletion because
# it says "you are here" on the mounted roster, not on the dial paint.
CALENDAR_MOUNT_ALPHA = 0.65
CALENDAR_MOUNT_LIT_DELTA = 0.35
# THE CAT'S DIMMING LAW (owner spec, item 5, R12 — Blue Moon): the
# "chinese" mount's doubled-month mark while The Cat holds the center —
# well below CALENDAR_MOUNT_ALPHA (present, but visibly lending its
# month away), never zero (a vanished mark would read as a rendering
# bug, not a story).
CALENDAR_MOUNT_DIMMED_ALPHA = 0.20
