# Continent Prompts — Pangea & Zealandia join the earth matrix

The owner's own earth family (`masters/celestial/earth/`) ships every
region in FOUR versions — `{atmo,clean} × {day,night}` — and the whole
instrument switches them live: atmosphere/clean is the user's one
`earth_style` setting, day/night follows the sky's own daylight law
(`config/continents.py`, `earth_face_art`). The two DEEP-TIME faces do
not have that matrix yet (owner audit 2026-08-14, his own folder
screenshot): Pangea exists as three one-off candidates under two
spellings (`pangaea.png`, `pangea.png`, `pangea_gem.png`), Zealandia as
two (`zealandia.png`, `zealandi_gem.png` — note the typo — and
`zealandia_gpt.png`), and NEITHER has a night face at all. His verdict:
one candidate per continent stays (HE picks which), and prompts are
written for everything the matrix still lacks. That is this sheet.

**Naming law (Rule #5):** the survivors and every generation here wear
the SAME stems the resolver already speaks —
`earth_{style}_{region}_{phase}.png` with the new regions `pangea` and
`zealandia` — so wiring them later is a roster entry, not a new code
path. No `<source>` split and no `_gem`/`_gpt` suffix: like the rest of
the earth family this is the owner's own area, suffixless by his sealed
verdict (`desktop/tests/test_assets_structure.py::
test_instrument_furniture_and_earth_are_suffixless_owner_art`).

**Register:** NOT the stained-glass night-window family — these must
sit in a row with the owner's existing 32 photorealistic globes. Space
photography register: the full Earth globe seen from orbit distance,
the target landmass centered on the visible hemisphere, real ocean
color, real cloud sparsity (thin, scattered — the existing faces keep
clouds rare so the land reads), NO lettering, NO borders drawn on the
land. `atmo` wears the thin blue atmospheric limb-glow halo of the
existing `earth_atmo_*` faces; `clean` cuts the globe clean against the
background with no limb glow, like `earth_clean_*`. `day` is the fully
sunlit hemisphere; `night` is the dark hemisphere lit only by cold
moonlight glinting off the ocean — NO city lights ever: Pangea is a
world before a single lamp, and Zealandia's night is emptier still.

**Reference:** each prompt renders from the SURVIVING candidate the
owner picks (`masters/celestial/earth/` — the winner is renamed to its
`earth_{style}_{region}_day` seat if it already reads as one of the
four, otherwise it stands as the model the generations copy). Keep the
survivor's continent geography EXACTLY — the generations change light
and atmosphere, never the coastline.

**Drop paths:** `masters/celestial/earth/` — the eight files below.

---

## Pangea — the world when it was one

**Pangea, atmosphere, day** → `masters/celestial/earth/earth_atmo_pangea_day.png`

```
Photorealistic Earth globe from orbit distance, the single supercontinent PANGEA centered on the sunlit hemisphere: one vast C-shaped landmass of ochre deserts, deep-green equatorial belts and rust-red mountain spines, wrapped by the single Panthalassa ocean in deep sapphire. Geography copied exactly from the reference image. Thin scattered white clouds, sparse enough that every coastline reads. A thin luminous blue atmospheric limb glow rings the whole globe. Fully sunlit day lighting, sun high. Isolated background, no stars needed, NO lettering, NO drawn borders.
```

**Pangea, atmosphere, night** → `masters/celestial/earth/earth_atmo_pangea_night.png`

```
Photorealistic Earth globe from orbit distance, the single supercontinent PANGEA centered on the NIGHT hemisphere: the landmass a near-black silhouette of deepest umber and slate, the single Panthalassa ocean around it catching cold blue-silver moonlight in a broad specular glint. ABSOLUTELY NO city lights — this is a world hundreds of millions of years before the first lamp; the darkness is total except for moonlit water and the faintest cloud sheen. Geography copied exactly from the reference image. A thin cold blue atmospheric limb glow rings the globe, dimmer than its day twin. Isolated background, NO lettering, NO drawn borders.
```

**Pangea, clean, day** → `masters/celestial/earth/earth_clean_pangea_day.png`

```
Photorealistic Earth globe from orbit distance, the single supercontinent PANGEA centered on the sunlit hemisphere: one vast C-shaped landmass of ochre deserts, deep-green equatorial belts and rust-red mountain spines in the single sapphire Panthalassa ocean. Geography copied exactly from the reference image. Thin scattered clouds. NO atmospheric limb glow — the globe's edge cuts clean and hard against the background, exactly like the existing earth_clean faces. Fully sunlit day lighting. Isolated background, NO lettering, NO drawn borders.
```

**Pangea, clean, night** → `masters/celestial/earth/earth_clean_pangea_night.png`

```
Photorealistic Earth globe from orbit distance, the single supercontinent PANGEA centered on the NIGHT hemisphere: near-black umber landmass silhouette, the Panthalassa ocean catching cold blue-silver moonlight, ABSOLUTELY NO city lights anywhere on a world before the first lamp. Geography copied exactly from the reference image. NO atmospheric limb glow — a clean hard globe edge against the background. Isolated background, NO lettering, NO drawn borders.
```

## Zealandia — the drowned continent

**Zealandia, atmosphere, day** → `masters/celestial/earth/earth_atmo_zealandia_day.png`

```
Photorealistic Earth globe from orbit distance centered on ZEALANDIA, the drowned eighth continent: the pale turquoise-and-jade submerged continental shelf glowing beneath shallow ocean around New Zealand's emerald islands — the only land above water — set in the deep sapphire South Pacific. The submerged plateau reads clearly as lighter, milky shallows against the abyssal dark blue. Geography copied exactly from the reference image. Thin scattered white clouds. A thin luminous blue atmospheric limb glow rings the globe. Fully sunlit day lighting. Isolated background, NO lettering, NO drawn borders.
```

**Zealandia, atmosphere, night** → `masters/celestial/earth/earth_atmo_zealandia_night.png`

```
Photorealistic Earth globe from orbit distance centered on ZEALANDIA at NIGHT: the South Pacific hemisphere in near-total darkness, New Zealand's islands a black silhouette, the vast submerged shelf faintly readable as a subtle milky sheen under cold blue-silver moonlight glinting across the ocean. ABSOLUTELY NO city lights — the drowned continent's night is the emptiest on Earth. Geography copied exactly from the reference image. A thin cold blue atmospheric limb glow rings the globe, dimmer than its day twin. Isolated background, NO lettering, NO drawn borders.
```

**Zealandia, clean, day** → `masters/celestial/earth/earth_clean_zealandia_day.png`

```
Photorealistic Earth globe from orbit distance centered on ZEALANDIA, the drowned eighth continent: pale turquoise-and-jade submerged continental shelf under shallow ocean around New Zealand's emerald islands, set in the deep sapphire South Pacific. Geography copied exactly from the reference image. Thin scattered clouds. NO atmospheric limb glow — the globe's edge cuts clean and hard against the background, exactly like the existing earth_clean faces. Fully sunlit day lighting. Isolated background, NO lettering, NO drawn borders.
```

**Zealandia, clean, night** → `masters/celestial/earth/earth_clean_zealandia_night.png`

```
Photorealistic Earth globe from orbit distance centered on ZEALANDIA at NIGHT: the South Pacific hemisphere in near-total darkness, New Zealand a black silhouette, the submerged shelf a subtle milky sheen under cold moonlight, ABSOLUTELY NO city lights. Geography copied exactly from the reference image. NO atmospheric limb glow — a clean hard globe edge. Isolated background, NO lettering, NO drawn borders.
```

---

## Cleanup owed beside this sheet (owner's own picks, not an agent's)

- **Pangea candidates:** `pangaea.png` / `pangea.png` / `pangea_gem.png`
  — ONE survives (owner picks), the other two leave `masters/`; the
  bake reconcile then clears their shipped twins.
- **Zealandia candidates:** `zealandia.png` / `zealandi_gem.png` (typo:
  missing `a`) / `zealandia_gpt.png` — same: one survives, owner picks.
- After the picks the earth area is suffixless again and
  `test_instrument_furniture_and_earth_are_suffixless_owner_art` goes
  back to green on its own.
