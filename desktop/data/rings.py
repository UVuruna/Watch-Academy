"""Ring preset cards — bundled JSON plus the user's custom rings.

One card = one dial styling: the COMPOSITIONAL model (owner decree
2026-08-05) — an OUTER band (config.constants.RING_OUTERS) whose empty
hour fields carry the preset's own JEWELS, an INNER band (the user's
own changeable pick, config.constants.RING_INNERS) and an optional
CROWN TEXT arc. `{name, outer, jewels}` is the whole card (JEWELS
naming sweep, owner ruling 2026-08-06: the field was `letters`, a
stored card under that key still loads via `validate_preset`'s
fallback); `outer` resolves the empty positions directly (no signature
guessing).
Validation is loud (Rule #1): a broken card must name itself, never
render blank.
"""

from config import constants, paths
from core.crown_text import (
    _occurrence_index,
    centered_word_angles,
    free_arc_angles,
    crown_glyph_angles,
)
from data._io import load_json_checked


def _validate_crown_text(name: str, raw: list, positions: tuple) -> tuple:
    """The optional `crown_text` card field (TASK 1, owner "može radi"
    2026-07-19, CANON.md §The Banknote): a list of crown text entries, each
    `{text, pins}` — `pins` is `[letter, occurrence, position]` triples
    (JSON has no tuples). Every pin's position must be one of the
    preset's own ring positions (the crown text's key letters land on the
    SAME hexagram seats the ring's own jewels occupy) and every
    character of `text` must be a space or a letter the shared library
    (`constants.LETTER_PLATE_FILES`) can draw — the crown text reuses that
    exact PNG library, never new art. Each entry may also carry
    `clockwise` (MOTO-FIX round, owner correction 2026-07-19; default
    true): true reads the arc sweeping increasing angle (the TOP arc,
    ANNUIT COEPTIS's own), false sweeps decreasing angle (the BOTTOM
    arc, NOVUS ORDO SECLORUM's own) — see `core.crown_text.crown_glyph_angles`
    for why the bottom arc must reverse direction to still read
    left-to-right to a viewer. The per-glyph angle math itself
    (`core.crown_text.crown_glyph_angles`) runs HERE, at load time, so a
    broken pin config (a typo'd occurrence, an out-of-order pin) fails
    loudly at startup, never mid-paint. Returns a tuple of
    `{"text": str, "angles": tuple[float, ...]}`, empty for every
    preset without a `crown_text` field (The One, Templar, every custom
    ring; DOMY and LOOP carry the CENTERED cross-word form, the
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
    for crown_entry in raw:
        text = str(crown_entry.get("text", ""))
        if not text:
            raise ValueError(f"ring preset {name!r}: a crown text entry needs text")
        unknown = {
            char for char in text
            if char != " " and char not in constants.LETTER_PLATE_FILES
        }
        if unknown:
            raise ValueError(
                f"ring preset {name!r}: crown text {text!r} uses unknown jewels "
                f"{sorted(unknown)}"
            )
        clockwise = bool(crown_entry.get("clockwise", True))
        # EVERY CROWN TEXT CARRIES ITS OWN HOVER (ring_rework §3, owner
        # ruling 2026-08-06): an optional `reading` {title, text} —
        # when present, `render.compositor._ring_word_legend_tooltip`
        # shows THIS for every word of this entry instead of the seat's
        # own letter legend (the exact reported bug: ANNUIT's hover
        # used to narrate the Anointed Aegis letter under it instead of
        # the Latin motto itself).
        reading_raw = crown_entry.get("reading")
        reading = None
        if reading_raw is not None:
            reading_title = str(reading_raw.get("title", "")).strip()
            reading_text = str(reading_raw.get("text", "")).strip()
            if not reading_title or not reading_text:
                raise ValueError(
                    f"ring preset {name!r}: crown text {text!r} reading "
                    "needs both a title and a text"
                )
            reading = {"title": reading_title, "text": reading_text}
        # THE CROWN TEXT form (custom rings, owner decree 2026-08-05):
        # `{"text", "orientation"}` — free-form, user-typed text arcing
        # from the top or from the bottom, NOT pinned to any ring seat.
        # Mutually exclusive with `center`/`pins` (the bundled presets'
        # own Great Seal / cross-word forms).
        orientation = crown_entry.get("orientation")
        if orientation is not None:
            if crown_entry.get("pins") or crown_entry.get("center") is not None:
                raise ValueError(
                    f"ring preset {name!r}: crown text {text!r} cannot carry "
                    f"`orientation` together with `center`/`pins`"
                )
            try:
                angles = free_arc_angles(text, str(orientation))
            except ValueError as error:
                raise ValueError(
                    f"ring preset {name!r}: crown text {text!r}: {error}"
                ) from error
            resolved.append({
                "text": text, "angles": angles,
                "words": _words(text, (), None),
                "reading": reading,
            })
            continue
        # The CROSS-WORDS form (owner UV inbox 2026-07-27): a single
        # station word CENTERED on one of the preset's own seats —
        # `{"text", "center", "clockwise"}`, the DOMY/LOOP cross
        # stations. Mutually exclusive with the pinned Great Seal form.
        center = crown_entry.get("center")
        if center is not None:
            if crown_entry.get("pins"):
                raise ValueError(
                    f"ring preset {name!r}: crown text {text!r} cannot carry "
                    f"both `center` and `pins`"
                )
            center = int(center)
            if center not in positions:
                raise ValueError(
                    f"ring preset {name!r}: crown text center {center} is not "
                    f"one of its own positions {positions}"
                )
            try:
                angles = centered_word_angles(text, center, clockwise=clockwise)
            except ValueError as error:
                raise ValueError(
                    f"ring preset {name!r}: crown text {text!r}: {error}"
                ) from error
            resolved.append({
                "text": text, "angles": angles,
                "words": _words(text, (), center),
                "reading": reading,
            })
            continue
        pins = []
        for letter, occurrence, position in crown_entry.get("pins", ()):
            if position not in positions:
                raise ValueError(
                    f"ring preset {name!r}: crown text pin position {position} "
                    f"is not one of its own positions {positions}"
                )
            pins.append((str(letter), int(occurrence), int(position)))
        try:
            angles = crown_glyph_angles(text, tuple(pins), clockwise=clockwise)
        except ValueError as error:
            raise ValueError(
                f"ring preset {name!r}: crown text {text!r}: {error}"
            ) from error
        pin_indices = tuple(
            (_occurrence_index(text, letter, occurrence), position)
            for letter, occurrence, position in pins
        )
        resolved.append({
            "text": text, "angles": angles,
            "words": _words(text, pin_indices, None),
            "reading": reading,
        })
    return tuple(resolved)


def validate_preset(entry: dict) -> dict:
    """One card checked: known outer, library jewels, matching counts.
    Returns {name, outer, positions, jewels, triangle, legend, crown_text,
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
    verbatim from CANON. `crown_text` (TASK 1, widened 2026-08-05 with the
    free-form CROWN TEXT) is an optional list of crown-text
    entries — see `_validate_crown_text`."""
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
    # JEWELS naming sweep (owner ruling 2026-08-06): the field is now
    # `jewels`; a card stored under the old `letters` key (bundled JSON
    # or a stored custom card) is read as the fallback.
    jewels_raw = entry.get("jewels", entry.get("letters", ()))
    jewels = tuple(str(jewel) for jewel in jewels_raw)
    if len(jewels) != len(positions):
        raise ValueError(
            f"ring preset {name!r}: {len(jewels)} jewels for "
            f"{len(positions)} positions (outer {outer!r})"
        )
    unknown = [j for j in jewels if j not in constants.LETTER_PLATE_FILES]
    if unknown:
        raise ValueError(f"ring preset {name!r}: unknown jewels {unknown}")
    # A NUMBER may only stand on its own hour (owner rule 2026-07-12:
    # a 4 at 12h makes no sense — that is why only the six ring-hour
    # numbers exist at all).
    for position, glyph in zip(positions, jewels):
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
        jewel_name = str(value.get("name", "")).strip()
        reading = str(value.get("reading", "")).strip()
        if not jewel_name or not reading:
            raise ValueError(
                f"ring preset {name!r}: legend entry {position} needs "
                "both a name and a reading"
            )
        legend[position] = {"name": jewel_name, "reading": reading}
    crown_text = _validate_crown_text(name, entry.get("crown_text") or [], positions)
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
    # The optional ABOUT text (RING PICKER round, owner ruling
    # 2026-08-06): theme-and-name marketing copy for the preset picker
    # — never a seat listing. Optional so a custom ring need not carry
    # one; the six bundled cards ship it VERBATIM from the approved
    # round (research/crown_content.md §5).
    about = str(entry.get("about", "")).strip() or None
    return {
        "name": name,
        "positions": positions,
        "jewels": jewels,
        "outer": outer,
        "triangle": triangle,
        "legend": legend,
        "crown_text": crown_text,
        "thematic": thematic,
        "about": about,
    }


#: The BUNDLED presets, parsed and validated ONCE per process (owner bug
#: 2026-08-06). The file is small but this function sits on the skin
#: install path — every settings change, on every watch, re-read and
#: re-validated all of it. The bundled entries are identical for every
#: watch; only the CUSTOM list and the PICK are per-watch, and the
#: custom list is validated fresh below on every call, as it must be.
_BUNDLED: list | None = None


def _bundled_presets() -> list:
    global _BUNDLED
    if _BUNDLED is None:
        raw = load_json_checked(
            paths.database_dir() / "ring_presets.json", "Ring presets database"
        )
        _BUNDLED = list(raw["presets"])
    return _BUNDLED


def ring_presets(custom: tuple = ()) -> dict:
    """name -> validated card for every bundled + custom preset."""
    presets: dict = {}
    for entry in _bundled_presets() + list(custom):
        card = validate_preset(entry)
        if card["name"] in presets:
            raise ValueError(f"ring preset name {card['name']!r} is duplicated")
        presets[card["name"]] = card
    return presets
