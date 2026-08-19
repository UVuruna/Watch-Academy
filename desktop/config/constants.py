"""Product-defining invariants. These values NEVER change at runtime
and are not user-tunable — they define what Watch Academy is.

The WEEKDAY theme tables here are DERIVED: `config.registry` holds one
entry per theme and every table below is computed from it in a single
assignment (owner decree 2026-08-01). The names stay because the
program reads them everywhere; the data has exactly one home.

Tunables (things a developer might reasonably adjust) live in defaults.py.
Win32 API literals live in winapi.py.
"""

from config import registry

# ═══════════════════════════ APP IDENTITY ═══════════════════════════

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

# ═══════════════════════════ THE CUBE LOOK ═══════════════════════════
# THE CUBE LOOK (owner seal 2026-07-26, CUBE.md §Display laws): the
# Double-Trinity FAMILY wheels — the Court (trio primary), Genesis (trio
# tertiary) and the Council (hexa tertiary) — render in TWO looks: "Diamond"
# (the slim arm diamonds, the current form) and "Cube" (the owner's
# corner-view: the arm diamonds widen to 180/N half-angles, so the
# three/six rhombi tile the hexagon exactly — three visible cube faces
# on the trio wheels, the two interlocked corners on the Council).
# `Settings.cube_look` toggles it; render.skin_geometry.cube_look_active gates.
CUBE_LOOK_WHEELS = (
    ("trio", "primary"), ("trio", "tertiary"), ("hexa", "tertiary"),
)

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

# ═══════════════════════════ WEEKDAY THEMES ═══════════════════════════
# Weekday body themes (SYMBOLISM.md canon): "planets" uses the skin's
# own weekday unit; the others swap in the owner's themed art from
# assets/skins/domy/weekday/<theme>/ with the canon display names.
WEEKDAY_THEMES = registry.THEMES

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

# ═══════════════════════════ THEME BLURBS & ARTICLES ═══════════════════════════
# Theme -> symbolism.json blurb key (the encyclopedic text under the
# hexa diamond hover follows the active theme).
WEEKDAY_THEME_BLURBS = registry.BLURBS

# Theme -> symbolism.json article set (the glyph theme shares the
# planet articles — same entities, different art).
WEEKDAY_THEME_ARTICLES = registry.ARTICLES

# ═══════════════════════════ THE NINTH TABLES ═══════════════════════════
# THE NINTH per weekday theme (CANON.md "The Ninth — Outside the
# Circle"; owner 8+1 doctrine 2026-07-14): (display name, plate path
# RELATIVE to WEEKDAY_ART_DIR). Themes absent from this table (planets,
# planet_signs, japan, virtues, sins, moods) run DUAL-only — two faces,
# no Ninth. Extracted round R3b (item 3) as the ONE shared table the
# Encyclopedia's ninths pass (app.encyclopedia) and the CENTER seat's
# solar-window face law (render.layers/compositor) both read — a
# parallel copy would drift the moment either side's roster changes
# (Rule #5). The zodiac-only ninths (Chinese "The Cat", Astrology
# "Ophiuchus") stay OUT of this table on purpose — they carry no
# weekday Sunday duality, so the render side never needs them.
WEEKDAY_THEME_NINTHS = registry.NINTHS

# THE PANGEA EASTER EGG (owner-sealed matrix 2026-07-21; trigger WIDENED
# to every principal moon phase 2026-07-29): Pangea shows INSTEAD of
# Zealandia on the Ninth seat ONLY when the sky is doing something on
# the traveled day — an eclipse, a season turning point, or a principal
# moon-phase day (full, new, or either quarter — core.continents'
# `pangea_over_zealandia`). Same story, deeper time: was once ALL,
# split, and by the supercontinent cycle will return. The LAW lives in
# core.continents; render.ninths.theme_ninth reads this alt table when
# the law fires (mechanism "easter_egg" below). Plate wired ahead of the
# owner's art (graceful-absent), same earth-family home as Zealandia.
WEEKDAY_THEME_NINTH_EASTER_EGG = registry.NINTH_EASTER_EGG

# THE DYAD'S NIGHT FACE (owner Double-Ninth verdict, 2026-07-29):
# sw_dyad's Ninth is a DAYLIGHT/NIGHT switch, not a date rotation — day
# shows the canonical `WEEKDAY_THEME_NINTHS["sw_dyad"]` entry (The
# Ghosts, the good side), night shows Exegol from this table (the
# owner's words: "the duality of that theme pulling the actors to one
# of two sides"). Mirrors `WEEKDAY_THEME_NINTH_EASTER_EGG`'s shape —
# theme -> (display name, plate) — read by `render.ninths.theme_ninth`
# when the mechanism dispatch (`NINTH_MECHANISMS` below) resolves to
# "daynight". Plate wired ahead of the owner's art (graceful-absent);
# neither Ghosts nor Exegol has landed yet.
WEEKDAY_THEME_NINTH_NIGHT = registry.NINTH_NIGHT

# ═══════════════════════════ NINTH MECHANISMS ═══════════════════════════
# THE DOUBLE NINTH LAW (standing law, owner decree 2026-07-29): a theme
# may mount a DOUBLE NINTH — two faces contending for the ONE seat —
# only with a DEFINED alternation mechanism, and every reader (the dial,
# its hover, the Encyclopedia) shows ONLY the currently active face,
# never both at once. `NINTH_MECHANISMS` names, per theme, WHICH
# mechanism governs its double Ninth (and, for "term_weekly", its whole
# synchronized Throne/Mirror/Ninth triple — the name stays "NINTH_" for
# historical continuity with the seat it was coined for):
#
# - "easter_egg"  — a SKY trigger (`core.continents.pangea_over_
#   zealandia`): the alt face surfaces only when an eclipse, a turning
#   point or a principal moon phase lands on the traveled day.
# - "daynight"    — the SAME daylight state `render.ninths.center_face`
#   reads (`TickState.is_daylight`): day the canonical face, night the
#   alt (`WEEKDAY_THEME_NINTH_NIGHT`).
# - "term_weekly" — cp_corpo's WEEKLY MANDATE: the traveled date's ISO
#   calendar week PARITY decides which half of the seat roster rules —
#   even week the canonical (Arasaka) triple, odd week the alternate
#   (NUSA) triple — for its Throne, Mirror AND Ninth together (the
#   existing `WEEKDAY_SEAT_ROSTERS`/`rotating_art_file` chokepoint,
#   cadence swapped from daily to weekly; `config.defaults.
#   _pick_weekly_mandate`). No separate alt TABLE — the roster already
#   names both halves, only the picker's cadence changes.
#
# A theme absent from this table has no double Ninth at all (the plain
# single canonical entry in `WEEKDAY_THEME_NINTHS`). `NINTH_MECHANISM_
# KINDS` is the vocabulary every dispatch above actually implements
# (`render.ninths.ninth_table_for`/`ninth_alt_active`, `render.
# compositor._center_ninth_alt`, `config.pantheon.rotating_art_file`'s
# cadence override) — `tests/test_ninth_mechanisms.py` fails the build
# if `NINTH_MECHANISMS` ever names anything outside it, or if a double
# Ninth found in ANY registry above has no entry here at all.
NINTH_MECHANISMS = registry.MECHANISMS
NINTH_MECHANISM_KINDS = frozenset({"easter_egg", "daynight", "term_weekly"})

# ═══════════════════════════ DUAL/NINTH TIME WINDOW ═══════════════════════════
# THE DUAL/NINTH TIME WINDOW (owner seal 2026-07-29, superseding
# INSTRUCTION #5's hour widths): half an hour either side of the day's
# SOLAR anchors (never wall-clock — `core.angles.hours_between` reads
# the actual `DayContext.sun.noon`), i.e. solar 11:30-12:30 and
# 23:30-00:30. In BOTH windows the NINTH shows; outside them the
# CENTER seat follows the sky itself — DAYLIGHT the Ruler, NIGHT the
# Servant (`render.ninths.center_face`) — and a two-badge Sunday swaps
# ONE seat per window (`render.ninths.dual_seat_ninth`: near noon the
# Ninth replaces the SERVANT beside the Ruler, near midnight the RULER
# beside the Servant). Themes with no Ninth ignore the windows.
CENTER_WINDOW_HOURS = 0.5

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

# ═══════════════════════════ GLOW WINDOWS & ECLIPSE VISIBILITY ═══════════════════════════
# Season/moon event glow windows (owner spec): the Earth marker glows
# ±12 h around the four season instants, the Moon marker ±6 h around the
# four principal phase instants. The phase NAME window stays ±12 h
# (MOON_PRINCIPAL_WINDOW above).
SEASON_GLOW_WINDOW_H = 12.0
MOON_GLOW_WINDOW_H = 6.0
# Eclipse display (owner 2026-07-18, ROADMAP 15h item 11): the sealed
# ±3h window, same shape as the season/moon windows above but its own
# constant (the owner's spec is explicitly ±3h, not the moon's ±6h).
ECLIPSE_GLOW_WINDOW_H = 3.0
# THE ECLIPSE BODY's own, WIDER window (owner ballot verdict 2026-08-12,
# option B2 with his written correction "+-12h"): the eclipse now stands
# on the dial as a THIRD celestial body at the hour it happens
# (`render.layers.year_marker.YearMarkerLayer._draw_eclipse_body`), and a
# body that only appeared three hours before its own instant would keep
# the dial silent for most of the day that carries the eclipse. Twelve
# hours is his number, and it is the SEASON window's number too — half a
# day either side, so an eclipse is on the dial for the whole span in
# which its own date is the current one.
ECLIPSE_BODY_WINDOW_H = 12.0

# Eclipse VISIBILITY (owner verdict "može", fix round E, 2026-07-19):
# a SOLAR eclipse is visible to the observer only within this great-
# circle distance of the catalog's greatest-eclipse point (the path of
# totality/partiality does not reach much farther); LUNAR visibility has
# no distance term — a lunar eclipse is visible from the whole night
# hemisphere, so only "Moon above the horizon" gates it.
ECLIPSE_SOLAR_VISIBILITY_KM = 3500.0
EARTH_RADIUS_KM = 6371.0            # mean radius — the great-circle distance basis

# ═══════════════════════════ TRANSLATION LANGUAGES ═══════════════════════════
# Languages offered in Settings (owner: "all the provider offers") —
# the Google-translate codes the gtx endpoint accepts, code -> English
# display name. ORIGINALS (owner decision 2026-07-11) ship hand-written
# in the app (Database/translations/) and sit pinned at the top of the
# combo; every other language machine-translates on first pick.
TRANSLATION_ORIGINALS = ("en", "sr-Latn")
TRANSLATION_LANGUAGES = {
    "en": "English",
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "hy": "Armenian", "az": "Azerbaijani", "eu": "Basque",
    "be": "Belarusian", "bn": "Bengali", "bs": "Bosnian",
    "bg": "Bulgarian", "ca": "Catalan", "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)", "hr": "Croatian", "cs": "Czech",
    "da": "Danish", "nl": "Dutch", "eo": "Esperanto", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "gl": "Galician", "ka": "Georgian",
    "de": "German", "el": "Greek", "gu": "Gujarati", "he": "Hebrew",
    "hi": "Hindi", "hu": "Hungarian", "is": "Icelandic",
    "id": "Indonesian", "ga": "Irish", "it": "Italian", "ja": "Japanese",
    "kn": "Kannada", "kk": "Kazakh", "ko": "Korean", "lv": "Latvian",
    "lt": "Lithuanian", "mk": "Macedonian", "ms": "Malay",
    "ml": "Malayalam", "mt": "Maltese", "mr": "Marathi",
    "mn": "Mongolian", "ne": "Nepali", "no": "Norwegian",
    "fa": "Persian", "pl": "Polish", "pt": "Portuguese",
    "pa": "Punjabi", "ro": "Romanian", "ru": "Russian",
    "sr": "Serbian (Cyrillic)", "sr-Latn": "Serbian (Latin)",
    "sk": "Slovak", "sl": "Slovenian", "es": "Spanish",
    "sw": "Swahili", "sv": "Swedish", "ta": "Tamil", "te": "Telugu",
    "th": "Thai", "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu",
    "uz": "Uzbek", "vi": "Vietnamese", "cy": "Welsh",
}

# ═══════════════════════════ UI SCALE & SATURATION RANGES ═══════════════════════════
# The Encyclopedia's Ctrl+MouseWheel ZOOM (owner round R8b item 5b:
# "uvodimo novu funkcionalnost CTRL + MOUSHE WHEEL... za smanjenje
# svega ili povecanje" — one factor scaling fonts, images and gallery
# tiles together). The RANGE bounds are the fixed product invariant
# (same pattern as ELEMENT_SCALE_RANGE above); the live factor itself
# is session-only state on `app.encyclopedia` (never written to
# settings — the owner asked for "the session at least", not
# persistence across restarts). STEP is the zoom delta per wheel notch
# (Qt reports ±120 angleDelta per notch — one notch = one STEP).
ENCYCLOPEDIA_ZOOM_RANGE = (0.6, 2.5)
ENCYCLOPEDIA_ZOOM_STEP = 0.1

# Element size multipliers (Settings sliders, owner EXTRAS) and the
# shared hover-enlarge factor (the element under the cursor draws this
# much larger; 1.0 disables the effect).
ELEMENT_SCALE_RANGE = (0.5, 2.0)
HOVER_ENLARGE_RANGE = (1.0, 2.0)
# The Saturation sliders (owner 2026-07-18, Settings ▸ Colors, Session
# 21-D — moved out of Display/Element sizes into their OWN "Saturation"
# group beside Palette + Ring tint): 0.0 grays the target to its own
# brightness, 1.0 is the owner preset unchanged. The slider itself is
# 0-100; the stored setting is the 0.0-1.0 factor.
# POINTER (formerly "palette_saturation" — renamed for clarity now that
# a second, independent RING slider exists): the Star+Aura palette's
# HSV saturation (`render.skin_geometry.palette_for`).
POINTER_SATURATION_RANGE = (0.0, 1.0)
POINTER_SATURATION_SLIDER_STEP = 1
# RING (new, Session 21-D): the ring band art's HSV saturation — the
# ring plate AND its letter/numeral overlay (`render.layers.ring.RingLayer`,
# after the ring_tint recolor). The Umbra and hands do not read this —
# see layers.md's RingLayer note for the ground-truthed scope.
RING_SATURATION_RANGE = (0.0, 1.0)
RING_SATURATION_SLIDER_STEP = 1
# HANDS (Watch Face Phase 4, R-25): the hand pack's own HSV saturation,
# independent of the ring's — `render.layers.hand.HandLayer` reads it
# alongside its existing `desaturate`/`tint` pipeline (the SAME
# `AssetCache.pixmap_by_height` saturation parameter the ring already
# uses, a bounded reuse — no new recolor math).
HANDS_SATURATION_RANGE = (0.0, 1.0)
HANDS_SATURATION_SLIDER_STEP = 1
# UMBRA (Watch Face Phase 4, R-25): scales the Umbra TINT's own HSV
# saturation before the black->tint->white tritone map runs
# (`render.skin_geometry.saturate_hue`, reused from the Aura's — Rule
# #5) — 0.0 grays the active tint to a plain neutral, 1.0 unchanged.
# A no-op while the Umbra follows Gray (tint is None): there is no hue
# to desaturate.
UMBRA_SATURATION_RANGE = (0.0, 1.0)
UMBRA_SATURATION_SLIDER_STEP = 1

# ═══════════════════════════ DUALITY SEATING ═══════════════════════════
# The SOUTH SLOT home angle and the Aurora DUAL layout (owner spec
# 2026-07-12): with BOTH the weekday body and the slot on, they flank
# the bottom ±45° — the weekday at 3h on the left, the slot at 21h on
# the right.
#
# STALE-COMMENT CORRECTION (owner 2026-07-27): this comment used to
# claim "the Compass reserves this bottom arm for it". It has not been
# true since the dual-Sunday round — the Compass shows all EIGHT arms,
# and its 24h seat belongs to the SERVANT face of Sunday
# (`render.slot_layout.servant_holds_the_seat`), which is exactly why
# `POINTER_WEEKDAY_SLOTS["octa"]` has no 180° entry. A later change
# moved the truth and left the old sentence standing, and a session
# read it and believed it. When behavior moves, the sentence that
# described the old behavior DIES WITH IT.
SOUTH_SLOT_ANGLE = 180.0
# The SERVANT face's own seat per pointer (owner 2026-07-27): 24h
# everywhere the dual Sunday has always sat, but the ROSE seats him on
# the BLUE arm at 06h — blue is Judas's hue and the servant's, red is
# Lucifer's and the master's, and 6 + 6 + 6 lands the pair on 06h and
# 18h (CUBE.md §The Rose). `render.skin_geometry.servant_seat_angle` is the
# ONE reader (Rule #5); absent = SOUTH_SLOT_ANGLE.
SERVANT_SEAT_ANGLE = {"rose": 270.0}
AURORA_DUAL_WEEKDAY_ANGLE = 225.0    # 3h — bottom left
AURORA_DUAL_SLOT_ANGLE = 135.0       # 21h — bottom right

# THE DUALITY-AXES CONFIG (owner decree 2026-07-28, CUBE.md §The
# Thirteen Axes — Display Plans). Every weekday theme's Sunday duality
# rides an axis whose two ends are Cube poles: VERTICAL (yellow-top/
# 12h <-> purple-bottom/24h) on the Compass and the Seasons, HORIZONTAL
# (blue-06h <-> red-18h, the Sunday axis) on the Rose instead. The
# default law is unconditional on the vertical axis — the Ruler
# (`WEEKDAY_DUAL_NAMES[theme][0]`) always pulls to the warm pole
# (yellow/top) there, no per-theme override exists or is needed. Only
# the HORIZONTAL axis is per-theme, because a blind carryover of that
# same default (Ruler -> warm/red) is wrong wherever the Sacred Axis
# (CUBE.md §The Thirteen Axes) already assigns a member to the COLD
# trio: Christianity is the LUMINOUS COLD member (blue), Satanism the
# FALLEN WARM one (red) — the reverse of the blind default, which
# today seats Satanism blue and Christianity red. Listed themes pull
# their RULER to the cold pole instead; absent = the default carries
# over unchanged. `render.skin_geometry.ruler_seat_angle`/`servant_seat_angle`
# are the two readers (Rule #5) — they swap which of the Ruler's/
# Servant's figures rides which arm, never their names or articles.
DUALITY_RULER_ON_COLD_POLE = frozenset({"religion"})

# THE DUAL SUNDAY WHEEL MAP (owner seal 2026-07-29, closing the Session
# 23 miss — the per-WHEEL split was the whole point of the Duality-Axes
# decree and the Compass's third wheel never received it). Sunday's
# duality displays one of THREE ways, and the way is a property of the
# WHEEL, not only the pointer:
#   CENTER (one image; daylight Ruler / night Servant / Ninth in the
#     solar windows) — the Trinity and the Prism (all wheels), PLUS the
#     wheels below: the Quaternity's Seasons wheel turns its arms onto
#     the diagonals, leaving no 12h/24h seat to stand on.
#   VERTICAL 12h/24h (Ruler top in the light, Servant bottom in the
#     dark) — the Quaternity and the Compass, primary + secondary.
#   HORIZONTAL 06h/18h (Servant on blue left, Ruler on red right) — the
#     Rose (both wheels) PLUS the wheels below: the Compass's Character
#     wheel wears the very ROSE_PALETTE hues, so its Sunday rides the
#     same blue<->red axis and its bodies take the Rose's own hue seats
#     (`render.layers` reads POINTER_WEEKDAY_SLOTS["rose"] for it).
CENTER_DUALITY_WHEELS = frozenset({("cross", "tertiary")})
HORIZONTAL_DUALITY_WHEELS = frozenset({("octa", "tertiary")})

# THE GEOGRAPHIC VERTICAL FLIP (owner seal 2026-07-29, theme poll 23/23):
# themes whose VERTICAL duality seats the SERVANT on top — continents,
# because the Arctic IS the north and a globe reads north-up: Arctic
# (Servant) 12h, Antarctica (Ruler) 24h. The horizontal axis stays
# standard (18h red Antarctica, 06h blue Arctic). Same reader pair as
# DUALITY_RULER_ON_COLD_POLE; every OTHER theme was polled and sealed
# STANDARD the same day (Ruler top+red, Servant bottom+blue).
DUALITY_SERVANT_ON_TOP = frozenset({"continents"})
