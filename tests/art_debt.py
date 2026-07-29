"""THE ART DEBT REGISTRY — the one list of plates a registered theme
declares and the owner has not generated yet.

Why this exists (completion wave III, Session 33, 2026-07-29). The three
Star Wars casts were registered with 25 of the 60 cast plates their sheet
briefs, on `WORKPLAN.md` §THE THEME BACKLOG's explicit instruction:
*"every missing plate is graceful-absent by contract... it is NOT a
reason to skip the cast"*. Four independent guards across three test
files assert, each for its own seat kind, that a registered theme's art
is on disk — and every one of them had grown its own hand-written
exception (`religion_alt/jupiter` for Eleusis, `religion` for the
Satanism dual, `continents` for Zealandia). Four parallel debt lists is
exactly the duplication Rule #5 forbids, and the fourth copy is where one
of them silently goes stale.

So the debt lives HERE, once, and the guards read it.

**Subset semantics, on purpose.** Every guard asserts
`missing <= PENDING_*`, never equality. Art ARRIVING must never turn the
suite red — the owner drops a plate in and the seat simply lights up. A
NEW gap, on the other hand, fails immediately: a stem typo, a folder
rename, or a future cast wired against art nobody queued is not in this
registry and never will be by accident.

The prose authority for all of it is `research/theme_staging.md`
§Art Owed, which the THEME COMPLETION LAW (project `CLAUDE.md`) requires
a wave to write in the same commit that ships the wiring. This module is
that ledger's assertion.
"""

# --- The weekday BODY seats -------------------------------------------------
# (theme, body) whose plate is not on disk in the theme's own look dir.
#
# BRONZE is the master the three metal looks are struck from; COLORED is
# the separately painted sibling. A seat can be missing one and have the
# other — Jabba and Palpatine shipped their colored poster with no bronze
# master, and Chewbacca the reverse — so the two are tracked apart rather
# than collapsed into "the seat has no art".
PENDING_BODY_BRONZE = frozenset({
    # The Ancient set's Eleusis plate, pending owner art since the
    # 2026-07-15 rework — the registry's oldest entry.
    ("religion_alt", "jupiter"),
    # Completion wave III (Session 33): the Star Wars casts.
    ("sw_jedi", "sun"),
    ("sw_sith", "mercury"), ("sw_sith", "saturn"), ("sw_sith", "sun"),
    ("sw_dyad", "mars"), ("sw_dyad", "mercury"), ("sw_dyad", "jupiter"),
    ("sw_dyad", "venus"), ("sw_dyad", "saturn"), ("sw_dyad", "sun"),
})
PENDING_BODY_COLORED = frozenset({
    ("sw_jedi", "saturn"), ("sw_jedi", "sun"),
    ("sw_sith", "saturn"),
    ("sw_dyad", "mars"), ("sw_dyad", "mercury"), ("sw_dyad", "jupiter"),
    ("sw_dyad", "venus"), ("sw_dyad", "saturn"), ("sw_dyad", "sun"),
})

# --- The Sunday SERVANT plate (`pantheon.WEEKDAY_DUAL_FILES`) ---------------
# Themes running dual-less until their Mirror lands. `religion`'s Satanism
# plate has been pending owner art since 2026-07-15; all three Star Wars
# Mirrors (Vader, Anakin, Kylo Ren) are wave III's own debt.
PENDING_DUAL = frozenset({"religion", "sw_jedi", "sw_sith", "sw_dyad"})

# --- The NINTH plate (`constants.WEEKDAY_THEME_NINTHS`) ---------------------
# Themes whose Ninth is wired ahead of its art. `continents` (Zealandia)
# has been so since the owner-sealed matrix of 2026-07-21; sw_jedi (Yoda)
# and sw_dyad (The Ghosts) are wave III's. sw_sith is NOT here — Darth
# Plagueis landed with the sheet.
PENDING_NINTH = frozenset({"continents", "sw_jedi", "sw_dyad"})

# --- SEAT ROSTERS (`pantheon.WEEKDAY_SEAT_ROSTERS`) -------------------------
# Casts whose rotating seats are wired ahead of their plates, so their
# rotation cannot be exercised yet. `_roster_candidates` already skips a
# member that is not on disk, so such a seat shows nothing until art
# arrives rather than failing.
PENDING_ROSTERS = frozenset({"sw_dyad"})
