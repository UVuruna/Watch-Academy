# Topic Builders

**Script:** [Topic Builders (script)](../builders.py) · **Flow:** [diagram](../__flow/builders.md)

## Purpose
Turn a theme key into `(icon, entries)`: the weekday skeleton every
theme shares, the pantheon and wider-court blocks the four god themes
add, the Continents topic's own custom build, and the Guide topic built
from the help book's own JSON.

Moved VERBATIM from the retired single 2,766-line `app/encyclopedia.py`
(root Rule #20) — the Session 27 reform changed how topics are GROUPED
and READ, never how a page is built.

## Connections

### Uses
- [Static Pages](pages.md) — `_GOD_TOPIC_GALLERY_TITLES`, `_INSTRUMENT_KEYS`, `_VSM_DAYS`, `_WEEK_EMBLEMS`, `_WEEK_ORDER`, `NINTH_SEAT_PHILOSOPHICAL_NAME`
- [Continents (core)](../../../core/__about/continents.md) — `ninth_is_pangea_from_repos`, the living Ninth
- [Asset Recolor](../../../render/__about/asset_recolor.md) — `metal_variant_path`
- config `pantheon`, `defaults`, `continents`, `constants`, `paths` — every art-path and roster helper

### Used by
- [Topic Tree](tree.md) — `_build_topics` calls every builder here

## Functions

- `_metal_looks(base, colored)` / `_colored_sibling(path)`: the shared
  Colored/Bronze/Gold/Silver look tuple and its colored-twin path rule
- `_ninth_looks(theme, plate)`: the Ninth's own finish switcher — the
  same cycle its seated eight wear, or `None` for a theme with no
  per-metal art
- `_live_ninth_face(theme, name, plate, is_daylight, travel_date)`: THE
  DOUBLE NINTH LAW's dispatch — which `(name, plate)` a theme's Ninth
  actually shows right now
- `_theme_dual_art(theme, colored=False, on_date=None)`: the theme's
  Sunday SERVANT plate
- `_weekday_topic(theme, travel_date=None) -> (icon, entries)`: the
  10/11-page skeleton every weekday theme shares
- `_pantheon_topic(theme) -> list[dict]`: the culture's own 11-page
  Pantheon-roster run, reusing the Planetary block's Ninth
- `_wider_topic(theme) -> list[dict]`: the trailing Wider Court block —
  a title page plus one plain page per seatless A-list figure
- `_continents_topic(travel_date) -> dict`: the custom Continents build
  — world-map title, the Atmosphere/Clean × Day/Night look switcher, the
  living Ninth (Zealandia normally, Pangea on a Pangea day)
- `_guide_topic(overlay) -> dict`: one guide JSON page becomes one entry

## The weekday skeleton

```
0     the theme's own title page
1..6  Monday..Saturday          (owner: "Uvek... Ponedeljak PRVI")
7     the week-duality title
8     the Ruler half of Sunday   (GOOD)
9     the Servant half           (EVIL)
10    the Ninth                  (appended separately, outside the week — CANON.md)
```

## Design Decisions
- **GOOD and EVIL are two ordinary pages, never a merged dual page**
  (owner verdict A, round R3b item 1) — each is shaped exactly like a
  Monday..Saturday page, resolved through `evil_looks_for` on the
  Servant side.
- **THE DOUBLE NINTH LAW's two mechanisms are theme-scoped**:
  `"daynight"` (sw_dyad) swaps to the night face; `"term_weekly"`
  (cp_corpo alone) rotates the canonical plate by ISO week. Every other
  theme ignores `travel_date`/`is_daylight` completely — this law never
  touches a theme's static gallery beyond its two owners.
- **The Pantheon safety law**: a seat whose pantheon plate has not
  landed keeps the WHOLE planetary bundle (file + name + article
  together); a missing pantheon DUAL pulls the whole Sunday pair back to
  planetary — never a pantheon name paired with planetary art.
- **`continents` needs neither Double-Ninth addition** — its own custom
  build already derives Pangea/Zealandia from `travel_date` directly.
