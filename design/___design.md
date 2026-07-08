# design/

The owner's master art — NOT bundled with the app (working copies are
downscaled into `assets/skins/domy/` and must be refreshed whenever a
master changes).

## Folders

- `hours/` — full dial-ring art per skin (`domy.png`, `morph.png`) with
  the 360-dot precision/seconds scale
- `pointer/` — vector hands (`hours.svg`, `minutes.svg`, `seconds.svg`;
  rotation hub centered 15 units from the bottom, hub radius 15)
- `background/` — the fixed 32-section gray wheel (`gray.png`) and the
  cross/hexa/octa pointer look references (drawn procedurally in-app)
- `weekday/planets/` — the seven weekday bodies
- `date/earth/{atmosphere|clean}/{day|night}/` — Earth per continent
- legacy loose files: `hours.png`, `minutes.png`, `seconds.png`,
  `hexaLight.png` (superseded by the folders above)

## Connections

### Used by
- [Assets (folder)](../assets/___assets.md) — downscaled working copies
- [Tests (folder)](../tests/___tests.md) — mockup day 20.6.2025 remains a
  golden test case (sunrise 4:52, sunset 20:27)
