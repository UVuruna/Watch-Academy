# Defaults — Flow

**About:** [description](../__about/defaults.md)

## Sections

```
📁 defaults.py  (812 lines, the Session-36 remnant)
  Cross-DAG remnants        ECLIPSE_SOLAR_ART, ECLIPSE_LUNAR_TYPE_ICON,
                             ECLIPSE_SOLAR_TYPE_ICON_SOURCE
  Location                  DEFAULT_CITY
  Tick scheduling           TICK_EPSILON_MS, CLOCK_JUMP_THRESHOLD_S,
                             CLICK_THROUGH_HOVER_POLL_MS
  Settings persistence      SETTINGS_SCHEMA_VERSION, _WRITE_DEBOUNCE_MS
  Tray / app presentation   TRAY_ICON_SIZE, LOGO_ASSET, WINDOW_ICON_SIZES_PX
  UI icon chrome            ICON_DIR, ICON_FILES, icon_path()
  Working-set ceilings      WORKING_SET_CEILINGS
  Time Travel Quick Jumps   QUICK_JUMP_POLE_LATITUDE, GREENWICH_*
  Subdial recolor recipe    SUBDIAL_RECOLOR_VALUE_RAMP, _SAT_CUTOFF, _RIM_RADIUS
  Report                    REPORT_REFRESH_MS, REPORT_BAR_TOP_N
  The Observatory           OBSERVATORY_BUNDLE_*, _ZOOM_*, _ECLIPSE_KIND_INFO
  The Guide                 GUIDE_DIR, GUIDE_INITIAL_IMAGE_PX
  Dialog opening sizes      DIALOG_A4_*, DIALOG_SQUARE_HEIGHT_FRACTION
  Translation                TRANSLATE_ENDPOINT, TRANSLATE_TIMEOUT_S
  Window margin              dial_window_margin_fraction()
  Shared art content roots  ZODIAC_ART_DIR, EMBLEM_ART_DIRS, ERA_ART_DIR, ...
  THE METAL SHADES          METAL_SHADES (ramp mapping), METAL_SOURCE_*
  DEFAULT_SKIN               the one SkinDefinition (see below)
  Pole light/dark windows   POLE_LIGHT_WINDOW, pole_is_light()
```

## The import DAG this file sits atop

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph BASE["base — every module may import these"]
        paths[paths.py]
        constants[constants.py]
        palette[palette.py]
    end
    subgraph PEERS["Session-36 DAG peers — never import each other"]
        dial[dial.py]
        shortcuts[shortcuts.py]
        pantheon[pantheon.py]
        calmounts[calendar_mounts.py]
        encui[encyclopedia_ui.py]
        glow[glow.py]
    end
    continents[continents.py\n— pantheon's own fallback,\nnot a DAG peer]
    remnant["defaults.py\n(this file) — may import\nEVERY peer downhill"]

    BASE --> PEERS
    pantheon --> continents
    PEERS --> remnant
    continents --> remnant
```

A value two peers both need cannot live in either peer (that would be
a cross-peer import, forbidden) and must not be duplicated (Rule #5) —
it lives in `defaults.py`, the one module allowed to import every peer.

## dial_window_margin_fraction — the flagship coordinator

```mermaid
flowchart TB
    A["dial.RING_LETTER_RADIUS_FRACTION,\ndial.RING_LETTER_ART_SCALE,\ndial.RING_LETTER_SHADOW_RADIUS"] --> D[letter_extent]
    B["dial.GLOW_RING_RADIUS_FRACTION,\nglow.GLOW_RADIUS_SCALE,\nskin.hover_enlarge"] --> C[glow_extent]
    E["dial.RING_MOTTO_RADIUS_FRACTION\n(only if skin.ring.motto)"] --> F[motto_extent, else 0.0]
    C --> G["margin = (MAX(glow, letter, motto) - 1.0) / 2\n+ DIAL_WINDOW_MARGIN_EPSILON"]
    D --> G
    F --> G
    G --> H[per-side transparent window margin,\nrecomputed on EVERY skin install]
```

## DEFAULT_SKIN's own shape

```
SkinDefinition
  z_order: (background, star, weekday_set, ring, year_marker, hands)
  background: BackgroundSpec   (day/twilight alpha, umbra/aura radius)
  star:        StarSpec         (day/twilight alpha, border, radius)
  ring:        RingSpec          (placeholder face — build_skin ALWAYS
                                  overlays the chosen preset card)
  weekday_set: WeekdaySpec       (7 body art paths, ghost/center display)
  year_marker: YearMarkerSpec    (Earth variants x style x continent x
                                  phase, the Moon's own art/colors)
  hands:       HandsSpec         (placeholder — build_skin ALWAYS
                                  resolves the chosen hand pack)
```

`ring` and `hands` are documented placeholders — the controller's
`build_skin` always replaces them with the user's actual choice before
the first paint; only `background`/`star`/`weekday_set`/`year_marker`
ship their real, final values here.
