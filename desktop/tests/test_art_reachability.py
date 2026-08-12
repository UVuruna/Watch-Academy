"""NO ART SITS UNSEEN — the whole `assets/` tree, not just the weeks.

THE THEME COMPLETION LAW (project `CLAUDE.md`) was written after 429
generated plates sat on disk invisible to the program. Its guard
(`test_theme_completeness.py`) watches `assets/weeks/` — and on
2026-08-05 an audit found the SAME failure one directory over: ~280
plates under `assets/archetypes/` that no config table resolves, some
of them tagged "not yet wired" in test comments years-of-sessions ago.
The owner's ruling that day: the guard covers the WHOLE tree, so we
have one source of truth for what exists and what is still owed.

THE CONTRACT. Every directory under `assets/` holding at least one
`.png` must be one of three things, and saying which is the point:

1. **RESOLVED** — some config table or resolver reaches it. This is
   computed, not declared: the collector below walks `config`'s own
   Path-valued tables and then applies the resolvers that BUILD paths
   (the colored-variant swap, the Ninth and dual plates, the pantheon
   candidates, the circle register THE DIAL LAW seats, the Scale's two
   look homes, the calendar mounts and the zodiac style dirs).
2. **NAMED ELSEWHERE** — resolved outside `config`, by a runtime path
   built from variables that no static walk can see (`f"{theme}/wider/
   bronze/…"`). Those live in `RESOLVED_ELSEWHERE` below, each with the
   module that reads it. An entry here is a STATEMENT, not silence.
3. **A NAMED DEBT** — art on disk that nothing shows yet, listed in the
   staging ledger's own §Art Outside The Weeks table with what it owes
   and who owes it.

Anything else fails. A future round that generates plates and walks
away fails in the same session that did it.
"""

import importlib
import pkgutil
import re
from pathlib import Path

import config
from config import (
    archetypes, calendar_mounts, constants, dial, pantheon, paths, registry,
)

_ROOT = Path(__file__).resolve().parents[1]
_LEDGER_PATH = _ROOT / "research" / "theme_staging.md"
_ASSETS = paths.assets_dir().resolve()

# ═══════════════════════════ RESOLVED ELSEWHERE ═══════════════════════════
# Directory (posix, relative to assets/) -> the reader that builds its
# path at runtime from variables. Static analysis cannot see an f-string;
# naming the reader is how the claim stays checkable by a human.
RESOLVED_ELSEWHERE: dict[str, str] = {
    "weeks/myth/{theme}/wider/{look}":
        "app.encyclopedia.builders._wider_topic — the four god themes' "
        "B-list court, path built per theme",
    "celestial/era/calendar":
        "app.encyclopedia.pages — the era calendar plates",
    "celestial/seasons/badges/turning_point":
        "app.encyclopedia.pages — the solstice/equinox plates",
    "celestial/seasons/badges/meteorological":
        "app.encyclopedia.pages — the meteorological season plates",
    "calendars/zodiac/chinese/elements/colored":
        "app.encyclopedia.tree — the five elements, a parallel reading "
        "of the same zodiac rather than a thirteenth animal",
    "instrument/subdial/{set}":
        "config.constants.SUBDIAL_SETS + app.controller.build_skin — the "
        "set name is a settings value, the path built from it",
    "instrument/hands/{style}":
        "the skin's own hand sets — path built from the skin JSON",
    "archetypes/sacred/{register}/colored":
        "config.cube.FIGURE_SETS — the three people-sets of the sacred "
        "seats, resolved per register",
    "archetypes/sacred/circle/colored":
        "THE DIAL LAW's plate for the sacred seat",
    "archetypes/crosses/circle/colored":
        "THE DIAL LAW's plate for the Two Crosses' stations",
    "archetypes/crosses/secondary/colored":
        "the Cross Words medallions — render.cube_diagrams reads them "
        "through the crosses family",
    "archetypes/edges/circle/colored":
        "THE DIAL LAW's plate for the thirteen-axes edge seats",
    "archetypes/life/circle/colored":
        "THE DIAL LAW's plate for the Eight Ages (whose figures live in "
        "registers, not in the ARCHETYPES figure table)",
    # The 2026-08-05 wiring round: the Triads and Dualities cards of the
    # Faith whole build every concept page's lancet + 1:1 companion from
    # `archetypes.TRIADS_ART_DIR` / `DUALITIES_ART_DIR` per trio/pair.
    "archetypes/triads/{trio}/primary/colored":
        "app.encyclopedia.tree — the Triads card's concept lancets",
    "archetypes/triads/{trio}/circle/colored":
        "app.encyclopedia.tree — the same pages' 1:1 circle companions",
    "archetypes/dualities/{pair}/primary/colored":
        "app.encyclopedia.tree — the Dualities card's pole lancets",
    "archetypes/dualities/{pair}/circle/colored":
        "app.encyclopedia.tree — the same pages' 1:1 circle companions",
    # The 2026-08-12 performance round: the whole plate library baked
    # into every finish at setup; the launch reads, never computes.
    "_baked/letters":
        "render.letter_bake.bake_dir — the pre-baked letter finishes "
        "written by setup/make_letter_bake.py; not unwired art but "
        "DERIVED art, named by asset_recolor.letter_cache_name and "
        "resolved at runtime by jewel_metal_path",
}

_PLACEHOLDER = re.compile(r"\{[a-z_]+\}")


def _matches_pattern(rel: str, pattern: str) -> bool:
    """`weeks/myth/greek/wider/bronze` matches `weeks/myth/{theme}/wider/
    {look}` — one path segment per placeholder, never a slash."""
    regex = "^" + _PLACEHOLDER.sub(r"[^/]+", re.escape(pattern)
                                   .replace(r"\{", "{").replace(r"\}", "}")) + "$"
    regex = re.sub(r"\{[a-z_]+\}", "[^/]+", regex)
    return re.match(regex, rel) is not None


# ═══════════════════════════ THE COLLECTOR ═══════════════════════════


def _resolved_dirs() -> set[Path]:
    """Every assets/ directory the CONFIG layer can reach — the tables it
    declares, plus the resolvers that build paths from them."""
    found: set[Path] = set()

    def add(value) -> None:
        if value is None:
            return
        path = Path(value)
        try:
            rel = path.resolve().relative_to(_ASSETS)
        except (ValueError, OSError):
            return
        target = _ASSETS / rel
        found.add((target if target.is_dir() else target.parent).resolve())

    def walk(value, depth: int = 0) -> None:
        if depth > 6:
            return
        if isinstance(value, Path):
            add(value)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item, depth + 1)
        elif isinstance(value, (list, tuple, set, frozenset)):
            for item in value:
                walk(item, depth + 1)

    for module_info in pkgutil.walk_packages(config.__path__, "config."):
        try:
            module = importlib.import_module(module_info.name)
        except Exception:                      # a module that needs Qt/state
            continue
        for name in dir(module):
            if name.startswith("__"):
                continue
            try:
                walk(getattr(module, name))
            except Exception:
                continue

    # --- the resolvers: what the tables DESCRIBE, code builds ----------
    for rel in registry.DIRS.values():
        art_dir = pantheon.weekday_art(rel)
        add(art_dir)
        for look in ("colored", "bronze"):     # colored_variant_rel's swap
            add(art_dir.parent / look)
    for rel in registry.DUAL_FILES.values():
        seat = pantheon.weekday_art(rel).parent
        add(seat)
        add(seat.parent / "colored")
    for table in (registry.NINTHS, registry.NINTH_EASTER_EGG,
                  registry.NINTH_NIGHT):
        for _name, plate in table.values():
            add(pantheon.weekday_art(plate).parent)
    for entry in registry.PANTHEON.values():
        candidates = [rel for cands in entry["files"].values() for rel in cands]
        candidates += list(entry["dual"])
        for rel in candidates:
            seat = pantheon.weekday_art(f"{rel}.png").parent
            add(seat)
            add(seat.parent / "colored")
    for mount in calendar_mounts.CALENDAR_MOUNTS.values():
        # a two-depiction wheel carries its dark face's plates too
        for face in (mount, mount.paint):
            if face is not None:
                add(_ASSETS / "calendars" / face.art_dir)
    for table in (constants.ZODIAC_STYLE_ART_DIRS,
                  constants.CHINESE_STYLE_ART_DIRS):
        for rel in table.values():
            add(_ASSETS / "calendars" / rel)
    for spec in archetypes.ARCHETYPES.values():
        for figure in spec.get("figures", ()):
            look_dir = Path(figure["file"]).parent
            add(look_dir)
            add(look_dir.parent.parent / "circle" / "colored")   # THE DIAL LAW
        center = spec.get("center") or {}
        add(center.get("file"))
    for look in ("primary", "glass"):          # pantheon.scale_variant_file
        add(pantheon.SCALE_ART_DIR / look / "colored")
    # THE LETTER PLATE LIBRARY (owner reorganization 2026-08-07): the
    # table names a plate per glyph, relative to `dial.LETTER_ART_DIR` —
    # every jewel, crown word, crown location and crown digit is drawn
    # from one of these (`render.letter_plates`).
    for plates in constants.LETTER_PLATE_FILES.values():
        for name in plates:
            add(dial.LETTER_ART_DIR / name)
    return found


def _ledgered_dirs() -> set[str]:
    """The staging ledger's §Art Outside The Weeks table — first cell of
    every row that names a path under assets/."""
    if not _LEDGER_PATH.exists():
        return set()
    out = set()
    for line in _LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cell = line.split("|")[1].strip().strip("`")
        if "/" in cell and not cell.startswith("-"):
            out.add(cell)
    return out


def _art_dirs() -> list[Path]:
    return [
        # `.webp` since THE ART BAKERY (2026-08-12) — a `*.png` glob
        # here would have found no directory at all in the baked areas
        # and passed this whole guard in silence.
        d for d in sorted(_ASSETS.rglob("*"))
        if d.is_dir() and any(paths.is_art_file(f) for f in d.glob("*"))
    ]


# ═══════════════════════════ THE GUARD ═══════════════════════════


def test_every_art_folder_is_resolved_named_or_owed():
    """The whole tree, one sentence per folder: the program reaches it,
    a named reader builds its path, or the ledger owes it."""
    resolved = _resolved_dirs()
    ledgered = _ledgered_dirs()
    offenders = []
    for directory in _art_dirs():
        rel = directory.relative_to(_ASSETS).as_posix()
        if directory.resolve() in resolved or rel in ledgered:
            continue
        if any(_matches_pattern(rel, pattern) for pattern in RESOLVED_ELSEWHERE):
            continue
        offenders.append(f"{rel} ({len(list(directory.glob('*.png')))} plates)")
    assert offenders == [], (
        "ART SITS UNSEEN (project CLAUDE.md -> THE THEME COMPLETION LAW, "
        "widened to the whole tree by the owner 2026-08-05): nothing in "
        "the program can draw these plates. Wire them, name the reader in "
        "RESOLVED_ELSEWHERE, or record the debt in the ledger's §Art "
        "Outside The Weeks — but never leave them silent:\n  "
        + "\n  ".join(offenders)
    )


def test_the_elsewhere_list_has_no_stale_entries():
    """RESOLVED_ELSEWHERE may only SHRINK: an entry whose folders have
    vanished is a claim about nothing, and a claim about nothing is how
    a list stops being read."""
    live = {d.relative_to(_ASSETS).as_posix() for d in _art_dirs()}
    stale = [
        pattern for pattern in RESOLVED_ELSEWHERE
        if not any(_matches_pattern(rel, pattern) for rel in live)
    ]
    assert stale == [], (
        "these RESOLVED_ELSEWHERE entries match no folder on disk — "
        "delete them: " + ", ".join(sorted(stale))
    )


def test_the_ledger_owes_only_what_exists():
    """A debt row for art that is gone (or that has since been wired) is
    a debt nobody owes — the ledger must shrink as the work lands."""
    live = {d.relative_to(_ASSETS).as_posix() for d in _art_dirs()}
    resolved = {
        d.relative_to(_ASSETS).as_posix()
        for d in _resolved_dirs() if d.is_dir()
    }
    stale = [
        rel for rel in _ledgered_dirs()
        if rel.startswith(("archetypes/", "calendars/", "celestial/",
                           "instrument/", "weeks/"))
        and (rel not in live or rel in resolved)
    ]
    assert stale == [], (
        "the ledger owes what is already wired or no longer exists — "
        "delete these rows: " + ", ".join(sorted(stale))
    )
