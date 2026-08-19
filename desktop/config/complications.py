"""THE SOUTH SLOT and what it may show.

A complication is a small reading the dial carries beside the time.
This module holds the vocabulary of the dial slots' CONTENT - which
modes the South ("octa") slot and the weekday slot may be set to,
the titles those modes wear in the menu, the three seat angles a
slot's content is hung from, the zodiac and chinese slot styles with
their art directories, and the Earth marker's own style list.

The neighbouring `config/registry/slots.py` answers a different
question - WHICH `Settings` field each of the three slots stores its
answers in. This module answers what the answers may BE.

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

# ═══════════════════════════ SOUTH SLOT & COMPLICATIONS ═══════════════════════════
# The SOUTH SLOT (menu name; the internal octa_* keys stay for settings
# and code stability, like the pointer keys): user-selected info near
# the dial bottom. On the Compass it IS the reserved bottom arm; the
# Trinity always has room at the south gap between its blue and red
# diamonds; Aurora always shows it (images only); Prism and Seasons
# gain it once the Weekday element is off (owner matrix 2026-07-12).
# The four image modes draw the owner's PNG art
# (assets/calendars/<dir>) and fall back to the text form until the art
# exists (documented fallback).
# COMPOSITE model (owner 2026-07-12): a top-level MODE plus a per-
# family STYLE dropdown — Astrology picks sign/logo/constellation/text
# ("colored" joins when the owner's art lands), the Chinese zodiac
# picks text/colored/gold/silver/bronze (the metals run the selective
# swap on the bronze logo, colored uses the fresh full-color badges).
# "ascendant" (owner request 2026-07-12): the RISING sign right now —
# the natal podznak, cycling through all twelve signs daily; it wears
# the zodiac styles through its own ascendant_style dropdown.
# "weekday" in the INFO slot (owner 2026-07-12): a SECOND weekday body
# — its own theme via info_slot_theme — so the pinned pair can read
# e.g. Norse left, Greek right, both showing today.
# "seconds" (owner 2026-07-14): a SMALL-SECONDS complication — the
# active hand set's seconds hand rotating inside the subdial (the big
# Elements seconds hand yields while a slot shows it).
OCTA_SLOT_MODES = (
    "time", "date", "day_length", "seconds", "weekday", "zodiac",
    "ascendant", "chinese",
)
# The DAY SLOT can carry an astrology badge instead of the bodies
# (owner 2026-07-12) — in the PINNED layouts (Aurora, or the Pointer
# element off): it stands at the usual bottom spot, so the pair can
# read official sign left, ascendant right. Elsewhere the bodies rule.
WEEKDAY_SLOT_MODES = (
    "weekday", "time", "date", "day_length", "seconds", "zodiac",
    "ascendant", "chinese",
)
# Display titles for the four COMPLICATION modes (owner spec) — the ONE
# table both the (retired) menu's Complications dropdown and the new
# Slot Theme window's own tab read (Rule #5). "weekday"/"zodiac"/
# "ascendant"/"chinese" are not complications — they get their own
# picker (the Weekday grid / the zodiac-style / Chinese-style groups).
SLOT_COMPLICATION_TITLES = {
    "time": "Digital Time",
    "date": "Date",
    "day_length": "Day length",
    "seconds": "Seconds",
}
# SLOT SEATS (owner matrix 2026-07-14): the fixed dial angles the
# multi-slot layouts use — the top (12h), the 20h/4h arm pair (the
# Trinity/Prism red and blue arms) and the 21h/3h between-arms pair;
# 24h (SOUTH_SLOT_ANGLE) hosts a lone pinned slot. Seats ride the
# star's rotation.
SLOT_SEAT_TOP_ANGLE = 0.0
SLOT_SEAT_RIGHT_ARM_ANGLE = 120.0      # the 20h arm (red on paint)
SLOT_SEAT_LEFT_ARM_ANGLE = 240.0       # the 4h arm (blue on paint)
ZODIAC_SLOT_STYLES = ("sign", "logo", "constellation", "text", "colored")
CHINESE_SLOT_STYLES = ("text", "colored", "gold", "silver", "bronze")
# Each SLOT carries its OWN style (owner 2026-07-12: the shared
# per-family fields collapsed both slots onto one look) — one value
# from either family's set, interpreted per the active family.
SLOT_STYLE_VALUES = tuple(dict.fromkeys(
    ZODIAC_SLOT_STYLES + CHINESE_SLOT_STYLES
))
# style -> art folder under assets/calendars/ (text styles draw no art).
# Family/variant tree (owner restructure 2026-07-14): astrology's
# plain logo is its PRIMARY variant.
ZODIAC_STYLE_ART_DIRS = {
    "sign": "zodiac/astrology/primary/sign",
    "logo": "zodiac/astrology/primary/logo",
    "constellation": "zodiac/astrology/primary/constellation",
    "colored": "zodiac/astrology/primary/colored",
}
CHINESE_STYLE_ART_DIRS = {
    "colored": "zodiac/chinese/primary/colored",
    "gold": "zodiac/chinese/primary/bronze",
    "silver": "zodiac/chinese/primary/bronze",
    "bronze": "zodiac/chinese/primary/bronze",
}

# ═══════════════════════════ EARTH MARKER STYLE ═══════════════════════════
# Earth marker style: the owner ships every continent in a clean and an
# atmosphere version.
EARTH_STYLES = ("clean", "atmo")
