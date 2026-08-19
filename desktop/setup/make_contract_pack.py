"""THE BAKERY — CONTRACT PACK generator (ANDROID.md Phase 1).

One-time, rerunnable (owner ballot verdict 2026-08-11/12): builds
`shared/contract/` — golden vectors for the future Kotlin `:core` port
plus JSON exports of the config registry tables the phone must read
instead of re-typing. Run from the repo root:

    python desktop/setup/make_contract_pack.py

Every golden vector is produced by IMPORTING the real desktop `core`
(pure, no Qt) and calling its actual functions — never typed by hand.
Every table export calls the actual registry the app itself reads, so a
registry edit with no re-export is exactly what `tests/
test_contract_pack.py` (THE PARITY LAW's guard) catches.

Outputs (into shared/contract/):
  * golden_vectors.json — named vector groups, each entry carrying its
    own `inputs`, `expected` and `tolerance` (ANDROID.md §The Bakery:
    "the port of an algorithm is DONE when its vectors are green").
  * tables/*.json — week_themes, availability, ring_presets, pointers,
    palette_numeral_parity, encyclopedia_tree. A table with no single
    clean source (none found this round) is skipped and recorded in
    PARITY.md instead of invented.
  * manifest.json — pack_version, created-at (from `git log -1`, never
    wall clock), sha256 per exported file, the vector group names.
"""

import hashlib
import json
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]     # desktop/
REPO_ROOT = PROJECT_ROOT.parent
SHARED = REPO_ROOT / "shared"
CONTRACT_DIR = SHARED / "contract"
TABLES_DIR = CONTRACT_DIR / "tables"

sys.path.insert(0, str(PROJECT_ROOT))

import astral                                            # noqa: E402

from config import dial                                    # noqa: E402
from config.registry import availability as availability_registry  # noqa: E402
from config.registry import pointers as pointers_registry  # noqa: E402
from config.registry.week import WEEK                     # noqa: E402
from config import encyclopedia_tree                       # noqa: E402
from config import palette                                 # noqa: E402
from core import angles                                    # noqa: E402
from core.moon import illumination, phase_fraction         # noqa: E402
from core.sun import compute_sun_day                       # noqa: E402
from core.year_wheel import year_marker_angle               # noqa: E402
from data.locations import LocationRepository               # noqa: E402
from data.moon_phases import MoonPhaseRepository             # noqa: E402
from data.rings import _bundled_presets                       # noqa: E402
from data.seasons import SeasonsRepository                     # noqa: E402

PACK_VERSION = "1"


# ═══════════════════════════ GOLDEN VECTORS ═══════════════════════════
# Each function below returns a list of vector dicts:
#   {"name": ..., "inputs": {...}, "expected": {...}, "tolerance": {...}}
# mirroring the exact golden values `desktop/tests/test_sun.py`,
# `test_angles.py`, `test_moon.py` and `test_year_wheel.py` pin.


def _belgrade_record():
    matches = LocationRepository().find_city("Belgrade")
    serbian = [record for record in matches if "Serbia" in record.path]
    assert serbian, "Belgrade (Serbia) must exist in the locations database"
    return serbian[0]


def _sun_day(observer: astral.Observer, tz: str, on_date: date):
    return compute_sun_day(observer, on_date, ZoneInfo(tz))


def _hms(value: datetime | None) -> str | None:
    return None if value is None else value.strftime("%H:%M")


def group_belgrade_dst() -> list[dict]:
    """Belgrade's DST star jump, −4.17° → +10.76° (test_sun.py
    TestBelgradeDst) — the single vector group ANDROID.md names first."""
    belgrade = _belgrade_record()
    observer = astral.Observer(latitude=belgrade.latitude, longitude=belgrade.longitude)
    vectors = []
    for on_date, expected_deg in ((date(2026, 3, 28), -4.17), (date(2026, 3, 29), 10.76)):
        sun_day = _sun_day(observer, belgrade.timezone, on_date)
        vectors.append({
            "name": f"belgrade_star_rotation_{on_date.isoformat()}",
            "inputs": {
                "latitude": belgrade.latitude, "longitude": belgrade.longitude,
                "timezone": belgrade.timezone, "date": on_date.isoformat(),
            },
            "expected": {
                "regime": sun_day.regime.value,
                "star_rotation_deg": angles.star_rotation_deg(sun_day.noon),
            },
            "tolerance": {"star_rotation_deg": 0.1},
        })
        assert vectors[-1]["expected"]["star_rotation_deg"] == pytest_approx(expected_deg, 0.1)
    return vectors


def pytest_approx(expected: float, tol: float):
    """Tiny stand-in so the generator self-checks against the desktop
    suite's own pinned numbers without importing pytest (a runtime dep
    only `tests/` needs)."""
    class _Approx:
        def __eq__(self, other):
            return abs(other - expected) <= tol
    return _Approx()


def group_tromso_regimes() -> list[dict]:
    """The four Tromsø/Longyearbyen daylight regimes (test_sun.py
    TestDaylightRegimes)."""
    tromso = astral.Observer(latitude=69.6489, longitude=18.9551)
    longyearbyen = astral.Observer(latitude=78.2232, longitude=15.6267)
    oslo_tz = "Europe/Oslo"
    cases = [
        ("tromso_twilight_only_january", tromso, oslo_tz, date(2026, 1, 15)),
        ("tromso_white_nights_may", tromso, oslo_tz, date(2026, 5, 10)),
        ("tromso_polar_day_late_may", tromso, oslo_tz, date(2026, 5, 25)),
        ("longyearbyen_polar_night", longyearbyen, oslo_tz, date(2026, 12, 21)),
    ]
    vectors = []
    for name, observer, tz, on_date in cases:
        sun_day = _sun_day(observer, tz, on_date)
        vectors.append({
            "name": name,
            "inputs": {
                "latitude": observer.latitude, "longitude": observer.longitude,
                "timezone": tz, "date": on_date.isoformat(),
            },
            "expected": {
                "regime": sun_day.regime.value,
                "dawn": _hms(sun_day.dawn), "sunrise": _hms(sun_day.sunrise),
                "sunset": _hms(sun_day.sunset), "dusk": _hms(sun_day.dusk),
                "noon": _hms(sun_day.noon),
                "star_rotation_deg": angles.star_rotation_deg(sun_day.noon),
            },
            "tolerance": {"clock_minutes": 0, "star_rotation_deg": 0.1},
        })
    return vectors


def group_moon_illumination() -> list[dict]:
    """The reference moment 2026-07-07 12:00 UTC: interpolated fraction
    0.7400 (test_moon.py test_reference_moment)."""
    window = MoonPhaseRepository().moon_window(2026)
    when = datetime(2026, 7, 7, 12, 0, tzinfo=timezone.utc)
    return [{
        "name": "moon_phase_fraction_2026_07_07",
        "inputs": {"instant_utc": when.isoformat()},
        "expected": {
            "phase_fraction": phase_fraction(when, window),
            "analytic_illumination": illumination(when),
        },
        "tolerance": {"phase_fraction": 0.01, "analytic_illumination": 0.006},
    }]


def group_mockup_day() -> list[dict]:
    """The design screenshot header for 20.6.2025: '4:52 - 20:27
    (12:39)' (test_sun.py TestMockupDay + test_year_wheel.py
    test_mockup_day_earth_near_top)."""
    belgrade = _belgrade_record()
    observer = astral.Observer(latitude=belgrade.latitude, longitude=belgrade.longitude)
    on_date = date(2025, 6, 20)
    sun_day = _sun_day(observer, belgrade.timezone, on_date)
    anchors = SeasonsRepository().year_anchors(2025)
    earth_angle = year_marker_angle(
        datetime(2025, 6, 20, 14, 34, tzinfo=timezone.utc), anchors,
    )
    return [{
        "name": "mockup_day_belgrade_2025_06_20",
        "inputs": {
            "latitude": belgrade.latitude, "longitude": belgrade.longitude,
            "timezone": belgrade.timezone, "date": on_date.isoformat(),
        },
        "expected": {
            "sunrise": _hms(sun_day.sunrise), "sunset": _hms(sun_day.sunset),
            "noon": _hms(sun_day.noon),
            "year_marker_deg_near_top_at_14_34_utc": earth_angle,
        },
        "tolerance": {"clock_minutes": 1, "year_marker_deg_from_0_or_360": 2.0},
    }]


def group_equinoxes() -> list[dict]:
    """Every 2026 cardinal instant lands EXACTLY on 0/90/180/270
    (test_year_wheel.py test_cardinal_points_exact/
    test_exact_anchor_instants_including_last)."""
    anchors = SeasonsRepository().year_anchors(2026)
    names = ("prev_winter_solstice", "spring_equinox", "summer_solstice",
             "autumn_equinox", "winter_solstice", "next_spring_equinox")
    vectors = []
    for name, instant, expected_angle in zip(names, anchors.instants, anchors.angles):
        vectors.append({
            "name": f"year_wheel_{name}_2026",
            "inputs": {"instant_utc": instant.isoformat()},
            "expected": {"year_marker_deg": expected_angle % 360.0},
            "tolerance": {"year_marker_deg": 1e-9},
        })
    return vectors


def group_hand_angles() -> list[dict]:
    """Hour hand 1 rev/24h (`angles.time_to_dial_angle`), minute hand
    1 rev/h (`angles.minute_hand_angle`), DIAL_OFFSET_DEG=180 — a dozen
    times across the day (test_angles.py test_dial_angle_quadrants /
    test_minute_hand_full_hour_revolution)."""
    from datetime import time as dtime

    samples = [
        dtime(0, 0, 0), dtime(2, 15, 0), dtime(4, 30, 0), dtime(6, 0, 0),
        dtime(8, 45, 0), dtime(10, 0, 0), dtime(12, 0, 0), dtime(14, 30, 0),
        dtime(16, 0, 0), dtime(18, 0, 0), dtime(20, 15, 0), dtime(21, 0, 0),
    ]
    vectors = []
    for t in samples:
        vectors.append({
            "name": f"hand_angles_{t.strftime('%H%M%S')}",
            "inputs": {"time": t.strftime("%H:%M:%S")},
            "expected": {
                "hour_hand_dial_angle_deg": angles.time_to_dial_angle(t),
                "minute_hand_angle_deg": angles.minute_hand_angle(t),
            },
            "tolerance": {"hour_hand_dial_angle_deg": 1e-9, "minute_hand_angle_deg": 1e-9},
        })
    return vectors


def group_hexagram_rotation() -> list[dict]:
    """The hexagram rotation formula, `(noon_secs - 43200) / 240`
    (test_angles.py test_star_rotation_sign_convention) — direct
    formula vectors, independent of any real sunrise/sunset."""
    cases = [
        (datetime(2026, 7, 7, 11, 0, 0), -15.0),
        (datetime(2026, 7, 7, 12, 0, 0), 0.0),
        (datetime(2026, 7, 7, 13, 0, 0), 15.0),
        (datetime(2026, 7, 7, 11, 30, 0), -7.5),
        (datetime(2026, 7, 7, 12, 45, 0), 11.25),
    ]
    vectors = []
    for solar_noon, expected_deg in cases:
        vectors.append({
            "name": f"hexagram_rotation_{solar_noon.strftime('%H%M%S')}",
            "inputs": {"solar_noon_local_time": solar_noon.strftime("%H:%M:%S")},
            "expected": {"star_rotation_deg": angles.star_rotation_deg(solar_noon)},
            "tolerance": {"star_rotation_deg": 1e-9},
        })
        assert vectors[-1]["expected"]["star_rotation_deg"] == pytest_approx(expected_deg, 1e-9)
    return vectors


VECTOR_GROUPS = {
    "belgrade_dst": group_belgrade_dst,
    "tromso_regimes": group_tromso_regimes,
    "moon_illumination": group_moon_illumination,
    "mockup_day": group_mockup_day,
    "equinoxes": group_equinoxes,
    "hand_angles": group_hand_angles,
    "hexagram_rotation": group_hexagram_rotation,
}


def build_golden_vectors() -> dict:
    return {
        "meta": {
            "what": "Golden test vectors for the future Kotlin :core port "
                    "(ANDROID.md Phase 1). Every value is computed by "
                    "calling the real desktop core, never typed by hand. "
                    "A group is DONE on the Kotlin side when its vectors "
                    "are green.",
            "dial_offset_deg": dial.DIAL_OFFSET_DEG,
            "seconds_per_day": dial.SECONDS_PER_DAY,
            "seconds_per_hour": dial.SECONDS_PER_HOUR,
            "hexagram_formula": "(noon_secs - 43200) / 240",
        },
        "groups": {name: builder() for name, builder in VECTOR_GROUPS.items()},
    }


# ═══════════════════════════ TABLE EXPORTS ═══════════════════════════
def build_week_themes() -> dict:
    """`config.registry.week.WEEK` verbatim — theme keys, display names,
    seats/members/sunday/ninth/pantheon, category via `MENU`. Tuples
    become JSON arrays; the `COMPUTED` sentinel travels as its own
    string (`config.registry.sentinel.COMPUTED`) — the Continents' stems
    are computed at RENDER time on both platforms, never frozen here."""
    from config.registry import week as week_module

    return {
        "menu_top": list(week_module.MENU_TOP),
        "menu": [
            {"group": group, "themes": list(themes)}
            for group, themes in week_module.MENU
        ],
        "week": WEEK,
    }


def build_availability() -> dict:
    """The sealed base-pack table (`config.registry.availability`) —
    the ONE source ANDROID.md's Base Pack Agreement names."""
    return {
        "base_theme_keys": sorted(availability_registry.BASE_THEME_KEYS),
        "locked_theme_keys": sorted(availability_registry.LOCKED_THEME_KEYS),
        "availability": dict(sorted(availability_registry.AVAILABILITY.items())),
    }


def build_ring_presets() -> dict:
    """The bundled ring cards, straight from `data.rings._bundled_presets()`
    — the same raw list `data.rings.ring_presets()` validates at
    runtime; `shared/Database/ring_presets.json` is already this table's
    one JSON source, so the export is a direct re-serialization through
    the real loader, not a hand copy."""
    return {"presets": _bundled_presets()}


def build_pointers() -> dict:
    """The pointer permission matrix (`config.registry.pointers`) —
    which theme KINDS each pointer may carry, per SHAPE."""
    return {
        "kinds": list(pointers_registry.KINDS),
        "shapes": [pointers_registry.STAR, pointers_registry.POLYGON],
        "bootstrap_week_theme": pointers_registry.BOOTSTRAP_WEEK_THEME,
        "pointers": pointers_registry.POINTERS,
    }


def build_palette_numeral_parity() -> dict:
    """`config.palette.NUMERAL_PARITY_COLORS` — plain hex strings, the
    one straightforward palette table (owner spec: even/odd wear two
    different styles, not a defect)."""
    return dict(palette.NUMERAL_PARITY_COLORS)


def build_encyclopedia_tree() -> dict:
    """The wholes -> cards STRUCTURE only (`config.encyclopedia_tree`) —
    no article bodies, exactly the deliverable asked for. The phone's
    Compose reader still reads the same three-level model from the same
    `encyclopedia.json`; this table is the SHAPE of the tree, not its
    text."""
    return {
        "wholes": [
            {
                "key": whole.key, "title": whole.title,
                "accent": whole.accent, "themes": list(whole.themes),
            }
            for whole in encyclopedia_tree.WHOLES
        ],
        "theme_to_whole": encyclopedia_tree.THEME_TO_WHOLE,
        "variant_sources": {
            key: {"title": title, "variants": [list(pair) for pair in variants]}
            for key, (title, variants) in encyclopedia_tree.VARIANT_SOURCES.items()
        },
        "topic_aliases": {
            key: list(value) for key, value in encyclopedia_tree.TOPIC_ALIASES.items()
        },
        "cube_topics": [list(entry) for entry in encyclopedia_tree.CUBE_TOPICS],
    }


TABLE_BUILDERS = {
    "week_themes": build_week_themes,
    "availability": build_availability,
    "ring_presets": build_ring_presets,
    "pointers": build_pointers,
    "palette_numeral_parity": build_palette_numeral_parity,
    "encyclopedia_tree": build_encyclopedia_tree,
}


# ═══════════════════════════ WRITE + MANIFEST ═══════════════════════════
def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _created_at() -> str:
    """The last commit's own timestamp — never wall clock (root
    CLAUDE.md's honesty rule: no timestamp claims what git cannot
    verify)."""
    return subprocess.run(
        ["git", "log", "-1", "--format=%cI"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()


def _art_gate() -> None:
    """THE ART SYNC GATE (owner order 2026-08-13).

    A pack built from an out-of-date `shared/assets/` is a pack that
    ships art the masters no longer say, and nothing downstream can
    tell — the manifest hashes the tables, not the pictures. So the
    packaging step asks the bakery first, and REPAIRS rather than
    merely complaining: the owner's order was "proveri ... i ako nije
    uskladi ga" — check, and if it is not in sync, bring it into sync.

    A machine with no `masters/` (any clone but the owner's) reports
    nothing to do and passes, which is correct: its shipped tree is the
    committed one and is already the truth.
    """
    from setup import make_art_bake

    drift = make_art_bake.bake(check=True)
    if drift:
        print(f"art out of sync ({drift} file(s)) — baking before the pack")
        make_art_bake.bake()


def main() -> None:
    _art_gate()
    vectors_payload = build_golden_vectors()
    _write_json(CONTRACT_DIR / "golden_vectors.json", vectors_payload)

    table_files = {}
    for name, builder in TABLE_BUILDERS.items():
        target = TABLES_DIR / f"{name}.json"
        _write_json(target, builder())
        table_files[name] = target

    hashes = {"golden_vectors.json": _sha256(CONTRACT_DIR / "golden_vectors.json")}
    for name, target in table_files.items():
        hashes[f"tables/{name}.json"] = _sha256(target)

    manifest = {
        "pack_version": PACK_VERSION,
        "created_at": _created_at(),
        "vector_groups": sorted(vectors_payload["groups"]),
        "files": {rel: {"sha256": digest} for rel, digest in sorted(hashes.items())},
    }
    _write_json(CONTRACT_DIR / "manifest.json", manifest)

    total_vectors = sum(len(v) for v in vectors_payload["groups"].values())
    print(
        f"contract pack v{PACK_VERSION}: {len(vectors_payload['groups'])} "
        f"vector groups ({total_vectors} vectors), {len(table_files)} "
        f"tables -> {CONTRACT_DIR}"
    )


if __name__ == "__main__":
    sys.exit(main())
