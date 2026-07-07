# tests/

**Planned — populated from M2.** Headless pytest suite (no QApplication for
core/data/skins/settings tests).

Golden values pinned to empirically verified ground truth:
- Dial angles: 12:00→0°, 18:00→90°, 00:00→180°, 06:00→270°
- Belgrade DST: hexagram −4.17° → +10.76° across 2026-03-28/29
- Tromsø: four daylight regimes (2026-01-15 / 05-10 / 05-25); Longyearbyen
  polar night with solar noon still computable
- Equinoxes exactly at 90°/270° (rejects the naive day/365 mapping ≈ 92.3°)
- Moon fraction 0.7400 on 2026-07-07; anchor instants exact
- Mockup day 20.6.2025: sunrise 4:52, sunset 20:27, Earth at top

Repository tests run against the LIVE `Database/` files (mixed-depth
country walk, "Last Quarter" normalization, winter-field trap, coverage
range errors). A purity test asserts nothing under `core/` or `data/`
imports PySide6.

## Connections

### Uses
- [Core (folder)](../core/___core.md), [Data (folder)](../data/___data.md),
  [Skins (folder)](../skins/___skins.md)
