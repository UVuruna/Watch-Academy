"""THE AVAILABILITY FIELD — which WEEK themes ship unlocked, base pack.

Owner-sealed ballot verdict 2026-08-12. Content is either BASE (unlocked
the moment the app installs) or LOCKED (L1 lock — visible in the picker
and the Encyclopedia, but not enterable until the owner's future
download/unlock flow admits it). On desktop, the existing
`identity.HIDDEN_MODE_SECRET` typed-sequence unlock
(`app.controller.Controller._collect_secret`) is the FUTURE trigger that
flips every LOCKED theme open at once for that session — this module
does not touch that mechanism, it only names the set it will one day
unlock.

**Scope, exactly as sealed.** Availability governs WEEK THEMES only.
The instrument itself, every ring preset and the whole astronomical
Encyclopedia are always-base by the EARLIER sealed verdict
(`ANDROID.md` -> Base Pack Agreement) and are never gated here — a
theme's own articles/blurbs travel WITH the theme's lock, they are not
a second thing to gate.

THE CONFIG SECTION LAW: one section, defined once, whole, below. Every
`WEEK` key is classified exactly once; nothing here is patched after
its own definition.

Layer: config — pure DATA. Imports only `config.registry.week`, so this
module stays a leaf exactly like `week.py` itself.
"""

from config.registry.week import WEEK

# ═══════════════════════════ THE AVAILABILITY TABLE ═══════════════════════════
# Every WEEK key, classified BASE or LOCKED. The owner's exact ballot list
# (2026-08-12) is BASE; every other WEEK key is LOCKED by construction —
# nothing here is a second list to keep in sync with the first.
BASE_THEME_KEYS = frozenset({
    "planets",
    "planet_signs",
    "planets_art",
    "cosmos",
    "continents",
    "profession",
    "corporate",
    "virtues",
    "sins",
    "moods",
})

AVAILABILITY = {
    key: ("base" if key in BASE_THEME_KEYS else "locked")
    for key in WEEK
}

LOCKED_THEME_KEYS = frozenset(key for key, tier in AVAILABILITY.items() if tier == "locked")
