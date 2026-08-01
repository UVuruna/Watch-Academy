# Slot Theme — Flow

**About:** [description](../__about/slot_theme.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WIN["SlotThemeDialog — square, 50% of screen height"]
        GATE["gate banner (hidden unless unavailable)"]
        MEDALS["🥇 1st   🥈 2nd (disabled if off)   🥉 3rd (disabled if off)"]
        subgraph TABS["active slot's tabs"]
            direction LR
            W["Weekday
            (Weekday Theme Grid)"]
            C["Complications"]
            A["Astrology"]
            AS["Ascendant"]
            CH["Chinese zodiac"]
        end
        NAMES["Names checkbox"]
    end
    GATE --> MEDALS --> TABS --> NAMES
```

## Algorithm — medal click / rebuild

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["_select(index)"] --> B["self._active_index = index"]
    B --> C[_build]
    C --> D["clear medal row; re-add one button per descriptor
    (highlighted if index == active, disabled if !enabled_value)"]
    D --> E["clear content host"]
    E --> F{active descriptor enabled?}
    F -- no --> G["show 'Slot is off — Ctrl+N cycles' note"]
    F -- yes --> H["build tabs: Weekday / Complications /
    Astrology / Ascendant / Chinese + Names checkbox"]
```

Each tab's pick calls the active `SlotDescriptor`'s own setter
(`set_mode` / `set_style_mode` / `set_weekday` / `set_names`) directly —
there is no intermediate dialog state; the controller re-supplies a
fresh `refresh(descriptors)` after every pick so the highlighted choice
in every tab always matches the live `Settings`.
