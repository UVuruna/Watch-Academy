"""CLI for the metal transformer — one file, or the owner's test plates.

    python -m recolor IN.png --source bronze --target gold --out OUT.png
    python -m recolor --plates "UV/color transformer" --source bronze

The second form is the verification loop: every plate in the folder is
rendered to every target, a contact sheet is written beside them and the
metrics table is printed, so a change is judged on numbers (Guideline
#1). Pillow lives here and in `preview.py` only; the algorithm core
stays numpy-only.
"""

import argparse
import sys
from pathlib import Path

from recolor import preview, recipe as recipe_module
from recolor.transform import recolor

DEFAULT_TARGETS = ("gold", "silver", "bronze")
DEFAULT_OUT = Path("research/recolor_preview")


def _crop(text: str | None) -> tuple[int, int, int, int] | None:
    if not text:
        return None
    parts = [int(v) for v in text.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("crop wants x0,y0,x1,y1")
    return tuple(parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="recolor", description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, help="a single PNG")
    parser.add_argument("--plates", type=Path, help="a folder of test plates")
    parser.add_argument("--source", default="bronze", help="the metal drawn")
    parser.add_argument("--target", help="one target metal (single-file mode)")
    parser.add_argument(
        "--targets", default=",".join(DEFAULT_TARGETS),
        help="comma-separated targets for --plates",
    )
    parser.add_argument("--out", type=Path, help="output file or folder")
    parser.add_argument(
        "--mask", default="chroma", choices=("chroma", "alpha"),
        help="chroma for art mixing metal with stone, alpha for glyphs",
    )
    parser.add_argument(
        "--crop", help="x0,y0,x1,y1 detail window to report separately",
    )
    parser.add_argument(
        "--only", help="substring a plate's filename must contain",
    )
    parser.add_argument(
        "--presets", type=Path, default=recipe_module.PRESETS,
        help="an alternative metals.json",
    )
    args = parser.parse_args(argv)

    recipe = recipe_module.load(args.presets)
    crop = _crop(args.crop)

    if args.plates:
        out_dir = args.out or DEFAULT_OUT
        plates = sorted(
            path for path in args.plates.glob("*.png")
            if not path.stem.endswith("- sheet")
            and (not args.only or args.only in path.stem)
        )
        if not plates:
            print(f"no plates in {args.plates}", file=sys.stderr)
            return 1
        targets = [name.strip() for name in args.targets.split(",")]
        print(preview.HEADER)
        print("-" * len(preview.HEADER))
        for plate in plates:
            for row in preview.run(
                plate, args.source, targets, recipe, out_dir,
                mask_mode=args.mask, crop=crop,
            ):
                print(row.row())
            print()
        print(f"wrote variants and contact sheets to {out_dir}")
        return 0

    if not args.image or not args.target:
        parser.error("give an IMAGE with --target, or --plates")

    rgba = preview.load_rgba(args.image)
    result = recolor(
        rgba, args.source, args.target, recipe,
        mask_mode=args.mask, image_key=args.image.stem,
    )
    out = args.out or args.image.with_name(
        f"{args.image.stem} - {args.target}.png"
    )
    preview.save_rgba(result, out)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
