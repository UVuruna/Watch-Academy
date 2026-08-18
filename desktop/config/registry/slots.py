"""THE SLOT REGISTRY — the three dial slots and the `Settings` field
each one keeps its content, look, theme, roster, names and enablement in.

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
