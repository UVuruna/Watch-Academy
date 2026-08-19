"""The weekday theme ENGINE — the resolvers, not the data.

Every WEEKDAY_* table this module used to declare now lives in
`config.registry` (owner decree 2026-08-01): one entry per theme,
each table computed from it in ONE assignment. The names below are
kept because thirty-odd call sites read them, and they resolve to the
registry's own tables — there is no second copy and nothing to keep
in step.

What remains here is BEHAVIOUR: THE UNIVERSAL ROTATION CONVENTION and
its pickers (daily, weekly mandate, seat roster), the PANTHEON seat
resolver with its graceful-absent law, the Scale badge rotation, the
weekday art path resolver, the colored-variant swap and the
title-plate resolver.

Layer: config — pure, no Qt, no wall clock.
"""

import re
from datetime import date
from pathlib import Path

from config import continents, ninth, paths, registry


# --- The PANTHEON roster (owner doctrine 2026-07-15) --------------------------
# Per theme: each seat lists CANDIDATE art paths (relative to
# assets/weekday/, first existing wins) — a seat with NO existing
# candidate falls back to the PLANETARY bundle (file + name + article
# together) so a half-generated pantheon never shows a wrong
# (figure, article) pair. Colored variants live under the register's
# own <register>/colored/ child mirroring the bronze stems (tree law
# 2026-07-26 — identical for pantheon and primary alike).
WEEKDAY_PANTHEON = registry.PANTHEON

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
        # `existing_art_file` answers from the resolution cache without a
        # second stat, and it tolerates a None resolution — the old
        # `art_file(path).exists()` would have raised on one.
        if _paths.existing_art_file(path) is not None:
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

#: Daily-rotation pools per (directory, stems), NON-EMPTY RESULTS ONLY
#: (owner bug 2026-08-06). `_rotation_candidates_in` is reached from
#: every weekday body and every seated slot on every tick, and it walked
#: the directory once PER STEM. Cleared whenever new art lands — see
#: `reset_rotation_cache` and its caller in `app.watch_manager`.
_ROTATION_CACHE: dict[tuple[str, tuple[str, ...]], list] = {}


def reset_rotation_cache() -> None:
    """Forget every scanned rotation pool: new art has landed on disk."""
    _ROTATION_CACHE.clear()


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
    key = (str(directory), stems)
    cached = _ROTATION_CACHE.get(key)
    if cached is not None:
        return list(cached)
    if not directory.is_dir():
        return []
    # ONE directory walk, not one PER STEM (owner bug 2026-08-06): this
    # runs for every weekday body and every seated slot on every tick,
    # and the `iterdir()` used to sit INSIDE the stem loop.
    # Any shipped art extension, not `.png` alone (THE ART BAKERY,
    # 2026-08-12). This was the seventh and most expensive blind site of
    # that round: on a baked tree the old filter matched NOTHING, so the
    # rotation POOL came back empty and every rotating family — every
    # weekday body, the ninths, the duals, the era and eclipse topics —
    # silently fell back to its own missing-art path. The version core
    # is read off the stem, so nothing else here cares what the file was
    # encoded as, and `existing_art_file` below still rebuilds the
    # canonical `.png` name and lets the one door resolve it.
    entries = [
        entry for entry in directory.iterdir()
        if paths.is_art_file(entry)
    ]
    candidates: list[Path] = []
    seen_names: set[str] = set()
    for stem in stems:
        stem_lower = stem.lower()
        for entry in entries:
            if entry.name in seen_names:
                continue
            core = _sourceless_core(entry.stem)
            if not core.lower().startswith(stem_lower):
                continue
            tail = core[len(stem):]
            if tail == "" or _VERSION_SUFFIX.match(tail):
                candidates.append(entry)
                seen_names.add(entry.name)
    if candidates:
        # NON-EMPTY RESULTS ONLY — an empty pool is "the art has not
        # landed yet", and remembering that would keep a freshly
        # generated figure off the dial until the next restart. Same
        # rule, same reason, as `config.paths._ART_FILE_CACHE`.
        _ROTATION_CACHE[key] = list(candidates)
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
            picked = paths.existing_art_file(directory / f"{core}.png")
            if picked is not None and picked not in seen_files:
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
    `ninth.NINTH_MECHANISMS["cp_corpo"] == "term_weekly"`): the
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
WEEKDAY_SEAT_ROSTERS = registry.SEAT_ROSTERS
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
    table here keeps (Rule #1's documented path). Each member is its own
    version FAMILY, not only its master file: a member shipped as
    `_v2`-only (sw_dyad's Finn and Maz, 2026-08-08) resolves to its
    first existing version instead of vanishing from the seat."""
    resolved: list[Path] = []
    for stem in stems:
        family = _rotation_candidates((directory,), (stem,))
        if family:
            resolved.append(family[0])
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
    (`_pick_weekly_mandate`, `ninth.NINTH_MECHANISMS["cp_corpo"] ==
    "term_weekly"` — THE WEEKLY MANDATE, owner decree 2026-07-29): ONE
    rotation chokepoint, a per-theme CADENCE rather than a second
    mechanism (Rule #5). Opt-in per consumer (scale duality, era
    emblems, tetramorph figures, every weekday body) — never on the hot
    `art_file` path. This is the ONE chokepoint every weekday consumer
    already calls, which is why the roster hooks in here rather than at
    four call sites. None only when the whole FAMILY has nothing on
    disk: a family whose master is absent but whose `_v2` siblings
    exist is still a family — an early master-existence guard here once
    made ten Star Wars seats (shipped as `_v2`-only files) invisible to
    the dial and every picker at once (owner screenshots 2026-08-08)."""
    stems = _seat_roster_of(canonical_path)
    if stems is not None:
        theme = canonical_path.parts[-4]
        picker = (
            _pick_weekly_mandate
            if ninth.NINTH_MECHANISMS.get(theme) == "term_weekly"
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
WEEKDAY_THEME_NAMES = registry.NAMES
# THE CONTINENTS (owner-sealed matrix 2026-07-21): the six weekday
# columns are the six continents; Sunday's body is Antarctica, the
# Ruler face of the polar dual (the Arctic Servant lives in
# WEEKDAY_DUAL_NAMES). Added after the literal so the FILES auto-build
# below still folds every OTHER theme's names; the continents file
# stems are the earth faces, overridden explicitly (like greek/norse).

# File stems on disk: the display names folded to ASCII (Sól -> Sol,
# Dažbog -> Dazbog) and PASCAL-CASED per token (tree law rule 5, the
# case half, owner-approved 2026-07-26: every stem reads as a NAME —
# Afu_Ra, Big_Bang — never a lowercase file token). The themes below
# historically shipped lowercase stems; their names are NORMALIZED
# (lowered, then Pascal-cased) so display-name capitals like "McX"
# can never drift the stem from what the disk rename produced.


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
WEEKDAY_THEME_DIRS = registry.DIRS
WEEKDAY_THEME_FILES = registry.FILES
# The dual center shows both faces in the hover title, but the owner's
# medallion file keeps the single name.
# The Corporation's six weekday stems ARE its display names (the
# acronyms already carry their own capitals, so the Pascal rule leaves
# them alone) — only the dual Sunday title needs the single-name file.
# The metal reads Quicksilver, the owner's file keeps the element name.
# The reworked Creeds and the wolf rank parentheticals keep plain stems.
# The Greek and Norse display names carry native-script parentheticals
# now — the files stay on the plain ASCII stems.
# The Japanese display names carry kanji — the files are the romaji
# day names folded to plain ASCII (macrons and the apostrophe dropped).
# The text-wave themes (owner 2026-07-14): explicit stems — the
# display names carry duals ("·") and compounds ("Adam & Eve");
# PascalCase per the tree law's stem casing (rule 5, 2026-07-26).
# Completion wave I (Session 31): explicit stems — the display names
# carry duals ("·"), spaces (Erymanthian Boar, Sun Wukong) and a
# diacritic (Zhinü) that the ASCII fold does not know.
# Completion wave II (Session 32): explicit stems for all three WoW
# casts — the display names carry the Sunday dual ("·"), epithets
# (the Lightbringer, the Deceiver), surnames the file drops, and the
# apostrophes of Vol'jin, Kel'Thuzad, Gul'dan and Kil'jaeden that the
# ASCII fold does not know. The stems are the sheet's own drop paths.
# Completion wave II, Cyberpunk half (Session 32): the stems are the
# CANONICAL member of each seat — the first entry of the seat's roster
# below, and the only one the auto-build could never have guessed, since
# a roster seat's display name lists every member. The stems are the
# sheet's own drop paths.
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
# The emblem stems ARE the single names (Capitalized) — only the dual
# sun display titles need the override.
# THE CONTINENTS' file stems ARE the Earth faces (owner exception
# 2026-07-21): the atmosphere-lit day globe per region is the baked
# preview/fallback stem; the live dial overrides both style and phase
# at render (continents_body_art). Built straight from CONTINENTS_
# REGIONS so the mapping lives in exactly one place (Rule #5).

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
WEEKDAY_DUAL_NAMES = registry.DUAL_NAMES
# Dual paths live FLAT inside the theme's look dir (owner DUAL
# FLATTEN 2026-07-19: the dual/ folder carried zero semantic weight at
# runtime — the config table already IS the identity, so the folder
# only added a navigation step); the colored dual is the same path
# with the LOOK segment (the last folder) swapped to colored/ —
# `colored_variant_rel` below is the ONE implementation of that swap
# (tree law 2026-07-26; the old "/primary/" string replace died with
# the sibling-colored shape).
WEEKDAY_DUAL_FILES = registry.DUAL_FILES


def weekday_dual_rel(theme: str, roster: str = "planetary") -> str | None:
    """WHICH Sunday dual plate a theme wears under `roster` — the ONE
    implementation of a rule the compositor used to hold alone (owner
    report 2026-08-15, "svaki bi trebao da prikazuje svoju verziju
    nedelje jer nisu isti": the Artwork previews drew the planetary dual
    for both rosters, because they never asked this question at all).

    The pantheon dual wins ONLY when its plate is actually on disk —
    otherwise the whole planetary pair stays, which is the classic
    unit's Sunday law. `None` when the theme carries no dual at all
    (graceful absence, never a stand-in)."""
    dual_rel = WEEKDAY_DUAL_FILES.get(theme)
    if dual_rel is None:
        return None
    if roster == "pantheon" and theme in WEEKDAY_PANTHEON:
        candidate = WEEKDAY_PANTHEON[theme]["dual"][0]
        if paths.existing_art_file(weekday_art(f"{candidate}.png")) is not None:
            return candidate
    return dual_rel


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
TITLE_PLATE_SEATS = registry.TITLE_PLATE_SEATS


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
    legend, `app.skin_builder._themed_weekday_set`'s baked bodies dict) —
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
WEEKDAY_THEME_TITLES = registry.TITLES

# The Weekday submenu's TOP entries (owner 2026-07-18): rendered FIRST,
# flat, ABOVE the kinship groups below — Planets is the DEFAULT theme
# and no longer hides inside Arcana. Nests Image/Sign plain plus the
# metal-capable Art look (planet_signs stays its own theme underneath;
# planets_art carries its Gold/Bronze/Silver dropdown via METAL_THEMES).
WEEKDAY_MENU_TOP = registry.MENU_TOP

# The Weekday submenu GROUPS (owner menu rework 2026-07-13): kinship
# submenus below the top entries. The Inner Wheel (Virtues/Sins/Moods)
# joins once those themes gain their dial texts.
WEEKDAY_MENU_GROUPS = registry.MENU
