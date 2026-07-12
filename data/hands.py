"""Hand packs (owner spec 2026-07-12): a folder of hours/minutes/
seconds images pointing UP plus hands.json — the display name, the
per-hand rotation PIVOT (x from the left, null = the image middle;
y in pixels FROM THE BOTTOM) and the bottom-up z_order. Bundled packs
ship in assets/hands/; the user's own live beside the settings file.
Validation is loud (Rule #1): the offending pack is always named.
"""

import json
from pathlib import Path

from config import paths

HAND_NAMES = ("hours", "minutes", "seconds")
_IMAGE_SUFFIXES = (".png", ".svg")


def user_hands_dir() -> Path:
    """Where the Settings builder writes the user's packs."""
    return paths.settings_path().parent / "hands"


def _load_pack(directory: Path) -> tuple[str, dict]:
    meta_path = directory / "hands.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"hand pack {directory}: broken hands.json: {error}")
    name = meta.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"hand pack {directory}: missing 'name'")
    files: dict[str, Path] = {}
    pivots: dict[str, tuple[float | None, float]] = {}
    for hand in HAND_NAMES:
        for suffix in _IMAGE_SUFFIXES:
            candidate = directory / f"{hand}{suffix}"
            if candidate.exists():
                files[hand] = candidate
                break
        else:
            raise ValueError(f"hand pack {name!r}: {hand} image missing")
        pivot = meta.get("pivot", {}).get(hand)
        if not isinstance(pivot, dict) or "y" not in pivot:
            raise ValueError(f"hand pack {name!r}: pivot for {hand} missing")
        x = pivot.get("x")
        if x is not None and not isinstance(x, (int, float)):
            raise ValueError(f"hand pack {name!r}: pivot x for {hand} not a number")
        pivots[hand] = (x, float(pivot["y"]))
    z_order = tuple(meta.get("z_order", HAND_NAMES))
    if sorted(z_order) != sorted(HAND_NAMES):
        raise ValueError(f"hand pack {name!r}: z_order must list {HAND_NAMES}")
    return name.strip(), {
        "dir": directory, "files": files, "pivots": pivots, "z_order": z_order,
    }


def hand_packs() -> dict[str, dict]:
    """name → pack for every bundled + user pack (duplicates are loud)."""
    packs: dict[str, dict] = {}
    roots = [paths.assets_dir() / "hands", user_hands_dir()]
    for root in roots:
        if not root.exists():
            continue
        for directory in sorted(root.iterdir()):
            if not (directory / "hands.json").exists():
                continue
            name, pack = _load_pack(directory)
            if name in packs:
                raise ValueError(f"hand pack name {name!r} appears twice")
            packs[name] = pack
    return packs
