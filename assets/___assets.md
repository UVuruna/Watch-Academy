# assets/

Bundled visual content — ALL of it shared app content (there are no
skin folders: DOMY and MORPH are ring preset names, nothing more).

```
📁 assets/
  🖼️ logo.svg              ← project logo (M7; also copied to monorepo logos/)
  🖼️ logo.svg              ← the owner's GOLD watch — tray icon now, EXE/installer art in M7
  🖼️ logo-setup.svg        ← the rose-gold variant (NSIS wizard art)
  📁 ring/                 ← dial ring faces: domy.png, morph.png (+ future rings)
    📁 letters/            ← the owner's GOLD letter library: latin SVG (D,G,H,I,M,P,S,
                             U,V,X,Y,Z) + greek PNG (Omega,Phi,Pi,Psi,Sigma,Theta).
                             Active per preset (RING_LETTER_FILES): domy M/D/Y+Omega,
                             morph M/Pi/H+Omega. Overlaid by calculation so the ring
                             TINT never touches them; SILVER = desaturated gold at load;
                             each preset's ACCENT letter wears the opposite metal
                             (domy inverts its Omega, morph inverts its M)
  📁 hands/                ← hour/minute/second.svg (owner canvases 240/290/300,
                             hub 15 design units above the bottom)
  📁 earth/                ← earth_{clean|atmo}_{continent}_{day|night}.png
  📁 weekday/              ← body art per THEME (SYMBOLISM.md), files carry ENTITY names:
                             planets/ (sun..saturn.png, real renders)
                             greek/ (Helios..Cronus.png)   norse/ (Sol..Sabbath.png)
                             religion/ (Christianity..Judaism.png)
                             profession/ (Ruler..Farmer.png)
                             — non-planet files are 1×1 placeholders until the owner
                             pastes his vectors over them (same names)
  📁 zodiac/               ← octa bottom-arm art: sign/, logo/, constellation/ (<Sign>.png),
                             chinese/ (<Animal>.png) — 1×1 placeholders, same convention
```

The star and the Umbra are deliberately NOT assets — both are simple
geometry drawn procedurally (owner decision: keeps the bundle light,
stays sharp at every size, and lets the pointer variant change the arm
count and the contrast setting change the shades at runtime).

Bundle copies are downscaled working resolutions (ring 1024 px, planets
and Earth markers 256 px); the full-resolution masters stay in `design/`
(untracked owner scratch space) — RE-COPY bundle files whenever the
masters change.

## Earth naming convention

`earth_<style>_<continent>_<day|night>.png` with style `clean` (default)
or `atmo`, continents: europe, north_america, south_america, africa,
asia, oceania. The night variant is shown between sunset and sunrise. The
moon marker reuses `weekday/planets/moon.png` with a procedural
terminator shadow. PNG or SVG both work (detected by extension,
rasterized once by the asset cache).

## Connections

### Used by
- [Config (folder)](../config/___config.md) — DEFAULT_SKIN + RING_PRESETS paths
- [Render (folder)](../render/___render.md) — asset cache
- [App Controller](../app/controller.md) — weekday theme + zodiac art paths
