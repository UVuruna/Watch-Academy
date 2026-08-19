"""THE NINTH - the seat outside the circle.

Eight bodies ride the dial; the NINTH stands outside them (CANON.md,
"The Ninth - Outside the Circle"; the owner's 8+1 doctrine of
2026-07-14). This module holds everything that seat needs and nothing
else: which theme mounts which Ninth face, the two ALT tables (the
Pangea easter egg, the Dyad's night face), THE DOUBLE NINTH LAW's
mechanism dispatch with the vocabulary a mechanism may be named from,
and THE DUAL/NINTH TIME WINDOW - the half hour either side of solar
noon and solar midnight in which the Ninth shows.

The window sits here rather than in `config/dial.py` because it is
not geometry: it is the rule that decides WHICH FACE the centre seat
wears, and it is read by the same `render.ninths` code as the tables
above it.

Born 2026-08-19, when the owner ruled that `config/constants.py`'s
**38 top-level sections** were a junk drawer, not a directory, and gave
the split its module names himself. Nothing here is new data - every
table below stood in `constants.py` under its own section banner and
moved WHOLE, with its comments; the callers were repointed, and no
re-export shim was left behind (`rules/CODE.md` - No backward
compatibility). The whole map, one row per module, is in
[the folder doc](___config.md).

Layer: config - pure Python, no Qt, no wall clock. It reads
`config.registry` for the per-theme Ninth tables THE REGISTRY
computes from each theme's own entry, and imports no other sibling.
"""

from config import registry

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
