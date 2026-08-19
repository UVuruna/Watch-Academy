"""ERA NOTATION & THIRD CALENDARS - how a year is WRITTEN.

One subject, whole: the notation the official year wears (BCE/CE or
BC/AD), the Earth-label and Z modes that choose which year form the
dial prints at all, the named eras (Anno Lucis, the Age of Light),
and the THIRD CALENDARS a user may set beside the official one -
their titles, epoch offsets, label formats and the notes the
Encyclopedia shows for each. The two coordinate ranges and the city
transliterations ride with them because they bound the same input:
WHERE and WHEN a date is being written for.

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

# ═══════════════════════════ ERA NOTATION & THIRD CALENDARS ═══════════════════════════
# Era notation (Settings, owner amendment 2026-07-17): governs ONLY the
# OFFICIAL year form's labels — "bce_ce" (default) or "bc_ad". Positive
# years render BARE ("2026", as the world writes it) unless the user
# opts into the suffix (Settings show_era_suffix); negative years ALWAYS
# carry their label ("44 BCE"). The ANNO LUCIS year is NOT a mode: it
# ALWAYS accompanies the official year in legends/hovers/the Time
# Travel header ("2026 · 6105. Anno Lucis") — see
# core.deep_time.format_year_line, the ONE pairing place.
ERA_NOTATIONS = ("bce_ce", "bc_ad")
ERA_NOTATION_TITLES = {"bce_ce": "BCE / CE", "bc_ad": "BC / AD"}

# The Earth marker's label mode (owner 2026-07-18, ROADMAP 15h — the FOUR
# exclusive Design ▸ Earth toggles, replacing the old show_earth_date/
# earth_weekday bool pair): "off" (no label), "date" ("8 Jul"), "weekday"
# ("FRI"), "date_weekday" (the date over the abbreviated weekday — the
# OLD combined "Full Date" meaning) and "full" (the date over the YEAR,
# the true Full Date, reusing the deep-travel year row's two-row shape).
EARTH_LABEL_MODES = ("off", "date", "weekday", "date_weekday", "full")

# Visibility Z modes (owner 2026-07-17, ROADMAP 15d; Settings z_mode):
# "bottom" — the clock stays BELOW every window except the desktop
# (WindowStaysOnBottomHint, the default); "top" — always ON TOP of
# everything (WindowStaysOnTopHint, a small clock the user always sees).
Z_MODES = ("bottom", "normal", "top")
Z_MODE_TITLES = {
    "bottom": "Below all windows (desktop layer)",
    "normal": "Normal window (above when focused)",
    "top": "Always on top",
}
# (current era, before era) labels per notation.
ERA_NAMES = {"bce_ce": ("CE", "BCE"), "bc_ad": ("AD", "BC")}
# ANNO LUCIS — the owner's measured world-era (SEALED 2026-07-16):
# A.L. 1 = 4079 BCE, the first year of the unbroken light era, so
# A.L. = CE + 4079 (2026 CE = A.L. 6105). Details in
# research/ephemeris/anno_lucis.json.
ANNO_LUCIS_OFFSET = 4079
ANNO_LUCIS_LABEL = "Anno Lucis"      # "6105. Anno Lucis" (owner's form)

# The Age of Light / Age of Darkness boundary (SEALED 2026-07-16, the
# doctrine research/ephemeris/anno_lucis.json measures): the current
# reigning age runs astronomical −4078…6423 inclusive (= 4079 BCE →
# 6423 CE, 10,501 unbroken years); every other covered year is the Age
# of Darkness. Owner fix-round B, 2026-07-19 (Earth hover card).
AGE_OF_LIGHT_START_YEAR = -4078
AGE_OF_LIGHT_END_YEAR = 6423

# The optional THIRD calendar on the year line (owner amendment
# 2026-07-17, Settings third_era; default none; "chinese" added owner
# fix-round B 2026-07-19 — "zašto nismo ubacili kineski"). Offsets live
# on the ASTRONOMICAL axis (1 BCE = 0), where every "CE + N" convention
# becomes a uniform +N: AUC 1 = 753 BCE = astro −752 (+753 → 1 ✓);
# Byzantine A.M. 1 = 5509 BCE (September epoch — tooltip note only);
# Hebrew A.M. counts from Tishri 3761 BCE (civil-axis convention
# CE + 3760 — tooltip note only). Anno Hegirae is LUNAR and has no
# fixed offset — displayed via the standard display-grade
# approximation AH ≈ (CE − 622) × 33/32 (core.deep_time). The Chinese
# (Huangdi) count uses the CE + 2697 convention (2026 CE → 4723) — the
# most common modern reading; sources spread 2695–2698 (the Encyclopedia's
# own "Eras of the World" article already flags the epoch drift). Kali
# Yuga (ERA-TRIO round, owner 2026-07-20) is a uniform CE + 3101 offset
# like the four above — epoch 3102 BCE = astro −3101 (the night of
# 17/18 February, Puranic tradition) — but its own Hindu luni-solar new
# year (Chaitra, in spring, not January) makes the reading ±1
# conventional near that boundary, the same class of honesty as the
# Chinese spread note above.
# THREE third eras are FORMATTERS rather than offsets, each a
# different shape: "maya" (MAYA round, owner 2026-07-20: "Jel Maje
# nisu imale kalendar?") is a TRUE DAY COUNT from a fixed epoch (no
# year concept at all) — `core.deep_time.maya_long_count` walks the
# real calendar date's Julian Day Number. "unix" (ERA-TRIO round) is
# likewise a day/second count, not a year — seconds since the Unix
# epoch (1970-01-01 00:00 UTC) at the displayed date's OWN midnight UTC
# — `core.deep_time.unix_epoch_seconds`. "olympiad" (ERA-TRIO round)
# needs only the YEAR, like the offset eras, but is not a uniform "CE +
# N": it is a 4-year CYCLE count from the first Olympiad (776 BCE,
# astro −775) — `core.deep_time.olympiad_year`. None of the three has a
# THIRD_ERA_OFFSETS entry and none is handled by `third_era_year` —
# `format_year_line` special-cases all three branches.
THIRD_ERAS = (
    "none", "auc", "byzantine", "hebrew", "hegirae", "chinese", "maya",
    "kali", "olympiad", "unix",
)
THIRD_ERA_TITLES = {
    "none": "None",
    "auc": "Ab Urbe Condita (Rome)",
    "byzantine": "Byzantine Anno Mundi",
    "hebrew": "Hebrew Anno Mundi",
    "hegirae": "Anno Hegirae (Islamic)",
    "chinese": "Huangdi (China)",
    "maya": "Maya Long Count",
    "kali": "Kali Yuga (Hindu)",
    "olympiad": "Olympiad (Ancient Greece)",
    "unix": "Unix Epoch (Computing)",
}
THIRD_ERA_OFFSETS = {
    "auc": 753, "byzantine": 5509, "hebrew": 3760, "chinese": 2697,
    "kali": 3101,
}
THIRD_ERA_LABELS = {
    "auc": "AUC",
    "byzantine": "Byzantine A.M.",
    "hebrew": "Hebrew A.M.",
    "hegirae": "AH",
    "chinese": "Huangdi",
    "maya": "Long Count",
    "kali": "Kali Yuga",
    # "olympiad"/"unix" embed their own label mid-string rather than
    # appending it (their display shape differs from every offset
    # era's "value. LABEL" — see `core.deep_time.olympiad_year`/
    # `format_year_line`'s unix branch) — kept here anyway (Rule #4)
    # so the words themselves stay data, not a second hardcoded copy.
    "olympiad": "Olympiad",
    "unix": "Unix",
}
# Epoch fine print for the Settings combo tooltips (owner amendment:
# tooltip only, never on the year line).
THIRD_ERA_NOTES = {
    "byzantine": "Year starts 1 September (5509 BCE epoch).",
    "hebrew": "Year starts at Tishri (autumn); civil convention CE + 3760.",
    "hegirae": "Lunar years — displayed via the AH ≈ (CE − 622) × 33/32 "
               "approximation; exact AH needs lunisolar math.",
    "chinese": "Continuous count from the Yellow Emperor's reign — "
               "sources spread 2695–2698 BCE; this dial uses CE + 2697.",
    "maya": "A true day count (baktun.katun.tun.uinal.kin), not a year "
            "offset — GMT correlation epoch 11 Aug 3114 BCE; 21 Dec 2012 "
            "was 13.0.0.0.0, a cycle rolling over, not an ending.",
    "kali": "The fourth and current age of Hindu cosmology — epoch "
            "3102 BCE; the Chaitra (spring) new year makes CE + 3101 a "
            "±1 approximation near the boundary.",
    "olympiad": "A 4-year cycle from the first Games, 776 BCE; the "
                "historical midsummer games-boundary is approximated "
                "by the calendar year.",
    "unix": "Seconds since 1970-01-01 00:00 UTC, read at this date's "
            "own midnight UTC — a day-level count, not the exact "
            "instant.",
}
# The Maya Long Count's GMT correlation constant (Goodman-Martinez-
# Thompson, the most widely accepted): Julian Day Number 584,283 =
# Long Count 0.0.0.0.0 = 11 August 3114 BCE proleptic Gregorian (6
# September 3114 BCE Julian). `core.deep_time.maya_long_count` golden-
# tested against two independently known, mutually consistent anchors
# (tests/test_deep_time.py): 21 Dec 2012 = 13.0.0.0.0, 1 Jan 2000 =
# 12.19.6.15.2.
MAYA_EPOCH_JDN = 584283
# The Olympiad's own epoch (ERA-TRIO round, owner 2026-07-20): the
# first Olympiad's Games, summer 776 BCE = astronomical year −775
# (`core.deep_time.astro_from_display`: 1 − 776 = −775). Golden-tested
# against a second, independent anchor: the classical chronographers'
# own running count reached the 293rd Olympiad in 393 CE, the
# conventional date of the last ancient Games under Theodosius I —
# `core.deep_time.olympiad_year` reproduces that number exactly from
# this same epoch (tests/test_deep_time.py).
OLYMPIAD_EPOCH_YEAR = -775

# The 400-year proleptic-Gregorian cycle (146,097 days — exactly 20,871
# weeks): shifting a moment by whole cycles preserves leap structure,
# weekdays and all intervals, which is what lets datetime (years 1-9999)
# carry Deep Time moments. Proxy years land in [PROXY_WINDOW_FIRST,
# PROXY_WINDOW_FIRST + GREGORIAN_CYCLE_YEARS) — opened at 2000 for
# modern tzdata rules and the sun model's reference era.
GREGORIAN_CYCLE_YEARS = 400
PROXY_WINDOW_FIRST = 2000

# --- Geography -------------------------------------------------------------------
LATITUDE_RANGE = (-90.0, 90.0)
LONGITUDE_RANGE = (-180.0, 180.0)

# City-name folding for search: NFKD decomposition strips most diacritics
# (š, č, ž, ü, ...) but NOT these single-codepoint letters — the bundled
# city names are ASCII transliterations, so native spellings must fold to
# match ("Tromsø" -> "tromso", "Đakovica" -> "dakovica").
CITY_NAME_TRANSLITERATIONS = {
    "ø": "o",
    "đ": "d",
    "ł": "l",
    "æ": "ae",
    "œ": "oe",
    "ß": "ss",
    "þ": "th",
    "ð": "d",
}
