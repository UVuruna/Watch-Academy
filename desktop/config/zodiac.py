"""ZODIAC & CHINESE CALENDAR - the two sign systems.

Both answer the same question - "which sign is this instant in" -
and both are ridden by the same seats (the calendar mounts, the South
slot, the ascendant readout), so they were one section and stay one
module: the twelve Chinese animals and five elements with their
new-year window and the branch terms that bound each month, the
twelve western signs and their span, THE THIRTEENTHS (Ophiuchus and
Sol, the signs a thirteen-seat mount adds) with the axle rule and
their windows.

The WEDGES they ride are geometry and live in
`config/calendar_mounts.py`; the STYLES a slot draws them in live in
`config/complications.py`.

Born 2026-08-19, when the owner ruled that `config/constants.py`'s
**38 top-level sections** were a junk drawer, not a directory, and gave
the split its module names himself. Nothing here is new data - every
table below stood in `constants.py` under its own section banner and
moved WHOLE, with its comments; the callers were repointed, and no
re-export shim was left behind (`rules/CODE.md` - No backward
compatibility). The whole map, one row per module, is in
[the folder doc](___config.md).

Layer: config - pure Python, no Qt, no wall clock, no sibling import.
"""

# ═══════════════════════════ ZODIAC & CHINESE CALENDAR ═══════════════════════════
# Chinese zodiac (sexagenary cycle): the animal repeats every 12 years,
# the element every 10 (two years per element). Year N maps via
# (N - 4) % 12 and ((N - 4) % 10) // 2 — 2026 = Fire Horse. The Chinese
# year starts at the new moon falling between Jan 21 and Feb 20 (China
# time), derived from the bundled principal-phase instants.
CHINESE_ANIMALS = (
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig",
)
CHINESE_ELEMENTS = ("Wood", "Fire", "Earth", "Metal", "Water")
CHINESE_NEW_YEAR_WINDOW = ((1, 21), (2, 20))   # (month, day) bounds, China time
CHINA_UTC_OFFSET_HOURS = 8

# THE CHINESE MONTH-BRANCH ANIMALS (owner R12, "Mount Chinese zodiac"):
# the traditional solar-term month branches — Yin (Tiger) begins at
# lichun (start of spring, ~Feb 4) and each subsequent branch begins at
# the next "jie" solar term, ~30 days apart; Zi (Rat) begins at daxue
# (~Dec 7) and so holds the December solstice, which is why the
# classical calendar calls that lunar month "the eleventh"
# (core.blue_moon.chinese_leap_month reads the SAME fact). Each solar
# term's start nearly always falls in the FIRST week of its Gregorian
# month, so — exactly like calendar_mounts.SLAVIC_MONTHS mounts by Gregorian
# month rather than by the true (locally-drifting) bloom date — this
# table fixes ONE animal per Gregorian month for the static 12-wedge
# mount; the LIVE lunar month (core.moon.chinese_zodiac) is unaffected.
CHINESE_MONTH_BRANCH_ANIMALS = {
    1: "Ox", 2: "Tiger", 3: "Rabbit", 4: "Dragon", 5: "Snake", 6: "Horse",
    7: "Goat", 8: "Monkey", 9: "Rooster", 10: "Dog", 11: "Pig", 12: "Rat",
}
# THE BRANCH'S TRUE SPAN (owner 2026-08-05: "na hoveru će stajati tačan
# datum od kad do kad"). A branch does NOT run from the 1st to the 31st:
# it opens on its own "jie" solar term and closes the day before the
# next one. Gregorian month -> (month, day, the term's name) of the day
# it OPENS; the CLOSE is computed as the day before the next branch's
# term (`chinese_branch_span`), so the twelve can never disagree about
# a boundary.
#
# The dates are the traditional Gregorian ones and drift by about a day
# with the leap cycle — which is why the hover says "approx." and why
# the MOUNT itself stays keyed to the Gregorian month (the wedge is a
# fixed seat; only the words are the astronomy).
CHINESE_BRANCH_TERMS = {
    1: (1, 6, "Xiaohan"),      # Minor Cold — the Ox
    2: (2, 4, "Lichun"),       # Start of Spring — the Tiger opens the cycle
    3: (3, 6, "Jingzhe"),      # Awakening of Insects — the Rabbit
    4: (4, 5, "Qingming"),     # Clear and Bright — the Dragon
    5: (5, 6, "Lixia"),        # Start of Summer — the Snake
    6: (6, 6, "Mangzhong"),    # Grain in Ear — the Horse
    7: (7, 7, "Xiaoshu"),      # Minor Heat — the Goat
    8: (8, 8, "Liqiu"),        # Start of Autumn — the Monkey
    9: (9, 8, "Bailu"),        # White Dew — the Rooster
    10: (10, 8, "Hanlu"),      # Cold Dew — the Dog
    11: (11, 7, "Lidong"),     # Start of Winter — the Pig
    12: (12, 7, "Daxue"),      # Major Snow — the Rat, which is why the
                               # classical calendar calls that lunar
                               # month "the eleventh"
}

def chinese_branch_span(month: int) -> tuple[tuple[int, int], tuple[int, int], str]:
    """((open month, open day), (close month, close day), term name) of
    one branch — the close is the day before the NEXT branch's term, so
    the twelve tile the year with no gap and no overlap."""
    open_month, open_day, term = CHINESE_BRANCH_TERMS[month]
    next_month, next_day, _next_term = CHINESE_BRANCH_TERMS[month % 12 + 1]
    if next_day > 1:
        close = (next_month, next_day - 1)
    else:                       # a term on the 1st closes the month before
        close = ((next_month - 2) % 12 + 1, 28)
    return (open_month, open_day), close, term

# Tropical zodiac: (name, symbol), indexed by dial angle // 30 on the
# year wheel — Cancer's first point IS the summer solstice (dial top),
# Capricorn's the winter solstice (bottom), Aries' the spring equinox.
# Sign boundaries are exact 30-deg arcs of the same piecewise-linear
# year wheel, i.e. anchored on the REAL season instants.
ZODIAC_SIGNS = (
    ("Cancer", "♋"),
    ("Leo", "♌"),
    ("Virgo", "♍"),
    ("Libra", "♎"),
    ("Scorpio", "♏"),
    ("Sagittarius", "♐"),
    ("Capricorn", "♑"),
    ("Aquarius", "♒"),
    ("Pisces", "♓"),
    ("Aries", "♈"),
    ("Taurus", "♉"),
    ("Gemini", "♊"),
)
ZODIAC_SPAN_DEG = 30.0

# --- THE BLUE MOON LAW (owner-sealed 2026-07-22) ------------------------------
# The 13th member of every 12-set — hidden except in a blue-moon year
# (core.blue_moon.thirteen_moon_year: the calendar year holds 13 Full
# Moons, ~37% of years) AND inside its own short date window. `key` ->
# (display name, encyclopedia family, encyclopedia entry name) — the
# SAME two-level lookup WEEKDAY_THEME_NINTHS uses for its (name, path),
# read by both the dial (render.ninths.thirteenth_plate) and its hover
# (render.compositor). "chinese" (The Cat) is NOT solar-triggered — see
# core.blue_moon.chinese_leap_month — it shares this table only because
# it shares the CENTER seat.
#
# THE AXLE LAW (CANON.md §The Axle, owner-sealed 2026-07-29) extends this
# SAME table with the ALWAYS-CENTERS — Hestia/Jesus/Prudence/Cunning/
# Peace/Hardness of Heart — the throne/hiding-place axles of the
# Olympians, Apostles, Virtue Wheel (both registers), Emotions and Sins
# Dozens. (Named `PERSON_CENTERS` on 2026-07-29 and RENAMED the same
# day: Peace and Hardness of Heart are STATES, not persons — the seam
# THE AXLE LAW draws is "not a leftover month", never personhood.)
# Unlike the four members above,
# they carry NO year-rule at all: `AXLE_ALWAYS_CENTERS` below marks them
# unconditionally present (core.blue_moon.thirteenth_candidates unions it
# in, never gated by a trigger+window). `family`/`article` are `None`
# where no Encyclopedia article has been written yet (Hestia alone
# already has one, under "wider" — the A-list pantheon figures written
# for exactly this axle story) — a caller reading THIRTEENTHS must treat
# `None` the SAME graceful-absent way a missing art plate is treated
# (render.compositor._thirteenth_tooltip skips the encyclopedia lookup
# entirely rather than crash on an unwritten entry).
THIRTEENTHS = {
    "ophiuchus": ("Ophiuchus", "ninths", "Ophiuchus"),
    "chinese": ("The Cat", "ninths", "The Cat"),
    "sol": ("Sol", "months", "Sol"),
    "modrenik": ("Modrenik", "months", "Modrenik"),
    "hestia": ("Hestia", "wider", "Hestia"),
    "jesus": ("Jesus", None, None),
    "prudence": ("Prudence", None, None),
    "cunning": ("Cunning", None, None),
    "peace": ("Peace", None, None),
    "hardness_of_heart": ("Hardness of Heart", None, None),
}
# THE AXLE LAW's ALWAYS-PRESENT half (CANON §The Axle: "ALWAYS-CENTERS
# stand on EVERY date... no moon count, no window") — every key here is
# unconditionally a member of `core.blue_moon.thirteenth_candidates` on
# every date, regardless of year or window, unlike the four calendar-
# driven keys above (whose sealed year-rules are untouched by this set).
AXLE_ALWAYS_CENTERS = frozenset({
    "hestia", "jesus", "prudence", "cunning", "peace", "hardness_of_heart",
})
# Year-agnostic (month, day) bounds, inclusive both ends — core.blue_moon
# stamps the trigger year on. Ophiuchus: the astronomical transit (the
# Sun's real path through the constellation, Nov 29 - Dec 17). Sol:
# carries the June solstice (International Fixed Calendar's Year Day
# analogue — CANON's "the Sun's thirteenth at the year's top").
OPHIUCHUS_WINDOW = ((11, 29), (12, 17))
SOL_WINDOW = ((6, 18), (7, 15))
# Modrenik has no fixed calendar dates — it is computed FROM the real
# December solstice instant (core.year_wheel.YearAnchors), this many
# days either side ("CANON's the Moon's thirteenth at the year's
# bottom" — honest across years, unlike a fixed MM-DD pair).
MODRENIK_WINDOW_HALF_DAYS = 14
