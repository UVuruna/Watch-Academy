"""The Encyclopedia's STATIC page tables.

One responsibility: WHAT pages exist and which plate each one wears —
the seasons, the sun's turning points, the eras, the two eclipse
families, the four Cube-canon sets and the emblem/week tables. Nothing
here builds a widget or reads the clock; the builders next door turn
these tuples into topic entries.

Split out of the old 2,766-line `app/encyclopedia.py` in the Session 27
rework (root Rule #20 — a file is one cohesive unit). The tables
themselves moved VERBATIM: their comments carry the owner decisions that
argued every entry, and the entry ORDER of several of them is a
contract (see `config/encyclopedia_tree.py`).

Layer: app. Documentation: pages.md.
"""

from config import archetypes, constants, defaults

# The SEASONS topic (owner 2026-07-13; split 2026-07-16, ROADMAP queue
# #10): the year's quarters, the tropics' halves and the measured twins
# — the turning points moved to the SUN topic below. Badges from
# assets/badge/season/, articles from encyclopedia.json.
_SEASON_ENTRIES = (
    ("Spring", "Spring.png"),
    ("Summer", "Summer.png"),
    ("Autumn", "Autumn.png"),
    ("Winter", "Winter.png"),
    ("Wet_Season", "Wet_Season.png"),
    ("Dry_Season", "Dry_Season.png"),
    ("Meteorological", None),          # four badges in one entry
)

# The SUN topic (owner 2026-07-16, ROADMAP queue #10): the turning
# points — the two solstices and the shared-badge equinox.
_SUN_ENTRIES = (
    ("Summer_Solstice", "turning_point/Summer_Solstice.png"),
    ("Winter_Solstice", "turning_point/Winter_Solstice.png"),
    ("Equinox", "turning_point/Equinox.png"),
)

# The ERA TERMS topic (ROADMAP 15a3, owner 2026-07-17): the two AGES
# and the four STARRY SEASONS carry an emblem each. Badges from
# assets/era/ (research/prompts/era/era_prompts.md).
# The comparative "Eras of the World" essay carries no plate of its
# own — instead it strings the calendar-system emblems the essay
# compares (owner fix-round B, 2026-07-19, TASK 3; Maya added the MAYA
# round, owner 2026-07-20; Kali Yuga/Olympiad/Unix added the ERA-TRIO
# round, owner 2026-07-20): graceful-absent until PromptPainter
# generates assets/era/calendar/*.png. Every entry here (Byzantine
# included) rotates through `_era_image` below like the six Age/Starry
# plates — the Byzantine v2 emblem (ERA-TRIO round) is a same-named
# `calendar/alt/Byzantine.png` sibling, discovered automatically, no
# second entry needed here.
_ERA_CALENDAR_ART = (
    "calendar/AUC.png",
    "calendar/Byzantine.png",
    "calendar/Hebrew.png",
    "calendar/Hegirae.png",
    "calendar/Buddhist.png",
    "calendar/Huangdi.png",
    "calendar/Maya.png",
    "calendar/KaliYuga.png",
    "calendar/Olympiad.png",
    "calendar/Unix.png",
)
_ERA_ENTRIES = (
    ("Age_of_Light", "Age_of_Light.png"),
    ("Age_of_Darkness", "Age_of_Darkness.png"),
    ("Starry_Spring", "Starry_Spring.png"),
    ("Starry_Summer", "Starry_Summer.png"),
    ("Starry_Autumn", "Starry_Autumn.png"),
    ("Starry_Winter", "Starry_Winter.png"),
    ("Eras_of_the_World", _ERA_CALENDAR_ART),
    # The Great Oscillations (fix round F, owner "bravo"): the season-
    # length / Milankovitch essay near the Observatory. Its figure is
    # the La2004 amplitude envelope — the SAME series the Observatory
    # plots — so the page names a DRAWER, not a plate (owner verdict
    # 2026-07-29, root Rule #19: a painted chart is a picture of a
    # number that changes when the bundle changes). A row is
    # (key, art) or (key, art, diagram).
    ("The_Great_Oscillations", None, ("instrument", "oscillations")),
)

# THE ECLIPSES ENCYCLOPEDIA (fix round F, owner order 2026-07-19:
# "posebno za mesec i sunce"): two topics, one per body, each opened
# by a per-body OVERVIEW (the entry-zero — a whole-phenomenon page a
# reader meets before the specific kinds) then one chapter per category
# we distinguish. Each category chapter wears its OWN category emblem
# (assets/eclipse/<Stem>.png, graceful-absent); the overview strings its
# body's category emblems as a strip, like the Eras essay. The chapter
# ORDER here is the golden the Spacebar jump indexes into
# (render.compositor._ENC_ECLIPSE_SOLAR_ORDER / _LUNAR_ORDER) — keep
# them in lockstep.
_ECLIPSE_SOLAR_EMBLEMS = (
    "Solar_Total.png", "Solar_Annular.png",
    "Solar_Partial.png", "Solar_Hybrid.png",
)
_ECLIPSE_LUNAR_EMBLEMS = (
    "Lunar_Total.png", "Lunar_Partial.png", "Lunar_Penumbral.png",
)
_ECLIPSE_SOLAR_ENTRIES = (
    ("Solar_Overview", _ECLIPSE_SOLAR_EMBLEMS),
    ("Solar_Total", "Solar_Total.png"),
    ("Solar_Annular", "Solar_Annular.png"),
    ("Solar_Partial", "Solar_Partial.png"),
    ("Solar_Hybrid", "Solar_Hybrid.png"),
)
_ECLIPSE_LUNAR_ENTRIES = (
    ("Lunar_Overview", _ECLIPSE_LUNAR_EMBLEMS),
    ("Lunar_Total", "Lunar_Total.png"),
    ("Lunar_Partial", "Lunar_Partial.png"),
    ("Lunar_Penumbral", "Lunar_Penumbral.png"),
)
_ECLIPSE_TOPICS = (
    ("eclipse_solar", "Solar Eclipses", "Solar_Total.png",
     _ECLIPSE_SOLAR_ENTRIES),
    ("eclipse_lunar", "Lunar Eclipses", "Lunar_Total.png",
     _ECLIPSE_LUNAR_ENTRIES),
)

# THE CUBE CANON TOPICS (WORKPLAN Session 21, 2026-07-27 — CUBE.md).
# (name, art) per entry; `None` art means the page has no plate of its
# own, exactly like the era essays — the Cube's axes, poles and
# vertices have no prompt sheet yet, while the Two Crosses' twelve
# stations and centres were declared by the Session 19 sheet and light
# up the moment the owner's glass lands (graceful-absent throughout).
#
# SESSION 25 (2026-07-28) grew the section from 20 pages to 42 — the
# Thirteen Axes wave: the doctrine block (the axes' arithmetic, The One
# in both descriptions, the Sacred Axis, the 65 terms), the nine new
# axis pages, the eight new edge cells and the hexagram projection. The
# READING ORDER is `config.cube.AXES`' own family order — doctrine, the
# three primaries with their poles, the six edge axes with the eight new
# cells, the four vertex axes with their corners, then what the cube
# reveals. The Sacred Axis' two cells open the corner block as its HUMAN
# ECHOES, because the axis itself stands up front beside The One.
#
# THE ORDER IS A CONTRACT: `config/archetypes.py` addresses these pages
# by index from its three Cube wheels (`enc=("cube", 11)` and friends),
# so an inserted entry must be added at the END or the wheels re-aimed
# in the same commit — `tests/test_cube_encyclopedia.py` pins the pairs
# BY NAME, so a mis-aimed index fails loudly rather than silently.
_CUBE_ENTRIES = (
    ("The Cube", None, ("cube", "")),
    ("The Thirteen Axes", None, ("axes", "")),
    ("The One", archetypes.SACRED_ART_DIR / "The_One.png"),
    ("The Sacred Axis", archetypes.SACRED_ART_DIR / "Sacred_Axis.png"),
    ("The Sixty-Five Terms", None, ("terms", "")),
    ("The Three Sets", None, ("sets", "")),
    ("The Activation Axis", None, ("axis", "Activation")),
    # THE ACTIVATION POLES ARE 3D, NOT PLATES (owner decree 2026-07-29:
    # "ovo će biti animacija izrađena uz pomoć Gadgets/3D Previewer").
    # The Character wheel is the Cube with this axis at zero, so these
    # two ends have no lancet and never will — the whole Cube family
    # goes to the rotating previewer. Until it lands they show the
    # COMPUTED cube with their own seat lit, which is the one thing a
    # flat figure can honestly say about a 3D position.
    ("Composure", None, ("pole", "Composure")),
    ("Vigor", None, ("pole", "Vigor")),
    ("The Moral Scope Axis", None, ("axis", "Moral Scope")),
    ("Integrity", archetypes.CHARACTER_ART_DIR / "Integrity.png"),
    ("Loyalty", archetypes.CHARACTER_ART_DIR / "Loyalty.png"),
    ("The Self-Regard Axis", None, ("axis", "Self-Regard")),
    ("Humility", archetypes.CHARACTER_ART_DIR / "Humility.png"),
    ("Dignity", archetypes.CHARACTER_ART_DIR / "Dignity.png"),
    # The six EDGE axes. An axis page carries no plate of its own by the
    # Rule #19 derivation check (an axis IS its two ends through the
    # centre — a composition, never a new scene); the eight new CELLS do,
    # and light up when `research/prompts/archetype/edges_prompts.md` is
    # generated.
    ("Reason ↔ Emotion", None, ("axis", "Reason ↔ Emotion")),
    ("Prudence", archetypes.EDGES_ART_DIR / "Prudence.png"),
    ("Ardor", archetypes.EDGES_ART_DIR / "Ardor.png"),
    ("Pragmatism ↔ Idealism", None, ("axis", "Pragmatism ↔ Idealism")),
    ("Steadfastness", archetypes.EDGES_ART_DIR / "Steadfastness.png"),
    ("Reform", archetypes.EDGES_ART_DIR / "Reform.png"),
    ("Person ↔ Cause", None, ("axis", "Person ↔ Cause")),
    ("Hearth ↔ Desert", None, ("axis", "Hearth ↔ Desert")),
    ("Lion ↔ Lamb", None, ("axis", "Lion ↔ Lamb")),
    ("Meekness", archetypes.EDGES_ART_DIR / "Meekness.png"),
    ("Aspiration", archetypes.EDGES_ART_DIR / "Aspiration.png"),
    ("Servant ↔ Sovereign", None, ("axis", "Servant ↔ Sovereign")),
    ("Self-Mastery", archetypes.EDGES_ART_DIR / "Self_Mastery.png"),
    ("Diligence", archetypes.EDGES_ART_DIR / "Diligence.png"),
    # The four VERTEX axes and their corners.
    ("The Contemplative Sage",
     archetypes.VERTICES_ART_DIR / "Contemplative_Sage.png"),
    ("The Charismatic Champion",
     archetypes.VERTICES_ART_DIR / "Charismatic_Champion.png"),
    ("Vow ↔ Vision", None, ("axis", "Vow ↔ Vision")),
    ("The Quiet Devotee",
     archetypes.VERTICES_ART_DIR / "Quiet_Devotee.png"),
    ("The Visionary Founder",
     archetypes.VERTICES_ART_DIR / "Visionary_Founder.png"),
    ("Preservation ↔ Revolution", None, ("axis", "Preservation ↔ Revolution")),
    ("The Steady Guardian",
     archetypes.VERTICES_ART_DIR / "Steady_Guardian.png"),
    ("The Principled Reformer",
     archetypes.VERTICES_ART_DIR / "Principled_Reformer.png"),
    ("Crown ↔ Shield", None, ("axis", "Crown ↔ Shield")),
    ("The Wise Statesman",
     archetypes.VERTICES_ART_DIR / "Wise_Statesman.png"),
    ("The Sacrificial Protector",
     archetypes.VERTICES_ART_DIR / "Sacrificial_Protector.png"),
    ("The Hexagram Projection", None, ("hexagram", "")),
    ("The Banknote Axes", None, ("banknote", "")),
)
_DOUBLE_TRINITY_ENTRIES = (
    ("The Double Trinity", None, ("trinity", "")),
    ("The Court", archetypes.center("trinity_primary")["file"]),
    ("Genesis", archetypes.center("trinity_genesis")["file"]),
    ("The Council", archetypes.center("prism_council")["file"]),
    ("The Twenty-Four Fields", None, ("fields", "")),
)
_CROSSES_ENTRIES = (
    ("The Two Crosses", None, ("crosses", "The Two Crosses")),
    ("The Path of Light", archetypes.CROSSES_ART_DIR / "Path_of_Light.png"),
    ("Hope", archetypes.CROSSES_ART_DIR / "Hope.png"),
    ("Faith", archetypes.CROSSES_ART_DIR / "Faith.png"),
    ("Love", archetypes.CROSSES_ART_DIR / "Love.png"),
    ("Salvation", archetypes.CROSSES_ART_DIR / "Salvation.png"),
    ("The Path of Darkness",
     archetypes.CROSSES_ART_DIR / "Path_of_Darkness.png"),
    ("Fear", archetypes.CROSSES_ART_DIR / "Fear.png"),
    ("Anger", archetypes.CROSSES_ART_DIR / "Anger.png"),
    ("Hate", archetypes.CROSSES_ART_DIR / "Hate.png"),
    ("Suffering", archetypes.CROSSES_ART_DIR / "Suffering.png"),
    ("Trust and Distrust", archetypes.CROSSES_ART_DIR / "Trust.png"),
    ("FALL and STAR", None, ("crosses", "FALL and STAR")),
    ("DOMY and SAFE", None, ("crosses", "DOMY and SAFE")),
)
# THE ONE SOUL THEME (owner verdict 2026-07-27: "napravi naravno — jedna
# od važnijih ljubavnih tematika"). The prism-SECONDARY wheel's own doctrine
# at last gets an Encyclopedia home: the theme's title page, the six
# pillars in the wheel's own arm order (12h, 16h, 20h, 24h, 04h, 08h),
# the Union at the centre and the Child as the Ninth — CANON.md §Prism
# light, `research/bond_theme.md`. The dial's per-arm HOVER articles
# (`symbolism.json` `archetype_prism_secondary`) are untouched: they read one
# seat, these pages argue the DOCTRINE (the conjugation law, the axes of
# love, the shadows, the union) — Rule #5, no text is duplicated.
#
# THE ORDER IS A CONTRACT here too: `config/archetypes.py`'s prism_secondary
# figures address these pages by INDEX (`enc=("one_soul", 1)` ...), the
# centre included — `tests/test_one_soul_theme.py` pins both ends.
#
# The eight seat pages all carry the wheel's OWN art (the one_soul
# family is fully drawn); only the title page has no plate, exactly like
# every other overview page in this hall.
_ONE_SOUL_ENTRIES = (
    (constants.ONE_SOUL_THEME_TITLE,
     archetypes.ONE_SOUL_ART_DIR / "Title.png"),
    ("Gratitude", archetypes.ONE_SOUL_ART_DIR / "Gratitude.png"),
    ("Support", archetypes.ONE_SOUL_ART_DIR / "Support.png"),
    ("Passion", archetypes.ONE_SOUL_ART_DIR / "Passion.png"),
    ("Tolerance", archetypes.ONE_SOUL_ART_DIR / "Tolerance.png"),
    ("Trust", archetypes.ONE_SOUL_ART_DIR / "Trust.png"),
    ("Respect", archetypes.ONE_SOUL_ART_DIR / "Respect.png"),
    ("The Union", archetypes.ONE_SOUL_ART_DIR / "Union.png"),
    ("The Child", archetypes.ONE_SOUL_ART_DIR / "Child.png"),
)
# (topic key, reader/gallery TITLE, TILE title or None, gallery icon,
# `encyclopedia.json` family, entries). The tile title exists for ONE
# reason (owner seal 2026-07-27, CANON §Prism secondary): the One Soul theme
# is TITLED IN FULL with the triple — which is what the reader's own top
# header shows — while a LABEL that must stand alone says "One Soul", and
# a fixed-size gallery card is such a label.
_ARCHETYPE_TOPICS = (
    ("cube", "The Cube", None,
     archetypes.CHARACTER_ART_DIR / "Integrity.png", "cube",
     _CUBE_ENTRIES),
    ("double_trinity", "The Double Trinity", None,
     archetypes.center("prism_council")["file"], "double_trinity",
     _DOUBLE_TRINITY_ENTRIES),
    ("crosses", "The Two Crosses", None,
     archetypes.CROSSES_ART_DIR / "Path_of_Light.png", "crosses",
     _CROSSES_ENTRIES),
    ("one_soul", constants.ONE_SOUL_THEME_TITLE,
     constants.ONE_SOUL_THEME_NAME,
     archetypes.center("prism_secondary")["file"], "one_soul",
     _ONE_SOUL_ENTRIES),
)

# The WEEK page image strip (owner spec: each day gathers everything it
# owns): planet render, planet sign, then the day's virtue / sin / mood
# emblems — Sunday, the dual day, carries both of each.
_WEEK_EMBLEMS = {
    "sun": (("Justice", "Humility"), ("Pride", "Servility"),
            ("Glory", "Awe")),
    "moon": (("Serenity",), ("Fear",), ("Calm",)),
    "mars": (("Courage",), ("Wrath",), ("Zeal",)),
    "mercury": (("Wisdom",), ("Greed",), ("Sorrow",)),
    "jupiter": (("Generosity",), ("Excess",), ("Joy",)),
    "venus": (("Love",), ("Jealousy",), ("Passion",)),
    "saturn": (("Patience",), ("Envy",), ("Renewal",)),
}
_VSM_DAYS = {
    "virtues": ("Justice", "Humility", "Serenity", "Courage", "Wisdom",
                "Generosity", "Love", "Patience"),
    "sins": ("Pride", "Servility", "Fear", "Wrath", "Greed", "Excess",
             "Jealousy", "Envy"),
    "moods": ("Glory", "Awe", "Calm", "Zeal", "Sorrow", "Joy",
              "Passion", "Renewal"),
}
_INSTRUMENT_KEYS = (
    "dial", "solar_rotation", "twilight", "year_wheel", "moon_lunations",
    "paint_light", "metals", "ring_letters",
)


_WEEK_ORDER = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")

# THE SPACE-JUMP INDEX REMAP (owner contract, round R3 restructure,
# item 9): `render.compositor._weekday_encyclopedia_target` (out of
# this round's scope) still returns the OLD raw index — sun=0,
# moon=1..saturn=6 (`_ENC_WEEK_ORDER`, unaware of the restructure).
# `_weekday_topic`'s new order happens to leave Monday..Saturday at
# that SAME index (Title only pushes in at 0; Sunday moves OUT to the
# end) — only raw index 0 (the Sun) needs remapping, to the GOOD
# (Ruler) half's new seat: Title(0) + Mon..Sat(1-6) + Duality title(7)
# + Good(8) [+ Evil(9) — round R3b item 1 split, EVIL is not a jump
# target of its own: a Spacebar press always lands on GOOD, matching
# the pre-split "jump to the merged dual page" intent]. Applied once
# in `__init__`. The GOOD half happens to land on the SAME raw index
# (8) the R3 merged dual page used to occupy — pure coincidence of the
# arithmetic (title+6+duality-title=8), not a second meaning read into
# the number.
_WEEKDAY_DUAL_PAGE_INDEX = 8
# Every `_weekday_topic`-built topic — every WEEKDAY_THEME_TITLES key
# EXCEPT virtues/sins/moods (those get OVERWRITTEN by the emblem-family
# pass in `_topics()` below and are never weekday-shaped in the end).
_WEEKDAY_RESTRUCTURED_TOPICS = frozenset(defaults.WEEKDAY_THEME_TITLES) - {
    "virtues", "sins", "moods",
}

# THE NINTH SEAT'S PHILOSOPHICAL NAME (owner decree 2026-07-20, round
# R3): across every theme the Ninth is the SAME archetype underneath
# its many costumes (CANON.md "The Ninth — Outside the Circle") — a
# potential member who never found its place and was never found BY
# the eight, the union or the exile alike. UV/INSTRUCTION.txt #7 walks
# the case studies: the Sigma wolf is a potential leader with no pack,
# the shepherd with no flock, the sailor with no sea, Freemasonry's own
# undefined god (the Unknown God, Ancient religions), the profession
# that knows a little of everything and is master of none, the
# existential intelligence that questions every OTHER intelligence,
# the virtue of Balance/objectivity (never loving, trusting or giving
# too much OR too little), the sin of WISH — the root every other sin
# grows from (wanting to be loved: servility; wanting to rule: pride;
# wanting what others have or keeping what is one's own: envy/
# jealousy). The sealed name for this position is **The Unfound**.
# Alternatives discussed and rejected the same evening: **The
# Uncalled** (implies someone else's failure to call, not the figure's
# own unsettled nature), **The Ninth Door** (a place, not a person —
# most Ninths ARE persons), **The Seeker** (too active/heroic — several
# Ninths, like Melchizedek or the Union badges, are not searching for
# anything), **The Unclaimed** (close, but reads as ownable property
# rather than a member who could belong and does not) — "The Unfound"
# won because it holds BOTH readings the owner insisted on keeping
# open at once (never found itself / never found by others), where
# every alternative above only covers one.
NINTH_SEAT_PHILOSOPHICAL_NAME = "The Unfound"

# THE GOD-TOPIC GALLERY TITLE (owner round R8b item 6): "Ubuduce posto
# ce biti podnaslov Gods onda ce nazivi biti samo Greek, Egypt, Norse
# ... itd" — with a "Gods" SUBGROUP heading now sitting above these four
# cards (`_GALLERY_SUBGROUPS` below, item 5c), the "gods" suffix is
# redundant on the tile itself. This overrides ONLY the gallery card
# text and the reader's own top header (`_topic_display_title`) — every
# OTHER reader of `defaults.WEEKDAY_THEME_TITLES` (the Ancient Gods
# menu, the Weekday theme picker, Settings) is a DIFFERENT surface the
# owner never asked to rename, so the shared table itself stays
# untouched (Rule #5: one shared name would have widened the blast
# radius past what was asked). Demonyms per the owner's own pick:
# "Egypt" (not "Egyptian"), "Norse" stays Norse (not "Nordic").
_GOD_TOPIC_GALLERY_TITLES = {
    "greek": "Greek", "norse": "Norse", "egypt": "Egypt", "slavic": "Slavic",
}
