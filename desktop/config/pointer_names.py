"""What a pointer is CALLED.

Every display name the pointer family wears: the pointers' own names
in the menu and Settings, the WHEEL labels (what each pointer's
primary/secondary/tertiary wheel MEANS - the one place a wheel's
meaning is written; `config/registry/slots.py` says only that the
slot exists), and the ARM labels each wheel's arms carry.

Split from `pointer_geometry.py` on purpose: a rename is a copy
decision and a half-angle is a drawing decision, and the two change
for entirely different reasons.

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

# ═══════════════════════════ POINTER DISPLAY NAMES ═══════════════════════════
# Display names chosen by the owner (FINAL.txt #8): the internal keys
# stay hexa/cross/octa/trio (settings and code stability); the menu and
# the docs speak these.
POINTER_DISPLAY_NAMES = {
    "trio": "Trinity",
    # QUATERNITY (owner seal 2026-07-28). "Seasons" stepped down to be
    # one of this pointer's three wheels, so the pointer needed a name
    # that can hold all three — the Elements, the Temperaments and the
    # Seasons are one fourfold read three ways, and only a word for
    # four-in-one holds them without favouring any. It answers Trinity
    # across the dial: three arms there, four here.
    "cross": "Quaternity",
    "hexa": "Prism",
    "octa": "Compass",
    "aurora": "Aurora",     # no arms — the day itself painted in bands
    "calendar": "Calendar",  # no arms — the year/day in twelve wedges
    "rose": "Rose",         # three octa stars, 15° apart (CUBE.md)
}

# ═══════════════════════════ WHEEL LABELS ═══════════════════════════
# The wheel LABELS per pointer (owner 2026-07-17, ROADMAP 11; naming
# refinements 2026-07-17/19; the CUBE third wheels sealed 2026-07-26,
# CUBE.md §Double Trinity/§Character Wheel) — RAW English, the ONE table
# both the Watch Face Pointer section's palette-style row
# (`app.watch_face.pointer`, `tr()`-wrapped at build time) and the watch
# TITLE row
# (`app.skin_builder.watch_title`, untranslated — a name, not chrome)
# read (Rule #5: one source, two readers). Index 0 = "primary", index 1
# = "secondary", index 2 (where present) = "tertiary" — the slot keys
# are POSITIONAL (owner decree 2026-07-28); the MEANING of a wheel lives
# only in the name below (`palette_styles_for` tells which pointers
# carry a third).

# THE PRISM-LIGHT THEME NAME (owner seal 2026-07-27, closing the last
# open naming decision of `research/bond_theme.md`): the theme KEEPS ALL
# THREE candidate names. Wherever the theme is titled it shows the
# triple — `ONE_SOUL_THEME_TITLE`, the Encyclopedia heading — and
# wherever ONE name has to stand alone (the Design window's wheel row,
# the menus, the watch title, any label) it is `ONE_SOUL_THEME_NAME`,
# "One Soul". One declaration, both readers (Rule #5); the Aristotle
# anchor behind the pick — "one soul dwelling in two bodies" (Diogenes
# Laertius V.20) — lives in the theme's own article.
ONE_SOUL_THEME_NAME = "One Soul"
ONE_SOUL_THEME_TITLE = "One Soul — The Vow — The Bond"

POINTER_PALETTE_LABELS = {
    "trio": ("Court", "Family", "Genesis"),
    # THE QUATERNITY'S THREE (owner seal 2026-07-28): the same four arms
    # read as the body's humours, as the world's matter, and as the
    # year's quarters. Seasons comes LAST because it is the plainest
    # reading — and because the two older wheels keep the slots they
    # have always had.
    "cross": ("Temperaments", "Elements", "Seasons"),
    # WALKS, not "Walks of Life" (owner 2026-07-28): the tail was added
    # in 2026-07-19 only to kill the hereditary-caste reading, and the
    # walking metaphor does that work by itself — a walk is taken, an
    # estate is inherited. Beside Ages and Character the short form
    # cannot be misread, and the watch title stops saying "Walks of Life
    # Compass". CANON's own sealed table already read "Compass | Walks |
    # Ages".
    "octa": ("Walks", "Ages", "Character"),
    # The hexa SECONDARY slot speaks the theme's sealed single name
    # (owner 2026-07-27); its PRIMARY slot says PERSONS since the same
    # day (owner "ok."), because that wheel IS the Persons — CANON.md
    # names it so. The generic TRIPLE under "default" serves any pointer
    # with no named wheels of its own; it counts three because the slot
    # has three positions (owner 2026-07-28 — the old pair was two
    # labels for a three-state slot).
    "hexa": ("Persons", ONE_SOUL_THEME_NAME, "Council"),
    "aurora": ("Warm", "Cool"),
    "calendar": ("Zodiac", "Almanac"),
    # THE ROSE'S TWO WHEELS (owner seal 2026-07-27, CUBE.md §The Rose).
    # Both seat the SAME three sets on the same two anchors — Modern on
    # the 0° star, Historical on the −15° star — and the wheel is named
    # for where the MYTH star goes: LEGACY puts it at −30° (the deepest
    # past, everything behind the hour), PROPHECY at +15° (ahead of the
    # hour, symmetric). The hues are identical on both (the wheel turns
    # geometry and figures, not colors — the Seasons pointer already
    # serves one palette under both styles).
    "rose": ("Legacy", "Prophecy"),
    "default": ("Primary palette", "Secondary palette", "Tertiary palette"),
}

# ═══════════════════════════ ARM LABELS ═══════════════════════════
# What each palette circle COLORS (owner spec 2026-07-11: hovering a
# palette swatch in Settings names its arm position). Order matches
# PALETTE_PRESETS — clockwise from the top arm; the Compass speaks in
# cardinal directions, the others in dial positions.
POINTER_ARM_LABELS = {
    "trio": ("Top", "Right", "Left"),
    # The Genesis wheel's inverted arms (trio + "tertiary" style — the
    # settings palette editor reads this via `defaults.
    # pointer_arm_labels`): 24h bottom, 08h upper-left, 16h upper-right.
    "trio_tertiary": ("Bottom", "Left", "Right"),
    "cross": ("Top", "Right", "Bottom", "Left"),
    "hexa": (
        "Top", "Top Right", "Bottom Right",
        "Bottom", "Bottom Left", "Top Left",
    ),
    "octa": (
        "North", "North-East", "East", "South-East",
        "South", "South-West", "West", "North-West",
    ),
    # Aurora speaks in day phases: the dawn band, five day hues from
    # sunrise to sunset, the dusk band.
    "aurora": (
        "Dawn", "Morning", "Forenoon", "Noon", "Afternoon", "Evening",
        "Dusk",
    ),
    # The ROSE speaks the YEAR (CUBE.md §The Rose — the Sunday axis):
    # its four cardinals are the sun's turning points and its four
    # diagonals the season centres, landing exactly where
    # `core.year_wheel` puts them. Clockwise from 12h.
    "rose": (
        "Summer Solstice", "Summer", "Autumn Equinox", "Autumn",
        "Winter Solstice", "Winter", "Spring Equinox", "Spring",
    ),
    # Calendar wedges, clockwise from the TOP wedge. The two wheels
    # differ (Zodiac = signs from the top boundary, Almanac = months
    # from the top center), so the palette-editor labels stay NEUTRAL — the
    # ordinal position of each wedge (owner spec: the swatch names its
    # place, the wheel gives the meaning).
    "calendar": tuple(f"Wedge {index + 1}" for index in range(12)),
}
