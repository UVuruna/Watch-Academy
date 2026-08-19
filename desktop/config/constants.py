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

# ═══════════════════════════ WEEKDAY THEMES ═══════════════════════════
# Weekday body themes (SYMBOLISM.md canon): "planets" uses the skin's
# own weekday unit; the others swap in the owner's themed art from
# assets/skins/domy/weekday/<theme>/ with the canon display names.
WEEKDAY_THEMES = registry.THEMES

# ═══════════════════════════ THEME BLURBS & ARTICLES ═══════════════════════════
# Theme -> symbolism.json blurb key (the encyclopedic text under the
# hexa diamond hover follows the active theme).
WEEKDAY_THEME_BLURBS = registry.BLURBS

# Theme -> symbolism.json article set (the glyph theme shares the
# planet articles — same entities, different art).
WEEKDAY_THEME_ARTICLES = registry.ARTICLES
