"""Ring preset cards — bundled JSON plus the user's custom rings.

One card = one dial styling (owner spec): {name, positions, letters}.
The positions signature resolves the LAYOUT (config RING_LAYOUTS) —
the ring face with matching gaps and the metal rules. Validation is
loud (Rule #1): a broken card must name itself, never render blank.
"""

from config import constants, paths
from data._io import load_json_checked

_SIGNATURES = {
    frozenset(layout["positions"]): name
    for name, layout in constants.RING_LAYOUTS.items()
}


def validate_preset(entry: dict) -> dict:
    """One card checked: known positions signature, library letters,
    matching counts. Returns {name, positions, letters, layout, triangle,
    legend}. `triangle` (ROADMAP 15b) is an optional 3-position override
    of the SEAL layout's own metal triangle (which is empty — one finish
    on all six, the NUMBERS way) so a 6-letter preset can split into two
    3-letter metal groups instead (the MASON G banknote's Trinity/Union
    read, CANON.md §The Banknote). `legend` is an optional hour(position)
    -> {name, reading} map — the per-letter HOVER LEGEND text, quoted
    verbatim from CANON."""
    name = str(entry.get("name", "")).strip()
    if not name:
        raise ValueError(f"ring preset without a name: {entry!r}")
    positions = tuple(int(p) for p in entry.get("positions", ()))
    layout = _SIGNATURES.get(frozenset(positions))
    if layout is None:
        raise ValueError(
            f"ring preset {name!r}: positions {positions} match no layout "
            f"(known: {[l['positions'] for l in constants.RING_LAYOUTS.values()]})"
        )
    letters = tuple(str(letter) for letter in entry.get("letters", ()))
    if len(letters) != len(positions):
        raise ValueError(
            f"ring preset {name!r}: {len(letters)} letters for "
            f"{len(positions)} positions"
        )
    unknown = [l for l in letters if l not in constants.RING_LETTER_FILES]
    if unknown:
        raise ValueError(f"ring preset {name!r}: unknown letters {unknown}")
    # A NUMBER may only stand on its own hour (owner rule 2026-07-12:
    # a 4 at 12h makes no sense — that is why only the six ring-hour
    # numbers exist at all).
    for position, glyph in zip(positions, letters):
        if glyph.isdigit() and int(glyph) != position:
            raise ValueError(
                f"ring preset {name!r}: number {glyph} cannot stand at "
                f"{position}h — numbers only fit their own position"
            )
    triangle_raw = entry.get("triangle")
    triangle = None
    if triangle_raw is not None:
        if layout != "seal":
            raise ValueError(
                f"ring preset {name!r}: a triangle override only applies "
                f"to the seal layout (this preset resolved to {layout!r})"
            )
        triangle = tuple(int(p) for p in triangle_raw)
        if len(triangle) != 3 or not set(triangle).issubset(positions):
            raise ValueError(
                f"ring preset {name!r}: triangle {triangle} must be "
                f"exactly 3 of its own positions {positions}"
            )
    legend_raw = entry.get("legend") or {}
    legend = {}
    for key, value in legend_raw.items():
        position = int(key)
        if position not in positions:
            raise ValueError(
                f"ring preset {name!r}: legend position {position} is "
                f"not one of its own positions {positions}"
            )
        letter_name = str(value.get("name", "")).strip()
        reading = str(value.get("reading", "")).strip()
        if not letter_name or not reading:
            raise ValueError(
                f"ring preset {name!r}: legend entry {position} needs "
                "both a name and a reading"
            )
        legend[position] = {"name": letter_name, "reading": reading}
    return {
        "name": name,
        "positions": positions,
        "letters": letters,
        "layout": layout,
        "triangle": triangle,
        "legend": legend,
    }


def ring_presets(custom: tuple = ()) -> dict:
    """name -> validated card for every bundled + custom preset."""
    raw = load_json_checked(
        paths.database_dir() / "ring_presets.json", "Ring presets database"
    )
    presets: dict = {}
    for entry in list(raw["presets"]) + list(custom):
        card = validate_preset(entry)
        if card["name"] in presets:
            raise ValueError(f"ring preset name {card['name']!r} is duplicated")
        presets[card["name"]] = card
    return presets
