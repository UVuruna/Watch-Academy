"""Ring-name resolution + custom-ring-card normalization for
`app.settings_store` — split out (THE STRUCTURE LAW) so the settings
file's general load/save plumbing does not also have to hold the ring
preset renames, the legacy-card migration and the per-ring-name dict
loader in the same file.
"""

from config import constants
from data.rings import validate_preset

# RING PRESET RENAMES (TASK 2, MASON/ICONS round, owner verdicts
# 2026-07-19, third batch; DOLLAR/EYE round, owner decree 2026-07-27):
# a stored settings file's OLD bundled preset name migrates onto its
# new one (external user data, not an API shim, Rule #6) — a bare
# case-insensitive fold alone cannot bridge these (unlike "MORPH" ->
# "Morph", a pure case change the existing fold already handles for
# free). The first-generation names chain straight to the CURRENT
# ones: "MASON G" -> "Mason" -> "Dollar", "NUMBERS" -> "Omega" ->
# "The One".
LEGACY_RING_NAMES = {
    "mason g": "Dollar",
    "mason": "Dollar",
    "numbers": "The One",
    "omega": "The One",
    # CROSS-WORDS round (owner UV inbox + PILOT pick 2026-07-27): the
    # chalice card "MORPH"/"Morph" became "PILOT" (Π-I-L-Ω-Θ), then
    # LOOP ROUND (owner ruling 2026-08-06): "PILOT" -> "LOOP" — L-Ω-Ω-Π
    # read around the wheel spells LOOP, the infinity reading (Omega
    # bent from ending into the circle without end) replacing the
    # retired "pilot/guide" one. Both first-generation names chain
    # straight to the CURRENT one.
    "morph": "LOOP",
    "pilot": "LOOP",
}


def fold_ring_name(raw_name: str, by_fold: dict) -> str | None:
    """One stored ring name resolved to its CURRENT bundled/custom name
    — the TASK 2 rename migration first, then the existing case-
    insensitive fold (older files stored "domy") — or None when it
    names nothing loaded (a stale bundled rename, or a custom ring the
    user later deleted). Shared by the top-level `ring` field (which
    must raise on a miss) and every per-ring-name dict's keys (which
    silently drop a miss, `theme_metals`'s own lenient policy)."""
    renamed = LEGACY_RING_NAMES.get(raw_name.lower(), raw_name)
    return by_fold.get(renamed.lower())


def load_named_dict(raw: dict, key: str, by_fold: dict, valid) -> dict:
    """One stored per-ring-name dict (`ring_eye_shine`, `ring_inner`,
    the crown-text fields), loaded with the shared lenient policy: a
    value failing `valid(value)` or a name resolving to nothing loaded
    is silently dropped rather than corrupting the whole file over one
    stale entry (Rule #5, one loader for all)."""
    result = {}
    for raw_name, value in dict(raw.get(key, {})).items():
        if not valid(value):
            continue
        resolved = fold_ring_name(str(raw_name), by_fold)
        if resolved is not None:
            result[resolved] = value if isinstance(value, bool) else str(value)
    return result


# Only bot_cross/top_cross/hexa existed before THE COMPOSITIONAL RING
# MODEL (owner decree 2026-08-05) — a legacy custom-ring card's
# positions signature resolves to exactly one of these three.
_LEGACY_OUTER_BY_POSITIONS = {
    frozenset(outer["positions"]): name
    for name, outer in constants.RING_OUTERS.items()
    if name in ("bot_cross", "top_cross", "hexa")
}


def migrate_legacy_ring_card(entry: dict) -> dict:
    """SETTINGS MIGRATION (owner decree 2026-08-05): a custom ring
    saved before the compositional ring model stored `{name, positions,
    letters}` (JEWELS naming sweep, owner ruling 2026-08-06: the field
    is now `jewels`, read as a fallback in `data.rings.validate_preset`)
    — no `outer` yet. Migrated in place by matching the positions
    signature; an unmatched entry is left untouched and fails loudly in
    `validate_preset`.

    Also migrates a card's `motto` field onto `crown_text` (TASK 1,
    owner ruling 2026-08-06, "one term for one thing" — `motto` is
    retired everywhere including a stored custom-ring card): a card
    saved before the rename carries its crown-arc entries under the
    old key, and `data.rings.validate_preset` now only reads
    `crown_text` — without this step the text would silently vanish on
    load rather than fail loudly, since the field is optional."""
    if "outer" in entry or "positions" not in entry:
        migrated_positions = entry
    else:
        positions = frozenset(int(p) for p in entry["positions"])
        outer = _LEGACY_OUTER_BY_POSITIONS.get(positions)
        if outer is None:
            migrated_positions = entry
        else:
            migrated_positions = dict(entry)
            migrated_positions["outer"] = outer
    if "motto" not in migrated_positions or "crown_text" in migrated_positions:
        return migrated_positions
    migrated = dict(migrated_positions)
    migrated["crown_text"] = migrated.pop("motto")
    return migrated


def normalized_ring_card(entry: dict) -> dict:
    """One custom ring card, validated by the shared card validator and
    stored in its JSON-serializable shape. `outer` (owner decree
    2026-08-05) replaces the old `positions` field; `jewels` (JEWELS
    naming sweep, owner ruling 2026-08-06) replaces the old `letters`
    field. `migrate_legacy_ring_card` upgrades a pre-existing stored
    card; `data.rings.validate_preset` reads a stored `letters` key as
    the fallback when `jewels` is absent."""
    card = validate_preset(migrate_legacy_ring_card(entry))
    normalized = {
        "name": card["name"],
        "outer": card["outer"],
        "jewels": list(card["jewels"]),
    }
    if card["thematic"] is not None:
        normalized["thematic"] = card["thematic"]
    return normalized
