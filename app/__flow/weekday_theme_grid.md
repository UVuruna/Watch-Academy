# Weekday Theme Grid — Flow

**About:** [description](../__about/weekday_theme_grid.md)

## Layout — `build_weekday_theme_grid`

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph SCROLL["QScrollArea"]
        subgraph TOP["Planets (no header)"]
            T1[tile] --- T2[tile] --- T3[tile]
        end
        subgraph G1["kinship group 1 — header + rule"]
            A1[tile] --- A2[tile] --- A3[tile] --- A4[tile]
        end
        subgraph G2["kinship group 2 — header + rule"]
            B1[tile] --- B2[tile]
        end
    end
```

Each tile is image-over-name (`ToolButtonTextUnderIcon`); the tile
matching `current_theme` carries a 2px accent border. Every section's
row of tiles wraps at 4 columns and centers as a block.

## Layout — `build_calendar_mount_grid`

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    N["None (mount off)"] --- M1[roster 1 tile] --- M2[roster 2 tile] --- M3[...]
```

Pseudocode:

    tiles <- [ tile("None", selected = current_mount == "off") ]
    FOR EACH (key, mount) IN calendar_mounts.CALENDAR_MOUNTS:
        preview <- plate of mount's FIRST member (or none if absent)
        label   <- "{mount.title} ({mount.seats})"
        tiles  += tile(label, preview, selected = key == current_mount)
    RETURN one section of these tiles, no header
