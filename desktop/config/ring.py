"""THE RING VOCABULARY's own tables - the band around the dial.

The ring is four different things and never variants of one (project
law, docs/DIAL.md#ring-vocabulary): JEWELS, NUMERALS, MINUTES and the
CROWN. This module is where the ring's declarative half lives: the
finishes and the metal shade ramps every metal-bearing surface reads,
the subdial plate styles and sets, the OUTERS (which hour fields a
ring layout leaves empty) with their per-preset lock, the INNERS, the
Eye of Providence glyph and its shine, the letter plate groups and
files THE ONE PLATE LAW resolves every glyph through, the crown-text
charset - and the theme METAL LOOKS, which are a ring-metal decision
wearing a theme's name.

The ring's GEOMETRY (band width, jewel seats, the crown arc radius)
stays in `config/dial.py`, which owns everything measured in pixels.

Born 2026-08-19, when the owner ruled that `config/constants.py`'s
**38 top-level sections** were a junk drawer, not a directory, and gave
the split its module names himself. Nothing here is new data - every
table below stood in `constants.py` under its own section banner and
moved WHOLE, with its comments; the callers were repointed, and no
re-export shim was left behind (`rules/CODE.md` - No backward
compatibility). The whole map, one row per module, is in
[the folder doc](___config.md).

Layer: config - pure Python, no Qt, no wall clock. It reads
`config.registry` for the one table THE REGISTRY owns (which themes
wear a metal at all) and imports no other sibling.
"""

from config import registry

# ═══════════════════════════ RING FINISHES & METAL SHADES ═══════════════════════════
# Ring letters and layouts (owner spec 2026-07-10, data-driven): ring
# presets live in Database/ring_presets.json (+ the user's custom ones
# in settings) as {name, positions, letters}; the POSITIONS signature
# picks a LAYOUT — the ring face with matching gaps and the metal
# rules. Finish rules (owner correction): the trio of ONE metal always
# forms a TRIANGLE — the GOLD finish puts the layout's triangle in gold
# and the rest in silver, the SILVER finish is the exact inverse; on
# the hexagram BOTH metals form triangles (12/20/4 vs 24/8/16). Silver
# and bronze letters are derived from the gold master AT LOAD (owner
# 2026-07-19, render.asset_recolor.jewel_metal_file).
RING_FINISHES = ("gold", "silver", "bronze", "thematic")
# THE THEMATIC FINISH (ENLARGE/THEMATIC round, owner 2026-07-27,
# "četvrta opcija za ring THEMATIC ... bojiti PREKO NOVOG PROGRAMA"):
# the 4th ring jewel finish — instead of a metal, the jewels wear the
# ACTIVE PRESET's own theme color, drawn by the SAME recolor
# transformer (a colored RAMP beside the metal ramps in
# recolor/presets/metals.json — "adding a metal costs one entry and
# zero code"). Per-preset shade (the ramp names double as shade names,
# METAL_SHADE_NAMES["thematic"]); a custom/unknown ring falls back to
# the moon indigo (the app's own signature hue). Outside the ring band
# (subdial borders, hands, follow-the-ring theme metals) the thematic
# finish reads as GOLD — the color belongs to the jewels and the
# words, not to every metal surface (documented containment).
RING_THEMATIC_SHADES = {
    "DOMY": "cross_red",        # the suffering cross
    "LOOP": "cross_blue",      # the salvation cross
    "Dollar": "dollar_green",   # the banknote's ink
    "The One": "moon_indigo",   # the winter-solstice violet
    "Templar": "templar_black", # the Beauceant
    "CHI": "ceramic",           # the cold porcelain of the 24th letter
}

# THE METAL SHADES (R8a round, owner spec 2026-07-21 night — the retry
# after the adaptive-percentile attempt was reverted for flattening
# every relief into a wash, see config.defaults's NOTE above
# METAL_SHADES): each metal offers several SELECTABLE shades, picked in
# Settings (app.settings_dialog.themes_section._build_metal_shade_group)
# and stored one per metal (`Settings.metal_shade_gold/_bronze/_silver`).
# Names here are the validation/enumeration source; the numeric (hue, saturation,
# reference value) recipe per shade lives in `config.defaults.
# METAL_SHADES` — kept in `defaults` because it depends on nothing else,
# same split as SUBDIAL_SETS (names, here) vs SUBDIAL_RECOLOR_COLORS
# (recipe, defaults).
METAL_SHADE_NAMES = {
    "gold": ("dark_amber", "amber", "classic", "pale", "champagne"),
    "bronze": ("dark_bronze", "bronze", "light_bronze"),
    "silver": ("gunmetal", "silver", "platinum"),
    # The THEMATIC pseudo-metal (ENLARGE/THEMATIC round, owner
    # 2026-07-27; widened for CUSTOM rings same day): its "shades" are
    # ALL the transformer's ramps — the five ring theme colors
    # (`RING_THEMATIC_SHADES`) PLUS every metal ramp (owner: "iron,
    # copper... sve") — so a custom card's own `thematic` pick can name
    # any of them. Bundled presets resolve automatically from
    # `RING_THEMATIC_SHADES`; never offered in the Settings shade
    # pickers. This tuple mirrors `recolor/presets/metals.json` and is
    # guarded against drift by `tests/test_skins.py`
    # (test_thematic_choices_mirror_the_recolor_presets) — constants.py
    # stays a pure-literals file (its own docstring law), the test is
    # the sync.
    "thematic": (
        "cross_red", "cross_blue", "dollar_green",
        "moon_indigo", "templar_black", "ceramic",
        "gold", "gold_dark_amber", "gold_amber", "gold_pale",
        "gold_champagne",
        "silver", "bronze", "bronze_dark", "bronze_light",
        "copper", "brass", "rose_gold", "steel", "gunmetal",
        "platinum", "pewter", "iron",
    ),
}
METAL_SHADE_DEFAULT = {
    "gold": "classic", "bronze": "bronze", "silver": "silver",
    "thematic": "moon_indigo",
}
METAL_SHADE_TITLES = {
    "dark_amber": "Dark amber", "amber": "Amber", "classic": "Classic gold",
    "pale": "Pale gold", "champagne": "Champagne",
    "dark_bronze": "Dark bronze", "bronze": "Bronze", "light_bronze": "Light bronze",
    "gunmetal": "Gunmetal", "silver": "Silver", "platinum": "Platinum",
    "cross_red": "Cross red", "cross_blue": "Cross blue",
    "dollar_green": "Dollar green", "moon_indigo": "Moon indigo",
    "templar_black": "Templar black", "ceramic": "Ceramic",
    # The remaining transformer ramps, pickable by a CUSTOM ring's own
    # thematic choice (ENLARGE/THEMATIC round, widened same day):
    "gold": "Gold", "gold_dark_amber": "Gold dark amber",
    "gold_amber": "Gold amber", "gold_pale": "Gold pale",
    "gold_champagne": "Gold champagne",
    "bronze_dark": "Dark bronze (ramp)", "bronze_light": "Light bronze (ramp)",
    "copper": "Copper", "brass": "Brass", "rose_gold": "Rose gold",
    "steel": "Steel", "pewter": "Pewter", "iron": "Iron",
}

# ═══════════════════════════ SUBDIAL PLATES ═══════════════════════════
# The subdial PLATE styles (owner 2026-07-15, his A/B spec): "theme" —
# the tapisserie field wears the clock tint (the AP design in the
# theme color) and the tick circle joins the finish metal; "black" —
# the standard dark AP field as drawn, white ticks. Both: rim, mini
# hand and complication texts in the jewel-finish metal, shadowed.
SUBDIAL_STYLES = ("theme", "black")

# The subdial PLATE SETS (owner decree 2026-07-21, Rsub round —
# retires the Rule #19 one-master-per-source model): the plate is its
# OWN shared thing now, not a Gemini/ChatGPT split — five hand-picked
# sets live under assets/subdial/ (see assets/___assets.md for why
# that root sits OUTSIDE ART_SOURCED_ROOTS). "set1".."set4" are each
# three hand-drawn finishes (no recolor); "solo" ships one hand-drawn
# silver file and the algorithm derives gold/bronze from it exactly
# like before.
SUBDIAL_SETS = ("set1", "set2", "set3", "set4", "solo")
SUBDIAL_SET_DEFAULT = "set1"
SUBDIAL_SET_TITLES = {
    "set1": "1", "set2": "2", "set3": "3", "set4": "4", "solo": "Solo",
}

# ═══════════════════════════ RING OUTERS, INNERS & LETTERS ═══════════════════════════
# THE COMPOSITIONAL RING MODEL (owner decree 2026-08-05, coordinator's
# pixel analysis on the actual PNGs): a ring is ALWAYS the composition
# of an OUTER band (`assets/instrument/ring/outter/`, carries the empty
# hour fields the jewels stand in) + an INNER band
# (`assets/instrument/ring/inner/`, the minute track) + the preset's
# own jewels in the outer's empty fields + an optional CROWN TEXT
# (crown text) arc. The old monolithic single-plate faces (`domy.png`,
# `morph.png`, `hexagram.png`) are DEAD — deleted from disk the same
# session this table replaced `RING_LAYOUTS`. `positions` is the empty
# hour fields, MEASURED off the art (owner naming keeps the pre-
# existing "24" convention for the bottom/midnight seat rather than
# "0" — `core.angles.ring_position_angle` treats them identically).
# `triangle` is the DEFAULT 3-of-N metal-split subset for outers that
# have one built in (bot_cross/top_cross, today's DOMY/LOOP look);
# empty for every other outer — a preset may still override it via its
# own `triangle` card field, but ONLY when its outer is `"hexa"`
# (`data.rings.validate_preset`).
RING_OUTERS = {
    "bot_cross": {
        "file": "bot_cross.png",
        "positions": (12, 20, 24, 4),
        "triangle": (12, 20, 4),     # points UP (the Flame, DOMY's own)
        "theme": "Masculine",
    },
    "top_cross": {
        "file": "top_cross.png",
        "positions": (12, 16, 24, 8),
        "triangle": (8, 16, 24),     # points DOWN (the Chalice, LOOP's own)
        "theme": "Feminine",
    },
    "hexa": {
        "file": "hexa.png",
        "positions": (12, 16, 20, 24, 4, 8),
        "triangle": (),              # the Seal wears ONE metal on all six
        "theme": "Union",
    },
    "cross": {
        "file": "cross.png",
        "positions": (12, 18, 24, 6),
        "triangle": (),
        "theme": "Cross",
    },
    "full": {
        "file": "full.png",
        "positions": (24,),
        "triangle": (),
        "theme": "Full",
    },
    "octa": {
        "file": "octa.png",
        "positions": (12, 15, 18, 21, 24, 3, 6, 9),
        "triangle": (),
        "theme": "Octa",
    },
}
# THE FIVE PRESETS' LOCKED OUTER (owner decree 2026-08-05): each
# bundled preset is locked to exactly one outer — the preset's INNER
# stays user-changeable (`RING_INNER_PRESET_DEFAULT` below is only the
# starting default). `data.rings.validate_preset` enforces this lock
# for every bundled card. RING VERDICTS round (owner correction
# 2026-08-05): "The One" moved off "full" onto "octa" — Ω alone at the
# midnight seat with the seven other empty fields wearing their own
# NUMBER glyphs (3/6/9/12/15/18/21), exactly what those number plates
# were made for. "full" itself is now PRESET-FREE — no bundled card
# locks to it any more, custom rings only.
RING_OUTER_LOCK = {
    "DOMY": "bot_cross", "LOOP": "top_cross", "Dollar": "hexa",
    "Templar": "cross", "The One": "octa", "CHI": "full",
}
# THE EIGHT INNER VARIANTS (owner's measured art,
# `assets/instrument/ring/inner/*.png`): "seconds*" carry the minute
# numbers (today's look), "simple*" ticks only; the _cross/_octa/_point
# suffix is an arrow-marker overlay at those positions. Legal on EVERY
# outer (custom rings) — the compositional model has no illegal pair.
RING_INNERS = (
    "seconds", "seconds_cross", "seconds_octa", "simple",
    "simple_cross", "simple_octa", "simple_point", "simple_seconds",
)
# The owner's FINAL per-preset default inner (RING VERDICTS round,
# 2026-08-05 correction — supersedes the coordinator's first pass):
# DOMY/LOOP/Dollar all read "seconds" (the minute numbers, today's
# banknote look shared across the whole trio); Templar reads
# "seconds_cross" (numbers + the cross-marker overlay, matching its
# own outer); The One reads "simple_octa" (ticks + the octa marker,
# matching its own new octa outer). Still user-changeable in
# Settings ▸ Ring like `RING_EYE_SHINE_DEFAULT`.
RING_INNER_PRESET_DEFAULT = {
    "DOMY": "seconds", "LOOP": "seconds", "Dollar": "seconds",
    "Templar": "seconds_cross", "The One": "simple_octa",
    # RULED "može" (Crown Polish round, owner 2026-08-06 — the S5
    # ring-rework CHI proposal is approved as written): "simple" — the
    # emptiest inner for the emptiest dial (a single X on the solid
    # "full" outer plate); still user-changeable in Settings ▸ Ring.
    "CHI": "simple",
}
RING_INNER_DEFAULT = "simple"       # every custom ring's own fallback
# TWO METALS RETIRED (owner decree 2026-08-11): the per-preset 3-3
# metal split toggle (TASK 3, MASON/ICONS round) and its
# `RING_TWO_METALS_DEFAULT` table are gone — every ring now wears the
# plain one-metal reading.
# THE EYE AT THE APEX (DOLLAR/EYE round, owner decree 2026-07-27): the
# Dollar preset's 12h seat wears the EYE OF PROVIDENCE instead of the
# letter G (CANON.md §The Banknote, CUBE.md §The Banknote Seal). "👁"
# is the ADAPTIVE glyph — its canonical Eye.png resolves to
# Eye_gem/Eye_gpt per the Settings art source (config.paths.art_file),
# and the per-preset "Shine" toggle (Settings.ring_eye_shine,
# app.skin_builder._ring_eye_shine) swaps the whole stem for the glory-of-rays
# master Eye_shine.png. The four EXPLICIT variants in the letter
# library below are the CUSTOM ring builder's own picks (owner: "any
# of the four") — source and rays baked into the chosen glyph,
# ignoring both switches.
RING_EYE_GLYPH = "👁"
RING_EYE_SHINE_FILE = "emblems/Eye_shine.png"
RING_EYE_SHINE_DEFAULT = {"Dollar": True}
# THE SHINE ENLARGE FACTOR (owner UV inbox 2026-07-27, "slika 2 kada
# ima SHINE mora da bude veca"; corrected same day — the first
# measurement trusted the alpha channel, but the glory of rays is
# ITSELF opaque, so it read the whole glow as "triangle" and landed on
# a uselessly small ~1.16): the factor is the ratio of the TRIANGLE's
# frame fraction between the no-light and shine masters, measured on
# the triangle's actual apex/base rows. The shine masters are also
# PADDED on disk so the triangle sits at the exact frame center
# (originally it rode high, which would have drawn the zoomed triangle
# off-seat). ChatGPT: plain 0.97 vs shine 0.46 of frame -> 2.11;
# Gemini: 0.98 vs 0.59 -> 1.67. `app.skin_builder.build_skin` stamps the
# factor into `SkinDefinition.ring.jewel_zoom` for the shine stems so
# the triangle draws the SAME size and only the rays extend beyond it.
RING_EYE_SHINE_ENLARGE = {"gem": 1.67, "gpt": 2.11}
# The full jewel library (glyph -> art file) — presets and the custom
# ring builder choose from these, GOLD masters only; silver and bronze
# are derived from the gold master at load (owner 2026-07-19,
# render.asset_recolor.jewel_metal_file — no more pre-rendered files).
#
# THE ONE PLATE LAW (owner decree 2026-08-07): everything drawn from
# THIS library — the JEWELS, the whole CROWN, the DUALS — is a plate
# taken as the GOLD master and recolored by the transformer into one of
# the app's metals or thematic colours. One style, one source, one
# algorithm: never a font, never a flat colour of its own. NOT the band
# NUMERALS/MINUTES, which are computed and wear their own even/odd
# parity by design ("JEWELS != NUMERALS", same day). The crown's
# colon had its own plate for exactly this reason
# (`symbols/colon.png`); the ten digits joined it the day the owner saw
# them drawn by a font instead.
#
# The library moved OUT of `instrument/ring/` the same day (owner:
# "nije mu to mesto jer nisu oni samo za ring") — it now sits at
# `assets/instrument/letters/`, grouped by SCRIPT, because the ring,
# the crown and (planned) the subdial all read from it:
#   latin/     A-Z
#   greek/     the ten capitals with a shape of their own
#   numerals/  0-9 — the SINGLE digits only; a two-digit hour seat
#              (12, 15, 16, 18, 20, 21) is COMPOSED from two of them at
#              runtime (`render.letter_plates`), never a plate on disk
#   symbols/   the typeable non-letters
#   emblems/   picked-only seat art, never typed into running text
# A value is therefore a TUPLE of plate paths relative to that root —
# one entry for a glyph with its own plate, two for a composed number.
_LATIN_JEWEL_GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_DIGIT_GLYPHS = "0123456789"
# THE GREEK TWINS (owner ruling 2026-08-07 — "greek koji fale kao što
# je alpha beta... pišu se isto kao latinski a, b; vidi kako ćeš to da
# rešiš"): fourteen Greek capitals are drawn EXACTLY like a Latin
# letter, so they get NO duplicate file — the alias resolves to the
# Latin master (THE ONE COPY RULE: one plate on disk, two glyph keys;
# a shortcut file would be a second copy to keep in sync).
GREEK_LATIN_TWINS = {
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I",
    "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T",
    "Υ": "Y", "Χ": "X",
}
# The ten with a shape Latin has not got — glyph -> its own plate stem.
GREEK_OWN_PLATES = {
    "Γ": "Gamma", "Δ": "Delta", "Θ": "Theta", "Λ": "Lambda",
    "Ξ": "Xi", "Π": "Pi", "Σ": "Sigma", "Φ": "Phi", "Ψ": "Psi",
    "Ω": "Omega",
}
_GREEK_ALPHABET = "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
# The hour NUMBERS the ring seats offer (owner decision: a number makes
# no sense away from its own hour) — every empty field across every
# RING_OUTERS outer EXCEPT 24, which always wears Ω. The multi-digit
# ones are composed from the digit plates, so this list costs no art.
_RING_NUMBERS = (
    "3", "4", "6", "8", "9", "12", "15", "16", "18", "20", "21",
)
LETTER_PLATE_GROUPS = {
    # Æ/Œ close the Latin group (THE LIGATURE PLATES, owner 2026-08-14).
    "Latin": tuple(_LATIN_JEWEL_GLYPHS) + ("Æ", "Œ"),
    "Greek": tuple(_GREEK_ALPHABET),
    "Numbers": _RING_NUMBERS,
    "Symbols": ("✠", "$", "&", ":", "@", "!", "?"),
    "Emblems": ("👁 ChatGPT", "👁 ChatGPT ☀", "👁 Gemini", "👁 Gemini ☀"),
}
LETTER_PLATE_FILES = {
    # The WHOLE library is PNG at 512 px height (owner decision
    # 2026-07-12 — the traced SVGs parsed in seconds; 512 covers every
    # on-dial size with room to spare).
    **{letter: (f"latin/{letter}.png",) for letter in _LATIN_JEWEL_GLYPHS},
    # THE LIGATURE PLATES (owner addition 2026-08-14): Æ and Œ are ONE
    # plate and ONE letter each — the Great Seal's own orthography
    # (CŒPTIS), and the letter count law of the INVERTED CROWN TEXTS
    # (CANON.md §The Banknote): ANNUIT CŒPTIS and SANCIT FŒDERA both
    # weigh 6 + 6 plates only because the ligature is one seat.
    "Æ": ("latin/AE.png",),
    "Œ": ("latin/OE.png",),
    **{glyph: (f"greek/{stem}.png",) for glyph, stem in GREEK_OWN_PLATES.items()},
    **{glyph: (f"latin/{twin}.png",) for glyph, twin in GREEK_LATIN_TWINS.items()},
    **{digit: (f"numerals/{digit}.png",) for digit in _DIGIT_GLYPHS},
    # A two-digit hour is its digits, in order — composed on the fly.
    **{
        number: tuple(f"numerals/{digit}.png" for digit in number)
        for number in _RING_NUMBERS if len(number) > 1
    },
    # Symbols (the owner is growing this set for custom rings; the
    # colon is the crown time's own separator plate, made for it).
    "✠": ("symbols/templar.png",),
    "$": ("symbols/dollar.png",),
    "&": ("symbols/ampersan.png",),
    ":": ("symbols/colon.png",),
    "@": ("symbols/@.png",),
    "!": ("symbols/exclamation.png",),
    "?": ("symbols/question.png",),
    # The Eye of Providence (DOLLAR/EYE round, 2026-07-27): the
    # adaptive glyph (the Dollar's own — source and shine resolved by
    # the switches) plus the four explicit custom-builder variants.
    # EMBLEMS, not symbols (owner ruling 2026-08-07, "u symbols je i
    # eye... odluči"): the line is TYPEABLE — ✠ and $ are characters a
    # crown text can spell, an Eye is seat art you pick, so it can
    # never leak into `RING_CROWN_TEXT_CHARSET` below.
    "👁": ("emblems/Eye.png",),
    "👁 ChatGPT": ("emblems/Eye_gpt.png",),
    "👁 ChatGPT ☀": ("emblems/Eye_shine_gpt.png",),
    "👁 Gemini": ("emblems/Eye_gem.png",),
    "👁 Gemini ☀": ("emblems/Eye_shine_gem.png",),
}
# THE CROWN TEXT WHITELIST (RING VERDICTS round, owner decree
# 2026-08-05): the exact set of characters the crown text renderer can draw
# one-per-character — a custom ring's crown-text field validates
# against this set so an unsupported character can never be TYPED at
# all (replaces the old silent-drop-on-build behaviour). DERIVED, never
# hand-written: every SINGLE-character key of `LETTER_PLATE_FILES` that
# is not an emblem (the multi-character keys — "👁 ChatGPT" and
# friends — are the custom builder's own picks, never typed into
# running text) plus the space that separates words.
RING_CROWN_TEXT_CHARSET = frozenset(
    {
        glyph for glyph, plates in LETTER_PLATE_FILES.items()
        if len(glyph) == 1 and not plates[0].startswith("emblems/")
    } | {" "}
)

# ═══════════════════════════ THEME METAL LOOKS ═══════════════════════════
# The bronze-plate themes (owner 2026-07-12): their medallions can wear
# a METAL — bronze is the art as drawn, gold and silver are runtime
# tritone tints. All other themes are full-color and never tint.
METAL_THEMES = registry.METAL_THEMES
# "colored" (owner 2026-07-12) is the FOURTH look: fresh full-color
# badges from the theme's colored/ subfolder — separate art, no swap.
THEME_METALS = ("gold", "bronze", "silver", "colored")
# Per-theme override (owner 2026-07-18): planets_art is bronze-plate
# medallion art like the pantheon sets, but its source has NO colored/
# subfolder — a half-available look must never be offered, so it drops
# "colored" from its own allowed set. Absent entries fall back to the
# full THEME_METALS tuple; every call site that offers a theme's metal
# choices (menu, Settings dialog, settings validation, tests) must read
# through `theme_metals()` rather than the flat tuple.
THEME_METALS_OVERRIDE: dict[str, tuple[str, ...]] = {
    "planets_art": ("gold", "bronze", "silver"),
}

def theme_metals(theme: str) -> tuple[str, ...]:
    """The metal looks `theme` may wear — THEME_METALS unless the theme
    overrides it (documented exceptions only, see THEME_METALS_OVERRIDE)."""
    return THEME_METALS_OVERRIDE.get(theme, THEME_METALS)
