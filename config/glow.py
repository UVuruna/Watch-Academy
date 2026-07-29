"""Event glow windows and the eclipse rendering knobs — the
season/moon turning-point glow (ring-band relocation, halo
alpha/radius) and the whole ECLIPSE_* family (state machine,
art, type icons/emblems).

Layer: config — pure, no Qt, no wall clock.
"""

from config import paths


# --- Season/moon event glow rendering (windows live in constants) ---------------
# Turning-point glow REWORK (owner 2026-07-16): at a GLOW event the
# glowing marker relocates RADIALLY to the ring band centerline — the
# radius where the hour numerals and ring letters sit — keeping its event
# ANGLE (New Moon still at the 12h reading). The compact halo then
# STRADDLES the ring, shining both inside and outside the circle, so it
# reads over any background (a white Compass tip, the bright yellow top
# arms) without needing to be huge. New colors: the Sun's events (the
# Earth marker at a solstice/equinox) glow GOLDEN, the Moon's phases glow
# SILVER — starting values the owner tunes here.

GLOW_CORE_ALPHA = 1.0

GLOW_MID_ALPHA = 0.85
GLOW_MID_STOP = 0.75                 # gradient position of the mid alpha
GLOW_RADIUS_SCALE = 1.5              # halo radius, multiple of the marker radius


ECLIPSE_INVISIBLE_STRENGTH_FACTOR = 0.5
# ECLIPSE_SOLAR_ART lives in defaults.py, not here: its value is
# `pantheon.weekday_art(...)`, and a new module may never import another
# new module (WORKPLAN-STRUCTURE.md's fixed DAG) -- the remnant is the
# one place that may import pantheon.py downhill, so the single
# cross-referencing name moved there instead of dragging weekday_art
# itself (and the whole pantheon namespace it needs) into glow.py.
ECLIPSE_LUNAR_FRINGE_STOP = 0.92              # gradient position (0..1 of halo radius)
ECLIPSE_LUNAR_FRINGE_HALF_WIDTH = 0.05        # ring thickness either side of the stop
ECLIPSE_LUNAR_FRINGE_ALPHA = 0.85             # peak alpha before the magnitude scale
# Glow STRENGTH scales with the catalog MAGNITUDE (owner idea, ROADMAP
# 15h item 11): magnitude 0 (grazing partial) maps to the MIN fraction
# of the normal glow alpha, magnitude at/above MAX (a comfortable
# totality margin) maps to the full alpha — linear between, clamped
# outside (Rule #4: config-driven, no magic numbers at the call site).
# Fix round C (owner decree 2026-07-19) narrows this mapping to ONE
# remaining caller — the SOLAR PARTIAL state — every other state's glow
# strength is now a fixed TYPE constant below.
ECLIPSE_MAGNITUDE_MIN = 0.0
ECLIPSE_MAGNITUDE_MAX = 1.2
ECLIPSE_GLOW_STRENGTH_MIN = 0.4
ECLIPSE_GLOW_STRENGTH_MAX = 1.0

# THE ECLIPSE STATE TABLE (owner decree 2026-07-19, fix round C — the
# lunar "translucent bronze wash" complaint: the old darkening scaled a
# translucent overlay's ALPHA by magnitude, so a bright moon under a
# weak wash still read as "a visible moon shining bronze". The fix: the
# catalog TYPE (ground-truthed from Database/deep_time.sqlite's actual
# rows — solar {partial, annular, total, hybrid}, lunar {partial,
# penumbral, total}) selects ONE fixed render STATE. The state alone
# sets the disc BRIGHTNESS (never translucency, never magnitude); it
# also sets the glow STRENGTH for every state except "solar_partial",
# which keeps the original magnitude-linear mapping
# (`render.layers.eclipse_glow_strength`) — the owner's one named
# exception ("SOLAR partial: art + glow scaled by magnitude").
#
# `hybrid` (annular-total transitional, ~3.2k of ~70k solar rows) has no
# dedicated owner state — it is mapped to "solar_total" (not the
# unknown-type fallback): a hybrid eclipse shows true totality along
# most of its ground track, the closer of the two sealed states.
ECLIPSE_TYPE_STATE = {
    ("lunar", "total"): "lunar_total",
    ("lunar", "partial"): "lunar_partial",
    ("lunar", "penumbral"): "lunar_penumbral",
    ("solar", "total"): "solar_total",
    ("solar", "hybrid"): "solar_total",       # nearest sealed state, see above
    ("solar", "annular"): "solar_annular",
    ("solar", "partial"): "solar_partial",
}
# Unknown/missing catalog type (should not occur — the generator only
# ever writes the vocabulary above) documented fallback: the kind's
# PARTIAL state — a plausible middle ground, never a crash (Rule #1).
ECLIPSE_STATE_FALLBACK = {"solar": "solar_partial", "lunar": "lunar_partial"}

# Moon-disc BRIGHTNESS as a fraction of full value (0..1) — a true
# multiply-darken of the rendered disc, not an alpha wash (owner: "DARKEN
# means BRIGHTNESS DOWN... unmistakably an eclipse"). Solar states are
# absent — the solar disc art (the eclipsed-Sun dual) never darkens,
# only its glow color/strength change.
ECLIPSE_STATE_MOON_BRIGHTNESS = {
    "lunar_total": 0.07,       # near-black disc
    "lunar_partial": 0.18,
    "lunar_penumbral": 0.60,   # real penumbral eclipses are barely visible
}
# Fixed glow-strength fraction per state (0..1, same scale as
# `eclipse_glow_strength`'s return). "solar_partial" is intentionally
# absent — it keeps the magnitude-linear mapping instead.
ECLIPSE_STATE_GLOW_STRENGTH = {
    "lunar_total": 1.0,
    "lunar_partial": 0.6,
    "lunar_penumbral": 0.25,
    "solar_total": 1.0,
    "solar_annular": 1.0,
}
# The turquoise ozone fringe (Option C) reads only where totality/near-
# totality actually darkens the sky rim — real penumbral eclipses show
# no such band, so the fringe is withheld there (owner spec, this round).
ECLIPSE_STATE_FRINGE = {
    "lunar_total": True,
    "lunar_partial": True,
    "lunar_penumbral": False,
}

# The ECLIPSES ENCYCLOPEDIA category emblems (fix round F, owner order
# 2026-07-19): one rose-window night-window medallion per category we
# distinguish, at assets/eclipse/<Stem>.png — graceful-absent until
# PromptPainter generates them (research/prompts/eclipse/eclipse_prompts.md).
# The SAME emblem backs the chapter page (app.encyclopedia) AND the
# eclipse-window hover badge on the Earth/Moon card (render.compositor).
ECLIPSE_ART_DIR = paths.assets_dir() / "celestial" / "eclipse"
# (kind, type) -> category emblem stem. `hybrid` keeps its OWN chapter
# and emblem here even though the RENDER state table folds it into
# solar_total — the reader still gets the distinct hybrid page; an
# unknown/missing type resolves to None (no badge, graceful — the
# render state table already documents its own fallback).
ECLIPSE_TYPE_EMBLEM = {
    ("solar", "total"): "Solar_Total",
    ("solar", "annular"): "Solar_Annular",
    ("solar", "partial"): "Solar_Partial",
    ("solar", "hybrid"): "Solar_Hybrid",
    ("lunar", "total"): "Lunar_Total",
    ("lunar", "partial"): "Lunar_Partial",
    ("lunar", "penumbral"): "Lunar_Penumbral",
}

# THE PER-TYPE ECLIPSE ICONS (ART-INFRA round, owner 2026-07-20/21):
# ECLIPSE_LUNAR_TYPE_ICON, eclipse_lunar_type_icon() and
# ECLIPSE_SOLAR_TYPE_ICON_SOURCE live in defaults.py, not here -- they
# key off ICON_DIR (the shared UI icon chrome root, itself used by many
# non-eclipse icon categories), and a new module may never import
# another new module (the fixed DAG); the remnant is the one place that
# may import glow.py's siblings downhill while also owning ICON_DIR.
ECLIPSE_TYPE_ICON_PX = 22   # the hover-line's small inline badge
