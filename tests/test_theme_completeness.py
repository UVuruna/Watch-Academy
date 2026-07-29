"""THE THEME COMPLETION LAW (project `CLAUDE.md`, owner decree
2026-07-29) — enforced, not merely written.

Born from a real, expensive failure: twelve figure casts (429 files)
were generated and correctly placed on disk under `assets/weeks/`, and
not one of them was visible anywhere in the program — never registered
in `constants.WEEKDAY_THEMES`, so the dial's picker never learned they
existed and the Encyclopedia had no page for any of them. The prompt
sheets that produced them wrote "two wiring rounds left for later" into
`research/prompts/COVERAGE.md` and moved on; later never came, and
nothing in the suite could say so (WORKPLAN.md §THE THEME BACKLOG has
the full story).

Two guards, symmetric to each other:

1. `test_no_registered_theme_is_textless` — every theme the dial can
   already SHOW must also be READABLE: its own article set, its own
   blurb set, its own title article and (where it has one) its own
   Ninth article all resolve. This one passes TODAY and must never stop
   passing — a future change that silently drops a theme's text would
   fail it immediately.
2. `test_no_art_sits_unseen` — every theme FOLDER on disk under
   `assets/weeks/` is either a registered `WEEKDAY_THEMES` key or an
   open row in `research/theme_staging.md` (the STAGING LEDGER). This
   one FAILS today with the ledger removed — twelve names, exactly the
   twelve casts CLAUDE.md's law describes — and that failure is the
   whole point: it is the sentence the suite could not say before this
   session. Each completion wave (Sessions 31-33) deletes its own rows
   until the ledger, and this guard's exception list, are both empty.
"""

import re
from pathlib import Path

from config import constants, defaults, pantheon, paths, taxonomy
from data.encyclopedia import EncyclopediaRepository
from data.symbolism import SymbolismRepository

_ROOT = Path(__file__).resolve().parents[1]
_LEDGER_PATH = _ROOT / "research" / "theme_staging.md"

_WEEKDAY_BODIES = (
    "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
)

# The STAGING LEDGER's table rows always open with the folder name alone,
# backticked, in the first cell — `research/theme_staging.md`'s own
# stated contract with this test.
_LEDGER_ROW = re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|", re.MULTILINE)


def _ledger_folders() -> set[str]:
    text = _LEDGER_PATH.read_text(encoding="utf-8")
    return set(_LEDGER_ROW.findall(text))


def _weekday_theme_folders() -> set[str]:
    """Every `assets/weeks/<group>/<folder>` name reachable from a
    registered `constants.WEEKDAY_THEMES` key, read off the already-
    resolved `pantheon.WEEKDAY_THEME_DIRS` (past `THEME_KEY_RENAMES`/
    `THEME_FOLDER` — Rule #5, the same chain `defaults.title_plate_art`
    walks, not reimplemented here). "planets" itself carries no themed
    dir of its own (the skin's default unit) but is reached through
    `planet_signs`/`planets_art`; "continents" steps up to
    `assets/celestial/earth`, outside `assets/weeks/` entirely, and
    contributes no folder here."""
    folders = set()
    for theme in constants.WEEKDAY_THEMES:
        rel = pantheon.WEEKDAY_THEME_DIRS.get(theme)
        if rel is None:
            continue
        parts = rel.split("/")
        if parts[0] == "..":
            if parts[1] == "emblem":
                folders.add(parts[2])
            continue  # "earth" — outside assets/weeks/ entirely
        folders.add(parts[0])
    return folders


def _emblem_only_folders() -> set[str]:
    """The Inner Wheel emblem families wired straight through
    `defaults.EMBLEM_ART_DIRS` / `app.encyclopedia.tree`'s own
    virtues/sins/moods/intelligence family pages rather than through
    `WEEKDAY_THEMES`. "intelligence" is the one member with NO weekday-
    theme entry at all (Gardner's eight intelligences, not a
    six-weekday + dual + ninth roster), so it needs this second,
    already-wired registry to count as "seen"; virtue/sin/mood are
    reachable both ways, which is fine — a set union does not care."""
    return {path.parent.parent.name for path in defaults.EMBLEM_ART_DIRS.values()}


def _look_only_themes() -> set[str]:
    """Dial themes with NO topic card of their own — resolved as a LOOK
    of another topic's card instead (`planets_art` rides the Planets
    card: it is absent from `pantheon.WEEKDAY_THEME_TITLES` on purpose,
    its own comment reading "rides the Planets encyclopedia topic as a
    look", so `app.encyclopedia.tree._build_topics` never calls
    `_weekday_topic` for it in the first place). Reused by
    `test_encyclopedia_tree.py`'s REACHABILITY LAW (Rule #5, one
    source) — a look-only theme has nothing of its own for the Home
    screen to seat, so it is the one documented exception to "every
    registered theme reaches a whole"."""
    return set(constants.WEEKDAY_THEMES) - set(pantheon.WEEKDAY_THEME_TITLES)


def test_no_registered_theme_is_textless():
    """Every key in `constants.WEEKDAY_THEMES` resolves an article set,
    a blurb set, a title article and (where it has a Ninth) a Ninth
    article. Two DOCUMENTED exceptions to the title-article check, both
    real production behavior rather than omissions:

    - `planets_art` never gets its own Encyclopedia topic at all (see
      `_look_only_themes` above).
    - The Inner Wheel emblem themes (virtues/sins/moods) DO get a
      `_weekday_topic` build, but `app.encyclopedia.tree` immediately
      OVERWRITES it with its own family pages
      (`pantheon.WEEKDAY_THEME_TITLES`'s own comment: "their
      ENCYCLOPEDIA topics stay the emblem pages... — the later family
      pass overwrites the weekday topics built from these titles —
      deliberate"), so they never carry a `theme_title` JSON entry by
      design.
    """
    symbolism = SymbolismRepository()
    encyclopedia = EncyclopediaRepository()
    emblem_override = set(defaults.EMBLEM_ART_DIRS) & set(constants.WEEKDAY_THEMES)
    no_own_topic = _look_only_themes()
    title_exempt = emblem_override | no_own_topic

    offenders = []
    for theme in constants.WEEKDAY_THEMES:
        article_set = constants.WEEKDAY_THEME_ARTICLES.get(theme)
        if article_set is None:
            offenders.append(f"{theme}: no WEEKDAY_THEME_ARTICLES entry")
            continue
        blurb_set = constants.WEEKDAY_THEME_BLURBS.get(theme)
        if blurb_set is None:
            offenders.append(f"{theme}: no WEEKDAY_THEME_BLURBS entry")
            continue
        for body in _WEEKDAY_BODIES:
            try:
                symbolism.article(article_set, body)
            except KeyError:
                offenders.append(f"{theme}: missing article {article_set}/{body}")
            if blurb_set not in symbolism.arm_blurbs(body):
                offenders.append(f"{theme}: missing blurb {blurb_set}/{body}")

        if theme not in title_exempt:
            try:
                encyclopedia.theme_title(theme)
            except KeyError:
                offenders.append(f"{theme}: missing theme_title")

        ninth = constants.WEEKDAY_THEME_NINTHS.get(theme)
        if ninth is not None:
            name, _plate = ninth
            try:
                encyclopedia.entry("ninths", name)
            except KeyError:
                offenders.append(f"{theme}: missing ninth article {name!r}")

    assert offenders == [], offenders


def test_no_art_sits_unseen():
    """Every theme FOLDER under `assets/weeks/` is either registered in
    `constants.WEEKDAY_THEMES` or listed in the STAGING LEDGER
    (`research/theme_staging.md`). Without the ledger this fails with
    exactly the twelve casts CLAUDE.md's THEME COMPLETION LAW names —
    that detection power is the deliverable; with it in place (and kept
    accurate as each wave deletes its own rows) the suite stays green."""
    seen = _weekday_theme_folders() | _emblem_only_folders()
    ledgered = _ledger_folders()

    weeks_root = paths.assets_dir() / "weeks"
    offenders = []
    for group_dir in sorted(p for p in weeks_root.iterdir() if p.is_dir()):
        if group_dir.name not in taxonomy.WEEK_GROUPS:
            continue  # tests/test_assets_structure.py's own guard covers this
        for theme_dir in sorted(p for p in group_dir.iterdir() if p.is_dir()):
            if theme_dir.name in seen or theme_dir.name in ledgered:
                continue
            offenders.append(f"{group_dir.name}/{theme_dir.name}")

    assert offenders == [], (
        "art sits unseen — register in constants.WEEKDAY_THEMES or add a "
        "row to research/theme_staging.md: " + ", ".join(offenders)
    )
