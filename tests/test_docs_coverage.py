"""THE DOCS LAW's first guard — MD-First 2.0 coverage.

Root `rules/DOCS.md` -> Tiers: docs are written where they carry
information, never for ritual. Every source file has exactly the docs its
TIER requires, and nothing more:

| Tier | Obligation |
|------|-----------|
| **Trivial** — glue, `__init__`, re-exports, plain wiring | one line in `___folder.md`, NO own docs |
| **Standard** — ordinary module | `__about/{name}.md` |
| **Algorithmic** — real algorithm, GUI window/widget, config/data table, protocol | `__about/{name}.md` **+** `__flow/{name}.md` |
| `tests/` | `___tests.md` folder doc only |

The two frozensets below ARE the tier assignment for this project.
Changing a file's tier means editing this test in the same commit — that
is the point: a tier is a decision, not an accident. A NEW source file is
Standard by default and must therefore gain an `__about/` doc, or be
named in `TRIVIAL`.

The guard also refuses the two shapes MD-First 2.0 replaced:
beside-script docs (`foo.md` sitting next to `foo.py`, which drowned this
project's folders) and orphan docs (an `__about/`/`__flow/` file whose
script is gone).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIR_NAMES = {
    ".git", ".claude", ".pytest_cache", "__pycache__",
    ".venv", "venv", "node_modules", "build", "dist", "UV",
}

# Test modules and their helpers: the folder doc `___tests.md` is the
# whole obligation (rules/DOCS.md -> Tiers). `test_*.py` and `conftest.py`
# are skipped wherever they live — `research/ephemeris/` keeps one of its
# own, described in that folder's doc.
DOC_EXEMPT_FOLDERS = {"tests"}

# ---------------------------------------------------------------- tiers
# TRIVIAL — package markers, re-export glue and plain wiring. These get
# ONE LINE in their `___folder.md` and no file of their own. Deleting a
# useless doc is progress, not loss.
TRIVIAL = frozenset({
    "app/__init__.py",
    "app/encyclopedia/__init__.py",
    "app/settings_dialog/__init__.py",
    "config/__init__.py",
    "core/__init__.py",
    "data/__init__.py",
    "data/_io.py",
    "recolor/__init__.py",
    "render/__init__.py",
    "render/layers/__init__.py",
    "skins/__init__.py",
})

# ALGORITHMIC — a real algorithm, a GUI window/widget, a config/data
# table or a protocol. These carry `__flow/` too: the logic drawn as a
# Mermaid diagram plus language-neutral pseudocode (a GUI file sketches
# its zones; a config file draws its section/key tree).
FLOW_REQUIRED = frozenset({
    "app/controller.py",
    "app/design_window.py",
    "app/encyclopedia/builders.py",
    "app/encyclopedia/cards.py",
    "app/encyclopedia/dialog.py",
    "app/encyclopedia/home.py",
    "app/encyclopedia/pages.py",
    "app/encyclopedia/reader.py",
    "app/encyclopedia/text.py",
    "app/encyclopedia/themes.py",
    "app/encyclopedia/tree.py",
    "app/encyclopedia_warm.py",
    "app/fast_travel_flash.py",
    "app/legend_popup.py",
    "app/native.py",
    "app/observatory.py",
    "app/pointer_theme.py",
    "app/report.py",
    "app/scheduler.py",
    "app/settings_dialog/colors_section.py",
    "app/settings_dialog/custom_art_section.py",
    "app/settings_dialog/dialog.py",
    "app/settings_dialog/display_section.py",
    "app/settings_dialog/language_system_section.py",
    "app/settings_dialog/location_section.py",
    "app/settings_dialog/themes_section.py",
    "app/settings_store.py",
    "app/slot_theme.py",
    "app/theme.py",
    "app/time_travel.py",
    "app/warm.py",
    "app/weekday_theme_grid.py",
    "app/widget.py",
    "config/archetypes.py",
    "config/calendar_mounts.py",
    "config/constants.py",
    "config/continents.py",
    "config/cube.py",
    "config/defaults.py",
    "config/dial.py",
    "config/doctrine.py",
    "config/encyclopedia_tree.py",
    "config/encyclopedia_ui.py",
    "config/glow.py",
    "config/palette.py",
    "config/pantheon.py",
    "config/paths.py",
    "config/profiling.py",
    "config/shortcuts.py",
    "config/taxonomy.py",
    "config/ui_text.py",
    "core/angles.py",
    "core/ascendant.py",
    "core/blue_moon.py",
    "core/clock_state.py",
    "core/continents.py",
    "core/cube_seating.py",
    "core/deep_time.py",
    "core/moon.py",
    "core/motto.py",
    "core/sun.py",
    "core/year_wheel.py",
    "data/cube_model_export.py",
    "data/deep_time.py",
    "data/locations.py",
    "data/observatory.py",
    "data/rings.py",
    "data/symbolism.py",
    "data/translations.py",
    "main.py",
    "recolor/filters.py",
    "recolor/mask.py",
    "recolor/ramp.py",
    "recolor/recipe.py",
    "recolor/space.py",
    "recolor/tone.py",
    "recolor/transform.py",
    "render/archetype_geometry.py",
    "render/art_warm.py",
    "render/asset_recolor.py",
    "render/asset_variants.py",
    "render/assets.py",
    "render/calendar_mount.py",
    "render/canon_diagrams.py",
    "render/compositor.py",
    "render/context.py",
    "render/cube_diagrams.py",
    "render/cube_preview3d.py",
    "render/daylight.py",
    "render/eclipse_glow.py",
    "render/instrument_diagrams.py",
    "render/layers/archetype.py",
    "render/layers/background.py",
    "render/layers/center_body.py",
    "render/layers/hand.py",
    "render/layers/hover_lift.py",
    "render/layers/ring.py",
    "render/layers/slot.py",
    "render/layers/star.py",
    "render/layers/weekday.py",
    "render/layers/year_marker.py",
    "render/ninths.py",
    "render/painting.py",
    "render/shapes.py",
    "render/skin_geometry.py",
    "render/slot_layout.py",
    "render/subdial.py",
    "render/weekday_body.py",
    "research/build_relocation_manifest.py",
    "research/build_roster.py",
    "research/ephemeris/ephemeris_common.py",
    "research/ephemeris/extract.py",
    "research/ephemeris/extract_eclipses.py",
    "research/ephemeris/long_envelope.py",
    "research/merge_articles.py",
    "research/migrate_tree_law.py",
    "research/pascalcase_stems.py",
    "research/rewrite_sheet_paths.py",
    "research/seating_preview.py",
    "setup/make_deep_time.py",
    "setup/make_observatory.py",
    "skins/manifest.py",
})


def _source_files() -> list[Path]:
    out = []
    for path in sorted(PROJECT_ROOT.rglob("*.py")):
        rel = path.relative_to(PROJECT_ROOT)
        if any(part in EXCLUDED_DIR_NAMES for part in rel.parts):
            continue
        if rel.parts[0] in DOC_EXEMPT_FOLDERS:
            continue
        if path.name.startswith("test_") or path.name == "conftest.py":
            continue          # test modules everywhere: folder doc only
        out.append(path)
    return out


def _code_folders() -> set[Path]:
    """Folders holding at least one NON-trivial source file."""
    return {
        path.parent
        for path in _source_files()
        if path.relative_to(PROJECT_ROOT).as_posix() not in TRIVIAL
    }


def test_every_code_folder_has_its_folder_doc():
    """`___folder.md` — the triple-underscore entry point that sorts
    first and orients an agent before it reads any code."""
    missing = []
    for folder in sorted(_code_folders()):
        if folder == PROJECT_ROOT:
            continue                      # the project root's entry is README.md
        doc = folder / f"___{folder.name}.md"
        if not doc.exists():
            missing.append(doc.relative_to(PROJECT_ROOT).as_posix())
    for name in sorted(DOC_EXEMPT_FOLDERS):
        doc = PROJECT_ROOT / name / f"___{name}.md"
        if not doc.exists():
            missing.append(doc.relative_to(PROJECT_ROOT).as_posix())
    assert not missing, (
        "THE DOCS LAW (rules/DOCS.md -> Structure): these folder docs are "
        "missing:\n  " + "\n  ".join(missing)
    )


def test_every_source_file_has_the_docs_its_tier_requires():
    """Standard -> `__about/`; Algorithmic -> `__about/` + `__flow/`."""
    missing = []
    for path in _source_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if rel in TRIVIAL:
            continue
        about = path.parent / "__about" / f"{path.stem}.md"
        if not about.exists():
            missing.append(
                f"{rel} -> {about.relative_to(PROJECT_ROOT).as_posix()} "
                "(Standard tier needs an __about doc; if it is glue, add it "
                "to TRIVIAL in this test)"
            )
        if rel in FLOW_REQUIRED:
            flow = path.parent / "__flow" / f"{path.stem}.md"
            if not flow.exists():
                missing.append(
                    f"{rel} -> {flow.relative_to(PROJECT_ROOT).as_posix()} "
                    "(Algorithmic tier needs a __flow diagram)"
                )
    assert not missing, (
        "THE DOCS LAW (rules/DOCS.md -> Tiers): missing docs:\n  "
        + "\n  ".join(missing)
    )


def test_trivial_files_carry_no_docs_of_their_own():
    """Docs are written where they carry information, never for ritual —
    a Trivial file's whole documentation is its line in `___folder.md`."""
    surplus = []
    for path in _source_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if rel not in TRIVIAL:
            continue
        for kind in ("__about", "__flow"):
            doc = path.parent / kind / f"{path.stem}.md"
            if doc.exists():
                surplus.append(doc.relative_to(PROJECT_ROOT).as_posix())
    assert not surplus, (
        "THE DOCS LAW (rules/DOCS.md -> Tiers): these files are TRIVIAL "
        "tier but carry their own docs — delete the doc, or move the file "
        "out of TRIVIAL in this test:\n  " + "\n  ".join(surplus)
    )


def test_no_flow_doc_without_its_about_doc():
    """`__flow/` shows HOW; it never stands without the `__about/` that
    says WHAT."""
    orphaned = []
    for flow in sorted(PROJECT_ROOT.rglob("__flow/*.md")):
        if any(part in EXCLUDED_DIR_NAMES for part in flow.parts):
            continue
        about = flow.parent.parent / "__about" / flow.name
        if not about.exists():
            orphaned.append(flow.relative_to(PROJECT_ROOT).as_posix())
    assert not orphaned, (
        "THE DOCS LAW: a __flow doc without its __about doc:\n  "
        + "\n  ".join(orphaned)
    )


def test_no_doc_describes_a_script_that_does_not_exist():
    """An orphan doc is a doc that lies — the file it describes is gone."""
    orphans = []
    for kind in ("__about", "__flow"):
        for doc in sorted(PROJECT_ROOT.rglob(f"{kind}/*.md")):
            if any(part in EXCLUDED_DIR_NAMES for part in doc.parts):
                continue
            script = doc.parent.parent / f"{doc.stem}.py"
            if not script.exists():
                orphans.append(doc.relative_to(PROJECT_ROOT).as_posix())
    assert not orphans, (
        "THE DOCS LAW: these docs describe a script that no longer "
        "exists — delete them, or restore the script:\n  " + "\n  ".join(orphans)
    )


def test_no_legacy_beside_script_docs_remain():
    """MD-First 2.0 moved per-file docs into `__about/`/`__flow/`; a
    `foo.md` sitting next to `foo.py` is the old shape that drowned whole
    folders (one `gui/` held 28 scripts + 28 docs = 56 entries)."""
    legacy = []
    for path in _source_files():
        beside = path.with_suffix(".md")
        if beside.exists():
            legacy.append(beside.relative_to(PROJECT_ROOT).as_posix())
    assert not legacy, (
        "THE DOCS LAW (rules/DOCS.md -> Structure): legacy beside-script "
        "docs — move each into its folder's `__about/` (and `__flow/` if "
        "its tier calls for it):\n  " + "\n  ".join(legacy)
    )
