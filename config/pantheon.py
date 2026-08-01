"""The weekday THEME registry — who sits on which day, in which
art. Every WEEKDAY_* table (names, folders, files, duals, seat
rosters, menu grouping), the PANTHEON roster and its seat
resolver, the universal rotation convention every weekday
consumer (and the Encyclopedia's scale/title-plate art) calls
through, and the theme title-plate resolver.

Layer: config — pure, no Qt, no wall clock.
"""

import re
from datetime import date
from pathlib import Path

from config import constants, continents, paths


# --- The PANTHEON roster (owner doctrine 2026-07-15) --------------------------
# Per theme: each seat lists CANDIDATE art paths (relative to
# assets/weekday/, first existing wins) — a seat with NO existing
# candidate falls back to the PLANETARY bundle (file + name + article
# together) so a half-generated pantheon never shows a wrong
# (figure, article) pair. Colored variants live under the register's
# own <register>/colored/ child mirroring the bronze stems (tree law
# 2026-07-26 — identical for pantheon and primary alike).
WEEKDAY_PANTHEON = {
    "greek": {
        "articles": "greek_pantheon",
        "files": {
            "sun": ("greek/pantheon/bronze/Zeus", "greek/primary/bronze/Zeus"),
            "moon": ("greek/pantheon/bronze/Poseidon",),
            "mars": ("greek/pantheon/bronze/Artemis",),
            "mercury": ("greek/pantheon/bronze/Athena",),
            "jupiter": ("greek/pantheon/bronze/Apollo",),
            "venus": ("greek/pantheon/bronze/Hera",),
            "saturn": ("greek/pantheon/bronze/Demeter",),
        },
        "names": {
            "sun": "Zeus (\u0396\u03b5\u03cd\u03c2)",
            "moon": "Poseidon (\u03a0\u03bf\u03c3\u03b5\u03b9\u03b4\u1ff6\u03bd)",
            "mars": "Artemis (\u1f0c\u03c1\u03c4\u03b5\u03bc\u03b9\u03c2)",
            "mercury": "Athena (\u1f08\u03b8\u03b7\u03bd\u1fb6)",
            "jupiter": "Apollo (\u1f08\u03c0\u03cc\u03bb\u03bb\u03c9\u03bd)",
            "venus": "Hera (\u1f2d\u03c1\u03b1)",
            "saturn": "Demeter (\u0394\u03b7\u03bc\u03ae\u03c4\u03b7\u03c1)",
        },
        "dual": ("greek/pantheon/bronze/Hades",),
        "dual_names": ("Zeus", "Hades"),
    },
    "norse": {
        "articles": "norse_pantheon",
        "files": {
            "sun": ("norse/pantheon/bronze/Odin",),
            "moon": ("norse/pantheon/bronze/Hel",),
            "mars": ("norse/primary/bronze/Thor",),
            "mercury": ("norse/primary/bronze/Loki",),
            "jupiter": ("norse/primary/bronze/Tyr",),
            "venus": ("norse/pantheon/bronze/Frigg",),
            "saturn": ("norse/pantheon/bronze/Freyr",),
        },
        "names": {
            "sun": "Odin (\u00d3\u00f0inn)", "moon": "Hel",
            "mars": "Thor (\u00de\u00f3rr)", "mercury": "Loki",
            "jupiter": "Tyr (T\u00fdr)", "venus": "Frigg",
            "saturn": "Freyr",
        },
        "dual": ("norse/primary/bronze/Odin",),
        "dual_names": ("Odin", "The Wanderer"),
    },
    "egypt": {
        "articles": "egypt_pantheon",
        "files": {
            "sun": ("egypt/primary/bronze/Ra",),
            "moon": ("egypt/pantheon/bronze/Isis",),
            "mars": ("egypt/pantheon/bronze/Horus",),
            "mercury": ("egypt/primary/bronze/Thoth",),
            "jupiter": ("egypt/pantheon/bronze/Anubis",),
            "venus": ("egypt/pantheon/bronze/Bastet",),
            "saturn": ("egypt/primary/bronze/Osiris",),
        },
        "names": {
            "sun": "Ra", "moon": "Isis", "mars": "Horus",
            "mercury": "Thoth", "jupiter": "Anubis",
            "venus": "Bastet", "saturn": "Osiris",
        },
        "dual": ("egypt/primary/bronze/Afu_Ra",),
        "dual_names": ("Ra", "Afu-Ra"),
    },
    "slavic": {
        "articles": "slavic_pantheon",
        "files": {
            "sun": ("slavic/primary/bronze/Perun",),
            "moon": ("slavic/primary/bronze/Mokos",),
            "mars": ("slavic/primary/bronze/Svetovid",),
            "mercury": ("slavic/pantheon/bronze/Svarog",),
            "jupiter": ("slavic/primary/bronze/Dazbog",),
            "venus": ("slavic/pantheon/bronze/Lada",),
            "saturn": ("slavic/primary/bronze/Morana",),
        },
        "names": {
            "sun": "Perun", "moon": "Moko\u0161", "mars": "Svetovid",
            "mercury": "Svarog", "jupiter": "Da\u017ebog",
            "venus": "Lada", "saturn": "Morana",
        },
        "dual": ("slavic/primary/bronze/Veles",),
        "dual_names": ("Perun", "Veles"),
    },
}

def pantheon_seat(theme: str, body: str):
    """The PANTHEON seat bundle for (theme, body) — (art_path, name,
    (article_set, body)) with the safety law: the first EXISTING
    candidate plate wins with the pantheon identity; NO existing
    candidate returns None and the caller keeps the PLANETARY bundle
    whole (file + name + article together). Shared by the classic
    unit, the seated slots and the hover resolution."""
    from config import paths as _paths

    table = WEEKDAY_PANTHEON.get(theme)
    if table is None:
        return None
    for rel in table["files"][body]:
        path = weekday_art(f"{rel}.png")
        if _paths.art_file(path).exists():
            return (
                path,
                table["names"][body],
                (table["articles"], body),
            )
    return None


# THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20, sealed
# alongside Rule #19 "Compute, Don't Generate" — this is the sanctioned
# way an asset family gets MULTIPLE generated versions instead of one
# frozen master, so it never re-grows into another twelve-plate
# mistake): beside any canonical asset `<dir>/<Name>.png`, additional
# versions live EITHER as `<dir>/<Name>_v2.png`-style suffix siblings
# OR same-named files inside a `<dir>/alt/` subfolder — both pools
# merge into ONE daily rotation, picked deterministically by the
# traveled date's proleptic ordinal modulo the candidate count. Opt-in
# ONLY (never on the hot `art_file` path): a consumer calls
# `rotating_art_file` explicitly. The cadence — how many days each
# shown file stays before advancing (1 = a new face every day) — is
# shared by every rotating family.
ROTATION_DAYS = 1
_VERSION_SUFFIX = re.compile(r"^_v\d*$", re.IGNORECASE)


def _sourceless_core(name_stem: str) -> str:
    """A filename stem with its terminal source suffix stripped
    (`Lion_v2_gem` -> `Lion_v2`): the RESTRUCTURE moved the source off the
    folder tree and onto the filename, so version discovery matches the
    base/_vN AFTER dropping `_gem`/`_gpt`."""
    low = name_stem.lower()
    for suffix in ("_gem", "_gpt"):
        if low.endswith(suffix):
            return name_stem[: -len(suffix)]
    return name_stem


def _rotation_candidates_in(
    directory: Path, stems: tuple[str, ...]
) -> list[Path]:
    """Every version FILE directly inside `directory` for any base stem
    in `stems` — SUFFIX-AWARE: a trailing `_gem`/`_gpt` is stripped
    before the bare-stem / `stem_v*` match, so both sources' files are
    recognised (the active-source pick happens in `_rotation_candidates`).
    A synthetic tmp tree with suffix-less names exercises the naming
    tolerance directly (no dependency on the real bundled assets)."""
    if not directory.is_dir():
        return []
    candidates: list[Path] = []
    seen_names: set[str] = set()
    for stem in stems:
        stem_lower = stem.lower()
        for entry in directory.iterdir():
            if entry.name in seen_names or entry.suffix.lower() != ".png":
                continue
            core = _sourceless_core(entry.stem)
            if not core.lower().startswith(stem_lower):
                continue
            tail = core[len(stem):]
            if tail == "" or _VERSION_SUFFIX.match(tail):
                candidates.append(entry)
                seen_names.add(entry.name)
    return candidates


def _rotation_candidates(
    directories: tuple[Path, ...], stems: tuple[str, ...]
) -> list[Path]:
    """The daily-rotation pool across `directories`: every distinct
    SOURCELESS version core (base, base_v2, …; both sources fold to one
    core) resolved through `paths.art_file` to the ACTIVE source's file
    (cross-source / suffix-less fallback), so a two-source directory
    never doubles the pool. Sorted by (filename, full path) for a
    deterministic order even when two registers share a basename."""
    resolved: list[Path] = []
    seen_files: set[Path] = set()
    seen_cores: set[tuple] = set()
    for directory in directories:
        for entry in _rotation_candidates_in(directory, stems):
            core = _sourceless_core(entry.stem)
            key = (directory, core)
            if key in seen_cores:
                continue
            seen_cores.add(key)
            picked = paths.art_file(directory / f"{core}.png")
            if picked is not None and picked.exists() and picked not in seen_files:
                resolved.append(picked)
                seen_files.add(picked)
    resolved.sort(key=lambda p: (p.name, str(p)))
    return resolved


def _pick_rotation(candidates: list[Path], on_date: date) -> Path | None:
    """The ONE shared date-modulo pick every rotating family uses: zero
    candidates -> None (the caller keeps its own fallback), exactly one
    -> that one every day (nothing to rotate), otherwise the SAME date
    always yields the SAME file and consecutive dates advance through
    the set."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    index = (on_date.toordinal() // ROTATION_DAYS) % len(candidates)
    return candidates[index]


def _pick_weekly_mandate(candidates: list[Path], on_date: date) -> Path | None:
    """cp_corpo's WEEKLY MANDATE (owner decree 2026-07-29,
    `constants.NINTH_MECHANISMS["cp_corpo"] == "term_weekly"`): the
    RULING triple flips at the ISO calendar week BOUNDARY, not daily —
    even week rules the canonical (Arasaka) half, odd week the
    alternate (NUSA) half, same graceful degrade as `_pick_rotation`
    (zero -> None, one -> that one every week). A 53-week ISO year
    hands the odd side one extra week — the owner knows and accepts
    it."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    index = on_date.isocalendar()[1] % len(candidates)
    return candidates[index]


# THE SEAT ROSTER (Cyberpunk casts, sheet-sealed 2026-07-22; wired by
# completion wave II's second half, Session 32, 2026-07-29). The
# universal rotation above pools ONE figure's own `_v2` versions — a
# second artwork of the SAME figure, which is all the convention was ever
# asked to mean. The Cyberpunk sheet needs the other shape: a SEAT that
# holds several DIFFERENT named figures and turns through them
# ("figure-first rosters" in the sheet, where every file is named after
# the figure it depicts and never after the seat). Without this table
# twelve of that franchise's plates would sit on disk unreachable — the
# exact failure THE THEME COMPLETION LAW exists to end.
#
# theme -> seat label -> the roster's stems, CANONICAL FIRST. The seat
# label is documentation only (a weekday body, or "dual"/"ninth" for the
# two seats that live in their own tables); the lookup below keys on the
# canonical stem, so one mechanism serves the weekday bodies, the Sunday
# Servant and the Ninth alike.
#
# DECLARED ORDER IS THE ROTATION ORDER, and that is load-bearing for the
# Power cast: its Throne, Mirror and Ninth each hold exactly two members,
# so the shared date modulo lands on the same index for all three on any
# given day (the sheet's "SYNCHRONIZED PAIR ROTATION" — no special-case
# code, a consequence of equal roster lengths). Alphabetical resolution
# would have paired Saburo with Rache instead of with Alt; declared order
# keeps the two empires standing together.
WEEKDAY_SEAT_ROSTERS: dict[str, dict[str, tuple[str, ...]]] = {
    "cp_gangs": {
        "moon": ("Aldecaldos", "Mox"),
        "mars": ("Maelstrom", "Barghest", "Wraiths"),
        "mercury": ("Voodoo_Boys", "6th_Street"),
        "saturn": ("Animals", "Scavengers"),
    },
    "cp_street": {
        "mars": ("Jackie", "Panam", "River"),
        "mercury": ("Wakako", "Padre"),
        "venus": ("Kerry", "Lizzy_Wizzy"),
    },
    "cp_corpo": {
        "sun": ("Saburo_Arasaka", "Rosalind_Myers"),
        "dual": ("Yorinobu", "Kurt_Hansen"),
        "ninth": ("Alt_Cunningham", "Rache_Bartmoss"),
    },
    # COMPLETION WAVE III (Session 33, 2026-07-29). The Star Wars Dyad's
    # rotating PEOPLE seats — Tuesday and Wednesday, ordinary two-way
    # pairs.
    #
    # THE NINTH'S MECHANISM IS RESOLVED (owner verdict 2026-07-29,
    # SEALED, superseding Session 33's PROVISIONAL date rotation): the
    # Ninth is a DAYLIGHT/NIGHT switch, not a seat roster — "the duality
    # of that theme pulling the actors to one of two sides." Day shows
    # The Ghosts (`constants.WEEKDAY_THEME_NINTHS["sw_dyad"]`, the
    # canonical/good face), night shows Exegol
    # (`constants.WEEKDAY_THEME_NINTH_NIGHT`) — dispatched through
    # `constants.NINTH_MECHANISMS["sw_dyad"] == "daynight"` by
    # `render.ninths.theme_ninth`/`ninth_alt_active` and `render.
    # compositor._center_ninth_alt`, reading the SAME `TickState.
    # is_daylight` `center_face` already reads. The "ninth" entry that
    # used to live here is GONE — see `research/theme_staging.md` for
    # the closed provisional note.
    "sw_dyad": {
        "mars": ("Finn", "Phasma"),
        "mercury": ("Maz", "DJ"),
    },
}
# (theme FOLDER, canonical stem) -> the whole roster (derived; the one
# lookup `rotating_art_file` performs). Keyed on the folder as well as
# the stem so a roster can never capture a same-named plate in another
# theme.
_SEAT_ROSTER_BY_PLATE = {
    (theme, stems[0]): stems
    for theme, seats in WEEKDAY_SEAT_ROSTERS.items()
    for stems in seats.values()
}


def _seat_roster_of(canonical_path: Path) -> tuple[str, ...] | None:
    """The roster `canonical_path` is the canonical member of, or None
    for every other asset in the program. Weekday plates live at
    `<theme>/<register>/<look>/<Stem>.png`, so the theme folder is the
    third parent — the same shape for bronze and for its colored
    sibling."""
    parts = canonical_path.parts
    if len(parts) < 4:
        return None
    return _SEAT_ROSTER_BY_PLATE.get((parts[-4], canonical_path.stem))


def _roster_candidates(directory: Path, stems: tuple[str, ...]) -> list[Path]:
    """A seat roster's plates, in the roster's DECLARED order, resolved
    to the active art source. A member with nothing on disk is skipped
    rather than raising — the seat then simply rotates through fewer
    figures, which is the same graceful-absent contract every other art
    table here keeps (Rule #1's documented path)."""
    resolved: list[Path] = []
    for stem in stems:
        picked = paths.art_file(directory / f"{stem}.png")
        if picked is not None and picked.exists():
            resolved.append(picked)
    return resolved


def rotating_art_file(canonical_path: Path, on_date: date) -> Path | None:
    """ONE asset from a rotating family, THE UNIVERSAL CONVENTION applied
    generically: `canonical_path` is a SOURCELESS `<dir>/<Name>.png`
    (exactly like every config path-table entry). The pool is the
    directory's own `<Name>` / `<Name>_v*` version siblings, resolved to
    the active art source by `paths.art_file` (RESTRUCTURE 2026-07-22
    retired the `alt/` subfolder — versions are `_v2`-style siblings in
    the SAME source-free folder now) — or, when the plate is the
    canonical member of a SEAT ROSTER above, that roster's own figures in
    declared order — normally by `_pick_rotation`'s daily modulo, except
    cp_corpo's own roster, which reads the ISO week's parity instead
    (`_pick_weekly_mandate`, `constants.NINTH_MECHANISMS["cp_corpo"] ==
    "term_weekly"` — THE WEEKLY MANDATE, owner decree 2026-07-29): ONE
    rotation chokepoint, a per-theme CADENCE rather than a second
    mechanism (Rule #5). Opt-in per consumer (scale duality, era
    emblems, tetramorph figures, every weekday body) — never on the hot
    `art_file` path. This is the ONE chokepoint every weekday consumer
    already calls, which is why the roster hooks in here rather than at
    four call sites. None when the canonical path resolves to nothing on
    disk (not even a master)."""
    resolved = paths.art_file(canonical_path)
    if resolved is None or not resolved.exists():
        return None
    stems = _seat_roster_of(canonical_path)
    if stems is not None:
        theme = canonical_path.parts[-4]
        picker = (
            _pick_weekly_mandate
            if constants.NINTH_MECHANISMS.get(theme) == "term_weekly"
            else _pick_rotation
        )
        return picker(_roster_candidates(canonical_path.parent, stems), on_date)
    candidates = _rotation_candidates(
        (canonical_path.parent,), (canonical_path.stem,)
    )
    return _pick_rotation(candidates, on_date)


# The Judas–Lucifer scale badges (owner 2026-07-13): the two triangle
# medallions illustrating "The Two Triangles" — wired before the art
# lands; the Encyclopedia hides missing files.
SCALE_ART_DIR = paths.assets_dir() / "archetypes" / "scale"
# SCALE ROTATION (owner decree 2026-07-19, CANON.md one-image-one-place
# amendment — "koje cemo koristiti na smenu"): Judas-Lucifer is a MAIN
# theme, every being living between excessive self-criticism and
# excessive self-love, so BOTH poles keep MULTIPLE generated versions
# instead of freezing on one master — the FIRST family the universal
# rotation convention above was generalized FROM (2026-07-20).
# The old naming-zoo tolerance ("_Triangle" masters beside a lowercase
# refresh batch) died in the RESTRUCTURE figure-first sweep
# (2026-07-22): every file now carries the plain figure stem
# (`Judas[_vN]_<src>`, `Lucifer[_vN]_<src>`), so the pool is the one
# universal `<stem>` / `<stem>_v*` search. `glass/` stays a second
# STYLE register (a parallel batch of the same two figures), pooled in.


def scale_variant_file(figure: str, on_date: date) -> Path | None:
    """One Scale badge file for `figure` ("Judas"/"Lucifer") on
    `on_date` — DISCOVERS what actually exists on disk for the ACTIVE
    art source at call time (`_rotation_candidates` against
    SCALE_ART_DIR AND its `glass/` register — the metal cameo and the
    stained-glass windows are two parallel batches of the SAME two
    figures), picked by the SHARED `_pick_rotation` — the SAME date
    always yields the SAME file, consecutive dates advance through the
    set, and Lucifer/Judas called with the SAME date stay IN STEP (one
    index driving two independent counts, since both figures' counts
    move together as art lands). Deep travel: the caller passes the
    TRAVELED date, consistent with the poles' light/dark glyph law
    (`controller._effective_travel_date`)."""
    root = paths.art_file(SCALE_ART_DIR)
    # Tree law 2026-07-26: the cameo batch lives at primary/colored/,
    # the stained-glass batch at glass/colored/ — the two look homes of
    # the same two figures.
    candidates = _rotation_candidates(
        (root / "primary" / "colored", root / "glass" / "colored"),
        (figure,),
    )
    return _pick_rotation(candidates, on_date)


INSTRUMENT_ART_DIR = paths.assets_dir() / "instrument"



def weekday_art(rel) -> Path:
    """Absolute path for a weekday theme-relative art path. The first
    segment names the theme FOLDER; `config.taxonomy` fixes its group,
    so 'greek/primary/Helios.png' -> assets/weeks/myth/greek/primary/...
    The Inner-Wheel and Continents step-ups ('../emblem/...',
    '../earth/...') resolve to their own relocated roots (RESTRUCTURE
    2026-07-22). The suffix-less path is returned; `paths.art_file`
    appends the active source suffix at the disk boundary."""
    from config import taxonomy

    parts = Path(rel).parts
    if parts and parts[0] == "..":
        family = parts[1]
        if family == "emblem":
            return taxonomy.inner_wheel_dir().joinpath(*parts[2:])
        if family == "earth":
            return continents.EARTH_ART_DIR.joinpath(*parts[2:])
    return taxonomy.weeks_dir(parts[0]).joinpath(*parts[1:])


# --- Weekday body themes (SYMBOLISM.md canon) -----------------------------------
# Display names per theme, body -> name (the weekday hover reads
# "Wednesday, Odin" in the norse theme). "planets" keeps the skin's own
# unit untouched. Saturday has no Norse god — the Sabbath stands in
# (canon). Art: assets/weekday/<theme>/<Entity>.png (files carry the
# ENTITY names; the two Norse diacritics fold to ASCII on disk).
WEEKDAY_THEME_NAMES = {
    # The owner's planet GLYPHS (☿ ♃ …) — same entities as "planets",
    # body-named files, planet display names.
    "planet_signs": {
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
    },
    # Display names carry the NATIVE script (owner 2026-07-12: "da
    # koristimo ta slova" — like the Japanese kanji and the Slavic
    # diacritics); the files keep plain ASCII stems via the explicit
    # overrides below.
    "greek": {
        "sun": "Helios (Ἥλιος)",
        "moon": "Selene (Σελήνη)",
        "mars": "Ares (Ἄρης)",
        "mercury": "Hermes (Ἑρμῆς)",
        "jupiter": "Zeus (Ζεύς)",
        "venus": "Aphrodite (Ἀφροδίτη)",
        "saturn": "Cronus (Κρόνος)",
    },
    "norse": {
        "sun": "Sól",
        "moon": "Máni",
        "mars": "Tyr (Týr)",
        "mercury": "Odin (Óðinn)",
        "jupiter": "Thor (Þórr)",
        "venus": "Freya (Freyja)",
        "saturn": "Loki",     # owner decision (FINAL.txt #2): Loki stands
                              # on Saturday — the bound trickster as
                              # Cronus' northern mirror
    },
    # Egyptian gods (owner art 2026-07-11, per the approved mapping):
    # Ra's Sunday, Khonsu the moon-walker, Montu the war falcon, Thoth
    # the scribe on the messenger's day, Amun the king of gods, Hathor
    # love and beauty, Osiris — harvest, patience and rebirth on
    # Saturn's day.
    "egypt": {
        "sun": "Ra",
        "moon": "Khonsu",
        "mars": "Montu",
        "mercury": "Thoth",
        "jupiter": "Amun",
        "venus": "Hathor",
        "saturn": "Osiris",
    },
    # Slavic gods (owner art 2026-07-12, per the approved mapping):
    # Dažbog the giving sun, Hors the night-walker, Svetovid's four
    # faces and white war-horse on Tuesday, Veles the horned trader-
    # trickster mirroring Odin and Hermes, Perun's oak and thunder at
    # noon, Mokoš spinning on the day her cult kept as Friday, Morana
    # — winter drowned each spring — on the arm of Renewal.
    "slavic": {
        "sun": "Dažbog",
        "moon": "Hors",
        "mars": "Svetovid",
        "mercury": "Veles",
        "jupiter": "Perun",
        "venus": "Mokoš",
        "saturn": "Morana",
    },
    # The seven metals of alchemy (owner art 2026-07-12): the classical
    # planet-metal correspondence — every medallion the same still life
    # of bars, nuggets and coiled wire, each wearing its own metal.
    "alchemy": {
        "sun": "Gold",
        "moon": "Silver",
        "mars": "Iron",
        "mercury": "Quicksilver",
        "jupiter": "Tin",
        "venus": "Copper",
        "saturn": "Lead",
    },
    # The Japanese week (owner art 2026-07-12, Gemini from our prompts):
    # the yōbi day names ARE the planetary week — sun, moon, then the
    # five Wu Xing element stars (fire=Mars, water=Mercury, wood=
    # Jupiter, metal=Venus, earth=Saturn). Display names KEEP the
    # kanji (owner instruction); files are folded ASCII overrides.
    "japan": {
        "sun": "Nichiyōbi (日曜日)",
        "moon": "Getsuyōbi (月曜日)",
        "mars": "Kayōbi (火曜日)",
        "mercury": "Suiyōbi (水曜日)",
        "jupiter": "Mokuyōbi (木曜日)",
        "venus": "Kin'yōbi (金曜日)",
        "saturn": "Doyōbi (土曜日)",
    },
    # NARRATIVE-FIRST remap (owner decision 2026-07-12): each religion
    # sits on the day its OWN canon points to, not its rest day —
    # Freemasonry's quest for Light under the All-Seeing Eye takes the
    # Sun (its Sunday DOUBLE = the rough vs the perfect ashlar);
    # Islam's calendar IS the moon (Quran 2:189); Buddhism wins the
    # war-day without weapons (Mara, Dhammapada 103); Christianity's
    # forgiving love lands on Venus's Friday (Good Friday, agape).
    "religion": {
        "sun": "Christianity",       # owner: replaces Zoroastrianism in
                                    # the basic seven (now an alternate)
        "moon": "Islam",
        "mars": "Buddhism",
        "mercury": "Taoism",
        "jupiter": "Hinduism",
        "venus": "Sikhism",
        "saturn": "Judaism",
    },
    # The ALTERNATE religion set — each on the day it fits best (canon
    # in SYMBOLISM.md; Egypt and Babylon per the owner's 2026-07-10 art:
    # Ra's Sunday, Ishtar IS Venus and Babylon invented the 7-day week).
    "religion_alt": {
        "sun": "Mithraism",     # owner decision 2026-07-12: replaces Egypt
                                # (a duplicate once the Egyptian gods became
                                # a full theme) — Sol Invictus IS dies Solis
        "moon": "Druidism",
        "mars": "Zoroastrianism",
        "mercury": "Shamanism",
        "jupiter": "Eleusinian Mysteries",
        "venus": "Babylon",
        "saturn": "Voodoo",
    },
    "profession": {
        "sun": "Ruler · Servant",   # the yin-yang center (owner spec
                                    # 2026-07-12): one figure, two faces
        "moon": "Physician",
        "mars": "Soldier",
        "mercury": "Merchant",
        "jupiter": "Priest",
        "venus": "Artist",
        "saturn": "Farmer",
    },
    # THE ANIMAL SOCIETIES (owner 2026-07-13) — three orders of order:
    # the pack ranks, the hive works by age (the career IS the clock),
    # the herd remembers (the leader is the one who holds the map).
    "wolf": {
        "sun": "Leader (Alpha) · Omega",     # the first and the last of the pack
                                    # — M at noon, Ω at midnight
        "moon": "Luna",
        "mars": "Hunter (Gamma)",
        "mercury": "Scout (Delta)",
        "jupiter": "Beta",
        "venus": "Mate",
        "saturn": "Elder",
    },
    "bee": {
        "sun": "Queen · Cleaner",   # the mother of the hive and the
                                    # day-one daughter at her birth cell
        "moon": "Nurse",
        "mars": "Guard",
        "mercury": "Scout",
        "jupiter": "Builder",
        "venus": "Drone",
        "saturn": "Forager",
    },
    "elephant": {
        "sun": "Matriarch · Memory",  # the ruler and the REMEMBERED
                                      # ruler — the bones that taught her
        "moon": "Allomother",
        "mars": "Musth",
        "mercury": "Caller",
        "jupiter": "Mentor",
        "venus": "Reunion",
        "saturn": "Elder",
    },
    # The SCRIPTURE family (owner 2026-07-14): three stained-glass sets.
    "bible": {
        "sun": "Ancient of Days · Son",
        "moon": "Mary",
        "mars": "David",
        "mercury": "Moses",
        "jupiter": "Solomon",
        "venus": "Adam & Eve",
        "saturn": "Joseph",
    },
    "bible2": {
        "sun": "Abraham · Isaac",
        "moon": "Jonah",
        "mars": "Samson",
        "mercury": "Jacob",
        "jupiter": "Noah",
        "venus": "Ruth",
        "saturn": "Job",
    },
    "bible_dark": {
        "sun": "Lucifer · Judas",
        "moon": "Lilith",
        "mars": "Goliath",
        "mercury": "The Serpent",
        "jupiter": "Herod",
        "venus": "Delilah",
        "saturn": "Cain",
    },
    # The DEEP SKY (owner 2026-07-14): star-chart medallions.
    "cosmos": {
        "sun": "Sun · Black Hole",
        "moon": "Nebula",
        "mars": "Supernova",
        "mercury": "Pulsar",
        "jupiter": "Galaxy",
        "venus": "Binary Stars",
        "saturn": "Comet",
    },
    # The Planets MEDALLION look — same entities, bronze art.
    "planets_art": {
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
    },
    # THE INNER WHEEL on the dial (owner 2026-07-14): the days ARE
    # their virtues / vices / hour-moods.
    "virtues": {
        "sun": "Justice · Humility",
        "moon": "Serenity",
        "mars": "Courage",
        "mercury": "Wisdom",
        "jupiter": "Generosity",
        "venus": "Love",
        "saturn": "Patience",
    },
    "sins": {
        "sun": "Pride · Servility",
        "moon": "Fear",
        "mars": "Wrath",
        "mercury": "Greed",
        "jupiter": "Excess",
        "venus": "Jealousy",
        "saturn": "Envy",
    },
    "moods": {
        "sun": "Glory · Awe",
        "moon": "Calm",
        "mars": "Zeal",
        "mercury": "Sorrow",
        "jupiter": "Joy",
        "venus": "Passion",
        "saturn": "Renewal",
    },
    # COMPLETION WAVE I (Session 31, 2026-07-29). Three casts sealed in
    # their own prompt sheets long before the wiring: the Olympians'
    # bestiary seated by the VICE of each arm rather than the virtue
    # (research/prompts/monsters/), the Chinese court drawn from folk
    # myth, the Three Kingdoms and Journey to the West
    # (research/prompts/chinese/), and the executive committee — the one
    # cast in the book whose members are OFFICES rather than persons
    # (research/prompts/corporate/).
    "age_of_heroes": {
        "sun": "Nemean Lion · Cerberus",
        "moon": "Medusa",
        "mars": "Minotaur",
        "mercury": "Sphinx",
        "jupiter": "Erymanthian Boar",
        "venus": "Sirens",
        "saturn": "Hydra",
    },
    "celestial_court": {
        "sun": "Sun Wukong · Six-Eared Macaque",
        "moon": "Chang'e",
        "mars": "Erlang Shen",
        "mercury": "Guan Yu",
        "jupiter": "Zhu Bajie",
        "venus": "Zhinü",
        "saturn": "Shennong",
    },
    "corporate": {
        "sun": "CEO · Chairman",
        "moon": "CHRO",
        "mars": "COO",
        "mercury": "CFO",
        "jupiter": "CMO",
        "venus": "CDO",
        "saturn": "CTO",
    },
    # COMPLETION WAVE II (Session 32, 2026-07-29). The three World of
    # Warcraft casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/wow/wow_prompts.md: the SAME nine seats held three
    # times over, with the arm bundle fixed and only the person changing
    # (CUBE.md Charter rule 5 — three different people holding one
    # office, never one character read three ways). The Alliance and the
    # Horde are seated by the arm's VIRTUE, the Evil cast by the VICE
    # that virtue is named against.
    "wow_alliance": {
        "sun": "Varian Wrynn · Genn Greymane",
        "moon": "Anduin",
        "mars": "Muradin Bronzebeard",
        "mercury": "Khadgar",
        "jupiter": "Uther the Lightbringer",
        "venus": "Jaina",
        "saturn": "Malfurion",
    },
    "wow_horde": {
        "sun": "Thrall · Garrosh",
        "moon": "Baine",
        "mars": "Grommash Hellscream",
        "mercury": "Gallywix",
        "jupiter": "Vol'jin",
        "venus": "Draka",
        "saturn": "Cairne",
    },
    "wow_evil": {
        "sun": "Arthas · Illidan",
        "moon": "Kel'Thuzad",
        "mars": "Mannoroth",
        "mercury": "Gul'dan",
        "jupiter": "Kil'jaeden the Deceiver",
        "venus": "Sylvanas",
        "saturn": "Deathwing",
    },
    # COMPLETION WAVE II, second half (Session 32, 2026-07-29). The
    # three Cyberpunk 2077 casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/cyberpunk/cyberpunk_prompts.md.
    #
    # THE ROSTER SEATS' DISPLAY LAW: where a seat holds several figures
    # (`WEEKDAY_SEAT_ROSTERS` below) the display name lists them all,
    # separated by the same "·" the Sunday dual already uses. The art
    # rotates daily and the label does not, so a per-figure label would
    # go stale the moment the plate turned; a label naming the WHOLE
    # roster is true on every day of it, and the seat's article argues
    # every member. SUNDAY is the one exception and keeps the
    # Ruler · Servant law every other theme obeys — its rotating
    # partners are named in the two face texts instead.
    "cp_gangs": {
        "sun": "Arasaka · Militech",
        "moon": "Aldecaldos · Mox",
        "mars": "Maelstrom · Barghest · Wraiths",
        "mercury": "Voodoo Boys · 6th Street",
        "jupiter": "Tyger Claws",
        "venus": "Valentinos",
        "saturn": "Animals · Scavengers",
    },
    "cp_street": {
        "sun": "Johnny Silverhand · Rogue",
        "moon": "Viktor Vektor",
        "mars": "Jackie · Panam · River",
        "mercury": "Wakako · Padre",
        "jupiter": "Misty",
        "venus": "Kerry · Lizzy Wizzy",
        "saturn": "Judy",
    },
    "cp_corpo": {
        "sun": "Saburo Arasaka · Yorinobu",
        "moon": "Songbird",
        "mars": "Adam Smasher",
        "mercury": "Dexter DeShawn",
        "jupiter": "Solomon Reed",
        "venus": "Evelyn Parker",
        "saturn": "Takemura",
    },
    # COMPLETION WAVE III (Session 33, 2026-07-29). The three Star Wars
    # casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/starwars/starwars_prompts.md. The same nine seats
    # a third time, and the wave where the repeat rule is most visible:
    # Anakin holds the Sith Mirror and the Jedi Mirror, Leia the Jedi
    # Tuesday and the Dyad Thursday, Han the Jedi Wednesday and the Dyad
    # Friday — three people at two ages each, six seats, six independent
    # arguments (CUBE.md Charter rule 5). The Dyad's Tuesday and
    # Wednesday follow the ROSTER SEATS' DISPLAY LAW stated above: the
    # label names every member because the plate turns and the label
    # does not.
    "sw_jedi": {
        "sun": "Young Luke · Vader",
        "moon": "Obi-Wan Kenobi",
        "mars": "General Leia Organa",
        "mercury": "Han Solo",
        "jupiter": "Qui-Gon Jinn",
        "venus": "Padmé Amidala",
        "saturn": "Chewbacca",
    },
    "sw_sith": {
        "sun": "Palpatine · Anakin",
        "moon": "Grand Moff Tarkin",
        "mars": "General Grievous",
        "mercury": "Jabba the Hutt",
        "jupiter": "Count Dooku",
        "venus": "Maul",
        "saturn": "Boba Fett",
    },
    "sw_dyad": {
        "sun": "Rey · Kylo Ren",
        "moon": "Rose Tico",
        "mars": "Finn · Phasma",
        "mercury": "Maz Kanata · DJ",
        "jupiter": "Old Leia",
        "venus": "Old Han",
        "saturn": "General Hux",
    },
}
# THE CONTINENTS (owner-sealed matrix 2026-07-21): the six weekday
# columns are the six continents; Sunday's body is Antarctica, the
# Ruler face of the polar dual (the Arctic Servant lives in
# WEEKDAY_DUAL_NAMES). Added after the literal so the FILES auto-build
# below still folds every OTHER theme's names; the continents file
# stems are the earth faces, overridden explicitly (like greek/norse).
WEEKDAY_THEME_NAMES["continents"] = {
    "sun": "Antarctica",
    "moon": "Oceania",
    "mars": "Europe",
    "mercury": "Asia",
    "jupiter": "Africa",
    "venus": "South America",
    "saturn": "North America",
}

# File stems on disk: the display names folded to ASCII (Sól -> Sol,
# Dažbog -> Dazbog) and PASCAL-CASED per token (tree law rule 5, the
# case half, owner-approved 2026-07-26: every stem reads as a NAME —
# Afu_Ra, Big_Bang — never a lowercase file token). The themes below
# historically shipped lowercase stems; their names are NORMALIZED
# (lowered, then Pascal-cased) so display-name capitals like "McX"
# can never drift the stem from what the disk rename produced.
_ASCII_FOLD = str.maketrans("óážš", "oazs")
_LOWERCASE_THEMES = (
    "religion", "religion_alt", "planet_signs", "egypt", "slavic", "alchemy",
    "wolf",
)


def _pascal_stem(stem: str) -> str:
    """Tree-law stem casing: capitalize each underscore token unless it
    already carries a capital of its own (Yggdrasil, KaliYuga stay as
    drawn) — the SAME rule research/pascalcase_stems.py renamed the
    disk with, so config and files can never disagree."""
    return "_".join(
        t if any(c.isupper() for c in t) else (t[:1].upper() + t[1:])
        for t in stem.split("_")
    )
# Theme -> art folder under assets/weeks/<group>/: THE TREE LAW
# (owner-approved 2026-07-26) — every theme dir is
# <theme>/<register>/<look>: related themes share a theme folder via
# registers (creeds = primary Creeds + secondary Mysteries; bible =
# primary/secondary/dark; planets = ONE primary register whose looks
# are photo/sign/art), and a register's colored arc is its own CHILD
# <register>/colored — identical at every level, pantheon and primary
# alike (the owner's decree; the old sibling-<family>/colored shape is
# dead). The DUAL FLATTEN law (owner 2026-07-19) still holds: every
# file, dual included, sits FLAT inside its look — WHO a file is lives
# only in WEEKDAY_DUAL_FILES/WEEKDAY_PANTHEON, never in a folder name.
# Cameo-master sets carry bronze/ (gold/silver derive by algorithm);
# as-drawn full-color sets carry colored/ as their single look.
WEEKDAY_THEME_DIRS = {
    "planet_signs": "planets/primary/sign",
    "greek": "greek/primary/bronze",
    "norse": "norse/primary/bronze",
    "egypt": "egypt/primary/bronze",
    "slavic": "slavic/primary/bronze",
    "alchemy": "alchemy/primary/colored",
    "japan": "japan/primary/colored",
    "religion": "creeds/primary/colored",
    "religion_alt": "creeds/secondary/colored",
    "profession": "profession/primary/bronze",
    "wolf": "wolf/primary/bronze",
    "bee": "bee/primary/bronze",
    "elephant": "elephant/primary/bronze",
    "bible": "bible/primary/colored",
    "bible2": "bible/secondary/colored",
    "bible_dark": "bible/dark/colored",
    "cosmos": "cosmos/primary/bronze",
    "planets_art": "planets/primary/art",
    # Completion wave I (Session 31): bronze primary registers with a
    # colored/ sibling apiece — the standard cameo-master shape.
    "age_of_heroes": "age_of_heroes/primary/bronze",
    "celestial_court": "celestial_court/primary/bronze",
    "corporate": "corporate/primary/bronze",
    # Completion wave II (Session 32): the same shape again — a carved
    # bronze relief master per cast with its full-paint colored/ sibling.
    "wow_alliance": "wow_alliance/primary/bronze",
    "wow_horde": "wow_horde/primary/bronze",
    "wow_evil": "wow_evil/primary/bronze",
    # Completion wave II, Cyberpunk half (Session 32): the same shape a
    # third time — one aged-bronze relief master per cast with its
    # neon-noir colored/ sibling. Every roster member's plate lives FLAT
    # in the same look dir beside the canonical one (the sheet's own
    # figure-first naming: a file is named after the figure it depicts,
    # never after the seat).
    "cp_gangs": "cp_gangs/primary/bronze",
    "cp_street": "cp_street/primary/bronze",
    "cp_corpo": "cp_corpo/primary/bronze",
    # Completion wave III (Session 33): the same shape a fourth time —
    # one aged-bronze relief master per cast with its full-paint colored/
    # sibling. The Dyad's roster members live FLAT in the same look dir
    # beside the canonical plate, the sheet's own figure-first naming
    # (the sheet's prose still describes the retired `alt/` subfolder;
    # its DROP PATHS already write Phasma, DJ and Exegol as siblings,
    # which is the shape wired here).
    "sw_jedi": "sw_jedi/primary/bronze",
    "sw_sith": "sw_sith/primary/bronze",
    "sw_dyad": "sw_dyad/primary/bronze",
    # The emblem families live OUTSIDE assets/weekday/ — the relative
    # step-up reaches assets/emblem/ (owner 2026-07-14).
    "virtues": "../emblem/virtue/primary/colored",
    "sins": "../emblem/sin/primary/colored",
    "moods": "../emblem/mood/primary/colored",
    # THE CONTINENTS reuse the dial's OWN Earth faces (assets/earth/,
    # owner exception 2026-07-21) — the relative step-up reaches them,
    # exactly like the emblem families reach assets/emblem/. The stems
    # (overridden below) are the earth_{style}_{region}_{phase} faces.
    "continents": "../earth",
}
WEEKDAY_THEME_FILES = {
    theme: {
        body: _pascal_stem(
            name.translate(_ASCII_FOLD).lower()
            if theme in _LOWERCASE_THEMES
            else name.translate(_ASCII_FOLD)
        )
        for body, name in names.items()
    }
    for theme, names in WEEKDAY_THEME_NAMES.items()
}
# The dual center shows both faces in the hover title, but the owner's
# medallion file keeps the single name.
WEEKDAY_THEME_FILES["profession"]["sun"] = "Ruler"
WEEKDAY_THEME_FILES["wolf"]["sun"] = "Alpha"
WEEKDAY_THEME_FILES["bee"]["sun"] = "Queen"
WEEKDAY_THEME_FILES["elephant"]["sun"] = "Matriarch"
# The Corporation's six weekday stems ARE its display names (the
# acronyms already carry their own capitals, so the Pascal rule leaves
# them alone) — only the dual Sunday title needs the single-name file.
WEEKDAY_THEME_FILES["corporate"]["sun"] = "CEO"
# The metal reads Quicksilver, the owner's file keeps the element name.
WEEKDAY_THEME_FILES["alchemy"]["mercury"] = "Mercury"
# The reworked Creeds and the wolf rank parentheticals keep plain stems.
WEEKDAY_THEME_FILES["religion_alt"]["jupiter"] = "Eleusis"
WEEKDAY_THEME_FILES["wolf"]["mars"] = "Hunter"
WEEKDAY_THEME_FILES["wolf"]["mercury"] = "Scout"
# The Greek and Norse display names carry native-script parentheticals
# now — the files stay on the plain ASCII stems.
WEEKDAY_THEME_FILES["greek"] = {
    "sun": "Helios", "moon": "Selene", "mars": "Ares",
    "mercury": "Hermes", "jupiter": "Zeus", "venus": "Aphrodite",
    "saturn": "Cronus",
}
WEEKDAY_THEME_FILES["norse"] = {
    "sun": "Sol", "moon": "Mani", "mars": "Tyr",
    "mercury": "Odin", "jupiter": "Thor", "venus": "Freya",
    "saturn": "Loki",
}
# The Japanese display names carry kanji — the files are the romaji
# day names folded to plain ASCII (macrons and the apostrophe dropped).
WEEKDAY_THEME_FILES["japan"] = {
    "sun": "Nichiyobi",
    "moon": "Getsuyobi",
    "mars": "Kayobi",
    "mercury": "Suiyobi",
    "jupiter": "Mokuyobi",
    "venus": "Kinyobi",
    "saturn": "Doyobi",
}
# The text-wave themes (owner 2026-07-14): explicit stems — the
# display names carry duals ("·") and compounds ("Adam & Eve");
# PascalCase per the tree law's stem casing (rule 5, 2026-07-26).
WEEKDAY_THEME_FILES["bible"] = {
    "sun": "Ancient_Of_Days", "moon": "Mary", "mars": "David",
    "mercury": "Moses", "jupiter": "Solomon", "venus": "Adam_And_Eve",
    "saturn": "Joseph",
}
WEEKDAY_THEME_FILES["bible2"] = {
    "sun": "Abraham", "moon": "Jonah", "mars": "Samson",
    "mercury": "Jacob", "jupiter": "Noah", "venus": "Ruth",
    "saturn": "Job",
}
WEEKDAY_THEME_FILES["bible_dark"] = {
    "sun": "Lucifer", "moon": "Lilith", "mars": "Goliath",
    "mercury": "Serpent", "jupiter": "Herod", "venus": "Delilah",
    "saturn": "Cain",
}
WEEKDAY_THEME_FILES["cosmos"] = {
    "sun": "Sun", "moon": "Nebula", "mars": "Supernova",
    "mercury": "Pulsar", "jupiter": "Galaxy", "venus": "Binary_Stars",
    "saturn": "Comet",
}
WEEKDAY_THEME_FILES["planets_art"] = {
    "sun": "Sun", "moon": "Moon", "mars": "Mars",
    "mercury": "Mercury", "jupiter": "Jupiter", "venus": "Venus",
    "saturn": "Saturn",
}
# Completion wave I (Session 31): explicit stems — the display names
# carry duals ("·"), spaces (Erymanthian Boar, Sun Wukong) and a
# diacritic (Zhinü) that the ASCII fold does not know.
WEEKDAY_THEME_FILES["age_of_heroes"] = {
    "sun": "Nemean_Lion", "moon": "Medusa", "mars": "Minotaur",
    "mercury": "Sphinx", "jupiter": "Erymanthian_Boar", "venus": "Sirens",
    "saturn": "Hydra",
}
WEEKDAY_THEME_FILES["celestial_court"] = {
    "sun": "Sun_Wukong", "moon": "ChangE", "mars": "Erlang_Shen",
    "mercury": "Guan_Yu", "jupiter": "Zhu_Bajie", "venus": "Zhinu",
    "saturn": "Shennong",
}
# Completion wave II (Session 32): explicit stems for all three WoW
# casts — the display names carry the Sunday dual ("·"), epithets
# (the Lightbringer, the Deceiver), surnames the file drops, and the
# apostrophes of Vol'jin, Kel'Thuzad, Gul'dan and Kil'jaeden that the
# ASCII fold does not know. The stems are the sheet's own drop paths.
WEEKDAY_THEME_FILES["wow_alliance"] = {
    "sun": "Varian", "moon": "Anduin", "mars": "Muradin",
    "mercury": "Khadgar", "jupiter": "Uther", "venus": "Jaina",
    "saturn": "Malfurion",
}
WEEKDAY_THEME_FILES["wow_horde"] = {
    "sun": "Thrall", "moon": "Baine", "mars": "Grommash",
    "mercury": "Gallywix", "jupiter": "Voljin", "venus": "Draka",
    "saturn": "Cairne",
}
WEEKDAY_THEME_FILES["wow_evil"] = {
    "sun": "Arthas", "moon": "Kel_Thuzad", "mars": "Mannoroth",
    "mercury": "Guldan", "jupiter": "Kiljaeden", "venus": "Sylvanas",
    "saturn": "Deathwing",
}
# Completion wave II, Cyberpunk half (Session 32): the stems are the
# CANONICAL member of each seat — the first entry of the seat's roster
# below, and the only one the auto-build could never have guessed, since
# a roster seat's display name lists every member. The stems are the
# sheet's own drop paths.
WEEKDAY_THEME_FILES["cp_gangs"] = {
    "sun": "Arasaka", "moon": "Aldecaldos", "mars": "Maelstrom",
    "mercury": "Voodoo_Boys", "jupiter": "Tyger_Claws",
    "venus": "Valentinos", "saturn": "Animals",
}
WEEKDAY_THEME_FILES["cp_street"] = {
    "sun": "Johnny", "moon": "Viktor", "mars": "Jackie",
    "mercury": "Wakako", "jupiter": "Misty", "venus": "Kerry",
    "saturn": "Judy",
}
WEEKDAY_THEME_FILES["cp_corpo"] = {
    "sun": "Saburo_Arasaka", "moon": "Songbird", "mars": "Adam_Smasher",
    "mercury": "Dexter", "jupiter": "Solomon", "venus": "Evelyn",
    "saturn": "Takemura",
}
# Completion wave III (Session 33): explicit stems for all three Star
# Wars casts — the display names carry the Sunday dual ("·"), the roster
# seats' "·" lists, hyphens (Obi-Wan, Qui-Gon), an age qualifier the file
# drops (Old Leia, Old Han) and the acute of Padmé that the ASCII fold
# does not know. The stems are the sheet's own drop paths, with ONE
# correction: the sheet writes `BobaFett.png`, which breaks the tree
# law's word-separator rule (`tests/test_assets_structure.py`
# test_figure_stems_separate_their_words) — the lawful stem is
# `Boba_Fett`, and the sheet has been corrected to match rather than the
# rule bent to it.
WEEKDAY_THEME_FILES["sw_jedi"] = {
    "sun": "Luke", "moon": "Obi_Wan", "mars": "Leia",
    "mercury": "Han", "jupiter": "Qui_Gon", "venus": "Padme",
    "saturn": "Chewbacca",
}
WEEKDAY_THEME_FILES["sw_sith"] = {
    "sun": "Palpatine", "moon": "Tarkin", "mars": "Grievous",
    "mercury": "Jabba", "jupiter": "Dooku", "venus": "Maul",
    "saturn": "Boba_Fett",
}
WEEKDAY_THEME_FILES["sw_dyad"] = {
    "sun": "Rey", "moon": "Rose", "mars": "Finn",
    "mercury": "Maz", "jupiter": "Leia", "venus": "Han",
    "saturn": "Hux",
}
# The emblem stems ARE the single names (Capitalized) — only the dual
# sun display titles need the override.
WEEKDAY_THEME_FILES["virtues"] = {
    "sun": "Justice", "moon": "Serenity", "mars": "Courage",
    "mercury": "Wisdom", "jupiter": "Generosity", "venus": "Love",
    "saturn": "Patience",
}
WEEKDAY_THEME_FILES["sins"] = {
    "sun": "Pride", "moon": "Fear", "mars": "Wrath",
    "mercury": "Greed", "jupiter": "Excess", "venus": "Jealousy",
    "saturn": "Envy",
}
WEEKDAY_THEME_FILES["moods"] = {
    "sun": "Glory", "moon": "Calm", "mars": "Zeal",
    "mercury": "Sorrow", "jupiter": "Joy", "venus": "Passion",
    "saturn": "Renewal",
}
# THE CONTINENTS' file stems ARE the Earth faces (owner exception
# 2026-07-21): the atmosphere-lit day globe per region is the baked
# preview/fallback stem; the live dial overrides both style and phase
# at render (continents_body_art). Built straight from CONTINENTS_
# REGIONS so the mapping lives in exactly one place (Rule #5).
WEEKDAY_THEME_FILES["continents"] = {
    body: f"earth_{continents.CONTINENTS_PREVIEW_STYLE}_{region}_day"
    for body, region in continents.CONTINENTS_REGIONS.items()
}

# THE DUAL SUNDAY (owner 2026-07-12): every theme's center day has a
# SECOND face — the Servant to the Ruler. On the Compass and the
# Seasons both faces shine (Ruler north 12h, Servant south 24h — two
# persons, a union); the Trinity and the Prism keep ONE image (two
# persons in one body) with both faces in the hover. Paths are
# relative to WEEKDAY_ART_DIR without the extension; the metal themes'
# COLORED look inserts a colored/ folder before the file name (the
# profession Servant is a full eighth plate living beside the Ruler).
# The two FACE NAMES of each theme's Sunday (hover titles: the north
# face and the south face; the combined single-image legend keeps the
# theme's own dual display name).
WEEKDAY_DUAL_NAMES = {
    "planets": ("Sun", "Eclipsed Sun"),
    "planet_signs": ("Sun", "Eclipsed Sun"),
    "greek": ("Helios", "Phaethon"),
    "norse": ("Sól", "Skoll"),
    "egypt": ("Ra", "Afu-Ra"),
    "slavic": ("Young Dažbog", "Old Dažbog"),
    "alchemy": ("Gold", "Raw Ore"),
    "japan": ("Amaterasu", "Ama-no-Iwato"),
    "religion": ("Christianity", "Satanism"),
    "religion_alt": ("Mithraism", "Corax"),
    "profession": ("Ruler", "Servant"),
    "wolf": ("Alpha", "Omega"),
    "bee": ("Queen", "Cleaner"),
    "elephant": ("Matriarch", "Memory"),
    "bible": ("Ancient of Days", "Son"),
    "bible2": ("Abraham", "Isaac"),
    "bible_dark": ("Lucifer", "Judas"),
    "cosmos": ("Sun", "Black Hole"),
    "planets_art": ("Sun", "Eclipsed Sun"),
    "virtues": ("Justice", "Humility"),
    "sins": ("Pride", "Servility"),
    "moods": ("Glory", "Awe"),
    # THE POLAR DUAL (owner-sealed matrix 2026-07-21): ANTARCTICA the
    # Ruler — a true continent, real rock under the ice — and the ARCTIC
    # the Servant — walkable ice with no land beneath, reality and its
    # shadow. The two live in eternal antiphase (polar day on one is
    # polar night on the other): the Ruler/Servant solar-window law made
    # planetary.
    "continents": ("Antarctica", "Arctic"),
    # COMPLETION WAVE I (Session 31). Three duals of one house rather
    # than three oppositions: two literal brothers (both children of
    # Typhon and Echidna), a Sage and his perfect counterfeit, and the
    # two offices company law itself recommends be held apart.
    "age_of_heroes": ("Nemean Lion", "Cerberus"),
    "celestial_court": ("Sun Wukong", "The Six-Eared Macaque"),
    "corporate": ("CEO", "Chairman of the Board"),
    # COMPLETION WAVE II (Session 32). Three duals of one house rather
    # than three oppositions, exactly as the sheet argues them: two
    # kings of the same alliance, a Warchief and the successor he
    # appointed himself, and two men who made the identical bargain and
    # were answered differently for it.
    "wow_alliance": ("Varian Wrynn", "Genn Greymane"),
    "wow_horde": ("Thrall", "Garrosh Hellscream"),
    "wow_evil": ("Arthas, the Lich King", "Illidan Stormrage"),
    # COMPLETION WAVE II, Cyberpunk half (Session 32). Three duals of
    # one house rather than three oppositions, as the sheet argues them:
    # the two corporations that fought the Fourth Corporate War and were
    # left reflecting each other, a legend and the woman who refused the
    # job that made him one, and a founder against the son who strangled
    # him and then sat in the chair.
    "cp_gangs": ("Arasaka", "Militech"),
    "cp_street": ("Johnny Silverhand", "Rogue"),
    "cp_corpo": ("Saburo Arasaka", "Yorinobu"),
    # COMPLETION WAVE III (Session 33). Three duals of one house rather
    # than three oppositions, exactly as the sheet argues them: a son and
    # the father he refused to execute, a master and the apprentice he
    # assembled from a nine-year-old, and the one pair in the whole
    # instrument whose SOURCE material calls them a single power in two
    # bodies.
    "sw_jedi": ("Young Luke", "Vader, the Father"),
    "sw_sith": ("Palpatine", "Anakin"),
    "sw_dyad": ("Rey", "Kylo Ren"),
}
# Dual paths live FLAT inside the theme's look dir (owner DUAL
# FLATTEN 2026-07-19: the dual/ folder carried zero semantic weight at
# runtime — the config table already IS the identity, so the folder
# only added a navigation step); the colored dual is the same path
# with the LOOK segment (the last folder) swapped to colored/ —
# `colored_variant_rel` below is the ONE implementation of that swap
# (tree law 2026-07-26; the old "/primary/" string replace died with
# the sibling-colored shape).
WEEKDAY_DUAL_FILES = {
    "planets": "planets/primary/photo/Sun_Eclipse",
    "planet_signs": "planets/primary/sign/Sun_Eclipse",
    "greek": "greek/primary/bronze/Phaethon",
    "norse": "norse/primary/bronze/Skoll",
    "egypt": "egypt/primary/bronze/Afu_Ra",
    "slavic": "slavic/primary/bronze/Dazbog_Old",
    "alchemy": "alchemy/primary/colored/Ore",
    "japan": "japan/primary/colored/Ama_No_Iwato",
    "religion": "creeds/primary/colored/Satanism",
    "religion_alt": "creeds/secondary/colored/Corax",
    # profession's flat "Servant" stem collides with an already-flat,
    # unreferenced orphan file the owner has separately at
    # profession/primary/Servant.png (different art, different hash —
    # a true collision found flattening this round) — config-side
    # rename to "Servant_dual" resolves it without touching the
    # unrelated orphan (Rule #3: never delete without the owner's own
    # look).
    "profession": "profession/primary/bronze/Servant_Dual",
    "wolf": "wolf/primary/bronze/Omega",
    "bee": "bee/primary/bronze/Cleaner",
    "elephant": "elephant/primary/bronze/Memory",
    "bible": "bible/primary/colored/Son_Servant",
    "bible2": "bible/secondary/colored/Isaac",
    "bible_dark": "bible/dark/colored/Judas",
    "cosmos": "cosmos/primary/bronze/Black_Hole",
    "planets_art": "planets/primary/art/Sun_Eclipse",
    # Completion wave I (Session 31): the servant plate flat inside the
    # theme's own look dir, colored twin via colored_variant_rel.
    "age_of_heroes": "age_of_heroes/primary/bronze/Cerberus",
    "celestial_court": "celestial_court/primary/bronze/Six_Eared_Macaque",
    "corporate": "corporate/primary/bronze/Chairman",
    # Completion wave II (Session 32): the servant plate flat inside the
    # cast's own look dir, colored twin via colored_variant_rel.
    "wow_alliance": "wow_alliance/primary/bronze/Genn",
    "wow_horde": "wow_horde/primary/bronze/Garrosh",
    "wow_evil": "wow_evil/primary/bronze/Illidan",
    # Completion wave II, Cyberpunk half (Session 32): the servant plate
    # flat inside the cast's own look dir, colored twin via
    # colored_variant_rel. The Power cast's Mirror ROTATES (Yorinobu /
    # Kurt Hansen) in lockstep with its Throne and its Ninth.
    "cp_gangs": "cp_gangs/primary/bronze/Militech",
    "cp_street": "cp_street/primary/bronze/Rogue",
    "cp_corpo": "cp_corpo/primary/bronze/Yorinobu",
    # Completion wave III (Session 33): the servant plate flat inside the
    # cast's own look dir, colored twin via colored_variant_rel. None of
    # the three Mirrors ROTATES — the Dyad's rotating seats are Tuesday,
    # Wednesday and its Ninth, never its Sunday.
    "sw_jedi": "sw_jedi/primary/bronze/Vader",
    "sw_sith": "sw_sith/primary/bronze/Anakin",
    "sw_dyad": "sw_dyad/primary/bronze/Kylo",
    "virtues": "../emblem/virtue/primary/colored/Humility",
    "sins": "../emblem/sin/primary/colored/Servility",
    "moods": "../emblem/mood/primary/colored/Awe",
    # THE ARCTIC SERVANT (owner exception 2026-07-21): the north_pole
    # Earth face, the Antarctic Ruler's antiphase mirror — the atmo-day
    # still frame is the baked stem (the live dial overrides style/phase
    # via continents_dual_art). Reaches the earth family with the same
    # "../earth" step-up the emblem duals use.
    "continents":
        f"../earth/earth_{continents.CONTINENTS_PREVIEW_STYLE}_{continents.CONTINENTS_DUAL_REGION}_day",
}


def colored_variant_rel(rel: str) -> str:
    """`rel`'s colored twin — the LOOK segment (the last folder of a
    `<theme>/<register>/<look>/<stem>` relative path) swapped to
    `colored` (tree law 2026-07-26: colored is a CHILD of its register
    at every level). THE ONE implementation — the old
    `.replace("/primary/", "/colored/")` string swap lived in five
    places (encyclopedia, controller, build_roster ×2, and implicitly
    the sibling-dir arithmetic) and silently broke the moment the look
    level appeared."""
    head, _, stem = rel.rpartition("/")
    register, _, _look = head.rpartition("/")
    return f"{register}/colored/{stem}"


# THE TITLE PLATE. A theme's opening page and its week-duality title
# page had no image NAME at all — not a missing file, a missing name, so
# no prompt sheet could even say what to draw (Session 27 coverage law,
# owner 2026-07-28: "svaki clanak mora sliku").
#
# THE SEAT IS THE ONE THE PROJECT ALREADY USES:
# `<theme>/<register>/<look>/Title.png` — `Title` is the reserved stem
# the tree law names, and `research/prompts/titles/theme_title_prompts.md`
# has been writing briefs against exactly these paths since R8c
# (2026-07-21). A parallel `title/` register was tried first and thrown
# out the same day: it would have orphaned twenty-odd already-written
# prompts for the sake of a second convention saying the same thing.
#
# A MERGED theme's three blocks land in their own three registers, which
# is what a register is for: greek/primary, greek/pantheon, greek/wider;
# bible/primary, bible/secondary, bible/dark. The week-duality title is
# the SAME seat under the reserved stem `Duality`.
TITLE_PLATE_STEM = "Title"
DUALITY_PLATE_STEM = "Duality"

# THE TWO GENERIC PLATES (owner decree 2026-07-29). Two pages repeat
# across the whole book with the SAME meaning every time, so they are
# ONE shared image each, not one per theme:
#
#   * the week's DUALITY title page — "one seat, two faces, and a ninth
#     outside the circle". The owner struck the per-theme version down
#     for the reader's sake, not for cost: the two faces open the very
#     next two pages ("njihova slika se sve pojavljuje odmah na sledeće
#     dve strane"), so a title plate that draws them again spends
#     attention on a repeat. The generic plate carries the SHAPE of the
#     idea and no figure at all.
#   * the THIRTEENTH of any twelve-based set (Sol, Modrenik, and
#     whatever else earns a thirteenth) — "the count that does not
#     close".
#
# Both belong to no theme, so they cannot live in a theme's register
# (the tree law has no seat for "everyone's"); they are the
# instrument's own furniture, beside the section logo and the
# paint/light legend. Briefs: research/prompts/instrument/.
DUALITY_GENERIC_ART = INSTRUMENT_ART_DIR / "duality.png"
THIRTEENTH_GENERIC_ART = INSTRUMENT_ART_DIR / "thirteenth.png"
# The ONE documented exception the owner allowed: a theme whose dual
# page presents something none of its three seat-holders already
# describes may claim its OWN plate. Key -> True. EMPTY today; the
# per-theme briefs stay written in `titles/theme_title_prompts.md` so
# claiming one is a one-line change plus a generation.
THEME_OWN_DUALITY_PLATE: dict[str, bool] = {}
# key -> (register, look) where either differs from primary/colored.
TITLE_PLATE_SEATS = {
    "planets": ("primary", "photo"),
    "planet_signs": ("primary", "sign"),
    "planets_art": ("primary", "art"),
    "bible2": ("secondary", "colored"),
    "bible_dark": ("dark", "colored"),
    "religion_alt": ("secondary", "colored"),
}


def theme_title_art(key: str, duality: bool = False) -> "Path":
    """The plate for one theme-title or week-duality-title page. `key` is
    the article key the page already carries — "greek", "greek_pantheon",
    "greek_wider", "bible_dark"."""
    from config import taxonomy

    base, register = key, None
    for suffix in ("_pantheon", "_wider"):
        if base.endswith(suffix):
            base, register = base[: -len(suffix)], suffix[1:]
            break
    # EVERY dual page shares ONE plate unless this theme earned its own
    # (owner decree 2026-07-29) — the block's register does not matter,
    # because the generic plate belongs to no register.
    if duality and not THEME_OWN_DUALITY_PLATE.get(base):
        return DUALITY_GENERIC_ART
    seat_register, look = TITLE_PLATE_SEATS.get(base, ("primary", "colored"))
    register = register or seat_register
    stem = DUALITY_PLATE_STEM if duality else TITLE_PLATE_STEM
    if duality and register == "pantheon":
        # A pantheon block whose dual pair is the SAME pair as the
        # planetary block's would need an identical plate — Egypt's Ra
        # and Afu-Ra sit at the centre of both rosters. Rule #19: the
        # second plate is not a variant to draw, it is the first plate,
        # so the page reads the primary register's own file. Derived,
        # never enumerated: the comparison is the canon's two tables.
        pantheon = WEEKDAY_PANTHEON.get(base, {})
        if pantheon.get("dual_names") == WEEKDAY_DUAL_NAMES.get(base):
            register = seat_register
    # The live CODE keys are still the pre-rename ones (`bible2`,
    # `religion_alt`) — the rename table takes them to the taxonomy's own
    # key, and THEME_FOLDER from there to the folder that holds them.
    renamed = taxonomy.THEME_KEY_RENAMES.get(base, base)
    folder = taxonomy.theme_folder(renamed)
    return weekday_art(f"{folder}/{register}/{look}/{stem}.png")


def weekday_theme_body_art(
    theme: str, body: str, on_date: date | None = None, colored: bool = False,
) -> Path:
    """One theme's plate for one weekday body (bronze / canon file) —
    moved here from `app.encyclopedia._theme_body_art` (R5 MENU REWORK,
    Rule #5): the Encyclopedia gallery AND the new Pointer/Slot Theme
    picker windows both need a representative preview per theme, so the
    resolution lives ONCE in config and both readers import it. THE
    SAME expression used to be re-typed at every render call site
    (`render.weekday_body._draw_weekday_slot`, `render.compositor`'s hover
    legend, `app.controller._themed_weekday_set`'s baked bodies dict) —
    consolidated here (weekday ALT ROTATION round, owner 2026-07-20/21)
    so the universal rotation convention has exactly ONE weekday-body
    chokepoint instead of four copies drifting apart. `colored`
    redirects to the metal theme's `colored/` sibling folder, exactly
    like `app.encyclopedia._theme_dual_art`'s own flag. `on_date` opts
    into THE UNIVERSAL ROTATION CONVENTION (`rotating_art_file`): None
    (every caller before this round) returns the plain canonical file;
    a date resolves the day's pick among the canonical file's `_v2`/
    `alt/` siblings, falling back to canonical when none exist."""
    if theme == "planets":
        canonical = weekday_art(f"planets/primary/photo/{body.capitalize()}.png")
    else:
        theme_dir = weekday_art(WEEKDAY_THEME_DIRS[theme])
        if colored:
            theme_dir = theme_dir.parent / "colored"
        canonical = theme_dir / f"{WEEKDAY_THEME_FILES[theme][body]}.png"
    if on_date is None:
        return canonical
    return rotating_art_file(canonical, on_date) or canonical


# ONE menu/encyclopedia/settings title per theme (English; translated
# through the ui/ overlay at display) — every theme list iterates this.
WEEKDAY_THEME_TITLES = {
    "planets": "Planets",
    "planet_signs": "Planet signs",
    "greek": "Greek gods",
    "norse": "Norse gods",
    "egypt": "Egyptian gods",
    "slavic": "Slavic gods",
    "alchemy": "Alchemy",
    "japan": "Japanese week",
    # Owner renames 2026-07-13: masonry and voodoo are creeds and
    # mysteries, not strictly religions — and "Religions II" is gone.
    "religion": "Creeds",
    "religion_alt": "Ancient religions",
    "profession": "Professions",
    "wolf": "Wolf Pack",
    "bee": "Bee Hive",
    "elephant": "Elephant Herd",
    # The text-wave themes (owner 2026-07-14). planets_art carries NO
    # title on purpose: it nests as the Planets "Art" option in the
    # menu and rides the Planets encyclopedia topic as a look.
    "bible": "Bible",
    "bible2": "Bible II",
    "bible_dark": "Bible Dark",
    "cosmos": "Cosmos",
    # THE CONTINENTS (owner-sealed matrix 2026-07-21): the six lands ride
    # the six weekday columns; its Encyclopedia topic is CUSTOM-built
    # (`app.encyclopedia._continents_topic`) rather than the generic
    # weekday shape, so it can carry the world-map title page and the
    # Atmosphere/Clean · Day/Night look switcher.
    "continents": "Continents",
    # The Inner Wheel dial themes; their ENCYCLOPEDIA topics stay the
    # emblem pages (the later family pass overwrites the weekday
    # topics built from these titles — deliberate).
    "virtues": "Virtues",
    "sins": "Sins",
    "moods": "Moods",
    # COMPLETION WAVE I (Session 31). "Chinese Mythology" is NOT the
    # existing "chinese" topic — that one is the twelve-animal ZODIAC
    # reading years; this is a seven-figure cast holding a week.
    "age_of_heroes": "Greek Monsters",
    "celestial_court": "Chinese Mythology",
    "corporate": "The Corporation",
    # COMPLETION WAVE II (Session 32). Each cast is its OWN dial theme
    # and needs a title that identifies itself in a FLAT list (the
    # Settings rotation grid has no group headings), so the franchise
    # leads and the faction follows. The Encyclopedia is the opposite
    # case and reads "World of Warcraft" once, with Alliance | Horde |
    # Evil on the variant switcher (encyclopedia_tree.VARIANT_SOURCES).
    "wow_alliance": "Warcraft Alliance",
    "wow_horde": "Warcraft Horde",
    "wow_evil": "Warcraft Evil",
    # COMPLETION WAVE II, Cyberpunk half (Session 32). Same rule as the
    # Warcraft half: each cast is its own dial theme and needs a title
    # that identifies itself in a FLAT list, so the franchise leads and
    # the block follows. The Encyclopedia reads "Cyberpunk 2077" once,
    # with Gangs | Street | Power on the variant switcher
    # (encyclopedia_tree.VARIANT_SOURCES).
    "cp_gangs": "Cyberpunk Gangs",
    "cp_street": "Cyberpunk Street",
    "cp_corpo": "Cyberpunk Power",
    # COMPLETION WAVE III (Session 33). Same rule a third time: each cast
    # is its own dial theme and needs a title that identifies itself in a
    # FLAT list, so the franchise leads and the block follows. The
    # Encyclopedia reads "Star Wars" once, with Jedi | Sith | Dyad on the
    # variant switcher (encyclopedia_tree.VARIANT_SOURCES). The sheet's
    # own set names — Svetla, Tamna, Nova — stay in the sheet: the
    # program's language is English (root Rule #17).
    "sw_jedi": "Star Wars Jedi",
    "sw_sith": "Star Wars Sith",
    "sw_dyad": "Star Wars Dyad",
}

# The Weekday submenu's TOP entries (owner 2026-07-18): rendered FIRST,
# flat, ABOVE the kinship groups below — Planets is the DEFAULT theme
# and no longer hides inside Arcana. Nests Image/Sign plain plus the
# metal-capable Art look (planet_signs stays its own theme underneath;
# planets_art carries its Gold/Bronze/Silver dropdown via METAL_THEMES).
WEEKDAY_MENU_TOP = ("planets",)

# The Weekday submenu GROUPS (owner menu rework 2026-07-13): kinship
# submenus below the top entries. The Inner Wheel (Virtues/Sins/Moods)
# joins once those themes gain their dial texts.
WEEKDAY_MENU_GROUPS = (
    # Completion wave I (Session 31) joins the EXISTING kinship groups
    # rather than opening new ones: the two myth casts sit with the four
    # pantheons (`taxonomy.WEEK_GROUPS["myth"]` already holds all six),
    # and the Corporation sits beside the Professions — the same
    # `crafts` group on disk, and the same subject: offices people hold.
    # The "Films" group belongs to wave III.
    ("Ancient Gods", ("egypt", "greek", "norse", "slavic",
                      "age_of_heroes", "celestial_court")),
    ("Society", ("profession", "corporate", "religion", "religion_alt")),
    # The Scripture family (owner 2026-07-14).
    ("Scripture", ("bible", "bible2", "bible_dark")),
    # GAMING — opened by completion wave II (Session 32), matching
    # `taxonomy.WEEK_GROUPS["gaming"]` on disk. The three WoW casts were
    # its first members; the three Cyberpunk casts joined in the same
    # wave's second half, and the group stays ONE picker submenu for
    # both franchises (the kinship is the medium, not the setting) —
    # the same order `taxonomy.WEEK_GROUPS["gaming"]` already lists.
    ("Gaming", ("wow_alliance", "wow_horde", "wow_evil",
                "cp_gangs", "cp_street", "cp_corpo")),
    # FILMS — opened by completion wave III (Session 33, 2026-07-29),
    # matching `taxonomy.WEEK_GROUPS["films"]` on disk and closing the
    # backlog's list of new picker groups (checklist line 12 named
    # exactly two: Gaming and Films). It stays a group of its own rather
    # than joining Gaming for the reason the Gaming comment gives — the
    # kinship is the MEDIUM, and a film is not a game.
    ("Films", ("sw_jedi", "sw_sith", "sw_dyad")),
    ("Animals", ("wolf", "elephant", "bee")),
    # The emblem families on the dial (owner 2026-07-14).
    ("The Inner Wheel", ("virtues", "sins", "moods")),
    # Planets moved to WEEKDAY_MENU_TOP (owner 2026-07-18) — Arcana now
    # holds only the remaining three, plus the Continents (the world
    # itself, sitting beside the deep-sky Cosmos — owner 2026-07-21).
    ("Arcana", ("alchemy", "japan", "cosmos", "continents")),
)
