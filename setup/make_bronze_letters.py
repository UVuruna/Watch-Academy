"""Pre-render the BRONZE ring letters (owner decision 2026-07-12).

Derives each `<Stem>_bronze.png` from the PRE-RENDERED silver letter
(`make_silver_letters.py` output): the letters are already bright, so
the medallion recipe (+brightness) would blow their detail out —
instead a SLIGHT DARKENING then a straight multiply with the bronze
tint (owner direction after the first preview round). Bronze is
ordinary art afterwards; the app never recolors letters at runtime.
Rerun after make_silver_letters.py whenever a letter master changes.

    python setup/make_bronze_letters.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  # noqa: E402

from config import constants, defaults  # noqa: E402


def _bronzed(source: Path) -> Image.Image:
    img = Image.open(source).convert("RGBA")
    alpha = img.getchannel("A")
    # The silver letters are grayscale — one channel is the luminance.
    gray = img.getchannel("R")
    brightness = defaults.BRONZE_LETTER_BRIGHTNESS
    tint = defaults.BRONZE_LETTER_TINT.lstrip("#")
    color = tuple(int(tint[i:i + 2], 16) for i in (0, 2, 4))
    lut = [max(0, min(255, round(v * brightness))) for v in range(256)]
    gray = gray.point(lut)
    out = Image.merge("RGB", [
        gray.point(lambda v, c=c: v * c // 255) for c in color
    ]).convert("RGBA")
    out.putalpha(alpha)
    return out


def main() -> None:
    for letter, filename in sorted(constants.RING_LETTER_FILES.items()):
        stem = Path(filename).stem
        source = defaults.RING_LETTER_ART_DIR / f"{stem}_silver.png"
        target = defaults.RING_LETTER_ART_DIR / f"{stem}_bronze.png"
        bronze = _bronzed(source)
        bronze.save(target)
        print(f"{letter}: {source.name} -> {target.name} "
              f"({bronze.width}x{bronze.height})")


if __name__ == "__main__":
    main()
