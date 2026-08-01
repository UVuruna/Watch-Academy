# Filters

**Script:** [Filters (script)](../filters.py) · **Flow:** [diagram](../__flow/filters.md)

## Purpose

The frequency-separation primitive the whole transformer rests on: split
a lightness map into **form** (low frequency) and **detail** (high
frequency) so the tonal curve touches only the form. This is what keeps
engraving lines, drapery folds, hair and the drawings on a book page
alive through a metal change — the retired kernel had no such split at
all, so a single global gain merged every fine relationship into flat
clipped areas.

## Connections

### Uses
- nothing (numpy only, by design)

### Used by
- [Tone](tone.md) — the base/detail split and the optional chroma-detail
  extraction
- [Preview](preview.md) — `guided_split` for the `detail_energy` metric

## Why a guided filter and not a Gaussian

A Gaussian blur does not know where edges are, so subtracting it leaves
a bright/dark halo hugging every strong edge. A medallion is nothing but
strong edges (engraved lines against a field), so the halos would read
as a cheap "HDR" glow. The guided filter fits a local linear model
instead and passes edges through untouched.

## Functions

### `box_mean(source, radius)`
Window mean with correct edge normalization — the denominator is the
same box sum taken over an all-ones array, so border pixels average only
the samples that actually exist.

### `clamp_radius(shape, radius)`
The largest radius `_box_sum`'s slicing supports for an image of
`shape` — `max(0, min(radius, (min(shape) - 2) // 2))`. Returns 0 for an
image too small to hold a single window (a 2x1 color probe, a 1px icon);
real art never hits this, but it keeps thumbnails and unit tests honest.

### `guided_split(channel, radius, epsilon) -> (base, detail)`
Self-guided (guide == input) collapses the general guided filter to a
compact form: within each window the filter is the linear model
`q = a*I + b` whose `a = variance / (variance + epsilon)` — flat regions
get `a -> 0` and are smoothed to their local mean, edge-straddling
regions get `a -> 1` and pass through unchanged. `epsilon` is the
variance below which local structure counts as texture rather than as
an edge — the one knob that decides what "detail" means. `base + detail`
reconstructs the input exactly. When `clamp_radius` returns 0 the image
has no frequencies to separate: `base` is the channel itself and
`detail` is zero — the honest answer, not a special case.
