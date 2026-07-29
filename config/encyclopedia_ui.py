"""The reading surfaces — Encyclopedia, legend and the computed
diagrams. Legend term highlighting, the Cube/Canon diagram
ratios, the Encyclopedia's card/gallery/reader sizing, the
hover warm-sweep tuning and the Instrument's own diagram
constants.

Layer: config — pure, no Qt, no wall clock.
"""

from config import constants, paths


# Article hovers (owner spec, FINAL.txt hover rework + EXTRAS): the
# entity's art rides on top of its article, larger and clearer than on
# the dial; the prose wraps at a fixed width so QToolTip stays a column.
ARTICLE_IMAGE_WIDTH_PX = 192         # owner: at least 2x — the details must read
ARTICLE_TEXT_WIDTH_PX = 460          # owner 2026-07-13 round two: the prose is
                                     # JUSTIFIED inside a fixed-width column
                                     # (Qt reflows it — no manual wrapping)
ARTICLE_COLUMN_WIDTH_PX = 400        # the hexa TWO-COLUMN legend: each sign's
                                     # column; two of them + spacing must fit
                                     # LEGEND_MAX_WIDTH_FRACTION of a 1080p
                                     # screen (0.45 × 1920 = 864)
# The THREE-SIDE article (owner 2026-07-17): a three-column layout whose
# TOTAL width stays the two-column width (2 × ARTICLE_COLUMN_WIDTH_PX) —
# each column narrower so the text wraps more. First consumer: the Ages
# archetype hover (age text + the Tree register + the Menagerie
# register, "oba odmah"). The image columns scale their register art to
# the column width.
ARTICLE_THREE_COLUMN_WIDTH_PX = round(2 * ARTICLE_COLUMN_WIDTH_PX / 3)   # ≈ 267
ARTICLE_THREE_IMAGE_PX = 240         # each register image in its column
# Subheading spacing (owner 2026-07-14 round two): the heading sits
# CENTERED and visibly closer to ITS paragraph than to the previous one
# — Qt collapses adjacent block margins to the larger, so the paragraph
# after a heading carries the same small top margin.
ARTICLE_SUBHEAD_GAP_ABOVE_PX = 18
ARTICLE_SUBHEAD_GAP_BELOW_PX = 2

# The Astrology/Ascendant hover image trio (owner 2026-07-13): the
# ACTIVE style's art large in the middle, the two remaining styles
# small at its sides.
ASTRO_MAIN_IMAGE_PX = 256
ASTRO_SIDE_IMAGE_FRACTION = 0.35
PERIOD_EARTH_IMAGE_PX = 128          # the Day/Night hover carries a mini Earth
                                     # of the active region (owner 2026-07-12)
ARTICLE_TITLE_PX = 17                # the entity NAME above the article (owner
                                     # spec 2026-07-11: a slightly bigger title,
                                     # then a margin, then the prose)

# --- Legend term highlighting (owner spec 2026-07-12) ------------------------------
# Canon terms POP inside article prose: virtues bold blue, vices bold
# red, moods/emotions bold yellow, color words bold in their own color.
# Applied at RENDER time over the English and Serbian originals (the
# machine-translated languages read plain); hex notes like "(#F8E600)"
# are stripped from the display. Patterns are regex fragments, ALL
# matched case-insensitively (owner report 2026-07-12: a lowercase
# "gordost" must burn red too); Serbian fragments cover the case
# endings including the -šću instrumentals.
# THE LEGEND BOLD LAW (owner 2026-07-26, CUBE.md §Display and Legend
# Laws — supersedes the 2026-07-12 rainbow): emphasis in article prose
# is BOLD ONLY, and ONLY on the web's spine — the virtue, the vice, the
# emotion/mood and the WEEKDAY. Everything else (color words, figure
# names) reads plain.
LEGEND_TERM_PATTERNS = {
    "virtue": (
        "Humility", "Justice", "Generosity", "Wisdom", "Courage",
        "Serenity", "Love", "Patience", "Faith", "Hope",
        "Poniznost(?:i)?", "Poniznošću", "Pravednost(?:i)?", "Pravednošću",
        "Velikodušnost(?:i)?", "Velikodušnošću",
        "Mudrost(?:i)?", "Mudrošću", "Hrabrost(?:i)?", "Hrabrošću",
        "Spokoj(?:a|u|em)?", "Ljubav(?:i|lju)?", "Strpljenj[eau]",
        "Strpljenjem", "Ver[aeiu]", "Verom", "Nad[aeiu]", "Nadom",
    ),
    "vice": (
        "Pride", "Servility", "Excess", "Greed", "Wrath", "Fear",
        "Jealousy", "Envy",
        "Gordost(?:i)?", "Gordošću", "Pokornost(?:i)?", "Pokornošću",
        "Neumerenost(?:i)?", "Neumerenošću",
        "Pohlep[aeiou]", "Pohlepom", "Gnev(?:a|u|om)?", "Strah(?:a|u|om)?",
        "Ljubomor[aeiou]", "Ljubomorom", "Zavist(?:i)?", "Zavišću",
    ),
    "mood": (
        "Joy", "Zeal", "Passion", "Sorrow", "Calm", "Renewal", "Glory",
        # Awe is the renamed servant mood (2026-07-14); Eclipse stays
        # matchable for The Ninth Mood's own article.
        "Awe", "Eclipse", "Longing",
        "Radost(?:i)?", "Radošću", "Žar(?:a|u|om)?",
        "Strast(?:i)?", "Strašću",
        "Tug[aeiou]", "Tugom", "Mir(?:a|u|om)?", "Obnov[aeiou]", "Obnovom",
        "Sjaj(?:a|u|em)?", "Strahopoštovanj[eau]", "Strahopoštovanjem",
        "Pomračenj[eau]", "Pomračenjem",
        "Čežnj[aeiou]", "Čežnjom",
    ),
    # THE WEEKDAY-TITLE LAW's prose half (owner 2026-07-26): weekday
    # names are part of the spine and pop bold wherever they appear.
    # (Serbian "nedelja" also means "week" — an accepted over-match;
    # the shipped originals rarely use it outside the day sense.)
    "weekday": (
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
        "Ponedeljak", "Ponedeljk(?:a|u|om)",
        "Utorak", "Utork(?:a|u|om)",
        "Sred[aeiou]", "Sredom",
        "Četvrtak", "Četvrtk(?:a|u|om)",
        "Petak", "Petk(?:a|u|om)",
        "Subot[aeiou]", "Subotom",
        "Nedelj[aeiou]", "Nedeljom",
    ),
}

# The Legend popup (replaces QToolTip, owner decision): capped to these
# screen fractions — taller content scrolls instead of clipping off a
# small screen; dark tooltip styling.
LEGEND_MAX_WIDTH_FRACTION = 0.45
LEGEND_MAX_HEIGHT_FRACTION = 0.85
LEGEND_CURSOR_OFFSET_PX = 14
LEGEND_PADDING_PX = 8
# THE HOVER TEASER LAW (owner 2026-07-26, CUBE.md §Display and Legend
# Laws): an article hover speaks only its THESIS — this many sentences
# of the first paragraph — and closes with the LEARN MORE / SPACE
# footer; the full article lives in the Encyclopedia.
LEGEND_TEASER_SENTENCES = 2

# The Encyclopedia article view (owner UX rounds 2026-07-12/13): the
# text BLOCK hugs the LEFT edge and spans this fraction of the window
# width — the prose reflows to fill it (no fixed wrap); the font grows
# with the width at a gentle em-like coefficient between the base and
# the cap.
ENCYCLOPEDIA_TEXT_WIDTH_FRACTION = 0.9
ENCYCLOPEDIA_BASE_FONT_PX = 13
ENCYCLOPEDIA_FONT_GROWTH = 0.006     # extra px per viewport px above the base width
ENCYCLOPEDIA_FONT_BASE_WIDTH = 560   # viewport width where the base font applies
ENCYCLOPEDIA_MAX_FONT_PX = 21
# The topic gallery cards (owner 2026-07-13: everything centered, the
# thumbnails RESPONSIVE — they grow/shrink with the window between the
# two bounds; below the minimum the scrollbar takes over).
ENCYCLOPEDIA_TOPIC_ICON_MIN_PX = 72
ENCYCLOPEDIA_TOPIC_ICON_MAX_PX = 200
# DECODE CEILINGS (owner order 2026-07-26: entering the Encyclopedia
# must never block or crash — full-res sources decoded straight into
# QPixmaps both stalled the first paint and piled up RAM). A gallery
# card never SHOWS more than ICON_MAX_PX, a reader image never more
# than the viewport at max zoom — decoding past 2× those sizes buys
# nothing. The background warm (`app.encyclopedia_warm`) pre-builds
# disk-cached downscales at these widths; the dialog reads them when
# present and falls back to the original (full-res, but only until the
# warm catches up) rather than paying a cold downscale on the GUI
# thread.
ENCYCLOPEDIA_CARD_ICON_DECODE_PX = 400    # 2× ENCYCLOPEDIA_TOPIC_ICON_MAX_PX
ENCYCLOPEDIA_READER_DECODE_CEILING_PX = 1600   # ~viewport height × max zoom
# LAYOUT fix round R3 (owner: "788px width, tiles clipping" — that class
# dies here); the WIDTH ARITHMETIC corrected round R8b item 5a (the
# original formula silently dropped the inter-card spacing and the
# gallery column's own margins, reliably overflowing the frame by
# ~100px — the "X scroll again" regression): a group NEVER spills more
# than this many cards per row — it WRAPS instead, never a horizontal
# scrollbar. `app.encyclopedia._gallery_content_width`/
# `_gallery_icon_ceiling` (one matched pair, Rule #5) are the ONE
# correct formula, both for the dialog's own MIN WIDTH
# (`EncyclopediaDialog.__init__`) and the live per-resize icon ceiling
# (`_rescale_topics`, zoom-clamped).
ENCYCLOPEDIA_GALLERY_MAX_COLUMNS = 4
ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX = 40   # matches _rescale_topics' + 40/+44

# --- THE COMPUTED DIAGRAMS (owner verdict 2026-07-29) -----------------------
# Twenty-three Encyclopedia pages are COMPOSITIONS the canon exempted
# from generation (CUBE.md, Session 25, root Rule #19). They are drawn
# live from `config.cube`'s own coordinates instead — see
# `render/cube_diagrams.py`. Every number here is a RATIO of the plate's
# own side, so one drawing serves every zoom level and every window.
CUBE_DIAGRAM_UNIT_RATIO = 0.185     # one cube step, as a share of the side
CUBE_DIAGRAM_NODE_RATIO = 0.055     # a cell's dot radius, per unit
CUBE_DIAGRAM_LABEL_RATIO = 0.30     # a label's pixel size, per unit
CUBE_DIAGRAM_LABEL_PUSH = 0.55      # how far outward a pole's name sits
CUBE_DIAGRAM_FRAME_OPACITY = 0.35   # the cube's twelve edges
CUBE_DIAGRAM_DIM_OPACITY = 0.30     # the cells an axis page does not light
CUBE_DIAGRAM_SIDE_PX = 900          # the drawing's own square, then scaled
CUBE_DIAGRAM_MARGIN_PX = 8          # no label is ever drawn past this edge
# The second diagram wave — the journeys and the tables
# (`render/canon_diagrams.py`).
CANON_DIAGRAM_RING_RATIO = 0.34     # the arms' own radius, per plate side
CANON_DIAGRAM_LABEL_RATIO = 0.026   # a station's name, per plate side
CANON_DIAGRAM_TABLE_RATIO = 0.022   # a table cell, per plate side
CANON_DIAGRAM_TABLE_MARGIN = 0.05   # the table's own inset

# --- THE SESSION 27 REWORK (owner-sealed 2026-07-28) -------------------------
# Three levels — nine WHOLES (Session 35, 2026-07-29), their THEME
# cards, then the article slider.
#
# THE WINDOW'S OWN MINIMUM IS THE OWNER'S OPENING SCREEN (his spec:
# "Pocetni ekran 16:9 rezolucija 1280 x 720p", "Prvi ekran nema scroll...
# min size je minimalni zoom out"). Pinning the minimum AT that
# resolution is what turns "the home screen never scrolls" from a hope
# into geometry: the 3x3 grid is measured from the viewport, and the
# viewport can never be smaller than the layout the owner specified.
ENCYCLOPEDIA_MIN_WIDTH_PX = 1280
ENCYCLOPEDIA_MIN_HEIGHT_PX = 720
# 3 rows x 3 columns = the nine wholes (Session 35, "može i 9 grupacija
# sa ovim novim velikim sekcijama"). Geometry still holds at the
# 1280x720 minimum: 3 rows x ENCYCLOPEDIA_CARD_MIN_HEIGHT_PX (150) + 4 x
# ENCYCLOPEDIA_CARD_GAP_PX (20) gaps = 530px, well under the 720 floor.
ENCYCLOPEDIA_HOME_COLUMNS = 3
# The card itself. The edge is the whole's own Rose accent — a hairline
# at rest (EDGE_ALPHA), lit on hover, with a tinted wash behind it.
ENCYCLOPEDIA_CARD_GAP_PX = 20
ENCYCLOPEDIA_CARD_PAD_PX = 12
ENCYCLOPEDIA_CARD_RADIUS_PX = 14
ENCYCLOPEDIA_CARD_EDGE_PX = 1
ENCYCLOPEDIA_CARD_EDGE_ALPHA = 90         # 0-255, the resting hairline
ENCYCLOPEDIA_CARD_HOVER_WASH_ALPHA = 46   # 0-255, the hover tint
ENCYCLOPEDIA_CARD_MIN_WIDTH_PX = 180
ENCYCLOPEDIA_CARD_MIN_HEIGHT_PX = 150
ENCYCLOPEDIA_CARD_IMAGE_MIN_PX = 60
ENCYCLOPEDIA_CARD_IMAGE_RATIO = 0.62   # plate height per card width (theme grid)
ENCYCLOPEDIA_CARD_FONT_RATIO = 0.038   # card font grows with the card's width
ENCYCLOPEDIA_CARD_TITLE_BUMP = 3       # the title sits this much above the body
# THE HOME CARD'S PLATE — COMPUTED, not generated (root Rule #19): a
# whole's tile is a 2x2 mosaic of its OWN theme plates, built live and
# cached in memory, so the nine wholes need no artwork to exist. A hand
# drawn plate dropped at `<whole key>.png` under this directory WINS —
# the same graceful-upgrade contract every derived asset here has.
ENCYCLOPEDIA_WHOLE_ART_DIR = paths.assets_dir() / "instrument" / "wholes"
ENCYCLOPEDIA_MOSAIC_PX = 512           # the composed tile's own side
ENCYCLOPEDIA_MOSAIC_GAP_PX = 6
# Modern reader buttons (owner 2026-07-14: "veći, upečatljiviji,
# življih boja — ne kao app iz 1990-e"): vivid gradient pills shared by
# the Encyclopedia and the Guide. Each role owns a (top, bottom)
# gradient pair; hover lightens and pressed darkens the same pair.
UI_BUTTON_FONT_PX = 17
UI_BUTTON_RADIUS_PX = 12
UI_BUTTON_PADDING_PX = (10, 26)         # vertical, horizontal
UI_BUTTON_SMALL_FONT_PX = 14            # the per-entry look arrows
UI_BUTTON_SMALL_PADDING_PX = (5, 12)
THEME_RADIUS_CONTROL_PX = 8      # buttons, inputs, combos
THEME_RADIUS_CARD_PX = 14        # group-box cards
THEME_RADIUS_PILL_PX = 999       # nav selection pill, checkbox indicator
# Reader image ceiling (owner imperative 2026-07-14): no article or
# Guide image may eat the page — anything taller than this fraction of
# the viewport height scales down to it, leaving room for the text.
# Round two: the WHOLE image grid shares the ceiling — stacked rows
# split it, so the Week's Sunday pairs still leave the text visible.
READER_IMAGE_MAX_HEIGHT_FRACTION = 0.35
# The unlocked hidden mode (owner 2026-07-16, top-only round): hovering
# within this many degrees of the 12h ring letter opens the Four
# Greetings. The hit zone is the LETTER band OUTSIDE the tick scale
# (owner round two: the ticks at that angle must keep their own
# day/year/moon reading), and the stanzas breathe with a small margin,
# not a full blank line. The 24h (Omega) letter no longer answers this
# hover — that spot now carries the reveal-week double-click below.
GREETINGS_LETTER_HALF_DEG = 6.0
GREETINGS_LETTER_OUTER_FRACTION = 1.08
GREETINGS_STANZA_GAP_PX = 6


# --- Hover article warm sweep (owner 2026-07-18) --------------------------------
# The background pre-build of every hover article (compositor
# .warm_hover_articles): a polar probe grid over the whole dial, walked
# through the real tooltip dispatch. 180 angles x 40 rings keeps the
# pitch under half the smallest hover target (the Moon marker) at every
# supported diameter; the per-ring pause keeps the sweep slow and
# polite — image by image, never a CPU burst at startup.
HOVER_WARM_ANGLE_STEPS = 180
HOVER_WARM_RADIAL_STEPS = 40
HOVER_WARM_RING_PAUSE_S = 0.05



# --- THE INSTRUMENT'S OWN DIAGRAMS (Session 27 coverage round, 2026-07-29) ----
# The seven "how this clock works" pages plus the Great Oscillations are
# COMPUTED, not painted (root Rule #19 — see render/instrument_diagrams.py).
# These are that module's only tunables; every astronomical number in the
# figures comes from `config.constants` or from the bundles themselves.
INSTRUMENT_DIAGRAM_SIDE_PX = 900        # the drawing's own square, then scaled
INSTRUMENT_DIAGRAM_MARGIN_PX = 8        # no label is drawn past this edge
INSTRUMENT_DIAGRAM_RING_RATIO = 0.34    # the dial circle's radius, per side
INSTRUMENT_DIAGRAM_YEAR_RING_RATIO = 0.27  # ...tighter on the year wheel,
#                                          whose anchor names are long and
#                                          two of them stand at the widest
#                                          point of the disc
INSTRUMENT_DIAGRAM_LABEL_RATIO = 0.026  # a label's pixel size, per side
INSTRUMENT_DIAGRAM_CAPTION_RATIO = 0.022
INSTRUMENT_DIAGRAM_CAPTION_Y = 0.90     # where the one-line caption sits
INSTRUMENT_DIAGRAM_GLYPH_RATIO = 0.075  # a ring letter, per side
INSTRUMENT_DIAGRAM_MOON_RATIO = 0.045   # one phase disc's radius, per side
INSTRUMENT_DIAGRAM_PHASE_STEPS = 8      # phases shown around the lunation
INSTRUMENT_DIAGRAM_CHART_INSET = 0.10   # the envelope plot's own margin
INSTRUMENT_DIAGRAM_CHART_HEIGHT = 0.62  # ...and its height, per side
# The moment drawn on the dial figure — any time whose two hands stand
# clearly apart reads the lesson (the hour hand is on ITS OWN 24-hour
# turn, the minute hand on the hour's).
INSTRUMENT_DIAGRAM_SAMPLE_TIME = (15, 20)
# The solar tilt drawn on the rotation figure: the project's own golden
# value (Belgrade under DST, tests/test_dial.py) rather than a made-up
# angle — the figure is a measurement.
INSTRUMENT_DIAGRAM_SAMPLE_TILT_DEG = 10.76
# THE TWILIGHT BANDS: (from, to, name) in degrees of solar depression.
# Civil comes from `constants.CIVIL_DEPRESSION` — the one the dial
# actually draws; the other two boundaries are the standard astronomical
# definitions and live here because nothing else in the program needs
# them.
INSTRUMENT_TWILIGHT_BANDS = (
    (0.0, constants.CIVIL_DEPRESSION, "civil"),
    (constants.CIVIL_DEPRESSION, 12.0, "nautical"),
    (12.0, 18.0, "astronomical"),
)
