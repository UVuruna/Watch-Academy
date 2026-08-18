"""THE SKIN BUILDER — settings in, a `SkinDefinition` out.

One question, asked on every launch and after every pick the owner
makes: given these `Settings` and this location, what exactly does the
dial look like? Ring preset and finish, pointer and its palette, hands,
the weekday cast and its metal, the slots' content and seating, crown
text, numerals, opacity — all of it resolved into the ONE typed record
(`skins.manifest.SkinDefinition`) the render layer paints from.

It lived at the top of `app/controller.py` — a thousand module-level
lines in front of a 3,000-line class that only CALLS them. The OOP audit
of 2026-08-18 measured that file at 4,483 lines carrying seven
responsibilities and named this the first cut (R10), because these are
free functions over plain data: they read no `self`, own no window, and
28 test files already imported them directly, as if the module they
wanted had always existed.

What did NOT come along, and why: the anchor filters
(`_filtered_sun_anchors`, `_filtered_moon_events`) belong to Time
Travel's jump keys, `_next_rotation_theme` to the rotation cycler,
`_StayOpenMenu` and `_guard_exclusive_choice` to the menu, and
`_location_flash_text` to the on-screen flash — none of them builds a
skin.

Layer: app (it reads `data` and `render` for asset resolution). The
controller and the tests both call `build_skin` / `apply_display_
settings` / `display_for` / `watch_title`.

Documentation: __about/skin_builder.md · __flow/skin_builder.md.
"""

import dataclasses
import sys
from pathlib import Path

from app.settings_store import Settings
from app.watch_face import thumbs
from config import (
    archetypes, constants, defaults, dial, palette, pantheon, paths,
    profiling,
)
from core.crown_text import free_arc_angles
from core.world import arc_centre_deg
from data.hands import HAND_NAMES, hand_packs
from data.rings import ring_presets
from render import letter_plates
from skins.manifest import HandSpec, HandsSpec


def _jewel_metal(position: int, outer_metal: dict, finish: str) -> str:
    """The owner's metal rules (extended with bronze 2026-07-12):
    4-position outers — the trio of one metal forms the outer's own
    TRIANGLE and the remaining letter wears the ACCENT metal (gold ->
    3 gold + 1 silver; silver -> 3 silver + 1 gold; bronze -> 3 bronze
    + 1 silver); "hexa" wears the ONE finish metal on all six — UNLESS
    the ring preset overrides the triangle (ROADMAP 15b — TWO METALS
    RETIRED, owner decree 2026-08-11: every ring now wears the plain
    one-metal reading; `outer_metal["triangle"]` is never populated by
    a resolved skin any more, so this branch is dead in practice and
    kept only as the shared 4-position rule's general form)."""
    if not outer_metal["triangle"] or position in outer_metal["triangle"]:
        return finish
    return "gold" if finish == "silver" else "silver"


def _ring_eye_shine(settings: Settings, card: dict) -> bool:
    """Whether the ACTIVE preset's Eye of Providence wears the glory
    of rays (DOLLAR/EYE round, owner decree 2026-07-27) — only presets
    seating the ADAPTIVE eye glyph (`constants.RING_EYE_GLYPH`, the
    Dollar today) are eligible; a custom ring with one of the four
    EXPLICIT eye variants has its rays baked into the chosen glyph and
    always reads False here. The user's stored per-preset choice
    (`Settings.ring_eye_shine`) wins; absent, the owner's documented
    per-preset default (`constants.RING_EYE_SHINE_DEFAULT`, Dollar
    True — the banknote's own eye radiates)."""
    if constants.RING_EYE_GLYPH not in card["jewels"]:
        return False
    return settings.ring_eye_shine.get(
        card["name"], constants.RING_EYE_SHINE_DEFAULT.get(card["name"], False)
    )


def watch_title(
    settings: Settings, full: bool = False, location_name: str | None = None,
) -> str:
    """The watch's own display NAME (owner INSTRUCTION.txt item 2A,
    R5 MENU REWORK round). A single watch shows just its LOCATION in
    the right-click/tray menus (`full=False`, the default); the FULL
    multi-attribute form backs the tray hover TOOLTIP always —
    f"{location}-{ring_finish} {ring}-{palette label} {pointer}", e.g.
    "Belgrade-Gold DOMY-Family Trinity". With 2+ watches (ADD WATCH
    round) the menu TITLE row and tray-menu title switch to the full
    form too — `WatchController` decides `full` from its own
    `watch_count()` callback at every call site; this function stays
    the ONE place that KNOWS the format, so that round only had to
    loop it, never reinvent it.

    `location_name` (R-31 fix, 2026-08) overrides `settings.city_name`
    for the LOCATION word alone: a running Quick Jump/Time Travel/
    Greenwich simulation moves the observer WITHOUT touching the home
    `Settings`, so the tray tooltip/menu title used to freeze on the
    home city forever — `WatchController` passes its own live
    `_active_location_name` here, which the exact same jump/settings
    paths that flash the location (R-30, `_flash_location`) keep
    current.

    Deliberately UNTRANSLATED (no `tr`): a NAME is an identifier, not
    UI chrome — the same treatment the ring preset name and the
    pointer's own `POINTER_DISPLAY_NAMES` already get (protected proper
    nouns, invariant across languages). The palette label is the
    pointer's own wheel-pair (`constants.POINTER_PALETTE_LABELS`), read
    by the ACTIVE `palette_style` — the SAME table the Design menu's
    pair labels translate from (Rule #5, one source)."""
    location = settings.place.name if location_name is None else location_name
    if not full:
        return location
    labels = constants.POINTER_PALETTE_LABELS.get(
        settings.pointer, constants.POINTER_PALETTE_LABELS["default"]
    )
    styles = constants.palette_styles_for(settings.pointer)
    style = palette.effective_palette_style(
        settings.pointer, settings.palette_style
    )
    palette_label = labels[styles.index(style)]
    pointer_name = constants.POINTER_DISPLAY_NAMES[settings.pointer]
    return (
        f"{location}-{settings.ring_finish.capitalize()} "
        f"{settings.ring}-{palette_label} {pointer_name}"
    )


def _theme_metal(settings: Settings, theme: str) -> str:
    """The METAL a bronze-plate theme wears (owner 2026-07-12):
    follow-the-ring wins, then the per-theme Settings choice, then
    bronze — the art as drawn. Non-metal themes are always bronze."""
    if theme not in constants.METAL_THEMES:
        return "bronze"
    if settings.theme_metal_follow_ring:
        # The THEMATIC finish reads as gold outside the ring band
        # (ENLARGE/THEMATIC round containment — the theme plates have
        # no colored-ramp path of their own).
        if settings.ring_finish == "thematic":
            return "gold"
        return settings.ring_finish
    return settings.theme_metals.get(theme, "bronze")


def _resolve_hands(settings: Settings):
    """The chosen HAND PACK (owner spec 2026-07-12) resolved into a
    HandsSpec: image sizes read here (header-only), pivots and z-order
    from the pack's hands.json; tip reach targets from defaults. A
    vanished USER pack falls back to CLASSIC with a stderr note
    (documented — an uninstalled pack must not brick the startup);
    user-pack art is desaturated so the clock tint can recolor it."""
    from PySide6.QtGui import QImageReader

    packs = hand_packs()
    chosen = next(
        (name for name in packs if name.lower() == settings.hands.lower()),
        None,
    )
    if chosen is None:
        print(
            f"hand pack {settings.hands!r} is gone — using CLASSIC",
            file=sys.stderr,
        )
        chosen = "CLASSIC"
    pack = packs[chosen]
    specs = {}
    for hand in HAND_NAMES:
        path = pack["files"][hand]
        size = QImageReader(str(path)).size()
        if size.height() <= 0:
            raise ValueError(f"hand pack {chosen!r}: unreadable {path}")
        x, y = pack["pivots"][hand]
        specs[hand] = HandSpec(
            asset=path,
            natural_height=float(size.height()),
            pivot_y=y,
            pivot_x_fraction=None if x is None else x / size.width(),
        )
    bundled = pack["dir"].parent == paths.assets_dir() / "instrument" / "hands"
    return HandsSpec(
        hour=specs["hours"],
        minute=specs["minutes"],
        second=specs["seconds"],
        minute_reach_fraction=dial.HAND_MINUTE_REACH_FRACTION,
        second_reach_fraction=dial.HAND_SECOND_REACH_FRACTION,
        z_order=pack["z_order"],
        desaturate=not bundled,
    )


@profiling.timed("Build skin")
def build_skin(settings: Settings, location_display: str = ""):
    """The ONE render config: DEFAULT_SKIN with the chosen RING PRESET
    CARD (Database/ring_presets.json + the user's custom cards — owner
    spec: {name, positions, letters}, the positions signature picks the
    layout/face), the jewel art of the chosen finish, the chosen HAND
    PACK and the user's display choices overlaid.

    `location_display` (RING VERDICTS round, owner decree 2026-08-05,
    the LOCATION crown option) is the ACTIVE location's "CITY, COUNTRY"
    text — `WatchController` passes its own live
    `_active_location_display` (the same value `_flash_location`
    resolves, R-30's own formatter, never duplicated); absent (every
    direct/test caller) the Location crown option simply draws nothing
    for this build rather than crashing.

    The WHOLE build runs inside this watch's own display context (owner
    bug 2026-07-28): every asset path it resolves goes through the ART
    SOURCE, so building watch 2's skin must never see watch 1's."""
    with paths.display(display_for(settings)):
        return _compose_skin(settings, location_display)


def _resolve_ring_inner(settings: Settings, card: dict) -> Path:
    """The preset's ACTIVE inner band (owner decree 2026-08-05: the
    inner is user-changeable independent of the outer's lock). The
    user's stored per-preset choice (`Settings.ring_inner`) wins;
    absent, the bundled presets' own coordinator-recommended default
    (`constants.RING_INNER_PRESET_DEFAULT`), else the custom-ring
    fallback (`constants.RING_INNER_DEFAULT`)."""
    default = constants.RING_INNER_PRESET_DEFAULT.get(
        card["name"], constants.RING_INNER_DEFAULT
    )
    inner = settings.ring_inner.get(card["name"], default)
    if inner not in constants.RING_INNERS:
        inner = default
    return dial.RING_INNER_ART_DIR / f"{inner}.png"


def _location_crown_text(text: str) -> str:
    """The LOCATION crown's own renderable text (RING VERDICTS round,
    owner decree 2026-08-05) — the crown-text glyph library is a FIXED set
    (`constants.RING_CROWN_TEXT_CHARSET`: uppercase Latin/Greek, digits,
    the space), while a city/country name is free-form (lower case, a
    comma, accents no glyph exists for). Uppercased, then filtered to
    that exact drawable set (never a hand-picked substitution list —
    Rule #5, the SAME set the crown-text field's own input validator
    enforces), with the leftover run of spaces (the dropped comma among
    them) collapsed to one. An input that filters down to nothing
    (every character unsupported) returns "" — the caller's own
    graceful-absence path (no crown drawn) then applies unchanged."""
    filtered = "".join(
        char for char in text.upper() if char in constants.RING_CROWN_TEXT_CHARSET
    )
    return " ".join(filtered.split())


def _compose_skin(settings: Settings, location_display: str = ""):
    card = ring_presets(settings.custom_rings)[settings.ring]
    outer = constants.RING_OUTERS[card["outer"]]
    # TWO METALS RETIRED (owner decree 2026-08-11): every ring wears
    # the plain one-metal reading now — see `_jewel_metal`'s docstring.
    metal_layout = {"triangle": ()}
    # The Eye's SHINE (DOLLAR/EYE round, owner decree 2026-07-27): the
    # adaptive eye glyph swaps its whole stem for the glory-of-rays
    # master when the per-preset toggle is on — see `_ring_eye_shine`.
    eye_shine = _ring_eye_shine(settings, card)
    jewels = {}
    jewel_art = {}
    jewel_metal = {}
    jewel_legend = {}
    jewel_zoom = {}
    jewel_no_shadow = {}
    for position, glyph in zip(card["positions"], card["jewels"]):
        hour = position % 24                     # cards say 24, hours say 0
        jewels[hour] = glyph
        # The jewel art is ALWAYS the gold master — silver/bronze are
        # derived from it AT LOAD (owner 2026-07-19,
        # render.asset_recolor.jewel_metal_file), never pre-rendered files.
        if eye_shine and glyph == constants.RING_EYE_GLYPH:
            master = dial.LETTER_ART_DIR / constants.RING_EYE_SHINE_FILE
        else:
            master = letter_plates.plate_path(glyph)
        stem = master.stem
        if stem.startswith("Eye_shine"):
            # THE SHINE ENLARGE (owner UV inbox 2026-07-27): the rays
            # pad the triangle, so the shine master draws bigger and
            # the TRIANGLE stays the no-light size. Explicit custom
            # variants carry their source in the stem; the adaptive
            # glyph reads the Settings art source directly.
            source = (
                stem.rsplit("_", 1)[-1]
                if stem.endswith(("_gem", "_gpt"))
                else paths.ART_SUFFIX[settings.art_source]
            )
            jewel_zoom[hour] = constants.RING_EYE_SHINE_ENLARGE[source]
            # SHADOW/SHINE round (owner ruling 2026-08-06): the baked
            # glory-of-rays master already carries its own light, so the
            # ring's cast-shadow stamp is skipped for this seat — same
            # condition as the enlarge factor just above (any resolved
            # "Eye_shine*" stem, toggle-driven or an explicit custom pick).
            jewel_no_shadow[hour] = True
        jewel_art[hour] = master
        jewel_metal[hour] = _jewel_metal(position, metal_layout, settings.ring_finish)
        if position in card["legend"]:
            jewel_legend[hour] = card["legend"][position]
    # The outer GREAT SEAL CROWN TEXT ARC (TASK 1, owner "može radi"
    # 2026-07-19): the preset's own `crown_text` card already carries the
    # resolved per-glyph angles (data.rings.validate_preset ->
    # core.crown_text.crown_glyph_angles) — here we only pair each non-space
    # character with its gold-master asset path (spaces are dropped, so
    # RingLayer's draw loop never has to check for them) and pick the
    # ONE finish the whole inscription wears (the same settings.
    # ring_finish the Trinity-triangle jewels use — the crown text is read
    # as one continuous inscription, not a seat-by-seat split).
    crown_arc_entries = list(card["crown_text"])
    # CROWN TEXT for CUSTOM rings (owner decree 2026-08-05): the
    # bundled presets keep their existing crown text (above); a custom
    # ring's own free-typed inscription is a SETTINGS-level choice
    # (`Settings.custom_ring_crown_text`/`custom_ring_crown_orientation`,
    # like `ring_inner`), resolved here rather than baked into the
    # card at creation time — the user can retype it any time. Unknown
    # characters (outside the jewel library) silently drop the crown
    # text for this build rather than crashing the running app on a
    # keystroke; a KNOWN GAP — see the session's OPEN QUESTIONS for the
    # honest alternative (a visible validation message).
    if settings.ring not in constants.RING_OUTER_LOCK:
        crown_text = settings.custom_ring_crown_text.get(settings.ring, "")
        if crown_text and not any(
            char != " " and char not in constants.LETTER_PLATE_FILES
            for char in crown_text
        ):
            orientation = settings.custom_ring_crown_orientation.get(
                settings.ring, "top"
            )
            angles = free_arc_angles(crown_text, orientation)
            crown_arc_entries.append({
                "text": crown_text, "angles": angles,
                "words": ({
                    "text": crown_text, "start": 0,
                    "end": len(crown_text) - 1, "seat": None,
                },),
            })
    # THE LOCATION CROWN (RING VERDICTS round, owner decree 2026-08-05):
    # when the per-ring toggle is on, the ACTIVE location REPLACES
    # whatever crown text the ring carries (a preset's own crown text or a
    # custom ring's typed text) — available for bundled presets AND
    # custom rings alike, since it is keyed by ring name.
    # `location_display` is the "CITY, COUNTRY" text
    # `WatchController._active_location_display` already resolves
    # through `_location_flash_text` (R-30's own formatter — reused,
    # never duplicated); an empty/unfiltered result (no controller
    # context, or a name with no drawable character at all) leaves
    # whatever crown the ring already had, the same graceful-absence
    # pattern the custom crown text uses above.
    #
    # THE RULED LOCATION ARC (owner defect 2026-08-07 — "The One's bottom
    # location line does not exist; implement it"): the ledger
    # (ring_rework §4, row D) rules The One's BOTTOM arc to be "City,
    # Country", and that is a property of the PRESET, not of the user
    # toggle above. `dial.RING_LIVE_CROWN[...]["location"]` names its
    # orientation; the arc is APPENDED (never replacing the preset's own
    # crown text, and never at "top", where it would run straight through
    # the live time). The user toggle still wins when it is ticked — it
    # already produced a location crown, and two of them would double.
    #
    # SEPARATOR: `_location_crown_text` drops the comma and collapses the
    # gap to ONE SPACE, because the jewel library has no comma plate
    # (`constants.LETTER_PLATE_FILES` — uppercase Latin/Greek,
    # digits, $, &, ✠, the Eye and the colon). "Belgrade, Serbia" reads
    # "BELGRADE SERBIA". That is the product's existing separator
    # practice, not a new invention: it is what the user toggle has drawn
    # since the RING VERDICTS round, and reusing it keeps ONE formatter
    # (Rule #5) instead of teaching the ruled arc a second one.
    ruled_location = dial.RING_LIVE_CROWN.get(settings.ring, {}).get("location")
    if ruled_location and not settings.ring_crown_location.get(settings.ring, False):
        location_text = _location_crown_text(location_display)
        if location_text:
            crown_arc_entries = list(crown_arc_entries) + [{
                "text": location_text,
                "angles": free_arc_angles(location_text, ruled_location),
                "words": ({
                    "text": location_text, "start": 0,
                    "end": len(location_text) - 1, "seat": None,
                },),
                "reading": dict(dial.RING_LIVE_CROWN_LOCATION_READING),
            }]
    if settings.ring_crown_location.get(settings.ring, False):
        location_text = _location_crown_text(location_display)
        if location_text:
            angles = free_arc_angles(location_text, "top")
            crown_arc_entries = [{
                "text": location_text, "angles": angles,
                "words": ({
                    "text": location_text, "start": 0,
                    "end": len(location_text) - 1, "seat": None,
                },),
                # THE ONE's OWN LOCATION LINE (ring_rework §3, owner
                # ruling 2026-08-06): verbatim from
                # research/crown_content.md §1 — the counterpart to the
                # live-hour crown's own reading (dial.RING_LIVE_CROWN_READING).
                # Stated once in config since 2026-08-07, shared with the
                # preset's own ruled bottom arc above (Rule #5).
                "reading": dict(dial.RING_LIVE_CROWN_LOCATION_READING),
            }]
    crown_arc = _crown_arc_glyphs(crown_arc_entries)
    # THE INVERTED CROWN TEXTS (owner verdict 2026-08-14): the preset's
    # own night pair, built by the SAME pass (Rule #5) — never extended
    # by the custom/location crowns above, which belong to the day list
    # and re-seat mirrored like every other preset's arcs.
    crown_arc_night = _crown_arc_glyphs(card["crown_text_night"])
    skin = dataclasses.replace(
        defaults.DEFAULT_SKIN,
        ring=dataclasses.replace(
            defaults.DEFAULT_SKIN.ring,
            outer_asset=dial.RING_OUTER_ART_DIR / outer["file"],
            inner_asset=_resolve_ring_inner(settings, card),
            jewels=jewels,
            jewel_art=jewel_art,
            jewel_metal=jewel_metal,
            jewel_legend=jewel_legend,
            jewel_zoom=jewel_zoom,
            jewel_no_shadow=jewel_no_shadow,
            crown_text=crown_arc,
            crown_text_night=crown_arc_night,
            crown_text_metal=settings.ring_finish,
        ),
        hands=_resolve_hands(settings),
    )
    return apply_display_settings(skin, settings)


def _crown_arc_glyphs(entries) -> tuple:
    """Card crown-text entries -> render-ready arc entries (glyph asset
    + angle pairs, per-word hover geometry, the entry's own reading) —
    ONE builder for the day list and the night list (THE INVERTED CROWN
    TEXTS, owner verdict 2026-08-14), so the two can never drift in
    shape."""
    return tuple(
        {
            "text": entry["text"],
            "glyphs": tuple(
                (letter_plates.plate_path(char), angle)
                for char, angle in zip(entry["text"], entry["angles"])
                if char != " "
            ),
            # THE ARC'S OWN CENTRE (owner defect 2026-08-16 — "M from the
            # ring and M from MUNDORUM do not line up nicely"): solved
            # from the WHOLE run, spaces included, because that is the
            # arc the pins were laid out across. The glyph list above
            # DROPS the spaces, and MUNDORUM ORDO NUMEN's two do not sit
            # symmetrically in it, so a centre re-derived from the drawn
            # glyphs stood 1.41 deg off — and THE ARC READING LAW's
            # reflection about the wrong axis moved every letter by
            # TWICE that, carrying the M 2.8 deg past its own jewel.
            # Solved ONCE here, never re-derived at paint time.
            "centre": arc_centre_deg(entry["angles"]),
            # Per-WORD hover geometry (WORD-HOVER round, owner
            # 2026-07-27): each word's angular center/half-span plus
            # the seat whose legend it answers with — solved once here,
            # read by render.compositor._ring_word_legend_tooltip.
            "words": tuple(
                {
                    "text": word["text"],
                    "seat": word["seat"],
                    "center": (
                        (entry["angles"][word["start"]]
                         + entry["angles"][word["end"]]) / 2.0
                    ) % 360.0,
                    "half": (
                        abs(entry["angles"][word["end"]]
                            - entry["angles"][word["start"]]) / 2.0
                        + dial.RING_CROWN_TEXT_LETTER_STEP_DEG / 2.0
                    ),
                }
                for word in entry["words"]
            ),
            # THE ONE TERM ONE HOVER LAW (ring_rework §3, owner ruling
            # 2026-08-06): an entry's own `reading`, when it carries
            # one, wins over the seat's letter legend in
            # render.compositor._ring_word_legend_tooltip. Custom rings'
            # free-typed/location crowns never carry one (graceful
            # absence — dict.get default).
            "reading": entry.get("reading"),
        }
        for entry in entries
    )


def slot_seconds(settings: Settings) -> bool:
    """Whether any ENABLED slot runs the small-seconds complication
    (owner 2026-07-14) — the big hand yields and its Visible toggle
    grays out."""
    if settings.show_weekday and settings.weekday_slot == "seconds":
        return True
    if settings.show_octa_slot and settings.octa_slot == "seconds":
        return True
    return (
        settings.show_third_slot
        and settings.show_octa_slot
        and settings.third_slot == "seconds"
    )


def effective_weekday_slot(settings: Settings) -> str:
    """The 1st slot's effective mode. Under the owner's SLOT MATRIX
    (2026-07-14) every mode is real under every pointer — the matrix
    gives it a seat. The single lock: the Seasons with all THREE
    slots up keep the 1st on the weekday unit (owner: mora 1st da
    bude weekday)."""
    if (
        settings.pointer == "cross"
        and settings.show_pointer
        and settings.show_octa_slot
        and settings.show_third_slot
    ):
        return "weekday"
    return settings.weekday_slot


def _classic_slot_theme(settings: Settings) -> tuple[str, str | None]:
    """The (theme, metal) DRESSING the classic weekday unit: normally
    the 1st slot's — except the Seasons/Compass two-slot case where
    only the 2ND is weekday, so the 2nd rides the rotation in its own
    theme (owner 2026-07-15)."""
    if (
        settings.pointer in ("cross", "octa")
        and settings.show_pointer
        and settings.show_weekday
        and settings.show_octa_slot
        and not settings.show_third_slot
        and effective_weekday_slot(settings) != "weekday"
        and settings.octa_slot == "weekday"
    ):
        theme = settings.info_slot_theme
        return theme, _theme_metal(settings, theme), settings.info_slot_roster
    theme = settings.weekday_theme
    return theme, _theme_metal(settings, theme), settings.weekday_roster


def _themed_weekday_set(base, theme: str, metal: str | None):
    """The weekday unit dressed in `theme` wearing `metal` — the
    SYMBOLISM canon swap (entity-named files, canon display names;
    "planets" keeps the pack's own unit), the hue-SELECTIVE metal at
    render, and the Sunday Servant dual (the COLORED look swaps in
    the sibling variant; owner restructure 2026-07-14)."""
    weekday = base
    if theme != "planets":
        names = pantheon.WEEKDAY_THEME_NAMES[theme]
        weekday = dataclasses.replace(
            weekday,
            # PENDING art (documented): a seat whose plate the owner
            # has not generated yet (the Ancient set's Eleusis today)
            # maps to None — the manifest contract draws the
            # procedural colored disc with the name label instead of
            # crashing on a missing file. The candidate path itself
            # comes from the ONE shared resolver (Rule #5 — this used
            # to re-type the theme_dir/colored-folder expression);
            # no `on_date` here — this dict is BAKED once at settings-
            # apply time, so a daily rotation pick would go stale
            # across a multi-day run. `render.weekday_body.draw_weekday_body`
            # re-resolves the LIVE rotation on top of whichever
            # canonical file lands here (same law as its own CONTINENTS
            # live override, right below it).
            bodies={
                body: (
                    candidate
                    if paths.art_file(candidate).exists()
                    else None
                )
                for body in names
                for candidate in (
                    pantheon.weekday_theme_body_art(
                        theme, body, colored=(metal == "colored")
                    ),
                )
            },
            body_names=dict(names),
        )
    if metal in defaults.METAL_SWAP_TARGETS:
        weekday = dataclasses.replace(weekday, metal=metal)
    dual_rel = pantheon.WEEKDAY_DUAL_FILES[theme]
    if metal == "colored" and theme in constants.METAL_THEMES:
        dual_rel = pantheon.colored_variant_rel(dual_rel)
    dual = pantheon.weekday_art(f"{dual_rel}.png")
    if not paths.art_file(dual).exists():
        # PENDING art (documented): a rework can point the dual at a
        # plate the owner has not generated yet (the Creeds' Satanism
        # dual today) — the Sunday runs single-faced until it lands,
        # never wearing a wrong plate.
        dual = None
    return dataclasses.replace(weekday, dual_asset=dual)


def _pantheon_weekday_set(base, theme: str, metal: str | None):
    """The PANTHEON roster's weekday set (owner doctrine 2026-07-15):
    per seat the first EXISTING candidate plate wins with the pantheon
    identity (name + pantheon article); a seat whose art has not
    landed yet falls back to the PLANETARY bundle — file, name and
    article TOGETHER, so a half-generated pantheon never pairs a
    wrong figure with a wrong text. The Sunday dual and its names
    follow the same rule."""
    table = pantheon.WEEKDAY_PANTHEON[theme]
    planetary = _themed_weekday_set(base, theme, metal)
    bodies: dict = {}
    names: dict = {}
    articles: dict = {}
    for body in constants.WEEKDAY_BODIES:
        seat = pantheon.pantheon_seat(theme, body)
        if seat is not None:
            bodies[body], names[body], articles[body] = seat
        else:
            bodies[body] = planetary.bodies[body]
            names[body] = planetary.body_names[body]
            articles[body] = (
                constants.WEEKDAY_THEME_ARTICLES[theme], body
            )
    dual_rel = table["dual"][0]
    dual = pantheon.weekday_art(f"{dual_rel}.png")
    if paths.art_file(dual).exists():
        dual_names = table["dual_names"]
        faces_set = table["articles"]
    else:
        # The pantheon dual's plate has not landed — the WHOLE Sunday
        # pair falls back together (plate, names AND face texts), so
        # the hover never says Hades over a Phaethon plate.
        dual = planetary.dual_asset
        dual_names = pantheon.WEEKDAY_DUAL_NAMES[theme]
        faces_set = None
    return dataclasses.replace(
        planetary,
        bodies=bodies,
        body_names=names,
        dual_asset=dual,
        article_set=faces_set,
        body_articles=articles,
        dual_names=dual_names,
    )


def display_for(settings: Settings) -> paths.DisplayContext:
    """THIS WATCH's own art choices as one immutable bundle (owner bug
    2026-07-28): the art source (owner 2026-07-14: Gemini vs ChatGPT),
    the subdial plate set (owner decree 2026-07-21) and the metal shades
    (R8a). All three used to be process-wide globals written on every
    skin install, which made every open watch render with the LAST-BUILT
    watch's choices — see `config.paths.DisplayContext` for the full
    post-mortem.

    THE THEMATIC pseudo-metal's shade follows the ACTIVE ring preset
    (ENLARGE/THEMATIC round, owner 2026-07-27): DOMY cross red, LOOP
    cross blue, Dollar green, The One moon indigo, Templar black. A
    CUSTOM ring may carry its OWN pick on its card — any transformer
    ramp, metals included (owner: "iron, copper... sve") — else the
    moon indigo. Not a Settings entry: the ring choice IS the choice."""
    thematic_shade = constants.RING_THEMATIC_SHADES.get(settings.ring)
    if thematic_shade is None:
        card = ring_presets(settings.custom_rings).get(settings.ring)
        thematic_shade = (
            (card or {}).get("thematic")
            or constants.METAL_SHADE_DEFAULT["thematic"]
        )
    return paths.display_context(
        art_source=settings.art_source,
        subdial_set=settings.subdial_set,
        metal_shades={
            "gold": settings.metal_shade_gold,
            "bronze": settings.metal_shade_bronze,
            "silver": settings.metal_shade_silver,
            "thematic": thematic_shade,
        },
    )


def apply_display_settings(skin, settings: Settings):
    """The user's choices win over whatever the skin pack declares:
    the tray display scalars, the opacity overrides (twilight alphas
    scale proportionally with the day alphas) and the custom palette
    for the active (pointer, style). Module-level — testable without
    a controller.

    The overlay runs INSIDE this watch's display context: the weekday/
    slot art it resolves goes through the ART SOURCE, so a watch on
    Gemini art must not read a sibling's ChatGPT choice."""
    display = display_for(settings)
    with paths.display(display):
        return _overlay_display_settings(skin, settings, display)


def _overlay_display_settings(skin, settings: Settings, display):
    # THE ARCHETYPE MODE (owner sealed package 2026-07-16): active
    # while the drawn pointer carries an archetype. The overriding
    # itself happens at the RENDER level (render.slot_layout.enabled_slots
    # answers empty), so every slot/weekday setting below stays the
    # user's own — toggling the mode back restores everything.
    archetype_on = (
        settings.archetype_mode
        and settings.show_pointer
        and archetypes.has_archetype(settings.pointer)
    )
    star = skin.star
    if settings.star_alpha is not None:
        star = dataclasses.replace(
            star,
            day_alpha=settings.star_alpha,
            twilight_alpha=settings.star_alpha
            * (star.twilight_alpha / star.day_alpha),
        )
    weekday = skin.weekday_set
    if settings.ghost_alpha is not None:
        # THE GHOST OPACITY OVERRIDE (Watch Face Phase 4, R-36 —
        # "Inactive icons"): None (default) keeps the active theme's own
        # `ghost_opacity` — themes differ today.
        weekday = dataclasses.replace(weekday, ghost_opacity=settings.ghost_alpha)
    if settings.slot_scale != 1.0:
        # ONE slot size (owner 2026-07-14): the multiplier scales the
        # spec values directly — bodies, subdials, hit regions alike.
        weekday = dataclasses.replace(
            weekday,
            diamond_scale=weekday.diamond_scale * settings.slot_scale,
            center_scale=weekday.center_scale * settings.slot_scale,
        )
    # The CLASSIC unit wears the theme of the slot that DRIVES it
    # (owner 2026-07-15): on the Seasons/Compass with two slots where
    # only the 2nd is weekday, that slot rides the rotation in ITS
    # OWN theme.
    theme, metal, roster = _classic_slot_theme(settings)
    if roster == "pantheon" and theme in pantheon.WEEKDAY_PANTHEON:
        weekday = _pantheon_weekday_set(weekday, theme, metal)
    else:
        weekday = _themed_weekday_set(weekday, theme, metal)
    background = skin.background
    if settings.aura_day_alpha is not None or settings.aura_twilight_alpha is not None:
        # The Aura's sunlight and twilight opacities are INDEPENDENT
        # overrides (owner spec) — no coupling ratio between them.
        background = dataclasses.replace(
            background,
            day_alpha=(
                settings.aura_day_alpha
                if settings.aura_day_alpha is not None
                else background.day_alpha
            ),
            twilight_alpha=(
                settings.aura_twilight_alpha
                if settings.aura_twilight_alpha is not None
                else background.twilight_alpha
            ),
        )
    marker = skin.year_marker
    if settings.earth_scale != 1.0 or settings.moon_scale != 1.0:
        marker = dataclasses.replace(
            marker,
            scale=marker.scale * settings.earth_scale,
            moon_scale=marker.moon_scale * settings.moon_scale,
        )
    # THE POSITION POINTER's color (owner feature 2026-08-09, Settings ▸
    # Earth): resolved ONCE here, never at paint time — `render/` never
    # imports `app/` (the one-way flow), and `thumbs.shade_hue` is a UI
    # accessor that reads `recolor/presets/metals.json` from disk, fine
    # on a settings change, never on a per-tick paint. The SAME metal
    # the ring's crown text wears (`skin.ring.crown_text_metal`, set by
    # `_compose_skin` before this overlay runs), at its ACTIVE shade
    # (`display.shade`, the same accessor `jewel_metal_file` resolves
    # through) — a custom ring's thematic name outside every known ramp
    # is the only way this falls back to THE PALETTE COLOUR LAW's own
    # `palette.MARKER_POINTER_FALLBACK_COLOR`.
    pointer_metal = skin.ring.crown_text_metal
    pointer_color = (
        thumbs.shade_hue(pointer_metal, display.shade(pointer_metal))
        or palette.MARKER_POINTER_FALLBACK_COLOR
    )
    marker = dataclasses.replace(
        marker,
        moon_hidden_alpha=settings.moon_hidden_alpha,
        # The Earth marker's continent is no longer baked into the skin
        # (owner bug R-28, 2026-08): `earth_region` computes it LIVE
        # from the day context's own coordinates every paint, so it
        # follows Quick Jump/Time Travel/Greenwich the same way it
        # follows the home settings.
        # THE MOON TRANSIT OPACITY OVERRIDE (Watch Face Phase 4, R-35):
        # None (default) keeps the skin's own `dial.MOON_TRANSIT_OPACITY`.
        transit_alpha=(
            settings.moon_transit_alpha
            if settings.moon_transit_alpha is not None
            else marker.transit_alpha
        ),
        pointer_enabled=settings.show_marker_pointer,
        transit_shadow=settings.transit_shadow,
        transit_shrink=settings.transit_shrink,
        transit_rim=settings.transit_rim,
        pointer_color=pointer_color,
        moon_band_mode=settings.moon_band_mode,
        moon_band_style=settings.moon_band_style,
        # THE MOVING BODIES (owner verdict 2026-08-10): eight menus, one
        # roster — `constants.MOVING_BODY_MENUS` names every one, and
        # the spec carries a field of the SAME name for each, so this
        # overlay never needs a line per menu and can never drift from
        # what storage loads.
        **{
            name: getattr(settings, name)
            for name in constants.MOVING_BODY_MENUS
        },
    )
    # A stored "tertiary" wheel only holds where the pointer serves one
    # (trio/hexa/octa — CUBE.md); everywhere else it normalizes to
    # "primary" HERE, the one choke point, so no render consumer ever
    # indexes PALETTE_PRESETS/ARCHETYPE_GRID with a pair that does not
    # exist. The stored setting itself stays untouched — switching back
    # to a Cube pointer restores its Cube wheel.
    palette_style = palette.effective_palette_style(
        settings.pointer, settings.palette_style
    )
    return dataclasses.replace(
        skin,
        star=star,
        background=background,
        weekday_set=weekday,
        year_marker=marker,
        pointer=settings.pointer,
        umbra_form=settings.umbra_form,
        umbra_contrast=settings.umbra_contrast,
        palette_style=palette_style,
        calendar_mount=settings.calendar_mount,
        # THE TWO WORLD-MODES (ring_rework.md §1): a plain pass-through
        # — `core.world` turns it into the pointer rotation and the
        # world offset, and "noon_up" (the default) makes both
        # exactly what every release before this one computed.
        world_mode=settings.world_mode,
        # WHAT THE ROTATION CARRIES (owner ballot verdict 2026-08-13) —
        # another plain pass-through: the ring layer reads it to decide
        # whether the jewels and the crown take the world offset, and
        # the band spec reads it to decide which numerals a fixed jewel
        # hides. "all_turn" (the default) is every release's behaviour.
        world_rotation_scope=settings.world_rotation_scope,
        # Aurora is ALWAYS solar-rotated (owner spec 2026-07-12): its
        # bands anchor to the real sun events, so the whole wheel keeps
        # the solar frame regardless of the toggle.
        solar_rotation=(
            True if settings.pointer == "aurora" else settings.solar_rotation
        ),
        octa_slot=settings.octa_slot,
        day_slot_style=settings.day_slot_style,
        info_slot_style=settings.info_slot_style,
        info_slot_theme=settings.info_slot_theme,
        info_slot_metal=_theme_metal(settings, settings.info_slot_theme),
        info_slot_roster=settings.info_slot_roster,
        weekday_slot=effective_weekday_slot(settings),
        third_slot=settings.third_slot,
        third_slot_style=settings.third_slot_style,
        third_slot_theme=settings.third_slot_theme,
        third_slot_metal=_theme_metal(settings, settings.third_slot_theme),
        third_slot_roster=settings.third_slot_roster,
        # The slots enable IN ORDER (owner 2026-07-14): the third
        # exists only on top of the second.
        show_third_slot=settings.show_third_slot and settings.show_octa_slot,
        earth_style=settings.earth_style,
        weekday_theme=settings.weekday_theme,
        legend=settings.legend,
        era_notation=settings.era_notation,
        show_era_suffix=settings.show_era_suffix,
        third_era=settings.third_era,
        show_earth=settings.show_earth,
        show_moon=settings.show_moon,
        show_eclipse=settings.show_eclipse,
        show_weekday=settings.show_weekday,
        show_pointer=settings.show_pointer,
        colorful=settings.colorful,
        # The big seconds hand YIELDS while a slot runs the
        # small-seconds complication (owner 2026-07-14) — except in
        # archetype mode, where the slots are overridden OFF and the
        # big hand returns.
        show_seconds=settings.show_seconds
        and not (slot_seconds(settings) and not archetype_on),
        archetype_mode=settings.archetype_mode,
        archetype_names=settings.archetype_names,
        cube_look=settings.cube_look,
        daylight=settings.daylight,
        pointer_shape=settings.pointer_shape,
        polygon_curvature=settings.polygon_curvature,
        polygon_edge=settings.polygon_edge,
        hide_night_borders=settings.hide_night_borders,
        earth_label=settings.earth_label,
        show_octa_slot=settings.show_octa_slot,
        show_weekday_names=settings.show_weekday_names,
        show_info_slot_names=settings.show_info_slot_names,
        ring_tint=settings.ring_tint,
        # THE THEMATIC CONTAINMENT (ENLARGE/THEMATIC round, owner
        # 2026-07-27): `skin.ring_finish` feeds the METAL surfaces
        # outside the ring band (subdial borders/plates, hands, slot
        # roundels) — under the thematic finish those read as GOLD; the
        # theme color itself travels only through `ring.jewel_metal`/
        # `ring.crown_text_metal` ("thematic"), which the jewel recolor
        # pipeline resolves to the active preset's ramp.
        ring_finish=(
            "gold" if settings.ring_finish == "thematic"
            else settings.ring_finish
        ),
        subdial_style=settings.subdial_style,
        ring_jewels_scale=settings.ring_jewels_scale,
        hover_enlarge=settings.hover_enlarge,
        palette_override=settings.palettes.get(
            f"{settings.pointer}_{palette_style}"
        ),
        pointer_saturation=settings.pointer_saturation,
        ring_saturation=settings.ring_saturation,
        # Watch Face Phase 4 — Colors + Opacity: every new field is a
        # direct pass-through (Rule #5, no override/None dance needed —
        # each already carries its own honest default).
        umbra_tint_mode=settings.umbra_tint_mode,
        umbra_tint=settings.umbra_tint,
        umbra_saturation=settings.umbra_saturation,
        umbra_alpha=settings.umbra_alpha,
        aura_off_tint_mode=settings.aura_off_tint_mode,
        aura_off_tint=settings.aura_off_tint,
        hands_tint=settings.hands_tint,
        hands_saturation=settings.hands_saturation,
        jewels_tint=settings.jewels_tint,
        ring_tint_inner=settings.ring_tint_inner,
        crown_text_alpha=settings.crown_text_alpha,
        crown_text_scale=settings.crown_text_scale,
        crown_text_tint=settings.crown_text_tint,
        # THE LIVE NUMERAL BANDS (ring_rework.md §2/§5): direct
        # pass-throughs, exactly like the Phase-4 fields above — each
        # already carries the ledger's own SETTLED default, and the
        # render side keys its band cache on them, so a changed knob
        # re-renders both plates once and never per frame. `ring_name`
        # rides along so the numeral layers can ask
        # `dial.RING_LIVE_CROWN` whether this preset keeps a live time.
        numeral_outer_size=settings.numeral_outer_size,
        minutes_size=settings.minutes_size,
        numeral_outer_ring_size=settings.numeral_outer_ring_size,
        numeral_face=settings.numeral_face,
        minutes_face=settings.minutes_face,
        numeral_seating=settings.numeral_seating,
        numeral_relief=settings.numeral_relief,
        numeral_depth=settings.numeral_depth,
        numeral_light=settings.numeral_light,
        numeral_darkness=settings.numeral_darkness,
        numeral_contact_blur=settings.numeral_contact_blur,
        numeral_border=settings.numeral_border,
        crown_time_format=settings.crown_time_format,
        ring_name=settings.ring,
        display=display,
    )
