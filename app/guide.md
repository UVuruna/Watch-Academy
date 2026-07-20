# Guide

**Script:** [Guide (script)](guide.py)

## Purpose
The right-click "Guide" window (name chosen over "About" — it is a
help/instructions carousel, not a version box): left/right navigation
over slides the owner prepares. Slides live in `assets/guide/` as
`NN_name.png` with an optional `captions.json` (`{"NN_name": "text"}`)
— the window shows a friendly placeholder until they land.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — the slides folder path
- [Assets (folder)](../assets/___assets.md) — guide slides
- [Theme](theme.md) — the dark dialog surface

### Used by
- [App Controller](controller.md) — `_open_guide()` opens (or raises)
  the ONE live instance

## Classes

### GuideDialog
- loads the ordered slides on open; Previous/Next buttons + a page
  counter; caption text under the image when provided
- **NON-MODAL (ITEM 1, R4 owner instruction batch 2026-07-20):** the
  controller `.show()`s this dialog instead of `.exec()`ing it — the
  dial stays interactive while it is open. `WA_DeleteOnClose` tears the
  C++ object down the moment the window closes; the controller clears
  its own live-instance reference on the `finished` signal and raises
  the existing window instead of opening a second one
- **OPENING SIZE (owner DESIGN #1):** square (1:1) at 50% of the
  screen's available height (`app.theme.size_to_screen`) — the images
  already rescale live with the window (`_rescale`/`resizeEvent`/
  `showEvent`), so the shape change from the old fixed
  `GUIDE_INITIAL_IMAGE_PX`-derived rectangle costs nothing; still a
  normal resizable/maximizable window past that first paint
