"""THE PARITY LAW's guard (ANDROID.md §parity, LAW #1/#2) — the CONTRACT
PACK on disk must be exactly what `setup/make_contract_pack.py` would
produce right now. A registry edit with no re-export goes RED here,
never silently ships a stale pack to the phone.

Deliberately fast: no astronomy sweep of its own — it calls the SAME
table builders the generator calls (in-memory, no file IO for the
comparison) and only re-derives a handful of golden numbers already
pinned elsewhere in this suite.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]        # desktop/
REPO_ROOT = PROJECT_ROOT.parent
CONTRACT_DIR = REPO_ROOT / "shared" / "contract"
TABLES_DIR = CONTRACT_DIR / "tables"


def _load_generator():
    """Import `setup/make_contract_pack.py` by path — `setup/` carries
    no `__init__.py` (it is a folder of standalone one-time scripts, not
    a package), so this mirrors how an operator runs it directly."""
    path = PROJECT_ROOT / "setup" / "make_contract_pack.py"
    spec = importlib.util.spec_from_file_location("make_contract_pack", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("make_contract_pack", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generator():
    return _load_generator()


@pytest.fixture(scope="module")
def manifest():
    path = CONTRACT_DIR / "manifest.json"
    assert path.exists(), (
        "shared/contract/manifest.json is missing — run "
        "`python desktop/setup/make_contract_pack.py` and commit its output."
    )
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_hashes_match_the_files_on_disk(manifest):
    missing, mismatched = [], []
    for rel, entry in manifest["files"].items():
        target = CONTRACT_DIR / rel
        if not target.exists():
            missing.append(rel)
            continue
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            mismatched.append(rel)
    assert not missing, f"manifest names files absent from disk: {missing}"
    assert not mismatched, (
        f"these pack files changed since the last export (re-run "
        f"make_contract_pack.py): {mismatched}"
    )


def test_manifest_names_pack_version_and_vector_groups(manifest):
    assert manifest["pack_version"]
    assert manifest["created_at"]
    assert manifest["vector_groups"], "manifest must list at least one vector group"
    vectors = json.loads((CONTRACT_DIR / "golden_vectors.json").read_text(encoding="utf-8"))
    assert set(manifest["vector_groups"]) == set(vectors["groups"])


@pytest.mark.parametrize("table_name", [
    "week_themes", "availability", "ring_presets", "pointers",
    "palette_numeral_parity", "encyclopedia_tree",
])
def test_table_export_matches_regenerating_it_in_memory(generator, table_name):
    """Someone edits `config/registry/week.py` (or any other table's
    real source) without re-running the generator: this goes RED,
    because the in-memory rebuild no longer equals the file on disk."""
    on_disk_path = TABLES_DIR / f"{table_name}.json"
    assert on_disk_path.exists(), f"tables/{table_name}.json is missing"
    on_disk = json.loads(on_disk_path.read_text(encoding="utf-8"))
    rebuilt = generator.TABLE_BUILDERS[table_name]()
    # Round-trip the rebuilt payload through JSON so tuples/enums compare
    # the same way the on-disk (already-JSON) payload does.
    rebuilt_as_json = json.loads(json.dumps(rebuilt, sort_keys=True, ensure_ascii=False))
    assert rebuilt_as_json == on_disk, (
        f"tables/{table_name}.json is stale — its registry source changed "
        f"with no re-export (THE PARITY LAW, ANDROID.md §parity). Run "
        f"`python desktop/setup/make_contract_pack.py`."
    )


def test_golden_vectors_contain_the_named_groups(generator):
    vectors = json.loads(
        (CONTRACT_DIR / "golden_vectors.json").read_text(encoding="utf-8")
    )
    assert set(vectors["groups"]) == set(generator.VECTOR_GROUPS)


def test_belgrade_dst_vectors_match_the_pinned_star_jump():
    """Mirrors `tests/test_sun.py::TestBelgradeDst` — the −4.17 -> +10.76
    deg jump across 2026's spring-forward."""
    vectors = json.loads(
        (CONTRACT_DIR / "golden_vectors.json").read_text(encoding="utf-8")
    )
    by_name = {v["name"]: v for v in vectors["groups"]["belgrade_dst"]}
    before = by_name["belgrade_star_rotation_2026-03-28"]["expected"]["star_rotation_deg"]
    after = by_name["belgrade_star_rotation_2026-03-29"]["expected"]["star_rotation_deg"]
    assert before == pytest.approx(-4.17, abs=0.1)
    assert after == pytest.approx(10.76, abs=0.1)


def test_moon_illumination_vector_matches_the_pinned_reference_moment():
    """Mirrors `tests/test_moon.py::test_reference_moment` — 0.7400 on
    2026-07-07."""
    vectors = json.loads(
        (CONTRACT_DIR / "golden_vectors.json").read_text(encoding="utf-8")
    )
    fraction = vectors["groups"]["moon_illumination"][0]["expected"]["phase_fraction"]
    assert fraction == pytest.approx(0.74, abs=0.01)


def test_mockup_day_vector_matches_the_screenshot_header():
    """Mirrors `tests/test_sun.py::TestMockupDay` — '4:52 - 20:27
    (12:39)' for Belgrade 20.6.2025."""
    vectors = json.loads(
        (CONTRACT_DIR / "golden_vectors.json").read_text(encoding="utf-8")
    )
    expected = vectors["groups"]["mockup_day"][0]["expected"]
    assert expected["sunrise"] in {"04:51", "04:52", "04:53"}
    assert expected["sunset"] in {"20:26", "20:27", "20:28"}


def test_equinoxes_land_exactly_on_the_cardinal_angles():
    """Mirrors `tests/test_year_wheel.py::test_cardinal_points_exact`."""
    vectors = json.loads(
        (CONTRACT_DIR / "golden_vectors.json").read_text(encoding="utf-8")
    )
    by_name = {v["name"]: v for v in vectors["groups"]["equinoxes"]}
    cases = {
        "year_wheel_spring_equinox_2026": 270.0,
        "year_wheel_summer_solstice_2026": 0.0,
        "year_wheel_autumn_equinox_2026": 90.0,
        "year_wheel_winter_solstice_2026": 180.0,
    }
    for name, expected_deg in cases.items():
        actual = by_name[name]["expected"]["year_marker_deg"]
        assert actual == pytest.approx(expected_deg, abs=1e-9)
