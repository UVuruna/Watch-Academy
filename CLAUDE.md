# Watch Academy

A transparent, frameless 24-hour analog clock widget for the Windows 11
desktop, built around a single dial named **DOMY** — an astronomical
instrument that also teaches: daylight arc, solar noon, moon, seasons, and a
symbolic weekday cast the user can read about in the built-in Encyclopedia.
For the owner first, then anyone who wants a widget instead of a clock.

Inherits the monorepo constitution (`../../CLAUDE.md`) and may only ADD or
TIGHTEN it. Everything longer than a rule lives in `docs/`.

profiles: laptop-avg, pc-low
installable: yes

<!-- The android/ module is a separate build target. Once `uv device` can run
     against its APK, its mandatory profiles are phone-portrait and
     phone-landscape; nothing on the desktop side waits for that. -->

## Stack

- Python 3.13 · PySide6 6.10 · astral 3.2 (+ tzdata) · Windows 11
- Pure-Python astronomy core (no Qt, no wall clock) under `desktop/core/`
- Data: JSON books and SQLite under `shared/Database/`; art under
  `shared/assets/` (WebP, baked — see [Art Pipeline](docs/ART-PIPELINE.md))
- `android/` — the Kotlin phone edition, **Pocket Watch**, not yet founded

## How to run

```
cd desktop
pip install -r requirements.txt
python main.py                     right-click the dial or tray for the menu
python -m core --city NAME --at ISO   eyeball any moment, headless
```

## How to test

```
cd desktop && python -m pytest tests          full suite — ~18 MINUTES
python desktop/tests/run_guards.py --fast     guards, fast (PostToolUse)
python desktop/tests/run_guards.py            guards, FULL (Stop)
python u:/Coding/UVuruna/rules/tools/uv.py shot --all    window screenshots
python shared/research/build_roster.py        regenerate ROSTER.md
```

Run a targeted subset while working; the full suite before committing.
Golden values and the launch/drive recipe: [Runtime
Notes](docs/RUNTIME-NOTES.md).

## Entry points

| Path | Role |
|------|------|
| `desktop/main.py` | process entry, single-instance, wiring |
| `desktop/app/controller.py` | orchestration: windows, tray, menu, ticks |
| `desktop/app/widget.py` | the frameless dial window itself |
| `desktop/render/compositor.py` | stacks the paint layers, hit-testing |
| `desktop/core/` | pure astronomy — no Qt, no wall clock |
| `desktop/setup/make_art_bake.py` | masters → shipped assets |
| `.claude/uv_windows.py` | window registry for `uv shot` |

## Project laws (TIGHTER or EXTRA vs the constitution)

- **The dial convention is fixed** — degrees clockwise from top, noon at the
  top, `DIAL_OFFSET_DEG = 180`; hexagram top vertex at true solar noon; every
  season spans exactly 90°. Never re-derive: [The Dial](docs/DIAL.md).
- **One-way flow** `config → core → data → skins → render → app`; the core
  stays pure (`desktop/tests/test_purity.py`). `render/layers.py` no longer
  exists — never import from it.
- **THE ONE PLATE LAW** — every glyph the program draws is one of the owner's
  plates, recolored; never a font, never a flat colour. A glyph with no plate
  RAISES. `render.letter_plates` is the single door.
- **THE ONE COPY RULE** — every bundled book and database is loaded ONCE per
  process through its `shared_*` accessor; never construct a repository class
  in app code. Two watches may differ only in observer and visual picks.
- **THE RING VOCABULARY** — jewels, numerals, minutes and crown are four
  different things, not variants ([The Dial](docs/DIAL.md#ring-vocabulary)).
- **THE THEME COMPLETION LAW** — a theme ships sheet + articles + dial wiring
  + Encyclopedia seat TOGETHER, or records its debt in the staging ledger in
  the same commit ([Enforcement](docs/ENFORCEMENT.md#theme-completion)).
- **Themes are one registry, casts are entries** — a new theme is a row, not
  a module; the open design brief is [The Theme
  Registry](docs/archive/THEME-REGISTRY.md).
- **Never edit art under `shared/assets/`** and never `rglob("*.png")` over
  it — edit the master and re-bake; use `paths.art_files_under`
  ([Art Pipeline](docs/ART-PIPELINE.md)).
- **English only in UI text during development** — the SR bundle is filled in
  one dedicated session before a release ([Decisions](docs/DECISIONS.md)).
- **`ROSTER.md` is GENERATED** — never hand-edited; regenerate it in the same
  session that changes a theme table or drops art.
- **RATCHETS (structure, zubi baseline, clones) may only SHRINK** — a new
  entry needs the owner's approval in that same session. The current lists
  and what each entry owes: [Enforcement](docs/ENFORCEMENT.md).

## Docs

- [README](README.md) — what it is, the name story, the navigation chain root
- [Decisions](docs/DECISIONS.md) — the owner's sealed verdicts, dated
- [The Dial](docs/DIAL.md) — conventions, architecture, ring vocabulary
- [Art Pipeline](docs/ART-PIPELINE.md) — masters → bakery → assets
- [Enforcement](docs/ENFORCEMENT.md) — the guards and the ratchets
- [Runtime Notes](docs/RUNTIME-NOTES.md) — golden values, closed root causes
- [The DOMY Canon](CANON.md) · [The Cube Canon](CUBE.md) — read before any
  theme, roster, character or naming work
- [Roadmap](ROADMAP.md) · [Work Plan](WORKPLAN.md) — what is left, in order
- [Android Charter](ANDROID.md) — Pocket Watch and THE PARITY LAW
- Folder docs: each code folder's `___folder.md` → `__about/`, `__flow/`

## Open items

- `[~]` The "New Content Specs" (Dozens) section of
  [Restructure](RESTRUCTURE.md) is unconfirmed — the owner owes a yes or no.
- `[~]` The android module has no build yet, so its two phone profiles are
  declared but not exercised.
