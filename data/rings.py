"""Ring preset cards — bundled JSON plus the user's custom rings.

One card = one dial styling: the COMPOSITIONAL model (owner decree
2026-08-05) — an OUTER band (config.constants.RING_OUTERS) whose empty
hour fields carry the preset's own LETTERS, an INNER band (the user's
own changeable pick, config.constants.RING_INNERS) and an optional
CROWN TEXT (motto) arc. `{name, outer, letters}` is the whole card;
`outer` resolves the empty positions directly (no signature guessing).
Validation is loud (Rule #1): a broken card must name itself, never
render blank.
"""

from config import constants, paths
from core.motto import (
    _occurrence_index,
    centered_word_angles,
    free_arc_angles,
    motto_glyph_angles,
)
from data._io import load_json_checked


def _validate_motto(name: str, raw: list, positions: tuple) -> tuple:
    """The optional `motto` card field (TASK 1, owner "može radi"
    2026-07-19, CANON.md §The Banknote): a list of motto entries, each
    `{text, pins}` — `pins` is `[letter, occurrence, position]` triples
    (JSON has no tuples). Every pin's position must be one of the
    preset's own ring positions (the motto's key letters land on the
    SAME hexagram seats the ring's own letters occupy) and every
    character of `text` must be a space or a letter the shared library
    (`constants.RING_LETTER_FILES`) can draw — the motto reuses that
    exact PNG library, never new art. Each entry may also carry
    `clockwise` (MOTO-FIX round, owner correction 2026-07-19; default
    true): true reads the arc sweeping increasing angle (the TOP arc,
    ANNUIT COEPTIS's own), false sweeps decreasing angle (the BOTTOM
    arc, NOVUS ORDO SECLORUM's own) — see `core.motto.motto_glyph_angles`
    for why the bottom arc must reverse direction to still read
    left-to-right to a viewer. The per-glyph angle math itself
    (`core.motto.motto_glyph_angles`) runs HERE, at load time, so a
    broken pin config (a typo'd occurrence, an out-of-order pin) fails
    loudly at startup, never mid-paint. Returns a tuple of
    `{"text": str, "angles": tuple[float, ...]}`, empty for every
    preset without a `motto` field (The One, Templar, every custom
    ring; DOMY and PILOT carry the CENTERED cross-word form, the
    Dollar the pinned Great Seal form)."""
    def _words(text: str, pins: tuple, center: int | None) -> tuple:
        """Per-WORD spans + the seat each word answers for (WORD-HOVER
        round, owner 2026-07-27: "HOVER tekst osim na slova treba i na
        reči"): a centered entry is one word on its own seat; a pinned
        entry maps each word to the seat of the ONE pin falling inside
        it — the Dollar's five words carry exactly one pin each
        (ANNUIT→A/8h, COEPTIS→S/16h, NOVUS→N/4h, ORDO→Ω/24h,
        SECLORUM→M/20h — the five words spell the five letters). A word
        with zero or several pins gets no seat and stays silent."""
        words = []
        i = 0
        for word in text.split(" "):
            start, end = i, i + len(word) - 1
            if center is not None:
                seat = center
            else:
                inside = [
                    position for index, position in pins
                    if start <= index <= end
                ]
                seat = inside[0] if len(inside) == 1 else None
            words.append(
                {"text": word, "start": start, "end": end, "seat": seat}
            )
            i = end + 2
        return tuple(words)

    resolved = []
    for motto_entry in raw:
        text = str(motto_entry.get("text", ""))
        if not text:
            raise ValueError(f"ring preset {name!r}: a motto entry needs text")
        unknown = {
            char for char in text
            if char != " " and char not in constants.RING_LETTER_FILES
        }
        if unknown:
            raise ValueError(
                f"ring preset {name!r}: motto {text!r} uses unknown letters "
                f"{sorted(unknown)}"
            )
        clockwise = bool(motto_entry.get("clockwise", True))
        # THE CROWN TEXT form (custom rings, owner decree 2026-08-05):
        # `{"text", "orientation"}` — free-form, user-typed text arcing
        # from the top or from the bottom, NOT pinned to any ring seat.
        # Mutually exclusive with `center`/`pins` (the bundled presets'
        # own Great Seal / cross-word forms).
        orientation = motto_entry.get("orientation")
        if orientation is not None:
            if motto_entry.get("pins") or motto_entry.get("center") is not None:
                raise ValueError(
                    f"ring preset {name!r}: motto {text!r} cannot carry "
                    f"`orientation` together with `center`/`pins`"
                )
            try:
                angles = free_arc_angles(text, str(orientation))
            except ValueError as error:
                raise ValueError(
                    f"ring preset {name!r}: motto {text!r}: {error}"
                ) from error
            resolved.append({
                "text": text, "angles": angles,
                "words": _words(text, (), None),
            })
            continue
        # The CROSS-WORDS form (owner UV inbox 2026-07-27): a single
        # station word CENTERED on one of the preset's own seats —
        # `{"text", "center", "clockwise"}`, the DOMY/PILOT cross
        # stations. Mutually exclusive with the pinned Great Seal form.
        center = motto_entry.get("center")
        if center is not None:
            if motto_entry.get("pins"):
                raise ValueError(
                    f"ring preset {name!r}: motto {text!r} cannot carry "
                    f"both `center` and `pins`"
                )
            center = int(center)
            if center not in positions:
                raise ValueError(
                    f"ring preset {name!r}: motto center {center} is not "
                    f"one of its own positions {positions}"
                )
            try:
                angles = centered_word_angles(text, center, clockwise=clockwise)
            except ValueError as error:
                raise ValueError(
                    f"ring preset {name!r}: motto {text!r}: {error}"
                ) from error
            resolved.append({
                "text": text, "angles": angles,
                "words": _words(text, (), center),
            })
            continue
        pins = []
        for letter, occurrence, position in motto_entry.get("pins", ()):
            if position not in positions:
                raise ValueError(
                    f"ring preset {name!r}: motto pin position {position} "
                    f"is not one of its own positions {positions}"
                )
            pins.append((str(letter), int(occurrence), int(position)))
        try:
            angles = motto_glyph_angles(text, tuple(pins), clockwise=clockwise)
        except ValueError as error:
            raise ValueError(
                f"ring preset {name!r}: motto {text!r}: {error}"
            ) from error
        pin_indices = tuple(
            (_occurrence_index(text, letter, occurrence), position)
            for letter, occurrence, position in pins
        )
        resolved.append({
            "text": text, "angles": angles,
            "words": _words(text, pin_indices, None),
        })
    return tuple(resolved)


def validate_preset(entry: dict) -> dict:
    """One card checked: known outer, library letters, matching counts.
    Returns {name, outer, positions, letters, triangle, legend, motto,
    thematic}. `outer` (owner decree 2026-08-05, the compositional ring
    model) resolves the empty hour fields directly from
    `constants.RING_OUTERS` — no more guessing a "layout" from a
    positions signature. The FIVE bundled presets are each LOCKED to
    exactly one outer (`constants.RING_OUTER_LOCK`); any other name
    (every custom ring) may pick any outer freely. `triangle` (ROADMAP
    15b) is an optional 3-position override of the `"hexa"` outer's own
    metal triangle (which is empty — one finish on all six, the plain
    Union reading) so a 6-letter preset can split into two 3-letter
    metal groups instead (the Dollar banknote's Trinity/Union read,
    CANON.md §The Banknote). `legend` is an optional hour(position) ->
    {name, reading} map — the per-letter HOVER LEGEND text, quoted
    verbatim from CANON. `motto` (TASK 1, widened 2026-08-05 with the
    free-form CROWN TEXT) is an optional list of motto/crown-text
    entries — see `_validate_motto`."""
    name = str(entry.get("name", "")).strip()
    if not name:
        raise ValueError(f"ring preset without a name: {entry!r}")
    outer = str(entry.get("outer", ""))
    if outer not in constants.RING_OUTERS:
        raise ValueError(
            f"ring preset {name!r}: unknown outer {outer!r} "
            f"(known: {sorted(constants.RING_OUTERS)})"
        )
    locked = constants.RING_OUTER_LOCK.get(name)
    if locked is not None and outer != locked:
        raise ValueError(
            f"ring preset {name!r} is locked to outer {locked!r}, got {outer!r}"
        )
    positions = constants.RING_OUTERS[outer]["positions"]
    letters = tuple(str(letter) for letter in entry.get("letters", ()))
    if len(letters) != len(positions):
        raise ValueError(
            f"ring preset {name!r}: {len(letters)} letters for "
            f"{len(positions)} positions (outer {outer!r})"
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
        if outer != "hexa":
            raise ValueError(
                f"ring preset {name!r}: a triangle override only applies "
                f"to the 'hexa' outer (this preset's outer is {outer!r})"
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
    motto = _validate_motto(name, entry.get("motto") or [], positions)
    # The optional THEMATIC color pick (ENLARGE/THEMATIC round, widened
    # for CUSTOM rings, owner 2026-07-27): a card may name ANY of the
    # transformer's ramps (the five ring theme colors plus every metal
    # ramp — copper, iron, …) as its own Thematic-finish color;
    # absent, `app.controller.apply_display_settings` falls back to
    # `constants.RING_THEMATIC_SHADES` (bundled) or the moon indigo.
    thematic_raw = entry.get("thematic")
    thematic = None
    if thematic_raw is not None:
        thematic = str(thematic_raw)
        if thematic not in constants.METAL_SHADE_NAMES["thematic"]:
            raise ValueError(
                f"ring preset {name!r}: unknown thematic color "
                f"{thematic!r} (known: "
                f"{sorted(constants.METAL_SHADE_NAMES['thematic'])})"
            )
    return {
        "name": name,
        "positions": positions,
        "letters": letters,
        "outer": outer,
        "triangle": triangle,
        "legend": legend,
        "motto": motto,
        "thematic": thematic,
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
