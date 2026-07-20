"""Deep Time calendar mathematics (Session 16, owner 2026-07-17).

Era notation formatting (the ONE dual-calendar formatter), the
astronomical-year convention (1 BCE = year 0), the 400-year Gregorian
PROXY mapping that lets datetime (years 1-9999) carry moments across
the −13000…+17000 span, the proleptic-Gregorian Julian Day, and the
Espenak & Meeus 2006 ΔT model.

The proxy mapping is EXACT: the proleptic Gregorian calendar repeats
every 400 years (146,097 days = 20,871 weeks), so shifting instants by
whole cycles preserves leap structure, weekdays and every interval
between equally-shifted instants — the dial's interpolations run on
proxies and produce identical results.
"""

import math
from datetime import datetime

from config import constants


# --- Era notation (owner amendment 2026-07-17) --------------------------------


def format_official(
    astro_year: int, notation: str, show_suffix: bool = False
) -> str:
    """The OFFICIAL year form: positive years bare ("2026", as the
    world writes it) unless `show_suffix` opts the label in; negative
    years ALWAYS carry it ("44 BCE"/"44 BC" per the notation)."""
    if notation not in constants.ERA_NAMES:
        raise ValueError(f"unknown era notation: {notation!r}")
    current, before = constants.ERA_NAMES[notation]
    if astro_year >= 1:
        return f"{astro_year} {current}" if show_suffix else str(astro_year)
    return f"{1 - astro_year} {before}"


def format_anno_lucis(astro_year: int) -> str:
    """Just the Anno Lucis half of the year line — "6105. Anno Lucis"
    (owner sealed 2026-07-16: A.L. = astronomical year + 4079). The
    Earth hover card's own era block reuses this directly;
    `format_year_line` reuses it too, so the form is derived ONCE."""
    return (
        f"{astro_year + constants.ANNO_LUCIS_OFFSET}. "
        f"{constants.ANNO_LUCIS_LABEL}"
    )


def format_year_line(
    astro_year: int,
    notation: str,
    show_suffix: bool = False,
    third_era: str = "none",
    month: int = 1,
    day: int = 1,
) -> str:
    """THE year line (owner amendment 2026-07-17, ONE pairing place):
    the Anno Lucis year ALWAYS accompanies the official year —
    "2026 · 6105. Anno Lucis" — and the optional third calendar joins
    the line ("… · 2779. AUC"). Every legend/hover/dialog-header year
    renders through here.

    `month`/`day` matter ONLY for "maya" (MAYA round, owner 2026-07-20):
    the Long Count is a true day count, not a year offset, so it needs
    the full displayed date — every caller whose `third_era` can be
    "maya" MUST pass the real calendar date. Every other era ignores
    them, so the 1 Jan default keeps their call sites/tests unchanged."""
    parts = [
        format_official(astro_year, notation, show_suffix),
        format_anno_lucis(astro_year),
    ]
    if third_era == "maya":
        parts.append(
            f"{maya_long_count(astro_year, month, day)}. "
            f"{constants.THIRD_ERA_LABELS['maya']}"
        )
    elif third_era != "none":
        parts.append(
            f"{third_era_year(astro_year, third_era)}. "
            f"{constants.THIRD_ERA_LABELS[third_era]}"
        )
    return " · ".join(parts)


def is_age_of_light(astro_year: int) -> bool:
    """True within the sealed Age of Light span — 4079 BCE → 6423 CE,
    astronomical −4078…6423 (research/ephemeris/anno_lucis.json,
    ROADMAP 15a3) — else the Age of Darkness (dark otherwise within
    this dial's coverage, owner sealed 2026-07-16)."""
    return (
        constants.AGE_OF_LIGHT_START_YEAR
        <= astro_year
        <= constants.AGE_OF_LIGHT_END_YEAR
    )


def third_era_year(astro_year: int, third_era: str) -> int:
    """The third calendar's year of an astronomical year. The offset
    eras are uniform +N on the astronomical axis; Anno Hegirae is
    LUNAR — the standard display-grade approximation
    AH ≈ (CE − 622) × 33/32 (exact AH needs lunisolar month math,
    documented in constants.THIRD_ERA_NOTES). NOT called for "maya" —
    the Long Count is a day count, not a year offset; see
    `maya_long_count`/`format_year_line`."""
    if third_era == "hegirae":
        return round((astro_year - 622) * 33 / 32)
    return astro_year + constants.THIRD_ERA_OFFSETS[third_era]


def maya_long_count(astro_year: int, month: int, day: int) -> str:
    """The TRUE Maya Long Count (MAYA round, owner 2026-07-20) — a pure
    day count from the GMT correlation epoch (Julian Day Number
    584,283 = 11 August 3114 BCE proleptic Gregorian, 6 September
    3114 BCE Julian; `constants.MAYA_EPOCH_JDN`), radix
    baktun(144000 days)/katun(7200)/tun(360)/uinal(20)/kin(1 day).
    Unlike every other THIRD_ERA this is not a year offset, so it
    needs the full displayed DATE, not just the year — `julian_day`
    with `day_fraction=0.5` (noon) lands exactly on the integer JDN
    (the same trick `julian_day_of`/the eclipse lookups already lean
    on). Golden-tested against two independently known, mutually
    consistent anchors (tests/test_deep_time.py): 21 Dec 2012 =
    13.0.0.0.0, 1 Jan 2000 = 12.19.6.15.2 — cross-checked against the
    2012 anchor via plain `datetime.date` subtraction, agrees exactly."""
    days = int(julian_day(astro_year, month, day, 0.5)) - constants.MAYA_EPOCH_JDN
    baktun, days = divmod(days, 144000)
    katun, days = divmod(days, 7200)
    tun, days = divmod(days, 360)
    uinal, kin = divmod(days, 20)
    return f"{baktun}.{katun}.{tun}.{uinal}.{kin}"


def era_names(notation: str) -> tuple[str, str]:
    """(current era, before era) combo labels of a notation."""
    if notation not in constants.ERA_NAMES:
        raise ValueError(f"unknown era notation: {notation!r}")
    return constants.ERA_NAMES[notation]


def display_from_astro(astro_year: int) -> tuple[int, int]:
    """(display_year, era_index) for the moment editor: era_index 0 =
    the current era (CE/AD), 1 = the before era (BCE/BC) — 1 BCE is
    year 0."""
    if astro_year >= 1:
        return astro_year, 0
    return 1 - astro_year, 1


def astro_from_display(display_year: int, era_index: int) -> int:
    """Inverse of display_from_astro — 1 BCE maps to year 0."""
    return display_year if era_index == 0 else 1 - display_year


# --- The 400-year proxy mapping ----------------------------------------------


def proxy_cycles(astro_year: int) -> int:
    """Whole 400-year cycles to ADD to `astro_year` so the year AND
    both neighbors are datetime-representable. 0 for 2…9998 (the
    season anchors reach one year past the target, so 1 and 9999 must
    shift too); otherwise into the canonical window."""
    if 2 <= astro_year <= 9998:
        return 0
    first = constants.PROXY_WINDOW_FIRST
    cycle = constants.GREGORIAN_CYCLE_YEARS
    if astro_year < 2:
        return math.ceil((first - astro_year) / cycle)
    last = first + cycle - 1
    return -math.ceil((astro_year - last) / cycle)


def canonical_proxy(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0
) -> tuple[datetime, int]:
    """(naive proxy datetime, cycles) of an astronomical calendar
    moment — the canonical frame every deep simulation runs in."""
    cycles = proxy_cycles(year)
    return (
        datetime(
            year + cycles * constants.GREGORIAN_CYCLE_YEARS,
            month, day, hour, minute,
        ),
        cycles,
    )


def real_year(proxy_year: int, cycles: int) -> int:
    """The astronomical year of a proxy datetime's year."""
    return proxy_year - cycles * constants.GREGORIAN_CYCLE_YEARS


# --- Proleptic-Gregorian helpers ---------------------------------------------


def is_leap(astro_year: int) -> bool:
    """Proleptic Gregorian, negative-year-safe (year 0 IS leap)."""
    return astro_year % 4 == 0 and (
        astro_year % 100 != 0 or astro_year % 400 == 0
    )


def month_length(astro_year: int, month: int) -> int:
    if month == 2:
        return 29 if is_leap(astro_year) else 28
    return (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[month - 1]


def shift_calendar(
    year: int, month: int, day: int, *, years: int = 0, months: int = 0
) -> tuple[int, int, int]:
    """Quick-jump unit arithmetic (owner slika 12): move by whole
    years or months in astronomical space (no year-0 gap), clamping the
    day to the target month's length (Feb 29 → Feb 28 on a non-leap
    target). Day jumps use plain timedelta on the proxy instead."""
    total = year * 12 + (month - 1) + months + years * 12
    target_year, target_month = divmod(total, 12)
    target_month += 1
    return target_year, target_month, min(day, month_length(target_year, target_month))


def julian_day(year: int, month: int, day: int, day_fraction: float = 0.0) -> float:
    """Proleptic-Gregorian Julian Day (Meeus 7.1 with floor — valid for
    negative years). `day_fraction` is the fraction of the UT day."""
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    return (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day + b - 1524.5 + day_fraction
    )


def julian_day_of(when: datetime, cycles: int = 0) -> float:
    """Julian Day (UT) of a tz-aware moment, un-shifting the proxy
    frame first — the deep pack's eclipse ordering key."""
    from datetime import timezone as _tz

    utc = when.astimezone(_tz.utc)
    return julian_day(
        real_year(utc.year, cycles), utc.month, utc.day,
        (utc.hour * 3600 + utc.minute * 60 + utc.second) / 86400.0,
    )


# --- ΔT (Espenak & Meeus 2006) -----------------------------------------------


def delta_t_seconds(year: float) -> float:
    """TT − UT in seconds — the published Espenak & Meeus 2006
    piecewise polynomials. Measured against the Swiss Ephemeris model
    over the pack (2026-07-17): within minutes in the bundled era,
    within ~4 h at the −13000/+17000 edges — part of the deep
    illumination tolerance, documented in the precision tiers."""
    y = year
    if y < -500 or y >= 2150:
        u = (y - 1820) / 100
        return -20 + 32 * u * u
    if y < 500:
        u = y / 100
        return (10583.6 - 1014.41 * u + 33.78311 * u**2 - 5.952053 * u**3
                - 0.1798452 * u**4 + 0.022174192 * u**5 + 0.0090316521 * u**6)
    if y < 1600:
        u = (y - 1000) / 100
        return (1574.2 - 556.01 * u + 71.23472 * u**2 + 0.319781 * u**3
                - 0.8503463 * u**4 - 0.005050998 * u**5 + 0.0083572073 * u**6)
    if y < 1700:
        t = y - 1600
        return 120 - 0.9808 * t - 0.01532 * t**2 + t**3 / 7129
    if y < 1800:
        t = y - 1700
        return (8.83 + 0.1603 * t - 0.0059285 * t**2 + 0.00013336 * t**3
                - t**4 / 1174000)
    if y < 1860:
        t = y - 1800
        return (13.72 - 0.332447 * t + 0.0068612 * t**2 + 0.0041116 * t**3
                - 0.00037436 * t**4 + 0.0000121272 * t**5
                - 0.0000001699 * t**6 + 0.000000000875 * t**7)
    if y < 1900:
        t = y - 1860
        return (7.62 + 0.5737 * t - 0.251754 * t**2 + 0.01680668 * t**3
                - 0.0004473624 * t**4 + t**5 / 233174)
    if y < 1920:
        t = y - 1900
        return (-2.79 + 1.494119 * t - 0.0598939 * t**2 + 0.0061966 * t**3
                - 0.000197 * t**4)
    if y < 1941:
        t = y - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    if y < 1961:
        t = y - 1950
        return 29.07 + 0.407 * t - t**2 / 233 + t**3 / 2547
    if y < 1986:
        t = y - 1975
        return 45.45 + 1.067 * t - t**2 / 260 - t**3 / 718
    if y < 2005:
        t = y - 2000
        return (63.86 + 0.3345 * t - 0.060374 * t**2 + 0.0017275 * t**3
                + 0.000651814 * t**4 + 0.00002373599 * t**5)
    if y < 2050:
        t = y - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t**2
    # 2050-2150: the long parabola blended toward the modern fit.
    u = (y - 1820) / 100
    return -20 + 32 * u * u - 0.5628 * (2150 - y)
