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
- [App Controller](controller.md) — the menu's Guide… entry

## Classes

### GuideDialog
- loads the ordered slides on open; Previous/Next buttons + a page
  counter; caption text under the image when provided
