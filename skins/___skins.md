# skins/

The typed RENDER CONFIGURATION — Qt-free so it is pytest-testable. All
rendering is driven by one `SkinDefinition` instance: `DEFAULT_SKIN` in
[Config (folder)](../config/___config.md), onto which the controller
overlays the chosen RING PRESET and the user's display choices at build
time (`build_skin` in [Watch Controller](../app/controller.md)).

**DOMY and MORPH are ring preset names — nothing more** (owner
decision): a ring face in `assets/ring/` plus its Greek-ordinal letter
positions (`RING_PRESETS` in config). There are no skin folders and no
skin.json packs; all art is shared app content under `assets/`.

## Files

### `manifest.py` — Typed Render Config
The six unit dataclasses (`SkinDefinition` + specs: background, star,
ring, weekday_set, year_marker, hands) and `missing_assets()`. See
[Manifest](manifest.md).

Dial pointer variants (user-selectable from the tray; display names
per the owner: Prism, Seasons, Compass, Trinity): **hexa/Prism**
(6-point — the default), **cross/Seasons** (4-point, arms shaped like
octa arms with gaps), **octa/Compass** (8-point) and **trio/Trinity**
(3-point — half of hexa, arms at the M/D/Y ring letters 12h/4h/20h).
The pointer sets the palette size (trio = 3 hues × 120°, cross = 4 ×
90°, hexa = 6 × 60°, octa = 8 × 45° — the Aura wedges and the Star
diamonds share ONE palette preset: hexa/octa in "paint" and "light"
styles, cross with its single seasons palette, trio with the single
trinity palette Faith yellow / Love red / Hope blue) and the weekday
slot layout: hexa and trio center the Sun (trio pairs Jupiter+Saturn,
Venus+Mars, Moon+Mercury on its three arms), cross pairs bodies on
three arms (the next-upcoming day wins a shared slot; Wednesday sits
alone at the bottom), octa seats one body per arm with a user-selected
info slot (time/date/day length/zodiac) on the bottom arm. Every
pointer, the trio included, centers its Aura wedges on the arm tips
(owner correction: trio thirds are 8-16 / 16-24 / 0-8).

## Connections

### Uses
- Nothing (stdlib dataclasses only — importable from anywhere)

### Used by
- [Config (folder)](../config/___config.md) — `DEFAULT_SKIN` + `RING_PRESETS`
- [Render (folder)](../render/___render.md) — layers read the specs
- [Watch Controller](../app/controller.md) — `build_skin` + display overlays
