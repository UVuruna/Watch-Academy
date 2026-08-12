"""The metal transformer's golden pins — including one REGRESSION test
per named failure of the kernel it replaces (Rule #25: a fix is not a fix
until a test forbids the failure from coming back).

The test plate is SYNTHESIZED here, never loaded from `UV/` (the owner's
inbox is gitignored, so a test that read it would pass only on his
machine). It carries the same three features the real medallions do: a
warm metal relief with engraved lines, a neutral gray stone field that
must survive untouched, and a pale page with dark ink whose detail the
old kernel destroyed.
"""

from pathlib import Path

import numpy as np
import pytest

from recolor import filters, mask, ramp, space, tone
from recolor import recipe as recipe_module
from recolor.transform import recolor

SIZE = 192
# The page window, in plate coordinates — the synthetic stand-in for the
# book page the owner circled in red.
PAGE = (24, 120, 84, 168)


@pytest.fixture(scope="module")
def recipe():
    return recipe_module.load()


@pytest.fixture(scope="module")
def plate():
    """A synthetic bronze plate: warm relief + engraved lines + neutral
    stone + a pale inked page. sRGB float RGBA."""
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    rgba = np.zeros((SIZE, SIZE, 4))
    rgba[..., 3] = 1.0

    # Neutral gray stone field with a little noise-free texture.
    stone = 0.30 + 0.05 * np.sin(xs / 7.0) * np.cos(ys / 9.0)
    rgba[..., :3] = stone[..., None]

    # A warm bronze relief disc, lit from the upper left, with engraved
    # lines cut into it.
    radius = np.hypot(xs - SIZE / 2, ys - SIZE / 2) / (SIZE / 2)
    disc = radius < 0.86
    shade = np.clip(0.62 - 0.45 * radius + 0.25 * (1.0 - ys / SIZE), 0.06, 1.0)
    engraved = (np.sin(xs / 3.5) * np.sin(ys / 3.5)) > 0.65
    shade = np.where(engraved, shade * 0.45, shade)
    bronze = np.array([1.00, 0.66, 0.36])          # a warm metal albedo
    rgba[..., :3] = np.where(
        disc[..., None], bronze * shade[..., None], rgba[..., :3]
    )

    # A pale page with DARK INK marks — the detail that must survive.
    x0, y0, x1, y1 = PAGE
    page = np.zeros((SIZE, SIZE), dtype=bool)
    page[y0:y1, x0:x1] = True
    ink = page & (((xs * 2 + ys * 3) % 11) < 2)
    rgba[..., :3] = np.where(page[..., None], np.array([0.86, 0.82, 0.74]),
                             rgba[..., :3])
    rgba[..., :3] = np.where(ink[..., None], np.array([0.34, 0.33, 0.36]),
                             rgba[..., :3])
    return rgba


def _weight(plate, recipe, source="bronze"):
    return mask.metal_weight(
        space.srgb_to_linear(plate[..., :3]),
        plate[..., 3],
        ramp.body_color(recipe.metal(source), recipe.tuning.body_position),
        recipe.tuning,
        "chroma",
    )


def _lightness(rgba):
    return space.linear_to_oklab(space.srgb_to_linear(rgba[..., :3]))[..., 0]


def _page_range(rgba):
    x0, y0, x1, y1 = PAGE
    window = _lightness(rgba)[y0:y1, x0:x1]
    return float(np.percentile(window, 95) - np.percentile(window, 5))


# --------------------------------------------------------------- spaces

def test_srgb_roundtrip_is_exact():
    values = np.linspace(0.0, 1.0, 257)
    back = space.linear_to_srgb(space.srgb_to_linear(values))
    assert np.abs(back - values).max() < 1e-9


def test_oklab_roundtrip_is_exact_to_far_below_8_bit():
    """Ottosson's published matrices are decimal approximations, so the
    inverse is not bit-exact — but the residual must stay orders of
    magnitude below one 8-bit step (1/255 = 3.9e-3), or a no-op recolor
    would visibly drift."""
    rng = np.random.default_rng(7)
    linear = rng.random((64, 64, 3))
    back = space.oklab_to_linear(space.linear_to_oklab(linear))
    assert np.abs(back - linear).max() < 1e-5


def test_hue_distance_wraps_around_zero():
    hue = np.array([1.0, 359.0, 180.0])
    assert np.allclose(space.hue_distance(hue, 0.0), [1.0, 1.0, 180.0])


# -------------------------------------------------------------- filters

def test_box_mean_of_a_constant_is_that_constant():
    field = np.full((48, 61), 0.375)
    assert np.abs(filters.box_mean(field, 5) - 0.375).max() < 1e-12


def test_guided_split_is_lossless():
    rng = np.random.default_rng(3)
    channel = rng.random((70, 55))
    base, detail = filters.guided_split(channel, 4, 0.002)
    assert np.abs(base + detail - channel).max() < 1e-12


def test_guided_split_keeps_a_step_edge_in_the_base():
    """The point of a guided filter over a Gaussian: a hard edge belongs
    to the FORM, so almost none of it leaks into the detail layer (a
    Gaussian would leave a halo there)."""
    channel = np.zeros((80, 80))
    channel[:, 40:] = 1.0
    detail = filters.guided_split(channel, 6, 1e-4)[1]
    assert np.abs(detail).max() < 0.05


# ----------------------------------------------------------------- tone

def test_detint_strips_the_source_cast_off_the_metal(plate, recipe):
    """A warm plate's METAL loses its cast — this is what makes ANY metal
    a valid source. One global division cannot flatten it completely,
    because art authored in sRGB has a chromaticity that drifts with
    brightness (the transfer function's offset is not separable), and it
    does not need to: the output color comes entirely from the target's
    ramp, so what de-tint must deliver is a FAIR relief reading, not a
    gray image.

    What must NOT be neutralized is the page and its ink — their chroma
    is not the metal's cast, and it is exactly the signal
    `tone._chroma_texture` later re-injects."""
    linear = space.srgb_to_linear(plate[..., :3])
    weight = _weight(plate, recipe)
    neutral = tone.detint(linear, weight, 1.0)

    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    radius = np.hypot(xs - SIZE / 2, ys - SIZE / 2) / (SIZE / 2)
    x0, y0, x1, y1 = PAGE
    page = np.zeros((SIZE, SIZE), dtype=bool)
    page[y0:y1, x0:x1] = True
    pure_metal = (radius < 0.80) & ~page & (weight > 0.5)

    def mean_chroma(image, where):
        return space.oklab_chroma_hue(
            space.linear_to_oklab(image[where])
        )[0].mean()

    assert mean_chroma(neutral, pure_metal) < 0.4 * mean_chroma(
        linear, pure_metal
    )
    assert mean_chroma(neutral, weight > 0.5) > 0.01


def test_the_relief_reads_all_three_channels():
    """THE FAILURE: the retired kernel's relief was `max(R,G,B)`, which on
    warm art is the RED channel alone (measured mean R 0.3721 vs mean V
    0.3740 on the owner's plate) — two thirds of the image discarded
    before any recolor began, which is why the ink on the book page had
    nothing left to be drawn from.

    The decisive property: `max()` cannot tell a deep red mark from a
    pale warm page (both 0.80), and any honest lightness must."""
    pair = np.array([[[0.80, 0.20, 0.20], [0.80, 0.75, 0.70]]])
    assert pair.max(axis=-1)[0, 0] == pair.max(axis=-1)[0, 1]

    lightness = space.linear_to_oklab(space.srgb_to_linear(pair))[..., 0]
    assert abs(lightness[0, 0] - lightness[0, 1]) > 0.15


def test_anchor_is_monotone_not_a_rank_remap(plate, recipe):
    """THE REVERTED FAILURE (`013b5ca`): a percentile RANK remap flattened
    every relief. The anchor must be one shared multiply and offset, so
    sorting order is preserved exactly and the mapping is affine."""
    linear = space.srgb_to_linear(plate[..., :3])
    weight = _weight(plate, recipe)
    base = space.linear_to_oklab(linear)[..., 0]
    anchored, scale = tone.anchor(base, weight, recipe.tuning)

    interior = (anchored > 0.02) & (anchored < 0.98)
    flat_base = base[interior].ravel()
    flat_out = anchored[interior].ravel()
    # Affine: every pixel shares one slope, so the residual against a
    # single line is zero to floating point.
    slope, offset = np.polyfit(flat_base, flat_out, 1)
    assert np.abs(flat_out - (slope * flat_base + offset)).max() < 1e-9
    assert abs(slope - scale) < 1e-6


def test_shape_fixes_the_endpoints_and_stays_monotone():
    values = np.linspace(0.0, 1.0, 1001)
    for contrast in (-0.5, 0.0, 0.45, 1.0):
        out = tone.shape(values, 1.0, contrast)
        assert abs(out[0]) < 1e-12 and abs(out[-1] - 1.0) < 1e-12
        assert np.diff(out).min() >= -1e-12


# ----------------------------------------------------------------- ramp

def test_every_metal_ramp_rises_and_desaturates_at_the_top(recipe):
    """THE LAW: chroma peaks in the body and FALLS toward the highlight.
    The retired kernel's flat S=1.0 is what this forbids."""
    for name, metal in recipe.metals.items():
        lab = space.linear_to_oklab(
            ramp.sample(metal, np.linspace(0.0, 1.0, 64))
        )
        lightness = lab[..., 0]
        chroma = space.oklab_chroma_hue(lab)[0]
        assert np.diff(lightness).min() > -1e-9, f"{name} ramp dips in L"
        # Chroma must PEAK in the body — never at either end.
        peak = int(np.argmax(chroma))
        assert 0 < peak < len(chroma) - 1, f"{name} peaks at an end"
        # A genuinely chromatic metal must additionally roll a long way
        # off at the specular; a near-neutral one (steel, iron, pewter)
        # has no chroma to roll off in the first place.
        if chroma.max() > 0.05:
            assert chroma[-1] < chroma.max() * 0.6, (
                f"{name} keeps its chroma at the specular"
            )


def test_body_color_matches_the_ramp_at_the_body_position(recipe):
    metal = recipe.metal("gold")
    direct = ramp.sample(metal, np.array(recipe.tuning.body_position))
    assert np.allclose(
        ramp.body_color(metal, recipe.tuning.body_position), direct.reshape(3)
    )


# ----------------------------------------------------------------- mask

def test_mask_claims_the_metal_and_spares_the_stone(plate, recipe):
    weight = _weight(plate, recipe)
    ys, xs = np.mgrid[0:SIZE, 0:SIZE]
    radius = np.hypot(xs - SIZE / 2, ys - SIZE / 2) / (SIZE / 2)
    x0, y0, x1, y1 = PAGE
    page = np.zeros((SIZE, SIZE), dtype=bool)
    page[y0:y1, x0:x1] = True
    stone = (radius > 0.95) & ~page
    assert weight[stone].max() < 0.05
    assert weight.mean() > 0.15


def test_alpha_mode_claims_every_opaque_pixel(plate, recipe):
    weight = mask.metal_weight(
        space.srgb_to_linear(plate[..., :3]), plate[..., 3],
        ramp.body_color(recipe.metal("gold"), recipe.tuning.body_position),
        recipe.tuning, "alpha",
    )
    assert weight.min() == 1.0


def test_unknown_mask_mode_raises(plate, recipe):
    with pytest.raises(ValueError, match="unknown mask mode"):
        mask.metal_weight(
            space.srgb_to_linear(plate[..., :3]), plate[..., 3],
            ramp.body_color(recipe.metal("gold"), 0.55),
            recipe.tuning, "value",
        )


# ---------------------------------------------- REGRESSION: the failures

@pytest.mark.parametrize("target", ["gold", "silver", "bronze", "copper"])
def test_no_channel_is_annihilated(plate, recipe, target):
    """THE FAILURE: gold `HSV(44.9, S=1.0, V)` expands to
    `(V, 0.748V, 0)` — 52.59% of the owner's gold plate had a blue
    channel of exactly zero, and every detail carried by chroma died
    with it. No masked pixel may have a dead channel again."""
    out = recolor(plate, "bronze", target, recipe)
    weight = _weight(plate, recipe)
    picked = out[..., :3][weight > 0.5]
    for channel, name in enumerate("RGB"):
        dead = float((picked[:, channel] <= 1 / 255).mean())
        assert dead < 0.01, f"{target}: {name} dead on {dead:.2%} of the metal"


@pytest.mark.parametrize("target", ["gold", "silver", "bronze", "platinum"])
def test_highlights_are_not_blown(plate, recipe, target):
    """THE FAILURE: the bounded-but-blind global gain hit its 1.90
    ceiling on dark medallion art and clipped 11.87% (gold) / 8.17%
    (silver) of the plate to one flat maximum — "previše osvetljeno, bez
    detalja". The percentile anchor cannot do that."""
    out = recolor(plate, "bronze", target, recipe)
    weight = _weight(plate, recipe)
    value = out[..., :3].max(axis=-1)[weight > 0.5]
    assert float((value >= 254 / 255).mean()) < 0.04


def test_silver_is_not_a_max_channel_grayscale(plate, recipe):
    """THE FAILURE: silver was `HSV(220, S=0, V)` = `max(R,G,B)`, which
    on warm art is the RED channel alone (measured mean R 0.3721 vs mean
    V 0.3740). The result must not be reproducible that way."""
    out = recolor(plate, "bronze", "silver", recipe)
    weight = _weight(plate, recipe)
    metal = weight > 0.5
    old_recipe = plate[..., :3].max(axis=-1)[metal]
    new = out[..., :3][metal]
    # Not the same pixels...
    assert np.abs(new.max(axis=-1) - old_recipe).mean() > 0.05
    # ...and not achromatic either: real silver carries a cool cast.
    chroma = space.oklab_chroma_hue(
        space.linear_to_oklab(space.srgb_to_linear(new))
    )[0]
    assert chroma.mean() > 0.002


@pytest.mark.parametrize("target", ["gold", "silver", "bronze"])
def test_page_detail_survives_the_metal_change(plate, recipe, target):
    """THE FAILURE the owner circled in red: the book page came out a
    flat blob (gold) or blown white (silver, p95 = 1.000 — the top of
    the page had NO information left). The page's lightness range must
    not collapse."""
    out = recolor(plate, "bronze", target, recipe)
    assert _page_range(out) > 0.7 * _page_range(plate)


def test_the_stone_field_is_left_as_drawn(plate, recipe):
    """The owner's 2026-07-12 insight, still law: only the warm metal may
    change — the gray stone and engravings stay exactly as drawn."""
    out = recolor(plate, "bronze", "gold", recipe)
    weight = _weight(plate, recipe)
    untouched = weight < 0.01
    assert np.abs(out[..., :3][untouched] - plate[..., :3][untouched]).max() < 2 / 255


def test_alpha_is_carried_through_untouched(plate, recipe):
    """No ARITHMETIC may touch the alpha channel. Since the float32
    pipeline (0.14.705) the output is single precision, so "untouched"
    means bit-exactly the float32 CAST of the input — any blend or
    scale would break that equality."""
    faded = plate.copy()
    faded[..., 3] = np.linspace(0.0, 1.0, SIZE)[None, :]
    out = recolor(faded, "bronze", "silver", recipe)
    assert np.array_equal(out[..., 3], faded[..., 3].astype(np.float32))


def test_every_metal_can_be_both_source_and_target(plate, recipe):
    """Ring letters go gold -> bronze/silver, badges go bronze ->
    gold/silver: any metal must work on either side of the transform
    through the one code path."""
    for source in ("bronze", "gold", "silver", "steel"):
        for target in ("gold", "bronze", "iron"):
            out = recolor(plate, source, target, recipe)
            assert np.isfinite(out).all()
            assert out.min() >= 0.0 and out.max() <= 1.0


def test_unknown_metal_names_its_alternatives(recipe):
    with pytest.raises(KeyError, match="unknown metal"):
        recipe.metal("unobtanium")


def test_the_algorithm_core_depends_on_numpy_alone():
    """The port guarantee: Pillow is allowed in the DEV tools only. If it
    ever reaches the algorithm, the Colorize SVG port inherits a
    dependency it cannot use."""
    core = Path(__file__).resolve().parents[1] / "recolor"
    dev_tools = {"preview.py", "__main__.py"}
    offenders = [
        source.name for source in sorted(core.glob("*.py"))
        if source.name not in dev_tools
        and "PIL" in source.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_overrides_are_empty_by_default(recipe):
    """The one-formula law: a per-image override is a documented BACKUP,
    and shipping one silently would hide that the shared formula failed
    for that plate."""
    assert recipe.overrides == {}


def test_box_mean_matches_the_naive_window_mean():
    """THE COUNTS CACHE PIN (0.14.703): `box_mean` now reuses its
    edge-normalization denominator across calls — the cache must never
    change the arithmetic, so the whole filter is pinned against a
    literal nested-loop window mean with clamped edges."""
    rng = np.random.default_rng(7)
    source = rng.random((13, 9))
    radius = 2
    expected = np.empty_like(source)
    for y in range(source.shape[0]):
        for x in range(source.shape[1]):
            window = source[
                max(0, y - radius):y + radius + 1,
                max(0, x - radius):x + radius + 1,
            ]
            expected[y, x] = window.mean()
    np.testing.assert_allclose(
        filters.box_mean(source, radius), expected, rtol=1e-12
    )


def test_box_mean_is_bit_identical_on_the_cached_second_call():
    """The cached denominator serves every later same-shape call — the
    second answer must be BIT-identical to the first, and the shared
    read-only counts plane must never be writable by a caller."""
    rng = np.random.default_rng(11)
    source = rng.random((21, 17))
    first = filters.box_mean(source, 3).copy()
    second = filters.box_mean(source, 3)
    np.testing.assert_array_equal(first, second)
    counts = filters._box_counts(source.shape, 3, source.dtype.str)
    assert not counts.flags.writeable


def test_ramp_stops_cache_serves_reads_only(recipe):
    """`_stops_oklab` is cached per frozen Metal — same object back on
    the second call, read-only both times, and `sample` still maps the
    ramp ends to the ramp ends."""
    metal = recipe.metal("silver")
    first = ramp._stops_oklab(metal)
    second = ramp._stops_oklab(metal)
    assert first[0] is second[0] and first[1] is second[1]
    assert not first[0].flags.writeable and not first[1].flags.writeable
    ends = ramp.sample(metal, np.array([0.0, 1.0]))
    assert ends.shape == (2, 3)
