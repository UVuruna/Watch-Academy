# Filters

**Script:** [Filters (script)](filters.py)

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

## Why a guided filter and not a Gaussian

A Gaussian blur does not know where edges are, so subtracting it leaves
a bright/dark halo hugging every strong edge. A medallion is nothing but
strong edges (engraved lines against a field), so the halos would read as
a cheap "HDR" glow. The guided filter fits a local linear model instead
and passes edges through untouched.

## Algorithm (pseudocode)

```
BOX MEAN (radius r), O(1) per pixel:
    running_sum ALONG rows, then ALONG columns
    divide by the same box sum over an all-ones image
    -> border pixels average only the samples that exist

SELF-GUIDED SPLIT (channel I, radius r, epsilon eps):
    mean     = BOX MEAN of I
    variance = BOX MEAN of I*I  -  mean*mean          (never below 0)
    slope    = variance / (variance + eps)
        IF variance << eps  -> slope -> 0  -> flat area, smooth to mean
        IF variance >> eps  -> slope -> 1  -> an edge, pass through
    offset   = mean * (1 - slope)
    base     = BOX MEAN of slope * I  +  BOX MEAN of offset
    detail   = I - base            (base + detail is exact)
```

## Functions

### `box_mean(source, radius)`
Window mean with correct edge normalization.

### `clamp_radius(shape, radius)`
The largest radius the cumulative-sum slicing supports for an image of
`shape`. Real art is never small enough to hit this; it keeps thumbnails
and unit tests honest.

### `guided_split(channel, radius, epsilon)`
Returns `(base, detail)`. `epsilon` is the variance below which local
structure counts as texture rather than as an edge — the one knob that
decides what "detail" means.
