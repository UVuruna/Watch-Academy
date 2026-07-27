"""The verification harness — a contact sheet AND a metrics table for a
set of plates, so every change to this package is judged on NUMBERS and
not on vibes (Guideline #1). See [Preview](preview.md).

This is a DEV tool: Pillow lives here and in `__main__.py` only, never
in the algorithm core, which stays numpy-only for the Colorize SVG port.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from recolor import filters, mask, ramp, space
from recolor.recipe import Recipe
from recolor.transform import recolor

# Contact-sheet layout.
TILE = 520
LABEL_HEIGHT = 34
PAD = 10
BACKGROUND = (24, 24, 28)
LABEL_COLOR = (232, 232, 238)

# A pixel at or above this counts as blown, at or below as crushed.
CLIP_HIGH = 254 / 255
CLIP_LOW = 1 / 255


@dataclass(frozen=True)
class Metrics:
    """What a plate is worth, in numbers."""
    label: str
    coverage: float
    mean_rgb: tuple[float, float, float]
    dead_blue: float
    clipped: float
    crushed: float
    mean_lightness: float
    lightness_spread: float
    detail_energy: float
    crop_range: float | None

    def row(self) -> str:
        crop = "     -" if self.crop_range is None else f"{self.crop_range:6.4f}"
        return (
            f"{self.label:<26} {self.coverage:6.1f}% "
            f"{self.mean_rgb[0]:.3f}/{self.mean_rgb[1]:.3f}/{self.mean_rgb[2]:.3f} "
            f"{self.dead_blue:6.2f}% {self.clipped:6.2f}% {self.crushed:6.2f}% "
            f"{self.mean_lightness:6.4f} {self.lightness_spread:6.4f} "
            f"{self.detail_energy:7.5f} {crop}"
        )


HEADER = (
    f"{'plate':<26} {'mask':>7} {'mean R/G/B':^17} {'B=0':>7} "
    f"{'blown':>7} {'crush':>7} {'L mean':>6} {'L sd':>6} "
    f"{'detail':>7} {'crop':>6}"
)


def measure(
    label: str, rgba: np.ndarray, weight: np.ndarray, recipe: Recipe,
    crop: tuple[int, int, int, int] | None = None,
) -> Metrics:
    """The metrics table's one row. `weight` is the SOURCE plate's mask,
    passed in unchanged for every variant so all rows describe the same
    set of pixels and are honestly comparable."""
    rgb = rgba[..., :3]
    selected = weight > 0.5
    if not selected.any():
        selected = rgba[..., 3] > 0.0
    picked = rgb[selected]

    value = picked.max(axis=-1)
    lightness = space.linear_to_oklab(
        space.srgb_to_linear(rgb)
    )[..., 0]

    radius = max(
        recipe.tuning.detail_radius_min,
        int(round(min(lightness.shape) * recipe.tuning.detail_radius_fraction)),
    )
    detail = filters.guided_split(
        lightness, radius, recipe.tuning.detail_epsilon
    )[1]

    crop_range = None
    if crop is not None:
        x0, y0, x1, y1 = crop
        window = lightness[y0:y1, x0:x1]
        crop_range = float(
            np.percentile(window, 95) - np.percentile(window, 5)
        )

    return Metrics(
        label=label,
        coverage=100.0 * float(selected.mean()),
        mean_rgb=tuple(float(v) for v in picked.mean(axis=0)),
        dead_blue=100.0 * float((picked[:, 2] <= CLIP_LOW).mean()),
        clipped=100.0 * float((value >= CLIP_HIGH).mean()),
        crushed=100.0 * float((value <= CLIP_LOW).mean()),
        mean_lightness=float(lightness[selected].mean()),
        lightness_spread=float(lightness[selected].std()),
        detail_energy=float(np.abs(detail[selected]).mean()),
        crop_range=crop_range,
    )


def load_rgba(path: Path) -> np.ndarray:
    """A PNG as (H, W, 4) float in [0,1], sRGB-encoded."""
    return np.asarray(
        Image.open(path).convert("RGBA"), dtype=np.float64
    ) / 255.0


def save_rgba(rgba: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(
        (np.clip(rgba, 0.0, 1.0) * 255.0).round().astype(np.uint8), "RGBA"
    ).save(path)


def source_weight(
    rgba: np.ndarray, source: str, recipe: Recipe, mask_mode: str
) -> np.ndarray:
    """The source plate's own metal mask — the pixel set every row of the
    metrics table is measured over."""
    linear = space.srgb_to_linear(rgba[..., :3])
    return mask.metal_weight(
        linear,
        rgba[..., 3],
        ramp.body_color(recipe.metal(source), recipe.tuning.body_position),
        recipe.tuning,
        mask_mode,
    )


def _tile(rgba: np.ndarray, label: str) -> Image.Image:
    """One labelled cell of the contact sheet, composited on the sheet's
    own background so transparency does not read as white."""
    image = Image.fromarray(
        (np.clip(rgba, 0.0, 1.0) * 255.0).round().astype(np.uint8), "RGBA"
    )
    image.thumbnail((TILE, TILE), Image.Resampling.LANCZOS)
    cell = Image.new("RGB", (TILE, TILE + LABEL_HEIGHT), BACKGROUND)
    cell.paste(
        image,
        ((TILE - image.width) // 2, LABEL_HEIGHT + (TILE - image.height) // 2),
        image,
    )
    draw = ImageDraw.Draw(cell)
    draw.text((8, 8), label, fill=LABEL_COLOR, font=ImageFont.load_default(22))
    return cell


def contact_sheet(cells: list[tuple[np.ndarray, str]], path: Path) -> None:
    """Every variant of one plate, side by side, on one image."""
    tiles = [_tile(rgba, label) for rgba, label in cells]
    width = len(tiles) * TILE + (len(tiles) + 1) * PAD
    height = TILE + LABEL_HEIGHT + 2 * PAD
    sheet = Image.new("RGB", (width, height), BACKGROUND)
    for index, tile in enumerate(tiles):
        sheet.paste(tile, (PAD + index * (TILE + PAD), PAD))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)


def run(
    plate: Path, source: str, targets: list[str], recipe: Recipe,
    out_dir: Path, mask_mode: str = "chroma",
    crop: tuple[int, int, int, int] | None = None,
) -> list[Metrics]:
    """Recolor one plate to every target, write the variants and the
    contact sheet, and return the metrics rows (source row first)."""
    rgba = load_rgba(plate)
    weight = source_weight(rgba, source, recipe, mask_mode)

    rows = [measure(f"{plate.stem[:14]} SOURCE", rgba, weight, recipe, crop)]
    cells = [(rgba, f"SOURCE ({source})")]
    for target in targets:
        result = recolor(
            rgba, source, target, recipe,
            mask_mode=mask_mode, image_key=plate.stem,
        )
        save_rgba(result, out_dir / f"{plate.stem} - {target}.png")
        rows.append(
            measure(f"{plate.stem[:14]} {target}", result, weight, recipe, crop)
        )
        cells.append((result, target))

    contact_sheet(cells, out_dir / f"{plate.stem} - sheet.png")
    return rows
