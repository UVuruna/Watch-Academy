"""BAKE-TIME POLICY — what the setup bakeries encode, and how well.

See [Bakery](__about/bakery.md).

A peer module rather than more of `defaults.py`, on THE STRUCTURE LAW's
own terms: these names are read at SETUP by `setup/make_art_bake.py` and
`setup/make_letter_bake.py` and by the teeth that check their output.
Nothing in the running dial asks them anything. That is a different
responsibility from the developer tunables `defaults.py` holds, and it
earned its own file the moment it made that file 1,001 lines long.

What is NOT here, deliberately: the pixel CEILINGS. Those live in
`defaults.WORKING_SET_CEILINGS`, because the RUNTIME working set reads
the same table — the bakery asks "how big may this ship?", the runtime
asks "is this bigger than the dial can draw?", and they must never be
able to disagree. One table, two readers (`setup/__about/make_art_bake.md`).
"""

# ═══════════════════════════ ART ENCODING ═══════════════════════════
# THE ART BAKERY's WebP quality for the lossy areas (owner decree
# 2026-08-12). Measured on a 30-plate sample of the real tree, against
# the full-resolution PNG masters: q85 -> 9.9%, q90 -> 11.8%,
# q95 -> 14.9%, q100 (still lossy) -> 18.8%, and WebP LOSSLESS -> 39.7%.
# 90 is the knee: below it the plates' hard alpha borders start trading
# visible edge quality for single-digit megabytes, above it the price
# climbs steeply for a difference the dial draws at 800 px. Lossless was
# rejected outright — 1.6 GB is not a saving.
#
# Graded, not assumed: `.claude/shots/art-bake-q90/master_vs_baked_ab.png` puts master
# against bake at drawing size and at 3x, and shows no blocking, no
# banding and no ringing on the alpha edges.
#
# `instrument/letters` is NOT covered by this and never will be: those
# are the transformer's gold masters, and the letter bake below is
# LOSSLESS for the same reason.
ART_BAKE_QUALITY = 90


# ═══════════════════════════ THE EAGER LETTER ROSTER ═══════════════════════════
# WHICH LETTER FINISHES ARE BAKED EAGERLY, and which wait to be asked
# for (owner decree 2026-08-12, on the 302 MB letter bake). His ruling:
# render only what is actually used — the three real metals with all
# their shades, plus the thematic colours the shipped rings and themes
# use — and leave the rest of the transformer's ramps (copper, brass,
# rose gold, steel, pewter, iron, and the thematic aliases of ramps the
# real metals already bake) to be derived the first time a user builds a
# custom ring that wants one. Nothing is lost by waiting: a miss is the
# ordinary runtime path that existed before any bake did, and
# `render.art_warm` drains it in the background while the dial shows the
# gold master.
#
# 17 of the 34 pairs — half the files. The dropped thematic entries are
# NOT missing colours: `thematic/gold`, `thematic/silver`,
# `thematic/bronze*` and the gold_* aliases are the SAME ramps the
# metals above already bake, duplicated only because the runtime key
# carries the pair. The bake pays for that duplication once; it need not
# pay for it eagerly.
#
# Validated against `defaults.METAL_SHADES` by
# `setup/make_letter_bake._finishes` and by
# `tests/test_startup_cost.py::test_the_eager_roster_names_only_real_shades`
# — a typo here must fail loudly, not bake sixteen finishes and leave one
# colour deriving forever.
EAGER_BAKED_SHADES = {
    "gold": ("dark_amber", "amber", "classic", "pale", "champagne"),
    "bronze": ("dark_bronze", "bronze", "light_bronze"),
    "silver": ("gunmetal", "silver", "platinum"),
    "thematic": (
        "cross_red",        # red
        "cross_blue",       # blue
        "dollar_green",     # green
        "moon_indigo",      # the indigo/violet default
        "templar_black",    # the Templar set
        "ceramic",          # ceramic white
    ),
}
