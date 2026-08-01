"""THE SHEET-PATH LINT (owner decree 2026-07-20, RULE-19 round —
"uvek ista priča zbog neusklađenih promptova", the recurring class of
bug where a sheet's drop path and the code's actual read path drift
apart — the exact failure the Tetramorph generations hit when they
landed under `archetype/<source>/temperaments/tetramorph_<Creature>
.png` while the app has only ever read `archetype/<source>/tetramorph/
<Creature>.png`).

Every prompt sheet under `research/prompts/**` states backticked
`assets/...` drop paths — the per-image title-and-arrow line
(`**Title** -> \\`assets/...\\``) and the summary "Drop paths:" prose.
This test walks every sheet, extracts every such CONCRETE path (a
`<placeholder>` or a `*` glob is a template, not a declared file, and
is ignored), and asserts each is either:

(a) a path some config table or a consuming module's own art table
    actually references — the reference set is built PRAGMATICALLY,
    NOT by fully evaluating Python semantics: every `config/*.py`
    module's top-level namespace is walked recursively (Path objects
    and path-shaped strings, nested inside dicts/tuples to any depth —
    this alone covers every family that is exhaustively enumerated in
    config: era, scale, the archetype figure/center tables,
    trinity/season/sun turning points, eclipse emblems), PLUS the same
    walk over `app/encyclopedia/*.py`, `render/compositor.py`, `render.
    layers.py`, `render/assets.py`, `render/asset_recolor.py` and
    `render/asset_variants.py` (the modules that actually consume
    these tables and occasionally hold their own), PLUS a plain TEXT
    scan of those same files for quoted `"....png"`/`"....svg"`
    literals (catches a filename built inside a function body, e.g.
    the "moon.png" default in `render.asset_variants.
    moon_phase_image`, that a namespace walk can never see since it is
    never bound to a module-level name).
    Matched on the canonical path AFTER stripping both a leading
    `assets/` and any art-SOURCE segment (sheets state source-less
    paths; some config entries are bare relative tails without a
    family-root prefix, so a whole-segment SUFFIX match covers those
    too); or

(b) under a KNOWN DATA-DRIVEN ROOT — weekday/zodiac/emblem art whose
    individual filenames come from `Database/*.json` (rosters,
    symbolism), never enumerated in any `.py` file, so only the FAMILY
    root is checkable here (per-name completeness is `ROSTER.md`'s
    job, not this lint's); or

(c) on the WHITELIST below, each entry commented with why (independently
    cross-checked against `research/prompts/COVERAGE.md`'s own prior
    audit, which tracks the same gaps).

A sheet path failing all three is exactly the failure class this test
exists to end."""

import importlib
import re
from pathlib import Path

import pytest

from config import calendar_mounts, constants, continents, pantheon

_ROOT = Path(__file__).resolve().parents[1]
_PROMPTS_ROOT = _ROOT / "research" / "prompts"

# The modules whose own path TABLES feed the reference set — config's
# whole package (the primary source per Rule #19/this lint's design)
# plus the handful of consuming modules known to hold their own art
# tables (the Encyclopedia gallery, the dial layers/compositor).
_SCAN_PY_FILES = tuple(sorted((_ROOT / "config").glob("*.py"))) + (
    *sorted((_ROOT / "app" / "encyclopedia").glob("*.py")),
    _ROOT / "render" / "compositor.py",
    *sorted((_ROOT / "render" / "layers").glob("*.py")),
    _ROOT / "render" / "archetype_geometry.py",
    _ROOT / "render" / "calendar_mount.py",
    _ROOT / "render" / "ninths.py",
    _ROOT / "render" / "subdial.py",
    _ROOT / "render" / "assets.py",
    _ROOT / "render" / "asset_recolor.py",
    _ROOT / "render" / "asset_variants.py",
)
_SCAN_MODULES = (
    tuple(f"config.{p.stem}" for p in (_ROOT / "config").glob("*.py") if p.stem != "__init__")
    + (
        # SESSION 27: the Encyclopedia is a PACKAGE — its path tables
        # live in `pages`/`builders`/`tree`, so the namespace walk has
        # to name the submodules (the package's `__init__` exports only
        # the dialog and the topic table).
        "app.encyclopedia.pages", "app.encyclopedia.builders",
        "app.encyclopedia.tree",
        "render.compositor",
        # SESSION 37: `render.layers` is a PACKAGE — the art tables that
        # used to sit in the one god-file now live in these modules.
        "render.layers.background", "render.layers.center_body",
        "render.layers.ring", "render.layers.slot",
        "render.layers.weekday", "render.layers.year_marker",
        "render.archetype_geometry", "render.calendar_mount",
        "render.ninths", "render.subdial",
        "render.assets", "render.asset_recolor", "render.asset_variants",
    )
)

# A backticked path starting with "assets/" and ending in a real image
# extension — the drop-path convention every sheet in this repo uses,
# in both the per-image arrow line and the summary "Drop paths:" prose.
# `<...>` template placeholders and `*` globs are NOT concrete paths.
_PATH_PATTERN = re.compile(r"`(assets/[^`<*]+\.(?:png|svg))`")

# A quoted filename literal anywhere in scanned source TEXT — the
# fallback for names built inside a function body (e.g. the "moon.png"
# default in `render.asset_variants.moon_phase_image`), invisible to
# namespace introspection.
_LITERAL_FILENAME = re.compile(r"[\"']([\w .\-]+\.(?:png|svg))[\"']")

# Family roots whose individual filenames are DATA-DRIVEN (owner's
# roster/symbolism JSON, or — for `guide` — `assets/instrument/guide/pages.json`) rather than enumerated anywhere in the scanned
# modules — a sheet path under one of these is checked only down to
# the FAMILY root.
_DATA_DRIVEN_ROOTS = (
    # RESTRUCTURE 2026-07-22: the weekday themes now live under weeks/
    # (their Inner-Wheel emblems too, at weeks/inner_wheel/*); the two
    # zodiacs under calendars/; the guide under instrument/.
    "weeks",
    "calendars/zodiac",
    "calendars/zodiac/chinese",
    # RESTRUCTURE Phase 3 (owner-sealed 2026-07-22, seats SEALED and
    # WIRED 2026-07-29): the four NEW Dozens of the Calendars category —
    # Emotions (System B), the Virtue Wheel's two registers (Virtues
    # light + Vices paint, System B), Olympians and Apostles (System A,
    # six pairs each). Every per-figure filename is now enumerated in
    # `config.calendar_mounts.CALENDAR_MOUNTS` (a real Python roster, not a
    # JSON file) — but, exactly like the existing `calendars/zodiac`/
    # `chinese`/`slavic_months` families above, each MEMBER name is a
    # bare string with no "/" (never collected by this lint's namespace
    # walk, which only picks up Path-shaped or "/"-containing values —
    # `CalendarMount.art_dir` alone is collected), so only the FAMILY
    # root is checkable here; per-name completeness is the roster's own
    # job (`tests/test_calendar.py`'s golden seat-pin tests). Full
    # sheets: `research/prompts/calendars/{emotions,virtue_wheel,
    # olympians,apostles}_prompts.md`.
    "calendars/emotions",
    "calendars/virtues",
    "calendars/vices",
    "calendars/olympians",
    "calendars/apostles",
    # The FIFTH Dozen (owner-sealed 2026-07-29): the Sins, System B —
    # Pride crowns, Treachery roots, axle Hardness of Heart. Sheet:
    # `research/prompts/calendars/sins_prompts.md`.
    "calendars/sins",
    # RESTRUCTURE Phase 3: the ABSTRACT trinity/duality art — the Trio's
    # stacked readings (Time, Callings, Theological, Dialectic) and the
    # two great dualities (Good/Evil, Self/Others), each concept a
    # lancet + a 1:1 circle companion. New archetype art whose figure
    # tables land in config with the taxonomy round; unwired in Phase 3,
    # so checked only to the family root like the Dozens above. Full
    # sheets: `research/prompts/archetype/{triads,dualities}_prompts.md`.
    "archetypes/triads",
    "archetypes/dualities",
    # THE CUBE PROMPT-SHEET WAVE (WORKPLAN Session 19, CUBE.md sealed
    # 2026-07-26): the three NEW third wheels — Genesis (the Trinity's
    # creation trio, drawn inverted), Council (the Prism's six offices in
    # session) and Character (the Compass's Cube-at-depth-zero) — plus
    # the Two Crosses' Encyclopedia plates (the Paths of Light and
    # Darkness, their stations and the TRUST/DISTRUST centres). Their
    # figure tables land in `config.archetypes` with WORKPLAN Session 20
    # (the crosses are Encyclopedia/legend plates and take no wheel slot
    # at all); content-only in this round, exactly like the Phase 3
    # families above, so only the FAMILY root is checkable here. Full
    # sheets: `research/prompts/archetype/{genesis,council,character,
    # crosses}_prompts.md`. Ledger: `research/prompts/COVERAGE.md`,
    # §The Cube Wave.
    "archetypes/genesis",
    "archetypes/council",
    "archetypes/character",
    "archetypes/crosses",
    # THE CROSS-WORDS ROUND (owner UV inbox 2026-07-27): the Dollar
    # ring legend's five Double-Trinity OFFICES as banknote-engraving
    # plates — a NEW family in the note's own craft (intaglio, dollar
    # green), never sharing files with the Court/Genesis/Council glass
    # (one-image-one-place). Content-only like the wave above; wiring
    # (hover-card/Encyclopedia images for the ring legend) is a future
    # round, so only the FAMILY root is checkable here. Full sheet:
    # `research/prompts/archetype/banknote_offices_prompts.md`; its
    # sibling `cross_words_prompts.md` rides the existing
    # `archetypes/crosses` root in the `secondary` register.
    "archetypes/banknote",
    # THE THIRTEEN-AXES WAVE (WORKPLAN Session 25, 2026-07-28): the
    # eight NEW edge cells (`edges`) and the two seats that left the
    # human circle plus the centre (`sacred`). The SEAT plates of both
    # families ARE enumerated — `app.encyclopedia._CUBE_ENTRIES` reads
    # `EDGES_ART_DIR`/`SACRED_ART_DIR` for the Cube pages' own art — but
    # their `circle` companions and their three FIGURE registers
    # (archetypal/historical/modern, 48 + 6 files) land in a roster the
    # way every other Rose figure family does, so only the FAMILY root
    # is checkable here. Full sheets:
    # `research/prompts/archetype/{edges,axes}_prompts.md` and
    # `research/rose_round/edge_figures_prompts.md`.
    "archetypes/edges",
    "archetypes/sacred",
    "instrument/guide",
    # THE SLAVIC MONTHS (R7b round, owner-sealed 2026-07-21): every
    # per-month filename is enumerated in `config.defaults.
    # SLAVIC_MONTHS`, a real Python table — but built into a Path
    # INSIDE `app.encyclopedia._topics`'s dict comprehension
    # (`defaults.MONTHS_ART_DIR / f"{stem}.png"`), an f-string never
    # bound to a module-level name and never a bare quoted literal —
    # invisible to both this lint's namespace walk AND its text scan,
    # the exact same blind spot weekday/zodiac already carry. The
    # FAMILY root (`MONTHS_ART_DIR` itself) IS a real module-level
    # Path, confirming the family is genuinely wired; only the
    # per-name completeness escapes static scanning.
    "calendars/slavic_months",
)

# Documented exceptions: art generated (or sheeted) with NO consuming
# code path yet — every entry independently confirmed against
# `research/prompts/COVERAGE.md`'s own prior audit (§Compass Objects,
# §Subdial Masters history, the Anno Lucis wiring-gap row), not a
# guess made up for this test.
_WHITELIST: dict[str, str] = {
    # The row2 "calling"/"hearth-role"/"object" rondels (owner sheets:
    # generate ONLY if the owner later wants a second image per row —
    # today the two rows share one lancet). COVERAGE.md §Compass
    # Objects: "WIRING GAP — fully painted, zero code reads any
    # rondel_* path outside the evangelist set."
    "archetypes/trinity/primary/colored/Rondel_Advocate.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/trinity/primary/colored/Rondel_Prosecutor.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/trinity/primary/colored/Rondel_Judge.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/family/primary/colored/Rondel_Shield.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/family/primary/colored/Rondel_Heart.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/family/primary/colored/Rondel_Dawn.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/walks/primary/colored/Rondel_Crown.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/walks/primary/colored/Rondel_Bell.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/walks/primary/colored/Rondel_Book.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/walks/primary/colored/Rondel_Coin.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/walks/primary/colored/Rondel_Mask.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/walks/primary/colored/Rondel_Plough.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/walks/primary/colored/Rondel_Staff.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetypes/walks/primary/colored/Rondel_Sword.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    # The twelve Almanac month medallions: generated for the Encyclopedia
    # gallery's planned "Almanac" topic, which does not exist yet
    # (COVERAGE.md tracks this as "OK" — art landed ahead of the topic).
    "calendars/almanac/primary/colored/January.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/February.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/March.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/April.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/May.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/June.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/July.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/August.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/September.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/October.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/November.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "calendars/almanac/primary/colored/December.png": "Almanac month medallion, Encyclopedia topic not built yet",
    # The dial's own Anno Lucis year is TEXT-ONLY today
    # (`core.deep_time.format_anno_lucis`) — COVERAGE.md: "ART GAP +
    # WIRING GAP — no code references assets/era/Anno_Lucis.png at all
    # today ... generating the art alone would not yet make it appear
    # anywhere." Art has since landed; the wiring gap stands.
    "celestial/era/Anno_Lucis.png": "generated, no draw site yet (COVERAGE.md)",
    # ("The Ninth" — the union's Child — left this whitelist on
    # 2026-07-27: it has no WHEEL seat, since it "stands outside the six"
    # pillars, but the One Soul Encyclopedia topic now pages it like
    # every other seat, so the plate is genuinely referenced.)
    # (The figurative Union window, Union_Meeting→Union_v2 in the
    # figure-first sweep 2026-07-22, needs no entry anymore — the scale
    # family is a data-driven rotation root, discovered automatically.)
    # (The Trinity badges' Hope/Love entries are GONE since Session 21:
    # they were whitelisted because `app.encyclopedia._topics` builds
    # them from a loop variable and only "Faith.png" also appeared as a
    # literal icon path. The Two Crosses topic now declares literal
    # `crosses/primary/colored/Hope.png` and `Love.png`, and the lint's
    # basename-tail match covers the Trinity badges through them — so
    # the exception is no longer needed, and keeping it would be stale
    # bookkeeping by this file's own rule.)
    # The Instrument section's own article images
    # (`app.encyclopedia._topics`: `pantheon.INSTRUMENT_ART_DIR /
    # f"{key}.png"` for `key in _INSTRUMENT_KEYS`) — same pattern.
    "instrument/paint_light.png": "read via the Instrument topic loop, built at runtime",
    # BADGE SISTEM round one (owner 2026-07-20/21, DESIGN
    # INSTRUCTIONS.txt): 1:1 circular companions for the 2:1 archetype
    # lancets, feeding a FUTURE hover-card left-column layout — the
    # wiring is undecided (owner call), so no code reads
    # `assets/badge/circle/**` yet. Most of the 38 round-one paths
    # need NO whitelist entry at all: the lint's own basename-suffix
    # leniency (its docstring's own (a), "a whole-segment SUFFIX match"
    # — deliberately pragmatic, not full Python semantics) already
    # treats a badge path as "referenced" purely because its FILENAME
    # matches the source LANCET's own literal `"Stem.png"` string in
    # `config/archetypes.py`'s `_fig(...)` calls — a real, accepted
    # false-negative in the lint's own design (see its docstring), not
    # a gap. Only the Life-Tree register's 8 paths genuinely escape
    # BOTH lint mechanisms: `_LIFE_DIR / register / f"{stem}.png"` is
    # built from an f-string (no literal `"Stem.png"` text to scan,
    # unlike every other family's `_fig()` call) AND its own
    # module-namespace value is an ABSOLUTE Path whose string form
    # `_normalize` cannot reduce (no leading `assets/` segment to
    # strip from an absolute string) — so these 8 need the same
    # explicit whitelist treatment as the row2 rondels above.
    # `badge_1to1_prompts.md`'s own Status section tracks the whole
    # round-one set, wired or not.
    "archetypes/life/circle/colored/Unborn.png": "BADGE SISTEM round-one circle, not yet wired (owner call)",
    "archetypes/life/circle/colored/Birth.png": "BADGE SISTEM round-one circle, not yet wired (owner call)",
    "archetypes/life/circle/colored/Childhood.png": "BADGE SISTEM round-one circle, not yet wired (owner call)",
    "archetypes/life/circle/colored/Youth.png": "BADGE SISTEM round-one circle, not yet wired (owner call)",
    "archetypes/life/circle/colored/Maturity.png": "BADGE SISTEM round-one circle, not yet wired (owner call)",
    "archetypes/life/circle/colored/Elder.png": "BADGE SISTEM round-one circle, not yet wired (owner call)",
    "archetypes/life/circle/colored/Old_Age.png": "BADGE SISTEM round-one circle, not yet wired (owner call)",
    "archetypes/life/circle/colored/Death.png": "BADGE SISTEM round-one circle, not yet wired (owner call)",
    # THE THEME TITLE PLATES (R8c PROMPT SHEETS round, owner item 7,
    # 2026-07-21): a NEW sourceless root, `assets/weeks/societies/wolf/primary/colored/<key>.png`,
    # fills every weekday theme's (and two sibling topics') documented
    # graceful-absent title_entry slot (`app.encyclopedia.
    # _weekday_topic`'s `title_entry`, `"images": ()`  — "a future theme
    # plate's slot"). No code reads `assets/weeks/societies/wolf/primary/colored/**` yet; wiring
    # `title_entry["images"]` to `(defaults.TITLE_ART_DIR /
    # f"{theme}.png",)`, mirroring the one title plate that already IS
    # wired (`continents.CONTINENTS_TITLE_IMAGE`, `assets/earth/world.png`
    # — Continents is deliberately excluded from this family, per the
    # owner's own instruction), is a future app-code round. Full briefs:
    # The theme-title plates need no whitelist entries any more: since
    # the tree law (2026-07-26) every `Title` plate lives INSIDE its
    # theme's own family root, which the data-driven roots above
    # already cover down to the family — the 36 old `titles/…` entries
    # died with the `assets/titles/` root itself.
    # THE GAMING + CORPORATION SHEET WAVE (R10, owner-sealed rosters
    # 2026-07-22): ten more theme title plates, same sourceless
    # `assets/weeks/societies/wolf/primary/colored/<key>.png` family as the block above — WoW,
    # Cyberpunk and Star Wars each carry three blocks/sets so each
    # names three title plates, The Corporation carries one. Written in
    # full in `titles/theme_title_prompts.md`'s own "GAMING +
    # CORPORATION SHEET WAVE title plates" section; each new theme
    # sheet (`wow_prompts.md`, `cyberpunk_prompts.md`,
    # `starwars_prompts.md`, `corporate_prompts.md`) carries only a
    # pointer, never a duplicate body. No code reads `assets/weeks/societies/wolf/primary/colored/**`
    # yet (same future wiring round as the block above).
}


def _sheet_paths() -> dict[Path, list[str]]:
    found: dict[Path, list[str]] = {}
    for sheet in sorted(_PROMPTS_ROOT.rglob("*.md")):
        matches = _PATH_PATTERN.findall(sheet.read_text(encoding="utf-8"))
        if matches:
            found[sheet] = matches
    return found


def _normalize(raw: str) -> str:
    """`raw` relative to assets/, with any art-SOURCE segment removed
    — the one canonical, comparable form both sides get reduced to.

    A leading `../` step-up is dropped: a few config tables reach across
    family roots that way (the Continents ninths name
    `"../earth/zealandia.png"` relative to `WEEKDAY_ART_DIR`, and
    `config.paths.art_file` collapses the step-up before touching disk),
    so it is a spelling of the reference, never part of its identity."""
    parts = Path(raw.replace("\\", "/")).parts
    if parts and parts[0] == "assets":
        parts = parts[1:]
    while parts and parts[0] == "..":
        parts = parts[1:]
    if len(parts) >= 2 and parts[1] in constants.ART_SOURCES:
        parts = (parts[0],) + parts[2:]
    return "/".join(parts)


def _collect(value, into: set[str], depth: int = 0) -> None:
    """Recursively pull every Path / path-shaped string out of a
    scanned module's value, to any nesting depth (dicts, tuples/lists/
    sets, and `_fig()`-style figure dicts alike)."""
    if depth > 8:
        return
    if isinstance(value, Path):
        into.add(str(value).replace("\\", "/"))
    elif isinstance(value, str):
        if "/" in value or value.lower().endswith((".png", ".svg")):
            into.add(value)
    elif isinstance(value, dict):
        for item in value.values():
            _collect(item, into, depth + 1)
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            _collect(item, into, depth + 1)


def _reference_set() -> set[str]:
    """Every path-shaped value reachable from the scanned modules' own
    top-level namespaces, PLUS every quoted filename literal in their
    raw source text, normalized."""
    raw: set[str] = set()
    for module_name in _SCAN_MODULES:
        module = importlib.import_module(module_name)
        for name, value in vars(module).items():
            if name.startswith("__"):
                continue
            _collect(value, raw)
    for py in _SCAN_PY_FILES:
        raw.update(_LITERAL_FILENAME.findall(py.read_text(encoding="utf-8")))
    return {_normalize(r) for r in raw}


_ROTATION_SUFFIX = re.compile(r"_v\d+$")
# THE UNIVERSAL ROTATION CONVENTION's SECOND legal form (ERA-TRIO
# round, owner 2026-07-20): a same-named file one level down in an
# `alt/` subfolder, exactly like `rotating_art_file`'s own
# `directory / "alt"` search — matches "/alt" only when immediately
# followed by another "/" (so "/alternate/" never false-positives).
_ROTATION_ALT_SEGMENT = re.compile(r"/alt(?=/)")


def _is_referenced(sheet_path_norm: str, references: set[str]) -> bool:
    stem_norm = sheet_path_norm.rsplit(".", 1)[0]     # extension-free tail form
    # THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20): a
    # rotation sibling is discovered ON DISK at runtime, by stem, never
    # enumerated by exact name anywhere — strip either of its two legal
    # forms before matching, exactly like `rotating_art_file`'s own
    # candidate search does: a `_v2`-style suffix, or an `/alt/` path
    # segment one level below the canonical file's own directory (the
    # Byzantine v2 calendar emblem, `calendar/alt/Byzantine.png`, is
    # the first sheet entry to actually DECLARE a concrete alt/-nested
    # path — every combination of the two forms is tried).
    destemmed = _ROTATION_SUFFIX.sub("", stem_norm)
    candidates = {
        stem_norm, destemmed,
        _ROTATION_ALT_SEGMENT.sub("", stem_norm),
        _ROTATION_ALT_SEGMENT.sub("", destemmed),
    }
    for ref in references:
        if sheet_path_norm == ref:
            return True
        ref_stem = ref.rsplit(".", 1)[0] if "." in Path(ref).name else ref
        for candidate in candidates:
            if candidate == ref_stem:
                return True
            # A bare relative/basename tail (no family-root prefix, or
            # no extension — a dict fragment or an identifier-like
            # config value) matches as a whole-segment SUFFIX either way.
            if candidate.endswith("/" + ref_stem) or ref_stem.endswith("/" + candidate):
                return True
            if candidate.rsplit("/", 1)[-1] == ref_stem:
                return True
    return False


def _is_data_driven(sheet_path_norm: str) -> bool:
    return any(
        sheet_path_norm == root or sheet_path_norm.startswith(root + "/")
        for root in _DATA_DRIVEN_ROOTS
    )


def test_every_sheet_path_is_read_by_something():
    references = _reference_set()
    offenders = []
    for sheet, raw_paths in _sheet_paths().items():
        sheet_rel = sheet.relative_to(_ROOT)
        for raw in sorted(set(raw_paths)):
            norm = _normalize(raw)
            if norm in _WHITELIST:
                continue
            if _is_data_driven(norm):
                continue
            if _is_referenced(norm, references):
                continue
            offenders.append(f"{sheet_rel}: `{raw}`")
    assert offenders == [], (
        "sheet path(s) nothing reads (fix the sheet or add a commented "
        "whitelist entry):\n" + "\n".join(offenders)
    )


def test_whitelist_has_no_stale_entries():
    """The flip side: a whitelisted path that turns out to BE
    referenced after all (or that no sheet even declares any more) is
    stale bookkeeping, not a real exception — keep the list honest."""
    references = _reference_set()
    declared = {
        _normalize(raw)
        for raw_paths in _sheet_paths().values()
        for raw in raw_paths
    }
    stale = [
        norm for norm in _WHITELIST
        if norm not in declared
        or _is_data_driven(norm)
        or _is_referenced(norm, references)
    ]
    assert stale == []


@pytest.mark.parametrize("sheet", sorted(_PROMPTS_ROOT.rglob("*.md")))
def test_every_sheet_declares_at_least_one_path_or_is_an_index(sheet):
    """A sanity net on the lint itself: every LEAF sheet (one actual
    prompt set, not an index/spec page) must state at least one
    backticked assets/ path — a sheet with ZERO recognizable drop
    paths is invisible to `test_every_sheet_path_is_read_by_something`
    and would hide a formatting drift instead of catching one."""
    if sheet.name.startswith("___"):
        pytest.skip("a ___folder.md index page, not a sheet (project convention)")
    text = sheet.read_text(encoding="utf-8")
    if "```" not in text:
        pytest.skip("no fenced prompt body — an index/spec page, not a sheet")
    assert _PATH_PATTERN.search(text) is not None, sheet


# --- THE FOLDER-EXISTS LAW (owner decree 2026-07-28) --------------------------
# "svi promptovi se sredjuju da ne dodjemo da toga da preko prompt
# paintere pravimo lazne foldere zato sto neki idiot agent nije sredio
# putanje u promptovima za slike."
#
# The lint above asks "does anything READ this path". That is not enough:
# a sheet can name a folder that does not exist and still pass, because
# some config entry mentions a similar tail. Generating from such a sheet
# CREATES the folder — a fake tree is born outside the five category
# roots, and the art has to be rescued later. It happened three times:
# the zodiac re-drop twice (4c683ed, 0.14.517) and the badge circles
# (0.14.519). These two tests close it.
_CONCRETE_ASSET_PATH = re.compile(r"assets/[A-Za-z0-9_./-]+")
_TEMPLATE_NEXT = "<[*"          # what follows a truncated placeholder path


def _declared(sheet_text: str):
    """(folder, is_drop_path) for every CONCRETE path a sheet declares.
    A placeholder (`<family>`, `Eye[_shine]`, a `*` glob) is a template,
    not a declaration; a `.md` link is a doc reference."""
    for match in _CONCRETE_ASSET_PATH.finditer(sheet_text):
        raw = match.group().rstrip(".,)`")
        tail = sheet_text[match.end():match.end() + 1]
        if raw.endswith(".md") or tail in _TEMPLATE_NEXT or raw.endswith(("_", "-")):
            continue
        path = Path(raw)
        yield (path.parent if path.suffix else path), bool(path.suffix)


def _sheet_folders():
    for sheet in sorted(_PROMPTS_ROOT.rglob("*.md")):
        name = sheet.relative_to(_ROOT).as_posix()
        for folder, is_drop in _declared(sheet.read_text(encoding="utf-8")):
            yield name, folder.as_posix(), is_drop


def test_no_sheet_names_a_folder_the_tree_does_not_have():
    offenders = sorted({
        f"{sheet} -> {folder}"
        for sheet, folder, _ in _sheet_folders()
        if not (_ROOT / folder).is_dir()
    })
    assert offenders == [], (
        "a prompt sheet declares a folder that does not exist — generating "
        "from it would CREATE a fake tree (owner decree 2026-07-28). Fix the "
        "sheet, or create the folder deliberately if the drop is real: "
        + ", ".join(offenders)
    )


def test_drop_folders_obey_the_tree_law():
    """A folder can exist and still be the wrong seat. Inside the three
    FIGURE categories every DROP folder is a LOOK whose parent is a
    REGISTER — the same law `tests/test_assets_structure.py` enforces on
    the files themselves."""
    from tests.test_assets_structure import _LAW_LOOKS, _LAW_REGISTERS

    offenders = sorted({
        f"{sheet} -> {folder}"
        for sheet, folder, is_drop in _sheet_folders()
        if is_drop
        and folder.split("/")[1:2] in (["weeks"], ["calendars"], ["archetypes"])
        and not (folder.split("/")[-1] in _LAW_LOOKS
                 and folder.split("/")[-2] in _LAW_REGISTERS)
    })
    assert offenders == [], (
        "sheet DROP folders off the TREE LAW — a drop folder is a LOOK "
        "inside a REGISTER (<theme>/<register>/<look>/): "
        + ", ".join(offenders)
    )
