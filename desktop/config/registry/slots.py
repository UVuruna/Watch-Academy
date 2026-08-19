"""THE SLOT REGISTRY — every SLOT the dial has, of both kinds.

The word "slot" names two different things on this dial, and both are
declared here so a reader finds the whole vocabulary in one place:

  * **the three DIAL slots** — the seats that carry content beside the
    time, each with the `Settings` field it keeps its content, look,
    theme, roster, names and enablement in (below);
  * **the three WHEEL slots** — primary / secondary / tertiary, the rows
    a pointer's palette carries, and the arm offsets two of those wheels
    seat their arms by (added 2026-08-19 by THE CONSTANTS SPLIT, the
    owner's map: they were "WHEEL SLOTS" and "WHEEL ARM OFFSETS" in the
    38-section `config/constants.py` junk drawer).

What a wheel MEANS is not here — that is `config/pointer_names.py`'s
`POINTER_PALETTE_LABELS`, the one place a wheel's meaning is written.
What a dial slot's content may BE is `config/complications.py`.

The dial carries three slots. They behave IDENTICALLY — pick a content
mode, pick that mode's style, pick a weekday theme (which is also how
you switch the slot INTO weekday display), pick a roster, show or hide
the names — and the only thing that differs between them is which
`Settings` field each answer is stored in. Those field names were never
written down anywhere: they were inlined, three at a time, into a
per-slot `if index == 1: ... if index == 2: ...` chain and into two
setter methods whose bodies the OOP audit of 2026-08-18 measured as
identical but for four strings (clones C4 and C6).

So the field names are the data, and one setter serves all three.

The names are historical and deliberately NOT renamed: slot 1 is the
weekday/day slot, slot 2 the "octa"/info slot, slot 3 the third slot,
because that is what the stored settings files on owners' disks say and
a rename here would silently reset everyone's dial.

Layer: config — pure data, imports nothing.
"""

# ═══════════════════════════ THE THREE SLOTS ═══════════════════════════
#
# One entry per slot, keyed by the 1-based index the shortcuts, the menu
# and the Watch Face window all address a slot by (Ctrl+1/2/3).
#
#   title    — how the slot names itself in the UI
#   mode     — WHAT it shows (weekday bodies, a complication, ...)
#   style    — that content's own look, independent of the other slots
#   theme    — the weekday theme it wears
#   roster   — which cast of that theme
#   names    — whether the seat names are drawn
#   enabled  — whether the slot is shown at all
#
# `names` is deliberately SHARED between slots 2 and 3
# (`show_info_slot_names`): the two info slots have always drawn their
# names together, and splitting them is a product decision nobody made.
SLOT_KEYS: dict[int, dict[str, str]] = {
    1: {
        "title": "1st Slot",
        "mode": "weekday_slot",
        "style": "day_slot_style",
        "theme": "weekday_theme",
        "roster": "weekday_roster",
        "names": "show_weekday_names",
        "enabled": "show_weekday",
    },
    2: {
        "title": "2nd Slot",
        "mode": "octa_slot",
        "style": "info_slot_style",
        "theme": "info_slot_theme",
        "roster": "info_slot_roster",
        "names": "show_info_slot_names",
        "enabled": "show_octa_slot",
    },
    3: {
        "title": "3rd Slot",
        "mode": "third_slot",
        "style": "third_slot_style",
        "theme": "third_slot_theme",
        "roster": "third_slot_roster",
        "names": "show_info_slot_names",
        "enabled": "show_third_slot",
    },
}

# ═══════════════════════════ WHEEL SLOTS ═══════════════════════════
# The WHEEL SLOTS a pointer's palette row can hold. The keys are
# POSITIONAL and carry NO meaning of their own (owner decree
# 2026-07-28, closing the "paint"/"light" era: those two words named a
# subtractive-vs-additive distinction that stopped being true the moment
# the slots started carrying the Zodiac, the Persons, the Walks of Life
# and the Rose's Legacy). A wheel's MEANING lives in exactly one place —
# `POINTER_PALETTE_LABELS` above. The third slot exists ONLY on the
# pointers `palette_styles_for` names; everywhere else a stored
# "tertiary" normalizes back to "primary"
# (`palette.effective_palette_style`).
PALETTE_STYLES = ("primary", "secondary", "tertiary")
# The pointers whose wheel row carries a THIRD wheel: trio — Genesis
# (the creation trio, drawn INVERTED); cross — Seasons (owner seal
# 2026-07-28, the wheel the pointer used to be named after); hexa —
# Council (all six Double-Trinity offices); octa — Character (the Cube
# at depth zero), CUBE.md. The law is the arm count: the pointers that
# draw 3, 4, 6 or 8 arms carry three wheels; the armless ones and the
# Rose (7, 12, 24) carry two — eighteen wheels in all.
THIRD_WHEEL_POINTERS = ("trio", "cross", "hexa", "octa")

def palette_styles_for(pointer: str) -> tuple[str, ...]:
    """The wheel slots THIS pointer actually serves — ("primary",
    "secondary") everywhere, plus "tertiary" on the three-wheel
    pointers. The ONE gate the Design window's wheel row, the settings
    normalization and the tests all read (Rule #5)."""
    if pointer in THIRD_WHEEL_POINTERS:
        return PALETTE_STYLES
    return PALETTE_STYLES[:2]

# ═══════════════════════════ WHEEL ARM OFFSETS ═══════════════════════════
# THE GENESIS INVERSION (owner: "trougao ka dole", CUBE.md §Double
# Trinity): the trio's TERTIARY wheel draws its three arms on the OPPOSITE
# seats — 24h/16h/08h instead of 12h/20h/04h — one arm-angle offset fed
# through render.skin_geometry.arm_offset_deg into the star diamonds, the Aura
# wedges, the weekday slots, the lit-index math and the arm hit-test.
GENESIS_ARM_OFFSET_DEG = 180.0

# THE SEASONS ROTATION (Pointers REWORK phase 1, owner spec 2026-07-29):
# the cross's TERTIARY wheel — the Seasons — turns its four arms by half
# a wedge, so the color BOUNDARIES land exactly on 12h/3h/6h/9h and the
# wheel reads ASTRONOMICAL seasons (a season begins at its turning
# point) instead of the meteorological quarters the primary
# (Temperaments) and secondary (Elements) wheels keep.
SEASONS_ARM_OFFSET_DEG = 45.0

# Every WHEEL that seats its arms off the pointer's own default angles,
# keyed (pointer, wheel slot) — the ONE table `render.layers.
# arm_offset_deg` reads, so a new offset wheel is a line here rather
# than a branch in the renderer (Rule #5).
WHEEL_ARM_OFFSET_DEG = {
    ("trio", "tertiary"): GENESIS_ARM_OFFSET_DEG,
    ("cross", "tertiary"): SEASONS_ARM_OFFSET_DEG,
}
