# Cube Model Export — Flow

**About:** [description](../__about/cube_model_export.md)

## The direction grammar

A cube coordinate `(x, y, z)` with components in `{-1, 0, 1}` already
IS the gadget's own direction token, letter for letter — no lookup
table:

    FUNCTION _token(coords):
        RETURN concat("+"|"-" + letter FOR letter, value IN zip("x","y","z", coords) IF value != 0)

`(1, 1, 1)` → `"+x+y+z"`; `(0, 1, -1)` → `"+y-z"` — this works because
`config.cube`'s own axis order (X Activation, Y Moral Scope, Z
Self-Regard) IS the gadget's `axisLetters` order.

## Algorithm — `build_model()`: assembling the whole export

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph AXES["axes[] — 13 entries"]
        A1[for each cube.AXES axis] --> A2[positive_coords = the + end]
        A2 --> A3[ends = end(positive), end(negative)]
        A3 --> A4["each end: token, cell_color, seat_names(coords)"]
    end
    subgraph CELLS["cells[] — 26 seats + centre"]
        B1[for each axis: cold + warm coords] --> B2["kind = face/edge/vertex by rank(coords)"]
        B2 --> B3["position = coords * size/2"]
        B3 --> B4[append centre cell separately]
    end
    subgraph VIEWS["views[] — owner + computed"]
        C1[4 owner views, transcribed] --> C2[+ one axis-solo view per axis]
        C2 --> C3[+ two pole-solo views per axis]
    end
    AXES --> M[build_model returns axes + cells + views + glass]
    CELLS --> M
    VIEWS --> M
```

Pseudocode (language-neutral):

    FUNCTION build_model(size):
        RETURN {
            name, label, root: "model", size,
            registers: [canon, myth, historical, movie],
            sacred: token(positive coords of the sacred axis),
            axes:  [axis_entry(axis) FOR axis IN cube.AXES],       # 13 axes
            cells: cell_entries(size),                              # 26 + centre
            glass: {opacity: CUBE_MODEL_GLASS_OPACITY,
                    colors: [cell_color(c) FOR c IN the 6 face directions]},
            views: owner_views + axis_solo_views + pole_solo_views,
        }

## Algorithm — per-seat register names (`_figure_names` / `_seat_names`)

    FUNCTION seat_names(coords):
        cell = CELL_BY_COORDS[coords]                    # None only for coords outside the 27 seats
        canon = {luminous: cell.luminous, fallen: cell.fallen OR cell.luminous}
        names = {canon: canon}
        FOR register, domy_set IN {myth: archetypal, historical: historical, movie: modern}:
            IF coords is centre OR a sacred vertex:
                name = sacred_figure(seat) OR THE_ONE_SEAT     # ONE name, both slots
                names[register] = {luminous: name, fallen: name}
            ELSE:
                names[register] = cube.roster(coords, domy_set)   # (luminous, fallen) pair
        RETURN names

## Algorithm — solo views (`_lit_view`, `_side_camera`)

    FUNCTION lit_view(name, camera, axis, lit_coords):
        opacity = {glass: 0}
        FOR each of the 13 axes: opacity[its group path] = 1.0 IF it IS axis ELSE DIM_OPACITY
        FOR each of the 26 cells: opacity[its group path] = 1.0 IF its coords IN lit_coords ELSE DIM_OPACITY
        opacity[centre] = 1.0
        RETURN {name, camera, opacity}

    FUNCTION side_camera(coords):
        direction = coords as floats
        reference = (1,0,0) IF direction is parallel to Y-axis ELSE (0,1,0)
        RETURN cross_product(direction, reference)   # perpendicular to the axis -> no foreshortening
