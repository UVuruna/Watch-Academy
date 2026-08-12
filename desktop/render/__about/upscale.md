# Upscale

**Script:** [upscale.py](../upscale.py) · **Flow:** [diagram](../__flow/upscale.md)

## Purpose

THE ON-THE-SPOT UPSCALER — what happens when the dial is asked to draw
an image LARGER than the file we ship.

Owner decree 2026-08-13. He had just lowered every working-set ceiling to
512 px, and was shown that at the absolute worst case (a 1,440 px dial
with a 200% element scale and a 200% hover enlarge, or a slot seat at its
150% pointer factor) a 512 source is visibly softer than a 1200 one. His
ruling, in translation: that is a situation nobody will ever use — and
even if somebody does insist on so abnormally large a display, let the
upscaling be done on the spot.

This module is that answer. It exists so the trade is honest in both
directions: **every ordinary user carries a small tree, and the one
person who zooms past it still gets a good picture** — computed once, on
their machine, for the size they actually asked for.

## Why not just let Qt scale it

Qt's `SmoothTransformation` is a bilinear filter. Downscaling with it is
fine. UPSCALING with it is where it shows: a single bilinear jump from
512 to 1200 px softens edges into ramps and leaves the image looking
washed rather than merely large.

Two cheap, well-understood steps fix most of that, and this module does
both:

1. **Step up in halvings, never in one leap.** Repeated ≤2× bilinear
   passes approximate a much better kernel than one big one, because
   each pass only ever interpolates between genuinely adjacent pixels.
   This is an old trick and it is a real one.
2. **Unsharp mask at the end.** Upscaling redistributes edge energy over
   more pixels; subtracting a blurred copy puts the definition back
   without inventing detail that was never there. The radius is small
   and the amount conservative on purpose — an aggressive unsharp turns
   a soft image into a crunchy one, which reads as worse, not better.

Neither step invents information. Both make the information that exists
land where the eye expects it.

## What it costs, and why that is acceptable

The whole point is that this path is RARE. It runs only when
`px_height > the source's own height` — which, on a shipped tree baked
to 512, means only at extreme dial sizes with extreme zoom.

- It is **disk-cached**, keyed by the source's content fingerprint and
  the target height, so a given size is computed once per machine, ever.
- It is **not** the working set. The working set makes files SMALLER for
  the common case and is warmed in the background. This makes one file
  bigger for a rare case and is paid at the moment of asking.
- A failure is never fatal: `upscaled_pixmap` returns `None` and
  `AssetCache._rasterize` falls back to the plain Qt scale — the picture
  the program would have drawn before this module existed (Rule #1, a
  documented fallback, never a silent one).

## Connections

### Uses
- [Raster Store](raster_store.md) — `source_prefix` for the cache key,
  `atomic_save` for the write
- [Config (folder)](../../config/___config.md) — `paths.settings_path`
  (where the raster cache lives)

### Used by
- [Assets](assets.md) — `AssetCache._rasterize`, the one chokepoint every
  art layer already rasterizes through

## Design Decisions

- **It lives beside the rasterizer, not inside it.** `assets.py` is the
  cache; this is an algorithm. Keeping them apart is what lets the
  algorithm be tested on plain images with no Qt cache in the way.
- **Numpy and Qt only, no new dependency.** Pillow does this in one call
  and is already used by the BAKERY — but the bakery is a setup script,
  and pulling Pillow into the runtime import graph would put it in the
  frozen build for a path that runs almost never. The two steps above
  cost a few dozen lines and no new shipped megabytes.
- **The unsharp blur is a separable box blur, run twice.** Two box
  passes approximate a gaussian closely enough for an unsharp mask, and
  a separable box blur is O(n) per axis instead of O(radius) — the
  difference between milliseconds and a visible stall on a large plate.
- **Never upscales past what was asked.** If the target is at or below
  the source, this module declines and says so; the caller keeps the
  ordinary path. An "upscaler" that also handles downscales would
  quietly become a second scaling policy beside the working set.
