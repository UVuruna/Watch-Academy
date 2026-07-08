"""Skin pack checker — `python -m skins.validate <folder>` verifies a
pack without launching the app: manifest syntax, unknown fields, missing
assets (all problems listed at once), then the referenced-assets sweep of
the merged result."""

import argparse
import sys
from pathlib import Path

from config import defaults
from skins import manifest, packs


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m skins.validate",
        description="Validate a DOMY Watch skin pack folder.",
    )
    parser.add_argument("folder", type=Path, help="pack folder containing skin.json")
    args = parser.parse_args()

    try:
        skin = packs.load_pack(args.folder, defaults.DEFAULT_SKIN)
    except packs.SkinValidationError as error:
        print(error)
        return 1
    missing = manifest.missing_assets(skin)
    if missing:
        print(f"Merged skin {skin.name!r} references missing assets:")
        for path in missing:
            print(f"  - {path}")
        return 1
    print(f"OK: skin {skin.name!r} is valid ({args.folder})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
