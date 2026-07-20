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
    config: era, subdial, scale, the archetype figure/center tables,
    trinity/season/sun turning points, eclipse emblems), PLUS the same
    walk over `app/encyclopedia.py`, `render/compositor.py`, `render.
    layers.py` and `render/assets.py` (the modules that actually
    consume these tables and occasionally hold their own), PLUS a
    plain TEXT scan of those same files for quoted `"....png"`/
    `"....svg"` literals (catches a filename built inside a function
    body, e.g. `SUBDIAL_ART_DIR / "master.png"`, that a namespace walk
    can never see since it is never bound to a module-level name).
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

from config import constants

_ROOT = Path(__file__).resolve().parents[1]
_PROMPTS_ROOT = _ROOT / "research" / "prompts"

# The modules whose own path TABLES feed the reference set — config's
# whole package (the primary source per Rule #19/this lint's design)
# plus the handful of consuming modules known to hold their own art
# tables (the Encyclopedia gallery, the dial layers/compositor).
_SCAN_PY_FILES = tuple(sorted((_ROOT / "config").glob("*.py"))) + (
    _ROOT / "app" / "encyclopedia.py",
    _ROOT / "render" / "compositor.py",
    _ROOT / "render" / "layers.py",
    _ROOT / "render" / "assets.py",
)
_SCAN_MODULES = (
    tuple(f"config.{p.stem}" for p in (_ROOT / "config").glob("*.py") if p.stem != "__init__")
    + ("app.encyclopedia", "render.compositor", "render.layers", "render.assets")
)

# A backticked path starting with "assets/" and ending in a real image
# extension — the drop-path convention every sheet in this repo uses,
# in both the per-image arrow line and the summary "Drop paths:" prose.
# `<...>` template placeholders and `*` globs are NOT concrete paths.
_PATH_PATTERN = re.compile(r"`(assets/[^`<*]+\.(?:png|svg))`")

# A quoted filename literal anywhere in scanned source TEXT — the
# fallback for names built inside a function body (e.g.
# `SUBDIAL_ART_DIR / "master.png"`), invisible to namespace introspection.
_LITERAL_FILENAME = re.compile(r"[\"']([\w .\-]+\.(?:png|svg))[\"']")

# Family roots whose individual filenames are DATA-DRIVEN (owner's
# roster/symbolism JSON, or — for `guide` — `assets/guide/pages.json`,
# `app/guide.py`) rather than enumerated anywhere in the scanned
# modules — a sheet path under one of these is checked only down to
# the FAMILY root.
_DATA_DRIVEN_ROOTS = (
    "weekday",
    "zodiac",
    "emblem/virtue",
    "emblem/sin",
    "emblem/mood",
    "emblem/intelligence",
    "guide",
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
    "archetype/trinity/rondel_Advocate.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/trinity/rondel_Prosecutor.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/trinity/rondel_Judge.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/family/rondel_Shield.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/family/rondel_Heart.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/family/rondel_Dawn.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/walks/rondel_Crown.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/walks/rondel_Bell.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/walks/rondel_Book.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/walks/rondel_Coin.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/walks/rondel_Mask.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/walks/rondel_Plough.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/walks/rondel_Staff.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    "archetype/walks/rondel_Sword.png": "optional row2 rondel, not yet wired (COVERAGE.md)",
    # The twelve Almanac month medallions: generated for the Encyclopedia
    # gallery's planned "Almanac" topic, which does not exist yet
    # (COVERAGE.md tracks this as "OK" — art landed ahead of the topic).
    "archetype/calendar/January.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/February.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/March.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/April.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/May.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/June.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/July.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/August.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/September.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/October.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/November.png": "Almanac month medallion, Encyclopedia topic not built yet",
    "archetype/calendar/December.png": "Almanac month medallion, Encyclopedia topic not built yet",
    # The dial's own Anno Lucis year is TEXT-ONLY today
    # (`core.deep_time.format_anno_lucis`) — COVERAGE.md: "ART GAP +
    # WIRING GAP — no code references assets/era/Anno_Lucis.png at all
    # today ... generating the art alone would not yet make it appear
    # anywhere." Art has since landed; the wiring gap stands.
    "era/Anno_Lucis.png": "generated, no draw site yet (COVERAGE.md)",
    # "The Ninth" — the union's child, explicitly "stands outside the
    # six" pillars (`one_soul_prompts.md` §The Ninth) — a deliberate
    # standalone concept, not one of the seated `prism_light` figures
    # COVERAGE.md tracks; no grid seat exists for it yet.
    "archetype/one_soul/Child.png": "the standalone Ninth, no grid seat wired yet",
    # The Union's SECOND, figurative glass window ("what if they had
    # met") — genuinely new content this round (scale_badge_prompts.md
    # §The two Unions), not yet added to `topics["duality"]`'s images.
    "badge/scale/glass/Union_Meeting.png": "figurative Union variant, not yet wired",
    # The Trinity badges ARE genuinely read (`app.encyclopedia._topics`:
    # `defaults.TRINITY_ART_DIR / f"{virtue}.png"` for `virtue in
    # ("Faith", "Hope", "Love")`) but `virtue` is a loop variable —
    # "Faith.png" happens to also appear as the topic's own literal
    # icon path (caught by the text scan), Hope/Love do not.
    "badge/trinity/Hope.png": "read via the Trinity topic loop, built at runtime",
    "badge/trinity/Love.png": "read via the Trinity topic loop, built at runtime",
    # The Instrument section's own article images
    # (`app.encyclopedia._topics`: `defaults.INSTRUMENT_ART_DIR /
    # f"{key}.png"` for `key in _INSTRUMENT_KEYS`) — same pattern.
    "instrument/paint_light.png": "read via the Instrument topic loop, built at runtime",
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
    — the one canonical, comparable form both sides get reduced to."""
    parts = Path(raw.replace("\\", "/")).parts
    if parts and parts[0] == "assets":
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


def _is_referenced(sheet_path_norm: str, references: set[str]) -> bool:
    stem_norm = sheet_path_norm.rsplit(".", 1)[0]     # extension-free tail form
    # THE UNIVERSAL ROTATION CONVENTION (owner decree 2026-07-20): a
    # `_v2`-style sibling is discovered on disk at runtime, by stem,
    # never enumerated by exact name anywhere — strip the suffix
    # before matching, exactly like `rotating_art_file`/
    # `scale_variant_file`'s own glob does.
    destemmed = _ROTATION_SUFFIX.sub("", stem_norm)
    candidates = {stem_norm, destemmed}
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
